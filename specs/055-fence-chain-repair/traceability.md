# Traceability — feature 055

Every requirement and criterion to the tasks and artifacts that discharged it, and **any
discharged in a weaker form than their words suggest**, said so here rather than implied.

## Functional requirements

| id | discharged by | evidence |
|---|---|---|
| FR-001 | phases 3-6, T086 | `282 fenced files replay onto relay-platform across 52 chapters`, EXIT 0 |
| FR-002 | T010, T011 | 110 with the flag, without it and with the leading `--`; `--at` replays separately |
| FR-003 | T042, T054a, T084 | per-target tables in `baseline.txt`, 24 + 12 + 29 measurements |
| FR-004 | T091 | one excursion, 1 → 4, completed inside `sentinel.sql`'s own work |
| FR-005 | T044-T057 | eight bodies, 1,100 lines, from `rework/part3-chM` |
| FR-006 | T029-T043 | 42 hunks re-anchored on the dumped state |
| FR-007 | T058-T085 | 29 appendix hunks, 3,471 lines |
| FR-008 | phase 3, T056 | 11 declared + 4 converted; every listing is a verified claim or a declared not-file |
| FR-009 | T089 | `git diff --stat part4-ch9` empty |
| FR-010 | research R2, T044 | corrected before the work: the appendix cannot introduce a path |
| FR-011 | T011, every repair | `MIRROR` 0 throughout; vi twins matched **by body**, not by line |
| FR-012 | T056, `gaps.md` 055-6 | four exceptions, converted **and** recorded with their price |
| FR-013 | phase 1 | all nine premises re-measured; eight held, T008 did not |
| FR-014 | T008 | resolved, not recorded: `ea0cb513` added `corpus.json` to `.gitignore` |
| FR-015 | T097, `gaps.md` 055-2 | 18 shadows down, ten invisible divergences up |
| FR-016 | T066, `gaps.md` 055-1 | **corrected rather than discharged** — the defect was the applier |

## Success criteria

| id | met | evidence |
|---|---|---|
| SC-001 | yes | the success line, verbatim, not the exit code |
| SC-002 | **pending** | T102 — only observable after the push |
| SC-003 | yes | a planted comment in `catalogue.ts`: 1 problem, EXIT 1, the file named |
| SC-004 | yes | `MIRROR` 0 at every measurement in all four repair phases |
| SC-005 | yes | each of the four classes reported separately at 0 |
| SC-006 | yes | 110 is the highest number in every table; one excursion, 1 → 4 |
| SC-007 | yes, and see below | T042a, T055, T084a — three read-throughs |
| SC-008 | yes, with the increase stated | untitled 360 unchanged; declared 222 → 252, every one recorded |
| SC-009 | yes | the method and every command in `baseline.txt`; the three judgements named |
| SC-010 | yes | zero platform files |

## Discharged in a weaker form than the words suggest

**SC-007 covers the English chapters.** *"Every repaired chapter's prose still describes the
listing beside it"* was read in English and written in English. The Vietnamese chapters carry
the same listings with no introducing sentence, because FR-011 forbids altering translated prose
(`gaps.md` 055-7). The criterion is met for the locale whose prose this feature is allowed to
touch, and not for the other.

**FR-008's "every listing" now includes 30 more declared not-files.** Eleven were prose titles
that named nothing — an unambiguous improvement. Four fence-pairs were real files whose
amendments could not be anchored, and declaring them is a *loss* of verification recorded under
FR-012. The requirement's words do not distinguish the two, and the arithmetic in `gaps.md`
055-6 does.

**FR-016 is not discharged, it is withdrawn.** Its premise was false.

**FR-002 permitted one change beyond the agreed flag.** The applier's `$$` bug was fixed
(`gaps.md` 055-1). It is a correctness fix, not a loosening — the checker now compares what the
fence actually says — but it is a change to a shared gate that no requirement authorised in
advance, and ADR-29 records it for that reason.
