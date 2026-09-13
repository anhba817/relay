# Contract — the analytical schema

**This is what movement II's ingester will be written against**, which is the only reason it is
a contract and not a file. A schema with no writer is a reader with no writer, and this project
has met that twice in three chapters — `message_edits` published in the SAD and unbuilt since
the first draft, `messages.attachments` a column whose only writer set it to null.

The ingester is two chapters away. **Every column below either has a producer named or is
marked as having none**, so that chapter inherits a schedule rather than a surprise.

## Applying it

```
node analytics/apply.mjs            # from relay-platform/
node analytics/apply.mjs --drop-all
```

Reads `analytics/*.sql` in filename order, applies what the ledger does not record, and prints
what it applied. **A second run applies nothing and says so.** That is the half
`CREATE … IF NOT EXISTS` cannot give: it is idempotent and silent about whether it did anything.

**The transport is Node's own `fetch` against the HTTP interface**, and that is what makes the
zero-dependency claim true rather than lucky — no `@clickhouse/client`, no driver, nothing in
the lockfile. Verified: a single statement carrying SQL comments posts `200 OK`, with or without
a trailing semicolon.

**The first version of this line read `RELAY_POSTGRES_PORT=15432 node
scripts/scale/../../analytics/apply.mjs`** — a Postgres variable on a script that never touches
Postgres, and a path traversal for a file two directories up. The quickstart wrote it plainly
and the two disagreed. **046's contract carried the identical defect and it took six analysis
passes to open the file.**

### One statement per file, and the script refuses more

The HTTP interface **rejects a multi-statement body**:

    Code: 62. DB::Exception: Syntax error (Multi-statements are not allowed)

So `analytics/*.sql` is a directory of **statements**, not of files that happen to contain some.
`apply.mjs` refuses a file holding more than one rather than discovering it mid-run — and the
ledger keyed on filename only means something if a filename is one change.

### The statements carry their own address

**The database is `relay_analytics`, and every statement names it.** Not because qualified
names read better — because the unqualified form has a wrong answer that looks like a right one:

    CLICKHOUSE_DB=relay_analytics          -> the database is created at first start
    SELECT currentDatabase()  (HTTP, relay) -> default
    CREATE TABLE message_events …           -> lands in `default`, no error

**`CLICKHOUSE_DB` creates a database and does not make it the session's.** So SAD §6.2's DDL,
posted exactly as published, builds the analytical schema in `default` while the database compose
provisioned sits empty beside it — and every later statement, every query and every cleanup
agrees with itself about the wrong place. `?database=relay_analytics` on the URL also works
(verified), and it is the weaker fix: it lives in the connection, so a statement pasted into
`clickhouse-client` — which is how a reader of this chapter will run one — goes back to landing
in `default`.

**`apply.mjs` refuses a statement that does not name the database**, in the same family as the
one-statement rule below. A file without an address is refused rather than applied somewhere
else: **the failure that was found here cannot arise rather than being handled.**

| behaviour | |
|---|---|
| **Idempotence** | Each file applies once, keyed on filename in `schema_applied`. |
| **Reporting** | Every run prints the files it applied and the files it skipped. **A run that applies nothing prints that it applied nothing** — a zero that proves it looked. |
| **Checksums** | The ledger stores each file's checksum. An edited file that has already been applied is **reported as changed and refused**, not silently skipped: ClickHouse has no `ALTER` path for most of what these files do, and a schema the ledger claims is applied but is not is worse than one that has not been applied. |
| **Isolation** | It writes to ClickHouse only. It does not touch `schema_migrations`, the Postgres runner, or any operational table (FR-012). |
| **`--drop-all`** | **`DROP DATABASE IF EXISTS relay_analytics`** — one named database, not a table-by-table sweep, and **not an unqualified `DROP DATABASE`**: dropping the provisioned database while the tables are in `default` returns no error and removes nothing, and dropping `default` leaves the server answering `SELECT 1` while every unqualified statement fails `Code: 81 … UNKNOWN_DATABASE`. **Both directions of the unnamed version are wrong and neither reports anything.** It does not re-create: the bootstrap does that on the next run, and `system.tables` reports **0** for an absent database rather than erroring, so the after-check stays honest. **Dropping the source table under a live materialised view succeeds with no error** and leaves the view behind, still queryable and returning 0 — so a sweep that enumerates tables in an unlucky order leaves a view pointing at nothing. (Dropping the *view* by name does clean up its hidden `.inner_id` table; that half was checked and is not a leak.) |
| **Ordering** | **Bootstrap first, then filename order.** The bootstrap is two statements the directory does not contain — `CREATE DATABASE IF NOT EXISTS relay_analytics`, then the ledger — and only then `0000`, `0001`, `0002` by filename. `0001_daily_usage.sql` reads `message_events`, so `0000` must have run: the materialised view creation fails with `UNKNOWN_TABLE` otherwise, which was checked. |

## The statements

| file | creates | source |
|---|---|---|
| `0000_message_events.sql` | `relay_analytics.message_events` | SAD §6.2, with `toDateTime(ts)` in the TTL and the database named |
| `0001_daily_usage.sql` | `relay_analytics.daily_usage` | SAD §6.2, with both its own name and its `FROM` qualified |
| `0002_schema_applied.sql` | `relay_analytics.schema_applied` | this chapter's |

**`0002` is applied before `0000` by the script's own bootstrap**, because a ledger cannot
record its own creation from a table that does not exist. The script creates it unconditionally
with `IF NOT EXISTS` and records everything after it.

**And the same argument runs one level further up, which is where it was missing.** A ledger
cannot be created in a database that does not exist either, so the bootstrap's first statement is
`CREATE DATABASE IF NOT EXISTS relay_analytics` — and under the one-statement-per-file rule it
cannot ride along inside `0002`. It is the script's, not the directory's: a `.sql` file for it
would need a filename sorting before `0000`, and the ledger cannot record the creation of the
database the ledger lives in.

## Comparing the two tables

**Both sides take the same 90-day predicate, always.** The rollup outlives the raw table by
however far the corpus reaches past the TTL, so an unwindowed comparison is between two
populations and every number it reports carries the difference between them. That matters most
where it is least visible: `uniqMerge` against `uniqExact` is supposed to measure `uniq`'s
approximation, which is **0.51% at 70,000 distinct** — small enough that a TTL-shaped difference
swallows it whole and still looks like an approximation error.

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
this table holds **one row per event** — 303,885 creations, **3,935** edits and 4,056 deletions
from the lane's 303,885 messages, **311,876** rows. The edit count comes from `message_edits`,
one row per edit; `messages.edited_at` holds only the latest and would give 3,201, **losing 734
events across the 428 messages edited more than once** (max 3). `daily_usage` filters `WHERE event = 'created'`, so
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
