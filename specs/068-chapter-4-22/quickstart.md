# Quickstart — chapter 4.22, "The identifier the customer gave it"

**Every section is MEASURED against the composed api on 2026-10-06**, after the
chapter shipped. Nothing here is a prediction.

**What this file said before.** §1 and §2 were the *wall* — the 500 a customer got
asking for a channel by the name they gave it — and §3 and §4 were marked
PREDICTION. The wall is gone, so the measured sections are now the working ones
and the wall is kept in §4 as the cause rather than the symptom. **Both
predictions came true on the first run**, which has not been the usual outcome:
4.21's were both wrong, 4.20's wrong five times, 4.16's three.

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
the composed container. 4.11, 4.19 and 4.20 each met a route answering 404
against a stale image and read it as a missing route.

## 1 · MEASURED — the name you gave it is the name that works

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

```
  order-2494                               200
  8a50e324-cb1f-4900-95ab-6f3f97d7ee60     200
```

**Both, and the first was a 500 before this chapter.** The second line is the half
that must not change: 173 call sites in the test corpus pass a uuid and every
published client holds one.

## 2 · MEASURED — every route beneath the prefix, by name

```bash
ORD="order-$RANDOM"; BOT="qb-$RANDOM"
curl -s -X POST localhost:4000/v1/channels -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d "{\"external_id\":\"$ORD\",\"type\":\"private\"}" >/dev/null
curl -s -X POST localhost:4000/v1/users -H "authorization: Bearer $K" \
  -H 'content-type: application/json' \
  -d "{\"users\":[{\"external_id\":\"$BOT\",\"kind\":\"bot\",\"description\":\"b\"}]}" >/dev/null
curl -s -X POST "localhost:4000/v1/channels/$ORD/members" -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d "{\"user_ids\":[\"$BOT\"]}" >/dev/null

for r in "GET /v1/channels/$ORD" "GET /v1/channels/$ORD/messages" \
         "POST /v1/channels/$ORD/archive" "DELETE /v1/channels/$ORD/archive"; do
  set -- $r
  printf '  %-6s %-46s %s\n' "$1" "$2" \
    "$(curl -s -o /dev/null -w '%{http_code}' -X "$1" -H "authorization: Bearer $K" "localhost:4000$2")"
done

curl -s -o /dev/null -w '  POST   send a message                           %{http_code}\n' \
  -X POST "localhost:4000/v1/channels/$ORD/messages" -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d "{\"user\":\"$BOT\",\"text\":\"hello\"}"
```

```
  GET    /v1/channels/order-30688                       200
  GET    /v1/channels/order-30688/messages              200
  POST   /v1/channels/order-30688/archive               200
  DELETE /v1/channels/order-30688/archive               200
  POST   send a message                                 201
```

**THE BOT IS NOT DECORATION.** An application credential may send only as a bot
user — `sender_not_permitted`, *"an application credential may send only as a bot
user; name one in `user`"* — so a fixture that creates a plain person gets a 403
on the send and the whole section reads as broken. That cost two wrong runs during
implementation and is the most common way this file goes wrong.

## 3 · MEASURED — an identifier nobody used

```bash
curl -s -o /dev/null -w '  absent identifier: %{http_code}\n' \
  -H "authorization: Bearer $K" "localhost:4000/v1/channels/order-nobody-created-this"
```

```
  absent identifier: 404
```

**This one line is the whole difference between a platform that refuses and one
that breaks.** It was `500 internal_error` before the chapter.

## 4 · MEASURED — why it was a 500, which is still true of the SQL

The database has not changed, and the statement the route used to send still fails
exactly as it did:

```bash
docker compose exec -T postgres psql -U relay -d relay -c \
  "select id from channels where external_id = 'x' or id = 'x'::uuid;"
```

```
ERROR:  invalid input syntax for type uuid: "x"
```

**Postgres raises before the `OR` can short-circuit.** What changed is not the
database's behaviour but whether the api ever asks it this question: a value that
cannot parse as a uuid now reaches the identity predicate alone, and `$1::uuid`
never appears in the statement.

**And the api still logs a 500 without its cause** — one `"status":500` line, no
`22P02`. That is every 500 on this platform, and this chapter did not fix it.

## 5 · And what this still cannot show

- **Whether a customer stops keeping a lookup table.** The chapter removes the
  need; whether anyone's tool changes is theirs to decide.
- **The collision.** An `external_id` that is itself a uuid is legal and **0 of
  41,772** channels have one, so the tie-break is a constructed test and not an
  observed case.
- **Whether the uuid is ever retired.** 173 call sites hold one. Not this chapter.
- **The internal-key sweep.** *Does any value we return name something no route
  accepts?* is an audit of every response shape, not a curl, so it lives in the
  chapter and in `baseline.txt`. It found one — `members[].user_id` — and that
  count is why ADR-37 is amended.
- **The real-time surface.** Every gateway frame carries `channel: <uuid>`, the
  session response hands a connecting client a list of channel uuids, and a socket
  send goes to a door typed `z.string().uuid()`. **So the lookup table this chapter
  removes from REST is still needed by anyone holding a socket** — on Journey 3's
  Stage 5, in the same journey whose Stage 1 promises zero of them.
