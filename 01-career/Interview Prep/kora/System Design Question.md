## **States**

Each account number goes through a set of states:

Available \-\> Assigned \-\> Dormant \-\> Available ...

Assigned at T \= 0 Payment made at  T \= 30m Dormant from T \= 30m to T \= 14 days \+ 30m Available from T \= 14 days

If payments are not made within 1 hour of generation, the account should go dormant.

## **Schema**

### AccountNumber

- id  
- account\_number (unique, 10 digit nuban)  
- status (enum: available, assigned, dormant)  
- dormant\_until (nullable timestamp)  
- created\_at

### Assignment

- id  
- account\_number\_id (FK \-\> AccountNumber)  
- customer\_id (FK \-\> Customer)  
- assigned\_at  
- expires\_at // assigned at \+ 1 hour  
- payment\_received\_at (nullable timestamp)  
- status (enum: active, paid, expired)

Assignment is separate from account number for history purposes. We ought to know the many assignments over the lifetime of an account number.

### Customer

- id  
- first\_name  
- last\_name  
- email

### Transaction

- id  
- assigmnent\_id (FK \-\> Assignment)  
- amount (decimal)  
- provider\_reference  
- completed\_at

### Webhook Event

- id  
- reference (unique  \- for idempotency check)  
- payload (jsonb string)  
- provider

  ## **Where Do Account Numbers Come From?**

In my experience, the provider (a bank) assigns a 3-digit prefix for the organisation and we generate the remaining characters. The full 10-digit number is a valid NUBAN and lives entirely in the organisation's database. I will continue with this assumption.

When a user at another bank wants to pay into one of these accounts:

- Their bank sends a transfer request to NIBSS  
- NIBSS routes a lookup to the destination bank  
- The destination bank calls the organisation's account lookup API to resolve the account details  
- If the account is valid and assigned, the org returns the customer details  
- The transfer completes and the org receives a payment webhook

The org's lookup API must therefore:

- Accept an account number  
- Return customer details if the account is ASSIGNED and the assignment is ACTIVE  
- Return an error/not-found if the account is AVAILABLE, DORMANT, or the assignment has EXPIRED

Account numbers are generated at provisioning time, not at assignment time. A one-time setup process (admin script or internal endpoint) generates the pool upfront.  
We only generate new account numbers if this pool needs to grow.

## **Scale 1: 10 Users**

Single Node \+ Express Service with a single Postgres instance \+ two cron jobs

### Flow

1. Customer requests an account number  
2. Find any `available` account number, lock it with `SELECT FOR UPDATE SKIP LOCKED`, set it to `assigned` and create an `Assignment` record.  
3. When the payment webhook arrives, set `Assignment.status` to `paid` & `AccountNumber.status` to dormant. Set `AccountNumber.dormantUntil` to the current datetime \+ 14 days.  
4. First cron runs every hour, finds account numbers where `status` \= `dormant` and `dormant_until < now` and sets `AccountNumber.status` to `available`.  
5. Second cron finds `Assignments` where `status` is `active`  and `expires_at` \< now, and sets `Assignment.status` to expired, and `AccountNumber.status` to `dormant`.

If two requests come in simultaneously for the same account, the second skips locked rows to get the next available one.

## **Scale 2: 1000 Users**

At this point our architecture still suffices, but with some changes.

We add partial indexes on:

- `AccountNumber.status` \= available  
- `AccountNumber.status & AccountNumber.dormantUntil` where `AccountNumber.status = dormant`  
- `Assignment.status & Assignment.expiresAt` where `Assignment.status = active`

Instead of a cron job, we schedule precise jobs using `dormantUntil` and `expiresAt`. The job scheduler already polls the database, so we can leave it to that and take out the cron jobs which scan the tables.

We can add a connection pool as well to recycle connections, else we hit connection limits. We can also cache the number of available accounts so we can quickly return 'no accounts available' without hitting Postgres on every request.

## **Edge Cases**

### Late Payment

A customer requests an account at 12:00 PM. The assignment expires at 1:00 PM. Your second cron job runs and marks the account as dormant/expired. However, bank networks can be slow. At 1:05 PM, a webhook arrives saying the customer actually made the transfer at 12:59 PM.

\[Raise this as a question back to them if they bring it up.\]

The system maintains the history of assignments, so it depends on a product decision. We can:

- check if there was an active assignment at the time and complete the payment \- marking the assignment as paid if the amount matches up.  
- or simply reverse the transaction if the assignment had already been marked as expired.

### Idempotency

I have a webhook events table that maintains a unique index on the reference field. When a webhook comes in we check if the reference had already been saved. If so, we quietly ignore the duplicate.