# Quickstart — chapter 4.23, "The channel a socket names"

**§0 to §2 are MEASURED on 2026-10-06. §3, §3b and §4 are PREDICTIONS** until phase 9
runs them. **§2's COMMAND was rewritten at analysis pass 1 and has not been run in
that form** — the original printed `f.payload.channels ?? f.payload.channel_ids`,
neither of which the ack has. What the new one prints is derived from
`connectionAckSchema` and from the gateway holding no channel external id at all, so
it is a prediction wearing a measured section's label until T006a runs it. 4.22's two predictions came true first time; 4.21's were both wrong,
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
  if (f.type === "connection.ack") console.log("   ack revisions =", JSON.stringify(Object.keys(f.payload.revisions)),
    "cursor =", JSON.stringify(Object.keys(f.payload.cursor)), "truncated =", JSON.stringify(f.payload.truncated));
});'
```

**Measured**: every `channel` is a uuid — **and the ack names channels three more
times without using the word**: `revisions` and `cursor` are keyed by uuid and
`truncated` is a list of them. The payload has no `channels` or `channel_ids` field
at all, which is why the first version of this section printed `undefined` and why
the premise it was written from counted seven fields and missed three structures.
The customer named the channel `order-NNNNN` and the socket has never heard of it.

## 3 · The identity on every frame (PREDICTION)

Provoke each of the seven and read the field:

```
message.created      channel = order-NNNNN
message.deleted      channel = order-NNNNN
message.updated      channel = order-NNNNN
media.updated        channel = order-NNNNN
membership.changed   channel = order-NNNNN
typing               channel = order-NNNNN
connection.ack       revisions keys = ["order-NNNNN", …]
                     cursor keys    = ["order-NNNNN", …]
                     truncated      = ["order-NNNNN", …] or []
```

**Expected after the chapter**: seven fields and three structures, ten of ten, and a
send naming `order-NNNNN` answering as a send naming the uuid does today.

## 3b · Saying the identifier, which §1 to §3 never do (PREDICTION)

**THE FIRST FOUR SECTIONS READ AND NEVER WRITE**, so the half of the chapter that
accepts an identifier had no section at all until analysis pass 7. FR-002, FR-003
and SC-002 live here.

```bash
node -e '
const { WebSocket } = require("ws");
const s = new WebSocket(process.env.WS, { headers: { authorization: `Bearer ${process.env.T}` } });
const say = (f) => s.send(JSON.stringify(f));
s.on("open", () => {
  // by the name the customer gave it
  say({ type: "message.send", payload: { idem_key: `k${Date.now()}`, channel: process.env.ORD, text: "by identifier" } });
  // by the uuid a client minted before this chapter
  say({ type: "message.send", payload: { idem_key: `k${Date.now()}b`, channel: process.env.UUID, text: "by key" } });
  // and the path with no refusal behind it
  say({ type: "typing.send", payload: { channel: process.env.ORD } });
});
s.on("message", (b) => console.log("  ", String(b).slice(0, 160)));'
```

```
message.ack                  for the send by identifier
message.ack                  for the send by uuid       (FR-003: both keep working)
typing  channel = order-NNNNN  echoed to the other member of the channel
```

**AND THE TYPING LINE IS THE ONE TO WATCH.** A send that is not understood is
refused by the api and the client is told. A typing frame for a channel the
connection does not hold is **dropped with no frame, no close code and no log line**
— so if the identifier is not translated, this section prints two acks and nothing
else, and that silence is the whole of FR-003's forbidden outcome.

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
