I used this update query to move access-to-price from Settings to Products
```json
  [
    {
      $set: {
        "permissions.Products": {
          $concatArrays: [
            { $ifNull: ["$permissions.Products", []] },
            {
              $filter: {
                input: "$permissions.Settings",
                cond: { $eq: ["$$this.title", "access-to-price"] }
              }
            }
          ]
        },
        "permissions.Settings": {
          $filter: {
            input: "$permissions.Settings",
            cond: { $ne: ["$$this.title", "access-to-price"] }
          }
        }
      }
    }
  ]
```

# Todo
- On deploy to beta, run this query - done
- On deploy to live, run this query - done. 