# Contract — the typing fabric, and the second frame a client may send

*What crosses between gateway instances, what crosses to a client, and what a client is
now allowed to say.*

---

## The fourth subject grammar

    typing:{channel_id}

One subject per channel. Every gateway instance holding a member of that channel
subscribes; the publishing instance is one of them and filters its own signaller out at
delivery rather than at publish, because it cannot know which other connections exist.

**Why not `chan:{channel_id}`.** ADR-19 refused it for presence and all three of its
reasons are still in the tree — `publish(message: Message)` and a
`messageCreatedSchema.shape.payload.safeParse` in `services/gateway/src/fanout.ts`, and the
literal `message.created` send in `session.ts`'s `deliver`. Carrying a second kind there
means widening a type, loosening a parse that currently rejects everything that is not a
message, and editing the highest-volume path in the system to serve the lowest-volume
traffic on it.

**The rule, now that three chapters have reached it independently: a fabric owns its
subject grammar, and a kind that cannot share a payload type cannot share a subject.**

Four grammars after this chapter:

| Subject | Carries | Addressed to |
|---|---|---|
| `chan:{channel_id}` | messages | a channel |
| `presence:{channel_id}` | presence transitions | a channel |
| `member:{channel_id}` | a removal, to both audiences at once | a channel |
| `member:{env}:{user}` | an addition, a ban | a **principal** |
| `typing:{channel_id}` | a typing signal | a channel |

---

## The fabric payload

```ts
{
  environment: string,   // checked by the receiver against the connection, never sent on
  channel: string,
  user: string,          // the EXTERNAL id, resolved from the signalling connection
}
```

A `z.strictObject`, validated on receipt even though the fabric is inside the trust
boundary — `fanout.ts` states the reason and it is unchanged: "inside" is one compromised
dependency away from "outside", and a malformed payload must not reach a client.

**No timestamp and no deadline.** The receiver's five seconds runs from the moment the
frame arrives at the client, not from when it was published. A deadline on the wire would
be a second clock, and chapter 3.19 has already recorded what two clocks on one deadline
cost.

---

## The wire frames

### Outbound — NOT EDITED

```ts
{ type: "typing", payload: { channel: string, user: string } }
```

`packages/protocol/src/frames.ts:96`, unchanged since chapter 1.3. `frames.test.ts` asserts
this shape and this chapter does not touch either.

### Inbound — new

```ts
{ type: "<decided in Phase 2>", payload: { channel: string } }
```

**The second frame a client may utter, and the first added since chapter 1.3.**

`services/gateway/src/session.ts:948` currently refuses everything else:

```ts
if (frame.data.type !== "message.send") {
  sendError(socket, "unknown_frame_type", `clients may not send ${frame.data.type}`);
  socket.close(4002, CLOSE_CODES[4002]);
}
```

That check becomes a set with two members. **The set is named and its size asserted**, so
that a third member is a decision somebody made rather than a diff nobody read — the same
instrument `codes.test.ts` applies to close codes and `targets.itest.ts` to routes.

---

## What the direction gauntlet has to say afterwards

`services/gateway/src/isolation.itest.ts` derives the union's members and asserts the count:

    it("derives all ten members from the union itself")   expect(members.length).toBe(10)
    it("classifies every member exactly once")
    it("names no frame the union does not have")

**All three fail on the build that adds a frame type**, which is the point. The eleventh
member needs a DIRECTIONS row with a direction and a stated reason, and a case in the
sample builder.

`typing` stays **outbound** in that table with its reason unchanged — *"server-fanned; a
client claiming one could type as anybody"* — and it remains true, because the new inbound
frame is a different type that carries no user.

---

## Refusals

| Case | Answer | Why |
|---|---|---|
| A signal for a channel the connection is not in | nothing published, no error | Revealing that a channel exists is a disclosure (FR-TEN-05) |
| A signal naming another user | the payload has no user field | Removed at the schema, not checked at the handler |
| Over the typing limit | **silence** — no frame, no close | An advisory indicator is not worth an error, and the client will signal again in seconds |
| Any other inbound frame type | `unknown_frame_type`, close 4002 | Unchanged for the other nine types |
| The fabric is unreachable | socket stays open, one logged event | FR-015; the client is told nothing because there is nothing it can do |

**The third row is the one that differs from every existing refusal in this platform.** A
refused connect is a 429 with `Retry-After`; a refused send is an error frame the client
must handle. A refused typing signal is dropped on the floor. That is defensible precisely
because the feature is cosmetic, and it should be stated rather than discovered.

---

## The log vocabulary

A closed set, asserted as the set an instance actually emitted rather than as what a grep
finds. Chapter 3.20's FR-032 named three and the code emitted six; the amendment is on
record and this chapter is not repeating it.

    typing.published        a signal went onto the fabric
    typing.failed           a publish or a subscribe failed, with an op
    typing.invalid_payload  a body that is not JSON, or JSON the schema rejects

**No name for a dropped rate-limited signal.** It is expected traffic, not a failure, and
one log line per keystroke over the limit is the unbounded output NFR-OBS-01 exists to
prevent.
