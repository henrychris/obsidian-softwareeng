# What’s the Problem?
Some venues in Nigeria run _drop-in football sessions_ where players show up, pay on the spot, and play in randomly formed teams.

But there’s a problem:

> **Venue managers can’t reliably match payments received with actual attendance.**

They currently issue paper tickets at the gate. It’s disorganised, hard to reconcile, and easily abused.

---
# What Are We Building?
We’re building a system that manages drop-in bookings, collects payments via **Monnify Checkout**, and issues **verifiable digital tickets**.

The goal is to:
- Let players scan a QR code to pay instantly
- Tie each payment to a specific drop-in session
- Automatically issue digital tickets with verifiable details
- Help venues reconcile attendance with payment logs
---
# How It Works (End-to-End)
## 1. Venue Creates a Drop-In Slot
- Manager logs into the dashboard.
- Creates a new drop-in slot (e.g. _6–8 PM_, _today_, at _Venue X_).
- System generates a **public booking page** (e.g. `/booking/ABC123`)
- A **QR code** is generated that links directly to this page.
	- This QR code is printed and placed at the pitch entrance.
---
## 2. Customer Pays via Checkout
- Player scans the QR code, landing on the public booking page.
- Page shows booking info: time, location, amount.
- Player clicks “Pay” and enters their **name and email**.
	- If they wish to pay for multiple people, they can add the names of the others as well
- The system:
    - Creates a Monnify transaction
    - Passes metadata: `bookingId`, `venueId`, `customerName`, `customerEmail`
    - Uses a preconfigured **split** (e.g. venue gets 90%, platform gets 10%)
    - Redirects to Checkout
- Player completes the payment
---
## 3. System Receives Webhook from Monnify
- On receiving the `payment.success` webhook:
    - Extracts metadata from the webhook payload
    - Matches payment to the correct booking
    - Logs payer as a **ticketed participant**
    - Ensures duplicate transactions aren’t processed (via transaction`reference`)
    - Optionally stores transaction ID for auditability
---
## 4. Ticket Issued
- After successful payment:
    - Customer is redirected to a **confirmation page**
    - System generates and displays a **digital ticket**
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
# How Funds Are Handled
- Each venue has a **Monnify Subaccount** tied to their bank account.
- Our platform is the primary merchant.
- Every transaction uses a **split payment**:
    - e.g. Venue gets 90%, Platform takes 10%
- Settlement is handled **directly by Monnify**, not us.
- We never receive or hold funds — just metadata and events.
---
# Edge Case Handling

|Case|How It’s Handled|
|---|---|
|Payment without metadata|Impossible — metadata is embedded in transaction setup|
|Duplicate webhook|Prevented using `reference` or `transaction_id`|
|Payment after session|Still valid, but flagged for review if too late|
|Failed payment|Customer not redirected, ticket not generated|

---
# Internal Notes
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
# Summary

> This feature lets drop-in football venues accept secure digital payments using Monnify Checkout, issue verifiable tickets, and track who paid — with zero reconciliation stress.  
> Funds go directly to the venue’s bank account (minus our platform fee), and players get an instant, trusted proof of payment.