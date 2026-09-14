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
awaited, one at a time   : 2000 publishes in 574 ms  -> 0.2870 ms each
  extrapolated to 10,000 closing at once: 2.87 s of awaited publishes
core publish + flush     : 2000 publishes in   5 ms  -> 0.0025 ms each
pipelined, 500 in flight : 2000 publishes in  52 ms  -> 0.0260 ms each
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
same connections, **split by period the way `entriesFor` splits them** — a socket open across a
month boundary owes minutes to two periods and each is credited independently, so a derivation
that does not split disagrees for a reason that is neither of the two this comparison exists to
show (FR-009b). The `HAVING` above is the other half: it keeps only connections with a close
record, because the meter also bills connections that are still open (FR-009a). Do **not**
compare duration against minutes: the meter charges every calendar
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
pnpm build             # the one that catches a chapter missing from lib/tutorial.ts
```

**`pnpm build` is a gate.** Chapter 4.4 shipped without an entry in `lib/tutorial.ts`, and
`<ChapterHeader id="4.4" />` calls `getChapter`, which throws on an unregistered id — so the
site failed to build from the moment 4.4 closed at 112 of 112 with every other gate green.
**None of the five above renders a page.**

`check:fences` exited 1 at **110** for 047, 048 and 049, and the exit code carries no
information about this chapter. The delta is what the chapter answers for.

```bash
cd ../relay-platform
pnpm lint && pnpm typecheck && pnpm test
pnpm test:integration    # the ONLY lane that runs *.itest.ts
pnpm coverage            # the only lane that enforces the per-file pins
```

**Eleven gates, and the last two run every test this chapter writes.** `.itest.ts` files load
`vitest.integration.config.mts`, which `pnpm test` never opens, so
`connection-log.itest.ts` — which carries all of US1's proofs and discharges SC-001, SC-004 and
SC-007 — executes under `test:integration` alone.

**Expect to owe fence hunks — for eight files, and `ingest.ts` is not one of them.** Counted
rather than remembered:

```
32 session.ts · 25 internal.ts · 23 vitest.coverage.config.mts · 22 main.ts
10 services/gateway/package.json · 4 internal.test.ts · 3 clickhouse.ts · 3 shape.ts
 0 services/ingester/src/ingest.ts
```

`ingest.ts` carries no titled fence anywhere, because 049 created it by moving `ingestOnce` out
of `main.ts` and fenced `main.ts` and `clickhouse.ts` instead. **`vitest.coverage.config.mts`
is the one that cannot be paid**: 048-3 records that the chain replays 317 lines where the tree
holds 944, so it takes a gaps entry rather than a hunk. 049 discovered at its close that
editing a fenced file costs six problems until the diffs are published; **phase 8** publishes
them, deliberately.

## 7. Bringing it down

```bash
cd relay-platform && docker compose --profile services down
```

Volumes are kept, which preserves the corpus.

**Check the order this stops things in before trusting it.** §0 states the hazard — 049-1
measured that the stream being *written* when the broker stops is the one that fails to
recover, graceful or not, and 4.4 made the api write on every request so `ANALYTICS` is never
idle. `compose down` stops containers in reverse dependency order, which should take the api
before NATS, but **this file has never verified that it does**. If `/healthz` comes back
degraded on the next `up`, stop the writers explicitly first:

```bash
docker compose stop api gateway dispatcher ingester && docker compose --profile services down
```
