# Problem Statement
When a user initiates a GM booking payment, a `GameManagerTransaction` is created with `Status = Initiated`. This acts as a soft reservation — it holds spots against the booking's capacity for `RESERVATION_TTL_IN_MINUTES` (currently 12 minutes). If the user hasn't completed payment by then, `MarkOutdatedInitiatedTransactionsAsAbandonedJob` marks the transaction `Abandoned`, releasing the reservation.

The problem: Monnify's checkout session remains open on their side after we abandon the record. A user can still complete payment after the TTL expires. When they do, the webhook arrives, `ProcessSuccessfulGameManagerBookingPaymentAsync` looks up the transaction filtered to `Status == Initiated`, finds nothing, logs a silent failure, and marks the webhook as processed. Money is collected. The user gets nothing. Nobody is alerted.

---
# Solution: Conditional Resurrection with Refund Fallback
When a `SUCCESSFUL_TRANSACTION` webhook arrives for a transaction we have marked `Abandoned`:
1. Re-check whether the booking still has capacity for the number of players in the transaction.
2. **If capacity is available** → resurrect: fulfil the booking exactly as if the payment had arrived on time.
3. **If capacity is full** → refund: call Monnify's refund API and notify the customer by email.

A separate, smaller change logs the references of transactions as they are abandoned, addressing a pre-existing TODO in the job.

---
# Code Changes

## 1. `src/Shared/Errors/Errors.Provider.cs`
Add one new error:
```
Provider.RefundFailed
Error.Failure("Provider.RefundFailed", "We couldn't initiate a refund for this transaction. Please contact support.")
```

---
## 2. `src/Shared/AllConstants.cs`
Add one new constant to `EmailTemplates`:
```
LATE_PAYMENT_REFUNDED = "late-payment-refunded"
```

---
## 3. `src/Application/Interfaces/Payments/IPaymentProvider.cs`
Add one method:
```
Task<Result<MyUnit>> RefundTransactionAsync(string providerTransactionReference, decimal amountToRefund, string? reason = null);
```
- `providerTransactionReference` — Monnify's own reference (the `ProviderReference` column on `GameManagerTransaction`, e.g. `MNFY|65|...`). This is what Monnify's refund endpoint calls `transactionReference`.
- `amountToRefund` — supports partial refunds; callers always pass `transaction.Amount` for a full refund.
- `reason` — optional free-text. Becomes both `refundReason` and `customerNote` on the Monnify request. Defaults to `"Payment received after reservation expired"` inside the implementation.

---
## 4. `src/Application/Interfaces/Payments/Providers/Monnify/IMonnifyApi.cs`
Add one Refit endpoint:
```
[Post("/refunds/initiate-refund")]
Task<ApiResponse<MonnifyResponse<MonnifyInitiateRefundResponse>>> InitiateRefundAsync(MonnifyInitiateRefundRequest request);
```

---
## 5. `src/Application/Interfaces/Payments/Providers/Monnify/MonnifyDtos.cs`
Add two new internal DTOs.
**`MonnifyInitiateRefundRequest`**

| Field                        | Type    | Notes                                                                 |
| ---------------------------- | ------- | --------------------------------------------------------------------- |
| `TransactionReference`       | string  | Monnify's ref                                                         |
| `RefundAmount`               | decimal |                                                                       |
| `RefundReference`            | string  | Merchant-generated unique ref, e.g. `RFD_{Guid:N}`                    |
| `RefundReason`               | string  |                                                                       |
| `CustomerNote`               | string  | Narration on customer's bank statement. Same value as `RefundReason`. |
| `DestinationAccountNumber`   | string? | Omitted — Monnify falls back to original payment source               |
| `DestinationAccountBankCode` | string? | Omitted — same                                                        |
**`MonnifyInitiateRefundResponse`**

| Field | Type |
|---|---|
| `RefundReference` | string |
| `TransactionReference` | string |
| `RefundReason` | string |
| `CustomerNote` | string |
| `RefundAmount` | decimal |
| `RefundType` | string |
| `RefundStatus` | string |
| `RefundStrategy` | string |
| `Comment` | string |
| `CreatedOn` | string |
Used only for logging. No business logic branches on any of these values.

---
## 6. `src/Application/Interfaces/Emails/EmailDtos.cs`
Add one new record:
```
public record LatePaymentRefundedEmail(
    string recipientEmailAddress,
    string customerName,
    string sessionTitle,
    string formattedDate,
    string formattedTimeRange,
    string formattedRefundAmount,
    string refundReference
) : EmailModelBase(recipientEmailAddress, "Your Payment Has Been Refunded — Session Was Full");
```

---
## 7. `src/Application/Interfaces/Emails/IEmailService.cs`
Add one method:
```
Task SendLatePaymentRefundedEmailAsync(LatePaymentRefundedEmail model);
```

---
## 8. `src/Infrastructure/Services/EmailService.cs`
Implement `SendLatePaymentRefundedEmailAsync` using template `EmailTemplates.LATE_PAYMENT_REFUNDED`. Standard pattern — load template, render with Handlebars, send.

---
## 9. `src/Resources/EmailTemplates/late-payment-refunded.html`
New Handlebars template. Must communicate clearly:
- Their payment was received, but their reservation had already expired by then.
- The session was full by the time their payment arrived.
- A full refund of `{{formattedRefundAmount}}` has been initiated.
- Refund reference: `{{refundReference}}` (for support queries).
- They are welcome to try again for a future session.

---
## 10. `src/Infrastructure/Services/Payments/Providers/Monnify/MonnifyProvider.cs`
Two changes.
### 10a. New method — `RefundTransactionAsync`
Implements `IPaymentProvider.RefundTransactionAsync`.
1. Generate `refundReference = $"RFD_{Guid.NewGuid():N}".ToUpper()`.
2. Build `MonnifyInitiateRefundRequest` using the provided params and the generated reference. `DestinationAccountNumber` and `DestinationAccountBankCode` are omitted entirely (not set to null — omitted from the JSON payload so Monnify falls back to the source instrument).
3. Call `monnifyApi.InitiateRefundAsync(request)`.
4. If `!response.IsSuccessStatusCode || !response.Content.RequestSuccessful`: log `Error` with the `TransactionReference` and Monnify's `ResponseMessage`; return `Result.Failure(Errors.Provider.RefundFailed)`.
5. Log `Information` with `TransactionReference` and `RefundReference`. Return `Result.Success(MyUnit.Value)`.
### 10b. Modify `ProcessSuccessfulGameManagerBookingPaymentAsync`
**Step 1 — Widen the transaction lookup status filter:**
Change `x.Status == PaymentStatus.Initiated` to `(x.Status == PaymentStatus.Initiated || x.Status == PaymentStatus.Abandoned)`.

Everything else in the query stays the same (reference, provider reference, provider, amount checks).
**Step 2 — Branch on the found transaction's current status (inside the existing DB transaction + row lock):**
If `transaction.Status == PaymentStatus.Initiated`: proceed exactly as today, no change.

If `transaction.Status == PaymentStatus.Abandoned`:
1. Log `Warning`: `"[{Source}] Late payment received for abandoned GM booking transaction {Ref}. Originally initiated at {InitiatedAt}, payment arrived at {Now}. Checking capacity."`.
2. **Capacity check** — load the booking (needs `ExpectedNumberOfPlayers`). Run the same two-gate check used in `InitiateBookingPaymentRequest`:
   - **Gate 1:** `activeCount` = count of non-voided `BookingTicketHolder` rows for this booking. If `metadata.Players.Count > booking.ExpectedNumberOfPlayers - activeCount` → slot is permanently full → go to refund path.
   - **Gate 2:** `liveReservedCount` = sum of `RequestedHolderCount` for other `Initiated` transactions on this booking within the TTL window (excluding the current transaction, which is `Abandoned`). If `metadata.Players.Count > booking.ExpectedNumberOfPlayers - activeCount - liveReservedCount` → slot is temporarily full → go to refund path.
   - If both gates pass → go to resurrection path.
3. **Resurrection path:**
   - Set `transaction.Status = PaymentStatus.Completed`.
   - Set `transaction.CompletedAt`, `transaction.RawWebhookPayload`, calculate and set `ProviderFee` / `ProviderFeeVat`.
   - Enqueue `fulfillmentService.FulfillGameManagerBookingAsync(...)` exactly as in the normal path.
   - Save and commit.
   - Log `Warning`: `"[{Source}] Successfully resurrected late-payment GM booking transaction {Ref}. BookingId: {BookingId}. Delay: {DelayMinutes} minutes."`. Warning level (not Info) so it is easy to monitor frequency.
4. **Refund path:**
   - Call `await RefundTransactionAsync(transaction.ProviderReference, transaction.Amount, "Payment received after reservation expired — session full")`.
   - If refund succeeds: enqueue `emailService.SendLatePaymentRefundedEmailAsync(...)` as a Hangfire job (do not send inline). Populate the email DTO using booking details fetched from the DB.
   - If refund fails: log `Error` with the reference. Do **not** throw — the DB transaction should still commit so the webhook is marked processed and not retried. A failed refund requires manual intervention.
   - Either way: leave `transaction.Status = PaymentStatus.Abandoned` (do not change it — the transaction was never completed).
   - Save and commit.
   - Log `Error`: `"[{Source}] Refunded late-payment GM booking transaction {Ref}. RefundSucceeded: {RefundSucceeded}. BookingId: {BookingId}."` — Error level so it appears in alerting.

**Note on the "not found" case:** If the wider query still returns `null` (i.e., neither `Initiated` nor `Abandoned` with matching reference/amount), log message stays the same: `"[{Source}] GM booking transaction not found or already processed: {Ref}"`. No change.

---
## 11. `src/Infrastructure/Jobs/MarkOutdatedInitiatedTransactionsAsAbandonedJob.cs`
Replace the single `ExecuteUpdateAsync` bulk operation with a fetch-then-update pattern:
1. `Select(t => t.Reference).ToListAsync()` first to capture the references.
2. If the list is empty, log the existing "nothing to do" message and return.
3. Log `Information`: `"Abandoning {Count} initiated GM transaction(s): {References}"`.
4. Then run `ExecuteUpdateAsync` as before.

The references list is the only data fetched — no full entity materialisation.

---
# Testing Strategy
## The Mocking Boundary Problem
`MonnifyProvider` is `internal` and is replaced entirely by `Mock<IPaymentProvider>` in `CustomWebApplicationFactory`. This means the resurrection/refund logic inside `ProcessSuccessfulGameManagerBookingPaymentAsync` cannot be exercised through the normal integration test HTTP flow.

**Resolution:** Write a dedicated unit test class (`MonnifyProviderLatePaymentTests`) that:
- Directly instantiates `MonnifyProvider` using a real `ApplicationDbContext` obtained from a `CreateScope()` call against the shared `CustomWebApplicationFactory` container.
- Mocks `IMonnifyApi`, `IFulfillmentService`, `IEmailService`, and `IBackgroundJobClient` via Moq.
- Uses the real `FakeTimeProvider` from the factory.
- Requires adding `[assembly: InternalsVisibleTo("QBallTests")]` to the main project (likely in `src/Infrastructure` or a `.csproj` property).

This gives you a real PostgreSQL + EF Core context (including execution strategies and row locks), real domain logic, and controlled HTTP boundaries. It follows the same pattern as the existing job tests (`CreateScope()` → get service → call method directly), just with `MonnifyProvider` directly rather than a Hangfire job.

For `RefundTransactionAsync` in isolation, the same class covers it — you don't need a separate unit test since it's exercised by the resurrection/refund tests.

---
# Test Scenarios
## `MonnifyProviderLatePaymentTests.cs`
*New file. Lives in `tests/QBallTests/UnitTests/` or a new `IntegrationTests/Services/` file — whichever is appropriate given it needs a real DB. Uses `[Collection(nameof(TestCollection))]`.*

The `InitializeAsync` should set up `SetupDefaultGoogleAuth` for the GM email used by the test helper.

**Setup helper (private):**
`BuildProvider(Mock<IMonnifyApi> monnifyApi, ...)` — constructs a `MonnifyProvider` instance from a scope's real services, substituting the provided mocks.

---
**Resurrection tests:**

| Test name                                                                                            | Scenario                                                                                  | Assert                                                                                                                |
| ---------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `ProcessWebhookAsync_AbandonedTransaction_SlotAvailable_ResurrectsAndFulfils`                        | Abandoned transaction, booking has free capacity, no live reservations                    | Transaction status → `Completed`; `FulfillGameManagerBookingAsync` enqueued once                                      |
| `ProcessWebhookAsync_AbandonedTransaction_SlotAvailable_WithLiveReservationsButStillFits_Resurrects` | Abandoned transaction; 1 live `Initiated` reservation but enough total capacity remaining | Transaction status → `Completed`; fulfillment enqueued                                                                |
| `ProcessWebhookAsync_AbandonedTransaction_PermanentlyFull_Refunds`                                   | Active ticket holders fill the venue (Gate 1 fails)                                       | `InitiateRefundAsync` called once; `SendLatePaymentRefundedEmailAsync` enqueued; transaction status stays `Abandoned` |
| `ProcessWebhookAsync_AbandonedTransaction_TemporarilyFull_Refunds`                                   | Live `Initiated` reservations from other users consume remaining spots (Gate 2 fails)     | Same as above                                                                                                         |
| `ProcessWebhookAsync_AbandonedTransaction_RefundApiFails_DoesNotThrow_LogsError`                     | Monnify's refund call returns a failure response                                          | Does not throw; webhook is still marked processed; transaction status stays `Abandoned`                               |
| `ProcessWebhookAsync_AbandonedTransaction_NoCapacitySet_Resurrects`                                  | `booking.ExpectedNumberOfPlayers` is null (uncapped)                                      | Skips capacity check; transaction → `Completed`; fulfillment enqueued                                                 |
| `ProcessWebhookAsync_InitiatedTransaction_SlotAvailable_ProcessesNormally`                           | Normal `Initiated` status — regression guard                                              | Existing behaviour unchanged; fulfillment enqueued; no refund call                                                    |
| `ProcessWebhookAsync_TransactionNotFound_LogsAndReturns`                                             | Reference doesn't exist in DB at all                                                      | No fulfillment, no refund, no throw                                                                                   |

---
**`RefundTransactionAsync` tests (can live in the same class):**

| Test name | Scenario | Assert |
|---|---|---|
| `RefundTransactionAsync_Success_ReturnsSuccess` | Monnify returns `RequestSuccessful = true` | Returns `Result.Success`; `InitiateRefundAsync` called with correct `TransactionReference` and `RefundAmount` |
| `RefundTransactionAsync_MonnifyReturnsFailure_ReturnsFailureResult` | Monnify returns `RequestSuccessful = false` | Returns `Result.Failure(Errors.Provider.RefundFailed)` |
| `RefundTransactionAsync_HttpError_ReturnsFailureResult` | Refit call returns a non-2xx status | Returns `Result.Failure(Errors.Provider.RefundFailed)` |
| `RefundTransactionAsync_GeneratesUniqueRefundReference` | Call twice | The two `refundReference` values sent to Monnify are different |
| `RefundTransactionAsync_DefaultReason_UsedWhenNoneProvided` | Call with `reason = null` | `RefundReason` and `CustomerNote` in the request are the default string, not null or empty |

---
## Updates to `MarkOutdatedInitiatedTransactionsAsAbandonedJobTests.cs`

These are in-place additions to the existing file — no new file needed.

| Test name | Scenario | Assert |
|---|---|---|
| `ExecuteAsync_WhenGmBookingReservationsAreStale_LogsAbandonedReferences` | Seed 2 stale `Initiated` GM booking transactions | After job runs, verify both references appear in the log output. Since the test doesn't capture `ILogger` directly, this assertion is best made by verifying the transactions were updated **and** adding a structured log capture helper — or defer to observing it in production and assert only on DB state. |

> **Note:** The existing tests already assert DB state (status → `Abandoned`). The logging assertion requires either a captured `ILogger` mock or a `FakeLogger`. If adding that instrumentation is considered out of scope for this change, the existing DB-state assertions are sufficient and the logging is validated by code review.

---
### `ExternalServicesMock` — no changes needed
The mock for `IPaymentProvider` already has `RefundTransactionAsync` available for setup once the interface is updated — Moq will auto-stub it. Tests that call endpoints which internally trigger `RefundTransactionAsync` (none currently, since all refund logic lives inside `MonnifyProvider`) don't need explicit setup.

---
# Sequence Diagrams
## Resurrection Path
```
Monnify → POST /api/webhook/monnify
  → HandleMonnifyWebhookRequest (validates, deduplicates, saves WebhookLog)
  → Hangfire enqueues ProcessWebhookAsync
  → MonnifyProvider.ProcessWebhookAsync
  → ProcessSuccessfulGameManagerBookingPaymentAsync
      → query: Initiated OR Abandoned with matching ref/amount
      → found: Abandoned
      → capacity check (inside DB txn + row lock)
      → capacity OK
      → transaction.Status = Completed
      → enqueue FulfillGameManagerBookingAsync
      → commit
      → log Warning (resurrected)
```

## Refund Path
```
Monnify → POST /api/webhook/monnify
  → ... (same as above until capacity check)
  → capacity FULL
  → RefundTransactionAsync(transaction.ProviderReference, transaction.Amount, reason)
      → POST /api/v1/refunds/initiate-refund → Monnify
  → enqueue SendLatePaymentRefundedEmailAsync
  → transaction.Status stays Abandoned
  → commit
  → log Error (refunded)
```

---
# Open Questions / Risks
1. **Monnify live environment approval.** The refund endpoint requires explicit approval from a Monnify relationship manager before it works in production. This must be actioned in parallel with development.
2. **Partial amount mismatch.** The implementation always refunds `transaction.Amount` (the full amount). If Monnify charged a processing fee that was already deducted before we receive the webhook, the refundable amount may differ. Confirm with Monnify whether `AmountPaid` on the webhook equals `transaction.Amount` in all cases, or whether we should use `eventData.AmountPaid` as the refund amount instead.
	- we refund `transaction.Amount`, as it is the full amount that was sent to us by the user.
3. **`CleanupAbandonedTransactionsJob` race.** If a late webhook arrives after `CleanupAbandonedTransactionsJob` has deleted the abandoned transaction row (after `InitiatedTransactionRetentionDays`), `ProcessSuccessfulGameManagerBookingPaymentAsync` will find nothing and log the existing "not found" message. Money is collected with no refund triggered. This window is days, making it unlikely for normal late payments, but it is a gap. A follow-up could be to check for the transaction in `WebhookLog` records in this fallback branch and trigger a refund from there — but that is out of scope for this change.
	- This is unlikely. Most transactions are closed within an hour of initiating. Abandoned transactions are cleaned up after 30 days to keep the DB clutter free.
4. **Email content for the refund path requires the booking's `Title`, `StartDateTimeUtc`, and `EndDateTimeUtc`**, which are not on `GameManagerTransaction`. The booking must be fetched from the DB (it's loaded anyway for the capacity check, so no extra query needed — just pass the fields through to the email DTO construction).