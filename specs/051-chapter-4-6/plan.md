# Implementation Plan: chapter 4.6, "metering you can bill on"

**Branch**: `051-chapter-4-6` · **Date**: 2026-09-15 · **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/051-chapter-4-6/spec.md`

**Read [research.md](./research.md) first.** Eight of its ten items were run against the
running store and three changed the design — including one that changed what the chapter is.

## Summary

Movement IV's first chapter. `docs/12` §3's brief is *"Daily rollup materialised views
(DR-10) — billing never scans raw events"*, and a daily rollup materialised view has existed
since chapter 4.2.

What the research found instead, in one line: **the rollup reads the only table in the
analytical store that nothing writes.**

    api_requests       11,683      producer since 4.4
    connection_events     154      producer since 4.5
    webhook_attempts       64      producer since 4.3
    message_events          0      no producer — a batch loader and nothing else
    daily_usage             0      the rollup, over message_events

So the chapter builds the rollup DR-10 asks for over the sources that **have** producers,
decides the connection-minute definition that SRS Appendix C question 4 has left open since
before Part 4 began, and states plainly that three of FR-ANL-05's four quantities rest on a
table with no producer. It does not build that producer: that is a send-path change on the
busiest path in the platform, and by §3's table it is not this chapter.

## Technical Context

**Language/Version**: TypeScript 5.x on Node 22, and ClickHouse SQL 25.3
**Primary Dependencies**: none added. The rollup is DDL and the read is a query.
**Storage**: ClickHouse `relay_analytics` (rollups), Postgres (the quota counter, untouched)
**Testing**: `vitest` — unit for any read helper, `.itest.ts` for anything touching the store
**Target Platform**: the composed stack, ClickHouse reachable on 8123, `RELAY_POSTGRES_PORT=15432`
**Project Type**: monorepo — `relay-platform` code, `relay-tutorial` prose and gates
**Performance Goals**: a metering read whose rows-read figure is a small fraction of the raw
event count, published with the corpus size beside it (4.2 published 315 against 1,052,655)
**Constraints**: the `analytics/` ledger keys on filename with a checksum and refuses a
changed one, so every schema change is a **new numbered statement** — `0001` cannot be edited
**Scale/Scope**: one new rollup table, two views, one read, one SRS amendment, two `docs/12`
amendments, one chapter

**THE FILE NUMBERS ABOVE FOLLOW THE PHASES, AND `tasks.md` IS AUTHORITATIVE.** A first draft
of this tree had `0007` as the message view and `0008` as the connection one — the reverse of
the order the phases build them. **The ledger keys on filename**, so a tree and a task list
that disagree produce a `schema_applied` row nobody can match to a file.

**AND THE READ IS `services/ingester/src/metering.ts`, NOT A SCRIPT.** A first draft left it
as *"`analytics/metering.mjs`, or a module if phase 5 needs it testable"* — an either/or
sitting exactly where constitution VI's coverage clause gets decided. Three things settle it:

- **A script under `analytics/` can carry no pin.** The coverage include is
  `packages/*/src/**/*.ts` and `services/*/src/**/*.ts`; `analytics/` is in neither, so a
  `.mjs` there is unreachable by the one lane that enforces the ratchet.
- **An unwired script is the defect this chapter is about.** `analytics/query.mjs` opens
  *"FR-ANL-05's daily question, asked of the analytical store"* and is referenced by nothing.
  Shipping a second one would repeat, in the same directory, the thing the chapter spends its
  argument on.
- **It has a caller from day one, and the caller is the test.** `metering.itest.ts` reading
  the rollup is what makes the read verified rather than demonstrated, and 4.8 wires it to a
  route when the query surface needs one.

It sits beside `services/ingester/src/clickhouse.ts` — **and the one-client property has to be
built, not claimed.** A first draft of this note said that file *"already owns the store's
client"*; measured, `ClickHouse` exposes `insert`, `insertRequests`, `insertConnections`,
`count`, `countRequests` and `countConnections`, and its `post()` helper is a private closure.
**It is an insert-and-count interface**, so a read placed beside it opens a second client
unless the interface gains a query method. It gains one: the interface has grown a method per
chapter since 4.3 and a fourth fits the shape it already has. Then the claim is a property of
the code rather than a sentence about it.

**No NEEDS CLARIFICATION remain.** The three the spec could have carried were settled by
running them: R1 (can one rollup be fed from several sources), R3 (are both connection-minute
definitions computable), R7 (what does extending 4.2's view cost).

## Constitution Check

**This section does not say PASS.** Chapter 4.5's plan wrote *"PASS, with one open case"* and
the open case turned out not to exist; the failure mode worth avoiding is a check that waves.

### III. Two Data Paths, Never Crossed — **A CONFLICT THIS CHAPTER CANNOT RESOLVE, AND MUST NAME**

The clause, verbatim:

> Analytical queries MUST NEVER execute against the operational database (PostgreSQL);
> **billing, metering, and dashboard analytics read only from the analytical store
> (ClickHouse)**, fed via a durable queue (SRS CON-01).

Two facts against it, both measured:

1. **Metering today reads only from Postgres.** `usage_periods (environment_id, period,
   messages_sent)` is a meter, in the operational database, maintained synchronously on the
   send path. Nothing reads the analytical store for metering — the only file that ever asked
   FR-ANL-05's question of it is `analytics/query.mjs`, referenced by no script, service or
   config.
2. **The only path message data has into the store is the one the clause forbids
   outright.** Its one writer is `scripts/scale/load-analytics.mjs:53`, which is
   `postgresql('${PG_HOST}', …)` — **ClickHouse executing a query against Postgres.** The
   clause's first prohibition is *"Analytical queries MUST NEVER execute against the
   operational database (PostgreSQL)"*, and that is this, not merely its `CON-01` queue
   qualifier. A first draft of this section read *"a batch pull, not a queue"* and cited the
   qualifier; the qualifier is the weaker half of the sentence it appears in. **Read the
   clauses, not the identifiers** — including the clause you are the one quoting.

**And this chapter cannot fix it.** After everything below ships, billing still cannot read
messages-sent from ClickHouse, because nothing emits the event. So the chapter makes the
conflict **visible and stated** rather than leaving a clause that reads as satisfied.

`docs/12` §4 already argues the half that is not a defect: *"a quota must refuse a send
synchronously, so its counter cannot live downstream of a lossy stream"*, therefore *"Two
counters of one quantity is the right answer and the reconciler is the price."* That
justifies the Postgres counter existing. **It does not justify the constitution's sentence
saying metering reads only from ClickHouse**, and nobody has reconciled the two. Constitution
VII requires a conflict to be *"resolved explicitly by amendment rather than silent
divergence"* — which makes the missing sentence the defect, exactly as it was for ADR-07 last
chapter. **Phase 6 decides it out loud.**

### III, third bullet — analytical store holds no message text

Satisfied by construction. Every column this chapter adds is a count, a duration or an
identifier. The allow-list — *"only lengths, identifiers, and metadata"* — is the citation;
FR-ANL-11 governs message text and NFR-SEC-06 governs application logs, and neither is the
authority here (050's pass-12 finding, applied rather than repeated).

### III, fourth bullet — 0.1% reconciliation

**Not this chapter's.** `docs/12` §3 row 8 is the reconciliation job and row 10 is the
milestone. 047-1 and 048-1 — DR-10 and FR-ANL-06 cannot both hold, for two independent
reasons — are filed *for movement IV*, and this chapter must hand them forward untouched
rather than appear to settle them by publishing agreeing numbers.

### I. Tenant Isolation — satisfied, and testable

Every rollup row is keyed on `environment_id` and every read is scoped by it. The test is a
second tenant's rows being unreachable from the first tenant's filter, as 4.4 and 4.5 wrote it.

### VI. Requirement-Driven, Test-Verified — satisfied with one measured caveat

70% of business logic and 100% branches on tenant isolation. A rollup is DDL and **a schema
has no branches to cover** — 048 recorded exactly that, and 4.4 and 4.5 met the clause only
because they had a producer with a tenancy branch in it. If this chapter's read path is a
query string and not a function, it has no branches either, and the plan says so in advance
rather than discovering it at the ratchet.

**The quickstart MUST run unmodified.** It carries the gate list and the fenced-file list,
both of which went stale inside a single feature last time.

### VII. Boring by Design — satisfied

No dependency added. One new table, views, a query, and amendments.

## Project Structure

### Documentation (this feature)

```
specs/051-chapter-4-6/
├── spec.md              # 21 FR, 13 SC
├── plan.md              # this file
├── research.md          # R1–R10, eight measured
├── data-model.md        # the rollup's rows and the deltas that make them
├── contracts/
│   └── metering-read.md # what a metering read returns, and what it may not touch
├── quickstart.md        # runnable, and the eleven gates
├── baseline.txt         # the measurement record, written as phases run
└── checklists/
    └── requirements.md
```

### Source Code

```
relay-platform/
├── analytics/
│   ├── 0006_daily_usage_v2.sql        # the rollup table, explicit target
│   ├── 0007_mv_connection_minutes.sql  # connection_events -> rollup  (phase 3)
│   ├── 0008_mv_messages.sql            # message_events -> rollup     (phase 5, no producer)
│   └── (no read here — see services/ingester/src/metering.ts below)
├── services/ingester/src/metering.ts  # the read, and metering.itest.ts its caller
├── services/…                        # otherwise unchanged — no producer, no send-path edit
└── vitest.coverage.config.mts        # pins, if the read is a module

relay-tutorial/
├── app/(en)/part-4/chapter-06/<the chapter's slug>/{page.mdx,figures.ts}
└── lib/tutorial.ts                   # register 4.6 — a step no requirement named until 050
```

## Phases

**MVP is phases 1–4.** A rollup exists with a named target, connection-minutes land in it
from a real producer, and a metering read answers from rollup rows.

### Phase 1 — Premises, measured before anything is built

Every item in `research.md` re-run and recorded in `baseline.txt`, plus the openings this
chapter is measured against:

- The four tables' row counts and the rollup's, as the opening figures.
- `pnpm check:fences` opening **by kind and locale, and with the two HEAD classes split** —
  `differs at line` against `does not exist` — because 050-4 measured 11 of the inherited 36
  to be fences whose title names no file.
- The fenced-file list for every file this chapter will touch, **counted, not remembered**.
  050 measured a list that was wrong in both directions.
- Whether `analytics/*.sql` files carry titled fences, and in which locales. The vi chain
  holds whole bodies for `services/ingester/*` (050-3) and the checker never compares them to
  the tree; this chapter must know which of its files are in that class before it edits them.
- The eleven gates' current colours, so an inherited red is not mistaken for a new one. Four
  api suites were red at 050's close for reasons no chapter caused.

### Phase 2 — The rollup table with a named target, and the view that waits for a producer

`0006` creates the rollup as a `SummingMergeTree` table with an explicit key, and **not** as a
view with an inline engine. R7 measured that 4.2's implicit inner table is what makes the
shipped view unextendable; this one is built the way R1 requires.

**Both views over sources that already exist are built here too**, the message one included —
`0008_mv_messages.sql`, over a table with no producer. It belongs in the foundation rather than
in phase 5 because the corpus proof in phase 4 is the only window in which its three columns
can be checked against raw data, and a corpus flowing through a rollup with no message view
proves nothing. A first draft had the view in phase 5 and the corpus in phase 4, which would
have loaded and removed a corpus that nothing was reading.

Decided here and recorded: what happens to `daily_usage`. The options are leave it beside the
new table, or supersede it. **A bare `DROP` of a source under a live view is the hazard 047
measured succeeding silently**, and the ledger refuses an edit to `0001`, so whichever is
chosen is a new numbered statement.

### Phase 3 — Connection-minutes, from the source that has a producer

`0008`'s view, using R3's `arrayJoin` expansion or `sum(duration_ms)` according to phase 6's
decision. This is the only quantity in FR-ANL-05 that this chapter can populate from live
traffic, which is why it is the MVP's centre rather than messages.

**R5's 44% is asserted here, not discovered later**: a test plants connections with and
without closes and asserts that the minutes figure comes from closes and that the
opens-without-closes count is reported beside it.

### Phase 4 — The metering read 🎯 **MVP**

One read answering FR-ANL-05's quantities for a tenant and a period from rollup rows, with
`sum()` and `GROUP BY` (R10). **The wrong read is shown failing first** — SC-005 — because
047 measured `SELECT messages` returning `1000 1000 1000` where the truth was 3000.

Rows read reported beside the raw tables' counts, and the empty-day distinction (FR-004)
tested: an MV emits no row for a day with no inserts, so "no activity" is always a missing row
and the read is what has to tell it from zero.

**THE CORPUS IS LOADED HERE, MEASURED HERE, AND REMOVED HERE.** The store holds 0
`message_events` and 154 `connection_events`, so a rows-read figure against it is not a
measurement — 4.2's 315-against-1,052,655 exists because that chapter loaded one. Two things
follow, and both are the chapter's material rather than its overhead. **The loader is
`postgresql()`**, so demonstrating the rollup requires executing the prohibition phase 6
amends: the clause is not merely unmet, it is unmeetable, and the demonstration needs the
forbidden path. **And the loader writes into the shared `relay_analytics`**, which every later
suite reads and which 050-2 records as having none of the three guards Postgres has — so the
rows come out again in the same phase, verified in both directions, before anything else is
counted.

### Phase 5 — Attribution

**Channel is in the key from phase 2**, because R6 measured it on the row — so this phase
prices the dimension rather than adding it: the rollup's rows become
`environments x channels x days`, and a tenant-day read sums across a tenant's channels.
Application recorded as an open item with its cost named — it is on no row, the store holds no
`applications` table, and the mapping lives in Postgres, so closing it means arguing
constitution III rather than writing a join.

### Phase 6 — The connection-minute definition, decided and amended

Both quantities published for one window with the gap stated (4.5 measured 2 against 0.03 for
one connection). **SRS Appendix C question 4 is answered and the SRS amended**, or the reason
it cannot be is recorded. It has been open since before Part 4 began, its owner is *Product /
Billing*, and this is the chapter that puts the number in a billing table.

Constitution III's conflict is decided here too, in the same shape 4.5 used for ADR-07: name
the form, choose it out loud, leave the clauses that still hold untouched.

### Phase 7 — The documents

- `docs/05-sad.md` §6.2 gains the rollup — the same series' next entry, the *incomplete rather
  than wrong* class 050 filed as FR-017a.
- `docs/12` §3's row for this chapter, which says to build a view that exists.
- **`docs/12` §7.1, closed.** §3's own amendment records 4.2 building all four items of its
  brief; §7.1 still reads as open. This is the defect 4.5 found at §7.2 and it survived the
  chapter that found it.
- DR-10 and FR-ANL-05 amended where measurement falsifies them.

### Phase 8 — The numbers, and the chapter

Phase 4's figures published rather than re-measured — the corpus is gone by then, and
re-loading would give a second corpus rather than a second reading of the first. Prose and
traps counted, figures from `baseline.txt`, fences generated from the checker's own
replay, eleven gates, `gaps.md` with **every carried item re-measured** — 050's eight and
049's and 048's survivors — `traceability.md`, the SPECKIT block, the tag.

## Dependencies & Execution Order

```
Phase 1  premises                 ── blocks everything
Phase 2  the table + both views   ── blocks 3, 4
Phase 3  connection-minutes       ── blocks 4
Phase 4  the read        🎯MVP    ── blocks 5
Phase 5  attribution              ── independent of 6
Phase 6  the definition + III     ── needs 3's numbers
Phase 7  the documents            ── needs 6
Phase 8  the chapter              ── needs all
```

## Complexity Tracking

| Thing | Why it is not simpler |
|---|---|
| A new rollup table rather than editing `0001` | The ledger keys on filename **and checksum** and refuses a changed one. 4.2 built that refusal and tested it red. |
| Several views into one table | R1 measured it as the only shape where "per tenant per day" is one row. A view reads one source table; there is no single-view alternative. |
| Publishing an unpopulated quantity's row count | FR-001a. A column reading 0 for a tenant that sent messages is worse than an absent column, and the row counts are how a reader tells the two apart. |

## Risks, each with what would catch it

- **The chapter reads as "metering is done".** It is not: three of four quantities have no
  producer. Phase 4's published row counts are the guard.
- **A number from this chapter is read as the reconciliation.** 047-1 and 048-1 are movement
  IV's and not this chapter's; phase 6 states the handover.
- **The fence chain charges for `analytics/*.sql`.** 4.5's first draft went 110 → 116 for six
  files. Phase 1 counts the exposure before phase 2 writes anything.
- **`daily_usage` is superseded carelessly.** 047 measured a `DROP` under a live view
  succeeding with no error and leaving an orphan answering with zeros. Phase 2 decides it in
  the direction that errors.
