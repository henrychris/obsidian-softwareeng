Sandbox Credentials
- ID - 01K0F16XZ9145TDARMEXDVS4YR
- Active - Yes
- User - FixMasterPOS
- Email - fixmasterpos@alanube.co
- Auth ID - 9fd0e65a-26ae-4a60-a4e2-99a576c8c153
- Countries - [ "dom" ]
- DOM - { "range": "9425001-9426000" }

- Environment: Sandbox
- URL: https://sandbox-reseller.alanube.co/login
- Username: lunixpos@alanube.co
- Password: 01K722XJVQ7PY4V5497A6WHKPX@a
- Billing Range: 9474001-9475000 (each encf uses the next number, i guess? they dont really say)
- Test RNC: 132109122
- Token: Ver adjunto
**
# Endpoints
## Create A Company
URL: POST [https://sandbox.alanube.co/dom/v1/company](https://sandbox.alanube.co/dom/v1/company)
Required data:
- name    
- tradeName    
- identification (company rnc)    
- type (associated)    
- address    
- province    
- municipality   
- certificate  
- name    
- extension    
- content
- password
## Issue A Fiscal Invoice
URL: POST [https://developer.alanube.co/v1.0-DOM/reference/createinvoicefiscals](https://developer.alanube.co/v1.0-DOM/reference/createinvoicefiscals)
Required data:
- company
	- id - the company id on the provider
- idDoc
	- encf (idk, add placeholder with todo)
	- sequenceDate (idk, add placeholder with todo)
- incomeType
	1. Income from operations (non-financial)
	2. Financial income
	3. Extraordinary income
	4. Income from leases
	5. Income from the sale of depreciable assets
	6. Other income
- paymentType
	1. Cash
	2. Credit
	3. Free
- sender (the person issuing the receipt - a lunixPos user)
	- rnc (string, max 11)
	- companyName (string)
	- address (string)
	- stampDate (string)
	- internalOrderNumber (not required, but we should add it) (string)
	- phone number (not required, but we should add it) (string)
	- mail (not required, but we should add it) (string)
- buyer (the customer purchasing from the lunixPos user)
	- rnc (string, max 11)
	- companyName (string)
	- contact - Buyer name and phone number (not required, but we should add it) (string)
	- mail (not required, but we should add it) (string)
- totals
	- totalAmount - Total Taxable Amount + Exempt Amount + Total VAT + Additional Tax Amount (number)
	- exemptAmount (not required, but we should add it since we have products that are non-taxable) (number)
- itemDetails - array of objects. The list of products in the order
	- lineNumber (number, starting at 1, max 1000)
	- billingIndicator - indicates if the item is exempt, taxable or non-billable (number) 
		1. 0. Non-billable
		2. ITBIS 1 item taxed at ITBIS rate 1 (18%).
		3. ITBIS 2 item taxed at ITBIS rate 2 (16%).
		4. ITBIS 3 item taxed at ITBIS rate 3 (0%).
		5. Exempt (E)
	- itemName (string)
	- goodServiceIndicator - is the item a good or a service? (number)
		1. Good
		2. Service
	- quantityItem (number, max 10000000000000000)
	- unitPriceItem (number, max 1000000000000000000)
	- discountAmount (number, depends on the subDiscounts field, must be the total of all discounts)
	- subDiscounts (array)
		- subDiscountRate ($ or %)
		- subDiscountPercentage (depends on subDiscountRate being %)
		- subDiscountAmount discount value as an amount
	- itemAmount - (Unit Price of the item * Quantity) – Discount Amount + Surcharge Amount (number, max 10000000000000000)

```json
{
    "company": {
        "id": ""     
    },
    "idDoc": {
        "encf": "",    
        "sequenceDate": ""
    },
    "incomeType": 1, // 1 or 2 or 3 or 4 or 5 or 6,
    "paymentType": 1, // 1 or 2 or 3
    "sender": {
        "rnc": "",
        "companyName": "",    
        "address": "",
        "stampDate": "",
        "internalOrderNumber": "",
        "phoneNumber": [
            ""
        ],
        "mail": ""
    },
    "buyer": {
        "rnc": "",
        "companyName": "",    
        "contact": "", // name, phone number
        "mail": ""
    },
    "totals": {
        "totalAmount": 0,
        "exemptAmount": 0,
    },
    "itemDetails": [
        {
            "lineNumber": 1, // max 1000
            "billingIndicator": 0,
            "itemName": "",
            "goodServiceIndicator": 1, // 1 or 2
            "quantityItem": 0,
            "unitPriceItem": 0,
            "discountAmount": 0,
            "subDiscounts": [
                {
                    "subDiscountRate": "$", // "$" or "%"
                    "subDiscountPercentage": 0, // if subDiscountRate is %
                    "subDiscountAmount": 0
                }
            ],
            "itemAmount"
        }
    ]
}
```

The response includes a status: REGISTERED OR TO_SEND OR WAITING_RESPONSE OR TO_NOTIFY OR FINISHED. Regardless, we will need to set up a webhook where updates will be sent to when a document is ready. We will need to find out what each status means.

Success response (201 Created)

|                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| {  <br>  "id": "01G021Z3QSRZ58GSTBH7TPGD2J",  <br>  "stampDate": "1990-12-31",  <br>  "status": "REGISTERED",  <br>  "companyIdentification": 132109122,  <br>  "encf": "E310000001727",  <br>  "xml": "https://api-alanube-e-provider-dom-test.s3.amazonaws.com/users/baa08af2-5924-4892-8554-0fe8ef561ab8/companies/f92f1ec0-80eb-4873-b06a-57534c678a04/fiscalInvoice/01G02X48J00NBR7GY1DMJ7CJXP.xml?AWSAccessKeyId=ASI...&Expires=1649368860&Signature=QB7y...&x-amz-security-token=IQoJb3J...",  <br>  "pdf": "https://api-alanube-e-provider-dom-test.s3.amazonaws.com/users/baa08af2-5924-4892-8554-0fe8ef561ab8/companies/f92f1ec0-80eb-4873-b06a-57534c678a04/fiscalInvoice/pdf/01G02X48J00NBR7GY1DMJ7CJXP.pdf?AWSAccessKeyId=ASI...&Expires=1649368860&Signature=QB7y...&response-content-disposition=attachment%3Bfilename%3DE310000001782.pdf&x-amz-security-token=IQoJb3J...",  <br>  "documentStampUrl": "https://ecf.dgii.gov.do/testecf/ConsultaTimbre?RncEmisor=123...&RncComprador=456...&ENCF=E310000001727&FechaEmision=04-04-2022&MontoTotal=1180&FechaFirma=07-04-2022%2016:58:25&CodigoSeguridad=MYUVCT",  <br>  "signatureDate": "2025-10-02T12:42:57.300Z",  <br>  "securityCode": "MYUVCT",  <br>  "sequenceConsumed": false  <br>} |
  Of course we must store the id of the generated document so that we may check the invoice status later.
## Check Status of Fiscal Invoice
URL: GET [https://sandbox.alanube.co/dom/v1/fiscal-invoices/{id}/idCompany/{idCompany}](https://sandbox.alanube.co/dom/v1/fiscal-invoices/%7Bid%7D/idCompany/%7BidCompany%7D)
We will provide the store's companyId and fiscalInvoiceId to this endpoint to check the status. This can be used in a cron job that queries for the status of invoices, instead of waiting for webhooks to arrive.

## Check Company RNC
URL: GET [https://sandbox.alanube.co/dom/v1/check-directory](https://sandbox.alanube.co/dom/v1/check-directory)
I believe this endpoint lets us check that a provided RNC is correct. Perhaps the frontend can use it to help us validate that the correct RNC is provided? The problem is, it doesn’t return details about the holder of the RNC, so I don’t think it’s useful.

The RNC is the company’s identifier.


# Gist
**how it works:**
- users subscribe to one add-on plan at a time (starter, pro, etc) as a recurring monthly charge on top of their base subscription
- this gives them a monthly credit allowance that resets at the start of each billing cycle
- if they want to switch plans, the change takes effect next cycle (no mid-cycle subscription changes)
**buying extra credits mid-cycle:**
- if users run out of credits before the month ends, they can purchase more immediately using a one-time charge
- they pick from the same plan options (starter, pro, etc) and we charge them as a one-time invoice, NOT a subscription change
- so if they're on the $100/month plan and need more credits now, they just buy another $100 worth instantly

**credit expiration:**
- hard reset at the start of each billing cycle
- when their subscription renews, credits reset to their base plan allowance
- any unused credits from purchases or the previous month are lost
- keeps the accounting simple and predictable

**switching plans:**
- users can switch between add-on tiers anytime, but it only takes effect at the next renewal
- no weird proration credits or mid-cycle changes
- they keep their current plan and allowance until the cycle ends

this way we avoid all the proration issues with stripe treating changes as replacements, and users have a clear way to top up when needed

---

Tomorrow

Switch `POST /fiscals/subscription` endpoint to use Checkout Session. Include plan Id & userId in metadata. Calculate the proration using the user's billing period and create the checkout session. When user completes payment, add the subscription item to their existing subscription. Stripe would not create an invoice, so we won't have to do all that invoice management nonsense.

We can specify a price by adding a `line item`.

Similarly, we can use checkout sessions for `POST /fiscals/topup`. Add `is_topup` to metadata.

Listen for `customer.subscription.deleted` to know when the user's subscription ends. If it ends, then remove the fiscal receipts. Use a cron job to renew the allowance every month.

```ts
const hasActiveFiscalSubscription =
    user.fiscalSubscription &&
    user.fiscalSubscription.status === FiscalSubscriptionStatus.ACTIVE &&
    (!user.fiscalSubscription.expiresAt || user.fiscalSubscription.expiresAt > new Date());
  if (!hasActiveFiscalSubscription) {
    return reply
      .status(403)
      .send(ApiResponse.error(FiscalResponses.FISCAL_SUBSCRIPTION_REQUIRED));
  }
```

[ENCF Format](https://docnova.ai/electronic-fiscal-receipt-ecf/)

The eNCF (Electronic Tax Receipt Number) structure: Format: E31XXXXXXXXXX (13 characters total) E = Electronic series indicator 31 = Fiscal credit invoice type Next 10 digits = Sequential number (e.g., 0009474001)

## Sequence Numbers
we have to generate a sequence number within the range 9474001-9475000.

using that range, we generate an encf by adding the prefix E31, and pad left the number to 10 digits.

The current range allows us to issue 999 receipts. When we use up that allowance, we will be issue a new range of sequence numbers.

It's possible that this range does not immediately follow the last sequence we were issued. That is, after we use 9475000, it is not certain that the next range we are issued starts from **9475001**. We can't simply increment our last sequence number, because these sequences are issued by the government, and might have been issued to a different company - not us.

When we use up our sequences, I want the system to be able to pick up the new sequence, and start generating receipts without us having to change anything else.
### Idea
Add `EncfSequence` model with four fields:
-   `start_sequence` (integer)
-   `end_sequence` (integer)
-   `current_sequence` (integer)
-   `is_active` (boolean)
-   `provider` (enum)

When generating a new receipt, the system will look for the active `EncfSequence`, and use the `current_sequence` to generate the receipt.
When a receipt is generated, the `current_sequence` is incremented by 1.

When the `current_sequence` exceeds or is equal the `end_sequence`, the system will throw an error indicating that the sequence is exhausted. We could also immediately disable the `EncfSequence`.

We should make sure we only ever have one active `EncfSequence` at a time.

When we are issued a new sequence range, we can create a new `EncfSequence` record, and set it as active, while deactivating the previous one.
When creating a new `EncfSequence`, we should validate that the new range does not overlap with any existing ranges in the database.
When generating the `encf`, we will pad the `current_sequence` to 10 digits and add the prefix `E31`.
This way, the system can seamlessly transition to new sequence ranges without any manual intervention in the receipt generation process.
### Concerns
-   Are we overcompensating for one provider?

