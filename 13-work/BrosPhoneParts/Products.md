# Inventory
After fetching products, we need to return each variant as a separate item. To do this, we will map out variants.

Product Database Design Overview (WIP): 
### Collection
* Title
* Desc
* Type (Manual)
* Image
* Products []
* MetaField
### Category
Categories are broader classifications to organize products.
* Title
* Products []
### Product
* TitleDesc
* Media (Multi)
* CategoryId
* collectionId
* Status
* InventoryId
* Variants []: 
* ProductTags []
* ProductType?
* Vendor?
* Pricing
    * Price
    * Compare-at-price
    * InventoryId
### Inventory
* productId
* Unavailable
* Committed
* On Hand
* Incoming
* SKU:( Unique identifier for stock-keeping, often used to generate barcodes.)

### Variant
* productId
* Name
* Vales []: Array of variant type (e.g., "Color: Red, Yellow, Blue” ).

### MetaData ?
- Attribute
    * Name
    * Values []

- ProductAttribute.
    * ProductId (Many-to-many relationship with products) 
    * AttributeId (Many-to-many relationship with attributes) 
    * Value
### ProductShippingInfo
* ProductId
* Weight
* Dimensions
* ShippingClass
### ProductTag
* ProductId
* Tag