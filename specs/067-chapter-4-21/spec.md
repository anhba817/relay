# Feature Specification: Chapter 4.21 — "Erasure, and every path it must find"

**Feature**: 067 · **Chapter**: 4.21, movement VII's fourth · **Created**: 2026-10-04
**Source**: `docs/12-part-4-structure.md` row 22 · FR-MOD-04, FR-MED-10
**Status**: specified

## Overview

FR-MOD-04 asks for an endpoint that permanently erases all data for a specified
end user — *messages, memberships, profile, and analytical records* — within
thirty days, returning a completion receipt. FR-MED-10 adds the user's media
objects and derived objects to that bound.

**The premise check was run before this was written** and the result is between
the two chapters that came before it. Chapter 4.19 found four of five
obligations already met; chapter 4.20 found none of three. Here it is mixed, and
the mixture is the chapter:

| obligation | state at the open |
|---|---|
| an erasure endpoint | **does not exist** — zero hits for `erase` in any controller |
| messages | reachable; 205,628 name a user |
| memberships | reachable; 172,965 rows |
| profile | reachable; 192,641 users |
| **analytical records** | **three sub-cases with three different answers** |
| media objects (FR-MED-10) | reachable, but **not by prefix**, and undefined for 73% |
| unlink on tombstone (FR-MED-10) | **already met** — `deleteMessage` writes `attachments: []` |
| the 24-hour orphan reaper (FR-MED-10) | **unbuilt**, and its predicate has waited since 4.15 |
| within 30 days | no scheduler; the fifth clause bounded by ADR-28's absence |
| a completion receipt | undefined — the clause does not say what it attests |

**THE CHAPTER'S SUBJECT IS THE PHRASE `analytical records`, WHICH IS NOT ONE
THING.** Measured in `relay_analytics`:

```
api_requests          205,697 rows   NO user column at all — only principal_kind
connection_events       1,081 rows   user_external_id String — deletable
message_events              0 rows   user_id Nullable(UUID) — and nothing writes it
daily_usage_billing       824 rows   active_users_state
daily_usage_v2             56 rows     AggregateFunction(uniq, Nullable(UUID))
```

**A `uniqState` CANNOT HAVE ONE MEMBER REMOVED.** It is a sketch, lossy by
construction, with no subtract operation — so a user's contribution to 880
rollup rows cannot be erased, only recomputed. And recomputing needs
`message_events`, which holds **0 rows**, has no producer anywhere under
`services/`, and carries a 90-day TTL. The chapter has to decide what erasure
means for a number that cannot forget.

## User Scenarios & Testing

### User Story 1 — A tenant erases an end user (Priority: P1)

A customer's support tool receives a deletion request from one of their users
and calls the erasure endpoint with that user's external id.

**Independent test**: create a user with messages, memberships, a profile and an
uploaded object; erase them; assert each store no longer identifies them, and
that the stores which structurally cannot are named in the receipt.

1. **Given** a user with messages in two channels, **When** the tenant erases
   them, **Then** the messages' author is no longer that user and no read path
   returns their profile.
2. **Given** that user's memberships, **When** erasure completes, **Then** no
   membership row names them.
3. **Given** the user uploaded a media object no surviving message references,
   **When** erasure completes, **Then** the object row, its renditions and its
   stored bytes are gone.
4. **Given** the user appears in `connection_events`, **When** erasure
   completes, **Then** no row there names them.
5. **Given** the user is inside 880 `active_users_state` sketches, **When**
   erasure completes, **Then** the receipt says so explicitly rather than
   implying those rows were cleaned.
6. **Given** an external id no user has, **When** erasure is requested,
   **Then** the answer is indistinguishable from one belonging to another
   tenant.

### User Story 2 — The receipt is evidence, not a status code (Priority: P2)

The clause requires *a completion receipt* and does not say what it attests. A
204 is not a receipt; a receipt a compliance officer can file names what was
erased, what could not be, and when.

**Independent test**: read the receipt alone, with no access to the platform,
and determine which stores were cleared and which were not.

1. **Given** a completed erasure, **When** the receipt is read, **Then** it
   carries a per-store outcome with a count.
2. **Given** a store that cannot erase a user structurally, **When** the receipt
   is read, **Then** that store is listed with the reason rather than omitted.
3. **Given** two erasures of the same user, **When** both receipts are read,
   **Then** the second reports zero erased rather than failing.

### User Story 3 — What the thirty days and the reaper mean (Priority: P3)

FR-MOD-04 bounds completion at thirty days and FR-MED-10 at twenty-four hours
for orphans. Nothing in this platform schedules anything.

**Independent test**: read the chapter and find a verdict for each obligation
with where, and a sentence naming what invokes each path.

1. **Given** no scheduler exists, **When** the clause's bound is published,
   **Then** the chapter states the obligation unmet by decision rather than
   implying a timer.
2. **Given** `unreferencedMediaIn` has had no caller since chapter 4.15, **When**
   this chapter closes, **Then** either it has one or the chapter says why not.

### Edge Cases

- **A user whose media objects have no recorded uploader.** 11,050 of 15,029
  objects carry `user_id IS NULL`, which FR-MED-06 made nullable on purpose for
  server-side uploads. *A user's media objects* is undefined for 73% of them.
- **A tombstone retaining its author.** FR-MSG-08 says a deletion retains the
  author; FR-MOD-04 says erasure removes the user. FR-USR-05's *unless message
  deletion is explicitly requested* is the escape, and this chapter is the
  request.
- **`deleteUser` ALREADY EXISTS AND DELIBERATELY KEEPS WHAT ERASURE MUST DESTROY.**
  FR-USR-05's deletion clears the profile, memberships and read positions and
  **keeps the row, the messages, and every `usage_active_users` row** — the last
  with a billing argument in the code. Erasure is the same verb with the opposite
  answer on three of those, and the chapter has to say which clause wins where.
- **An audit entry naming the erased user.** 1,324 rows name a user target and
  the log is append-only (ADR-35). An entry recording that somebody was banned
  is itself a record of that person.
- **A user in another tenant with the same external id.** External ids are
  unique per environment, not globally.
- **Erasure of a user who has already been erased.** The second call must be a
  receipt reporting zero, not a 404.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST provide an endpoint that erases a specified end
  user's data within the calling tenant's environment.
- **FR-002**: Erasure MUST remove the user's profile, memberships, and
  identifying authorship of their messages.
- **FR-003**: Erasure MUST destroy media objects the user uploaded that no
  surviving message references, with their renditions and stored bytes.
- **FR-004**: Erasure MUST remove rows naming the user from every analytical
  table that identifies a user and is capable of row-level deletion.
- **FR-005**: Where an analytical representation cannot have one user removed,
  erasure MUST say so in the receipt rather than omit the store.
- **FR-006**: The endpoint MUST return a receipt listing, per store, what was
  erased, what could not be, and when.
- **FR-007**: Erasure MUST be re-runnable: a second call for the same user
  reports zero erased and does not fail.
- **FR-008**: Erasure MUST act only within the calling tenant's environment, and
  an external id belonging to another tenant MUST be indistinguishable from one
  that does not exist.
- **FR-009**: The endpoint MUST accept an application credential only.
- **FR-010**: The counted output MUST distinguish *nothing to erase* from *user
  not found*.
- **FR-011**: Nothing outside this chapter's subject may change behaviour.
- **FR-012**: Where measurement falsifies a published clause or document, the
  document MUST be amended rather than left to diverge.
- **FR-013**: An erasure MUST write an `audit_log` entry, since FR-MOD-03's
  population is moderation actions and this is one performed by a credential.

### Key Entities

- **`users`** — the profile; 192,641 rows. `external_id` is unique per
  environment.
- **`members`** — 172,965 rows.
- **`messages.user_id`** — nullable, and the foreign key is **`NO ACTION`**, not
  `ON DELETE SET NULL`. All five foreign keys to `users` are, measured. `ON DELETE SET
  NULL` is the thing FR-USR-05's implementation **rejected** and says so in both the SRS
  and the code: it *"satisfies the letter of preserving their messages and breaks
  delivery — the resume path drops a senderless row."*
- **`usage_active_users`** — **22,150 rows naming 22,147 users, in Postgres**, and
  `deleteUser` keeps every one of them on purpose: *"a customer who deleted a user in
  March still owes for March."* FR-MOD-04 calls analytical records erasable and this
  table is the strongest counter-argument in the platform.
- **`media_objects.user_id`** — nullable, and null on 11,050 of 15,029 rows.
- **`connection_events.user_external_id`** — the one analytical column holding a
  user identifier in a deletable form.
- **`daily_usage_billing.active_users_state`, `daily_usage_v2.active_users_state`**
  — `AggregateFunction(uniq, Nullable(UUID))` over 880 rows. No member can be
  removed from a sketch.

## Success Criteria

### Measurable Outcomes

- **SC-001**: After erasure, no read path in the platform returns the erased
  user's profile or external id.
- **SC-002**: After erasure, a count of rows naming the user is zero in every
  operational table that identifies one.
- **SC-003**: After erasure, a count of rows naming the user is zero in every
  analytical table capable of row-level deletion.
- **SC-004**: The receipt names every store, including those that could not
  erase, and a reader with only the receipt can say which is which.
- **SC-005**: A second erasure of the same user reports zero erased.
- **SC-006**: An external id from another tenant produces a response
  byte-identical to one that does not exist, apart from the request id.
- **SC-007**: The user's sole-referenced media objects are gone from the
  database and the object store; a shared one survives.
- **SC-008**: Every change outside tests and documents is listed and checked
  against the diff.
- **SC-009**: The CI error set after this chapter is compared per error against
  the set before it, in both directions.
- **SC-010**: `check:fences` reports zero and all six tutorial gates pass,
  measured after the last edit to any published file.
- **SC-011**: The chapter is between 2,000 and 4,000 prose words.
- **SC-012**: The number of analytical rows that cannot be erased is published
  with the reason, and re-measured at the close.
- **SC-013**: Each of FR-MOD-04's four obligations and FR-MED-10's three has a
  verdict with where.

## Assumptions

- **Erasure is per environment, not per platform.** External ids are unique per
  environment and a tenant may only erase within their own.
- **`api_requests` needs no erasure.** It carries no user column — only
  `principal_kind` — so the largest analytical table is already clean. This is
  recorded as a finding rather than assumed silently.
- **`message_events` needs none either**, for a different reason: it holds 0
  rows and nothing under `services/` writes it (`gaps.md` 051).
- **The thirty-day bound will be unmet by decision**, as the fifth clause
  bounded by ADR-28's absent scheduler. Erasure is synchronous on the request,
  which satisfies the bound trivially while the clause's *within 30 days*
  language goes unexercised.
- **The 24-hour orphan reaper stays out of scope** unless the measurement says
  otherwise. It is FR-MED-10's second sentence and has its own population — 48
  never-attached objects in one environment, measured by chapter 4.20.

## Out of Scope

- **Tenant-level export (FR-MOD-05).** Still unbuilt, still the undo that does
  not exist, and named again rather than quietly omitted.
- **Repairing `gaps.md` 058-3.** Twenty-three routes answer 500 to a malformed
  path parameter; this chapter's would make twenty-four.
- **Deleting from `audit_log`.** It is append-only and an entry is a record of
  an action, not a copy of its target. The tension is stated.
