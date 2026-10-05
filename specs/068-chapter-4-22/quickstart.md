# Quickstart — chapter 4.22, "The identifier the customer gave it"

**§0 to §2 are MEASURED on 2026-10-05. §3 and §4 are PREDICTIONS** until phase 9 runs
them. Chapter 4.21's two predictions were both wrong for one reason — they were
written before two decisions were taken — so distrust any section whose behaviour
Phase 2 still decides.

## 0 · Prerequisites

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
pnpm build
DATABASE_URL=postgres://relay:relay@localhost:15432/relay node services/api/dist/db/migrate.js
RELAY_POSTGRES_PORT=15432 docker compose --profile services build api
RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d --wait
export K=$(RELAY_POSTGRES_PORT=15432 node scripts/seed-demo-tenant.mjs 2>/dev/null | tail -1)
```

**THE IMAGE REBUILD IS NOT OPTIONAL.** Everything below talks to `localhost:4000`,
the composed container. 4.11, 4.19 and 4.20 each met a route answering 404 against a
stale image and read it as a missing route.

## 1 · MEASURED — the wall

```bash
ORD="order-$RANDOM"
CID=$(curl -s -X POST localhost:4000/v1/channels -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d "{\"external_id\":\"$ORD\",\"type\":\"private\"}" \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["id"])')

for key in "$ORD" "$CID"; do
  printf '  %-40s %s\n' "$key" \
    "$(curl -s -o /dev/null -w '%{http_code}' -H "authorization: Bearer $K" \
       "localhost:4000/v1/channels/$key")"
done
```

**Measured**: the identifier answers **500**, the uuid answers **200**.

## 2 · MEASURED — why it is a 500 and not a 404

```bash
docker compose exec -T postgres psql -U relay -d relay -c \
  "select id from channels where external_id = 'x' or id = 'x'::uuid;"
```

```
ERROR:  invalid input syntax for type uuid: "x"
```

**Postgres raises before the `OR` can short-circuit.** The path segment reaches a
uuid-typed column, the driver sends it as a uuid, the database refuses it. That is
the 500 — and **the api logs the status without the cause**, measured: one `"status":500`
line and nothing else.

## 3 · The identifier works everywhere (PREDICTION)

```bash
ORD="order-$RANDOM"
curl -s -X POST localhost:4000/v1/channels -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d "{\"external_id\":\"$ORD\",\"type\":\"private\"}" >/dev/null
curl -s -X POST localhost:4000/v1/users -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d '{"users":[{"external_id":"qb","kind":"bot","description":"b"}]}' >/dev/null
curl -s -X POST "localhost:4000/v1/channels/$ORD/members" -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d '{"user_ids":["qb"]}' >/dev/null

for r in "GET /v1/channels/$ORD" "GET /v1/channels/$ORD/messages" \
         "POST /v1/channels/$ORD/archive" "DELETE /v1/channels/$ORD/archive"; do
  set -- $r
  printf '  %-6s %-46s %s\n' "$1" "$2" \
    "$(curl -s -o /dev/null -w '%{http_code}' -X "$1" -H "authorization: Bearer $K" "localhost:4000$2")"
done
```

**Expected after the chapter**: 200 on every line, and a send to
`/v1/channels/$ORD/messages` answering 201 without the customer ever seeing a uuid.

## 4 · And an identifier nobody used (PREDICTION)

```bash
curl -s -o /dev/null -w '  absent identifier: %{http_code}\n' \
  -H "authorization: Bearer $K" "localhost:4000/v1/channels/order-nobody-created-this"
```

**Expected**: `404`. **It is `500` today**, and this one line is the whole difference
between a platform that refuses and one that breaks.

## 5 · And what this still cannot show

- **Whether a customer stops keeping a lookup table.** The chapter removes the need;
  whether anyone's tool changes is theirs to decide.
- **The collision.** An `external_id` that is itself a uuid is legal and **0 of
  41,768** channels have one, so the tie-break is a constructed test and not an
  observed case.
- **Whether the uuid is ever retired.** 157 call sites hold one. Not this chapter.
