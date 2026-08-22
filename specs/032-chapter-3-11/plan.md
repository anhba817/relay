# Implementation Plan: Chapter 3.11 — Counting a connection

**Branch**: `032-chapter-3-11` | **Date**: 2026-08-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/032-chapter-3-11/spec.md`

## Summary

Connection-minutes — the third dimension FR-RTL-05 names and the only one the api
cannot compute from its own tables. Metered by the gateway, recorded by the api,
capped at the socket door, and closing FR-RTL-05.

Chapter 3.10 counted messages and distinct users, both of which were already
rows. A connection is not a row anywhere, and the only process that can see one
is the gateway, which owns no tables and no identity of its own. What research
settled:

- **The gateway becomes the second platform-credentialled service.** Every
  internal call it makes today forwards the end user's token — `api-client.ts`
  says it "holds no secret that could" verify one. A usage report is nobody's
  user action, and the workaround of reporting per connection with that
  connection's token fails hardest on the long-lived socket whose token has
  expired, which is the one with the most minutes on it. Chapter 3.5 already
  built the credential class this needs (R1).
- **Reports carry totals, not deltas, and that deletes the retry buffer.** A
  lost report is repaired by the next one; a repeated one credits
  `max(0, reported − credited) = 0`; a report that cannot be delivered is
  dropped rather than queued. The gateway keeps no outbox, which is the right
  amount of durable state for a service designed to hold none (R3).
- **A connection-minute is a wall-clock minute bucket, charged per connection.**
  Five seconds costs one minute; 00:00:59 to 00:01:01 costs two. This answers the
  question `docs/04-srs.md` records as open, charges reconnect churn, and makes
  the deduplication fall out of the unit rather than being bolted on (R2).
- **Idempotency state is one row per connection per period, not per minute.** The
  naive key is 43.2 million rows a month at a thousand concurrent sockets, which
  FR-010 forbids and which is chapter 3.10's R1 argument arriving in a new
  costume (R4).
- **Enforced at the door, in `POST /internal/session`.** Which means adding a
  usage read to the exact path chapter 3.10's second analysis pass protected from
  one, and it means `Authentication` grows a fourth outcome — a 402 today closes
  the socket as 1011, "we are broken, retry", which is wrong twice (R6, R7).
- **The refusal has two hops and two shapes.** The api answers `402`; the gateway
  completes the handshake, sends an error frame with the resume date, and closes
  with **4008** — a code `packages/protocol/src/codes.ts` has read "quota
  exhausted" since chapter 1.3 with nothing emitting it, which EIR-WS-06 asks for
  by name and which `session.test.ts` currently has a live test asserting the
  absence of. An earlier draft forwarded an HTTP status onto a socket, borrowing
  chapter 3.8's shape while discarding the `Retry-After` that was its only
  justification (R21).
- **The email tests drive a sweep both guards miss.** `createQuotaRelay(...).drainOnce()`
  calls `drainQuotaNotifications`, which claims rows across every environment.
  Chapter 3.10 added it and put it on neither the lint restriction list nor
  `exempt.ts`, whose comment says the two must agree — and the lint rule could not
  have caught this chapter anyway, because the call is indirect. The half that
  protects the chapter is scoping the assertions to rows it created (R22).
- **The gateway had no graceful shutdown to hang the flush on.** `serve()` returns
  a bare `node:http` Server and nothing ever calls `server.close()`; only the
  dispatcher installs signal handlers. Four documents agreed the flush happened
  and none of them was the thing that had to be true (R11).
- **Still no sweep.** Usage rises only on a report, and the report transaction
  knows the figure before and after, so it writes its own crossings. Second
  chapter running to reach that result by that argument (R5).
- **The close path is metered too, and that narrows R3.** `session.ts` removes a
  connection from the registry in its `close` handler, and the meter walks the
  registry — so the design as first planned counted a socket that opened and
  closed between two reports as **zero**, which FR-002 forbids and which would have
  made reconnect churn free, the one thing the bucket model was chosen to charge.
  The close handler hands its final totals to the meter. Retention then applies to
  closed connections and not to open ones, because a closed connection has no next
  report to repair a lost one (R19).
- **A report naming an unseen connection is accepted as that connection's
  first.** The api is never told when a connection opens, so "unknown" and "first"
  are the same state; what is refused is a report naming a connection whose row
  already carries a different environment (R20).

And one finding that is about the chapter before this one: **chapter 3.10 added
three environment-scoped tables and extended feature 030's guard to none of
them.** Its SC-008 read "no new file is added to the exemption list", which
passed and is true and is quieter than it sounds. Extending the guard is also not
the one-line array change it looks like — the refusal message interpolates
`OLD.id` and `usage_periods` has no `id` column (R5a).

## Technical Context

**Language/Version**: TypeScript 5.x on Node.js 22, as everywhere in this
repository (constitution VII).

**Primary Dependencies**: NestJS for the api's HTTP surface, Drizzle inside the
repository layer (ADR-16), `pg` for the driver, `ws` in the gateway, zod through
`@relay/protocol` for the report schema, Mailpit in compose for what an admin
received. Nothing new.

**Storage**: PostgreSQL. Migration `0010_connection_minutes.sql`: one new table
(`usage_connections`), one new column on `usage_periods`, and two CHECK
constraints dropped and recreated because Postgres has no `ALTER CONSTRAINT` for
a CHECK expression. No new policy column — `connection_minutes` is a third key in
`environments.quota_config`, which is what chapter 3.10 said the jsonb shape was
for.

**Testing**: Vitest, in two integration lanes and **not in `packages/e2e`**. Unit
tests for the minute function and the report arithmetic; the api's lane for the
credit, its failure modes, the route's isolation and the Mailpit reads; the
gateway's lane — which has spawned a live api child since chapter 3.2 — for
anything needing a real socket, with the gateway itself in-process so its clock is
injectable. Chapter 3.10 put the equivalent socket test in e2e on a rationale that
does not hold today, and e2e is refused here for a different reason: the gateway
is a child process there, so no timing assertion in this chapter could be driven
rather than waited out (R24). Two tests are the exception and spawn a gateway
process, because a signal is the one thing an in-process gateway cannot receive.
Every time-based test drives a clock — `attachSessions` already takes
`pingIntervalMs` as a parameter for exactly this reason, and nothing in the suite
sleeps for a minute.

**Target Platform**: Linux server, the same compose stack. The gateway's
`compose.yaml` block gains its first `RELAY_*` credential variable.

**Project Type**: Monorepo service work plus a published tutorial chapter.

**Performance Goals**: The connect path must not gain work proportional to the
tenant's traffic, connection history, or elapsed minutes in the period (FR-025).
The added read is `environments` left-joined to `usage_periods` on two primary
keys, one round trip, with an early exit for the unconfigured tenant. Measured at
concurrency with `EXPLAIN (ANALYZE, BUFFERS)`, not asserted.

**Constraints**: The gateway may not touch the database (ADR-05, and the chapter
2.1 lint ban that makes it a build failure). Metering may not close a socket,
refuse a connect, or fail a send (FR-012). Reported figures must survive a flush
of the per-minute counter store (FR-026).

**Scale/Scope**: One migration, one new internal route, one new gateway module,
seven places where a third dimension has to be named on R15's reading — a prediction T066 measures rather than confirms — and **twenty-one** existing
files carrying **95** fences between them (R16) — four of them build-gate files
(`compose.yaml`, `turbo.json`, `vitest.coverage.config.mts`, `eslint.config.mjs`)
that this chapter has to edit. That table was wrong in all three analysis passes,
every time by extending a list rather than counting one, and T006 now generates it.

## Constitution Check

*GATE: passed before Phase 0, re-checked after Phase 1 design.*

| Principle | Check | Verdict |
|---|---|---|
| **I. Tenant isolation is a correctness property** | Every accounting row carries `environment_id`, written by the first report and never updated: a later report naming a different environment for the same connection is refused with a 409 rather than reconciled. The report route accepts a platform credential only, because an `application` credential is scoped to one environment and a route that ignored that scope is the shape a cross-tenant hole takes. | Pass |
| **II. No acknowledged message is ever lost** | Metering touches no message. A refused *connect* refuses nothing already acknowledged, and FR-017 keeps open sockets delivering past the cap. | Pass |
| **III. Two data paths, never crossed** | **The clause names this chapter's own word**, so the verdict needs an argument and not an assertion: "billing, *metering*, and dashboard analytics read only from the analytical store (ClickHouse), fed via a durable queue". This chapter meters into PostgreSQL. FR-RTL-05 and FR-ANL-05 are two requirements over the same three dimensions and they need different stores — FR-ANL-05 *reports*, asynchronously, and belongs in ClickHouse in Part 4; FR-RTL-05 *enforces*, and a connect cannot be refused from a store whose feed is allowed to have backlog. A cap read from an eventually-consistent store makes the refusal eventually correct, which for a commercial limit means wrong. Nothing here writes to or reads from the analytical store. **The clause's fourth bullet has no counterpart here**: "metered totals MUST reconcile against operational counts to within 0.1%" assumes two figures, and this chapter's metered total *is* the operational count — the first in the project with nothing to reconcile against. `contracts/metering.md` §5 carries that burden instead, which is why every loss in it is enumerated rather than summarised. | Pass, with the argument stated |
| **IV. Single writer, single source of truth** | The api remains the only writer. The gateway gains a credential, not a database client, and the 2.1 lint ban stays in force — SC-018 makes that a regression test rather than an intention. | Pass |
| **V. API-first, developer-first** | The refusal names its own code rather than letting the envelope infer one, carries the dimension, period, figure and resume date, and deliberately omits `Retry-After` — the one header that separates it from chapter 3.8's refusal at the same door. | Pass, with an inherited debt |
| **VI. Requirement-driven, test-verified** | **32 requirements, 23 measurable outcomes** — derived with `grep -c '^- [*][*]FR-' spec.md` and the same for `SC-`, not carried forward by hand. Every requirement mapped, re-checked after each analysis pass. Five requirements had no outcome on the specification's first pass and got one before the checklist was marked complete; four passes added seven more. This row read “28 and 20” through three passes that each added requirements — the claim stayed true and the count beside it did not, which is why it now says how to re-derive it. | Pass |
| **VII. Boring by design — scope is a commitment** | No new language, no new dependency, no new service. One new table, one new route, one new timer. The platform credential is an existing class getting its second holder. Guard extension, row pruning and per-day analytics are all named and refused rather than absorbed. | Pass |

**No violation to justify and no ADR required.** The two changes that come
closest are one credential per service instead of one shared secret (R1a), which
narrows an existing mechanism rather than adding one, and extracting two private
repository methods to standalone functions (R8), which moves about forty lines and
changes no behaviour.

## Project Structure

### Documentation (this feature)

```text
specs/032-chapter-3-11/
├── plan.md              # This file
├── research.md          # Phase 0 — R1 to R23, with what was read and what is owed
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1 — V0 to V14, plus V2a
├── contracts/
│   └── metering.md      # Phase 1 — the report, the 402, the email, the read,
│                        #           and what the platform admits it can lose
├── checklists/
│   └── requirements.md  # 16/16, plus a section per analysis pass
└── tasks.md             # Phase 2 — /speckit-tasks, not created here
```

### Source Code (repository root)

```text
relay-platform/
├── compose.yaml                              # the gateway's first credential
├── turbo.json                                # its env entry (strict env mode)
├── vitest.coverage.config.mts                # three ratchet entries (R23)
├── eslint.config.mjs                         # drainQuotaNotifications joins the
│                                             # restricted family (R22)
├── packages/protocol/src/
│   ├── internal.ts                           # the report request/response schemas
│   └── codes.ts                              # quota_exceeded joins ERROR_CODES;
│                                             # 4008 stops being unemitted (R21)
├── services/api/
│   ├── migrations/
│   │   └── 0010_connection_minutes.sql       # usage_connections, the column,
│   │                                         # two CHECKs dropped and recreated
│   └── src/
│       ├── auth/
│       │   └── authenticate.middleware.ts    # one credential per service;
│       │                                     # `service: "dispatcher"` stops
│       │                                     # being a constant
│       ├── db/
│       │   ├── schema.ts                     # usage_connections, the column
│       │   └── repository.ts                 # creditConnectionMinutes;
│       │                                     # recordCrossings and
│       │                                     # organisationOf extracted
│       ├── internal/
│       │   ├── usage.controller.ts           # NEW — POST /internal/usage/connections
│       │   ├── internal.module.ts            # where the new controller registers
│       │   └── session.controller.ts         # the cap check at the door
│       ├── limits/
│       │   └── rate-limit.middleware.ts      # a comment that says the gateway
│       │                                     # makes three calls and holds no
│       │                                     # platform credential. Both stop
│       │                                     # being true (R16)
│       └── quotas/
│           ├── period.ts                     # minuteOf, beside periodOf
│           ├── config.ts                     # the third key
│           ├── quota.error.ts                # the third Dimension
│           └── quota-email.ts                # the third dimension's copy
├── services/gateway/src/
│   ├── meter.ts                              # NEW — buckets, the timer, the report
│   ├── meter.test.ts                         # the arithmetic, on a driven clock
│   ├── meter.itest.ts                        # replay, loss, and the kill
│   ├── registry.ts                            # what a connection remembers about time
│   ├── session.ts                            # the second timer; the error frame
│   │                                          # and close 4008 at the door
│   ├── session.test.ts                       # the 4008 absence test, inverted
│   ├── auth.ts                               # a fourth outcome
│   ├── api-client.ts                         # the report call, and a credential
│   └── main.ts                               # wiring, and the shutdown flush
└── relay-tutorial/
    └── app/(en)/part-3/chapter-11/counting-a-connection/
        ├── page.mdx                          # and the (vi) mirror
        └── figures.ts
```

**Why `meter.ts` in the gateway rather than extending `limits.ts`.** They share
a shape — count something, tell the api — and nothing else. `limits.ts` is a
Redis counter over a one-minute window that is allowed to fail open and whose
loss costs one window of over-service. The meter is a claim about money that must
not be lost twice and must not be counted twice, and it talks to Postgres through
the api rather than to Redis at all. Chapter 3.10 made the same argument for
keeping `quotas/` out of `limits/`; this is that argument on the other side of
the wire.

**Why `usage.controller.ts` rather than a method on the existing `/internal`
controller.** The existing internal controllers are `@Accepts("user")` —
`/internal/session`, `/internal/messages`, `/internal/backfill` all forward an
end user's token. The report is `@Accepts("platform")`, and mixing credential
classes inside one controller means the class-level decorator stops being the
answer to "who may call this". `dispatch.controller.ts` is the precedent: a
separate controller for the platform-credentialled routes.

## Phases

**Phase order puts the separable half last**, the rule chapter 3.8 established
and 3.10 followed: three of Part 3's four splits were discovered mid-chapter, and
sequencing the seam last is what lets the size decision be made against a counted
page instead of an estimate.

**Numbered as `tasks.md` will number them**, because one sequence described twice
with two numbering schemes is a trap for whoever reads them in order.

| Phase | Content | Maps to |
|---|---|---|
| 1 | Baseline: the lane's current counts, timings and coverage, before anything changes | — |
| 2 | Foundational: the migration, the schema, `minuteOf`, the third key in three enumerations, the protocol schemas | FR-001, FR-002, FR-003, FR-013, FR-014 |
| 3 | The credential: one per service, the gateway's compose and turbo entries, `service` stops being a constant | FR-011 |
| 4 | **US1** — the meter, the close path, the report route, the credit, the flush test, and the coverage the ratchets will ask for | FR-001 to FR-005, FR-009, FR-010, FR-026, FR-004 |
| 5 | **US2** — replay, loss, reordering, the kill, the signal handler and its flush, the isolation of a failed report | FR-006 to FR-008, FR-012, FR-029, FR-031 |
| 6 | **US3** — the cap at the door, the fourth outcome, the 402 and the 4008, the degradation tests, the overshoot bound | FR-015 to FR-020, FR-025, FR-030 |
| 7 | **US4** — the third dimension's crossings and emails, scoped to their own rows | FR-021 to FR-023, FR-027, FR-032 |
| 8 | Verification: the guard prediction, the connect-path measurement, twenty lane runs, the dimension-cost count | SC-012, SC-013, SC-014, FR-024, FR-027 |
| 9 | The chapter in English, and the size count | SC-015, FR-019, FR-028 |
| 10 | Publication: the fences, their routing, and both locales | — |
| 11 | Close-out: the plan table, traceability, the notes, the tag | — |

**Phase 7 is the seam.** It is the fourth telling of the outbox and, for this
chapter, almost entirely reuse: a new value in an existing column, a new branch
in existing copy, an existing UNIQUE constraint doing the work. A reader who
stops before it has the chapter's subject, which is metering a duration from a
service that cannot write. If Phase 9's count comes in over 4,000 words, Phase 7
moves out and Phase 6 goes with it — the cap and the email are the two halves
that read as one chapter.

**Phase 3 is early on purpose.** The credential gates every integration test in
Phases 4 to 7: a report cannot be sent, so a figure cannot be credited, so
nothing downstream can be tested. Discovering that after writing the meter would
mean writing the meter's tests twice.

## Complexity Tracking

| Thing | Why it is here | Cheaper alternative rejected because |
|---|---|---|
| `usage_connections`, a fourth usage table | A repeated report has to credit nothing, and knowing that requires remembering what was already credited (FR-006) | Remembering minutes instead of connections is 43.2M rows a month at a thousand concurrent sockets (R4). Trusting the caller not to retry is not a mechanism |
| A second credential variable | `PlatformPrincipal.service` is documented as "which internal service presented it" and is a hardcoded `"dispatcher"`; a second caller makes the field wrong (R1a). One secret shared between them also lets the more exposed service set the blast radius for both | A caller-asserted service header is the pattern chapter 3.2 spent itself removing, and "only for logs" is the sentence it survives under |
| Retaining a closed connection's final total until a report is accepted | A closed connection has no next report to repair a lost one, so R3's "totals repair themselves" reasoning stops applying exactly there (R19) | Reporting synchronously from the `close` handler puts an HTTP call in the one place already documented as "the last place that should throw", and turns a mass disconnect into a burst of requests. Dropping the total instead makes reconnect churn free, which is what R2 chose the bucket model to prevent |
| A SIGINT/SIGTERM handler in the gateway, and `sessions.close()` becoming async | Nothing in the gateway calls `server.close()`, so the flush FR-008 and `contracts/metering.md` §5 promise had no path that runs. The dispatcher's `main.ts:313` is the precedent (R11) | Leaving it means the guarantee is prose. Firing the flush without awaiting it is the same non-guarantee moved one line down: the process exits first |
| Emitting close code 4008, and inverting a test chapter 3.8 shipped | EIR-WS-06 requires a close code for quota exhaustion; 4008 has been declared and unemitted for nineteen published chapters; a browser cannot read a raw HTTP refusal on a failed upgrade (R21) | Forwarding the 402 onto the socket keeps a shipped test green and leaves the requirement open, in the chapter whose subject it is |
| Three coverage ratchet entries and the tests to earn them | `repository.ts` is pinned at branches 90 and went red in chapters 3.5 and 3.6 for exactly this reason; pure decision files are pinned at 100 by a convention with a written reason each time (R23) | Discovering it in Phase 8 is what 3.5 and 3.6 both did, and both had to write the tests anyway with four phases stacked on top |
| A second timer in the gateway | Billing cadence and liveness cadence are different requirements; the heartbeat's 30s comes from EIR-WS-04's death detection (R10) | Reusing the heartbeat makes one number answer to two requirements, and the next change to either argues with the other |
| A fourth `Authentication` outcome | A 402 currently becomes `ApiError` → `unavailable` → close 1011, which tells the client we are broken and that retrying will help. Both wrong (R6) | Mapping 402 to `refused` closes 4001, "your credential is bad", which is also wrong and is the answer a client will act on by re-authenticating for ever |
| `recordCrossings` and `organisationOf` extracted from `Repository` | The report route is platform-credentialled and `Repository` is environment-scoped by construction; the notification machinery is behind scoping the route cannot satisfy (R8) | Copying the crossing logic into the platform path is a fifth place that has to agree about thresholds. `usageFor` already sets the precedent for a standalone admin-surface function |
| A read added to the connect path | It is where the cap has to be enforced, because that is the operation the dimension meters | Chapter 3.10's H2 protected this path from a usage join and was right to for *sends*. Enforcing connection-minutes on the send path would leave an idle listener burning the metered resource with no brake (spec Assumptions) |
