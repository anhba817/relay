# Relay — Metering Reconciliation Measurement

**Date:** 2026-09-17
**Subject:** FR-ANL-06 **as amended at SRS revision 1.14**, for the one quantity the amended
clause says can meet the bound
**Method:** `T` — and this document is **evidence, not the verification**. `docs/11` could put
`Method: A` at its head because NFR-SCL-01's verification letter is `A` and a published analysis
*is* the verification for an `A` clause. FR-ANL-06's letter is **`T`**: the discharge is the
planted-drift suite that runs on every push (`services/api/src/metering/reconcile.itest.ts`), and
what follows is the figure that suite cannot produce, taken once at a volume where 0.1% means
something.
**Harness:** `relay-platform/scripts/scale/` — `corpus.mjs`, then `load-analytics.mjs`
**Clause under verification:** FR-ANL-06 as amended at SRS 1.14. Verifying the original would
mean publishing a number the SRS itself says cannot exist for three of the four quantities.

---

## Why this exists

`docs/12` §2.3 splits movement IV's milestone in two, and the half that needs a document says:
*"the 0.1% figure, at a volume where 0.1% is a real threshold"*. The other half — a planted
drift the lane catches every run — is a test, and it is where the clause is actually discharged.

The reason for the split is a number. **0.1% of a small count is an assertion that cannot fail
for its own reason**, because a count is a whole number of messages and below some volume the
smallest drift that exists already breaches:

    volume        9      100    1,000   10,000   100,000
    smallest      1        1        2       11       101
    as a %   11.111    1.000    0.200    0.110     0.101

At the lane's own largest tenant-period — 1,017 messages — the smallest expressible drift is
**0.197%, twice the bound**. Every drift there breaches, so a green 0.1% assertion at that size
claims that nothing drifted at all. That is what this measurement exists to avoid, and it is why
it needed a corpus rather than the lane.

## What was measured

One corpus, built by the platform's own harness against a disposable PostgreSQL database, loaded
into the lane's ClickHouse by the same `postgresql()` table function chapter 4.2 established, and
reconciled by the job `scripts/reconcile-usage.mjs` runs — **not by a query written for this
document**.

    corpus            relay_corpus_20260917151241, built in 51.9 s
                      389,277 messages · 2 environments · 91 days · 2,000 channels
                      subject environment a2e82259-b5aa-41b1-b5ca-b544feb44163
    operational       usage_periods 8 rows · usage_active_users 21,999 rows
                      written by corpus.mjs from the messages rows it had just written
    analytical        402,424 events sent · 397,978 held over 91 days · 573 ms
                      message_events → mv_billing_messages → daily_usage_billing
    the tenant-period 2026-08, the largest the corpus produced

**The volume is read off the harness's own report, not derived from its knobs.**
`CORPUS_MESSAGES` is the subject environment's ninety-day window rather than a total, and the
split across channels is floor division with a remainder, so any figure computed from the
parameters is an estimate. The number below is a count.

## Results

    quantity            analytical   operational   difference   verdict   standing
    -----------------   ----------   -----------   ----------   -------   ---------------------
    messages               121,057       121,057      0.0000%   pass      THE MEASUREMENT
    activeUsers              5,000         5,000      0.0000%   pass      agrees by construction
    connectionMinutes            0             0      0.0000%   pass      zero against zero
    storedMessages         285,187        absent            —   not-comparable

    exit code 0 · 31 days of rollup rows for the tenant-period · window 2026-08-01 … 2026-09-01

**Three of the four passes are not evidence, and a table without that last column reads as
corroboration.**

- `activeUsers` agrees **by construction**: `uniq` is exact below 65,536 distinct and the corpus
  holds 5,000 users, so both sides count the same set exactly. The amended clause excludes this
  quantity at scale for the opposite reason — 0.5676% at 65,537.
- `connectionMinutes` is **0 against 0**, and `differencePct` returns 0 for that because
  both-zero is agreement. The corpus writes no connections and the harness says so in its own
  report rather than letting a reader infer one.
- `storedMessages` has **no operational counterpart anywhere in this platform**, which is a fact
  about the platform rather than about this tenant.

### What 0.1% can express at this volume

    volume 121,057        under        over
    smallest drift          122         122
    as a %              0.10078%    0.10068%

The two directions are computed separately because `max(analytical, operational)` is the
denominator: a surplus of `d` divides by `volume + d` and a shortfall by `volume`, so the surplus
is always the harder one to breach. They coincide here. **They do not always** — see the finding
below.

### The drift, planted at the bound and one unit past it

Planted by moving the **operational** counter and re-running the same job, at the measurement's
own volume. `smallestExpressibleDrift(121057)` predicts 122 in both directions; the job was not
told about that function.

    operational   analytical   difference   verdict   exit
    -----------   ----------   ----------   -------   ----
        121,057      121,057      0.0000%   pass         0    the measurement
        120,936      121,057      0.1000%   pass         0    short by 121 — AT the bound
        120,935      121,057      0.1008%   breach       1    short by 122
        121,178      121,057      0.0999%   pass         0    over by 121
        121,179      121,057      0.1007%   breach       1    over by 122

**121 passes and 122 breaches on both sides**, which is what the function said and what the
resolution table above means in practice. The two breaching runs exited 1 with
`reconcile: 1 breach(es) … messages` — FR-ANL-06's *"raises an alert"*, in the only form this
platform can currently give it.

**And the boundary cases sit ON the bound, shown by breaking the comparison.** Changing
`pct <= threshold` to `pct <` in `verdictFor` and running the whole integration gate moved
**exactly one assertion** of 676 — `puts analytical 99900 on the pass side of the bound`, in
`services/api/src/metering/reconcile.itest.ts`. The gate reported it by name and exited 1 while
**all 54 suites still ran**, which is the change ADR-27 is about: before this chapter a run that
went red stopped scheduling, and five lanes went unexecuted.

## What this says about the bound, and about the three quantities the clause excludes

FR-ANL-06's bound is met, for messages sent, at a volume where meeting it means something: the
smallest drift this tenant-period can express is 122 messages, and the measured difference is 0.

The amended clause names three quantities that cannot meet it, and this corpus shows why each
one is excluded rather than failing:

| quantity | why the bound is unreachable | what this corpus shows |
|---|---|---|
| unique active users | `uniq` is exact to 65,536 distinct and **0.5676%** at 65,537 — a cliff one user wide | 5,000 users, comfortably below the cliff, so the 0.0000% here is a fact about the corpus |
| any quantity at the retention boundary | a daily rollup's finest grain is a day and the TTL cuts at a timestamp, so the oldest day disagrees by **0% at midnight rising to 1.0989% just before it** | the corpus spans 91 days against a 90-day TTL, and **4,446 rows were removed on the way in** — the window measured is well inside what survived |
| connection-minutes | the meter bills every calendar minute a connection was open; the records bill only connections that **closed** | 0 against 0, which is agreement and is not evidence |

## The finding nobody was looking for

**The smallest expressible drift is not the same number in both directions, and five measured
volumes said it was.**

Chapter 4.7 published *"the smallest breaching drift is 101 in both directions"* at 100,000, and
this feature's own phase 1 re-derived the table at 9, 100, 1,000, 10,000, 100,000 and the lane's
1,017 — over and under equal at every one. All six land on the agreeing side by luck:

    volume        under     over
       999            1        2     the first volume where they differ
     1,000            2        2
     1,017            2        2     the lane's largest tenant-period
   121,057          122      122     this measurement's
 1,000,000        1,001    1,002     and every volume above a million differs

**500,500 of the 999,999 volumes below a million differ** — half of them. At 999 a surplus of one
message passes and a shortfall of one breaches, on the same bound. The rule is one line of
arithmetic: the denominator is `max(analytical, operational)`, so a surplus divides by a larger
number than the shortfall it mirrors.

It was found by writing the function rather than by reading the table, which is the whole
argument for `smallestExpressibleDrift` existing at all: six samples agreeing is not a rule.

## What this figure does not prove

**Both sides come from the same rows.** `corpus.mjs` writes the messages, then derives
`usage_periods` and `usage_active_users` from them with a `GROUP BY`; `load-analytics.mjs` reads
the same rows into `message_events`, and the materialised view rolls those into
`daily_usage_billing`. The two agree by construction. The harness prints that sentence in its own
closing report so a reader does not have to find it in a chapter.

So what is established here is **the reconciler's arithmetic at volume, and what 0.1% can express
at that size**. What is *not* established is that the platform's own two counters agree when the
platform writes them.

**That is established by a mechanism, and it was measured separately.** `sendMessage` writes the
message and increments the counter in one transaction, and chapter 4.7 found **0 of 1,385
tenant-periods disagreeing for a non-fixture reason** — every disagreement attributable to a
fixture doing a raw `INSERT INTO messages` or a hard `DELETE`.

**The alternative was rejected on cost rather than on principle.** Driving 100,000 messages
through the real send path at the lane's measured 20.5 ms p95 is over half an hour of wall clock,
and what it would measure is the send path — the harness — rather than the meter.

## What went wrong while measuring, and why the numbers still stand

**The loader's own report was a whole-table count, and a second corpus exposed it.**
`load-analytics.mjs` computed `removed_by_ttl` as `events_sent - count(*)` over the whole
`message_events` table. Loading a second corpus while the first sat there printed:

    removed_by_ttl   -393,562

A negative TTL. Nothing in the figures above came from that arithmetic — the row counts are
scoped queries — but the number was published by the script that produced the load, and a reader
would have had no reason to doubt it. Every count that script prints is scoped to the corpus's
own environment ids now, which is also what makes the cleanup below possible.

**And the TTL behaved differently on two loads of the same data.** The first removed its 4,425
rows **at INSERT**; the second removed none there and all 4,446 at the merge. Chapter 4.2's
*"the TTL is a schedule, not an event"*, now observed in both directions rather than one. Asked of the
store, the oldest day surviving for this tenant is **2026-06-19**, which is exactly
`today() - 90` — so the cut falls **43 days before** the window this measurement quotes opens,
and neither behaviour reaches it.

**The corpus's period expression carries a control that cannot fail on this lane.** The counter
rows are keyed by `date_trunc('month', created_at at time zone 'UTC')`, matching
`quotas/period.ts`, and the harness also computes the same aggregate **without** the zone and
reports both. On this server they are identical — `show timezone` is `UTC` — so **this lane
cannot demonstrate the failure the zone exists to prevent**. Reported rather than asserted, for
that reason.

## Reproducing

Every command below was run as written. `RELAY_POSTGRES_PORT=15432` is this machine's lane
(the host's own PostgreSQL holds 5432).

    cd relay-platform
    docker compose up -d --wait
    pnpm build                                   # the harness runs the built migrator

    CORPUS_MESSAGES=350000 CORPUS_ENVIRONMENTS=2 CORPUS_DAYS=91 \
      node scripts/scale/corpus.mjs > corpus.json

    node analytics/apply.mjs                     # BEFORE the load: a view is a trigger
    node scripts/scale/load-analytics.mjs --corpus corpus.json

    node scripts/reconcile-usage.mjs \
      --environment "$(jq -r .largest_period.environment_id corpus.json)" \
      --period      "$(jq -r .largest_period.period corpus.json)" \
      --database    "postgres://relay:relay@localhost:15432/$(jq -r .database corpus.json)"

**`analytics/apply.mjs` runs before the load and the order is not cosmetic.** A materialised view
is a trigger on future inserts, not a query over history (chapter 4.6), so a corpus loaded before
the views exist produces an analytical side of zero. **And the backfill is not the recovery**:
`daily_usage_billing` is a `SummingMergeTree`, so a second `INSERT … SELECT` sums with the first
and doubles every count, while the applier's ledger makes re-running `0013` a silent no-op.

**The commands above were run from a clean state as published**, and the figure they produce is
reproducible in shape rather than to the message: a second corpus built with the same knobs put
its largest tenant-period in **2026-07 at 120,471 messages**, agreeing at 0.0000%, where the
smallest expressible drift is 121. `corpus.mjs` distributes `created_at` with `random()`, so
which month is largest and by how much is not fixed — which is why every figure in this document
is read off the harness's report rather than computed from its parameters.

**The three knobs are floors the harness enforces**, and the reasons are about measurement rather
than size: `CORPUS_DAYS` must exceed 90 or the date predicate excludes nothing, and
`CORPUS_ENVIRONMENTS` must be at least 2 or the tenant predicate excludes nothing.
`CORPUS_MESSAGES` is the **subject environment's ninety-day window**, so a month is roughly a
third of it.

## What this left in the lane

The corpus's analytical half loads into `relay_analytics` — **the lane's own store**, beside four
chapters' data — and the only cleanup this repository shipped before this measurement was
`analytics/apply.mjs --drop-all`, which is `DROP DATABASE`.

One run leaves:

    .inner_id.3f6e34d9-…  (chapter 4.2's daily_usage)        184 rows
    daily_usage_billing                                      184
    daily_usage_v2                                       172,965
    message_events                                       398,000
                                                         571,333 rows

The scoped cleanup is `node scripts/scale/load-analytics.mjs --corpus corpus.json --clean`. It
asks `system.columns` which tables carry an `environment_id` and `system.tables` which of those
are not views — **a hand-maintained list would have missed the first row, whose name is a UUID
and which no document mentions** — deletes by this corpus's environment ids, polls
`system.mutations`, and then **counts**, because a mutation is not a delete.

Run against both corpora built for this measurement:

    corpus 1     571,333 rows removed, 0.7 s, 0 mutations pending, after-count 0
    corpus 2     570,974 rows removed,        after-count 0

**And the store is not quite where it started, for a reason that is not the corpus.**

    before the corpus    message_events 0 · daily_usage_billing 7 rows over 4 environment ids
    after the cleanup    message_events 0 · daily_usage_billing 9 rows over 6 environment ids

`message_events` is exactly back. The two extra rollup rows carry **connection-minutes and no
messages**, and they belong to two gateway test tenants — they arrived because **this chapter
made the lane drain its own analytics stream**. `request-log.itest.ts` now starts an ingester for
its own duration, and the first run of it consumed a 1,038-record backlog that had been sitting
on the stream since chapter 4.4 because nothing had ever consumed it. Records that used to
accumulate on a queue now become rollup rows.

That is a change to the opening state every later analytical chapter inherits, so it is said here
rather than left for somebody to find as a drift.

**A bare `count()` on a `SummingMergeTree` is not a stable number, and this comparison was wrong
once before it was right.** Taken immediately after the second cleanup, `daily_usage_billing`
read **15**; taken again after the background merge, **9**, with `count() FINAL` and
`uniqExact((environment_id, day))` both also 9. The rows had not gone anywhere — they were
unmerged parts holding the same keys. **Any before-and-after on a summing table has to be taken
against a merge-stable measure**, which is the same lesson chapter 4.2 learned about the TTL from
the other direction: a count taken the moment a load finishes describes a moment, not a state.
