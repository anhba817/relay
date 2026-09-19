# Quickstart — chapter 4.11

Prove the chapter end to end against a running stack: a slot, an upload, a message that attaches
it, and the three refusals that look alike.

**Every command here was run before it was written**, which this file could not say until it was.
Running it found three things the reading had not: the api is not started by the prerequisite
block, the credential has no public source, and **the credential is not a user token** — see §0.

## Prerequisites

The stack, on this machine's documented ports — **`RELAY_POSTGRES_PORT=15432`**, because the host
holds 5432:

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
pnpm build
DATABASE_URL=postgres://relay:relay@localhost:15432/relay node services/api/dist/db/migrate.js
RELAY_CLICKHOUSE_HOST=localhost node analytics/apply.mjs
```

**`up -d --wait` WITHOUT A SERVICE LIST STARTS THE STORES AND NOTHING ELSE.** `api`, `gateway` and
`dispatcher` all carry `profiles: ["services"]`, so a list of store names and no list do the same
thing — and neither answers `localhost:4000`. The api is a second step:

```bash
RELAY_POSTGRES_PORT=15432 docker compose --profile services build
RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d --wait
```

`--build` is not caution: `ci.yml:298` records a run against a stale image reporting six failures,
404s for routes that exist, none of which named the cause.

**AND THE COMPOSED API ANSWERS 503 TO EVERY SLOT REQUEST UNTIL T001b LANDS.** `compose.yaml`'s
`api` names `postgres:5432`, `nats:4222`, `redis:6379` and `clickhouse` and names MinIO nowhere,
while `depends_on` waits on it — so `store.ts:18` falls back to `http://localhost:9100`, which
inside that container is that container, and FR-017's outage refusal fires permanently. Section 1
measures that first and the fix second.

MinIO publishes **9100** on the host, not its conventional 9000 — ClickHouse's native port has
held 9000 since chapter 1.2, and the two cannot both bind it. Which of the two addresses the api
signs with is T001b's decision, and the host is inside the signature.

## 0 · The credential, which has no public source

```bash
export CREDENTIAL=$(RELAY_POSTGRES_PORT=15432 node scripts/seed-demo-tenant.mjs)
export CHANNEL=$(curl -s -X POST localhost:4000/v1/channels \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d '{"external_id":"quickstart-411","type":"public"}' | jq -r .id)
curl -s -o /dev/null -X POST localhost:4000/v1/users \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d '{"users":[{"external_id":"qs-bot","kind":"bot","description":"sends the quickstart messages"}]}'
```

**IT IS AN APPLICATION CREDENTIAL AND NOT A USER TOKEN, WHICH THE FIRST DRAFT OF THIS FILE
GOT WRONG.** The variable was called `USER_TOKEN` and every send below omitted `user`; run as
written it answered **400** — *"name the sender in `user` — an application credential has no
user of its own"*. An application credential may send only as a bot (FR-007), which is why
there is a third command here. A user token is a different route (`POST /auth/dev-token`) and
a different half of FR-MED-06; §2 uses the credential's own objects, so the distinction does
not change what those refusals prove.

`ci.yml:305` says why this is a script and not a sign-up: *"There is no public way to obtain one —
sign-up ends at an OAuth consent screen and key management is the dashboard's chapter."* The
sealed suite has used this seeder since 3.26; **the earlier draft of this file used `$USER_TOKEN`
six times and never said where it comes from.**

## 1 · The accept path

```bash
# FIRST, what it answers today — T001a's measurement, not a step to skip
curl -s -o /dev/null -w '%{http_code}\n' -X POST localhost:4000/v1/media \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d '{"filename":"holiday.jpg","mime_type":"image/jpeg","bytes":2097152}'
# → 503 media_storage_unavailable, until the store's address is set (T001b)

# a slot, then the upload, then the message — every variable set from the step above it
SLOT=$(curl -s -X POST localhost:4000/v1/media \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d '{"filename":"holiday.jpg","mime_type":"image/jpeg","bytes":2097152}')
# → 201 { "media_id": "…", "state": "pending", "upload_url": "…", "expires_at": "…" }
MEDIA_ID=$(jq -r .media_id <<<"$SLOT")
UPLOAD_URL=$(jq -r .upload_url <<<"$SLOT")

head -c 2097152 /dev/urandom > holiday.jpg
curl -s -X PUT "$UPLOAD_URL" --data-binary @holiday.jpg -o /dev/null -w '%{http_code}\n'
# → 200, and no byte of it reached the api

curl -s -X POST "localhost:4000/v1/channels/$CHANNEL/messages" \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d "{\"text\":\"look\",\"user\":\"qs-bot\",\"attachments\":[{\"type\":\"media\",\"media_id\":\"$MEDIA_ID\"}]}"
# → 201
```

**The PUT goes to whatever host the api signed**, which is T001b's decision and not a detail: the
host is inside the SigV4 signature, so a URL signed `http://minio:9000` is unreachable from here
and one signed `http://localhost:9100` is unreachable from the api's own probe.

**Expected**: the message is created and reading it back returns the attachment as sent. The object
is still `pending` — nothing has verified it, and nothing will until movement VI.

## 2 · The three refusals look the same

**RE-RUNNING THE SEEDER DOES NOT GIVE YOU A SECOND TENANT, and taking it at its word costs you
the whole section.** `seed-demo-tenant.mjs` reuses an existing demo environment and mints a new
credential in it — two different credential strings, one `environment_id`. An object obtained
that way is **yours**, the send answers **201**, and a reader watching for a refusal concludes
the platform leaks across tenants. Measured, on the run that wrote this paragraph.

A genuinely foreign object needs a second environment, which no published route creates:

```bash
FOREIGN=$(psql "postgres://relay:relay@localhost:15432/relay" -tAc "
  WITH e AS (
    INSERT INTO environments (id, application_id, kind, signing_secret)
    SELECT gen_random_uuid(), application_id, 'production', signing_secret
      FROM environments WHERE kind = 'development' LIMIT 1
    ON CONFLICT DO NOTHING RETURNING id)
  INSERT INTO media_objects
    (id, environment_id, filename, mime_type, declared_bytes, object_key, state)
  SELECT gen_random_uuid(), e.id, 'f.png', 'image/png', 1, 'f/k', 'pending' FROM e
  RETURNING id" | tr -d '[:space:]')
```

Then all three, with the bodies compared after `request_id` is stripped:

```bash
NOBODYS=$(cat /proc/sys/kernel/random/uuid)
for ID in "$FOREIGN" "$NOBODYS" "$(cat /proc/sys/kernel/random/uuid)"; do
  curl -s -X POST "localhost:4000/v1/channels/$CHANNEL/messages" \
    -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
    -d "{\"text\":\"x\",\"user\":\"qs-bot\",\"attachments\":[{\"type\":\"media\",\"media_id\":\"$ID\"}]}" \
  | jq 'del(.request_id)'
done
```

**AND `environments` HAS NO `name` COLUMN**, which the first version of that statement assumed:
`id, application_id, kind, signing_secret, retention_days, quota_config` and three rate limits.
Asked of `information_schema` rather than remembered — the third time in this feature that a
fixture was wrong about a schema and only the database could say. An application holds one
environment per `kind` (FR-TEN-04, `unique (application_id, kind)`), so the second one is the
`production` half of the same application.

**`uuidgen` IS NOT ON EVERY MACHINE AND IS NOT ON THIS ONE.** The first draft used it and the
shell answered `command not found` three times — so the loop ran with EMPTY ids and every refusal
came back for the wrong reason. `/proc/sys/kernel/random/uuid` needs nothing installed.

**AND `psql -tAc` LEAVES A NEWLINE**, which `tr -d ' '` does not strip. The id then travelled into
the JSON body with a control character in it and the api answered *"Bad control character in
string literal in JSON at position 107"* — a fourth wrong refusal, and the fourth time in this
section that a shell detail produced a red that looked like a platform one. `tr -d '[:space:]'`.

**Expected**: three identical 422 bodies. Anything that distinguishes them is an existence oracle
(SC-002). The third arm of FR-MED-06 — another USER's object in your own tenant — needs a user
token and is exercised in `attach.itest.ts` rather than here; this section proves the property
that matters on the wire, which is that the three answers cannot be told apart.

## 3 · A malformed id is a different failure

```bash
curl -s -X POST "localhost:4000/v1/channels/$CHANNEL/messages" \
  -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
  -d '{"text":"x","user":"qs-bot","attachments":[{"type":"media","media_id":"not-a-uuid"}]}' | jq .code
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
pnpm test:integration                      # 12 of 12 tasks — EXCLUDES @relay/outsider
pnpm test:outsider                         # the sealed suite, after the seeder in §0
cd ../relay-tutorial
pnpm check:errors                          # both directions, after the code is removed
pnpm check:fences 2>&1 | grep 'problem(s)\|replay onto'
```

**`check:errors` is the one no CI job runs** (`gaps.md` 055-3), and this chapter both removes a
code and adds one. Run it by hand, in both directions, and read its counted line rather than its
exit code.

**AND `test:outsider` IS THE ONE NO LOCAL ARTIFACT NAMED.** `integration-gate.mjs:101` excludes
`@relay/outsider` from `test:integration` by name and deliberately — it integrates against a
platform it does not start — and CI gives it a job of its own at `ci.yml:244`. A chapter adding a
test there and running only `test:integration` would see it pass by never running.

**And nothing runs this file.** NFR-USE-03 makes *"the quickstart shall run without modification,
verified by automated execution in CI"* a `T` clause at 100% pass, and `ci.yml` contains the word
`quickstart` zero times. T073b is its whole verification.
