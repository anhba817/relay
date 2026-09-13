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
  --data-binary "SELECT count(), uniqExact((delivery_id, attempt)) FROM relay_analytics.webhook_attempts"
```

**The two numbers must be equal.** If `count()` exceeds the distinct pairs, something was
written twice.

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
broker redelivers the same sequence range.

**Expected:** the row count does not move, because the server refuses the duplicate block.

**Check the negative control too.** Remove `non_replicated_deduplication_window` from the
table and repeat: the token is accepted, the block is inserted, the count doubles, and
**nothing reports an error**. A mechanism that fails silently when half-configured has to be
shown failing, or a reader will assume the token alone was doing the work.

## 6. Clean up

```bash
node analytics/apply.mjs --drop-all
```

Each phase drops what it made. Confirm with
`SELECT count() FROM system.tables WHERE database = 'relay_analytics'` — 0 from a database
that does not exist, not an error.
