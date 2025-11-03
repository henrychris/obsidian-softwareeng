This document outlines the API endpoints for managing a venue's photo gallery.
# Base URL
`/api/venue-manager/my-venue/{venueId}/photos`
# Authentication
All endpoints that modify data (`POST`, `PUT`, `DELETE`) require the user to be authenticated and to be the manager of the specified venue.

---
# Data Models

## `VenuePhoto` Object
This is the main resource representation for a photo in the gallery.
```json
{
  "id": "101",
  "url": "https://res.cloudinary.com/your-cloud/image/upload/v12345/venue-photos/venue-1/abcdef.jpg",
  "caption": "Main field during a sunny afternoon.",
  "isCoverPhoto": true,
  "displayOrder": 1,
  "dateCreated": "2025-09-16T10:00:00Z"
}
```

---

# Endpoints
## 1. List Venue Photos
Retrieves an ordered list of all photos for a specific venue.
*   **Endpoint:** `GET /api/venue-manager/my-venue/{venueId}/photos`
*   **Permissions:** Public
**Success Response (200 OK)**
```json
{
  "success": true,
  "message": "Venue photos retrieved successfully.",
  "note": null,
  "data": [
    {
      "id": "101",
      "url": "https://res.cloudinary.com/your-cloud/image/upload/v12345/venue-photos/venue-1/abcdef.jpg",
      "caption": "Main field during a sunny afternoon.",
      "isCoverPhoto": true,
      "displayOrder": 1,
      "dateCreated": "2025-09-16T10:00:00Z"
    },
    {
      "id": "102",
      "url": "https://res.cloudinary.com/your-cloud/image/upload/v12345/venue-photos/venue-1/ghijk.jpg",
      "caption": "Entrance and parking area.",
      "isCoverPhoto": false,
      "displayOrder": 2,
      "dateCreated": "2025-09-16T10:05:00Z"
    }
  ]
}
```
**Error Response (404 Not Found)**
If the `{venueId}` does not exist.
```json
{
  "success": false,
  "message": "The requested resource was not found.",
  "errors": [
    {
      "code": "Venue.NotFound",
      "description": "A venue with the specified ID was not found."
    }
  ]
}
```

---
## 2. Upload a New Photo
Adds a new photo to a venue's gallery. The request body must be `multipart/form-data`.
*   **Endpoint:** `POST /api/venue-manager/my-venue/{venueId}/photos`
*   **Permissions:** Venue Manager
**Request Body (`multipart/form-data`)**

| Field          | Type    | Required | Description                                                                                                |
| :------------- | :------ | :------- | :--------------------------------------------------------------------------------------------------------- |
| `photo`        | File    | Yes      | The image file to upload.                                                                                  |
| `caption`      | String  | No       | A brief description or caption for the photo.                                                              |
| `isCoverPhoto` | Boolean | No       | If `true`, this photo will become the new cover photo, and the old one will be unset. Defaults to `false`. |

**Success Response (201 Created)**
Returns the newly created `VenuePhoto` object.
```json
{
  "success": true,
  "message": "Photo uploaded successfully.",
  "note": null,
  "data": {
    "id": 103,
    "url": "https://res.cloudinary.com/your-cloud/image/upload/v12345/venue-photos/venue-1/lmnopq.jpg",
    "caption": "Our brand new indoor court.",
    "isCoverPhoto": false,
    "displayOrder": 3,
    "dateCreated": "2025-09-16T11:00:00Z"
  }
}
```
**Error Response (400 Bad Request)**
If the file is missing or invalid.
```json
{
  "success": false,
  "message": "The request could not be processed due to invalid input.",
  "errors": [
    {
      "code": "Photo.Required",
      "description": "A photo file must be provided."
    }
  ]
}
```

---
## 3. Update Photo Details
Updates the details of a specific photo, such as its caption.
*   **Endpoint:** `PUT /api/venue-manager/my-venue/{venueId}/photos/{photoId}`
*   **Permissions:** Venue Manager
**Request Body (`application/json`)**
```json
{
  "caption": "An updated caption for the photo."
}
```
**Success Response (200 OK)**
Returns the updated `VenuePhoto` object.
```json
{
  "success": true,
  "message": "Photo details updated successfully.",
  "note": null,
  "data": {
    "id": 102,
    "url": "https://res.cloudinary.com/your-cloud/image/upload/v12345/venue-photos/venue-1/ghijk.jpg",
    "caption": "An updated caption for the photo.",
    "isCoverPhoto": false,
    "displayOrder": 2,
    "dateCreated": "2025-09-16T10:05:00Z"
  }
}
```

---
## 4. Set as Cover Photo
A dedicated endpoint to mark a specific photo as the venue's primary cover photo.
*   **Endpoint:** `POST /api/venue-manager/my-venue/{venueId}/photos/{photoId}/set-cover`
*   **Permissions:** Venue Manager
*   **Request Body:** Empty
**Success Response (204 No Content)**
An empty response body with a 204 status code indicates success.

---
## 5. Reorder Photos
Updates the `displayOrder` for multiple photos in a single request. This is efficient for drag-and-drop gallery reordering on the frontend.
*   **Endpoint:** `PUT /api/venue-manager/my-venue/{venueId}/photos/reorder`
*   **Permissions:** Venue Manager
**Request Body (`application/json`)**
The body should contain an array of objects, each with a `photoId` and its new `displayOrder`.
```json
[
  { "photoId": 101, "displayOrder": 2 },
  { "photoId": 102, "displayOrder": 1 },
  { "photoId": 103, "displayOrder": 3 }
]
```
**Success Response (204 No Content)**
An empty response body with a 204 status code indicates success.

---
## 6. Delete a Photo
Permanently removes a photo from the gallery and from the underlying storage (Cloudinary).
*   **Endpoint:** `DELETE /api/venue-manager/my-venue/{venueId}/photos/{photoId}`
*   **Permissions:** Venue Manager
**Success Response (204 No Content)**
An empty response body with a 204 status code indicates the photo was successfully deleted.
**Error Response (404 Not Found)**
If the `{photoId}` does not exist for the given venue.
```json
{
  "success": false,
  "message": "The requested resource was not found.",
  "errors": [
    {
      "code": "VenuePhoto.NotFound",
      "description": "A photo with the specified ID was not found for this venue."
    }
  ]
}
```

next steps
- run migration endpoint on each environment
- after migration on prod, remove venue.PhotoUrl and venue.AdditionalPhotoUrls