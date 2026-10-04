# Feature Specification: Chapter 4.20 — The messages that expire

**Feature Branch**: `066-chapter-4-20`

**Created**: 2026-10-03

**Status**: Draft

**Input**: User description: "chapter 4.20"

---

## Context — the premise was run first, and the chapter is the obstacle rather than the job

`docs/12` row 21 is *"The messages that expire — FR-MOD-06's retention job. Expired messages
take their media objects with them (FR-MED-11)."* Chapter 4.19 established the habit `docs/12`
§7.5 asked for, so the premise was run before this document was written.

| clause | measured |
|---|---|
| FR-MOD-06 — **configurable** retention per environment | **The column exists and nothing uses it.** `environments.retention_days` has been in `schema.ts` since chapter 2.1, with its own comment: *"DECLARED IN 2.1 AND STILL EMPTY. Named in SRS §6.1's Environment entity and SAD §338, read by nothing in seventeen chapters."* **0 of 33,051 environments have a value** |
| FR-MOD-06 — **by a scheduled job** | **No scheduler of any kind.** Zero `schedule:` triggers in `ci.yml`, no cron, no timer. ADR-28 is the precedent and this is the fourth clause bounded by the same absence, after FR-ANL-06, DR-17 and FR-MOD-03's retention year |
| FR-MOD-06 — **hard-deleted** | **REFUSED BY THE DATABASE, measured with a control.** See below |
| FR-MED-11 — expired messages delete their objects | **No referential integrity to lean on.** `media_objects` has **no foreign key to `messages`** — the link is a `media_id` inside the `messages.attachments` jsonb, so this is a lookup rather than a cascade |

### The hard delete is refused, and the thing refusing it shipped yesterday

Run inside a rolled-back transaction, with the control that tells an obstacle from a
coincidence:

```
DELETE FROM messages WHERE id = (a message WITH a version row)
  ERROR: update or delete on table "messages" violates foreign key constraint
         "message_edits_message_id_fkey" on table "message_edits"

DELETE FROM messages WHERE id = (a message with NO version row)
  DELETE 1
```

**Exactly one table references `messages` and it is `message_edits`, `NO ACTION`.** The
control deletes cleanly, so the foreign key is the only obstacle — not one of several.

**And chapter 4.19 made it bite on every deleted message.** Before that chapter only *edited*
messages had a version row; now every deletion writes one. 4.19 measured **4,565** messages
undeletable at its close and handed the number forward with the words *"row 22's erasure will
meet it"*.

**It is row 21 that meets it first, and the number is 5,495 today** — growing by one for every
deletion the platform performs.

### And the lane cannot exercise the clause at any of its four settings

```
oldest message on the lane     2026-09-14          19 days
messages older than  30 days   0
messages older than  90 days   0
messages older than 365 days   0
```

FR-MOD-06's shortest policy is 30 days and **nothing on this lane is 30 days old**. Every
demonstration in this chapter needs a backdated fixture, and the figure that matters — how much
a sweep deletes on real data — cannot be measured here at all.

---

## User Scenarios & Testing *(mandatory)*

The reader is Priya from `docs/03`'s Journey 3, and behind her the person who signed the
contract: a customer whose compliance team has promised that chat older than ninety days does
not exist.

### User Story 1 - A tenant's expired messages are actually gone (Priority: P1)

An operator sets an environment's retention to ninety days. Messages older than that are
destroyed — the row, not a tombstone — along with everything that would let somebody
reconstruct them.

**Why this priority**: it is the clause. FR-MOD-06 says *hard-deleted*, and the platform
currently cannot hard-delete a message at all on the commonest path.

**Independent Test**: backdate a message past the policy, run the sweep, and find the row gone
from `messages` and from every table that referenced it.

**Acceptance Scenarios**:

1. **Given** an environment with a 90-day policy and a message 91 days old, **When** the sweep
   runs, **Then** the message row no longer exists and neither does its edit history.
2. **Given** the same environment and a message 89 days old, **When** the sweep runs, **Then**
   the message is untouched.
3. **Given** an environment with **no** policy, **When** the sweep runs, **Then** nothing in
   that environment is deleted, at any age.
4. **Given** a message that was edited or deleted before expiry — and therefore has version
   rows — **When** the sweep runs, **Then** it is destroyed along with them rather than being
   refused, which is what the platform does today.
5. **Given** an expired message that was already a tombstone, **When** the sweep runs, **Then**
   the tombstone is destroyed too: a tombstone is a message that has expired like any other.
   *(**DR-06 said the opposite in as many words** — "Deleted messages shall retain their row;
   only `text` and `attachments` shall be cleared" — and this scenario names exactly the
   population that clause protected. Resolved at analysis pass 5 by **ADR-36 decision 1**: a
   retention sweep is a compliance path, so FR-MSG-08 and DR-06 are amended rather than this
   scenario narrowed.)*

### User Story 2 - The objects go with the messages (Priority: P2)

A message that expires takes its attachments with it. A customer who deletes chat does not keep
the photographs.

**Why this priority**: FR-MED-11 names it and it is the half with no referential integrity
behind it — an attachment is a `media_id` inside a jsonb column, so nothing in the database
will do this for us and nothing will notice if we get it wrong.

**Independent Test**: expire a message carrying an attachment, run the sweep, and find both the
database row and the stored bytes gone.

**Acceptance Scenarios**:

1. **Given** an expired message with an attachment referenced by no other message, **When** the
   sweep runs, **Then** the media object and its stored bytes are gone.
2. **Given** an expired message whose attachment is **also referenced by a message that has not
   expired**, **When** the sweep runs, **Then** the object survives — FR-MSG-11 has allowed the
   same id in two messages since chapter 3.24.
3. **Given** an object with a derived rendition (chapter 4.15), **When** its parent is swept,
   **Then** the rendition goes too, because its reachability is its parent's.

### User Story 3 - What runs it, and what happens when nothing does (Priority: P3)

A reader learns what this platform does and does not promise about *when* expiry happens, and
an operator can run the sweep deliberately.

**Why this priority**: the clause says *by a scheduled job* and this platform has no scheduler.
Pretending otherwise would put a compliance promise behind a mechanism that does not exist.

**Independent Test**: the chapter states who invokes the sweep, what the bound is, and what a
tenant is owed in the absence of one — with the same four-verdict treatment FR-MOD-03's
retention year got at chapter 4.18.

**Acceptance Scenarios**:

1. **Given** the shipped platform, **When** a reader asks when an expired message disappears,
   **Then** the answer names what invokes the sweep and does not imply a timer exists.
2. **Given** a sweep interrupted partway, **When** it is run again, **Then** it completes the
   work rather than double-deleting or skipping.

### Edge Cases

- **A message with version rows.** The common case after chapter 4.19, refused by
  `message_edits_message_id_fkey` today, and **the central obstacle of this chapter**. Whether
  the resolution is a cascade, an explicit ordered delete, or a change to the constraint is a
  decision this feature must take and record.
- **A policy changed from 365 to 30.** A large volume becomes expired at once. Whether the
  sweep is bounded per run, and what a half-finished sweep leaves, needs an answer.
- **A policy changed from 30 to indefinite.** Nothing is un-deleted. The chapter says so.
- **An attachment shared by an expired and a live message.** Covered by US2 scenario 2 and the
  reason FR-MED-11 cannot be a cascade.
- **An expired message in an archived channel, or one whose author was deleted.** Both rows
  survive their parents by design — **FR-CHN-10** (*"Archiving a channel shall preserve history
  and prevent new messages"*) and **FR-USR-05** (*"preserving their messages as authored by a
  deleted user"*). Expiry is about age, not reachability.
- **The audit log.** Chapter 4.18's entries name a `target_id` that may be an expired message.
  Whether a destroyed message leaves a dangling audit target is a question this chapter must
  answer rather than discover — `audit_log` has no foreign key to `messages`, so nothing will
  refuse it.
- **The analytical store.** Constitution III keeps ClickHouse independent; expiry of
  operational rows does not reach it, and DR-09's 90-day raw-event TTL is a different clock.
  The chapter states the boundary rather than widening its own scope.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: An environment MUST be able to carry a retention policy of 30, 90 or 365 days, or
  none, and the stored value MUST be readable back by the surface that set it.
- **FR-002**: A message older than its environment's policy MUST be destroyed rather than
  tombstoned — the row gone, not its text nulled.
- **FR-003**: Destruction MUST include every row that would let the message be reconstructed,
  specifically its version history, and MUST NOT be refused by a referential constraint.
- **FR-004**: An environment with no policy MUST lose nothing, at any age.
- **FR-005**: A message inside its environment's policy MUST be untouched, and the boundary MUST
  be tested on both sides of it.
- **FR-006**: An expired message's attachments MUST be destroyed with it — the database row and
  the stored bytes — unless the same object is referenced by a message that has not expired.
- **FR-007**: A derived rendition MUST be destroyed with its parent object.
- **FR-008**: The sweep MUST be re-runnable: interrupting it and running it again MUST complete
  the work without double-deleting or skipping.
- **FR-009**: The sweep MUST act only within the environment whose policy it is applying, and a
  tenant's policy MUST NOT be able to destroy another tenant's data by any parameter.
- **FR-010**: The platform MUST NOT imply that expiry happens on a timer it does not have. What
  invokes the sweep MUST be stated, and the absence of a scheduler recorded with the same
  treatment FR-MOD-03's retention year received.
- **FR-011**: The feature MUST NOT change the behaviour of sending, editing, deleting or reading
  a message. Any action whose answer or timing changes is recorded with the measurement.
- **FR-012**: Where measurement falsifies a published clause or document, the document MUST be
  amended rather than left to diverge.
- **FR-013**: Destroying a media object MUST publish the analytical store's `deleted` storage
  event, with a **negative** `bytesDelta`. The operational quota needs nothing — SRS 1.17 made
  committed bytes a `sum(declared_bytes)` over rows, so deleting the row corrects it. The
  analytical meter is event-sourced and does not self-correct: without this, chapter 4.16's
  reconciliation reports a tenant charged for bytes that no longer exist, permanently, and
  attributes the gap to reservations.
- **FR-014**: The policy route MUST carry a moderation classification, recorded with its
  reason, because `moderation-routes.ts` requires a decision for every mutating route a tenant
  can reach. If classified as moderation, setting a policy MUST write an `audit_log` entry —
  which obliges a fifth `target_kind`, since the column's CHECK constraint admits only `user`,
  `message`, `membership` and `channel`.

### Key Entities

- **A retention policy** — an integer on an environment, today unread by anything, whose four
  legal values FR-MOD-06 names.
- **An expired message** — a message whose age exceeds its environment's policy. Distinct from a
  deleted one: a tombstone is still a row, and an expired message is not.
- **A media object and its renditions** — reachable from a message only through a jsonb field,
  which is why FR-MED-11 cannot be delegated to the database.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A message past its environment's policy is gone from `messages` after the sweep,
  and so are its version rows — demonstrated against the constraint that refuses it today.
- **SC-002**: A message one day inside the policy survives the same sweep, asserted on both
  sides of the boundary.
- **SC-003**: An environment with no policy loses nothing, demonstrated by an absolute count
  before and after rather than by a delta.
- **SC-004**: An expired message's sole-referenced attachment is gone from the database and
  from the object store; a shared attachment survives.
- **SC-005**: Running the sweep twice produces the same end state as running it once, counted
  rather than inferred from a return value.
- **SC-006**: A sweep applying one tenant's policy destroys nothing belonging to another,
  measured against the cross-tenant suite.
- **SC-007**: What invokes the sweep is published, and the absence of a scheduler is recorded
  with a verdict rather than left implicit.
- **SC-008**: Every change outside tests and documents is listed and checked against the diff.
- **SC-009**: The CI error set after this chapter is compared per error against the set before
  it, in both directions, and the comparison is published.
- **SC-010**: `check:fences` reports zero and the tutorial builds, measured after the last edit
  to any file the chain publishes.
- **SC-011**: The chapter is between 2,000 and 4,000 prose words, counted outside fences and
  tables.
- **SC-012**: The number of messages a sweep would be refused on today is published, and
  re-measured at the close.
- **SC-013**: Destroying a media object publishes one `deleted` storage event with a negative
  `bytesDelta`, asserted by count and by sign rather than by the event's presence alone
  (FR-013).
- **SC-014**: Every mutating route a tenant can reach carries a moderation classification,
  which `moderation-routes.itest.ts` asserts in both directions from a booted application; the
  classification chosen for the policy route is recorded with its reason (FR-014).

---

## Assumptions

- **The chapter is row 21 of `docs/12` and it is chapter 4.20 by position**, not by that row's
  number. The numbering rule Part 3 taught: name a chapter by its movement and title. This is
  movement VII's third chapter, *"The messages that expire"*.
- **`environments.retention_days` is the column this feature uses.** It exists, it is empty, it
  is named in SRS §6.1 and SAD §338, and a second column would be a parallel policy. The
  surface that writes it is a decision for the plan.
- **The foreign key is the chapter's central problem and chapter 4.19 is why.** That chapter
  wrote the collision down and declined to pre-solve it, naming row 22. Row 21 arrives first,
  so this feature resolves it — and the resolution is inherited by erasure rather than
  duplicated there.
- **The scheduler is not built here.** ADR-28 declined to add one for FR-ANL-06, and three
  clauses now stand behind the same absence. A fourth does not change the architecture; what
  changes is that this clause's promise is a compliance promise, which is worth saying in the
  chapter rather than in a gap entry.
- **The lane cannot demonstrate the clause with real data** — nothing is 30 days old — so every
  scenario uses a backdated fixture, and the chapter publishes that limitation rather than
  implying the measurement is from production-shaped data.
- **Analytical rows are out of scope** by constitution III, and DR-09's 90-day TTL on raw events
  is a different clock with a different owner.

---

## Out of Scope

- **Building a scheduler.** Four clauses now want one. That is an architecture decision with its
  own ADR, not a line in a retention chapter.
- **FR-MOD-04's compliance erasure** (row 22). It shares this chapter's obstacle and has its own
  bound, receipt and population.
- **Retention of anything but messages and their media** — the audit log's year, the request
  log's TTL and the analytical store's are three different clocks owned by three other clauses.
- **A per-channel or per-user policy.** FR-MOD-06 says per environment.
- **Repairing `gaps.md` 058-3**, the malformed-path-parameter 500 — **twenty-two routes, not
  the sixteen that entry records**, re-measured at analysis pass 11. This chapter's route makes
  twenty-three and the repair stays out of scope; the corrected count is the deliverable.
