# Category Path Issues
After importing a product, DUNSIN tried to edit it. She opened the category section on the edit product page, and attempted to delete a category. The category was successfully deleted, so was every other imported category.
## Problem
In `importProducts.ts`, we create a new category like so:
```ts
const category = {
    title,
    slug: `fix-${slugify(title)}`,
    store: new Types.ObjectId(storeId),
    location: new Types.ObjectId(locationId),
    createdBy: new Types.ObjectId(userId),
    path: '/',
    isActive: true,
  };
```
In the `destroy()` method of `category.controller.ts`, we have this:
```ts
const category: any = await Categories.findOneAndDelete({ _id: id, store });

  if (!category) {
    return reply
      .code(400)
      .send(ApiResponse.error("Default categories can't be deleted."));
  }

  //! 1. parent / delete all sub category and make an array of sub-categories id
  //? delete all repair product, matched category id included in arrar
  if (category?.parent && category?.parent === "/") {
    const categoriesIds = await Categories.find({
      parent: category?.path,
      store,
    })
      .select("_id")
      .lean();
    const transformedArray = categoriesIds.map((obj: any) => obj._id);

    await Categories.deleteMany({ _id: { $in: transformedArray } });
    await RepairProducts.deleteMany({
      category: { $in: transformedArray },
      store,
    });
  }
  //! 2. parent !/ delete all repair product, matched category id
  else if (category?.parent && category?.parent !== "/") {
    await RepairProducts.deleteMany({
      category: category?._id,
      store,
    });
  }
```

To avoid orphaned records, it finds categories in the store whose `parent` matches the selected categories `path`. Above you will see all imported categories have `/` as `path`, and the `parent` field defaults to `/`.
## Solution
1. In `importProducts.ts`, we will set the `path` to the slugified category title.
2. Add an `isImported` field to the category model.
3. We will run a migration to update the path for imported products. Here's how it'll work:
	-  Default categories have no `store` field, so we only search for categories where store exists and is not null
	- The problematic categories have `store`, and their `path` and `parent` are `/`.
	- We will filter on a store by store basis, where `store` = the store's id and `category.path` & `category.parent` = `/` . 
4. Run a migration on all categories. Where `store`  does not exist, set `isImported` to false.

```ts
export async function fixAllImportedCategories() {
  console.log("Starting simple migration to fix all imported categories...");

  // Find ALL problematic categories across all stores
  // These are definitely imported categories based on your criteria:
  // - Have store field (not default categories)
  // - Have path="/" and parent="/" (not properly created categories)
  // - Title is not "/" (not an actual root category)
  const problematicCategories = await Categories.find({
    store: { $exists: true, $ne: null },
    path: "/",
    parent: "/",
    title: { $ne: "/" }
  });

  console.log(`Found ${problematicCategories.length} problematic categories total`);

  const bulkOps = [];

  for (const category of problematicCategories) {
    const correctPath = `/${slugify(category.title)}`;
    
    bulkOps.push({
      updateOne: {
        filter: { _id: category._id },
        update: {
          $set: {
            path: correctPath,
            isImported: true
          }
        }
      }
    });

    console.log(`Will fix: Store ${category.store}, "${category.title}" -> path: "${correctPath}"`);
  }

  if (bulkOps.length > 0) {
    const result = await Categories.bulkWrite(bulkOps);
    console.log(`Fixed ${result.modifiedCount} categories total`);
    return result.modifiedCount;
  }

  console.log("No categories needed fixing");
  return 0;
}
```

The migration endpoints exist on `chore/fix-categories`.