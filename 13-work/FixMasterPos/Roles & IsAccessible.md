There is a field named `isAccessable` on the Permission sub-model of our Roles model. Sammie noticed some fields have `isAccessible` instead, which caused problems when validating permissions on the frontend.

## Dev Environment
1. I figured out only `permissions.Order` fields had `isAccessible` in their permission objects. I used this query to find them:
```ts
{
  "permissions.Order.isAccessible": {
    $exists: true
  }
}
```
2. I had Claude generate a query to add an `isAccessable` field with the same value. The query:
```ts
// add isAccessable value where isAccessible exists

[
  {
    $set: {
      "permissions.Order": {
        $map: {
          input: "$permissions.Order",
          as: "item",
          in: {
            $mergeObjects: [
              "$$item",
              {
                $cond: {
                  if: {
                    $ne: [
                      {
                        $type:
                          "$$item.isAccessible"
                      },
                      "missing"
                    ]
                  },
                  then: {
                    isAccessable:
                      "$$item.isAccessible"
                  },
                  else: {}
                }
              }
            ]
          }
        }
      }
    }
  }
]
```
3. Now that each permission has the correct field, we can remove the wrong one with this:
```ts
// remove isAccessible field 
 
{ $unset: { "permissions.Order.$[].isAccessible": "" } }
```

This solves the problem.