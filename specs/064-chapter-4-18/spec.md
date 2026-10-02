# Feature Specification: Chapter 4.18 — The log that cannot be edited

**Feature Branch**: `064-chapter-4-18`

**Created**: 2026-10-02

**Status**: Draft

**Input**: User description: "chapter 4.18"

---

## Context

Chapter 4.18 is row 19 of `docs/12-part-4-structure.md` and the first chapter of **movement
VII, "The reckoning"**. Its line reads:

> FR-MOD-03's audit log. **First in its movement, not last** — everything after it writes to
> it. Registry-shaped, the same shape as *Errors that resolve*, which 045 moved to the front
> of Part 3 for this reason.

The clause it builds:

> **FR-MOD-03.** Every moderation action shall be recorded in an immutable audit log with
> actor, action, target, timestamp, and request ID, retained for 1 year.

A premise check before this spec was written, against the tree rather than against the plan.

| the thing that looks like it already does this | what it actually holds |
|---|---|
| an `audit_log` table | **does not exist.** `docs/05-sad.md` says so in as many words, and names chapter 3.23's `gaps.md` item 2 as where the boundary was written down |
| `messages.metadata.deleted_by` | the actor's **kind**, and their external id when there is one. One mutable column on the row it describes: no request id, not appendable, and silent about actions that leave no row |
| the request log (chapter 4.8) | `environment_id · ts · request_id · endpoint · method · status · latency_ms · principal_kind · refused_at · limited_operation` |

**THE REQUEST LOG HAS THREE OF FR-MOD-03's FIVE FIELDS AND CONTRADICTS TWO OF ITS THREE
QUALIFIERS.** It carries the timestamp and the request id, and the action only as a route
template. It has **no actor** — `principal_kind` says `application` or `user`, never which
key or which person — and **no target**, because the user id, message id and channel id live
in the path and the path is never stored. Against the qualifiers: its engine is
`ReplacingMergeTree`, where a row with the same sort key replaces an earlier one, and its
`TTL` is **30 days** against the clause's year. It is a good instrument for the question
chapter 4.8 asked and it is not this one.

**AND A BAN FOLLOWED BY AN UNBAN LEAVES NO TRACE ANYWHERE.** `POST /v1/users/{id}/ban` sets
`banned_at` to the current instant and `DELETE /v1/users/{id}/ban` sets it back to `NULL`, so
a user who was banned and reinstated has a row byte-identical to one that was never banned.
The current state is stored; the history is not. That is the gap an audit log is for, and it
is the clearest single demonstration this chapter has.

**THE LOG HAS A WRITER ON DAY ONE, WHICH IS WHAT KEEPS IT OUT OF 4.6's SHAPE.** The structural
argument for putting this chapter first in its movement — *everything after it writes to it* —
describes a store whose writers arrive later, and this project has twice shipped one of those:
chapter 4.6's rollup over a table with no producer, and chapter 4.16's column with one writer
and no reader. The difference here is measurable rather than hoped for. **FR-MOD-02 is already
met**: `deleteMessage` skips the authorship comparison when the principal carries no user, so
an application credential can already delete any message irrespective of author. The ban pair
is already built and is application-credential-only. Both are moderation actions under any
reading of the clause, and both ship before this chapter opens.

**AND THE TWO HARD FIELDS ARE ALREADY IN HAND.** `ApplicationPrincipal` carries `keyId`,
`UserPrincipal` carries `userExternalId`, and the request object carries `requestId`. The
clause is buildable because chapter 3.2's credential work resolved an actor and chapter 3.8's
request handling resolved an id; nothing in FR-MOD-03's field list needs inventing.

**WHAT THE CLAUSE DOES NOT DEFINE IS THE SET.** *"Every moderation action"* names a population
and gives no membership rule, and the platform has **nine** mutating routes a tenant can reach
that a reasonable reader might include: ban, unban, delete a user, delete another author's
message, edit another author's message, remove a member, change a member's role, archive a
channel, unarchive a channel. Deciding which are in, in writing, with the reason, is this
chapter's main product. It is the same shape as FR-ANL-06's *"counts derived from operational
data"* at chapter 4.7 and FR-MED-09's *"renders as"* at 4.17: the clause's own words are the
work.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — A moderation action leaves a record nothing can change (Priority: P1)

A customer's support tool, acting with an application credential, bans an end user. Later it
lifts the ban. Later still, somebody asks who did that and when.

Today the answer is unavailable: the user's row says only that they are not currently banned.
After this chapter, both actions are entries in an append-only log, each naming the actor, the
action, the target, the instant and the request that caused it, and neither entry can be
altered or removed by any path the platform exposes.

**Why this priority**: it is the clause, and it is the one story that cannot be told at all
today. Every other story in this feature assumes an entry exists to read.

**Independent test**: ban a user and lift the ban, then read the log back and find two entries
with the right actor, target and order. Attempt to modify or delete an entry through every
path the platform offers and find none that succeeds.

---

### User Story 2 — An investigator reads a tenant's moderation history (Priority: P2)

Priya is reconstructing what happened in a channel. She has the request log, which tells her
that a `DELETE` was issued and answered 204, and she needs to know **which message** and **on
whose authority**. She reads the tenant's audit entries, filters to the window, and sees the
actions in order with their targets.

**Why this priority**: a log nobody can read is the defect chapter 4.6 recorded and chapter
4.16 recorded again. The read path is what makes the write path worth having, and the
milestone that closes this movement — *the Priya test*, row 23 — ends in an audit step that
needs it.

**Independent test**: perform a mixed sequence of moderation actions against one environment
and a second sequence against another, then read as the first tenant and find exactly the
first sequence, in order, with no entry of the second visible by any filter.

---

### User Story 3 — The actions that are not recorded are named, not forgotten (Priority: P3)

A reader of the chapter wants to know what the log does not cover. They find a list: which of
the platform's mutating routes are moderation actions, which are not, and why — and, for the
clause's qualifiers that this chapter cannot discharge, a statement of which and the reason.

**Why this priority**: *"every moderation action"* is unfalsifiable until the set is written
down. A chapter that records some actions and describes itself as satisfying the clause is one
nobody can check, and a later chapter adding a tenth route has no way to know whether it owes
an entry.

**Independent test**: the published set is derived from the running router rather than
hand-listed, and a route added without a decision about it makes a check fail.

---

### Edge Cases

- **An action that fails.** A ban that is refused with 403, or one whose target does not
  exist. The attempt was made; whether a refusal is a moderation action is a decision this
  chapter must take and state.
- **An action that changes nothing.** Banning an already-banned user updates no row, by the
  same `isNull(banned_at)` guard that makes a re-ban idempotent. One request, no state change
  — and chapter 4.17's quickstart found the api answering 422 for the analogous media case.
- **An action that is partly done when the request fails.** If the entry and the action are
  not written together, there is a window in which one exists and the other does not, in
  either direction. Which direction is acceptable is a decision with a reason.
- **An end user acting within their own rights.** Deleting one's own message is permitted by
  FR-013 of chapter 3.23 and is not moderation. The same route, the same verb, a different
  principal.
- **A platform principal.** The dispatcher and gateway call the api on the internal seam with
  `environmentId: undefined` by design (chapter 4.4). An internal caller is neither a tenant
  nor a user, and the clause's "actor" has no value for it.
- **An entry whose target no longer exists.** Erasure (FR-MOD-04, row 22) deletes a user's
  data. An audit entry naming that user is a record of an action, not the user's data — and
  the two clauses point in opposite directions.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The platform MUST record an entry for every action in the published moderation
  set, carrying actor, action, target, timestamp and request id.
- **FR-002**: The moderation set MUST be published as an explicit list with a reason for each
  inclusion and each exclusion, covering every mutating route a tenant credential can reach.
- **FR-003**: The set MUST be derived from the running router rather than maintained by hand,
  so that a route added later without a decision about it fails a check rather than passing
  silently.
- **FR-004**: An entry MUST NOT be modifiable or removable by any path the platform exposes,
  and the refusal MUST be demonstrated rather than asserted — a probe that attempts the
  modification and is refused.
- **FR-005**: An entry MUST be written as part of the action it records, so that an action
  that succeeded with no entry, or an entry with no action, is not reachable.
- **FR-006**: A tenant MUST be able to read its own entries, ordered, filtered by a time
  window, and MUST NOT be able to read any other tenant's.
- **FR-007**: The actor MUST identify the credential or user that acted. Where the platform
  cannot identify a person — an application credential names a key, not its holder — the
  limit MUST be stated in the clause record rather than left for a reader to discover.
- **FR-008**: Where an action is refused, or changes no state, the chapter MUST state whether
  an entry is written and why, and the behaviour MUST match the statement.
- **FR-009**: Recording an entry MUST NOT depend on any path that is permitted to lose or
  delay a record. An outage or backlog anywhere outside the action's own write MUST NOT cause
  a moderation action to go unrecorded.
- **FR-010**: Where FR-MOD-03's retention of 1 year cannot be enforced by anything this
  chapter builds, the clause MUST be amended to say so, naming what would enforce it.
- **FR-011**: The chapter MUST state that the log begins now — entries do not exist for
  actions taken before it shipped — and MUST NOT present a reader with a view that implies
  otherwise.
- **FR-012**: This feature MUST NOT change the behaviour of any moderation action it records.
  Where recording an action would require changing it, the requirement is recorded with its
  cost rather than satisfied.
- **FR-013**: The chapter MUST publish what the development lane cannot demonstrate about the
  log, as a list rather than as a qualifier.

### Key Entities

- **Audit entry**: one moderation action that happened. Carries who acted, what they did, what
  they did it to, when, and the request that caused it. Written once and never again.
- **Moderation set**: the published list of actions that owe an entry, with the reason for each
  decision, derived from the routes the platform actually serves.
- **Actor**: the credential or user that performed the action. An application credential
  identifies a key; a user token identifies a user; an internal caller is neither.
- **Target**: the thing acted upon — a user, a message, a membership, a channel — identified
  well enough that a reader can find it a year later.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A ban and its reversal produce two entries that name the actor, the target and
  the order, where today the two actions together leave the stored state indistinguishable
  from a user who was never banned.
- **SC-002**: Every path **the platform exposes** that could modify or remove an entry is
  attempted and refused, and the attempts are listed with their outcomes — a count, not an
  adjective. **And the paths that are NOT refused are attempted too, and listed beside them**:
  research R2 measured `SET session_replication_role = replica` and `DROP TRIGGER` both
  succeeding against the role the api connects as. A criterion claiming every path is refused
  would be false on the day it was written, and the chapter's own subject is a sentence like
  that surviving because the assertion beside it was right.
- **SC-003**: The moderation set is published with a decision and a reason for every mutating
  tenant-reachable route, and the count of routes decided equals the count of **mutating
  tenant-reachable** routes the router serves. **The internal routes are counted and published
  separately**, as outside the set by construction rather than by decision — the router serves
  33 mutating routes and 8 of them are `/internal/`, so an equality against the router's whole
  count would be wrong by eight and would demand a reason for routes that cannot have one.
- **SC-004**: A route added to the platform without a decision about its moderation status
  turns a check red, demonstrated by adding one.
- **SC-005**: A tenant reading its own entries sees every entry of its own and zero of any
  other tenant's, measured against a second environment that performed the same actions.
- **SC-006**: A moderation action performed while every component the action does not strictly
  need is stopped still produces its entry, demonstrated by stopping them.
- **SC-007**: The number of FR-MOD-03's obligations this chapter discharges, and the number it
  records unmet, are published as counts with the reason for each.
- **SC-007a**: Every change this feature makes outside tests and documents is listed, and the
  list is checked against the actual diff rather than asserted — FR-012 measured, on chapter
  4.17's method.
- **SC-008**: The CI error set after this chapter is compared per error against the set before
  it, in both directions, and the comparison is published.
- **SC-009**: `check:fences` reports zero and the tutorial builds.
- **SC-010**: The chapter is between 2,000 and 4,000 prose words, counted outside fences and
  tables.

---

## Assumptions

Each of these was decided rather than asked, with the evidence that decided it.

- **The log is operational, not analytical.** Constitution III requires analytical events to be
  emitted asynchronously and accepts that the pipeline may lag or lose — chapter 4.16 wrote
  *"a lost record is the accepted cost"* in as many words. A clause that says *every* action is
  recorded cannot be built on a path that accepts loss. This also means constitution III is not
  engaged: an audit log is not an analytical query, and the plan is expected to say so
  explicitly rather than leave the reader to infer it.
- **The moderation set is the mutating routes an application credential can reach that act on
  something other than the caller.** That is a rule rather than a list, which is what FR-003
  needs. It admits ban, unban, delete a user, delete another author's message, edit another
  author's message, remove a member, change a member's role, archive and unarchive. It excludes
  reads, because FR-MOD-01 is a read and the request log already records that one was made; it
  excludes a user acting on their own message, which FR-013 of chapter 3.23 grants them.
  Expect the rule to survive contact with the router imperfectly — the routes it classifies
  wrongly are the chapter's findings.
- **Retention is stated and not enforced.** Nothing in the platform prunes an operational table;
  `schema.ts:867` already records pruning as named and deferred, and FR-MOD-06's retention job
  is row 21, three chapters away. The clause's year is recorded as an obligation with no
  mechanism, on the precedent of ADR-28 and chapter 4.9's treatment of FR-ANL-06's *daily*.
- **Immutability is enforced by the database, not by convention.** A comment saying a table is
  append-only is the shape this project has twice found to be false — *a comment is not a test*
  (chapter 4.17). What the mechanism is belongs to the plan; that the probe must attempt the
  write and be refused is FR-004.
- **The actor for an application credential is a key id.** The platform resolves `keyId` and
  cannot resolve the person holding the key. FR-007 requires the limit to be stated; it does
  not require solving it, which would be a product change this feature forbids itself.
- **The read path is this chapter's, not a later one's.** A store with no reader is chapter
  4.6's rollup and chapter 4.16's column, recorded twice as a defect. The milestone at row 23
  ends in an audit step, so the reader exists either here or as a gap that milestone inherits.
- **No existing moderation action changes.** FR-012 is the same constraint chapter 4.17 held and
  checked rather than trusted. Chapter 4.2 built four items of a later chapter's brief and that
  chapter ceased to exist; the way that happens is one useful addition at a time.

---

## Out of Scope

- **FR-MOD-01 and FR-MOD-02's chapter.** Row 20 owns them, and §7.5 of `docs/12` says to check
  their premise first. This feature notes that FR-MOD-02 appears already met and leaves the
  measurement to the chapter that owns it.
- **The retention job.** Row 21, FR-MOD-06.
- **Erasure.** Row 22, FR-MOD-04 — including the question of what erasure does to an audit
  entry naming the erased user. This feature records the tension; it does not resolve it.
- **A content classifier.** FR-MOD-07 is P4 and is not in Part 4's table at all.
- **Identifying the human behind an application credential.** FR-007 states the limit; closing
  it is key management's chapter.
