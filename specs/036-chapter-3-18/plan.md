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

**This column was rebuilt in analysis pass 4 from the task list**, after the first version — a
prediction written before tasks existed — was found to omit five files that tasks modify and to
invent one that they do not. Each row carries who owns the file today, because a fence is built
against the last chapter to claim it, not against a generic HEAD.

| platform file | teaches | fences | fenced today by |
|---|---|---|---|
| `packages/protocol/src/fanout.ts` (new — `subjectFor`) | yes | yes | — |
| `packages/protocol/src/fanout.test.ts` (new) | no | **yes** | — |
| `packages/protocol/src/index.ts` | no | **yes** | p1/ch03, p2/ch05 |
| `services/gateway/src/fanout.ts` | yes | yes | **p2/ch06** (whole file) |
| `services/gateway/src/fanout.itest.ts` | no | **yes** | p2/ch06, ch07 |
| `services/api/src/fanout/publisher.ts` (new) | yes | yes | — |
| `services/api/src/fanout/publisher.test.ts` (new) | yes | yes | — |
| `services/api/src/fanout/fanout.itest.ts` (new) | yes | yes | — |
| `services/api/src/messages/messages.controller.ts` | yes | yes | six chapters, last **p3/ch17** |
| `services/api/src/messages/messages.module.ts` | yes | yes | p2/ch02, ch05, p3/ch02 |
| `services/gateway/src/session.itest.ts` | yes | **decide** | **NOBODY** — see below |
| `services/gateway/src/resume.itest.ts` | no | **yes** | p2/ch07, p3/ch02, ch07, ch08, ch16 |
| `vitest.coverage.config.mts` | no | **yes** | seven chapters, last p3/ch17 |
| `packages/outsider/src/integrate.itest.ts` | yes | yes | p3/ch14, p3/ch17 |
| `services/gateway/src/public-surface.itest.ts` | no | **yes** | p3/ch13, ch16, ch17 |
| `services/gateway/src/isolation.itest.ts` | no | **yes** | p3/ch12, ch15, ch16, ch17 |

**Nine taught, fifteen-or-sixteen fenced** — the column grew twice under analysis, and the second
time is the more instructive: **pass 9 found comments in `public-surface.itest.ts` and
`isolation.itest.ts` that this feature falsifies** (FR-018), which turns two files nothing was
going to touch into two files that must be edited and therefore fenced. A fence column tracks the
task list, and the task list moves when analysis reads prose.

**Nine taught, thirteen-or-fourteen fenced** was the pass-4 figure. The five the first column-guess missed —
`vitest.coverage.config.mts`, `session.itest.ts`, `resume.itest.ts`,
`packages/outsider/src/integrate.itest.ts`, and `packages/protocol/src/fanout.test.ts` — are all
files a task modifies without teaching, which is the category a prediction written before the tasks
cannot see. It also invented `services/api/package.json`: **`ioredis` is already a direct
dependency** (`:22`, `^6.0.0`), and `services/api/src/main.ts`, which does not change because the
publisher reads `RELAY_REDIS_URL` the way `limits/store.ts` already does.

Not fenced, and edited anyway: `docs/05-sad.md` and its mirror (governed by `check:docs`, not the
chain), `docs/07-tutorial-plan.md`, `relay-tutorial/lib/tutorial.ts`, and the chapter's own four
pages. The chain fences platform files a chapter claims; the tutorial *is* the tutorial.

### How each file is fenced, decided here rather than at T050

`check-fence-chain.mjs:39` excludes any fence whose title contains `(excerpt)` or `.naive.` —
`NOT_A_FILE`. That is the mechanism behind `gaps.md` item 7's three permanently-unverified files,
and this column now holds five large integration tests: `isolation.itest.ts` **833 lines**,
`session.itest.ts` 442, `resume.itest.ts` 358, `public-surface.itest.ts` 341,
`integrate.itest.ts` 310. A chapter does not show an 833-line test in full, so the hatch will be
reached for; it is already used six ways in the published corpus.

**But `(excerpt)` is not a free choice for a file already in the chain.** The replay compares the
end state, so if 3.18 excerpts a file it changed, the last contributing fence is some older
chapter's and the replayed bytes will not match HEAD — a `[HEAD]` drift failure. There are three
options, not two:

| | what it means |
|---|---|
| **titled** | the chapter shows the file and the chain verifies it |
| **`(excerpt)` + a `fences/post-series.md` hunk** | the chapter shows a fragment; the appendix carries the byte-exact change. This is what the appendix is *for* — *"changes to fenced files made by work that publishes no chapter"* |
| **`(excerpt)` alone** | only legitimate for a file that was never in the chain |

So, per file:

    protocol/fanout.ts, fanout.test.ts        titled — new, small, the chapter's subject
    protocol/index.ts                         titled — a one-line change, cheap to show
    gateway/fanout.ts                         titled — T007 discusses it, comment and all
    gateway/fanout.itest.ts        152 l      titled — an import split, and 152 lines is showable
    api/fanout/publisher.ts, .test.ts         titled — the centrepiece
    api/fanout/fanout.itest.ts    new, big    EXCERPT + appendix hunk; ten cases by the end
    api/messages/messages.controller.ts       titled — the publish site itself
    api/messages/messages.module.ts           titled
    gateway/resume.itest.ts       358 l       EXCERPT + appendix hunk
    gateway/public-surface.itest.ts 341 l     EXCERPT + appendix hunk — a COMMENT-only change
    gateway/isolation.itest.ts    833 l       EXCERPT + appendix hunk — a COMMENT-only change
    vitest.coverage.config.mts    7 chapters  EXCERPT + appendix hunk (one already at :1419)
    outsider/integrate.itest.ts   310 l       titled — T003 inverts its central test, and a
                                              reader following the exercise needs to see it
    gateway/session.itest.ts      442 l       T014a decides; in no chapter today

**The two comment-only changes are the clearest appendix cases in the feature.** 3.18 does not
teach `isolation.itest.ts` or `public-surface.itest.ts`; it retires a stale sentence in each
(FR-018). Putting an 833-line file into a chapter that never discusses it is the exact thing
`post-series.md` exists to prevent — *"no chapter is made to lie."*

**`session.itest.ts` is a decision, not an omission.** It is fenced by no chapter — outside the
chain the way `sentinel.ts` and `guard.itest.ts` are (`gaps.md` item 7) — and 3.18 puts its
end-to-end test there, the one test a reader most wants to see. Either the chapter fences it, adding
a file to the chain for the first time, or it shows an unfenced test and says so. T014a decides.

**Two appendix interactions, both measured rather than assumed.** `fences/post-series.md:1419`
holds a ```diff hunk titled `vitest.coverage.config.mts` anchored at `@@ -18,8 +18,33 @@` — near
the top, clear of the `thresholds` object T011 edits around line 104, so the two do not collide.
`post-series.md:1204` mentions `services/gateway/src/fanout.ts` as a *string inside an
`eslint.config.mjs` exemption array*, not as a claim on the file. Neither is the last-line anchoring
that forbids appending, and checking beat assuming in both directions.

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

3.18 has a small surface and, after seven analysis passes, **six** arguments. The first estimate
said five and was made before three more arrived — which is what an estimate derived from arguments
has to survive, so it was re-derived in pass 7 rather than carried:

    1  the ordering that cannot be copied to REST, and the two NFRs it pulls apart
    2  why the subject grammar moved and the client did not
    3  the recovery property under a lost publish — constitution IV's gate
    4  the membership question in R5, and whatever T031–T034 make of FR-RTM-10
    5  the SAD disagreeing with itself: an amendment, but not the one a 3.17 reader expects
    6  a second output channel the isolation oracle cannot see (FR-008a)

Eight were on the table. **Two did not survive the cut**, and saying which is the point of counting
arguments rather than files:

- The two NFRs pulling opposite ways is not its own argument — it is the *cost* of argument 1, and
  splitting them would say the same thing twice.
- The subject grammars' tenancy asymmetry moves to `chapter-notes.md`. It is real, it is
  defensible, and it is a sidebar: the chapter that makes it visible is not obliged to resolve it,
  and a reader following the build does not need it to finish.

At the rate the first estimate used — 440 to 560 words per argument — six gives **2,650–3,350
prose words**, inside SC-011's 2,000–4,000 with room at both ends. Eight would have given
3,500–4,500 and brushed the ceiling, which is the finding pass 7 raised. A file rate would have
predicted ~1,300 and been wrong for the reason above.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Principle I — Tenant Isolation (NON-NEGOTIABLE): engaged, and its own suite cannot see this.**

Clause 1 forbids revealing another tenant's data *"under any input"*; clause 4 mandates a suite that
attacks every endpoint with foreign IDs on every build. That suite exists, `POST
/v1/channels/:channelId/messages` is one of its targets (`isolation/targets.ts:185`), and **its
oracle compares responses** — *"nothing of the victim's came back, not that a status was 4xx."*

This feature gives that endpoint a **second output channel**. A publish on a refused
foreign-channel send would emit onto a subject outside the caller's tenant with every existing
test green. The gauntlet cannot be extended to catch it, because comparing responses is what it
is; so the feature's own test carries the clause. Spec **FR-008a**, task T033.

The other three clauses are untouched: nothing new is persisted, so clause 2 does not bind a
payload that is never written; data access still goes through the environment-scoped repository,
and the publish transmits a value that layer already returned rather than reading anything.

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

**Principle VI — Requirement-Driven, Test-Verified Delivery: satisfied by citation of the SRS, and
by an amendment to the SAD.** FR-RTM-01 is the unmet clause (not FR-RTM-05, which the tutorial
plan's row names — see spec FR-001). Chapter 3.17's gate was an SRS amendment because the SRS had
no bot concept; **no SRS clause changes here, and a reader arriving from 3.17 will look for one.**

**`docs/05-sad.md` does change, and the first version of this section said it did not.** It says
two different things about who publishes: `:138`'s component diagram gives the edge to the api,
`:248`'s sequence diagram draws `G->>G`, and `:254`'s ordering bullet is unconditional where
FR-005 now splits by transport. The amendment is a REST send sequence plus that split, and it is
not complete until `pnpm sync:docs` has run — `05-sad.md` is mirrored into
`relay-tutorial/content/docs/` and `check-docs-drift.sh` fails on divergence. See spec FR-002a.

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

**Close-out spans three repositories.** `relay-platform` and `relay-tutorial` are submodules and
`docs/`+`specs/` are the parent's, so one chapter is three commits, a gitlink bump, and a tag in
each — **tagged last**, because CLAUDE.md's fence lesson 2 exists precisely because a feature's tail
amended a platform file after tagging. T063–T066. Absent from the first task list, found in analysis
pass 10.

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
