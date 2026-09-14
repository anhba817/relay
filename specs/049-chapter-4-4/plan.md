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
│   ├── request-log/event.ts                 NEW — toRequestEvent() + publishRequest()
│   ├── request-log/event.test.ts            NEW — unit, the tenancy branch at 100%
│   ├── request-log/request-log.middleware.ts       NEW — assembles on finish
│   ├── request-log/request-log.itest.ts     NEW — integration against the broker
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

**Structure Decision**: the producer lives in a new `services/api/src/request-log/` directory
rather than inside `request-context.middleware.ts`. R9 has the argument: that middleware's
contract is a log line and a header, it is cited by EIR-API-05 and NFR-OBS-06, and it is
fenced in the tutorial. A second middleware registered after it reads the request id the
first one set.

**The producer is registered SECOND in the chain, not last.** `RateLimitMiddleware` refuses a
429 with `res.end(); return;` and never calls `next()`, so a middleware in position 4 is never
reached — and a rate-limited request is exactly the one an operator opens a request log to find.
Registered second it attaches its `finish` listener before anything can short-circuit, and reads
`req.principal` when the listener fires rather than when it is attached. **Attach early, read
late**; the gap between the two moments is what makes both the authenticated and the refused
request produce a correct record.

**And `ANALYTICS_PUBLISHER` has to be provided in `AppModule`.** It is declared in
`webhooks/analytics.ts` but *provided* only in `InternalModule`, which has **no `exports:`
array** — so a middleware configured in `AppModule.configure()` cannot inject it and Nest fails
at boot. `internal.module.ts` writes the rule down twelve lines below that provider: *"a
provider is visible to the module that declares it and to nothing it imports."* A second
provider with the same factory follows `LOGGER`'s precedent in the same file, and costs a second
NATS connection and a second `ensureAnalyticsStream` call at boot.

**`request-log/`, not `analytics/`, and `toRequestEvent()`, not `shape()`.** Both were
`analytics`/`shape` in the first draft of this plan, which would have put a second "analytics"
home in a service that already has `webhooks/analytics.ts`, and made `shape()` the **third**
function of that name on one data path — record-to-wire in `webhooks/analytics.ts`,
wire-to-row in `ingester/src/shape.ts`, and this one. FR-ANL-07's own word is *request log*,
and 048's central defect was a silent mismatch across exactly the wire-to-row boundary those
three names straddle.

## Phases

Seven, and the order is an argument. **The consumer is fixed before the producer exists**,
because publishing into a consumer that terminates the record is shipping a defect and then
fixing it.

**This was six when the plan was first written.** `/speckit-tasks` split the producer phase in
two: US1 (a record for every request) and US3 (a record for the requests with no tenant) have
different independent tests, and US3 carries the constitution I argument. Folding them into
one phase would have made the gate on principle I a task inside somebody else's phase.

| # | Phase | Story | What it settles |
|---|---|---|---|
| 1 | **Premises and the numbers inherited** | — | `baseline.txt`: the stack, the fence-chain opening by kind and locale, the route inventory by principal class, and every `research.md` figure re-run at this tag. |
| 2 | **The consumer stops destroying records** | US4 | R11's `type` routing, with the absent-`type`-means-attempt compatibility rule tested. R1's finding proved red, then green. Nothing publishes yet. |
| 3 | **The table** | — | `0004_api_requests.sql` through 4.2's ledger; `toDateTime` TTL, `ts_is_real`, the sorting key ending at `request_id`. |
| 4 | **The producer** | US1 | The protocol function, the middleware, the first request-to-row. **MVP ends here.** |
| 5 | **The requests with no tenant** | US3 | The `_none` arm, `principal_kind`, the isolation test, and the tenancy branch at the coverage constitution VI names. |
| 6 | **The path never costs a response** | US2 | Latency with the broker up and stopped, as two distributions; the status codes served while it was down. |
| 7 | **The numbers, the amendments, the chapter** | — | The eviction rate, the health-check share, FR-ANL-07, the SAD's 24 h, `docs/12` §4, then prose, fences, gates and the tag. |

**MVP is phases 1–4.** A record for every request, in a table, not destroyed by the consumer
that was there first. Phases 5 and 6 are what make it correct rather than working — US3 is the
constitution I argument and US2 is the constitution III one — and phase 7 is the chapter.

## Risks carried into tasks

- **A coverage pin on the ingester cannot fail, and this chapter edits the file it names.**
  `services/ingester/src/main.ts` is pinned and excluded in the same config; measured, 1 of 45
  pins is unbindable and it is that one. Phase 2 splits `ingestOnce` into `ingest.ts` before
  touching it, and runs **both halves** of the threshold probe — the half that proves the key
  binds is the one 048 skipped (R23).
- **The ingester change touches a live consumer.** `analytics-ingester` exists on the real
  stream with 36 records written by a binary that never heard of `type`. R11's compatibility
  rule is the mitigation and it needs a test that plants one of those records.
- **R4 may force a stream split mid-feature.** R12 is deliberately unsettled. If the measured
  rate says split, R2 says the split is a subject-list narrowing on a published stream with a
  live consumer, and that is a phase of its own rather than a line.
- **`req.route.path` is safe because of how these controllers are declared.** R6 measured
  both arrangements; a task asserts the property rather than assuming it survives.
- **A premise that came back clean, recorded because a clean one is evidence.**
  `app/(vi)/part-4/` is **empty** — Part 4 has no Vietnamese chapters, and 4.1 through 4.3
  shipped `(en)` only. So this chapter adds no vi page and the thirty vi fences in the
  opening 110 are all Part 3 and earlier. That is what makes the locale breakdown the right
  instrument rather than a precaution: the vi total moves under translation and this chapter
  can never be the cause.
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
