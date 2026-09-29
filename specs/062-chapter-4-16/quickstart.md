# Quickstart — chapter 4.16

Prove the chapter against a running stack: bytes appearing in a tenant's daily figure as objects
are taken, a rejection taking them back out, the metered level agreeing with the object store,
and a slot request that still succeeds with the analytical store stopped.

**NOT YET RUN AS A WHOLE. This is a plan-time draft**, and saying otherwise before it has been
run is the one failure this document cannot recover from. Running it is a phase-9 task and every
correction goes here with what the wrong version looked like.

**What HAS been verified, during planning:** the ClickHouse client invocation below answers
(`message_events 0`, `api_requests 118238`); the bucket listing returns a `ListBucketResult`
with 1,000 keys, `IsTruncated: true`, a `<Size>` per key and every key tenant-prefixed; and the
operational sum is 8,120 objects at 4,255 MB across 1,576 environments.

The corrections earlier chapters earned are applied rather than rediscovered:

- the api is on **port 4000**, the gateway on **4001** (`ci.yml:359` — 4.15 lost seven outsider
  tests to that one);
- a channel takes `{external_id, type}`, a slot takes `{filename, mime_type, bytes}`, and
  neither takes `idem_key`;
- the seeder's credential is an **application** credential, so every send names a bot, and
  `outside-bot` exists in the demo tenant where `demo-bot` does not;
- the worker credential is `rk_svc_local_development_worker_000000`;
- `psql -tAc` with `RETURNING` prints the value **and** the command tag, so `head -1` first;
- `uuidgen` is not installed; `/proc/sys/kernel/random/uuid` needs nothing;
- **`docker compose --profile services stop` names its services, and `ingester` is not one** —
  it has no Dockerfile, and naming it makes the whole command fail rather than partly apply;
- the PNG fixture below is 4.15's, which wrote 447,377 bytes and decoded.

## 0 · Prerequisites

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
pnpm build
DATABASE_URL=postgres://relay:relay@localhost:15432/relay node services/api/dist/db/migrate.js
node analytics/apply.mjs          # the ClickHouse schema — keyed on (filename, checksum)
RELAY_POSTGRES_PORT=15432 docker compose --profile services build
RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d --wait
export CREDENTIAL=$(RELAY_POSTGRES_PORT=15432 node scripts/seed-demo-tenant.mjs)
```

**This chapter needs the ingester running**, and it is not a compose service (4.9). A record on
the stream with nothing draining it leaves every figure at zero — which is indistinguishable
from a tenant that stored nothing, and is the reason §1 starts by reading the baseline.

## 1 · What the tenant is metered at before anything happens

```bash
cq() { docker compose exec -T clickhouse clickhouse-client --query "$1 FORMAT TSV"; }
export ENV_ID=$(RELAY_POSTGRES_PORT=15432 psql postgres://relay:relay@localhost:15432/relay -tAc \
  "select environment_id from media_objects group by 1 order by count(*) desc limit 1" | head -1 | tr -d ' ')
echo "env=$ENV_ID"

cq "SELECT sum(stored_bytes_delta) FROM relay_analytics.daily_usage_billing
    WHERE environment_id = toUUID('$ENV_ID')"
```

**Expected**: a number, and `0` is a legitimate answer for a tenant whose objects predate this
chapter. **Record it** — every later step is a difference from this, not an absolute.

## 2 · Take a slot and watch the figure move

```bash
node -e '/* 4.15's fixture, 800x600, 447,377 bytes */' > /dev/null   # see quickstart 4.15 §1
export BYTES=$(stat -c%s /tmp/relay-4-15.png)
SLOT=$(curl -sX POST localhost:4000/v1/media \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d "{\"filename\":\"bill.png\",\"mime_type\":\"image/png\",\"bytes\":$BYTES}")
export MEDIA=$(printf '%s' "$SLOT" | python3 -c 'import sys,json;print(json.load(sys.stdin)["media_id"])')

cq "SELECT event, kind, bytes_delta FROM relay_analytics.media_events
    WHERE media_id = toUUID('$MEDIA')"
```

**Expected**: one row, `reserved image <BYTES>`. **A slot that has not been uploaded to is
already charged** — the quota counts `pending`, and FR-002 makes the meter agree.

**If the row is absent**, ask in this order, because three of these look identical from here:
is the ingester running; did the record reach the stream
(`curl -s localhost:8222/jsz?streams=1`); and is `route()` claiming the type — an unrecognised
type is **redelivered, not destroyed**, so the record is still on the stream and the ingester's
`unclaimed` count is the only place that says so.

## 3 · A rejection takes the bytes back

```bash
export WORKER=rk_svc_local_development_worker_000000
curl -sS -X POST "localhost:4000/internal/media/$MEDIA/verdict" \
  -H "authorization: Bearer $WORKER" -H 'content-type: application/json' \
  -d '{"verdict":"rejected","reason":"declaration_mismatch","verified_bytes":10}'

cq "SELECT event, bytes_delta FROM relay_analytics.media_events
    WHERE media_id = toUUID('$MEDIA') ORDER BY occurred_at"
cq "SELECT sum(bytes_delta) FROM relay_analytics.media_events WHERE media_id = toUUID('$MEDIA')"
```

**Expected**: two rows — `reserved +N` then `rejected −N` — and a sum of **0**. The object is
charged while it is `pending` and not once it is refused, which is exactly what the quota's
`state <> 'rejected'` does.

**Then deliver the same verdict again** and re-read: still two rows. The second verdict updates
no rows (4.14's compare-and-set), so it emits nothing.

## 4 · The reconciliation against the store's own inventory

```bash
node scripts/reconcile-storage.mjs --environment "$ENV_ID"
```

**Expected**: a verdict per tenant naming what was compared and how many tenants were examined.
A zero that does not say how many it looked at is the shape this project keeps finding — five of
seven gate scripts exit 0 over an absent corpus.

**The listing pages**, and the test asserts more than 1,000 keys were seen: one response carries
1,000 with `IsTruncated: true`, and 4.13's sweep read one page and left objects unswept for ever.

## 5 · Constitution III: the analytical store goes away and the upload does not

```bash
RELAY_POSTGRES_PORT=15432 docker compose stop clickhouse
curl -s -o /dev/null -w 'slot with ClickHouse down -> %{http_code}\n' \
  -X POST localhost:4000/v1/media -H "authorization: Bearer $CREDENTIAL" \
  -H 'content-type: application/json' \
  -d '{"filename":"outage.png","mime_type":"image/png","bytes":1024}'
RELAY_POSTGRES_PORT=15432 docker compose start clickhouse
```

**Expected**: **201**. The operational path publishes to a stream and never reads the analytical
store, so an outage costs history and not availability.

**And the record should survive**: the ANALYTICS stream's `max_age` is 7 days
(`jetstream.publisher.ts:51`), so a few minutes of ClickHouse being down is well inside it.
Confirm both ends rather than assuming either — the record present on the stream during the
outage (`curl -s localhost:8222/jsz?streams=1`), and in `media_events` after the restart.

## 6 · What this cannot show

- **A `deleted` delta**, because nothing deletes a `media_objects` row (4.15). The negative arm
  is exercised by rejection only, and the reconciliation therefore cannot fail in the direction
  it exists to catch until the erasure chapter ships.
- **The weekly cadence**, because this platform has no runner for a recurring job (ADR-28). The
  comparison is invokable; the cadence is recorded as unmet.
- **The dashboard**, because there is not one.
