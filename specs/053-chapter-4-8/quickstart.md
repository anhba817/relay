# Quickstart — chapter 4.8

**Every command below was run before it was written.** Chapter 4.6's record carries the reason:
an analysis pass put `CORPUS_DAYS=60` into a quickstart, nobody ran it, and the seeder refuses
that value in as many words.

The lane's Postgres lives on **15432** — this machine's own holds 5432.

---

## 1. Bring the stack up

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d
docker compose ps --format '{{.Service}} {{.State}}'
```

Expected: `clickhouse`, `mailpit`, `nats`, `postgres`, `redis`, all `running`.

## 2. Prove the store answers before trusting anything it says

```bash
curl -sS -u relay:relay 'http://localhost:8123/' --data-binary "SELECT 1 FORMAT TSV"
```

Expected: `1`. Chapter 4.2 shipped a probe that read `curl`'s output without checking it and
reported an authentication error three times as data; this line is the positive control.

## 3. Read the table's shape from the server, not from the migration file

```bash
curl -sS -u relay:relay 'http://localhost:8123/' \
  --data-binary "SHOW CREATE TABLE relay_analytics.api_requests FORMAT TSVRaw" \
  | grep -E '^TTL|^ORDER BY'
```

Expected:

```text
ORDER BY (environment_id, ts, request_id)
TTL toDateTime(ts) + toIntervalDay(30)
```

The server normalises what the file says — chapter 4.6 read `engine_full` for `25 MONTH`, got
zero, and read it as a failed `ALTER`. `SHOW CREATE TABLE` is the instrument that answers.

## 4. The three opening measurements

```bash
CH() { curl -sS -u relay:relay 'http://localhost:8123/' --data-binary "$1"; }

# the tenantless share
CH "SELECT count() AS total,
           countIf(environment_id IS NULL) AS tenantless,
           round(countIf(environment_id IS NULL)/count()*100, 2) AS pct
      FROM relay_analytics.api_requests FORMAT TSV"

# how much of the attributed half is the platform calling itself
CH "SELECT countIf(startsWith(assumeNotNull(endpoint), '/internal')) AS internal,
           countIf(startsWith(assumeNotNull(endpoint), '/v1'))       AS v1,
           count()                                                  AS attributed
      FROM relay_analytics.api_requests
     WHERE environment_id IS NOT NULL FORMAT TSV"

# what one tenant holds
CH "SELECT quantileExact(0.5)(n), quantileExact(0.95)(n), max(n), count() AS tenants
      FROM (SELECT environment_id, count() AS n
              FROM relay_analytics.api_requests
             WHERE environment_id IS NOT NULL
             GROUP BY environment_id) FORMAT TSV"
```

Measured 2026-09-16: `11684 7063 60.45`, `1656 1857 4621`, `10 155 208 152`.

**Two decimals, not one.** `round(…, 1)` reports 60.5 for the same rows, and SC-010 asks for
this figure again at the close — a criterion measured at two precisions is a criterion that
looks like it moved.

**These are facts about the lane on that day and they will move.** Chapter 4.7's opening figures
changed while its own phases ran, because integration lanes write to the store this chapter
reads. Take them again at the close.

## 5. Watch a page read one whole granule

```bash
BIG=$(curl -sS -u relay:relay 'http://localhost:8123/' --data-binary \
  "SELECT environment_id FROM relay_analytics.api_requests
    WHERE environment_id IS NOT NULL GROUP BY environment_id
    ORDER BY count() DESC LIMIT 1 FORMAT TSV")

curl -sS -u relay:relay 'http://localhost:8123/' --data-binary \
  "SELECT ts, request_id, endpoint, method, status, latency_ms
     FROM relay_analytics.api_requests
    WHERE environment_id = toUUID('$BIG')
    ORDER BY ts DESC, request_id DESC LIMIT 50 FORMAT Null" -D - \
  | grep -i 'X-ClickHouse-Summary'
```

Expected: `"read_rows":"8194"` for `"result_rows":"50"`. `index_granularity` is 8192, so one
granule is the floor. That tenant owns 208 rows in total.

## 6. See that `quantile` is not exact, at the sizes this chapter cares about

```bash
CH "SELECT 100, quantile(0.95)(x), quantileExact(0.95)(x)
      FROM (SELECT (number % 10000) + 1 AS x FROM numbers(100)) FORMAT TSV"
```

Expected: `100  95.05  96` — 0.99% apart at a hundred samples, which is larger than an hour of
one tenant's deliveries. The error does not shrink with size the way `uniq`'s does; see
`research.md` R2 for the table.

## 7. The gates, run the way this project has to run them

```bash
cd relay-platform
pnpm lint && pnpm typecheck && pnpm test
for p in api gateway ingester test-harness; do
  RELAY_POSTGRES_PORT=15432 pnpm --filter @relay/$p test:integration
done

cd ../relay-tutorial
pnpm run check:docs && pnpm run check:srs && pnpm run check:figures
pnpm build && pnpm run check:errors
pnpm check:fences
```

**Run the four integration lanes separately.** `pnpm test:integration` at the root is
`turbo run … --concurrency=1`, which stops scheduling at the first failure: it plans 18 tasks,
attempts 9, and prints `Tasks: 7 successful, 9 total` while three lanes never start
(`gaps.md` 051-3, measured at chapter 4.7's close).

**And use `pnpm run <script>`, not `pnpm -s <script>`.** The `-s` form reports RED for all four
tutorial gates that are green — measured at 4.7, and every figure in that record was re-taken
with `pnpm run`.

## 8. Expected reds at this feature's opening

`request-log.itest.ts` fails 5 of 5 at 5,001 ms each without an ingester process running
(`gaps.md` 050-8). That suite is chapter 4.4's, over the table this chapter reads, and its
redness is the reason phase 1 measures the opening rather than inheriting it.
