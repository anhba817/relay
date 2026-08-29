# Implementation Plan: chapter 3.19 — presence, and who is allowed to see it

**Branch**: `037-chapter-3-19` | **Date**: 2026-08-27 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/037-chapter-3-19/spec.md`

## Summary

`presence.changed` has been in the protocol union since chapter 1.3 and nothing has ever
produced one. This chapter gives it a producer: a transition derived from connection state, a
30-second grace period that survives a reconnection to a different instance, and delivery bounded
to users who share a channel with the subject.

The approach, from research:

- **A second subject grammar**, `presence:{channel_id}`, in a new
  `services/gateway/src/presence.ts` that owns its own Redis clients. `fanout.ts` is not touched.
  The fan-out is typed to messages at three points and one of them sits inside a function ten
  chapters fence (R1).
- **The presence key's TTL is the cross-instance liveness signal.** A refresh timer keeps it
  alive while any instance holds a connection; the closing instance re-pins the key to `graceMs`,
  schedules one check at `+graceMs`, and publishes `offline` only if the key is gone. `SET … NX`
  elects a single publisher. Verified against Redis 8.10.0 rather than assumed (R2). **The
  re-pinning is not decoration** — without it the key dies up to `refreshMs` before the grace ends
  and a late reconnection publishes a second `online`, which FR-007 forbids (R2a, found in analysis
  pass 1). The pin is **awaited** and the check runs at `graceMs + marginMs`, because pinning and
  checking at the same instant strands the user online permanently — a worse defect than the one the
  pin fixed, found in pass 2 auditing pass 1 (R2b).
- **Three quantities currently share one number** — the ping interval, the grace period and the
  key TTL are all 30 s, and a TTL equal to its refresh interval expires a connected user.
  Presence gets its own interval at 10 s (R3).
- **An internal `transition` id** so a watcher sharing three channels receives one frame, not
  three. It never reaches the wire; the published frame shape does not change (R5).

FR-RTM-10 stays out, on a recorded reason that corrects the one chapter 3.18's `gaps.md` item 4 gave (R7).

## Technical Context

**Language/Version**: TypeScript 5.x on Node.js 22, ESM. One language across services
(constitution VII, ADR-01).

**Primary Dependencies**: `ioredis` (already present in the gateway three times over); `zod` for
the payload schema, in `@relay/protocol`; `ws`; `vitest`.

**Storage**: Redis only, and nothing durable. Two keys per subject user — `presence:{env}:{user}`
and an offline-election marker — both with TTLs, neither a source of truth (constitution IV,
ADR-10). **No Postgres.** The gateway has no database and chapter 2.1's lint ban makes a
violation a build failure (ADR-05).

**Testing**: `vitest`, two lanes. Unit (`*.test.ts`, Docker-free) for the transition arithmetic
and the payload schema; integration (`*.itest.ts`, compose stores up) for everything crossing
Redis, including two-instance cases. Coverage across both lanes via
`relay-platform/vitest.coverage.config.mts`, per-file pins written after measurement (R15).

**Target Platform**: Linux; the gateway service, horizontally scaled with no sticky routing
(CON-02).

**Project Type**: Monorepo — a platform (`relay-platform`) and the tutorial that fences it
(`relay-tutorial`), plus governing documents in `docs/` mirrored into the tutorial.

**Performance Goals**: No clause gives presence a latency budget. What this feature must not do
is add cost to the message path — R1's decision keeps the message subscriber's parse
byte-identical. The subscription count per channel doubles, and that is the number to measure.

**Constraints**: The integration lane closed chapter 3.18 at **607 tests, 195 s against a 240 s
budget — 45 s of headroom**. That headroom is a *lane* total; inside the gateway package files run
in parallel, so what this feature actually spends is set by whether `presence.itest.ts` becomes the
pool's slowest file (research R18). Grace-period tests must run in milliseconds (R4), with exactly one
case asserting the production default is 30_000.

**Scale/Scope**: One new platform module, one new protocol helper, one new payload schema, edits
to `session.ts` at two existing hook points, **four** governing-document amendments — the fourth,
`docs/06-adr-deep-dives.md`, found in analysis pass 1 — **corrections to four claims in three
already-published chapters, in both locales** (FR-033, found in pass 7), and one new chapter in two
locales. The lane's largest membership set is five channels, which is why ADR-10's revisit
trigger cannot be discharged here (FR-016a).

## Constitution Check

*GATE: must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Verdict | How |
|---|---|---|
| **I — Tenant isolation is a correctness property** | **PASS, and it is the risk** | Presence is a statement about a person delivered to an audience the sender does not name. FR-014 and SC-007 put a must-not-receive socket in the same run as a must-receive one; the presence key is `{env}`-scoped; `isolation.itest.ts` already refuses a forged `presence.changed`. |
| **II — No acknowledged message is ever lost** | **PASS, not engaged** | Presence is never acknowledged. FR-026 forbids giving it durability, per ADR-10. |
| **III — Two data paths, never crossed** | **PASS** | Presence is entirely on the live path. It writes no outbox row and publishes to no JetStream subject. |
| **IV — Single writer, single source of truth** | **PASS** | Presence is derived, ephemeral and in Redis. Total loss is a cosmetic outage that self-heals on the next transition. |
| **V — API-first, developer-first** | **PASS** | No new public surface. The frame the client sees is the one chapter 1.3 published; the internal payload's `transition` id never leaves the gateway (R5). |
| **VI — Requirement-driven, test-verified** | **PASS, and it names a coverage class** | Four clauses, no clause text changed (FR-002). `traceability.md` is built now, in planning, not at close-out. **NFR-MNT-02 is engaged**: presence is tenant-isolation code and pins at 100% branches — see below (FR-032). |
| **VII — Boring by design** | **PASS, and it took a new ADR to stay that way** | No new service — ADR-10 and the SAD's not-a-service table both say presence is gateway + Redis. No new language, no new dependency. **Declared:** a fifth Redis connection per gateway instance, and FR-RTM-10 deliberately left out rather than absorbed. **And the ADR clause is engaged**: presence moving to its own subject grammar changes what ADR-10 decided, so it needs **ADR-19** superseding it — ADRs are immutable once accepted (FR-034, found in analysis pass 14). |

**No gate fails.** Two items are recorded in Complexity Tracking rather than waved through.

### NFR-MNT-02: presence is tenant-isolation code, and the pin is 100% branches

The constitution names three classes that must reach 100% branch coverage — message ordering,
idempotency, and tenant isolation. **This feature is in the third**, and the classification is a
decision rather than an observation, so it is made here rather than left to whatever the coverage
run reports.

The isolation chain for a presence event runs through three places, and two of them are this
feature's:

    POST /internal/session      channel_ids, scoped by tenant — the api's, unchanged here
    presence.ts                 subscribe/unsubscribe per channel: which subjects this instance hears
    session.ts                  deliverPresence over subscribersOf(channelId): which sockets get it

A defect in the middle row sends a statement about a person to a tenant that should not know they
exist. That is the same property principle I calls a correctness concern, not a cosmetic one.

**So `services/gateway/src/presence.ts` and `packages/protocol/src/presence.ts` pin at 100
branches, functions, lines and statements**, matching what chapter 3.18's two new fan-out files
reached. If a branch proves unreachable, the rule is the ratchet's own history — it has removed
code three times rather than covered it, and 3.17's unreachable `throw` went rather than the pin.
Lowering the pin with a plausible reason is the failure mode this section exists to prevent: the
coverage task writes pins "from the measurement", and a measurement will always supply a reason.

**Found in analysis pass 5.** `NFR-MNT-02` appeared in none of this feature's artifacts while a
constitution MUST turned on it.

## Project Structure

### Documentation (this feature)

```text
specs/037-chapter-3-19/
├── plan.md              # This file
├── spec.md
├── research.md          # Phase 0 — R1..R15
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── traceability.md      # Phase 1, and built BOTH WAYS here rather than at close-out
├── contracts/
│   ├── presence-fabric.md      # subject grammar + internal payload
│   └── presence-lifecycle.md   # the transition state machine and its guards
├── checklists/
│   └── requirements.md
├── check-refs.py        # structure + cross-artifact reference checker, run at every phase end
├── check-prose.py       # FR-033's gate: four contradicted published claims, one fragment per locale
└── tasks.md             # /speckit-tasks — NOT created here
```

### Source code

```text
relay-platform/
├── packages/protocol/src/
│   ├── presence.ts                  # NEW — subjectForPresence AND the fabric payload schema
│   └── index.ts                     # + one `export * from "./presence.js"`
│                                    # fanout.ts is NOT touched — see below
├── services/gateway/src/
│   ├── presence.ts                  # NEW — clients, key operations, publish, subscribe
│   ├── presence.test.ts             # NEW — unit: transitions, guards, defaults
│   ├── presence.itest.ts            # NEW — integration: one Redis, two instances
│   ├── session.ts                   # two hook points (:355, :391) + three options
│   ├── registry.ts                  # a per-user lookup
│   └── main.ts                      # wiring, and the fifth client's close
└── vitest.coverage.config.mts       # per-file pins, written after measurement

docs/                                # + relay-tutorial/content/docs mirrors via sync:docs
├── 04-srs.md                        # Appendix C row 3 -> closed (FR-016)
├── 05-sad.md                        # ADR-10's subject sentence, §210's pointer, the Redis table
├── 06-adr-deep-dives.md             # ADR-10's deep dive: :633 and :651 (FR-016, FR-017)
└── 07-tutorial-plan.md              # the 3.19 row names FR-RTM-07 and FR-CHN-05 (FR-018)

relay-tutorial/
├── app/(en)/part-3/chapter-19/<slug>/page.mdx    # NEW
├── app/(vi)/vi/part-3/chapter-19/<slug>/page.mdx # NEW
└── lib/tutorial.ts                               # + the 3.19 entry, both Vietnamese fields
```

**`packages/protocol/src/fanout.ts` is not edited at all.** The first draft put
`subjectForPresence` beside `subjectForChannel`, which reads well and costs a `diff` hunk on a
file chapter 3.18 fences. `internal.ts` already holds the event spine's own `subjectFor` in its
own file, so **each fabric owning its subject grammar is the established precedent**, not a
compromise. A new file is a whole-file fence and touches nothing downstream.

**Structure Decision**: the existing monorepo layout, with one new module in the gateway and one
new module in the protocol package. The new gateway module follows the shape `fanout.ts`,
`limits.ts` and `meter.ts` share — a factory returning an interface, injected into
`attachSessions` as an optional field so chapter 2.5's tests and a single-process dev run still
work without Redis.

## Implementation phases

Nine phases, each its own commit. `git checkout` on a file with uncommitted work destroyed work
twice in chapter 3.12, and a phase that adds raw SQL must run the suite that executes it — this
feature adds none, but it adds Redis commands, which are strings in exactly the same way.

| # | Phase | What it must not be believed without |
|---|---|---|
| 1 | Setup, and the failing state observed | A test that shows no presence event exists today, red before anything is built. `git status --short` in all three repositories at the end. |
| 2 | The grammar and the module | The payload schema and the subject helper, with the union's totality check still green. Unit tests for the transition arithmetic. |
| 3 | Online | One instance, then two. Delivery asserted by count, not by arrival. |
| 4 | Offline and the grace period | The re-pin at the close and the check a margin after it (R2a, R2b); the election; the case asserting the production defaults; a reconnect *after* `ttlMs` lapses; a deploy drain; five connections. Swapping the two calls in the close handler must fail a test (R8). |
| 5 | Scope | Must-receive and must-not-receive in the same run. Cross-tenant. The dedup asserted by count with three shared channels. |
| 6 | Failure | Redis down: the socket opens, the log line exists, messages still deliver. Then Redis restored and the next transition published — the half that proves the path was alive. |
| 7 | The documents | Three files amended, `pnpm sync:docs` run, `pnpm check:docs` green. Open question 3 has one answer and a grep finds no third position. |
| 8 | The chapter | Both locales, `pnpm check:fences` from predecessor `caeabc9`, `check:figures`, `check:srs`, `check:errors` after a build. MDX is not markdown. |
| 9 | Close-out | The lane battery, the count read with the colour codes stripped, coverage pins written from measurement, `traceability.md` re-derived, `gaps.md` with owners. |

**Before phase 1 and before phase 9's coverage run:** stop the compose `services` profile.
Measured during research — `relay-api-1`, `relay-gateway-1` and `relay-dispatcher-1` are all up
right now, and chapter 3.18 lost half an hour to a live dispatcher moving a branch pin on a file
it never touched (R14).

## Complexity Tracking

| Violation | Why needed | Simpler alternative rejected because |
|---|---|---|
| A **fifth Redis connection** per gateway instance (fanout ×2, limiter ×1, presence ×2) | A subscribed ioredis connection cannot issue ordinary commands, and presence needs `SET`, `EXISTS` and `PUBLISH` as well as `SUBSCRIBE`. So presence needs a subscriber and a command client. | Reusing `fanout`'s publisher saves one connection and couples two modules' lifecycles. Chapter 3.8 faced this exact choice and stated the reason at `services/gateway/src/main.ts:40`: one of fanout's two is a subscriber, and a separate client is how its close has an owner. |
| A **second subject grammar** rather than one enveloped subject | The message path hardcodes the kind at three points, the third inside a function ten chapters fence. A second subject leaves the highest-volume path byte-identical and makes cross-kind mis-delivery impossible instead of test-enforced. | Enveloping both kinds on `chan:{id}` halves the subscription count and reads closer to ADR-10's letter. Rejected in R1; the doubled `SUBSCRIBE` count is the declared price and phase 3 measures it. |
| An **internal payload field** (`transition`) the public frame does not have | Three shared channels produce three publishes for one transition, and the frame carries no channel to tell them apart. FR-012 forbids the duplicates. | A clock-based suppression window needs no field, and answers "was this the same transition?" with a heuristic. Rejected in R5. |

## Open decisions this plan closes

- **FR-016 / open question 3** — closed as *not opt-in per channel*, confirming ADR-10, with the
  revisit trigger named as undischarged because the lane's largest membership set is five
  channels. **The question has five positions across three documents, not the three this plan
  first counted** — `docs/06-adr-deep-dives.md` holds two of them and had not been opened until
  the task list ran the grep. One of those two, ADR-10's revisit-when clause, names *"presence
  subjects get their own fabric"* as a remedy: **R1 takes that remedy early, for a different
  reason than the trigger names**, and the chapter has to say so.
- **FR-020a / FR-RTM-10** — **out**, and the reason chapter 3.18's `gaps.md` item 4 gave is corrected rather than
  inherited. Its stated premise, that presence needs a membership push, does not hold; and my own
  first replacement reason (that a removal cannot reach the gateway) is also wrong, because on a
  removal the gateway is still subscribed to that channel. The reason that survives is that
  FR-RTM-10 is a second argument — a third payload kind, an api-side publisher, and a mutation of
  a live connection's channel set — in a chapter that has one. See R7.

## Constitution re-check, after Phase 1 design

Re-run against the artifacts rather than against the summary, because the design added things the
first pass could not see.

| Principle | Still passes? | What Phase 1 added |
|---|---|---|
| I | yes | The internal payload gained a `transition` id and nothing else. It carries no channel list — the alternative that would have, R5's third option, was rejected partly for this: it hands an instance the subject's channel set including channels it hosts nobody for. |
| II, III, IV | yes | FR-026 gained a **test** rather than an inspection: a transition adds no outbox row. That is the assertable form of "presence acquired no durability". |
| V | yes | The wire frame is byte-identical to chapter 1.3's. The internal payload is a different shape from the public frame for the first time in this system, and `contracts/presence-fabric.md` says so where a reader will find it. |
| VI | **yes, and it changed the spec** | Building `traceability.md` both ways added FR-027, FR-028 and FR-029 — a resume-path rule decided in research and carried by no requirement, an edge case carried by no requirement, and a cross-kind rule that lived in the contract and in no requirement. Every FR now has a verification; the ones with no runnable check are listed rather than absent. |
| VII | yes, with the same two declarations | The fifth Redis connection and FR-RTM-10's exclusion, both in Complexity Tracking. Phase 1 added no service, no dependency and no language. |

**The map earned its hour before a line of code.** That is the whole of chapter 3.18's advice,
and the three requirements it produced are the evidence rather than the claim.

## What could still be wrong

Recorded now so the analysis passes have something to attack, in the spirit of not stopping on
falling yield — chapter 3.16's pass 12 recommended stopping and passes 13, 14 and 15 each found a
CRITICAL.

- **The doubled subscription count is unmeasured until Phase 3 measures it**, and Phase 3 now has a
  task that does — it did not when this line was first written, which analysis pass 2 caught. R1
  chose the design on structure and named the cost without a number; a user in 20 channels issues 40
  `SUBSCRIBE`s. If the number is bad the enveloped-subject alternative is still there, and it is
  only still there while somebody produces the number.
- **The refresh interval and the TTL are a ratio I chose, not one I measured.** 10 s against 30 s
  survives two consecutive misses. Whether a loaded gateway misses three in a row is a question
  about event-loop latency that nothing here has asked.
- **`presence:{env}:{user}` needs the environment id, and the fan-out subject carries no tenant
  token.** The key is env-scoped and the subject is not, which is correct — but it means two
  different scoping rules in one module, and that is the kind of thing an isolation test should
  be pointed at rather than trusted.
- **The three-way ordering in the close handler** (meter before `registry.remove`, presence
  after) is a comment away from being broken by a later edit. Phase 4 owes it a test that fails
  on a swap, and chapter 3.18's T086 is the warning: removing a check can come back green when an
  earlier phase replaced rather than nested.
