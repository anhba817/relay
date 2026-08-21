# Chapter 3.10 — data model

Four schema changes in one migration, `0009_quotas.sql`.

## Quota policy — columns on `environments`

Beside chapter 3.8's three limit columns, and for the same reasons: FR-RTL-04's
independence is per environment, there is exactly one row per environment with no
history, and a separate table would be a join for a value read on every request.

| Column | Type | Null | Meaning |
|---|---|---|---|
| `message_quota` | `integer` | yes | Hard cap on messages this period. Null: unlimited. |
| `message_quota_soft` | `integer` | yes | Soft threshold. Alerts, refuses nothing. |
| `active_user_quota` | `integer` | yes | Hard cap on distinct senders this period. |
| `active_user_quota_soft` | `integer` | yes | Soft threshold for the same. |

**`message_quota` IS the hard cap.** The spec says "hard cap" and "soft threshold";
the columns say `message_quota` and `message_quota_soft`. Two names for one thing,
and the reason is that "quota" is the feature's name in prose and the cap's name in
the schema. Named here once so a reader does not go looking for a separate
`message_cap` column that does not exist.

**Null is not zero**, the rule chapter 3.8's columns established. Null means no
cap; zero means refuse everything, and an environment can be switched off
deliberately, so the two cannot share a representation (FR-006).

Constraints: each column `IS NULL OR >= 0`. A soft threshold above its hard cap is
permitted and means the soft alert never fires before the hard one — a
configuration the operator can express, not an error the schema should invent an
opinion about.

## `usage_periods` — the roll-up

| Column | Type | Null | Meaning |
|---|---|---|---|
| `environment_id` | `uuid` | no | FK to `environments`. Part of the key. |
| `period` | `date` | no | First day of the calendar month, UTC. Part of the key. |
| `messages_sent` | `bigint` | no | Default 0. Increments in the send transaction. |
| `created_at` | `timestamptz` | no | Default `now()`. |

Primary key `(environment_id, period)`. The period is **stored, not computed**, so
a lookup is the whole key rather than a predicate over a range, and a month
boundary is a different row rather than a different filter (R7).

`bigint` rather than `integer` because this is a cumulative count on the hot path
and an overflow would be a wrong bill — declared
`bigint("messages_sent", { mode: "number" })`, the mode the project's two existing
bigints use (`channels.last_sequence`, `messages.sequence`). Drizzle requires one.

**`date` WOULD BE THIS PROJECT'S FIRST.** `schema.ts` declares 28 `timestamp(`,
12 `integer(`, 2 `bigint(` and no `date(` at all, so drizzle's mode for it —
string or `Date` — is unsettled here. That matters more than it looks: `period` is
a **primary key component** on this table and on `usage_active_users`, so a
writer and a reader disagreeing about the mode is a row that cannot be found
rather than a compile error. T011a chooses it and round-trips it before anything
depends on it.

The previous month's row is never deleted, which is all FR-003's "remains
readable" requires.

## `usage_active_users` — the membership

| Column | Type | Null | Meaning |
|---|---|---|---|
| `environment_id` | `uuid` | no | Part of the key. |
| `period` | `date` | no | Part of the key. |
| `user_id` | `uuid` | no | Part of the key. FK to `users`. |
| `first_seen_at` | `timestamptz` | no | Default `now()`. |

Primary key `(environment_id, period, user_id)`. Written
`INSERT … ON CONFLICT DO NOTHING` on every attributed send; the count is an
index-only scan over the key prefix.

Bounded by the tenant's distinct users per month, not by their traffic — which is
the property that makes it affordable and the reason it is a table rather than a
counter (R2).

**A send with no `user_id` writes no row.** A key-authenticated REST send is
unattributed by design, from chapter 3.3, and an unattributed send is a message
that counts toward the message quota and toward no user.

## `quota_notifications` — the outbox, a fourth time

| Column | Type | Null | Meaning |
|---|---|---|---|
| `id` | `uuid` | no | Primary key. |
| `environment_id` | `uuid` | no | FK. Who crossed. |
| `organisation_id` | `uuid` | no | FK. Who gets told. |
| `period` | `date` | no | Which period's crossing. |
| `dimension` | `text` | no | `messages` or `active_users`. Checked. |
| `threshold` | `integer` | no | 50, 80 or 100. Checked. |
| `quota` | `bigint` | no | The figure the percentage is of, as it stood. |
| `usage_at_crossing` | `bigint` | no | What tripped it. |
| `crossed_at` | `timestamptz` | no | Default `now()`. |
| `delivered_at` | `timestamptz` | **yes** | Null until sent. The claim predicate. |
| `last_error` | `text` | yes | Why the last attempt failed. |

Unique on `(environment_id, period, dimension, threshold)`. That constraint **is**
FR-015 — at most one email per threshold per quota per period — enforced by the
schema rather than by the code that writes it, so a concurrent double-crossing
resolves to one row rather than to two emails.

`quota` and `usage_at_crossing` are stored rather than looked up at send time
because the cap can change between crossing and delivery, and an email that says
"you have used 80% of 10,000" should mean the 10,000 that was true when it
happened.

## Relationships

```
environments 1───n usage_periods          (environment_id, period)
environments 1───n usage_active_users     (environment_id, period, user_id)
environments 1───n quota_notifications
users        1───n usage_active_users
organisations 1───n quota_notifications
```

## State transitions

**A usage period** has one: absent → present. It is created by the first send of
the month (`INSERT … ON CONFLICT DO UPDATE SET messages_sent = … + 1`) and never
deleted or decremented. There is no "closed" state; the month simply stops being
the current one.

**A quota notification** has two: written (`delivered_at` null) → delivered
(`delivered_at` set), or written → failed-and-still-claimable (`last_error` set,
`delivered_at` still null), which is chapter 3.9's shape exactly. A row with no
addressable recipient is marked delivered with the failure logged, because leaving
it claimable means reclaiming an undeliverable row for ever (FR-018).

## What the guard sees

Every table here carries `environment_id`, so feature 030's trigger would guard
them if they were added to `sentinel.sql`'s list. **They are not, and should not
be**: nothing in this design performs a cross-environment mutation, so there is no
sentinel row for a quota to damage. R11 schedules a run against a baited database
to find out whether that prediction is wrong.
