type=FreeShipping
method = discountCode
```json
"minimumPurchaseRequirements": {
	"minmumAmount": null,
	"minimumQuantity": 3
},
"eligibility": {
	"choice": "ALL_CUSTOMERS",
	"selectedCustomers": null
},
"maximumDiscountUses": {
	"maxNumberOfUses": 3,
	"oneUsePerCustomer": true
},
"combinations": {
	"productDiscounts" : true,
	"orderDiscounts": false 
}, 
"activeDates": {
	"startDateAndTime": "22/02/2025",
	"endDateAndTime": null
}
```
# Interfaces and Usage
```ts
// Specific configurations for each discount type
interface FreShippingConfig {
}

interface AmountOffOrderConfig {
  discountValue: {
    type: 'FIXED_AMOUNT' | 'PERCENTAGE';
    value: number;
  };
}

interface AmountOffProductsConfig {
  discountValue: {
    type: 'FIXED_AMOUNT' | 'PERCENTAGE';
    value: number;
  };
  appliesTo: {
    type: 'SPECIFIC_PRODUCTS' | 'SPECIFIC_COLLECTIONS';
    products?: string[]; // product IDs
    collections?: string[]; // collection IDs
  };
}

interface BuyXGetYConfig {
  customerBuys: {
    type: 'QUANTITY' | 'AMOUNT';
    value: number;
    items: {
      type: 'SPECIFIC_PRODUCTS' | 'SPECIFIC_COLLECTIONS';
      products?: string[]; // product IDs
      collections?: string[]; // collection IDs
    };
  };
  customerGets: {
    quantity: number;
    items: {
      type: 'SPECIFIC_PRODUCTS' | 'SPECIFIC_COLLECTIONS';
      products?: string[]; // product IDs
      collections?: string[]; // collection IDs
    };
    discountValue: {
      type: 'PERCENTAGE' | 'FIXED_AMOUNT' | 'FREE';
      value: number;
    };
    maxUsesPerOrder?: number;
  };
}

// Union type for all possible configurations
type DiscountConfig =
  | { type: 'FREE_SHIPPING'; config: FreeShippingConfig }
  | { type: 'AMOUNT_OFF_ORDER'; config: AmountOffOrderConfig }
  | { type: 'AMOUNT_OFF_PRODUCTS'; config: AmountOffProductsConfig }
  | { type: 'BUY_X_GET_Y'; config: BuyXGetYConfig };

// Helper functions to validate and apply discounts
function parseDiscountConfig(
  type: DiscountType,
  configJson: any
): DiscountConfig {
  // Validate and parse the JSON based on the discount type
  switch (type) {
    case 'FREE_SHIPPING':
      return {
        type: 'FREE_SHIPPING',
        config: configJson as FreeShippingConfig
      };
    case 'AMOUNT_OFF_ORDER':
      return {
        type: 'AMOUNT_OFF_ORDER',
        config: configJson as AmountOffOrderConfig
      };
    // ... handle other types
  }
}

// Example usage for calculating discount
async function calculateDiscount(
  discountId: string,
  order: Order
): Promise<number> {
  const discount = await prisma.discount.findUnique({
    where: { id: discountId }
  });

  if (!discount) throw new Error('Discount not found');

  const config = parseDiscountConfig(discount.type, discount.configuration);

  // Check eligibility
  if (!isEligible(config.config, order)) {
    return 0;
  }

  // Calculate discount amount based on type
  switch (config.type) {
    case 'FREE_SHIPPING':
      return calculateShippingDiscount(config.config, order);
    case 'AMOUNT_OFF_ORDER':
      return calculateOrderDiscount(config.config, order);
    // ... handle other types
  }
}
```
