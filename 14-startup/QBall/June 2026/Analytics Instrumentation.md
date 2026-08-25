## Problem Statement

QBall already has PostHog installed, but the product only captures broad usage signals such as
page visits and session replay. We need reliable event tracking for key product actions so we
can understand which features are used, where booking/payment funnels drop off, and which user
flows deserve more work.

The current frontend sends a few direct PostHog events, but important business outcomes happen
on the backend through MediatR handlers, payment webhooks, Hangfire jobs, and fulfillment jobs.
Those backend outcomes must be the source of truth.

## Goals

- Track key admin, game-manager, public booking, bundle, ticket, and payment events.
- Keep backend and frontend analytics work independently implementable.
- Avoid duplicate or unjoinable PostHog events by using stable names and IDs.
- Make payment funnels traceable from frontend intent through backend completion or abandonment.
- Avoid sending raw PII such as email addresses or phone numbers to PostHog event properties.

## Non-Goals

- Replacing PostHog.
- Building an internal analytics dashboard.
- Tracking every button click.
- Adding heavy event-sourcing infrastructure.
- Perfect analytics coverage in the first pass.

## Current State

Frontend:

- `posthog-js` is initialized in `src/routes/+layout.svelte`.
- Authenticated users are identified in `src/routes/(authenticated)/+layout.svelte`.
- A few payment events are captured directly from Svelte components.
- Server-side PostHog access exists in `src/lib/server/posthog.ts`.

Backend:

- No analytics wrapper exists yet.
- Business actions are handled through MediatR request handlers.
- Payment initiation creates `GameManagerTransaction` records.
- Payment completion, failure, late payment handling, and abandonment are centralized in payment
  provider and Hangfire job code.

## Product Approach

Use both frontend and backend analytics, but with different ownership:

- Frontend tracks user intent and UX behavior.
- Backend tracks canonical business facts and state transitions.

For example:

- Frontend: `join_session_clicked`, `payment_checkout_opened`, `session_create_form_started`.
- Backend: `payment_initiated`, `payment_completed`, `payment_abandoned`, `session_created`.

## Shared Event Rules

Event names use `snake_case`.

Backend event names should describe facts that already happened:

- `session_created`
- `bundle_created`
- `payment_completed`
- `ticket_issued`

Frontend event names should describe intent or interaction:

- `join_session_clicked`
- `payment_checkout_opened`
- `venue_search_performed`
- `calendar_view_changed`

Every relevant event should include stable IDs when available:

- `user_id`
- `gm_id`
- `gm_slug`
- `venue_id`
- `booking_id`
- `bundle_id`
- `transaction_reference`
- `provider`
- `origin`: `frontend` or `backend`
- `app_surface`: `admin_frontend` or `qball_api`

## Distinct ID Strategy

PostHog's `distinct_id` answers "who did this?". It does not have to be a QBall user ID for
anonymous/public flows, but it must be stable enough to connect related events.

Use this order:

1. Authenticated users: `currentUser.UserId`.
2. Public player flows: frontend `posthog.get_distinct_id()` passed through the SvelteKit action
   and backend request as `clientDistinctId`.
3. Background payment events: the `AnalyticsDistinctId` stored on the transaction at initiation.

Do not fall back to `transaction_reference`, `application_id`, IP address, or raw contact details
as `distinct_id`. If an unauthenticated or system-generated event does not have a frontend
PostHog distinct ID or a previously persisted `AnalyticsDistinctId`, skip the event.

Do not use raw email, phone number, or IP address as `distinct_id`.

For payment and application flows, add a nullable `AnalyticsDistinctId` to records that can be
completed or acted on later by webhooks, jobs, or admin workflows:

- `GameManagerTransaction.AnalyticsDistinctId`
- `VenueTransaction.AnalyticsDistinctId`
- `GameManagerApplication.AnalyticsDistinctId`

For GM public payments, set it from the frontend anonymous distinct ID when available. This lets
the frontend event `payment_checkout_opened` and backend events such as `payment_completed` belong
to the same anonymous PostHog person before the player has an account.

`transaction_reference` remains the primary join key in event properties and stable insert IDs,
but it is not used as `distinct_id`.

## Backend Work

### 1. Add an analytics service wrapper

Create a small backend abstraction:

```text
src/Application/Interfaces/Analytics/IAnalyticsService.cs
src/Application/Interfaces/Analytics/AnalyticsEvent.cs
src/Infrastructure/Services/Analytics/PostHogAnalyticsService.cs
src/Application/Settings/AnalyticsSettings.cs
```

Suggested interface:

```csharp
public interface IAnalyticsService
{
    Task TrackAsync(
        string eventName,
        string distinctId,
        object? properties = null,
        CancellationToken cancellationToken = default
    );
}
```

Register it in DI. The implementation should be no-op when analytics is disabled or the PostHog
key is missing.

Do not add `IdentifyAsync` on the backend in the first pass. The frontend already identifies
authenticated users with `user.id`, and backend request events can use that same ID as
`distinctId`. Add backend identify later only if the backend becomes responsible for updating user
traits that the frontend cannot know.

### 2. Track canonical business events

Add backend events after successful persistence or state transition. Start with:

#### Authenticated - CurrentUser.UserId as `distinctId`

- `session_created`
- `session_updated`
- `session_cancelled`
- `ticket_issued`
- `ticket_holder_voided`
- `bundle_created`
- `bundle_updated`
- `bundle_deleted`
- `bundle_holder_granted`
- `gm_settings_updated`
- `kyc_submitted`
- `sub_account_created`

#### Unauthenticated - use Posthog generated `distinctId`

- `gm_application_submitted`
- `gm_application_approved`
- `gm_application_rejected`
- `payment_initiated`
- `payment_completed`
- `payment_failed`
- `payment_late_resurrected`
- `payment_late_refund_initiated`
- `booking_joined`
- `bundle_purchased`

#### System Generated

- `payment_abandoned`

Unauthenticated and system-generated events are emitted only when the relevant request or entity
has a non-empty `clientDistinctId` or persisted `AnalyticsDistinctId`.

### 3. Payment instrumentation points

Use backend payment events as the source of truth:

- `payment_initiated`: after `ProviderReference` is persisted on `GameManagerTransaction`.
- `payment_completed`: in the payment provider base completion methods.
- `payment_failed`: when a provider status marks an initiated transaction as failed.
- `payment_abandoned`: in `MarkOutdatedInitiatedTransactionsAsAbandonedJob`.
- `payment_late_resurrected`: when a late abandoned payment is accepted.
- `payment_late_refund_initiated`: when a late abandoned payment is refunded.
- `booking_joined`: after game-manager booking fulfillment creates ticket holders.
- `bundle_purchased`: after bundle fulfillment creates bundle holders.

Use `transaction_reference` as the primary property-level join key and insert-ID component. Do not
use it as `distinct_id`.

### 4. Idempotency

Payment events can be reached through webhooks and requery jobs, so use a stable insert ID where
PostHog supports it:

```text
payment_completed:{transaction_reference}
payment_failed:{transaction_reference}
payment_abandoned:{transaction_reference}
booking_joined:{transaction_reference}
bundle_purchased:{transaction_reference}
```

If duplicate events become a problem, add a lightweight analytics outbox table. Do not start
with a large event pipeline.

### 5. Backend tests

Add focused tests around the wrapper and a few high-risk event points:

- Analytics service is no-op when disabled.
- `payment_initiated` receives `transaction_reference`, `booking_id` or `bundle_id`, amount,
  provider, and count.
- `payment_abandoned` is emitted for stale initiated GM transactions with `AnalyticsDistinctId`.
- Payment and application events are skipped when no distinct ID is available.
- Completion paths use stable insert IDs.

Avoid asserting every event in every handler in the first pass.

## Frontend Work

### 1. Add a frontend analytics wrapper

Create:

```text
src/lib/analytics/events.ts
src/lib/analytics/client.ts
src/lib/analytics/server.ts
```

The client wrapper should hide direct `posthog.capture` calls:

```ts
export function track(
  event: AnalyticsEventName,
  properties?: AnalyticsProperties,
) {
  posthog.capture(event, {
    ...properties,
    origin: "frontend",
    app_surface: "admin_frontend",
  });
}
```

Components should import this wrapper instead of importing `posthog-js` directly.

### 2. Preserve the transaction join key

The backend already returns `transactionReference` for GM booking and bundle payment initiation.
The SvelteKit actions should return it to the browser along with `checkoutUrl`.

Update these actions:

- `src/routes/gm/[gmSlug]/bookings/[bookingIdentifier]/+page.server.ts`
- `src/routes/gm/[gmSlug]/booking-bundles/[bundleId]/pay/+page.server.ts`

Then include `transaction_reference` in frontend payment events.

### 3. Track public payment funnel events

Start with:

- `public_gm_profile_viewed`
- `public_session_viewed`
- `public_bundle_viewed`
- `join_session_clicked`
- `buy_bundle_clicked`
- `payment_form_submitted`
- `payment_checkout_opened`
- `payment_status_viewed`

Suggested funnel:

```text
public_session_viewed
join_session_clicked
payment_form_submitted
payment_initiated
payment_checkout_opened
payment_completed | payment_failed | payment_abandoned
booking_joined
```

### 4. Track GM/admin UX events

Track behavior the backend cannot see clearly:

- `session_create_form_started`
- `session_create_form_submitted`
- `bundle_create_form_started`
- `bundle_create_form_submitted`
- `session_search_performed`
- `calendar_view_changed`
- `venue_search_performed`
- `dashboard_viewed`

Do not duplicate backend fact events such as `session_created` from the frontend.

### 5. Identity

For authenticated users, keep using:

```ts
posthog.identify(user.id, traits);
```

Backend events for authenticated flows should use the same `user.id` as `distinctId`.

For public payment flows, include the anonymous PostHog distinct ID in the form/action payload
when possible. The backend should use that anonymous ID for `payment_initiated` and skip
unauthenticated analytics events when it is missing.

Suggested frontend field name:

```ts
clientDistinctId: posthog.get_distinct_id();
```

The backend should persist this value on the created transaction as `AnalyticsDistinctId`.

Frontend must include `clientDistinctId` in the JSON body for these unauthenticated endpoints:

| Endpoint | Request body field | Why |
| --- | --- | --- |
| `POST /api/game-manager/applications` | `clientDistinctId` | Links `gm_application_submitted`, `gm_application_approved`, and `gm_application_rejected`. |
| `POST /api/public/game-managers/{slug}/bookings/{bookingId}/initiate-payment` | `clientDistinctId` | Links GM session payment initiation, completion, abandonment, late-payment, and fulfillment events. |
| `POST /api/public/game-managers/{slug}/booking-bundles/{bundleId}/initiate-payment` | `clientDistinctId` | Links bundle payment initiation, completion, abandonment, late-payment, and fulfillment events. |
| `POST /api/venues/{venueIdentifier}/booking/{bookingId}/initiate-payment` | `clientDistinctId` | Links venue booking payment initiation, completion, and failure events. |

If `posthog.get_distinct_id()` is unavailable, omit `clientDistinctId`; the backend will skip
unauthenticated/system analytics for that flow instead of falling back to entity IDs.

### 6. Server-side PostHog helper

Do not call `shutdown()` on a shared singleton PostHog client per request. Either avoid
server-side identify in SvelteKit, or expose a helper that flushes without shutting down the
shared client.

## Initial Event Catalog

Every event below also includes:

- `origin`
- `app_surface`
- `environment`

### Backend

| Event                           | Distinct ID                                                                | When                                              | Required properties                                                                                                                                                                          |
| ------------------------------- | -------------------------------------------------------------------------- | ------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `gm_application_submitted`      | `clientDistinctId`; skip if missing                                        | Game manager application is saved                 | `application_id`, `source`                                                                                                                                                                   |
| `gm_application_approved`       | `application.AnalyticsDistinctId`; skip if missing                         | Admin approves GM application                     | `application_id`, `user_id` when known, `admin_user_id`                                                                                                                                      |
| `gm_application_rejected`       | `application.AnalyticsDistinctId`; skip if missing                         | Admin rejects GM application                      | `application_id`, `user_id` when known, `admin_user_id`, `reason_code` when available                                                                                                        |
| `gm_settings_updated`           | `currentUser.UserId`                                                       | GM settings update succeeds                       | `user_id`, `gm_id`, `changed_fields`, `collect_player_positions`, `absorb_transaction_fees`, `timezone`                                                                                      |
| `session_created`               | `currentUser.UserId`                                                       | GM session created                                | `user_id`, `gm_id`, `booking_id`, `booking_code`, `venue_id`, `is_public`, `price_per_player`, `player_cap`, `start_time_utc`, `end_time_utc`                                                |
| `session_updated`               | `currentUser.UserId`                                                       | GM session update succeeds                        | `user_id`, `gm_id`, `booking_id`, `venue_id`, `changed_fields`, `is_public`, `price_per_player`, `player_cap`                                                                                |
| `session_cancelled`             | `currentUser.UserId`                                                       | GM session cancelled                              | `user_id`, `gm_id`, `booking_id`, `booking_code`, `venue_id`, `start_time_utc`                                                                                                               |
| `ticket_issued`                 | `currentUser.UserId`                                                       | GM manually issues a ticket                       | `user_id`, `gm_id`, `booking_id`, `ticket_id`, `holder_count`, `positions_collected`                                                                                                         |
| `ticket_holder_voided`          | `currentUser.UserId`                                                       | GM voids one holder                               | `user_id`, `gm_id`, `booking_id`, `ticket_id`, `holder_id`                                                                                                                                   |
| `bundle_created`                | `currentUser.UserId`                                                       | GM bundle created                                 | `user_id`, `gm_id`, `bundle_id`, `session_count`, `max_holders`, `price`, `booking_ids`                                                                                                      |
| `bundle_updated`                | `currentUser.UserId`                                                       | GM bundle update succeeds                         | `user_id`, `gm_id`, `bundle_id`, `changed_fields`, `max_holders`, `price`                                                                                                                    |
| `bundle_deleted`                | `currentUser.UserId`                                                       | GM bundle deleted                                 | `user_id`, `gm_id`, `bundle_id`, `session_count`                                                                                                                                             |
| `bundle_holder_granted`         | `currentUser.UserId`                                                       | GM manually grants bundle access                  | `user_id`, `gm_id`, `bundle_id`, `holder_id`, `holder_count`, `positions_collected`                                                                                                          |
| `payment_initiated`             | `request.ClientDistinctId`; skip if missing                                | Checkout created and provider reference persisted | `transaction_reference`, `transaction_type`, `booking_id` or `bundle_id`, `gm_id`, `gm_slug`, `amount`, `platform_fee`, `gm_bears_fee`, `provider`, `quantity`, `reservation_expires_at_utc` |
| `payment_completed`             | `transaction.AnalyticsDistinctId`; skip if missing                         | Provider confirms payment via webhook or requery  | `transaction_reference`, `transaction_type`, `booking_id` or `bundle_id`, `gm_id`, `amount`, `platform_fee`, `provider_fee`, `provider`, `source`, `completed_at_utc`                        |
| `payment_failed`                | `transaction.AnalyticsDistinctId`; skip if missing                         | Provider status marks payment failed              | `transaction_reference`, `transaction_type`, `booking_id` or `bundle_id`, `amount`, `provider`, `failed_at_utc`, `source`                                                                    |
| `payment_abandoned`             | `transaction.AnalyticsDistinctId`; skip if missing                         | Reservation TTL expires                           | `transaction_reference`, `transaction_type`, `booking_id` or `bundle_id`, `amount`, `provider`, `initiated_at_utc`, `abandoned_at_utc`                                                       |
| `payment_late_resurrected`      | `transaction.AnalyticsDistinctId`; skip if missing                         | Late payment is accepted after abandonment        | `transaction_reference`, `transaction_type`, `booking_id` or `bundle_id`, `amount`, `provider`, `delay_minutes`                                                                              |
| `payment_late_refund_initiated` | `transaction.AnalyticsDistinctId`; skip if missing                         | Late payment is refunded because capacity is gone | `transaction_reference`, `transaction_type`, `booking_id` or `bundle_id`, `amount`, `provider`, `refund_reference` when available                                                            |
| `booking_joined`                | `transaction.AnalyticsDistinctId`; skip if missing                         | Booking fulfillment creates ticket holders        | `transaction_reference`, `booking_id`, `gm_id`, `venue_id`, `ticket_id`, `player_count`, `positions_collected`                                                                               |
| `bundle_purchased`              | `transaction.AnalyticsDistinctId`; skip if missing                         | Bundle fulfillment creates holders                | `transaction_reference`, `bundle_id`, `gm_id`, `holder_count`, `session_count`, `positions_collected`                                                                                        |
| `kyc_submitted`                 | `currentUser.UserId`                                                       | User KYC data is saved                            | `user_id`, `kyc_id`                                                                                                                                                                          |
| `sub_account_created`           | `currentUser.UserId`                                                       | Provider sub-account is created or synced         | `user_id`, `sub_account_id`, `provider`, `bank_name`, `split_percentage`, `source`                                                                                                           |

### Frontend

| Event                           | Distinct ID                   | When                                   | Required properties                                                                                                      |
| ------------------------------- | ----------------------------- | -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| `public_gm_profile_viewed`      | PostHog anonymous distinct ID | Public GM profile page loaded          | `gm_slug`, `gm_id` when available                                                                                        |
| `public_session_viewed`         | PostHog anonymous distinct ID | Public session page loaded             | `gm_slug`, `booking_id`, `booking_code`, `price_per_player`, `spots_remaining`                                           |
| `public_bundle_viewed`          | PostHog anonymous distinct ID | Public bundle page loaded              | `gm_slug`, `bundle_id`, `price`, `spots_remaining`, `session_count`                                                      |
| `join_session_clicked`          | PostHog anonymous distinct ID | Player starts joining session          | `gm_slug`, `booking_id`, `spots_remaining`                                                                               |
| `buy_bundle_clicked`            | PostHog anonymous distinct ID | Player starts buying bundle            | `gm_slug`, `bundle_id`, `spots_remaining`                                                                                |
| `payment_form_submitted`        | PostHog anonymous distinct ID | Public payment form submitted          | `gm_slug` when available, `booking_id` or `bundle_id`, `transaction_type`, `quantity`, `positions_required`              |
| `payment_checkout_opened`       | PostHog anonymous distinct ID | Browser redirects to provider checkout | `transaction_reference`, `transaction_type`, `booking_id` or `bundle_id`, `quantity`                                     |
| `payment_status_viewed`         | PostHog anonymous distinct ID | Player lands on status page            | `transaction_reference`, `transaction_type`, `gm_slug`                                                                   |
| `dashboard_viewed`              | authenticated `user.id`       | GM dashboard page loaded               | none beyond shared event properties                                                                                      |
| `session_create_form_started`   | authenticated `user.id`       | GM starts creating a session           | `source`                                                                                                                 |
| `session_create_form_submitted` | authenticated `user.id`       | GM submits session form                | `venue_id`, `is_public`, `has_player_cap`                                                                                |
| `bundle_create_form_started`    | authenticated `user.id`       | GM starts creating a bundle            | none beyond shared event properties                                                                                      |
| `bundle_create_form_submitted`  | authenticated `user.id`       | GM submits bundle form                 | `session_count`, `max_holders`                                                                                           |
| `session_search_performed`      | authenticated `user.id`       | GM searches sessions                   | `has_query`, `has_date_filter`, `has_status_filter`, `eligible_for_bundle`                                               |
| `calendar_view_changed`         | authenticated `user.id`       | GM changes calendar view/date          | `view_type`, `reference_date`                                                                                            |
| `venue_search_performed`        | authenticated `user.id`       | GM searches venue catalogue            | `radius_km`, `has_query`                                                                                                 |
| `settings_updated_submitted`    | authenticated `user.id`       | GM submits settings form               | `changed_fields`                                                                                                         |

Frontend event names are represented in code by `AnalyticsEventName`; event payloads are represented by the `AnalyticsEvent` discriminated union. Current `transaction_type` values are `gm_booking`, `gm_bundle`, and `venue_booking`.

## Rollout Plan

1. Add backend and frontend analytics wrappers.
2. Add `AnalyticsDistinctId` to long-lived payment and application records.
3. Send frontend `posthog.get_distinct_id()` as `clientDistinctId` to the unauthenticated application and payment initiation endpoints.
4. Persist `clientDistinctId` as `AnalyticsDistinctId`; skip unauthenticated/system backend events when it is missing.
5. Fix payment initiation actions to return `transactionReference` to the browser.
6. Replace direct frontend PostHog calls in payment forms with the wrapper.
7. Add backend GM session, ticket, and bundle events.
8. Add backend application, payment, abandonment, and fulfillment events.
9. Add frontend funnel and UX events.
10. Review PostHog event names/properties after one week and prune noisy events.

## Open Questions

Decisions for the first pass:

- Public player events use anonymous PostHog distinct IDs. A stable player/customer ID can be
  added later.
- Do not send emails, phone numbers, full names, or email hashes.
- Analytics failures should be logged only. Do not send Discord notifications for analytics
  delivery failures.
