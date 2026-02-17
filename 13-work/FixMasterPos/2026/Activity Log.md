A system-wide, store-scoped audit trail using Typegoose with manual logging calls, async Agenda-based writes, auto-generated summaries, and TypeScript generics enforcing compile-time type safety. All logs are immutable, idempotent, and queryable with flat entity types and camelCase conventions.
## Implementation Steps
### 1. Create `ActivityLog` Typegoose Model
**File:** `src/modules/activityLog/models/activityLog.model.ts`
Create Typegoose model extending `TimeStamps` with the following fields:
- `eventType: EventType` - The specific event that occurred (e.g., "product.created")
- `entityType: EntityType` - Flat entity type (e.g., "product", "order", "repair")
- `entityId: Types.ObjectId` - Reference to the entity affected
- `actorType: ActorType` - Type of actor performing the action
- `actorId?: Types.ObjectId` - Reference to User (nullable for system actions)
- `actorName: string` - Cached actor name (user's fullName or "System")
- `summary: string` - Auto-generated human-readable summary
- `metadataJson: string` - Event-specific structured data (with warning about keeping concise)
- `ipAddress?: string` - Optional IP address of the request
- `source: SourceType` - Origin of the action
- `store: Types.ObjectId` - Required store reference (all logs are store-scoped)
- `location?: Types.ObjectId` - Optional location reference
**Indexes:**
- `[{store: 1, createdAt: -1}]` - Primary query pattern
- `[{store: 1, entityType: 1, entityId: 1, createdAt: -1}]` - Entity history
- `[{store: 1, actorId: 1, createdAt: -1}]` - Actor activity
- `[{store: 1, eventType: 1, createdAt: -1}]` - Event filtering

**Collection name:** `activitylogs`
**JSDoc:** Add warning comment on `metadataJson` field about keeping data concise to avoid bloat.

---
### 2. Define Comprehensive Type System with Discriminated Unions
**Directory:** `src/types/activityLog/`
**File to create:**
#### `eventTypes.ts`
Define string enums per category covering all spec events:
- `ProductEvent` - Created, Updated, Deleted, StockManuallyAdjusted, StockAutomaticallyAdjusted, BulkImportPerformed
- `OrderEvent` - Created, StatusChanged, Edited, PaymentReceived, PaymentRefunded, DiscountApplied, DiscountRemoved, TaxModified
- `RepairEvent` - Created, StatusChanged, DeviceAssigned, DeviceReassigned, CostUpdated, Completed, Cancelled, PaymentReceived, PaymentRefunded, DiscountApplied, DiscountRemoved
- `CustomerEvent` - Created, Updated, Deleted, Merged
- `StaffEvent` - Invited, Removed, RoleChanged, PermissionsUpdated, PinChanged
- `CashRegisterEvent` - Opened, Closed, CashAdded, CashRemoved, DiscrepancyDetected, DrawerForcedOpen
- `ExpenseEvent` - Created, Updated, Deleted, RecurringGenerated, RecurringDue
- `PayoutEvent` - Created, Completed, Failed, PartialIssued
- `AuthEvent` - LoginSuccess, LoginFailure, Logout, PasswordChanged, TwoFactorEnabled, TwoFactorDisabled, SuspiciousActivity
- `SystemEvent` - ScheduledJobExecuted, MigrationPerformed, WebhookReceived, IntegrationSyncCompleted, IntegrationSyncFailed
#### `metadata.ts`
Define TypeScript interfaces using discriminated unions for type-safe metadata per event. Use camelCase for all fields (e.g., `oldValue`, `newValue`, `field`).

Example structure:
```typescript
type ActivityLogMetadata = 
  | { eventType: ProductEvent.Created; productName: string; sku: string; cost: number }
  | { eventType: ProductEvent.Updated; field: string; oldValue: any; newValue: any }
  | { eventType: OrderEvent.Created; orderNumber: string; total: number; customerId?: string }
  | { eventType: OrderEvent.StatusChanged; oldStatus: string; newStatus: string }
  | { eventType: AuthEvent.LoginSuccess; email: string; method: string }
  // ... all 40+ event types
```

Create `MetadataMap` type mapping event types to their metadata interfaces for generic type inference.
#### `enums.ts`
Define shared enums:
- `ActorType` - "employee" | "system"
- `EntityType` - "product" | "order" | "repair" | "customer" | "staff" | "cashRegister" | "expense" | "payout" | "auth" | "system"
- `SourceType` - "POS" | "Admin" | "API" | "Automation"
- `EventType` -
```ts
export type EventType = 
  | ProductEvent 
  | OrderEvent 
  | RepairEvent 
  | CustomerEvent 
  | StaffEvent 
  | CashRegisterEvent 
  | ExpenseEvent 
  | PayoutEvent 
  | AuthEvent 
  | SystemEvent;
```
#### activityLog.types.ts`
Export all types, enums, and interfaces.

---
### 3. Build Type-Safe `ActivityLogService` with Generics
**File:** `src/modules/activityLog/activityLog.service.ts`
#### Public Method: `log<T extends EventType>()`
**Signature:**
```typescript
async log<T extends EventType>(
  request: FastifyRequest,
  eventType: T,
  entityType: EntityType,
  entityId: Types.ObjectId,
  source: SourceType,
  metadata: MetadataMap[T]
): Promise<void>
```

**Logic:**
1. Extract actor info:
   - If `request.user` exists: `actorType = 'employee'`, `actorId = request.user._id`, `actorName = request.user.fullName`
   - If no user (system action): `actorType = 'system'`, `actorId = undefined`, `actorName = "System"`
2. Extract store/location from headers: `request.headers['x-store-id']`, `request.headers['x-location-id']`
3. Get IP address: `getClientIp(request)` (import from `utils/getClientIp`)
4. Generate summary: `generateSummary(eventType, entityType, metadata)`
5. Enqueue Agenda job: `"activity-log:write"` with all data as payload
#### Private Method: `logInternal()`
**Purpose:** Actual database write, called by Agenda job.
**Logic:**
1. Create new `ActivityLogModel` document with all fields
2. Save to database
3. Idempotent via timestamp uniqueness (collision odds negligible)
#### Helper Method: `generateSummary()`
**Purpose:** Generate human-readable summary from event type.
**Logic:**
Inline switch/map statement returning templates based on event type:
- `ProductEvent.Created` → `"Product created"`
- `ProductEvent.Updated` → `"Product updated"`
- `OrderEvent.StatusChanged` → `"Order status changed"`
- `AuthEvent.LoginSuccess` → `"User logged in"`
- etc.
Can optionally enhance with entity names from metadata (e.g., `"Product 'iPhone 13' created"`).
#### Agenda Job Registration
In service initialization:
1. Import Agenda instance from `src/core/agenda/`
2. Define job: `agenda.define("activity-log:write", async (job) => { await this.logInternal(job.attrs.data) })`
3. Set immediate execution (no delay)
4. Rely on Agenda's built-in retry for idempotency

---
### 4. Implement REST API with Comprehensive Filtering
#### Controller: `src/modules/activityLog/activityLog.controller.ts`
**Method: `getActivityLogs()`**
- Extract query params: `startDate`, `endDate`, `actorId`, `entityType`, `eventType`, `actorType`, `source`, `page`, `limit`
- Extract store from `request.headers['x-store-id']`
- Build MongoDB query with filters
- Sort by `createdAt: -1` (newest first)
- Use `ApiResponse.paginate()` for response
- Return: logs array, total count, page, limit
- **Access:** Protected by `checkOwnerOrManager` middleware (only store owners and managers can view)

**Method: `getActivityLogById()`**
- Extract `id` from params
- Extract store from headers for scope validation
- Find log by `_id` and `store`
- Return with `ApiResponse.success()`
- Throw `AppError` if not found or wrong store
- **Access:** Protected by `checkOwnerOrManager` middleware (only store owners and managers can view)
#### Route: `src/modules/activityLog/activityLog.route.ts`
**Pattern:**
```typescript
export async function activityLogRoute(app: FastifyInstance) {
  app.setValidatorCompiler(validatorCompiler);
  app.setSerializerCompiler(serializerCompiler);

  app.withTypeProvider<ZodTypeProvider>().get(
    "/activity-logs",
    {
      schema: ActivityLogSchema.ListSchema,
      preHandler: [checkLogin, checkOwnerOrManager]
    },
    ActivityLogController.getActivityLogs
  );

  app.withTypeProvider<ZodTypeProvider>().get(
    "/activity-logs/:id",
    {
      schema: ActivityLogSchema.GetByIdSchema,
      preHandler: [checkLogin, checkOwnerOrManager]
    },
    ActivityLogController.getActivityLogById
  );
}
```

**Access Control:**
Create middleware `checkOwnerOrManager` that verifies `request.user.role` is either `UserRoles.OWNER` or `UserRoles.MANAGER` (from `src/config/constant/userRoleTypes.ts`). Return 403 error if user lacks permission.

**Zod Schemas:** (`src/modules/activityLog/activityLog.schema.ts`)
- `ListSchema` - Query params with optional filters
- `GetByIdSchema` - Params with `id` field

Follow patterns from `src/modules/order/order.route.ts`.

---
### 5. Integrate Type-Safe Logging into 8-10 Controllers
Import singleton `ActivityLogService` and add logging calls after successful operations:
#### `ProductController` (`src/modules/product/`)
- **Created:** After product save, log `ProductEvent.Created` with `{ productName, sku, cost }`
- **Updated:** After update, log `ProductEvent.Updated` with `{ field, oldValue, newValue }`
- **Deleted:** After soft-delete, log `ProductEvent.Deleted` with `{ productName, sku }`
- **Stock Adjusted:** After inventory change, log `ProductEvent.StockManuallyAdjusted` or `StockAutomaticallyAdjusted` with `{ productName, quantity, reason }`
#### `OrderController` (`src/modules/order/`)
- **Created:** Log `OrderEvent.Created` with `{ orderNumber, total, customerId }`
- **Status Changed:** Log `OrderEvent.StatusChanged` with `{ oldStatus, newStatus, orderNumber }`
- **Payment Received:** Log `OrderEvent.PaymentReceived` with `{ amount, method, orderNumber }`
- **Refunded:** Log `OrderEvent.PaymentRefunded` with `{ amount, reason, orderNumber }`
#### `RepairController` (`src/modules/repairs/`)
- **Created:** Log `RepairEvent.Created` with `{ deviceType, customerName, issue }`
- **Status Changed:** Log `RepairEvent.StatusChanged` with `{ oldStatus, newStatus, repairId }`
- **Cost Updated:** Log `RepairEvent.CostUpdated` with `{ oldCost, newCost, reason }`
#### `CustomerController` (`src/modules/customer/`)
- **Created:** Log `CustomerEvent.Created` with `{ customerName, email, phone }`
- **Updated:** Log `CustomerEvent.Updated` with `{ field, oldValue, newValue, customerName }`
- **Deleted:** Log `CustomerEvent.Deleted` with `{ customerName, email }`
#### `CashRegisterController` (`src/modules/cashRegister/`)
- **Opened:** Log `CashRegisterEvent.Opened` with `{ openingBalance, registerName }`
- **Closed:** Log `CashRegisterEvent.Closed` with `{ closingBalance, expectedBalance, difference }`
- **Cash Added:** Log `CashRegisterEvent.CashAdded` with `{ amount, reason }`
- **Cash Removed:** Log `CashRegisterEvent.CashRemoved` with `{ amount, reason }`
#### `ExpenseController` (`src/modules/expense/`)
- **Created:** Log `ExpenseEvent.Created` with `{ amount, category, vendor }`
- **Updated:** Log `ExpenseEvent.Updated` with `{ field, oldValue, newValue }`
- **Deleted:** Log `ExpenseEvent.Deleted` with `{ amount, category }`
#### `AuthController` (`src/modules/auth/`)
- **Login Success:** Log `AuthEvent.LoginSuccess` with `{ email, method }`
- **Login Failure:** Log `AuthEvent.LoginFailure` with `{ email, reason }`
- **Logout:** Log `AuthEvent.Logout` with `{ email }`

**Source determination:**
- Admin panel operations: `source = 'Admin'`
- API calls (webhooks, integrations): `source = 'API'`
- Cron jobs/scheduled tasks: `source = 'Automation'`
- POS operations: `source = 'POS'`

---
### 6. Register Routes, Export Service, Validate Integration
#### Export Service
In `src/modules/activityLog/activityLog.service.ts`:
```typescript
export const ActivityLogService = new ActivityLogServiceClass();
```
#### Register Routes
In `src/routes.ts`:
```typescript
import { activityLogRoute } from "./modules/activityLog/activityLog.route";

// ... after other routes
app.register(activityLogRoute);
```
#### Create Access Control Middleware
In `src/modules/activityLog/activityLog.middleware.ts` (or add to existing middleware file):
```typescript
import type { FastifyReply, FastifyRequest } from "fastify";
import { ApiResponse } from "../../core/ApiResponse";
import { UserRoles } from "../../config/constant/userRoleTypes";

export const checkOwnerOrManager = async (
  request: FastifyRequest,
  reply: FastifyReply
) => {
  const user = request.user;
  
  if (!user || (user.role !== UserRoles.OWNER && user.role !== UserRoles.MANAGER)) {
    return reply
      .code(403)
      .send(
        ApiResponse.error("Only store owners and managers can view activity logs")
      );
  }
};
```
#### Ensure Agenda Initialization
Verify in `src/plugins/agenda.plugin.ts` that Agenda is initialized before any activity logging occurs (typically on app startup).
#### Manual Testing Scenarios
Test the following flows:
1. **Product creation** - Verify log with correct product details, actor, store
2. **Order status change** - Verify old/new status in metadata
3. **Cash register open** - Verify opening balance, employee name
4. **User login** - Verify email, IP address captured
5. **System automation** - Verify `actorType: 'system'`, `actorName: "System"`

Check:
- Logs persist in database with correct `createdAt` timestamps
- Summaries are human-readable
- Metadata matches event type
- Store scoping works correctly
- Filtering API returns expected results
- Async Agenda writes complete successfully

---
## Architecture Decisions Summary
1. **Manual logging calls** - Precise metadata control, no middleware magic
2. **TypeScript generics** - Compile-time type safety for metadata per event type
3. **No runtime validation** - TypeScript type checking only, no Zod for metadata
4. **Existing timeline data** - Left as-is, no migration required
5. **Async writes via Agenda** - Hidden from caller, automatic retry for idempotency
6. **System actor naming** - Always `"System"` when `actorType: 'system'`
7. **CamelCase conventions** - `oldValue`, `newValue`, `field` for update events
8. **Flat entity types** - Single-word types: `product`, `order`, `repair`, etc.
9. **Auto-generated summaries** - Template-based in `generateSummary()` method
10. **Store-scoped logs** - All logs require `store` reference, no global system logs
11. **Immutable logs** - No edits, no deletes, append-only audit trail
12. **Metadata size warning** - JSDoc comment advising developers to keep data concise
13. **Source flexibility** - `source` field differentiates Admin/API/Automation/POS contexts
14. **Access control** - Only store owners and managers can view activity logs via REST API

---
## Key Patterns from Codebase
- **Typegoose model** - Extend `TimeStamps`, use `@prop`, `@modelOptions`, `@index`
- **Actor tracking** - Reference User with `Types.ObjectId`, cache `fullName` as string
- **Store/location context** - Extract from headers: `x-store-id`, `x-location-id`
- **IP tracking** - Use `getClientIp(request)` utility
- **API responses** - Use `ApiResponse.success()` and `ApiResponse.paginate()`
- **Route protection** - Use `checkLogin` middleware preHandler
- **Zod validation** - Define schemas in separate `.schema.ts` file
- **Module structure** - `models/`, `controller.ts`, `route.ts`, `schema.ts`, `service.ts` (optional)
- **Access control** - Owner and Manager roles only for activity log endpoints (`UserRoles.OWNER`, `UserRoles.MANAGER` from `src/config/constant/userRoleTypes.ts`)
---
## Future Considerations
1. **Batch writes** - If log volume exceeds 10K/day per store, consider batching Agenda jobs
2. **Archival strategy** - For long-term storage, implement periodic archival of old logs (>1 year)
3. **Enhanced summaries** - Optionally include entity names in summaries (e.g., "Product 'iPhone 13' created")
4. **Export functionality** - Add CSV/JSON export endpoint for compliance/reporting
5. **Real-time notifications** - Consider webhook/SSE for critical events (e.g., suspicious login)
6. **Performance monitoring** - Track Agenda job processing time, log write latency
7. **UI integration** - Build frontend components for collapsed/expanded log views per spec

---
## Non-Goals (Out of Scope)
- Editing or deleting logs (immutable by design)
- Aggregation/analytics features (separate reporting system)
- Role-based log redaction (all owners see all logs)
- Migrating existing timeline/history data
- Real-time log streaming (async writes acceptable)
- Advanced search (full-text indexing)
