# What’s the Problem?
Some venues in Nigeria run _drop-in football sessions_ where players show up, pay on the spot, and play in randomly formed teams.

But there's a problem:

> **Venue managers can’t reliably match the amount of money received with the number of people who paid.**

They currently issue paper tickets at the gate, but it’s messy, hard to reconcile, and prone to abuse.

---
# What Are We Building?
We're building a system to manage drop-in bookings, collect payments through **virtual accounts**, and generate **verifiable tickets** for each payer.

The goal is:
- Let players pay into a venue's dedicated account
- Match each payment to a specific drop-in session
- Automatically issue a digital ticket
- Help venues reconcile payments with attendance
---
# How It Works (End-to-End)

## 1. Venue Creates a Drop-In Slot
- Manager logs into our dashboard.
- Creates a new drop-in slot (e.g. _6–8 PM_, _today_, at _Venue X_).
- System generates a unique **6-digit code** (e.g. `Z4G9P1`) tied to this session.
- Payment instructions are generated:
    > Send ₦2,000 to **1234567890**  
    > Use `Z4G9P1` as the _transfer narration_
## 2. Customers Pay
- Players transfer money using the booking code in the narration field.
- Everyone pays the same amount, same code, but each transfer has:
    - A different **sender name** (Monnify captures this)
    - A unique **transaction reference**
## 3. System Receives Webhook from Monnify
- On receiving a successful transfer webhook:
    - Extracts: amount, narration, sender name, sender bank, reference
    - Matches narration to an **active drop-in slot**
    - Logs payer as a **ticketed participant**
    - Deduplicates using the transaction reference
## 4. Ticket Issued
- A digital ticket is generated and sent via SMS/email
    - Includes player name, time, date, booking code, and amount
- Ticket has a **QR code** linking to a `/verify` page
## 5. Security Checks at the Gate
- Player shows ticket
- Security verifies:
    - Date matches today
    - Time matches current session
    - Name matches sender
- Can optionally scan the QR code to validate it
---
# How Funds Are Handled (Needs Verification)
- Each venue gets a **dedicated virtual account**, created using their BVN and bank info.
- Incoming payments are held by **Monnify**, not our platform.
- Monnify **automatically settles funds to the venue’s real bank account at 10 PM daily**.
- We do not hold, manage, or withdraw funds. We just track and match them.
---
# Edge Case Handling

| Case                  | How It’s Handled                 |
| --------------------- | -------------------------------- |
| No code in narration  | Try to match by amount + time    |
| Wrong/invalid code    | Log as unmatched, show in admin  |
| Duplicate payment     | Skip using transaction reference |
| Payment after session | Flag for manual review           |

---
# Internal Notes 
- Each virtual account is tied to a Monnify **subaccount**
- We assume Monnify sweeps payments to the venue’s bank automatically (with external sweep enabled). This needs confirmation.
- If not, we may need to enforce 100% split to the subaccount — confirm with Monnify
- Consider whether to show a separate **Payments** page for listing unmatched or historical payments. If we don't, users will have to navigate to a booking to view payments on it.
- How much do Monnify take from a transaction when it comes through the virtual account? How much are we keeping for ourselves as a transaction fee?
---
# Summary
> This feature allows drop-in football venues to collect payments through virtual accounts, issue digital tickets automatically, and reduce fraud or reconciliation errors.  
> Funds go straight to the venue. We handle payment matching and ticket generation.
