# Traceability — feature 054, chapter 4.9, "Milestone: the meter agrees"

Every requirement against the task that discharged it and the artifact that carries it.
**Requirements discharged in a weaker form than their words suggest are marked and explained** —
a table of ticks with nothing qualified is a table nobody checks.

---

## Functional requirements

| id | discharged by | artifact | note |
|---|---|---|---|
| FR-001 | T030, T034 | `relay-platform/scripts/integration-gate.mjs` | 54 suites executed of 54 present, printed per lane. **The reconciler's suite was already reached** — the requirement's own premise was falsified at phase 4 |
| FR-002 | T035 | `reconcile.itest.ts`, gate run | `pct <= threshold` → `pct <`: exactly one assertion of 676 moved, the gate exited 1 and named `src/metering/reconcile.itest.ts`. **Scoped to the step, not the workflow** (FR-002a) |
| FR-002a | T032c, ADR-27 | `gaps.md` 054-1 | **Recorded, not built.** The design — a per-kind baseline in `fences/baseline.json` — was written and refused by this environment's guard as a CI bypass. The claim is scoped to the step for exactly this reason |
| FR-003 | T031 | `request-log.itest.ts` | the suite spawns its own ingester; 5 red → 5 green |
| FR-004 | T031, T032 | both vitest configs | six failures → zero, by fixing causes rather than excluding suites |
| FR-004a | T032a, ADR-28 | `docs/05-sad.md`, `docs/06-adr-deep-dives.md` | **Decided as a recorded absence.** No sixth relay was built, and the reversal condition is stated |
| FR-005 | T025, T027 | `corpus.mjs`, the reconciler run | 121,057 in one tenant-period, verdict `pass` |
| FR-006 | T020, T021, T024 | `corpus.mjs`, `reconcile-usage.mjs` | both counter tables written; `--database` addresses a corpus |
| FR-006a | T028a | `load-analytics.mjs --clean` | scoped delete, `system.mutations` polled, count asserted 0 |
| FR-006b | T021, T026b | `corpus.mjs` | `usage_active_users` written and asserted before any verdict |
| FR-006c | T017 | `reconcile.ts`, `reconcile.test.ts` | **stronger than specified**: the guard is inside `reconcile()`, so no caller can skip it, and the script calls the same exported functions at parse time |
| FR-007 | T013, T023, T039 | `smallestExpressibleDrift`, the harness report, `docs/13` | every figure carries its volume and the smallest drift expressible at it |
| FR-007a | T027, T039a | `docs/13`'s results table | four quantities with a **standing** column; three of four passes are not evidence |
| FR-008 | T043 | `docs/13` | the quantity is named — messages sent — and the three excluded ones each carry their reason |
| FR-009 | T040 | `docs/13`'s drift table | 121 passes and 122 breaches, in both directions, through the real job |
| FR-010 | T042, T045 | `docs/13-metering-measurement-2026-09-17.md` | on `docs/11`'s model, eight sections, the method stated rather than borrowed |
| FR-010a | T042a | `docs/13` | *"what went wrong while measuring"* and *"what this left in the lane"*, both present |
| FR-011 | T041 | `docs/13` | window 2026-08-01…2026-09-01; the TTL cut is at 2026-06-19, **43 days before the window opens**, measured from the store |
| FR-012 | T055 | the chapter's closing sections | what movement IV established, amended, and defined without building |
| FR-013 | T065 | `gaps.md` | 8 new, 14 carried and re-measured, 2 closed, 1 corrected twice |
| FR-014 | T013, T039 | `docs/13`, the harness report | no figure is published without its volume |
| FR-015 | T056 | the chapter | 4.5–4.8 are cited, not re-derived |
| FR-016 | T060 | `relay-tutorial/lib/tutorial.ts` | registered as `4.9`; the anchor was checked for uniqueness before the edit |
| FR-017 | T054, T059 | `page.mdx` | **2,666 prose words**, 2 `<Trap>`, 1 `<Why>`, 1 `<Checkpoint>` |
| FR-017a | T059a | `gaps.md` 054-5 | the floors are read as applying to milestones; the two published ones are a gap, not a category the document never covered |
| FR-017b | T057 | `figures.ts` | 3 figures, one in the first half and two in the second; every source in `figures.ts`, every one passed as `code=` |
| FR-018 | T063 | close-out record | the fence delta reported by kind and locale, with the third APPLY bucket named |
| FR-019 | T047d, T048, T048a, T049 | `docs/07` §6, `docs/12` §2.3 and row 10, SRS 1.16 | four documents amended where this feature falsified them |
| FR-020 | T055a | the chapter's `<Checkpoint>` | one sentence, supported by the test and informed by the document, and **it says how often anybody checks** |

## Success criteria

| id | met? | evidence |
|---|---|---|
| SC-001 | **partially** | the gate goes red for a planted drift and the failure names the reconciler. **At the workflow level it does not**, and FR-002a records why — the claim is scoped to the step |
| SC-001a | yes | the permanently-red workflow is recorded with its count, its step and its options (ADR-27, `gaps.md` 054-1) |
| SC-002 | yes | 54 of 54 suites reported per lane by the gate itself |
| SC-002a | yes | both interpolated values refused, both refusals tested and run red |
| SC-003 | yes | unexplained reds: **0**. Six were resolved by cause, not by exclusion |
| SC-003a | yes | the schedule is decided and recorded (ADR-28) |
| SC-004 | yes | 121,057 messages in one tenant-period, above the 100,000 the criterion names |
| SC-005 | yes | the verdict is `pass` — not `no-data`, not `not-comparable` |
| SC-005a | yes | the cleanup returns the store to its opening counts, verified by count |
| SC-006 | yes | the figure carries both row counts, the volume and the smallest expressible drift |
| SC-006a | yes | the per-quantity table carries a standing column |
| SC-007 | yes | at the bound: pass; one unit past: breach — in both directions |
| SC-008 | yes | the quantity named, the three exclusions each with a reason |
| SC-009 | yes | the document's commands run as written |
| SC-009a | yes | both precedent sections present |
| SC-010 | yes | the chapter's close records what movement IV built, amended and deferred |
| SC-011 | yes | `gaps.md`, with every carried item re-measured or explicitly carried unchanged and said so |
| SC-012 | yes | 2,666 prose words, inside 2,000–4,000 |
| SC-012a | yes | the floor decision recorded with both measurements |
| SC-012b | yes | 3 figures, at least one per half |
| SC-013 | yes | registered, and `pnpm build` renders the chapter |
| SC-014 | yes | fence delta reported by kind and locale |
| SC-015 | yes | the one-sentence answer is supported by a figure published in the same chapter |

## What nothing discharged

- **FR-ANL-06's schedule and alert.** Neither is built; both are recorded (ADR-28, `gaps.md`
  054-2). The clause's `T` letter is discharged for the **comparison** only, and SRS 1.16 says
  so in those words rather than letting "discharged" cover the sentence.
- **The constitution III amendment.** Written in full and not applied
  (`constitution-amendment.md`, `gaps.md` 054-3). Three items now stand against one principle.
- **The workflow's colour.** FR-002a is recorded rather than built, and the reason is in
  `gaps.md` 054-1.

## Where a requirement was met in a stronger form than written

- **FR-006c** asked for validation *"before the reconciler is called"*. It is inside
  `reconcile()`, where no caller can skip it, and exported so the script can also refuse at parse
  time and name the flag. One rule, two call sites.
- **FR-004** asked for the six reds to be *"resolved or recorded"*. All six are resolved, and
  fixing one of them turned on three isolation-gauntlet attacks that had been reporting green
  without running — which no requirement had asked for because nobody knew.
