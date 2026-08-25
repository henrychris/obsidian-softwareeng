## 1. What This Stage Is

- Project review is done — they liked it enough to bring you here
- This is about your engineering story, technical decisions, and communication
- Tone: communication, collaboration, deliberate drive to improve
---
## 2. Two-Minute Intro — Triggers

- Product engineer, not just backend — 0 to 1 by myself
- Wanted consulting → landed fintech (ErrandPay) → never left
- Limestone → LunixPos → QBall on the side (ticketing + Monnify — "forgive me for using your rivals")
- Why Kora: scale + hard problems + strong teammates. Haven't hit the traffic that stretches an engineer
---
## 3. Stories
### ErrandPay — Outbox / Webhook Reliability
**Q: Tell me about a time you improved system reliability.**
- Webhooks dropping twice a week → customer complaints
- Root cause: non-atomic publish — DB write succeeded, webhook send failed silently
- Fix: Transactional Outbox — write event to outbox table in same DB transaction, background job delivers
- Result: complaints stopped entirely
### Limestone — Docker / Unblocking the Team
**Q: Tell me about a time you took initiative to unblock your team.**
- Mid-migration, API gateway went down, frontend + mobile blocked
- Set up Docker Compose replicating the full service topology locally
- Saved ~4 weeks of blocked development time
### LunixPos — N+1 Fix
**Q: Tell me about a performance problem you diagnosed and fixed.**
- Slow customer data endpoint, real user pain
- No APM — only MongoDB Atlas slow query logs
- Created 1000 dummy records, used Postman test runner to profile before/after
- Found 200+ DB calls per request → replaced with single aggregation pipeline
- P90 dropped to under 1.6s
### LunixPos — Cross-Region Latency
**Q - Tell me about a performance win you drove.**
- Backend on `us-west-2`, DB on `us-east-1` — silently killing latency
- Moved DB, measured a week later
- Median: 250ms → 20ms. P90: 600-700ms → 130-150ms
### Limestone — NATS Library
**Q - Tell me about something you built from scratch that others relied on.**
- Built internal wrapper around NATS, published as NuGet package to our internal feed on Azure
- JetStream for message persistence, connection pooling, auto-stream creation via .NET reflection
- Documented for the team
- **Depth**: made a design mistake — used NATS request-reply (distributed monolith). Caught early, fixed by duplicating data across service DBs and using eventual consistency
### Limestone — Azure App Config / DX
**Q - How have you improved developer experience at a previous company?**
- Config variables scattered in workflow files and env files
- Moved to Azure App Config with environment labels and prefixes
- New devs only needed Azure CLI setup — application picked up config automatically
### Limestone — PIN Storage Bug
**Q - Tell me about a time you caught something important before it caused a problem.**
- `pin` sent as string, typed as `byte[]` in request model when creating a wallet
- .NET model binder silently converted to array of bytes, which were saved in DB as a hex string — PINs reversible by anyone with DB access
- Ran migration to properly hash and salt all PINs, updated validation logic
### QSet — Shipped Fast
**Q - Tell me about a time you shipped something fast**
- Watched a football session collapse into a 30-minute queue argument, session ended without playing
- Went home, built working prototype that night in HTML/JS/CSS
- Demoed next day, immediately spotted missing undo/redo, added before next session
- Rewrote in TypeScript + Svelte — currently live, 20 weekly active users
### LunixPos - Fiscal Receipts / System Design
**Q: How do you approach system design decisions? Give an example.**
Three things I think about:
- What's likely to change → design for swappability
- What's expensive → push to background
- What's complex → hide behind a simple interface

Example: fiscal receipts at LunixPos. Alanube's API was extremely complex — tax bracket logic, billing indicators per product type, lots of data wrangling.
- Designed IFiscalReceiptProvider with clean methods: issueReceipt, getReceiptStatus, processWebhook
- AlanubeProvider implements the interface, handles all complexity in private methods
- Caller just does provider.issueReceipt(order) — knows nothing about Alanube's quirks
- Switching providers = write a new class. Nothing else changes.

---
## 4. Kora Assessment Walkthrough
### Core design points
- **Double-entry ledger** — every transaction = debit + credit. Balance is denormalised for reads, ledger is source of truth
- **`FOR UPDATE`** — row-level lock on wallet before every balance mutation. Prevents race conditions
	- mention deadlock prevention issue for recipient wallet?
- **Idempotency** — unique `reference` on Transaction and WebhookEvent. Duplicate returns cached result
- **Payment factory** — `IPaymentProvider` interface, factory reads provider from env. New providers don't touch business logic
- **Async payout** — returns PENDING immediately, webhook finalises it, sync job is the fallback
### Known weaknesses (if asked)
- Reversal logic duplicated between webhook handler and sync job — should be a shared `finalisePayout` function
- `process-payout-webhook` should resolve the provider from the `provider` field on the webhook record, not env
- `sync-pending-payouts` should ignore transactions older than a threshold — dead ones should go to manual intervention
	- it should get provider instance using `transaction.provider`.
	- it should be provider agnostic when fetching pending transactions.
- Testcontainers segfault with Bun — documented workaround, would invest more in a real codebase
---
## 5. Technical Concepts
### Row-level vs Table-level locking
- Table lock = blocks everyone on the entire table. Fine for migrations, fatal for a live API
- Row lock (`FOR UPDATE`) = only blocks concurrent ops on that specific row
- Used in: `top-up.ts`, `payout.ts` (wallet row), `sync-pending-payouts` (transaction row)
- Without it: two concurrent requests read same stale balance, both proceed, one clobbers the other
### Deadlock prevention
- Deadlock = A waits for B's lock, B waits for A's lock, forever
- In `transfer.ts`: only lock sender wallet — recipient balance only goes up, increment is atomic
- Increment is safe without a lock. SET is not — it bakes a stale value into the write
- Proper fix: lock both wallets, always in consistent order (lower wallet ID first)
### Optimistic vs pessimistic locking
- **Optimistic:** read + note version → ready to write → check version hasn't changed → retry if it has
- **Pessimistic:** acquire lock before reading → nobody else can touch the row until commit
- Pessimistic is right for money because:
  - By the time an optimistic conflict is detected, you may have already called the payment provider — you can't un-call an external API
  - Under high traffic, optimistic causes retry storms — 9 losers retry, some lose again
### Transaction isolation levels
- **READ COMMITTED** (Postgres default): each statement sees latest committed data at the moment it runs
- **SERIALIZABLE**: entire transaction sees one consistent snapshot from start to finish
- READ COMMITTED is fine for the transfer because `FOR UPDATE` does the serialisation work — nothing can commit to that wallet row while you hold the lock
- SERIALIZABLE matters when decisions are based on **aggregate reads** (counts, sums) — row locks can't protect something that doesn't exist yet
- Example: max 3 pending transfers. Two users both read count = 2, both pass, both insert. SERIALIZABLE detects the conflict at commit time and rejects one. This is called **write skew**
### Idempotency
- **Why**: client retries, duplicate webhook delivery, sync job + webhook race
- API endpoints: check `reference` before processing, return cached result if found. DB unique constraint as backstop
- Webhook handler: check `WebhookEvent.reference` first, acknowledge silently if duplicate
- Sync job race: `FOR UPDATE` on Transaction row + status check. Only one process enters the critical section. Second one sees non-PENDING status and exits
### Outbox pattern
- Problem: DB write + webhook send are two separate operations. DB can succeed and webhook can fail — inconsistent state
- Fix: write outbox record in same transaction as business data. Background job delivers it with retries
- Tradeoff: at-least-once delivery. Consumers must be idempotent (same as your webhook handler)
### Double-entry bookkeeping
- Every movement = debit one wallet + credit another. Net change to system: zero
- Balance field = denormalised cache for fast reads
- Ledger = source of truth. Can always recompute balance by summing entries
- If balance is corrupted: recalculate from ledger. If there's a discrepancy: ledger wins
### N+1 queries
- One query to get a list, then N queries to get related data for each item
- Detection: read the code and look for DB calls inside loops
- Fix: SQL joins, Prisma `include`, MongoDB aggregation pipeline, DataLoader (batch IDs into `WHERE id IN (...)`, store result in a map)
### Microservices
#### Service Decomposition
- Split by domain (business responsibility), not by technical layer
	- Kora example domains: identity, wallets, payouts, notifications, compliance
- Key question: what changes together vs independently?
	- Split when you need independent deployability or independent scaling
- Don't split prematurely — a modular monolith beats a distributed monolith
#### Sync vs Async Communication
**Synchronous (HTTP/gRPC)**
- Caller waits for response
- Good for: queries needing immediate answers, external-facing APIs
- Risk: temporal coupling, cascading failures, caller dies if callee is slow
**Asynchronous (message queues)**
- Caller publishes and moves on
- Good for: work without immediate result, decoupling, load levelling during spikes
- Risk: harder to reason about, eventual consistency, silent failures in queues

The assessment mixes both correctly:
- Payout endpoint = sync HTTP → client gets PENDING immediately
- Webhook processing = async job queue → processed when ready, retried on failure
#### API Gateway
**What it does:**
- Routes requests to the right service
- Handles auth (verify JWT once, not in every service)
- Rate limiting, SSL termination, load balancing

**The Limestone story:**
- Gateway went down → frontend and mobile completely blocked
- Fix: Docker Compose replicating service topology locally — teams bypassed gateway entirely
- Lesson: services should be testable without the gateway in development
---

## 5.1 Other Questions
### How would you handle distributed locks if this were across multiple service instances?
- Using Redis, set a key - only if it doesn't exist with an expiration time.
- Expiry is critical: if the process crashes before releasing, lock auto-expires instead of blocking forever
- The hard part is choosing the correct TTL, which would probably require studying how long the operations usually take.
### How would you scale this wallet service to handle thousands of concurrent transactions?
- **DB-Level**: Row-level locking already handles concurrency. Add connection pooling (PgBouncer) + read replicas for read-heavy endpoints
- **App-Level**: Stateless → horizontal scaling behind a load balancer
- **Problem that creates**: distributed locking → Redis (see below)
- **Payouts**: already async via job queue — naturally absorbs spikes
### How would you design for eventual consistency?
- Each service publishes an event when something notable happens
- Other services consume events and update their own data stores independently
- System is temporarily inconsistent but eventually every node has processed the event
- Handle out-of-order events with versioning: compare incoming version to current. Newer → apply. Older → discard. Duplicate → idempotent handler
#### How about in a payout flow?
- When a user requests a payout, we debit their wallet immediately and mark the transaction PENDING.
- We wait for an event to arrive from the payment provider. Meanwhile, the system is in an intermediate state where money has left the wallet but the recipient is yet to receive value.
- Event comes in as a webhook, they system triggers a success or failure workflow.
- It is guaranteed that eventually, the transaction reaches a terminal state: Completed or Failed.
### Tell us about a time you had to work across teams / with non-engineers
- At most jobs I got vague specs from PMs or the CEO — standard for early-stage startups
- I elicit real requirements: ask questions, research, cross off out-of-scope items — before opening the editor
- Work with QA constantly. They surface bugs and sometimes expose incorrect design assumptions from their end-user perspective
- I like it — every function has a different view of the product and it all adds up when trying to build something great
### What's your experience with distributed systems / payments / high-scale systems?
- i have not operated at Kora scale - that's part of what draws me here.
- At ErrandPay I worked on payments but it was a small startup, 20 million naira a day in volume at the time.
- What I've built up is the patterns — idempotency, the outbox pattern, double-entry ledger — and I've applied them in real systems. 
- The QBall ticketing product handles payments in production today. 
- I'm confident in the fundamentals; the missing piece is operating at the scale that stress-tests them, and that's exactly what I want here.
### How do you handle disagreements on technical direction?
- Make the disagreement concrete: what does X cost in time/complexity/debt vs what do we gain
- Advocate for what I think is right, but not precious about it — if someone has a better argument, I change my mind
- We go all-in as a team once a decision is made
### How do you handle database indexing and query optimisation on large transaction tables
- Depends on query patterns — start by understanding what queries run most often

- Common transaction table queries and indexes:
	- Fetch by wallet/user → index on (walletId, createdAt DESC)
	- Fetch by status → index on status (consider partial index on status = 'PENDING' — small, hot subset)
	- Fetch by reference → unique index
### How do you approach system design decisions? Give an example
I think about three things: 
- what's likely to change and whether I need to swap implementations; 
- what's expensive and could run in the background; 
- and how to hide complexity behind a simple interface.

A good example is a fiscal receipts feature I built at LunixPos. Fiscal receipts are documents companies issue to prove transactions were recorded for tax purposes. We used a provider called Alanube with an extremely complicated API — lots of data wrangling, tax bracket logic, different billing indicators per product type.

I designed an `IFiscalReceiptProvider` interface with clean methods like `issueReceipt`, `getReceiptStatus`, `processWebhook`. The `AlanubeProvider` class implements that interface and handles all the complexity internally — tax calculations, payload mapping, error handling — all in private methods the caller never sees.

The result: the endpoint that issues receipts just calls `provider.issueReceipt(order)` and knows nothing about Alanube's quirks. If we switch providers, we write a new class implementing the same interface. Nothing else changes.
### CAP Theorem
In a distributed system, it is impossible to guarantee the following three properties at the same time:
- Consistency: Every read sees the latest write
- Availability: Every request receives a response
- Partition Tolerance: The system continues to work despite network failures
## 6. Questions to Ask
- What does the backend stack look like today — fully Node/TypeScript or a mix?
- What's the biggest infra, reliability or DX challenge the team is actively working on?
- How does the team handle incident response when a flow breaks in production?
- What does the first 90 days look like for a new backend engineer?
- How does code review work — async or pairing?
- How much ownership do engineers have over technical decisions vs the lead?
---
## 7. Import Products
### What it is
Bulk product import handler at LunixPos. Merchants upload an Excel file with hundreds of products. Three product types: **simple**, **serialized** (IMEI-tracked), **variable** (size/colour variants).
### Flow
1. HTTP handler parses file, groups rows by `handle`, validates synchronously
2. Returns `{ action: "queued", importId }` immediately — client doesn't wait
3. Background job (Agenda) picks it up and processes in batches of 50
4. Real-time progress via WebSocket after each product
5. Summary email when complete
### Key Design Decisions
#### Sync validation, async processing
- Cheap work (parse, group, validate) stays in the request/response cycle
- Expensive work (DB lookups, SKU gen, bulk writes, inventory history) goes to background job
#### Batch processing (BATCH_SIZE = 50)
- Never holds the full dataset in memory
- Progress updates are granular, not 0% → 100%
- Each batch: process products → bulkWrite → next batch
- Collects all insert/update operations for the batch, fires one `bulkWrite`
- One MongoDB round trip per batch instead of one per product
#### Reference data pre-loading
- Before processing starts: one Promise.all fetches all vendors, categories, locations for the store
- Stored in Maps keyed by name/ID — O(1) lookup per product
- Eliminates potentially 1000+ individual DB queries on a large import
#### Websocket Progress Tracking
The client receives an `importID` in the response from the initial HTTP request. Client opens a WebSocket to `/ws/import-progress?import-id=<uuid>` when import starts. Server pushes progress updates after each product. Final completed message closes the connection.

**Why WebSocket, not polling**
- Polling = N HTTP requests over the import lifetime, client asks repeatedly
- WebSocket = one persistent connection, server pushes when ready
- For a progress bar updating after every product, push is cleaner and cheaper

**Websocket Map**
- `importSockets = new Map<string, WebSocket>()` — module-level, in-memory created in the route file.
- Keyed by importId — background job looks up the right socket per import
- Works fine for single-instance deployments
- Breaks with multiple instances — if the job runs on instance A but the client is connected to instance B, B's Map has no entry → client gets nothing
- Fix at scale: Redis pub/sub. Job publishes to a channel keyed by importId, every instance subscribes and forwards to its local sockets

**readyState checks**
- Background job is async — by the time it sends, client may have disconnected
- Check readyState === 1 (OPEN) before every send
- If readyState === 3 (CLOSED), delete from Map — don't accumulate stale references
- Catch send errors, delete on ECONNRESET

 **Cleanup**
- `connection.on("close")` deletes the entry from the Map
- Without it, every completed import leaves a dead socket reference — Map grows unbounded

---
## 8. Day-Of

- [ ] Test video/audio the night before
- [ ] Resume + JD on second screen
- [ ] This sheet on second screen
- [ ] Water nearby
- [ ] 5 min before: close Slack, Discord, notifications
- [ ] Blank on a question → "Let me think about that for a second." Don't ramble
- [ ] You can ask them to repeat or clarify

> You delivered a strong assessment under real pressure. They've already seen your work and liked it. Walk in with that.