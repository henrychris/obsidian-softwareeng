## Tier 1: Fix the Foundation (unblock everything else)

These are blockers. Nothing meaningful can be built on top of broken state transitions.

**1. The Booking Status Machine**
Your own todo has this roughed out. The drop-in flow is clear (`Confirmed → Cancelled`). Get this locked in and tested before anything else. Everything downstream — refunds, late payments, cancellation policy — branches from status.

**2. Late Payment Gate**
You already know payments are being accepted after a session starts. This is a trust problem. A GM shares a link, and theoretically someone can "pay" after the game ended. Fix the payment window guard server-side (don't rely on the frontend).

**3. Lock Transactions on Update**
Also already in your todo. Concurrency bugs here will corrupt money data. This should have been done before launch.

---
## Tier 2: The Wallet — but you need to think about it more carefully

You're right that a wallet simplifies refunds. But the design decision matters enormously, because it determines whether the wallet is a liability simplification feature or a product moat.

There are three options:

- **GM-side credit only** — GM cancels a session → they manually issue credit codes or handle refunds externally. Simple to build, but puts the burden on the GM and doesn't build any ecosystem lock-in.

- **Player wallet (email-linked, no account required)** — When a player pays with an email address, that email has an implicit wallet. If a session is cancelled, credit is issued to that email automatically. On next purchase, the system detects an existing balance and applies it. The player doesn't need to sign up for anything — it just works.

- **Escrow/hold model** — Payment is held and only released to the GM after the session happens. If cancelled, automatic card refund. No wallet needed. But settlement is slow, and slow settlement is already your biggest blocker (see: the ALAT situation).

**The right answer is the email-linked player wallet.** Here's why:

1. It solves refunds without requiring player sign-up (low friction)
2. Any credit balance creates a reason for the player to come back through QBall specifically
3. It's the first step toward a player identity, which unlocks everything in Tier 3
4. It makes the GM look more professional — "your refund is in your QBall balance" vs "I'll sort you out on WhatsApp"

The wallet doesn't need to be complex. Start with: a `PlayerWallet` table keyed by email, a balance, and a credit history. That's it. Refunds debit the GM's settlement amount and credit the player's email-linked balance. At checkout, check for an existing balance and apply it.

---
## Tier 3: The Cancellation Policy (directly tied to the wallet)

Your todo says "requires policy on refunds. Should be left up to game managers." That's the right instinct. GMs should be able to configure:

- **Full wallet credit** if cancelled >X hours before kickoff
- **Partial credit** (e.g. 50%) if within X–Y hours
- **No refund** inside Y hours of kickoff

This is just settings on `GameManagerSettings`. The cancellation handler reads the policy, calculates the credit amount, and issues it to the player wallet. The GM absorbs any fee difference based on their policy.

This is also a selling point. GMs can advertise "full refund up to 48 hours before" — it makes them look legitimate and reduces the friction for players who are unsure.

---
## Tier 4: Player Identity (the biggest unlock)
Right now, players don't exist in your system. They're just email addresses attached to `TicketHolder` rows. The GM has no CRM. They can't see who their regulars are, who always pays on time, who bought three bundles in a row.

A lightweight player account — created automatically when someone pays for the first time — would give you:

- **GM regulars dashboard**: who has attended the most sessions, total spend per player
- **Waitlists**: when a session fills up, players can join a waitlist and get notified/auto-charged when a spot opens
- **Player booking history**: they can look up their past sessions and upcoming ones

This doesn't need to be a big feature. The player doesn't need to "sign up." Their first payment creates a `Player` record linked to their email. If they later want to claim their history, they use the Magic Link flow. Done.

---
## Tier 5: The Differentiated Feature — Team Generation
This is the thing in your todo that I think you're underselling. Let me reframe it.

Right now QBall solves: **"how do I collect money before kickoff."**

The next problem it could solve: **"how do I make sure the game is actually fair."**

Here's the full picture of what you've already thought about in that todo:

- Players declare their position (defence, midfield, attacker) when booking
- Premium price for groups who want to play as a pre-formed team
- Auto-generate balanced teams from the player pool
- A "selection pool" for solo players who get assigned to teams

If you build this, QBall is no longer just a payment tool. It becomes the platform that runs the whole session — payment, attendance, and team sheets. No other product in this space does that. Footy Addicts handles player discovery but not payments. CourtReserve handles venue bookings but not team generation. You'd be the only one doing the full loop.

The sequencing would be:
1. Add `Position` to the ticket purchase form (enum: `Goalkeeper`, `Defender`, `Midfielder`, `Attacker`)
2. Add team generation in the dashboard — a button that takes the confirmed player list and splits them into balanced teams
3. Add the premium "bring your team" pricing tier (already in your todo under pricing tiers)
---
## Tier 6: Check-in Flow
You have the verify endpoint. Players have QR codes in their ticket emails. This is 80% done. The gap is the UX — a GM at the gate needs a fast, mobile-friendly scanner UI. This is a frontend job more than a backend one, but it's a hygiene feature that makes the product feel complete.

---
## Reprioritised Roadmap

| Priority | What | Why |
|---|---|---|
| 1 | Booking status machine + late payment gate | Foundation — everything branches from here |
| 2 | Transaction locking | Correctness — money data can't be corrupted |
| 3 | Email-linked player wallet | Unblocks refunds, creates ecosystem lock-in |
| 4 | GM cancellation policy settings | Gives GMs control, uses the wallet |
| 5 | Auto-created player profiles | Unlocks CRM for GMs, enables waitlists |
| 6 | Waitlists | Maximises attendance, GMs stop guessing demand |
| 7 | Player regulars / GM CRM view | Retention — GMs know who to chase with bundles |
| 8 | Position declaration at checkout | Seeds team generation |
| 9 | Team sheet generator | The differentiating feature |
| 10 | Check-in scanner UX | Completes the day-of experience |
| 11 | Settlement speed (ALAT) | Critical business issue — run in parallel with above |

---

The through-line here is: **you're building a platform for recurring football communities, not a one-off booking tool.** The booking link is the acquisition channel. The wallet is the retention mechanism. The team sheet is the thing that makes GMs never want to leave. All three are within reach.