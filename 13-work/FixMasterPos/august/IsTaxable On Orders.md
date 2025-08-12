# Summary
when we create an order from a cart, we're losing the `isTaxable` field during the transfer. this causes a tax calculation bug: if someone manually adjusts a product's price upward on an existing order, and that increase pushes the total above the original `nonTaxableAmount`, we incorrectly calculate tax on the difference—even for products that should be tax-exempt. 
# Fix
1. add `isTaxable` field to the `productsForSell` schema in the order model,
2. ensure `isTaxable` gets passed from cart to order during order creation,
3. update tax calculation logic to respect the `isTaxable` flag,

this will preserve the original tax exemption status and prevent incorrect tax charges when an order is updated.

# Update
I have completed the migration script. It lives on a branch named `chore/migrate-add-is-taxable-to-orders`.
# Notes
- For variable products, `isTaxable` is stored in the variation object.
```json
{
    "variation": {
        "id": "6891f70e7df0a95ad62fabac",
        "title": "kitty",
        "isTaxable": false,
	    "isService": false
    },
    "discount": { "type": "%", "value": 0 },
    "id": "6891f70e7df0a95ad62fabaf",
    "title": "non taxable variant",
    "isService": false,
    "type": "variable",
    "actionType": "sell",
    "slug": "non-taxable-variant",
    "isTaxable": false,
    "cost": 10,
    "sku": "G2DU32",
    "price": 100,
    "imei": [],
    "thumbnail": "",
    "images": [],
    "quantity": 1,
    "_id": "6891f73a7df0a95ad62fad0b",
    "serviceCharge": 0,
	"currency": "USD",
	"minimumPrice": 0,
	"discountAmount": 0,
    "totalPrice": 100
}
```
- For simple and serialised products, refer to the `isTaxable` field on the object root
```json
{
    "discount": { "type": "%", "value": 0 },
    "id": "6890c546f03464b9729ec681",
    "title": "not taxable ",
    "isService": false,
    "type": "simple",
    "actionType": "sell",
    "slug": "not-taxable",
    "isTaxable": false, // here
    "cost": 0,
    "sku": "X7KME8",
    "price": 100,
    "imei": [],
    "thumbnail": "",
    "images": [],
    "quantity": 1,
    "_id": "6891f76d7df0a95ad62fadbc",
    "serviceCharge": 0,
    "currency": "USD",
    "minimumPrice": 0,
    "discountAmount": 0,
    "totalPrice": 100
}
```

# Application
- Dev - DONE
- Beta - 
- Live - IN PROGRESS