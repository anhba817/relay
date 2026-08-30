# Contract — the membership lifecycle

*Write, record, publish, act. Four steps, three of which already exist, and one ordering that is
a requirement rather than an implementation note.*

---

## The happy path, a removal

```
api                                          gateway A (Mai)      gateway B (Tuan)
 |
 |-- BEGIN
 |   DELETE FROM channel_members ...
 |   INSERT INTO outbox (channel.member_removed)
 |-- COMMIT
 |
 |-- PUBLISH member:{channel_id} -----------------> receives          receives
 |                                                  |                  |
 |                                          sends the frame     sends the frame to Tuan   <- FIRST
 |                                          to local members      (neither phase nor marks)
 |                                                              deletes from channelIds
 |                                                              drops that channel's frames
 |                                                                from connection.buffer
 |                                                              decrements chan:, presence:,
 |                                                                member:                 <- SECOND
 |-- 200
```

**One publish, both audiences.** The removed user is still a member at the moment of the publish,
so their instance is still subscribed to the channel's subject. That is what makes a removal
cheaper than an addition.

**The two resume steps are FR-029 and FR-030**, and this diagram omitted them for seven analysis
passes while the `may not` table below already carried both. A diagram that contradicts its own
contract is worse than one that says less: an implementer follows the picture.

**FIRST and SECOND are FR-008.** Cut-then-send delivers the notice to a client whose membership no
longer grants access — the clause this chapter exists to satisfy, violated by the frame announcing
it. The ordering is a property of one instance's own sequence, which is the only place it can be:
the fabric guarantees nothing about order between two publishes.

---

## The happy path, an addition

```
api
 |-- BEGIN; INSERT INTO channel_members; INSERT INTO outbox (channel.member_added); COMMIT
 |
 |-- PUBLISH member:{channel_id} ----> existing members' instances send the frame
 |-- PUBLISH member:{env}:{user} ----> the new member's instances:
 |                                       subscribe chan:, presence:, member:{channel_id}
 |                                       insert into connection.channelIds
 |                                       send the frame
 |-- 200
```

**Two publishes, and the second is the one that could not have been avoided** (research R1). The
instance holding the new member is not subscribed to the channel, so nothing derived from the
channel reaches it.

**Subscribe before inserting into `channelIds`.** The reverse order opens a window in which
`registry.subscribersOf` returns a connection for a channel this instance is not yet receiving,
which is a silently lost message rather than an error.

---

## A ban

```
api
 |-- BEGIN; UPDATE users SET banned = true; INSERT INTO outbox; COMMIT
 |-- PUBLISH member:{env}:{user}  (once, not once per channel)
 |                                  the instance drops every channel for that user
 |-- 200
```

The only change whose scope is a user rather than a pair. `POST /internal/session` already carries
`banned` and refuses at connect (chapter 3.15); this makes the live path agree with the connect
path.

---

## When the fabric is unreachable

```
api                                          gateway
 |-- BEGIN; DELETE; INSERT INTO outbox; COMMIT      <- the durable record survives
 |-- PUBLISH ... -> throws                          <- swallowed, resolved
 |-- log membership.failed { op, error }            <- THE REQUIREMENT'S EVIDENCE
 |-- 200                                            <- the route still answers
                                                     |
                                    ...up to one backstop interval later...
                                                     |
 |<-- GET /internal/memberships ---------------------|  the re-read corrects it
```

**Three things must be true here and only one of them is obvious.** The route answers, the row is
written, and *one structured event is logged* — because a publisher that does nothing satisfies
the first two exactly as well as a working one does. This is chapter 3.18's trap against its own
publisher, and it caught chapter 3.19's presence module too.

**The backstop is what makes this contract honest** (research R3). Constitution IV permits a lossy
fabric *"precisely because durability and resume live in PostgreSQL sequences and cursors"* and
requires a new mechanism to preserve that recovery property. A message recovers through its resume
cursor; a revocation has none. The re-read is the substitute, its interval is a number the chapter
publishes with its arithmetic beside it, and **FR-014a says what to do if no interval is
affordable**: record FR-RTM-10 as met on the happy path and unmet under fabric loss. Not a clause
narrowed until it passes.

---

## The re-read contract, revived

```ts
// packages/protocol/src/internal.ts — exported since chapter 3.2, parsed by nothing
export const internalMembershipsResponseSchema = z.strictObject({
  channel_ids: z.array(z.string().min(1)),
});
```

`GET /internal/memberships` returns the caller's current channel ids. The gateway diffs them
against `connection.channelIds` and applies the difference through the same code path a published
change takes — **one act, two triggers**, so the backstop cannot drift from the fast path.

**Read the negative fixture before the route exists, not after.**
`services/api/src/tenancy/signup.itest.ts:280` **POSTs** this path with no credential and asserts
`status !== 200`. A GET-only route answers that with a 404, so reviving it as a GET breaks nothing
— registering `ALL`, adding a POST twin, or answering an unauthenticated caller does. The path in
that test is not the evidence; the assertion is.

---

## What each step may not do

| Step | May not |
|---|---|
| the outbox insert | be skipped on an idempotent no-op — a repeated add that changed nothing writes no row and publishes nothing (FR-005) |
| the publish | fail the write it follows, or be awaited in a way that can (FR-016) |
| the gateway's act | close the socket, emit a close code, or send an error frame (FR-013) |
| the gateway's act | leave the resume buffer alone. `flushable(buffer, marks)` filters on `frame.seq` and not on membership, so a removal mid-resume must drop that channel's buffered frames or the flush delivers them afterwards (FR-029) |
| the gateway's act | put the notice into that same buffer. The frame reads neither `phase` nor `marks` — buffered, it arrives after the cut-off, or FR-029's filter drops it and it never arrives (FR-030) |
| the unsubscribe | release a channel another local member still holds — decrement, never release (research R6) |
| the backstop | be the mechanism. It bounds the damage from a dropped publish; it is not how the five seconds are met |
