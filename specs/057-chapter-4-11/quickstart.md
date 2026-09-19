# Quickstart — chapter 4.11

Prove the chapter end to end against a running stack: a slot, an upload, a message that attaches
it, and the three refusals that look alike.

## Prerequisites

The stack, on this machine's documented ports — **`RELAY_POSTGRES_PORT=15432`**, because the host
holds 5432:

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait postgres redis nats clickhouse minio mailpit
pnpm build
node services/api/dist/db/migrate.js
```

MinIO publishes **9100**, not its conventional 9000 — ClickHouse's native port has held 9000 since
chapter 1.2, and the two cannot both bind it.

## 1 · The accept path

```bash
# a slot, then the upload, then the message
curl -s -X POST localhost:4000/v1/media \
  -H "authorization: Bearer $USER_TOKEN" -H 'content-type: application/json' \
  -d '{"filename":"holiday.jpg","mime_type":"image/jpeg","bytes":2097152}'
# → 201 { "media_id": "…", "state": "pending", "upload_url": "…", "expires_at": "…" }

curl -s -X PUT "$UPLOAD_URL" --data-binary @holiday.jpg -o /dev/null -w '%{http_code}\n'
# → 200, and no byte of it reached the api

curl -s -X POST "localhost:4000/v1/channels/$CHANNEL/messages" \
  -H "authorization: Bearer $USER_TOKEN" -H 'content-type: application/json' \
  -d "{\"text\":\"look\",\"attachments\":[{\"type\":\"media\",\"media_id\":\"$MEDIA_ID\"}]}"
# → 201
```

**Expected**: the message is created and reading it back returns the attachment as sent. The object
is still `pending` — nothing has verified it, and nothing will until movement VI.

## 2 · The three refusals look the same

Run all three and diff the bodies with `request_id` stripped. They must be identical.

```bash
for ID in "$OTHER_TENANTS_MEDIA" "$OTHER_USERS_MEDIA" "$(uuidgen)"; do
  curl -s -X POST "localhost:4000/v1/channels/$CHANNEL/messages" \
    -H "authorization: Bearer $USER_TOKEN" -H 'content-type: application/json' \
    -d "{\"text\":\"x\",\"attachments\":[{\"type\":\"media\",\"media_id\":\"$ID\"}]}" \
  | jq 'del(.request_id)'
done
```

**Expected**: three identical 422 bodies. Anything that distinguishes them is an existence oracle
(SC-002).

## 3 · A malformed id is a different failure

```bash
curl -s -X POST "localhost:4000/v1/channels/$CHANNEL/messages" \
  -H "authorization: Bearer $USER_TOKEN" -H 'content-type: application/json' \
  -d '{"text":"x","attachments":[{"type":"media","media_id":"not-a-uuid"}]}' | jq .code
```

**Expected**: `invalid_request`, 400, `field: "attachments.0.media_id"`. **Not** a 500 — research
R3 measured that the looser schema sends `invalid input syntax for type uuid` to the driver and
the filter answers `internal_error`.

## 4 · The state the clause names and the database refuses

```bash
psql "postgres://relay:relay@localhost:15432/relay" -c \
  "INSERT INTO media_objects (id, environment_id, filename, mime_type, declared_bytes, object_key, state)
   SELECT gen_random_uuid(), id, 'p.png', 'image/png', 1, 'p/k', 'ready' FROM environments LIMIT 1;"
```

**Expected**: `violates check constraint "media_objects_state_check"`. That refusal is the
chapter's evidence that FR-MED-06's `ready` arm cannot be exercised, and it is quoted rather than
worked around.

## 5 · A refused send leaves nothing behind

```bash
psql "postgres://relay:relay@localhost:15432/relay" -tAc \
  "SELECT count(*), coalesce(max(sequence), 0) FROM messages WHERE channel_id = '$CHANNEL'"
# run a refusal from §2, then the same query
```

**Expected**: both figures unchanged. Scoped to this channel — a whole-table count is a
neighbour's problem in a lane that runs two files at a time.

## The gates

```bash
cd relay-platform && pnpm lint && pnpm typecheck && pnpm test
pnpm test:integration                      # 12 of 12 tasks
cd ../relay-tutorial
pnpm check:errors                          # both directions, after the code is removed
pnpm check:fences 2>&1 | grep 'problem(s)\|replay onto'
```

**`check:errors` is the one no CI job runs** (`gaps.md` 055-3), and this chapter both removes a
code and adds one. Run it by hand, in both directions, and read its counted line rather than its
exit code.
