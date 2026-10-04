# Clauses — chapter 4.21, "Erasure, and every path it must find"

A verdict per obligation, with where. The clause texts are quoted rather than
summarised, because this chapter's two predecessors both found a clause whose
own words were stricter or wider than the sentence everybody remembered.

**met** — the platform does it and a test says so.
**demonstrated** — met, and the chapter shows it end to end.
**unmet by decision** — not built, with the reason recorded.
**unreachable** — cannot be exercised here, and why.

---

## FR-MOD-04, split into its four obligations

> The system shall provide an endpoint that permanently erases all data for a
> specified end user — messages, memberships, profile, and analytical records —
> completing within 30 days and returning a completion receipt.

| # | obligation | verdict | where |
|---|---|---|---|
| 1 | an endpoint | **demonstrated** | `DELETE /v1/users/:externalId/data`, `users.controller.ts` · `erasure.itest.ts` 12 of 12 |
| 2 | permanently erases all data — four nouns | **split, see below** | |
| 3 | completing within 30 days | **met and unexercised** | synchronous, 53 ms measured. T033 |
| 4 | returning a completion receipt | **demonstrated** | five outcomes · `contracts/erasure.md` |

### Obligation 2 is four nouns and they do not get one verdict

| noun | verdict | what happens |
|---|---|---|
| **profile** | **demonstrated** | `display_name`, `avatar_url`, `metadata` cleared and **`external_id` replaced** with `erased:<users.id>` |
| **memberships** | **demonstrated** | `members` and `read_positions` deleted; the gauntlet asserts the other tenant's survive |
| **messages** | **unmet by decision** | FR-028 keeps a channel's history whole. The author is erased and the text is not. T010 |
| **analytical records** | **three answers, none of them one word** | below |

**THE FOURTH NOUN IS WHY THIS CHAPTER NEEDED A DECISION AND NOT A TRAVERSAL.**

| store | verdict | measured |
|---|---|---|
| `connection_events` | **demonstrated** | holds `user_external_id String` — the identity. Deleted, both predicates bound |
| `api_requests` | **met, vacuously** | **no user column at all** over 205,697 rows. Chapter 4.4's design: the cheapest erasure is the column nobody collected |
| `message_events` | **met, vacuously, and by defect** | 0 rows, no producer (`gaps.md` 051) |
| `daily_usage_*` | **met by T011's reading** | seven `AggregateFunction(uniq, Nullable(UUID))` columns, keyed on the internal uuid. A key into an erased row names nobody, so there is nothing to subtract and nothing identifying. **ADR-37** |

**AND `audit_log` IS THE ONE THAT CANNOT.** It is not analytical and the clause does
not name it, which is why it was nearly missed: it holds `target_id text` — the
person's EXTERNAL id — on **1,357 of 1,357 user-target rows, not one a uuid** — and
ADR-35 made it append-only. The erasure **writes one more**. Reported as
`cannot_erase` rather than omitted, and the chapter's TRAP box.

---

## FR-MED-10, split into its three

> Deleting a message (tombstone) shall unlink its attachments; unreferenced media
> objects shall be hard-deleted by a scheduled job after 24 hours. Compliance
> erasure (FR-MOD-04) shall delete a user's media objects and derived objects
> within the same 30-day bound.

| # | obligation | verdict | where |
|---|---|---|---|
| 1 | a tombstone unlinks its attachments | **already met** | `deleteMessage` writes `attachments: []`. Not this chapter's, and T034 says so rather than claiming it |
| 2 | a scheduled job reaps unreferenced objects after 24 hours | **unmet by decision** | `unreferencedMediaIn` has had no caller since chapter 4.15; chapter 4.20 declined it deliberately because its population is objects nothing ever attached. **ADR-28's absent scheduler**, and this chapter does not move it |
| 3 | erasure deletes the user's objects and derived objects within 30 days | **demonstrated, and incomplete in a way the receipt names** | `destroyMediaObjects` + `deleteObjectWithRenditions`, renditions by `media_objects_parent_fk`'s cascade |

**OBLIGATION 3's INCOMPLETENESS IS A COLUMN, NOT A BUG.** `media_objects.user_id` is
nullable and **11,173 of 15,189 objects — 73.6% — record no uploader**. An erasure
that takes the attributed ones is correct and cannot be complete. The receipt says
so in its own `note`, which is where a compliance officer will read it.

**SO THIS CHAPTER MOVED ONE OF THE THREE.** One was already met and one stays unmet.

---

## FR-MOD-05, named for the third chapter running

> The system shall support exporting all data for a tenant as newline-delimited
> JSON, generated asynchronously with a notification on completion.

**UNMET, UNBUILT, AND IT IS THE CLAUSE THAT WOULD MAKE THIS ONE SURVIVABLE.** There
is no undo for an erasure and there cannot be; an export is what lets a tenant hold
a copy before asking. It is two rows above FR-MOD-06 in the SRS and has been named
by chapters 4.19, 4.20 and this one without moving.

---

## The bound that is met and never tested (T033)

**`within 30 days` IS SATISFIED TRIVIALLY.** The erasure is synchronous — 53 ms
measured with the analytical store stopped, which is the slow path — so the bound is
met by four orders of magnitude and **no test can exercise it**. There is no
scheduler, so there is no asynchronous mode for the bound to govern.

**IT IS THE FIFTH CLAUSE BOUNDED BY ADR-28's ABSENCE**, after FR-ANL-06's daily job,
DR-17, FR-MOD-03's year and FR-MOD-06's sweep. And it is the second whose absence
would be a **compliance promise** rather than a reporting one — except that here the
absence costs nothing, because nothing needs scheduling. Recorded so the count stays
honest: four of the five are gaps and this one is not.

---

## What is NOT amended, and why that is a decision

- **FR-USR-05** needs no amendment. Its *"unless message deletion is explicitly
  requested"* is not what FR-MOD-04 asks for, and T010 chose the reading in which the
  two clauses do not collide rather than the one that makes them.
- **FR-029** needs no amendment. `usage_active_users` is kept in full and its count
  is unchanged to the row, so *"a customer who deleted a user in March still owes for
  March"* is true after an erasure exactly as before.
- **FR-MOD-04 DOES need one sentence** (T043a), and it is the cheap version rather
  than a recorded non-conformance: *an analytical record whose only identifier is a
  key into an erased row counts as erased.* That is what ADR-37 establishes and what
  lets four of the five analytical stores be met rather than excused.
