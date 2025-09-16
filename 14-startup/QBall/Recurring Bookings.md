Fabio asked that we implement recurring bookings. Here's the gist:

We're gonna start with a basic implementation. A booking can be recurring - daily, weekly, monthly or annually. The booking starts at a certain time & ends at a certain time. Customers can be attached to these bookings. Both standard and DropIn bookings can be recurring. Recurring bookings will show up on the calendar & will be validated against when creating new bookings to prevent conflicts.

Fabio would use it this way.
 - Create a recurring booking every Thursday between 8-10 pm for Customer X.
- Create a recurring booking every Sunday between 4-6 pm for Customer X.

of course, existing bookings can also be made recurring. 
## Implementation
1. Add a new `RecurringBookings`. Key columns:
	- Id, VenueId, CustomerId (nullable)
	- Title, Notes, BookingType
	- StartTime, EndTime (as TimeOnly to store the time of day)
	- Frequency (Daily, Weekly, Annually)
	- DayOfWeek (array, nullable)
	- StartDate, EndDate (as DateOnly, with EndDate being mandatory and validated)
	- LastGeneratedDate (to track the progress of the background job)
	- IsActive (to easily pause/disable a series)
2. Add a nullable `RecurringBookingId` foreign key to the `Bookings` table
3. Modify `CreateBookingRequest`
	1. Add an optional RecurrenceInfo object to the CreateBookingRequest model.
	```cs
	public class RecurrenceInfo
	{
	    public required string Frequency { get; set; } // "Weekly", etc.
	    public List<DayOfWeek>? ByDay { get; set; }
	    public required DateOnly EndDate { get; set; } // Mandatory
	}
	```
	2.  Update the Handler Logic: The Handle method in `CreateBookingRequest.cs` will have a conditional branch:
	    - **If Recurrence is null:** Execute the existing logic for creating a single booking.
	    - **If Recurrence is not null:**    
	        1. Validate that the `EndDate` is no more than 6 months after the `StartDateTime`.
	        2. Create and save the new `RecurringBooking` template entity.
	        3. Immediately create the first Booking instance for the `StartDateTime` provided, linking it with the new `RecurringBookingId`. Set `LastGeneratedDate` on `RecurringBooking`.
	        4. Return a Success response for this first created booking, so the user gets immediate feedback.
	3. Update the Validator: Add a conditional validation block `(When(x => x.Recurrence != null, ...))` to enforce the 6-month limit and require the `EndDate`.
4. Create a background job to generate `Booking` instances following the `RecurringBooking` template
	1. This should be enqueued with the `RecurringBookingId`.
	2. It should calculate the dates of future occurrences between `LastGeneratedDate` and `EndDate`.
	3. For each calculated occurrence, perform a conflict check against the Bookings table.
	4. If there's no conflict, create a new Booking instance and save it.
	5. Update the `LastGeneratedDate` on the parent `RecurringBooking` template to prevent re-processing.
	6. If there's a conflict, save it as an error so we can notify the user at the end of this method.
5. Making a series non-recurring. To stop a series:
	1. Update the parent `RecurringBooking` entity (e.g., set `IsActive` = false and update `EndDate` to the current date).
    2. Delete all future Booking instances that have the corresponding `RecurringBookingId`.
## Edge Cases
1. Timezone and Daylight Saving Time (DST
	- **The Problem:** Fabio sets a recurring booking for 8:00 PM every Thursday. DST starts or ends. Should the booking be at 8:00 PM local time or should it shift by an hour? Users almost always expect it to remain at 8:00 PM local time.
	- **Required Solution:** The background job must be timezone-aware. When generating a Booking instance for a specific date, it must:
	    1. Take the `StartDate` (e.g., 2025-11-06) and the `StartTime` (e.g., 20:00).
	    2. Combine them into a local `DateTime` for the venue.
	    3. Use `ITimeZoneService` to convert this local `DateTime` into the correct `StartDateTimeUtc` for that specific date.  This prevents DST shifts from breaking the user's expectation.
2. Modification of an Entire Series
	- **The Problem:** Fabio wants to change his recurring Thursday 8-10 PM booking to 7-9 PM, starting next month. This is more complex than just updating a value.
- **Proposed Solution (Safest Approach):** Treat this as an "end and new" operation.
    1. The UI would present this as "editing" the series.
    2. Behind the scenes, the API would take the user's request and:  
        a. Update the EndDate of the original RecurringBooking template to the last valid date before the change.  
        b. Create a new RecurringBooking template with the updated details (new time, new StartDate).
    3. This avoids a messy process of deleting and regenerating bookings, which could fail if individual future instances were already paid for or modified.
3. Conflict Resolution Strategy
	- **The Problem:** The background job tries to create a booking for next Thursday, but Fabio's colleague has already booked that slot for a one-off event. What happens? 
    - **Solution - Skip and Notify:** The job skips the conflicting slot and creates a notification for the venue manager (email and in-app alert). The notification should be clear: "Could not create recurring booking 'Fabio's Football' on Nov 20, 2025, due to a conflict with booking BK-123XYZ."
4. Customer/Data Integrity
	- **The Problem:** Customer X, who has a 6-month recurring booking, is deleted from the system. What happens to the `RecurringBooking` template and all the future generated Booking instances?
	- **Required Solution:** The "Delete Customer" logic must be updated. When a customer is deleted, the system must also:
	    1. Find and delete any `RecurringBooking` templates linked to that `CustomerId`.
	    2. Find and delete all future, non-completed `Booking` instances linked to that `CustomerId`. This prevents orphaned bookings and templates in the system. We must warn users about what data is being deleted when they do this.
5. Drop-In Recurring Bookings
	- **Consideration:** On the calendar, we should display DropIn bookings with a different color  to distinguish them from standard customer-attached bookings.
6. The "First Booking" Conflict
	- **The Problem:** When creating a new recurring series, the current Handler logic checks for conflicts for the very first booking instance. But what if the first slot is free, but the second one (next week) is booked?
	- **Solution:** the Handler (create/update booking) should perform a "dry run" conflict check for at least a few future periods (e.g., the next 4 occurrences or 1 month's worth). If any conflicts are found in this initial check, the entire creation request should be rejected upfront with a clear error message. This provides a much better user experience than creating the series and then having it fail silently in the background a week later.
## Updating Existing Bookings
A user can do multiple things when updating a booking:
1. Update the booking as normal. This is what we currently support
2. Make a on booking recurring
3. Update a booking in a series, but only that specific booking
4. Updating a booking in a series and all future bookings in the series
5. Make a booking non-recurring (and delete future bookings in the series)

We will update the `UpdateBookingRequest` endpoint to support this. 
```cs
public class UpdateBookingRequest : IRequest<Result<BookingResponse>> {
    // NEW PROPERTY: To control the scope of the update for recurring bookings.
    // Allowed values: "ThisEventOnly", "ThisAndFutureEvents". Defaults to "ThisEventOnly".
    public string UpdateScope { get; set; } = "ThisEventOnly";

    // NEW PROPERTY: To make an existing booking recurring.
    // Same model used in the Create request.
    public RecurrenceInfo? Recurrence { get; set; }
}
```

Then the new handle logic:
```cs
public async Task<Result<BookingResponse>> Handle(UpdateBookingRequest request, CancellationToken cancellationToken)
{
    // 1. Fetch the booking and its related data (same as before)
    var booking = await context
        .Bookings.Include(b => b.Venue).ThenInclude(v => v.OperatingHours)
        .FirstOrDefaultAsync(b => b.Id == request.BookingId /* ... */, cancellationToken);

    if (booking is null)
    {
        return Result<BookingResponse>.Failure(Errors.Booking.NotFound);
    }

    // 2. NEW LOGIC BRANCH: Check if the user is trying to make a single booking recurring.
    if (booking.RecurringBookingId is null && request.Recurrence is not null)
    {
        // This is the "make existing booking recurring" flow.
        return await MakeBookingRecurringAsync(booking, request, cancellationToken);
    }

    // 3. NEW LOGIC BRANCH: Handle updates to bookings already in a series.
    if (booking.RecurringBookingId is not null)
    {
        return request.UpdateScope switch
        {
            "ThisAndFutureEvents" => await UpdateThisAndFutureBookingsAsync(booking, request, cancellationToken),
            _ => await UpdateSingleBookingOnlyAsync(booking, request, cancellationToken), // Default to "ThisEventOnly"
        };
    }

    // 4. Fallback to the original logic for a simple update of a non-recurring booking.
    return await UpdateSingleBookingOnlyAsync(booking, request, cancellationToken);
}
```

Make a one-off booking recurring:
```cs
private async Task<Result<BookingResponse>> MakeBookingRecurringAsync(Booking booking, UpdateBookingRequest request, CancellationToken ct)
{
    logger.LogInformation("Making existing booking {BookingId} recurring", booking.Id);

    // Validate the new recurrence rules (time, conflicts for first few, 6-month limit, etc.)
    // ...

    var strategy = context.Database.CreateExecutionStrategy();
    return await strategy.ExecuteAsync(async () =>
    {
        await using var transaction = await context.Database.BeginTransactionAsync(ct);

        // 1. Create the new RecurringBooking template from the request.
        var recurringBooking = new RecurringBooking
        {
            Title = request.Title,
            VenueId = booking.VenueId,
            CustomerId = booking.CustomerId,
            // ... copy all relevant properties
            StartDate = DateOnly.FromDateTime(request.StartDateTime),
            EndDate = request.Recurrence!.EndDate,
            RecurrenceRule = ConvertToRRule(request.Recurrence),
        };
        context.RecurringBookings.Add(recurringBooking);
        await context.SaveChangesAsync(ct); // Save to get the new ID

        // 2. Update the original booking to be the first in the series.
        booking.RecurringBookingId = recurringBooking.Id;
        booking.Title = request.Title;
        // ... update other properties on the first booking from the request
        await context.SaveChangesAsync(ct);
        
        // 3. Trigger background job to generate future bookings.
        // _backgroundJobClient.Enqueue<GenerateRecurringBookingsJob>(j => j.ExecuteFor(recurringBooking.Id));

        await transaction.CommitAsync(ct);
        return Result<BookingResponse>.Success(BookingMapper.ToBookingResponse(booking));
    });
}
```

Update a booking in a series, not updating future events:
```cs
private async Task<Result<BookingResponse>> UpdateSingleBookingOnlyAsync(Booking booking, UpdateBookingRequest request, CancellationToken ct)
{
    logger.LogInformation("Updating single booking instance {BookingId}", booking.Id);

    // Perform all conflict and operating hours checks (same as your original handler)
    // ...

    // Update booking details from the request
    booking.Title = request.Title;
    booking.StartDateTimeUtc = /* ... new start UTC */;
    booking.EndDateTimeUtc = /* ... new end UTC */;
    // ...

    // If this booking was part of a series, it has now become an exception.
    // Detach it so it's no longer managed by the series.
    if (booking.RecurringBookingId is not null)
    {
        booking.RecurringBookingId = null;
    }

    await context.SaveChangesAsync(ct);
    return Result<BookingResponse>.Success(BookingMapper.ToBookingResponse(booking));
}
```

Update the current booking and all future occurrences: 
```cs
private async Task<Result<BookingResponse>> UpdateThisAndFutureBookingsAsync(Booking booking, UpdateBookingRequest request, CancellationToken ct)
{
    var strategy = context.Database.CreateExecutionStrategy();
    return await strategy.ExecuteAsync(async () =>
    {
        await using var transaction = await context.Database.BeginTransactionAsync(ct);
        var originalRecurringBookingId = booking.RecurringBookingId!.Value;

        // 1. End the old recurring series by setting its EndDate to just before this booking.
        var parent = await context.RecurringBookings.FindAsync(originalRecurringBookingId);
        if (parent != null)
        {
            parent.EndDate = DateOnly.FromDateTime(booking.StartDateTimeUtc.AddDays(-1));
        }

        // 2. Delete all future bookings from the old series.
        var futureBookings = await context.Bookings
            .Where(b => b.RecurringBookingId == originalRecurringBookingId && b.StartDateTimeUtc > booking.StartDateTimeUtc)
            .ToListAsync(ct);
        context.Bookings.RemoveRange(futureBookings);

        // 3. Check if the user wants to stop the series entirely.
        if (request.Recurrence is null)
        {
            // This is the "Make Non-Recurring" flow.
            logger.LogInformation("Making recurring series for {BookingId} non-recurring", booking.Id);
            booking.RecurringBookingId = null; // Detach the current booking
            // We've ended the old series and deleted future bookings. We're done.
        }
        else
        {
            // This is the "Update The Series" flow.
            logger.LogInformation("Updating series starting from booking {BookingId}", booking.Id);
            // Create a NEW recurring series starting from this booking's new details.
            var newRecurringBooking = new RecurringBooking { /* ... from request ... */ };
            context.RecurringBookings.Add(newRecurringBooking);
            await context.SaveChangesAsync(ct); // Get ID

            booking.RecurringBookingId = newRecurringBooking.Id; // Link current booking to the new series
            // Trigger background job for the new series...
        }

        // 4. Finally, apply the requested updates to the current booking instance itself.
        // ... (update title, time, etc. from the request) ...

        await context.SaveChangesAsync(ct);
        await transaction.CommitAsync(ct);

        return Result<BookingResponse>.Success(BookingMapper.ToBookingResponse(booking));
    });
}
```

### API Usage
- Update a one-off booking
	- `UpdateScope`: ThisEventOnly
	- `Recurrence`: null
	- `Calls`: UpdateSingleBookingOnlyAsync
- Make a one-off booking recurring
	- `Recurrence`: {...rules...}
	- `Calls`: MakeBookingRecurringAsync
- Change one event in a series:
	- `UpdateScope`: ThisEventOnly
	- `Calls`:  UpdateSingleBookingOnlyAsync (detaches it from the series)
- Stop a recurring series:
	- `UpdateScope`: ThisAndFutureEvents
	- `Recurrence`: null
	- `Calls`: UpdateThisAndFutureBookingsAsync (ends old series, deletes future)
- Change a recurring series:
	- `UpdateScope`: ThisAndFutureEvents
	- `Recurrence`: {...new rules...}
	- `Calls`: UpdateThisAndFutureBookingsAsync (ends old series, starts a new one)