We should swap title & handle in the CSV. While the title is not different, we can assume it is the same product. Each line till the title changes is a new variant.
Example:
![[Pasted image 20241121113242.png]]

In the image above, 'Example T-shirt' has three variants. The first item is a variant, then the next two are other variants.
At row A5, the title changes, indicating a new product. Each line should be packed into a `ShopifyExportLine` object, containing each header in the csv.

## Categories
To parse categories, we should probably have some in-memory store of categories so we can easily query a category title and get its id. The id will be attached to the product. 
The question is how do we import Shopify's categories?

For parsing categories, we simply split it by the `>` character. This will give an array of strings, each string is a category. The category after a category is a subcategory (e,g in Apparel & Accessories > Clothing, Clothing is a subcategory).
## Options and Metafields
For options, this is simple enough. We will create an attributes JSON object for each product variant, built from each option and option value.
However, metafields are also supported. Metafield headers are in this format: `Brand (product.metafields.my_fields.brand)`. We can use them to build the attributes object too.
If a header contains `metafields`, then we get the metafield name. If it has a value

However, this means we can't have a `ShopifyExportLine` object, because the number of headers is never known.

## Prompt
i am trying to import data from shopify into my system. I attached my data model. product variant attributes are stored as json. I am using typescript & express

Here's my process.

1. Identifying a product and a variant.

I will swap the title and handle columns when processing the csv.

When I encounter a new title, I will start to build a product entity. For each line where the title does not change, I will build a new product variant related to that product.

The first line I encounter a title is also a variant. example, in the csv, line 1 (after the headers) with 'Example T-Shirt' as title is a product & variant

2. For attributes, the csv has Option1 Name, Option1 Value & so on. I will create a json object for each set of name & value. like where Option1 Name is brand, and value is Samsung, i create:

```json

{

"brand": "samsung"

}

```

However, there's also an unknown amount of 'metafields'. That is the headers in this format:

`Brand (product.metafields.my_fields.brand)`. I want to use metafields to build the attribute json too.

If a metafield header exists, and has a value, we add it to attributes.

e.g. if we have Color (product.metafields.my_fields.color) = 'red', our json will now be:

```json

{

"brand": "samsung"

}

```

when a new title is reached, the previous product and product variants will be saved in a db transaction, while we move to the next. what do you think of this approach?