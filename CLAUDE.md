<!-- SPECKIT START -->
**CHAPTER 3.11 IS CLOSED.** 117 of 117 tasks, checklist 16/16, tagged
`part3-ch11` at `c7fd20c`, published in both locales, pushed. Its record is
`specs/032-chapter-3-11/` — read `chapter-notes.md` first (what the plan said
against what shipped) and `baseline.txt` for every measurement.

**NEXT IS CHAPTER 3.12, "Milestone: the isolation gauntlet"** — the cross-tenant
attack suite against every endpoint (NFR-SEC-09), and the SRS Phase 2 exit
criterion: *"an external developer integrates using only public documentation,
with no assistance"*. It has no spec yet; start with `/speckit-specify`.

Three debts 3.12 inherits, all recorded rather than remembered:

1. **`docs_url` resolves to nothing** for `rate_limited` (chapter 3.8) and
   `quota_exceeded` (3.10, 3.11). 3.11 declined to add a third instance. A
   chapter whose exit criterion is "integrates on public documentation alone"
   cannot ship with error codes whose documentation link 404s.
2. **Feature 030's guard watches five tables and none of the four usage tables**
   — `usage_periods`, `usage_active_users`, `quota_notifications`,
   `usage_connections`. Extending it is NOT a one-line array change: the refusal
   message interpolates `OLD.id` and `usage_periods` has no `id` column. Owned by
   whichever feature next touches `packages/test-harness/`. See R5a in
   `specs/032-chapter-3-11/research.md`.
3. **`limits.itest.ts` binds a fixed api port** (`?? 4124`) and carries the
   lingering-child fault that broke `session.itest.ts` in 3.11 — a previous run's
   child still holding the port, and the health check answered by an api serving a
   different environment. Green today; the fix is a random high port, as
   `session.itest.ts` and `meter.itest.ts` now use.

**THE CHAPTER CYCLE THIS PROJECT USES**, in order: `/speckit-specify` →
`/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` (repeatedly) →
`/speckit-implement` (once per phase). 3.11 ran SEVEN analyze passes and each read
a different surface — documents against each other and against the published
series, the code, the build gates, the numbers, the governing documents, task
executability, and the previous pass's own edits. Seventy findings, three
CRITICAL, all three in the first three passes; the seventh found only the sixth's
mistakes, which is what running out of reading looks like.

**AND SEVEN THINGS IMPLEMENTATION FOUND THAT READING COULD NOT.** Budget for
this: a twenty-run battery is an hour and it earned it twice. Two of chapter
3.10's tripwires (one unscheduled), three defects in the battery (two older than
the chapter), one plan decision corrected by a benchmark, and one comment in a
shipped chapter that had quietly stopped being true.

**COMMIT EACH PHASE.** A bad regex in 3.11's traceability pass broke 36 files;
because everything through the previous phase was committed, the repair was one
`git checkout` and five minutes.
<!-- SPECKIT END -->
