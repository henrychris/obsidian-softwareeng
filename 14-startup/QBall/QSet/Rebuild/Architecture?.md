## Project Structure

```
// /dev/null/structure.md#L1-60
src/
├── lib/
│   ├── prisma.ts              // Prisma singleton (already done)
│   ├── auth.ts                // better-auth config
│   ├── auth-client.ts         // browser-side auth client
│   ├── session-state.ts       // builds the full SessionState object
│   └── websocket.ts           // broadcast helper
│
├── server/
│   ├── middleware.ts           // host token validation, shared guards
│   └── procedures/
│       ├── sessions.ts         // session business logic
│       ├── teams.ts
│       ├── matches.ts
│       ├── queue.ts
│       └── events.ts          // undo/redo
│
└── routes/
    ├── +layout.svelte
    │
    ├── api/
    │   ├── sessions/
    │   │   └── +server.ts              // POST /api/sessions
    │   │
    │   └── sessions/[code]/
    │       ├── +server.ts              // GET  /api/sessions/[code]
    │       ├── end/
    │       │   └── +server.ts          // POST /api/sessions/[code]/end
    │       ├── undo/
    │       │   └── +server.ts          // POST /api/sessions/[code]/undo
    │       ├── redo/
    │       │   └── +server.ts          // POST /api/sessions/[code]/redo
    │       ├── teams/
    │       │   ├── +server.ts          // POST /api/sessions/[code]/teams
    │       │   └── [teamId]/
    │       │       └── +server.ts      // PATCH / DELETE
    │       ├── matches/
    │       │   └── [matchId]/
    │       │       └── +server.ts      // PATCH (record result)
    │       ├── queue/
    │       │   └── +server.ts          // PATCH (reorder)
    │       └── timer/
    │           └── +server.ts          // POST (start/stop/reset)
    │
    └── sets/
        └── [code]/
            ├── +page.server.ts         // initial load
            └── +page.svelte            // UI
```

---

## The Core Patterns

### Pattern 1 — The session state builder

Every mutation ends by broadcasting the same shape to all connected clients. Centralise that query so it's never duplicated.

```ts
// /dev/null/src/lib/session-state.ts#L1-50
import { prisma } from './prisma';

export async function getSessionState(sessionId: string) {
  const session = await prisma.session.findUniqueOrThrow({
    where: { id: sessionId },
    include: {
      teams: { orderBy: { createdAt: 'asc' } },
      matches: { orderBy: { createdAt: 'asc' } },
      queueEntries: { orderBy: { position: 'asc' }, include: { team: true } },
    },
  });

  return session;
}

export type SessionState = Awaited<ReturnType<typeof getSessionState>>;
```

This return type becomes the contract between your server and your Svelte stores. Every endpoint returns it; every WebSocket broadcast sends it.

---

### Pattern 2 — Host token middleware

SvelteKit doesn't have Express-style middleware, but you can write a plain async function and call it at the top of any handler.

```ts
// /dev/null/src/server/middleware.ts#L1-40
import { prisma } from '$lib/prisma';
import { error } from '@sveltejs/kit';
import type { RequestEvent } from '@sveltejs/kit';

export async function requireHost(event: RequestEvent) {
  const token = event.request.headers.get('x-host-token');

  if (!token) {
    error(401, 'Missing host token');
  }

  const session = await prisma.session.findUnique({
    where: { hostToken: token },
  });

  if (!session) {
    error(401, 'Invalid host token');
  }

  if (session.status === 'ENDED') {
    error(403, 'Session has ended');
  }

  return session;
}
```

---

### Pattern 3 — An API endpoint

```ts
// /dev/null/src/routes/api/sessions/[code]/teams/+server.ts#L1-40
import { json, error } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { prisma } from '$lib/prisma';
import { requireHost } from '$server/middleware';
import { getSessionState } from '$lib/session-state';
import { broadcast } from '$lib/websocket';
import { z } from 'zod';

const schema = z.object({
  name: z.string().min(1).max(50),
});

export const POST: RequestHandler = async (event) => {
  const session = await requireHost(event);

  const body = await event.request.json();
  const { name } = schema.parse(body);

  await prisma.$transaction(async (tx) => {
    const team = await tx.team.create({
      data: { name, sessionId: session.id },
    });

    const lastEntry = await tx.queueEntry.findFirst({
      where: { sessionId: session.id },
      orderBy: { position: 'desc' },
    });

    await tx.queueEntry.create({
      data: {
        sessionId: session.id,
        teamId: team.id,
        position: (lastEntry?.position ?? -1) + 1,
      },
    });

    await tx.sessionEvent.create({
      data: {
        sessionId: session.id,
        type: 'TEAM_ADDED',
        payload: { teamId: team.id, name },
      },
    });
  });

  const state = await getSessionState(session.id);
  broadcast(session.id, { type: 'STATE_UPDATE', state });

  return json(state);
};
```

The pattern is always: **validate → guard → mutate in a transaction → fetch fresh state → broadcast → return state**.

---

### Pattern 4 — The page server load

```ts 
// /dev/null/src/routes/sets/[code]/+page.server.ts#L1-35
import { error } from '@sveltejs/kit';
import type { PageServerLoad } from './$types';
import { prisma } from '$lib/prisma';
import { getSessionState } from '$lib/session-state';

export const load: PageServerLoad = async ({ params, cookies }) => {
  const session = await prisma.session.findUnique({
    where: { code: params.code },
  });

  if (!session) error(404, 'Session not found');

  const state = await getSessionState(session.id);

  // The host token lives in sessionStorage client-side, but on first load
  // we can check a cookie as a fallback so the host gets the right UI.
  const hostToken = cookies.get(`host_token_${session.id}`);
  const isHost = hostToken === session.hostToken;

  return {
    state,
    isHost,
  };
};
```

---

### Pattern 5 — Svelte store wired to WebSocket

```ts 
// /dev/null/src/routes/sets/[code]/+page.svelte#L1-45
<script lang="ts">
  import { writable } from 'svelte/store';
  import type { PageData } from './$types';
  import type { SessionState } from '$lib/session-state';

  let { data }: { data: PageData } = $props();

  const state = writable<SessionState>(data.state);

  // WebSocket: replace local state wholesale on every message
  import { onMount } from 'svelte';
  onMount(() => {
    const ws = new WebSocket(`/ws/sessions/${data.state.id}`);

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'STATE_UPDATE') {
        state.set(msg.state);
      }
      if (msg.type === 'SESSION_ENDED') {
        // redirect to summary
      }
    };

    return () => ws.close();
  });
</script>
```

---

### Pattern 6 — The client calling an endpoint

```ts 
// /dev/null/src/lib/api.ts#L1-30
// A tiny typed fetch wrapper — no oRPC needed.

export async function apiPost<T>(
  path: string,
  body: unknown,
  hostToken?: string
): Promise<T> {
  const res = await fetch(path, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(hostToken ? { 'x-host-token': hostToken } : {}),
    },
    body: JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.message ?? `Request failed: ${res.status}`);
  }

  return res.json();
}
```

---
## Key Design Decisions for Your Setup

**`sessionStorage` for the host token.** On session creation, the server returns the `hostToken`. The client stores it in `sessionStorage` and attaches it as an `x-host-token` header on every mutating request. Observers never have it, so they naturally get a read-only view. When a host refreshes, the token survives (unlike `localStorage` on a different tab, and unlike a cookie that every tab shares).

**No oRPC, but keep the procedures folder.** Even without oRPC, keeping business logic in `src/server/procedures/` rather than directly in `+server.ts` files keeps your route handlers thin and your logic testable. The `+server.ts` file just validates input, calls the procedure, and returns the result.

**Zod at the boundary.** Validate every request body with Zod in the route handler before any DB work. Throw early, throw clearly.

**WebSockets.** With `@sveltejs/adapter-node`, you can access the raw HTTP server and attach a `ws` WebSocket server to it. A `Map<sessionId, Set<WebSocket>>` is all you need for the broadcast map. This lives in `src/lib/websocket.ts` and is initialised once in `src/hooks.server.ts`.

**Undo/redo stays purely server-side.** Exactly as you designed — the client sends `POST /api/sessions/[code]/undo`, gets back the full new state, replaces the store. The client only needs to know whether there's anything to undo (you can include `canUndo` and `canRedo` booleans in the state response).