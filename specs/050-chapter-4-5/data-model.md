# Data model — chapter 4.5

**Feature**: `specs/050-chapter-4-5/` · **Date**: 2026-09-14

Two record types, one table, and one quantity that is computed two ways on purpose.

---

## 1. `relay_analytics.connection_events`

```sql
CREATE TABLE IF NOT EXISTS relay_analytics.connection_events (
    environment_id UUID,
    ts             DateTime64(3, 'UTC'),
    connection_id  UUID,
    event          LowCardinality(String),
    -- Only on a close. Absent on an open, and `LowCardinality(Nullable(...))` because
    -- 4.4 measured that `LowCardinality(String)` cannot hold the difference between an
    -- absent field and an explicit empty one -- both land as ''.
    close_code     LowCardinality(Nullable(String)),
    duration_ms    Nullable(UInt32),
    user_external_id Nullable(String),
    CONSTRAINT ts_is_real CHECK ts > toDateTime64('2020-01-01 00:00:00', 3, 'UTC')
)
ENGINE = ReplacingMergeTree
PARTITION BY toYYYYMM(ts)
ORDER BY (environment_id, ts, connection_id, event)
TTL toDateTime(ts) + INTERVAL 90 DAY
```

**`environment_id` is NOT nullable here, unlike `api_requests`.** That is the difference
between the two chapters and it is worth stating rather than inheriting: a request can be
made by nobody, but a *connection* that has an event has completed a handshake, and a
handshake produces an identity. R5 leaves one case open — a socket that never authenticates —
and phase 1 decides whether it has an event at all rather than whether it has a tenant.

**`event` in the sorting key, after `connection_id`.** One connection produces two rows with
the same `connection_id`, so without it a `ReplacingMergeTree` would collapse the open into
the close. That is the 4.3 lesson applied rather than re-learned: idempotence is the record's
own key, and the record's own key here includes which event it is.

**Every other line carries a measurement from a previous chapter**: `toDateTime(ts)` because
047 measured `TTL ts + INTERVAL` refused on a `DateTime64`; `ts_is_real` because 048 measured
an absent column taking a default older than any TTL; `Nullable` on the close-only columns
because 4.4 measured `LowCardinality(String)` flattening absent into empty.

**90 days, not 30.** `api_requests` is 30 because FR-ANL-07 says so. Nothing says so here, and
FR-ANL-05's metering window is the calendar month — so 90 matches `webhook_attempts` and the
chapter states that it is a default rather than a derivation.

---

## 2. The two records

| field | open | close |
|---|---|---|
| `event` | `"opened"` | `"closed"` |
| `connection_id` | yes | yes, the same |
| `environment_id` | yes | yes |
| `ts` | when the handshake completed | when the socket closed |
| `close_code` | absent | the WebSocket close code |
| `duration_ms` | absent | close `ts` − open `ts` |
| `user_external_id` | yes | yes |

**No credential, no token, no message content, no channel list.** The allow-list is built by
naming every field, as 3.20's shaper and 4.4's both are.

**`close_code` is a code and not a reason.** `CLOSE_CODES` is a published registry that
`check:errors` compares in both directions, so the vocabulary is already guarded. A reason
string is a sentence somebody writes.

---

## 3. The quantity computed twice

`meter.ts` reports **minute buckets touched**: a connection open at 00:00:59 and closed at
00:01:01 owes **two** connection-minutes. The records above give **elapsed duration**: 2,000 ms.

These are not the same quantity and no amount of care makes them agree. What FR-009 compares is
one quantity computed two ways:

    buckets derived from (open ts, close ts)   ==   buckets the meter reported

Both count calendar minutes touched; one derives them from the records and one from the
gateway's own tick. A disagreement there is a defect. A disagreement between *duration* and
*buckets* is arithmetic, and the chapter publishes it as a number so nobody reads it as one.

**This is 4.2's boundary day one domain over.** There a daily rollup and a timestamp TTL
disagreed on the oldest day by 4,941 and always would; here a wall-clock bucket and an elapsed
duration disagree by up to a minute per connection, and always will.

---

## 4. Entities and their relationships

| entity | holds | reaches a tenant |
|---|---|---|
| **Connection opened** | connection id, environment, user, the instant | directly |
| **Connection closed** | the same identity, the instant, duration, close code | directly |
| **The meter's report** | connection id, environment, period, minutes — unchanged | directly |
| **`connection_events` row** | either record, until the TTL removes it | through `environment_id` |

No join, no foreign key. The analytical store does not reference the operational one
(constitution III), and `environment_id` is on the row.
