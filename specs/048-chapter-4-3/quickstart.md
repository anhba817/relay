# Quickstart — chapter 4.3

Prerequisites: the stack up with `RELAY_POSTGRES_PORT=15432`, and
`DOCKER_HOST=unix:///var/run/docker.sock` if `docker context ls` shows a selected `rootless`
context against a root-socket daemon.

## 1. See the thing this chapter is about

```bash
curl -s 'localhost:8222/jsz?streams=1&consumers=1' | jq '.account_details[].stream_detail[]
  | select(.name=="ANALYTICS") | {messages: .state.messages, consumers: .consumer_count}'
```

**Expected before this chapter:** a non-zero message count and **`consumers: 0`**. The
publisher has been running since chapter 3.20; nothing has ever read what it wrote.

## 2. Apply the new table

```bash
node analytics/apply.mjs
```

**Expected:** `applied 1: 0003_webhook_attempts.sql`, and the other three skipped. Run it
again and expect **`applied nothing`** — the line `CREATE TABLE IF NOT EXISTS` cannot give
you.

## 3. Drain the stream

```bash
node <the ingester> --once
```

**Expected:** rows in `relay_analytics.webhook_attempts` matching what the stream held, and
the consumer reporting zero pending. Compare the two counts; do not take the ingester's word
for what it wrote.

```bash
curl -s "http://localhost:${RELAY_CLICKHOUSE_HTTP_PORT:-8123}/" -u relay:relay \
  --data-binary "SELECT count(), count() FROM relay_analytics.webhook_attempts FINAL"
```

**Read this table with `FINAL`.** It is a `ReplacingMergeTree`, so a redelivered record is
physically present until a merge collapses it and a bare `SELECT count()` over-counts.
`FINAL` is the right answer at any moment; the bare count is right only after maintenance
somebody has to remember to run.

## 4. Take the store away

```bash
docker compose stop clickhouse
# exercise the platform: send messages, trigger webhook deliveries
docker compose start clickhouse
```

**Expected:** no send fails, no delivery fails, and the stream's depth grows. On recovery
the backlog drains and the counts reconcile against what was published.

**This is the step that justifies the whole design.** If messaging degrades when the
analytical store is gone, the second store bought nothing.

## 5. Force a redelivery

Stop the ingester after an insert but before the acknowledgement, then restart it so the
broker redelivers those records.

**Expected:** `SELECT count() FINAL` does not move. The bare `SELECT count()` **does** move,
and that is not a failure — it is the engine holding the duplicate until a merge, which is
exactly what `FINAL` is for.

**Force the regrouping, because that is the case that matters.** Restart the ingester with a
different batch size so the redelivered records are cut differently from the originals. The
count under `FINAL` still must not move. A redelivery test that replays the same batch shape
proves the easy half; the first version of this design passed that half and was wrong.

## 6. Clean up

```bash
node analytics/apply.mjs --drop-all
```

Each phase drops what it made. Confirm with
`SELECT count() FROM system.tables WHERE database = 'relay_analytics'` — 0 from a database
that does not exist, not an error.
