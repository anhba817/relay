# Data model — feature 054, chapter 4.9

Nothing here is a new table. This feature writes rows into tables that exist and reads them
with a function that exists; what it defines is **which rows, in which database, and derived
from what**.

---

## The two sides of one comparison

    operational (PostgreSQL)                    analytical (ClickHouse)
    usage_periods                               daily_usage_billing
      environment_id  → environments.id           environment_id
      period          date, YYYY-MM-01            day             date
      messages_sent   bigint, >= 0                messages        UInt64
      connection_minutes bigint, >= 0             connection_minutes
    usage_active_users                            active_users_state  AggregateFunction(uniq)
      (environment_id, period, user_id,           stored_delta        Int64
       first_seen_at) — ONE ROW PER USER

`reconcile(db, store, { environmentId, period })` compares four quantities for one tenant and
one period, and the period is a **month** — `YYYY-MM-01`. The rollup is keyed by day, so the
range is half-open: `day >= period AND day < nextPeriod(period)`.

**Three of the four cannot meet 0.1% and the amended clause says so.** The comparison this
feature measures is `messages` against `usage_periods.messages_sent`.

---

## Where the rows live, which is the part that has never worked

`corpus.mjs` builds `relay_corpus_<timestamp>` in PostgreSQL and **refuses `relay`** (chapter
4.2). It runs the platform's migration runner against that database, so `usage_periods` and
`usage_active_users` exist there and are empty.

`load-analytics.mjs` reads that database from ClickHouse through `postgresql()` and writes
`message_events` — **in `relay_analytics`, the lane's own database** (`load-analytics.mjs:14`),
which is why the views are reached at all and why a run leaves ≈389,000 rows behind that only a
scoped cleanup removes (R6a). `daily_usage_billing` is fed from there by two materialised views
on future inserts. Measured: an MV does fire on an `INSERT … SELECT` from a table function, and
a second identical insert **doubles** the `SummingMergeTree`'s sum — 3 rows and sum 30 became 6
and 60 on a probe built for the question.

So the chain is:

    corpus.mjs ──► relay_corpus_<ts>.messages ──► message_events ──► daily_usage_billing
                            │
                            └──► usage_periods            ◄── THIS ARROW DOES NOT EXIST

**The missing arrow is the whole of FR-005 and FR-006.** Measured: `usage_periods` appears once
in `corpus.mjs`, as a row count in its closing report, and `usage_active_users` not at all.

---

## What the harness writes, and what it must not

**For each environment it created, for each period the messages span:**

| row | derived from | rule |
|---|---|---|
| `usage_periods` | `count(*)` of that environment's `messages` in that period | one row per `(environment_id, period)` |
| `usage_active_users` | `distinct user_id` of those messages, excluding null senders | one row per `(environment_id, period, user_id)` |

**Null senders are excluded, and there are three reasons rather than the one first written
down.** `corpus.mjs` writes a `CORPUS_NULL_SENDER_RATIO` of deleted authors. `usage_active_users.user_id`
is not nullable — and it is also a **foreign key to `users.id`** (`schema.ts:1043`), so there is
no row to reference even if the column allowed it. And the analytical side's `uniqState(user_id)`
ignores NULL (chapter 4.2's pass 1), so the two agree only if the operational side excludes them
too. **The foreign key is the strongest of the three**: it makes the rule the schema's rather
than the harness's, and a harness that got it wrong would fail loudly instead of drifting.

**It must not write into `relay`.** `usage_periods.environment_id` is a foreign key, so a write
for a corpus environment into the lane's database would fail — which is the schema refusing the
mistake rather than a rule anyone has to remember. Constitution IV's *"only the API service
writes to PostgreSQL"* is the clause; a disposable measurement database is not the product's
store, and the lane's is.

---

## The drift, planted

A planted drift is an adjustment to **one side** of one tenant-period, of a stated size, applied
after both sides exist. The reconciler's arithmetic decides the verdict:

    difference = |analytical - operational| / max(analytical, operational)
    verdict    = difference <= 0.001 ? pass : breach

**So the smallest breaching drift is the same size in both directions**, and a drift computed
against the smaller side lands inside the bound (chapter 4.7). At volume *v* the smallest
breaching integer drift is:

    v            9    100    1,000   10,000   100,000
    smallest     1      1        2       11       101
    as a %  11.111  1.000    0.200    0.110     0.101

---

## The two counters are one unit, and writing half of them is a breach

`reconcile.ts:177` builds the active-user comparison as
`op.messagesSent === null ? null : op.activeUsers`. Chapter 4.7 wrote that to cover the tenant
with **no `usage_periods` row at all** — then both sides are null and the verdict is `no-data`.

It does not cover the state a half-built harness is in. **With `usage_periods` written and
`usage_active_users` not**, `messagesSent` is non-null, so `activeUsers` is read as **0** — and
`usage_active_users` is a COUNT OF ROWS, so absent and zero are the same number on that side.
Against an analytical `uniqMerge` of ≈5,000 that is a **`breach`**, and it is the harness's
breach rather than the platform's.

So the two writes are one unit. **Both row counts are asserted before the reconciler is asked
anything**, which is the same positive control the analytical side gets (R6a): a verdict
computed over a side nobody checked arrived is a verdict about the harness.

---

## What the four rows will actually say, which is not "three of four agree"

The reconciler compares four quantities and a messages-only corpus gives each a different
standing. Printing the verdicts without that column is how a vacuous pass reads as corroboration.

| quantity | analytical | operational | verdict | standing |
|---|---|---|---|---|
| `messages` | the MV's sum | `usage_periods.messages_sent` | pass or breach | **the measurement** |
| `activeUsers` | `uniqMerge`, ≈5,000 distinct | count of `usage_active_users` rows | pass | **agrees by construction** — `uniq` is exact below 65,536 and `CORPUS_USERS` defaults to 5,000 |
| `connectionMinutes` | 0 — the messages view leaves the column at its default and `SummingMergeTree` sums it | 0 — the harness writes it (T022) | pass | **vacuous.** `differencePct` returns 0 when the denominator is 0, because both-zero is agreement |
| `storedMessages` | — | — | not-comparable | no operational source anywhere in this platform |

`exitCodeFor` returns 0, correctly. **Three of those four passes are not evidence**, and chapter
4.7 already wrote the general form of the mistake: *a green 0.1% assertion at lane scale claims
that nothing drifted at all.* Here it is again as 0 against 0.

---

## The verdicts, and the two this feature exists to stop seeing

`verdictFor` decides from **presence before arithmetic**:

| verdict | when |
|---|---|
| `not-comparable` | no operational counterpart exists for the quantity — the stored message count has none in this platform |
| `no-data` | this tenant holds nothing on either side |
| `pass` | both sides present and within the bound |
| `breach` | both sides present and outside it |

**Every tenant in the platform is in one of the first two**, measured at chapter 4.7 and again
here: 4 environment ids in `daily_usage_billing` of which 0 exist in PostgreSQL, against 2,212
environments with operational usage and no rollup rows. SC-005 is the requirement that the
measurement's tenant is in neither.
