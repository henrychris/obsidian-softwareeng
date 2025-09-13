### Overview
The system supports two pricing strategies:
- **Generic Pricing** (`useLocationPricing = "no"`): Same prices across all locations
- **Location-Specific Pricing** (`useLocationPricing = "yes"`): Different prices per location
### 1. New Products Creation Flow
```
Import Product (New)
├── useLocationPricing = "yes" (Location-Specific)
│   ├── Target Location:
│   │   ├── quantity: from CSV
│   │   ├── price/cost: from CSV
│   │   └── isActiveForLocation: TRUE
│   └── Other Locations:
│       ├── quantity: 0
│       ├── price/cost: 0
│       └── isActiveForLocation: FALSE
│
├── useLocationPricing = "no" (Generic)
│   ├── Target Location:
│   │   ├── quantity: from CSV
│   │   ├── price/cost: 0
│   │   └── isActiveForLocation: TRUE
│   └── Other Locations:
│       ├── quantity: 0
│       ├── price/cost: 0
│       └── isActiveForLocation: TRUE
│
└── useLocationPricing = "" or undefined
    └── Defaults to Generic Pricing behavior
```

**Key Code Location:** `createInventoryForLocations()` function

```typescript
isActiveForLocation: useLocationSpecificPricing ? isTargetLocation : true
```

### 2. Updating Existing Products Flow
```
Import Product (Existing)
├── useLocationPricing = "yes" (Switch to Location-Specific)
│   ├── Target Location:
│   │   ├── quantity: from CSV
│   │   ├── price/cost: from CSV
│   │   └── isActiveForLocation: TRUE
│   └── Other Locations:
│       ├── quantity: PRESERVED from existing
│       ├── price/cost: PRESERVED from existing
│       └── isActiveForLocation: PRESERVED from existing
│
├── useLocationPricing = "no" (Switch to Generic)
│   ├── ALL Locations:
│   │   ├── quantity: Target location = CSV, Others = existing
│   │   ├── price/cost: from CSV (product-level)
│   │   └── isActiveForLocation: TRUE (forced)
│
└── useLocationPricing = "" or undefined (Preserve Strategy)
    └── ALL Locations:
        ├── quantity: Target location = CSV, Others = existing
        ├── price/cost: PRESERVED from existing
        └── isActiveForLocation: PRESERVED from existing
```

**Key Code Location:** `applyInventoryPricing()` function

### 3. Product Visibility in GET Products Endpoint

The `index()` function in `product.controller.ts` filters products based on:

```typescript
// Must match BOTH conditions for the location
inventory: {
  $elemMatch: {
    locationId: location,
    isActiveForLocation: true,  // ← This is the key filter
  }
}
// OR for variable products
"variations.inventory": {
  $elemMatch: {
    locationId: location,
    isActiveForLocation: true,  // ← This is the key filter
  }
}
```

### 4. Visibility Matrix by Location

| Pricing Strategy | Import Location | Other Locations |
|------------------|----------------|-----------------|
| `useLocationPricing = "yes"` | ✅ Visible (`isActiveForLocation: true`) | ❌ Hidden (`isActiveForLocation: false`) |
| `useLocationPricing = "no"` | ✅ Visible (`isActiveForLocation: true`) | ✅ Visible (`isActiveForLocation: true`) |

### 5. Your Test Case Analysis

**Your Import Results:**
- 27 products with `useLocationPricing = "no"` 
- 21 products with `useLocationPricing = "yes"`
- Import target: Location 1

**Expected Visibility:**
- **Location 1**: 48 products (27 + 21) - All visible
- **Location 2**: 27 products only - Only generic pricing products visible

**You reported seeing 21 products in Location 2**, which suggests either:
1. Count mismatch in your CSV data
2. Some variable products with mixed pricing strategies
3. Some products were updates to existing products with different behavior
### 6. Business Logic Rationale
**For New Products:**
- Location-specific products are "exclusive" to their import location
- Generic products are "available everywhere" but only stocked at import location
**For Existing Products:**
- Changing to generic pricing enables the product everywhere
- Changing to location-specific pricing only updates the target location
- Preserving strategy maintains existing visibility patterns

This design ensures that:
- Products with location-specific pricing remain location-exclusive unless explicitly changed
- Products with generic pricing are available across all locations
- Updates respect the existing business logic while allowing strategy changes
