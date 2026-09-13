# Contract — the analytical schema

**This is what movement II's ingester will be written against**, which is the only reason it is
a contract and not a file. A schema with no writer is a reader with no writer, and this project
has met that twice in three chapters — `message_edits` published in the SAD and unbuilt since
the first draft, `messages.attachments` a column whose only writer set it to null.

The ingester is two chapters away. **Every column below either has a producer named or is
marked as having none**, so that chapter inherits a schedule rather than a surprise.

## Applying it

```
RELAY_POSTGRES_PORT=15432 node scripts/scale/../../analytics/apply.mjs
```

Reads `analytics/*.sql` in filename order, applies what the ledger does not record, and prints
what it applied. **A second run applies nothing and says so.** That is the half
`CREATE … IF NOT EXISTS` cannot give: it is idempotent and silent about whether it did anything.

| behaviour | |
|---|---|
| **Idempotence** | Each file applies once, keyed on filename in `schema_applied`. |
| **Reporting** | Every run prints the files it applied and the files it skipped. **A run that applies nothing prints that it applied nothing** — a zero that proves it looked. |
| **Checksums** | The ledger stores each file's checksum. An edited file that has already been applied is **reported as changed and refused**, not silently skipped: ClickHouse has no `ALTER` path for most of what these files do, and a schema the ledger claims is applied but is not is worse than one that has not been applied. |
| **Isolation** | It writes to ClickHouse only. It does not touch `schema_migrations`, the Postgres runner, or any operational table (FR-012). |
| **Ordering** | Filename order. `0001_daily_usage.sql` reads `message_events`, so `0000` must have run — the materialised view creation fails with `UNKNOWN_TABLE` otherwise, which was checked. |

## The statements

| file | creates | source |
|---|---|---|
| `0000_message_events.sql` | the raw event table | SAD §6.2, with `toDateTime(ts)` in the TTL |
| `0001_daily_usage.sql` | the daily rollup | SAD §6.2, verbatim |
| `0002_schema_applied.sql` | the ledger | this chapter's |

**`0002` is applied before `0000` by the script's own bootstrap**, because a ledger cannot
record its own creation from a table that does not exist. The script creates it unconditionally
with `IF NOT EXISTS` and records everything after it.

## Column producers, stated

| column | source expression | when |
|---|---|---|
| `environment_id`, `channel_id`, `ts` | `channels.environment_id`, `messages.channel_id`, `messages.created_at` | this chapter, then movement II |
| **`user_id`** | `messages.user_id` into a **`Nullable(UUID)`** column | this chapter |
| **`event`** | **three rows per message** — `created` at `created_at`, `edited` at `edited_at`, `deleted` at `deleted_at` | this chapter |
| `text_length` | **`lengthUTF8(text)`** into a **`Nullable(UInt32)`** — code points, not bytes | this chapter |
| `attachment_count` | **`JSONLength(attachments)`** into a **`Nullable(UInt8)`** — the jsonb arrives as a String | this chapter |
| **`delivery_latency_ms`** | **NONE** | FR-ANL-10, a later chapter |

**Five of those were wrong across two analysis passes**, and the last three were found by
asking pass 1's own question of the columns pass 1 did not ask it about.

**Three of those expressions were wrong in this contract's first version**, and every one was
wrong in the same way: the column name implied a type the data does not arrive as.
`postgresql()` delivers jsonb as `Nullable(String)`, so `length(attachments)` returned **151**
for a two-attachment row; `length(text)` is **bytes** where FR-EMJ-02 counts code points; and
`messages.user_id` is `Nullable(UUID)`, which SAD §6.2's non-nullable column converts to the
**zero UUID** without failing. See `data-model.md` §1 for the measurements.

## What the ingester may assume, and what it may not

**May assume**: the ordering is `(environment_id, ts)` and the partition is monthly, so a
tenant-scoped range query skips parts — measured at **4 of 12 parts and 49 of 147 granules**
with one environment of three named. It may assume the rollup is maintained on insert and
needs no refresh.

**May not assume**: that a row it inserts will still be there. **The TTL removes rows at
insert time, not at merge** — 120,000 rows spanning 120 days became 90,000 immediately, with
no error and no report. An ingester replaying a backlog older than 90 days will write rows
that vanish, and nothing will tell it.

**MUST read the rollup with `sum()` and `GROUP BY`, never a bare column.** It holds one row per
INSERT per `(environment_id, day)` until a background merge collapses them — three inserts on
one day measured **three rows**, and `SELECT messages` returned `1000 1000 1000` where the truth
was 3000. `OPTIMIZE … FINAL` collapses them, and **a query whose correctness depends on somebody
having run that is right in a demo and wrong in production.** Mixing the state column with a
bare one is refused (`NOT_AN_AGGREGATE`); leaving the state out is what goes quietly wrong.

**MUST NOT assume one row per message.** The `event` column is `created|edited|deleted` and
this table holds **one row per event** — 303,885 creations, 3,201 edits and 4,056 deletions from
the lane's 303,885 messages, 311,142 rows. `daily_usage` filters `WHERE event = 'created'`, so
an ingester that labels everything `created` inflates FR-ANL-05's *messages sent* by every
deletion.

**MUST NOT assume `text_length` is always known.** It is `Nullable(UInt32)`, and **3,282 rows
in this corpus carry NULL** — tombstoned messages whose original length is unrecoverable,
because chapter 3.23 preserves no prior text for a deletion. **Those NULLs are an artefact of
reconstructing an event log from current state.** An ingester sees the send and writes a length
every time; if it ever writes NULL, something upstream lost the event.

**May not assume a NULL sender survives as a NULL.** `message_events.user_id` is
`Nullable(UUID)` **because SAD §6.2's `UUID` silently becomes the zero UUID** for every message
whose author was deleted (FR-USR-05). An ingester writing into a non-nullable column would give
each environment one phantom active user and no error. `uniqState` ignores NULLs, which is what
Postgres's `count(DISTINCT user_id)` does — that agreement is the point.

**May not assume the rollup is exact.** `uniq` is exact to 60,000 distinct values and off by
**0.51%** at 70,000. FR-ANL-06's reconciliation bound is 0.1%. The two cannot both hold above
roughly 65,000 distinct senders in a period, and DR-10 forbids the reconciliation from reading
raw events instead. **That conflict is filed for movement IV**, unresolved here.

## The stability this promises

Movement II may need columns this schema does not have, a second table, or a different engine
for one of them. **If it does, the finding is that this contract was written by one caller** —
045's deferral lesson one level down, and 046's contract said the same thing and was right to.
