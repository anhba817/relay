# Traceability — 051, chapter 4.6, "the rollup nobody read"

**23 functional requirements, 13 success criteria.** Measurements live in `baseline.txt`
under the task id in the second column.

## Functional requirements

| FR | Tasks | Discharged by |
|----|-------|---------------|
| FR-001 | T022–T026, T030 | connection-minutes in both rollups, from `connection_events` |
| FR-001a | T038 | The four tables' row counts published; unpopulated columns present and documented, decided once |
| FR-001b | T017a, T017b | `0007_mv_messages.sql` — built over a source with no producer, deliberately |
| FR-002 | T023, T024 | Close rows only; `ts - duration_ms` recovers the open (measured, T004) |
| FR-003 | T015, T017b | `stored_delta` as signed `Int64`, citing DR-17 rather than deriving it |
| FR-004 | T035 | A day with no activity has no row; the distinction lives in the read |
| FR-005 | T033 | The wrong read shown failing first: `1000 1000 1000` against 3000 |
| FR-006 | T032, T036 | `dailyUsage()` over rollup rows; rows-read published |
| FR-007 | T068a | `git diff` over the quota code and both migrations — empty |
| FR-008 | T039 | The chapter states DR-10 was satisfied by a view nothing read over a table nothing wrote |
| FR-009 | T045 | Three of four dimensions answered; application recorded with its cost |
| FR-010 | T046 | gaps 051 — application attribution, and why it is a constitution argument |
| FR-011 | T051 | SRS revision 1.13 closes Appendix C question 4 |
| FR-012 | T048 | 56 calendar minutes against 0.6513 elapsed, **86×** |
| FR-013 | T060, T062 | DR-09 and DR-10 amended where measurement falsified them |
| FR-014 | T057 | `docs/05-sad.md` §6.2 gains both rollups and the backfill finding |
| FR-015 | T058 | `docs/12` §3's row 7 amended |
| FR-016 | T059 | `docs/12` §7.1 closed — 4.2 built it, §3 recorded it, §7 never knew |
| FR-017 | T069 | 4.2's mechanics, `uniq`'s approximation and Part 3's counters cited, not re-derived |
| FR-018 | T073 | 2,302 prose words, 2 `<Trap>` |
| FR-018a | T067 | Registered in `lib/tutorial.ts`; the build failed first with `Unknown chapter id: 4.6` |
| FR-019 | T077 | 110 → 110 by kind, locale, and both HEAD classes |
| FR-020 | T078 | Eleven gates run; every red diagnosed against T008's opening |

## Success criteria

| SC | Tasks | Result |
|----|-------|--------|
| SC-001 | T030, T036a | Connection-minutes 56 = 56 against the raw computation; the message quantities checked in the corpus window |
| SC-001a | T038 | Four tables' counts published together: 0 / 11,683 / 154 / 64 |
| SC-002 | T036 | 32,778 rows read against the raw table's 32,768 — **the finding, not the confirmation** |
| SC-003 | T048 | 56 against 0.6513, ratio 86, median connection 252 ms |
| SC-004 | T051 | Appendix C question 4 closed in SRS 1.13 |
| SC-005 | T033 | The bare read shown returning `1000 1000 1000`, then 3000 after `OPTIMIZE` |
| SC-006 | T035 | A day with no activity returns no row, asserted |
| SC-007 | T045 | Three of FR-ANL-09's four dimensions; the fourth with its cost |
| SC-008 | T068a | The quota counter unchanged, by diff |
| SC-009 | T058, T059 | `docs/12` §3 row 7 and §7.1 both amended |
| SC-010 | T077 | 110 → 110, delta 0 in every cell |
| SC-011 | T073 | 2,302 words, 2 traps |
| SC-012 | T067 | `pnpm build` exits 0, 120 static pages |

## What nothing discharged

**Nothing.** Every FR and SC has a task and an artifact.

Three carry a qualification, each recorded where it was measured:

- **SC-002 was discharged by failing.** The rollup read more rows than the raw table, which
  is what forced the second rollup. The criterion asked for the figure to be published, and
  it is — including the version that made the design change.
- **FR-001 covers the quantity with a producer.** The other three are FR-001b's, built and
  unpopulated, which FR-001a governs and `gaps.md` 051-1 carries.
- **FR-013's amendments are the SRS's.** Constitution III's conflict is recorded rather than
  amended, because that amendment is the constitution's own — `gaps.md` 051-2.
