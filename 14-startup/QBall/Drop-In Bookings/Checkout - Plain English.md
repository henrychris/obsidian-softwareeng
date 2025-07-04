# ⚽ What's the Problem?

Many football venues in Nigeria run **drop-in sessions** — players just show up, pay, and join a game.

But there’s a major headache:

> **Venue managers can’t easily tell who paid and how much they collected.**

They currently use **paper tickets**, which are messy, easy to abuse, and hard to track.

---
# 💡 What Are We Building?

We’re building a simple system that:
* Lets venues set up drop-in sessions
* Lets players **pay by scanning a QR code**
* Automatically issues a **digital ticket** after payment
* Helps venue managers clearly see who paid and how much was received
---
# 🔁 How It Works

### 1. The Venue Creates a Drop-In Slot
* The manager logs into our dashboard
* They create a new drop-in session (e.g. 6–8 PM today)
* A **QR code** is generated for that session
* The QR is printed and placed at the venue gate
---
### 2. Players Scan and Pay
* When players arrive, they scan the QR with their phone
* They see the session info (date, time, price)
* They enter their **name and email**, and complete payment
---
### 3. We Track the Payment
* As soon as payment is made, we get notified
* The system records the payment and links it to the session
* Each payment is automatically matched to a player and time
---
### 4. Ticket is Generated
* After paying, the player is shown a **digital ticket**
* This ticket includes their name, the session time/date, and a QR code
* They can show this ticket on their phone or print it
---
### 5. Security Checks at the Gate
* Player shows the digital ticket
* Security verifies that:  
	- The ticket is for today’s session
	- The name matches what’s on the screen
	- Optionally, they can scan the QR to double-check

---
# 💸 How Payments Work
* Every venue gets a unique account (subaccount)
* When someone pays, the money goes **directly to the venue’s bank account**
* We take a small cut automatically — the rest goes to the venue
* **We don’t hold the money** — we just process and track it
---
# 🛡️ What About Edge Cases?

| Situation                      | What Happens                                             |
| ------------------------------ | -------------------------------------------------------- |
| Player pays late               | Payment is flagged for review                            |
| Player tries to pay twice      | System ignores duplicate payments                        |
| Payment fails halfway          | No ticket is issued                                      |
| Someone doesn’t finish payment | No worries — they can try again by scanning the QR again |

---
# 📌 In Summary

> This system helps football venues collect payments easily, issue digital tickets, and know exactly who paid — all without paper, confusion, or stress.

Players just scan → pay → show their ticket.
Venues get paid automatically. Everyone wins. 🏆
