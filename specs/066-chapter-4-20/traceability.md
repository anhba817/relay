# Traceability — chapter 4.20, "The messages that expire"

Built by **reading**, not by grep. Analysis pass 10 of feature 057 ran the
mechanical coverage map and found 14 of 51 requirements uncited in `tasks.md`,
**all 14 covered in substance** — fourteen alarms and fourteen false. A grep
counts citations; this counts work.

## Functional requirements

| FR | where it is met | how it is verified |
|---|---|---|
| FR-001 expired messages destroyed | `Repository.destroyMessages`, `sweep.ts` | `retention.itest.ts` — the inverted probe |
| FR-002 version rows go with them | `0025`'s cascade + exception | the same test asserts `versionRowCountRaw` 1 → 0 |
| FR-003 the policy is set per environment | `PATCH /v1/environments/{id}` | `environments.itest.ts`, three values |
| FR-004 no policy loses nothing | the sweep iterates `environmentsWithPolicy` | counted absolutely before and after |
| FR-005 the boundary, both sides | `olderThan` computed per environment | 31 days destroyed, 29 spared |
| FR-006 attachments destroyed with the message | the sweep's media half | sole-referenced gone, shared survives |
| FR-007 renditions with their parent | `media_objects_parent_fk` cascade | asserted rather than reasoned about |
| FR-008 re-runnable | the predicate is self-clearing | second run 0, and `expiredMessageIds` returns `[]` |
| FR-009 tenancy | two predicates, and one was invisible | `destroyMessages refuses an id from another tenant` |
| FR-010 the counted line | `report()` | distinguishes *no policy* from *nothing expired* |
| FR-011 nothing else changes | — | `messages` · `repository` · `internal` · `versions`, 159 green |
| FR-012 amend what measurement falsifies | — | four SRS clauses, four SAD sites, two tables, ADR-36 |
| FR-013 the `deleted` storage event | `sweep.ts` via `publishStorageDelta` | bytesDelta negative, carried not derived |
| FR-014 the route is classified | `moderation-routes.ts`, `not-moderation` | both-directions accounting test, 77 green |

## Success criteria

SC-001 through SC-007 are the retention and route suites above. SC-008 is T068's
diff check, SC-009 T073's CI error set, SC-010 the fence chain and the build,
SC-011 the word count, SC-012 the refused count published at both ends, SC-013
the storage event, SC-014 the classification.

## What is in this feature with NO requirement behind it

A grep cannot produce this section, which is why the file is written by reading.

- **`environments_retention_policy` and `messages_channel_created`.** Two
  indexes. No clause asks for an index; T013a measured both and
  `0024` carries them. The second costs 7,992 kB on a 24 MB table and the
  justification is the plan shape — `created_at` moves from `Filter` to `Index
  Cond` — rather than a ratio.
- **`unreferencedAmong`.** An extraction, not a new capability. It exists
  because `unreferencedMediaIn` asks a different question and the sweep must not
  call it.
- **Five `…Raw` repository methods.** Test fixtures that need SQL, which lint
  keeps inside `services/api/src/db/**`. `listMessagesRaw` is the precedent.
- **`expiringFlag`.** A read with no clause behind it, which exists because the
  mechanism's whole guarantee is one keyword and both ways of getting it wrong
  are silent.
- **The update to `rendition.itest.ts`.** Chapter 4.15's assertion that nothing
  deletes a `media_objects` row, which this chapter falsified on purpose.

## Clauses deliberately NOT amended

- **Constitution II.** ADR-36 decision 1 reads its existing word `path` rather
  than changing it. A feature has no authority to amend a principle, and this
  one did not need to.
- **ADR-35.** Constitution VII makes an accepted ADR immutable. ADR-36
  supersedes its scope clause for `message_edits`; `audit_log`'s is untouched.
- **FR-MED-10.** The 24-hour orphan reaper is still unbuilt and still row 22's.
  This chapter came close to implementing it by accident and the ADR records
  why it did not.
- **FR-MOD-05.** The export that would be the undo. Named in `clauses.md` as
  unbuilt rather than quietly omitted.
- **`gaps.md` 058-3.** Twenty-two routes answer 500 to a malformed path
  parameter and this chapter's makes twenty-three. Carried with its corrected
  count, not repaired.
