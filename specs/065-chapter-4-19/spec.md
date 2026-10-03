# Feature Specification: Chapter 4.19 — Everything, including what was deleted

**Feature Branch**: `065-chapter-4-19`

**Created**: 2026-10-03

**Status**: Draft

**Input**: User description: "chapter 4.19"

---

## Context — the premise was run first, and most of the chapter already exists

`docs/12` row 20 is *"Everything, including what was deleted — FR-MOD-01/02 via API key"*, and
the same document attaches a warning to it: **§7.5, "Check ch 20's premise before writing it.
FR-MOD-01/02 are P2, and chapter 3.23 built edit history and tombstones. Some of this chapter
may already exist."**

It was run against the composed platform before this specification was written. Most of it
does exist.

| clause | measured |
|---|---|
| **FR-MOD-02** — delete any message via API key, irrespective of author | **MET.** A tenant key deleted another user's message: **204**. Chapter 4.18 measured the same thing one chapter ago |
| **FR-MOD-01** — retrieve any channel's complete history, **including tombstones** | **MET in part.** The tombstone comes back in history, as a row with `text: null` |
| FR-MOD-01 — **and edit history** | **MET in part.** `GET …/messages/{id}/edits` returns each prior text with its instant, and it is **API-key only** — a user token gets **403**, which is the access decision the clause's *"via API key"* asks for |

So the chapter is not *build FR-MOD-01 and FR-MOD-02*. It is the hole the premise check found,
which is at the join between the two things that already work.

### The hole: you can recover every text a message ever had except the last one

Measured end to end. One message, two edits, then deleted by the key:

```
sent          "will be edited"
edit 1        "edited once"
edit 2        "edited twice"
DELETE        204, by the tenant key

GET …/edits   → "will be edited"   (prior text, edit 1)
              → "edited once"      (prior text, edit 2)

the row       text = <NULL>
message_edits 2 rows
```

**`"edited twice"` — the text the message held at the moment it was deleted — is in no
table.** An edit records the text it *replaced*; a deletion records nothing. A message deleted
after N edits leaves **N** recoverable texts out of the **N+1** that existed, and a message
deleted with no edits leaves **zero of one** — confirmed: `/edits` returns `{"edits": []}`.

FR-MOD-01 says *"complete history"*. Each of its two nouns is built. Their composition loses
exactly one version, every time, and nothing in the platform records that it did.

### Three smaller things the probe found, each measured

**`deleted_at` is absent from the history row.** The real-time `message.deleted` *frame*
carries it and the `message.deleted` *webhook* carries it, both read off the same row inside
the transaction; the history row does not. **The `DELETE` itself answers 204 with an empty
body and carries nothing** — this paragraph said it carried the instant until the seventh
analysis pass ran it. A client that was offline when a message was removed and catches up
through history learns that it is gone and not when:

```
seq=3  text=null  user=prem-b-…  created_at=2026-10-03T00:04:04.509Z  edited_at=null
```

**The history row and `messageSchema` are different shapes.** History serves `channel_id`
where the schema declares `channel`, carries `edited_at` which the schema does not, and
returns `text: null` against a schema that says `z.string()`. Nothing parses the history
response against that schema, so the divergence costs nothing today and is invisible to every
instrument.

**And a comment justifies a fallback with a row class the lane holds none of.**
`deleteMessage` explains its `?? toIso(row.createdAt)` with *"a system message with a null text
and no `deleted_at`, which has existed since chapter 2.1"*. Counted:

```
messages with text IS NULL                       4,861
  of those, deleted_at IS NOT NULL (tombstones)  4,861
  of those, deleted_at IS NULL                       0
messages that still have text                  176,157
```

So the ambiguity the fallback exists for has **zero instances** on this lane. The branch may
still be right — a lane is not production — but the sentence justifying it is a claim about
data, and the data disagrees.

---

## User Scenarios & Testing *(mandatory)*

The reader of this chapter is Priya, from `docs/03`'s Journey 3 — *"Priya never touches Relay
directly. She uses an internal support tool that Mai built on Relay's moderation APIs in an
afternoon."* Every scenario below is that tool holding an application credential.

### User Story 1 - What a message said when it was removed (Priority: P1)

A moderator removes a message. A week later somebody asks what it said. The support tool holds
the tenant's API key, the audit log says who removed it and when (chapter 4.18), the edit
history says every text the message held before its last edit — and the one text that matters,
the one that was on screen when the moderator acted, is gone.

**Why this priority**: it is the gap the premise check found, and it is the only part of
FR-MOD-01's *"complete history"* that the platform cannot currently serve. Everything else in
row 20's brief already works.

**And immutability is part of this story rather than beside it.** A recovered text that the
application can rewrite is not an answer to *what did it say* — it is a note. FR-MSG-07 has
asked for an immutable edit history since chapter 3.23 and nothing enforced it, so the
preservation and the enforcement ship together or the first is worth less than the clause
already claims. *(This arrived through `research.md` R5 and reached the plan, the data model,
the contract and five tasks before any requirement here mentioned it — which the second
analysis pass found by grepping this document for the word.)*

**Independent Test**: send a message, edit it twice, delete it with the API key, and ask for
its history. Every version it ever held comes back, including the last one.

**Acceptance Scenarios**:

1. **Given** a message edited twice and then deleted by an application credential, **When**
   the tool reads that message's history, **Then** three texts come back — the original, the
   first edit and the text at the moment of deletion — each with the instant it was replaced
   or removed.
2. **Given** a message deleted with no edits, **When** the tool reads its history, **Then**
   one text comes back: the only text it ever had.
3. **Given** a message that was never deleted, **When** the tool reads its versions, **Then**
   the prior texts come back and **the current text is not among them**, because it has not
   stopped being current — and the response the tool already has from the channel's history
   is where that text lives. The two sources are named rather than left to be worked out.
   *(An earlier draft of this scenario asked the version list to identify the current text as
   current. That would put a text that has not ended into a list of texts that have, and
   nothing in `contracts/message-versions.md` returns it — the scenario and the contract
   disagreed and the task list had silently resolved it in the contract's favour.)*
4. **Given** a message deleted twice (a retried call), **When** the tool reads its history,
   **Then** one removal is recorded, because the second deletion changed nothing.
5. **Given** any recovered version, **When** the application attempts to change or remove it,
   **Then** the attempt is refused at the storage layer and the version is unchanged — so the
   answer to *what did it say* is evidence rather than a note somebody could have edited.

### User Story 2 - When it was removed, from history alone (Priority: P2)

A tool that was not listening at the time catches up by reading history. It must be able to
tell a removed message from one that never had text, and say when the removal happened,
without a second request.

**Why this priority**: it is a one-field gap on a route that already serves the row, and it is
what makes a tombstone legible to a reader who arrives late. It is P2 rather than P1 because
the instant is recoverable today from the audit log by request id — at the cost of a join the
caller should not have to make.

**Independent Test**: delete a message, read the channel's history as a tool that never saw
the delete, and identify the removal and its instant from the response alone.

**Acceptance Scenarios**:

1. **Given** a deleted message, **When** the tool reads the channel's history, **Then** the
   row carries the instant of removal.
2. **Given** a message that was never deleted, **When** the tool reads the same history,
   **Then** the row carries no removal instant, and the two cases are distinguishable by a
   field rather than by the absence of text.

### User Story 3 - What "complete" does not include, named (Priority: P3)

A reader of the chapter, and of the clause, learns where the recoverable history stops and
why — rather than discovering the boundary when somebody asks a question it cannot answer.

**Why this priority**: it is the chapter's written product rather than its code, and it is
what stops the next chapter assuming more than this one delivers. Rows 21 and 22 both destroy
data and both will read this boundary.

**Independent Test**: the chapter states, with a measurement beside each, what a tenant can
recover about a removed message and what it cannot.

**Acceptance Scenarios**:

1. **Given** the shipped platform, **When** a reader asks what survives a deletion, **Then**
   the answer names the author, the sequence, the creation instant, every text version, the
   removal instant and the audit entry — and names what does not survive.
2. **Given** retention (row 21) and erasure (row 22), **When** a reader asks how long the
   recovered history lasts, **Then** the answer says which of those two removes it and that
   neither is built.

### Edge Cases

- **A message deleted before this chapter ships.** Its last text is already gone and no
  migration can recover it. The chapter cannot backfill and must say so. **4,862 messages are
  in that position on this lane**, of which 3,610 have nothing recoverable at all.
- **A message edited after a chapter-shipped version row exists, then edited again.** The
  version chain must stay ordered and must not duplicate the text that is still current.
- **An empty final text.** FR-MSG-01's minimum length makes `""` unsendable, so a recorded
  final version is never empty for that reason — but a system message with a null text is a
  different case and the lane holds zero of them today.
- **A message with attachments, deleted.** FR-MED-10 unlinks the attachments and the tombstone
  reports `attachments: []`. Whether a recovered version names what was attached is a decision
  this feature must take rather than inherit.
- **Erasure (row 22) against a recovered version.** A version row holds a user's words; erasure
  deletes a user's data. **The collision is TWO obstacles and the first is not the one the
  audit log has.** `message_edits_message_id_fkey` is `NO ACTION`, so deleting a message that
  has version rows is refused by the **foreign key**, before any trigger is consulted — run
  and confirmed: *"update or delete on table `messages` violates foreign key constraint"*. The
  append-only trigger is the second. The audit log has neither problem: its foreign key points
  at `environments` and nothing deletes those.

  **And this chapter makes the first one bite far more often.** Measured: **4,039 messages
  cannot be hard-deleted today and 7,649 after this chapter**, because every deletion now
  leaves a version row where only edited messages had one — 3,610 existing tombstones gain
  theirs, and the count grows by one for every deletion after that. Row 22 owns the problem;
  this chapter owns saying how much larger it made it.
- **A very long edit chain.** Nothing bounds the number of edits, so nothing bounds the number
  of version rows a single message can accumulate.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST preserve the text a message held at the moment it was deleted, so
  that the sequence of every text a message ever had is recoverable after deletion.
- **FR-002**: The preserved final text MUST be readable through the same surface that already
  serves prior texts, so that **a caller assembling a deleted message's history makes one
  request**. For a message that still exists it remains two — the versions from one route and
  the current text from the channel's history — because the current text has not ended and a
  list of ended versions is the wrong place for it.
- **FR-003**: Each recovered version MUST carry the instant at which it stopped being current,
  and the reason it stopped MUST be distinguishable between *replaced by an edit* and *removed
  by a deletion*.
- **FR-004**: A deletion that changes nothing MUST preserve nothing, so that a retried call
  does not record a second final version. This mirrors the rule chapter 4.18 applied to the
  audit log and the rule FR-009 of chapter 3.23 applied to the deletion itself.
- **FR-005**: The surface that serves recovered versions MUST remain application-credential
  only, as it is today — a user token receives 403.
- **FR-006**: A tenant MUST NOT be able to read any other tenant's recovered versions by any
  parameter.
- **FR-007**: A history row for a deleted message MUST carry the instant of removal, so that a
  caller reading history alone can tell a removal from a message that never had text and can
  say when it happened.
- **FR-008**: The feature MUST NOT change the behaviour of sending, editing or deleting a
  message, beyond the preservation FR-001 requires. Any action whose answer or timing changes
  is recorded with the measurement.

  **AND THE READ IS NAMED HERE RATHER THAN LEFT OUT OF IT.** Sending, editing and deleting are
  three verbs and the version list is a fourth surface, whose **content changes by design**: a
  deleted message's list gains an entry and every row gains two fields, so a caller counting
  `edits.length` sees a different number. That is additive and intended, it is the point of
  FR-001, and FR-008 would otherwise be a no-change clause that does not mention the one thing
  that changes.
- **FR-009**: The chapter MUST state what a tenant can and cannot recover about a removed
  message, with a measurement beside each claim, including the versions that are already
  unrecoverable because they predate this feature. **That population is two numbers, not
  one**: every tombstone lost the text it held at deletion — **4,862** on this lane — and
  **3,610** of those have no recoverable version at all, leaving **1,252** that kept their
  earlier texts and lost only the last. *(A single figure was the fourth of these until the
  sixth analysis pass re-derived them from the table; 3,610 alone understates the boundary by
  26% and contradicts this document's own N-of-N+1 arithmetic.)*
- **FR-010**: Where the shipped behaviour and a published document disagree, the document MUST
  be amended rather than left to diverge. Three disagreements are known in advance and are
  listed in Assumptions.
- **FR-011**: A recorded version MUST NOT be modifiable or removable by any path the platform
  exposes, and the refusal MUST be demonstrated rather than asserted — a probe that attempts
  the write and is refused. **FR-MSG-07 has said *"an immutable edit history"* since chapter
  3.23 and nothing enforced it**, which is a measurement rather than a reading: the table
  carries no trigger where `audit_log` has carried one since chapter 4.18.
- **FR-012**: The scope of FR-011's refusal MUST be published with the claim — what it refuses
  and what it does not — rather than left as the word *immutable*. The mechanism is the one
  ADR-35 already measured, and that ADR's own finding is that two ways around it remain.

### Key Entities

- **A message version** — one text a message held, the instant it stopped being current, and
  why it stopped. Today this exists for edits only, as a prior text with an instant, and not
  for the text at deletion.
- **A tombstone** — the surviving row of a deleted message: its author, sequence, creation
  instant and empty attachment list, with no text.
- **The audit entry** (chapter 4.18) — who removed it, when, and under which request. It
  records that a deletion happened and holds nothing about what was deleted, which is the
  division this feature does not change.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A message edited twice and then deleted yields three texts, in order, each with
  the instant it stopped being current — measured against the three-of-three the probe found
  to be two-of-three today.
- **SC-002**: A message deleted with no edits yields one text, where it yields zero today.
- **SC-003**: A history row for a deleted message carries the removal instant, and a row for a
  live message does not.
- **SC-004**: A second deletion of the same message adds no version, demonstrated by counting
  before and after rather than by reading the response.
- **SC-005**: A tenant asking for another tenant's message versions receives the answer it
  receives for a message that exists nowhere, with version rows present on both sides —
  measured against the cross-tenant attack that already covers this route.

  *(This read "sees its own and zero of a second tenant's, measured against a second
  environment that performed the same actions" until the first analysis pass. That sentence
  was carried over from chapter 4.18's audit log, which is a **list** route where another
  tenant's rows could appear in your page. This route returns **one message's** versions by
  id, so the only cross-tenant shape is a foreign id — and `gauntlet.itest.ts:242` already
  attacks it. As written the criterion could not have failed for its own reason.)*
- **SC-006**: A user token is refused the recovered-version surface with the code the platform
  already uses, asserted by code and not by status alone.
- **SC-007**: What a tenant can and cannot recover is published as a counted list, not an
  adjective, with the clause each item discharges.
- **SC-008**: Every change outside tests and documents is listed and checked against the diff
  rather than asserted (FR-008).
- **SC-009**: The CI error set after this chapter is compared per error against the set before
  it, in both directions, and the comparison is published.
- **SC-010**: `check:fences` reports zero and the tutorial builds, **measured after the last
  edit to any file the chain publishes** — which is the coverage config, in the final phase,
  not the chapter's own pages.
- **SC-011**: The chapter is between 2,000 and 4,000 prose words, counted outside fences and
  tables.
- **SC-012**: An attempt to modify and an attempt to remove a recorded version are both
  refused and the row survives both, demonstrated at the storage layer — and what the refusal
  does **not** cover is published beside the claim, measured rather than assumed to match the
  table chapter 4.18 made append-only.

---

## Assumptions

- **The chapter is row 20 of `docs/12` and it is chapter 4.19 by position, not by that row's
  number.** The numbering rule this project learned in Part 3 applies: name a chapter by its
  movement and title. This is movement VII's second chapter, *"Everything, including what was
  deleted"*.
- **Three documents are expected to need amendment**, because the premise check found them
  disagreeing with the platform:
  1. `deleteMessage`'s comment in `repository.ts` justifies a fallback with *"a system message
     with a null text and no `deleted_at`, which has existed since chapter 2.1"* — the lane
     holds **0** such rows against 4,861 tombstones.
  2. The history response and `messageSchema` are different shapes — `channel_id` against
     `channel`, an `edited_at` the schema does not declare, and a `text: null` against
     `z.string()`. Nothing parses one against the other, so this is a documentation question
     rather than a defect, and which document is wrong is the thing to decide.
  3. **FR-MOD-01 itself**, if the measurement shows *"complete history"* cannot mean what it
     says. Amending the clause is what this project does when measurement falsifies one.
- **FR-MOD-02 needs no work** and the chapter says so rather than re-deriving it. Chapter 4.18
  measured it met and this premise check measured it again: 204, another author's message, via
  the key.
- **The preserved final text is a new row in the existing edit-history table rather than a new
  table**, unless measurement says otherwise. The alternative — a column on `messages` — puts a
  version on the row it is a version of, which is the shape constitution IV refuses.
- **Nothing expires a recovered version.** Retention is row 21's and erasure is row 22's;
  neither is built, and the same absent scheduler bounds both (ADR-28). The chapter states the
  boundary and does not build a job.
- **`docs/07` §4 rule 2 is checked and is not this chapter's.** *"The journeys are the
  milestones — Parts 2, 4 and 5 each terminate in an executable journey (Tuan, Priya, Mai)."*
  Part 4's is Priya's and this chapter's reader is Priya, but the milestones are rows 9, 17
  and 22; row 20 adds to the surfaces that journey will use and does not terminate it. Rule 1
  and rule 3 are both this chapter's and both have tasks.
- **The probe's rows are left in place.** They are scoped to a channel this feature created in
  the seeded tenant, which is `fixtures.ts`'s standing convention — every row belongs to an
  environment the fixture minted, and a teardown reaching wider would be a global operation
  asserting a local fact.

---

## Out of Scope

- **FR-MOD-06's retention job** (row 21) and **FR-MOD-04's erasure** (row 22). This chapter
  writes the tension down where those chapters will find it.
- **Recovering versions that predate this feature.** A deletion before it ships destroyed the
  final text and no migration can recover it.
- **Repairing `gaps.md` 058-3 on this route.** A malformed path parameter answers **500
  `internal_error`** where an absent one answers 404 — measured here with a control, on the
  very route this chapter extends. Chapter 4.12 found it across sixteen routes and recorded it
  with its bill. Repairing this one would be cheap, because the controller is already in this
  chapter's fence bill, **and cheapness is the wrong test**: one validating route among sixteen
  that do not makes the remaining fifteen harder to sweep. Carried, with the measurement this
  chapter added to it.
- **Recording who read a message's history.** A log of reads is a different clause and a much
  larger table; chapter 4.18 took the same position for the audit log.
- **Changing what the real-time `message.deleted` frame carries.** It already carries
  `deleted_at`; the gap is in the REST history row.
- **A second implementation of `messageSchema`.** If the history shape and the frame shape
  should converge, that is a decision this chapter records and does not act on unilaterally —
  chapter 4.14 measured what making a field required costs across construction sites.
