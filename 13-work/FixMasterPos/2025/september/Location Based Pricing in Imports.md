## Overview
Add support for location-specific pricing in product CSV imports through a new `useLocationPricing` column.
## CSV Changes
- **New Column**: `useLocationPricing` with values `"yes"` or `"no"` or empty
- **Export Enhancement**: Include current location pricing strategy in exports (either 'yes' or 'no')
- **Variation Support**: Each variation row can have independent `useLocationPricing` value
## Behavior Rules
### New Products
- `undefined/empty` → Default to generic pricing
- `"yes"` → Enable location-specific pricing
- `"no"` → Use generic pricing
### Existing Products
- `undefined/empty` → **No change** to current pricing strategy
- `"yes"` → Convert to location-specific pricing
- `"no"` → Convert to generic pricing

## Pricing Logic
### When `useLocationPricing = "yes"`
- Apply pricing only to current import location
- Set `isActiveForLocation = true` for current location
- Use `price` value as `minimumPrice` (no separate CSV field needed)
- **Required fields**: `price` and `cost`
- Root-level product fields set to CSV values for fallback
### When `useLocationPricing = "no"`
- Apply generic pricing across all locations
- Update root-level product pricing with CSV values
- Set `useLocationSpecificPricing = false`
## Key Features
- **Backward Compatible**: Existing CSVs work unchanged
- **Granular Control**: Per-product and per-variation pricing strategy
- **Flexible Updates**: Can switch between pricing strategies during import
