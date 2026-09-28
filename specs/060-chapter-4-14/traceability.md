# traceability.md — feature 060, chapter 4.14

**Built by reading, not by grep.** 057 ran the mechanical coverage map for the first time and
found 14 of 51 requirements uncited in `tasks.md`, **all 14 covered in substance** — fourteen
alarms, fourteen false. A citation is not coverage and an absent citation is not a gap.

## The clause this chapter exists for

| Clause | Sentence | Where it is met | Verified by |
|---|---|---|---|
| FR-MED-07 | *"Real-time and history delivery shall include each attachment's state"* | `deliveredAttachmentSchema`; `messageSchema` points at it; `withMediaStates` at every read | `attachment-state.itest.ts` (6), `attach.itest.ts` (3 repaired), `messages.itest.ts` (1 repaired) |
| FR-MED-07 | *"A `media.updated` event shall be delivered on the referencing channels…"* | the verdict seam's `announce`, on `revision:{channel_id}`'s third arm | `media-updated.itest.ts` (9), `session.test.ts` (2) |

**Amended as SRS revision 1.21**, because the platform is broader than the clause: the clause
names two doors and the derivation finds more, including the send response, the edit response
and resume. Extending a published clause silently is the divergence constitution VII forbids.

## This feature's own requirements

| FR | Met by | Verified by |
|---|---|---|
| FR-001 state on every media attachment | `deliveredAttachmentSchema`, required | `attachments.test.ts` ×4 |
| FR-002 read at serve time, not stored | `withMediaStates` after the transaction | `attachment-state.itest.ts` — the column asserted byte-identical either side of a verdict |
| FR-003 doors derived, not listed | `doors.txt`; FR-003 deletes its own list | `tsc --noEmit` + the suites; SC-002 |
| FR-004 one frame per referencing channel | `announce` + `channelsReferencingMediaIn` | `media-updated.itest.ts` at N = 0, 1, 2 and two-in-one-channel |
| FR-005 only on a real transition | gated on the compare-and-set's `applied` | the duplicate-verdict test; per-arm probe |
| FR-006 no reference → nothing, no failure | an empty channel list is success | the no-reference test, with a positive control |
| FR-007 authorised only | delivery is to channel subscribers | `session.test.ts` ×2; and see R5 — subscribers ⊆ authorised |
| FR-008 ADR with ADR-25's arithmetic | **ADR-33** | the record itself; SC-007 |
| FR-009 the event is not the only means | the floor at every door | the already-terminal test (SC-006) |
| FR-010 no rejection reason on the frame | the arm has no such field | `frames.test.ts`, `media-updated.itest.ts` |
| FR-011 tombstone matches the delivery gate | **no code** — the unlink already empties the array | the tombstone test, and 2,867 rows measured |
| FR-012 amend the clause | **SRS 1.21** | `check:docs` — 22 revisions ascend, 1.0 to 1.21 |

## Success criteria

| SC | Result |
|---|---|
| SC-001 zero client requests between send and update | met — `media-updated.itest.ts`; latency bound cited as NFR-PRF-01 with the interval stated |
| SC-002 derived doors = covered doors, both directions | met — `doors.txt`, with each door's provenance |
| SC-003 N deliveries for N channels, at 0, 1, 2 | met at all three, plus two-messages-one-channel |
| SC-004 unauthorised receives zero | met — `session.test.ts`, and the cross-tenant query test |
| SC-005 duplicate verdict produces zero | met |
| SC-006 correct state with no frame at all | met — the already-terminal case |
| SC-007 both ADR-25 bounds evaluated numerically | met — ADR-33 and the chapter |
| SC-008 `check:fences` 0; CI per error | **half met.** Fences 0 across 57 chapters. The CI comparison could not run — `gaps.md` 060-11 |
| SC-009 prose within bound, figures measured | met — 2,254 words; every figure from `baseline.txt` |

## Constitution

| Principle | How |
|---|---|
| I tenant isolation | one query body, one predicate, two callers; the cross-tenant test is the arm the probe deletes |
| III two data paths | operational only; `media_events` stays deferred (059-11) |
| IV single writer | the state has one home; storing it on the message would give one fact two |
| V API-first | additive on the wire — a new key on a payload clients already parse, and one new frame |
| VI test-verified | every behaviour has a red-first test; the per-arm probe is the instrument, not the coverage number |
| VII boring | no service, no dependency, **no sixth subject grammar** — ADR-25's threshold preserved rather than spent |
