# Stage 1 — Project Scaffold & Infrastructure
Get the new repo to a deployable (empty) state on Railway before writing any feature code.
- Init new SvelteKit 2 + Svelte 5 project with `adapter-node`, TypeScript, Tailwind v4, Bun
- Add Prisma, configure `schema.prisma` with the full data model (all tables — don't defer schema)
- Run initial migration, connect Railway PostgreSQL plugin
- Write `server.ts` custom entry point (HTTP + WebSocket server skeleton — `broadcast` function in place even if nothing calls it yet)
- Add `GET /api/health` endpoint
- Wire all env variables (`.env.example` committed, actuals set in Railway)
- Confirm: `bun run build && node build/server.js` runs cleanly on Railway

**Exit criteria:** Railway deploy is green, health check passes, DB migrations run in CI.

---
# Stage 2 — Sets Core (No Auth, No Real-time)
Rebuild the primary product flow — session creation and the game screen — server-backed but without WebSocket sync yet. This is the MVP that replaces the current `localStorage` app.

- Migrate shared UI components (`$lib/components/shared/*`, design tokens, Tailwind config) from old repo
- `/sets` — session creation form (POST server action → creates `Session`, `Team`, `QueueEntry` records)
- `/sets/[code]` — game screen, server-loaded from DB, host-mode only (no observer mode yet)
- Port `GameService.ts` from `game.svelte.ts` — stateless methods (queue ops, `handleResult`, streak calc) backed by Prisma
- Client `$state` store initialised from `+page.server.ts` load data
- All host actions: optimistic update → POST server action → DB write (no broadcast yet)
- `/` — home page with mode selector and join-by-code input

**Exit criteria:** A full sets session can be run end-to-end (create → play → end) with state persisted in PostgreSQL.

---
# Stage 3 — Real-time (Observer Mode)
Layer WebSocket broadcasting onto the working Sets foundation.
- Complete the `server.ts` WS room management (connect, disconnect, room cleanup)
- `GameService` calls `broadcast()` after every state mutation
- Client `SessionSocket` store (`sessionSocket.svelte.ts`) — connect on page load, apply deltas
- Implement all WS message handlers: `MATCH_RESULT`, `QUEUE_UPDATE`, `TEAM_ADDED`, `TEAM_REMOVED`, `TEAM_RENAMED`, `TIMER_START/STOP/RESET`, `SESSION_ENDED`
- Observer mode on `/sets/[code]` — no host token in `sessionStorage` → read-only, live updates
- `SESSION_STATE` message on connect (catch-up if state changed since page load)
- Share button + session code display in Nav

**Exit criteria:** Two browser windows open on the same session URL — one as host, one as observer — stay in sync in real time.

---
# Stage 4 — Authentication & Session History
Add Better Auth and the account-gated features.
- Install and configure Better Auth with Prisma adapter
- Email + password auth (magic link as fast follow)
- `/account/login`, `/account/register`
- Route protection middleware (`+layout.server.ts`) at `/account`, `/history`, `/tournaments/new`, `/tournaments/[id]/manage`
- Claim anonymous session: when authenticated, `hostId` is set; when anonymous, offer "Sign in to save this session" on session end
- `/history` — list of user's past sessions
- `/history/[sessionId]` — read-only session replay (final table, match list)
- `/account` — profile, billing placeholder (populated in Stage 5)
- Server-side email via Resend for transactional mail; remove EmailJS

**Exit criteria:** Full auth loop works. Authenticated sessions appear in history. Anonymous sessions are ephemeral with a 7-day cleanup job configured in Railway.

---
# Stage 5 — Tournaments
Build the paid tournament feature on top of the stable auth + sets foundation.
- `/tournaments` — browse page + create CTA
- `/tournaments/new` — multi-step creation wizard (details → teams → review), auth-gated
- Monnify payment initiation (`POST /api/tournaments/[id]/initiate-payment`)
- Monnify webhook handler (`POST /api/webhooks/monnify`) with HMAC-SHA512 verification
- Tournament status polling (`GET /api/tournaments/[id]/status`, 3s interval, max 30s)
- `DRAFT → ACTIVE` tournament lifecycle on payment confirmation
- `/tournaments/[id]` — public view: Round Robin (fixture list + live league table) and Single Elimination (bracket)
- `/tournaments/[id]/manage` — host control panel, auth-gated, result entry with per-format unlock logic
- `TOURNAMENT_UPDATE` WebSocket broadcast from tournament manage actions
- `/account` billing section — tournament list + payment status
- 24-hour draft cleanup cron job on Railway

**Exit criteria:** Full tournament flow works end-to-end in Monnify test mode (create → pay → manage → complete).

---
# Stage 6 — Migration & Cutover
Swap `qset.qballxi.com` from the old deploy to the new one.

- `localStorage` migration banner (detect old `GameState` key on first load, offer to seed a new server session)
- Old route redirects: `/game` → `/sets/[code]`, `/` → `/sets` or `/`
- PostHog continuity check (existing `PUBLIC_POSTHOG_API_KEY` env var, no code changes needed)
- Smoke test the full flow on the new Railway service against production DB
- DNS cutover: point `qset.qballxi.com` to new Railway service
- Monitor for 48 hours, keep old deploy on standby

**Exit criteria:** `qset.qballxi.com` serves the new app, no regressions, old sessions gracefully handled.

---
