# Quickstart — chapter 4.13

Prove the chapter against a running stack: an image that becomes `ready`, a lie that becomes
`rejected`, a virus that becomes `rejected`, and a scanner that is down leaving the object
alone.

**Not yet run.** This file may not say *"every command here was run before it was written"*
until its own task does. 4.11's quickstart was wrong five times and **four of the five produced
a red that looked like a platform defect**; 4.12's was wrong three times and the first of them
was that chapter's own subject. The corrections both earned are already applied below rather
than rediscovered:

- the credential comes from the seeder and **it is an application credential**, so every send
  names a bot;
- **re-running the seeder reuses the demo tenant** rather than making a second one;
- `psql -tAc` with `RETURNING` prints the value **and** the command tag, so `head -1` before
  `tr`;
- `uuidgen` is not on this machine — `/proc/sys/kernel/random/uuid` needs nothing installed.

## Prerequisites

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
pnpm build
DATABASE_URL=postgres://relay:relay@localhost:15432/relay node services/api/dist/db/migrate.js
RELAY_POSTGRES_PORT=15432 docker compose --profile services build
# and 0018 is one-way once anything reaches a terminal state: restoring the narrow
# CHECK answers `is violated by some row` until the ready and rejected rows are gone.
# ADR-16 makes migrations forward-only, so this is a property — but it is the first
# thing a local rollback meets.
RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d --wait
```

**`up -d --wait` with no service list starts the stores and nothing else** — `api`, `gateway`
and `dispatcher` carry `profiles: ["services"]`. **Stop them again before `pnpm test:integration`**:
the composed stack is a second set of relays on the same `outbox` and turns invariant 8 red
(`gaps.md` 057-5).

**And the scanner is a store now.** Whether `clamav` joins the default profile or the services
one is plan open question 4; whichever it is, `packages/config/src/infra.ts` must agree with
`compose.yaml` **in both directions** — the assertion chapter 4.10 tripped over when it added
the sixth container and not the registry entry.

## 0 · The credential and a channel

```bash
export CREDENTIAL=$(RELAY_POSTGRES_PORT=15432 node scripts/seed-demo-tenant.mjs)
export CHANNEL=$(curl -s -X POST localhost:4000/v1/channels \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d '{"external_id":"quickstart-413","type":"public"}' | jq -r .id)
curl -s -o /dev/null -X POST localhost:4000/v1/users \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d '{"users":[{"external_id":"qs-bot","kind":"bot","description":"sends the quickstart messages"}]}'
```

## 1 · A real image becomes `ready`

```bash
python3 -c "
import zlib, struct
def chunk(t,d):
    c=t+d; return struct.pack('>I',len(d))+c+struct.pack('>I',zlib.crc32(c)&0xffffffff)
w,h=640,480
raw=b''.join(b'\x00'+bytes([(x*3)%256 for x in range(w*3)]) for _ in range(h))
open('holiday.png','wb').write(b'\x89PNG\r\n\x1a\n'
  +chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))
  +chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b''))
"
BYTES=$(stat -c%s holiday.png)
SLOT=$(curl -s -X POST localhost:4000/v1/media \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d "{\"filename\":\"holiday.png\",\"mime_type\":\"image/png\",\"bytes\":$BYTES}")
export MEDIA_ID=$(jq -r .media_id <<<"$SLOT")
curl -s -X PUT "$(jq -r .upload_url <<<"$SLOT")" --data-binary @holiday.png \
  -o /dev/null -w 'PUT -> %{http_code}\n'

# the worker finds it on its own — nothing tells it
until [ "$(psql "postgres://relay:relay@localhost:15432/relay" -tAc \
  "select state from media_objects where id='$MEDIA_ID'" | head -1 | tr -d '[:space:]')" = "ready" ]; do
  sleep 1
done
psql "postgres://relay:relay@localhost:15432/relay" -c \
  "select state, verified_type, verified_bytes, width, height
     from media_objects where id='$MEDIA_ID'"
```

**Expected**: `ready · image/png · <BYTES> · 640 · 480`.

**Nothing told the worker the upload happened.** That is `research.md` R1's whole finding: the
sweep costs 1.412 ms an object and the client notice would have made FR-MED-04's *"every
uploaded object"* contingent on a client choosing to send one.

## 2 · Only a `ready` object is deliverable

```bash
curl -s -o /dev/null -w 'ready  -> %{http_code}\n' \
  "localhost:4000/v1/media/$MEDIA_ID" -H "authorization: Bearer $CREDENTIAL"

PENDING=$(jq -r .media_id <<<"$(curl -s -X POST localhost:4000/v1/media \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d '{"filename":"never.png","mime_type":"image/png","bytes":1}')")
curl -s -o /dev/null -w 'pending -> %{http_code}\n' \
  "localhost:4000/v1/media/$PENDING" -H "authorization: Bearer $CREDENTIAL"
```

**Expected**: `200` then `404`. This is ADR-14's *"no signed URL until `ready`"*, which chapter
4.12 shipped the opposite of — and `research.md` R4 measured why it could not have shipped
earlier: the gate alone turns **10 of 76 tests red**, because nothing could produce `ready`.

## 3 · A lie about the bytes is rejected, and the bytes go

```bash
LIAR=$(curl -s -X POST localhost:4000/v1/media \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d '{"filename":"pic.png","mime_type":"image/png","bytes":1024}')
LIAR_ID=$(jq -r .media_id <<<"$LIAR")
head -c 40000 /dev/urandom > not-a-png.bin
curl -s -X PUT "$(jq -r .upload_url <<<"$LIAR")" --data-binary @not-a-png.bin -o /dev/null

sleep 5
psql "postgres://relay:relay@localhost:15432/relay" -c \
  "select state, rejected_reason, declared_bytes, verified_bytes
     from media_objects where id='$LIAR_ID'"
curl -s -o /dev/null -w 'the bytes -> %{http_code}\n' \
  "$(node -e '…signed HEAD for the object key…')"
```

**Expected**: `rejected · declaration_mismatch · 1024 · 40000`, and the store answers **404** to
a signed HEAD of the key. **The size half of that verdict came from the sweep's own `HEAD`** —
`content-length` is the store's count — so this object was refused without its bytes ever being
fetched for comparison. Only the scan read them, and only because T039a puts the scan first. **Both halves**, because a state change that leaves the bytes in the
store is the failure FR-MED-03 exists to prevent — and the tenant's committed bytes must fall
with them (SRS 1.17's sum over the media rows).

## 4 · EICAR is rejected by a scanner that is running

```bash
printf 'X5O!P%%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*' > eicar.bin
wc -c eicar.bin      # 68 — exactly, with no trailing newline
EICAR=$(curl -s -X POST localhost:4000/v1/media \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d '{"filename":"eicar.png","mime_type":"image/png","bytes":68}')
curl -s -X PUT "$(jq -r .upload_url <<<"$EICAR")" --data-binary @eicar.bin -o /dev/null
sleep 5
psql "postgres://relay:relay@localhost:15432/relay" -c \
  "select state, rejected_reason from media_objects
     where id='$(jq -r .media_id <<<"$EICAR")'"
```

**Expected**: `rejected · scan_failed`.

**NOT `declaration_mismatch`, AND THAT IS THE WHOLE POINT OF THE ORDER.** Those 68 bytes are not
a PNG, so under a declaration-first worker this object is refused before the scanner is asked,
and the step above would read `declaration_mismatch`. Analysis pass 1 tried to dodge that by
embedding the signature in a valid PNG and asked ClamAV through `INSTREAM`:

    EICAR alone                        68 B   Eicar-Test-Signature FOUND
    EICAR + a newline                  69 B   Eicar-Signature FOUND
    EICAR + 200 spaces                268 B   OK
    EICAR prepended to a valid PNG    422 B   OK
    EICAR appended to a valid PNG     422 B   OK

**The signature matches the file, not a substring in it.** So no object can both satisfy
FR-MED-03 and trip the scanner, and FR-MED-04's *"every uploaded object shall be
virus-scanned"* is what decides the order (`research.md` R5a). **Write the 68 bytes with no
trailing newline**: `printf` does not add one and `echo` does, and the padded file above is the
measurement showing why that matters.

**EICAR is the standard harmless string every scanner is required to detect.** A test that mocks
the scanner asserts that the mock was called; this one asserts that ClamAV was running and had
definitions — which is the distinction `research.md` R5 flags, because **a scanner with no
definitions reports clean on everything**.

## 5 · A scanner that is down leaves the object alone

```bash
docker compose stop clamav
# take a slot, upload a good image, wait past two sweep intervals
psql "postgres://relay:relay@localhost:15432/relay" -tAc "select state from media_objects where id='$ID'"
docker compose start clamav
# wait one more interval
psql "postgres://relay:relay@localhost:15432/relay" -tAc "select state from media_objects where id='$ID'"
```

**Expected**: `pending`, then `ready`. FR-009: a transient failure produces neither terminal
state, because a worker that marked an object `rejected` because the scanner was down would be
deleting a customer's photo to record an outage.

**AND THIS COMMAND TAKES A SHARED SERVICE AWAY FROM ITS NEIGHBOURS.** `docker compose stop
minio` is chapter 4.10's finding 056-5 exactly — the api lane runs two files at a time and a
suite that stops a container answers 503 in a file that never mentions it. The *test* for this
must reach the scanner through a variable it can point at a closed port; the *quickstart* may
stop the container because a person reading it is not running a lane beside it.

## 6 · What the sweep costs

```bash
psql "postgres://relay:relay@localhost:15432/relay" -tAc \
  "select state, count(*) from media_objects group by 1"
```

**And if nothing ever reaches `ready`, check the bucket before the worker.** A missing bucket
answers every object's `HEAD` with 404, which the sweep reads as *"not uploaded yet"* — measured
at analysis pass 6, and 056-10's condition, which a persisting local volume hides. The worker
probes the bucket once per sweep for that reason and says so in its log.

**And the sweep's `HEAD` is where SC-006's clock starts**: `last-modified` is the only record of
when the upload finished, at one-second resolution. The platform does not observe the PUT.

**Measured before this chapter existed**: 3,005 rows, every one `pending`, 253 with bytes —
8.4%. One signed `HEAD` is **1.412 ms** (p50 1.094, p95 1.714, n=200), so the whole backlog is
**4.2 s serial**. Publish the figure again at the close, because the population moves: chapter
4.8 watched a median shift because the feature itself changed the population.

## The gates

```bash
cd relay-platform && pnpm lint && pnpm typecheck && pnpm test
pnpm test:integration                       # composed services STOPPED
RELAY_DEMO_CREDENTIAL=$CREDENTIAL RELAY_API_URL=http://localhost:4000 \
  RELAY_WS_URL=ws://localhost:4001 pnpm test:outsider   # needs a worker in the profile
cd ../relay-tutorial
pnpm check:errors                           # expect 34 codes, 34 sections — UNCHANGED
pnpm check:fences 2>&1 | grep 'problem(s)\|replay onto'
```

**And the four gate commands need two opposite arrangements**, which the task list did not say
until analysis pass 4: `pnpm test`, `pnpm test:integration` and `pnpm check:errors` want the
composed services **stopped** (`gaps.md` 057-5), and `pnpm test:outsider` wants them **up** plus
the three variables above. Run without them it answers
`Missing: RELAY_API_URL, RELAY_WS_URL, RELAY_DEMO_CREDENTIAL` and **`Tests 19 skipped (19)`** —
a counted line that is a number and means nothing ran.

**And the sealed suite now needs a running worker.** Its media test fetches the bytes of an
object it uploaded itself, which the gate refuses until something moves it to `ready` — so this
command's preconditions include the worker being in the composed profile (plan open question 4).
Chapter 4.12's version of this suite ran against a `pending` object and passed.

**`check:errors` is expected not to move.** This chapter changes what a route refuses and adds
no vocabulary, so 34/34 is an assertion rather than a formality — and it is a script no CI job
runs (`gaps.md` 055-3), so by hand is the only way it runs at all.
