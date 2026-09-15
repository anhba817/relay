# Feature Specification: chapter 4.6, "metering you can bill on"

**Feature Branch**: `051-chapter-4-6`
**Created**: 2026-09-15
**Status**: Draft
**Input**: User description: "chapter 4.6"

## 1. Which chapter this is, and why the number had to be derived

**Movement IV, first chapter — `docs/12` §3's table row 7, *"Metering you can bill on"*.**
The number was derived rather than read: §3's table keeps **pre-contraction ordinals** in
its first column on purpose, so the shipped chapters run 4.1=row 1, 4.2=row 2, 4.3=row 4,
4.4=row 5, 4.5=row 6. §3's movement map uses **current** ordinals (`IV ch 6–9`), and the two
columns disagree by design. Naming a Part 4 chapter by its number without checking both is
how this project has already gone wrong twice.

Its one-line brief: *"Daily rollup materialised views (DR-10) — billing never scans raw
events."*

## 2. The brief is already half-built, and the half that exists is not the half that bills

**`analytics/0001_daily_usage.sql` shipped with chapter 4.2.** A `SummingMergeTree`
materialised view over `message_events`, `ORDER BY (environment_id, day)`, carrying
`messages` and `active_users_state`. So "build the daily rollup" is not this chapter's
subject — the rollup exists, was measured at 13.22 ms against the raw table's 585.9 ms, and
turns 1,000,000 raw rows into 89.

**Three facts about it decide what this chapter is instead**, each established by reading
the tree rather than the structure document:

**(1) Nothing reads it.** `grep daily_usage` across every `.ts` and `.mjs` in
`relay-platform` returns one standalone script (`analytics/query.mjs`) and one comment in
the corpus loader. That script opens *"FR-ANL-05's daily question, asked of the analytical
store"* — and it is referenced by no `package.json` script, no service and no config, so
**the only thing that has ever asked FR-ANL-05's question of this store is a file nothing
runs.** What bills today is
Postgres: `usage_periods (environment_id, period, messages_sent)` from migration 0013, plus
0014's connection-minute buckets, both maintained synchronously on the write path.

**(2) It carries two of FR-ANL-05's four quantities.** The clause, verbatim: *"The system
shall meter, per tenant per day: **messages sent, unique active users, connection-minutes,
and stored message count.**"* The view has messages and unique active users.
**Connection-minutes and stored message count are absent**, and the analytical store only
acquired the raw material for the third of them last chapter.

**(3) It carries two of FR-ANL-09's four dimensions.** *"Usage shall be attributable by
**application, environment, channel, and day**."* The view's sorting key is
`(environment_id, day)`. There is no application and no channel, and `message_events`
carries `channel_id` while nothing groups by it.

**So the chapter is not "build a rollup". It is "the rollup that exists answers two of four
questions in two of four dimensions, and nothing bills on it."**

## 3. What this chapter does not decide, and where each of those lives

- **The reconciliation job is 4.7** (`docs/12` §3 row 8, *"The job that checks the meter"*),
  and the milestone where the meter agrees is 4.9 (row 10). **047-1 and 048-1 — DR-10 and
  FR-ANL-06 cannot both hold** — are filed *for movement IV* and belong to those chapters,
  not this one. This chapter must not pretend to settle them.
- **The customer-facing query surface is 4.8** (row 9, FR-ANL-07 and FR-ANL-10).
- **Enforcement stays in Postgres.** `docs/12` §4 already argues it: *"a quota must refuse a
  send synchronously, so its counter cannot live downstream of a lossy stream"*, therefore
  *"Two counters of one quantity is the right answer and the reconciler is the price."* §4 is
  the section headed **"Chapters must not re-teach these"**. This chapter cites it; it does
  not re-derive it, and it does not move the quota counter.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The four quantities FR-ANL-05 names are all in the rollup (Priority: P1)

An operator asks the analytical store for one tenant's usage for one day and gets all four
metered quantities — messages sent, unique active users, connection-minutes and stored
message count — from rollup rows, without reading a raw event table.

**Why this priority**: it is the clause the chapter is named for, and two of the four have
never existed anywhere but Postgres.

**Independent test**: load a known corpus, read the rollup for a chosen
`(environment_id, day)`, and compare each of the four against the same quantity computed
from the raw tables over the same window.

**Acceptance scenarios**:

1. **Given** a day with a known number of messages sent, **When** the rollup is read for that
   environment and day, **Then** `messages` equals the count of `event = 'created'` rows in
   `message_events` for that environment and day.
2. **Given** connection open and close records for that environment and day, **When** the
   rollup is read, **Then** connection-minutes are present and derived from those records
   rather than from the Postgres meter.
3. **Given** messages created and deleted across several days, **When** the rollup is read
   for a given day, **Then** stored message count reflects creations minus deletions up to
   and including that day, not that day's creations alone.
4. **Given** a tenant with no activity on a day, **When** the rollup is read for that day,
   **Then** the absence is distinguishable from a zero — a missing row and a row of zeros
   must not be the same answer.

---

### User Story 2 - A rollup read is a rollup read, not a raw scan in disguise (Priority: P1)

DR-10's clause is *"so billing never scans raw events"*. A reader must be able to show that
the metering read touched rollup rows and not the raw tables.

**Why this priority**: DR-10 is the clause the brief cites, and it is a claim about what a
query READS, which is measurable and currently unmeasured.

**Independent test**: run the metering read and report rows read against the raw tables'
row counts, the way 4.2 published 315 rows read against 1,052,655.

**Acceptance scenarios**:

1. **Given** a raw corpus large enough for the difference to be visible, **When** the
   metering read runs, **Then** the rows it reads are reported and are a small fraction of
   the raw event count.
2. **Given** the same query, **When** its cost is compared against the same question asked of
   the raw tables, **Then** both numbers are published together with the corpus size beside
   them.

---

### User Story 3 - The rollup answers by application and by channel, or says it cannot (Priority: P2)

FR-ANL-09 names four attribution dimensions and the shipped view supports two.

**Why this priority**: it is a published clause the chapter makes visibly incomplete, and
the cost of adding a dimension to a rollup is the chapter's own subject matter.

**Independent test**: ask for one application's usage across its environments, and one
channel's usage within an environment; record which of the four dimensions the store can
answer and what each costs.

**Acceptance scenarios**:

1. **Given** an application holding two environments, **When** usage is asked for by
   application, **Then** it is answerable from rollup rows, or the reason it is not is
   recorded with the cost of making it so.
2. **Given** a channel with known message activity, **When** usage is asked for by channel,
   **Then** the same holds.

---

### User Story 4 - The two connection-minute counters are reconciled, and SRS open question 4 is answered (Priority: P2)

Chapter 4.5 measured two counters of one name that measure different quantities: the meter
charges every calendar minute a connection was open for any part of (**2** for a two-second
connection crossing a boundary) and a connection record gives elapsed duration (**0.03**).
**SRS Appendix C open question 4 asks exactly this** — *"Does connection-minute metering need
per-second precision, or is per-minute rounding acceptable?"*, against FR-ANL-05, owner
*Product / Billing* — and it is still open.

**Why this priority**: the chapter that puts connection-minutes in the billing rollup is the
chapter that must say which of the two quantities a customer is charged for. It cannot put a
number in a billing table and leave the definition open.

**Independent test**: compute connection-minutes both ways over one window and publish both,
then record the decision and amend the SRS.

**Acceptance scenarios**:

1. **Given** connections that cross minute boundaries, **When** minutes are computed by
   calendar bucket and by elapsed duration, **Then** both totals are published with the gap
   stated.
2. **Given** that comparison, **When** the chapter chooses which one bills, **Then** the SRS
   records the answer and Appendix C's question 4 is closed rather than carried.

---

### Edge Cases

- **A day at the TTL boundary.** `message_events` expires at 90 days and `daily_usage` does
  not (FR-003a). 047 measured the oldest day in a window disagreeing by 4,941 — 0.49% — for
  the structural reason that a TTL cuts at a timestamp and a daily rollup's finest grain is a
  day. A rollup read must not be compared against a raw read without a window on both sides.
- **A rollup row per insert.** `SummingMergeTree` holds one physical row per
  `(environment_id, day)` per insert until a background merge; 047 measured `SELECT messages`
  returning `1000 1000 1000` where the truth was 3000. The read contract is `sum()` with
  `GROUP BY`, and a query whose correctness depends on somebody having run `OPTIMIZE` is
  right in a demo and wrong in production.
- **`uniq` is approximate.** Exact to roughly 60,000-65,000 distinct and off by 0.51% at
  70,000. Any distinct-user figure published here states the corpus cardinality beside it.
- **Stored message count is a stock, not a flow.** Every other metered quantity is a daily
  count; this one is a running balance. DR-17 states the technique for its media analogue —
  *"summing `media_events` deltas (uploaded/deleted)"* — and a rollup that counts today's
  creations is answering a different question.
- **Deletions are events, not absences.** `message_events.event` is `created|edited|deleted`,
  so a deletion is a row rather than a missing row. A stored count built by counting rows
  that still exist would be reconstructing from state, which is the failure FR-ANL-02's
  emit-at-the-time rule exists to prevent.
- **Connection-minutes may span days.** A connection opening at 23:59 and closing at 00:02
  belongs to two days. Whichever definition bills, the day boundary must be decided rather
  than inherited from whichever timestamp happened to be indexed.

## Requirements *(mandatory)*

### Functional Requirements

**The rollup**

- **FR-001**: The analytical store shall carry, per tenant per day, all four quantities
  FR-ANL-05 names: messages sent, unique active users, connection-minutes, and stored message
  count.
- **FR-002**: Connection-minutes shall be derived from the connection records chapter 4.5
  publishes, not from the Postgres meter, and the chapter shall say which of the two
  definitions of a connection-minute it uses.
- **FR-003**: Stored message count shall be maintained as a running balance from creation and
  deletion events rather than as a count of surviving rows, and the chapter shall cite DR-17
  as the published statement of that technique rather than deriving it.
- **FR-004**: A day on which a tenant had no activity shall be distinguishable from a day
  whose figures are zero.
- **FR-005**: Every rollup read published in this chapter shall use `sum()` with `GROUP BY`
  and shall not depend on a merge having run. A read that is correct only after `OPTIMIZE`
  shall be shown failing before it is shown passing.

**What billing reads**

- **FR-006**: A metering read shall be defined that answers FR-ANL-05's four quantities for a
  tenant and a period from rollup rows alone, and the rows it reads shall be reported.
- **FR-007**: The chapter shall state plainly that the Postgres quota counter is unchanged
  and why, citing `docs/12` §4 rather than re-deriving the argument: a quota refuses a send
  synchronously and its counter cannot live downstream of a lossy stream.
- **FR-008**: The chapter shall record that DR-10's clause was previously satisfiable by a
  view nothing read, and that a rollup with no reader discharges a clause about what billing
  scans only in form.

**Attribution**

- **FR-009**: The chapter shall measure which of FR-ANL-09's four dimensions — application,
  environment, channel, day — the rollup can answer, and record the cost of each it adds.
- **FR-010**: Any dimension FR-ANL-09 names that this chapter does not add shall be recorded
  as an open item naming what closing it would cost, not left implied by its absence.

**The open question this chapter closes**

- **FR-011**: SRS Appendix C open question 4 shall be answered and the SRS amended, or the
  reason it cannot be answered here shall be recorded. Carrying it forward unremarked is not
  an outcome.
- **FR-012**: Both connection-minute quantities shall be published side by side for one
  window with the gap stated, so the decision in FR-011 rests on a number.

**Documents this chapter makes wrong or incomplete**

- **FR-013**: Where a measurement here falsifies a published document, that document shall be
  amended rather than left to diverge.
- **FR-014**: Where this chapter makes a published document **incomplete** rather than wrong,
  the same applies. `docs/05-sad.md` §6.2 declares the analytical schema and has gained a
  table per chapter since revision 1.3; a second materialised view is the same series' next
  entry.
- **FR-015**: `docs/12` §3's row for this chapter shall be amended where this chapter
  falsifies its one-line description — which it does, because the brief says *"daily rollup
  materialised views (DR-10)"* and one has existed since 4.2.
- **FR-016**: **`docs/12` §7.1 shall be closed.** §3's 2026-09-13 amendment records chapter
  4.2 building all four items of its brief and the chapter it belonged to is gone, while §7.1
  still reads as open. This is the defect chapter 4.5 found at §7.2 and fixed one entry over;
  it survived the chapter that learned the lesson. §7 is *"open questions, each owned by the
  chapter that needs it"* and no entry owns this chapter, so the housekeeping falls here.

**The chapter itself**

- **FR-017**: The chapter shall not re-derive 4.2's `SummingMergeTree` mechanics, 4.2's
  `uniq` approximation finding, or Part 3's quota counters. It cites them.
- **FR-018**: Prose shall stay inside the 2,000–4,000 word bound measured outside code
  fences, with at least one `<Trap>` box (`docs/07` §line 70), and both counted.
- **FR-019**: `pnpm check:fences` shall be reported as a delta against an opening measured in
  this feature, broken down by kind and locale — and, following 050-4, **separating the
  `differs at line` class from the `does not exist` class**, because 11 of the inherited 36
  are fences whose title names no file and can never be repaired by editing the platform.
- **FR-020**: All eleven gates shall run. Where one is red for an inherited reason, the
  diagnosis shall name the cause rather than the count.

### Key Entities

- **Daily usage rollup** — one row per tenant per day carrying the four metered quantities.
  Today's `daily_usage` is the first two over `message_events`.
- **Connection record** — chapter 4.5's `connection_events`: an open row and a close row per
  connection, the close carrying a duration. The raw material for connection-minutes.
- **Stored message balance** — creations minus deletions, cumulative, distinct in shape from
  every other quantity here.
- **Postgres usage period** — `usage_periods (environment_id, period, messages_sent)`, the
  counter that enforces quotas synchronously. Unchanged by this chapter and named so that
  nobody reads the new rollup as its replacement.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All four of FR-ANL-05's quantities are readable from the rollup for a chosen
  tenant and day, and each is compared against the same quantity computed from raw data over
  the same window, with the difference published.
- **SC-002**: The metering read's rows-read figure is published beside the raw tables' row
  count, with the corpus size stated.
- **SC-003**: The two connection-minute definitions are published side by side for one window
  with the gap stated as a number.
- **SC-004**: SRS Appendix C open question 4 is closed, or the reason it cannot be is
  recorded.
- **SC-005**: A rollup read that depends on a merge having run is shown failing, then shown
  passing under the `sum()` and `GROUP BY` contract.
- **SC-006**: A day with no activity and a day with zero figures are distinguishable, shown by
  a test.
- **SC-007**: Which of FR-ANL-09's four dimensions the rollup answers is measured and
  recorded; anything not added is an open item with its cost named.
- **SC-008**: The Postgres quota counter is shown unchanged, by diff.
- **SC-009**: `docs/12` §3's row for this chapter and §7.1 are both amended.
- **SC-010**: `check:fences` reported as a delta against an opening measured in this feature,
  by kind and locale, with the two HEAD classes separated.
- **SC-011**: Prose measured outside code fences against the 2,000–4,000 bound, with the
  `<Trap>` count beside it.

## Assumptions

- **This chapter builds the rollup billing reads; it does not build the reconciliation.**
  `docs/12` §3 gives 4.7 *"The job that checks the meter"* and 4.9 the milestone. 047-1 and
  048-1 are filed for movement IV and are those chapters', which is why FR-001 asks for the
  quantities and not for the 0.1% agreement.
- **Enforcement stays in Postgres**, on `docs/12` §4's published argument. This is an
  assumption in form only: §4 is the section chapters must not re-teach, and it settles the
  question in as many words.
- **The existing `daily_usage` view is extended or joined rather than replaced.** Replacing a
  materialised view means deciding what happens to the rows it already holds, and 047
  measured the hazard in the quiet direction: `DROP TABLE` on a view's source succeeds
  silently and leaves an orphan answering queries with zeros. The plan phase decides the
  shape; this spec assumes the existing rows survive.
- **Connection-minutes are derivable from 4.5's records for connections with both an open and
  a close.** 4.5 measured that neither a clean stop nor a kill produces close records, so a
  window containing a deploy has opens with no closes. The metering read is expected to need
  the same scoping FR-009a gave the reconciliation.
- **The stored-message-count arm has no producer yet in the sense that matters.**
  `message_events` carries `created|edited|deleted`, so the deltas exist; what does not exist
  is anything that accumulates them.
- **Part 4 is 22 chapters and this is the 6th**, movement IV of seven, with the milestone at
  the 9th. Movement IV is four chapters: this one, the reconciler, the customer-facing log,
  and the milestone.

## Dependencies

- Chapter 4.2's `daily_usage` view and the `analytics/` migration runner and ledger.
- Chapter 4.5's `connection_events` table, which is the only source of connection data in the
  analytical store.
- The composed stack with ClickHouse reachable from outside its container (4.2's finding), and
  `RELAY_POSTGRES_PORT=15432`.
- **An ingester process for any integration test that waits on a row.** 050-8 measured 4.4's
  suite passing 5 of 5 with one running and failing 5 of 5 without, and there is no ingester
  service in `compose.yaml`.
