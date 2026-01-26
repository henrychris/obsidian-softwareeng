# Overview
There are three types of products: simple, serialised and variable.
# Questions
1. is tax also location based? i don't see any mention of it on the design,
	- tax is set in store settings
	- tax applies to all orders by default
	- tax can be adjusted on orders
	- we don't need location based tax
2. does this pricing apply to all types of products, like repair and custom products?
	1. no. This only applies to normal products created in the system. Custom and repair products are excluded.
3. when a new location is added, what should the default pricing be?
# Implementation
## Variants
- They can set quantity, price, cost, margin and sku at multiple locations (if using location-based pricing)
- If using generic pricing, they can set the quantity at different locations, but not different price schemes.
- On the frontend, they can disable a variable product at a location, which means users can not set a price, quantity and inventory at the location.
!!![[pricing-by-location-1.png]]
!!![[pricing-by-location-2.png]]
### Simple and Serialized
- Products can be disabled at a location, which means users can not set a price, quantity and inventory at the location.
## Plan v1
1. Update the product model  - **DONE**
	- Add `useLocationSpecificPricingBoolean` that defaults to `false`
	- Update inventory model
		- `price`: Number, Location-specific price
		- `cost`: Number, Location-specific cost
		- `minimumPrice`: Number, Location-specific minimum price
		- `isActiveForLocation`: Boolean, For the "Edit Locations" modal (visibility/availability)
	- The existing root-level price, cost, minimumPrice on the product and variations will serve as the *generic* price used when `useLocationSpecificPricingBoolean` is `false`.
2. Add create product endpoint  - **DONE**
3. Add update product endpoint  - **DONE**
4. Update add-products to cart
	1. This endpoint receives products as input with price and quantity
	2. It calculates the subtotal and total and returns the products as a response.
	3. The cart model stores only product quantity and price. We don't need to update it to store location pricing data, we only need to fetch the correct price for a location.
	4. Currently, the add-product to cart model expects incorrect data from the frontend. I will need to update the schema and typing. we only need the `product id`, but the frontend sends this:
		```json
{
    "products": [
        {
            "id": "682d9e8bbb8b0fd6c1873bab",
            "title": "Airpod pro",
            "type": "simple",
            "isService": false,
            "isTaxable": true,
            "actionType": "sell",
            "slug": "airpod-pro",
            "quantity": 1,
            "sku": "DRMW5J"
        }
    ]
}
```
		5. I updated addProductToCart. This function handles getting the correct price for the products and storing in the cart, then `cartModifier` tallies up the totals.
		6. I refactored `cartModifier` so that it is easier to read. At this point, I need to test what I have done so far before I continue. Need to wait for the frontend to catch up.
5. Update 'update-product-quantity'.
	1. This updates the quantity of a product, and of course, updates the total and subtotal.
6. Update the price range virtual to account for variants & location-based pricing - **DONE**.
### Notes
- Location is stored on the order
- I might need to update the `priceRange` virtual on the product model  - **DONE**
## Migration
1. Remove old endpoints and replace with new implementations
	- Create Product
	- Update Product
2.  Run script to add pricing data to all inventory objects at all stores & set `useLocationSpecificPricing` to false.
	- This exists on the `misc/migrate-products-location-based` branch
3. Run script to update locations status on all products.
	 - This exists on `chore/migrate-product-locations`.
	 - So by this point, every product will have the expected fields and the inactive locations will be inactive on the products.