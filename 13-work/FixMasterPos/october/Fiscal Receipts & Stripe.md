# Endpoints & Methods To Check
- `plans/:planId/subscribe` in plans.routes.ts
- `user.createSubscription` in user.model.ts
- `createStoreForUser` in stores.ts

# Existing Subscription Flow
- When a user creates a store we create a subscription for them and place them on trial.
- When the subscription expires, the FE prompts the user to resubscribe, which calls the `plans/:planId/subscribe` endpoint
- Plans are stored in the database with `stripePriceId`. They correlate to products in the Stripe Product Catalogue. 
	- Perhaps Fiscal Receipt Plans will go here.
# Questions
- Where do we add Fiscal Receipt Plans as addons to the existing subscription?
- How do we prorate the Fiscal Receipt Plans?
- How do we handle reupping Fiscal Receipt Allowance - without extending billing period.

# Other
## Conversation With Bot
**ME** 
im new here. first i need to know how plans and subscriptions work on stripe, what the available subscriptions/plans are, and how we know when users resubscribe
**BOT**
Stripe's subscription model allows you to manage recurring payments for your products. Subscriptions involve creating a plan that customers can subscribe to, which can include features like different pricing models, discounts, trials, and automated invoicing. You can manage these subscriptions through the Stripe Dashboard or API.

To know when users resubscribe, you can use webhooks to listen for subscription events. For example, the customer.subscription.created event is triggered when a subscription is created, and the customer.subscription.resumed event is triggered when a paused subscription is resumed. These events help you track subscription activities and manage customer access accordingly.
**ME**
okay. we have an existing recurring plan. this is our main subscription, but now we want to add an 'addon' plan, that can be prorated.
​
When a user pays for such a plan, it grants an allowance of a certain value which is available for the duration of that billing period. The price is prorated depending on how many days are left till the end of that billing period.
​
The addon is added to the existing subscription cost & renews every billing period. The user can also repurchase this addon to increase their allowance, but additional purchases wont be added to the subscription cost, and the billing period wont change.
​
is this possible? how?
**BOT**
Yes, it's possible to create an add-on plan with proration for an existing subscription on Stripe. Here's how you can set it up:

Create the Add-on Plan: Define a new product and price for the add-on. Ensure the price is set to be prorated by enabling proration settings.

Add to Existing Subscription: Use the Stripe API to add this add-on to a customer's existing subscription. You can do this by updating the subscription and including the add-on as an additional subscription item.

Proration: When adding the add-on mid-cycle, Stripe will automatically calculate the prorated amount based on the remaining days in the billing period.

Repurchase Allowance: To allow users to repurchase the add-on without affecting the billing cycle, you can create one-off invoices for additional purchases. This way, the add-on's allowance can be increased without altering the subscription's billing period.

By following these steps, you can effectively manage add-ons with prorated billing in Stripe.

## Plans
```json
[
    {
        "title": "300 Fiscal Receipts Plan",
        "price": 120.0,
        "stripePriceId": "price_1SHkV3L97dPtY3qObCTnL318",
        "allowance": 300,
        "region": "dominican-republic",
        "isActive": true
    },
    {
        "title": "250 Fiscal Receipts Plan",
        "price": 100.0,
        "stripePriceId": "price_1SHkUmL97dPtY3qOZ8rFQrki",
        "allowance": 250,
        "region": "dominican-republic",
        "isActive": true
    },
    {
        "title": "200 Fiscal Receipts Plan",
        "price": 70.0,
        "stripePriceId": "price_1SHkUVL97dPtY3qOQeZt22wx",
        "allowance": 200,
        "region": "dominican-republic",
        "isActive": true
    },
    {
        "title": "150 Fiscal Receipts Plan",
        "price": 50.0,
        "stripePriceId": "price_1SHkU3L97dPtY3qOXDIDRwGQ",
        "allowance": 150,
        "region": "dominican-republic",
        "isActive": true
    },
    {
        "title": "100 Fiscal Receipts Plan",
        "price": 30.0,
        "stripePriceId": "price_1SHkSFL97dPtY3qOgD4nr9WD",
        "allowance": 100,
        "region": "dominican-republic",
        "isActive": true
    }
]
```

## Go Live
- create Fiscal Receipt Addon on live mode & save to live database.
- fiscal-receipts
	- feat/fiscal-receipts-cron
		- feat/fiscal-receipts-populate-order