# Phase 1 — Data model: Chapter 3.11, Counting a connection

Three changes to what chapter 3.10 built, and one new table. Migration
`0010_connection_minutes.sql`.

---

## Quota policy — `environments.quota_config`, a third key

The jsonb column gains `connection_minutes` beside the two dimensions chapter
3.10 put there:

```json
{ "messages":           { "hard": 10000, "soft": 8000 },
  "active_users":       { "hard": null,  "soft": 500  },
  "connection_minutes": { "hard": 50000, "soft": 40000 } }
```

The rules are chapter 3.10's, unchanged and restated because they are what
FR-013 and FR-014 require: **absent and null both mean no cap; zero means refuse
everything.** `#>> '{connection_minutes,hard}'` returns SQL NULL for an absent
key and for a JSON null alike, and the string `'0'` for zero.

`environments_quota_config_shape` is the CHECK that enumerates dimensions, and
chapter 3.10 said out loud that a third one would cost a change here. What it
costs, exactly: one `jsonb_typeof` clause and two regex clauses, mirroring what
is already written for each of the other two. The constraint is dropped and
recreated — Postgres has no `ALTER CONSTRAINT` for a CHECK expression.

`quotaConfigSchema` in `quotas/config.ts` is `.strict()`, so the key has to be
added there in the same change or a configured `connection_minutes` becomes a
parse failure and `capsFor` fails closed to no caps at all. Two places, one
change, and the second one fails quietly rather than loudly — which is why they
belong in one task.

---

## `usage_periods` — a third figure

```sql
ALTER TABLE usage_periods
  ADD COLUMN connection_minutes bigint NOT NULL DEFAULT 0,
  ADD CONSTRAINT usage_periods_connection_minutes_non_negative
    CHECK (connection_minutes >= 0);
```

`bigint`, `{ mode: "number" }` on the Drizzle side, for the reason chapter 3.10
gave for `messages_sent`: it is a cumulative count and an overflow here is a
wrong bill rather than a wrapped counter. Concretely, a tenant holding ten
thousand sockets continuously accrues 5.26 billion connection-minutes a year, and
`integer` tops out at 2,147,483,647 — about five months in.

Same primary key, same period semantics, same `periodOf`. A row already exists
for any environment that has sent a message this period; the metering path
upserts one for an environment that has only ever connected.

---

## `usage_connections` — the state that makes a repeated report free

```sql
CREATE TABLE usage_connections (
  connection_id  uuid        NOT NULL,
  period         date        NOT NULL,
  environment_id uuid        NOT NULL REFERENCES environments(id),
  minutes        bigint      NOT NULL DEFAULT 0,
  first_seen_at  timestamptz NOT NULL DEFAULT now(),
  last_seen_at   timestamptz NOT NULL DEFAULT now(),
  PRIMARY KEY (connection_id, period),
  CONSTRAINT usage_connections_minutes_non_negative CHECK (minutes >= 0)
);

CREATE INDEX usage_connections_by_environment
  ON usage_connections (environment_id, period);
```

**One row per connection per period, and that is the whole idempotency
mechanism.** A report says a connection has occupied N minute-buckets in a
period. The api credits `max(0, N − minutes)` to `usage_periods` and sets
`minutes = greatest(N, minutes)`. A replayed report credits zero. A lost report
is invisible: the next one carries the same total plus what has accrued since.
A report that arrives out of order credits nothing and lowers nothing.

**Why not one row per minute.** That is the naive dedup key, and at a thousand
concurrent sockets it is 43.2 million rows a month (research R4). FR-010 forbids
storage proportional to elapsed time. This table is proportional to distinct
connections instead — chapter 3.10 made the same trade for distinct users and
bounded it by users rather than by traffic.

**`connection_id` alone would be unique** — it is a `randomUUID()` minted by the
gateway in `session.ts` — but `period` is in the key because a connection open
across a month boundary owes minutes to two periods and each is credited
independently (FR-009).

**A connection may not change environment.** `environment_id` is written by the
first report and never updated. A later report naming a different environment
for the same `connection_id` is refused rather than reconciled: a connection
moving tenants is either a bug or an attempt, and constitution I makes it a
correctness question rather than a data-quality one.

**The lock that works here.** Crediting the delta is read-then-write, and it
takes `SELECT … FOR UPDATE` on the accounting row. Chapter 3.10 wanted the same
lock on the usage row and could not have it — `FOR UPDATE cannot be applied to
the nullable side of an outer join`, because caps and usage had become one
joined read. Here the lock is a single table by primary key and Postgres allows
it. The same instinct, in the one place it is permitted.

**Nothing prunes this table.** Rows accumulate at roughly the tenant's distinct
connections per period: a tenant whose sockets turn over hourly across a
thousand concurrent clients leaves about 720,000 rows a month. Deleting a
finished period is a global operation over an environment-scoped table and is
the only sweep this chapter could have contained. Out of scope, stated here
rather than discovered by whoever opens the table first (research R9).

---

## `quota_notifications` — a third dimension in an existing column

```sql
ALTER TABLE quota_notifications
  DROP CONSTRAINT quota_notifications_dimension_check,
  ADD CONSTRAINT quota_notifications_dimension_check
    CHECK (dimension IN ('messages', 'active_users', 'connection_minutes'));
```

No new table. Chapter 3.10 said "four concrete tables that look alike is a
pattern, one abstract table serving four purposes is a framework", and a third
dimension in the fourth table is neither — it is a new value in a column that
already exists. `quota_notifications_once_per_threshold` already keys on
`(environment_id, period, dimension, threshold)`, so at-most-one-email-per-
threshold holds for the new dimension without a line of code.

---

## Relationships

```
environments ─┬─ 1:1 quota_config (jsonb, three dimensions)
              ├─ 1:N usage_periods        (environment_id, period)
              │        messages_sent, connection_minutes
              ├─ 1:N usage_active_users   (environment_id, period, user_id)
              ├─ 1:N usage_connections    (connection_id, period)   ← new
              └─ 1:N quota_notifications  (…, dimension, threshold)

usage_connections.minutes  ──summed into──▶  usage_periods.connection_minutes
                              (by delta, at report time, one transaction)
```

The arrow is a **derivation that is maintained, not computed**. Recomputing it
would scan the tenant's connections for the month, which is research R4's
rejected shape wearing chapter 3.10's R1 costume.

---

## State transitions

A connection's accounting row:

```
   (no row)
      │  first report for (connection, period)
      ▼
   minutes = N ──── report with N' > N ────▶ minutes = N'   (credit N' − N)
      │                                          │
      │◀─── report with N' ≤ N ──────────────────┘   (credit 0, no update)
      │
      └─── gateway dies ───▶ minutes stays where it is, for ever
```

There is no closed state and no terminal transition. A connection that ends
cleanly simply stops being reported, and a connection whose gateway died stops
being reported in exactly the same way. **The api cannot tell the two apart, and
does not need to** — which is why there is no reaper, no orphan sweep, and no
"connection still open?" question anywhere in the design.

---

## What the guard sees

Nothing. Feature 030's triggers cover five tables — `webhook_endpoints`,
`webhook_deliveries`, `webhook_disable_notifications`, `channels`, `users` — and
`usage_connections` joins `usage_periods`, `usage_active_users` and
`quota_notifications` as an environment-scoped table the guard does not watch.

That is a **stated gap, not a claim of safety** (research R5a). Chapter 3.10's
SC-008 read "no new file is added to the exemption list" and passed, which was
true and quieter than it sounded. Extending the guard is also not the one-line
array change it looks like: the refusal message interpolates `OLD.id`, and
`usage_periods` has no `id` column, so the trigger would raise `record "old" has
no field "id"` on the first legitimate update.
