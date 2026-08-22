<!-- SPECKIT START -->
**CHAPTER 3.11 IS CLOSED.** 117 of 117 tasks, checklist 16/16, tagged
`part3-ch11` at `c7fd20c`, published in both locales, pushed. Its record is
`specs/032-chapter-3-11/` — read `chapter-notes.md` first (what the plan said
against what shipped) and `baseline.txt` for every measurement.

**CHAPTER 3.12 IS SPECIFIED AND PLANNED, "Milestone: the isolation gauntlet"** —
the cross-tenant attack suite against every endpoint (NFR-SEC-09), and the SRS
Phase 2 exit criterion: *"an external developer integrates using only public
documentation, with no assistance"*. Its record is `specs/033-chapter-3-12/` —
read `plan.md` for the eleven phases and `research.md` for R1 to R26, eighteen of
which were measured against a running stack rather than reasoned about.

**Six analysis passes are applied — 56 findings, 6 CRITICAL** — reading, in order,
the documents and the published series, the code, the build gates, the numbers, the
governing documents, and task executability. The fifth found the worst of them: `POST /v1/channels` was about to
accept `type: "private"` while **nothing in the platform reads `channels.type`**, so
FR-CHN-05 is unimplemented and the endpoint would have sold a guarantee the platform does
not keep. The documented enum is now `public` alone, and FR-CHN-03's private half goes to
3.13 with FR-CHN-05.
Three turned up product work rather than corrections: `@Accepts` grows a service
argument (FR-044), because a platform credential was authorized by class and not by
service, so the gateway's credential reached `POST /internal/dispatch/replay`; that
refusal gets its own code, `wrong_credential_service`, so the shipped set is twelve
codes rather than eleven (FR-046, and FR-CHN-07 adds a thirteenth); and compose starts the platform in a CI job of its
own (FR-045), because the sealed package may not start a server and nothing else did.

**Two things the plan found that no document contained.** There is no public
endpoint to create a channel or add a member — `packages/e2e/src/harness.ts` has
said since chapter 2.8 that this is "Part 3's tenancy work", and Part 3 ends at
3.12 — so the exit criterion was unreachable for reasons unrelated to
documentation. 3.12 builds the two endpoints it needs; the rest of FR-CHN and
FR-USR goes to **chapter 3.13**, which means Part 3's milestone no longer sits
last in the part. And the **outbox keeps message text for ever** — `drainOutbox` sets
`published_at` and never deletes, nothing in the api deletes a row from any
table, and the payload copies `data.text`; 286,871 rows in the test lane. That
collides with DR-06, FR-MSG-08, FR-TEN-08 and FR-MOD-06, and the fix is a
one-line prune, not the tenant column an earlier draft proposed (R7, R7a).
Owned by FR-MOD-06's chapter.

All three debts 3.12 inherited are in its scope, and a fourth turned up while
analysing it — **Principle I's lint ban is not in force for any integration test**,
because a second flat-config block for `**/*.itest.ts` replaces the rule instead of
merging with it (R23, FR-043). The plan says how for all four:

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
