1. when a repair product exists in a card, clicking add issue should add the new issue to the existing repair product.,
2. However, if the user chooses to add a new repair device, then it should be separate from the one that exists in the cart, even if they are the same kind of device.,

there's a function in cart controller to handle this scenario, I'll use it and make any needed changes.

When an issue is added to an existing repair product, this JSON is sent:
```json
{
    "repairProduct": {
        "id": "66e7dc17886d37575ad8999c",
        "title": "iPhone 16 Pro Max",
        "serviceAndRepairs": [
            {
                "title": "Charging Port - Charging port Pin",
                "stock": 0,
                "cost": 0,
                "price": 0,
                "sku": "",
                "parent": "Charging Port",
                "quantity": 1
            }
        ],
        "quantity": 1,
        "action": "add-issue",
        "index": 0
    }
}

```

When I added a new repair product (different device):
```json
{
    "repairProduct": {
        "id": "66e7dc17886d37575ad89999",
        "title": "iPhone 16",
        "serviceAndRepairs": [
            {
                "title": "Cameras - Rear Camera",
                "stock": 0,
                "cost": 0,
                "price": 0,
                "sku": "",
                "parent": "Cameras",
                "quantity": 1
            }
        ],
        "quantity": 1,
        "action": "add-repair",
        "index": 0
    }
}
```

Added a new repair product (same device):
```json
{
    "repairProduct": {
        "id": "66e7dc17886d37575ad8999c",
        "title": "iPhone 16 Pro Max",
        "serviceAndRepairs": [
            {
                "title": "Back Glass - Black",
                "stock": 0,
                "cost": 0,
                "price": 0,
                "sku": "",
                "parent": "Back Glass",
                "quantity": 1
            },
            {
                "title": "Back Glass - White",
                "stock": 0,
                "cost": 0,
                "price": 0,
                "sku": "",
                "parent": "Back Glass",
                "quantity": 1
            }
        ],
        "quantity": 1,
        "action": "add-repair",
        "index": 0
    }
}
```