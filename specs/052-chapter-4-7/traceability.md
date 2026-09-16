# Traceability — chapter 4.7, "the job that checks the meter"

Every requirement and success criterion, the tasks that discharge it, and the artifact a
reader can open. Nothing below is claimed on the strength of a task being marked complete;
each row names something in the tree or a figure in `baseline.txt`.

## Functional requirements

| ID | Discharged by | Artifact |
|---|---|---|
| FR-001 | T021–T031 | `services/api/src/metering/reconcile.ts` — `reconcile()` takes one `environmentId` and one `period` and returns four `ReconcileRow`s |
| FR-002 | T014–T020, T021–T031 | The verdict half (`verdictFor`, `differencePct`, `exitCodeFor`) runs with no store, no database and no broker: `reconcile.test.ts`, 17 tests, Docker-free. The gathering takes its two handles as arguments |
| FR-003 | T024, T029 | `ReconcileRow.operationalSource`; asserted in `reconcile.itest.ts` *"reports four quantities, each with its operational source named"* |
| FR-004 | T016, T028 | `Verdict` carries `no-data` and `not-comparable`; `verdictFor` decides from presence before any arithmetic |
| FR-005 | T024, T029 | The report carries `analytical`, `operational`, `operationalSource` and `differencePct` beside the verdict — a breach names which side was absent, or by how much they differ |
| FR-006 | T002, T041 | SRS 1.14 names `usage_periods` for messages; `baseline.txt` T041 carries the measurement (19,012 vs 18,962, 0.2630%) and the attribution of every disagreeing tenant |
| FR-007 | T041, T042a, phase 6 | Per quantity: `usage_periods` for messages and connection-minutes, `usage_active_users` for active users, **nothing** for stored count. All four in SRS 1.14 and in the chapter |
| FR-008 | T036 | `exitCodeFor` in `reconcile.ts`, four unit tests, called by `scripts/reconcile-usage.mjs`. Measured through the script: exit 1 planted, exit 0 removed |
| FR-009 | T015 | `RECONCILE_THRESHOLD = 0.001; // 0.1%, SRS FR-ANL-06`, with a unit test pinning the value and one driving an override |
| FR-010 | T032, T033 | `reconcile.itest.ts` *"raises for that tenant and that quantity"* and *"does not raise once the drift is removed"* |
| FR-011 | T017, T034 | Four boundary points at unit scale and the same four at integration scale, 99,900 / 99,899 / 100,100 / 100,101 |
| FR-012 | T045, T046 | 50 real lane environments at 100,000 connection-minutes each, matched exactly; the smallest breaching drift walked up one unit at a time at five volumes |
| FR-013 | T041, T042a, T043, T044 | All four obstacles in `baseline.txt` phase 5 and in the chapter, each with its own cause |
| FR-014 | T042b, T049, T052 | The chapter publishes no agreement percentage for the three unreachable quantities; SRS 1.14 states where the bound cannot be met |
| FR-015 | T051 | `gaps.md` — 047-1 / 048-1 closed by amendment, both numbers re-measured and both moved |
| FR-016 | T052, T055, T056 | SRS 1.14; `docs/05-sad.md` §6.2 (the reconciler, and the rollup-TTL sentence corrected); `docs/12` §3 row 8 |
| FR-017 | T052 | FR-ANL-06's row in `docs/04-srs.md`, amended in four directions |
| FR-018 | T054 | `docs/12-part-4-structure.md` §3 row 8, first column untouched |
| FR-019 | T061 | The chapter cites 4.2's rollup, 4.6's two-rollup argument and `docs/12` §4's two-counters argument; it re-derives none of them |
| FR-020 | T060 | `relay-tutorial/lib/tutorial.ts` id `4.7`; `pnpm build` exits 0 with 121 pages |
| FR-021 | T059, T064 | 2,265 prose words outside code fences; 2 `<Trap>` boxes |
| FR-022 | T068 | 110 at the close against 110 at T006's opening — APPLY 74, HEAD 36, delta 0 |
| FR-023 | T069 | Eleven gates run; every red diagnosed by running the suites directly |

## Success criteria

| ID | Evidence |
|---|---|
| SC-001 | `scripts/reconcile-usage.mjs` against a real environment prints four quantities with both totals, the percentage and the verdict; `baseline.txt` T036 carries both runs |
| SC-002 | `reconcile.itest.ts`: breach at 1.0000% with `exitCodeFor` 1, then pass at 0.0000% with `exitCodeFor` 0 |
| SC-003 | `it.each` over `[99_900 pass, 99_899 breach, 100_100 pass, 100_101 breach]`, plus the same four in the unit suite |
| SC-004 | `reconcile(db, store, { environmentId, period })` is called directly by 16 integration tests |
| SC-005 | *"returns the same report twice, because it writes nothing"* |
| SC-006 | *"calls a tenant with nothing on either side no-data, not agreement"* |
| SC-007 | *"reports four quantities, each with its operational source named"*, and the gap to the alternative published in `baseline.txt` T041 and in SRS 1.14 |
| SC-008 | Four obstacles, four separate causes, `baseline.txt` phase 5 — the missing producer, connection-minutes over two populations, `uniq`'s cliff, the retention boundary |
| SC-009 | The resolution table at five volumes, measured against the real job on 50 real environments |
| SC-010 | `gaps.md` 047-1 / 048-1, closed with re-measured numbers: the `uniq` cliff at 65,536 and the retention gap as a curve rather than 0.49% |
| SC-011 | 110 → 110, delta 0, with the two HEAD classes split (25 `differs at line`, 11 `does not exist`) |
| SC-012 | 2,265 words, inside 2,000–4,000; 2 Traps |
| SC-013 | `pnpm build` exit 0, `/part-4/chapter-07/the-job-that-checks-the-meter` in the route list |

## What nothing discharged

**Nothing in this list is undischarged.** Two things are discharged in a weaker form than the
words suggest, and both are named where they are claimed rather than here:

- **FR-008's "raise"** is an exit code. There is no alerting integration in this platform, and
  the chapter and `gaps.md` 052-5 both say what a real one would cost instead of implying the
  exit code is one.
- **FR-012's "0.1% figure"** is a resolution rather than an agreement. No agreement figure was
  measured, because three of the four quantities cannot reach the bound for reasons that are
  not defects — which is FR-014, and the reason FR-012 is discharged as *"the smallest drift
  the threshold detects at a stated volume"* rather than as a percentage.

**AND ONE REQUIREMENT WAS DISCHARGED BY A DOCUMENT RATHER THAN BY CODE.** FR-017 asks that
FR-ANL-06 be amended where the measurements show it cannot hold. It was — and the amendment is
the whole of what this chapter could do about three of its four obstacles.
