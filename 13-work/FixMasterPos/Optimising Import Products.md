# Requirements
- Users see a progress bar they can use to monitor imports
- Users see a summary after the import is complete
# Implementation
I want to borrow from Shopify's implementation. On Shopify, when there are < 50 products being imported, a progress modal is shown. Users can watch the import process in real-time, and they will see a summary when it completes.

When they import > 50 products, the job is queued and the user will _not_ be able to watch the progress in real time. This is to save resources, as the import will take much longer to complete. When the import process is complete, users receive an email summarising the procedure.
!!![[../../assets/optimising-import-products-1.png]]

# Plan
### For < 50 products (live processing with progress)
- Implement websockets progress bar for real-time updates
- Implement summary modal when complete
- Implement optimisations:
	- Pre-fetch and store vendor, categories and locations in maps, instead of making multiple db queries. Use the maps for lookups & add newly created values back to the maps.
		- done. Took 6 mins to process
    - Use bulk operations to write/update data
### For > 50 products (background processing)
- Implement background handler using agenda jobs
- Implement batching for processing. Batches of 50 should suffice, right?
- Implement email notifications with import summary