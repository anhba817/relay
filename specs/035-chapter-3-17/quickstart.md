# Quickstart — validating chapter 3.17

How to prove this chapter works, end to end, against a running stack. Not implementation
detail: `data-model.md` has the schema and `contracts/` has the routes.

## Prerequisites

```bash
cd relay-platform
docker compose up -d              # Postgres on 15432, Redis, NATS
pnpm install && pnpm build
pnpm --filter @relay/api migrate
```

The lane's Postgres is on **15432**, not 5432 — this machine's own Postgres holds the default
port.

## 1. A tenant creates a bot, and the database refuses one without a description

```bash
# succeeds
curl -sS -X POST "$API/v1/users" -H "authorization: Bearer $KEY" \
  -H 'content-type: application/json' \
  -d '{"users":[{"external_id":"support-bot","kind":"bot",
       "display_name":"Support Bot",
       "description":"Posts ticket updates from the helpdesk. Never reads."}]}'

# 400, field: "users.0.description"
curl -sS -X POST "$API/v1/users" -H "authorization: Bearer $KEY" \
  -H 'content-type: application/json' \
  -d '{"users":[{"external_id":"naked-bot","kind":"bot"}]}'
```

**Expected**: the first returns a per-entry result with `status: "created"`. The second is
refused and names the field.

**And prove the database holds it, not only the validator** — the requirement is that a bot
without a description is unrepresentable:

```bash
psql "$DB" -c "insert into users (id, environment_id, external_id, kind)
               values (gen_random_uuid(), '$ENV', 'sneaky', 'bot')"
# ERROR:  new row violates check constraint "users_bot_description_check"
```

## 2. The kind cannot change

```bash
# create a person, then try to make it a bot — 400, field: "users.0.kind"
curl -sS -X POST "$API/v1/users" -H "authorization: Bearer $KEY" \
  -H 'content-type: application/json' \
  -d '{"users":[{"external_id":"ana","display_name":"Ana"}]}'
curl -sS -X POST "$API/v1/users" -H "authorization: Bearer $KEY" \
  -H 'content-type: application/json' \
  -d '{"users":[{"external_id":"ana","kind":"bot","description":"nope"}]}'
```

## 3. A bot cannot be minted for

```bash
curl -sS -X POST "$API/auth/dev-token" -H "authorization: Bearer $KEY" \
  -H 'content-type: application/json' -d '{"user":"support-bot"}'
```

**Expected**: 404, and the body identical to the one an identifier with no row gets. Compare
them — if they differ, the route is an oracle for which identifiers are bots.

## 4. The send requires a sender, and may not name a person

```bash
CH=$(curl -sS -X POST "$API/v1/channels" -H "authorization: Bearer $KEY" \
     -H 'content-type: application/json' \
     -d '{"external_id":"support","type":"public"}' | jq -r .id)

# 201 — sent as the bot
curl -sS -X POST "$API/v1/channels/$CH/messages" -H "authorization: Bearer $KEY" \
  -H 'content-type: application/json' \
  -d '{"text":"your ticket was updated","user":"support-bot"}'

# 400, field: "user"
curl -sS -X POST "$API/v1/channels/$CH/messages" -H "authorization: Bearer $KEY" \
  -H 'content-type: application/json' -d '{"text":"anonymous"}'

# 403 — a key may not post as a person
curl -sS -X POST "$API/v1/channels/$CH/messages" -H "authorization: Bearer $KEY" \
  -H 'content-type: application/json' -d '{"text":"as ana","user":"ana"}'
```

## 5. The refusals that must be indistinguishable

```bash
# a bot of another tenant, and an identifier that exists nowhere
curl -sS -X POST "$API/v1/channels/$CH/messages" -H "authorization: Bearer $KEY" \
  -H 'content-type: application/json' -d '{"text":"x","user":"'"$FOREIGN_BOT"'"}'
curl -sS -X POST "$API/v1/channels/$CH/messages" -H "authorization: Bearer $KEY" \
  -H 'content-type: application/json' -d '{"text":"x","user":"no-such-identifier"}'
```

**Expected**: byte-identical bodies but for `request_id`. This is the check the isolation
suite automates; run it by hand once so the two are seen side by side.

## 6. The message reads back with its sender

```bash
curl -sS "$API/v1/channels/$CH/messages?limit=5" -H "authorization: Bearer $KEY" | jq '.messages[0]'
```

**Expected**: `user` is `"support-bot"`, not null. A message the customer's server sent now has
an identity a person can read.

## 7. The gates

```bash
cd relay-platform
pnpm lint && pnpm typecheck && pnpm build
pnpm turbo run test
pnpm test:integration          # budget 240 s
pnpm coverage                  # every ratchet
pnpm test:outsider             # the sealed integration — it changed, and it must pass unaided

cd ../relay-tutorial
pnpm check:docs && pnpm check:errors && pnpm check:figures && pnpm check:fences
```

**`pnpm test:outsider` is the one that matters most.** It is the artifact chapter 3.14 built to
stand for an external developer, its send changed in this chapter, and chapter 3.14's own
verdict recorded that a suite which passes *because it was corrected by a failing test* is the
assistance the Phase 2 exit criterion forbids. It has to pass because the documentation told an
outsider what to do — not because we fixed the test until it went green.
