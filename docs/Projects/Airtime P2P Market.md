- Vertical Slice Architecture in a Monolith (Watch Videos)
- Create a temporary escrow account for each transaction.
- multiple endpoints for order processing.
	- CreateOrder
	- PlaceOrderInEscrow
	- CompleteOrder
	- CancelOrder
- Database:
	- User
	- Transactions - record payments, withdrawals, etc
	- Accounts (Wallets)
	- Orders
	- KYC?
	- Transaction Limits

# Flowcharts/Screens - for user flow
- Signup
- Create Offer
- Purchase Airtime / Accept Offer
- Fund Wallet

Related:
- [Build a Peer-to-Peer Marketplace Website: In-Depth Guide - Northell](https://northell.design/blog/how-to-build-a-peer-to-peer-marketplace-website)
- [4 Steps to Build a Peer-to-Peer Marketplace Guide with Examples](https://gearheart.io/articles/building-peer-peer-marketplace-scratch/)
- [How to Build a Peer to Peer Marketplace: A Complete Guide (fatbit.com)](https://www.fatbit.com/fab/how-to-build-a-peer-to-peer-marketplace/)

# Modules
## Auth

### Signup
1. User creates account with email and password. Other platform integrations can be used here, like Google.
2. The user is required to provide a NIGERIAN phone number.
3. An OTP is sent to the user's phone to verify ownership.

### Login
1. User can either provide email and password, or phone number and password. A button should be clicked to switch between options. A user may use a platform integration, like Google, to sign in.
2. If the user provides the wrong password **three** times, show a *CAPTCHA*.
3. If the user provides the wrong password **five** times, lock them out. Have them use the forgot password screen to verify their identity.
4. If the user forgets their password, an email is sent to the registered email address.
## Messaging
1. Buyer and Seller should be able to send messages to one another in a **transaction-scoped** chat room. 
2. When a transaction concludes, the chat should be inaccessible to the user. A copy of the messages should be emailed to each party in a **signed** PDF.

## User Ratings and Reviews
1. After a transaction, users can review one another using a star system.
2. There will also be checkboxes with review options as well as a text box for a longer review. 
		The checkboxed reviews should have an associated score used as weights when updating the users review. Good reviews have a higher weight, and vice versa.
3. After review, the new scores are added to the user's average. 
		Use a formula that doesn't require knowledge of past review scores.
## Orders
1. A user can create a maximum of **ten** offers per time.
2. An offer includes: network, airtime amount, expiry date. The DB also maintains the date it was created.
3. Orders may have one of four states: **Available**, **Expired**, **InEscrow**, **Completed**.
4. Order references should be in this format: `O-NETWORK_SHORT_CODE-Number`
## Transactions
1. When a buyer chooses to engage in an offer, it goes into **escrow**. 
2. A **random** wallet is generated and funds go from the buyers wallet into the escrow account.
3. Once **BOTH** buyer and seller approve that airtime has been moved, the funds move from escrow to the seller's wallet.
4. Transaction in DB: OrderID, Amount, IsCompleted, ChatID (not sure about this).
5. Transaction references should be in this format: `T-NETWORK_SHORT_CODE-Number`
## Wallet
### Normal Wallet
1. To purchase airtime on the platform, users must have funds in their wallet. This is for security reasons.

### Escrow Wallet
1. A random wallet is created on a per-transaction basis. It exists for a single order, and is deleted afterwards.
2. In DB: TransactionID, BuyerID, SellerID, Amount, BuyerConfirmed, SellerConfirmed.
## Message Broker
