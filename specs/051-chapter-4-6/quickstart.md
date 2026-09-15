# Quickstart — chapter 4.6, "metering you can bill on"

**Feature**: `specs/051-chapter-4-6/` · **Date**: 2026-09-15

**Constitution VI requires this to run unmodified.** Everything below was executed while this
file was written, except the blocks marked **after phase N**, which name what does not exist
yet. Paths are relative to `relay-platform/` unless stated.

---

## 0. The stack

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d
```

```bash
curl -s localhost:8222/healthz          # {"status":"ok"}
curl -s localhost:4000/healthz          # {"status":"ok","service":"api",...}
curl -s -X POST http://localhost:8123/ -u relay:relay --data-binary "SELECT 1"
```

The third is a positive control. 047 read three `curl` outputs as data when all three were
authentication errors.

**One statement per request.** The HTTP interface refuses a multi-statement body with
`Code: 62`, which is the interface's rule rather than a tidiness convention.

**And start an ingester if you intend to wait on a row.** There is no ingester service in
`compose.yaml` and 050-8 measured 4.4's suite passing 5 of 5 with one running and failing 5 of
5 without:

```bash
RELAY_NATS_URL=nats://localhost:4222 node services/ingester/dist/main.js
```

## 1. Which tables have producers, and which do not

The figure this chapter is about. Run it before reading any of the argument:

```bash
for t in message_events api_requests connection_events webhook_attempts; do
  echo -n "$t: "
  curl -s -X POST http://localhost:8123/ -u relay:relay \
    --data-binary "SELECT count() FROM relay_analytics.$t FORMAT TSV"
done
```

Measured 2026-09-15:

```
message_events: 0
api_requests: 11683
connection_events: 154
webhook_attempts: 64
```

**The one table the rollup reads is the one table nothing writes.** Confirm it from the other
side — every file in the repository that mentions it:

```bash
grep -rln "message_events" --include=*.ts --include=*.mjs --include=*.sql . | grep -v node_modules
```

```
scripts/scale/load-analytics.mjs      the batch loader
analytics/0000_message_events.sql     the DDL
analytics/0001_daily_usage.sql        the view
analytics/0003_webhook_attempts.sql   a comment
analytics/query.mjs                   an unwired demo script
```

**Occurrences under `services/`: zero.** Every table with rows flows through
`services/ingester/src/clickhouse.ts`.

## 2. The rollup that already exists, and what it holds

```bash
curl -s -X POST http://localhost:8123/ -u relay:relay --data-binary \
  "SELECT count() FROM relay_analytics.daily_usage FORMAT TSV"
```

`0`. **The view is not broken** — planting one row in `message_events` produces exactly one
rollup row, which research R8 did and then cleaned up. It has simply never had input on this
stack, because 4.2's measurements were taken against a `relay_corpus_<timestamp>` database.

Its storage shape, which decides what extending it costs:

```bash
curl -s -X POST http://localhost:8123/ -u relay:relay --data-binary \
  "SELECT name, engine FROM system.tables WHERE database='relay_analytics' ORDER BY name FORMAT TSV"
```

```
.inner_id.3f6e34d9-…   SummingMergeTree     <- an IMPLICIT inner table
daily_usage            MaterializedView
```

There is no named target for a second view to write into. That is research R7, and it is why
this chapter adds a statement rather than editing `0001` — which the ledger would refuse
anyway, on its checksum.

## 3. What a connection record carries

```bash
curl -s -X POST http://localhost:8123/ -u relay:relay --data-binary \
  "SELECT ts, close_code, duration_ms,
          toString(ts - toIntervalMillisecond(duration_ms)) AS derived_open
     FROM relay_analytics.connection_events FINAL
    WHERE event='closed' ORDER BY ts DESC LIMIT 3 FORMAT TSV"
```

```
2026-09-15 02:58:03.876   1000   252   2026-09-15 02:58:03.624
```

A close row alone gives both endpoints. The open record is not needed.

And the number that bounds what can be billed:

```bash
curl -s -X POST http://localhost:8123/ -u relay:relay --data-binary \
  "SELECT countIf(n=2) AS both, countIf(n=1) AS one_only, count() AS connections
     FROM (SELECT connection_id, uniqExact(event) AS n
             FROM relay_analytics.connection_events FINAL GROUP BY connection_id) FORMAT TSV"
```

```
55   44   99
```

**Forty-four percent have no close record.** Chapter 4.5 measured why — a clean stop produces
opens with no closes and a kill produces neither — and 050-5 files it.

## 4. After phase 2 — the rollup table

```bash
node analytics/apply.mjs
```

Expect `applied 1: 0006_daily_usage_v2.sql`, then `applied nothing` on a second run.

## 5. After phase 4 — the metering read

```bash
curl -s -X POST http://localhost:8123/ -u relay:relay --data-binary \
  "SELECT day, sum(messages), uniqMerge(active_users_state), sum(connection_minutes)
     FROM relay_analytics.daily_usage_v2
    WHERE environment_id = toUUID('<env>')
    GROUP BY day ORDER BY day FORMAT TSV"
```

**`sum()` with `GROUP BY`, and `uniqMerge` for the state column.** 047 measured
`SELECT messages` returning `1000 1000 1000` where the truth was 3000 — one physical row per
key per insert until a merge. See `contracts/metering-read.md` for the full contract,
including why the stored count is a separate read with no lower bound.

## 6. The eleven gates

**Eleven, and the last two are the ones a chapter can ship without.** `.itest.ts` files load
`vitest.integration.config.mts`, which `pnpm test` never opens, and `coverage` is the only
lane that enforces the per-file pins.

```bash
cd relay-tutorial
pnpm check:fences
pnpm check:docs
pnpm check:srs
pnpm check:figures
pnpm build            # 90 s; the gate that caught 4.4 missing from lib/tutorial.ts
pnpm check:errors     # reads the BUILT dist — build first
```

```bash
cd relay-platform
pnpm build
pnpm lint
pnpm typecheck
pnpm test
pnpm test:integration
pnpm coverage
```

**Four api suites were red at 050's close for reasons no chapter caused** —
`request-log.itest.ts` (needs an ingester, 050-8), `limits.itest.ts` (`RELAY_INTERNAL_CREDENTIAL`
unset), `session.perf.itest.ts` (a `Seq Scan` on an empty table), and an outbox concurrency
flake. Measure the colours at phase 1 so an inherited red is not read as a new one.

**And `pnpm coverage` has produced a false "No test files found" once**, reproduced in a
worktree and then not reproducible (050-1). If it says that, it is not evidence the lane is
broken.

## 7. The fence chain

```bash
cd relay-tutorial && pnpm check:fences
```

Report the close as a delta against an opening measured in this feature, **by kind and
locale**, and **split the two HEAD classes**: 11 of the inherited 36 are
`<title> does not exist in relay-platform` — fences titled with a prose phrase rather than a
path, which can never be repaired by editing the platform (050-4). The other 25 are real
divergences.

**Count the fenced-file list; do not carry it.** 050's was wrong in both directions.

```bash
grep -rn '^```[a-z]* title=' "app/(en)" "app/(vi)" | grep -oP 'title="\K[^"]+' | sort | uniq -c | sort -rn
```

**And check the vi locale before editing a file.** The vi chain holds whole bodies that the
checker never compares against the tree (050-3), so breaking one is invisible to every gate.
