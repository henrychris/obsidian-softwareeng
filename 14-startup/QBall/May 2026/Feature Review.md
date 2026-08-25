## Full Feature Inventory — QBall Admin
### Authentication (all users)
- Google OAuth login/logout
- Magic Link request + verify (used by Game Managers specifically — they can't use Google auth)
- Refresh token + logout all devices
- Username availability check
### User Profile (all users)
- Get/update profile
- Upload profile picture
- Delete account
- KYC — submit and retrieve identity/bank information
- Address management
- Favourite venues (save/remove)
- Sub-accounts — create a Monnify settlement account, assign/unassign venues to it

---
### Game Manager (the current focus)
#### Onboarding
- Submit a Game Manager application
- Admin approves or rejects the application (manual review gate)
#### Settings
- Get/update settings: display name, public-facing slug, default drop-in price, timezone, and an "absorb transaction fees" toggle
#### Dashboard
- Next upcoming session (with countdown)
- Today's sessions list
- Stats: player count this week, total upcoming sessions
#### Calendar
- View sessions in a calendar format
#### Sessions (Bookings)
- Create a session — title, venue, start/end, price per player, optional player cap, notes, public/private toggle
- List all sessions
- Search sessions — full-text by title or booking code, date range filter, status filter, and an `EligibleForBundle` filter
- Get a single session with full detail
- Update a session — title, time, venue, price, player cap, notes, public/private (player cap is locked once the session is in a bundle)
- Cancel a session
- Conflict detection — blocks double-booking the same venue at the same time
#### Tickets
- Get all tickets for a session
- Manually issue a ticket to a named player (first name, last name, email, optional phone) — sends them a ticket email via Hangfire job
- Void a ticket holder (removes them from headcount)
- QR code verification endpoint (public — used by a scanner at the gate)
#### Booking Bundles
- Create a bundle — group multiple sessions together, set a single price and a max holder count
  - Business rules: all sessions must be Confirmed, in the future, have a player cap set, share the same cap value, and not already belong to another bundle
- Get all bundles
- Get a single bundle with all sessions and holders
- Update a bundle (title, description, price, max holders)
- Delete a bundle
- Get bundle holders
- Manually grant a bundle holder (add someone to a bundle outside of the payment flow)
#### Revenue
- Revenue overview: total all-time, this month, last month (transaction counts included for each)
#### Transactions
- Paginated transaction history (bookings + bundles)
#### Venue Search
- Search the venue catalogue to find a pitch to host at (spatial, not ownership)

---
### Public / Player-Facing (Game Manager side)
- Get a game manager's public profile by slug
- List a GM's upcoming public sessions (paginated)
- Get a single public session
- List a GM's active bundles
- Get a single bundle with spots remaining
- Initiate payment to join a session (reserves a spot, returns a checkout URL, expires in 30 min)
- Initiate payment to purchase a bundle (same reservation model)
- Check transaction status (works for both session and bundle payments — also requeries the payment provider if still pending)

---
### Venue Manager (pitch owners — separate persona)
- Create/get/update a venue
- Manage operating hours
- Photo upload and management
- Pricing tiers
- Bookings calendar
- Create/manage bookings on behalf of customers
- Customer database (profiles, last visit, contact details)
- Revenue and transaction analytics
- Venue dashboard
- Sub-account management
- Notifications
### Admin (internal ops)
- Approve/reject Venue Manager applications
- Approve/reject Game Manager applications
- Migrate user to Game Manager role

---
## Observations (outside eyes)
Now that I've seen everything laid out — here are my honest observations on where the product stands and what's pulling it in different directions.

**You have two separate products that share an auth layer.** The Venue Manager and Game Manager personas have almost nothing in common at the use-case level. A pitch owner's core job is calendar management, customer profiles, and revenue tracking. A game manager's core job is getting paid before kickoff and not chasing people. These are completely different workflows with different mental models. The only thing they share is "football" and "payments."

**The Game Manager product is more coherent and more differentiated.** The bundle mechanic is genuinely interesting — it solves a real, specific problem (recurring group players who you don't want to re-chase every week). The public booking link + QR ticket flow is clean. There's a tight story there: *create a session, share a link, players pay, you scan them in.* That's the whole loop and it works.

**The Venue Manager product risks becoming a generic booking system.** Pitch owners already have options (Bookteq, CourtReserve, etc.). The features you have (calendar, pricing tiers, customers) are table-stakes in that space. Unless there's a differentiated angle there — like integration with the Game Manager side so GMs can discover and book pitches directly through QBall — it's hard to see why a venue owner picks you over an incumbent.

**The two personas don't talk to each other yet.** A Game Manager searches the venue catalogue to find a pitch. A Venue Manager manages their pitches. But there's no transactional loop between them — a GM can't actually book a pitch through the platform, and a Venue Manager doesn't see GM demand. That connection, if you built it, would be the thing that makes both sides of the product more valuable: GMs get pitch discovery, Venue Managers get a demand channel. Right now it's two separate dashboards that happen to share a database.

**The Game Manager side has one meaningful gap**: there's nothing for players. The entire player experience is a single-use public URL — they pay, get a ticket email, show up. There's no player account, no history, no way to follow a GM they like. That's fine as an MVP, but it also means the GM has no CRM — they can't see who their regulars are, who always books, who bought bundles. The `Customer` entity exists on the Venue Manager side. It might be worth asking whether GMs need something similar.

**The bottom line on identity:** QBall is currently trying to be "Stripe + Eventbrite for football hosts" (Game Manager) and "a booking system for pitch owners" (Venue Manager) at the same time. Those are both viable products, but they'll compete for your focus. The cleaner story right now — especially given the bundle mechanic — is the Game Manager side. That's where the clearest pain point is ("I'll transfer later") and the clearest differentiation is (bundles + QR tickets + no monthly fee).