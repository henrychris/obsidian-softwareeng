## Flow
1. Choose products or add custom products.
2. Click checkout
3. Choose shipping options from a list defined in store settings.
	1. Each option has a price and title.
4. Choose payment options from a predefined list
	1. Cash
		- For cash, we can specify paid or pending.
	2. Split Payment
	3. Deposit
5. Create order with status as Unfulfilled.
# Implementation
- for each product
	- check if variant is provided
		- validate variant exists
		- set order item name, title and location. override details set by frontend for accuracy
		- get inventory location
			- check if it is in stock at default location.
			- if out of stock at default location, check other locations. if no other locations have stock, set default location as the order item location.
	- all order item objects should exist in an array at this point. we haven't created anything yet.
	- start a transaction
		- deduct inventory from locations
		- calculate subtotal and total
		- create order items
		- create order
		- return order id and details

### Alternative Location Check Code
```ts
// Find available inventory at default location
      let locationWithStock = variant.inventory.find(
        (inv) => inv.storeLocation.isDefault && inv.available >= item.quantity,
      );
      if (!locationWithStock) {
        locationWithStock = variant.inventory.find(
          (inv) => inv.available >= item.quantity,
        );
      }

      if (!locationWithStock) {
        // Check if default location exists in inventory
        const defaultLocationInventory = variant.inventory.find(
          (inv) => inv.storeLocation.isDefault,
        );

        if (!defaultLocationInventory) {
          log.error(
            `No inventory found for variant ${variant.name} at any location.`,
          );
          return Result.error(
            `No inventory found for variant ${variant.name} at any location.`,
          );
        }

        // Deduct from default location even if it becomes negative
        locationWithStock = defaultLocationInventory;
      }
```
## Notes
1. Use **Shopify's** Create Order layout and interface, but remove payment section in favour of Shipping and Payment pages. 
	- *Question* - Do we keep this section on the create order page, or move it to the Payment page
	  ![[Pasted image 20250129151228.png]]
2. Use **Shopify's** fulfilment layout and UI.
3. Use **FixMaster PoS'** View Order layout and UI.
4. Users needs to be able to print receipts and send receipt emails to users.
5. On the View All Orders page, users should be able to mark multiple items as fulfilled.
6. On the View All Orders page, users should be able to print receipts for multiple orders at once.
	- All receipts will be in one document, on different pages.
7. When cancelling an order, a refund must be given. Users must choose a payment method and optionally specify a reason.
8. If new products are added to a paid order, status should change to partially paid.

## Proposed Draft Order Flow
- While creating an order, optionally save as draft to continue later.
- Draft orders only contain order items, notes, customer info and tags. There are no shipping or payment terms.
- There will only be three options / buttons on the page: `Discard`, `Save` and `Create Order`.
- The `Create Order` button will show the modal to select shipping options, then the modal to select payment terms. Finally, the admin will choose `Create Order` to send the `POST` request and create the order in the system.
	- The front-end will add the items, notes, customer info and tags to the request.
- Optionally, the create order endpoint will accept `draftOrderId`. If provided, add a timeline entry specifying that the order was created from a draft.
![[draft-flow.png]]

# Flow II
- Create Order
![[Pasted image 20250131102229.png]]
On this page there are 3 options: 'Save Draft', 'Discard' or 'Create Order'.
- SaveDraft - call create draft order endpoint
- Discard - discard changes and return to previous screen
- Create Order - navigate to select shipping & payment pages, then finally create an order.

Replace `Mark As Paid` with `Create Order`.
Remove `Send Invoice`.
## Create Order Request
```json
{
    "order": {
        "items": [
            {
                "name": "Item WIth Variants - Amateur / 24",
                "price": 45.99,
                "quantity": 1,
                "isTaxable": true,
                "isPhysical": true,
                "weight": 0,
                "weightUnit": "kg",
                "productVariantId": "c4ff27de-7097-47b0-a151-93cb6982e107"
            }
        ],
        "notes": "First order test.", // optional
        "customerId": "", // optional
        "tagIds": [""], // optional
        "draftOrderId": "" // optional
    },
    "shipping": {},
    "payment": {}
}
```

## Timeline
- add timeline events for adding, removing and changing phone number.
