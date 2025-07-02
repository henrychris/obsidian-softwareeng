After providing order details, users hit the 'checkout' button. This pulls up the the select payment modal.
![[Pasted image 20250416111141.png]]
After selecting an option, this body is sent to the backend:
- Cash Payment
```json
{
    "type": "credit",
    "orderId": "67ff82d058afef2db852b75e",
    "paymentStatus": "paid",
    "payments": [
        {
            "amount": "70.00",
            "status": "success",
            "message": "Order payment with cash",
            "option": "cash"
        }
    ],
    "customer": "Walk-In"
}
```
- Split Payment (full amount)
```json
{
    "type": "credit",
    "orderId": "67ff831858afef2db852b891",
    "paymentStatus": "paid",
    "payments": [
        {
            "amount": 15,
            "status": "success",
            "message": "First split payment with cashapp",
            "option": "cashapp"
        }
    ],
    "customer": "Walk-In"
}
```
- Split Payment (part payment)
```json
{
    "type": "credit",
    "orderId": "67ff836958afef2db852b93f",
    "paymentStatus": "paid",
    "payments": [
        {
            "amount": 10,
            "status": "success",
            "message": "First split payment with others",
            "option": "others"
        }
    ],
    "customer": "Walk-In"
}
```
Now, we wish to replace these with store defined Payment Methods.
![[Pasted image 20250416112044.png]]

The default payment methods must be created for all stores & are enabled by default.
Users can add custom payment methods:
![[Pasted image 20250416112436.png]]
The radio button determines what payment status should be applied to the order when the payment method is selected. However, I think this can lead to bugs and the payment status should instead be derived based on how much is received vs how much is expected

![[Pasted image 20250416112708.png]]
Custom payment methods can be enabled and disabled. They can also be edited to change the name and status modifier.
## Endpoints

## Implementation
- Add StorePaymentMethod model
	- id
	- name
	- type - system or custom
	- status - active or disabled
	- section - normal or apps or custom (used by frontend to render checkout options in different visual sections)
	- statusToApplyToOrder - pending or paid (yet to decide if this stays or goes)
	- storeId
	- date created
- Update create store endpoints
	- create default storePaymentMethods matching the default payment options on the application 
- add endpoint to create storePaymentMethod. This should accept:
	- name
	- statusToApplyToOrder - pending or paid (yet to decide if this stays or goes)
- add endpoint to update storePaymentMethod. This should accept:
	- storePaymentMethodId (optional)
	- name (optional) 
	- status - active or disabled (optional)
	- statusToApplyToOrder - pending or paid (yet to decide if this stays or goes)
- add endpoint to get all storePaymentMethods
	- This should return an array of storePaymentMethod objects
- update create payment endpoint
	- accept storePaymentMethodId, instead of `option` string
	- validate that storePaymentMethod exists in store & isActive, else return an error
	- apply the status specified in `statusToApplyToOrder` to the Order.
## Notes
We will need to update existing payments, update finance analytics to fetch payment breakdown using  `storePaymentMethodId` instead of the payment option string and add default `storePaymentMethod` models to all stores

### Store
- Run a script to add default `storePaymentMethods` to all stores in the system that do not have them. 
### Existing Payments
- Add a nullable `storePaymentMethodId` field to the payment model.
- Run a script to fetch the `storePaymentMethod` using the name and insert the `storePaymentMethodId` into the `Payment` model
- When this is done, all payments will reference the `storePaymentMethod`, instead of only storing the payment method name.
### Update Analytics
- Finance analytics currently groups payments by the option string. After implementing the `storePaymentMethod` model, we will update the query to group by the `storePaymentMethodId` field on the `Payment` model.