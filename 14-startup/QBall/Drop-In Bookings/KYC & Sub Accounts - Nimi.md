We're building a feature that allows venue owners to receive payments through our platform. This involves collecting personal information and setting up payment accounts. We need your review on the following implementation:

**What We're Collecting:**
- Personal details: First name, middle name, last name, email, phone number, home address, date of birth
- Bank Verification Number (BVN) - Nigeria's unique banking identifier
- Bank account details: Bank name, account number, account name

**How We Handle This Data:**
1. Users voluntarily provide their information to set up payments
2. We encrypt and store their BVN in our database
3. We use a third-party service (Monnify) to verify that the BVN matches the person's identity
4. We use the same service to verify that the BVN matches their bank account
5. If verification passes, we create a "subaccount" with the payment provider so the venue can receive money

**Key Legal Questions:**
1. **BVN Storage**: Are we legally allowed to store Bank Verification Numbers, even if encrypted? What are the compliance requirements?
2. **Data Protection**: What Nigerian data protection laws apply to storing this personal and financial information?
3. **Consent**: Is the user's voluntary submission sufficient, or do we need specific consent language?
4. **Third-Party Sharing**: Are there restrictions on sharing BVN data with payment processors like Monnify for verification?
5. **Revenue Split**: We automatically take a percentage of payments before sending the rest to the venue - are there disclosure requirements for this?

**Our Security Measures:**
- BVN is encrypted before storage
- We only use the data for identity verification and payment processing
- We don't store raw BVN data
- All verification is done through licensed payment processors

Please advise if this implementation complies with Nigerian banking, data protection, and financial regulations, and what additional safeguards or disclosures we might need.

# Update - July 11
This document is now outdated, as we have consulted with Nimi.