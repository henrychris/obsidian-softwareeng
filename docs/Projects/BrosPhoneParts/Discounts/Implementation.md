[[PRD - Discount]]
# Schema
```prisma
model Discount {
  id     String         @id @default(uuid())
  title  String? /// Required for automatic discounts, optional for code-based
  code   String? /// Required for code-based discounts, optional for automatic
  method DiscountMethod
  type   DiscountType
  status DiscountStatus @default(Active)

  minimumPurchaseAmount   Int? /// Minimum purchase amount required for the discount to be applied
  minimumPurchaseQuantity Int? /// Minimum quantity of items required for the discount to be applied

  eligibilityChoice DiscountEligibilityChoice
  selectedCustomers Customer[]                @relation("CustomerDiscountEligibility")

  maximumNumberOfUses Int? /// Maximum number of times the discount can be used
  oneUsePerCustomer   Boolean @default(false) /// Whether the discount can be used only once per customer

  allowProductDiscounts  Boolean  @default(false) /// Whether the discount can be combined with product discounts
  allowOrderDiscounts    Boolean  @default(false) /// Whether the discount can be combined with order discounts
  allowShippingDiscounts Boolean? /// Whether the discount can be combined with shipping discounts

  startDate DateTime /// The date and time the discount becomes active
  endDate   DateTime? /// The date and time the discount expires

  configuration Json /// Stores the type-specific config

  storeId          String
  store            Store             @relation(fields: [storeId], references: [id])
  appliedDiscounts AppliedDiscount[]

  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@unique([code, storeId])
  @@map("discounts")
}

enum DiscountEligibilityChoice {
  AllCustomers
  SpecificCustomers
}

enum DiscountMethod {
  Automatic
  Code
}

enum DiscountType {
  AmountOffProducts
  BuyXGetY
  AmountOffOrder
  FreeShipping
}

enum DiscountStatus {
  Active
  Scheduled
  Expired
}

enum DiscountValueType {
  FixedAmount
  Percentage
}

model DraftAppliedDiscount {
  id          String   @id @default(uuid())
  
  type      AppliedDiscountType
  valueType DiscountValueType?
  value     Decimal?            @db.Decimal(10, 2)
  reason    String?
  
  // For tracking non-custom discounts
  discountId  String?
  discount    Discount? @relation(fields: [discountId], references: [id])
  
  // Relations - only one will be populated
  draftOrderId String?
  draftOrder   DraftOrder? @relation(fields: [draftOrderId], references: [id])
  
  draftOrderItemId String?
  draftOrderItem   DraftOrderItem? @relation(fields: [draftOrderItemId], references: [id])

  // Track which customer used the discount
  customerId String?
  customer   Customer? @relation(fields: [customerId], references: [id])
  
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt
  
  @@map("draftAppliedDiscounts")
}

enum DraftAppliedDiscountEntityType {
	DraftOrder
	DraftOrderItem
}

enum AppliedDiscountType {
  DiscountCode
  Automatic
  Custom /// Custom one-off discount - on order items, or orders
}
```

# Removed Code
```ts
async function applyAutomaticDiscounts(
  items: OrderItemInput[],
  storeId: string,
  customer: OrderCustomerInput | undefined | null,
): Promise<DiscountResult> {
  log.debug(`Fetching and applying automatic discounts`);
  const activeAutomaticDiscounts = await prisma.discount.findMany({
    where: {
      storeId,
      method: DiscountMethod.Automatic,
      type: DiscountType.AmountOffOrder, // Feb 20, 2025 - from my tests, only order discounts are applied automatically
      status: DiscountStatus.Active,
      startDate: { lte: new Date() },
      OR: [{ endDate: null }, { endDate: { gt: new Date() } }],
    },
    include: {
      _count: {
        select: {
          appliedDiscountsOnDraftOrders: true,
        },
      },
      selectedCustomers: true,
    },
  });

  let itemDiscounts: ItemWithDiscounts[] = [];
  let orderDiscounts: LeanAppliedDiscount[] = [];

  for (const discount of activeAutomaticDiscounts) {
    log.debug(`Checking eligibility for automatic discount: ${discount.id}`);
    const mappedDiscount = {
      ...discount,
      numberOfDiscountUses: discount._count.appliedDiscountsOnDraftOrders,
    };

    const discountValidationResult = await validateDiscountRequirements(
      mappedDiscount,
      items,
      customer,
    );
    if (discountValidationResult.success) {
      log.debug(`Applying automatic discount: ${discount.id}`);
      const appliedDiscountResult = await applyDiscount(
        {
          items,
          discount: {
            id: discount.id,
            type: discount.type,
            method: discount.method,
            configuration: discount.configuration as AllConfig,
          },
        },
        storeId,
      );

      itemDiscounts = mergeItemDiscounts(
        itemDiscounts,
        appliedDiscountResult.itemsWithDiscounts,
      );
      orderDiscounts = orderDiscounts.concat(
        appliedDiscountResult.orderDiscounts,
      );
    }
  }

  return {
    itemsWithDiscounts: itemDiscounts,
    orderDiscounts,
  };
}
```
