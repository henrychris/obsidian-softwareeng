## 1. What to Expect

This is the Team Interview Stage — a 60-minute conversation where Kora's engineers explore your professional background in detail and introduce you to the team. The project review already happened when they read your assessment and passed you, so this is less about grinding algorithms and more about:

- Telling your engineering story clearly and confidently
- Discussing past technical decisions and why you made them
- Demonstrating that you can think at scale and communicate well
- Showing genuine interest in what Kora is building

> 💡 **KEY TONE** The JD emphasises communication, collaboration, and deliberate drive to improve — lean into those throughout.

---
## 2. Two-Minute Intro
> I'm Henry Ihenacho. Originally, a backend engineer but I prefer to think of myself as a product engineer these days. I like the idea of being able to take a product or feature from 0 - 1 by myself. I have roughly 3 years of experience.

> Interestingly, I originally wanted to work in consulting. You know, Big 4, BCG and friends. But unfortunately, the first role I got was ridiculously far from home and I couldn't afford to make that trip everyday. I ended up working at a fintech called ErrandPay and I have been in tech ever since.

> Most recently, I've been at LunixPos working on a node js backend and before that I was a backend engineer at Limestone where I led a monolith to microservices migration using C# and NATS. On the side, nights and weekends, I build football tech applications with a friend of mine. One of these includes a ticketing product with a payment integration using Monnify - forgive me for using your rivals.

 > I'm drawn to Kora because of the scale, structure and the level of problems that await. I have worked at a lot of startups and I have worn many hats. But I am yet to really work with the level of traffic that makes an engineer reach their full potential. 

> So scale + excellent teammates + hard problems. That's exactly what I'm looking for at this stage of my career. I want to learn & I want to leave an impact.
---
## 3. Your Strongest Stories (STAR Format)
### ErrandPay — Outbox Pattern for Webhook Reliability

**Q: Tell me about a time you improved system reliability.**
- **Situation:** Webhook notifications at ErrandPay were dropping twice a week. Customers complained and it eroded trust.
- **Task:** Find a durable solution without significant rework of existing flows.
- **Action:** Implemented the Transactional Outbox pattern in C#. Instead of firing webhooks inline, I wrote events to an outbox table within the same DB transaction as the business operation. A background job then reliably delivered them, with retries.
- **Result:** Customer complaints about notification drop-offs stopped entirely.

**Key talking point:** The original failure was a non-atomic publish. The DB write would succeed but tranisent errors when sending the webhook would cause them to 'vanish'. The outbox made the publish atomic.

---
### Limestone — Microservices Migration & Docker Workaround
**Q: Tell me about a time you took initiative to unblock your team.**
- **Situation:** We were mid-migration from monolith to microservices at Limestone. The API gateway went down for an extended period — frontend and mobile teams were completely blocked.
- **Task:** Find a way to keep development moving without the gateway.
- **Action:** Set up a local Docker environment that replicated the Limestone 2.0 service topology using Compose. This let frontend and mobile teams run the full stack locally and continue their work.
- **Result:** Saved a 4 weeks of development time - which is how long it took the DevOps team to get it running.
- **Depth**: I made a mistake when designing the system which led to me using NATS request-reply pattern when communicating between services. This meant I was building a distributed monolith, not microservices. Thankfully, we caught this early and duplicated the necessary data across service databases, relying on eventual consistency to ensure they *eventually* had the same data within.  

---
### LunixPos — N+1 Query Optimisation
**Q: Tell me about a performance problem you diagnosed and fixed.**
- **Situation:** A critical customer data endpoint at LunixPos was slow — causing real user pain.
- **Task:** Diagnose and fix without introducing risk to the data layer.
- **Action:** Identified an N+1 query pattern — the code was making 200+ individual DB calls per request. Replaced it with a single MongoDB aggregation pipeline.
- **Result:** P90 response time dropped to under 1.6 seconds.

**Key talking point:** The process — profiling, logging, tracing — not just the fix:

The problem was reported by a customer and raised to us. At the time, there was no observability setup,  only MongoDB Atlas' reporting on slow queries. 

I created dummy data in the database (about 1000 records, in line with what the largest customer might have) & used Postman's test runner to profile the requests before and after my changes to measure the improvement.

---
### Kora Assessment
**Q: Walk  us through your assessment.**
Key points to hit:
- **Double-entry ledger:** Every transaction creates two ledger entries (debit + credit). The wallet balance is denormalised for performance but the ledger is the source of truth. Summing ledger entries always gives the correct balance.
- **Row-level locking (`FOR UPDATE`):** Used on the wallet row before every balance mutation to prevent race conditions and double-spends in concurrent requests.
- **Idempotency:** Both transaction references and webhook event references are unique-constrained. Any duplicate request returns the cached result rather than re-processing.
- **Payment factory + IPaymentProvider interface:** New providers can be added without touching business logic. Factory reads from env at runtime — could be extended to feature flags or automatic failover.
- **Async payout flow:** Payout is initiated and immediately returns PENDING. The webhook handler finalises it. The sync job is the fallback safety net for missed or **missing** webhooks.

**Known weaknesses to acknowledge if asked:**
- Duplicate reversal logic between `processWebhook` and `sync-pending-payouts` — should be extracted into a shared `finalisePayout` function.
- Testcontainers segfault with Bun — documented the workaround but would invest more time in a real production codebase.
- The `process-payout-webhook` job ought to get a payment provider instance using the `provider` stored on the webhook event db record. And the payment provider ought to have a method for fetching an instance using the provider enum. 
- The `sync-pending-payouts` job ought to ignore transactions older than a certain time period, else it risks reprocessing dead transactions that should require manual intervention.
## 3.5. Other Stories
### Q - Tell me about something you built from scratch that others relied on.
At Limestone, I built the library that wrapped NATS to make the microservices architecture work. I published it as an internal NuGet package using our Azure feed, added JetStream support for message persistence, connection pooling, auto-stream creation via .NET reflection when the application started, and documented it for the team.
### Q - How have you improved developer experience at a previous company?
At Limestone, our workflow files required specifying all configuration variables within them. Similar was also required for our environment variables. To make this easier, and to speed up onboarding for new developers, I moved our config to Azure App Config. I used environment labels and prefixes to distinguish them.

New developers would only need to setup the Azure CLI on their machines - a normal part of onboarding - and the .NET application would use that to pick up the correct configuration. 

The deployed application on each environment had its own identity setup with the azure CLI to authenticate it and get access to the secrets it needed.

### Q - Tell me about a time you caught something important before it caused a problem.
At Limestone, I found an issue with how wallet PINs were stored. 
From the frontend, the `pin` field was sent as a string, but another engineer had typed it as a byte array in the request model.
.NET's model binder would simply convert the string to a hexadecimal number. 

As a result, all PINs were stored in DB as their hexadecimal equivalent, meaning anyone with DB access could reverse any PIN in the system. 

This, I ran a migration script that properly hashed & salted all PINs. Of course, this included updating the code to validate a PIN before a transaction. 
### Q - Tell me about a performance win you drove.
At LunixPos, our applications were deployed using Render while our databases were hosted on MongoDB Atlas. I noticed our backend was on `us-west-2` and the DB on `us-east-1` — cross-region latency was silently killing response times. I moved the DB, measured the results a week later, and median latency dropped from 250ms to under 20ms (~92% faster), p90 from 600-700ms down to 130-150ms.

### Q - Tell me about a time you shipped something fast
This was for QSet. One of my favourite projects. My friend and I went to play football at a pitch and at some point, the various teams started to argue over who would play next, and this went on for over 30 minutes. We eventually ran out of time as the sun went down. The session ended up being wasted.
We thought of a possible solution for this,went home and built a working prototype that same night using HTML/JS/CSS with Claude.
We demoed it the very next day. It worked. We immediately identified a new problem and added undo/redo before the next session. Eventually, I rewrote it in TypeScript + Svelte. It's currently live with 20 weekly active users + a fresh design.

---
## 4. Technical Topics to Brush Up On
The JD mentions distributed systems, high throughput, microservices, and database optimisation. You won't be tested algorithmically, but be ready to discuss these fluently.
### Concurrency & Locking
#### **Row-level locking vs table-level locking**
A **table-level lock** blocks every reader and writer on the entire table. It's a blunt instrument — useful for bulk migrations, useless for a live payments API where thousands of users might transact simultaneously.

A **row-level lock** (`SELECT ... FOR UPDATE`) locks only the specific row(s) you're touching, letting everyone else continue in parallel.

**I used it in three places:**
```ts
// top-up.ts
SELECT * FROM "Wallet" WHERE "userId" = ${user.id} FOR UPDATE

// payout.ts
SELECT * FROM "Wallet" WHERE "userId" = ${user.id} FOR UPDATE

// sync-pending-payouts.job.ts
SELECT id, status FROM "Transaction" WHERE id = ${transaction.id} FOR UPDATE
```
**Why it was necessary:** Without the lock, two concurrent top-ups could both read `balance = 5000`, both decide that's enough, and both increment — but since they read the same stale value, one write clobbers the other. The `FOR UPDATE` forces the second request to wait until the first transaction commits, so it reads the *updated* balance.
#### Deadlock Prevention
A deadlock is when Transaction A holds a lock that B needs, and B holds a lock that A needs. They wait on each other forever.

In `transfer.ts`, I lock the **sender first**, then fetch the recipient without locking them (Prisma ORM call, no `FOR UPDATE`) since I only need to prevent double-spends from the sender's side. The recipient's balance only goes up using an **increment**, so a race there isn't dangerous.

This only works because I chose to **increment** (Prisma performs this operation atomically) instead of **setting the value**. 

```
Scenario - Problem with SET

Time  Transfer (+500)                    Payout (-300)
----  --------------------------------   --------------------------------
T1    SELECT wallet → reads 1000
T2                                       SELECT wallet FOR UPDATE → reads 1000
T3    wallet.update SET balance = 1500   (still inside payout transaction)
T4                                       wallet.update SET balance = 700
T5    commit                             commit
```

```
Scenario - Increment

Time  Transfer                           Payout
----  --------------------------------   --------------------------------
T1    UPDATE SET balance += 500          (waiting for row lock)
T2    commit → balance is 1500
T3                                       UPDATE SET balance -= 300
T4                                       commit → balance is 1200
```

Ideally, I'd lock both rows and make sure to **always acquire the locks in the same order**. This is usually done by ordering them, something like:

```ts
// Lock both wallets in consistent order (lower ID first)
const firstId  = senderWallet.id < recipient.wallet.id ? senderWallet.id : recipient.wallet.id;
const secondId = senderWallet.id < recipient.wallet.id ? recipient.wallet.id : senderWallet.id;

await tx.$queryRaw`SELECT id FROM "Wallet" WHERE id = ${firstId}  FOR UPDATE`;
await tx.$queryRaw`SELECT id FROM "Wallet" WHERE id = ${secondId} FOR UPDATE`;
```

#### Optimistic vs pessimistic locking
**Optimistic:** Read a record and note a version. Before committing changes, check if this version has changed. If it has changed, abort the transaction and restart.
**Pessimistic:** Lock the record for exclusive use until the transaction is complete. It has more integrity but must be designed carefully to prevent deadlocks.

I used **pessimistic** throughout — correct for a wallet balance. Imagine if using **optimistic**, and the version changes **after** calling the external provider and causing an external side effect. How does one roll that back? 
Even if there were no side effects, under high traffic **optimistic** causes problems because if 10 concurrent requests are made and one succeeds fastest, nine others have to retry and some lose on the next round.
**Pessimistic** locking prevents these scenarios from **ever occuring**

Optimistic locking looks like:
```sql
UPDATE wallet SET balance = balance - 100, version = version + 1
WHERE id = ? AND version = ?  -- fails if someone else updated first
```
You'd check `rowsAffected === 0` and retry. Fine for low-stakes, bad for money.
### Transaction Isolation Levels
#### READ COMMITTED (PostgreSQL default) vs SERIALIZABLE.
**READ COMMITTED** means every statement in your transaction sees the latest committed data *at the moment that statement runs*. Not at the moment the transaction started — at the moment each individual statement executes.

Look at your transfer flow:

```ts
// Statement 1 — reads committed balance at this moment
const [senderWallet] = await tx.$queryRaw`
  SELECT * FROM "Wallet" WHERE "userId" = ${sender.id} FOR UPDATE
`;

// ... some time passes, other transactions may commit ...

// Statement 2 — reads committed data at THIS moment, not T1's moment
const recipient = await tx.user.findUnique(...)

// Statement 3 — another read, another snapshot
await tx.wallet.update(...)
```

Each statement gets a fresh look at the world. This means if another transaction commits between your statements, your later statements will see that new data.

**SERIALIZABLE** gives the entire transaction one consistent snapshot from start to finish. Every statement sees the world as it was when the transaction began — nothing that commits after your transaction starts is visible to you, even if your transaction runs for a while.
##### **Why READ COMMITTED is fine for your transfer**
Because your `FOR UPDATE` on the sender wallet is doing the real work. The moment that lock is acquired, no other transaction can write to that row until yours commits. So even though READ COMMITTED would normally let you see new commits mid-transaction, there are no new commits *on that row* to see — you've blocked them all out.

The sequence:
```
T1: SELECT sender wallet FOR UPDATE  ← lock acquired
T2: [any concurrent payout on same wallet waits here]
T3: read recipient, check balance, write entries, update balances
T4: commit  ← lock released
T5: [concurrent payout proceeds, sees updated balance]
```

Between T1 and T4, the sender wallet is frozen for everyone else. READ COMMITTED's "fresh read per statement" behaviour is irrelevant for that row because nothing can change it while you hold the lock.
##### Where SERIALIZABLE would actually matter
Imagine a rule: *a user cannot have more than 3 pending transfers at once*. Your check would look like:
```ts
const pendingCount = await tx.transaction.count({
  where: { userId: sender.id, status: 'PENDING' }
});
if (pendingCount >= 3) throw new Error('Limit reached');

// create the transfer...
```

Two users, Alice and Bob, both trying to send a transfer at the exact same time. The rule is max 3 pending transfers per user. Both of them currently have 2 pending.

```
Time   Alice's transaction              Bob's transaction
----   --------------------------       --------------------------
T1     COUNT pending → reads 2
T2                                      COUNT pending → reads 2
T3     2 < 3, check passes
T4                                      2 < 3, check passes
T5     INSERT transfer (now 3 pending)
T6     commit
T7                                      INSERT transfer (now 4 pending)
T8                                      commit
```

At T1 and T2, neither transaction can see the other's INSERT because neither has committed yet. That's READ COMMITTED doing exactly what it says — you only see _committed_ data, and at that point nothing new has been committed. So both read 2, both pass the check, both insert.

Under SERIALIZABLE, Postgres tracks that both transactions _made a decision based on the same rows_. When Alice commits at T6, Postgres notices that Bob's transaction read the same pending count that Alice just changed. It knows Bob's decision at T4 was based on stale information. So at T8, Bob's commit gets rejected with a serialisation error — his code has to catch that and retry.

The key thing to understand: SERIALIZABLE doesn't change what you _read_. It changes whether your _commit is allowed_ based on whether your reads are still valid. It's a check at the end, not a lock at the start.
### Idempotency in Payments
#### Why it matters
Networks fail. Clients retry. Webhooks get delivered twice. Without idempotency, a retry becomes a double-charge.

The three scenarios:
1. **Client retry** — user's app times out and resends the same request
2. **Webhook duplicate delivery** — Kora sends the `transfer.success` event twice
3. **Your sync job + webhook race** — both try to finalise the same payout
#### How I implemented it
**For API endpoints** — unique `reference` on the `Transaction` table:
```ts
// top-up.ts, transfer.ts, payout.ts — same pattern
const existingTransaction = await prisma.transaction.findUnique({
    where: { reference },
    include: { entries: true },
});
if (existingTransaction) {
    ok(res, mapToResponse(existingTransaction));
    return;
}
```
If the reference exists, return the cached result without re-executing. The DB unique constraint is the safety net if two concurrent requests slip through the application-level check simultaneously.

**For webhook events** — unique `reference` on the `WebhookEvent` table:
```ts
// kora.ts webhook handler
const existing = await prisma.webhookEvent.findUnique({ where: { reference } });
if (existing) {
    ok(res, null, "Event already received");
    return;
}
```

**For the sync job vs webhook race** — `FOR UPDATE` + status check:
```ts
// sync-pending-payouts.job.ts
const [locked] = await tx.$queryRaw`
    SELECT id, status FROM "Transaction"
    WHERE id = ${transaction.id}
    FOR UPDATE
`;
if (locked.status !== "PENDING") {
    // webhook already finalised it — skip
    return;
}
```

This is the most sophisticated one. The lock ensures only one process (sync job OR webhook handler) finalises a given transaction. The status check ensures that even if both acquire the lock sequentially, the second one sees the already-final status and bails.
#### At-least-once delivery and the sync job
Kora (like every payment provider) guarantees **at-least-once** webhook delivery — not exactly-once. The webhook *will* arrive, but may arrive late, or more than once.

Your sync job (`sync-pending-payouts`) is the safety net for the "late or never" case. It polls PENDING payouts and calls the provider's verify endpoint directly. If the webhook arrives later for something the sync job already finalised, the status check handles it gracefully.
### The Outbox Pattern
#### The dual-write problem
You have two things to do atomically:
1. Write to the database (e.g. mark order as paid)
2. Publish an event or send a webhook

If you do them sequentially — DB write, then send webhook — you have a window where the DB write succeeds but the webhook send fails. The system is now inconsistent and the consumer never gets a notification.
#### How the outbox solves it
Instead of sending the webhook directly, you write an "outbox" record to the DB **in the same transaction** as the business data:

```sql
BEGIN
  UPDATE orders SET status = 'paid' WHERE id = ?
  INSERT INTO outbox (event_type, payload, sent = false) VALUES (...)
COMMIT
```

A separate background job reads unsent outbox records and delivers them. If delivery fails, it retries. Since the outbox record and the business data are in the same transaction, you cannot have one without the other.

**The tradeoff:** Outbox gives you at-least-once delivery (the job might deliver twice if it crashes mid-send). Downstream consumers must be idempotent — same principle as your webhook handler.
### Double-Entry Bookkeeping
Every money movement creates **two ledger entries**: a debit from one wallet and a credit to another. The balance never changes for the system as a whole — money moves, not disappears.

From your `top-up.ts`:
```ts
entries: {
    create: [
        { walletId: SYSTEM_WALLET_ID, direction: "DEBIT",  amount }, // system loses
        { walletId: wallet.id,        direction: "CREDIT", amount }, // user gains
    ],
},
```

System wallet debited = user wallet credited. Net change to the system: zero.
#### Why not just store a balance?
- **Auditability** — the ledger is a permanent record of every movement. The balance is just a cached sum.
- **Recalculability** — if a bug corrupts the `balance` field, you can recompute it by summing ledger entries. You cannot reconstruct history from a single number.
- **Tamper evidence** — you can detect inconsistencies. If the sum of all entries doesn't equal zero across the system, something went wrong (or was tampered with).

Your design stores both: the `balance` field on `Wallet` for fast reads (denormalised), and the `LedgerEntry` records as the source of truth. This is the right tradeoff for a production system — query the balance for display, trust the ledger for accounting.
### N+1 Queries
#### What It Is
You make one query to fetch a list, then N more queries to fetch related data for each item.
```ts
// Classic N+1
const users = await db.find('SELECT * FROM users');       // 1 query
for (const user of users) {
    user.wallet = await db.find('SELECT * FROM wallets WHERE userId = ?', user.id); // N queries
}
```
For 200 users, that's 201 queries. For 1000 users (your LunixPos scenario), it was 1000+ queries per request.
#### How to detect it
I have never actually used DB tools for this, I usually just read the code and check for DB calls within a loop.
#### How to fix it
**In SQL (joins):**
```sql
SELECT users.*, wallets.* FROM users
JOIN wallets ON wallets.userId = users.id  -- 1 query
```

**In Prisma (include):**
```ts
await prisma.user.findMany({ include: { wallet: true } });
```

**DataLoader pattern** (batching, common in GraphQL): instead of N individual queries, batch all IDs and fetch in one `WHERE id IN (...)` call. I use this a lot and store the result in a map linking ID -> data.

---
## 4.5 Quick Fire Answers

**Q: How does your sync job know it's not duplicating what the webhook already did?**
> Two layers. First, `FOR UPDATE` on the Transaction row means only one of them can be inside the critical section at a time. Second, the status check — if the webhook already set it to COMPLETED or FAILED, the sync job reads that, logs a warning, and returns without touching anything.
---
## 5. Questions to Ask Them
Ask these throughout, not just at the end. It signals curiosity and engagement.
### About the Engineering Work
- What does the current backend stack look like — are you fully on Node/TypeScript or is there a mix?
- What's the biggest infrastructure or reliability or developer experience challenge the team is actively working on?
- How does the team approach incident response when a flow breaks in production?
### About the Team & Culture
- What does a typical first 90 days look like for a new backend engineer?
- How does code review work — is it async, or do you do pairing sessions?
- How much ownership do engineers have over technical decisions vs the lead?

---
## 6. Day-Of Checklist

> 📅 Interview is virtual — Thursday at 12:00 PM WAT

- [ ] Test your video/audio setup the night before
- [ ] Have your resume and the JD open on a second screen
- [ ] Keep this guide open on your second screen for quick reference
- [ ] Have water nearby
- [ ] 5 minutes before: close Slack, Discord, notifications
- [ ] If you go blank on a question — say "Let me think about that for a second" and pause. Better than rambling.
- [ ] You're allowed to ask them to repeat or clarify a question

> ✅ **REMEMBER** You delivered a strong assessment under real pressure. Walk in with that confidence — they've already seen your work and liked it enough to bring you here.