# Quickstart — chapter 4.16

Prove the chapter against a running stack: bytes appearing in a tenant's daily figure as objects
are taken, a rejection taking them back out, the metered level agreeing with the object store,
and a slot request that still succeeds with the analytical store stopped.

**RUN END TO END ON 2026-09-30**, against the composed stack. It was wrong in three places and
each one is corrected below with what the wrong version looked like. One further failure was
mine rather than the document's: §2 returned no row because I had not started the ingester,
which §0 says to do in bold — the warning working rather than a defect.

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

**IF `apply.mjs` REFUSES `0018_mv_billing_storage.sql` AS CHANGED**, this lane applied the
first version of that view, which counted a zero for every kind that had a non-upload event.
The migration was amended in place because it has shipped nowhere (`gaps.md` 062-6), and the
ledger refusing it is the gate working. Two commands, then re-run the apply:

```bash
cq() { curl -s -u relay:relay "http://localhost:8123/" --data-binary "$1"; }
cq "DROP TABLE IF EXISTS relay_analytics.mv_billing_storage"
cq "ALTER TABLE relay_analytics.schema_applied DELETE WHERE filename = '0018_mv_billing_storage.sql'"
node analytics/apply.mjs
```

A fresh clone and CI never meet this.

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

**CORRECTION 1 — this step referred the reader to another document.** It read
`node -e '/* 4.15's fixture … */' # see quickstart 4.15 §1`, which runs nothing and leaves
`/tmp/relay-4-15.png` absent, so `stat` fails and `$BYTES` is empty. A quickstart that cannot be
run from itself is a quickstart nobody runs. The generator is inlined:

```bash
node -e '
const z=require("node:zlib"), fs=require("node:fs");
const W=800,H=600, raw=Buffer.alloc(H*(1+W*3));
for(let y=0;y<H;y++){const o=y*(1+W*3); raw[o]=0;
  for(let x=0;x<W;x++){const p=o+1+x*3; raw[p]=(x*7)&255; raw[p+1]=(y*5)&255; raw[p+2]=((x^y)*3)&255;}}
const chunk=(t,d)=>{const l=Buffer.alloc(4);l.writeUInt32BE(d.length);
  const b=Buffer.concat([Buffer.from(t),d]); const c=Buffer.alloc(4);
  c.writeUInt32BE(z.crc32(b)); return Buffer.concat([l,b,c]);};
const ihdr=Buffer.alloc(13); ihdr.writeUInt32BE(W,0); ihdr.writeUInt32BE(H,4);
ihdr[8]=8; ihdr[9]=2;
fs.writeFileSync("/tmp/relay-4-16.png", Buffer.concat([
  Buffer.from([0x89,0x50,0x4e,0x47,0x0d,0x0a,0x1a,0x0a]),
  chunk("IHDR",ihdr), chunk("IDAT",z.deflateSync(raw)), chunk("IEND",Buffer.alloc(0))]));
console.log("wrote", fs.statSync("/tmp/relay-4-16.png").size, "bytes");'
export BYTES=$(stat -c%s /tmp/relay-4-16.png)   # measured: wrote 447377 bytes
SLOT=$(curl -sX POST localhost:4000/v1/media \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d "{\"filename\":\"bill.png\",\"mime_type\":\"image/png\",\"bytes\":$BYTES}")
export MEDIA=$(printf '%s' "$SLOT" | python3 -c 'import sys,json;print(json.load(sys.stdin)["media_id"])')

cq "SELECT event, kind, bytes_delta FROM relay_analytics.media_events
    WHERE media_id = toUUID('$MEDIA')"
```

**Expected**: one row, `reserved image 447377` — measured. **A slot that has not been uploaded
to is already charged** — the quota counts `pending`, and FR-002 makes the meter agree.

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
    WHERE media_id = toUUID('$MEDIA') ORDER BY ts"
cq "SELECT sum(bytes_delta) FROM relay_analytics.media_events WHERE media_id = toUUID('$MEDIA')"
```

**CORRECTION 2 — this query said `ORDER BY occurred_at` and the column is `ts`.** Measured:
`Code: 47. DB::Exception: Unknown expression identifier 'occurred_at'`. `occurred_at` is the
PRODUCER's field name; `shapeMediaStored` renames it on the way in, which is the rename
`shape.ts`'s own header warns fails silently if it ever stops happening — and this document
tripped over the other side of it.

**Expected**: two rows — `reserved +447377` then `rejected −447377` — and a sum of **0**,
measured. The object is charged while it is `pending` and not once it is refused, which is
exactly what the quota's `state <> 'rejected'` does.

**Then deliver the same verdict again** and re-read: still two rows, sum still 0.

**CORRECTION 3 — the sentence explaining that was wrong, and it is this feature's own finding
written down twice.** The draft read *"the second verdict updates no rows (4.14's
compare-and-set), so it emits nothing."* Measured: **HTTP 422**,
`this object was rejected and its bytes are gone; a verdict cannot change that`. The
`applied: false` path belongs to a `ready` object; a rejected one is refused by name. Phase 3's
integration suite found exactly this and got `expected undefined to be false`, and the
correction did not reach this document. **The assertion held and the explanation did not**,
which is the harder half to notice.

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

**Expected**: **201**, measured. The operational path publishes to a stream and never reads the
analytical store, so an outage costs history and not availability. **And the record survived**:
`ANALYTICS` held 1,177 messages during the outage and the row was queryable **4 seconds** after
the restart, carrying its own `occurred_at` as `ts` — so the outage does not move the day the
bytes were charged.

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
