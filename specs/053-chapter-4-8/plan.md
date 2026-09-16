# Implementation Plan: chapter 4.8, "the log a customer can search"

**Branch**: `053-chapter-4-8` | **Date**: 2026-09-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/053-chapter-4-8/spec.md`

**Read `research.md` first.** Eight of its ten items were measured against the running store or
the tree, and two of them change the chapter's shape: `quantile()` is approximate at every
sample size and worst at the smallest, and the platform's existing pagination cursor stands on a
column the analytical log does not have.

---

## Summary

Chapter 4.4 built FR-ANL-07's producer and nothing reads it. This chapter builds the read: a
tenant-scoped, paged, windowed query over `relay_analytics.api_requests`, served by the api
behind the same guard every customer-facing route already uses.

FR-ANL-10 is the other half of the brief and it cannot be built as written. The quantity it
names has never been defined, its column has never had a producer, and the one latency the store
holds measures a different thing by a comment written at the time. The chapter defines the
quantity, records the two readings it does not take, and amends FR-ANL-10 rather than publishing
a percentile of something else.

## Technical Context

**Language/Version**: TypeScript, Node 22, as the rest of the platform
**Primary dependencies**: NestJS (api only, ADR-15), Zod for the query schema,
`services/api/src/metering/clickhouse.ts` for the store read — no new dependency
**Files this touches that carry titled fences**: `services/api/src/app.module.ts` — **11 per
locale, and already a HEAD problem at line 20**, so registering the controller will read as
costing the chain nothing while the file drifts further (4.7's `vitest.coverage.config.mts`,
measured in advance this time). Everything else the feature adds is a new file.
**Storage**: `relay_analytics.api_requests` — 11,684 rows, 152 attributed tenants, 30-day TTL,
`ReplacingMergeTree` ordered `(environment_id, ts, request_id)` with `allow_nullable_key = 1`
**Testing**: vitest, unit for the schema and cursor arithmetic, integration against the store
**Target platform**: the api service, one new controller and one new reader
**Project type**: three repositories — `relay` (docs/specs), `relay-platform` (code),
`relay-tutorial` (chapters and gates)
**Performance goals**: FR-ANL-08's 2 s at p95 over 90 days. **Not exercisable at lane volume**
— the largest tenant holds 208 rows (R7) — so the chapter states the bound it measures against
**Constraints**: 60.45% of the log has no tenant and can never be served (R5); the page read
floor is one granule, 8,194 rows (R6); a caller-supplied window reaches a SQL string (R9);
**every read carries `FINAL`** because the engine is a `ReplacingMergeTree` that held a
duplicate key when this feature opened (R13); and **FR-ANL-08's 90-day window cannot be
reached in this table at any volume** — a row inserted 60 days old vanishes on INSERT (R14)
**Scale/Scope**: one controller, one reader, one schema, one contract document, one chapter

---

## Constitution Check

| Principle | Verdict | Reason |
|---|---|---|
| **I — Tenant isolation** | **PASS on three bullets, and the fourth was missed for five passes** | Every statement filters on the principal's `environmentId`. The surface can reach neither another tenant's rows nor the 7,063 tenantless ones, and the isolation test asserts on a second tenant's planted rows rather than on a count — the form 4.4 and 4.7 both used. **The clause's fourth bullet is also a MUST**: *"an automated cross-tenant access test suite MUST attack every endpoint with foreign IDs on every build."* That suite is `services/api/src/isolation/`, it derives its targets from the live router, and it fails on any route with no classification — so registering this controller turns it red until `targets.ts` carries an entry. This row read PASS on the first three bullets through five analysis passes. FR-029 and T028a–T028d close it. |
| **II — No acknowledged message lost** | **N/A** | Read-only. No write path is touched. |
| **III — Two data paths, never crossed** | **PASS on the first clause, and the second one needed work** | *"…billing, metering, and **dashboard analytics** read only from the analytical store."* A customer-facing request log is dashboard analytics reading ClickHouse — the clause's central case. Chapter 4.7's conflict was about an auditor reading **both** stores (`gaps.md` 052-6); nothing here reopens it. **But the clause has a second sentence** — *"failure or backlog of the analytical pipeline MUST NOT affect … API availability"* — and neither ClickHouse client sets a timeout, so the first draft of this plan put an unbounded read on a customer request path. FR-025 and T023a/T023b bound it. Found at analysis pass 3, after two passes had marked this row PASS on the first sentence alone. |
| **IV — Single writer** | **PASS** | Nothing is written. The api already holds the only ClickHouse client an operational service has (chapter 4.7); this adds a second caller of it, not a second client. |
| **V — API-first** | **PASS, and it is the chapter's subject** | The surface is a documented contract with a stated order, a stated page bound and a stated retention edge. `contracts/request-log.md` is written before the route. |
| **VI — Test coverage** | **PASS with a pin** | New files pinned per-file in `vitest.coverage.config.mts` with two observations each, and both halves of the threshold probe run. The lane now reports on a red run (`reportOnFailure`, chapter 4.7), so the pins bind. |
| **VII — Governance** | **PASS, with one amendment owed** | FR-ANL-10 is amended rather than approximated, following revisions 1.12–1.14. Constitution III's own amendment stays 052-6's. |

**No violation requires justification.** The one gate that is weaker than it looks is VI's
100%-branch clause for tenant isolation: the branch here is a `WHERE` predicate rather than a
conditional, so it is met by a test that proves the filter, not by a covered arm.

---

## Phases

### Phase 1 — Premises and openings (blocks everything)

Every number this chapter publishes is taken twice: once now and once at the close. Chapter
4.7's opening figures moved while its own phases ran, and its record says so.

- The eleven gates, each lane run **directly** — `pnpm test:integration` runs three of its six
  lanes (`gaps.md` 051-3), so turbo's summary is not the opening.
- `check:fences` with both HEAD classes split (`gaps.md` 050-4).
- The store: row counts, tenantless share, internal share, per-tenant distribution, TTL read
  from `SHOW CREATE TABLE` rather than from a pattern (chapter 4.6's `engine_full` lesson).
- Re-check every premise in `research.md` that was measured more than a day before this phase.

### Phase 2 — The query contract, with no store in sight (blocks 3)

The same split chapter 4.7 used, and for the same reason: the half that can be unit-tested is
the half worth separating.

- The Zod schema: window, cursor, direction, limit — reusing `historyQuerySchema`'s shape
  (R3) rather than inventing a second one.
- Cursor encode/decode over `(ts, request_id)`, with the millisecond-tie case (R3: 43 pairs,
  91 rows, worst 3) driven by a unit test.
- The refusal cases: a limit above the maximum, a window whose end precedes its start, a
  malformed cursor, and a window older than retention.
- **A hostile-window test that goes red against an unvalidated version first** (R9).

### Phase 3 — The reader and the route (blocks 4) 🎯 MVP begins

- A reader at `services/api/src/request-log/reader.ts` — the directory chapter 4.4 already
  created for the producer — taking a validated query and returning rows. Read-only, and the
  tenant id is an argument rather than a string in the SQL. It calls
  `services/api/src/metering/clickhouse.ts`'s client; it does not open a second one.
- **Every read carries `FINAL`.** The engine is a `ReplacingMergeTree` and the lane held one
  duplicate key at this feature's opening; without it a page repeats a request until a merge
  runs, which would make FR-007's assertion a statement about merge timing. Same rule as
  chapter 4.6's `sum()` with `GROUP BY`, one engine over.
- **The statement carries a presence column, because TSV cannot say null.**
  `AnalyticalStore.query` returns `string[][]` split from a TSV body, and ClickHouse writes
  NULL as the two characters `\N`. Selecting `endpoint IS NULL` beside `endpoint` is the same
  move chapter 4.7 made with `count()`: give absence its own signal instead of a value someone
  has to interpret.
- The controller: `@UseGuards(CredentialGuard)` and the `Accepts` decision from R4, stated with
  its argument rather than copied.
- The response envelope, matching the contract document written in phase 2.
- Integration tests against the real store, every statement naming its own environment ids
  (`gaps.md` 050-2 — the analytical store has no lane guard).

### Phase 4 — What the log can and cannot show 🎯 MVP (Priority: P1)

- Tenant isolation: two planted tenants, the assertion on the second's rows.
- Tenantless rows unreachable from every tenant.
- The `/internal/*` decision, implemented and asserted whichever way it goes (R5).
- The retention edge: "no requests" told apart from "outside retention" (R8).
- Paging: two consecutive pages, no row in both, every row once.
- Coverage pins with two observations and both halves of the threshold probe.
- Run the four lanes and `pnpm coverage`; commit.

### Phase 5 — The percentile requirement, resolved rather than approximated

- Define "end-to-end delivery latency" by naming its two instants, and record the two readings
  not taken with what each would cost (R1).
- Measure `quantile` against `quantileExact` at the bucket sizes FR-ANL-10 actually produces,
  and publish the table (R2 measured it at 100–1,000,000; this phase measures it at the sizes a
  per-tenant-per-hour bucket has).
- If the chosen reading has a source: compute per tenant per hour and test it. If it does not:
  record what the producer would cost and amend the clause.
- Close or restate `gaps.md` 048-2, carried through five features.

### Phase 6 — The amendments

- Amend FR-ANL-10 to what the platform can produce, or to the definition it was missing.
- Record FR-ANL-08's 90 days against FR-ANL-07's 30 where the two are read over this table.
- `docs/12` §3 row 9, first column untouched.
- `docs/05-sad.md`: the query surface in the data view, and the FR-ANL-10 sentence at :758
  re-checked — it says the column has no producer *"until FR-ANL-10"*, which this chapter
  either satisfies or falsifies.
- Re-check every cited clause by opening the SRS. Chapter 4.7 found `FR-003a` cited as a clause
  in two published documents and there is no `FR-003`.
- `check:docs` and `check:srs`, and **check the SRS version header by looking at it**.

### Phase 7 — The numbers, and the chapter

- Title and slug fixed once, four strings recorded.
- The chapter, at least one `<Trap>`, 2,000–4,000 prose words outside code fences.
- Registration in `lib/tutorial.ts` — **assert the anchor is unique before editing** (4.4 shipped
  a site that did not build; 4.6 and 4.7 both checked first).
- Figures in `figures.ts`, passed as `code=`, every number from `baseline.txt`.
- Fences: new files whole, changed files as `diff` hunks against `part4-ch7`. **A `diff` fence
  carries the `@@` hunks only** — chapter 4.7 lost two attempts to the `--- a/` headers.
- Eleven gates, `gaps.md`, `traceability.md`, `CLAUDE.md`, tag `part4-ch8`, push.

---

## Dependency order

```
Phase 1  premises + openings         ── blocks everything
Phase 2  the contract, pure          ── blocks 3
Phase 3  the reader and the route    ── blocks 4
Phase 4  what the log can show  🎯MVP ── blocks 5
Phase 5  the percentile              ── needs 4's shape, not its data
Phase 6  the amendments              ── needs 5's decision
Phase 7  the chapter                 ── needs all
```

**MVP is phases 1–4**: a customer can read their own request log, paged and windowed, cannot
read anyone else's, and is told when the window they asked for is older than the log. US3 is P1
for that last clause — a zero from an emptied window and a zero from a quiet week are the same
number, and a log that cannot tell them apart answers the wrong question confidently.

---

## Complexity tracking

**One new dependency: none.** The store client exists (chapter 4.7), the guard exists, Zod
exists, and the pagination shape exists. The only new code is a schema, a reader, a controller
and their tests.

**And one task premise was false before implementation started.** The first draft of phase 4
said to plant a tenant at a volume where FR-ANL-08's 90-day clause means something. The table
refuses it: a row inserted at `now() - 60 DAY` is gone before the statement returns, because
the 30-day TTL removes rows at INSERT. So there is no fixture that makes that clause meaningful
here, and the phase records the measurement and hands the clause to the amendments instead of
building something that cannot exist.

**One thing that looks like scope and is not.** Phase 5 may end with no percentile computed at
all. That is a complete outcome rather than an abandoned phase: FR-ANL-10's quantity has never
been defined, and defining it — with the readings not taken and the cost of each recorded — is
the work. Chapter 4.6 closed Appendix C question 4 the same way, by settling a unit before
anything billed one.

**And one risk the plan names rather than discovers.** The `/internal/*` decision (R5) is a
product question wearing a filter's clothes. Whichever way it goes, one of FR-ANL-01's *"every
request"* and FR-ANL-07's *"per tenant"* is served less well, and the chapter's job is to say
which and why — the same shape as 4.4's third reading of constitution I.
