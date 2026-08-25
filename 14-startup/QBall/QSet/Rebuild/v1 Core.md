This document covers the database schema, feature overviews, and key design decisions for the v1 core of the QSet rebuild. v1 core covers sets sessions only — no auth, no tournaments.
## Database Schema

```prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model Session {
  id           String         @id @default(uuid())
  displayName  String?
  status       SessionStatus  @default(ACTIVE)
  hostToken    String         @unique @default(uuid())
  hostId       String?        // nullable — populated when auth lands
  teams        Team[]
  matches      Match[]
  queueEntries QueueEntry[]
  events       SessionEvent[]
  createdAt    DateTime       @default(now())
  updatedAt    DateTime       @updatedAt

  @@index([hostId])
  @@index([status])
}

enum SessionStatus {
  ACTIVE
  ENDED
  ARCHIVED
}

model Team {
  id            String    @id @default(uuid())
  name          String
  sessionId     String
  session       Session   @relation(fields: [sessionId], references: [id], onDelete: Cascade)
  wins          Int       @default(0)
  draws         Int       @default(0)
  losses        Int       @default(0)
  currentStreak Int       @default(0)
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  @@unique([sessionId, name])
  @@index([sessionId])
}

model Match {
  id          String       @id @default(uuid())
  sessionId   String
  session     Session      @relation(fields: [sessionId], references: [id], onDelete: Cascade)
  teamAId     String
  teamA       Team         @relation("MatchTeamA", fields: [teamAId], references: [id])
  teamBId     String
  teamB       Team         @relation("MatchTeamB", fields: [teamBId], references: [id])
  result      MatchResult?  // null while match is in progress
  createdAt   DateTime     @default(now())
  completedAt DateTime?

  @@index([sessionId])
}

enum MatchResult {
  TEAM_A
  TEAM_B
  DRAW
}

model QueueEntry {
  id        String   @id @default(uuid())
  sessionId String
  session   Session  @relation(fields: [sessionId], references: [id], onDelete: Cascade)
  teamId    String
  position  Int      // zero-based; lower = closer to next match
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  @@unique([sessionId, position])
  @@unique([sessionId, teamId])
  @@index([sessionId])
}

model SessionEvent {
  id        String           @id @default(uuid())
  sessionId String
  session   Session          @relation(fields: [sessionId], references: [id], onDelete: Cascade)
  type      SessionEventType
  payload   Json             // context per event type, e.g. { matchId, result, teamAId, teamBId }
  undone    Boolean          @default(false)
  createdAt DateTime         @default(now())

  @@index([sessionId])
}

enum SessionEventType {
  TEAM_ADDED
  TEAM_REMOVED
  TEAM_RENAMED
  QUEUE_REORDERED
  MATCH_STARTED
  MATCH_RESULT_RECORDED
  MATCH_RESULT_UNDONE
  TEAM_SWAPPED
  SESSION_ENDED
  TIMER_STARTED
  TIMER_STOPPED
  TIMER_RESET
}
```

---
## Schema Design Decisions
**`hostToken` on Session.** Every session gets a UUID generated server-side at creation. It is returned once to the creating client and stored in `sessionStorage`. Any request that includes the correct token is granted host privileges. When auth lands, `hostId` is added alongside it — authenticated users are checked by `hostId`; anonymous sessions fall back to `hostToken`. No schema migration needed at that point.

**`hostId` is not unique.** A unique constraint would prevent the same user from hosting more than one session. Instead, `hostId` is indexed for fast lookups. If a "one active session per user" rule is desired, it is enforced in the application layer (`POST /sessions` checks for existing `ACTIVE` sessions for that `hostId`) — not in the schema.

**`displayName` is nullable.** The venue name is optional. An anonymous host in a hurry should not be blocked by it.

**`@@unique([sessionId, name])` on Team.** Duplicate team names within a session are prevented at the database level, not just in application code.

**`@@unique([sessionId, position])` on QueueEntry.** Two teams cannot occupy the same queue position within a session. Reordering is an update to `position` values across affected rows, done in a transaction.

**`@@unique([sessionId, teamId])` on QueueEntry.** A team can only appear in the queue once per session at any given time.

**Named relations on Match (`"MatchTeamA"`, `"MatchTeamB"`).** Prisma requires disambiguation when a model holds two foreign keys pointing at the same table. The labels are a Prisma schema requirement only — they produce no extra table or join. Match queries use a single `matches` collection filtered by `teamAId` or `teamBId` as needed:

```typescript
prisma.match.findMany({
  where: {
    sessionId,
    OR: [{ teamAId: teamId }, { teamBId: teamId }]
  }
})
```

**`SessionEvent` with `undone` flag.** Every host action writes a row to `SessionEvent`. The `undone` flag is what makes server-side undo/redo work — see the Undo/Redo section below. The `payload` JSON is unstructured by design; shape is defined per event type in application code, not enforced by the schema. This keeps the debug log flexible without requiring migrations for new event types.

**No `MatchEvent` or `Player` in v1.** Goals, assists, and per-player stats are deferred. The full plan includes these models; they will be added as additive migrations when the UI is built. Nothing in v1 should make adding them harder.

**No `Tournament` or `TournamentTeam` in v1.** Tournament support is a separate stage. The schema starts clean.

---
## Feature Overviews
### Session Creation
A host POSTs team names and an optional venue name. The server creates a `Session` record, one `Team` record per name, and initial `QueueEntry` records ordered by the submitted sequence. It returns the session `code` (short human-readable identifier, e.g. `AJK-492`) and the `hostToken`.

The client stores `hostToken` in `sessionStorage` and navigates to `/sets/[code]`. Any subsequent browser tab that opens the same URL without the token is an observer.

All subsequent host actions include the `hostToken` in the request (header or signed cookie). The server validates it before processing.

---
### Team Management
Teams can be added or removed before and during a session.

**Add team:** server creates a `Team` record, appends a `QueueEntry` at the next available position. If fewer than two teams are in the match slots, `setupNextMatch` runs immediately.

**Remove team:** server deletes the `Team` record (cascades to `QueueEntry`). If the removed team was in a match slot, the current match is cleared and `setupNextMatch` runs.

**Rename team:** server updates `Team.name`. Uniqueness within the session is enforced by the DB constraint.

All three actions write a `SessionEvent` row and broadcast the updated state to connected clients.

---
### Queue Management
The queue is the ordered list of teams waiting to play. It is stored as `QueueEntry` rows with integer `position` values.

**Reorder (drag and drop):** the client sends the new ordered list of `teamId`s. The server recalculates `position` values and updates all affected rows in a single transaction. A `QUEUE_REORDERED` event is logged.

**Next team determination:** always the `QueueEntry` with the lowest `position` for the session.

The in-memory `Queue` class from the current client app (`queue.items`, `enqueue`, `dequeue`, etc.) is replaced by DB reads and writes. The client store is a mirror initialised from the server load, kept in sync by WebSocket messages.

---
### Match Flow
A match is an in-progress `Match` record with a null `result`. When a result is recorded:
1. `Match.result` is set and `completedAt` is stamped
2. Winner and loser `Team` stats are updated (wins, losses, draws, currentStreak)
3. The loser is appended to the queue; the winner stays in their slot
4. A new in-progress `Match` record is created for the next pairing
5. A `MATCH_RESULT_RECORDED` `SessionEvent` is written with `payload: { matchId, teamAId, teamBId, result }`
6. The updated session state is broadcast to all connected clients

Draw handling: both teams re-enter the queue. The team with fewer wins goes in first (matching current app behaviour).

---
### Undo / Redo
Undo and redo are server-side operations. The client sends one request; the server derives everything from the `SessionEvent` log.

```
POST /api/sessions/:code/undo
POST /api/sessions/:code/redo
```

**Undo:** the server finds the last `SessionEvent` for the session where `undone = false`. It reverses the action described by that event's `type` and `payload`, then sets `undone = true` on that event row.

**Redo:** the server finds the last `SessionEvent` where `undone = true`. It reapplies the action, then sets `undone = false`.

The client holds an undo/redo stack in memory for UI state only (enabling/disabling the buttons). It never sends state to the server — just the intent to undo or redo. After a server response, the client replaces its local state with what the server returns.

**Why not client-driven compensating actions?** If the client were responsible for deciding which records to delete or patch, it would be encoding server business logic. A stale or buggy client could send the wrong mutations and corrupt the DB. The server owning undo logic keeps it consistent and correct regardless of client state.

---
### Timer
The timer is entirely client-side. Each connected client runs its own countdown, synchronised by the `endsAt` Unix timestamp broadcast by the server.

Timer actions (start, stop, reset) are sent by the host to the server, which logs the event (`TIMER_STARTED`, `TIMER_STOPPED`, `TIMER_RESET`) and broadcasts the relevant payload to all observers:

- `TIMER_STARTED` → payload: `{ endsAt: number }` (Unix ms)
- `TIMER_STOPPED` → payload: `{}`
- `TIMER_RESET` → payload: `{ durationSeconds: number }`

The server does not track timer state in the DB — there is no `timerEndsAt` column on `Session`. The timer is ephemeral session UI, not persistent data.

---
### League Table
Derived on demand from `Team` stats (`wins`, `draws`, `losses`, `currentStreak`) stored on each `Team` record. No separate table needed. The client computes sort order (by wins, then draws, then name) from the team data it already has in its local store.

---
### Match History
All completed `Match` records for a session (where `result` is not null), ordered by `completedAt`. Loaded as part of the initial server page load and kept up to date by `MATCH_RESULT` WebSocket messages. No separate history table — it is a filtered view of the `matches` relation.

---
### Session End
The host sends `POST /api/sessions/:code/end`. The server sets `Session.status = ENDED`, stamps `updatedAt`, logs `SESSION_ENDED`, and broadcasts a `SESSION_ENDED` WebSocket message to all observers. Observers are redirected to a read-only summary view.

Anonymous sessions are retained for 7 days after ending, then deleted by a scheduled cleanup job. When auth lands, authenticated sessions are retained indefinitely and appear in the host's session history.

---
## What Is Explicitly Deferred
- Authentication and session history (`hostId`, user accounts, `/history` routes) — schema has `hostId` placeholder; no other auth work in v1
- Player rosters and match events (goals, assists) — schema omitted intentionally; added as additive migrations later
- Tournaments — no schema, no routes
- Observer mode and WebSocket real-time sync — noted in the stages doc as Stage 3; v1 core is host-only
- Short session `code` generation logic — needs a collision-safe approach (retry loop or pre-generated pool); deferred to implementation