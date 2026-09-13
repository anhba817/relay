# Feature Specification: Chapter 4.2 — ClickHouse from zero

**Feature Branch**: `047-chapter-4-2`
**Created**: 2026-09-13
**Status**: Draft
**Input**: User description: "chapter 4.2"

**THIS IS NOT THE CHAPTER `docs/12-part-4-structure.md` CALLED 4.2 WHEN IT WAS WRITTEN.** That
document specified movement I as two chapters — the question and the harness, then the
counterfactual and the verdict. **Chapter 4.1 shipped with both at 2,132 prose words**, inside
the 2,000–4,000 bound, because the counterfactual turned out to be four numbers and a plan
rather than a sitting's worth of argument. Movement I is one chapter, Part 4 is **23**, and
every ordinal after the first has moved down by one. Both records were amended before this spec
was written.

**It is the first estimate this project has made that was too high.** Part 3 was planned as
seven chapters and shipped 26; `docs/12` §3 still carries the warning that 23 will not be 23.
The churn §2.1 accepted turns out to be symmetric, and nobody had said so.

## What 4.1 leaves on the table

The predecessor asked Postgres FR-ANL-05's question against a million rows in the subject
environment's ninety-day window and published four numbers:

    the query                       585.9 ms, 603.4 ms      three corpora
    with the column and index       560.2 ms, 552.0 ms      a gap inside the run-to-run spread
    the fix's storage               24.8 MB column + 62.0 MB index = +49%
    the lane's answer               0.9 ms over 1,018 rows  — a factor of 651

and the plan said why the index does not help: the join is ~140 ms of a 698 ms plan and **the
sort is 656**, spilling 33 MB to disk, because `count(DISTINCT user_id)` per day orders a
million rows before it counts anything. **No index removes that sort.**

This chapter builds the store whose answer to the same question is a different shape:
`ORDER BY (environment_id, ts)` — the two columns Postgres orders by neither of — and a rollup
that maintains the distinct count as rows arrive instead of sorting for it at read time.

**It builds the store and not the pipe.** Nothing ingests yet; that is the chapter after next.
A schema with no writer is a reader with no writer, which this project has met before and which
is the right shape here: the schema is what the ingester is written against.

## What exists, and it is four lines

`clickhouse/clickhouse-server:25.3` has been in `compose.yaml` since chapter 1.2 with a
`clickhouse-data` volume and a `/ping` health check. The only reference to it in any source file
is `packages/config/src/infra.ts`, where the string `"clickhouse"` sits in `INFRA_SERVICES`
beside four other names.

**No client, no schema, no migration runner, no query.** The compose entry has been carrying a
comment since 1.2 that says what this chapter is for:

> The analytical store rides its own path (CON-01): single node in v1, schema already
> cluster-shaped (ADR-08).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The same question, answered by a store shaped for it (Priority: P1)

A reader who finished 4.1 holds a 586 ms query and a plan that says why an index will not fix
it. They create the analytical table, load the same corpus into it, and ask the same question.

**Why this priority**: it is the chapter's reason to exist and the answer to its predecessor. A
ClickHouse chapter that does not re-run 4.1's query has changed the subject.

**Independent Test**: load the corpus into the analytical table, run FR-ANL-05's question
against it, and publish the duration beside 4.1's 585.9 ms with both row counts.

**Acceptance Scenarios**:

1. **Given** the analytical table exists and holds the same events 4.1 measured, **When**
   FR-ANL-05's daily question is asked of it, **Then** its duration is recorded beside 4.1's,
   and both are stated with the number of rows each scanned.
2. **Given** the same table, **When** the query's plan is captured, **Then** it shows the
   ordering doing the work the Postgres plan's sort was doing.
3. **Given** a query naming one environment, **When** its plan is read, **Then** it shows which
   parts were skipped — the tenant predicate is the first key and a store that reads every part
   anyway is not ordered the way the table says.

---

### User Story 2 - A rollup that never scans raw events (Priority: P2)

DR-10 says materialised views maintain daily per-tenant rollups so billing never scans raw
events. The reader builds that view and asks the same question of it.

**Why this priority**: it is the structural answer to 4.1's finding. The raw-table query is
faster than Postgres; the rollup is a different claim — that the distinct count is maintained
as rows arrive and never ordered at read time.

**Independent Test**: query the rollup for the same ninety days and compare its answer, row for
row, against the raw table's.

**Acceptance Scenarios**:

1. **Given** the rollup exists and the corpus has been loaded, **When** the same ninety-day
   question is asked of the rollup, **Then** it returns the same daily figures as the raw table.
2. **Given** both are queried, **When** their durations and scanned-row counts are compared,
   **Then** the difference between them is published as a number.
3. **Given** rows are inserted after the rollup exists, **When** the rollup is queried again,
   **Then** it includes them without being rebuilt — which is what makes it a view and not a
   table somebody refreshes.
4. **Given** the distinct-user figure, **When** it is compared against the raw table's
   `count(DISTINCT user_id)`, **Then** any disagreement is reported rather than absorbed:
   the rollup keeps an aggregate state, and an aggregate state is an approximation unless it is
   shown not to be.

---

### User Story 3 - A second store's schema changes need a ledger of their own (Priority: P3)

The platform hand-writes forward-only `.sql` for Postgres and keys `schema_migrations` on the
filename. ClickHouse's DDL cannot go through that runner. The reader gives the second store a
way to change.

**Why this priority**: nothing downstream can be built on a schema that has no way to change,
and `gaps.md` 045-69 is what an identity scheme going wrong costs — seven byte-identical
migrations under different numbers and a lane that failed in 0.6 s, three times. It ranks below
the two stories that answer 4.1 because a first schema can be created before it can be migrated.

**Independent Test**: apply the schema to an empty ClickHouse twice and confirm the second run
is a no-op that reports what it found; add a change and confirm it applies once.

**Acceptance Scenarios**:

1. **Given** an empty analytical store, **When** the schema is applied, **Then** the tables and
   views exist and the run records what it applied.
2. **Given** the same store, **When** the schema is applied again, **Then** nothing is
   re-applied and the run says so.
3. **Given** a new statement added to the schema, **When** it is applied, **Then** only that
   statement runs.

---

### Edge Cases

- **The analytical store is unavailable.** NFR-REL-05 says loss of it must not affect messaging.
  Nothing in this chapter is on a request path, so the case is structural rather than handled —
  and the chapter states which it is.
- **A query that reads every part.** If the ordering is wrong or the predicate does not reach
  the first key, ClickHouse scans everything and still answers quickly at this size. **Fast is
  not the same as ordered**, and only the parts-skipped figure distinguishes them.
- **The rollup and the raw table disagree.** `uniqState` is approximate by construction. At a
  million rows the error may be zero and it will not stay zero.
- **The corpus has no `delivery_latency_ms`.** SAD §6.2's table carries a column the operational
  store has never recorded. A schema published with a column nothing can fill is a reader with
  no writer, and the chapter says which columns are in that state.
- **TTL removes rows during a measurement.** DR-09 retains raw events 90 days and the corpus
  spans 120. A table created with its TTL active drops a quarter of what was just loaded.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The analytical schema MUST be created from SAD §6.2's published DDL, and every
  divergence from it MUST be stated with the reason.
- **FR-002**: The raw event table MUST be partitioned by month and ordered by
  `(environment_id, ts)` (DR-07).
- **FR-003**: The raw event table MUST carry a 90-day TTL (DR-09), and the chapter MUST state
  what that does to a corpus spanning more than 90 days.
- **FR-003a**: The rollup MUST be stated to carry no TTL and to outlive the raw events it was
  built from, and the chapter MUST say why that is DR-09 and DR-10 working as a pair rather than
  a discrepancy: metering must not lose history when raw events expire.
- **FR-004**: A daily per-tenant rollup MUST be maintained as a materialised view so that
  metering never scans raw events (DR-10).
- **FR-005**: The rollup MUST include rows inserted after it was created, without being rebuilt.
- **FR-006**: The analytical store MUST hold no message text — only lengths, identifiers and
  metadata (FR-ANL-11, DR-08).
- **FR-006a**: Any column SAD §6.2 publishes that no producer can currently fill MUST be named
  as such rather than created silently.
- **FR-007**: FR-ANL-05's question MUST be asked of the analytical store and its answer published
  **beside chapter 4.1's 585.9 ms**, with the rows each scanned.
- **FR-007a**: The corpus the chapter loads MUST contain all three event kinds, messages with
  and without attachments, and text that is not pure ASCII, so that every figure the chapter
  publishes is reproducible by a reader who builds the corpus from the seeder. A figure measured
  on one database and published beside a store built from another is not reproducible.
- **FR-008**: The same question MUST be asked of the rollup and compared against the raw table,
  both for agreement of the figures and for cost.
- **FR-009**: The rollup's distinct-user figure MUST be compared against an exact count, and any
  divergence reported as a number rather than described.
- **FR-010**: Query plans MUST be published with durations, and MUST include how many parts were
  read and how many skipped. A duration alone cannot distinguish an ordered store from a fast one.
- **FR-011**: The analytical store MUST have a way to apply schema changes that is idempotent and
  reports what it applied.
- **FR-012**: The schema-change mechanism MUST NOT go through the Postgres runner or write to
  `schema_migrations`. The two stores' ledgers are separate.
- **FR-013**: This chapter MUST NOT build the ingester, the emission path, or any producer. It
  creates a schema and loads a corpus into it by hand.
- **FR-014**: No analytical query may run against the operational database at this chapter's tag
  (constitution III). 4.1's measurement was the deliberate exception and it is not repeated.
- **FR-015**: Every gate MUST be green at close-out, with `check:fences` reported as a **delta**
  against its opening rather than as a total.

### Key Entities

- **The raw event table**: one row per analytical event, tenant-scoped and time-ordered,
  carrying no message text.
- **The daily rollup**: per environment per day, maintained as rows arrive, holding an aggregate
  state for the distinct-user count rather than the identities behind it.
- **The schema ledger**: what has been applied to the analytical store, kept separately from
  Postgres's.
- **A comparison**: a duration, a plan, the rows scanned, the parts skipped, and the corpus it
  ran against. Any of the five missing makes the other four uninterpretable — 4.1 established
  this and this chapter inherits it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: FR-ANL-05's question is answered by the analytical store and published beside
  4.1's 585.9 ms, with the rows each scanned stated.
- **SC-002**: The rollup, **queried with `sum()` and `GROUP BY`**, returns the same daily figures
  as the raw table for the same ninety days — one figure per day, and any disagreement in the
  distinct-user column published as a number. **Not "row for row"**: the rollup holds one row per
  insert per key until a background merge, so three inserts on one day leave three rows and a
  bare `SELECT messages` reads one of them.
- **SC-003**: The rollup's cost and the raw table's are both published, and the factor between
  them is stated.
- **SC-004**: A query naming one environment reports how many parts it skipped, and that figure
  distinguishes the ordering from the size of the data.
- **SC-005**: The schema applies to an empty store, is a reported no-op on a second run, and
  applies exactly one statement when one is added.
- **SC-006**: Every column in the published schema is either filled by the loaded corpus or named
  as having no producer.
- **SC-007**: At this chapter's tag, `schema_migrations` is unchanged and no analytical query
  runs against Postgres.
- **SC-008**: The chapter's prose stays inside the 2,000–4,000 word bound measured outside code
  fences, and carries at least one `TRAP` box and two figures.

## Assumptions

- **The corpus is 4.1's, loaded by hand.** `scripts/scale/corpus.mjs` builds the Postgres side;
  this chapter reads from it and writes analytical rows directly. **No ingester, no stream, no
  consumer** — the pipe is two chapters away and this schema is what it will be written against.
- **One node.** ADR-08 accepts a single-node ClickHouse in v1 with a cluster-shaped schema, and
  this chapter builds what that ADR describes rather than reopening it.
- **`message_events` first.** SAD §6.2 calls its table "representative"; FR-ANL-01 names four
  event kinds and FR-ANL-07 a request log. This chapter builds the one the predecessor's question
  needs, and names the others as later chapters'.
- **The comparison is against 4.1's recorded numbers, not a re-run.** They are in
  `specs/046-chapter-4-1/baseline.txt` with the corpus and machine they were taken on. Re-running
  4.1's measurement is not this chapter's work; quoting it with its conditions is.
- **The chapter can be written but tagging follows `part4-chN`.** 046 settled the convention and
  deleted the twenty-one stale `part3-chN` tags; this chapter's tag is `part4-ch2`.
- **`check:fences` opens where 4.1 closed it** — 110, APPLY 74, HEAD 36 — and that is re-measured
  rather than carried.

## Out of Scope

- The ingester, the JetStream consumer, and any producer of analytical events.
- The request log (FR-ANL-07), latency percentiles (FR-ANL-10), and the reconciliation job
  (FR-ANL-06).
- Emoji usage events (DR-14) and storage metering (FR-MED-12).
- Any change to the operational schema, to `schema_migrations`, or to the Postgres migration
  runner.
- Re-running chapter 4.1's Postgres measurement.
