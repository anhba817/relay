# Data model — chapter 3.21

**This chapter adds no persistent data.** No table, no column, no migration, no Redis key,
no outbox row. That is the whole of section 1, and it is a design outcome rather than an
omission — see research R3.

---

## 1. What is stored: nothing

    PostgreSQL     unchanged
    Redis keys     none added
    outbox         no new event type
    ClickHouse     untouched

FR-RTM-08 says a typing indicator *"shall not be persisted"*. Most requirements of that
shape are met by remembering not to write something. This one is met by there being nothing
to write: the expiry lives in the receiving client (R3), so no component holds typing state
long enough to persist it.

**The one thing that could have been stored, and why it is not.** A Redis key with a
five-second TTL would let the gateway know when an indicator lapsed. It could then do
nothing with that knowledge, because `typingSchema` has no state field and there is no
frame for "stopped". The key would answer a question nobody can ask.

---

## 2. The two frames

### Inbound — new in this chapter

    { type: "<name decided in Phase 2>", payload: { channel } }

**No `user` field, and that absence is a security property.** The identity is the
connection's, resolved the way chapter 3.17 made the send path resolve its sender. A client
that could name a user could type as anybody, which is exactly what chapter 3.12's gauntlet
row says about the outbound frame.

`channel` is the id a `message.send` frame names, so a client that can send to a channel can
signal typing in it with the same value and no new lookup.

### Outbound — unchanged since chapter 1.3

    { type: "typing", payload: { channel, user } }

`packages/protocol/src/frames.ts:96`, two fields, a `z.strictObject`. **This chapter does
not edit it.** `frames.test.ts` has asserted its shape for twenty chapters and the
direction gauntlet has asserted a client cannot forge it since 3.12 — against a system that
produced none.

**The two shapes differ, and the difference is the whole design.** Inbound carries a
channel because the server supplies the user. Outbound carries both because the receiver
needs to know who. A single bidirectional frame would have to carry a user inbound, and
then the server would have to ignore it — a field that exists and is discarded is worse
than no field.

---

## 3. The fabric payload

One subject per channel, carrying the user and nothing else the wire frame does not need.
The full shape is in [contracts/typing-fabric.md](./contracts/typing-fabric.md).

**The environment travels on the fabric and not on the wire**, as chapter 3.20's does, and
for the same reason: a receiving gateway checks it against the connection it is about to
act on, while a client already knows its own environment and has no use for a tenant id.

---

## 4. What has a lifetime, and where it is kept

| Thing | Lives | Length | Ends by |
|---|---|---|---|
| The indicator a user sees | the receiving client | 5 s from the last frame | a timer lapsing, silently |
| Permission to publish again | a `Map` in `attachSessions`'s closure, keyed by connection then channel | `DEFAULT_RENEWAL_INTERVAL_MS` = 2 s, injectable per instance | the value by the interval elapsing, **the connection's whole entry by the close handler** |
| The fabric subscription | the gateway, reference-counted | the connection | the last local member leaving |

**The module holds two Redis connections, not one** — a publisher and a subscriber, because
a subscribed connection cannot issue ordinary commands and `PUBLISH` is one
(`fanout.ts:33`). Neither holds typing state; they are transport. Chapter 3.20's equivalent
module needed only a subscriber because its api published, and analysis pass 5 found this
chapter's task list carrying that shape forward to a module that publishes from the
gateway.

**The middle row said "a `Map` on the connection" until analysis pass 10, and the task that
builds it says the opposite in bold** — not a field on `Connection`, because `registry.ts`
is fenced by four chapters. Two artifacts describing one structure, and the one a reader meets first was
wrong. **The row was also wrong in its last column**: an outer key never ends by an interval
elapsing, and at NFR-SCL-01's 10,000 connections a closure-level map keyed by connection id
with nothing reaping it grows for the life of the process.

**The interval is injectable and the expiry is not.** Five seconds is FR-RTM-08's and lives
in the client, where no test can shorten it. Two seconds is this chapter's, lives on
`attachSessions`'s options beside `meterIntervalMs`, and a test builds an instance with 40 —
chapter 3.20 tests a sixty-second backstop that way. **Two quantities, and now two
mechanisms.**

**Three lifetimes, three owners, and none of them is a stored fact.** The middle row was a
token bucket until analysis pass 1 read the limiter it would have used: keyed per
environment on a 60-second window, against a rule that is per connection, per channel and 2
seconds. Three mismatches, each fatal alone. Chapter 3.19's most
expensive finding was three separate 30-second numbers that turned out to be three
quantities; this table exists so that the five and the two are never read as one number.

**Five seconds is the clause's and cannot move. Two seconds is this chapter's and is
argued** — 2.5 renewals per expiry window, so one dropped publish does not make an
indicator flicker. Chapter 3.19 armed a grace check at exactly its own grace period, put
two deadlines on one instant reached by two clocks, and stranded a user online for ever.
The margin here is the lesson applied.

---

## 5. What a reconnecting client gets: nothing

A typing frame carries no sequence, so it can neither duplicate a backfilled row nor leave
a gap — chapter 3.20's argument for `membership.changed`, and stronger here. A membership
change is still true when it arrives late. **A typing indicator replayed after a reconnect
is a claim about the present that was true five seconds ago.**

It is sent immediately when it arrives and never enters `connection.buffer`. `flushable`
filters on `frame.seq` and on nothing else, which is the reader chapter 3.20 found the hard
way — a frame that got into that buffer would flush.
