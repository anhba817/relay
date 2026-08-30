# Data model — chapter 3.20

**No migration, and that is the first thing worth saying.** Every row this feature reads or
writes already exists. `channel_members` is chapter 2.1's table, `outbox` is chapter 3.3's, and
`users.banned` is chapter 3.15's. What is new is an event, a subject grammar and a mutation of
in-memory state that has been immutable since chapter 2.5.

---

## 1. The thing that changes

A **membership change** is not a row. It is the news that a row in `channel_members` was written
or deleted, addressed to two audiences that are reached by different means.

| Field | Source | Why it is on the wire |
|---|---|---|
| `environment` | the writing repository's own scope | so a receiving gateway can refuse a change belonging to another tenant (FR-007, principle I) |
| `channel` | the route's path parameter | the subject is derived from it; the frame carries it so a client can name what changed |
| `user` | the external id, as everywhere on this contract | the frame's payload names it, which is what makes the frame readable by somebody who is not its subject |
| `change` | `added` \| `removed` | chapter 1.3's enum, and it has no third member — a role change has no spelling here (FR-006) |

**Internal uuids do not cross this boundary.** `user` is the external id, matching
`internalSessionResponseSchema` and every other api → gateway contract.

---

## 2. Two representations of one change, and they are not the same object

This is the second time in two chapters that the fabric payload and the wire frame differ, and
the reason differs too. Chapter 3.19 separated them because presence needed a `transition` id for
dedup that no client should see. Here they separate because **the fabric payload carries an
environment and the frame does not**.

    fabric payload (gateway <-> gateway)   { environment, channel, user, change }
    wire frame     (gateway -> client)     { type: "membership.changed",
                                             payload: { channel, user, change } }
    outbox event   (api -> spine)          { id, type, environment_id, occurred_at, data }

The wire frame is unchanged from chapter 1.3 and `frames.test.ts` still asserts it. A client
already knows its own environment; telling it again would be the first place the platform leaked
a tenant identifier onto a socket for no purpose.

**The outbox event is a third shape and it is FR-WHK-02's, not this chapter's.** Its `type` is
`channel.member_added` or `channel.member_removed`, spelled as that requirement spells them,
because a customer's webhook subscription filters on those strings. Its `data.user` is the
**external** id, like every other api → consumer payload — and the three repository methods that
would build it hold only `users.id`, so the caller passes the external id down beside the internal
one. `sendMessage` takes `userExternalId` for exactly this reason.

---

## 3. The subject grammar

    member:{channel_id}        every instance holding a member of that channel
    member:{env}:{user}        every instance holding a connection for that user

**Both are needed and neither is redundant** (research R1). A removal reaches both audiences
through the first, because the removed user is still a member at the moment of publish. An
addition cannot: the instance holding the new member is not subscribed to that channel yet, so the
second shape is the only way to reach it.

`presence:{env}:{user}` is a Redis **key** and `member:{env}:{user}` is a pub/sub **channel**.
Different namespaces, no collision — but the two now read alike in a log line, which is worth a
sentence in the chapter rather than a discovery.

| Subject | Subscribed when | Unsubscribed when | Counted |
|---|---|---|---|
| `member:{channel_id}` | an instance's first local member of the channel connects | its last one leaves **or is removed** | reference-counted per channel, like `chan:` and `presence:` |
| `member:{env}:{user}` | a user's first connection on the instance | their last one closes | reference-counted per user |

**The "or is removed" is the new edge.** Every other unsubscribe in this system is driven by a
socket closing. This one is driven from outside the connection's lifecycle, and it is the first
caller of the reference counters that is not the connection's own open or close path.

---

## 4. State this feature mutates while a socket is open

| State | Owner | Immutable until now | What changes it |
|---|---|---|---|
| `connection.channelIds` | `registry.ts`, built once at connect | yes, since chapter 2.5 | an add inserts, a removal deletes |
| `fanout` reference counts | `fanout.ts` | driven by open and close only | a removal decrements, an add increments |
| `presence` reference counts | `presence.ts` | same | same |
| the user's ban flag | read once at connect | yes | a ban revokes every channel at once |
| **`connection.buffer`** | `session.ts`, filled by `deliver` while the connection is `buffering` | yes | **a removal drops that channel's frames from it** (FR-029) |

**Everything in the first column is read on the delivery path.** `registry.subscribersOf` reads
`channelIds` on every frame, so a mutation that is not atomic with respect to a delivery in flight
is a defect that will present as an occasional stray frame rather than as a failure.

**The buffer was missing from this table for seven analysis passes**, and it is the row that cost
a CRITICAL. `flushable(buffer, marks)` at `session.ts:632` filters on `frame.seq` and not on
membership, so a removal that lands mid-resume unsubscribes the channel and the frames already
buffered for it flush afterwards — FR-RTM-10 violated by a flush rather than by a subscription,
with every other test in this feature passing. A table of what a feature mutates is exactly where
that belongs, and a requirement, a task, a test, two traceability rows, a contract clause and a
success criterion all named it before this table did.

---

## 5. The transitions, and the one ordering that is a requirement

    ADD      row written -> outbox row (same tx) -> commit
                         -> publish member:{channel_id}   existing members are told
                         -> publish member:{env}:{user}   the new member's instances
                            -> subscribe chan:, presence:, member:{channel_id}
                            -> insert into connection.channelIds
                            -> send the frame

    REMOVE   row deleted -> outbox row (same tx) -> commit
                         -> publish member:{channel_id}   ONE publish, both audiences
                            -> every instance: send the frame to local members
                            -> the affected user's instance, and only it:
                                 send the frame to that user      <- FIRST
                                   (its own path: neither phase nor marks, FR-030)
                                 delete from connection.channelIds
                                 drop that channel's frames from connection.buffer (FR-029)
                                 decrement chan:, presence:, member:  <- SECOND

**The two middle steps are the resume path, and they are easy to leave out** — this sequence did
for seven passes. The buffer holds messages for a channel the user is no longer in, and the notice
itself must not join them: buffered, it arrives after the cut-off, or FR-029's own filter drops it
and it never arrives.

**`FIRST` and `SECOND` are FR-008 and they are not an implementation detail.** Cut-then-send makes
the notice itself a frame delivered to a client whose membership no longer grants access, which is
the clause this chapter exists to satisfy. The ordering is a property of one instance's own
sequence — the fabric guarantees nothing about order between two publishes, so it must not be
asked to.

    BAN      users.banned = true -> outbox row -> commit
                                 -> publish member:{env}:{user} once
                                    -> the instance drops every channel for that user

A ban publishes **once per user**, not once per channel. It is the only change whose scope is a
user rather than a pair.

---

## 6. What is deliberately not modelled

- **A role change.** `change` has two members and neither means "role" (FR-006). This is a fact
  about the frame chapter 1.3 published.
- **Archiving.** The members are unchanged and the api already refuses sends (chapter 3.15). No
  membership event.
- **Channel deletion.** Nothing deletes a channel. If that changes it is a removal for every
  member, and the shape above already covers it.
- **Order between two publishes.** A removal and an addition for the same pair may arrive in
  either order. The later database write is the truth and the design does not attempt to make the
  fabric agree; the backstop (research R3) is what converges them.
