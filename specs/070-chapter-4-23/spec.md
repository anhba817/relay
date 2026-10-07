# Feature Specification: chapter 4.23, "The channel a socket names"

**Feature directory**: `specs/070-chapter-4-23/`
**Created**: 2026-10-06
**Chapter**: Part 4, movement VII — **new**, and the second chapter Part 4 gained
**Source**: `docs/06-adr-deep-dives.md` ADR-38 · `docs/04-srs.md` FR-USR-01, FR-CHN-11,
FR-RTM-01/03 · `docs/03-journey-map.md` Journey 3 Stages 1 and 5 ·
`packages/protocol/src/internal.ts`

**Why this chapter exists.** Chapter 4.22 made thirteen REST routes take the
identifier the customer gave a channel. The gateway did not change, and it was never
asked to. So the same platform now answers one way on one surface and the other way
on the other — and `docs/12` §5 rule 4 says a milestone verifies rather than builds,
so the fix is its own chapter placed before 4.24.

**Name a chapter, never number it.** This is movement VII's sixth and the Priya
milestone follows it.

---

## The rule this chapter applies, written one chapter ago

> **ADR-38** — *"a noun with a customer-supplied identifier is addressed by it; a
> noun with only a Relay identifier is addressed by that, and where both could name
> the same thing the customer's wins."*

A channel has a customer-supplied identifier. On REST it is addressed by it. On the
socket it is not, and **nothing recorded that as a decision** — the ADR was written
after the gateway, and the gateway has never been read against it.

**AND THE CONTRACT STATES THE PRINCIPLE TWO LINES ABOVE THE FIELD THAT BREAKS IT.**
`packages/protocol/src/internal.ts`, on the session response:

> `user` is the EXTERNAL id, as everywhere else on this contract: internal uuids are
> the api's business.

The field below it is `channel_ids`, and it carries uuids. One contract, one
sentence, applied to one of its two identifier fields.

## The premise check, measured 2026-10-06

```
client-facing frame schemas carrying `channel`          7
  messageSchema · messageSendSchema · messageDeletedPayloadSchema
  mediaUpdatedSchema · membershipChangedSchema · typingSchema · typingSendSchema

sites in the gateway writing `channel:` onto a frame   21
  and a 22nd one call away, in the revocation backstop   session.ts:741
client-facing structures that name a channel by KEY or in a LIST   3
  connection.ack.payload.revisions · .cursor · .truncated
the gateway's references to a channel's external id     0
  the naive grep returns 5, all of them a user's
internalSendRequestSchema.channel_id                    z.string().uuid()
session.controller.ts:132  channel_ids: channels.map(c => c.channel_id)
  …which is `members.channelId` — the uuid, straight off the join
FR-RTM clauses naming which identifier addresses a channel   0 of 10
```

**THE GATEWAY CANNOT TRANSLATE TODAY BECAUSE IT HAS NOTHING TO TRANSLATE FROM.** It
holds no external id for a channel anywhere. That is the shape of the work: not a
rename, but giving the gateway the mapping it has never had.

**AND A COUNT OF FIELDS CANNOT SEE A MAP THAT IS KEYED BY ONE.** The first version
of this premise counted seven `channel` fields and twenty-one writes of them. The
`connection.ack` payload also carries `revisions` and `cursor`, both keyed by
channel, and `truncated`, a list of channel ids — three structures, on the one frame
every client receives first, that no grep for `channel:` can find. **The surface is
seven fields and three structures**, and the correction is here rather than in the
plan because it is what the chapter is about.

**AND THE SILENCE IS THE SAME SILENCE 4.22 FOUND.** No FR-RTM clause says which
identifier names a channel, exactly as no FR-CHN clause said it before FR-CHN-11.
The difference is that this time the rule already exists — so this chapter applies a
published decision rather than discovering that one is missing.

## What it costs a customer today

Journey 3's Stage 1 promises *"map order #88412 → channel `order-88412` with zero
lookup tables."* After 4.22 that holds on REST. Stage 5 is real-time — *"connected
clients see the deletion event immediately (FR-RTM-05)"* — and a client receiving
that frame gets a uuid. **To know which order it is about, they need the mapping the
journey says they will not need.**

So the promise is half-kept, on the two surfaces one support tool uses together.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A socket client never learns a uuid (Priority: P1)

A support tool opens a connection, receives events for the channels its user belongs
to, and sends into one of them — using the order numbers it already has.

**Why this priority**: it is the chapter. Everything else is a consequence.

**Independent test**: connect, provoke each frame kind, and read every `channel`
field; send by identifier; find no uuid in anything the client received.

**Acceptance scenarios**

1. **Given** a connected client, **when** any frame naming a channel is delivered,
   **then** its `channel` field is the identifier the customer supplied.
2. **Given** a connected client, **when** it sends with a channel identifier, **then**
   the message lands in that channel.
3. **Given** a client holding a uuid from before this chapter, **when** it sends with
   that uuid, **then** it keeps working or is refused with a named cause — never
   silently misrouted.
4. **Given** the session response at connect, **when** its channel list is read,
   **then** it carries identifiers.

### User Story 2 - The internal plumbing keeps its keys (Priority: P2)

Nothing behind the gateway's edge changes shape.

**Independent test**: read the fan-out subjects, the resume cursors and the
api-facing contract; find uuids, unchanged.

**Acceptance scenarios**

1. **Given** the fan-out subjects, **when** this chapter closes, **then** they are
   still derived from the channel's key.
2. **Given** the api's internal send door, **when** the gateway forwards a send,
   **then** what reaches the api is a key.

### User Story 3 - The clause catches up with the surface (Priority: P3)

A reader can find out, without reading code, which identifier names a channel on
each surface.

**Independent test**: read the amended clauses and answer the question for REST and
for the socket.

**Acceptance scenarios**

1. **Given** the specification after this chapter, **when** a reader asks how a
   channel is named in a real-time frame, **then** a clause answers.

### Edge Cases

- **A frame for a channel the client has since left.** The gateway's map is
  populated at connect; membership changes mid-session.
- **A channel renamed, or an identifier reused after a channel is deleted.** The map
  is a snapshot and the truth moves.
- **A send with an identifier the user is not a member of**, which must answer as it
  does today rather than leaking that the channel exists.
- **`ALL_CHANNELS`**, the membership-change sentinel, which is not a channel and
  must not be translated.
- **A resume cursor minted before this chapter**, keyed by uuid.
- **An identifier arriving inbound**, which has to become a key before the api, a
  subject or a cursor filter sees it — the translation runs in both directions and
  the first draft of this spec described only one.
- **A frame held rather than sent.** A message waiting in a resuming connection's
  buffer is both what a client will receive and what two internal comparisons index
  by channel. Whichever name it carries while it waits, both must keep working.
- **A ban**, which never reaches a client as a wildcard: the sentinel is expanded
  into one frame per real channel before any socket sees it.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every field naming a channel in a frame delivered to a client MUST
  carry the customer-supplied identifier.
- **FR-002**: Every field naming a channel in a frame accepted from a client MUST
  accept the customer-supplied identifier.
- **FR-003**: A client holding a Relay identifier from before this chapter MUST
  either keep working or be refused with a named cause. Silent misrouting is the one
  forbidden outcome.
- **FR-004**: The translation MUST be confined to the gateway's client edge. The
  fan-out subjects, the resume cursors' internal keying and the api-facing contract
  keep the Relay identifier.
- **FR-005**: An identifier that names no channel the client may see MUST be refused
  exactly as that case is refused today, revealing nothing new about what exists.
- **FR-006**: The mapping MUST be scoped to the connection's own tenant, and that
  scope MUST be demonstrated by removing it and observing a named test fail.
- **FR-007**: Membership gained or lost during a session MUST NOT leave the mapping
  wrong in a way a client can observe.
- **FR-008**: A clause MUST state which identifier names a channel on the real-time
  surface, so the next frame added is decided rather than guessed.
- **FR-009**: Nothing outside this chapter's subject may change behaviour.
- **FR-010**: Where measurement falsifies a published clause or document, the
  document MUST be amended rather than left to diverge.

### Key Entities

- **A channel's identity** — the string the customer supplied. What a client names.
- **A channel's key** — the identifier Relay minted. What subjects, cursors and the
  api continue to use.
- **The session's mapping** — key to identity, for the channels one connection may
  hear, held for that connection's life.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every frame kind that names a channel is provoked in one test and its
  `channel` field asserted to be the identifier — **7 of 7**, asserted per frame
  rather than in aggregate; **and the three structures that name a channel by key or
  in a list are asserted separately — `revisions`, `cursor` and `truncated`, 3 of
  3.** Ten assertions, not one.
- **SC-002**: A send by identifier reaches the channel, and a send by Relay
  identifier behaves as FR-003 requires, each asserted separately — **and the same
  pair for a typing frame**, which is the one inbound path with no refusal behind it:
  an unknown channel there is dropped with no frame, no close code and no log line.
- **SC-003**: The first frame a client receives — `connection.ack` — carries no
  Relay identifier for a channel, in a field, as a key, or in a list. **Stated about
  the ack rather than about the internal session response**, because a client never
  sees the latter and the criterion as first written could pass while every ack still
  handed out uuids.
- **SC-004**: Nothing a connected client receives over a full session contains a
  channel's Relay identifier — counted across the session, with the count stated.
- **SC-005**: Removing the mapping's tenant scope turns at least one named test red.
- **SC-006**: The fan-out subjects and the api-facing send door are unchanged,
  demonstrated rather than asserted.
- **SC-007**: Journey 3 Stage 5 is reachable with the order number alone, which
  chapter 4.24's milestone then asserts end to end.
- **SC-008**: `git diff --name-only part4-ch22 --` contains no file outside this
  chapter's subject, tests and documents. One dot, not two (067-3).
- **SC-009**: The fence chain reports 0 and all six tutorial gates exit 0.
- **SC-010**: The CI error set is compared per error against the pre-chapter
  baseline, in both directions.

---

## Assumptions

- **The division is 4.22's.** That chapter resolved at the request boundary and left
  ten repository methods untouched; this one translates at the gateway's client edge
  and leaves the subjects, the cursors and the internal contract untouched. The
  assumption is that the same line holds here, and the premise check for it is that
  the gateway's own plumbing never needs to show a client anything.
- **Accepting both forms is a transition, not a design.** Published clients hold
  uuids. Whether the Relay identifier is ever refused on the socket is a later
  chapter with a deprecation path, exactly as it is for REST.
- **The map is per connection, populated at connect.** The session response already
  returns the channel list at that moment, so the identities can ride with it. A
  channel the user joins mid-session arrives through a membership change, which is
  the path FR-007 is about.
- **`ALL_CHANNELS` is not a channel.** It is the sentinel the membership-change frame
  uses, and translating it would be a defect.
- **No FR-RTM clause is being contradicted**, because none of the ten names an
  identifier. FR-008's clause is new rather than an amendment, which is FR-CHN-11's
  shape one chapter on.
- **Two chapters in a row have come from the previous chapter's findings.** This is
  worth saying in the chapter rather than only here: 4.22 came from the milestone's
  premise check, and this came from 4.22's response-shape sweep. The argument for
  taking it is that the surface is bounded and measured; the argument against is that
  a part growing from its own discoveries can stop converging.
