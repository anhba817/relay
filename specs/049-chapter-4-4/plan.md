# Implementation Plan: chapter 4.4 — every request is an event

**Feature dir**: `specs/049-chapter-4-4/` | **Date**: 2026-09-14 | **Spec**: [spec.md](./spec.md)
**Branch**: `main` (this project ships chapters on `main` and tags them; see CLAUDE.md)

**Read `research.md` first.** Six of its sixteen items were measured against the running
stack, and three of those changed the design before a line was written.

## Summary

Give the api a producer that publishes one analytical record per request, land those records
in a 30-day ClickHouse table, and stop the ingester destroying them on the way. FR-ANL-07's
producer; its query surface is movement IV's.

The chapter's argument is that **"every request" and "per tenant" are not the same
population**, and that the gap is widest exactly where the traffic is: the dispatcher's and
gateway's calls to the internal seam carry a principal whose `environmentId` is undefined by
design, and that design is correct. Constitution I says every analytical record must carry a
non-null tenant. R7 is where those two meet.

## Technical Context

**Language/Version**: TypeScript 5.x, Node 22, `"type": "commonjs"` in `services/api`,
`"type": "module"` in `services/ingester`.

**Primary Dependencies**: NestJS 11.1.28 on `@nestjs/platform-express`, **Express 5.2.1**
(not 4 — the middleware mounts with `{*path}` for that reason), `nats` 2.29.3, ClickHouse
25.3 over its HTTP interface with no client package.

**Storage**: ClickHouse `relay_analytics`, reached through 4.2's `analytics/apply.mjs`
ledger. PostgreSQL is not touched on this path (constitution III).

**Testing**: vitest — unit in the api's lane, integration against the live stack via
`vitest.integration.config.mts`.

**Target Platform**: Linux, `compose.yaml`, `RELAY_POSTGRES_PORT=15432`.

**Performance Goals**: the producer must not move NFR-PRF-02's p95 < 150 ms. The measurement
is the chapter's, taken with the broker up and with it stopped.

**Constraints**: the publish is not awaited on the request path; no request or response body
reaches the record; no PostgreSQL query on this path.

**Scale/Scope**: one new middleware in `services/api`, one new protocol function, routing in
`services/ingester`, one `.sql` file, one SRS amendment, one SAD amendment, one `docs/12`
amendment, one chapter.

## Constitution Check

*GATE: must pass before Phase 0. Re-checked after Phase 1 — see the bottom of this file.*

| Principle | Bearing | Verdict |
|---|---|---|
| **I. Tenant isolation (NON-NEGOTIABLE)** | *"Every persisted operational and analytical record MUST carry a non-null tenant identifier."* FR-009 requires a record for requests that have none. | **GATE — resolved by R7, not waived.** The clause governs tenant data; a record with no tenant is unreachable by any tenant-scoped filter, measured in R3b. Carried into FR-010 as a test rather than a claim. If the reading is rejected, FR-009 falls and FR-ANL-01 is amended instead. |
| **III. Two data paths** | The producer is on the request path — the first one that is. | **PASS by construction, verified by measurement.** The publish is not awaited; SC-002 measures request latency with the broker stopped. No PostgreSQL on this path. |
| **III, content clause** | *"MUST NOT contain message text."* | **PASS, and it forces an SRS amendment.** R8: FR-ANL-07's "truncated payload" cannot hold. |
| **VI. Requirement-driven, test-verified** | 70% coverage; tenant isolation at 100% branches. | **PASS with a stated measurement.** The tenancy branch — environment present, environment absent — is the one constitution VI names, and its coverage is published as a number, met or pinned. |
| **VII. Boring by design** | A new middleware, a new table, no new dependency. | **PASS.** Nothing here needs a language or a package the platform does not have. |
| **I, subject tokens** | An environment id becomes a subject token. | **PASS and strengthened.** R3a measured a dot-bearing token producing a subject one level deeper that no intended filter matches. `analyticsSubjectFor`'s UUID refusal stays; the tenantless case gets its own function rather than a relaxed argument. |

**No violation requires justification.** The one gate is I, and it is resolved by naming which
records the clause governs — not by diluting it. Complexity Tracking is therefore empty and
omitted.

## Project Structure

### Documentation (this feature)

```text
specs/049-chapter-4-4/
├── plan.md              # this file
├── research.md          # R1–R16, six measured
├── data-model.md
├── quickstart.md
├── contracts/
│   └── api-request-event.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks
```

### Source (three repositories)

```text
relay-platform/
├── packages/protocol/src/internal.ts        API_REQUEST_ACTION, apiRequestSubject,
│                                            and the tenantless arm
├── services/api/src/
│   ├── analytics/request-event.ts           NEW — shape() + publishRequest()
│   ├── analytics/request-event.test.ts      NEW — unit, the tenancy branch at 100%
│   ├── analytics/request-analytics.middleware.ts   NEW — assembles on finish
│   ├── analytics/request-analytics.itest.ts NEW — integration against the broker
│   └── app.module.ts                        the middleware chain gains one entry
├── services/ingester/src/
│   ├── shape.ts                             route by `type`; absent means attempt
│   ├── shape.test.ts                        the compatibility rule, tested
│   ├── clickhouse.ts                        a second table
│   └── main.ts                              two row buffers, one fetch loop
├── analytics/0004_api_requests.sql          NEW — 30-day TTL
└── vitest.coverage.config.mts               per-file pins for the new files

relay/
├── docs/04-srs.md                           FR-ANL-07 amended (R8)
├── docs/05-sad.md                           the 24 h claim amended (R4)
└── docs/12-part-4-structure.md              §4's five references (R16)

relay-tutorial/
└── app/(en)/part-4/chapter-04/<slug>/       page.mdx + figures.ts
```

**Structure Decision**: the producer lives in a new `services/api/src/analytics/` directory
rather than inside `request-context.middleware.ts`. R9 has the argument: that middleware's
contract is a log line and a header, it is cited by EIR-API-05 and NFR-OBS-06, and it is
fenced in the tutorial. A second middleware registered after it reads the request id the
first one set.

## Phases

Six, and the order is an argument. **The consumer is fixed before the producer exists**,
because publishing into a consumer that terminates the record is shipping a defect and then
fixing it.

| # | Phase | What it settles |
|---|---|---|
| 1 | **Baseline and the premises** | `baseline.txt`: the stack's state, the fence-chain opening broken down by kind and locale, the api's route inventory by principal class, and R4's eviction number re-run in this environment. Re-run every premise the spec cites. |
| 2 | **The consumer stops destroying records** | R11's `type` routing in `shape.ts`, with the absent-`type`-means-attempt compatibility rule tested. Proves R1's finding red first, then green. Nothing publishes yet. |
| 3 | **The table** | `0004_api_requests.sql` through 4.2's ledger; `toDateTime` TTL, the `ts_is_real` constraint, the sorting key ending at `request_id`. The ingester writes it. |
| 4 | **The producer** | The protocol function and its tenantless arm; the middleware; the tenancy branch at the coverage constitution VI asks for. The first end-to-end request-to-row. |
| 5 | **The numbers and the amendments** | Latency with the broker up and stopped; the tenantless share, volume-weighted; the health-check share; the eviction rate against the SAD's 24 h. Then FR-ANL-07, the SAD and `docs/12` §4. |
| 6 | **The chapter** | Prose, figures, fences, the eight gates, the fence delta, the tag. |

**MVP is phases 1–4.** A record for every request, in a table, not destroyed. Phase 5 is what
makes the chapter worth reading and phase 6 is the chapter.

## Risks carried into tasks

- **The ingester change touches a live consumer.** `analytics-ingester` exists on the real
  stream with 37 records written by a binary that never heard of `type`. R11's compatibility
  rule is the mitigation and it needs a test that plants one of those records.
- **R4 may force a stream split mid-feature.** R12 is deliberately unsettled. If the measured
  rate says split, R2 says the split is a subject-list narrowing on a published stream with a
  live consumer, and that is a phase of its own rather than a line.
- **`req.route.path` is safe because of how these controllers are declared.** R6 measured
  both arrangements; a task asserts the property rather than assuming it survives.
- **The 2,000–4,000 word bound.** Movement III's first chapter carries R7's constitutional
  argument, R8's clause conflict and R4's number. 4.3 came in under the floor at 1,659 words
  on its first draft and 4.1's estimate ran high. **Every Part 4 estimate so far has been
  wrong downward**, and this one is expected to run the other way.

## Constitution re-check after Phase 1 design

Re-evaluated against `data-model.md` and `contracts/api-request-event.md`:

- **I** — the contract carries no field that could hold another tenant's data, and the
  tenantless record's subject is measured unreachable by exact-match tenant filters (R3b).
  The data model states the column's nullability as the open decision it is.
- **III** — the contract's field list has no body, no header and no credential, and the
  publish is specified as not awaited. Unchanged.
- **VI** — the contract names the branch that must reach 100%.
- **VII** — no dependency added; `grep -c clickhouse pnpm-lock.yaml` stays at 0.

**No new violations.** The gate on I is resolved as recorded above, and it is the chapter's
subject rather than a footnote in it.
