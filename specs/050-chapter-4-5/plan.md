# Implementation Plan: chapter 4.5 — the gateway's first stream

**Feature dir**: `specs/050-chapter-4-5/` | **Date**: 2026-09-14 | **Spec**: [spec.md](./spec.md)
**Branch**: `main` (this project ships chapters on `main` and tags them)

**Read `research.md` first.** Four of its ten items were measured, and two changed the design
before anything was written: a publish per close is 2.3 seconds at NFR-SCL-01's connection
count, and the two connection-minute counters measure different quantities.

## Summary

Give the gateway a broker client and emit an analytical event when a connection opens and when
it closes — FR-ANL-01's last arm without a producer. Buffer and publish on a tick rather than
from the close handler, because `meter.ts` already solved this shape and the numbers say the
same answer applies to a broker.

The chapter's argument is that **the gateway already had a path for connection data and it was
built for a different question.** The existing one computes wall-clock minutes for a quota that
must refuse synchronously; this one records events for a store that must not. Both stay, and
the reconciler that compares them is movement IV's.

And ADR-07's rejection of NATS rests on a count this chapter increases by one.

## Technical Context

**Language/Version**: TypeScript 5.x, Node 22. `services/gateway` is ESM.

**Primary Dependencies**: `ws`, `ioredis`, `jose`, `@relay/protocol`, `@relay/service-kit` —
five, none of them a broker client. This chapter adds `nats`, taking it to six, and that number
is the subject of FR-011 rather than a detail of it.

**Storage**: ClickHouse `relay_analytics`, through 4.2's ledger and 4.3's ingester. The
gateway writes to neither directly.

**Testing**: vitest. The gateway's lane runs four files at a time (045-79).

**Target Platform**: Linux, `compose.yaml`, `RELAY_POSTGRES_PORT=15432`.

**Performance Goals**: NFR-SCL-01 is 10,000 concurrent connections per gateway instance at
160 MB RSS. A publisher that moves either number is a publisher that has to justify it.

**Constraints**: no publish inside a socket handler; no credential or message content in a
record; the meter and the quota path unchanged.

**Scale/Scope**: one dependency, one publisher, two record types, one ingester arm, one ADR
amendment, one chapter.

## Constitution Check

*GATE: must pass before Phase 0. Re-checked after Phase 1 — see the bottom of this file.*

| Principle | Bearing | Verdict |
|---|---|---|
| **I. Tenant isolation (NON-NEGOTIABLE)** | Every record carries an environment, taken from the resolved identity. | **PASS, with one open case.** A connection that never authenticates has no identity; R5 leaves whether it produces a record to phase 1 rather than assuming. 4.4's `_none` arm is for requests and is not reused without an argument. |
| **III. Two data paths** | The gateway is the service where a blocking publisher is most expensive: it holds long-lived sockets. | **PASS by construction, verified by measurement.** Nothing publishes from a handler; SC-002 measures connection outcomes with the broker stopped. |
| **III, separation** | The quota counter must refuse synchronously and cannot move downstream of a lossy queue. | **PASS.** FR-007 keeps `/internal/usage/connections` unchanged; the two counters coexist and movement IV reconciles them. |
| **VI. Requirement-driven** | 70% coverage; tenant isolation at 100% branches. | **PASS with a stated measurement**, as 4.4 did — the tenancy branch is coverable here too. |
| **VII. Boring by design** | A sixth dependency on the gateway. | **PASS, and argued rather than assumed.** It is the same broker client three other services hold, not a new mechanism. But ADR-07's rejection of NATS *is* a count of gateway dependencies, so VII's "scope is a commitment" is exactly what FR-016 is about. |

**No violation requires justification.** Complexity Tracking is empty and omitted.

## Project Structure

### Documentation (this feature)

```text
specs/050-chapter-4-5/
├── plan.md              # this file
├── research.md          # R1–R10, four measured
├── data-model.md
├── quickstart.md
├── contracts/
│   └── connection-event.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source (three repositories)

```text
relay-platform/
├── packages/protocol/src/internal.ts          CONNECTION_ACTION and its subjects
├── services/gateway/
│   ├── package.json                           the sixth dependency
│   └── src/
│       ├── connection-log/event.ts            NEW — toConnectionEvent() + a buffer
│       ├── connection-log/event.test.ts       NEW — unit, tenancy branch at 100%
│       ├── connection-log/publisher.ts        NEW — one client, lazy, shared
│       ├── connection-log/connection-log.itest.ts  NEW
│       ├── session.ts                         two hand-overs beside meter.opened/closed
│       └── main.ts                            the publisher's lifecycle
├── services/ingester/src/
│   ├── shape.ts                               a third arm on route()
│   └── ingest.ts                              a third buffer
├── analytics/0005_connection_events.sql       NEW
└── vitest.coverage.config.mts                 per-file pins for the new files

relay/
├── docs/05-sad.md                             ADR-07 amended a third time
└── docs/04-srs.md                             only if a measurement falsifies a clause

relay-tutorial/
└── app/(en)/part-4/chapter-05/<slug>/         page.mdx + figures.ts
```

**Structure Decision**: the producer lives in `services/gateway/src/connection-log/`, beside
`meter.ts` rather than inside it. The meter's contract is connection-minutes for a quota, it is
fenced in chapter 3.24, and it reports to the api — three reasons not to hang a broker off it.
The two sit side by side and `session.ts` hands to both, which is also what makes the
reconciliation in FR-009 a comparison of two independent computations rather than of one
computation with itself.

## Phases

Six. The order puts the dependency decision first, because it is the one that cannot be undone
quietly.

| # | Phase | Story | What it settles |
|---|---|---|---|
| 1 | **Premises and the dependency** | — | `baseline.txt`: the gateway's dependency count, R3's burst numbers re-run, the fence-chain opening by kind and locale, and the ADR-07 text quoted from the document rather than from `docs/12`. |
| 2 | **The records exist** | US1 | The protocol subjects, the event shapes, the buffer, and the hand-overs in `session.ts`. Published to a stream nothing writes yet — R8 says the ingester's `unclaimed` arm makes that safe, and this is the proof on a real record. |
| 3 | **The gateway keeps serving** | US2 | Broker stopped: connections open, carry messages and close. Outcomes published beside latencies. |
| 4 | **The store** | US1 | `0005_connection_events.sql`, the ingester's third arm, and the first connection that becomes a row. |
| 5 | **The two counters** | US3 | The meter untouched and proven so; the reconciliation computed, and the structural disagreement published as a number. |
| 6 | **ADR-07, the numbers, and the chapter** | US4 | The amendment naming the spent argument; the combined byte rate; prose, figures, fences, gates, tag. |

**MVP is phases 1–4.** A connection that opens and closes becomes two rows.

## Risks carried into tasks

- **The close handler is documented as the last place that should throw.** Anything added there
  has to be non-throwing and non-blocking, and a test should assert it rather than a comment.
- **R7's volume assumption is unmeasured.** Connection events are *assumed* rarer than request
  events. If a reconnect storm makes them commoner, the shared stream's crossover moves and
  4.4's number stops being the binding one.
- **4.4 discovered at its close that editing a fenced file costs the chain.** This chapter
  edits `session.ts`, `main.ts`, `shape.ts`, `ingest.ts` and the protocol — all fenced. FR-020
  says the chapter expects to owe hunks; phase 6 should not discover that.
- **The gateway's lane runs four files at a time**, so any whole-table or whole-registry
  assertion is a neighbour's problem. `check-lane-scope.py` is the instrument and 049-3 records
  that it points at a deleted worktree — retarget it or it reports zero for the wrong reason.
- **NFR-SCL-01's 160 MB RSS** is a published number measured without a broker client in the
  gateway. Adding one may move it, and the chapter should say by how much rather than leave the
  figure to be re-derived by whoever next runs that battery.

## Constitution re-check after Phase 1 design

Re-evaluated against `data-model.md` and `contracts/connection-event.md`:

- **I** — every record carries an environment taken from the resolved identity; the
  unauthenticated case is named as open rather than defaulted.
- **III** — the contract states that publishing is buffered and never awaited in a handler, and
  that the meter is untouched.
- **VI** — the contract names the branch that must reach 100%.
- **VII** — one dependency, counted and argued, and ADR-07 amended rather than left resting on
  a reason this chapter spends.

**No new violations.**
