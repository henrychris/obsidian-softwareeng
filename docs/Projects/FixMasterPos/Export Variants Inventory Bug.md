How to reproduce:
- a store has two locations
- both locations have the same product in stock
- location one has 10 items. location two has 5 items.
- If the user exports products from location two, the product will have location one quantity listed in the CSV
Possible Cause:
- the query to fetch products includes inventory at all locations
- we use inventory\[0\] to get inventory, which fetches the inventory from the first location - not necessarily from the location being exported from.

This has been fixed by fetching the inventory from the selected location. 

# Bug 2 - Invalid Exported Options
I am not able to reproduce this. However, QA are able to:
- create variable product on UI
- export selected product

The exported CSV has only option name filled out, while the values are empty