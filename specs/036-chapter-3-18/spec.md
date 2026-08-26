# Feature Specification: chapter 3.18 — the message that never arrived

**Feature directory**: `specs/036-chapter-3-18/`
**Created**: 2026-08-26
**Status**: in planning
**Predecessor**: `specs/035-chapter-3-17/` (chapter 3.17, the sender a message never had)

## Summary

A customer's server sends a message over REST. A member of that channel is connected to a
socket. The message does not arrive.

Chapter 3.12 recorded this and named **two** independent mechanisms. Chapter 3.17 removed one —
every message now carries a sender, so the backfill has no reason to drop it, and **a resume
now delivers a REST-sent message**. The other mechanism stands: the api publishes to no
fan-out, so nothing arrives *live*. This chapter is that publish.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — a REST-sent message reaches a connected member (Priority: P1)

A customer's build server posts to `POST /v1/channels/:channelId/messages`. A teammate has the
app open, is a member of that channel, and is connected to a socket. The message appears
without the client polling, refetching, or reconnecting.

**Independent test**: send over REST as a bot; watch a `message.created` frame arrive on a
socket that was already open.

### User Story 2 — it works when the sender and the recipient are on different instances (Priority: P1)

Two gateway instances. The recipient's socket is held by one; the api that accepted the REST
send has no relationship with either. The message arrives.

**Independent test**: two gateway processes, a member connected to each, one REST send — both
receive it.

### User Story 3 — a message does not reach somebody who may no longer see it (Priority: P2)

A user is removed from a channel. A message is sent to that channel seconds later. It does not
appear on their socket.

**Independent test**: remove a member over the public route, send, and assert nothing arrives on
their open socket within the clause's window.

### Edge cases

- **A recognised idempotent retry must not deliver twice.** The gateway's own publisher already
  refuses this; the api's must too, and the reason is the same — storage safety is not delivery
  safety.
- **A send whose channel has no connected member** publishes to a subject nobody is subscribed
  to. That frame is gone, and that is correct rather than a loss.
- **A send that is refused** — banned sender, archived channel, quota exhausted, a key naming a
  person — must publish nothing. Nothing that did not commit may be delivered.
- **Redis is unavailable.** The send must still succeed. Delivery is not durability, and
  refusing a paying customer's write because a cache is down is the failure direction chapter
  3.8 already decided against.
- **The same user on several connections** must receive the message on each of them.
- **A legacy senderless row** cannot be delivered live any more than it can on resume: the frame
  contract requires a sender. Nothing new produces one, so this is a statement rather than a
  path.

## Requirements *(mandatory)*

### The clause this chapter is about, and the one the plan named

- **FR-001**: The plan's row names **FR-RTM-05** ("shall emit real-time events for message
  creation, edit, deletion, membership change, presence change, and typing"). The clause more
  directly unmet is **FR-RTM-01**: *"A connected client shall receive messages for every channel
  of which it is a member, without per-channel subscription."* P1, verification by test. A
  REST-sent message reaching no connected member is a violation of FR-RTM-01 today, and the
  chapter MUST cite the clause it actually satisfies.
- **FR-002**: **No SRS amendment is required, and the chapter MUST say so.** Unlike chapter
  3.17, whose gate was an amendment, both the requirement and the design already exist:
  FR-RTM-01 and FR-RTM-02 are P1 clauses, and `docs/05-sad.md` line 138 already draws
  `api -- "publish fan-out" --> redis`. This chapter builds a documented edge that was never
  built, and that is a different kind of gap from a missing clause.
- **FR-003**: The chapter MUST state what FR-RTM-05's other five event kinds do, because a
  reader will ask. Measured: `message.updated` and `membership.changed` have **zero** producers
  outside tests, nothing writes `messages.edited_at` or `messages.deleted_at`, and typing has no
  frame in the union at all. Only message creation is producible, so only message creation can
  be delivered.

### The publish

- **FR-004**: A message accepted over the public REST route MUST be published to the channel's
  fan-out subject after the write commits.
- **FR-005**: The publish MUST happen **after the acknowledgement**, not before. `docs/05-sad.md`
  states the ordering: *"Ack after commit, never before (FR-MSG-05). The Redis fan-out happens
  after the ack; a recipient may see the message milliseconds after the sender's ack, never
  before durability."*
- **FR-006**: A message accepted over the **internal** route (a socket send, forwarded by the
  gateway) MUST NOT be published twice. The gateway publishes for that path today, and two
  publishers on one path put the same message on every member's screen twice.
- **FR-007**: A recognised idempotent retry MUST publish nothing. It wrote no row.
- **FR-008**: A send that is refused MUST publish nothing.
- **FR-009**: The frame delivered MUST be byte-compatible with what a socket send produces
  today. A client cannot tell which entrance a message used, and `messageSchema` is the contract
  that makes that true.

### Failure, and what it must not take down

- **FR-010**: A fan-out publish that fails MUST NOT fail the send. The row is committed and
  acknowledged; delivery is best-effort by construction, and the SAD says so: *"Redis lost →
  presence + fan-out pause"*.
- **FR-011**: A publish failure MUST be observable — logged with the channel and the message, at
  a level an operator's alerting can find. A silent drop is the defect this chapter exists to
  remove, reintroduced one layer down.
- **FR-012**: The chapter MUST state what a client can and cannot conclude from having received
  nothing. A missing frame is not evidence a message does not exist; the resume path is the
  guarantee, and the fan-out is the optimisation.

### Membership at delivery

- **FR-013**: **FR-RTM-10** requires that events not reach a client whose membership no longer
  grants access, *"effective within 5 seconds of the membership change"*. Making REST sends
  deliver puts a second path under that clause. The chapter MUST establish where membership is
  checked for a REST-originated frame and MUST NOT assume the socket path's answer covers it.
- **FR-014**: A private channel's message MUST NOT reach a non-member's socket, by the same
  reasoning chapter 3.15 applied to the read paths. The delivery path is a fourth door onto
  FR-CHN-05 and MUST be tested as one.

### What this chapter closes, and what it does not

- **FR-015**: Chapter 3.12's `gaps.md` G1 MUST be closed rather than amended again. Chapter 3.17
  amended it from two mechanisms to one; this chapter removes the last one. A gap that has been
  half-closed twice and never closed is a record nobody trusts.
- **FR-016**: Chapter 3.14's Phase 2 verdict MUST be re-examined. Its concrete half was that an
  outsider who sends over REST and waits on a socket cannot succeed and no document says so.
  This chapter makes the attempt succeed; the chapter MUST state whether the verdict is
  satisfied or whether its documentation half remains.
- **FR-017**: Presence is **not** in scope. FR-RTM-06 and FR-RTM-07 are chapter 3.19, and
  FR-CHN-05's third verb stays unbuilt. The chapter MUST say so rather than leaving a reader to
  infer it from silence.

### Key Entities

- **The fan-out subject** — `chan:{channelId}` today, published by the gateway and subscribed by
  every gateway instance. This chapter adds a second publisher; it introduces no new subject and
  no new frame type.
- **A published frame** — a `message.created` payload conforming to `messageSchema`. Not a new
  entity; the same one the socket path already puts on the wire.

## Success Criteria *(mandatory)*

- **SC-001**: A member with an open socket receives a message sent over REST, with no client
  action in between.
- **SC-002**: The same holds when the sender's api and the recipient's socket are on different
  instances.
- **SC-003**: A socket-originated send delivers exactly once, verified by count rather than by
  observing that a message arrived.
- **SC-004**: A refused send, and a recognised retry, each deliver nothing.
- **SC-005**: With the fan-out unavailable, a REST send still returns 201 and the message is
  readable from history.
- **SC-006**: A user removed from a channel receives no message sent after the removal, within
  FR-RTM-10's five seconds.
- **SC-007**: A non-member's socket receives nothing from a private channel.
- **SC-008**: A client cannot distinguish a REST-originated frame from a socket-originated one.
- **SC-009**: Chapter 3.12's G1 is closed, and this feature's traceability map cites FR-RTM-01
  and FR-RTM-02 in both directions.
- **SC-010**: The sealed outsider sends over REST, waits on a socket, and succeeds — the exercise
  chapter 3.14 recorded as impossible.
- **SC-011**: The chapter is inside the series' 2,000–4,000 prose-word bound, and every fenced
  file replays onto the platform repository.

## Assumptions

- **The fan-out subject and the frame stay as they are.** No new subject, no new frame type, no
  change to `messageSchema`. A published client tolerates neither, and chapter 3.17's frame-shape
  assertion is what holds it still.
- **The api already reaches Redis.** `services/api/src/limits/store.ts` uses it for rate
  limiting, so this is not a new dependency — measured, not assumed.
- **The publish happens on the send path, not in the outbox consumer.** The SAD draws
  `api → redis` directly and specifies the ordering relative to the ack. The consumer's handler
  is `createRecorder`, which records; moving delivery there would add the outbox relay's latency
  to every message and contradict a drawn edge. The plan may revisit this with a measurement,
  but the architecture document is the default.
- **Best-effort delivery is the existing contract**, not a compromise introduced here. The
  gateway's own comment says a frame that misses a subscriber "is simply gone", and the resume
  path is the guarantee.
- **The lane environment is the one chapter 3.17 recorded**: Postgres on 15432, the two internal
  credentials, NATS on 4222, and the compose `services` profile stopped.

## Dependencies

- **Chapter 3.17 is closed** (tagged `part3-ch17`). Every message carries a sender, which is what
  makes a REST-sent row deliverable at all — the frame contract requires one.
- **Chapter 3.12's gap record** is the thing being closed, and it has already been amended once.
- **Chapter 3.14's Phase 2 verdict** is the outsider criterion this chapter is measured against.

## Out of scope

- **Presence** (FR-RTM-06, FR-RTM-07, FR-CHN-05's third verb) — chapter 3.19.
- **Typing indicators** (FR-RTM-08) — no frame exists in the union.
- **Message edit and deletion events** (FR-RTM-05's second and third kinds) — nothing writes an
  edit or a tombstone, so there is nothing to emit. Recorded, not built.
- **Membership-change events** — the writer exists and the frame exists, but no producer connects
  them. A candidate for a later chapter, and named here so it is not assumed delivered.
