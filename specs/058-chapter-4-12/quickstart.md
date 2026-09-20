# Quickstart — chapter 4.12

Prove the chapter against a running stack: a URL that fetches the bytes, three refusals that
look alike, and an expiry the store enforces from its own clock.

**Every command below was run, against the composed stack, on 2026-09-20.** It was wrong three
times and every correction is recorded where it happened rather than quietly applied:

  1. §2's foreign object came back as the string `INSERT00` on a stack where a `production`
     environment already existed. The `WITH … ON CONFLICT DO NOTHING RETURNING id` CTE returns
     no rows on a second run, so the outer INSERT inserted nothing and `psql` printed its
     command tag, which `tr -d '[:space:]'` turned into an identifier. **It answered 400 rather
     than the 404 the step claims — and before this chapter it would have answered 500**, which
     is the very class §5 measures.
  2. `psql -tAc` with `RETURNING` prints the value **and** the command tag, so `tr` alone glues
     them: `661e39fd-…-224d381ba807INSERT01`. `head -1` is the fix. 4.11 paid the smaller
     version of this — a newline `tr -d ' '` does not strip.
  3. §3 used `$OBJECT_KEY` and nothing set it.

And `pnpm test:outsider` takes three variables the step did not name.

## Prerequisites

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
pnpm build
DATABASE_URL=postgres://relay:relay@localhost:15432/relay node services/api/dist/db/migrate.js
RELAY_CLICKHOUSE_HOST=localhost node analytics/apply.mjs
RELAY_POSTGRES_PORT=15432 docker compose --profile services build
RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d --wait
```

**`up -d --wait` with no service list starts the stores and nothing else** — `api`, `gateway` and
`dispatcher` carry `profiles: ["services"]`, so the second pair of commands is what answers
`localhost:4000`. And **stop them again before running `pnpm test:integration`**: the composed
stack is a second set of relays on the same `outbox` and turns invariant 8 red (`gaps.md` 057-5).

## 0 · The credential, which is an application credential

```bash
export CREDENTIAL=$(RELAY_POSTGRES_PORT=15432 node scripts/seed-demo-tenant.mjs)
export CHANNEL=$(curl -s -X POST localhost:4000/v1/channels \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d '{"external_id":"quickstart-412","type":"public"}' | jq -r .id)
curl -s -o /dev/null -X POST localhost:4000/v1/users \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d '{"users":[{"external_id":"qs-bot","kind":"bot","description":"sends the quickstart messages"}]}'
```

**It is not a user token**, which 4.11's quickstart learned by answering 400 six times. An
application credential may send only as a bot, hence the third command. And **re-running the
seeder does not give you a second tenant** — it reuses the existing demo environment and mints a
new credential in it, so an object obtained that way is yours and the send answers 201.

## 1 · A URL, and the bytes

```bash
SLOT=$(curl -s -X POST localhost:4000/v1/media \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d '{"filename":"holiday.jpg","mime_type":"image/jpeg","bytes":11}')
MEDIA_ID=$(jq -r .media_id <<<"$SLOT")
printf 'hello world' > holiday.jpg
curl -s -X PUT "$(jq -r .upload_url <<<"$SLOT")" --data-binary @holiday.jpg -o /dev/null -w 'PUT -> %{http_code}\n'

curl -s -o /dev/null -w 'send -> %{http_code}\n' -X POST "localhost:4000/v1/channels/$CHANNEL/messages" \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d "{\"text\":\"look\",\"user\":\"qs-bot\",\"attachments\":[{\"type\":\"media\",\"media_id\":\"$MEDIA_ID\"}]}"

DELIVERY=$(curl -s "localhost:4000/v1/media/$MEDIA_ID" -H "authorization: Bearer $CREDENTIAL")
curl -s "$(jq -r .url <<<"$DELIVERY")"
```

**Expected**: `hello world`. The bytes come from the store and never touch the api — the same
claim the upload makes, in reverse, and the api's own request log is where it is checked.

## 2 · The three refusals look the same

A genuinely foreign object needs a second environment, which no published route creates. An
application holds one environment per `kind` (`unique (application_id, kind)`), so the second is
the `production` half of the same application:

```bash
psql "postgres://relay:relay@localhost:15432/relay" -tAc "
  INSERT INTO environments (id, application_id, kind, signing_secret)
  SELECT gen_random_uuid(), application_id, 'production', signing_secret
    FROM environments WHERE kind = 'development' LIMIT 1
  ON CONFLICT DO NOTHING" > /dev/null

FOREIGN=$(psql "postgres://relay:relay@localhost:15432/relay" -tAc "
  INSERT INTO media_objects
    (id, environment_id, filename, mime_type, declared_bytes, object_key, state)
  SELECT gen_random_uuid(), id, 'f.png', 'image/png', 1, 'f/k', 'pending'
    FROM environments WHERE kind = 'production' LIMIT 1
  RETURNING id" | head -1 | tr -d '[:space:]')

UNREFERENCED=$(jq -r .media_id <<<"$(curl -s -X POST localhost:4000/v1/media \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d '{"filename":"orphan.png","mime_type":"image/png","bytes":1}')")

for ID in "$FOREIGN" "$UNREFERENCED" "$(cat /proc/sys/kernel/random/uuid)"; do
  curl -s "localhost:4000/v1/media/$ID" -H "authorization: Bearer $CREDENTIAL" | jq 'del(.request_id)'
done
```

**Expected**: three identical `404 not_found` bodies. **The middle one is this chapter's own
finding** — an object the caller's own tenant owns, that the caller's own credential uploaded,
and which no message references. `research.md` R1 settles it: authorisation follows the message,
there is no message, and granting the uploader access would be the parallel ACL the clause's own
note forbids.

**Two statements, not one CTE, and `head -1` after the `RETURNING`.** Creating the environment
separately is what makes the step idempotent: a `RETURNING` inside `ON CONFLICT DO NOTHING`
yields nothing on a second run, and the outer INSERT then inserts nothing. And `psql -tAc` prints
the command tag underneath the value, so `tr` alone produces
`661e39fd-…-224d381ba807INSERT01` — a malformed id, which this route answers **400
`invalid_request`** and every other route in the api answers **500**.

`uuidgen` is not on every machine and is not on this one; `/proc/sys/kernel/random/uuid` needs
nothing installed.

## 3 · The expiry is the store's, not ours

```bash
MEDIA_ID=${MEDIA_ID:?run §1 first}
OBJECT_KEY=$(psql "postgres://relay:relay@localhost:15432/relay" -tAc \
  "select object_key from media_objects where id='$MEDIA_ID'" | head -1 | tr -d '[:space:]')

node -e '
const { presign } = await import("./services/api/dist/media/presign.js");
console.log(presign({ method: "GET", endpoint: "http://localhost:9100", bucket: "relay-media",
  key: process.argv[1], accessKey: "relay", secretKey: "relay-secret",
  expiresIn: 1, now: new Date(Date.now() - 10_000) }));' "$OBJECT_KEY" > /tmp/expired.txt
curl -s -o /dev/null -w 'expired -> %{http_code}\n' "$(cat /tmp/expired.txt)"
```

**Expected**: `403`, and the body says `Request has expired`. Signed ten seconds in the past with
a one-second life, so the refusal comes from **the store's clock** rather than from anything
Relay decided — the same method 4.10 used for the upload slot.

## 4 · What the index is worth

```bash
psql "postgres://relay:relay@localhost:15432/relay" -c "
  EXPLAIN (ANALYZE, BUFFERS) SELECT m.id, m.channel_id FROM messages m
   WHERE m.attachments @> '[{\"type\":\"media\",\"media_id\":\"$(cat /proc/sys/kernel/random/uuid)\"}]'::jsonb"
```

**Measured**, once `0017` has run: `Bitmap Index Scan on messages_attachments_gin`, **18
buffers**, no `Rows Removed by Filter`. Before it: `Seq Scan`, **68,112 rows removed and 1,042
buffers** for an id that matches nothing.

**AND THIS IS NOT THE QUERY THE ROUTE SENDS.** It is the bare containment scan, which is where the
index earns its keep and where the sentence *"the refusal is the expensive case"* is true — a hit
can stop early and a miss cannot. The route's own lookup is scoped to one tenant and is a
different measurement entirely: 86 buffers as a single joined query with this index idle, 20 as
the two the route actually issues. `baseline.txt` T005 and T013 carry the table, and the chapter
publishes it beside chapter 4.1's opposite conclusion.

## The gates

```bash
cd relay-platform && pnpm lint && pnpm typecheck && pnpm test
pnpm test:integration                      # composed services STOPPED
RELAY_DEMO_CREDENTIAL=$CREDENTIAL RELAY_API_URL=http://localhost:4000 \
  RELAY_WS_URL=ws://localhost:4001 pnpm test:outsider    # the sealed suite
cd ../relay-tutorial
pnpm check:errors                           # expect 34 codes, 34 sections — UNCHANGED
pnpm check:fences 2>&1 | grep 'problem(s)\|replay onto'
```

**`check:errors` is expected not to move**, which is the unusual half. This chapter adds a route
and no vocabulary, so 34/34 at the close is an assertion rather than a formality — and it is a
script no CI job runs (`gaps.md` 055-3), so by hand is the only way it gets run at all.
