# Chapter notes — Part 2, chapters 2.2–2.8

Provenance for the seven core-loop chapters this feature produced. It replaces
the `DRAFT-HEADER` blocks that lived inside `relay-tutorial/drafts/part-2/`.

**Why this file exists.** Those drafts were the working copies: feature 020
wrote all seven chapters *ahead of* their platform code, so each carried a
header recording what still needed verifying (`«TBV»` markers) and, later, how
each item was resolved. After publication the drafts became byte-identical
duplicates of the published pages, tracked by nothing and checked by nothing.
The directory was deleted; this file keeps what was worth keeping.

**What is measured and what is remembered.** Everything under *Fences*,
*Translated* and *Battery* below was extracted mechanically from the published
pages just now, and the word counts match the retired `draft-battery.txt` row
for row — which is the evidence that the drafts and the published pages had
identical bodies. The *Findings* sections are reconstructed from this session's
working record; where a chapter's findings predate that record, it says so
rather than inventing them.

**One column changed meaning.** `draft-battery.txt`'s `tickLines` values came
from a metric defined in an earlier pass that could not be reproduced from the
files; the counts here are changed lines inside diff fences. Every other column
is identical.

## 2.2 — The write path

- **Published**: `app/(en)/part-2/chapter-02/the-write-path/`
- **Translated**: yes (vi)
- **Tag**: `part2-ch2` — intended; Part 2's tags are not yet cut
- **Battery**: 3070 words · Why 3 · Skip 1 · Fwd 1 · Chk 1 · Trap 1 · Figures 3 · 135 changed lines in diff fences
- **Fences, whole files** (9): `services/api/src/db/repository.naive.ts`, `services/api/src/db/repository.ts (excerpt)`, `services/api/src/messages/messages.controller.ts`, `services/api/src/messages/messages.schema.ts`, `services/api/src/messages/zod-validation.pipe.ts`, `services/api/src/messages/environment-context.guard.ts`, `services/api/src/messages/messages.service.ts`, `services/api/src/messages/messages.module.ts`, `services/api/src/messages/messages.itest.ts`
- **Fences, amendments** (4): `services/api/src/db/repository.ts`, `services/api/src/db/repository.itest.ts`, `services/api/package.json`, `services/api/src/protocol-error.filter.ts`

### Findings
- Four defects in the draft's own code, found by running it: an unused `Headers` import (lint), `zod` missing from the api's dependencies, TS1272 (a type used in a decorated signature needs `import type`), and `MessagesModule` never registered in `AppModule` — which made every route 404.
- A bare `ON CONFLICT DO NOTHING` disarmed DR-01: forcing a sequence collision silently dropped a message. Fixed by attaching the conflict clause only when an idempotency key exists.
- Duplicate retries burned sequence numbers (`last_sequence=3` with one row); the channel UPDATE moved below the insert.
- The naive concurrency test did not reproduce the race — plain `Promise.all` gave a clean result. A gate promise held between read and write makes it fail every time.
- `MessageRow` and `ChannelNotFoundError` were used but never defined in the draft; both became real fences.

## 2.3 — Send it twice

- **Published**: `app/(en)/part-2/chapter-03/send-it-twice/`
- **Translated**: yes (vi)
- **Tag**: `part2-ch3` — intended; Part 2's tags are not yet cut
- **Battery**: 2514 words · Why 2 · Skip 1 · Fwd 1 · Chk 1 · Trap 1 · Figures 3 · 230 changed lines in diff fences
- **Fences, whole files** (1): `services/api/src/messages/idempotency.itest.ts (excerpt)`
- **Fences, amendments** (4): `services/api/src/messages/messages.schema.ts`, `services/api/src/messages/messages.service.ts`, `services/api/src/db/repository.ts`, `services/api/src/db/repository.itest.ts`

### Findings
- Not recovered. 2.3 was implemented and translated before this session's record begins, and its DRAFT-HEADER was lost with the directory. The chapter itself is intact and its claims are checkable against the published fences.

## 2.4 — History that pages

- **Published**: `app/(en)/part-2/chapter-04/history-that-pages/`
- **Translated**: yes (vi)
- **Tag**: `part2-ch4` — intended; Part 2's tags are not yet cut
- **Battery**: 2757 words · Why 3 · Skip 1 · Fwd 1 · Chk 1 · Trap 1 · Figures 2 · 161 changed lines in diff fences
- **Fences, whole files** (4): `services/api/src/db/history-drift.itest.ts`, `services/api/migrations/0001_drop_redundant_index.sql`, `services/api/src/messages/cursor.ts`, `services/api/src/messages/cursor.test.ts`
- **Fences, amendments** (5): `services/api/src/db/repository.ts`, `services/api/src/db/schema.ts`, `services/api/src/messages/messages.schema.ts`, `services/api/src/messages/messages.service.ts`, `services/api/src/messages/messages.controller.ts`

### Findings
- `EXPLAIN` contradicted the chapter: the planner used `Index Scan Backward using messages_channel_id_sequence_unique`, not the dedicated DESC index. Dropping that index changed neither plan nor cost (`0.41..5.04` either way), which produced the SAD §6.3 amendment and migration `0001_drop_redundant_index.sql`.
- The offset-drift demonstration moved into `history-drift.itest.ts` as a test-local helper rather than shipping a `listMessagesByOffset` nobody should call.
- The gap variant would not reproduce by deleting the oldest row; it needed a row inside page one's range (`page1[25]`).

## 2.5 — The socket

- **Published**: `app/(en)/part-2/chapter-05/the-socket/`
- **Translated**: yes (vi)
- **Tag**: `part2-ch5` — intended; Part 2's tags are not yet cut
- **Battery**: 2885 words · Why 3 · Skip 1 · Fwd 1 · Chk 1 · Trap 2 · Figures 3 · 68 changed lines in diff fences
- **Fences, whole files** (9): `services/gateway/src/auth.ts`, `services/gateway/src/session.ts`, `services/gateway/src/registry.ts`, `packages/protocol/src/internal.ts`, `services/gateway/src/api-client.ts`, `services/api/src/internal/internal.controller.ts`, `services/api/src/internal/internal.module.ts`, `scripts/ws-walk.mjs`, `services/gateway/src/session.test.ts`
- **Fences, amendments** (7): `services/gateway/package.json`, `services/gateway/src/main.ts`, `packages/protocol/src/index.ts`, `services/api/src/app.module.ts`, `services/api/src/messages/messages.module.ts`, `package.json`, `eslint.config.mjs`

### Findings
- An empty-claim auth hole: `typeof payload.env === "string"` accepts `""`, so a token with an empty environment claim opened a tenant-less session. Found by a test of mine that timed out; fixed with non-empty checks and written up as the chapter's TRAP.
- `connection.ack` latency measured at 38–40 ms against EIR-WS-03's 1,000 ms budget.
- The `ws` upgrade wiring was verified against ws 8.21.1: `new WebSocketServer({ noServer: true })` plus a manual `server.on("upgrade")`, so the token is checked while the connection is still a pending upgrade.
- eslint needed `globals.nodeBuiltin` for `scripts/**/*.mjs`; `jose` and `ws` became root devDependencies for the walk script.

## 2.6 — Two servers, one conversation

- **Published**: `app/(en)/part-2/chapter-06/two-servers-one-conversation/`
- **Translated**: yes (vi)
- **Tag**: `part2-ch6` — intended; Part 2's tags are not yet cut
- **Battery**: 3746 words · Why 4 · Skip 1 · Fwd 1 · Chk 1 · Trap 2 · Figures 4 · 352 changed lines in diff fences
- **Fences, whole files** (5): `scripts/split-brain.mjs`, `services/gateway/src/fanout.ts`, `services/api/src/internal/internal.itest.ts`, `services/gateway/vitest.integration.config.mts`, `services/gateway/src/fanout.itest.ts`
- **Fences, amendments** (8): `packages/protocol/src/internal.ts`, `services/api/src/messages/messages.service.ts`, `services/api/src/internal/internal.controller.ts`, `services/api/src/messages/messages.controller.ts`, `services/gateway/src/session.ts`, `services/gateway/src/main.ts`, `services/gateway/package.json`, `services/gateway/src/session.test.ts`

### Findings
- `ioredis` v6 is CommonJS and the gateway is ESM, so the default import is not constructable (TS2351) — the named import is required.
- Every message 2.5 wrote through the socket had `user_id` NULL: the internal route resolved the sender for authorization and dropped it. Fan-out cannot name a sender it never recorded, so the write path was fixed forward.
- Idempotent storage is not idempotent delivery: a recognised retry would have been republished to every member. `duplicate` now crosses the internal boundary while the public wire still hides it.
- Awaiting `fanout.subscribe()` before `connection.ack` made a stopped broker block the handshake (EIR-WS-03). Fixed and locked in by a test whose stub subscribe never settles.
- 2.5 shipped the internal routes with tests only on the gateway's side, where the api was a stub; `internal.itest.ts` closes that. Writing it showed that a still-running 2.5 gateway rejected the new response, because `z.strictObject` makes an added field breaking in both directions.

## 2.7 — The tunnel

- **Published**: `app/(en)/part-2/chapter-07/the-tunnel/`
- **Translated**: yes (vi)
- **Tag**: `part2-ch7` — intended; Part 2's tags are not yet cut
- **Battery**: 3628 words · Why 3 · Skip 1 · Fwd 1 · Chk 1 · Trap 1 · Figures 3 · 677 changed lines in diff fences
- **Fences, whole files** (6): `services/gateway/src/resume.ts`, `services/api/src/internal/backfill.controller.ts`, `services/gateway/src/resume.test.ts`, `services/gateway/src/resume.itest.ts`, `services/api/src/internal/backfill.itest.ts`, `scripts/tunnel-walk.mjs`
- **Fences, amendments** (9): `packages/protocol/src/internal.ts`, `services/api/src/db/repository.ts`, `services/api/src/messages/messages.service.ts`, `services/api/src/internal/internal.module.ts`, `services/gateway/src/registry.ts`, `services/gateway/src/api-client.ts`, `services/gateway/src/session.ts`, `services/gateway/src/session.test.ts`, `services/gateway/src/fanout.itest.ts`

### Findings
- Both naive orderings were measured, not asserted: no buffer gives `[43, 42, 43]` (doubled and out of order); subscribing after the fetch gives `[42]` (the silent gap).
- 2.6's rule (never await the subscribe on connect) and 2.7's step 1 (the subscription must exist before the backfill) contradict each other. Resolved with a deadline plus `resume_ok: false`, which became the single degrade answer for a corrupt cursor, an unavailable api, and buffer overflow.
- The socket's `close` listener was registered after the ack, so a socket dying during a resume leaked its registry entry and its fabric subscription. Listeners now precede the resume.
- `resume.itest.ts` and 2.6's `fanout.itest.ts` shared a hard-coded channel id on one broker and heard each other (`[42, 43, 6]`). Both now mint per-run subjects — 2.1's per-suite-environment lesson applied to pub/sub.
- 2.5 discussed `internal.module.ts` without ever fencing it; added to 2.5 in both locales so 2.7's diff had a real pre-image.

## 2.8 — Milestone: the Tuan test

- **Published**: `app/(en)/part-2/chapter-08/milestone-the-tuan-test/`
- **Translated**: yes (vi)
- **Tag**: `part2-ch8` — intended; Part 2's tags are not yet cut
- **Battery**: 3157 words · Why 2 · Skip 1 · Fwd 1 · Chk 1 · Trap 1 · Figures 3 · 77 changed lines in diff fences
- **Fences, whole files** (5): `packages/e2e/package.json`, `packages/e2e/tsconfig.json`, `packages/e2e/vitest.integration.config.mts`, `packages/e2e/src/harness.ts`, `packages/e2e/src/tuan.itest.ts`
- **Fences, amendments** (6): `turbo.json`, `package.json`, `services/api/src/db/repository.ts`, `services/api/src/messages/messages.service.ts`, `services/api/src/messages/messages.itest.ts`, `services/gateway/src/session.ts`

### Findings
- The suite passed with 2.7's buffer deleted. As first scripted, the dispatcher stopped talking during the reconnect, so nothing was published inside the resume window and the assertion proving 2.7 proved nothing. Fixed by making the script honest; the sabotage now fails 5 runs out of 5. This became the chapter's TRAP.
- Four defects found in earlier chapters: history answered 200-empty where send answers 404; 2.7's close path leaked an unhandled rejection; Turborepo 2's strict env mode silently dropped the store coordinates; and `^build` does not build packages a suite merely boots.
- The harness discarded child stdio, which turned "memberships returned 500" into "no connection.ack within 5000ms". Child logs are now captured and attached to handshake failures.
