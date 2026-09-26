# Traceability — feature 059, chapter 4.13, "the only service that reads the bytes"

**Built by reading, not by grep.** A mechanical citation map at 4.11 reported **14 of 51
requirements uncited in `tasks.md`** and all fourteen were covered in substance — fourteen
alarms, fourteen false. Every row below names the artefact that discharges it and the
measurement or test that says so.

---

## Functional requirements

| Id | Where it is met | The evidence |
|---|---|---|
| FR-001 | `services/media-worker/src/sweep.ts`, `GET /internal/media/pending` | A sweep, not a notice, and the decision is measured: one signed `HEAD` is 1.412 ms and the whole 3,292-row backlog is 4.2 s serial. `gaps.md` 059-1 carries why the event the SAD names cannot exist. |
| FR-002 | `services/media-worker/src/verify.ts` `judge`, `sniff.ts` | Size from the store's `content-length`, type from the **bytes**. Measured: a presigned PUT of twelve MP4 bytes sent as `image/png` answers `HEAD` with `image/png`, so the store's header is the client's own claim. `verify.test.ts`, `sniff.test.ts`, and `verify.itest.ts`'s "REJECTS A GIF DECLARED AS A PNG". |
| FR-003 | `media.controller.ts` `verdict`, `store.ts` `deleteObject` | Both halves asserted against the STORE rather than against a spy: `verify.itest.ts` "AND THE REJECTED OBJECT'S BYTES ARE GONE" does a signed `HEAD` and expects 404. |
| FR-004 | `services/media-worker/src/scan.ts`, and the order in `verify.ts` | The scan runs first and unconditionally — nothing above it can refuse the object. `scan.itest.ts` "THE CONTROL: the scanner itself finds EICAR" asserts the engine's own answer so a green `scan_failed` cannot come from a scanner that refused everything. |
| FR-005 | `media_objects.rejected_reason`, and `contracts/` §4 | Two values, `declaration_mismatch` and `scan_failed`, distinguishable **to the platform**. The customer sees neither: the delivery route answers one 404 to six conditions, compared whole with `request_id` removed. |
| FR-006 | `dimensions.ts`; **duration is NOT met** | Dimensions for all four image formats, each arm run red on its own. Duration is recorded PARTLY MET in SRS revision 1.20 and in `gaps.md` 059-7 — *unmet by decision*, on FR-MED-07's precedent. |
| FR-007 | `verify.ts` `probe` and `judge` | One function produces the verdict and it cannot answer `ready` before the scan, the size check and the type check have each run. Proven by deleting each: disjoint sets of red tests. |
| FR-008 | `recordMediaVerdict`'s `WHERE state = 'pending'`; `verify.itest.ts` | Idempotent at the seam (a second `ready` answers `applied: false`) **and** at the worker: "A SECOND PASS DOES NOT RE-READ THE BYTES" counts requests for that object's own key and expects zero. |
| FR-009 | `verify.ts`'s `unavailable` arm; `scan.itest.ts` | Both halves — the object stays `pending` with the scanner unreachable, **and** reaches `ready` when it comes back, because only the second proves the first was a pause. Plus "A SCANNER THAT ANSWERS NONSENSE IS ALSO AN OUTAGE". |
| FR-010 | `migrations/0018_media_states.sql`, `schema.ts` | The widened CHECK, and a test that inserts `'scanning'` and asserts `violates check constraint "media_objects_state_check"`. |
| FR-011 | `services/media-worker/` has no database client | Enforced by the build, not by discipline: `eslint.config.mjs` refuses a `pg` or `drizzle-orm` import outside the api's `db/`. The worker's two questions are HTTP. |
| FR-012 | `readableMediaObjectKey`'s fourth predicate | Decided **yes**, in `page.mdx` and in ADR-14's own terms, with the reason it could not have shipped a chapter earlier: 10 of 76 red, measured. |
| FR-013 | **ADR-31** and **ADR-32** in `docs/05-sad.md` | Both clauses of constitution VII, and only one had been named by any artifact. `docs/12` §7.3 closed in the table and in §7. |
| FR-014 | `scan.ts`'s header comment and `page.mdx` | *A signature scanner detects known signatures.* SAD R9 names scanner misses as residual; the chapter says a reader who finishes believing *scanned* means *safe* has learned something false. |
| FR-015 | `reserveMediaSlot`'s `ne(state, 'rejected')` | The ROW leaves the sum; `declared_bytes` is untouched, because it is the audit record's substance. `media-verdict.itest.ts` asserts the committed figure returns to its earlier value and the column does not. |

## Success criteria

| Id | Result | The measurement |
|---|---|---|
| SC-001 | MET | `verify.itest.ts` "carries a real PNG from pending to ready, with its dimensions" — 320×200, `verified_bytes` and `verified_type` from the probe. |
| SC-002 | MET | Three deltas — one byte over, one byte under, five thousand over — all `rejected` with `declaration_mismatch`, plus the GIF-declared-as-PNG case at exactly the right size. |
| SC-003 | MET, **and it cannot prove the scanner is current** | EICAR rejected with `scan_failed` and the bytes gone. `gaps.md` 059-5: that signature is in `main.cvd` v63 and detects identically against a database thirteen days old. |
| SC-004 | MET | The scanner's address pointed at a port the kernel refuses — **not** the container stopped, which is an action wider than its own test. Both halves, and the bytes survive the outage. |
| SC-005 | MET | Zero store requests for the object's own key on the second pass. Counted by watching the store, not by asserting a method was called. |
| SC-006 | MET, with the figure it exposes | p50 **5,080 ms** at a five-second interval, of which the work is **7 ms**. Start instant from the store's `last-modified`, at one-second resolution. `gaps.md` 059-2. |
| SC-007 | MET | **3,337** prose words, **3** TRAP boxes, 4 figures. |
| SC-008 | MET | `check:fences` **0**, EXIT 0, 291 files across 56 chapters — stated as the absolute number, which is 055's rule. |
| SC-009 | see `baseline.txt`'s close-out | The tutorial job on this chapter's push. |
| SC-010 | MET | **31 dependency entries against 29 at `part4-ch12`, and both new ones are workspace links.** Third-party entries 20 → 20; distinct third-party packages 13 → 13. A fifth service and a seventh container, and no new third-party dependency. |
| SC-011 | MET | `docs/12` §7.3 closed in the table row **and** in §7's prose, by the chapter that owns it — which §7.1 was not, and it stayed open for two features. |

---

## What is deliberately not met

| Clause | Why | Where it is written |
|---|---|---|
| FR-MED-04, the duration half | Four unrelated container parsers, MP3 VBR the hard case | SRS 1.20, `gaps.md` 059-7 |
| FR-MED-07, `media.updated` | The clause asks for an EVENT and no chapter has written the producer; 4.13 makes its subject reachable | SRS 1.20 |
| `media_events` | This chapter owns `ready` and `rejected`; DR-17's sum reads `uploaded` and `deleted` | `gaps.md` 059-11, `data-model.md` §4 |
| `media.uploaded` | It has no producer and cannot have one under ADR-13 | `gaps.md` 059-1 |
