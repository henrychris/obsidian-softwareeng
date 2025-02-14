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

model AppliedDiscount {
  id        String              @id @default(uuid())
  type      AppliedDiscountType
  valueType DiscountValueType
  value     Decimal             @db.Decimal(10, 2)
  reason    String?

  // For pre-configured discounts
  discountId String?
  discount   Discount? @relation(fields: [discountId], references: [id])

  /// The order this discount was applied to. This is optional.
  /// A discount may be applied to an entire order or to a specific item in an order. Not both.
  orderId String?
  order   Order?  @relation(fields: [orderId], references: [id])

  /// The order item this discount was applied to. This is optional.
  /// A discount may be applied to an entire order or to a specific item in an order. Not both.
  orderItemId String?    @unique
  orderItem   OrderItem? @relation(fields: [orderItemId], references: [id])

  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@map("appliedDiscounts")
}

enum DiscountValueType {
  FixedAmount
  Percentage
}

enum AppliedDiscountType {
  DiscountCode
  Automatic
  Custom /// Custom one-off discount - on order items, or orders
}
```

# 