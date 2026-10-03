# Traceability — chapter 4.19, "Everything, including what was deleted"

**Built by reading, not by grep.** Chapter 4.11's mechanical coverage map raised fourteen
alarms over `tasks.md` and all fourteen were false — a requirement can be discharged by
work that never cites its number. Each row below names where the obligation is actually
met and what would have to change for the row to stop being true.

## Functional requirements

| | discharged by | evidence |
|---|---|---|
| **FR-001** preserve the text held at deletion | `deleteMessage`'s insert on the branch that deletes, `0022`'s column | `versions.itest.ts` — three texts for edited-twice-then-deleted, one for deleted-with-no-edits. Removing the insert turns **4 of 6** red |
| **FR-002** readable through the same surface, one request | `listMessageEdits` returns the new rows; no second route | the route test in `versions.itest.ts`; the contract states the live-message asymmetry rather than hiding it |
| **FR-003** each version carries when and why | `ended_at` and `ended_by`, `message_edits_ended_by_check` | `versions.itest.ts` asserts `["edit","edit","deletion"]`; the catalogue shows the constraint |
| **FR-004** a no-op deletion preserves nothing | the insert sits after the already-deleted early return | `versions.itest.ts` — an **absolute count, twice**, 2 and 2, not a delta |
| **FR-005** application credential only | `@Accepts("application")`, unchanged | `versions.itest.ts` asserts 403 **by code**; deleting the decorator answers 200 |
| **FR-006** no cross-tenant read | three scoped reads on the route | `gauntlet.itest.ts:242`, which predates this feature and still passes with version rows on both sides. **T037 measured that removing any two of the three scopes is invisible** |
| **FR-007** the removal instant on the history row | `deleted_at` on `MessageWithSender`, filled by `listMessages` | `versions.itest.ts` — present key with a null on a live row, the instant on a tombstone, equal to the outbox event's |
| **FR-008** no behaviour change beyond FR-001 | — | **checked, and it caught a violation**: a required `deleted_at` on `MessageRow` broke the internal send response in 3 tests. Moved to the read shape. Final state: `messages.itest.ts` 68, `repository.itest.ts` 71, `internal.itest.ts` green, `history-drift` 2 |
| **FR-009** state what can and cannot be recovered | `clauses.md`, and the chapter's own closing section | 13 obligations across 4 clauses; the boundary as **5,060 / 3,762 / 1,298** |
| **FR-010** amend documents that disagree | SRS 1.26, FR-MSG-07, FR-MOD-01, four SAD sites, ADR-35 in both homes, both Part 4 tables, `docs/12` §7.5 | `check:docs` green, 27 revisions ascending to 1.26 |
| **FR-011** a version cannot be modified or removed, demonstrated | `0023`'s trigger | `UPDATE` and `DELETE` refused through `psql`, the row surviving both — **attempted, not asserted** |
| **FR-012** publish the refusal's scope | the migration's comment, `clauses.md`, SRS FR-MSG-07 | both bypasses re-measured on this table: `session_replication_role = replica` and `DROP TRIGGER` each succeed |

## Success criteria

| | met | where |
|---|---|---|
| **SC-001** three texts, in order, each with its instant | yes | `versions.itest.ts`; it was two of three before |
| **SC-002** one text for a message deleted with no edits | yes | `versions.itest.ts`; it was zero of one before |
| **SC-003** removal instant on a tombstone's row, absent on a live one | yes | `versions.itest.ts`, asserted as a **present key** |
| **SC-004** a second deletion adds no version | yes | counted absolutely, twice |
| **SC-005** a foreign message's versions read as an absent message's | yes | `gauntlet.itest.ts:242`, with version rows present on both sides |
| **SC-006** the user-token refusal asserted by code | yes | `wrong_credential_type`, and run red by deleting the decorator |
| **SC-007** the boundary as a counted list with clauses | yes | `clauses.md` |
| **SC-008** every non-test, non-document change listed against the diff | T070 | phase 9 |
| **SC-009** the CI error set compared per error, both directions | T075 | phase 9 |
| **SC-010** `check:fences` zero and the tutorial builds | T063, T067a | phase 8 and 9 |
| **SC-011** 2,000–4,000 prose words | T054, T064 | phase 8 |
| **SC-012** modify and remove both refused, scope published | yes | T031 and T032 |

## What is NOT traceable to a requirement, and is in the feature anyway

- **`schema.ts`'s millisecond/microsecond correction.** No clause asked for it. It is a
  comment that was wrong by a factor of 1000 about a primary key, found because this
  chapter's insert collided with the edit path's in a concurrent test. The fix to the
  deletion path is FR-001's; the corrected sentence is nobody's requirement and is in
  `gaps.md` 065-2 with the half that remains.
- **`messages.controller.ts`'s widened return type.** The compiler could not ask for it
  and no test could see it: the two new fields reached the client either way. A type
  that was silently wrong.

## Clauses this chapter did NOT amend, and why

- **FR-MSG-08** — the clause the defect was breaking, correct as written. Losing the
  final text at a moderation delete is a hard deletion on the path that sentence
  reserves for the compliance endpoint. Nothing to change.
- **FR-MSG-10** — *"History responses shall include tombstones so that clients can
  render deletions without gaps in ordering."* US2 serves it and no artifact in this
  feature named it until T042 read the rows beside FR-MSG-08. The clause's letter was
  already met; what this chapter adds is the instant that makes the rendering legible.
  Recorded rather than amended, because the words do not need to change.
- **FR-MSG-09** — bounds history at 200 per page and says nothing about the versions
  route, which is bounded by nothing. T040 measured the lane's worst case at three
  versions on one message and recorded the shape rather than solving it.
