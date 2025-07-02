Search Products
```ts
import { prisma } from '../../lib/prisma';
import { ServiceResponse } from '../../common/serviceResponse';

export interface SearchProductsDto {
  query: string;
  page?: number;
  limit?: number;
}

export async function searchProductsAsync(payload: SearchProductsDto) {
  const { query, page = 1, limit = 10 } = payload;
  const skip = (page - 1) * limit;

  try {
    const [products, total] = await prisma.$transaction([
      prisma.product.findMany({
        where: {
          OR: [
            { title: { contains: query, mode: 'insensitive' } },
            { description: { contains: query, mode: 'insensitive' } },
            { sku: { contains: query, mode: 'insensitive' } },
          ],
        },
        include: {
          category: {
            select: {
              id: true,
              title: true,
            },
          },
        },
        skip,
        take: limit,
      }),
      prisma.product.count({
        where: {
          OR: [
            { title: { contains: query, mode: 'insensitive' } },
            { description: { contains: query, mode: 'insensitive' } },
            { sku: { contains: query, mode: 'insensitive' } },
          ],
        },
      }),
    ]);

    return ServiceResponse.ok('Products retrieved successfully', {
      products,
      pagination: {
        total,
        page,
        limit,
        pages: Math.ceil(total / limit),
      },
    });
  } catch (error) {
    return ServiceResponse.serverError();
  }
}
```

getSearchFilters
```ts
import { prisma } from '../../lib/prisma';
import { ServiceResponse } from '../../common/serviceResponse';

interface FilterValue {
  value: string;
  count: number;
}

interface Filter {
  name: string;
  values: FilterValue[];
}

export interface GetSearchFiltersDto {
  query: string;
}

export async function getSearchFiltersAsync(payload: GetSearchFiltersDto) {
  const { query } = payload;

  try {
    // Get matching products
    const products = await prisma.product.findMany({
      where: {
        OR: [
          { title: { contains: query, mode: 'insensitive' } },
          { description: { contains: query, mode: 'insensitive' } },
          { sku: { contains: query, mode: 'insensitive' } },
        ],
      },
      select: {
        attributes: true,
        category: {
          select: {
            id: true,
            title: true,
          },
        },
      },
    });

    // Initialize filters
    const filterMap = new Map<string, Map<string, number>>();
    const categoryMap = new Map<number, { title: string; count: number }>();

    // Process products
    products.forEach((product) => {
      // Process attributes
      const attributes = product.attributes as Record<string, string>;
      Object.entries(attributes).forEach(([key, value]) => {
        if (!filterMap.has(key)) {
          filterMap.set(key, new Map());
        }
        const valueMap = filterMap.get(key)!;
        valueMap.set(value, (valueMap.get(value) || 0) + 1);
      });

      // Process categories
      if (product.category) {
        const existing = categoryMap.get(product.category.id);
        categoryMap.set(product.category.id, {
          title: product.category.title,
          count: (existing?.count || 0) + 1,
        });
      }
    });

    // Convert maps to response format
    const filters: Filter[] = Array.from(filterMap.entries()).map(
      ([name, values]) => ({
        name,
        values: Array.from(values.entries()).map(([value, count]) => ({
          value,
          count,
        })),
      })
    );

    // Add categories as a filter
    const categoryFilter: Filter = {
      name: 'Category',
      values: Array.from(categoryMap.entries()).map(([_, data]) => ({
        value: data.title,
        count: data.count,
      })),
    };

    return ServiceResponse.ok('Filters retrieved successfully', {
      filters: [categoryFilter, ...filters],
    });
  } catch (error) {
    return ServiceResponse.serverError();
  }
}
```

controller
```ts
import { Request, Response } from 'express';
import { asyncHandler } from '../../common/util/asyncHandler';
import { handleServiceResponse } from '../../common/util/httpHandler';
import { searchProductsAsync } from './searchProductsRequest';
import { getSearchFiltersAsync } from './getSearchFiltersRequest';

export const searchProducts = asyncHandler(async (req: Request, res: Response) => {
  const { q: query, page, limit } = req.query;
  const resp = await searchProductsAsync({
    query: query as string,
    page: page ? parseInt(page as string) : undefined,
    limit: limit ? parseInt(limit as string) : undefined,
  });
  handleServiceResponse(resp, res);
});

export const getSearchFilters = asyncHandler(
  async (req: Request, res: Response) => {
    const { q: query } = req.query;
    const resp = await getSearchFiltersAsync({ query: query as string });
    handleServiceResponse(resp, res);
  }
);
```

Precompute
```ts
model PrecomputedFilter {
  id        Int      @id @default(autoincrement())
  type      String   // 'search' or 'category'
  queryHash String   // hash of the search query or categoryId
  filters   Json
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@unique([type, queryHash])
  @@index([updatedAt])
}
```

```ts
import { prisma } from '../../../lib/prisma';
import { createHash } from 'crypto';
import log from '../../../common/util/logger';

interface FilterValue {
  value: string;
  count: number;
}

interface Filter {
  name: string;
  values: FilterValue[];
}

export class FilterCacheService {
  private static CACHE_TTL = 60 * 60 * 1000; // 1 hour in milliseconds

  private static hashQuery(query: string): string {
    return createHash('md5').update(query.toLowerCase()).digest('hex');
  }

  static async getSearchFilters(query: string): Promise<Filter[] | null> {
    const queryHash = this.hashQuery(query);

    const cachedFilters = await prisma.precomputedFilter.findFirst({
      where: {
        type: 'search',
        queryHash,
        updatedAt: {
          gt: new Date(Date.now() - this.CACHE_TTL),
        },
      },
    });

    if (cachedFilters) {
      return cachedFilters.filters as Filter[];
    }

    return null;
  }

  static async computeAndCacheSearchFilters(query: string): Promise<Filter[]> {
    try {
      // Get matching products
      const products = await prisma.product.findMany({
        where: {
          OR: [
            { title: { contains: query, mode: 'insensitive' } },
            { description: { contains: query, mode: 'insensitive' } },
            { sku: { contains: query, mode: 'insensitive' } },
          ],
        },
        select: {
          attributes: true,
          category: {
            select: {
              id: true,
              title: true,
            },
          },
        },
      });

      const filters = await this.computeFilters(products);
      const queryHash = this.hashQuery(query);

      // Store in cache
      await prisma.precomputedFilter.upsert({
        where: {
          type_queryHash: {
            type: 'search',
            queryHash,
          },
        },
        create: {
          type: 'search',
          queryHash,
          filters,
        },
        update: {
          filters,
          updatedAt: new Date(),
        },
      });

      return filters;
    } catch (error) {
      log.error('Error computing filters:', error);
      throw error;
    }
  }

  static async getCategoryFilters(categoryId: number): Promise<Filter[] | null> {
    const queryHash = categoryId.toString();

    const cachedFilters = await prisma.precomputedFilter.findFirst({
      where: {
        type: 'category',
        queryHash,
        updatedAt: {
          gt: new Date(Date.now() - this.CACHE_TTL),
        },
      },
    });

    if (cachedFilters) {
      return cachedFilters.filters as Filter[];
    }

    return null;
  }

  static async computeAndCacheCategoryFilters(
    categoryId: number
  ): Promise<Filter[]> {
    try {
      const products = await prisma.product.findMany({
        where: {
          categoryId,
        },
        select: {
          attributes: true,
          category: {
            select: {
              id: true,
              title: true,
            },
          },
        },
      });

      const filters = await this.computeFilters(products);
      const queryHash = categoryId.toString();

      // Store in cache
      await prisma.precomputedFilter.upsert({
        where: {
          type_queryHash: {
            type: 'category',
            queryHash,
          },
        },
        create: {
          type: 'category',
          queryHash,
          filters,
        },
        update: {
          filters,
          updatedAt: new Date(),
        },
      });

      return filters;
    } catch (error) {
      log.error('Error computing category filters:', error);
      throw error;
    }
  }

  private static async computeFilters(
    products: Array<{
      attributes: any;
      category: { id: number; title: string } | null;
    }>
  ): Promise<Filter[]> {
    const filterMap = new Map<string, Map<string, number>>();
    const categoryMap = new Map<number, { title: string; count: number }>();

    products.forEach((product) => {
      // Process attributes
      const attributes = product.attributes as Record<string, string>;
      Object.entries(attributes).forEach(([key, value]) => {
        if (!filterMap.has(key)) {
          filterMap.set(key, new Map());
        }
        const valueMap = filterMap.get(key)!;
        valueMap.set(value, (valueMap.get(value) || 0) + 1);
      });

      // Process categories
      if (product.category) {
        const existing = categoryMap.get(product.category.id);
        categoryMap.set(product.category.id, {
          title: product.category.title,
          count: (existing?.count || 0) + 1,
        });
      }
    });

    // Convert maps to response format
    const filters: Filter[] = Array.from(filterMap.entries()).map(
      ([name, values]) => ({
        name,
        values: Array.from(values.entries()).map(([value, count]) => ({
          value,
          count,
        })),
      })
    );

    // Add categories as a filter if we have more than one category
    if (categoryMap.size > 1) {
      const categoryFilter: Filter = {
        name: 'Category',
        values: Array.from(categoryMap.entries()).map(([_, data]) => ({
          value: data.title,
          count: data.count,
        })),
      };
      filters.unshift(categoryFilter);
    }

    return filters;
  }

  // Method to clean up old cache entries
  static async cleanupOldCaches(): Promise<void> {
    try {
      await prisma.precomputedFilter.deleteMany({
        where: {
          updatedAt: {
            lt: new Date(Date.now() - this.CACHE_TTL),
          },
        },
      });
    } catch (error) {
      log.error('Error cleaning up old caches:', error);
    }
  }
}
```

```ts
import { ServiceResponse } from '../../common/serviceResponse';
import { FilterCacheService } from './services/filterCacheService';

export async function getSearchFiltersAsync(payload: { query: string }) {
  try {
    // Try to get from cache first
    let filters = await FilterCacheService.getSearchFilters(payload.query);

    // If not in cache, compute and cache
    if (!filters) {
      filters = await FilterCacheService.computeAndCacheSearchFilters(
        payload.query
      );
    }

    return ServiceResponse.ok('Filters retrieved successfully', { filters });
  } catch (error) {
    return ServiceResponse.serverError();
  }
}
```

periodically update caches
```ts
import { FilterCacheService } from '../../features/product/services/filterCacheService';
import { prisma } from '../../lib/prisma';
import log from '../util/logger';

export async function refreshPopularFilterCaches() {
  try {
    // Clean up old caches first
    await FilterCacheService.cleanupOldCaches();

    // Get popular categories (those with most products)
    const popularCategories = await prisma.category.findMany({
      select: { id: true },
      orderBy: {
        Product: {
          _count: 'desc',
        },
      },
      take: 10, // top 10 categories
    });

    // Recompute filters for popular categories
    for (const category of popularCategories) {
      await FilterCacheService.computeAndCacheCategoryFilters(category.id);
    }

    // You could also maintain a table of popular searches and recompute those
    // For now, we'll just log completion
    log.info('Filter cache refresh completed');
  } catch (error) {
    log.error('Error refreshing filter caches:', error);
  }
}
```
