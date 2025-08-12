### Describe your most challenging backend project (What, Why, How, Results)
I recently built ticketing infrastructure for casual football matches.

Football venues - businesses that rent out football pitches for people to play on - have two main business models: bookings and dropins. For the former, a group or individual books the pitch on a certain date for a certain length of time. For the latter, random people show up at a certain time, pay an amount of money to join the session and create random teams for the duration of that session.

The main problem I solved was reconciliation and verification. The venues were having trouble matching payments they received with the paper tickets they issued at the gate - it was disorganized, hard to reconcile, and easily abused.

The technical challenge was handling real-time payments while maximizing trust. People weren't paying ahead of time, so payments needed to be processed instantly, and I needed to get money to venue managers as quickly as possible to build confidence in the system.

I built this infrastructure using Monnify's Payment APIs. Here's how it works:

- Venue creates a drop in booking for a time period. A unique text code and QR are generated for this booking.
- Customers scan the QR code, taking them to the booking page. They make the payment here. This involves initiating a payment to get a checkout url, and then visiting that URL to pay through Monnify.
- The backend receives a webhook with the payment details & completes the transaction. A ticket is generated & cryptographically signed to verify it was created by my application. The ticket is emailed to the customer.
- Monnify sends the amount received directly to the venue manager's bank account through subaccounts we create during onboarding - we hold no money.

Key technical challenges I solved included implementing idempotent payment processing to handle duplicate webhooks, creating a cryptographic signing system for ticket verification, and building retry mechanisms for failed payment notifications.
### If you had all the money you ever needed and do not have to work for money, what will you be doing? Why will you be doing it?
I would probably spend my time making video games. In secondary school, they were what got me interested in programming. I used to make text-based games using BASIC to impress my friends.

I enjoy programming & I enjoy video games. It seems like a good use of time :)
### What was the last new thing you learned? Why did you learn it? How did you learn it? Where have you applied it? Share results where possible.
I recently learnt to build frontend applications using Svelte. I am primarily a backend engineer, and one drawback to that is I find it hard to take projects from zero to one all on my own.

I initially planned to learn React, but found the syntax cumbersome and annoying. A mutual on Twitter (now known as X, unfortunately) mentioned Svelte to me and it was like a breath of fresh air.

I have worked with Svelte since January now, and have built a couple of projects with it. Some simpler than others, most of them private.

The one I can share is QSet, you can see it here https://qset.qballxi.com.

I play football a lot. One major problem when playing is figuring out which team you're on and the playing order - this often led to 10-30 minute arguments that wasted precious playing time. My knowledge of Svelte allowed me to take this application from zero to one - solving the problem I had.

QSet is used regularly at the pitch I play at, as well as 5 others in Lagos.
### What excites you about joining Polaroid?
