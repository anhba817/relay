# Research — 051, chapter 4.6, "metering you can bill on"

**Eleven items. Nine were run against the running store rather than reasoned about, and three
of those changed the design.** The probes wrote to a scratch database `r051_probe` and one
planted row in `relay_analytics.message_events`; both are cleaned up and the cleanup is
verified below, because 043 measured what a probe left behind costing a later measurement
its meaning.

Every probe opened with `SELECT 1` as a positive control. 047 read three authentication
errors as data.

---

## R1 — Can one rollup table be fed from several source tables? **YES, AND IT DECIDES THE SHAPE**

**Measured.** A materialised view fires on inserts to exactly one source table, so no single
view can carry FR-ANL-05's four quantities: messages and active users come from
`message_events`, connection-minutes from `connection_events`. The question is whether the
four can still land in **one** rollup row.

Two views, two different sources, one `TO` target:

    view over the message source  -> delta   1
    view over the connection source -> delta 100
    SELECT sum(delta) FROM target -> 101

**Decision**: one rollup table with an explicit `TO` target, and one view per source table
feeding it. This is the ClickHouse idiom rather than a trick, and it is the only shape in
which "per tenant per day" is one row rather than a join across four.

**Alternative considered**: a rollup table per source, joined at read time. Rejected — it
makes every metering read a join over four tables, which is the shape 4.1 measured at 585.9
ms and 4.2 replaced.

## R2 — Does `SummingMergeTree` sum a signed delta? **YES**

**Measured.** `multiIf(event='created', 1, event='deleted', -1, 0)` as `Int64` over two
creations, one deletion and one edit:

    sum(delta) = 1

**Decision**: stored message count is a **running balance of signed deltas**, which is the
technique DR-17 already states for its media analogue — *"summing `media_events` deltas
(uploaded/deleted)"*. The chapter cites DR-17 rather than deriving it.

**Note the shape difference this settles**: every other metered quantity is a daily flow and
this one is a stock. A daily row holding the day's *delta* is not the stored count; the
stored count is the cumulative sum of deltas up to that day, and the read has to say so.

## R3 — Can a view expand one connection into its calendar minutes? **YES, AND IT REPRODUCES THE METER'S RULE**

**Measured.** `arrayJoin` over a minute range inside the view's SELECT, against a connection
running 00:00:59 to 00:01:01 — two seconds of wall clock:

    calendar-minute buckets: 2

That is `meter.ts`'s documented rule verbatim — *"Open at 00:00:59 and closed at 00:01:01 is
two seconds of wall clock and TWO connection-minutes"* — computed in the analytical store
from a close record alone. The expansion also assigns each minute its own `toDate`, so a
connection spanning midnight splits across two days without special handling.

**This is the item that makes SRS Appendix C question 4 answerable here.** Both definitions
are buildable — elapsed duration is `sum(duration_ms)` and the calendar bucket is the
expansion above — so the chapter faces a **choice about what a customer is charged for**,
not a constraint about what the store can compute. A chapter that put a number in a billing
table while leaving that open would be publishing an undefined unit.

## R4 — Is a close record enough on its own? **YES**

**Measured** against `relay_analytics.connection_events`:

    ts                        close_code  duration_ms   ts - duration_ms
    2026-09-15 02:58:03.876   1000        252           2026-09-15 02:58:03.624

The close row carries the closing instant and the elapsed duration, so both endpoints are
recoverable from one row. The open record is not needed to compute either definition of a
connection-minute.

## R5 — How many connections have both records? **55 OF 99. FORTY-FOUR PERCENT DO NOT**

**Measured on the store as it stands:**

    both records   55
    one only       44
    connections    99

**This is the number that constrains FR-002.** Chapter 4.5 measured why: `sessions.close()`
calls `wss.close()`, which does not close established sockets, so a clean stop produces opens
with no closes and a kill produces neither — and 050-5 files the consequence. R4 says a close
record alone is sufficient; R5 says **44% of the connections in this store have no close
record at all**, so those connections contribute **zero** connection-minutes rather than a
wrong number.

**Decision**: the metering read is defined over closes, and the chapter **publishes the
opens-without-closes count beside the minutes figure** rather than silently billing a
fraction of reality. That is FR-009a's scoping lesson one domain over: scope the comparison
and say what the scope excluded.

**Alternative considered**: impute a close at the end of the window for a dangling open.
Rejected for this chapter — it invents a duration, and 047's zero-UUID phantom user is what
inventing a value to satisfy a schema costs.

## R6 — Which of FR-ANL-09's four dimensions does the source carry? **TWO OF FOUR, AND THE THIRD IS FREE**

**Measured** — `message_events`' columns:

    environment_id  UUID
    channel_id      UUID
    user_id         Nullable(UUID)
    ts              DateTime64(3, 'UTC')
    event           LowCardinality(String)
    text_length / attachment_count / delivery_latency_ms

FR-ANL-09 names **application, environment, channel, day**.

- **environment** and **day** are the shipped view's sorting key.
- **channel** is on the row and nothing groups by it — so it costs a key column, not a join.
- **application** is on no row in the analytical store, and the store holds no `applications`
  table. An application holds two environments (`unique (application_id, kind)`, 046's
  finding), so application-level usage is a sum over that tenant's environments — which
  needs the mapping, and the mapping lives in Postgres.

**Decision**: add channel to the rollup's key; record application as an open item with its
cost named, which is FR-010. Putting a Postgres join behind a ClickHouse metering read is a
cross-path read and would want constitution III argued rather than assumed.

## R7 — What shape is the shipped view, and what does extending it cost? **AN IMPLICIT INNER TABLE**

**Measured** — `system.tables` for `relay_analytics`:

    .inner_id.3f6e34d9-d701-42a3-8d17-4190849c92e5   SummingMergeTree
    daily_usage                                      MaterializedView
    message_events / api_requests / connection_events / webhook_attempts / schema_applied

4.2's view was created with an inline `ENGINE =` and therefore owns an **implicit inner
table**. There is no named target for a second view to write into, so R1's shape is not
reachable by adding a view alongside it.

**Decision**: the plan phase decides between converting `daily_usage` to an explicit `TO`
target and leaving it in place beside a new rollup. **What must not happen is a bare `DROP`
of the source under a live view** — 047 measured that succeeding with no error and leaving an
orphan that answers queries with zeros, and recorded that the direction which errors is the
safe one.

**And the migration ledger makes this concrete**: `analytics/` statements are keyed on
filename with a checksum, one statement per file, and 4.2's runner refuses a changed
checksum. So amending `0001_daily_usage.sql` in place is refused by design; the change is a
new numbered statement.

## R8 — How many rows does the rollup hold today? **ZERO, AND ITS SOURCE IS THE REASON**

**Measured:**

    daily_usage       0 rows
    message_events    0 rows
    api_requests      11,683
    connection_events 154
    webhook_attempts  64

**The view is not broken.** Planting one row in `message_events` produced exactly one rollup
row, and the probe row was then removed from both the source and the inner table (verified: 0
and 0).

**The one table the rollup reads is the one table nothing writes.**

## R9 — Does `message_events` have a producer? **NO. IT HAS A LOADER**

**Measured** — every file in `relay-platform` mentioning `message_events`:

    scripts/scale/load-analytics.mjs      the batch loader
    analytics/0000_message_events.sql     the DDL
    analytics/0001_daily_usage.sql        the view
    analytics/0003_webhook_attempts.sql   a comment
    analytics/query.mjs                   the unwired demo script

**Occurrences under `services/`: zero.** By contrast every table with rows flows through
`services/ingester/src/clickhouse.ts` and `shape.ts` — the arms chapters 4.3, 4.4 and 4.5
built. `message_events` is filled by a script someone runs by hand against a corpus database,
which is also why 047's pass 9 found every one of its measurements to be about
`relay_corpus_<timestamp>` rather than the lane.

**This is the finding that reframes the chapter.** Two of FR-ANL-05's four quantities —
messages sent and unique active users — are derived from a table with no producer. So the
brief's *"billing never scans raw events"* is currently satisfied by a rollup over a table
that receives no events.

**Decision — stated here because it is the plan's spine**: chapter 4.6 does **not** build a
message-event producer. That is a send-path change on the busiest path in the platform, it
duplicates a counter Part 3 already maintains synchronously in `usage_periods`, and
`docs/12` §4 already argues why the synchronous counter has to stay. What the chapter does
instead is **name the gap as the thing DR-10's clause is actually resting on**, meter what
the store can honestly meter, and file the producer with its cost.

**Alternative considered**: a fourth arm on `route()` plus a send-path publisher, making the
rollup complete. Rejected for scope — it is a chapter, and by §3's table it is not this one.
Recorded as an open item rather than left implied.

## R10 — Does the read contract still need `sum()` and `GROUP BY`? **YES, UNCHANGED**

047 measured `SELECT messages` returning `1000 1000 1000` where the truth was 3000, because
`SummingMergeTree` holds one physical row per key per insert until a background merge. That
is a property of the engine, not of the corpus, and every rollup this chapter adds inherits
it. **The chapter shows the wrong read failing before it shows the right one passing**
(SC-005), because a query that is correct only after somebody runs `OPTIMIZE` is right in a
demo and wrong in production.

## R11 — What does the fence chain charge for `analytics/`? **FIVE FENCES, AND `0001` IS NOT ONE**

**Measured** across both locales:

    2   analytics/0000_message_events.sql
    2   analytics/0003_webhook_attempts.sql
    1   analytics/0005_connection_events.sql
    0   analytics/0001_daily_usage.sql
    0   analytics/apply.mjs

Every fenced `analytics/` file is a **whole body of a file its own chapter created**, which is
the cheapest class: a new file costs the chain nothing, because no earlier fence anchors on
it. 4.5 published `0005` exactly that way and closed at delta 0.

**`0001_daily_usage.sql` carries no titled fence in either locale.** So nothing in the chain
replays it, and whatever phase 2 decides about the shipped view — leave it or supersede it —
no hunk is owed for the file itself.

**This does not make the chapter free.** 4.5's first draft went 110 → 116 for six files it
edited that earlier chapters publish as whole bodies, and the exposure is a property of the
files touched, not of the directory. Phase 1 counts the list for every file this chapter
edits rather than carrying this one — 050's remembered list was wrong in both directions.

---

## Cleanup, verified

    DROP DATABASE r051_probe          -> gone (count()=0 in system.databases)
    probe row removed from message_events and from the view's inner table
    message_events 0 · daily_usage rows for the probe environment 0

## What the research changed

1. **R1** turned "extend the view" into "one target table, one view per source" — and **R7**
   then showed the shipped view cannot be extended that way without being recreated.
2. **R5** turned "derive connection-minutes from the records" into "derive them from closes
   and publish what that excludes", against a measured 44%.
3. **R9** turned the chapter from *"complete the rollup"* into *"the rollup's source has no
   producer, and saying so is the chapter"*.

**R3 did not change the design; it removed an excuse.** Both connection-minute definitions
are computable in a view, so Appendix C question 4 has to be decided rather than deferred for
want of a mechanism.
