# Traceability — feature 056, chapter 4.10, "the upload that never reaches us"

Every requirement and criterion to the tasks and artifacts that discharged it, and **anything
discharged in a weaker form than its words suggest**, said so here rather than implied.

## Functional requirements

| id | discharged by | evidence |
|---|---|---|
| FR-001 | T001, T002 | `quay.io/minio/minio` in `compose.yaml`, 241 MB, healthy; `presign.itest.ts` reaches it from the host, 9 of 9 |
| FR-002 | T014, T014a, T016 | `POST /v1/media`, `@Accepts("application", "user")`; `media.itest.ts` issues a slot with each credential class |
| FR-003 | T012, T015, T009 | `SLOT_SECONDS = 900`; the row holds nine columns and none is the URL or its expiry; the store answers `Request has expired` from its own clock |
| FR-004 | T011, T017 | `environment_id` non-null, `user_id` nullable; the pair of tests — an API key's row carries no user and a user token's does |
| FR-005 | T013, T022 | `ALLOWED_TYPES`, ten entries; 415 `media_type_not_allowed`, **and all ten accepted types asked for in the same file** |
| FR-006 | T013, T023 | `KIND_CAPS` 10/25/100 MB; 413 `media_too_large` naming both figures, and 25 MB of audio accepted beside 25 MB of image refused |
| FR-007 | T024, T031, T041 | 402 `media_storage_exhausted`; 999 issued, 1,000 issued, 1,001 refused, +1 on a full cap refused |
| FR-008 | T021, T026, T027, T028 | four codes, asserted by code and not by status; `check:errors` 33 codes, 33 sections, exit 0 |
| FR-009 | T025, T024b | before, before, before + 1 — the accepted request beside the two refusals is the control; and no row after the store refusal |
| FR-010 | T031, T032 | `storage_bytes` in the parser and in `0016`'s twelve CHECK clauses; `{"disk_inodes":…}` accepted by the column and refused by `.strict()` |
| FR-011 | T037, T038 | SRS 1.17 amends FR-RTL-05 and FR-MED-12; the amendment names which kind of quantity each of the four is |
| FR-012 | T033 | no key: two 9 MB slots issued, 18,000,000 committed; `hard: 0`: one byte refused |
| FR-013 | T016 | the api's own request log — 5 slot requests, 0 rows for the 44-byte PUT |
| FR-014 | T043, T045a | `gaps.md` 056-2 and a `TRAP` box; the error reference says *"declared"* because that is what it refuses |
| FR-015 | T042 | `gaps.md` 056-1, measured: the tenant issued 600 against a cap of 1,000 and then refused still reports 600 committed |
| FR-016 | T028a | `messages.itest.ts` attaches an id `POST /v1/media` really minted: still 422, still `media_not_available`, and the message does not echo the id |
| FR-017 | T024a, T024b | `storeReachable()`, +1.524 ms p50; 503 `media_storage_unavailable` with the endpoint moved to a port the kernel refuses |
| FR-018 | T027a, T027b | four rungs — 402, 413, 415, 503 — and 19 tests throwing **unnamed** at eight statuses, red on deleting the 415 rung |

## Measurable outcomes

| id | met | evidence |
|---|---|---|
| SC-001 | yes | `media.itest: the ingester drained 1 batches, 5 records` — five slot requests, nothing for the upload, scoped by `ts` so the earlier tests' rows cannot inflate it |
| SC-002 | yes | measured against the store, not asserted from the issuing code: `403 · Request has expired` from its own clock |
| SC-003 | yes | four codes, asserted by code; distinctness one assertion and correctness four |
| SC-004 | yes | `check-error-codes: 33 codes, 33 sections`, exit 0, and both failure directions reproduced |
| SC-005 | yes | 999 / 1,000 / 1,001, three tenants; falsified by flipping `>` to `>=` |
| SC-006 | yes | both sides asked, in one test |
| SC-007 | yes | **`290 fenced files replay onto relay-platform across 53 chapters`, EXIT 0.** The absolute number, not a delta |
| SC-008 | yes | 3,992 prose words; four `TRAP` boxes |
| SC-009 | pending | observable only after the push (T060, T061) |
| SC-010 | yes | one container; **29 runtime dependencies at `part4-ch9` and 29 now**, across all eight `package.json` files, and no S3 client of any kind in any of them |

## Discharged in a weaker form than the words suggest

**FR-013 is proven for this chapter's upload path and not as a platform property.** The request
log shows no row for the PUT because the PUT went to a different server on a different port; what
it cannot show is that no future route buffers a body. The claim is an observation about one path,
not an invariant anything enforces.

**FR-007's cap is over declarations.** `gaps.md` 056-2. The arithmetic is correct and the input is
the client's own number, so the requirement holds against an honest or buggy client and not
against a hostile one until FR-MED-03 ships.

**FR-003's fifteen minutes is enforced by the store and published by the api.** The two agree
because the api computes both from one constant; nothing compares them. A future change to
`SLOT_SECONDS` that touched the signature and not the published `expires_at` would be invisible.

**FR-009 is asserted for the four refusals this chapter can produce.** A refusal raised by a
future guard before the service runs writes no row for a different reason, and no test covers
that case because no such guard exists.

**SC-002's "refused after" is measured with a URL signed in the past**, not by waiting fifteen
minutes. The store's clock is the authority either way, and a slot whose expiry is fifteen minutes
in the future is not distinguishable from one that is fifteen hours out by any test that does not
wait.

**And FR-011 was satisfiable two ways — amend or record why not.** It was amended. What the
amendment cannot do is make the three citing clauses consistent retroactively: FR-MED-12's daily
figure is a time series for the dashboard and the quota reads the level, which the clause now says
and no code reads yet, because FR-MED-12's chapter is in movement VI.
