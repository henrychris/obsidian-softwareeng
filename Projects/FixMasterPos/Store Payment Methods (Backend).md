# Goal
Replace the current hardcoded `option: string` field in the Payment model with a reference to a new, store-configurable `StorePaymentMethod` model. This will allow stores to manage their own list of active payment methods, including custom ones.
## Proposed Solution
- Introduce a new `StorePaymentMethod` Mongoose model.
- Add a storePaymentMethodId reference field to the `Payment` model.
- Create new API endpoints to create, update and get `StorePaymentMethod` records.
- Update the store creation process to add default payment methods.
- Modify the payment creation endpoint (POST /payments) to use `storePaymentMethodId`.
- Implement a migration strategy for existing stores and payments.
- Update financial analytics queries.
## Data Models
1. **New Model - `StorePaymentMethod`**
	- **id**: ObjectId
	- **name**: String (e.g., "Cash", "Visa/MC", "Manual Bank Transfer") - Required
	- **type**: String, Enum: \[system, custom\] - Required (System methods are defaults, Custom are user-added)
	- **status**: String, Enum: \[active, disabled\] - Required (Controls visibility in checkout)
	- **section**: String, Enum: \[normal, apps, custom\] - Required (For frontend grouping/rendering)
	- **storeId**: ObjectId, Ref: Store - Required, Indexed
	- **createdAt**: Date
	- **updatedAt**: Date
	- (Removed) **statusToApplyToOrder**: We will **NOT** use this. The order's payment status (paid, partially-paid, pending-payment) will continue to be determined dynamically based on the dueAmount vs paidAmount after a payment is processed.
2. **Update Model - `Payment**`
	- **Add**: `storePaymentMethodId`: { type: Types.ObjectId, ref: 'StorePaymentMethod', required: false, index: true }` (Nullable initially for migration)
	- **Keep**: `option: String` (Temporarily for migration, to be removed later)
## Endpoints
1. **POST /store** -> create store
	- **Update**: After creating a `Store` and `Location`, automatically create the default set of `StorePaymentMethod` records for that `storeId`.
	- **Defaults**: Define the list of default system payment methods clearly (e.g., Cash, Card, E-Transfer, Manual Debit Card, Split Payment, Deposit, Payment Link, Zelle, Affirm, CashApp, PayPal, Others). Mark them as `type: 'system'`, `status: 'active'`, and assign the appropriate `section`.
	- **DONE**
2. **POST /store/payment-methods** -> **new** endpoint to create a store payment method
	- **Input:** name. Type and Section will be `custom`.
	- **DONE**
3. **GET /store/payment-methods** -> **new** endpoint to fetch payment methods for the current store.
	- **Input:** status (optional)
	- **DONE**
4. **PATCH /store/payment-methods/{id}**  -> **new** endpoint to update a custom payment method
	- **Input:** name (optional), status (optional)
	- **Note**: For default payment methods, only the status can be updated. For custom payment methods, the name and status can be updated.
	- **DONE**
5. **POST /payments**
	- **Update:** 
		- Replace `option` in input with `storePaymentMethodId`
		- validate that selected `storePaymentMethod` is active and exists in the store
		- use `storePaymentMethod`.name when adding timeline record
	- **Note:** The current refund logic identifies refunds by checking if option includes 'refund'. This will break.
		- **Proposal:** Introduce an `isRefund: boolean` field to the `Payment` model. When processing a refund payment, set this flag to true and associate it with the relevant `storePaymentMethodId` used for the refund (e.g., 'Cash Refund' method). The analytics query will need to be updated to account for this flag when calculating totals for payment methods.
	- **DONE**
6. **POST /store/orders/{id}** 
	- This endpoint cancels an order. In doing so, it creates a Payment record refunding the order.
	- **Update:**
		- Accept `storePaymentMethodId` not `option` in the request body. 
		- Check that the payment method id exists and is active. 
		- Assign the store payment method to the payment.
		- Update the timeline record to use `storePaymentMethod.name`.
	- **Note:**
		- Perhaps create a new endpoint called `store/orders/{id}/cancel` to make the functionality less confusing. 
	- **DONE**
7. **POST /webhooks/stripe**
	- When webhook updates are received, the order payment status is updated using the 'payment method'. The specified payment method is a string, so we need to change it to the Default Store Payment Method name, and then assign the relevant id within the store.
	- **DONE**
## Migrations
1. **Update Stores**
	- Run script to iterate through all stores and create the full set of default `StorePaymentMethod` models.
	- This code is **READY** on `feat/sync-payment-methods`
2. **Update Payments**
	- Run script to iterate through all payments where `storePaymentMethodId` is null. For each payment, find a default payment method where `storePaymentMethod`.name equals `option`. If a match is found, save the `storePaymentMethodId`. 
	- Log `Payment` documents where a valid `storePaymentMethod` wasn't found.
	- This code is **READY** on `feat/update-option-to-store-payment-methods`.
3. **Update Order Adjustments** 
	- Do the same for `Adjustment` objects on Orders.
	- They also store `option`, which should be replaced with `storePaymentMethodId`.
	- This code is **READY** on `feat/migrate-adjustments`.
4. **Update related interfaces & entities**: 
	- ProductDocument and OrderDocuments
5. **Update analytics** 
	- The current finance analytics endpoint groups payments by `option`. To deprecate options, we'll need to update the aggregation query here to group by `storePaymentMethodId` instead.
	- **Note:** The current aggregation checks if the option field = `cash refund` to calculate refunds. Instead, we should use the proposed `isRefund` flag to calculate cash refunds.
	- **DONE**
6. Search across the codebase for 'refund' and update logic if necessary.
7. Other endpoints/functions to update:
	1. reports/finance-payment-type - **DONE*feat*
	2. generate order receipt
		- there is a `generateReceipt` util which is  a default export. it is called by two endpoints: generateReceipt and send generate receipt - both in the order controller.
		- need to check how it gets the payment methods
		- **DONE**
	3. function `cashRegisterPaymentBreakdown` in cashRegister.controller.ts
		- `cashRegisterPaymentBreakdown` is used in multiple places, and it calls `paymentBreakDownFunc`. Need to fetch the stores payment methods, and compare against that.
	4. get all orders uses `adjustment.option` **DONE**
8. **Cleanup**
	- Verify that all default payment methods share the same name and handle 
	- create payment methods for all stores
	- migrate all payments from option to storePaymentMethodId
	- When deployed to live and all is well, we can remove the `option` field from the `Payment` model and make `storePaymentMethodId` required.
	- remove old `cancel order`, `create payment` endpoint. 
	- for the **ORDERS** table, we need to make the following updates
		- where `{ isDefaultTaxActive: { $exists: false } }`, we must set `isDefaultTaxActive` to `true`.
		- where `{ nonTaxableAmount: { $exists: false } }`, we must set `nonTaxableAmount` to `0`.