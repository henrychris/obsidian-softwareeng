We currently issue one type of Fiscal Invoice: E31. Now, we want to add support for the other types: E33, 34 and E41.

E31: Fiscal Invoice
E33: Debit Note - for additional charges, such as freight or interest
E34: Credit Note - for corrections, such as changes to text or amounts on a previously issued fiscal invoice. or to annul a previously issued fiscal invoice.
E41: Purchase - for recording purchases from unregistered individuals. I guess this means individuals without rnc's.

These invoices can only be issued in a certain scenario.

A credit note can only be issued if the order had a fiscal invoice (E31) issued & had been changed afterwards. If a credit note has been issued, no further fiscal invoices can be issued for the order.

If the order has no fiscal invoice (E31), credit or debit notes cannot be issued.

Currently, the caller simply passes the orderId to the request fiscal receipt endpoint & an E31 is generated. 

Now, we want to allow the user to choose the type of invoice they want, and also apply the rules so they don't need to think about how to follow the law to the letter. 

## Migrations
1. Set default document type on `fiscalReceipts` collection
```json
// filter
$or: [
          { documentType: { $exists: false } },
          { payloadSent: { $exists: false } },
          { responseLast: { $exists: false } },
        ]

// update query
$set: {
 documentType: "E31",
          payloadSent: null,
          responseLast: null,
          }
```
2. Set default document type on `encfSequences` collection
```json
// filter
{         documentType: { $exists: false }        }

// update query
documentType: "E31"
```