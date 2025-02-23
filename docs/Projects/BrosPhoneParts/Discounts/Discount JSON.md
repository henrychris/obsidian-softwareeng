## Code Based Amount Off Products
```json
{
    "method": "Code",
    "code": "SAVE2",
    "type": "AmountOffProducts",
    
    "minimumPurchaseAmount": 50, // optional
    // "minimumPurchaseQuantity": 50, // optional

    "eligibilityChoice": "AllCustomers", // or 'SpecificCustomers'
    // "selectedCustomerIds": [""], // optional if eligibilityChoice is not SpecificCustomers
    // "maximumNumberOfUses": 200 // optional
    "oneUsePerCustomer": false,
    "allowProductDiscounts": true,
    "allowOrderDiscounts": false,
    "allowShippingDiscounts": false,
    "startDate": "2024-02-15T00:00:00Z",
    // "endDate": "2025-03-15T00:00:00Z", // optional, must be ahead of startDate
    
    "configuration": {
        "type": "AmountOffProducts",
        "discountDetails": {
            "discountValue": {
                "type": "Percentage", // or FixedAmount 
                "value": 2
            },
            "appliesTo": {
                "type": "SpecificProducts", // or SpecificCollections
                "productVariantIds": [
                    "226e9609-fff8-4995-affb-f7b70b87ecb8"
                ] // or collectionIds
            }
        }
    }
}
```
## Automatic Amount Off Products
```json
{
    "method": "Automatic",
    "title": "20% Off Selected Products",
    "type": "AmountOffProducts",

    "minimumPurchaseAmount": 50, // optional
    // "minimumPurchaseQuantity": 50, // optional

    "allowProductDiscounts": true,
    "allowOrderDiscounts": false,
    "allowShippingDiscounts": false,

    "startDate": "2025-03-01T00:00:00Z",
    // "endDate": "2025-04-01T00:00:00Z", // optional

    "configuration": {
        "type": "AmountOffProducts",
        "discountDetails": {
            "discountValue": {
                "type": "Percentage",
                "value": 20
            },
            "appliesTo": {
                "type": "SpecificProducts",
                "productVariantIds": [
                    "8ba631aa-3129-4b75-83fc-807fb9f5af7e"
                ]
            }
        }
    }
}
```
## Code Based Free Shipping
```json
{
    "method": "Code",
    "code": "FREESHIP",

    "type": "FreeShipping",
    "minimumPurchaseAmount": 100, // optional
    // "minimumPurchaseQuantity": 0, // optional
    
    "eligibilityChoice": "AllCustomers",
    // "selectedCustomerIds": [""], // optional if eligibilityChoice is not SpecificCustomers
    "maximumNumberOfUses": 200, // optional
    "oneUsePerCustomer": false,
    
    "allowProductDiscounts": false,
    "allowOrderDiscounts": false,
    
    "startDate": "2025-02-15T00:00:00Z",
    // "endDate": "2025-03-15T00:00:00Z", // optional
    
    "configuration": {
        "type": "FreeShipping",
        "discountDetails": {}
    }
}
```
## Automatic Free Shipping
```json
{
    "method": "Automatic",
    "title": "Free Shipping on Orders Over $75",
    "type": "FreeShipping",
    
    "minimumPurchaseAmount": 75, // optional
    // "minimumPurchaseQuantity": 75, // optional

    "allowProductDiscounts": true,
    "allowOrderDiscounts": true,
    
    "startDate": "2025-03-01T00:00:00Z",
    // "endDate": "2025-03-02T00:00:00Z", // optional
    
    "configuration": {
        "type": "FreeShipping",
        "configuration": {}
    }
}
```
## Code Based BuyXGetY
```json
{
    "method": "Code",
    "code": "BUY2GET1",
    
    "type": "BuyXGetY",
    
    "eligibilityChoice": "AllCustomers",
    // "selectedCustomerIds": [""], // optional if eligibilityChoice is not SpecificCustomers
    "maximumNumberOfUses": 200, //optional
    "oneUsePerCustomer": true,
    
    "allowProductDiscounts": true,
    "allowOrderDiscounts": false,
    "allowShippingDiscounts": false,
    
    "startDate": "2025-02-15T00:00:00Z",
    "endDate": "2025-03-15T00:00:00Z", // optional

    "configuration": {
        "type": "BuyXGetY",
        "discountDetails": {
            "customerBuys": {
                "type": "MinimumQuantity", // or MinimumAmount
                "value": 2,
                "items": {
                    "type": "SpecificProducts", // or SpecificCollections
                    "productVariantIds": [
                        "8ba631aa-3129-4b75-83fc-807fb9f5af7e"
                    ] // or collectionIds
                }
            },
            "customerGets": {
                "quantity": 1,
                "items": {
                    "type": "SpecificProducts", // or SpecificCollections
                    "productVariantIds": [
                        "8ba631aa-3129-4b75-83fc-807fb9f5af7e"
                    ] // or collectionIds
                },
                "discountValue": {
                    "type": "Free" // or FixedAmount or Percentage. Those require a `value` field
                },
                "maxUsesPerOrder": 1
            }
        }
    }
}
```
## Automatic BuyXGetY
```json
{
    "method": "Automatic",
    "title": "Buy 2 Get 1 50% Off",
    "type": "BuyXGetY",
    
    "allowProductDiscounts": true,
    "allowOrderDiscounts": false,
    "allowShippingDiscounts": false,
    
    "startDate": "2025-03-01T00:00:00Z",
    // "endDate": "2025-03-01T00:00:00Z", // optional
    
    "configuration": {
        "type": "BuyXGetY",
        "discountDetails": {
            "customerBuys": {
                "type": "MinimumQuantity",
                "value": 2,
                "items": {
                    "type": "SpecificCollections",
                    "collectionIds": [
                        "2e9ced3f-beb6-4164-a896-af4d8073bbca"
                    ]
                }
            },
            "customerGets": {
                "quantity": 1,
                "items": {
                    "type": "SpecificCollections",
                    "collectionIds": [
                        "2e9ced3f-beb6-4164-a896-af4d8073bbca"
                    ]
                },
                "discountValue": {
                    "type": "Percentage",
                    "value": 50
                },
                "maxUsesPerOrder": 2
            }
        }
    }
}
```
## Code Based Amount Off Order
```json
{
    "method": "Code",
    "type": "AmountOffOrder",
    "code": "SAVE30",
    
    "eligibilityChoice": "AllCustomers",
    // "selectedCustomerIds": [""], // optional if eligibilityChoice is not SpecificCustomers
    
    "minimumPurchaseAmount": 100, // optional
    // "minimumPurchaseQuantity": 50, // optional
    
    // "maximumNumberOfUses": 200, // optional
    "oneUsePerCustomer": true,
    
    "allowProductDiscounts": false,
    "allowOrderDiscounts": true,
    "allowShippingDiscounts": true,
    
    "startDate": "2025-03-01T00:00:00Z",
    // "endDate": "2025-03-15T00:00:00Z", // optional, must be ahead of startDate
    
    "configuration": {
        "type": "AmountOffOrder",
        "configuration": {
            "discountValue": {
                "type": "FixedAmount", // or Percentage
                "value": 30
            }
        }
    }
}
```
## Automatic Amount Off Order
```json
{
    "method": "Automatic",
    "title": "$30 Off Orders Over $100",
    "type": "AmountOffOrder",

    "minimumPurchaseAmount": 100,
    // "minimumPurchaseQuantity": 100, // optional
    
    "allowProductDiscounts": false,
    "allowOrderDiscounts": true,
    "allowShippingDiscounts": true,
    
    "startDate": "2025-03-01T00:00:00Z",
    // "endDate": "2025-03-01T00:00:00Z", // optional
    
    "configuration": {
        "type": "AmountOffOrder",
        "discountDetails": {
            "discountValue": {
                "type": "FixedAmount",
                "value": 30
            }
        }
    }
}
```