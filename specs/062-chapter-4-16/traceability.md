# 062 — traceability

**Built by READING, not by grep.** Chapter 4.11's mechanical coverage map reported 14 of 51
requirements uncited in `tasks.md` and **all 14 were covered in substance** — fourteen alarms,
fourteen false. What follows names, for each requirement, the artifact that discharges it and
the test that would go red if it stopped being true.

## The specification's functional requirements

| FR | what it asks | where it is | what would go red |
|---|---|---|---|
| FR-001 | a record for every change to a tenant's stored bytes | `metering/storage-event.ts`, three call sites | `storage-metering.itest.ts` — *"moves the day's delta by exactly the bytes the quota counts"* |
| FR-002 | the record carries the quota's own quantity | `publishStorageDelta`'s `bytesDelta`, `declared_bytes` at every caller | same, and the rejection test asserts the negation |
| FR-003 | the record carries the kind | `mediaStoredRecordSchema.kind`, required | `shape.test.ts` — *"refuses a record missing any field it must carry"* |
| FR-003a | the record's time is when it became true | `occurred_at` → `ts` in `shapeMediaStored` | `shape.test.ts` — *"renames occurred_at to ts"* |
| FR-004 | the consumer claims the record rather than terminating it | `route()`'s fourth arm | `ingest.itest.ts` — the media drain, `writtenMediaEvents` 2 and `malformed` 6 |
| FR-005 | recorded exactly once under retry or redelivery | `Nats-Msg-Id` = `${mediaId}:${cause}`; `applied` gates the verdict emitter | `storage-metering.itest.ts` — the duplicate verdict, 422 and no second delta |
| FR-006 | a comparison per tenant, reporting the direction | `metering/storage-reconcile.ts` `verdictFor` | `storage-reconcile.test.ts` (15) and `.itest.ts` (9) |
| FR-007 | report how many tenants were examined | `StorageReport.tenantsExamined` and `sides` | `.itest.ts` — *"reports how many tenants it examined and where they came from"* |
| FR-008 | a verdict for a tenant present on one side only | `not-comparable` / `no-data`, decided before any arithmetic | `.itest.ts` — *"calls a tenant present on one side only what it is"* |
| FR-009 | uploads counted per tenant per day by kind | `0018`'s `sumMapIf`, read by `uploadsByKind` | `storage-metering.itest.ts` SC-007, and `metering.itest.ts` |
| FR-010 | one answer about whether a rendition is an upload | the view's `event = 'reserved'` predicate; SRS 1.23 states it | `storage-metering.itest.ts` — *"keeps a rendition out of the count and inside the level"* |
| FR-011 | unmet clauses recorded in the SRS rather than left to look built | SRS 1.23, FR-MED-12 and DR-17 | `check:srs`, `check:docs`; and `clauses.md` counts them |
| FR-012 | the chapter states what a delta-summed level costs | chapter §*What a summed delta costs*, with the distribution | `check:fences`, `pnpm build`; the figures are in `figures.ts` |
| FR-013 | the comparison is invokable and exits non-zero on breach | `scripts/reconcile-storage.mjs`, `exitCodeFor` | `storage-reconcile.test.ts` — *"exits non-zero only for an unexplained drift"* |

## The success criteria

| SC | measured | where the number is |
|---|---|---|
| SC-001 | a slot's bytes reach the rollup | `baseline.txt` T025–T029 |
| SC-002 | the rollup read against the raw accumulation | T047 — 276 rows / 5,456 B against 89,823 / 2,874,336 B |
| SC-003 | every scope arm probed by deletion | T046 — eleven arms, nine red, one deleted, one now tested |
| SC-004 | one tenant's bytes stay out of another's figure | `storage-metering.itest.ts`, and T046 arms A7/A8 |
| SC-005 | a slot request survives an analytical outage | T050 — 201 with ClickHouse down, queryable 27 s after restart |
| SC-006 | the comparison against all three stores | `storage-reconcile.itest.ts`, 9 of 9 |
| SC-007 | two kinds on one day sum to the day's total | `storage-metering.itest.ts` — `{'audio':1,'image':2}`, 3 |
| SC-008 | the clause count is published | `clauses.md`, 15 clause-parts |
| SC-009 | the drift from one lost delta, as a distribution | T048 — p50 1,024 B, mean 521,671 B, max 26,214,400 B |
| SC-010 | the CI error set compared per error | T083 |
| SC-011 | the fence chain is zero and the tutorial builds | T074 — `check:fences` REAL EXIT 0, 291 files, 59 chapters |

## The constitution

| principle | engaged how | evidence |
|---|---|---|
| I — tenant isolation | every read scoped; eleven arms deleted one at a time | T046's table; `check-lane-scope` |
| III — two data paths | **a fourth item against the unapplied amendment**: three stores in one function | `gaps.md` 062-4; `docs/05-sad.md` §6 |
| IV — single writer | no second writer added; the compare-and-set at the verdict is unchanged | `media.controller.ts`'s `applied` gate |
| VI — test-verified | coverage REAL EXIT 0, zero threshold errors, three new pins added | `vitest.coverage.config.mts` |
| VII — boring by design | no new dependency, no new service, no new container | 32 dependency entries at the open and 32 at the close |

## What no artifact here discharges

- **DR-17's *weekly*.** No scheduler exists. ADR-28's precedent, recorded in SRS 1.23 and
  `gaps.md` 062-2.
- **FR-MED-12's *visible in the dashboard*.** No dashboard exists; FR-DSH-04/05 are unbuilt.
- **The `deleted` cause.** No producer, because nothing removes a `media_objects` row. The
  signature is written and its caller is the erasure chapter's. `gaps.md` 062-1.
