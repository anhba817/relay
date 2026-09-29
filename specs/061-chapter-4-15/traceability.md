# traceability.md — feature 061, chapter 4.15

**Built by reading, not by grep.** 4.11's mechanical coverage map reported 14 of 51
requirements uncited and all 14 were covered in substance — fourteen alarms, fourteen false.

## Functional requirements

| id | what it required | discharged by | evidence |
|---|---|---|---|
| FR-001 | parenthood recorded, queryable both ways, cannot cross an environment | migration `0020`, `schema.ts` | the composite FK refuses a cross-environment parent **by name** (`media_objects_parent_fk`), probed live |
| FR-002 | a rendition is never treated as unreferenced | `unreferencedMediaIn` | `rendition.itest.ts` "collects an unreferenced parent, and never its rendition" — and the clause is discharged by `ON DELETE CASCADE` rather than a second predicate arm |
| FR-003 | deleting an object deletes its renditions, both halves | `0020`'s cascade + `deleteObjectWithRenditions` | `rendition.itest.ts` "takes its rendition with it"; `store.test.ts` covers the store half, which has **no caller yet** and says so |
| FR-004 | a rendition is not attachable, not listed as an upload | `isNull(parentId)` inside the existing attach predicate | `rendition.itest.ts` "refuses to let a message attach a rendition" — 422 `media_not_attachable`, the same code a foreign object gets, from the one throw site |
| FR-005 | authorisation is the parent's, by the same predicate | `readableMediaObjectKey`, one substitution | `rendition.itest.ts` refusal-equality test: bodies identical but for `request_id` |
| FR-006 | generate a rendition for decodable images during processing | `thumbnail.ts`, `rendition.ts`, wired into `verifyObject` | `thumbnail.itest.ts` 10/10 against a real store; the quickstart end to end |
| FR-007 | the type set derived, a failure recorded as a value | `decodableTypes()` from `sharp.format`; `rendition_failed_reason` | `thumbnail.test.ts` "asks the decoder rather than carrying a list"; `rendition.itest.ts` "records a reason on the parent" |
| FR-008 | a rendition failure cannot block `ready`, and cannot retry for ever | the reason is set on the same verdict | `rendition.itest.ts` — parent reaches `ready` carrying `decode_failed` |
| FR-009 | a rejected object produces no rendition and no bytes | R7's ordering: generation after the checks | `thumbnail.itest.ts` "leaves a rejected verdict alone and writes nothing" |
| FR-010 | processing twice leaves one rendition | the CAS, plus a partial unique index | `rendition.itest.ts` "writes one rendition when the verdict is delivered twice"; the index verified against `postgres:16-alpine` for NULL semantics **before** it was written |
| FR-011 | delivery offers the address, or states its absence | `thumbnail` on the delivered arm; `withMediaStates` | `rendition-delivery.itest.ts` 7/7 — every door, and `Object.hasOwn` for the absence |
| FR-012 | derived bytes accounted, and the quota overshoot stated | `declared_bytes` holds the actual length | SRS 1.22 on FR-MED-12: the overshoot has no request to refuse, bounded by the rendition's own size |
| FR-013 | the video half ruled on explicitly | SRS 1.22 and ADR-34 | unmet **by decision**, with ffmpeg's 113,994,336 B and a reversal condition |
| FR-014 | the dependency chosen in an ADR | ADR-34 | four options measured; states that the size did **not** decide it; makes its own VII argument rather than borrowing ADR-32's |
| FR-015 | publish what it costs, as numbers | the chapter | ~7 kB and 15.2 ms; 8.2 ms fetch of a 60.2 ms total; 0.4 MB RSS against 36 MB of arithmetic; **and the ratio refused as a figure** |

## Success criteria

| id | status | evidence |
|---|---|---|
| SC-001 | met | the reaper predicate probed either side of the 24 h boundary, with the instant pinned before the query |
| SC-002 | met, **with the floor the criterion needed** | the cascade exercised by direct `DELETE`; the enumeration asserts the count it found, which is **zero** row-deletion paths, and names the chapter that changes it |
| SC-003 | met | byte-identical refusals, `request_id` removed before comparison |
| SC-004 | met | four arms deleted individually; two of this chapter's tested, one pre-existing arm **unnecessary** (4.12's finding reproduced), one **tested by a suite the probe had not included** |
| SC-005 | met | all four allowed types with real bytes; the thumbnail read back **out of the store**, not off the return value |
| SC-006 | met | the store listed rather than the database queried |
| SC-007 | met | a deliberate duplicate verdict; one rendition |
| SC-008 | met | three figures with their method and corpus provenance, and the corpus's limits published in the chapter body |
| SC-009 | met | 31 → 32 dependency entries, 13 → 14 third-party; worker image 245 → 279 MB; the option not taken and why |
| SC-010 | met | SRS 1.22 records the video half unmet by decision with reason and reversal condition |
| SC-011 | met | `check:fences` 0 across 58 chapters; the CI error set compared per error, both directions |
| SC-012 | met | 2,385 prose words, 2 TRAP boxes, 4 figures, every fence replays |

## Requirements this chapter deliberately did not discharge

- **FR-MED-10's reaper.** Not built; `docs/12` row 22 owns it. This chapter ships the
  predicate and the store-side deletion with **no production caller**, both commented with
  the chapter that will supply one.
- **FR-MED-12's meter.** Row 17. This chapter records the quota consequence it inherits.
- **FR-MED-05's video half.** Ruled out in writing with its price.
