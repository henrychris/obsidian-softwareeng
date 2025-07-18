# Shared Interface
```cs
public interface IPaymentProvider
{
    Task<Result<PaymentCheckoutResult>> CreateCheckoutAsync(PaymentCheckoutRequest request);
    Task<Result<SubAccountResult>> CreateSubAccountAsync(SubAccountCreateRequest request);
    Task<Result<WebhookHandlingResult>> HandleWebhookAsync(string rawPayload, IHeaderDictionary headers);
}

public class PaymentCheckoutRequest
{
    public required decimal Amount { get; set; }
    public required string CustomerFullName { get; set; }
    public required string CustomerEmail { get; set; }
    public required string TransactionReference { get; set; }
    public required string SubAccountCode { get; set; }
    public required string BookingId { get; set; } // metadata
    public required string VenueId { get; set; } // metadata
}

public class PaymentCheckoutResult
{
    public string ProviderTransactionReference { get; init; } = null!;
    public string CheckoutUrl { get; init; } = null!;
}

public class SubAccountCreateRequest
{
    public required string CurrencyCode { get; set; }
    public required string BankCode { get; set; }
    public required string AccountNumber { get; set; }
    public required string EmailAddress { get; set; }
    public required string BVN { get; set; }
}

public class SubAccountResult
{
    public string BankCode { get; init; } = null!;
    public string CurrencyCode { get; init; } = null!;
    public string SubAccountCode { get; init; } = null!;
}

public class WebhookEvent
{
    public required string EventType { get; init; }
    public required string TransactionReference { get; init; }
    public string? BookingId { get; init; }
    public string? VenueId { get; init; }
    public required decimal AmountPaid { get; init; }
    public required DateTime PaidOn { get; init; }
    public required string RawPayload { get; init; }
}

public enum WebhookHandlingStatus
{
    Processed,
    Duplicate,
    InvalidSignature,
    UnsupportedEvent,
    Error,
}

public class WebhookHandlingResult
{
    public WebhookHandlingStatus Status { get; init; }
    public WebhookEvent? Event { get; init; }
    public string? ErrorMessage { get; init; }
}
```

# Factory
```cs
public interface IPaymentProviderFactory
{
    IPaymentProvider Get(PaymentProvider provider);
}

public class PaymentProviderFactory(IServiceProvider serviceProvider) : IPaymentProviderFactory
{
    public IPaymentProvider Get(PaymentProvider provider)
    {
        return provider switch
        {
            PaymentProvider.Monnify => serviceProvider.GetRequiredService<MonnifyProvider>(),
            _ => throw new NotSupportedException($"Unsupported provider: {provider}"),
        };
    }
}
```

# Monnify Provider
```cs
public class MonnifyProvider(IMonnifyApi monnifyApi, IOptions<MonnifySettings> options) : IPaymentProvider
{
    private readonly MonnifySettings _monnifySettings = options.Value;

    public Task<Result<PaymentCheckoutResult>> CreateCheckoutAsync(PaymentCheckoutRequest request)
    {
        throw new NotImplementedException();
    }

    public Task<Result<SubAccountResult>> CreateSubAccountAsync(SubAccountCreateRequest request)
    {
        throw new NotImplementedException();
    }

    public Task<Result<WebhookHandlingResult>> HandleWebhookAsync(string rawPayload, IHeaderDictionary headers)
    {
        throw new NotImplementedException();
    }
}
```