# Feature Specification: Chapter 3.17 — the message that never arrived, and the sender it never had

**Feature Branch**: `035-chapter-3-17`

**Created**: 2026-08-25

**Status**: Draft

**Input**: User description: "chapter 3.17"

---

## What this chapter is about

A customer sends a message over REST. A member of that channel is connected on a socket.
The message does not arrive — not live, and not when the socket reconnects. Nothing in
the published documentation says it will not.

**Two things are wrong and only one of them is the missing arrow.** The api never publishes,
so nothing reaches a socket. And a message sent by the customer's own server has no sender at
all, so even the path that could deliver it has nothing to put in the frame. The second is the
older mistake: the platform has been treating "the customer's software posted this" as an
absence, when it is an identity the customer was never given a way to name.

Chapter 3.14 gave the SRS Phase 2 exit criterion its verdict — *"an external developer
integrates using only public documentation, with no assistance"* — and recorded it as **met
in part**. This is the concrete half of what is missing. An outsider who builds the obvious
integration cannot succeed, and the sealed integration suite only passes because a failing
test corrected it, which is the assistance the criterion forbids.

**The architecture already describes the fix.** `docs/05-sad.md`'s C4 diagram draws
`api -- "publish fan-out" --> redis`, and the gateway as `subscribe chan:{id}`. The api
half of that arrow was never built: the gateway publishes when a message arrives over a
socket, so socket-sent messages fan out and REST-sent ones do not.

### The state as measured, not as recorded

Chapters 3.12 and 3.13 recorded this as **two independent causes**. It is now one, and the
difference matters because it halves the work and changes what the chapter has to decide.

| send path | attributed | live delivery | delivery on resume |
|---|---|---|---|
| socket `message.send` | yes | yes — the gateway publishes | yes |
| internal `POST /internal/messages` | yes | yes — the gateway publishes after it returns | yes |
| **REST with a user token** | **yes, since chapter 3.15** | **no** | **yes — and nothing tests it** |
| **REST with an application credential** | no, by design (chapter 3.3) | **no** | **no** |

The second cause — a senderless row cannot become a frame, because `toFrame` drops it and
`messageSchema.user` is a non-empty string — now applies only to the **key-authenticated**
send, which is unattributed deliberately: chapter 3.3 decided a tenant acting for itself
carries no user.

**And that decision is what this chapter reverses.** A message with no sender cannot be
rendered, cannot be moderated, cannot be attributed in an audit trail, and cannot be
delivered without inventing a representation for "nobody". The platform has been treating
"the customer's own server posted this" as an absence when it is an identity — the customer
simply had no way to name it.

`public-surface.itest.ts` pins the current behaviour and pins it with an application
credential, so its name — *"does NOT deliver a REST-sent message, live or on resume"* — is
broader than what it proves.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — a REST-sent message reaches a connected member (Priority: P1)

A customer's server posts a message to a channel over REST. Every member of that channel who
is connected receives it within the same moment a socket-sent message would arrive.

**Why this priority**: it is the integration every outsider writes first, and the reason
Phase 2's exit criterion is unmet.

**Independent test**: connect a member, post over REST, assert the frame arrives; disconnect,
post, reconnect with a cursor, assert it arrives on the resume.

**Acceptance scenarios**

1. **Given** a member connected to a channel, **When** a message is posted to that channel
   over REST with a user token, **Then** that member receives a `message.created` frame.
2. **Given** a bot user the tenant created, **When** a message is posted with an application
   credential naming that bot, **Then** connected members receive a `message.created` frame
   whose sender is the bot — indistinguishable in shape from a person's message, and
   distinguishable in identity because the bot's record says what it is.
3. **Given** an application credential, **When** a message is posted naming **a person**,
   **Then** it is refused: a key that can post as any human is an impersonation surface.
4. **Given** an application credential, **When** a message is posted naming no sender at all,
   **Then** it is refused with the field named.
3. **Given** a member whose socket is closed, **When** a message is posted over REST and the
   member reconnects with a cursor, **Then** the message is in the resume.
4. **Given** two members on two different gateway instances, **When** a message is posted
   over REST, **Then** both receive it.
5. **Given** a non-member of a private channel connected to a socket, **When** a message is
   posted to that channel, **Then** that socket receives nothing.

### User Story 2 — a message is delivered once, not twice (Priority: P1)

A message that reaches a socket arrives exactly once, whichever door it came in through.

**Why this priority**: the fix creates this risk. The gateway publishes today; if the api
also publishes, every socket-sent message is delivered twice. This story is what makes story
1 safe to build.

**Independent test**: send over a socket, assert one frame; send over REST, assert one frame;
send a recognised idempotent retry, assert no second frame.

**Acceptance scenarios**

1. **Given** a member connected to a channel, **When** another member sends over a socket,
   **Then** exactly one `message.created` frame arrives.
2. **Given** the same, **When** a send is repeated with an idempotency key that has already
   been used, **Then** no frame is published for the repeat.
3. **Given** a message whose text is a tombstone, **When** it is committed, **Then** no
   `message.created` frame is published for it.

### User Story 3 — the documentation says what a customer will see (Priority: P2)

An integrator reading the published reference can predict, before writing code, which sends
reach a socket and which do not.

**Why this priority**: Phase 2's criterion is about documentation, not only behaviour. A
platform that delivers correctly and describes it wrongly fails the criterion the same way.

**Independent test**: the sealed outsider suite posts over REST with an API key, receives the
frame on a socket, and passes without being corrected.

**Acceptance scenarios**

1. **Given** the published documentation, **When** an integrator looks for whether a
   REST-sent message reaches a socket, **Then** they find a statement that matches the
   platform's behaviour for both credential classes.
2. **Given** the published frame contract, **When** an integrator reads what `user` may hold,
   **Then** it says the sender is null for a message the tenant sent on its own behalf.

### Edge cases

- The fan-out fabric is unavailable when a message commits. Delivery is lossy by design
  (ADR-07) and durability is not: the send must still succeed.
- A message commits and the publish fails. The message is in history and the resume path
  recovers it; the chapter states this rather than treating a failed publish as an error the
  caller sees.
- A channel with no connected members. Publishing costs one round trip to a subject nobody
  is subscribed to.
- A message posted to an archived channel is refused before any publish (chapter 3.15).
- A banned user's REST send is refused before any publish (chapter 3.16).

---

## Requirements *(mandatory)*

### The delivery path

- **FR-001**: A message committed through any public or internal write path MUST be published
  to its channel's fan-out subject.
- **FR-002**: The publish MUST happen after the commit, never before, and MUST NOT be part of
  the transaction that commits the message.
- **FR-003**: A failed publish MUST NOT fail the send. The caller receives the same response
  it receives today, and the failure is recorded where an operator can see it.
- **FR-004**: A message MUST be published exactly once per commit. A recognised idempotent
  retry MUST NOT publish a second time.
- **FR-005**: The publish MUST NOT be performed twice for one message by two different
  services. Whichever component publishes, the other stops.

### The unattributed send

- **FR-006**: Every message MUST have a sender. The platform MUST NOT accept a write that
  leaves `messages.user_id` null.
- **FR-006a**: A tenant MUST be able to create a **bot user** — a user record that represents
  the customer's own software rather than a person — carrying a **description** of what it is
  and what it posts. The description is what a human sees when they ask "what is this and why
  did it message me".
- **FR-006b**: A bot user MUST be distinguishable from a person by a stored property, not by
  a naming convention. A client rendering a conversation, a moderator reading an audit trail
  and a permission check must all be able to tell them apart without parsing an identifier.
- **FR-006c**: A key-authenticated send MUST name its sender, and the named user MUST be a
  bot user of that tenant. A key-authenticated send naming a **person** MUST be refused: an
  API key that can post as any human is an impersonation surface, and the credential's holder
  is the customer's server rather than any of its users.
- **FR-006d**: A bot user MUST NOT authenticate. No token is minted for it and no socket is
  opened as it — it is an identity messages are sent *as*, not an account that logs in.
  Implicit creation on first authentication (FR-USR-02) therefore never produces one.
- **FR-006e**: A bot user MUST otherwise behave as a user: it can be a channel member, hold a
  role, be listed, be banned, and be deleted, and every isolation guarantee that applies to a
  user applies to it.
- **FR-006f**: The public send route MUST refuse a key-authenticated request that names no
  sender, naming the field. **This is a breaking change to a route shipped since chapter
  2.2**, and the chapter MUST say so and state what an existing caller has to change.
- **FR-006g**: Messages already stored with no sender MUST keep working on every read path
  that can reach them — history, the listing's `last_message`, and the resume — because the
  column is nullable and the rows exist. The chapter MUST state whether those rows become
  deliverable, and the answer MUST be the same live and on resume (FR-007).

### Scope

- **FR-016**: [NEEDS CLARIFICATION: does the bot-user model ship in this chapter, or as its
  own chapter ahead of it?] This chapter was scoped as one missing publish. It now carries a
  new user kind, a description field, an amendment to the SRS, a breaking change to a route
  shipped in chapter 2.2, and the fan-out. Chapter 3.12 was specified as one chapter and
  shipped as three; chapter 3.15 as one and shipped as two — both because a chapter reached
  its word ceiling and split. The two candidate shapes are **one chapter** ("a message has a
  sender, and it arrives") or **two** (3.17 the bot user and the sender requirement, 3.18 the
  fan-out — pushing presence to 3.19).

### The governing documents

- **FR-014**: The SRS has **no bot, system, or service-account concept** — `FR-USR-01`
  through `FR-USR-06` describe end users supplied by the customer, and nothing in the SAD
  mentions one either. This chapter's model therefore requires an **explicit amendment**,
  which is what the constitution's Governance section demands: where the constitution
  conflicts with the SRS or SAD, *"the conflict MUST be resolved explicitly by amendment
  rather than"* ignored.
- **FR-015**: The amendment MUST be made before the chapter claims delivery, and the chapter
  MUST cite the amended clause rather than describe behaviour the governing document does not
  contain. A feature that ships ahead of its requirement is the defect chapter 3.12's
  traceability map recorded and this feature corrected twice.

### What must not change

- **FR-008**: Delivery MUST remain scoped: a socket receives frames only for channels its
  session carries, and a non-member of a private channel receives nothing (FR-CHN-05,
  chapter 3.15's four doors).
- **FR-009**: Ordering MUST remain the sequence the write path assigns. The fan-out does not
  reorder and does not renumber.
- **FR-010**: A send MUST remain durable when the fan-out is unavailable, and the acknowledged
  sequence MUST remain the committed one (FR-MSG-05).

### The record

- **FR-011**: `public-surface.itest.ts`'s pinned behaviour MUST be replaced rather than
  deleted: the chapter states what the platform did, what it does now, and which of the two
  causes recorded in chapters 3.12 and 3.13 was already closed by chapter 3.15.
- **FR-012**: Chapter 3.14's Phase 2 verdict MUST be re-issued with the concrete half closed
  and the comprehensibility half still open, in the chapter rather than only in a spec
  document.
- **FR-013**: The chapter MUST state that a user-token REST send has been recoverable on
  resume since chapter 3.15 and that no test covered it, because a behaviour nobody asserted
  is a behaviour nobody has.

---

## Success Criteria *(mandatory)*

- **SC-001**: A message posted over REST reaches a connected member of that channel, measured
  end to end through the public API and a real socket.
- **SC-002**: A message posted over REST while a member is disconnected is present when that
  member reconnects with a cursor.
- **SC-003**: A message sent over a socket produces exactly one frame per connected member,
  measured before and after this chapter's change.
- **SC-004**: A message is delivered to members on two different gateway instances.
- **SC-005**: A non-member of a private channel receives nothing, across every write path,
  verified by the existing indistinguishability oracle.
- **SC-006**: With the fan-out fabric stopped, a send still succeeds and the message is
  retrievable from history.
- **SC-007**: A message sent by a customer's server arrives with an identity a person can
  read, on the socket and in history, and that identity says it is software rather than a
  person.
- **SC-007a**: No write path in the platform can produce a message with no sender, shown by
  removing each guard in turn and watching a test go red.
- **SC-007b**: Messages already stored without a sender behave identically live and on resume,
  whichever behaviour FR-006g chooses.
- **SC-007c**: An application credential cannot post as a person, verified over the public
  route with a real human user of the same tenant.
- **SC-008**: The sealed outsider suite exercises the REST-then-socket path and passes
  without being corrected — which is the specific failure chapter 3.14 recorded.
- **SC-009**: The chapter is inside the series' 2,000–4,000 prose-word bound, and every
  fenced file replays onto the platform repository.

---

## Assumptions

- **The fan-out stays lossy and stays Redis.** ADR-07 chose fire-and-forget pub/sub and
  rejected JetStream for live delivery, on the grounds that ordering and resume are correct
  independently. This chapter delivers a message; it does not revisit that decision.
- **The publish belongs to the api.** The SAD's C4 diagram already draws it there, the api is
  the only service that knows a message committed, and putting it there is what removes the
  duplicate risk rather than creating it.
- **A bot lives in `users` rather than in a table of its own.** Membership, read positions,
  roles, the listing, `toFrame`, the ban and every isolation guarantee are keyed on
  `users.id`; a parallel table would fork all of them and would have to be attacked separately
  by the gauntlet. The cost is that `users` now holds two kinds of thing and every query that
  means "a person" has to say so.
- **The frame contract does not change.** This is the reason to prefer a bot over a nullable
  sender: `messageSchema.user` stays a non-empty string, no published client has to tolerate a
  new shape, and chapter 3.16's frame-shape assertion keeps passing. **The alternative
  specified two hours earlier — making the sender nullable — is rejected on those grounds**,
  and the rejection is worth recording because the nullable version looked cheaper right up
  until "what does a client render for nobody" had to be answered.
- **Chapter 3.3's decision is reversed, not reinterpreted.** It reads: *"Absent on the public
  REST route, where a key-authenticated send is unattributed."* That was right when nothing
  read the sender and wrong once the sender has to be rendered, delivered and moderated. The
  chapter states the reversal rather than quietly editing the comment.
- **Existing senderless rows are legacy, not a supported state.** The nullable column stays
  because the rows exist; nothing new may create one.
- **The gateway keeps its subscription model.** One subject per channel, subscribed when a
  session needs it. This chapter changes who publishes, not who listens.
- **Presence and typing are chapter 3.18's.** FR-RTM-05 names message creation, edit,
  deletion, membership change, presence change and typing in one clause. This chapter takes
  the message half; the rest is the next chapter, and the split is stated so the clause is
  not recorded as delivered twice.
- **Message edit and deletion have no writer yet.** FR-MSG-08 is unimplemented — nothing in
  the platform writes a tombstone — so `message.updated` and `message.deleted` remain declared
  frames with no sender. This chapter does not build them and says so.

## Dependencies

- Chapter 3.15's attributed public send (`messages.controller.ts` resolves the caller), which
  is what closed the resume half for user-token sends.
- Chapter 2.6's fan-out fabric and its subject-per-channel scheme.
- Chapter 2.7's resume and backfill path, which is the safety net a lossy fan-out relies on.
- The isolation gauntlet's oracle, for SC-005.
