# Feature Specification: Chapter 4.1 — the question the counters can't answer

**Feature Branch**: `046-chapter-4-1`
**Created**: 2026-09-12
**Status**: Draft
**Input**: User description: "Chapter 4.1"

Part 4 opens on CON-01, and `docs/07-tutorial-plan.md` specified the opening chapter as
*"run the metering query against Postgres under write load, watch it hurt."*

**There is no metering query.** `services/api/src/quotas/credit.ts` is two pure functions —
`creditFor(reported, credited)` returns `max(0, reported - credited)` and
`highWaterMark(reported, credited)` returns `max(reported, credited)`. No `count(`, `sum(` or
`countDistinct` appears anywhere in the quotas module. Part 3's counters rise on the send path
because a quota must refuse a send synchronously, so there is nothing to put under load and
watch slow down. **The chapter's planned demonstration does not exist to be run.**

**The true premise is a shape mismatch, and it is a better chapter.** The operational question
is *give me the next 50 messages in this channel after cursor X*, and Part 2 shaped the table
for it. The analytical question (FR-ANL-05, FR-ANL-09) is *messages and unique active users
per environment per day, over 90 days* — and asking it costs a join and a scan, because
`messages` carries no `environment_id` and nothing indexes `created_at`. SAD §6.2's ClickHouse
table is `ORDER BY (environment_id, ts)`: the two columns the Postgres table orders by neither
of.

**The reader watched the minimisation happen.** `schema.ts` carries the comment *"No dedicated
(channel_id, sequence DESC) index: DR-01's unique constraint above already supplies that
ordering… Chapter 2.4 measured it and migration 0001 dropped the redundant twin."* An index was
measured and removed on camera, for the operational question. This chapter is where the bill
for that arrives, and the bill is correct — the removal was right.

**And the method already has a precedent the reader has seen.** The chapter on what a user sees
— published 3.16, renumbered by the rework, which is why it is named here and not counted — built
a scratch database of 2,000 channels and 1,000,000 messages and recorded 159 ms of sequential scan
against the test lane's 0.87 ms for the same query. Its lesson is this chapter's own warning,
already taught: *the lane answered 0.87 ms and would have settled the question the wrong way.*
What it did not leave behind is a seeder — `specs/034-chapter-3-15/baseline.txt:153` says
plainly that *"the scratch database is not this lane and is not seeded by anything in the
repository."* `scripts/scale/seed.mjs` seeds users and channels for NFR-SCL-01 and writes no
messages. **The instrument has to be built, and this is the chapter that introduces it**, because
a file created by chapterless work has nowhere to be introduced (045-73).

**This chapter ships almost no product code, and that is deliberate.** It adds an instrument
and four numbers. Everything it proves is proved against the platform as Part 3 left it.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The reader asks the analytical question and watches the neighbour pay (Priority: P1)

A reader who has finished Part 3 holds a platform that meters quotas accurately and cannot
answer a single question the dashboard will ask. They generate a realistic corpus, write the
daily-usage query against Postgres for the first time, and read its plan. Then they send
messages while it runs and watch write latency move.

**Why this priority**: it is the chapter's reason to exist. Without it Part 4 opens by asserting
CON-01 rather than demonstrating it, which is Rule 1 inverted — the machinery before the failure.

**Independent Test**: seed a scratch database to the stated volume, run the query, capture its
plan and duration; then run it again while a send loop reports latency percentiles, and compare
those percentiles against the same loop with the query absent.

**Acceptance Scenarios**:

1. **Given** a scratch database seeded to the stated volume, **When** the daily-usage query for
   one environment over 90 days is run, **Then** its plan and its duration are recorded, and the
   plan names the scan and the join rather than an index seek.
2. **Given** a send loop reporting write latency, **When** the analytical query runs beside it,
   **Then** the loop's p95 is recorded both with the query running and without it, and both
   numbers are stated against NFR-PRF-02's published 150 ms.
3. **Given** the same query run against the test lane instead of the scratch database, **When**
   its duration is recorded, **Then** the chapter states both numbers and says which one would
   have decided the question wrongly.
4. **Given** the measurements are complete, **When** the chapter reports them, **Then** the row
   counts of the database they were taken against are reported beside them.

---

### User Story 2 - The reader tries the obvious fix and finds it costs more (Priority: P2)

The reader's first instinct is to add an index. They add the column the query needs and the
index that would serve it, re-run both measurements, and find the analytical question fast and
the write path slower — a cost every send now pays for a question no send asks.

**Why this priority**: it closes the objection the chapter would otherwise leave open. A slow
query is an argument for an index; a slow query whose fix taxes the write path is an argument
for a second store. Without this story the chapter can be answered in one sentence by any
reader who has used Postgres.

**Independent Test**: on a throwaway copy of the seeded database, add the denormalised column
and the index, re-run the query and the send loop, and compare all four numbers against Story 1's.

**Acceptance Scenarios**:

1. **Given** the seeded corpus copied to a throwaway database, **When** `environment_id` is
   denormalised onto messages and `(environment_id, created_at)` is indexed, **Then** the
   analytical query's duration and plan are recorded again.
2. **Given** that same database, **When** the send loop runs against it, **Then** its write
   latency is recorded and compared with Story 1's.
3. **Given** the index exists, **When** the storage cost of the column and index is measured,
   **Then** it is reported as a figure rather than described.
4. **Given** the measurements are complete, **When** the chapter's repository state is inspected,
   **Then** it contains no migration, no column and no index from this experiment, and the
   chapter fences none.

---

### User Story 3 - The instrument survives the chapter that built it (Priority: P3)

The reconciliation chapter will need a volume at which 0.1% is a real threshold. This story does
not deliver that chapter's reuse — it delivers the thing reuse requires: a seeder in the
repository, with a published interface, that produces what it says it produces.

**Why this priority**: an instrument built for one measurement and abandoned is what the
predecessor did — `specs/034-chapter-3-15/baseline.txt:153` records that its million-row corpus
"is not seeded by anything in the repository". The value is realised later, so it ranks below the
two stories that realise value here.

**Independent Test**: run the seeder with different volume parameters against an empty database
and confirm the resulting row counts match what was asked for; confirm the database it made
carries the platform's schema; and send one message with what it emitted.

**Acceptance Scenarios**:

1. **Given** an empty database, **When** the seeder is run with a stated message count, channel
   count and environment count, **Then** the resulting row counts match the request.
2. **Given** the seeder has run, **When** its output is read, **Then** it reports what it
   created, so a measurement can record its corpus without querying for it.
3. **Given** the seeder is run twice, **When** the second run completes, **Then** it has either
   added to the corpus or refused, and which of the two is documented rather than discovered.
4. **Given** the seeder is pointed at a database that does not exist, **When** it finishes,
   **Then** that database holds the platform's own schema, applied by the repository's migration
   runner, and the seeder has written no DDL of its own (FR-003b).
5. **Given** a corpus the seeder built, **When** a client authenticates with the emitted
   credential and sends a message as the emitted bot to the emitted channel, **Then** the send
   succeeds (FR-003c). **This scenario exists because the first attempt did not.** A send as a
   `kind = 'person'` user is refused `403 sender_not_permitted`, and a corpus of people alone is
   one no measurement can write to.

---

### Edge Cases

- **The query does not hurt at the volume the machine can reach.** The chapter reports the
  volume reached and states what the measurement does not prove, rather than raising the volume
  until the number is persuasive. NFR-SCL-01 was discharged this way.
- **The machine cannot hold the corpus.** The seeder's volume is a parameter and the reported
  corpus is whatever was actually created.
- **Something else runs on the machine during the measurement.** A battery run beside a few
  hundred `git show` calls cost one run 768 seconds while its per-suite times stayed identical;
  interference is distinguishable from a defect only if the condition is recorded.
- **The premise is false at this chapter's tag.** If an index on `created_at` or an
  `environment_id` column has arrived since grooming, the chapter's argument changes and the
  finding is that, not an inconvenience.
- **The probe leaves state behind.** A red probe writes to the lane: 043 left two
  `javascript:alert(1)` rows and the next measurement read them as pre-existing data
  contradicting the plan.
- **The send loop is rate-limited or quota-capped.** Part 3 built both. A loop that measures
  refusals instead of writes is measuring the wrong thing.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The chapter MUST demonstrate CON-01 by measurement rather than assert it.
- **FR-002**: The demonstration MUST use the platform as Part 3 left it. No schema change, no
  new column and no new index is published by this chapter.
- **FR-003**: A seeder MUST exist in the repository that generates messages, channels, users,
  environments and **a credential the measurement can authenticate with** to a requested volume,
  and MUST be introduced by this chapter rather than arriving without one.
- **FR-003a**: The seeder MUST report the corpus it created, so a measurement records its own
  instrument rather than a number somebody remembered.
- **FR-003b**: The seeder MUST create the corpus database **and migrate it with the repository's
  own migration runner**. It MUST hand-write no DDL: a measurement is a measurement of this
  platform only if the corpus carries the schema this platform ships.
- **FR-003c**: The corpus MUST include **a bot user that the send loop sends as**, a channel it is
  a member of, and both MUST be named in the seeder's output. An application credential may send
  only as a bot (FR-MSG-13, narrowed by the bot chapter), so a corpus of people alone is a corpus
  no measurement can write to.
- **FR-004**: The analytical query MUST be the one FR-ANL-05 and FR-ANL-09 ask for — messages and
  unique active users, per environment, per day — and MUST be written as somebody would write it
  against this schema, not as a straw man.
- **FR-005**: The query's execution plan MUST be published alongside its duration. A duration
  without a plan says a query was slow; the plan says why.
- **FR-006**: Write latency MUST be measured beside the analytical query and without it, and both
  MUST be stated against NFR-PRF-02's published p95 of 150 ms.
- **FR-007**: The counterfactual — denormalised column plus `(environment_id, created_at)` index
  — MUST be measured on a throwaway database, never on the test lane and never at this chapter's
  tag.
- **FR-007a**: The counterfactual MUST report the analytical query's improvement **and** the write
  path's cost **and** the storage cost. Reporting only the first makes the reader's own argument
  for them.
- **FR-008**: Every duration published MUST carry the row counts of the database it was taken
  against, because those counts are part of the instrument.
- **FR-009**: The chapter MUST state the test lane's answer to the same query beside the scratch
  database's, and MUST say which would have decided the question wrongly.
- **FR-010**: If the measurement does not show a cost the reader would act on, the chapter MUST
  publish the volume reached and what it does not prove, and MUST fall back to the arithmetic
  argument — an analytical event per API request rather than per message, and 90-day retention as
  a declared TTL against a partition-and-delete job.
- **FR-011**: The chapter MUST NOT re-teach the fire-and-forget emission path. The chapter on when
  to stop trying shipped
  `analytics.{domain}.{action}.{environment_id}`, argued the tradeoff, and recorded that *"every
  attempt is APPROXIMATE"*. This chapter may cite it and must not derive it again.
- **FR-012**: The chapter MUST NOT teach ClickHouse. The second store arrives in the chapter after
  the next one, and a chapter that introduces the answer alongside the problem has no failure to
  show first.
- **FR-013**: The repository state at this chapter's tag MUST contain no artefact of the
  counterfactual — no migration file, no column, no index, and no row written by the probe.
- **FR-014**: The index facts this chapter's argument rests on MUST be re-derived from
  `services/api/src/db/schema.ts` at this chapter's tag rather than carried from
  `docs/12-part-4-structure.md`, and the count of indexes MUST be stated from that derivation.
- **FR-015**: Every gate MUST be green at close-out, with one stated exception: `check:fences`
  opens Part 4 at 109 problems (APPLY 74, HEAD 35) and this chapter's contribution to that number
  MUST be reported separately from the inherited backlog.

### Key Entities

- **The seeded corpus**: environments, channels, users and messages at a requested volume, with
  the counts it actually produced. It is the instrument, and it is reported with every number
  taken against it.
- **A measurement**: a duration, the plan that produced it, the corpus it ran against, and the
  condition of the machine while it ran. Any of the four missing makes the other three
  uninterpretable.
- **The counterfactual database**: a throwaway copy carrying the denormalised column and the
  index, existing only for the duration of the experiment and named in no migration.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader can run the seeder and reproduce the chapter's corpus, and the row counts
  they get match the ones the chapter publishes.
- **SC-002**: The analytical query's cost is published as a duration, a plan and a corpus size,
  for both the scratch database and the test lane, and the two differ by a factor the chapter
  states.
- **SC-003**: Write latency beside the analytical query and without it are both published, both
  compared to 150 ms, and the difference between them is stated as a number rather than as a
  direction.
- **SC-004**: The counterfactual publishes four figures — query duration, query plan, write
  latency, storage cost — and at least one of them is worse than before the index existed.
- **SC-005**: After the chapter's work is complete, the repository at its tag contains no
  migration, column or index introduced by the counterfactual, and **every database any task
  created is gone** — the seeded corpus, the throwaway copy, and the ones the three-volume run and
  the falsification each make.
- **SC-006**: The seeder's interface is published as a contract, it is imported by no service and
  run by no lane, and it produces the requested corpus at three different volumes. **The claim that
  a later chapter reuses it unmodified is not verifiable here** — it is a property of movement IV,
  recorded in this feature's `gaps.md` for the chapter that can settle it.
- **SC-007**: One person who has not read this specification, given the published chapter and
  nothing else, answers three questions from it in their own words: which question Postgres
  answered slowly, what the index fixed and what it cost, and what the chapter did not do. The
  procedure is `specs/036-chapter-3-18/reader-protocol.md`; unanswered questions are recorded
  verbatim whether or not they are acted on.
- **SC-008**: The chapter's prose stays inside the 2,000–4,000 word bound measured outside code
  fences, and carries at least one `TRAP` box and two figures.

## Assumptions

- **The chapter builds an instrument and takes measurements; it ships no feature.** This is the
  first chapter in the series with that shape, and it is what Rule 1 requires when the machinery
  being justified is an entire second datastore.
- **The scratch-database method is precedent rather than invention.** The chapter on what a user
  sees used it and published 159 ms against 1,000,000 rows. What is new is that the seeder lands in the repository
  instead of being discarded.
- **The measurement environment is the compose stack with real processes, not the vitest lane.**
  `docs/11-scalability-measurement-2026-09-06.md` is the model, including bringing the stack up on
  `RELAY_POSTGRES_PORT=15432` because this machine's own Postgres holds 5432.
- **Nothing else runs on the machine during a measurement, and nothing touches the repository.**
- **The corpus target is 1,000,000 messages or more INSIDE BOTH OF THE QUERY'S PREDICATES** — the
  measured environment, and the 90-day window — which is what the seeder's variables now mean and
  what `subject.messages_in_window` reports. Stated as a database total it was wrong by a factor of
  three, and as an environment total by a further quarter. That chapter's figure is the floor because it is
  the number this project has already published for a comparable query; 045's close-out counted
  300,719 messages in the lane, which is not enough.
- **Part 4's numbering is global and its first tag convention is unsettled.** `part3-chN` and
  `rework/part3-chN` both exist and point at different commits; this chapter cannot be tagged
  until that is resolved, and resolving it is not this chapter's work.
- **`docs/12-part-4-structure.md` is the structure record and is newer than
  `docs/07-tutorial-plan.md` where they disagree.** Both were amended during grooming; the plan's
  Part 4 section now points at 12.
- **FR-ANL-08's p95 under 2 seconds over 90 days is not verified here.** It is the target the
  second store must meet, and this chapter measures only what the first store does.

## Out of Scope

- ClickHouse: its schema, its client, its migrations, and the ingester.
- The analytics emission path for API requests and connection events — movement III's.
- Any change to `messages`, `channels`, or the quota tables.
- FR-ANL-06's reconciliation, which needs a second store to reconcile against.
- The fence-chain backlog of 109 problems inherited from Part 3's close-out, beyond reporting this
  chapter's own contribution separately.
