# Quickstart — chapter 4.14

Prove the chapter against a running stack: a placeholder that resolves while a client watches,
the same object resolving on two channels at once, a verdict that announces nothing because
nobody attached the object, and a client that never receives a frame and is still right.

**EVERY COMMAND HERE WAS RUN AGAINST THE COMPOSED STACK BEFORE THIS LINE WAS WRITTEN**, in the
order they appear — which is NFR-USE-03's whole verification, since `ci.yml` contains the word
`quickstart` zero times. **It was wrong six times**, and every one was a fixture fault that
would have read as a platform defect:

1. **The api is on port 4000, not 3000.** Every step said 3000 and answered
   `Failed to connect`. The plan-time draft inherited the number from nowhere.
2. **A channel takes `{external_id, type}`**, not `{name, visibility}` —
   `Invalid input: expected string, received undefined`, which names no field.
3. **A slot takes `{filename, mime_type, bytes}`**, not `{kind, …}`. The wrong shape
   answers **`internal_error`, a 500** — a caller-triggered one, which is `gaps.md`
   058-3's class arriving on a route that does validate its path parameter.
4. **`idem_key` is the socket frame's field, not the REST body's** —
   `Unrecognized key: "idem_key"`.
5. **The sender must exist in the demo tenant.** `demo-bot` does not;
   `outside-bot` does. `the sender named in \`user\` is not a user of this
   environment`.
6. **The worker credential is `rk_svc_local_development_worker_000000`**, which
   `compose.yaml` defaults it to. Without it every verdict is a 401 and the producer
   under test is never reached — 4.9's finding, and the second time this feature met it.

The corrections the last three chapters earned are already applied below rather than
rediscovered:

- the credential comes from the seeder and **it is an application credential**, so every send
  names a bot;
- **re-running the seeder reuses the demo tenant** rather than making a second one;
- `psql -tAc` with `RETURNING` prints the value **and** the command tag, so `head -1` before
  `tr`;
- `uuidgen` is not on this machine — `/proc/sys/kernel/random/uuid` needs nothing installed;
- every variable a later step reads is assigned by an earlier one, and no step is an ellipsis.

## 0 · Prerequisites

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
pnpm build
DATABASE_URL=postgres://relay:relay@localhost:15432/relay node services/api/dist/db/migrate.js
RELAY_POSTGRES_PORT=15432 docker compose --profile services build
RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d --wait
export CREDENTIAL=$(RELAY_POSTGRES_PORT=15432 node scripts/seed-demo-tenant.mjs)
```

**Stop the composed services again before `pnpm test:integration`** — a second set of relays on
the same `outbox` turns invariant 8 red (`gaps.md` 057-5).

**This chapter needs the media worker running**, because the event fires on a verdict and only
the worker produces verdicts. A stack whose worker cannot reach the scanner leaves every object
`pending` and **that is FR-009 working**, indistinguishable from an object nobody uploaded to
(4.13's own finding). The boot line names the scanner's version; read it.

## 1 · A channel, an upload slot, and a message

Take a slot, PUT the bytes, and attach the object while it is still `pending` — which FR-MED-06
permits and which is the whole point of the chapter.

```bash
export CHANNEL=$(curl -sX POST localhost:4000/v1/channels \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d '{"external_id":"placeholders-qs","type":"public","name":"placeholders"}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
echo "channel=$CHANNEL"
```

Then a slot, the PUT, and a send naming a bot (an application credential has no user):

```bash
SLOT=$(curl -sX POST localhost:4000/v1/media \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d '{"filename":"p.png","mime_type":"image/png","bytes":70}')
export MEDIA=$(printf '%s' "$SLOT" | python3 -c 'import sys,json;print(json.load(sys.stdin)["media_id"])')
export PUT_URL=$(printf '%s' "$SLOT" | python3 -c 'import sys,json;print(json.load(sys.stdin)["upload_url"])')
printf '\x89PNG\r\n\x1a\n' > /tmp/relay-4-14.png
curl -sS -X PUT --data-binary @/tmp/relay-4-14.png "$PUT_URL" -o /dev/null -w '%{http_code}\n'

curl -sX POST "localhost:4000/v1/channels/$CHANNEL/messages" \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d "{\"user\":\"outside-bot\",\"text\":\"a photo\",\"attachments\":[{\"type\":\"media\",\"media_id\":\"$MEDIA\"}]}"
```

**Measured.** The send response and history both answer:

```text
[{"type": "media", "media_id": "bb3c9338-…", "state": "pending"}]
```

**Expected**: the send returns 201 and the message's attachment reads `"state": "pending"`.
**A `state` that is absent is this chapter's first failure** and means the delivery schema was
changed and a door was not.

## 2 · Watch the placeholder resolve

Open a socket subscribed to `$CHANNEL` before the worker picks the object up.

```bash
export WORKER=rk_svc_local_development_worker_000000
docker compose exec -T redis redis-cli psubscribe 'revision:*' &
curl -sS -X POST "localhost:4000/internal/media/$MEDIA/verdict" \
  -H "authorization: Bearer $WORKER" -H 'content-type: application/json' \
  -d '{"verdict":"ready","verified_bytes":8,"verified_type":"image/png"}'
```

**Measured.** The verdict answers `{"applied":true,"state":"ready"}` and the subscription sees:

```text
revision:0fd39943-…
{"kind":"media","media_id":"bb3c9338-…","channel":"0fd39943-…","state":"ready"}
```

and history, read again, now answers `"state": "ready"` for the same message — **with no request
issued by the client between the send and the frame**, which is SC-001 and the chapter's title.

**If the frame never arrives**, ask in this order, because three of these look identical from
the client: is the worker running; can it reach the scanner (`zVERSION`, third field); did the
verdict apply (`applied: true`); and did `channelsReferencingMedia` return this channel.

## 3 · The same object on two channels

Forward the message to a second channel so one object is referenced twice, then verify a second
object attached in both.

**Expected**: **two** frames, one per channel, for one verdict. This is the case the lane says
is real rather than theoretical — **44 objects on the development lane are referenced from two
channels** — and a fan-out written for N = 1 is correct on 97% of it.

## 4 · The two cases that must announce nothing

```bash
# (a) a slot taken and never attached, then verified
SLOT_B=$(curl -sX POST localhost:4000/v1/media \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d '{"kind":"image","mime_type":"image/png","bytes":70}')
export MEDIA_B=$(printf '%s' "$SLOT_B" | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')
curl -sS -X PUT --data-binary @/tmp/relay-4-14.png \
  "$(printf '%s' "$SLOT_B" | python3 -c 'import sys,json;print(json.load(sys.stdin)["upload_url"])')" \
  -o /dev/null -w '%{http_code}\n'

# (b) the second verdict for $MEDIA, which §2 already drove to a terminal state
RELAY_POSTGRES_PORT=15432 docker compose exec -T postgres \
  psql -U relay -d relay -tAc "select id, state from media_objects where id = '$MEDIA'"
```

**Expected (a)**: the verdict succeeds and **no frame is published anywhere**. This is the
common path, not an edge: **4,725 of 5,403 objects on the lane are unreferenced.**

**Expected (b)**: the compare-and-set reports `applied: false` and **no frame is published**.
A frame here would mean the producer hangs off the request rather than the transition.

## 5 · The client that gets no frame and is still right

Attach an object that is **already** `ready`. No transition remains, so no frame can ever fire.

**Expected**: the send response and history both read `"state": "ready"`. A client that never
receives an event reports the correct state — SC-006, and the reason the state on the
attachment is the mechanism and the frame is the optimisation.

**538 of the 1,589 referenced objects on the lane are already terminal**, so this is not a
contrived case; it is a third of them.

## 6 · The refusal

A non-member of a **private** referencing channel receives no frame, and a caller from another
environment receives nothing at all.

**Expected**: zero frames on both. Note the direction: real-time delivery reaches channel
*subscribers*, which is a subset of those *authorised to read* under FR-MED-08 — a non-member
of a **public** channel is authorised and will not be subscribed. **That is the safe direction**
and history is their repair (R5). Do not "fix" it by broadcasting wider.

## What this quickstart does not prove

- **That a rejection renders as a rejection marker.** FR-MED-09 is the milestone chapter's.
- **That the state is right under load.** Every figure here is one lane.
- **That the frame is delivered exactly once.** The platform's channel-frame guarantee is what
  it always was, and a client that misses one repairs from history — which §5 is the proof of.
