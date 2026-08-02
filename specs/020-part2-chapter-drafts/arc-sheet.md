# Arc Sheet — Part 2 drafts (feature 020)

Part-level design memo. Not published. Every draft draws names, shapes,
and sequencing from here; T011's continuity pass checks against it.

## A. The 2.8 journey script skeleton (FIRST — FR-009)

The Tuan test (`packages/e2e`, `tuan.itest.ts`, integration lane), staged
steps → the chapter that must supply each capability:

1. Boot compose Postgres+Redis; migrate; create environment + two users
   (dispatcher D, driver T) + one channel, both members — **2.1**.
2. Boot the api (built, ephemeral port) and TWO gateway instances G1, G2 —
   **1.4/2.5/2.6**.
3. D connects to G1, T connects to G2 (JWT dev tokens; `connection.ack`
   carries identity + resume cursor) — **2.5** (EIR-WS-01/03).
4. D sends "which entrance?" via `message.send` on G1; T receives
   `message.created` on G2 (cross-instance) — **2.2** (write path),
   **2.6** (fan-out, FR-RTM-02).
5. T types "B2, north ramp", sends — and the socket is KILLED before any
   ack (mid-send; idempotency key already generated) — **2.3**
   (FR-SDK-06's key-at-send-time, FR-MSG-05's honest un-acked state).
6. Tunnel window: D sends "ok, coming down" while T is offline — **2.2**.
7. T reconnects to G1 (either instance — no stickiness) with resume
   cursor; retries "B2, north ramp" with the ORIGINAL key — **2.7**
   (resume: subscribe-first, buffer, backfill, flush) + **2.3**
   (duplicate recognized, original returned).
8. Assertions: T has exactly one "B2, north ramp" (exactly-once,
   FR-MSG-04); both clients see identical order by seq (FR-MSG-03) with
   D's reply after T's message iff seq says so; no gaps, no duplicates
   across backfill+live (the §5.2 race closed); a third environment's
   channel remains invisible throughout (constitution I ride-along).
9. Close: quote SRS §7.3 Phase 1 exit verbatim — "Two clients exchange
   messages through the public API, surviving a forced disconnect with
   correct ordering and no duplicates" — declared met «TBV: suite run».

## B. Shared codebase story (all drafts draw from this)

**Tenant context before Part 3 (RECORDED DECISION, every chapter restates
briefly)**: real keys/JWT-minting arrive in 3.1/3.2. Until then the api
accepts `X-Relay-Environment: <environment_id>` on public routes as a
dev-mode scaffold (guard `EnvironmentContextGuard` resolves it, request
carries it to the request-scoped repository), and gateway dev tokens are
HS256 JWTs signed with `RELAY_DEV_JWT_SECRET` (default `dev-secret`),
claims `{ sub: <user external_id>, env: <environment_id> }`. Both are
explicitly Part-3-replaceable seams.

**Request-scoped repository (2.2 wiring, forecast in 019's 1.4/2.1)**:
`RepositoryModule` provides `Repository` at `Scope.REQUEST` via factory
`(db, ctx) => new Repository(db, ctx.environmentId)`; the class itself
stays the plain 2.1 class.

**Endpoints (api, NestJS, continuing 1.4 idioms — controller + zod pipe
from @relay/protocol shapes, ProtocolErrorFilter envelope)**:
- 2.2 `POST /v1/channels/:channelId/messages` body `{text, metadata?}` →
  201 `{id, channel_id, seq, text, created_at}`.
- 2.3 body gains `idempotency_key?`; repeat → 200-semantics per FR-MSG-04
  (chapter records the 201-equivalent wording).
- 2.4 `GET /v1/channels/:channelId/messages?cursor&direction&limit` →
  `{messages, next_cursor, prev_cursor}`; limit cap 200 (FR-MSG-09);
  cursor = base64url(`s:<seq>`) — opaque per constitution V (DECISION).
- 2.5 internal: `POST /internal/messages` (gateway sends, ADR-05; trusts
  gateway, env/user via headers — Part-3 hardening named).
- 2.7 internal: `POST /internal/backfill` `{userExternalId, cursors}` →
  per-channel `{messages, truncated}` cap 500 (FR-RTM-04).

**Repository additions** (all Drizzle inside the layer; every method
tenant-scoped as 2.1 built):
- 2.2 `sendMessage(channelId, {userId?, text, metadata?})`:
  `db.transaction` → channel `SELECT … FOR UPDATE` scoped by environment
  (`.for("update")`) → seq = last_sequence + 1 → UPDATE channel → INSERT
  message → return row. Ack-after-commit lives in the service returning
  only post-transaction.
- 2.3 same method gains `idempotencyKey?`: INSERT
  `.onConflictDoNothing()` against the DR-03 partial index («TBV: exact
  drizzle conflict-target syntax for a partial unique index»), zero-row
  result → SELECT original → `{message, duplicate: true}`.
- 2.4 `listMessages(channelId, {afterSeq?, beforeSeq?, limit})` riding
  `messages_channel_seq` (index-order scan, FR-MSG-09).
- 2.7 `backfill(userExternalId, cursors)` → per-membership seq>cursor,
  LIMIT 501 → truncated flag.

**Gateway (frameworkless, ws 8.21.1, jose 6.2.7, ioredis 6.0.0 — intended
pins; ioredis over node-redis for its subscriber-mode ergonomics, one-line
rationale in 2.6)**:
- 2.5 `session.ts` (WS upgrade on `/v1/ws?token=`, jose verify, 4001 on
  bad token per EIR-WS-05, `connection.ack` within 1s per EIR-WS-03,
  ping/30s ×2 per EIR-WS-04), `registry.ts` (in-memory conn registry +
  membership map fetched from api), frames via @relay/protocol safeParse
  (`error` frame + 4002 on garbage). Sends: `message.send` → internal
  POST → `message.ack {seq}` (§5.1).
- 2.6 `fanout.ts`: publisher (the send-handling gateway publishes
  `chan:{channel_id}` after ack, §5.1) + per-instance subscriber
  delivering `message.created` to local members. Lossy on purpose
  (ADR-07); REST-originated sends' fan-out recorded as completed by the
  outbox spine (3.3) — DECISION, one sentence.
- 2.7 `resume.ts`: connect params gain `cursor` (per-channel map);
  subscribe FIRST → buffer live → backfill via internal POST → emit
  backfill in seq order → flush buffer dropping `seq ≤` high-water mark →
  live. The §5.2 timeline verbatim.

**Fence inventories / amendments per draft (header `fences` /
`amendments`)**:
- 2.2 fences: messages module/controller/dto/service files; amendments:
  `services/api/src/db/repository.ts` (diff: +sendMessage),
  `services/api/src/app.module.ts` (diff: +MessagesModule +guard).
- 2.3 amendments: repository.ts (idempotency leg), messages controller/
  service (key plumbed); fences: the retry itest.
- 2.4 fences: cursor codec, history controller additions; amendments:
  repository.ts (+listMessages), messages.controller.ts.
- 2.5 fences: gateway session/registry/auth files, api internal module;
  amendments: `services/gateway/package.json` (+ws +jose),
  `services/gateway/src/main.ts` (WS server wiring), api app.module.
- 2.6 fences: gateway fanout.ts; amendments: gateway package.json
  (+ioredis), session wiring.
- 2.7 fences: gateway resume.ts, api backfill files; amendments: session
  (cursor param), repository.ts (+backfill).
- 2.8 fences: `packages/e2e/{package.json,vitest.integration.config.mts,
  src/tuan.itest.ts}`; DECISION: dev-only e2e package under `packages/`
  (workspace globs unchanged; never published).

**Lane commands every chapter claims**: `pnpm lint && pnpm typecheck &&
pnpm test` (Docker-free, turbo) + `pnpm --filter <pkg> test:integration`
against compose (2.8: `pnpm --filter @relay/e2e test:integration`).

## C. Source extracts pinned during T001

- §7.3 Phase 1 exit (verbatim): "Two clients exchange messages through
  the public API, surviving a forced disconnect with correct ordering and
  no duplicates".
- §5.2 race (verbatim core): "subscribe-then-backfill can deliver a live
  frame that is also in the backfill (duplicate); backfill-then-subscribe
  can drop a message that lands in the gap." Buffer rule: subscribe
  first → buffer → backfill → flush discarding `seq ≤` high-water mark;
  cap 500 → `truncated: true` (FR-RTM-04).
- §5.1 decisions: ack after commit never before (FR-MSG-05); idempotency
  at storage via DR-03 (survives restarts, cross-instance, FR-MSG-04);
  row-lock scope = one channel = FR-MSG-03's guarantee; outbox named for
  3.3.
- Journey 4: "B2, north ramp" typed as signal dies; clock icon
  (`sending`, FR-SDK-05); key generated BEFORE failure (FR-SDK-06);
  naive retry → dispatcher gets it three times; reconnect = backoff +
  jitter (forty drivers, thundering herd), cursor resume (FR-RTM-03),
  flush queued send with ORIGINAL key, seq puts reply below (FR-MSG-03),
  600-message backlog → truncate + refetch (FR-RTM-04).
- FR rows quoted by drafts: FR-MSG-02/03/04/05/09, FR-RTM-01/02/03/04,
  EIR-WS-01/02/03/04/05, CON-02.
- Protocol surface (1.3, live): frames connection.ack, message.send,
  message.ack, message.created, message.updated, message.deleted,
  membership.changed, presence.changed, typing, error; close codes
  4001/4002/4008/4009.
- Intended pins: ws 8.21.1 · jose 6.2.7 · ioredis 6.0.0 (chosen over
  node-redis 6.2.0) — registry-checked 2026-08-02, TBV at install.
- Freeze snapshots: sitemap 34 URLs (scratchpad/sitemap-pre-feature.txt,
  re-verified post-019); build 41/41 pages.
