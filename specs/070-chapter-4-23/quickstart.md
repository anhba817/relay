# Quickstart — chapter 4.23, "The channel a socket names"

**§0 to §2 are MEASURED on 2026-10-06. §3 and §4 are PREDICTIONS** until phase 9
runs them. 4.22's two predictions came true first time; 4.21's were both wrong,
4.20's five times. Distrust any section whose behaviour Phase 2 still decides —
here that is §4, which depends on how a mid-session join gets its identity.

**A socket needs a client, and there is one.** `packages/e2e/src/harness.ts` imports
`ws` and already connects (`:176`). The commands below use `node` with it rather
than `curl`, because `curl` cannot hold a WebSocket.

## 0 · Prerequisites

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
pnpm build
DATABASE_URL=postgres://relay:relay@localhost:15432/relay node services/api/dist/db/migrate.js
RELAY_POSTGRES_PORT=15432 docker compose --profile services build api gateway
RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d --wait
export K=$(RELAY_POSTGRES_PORT=15432 node scripts/seed-demo-tenant.mjs 2>/dev/null | tail -1)
```

**BOTH IMAGES, NOT JUST THE API.** This chapter changes the gateway, and 4.11, 4.19
and 4.20 each met a route answering wrongly against a stale image and read it as a
missing feature. The api is rebuilt too because the session response changes.

## 1 · MEASURED — what a client is told at connect

```bash
ORD="order-$RANDOM"; U="watcher-$RANDOM"
curl -s -X POST localhost:4000/v1/channels -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d "{\"external_id\":\"$ORD\",\"type\":\"public\"}" >/dev/null
curl -s -X POST localhost:4000/v1/users -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d "{\"users\":[{\"external_id\":\"$U\"}]}" >/dev/null
curl -s -X POST "localhost:4000/v1/channels/$ORD/members" -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d "{\"user_ids\":[\"$U\"]}" >/dev/null
```

The channel is named `order-NNNNN` and the member is a person. **Both created by
identifier, which is 4.22's work and the premise this chapter builds on.**

## 2 · MEASURED — every channel the socket names is a uuid

Connect with that user's token and print the `channel` field of whatever arrives:

```bash
node -e '
const { WebSocket } = require("ws");
const s = new WebSocket(process.env.WS, { headers: { authorization: `Bearer ${process.env.T}` } });
s.on("message", (b) => { const f = JSON.parse(b);
  const c = f.payload?.channel ?? f.channel;
  if (c) console.log("  ", f.type, "channel =", c);
  if (f.type === "connection.ack") console.log("   ack channels =", JSON.stringify(f.payload?.channels ?? f.payload?.channel_ids));
});'
```

**Measured**: every `channel` is a uuid, and the ack's channel list is uuids. The
customer named the channel `order-NNNNN` and the socket has never heard of it.

## 3 · The identity on every frame (PREDICTION)

Provoke each of the seven and read the field:

```
message.created      channel = order-NNNNN
message.deleted      channel = order-NNNNN
message.updated      channel = order-NNNNN
media.updated        channel = order-NNNNN
membership.changed   channel = order-NNNNN
typing               channel = order-NNNNN
connection.ack       channels = ["order-NNNNN", …]
```

**Expected after the chapter**: seven of seven, and a send naming `order-NNNNN`
answering as a send naming the uuid does today.

## 4 · A channel joined while connected (PREDICTION, and the one Phase 2 decides)

```bash
# with the socket already open, add the user to a second channel
curl -s -X POST "localhost:4000/v1/channels/$ORD2/members" -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d "{\"user_ids\":[\"$U\"]}" >/dev/null
```

**Expected**: the `membership.changed` frame names `$ORD2`, and so does every frame
for that channel afterwards.

**THIS IS THE SECTION TO DISTRUST.** The map is filled at connect and a channel
joined after it is one the map cannot name (R3). Which of the three options Phase 2
takes decides whether this prints an identity, costs a round trip, or — in the
option listed to be refused — prints a uuid for exactly the channels a user most
recently joined.

## 5 · And what this still cannot show

- **Whether a customer's real-time client stops keeping a lookup table.** The
  chapter removes the need on the last surface that had one; whether anyone's tool
  changes is theirs.
- **The uuid-keyed cursor across an upgrade.** It needs a client that connected
  before the deployment and reconnected after, which no local run reproduces — the
  assertion for it is a constructed cursor, not an observed one (R4).
- **Whether the cross-tenant suite can attack a socket at all.** The gauntlet
  attacks REST routes; Phase 1 finds out, and either answer is recorded.
- **The REST surface**, which 4.22 finished and this chapter does not touch.
