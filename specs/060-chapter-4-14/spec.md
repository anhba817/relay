# Feature Specification: Chapter 4.14 — "Pending, ready, rejected"

**Feature Branch**: `060-chapter-4-14`

**Created**: 2026-09-28

**Status**: Draft

**Input**: User description: "chapter 4.14"

Movement VI, second chapter. `docs/12` §3 row 15: *the state machine and `media.updated`
(FR-MED-07). A placeholder becomes real without polling.* Open question §7.4 belongs to this
chapter.

## What the premise check found

Run before this specification was written, because four tasks in this project have had a false
premise and one of them would have caused a defect.

| Claim | Measured | Consequence for scope |
|---|---|---|
| The three states exist | `0018_media_states.sql` widens the CHECK to `pending, ready, rejected`; the worker produces the last two | The state machine is **built**. This chapter does not build it. |
| FR-MED-07 is one obligation | It is **two sentences**: state on every door, and a `media.updated` event | Two independent deliverables, not one |
| An attachment carries a state | `attachmentSchema`'s media arm is `{ type, media_id }` — **no state field** | Sentence 1 is unmet, and nothing had recorded that |
| A `media.updated` producer exists | Zero occurrences. The worker posts a verdict to the api and publishes nothing | Sentence 2 needs a producer, which is the §7.4 question |
| §7.4 is undecided | **ADR-25 already set the threshold**: consolidate when per-channel SUBSCRIBEs *exceed* six, or projected subjects exceed 250,000 | The question is not "what is the rule" but "run the rule". A sixth grammar sits **at** the bound, not past it |
| One verdict means one channel | FR-MSG-11 has allowed the same media id twice since 3.24; 4.12 built `channelsReferencingMedia` returning a list | One verdict fans out to N channels |

**THE TWO SENTENCES ARE NOT REDUNDANT, AND THAT IS THE CHAPTER'S ARGUMENT.** FR-MED-06 permits
attaching an object in `pending` **or** `ready`. A client that attaches an object already
`ready` will never see a `media.updated` for it, because the transition happened before the
reference existed. The event cannot be the only way a client learns the state; the state on the
attachment is the floor and the event is what removes the polling. Either half alone leaves a
reader with a placeholder that never resolves.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The state is on the attachment, at every door (Priority: P1)

A client reads history, or receives a live message, and the attachment it gets says which state
the media object is in. Today it gets an id and nothing else, so a UI cannot tell a photo that
is still being scanned from one that was rejected from one that is ready to display.

**Why this priority**: It is FR-MED-07's first sentence, it is the floor the event sits on, and
it is the only half that works for an object attached after its verdict. Shipping it alone
gives a client a correct — if polled — picture.

**Independent Test**: Attach a `pending` object and read the message back through history and
through a live delivery; both carry `state: "pending"`. Record a verdict, read again; both
carry the new state. No event is involved.

**Acceptance Scenarios**:

1. **Given** a message attaching a media object in `pending`, **When** a client reads channel
   history, **Then** the attachment carries `state: "pending"`.
2. **Given** that object has since been verified, **When** the same history is read again,
   **Then** the attachment carries `state: "ready"` — the state is read at query time, not
   frozen into the message when it was sent.
3. **Given** a message attaching an object already in `ready` at send time, **When** the sender
   receives its send response and when a subscriber receives the live frame, **Then** both
   carry `state: "ready"`.
4. **Given** an object that was rejected, **When** history is read, **Then** the attachment
   carries `state: "rejected"` and the message is still present — FR-MED-09's record that
   *something* was sent.

---

### User Story 2 - A placeholder resolves without polling (Priority: P2)

A client holding a message whose attachment is `pending` receives a frame when the verdict
lands, and replaces the placeholder. It does not poll.

**Why this priority**: FR-MED-07's second sentence and the chapter's title. It depends on story
1's state being defined, and it is the half a customer notices.

**Independent Test**: Subscribe to a channel, send a message attaching a `pending` object,
record a verdict, and assert a frame arrives on that channel naming the object and its new
state — with no request from the client in between.

**Acceptance Scenarios**:

1. **Given** a subscriber on a channel holding a message with a `pending` attachment, **When**
   the object becomes `ready`, **Then** that subscriber receives a frame carrying the media id
   and `ready`.
2. **Given** the same, **When** the object becomes `rejected`, **Then** the subscriber receives
   a frame carrying `rejected`.
3. **Given** an object referenced by messages in two channels the subscriber can see, **When**
   one verdict is recorded, **Then** a frame arrives on **each** referencing channel.
4. **Given** an object with no referencing message, **When** a verdict is recorded, **Then** no
   frame is published anywhere and the verdict still succeeds.
5. **Given** a duplicate verdict for an object already terminal, **When** it is refused by the
   compare-and-set, **Then** **no** frame is published — the event follows the state change,
   not the request.

---

### User Story 3 - A client that may not read the channel is not told (Priority: P3)

The frame reaches only connections authorised to read a referencing message, by the same rule
FR-MED-08 uses for the bytes.

**Why this priority**: Constitution I. It is separable from story 2 — story 2 can be built and
demonstrated on a channel the subscriber owns — but it is not optional to ship.

**Independent Test**: Two connections, one a member of a private referencing channel and one
not; record a verdict and assert exactly one receives the frame.

**Acceptance Scenarios**:

1. **Given** an object referenced only by a message in a private channel, **When** a verdict is
   recorded, **Then** a non-member connection receives nothing.
2. **Given** an object referenced by a message in a public channel of the environment,
   **When** a verdict is recorded, **Then** a non-member connection of that environment
   receives the frame — visibility, not membership (SRS 1.19).
3. **Given** two environments, **When** a verdict is recorded in one, **Then** no connection of
   the other receives anything.

---

### Edge Cases

- **A verdict for an object attached to nothing.** The commonest case in the lane: an upload
  slot taken and never used. No referencing channel, no frame, no error.
- **A verdict that races the attach.** The object goes `ready` between the send request being
  validated and the row being committed. The event fires against a reference that does not yet
  exist and reaches nobody; the send response carries the state, so the client is still correct.
  This is the case that makes story 1 load-bearing rather than redundant.
- **An object referenced by a message that was since deleted.** FR-MED-10 unlinks attachments on
  tombstone. Whether a tombstoned message still counts as a referencing channel for the purpose
  of this event must be answered, and answered the same way the delivery gate answers it.
- **The same object referenced twice in one channel.** One frame or two — a client that
  deduplicates on media id sees no difference, but the count is assertable and should be chosen
  rather than emergent.
- **A rejected object's frame.** FR-MED-09 wants a rejection marker, not a broken link, so the
  frame must carry enough for a client to render the refusal. Whether it carries the reason
  (`declaration_mismatch`, `scan_failed`) is a disclosure decision: the reason tells a sender
  why their file was refused and tells everyone else in the channel the same thing.
- **A client connected but buffering a resume.** The revision fabric sends buffering
  connections nothing, because the backfill is about to carry current state. The same question
  applies here and the same answer probably holds — but the attachment state is read at query
  time, so a backfill genuinely does carry it.
- **Six per-channel subscriptions.** If this chapter takes a sixth grammar it consumes the whole
  of ADR-25's remaining headroom, and the chapter after it that wants one is refused by a
  threshold this chapter did not set.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every attachment of type `media` returned on any read path MUST carry the media
  object's current state, one of `pending`, `ready`, `rejected`.
- **FR-002**: The state MUST be read at the time the message is served, not stored on the
  message when it was sent, so that a message sent before a verdict reflects the verdict
  afterwards without being rewritten.
- **FR-003**: A door that returns a message and omits the state is a defect of this requirement.
  **The set of such doors is whatever the derivation finds — this requirement deliberately does
  not list them.** Analysis pass 2 found the first version of FR-003 naming three doors while
  the code holds at least six construction sites: history and the send response
  (`messages.controller.ts:255,270`), **the edit response** (`:361,381`), live delivery,
  **resume/backfill** (`backfill.controller.ts:123`), and the gateway's socket ack
  (`session.ts:1628`). **The requirement forbade hand lists and then contained one.** The
  derived set is the definition and SC-002's both-directions assert is the test; a prose list
  beside it is a second source of truth that goes stale the first time a door moves.
  **THIS IS A DELIBERATE SUPERSET OF THE CLAUSE AND MUST BE AMENDED INTO IT.** FR-MED-07 names
  two doors — *"Real-time and history delivery"* — and the derivation finds more, including the
  send response and resume. A sender holding a 201 and a client replaying after a disconnect
  have the same placeholder problem as a reader. Extending a published clause silently is the
  divergence constitution VII's amendment rule forbids, so FR-012's revision states the derived
  set rather than leaving the platform broader than its specification.
- **FR-004**: When a media object transitions out of `pending`, the platform MUST publish an
  event naming the object and its new state to every channel holding a message that references
  it.
- **FR-005**: The event MUST be published only when the transition actually occurred. A verdict
  refused by the existing compare-and-set MUST publish nothing.
- **FR-006**: A transition for an object with no referencing message MUST publish nothing and
  MUST NOT fail the verdict.
- **FR-007**: A connection MUST receive the event only if it is authorised to read at least one
  referencing message, by the same channel-visibility rule FR-MED-08 uses — not a second access
  rule written for this path.
- **FR-008**: The decision on whether this event takes a sixth subject grammar MUST be recorded
  as an ADR that runs ADR-25's own arithmetic, stating the resulting per-channel SUBSCRIBE count
  and projected subject count against that ADR's two bounds. The working answer is **a sixth
  grammar** (see Assumptions); research MUST either confirm it by measurement or record why the
  rule points elsewhere.
- **FR-009**: The event MUST NOT be the only means by which a client can learn an attachment's
  state, and a test MUST demonstrate a client arriving at the correct state with no event
  delivered — the attach-after-verdict case.
- **FR-010**: The event MUST carry the state and MUST NOT carry the rejection reason, following
  the platform's existing disclosure reflex (FR-MED-06's three refusals are indistinguishable by
  decision). A sender that needs the reason reads it from a door already authorised to them. If
  research overturns this, the reason for overturning it MUST be recorded rather than the field
  simply appearing.
- **FR-011**: The behaviour for a message that has been tombstoned MUST match the delivery
  gate's existing answer for the same object, and MUST be asserted rather than assumed.
- **FR-012**: SRS FR-MED-07 MUST be amended to record what this chapter met and anything it
  left unmet, following the precedent of revisions 1.18, 1.19 and 1.20 — the clause moved from
  *vacuous* to *unmet with a reachable subject* and this chapter is where that sentence is
  resolved or re-stated. The amendment MUST record **every door the
  derivation found** (FR-003), not a count — pass 2 found "three" wrong before implementation
  began — and MUST record that `messageSchema`, the outbound contract published since chapter
  1.3, is what carries the state — because the clause's wording
  implies a delivery-time decoration and the platform's answer is a shape.

### Key Entities

- **Media object state**: one of three values on `media_objects`, already constrained by
  migration `0018`. This feature reads it and publishes its transitions; it does not add a
  value.
- **Attachment (media arm)**: today `{ type, media_id }` on one schema serving four users.
  **Analysis pass 1 falsified this entry's first version**, which said the request shape and the
  delivery shape were already different schemas. They are not: three request doors and
  `messageSchema` — the outbound contract the api builds — all use `attachmentSchema`. The
  chapter adds a third shape, `deliveredAttachmentSchema`, with `state` **required**, and points
  `messageSchema.attachments` at it. A sender still declares no state.
- **Referencing channel set**: the channels holding at least one message attaching a given
  object. Already computed by `channelsReferencingMedia`, built by 4.12 for the delivery gate
  and private to the repository.
- **The transition event**: new. Its subject, payload type and frame name are the design work
  of this chapter and are governed by ADR-19's rule and ADR-25's threshold.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A client holding a message with a `pending` attachment learns the terminal state
  with **zero requests issued by that client** between the send and the update. The latency
  bound is **NFR-PRF-01** — p50 < 100 ms, p95 < 250 ms, p99 < 500 ms — and **the interval is
  the verdict being recorded to the frame reaching the socket**, not NFR-PRF-01's own
  *send-acknowledged to recipient-receipt*. Same fabric, different endpoints: the clause is
  cited for its numbers, and the interval is stated here because measuring the wrong one would
  compare this chapter against a figure for something else.
- **SC-002**: Every door that returns a message with a media attachment returns its state:
  derived count of such doors equals the count covered by tests, in both directions.
- **SC-003**: An object referenced from N channels produces exactly N deliveries of the
  transition, for N of 0, 1 and 2, asserted at each value.
- **SC-004**: A connection not authorised to read any referencing message receives zero
  transition events, asserted for the private-channel non-member case and the cross-tenant case.
- **SC-005**: A duplicate verdict produces exactly zero additional events.
- **SC-006**: A client attaching an already-terminal object reports the correct state having
  received no event at all.
- **SC-007**: The subject-grammar decision is published with both of ADR-25's bounds evaluated
  numerically against the deployment law `5 × channels + 1 × connected users`.
- **SC-008**: `pnpm check:fences` reports 0 at the close, and the CI error set is compared per
  error against the pre-chapter baseline rather than per colour.
- **SC-009**: The chapter's prose is within the movement's word bound, with every published
  figure measured rather than estimated.

## Assumptions

- **The state machine is not this chapter's to build.** `0018` shipped it and the worker drives
  it. This chapter reads it and announces it. If a fourth state turns out to be needed, that is
  a finding to record, not a licence to widen the constraint — `0018`'s own comment argues
  against `scanning` specifically.
- **The verdict seam stays where it is.** `POST /internal/media/:mediaId/verdict` with its
  compare-and-set is 4.13's and is the natural place for a producer to hang, because it is the
  one place that knows a transition *happened* rather than that a verdict *arrived*.
- **The referencing-channel lookup exists and is correct.** 4.12 built and tested it. This
  chapter uses it rather than writing a second one; if it must become non-private that is a
  visibility change, not a new query.
- **The authorisation rule is `channelVisibleTo`.** SRS 1.19 settled this for the bytes, and a
  second rule for the notification would be the parallel ACL FR-MED-08's note forbids.
- **The working answer to §7.4 is a sixth subject grammar, `media:{channel_id}`.** ADR-19's rule
  is *a kind that cannot share a payload type cannot share a subject*, and both arms of
  `revisionFabricSchema` carry a `Message` — a media transition is not one. ADR-25 permits it:
  six per-channel SUBSCRIBEs does not *exceed* six. **It spends the whole remaining headroom**,
  so the chapter must say so plainly, because the next chapter wanting a grammar is refused by a
  bound this one consumed. Research confirms or overturns this; it is not assumed into the tasks.
- **The event is an optimisation over a correct floor**, in the same sense 4.13 recorded the
  upload notice as an optimisation over the sweep: it may not change any answer that the state
  on the attachment already gives.
- **Deferred to later chapters of this movement**: thumbnails and derived objects (FR-MED-05,
  next chapter), stored-byte metering (FR-MED-12), the `media_events` analytical table — 4.13's
  `gaps.md` 059-11 deferred it to the erasure chapter because its sum reads `uploaded` and
  `deleted`, and `deleted` does not exist until FR-MED-10 is built.
- **Not deferred, but not this chapter's subject**: FR-MED-09's rendering. This chapter makes
  the state available; the milestone chapter is where a rejection is shown to a reader.

## Open questions carried into planning

These are research obligations, not blockers. Each has a working answer recorded in Assumptions;
the chapter's job is to confirm or overturn it by measurement, which is how 059 resolved §7.3.

**Q1 — `docs/12` §7.4, and it is narrower than the document states.** ADR-25 already wrote the
threshold, so the chapter does not choose a policy; it runs one. Three candidate shapes:

| | Per-channel SUBSCRIBEs | Against ADR-25 |
|---|---|---|
| A sixth grammar, `media:{channel_id}` | 6 | At the bound — permitted, and it spends all remaining headroom |
| Widen `revision:{channel_id}`'s payload union with a third kind | 5 | Below the bound; but ADR-24's rule is *a kind that cannot share a payload type cannot share a subject*, and a media transition is not a `Message` |
| Widen `chan:{channel_id}` | 5 | Refused by the same rule ADR-24 used: everything on `chan` **is** a creation |

The second is the interesting one, because `revisionFabricSchema` is *already* a discriminated
union on `kind` — the precedent for a subject carrying more than one payload type exists on that
exact subject. The question is whether "a revision of a message" and "a transition of an object
a message references" are the same kind of thing. **This is the chapter's central design
argument and it should be decided by measurement and rule, not by taste.**

**Q2 — Does the transition event carry the rejection reason?** Answered *no* by default in
FR-010. The reason is a closed set of two (`declaration_mismatch`, `scan_failed`). Carrying it
lets a sender's UI say why; it also tells every other member of the channel that someone's
upload failed a virus scan. **The platform has already chosen this direction once**: FR-MED-06's
three refusals are byte-identical precisely so that a refusal does not report a fact about
somebody else. Overturning it needs an argument, not a preference.

**Q3 — One frame per referencing channel, or one per referencing message?** Answered *per
channel* by default, because the delivery gate is per object and `channelsReferencingMedia`
already returns a channel list. A channel can hold two messages attaching the same object, so a
client rendering per message must find them itself. The count MUST be asserted at N = 0, 1, 2
either way (SC-003), which is what makes the default falsifiable.
