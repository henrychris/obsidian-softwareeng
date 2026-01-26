### 1. New Model: `favouriteProduct.model.ts`

First, create the new Mongoose model to store the location-specific, shared favourite products.

**Create a new file: `src/modules/product/models/favouriteProduct.model.ts`**
```typescript
import { model, Schema, Types } from "mongoose";
import { ProductDocument } from "../../../types/products/products.types";
import { UserDocument } from "../../../types/user/user.types";

export interface FavouriteProductClass {
  _id: Types.ObjectId;
  store: Types.ObjectId;
  location: Types.ObjectId;
  product: Types.ObjectId | ProductDocument;
  variationId?: Types.ObjectId;
  addedBy: Types.ObjectId | UserDocument;
  createdAt: Date;
}

const favouriteProductSchema = new Schema<FavouriteProductClass>(
  {
    store: { type: Schema.Types.ObjectId, ref: "Store", required: true },
    location: { type: Schema.Types.ObjectId, ref: "Location", required: true },
    product: { type: Schema.Types.ObjectId, ref: "Product", required: true },
    variationId: { type: Schema.Types.ObjectId },
    addedBy: { type: Schema.Types.ObjectId, ref: "User", required: true },
  },
  { timestamps: true },
);

// Index for quickly fetching a location's favourites list
favouriteProductSchema.index({ store: 1, location: 1 });

// Unique index to prevent duplicates at the same location
favouriteProductSchema.index(
  { store: 1, location: 1, product: 1, variationId: 1 },
  { unique: true },
);

export const FavouriteProduct = model<FavouriteProductClass>(
  "FavouriteProduct",
  favouriteProductSchema,
);
```

### 2. API Routes & Schema: `product.route.ts` & `product.schema.ts`

Register the new API endpoints and add the necessary Zod schema for validation.

**Update file: `src/modules/product/product.schema.ts`**
```typescript
// ... other imports
import { z } from "zod";

// ... other schemas

// Add this new schema for the favourite product endpoints
export const FavouriteProductSchema = {
  params: z.object({
    productId: z.string().refine((val) => /^[0-9a-fA-F]{24}$/.test(val), {
      message: "Invalid product ID",
    }),
  }),
  body: z.object({
    variationId: z.string().optional(),
  }),
};
```

**Update file: `src/modules/product/product.route.ts`**
```typescript
// ... existing imports
import {
  // ... existing controller functions
  addFavouriteProduct,
  removeFavouriteProduct,
  listFavouriteProducts,
  listMostSoldProducts,
} from "./product.contoller";
import * as ProductSchema from "./product.schema";

export async function productRoute(app: FastifyInstance) {
  // ... existing code ...

  app.withTypeProvider<ZodTypeProvider>().delete(
    "/products/remove",
    {
      preHandler: checkLogin,
      schema: ProductSchema.MultiProductDeleteSchema,
    },
    deleteMultipleProducts,
  );

  // START: Add New Favourite and Most Sold Routes
  app.get(
    "/products/favourites",
    { preHandler: checkLogin },
    listFavouriteProducts,
  );

  app.post(
    "/products/:productId/favourite",
    { schema: ProductSchema.FavouriteProductSchema, preHandler: checkLogin },
    addFavouriteProduct,
  );

  app.delete(
    "/products/:productId/favourite",
    { schema: ProductSchema.FavouriteProductSchema, preHandler: checkLogin },
    removeFavouriteProduct,
  );

  app.get(
    "/products/most-sold",
    { preHandler: checkLogin },
    listMostSoldProducts,
  );
  // END: Add New Favourite and Most Sold Routes

  app.register(fastifyMaltipart);
}
```

### 3. Controller Logic: `product.controller.ts`

This is the core implementation, including the mappers and the main controller functions.

**Update file: `src/modules/product/product.contoller.ts`**

```typescript
// Add these new imports at the top of the file
import { Types } from "mongoose";
import { ProductType } from "../../config/constant/productType";
import { redisClient } from "../../core/redis";
import { AttachableFile } from "../../types/file/file.types";
import { Order } from "../order/models/orders.model";
import { FavouriteProduct, FavouriteProductClass } from "./models/favouriteProduct.model";
import { ProductDocument } from "../../types/products/products.types";

// Define constants for the new features
const MAX_FAVOURITES_PER_LOCATION = 13;
const MAX_MOST_SOLD_PRODUCTS = 14;
const MOST_SOLD_DATE_RANGE_DAYS = 30;
const MOST_SOLD_CACHE_TTL_SECONDS = 43200; // 12 hours

// --- START: Response Shapes and Mappers ---

// Response shape for Favourite Products
export interface FavouriteProductResponse {
  id: string;
  title: string;
  imageUrl?: string | null;
  product: ProductDocument;
  variationId?: string;
  quantity: number;
}

// Response shape for Most Sold Products
export interface MostSoldProductResponse {
  title: string;
  imageUrl?: string | null;
  product: ProductDocument;
  variationId?: string;
  quantity: number;
  totalSold: number;
}

// Type alias for a populated favourite product from the database
type PopulatedFavouriteProduct = Omit<FavouriteProductClass, "product"> & {
  product: ProductDocument;
};

/**
 * Maps a populated FavouriteProduct from the DB to the API response shape.
 */
function mapFavouriteToResponse(
  fav: PopulatedFavouriteProduct,
  locationId: string,
): FavouriteProductResponse | null {
  if (!fav.product) return null;

  const product = fav.product;
  let displayTitle = product.title;
  let displayImage: string | null =
    product.images && product.images.length > 0 ? product.images[0].url : null;
  let stock = 0;
  const variationIdStr = fav.variationId?.toString();

  if (variationIdStr && product.type === ProductType.VARIABLE && product.variations) {
    const variation = product.variations.find((v) => v._id.toString() === variationIdStr);
    if (variation) {
      displayTitle = `${product.title} - ${variation.title}`;
      displayImage = variation.image?.url || displayImage;
      const inv = variation.inventory?.find((i) => i.locationId.toString() === locationId);
      stock = inv?.quantity || 0;
    }
  } else {
    const inv = product.inventory?.find((i) => i.locationId.toString() === locationId);
    stock = inv?.quantity || 0;
  }

  return {
    id: fav._id.toString(),
    title: displayTitle,
    imageUrl: displayImage,
    product: product,
    variationId: variationIdStr,
    quantity: stock,
  };
}

// Type alias for an item from the Most Sold aggregation pipeline
type AggregatedMostSoldProduct = {
  product: ProductDocument;
  totalSold: number;
  variationId?: Types.ObjectId;
};

/**
 * Maps an aggregated Most Sold Product to the API response shape.
 */
function mapMostSoldToResponse(
  item: AggregatedMostSoldProduct,
  locationId: string,
): MostSoldProductResponse {
  const product = item.product;
  let displayTitle = product.title;
  let displayImage: string | null =
    product.images && product.images.length > 0 ? product.images[0].url : null;
  let stock = 0;
  const variationIdStr = item.variationId?.toString();

  if (variationIdStr && product.type === ProductType.VARIABLE && product.variations) {
    const variation = product.variations.find((v) => v._id.toString() === variationIdStr);
    if (variation) {
      displayTitle = `${product.title} - ${variation.title}`;
      displayImage = variation.image?.url || displayImage;
      const inv = variation.inventory?.find((i) => i.locationId.toString() === locationId);
      stock = inv?.quantity || 0;
    }
  } else {
    const inv = product.inventory?.find((i) => i.locationId.toString() === locationId);
    stock = inv?.quantity || 0;
  }

  return {
    title: displayTitle,
    imageUrl: displayImage,
    product: product,
    variationId: variationIdStr,
    quantity: stock,
    totalSold: item.totalSold,
  };
}
// --- END: Response Shapes and Mappers ---


// ... existing controller functions (createProduct, index, show, etc.)


// START: Add the four new controller functions at the end of the file

export async function addFavouriteProduct(
  request: FastifyRequest<{
    Params: { productId: string };
    Body: { variationId?: string };
  }>,
  reply: FastifyReply,
) {
  const { productId } = request.params;
  const { variationId } = request.body;
  const user = request.user;
  const store = await user.getCurrentStore(request, reply);
  const location = request.headers["x-location-id"]?.toString();

  if (!location) {
    return reply.code(400).send(ApiResponse.error("Location is required."));
  }

  const favouriteCount = await FavouriteProduct.countDocuments({ store, location });
  if (favouriteCount >= MAX_FAVOURITES_PER_LOCATION) {
    return reply.code(400).send(ApiResponse.error(`The favourite products limit of ${MAX_FAVOURITES_PER_LOCATION} has been reached for this location.`));
  }

  const productExists = await Product.exists({ _id: productId, store });
  if (!productExists) {
    return reply.code(404).send(ApiResponse.error("Product not found."));
  }

  try {
    const favourite = await FavouriteProduct.create({
      store,
      location,
      product: productId,
      variationId: variationId,
      addedBy: user._id,
    });
    return reply.code(201).send(ApiResponse.success("Product added to favourites.", favourite));
  } catch (error: any) {
    if (error.code === 11000) {
      return reply.code(409).send(ApiResponse.error("This product is already a favourite at this location."));
    }
    logger.error(error, "Failed to add favourite product");
    return reply.code(500).send(ApiResponse.error("An unexpected error occurred."));
  }
}

export async function removeFavouriteProduct(
  request: FastifyRequest<{
    Params: { productId: string };
    Body: { variationId?: string };
  }>,
  reply: FastifyReply,
) {
  const { productId } = request.params;
  const { variationId } = request.body;
  const user = request.user;
  const store = await user.getCurrentStore(request, reply);
  const location = request.headers["x-location-id"]?.toString();
  
  if (!location) {
    return reply.code(400).send(ApiResponse.error("Location is required."));
  }

  const result = await FavouriteProduct.deleteOne({
    store,
    location,
    product: productId,
    variationId: variationId,
  });

  if (result.deletedCount === 0) {
    return reply.code(404).send(ApiResponse.error("Favourite product not found at this location."));
  }

  return reply.code(200).send(ApiResponse.success("Product removed from favourites."));
}

export async function listFavouriteProducts(
  request: FastifyRequest,
  reply: FastifyReply,
) {
  const user = request.user;
  const store = await user.getCurrentStore(request, reply);
  const location = request.headers["x-location-id"]?.toString();
  
  if (!location) {
    return reply.code(400).send(ApiResponse.error("Location is required."));
  }

  const favourites = await FavouriteProduct.find({ store, location })
    .populate<{ product: ProductDocument }>({ path: 'product' })
    .limit(MAX_FAVOURITES_PER_LOCATION)
    .sort({ createdAt: 1 }) // sort by oldest first
    .lean();

  const responseData = favourites
    .map(fav => mapFavouriteToResponse(fav as PopulatedFavouriteProduct, location))
    .filter((p): p is FavouriteProductResponse => p !== null);

  return reply.code(200).send(ApiResponse.success("Favourite products fetched successfully.", responseData));
}

export async function listMostSoldProducts(
  request: FastifyRequest,
  reply: FastifyReply,
) {
  const user = request.user;
  const store = await user.getCurrentStore(request, reply);
  const location = request.headers["x-location-id"]?.toString();

  if (!location) {
    return reply.code(400).send(ApiResponse.error("Location is required."));
  }

  const cacheKey = `most-sold:${store}:${location}`;

  try {
    const cachedData = await redisClient.get(cacheKey);
    if (cachedData) {
      return reply.code(200).send(ApiResponse.success("Most sold products fetched successfully from cache.", JSON.parse(cachedData)));
    }
  } catch (redisError) {
    logger.error(redisError, "Cache get error for most sold products");
  }

  const thirtyDaysAgo = new Date();
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - MOST_SOLD_DATE_RANGE_DAYS);

  const pipeline: PipelineStage[] = [
    { $match: { store: new Types.ObjectId(store), location: new Types.ObjectId(location), status: { $ne: "cancelled" }, createdAt: { $gte: thirtyDaysAgo } } },
    { $unwind: "$productsForSell.products" },
    { $group: { _id: { productId: "$productsForSell.products.id", variationId: "$productsForSell.products.variation.id" }, totalSold: { $sum: "$productsForSell.products.quantity" } } },
    { $sort: { totalSold: -1 } },
    { $limit: MAX_MOST_SOLD_PRODUCTS },
    { $lookup: { from: "products", localField: "_id.productId", foreignField: "_id", as: "productDetails" } },
    { $unwind: "$productDetails" },
    { $project: { _id: 0, product: "$productDetails", totalSold: 1, variationId: "$_id.variationId" } }
  ];

  const mostSoldProducts = await Order.aggregate(pipeline);

  const responseData = mostSoldProducts.map(item => mapMostSoldToResponse(item as AggregatedMostSoldProduct, location));

  try {
    await redisClient.set(cacheKey, JSON.stringify(responseData), "EX", MOST_SOLD_CACHE_TTL_SECONDS);
  } catch (cacheError) {
    logger.error(cacheError, "Cache set error for most sold products");
  }

  reply.code(200).send(ApiResponse.success("Most sold products fetched successfully.", responseData));
}

// END: New controller functions
```