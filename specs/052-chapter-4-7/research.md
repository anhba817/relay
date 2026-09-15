# Research — 052, chapter 4.7, "the job that checks the meter"

**Ten items. Eight were run against the lane rather than reasoned about, and two changed what
the chapter is.** No probe wrote anything: every measurement below is a `SELECT`.

---

## R1 — Which number is *"counts derived from operational data"*? **TWO CANDIDATES, AND THEY DISAGREE**

**Measured.** FR-ANL-06 compares metered totals against *"counts derived from operational
data"* and does not say which count.

    messages, joined to channels for the tenant   9,650
    usage_periods.messages_sent                   9,624
    gap                                              26      0.2694%

**Both are operational**, and the gap is nearly three times the clause's own 0.1% bound before
the analytical store is consulted at all.

**And the aggregate hides the shape.** Per environment:

    aggregate gap                0.2694%
    worst tenant                   100%      messages present, none counted
    tenants over 0.1%                 19
    the common shape                  31 environments at exactly 70 messages / 68 counted

**FR-ANL-06's totals are per tenant.** A reconciler that aggregates reports 0.2694% — a number
a reader rounds away — while 19 tenants breach and one is wrong by everything it has.

**Decision**: the job compares **per tenant per period** and never aggregates before verdict.
The chosen operational source is named in the report, and the rejected one is published with
its gap.

**Cause: unresolved, and it is a phase-1 task rather than a guess.** `repository.ts` holds one
`insert(messages)` at line 4214 and increments `usagePeriods` at 4344, inside the same
transaction, on the inserted branch only — *"a recognised idempotent retry wrote no message and
must consume no quota either"*. That path keeps the two equal. Something else writes messages,
the gap is entirely inside the current period rather than historical, and its shape is too
regular to be incidental.

## R2 — What does the counter count? **INSERTED MESSAGES, BY DESIGN AND FOR A MEASURED REASON**

**Read, not assumed.** `repository.ts:4325` explains why it is an increment rather than a
query: *"the alternative is a read over `messages`, which carries no `environment_id` and no
index on `created_at`: the month predicate becomes a Filter applied after every row the tenant
has ever sent is read off the heap. Fast today, and proportional to lifetime traffic forever."*

**This is the argument against the other candidate.** Chapter 4.1 measured that read at 585.9
ms over 1,000,000 rows. So the counter is the operational number a reconciler can afford, and
the table is the one it would rather trust — which is the whole of R1's decision in one
sentence.

## R3 — Which FR-ANL-05 quantities have an operational counterpart at all?

**Measured** — `usage_periods`' columns are `environment_id, period, messages_sent,
created_at, connection_minutes`, and `usage_active_users` is a separate membership table.

| quantity | operational source | comparable? |
|---|---|---|
| messages sent | `usage_periods.messages_sent` | yes, and R1's gap applies |
| connection-minutes | `usage_periods.connection_minutes` | yes |
| unique active users | `usage_active_users` | yes, and `uniq`'s error applies |
| stored message count | **none** | **no** |

**Decision**: the report carries a **not-comparable** verdict as a first-class outcome, not an
error. Three of four quantities have an operational side; the stored count has none, and
saying so is more useful than omitting the row.

## R4 — How many tenants have data on both sides? **FOUR AGAINST SIX HUNDRED AND SEVENTY-FIVE**

**Measured.**

    environments in daily_usage_billing      4
    environments in usage_periods          675

So 671 tenants have an operational history and no analytical rows at all. Every one of them is
a 100% breach, and the reason is chapter 4.6's: `message_events` has no producer.

**Decision**: the report distinguishes **not compared** (no data on either side) from
**breach** (data on one side only). Collapsing them would let the platform's largest defect
read as an absence of data.

## R5 — What shape is a job this platform can call in isolation? **`scripts/*.mjs`**

**Measured** — the established shape is a standalone script: `reset-lane.mjs`,
`consumer-walk.mjs`, `credential-walk.mjs`, `signup-walk.mjs`, `backfill-channel-activity.mjs`.

**Decision**: the comparison logic is a **module** under `services/`, and any script is a thin
caller. `docs/12` row 8 says *"callable in isolation"*, and chapter 4.6 measured the cost of
the other choice: `analytics/` is outside `vitest.coverage.config.mts`'s include, so a script
there can carry no per-file pin and no test can reach it — which is how `analytics/query.mjs`
became a file nothing runs.

## R6 — What can "raises an alert" mean here? **A LOG LINE, A NON-ZERO EXIT, AND ONE PRECEDENT**

**Measured**: the platform has no alerting integration. The one notification path that exists
is `services/api/src/quotas/quota-email.ts`, which sends mail through
`../notifications/mailer` when a quota threshold is crossed — and whose failure mode is
already visible in the lane as `quotas.unaddressable: no member has an email address`.

**Decision**: the breach raises as a structured log line and a non-zero exit, and the chapter
names what a real alert would cost rather than pretending the log is one. The quota-email path
is the precedent worth citing, including its failure mode: **a notification with no recipient
is not an alert.**

## R7 — Is a period closed? **NO, AND THE COMPARISON HAS TO SAY SO**

`periodOf` is the calendar month in UTC, and `services/api/src/quotas/period.ts` is the single
definition — *"a quota that disagrees with itself about which month it is counts a tenant twice
in one and not at all in the other."*

Reconciling the current period compares a rollup that is still being written against a counter
that is still being incremented. **Decision**: the job takes an explicit period and the
chapter's published measurement uses a closed one. A reconciler run against an open period
measures the clock.

## R8 — The 25-month/90-day asymmetry

The rollups carry a 25-month TTL (chapter 4.6, DR-09) and `message_events` 90 days. Beyond 90
days the raw side cannot answer, and `usage_periods` has no TTL at all.

**Decision**: a period older than the raw retention is **not comparable against raw events**,
and the job says so rather than reporting the rollup's number as unverified agreement. This is
DR-09's two halves meeting, and it is not a defect.

## R9 — 047-1's two obstacles, carried since chapter 4.2

Both filed *for movement IV*, both re-measured in the features since and neither closed.

- **`uniq` is exact to roughly 60,000–65,000 distinct and off by 0.51% at 70,000** — five times
  FR-ANL-06's bound. DR-10 forbids reading raw events instead, so the reconciliation must use
  the approximate number it is checking.
- **The TTL boundary bites at any cardinality**: 90 of 91 days agreeing exactly and the 91st
  differing by 4,941, **0.49%**. Chapter 4.6 measured the same effect from the other side — a
  view counting 242,667 over 92 days where a backfill found 239,997 over 91.

**Decision**: neither is fixable here and both are this chapter's to **close or restate**. The
honest resolution is an amendment to FR-ANL-06 rather than a tolerance quietly widened to fit,
and the chapter must say which quantities the 0.1% can apply to at all.

## R10 — What §2.3 already decided, and it is the plan's spine

> FR-ANL-06 wants metered totals to agree with operational counts **within 0.1%**. The lane's
> largest membership set is five channels; 0.1% of a small number is an assertion that cannot
> fail for its own reason.

| half | claim | where |
|---|---|---|
| **CI gate** | a *planted* drift is detected and the reconciler raises | the lane, every run |
| **recorded measurement** | the 0.1% figure, at a volume where 0.1% is a real threshold | once, in the chapter |

**Decision**: the deliverable is a job plus a planted-drift test, both halves of it. The
agreement claim belongs to the milestone at chapter 4.9.

---

## What the research changed

1. **R1 turned "build a reconciler" into "decide what it compares against".** Two operational
   numbers, 0.2694% apart in aggregate and 100% apart for one tenant, and the clause names
   neither.
2. **R1's per-tenant split changed the job's shape.** Aggregating before the verdict turns 19
   breaches into one number below a threshold nobody would question.
3. **R4 made "not compared" a first-class outcome.** 671 tenants have one side only, and a
   reconciler that treats that as missing data hides the defect this movement exists to expose.

**R2, R5, R7 and R10 came back confirming what a document already said**, which is what makes
R1 and R4 worth acting on.
