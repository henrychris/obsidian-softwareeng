We will need to implement discounts in two sections:
1. The create order form
2. The discount sections.
# Create Order Form
![[create-order-overview.png]]
Here, we can add discounts in two places:
3. On items, by clicking the price in blue text.
4. On the order as a whole, by clicking the `add discount` hyperlink.
## Item Discounts
![[add-simple-discount.png]]
![[add-simple-discount-percentage.png]]
Item discounts are simple. 
- The admin selects a discount type, either `Amount` or `Percentage`.
- The admin provides a discount value, greater than 0.
- The admin may optionally provide a reason for the discount, which is displayed to the customer.
## Order Discounts
![[add-discount-to-order.png]]
Order discounts are a bit more complex:
- The admin may provide/choose an existing discount code in the store.
	- These discounts are created in the discount section of the admin portal.
- The admin may choose to apply all eligible automatic discounts
	- Automatics discounts are created in the discount section of the admin portal.
- The admin may add a custom order discount.
	- The admin selects a discount type, either `Amount` or `Percentage`.
	- The admin provides a discount value, greater than 0.
	- The admin may optionally provide a reason for the discount, which is displayed to the customer.

An `Order` may have zero or multiple discounts applied. An `OrderItem` may have zero or one discounts applied.
# Discount Section
![[discount-overview.png]]
![[select-discount-type.png]]
The admin can create four types of discounts on this section:
- [[Amount Off Products (Product Discount)]]
- [[Buy X Get Y (Product Discount)]]
- [[Amount Off Order (Order Discount)]]
- [[Free Shipping (Shipping Discount)]]
# Other Requirements
- Customers can apply discount codes on orders by typing in a code. 
- Automatic discounts should be auto applied to orders on checkout.
- The admin should be able to see how many times a discount was used, and the total amount of sales made with said discount.
- Customers can use a maximum of 5 product or order discount codes and 1 shipping discount code on the same order. This doesn't affect the automatic discounts, where a maximum of 25 can apply to an order at once.
	- Custom or manual discounts aren't included in this maximum.
- Products that are part of a [Buy X get Y](https://help.shopify.com/en/manual/discounts/discount-types/buy-x-get-y) discount are ineligible for further product discounts. If a customer enters a discount code that applies to products in a Buy X get Y discount, then the Buy X get Y discount is removed and only the discount code that the customer entered is applied to the order.
## Discount Codes
- Discount codes may be up to 255 characters long.
- Generated codes are 12 characters long.
- Of course, we should check that a code is unique.
- Don't allow special characters in the discount code.
- A store may have a maximum of 20,000,000 unique discount codes.
- A code may apply to a max of 100 specific customers, products or variants.
## Automatic Discounts
- You may have a maximum of 25 **active** automatic discounts.
- For an automatic discount to apply correctly, your customers need to add all eligible items to their cart before they move to checkout. This includes the items that they need to buy to qualify for the discount, as well as any items that they get as part of a promotion.
## Amount Off Discounts
- If your amount off discount applies to all products, then the discount is applied proportionally across all items in the cart. For example, if you have a $50 discount applied to a cart with a $50 item and a $100 item, then the first item is discounted by $16.50 and the second one by $33.50. If the total price of the order is less than $50, then the value of each item is discounted to $0. The order value can't go below $0.
### How?
1. First, let's understand why the $50 discount splits into $16.50 and $33.50:
   * Total cart value = $50 + $100 = $150
   * For the $50 item:
     * Proportion of total = $50/$150 = 1/3
     * Discount amount = $50 × (1/3) = $16.50
   * For the $100 item:
     * Proportion of total = $100/$150 = 2/3
     * Discount amount = $50 × (2/3) = $33.50
2. We can verify this works:
   * $16.50 + $33.50 = $50 (total discount)
   * The discounts maintain the same proportions as the original prices (1:2 ratio)
3. The general formula would be:
   `Item discount = Total discount × (Item price / Cart total)`
4. For the case where the total order is less than the discount:
   * If cart total < $50, each item becomes $0
   * This makes sense because you can't have negative prices
   * Example: If you have a $30 item and a $10 item with a $50 discount:
     * Both items would be reduced to $0
     * The full $50 discount isn't applied (only $40 is used)
## Buy X Get Y
- With buy X get Y promotions, you can't have the free or discounted 'get' item automatically added to the cart. Your customers **must add all relevant items** to their cart themselves. With buy X get Y discount codes, customers need to add all applicable products to their cart and then they enter the discount code at checkout. With buy X get Y automatic discounts, customers need to add all applicable products to their cart and then the discount is automatically applied.
# Implementation Details
When a user selects the discount type, and method, we format their settings into a JSON shape and save it in the database (as JSON). When we need to apply that discount, we parse the JSON as that type, validate as needed and calculate the amount to deduct from the order total.
For now we don't need to think on parsing, just store the configuration data in the JSON field.