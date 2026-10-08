# Quickstart — chapter 4.23, "The channel a socket names"

**§0 AND §1 ARE MEASURED on 2026-10-06. §2 WAS LABELLED MEASURED AND WAS NOT**, which
analysis pass 8 established twice over: it printed `f.payload.channels ??
f.payload.channel_ids`, neither of which exists on the ack, **and it connected with an
`authorization` header, which the gateway's upgrade handler never reads** — it takes
the token from `?token=` on `/v1/ws` and nothing else (`session.ts:758`). One wrong
field is a typo; a wrong field and a refused handshake is a section nobody ran.
**§2 onward are PREDICTIONS** until T006a and T064 run them. **§2's COMMAND was rewritten at analysis pass 1 and has not been run in
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
export WS=ws://localhost:4001
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

Keep what the socket sections need — **the channel's Relay id, which this chapter is
about not needing, and an end-user token, which no earlier draft of this quickstart
minted**:

```bash
export ORD
export UUID=$(curl -s "localhost:4000/v1/channels/$ORD" -H "authorization: Bearer $K" \
  | node -pe 'JSON.parse(require("fs").readFileSync(0)).id')
export T=$(curl -s -X POST localhost:4000/auth/dev-token -H "authorization: Bearer $K" \
  -H 'content-type: application/json' -d "{\"user\":\"$U\"}" \
  | node -pe 'JSON.parse(require("fs").readFileSync(0)).token')
```

`POST /auth/dev-token` takes `{user, ttl_seconds?}` and answers `{token, expires_at}`.
**An api key is not a socket credential**: the gateway authenticates an end user, and
§2 and §3b used a `$T` that nothing set.

The channel is named `order-NNNNN` and the member is a person. **Both created by
identifier, which is 4.22's work and the premise this chapter builds on.**

## 2 · MEASURED — every channel the socket names is a uuid

Connect with that user's token and print the `channel` field of whatever arrives:

```bash
node -e '
const { WebSocket } = require("ws");
// THE TOKEN GOES IN THE QUERY STRING. `server.on("upgrade")` reads
// `url.searchParams.get("token")` and refuses any path but `/v1/ws`; an
// authorization header is never looked at (session.ts:758).
const s = new WebSocket(`${process.env.WS}/v1/ws?token=${process.env.T}`);
s.on("message", (b) => { const f = JSON.parse(b);
  const c = f.payload?.channel ?? f.channel;
  if (c) console.log("  ", f.type, "channel =", c);
  if (f.type === "connection.ack") console.log("   ack revisions =", JSON.stringify(Object.keys(f.payload.revisions)),
    "cursor =", JSON.stringify(Object.keys(f.payload.cursor)), "truncated =", JSON.stringify(f.payload.truncated));
});'
```

**THIS SECTION CANNOT BE REPRODUCED AFTER THE CHAPTER, AND THAT IS THE POINT.** It
records what the socket did before: every `channel` a uuid, and the ack naming
channels three more times without using the word — `revisions` and `cursor` keyed by
uuid, `truncated` a list of them. The payload has no `channels` or `channel_ids`
field at all, which is why the first version of this section printed `undefined`,
and why the premise it was written from counted seven fields and missed three
structures.

Run the command above against this chapter's build and it prints the NEXT section's
output instead. Measured on 2026-10-08, against the composed stack:

```
ack revisions = ["order-23266"] cursor = [] truncated = []
```

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

**MEASURED on 2026-10-08** for the ack, which is the frame that always arrives:

```
connection.ack   revisions = ["order-23266"]   cursor = []   truncated = []
```

An empty `cursor` and `truncated` are a fresh connect, not an absence — §4's resume
is where those two carry a channel. The other six kinds are provoked by
`channel-naming.itest.ts` and by each frame's own suite; this section is the one a
reader can run in a minute.

## 3b · Saying the identifier, which §1 to §3 never do (PREDICTION)

**THE FIRST FOUR SECTIONS READ AND NEVER WRITE**, so the half of the chapter that
accepts an identifier had no section at all until analysis pass 7. FR-002, FR-003
and SC-002 live here.

```bash
node -e '
const { WebSocket } = require("ws");
const s = new WebSocket(`${process.env.WS}/v1/ws?token=${process.env.T}`);
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

**MEASURED on 2026-10-08**, with the ids this run produced:

```
{"type":"connection.ack","payload":{"user":"watcher-9174","revisions":{"order-23266":0},…}}
{"type":"message.ack","payload":{"seq":1}}
{"type":"message.created","payload":{…,"channel":"order-23266","seq":1,"text":"by key"}}
{"type":"message.ack","payload":{"seq":2}}
{"type":"message.created","payload":{…,"channel":"order-23266","seq":2,"text":"by identifier"}}
```

Both sends are acked and **both come back naming `order-23266`** — the one sent by
uuid included, which is FR-003 from the other side: a client that still speaks the
old name is answered in the new one.

**THE TYPING LINE NEEDS A SECOND MEMBER AND THIS RUN HAD ONE.** A typing signal is
not echoed to the signaller — deliberately, and `typing.itest.ts` asserts it — so a
single socket provokes nothing it can see. Connect a second member's token to watch
it arrive.

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
