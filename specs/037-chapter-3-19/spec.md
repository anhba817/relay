# Feature Specification: chapter 3.19 — presence, and who is allowed to see it

**Feature Branch**: `037-chapter-3-19`

**Created**: 2026-08-27

**Status**: Draft

**Input**: User description: "Start chapter 3.19"

## Summary

`presence.changed` has been in the protocol union since chapter 1.3 published
`packages/protocol/src/frames.ts`. Its states are `online` and `offline`, its comment cites
FR-RTM-06 and hands the scoping question to FR-RTM-07, `frames.test.ts` asserts its shape,
chapter 3.12's isolation gauntlet classifies it outbound and proves a client cannot forge one.
Nothing has ever produced one.

**This chapter was assigned by name, two chapters ago, and this spec did not say so until analysis
pass 12.** Chapter 3.17's `gaps.md` item 2 reads *"Presence is a declared frame with no sender —
FR-RTM-05, FR-RTM-06, FR-RTM-07"*, owner *"chapter 3.19. Carried forward; still open, and now it has
a chapter."* It checked the claim rather than assuming it: *"the only occurrence of 'presence' in
`services/gateway/src` is the English word, in a comment about cursors."*

This is chapter 3.18's shape one layer up. There, the fan-out had exactly one publisher and a
REST send reached no socket; here, the frame exists, the grammar is tested, the refusal is
tested, and the event does not exist. Chapter 3.18's own close-out states it as the inheritance:
`FR-RTM-05  one of six event kinds has a producer. Presence change is 3.19's.`

Three things this chapter has to settle before it can build anything, all found by reading:

**The fan-out fabric is typed to messages end to end, and ADR-10 requires it not to be.** *(Line numbers in this section describe the tree at the fence predecessor `caeabc9`.)*
ADR-10 (`docs/05-sad.md:901`) says presence "transitions publish on the affected channels'
subjects only" — the same `chan:{channel_id}` subjects the messages use. But
`services/gateway/src/fanout.ts:47` declares `publish(message: Message)`, line 80 parses every
arriving payload with `messageCreatedSchema.shape.payload` and logs `fanout.invalid_payload` on
anything else, and `services/gateway/src/session.ts:194` sends the literal `{ type: "message.created", payload:
message }`. A presence payload published on a channel subject today produces a log line, not a
frame. No document says the fabric has to become multi-kind; ADR-10 assumes it already is.

**Open question 3 has two answers in three places.** SRS Appendix C row 3 lists *"Should presence
be opt-in per channel to reduce fan-out at scale?"* as open, owner Architecture. ADR-10's status
line says it "resolves SRS Open Question 3 (provisionally)". The SAD's own
deliberately-not-a-service table (`docs/05-sad.md:210`) points at it as still open — *"If presence
fan-out dominates gateway CPU (see Open Q3, SRS)"*. Chapter 3.18 spent three analysis passes on
`:138` versus `:248` before anyone read ten lines further; this is the same defect in the same
document.

**The mechanism chapter 3.18 assigned here is not the mechanism presence needs.** Chapter 3.18's `gaps.md` item 4
gives FR-RTM-10 to this chapter, reasoning that *"presence needs the same missing mechanism —
something that tells a gateway a membership changed."* It does not. Presence needs the subject's
channel set at the instant of a transition, and `POST /internal/session` already supplies it
(`session.controller.ts:129`). FR-RTM-10 needs that set **re-read** while a socket is open, which
is a second feature. The premise is wrong and the item is still real — see FR-020.

## User Scenarios & Testing *(mandatory)*

### User Story 1 — a member sees a co-member arrive (Priority: P1)

Two users share a channel. One is connected and watching; the other opens a socket. The watcher
receives `presence.changed` with state `online` for the arriving user, with no request and no
polling. It holds when the two are on different gateway instances, because a client cannot be
told which instance anybody landed on.

**Why this priority**: it is the whole clause. FR-RTM-06 has no producer and FR-RTM-05's presence
half has no event; without this there is nothing to scope, nothing to grace, and nothing to
verify.

**Independent Test**: connect a watcher, connect a subject, assert one `online` frame naming the
subject. Run it again with two gateway instances and one Redis.

**Acceptance Scenarios**:

1. **Given** two members of one channel and one of them connected, **When** the other opens a
   socket, **Then** the connected member receives `presence.changed` with `state: "online"` and
   the subject's user id.
2. **Given** the same two members on different gateway instances, **When** the subject connects,
   **Then** the watcher still receives it.
3. **Given** a watcher who shares three channels with the subject, **When** the subject connects,
   **Then** the watcher receives exactly one `online` frame, not three.
4. **Given** a subject already online on one connection, **When** the subject opens a second,
   **Then** no further `online` frame is delivered to anybody.

---

### User Story 2 — the grace period, so a tunnel does not look like a departure (Priority: P1)

A user on a phone loses signal and reconnects eleven seconds later. Nobody sees them leave.
A user who closes the app and does not come back is shown as offline, once, after the grace
period FR-RTM-06 names.

**Why this priority**: the 30-second grace period is the clause's second half and the reason the
state is not simply "socket open". Without it every lift ride is a departure and a return, and
the events are noise. It is also where the design is hardest: a TTL expiring in Redis publishes
nothing, and the instance that saw the disconnect may be gone before the grace period ends.

**Independent Test**: close the subject's only connection, assert nothing for 30 seconds, assert
one `offline` after. Separately: close it and reconnect inside the window, assert no `offline`
ever arrives — including to a watcher on a third instance.

**Acceptance Scenarios**:

1. **Given** a subject with one open connection, **When** it closes and stays closed, **Then**
   watchers receive exactly one `offline` frame, and not before 30 seconds have passed.
2. **Given** the same, **When** the subject reconnects 10 seconds later, **Then** no `offline`
   frame is ever delivered, and no second `online` frame either.
3. **Given** the same, **When** the subject reconnects 10 seconds later **to a different gateway
   instance**, **Then** the outcome is identical.
4. **Given** a subject with two open connections, **When** one closes, **Then** no `offline`
   frame is delivered at any time while the other remains open.
5. **Given** a subject whose two connections are on two different instances, **When** the one on
   instance A closes, **Then** no `offline` frame is delivered.

---

### User Story 3 — a stranger learns nothing (Priority: P1)

Presence is a statement about a person. FR-RTM-07 bounds who may hear it to users sharing at
least one channel with the subject, and FR-CHN-05's third verb forbids observing presence in a
private channel of which the observer is not a member. This story is the negative half, and it is
the half a test can pass while proving nothing — a watcher who receives no frame receives no
frame whether the scoping works or the producer is broken.

**Why this priority**: constitution principle I. A leak here is a correctness defect, not a
cosmetic one, and the same suite that proves delivery must prove non-delivery against a producer
observed working in the same run.

**Independent Test**: one socket that must receive the frame and one that must not, in the same
run, asserted together — the shape chapter 3.12's gauntlet uses.

**Acceptance Scenarios**:

1. **Given** a user sharing no channel with the subject, **When** the subject connects or
   disconnects, **Then** that user receives no presence frame, while a co-member in the same run
   receives one.
2. **Given** a private channel and a non-member of it, **When** a member of that channel
   connects, **Then** the non-member receives no presence frame.
3. **Given** a user in a different tenant, **When** the subject connects, **Then** that user
   receives no presence frame.
4. **Given** any connected client, **When** it utters a `presence.changed` frame itself, **Then**
   the gateway refuses it with `unknown_frame_type` and close code 4002.
5. **Given** a subject who is a member of no channel at all, **When** they connect, **Then** no
   presence frame is published to anybody.

---

### User Story 4 — presence failure costs nothing but presence (Priority: P2)

Redis is unavailable. Sockets still open, messages still deliver, sends still commit. ADR-10 is
explicit that presence loss is cosmetic and self-heals; this story is what makes that a tested
property rather than a sentence.

**Why this priority**: chapter 3.18's `gaps.md` records the trap directly — the fan-out's
`publish` swallows its own errors and resolves, so "the connect succeeded with Redis down" is
equally true of a presence path that does nothing at all. The assertion that carries the
requirement is the log line.

**Independent Test**: point the presence path at a dead port, connect a socket, assert the
connection establishes and a named error is logged. Then restore Redis and assert a subsequent
transition is published — the same test proves the path was alive.

**Acceptance Scenarios**:

1. **Given** Redis unreachable, **When** a client connects, **Then** the socket opens, the
   handshake completes, and the failure appears as one structured log event.
2. **Given** Redis unreachable, **When** a member sends a message over either entrance, **Then**
   delivery to connected members is unaffected.
3. **Given** Redis restored, **When** the next transition occurs, **Then** it is published
   without a restart.

---

### Edge Cases

- **A watcher who connects during the gap.** There is no presence snapshot: `connection.ack`
  carries `user`, `cursor`, `resume_ok` and `truncated` and nothing else. A client that connects
  after a co-member came online sees an empty roster until the next transition. No SRS clause
  requires a snapshot, so building one would need a clause first (constitution VI). Out of scope,
  recorded as a gap — and it is the difference between this chapter delivering the clause and
  delivering a usable feature.
- **The subject's own connections.** A subject shares every one of their channels with
  themselves, so the scoping rule includes them. Pinned rather than special-cased — see FR-011.
- **A deploy drain.** `docs/05-sad.md:634` stops the gateway accepting on SIGTERM and clients
  reconnect elsewhere. The 30-second grace period is what stops a rolling deploy from emitting an
  `offline` for every connected user, which is exactly what it is for. Worth one test, because
  a mass disconnect is also the worst case for whatever schedules the grace check.
- **A user with five connections closing all five.** FR-RTM-09's five per user is *not enforced*
  anywhere — `services/api/src/limits/policy.ts:13` mentions it in a comment and nothing counts.
  The grace period must therefore reference-count an unbounded set, and the last close is the one
  that matters.
- **Two transitions inside one grace window.** Close, reopen at 5 s, close again at 10 s. There
  must be exactly one pending offline decision and it must be answered by the state at the end of
  the window, not by the first close that scheduled it.
- **The instance that saw the disconnect dies inside the grace window.** Nothing publishes the
  `offline`, and the presence key expires silently. Watchers hold a stale green circle until the
  subject next transitions. Acceptable under ADR-10, and it must be stated in the chapter rather
  than discovered by a reader.
- **A presence payload arriving on a message subject, or the reverse.** Today's subscriber
  answers this with `fanout.invalid_payload`. Whatever carries two kinds must not let either be
  delivered as the other.
- **Redis pub/sub is at-most-once.** A presence frame that misses a subscriber is gone, and
  unlike a message there is no sequence, no cursor and no backfill to recover it. Presence has no
  resume path and must not be given one.

## Requirements *(mandatory)*

### The clauses this chapter is about

- **FR-001**: The chapter and its record MUST cite **FR-RTM-06** (states `online`/`offline`
  derived from connection state with a 30-second grace period), **FR-RTM-07** (delivery only to
  users sharing at least one channel with the subject), **FR-RTM-05**'s presence-change kind, and
  **FR-CHN-05**'s third verb (observe presence). Priorities are P1, P1, P1, P1.
- **FR-002**: No SRS clause text changes. All four clauses already say what this chapter builds;
  principle VI is satisfied by citing them.
- **FR-002a**: `docs/04-srs.md` Appendix C row 3 DOES change, and it is an appendix row rather
  than a clause. See FR-016.

### The producer

- **FR-003**: A user's transition from zero open connections to one MUST publish a
  `presence.changed` event with `state: "online"` naming that user.
- **FR-004**: A user's transition from one open connection to zero MUST publish
  `presence.changed` with `state: "offline"`, and MUST NOT publish it earlier than 30 seconds
  after the last connection closed.
- **FR-005**: An `offline` event MUST NOT be published if any connection for that user is open at
  the end of the grace period, including one opened after the close and including one held by a
  different gateway instance.
- **FR-006**: Opening a second or subsequent connection for a user already online MUST NOT
  publish a further `online` event. Closing one while others remain open MUST NOT publish an
  `offline` event.
- **FR-007**: A reconnection inside the grace period MUST publish nothing — neither an `offline`
  nor a repeated `online`. The state did not change.
- **FR-008**: The producer MUST derive state from connection state alone (FR-RTM-06). No client
  frame, no request parameter and no stored user preference may set it.
- **FR-009**: The gateway MUST NOT read the database on the presence path. ADR-05 forbids it and
  chapter 2.1's lint ban makes a violation a build failure.
- **FR-028**: Several last-closes for one user inside one grace window MUST resolve to exactly one
  offline decision, answered by the state at the end of the window rather than by the close that
  started it. Close, reopen at 5 s, close again at 10 s leaves one pending decision, not two.
  *Added by building the traceability map the second way: the edge case was listed and no
  requirement carried it.*

### Scope of delivery

- **FR-010**: A presence event MUST be delivered only to users sharing at least one channel with
  the subject (FR-RTM-07).
- **FR-011**: The subject's own connections are within that set and MUST receive the event. A
  pinned decision, not an accident: "only users sharing a channel with the subject" is an upper
  bound, both readings satisfy it, and one of them has to be tested.
- **FR-012**: A connection MUST receive at most one frame per transition, however many channels
  it shares with the subject. The payload carries `user` and `state` and no channel, so two
  copies are indistinguishable duplicates.
- **FR-013**: **Retired in analysis pass 11 — folded into FR-010.** It read *"a user who shares no
  channel with the subject MUST receive nothing"*, which is what FR-010's "only to users sharing"
  already forbids: the same constraint in the opposite polarity, mapped to the same task. What it
  contributed was a **verification method**, which now sits in FR-010. The id is retired rather than
  reused — constitution VI: identifiers are never reused.
  *Found by reading. A token-overlap comparison across all 41 requirements scored this pair at 0.08
  while surfacing two false positives at 0.45 and 0.32: the redundancy is logical entailment in
  opposite polarity, so the two sentences share almost no vocabulary.*
- **FR-014**: A non-member of a private channel MUST NOT observe presence of that channel's
  members through it (FR-CHN-05). A user of a different tenant MUST NOT receive presence events
  at all (principle I).
- **FR-015**: A client that utters `presence.changed` MUST be refused with `unknown_frame_type`
  and close code 4002. **Already true and already tested** —
  `services/gateway/src/isolation.itest.ts` classifies the frame outbound and drives the refusal
  against a running gateway. Stated as a requirement so the traceability map cites the test that
  exists rather than reporting the clause untested.
- **FR-027**: A presence frame MUST be delivered as soon as it arrives, whatever the receiving
  connection's resume phase. It MUST NOT enter the resume buffer and MUST NOT be filtered by the
  backfill marks. Presence carries no sequence, so it can neither duplicate a backfilled row nor
  leave a gap, and both mechanisms take a message. *Added by the reverse traceability map: the
  behaviour was decided in research R10 and no requirement carried it.*
- **FR-029**: A presence payload MUST NOT be delivered to a client as a message, and a message
  MUST NOT be delivered as a presence frame. *Added by the reverse traceability map: the rule was
  in the spec's edge cases and in the fabric contract, and in no requirement.*

### Open question 3, and the documents

- **FR-016**: This chapter MUST close open question 3 as **not opt-in per channel**, confirming
  ADR-10, and MUST leave that answer in one place. Presence publishes on every channel the subject
  is a member of; there is no per-channel presence flag and no opt-in.
  **Five positions in three documents today**, found by running the grep rather than by counting
  the documents already read:

      docs/04-srs.md:903            the row itself — open, owner Architecture
      docs/05-sad.md:899            ADR-10 — "resolves … (provisionally)"
      docs/05-sad.md:210            the not-a-service table — "see Open Q3, SRS"
      docs/06-adr-deep-dives.md:633 "SRS Open Question 3 … stays open"
      docs/06-adr-deep-dives.md:651 the revisit-when clause, which names the remedy

  An earlier draft of this requirement said three, in two documents. `docs/06-adr-deep-dives.md`
  had not been opened.
- **FR-016a**: The closure MUST state what it does not settle. ADR-10's revisit trigger is presence
  fan-out exceeding roughly 30% of gateway publish volume in load tests, and this chapter does not
  discharge it: the lane's largest membership set is five channels, so the measurement that would
  trip the trigger cannot be taken here. The SRS row moves to closed **citing ADR-10 and naming the
  undischarged trigger** — not on the strength of a number this feature produced. An easy instrument
  tells you what it measures, not what you wanted to know.
- **FR-016c**: The closure MUST name **NFR-SCL-01** as well as FR-RTM-07. Appendix C row 3 lists
  *both* as what open question 3 blocks, and NFR-SCL-01 is the harder one: *"The system shall sustain
  10,000 concurrent WebSocket connections per gateway instance"* (P1, verified by analysis). Closing
  the question as not-opt-in decides that presence fan-out rides the message fabric at that scale,
  and this chapter measures nothing at that scale. The row closes for FR-RTM-07 and records
  NFR-SCL-01 as resting on ADR-10's trigger rather than on evidence. *Found in analysis pass 4:
  NFR-SCL-01 appeared in none of this feature's artifacts while half of the row being closed was
  about it.*
- **FR-016b**: `docs/05-sad.md:210`'s *"see Open Q3, SRS"* MUST stop pointing at a row that no
  longer asks a question. The not-a-service table's revisit condition survives — presence fan-out
  dominating gateway CPU is still the trigger — and it cites ADR-10 instead.
- **FR-017**: `docs/05-sad.md` MUST record that the fabric it describes is not the fabric that
  ships. ADR-10 puts presence transitions on the channel subjects; `fanout.ts` accepts a `Message`
  and the delivery path emits `message.created`. One of the two moves, and the record says which.
- **FR-034**: That record MUST be a **new ADR — ADR-19 — superseding ADR-10's subject-grammar
  clause, not an edit to ADR-10.** Constitution VII and `docs/05-sad.md:49` both say *"ADRs are
  immutable once accepted; superseding requires a new ADR."* **ADR-10 is edited in exactly one
  place: its `**Status:**` line**, which already carries annotations, gains a supersession note.
  Its decision text, its Consequences and its deep-dive Decision section are not touched.

  ADR-19 carries what the house format requires — status, drivers, the decision, the rejected
  alternative and a revisit condition — and its substance is research R1: presence gets its own
  subject grammar because the fan-out is typed to messages at three points and the third sits
  inside a function ten chapters fence, so the rejected alternative (envelope both kinds on
  `chan:{id}`) means editing the hot path. It also records what ADR-10's own **Revisit when**
  clause makes unavoidable: *"presence subjects get their own fabric or channels opt in"* is the
  remedy ADR-10 reserved for ~30% of publish volume, and **this chapter takes half of it before the
  trigger fired**, for a different reason than the trigger names.

  *Found in analysis pass 14. Two tasks planned to rewrite ADR-10's decision text, including the
  deep dive's `Decision` section. No ADR in this project has ever been amended or superseded — one
  grep returns only the rule itself — and this spec already invoked that rule to reject the opt-in
  option while planning to walk through it here.*
- **FR-018**: `docs/07-tutorial-plan.md`'s 3.19 row MUST name FR-RTM-07 and FR-CHN-05, neither of
  which appears anywhere in that document today. Chapter 3.18's `gaps.md` item 8, owner this
  chapter.
- **FR-019**: Amendments to the **published** documents MUST be re-synced to
  `relay-tutorial/content/docs/` with `pnpm sync:docs` — here `docs/04-srs.md`, `docs/05-sad.md`
  and `docs/06-adr-deep-dives.md`. `check-docs-drift.sh` reads divergence, not correctness, and
  will not say which of the two copies is right.
- **FR-019a**: **`docs/07-tutorial-plan.md` MUST NOT be mirrored**, so the amendment FR-018 makes
  to it syncs nothing. `sync-docs.sh` holds the published set as an explicit list and gives the
  reason in its own comment: the file is *"the SERIES' OWN PLAN and is not a published reference"*,
  and a range of `0[1-8]` *"would have published it. Nobody would have noticed until a reader found
  the chapter list with its unpublished chapters in it."* *Found in analysis pass 8: FR-019 said
  "every `docs/` amendment", which is false, and an implementer satisfying it literally adds 07 to
  that list and ships the unreleased chapter plan to readers.*

### What this chapter does not close

- **FR-020**: FR-RTM-10 remains unmet and MUST be re-recorded rather than inherited silently.
  Chapter 3.18 measured it: a member removed over REST keeps receiving on an open socket
  indefinitely, because `connection.channelIds` is built once at connect and read unchanged on
  every frame. Chapter 3.18's `gaps.md` item 4 assigns it here on the premise that presence needs the same
  mechanism; presence needs the channel set at transition time, which already arrives on the
  session response, so the premise does not hold.
- **FR-020a**: **Whether this chapter also closes FR-RTM-10 is a decision `/speckit-plan` MUST
  make and record, with the measurement or argument it rests on.** The question research answers
  is narrow: does the mechanism presence needs — a per-user cross-instance connection count, and
  a producer that publishes on a channel set — put a membership push within reach cheaply, or is
  it a second feature with its own argument set? Two mechanisms in one chapter is what the word
  estimate tracks, since prose follows arguments and not files.
- **FR-020b**: **If research is inconclusive, the answer is no.** Named here so that an
  undecided question cannot be settled later by whichever scope the implementation found
  convenient — the failure mode chapter 3.18's `gaps.md` item 4 describes when it says **chapter 3.18's own
  FR-013** was not narrowed to make a test pass. A different feature's identifier, and since pass 11
  also this spec's retired one, so the chapter is named. A chapter that takes FR-RTM-10 on does so on a recorded reason; a chapter that
  leaves it open leaves the corrected premise behind, and the gateway test that asserts the
  violation keeps asserting it.
- **FR-021**: The presence path inherits FR-RTM-10's staleness and MUST say so. A user who joins
  a channel while connected does not appear online to that channel's members until they
  reconnect, because the channel set the transition publishes on is the one taken at connect.
- **FR-022**: FR-RTM-05's remaining kinds stay unbuilt and MUST be listed by name. All six frames
  exist in the union; `message.created` alone has a producer.

### Failure, and what it must not take down

- **FR-023**: A presence-path failure MUST NOT fail a connection, a disconnection, a send, or a
  message delivery. Presence is the only thing that degrades.
- **FR-024**: Every presence-path failure MUST emit one structured log event with a stable name.
  This is the assertion that carries FR-023: a path that silently does nothing satisfies "the
  socket still opened" exactly as well as a working one does.
- **FR-025**: Each published transition MUST be logged with a stable event name, the subject and
  the state. No message content, no token (constitution VI).
- **FR-030**: Beyond the events FR-024 and FR-025 already require, the presence path MUST emit and
  a test MUST reach `presence.suppressed` (a guard or an election lost, or a reconnection that
  cancelled a grace check) and `presence.invalid_payload`. Those four names are the whole
  vocabulary; nothing else is emitted from this path. *Added in analysis pass 1: two of the four were specified in
  `contracts/presence-lifecycle.md`, implemented by tasks, mandated by no requirement and asserted
  by no test.*
- **FR-031**: A `presence.changed` `online` event MAY be published for a user who is already online
  in two bounded cases, and in no others. **First**, the presence key is lost under a live
  connection — a Redis restart or an eviction. **Second**, a reconnection lands in the `marginMs`
  window between the grace ending and the check running: the key has expired, so the reconnection
  wins `SET … NX` and publishes `online`, while the check then finds the key present and suppresses
  the `offline` that would have preceded it. Observers see two `online` events with no `offline`
  between them, for at most `marginMs`. Both are cosmetic and self-heal, which is what ADR-10
  authorises. *Added in analysis pass 1: the behaviour was
  described in `research.md` R11 and in the data model's state machine, and no requirement
  allowed it. An unrequired behaviour is one a later reader deletes as a bug.*
- **FR-033**: Four published claims that this design contradicts MUST be corrected, in **both
  locales** — eight files in all. No checker reads prose, so each is named here rather than left to
  be found:

      part-2/chapter-06  a ForwardRef: presence and typing "will reuse this exact pub/sub
                         plumbing". R1 gives presence its own subject and its own module.
      part-3/chapter-18  ":651" and ":1596" — presence "needs the same missing mechanism",
                         a membership push. R7 established the premise does not hold.
      part-3/chapter-08  ":3415" — presence "needs the same" connection registry. R6
                         established it is not needed, and that the SAD's shape for it
                         cannot expire a dead instance's member.

  Chapter 2.6's is a **promise to the reader about this chapter**, so 3.19's own prose MUST answer
  it rather than quietly diverge. *Found in analysis pass 7, by reading the published chapters —
  the only pass that did. Chapter 3.18's `gaps.md` item 8 is the standing record that no instrument here reads
  prose, and a published Trap contradicting chapter 3.17 survived fifteen analysis passes.*
- **FR-033a**: The four claims MUST be verified gone by `check-prose.py`, which carries **one fragment per claim per locale**, taken from the files rather than translated by guess. Chapter 3.18's lesson holds here and was re-measured on this instrument: substituting the English fragment for the Vietnamese locale drops a claim's detections from two to one, so the Vietnamese sentence reads as already corrected. The checker proves a sentence is **absent**, never that what replaced it is right — so FR-033 keeps a reader as well.
- **FR-032**: `services/gateway/src/presence.ts` and `packages/protocol/src/presence.ts` MUST reach
  **100% branch, function, line and statement coverage**. They are tenant-isolation code under
  NFR-MNT-02, which the constitution makes a MUST rather than a target: the subscribe set decides
  which subjects an instance hears, and that is what keeps a statement about a person inside the
  tenant it belongs to. An unreachable branch is removed, not pinned around — the ratchet has taken
  that option three times. *Added in analysis pass 5: NFR-MNT-02 appeared in no artifact while a
  constitution MUST turned on it, and the coverage task wrote pins "from the measurement", which
  always supplies a reason.*
- **FR-026**: Presence MUST NOT acquire durability. No outbox row, no JetStream subject, no
  retry, no replay on resume. ADR-10: the correct amount of durability for a green circle is
  none.

### Key Entities

- **Presence state** — one of `online` or `offline`, per user per environment, derived and
  ephemeral. Not a source of truth (constitution IV); total loss is a cosmetic outage that
  self-heals on the next transition.
- **Connection count per user** — how many open sockets a user holds across all gateway
  instances. The thing the grace period asks about at the end of the window. `docs/05-sad.md:574`
  names `conn:{env}:{user}` → set of instance IDs for it, TTL 60 s heartbeat-refreshed, and it
  does not exist yet.
- **Presence key** — `docs/05-sad.md:575` names `presence:{env}:{user}`, TTL 30 s. Also does not
  exist.
- **The subject's channel set** — the channels a transition is published on, taken from
  `POST /internal/session`'s `channel_ids` at connect and fixed for the connection's life,
  alongside `sendLimit` and `openedAt` and for the same stated reason.

## Success Criteria *(mandatory)*

- **SC-001**: A connected member receives one `presence.changed` `online` frame when a co-member
  connects, with no client action in between.
- **SC-002**: The same holds when subject and watcher are on different gateway instances.
- **SC-003**: A watcher sharing three channels with the subject receives exactly one frame per
  transition, verified by count.
- **SC-004**: A subject's second connection produces no frame, and closing one of two produces
  none — verified by count, in a run where a transition that should fire does.
- **SC-005**: An `offline` frame arrives after the subject's last connection closes, no earlier
  than 30 seconds and within an upper bound this feature **measures and records** — the observed
  close-to-`offline` delay across the suite's runs, not an estimate.
- **SC-006**: A reconnection 10 seconds after the close produces no `offline` frame and no second
  `online` frame, including when the reconnection lands on a different instance.
- **SC-007**: A user sharing no channel with the subject receives nothing; a non-member of a
  private channel receives nothing; a user of another tenant receives nothing. All three asserted
  in runs where a co-member receives the frame.
- **SC-008**: A client uttering `presence.changed` is refused with `unknown_frame_type` and close
  4002, and the frame union's ten members are still each classified exactly once.
- **SC-009**: With Redis unavailable, a socket still opens and messages still deliver, and the
  presence failure is visible as a named log event rather than as silence.
- **SC-010**: Open question 3 reads *closed, not opt-in* in `docs/04-srs.md`, cites ADR-10, and
  names the undischarged revisit trigger. A grep for the question across `docs/` finds no
  surviving third position, `docs/05-sad.md:210` included.
- **SC-011**: `docs/07-tutorial-plan.md`'s 3.19 row names FR-RTM-05, FR-RTM-06, FR-RTM-07 and
  FR-CHN-05, and the traceability map cites all four in both directions — requirement to test and
  test to requirement — built during planning rather than at close-out.
- **SC-012**: FR-RTM-10's state is recorded with its premise corrected, the in-or-out decision is
  written down in `plan.md` with the reason it rests on, and the test that asserts the violation
  still asserts it or is inverted deliberately.
- **SC-013**: The chapter is inside the series' 2,000–4,000 prose-word bound, every fenced file
  replays onto `relay-platform` from predecessor `caeabc9`, and both locales route.
- **SC-014**: The full integration lane is green and inside its 240-second budget, from a count
  read after the ANSI colour codes rather than through them.

## Assumptions

- **The frame does not change.** `presenceChangedSchema` has been published since chapter 1.3 and
  carries `user` and `state`. Adding a `channel` field would make duplicates distinguishable and
  would edit a fence chapter 1.3 owns. Measured rather than estimated: `frames.ts` is fenced by **two** chapters, 1.3 and 3.8, so **one** lies downstream of 1.3 — a smaller cost than an earlier draft of this assumption claimed, and the argument should rest on the real number. FR-012 answers
  the duplicate question instead, and chapter 3.17's frame-shape assertion is what holds the
  union still.
- **The subject's channel set at transition time is enough.** It arrives on the session response
  and is already kept per connection. FR-021 states the staleness this accepts.
- **The gateway already reaches Redis three times over** — `fanout.ts` opens a publisher and a
  subscriber, and chapter 3.8 added a third client for the limiter with its own documented
  ownership. Presence is not a new dependency, and ADR-10 says Redis is where it lives.
- **ADR-10 stands, and this chapter confirms rather than reopens it.** Presence lives in Redis
  with a TTL, no dedicated service, and no per-channel opt-in (FR-016). ADRs are immutable once
  accepted; opting presence in per channel would need a superseding ADR, a channel-model column
  and an SRS clause, and nothing here argues for one. Its revisit trigger stays undischarged
  (FR-016a). What the lane can measure it should measure, and the number it cannot produce it
  should not imply.
- **Redis pub/sub at-most-once is the contract**, inherited from chapter 2.6 and not weakened
  here. For messages the resume path recovers a gap; for presence nothing does, and FR-026 keeps
  it that way.
- **The lane environment is the one `specs/036-chapter-3-18/baseline.txt` pins**: Postgres on
  15432 and *only* Postgres on a non-default port — Redis is on 6379 and NATS on 4222. Fourteen of
  chapter 3.18's analysis passes repeated "Redis on 16379" without asking docker, and nothing in
  the repository runs it there. The compose `services` profile must be stopped, for `pnpm
  coverage` as well as the lane, which cost chapter 3.18 half an hour proving itself innocent of
  a pin on a file it never touched.
- **The integration lane is not idempotent from cold volumes** (chapter 3.18's `gaps.md` item 3). After a
  `docker compose down -v`, run it twice and believe the second.

## Dependencies

- **Chapter 3.18 is closed**, tagged `part3-ch18`. The fence predecessor is commit `caeabc9` in
  `relay-platform` and `5558e2e` in `relay-tutorial` — a commit, not the tag, and chapter 3.18's
  `chapter-notes.md` T065 section states that nothing fenced was amended after it.
- **`packages/protocol/src/frames.ts`** already contains the frame. Chapters 1.3 and 3.8 both
  fence it, so if nothing in it changes, neither chapter's hunks move.
- **`services/gateway/src/session.ts` is fenced by ten chapters** — 2.5, 2.6, 2.7, 2.8, 3.2, 3.7,
  3.8, 3.11, 3.14 and 3.16 — and **`fanout.ts` by two**, 2.6 and 3.18. Whatever makes the fabric
  multi-kind lands in files with ten chapters' worth of hunks already replayed onto them. Counted
  from `title=` attributes, not from which chapters mention the filenames: the looser grep returns
  fourteen and includes chapters 3.12, 3.13, 3.17 and 3.18, which discuss these files without
  fencing them.
- **`services/gateway/src/isolation.itest.ts`** derives the frame list from `frameSchema.options`
  and fails on an unclassified member — the checker that fails on an unknown member rather than on
  the examples in front of it, and already green for `presence.changed`. Fenced by five chapters:
  3.12, which added the classification, then 3.15, 3.16, 3.17 and 3.18.
- **`relay-tutorial/lib/tutorial.ts`** holds exactly the shipped chapters. Without a 3.19 entry
  with both Vietnamese fields the chapter does not route and is not among the static pages.
- **`docs/05-sad.md`, `docs/04-srs.md` and `docs/07-tutorial-plan.md`**, each with a mirror under
  `relay-tutorial/content/docs/` that `pnpm sync:docs` writes and `check:docs` guards.
- **Chapter 3.18's reader protocol** (`specs/036-chapter-3-18/reader-protocol.md`), which needs a
  second person. Chapters 3.14 through 3.18 have each named this gap and none has closed it, and
  3.18 asked for it to be run before this chapter rather than named a sixth time. It is a
  dependency on a person, not on a command.

## In scope beyond the producer

- **A cross-instance connection count.** FR-005 cannot be answered from one instance's registry:
  CON-02 forbids sticky routing, so a reconnection lands wherever it lands. `docs/05-sad.md:574`
  already names the key.
- **Whatever makes the fan-out carry two frame kinds**, and the SAD amendment that records which
  way it went (FR-017). This is the largest unknown in the feature and it belongs to research.
- **A new ADR — ADR-19** (FR-034), because ADR-10 cannot be edited. ADR-01 through ADR-18 exist, so
  the number is free and the compliant path costs one document section.
- **Amendments to four governing documents, not two.** `docs/04-srs.md`'s Appendix C row — an
  appendix row, not a clause (FR-002a, FR-016); `docs/05-sad.md`'s ADR-10, its `:210` pointer
  (FR-016b) and its Redis table; **`docs/06-adr-deep-dives.md`**, which holds two of open question
  3's five positions and whose ADR-10 deep dive has the same subject-grammar sentence to correct
  (FR-016, FR-017); and `docs/07-tutorial-plan.md`'s 3.19 row (FR-018). Each has a mirror under
  `relay-tutorial/content/docs/` that `pnpm sync:docs` writes (FR-019).
- **A `relay-tutorial/lib/tutorial.ts` entry** with both Vietnamese fields.
- **Corrections to four published prose claims, in both locales** (FR-033). Chapter 3.18 carried
  the same kind of scope item and named it; this feature had none until analysis pass 7 read the
  chapters.
- **A correction carried forward from chapter 3.18's spec.** Its out-of-scope list says *"Typing
  indicators (FR-RTM-08) — no frame exists in the union"*. `typingSchema` is in `frameSchema` and
  `isolation.itest.ts` classifies `typing` as outbound, so the claim is false. It sits in a closed
  feature's record; FR-022 is what stops this chapter repeating it, and whether 3.18's record gets
  an annotation or is left as written is a small call for the plan.

## Out of scope

- **A presence snapshot on connect.** No clause requires one and `connection.ack` has no field
  for it. Recorded as a gap, because without it a client's roster starts empty.
- **Typing indicators** (FR-RTM-08). The frame exists; the producer does not. P2.
- **Membership-change events** (FR-RTM-05's fourth kind). The frame exists and the writer exists;
  nothing connects them.
- **Message edit and deletion events** (FR-RTM-05's second and third kinds). Nothing writes an
  edit or a tombstone.
- **FR-RTM-09's five-connection cap.** This chapter counts connections per user and does not
  limit them. The cap is enforced nowhere today and this chapter does not change that.
- **`user.connected` / `user.disconnected` webhooks** (FR-WHK-02). A different fabric, a
  different phase.
- **The `connection_events` table's presence analytics** (`docs/04-srs.md:814`). Chapter 3.11
  meters connection-minutes; nothing here reads or writes that table.
