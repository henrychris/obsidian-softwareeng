# The Question
Should we treat **Standard Bookings** (group reserves pitch) and **DropIn Bookings** (individuals pay to join) as:
- **Option A**: One shared `Booking` model with a `Type` field
- **Option B**: Two separate models `StandardBooking` and `DropInBooking`
## Current Approach (Option A) ✅

```csharp
// Single model handles both types
public class Booking {
    public BookingType Type { get; set; } // Standard or DropIn
    public decimal? ExpectedAmountPerPlayer { get; set; } // Only for DropIn
    // ... other shared fields
}
```

**Business Benefits:**
- **Calendar works seamlessly** - all reservations show up in one view
- **Availability checking is simple** - one query finds all conflicts
- **Dashboard/analytics easier** - single source for all venue activity
- **Venue managers see everything in one place**
## Alternative Approach (Option B) ❌

```csharp
// Two separate models
public class StandardBooking { /* standard fields */ }
public class DropInBooking { /* dropin fields + pricing */ }
```

**Would require:**
- Complex calendar queries (merge two data sources)
- Availability checking becomes much more complicated
- Dashboard needs to combine data from multiple places
- API responses become more complex
## Real-World Impact
**With Current Approach:**
- Venue manager opens calendar → sees all bookings instantly
- Customer checks availability → one fast query
- Adding new booking types later → just add to existing enum
**With Separate Models:**
- Calendar loading → multiple database calls, slower
- Availability checking → query both tables, merge results, complex logic
- New booking type → significant code changes across the system
## Recommendation: Keep Current Approach
The shared model works because **both types are fundamentally the same business concept**: *reserving a time slot at a venue*. The only real difference is the pricing model.

We can get the best of both worlds by:
1. Keep the shared data model (what we have)
2. Use different response types for the API (cleaner frontend code)
3. Add type-specific validation (already implemented in your `CreateBookingRequest`)

This gives us type safety where it matters (API responses) while keeping the complex operations (calendar, availability) simple and fast.

**Bottom line:** The current approach is more maintainable, performs better, and provides a better user experience for venue managers.
