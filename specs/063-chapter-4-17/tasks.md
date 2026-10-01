---

description: "Task list — chapter 4.17, ★ Milestone: an image, end to end"
---

# Tasks: Chapter 4.17 — ★ Milestone: an image, end to end

**Input**: Design documents from `/specs/063-chapter-4-17/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/journey.md, quickstart.md

**Tests**: this feature is almost entirely tests. The journey suite IS the deliverable, so the
usual "tests are optional" note does not apply — a task that writes an assertion is an
implementation task here.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel (different files, no dependency on an incomplete task)
- **[Story]**: US1, US2, US3 from `spec.md`
- Every task names the file it touches

## Path conventions

Three repositories. `relay-platform/` and `relay-tutorial/` are git submodules of the
superproject, which holds `docs/`, `specs/` and `.github/workflows/ci.yml`. Paths below are
relative to the repository named in the task.

---

## Phase 1: Setup — the baseline, measured before anything is edited

**Purpose**: write down what is true now, including what is red. Every later number is a
difference from these.

- [ ] T001 Bring the stores up and record what answers, in `specs/063-chapter-4-17/baseline.txt`: `cd relay-platform && RELAY_POSTGRES_PORT=15432 docker compose up -d --wait`, then `--profile services build` and `up -d --wait`. **Read the media worker's boot line and record the scanner version** — 4.13's defect was a worker that started clean and verified nothing, and `scanner: "unreachable"` makes every later step look like a slow upload.
- [ ] T002 Record the five lanes with their REAL exit codes, read outside any pipe, in `specs/063-chapter-4-17/baseline.txt`: `pnpm lint`, `pnpm exec turbo run typecheck --force`, `pnpm build`, `pnpm exec turbo run test --force`, `pnpm test:integration`. **`echo "EXIT=$?"` after a pipeline reads the last command's status — seven occurrences in this project, the last two mine.**
- [ ] T003 [P] Record `pnpm coverage`'s REAL exit code, file count and test count in `specs/063-chapter-4-17/baseline.txt`, and note that `packages/outsider` is **outside** that lane — this chapter's central suite contributes nothing to the number constitution VI is stated in.
- [ ] T004 [P] Record `pnpm test:outsider`'s REAL exit code and test count in `specs/063-chapter-4-17/baseline.txt`, with the three variables the sealed job sets. No local lane reaches it.
- [ ] T005 [P] Record the five tutorial gates by name in `specs/063-chapter-4-17/baseline.txt` — `check:docs`, `check:errors`, `check:fences`, `check:figures`, `check:srs` — each run outside a pipe with its **counted line** quoted, not just its exit code (055-4: five of seven gate scripts exit 0 over an absent corpus).
- [ ] T006 Record the CI baseline in `specs/063-chapter-4-17/baseline.txt`: the latest run on `main`, per job, with its `##[error]` lines normalised and sorted. This is what T082 compares against, per error and in both directions.
- [ ] T007 **Count the fence exposure before any edit**, in `specs/063-chapter-4-17/baseline.txt`: for every file this feature might touch, how many titled fences name it across `relay-tutorial`. 061's rule — move the count to phase 1, where it can still change how the work is sequenced, **which a task that predicts the answer defeats**. The first draft of this line said *"expect it to be near zero"* and the analysis pass measured **five**: `packages/outsider/src/integrate.itest.ts` is titled in part-3/chapter-26 (en and vi), part-4/chapter-08, part-4/chapter-09 and `fences/post-series.md` — **two whole bodies and six diffs**. Re-count rather than copy that figure; the point is the count, not the number.
- [ ] T008 Quote the sealed suite's **current** media assertions verbatim into `specs/063-chapter-4-17/baseline.txt`, from `relay-platform/packages/outsider/src/integrate.itest.ts` — the `state: "pending"` expectation and the comment explaining it. The chapter's first finding is that the comment is false, and a quote taken after the edit proves nothing.
- [ ] T009 Re-run research R1's five-run timing against the composed stack and record it in `specs/063-chapter-4-17/baseline.txt`. Phase 0 measured 5,656–6,143 ms with a 5,000 ms interval; **a figure taken once, three days before the work, is a figure about a different machine state.**

---

## Phase 2: Foundational — what the journey needs before it can be written

**Purpose**: the shared pieces US1, US2 and US3 all sit on. Blocking.

- [ ] T010 Read `relay-platform/packages/outsider/src/integrate.itest.ts` end to end and record in `specs/063-chapter-4-17/baseline.txt` which helpers exist and where. **Measured during analysis: `post` and `get` are defined once inside the describe, and `waitFor` is defined THREE TIMES — lines 280, 348 and 423, one per test.** The risk the plan names is a second harness, and the file has already duplicated one three ways.
- [ ] T010a **Decide, and write the decision down** in `specs/063-chapter-4-17/baseline.txt`: either lift the three `waitFor` copies in `relay-platform/packages/outsider/src/integrate.itest.ts` to one shared helper before adding anything, or state why a fourth local copy is cheaper than consolidating. A note that records the duplication without acting on it is how it becomes four.
- [ ] T011 Add the poll-to-deadline helper to `relay-platform/packages/outsider/src/integrate.itest.ts` **in the shape T010a chose** — one helper beside `post` and `get` if the copies were consolidated, a local one if they were not. It reads the attachment's state through `GET /v1/channels/{id}/messages` and returns when it leaves `pending`. **Published surface only** — there is no route that answers *"has the worker run yet"*, which is why the journey learns it the way a client would.
- [ ] T012 Make that helper's failure in `relay-platform/packages/outsider/src/integrate.itest.ts` name the worker: on deadline, throw with the state it last saw, the elapsed time and the sweep interval. **A stopped worker and an object that never existed are the same 404 from outside** (research R6), so the message is the only thing that can tell a reader which.
- [ ] T013 Correct the false comment at `relay-platform/packages/outsider/src/integrate.itest.ts` — *"this suite runs no media worker, which is what makes the value stable rather than timing-dependent"* — with the measured truth: CI's job starts the worker, the sweep is 5,000 ms, the read happens within milliseconds, and the margin is about five seconds. **It is timing-dependent and it is stable, which are two claims and the comment makes the wrong one.**
- [ ] T014 [P] Assert the correction in `relay-platform/packages/outsider/src/integrate.itest.ts` rather than only writing it: keep the existing `state: "pending"` expectation and add the reason as a checked fact — the read happens inside one sweep interval. A comment is not a test, and this is the chapter's own subject applied to itself.

---

## Phase 3: User Story 1 — one image, through the worker that ships, to a recipient (P1)

**Goal**: one suite carries a single image from slot to delivered bytes, with the deployed
worker making the verdict.

**Independent test**: run `pnpm test:outsider` against the composed stack. Stop the worker and a
named assertion fails.

- [ ] T015 [US1] Write the journey's opening in `relay-platform/packages/outsider/src/integrate.itest.ts`: a slot for a real PNG, the signed PUT, and the assertion that both answer as `contracts/journey.md` says. Name chapter 4.10 in the assertion's comment — **each step names the chapter that made it possible**, which is `tuan.itest.ts`'s shape and FR-002.
- [ ] T016 [US1] Generate an **800×600** PNG inside `relay-platform/packages/outsider/src/integrate.itest.ts` with `node:zlib`, measured at **447,377 bytes** (FR-004a). **It must exceed 320 px on its long edge or there is no thumbnail to fetch**: `thumbnailOf` answers `within-bound` at or below the bound and the worker writes no rendition, and the suite's existing fixture is a **1×1 PNG, 67 bytes**, which would make T021 assert an id the payload never carries. A literal is not available at this size — 447,345 bytes of deflate — and a 321×1 strip that would fit one is rejected in the spec's Assumptions. No fixture read from `/tmp`: 4.16's quickstart referred the reader to another document for its fixture and that was correction 1 of three.
- [ ] T016a [US1] Correct the header sentence in `relay-platform/packages/outsider/src/integrate.itest.ts` that reads *"AND IT IMPORTS NOTHING AT ALL BEYOND VITEST"*. **It is already false** — line 1 is `import { randomUUID } from "node:crypto"` — and `node:zlib` makes it falser. The seal's rule is that no workspace path may be reached, not that no builtin may be; say that, because a sentence nobody can trust is worse than no sentence.
- [ ] T017 [US1] Send a message naming the object **before** the verdict, in `relay-platform/packages/outsider/src/integrate.itest.ts`, and assert the attachment comes back `pending`. FR-MED-06's decision at 4.11: a photo can be sent the moment the upload completes.
- [ ] T018 [US1] Wait for the deployed worker with the T011 helper and assert the state becomes `ready`, in `relay-platform/packages/outsider/src/integrate.itest.ts`. **No test may call `POST /internal/media/{id}/verdict`** — `contracts/journey.md` forbids it, and calling it is the thing this chapter exists to stop doing.
- [ ] T019 [US1] Assert the history payload's full shape in `relay-platform/packages/outsider/src/integrate.itest.ts`: `{type, media_id, state:"ready", thumbnail:{media_id, width, height}}`. Measured at 320×240. **Read the array under `messages`, not `data`** — research R7's wrong key rendered as a missing attachment.
- [ ] T020 [US1] Ask for the link and fetch the bytes in `relay-platform/packages/outsider/src/integrate.itest.ts`, and assert they are **byte-identical** to what was uploaded — not the same length. A length check passes for a file the store truncated.
- [ ] T021 [US1] Fetch the thumbnail by the id the history payload handed over, in `relay-platform/packages/outsider/src/integrate.itest.ts`, and assert 200 and a smaller body. **This depends on T016's image exceeding the bound** — measured at 18,090 bytes against the parent's 447,377. **It is the only media id the platform gives out that no message names**, and 4.15's composite key is what makes it reachable.
- [ ] T022 [P] [US1] Assert the thumbnail's bytes are not the parent's, in `relay-platform/packages/outsider/src/integrate.itest.ts`. Two signed URLs that both answer 200 prove nothing if they serve the same object, and `readableMediaObjectKey` resolves `parentId ?? mediaId` — a reader will want to know which it returned.
- [ ] T023 [US1] Run the suite green against the composed stack and record the output in `specs/063-chapter-4-17/baseline.txt`, with the elapsed time of the verdict wait.
- [ ] T024 [US1] **Run it red**: stop the deployed worker, run the suite, and record in `specs/063-chapter-4-17/baseline.txt` which assertion fails and what its message says. SC-002. A suite that has never failed is a suite nobody has checked.
- [ ] T025 [US1] Restart the worker, re-run, and record the green in `specs/063-chapter-4-17/baseline.txt`. **Clean up a probe before anything is counted** (043) — a stopped worker leaves `pending` rows that the next run's sweep will process.

---

## Phase 4: User Story 2 — a rejected upload arrives as a marker, not a gap (P2)

**Goal**: a refusal reaches the recipient as a state on a message that is still there.

**Independent test**: upload bytes that contradict the declaration and read the channel.

- [ ] T026 [US2] Add the rejection journey to `relay-platform/packages/outsider/src/integrate.itest.ts`: a slot declaring one type, a PUT of bytes that are another, and the deployed worker's refusal. 4.13 measured that a GIF declared as a PNG is rejected at exactly the right byte count.
- [ ] T027 [US2] Assert the message is still in history and its attachment reads `rejected`, in `relay-platform/packages/outsider/src/integrate.itest.ts`. FR-MED-09's testable half: the record that *something* was sent survives the refusal.
- [ ] T028 [US2] Assert the link request for the rejected object is refused, in `relay-platform/packages/outsider/src/integrate.itest.ts`, and that the body is **byte-identical** to the refusal for an id nobody has apart from `request_id`. 4.12 built that property; this is the first time it is checked from outside with a real refusal behind it.
- [ ] T029 [US2] Assert a rejected attachment is distinguishable from a message with no attachment and from a deleted message, in `relay-platform/packages/outsider/src/integrate.itest.ts`, using only published fields. That is the clause's own reason — Priya must tell "rejected upload" from "deleted message".
- [ ] T030 [US2] Check the premise before asserting it in `relay-platform/packages/outsider/src/integrate.itest.ts`: confirm that a message whose only attachment was rejected is still returned by the history route rather than filtered. If it is filtered, **that is a finding and the chapter records it** rather than the suite working around it.
- [ ] T030a [US2] Hold a socket open from before the send, in `relay-platform/packages/outsider/src/integrate.itest.ts`, and assert a **`media.updated`** frame arrives carrying `rejected` after the verdict (FR-006a, SC-003a). **Measured: it does** — `{"media_id":…,"channel":…,"state":"rejected"}`, on `${ws}/v1/ws?token=…` with a token from `POST /auth/dev-token` and the subscriber added by `POST /v1/channels/{id}/members` with `{user_ids:[…]}`. **Those four details took four attempts and three of the failures looked like the platform**: the wrong socket path, a missing token, and a members call with the wrong body swallowed by a `.catch(() => {})` — which left the subscriber outside the channel, seeing no frames at all, so *"no `media.updated`"* read exactly like the feature being absent. **Swallow nothing in this test.** 4.14 built that frame for a recipient holding a stale `pending`, and **the sealed suite mentions it zero times** — this is the only end-to-end evidence that chapter's work has.
- [ ] T030b [P] [US2] Check `media.updated`'s premise before asserting it, and record the answer in `specs/063-chapter-4-17/baseline.txt`: does the frame reach a subscriber on the REJECTION path, or only on `ready`? 4.14's suite drives it through `recordMediaVerdict` called directly; through the deployed worker it has never been watched.
- [ ] T031 [US2] Record in `specs/063-chapter-4-17/baseline.txt` what FR-MED-09's *"renders as an explicit rejection marker"* can and cannot be discharged by, with the reason: there is no client in this repository and FR-MED-14's reference client is P4 and unbuilt.

---

## Phase 5: User Story 3 — what the path costs, measured once (P3)

**Goal**: the end-to-end figure, decomposed, with its sample size.

**Independent test**: run the path a stated number of times and publish the distribution.

- [ ] T032 [US3] Measure the path step by step against the composed stack and record every run in `specs/063-chapter-4-17/baseline.txt`: slot, PUT, PUT→verdict, history, link, GET, thumbnail. **Not with `date +%s%3N`** — research R7 measured that it appends nine digits of nanoseconds on this machine and the first harness reported `slot 70934383ms`.
- [ ] T033 [US3] State the sample size beside every figure in `specs/063-chapter-4-17/baseline.txt`, and give min, p50 and max rather than a mean alone. 4.16 published a distribution whose mean was 509× its median; one number is a choice of which story to tell.
- [ ] T034 [US3] Separate the sweep interval from the work in `specs/063-chapter-4-17/baseline.txt`. Of ~5,700 ms, 5,000 is a timer. **Publishing the total alone describes a platform that is slow at scanning when it is a platform that checks every five seconds.**
- [ ] T035 [US3] Record the ~700 ms remainder **as a residual, not a measurement**, in `specs/063-chapter-4-17/baseline.txt`. It is a total minus a bound. 4.13 measured the scan directly; re-deriving it by subtraction would publish a worse number for a quantity that already has a good one.
- [ ] T036 [P] [US3] Record what the lane cannot say about this figure in `specs/063-chapter-4-17/baseline.txt`: one image, one tenant, loopback, a 447,377-byte PNG. The scan is 52% of the work at 4 KiB and 97.7% at 100 MB (ADR-31), so this sample sits at one point on a curve.

---

## Phase 6: The probes — making the silent failures loud

**Purpose**: each probe produces a named red rather than a plausible green. Run after the
stories so the suite exists to be broken.

- [ ] T037 Probe the worker's absence as its own experiment, recorded in `specs/063-chapter-4-17/baseline.txt`: with the worker stopped, what does the API say about an uploaded object, attached and unattached? Research R6 measured 404 `not_found` for the unattached case; the attached case has not been measured.
- [ ] T038 [P] Probe an unreachable scanner by pointing `RELAY_CLAMAV_HOST` at a closed port in a throwaway `docker compose run` of the worker, and record in `specs/063-chapter-4-17/baseline.txt` what the boot line and the sweep line say. **It sweeps the real lane and writes nothing**, which is the point: a worker that cannot scan produces no verdict, so no row moves. Stop it before the real worker is restarted so the two are never sweeping together. 4.13's defect, reproduced deliberately — **the symptom is objects not becoming `ready`, and that is what an un-uploaded object looks like too.**
- [ ] T039 [P] Probe the journey's own scope: confirm no assertion in the new suite depends on a row another suite planted, in `relay-platform/packages/outsider/src/integrate.itest.ts`. 4.16's debris assertion passed locally on 83 keys of old probe residue and failed on CI's empty volume; **the sealed suite runs against whatever bucket CI has.**
- [ ] T040 Run `python3 relay-tutorial/scripts/check-lane-scope.py` and record **the counted line, not the exit code**, in `specs/063-chapter-4-17/baseline.txt` — the file count is the point, because 049 found that checker reading a worktree 045 had deleted and exiting 0 over nothing. **It cannot see this chapter's suite**, which contains no SQL, and that is recorded as a limit rather than reported as a pass.
- [ ] T041 Count the assertions in the journey that do **not** name a chapter, and record the number in `specs/063-chapter-4-17/baseline.txt`. SC-004 wants zero. A count, not an adjective.

---

## Phase 7: The documents

- [ ] T042 Amend **FR-MED-09** in `docs/04-srs.md`: the data half met — a rejected attachment reaches a recipient as an explicit state on a message that stays in history — and *"renders as"* recorded **unmet, with the reason**. 4.16's precedent with *"visible in the dashboard"*. **Read the clause before editing it**; four documents once agreed on two clauses that do not exist.
- [ ] T043 [P] Read the clauses **beside** FR-MED-09 in `docs/04-srs.md` while the file is open. 4.16 found the SRS's `media_events` dictionary row describing a table nobody built, two rows from the one it went in to edit, and no checker reads a clause against the schema it describes.
- [ ] T044 Add revision row **1.24** to `docs/04-srs.md`, stating what the milestone demonstrated and what it could not.
- [ ] T045 [P] Count the clauses in `specs/063-chapter-4-17/clauses.md`: how many this chapter demonstrates, how many it records unmet, how many are unreachable. SC-006. A chapter that says "mostly met" is one nobody can check.
- [ ] T046 [P] Amend **both** copies of the Part 4 table — `docs/12-part-4-structure.md` row 18 CLOSED and `docs/07-tutorial-plan.md` row 18 SHIPPED. Two copies, and amending one is how they drift.
- [ ] T047 [P] Record in `docs/05-sad.md` that the sealed suite is the only lane that exercises the deployed media worker, and that it is outside the coverage lane. The architecture document says which suites prove what; this is a gap in that account.
- [ ] T048 [P] Grep `docs/` for feature-local ids leaking in, by **diffing** rather than grepping the tree: `git diff HEAD -- docs/ | grep '^+' | grep -oE 'FR-0[0-9][0-9]'`. It caught one in 4.16 — inside the sentence correcting somebody else's citation — and **nothing runs this check**.
- [ ] T049 Run `pnpm sync:docs` then `pnpm check:docs` from `relay-tutorial`, which rewrites `relay-tutorial/content/docs/*`. The tutorial keeps mirrored copies and 061's first run of that gate was red for exactly this.

---

## Phase 8: The chapter

- [ ] T050 Register 4.17 in `relay-tutorial/lib/tutorial.ts` with **all seven fields**. `path` is checked by no gate, and an unregistered id throws at build.
- [ ] T051 Write the chapter at `relay-tutorial/app/(en)/part-4/chapter-17/<slug>/page.mdx`, 2,000–4,000 prose words counted **outside fences and tables**, English only.
- [ ] T052 [P] Write the figures in `relay-tutorial/app/(en)/part-4/chapter-17/<slug>/figures.ts`, passed as `code` and not `chart` — `check:figures` caught three dead diagrams `pnpm build` did not.
- [ ] T053 [P] Write the `TRAP` box in `relay-tutorial/app/(en)/part-4/chapter-17/<slug>/page.mdx`. The candidate is phase 2's: **a comment that explains why an assertion is stable, and is false in the job that runs it.** It survived because the assertion was right.
- [ ] T054 [P] Publish the decomposition in `relay-tutorial/app/(en)/part-4/chapter-17/<slug>/page.mdx` with the timer named as the dominant term, and the sample size beside it.
- [ ] T054a [P] State the milestone's **two halves** in `relay-tutorial/app/(en)/part-4/chapter-17/<slug>/page.mdx` (FR-008): which claim the lane checks on every run, and which figure is recorded once. `docs/12` §2.3 sets that split for every milestone in this part and 4.9 followed it — *"the CI half is falsifiable and fails for its own reason; the recorded half follows `docs/11`'s precedent"*. **Presenting the measurement as the gate is the failure the split exists to prevent.**
- [ ] T055 [P] Publish what the milestone could not demonstrate, in `relay-tutorial/app/(en)/part-4/chapter-17/<slug>/page.mdx`: no renderer, no metering in the path, one image. **A milestone that reports only the parts that worked is one nobody trusts.**
- [ ] T056 Write the chapter's fences in `relay-tutorial/app/(en)/part-4/chapter-17/<slug>/page.mdx`. **A titled fence is a whole-body claim** (051-6) — an excerpt must be untitled, and 4.14 paid three fences for forgetting it.
- [ ] T057 Generate hunks from the checker's own replay: `pnpm check:fences --dump <dir>` in `relay-tutorial`, then diff against `relay-platform`. **Verify every pre-image matches the dumped state exactly once** before pasting, widening past `-U6` only when it does not.
- [ ] T058 Put hunks in `relay-tutorial/fences/post-series.md` for any file the appendix already amends (4.8), and read T007's counted table to work the bill biggest-first.
- [ ] T059 Run `check:fences` to 0 and `pnpm build` green from `relay-tutorial` (SC-009). **Run `check:fences` after ANY source edit** — 4.16's CI failure was a coverage pin added after the chain was taken to zero, and the edit that broke it was the ratchet being tightened.
- [ ] T060 [P] Count the prose words in `relay-tutorial/app/(en)/part-4/chapter-17/<slug>/page.mdx` and confirm the bound. SC-010.

---

## Phase 9: The record and the close

- [ ] T061 Write `specs/063-chapter-4-17/baseline.txt` phase by phase, **in the order the measurements were taken, including the ones that were wrong first**.
- [ ] T062 [P] Write `specs/063-chapter-4-17/gaps.md`, numbered, with the carried ledger **re-measured** rather than copied. Known carries: 050-8 (three test files spawn the ingester and it is still not a deployment), 062-7 (coverage cannot see a service run in a child process — this chapter's suite is the same shape one step further out), 062-12 (68 of 139 files unpinned), 055-3 as corrected at 062, 043.
- [ ] T063 [P] Write `specs/063-chapter-4-17/traceability.md` by **reading**. 4.11's mechanical map raised fourteen false alarms out of fourteen.
- [ ] T064 Run `specs/063-chapter-4-17/quickstart.md` end to end and correct it in place, recording each wrong version. Every step in it has been run once; **the document as a document has not**, which is the failure 4.16 met three times.
- [ ] T065 Stop the composed services **by name**, from `relay-platform/compose.yaml`'s `services` profile — `api gateway dispatcher media-worker`, and **not `ingester`**, which has no Dockerfile and makes the whole command fail.
- [ ] T066 Run the full lane set once more and record every REAL exit code in `specs/063-chapter-4-17/baseline.txt`: lint, typecheck, build, unit, `test:integration`, `coverage`, `test:outsider`, the five tutorial gates.
- [ ] T066a **Check FR-012 rather than trusting it**: `git diff` the platform changes this feature made and confirm in `specs/063-chapter-4-17/baseline.txt` that every one is a test, a comment or a document. 4.2 built all four items of a later chapter's brief and that chapter ceased to exist; the way that happens is one useful addition at a time.
- [ ] T067 Commit each phase to the repository it belongs to — `relay-platform`, `relay-tutorial`, or the superproject holding `specs/` and `docs/`. Under five lines, no trailer.
- [ ] T068 **Push submodules first, then the superproject.** `ci.yml` is the outer repository's and the other two are gitlinks, so the reverse order checks out commits no remote has.
- [ ] T069 Compare the CI error set **per error** against T006's baseline, in both directions, and record it in `specs/063-chapter-4-17/baseline.txt` (SC-008). One comparison supports *"this run introduced nothing new"*, not *"the set is stable"*.
- [ ] T070 **Watch the sealed job specifically** — `relay-platform — the sealed integration`, defined in `.github/workflows/ci.yml`. It is the only job that runs this chapter's suite, and it is the first honest execution of it — no local lane reaches it. If it is red, the journey is wrong about the stack rather than about the code.
- [ ] T071 If CI is red, fix the platform, then **re-dump, re-hunk `relay-tutorial/fences/post-series.md`, and push both** — repairing a platform file invalidates the appendix hunks that publish it.
- [ ] T072 Tag `part4-ch17` in `relay-platform`, annotated, on a commit CI has proved green. 4.14's tag had to be moved off one that fails `pnpm typecheck`.
- [ ] T073 Compress 062's `CLAUDE.md` entry to its headline, measurement block and still-cited findings, and add this one. **The file has a 150,000-character budget**; it stood at 139,238 after 062's close and the active-plan line.
- [ ] T074 Remove the active-plan line from between the `SPECKIT` markers in `CLAUDE.md` when the feature closes, so the next feature's line replaces a plan rather than joining a list.

---

## Dependencies

```
Phase 1  →  Phase 2 (the helpers, and the comment that is wrong)
Phase 2  →  Phase 3 (US1)  →  Phase 4 (US2)
Phase 2  →  Phase 5 (US3)          US3 needs the path, not the assertions
Phases 3-5  →  Phase 6  →  Phase 7  →  Phase 8  →  Phase 9
```

**T008 blocks T013, and the order is the point.** The comment has to be quoted before it is
corrected, or the chapter's first finding is a claim with no evidence.

**T024 blocks T025, and both block the close.** A suite that has not been run red has not been
checked, and SC-002 is the only success criterion that cannot be satisfied by writing code.

**US2 depends on US1** for the journey's helpers, not for its assertions. **US3 depends on
neither** — it measures the path, which already works.

### Parallel opportunities

- **Phase 1**: T003–T005 and T007 are independent reads.
- **Phase 3**: T022 is independent of T015–T021 once the journey exists.
- **Phase 4**: nothing. Every task touches `integrate.itest.ts`, and `[P]` means a different
  file — the first draft marked T029 parallel because it is a separate `it(...)`, which is not
  what the marker means.
- **Phase 5**: T036 is a note, not a measurement, and can be written while T032 runs.
- **Phase 7**: T043 and T045–T048 touch different documents.
- **Phase 8**: T052–T055 are separate concerns in two files.

### Suggested MVP

**Phase 1 + Phase 2 + Phase 3.** US1 alone is the milestone's claim: one image, through the
deployed worker, to a recipient's bytes. US2 and US3 make it a chapter.

---

## What this feature must not do

- **Add product surface.** Row 18's line is a claim about what already works. If the journey
  wants something the platform does not expose, it is recorded rather than invented — 4.2 is the
  counter-example, and the chapter it pre-empted ceased to exist.
- **Call the worker's route.** `POST /internal/media/{id}/verdict` is the worker's, and a test
  calling it is the thing this chapter exists to stop doing.
- **Shorten the sweep interval to make a test faster.** 5,000 ms is a deployment property.
- **Absorb a repair.** If the journey finds a defect in an earlier chapter's work, it is recorded
  with its bill and scoped deliberately. A milestone that fixes things stops being a measurement
  of what was already there.
