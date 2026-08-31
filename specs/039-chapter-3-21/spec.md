# Feature Specification: Chapter 3.21 — the typing indicator, and the frame a client may not send

**Feature Directory**: `specs/039-chapter-3-21`
**Created**: 2026-08-31
**Status**: Draft
**Predecessor**: chapter 3.20, tagged `part3-ch20` — fence predecessor is
`git rev-parse part3-ch20^{commit}`, not the annotated tag

---

## What this chapter is, after the premises were checked

**The brief for this chapter was wrong in two places, and both were checked before a
requirement was written.** They are recorded here rather than in research because they
change the scope rather than inform it.

**WRONG 1: "the one remaining kind that reuses `chan:{channel_id}`."** ADR-19 refused
`chan:` for presence because the message path is typed to messages at **seven** points — ADR-19 said three and
analysis pass 4 counted them. All seven are intact:

    services/gateway/src/fanout.ts:44   onDelivery(handler: (channelId, message: Message) => void)
    services/gateway/src/fanout.ts:47   publish(message: Message): Promise<void>
    services/gateway/src/fanout.ts:80   messageCreatedSchema.shape.payload.safeParse(parsed)
    services/gateway/src/session.ts:223 send(socket, { type: "message.created", payload: message })

Nothing about typing makes that argument weaker than it was for presence, and seven
places is a worse case than the three ADR-19 argued from. Riding `chan:`
still means editing the highest-volume path in the system to carry the lowest-volume
traffic on it, and it still makes cross-kind mis-delivery a property tests defend rather
than one the topology guarantees. **This chapter takes the fourth grammar**, and the
interesting part is that the reasoning is now a pattern rather than a judgement call.

**WRONG 2: "typing is the small one."** It is the first chapter in this platform that must
open a **second inbound frame**, and that is a larger change than a subject grammar.

    services/gateway/src/session.ts:948
    if (frame.data.type !== "message.send") { … unknown_frame_type … close(4002) }

`message.send` is the only frame a client may utter. Chapter 3.12's direction gauntlet
states it as a row — *"the only frame a client may utter (session.ts)"* — and classifies
`typing` as **outbound**, *"server-fanned; a client claiming one could type as anybody"*.
So today a client cannot tell the server it is typing, and the server has no other way to
find out.

**AND THE PUBLISHED FRAME CANNOT SAY "STOPPED".** `typingSchema` has been in the protocol
union since chapter 1.3 with a payload of exactly two fields:

    export const typingSchema = z.strictObject({
      type: z.literal("typing"),
      payload: z.strictObject({ channel: …, user: … }),
    });

No `state`, no expiry, no `until`. There is no frame for "X stopped typing" and adding one
means editing `frames.ts`, which chapters 3.19 and 3.20 both refused to do. **The expiry
therefore belongs to the receiving client by construction**, not by preference — and that
is the answer to the brief's open question about Redis state, arrived at from the protocol
rather than from arithmetic.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Mai sees that Tuan is typing (Priority: P1)

Mai has #incidents open. Tuan starts typing a reply on another gateway instance. Mai sees
an indicator naming Tuan, and it disappears on its own when he stops.

**Why this priority**: it is the whole feature. FR-RTM-05's sixth frame kind is discharged
by this scenario and nothing else. **FR-RTM-08 is discharged in part** — the platform's half
— and the other half is the receiving client's timer, which is FR-009c's verdict rather than
a completion this story can claim.

**Independent Test**: two sockets on two instances, one member of a shared channel signals
typing, assert the other receives a `typing` frame naming the first, and assert the
signaller does not receive their own.

**Acceptance Scenarios**:

1. **Given** Mai and Tuan are members of #incidents on different gateway instances,
   **When** Tuan's client signals that he is typing, **Then** Mai receives exactly one
   `typing` frame whose payload names Tuan and #incidents.
2. **Given** Tuan has signalled typing, **When** he signals again **after** the renewal
   interval has elapsed, **Then** Mai receives a second frame — renewal is a repeat, not a
   state change, and there is no "already typing" to suppress.
3. **Given** Tuan has signalled typing, **When** he signals again **inside** the interval,
   **Then** Mai receives nothing further — the interval is what stops a keystroke becoming
   a publish (FR-012).
4. **Given** Tuan signals typing, **When** he stops and the expiry elapses, **Then** no
   further frame is sent and Mai's indicator clears on her own timer.
5. **Given** Tuan signals typing in #incidents, **When** Linh is a member of #ops only,
   **Then** Linh receives nothing.
6. **Given** Tuan signals typing, **Then** Tuan does not receive his own indicator.
7. **Given** Tuan signals typing several times, **When** he then sends a message, **Then**
   his send budget is what it was — a typing signal spends no message quota (FR-014).
8. **Given** Mai has received a typing frame, **When** Tuan sends nothing further, **Then**
   no frame of any kind reaches Mai for that channel until he signals again (FR-009a).
9. **Given** Linh is added to #incidents **while already connected**, **When** Tuan signals
   typing there, **Then** Linh receives the frame without reconnecting (FR-004a).

### User Story 2 - A client may say it is typing, and may not say anything else (Priority: P1)

The socket has accepted exactly one inbound frame for twenty chapters. This adds the
second, and the refusal that guarded the first has to keep working for everything else.

**Why this priority**: the inbound seam is where a protocol is attacked. Chapter 3.12 built
a gauntlet asserting that every outbound frame type is refused when a client utters it, and
this chapter moves one frame across that line. A widened check that accidentally admits a
third type is a client typing as somebody else, or worse.

**Independent Test**: send each frame type in the union from a client; assert the two
inbound types are accepted and every other type is refused with `unknown_frame_type` and
close 4002.

**Acceptance Scenarios**:

1. **Given** a connected client, **When** it sends the typing signal, **Then** the frame is
   accepted and the socket stays open.
2. **Given** a connected client, **When** it sends any other non-`message.send` frame type,
   **Then** it receives `unknown_frame_type` and the socket closes with 4002.
3. **Given** a connected client, **When** it signals typing for a channel it is not a member
   of, **Then** nothing is published and no member of that channel receives a frame.
4. **Given** a connected client, **When** it signals typing naming a different user, **Then**
   the identity on the wire is ignored and the connection's own identity is used.

### User Story 3 - A keystroke does not become a publish (Priority: P2)

A typing indicator renewed on every keystroke is a publish per keystroke. At NFR-SCL-01's
10,000 connections per instance that is the highest-frequency inbound path in the system.

**Why this priority**: the feature works without it and the platform does not survive it.
Separable because the delivery path is testable before the interval exists.

**P2 MEANS SEPARABLE, NOT OPTIONAL, AND THE DISTINCTION MATTERS HERE.** An earlier draft
put FR-014 — a typing signal must not spend the message send quota — in this story, where
stopping after the MVP would ship a cosmetic feature capable of exhausting a customer's
message budget. That requirement moved to US1, which is the story that first publishes.
What is left here is the interval itself, which changes a cost rather than a correctness
property.

**Independent Test**: signal typing faster than the renewal interval and assert the number
of frames other members receive is bounded rather than proportional to the signals sent.

**Acceptance Scenarios**:

1. **Given** a client signals typing repeatedly within one renewal interval, **When** the
   interval has not elapsed, **Then** at most one publish reaches the fabric.
2. **Given** a client exceeds the typing signal limit, **When** the next signal arrives,
   **Then** it is dropped without an error frame and without closing the socket.
3. **Given** two connections of one user typing in one channel, **When** both signal within
   one interval, **Then** both publish — the interval is per connection, not per user.

### Edge Cases

- A client signals typing and disconnects before the expiry elapses. **Nothing further is
  published and no frame ends it** — the signal itself was published, which is why an
  indicator is showing — and the receiver's timer clears it with no help from the server.
- A member is removed from the channel (chapter 3.20) while an indicator is showing for
  them. The removal frame arrives; the typing indicator clears on its own timer.
- Two members type at once. Each receiver holds one timer per (channel, user) and shows
  both.
- A user types on one connection while holding a second one in the same channel. **The
  second receives nothing**: the filter is by identity, not by socket, and the frame crosses
  the fabric with no socket reference to compare against. A test with one connection per
  user passes either way (FR-005).
- The fabric is unreachable when a signal arrives. The signal is dropped, the socket stays
  open, and one structured failure event is logged.
- A client signals typing for a channel that does not exist. Treated as a channel it is not
  a member of: nothing published, no error.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept an inbound signal on the socket by which a connected
  client states that it is typing in a named channel.
- **FR-002**: The inbound signal MUST be a distinct frame type from the outbound `typing`
  frame. A client MUST NOT be able to utter the outbound frame, and chapter 3.12's
  direction gauntlet MUST continue to assert that for every outbound type.
- **FR-003**: The set of frame types a client may send MUST be a named set with more than
  one member, and a test MUST assert its exact membership and its exact size. A third
  member MUST be a decision rather than an accident.
- **FR-004**: The system MUST deliver a `typing` frame to every other member of the named
  channel who holds a connection, across gateway instances.
- **FR-004a**: The typing subscription MUST follow membership for the whole life of a
  connection, not only at connect. A channel joined mid-connection MUST be subscribed and a
  channel revoked mid-connection MUST be released, **through the same two branches chapter
  3.20 built for its own fabric**. A fourth grammar makes both incomplete, and the failure
  is silent: a user added mid-connection would receive messages and presence but no typing.
- **FR-005**: The signalling user MUST NOT receive their own typing frame **on any of their
  connections**. The filter is by identity, not by socket: a user may hold several
  connections (chapter 3.22 caps them at five), the fabric frame carries no socket
  reference, and FR-011a **requires** the multi-connection case to exist by making the
  renewal interval per connection. A test with one connection per user passes whether the
  filter is per user or per socket, and the wrong one shows a user their own indicator on
  their own second device.
- **FR-006**: The user named in a delivered frame MUST be the authenticated identity of the
  signalling connection, never a value taken from the inbound payload.
- **FR-007**: A signal naming a channel the connection is not a member of MUST publish
  nothing and MUST NOT reveal whether the channel exists.
- **FR-008**: `packages/protocol/src/frames.ts`'s `typingSchema` MUST NOT change. The frame
  a client receives is what chapter 1.3 published and `frames.test.ts` asserts. **A command
  MUST verify it** — the file is edited by this chapter to add a sibling schema, so "not
  changed" is a claim about one region of a file that did change.
- **FR-009**: The indicator MUST expire without any frame being sent to end it. Expiry is
  the receiving client's timer, five seconds from the last frame for that (channel, user).
- **FR-009a**: A test MUST assert that after a signal, **no further frame of any kind
  reaches the watcher** for that channel until another signal is sent. "The server sends
  nothing to end an indicator" is otherwise satisfied by a server that sends nothing at all,
  and it is the obligation FR-RTM-08 actually states.
- **FR-009b**: The chapter MUST state the client's side of the contract — five seconds from
  the last frame, per (channel, user) — because it is the half of this requirement no test
  in this repository can reach.
- **FR-009c**: **The chapter MUST record an honest verdict on FR-RTM-08 rather than assert
  the clause is closed.** That clause reads *"Typing indicators **shall** expire
  automatically after 5 seconds without renewal"* — a system obligation — and this design
  delegates the expiry to the customer's own application. There is no SDK in this
  repository, so "the client" is code the platform does not own, and the server cannot end
  an indicator: `typingSchema` carries no state field and no frame exists to send.

  The verdict to record is **met, with the boundary named**: the platform emits and stops
  emitting, the disappearance is the client's, and the clause's second half — *"shall not be
  persisted"* — is met absolutely because nothing is stored anywhere. Nothing else the
  platform could build would satisfy the first half without editing `frames.ts`, which this
  chapter refuses for chapters 3.19 and 3.20's reason.

  **And the verdict MUST reach a published document, not only the chapter and the
  chapter's notes.** `docs/04-srs.md` is published and mirrored, its FR-RTM-08 reads as a
  platform obligation, and FR-019 forbids editing the clause — so the boundary goes in the
  SAD as its own ADR, which is published and is the instrument for a decision whose
  consequence a requirement's plain reading does not convey. A verdict recorded only where
  the customer cannot read it is the same defect as a correction that reaches the argument
  and not the instruction.

  **What is forbidden is claiming closure without the argument.** Chapter 3.20 recorded
  FR-RTM-10 as met on the happy path and bounded by an interval under fabric loss, with the
  55-second excess stated rather than hidden; chapter 3.18 refused to narrow a clause until
  the code passed. A design that cannot execute a *shall* has to say so.
- **FR-010**: Nothing about a typing indicator MUST be persisted — no database row, no
  Redis key, no outbox event.
- **FR-011**: The renewal interval MUST be defined as a number with its arithmetic recorded
  against NFR-SCL-01's 10,000 connections per instance, and MUST be shorter than the
  five-second expiry by a margin that is stated rather than assumed.
- **FR-011a**: The renewal interval MUST be enforced **per connection and per channel**,
  and the enforcement MUST be authoritative at the gateway rather than trusted to the
  client. Two connections of one user typing in one channel are two independent signals; a
  well-behaved client and a hostile one MUST cost the fabric the same.
- **FR-012**: Repeated signals from one connection for one channel within one renewal
  interval MUST produce at most one publish.
- **FR-013**: A signal dropped for arriving inside the renewal interval MUST be dropped
  **silently** — no error frame, no close code, and no log line. A typing indicator is not
  worth a disconnection, and a line per keystroke is the unbounded output NFR-OBS-01 exists
  to prevent.
- **FR-013a**: The system MUST NOT add a per-environment typing quota. The per-connection
  interval already bounds each connection to one publish per interval, so an
  environment-scoped counter would bound a rate that is already bounded and would refuse one
  tenant's users on account of another's.

  **AND THE REMAINING RISK IS NOT FR-RTM-09's — AN EARLIER DRAFT SAID IT WAS.** That clause
  caps connections **per user** at five; a tenant with 3,000 users may hold 15,000
  connections and be fully compliant, so chapter 3.22 does not bound this and never will.
  What bounds the per-instance publish rate is the connection count itself: 0.5 publishes
  per second per connection, so **NFR-SCL-01's 10,000 per instance is 5,000 per second worst
  case.** That clause is a budget the SAD's own risk register calls *"a budget, not a
  measurement"* (R2, its single most urgent action item), and nothing enforces it.

  **This chapter neither introduces that risk nor can fix it**, and a per-tenant counter
  would not have: the thing at risk is an instance and a tenant counter bounds a tenant. The
  chapter MUST state the arithmetic and name R2 rather than defer to a clause that cannot
  accept the deferral.
- **FR-014**: A typing signal MUST NOT consume the message send quota (FR-RTL-01), and a
  test MUST assert the send budget is unchanged across typing signals. **This is verified in
  the story that first publishes**, not in the story that adds the interval — a cosmetic
  feature exhausting a customer's message quota is an outage, and it must not be reachable
  by stopping after the MVP.
- **FR-015**: A fabric failure on the typing path MUST NOT fail the connection, MUST NOT
  close the socket, and MUST be logged once with a stable event name.
- **FR-016**: The typing path's log vocabulary MUST be a closed set of names, a test MUST
  reach each, and the test MUST assert the set of names an instance actually emitted rather
  than what a grep finds.
- **FR-017**: A typing frame MUST NOT reach a client as another kind, and no other kind MUST
  reach a client as a typing frame. After this chapter the fabric carries five subject
  shapes.
- **FR-018**: A typing signal MUST NOT enter the resume buffer and MUST NOT be replayed on
  reconnect. It carries no sequence and expires in five seconds; a replayed one is a lie
  about the present.
- **FR-019**: No SRS clause MAY change. If a clause is found to say something this chapter
  cannot satisfy, the chapter records the mismatch rather than editing the clause.
- **FR-019a**: Every published document this chapter makes false MUST be corrected, and the
  search MUST cover `docs/` as well as both locales of the tutorial. **`docs/` holds the
  product's claims and a customer reads those**; the tutorial holds a chapter's narrative
  claims. Two are outside the tutorial's narrative and both were
  missed by the first search: `docs/08-error-reference.md`'s `unknown_frame_type` entry names
  `message.send` as the only inbound frame, in the reference for the error code this
  chapter's own seam produces; and chapter 3.19 carries a **fenced** IOU from chapter 2.6
  promising that typing reuses `chan:` — a promise made to the reader, which chapter 3.20
  examined and cleared because it was not contradicted by *that* chapter.
- **FR-020**: The chapter MUST state which of FR-RTM-05's six frame kinds now have
  producers and MUST NOT claim FR-WHK-02 or FR-RTM-09 are affected by this chapter.
- **FR-021**: The chapter MUST state that the fourth subject grammar was taken rather than
  avoided, with **the seven typed points R1 measured** cited as the reason — and MUST say
  that ADR-19's own record counts three. The plan for Part 3's closing chapters assumed the
  opposite conclusion, and **this requirement said "three" until analysis pass 12**: the
  correction landed in research, the contract and the plan, and left the MUST that cites it
  behind. FR-020 and FR-021 are verified by a sentence, so nothing downstream would have
  caught the chapter publishing the number its own research disproved.

### Key Entities

- **Typing signal (inbound)**: a client's statement that it is typing in one channel.
  Carries a channel; carries no user, because the connection supplies it. Never stored.
- **Typing frame (outbound)**: `{ type: "typing", payload: { channel, user } }` — unchanged
  since chapter 1.3. Carries no state and no deadline, which is why the expiry is the
  receiver's.
- **The typing fabric subject**: the fourth grammar, per channel, carrying no membership
  question and no sequence.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A member of a shared channel sees another member's typing indicator within
  the same budget a message takes, on a different gateway instance.
- **SC-002**: The indicator disappears five seconds after the last signal, with no message
  crossing the network to end it — asserted as **no frame of any kind arriving** after a
  signal, not as the absence of a frame nobody sends. **The disappearance itself is the
  client's and this criterion does not claim otherwise** (FR-009c).
- **SC-003**: One connection signalling typing continuously in one channel produces no more
  than one publish per renewal interval, regardless of keystroke rate, and a second
  connection is unaffected by the first.
- **SC-004**: A client cannot cause any other user's name to appear in a typing indicator.
- **SC-005**: A user who shares no channel with the signaller receives nothing, in a run
  where a channel member does receive.
- **SC-006**: Every frame type except the named inbound set is still refused with
  `unknown_frame_type` and close 4002.
- **SC-007**: Typing signals leave the message send budget unchanged.
- **SC-008**: With the fabric unreachable, the socket stays open, no error reaches the
  client, and one failure event is logged.
- **SC-009**: A reconnecting client receives no typing frames for signals sent while it was
  away.
- **SC-010**: FR-RTM-05's six frame kinds have four producers after this chapter, and the
  two without them are named with the reason each waits.

---

## Assumptions

- **The expiry lives in the receiving client, and the protocol forced that.** With no
  `state` field and no "stopped" frame, the server cannot end an indicator. Recorded as an
  assumption because it could be reversed by editing `frames.ts`, which this chapter
  refuses for chapters 3.19 and 3.20's reason: the frame a client parses is what chapter
  1.3 published.
- **A fourth subject grammar, not `chan:`.** ADR-19's argument holds unchanged and
  **strengthened**: its record counts three typed points, and running the verification
  returned eight lines covering seven. All seven were verified present before this was
  assumed.
- **The gateway holds no state about an INDICATOR, and it does hold state about its own
  recent publishes.** These are two claims and the first version of this bullet said only
  the strong one — "the gateway holds no typing state" — which the debounce below
  contradicts. Nothing anywhere knows an indicator exists: no table, no Redis key, no
  server timer, nothing to refresh, which is why nothing can announce that one stopped.
  What the gateway keeps is a last-publish timestamp per (connection, channel), in memory,
  with a lifetime of one renewal interval. **So the cost against NFR-SCL-01's 10,000
  connections per instance is a publish rate plus a bounded map**, and the bound is the
  number of (connection, channel) pairs typed in within the last interval — an entry is
  written on publish and deleted when it goes stale, on close, or when a revocation drops
  the channel. Conflating the two claims costs twice: a reader finds the spec contradicting
  itself, and someone eventually deletes the map believing FR-010 forbids it. **FR-010
  forbids persistence, and an in-memory map is not that.**
- **The inbound frame is new rather than the existing `typing` made bidirectional.** A
  bidirectional frame would let a client name a user, which is exactly what chapter 3.12's
  gauntlet row forbids.
- **`message.deleted`, `message.updated` and the webhook names are out of scope.** They are
  chapters 3.23 and 3.24 in the plan that closes Part 3.

- **The renewal interval is a gateway-held debounce, not a token bucket.** Analysis pass 1
  found that the existing limiter cannot express it: `spend(environmentId, operation, limit)`
  keys on `rl:{environmentId}:{operation}:{window}` with a 60-second window, which is
  per tenant and per minute. A 2-second rule per connection and per channel is neither.
  **The planned third bucket is not built** — see FR-013a.

---

## Out of scope

- FR-RTM-09's five-connection cap — chapter 3.22, and a design change before it is an
  implementation.
- FR-MSG-07, FR-MSG-08 and FR-MSG-10 — editing and deleting a message, chapter 3.23.
- FR-WHK-02's five remaining event types and FR-WHK-01's type registry — chapter 3.24. The
  registry currently accepts any string, which chapter 3.20 found and did not fix.
- Any change to `frames.ts`'s existing schemas.
