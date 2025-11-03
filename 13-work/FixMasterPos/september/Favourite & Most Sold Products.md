# Goal
The new Create Order UI will include two new tabs: a managed **"Favourite Products"** list and a system-generated **"Most Sold Products"** list.
# Proposed Solution
-   **Favourite Products:**
    -   Introduce a new `FavouriteProduct` model to store a list of products favourited for a specific **store and location**.
    -   This list is **shared and visible to all users** within the store, not tied to a specific user account.
    -   Create new API endpoints to allow users to add and remove products from this shared list, with a hard limit of **13 favourites per location**.
    -   The user who adds a product to the list will be tracked for attribution.
-   **Most Sold Products:**
    -   Implement a new API endpoint that calculates the top **14** most sold products on-demand for a specific **location**.
    -   The calculation will be based on sales data from the last **30 days**.
    -   Results will be aggressively cached using Redis for **12 hours**.
# Data Models
## 1. New Model - `FavouriteProduct`
A new collection will store the shared list of favourite products for each location.
-   **`store`**: ObjectId, Ref: `Store` - *Required, Indexed*
-   **`location`**: ObjectId, Ref: `Location` - *Required, Indexed*
-   **`product`**: ObjectId, Ref: `Product` - *Required, Indexed*
-   **`variationId`**: ObjectId, Ref: `Product.variations` - *Optional* (Used when a specific product variation is favourited).
-   **`addedBy`**: ObjectId, Ref: `User` - *Required* (Tracks which user added the item).
-   **`createdAt`**: Date
**Indexes:**
-   A compound index on `{ store: 1, location: 1 }` for fast retrieval of a location's list.
-   A unique compound index on `{ store: 1, location: 1, product: 1, variation: 1 }` to prevent the exact same item from being added as a favourite to the same location more than once.
# API Endpoints
All new endpoints will be added to the product module (`product.route.ts`) and will require authentication. They will operate based on the `x-store-id` and `x-location-id` headers.
## 1. GET `/products/favourites`
-   **Description:** Fetches the shared list of favourite products for the specified store and location.
-   **Response:** An array of up to 13 items.
## 2. POST `/products/:productId/favourite`
-   **Description:** Adds a product (or a specific variation) to the shared favourites list for the current location.
-   **Params:** `productId` (the ID of the product to favourite).
-   **Body (optional):** `{ "variationId": "..." }`
-   **Logic:**
    -   Checks the count of existing favourites for the current **store and location**. If the count is 13 or more, it returns an error.
    -   Validates that the product exists.
    -   Creates a new `FavouriteProduct` record, setting the `addedBy` field to the current user's ID.
## 3. DELETE `/products/:productId/favourite`
-   **Description:** Removes a product (or a specific variation) from the shared favourites list for the current location.
-   **Params:** `productId` (the ID of the product to remove).
-   **Body (optional):** `{ "variationId": "..." }`
-   **Logic:** Finds and deletes the corresponding `FavouriteProduct` record based on the `store`, `location`, `product`, and optional `variation`. 
## 4. GET `/products/most-sold`
-   **Description:** Fetches a system-generated list of the top **14** best-selling products for the specified store and location over the last **30 days**.
-   **Response:** An array of up to 14 product objects, each including the full product details and the total quantity sold.
# Detailed Implementation
## Most Sold Products: Aggregation & Caching Strategy
This feature will be powered by an on-demand MongoDB aggregation pipeline on the `orders` collection.
1.  **Cache Check:**
    -   When `GET /products/most-sold` is called, the system will first check Redis for a result using the key `most-sold:<store_id>:<location_id>`.
    -   If a cached result is found, it is returned immediately.
2.  **Aggregation Pipeline (if cache miss):**
    -   **`$match`**: Filter for orders within the last **30 days** for the specific `store` and `location`. Exclude orders with a `status` of `cancelled`.
    -   **`$unwind`**: Deconstruct the `productsForSell.products` array to create a separate document for each item sold.
    -   **`$group`**: Group documents by `productId` and `variationId`. Use `$sum` to calculate the `totalSold` quantity for each unique item.
    -   **`$sort`**: Order the results by `totalSold` in descending order.
    -   **`$limit`**: Keep only the top **14** results.
    -   **`$lookup`**: Join with the `products` collection to fetch the full details for each top-selling product.
    -   **`$project`**: Format the final response to include the product details, the `totalSold` count, and the `variationId` if applicable.
3.  **Cache Set:**
    -   After the aggregation completes, the result is stored in Redis with a **12-hour Time-To-Live (TTL)**, ensuring the query runs at most twice per day for any given location.
# Frontend Integration
-   The order creation UI will display two tabs: "Favourites" and "Most Sold".
-   The "Favourites" tab will call `GET /products/favourites` to populate its list. It will need UI controls (e.g., an "Add Favourite" button in the product search and a "Remove" button on the list items) that call the corresponding `POST` and `DELETE` endpoints.
-   Simultaneously, the "Most Sold" tab will call `GET /products/most-sold`.