## Goal

Extract Drop In Bookings Feature so it is useable by Joe - the game manager - for managing his weekly games. People should be able to pay for a ticket & receive a confirmation. Joe does not own a venue, so this must be considered. Joe can see users that have paid, copy their names into a numbered list & generate random teams.
## Context
We have three existing codebases:
1. Qball Admin: Frontend, Svelte
2. Qball: Frontend, React
3. Qball Backend: C#

Qball hasn't been updated for a year, and I can't write React - only Svelte. Qball Admin is meant for venue managers and is tailored to them completely. Qball Backend serves both applications, but is focused on Admins/Venue Managers as the source of bookings. The booking model in system looks like this:

```cs
public class Booking : BaseEntity
{
    public required string Title { get; set; }
    public DateTime StartDateTimeUtc { get; set; }
    public DateTime EndDateTimeUtc { get; set; }
    public required string Code { get; set; }
    public int? ExpectedNumberOfPlayers { get; set; }
    public decimal? ExpectedAmountPerPlayer { get; set; } // Nullable for standard bookings

    // Stores the hourly rate at the time the booking was made.
    public decimal? PricePerHour { get; set; } // not needed for dropin bookings

    // Stores the final calculated price. Essential for invoices.
    public decimal? TotalPrice { get; set; }
    public string? Notes { get; set; }
    public BookingPaymentStatus PaymentStatus { get; set; } = BookingPaymentStatus.Pending;
    public BookingStatus Status { get; set; } = BookingStatus.Confirmed;
    public BookingType Type { get; set; } = BookingType.Standard;

    /// <summary>
    /// When true, allows payment collection outside the booking's time window and allows users to see the booking on the venue page.
    /// When false, payments can only be collected between StartDateTimeUtc and EndDateTimeUtc.
    /// Typically true for drop-in bookings to allow advance registration.
    /// Does not apply to standard bookings.
    /// </summary>
    public bool IsPublic { get; set; } = false; // Only for drop-in bookings at the moment.

    // Requester details for bookings made before customer is known/created
    public string? RequesterFirstName { get; set; }
    public string? RequesterLastName { get; set; }
    public string? RequesterEmail { get; set; }
    public string? RequesterPhoneNumber { get; set; }

    // Navigation properties
    public required int VenueId { get; set; }
    public Venue Venue { get; set; } = null!;

    public string? CustomerId { get; set; }
    public Customer? Customer { get; set; }

    public string? RecurringBookingId { get; set; }
    public RecurringBooking? RecurringBooking { get; set; }

    public VenueBookingBankAccount? VenueBookingBankAccount { get; set; }

    public ICollection<VenueBookingTicket> Tickets { get; set; } = [];
    public ICollection<VenueTransaction> Transactions { get; set; } = [];

    internal static Booking CreateStandardBooking(
        CreateBookingRequest request,
        DateTime startUtc,
        DateTime endUtc,
        string bookingCode,
        Customer? customer
    )
    {
        if (!request.PricePerHour.HasValue)
        {
            throw new InvalidOperationException("Cannot create a standard booking without a PricePerHour. The request was not validated correctly.");
        }

        var durationInHours = (decimal)(endUtc - startUtc).TotalHours;
        var pricePerHour = request.PricePerHour;

        var booking = new Booking
        {
            Title = request.Title,
            StartDateTimeUtc = startUtc,
            EndDateTimeUtc = endUtc,
            Code = bookingCode,
            ExpectedNumberOfPlayers = request.ExpectedNumberOfPlayers,
            ExpectedAmountPerPlayer = null,
            Notes = request.Notes,
            Type = BookingType.Standard,
            Status = BookingStatus.Confirmed,
            Customer = customer,
            CustomerId = customer?.Id,
            VenueId = request.VenueId,
            PricePerHour = pricePerHour,
            TotalPrice = pricePerHour * durationInHours,
        };

        return ValidateAndThrowIfInvalid(booking);
    }

    internal static Booking CreateStandardBooking(RequestBookingRequest request, string title, string bookingCode, Venue venue)
    {
        var durationInHours = (decimal)(request.EndDateTimeUtc - request.StartDateTimeUtc).TotalHours;
        var pricePerHour = venue.VenueSettings.DefaultBookingPricePerHour;

        var booking = new Booking
        {
            Title = title,
            StartDateTimeUtc = request.StartDateTimeUtc,
            EndDateTimeUtc = request.EndDateTimeUtc,
            Code = bookingCode,
            ExpectedNumberOfPlayers = request.ExpectedNumberOfPlayers,
            Notes = request.Notes,
            VenueId = venue.Id,
            RequesterFirstName = request.FirstName,
            RequesterLastName = request.LastName,
            RequesterEmail = request.Email,
            RequesterPhoneNumber = request.PhoneNumber,
            Type = BookingType.Standard,
            Status = BookingStatus.Requested,
            PricePerHour = pricePerHour,
            TotalPrice = pricePerHour * durationInHours,
        };

        return ValidateAndThrowIfInvalid(booking);
    }

    internal static Booking CreateDropInBooking(CreateBookingRequest request, DateTime startUtc, DateTime endUtc, string bookingCode)
    {
        var booking = new Booking
        {
            Title = request.Title,
            StartDateTimeUtc = startUtc,
            EndDateTimeUtc = endUtc,
            Code = bookingCode,
            ExpectedNumberOfPlayers = request.ExpectedNumberOfPlayers,
            ExpectedAmountPerPlayer = request.ExpectedAmountPerPlayer,
            Notes = request.Notes,
            Type = BookingType.DropIn,
            Status = BookingStatus.Confirmed,
            VenueId = request.VenueId,
            IsPublic = request.IsPublic,
        };

        return ValidateAndThrowIfInvalid(booking);
    }

    internal static Booking CreateStandardBooking(RecurringBooking recurringBooking, DateTime startUtc, DateTime endUtc, string bookingCode)
    {
        if (!recurringBooking.PricePerHour.HasValue)
        {
            throw new InvalidOperationException("Cannot create a standard booking without a PricePerHour. The request was not validated correctly.");
        }

        var durationInHours = (decimal)(endUtc - startUtc).TotalHours;
        var pricePerHour = recurringBooking.PricePerHour;

        var booking = new Booking
        {
            Title = recurringBooking.Title,
            StartDateTimeUtc = startUtc,
            EndDateTimeUtc = endUtc,
            Code = bookingCode,
            ExpectedNumberOfPlayers = recurringBooking.ExpectedNumberOfPlayers,
            Notes = recurringBooking.Notes,
            Type = BookingType.Standard,
            Status = BookingStatus.Confirmed,
            CustomerId = recurringBooking.CustomerId,
            VenueId = recurringBooking.VenueId,
            PricePerHour = pricePerHour,
            TotalPrice = pricePerHour * durationInHours,
            RecurringBookingId = recurringBooking.Id,
        };

        return ValidateAndThrowIfInvalid(booking);
    }

    internal static Booking CreateDropInBooking(RecurringBooking recurringBooking, DateTime startUtc, DateTime endUtc, string bookingCode)
    {
        var booking = new Booking
        {
            Title = recurringBooking.Title,
            StartDateTimeUtc = startUtc,
            EndDateTimeUtc = endUtc,
            Code = bookingCode,
            ExpectedNumberOfPlayers = recurringBooking.ExpectedNumberOfPlayers,
            ExpectedAmountPerPlayer = recurringBooking.ExpectedAmountPerPlayer,
            Notes = recurringBooking.Notes,
            Type = BookingType.DropIn,
            Status = BookingStatus.Confirmed,
            IsPublic = recurringBooking.IsPublic,
            VenueId = recurringBooking.VenueId,
            RecurringBookingId = recurringBooking.Id,
        };

        return ValidateAndThrowIfInvalid(booking);
    }

    private static Booking ValidateAndThrowIfInvalid(Booking booking)
    {
        var validator = new BookingValidator();
        var validationResult = validator.Validate(booking);
        return validationResult.IsValid ? booking : throw new ValidationException(validationResult.Errors);
    }
}
```

It requires us to specify a venue when creating a booking. Making that nullable would be hectic.
## Approaches
1. Build a new application where this is the sole focus & the game manager is the main user. The flow:
    - User signs up.
    - User provides KYC details
    - User sets up a withdrawal bank account where payments are split to.
    - User creates a booking: setting a date, address, capacity & amount.
    - User sends link to prospective attendees.
    - Attendees visit link, pay and their names show up on the booking page.
    - User can copy their names into a numbered list.
    - User can sort the attendees who have paid into random teams.
2. Extend Qball Admin to allow non venue owners access the drop in feature. The app is meant for venue managers as is. This is a violation of focus, or something.
3. Build a new frontend for this. Extend the backend: add a new user role and DB model for these types of customer-focused bookings. 
