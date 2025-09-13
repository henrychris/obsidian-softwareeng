**Simple or Serialized Product**
*   **New Product**
    *   **When `useLocationPricing` is `yes`**:
        *   Create a new product with `useLocationSpecificPricing` set to `true`.
        *   Set the root `price` and `cost` to `0`.
        *   Create inventory records for **all** store locations.
        *   For the location specified in the import, populate `inventory.price`, `inventory.cost`, and `inventory.quantity` from the CSV.
        *   For all other locations, set `inventory.price`, `inventory.cost`, and `inventory.quantity` to `0`.

    *   **When `useLocationPricing` is `no` or missing**:
        *   Create a new product with `useLocationSpecificPricing` set to `false`.
        *   Set the root `price` and `cost` from the CSV.
        *   Create inventory records for **all** store locations.
        *   For the location specified in the CSV, set `inventory.quantity` from the CSV.
        *   Set `inventory.price` and `inventory.cost` to `0` for all inventory records (as the root price is the source of truth).

*   **Updating Product**
    *   **When `useLocationPricing` is `yes`**:
        *   **If product already uses location pricing**: Update the `inventory.price`, `inventory.cost`, and `inventory.quantity` for the target location only. Leave other inventory records untouched.
        
	    *   **If product uses generic pricing (convert to location-based)**:
            1.  Set `product.useLocationSpecificPricing` to `true`.
            2.  For all inventory records **except the target location**, set their `inventory.price` and `inventory.cost` from the product's existing root `price` and `cost`.
            3.  For the target location, update `inventory.price`, `inventory.cost`, and `inventory.quantity` from the CSV.
            4.  Set the root `price` and `cost` to `0`.

    *   **When `useLocationPricing` is `no`**:
        *   **If product already uses generic pricing**: Update the root `price` and `cost` from the CSV. Update the `inventory.quantity` for the target location.
        
        *   **If product uses location pricing (convert to generic pricing)**:
            1.  Set `product.useLocationSpecificPricing` to `false`.
            2.  Update the root `price` and `cost` from the CSV.
            3.  Update the `inventory.quantity` for the target location.
            4.  Set the `inventory.price` and `inventory.cost` to `0` for **all** inventory records.

    *   **When `useLocationPricing` is missing**:
	    * Preserve the existing pricing strategy.
        *   Do not change the `useLocationSpecificPricing` flag.
        * Check if the product uses location-based or generic pricing
	        * Generic:
		        * Update the root price & cost.
		        * Update the inventory.quantity at the target location.
		    * Location-based
			    * Update the price, cost and quantity at the target location. Other locations remain untouched.

**Variable Products**
A variable product contains an array of variations, which use the product schema. Each variation can have a pricing strategy independent of other variations. e.g.
- product X has two variations
	- variation a is location-based
	- variation b is generic

Imports should be able to update the pricing strategy of each variation using the same conditions above. Each variation can be considered a 'simple product' when applying the conditions.

If a user attempts to import and update variation a to generic pricing, that change should *not* affect variation b, and vice versa.

# English
## Simple & Serialised products
*   **Updating Product**
    *   **When `useLocationPricing` is `yes`**:
        *   **If product already uses location pricing**: 
	        * The price, cost and quantity are updated for the target location alone. Other locations are untouched.
	    *   **If product uses generic pricing (convert to location-based)**:
		    * The product is converted to use location-based pricing.
		    * Other locations inherit the generic price & cost. Their quantity is unchanged.
		    * The target location's price, cost and quantity is updated.
    *   **When `useLocationPricing` is `no`**:
        *   **If product already uses generic pricing**: 
	        * The generic price is updated for all locations. 
	        * The quantity is updated for the **target** location.
        *   **If product uses location pricing (convert to generic pricing)**:
            1. The product is converted to use generic pricing.
            2. The price and cost is updated for all locations.
            3. The quantity is updated for the **target** location.
    *   **When `useLocationPricing` is missing**:
	    * The existing pricing strategy is preserved.
	        * if the product uses generic pricing:
		        * The price and cost is updated for all locations.
		        * The quantity is updated for the **target** location.
		    * Location-based
			    * The price, cost and quantity are updated at the **target** location. O
			    * ther locations remain untouched.