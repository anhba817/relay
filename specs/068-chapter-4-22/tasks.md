# Tasks — chapter 4.22, "★ Milestone: the Priya test"

**Feature**: `specs/068-chapter-4-22/` · **Plan**: [plan.md](./plan.md) ·
**Research**: [research.md](./research.md) · **Contract**: [contracts/journey.md](./contracts/journey.md)

**A milestone appears after all the work it verifies** (`docs/12` §5 rule 4). Where a
task would build product surface, it says what that costs and why it is still the
answer — or it does not build it.

---

## Phase 1: Baseline

- [ ] T001 Pin the lane environment in `specs/068-chapter-4-22/baseline.txt`: `RELAY_POSTGRES_PORT=15432`, the composed services that must be up, and the row counts (`channels`, `users`, `messages`, `media_objects`, `audit_log` user targets, `connection_events`). **Record the counts beside every later timing** — they are part of the instrument.
- [ ] T002 Record every lane's opening exit code in `specs/068-chapter-4-22/baseline.txt`, **each with its `Cached:` line and elapsed time, or under `--force`**. Chapter 4.20 and 4.21 both saw `pnpm test` answer **EXIT 0 in 3 seconds with every counted line present** and `Cached: 9 of 13` — nothing ran. **`turbo run lint` is not a task**; the root task is `//#lint:root` and `pnpm lint` is the form that runs it.
- [ ] T003 Run all six tutorial gates from `relay-tutorial` and record each counted line: `lint`, `build`, `check:docs`, `check:srs`, `check:figures`, `check:fences`. **Assert the line, not the exit code** (055-4). `check:fences` was **0 across 64 chapters** at 4.21's close.
- [ ] T004 Capture the CI error-set baseline for the per-error comparison at close (SC-010): `gh run view <last green run> --log-failed`, `##[error]` lines only, uuids normalised. 4.21's baseline and its run were **both empty**, and the record says plainly that an empty diff between two green runs carries nothing — **the comparison earns its cost when the colour is useless**.
- [ ] T005 **Count the fence bill now, derived from what the tasks touch rather than remembered** (4.15's rule, 4.21's correction). `research.md` R6 has the table; re-derive it with `grep -rl 'title="[^"]*<file>"' app/ fences/` and expect it to be short, because every file it misses arrives from a repair made after the list was written. **4.21's bill said six files and the chain charged six, and they were not the same six.**
- [ ] T006 **Re-measure `research.md`'s figures before trusting them**, in `specs/068-chapter-4-22/baseline.txt`: the 500 on `GET /v1/channels/{externalId}`, the 200 on the uuid, the same-channel re-POST, and `0 of 41,766 channels with a uuid-shaped external_id`. They were taken on 2026-10-05 and the lane moves.

---

## Phase 2: The decisions (BLOCKING — nothing in Phase 3 starts until these are recorded)

- [ ] T007 **Decide R2's option** in `specs/068-chapter-4-22/baseline.txt`, with all four priced and **the losing argument written out**. `research.md` R2 has the table: **A** a new route (~91 fence pages, and the four lists a route joins), **B** a query parameter (there is no channel list route to hang one on), **C** `:channelId` resolves a uuid or an external id (~65 pages, no new route), **D** amend FR-CHN to record the idempotent create as the supported resolution (0 pages).
  **TWO RULES POINT AT D AND ONE CONSEQUENCE ARGUES AGAINST IT.** Constitution VI: *new behaviour without a requirement gets a requirement first.* `docs/12` §5 rule 4: *a milestone appears after all the work it verifies.* Against: D leaves a support engineer performing a **write** to perform a **read**, which is the thing `docs/03` says external ids exist to avoid. **Name which rule loses.**
- [ ] T008 **Decide whether this chapter needs an ADR**, and record the reasoning either way. Probably yes under A or C — a second key space on an existing route is an architecture decision with a reversal condition — and probably no under D. **Chapter 4.21's plan predicted no ADR and was wrong**, so a prediction is worth nothing without the check. Constitution VII requires one for every architecture decision.
- [ ] T009 **If T007 chose A or C, decide how the resolution is tenancy-scoped**, and say whether by construction or by a predicate somebody wrote. `Repository`'s constructor requires an `environment_id`, which is how six of seven stores in 4.21's traversal were scoped without anyone remembering. **If the answer is "a predicate", T026 must delete it and re-run** — 4.21 found three of four scoped arms invisible to a single-mutation probe.
- [ ] T010 **Decide whether the image→erasure arrow is added to `priya.itest.ts` or to `integrate.itest.ts`**, and record the bill. The image path already exists in `integrate.itest.ts` (**5 fence pages, 5 appendix hunks, 1,677 lines**); a new file costs **0 pages** and must build its own image. **4.17 measured what touching a published file costs** when a formatter turned six edits into 23 hunks.
- [ ] T011 **Decide whether §7.6 is this chapter's**, in `specs/068-chapter-4-22/baseline.txt`. It records that the SRS phase table disagrees with itself over FR-DSH and FR-EMJ — **which are Part 5's** — but this is Part 4's last chapter and the one that reads §7.3 hardest. **Record a decision rather than leaving the task unticked**, which is what 4.21 did with its ADR question.
- [ ] T011a **Decide what to do about the Stage 6 join**, in `specs/068-chapter-4-22/baseline.txt`. `docs/03` Stage 6 names a join — audit entry to request-log row, by request id — that **no query on either side supports**. It is Stage 2's shape a second time: a journey names a capability, no chapter owned it, no clause carries it. Three options: **(a)** publish it as a limit and have Priya's tool page both logs, **(b)** add a `request_id` filter to one or both readers, **(c)** amend `docs/03` to describe the paging. **Price (b) before choosing** — `request-log.schema.ts` and `audit.schema.ts` are both fenced, and a milestone that adds two filters is building, not verifying.
- [ ] T011b **Decide whether this chapter closes constitution VI's third bullet or carries it again with a reason.** It gates releases on the cross-tenant suite, a dependency vulnerability scan and an OWASP Top 10 scan; **two of the three do not exist anywhere in the workspace** and have been carried since before Part 4. **A milestone is the release gate's own shape**, which makes this the chapter where carrying it again needs an argument rather than a line in `gaps.md`.
- [ ] T012 **Check T007's premise by reading, not by grepping.** Open `services/api/src/channels/channels.controller.ts`, `channels.schema.ts`, `channels.service.ts` and the repository method behind `GET /v1/channels/:channelId`, and confirm what the chosen option actually costs. **065's T007 said fourteen sites and the real number was five, because a grep counts mentions.** If the option is D, this task confirms there is nothing to open and says so.

---

## Phase 3: User Story 1 — Priya's Tuesday, executable (P1) 🎯 MVP

**Goal**: one test that performs all six stages in order against the deployed
containers, through the published API only.

**Independent test**: boot the stack, run the sealed suite, and read the six stages
in order with no database access.

- [ ] T013 [US1] **Write the one assertion that is red today, first**, in `relay-platform/packages/outsider/src/priya.itest.ts`: an order number nobody used must produce a refusal that names its cause. **It is a 500 today** — measured — and it is the only assertion in this file that can fail before the chapter starts. Everything else in Phase 3 is green-on-arrival and proves nothing about the fix.
- [ ] T014 [US1] Create `relay-platform/packages/outsider/src/priya.itest.ts` with the sealed package's preamble: `RELAY_API_URL`, `RELAY_WS_URL`, `RELAY_DEMO_CREDENTIAL`, and a local `required()`. **Duplicate the six lines rather than extract them** — `integrate.itest.ts` is 1,677 lines across 5 fence pages and editing it to save six lines is the wrong trade (R1). **If the duplication grows past a dozen lines, extract and pay the hunks.**
  **AND THIS IS THE SECOND FILE THAT PACKAGE HAS EVER HAD, WHICH CHANGES WHAT AN ASSERTION MEANS (R9).** Measured: two files in that config run **concurrently** — 6.01s of tests in 3.10s of wall clock — and `ci.yml:355` seeds **one** `RELAY_DEMO_CREDENTIAL` for the whole run, so both files address one tenant's channels, users, quota, audit log and request log. **Every assertion in this file must be scoped to a fixture this file created.** Setting `fileParallelism: false` is refused: it makes the package slower for every future file to avoid writing one predicate.
- [ ] T014a [US1] **Name this file's fixtures so they cannot collide with the neighbour's**, and record the convention in `specs/068-chapter-4-22/baseline.txt`. `integrate.itest.ts` uses `ana`, `rejectId` and similar; this file prefixes every external id it mints with a per-run token. **A collision here is not a failure, it is a pass for the wrong reason** — two tests moderating the same user look exactly like one test working.
- [ ] T015 [US1] **Stage 1 — the ticket.** Create a channel under an order-number `external_id` and two users under customer-supplied ids, each in one call. Assert each is reachable by the identifier the customer chose, **or record which is not** — that is Stage 2's subject and the asymmetry is the finding.
- [ ] T016 [US1] **Stage 2 — locate**, per T007's decision. Assert the conversation is reached from the order number alone **without the caller holding a mapping**, and pair it with T013's refusal. **If T007 chose D, this stage asserts the re-POST and the chapter publishes the write-to-read as a limit** rather than hiding it behind a helper.
- [ ] T017 [US1] **Stage 3 — the conversation**, built from outside. Two participants with **user tokens**, not the application key: a send naming a `person` is refused with *"an application credential may send only as a bot user; name one in `user`"* — measured during planning, and it is why Priya's key cannot create the dispute she investigates.
- [ ] T018 [US1] **Stage 3 — reconstruct.** Edit the decisive message, moderator-delete the abusive one, then assert from the record alone that three outcomes are distinguishable: **never sent, sent and deleted, sent and edited**. The edited message yields both texts and both instants in order. **The eleven-minute interval is not testable**; assert that the instants differ and which came first, which is the property the dispute needs.
- [ ] T019 [US1] **Stage 4 — judge.** Assert every instant in the record is **UTC, RFC 3339, with millisecond precision** — CON-04's three properties, read off the clause rather than remembered as two. **This is the only stage with no behavioural assertion**, and saying so is better than inventing one — `docs/03` says Relay's job here is to stay out of the way.
- [ ] T020 [US1] **Stage 5 — act.** Assert the moderator's deletion reaches a connected socket, the banned user is refused **both** connect and send, and their history survives. Three assertions, because FR-USR-06 says *preventing connection and message send while preserving history* and a ban that only blocks one of the two passes a weaker test.
- [ ] T021 [US1] **Stage 6 — record**, and the assertion is narrower than the journey's sentence because the platform is. Assert the audit entry for that deletion **carries** the `request_id` the caller was given, found by paging the log and matching. Then erase a participant and assert the receipt names each store.
  **SCOPE THE READ TO THIS TEST'S OWN ACTION AND TARGET (R9).** The audit query accepts `action`, and the target id is one this test minted — so the entry is found by filtering on action and matching the target, never by position and never by a count. **`integrate.itest.ts:1224` issues a moderator `DELETE` with the same credential, concurrently**, and writes an entry into the same tenant's log while this assertion runs.
  **NEITHER LOG CAN BE QUERIED BY `request_id`, WHICH T011a DECIDES WHAT TO DO ABOUT.** Measured: `audit.schema.ts` filters on `cursor`, `limit`, `action`; `request-log.schema.ts` on `from`, `to`, `cursor`, `direction`, `limit`, `endpoint`, `status`. **Both rows carry the id and neither surface accepts it.** So `docs/03`'s *"the request id is what joins an entry to the request log's row for the same request"* describes a join a customer's tool must do by paging both logs. **Do not write an assertion that implies a filter exists.**
- [ ] T022 [US1] **Annotate every assertion's margin with the clause and the chapter it verifies**, per `contracts/journey.md`. `tuan.itest.ts`'s rule: *remove that chapter's work and a named assertion here fails.* **A margin nobody has falsified is a comment**, which is what T027 exists to fix.
- [ ] T023 [US1] Run the sealed suite and record the counted line: it was **21 of 21** at 4.21's close. **`pnpm test:outsider`**, with the three environment variables exported and the api image rebuilt first.
  **THAT IS THE FORM `ci.yml:360` RUNS**, and `vitest.coverage.config.mts:97` says so in as many words: *"`pnpm test:outsider` is the way in."* A first draft used `pnpm --filter @relay/outsider test:integration`, which works and is not what CI does — 055's rule is to read the commands off `ci.yml` rather than off memory.
- [ ] T024 [US1] **Check FR-011 per action**: re-run `integrate.itest.ts` **unedited** and the api integration lane, and record both. **Run the sealed suite at least three times** — the two files run concurrently against one tenant (R9), so a collision is a race and one green run is not evidence. 045's rule: *twenty runs is a sample of the lane's timing and a very thin sample of its failure modes.*

---

## Phase 4: User Story 2 — the arrow nobody walked (P2)

**Goal**: carry an image across Phase 3's fifth arrow, or record which segment could
not be and why.

**Independent test**: upload, scan, send, fetch the signed bytes, erase the uploader,
and assert the object is gone and the message still reads.

- [ ] T025 [US2] **Carry an image from upload to erasure**, in the file T010 chose. The first four arrows exist — `integrate.itest.ts` has carried one image from slot to delivered bytes since 4.17. Add: erase the uploader, then assert **(a)** the signed URL no longer serves the object, **(b)** the renditions are gone, **(c)** the receipt names `media_objects` with a count, and **(d)** the message carrying the attachment **still reads as a message**.
  **(d) IS THE ONE A READER WILL NOT PREDICT** and it is `docs/07` row 23's own clause one erasure later: a rejected upload renders as rejected, not broken — and an erased attachment must not render as broken either.
- [ ] T026 [US2] **If T007 chose A or C, probe the new resolution's tenancy arm** by deleting it and re-running both the sealed suite and the gauntlet, and record which turn red. **When an arm turns nothing red, the answer is the test that makes it visible, not the deletion that makes it honest** — 4.21 wrote two tests for exactly that and found a third arm genuinely redundant.

---

## Phase 5: User Story 3 — the verdicts (P3)

**Goal**: a verdict per Journey 3 stage and per Phase 3 exit clause, including the
ones that cannot be met.

- [ ] T027 [US3] **Falsify the margin by reverting the MECHANISM, not the chapter** (SC-002). Three surgical edits, each applied alone, the sealed suite run, the named assertion recorded, and the edit restored:

      4.18   `repository.ts:3034`  `recordAction` — make it a no-op
             -> Stage 6's audit assertion must fail
      4.19   `repository.ts:5882`  the `insert(messageEdits)` inside `deleteMessage`
             -> Stage 3's "the text a deletion destroyed" assertion must fail
      4.21   `users.controller.ts:160`  `@Delete(":externalId/data")` — remove the route
             -> Stage 6's receipt assertion must fail

  **`git revert <tag>` WOULD NOT HAVE WORKED AND WOULD HAVE LIED.** A tag names ONE commit — the tip — and a chapter is several: measured, **4.18 is 7 commits, 4.19 is 3, 4.21 is 5**. Reverting 4.21's tip reverts `test(erasure): the media branch…`, a test-only commit whose removal turns **nothing** red in the sealed suite, so the margin's claim would read as FALSE when it is true. **A probe that goes green for the wrong reason**, which is the mirror of 4.21's payload that went red for the wrong one.
  **AND THE RANGE FORM CONFLICTS**: `git diff --name-only part4-ch17..part4-ch18` and `part4-ch18..part4-ch21` share **10 files**, `repository.ts` and `schema.ts` among them. Later chapters are built on top. **The arm probe is the precedent** — 4.21 deleted one predicate at a time and restored it, and that is what this task does.
- [ ] T028 [P] [US3] Write `specs/068-chapter-4-22/clauses.md`: Journey 3's **six stages** and SRS §7.3 Phase 3's **three clauses**, each **demonstrated / met / unmet by decision / unreachable** with where. **State the count of demonstrated stages as a number** (SC-007).
- [ ] T029 [US3] Record in `clauses.md` that Phase 3's first clause — *"metered usage reconciles … for 7 consecutive days"* — **cannot be met**: the comparison runs on every push (4.9) and the seven days need a scheduler ADR-28 declined to build. **The sixth clause bounded by that absence**, after FR-ANL-06, DR-17, FR-MOD-03's year, FR-MOD-06's sweep and FR-MOD-04's thirty days.
- [ ] T030 [US3] **RESOLVE the `docs/07`-versus-§7.3 contradiction — naming which document wins — and amend the other.** Recording it is not enough, because the two define Phase 3's exit as different things and this chapter's status depends on which:

      docs/07 Rule 2   "the journeys are the milestones … they are the SRS phase exit
                        criteria. A reader who passes the Tuan test has built Phase 1,
                        DEFINITIONALLY."    -> passing the Priya test IS Phase 3
      SRS §7.3         Phase 3 = metering reconciles within 0.1% for 7 consecutive days;
                        an image survives upload -> … -> erasure.  Journey 3 is NOT NAMED

  **UNDER RULE 2 THIS CHAPTER FINISHES PHASE 3. UNDER §7.3 PHASE 3 CANNOT BE EXITED AT ALL**, because its first clause needs a scheduler ADR-28 declined to build (T029). **They cannot both be the criterion.** §7.6's own instruction is *amend the clause rather than diverge from it*; the precedent is FR-RTM-09, FR-RTM-10 and 043's FR-016.
  **AND THIS WAS FOUND AT ANALYSIS PASS 3, NOT PASS 1** — because §7.3 and `docs/07` Rule 2 were each read in a different pass and never beside each other. *Read the clauses, not the identifiers*, and read them on the same desk.

---

## Phase 6: The probes

- [ ] T031 Run `python3 specs/045-part-3-rework/check-lane-scope.py` and record its **counted line**, not its exit code. It was **78 integration files, 0 unscoped reads, 10 of 10 controls firing** at 4.21's close; this chapter adds one file.
  **AND RECORD THE BOUND ON ITS ZERO, BECAUSE THIS CHAPTER IS OUTSIDE IT.** The checker globs `packages/*/src/**/*.itest.ts`, so it **reads** `priya.itest.ts` — and it scans for **SQL table reads**. The sealed package talks HTTP and contains no SQL, so its zero says nothing about R9's hazard. Its own last line already says *"SQL text only — a scope applied in JavaScript is invisible to it"*; this is that blind spot one transport further out. **A zero from an instrument is a claim about the corpus only if the instrument can be shown to have read the thing you care about.**
- [ ] T032 **Re-measure the coverage pins this chapter's edits could move**, in `relay-platform/vitest.coverage.config.mts`, **after** the fence chain is at zero. `packages/outsider` is excluded from the coverage lane, so a test-only chapter may move nothing — **confirm that rather than assume it**, and if T007 chose A or C the channels files are in the population.
- [ ] T033 **Probe the pins both ways through `pnpm coverage`**, not a filtered `vitest run`: a key matching no file must be silent and an impossible pin on a real file must fire. **4.21's probe caught its own pin as a side effect** — `erasure.ts` measured 81.81% where 100 was assumed, and a pin below the real number is as silent as a pin on a file that does not exist.
- [ ] T034 **Re-run `check:fences` after any source edit and after the ratchet**, even when nothing changed. **23 pages publish `vitest.coverage.config.mts`** and 4.21's chain went red there exactly as predicted; the control is what tells a clean chain from an unchecked one.

---

## Phase 7: The documents

- [ ] T035 **Read FR-CHN-01, FR-CHN-02 and FR-CHN-08 before editing any of them**, and record what the reading found — **including *nothing to amend* if that is the answer**.
- [ ] T036 Read the clauses **beside** them while `docs/04-srs.md` is open. 4.21's T041 found FR-MOD-03 one row above FR-MOD-04 and in direct tension with it, which nobody had written down; 065's T042 found FR-MSG-10 two rows from the one it opened the file to edit.
- [ ] T037 Amend the **FR-CHN** group per T007: the lookup this journey needs and no clause carries. **Name the journey as the driver**, because constitution VI says new behaviour gets a requirement first and this requirement exists for Priya.
- [ ] T038 Amend **SRS §7.3** with a verdict per Phase 3 exit clause, and resolve the Rule 2 disagreement T030 recorded.
- [ ] T039 Add revision row **1.29** to `docs/04-srs.md`, stating what the chapter demonstrated and what it could not. **Newest LAST** — `check-revision-order` caught 1.28 inserted before 1.27 on the first run after the edit.
- [ ] T040 **If T008 decided an ADR is needed, write it into BOTH homes** — the summary in `docs/05-sad.md` and the argument in `docs/06-adr-deep-dives.md`. 4.5 found an ADR lives in two documents and ten passes amended only the summary. **If no ADR, record that as DONE with the reason.**
- [ ] T041 Amend `docs/05-sad.md` where this chapter changes what a section claims — **and check every sentence in the section you edit**. 4.21 found three of four erasure sentences false in sections a task naming one would have reached one.
- [ ] T042 Amend **both** copies of the Part 4 table — `docs/12-part-4-structure.md` **row 23** CLOSED and `docs/07-tutorial-plan.md` **row 23** SHIPPED. **Match on the title, not the number**: `docs/07` holds two rows numbered 23, and row 23 is chapter **4.22**.
- [ ] T043 [P] Sweep `docs/` for feature-local ids **both ways**: diff-scoped and tree-wide, every hit classified. **Use `git diff <tag> -- docs/`, not `<tag>..HEAD`** — the two-dot form reads committed state and reported a confident **0** for 4.21 while two `FR-014`s sat in the working tree.
- [ ] T044 Run `pnpm sync:docs` then `pnpm check:docs` from `relay-tutorial`.
- [ ] T045 [P] Write `specs/068-chapter-4-22/traceability.md` by **reading**, not by grep — including the two sections a grep cannot produce: what is in the feature with no requirement behind it, and the clauses deliberately not amended.

---

## Phase 8: The chapter

- [ ] T046 Register 4.22 in `relay-tutorial/lib/tutorial.ts` with all seven fields, at **`/part-4/chapter-22/milestone-the-priya-test`**, title **`"Milestone: the Priya test"`**. An unregistered id throws at build, which is how 4.6 learned the manifest exists.
  **THE PATH AND TITLE FOLLOW THE OTHER TWO MILESTONES, WHICH A FIRST DRAFT DID NOT CHECK**: `/part-4/chapter-09/milestone-the-meter-agrees` and `/part-4/chapter-17/milestone-an-image-end-to-end`, titled `"Milestone: the meter agrees"` and `"Milestone: an image, end to end"`. **The ★ is `docs/12`'s and does not travel into the title.** The directory under `app/(en)/part-4/chapter-22/` matches the path's last segment.
- [ ] T047 **Open the chapter with Stage 2** — `docs/07` §4 rule 1. The reader types an order number into the one route that should take it and gets a **500**. **That is a better opening than 4.21's**, which had to work to make three correct answers look like a gap; this one is a wall on the first step of the journey the chapter is named for.
- [ ] T048 Write the chapter at `relay-tutorial/app/(en)/part-4/chapter-22/the-priya-test/page.mdx`, 2,000–4,000 prose words counted outside fences and tables, English only.
- [ ] T049 [P] Write the figures in that directory's `figures.ts`, passed as `code` and not `chart` — `check:figures` caught three dead diagrams `pnpm build` did not.
- [ ] T050 Write the TRAP box. Two candidates and the second is new at analysis pass 3. **The two key spaces**: a reader assumes a channel is addressed the way a user is, because every other noun in the journey is, and the 500 is what that assumption costs. **Or the ban**: a reader assumes a ban disconnects, because `docs/03` says so in bold and calls it a safety property — and the platform refuses the next connection and the next send and leaves the open socket alone. **Pick one and put the other in a WHY**; both are a reader believing a sentence that names no clause.
- [ ] T051 Write at least one `WHY` box. The candidate is **why a milestone is allowed to find a hole at all** — rule 4 says a milestone verifies work other chapters did, so a milestone that has to build something has found a gap in the plan, not in itself. `docs/07` §4 rule 3; 4.17 through 4.21 carry 2, 3, 1, 2 and 4.
- [ ] T052 Publish what the chapter could not do: Phase 3's seven days, the 22 routes that still 500 on a malformed uuid, the eleven-minute interval, whether a real engineer finds the journey, and the two release gates constitution VI names that do not exist.
  **AND HOLE 3, WITH ITS BOUND RATHER THAN ITS ALARM (R10a).** `docs/03` Stage 5 calls *"a banned user's connections drop"* a safety property; FR-USR-06 says *"preventing **connection** and message send"*, the gateway checks the ban at auth and at send, and **no frame exists that could tell a live socket anything**. State the three facts: **sending stops immediately, reconnecting is refused with 4003, and an already-open socket keeps receiving until it closes on its own.** Whether that matters is the customer's judgement and the chapter does not make it for them.
- [ ] T052a **Publish the predicate, which is the chapter's thesis** (R11): Journey 3's six stages assert **fourteen** capabilities; **eleven cite a requirement and eleven hold; three cite none and three are holes.** *A capability `docs/03` asserts without naming a clause is a capability nobody built.* **Say what it does not claim**: the predicate is perfect on these fourteen and has been tested nowhere else — Journey 4's blocks are unswept — so it is a rule with one confirmation, published as that and not generalised.
- [ ] T053 Write the chapter's fences. **A titled fence is a whole-body claim** (051-6); an excerpt must be untitled. Chapters 4.19, 4.20 and 4.21 each contributed **0 titled fences** and put every diff in the appendix.
- [ ] T054 Generate hunks from the checker's own replay — `pnpm check:fences --dump <dir>` — then diff against `relay-platform` at `-U6`. **Verify every pre-image matches exactly once before pasting**; widen only where it does not, because widening merges adjacent hunks. **Strip the `--- a/` and `+++ b/` headers.**
- [ ] T055 Put every hunk in `relay-tutorial/fences/post-series.md`, **placed last**, working biggest-first from T005's table.
- [ ] T056 Run **all six tutorial gates** green from `relay-tutorial`, **after** every source edit, and compare each counted line against T003's.
- [ ] T057 [P] Count the prose words and confirm the bound.

---

## Phase 9: The record and the close

- [ ] T058 Write `specs/068-chapter-4-22/baseline.txt` phase by phase, **in the order the measurements were taken, including the ones that were wrong first**.
- [ ] T059 [P] Write `specs/068-chapter-4-22/gaps.md`, numbered, with the carried ledger **re-measured** rather than copied. Known carries: **067-1** (the audit log holds the name of everyone it says was erased), **067-2** (a published payload that does not reproduce its finding), **067-3** (a feature-local id in an API response, and `..HEAD` hiding it), 066-1, 066-4, 065-2, 065-3, 063-4, 062-12, 058-3 (**22 routes, re-measured**), 050-8, 043-1.
  **AND ONE THIS CHAPTER MUST NOT DROP**: constitution VI's third bullet gates releases on three mechanisms and **two of them do not exist** — no dependency vulnerability scan and no OWASP scan anywhere in the workspace. **A milestone is where that absence is most visible.**
  **AND TWO THIS CHAPTER OPENS.** *Journey 4's "What Relay must provide" blocks are unswept* — R11's predicate is 3 of 3 on Journey 3 and untested anywhere else, and the sweep costs one reading. *And no checker reads a journey map*, which is why three capabilities with no clause survived twenty chapters; `check-refs` already says *"ids only — this says nothing about whether the prose around them is true"*, and a checker that compared `docs/03`'s assertions to the SRS would have found all three.
- [ ] T060 **Record the `qs-bot` finding**, discovered during planning: chapter 4.21's quickstart §3 **erases `qs-bot`**, erasure is irreversible, and the seeder's best-known fixture id is therefore permanently absent on any lane where that quickstart ran. A later chapter borrowing it measures **404** and reads it as a broken route. **A quickstart that destroys a shared fixture has to say so.**
- [ ] T061 **Rebuild the api image before running the quickstart** — `pnpm build`, then `docker compose --profile services build api`, then `up -d --wait`. Then run `specs/068-chapter-4-22/quickstart.md` end to end and correct it in place, **recording each wrong version**. §1 and §2 are measured; **§3 and §4 are predictions and §3 depends on T007**, so expect it to be wrong. The last eight chapters' were wrong 3, 4, 3, 5, 2, 0, 5 and 2 times.
- [ ] T062 **Check FR-011 rather than trusting it** (SC-008): `git diff --name-only part4-ch21..HEAD` and confirm every file outside tests and documents is one the chapter is for. **A milestone's diff should be small**; if it is not, T007 chose an expensive option and the record should say that plainly.
- [ ] T063 Stop the composed services **by name** from `relay-platform` — `docker compose stop api gateway dispatcher media-worker`, and **not `ingester`**, which has no compose service.
- [ ] T064 Run the full lane set with nothing else against the stack and record every REAL exit code, **each with its `Cached:` line and elapsed time or under `--force`**, compared against T002. **Compare CLASS BY CLASS, not test by test** — 4.21's three coverage runs each failed different tests in the same carried class, and the gateway's `typing.itest.ts` went green/red/green over three isolated runs.
- [ ] T065 **Run the sealed suite last**, with the composed services back up, and record its counted line. It is the lane this chapter's whole product lives in.
- [ ] T066 Confirm every phase was committed as it closed, **submodule before pointer**, checked with `git -C relay-platform log -1` and `git ls-tree HEAD relay-platform`. **`git add -A` in the superproject stages a gitlink that may not have moved** (4.18).
- [ ] T067 **Push submodules first, then the superproject** — `relay-platform`, then `relay-tutorial`, then the root. CI is the superproject's and the other two are submodules; the other order checks out gitlinks no remote has. **Confirm with the user before pushing.**
- [ ] T068 Compare the CI error set **per error** against T004's baseline, in both directions, and record it (SC-010). **If both runs are green the diff carries nothing** — say so rather than presenting an empty diff as evidence.
- [ ] T069 If CI is red, fix the platform, then **re-dump, re-hunk `relay-tutorial/fences/post-series.md` and push both** — repairing a platform file invalidates the appendix hunks that publish it, and `relay-tutorial`'s job goes red with nothing in that repository changed (060).
- [ ] T070 Tag `part4-ch22` in `relay-platform` and the superproject, annotated, on a commit CI has proved green.
- [ ] T071 **Write the `CLAUDE.md` entry under the new convention**, which 067 established: an entry older than the last four is cut to its headline, its measurement blocks, any paragraph carrying a gap id cited elsewhere, and a one-line digest of every other finding's claim. **Headroom was 57,886 after 067's compression** — this is the first chapter that does not have to fight for space, and the convention's cost should be re-measured rather than assumed to hold.
- [ ] T072 Remove the active-plan line from between the `SPECKIT` markers in `CLAUDE.md` when the feature closes, leaving the markers and the note that explains why they span only that block.
- [ ] T073 **Part 4 is finished at this chapter.** Record in `specs/068-chapter-4-22/baseline.txt` what the part cost end to end — 22 chapters, the movements, the tags — and whether `docs/12`'s §7 open questions are all closed or whether any outlived the part. **§7.6 was open at the start of this feature**; T011 decides whether it is this chapter's and this task records the outcome either way.

---

## Dependencies

```
Phase 1 (T001–T006)  baseline — nothing depends on a figure nobody took
      ↓
Phase 2 (T007–T012)  BLOCKING. T007 decides the fence bill, the ADR question,
                     Stage 2's assertion and the chapter's opening
      ↓
Phase 3 (T013–T024)  US1 — the MVP. T013 first, because it is the only red one
      ↓
Phase 4 (T025–T026)  US2 — independent of US1 except for T010's file choice
      ↓
Phase 5 (T027–T030)  US3 — T027 needs US1 green to falsify it
      ↓
Phases 6–9           probes, documents, chapter, close
```

**T007 is the hinge.** Options A and C put `channels.controller.ts`,
`channels.schema.ts`, `channels.service.ts` and `repository.ts` into Phases 3, 6 and
7 and add T009 and T026; option D removes all of that and makes this a documents-and-
test chapter. **Do not start Phase 3 before T007 is recorded.**

## Parallel opportunities

- **Phase 1**: T003, T004 and T005 are independent of each other.
- **Phase 3**: T015 through T021 are one file in sequence — **not parallel**, and
  pretending otherwise is how a journey test stops being a journey.
- **Phase 5**: T028 is [P] against T027.
- **Phase 7**: T043 and T045 are [P].
- **Phase 8**: T049 and T057 are [P].

## Independent test criteria

| story | independently testable by |
|---|---|
| **US1** | boot the stack, run the sealed suite, read the six stages in order with no database access |
| **US2** | upload an image, deliver it, erase its uploader, assert the bytes are gone and the message still reads |
| **US3** | read `clauses.md` and find a verdict for each of six stages and three Phase 3 clauses, each with where |

## MVP

**User Story 1 alone.** Journey 3 executable is the milestone; the arrow and the
verdicts are what make it honest, and neither is needed for the journey to run.

---

## The mechanical coverage check, run and its result recorded

`grep` for each `FR-0NN` and `SC-0NN` in this file: **1 of 12 FR and 4 of 10 SC
cited by identifier.** Read rather than grepped, **all twenty-two are covered in
substance**:

```
FR-001 one test, six stages      T013–T023      FR-007 the arrow            T025
FR-002 the margin names chapters T022           FR-008 every claim measured T001·T006·T058
FR-003 reachable by customer id  T016           FR-009 per-stage verdicts   T028
FR-004 a refusal, never a 5xx    T013           FR-010 amend, don't build past T037
FR-005 three outcomes apart      T018           FR-011 nothing else changes T024·T062
FR-006 reaches recipient + audit T020·T021      FR-012 amend what is falsified T030·T037·T038

SC-001 T023   SC-003 T013·T016   SC-004 T018   SC-005 T020·T021   SC-006 T025   SC-009 T056
```

**TWENTY-TWO ALARMS, TWENTY-TWO FALSE** — chapter 4.11's pass 10 ran this check for
the first time and got fourteen of the same, which is why `traceability.md` is built
by reading. **The repair is not to sprinkle identifiers into task lines**: a task
citing an id it does not really discharge is worse than one citing none, because the
next mechanical check passes and the reading never happens.
