# Feature Specification: Chapter 3.23 — editing and deleting a message

**Feature Branch**: `041-chapter-3-23`
**Created**: 2026-09-03
**Status**: Draft
**Input**: User description: "chapter 3.23"

FR-RTM-05 names six real-time event kinds. Five have producers. `message.updated` and
`message.deleted` have been in the published protocol since chapter 1.3 with **nothing that
emits them**, because there is no route to edit a message and no route to delete one.

**Most of this design is already written in the tree, and finding that out came first.**
Chapter 3.22's hand-off asked whether an edit and a deletion are one event kind or two;
`frames.ts` has answered *two* since chapter 1.3, both carrying a `messageSchema` payload.
The columns exist — `messages.edited_at`, `messages.deleted_at`, a nullable `text`, an
`attachments` column. `docs/05-sad.md:342` publishes the deletion as
`UPDATE message SET text=NULL, attachments=NULL, deleted_at=now()`, and `:435` publishes a
`message_edits` table with `prior_text TEXT NOT NULL`. `schema.ts:26` names `message_edits`
as a deliberate absence with an arrival date: *"the edit chapter"*, which is this one.

**What is not decided is how a tombstone crosses the wire.** `messageSchema.text` is
`z.string()`. A `message.deleted` frame's payload is a `messageSchema`. **A tombstone has no
text, so the frame the platform has been waiting for cannot express the thing it is for.**
Two places in the running code already say so in their own comments —
`messages.controller.ts:194` refuses to publish a recovered tombstone because *"`messageSchema.text`
is `z.string()`, not nullable"*, and `backfill.controller.ts:83` drops a tombstone from a
resume because *"a tombstone is not a creation… when deletes arrive they get
`message.deleted`"*.

**And four behaviours across four read paths already disagree about tombstones**, each
deliberately, none of them wrong today because no writer exists. Three were visible from the
start; the fourth — the backfill's truncation arithmetic — was found by this feature's own
research, which is why the requirement that documents them insists on being derived from the
code rather than from a list:

| Read path | What it does with a null text | Since |
|---|---|---|
| REST history (`GET …/messages`) | passes the row through unchanged | never filtered |
| Internal backfill (resume) | drops the row; the sequence gap is the signal | chapter 2.6 |
| Channel listing preview | reports it with a null text and still counts it | chapter 3.15 |
| Backfill truncation flag | computed from rows **read**, not frames delivered | chapter 2.6 |

## User Scenarios & Testing *(mandatory)*

### User Story 1 - An author corrects what they said (Priority: P1)

Tuan sends a message with a typo. He edits it. Everyone looking at the channel sees the
corrected text without the conversation re-ordering around it, and the record of what he
originally said is kept.

**Why this priority**: FR-MSG-07, and it is the half that gives `message.updated` its first
producer. An edit is the cheaper of the two to reason about because the row keeps its text.

**Independent Test**: Send a message, edit it through the API, and assert that a second
connected member receives `message.updated` carrying the new text and the original sequence
number, and that the prior text is readable through the edit-history route with a tenant API
key.

**Acceptance Scenarios**:

1. **Given** a message Tuan sent, **When** Tuan edits its text, **Then** the message keeps
   its sequence number and its creation timestamp, and records when it was edited.
2. **Given** two members connected to the channel, **When** the message is edited, **Then**
   both receive `message.updated` exactly once.
3. **Given** a message edited three times, **When** its edit history is read with a tenant
   API key, **Then** all three prior texts are present with their timestamps, oldest first,
   and none has been overwritten.
3a. **Given** the same message, **When** an end user reads that route — including its author —
   **Then** the read is refused.
4. **Given** an edit, **When** the channel listing is read, **Then** the channel's position
   in the listing is unchanged by the edit alone.

### User Story 2 - A message is deleted and the conversation keeps its shape (Priority: P1)

Priya deletes a message. Everyone sees it disappear as content while the conversation keeps
its ordering: the message's place in the sequence is still there, and no client is left with
a hole it cannot explain.

**Why this priority**: FR-MSG-08 and FR-MSG-10 together, and it is where the chapter's one
real design decision lives.

**Independent Test**: Delete a message and assert that a connected member receives
`message.deleted`, that the row survives with its sequence number and author, and that the
REST history for that channel still returns the message's position.

**Acceptance Scenarios**:

1. **Given** a message, **When** it is deleted, **Then** its text and attachments are gone,
   its sequence number, author and creation timestamp remain, and the deletion is recorded.
2. **Given** a connected member, **When** a message is deleted, **Then** they receive
   `message.deleted` identifying the message.
3. **Given** a deleted message, **When** the channel history is read, **Then** the deleted
   message appears in its original position with no text.
4. **Given** a deleted message, **When** it is deleted again, **Then** the second deletion
   changes nothing and does not emit a second event.
5. **Given** a deleted message, **When** an edit is attempted on it, **Then** the edit is
   refused.

### User Story 3 - A moderator removes somebody else's message (Priority: P2)

A support operator removes a message they did not write, using a tenant credential rather
than acting as any person.

**Why this priority**: FR-MOD-02 says the system shall permit deleting any message via API
key irrespective of author. It is a different authorisation path, not a different behaviour.

**Independent Test**: Delete a message authored by one user using an API key that acts as no
user, and assert the same tombstone and the same event.

**Acceptance Scenarios**:

1. **Given** a message authored by Tuan, **When** it is deleted with a tenant API key,
   **Then** the deletion succeeds and produces the same tombstone as an author's deletion.
2. **Given** a message authored by Tuan, **When** another end user attempts to delete it,
   **Then** the attempt is refused.
3. **Given** a message in another tenant's channel, **When** deletion is attempted, **Then**
   the message is not found.

### User Story 4 - A client that was away learns what changed (Priority: P2)

A client disconnects, an edit and a deletion happen while it is away, and it reconnects with
a cursor. What it can and cannot learn is stated rather than discovered.

**Why this priority**: FR-RTM-03's resume contract is what makes the lossy real-time fabric
acceptable (ADR-07), and an edit below a client's cursor is invisible to a cursor. Chapter
3.20 met the same shape with revocations, which have no cursor either, and answered it with
a periodic re-read rather than by pretending the fabric was reliable.

**Independent Test**: Connect, disconnect, edit and delete two messages below the cursor,
reconnect, and assert what arrives and what does not — then assert that the documented
repair produces the truth.

**Acceptance Scenarios**:

1. **Given** a client resuming from a cursor, **When** a message **newer** than that cursor
   was edited while it was away, **Then** the replay carries the current text, because the
   replay is read from current state rather than from a log of what happened.
2. **Given** a client resuming from a cursor, **When** a message **newer** than that cursor
   was deleted while it was away, **Then** the replay does not present the deleted content.
3. **Given** a client resuming from a cursor, **When** a message **older** than that cursor
   was edited while it was away, **Then** nothing is replayed for it and no sequence gap
   appears — the client keeps its stale copy until it re-reads.
4. **Given** that client, **When** it re-reads that range of history, **Then** it sees the
   current text and the tombstone, and its view matches a client that never disconnected.

### Edge Cases

- **An edit that sets the text to what it already was is an edit.** It records an edit time,
  appends a history row and emits an event, because the platform does not compare texts. The
  alternative needs a definition of equality — trailing whitespace, Unicode normalisation,
  an emoji shortcode that resolves to the same glyph — and every answer to that is a decision
  a customer would have to be told about. Slack treats an identical edit as an edit for the
  same reason. Decided here rather than left as a question.
- Editing or deleting a message that is already a tombstone.
- A deletion of the newest message in a channel, which is the row the channel listing shows
  as its preview and counts as unread.
- A message with attachments: the deletion removes them, and any hosted media they referenced
  outlives the row.
- A message with no sender at all — 121,250 of them exist in the lane, and every one predates
  chapter 3.17's sender rule. Editing or deleting one has no author to authorise against.
- An edit arriving while the same message is being deleted.
- A tombstone reached through the channel listing's preview, which reports it with a null
  text and still counts it as one unread.
- The edit history of a message whose channel is later archived, or whose author is later
  deleted — the row survives both.
- A backfill page whose 500-message limit is filled partly by tombstones.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST allow the author of a message to change its text.
- **FR-002**: An edit MUST preserve the message's sequence number, its channel, its author
  and its creation timestamp.
- **FR-003**: An edit MUST record when it happened, distinguishably from when the message was
  created.
- **FR-004**: Every edit MUST append the superseded text to an immutable history with its own
  timestamp. History entries MUST NOT be updated or removed by any later edit.
- **FR-005**: An edit MUST be announced to every connected member of the channel as
  `message.updated`, once per connection.
- **FR-006**: The system MUST allow a message to be deleted, replacing its text and its
  attachments with nothing while retaining its sequence number, author, creation timestamp,
  and the deletion's own metadata.
- **FR-006a**: The deletion's metadata MUST record **who performed it** as well as when.
  FR-MSG-08 itemises *"sequence number, author, timestamps, and deletion metadata"* — with
  timestamps listed separately, so a timestamp alone cannot be what the last item means. And
  a tenant API key may delete any message (FR-012), so the author the tombstone keeps is the
  person who wrote it, not the one who removed it.
- **FR-007**: A deletion MUST be announced to every connected member of the channel as
  `message.deleted`, once per connection.
- **FR-008**: The deletion event MUST identify the message, its channel, its position in the
  channel's ordering, its author and when it was deleted. It MUST NOT carry a text field,
  because a deleted message has no text and an empty one would be indistinguishable from a
  message somebody sent blank.
- **FR-008a**: The message payload used by creation and edit events MUST be left unchanged.
  It has been published since chapter 1.3 and is parsed by every client in the series; a
  deletion is the one event that does not carry a message, and it is the event that changes
  rather than the contract twenty-two chapters rely on.
- **FR-009**: Deleting an already-deleted message MUST succeed without changing the row and
  without emitting a second event.
- **FR-010**: Editing a deleted message MUST be refused.
- **FR-011**: History responses MUST include deleted messages in their original position, so
  a reader sees no gap in the ordering.
- **FR-012**: A tenant API key MUST be permitted to delete any message in its environment
  irrespective of author.
- **FR-013**: An end user MUST NOT be permitted to edit or delete a message they did not
  author.
- **FR-013a**: A tenant API key MUST NOT be permitted to edit a message. FR-MOD-02 grants it
  deletion of any message and is silent on editing; silence is read as absence of permission.
  Removing somebody's words and rewriting them **as them** are different acts, and only the
  second leaves a message saying something its author never wrote with nothing on the wire to
  say so.
- **FR-014**: A message in another tenant's environment MUST be indistinguishable from one
  that does not exist.
- **FR-015**: Neither an edit nor a deletion MUST change a channel's position in the activity
  ordering by itself.
- **FR-016**: A resuming client MUST NOT be sent the superseded text of a message that was
  edited while it was disconnected. Replay is read from current state, so a message newer
  than the cursor carries its current text and its deletion if it has one.
- **FR-016a**: Resume MUST stay ordered by the channel sequence alone. A message older than
  the client's cursor that was edited or deleted during the absence MUST NOT be replayed, and
  the client's stale copy MUST be repairable by re-reading that range of history.
- **FR-016b**: The limit in FR-016a MUST be documented as a property of a cursor rather than
  left to be discovered — including the fact that it produces no sequence gap and therefore
  trips no existing client-side detector.
- **FR-017**: The behaviour of **every** read path with respect to tombstones MUST be stated
  in one place and MUST agree with what the code does. There are four behaviours across four
  paths, and the fourth was found by this feature's own research rather than listed at the
  start: history passes a tombstone through, resume drops it, the channel listing reports it
  with a null text and still counts it, and **the backfill's truncation flag is computed from
  rows read rather than frames delivered** — so a tombstone-heavy page returns fewer frames
  and still reports itself truncated.
- **FR-017a**: The statement required by FR-017 MUST be derived from the code at the time it
  is written rather than from an earlier list. This requirement counted three paths until the
  fourth was measured.
- **FR-018**: An edit or deletion MUST be refused for a message whose author cannot be
  established, rather than applied without an authorisation check.
- **FR-019**: An edit MUST be emitted to subscribed webhook endpoints as `message.updated`,
  and a deletion as `message.deleted`, spelled as FR-WHK-02 spells them because a customer's
  subscription filters on those exact strings.
- **FR-020**: The deletion webhook event MUST NOT carry the message's text, for the same
  reason the real-time frame does not.
- **FR-023**: A message's edit history MUST be readable, oldest entry first, by a tenant API
  key. FR-MOD-01 requires exactly this audience — *"retrieving any channel's complete history,
  including tombstones and edit history, via API key"* — and nothing in the SRS asks for an
  end user to read it, so nothing here invents that.
- **FR-023a**: The edit-history read MUST be refused to an end user, including the message's
  own author. The published surface says a message was edited; what it used to say is a
  moderation surface.
- **FR-021**: An edit whose text equals the current text MUST be treated as an edit — an edit
  time, a history row and an event — rather than detected and skipped. The system MUST NOT
  compare message texts to decide whether an edit happened.
- **FR-022**: A refusal because the caller did not write the message MUST carry a code of its
  own rather than the generic permission refusal. **Authorship is a fact about the message,
  not a permission on the caller**, so the generic code's stated remedy — a change of
  credential or of permission — is advice no credential can act on.

### Key Entities

- **Message**: gains a recorded edit time and a recorded deletion time. Its sequence number
  is fixed at creation and is never reassigned by either operation.
- **Edit history entry**: one per edit, holding the text that was superseded and when. Append
  only. Belongs to exactly one message.
- **Tombstone**: not a separate entity — a message whose text and attachments are gone and
  whose deletion time is set. It keeps its identity, its place and its author.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: An author can correct a message and every other member watching the channel
  sees the correction without reloading.
- **SC-002**: After three edits, an operator can retrieve all three superseded texts in
  order, through a documented route rather than through the database.
- **SC-002a**: An end user cannot retrieve what a message used to say.
- **SC-003**: A deleted message leaves no gap: a reader paging through the channel's history
  sees an unbroken run of positions.
- **SC-004**: A deletion removes the content from every path a reader can reach it by, in the
  same request that performs it.
- **SC-005**: An operator can remove any message in their environment without acting as a
  person.
- **SC-006**: A client that was disconnected across an edit and a deletion, and follows the
  documented repair, ends with the same view as a client that stayed connected.
- **SC-006a**: The one case the repair is needed for — a change to a message older than the
  client's cursor — is stated in the published documents, including the fact that it leaves
  no sequence gap to detect.
- **SC-007**: Repeating a deletion produces no additional events and no additional history.
- **SC-008**: FR-RTM-05's six event kinds all have producers, with none of the six emitted by
  nothing.
- **SC-009**: Every read path's tombstone behaviour is documented — four of them — and each
  documented claim is checked against the code rather than asserted.
- **SC-010**: The full integration lane's mean stays inside its 240-second budget.
- **SC-011**: A customer subscribed to message events is told about an edit and a deletion,
  not only about a creation — which is what FR-WHK-02 has asked for since the first draft.

## Clarifications

Three decisions, taken because the tree did not already contain them. The other four this
chapter needed were read out of the repository rather than decided.

### The deletion event carries no text, and the message payload is untouched

`messageSchema.text` is `z.string()`, and two places in the running code already refuse to
publish a tombstone through it and say why. Widening that field would make `text: null` legal
on a creation too — where the send path deliberately refuses it — and would edit a contract
published since chapter 1.3. So the deletion event gets a payload of its own: identity,
position, author, and when. **The event that has no message is the one that stops carrying
one.**

### Resume stays ordered by the sequence alone, and history is the repair

**This is what Slack does**, and Relay is already standing where Slack stands. Slack's Events
API and Socket Mode deliver `message_changed` and `message_deleted` as events and do not
replay them to a client that was offline; the documented recovery is to re-read a range
through `conversations.history`, which returns the *current* state of those messages rather
than a log of what happened to them. Discord is the same shape with a bounded per-session
replay buffer in front of it.

The two alternatives were both considered and both rejected here:

- **Matrix never mutates.** An edit is a new event and a redaction is a new event, so a
  client syncing from a token gets them for free and the problem does not exist. Relay cannot
  reach that cheaply: FR-MSG-07 keeps a message's sequence number across an edit, so an edit
  appends nothing a cursor could find. Making edits appends would mean a second ordering,
  which is a larger change than the alternative below rather than a smaller one.
- **IMAP added a modification sequence.** CONDSTORE/QRESYNC increments a `MODSEQ` on any
  change, including to old messages, and a client resyncs on "everything changed since X".
  That is a second dimension beside the sequence cursor, with its own page-size question,
  and FR-RTM-03 describes no such thing.

**What makes the Slack answer cheap here is not this chapter's work.** The REST history
endpoint already passes a null text and an edited text straight through — it has never
filtered them — so the repair path exists and is tested before the writer that needs it does.
The cost is stated rather than hidden: a client holding a message older than its cursor can
be stale indefinitely, and because the row keeps its sequence number this produces **no gap**
and trips no existing client-side detector.

### The edit history needed a read surface, and three sentences already assumed one

The first draft asserted retrievability in three places — a success criterion, an acceptance
scenario and a story's independent test — and specified no route. FR-004 said only that the
history is appended and immutable, which is a statement about writing.

**The audience is FR-MOD-01's, not an invention.** That clause names an API key retrieving a
channel's complete history *including edit history*, and nothing in the SRS asks for an end
user to read what a message used to say. So the route is moderation-scoped, and this chapter
closes the per-message half of FR-MOD-01 while the channel-level "complete history" stays
that clause's own chapter.

**Found in analysis pass 5 by reading the clause rather than the identifier**, which is this
project's second-highest-yield mechanism and the one that found three of chapter 3.17's most
expensive defects.

### Webhooks were a third surface, added after the spec was first written

Planning research found that FR-WHK-02 names eight event types, that the platform emits
three, and that two of the missing five are **this chapter's two**. The spec's first draft
covered the REST routes and the real-time frames and missed the event spine entirely.

Chapter 3.20 set the precedent: it created `channel.member_added` and
`channel.member_removed` and emitted their webhooks in the same chapter rather than leaving
them to a later one. Following it costs two entries in an array that already exists to be
counted, and not following it would ship an event kind that half the platform knows about.

**Recorded here rather than folded in silently**, because a spec that grows during planning
should say where the growth came from.

### The non-author refusal gets its own error code

The generic 403 exists and its published entry says what it is for: *"The generic case: where
a more specific code exists … that one is sent instead"*, with the remedy *"nothing the client
can retry. This is a change of credential or of permission."*

**Neither half of that fits.** No credential grants authorship, and no permission change makes
a message yours. `codes.ts` argues against reusing the generic code twice in its own comments,
both times on the ground that *"the response has to say what actually happened"* — and "you
did not write this" is a different fact from "you lack a permission".

So both routes' non-author refusal carries one new code. **One, not two**: an end user who is
not the author and a tenant API key attempting an edit have the same cause — the caller is not
the author — and the same remedy. A tenant key can still delete anything, which is a different
route and not a refusal.

**Left undecided, the default was the generic code**, because the error filter maps a bare 403
to it. That is how a protocol decision gets made by omission.

### A tenant API key may delete any message and may edit none

FR-MOD-02 grants deletion irrespective of author and says nothing about editing. Silence is
read as absence of permission. An operator can remove what somebody said; nobody but the
author can change what it says.

## Assumptions

- **The two frame kinds stay two.** `message.updated` and `message.deleted` are published and
  parsed by twenty-two chapters of clients; this chapter gives them producers rather than
  reconsidering their existence.
- **The deletion is the SAD's published shape plus one field it does not publish.** Text and
  attachments cleared and the row kept are `docs/05-sad.md:342`'s own sequence diagram and its
  DDL. **The deletion's actor is not**: `metadata JSONB NOT NULL DEFAULT '{}'` is declared on
  three tables in that DDL and its contents are documented for none of them, so this chapter
  amends the document rather than following it. FR-006a says why — FR-MSG-08 itemises
  timestamps and deletion metadata separately, so the last item has to mean more than a
  timestamp.
- **`message_edits` arrives as the SAD's DDL describes it**, since `schema.ts` records it as
  a deliberate absence awaiting this chapter.
- **Hard deletion stays out of scope.** FR-MSG-08's second sentence sends it to the
  compliance endpoint, which is FR-MOD-04's, and that is a different chapter.
- **Retention and scheduled hard-deletes are out of scope** (FR-MOD-06).
- **The moderation audit log is out of scope** (FR-MOD-03), and this chapter does not claim
  it. A deletion by API key is permitted here and audited later.
- **Attachments are cleared rather than reclaimed.** Hosted media outliving a deleted message
  is FR-MED's problem and this chapter states the consequence rather than solving it.
- **The edit is text-only.** Changing a message's attachments is not an edit for FR-MSG-07's
  purposes, and nothing in the SRS asks for it.

## Out of scope

- Hard deletion of any kind, and the compliance erasure endpoint (FR-MOD-04).
- The moderation audit log (FR-MOD-03).
- Message retention policy and its scheduled job (FR-MOD-06).
- Reclaiming hosted media referenced by a deleted message.
- Editing attachments, reactions, or anything other than a message's text.
- Any change to how sequence numbers are assigned.
