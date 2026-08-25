## Table of Contents
1. [Overview](#1-overview)
2. [Tech Stack](#2-tech-stack)
3. [Architecture Overview](#3-architecture-overview)
4. [Authentication](#4-authentication)
5. [Data Model](#5-data-model)
6. [Feature Specifications](#6-feature-specifications)
   - 6.1 [Home Page](#61-home-page)
   - 6.2 [Sets](#62-sets)
   - 6.3 [Tournaments](#63-tournaments)
   - 6.4 [Session History](#64-session-history)
   - 6.5 [Account](#65-account)
7. [Real-time Architecture](#7-real-time-architecture)
8. [Payment Integration — Monnify](#8-payment-integration--monnify)
9. [Route Map](#9-route-map)
10. [Infrastructure](#10-infrastructure)
11. [Migration from Current App](#11-migration-from-current-app)
12. [What to Reuse vs. Rebuild](#12-what-to-reuse-vs-rebuild)
13. [Environment Variables](#13-environment-variables)
14. [Out of Scope for v1](#14-out-of-scope-for-v1)

---
## 1. Overview

QSet helps people manage sports sessions — tracking teams, matches, queues, results, and standings in real time. It is built for Nigerian venues (football pitches, sports centres, etc.) where one person runs the session on a phone and others want to follow along on their own screens.

The current app is a fully client-side SvelteKit PWA with no backend. All state lives in `localStorage`. This rebuild introduces a proper server, database, real-time WebSocket broadcasting, user accounts, and a paid tournament hosting feature.
### Goals of the rebuild
- **Sets remain frictionless.** Anonymous users can start a session without an account. The experience must be at least as fast as the current app.
- **Sets become persistent and shareable.** A session lives on the server. The host controls it; anyone with the link can watch live.
- **Design for the planned sets roadmap now.** Players, goals, assists, and per-session match history are coming. The data model must support them from day one even if the UI is deferred.
- **Tournaments are a paid feature.** Authenticated users pay a per-tournament fee (via Monnify) to create and host a tournament.
- **Single application.** Sets and tournaments share one SvelteKit codebase, one design system, and one deployment.

---
## 2. Tech Stack

| Concern         | Choice                                     | Notes                                    |
| --------------- | ------------------------------------------ | ---------------------------------------- |
| Framework       | SvelteKit 2 + Svelte 5 (runes)             | Existing — keep                          |
| Language        | TypeScript                                 | Existing — keep                          |
| Styling         | Tailwind CSS v4                            | Existing — keep                          |
| UI primitives   | bits-ui, shared component library          | Existing — keep                          |
| ORM             | Prisma                                     | New                                      |
| Database        | PostgreSQL                                 | Hosted on Railway                        |
| Auth            | Better Auth                                | New — replaces nothing (no auth existed) |
| Real-time       | `ws` (WebSocket library) via custom server | New                                      |
| Payments        | Monnify                                    | New                                      |
| Hosting         | Railway (Node.js service)                  | New — was static host                    |
| Adapter         | `@sveltejs/adapter-node`                   | Replaces `adapter-static`                |
| Analytics       | PostHog                                    | Existing — keep                          |
| Email           | Resend (or Nodemailer)                     | Replaces EmailJS                         |
| Package manager | Bun                                        | Existing — keep                          |

---
## 3. Architecture Overview
### Current (client-only)
```
Browser
  └── SvelteKit (static, prerendered)
        └── localStorage  ←  all game state
```
### Rebuilt (server-centric)
```
Browser (SvelteKit client)
  │
  ├── HTTP  →  SvelteKit server routes  →  Prisma  →  PostgreSQL
  │
  └── WebSocket  →  ws server  →  session rooms  →  broadcast to observers
```

The SvelteKit server and the WebSocket server share a single Node.js HTTP server (see [Section 7](#7-real-time-architecture)). They are deployed as one Railway service.
### Key conceptual shift
The `Game` class in `game.svelte.ts` is today a client-side singleton backed by `localStorage`. In the rebuild it is split:
- **`GameService`** — server-side TypeScript class. Contains all domain logic (queue management, match result handling, streak calculation). Reads and writes via Prisma. Has no Svelte reactivity.
- **Client store** — Svelte 5 `$state` objects on the client. Initialised from a server load, then kept in sync via WebSocket messages. The host's UI dispatches actions to the server; the server updates the DB and broadcasts the new state to all connected clients.

---
## 4. Authentication
### Provider: Better Auth
Better Auth is a self-hosted, framework-agnostic TypeScript auth library. It integrates directly with Prisma and has a SvelteKit adapter.
### Supported methods (v1)
- Email + password
- Magic link (OTP via email) — preferred for venue context; no password to forget
### Account requirement by feature

| Feature | Auth required |
|---|---|
| Create a sets session | No — anonymous |
| Control a sets session (host) | No — session token in URL is sufficient |
| View a live sets session | No |
| Save session to history | Yes — anonymous sessions are ephemeral |
| Claim an anonymous session | Yes — sign in after the fact |
| Create a tournament | Yes |
| Pay for a tournament | Yes |
| View a tournament bracket | No |
### Session ownership
When an anonymous user creates a sets session, a `hostToken` (random UUID) is generated and stored in the URL and in `sessionStorage`. This token is what grants host control. If the user signs in, they can link the session to their account via the `hostId` field.

Better Auth manages its own tables (`user`, `session`, `account`, `verification`) separately from the QSet domain tables. Do not conflate Better Auth's `session` table with QSet's `Session` model.

---
## 5. Data Model
Full Prisma schema. The Better Auth tables are generated separately by the library — they are noted here for completeness but not manually defined.
```prisma
// prisma/schema.prisma

generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

// ─────────────────────────────────────────────
// BETTER AUTH TABLES (managed by the library)
// ─────────────────────────────────────────────
// model User         { ... }   ← email, name, emailVerified, image
// model AuthSession  { ... }   ← token, userId, expiresAt
// model Account      { ... }   ← provider, providerAccountId, userId
// model Verification { ... }   ← identifier, value, expiresAt


// ─────────────────────────────────────────────
// QSET DOMAIN
// ─────────────────────────────────────────────

/// A sets game session. Anonymous or owned by a User.
model Session {
  id           String        @id @default(cuid())
  /// Short human-readable join code, e.g. "ABC-123". Used in URLs and sharing.
  code         String        @unique
  /// Display name for the session (venue name). E.g. "Qball Turf - Ikeja".
  name         String?
  status       SessionStatus @default(ACTIVE)
  /// Better Auth user ID of the host. Null for anonymous sessions.
  hostId       String?
  /// Token that grants host control for anonymous sessions.
  /// Stored client-side in sessionStorage; included in the control URL.
  hostToken    String        @unique @default(cuid())
  teams        Team[]
  matches      Match[]
  queueEntries QueueEntry[]
  createdAt    DateTime      @default(now())
  endedAt      DateTime?

  @@index([hostId])
  @@index([status])
}

enum SessionStatus {
  ACTIVE
  ENDED
  ARCHIVED
}

/// A team within a session.
model Team {
  id            String       @id @default(cuid())
  name          String
  session       Session      @relation(fields: [sessionId], references: [id], onDelete: Cascade)
  sessionId     String
  players       Player[]
  matchesAsA    Match[]      @relation("MatchTeamA")
  matchesAsB    Match[]      @relation("MatchTeamB")
  wins          Int          @default(0)
  draws         Int          @default(0)
  losses        Int          @default(0)
  currentStreak Int          @default(0)
  createdAt     DateTime     @default(now())

  @@unique([sessionId, name])
  @@index([sessionId])
}

/// Ordered queue position for a team within a session.
/// Separate table so order is persistent and auditable.
model QueueEntry {
  id        String   @id @default(cuid())
  session   Session  @relation(fields: [sessionId], references: [id], onDelete: Cascade)
  sessionId String
  teamId    String
  /// Zero-based position. Lower = closer to next match.
  position  Int
  createdAt DateTime @default(now())

  @@unique([sessionId, position])
  @@unique([sessionId, teamId])
  @@index([sessionId])
}

/// A player within a team. Included in schema now; stats UI is deferred to a future release.
model Player {
  id        String       @id @default(cuid())
  name      String
  team      Team         @relation(fields: [teamId], references: [id], onDelete: Cascade)
  teamId    String
  events    MatchEvent[]
  createdAt DateTime     @default(now())

  @@unique([teamId, name])
  @@index([teamId])
}

/// A single match within a session or tournament.
model Match {
  id           String       @id @default(cuid())
  session      Session      @relation(fields: [sessionId], references: [id], onDelete: Cascade)
  sessionId    String
  teamA        Team         @relation("MatchTeamA", fields: [teamAId], references: [id])
  teamAId      String
  teamB        Team         @relation("MatchTeamB", fields: [teamBId], references: [id])
  teamBId      String
  /// Null while the match is in progress.
  result       MatchResult?
  events       MatchEvent[]
  playedAt     DateTime     @default(now())
  completedAt  DateTime?
  /// Set only when this match belongs to a tournament.
  tournament   Tournament?  @relation(fields: [tournamentId], references: [id])
  tournamentId String?
  /// Round number within the tournament (null for sets matches).
  round        Int?

  @@index([sessionId])
  @@index([tournamentId])
}

enum MatchResult {
  TEAM_A
  TEAM_B
  DRAW
}

/// An event recorded during a match (goal, assist, etc.).
/// The metadata Json field is an escape hatch for future event types
/// so new types can be added without schema migrations.
model MatchEvent {
  id        String         @id @default(cuid())
  match     Match          @relation(fields: [matchId], references: [id], onDelete: Cascade)
  matchId   String
  type      MatchEventType
  /// Null if no specific player is attributed (e.g. own goal before players feature ships).
  player    Player?        @relation(fields: [playerId], references: [id])
  playerId  String?
  /// Which team this event belongs to. Denormalised for query convenience.
  teamId    String?
  /// Minute of the match the event occurred. Optional.
  minute    Int?
  /// Arbitrary JSON for future event metadata.
  metadata  Json?
  createdAt DateTime       @default(now())

  @@index([matchId])
  @@index([playerId])
}

enum MatchEventType {
  GOAL
  ASSIST
}

// ─────────────────────────────────────────────
// TOURNAMENTS
// ─────────────────────────────────────────────

/// A tournament, always owned by an authenticated user.
model Tournament {
  id        String           @id @default(cuid())
  name      String
  format    TournamentFormat
  status    TournamentStatus @default(DRAFT)
  /// Better Auth user ID of the host.
  hostId    String
  teams     TournamentTeam[]
  matches   Match[]
  payment   Payment?
  createdAt DateTime         @default(now())
  startedAt DateTime?
  endedAt   DateTime?

  @@index([hostId])
  @@index([status])
}

enum TournamentFormat {
  ROUND_ROBIN
  SINGLE_ELIMINATION
  /// Deferred to a future release. Included in enum now to avoid a migration later.
  DOUBLE_ELIMINATION
  /// Deferred to a future release.
  SWISS
}

enum TournamentStatus {
  /// Created but payment not yet confirmed.
  DRAFT
  /// Payment confirmed. Accepting teams or in progress.
  ACTIVE
  COMPLETED
}

/// A team participating in a tournament. Separate from Session Team
/// because tournament teams are not part of a sets session.
model TournamentTeam {
  id           String     @id @default(cuid())
  name         String
  tournament   Tournament @relation(fields: [tournamentId], references: [id], onDelete: Cascade)
  tournamentId String
  /// Optional seeding for bracket formats.
  seed         Int?
  createdAt    DateTime   @default(now())

  @@unique([tournamentId, name])
  @@index([tournamentId])
}

// ─────────────────────────────────────────────
// PAYMENTS
// ─────────────────────────────────────────────

/// Payment record for a tournament. One payment per tournament.
model Payment {
  id              String        @id @default(cuid())
  tournament      Tournament    @relation(fields: [tournamentId], references: [id])
  tournamentId    String        @unique
  /// Monnify transaction reference returned at initiation.
  monnifyRef      String?       @unique
  /// Monnify's own payment reference (confirmed in webhook).
  monnifyPayRef   String?       @unique
  status          PaymentStatus @default(PENDING)
  /// Amount in kobo (smallest NGN unit), e.g. 500000 = ₦5,000.
  amountKobo      Int
  currency        String        @default("NGN")
  createdAt       DateTime      @default(now())
  updatedAt       DateTime      @updatedAt
}

enum PaymentStatus {
  PENDING
  COMPLETED
  FAILED
  REFUNDED
}
```
### Design decisions
- **`QueueEntry` as a first-class table.** Queue order is persistent and can be audited. Reordering is an update to `position` values, not an array mutation.
- **`Match` shared between sets and tournaments.** A tournament match has a non-null `tournamentId`; a sets match has a null one. This avoids a parallel `TournamentMatch` table with duplicate columns.
- **`Player` and `MatchEvent` included now.** The UI for recording goals/assists is deferred, but the schema is in place so future migrations are additive only.
- **`metadata: Json` on `MatchEvent`.** New event types (yellow card, save, substitution) can carry arbitrary data without a schema migration.
- **Amounts in kobo.** All monetary values stored as integers in the smallest currency unit. Never store floats for money.
- **Better Auth tables separate.** Never join on Better Auth's `user.id` directly in application queries. Store it as a plain `String` (`hostId`, etc.) and let Better Auth manage its own tables.

---
## 6. Feature Specifications
### 6.1 Home Page
**Route:** `/`
The home page is the entry point for all users. It replaces the current behaviour of immediately rendering the team setup form.
**Layout:**
- QSet logo / wordmark at the top
- Two large mode cards side by side (or stacked on mobile):
  - **Sets** — "Manage teams, track results, see who's next" — CTA: "Start a Session"
  - **Tournaments** — "Bracket-style competitions with full standings" — CTA: "Host a Tournament"
- Below the cards: "Have a session code? Join here" → input for a 6-character code

**Behaviour:**
- "Start a Session" navigates to `/sets` (setup flow, no auth required)
- "Host a Tournament" navigates to `/account/login` if not authenticated, then `/tournaments/new`
- Entering a session code navigates to `/sets/[code]`

---
### 6.2 Sets
Sets are the core product. The experience must feel instant for the host.
#### 6.2.1 Session Creation (`/sets`)
Identical to the current `SetupPage` flow:
1. Enter venue name
2. Enter team names (min 2, validated, uppercase)
3. Optionally reorder teams (drag-and-drop)
4. Press "Start"

On submit, the client POSTs to a server action which:
1. Creates a `Session` record with a generated `code` (e.g. `AJK-492`)
2. Creates `Team` records
3. Creates initial `QueueEntry` records
4. Returns the session `code` and `hostToken`

The client stores `hostToken` in `sessionStorage` and navigates to `/sets/[code]`.
#### 6.2.2 Session View (`/sets/[code]`)
This is the main game screen. Its layout is identical to the current `/game` page:
- **Nav** (with session code displayed and a share button)
- **Tabs:** Match | Table | History

The page detects the user's role on load:
- If `sessionStorage` contains a matching `hostToken` → **host mode** (full controls)
- Otherwise → **observer mode** (read-only, live updates via WebSocket)

The `+page.server.ts` load function fetches the full session state from the DB and passes it as initial data. The client hydrates its reactive store from this, then opens a WebSocket connection to receive deltas.
#### 6.2.3 Host Controls (Match Tab)
Identical to current behaviour:
- Undo / Redo
- Match display (Team A vs Team B with result buttons: A Wins, Draw, B Wins)
- Timer (per-match countdown, configurable)
- Queue display (drag-and-drop reorder, remove team)
- Add team

Every host action:
1. Optimistically updates the client store (feels instant)
2. POSTs to a server action
3. Server updates DB via `GameService`
4. Server broadcasts a WebSocket message to the session room
5. All connected observers receive and apply the delta

If the server rejects the action (validation failure, race condition), the client rolls back the optimistic update and shows an error toast.
#### 6.2.4 Ending a Session
The host can press "End Session" (currently "Reset"). This:
1. Sets `Session.status = ENDED`, records `endedAt`
2. Broadcasts a `SESSION_ENDED` WebSocket message to all observers
3. If the host is authenticated, the session is preserved in their history
4. If the host is anonymous, the session data is retained for 7 days then deleted (a scheduled job on Railway)
5. Host is offered: "Sign in to save this session permanently"

#### 6.2.5 Joining as an Observer
Anyone with the session URL (`/sets/[code]`) or the 6-character code is an observer by default. The page renders in read-only mode: all match controls are hidden. They see the current match, queue, table, and history — all updating in real time.
#### 6.2.6 Players & Stats _(data model ready — UI deferred)_
Each `Team` will eventually have a roster of `Player` records. During a match, the host will record `MatchEvent` entries (GOAL, ASSIST) against specific players. Per-player stats (goals, assists) will accumulate across the session.

The schema supports this from day one. The UI for it is **not in v1** — do not build the player management screens yet, but do not build anything that would make adding it harder.

---
### 6.3 Tournaments
#### 6.3.1 Tournament Creation (`/tournaments/new`)
Requires authentication. Flow:
1. **Details step:** Enter tournament name, select format (Round Robin or Single Elimination for v1)
2. **Teams step:** Add team names (min 2 for round robin, must be power of 2 for single elimination — validate)
3. **Review step:** Summary + payment CTA
4. **Payment:** Monnify checkout (see [Section 8](#8-payment-integration--monnify))

On payment confirmation (via webhook), the tournament `status` moves from `DRAFT` → `ACTIVE`.

A `DRAFT` tournament is invisible to public URLs. If the user abandons before paying, the draft is cleaned up after 24 hours.
#### 6.3.2 Tournament View (`/tournaments/[id]`)
Public, no auth required to view.
**Round Robin:**
- Fixture list showing all matches (scheduled → in progress → completed)
- Live league table (same logic as the current `LeagueTable` component)
- Match history

**Single Elimination:**
- Visual bracket (left-to-right rounds)
- Completed matches show scores; upcoming matches show TBD

Both formats show a "Live" indicator when the host is actively entering results.
#### 6.3.3 Host Control (`/tournaments/[id]/manage`)
Auth-gated (must be the tournament's `hostId`).

- Enter results for the current round's matches
- For round robin: all matches can be entered in any order
- For single elimination: matches unlock when previous round is complete
- Each result submission: server updates DB, broadcasts WebSocket delta to all viewers of that tournament
#### 6.3.4 Tournament Formats (v1 scope)
**Round Robin:**
- Every team plays every other team once
- Points: 3 for win, 1 for draw, 0 for loss
- Final standings: points → goal difference (future) → name alphabetically
- Fixture generation: round-robin algorithm on tournament creation
**Single Elimination:**
- Teams seeded 1–N (host can reorder seeding before activation)
- Bracket generated on tournament creation
- Each round: winners advance, losers are eliminated
- Final match produces champion

---
### 6.4 Session History
**Route:** `/history` (auth required)
Lists all `Session` records where `hostId` matches the authenticated user, ordered by `createdAt` desc.
Each entry shows: venue name, date, number of teams, number of matches played.

**Route:** `/history/[sessionId]`
Full session replay: final league table, all matches in order, match events (when players feature ships). Read-only.

---
### 6.5 Account
**Route:** `/account`
- Display name and email
- Billing: list of tournaments and their payment status
- Danger zone: delete account (cascades to sessions, tournaments)

**Routes:** `/account/login`, `/account/register` — standard Better Auth forms (email/password or magic link).

---
## 7. Real-time Architecture
### Custom server
SvelteKit with `adapter-node` supports a custom `server.ts` entry point. This is how we attach the WebSocket server to the same HTTP port without needing a second process.
```typescript
// server.ts
import { createServer } from 'http';
import { WebSocketServer, WebSocket } from 'ws';
import { handler } from './build/handler.js';

const server = createServer(handler);
const wss = new WebSocketServer({ server, path: '/api/ws' });

// Map of sessionCode → Set of connected WebSocket clients
const rooms = new Map<string, Set<WebSocket>>();

wss.on('connection', (ws, req) => {
  const url = new URL(req.url!, `http://localhost`);
  const code = url.searchParams.get('code');
  if (!code) { ws.close(); return; }

  if (!rooms.has(code)) rooms.set(code, new Set());
  rooms.get(code)!.add(ws);

  ws.on('close', () => {
    rooms.get(code)?.delete(ws);
    if (rooms.get(code)?.size === 0) rooms.delete(code);
  });
});

export function broadcast(code: string, message: WsMessage) {
  const room = rooms.get(code);
  if (!room) return;
  const payload = JSON.stringify(message);
  for (const client of room) {
    if (client.readyState === WebSocket.OPEN) client.send(payload);
  }
}

server.listen(process.env.PORT ?? 3000);
```

The `broadcast` function is imported by `GameService` and called after every state mutation.
### WebSocket message types
All messages are JSON with a `type` discriminant.

| `type`              | Direction       | Payload                                                                              | Description                                                  |
| ------------------- | --------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------------------ |
| `SESSION_STATE`     | Server → Client | Full session snapshot                                                                | Sent on initial connect if state has changed since page load |
| `MATCH_RESULT`      | Server → Client | `{ matchId, result, teamAStats, teamBStats, nextMatchTeamA, nextMatchTeamB, queue }` | A result was recorded                                        |
| `QUEUE_UPDATE`      | Server → Client | `{ queue: QueueEntry[] }`                                                            | Queue was reordered                                          |
| `TEAM_ADDED`        | Server → Client | `{ team: Team, queue: QueueEntry[] }`                                                | A new team was added                                         |
| `TEAM_REMOVED`      | Server → Client | `{ teamId, queue: QueueEntry[] }`                                                    | A team was removed                                           |
| `TEAM_RENAMED`      | Server → Client | `{ teamId, name }`                                                                   | A team was renamed                                           |
| `TIMER_START`       | Server → Client | `{ endsAt: number }`                                                                 | Host started the timer (Unix ms)                             |
| `TIMER_STOP`        | Server → Client | `{}`                                                                                 | Host stopped the timer                                       |
| `TIMER_RESET`       | Server → Client | `{ durationSeconds: number }`                                                        | Host reset the timer                                         |
| `SESSION_ENDED`     | Server → Client | `{}`                                                                                 | Host ended the session                                       |
| `TOURNAMENT_UPDATE` | Server → Client | `{ tournamentId, matches, standings }`                                               | A tournament result was recorded                             |
The client subscribes to the relevant message types and applies deltas to the local `$state` store. It never re-fetches the full session from the server on a WebSocket message — it applies the delta in place.
### Client WebSocket store
```typescript
// $lib/stores/sessionSocket.svelte.ts
export class SessionSocket {
  private ws: WebSocket | null = null;
  connected = $state(false);

  connect(code: string) {
    this.ws = new WebSocket(`/api/ws?code=${code}`);
    this.ws.onopen = () => (this.connected = true);
    this.ws.onclose = () => { this.connected = false; this.reconnect(code); };
    this.ws.onmessage = (e) => applyMessage(JSON.parse(e.data));
  }

  private reconnect(code: string) {
    setTimeout(() => this.connect(code), 2000); // simple backoff
  }
}
```

`applyMessage` is a dispatcher that routes each `WsMessage` type to the appropriate store mutation.

---
## 8. Payment Integration — Monnify
### About Monnify
Monnify is a Nigerian payment gateway (by Moniepoint). It supports card payments, bank transfer, and USSD. We use their web SDK for checkout initiation and their webhook for server-side confirmation.
### Flow
```
1. User completes tournament creation form → clicks "Pay to Activate"
2. Client calls server action: POST /api/tournaments/[id]/initiate-payment
3. Server calls Monnify API to create a transaction → receives paymentUrl + monnifyRef
4. Server saves Payment record { status: PENDING, monnifyRef }
5. Client redirects to paymentUrl (Monnify hosted checkout)
6. User completes payment on Monnify's page
7. Monnify calls POST /api/webhooks/monnify with payment confirmation
8. Server verifies the webhook signature (HMAC-SHA512)
9. Server updates Payment { status: COMPLETED, monnifyPayRef }
10. Server updates Tournament { status: ACTIVE }
11. Client polls /api/tournaments/[id]/status (every 3s, max 30s) until ACTIVE
12. Client navigates to /tournaments/[id]
```
### Webhook verification
Monnify signs webhook payloads with HMAC-SHA512 using the secret key. Always verify before trusting:
```typescript
// src/routes/api/webhooks/monnify/+server.ts
import { createHmac } from 'crypto';
import { MONNIFY_SECRET_KEY } from '$env/static/private';

export async function POST({ request }) {
  const body = await request.text();
  const signature = request.headers.get('monnify-signature');
  const expected = createHmac('sha512', MONNIFY_SECRET_KEY)
    .update(body)
    .digest('hex');

  if (signature !== expected) {
    return new Response('Forbidden', { status: 403 });
  }

  const payload = JSON.parse(body);
  // update Payment + Tournament status...
  return new Response('OK', { status: 200 });
}
```

### Amount
Tournament fee amount is defined as a server-side constant (not in the DB, not client-configurable). Set it in an env variable `TOURNAMENT_FEE_KOBO` (e.g. `500000` = ₦5,000). This makes it easy to change without a deployment.
### Test vs. live mode
Monnify provides separate test and live API keys. Use `MONNIFY_ENV=test` in development, `MONNIFY_ENV=live` in production. The Monnify SDK base URL changes accordingly.

---
## 9. Route Map
```
/                              Home — mode selector

/sets                          New session setup (anonymous ok)
/sets/[code]                   Live session — host or observer (role auto-detected)

/history                       Past sessions (auth required)
/history/[sessionId]           Session detail / replay

/tournaments                   Browse tournaments + create CTA
/tournaments/new               Create tournament wizard (auth required)
/tournaments/[id]              Public tournament view (bracket / table)
/tournaments/[id]/manage       Host control panel (auth required, must be host)

/account                       Profile + billing (auth required)
/account/login                 Login (email/password or magic link)
/account/register              Register

/api/ws                        WebSocket upgrade endpoint
/api/webhooks/monnify          Monnify payment webhook (server only, no auth)
/api/tournaments/[id]/initiate-payment   Initiate Monnify checkout
/api/tournaments/[id]/status   Poll tournament activation status
```
### Route protection
Use a SvelteKit `+layout.server.ts` at the `/account` and `/tournaments/new` and `/tournaments/[id]/manage` segments to check for a valid Better Auth session. Redirect to `/account/login` if not authenticated, preserving `?redirect=` so the user lands back after login.

---
## 10. Infrastructure
### Railway setup
- **Service:** Node.js (single service)
- **Plugin:** PostgreSQL (Railway managed)
- **Build command:** `bun run build`
- **Start command:** `node build/server.js` (the custom server entry, not the default SvelteKit output)
- **Health check:** `GET /api/health` → `200 OK`
### Database migrations
Use Prisma Migrate. CI/CD pipeline runs `prisma migrate deploy` before starting the server. Never run `prisma migrate dev` in production.
### Scheduled jobs
Railway supports cron jobs. Define:
- **Cleanup anonymous sessions:** daily at 03:00 WAT — delete `Session` records where `status = ENDED`, `hostId IS NULL`, and `endedAt < NOW() - INTERVAL '7 days'`
- **Cleanup abandoned drafts:** daily at 03:00 WAT — delete `Tournament` records where `status = DRAFT` and `createdAt < NOW() - INTERVAL '1 day'`

---
## 11. Migration from Current App
### Adapter
Replace `@sveltejs/adapter-static` with `@sveltejs/adapter-node` in `svelte.config.js`. Remove `export const prerender = true` from `src/routes/+layout.ts`.
### Game state in localStorage
On first load after the upgrade, if `localStorage` contains a `GameState` key:
- If there is an active game: show a banner — "You have an unsaved session. Start a new server session with these teams?" → button to POST the team names and seed a new `Session`
- Clear `localStorage` after migration or dismissal
### Routing

| Old route   | New route                                 |
| ----------- | ----------------------------------------- |
| `/`         | `/sets` (setup) or `/` (home)             |
| `/game`     | `/sets/[code]`                            |
| `/feedback` | Replaced by server-side feedback endpoint |

The old `/game` route can serve a redirect for any bookmarked users.
### EmailJS → Server-side email
Remove `@emailjs/browser`. Add a server action at `/api/feedback` that sends email via Resend (or Nodemailer + SMTP). The feedback form POSTs to this endpoint.
### Dexie / FeedbackDB
Remove entirely. Feedback records go to the server.

### `game.svelte.ts` → `GameService` + client store
The `Game` class logic (queue operations, `handleResult`, streak tracking) is sound. Extract it into `src/lib/server/GameService.ts` as a stateless service — each method takes the current session state and returns the new state, which `GameService` then persists via Prisma. The client-side `$state` store is a simplified mirror, initialised from `+page.server.ts` load data and updated by WebSocket messages.

### `TimerManager`
Stays entirely client-side. However, `start`/`stop`/`reset` events are now broadcast to observers via WebSocket (see `TIMER_START`, `TIMER_STOP`, `TIMER_RESET` message types). The timer runs independently on each client, synchronised by the `endsAt` timestamp.

### PostHog
No change needed. Keep existing `PUBLIC_POSTHOG_API_KEY` env var.

---
## 12. What to Reuse vs. Rebuild
### Keep as-is (zero or minimal changes)

| File/Module | Notes |
|---|---|
| `$lib/components/shared/*` | All UI primitives — Card, Button, Dialog, NumberInput, Page, etc. |
| `$lib/components/game/table-page/*` | LeagueTable, ShareLeagueTable, CurrentMatchPreview |
| `$lib/components/game/match-history-page/MatchHistory.svelte` | Minor prop changes only |
| `$lib/components/shared/tabs/*` | TabContext, TabHeader — no changes |
| `$lib/main/tour.svelte.ts` + tour data | No changes |
| `$lib/common/util.ts` | All utility functions |
| `$lib/common/enums.ts` | Keep, extend with new enums |
| Tailwind config + design tokens | No changes |
| PostHog wiring in `+layout.svelte` | No changes |
### Evolve (extend without breaking)

| File/Module                                      | Changes                                                                        |
| ------------------------------------------------ | ------------------------------------------------------------------------------ |
| `Nav.svelte`                                     | Add: session code display, account avatar/menu when authenticated              |
| `$lib/components/setup/TeamConfiguration.svelte` | Add: optional player roster input per team (behind a toggle, deferred UI)      |
| `$lib/main/game.svelte.ts`                       | Split: extract logic to `GameService.ts`; keep client store for reactive state |
| `$lib/common/constants.ts`                       | Add: new route constants, WS message type constants                            |
### Rebuild from scratch

| File/Module                    | Reason                                              |
| ------------------------------ | --------------------------------------------------- |
| `src/routes/+page.svelte`      | New home page (mode selector)                       |
| `src/routes/+layout.ts`        | Remove prerender, add auth session loading          |
| `src/routes/game/+page.svelte` | Moves to `/sets/[code]/+page.svelte`, server-loaded |
| All `/sets/*` routes           | New                                                 |
| All `/tournaments/*` routes    | New                                                 |
| All `/account/*` routes        | New                                                 |
| All `/api/*` routes            | New                                                 |
| `$lib/db/db.ts`                | Replace Dexie with Prisma client                    |
| `svelte.config.js`             | adapter-node, remove static config                  |
| `server.ts`                    | New custom server entry point                       |

---
## 13. Environment Variables

| Variable | Where used | Notes |
|---|---|---|
| `DATABASE_URL` | Prisma | PostgreSQL connection string. Set by Railway. |
| `BETTER_AUTH_SECRET` | Better Auth | Random secret, min 32 chars. |
| `BETTER_AUTH_URL` | Better Auth | Full base URL of the app, e.g. `https://qset.app` |
| `MONNIFY_API_KEY` | Server only | Monnify public API key |
| `MONNIFY_SECRET_KEY` | Server only | Monnify secret — never expose to client |
| `MONNIFY_CONTRACT_CODE` | Server only | Monnify merchant contract code |
| `MONNIFY_ENV` | Server only | `test` or `live` |
| `TOURNAMENT_FEE_KOBO` | Server only | Tournament fee in kobo, e.g. `500000` |
| `PUBLIC_POSTHOG_API_KEY` | Client + server | Existing. Prefix `PUBLIC_` means it is safe to expose. |
| `PUBLIC_BASE_URL` | Client | Full base URL for generating shareable links |
| `RESEND_API_KEY` | Server only | For transactional email (feedback, magic links) |
| `PORT` | Server | Set by Railway automatically |

All `PUBLIC_` prefixed variables are safe to include in the SvelteKit client bundle. All others must only be imported from `$env/static/private`.

---
## 14. Out of Scope for v1
The following are known desirable features that are explicitly deferred:
- **Players & stats UI** — schema is in place; build the data entry UI in v2
- **Double Elimination and Swiss tournament formats** — enum values included; logic deferred
- **Match goals/scorelines** — currently only win/draw/loss; per-match scores deferred
- **Tournament spectator chat**
- **Push notifications** (match result, session invite)
- **Admin dashboard** (usage metrics, payment history, moderation)
- **Team/player profiles across sessions** — players currently scoped to a single session's team
- **Mobile native app** (iOS/Android via Capacitor or similar)
- **Multiple payment providers** (Stripe, Paystack, etc.)
- **Refunds** — handled manually in v1
- **Dark mode**
- **Offline support / PWA service worker** — deprioritised once app becomes server-dependent; revisit

---
