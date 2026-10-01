# Quickstart — chapter 4.17

Walk the milestone by hand, from outside, as a customer's backend would: a slot, an upload, a
message, a wait, a link, the bytes, and the thumbnail. Then break it two ways and see what each
looks like.

**EVERY STEP BELOW WAS RUN ON 2026-10-01** and the expected values are measured rather than
predicted. That is unusual for a plan-time quickstart and it is why: this chapter's whole
premise is that the path works and nothing asserts it, which cannot be claimed without walking
it first. What has **not** been run is this document as a document, start to finish, copy-paste
— that is a phase-8 task and the corrections go here.

The corrections earlier chapters earned are applied rather than rediscovered:

- the api is on **4000**, the gateway on **4001**;
- a send takes `{text, user, idempotency_key, attachments}` — **not `sender`**, which answers
  `400 Unrecognized key: "sender"`;
- `outside-bot` is the user the demo tenant has;
- the history response's array is keyed **`messages`**, not `data`;
- `psql -tAc` with `RETURNING` prints the value **and** the command tag;
- **`docker compose --profile services stop` names its services and `ingester` is not one**;
- `date +%s%3N` does **not** truncate on this machine — it appends nine digits of nanoseconds,
  so time things with something else.

## 0 · Prerequisites

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
pnpm build
DATABASE_URL=postgres://relay:relay@localhost:15432/relay node services/api/dist/db/migrate.js
node analytics/apply.mjs
RELAY_POSTGRES_PORT=15432 docker compose --profile services build
RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d --wait
export CREDENTIAL=$(RELAY_POSTGRES_PORT=15432 node scripts/seed-demo-tenant.mjs | tail -1)
```

**Read the worker's boot line before anything else.** It is the only thing that says the scanner
is reachable, and 4.13's defect was a worker that started clean and verified nothing:

```bash
docker compose logs media-worker | tail -2
```

**Expected**: `media worker started  interval_ms 5000  scanner "ClamAV 1.5.4/…"`. A `scanner`
of `unreachable` means every object below will stay `pending` for ever and **nothing will
fail**.

## 1 · A slot and an upload

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
fs.writeFileSync("/tmp/relay-4-17.png", Buffer.concat([
  Buffer.from([0x89,0x50,0x4e,0x47,0x0d,0x0a,0x1a,0x0a]),
  chunk("IHDR",ihdr), chunk("IDAT",z.deflateSync(raw)), chunk("IEND",Buffer.alloc(0))]));
console.log("wrote", fs.statSync("/tmp/relay-4-17.png").size, "bytes");'
export BYTES=$(stat -c%s /tmp/relay-4-17.png)

SLOT=$(curl -sX POST localhost:4000/v1/media -H "authorization: Bearer $CREDENTIAL" \
  -H 'content-type: application/json' \
  -d "{\"filename\":\"journey.png\",\"mime_type\":\"image/png\",\"bytes\":$BYTES}")
export MEDIA=$(printf '%s' "$SLOT" | python3 -c 'import sys,json;print(json.load(sys.stdin)["media_id"])')
export PUT_URL=$(printf '%s' "$SLOT" | python3 -c 'import sys,json;print(json.load(sys.stdin)["upload_url"])')
curl -sS -X PUT --data-binary @/tmp/relay-4-17.png "$PUT_URL" -o /dev/null -w 'PUT %{http_code}\n'
```

**Expected**: `wrote 447377 bytes`, then `PUT 200`. The slot costs 8–34 ms and never touches the
store — it is a signature (4.10).

## 2 · A channel, and a message that names the object before it is verified

```bash
CH=$(curl -sX POST localhost:4000/v1/channels -H "authorization: Bearer $CREDENTIAL" \
  -H 'content-type: application/json' -d "{\"external_id\":\"journey-$RANDOM\",\"type\":\"public\"}")
export CID=$(printf '%s' "$CH" | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')

curl -sX POST "localhost:4000/v1/channels/$CID/messages" -H "authorization: Bearer $CREDENTIAL" \
  -H 'content-type: application/json' \
  -d "{\"text\":\"an image, end to end\",\"user\":\"outside-bot\",\"idempotency_key\":\"$(cat /proc/sys/kernel/random/uuid)\",\"attachments\":[{\"type\":\"media\",\"media_id\":\"$MEDIA\"}]}" \
  | python3 -m json.tool | grep -A 4 attachments
```

**Expected**: `201`, and the attachment carries `"state": "pending"`. **A message may name an
object the scanner has not cleared** — that is FR-MED-06's decision at 4.11, so a photo can be
sent the moment the upload completes.

## 3 · The deployed worker

```bash
for i in $(seq 1 60); do
  S=$(psql postgres://relay:relay@localhost:15432/relay -tAc "select state from media_objects where id='$MEDIA'" | tr -d ' ')
  [ "$S" != "pending" ] && break
  sleep 0.5
done
echo "state=$S after ~$((i/2)) s"
```

**Expected**: `ready`, after **anywhere from 1.2 to 5.8 seconds — p50 2,953 ms over ten
trials**. If it comes back in a second, nothing is wrong: the sweep is a 5,000 ms timer and an
upload lands at a random point in the cycle, so **the wait is uniform over the interval and
only about 0.7 s of it is work.** An earlier draft of this line said *"about 5.7 s"* from five
runs taken in a loop — each starting just after the sweep that finished the one before, which
measured the worst case and called it typical. Nothing in the platform is told the upload
finished (ADR-13: the client PUTs straight to the store), so the worker checks every 5,000 ms.

`psql` is used here and nowhere else in this document, because **there is no published surface
that answers "has the worker run yet"** — a client learns it by reading the message again, which
is what §4 does. The journey suite uses §4's method; this step exists so a reader can see the
transition directly.

## 4 · What the recipient sees

```bash
curl -s "localhost:4000/v1/channels/$CID/messages?limit=10" -H "authorization: Bearer $CREDENTIAL" \
  | python3 -m json.tool | head -22
```

**Expected**: one message, and its attachment now reads

```json
{ "type": "media", "media_id": "…", "state": "ready",
  "thumbnail": { "media_id": "…", "width": 320, "height": 240 } }
```

**The thumbnail's id arrives unasked.** It is the only place the platform hands out a media id
that no message names, and §6 is what a client would do with it.

## 5 · The bytes

```bash
LINK=$(curl -s "localhost:4000/v1/media/$MEDIA" -H "authorization: Bearer $CREDENTIAL")
printf '%s' "$LINK" | python3 -c 'import sys,json;print(json.load(sys.stdin)["url"])' \
  | xargs curl -sS -o /tmp/got-4-17.png -w 'GET %{http_code}  %{size_download} bytes\n'
cmp /tmp/relay-4-17.png /tmp/got-4-17.png && echo "IDENTICAL to what was uploaded"
```

**Expected**: `GET 200  447377 bytes`, then `IDENTICAL`.

## 6 · The thumbnail, which no message names

```bash
export THUMB=$(psql postgres://relay:relay@localhost:15432/relay -tAc \
  "select id from media_objects where parent_id='$MEDIA'" | head -1 | tr -d ' ')
curl -s -o /tmp/t.json -w 'thumbnail link -> %{http_code}\n' \
  "localhost:4000/v1/media/$THUMB" -H "authorization: Bearer $CREDENTIAL"
python3 -c 'import json;print(json.load(open("/tmp/t.json"))["url"])' \
  | xargs curl -sS -o /tmp/thumb.webp -w '%{size_download} bytes\n'
```

**Expected**: `200`, then **30,612 bytes** against the parent's 480,813. A rendition is named by
no message and is reachable anyway, because 4.15 made its reachability its parent's — the
composite key, not a second predicate.

(In the journey suite the id comes from §4's payload, not from `psql`. It is read from the
database here only so this section can be run on its own.)

## 7 · Break it: stop the worker

**`$MEDIA2` WAS USED HERE TWICE AND SET NOWHERE** until the analysis pass caught it. That is
4.12's defect word for word — *"§3 used `$OBJECT_KEY` with nothing setting it"* — in the
quickstart of the chapter two after the one that recorded it, and it fails quietly: `psql`
queries `id=''` and `curl` fetches `/v1/media/`. The slot is taken here instead of being
referred to.

```bash
RELAY_POSTGRES_PORT=15432 docker compose --profile services stop media-worker

SLOT2=$(curl -sX POST localhost:4000/v1/media -H "authorization: Bearer $CREDENTIAL" \
  -H 'content-type: application/json' \
  -d "{\"filename\":\"noworker.png\",\"mime_type\":\"image/png\",\"bytes\":$BYTES}")
export MEDIA2=$(printf '%s' "$SLOT2" | python3 -c 'import sys,json;print(json.load(sys.stdin)["media_id"])')
printf '%s' "$SLOT2" | python3 -c 'import sys,json;print(json.load(sys.stdin)["upload_url"])' \
  | xargs -I{} curl -sS -X PUT --data-binary @/tmp/relay-4-17.png {} -o /dev/null -w 'PUT %{http_code}\n'

sleep 20
echo "state: $(psql postgres://relay:relay@localhost:15432/relay -tAc "select state from media_objects where id='$MEDIA2'")"
curl -s -o /dev/null -w 'link -> %{http_code}\n' "localhost:4000/v1/media/$MEDIA2" -H "authorization: Bearer $CREDENTIAL"
RELAY_POSTGRES_PORT=15432 docker compose --profile services start media-worker
```

**Expected**: `pending`, for ever, and the link answers **404 `not_found`** — the same answer as
for an id nobody has. **A stopped worker and an object that never existed are indistinguishable
from outside**, which is 4.12's refusal working as designed and is the reason this chapter's
suite must fail on a condition rather than observe a state.

## 8 · What this cannot show

- **A rendering.** FR-MED-09 says a rejected attachment *renders* as a marker; this repository
  has no client and FR-MED-14's reference client is P4 and unbuilt. The state reaching a
  recipient is the whole of what can be demonstrated.
- **The metering.** 4.16's records travel through a process no deployment starts (050-8), so
  they are deliberately not in this walk.
- **Scale.** One image. The lane holds 6,535 media objects and four above the thumbnail bound.
