# Feature Specification: Chapter 3.24 — the message that is not only text

**Feature Branch**: `042-chapter-3-24`
**Created**: 2026-09-04
**Status**: Draft
**Input**: User description: "chapter 3.24"

FR-MSG-11 has been P2 — Phase 2, this part of the book — since the SRS's first draft:

> The system shall support up to 10 attachments per message. An attachment is either a
> reference to a Relay-hosted media object (`media_id`, see §4.14) or an external URL with a
> declared kind (`image`, `audio`, `video`).

**`messages.attachments` has been a column since chapter 2.1 and nothing has ever written
it.** One thing touches it: chapter 3.23's deletion, which sets it to `NULL` because
`docs/05-sad.md:342` says a tombstone does. The column is read by nothing, returned by no
route, and absent from every frame.

**This is the third time this shape has come up and the second chapter in a row.** 3.23 found
`edited_at`, `deleted_at` and a nullable `text` in the same state and called it the reverse of
the usual gap — readers with no writer. Here it is narrower and stranger: a column whose only
writer sets it to null, in a chapter that shipped one chapter ago.

**AND THE PROTOCOL SAYS THIS ARRIVES IN PART 4.** `packages/protocol/src/frames.ts:14` reads
*"metadata/attachments/edit/tombstone fields arrive with Part 2/4"*. The edit and tombstone
halves arrived in Part 3; the SRS marks FR-MSG-11 **P2**, which is Part 3, and §4.14's hosted
media **P3**, which is Part 4. **One clause, two halves, two phases** — and a comment in the
published protocol that schedules the whole thing for the later one.

**A second reader with no writer sits in the analytical schema.** `docs/05-sad.md:608`
publishes `attachment_count UInt8` on `message_events`. That table is Part 4's and unbuilt, so
nothing is wrong today — but the count has to be derivable from what this chapter writes, and
saying so now is cheaper than discovering it then.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A message carries a picture somebody else is hosting (Priority: P1)

A courier's dispatch system already stores photographs. When a driver reports a damaged
parcel, the customer's backend sends a message whose text is the driver's note and whose
attachment is the URL of the photograph it already holds. Every member of the channel — those
connected now and those who read history later — receives the note and the link together, and
knows the link is an image without fetching it.

**Why this priority**: it is the whole of the P2 half of FR-MSG-11. Without it the clause is
unmet and `messages.attachments` stays a column nothing writes.

**Independent Test**: send a message with one external-URL attachment, assert a connected
member's socket receives it with the attachment, and assert the history route returns the same
attachment for a client that was not connected.

**Acceptance Scenarios**:

1. **Given** a channel with two connected members, **When** one sends a message with an
   attachment of kind `image` and an external URL over REST, **Then** the other member's socket
   receives the message with that attachment, and **the REST response carries it too**.
2. **Given** the same send made over a socket instead, **When** it commits, **Then** the
   sender's `message.ack` carries **only the sequence number**, as it has since chapter 2.2 —
   and the sender learns its attachments landed from the `message.created` frame the fan-out
   delivers to it like any other member.

   **This scenario exists because the first draft asked for something the protocol cannot do.**
   It said "the sender's acknowledgement carries it too" without naming a door.
   `messageAckSchema`'s payload is `{ seq }` and has never carried a message; widening it is a
   protocol change no requirement asks for, and the socket sender already holds what it sent.
3. **Given** a message sent with two attachments, **When** any member reads channel history,
   **Then** both attachments are returned in the order they were sent.
4. **Given** a message sent with no attachments, **When** it is read back, **Then** the
   attachment list is empty rather than absent, so a client needs no special case.

### User Story 2 - Ten is a limit and eleven is a refusal (Priority: P1)

A customer's integration loops over a folder and attaches everything in it. The eleventh
attachment is refused with a message naming the bound, before any part of the message is
written — so a retry with ten succeeds and nothing half-landed.

**Why this priority**: FR-MSG-11 states a bound, and a bound with no refusal is a suggestion.
Every other list bound in this platform — 100 members, 100 users, 500 backfill rows — is
enforced at the boundary and this one has to be too.

**Independent Test**: send eleven attachments, assert the refusal names the field and the
bound, and assert no message row was written.

**Acceptance Scenarios**:

1. **Given** a send with eleven attachments, **When** it is submitted, **Then** it is refused
   with a validation error naming the offending field, and the channel's sequence does not
   advance.
2. **Given** a send with exactly ten attachments, **When** it is submitted, **Then** it
   succeeds and all ten are returned.
3. **Given** an attachment whose kind is not one of the three the clause names, **When** it is
   submitted, **Then** it is refused rather than stored as an unknown kind.

### User Story 3 - A moderator reads what was attached, after it was deleted (Priority: P2)

A tenant's operator investigating a complaint reads a channel's history. A message that was
deleted shows as a tombstone with no text and **no attachments**, because deletion unlinks
them — and the operator can see that it had them, without seeing what they were.

**Why this priority**: FR-MSG-08 already nulls the column and FR-MOD-01 gives an operator the
complete history. The interaction between the two is decided by what this chapter writes, and
deciding it by accident is how a deleted photograph stays reachable.

**Independent Test**: send a message with attachments, delete it, and assert the history
route returns the tombstone with an empty attachment list.

**Acceptance Scenarios**:

1. **Given** a message with two attachments, **When** it is deleted, **Then** history returns
   it with a null text and an empty attachment list.
2. **Given** that same deletion, **When** a connected member receives the deletion event,
   **Then** the event carries no attachment data, for the reason it carries no text.

### Edge Cases

- **A URL that is not a URL.** A caller sends `javascript:alert(1)` or a `data:` URI as an
  attachment. Clients render attachments; a scheme other than `http`/`https` is a client-side
  execution surface reaching them through this platform.
- **A URL nobody can reach.** Relay does not fetch attachment URLs, so a 404, a private
  address, or a host that never resolves is indistinguishable from a working link at send
  time. What the platform can promise is bounded by that.
- **An attachment with no message.** A send whose text is empty and whose only content is an
  attachment — the case the SRS's own reversal note calls out: *"a driver's photo of a damaged
  parcel **is** the message."*
- **An edit that changes attachments.** FR-MSG-07 says an edit changes message *text*.
  Chapter 3.23's edit route takes a body of one field and its history table stores
  `prior_text`. Whether attachments can be edited at all is a decision this chapter inherits.
- **A duplicate URL.** The same link attached twice to one message: **two attachments**
  (FR-021). Nothing deduplicates, for the reason chapter 3.23 gave about comparing texts.
- **The idempotent retry.** A repeated send with the same idempotency key returns the original
  message; its attachments must come back with it and must not be re-inserted.
- **A tombstone recovered by an old idempotency key**, which chapter 3.18 already guards for
  text, now has an attachment list too. Both guards read `text !== null` and an
  attachments-only message carries `""`, so they hold — **and that is a claim about two lines
  of code that this chapter changes the meaning of**, which is what a test is for rather than a
  reading.

- **A stored value that today's rules would refuse.** A row whose attachments were written
  before FR-023 (3.24)'s 2,048-character bound, or planted by hand in a test fixture. **The read
  paths do not re-validate** — the column is written only through the validated send path, and
  a cast at the read site is not a check (`data-model.md`, "What the reader gets"). The cost of
  that decision is where the failure lands: an invalid stored array is refused by the gateway's
  strict parse of the api's response, which throws and closes the socket **1011**, not by
  anything that names the row. Every other edge case here guards the door; this one is about
  the cupboard, and the decision is to trust it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST accept up to 10 attachments on a message send.
- **FR-002**: An attachment MUST declare a kind of `image`, `audio` or `video`, and a kind
  outside that set MUST be refused.
- **FR-003**: An attachment MUST carry an external URL. A `media_id` attachment MUST be
  refused with a code of its own until §4.14 exists.
- **FR-003a**: The refusal in FR-003 MUST say that hosted media is not available rather than
  that the field is invalid, because `media_id` is a published part of FR-MSG-11 and a
  customer reading the clause will send one.
- **FR-003b**: The attachment shape MUST be a discriminated union on a kind field from the
  first version, so §4.14 adds an arm rather than changes one. **This is the same rule
  chapter 3.23 reached for its subject grammars**: a kind that cannot share a payload type
  cannot share a shape, and a `media_id` attachment carries no URL.
- **FR-004**: An attachment URL MUST be refused unless its scheme is `http` or `https`.
- **FR-005**: A send carrying more than 10 attachments MUST be refused, and MUST write no
  message row.
- **FR-006**: Attachments MUST be returned in the order they were submitted, on every path
  that returns a message.
- **FR-007**: A message with no attachments MUST be returned with an empty list rather than an
  absent field, so a reader needs no special case.
- **FR-008**: Attachments MUST be delivered to connected members in the same frame as the
  message they belong to, not as a second event.
- **FR-009**: History responses MUST include each message's attachments.
- **FR-010**: The resume backfill MUST include attachments, so a client that was away and a
  client that stayed connected hold the same message.
- **FR-011**: A recognised idempotent retry MUST return the original message's attachments and
  MUST NOT write them a second time.
- **FR-012**: Deleting a message MUST unlink its attachments, and the tombstone MUST be
  returned with an empty attachment list on every read path.
- **FR-013**: The deletion event MUST NOT carry attachment data, for the same reason it
  carries no text.
- **FR-014**: An attachment MUST NOT be readable by a caller who cannot read the message it
  belongs to.
- **FR-015**: The message payload used by creation and edit events MUST carry attachments
  identically, so a consumer needs one shape for both.
- **FR-016**: Whether an edit may change attachments MUST be decided and stated. If it may
  not, an edit MUST leave them unchanged rather than clearing them.
- **FR-017**: The number of attachments on a message MUST be derivable from what this chapter
  writes, so §4.14's `attachment_count` has a source when Part 4 builds it.
- **FR-018**: The comment at `packages/protocol/src/frames.ts:14` scheduling attachments for
  Part 4 MUST be corrected, because FR-MSG-11 is P2.
- **FR-019**: A message whose text is empty MUST be accepted when it carries at least one
  attachment, and MUST be stored with an empty string rather than a null.
- **FR-019a**: An attachments-only message MUST stay distinguishable from a tombstone on
  every read path. `text = ""` and `text IS NULL` are different values and chapter 3.23's
  tombstone predicate reads the second, so this MUST hold without changing that predicate —
  and a test MUST assert it rather than a comment claiming it.
- **FR-019b**: A message with no text and no attachments MUST still be refused. Relaxing the
  bound is conditional on there being something to carry, not unconditional.
- **FR-020**: The attachment shape MUST leave room for §4.14's `media_id` arm without a
  breaking change to any published payload.
- **FR-021**: The same URL attached twice to one message MUST be stored and returned twice.
  The platform MUST NOT deduplicate attachments. **Two identical links are two attachments**
  for the same reason FR-021 of chapter 3.23 gives about texts: every definition of sameness —
  a trailing slash, a case-different host, a query parameter in another order — is a decision a
  customer would have to be told about, and the caller's list is the caller's.
- **FR-022**: The attachments field on a message payload MUST be present on every payload that
  carries a message, never optional, so that a reader needs no special case on the wire either.
  A message with none carries an empty list.
- **FR-023**: An attachment URL MUST be refused above 2,048 characters. **FR-MSG-11 states no
  length**, so this is the chapter's own bound and it takes the platform's only precedent for a
  stored URL: `users.avatar_url` has been capped at 2,048 since chapter 3.16. A second number
  for the same kind of value would be two limits a customer has to remember. **A refusal no
  requirement authorises is what this clause exists to prevent** — the bound was in the data
  model, the contract and a test assertion for seven analysis passes with no clause behind it.

### Key Entities

- **Attachment** — a kind (`image`, `audio`, `video`) and a location. Belongs to exactly one
  message, ordered within it. Carries no bytes: this platform stores a reference and never
  fetches it.
- **Message** — gains an ordered list of attachments. Its existing fields are unchanged, which
  FR-015 makes a requirement rather than an accident.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A member connected when a message with attachments is sent, and a member who
  reads it from history an hour later, see the same attachments in the same order.
- **SC-002**: A send with eleven attachments is refused, and the channel's message count is
  unchanged afterwards.
- **SC-003**: A deleted message's attachments are unreachable through **each of the six read
  shapes** `data-model.md` enumerates, named one at a time rather than asserted for the ones
  somebody remembered. Six is the count this chapter's research took from the code; a seventh
  appearing is the finding, not an inconvenience.
- **SC-004**: An attachment whose URL uses a scheme other than `http` or `https` never reaches
  a client.
- **SC-005**: A client that was disconnected across a send with attachments, and follows the
  documented repair, ends with the same view as a client that stayed connected.
- **SC-006**: Every read path's behaviour with respect to attachments is stated in the
  architecture document, derived from the code at the time of writing rather than from a list.

## Assumptions

- **Relay never fetches an attachment URL.** Not at send time, not later. The platform stores
  a reference; whether it resolves is between the client and whoever hosts it. This follows
  §4.14's whole design premise — bytes go direct to storage and never through Relay compute
  (NFR-PRF-08, ASM-06) — applied to the half of FR-MSG-11 that has no storage at all.
- **No thumbnailing, no probing, no scanning.** FR-MED-04 and FR-MED-05 attach those to hosted
  media, which is Part 4. An external URL gets none of them, and a customer attaching a link
  is attaching their own content at their own risk.
- **The 4 KB metadata bound (FR-MSG-01) is separate.** Attachments are not metadata and do not
  consume that budget.
- **§4.14's `media_id` arm arrives in Part 4** with FR-MED-06's environment-scoped validation,
  which cannot be written before media objects exist.
- **The tombstone predicate is chapter 3.23's and this chapter does not touch it.** That
  chapter chose `text === null` as the test for "this message is deleted", with a written
  argument, and five places branch on it. An attachments-only message stores `text = ""`,
  which is a value those five places already treat as a live message — so the predicate keeps
  working and nothing is reopened. **The cost is that the empty string now means two things**:
  a message somebody sent with no words, and a message somebody sent with attachments and no
  words. Nothing distinguishes them, and nothing needs to.

## Decisions taken during specification

**Two questions had no defensible default and both were put to the reader.**

**The chapter builds the external-URL half and refuses `media_id`** (FR-003, FR-003a,
FR-003b). FR-MSG-11 is P2 and §4.14 is P3; a clause cannot depend on a later phase's
infrastructure. The alternative — accepting a `media_id` as an opaque reference now — would
have the platform holding references it cannot resolve, cannot scope to a tenant and cannot
refuse, with FR-MED-06's environment check arriving after the data it is meant to guard. The
shape is a discriminated union from the first version so Part 4 adds an arm.

**An attachments-only message stores an empty string, not a null** (FR-019, FR-019a,
FR-019b). The rejected alternative is the interesting one: a null text reads more honestly as
*this message has no text*, and collides head-on with chapter 3.23's tombstone predicate,
which five places branch on and which was chosen one chapter ago with a written argument.
`text = ""` is a value every read path already handles, so the predicate is untouched and
nothing is reopened.

## Dependencies

- Chapter 3.23's deletion path, which already nulls `attachments` and whose tombstone
  predicate this chapter must not break.
- Chapter 3.18's fan-out and 3.23's revision fabric, which carry the payloads that gain a
  field.
- `messages.attachments`, present since chapter 2.1 and unwritten.
