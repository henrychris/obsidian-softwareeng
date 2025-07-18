# 💥 PHASE 1: Foundations

## ✅ Step 0: Define `IPaymentProvider`
Create the contract that _all_ providers (Monnify, Paystack, Flutterwave, etc.) will follow:

```cs
interface IPaymentProvider
{
    Task<Result<PaymentCheckoutResult>> CreateCheckoutAsync(PaymentCheckoutRequest request);
    Task<Result<SubAccountResult>> CreateSubAccountAsync(SubAccountCreateRequest request);
    Task<Result<WebhookHandlingResult>> HandleWebhookAsync(string rawPayload, IHeaderDictionary headers);
}
```

## ✅ Step 0.5: Define `IKycVerifier`
Create the contract for verifying a user's identity:

```cs
public interface IKycVerifier
{
    Task<Result<BvnVerificationResult>> VerifyBvnAsync(BvnVerificationRequest request);
    Task<Result<AccountMatchResult>> VerifyAccountMatchAsync(AccountMatchRequest request);
}
```

---
## ✅ Step 1: KYC Setup Flow
-  Create KYC controller (`POST /venues/{venueId}/kyc`)
	-  Accepts DOB, BVN, phone, home address    
    -  Calls `VerifyBvnAsync()` and saves `VenueKyc` if valid
	-  Add a method: `bool VenueHasKyc(int venueId)`
---
## ✅ Step 2: Subaccount Setup Flow
-  Create endpoint: `POST /venues/{venueId}/subaccount`
    -  Accepts bank code, account number, bvn
    -  Verifies match using `VerfiyAccountMatch()`, creates subaccount if valid using `CreateSubAccount()`
    - **Note:** If user has no KYC, this action should be blocked.
-  Add a method: `bool VenueHasSubAccount(int venueId, PaymentProvider provider)`
---
# 💰 PHASE 2: Payments
## ✅ Step 3: Define Payment Abstractions
-  Build `PaymentProviderFactory` to switch between providers that implement `IPaymentProvider`.
---
## ✅ Step 4: Payment Initiation
-  Endpoint: `POST /payments/initiate`
    -  Accepts: booking code, customer info
    -  Fetches booking, venue, venue’s subaccount
    -  Creates `PaymentTransaction` (status: Initiated)
    -  Calls `CreateCheckoutAsync()` on the provider
    -  Returns Monnify Checkout URL
---
## ✅ Step 5: Handle Webhook
-  Add Monnify webhook endpoint: `POST /webhooks/monnify`
    -  Call `HandleWebhookAsync(rawPayload)`
    -  Parse reference, bookingCode
    -  Lookup `PaymentTransaction` by reference
    -  If not processed:
        -  Mark status as `Completed`
        -  Store `RawWebhookPayload`
        -  Generate ticket
        -  Link ticket to booking + customer
-  Idempotency: guard via `reference`
---
# 🎟️ PHASE 3: Ticketing
## ✅ Step 6: Ticket Generation
-  Generate signed ticket payload using private key
-  Ticket structure:
```json
{
  "bookingCode": "ABC123",
  "players": [{ "name": "...", "email": "..." }],
  "timestamp": "...",
  "signature": "..."
}
```
-  QR code encodes `/verify/:ticketId`
---
## ✅ Step 7: Ticket Verification
-  Endpoint: `GET /verify/:ticketId`
    -  Loads ticket
    -  Verifies signature
    -  Returns ticket details & status (`valid`, `expired`, `already-used`, etc.)
---
# 📌 Optional Enhancements
-  Add fallback reminder flow for incomplete checkouts
-  Log webhook failures for manual review
-  Add admin dashboard for reconciling bookings + payments
-  Rate-limit KYC + webhook endpoints