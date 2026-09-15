# Feature Specification: chapter 4.7, "the job that checks the meter"

**Feature Branch**: `052-chapter-4-7`
**Created**: 2026-09-15
**Status**: Draft
**Input**: User description: "chapter 4.7"

## 1. Which chapter this is

**Movement IV's second chapter — `docs/12` §3's table row 8, *"The job that checks the
meter"*.** The number is derived, not read: §3's table keeps **pre-contraction ordinals** in
column one while its movement map uses current ones, so the shipped chapters run 4.1=row 1,
4.2=row 2, 4.3=row 4, 4.4=row 5, 4.5=row 6, 4.6=row 7. Naming a Part 4 chapter without
reconciling both columns is how this project has gone wrong twice.

Its brief: *"FR-ANL-06's reconciliation job, built to be callable in isolation (§2.3)."*

The clause, verbatim: **"Metered totals shall agree with counts derived from operational data
to within 0.1%, verified by a daily reconciliation job that raises an alert on breach."**

No §7 open question owns this chapter — 7.3 is ch 14, 7.4 ch 15, 7.5 ch 20, and 7.6 and 7.7
belong to nobody in particular.

## 2. The job's first honest run fails, and three of the four reasons are not the analytical path's fault

**Three obstacles** stand between this clause and a green reconciliation, all measured by
earlier chapters and filed *for this movement*. A fourth item — two operational counters that
disagree — is a question the clause leaves open rather than an obstacle, and its measured
divergence turned out to belong to the test lane; both facts are below, because a first draft
of this spec had it as obstacle four.

**(1) One side has no producer.** Chapter 4.6 measured `message_events` at **0 rows**, with
zero occurrences under `services/`. The operational side holds **9,624** in
`usage_periods.messages_sent`. That is not a 0.1% disagreement; it is **100%**, and no
reconciler can be written that does not report it.

**(2) `uniq` is approximate above the corpus size that hides it.** 047-1 measured it exact to
roughly 60,000–65,000 distinct and **off by 0.51% at 70,000** — five times the bound. DR-10
forbids reading raw events instead, so the reconciliation has to use the approximate figure
it is being asked to check.

**(3) The TTL boundary bites at any cardinality.** A TTL cuts at a timestamp and a daily
rollup's finest grain is a day, so the oldest day in a window is counted whole by the rollup
and partly deleted from the source. 047-1 measured 90 of 91 days agreeing exactly and the
91st differing by **4,941 — 0.49%**. Chapter 4.6 measured the same effect from the other
direction: a view counted 242,667 messages over 92 days where a backfill minutes later found
239,997 over 91.

**(4) "Counts derived from operational data" is not one number.** The clause names two
candidates and chooses neither, and they can diverge. Measured on the lane:

```
messages table            9,650
usage_periods.messages_sent  9,624
gap                             26      0.2694%   aggregate
                                       100%       worst tenant
                                        19        tenants over the bound
```

**Both of those are operational.** A reconciler cannot be written until somebody says which
number the clause means, and that is a decision this chapter must make rather than inherit.

**THE DIVERGENCE ITSELF IS THIS LANE'S, NOT THE PLATFORM'S** — established at analysis pass 1
and stated here so the chapter never publishes it the other way. The send path cannot drift:
the counter is incremented inside the same transaction as the insert, behind the same early
return. The gap comes from raw-SQL fixtures (`backfill.itest.ts`, `repository.itest.ts`,
`dual-write-walk.mjs`, `corpus.mjs`) and from `test-harness/sentinel.ts:159`, which deletes
counter rows while leaving messages. **All 31 disagreeing tenants belong to fixtures or walk
scripts; zero do not.**

So this is **not** a fourth obstacle to FR-ANL-06 — there are three — and the chapter says so
rather than publishing a lane artifact as a platform defect. What it is instead is the
demonstration that makes FR-006 necessary, and the reason the job compares per tenant: the
aggregate reads 0.2694% and nobody looks; the per-tenant split shows one tenant wrong by
everything it has, which is what sends somebody to find the cause.

## 3. What §2.3 has already decided, and this chapter must not re-litigate

`docs/12` §2.3 splits the milestone into two claims and gives the reason:

> FR-ANL-06 wants metered totals to agree with operational counts **within 0.1%**. The lane's
> largest membership set is five channels; 0.1% of a small number is an assertion that cannot
> fail for its own reason, which is the defect class this project keeps finding.

| half | claim | where |
|---|---|---|
| **CI gate** | a *planted* drift is detected and the reconciler raises | the lane, every run |
| **recorded measurement** | the 0.1% figure, at a volume where 0.1% is a real threshold | once, in the chapter |

So the deliverable is **a job plus a planted-drift test**, not a green number. The milestone
that closes on agreement is 4.9, not this chapter.

## 4. What this chapter does not decide

- **The customer-facing query surface is 4.8** (row 9, FR-ANL-07 and FR-ANL-10).
- **The milestone where the meter agrees is 4.9** (row 10).
- **`message_events`' producer is not this chapter.** `gaps.md` 051-1 records why: it is a
  send-path change on the busiest path in the platform, and Part 3's counters already
  maintain the same quantity synchronously for a reason `docs/12` §4 argues.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The job runs, compares, and reports a breach (Priority: P1)

An operator runs the reconciliation for a tenant and a period and gets, for each metered
quantity, the analytical total, the operational total, the difference, and whether it breached
0.1%.

**Why this priority**: it is the clause the chapter is named for, and nothing in the platform
compares the two sides today.

**Independent test**: run the job against the lane and read its output.

**Acceptance scenarios**:

1. **Given** a tenant with data on both sides, **When** the job runs for a period, **Then** it
   reports both totals, the absolute difference, the percentage, and a pass or breach verdict
   per quantity.
2. **Given** a quantity whose analytical side has no producer, **When** the job runs, **Then**
   it reports the breach with the reason rather than a bare percentage.
3. **Given** a tenant with no data on either side, **When** the job runs, **Then** it reports
   no comparison rather than a 0% agreement — **zero against zero is not agreement.**
4. **Given** the job has run, **When** its output is read, **Then** the operational number's
   source is named, because two operational counters disagree by 0.27%.

---

### User Story 2 - A planted drift is detected (Priority: P1)

The CI half of §2.3's split. A deliberate discrepancy is introduced and the job raises.

**Why this priority**: §2.3 says the 0.1% assertion cannot fail for its own reason at lane
volume, so the thing the lane can check is detection, not agreement.

**Independent test**: plant a drift, run the job, assert it raises; remove the drift, run it
again, assert it does not.

**Acceptance scenarios**:

1. **Given** a tenant whose two sides agree, **When** a drift larger than the threshold is
   planted on one side, **Then** the job raises for that tenant and quantity.
2. **Given** the same tenant, **When** the drift is removed, **Then** the job does not raise —
   **both halves of the probe, because a check that only ever fires is not a check.**
3. **Given** a drift smaller than the threshold, **When** the job runs, **Then** it does not
   raise, and the tolerance boundary is exercised from both sides.

---

### User Story 3 - The job is callable in isolation (Priority: P1)

`docs/12` row 8 names this explicitly: *"built to be callable in isolation (§2.3)."*

**Why this priority**: a reconciler that only runs inside a scheduler cannot be tested, and
§2.3's CI half depends on calling it directly.

**Independent test**: call it from a test with an explicit tenant and period and no scheduler,
no environment mutation, and no side effect beyond its report.

**Acceptance scenarios**:

1. **Given** a tenant and a period, **When** the job is invoked directly, **Then** it returns
   its report as a value rather than only emitting it.
2. **Given** two invocations with the same arguments, **When** both run, **Then** they produce
   the same report — the job reads and does not write.

---

### User Story 4 - The four obstacles are published, not discovered (Priority: P2)

The chapter states what prevents FR-ANL-06's 0.1% from holding, with the measurement behind
each.

**Why this priority**: two of the four have been carried in `gaps.md` since chapter 4.2 and
filed *for this movement*. This is the movement. A chapter that builds the job and publishes a
percentage without naming why the percentage cannot be trusted would be the most misleading
artifact in the series.

**Independent test**: each obstacle has a number in `baseline.txt` and a sentence in the
chapter.

**Acceptance scenarios**:

1. **Given** the job's report, **When** the chapter publishes it, **Then** each quantity that
   cannot meet the bound is named with its reason and its measurement.
2. **Given** the two operational counters, **When** the chapter names which one the job uses,
   **Then** the other is named too, with the gap between them.

---

### Edge Cases

- **Zero against zero.** A tenant with no messages on either side agrees perfectly and means
  nothing. The report distinguishes "no data" from "agreement", or the first green number this
  chapter publishes is a lie.
- **A period still open.** Reconciling today's figures compares a complete analytical rollup
  against an operational counter still being written. The period boundary has to be closed on
  both sides or the comparison measures the clock.
- **The rollup keeps history the raw side has lost.** The rollups carry a 25-month TTL and raw
  events 90 days, so beyond 90 days the operational side cannot answer at all and a comparison
  there is not a breach.
- **Two rollups now disagree legitimately.** `gaps.md` 051-4: `daily_usage_billing` and
  `daily_usage_v2` are fed by four views over two sources and nothing compares them. They
  disagreed by 2,670 once, correctly.
- **A tenant that existed for part of the period.** An environment created mid-period has a
  partial operational history and a rollup that starts when its first event arrived.
- **`uniq`'s error is a function of cardinality, not of row count.** A tenant with 70,000
  distinct users breaches on active users while agreeing on messages.

## Requirements *(mandatory)*

### Functional Requirements

**The job**

- **FR-001**: A reconciliation job shall compare, per tenant per period, each FR-ANL-05
  quantity's analytical total against its operational counterpart and report both totals, the
  difference, the percentage, and a verdict against 0.1%.
- **FR-002**: The job shall be **callable in isolation** — invoked directly with a tenant and
  a period, returning its report as a value, with no scheduler and no write.
- **FR-003**: The job shall name the operational source it used for each quantity.
- **FR-004**: A quantity with no data on either side shall be reported as **not compared**,
  never as agreeing.
- **FR-005**: A breach shall carry a reason where one is known, not only a percentage.

**The decision the clause does not make**

- **FR-006**: The chapter shall decide and record which number *"counts derived from
  operational data"* means for messages sent, and shall publish the gap to the rejected
  candidate with **what causes it**. Measured: `messages` 9,650 against
  `usage_periods.messages_sent` 9,624 — 0.2694% aggregate, 100% for one tenant — and every
  disagreeing tenant is a test fixture. **Publishing the gap without the cause would make a
  lane artifact read as a platform defect.**
- **FR-007**: The same decision shall be made and recorded for every other FR-ANL-05 quantity
  that has more than one operational candidate, or the absence of a second candidate stated.

**The alert**

- **FR-008**: A breach shall raise, and the raise shall be observable by a test rather than
  only by a human reading output.
- **FR-009**: The threshold shall be a named constant with its clause cited, not a literal.

**§2.3's two halves**

- **FR-010**: A **planted drift** shall be detected, asserted in the lane, and the same
  assertion shall be shown **not** raising once the drift is removed.
- **FR-011**: The tolerance boundary shall be exercised from both sides — a drift just over
  the threshold raises and one just under does not.
- **FR-012**: The 0.1% figure shall be measured **once, at a volume where 0.1% is a real
  threshold**, and recorded. §2.3: *"0.1% of a small number is an assertion that cannot fail
  for its own reason."*

**The obstacles**

- **FR-013**: The chapter shall publish all three obstacles with their measurements — the
  missing producer, `uniq`'s approximation and the TTL boundary — and shall publish the two
  operational candidates separately, as the question FR-006 answers rather than as a fourth
  obstacle.
- **FR-014**: Where an obstacle makes the 0.1% bound unreachable for a quantity, the chapter
  shall say so and shall not publish a percentage that implies otherwise.
- **FR-015**: `gaps.md` 047-1 and 048-1 shall be **re-measured and closed or restated** — they
  were filed *for this movement* and this is the movement.

**Documents**

- **FR-016**: Where a measurement falsifies a published document, that document shall be
  amended.
- **FR-017**: FR-ANL-06 shall be amended if this chapter's measurements show the clause as
  written cannot hold, following the precedent of DR-11 and DR-09.
- **FR-018**: `docs/12` §3's row 8 shall be amended where this chapter falsifies its one-line
  description.

**The chapter**

- **FR-019**: The chapter shall not re-derive 4.2's rollup mechanics, 4.6's two-rollup
  argument, or `docs/12` §4's two-counters argument. It cites them.
- **FR-020**: The chapter shall be registered in `relay-tutorial/lib/tutorial.ts`, with its
  title and slug fixed once and matching across the directory, the manifest `path` and the MDX
  `metadata.alternates`. **Chapter 4.4 shipped at 112 of 112 with a site that did not build**,
  and 4.6 reproduced the same failure before registering.
- **FR-021**: Prose shall stay inside the 2,000–4,000 word bound measured outside code fences,
  with at least one `<Trap>`, and both counted.
- **FR-022**: `pnpm check:fences` shall be reported as a delta against an opening measured in
  this feature, by kind and locale, with the two HEAD classes separated.
- **FR-023**: All eleven gates shall run, and every red shall be diagnosed against the
  opening rather than counted. **`pnpm test:integration` reports one failure where three lanes
  fail** (`gaps.md` 051-3), so the diagnosis cannot come from its summary.

### Key Entities

- **Reconciliation report** — per tenant, per period, per quantity: the analytical total, the
  operational total, the named operational source, the difference, the percentage, and a
  verdict of pass, breach, or not-compared.
- **Analytical total** — from `daily_usage_billing`, the rollup chapter 4.6 built for billing.
- **Operational total** — from Postgres. Which table is FR-006's decision.
- **Planted drift** — a deliberate discrepancy, introduced and removed, that makes the
  detection testable at a volume where the real threshold cannot fire.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The job runs against the lane and reports both totals, the difference, the
  percentage and a verdict for every FR-ANL-05 quantity.
- **SC-002**: A planted drift raises, and the same assertion is shown not raising with the
  drift removed.
- **SC-003**: The tolerance boundary is exercised from both sides.
- **SC-004**: The job is invoked directly from a test with a tenant and a period, and returns
  its report as a value.
- **SC-005**: Running it twice produces the same report, shown by a test.
- **SC-006**: A tenant with no data on either side reports not-compared, shown by a test.
- **SC-007**: The chosen operational source for each quantity is named, with the gap to any
  rejected candidate published.
- **SC-008**: All three obstacles are published with their measurements, and the two operational candidates are published as a separate finding with their cause.
- **SC-009**: The 0.1% figure is measured once at a volume where it is a real threshold, with
  the volume stated.
- **SC-010**: `gaps.md` 047-1 and 048-1 are re-measured, and each is closed or restated with
  its current number.
- **SC-011**: `check:fences` reported as a delta against an opening measured in this feature,
  by kind and locale, with the HEAD classes separated.
- **SC-012**: Prose measured outside code fences against the 2,000–4,000 bound, with the
  `<Trap>` count beside it.
- **SC-013**: `pnpm build` exits 0 with the chapter rendering.

## Assumptions

- **The job compares against `daily_usage_billing`, not `daily_usage_v2`.** 4.6 measured the
  channel-keyed rollup at 147,534 rows against 281 for the same data; billing reads the coarse
  one and so does its checker.
- **This chapter does not make the numbers agree.** §2.3 gives the agreement claim to the
  milestone at 4.9 and gives this chapter detection. A chapter that reported agreement would
  have to explain how, given that one side has no producer.
- **The alert is a log line and a non-zero exit, not a pager integration.** No requirement
  names a notification channel, and the platform has no alerting surface — `gaps.md` will
  carry what a real alert would cost.
- **"Period" means the calendar month `periodOf` already defines.** `services/api/src/quotas/period.ts`
  is the one definition, imported by the migration's default, the repository's predicate and
  the relay's read, *"because a quota that disagrees with itself about which month it is counts
  a tenant twice in one and not at all in the other."*
- **Part 4 is 22 chapters and this is the 7th**, movement IV of seven, with the milestone at
  the 9th.

## Dependencies

- Chapter 4.6's `daily_usage_billing` and `services/ingester/src/metering.ts`.
- Postgres `usage_periods` and `usage_active_users`, and `periodOf`.
- The composed stack with ClickHouse reachable from outside its container, and
  `RELAY_POSTGRES_PORT=15432`.
- **A corpus for FR-012's measurement**, and with it the bind `gaps.md` 051-2 records: the
  loader is `postgresql()`, which constitution III's first prohibition forbids.
- **An ingester for any integration test that waits on a row** (051-3, 050-8).
