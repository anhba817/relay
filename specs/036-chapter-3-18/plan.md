# Implementation Plan: chapter 3.18 — the message that never arrived

**Branch**: `main` | **Date**: 2026-08-26 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/036-chapter-3-18/spec.md`

## Summary

An outsider who sends a message over REST and waits for it on a socket waits forever. The write
commits, the sender gets a `201`, and nobody hears about it — because the only code in the
repository that publishes to the live fan-out is the gateway's own socket handler
(`session.ts:651`). Chapter 3.14 recorded this as a verdict without fixing it; `docs/05-sad.md`
has drawn the missing edge since before the api existed.

The fix is one publisher. The fan-out fabric, the payload schema, the gateway's subscription and
the cross-instance delivery test all exist and all work today (R3, R5, R7). This chapter adds the
api as a second publisher onto a subject the gateway currently owns alone, moves the subject
*grammar* — `subjectFor` alone; not the payload type, which is already shared, and not
`DEFAULT_REDIS_URL`, which is declared in three files and is configuration rather than protocol —
into `packages/protocol`, and mirrors the two conditions that guard the gateway's publish: a
recognised retry is not republished, and a tombstone is not a creation.

The api writes its own ten-line publisher rather than reusing the gateway's, and R10 is why. The
gateway's client is built with default ioredis options and no `error` listener; the api's own
rate-limit store is built with `maxRetriesPerRequest: 0` and a one-second `connectTimeout`,
because — in its own words — *"an outage that instead adds seconds to every request has refused it
in a slower way, and NFR-PRF-02 asks for a p95 under 150 ms."* A publisher on the request path
takes the limiter's options, not the fan-out's.

**The interesting part is not the publish. It is that the documented ordering cannot be copied.**
The gateway sends its ack as a socket frame and *then* awaits the publish; §5.1's ordering —
durability, the sender's confirmation, everybody's copy — is a sequence it can actually perform
because it has two channels. REST has one. The response *is* the ack, so there is no "after the
ack" inside a request handler. This chapter decides what that ordering means for a transport that
cannot honour it literally, which is the same shape as chapter 3.17's phase-4 finding: a
documented order that was not achievable as written.

## Technical Context

**Language/Version**: TypeScript 5.x on Node 22, ESM throughout

**Primary Dependencies**: `ioredis` (already in the api via `limits/store.ts` — no new
dependency, R6), NestJS 11 (api only), zod at boundaries, Vitest 4

**Storage**: PostgreSQL is unchanged. This feature adds no column, no table, no migration.
Redis pub/sub carries the fan-out and is not a source of truth (principle IV).

**Testing**: `pnpm turbo run test` (unit), `pnpm test:integration` (`--concurrency=1`, 240 s
budget, 589 tests at 3.17's close), `pnpm test:outsider` (the sealed lane — where the failing
scenario actually lives), `pnpm coverage` (per-file ratchets)

**Target Platform**: Linux server, three services (api, gateway, outbox relay)

**Project Type**: A tutorial chapter that amends a running platform. Two repositories change
together: `relay-platform` gets the publisher, `relay-tutorial` teaches it in both locales and
fences every changed path.

**Performance Goals**: NFR-PRF-02 (REST write latency, p95 < 150 ms) is the budget the publish
lands in if the api awaits it. NFR-PRF-01 (send acknowledged → recipient receipt, p95 < 250 ms)
is the budget it lands in if the api detaches it. **Both are affected by a decision this plan
has to make, so the publish must be measured, not assumed cheap.**

**Constraints**: `exactOptionalPropertyTypes: true`. The fan-out payload must stay byte-compatible
with what the gateway publishes today — `messageSchema` validates on the delivery side, and a
seventh field or a missing `user` is dropped rather than forwarded (`fanout.itest.ts:128`).

**Scale/Scope**: See the two counts below. They are two counts and this plan keeps them apart.

### The two file counts

Chapter 3.15/3.16 conflated these and paid eight revisions for it. One column drives the word
estimate; the other drives the fence chain, and neither predicts the other.

| | teaches | fences |
|---|---|---|
| `packages/protocol/src/fanout.ts` (new — `subjectFor` only) | yes | yes |
| `packages/protocol/src/fanout.test.ts` (new — the grammar's own test) | no | **yes** |
| `services/gateway/src/fanout.ts` (consumes it instead of defining it) | yes | yes |
| the api's publisher module | yes | yes |
| the api's send path (the publish site) | yes | yes |
| the api's module wiring | yes | yes |
| `services/api/src/main.ts` or config (the Redis URL) | maybe | yes |
| the api-side publish test | yes | yes |
| the cross-service delivery test | yes | yes |
| the outsider scenario (3.14's verdict, now passing) | yes | yes |
| `packages/protocol/src/index.ts` (a re-export) | no | **yes** |
| the gateway's fanout tests (import path moved) | no | **yes** |
| `services/api/package.json` (if `ioredis` is not yet a direct dep) | no | **yes** |
| `docs/07-tutorial-plan.md` (the row goes from planned to shipped) | no | n/a |

**Nine taught, thirteen fenced, and the three that diverge are the ones a chapter forgets.** A
re-export and a moved import path change no behaviour and teach nothing, and the chain does not
care: a claimed path's state must equal the repository's. The count above is a first count and
will be wrong. `git diff --name-only` against `pnpm check:fences` at the end is what settles it —
that comparison split the count in 3.16 and found two files in no bucket.

### The word estimate, and why the rate it would have used was discarded

    chapter   prose words (reconstructed)   taught files   words/file
    3.15                     3,070                   20        153.5
    3.16                     4,011                   26        154.3
    3.17                     3,134                   37         84.7

3.15 and 3.16 agree to within 1% and 3.17 falls 45% below them. **A per-file word rate is not an
estimator.** 3.17 taught 37 files to make one argument; the prose tracks arguments, not paths.

Two cautions on the table itself. The reconstructed counts run 4–6% above the figures recorded in
`baseline.txt` for the same chapters (2,947 / 3,800 / 2,962) — consistently high, so the ratios
hold, but **the instrument that produced the recorded numbers no longer exists in the repository**
and this is a reconstruction, not that instrument. Whatever counts 3.18 should re-count all three.

3.18 has a small surface and five distinct arguments: the ordering that cannot be copied, the two
NFRs pulling opposite ways, the subject grammar's move, the recovery property under a lost
publish, and the membership question in R5. Estimate **2,200–2,800 prose words**, from the
arguments. A file rate would have predicted ~1,300 and been wrong for the reason above.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principle IV — Single Writer, Single Source of Truth: this is the gate.**

> "The live fan-out fabric is permitted to be lossy (at-most-once) precisely because durability
> and resume live in PostgreSQL sequences and cursors (SAD ADR-07). **Any new delivery mechanism
> MUST preserve this recovery property.**"

A REST-sent message published at-most-once must still reach a client that missed the publish, by
resume. It does — the row and its `seq` are committed before anything is published — but this
chapter must *demonstrate* it rather than reason about it. The test: make the publish fail, watch
the send succeed, reconnect, and find the message in the backfill. That single test is the
constitutional argument for the whole feature, and it is also FR-010 and FR-011's test.

The rest of IV is satisfied by not being touched: the api remains the only writer to PostgreSQL,
and nothing in Redis becomes a source of truth. Pub/sub fan-out is named in IV's own list of
permitted ephemeral state.

**Principle III — Two Data Paths, Never Crossed: not engaged, and worth saying why.** The
fan-out publish is operational delivery, not an analytical event, so III's "never synchronously on
the request path" does not apply to it. The similarity is close enough to mislead: this feature
does put a synchronous Redis call on a request path, and a reader who has III in mind will flag
it. The chapter should answer that objection rather than let it stand.

**Principle VI — Requirement-Driven, Test-Verified Delivery: satisfied by citation, not by
amendment.** FR-RTM-01 is the unmet clause (not FR-RTM-05, which the tutorial plan's row names —
see spec FR-001), and `docs/05-sad.md:138` already draws the edge. Chapter 3.17's gate was an SRS
amendment because the SRS had no bot concept; **there is no amendment here, and a reader arriving
from 3.17 will look for one.** Say so in the chapter.

**Principle VII — Boring by Design:** presence stays out (spec FR-017). It is chapter 3.19's row
in `docs/07-tutorial-plan.md`, it needs FR-RTM-06's grace period and FR-RTM-07's scoping, and
delivering half of it here would leave the other half harder to teach.

**Principle II — No Acknowledged Message Is Ever Lost:** unchanged. Nothing about this feature
alters what an ack means or when it is sent. The publish happens after the commit in every design
considered; a publish that fails loses a *delivery*, never a message.

**No violations. Complexity Tracking is empty and the section is removed.**

### Post-design re-check

Three things changed between the gate above and the Phase 1 contracts, and one of them is new.

1. **Only the grammar moves; `createFanout` stays in the gateway** (R3, corrected). No
   zero-dependency package gains a Redis client. A scope reduction — principle VII is happier than
   it was.
2. **The publish is awaited before the response is written** (`contracts/fanout-publisher.md`).
   Ordering is now commit → publish → response, so the ack is strictly *later* than before:
   principle II is unaffected, and nothing is acknowledged that is not durable. **Principle III is
   still not engaged** — its "never synchronously on the request path" governs analytical events,
   and this is operational delivery — but the design now actively does the thing III's sentence
   resembles, so the chapter answers the objection rather than leaving it standing.
3. **New, and not resolved by the contracts:** `maxRetriesPerRequest: 0` and
   `connectTimeout: 1_000` bound a *dead* Redis. They do not bound a **connected but slow** one —
   ioredis has no command timeout unless one is set, and `limits/store.ts` does not set one either.
   A hung Redis would hold every send open. This is a real residual risk of awaiting the publish,
   it is inherited from the limiter rather than introduced here, and it needs a measurement and
   possibly a `commandTimeout` before close-out. Recorded rather than assumed away.

**Still no violations. Complexity Tracking stays empty and the section is removed.**

## Project Structure

### Documentation (this feature)

```text
specs/036-chapter-3-18/
├── plan.md              # This file
├── spec.md              # 17 FRs, 11 SCs
├── research.md          # Phase 0 — R1..R9, all measured
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1 — validation guide
├── contracts/           # Phase 1
├── checklists/
│   └── requirements.md  # 16/16 at /speckit-specify
└── tasks.md             # Phase 2 (/speckit-tasks — not created here)
```

### Source Code (both repositories)

```text
relay-platform/
├── packages/protocol/src/
│   ├── fanout.ts               # NEW — subjectFor(channelId), the payload type
│   └── index.ts                # re-export
├── services/api/src/
│   ├── messages/               # the publish site (R2) + module wiring
│   └── fanout/                 # NEW — the publisher half only (R6)
├── services/gateway/src/
│   ├── fanout.ts               # consumes the moved grammar
│   └── fanout.itest.ts         # import path moves; :89 already proves R7
└── tests/outsider/             # 3.14's verdict, now expected to pass

relay-tutorial/
├── app/(en)/part-3/chapter-18/the-message-that-never-arrived/
│   ├── page.mdx
│   └── figures.ts
├── app/(vi)/part-3/chapter-18/…/   # mirror, byte-identical fences
└── fences/                          # every path in the "fences" column above
```

**Structure Decision**: the existing three-service layout, unchanged. The one structural move is
`subjectFor` going from `services/gateway/src/fanout.ts` into `packages/protocol` — because the api cannot import from the gateway (R3), and because chapter 3.4
already made this exact move for the JetStream subject grammar with the reason written into
`internal.ts`. Two publishers on one subject is that argument, one subject over.

`createFanout` stays in the gateway. Putting it in `protocol` (one dependency) or `service-kit`
(none) would give a pure package a socket, and the api needs the publisher half only — no
`subscribe`, no `unsubscribe`, no `onDelivery`.

## Phases

**Phase 0 — research.** Done. Nine questions, all answered against the repository. The two that
changed the plan: R2's ordering (the SAD decides the publish site twice, and the outbox
alternative is more attractive than it looks) and R5, below.

**Phase 1 — design.** `data-model.md` (no schema change; the fan-out payload is the only "entity"
and it already has a zod schema), `contracts/` (the subject grammar and the publisher interface),
`quickstart.md` (the validation guide, including the constitutional recovery test).

**Phase 2 — tasks.** `/speckit-tasks`. Every task's first step is checking its own premise; five
were wrong in 3.17 and three more surfaced during implementation. Two premises in this plan are
already known to need checking before anything is built: R10's claim that a listener-less client
takes the process down, and R5's five-second window.

### The test that cannot tell the difference

`publish` swallows its own failures and resolves normally (R8). So the obvious test for FR-010 —
"the send still succeeds when the fan-out is down" — **passes identically when the publish
succeeds**, and would pass with the publisher deleted. FR-011's log assertion is the one that
carries the requirement. Every task that tests a failure path here states what would have to be
false for it to fail, because this feature's central mechanism is designed to be invisible when it
breaks. That is 3.17's T086 and T126 in advance rather than in hindsight.

### The largest risk, carried forward from R5

Delivery filters by **subscription**, not by a membership read. An instance subscribes to
`chan:{id}` while it holds a connection whose session named that channel, and that channel list
comes from `POST /internal/session` at connect time. So if a member is removed while their socket
is open, nothing in the delivery path re-reads membership, and **FR-RTM-10's five-second window
may not be met on either path.**

This chapter makes it reachable on a second path, which is why spec FR-013 forbids assuming the
socket path's answer covers the REST path. Chapter 3.15's T153 asked what a ban does to an open
socket and the answer turned out to be a third thing nobody had written down. This is that
question for a membership change. **If neither path meets FR-RTM-10, the outcome is a recorded gap
and a sentence in the chapter, not a quiet claim** — and it may be chapter 3.19's work, since
presence and membership-change delivery share the same missing re-read.
