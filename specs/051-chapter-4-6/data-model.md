# Data model — 051, chapter 4.6

## The rollup row

One row per `(environment_id, channel_id, day)`, summed. Every column is a count, a duration
or an identifier — constitution III's allow-list, *"only lengths, identifiers, and
metadata"*.

| Column | Type | Source | Producer? |
|---|---|---|---|
| `environment_id` | `UUID` | every source row carries it | — |
| `channel_id` | `UUID` | `message_events.channel_id` | R6: on the row |
| `day` | `Date` | `toDate(ts)` | — |
| `messages` | `UInt64` | `message_events` where `event='created'` | **no** |
| `active_users_state` | `AggregateFunction(uniq, Nullable(UUID))` | `message_events.user_id` | **no** |
| `stored_delta` | `Int64` | `+1` created, `-1` deleted, `0` edited | **no** |
| `connection_minutes` | `UInt64` | `connection_events` close rows | **yes, since 4.5** |

**`Int64`, not `UInt64`, for `stored_delta`.** R2 measured `SummingMergeTree` summing a
signed delta correctly (2 created − 1 deleted = 1). An unsigned column would wrap on a day
whose deletions exceed its creations, which is any day a tenant clears a backlog.

**`stored_delta` is a delta, not a balance.** The stored message count is the cumulative sum
of deltas up to and including a day — a stock computed from flows. DR-17 states the technique
for the media analogue: *"summing `media_events` deltas (uploaded/deleted)"*. A column holding
today's delta and a read reporting it as the stored count are two different answers, and the
contract says which is which.

**`active_users_state` is an aggregate state, not a number.** Written with `uniqState`, read
with `uniqMerge`. 047 measured that `uniqState`/`uniqMerge` ignore NULL exactly as `uniqExact`
does, so the `Nullable(UUID)` that 046 fixed survives into the rollup — a deleted author's
messages do not become one phantom user per environment.

**`uniq` is approximate.** Exact to roughly 60,000–65,000 distinct, off by 0.51% at 70,000.
Any distinct-user figure this chapter publishes states the corpus cardinality beside it, and
047-1 is the record of why that matters against FR-ANL-06's 0.1%.

## The views that feed it

A materialised view fires on inserts to one source table. R1 measured two views over two
sources writing into one `TO` target and summing correctly (1 + 100 = 101), which is the only
shape in which a tenant-day is one row.

| View | Source | Writes |
|---|---|---|
| messages | `message_events` | `messages`, `active_users_state`, `stored_delta` |
| connection minutes | `connection_events` | `connection_minutes` |

Each view writes its own columns and leaves the others at their type's zero, which
`SummingMergeTree` then adds. A row from one view and a row from the other merge into the
tenant-day.

**The connection view reads close rows only.** R4 measured that a close carries the closing
instant and the elapsed duration, so `ts - duration_ms` recovers the open and the open record
is not needed. R5 measured that **55 of 99 connections in the store have both records and 44
have only one** — so an open with no close contributes nothing, and the count of those is
published beside the minutes rather than hidden inside them.

## The two connection-minute quantities

Both are computable in a view; R3 measured the harder one working.

| Definition | Expression | A 2-second connection crossing a boundary |
|---|---|---|
| calendar buckets | `arrayJoin` over the minute range | **2** |
| elapsed duration | `sum(duration_ms)` | **0.03** |

The first reproduces `meter.ts`'s documented rule — *"Open at 00:00:59 and closed at 00:01:01
is two seconds of wall clock and TWO connection-minutes"* — and charges reconnect churn. The
second is what a connection record literally contains. **SRS Appendix C question 4 asks which
one bills and is still open.** Phase 6 answers it; until then neither is the default.

The calendar expansion assigns each minute its own `toDate`, so a connection spanning midnight
splits across two days without special handling.

## What is unchanged

**`usage_periods (environment_id, period, messages_sent)`** in Postgres, and 0014's
connection-minute buckets. The quota counter is maintained synchronously on the send path
because a quota refuses a send synchronously, which `docs/12` §4 argues and this chapter
cites. Nothing here replaces it, and phase 8 shows it unchanged by diff.

## State and lifecycle

- **No TTL on the rollup**, matching FR-003a's reasoning for `daily_usage`: `message_events`
  expires at 90 days and metering must not lose history when raw events do. 048-4 carries the
  consequence — the rollup grows at `environments × channels × days` forever and no clause
  says how long metering history is kept — and this chapter adds a dimension to that product,
  so it re-measures the item rather than inheriting the sentence.
- **A day with no inserts produces no row.** An MV emits nothing for a group that had no
  input, so "no activity" is a missing row and can never be a row of zeros. FR-004's
  distinction therefore lives in the read, not in the table.
- **One physical row per key per insert until a merge.** R10: the read contract is `sum()`
  with `GROUP BY`, and a read that is correct only after `OPTIMIZE` is shown failing first.
