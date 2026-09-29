# Quickstart — chapter 4.15

Prove the chapter against a running stack: an image that gains a thumbnail, an image already
small enough that it does not, a rendition that nobody can address directly, and a parent whose
deletion takes its rendition with it.

**NOT YET RUN. This is a plan-time draft.** Every quickstart in this series has been wrong at
plan time — six times in 4.14, five in 4.11, three in 4.12 — and each was a fixture fault that
read as a platform defect. Running it is a task in phase 8, and the corrections go here with
what each wrong version looked like. Saying it is verified before it has been run is the one
failure this document cannot recover from.

The corrections earlier chapters already earned are applied below rather than rediscovered:

- the api is on **port 4000**;
- a channel takes `{external_id, type}`, a slot takes `{filename, mime_type, bytes}`, and
  neither takes `idem_key` — that is the socket frame's field;
- the seeder's credential is an **application** credential, so every send names a bot, and
  `outside-bot` exists in the demo tenant where `demo-bot` does not;
- the worker credential is `rk_svc_local_development_worker_000000`;
- `psql -tAc` with `RETURNING` prints the value **and** the command tag, so `head -1` first;
- `uuidgen` is not on this machine; `/proc/sys/kernel/random/uuid` needs nothing installed;
- every variable a later step reads is assigned by an earlier one.

**And this chapter needs a decodable image, which no earlier quickstart did.** 4.14 uploaded
the eight bytes `\x89PNG\r\n\x1a\n` — a signature, not an image. A thumbnail needs pixels, and
an eight-byte file produces `unsupported_source` rather than a thumbnail. Step 1 writes a real
PNG with `node:zlib`, which is the same thing `services/media-worker/src/fixtures.ts` does.
PNG and GIF are the two formats whose fixtures a decoder actually accepts — measured, after an
earlier draft of this sentence said PNG alone — and PNG is the one a reader can write here in
twelve lines without an encoder.

## 0 · Prerequisites

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
pnpm build
DATABASE_URL=postgres://relay:relay@localhost:15432/relay node services/api/dist/db/migrate.js
RELAY_POSTGRES_PORT=15432 docker compose --profile services build
RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d --wait
export CREDENTIAL=$(RELAY_POSTGRES_PORT=15432 node scripts/seed-demo-tenant.mjs)
export WORKER=rk_svc_local_development_worker_000000
```

**Stop the composed services again before `pnpm test:integration`** — a second set of relays on
the same `outbox` turns invariant 8 red (`gaps.md` 057-5).

**`docker compose --profile services build` is a third thing that can be stale** (4.11): the
worker's image is what gains `sharp`, and a `pnpm build` does not rebuild it. If the worker's
boot line does not name a libvips version, the image is old.

## 1 · An image large enough to be worth shrinking

```bash
node -e '
const z=require("node:zlib"), fs=require("node:fs");
const W=800,H=600, raw=Buffer.alloc(H*(1+W*3));
for(let y=0;y<H;y++){const o=y*(1+W*3); raw[o]=0;
  for(let x=0;x<W;x++){const p=o+1+x*3; raw[p]=(x*7)&255; raw[p+1]=(y*5)&255; raw[p+2]=((x^y)*3)&255;}}
const chunk=(t,d)=>{const l=Buffer.alloc(4);l.writeUInt32BE(d.length);
  const b=Buffer.concat([Buffer.from(t),d]); const c=Buffer.alloc(4);
  c.writeUInt32BE(z.crc32?z.crc32(b):require("node:zlib").crc32(b)); return Buffer.concat([l,b,c]);};
const ihdr=Buffer.alloc(13); ihdr.writeUInt32BE(W,0); ihdr.writeUInt32BE(H,4);
ihdr[8]=8; ihdr[9]=2; 
fs.writeFileSync("/tmp/relay-4-15.png", Buffer.concat([
  Buffer.from([0x89,0x50,0x4e,0x47,0x0d,0x0a,0x1a,0x0a]),
  chunk("IHDR",ihdr), chunk("IDAT",z.deflateSync(raw)), chunk("IEND",Buffer.alloc(0))]));
console.log("wrote", fs.statSync("/tmp/relay-4-15.png").size, "bytes");'
export BYTES=$(stat -c%s /tmp/relay-4-15.png)
```

**Measured, and this is the one step of this draft that has been run**: `wrote 447377 bytes`,
which `sharp` reads back as `800x600 png` and turns into an 18,090 B WebP at 320×240. The first
draft of this line said *"roughly 1.4 MB"* from the raw pixel count and was wrong by 3×, because
a smooth pattern deflates well — the kind of guess that becomes a quickstart correction three
chapters later. **If `z.crc32` is undefined** the expression throws rather than writing a corrupt
PNG, which is the point of the guard; Node gained `zlib.crc32` in 22.2 and this machine runs
22.23.2.

## 2 · Upload it and let the worker look

```bash
export CHANNEL=$(curl -sX POST localhost:4000/v1/channels \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d '{"external_id":"thumbnails-qs","type":"public","name":"thumbnails"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')

SLOT=$(curl -sX POST localhost:4000/v1/media \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d "{\"filename\":\"big.png\",\"mime_type\":\"image/png\",\"bytes\":$BYTES}")
export MEDIA=$(printf '%s' "$SLOT" | python3 -c 'import sys,json;print(json.load(sys.stdin)["media_id"])')
export PUT_URL=$(printf '%s' "$SLOT" | python3 -c 'import sys,json;print(json.load(sys.stdin)["upload_url"])')
curl -sS -X PUT --data-binary @/tmp/relay-4-15.png "$PUT_URL" -o /dev/null -w '%{http_code}\n'

curl -sX POST "localhost:4000/v1/channels/$CHANNEL/messages" \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d "{\"user\":\"outside-bot\",\"text\":\"a big one\",\"attachments\":[{\"type\":\"media\",\"media_id\":\"$MEDIA\"}]}"
```

**Expected after the sweep picks it up** (the worker polls; give it one interval): history shows
the attachment `ready` **with a `thumbnail`**:

```text
[{"type":"media","media_id":"…","state":"ready",
  "thumbnail":{"media_id":"…","width":320,"height":240}}]
```

**A `state":"ready"` with no `thumbnail` is this chapter's first failure.** Ask in this order,
because three of these look identical from the client: did the worker's image get rebuilt with
`sharp`; did the worker reach the store; did generation fail and record a reason —

```bash
RELAY_POSTGRES_PORT=15432 psql postgres://relay:relay@localhost:15432/relay -tAc \
  "select state, rendition_failed_reason from media_objects where id = '$MEDIA'"
```

## 3 · An image already inside the bound gets nothing

This is the measured rule from `research.md` R2 — at or below 320 px a rendition is 97.3% of the
parent and identical to it, so there is none.

Repeat step 1 with `W=200,H=150`, upload it the same way, and read the attachment back.

**Expected**: `"state":"ready"` with **no `thumbnail` key at all**, and
`rendition_failed_reason` **null** — because nothing failed. A `rendition_failed_reason` of
`unsupported_source` here would mean the bound was implemented as a refusal rather than as a
decision not to bother.

## 4 · The rendition is not addressable on its own

```bash
export THUMB=$(RELAY_POSTGRES_PORT=15432 psql postgres://relay:relay@localhost:15432/relay -tAc \
  "select id from media_objects where parent_id = '$MEDIA'" | head -1 | tr -d ' ')
echo "thumb=$THUMB"

# through the parent's channel: a signed URL
curl -s -o /dev/null -w '%{http_code}\n' "localhost:4000/v1/media/$THUMB" \
  -H "authorization: Bearer $CREDENTIAL"

# and the control — an id no object has, which must answer identically
curl -s "localhost:4000/v1/media/$(cat /proc/sys/kernel/random/uuid)" \
  -H "authorization: Bearer $CREDENTIAL"
```

**Expected**: the first answers 200 for a credential that may read the channel. The second is
the refusal, and **the interesting comparison is against a rendition whose parent the caller
may not read** — same body, same code, differing only in `request_id`. A separate tenant's
credential is what makes that test honest, and it is `rendition-delivery.itest.ts`'s job
rather than a curl's.

## 5 · The parent goes and the rendition goes with it

```bash
RELAY_POSTGRES_PORT=15432 psql postgres://relay:relay@localhost:15432/relay -tAc \
  "select count(*) from media_objects where id = '$MEDIA' or parent_id = '$MEDIA'"
# expect 2

RELAY_POSTGRES_PORT=15432 psql postgres://relay:relay@localhost:15432/relay -tAc \
  "delete from media_objects where id = '$MEDIA'" | head -1

RELAY_POSTGRES_PORT=15432 psql postgres://relay:relay@localhost:15432/relay -tAc \
  "select count(*) from media_objects where id = '$MEDIA' or parent_id = '$MEDIA'"
# expect 0 — the cascade
```

**Expected**: 2, then 0. **This proves the database half only, and a raw `DELETE` is the only
way to prove even that** — nothing in this platform deletes a `media_objects` row. The rejection
path deletes bytes and keeps the row on purpose, so `ON DELETE CASCADE` is correct and dormant
until the erasure chapter writes the first row deletion.

The store half is not a cascade at all: the bytes are still in MinIO after the `DELETE` above,
and the function that removes both keys is written here with no caller. That asymmetry is the
chapter's `TRAP` box, and it is why SC-006 lists the store rather than querying the database.

## 6 · What this cannot show

- **The reaper**, because it is not built (R4). The exclusion predicate is exercised by a test
  with a stand-in caller, not by a job.
- **The video half**, because it is not built (R8) and the SRS says so.
- **A photograph.** Every figure this chapter publishes comes from synthetic images or from six
  files of convenience, and says which.
