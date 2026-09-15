# Contract — the metering read

**What a caller asks for, what comes back, and what the read may not touch.** This is the
artifact nothing else reads, which is where 046 and 047 each hid a defect for six and four
passes — so every invocation line here is one somebody can paste.

## The question

For one tenant and one period, FR-ANL-05's quantities: messages sent, unique active users,
connection-minutes, and stored message count.

## Where it lives

`relay-platform/services/ingester/src/metering.ts`, over a query method on `ClickHouse` —
beside `clickhouse.ts`, which owns the store's client and its four environment variables. That
interface was insert-and-count when this chapter opened (`insert`, `insertRequests`,
`insertConnections`, `count`, `countRequests`, `countConnections`, with `post()` a private
closure), so the read is not merely placed beside it: the interface gains a method, the way it
has gained one per chapter since 4.3. **Otherwise a read "beside the client" opens a second
one**, and the one-client claim is a sentence rather than a property.

Its caller from day one is `services/ingester/src/metering.itest.ts`, which the ingester's
`test:integration` reaches — `include: ["src/**/*.itest.ts"]`, recursive. **A read with no
caller is `analytics/query.mjs`**, which opens *"FR-ANL-05's daily question, asked of the
analytical store"* and is referenced by no script, service or config.

## The invocation

ClickHouse over HTTP, `relay` / `relay`, port 8123, one statement per request — the HTTP
interface refuses a multi-statement body (`Code: 62`), which 047 established is the
interface's rule rather than a convention.

```bash
curl -s -X POST http://localhost:8123/ -u relay:relay --data-binary "
  SELECT day,
         sum(messages)                  AS messages,
         uniqMerge(active_users_state)  AS active_users,
         sum(connection_minutes)        AS connection_minutes
    FROM relay_analytics.daily_usage_v2
   WHERE environment_id = toUUID('<env>')
     AND day BETWEEN '<from>' AND '<to>'
   GROUP BY day ORDER BY day FORMAT TSV"
```

**`sum()` and `GROUP BY` are the contract, not a style.** `SummingMergeTree` holds one
physical row per key per insert until a background merge; 047 measured `SELECT messages`
returning `1000 1000 1000` where the truth was 3000. A read whose correctness depends on
somebody having run `OPTIMIZE` is right in a demo and wrong in production.

**`uniqMerge`, not `sum`,** for active users: the column is an aggregate state.

## The stored count is a separate read

```bash
  SELECT sum(stored_delta)
    FROM relay_analytics.daily_usage_v2
   WHERE environment_id = toUUID('<env>') AND day <= '<to>'
```

**No lower bound, deliberately.** The stored message count is a running balance, so it sums
every delta up to the day asked for. A `BETWEEN` here would report the period's *change* in
stored messages, which is a different question and reads as a plausible wrong answer.

## The rows-read claim needs a corpus, and the corpus fills two rollups

**The store cannot answer this question unloaded.** `message_events` holds 0 rows and
`connection_events` 154; 4.2's published 315-against-1,052,655 exists because that chapter
loaded a corpus. So the figure below is taken inside one window, against a corpus whose size
and day-span are stated, and the corpus is removed afterwards.

**And the load fills `daily_usage` as well.** `analytics/0001_daily_usage.sql:19` reads
`FROM relay_analytics.message_events`, so chapter 4.2's view gains rows from the same insert.
Anything that cleans up after this measurement cleans both — and a delete on the source does
not propagate to a materialised view's target, so 4.2's inner table is cleaned by its own
name.

## What the read may not touch

- **No raw event table.** DR-10: *"so billing never scans raw events."* The rows-read figure
  is published beside the raw tables' counts, the way 4.2 published 315 against 1,052,655.
- **No Postgres.** Constitution III's first bullet. The plan's Constitution Check records that
  metering today reads *only* Postgres and that this chapter cannot close that gap — the read
  defined here does not widen it.
- **No message text.** Nothing in the rollup carries any; the allow-list is satisfied by
  construction rather than by a filter.

## What comes back when there is nothing

**A missing row, never a row of zeros.** A materialised view emits nothing for a group with
no input, so a tenant-day with no activity has no row at all. A caller that needs a dense
series fills the gaps itself and must not read an absent row as "we measured zero" — the two
are different claims and only one of them is evidence.

## Scoping, and what it excludes

**Connection-minutes come from close records only.** R4: a close carries the closing instant
and the duration, so the open adds nothing. R5 measured the cost on the store as it stands:

    connections with both records   55
    with one only                   44
    total                           99

A connection with no close contributes zero minutes. **The count of opens without closes is
published beside the minutes figure** — 4.5 measured why they exist (a clean stop produces
opens with no closes, a kill produces neither) and 050-5 files it. A billing figure that
silently drops 44% of its population is the failure FR-009a's scoping lesson exists to
prevent, one domain over.

## Tenancy

Every row is keyed on `environment_id` and every read above names it. The test is the one 4.4
and 4.5 wrote: a second tenant's rows are unreachable from the first tenant's filter, asserted
in both directions.

## What this contract does not cover

- **Agreement to within 0.1%.** FR-ANL-06's reconciliation is chapter 4.7 and the milestone is
  4.9. 047-1 and 048-1 — DR-10 and FR-ANL-06 cannot both hold, for two independent reasons —
  are filed for movement IV and are handed forward from here untouched.
- **A customer-facing query surface.** FR-ANL-07 and FR-ANL-10 are chapter 4.8.
- **Application-level attribution.** No analytical row carries an application, and the
  environment-to-application mapping lives in Postgres. Recorded as an open item with its cost
  named rather than answered with a cross-path join.
