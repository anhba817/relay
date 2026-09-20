# Tasks: chapter 4.13 — the only service that reads the bytes

**Input**: `specs/059-chapter-4-13/` — spec, plan, research, data-model, contracts, quickstart
**Prerequisites**: chapter 4.12 shipped and tagged `part4-ch12`

**Tests are requested.** FR-MED-03 and FR-MED-04 are both `T` clauses, and the chapter's two
hardest claims — *the scanner actually ran* and *a transient failure changes nothing* — are
claims a test can make and a document cannot.

## Format: `[ID] [P?] [Story] Description`

- **[P]** — different files, no dependency on an incomplete task
- **[US1] [US2] [US3]** — the user story the task serves; setup, foundational and polish carry none

## Path Conventions

`relay-platform/` is the platform, `relay-tutorial/` the chapter, `docs/` the published
documents. Paths below are relative to the repository that owns them.

---

## Phase 1: Setup — the measurements this chapter is compared against

- [ ] T001 Bring the stores up and record what answers: `RELAY_POSTGRES_PORT=15432 docker compose up -d --wait`. **Read the counted line, not the exit code.** And if NATS comes up unhealthy, the health check **names one unrecoverable stream at a time** (`gaps.md` 058-7) — clearing the first reveals the second, and the bulk form of that clear was refused by this environment's guard where one-at-a-time was allowed.
- [ ] T002 Record the opening `check:fences` figure as an **absolute number**. It is 0 at `part4-ch12`, over 291 files and 55 chapters. A delta of zero is what hid a problem for nine chapters.
- [ ] T003 [P] Record the opening dependency count across every `package.json` in `relay-platform` — **29** at `part4-ch12`. **Write the counter as a file, not a shell one-liner** (057's `TOTAL 0`). SC-010 expects this number to MOVE; the task is to have the before figure, not to hold it.
- [ ] T004 [P] Record the opening state of the lanes: `pnpm test`, `pnpm test:integration`, `pnpm test:outsider`, `pnpm check:errors` (**34 codes, 34 sections**). **Two reds are carried and neither is this chapter's** — `services/ingester/src/shape.ts` pinned at 100 and measuring **95.12** since 048, and `typing.itest.ts` flaking at a deadline (`gaps.md` 058-8, four runs: 22/23, 22/23, 22/23, 23/23). Record them at the open so the close is a comparison.
- [ ] T004a **Stop the composed services before any lane runs** (`gaps.md` 057-5), and record which state each measurement was taken in. `docker compose --profile services` is a second set of relays on the same `outbox`.
- [ ] T005 **Re-measure the sweep before anything is built.** `research.md` R1 measured 1.412 ms per signed `HEAD` (p50 1.094, p95 1.714, n=200) over 3,005 `pending` rows, 4.2 s for the whole backlog, 34 of 200 with bytes. **The lane moves between chapters** — 4.8 watched a median shift because the feature itself changed the population — so a figure carried from `research.md` into the chapter without re-measurement is a figure about a different database. **And the sample was newest-first and biased**: 17% had bytes against the bucket's 8.4% overall. Say which the chapter publishes.
- [ ] T006 **Count the fenced files this chapter will touch, against the checker.** `plan.md` lists twelve as a floor and says so. `pnpm check:fences --dump <dir>` after the first source edit, then diff each dumped path against the tree. **Give the helper a control**: with no edit yet the bill must be 0, and 058's first version charged eleven files for a sole trailing-newline difference the checker normalises.
- [ ] T007 **Record what a container costs before adding one** (plan open question 3). `services/ingester` has **no Dockerfile** and nothing starts it but a test suite spawning a child (`gaps.md` 050-8, open since 4.5). Count today's containers, today's `INFRA_SERVICES` entries, and confirm the two agree — the both-directions assertion 4.10 tripped over.

---

## Phase 2: Foundational — the states, the seam, and the service that does not exist

**Blocking.** Every story needs somewhere to put a verdict and something to put it there.

- [ ] T008 Write `services/api/migrations/0018_media_states.sql` — drop and re-add `media_objects_state_check` as `state IN ('pending','ready','rejected')`, and add the probe and verification columns (`data-model.md` §2, §3). The tail is `0017_media_reference_index.sql`, checked rather than remembered.
- [ ] T009 **Run `services/api/migrations/0018_media_states.sql`'s constraint red before trusting it**: a fourth value must still fail. 4.11 published the database's own `violates check constraint` as evidence; the widened version has to keep earning that.
- [ ] T010 Declare the same states and columns in `services/api/src/db/schema.ts` so drizzle and the migration agree. **The migration is the source of truth** (ADR-16); the declaration stops the next generator run proposing to drop them.
- [ ] T011 **`scanning` IS NOT A STATE, AND THE TASK IS TO NOT ADD IT** (`data-model.md` §2). It is not in the clause, FR-MED-07 publishes three states to clients, and what a second worker actually needs is a lease with a timeout rather than a value somebody must clear after a crash. Record the decision where the next reader of the enum will find it.
- [ ] T012 Add the read side of the seam — `GET /internal/media/pending` — in `services/api/src/internal/`, returning id, object key, declared type and declared bytes, oldest first (`contracts/media-verification.md` §2). **It takes no tenant parameter**, which is the isolation property to assert rather than a scope to add.
- [ ] T013 Add the write side — `POST /internal/media/:mediaId/verdict` — accepting `ready` with the probe's findings or `rejected` with a reason. **There is no `retry` verdict**: a transient failure sends nothing, because a row recording *"we could not tell"* is one somebody later reads as a fact.
- [ ] T014 Idempotence by state in `services/api/src/internal/`, **and the 409 is the part worth testing.** A second `ready` for a `ready` object answers 200 and changes nothing; a `ready` for a **`rejected`** object answers **409**, because the bytes are gone and a 200 would let a stale worker resurrect a state whose object no longer exists.
- [ ] T015 In `services/api/src/internal/`, **the rejection path deletes the bytes AND keeps the row** (FR-MED-04's *"retaining only the audit record"*). Assert both halves — a state change that leaves the bytes in the store is the failure FR-MED-03 exists to prevent.
- [ ] T016 **A rejected object's bytes stop counting against the quota, by EXCLUDING the row rather than zeroing the column** (`data-model.md` §4). SRS 1.17 made committed bytes a sum over the media rows precisely so a delete needs no subtraction, and zeroing `declared_bytes` would destroy the fact FR-MED-03 is about.
- [ ] T017 Create `services/media-worker/` — the sweep loop, the store reads, the verdict call. **Copy the dispatcher's shape, not its sentences**: `services/dispatcher/src/api-client.ts:67` is the one existing client of this seam, and 050 recorded a probe that copied a shape and dropped its guards.
- [ ] T018 **Decide plan open question 3 in writing and land it**: compose service, or the ingester's unpackaged shape. If it is a container, `compose.yaml` and `packages/config/src/infra.ts` change **together** — and `INFRA_SERVICES` is checked in both directions by a unit test no integration lane imports, so `pnpm coverage` is the only command that reaches it (056-8).
- [ ] T019 **Decide plan open question 4 in writing**, in `specs/059-chapter-4-13/data-model.md` §7: what stops two workers processing one object. One worker is the current reality and *"we only run one"* is a deployment fact rather than a design. `FOR UPDATE SKIP LOCKED` is not available to the worker — the read is through the api (ADR-04) — so the lease, if there is one, lives on the api's side of the seam.
- [ ] T020 Commit phase 2.

---

## Phase 3: An uploaded image becomes readable (US1) 🎯 MVP

**Goal**: FR-MED-03 and FR-MED-04's happy path. **Independently testable**: upload a real PNG
through the published slot route and watch it reach `ready` with the right dimensions.

- [ ] T021 [US1] Implement the sweep in `services/media-worker/`: ask the api for `pending` rows, ask the store `HEAD` for each, and process the ones that have bytes. **A 404 is "not yet", never "rejected"** — 91.6% of the lane's rows are in that state and FR-MED-10 reaps them at 24 hours, which is a different mechanism with a different clause.
- [ ] T022 [US1] **Verify size and type against the declaration** in `services/media-worker/src/verify.ts` (FR-MED-03). The size is the store's `Content-Length`; the type is what the bytes say, not what the store echoes back — the store returns whatever `Content-Type` the client PUT with, which is the same claim the declaration already made.
- [ ] T023 [US1] **Read dimensions from the header, with no dependency** (`contracts/` §5). PNG's `IHDR` is a fixed offset — checked at **24 bytes of 4,722** on a real 640×480 file — GIF's screen descriptor is bytes 6–10, JPEG needs a short walk to the first `SOF`, WebP's are in the `VP8X`/`VP8`/`VP8L` chunk. Four formats, one small reader; ADR-30's *"28 lines of `node:crypto`"* is the precedent.
- [ ] T024 [US1] **Run `services/media-worker/src/dimensions.ts` red per format**, not once. A reader that returns the right answer for PNG and silently returns zeros for WebP passes a single-format test and ships. One real file per allowed image type.
- [ ] T025 [US1] Transition to `ready` through the seam, with `verified_bytes`, `verified_type`, `width` and `height` (`contracts/` §1).
- [ ] T026 [US1] Integration test in a **new file**, `services/media-worker/src/verify.itest.ts`: slot, PUT a real PNG, wait, assert `ready` and the dimensions. A new file costs the fence chain nothing, which is the cheap direction 051 recorded.
- [ ] T027 [US1] **Measure the three round trips and decide whether they collapse** (plan open question 4's sibling; `contracts/` §3). `HEAD`, a `Range` GET for the probe, a streamed GET for the scan. 4.10 measured one extra round trip on the slot path at **+24.1%**, so the cost is a known number rather than an intuition — and the largest allowed object is **100 MB**, which is what makes fetching everything to read 24 bytes worth avoiding.
- [ ] T028 [US1] **Measure the worker's peak RSS against the largest object it may see**, and do NOT cite NFR-SCL-01 for it (`research.md` R9). That clause names 10,000 connections and no memory figure; the 160 MB everyone reaches for is `docs/11`'s measurement of the **gateway's** RSS, and 050 recorded this exact mis-citation.
- [ ] T029 [US1] Commit phase 3.

**Checkpoint**: a photo uploaded through the published route becomes `ready` on its own.

---

## Phase 4: A lie about the bytes is rejected (US2)

**Goal**: FR-MED-03's refusal, with the bytes gone and the record kept.

- [ ] T030 [US2] Reject an object whose actual type contradicts its declaration, in `services/media-worker/src/verify.itest.ts`: `rejected`, reason `declaration_mismatch`, bytes deleted from the store.
- [ ] T031 [US2] Reject an object materially larger than declared, in `services/media-worker/src/verify.itest.ts`, with the same three assertions.
- [ ] T032 [US2] In `services/media-worker/src/verify.itest.ts`, **assert the bytes are gone by asking the STORE, not by asserting the platform called delete.** A signed `HEAD` answering 404 is the claim; a spy on a method is a claim about the code.
- [ ] T033 [US2] **Assert the quota moved.** The tenant's committed bytes fall by the rejected object's declaration, read through the same sum `media.service.ts` uses — otherwise a rejected upload holds a tenant's storage forever.
- [ ] T034 [US2] **Run `services/media-worker/src/verify.ts` red by deleting the type check**, and confirm the size test still passes and the type test fails. Two conditions that always agree are one condition with two names.
- [ ] T035 [US2] **What `verified_type` is measured from, tested rather than assumed.** A test that PUTs an MP4 with `Content-Type: image/png` must still be rejected — if it passes, the platform is reading the client's claim twice and calling the second one a verification.
- [ ] T036 [US2] Commit phase 4.

---

## Phase 5: A virus is rejected, by a scanner that is running (US3)

**Goal**: FR-MED-04's scan, and FR-009's refusal to guess when the scanner is down.

- [ ] T037 [US3] Add ClamAV to `compose.yaml` — **151 MB compressed, 7 layers** (`research.md` R5) — with `INFRA_SERVICES` updated in the same commit (T018's rule).
- [ ] T038 [US3] **The health check must distinguish *running* from *has definitions*.** A scanner with no signature database reports clean on everything, and a check that only proves the socket answers is *"a check that cannot fail for the reason you care about"* — chapter 4.2's `/ping`, 4.9's unset credential and 4.10's bucket are the three precedents.
- [ ] T039 [US3] Speak `INSTREAM` over the socket in `services/media-worker/`, chunked. No client library: the protocol is a length prefix and a terminator, and the object may be 100 MB.
- [ ] T040 [US3] Integration test in `services/media-worker/src/scan.itest.ts`: **the EICAR signature is rejected** — `rejected`, reason `scan_failed`, bytes gone. The standard harmless string, against the real scanner. A test that mocks the scanner asserts that the mock was called.
- [ ] T041 [US3] In `services/media-worker/src/scan.itest.ts`, **a scanner that is unreachable leaves the object `pending`** (FR-009), and the object reaches `ready` once it returns. Both halves, because only the second proves the first was a pause rather than a silent drop.
- [ ] T042 [US3] **The scanner-down test must NOT stop the container** (056-5). `docker compose stop` is an action scoped wider than its own test — the lane runs two files at a time and 4.10's version of this made `gauntlet.itest.ts` answer 503 in a file that never mentions media storage. Point the worker's scanner address at a port the kernel refuses, and make the variable wrong **at the moment of the request** rather than at the moment of the wiring (4.10's second finding, where a second Nest app answered 201 because the service was request-scoped).
- [ ] T043 [US3] **Say what the scan does not promise** in `services/media-worker/src/scan.ts`'s header and in `page.mdx` (FR-014). A signature scanner detects known signatures; SAD R9 names *"scanner misses"* as residual. A reader who finishes this chapter believing *scanned* means *safe* has learned something false.
- [ ] T044 [US3] Measure the scan's share of time-to-`ready` and record it in `specs/059-chapter-4-13/baseline.txt` (SC-006), separated from the fetch and the probe.
- [ ] T045 [US3] Commit phase 5.

---

## Phase 6: The gate, the gauntlet, and two constitution arguments

- [ ] T046 **Gate `GET /v1/media/:mediaId` on `ready`** (FR-012, ADR-14). Measured at `research.md` R4 **before** the state machine existed: the gate alone turns **10 of 76 tests red**, including the isolation gauntlet's own control. With this chapter's transitions in place it should turn none — and if it turns any, that is the finding.
- [ ] T047 **A `rejected` object answers the same 404 as an absent one** (`contracts/` §4). Five conditions, one body, compared whole with `request_id` removed — the discipline 4.11 and 4.12 both built. FR-MED-09's rejection marker is a later chapter and reaches the client through the message payload, not through this route's refusal.
- [ ] T048 **Update 4.12's `delivery.itest.ts` for the gate**, and check what it now asserts. Nine of its tests grant a URL; every one of them needs an object that reaches `ready` first, which makes the suite depend on the worker. **Say whether that is acceptable or whether the fixture should write the state directly** — a delivery test that fails when the scanner is down is a test that reports somebody else's outage.
- [ ] T049 **Run the derivation first and record what it says.** `targets.itest.ts` derives from the running router. This chapter adds internal routes, not public ones, so the derivation may report nothing — and if it comes back green with no new target, that is the finding rather than the absence of one. Nine chapters running have had it name a route first.
- [ ] T050 If a target appears, classify it in `services/api/src/isolation/targets.ts` and expect **"classified but never attacked"** — the third accounting direction 4.8 found.
- [ ] T051 **Attack the internal seam's verdict route**, in `services/api/src/isolation/gauntlet.itest.ts`: a verdict for another tenant's object. The route takes no tenant parameter by design (T012), so the attack's job is to show that the object id alone cannot be used to reach across — with a control first, because **an empty `media_objects` passes a leak check for the same reason an empty page does**.
- [ ] T052 **Write the ADR for `docs/12` §7.3** (FR-013). The line: *a program Relay addresses over a socket is not a program Relay is implemented in*, and the platform already speaks to Postgres, Redis, NATS, MinIO and ClickHouse in four languages that are not TypeScript. What constitution VII would forbid is writing the worker itself in Go — the case ADR-01 named in advance.
- [ ] T053 **Argue the FIFTH SERVICE against SAD §4.2's table** (FR-013, `research.md` R3). VII's other clause, which no artifact in this feature or in `docs/12` had named: different datastore, no transactions, CPU-bound off the request path — all three merge criteria fail. **And the table's own column is "Revisit when"**, so the argument needs a reversal condition.
- [ ] T054 **Argue constitution IV's second writer** (`plan.md`'s table). The api writes `pending`, the worker writes the terminal states; disjoint transitions is the argument, and it is written down rather than assumed because two writers on one column is what that principle names.
- [ ] T055 [P] Record in `gaps.md`: **`media.uploaded` was never built**, and why. The SAD names a consumer and an event; this chapter ships the consumer and no event. A later chapter that adds bucket notifications inherits the measurement rather than the question.
- [ ] T056 [P] Record in `gaps.md`: **time-to-`ready` is bounded below by the sweep interval**, with the measured p50. That is what the sweep gives up against the notice it replaced, and a chapter that published only the 4.2-second figure would be selling the trade rather than stating it.
- [ ] T057 [P] Record in `gaps.md`: **audio and video carry no duration** (FR-MED-04 partly met). On FR-MED-07's SRS 1.18 precedent — *unmet by decision and not by oversight*. Name what it costs a client: no scrubber length before playback.
- [ ] T058 Run `check-lane-scope.py` and record the file count. It read **61** at 058's close; this chapter adds integration tests and the number must rise. A run that reads nothing exits 2.
- [ ] T059 Commit phase 6.

---

## Phase 7: The chapter

- [ ] T060 Write `relay-tutorial/app/(en)/part-4/chapter-13/…/page.mdx`, **2,000–4,000 words outside code fences**, measured with `node relay-tutorial/scripts/prose-words.mjs <page>`.
- [ ] T061 **At least one `TRAP` box** in `page.mdx`, and the candidates are measured rather than invented: the event with no producer, the sweep that costs 4.2 seconds where the spec priced it as waste, and the gate that turns 10 of 76 red if it ships alone.
- [ ] T062 **Publish the sweep-against-notice comparison in `page.mdx` as the chapter's central argument.** The specification was wrong and the measurement is what corrected it; a chapter that presents the sweep as the obvious choice teaches nothing, because it was not obvious enough to survive the spec.
- [ ] T063 **Say in `page.mdx` which half of FR-MED-04 shipped.** Dimensions, not duration, and the reason is four container parsers with MP3 VBR as the hard case — not that duration is unimportant.
- [ ] T064 Register the chapter in `relay-tutorial/lib/tutorial.ts`. `<ChapterHeader id="4.13" />` throws on an unregistered id, so `pnpm build` exits 1 from the moment the page exists.
- [ ] T065 [P] Figures in `figures.ts`, each named by a `<Figure>`. **Pass each diagram as `code`, not `chart`** — 4.11 used `chart` and all three rendered nothing on a page that built and served 125 pages green. `check:figures` is the only thing that asks.
- [ ] T066 A hunk per fenced file this chapter edits, **counted at T006 rather than remembered**. Generate each with `pnpm check:fences --dump`, never with `git diff` against the working tree.
- [ ] T067 **Verify each hunk by exact occurrence count, not `patch --dry-run`** (`gaps.md` 056-7). `patch` applies with fuzz and offset and said yes to seven hunks the checker refused.
- [ ] T068 **Check which state each hunk is written against** before blaming it. `vitest.coverage.config.mts` carries **twelve** appendix hunks and `codes.ts` three; a hunk whose anchor line is one the appendix adds has nothing to match at this chapter, which 4.8, 4.11 and 4.12 each paid once.
- [ ] T069 **Decide the chapter/appendix split before the prose is written.** `repository.ts` carries 50 fences and `schema.ts` 32; deciding afterwards is how a chapter ends up showing a reader 1,576 diff lines to make one point.
- [ ] T070 **There is no Vietnamese twin to write** — check it rather than assume it. `app/(vi)/vi/part-4/` held 3 chapters against en's 12 at 4.12's close, a lag of nine. 050, 056 and 058 all recorded a task that described a corpus instead of checking one.
- [ ] T071 Run `pnpm check:fences` and report the **absolute number**.

---

## Phase 8: The record

- [ ] T072 Write `baseline.txt` carrying every phase's measurements in the order they were taken, and the pinned lane environment.
- [ ] T073 **Re-measure the dependency count and explain the movement** (SC-010). 29 at the open. A new package adds `package.json` entries even if it adds no third-party dependency, so the figure has to be read rather than compared.
- [ ] T074 Write `gaps.md`. **Re-measure every carried item rather than copying it**: 058-1 (the URL outliving its authorisation — now interacts with the gate), 058-3 (the path-param 500 on sixteen routes), 058-4 (three invisible tenancy scopes), 058-5 (no operational corpus at realistic tenant size), 058-6, 058-8 (the `typing.itest.ts` flake), 057-2 (an attachment for an object nobody uploaded to — **this chapter is its answer**), 056-1, 056-2, 055-3, 050-8.
- [ ] T075 In `specs/059-chapter-4-13/gaps.md`, **057-2 and 056-1 are this chapter's to close or narrow in writing.** 057-2 is *"a message can attach an object nobody uploaded to"* and 056-1 is *"an unused slot holds its bytes forever"*. The gate answers the first and FR-MED-10 still owns the second; say which is which rather than claiming both.
- [ ] T076 **Decide whether `docs/04-srs.md` needs a revision, and write it if it does.** Candidates: FR-MED-04 recorded partly met (the duration half), FR-MED-07 moving from *unmet* to *partly met* now that states exist, and ADR-14's delivery gate becoming true for the first time. Five of the last seven chapters amended; 4.11's default of "no revision" was flipped by reading the clause verbatim.
- [ ] T077 **Amend BOTH copies of the Part 4 table** — `docs/12` §3 row 14 **and** `docs/07-tutorial-plan.md`'s copy. Chapters 4.7 through 4.10 each amended one of the two and 4.11 was the first to find the other had received none of them.
- [ ] T078 **Close `docs/12` §7.3 in the table AND in §7** (SC-011). §7.1 was closed by a chapter that did not own it and the entry stayed open for two features, which is the defect 4.5 fixed one entry down and which survived the chapter that found it.
- [ ] T079 Write `traceability.md`. **Enumerate the ids and read each row** — a literal grep produced fourteen alarms at 4.11 and all fourteen were false.
- [ ] T080 Update `CLAUDE.md`'s `<!-- SPECKIT -->` block for the close, including every task premise this chapter falsified by running it.
- [ ] T081 Pin the new files in `vitest.coverage.config.mts`, and **probe both halves**: demand an impossible figure of each new key and confirm it fires, then confirm the measured pins pass. A pin whose key matches no file is silent, and 058's probe is the worked example.
- [ ] T082 **Read `coverage-summary.json`, not the text table.** v8's text reporter omits a file at 100/100/100/100, which cost 056 three of five new files.
- [ ] T083 **Answer constitution VI's 100%-branch clause per arm** in `services/media-worker/src/` — for the **verdict**, which has four outcomes and two terminal states. Delete each arm and re-run, as 4.11 and 4.12 did. 4.12's probe found three tenancy predicates no single mutation could see; the question here is whether the transient arm is reachable at all without the scanner being down.
- [ ] T084 Run the tutorial job's six gates, named from `ci.yml` rather than memory, and **read each one's counted success line**. `lint` is the one with no counted line at all.
- [ ] T085 **Add the worker and the scanner to `.github/workflows/ci.yml`, and put the step where a failure cannot skip it.** 4.10 learned that a provisioning step after the first failure is skipped on exactly the runs where the lane it provisions for still executes.
- [ ] T086 Run `pnpm test:outsider` with the outsider job's own preconditions, and extend the sealed suite to watch an object reach `ready` from outside. **That suite asserted a fact the platform publishes as false until 4.12 fixed it**; check what this chapter's gate does to its media test, which currently fetches the bytes of a `pending` object.
- [ ] T087 **Rebuild in all three senses before believing a run.** `pnpm build` for the spawned `dist`, `docker compose --profile services build` for the container image, and the protocol package before anything reads a type from it. 4.11 lost a confusing failure to each of the first two.
- [ ] T088 Run the quickstart **unmodified**, and only then let it say every command was run before it was written. NFR-USE-03 is a `T` clause at 100% and `ci.yml` contains the word `quickstart` zero times, so this run is its whole verification. 4.11's was wrong five times; 4.12's three, and the first of those was that chapter's own subject.
- [ ] T089 Run `pnpm check:errors` by hand, in both directions, and assert **34/34 unchanged**. It is a script no CI job runs (055-3).
- [ ] T090 Tag `part4-ch13` on `relay-platform`, commit, and push all three repositories.
- [ ] T091 After the push, confirm CI. **Compare per error, not per colour — and over more than one run.** 4.11 compared a single run and called the set identical; three runs read 3, 6, 3. 4.12's baseline was 4 distinct and its own run matched in both directions, with one query-plan assertion that comes and goes.

**Checkpoint**: an image uploaded by a customer is read once by one service, and only then can anybody else read it.

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 (setup) ───────────────► everything
Phase 2 (states + seam) ───────► US1, US2, US3   — no verdict has anywhere to go without it
Phase 3 (US1) ─────────────────► US2, US3        — there is no grant to refuse against
Phase 5 (US3) ─────────────────► T046            — the gate needs `ready` to be reachable
T005 ────► T027, T044            the before figures must exist before the after ones
T007 ────► T018                  count the containers before adding one
T008 ────► T009 ────► T010       write the constraint, run it red, then declare it
T037 ────► T038 ────► T040       the scanner, its health check, then what it catches
T046 ────► T047, T048            gate first, then what the gate answers
T049 ────► T050 ────► T051       derive, classify, attack — in that order
T006 ────► T066                  a hunk list counted, not remembered
T069 ────► T060                  the split decided before the prose
T076 ────► T077, T078            write the amendment once, apply it everywhere
T087 ────► T086, T088            three kinds of stale build, before anything is believed
T090 ────► T091                  CI is only observable after a push
```

### User Story Dependencies

**US1 is the MVP and it is not independently shippable.** A worker that marks objects `ready`
without scanning them is worse than no worker: it would turn ADR-14's gate from a safety
property into a rubber stamp, and the gate is what makes `ready` mean anything. **Phases 2, 3, 4
and 5 are one shippable increment.**

US2 and US3 are independent of each other — a declaration check and a signature scan are
different refusals reached by different code — and either could ship first. US2 is ordered first
because it needs no new container.

### Parallel Opportunities

- **T003, T004** — different commands, no shared state.
- **T055, T056, T057** — three `gaps.md` entries, written independently.
- **T065** — figures, while the prose is drafted.
- **Nothing in phase 2 is parallel.** The migration, the constraint probe, the declaration, the
  seam and the worker skeleton are one chain.
- **T037 can start early**, because pulling a 151 MB image is the longest single wait in the
  feature and it blocks only phase 5.

---

## Implementation Strategy

**MVP is phases 2 through 5**, for the reason above: `ready` has to mean scanned.

**What this chapter could get wrong, ranked by how quietly it would happen:**

1. **Verifying the client's claim twice and calling the second one a verification.** The store
   echoes back whatever `Content-Type` the client PUT with, so a worker that reads the response
   header has learned nothing and will pass every test somebody thinks to write. **T035 is the
   test that catches it** and it is in US2 rather than US1 on purpose.
2. **A scanner with no definitions.** Reports clean on everything, answers its socket, passes a
   health check that asks whether the socket answers. T038.
3. **Marking an object `rejected` because the scanner was down.** Deletes a customer's photo to
   record an outage. T041, and the test has to prove the pause was a pause by letting the
   scanner come back.
4. **A dimension reader that is right for PNG and silent for WebP.** One format per test. T024.
5. **Shipping the gate before the state machine.** Measured: 10 of 76 red, including the
   gauntlet's own control. T046 is ordered after phase 5 for that reason and not for tidiness.
6. **Believing a green run against a stale build.** Three kinds, and this chapter adds the
   fourth thing that can be stale — a scanner container whose definitions are from last week.
   T087.
