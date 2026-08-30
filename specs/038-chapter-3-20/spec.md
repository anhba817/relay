# Feature Specification: chapter 3.20 — the membership that changed under a live socket

**Feature Branch**: `038-chapter-3-20`

**Created**: 2026-08-29

**Status**: Draft

**Input**: User description: "start chapter 3.20"

## Summary

Two clauses in `docs/04-srs.md` are P1 and unmet, and they are one mechanism.

**FR-RTM-10** says events *"shall not be delivered to a client whose membership no longer grants
access, effective within 5 seconds of the membership change."* It is not met, and the repository
says so out loud: `services/gateway/src/session.itest.ts:677` is titled *"keeps delivering to a
member who was REMOVED while connected (FR-RTM-10)"*, waits out the clause's own five-second
budget, and asserts that the frame the clause forbids **does** arrive. It closes with *"change
this to `.rejects` on the day a re-read exists."*

**FR-RTM-05** says the system *"shall emit real-time events for message creation, edit, deletion,
membership change, presence change, and typing."* Six kinds. All six have frames in
`frameSchema`. After chapter 3.19, two have producers. `membership.changed` is the third, and
producing it is the same act as satisfying FR-RTM-10 — because the thing a gateway needs in order
to stop delivering is the news that a membership changed.

**The gateway cannot find this out by itself.** It has no database (ADR-05) and learns memberships
exactly once, from `POST /internal/session`, at connect. `connection.channelIds` is a `Set` built
there; `fanout.subscribe` and `presence.subscribe` run once over it; `registry.subscribersOf`
reads that same set on every delivery; the unsubscribes run when the socket closes. Nothing
between connect and close re-reads anything, and there is no path that could.

**And this event is addressed to a user, not to a channel — which neither existing fabric is.**
`chan:{channel_id}` carries messages to a channel's subscribers. `presence:{channel_id}`, added
last chapter, carries transitions to the same audience by a second grammar. Both assume the
receiving instance is already subscribed to the channel. For a **removal** that happens to be
true; for an **addition** it is false by definition — the gateway holding that user's socket is
not subscribed to the channel they are about to join, so nothing addressed to that channel can
reach them. This is the first event in the system whose recipient is a principal.

**One more thing separates it from chapter 3.19: presence was allowed to fail.** FR-023 there let
a presence-path failure degrade without failing a connection, and ADR-10 authorises the loss
because a green circle self-heals. A dropped membership revocation does not self-heal. It leaves a
removed user receiving messages until they reconnect, which is the exact defect FR-RTM-10 exists
to forbid. ADR-07 makes the fan-out fabric explicitly lossy. **What carries a revocation, and what
happens when it is dropped, is the first thing this chapter has to decide** — and this spec
requires the decision to be made and written rather than arrived at.

### Three things read from the repository, not assumed

**A dead contract is still exported.** `packages/protocol/src/internal.ts:121` exports
`internalMembershipsResponseSchema` — *"api → gateway: the channels this user may hear
(FR-RTM-01)"* — and the comment eleven lines below says chapter 3.2 *"replaces the memberships
response above rather than joining it."* One grep: nothing serves `GET /internal/memberships`,
nothing parses the schema, and `services/api/src/tenancy/signup.itest.ts:280` POSTs the path with
no credential and asserts the answer is not a 200 — a **negative** fixture whose subject is the
router, not this schema. It ships in `dist` and has for eighteen chapters. That is `presence.changed`'s shape one contract down, and this chapter is the one that
meets it.

**Four routes and one flag can change what a user may hear.**

    POST   /v1/channels/:id/members          addMembers      bulk
    POST   /v1/channels/:id/members/remove   removeMembers   bulk
    POST   /v1/channels/:id/join             join            a user token, acting for itself
    PATCH  /v1/channels/:id/members/:user    setMemberRole   NOT in the frame's vocabulary
    PUT    /v1/users/:id  (banned: true)     setBanned       revokes everything at once

`membership.changed`'s payload is `{ channel, user, change }` with `change` an enum of `added` and
`removed`. **A role change has no spelling in it**, which is a fact about the frame chapter 1.3
published rather than an omission of this one.

**The frame is shaped for a reader who is not its subject.** The payload names a `user`, which is
only useful to somebody else, and chapter 3.12's isolation gauntlet already classifies it
outbound — *"membership is written through the api, never the socket"*. That settles who it is
for and leaves the harder half: the removed user is also owed the news, and telling them is the
last thing that may reach them on that channel.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A removed member stops receiving, and is told why (Priority: P1)

Tuan is connected and reading `#ops`. An administrator removes him from the channel. Within five
seconds Tuan receives one `membership.changed` frame naming the channel, himself and `removed` —
and after that, nothing from `#ops` ever again on that socket. His connection stays open and every
other channel he belongs to keeps working.

**Why this priority**: this is FR-RTM-10, P1, and the only clause in the set that is about access
rather than about liveness. It is also the half that a test in the tree currently asserts is
broken.

**Independent Test**: connect a member, remove them over the public route, wait out the clause's
five-second budget, post to the channel, and assert the frame does not arrive — against the same
fixture that today asserts it does.

**Acceptance Scenarios**:

1. **Given** a user connected and subscribed to a channel, **When** they are removed from it,
   **Then** they receive exactly one `membership.changed` frame for that channel with `removed`,
   and it arrives before any cut-off takes effect.
2. **Given** the removal has taken effect, **When** a message is posted to that channel more than
   five seconds later, **Then** no frame for it reaches that socket.
3. **Given** the removed user is also a member of a second channel, **When** a message is posted
   to the second channel, **Then** it is delivered normally.
4. **Given** the removed user's socket, **When** the removal takes effect, **Then** the socket is
   not closed and no error frame is sent.
5. **Given** a user connected on two gateway instances, **When** they are removed, **Then** both
   sockets stop receiving that channel within the same budget.
6. **Given** the fabric is unreachable, **When** a removal is requested, **Then** the route still
   answers success, the membership is still written, and one structured failure event is logged
   (FR-015, FR-016).
7. **Given** a user whose connection is mid-resume, with messages for a channel already sitting in
   its buffer, **When** they are removed from that channel and the resume then completes, **Then**
   the `membership.changed` notice reaches them **during** the resume and **none** of the buffered
   messages for that channel is flushed (FR-029, FR-030). *Added in analysis pass 11: the scenario
   list had been twenty since the spec was written, and this is the journey behind pass 3's
   CRITICAL — a removal that every other test in the feature passes against.*

---

### User Story 2 — The channel's other members see who left (Priority: P1)

Mai is connected and reading `#ops`. Tuan is removed. Mai receives one `membership.changed` frame
naming Tuan and `removed`, so her member list can be right without refetching.

**Why this priority**: FR-RTM-05 names membership change as an event kind at P1, and the frame's
payload is shaped for exactly this reader. Without it the frame's `user` field means nothing.

**Independent Test**: connect a second member, remove a first, assert the second receives one
frame naming the first — in the same run in which the removed user's own delivery stops.

**Acceptance Scenarios**:

1. **Given** two members connected to one channel, **When** one is removed, **Then** the other
   receives exactly one `membership.changed` frame naming the removed user.
2. **Given** a remaining member connected to a **different gateway instance from the one hosting
   the removed user**, **When** a removal happens, **Then** that member still receives the frame.
   *(The removal originates at the api, which is neither gateway, so "the removal's origin" —
   what this scenario said until analysis pass 3 — names nothing that distinguishes the two.)*
3. **Given** a user who is a member of no channel the change touches, **When** a removal happens,
   **Then** they receive nothing.
4. **Given** a user in a different environment, **When** a removal happens, **Then** they receive
   nothing.
5. **Given** a bulk removal of several users in one call, **When** it succeeds, **Then** a
   remaining member receives one frame per removed user and no frame is coalesced away.
6. **Given** two members connected to one channel, **When** one's role is changed, **Then**
   neither receives a `membership.changed` frame — the enum has no spelling for it (FR-006).

---

### User Story 3 — A member added mid-connection starts receiving (Priority: P1)

Tuan is connected. An administrator adds him to `#night-shift`, a channel he was not in when his
socket opened. Within five seconds he begins receiving that channel's messages, and its members
see him as online, without reconnecting.

**Why this priority**: it is the other half of the same mechanism, it is the half no existing test
covers, and it closes chapter 3.19's `gaps.md` item 2 — *"a user who joins a channel while
connected does not appear online to that channel's members until they reconnect"*.

**Independent Test**: connect a user, add them to a channel they did not hold at connect, post to
that channel, and assert delivery — plus a presence transition observed by that channel's members.

**Acceptance Scenarios**:

1. **Given** a connected user not in a channel, **When** they are added, **Then** they receive
   one `membership.changed` frame with `added` for it.
2. **Given** the addition has taken effect, **When** a message is posted to that channel, **Then**
   it reaches that socket.
3. **Given** the addition has taken effect, **When** the user's presence next changes, **Then**
   that channel's other members observe it.
4. **Given** a user who joins a channel using their own token, **When** the join succeeds, **Then**
   the same delivery follows as for an administrative add.
5. **Given** a user added to a channel they are already in, **When** the call succeeds
   idempotently, **Then** no `membership.changed` frame is published.

---

### User Story 4 — A ban revokes everything at once (Priority: P2)

A user is banned in an environment. Every channel they were receiving stops, on every instance,
within the same five-second budget.

**Why this priority**: a ban is the strongest revocation the platform has and it currently reaches
no open socket. It is P2 rather than P1 because FR-RTM-10 speaks of membership and a ban is a user
flag — but leaving a banned user receiving is the same defect wearing a different name.

**Independent Test**: connect a user in two channels, ban them, and assert both channels stop
inside the budget while another user's delivery is unaffected.

**Acceptance Scenarios**:

1. **Given** a connected user in two channels, **When** they are banned, **Then** neither channel
   delivers to them after the budget.
2. **Given** a banned user, **When** they are unbanned, **Then** delivery resumes without a
   reconnect, or the spec's stated alternative holds and is tested.
3. **Given** a banned user's socket, **When** the ban takes effect, **Then** other users'
   deliveries are unaffected.

---

### Edge Cases

- A removal and an addition for the same user and channel arriving out of order. The later write
  is the truth; the fabric does not guarantee order between two publishes.
- A membership change published while the affected user has no connection anywhere. Nothing
  receives it and nothing should be retained.
- A membership change published while the gateway's fabric is unreachable. **This is the case that
  separates this chapter from 3.19** — see FR-014 and FR-014a.
- A user removed from a channel during their own resume backfill. **The buffer is a second delivery path and FR-029 is the answer** — the flush filters by sequence, not by membership.
- A bulk removal in which some ids do not exist or are already absent. Only real changes publish.
- A role change, which the frame cannot express.
- A user removed from a channel and re-added inside the five-second budget.
- The last member of a channel being removed.
- A membership change for a channel the receiving instance holds no connection for.
- An archived channel. Archiving is not a membership change and no membership event is published
  for it; sends are already refused at the api (chapter 3.15).

## Requirements *(mandatory)*

### The clauses this chapter answers

- **FR-001**: The chapter and its traceability MUST cite **FR-RTM-05** (membership change, of six
  named kinds), **FR-RTM-10** (five-second revocation), **FR-RTM-01** (a connected client receives
  messages for every channel of which it is a member — the clause an addition makes true for a
  channel joined mid-connection), **FR-WHK-02** (the two event types the outbox rows carry),
  **NFR-OBS-01** (the log vocabulary FR-031 and FR-032 rest on) and **NFR-MNT-02** (the coverage
  class FR-027 rests on). Constitution principle VI is satisfied by citation, not by new clauses.
  *This named three until analysis pass 12 — and a requirement about citation is the one place an
  undercount matters. The last two arrived with FR-031, FR-032 and FR-027 at pass 8.*
- **FR-002**: No SRS **clause** MUST change. FR-RTM-05 and FR-RTM-10 already require everything
  built here. Verified by a diff over `docs/04-srs.md`'s clause tables showing no row changed.
- **FR-002a**: **Whether any SRS appendix row changes is a decision, not a default.** Chapter 3.19
  closed Appendix C row 3 and recorded the diff. This chapter must state, before implementing,
  whether it touches Appendix C at all — and if it does not, say so where a reader can check it.

### The producer

- **FR-003**: `membership.changed` MUST have a producer. After this chapter three of FR-RTM-05's
  six kinds have one, and the chapter MUST name the remaining three by name — `message.updated`,
  `message.deleted` and `typing` — with the reason each is still absent.
- **FR-004**: **Every path that changes what a user may hear MUST publish**, and the chapter MUST
  enumerate them rather than gesture at them: `addMembers`, `removeMembers`, `join`, and the ban
  flag. A path that writes a membership and publishes nothing is the defect this chapter exists to
  remove, one layer down.
- **FR-005**: A publish MUST happen only for a real change. An idempotent add of an existing
  member, a removal of an absent one, and a bulk call whose outcomes are all no-ops MUST publish
  nothing.
- **FR-006**: A **role change MUST NOT publish** `membership.changed`. The frame's `change` enum
  has two members and neither means "role". The chapter MUST say so rather than leave a reader to
  discover that a `PATCH` is silent.
- **FR-007**: A publish MUST carry the environment, so that a gateway can refuse a change that
  does not belong to the connection it would act on. Principle I is structural here, not
  procedural.

### The delivery

- **FR-008**: A removed user MUST receive exactly one `membership.changed` frame for the channel,
  with `change: "removed"`, **before** delivery for that channel stops. The ordering is a
  requirement and not an implementation detail: cut-then-send makes the notice itself a violation
  of FR-RTM-10.
- **FR-009**: The channel's remaining members MUST each receive exactly one `membership.changed`
  frame naming the removed user, once per connection however many channels they share with them.
- **FR-010**: An added user MUST receive exactly one `membership.changed` frame with
  `change: "added"`, and MUST begin receiving that channel's messages within the **addition
  budget** — five seconds, chosen here, because no clause bounds it.
- **FR-011**: A user who shares no channel with the change MUST receive nothing, and a user in
  another environment MUST receive nothing, **asserted in a run where a member does receive**. A
  must-not-receive test that passes because the producer is dead proves nothing.
- **FR-012**: Delivery MUST work when the change originates on a different gateway instance from
  the one holding the affected socket, and when the user holds connections on several instances at
  once.
- **FR-029**: **A removal MUST also filter what the resume buffer will flush.** A connection in
  its `buffering` phase holds messages the fabric delivered during a backfill, and the flush sends
  every one whose sequence is past the resume mark — `flushable(buffer, marks)` filters on
  `frame.seq` and on nothing else. A removal that lands mid-resume deletes the channel from the
  connection's set and unsubscribes, and the frames already buffered for that channel flush
  afterwards **to a client whose membership no longer grants access**. Dropping them is the
  requirement. *Added in analysis pass 3: the edge-case list named this case and no requirement,
  plan element, contract or task followed it — "resume", "buffer" and "phase" appeared once in
  five documents. Chapter 3.19 asked the mirror question for presence and answered it as FR-027;
  this spec did not ask it.*
- **FR-030**: **The `membership.changed` frame itself MUST bypass the resume buffer**, consulting
  neither the connection's `phase` nor its backfill marks. FR-029 stops the buffered *messages*
  from flushing; this stops the *notice* from joining them. Buffered, it arrives after the cut-off
  and FR-008's ordering is violated in the mid-resume case — or FR-029's own filter drops it and it
  never arrives at all. A membership change carries no sequence, so it can neither duplicate a
  backfilled row nor leave a gap, which is the same argument chapter 3.19 made for presence in its
  FR-027: *"A presence frame MUST be delivered as soon as it arrives, whatever the receiving
  connection's phase."* *Added in analysis pass 7: chapter 3.19 needed both halves and wrote both;
  this spec had the message half from pass 3 and no equivalent for the frame.*
- **FR-013**: The affected user's socket MUST stay open. A revocation is not a disconnection, no
  close code is emitted, and no error frame is sent. Close code 4009 exists and this is not it —
  the same refusal chapter 3.8 made by name.

### What happens when the fabric drops one

- **FR-014**: **The chapter MUST decide and record what carries a revocation, and what a dropped
  one costs.** ADR-07 makes the fan-out fabric explicitly lossy and chapter 3.19's presence path
  was authorised to degrade (its FR-023) because a green circle self-heals. A dropped revocation
  does not: it leaves a removed user receiving until they reconnect, which is FR-RTM-10's exact
  prohibition. The decision belongs in a record a later reader can find, and the options MUST be
  stated with their costs rather than the chosen one asserted alone.
- **FR-014a**: **If the answer is a lossy fabric, the design MUST carry a backstop and the
  backstop MUST be tested.** A periodic re-read, a bounded connection lifetime, or a re-read on any
  signal — whichever is chosen, the requirement is that a revocation lost in transit is corrected
  by something other than the user's decision to reconnect. *If research shows no backstop is
  affordable, the honest outcome is that FR-RTM-10 is met on the happy path and unmet under fabric
  loss, recorded as such — not a clause narrowed until it passes.*
- **FR-015**: A membership-path failure MUST NOT fail a connection, **a disconnection**, a send, or a message delivery.
  The failure MUST emit one structured log event with a stable name and enough context to act on,
  and the **log line is the requirement's evidence** — a path that silently does nothing satisfies
  "the socket still opened" exactly as well as a working one does.
- **FR-031**: **Each published change MUST be logged with a stable event name**, the channel and
  the user's external id, and **no message content and no token** (constitution VI). Every log
  requirement this chapter had until analysis pass 8 was about failure, because every argument it
  inherited was about failure — chapter 3.18's trap, chapter 3.19's `presence.failed`. The working
  path said nothing out loud, so an operator could see the mechanism breaking and never see it
  working. Chapter 3.19 required this as its FR-025 and this spec had no counterpart.
- **FR-032**: **The membership path's log vocabulary is exactly four names and a test MUST reach
  each**: `membership.published` (FR-031), `membership.applied`, `membership.failed` (FR-015) and
  `membership.invalid_payload` — a body that is not JSON, or JSON the fabric schema rejects.
  Nothing else is emitted from this path. *`membership.invalid_payload` appeared once in the whole
  feature directory, in a task, mandated by no requirement and asserted by no test — which is the
  sentence chapter 3.19's FR-030 was written to stop being true a second time.*

  **AMENDED FROM THREE TO FOUR IN PHASE 8, AND THE AMENDMENT IS THE KIND THIS PROJECT ALLOWS.**
  Written at analysis pass 8, this clause named the vocabulary of the api's *publisher*. The
  gateway's delivery half did not exist in code yet, and when it did it emitted six names —
  `revoked`, `granted`, `revoked_all` and `rejected` beside the two it shared. Four of those are
  gone: `rejected` is a failure and became `membership.failed` with an `op`, `revoked_all` said
  nothing its per-channel lines did not, and `revoked`/`granted` collapsed into one
  `membership.applied` carrying its direction — the fabric's own payload spells direction in a
  field, and two names would be two entries for one event.

  What is left is the name FR-031's own argument demands and this clause had no slot for.
  `membership.published` means *it went onto the fabric*; `membership.applied` means *it took
  effect on a connection*, which is the event an operator wants when a customer says access did
  not change. A publish with no application is exactly the failure the backstop exists for, and
  with three names it was invisible.

  **This is not the amendment chapter 3.18 refused.** That would have been narrowing FR-RTM-10
  until the code passed — destroying the clause's purpose. This keeps the purpose intact: the
  vocabulary is still closed, still exhaustive, still tested name by name. It grew by one because
  it was counted before half the path was built.
- **FR-033**: **No frame may arrive as the wrong kind.** After this chapter the fabric carries four
  subject shapes — `chan:{channel_id}`, `presence:{channel_id}`, `member:{channel_id}` and
  `member:{env}:{user}` — and a message MUST NOT reach a client as a membership frame, a membership
  change MUST NOT reach one as a message or a presence transition, and the reverse of each. The
  topology makes this true rather than a filter enforcing it, **and that is exactly why it is
  asserted end to end**: "no special case was needed" and "the case was never considered" look
  identical from outside. A unit test that the four subject builders return distinct strings tests
  a naming function, not a delivery.
- **FR-016**: Publishing MUST NOT be able to fail the write it follows. A membership change that
  committed and did not publish is a bug this chapter must be able to see; a membership change
  that failed to commit because a publish threw is a worse one.

### The dead contract

- **FR-017**: `internalMembershipsResponseSchema` MUST stop being a schema nothing parses. The
  chapter MUST either delete it or give it a caller, and MUST state which and why. Deleting an
  exported symbol from the protocol package is a decision with a blast radius; leaving a contract
  that eighteen chapters have shipped and none has used is the habit chapter 3.8 named.
- **FR-017a**: Either way, `services/api/src/tenancy/signup.itest.ts`'s use of
  `/internal/memberships` MUST be read before the change lands, not after — and read as an
  **assertion**, not as a path. It POSTs with no credential and requires the answer not be a 200,
  so a GET-only revival leaves it standing while an `ALL` handler or an unauthenticated 200 does
  not. A test that mentions a path is not automatically a test about that path.

### What this chapter does not close

- **FR-018**: **FR-RTM-08 (typing) stays unbuilt and MUST be said so by name.** Chapter 2.6
  promised that *"presence (FR-RTM-06) and typing (FR-RTM-08) will reuse this exact pub/sub
  plumbing"*; chapter 3.19 corrected the presence half and left typing's open in print. Typing can
  genuinely reuse the fan-out, which is what makes it the contrast case and a chapter of its own.
- **FR-019**: **FR-RTM-09's five-connection cap stays unbuilt and MUST be said so by name**, with
  the reason: it needs the `conn:{env}:{user}` registry, and chapter 3.19's `gaps.md` item 6
  records that the SAD specifies it as a Redis set with one TTL — a shape in which one live
  instance keeps a dead instance's entry alive for ever. Building the cap means fixing the
  specification first.
- **FR-020**: `message.updated` and `message.deleted` stay unbuilt. Nothing writes
  `messages.edited_at` and nothing writes a tombstone; both belong with the moderation work in
  Part 4. Chapter 3.17's `gaps.md` item 5 is the standing record.

### The records

- **FR-021**: The test at `services/gateway/src/session.itest.ts:677` MUST be inverted rather than
  deleted, and its comment — *"change this to `.rejects` on the day a re-read exists"* — is the
  instruction. The inverted test MUST wait out the same five-second budget, so that a pass means
  the clause is met rather than that the assertion moved.
- **FR-022**: Chapter 3.19's `gaps.md` item 2 MUST be closed by name, and its correction carried:
  the item records that chapter 3.18 assigned FR-RTM-10 to 3.19 for a reason that did not hold.
- **FR-023**: `docs/07-tutorial-plan.md` MUST gain a 3.20 row **and** its Part 3 header MUST stop
  saying *"16 published, 3 planned"*. Measured at `docs/07-tutorial-plan.md:137` against the table
  below it: **19 rows, zero `(planned)` markers** — the header is stale by three, not by one, and
  has been since chapter 3.17 shipped. A count in a header that nobody re-derives is the class of
  defect chapter 3.19 found twice.
- **FR-024**: Amendments to the **published** documents MUST be re-synced with `pnpm sync:docs`
  and checked with `pnpm check:docs`. `docs/07-tutorial-plan.md` MUST NOT be mirrored — it is the
  series' own plan and `sync-docs.sh` holds the published set as an explicit list.
- **FR-025**: Whether the architecture record changes MUST be decided rather than defaulted. A
  third addressing scheme, or a revocation carried on a fabric ADR-07 calls lossy, is the kind of
  claim the SAD makes; ADRs are immutable once accepted, so any change is a new record.
- **FR-026**: Published prose that this design contradicts MUST be corrected in **both locales**,
  and each claim MUST be named in this spec rather than left to be found. Chapter 3.19's
  `check-prose.py` is the precedent: a per-claim, per-locale fragment that fails while any survives.
  **No checker reads prose**, and a published Trap contradicting chapter 3.17's own chapter
  survived fifteen analysis passes.
- **FR-027**: Both new or substantially changed production files MUST reach **100% on statements,
  branches, functions and lines**. Membership revocation is tenant-isolation code — it decides who
  may hear what — and NFR-MNT-02 requires 100% branch coverage of that class. **The pin MUST NOT
  be lowered with a reason**; a measurement always supplies one.
- **FR-028**: `gaps.md` MUST carry chapter 3.19's still-open items forward with their status
  re-checked, each reference naming its chapter. Item numbers collide across ledgers, and chapter
  3.19's item 17 — six of the gateway's eight integration files each spawning their own api — is
  the one this chapter is most likely to make worse.

## Success Criteria *(mandatory)*

- **SC-001**: A removed member stops receiving that channel's messages within five seconds,
  measured against the clause's own budget rather than a shorter one.
- **SC-002**: The same removed member keeps receiving every other channel they belong to, in the
  same run.
- **SC-003**: Within five seconds, a member added while connected receives that channel's next message without
  reconnecting.
- **SC-004**: A member added while connected is observed by that channel's other members the next
  time their presence changes — chapter 3.19's staleness, closed.
- **SC-005**: A removed user receives exactly one `membership.changed` frame for the channel, and
  no further frame for that channel arrives within the revocation budget. *"The last frame" is
  what this means and not what it can measure — nothing observes "last", only "none within a
  window", and the window has to be named or the criterion cannot fail.*
- **SC-006**: A remaining member receives exactly one `membership.changed` frame per removed user,
  however many channels they share with them.
- **SC-007**: A non-sharer and a user of another tenant each receive nothing, in a run where a
  member receives.
- **SC-008**: A banned user's delivery stops on every channel and every instance within the revocation budget, which a ban borrows rather than being covered by.
- **SC-009**: With the fabric unreachable, sockets still open and messages still deliver, one
  structured failure event is logged, and the chapter's stated backstop is exercised by a test.
- **SC-010**: `services/gateway/src/session.itest.ts`'s FR-RTM-10 test asserts the clause is met,
  after waiting the same five seconds it waits today.
- **SC-011**: Three of FR-RTM-05's six kinds have producers, and the other three are named in the
  chapter with the reason each is absent.
- **SC-012**: Every requirement here has a verification, mapped in both directions and re-derived
  from the shipped tree at close-out.
- **SC-013**: The chapter routes in both locales, the fence chain replays from this chapter's
  named predecessor commit, and the prose falls inside the series' 2,000–4,000 word bound.
- **SC-014**: The full integration lane is green inside its 240-second budget, counted with the
  colour codes stripped, and the gateway package's own wall clock is recorded separately.
- **SC-015**: A member removed **during their own resume** receives the notice before the resume
  completes and none of the messages the buffer was holding for that channel. *Neither half of this
  is observable from SC-001: the messages arrive through the message path after the membership path
  has already done its job correctly, and the notice's absence looks like a producer that did not
  fire.*
- **SC-016**: All three of the membership path's log names appear in a run — a working change, a
  swallowed failure, and a payload the fabric schema rejects — and nothing else is emitted from
  that path. A working change is visible in the log, not only a broken one.
- **SC-017**: With four subject shapes on one Redis, a message, a presence transition and a
  membership change published over the same channels each reach their subscribers exactly once and
  never under another kind's `type`.

*SC-015 through SC-017 were added in analysis pass 9. The list had been fourteen since the spec was
written and never moved while the requirements grew from 31 to 36 — so four requirements added for
a CRITICAL and two HIGHs produced no outcome the chapter is judged on.*

## Key Entities

- **A membership change**: an environment, a channel, a user and a direction (`added` or
  `removed`). It is not a row anywhere; it is the news that a row was written.
- **`membership.changed`**: the wire frame, in `frameSchema` since chapter 1.3 —
  `{ channel, user, change }`, `change` an enum of two. Outbound only, per chapter 3.12's gauntlet.
- **The connection's channel set**: `connection.channelIds`, built once at connect and read on
  every delivery. This chapter is the first thing that changes it while a socket is open.
- **The connection's resume buffer**: `connection.buffer`, filled by the message path while a
  connection is `buffering` and flushed by `flushable(buffer, marks)`, which filters on sequence
  and not on membership. **A second delivery path the membership design cannot see** — FR-029 and
  FR-030 exist because of it. *Added in analysis pass 10: two requirements governed it before this
  list named it.*
- **The revocation budget**: five seconds, from FR-RTM-10, measured from the membership write.
  It covers **removals and bans only** — FR-RTM-10 speaks of access no longer granted and says
  nothing about an addition.
- **The addition budget**: **five seconds, and it is this chapter's number rather than a clause's.**
  No SRS clause bounds how long an added member may wait, so one is chosen here and matched to the
  revocation budget for symmetry. Without it FR-010 and SC-003 are unfalsifiable in both
  directions: a test author picks a window, and too generous never fails while too tight flakes.

## Assumptions

- **A ban is a revocation for this chapter's purposes.** FR-RTM-10 speaks of membership and a ban
  is a user flag, but a banned user still receiving is the same defect. `POST /internal/session`
  already carries `banned`, so the connect path treats it as access-affecting; the live path should
  agree with the connect path.
- **Archiving is not a membership change.** An archived channel keeps its members and refuses
  sends at the api (chapter 3.15). No membership event is published for it.
- **Channel deletion is out of scope** because nothing deletes a channel. If that changes, a
  deletion is a removal for every member.
- **Both budgets are measured from the membership write**, not from the publish — the revocation
  budget and the addition budget alike. A design that publishes late and delivers promptly has
  still missed the clause. *This said "the five-second budget", singular, until analysis pass 7;
  pass 3 had split it in two and left this line behind.*
- **A user removed from their last channel keeps an open socket** and simply receives nothing.
  A connection is not a membership.
- **Ordering between two publishes is not guaranteed** by the fabric, and the design does not
  assume it. Where order matters — the notice before the cut-off — it must be a property of one
  instance's own sequence rather than of the fabric.
