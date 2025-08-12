# What's Happening 
users edit their store name, hit save, but when they refresh the page it goes back to the old name. 
# The Problem
![[Pasted image 20250807111800.png]]
Stores have locations. Stores have settings & locations **also** have settings. The UI doesn't make that clear. Note in the top left, it says 'Modify store settings for this location'. When a setting exists for both sections, the location settings override the store settings.

On this page, when the request is sent to update the store name:
1. it saves the **settings** to both the store AND the location 
2. but we have these database hooks - a hook is a piece of  code that runs every time we fetch or update some data - that automatically override the store data with location data every time we fetch or update.
3. so the store name gets immediately overwritten by the location name
4. user sees their change disappeared

basically our data flow is: `user saves → store gets updated → database hooks override with location data → user sees old name`

the hooks are in `store.model.ts` around line 308+:
```ts
store.name = location.name;  // this is the problem line
```
# The Fix
instead of trying to make this single confusing interface work, let's just split it into two clear sections:
**Store Details** (affects your whole business)
- store name 
- phone
- email  
- address
- settings
**Location Settings** (affects just this location & overrides store settings)
- currency
- language
- tax settings
- discount settings

We can add the location name, phone, email & address here too.
# What Each Team Needs To Do
## Backend
- **remove the mongoose hooks entirely** - they're the root cause
- **create two separate endpoints:**
  - `PATCH /stores/:id/ for store-level stuff
  - `PATCH /locations/:locationId/` for location stuff (uses store header to identify store it belongs to)
- **update the GET response** to clearly separate store vs location data
## Frontend  
- **split the current form into two sections** with clear headers
- **use the new separate API endpoints** 
- **add some visual indicators** so users know what affects what scope
## Design
- **make two distinct sections** on the page 
- **add clear labels** like "Store Information (applies to all locations)" and "Location Settings (this location only)"
- **maybe some icons** to make the difference obvious
# Why This Approach
- **fixes the actual bug** - no more data overriding
- **makes it clear to users** what they're changing  
- **works for single location stores** (most of our users) and multi-location ones
- **cleaner code** - no more confusing hooks
# Next Steps
1. backend removes the hooks and creates new endpoints
2. design creates mockups for the split interface  
3. frontend implements the new form structure
4. we test

should be a pretty straightforward fix once we stop trying to make one interface do two things.
# Some Concerns (Backend) 
- With the way the relationship between store & locations is modelled, I am concerned about what happens when a location is updated. We will have to update the related location entry on the store document.
# Notes From Babz
- That page ought to update the *store* & not the location.
- Think of a store as a company, and the locations as branches of that company. 
- Alex wants us to keep 
- Store Based Settings - only on store
	- Business Details
	- App Auto Lock
- Location Based Settings - exist on location only 
	- Language
	- Currency
	- Order Settings
	- Default Order Fulfilment Status