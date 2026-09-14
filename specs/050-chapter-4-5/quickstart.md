# Quickstart — chapter 4.5, the gateway's first stream

**Feature**: `specs/050-chapter-4-5/` · **Date**: 2026-09-14

**Constitution VI requires this to run unmodified.** Everything below was executed while this
file was written, except the blocks marked **after phase 4**, which name what does not exist
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

**Stop the api before restarting NATS, not after.** 049-1 measured that the stream being
*written* when the broker restarts is the one that fails to recover — graceful or not — and
049-2 measured that the compose api cannot recreate a stream it does not have
(`replicas > 1 not supported in non-clustered mode`, because the image sets
`NODE_ENV=production`).

## 1. What the gateway holds before this chapter

```bash
node -e 'const p=require("./services/gateway/package.json");
         const d=Object.keys(p.dependencies||{});
         console.log(d.length, "-", d.join(", "))'
```

```
5 - @relay/protocol, @relay/service-kit, ioredis, jose, ws
```

**That number is the subject, not a detail.** ADR-07 rejects NATS for the gateway on an argument
about *"how many client libraries the gateway holds, not about whether the mechanism fits"*.
This chapter takes it to six.

And the gateway already reports connection data — it has since 3.24:

```bash
grep -n "usage/connections" services/gateway/src/api-client.ts
grep -n "METER_INTERVAL_MS" services/gateway/src/meter.ts
```

Every sixty seconds, batched, to the api. The question this chapter answers is not *"how does
the gateway report?"* but *"why is that report the wrong shape for FR-ANL-01?"*

## 2. Reproduce the burst measurement

The number that decides where the publish goes. From `research.md` R3, 2,000 close records
three ways:

```
awaited, one at a time   : 2000 publishes in 458 ms  -> 0.229 ms each
  extrapolated to 10,000 closing at once: 2.3 s of awaited publishes
core publish + flush     : 2000 publishes in   6 ms  -> 0.0030 ms each
pipelined, 500 in flight : 2000 publishes in   7 ms  -> 0.0034 ms each
```

The third row is **one message per record with 500 publishes in flight**, not 500 records in
one message. Analysis pass 5 found the original wording read as the second, which the ingester
terminates: an array has no `type`, so `route()` shapes it to `null` and `ingest.ts` calls
`m.term()`. Re-run the probe in the shape you are going to ship.

`session.ts`'s close handler already argues the conclusion, for HTTP:

```bash
grep -n "burst of HTTP requests" -B2 services/gateway/src/session.ts
```

## 3. After phase 4 — the table exists

```bash
node analytics/apply.mjs
```

Expect `applied 1: 0005_connection_events.sql`, then `applied nothing` on a second run.

```bash
curl -s -X POST http://localhost:8123/ -u relay:relay --data-binary \
  "SELECT count() FROM relay_analytics.connection_events FINAL FORMAT TSV"
```

## 4. After phase 4 — a connection becomes two rows

Open a socket, let it settle, close it. Then:

```bash
curl -s -X POST http://localhost:8123/ -u relay:relay --data-binary \
  "SELECT event, connection_id, ts,
          ifNull(toString(close_code),'~absent')  AS close_code,
          ifNull(toString(duration_ms),'~absent') AS duration_ms
     FROM relay_analytics.connection_events FINAL
    ORDER BY ts DESC LIMIT 10 FORMAT TSV"
```

**Two rows, not one.** `event` is in the sorting key for that reason — without it a
`ReplacingMergeTree` collapses the open into the close. Verified against the real server while
this file was written:

```
opened   ~absent  ~absent
closed   1000     5000
count() FINAL: 2
```

`FINAL` is not decoration: 048 measured a bare `count()` answered from part metadata, 0.9 ms
and wrong by 100,000.

## 5. After phase 5 — the two counters, compared

```bash
curl -s -X POST http://localhost:8123/ -u relay:relay --data-binary \
  "SELECT connection_id,
          anyIf(ts, event='opened')  AS opened_at,
          anyIf(ts, event='closed')  AS closed_at,
          anyIf(duration_ms, event='closed') AS duration_ms
     FROM relay_analytics.connection_events FINAL
    GROUP BY connection_id
   HAVING closed_at > toDateTime64('2020-01-01 00:00:00',3,'UTC') FORMAT TSV"
```

Compare the **minute buckets** those timestamps touch against what the meter reported for the
same connections. Do **not** compare duration against minutes: the meter charges every calendar
minute a connection was open for any part of, so a two-second connection across a boundary is
two connection-minutes. Those are different quantities sharing a name, and the chapter publishes
the difference rather than calling it small.

## 6. The gates

All five `check:*` live in **`relay-tutorial`**. `pnpm` in the wrong repository fails loudly
(exit 254) but names a script that does not exist, which reads like a broken gate rather than a
wrong directory.

```bash
cd ../relay-tutorial
pnpm check:fences      # exits 1 at the inherited baseline — report the DELTA
pnpm check:docs
pnpm check:srs
pnpm check:figures     # the gate over figures.ts — pass diagrams as `code`, not `chart`
pnpm check:errors      # reads the BUILT dist — build first
```

`check:fences` exited 1 at **110** for 047, 048 and 049, and the exit code carries no
information about this chapter. The delta is what the chapter answers for.

```bash
cd ../relay-platform
pnpm lint && pnpm typecheck && pnpm test
```

**Expect to owe fence hunks.** This chapter edits `session.ts`, `main.ts`, `shape.ts`,
`ingest.ts` and the protocol, all of which earlier chapters publish as whole bodies. 049
discovered at its close that this costs six problems until the diffs are published; do not
discover it again in phase 6.

## 7. Bringing it down

```bash
cd relay-platform && docker compose --profile services down
```

Volumes are kept, which preserves the corpus.
