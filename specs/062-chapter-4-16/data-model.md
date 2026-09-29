# Data model — Chapter 4.16

## 1. `relay_analytics.media_events`

The event DR-17 names. Modelled on `connection_events`, which is the closest existing shape: a
signed fact about one object at one moment.

| column | type | meaning |
|---|---|---|
| `environment_id` | `UUID` | the tenant. Every read is scoped by it |
| `media_id` | `UUID` | the object. Present so a reconciliation can name what disagrees |
| `event` | `LowCardinality(String)` | `reserved`, `rejected`, `rendition`, `deleted` |
| `kind` | `LowCardinality(String)` | image / audio / video, for FR-009's counts |
| `bytes_delta` | `Int64` | signed. The quota's quantity, not the store's |
| `occurred_at` | `DateTime64(3)` | when it became true, not when it was ingested |

**`bytes_delta` IS SIGNED AND THE EVENT NAME DOES NOT IMPLY ITS SIGN.** `reserved` and
`rendition` are positive, `rejected` and `deleted` negative — but the sign is carried, not
derived, because a reader that infers it from the name is a second place the rule lives. This
is `stored_delta`'s own lesson from the other direction: that column derives its sign from
`multiIf(event = 'created', 1, …)` and its name has since misled a planner into thinking it
counted bytes.

**`LowCardinality(String)` CANNOT SAY "ABSENT" (4.4's finding).** An absent field and an
explicit `""` both land as `''`, and none of the ingester's guards catches an absent one. Both
`event` and `kind` are required in the schema for that reason.

**90-DAY TTL ON THE EVENTS, matching `message_events` and DR-09.** 4.2 measured that the TTL
cuts at INSERT rather than at merge, so a count taken the moment a load finishes shrinks
overnight on its own.

**AND THE ROLLUP'S TTL IS 25 MONTHS, NOT ABSENT — WHICH BOUNDS THE LEVEL.** The first draft of
this paragraph said the rollup carries none, copying `0010`'s comment. **`0014` had already
corrected that comment**: *"'No TTL' was never what FR-003a asked for — only 'not the raw
table's TTL'."* Measured on the running store:

    daily_usage_billing   TTL toDateTime(day) + toIntervalMonth(25)
    daily_usage_v2        TTL toDateTime(day) + toIntervalMonth(25)
    message_events        TTL toDateTime(ts)  + toIntervalDay(90)

**A level summed from deltas does not survive that.** The level is
`sum(stored_bytes_delta) WHERE day <= asOf`, accumulated from the beginning of time, so once
the TTL removes the earliest days the level is **understated by exactly what they summed to**,
permanently and with nothing in the system able to notice. A count of stored messages has the
same defect and nobody has met it, because `message_events` has no producer; this chapter would
ship the first live instance.

**What makes the horizon survivable is DR-17's other half.** The object store holds the level
directly, so the reconciliation can re-base a truncated sum from the inventory. That is the
third reason the rollup and the reconciliation are one feature: the first is that a summed
level is not self-correcting (R5), the second is that a lost event is permanent, and the third
is that the retention boundary makes a re-base **necessary** rather than merely prudent.

## 2. `daily_usage_billing`, extended

Two columns at the existing `(environment_id, day)` key. **The row count does not move**, which
is what separates this from 4.6's channel-keyed rollup.

| column | type | meaning |
|---|---|---|
| `stored_bytes_delta` | `Int64` | the day's net byte change. Accumulate for a level |
| `uploads_by_kind` | `SimpleAggregateFunction(sumMap, Map(String, UInt64))` | FR-009's counts |

**IT IS NOT CALLED `stored_delta` AND THAT IS THE POINT.** The existing `stored_delta` is
`sum(multiIf(event = 'created', 1, event = 'deleted', -1, 0))` over `message_events` — a net
count of stored **messages**. The premise check found this by reading the view rather than the
name, and a column called `stored_bytes` beside it would read as the same thing measured
differently.

**A MAP RATHER THAN ONE COLUMN PER KIND — AND THE OBVIOUS MAP TYPE DOES NOT WORK.**
Three kinds exist and `ALLOWED_TYPES` decides them; a column each would make a fourth kind a
migration, which is the reason to want a map.

The first version of this table wrote `Map(LowCardinality(String), UInt64)` and this paragraph
asserted that `SummingMergeTree` sums it by key. **It does not.** Measured against ClickHouse
25.3.14.14, two rows at one key:

    inserted   map('image',2,'audio',1)   and   map('image',3,'video',5)
    merged     {'image':2,'audio':1}            <- the FIRST row wins
    an Int64 column beside it                    summed correctly, 1 + 1 = 2

`image` is not summed and `video` is gone. Plain `String` keys fail identically, so
`LowCardinality` is not the cause, and three plain `UInt64` columns give `5 1 5`.

**`SimpleAggregateFunction(sumMap, …)` is the type that merges**, measured the same way:
`{'audio':1,'image':5,'video':5}`. It keeps the map's advantage — a fourth kind is an insert
rather than a migration — and costs a declaration a reader has to know to write.

**The key is plain `String`, not `LowCardinality`**, because that is the combination that was
measured. Whether `LowCardinality` survives inside `SimpleAggregateFunction` here is untested,
and guessing is how this paragraph was wrong the first time.

## 3. The third materialised view

`0018_mv_billing_storage` writes `media_events` → `daily_usage_billing`, alongside the two
that already do this from `message_events` and `connection_events`.

**A MATERIALISED VIEW IS A TRIGGER ON FUTURE INSERTS (4.6).** It computes nothing about rows
already in the table, so a deployment applying this to a store with history needs a backfill —
and here there is no history, because `media_events` is new. The chapter states this rather
than discovering it: **this rollup starts correct precisely because its source starts empty**,
which is the one circumstance 4.6's finding does not bite.

## 4. What is read, and by whom

| reader | question | shape |
|---|---|---|
| `storedBytes(store, env, asOf)` | the level on a day | `sum(stored_bytes_delta) WHERE environment_id = ? AND day <= ?` |
| a chart | the series | one row per day, no accumulation |
| `storage-reconcile` | does the level match the store | the level, against the inventory |
| the quota | the level **now** | **unchanged — Postgres.** Not this table |

**THE QUOTA DOES NOT MOVE, AND THAT IS A DECISION.** It reads `sum(declared_bytes)` in the
operational store, which costs 252 buffers for the lane's busiest tenant. Pointing it at the
rollup would make a request path depend on the analytical store, which constitution III
forbids and which would turn an outage into a refused upload. The rollup is history; the quota
is a level; DR-17's reconciliation is what stops them drifting silently.

## 5. State

None added. `media_objects`' three states are unchanged. The events record transitions that
already exist rather than introducing new ones — which is why every emission point hangs off a
compare-and-set that is already there (R7).
