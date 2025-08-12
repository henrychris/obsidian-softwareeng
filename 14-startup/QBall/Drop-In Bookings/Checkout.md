# Overview
## What’s the Problem?
Some venues in Nigeria run _drop-in football sessions_ where players show up, pay on the spot, and play in randomly formed teams.

But there’s a problem:

> **Venue managers can’t reliably match payments received with actual attendance.**

They currently issue paper tickets at the gate. It’s disorganised, hard to reconcile, and easily abused.

---
## What Are We Building?
We’re building a system that manages drop-in bookings, collects payments via **Monnify Checkout**, and issues **verifiable digital tickets**.

The goal is to:
- Let players scan a QR code to pay instantly
- Tie each payment to a specific drop-in session
- Automatically issue digital tickets with verifiable details
- Help venues reconcile attendance with payment logs
---
## How It Works (End-to-End)
### 1. Venue Creates a Drop-In Slot
- Manager logs into the dashboard.
- Creates a new drop-in slot (e.g. _6–8 PM_, _today_, at _Venue X_).
- System generates a **public booking page** (e.g. `/booking/ABC123`)
- A **QR code** is generated that links directly to this page.
	- This QR code is printed and placed at the pitch entrance.
---
### 2. Customer Pays via Checkout
- Player scans the QR code, landing on the public booking page.
- Page shows booking info: time, location, amount.
- Player clicks “Pay” and enters their **name and email**.
	- If they wish to pay for multiple people, they can add the names of the others as well
- The system:
    - Creates a Monnify transaction
    - Passes metadata: `bookingId`, `venueId`, `customerName`, `customerEmail`
    - Uses a preconfigured **split** (e.g. venue gets 90%, platform gets 10%)
    - Redirects to Checkout
- Player completes the payment and is redirected to a ticket page.
---
### 3. System Receives Webhook from Monnify
- On receiving the `payment.success` webhook:
    - Extracts metadata from the webhook payload
    - Matches payment to the correct booking
    - Logs payer as a **ticketed participant**
    - Ensures duplicate transactions aren’t processed (via transaction`reference`)
    - Optionally stores transaction ID for auditability
---
### 4. Ticket Issued
- After successful payment:
    - Customer is redirected to a **confirmation page**
    - System generates and send a **digital ticket**
    - Ticket includes: name, time, date, booking ID, and amount
    - Optionally sent via SMS/email
- Ticket has a **QR code** linking to `/verify/:ticketId`
---
## 5. Security Checks at the Gate
- Player shows digital ticket (on phone or printed)
- Security verifies:
    - Time and date match current session
    - Name matches what they see
    - QR code scan (optional) hits `/verify` endpoint to confirm ticket validity
---
## How Funds Are Handled
- Each venue has a **Monnify Subaccount** tied to their bank account.
- Our platform is the primary merchant.
- Every transaction uses a **split payment**:
    - e.g. Venue gets 90%, Platform takes 10%
- Settlement is handled **directly by Monnify**, not us.
- We never receive or hold funds — just metadata and events.
---
## Edge Case Handling

|Case|How It’s Handled|
|---|---|
|Payment without metadata|Impossible — metadata is embedded in transaction setup|
|Duplicate webhook|Prevented using `reference` or `transaction_id`|
|Payment after session|Still valid, but flagged for review if too late|
|Failed payment|Customer not redirected, ticket not generated|

---
## Internal Notes
- Subaccounts must be created for each venue to enable split payments.
- Split codes should be stored per venue.
- Use `metadata` to avoid ambiguous reconciliation (unlike virtual account model).
- Consider a fallback method if customer doesn’t complete checkout (e.g. reminder system?).
- QR codes should always point to booking page, never directly to a Monnify link.
- For security, we will need to sign the ticket data. We can go with simple public-private key cryptography. The `/verify` page will verify the signature was created using the private key stored on the backend.
	- We should include the following data in the signature:
		- names & emails of each person
		- booking code
		- Booking ID or code
		- Date & time of booking
		- Transaction Reference
		- Ticket issuance timestamp
- The ticket will contain:
```json
{
  "bookingCode": "Z4G9P1",
  "players": [
	  {
		  "name": "Chuka Obi",
		  "email": "chuka@example.com",
	  }
  ],
  "timestamp": "2025-07-04T16:30:00Z",
  "signature": "MEUCIQC…etc…"
}
```
- The ticket payload should fit in the QR code on the ticket.
---
## Summary

> This feature lets drop-in football venues accept secure digital payments using Monnify Checkout, issue verifiable tickets, and track who paid — with zero reconciliation stress.  
> Funds go directly to the venue’s bank account (minus our platform fee), and players get an instant, trusted proof of payment.

# Implementation
## Bookings
- Bookings need to support two types - `DropIn` and `Standard`. By default, bookings will be `Standard`.
	- All `DropIn` bookings will have status as `Confirmed` when created.
	- **Todo**:
		- ~~Add a `Type` field to the Booking model, with a default value of `Standard`.~~
		- ~~Check in the create booking test that the type is set to `Standard` when not specified.~~
		- ~~Add a test to ensure `DropIn` type is used when specified & the status is set to `Confirmed`.~~
- Venues need to set a price for bookings. This price is per player for `DropIn` bookings, and for the entire slot for `Standard` bookings.
	- Venues should be able to set a default price for these in the venue settings. These prices will be used when creating a new booking, but can be changed by the venue manager.
	- The prices will be displayed on the public booking page.
	- We need to sort out the UI for this.
	- **Todo:**
		- ~~Add a `VenueSettings` model. This should have a foreign key relationship with `Venue.` The model will have two fields: `DefaultDropInPrice` & `DefaultBookingPrice`. The model must be created whenever a new venue is created.~~
		- ~~Add a test to ensure that it is created as expected with a default value of 0 in each field.~~ 
- All bookings must have a unique 6-digit code. This code will allow users to access the booking on the public page.
	- **Todo:**
		- ~~Add a nullable `Code` field~~
		- ~~Create a one time endpoint to fetch all bookings, generate unique codes for them, set the code in each booking, and save to the database~~
		- ~~Run this script on dev and local~~
		- ~~Update the create booking endpoint to generate a unique 6-digit code~~
		- ~~Create a migration to make `Code` non-nullable~~
		- ~~Verify in tests that a unique code is set~~
## Venue KYC & Subaccount
We need to collect KYC data from users of our application. When KYC is complete, we will create a subaccount using their bank account details. This implementation has two parts.

See: [KYC reference](https://support.paystack.com/en/articles/2127810)

---
### KYC

~~We’ll add a `VenueKyc` model:~~

```csharp
// A venue can have only one KYC entry.
[Index(nameof(VenueId), IsUnique = true)]
public class VenueKyc : BaseEntity
{
	public required string FirstName { get; set; }
    public string? MiddleName { get; set; }
    public required string LastName { get; set; }

    public required string Email { get; set; }
    public required string PhoneNumber { get; set; }
    public required string HomeAddress { get; set; }
	
	public required int VenueId { get; set; }
    public Venue Venue { get; set; } = null!;
}
```

~~We’ll also add a navigation property to `Venue`:~~

```csharp
public VenueKyc? VenueKyc { get; set; }
```

---

When the user views the **Payments** section on the venue page, we check:

* If `VenueKyc` exists
* If the venue has a valid subaccount for the current payment provider

If either is missing, we prompt them to set up KYC.

---
#### KYC Setup Flow
- User provides:
  - First name (pre-filled)
  - Middle name
  - Last name (pre-filled)
  - Email (pre-filled)
  - Date of birth
  - Phone number
  - Home address
  - BVN
- They click **Verify**
- We pass this data to Monnify’s `bvn-details-match` endpoint
- If successful, we create the `VenueKyc` model
- If not, we return an error
---
### Subaccount
After KYC is complete, the venue must provide **bank account details**.
At this point, we’ll have:
- User’s basic KYC data

~~We’ll create a `VenueSubAccount` model:~~

```csharp
// we cant have a venue with multiple sub accounts for the same provider
[Index(nameof(Provider), nameof(VenueId), IsUnique = true)]
public class VenueSubAccount : BaseEntity 
{
    public required PaymentProvider Provider { get; set; }
    public required string SubAccountCode { get; set; }
    public required string CurrencyCode { get; set; }
    public required string BankCode { get; set; }

	// navigation properties
	public required int VenueId { get; set; }
	public Venue Venue { get; set; } = null!;
}
```

~~And add a navigation property to `Venue`:~~

```csharp
public ICollection<VenueSubAccount> SubAccounts { get; set; }
```

---

**Subaccount Setup Flow**

- User selects a bank and enters their account number
- User also provides BVN again - we are not allowed to store it.
- Backend:
	- Looks up their venue email
	- Passes email and BVN to Monnify’s `bvn-account-match` endpoint
- If the match is valid:
  - We call Monnify’s subaccount creation endpoint
  - On success, we save the subaccount
- If invalid, we return the error

---

**Note:**
We must define a default revenue split for subaccounts in application configuration. This defines what % of incoming funds go to the venue vs the platform.

---
**Before we create any subaccount, we must:**
- Check if the venue already has one for the current provider
- Prevent duplicates via a composite key (e.g., `venueId + provider`)

## Payments
- We will need to support multiple payment providers, in case we need to switch at any time. For that reason, we need to build our application in a way that makes this easy. For payments, we will use the factory pattern to define the actions we perform on each provider and to use different ones at runtime.
- Per Monnify's terms of service, we need to maintain an immutable record of transactions. This is simple enough. When a transaction is completed, it must be locked from future updates. 
	- The schema:
```cs
	public required string Reference { get; set; } // Monnify ref
    public required string BookingCode { get; set; }
    public required string VenueId { get; set; }

    public string? CustomerFirstName { get; set; }
    public string? CustomerLastName { get; set; }
    public string? CustomerEmail { get; set; }
    public string? CustomerPhoneNumber { get; set; }

    public required int Amount { get; set; }
    public required PaymentProvider Provider { get; set; } = PaymentProvider.Monnify;

    public PaymentStatus Status { get; set; } = PaymentStatus.Initiated;

    public DateTime InitiatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? CompletedAt { get; set; }
    public DateTime? FailedAt { get; set; }

    public string? RawWebhookPayload { get; set; } // JSONB

    // if available
    public string? ExternalTransactionId { get; set; }
```
- Payments will be initiated on the backend and the checkout link will be returned to the frontend.
	- Initiating a payment creates a transaction record that is `Initiated` or `Pending`.
	- The metadata must contain: `bookingId`, `venueId`, `customerFirstName`, `customerLastName`, `customerEmail`
- Completed payments will send a webhook to our system. The system will get the correct provider depending on the webhook URL. Using the transaction reference, we will find the initated transaction and mark it as completed (storing the data sent by the provider).
