# Research — chapter 4.23, "The channel a socket names"

Every figure measured against the tree on 2026-10-06, before the plan was written.

---

## R1 — The surface, counted from the schemas rather than from the frames

```
client-facing schemas carrying `channel`                7
  messageSchema · messageSendSchema · messageDeletedPayloadSchema
  mediaUpdatedSchema · membershipChangedSchema · typingSchema · typingSendSchema

sites in the gateway writing `channel:` onto a frame   21
  session.ts  18        fanout.ts  1        resume.ts  1        typing.ts  1

what those sites write
  change.channel      8      signal.channel      3
  channelId           6      committed.channel   1
  message.channel     1      revision.channel    1

the gateway's references to a channel's external id     0
```

**THE GATEWAY CANNOT TRANSLATE TODAY BECAUSE IT HAS NOTHING TO TRANSLATE FROM.** Not
one reference, anywhere in the service. So this is not a rename of 21 expressions —
it is giving the gateway a mapping it has never held, and the 21 sites are what
happens afterwards.

## R2 — Where the translation goes, and the cheap-looking option is the expensive one

Three designs. The spec assumed the first; this section tested the second and found
it worse, for a reason that did not exist a day ago.

**A — A MAP AT THE GATEWAY'S CLIENT EDGE.** The connection already holds
`channelIds: Set<string>` (`auth.ts:103`, filled from the session response). It gains
a parallel `Map<key, identity>`, and the 21 sites read through it on the way out. The
registry keeps routing on keys (`registry.subscribersOf(channelId)`), the fan-out
subjects keep their shape, the api-facing door keeps its uuid.

**B — THE IDENTITY RIDES ON EVERY INTERNAL PAYLOAD.** The api annotates each frame at
publish time and the gateway passes it through. No map, no staleness, nothing to go
out of date — and it is the one that looks cheapest until you ask whether the api has
the identity where it publishes. Measured at the five publish sites:

```
messages.controller.ts:250   send        external_id in scope: 0
messages.controller.ts:356   edit        0
messages.controller.ts:456   delete      0
channels.controller.ts:237   membership  0
backfill.controller.ts:111   backfill    0
users.controller.ts:200      ban         1  (the USER's, not the channel's)
```

The message row the send returns carries `channel_id` and no identity
(`repository.ts:2698`). So annotating means either **a query per publish on the send
path**, or widening the repository shapes that feed it.

**AND CHAPTER 4.22 IS WHY THIS GOT HARDER RATHER THAN EASIER.** `ChannelIdPipe`
resolves the identity to a key at the request boundary, so **every handler now
receives a uuid and the identity is gone by the time it publishes** — where before
4.22 a handler at least held the raw path segment. The chapter that made REST speak
the customer's language is the same chapter that removed the identity from the place
B would need it. That is not a defect in either design; it is the cost of resolving
early, and it is worth writing down because the next chapter to want an identity
deep in the write path will meet it too.

**C — THE GATEWAY ASKS THE API ON DEMAND.** A lookup per unknown channel, on the
delivery path, with a new failure mode when the api is unavailable — on the one
surface whose whole promise is immediacy. Refused without measurement; the shape is
disqualifying.

**DECISION: A.** It is 4.22's division applied one service over — resolve at the
edge, leave everything behind it keyed. The thing A has to answer that B would not is
staleness, which is R3.

## R3 — How the map gets filled, and the one hole in it

**At connect, from the session response.** `session.controller.ts:132` builds
`channel_ids` from `channels.map(c => c.channel_id)`, which is `members.channelId`
off the join in `channelsForUser` (`repository.ts:4106`). The same read can return
the identity beside the key; the contract field becomes pairs rather than strings.

**THE HOLE IS MEMBERSHIP CHANGE.** A user added to a channel mid-session learns about
it through `membershipChangedSchema`, and `membership/publisher.ts:105` publishes
`channel: change.channel` — a key, from a handler that no longer has the identity
(R2). So a channel joined after connect is one the map cannot name.

Three ways to close it, and the plan should pick with a measurement rather than a
preference:

```
the membership frame carries the identity      one payload, one publish site, and
                                               the api must look it up — B's problem
                                               confined to one low-rate path
the gateway refetches its session on change    one round trip per membership change,
                                               and the data is already shaped for it
the map falls back to the key                  no round trip, and the client sees a
                                               uuid for exactly the channels it most
                                               recently joined — the worst case the
                                               chapter exists to remove
```

The third is listed to be refused in writing.

## R4 — What happens to a client holding a uuid, which the spec left open

FR-003 forbids silent misrouting and permits either *keeps working* or *named
refusal*. The measurement that bears on it:

```
cursorSchema   z.record(z.string(), z.number().int().positive())
               the resume cursor is {channel: seq} and a client sends back
               whatever keys it was given
```

So a client reconnecting across the deployment presents a cursor keyed by uuids,
and a gateway that only understood identities would silently resume nothing for
every channel — **which is the forbidden outcome, reached by accident rather than by
design.** Accepting both forms on the way in is therefore not a courtesy; it is what
keeps FR-003 true across the upgrade.

**Leaning: accept both inbound, emit identity only outbound**, which is exactly
4.22's shape — thirteen routes that take either and a create response that leads with
one. The plan should confirm that the inbound ambiguity is resolvable, because unlike
a channel path segment, a cursor key has no shape test to fall back on: both forms
are strings in a record, and the uuid shape test is the only thing separating them.

## R5 — `ALL_CHANNELS` is not a channel

`membership.ts:75` — `export const ALL_CHANNELS = "*"`. A ban is a removal from every
channel and publishes this sentinel. **Translating it would turn a wildcard into a
lookup miss**, and the fallback in R3's third option would then emit `"*"` to a
client as though it were a channel's name. It must be special-cased before the map is
consulted, and the test for it belongs with the ban path rather than with the map.

## R6 — What the fence chain charges, and the spec's estimate was 40% low

```
                                        en   vi   blocks
packages/protocol/src/frames.ts          6    5     1
packages/protocol/src/internal.ts       14   12     4
services/gateway/src/session.ts         17   16     2
services/gateway/src/auth.ts             6    6     0   CREATE
services/gateway/src/fanout.ts           3    3     2
services/gateway/src/resume.ts           2    2     1
services/gateway/src/typing.ts           1    1     0   CREATE
services/api/src/internal/session.controller.ts
                                         6    6     0   CREATE
services/api/src/db/repository.ts       28   23     8
                                        --   --    --
                                        83   74    18   3 to create
```

**83 ENGLISH PAGES ACROSS 9 FILES, AGAINST THE SPEC'S "~50 ACROSS 7".** I wrote that
estimate, from the seven files the gap itself touches, and it missed `auth.ts` (where
the connection's channel set is built), `typing.ts` (one site, one page) and
`repository.ts` — which is 28 pages on its own and is in the bill because
`channelsForUser` must return the identity beside the key.

4.15's rule earns its place again, and in the same direction it always does: the
count rises when the work is traced rather than listed. 068 charged 9 files against a
bill of 8 and every surprise came from running something.

**The 74 Vietnamese pages are a mirror cost, not a replay cost** (050-3) — the vi
chain is compared against the English chapter and never against `relay-platform`.

## R7 — What this chapter must not do

**It must not touch the fan-out subjects.** `subjectForChannel`,
`subjectForChannelRevision`, `subjectForPresence`, `subjectForTyping` and
`subjectForChannelMembership` all derive a NATS subject from a key. A subject is not
a thing a client sees, and rekeying them would move the delivery path for no reader's
benefit.

**It must not re-key the resume cursor internally.** Its storage and its comparison
stay on keys; only what crosses to the client changes.

**It must not change `internalSendRequestSchema.channel_id`'s type.**
`z.string().uuid()` is correct — that door is the gateway talking to the api, and
`internal.ts` already says internal uuids are the api's business. The gateway
translates before it knocks.

**And it must not retire the uuid on the socket.** R4's cursor measurement is the
reason: every connected client across the deployment holds one.
