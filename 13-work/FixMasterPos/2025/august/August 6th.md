Oladipo keeps tagging me to fix shit and my brain is now fried. I have to look into these after I have taken a break

- Alex reported not being able to rename his store.
	- On investigation, I figured out the update is being applied to the document.
	- However, there is a hook on the store model that sets the name of the store to the name of the default location. In essence, the hook always overwrites the users changes.
	- In the db, `store.name` changes to the provided value, but the user will always see the old change.
![[Pasted image 20250806151814.png]]
- The PR to add `isTaxable` to orders was merged, yet Oladipo claims his order was missing the `isTaxable`  field. I need to create a new order and see what is up.
- Product search is not working as expected - whatever that fucking means.
# Bug With Updating Store Name
In the first image, you can see the screen to update the 'store details'. But if you look in the top left corner, under the **Store Settings** header, it says 'Modify store settings for this location'. I think this is the first problem, as the design likely informed the API design.
![[Pasted image 20250807100126.png]]
On the backend, there is a piece of code that runs when a user fetches, or updates a store. There are two levels of settings:
- Store settings
- Location settings

When the request is sent, these settings are updated for both the store and current location:
- currency
- language
- sales
- tax
- cardProcessingFee
- orderSuffix
- timezone
- dateFormat
- timeFormat
- numberFormat
- discount
- autoLock

These items are updated for only the store:
- address
- name
- phone
- email

The issue is this piece of code that runs when fetching or updating a store, which was likely informed by the design of this page.
When a store is fetched, it sets the store details, using the locations details:
```ts
store.name = location.name;
store.phone = location.phone;
store.email = location.email || store.email;
store.legalName = location.legalName || store.legalName;
store.address = location.address || store.address;
store.settings = location.settings || store.settings;
store.receipt = location.receipt || store.receipt;
store.currency = location.currency || store.currency;
store.language = location.language || store.language;
store.orderFulfilmentStatus = location.orderFulfilmentStatus || store.orderFulfilmentStatus
```

I think this was done to show users they are updating 'the location' or something. regardless, it is the cause of this bug. I think a fix would need both a mild page redesign to show what settings are being changed at what level, changing some text & a mild API change to accept & return the data in a way that makes sense (and also removing the hooks)