We noticed that roles have the `edit-order-payment` permission duplicated in permission.Orders. I generated a script to remove the duplicate. This code lives on `chore/deduplicate-permissions`.

# Missing Owner role
Some stores have no owner role, but all stores ought to have an owner role.