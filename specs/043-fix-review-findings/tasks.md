# Tasks: Fix the platform implementation review's findings

**Input**: Design documents from `/specs/043-fix-review-findings/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/, quickstart.md

**Tests**: included. Constitution VI requires it, FR-007 asks for one by name, and every
acceptance scenario in the spec is written as something to run.

**Organization**: by user story. US1 is the MVP and the other three do not depend on it —
but every claim they make is measured by the lane US1 repairs, so shipping US2 first means
validating it with an instrument known to be wrong.

**EVERY NUMBER IN THIS FILE WAS MEASURED DURING ANALYSIS, AND THE LANE MOVES.** The 741
subscriptions, the zero rejectable avatar rows, the 12-and-5 split, the 5.39 seconds of budget
headroom, the 7.41 s the e2e package costs — each was taken with a command that is written
beside it, and this session's battery moved the row counts twice while the analysis was running.
**Re-run the command before acting on the number.** A premise inherited from a record and never
re-run is the defect this repository has caught in three of its own chapters.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: different file, no dependency on an incomplete task
- **[Story]**: US1–US4, on user-story phases only

## Path conventions

Three repositories. `relay-platform/` holds code, `relay-tutorial/` holds the published
listings and the gates, and the root holds `docs/` and `specs/`. Paths below are written
from the repository root.

---

## Phase 1: Setup

**Purpose**: a record to write into, instruments that work, and a lane whose state is known.
**Re-take every measurement this phase records** — the numbers in T003 and T006a were taken
during analysis, on a lane that has since run a twenty-run battery.

- [X] T001 **Already copied, during analysis pass 9** — the six instruments are in `specs/043-fix-review-findings/` and were run against this feature's artifacts there. Verify and re-run each. **Nine passes of analysis had checked 043 with tools pointed at 042**, because this task used to run at implementation time; all five that produce findings failed on first contact. **One staleness is already fixed and is the kind to expect**: `check-refs.py`'s path pattern listed `ts|mts|md|txt|mdx|json|yaml` and not `mjs`, so it reported the two `.mjs` files this feature adds as tasks naming no file. **Three still need their per-feature configuration** — `check-quickstart.py`'s OWED and MENTIONED_NOT_OWED lists, `check-checklist.py`'s file enumeration, and `sweep.py`'s expectation of `### Phase N` headings in `plan.md` and of a read-path table this feature's data model does not have, are all 042's, and each reports about ten problems that are its configuration rather than this feature's artifacts. **Expect every copy to arrive stale** — chapter 3.23's arrived with 31 stale pairs from its predecessor and a docstring naming the wrong chapter, and both were found by running them rather than by reading them. `gaps.md` 3.22-8 has recorded this copy-forward with no owner for five chapters; this is the sixth.
- [X] T001a Re-run all six instruments in `specs/043-fix-review-findings/` and confirm each exits 0. **This task was created to own per-feature configuration and that turned out to be one line.** Analysis pass 10 filed twenty-four complaints from `check-quickstart.py` and `check-checklist.py` as the predecessor's configuration without reading them; pass 11 read them and **twenty-three were real** — thirteen success criteria named in scenario headings rather than in the `**Expected**` lines that prove them, and eight files `spec.md` names that the checklist did not enumerate. Both are fixed. The one that was configuration was a `MENTIONED_NOT_OWED` exemption for a file this feature's quickstart no longer mentions.
- [X] T002 [P] Create `specs/043-fix-review-findings/baseline.txt` and pin the nine lane environment variables in it, copied from `specs/042-chapter-3-24/quickstart.md`. Tasks that spawn a service read them from here.
- [X] T003 Run `node relay-platform/scripts/stream-info.mjs` and the four row-count queries from `quickstart.md`, and write the starting state into `baseline.txt`. **This is the before half of a measurement**; the after half is T062's battery, and without this one that number means nothing.
- [X] T004 Clear the lane by hand this once. **`quickstart.md` scenario 1 names `scripts/reset-lane.mjs` and T014 is what writes it**, so this task cannot follow that scenario and spells the steps instead: connect to NATS and purge `ANALYTICS`, `DELIVERIES` and `EVENTS`; delete every consumer on each; in `relay-platform`, `SET relay.allow_global = 'webhook_deliveries'` then delete `pending` rows older than 30 minutes; and `rm -rf` every `node_modules/.vite/vitest` directory in the workspace. **The cache removal is not optional and it is the half that gets forgotten** — the runner orders files by what failed last time, so leaving it makes the first run's result depend on a previous session.

---

## Phase 2: Foundational (blocking prerequisites)

**Purpose**: establish that the tree is green before anything is edited, so a later red is attributable.

- [X] T005 Run all fourteen gates and write every exit code into `baseline.txt`: `typecheck`, `lint`, `build` from `relay-platform`; `check:fences`, `check:docs`, `check:figures`, `check:srs`, `check:errors` from `relay-tutorial`; and this feature's six Python instruments. **Assign each exit code to a variable outside any pipeline** — `fail=1` inside a `for … done | sort` runs in a subshell and dies with it, which is how chapter 3.24 printed "ALL GATES: GREEN" over a red one.
- [X] T006 Read `relay-tutorial/fences/post-series.md` and write into `baseline.txt` which of this feature's thirteen platform files already have an appendix hunk. **Three do** (`harness.ts`, `dispatcher.itest.ts`, `repository.ts`), and a second hunk for the same file must be appended after the first rather than merged into it.
- [X] T006a Measure and record in `baseline.txt` what the e2e package costs today: the `@relay/e2e` duration line from one integration run (7.41 s across three suites in the last battery), the count of `boot()`/`stop()` cycles per run, and the headroom on the slowest green run of the last battery (234.61 s against a 240 s budget, so **5.39 s**). **This feature spends that headroom**: T010 replaces a flat 200 ms teardown with waiting for processes to exit, and T011 adds a fourth suite that boots twice. Without this number, T019 cannot tell a budget overrun from a slow machine. (SC-012)

---

## Phase 3: User Story 1 — the test lanes report the product (Priority: P1) 🎯 MVP

**Goal**: an integration run's result depends on the code, not on the file order or on debris.

**Independent test**: twenty consecutive runs from a cleared lane with the sequencer caches
removed, and the container-free lane with every container stopped.

- [X] T007 [US1] Change `relay-platform/services/api/src/main.ts` to log the port the server actually bound rather than the value of the `port` variable. **The current line logs the requested port**, so `PORT=0` would log `0` — read it off the listener instead. This is a correctness fix on its own terms and not only a favour to the harness. (FR-002)
- [X] T008 [P] [US1] Make the same change in `relay-platform/services/gateway/src/main.ts:151-154`, which has the identical shape. (FR-002)
- [X] T008a [US1] Add the e2e lane to the port map (FR-026) at `relay-platform/services/gateway/src/limits.itest.ts:16`, **before T009 changes it**. The map has nine entries and **not one for `packages/e2e`** — `grep -c e2e` on the file that owns it returns zero — while the harness hard-codes 4100, 4101 and 4102 inside the 4100-4300 that map registers to `limits.itest.ts`. **The overlap is latent, not active**: `package.json:15` runs turbo with `--concurrency=1`, so these two packages never execute together and nothing in the integration lane can make them meet. Register it anyway — the map's doctrine is *"two files drawing from one range is the same fault as two files sharing a fixed port"*, and a range that is safe only because of a flag in another file's script is a range nobody should have to check twice. Record the range the e2e lane takes after T009 (the OS ephemeral range, not a band in this map) so the next reader does not re-register a fixed one. **This file is NOT fenced, and that is the second half of the finding.** The only titled fence naming it anywhere is `title="services/gateway/src/limits.itest.ts (excerpt)"`, and `check-fence-chain.mjs:42` skips any title containing `(excerpt)` — zero real fences, zero appendix hunks. **The edit costs no amendment and is invisible to `check:fences`**, which is `gaps.md` 3.22-3's whole point, and this is one of the ten files that item names. Analysis pass 10 asserted the opposite from memory; pass 13 checked it.
- [X] T009 [US1] Change `packages/e2e/src/harness.ts` to spawn each child with `PORT=0` and take the bound port from the child's own log line, which the harness already captures at `harness.ts:342`. **Do not probe for a free port and pass it** — the window between the probe and the child's bind is the bug being fixed. (FR-002)
- [X] T010 [US1] Change `harness.ts:534`'s `stop()` to await each child's `exit` with a bounded timeout instead of sleeping 200 ms. **Await the whole set, not each in turn**, and give the timeout a distinct failure message so a hung child is not reported as a port problem. (FR-001)
- [X] T011 [US1] Add `relay-platform/packages/e2e/src/harness.itest.ts` that boots, stops, and boots again inside one file, and asserts the second boot's api answers a request rather than only that `boot()` returned. **This is the assertion that would have caught the defect**: today the health check passes against the dying predecessor, so a test that only checks `boot()` returns cannot see it. (FR-001)
- [X] T012 [P] [US1] Change `relay-platform/services/dispatcher/src/dispatcher.itest.ts:407`'s `afterAll` to delete `itest-expand-${run}` and `itest-deliver-${run}`. `services/api/src/consumer/consumer.itest.ts:201` already does this and its comment says why — **the fix is written in the file next door and was never applied here.** (FR-003)
- [X] T013 [US1] Give `dispatcher.itest.ts`'s own durables `DeliverPolicy.New` so a dirty stream cannot starve a fresh run. Leave `services/dispatcher/src/main.ts`'s default alone: production replaying from the start is correct. (FR-004)
- [X] T014 [US1] Write `relay-platform/scripts/reset-lane.mjs` that purges the streams, deletes the durables, and clears stale `pending` deliveries. Put it beside `stream-info.mjs`, which can already read the state this clears. **Guard it with an explicit opt-in flag, not with a guess about the URL** — "looks like the lane" is not checkable and every heuristic for it is wrong on somebody's machine; require `--yes-this-is-my-test-lane` and exit non-zero without it. **And the seeded demo tenant MUST survive**: the constitution requires `docker compose up` to bring the stack up with one, so the script deletes lane debris and never the seed. Assert both in the script's own test. (FR-005)
- [X] T015 [US1] Take the split from `research.md` R2 rather than re-deriving it — **analysis pass 4 measured it** with `RELAY_REDIS_URL=redis://127.0.0.1:6399 vitest run src/connections.test.ts`, which reports `12 failed | 5 passed`. Five need no broker: `does not throw for a slot the connection never held`, `does not throw when it holds nothing`, `returns unenforced rather than zero when Redis is unreachable`, `keeps the heartbeat strictly inside the bound` and `states the maximum in exactly one place`. **Re-run that one command to confirm the count before moving anything** — the split is a measurement, and a measurement taken in analysis is stale by implementation. (FR-024a)
- [X] T016 [US1] Move the twelve assertions that need a broker from `relay-platform/services/gateway/src/connections.test.ts` into `connections.itest.ts`, keeping each assertion's behaviour unchanged (FR-024, FR-024a). **The five stay, and that is FR-006a**: emptying the container-free lane would satisfy FR-006 and prove nothing, so confirm afterwards that `connections.ts` still meets its coverage pin. The five measured in T015 stay — the first needs a *dead* broker and the second reads a file. **All five stay**, and all five should leave the `describe` that owns the `beforeEach` — not because it breaks them (pass 4 measured that it does not; `createConnections` is lazy) but because a container-free lane holding a Redis client it never uses is untidy.
- [X] T017 [US1] Write the forced-race test for a concurrent edit and deletion of one message in `relay-platform/services/api/src/db/repository.itest.ts` (FR-007), driving the two writes from two separate pool clients. **This is the one US1 task that is not about a lane**, and US1's independent test was widened in analysis pass 7 to reach it — a story whose test cannot see a requirement is not independently testable. **Do not start from `Promise.all`** — chapter 3.22 spent a phase learning that two operations on one client serialise at the socket, and seeing a race needed two separate clients. Assert that both orderings end in a tombstone; that claim is what is untested, not the outcome.
- [ ] T018 [US1] Append an amendment hunk to `relay-tutorial/fences/post-series.md` for each **fenced** file changed in this phase. **Fourteen of the fifteen this feature edits take one; `limits.itest.ts` does not** — its chain is excerpt-only, so there is nothing to amend and nothing to catch a mistake in it either. **Run `check:fences` after each one, not once at the end** — it reports only the first difference per file, so "three problems" can be thirty stale lines.
- [ ] T018a [US1] Sweep the published chapters for prose this phase falsifies and amend each hit (FR-027). **No gate can find these**: `grep -rn '4100\|4101\|4102\|200 ms\|200ms' 'relay-tutorial/app/(en)/part-*/*/*/page.mdx'` returns hits in six pages, and the two that matter are not fences of any file. `part-2/chapter-08/…/page.mdx:908` publishes an **untitled** ` ```text ` transcript — `api up on 4100`, `gateway 1 up on 4101`, `ws://127.0.0.1:4102` — as the milestone's proof the journey runs, and an untitled fence names no file so `check-fence-chain` skips it. `part-3/chapter-13/…/page.mdx:1542` publishes the port map as a text block, under a sentence warning that a range *"goes stale the next time a file is added"* — **and line 1509 publishes it again as an `(excerpt)` fence**. **Amend both.** An excerpt fence falls between this feature's two mechanisms: a prose sweep does not think to look inside a fence, and the chain check skips anything titled `(excerpt)`. **Mirror every amendment into the Vietnamese page.**
- [ ] T019 [US1] Verify: `node relay-platform/scripts/reset-lane.mjs`, remove the sequencer caches, then twenty consecutive `pnpm test:integration`. Then `docker compose down` and `pnpm -s test`. Record both, and record which durable consumers outlive one run — **service-created durables are not test debris and are counted separately** (SC-003). (FR-006, SC-001, SC-002)
- [ ] T019a [US1] Re-measure the e2e package's duration and the integration total against T006a, and settle SC-012. If the total exceeds 240 s, **record which of three was chosen and why**: raise the budget with this measurement attached, make `harness.itest.ts` boot once instead of twice, or bound the teardown wait lower. **Do not let the budget quietly become whatever the lane now costs** — a budget that follows the measurement is not a budget, and this feature's own fixes are what spend it.

**Checkpoint**: US1 stands alone. Every later story's verification runs on this lane.

---

## Phase 4: User Story 2 — a client is refused at the boundary it wrote to (Priority: P2)

**Goal**: the published message-length rule is enforced at all three doors, and no avatar URL can carry an executable scheme.

**Independent test**: send the same over-long text three ways; attempt each of four schemes.

**Re-take T028's measurement before relying on it.** Analysis measured zero stored avatar values
the new rule would reject; that is a fact about this database on that day.

- [ ] T020 [US2] Export `MESSAGE_TEXT_MAX` from `relay-platform/packages/protocol/src/frames.ts`, beside `messageSchema`. **Not from `attachments.ts`**, whose six exports are all about attachments — a message-text bound on that shelf is the drift this task exists to remove. `internal.ts` already imports `messageSchema` from `./frames.js`, so the direction exists and no cycle is created. The value is 8000, which is what the REST and internal doors already carry. (FR-008)
- [ ] T021 [US2] Import it in `packages/protocol/src/frames.ts:34`, which today declares `z.string()` with no bound at all. (FR-008)
- [ ] T022 [P] [US2] Import it in `packages/protocol/src/internal.ts:32`, replacing the literal. (FR-008)
- [ ] T023 [P] [US2] Import it in `relay-platform/services/api/src/messages/messages.schema.ts:18`, replacing the literal. **Check `editMessageBodySchema` at the same time**: chapter 3.24 found it borrowing the send's bound by reference, so relaxing one silently relaxed the other. Two schemas that must differ cannot share a reference. (FR-008)
- [ ] T024 [US2] Make the gateway's refusal for over-long text carry a registered code and `field`, in `relay-platform/services/gateway/src/session.ts`. `sendError` has taken an optional `field` since chapter 3.24; no new plumbing is needed. (FR-009, FR-010)
- [ ] T025 [US2] Build `relay-platform/packages/protocol` so its `dist` carries the new export from `packages/protocol/src/frames.ts`, then type-check the api and the gateway against it. **Consumers resolve `@relay/protocol` through `dist`**, so a protocol change is invisible until it is built — and the compiler's list of call sites is the inventory, not a grep. (FR-008)
- [ ] T026 [US2] Write the tests in `relay-platform/packages/protocol/src/frames.test.ts`, `services/api/src/messages/messages.itest.ts` and `services/gateway/src/session.itest.ts`: the same over-long text refused at all three doors, and the socket refusal naming `payload.text` and making no internal request. **Assert the absence of the internal request**, not only the refusal — a test that checks the refusal alone passes whether or not the hop was saved. (FR-010, SC-004)
- [ ] T027 [P] [US2] Add `AVATAR_URL_SCHEMES` and apply it in `relay-platform/services/api/src/users/users.schema.ts:54` and `:92`, parsing with `new URL(value).protocol` rather than matching text. `packages/protocol/src/attachments.ts` is the precedent and it exists because research measured that the generic validator accepts `javascript:`. (FR-011, FR-012)
- [ ] T028 [P] [US2] Measure and record in `baseline.txt` how many stored `avatar_url` values the new rule would reject (FR-013). Research measured zero in this database. **Record it as a measurement of this database**, not as a claim about a customer's.
- [ ] T029 [US2] Write the tests in `relay-platform/services/api/src/users/users.itest.ts`: `javascript:`, `data:`, `file:` and `vbscript:` each refused with `field: "avatar_url"`, and `https:` accepted. (SC-005)
- [ ] T030 [US2] Append an amendment hunk to `relay-tutorial/fences/post-series.md` for each file changed in this phase, and re-run `check:fences` after each. **Then sweep this phase's published prose (FR-027)**: `avatar_url` appears in five chapter pages and the message-length rule in more, and no gate reads any of it.
- [ ] T031 [US2] Verify against `quickstart.md` scenarios 2 and 3, including the grep that proves the maximum is defined once. (SC-004)

**Checkpoint**: US2 is independent of US1 and US3.

---

## Phase 5: User Story 3 — a customer's mistake is labelled as theirs (Priority: P2)

**Goal**: every refusal a customer can cause names the cause, and every close code has a page.

**Independent test**: read the `code` in each response body, not the status. Look up each close code.

**Re-take T037's measurement before relying on it.** Analysis measured 741 subscriptions to
`channel.created` out of 32,606 type-rows, and the whole design rests on that comparison.

- [ ] T032 [US3] Add `WEBHOOK_EVENT_TYPES` — the eight types FR-WHK-02 declares, each marked with whether the platform emits it. **Derive `OUTBOX_EVENT_TYPES` from it rather than maintaining both.** Two lists that must agree and are maintained separately is what `gaps.md` 3.23-4 records about `targets.ts`, and what `eslint.config.mjs`'s own comment says *MUST AGREE* with nothing comparing them. (FR-016)
- [ ] T033 [US3] Make adding a type to `WEBHOOK_EVENT_TYPES` without deciding `emitted` a compile error, and add a test asserting the exact declared set and its count. Chapter 3.24 added two error codes where its plan expected one, and `codes.test.ts`'s exact-count assertion is what caught it. (FR-016)
- [ ] T034 [US3] Add one error code per customer-caused webhook refusal to `packages/protocol/src/codes.ts`. **Read the filter's ladder before choosing statuses**: `ProtocolErrorFilter` derives a code from 400, 401, 403 and 404 and answers `internal_error` for anything else, which is why a bare 422 misattributes the fault. (FR-014)
- [ ] T035 [US3] Replace the five bare `UnprocessableEntityException` throws in `relay-platform/services/api/src/webhooks/webhooks.service.ts` at lines 88, 193, 196, 202 and 210 with `protocolError(code, message, 422)`, following chapter 3.24's `media_not_available` precedent. (FR-014)
- [ ] T036 [US3] Change `assertEventTypes` at `webhooks.service.ts:208` to validate against the **declared** eight. **Not against `OUTBOX_EVENT_TYPES`** — the review and `gaps.md` 3.23-1 both recommend that and both are wrong: 741 stored subscriptions name `channel.created`, which FR-WHK-02 declares and the platform does not emit yet. Accept those and say the type is not emitted yet. (FR-016)
- [ ] T037 [P] [US3] Re-run the event-type query and record the count in `baseline.txt` (FR-017), including how many name a declared-but-unemitted type and how many name nothing at all.
- [ ] T038 [US3] Write a section in `docs/08-error-reference.md` for each new code, reachable from its `docs_url`. Constitution V and NFR-USE-05 both require it and `check:errors` enforces it. (FR-015)
- [ ] T039 [US3] Document all six close codes in `docs/08-error-reference.md`. **Inside the `**Status:**` line of the error code that carries each one** — chapter 3.21's convention. A `## 4001` heading fails `check-error-codes.mjs:59`'s orphan check with no exemption. (FR-018)
- [ ] T040 [US3] Extend `relay-tutorial/scripts/check-error-codes.mjs` to compare `CLOSE_CODES` against the reference's text as it already does for `ERROR_CODES`. (FR-019)
- [ ] T041 [US3] Test `relay-tutorial/scripts/check-error-codes.mjs` red, three ways: remove one close code's text from `docs/08-error-reference.md`, add a close code to `packages/protocol/src/codes.ts` with no text, and rename one. **A checker that has never failed has an unverified class list.** (FR-019)
- [ ] T042 [US3] Write the route tests: each of the five refusals asserted **by code**, and a misspelled event type refused while `channel.created` is accepted with the not-emitted-yet answer. Today `webhooks.itest.ts:90` asserts the status and the message text, which is why nothing has caught this since chapter 3.5. (SC-006, SC-008)
- [ ] T043 [US3] Append an amendment hunk to `relay-tutorial/fences/post-series.md` for each file changed in this phase, and re-run `check:fences` after each. **Then sweep this phase's published prose (FR-027)**: `OUTBOX_EVENT_TYPES` appears in three chapter pages, and this phase changes what subscriptions are validated against.
- [ ] T044 [US3] Verify against `quickstart.md` scenarios 4, 5 and 6. (SC-007)

**Checkpoint**: US3 is independent of US1 and US2.

---

## Phase 6: User Story 4 — the records read true (Priority: P3)

**Goal**: no published document states something the tree contradicts.

**Independent test**: read the revision ledger top to bottom; read each amended clause against the behaviour it now describes.

- [ ] T045 [US4] Reorder `docs/04-srs.md` Appendix D so the version column ascends. It reads 1.0, 1.1, 1.2, 1.3, 1.4, **1.7, 1.6, 1.5** — three chapters each inserted above their predecessor. (FR-020)
- [ ] T046 [US4] Write `relay-tutorial/scripts/check-revision-order.mjs` for `docs/04-srs.md` and add it to the `check:docs` script. It costs no amendment: the tutorial's own scripts are fenced by nobody. (FR-021)
- [ ] T046a [US4] Add the same rule for this feature's own success criteria to `specs/043-fix-review-findings/check-refs.py`, which already reads `spec.md`. **Not to the tutorial's script** — `relay-tutorial` is its own git repository, nothing in it reads `../specs`, and `sync-docs.sh`'s precedent for `../docs` errors out when the parent is absent. A feature directory is transient; a gate pointed at one dies with it. (FR-021a)
- [ ] T047 [US4] Test both gates red: move one row in `docs/04-srs.md` Appendix D, and move one success criterion in `specs/043-fix-review-findings/spec.md`. Restore both. (FR-021, FR-021a)
- [ ] T048 [P] [US4] Correct the bot/quota finding in `docs/09-platform-implementation-review-2026-09-03.md` to state what `assertWithinQuota` does: the message hard cap throws before the sender test, and the exemption is from the unique-active-persons ceiling alone (FR-022). (SC-010)
- [ ] T049 [US4] Correct the same review's webhook remedy to name the declared set, and re-point `specs/041-chapter-3-23/gaps.md` item 1, whose recommended fix has the same defect. **Amend by annotation** — chapter 3.23 established that a closed ledger's factual error is corrected with a bracketed note naming the amender, so the original claim stays readable. (SC-010)
- [ ] T050 [US4] Retire the migration generator: delete `relay-platform/services/api/migrations/meta/`, remove the `generate` step, and state in `drizzle.config.ts` that migrations here are hand-written and reviewed against SAD §6.1. **Add an assertion that fails if `migrations/meta/` or the generate script returns** (FR-023, FR-023a) — a decision recorded only in a comment is a decision the next contributor reverses by accident. The constitution already says this — *"migrations remain versioned, forward-only, hand-reviewed SQL"* — so the tooling has contradicted it since chapter 3.9, not the other way round.
- [ ] T051 [US4] Amend FR-RTM-10 in `docs/04-srs.md` to state the bound that applies when the fabric is unavailable, citing ADR-20, which already says *"exceeding the clause by 55 seconds"* and gives the arithmetic. (FR-025, FR-025b)
- [ ] T052 [US4] Amend FR-RTM-09 in `docs/04-srs.md` to state that the connection limit is best-effort and what happens when it cannot be checked, citing ADR-23. (FR-025a, FR-025b)
- [ ] T053 [US4] Read both amended clauses in `docs/04-srs.md` against the measured behaviour and confirm neither permits more than the platform already does (FR-025c). **This is the one check no instrument can run**: "amend the clause" and "weaken the clause" are one edit apart, and every gate here compares bytes. (SC-011)
- [ ] T054 [US4] Add revision **1.8** to `docs/04-srs.md` Appendix D for this feature's two clause amendments — **appended, below 1.7**, which is the shape T046's gate now enforces. (FR-020)

**Checkpoint**: US4 is independent of every other story.

---

## Phase 7: Polish and close-out

**Scope this phase to the stories that shipped.** tasks.md claims US1 alone is a viable
stopping point, and this phase was written as though all four always land. Per story:
T055-T057 (coverage and the ratchet), T058 (titles) and T059 (credential scan) run over
whatever shipped and their file lists shrink accordingly — T058's ten files include
`users.itest.ts` from US2 and `webhooks.itest.ts` from US3, so a US1-only close-out reads four.
T060, T060a and T061 record what shipped and say what did not. **T062-T064 run whole either
way**: a battery, a gate set and a files-changed count do not divide by story.

- [ ] T055 Run the coverage lane with the pinned variables and read `coverage/coverage-summary.json`, not the text table — the text reporter omits a file at 100% on all four metrics, and a failing test writes no report at all.
- [ ] T056 For any uncovered arm named in `relay-platform/coverage/coverage-final.json` for a file this feature touched, **ask whether the code should be deleted before asking for a test**. The ratchet has removed code five times. And remember what 100% does not mean: v8 records a `&&` operand as covered when it was *evaluated*, not when it went both ways.
- [ ] T057 Re-pin the changed files in `relay-platform/vitest.coverage.config.mts`. **This edit breaks that file's chain, which ends in the appendix rather than in a chapter** — it did so in chapter 3.24's close-out and cost a late scramble.
- [ ] T058 [P] Read every new test's title against its assertion, one at a time, in every file this feature adds tests to — named rather than described: `packages/protocol/src/frames.test.ts`, `packages/e2e/src/harness.itest.ts`, `services/api/src/db/repository.itest.ts`, `services/api/src/messages/messages.itest.ts`, `services/api/src/users/users.itest.ts`, `services/api/src/webhooks/webhooks.itest.ts`, `services/gateway/src/session.itest.ts`, `services/gateway/src/connections.test.ts`, `services/gateway/src/connections.itest.ts`, `services/dispatcher/src/dispatcher.itest.ts`. **Ten, and expect the count to be wrong** — chapter 3.24's task named nine and the tree held twenty-two. **Strip any task id from a title before it ships**: 3.22 wrote one, 3.23 fifty-two, 3.24 thirty-three. Requirement ids belong there; task ids do not.
- [ ] T059 [P] Run the credential scan over this feature's diff and record every pattern searched and every hit classified in `baseline.txt`. **Cover all three repositories** — chapter 3.24's first run skipped the root, which is where all fifty hits were.
- [ ] T060 Write `specs/043-fix-review-findings/gaps.md`, carrying **twenty-three items, not twenty-two** — chapter 3.24's five, the seventeen numbered before them, and **the one that is not numbered**, which its predecessor files under `## THE ONE THAT IS NOT NUMBERED, BECAUSE ELEVEN CHAPTERS HAVE NUMBERED IT`. All **re-measured against the tree rather than copied**. **"Five items and the seventeen before them" excluded the unnumbered one by arithmetic**, which is how an item with no owner finally disappears — not by being resolved. `specs/036-chapter-3-18/reader-protocol.md`: 45 minutes, six questions, one person who has not read the work. Three of the seventeen were wrong on the day they were written. Close 3.23-1, 3.23-8, 3.23-9, 3.24-1 through 3.24-5, and re-point the rest. **And open one this analysis found and this feature does not close**: `check-fence-chain.mjs:77` collects a fence only if it matches `title="…"`, so an untitled fence is never compared to anything. Measured across the 41 English chapter pages: **758 titled, 146 untitled — 16% of opening code fences are outside every gate.** `gaps.md` 3.22-3 records excerpt-only chains, which are skipped *by* title; this is one step further out. T018a repairs one of the 146 because pass 2 happened to grep for a port number. The class needs an owner.
- [ ] T060a Mark **all twenty-one rows** of `docs/09-platform-implementation-review-2026-09-03.md` with what happened to each (SC-013): closed, and by what; or open, and whose it is. **Two tables, not one** — ten current findings and three roadmap rows in the first, and eight more in "Part 3 SRS/SAD/ADR amendment assessment", which the review calls *concerns* rather than findings. **This feature closes four of those eight** (ADR-20's revocation bound, ADR-23's fail-open cap, the bot-quota error, the misordered ledger), and "every finding" would have left all eight unmarked. **The feature is named after this document and edits it twice without ever telling it the work is done** — T048 and T049 only correct errors in it. Two rows stay open on purpose and must say so: the moderation audit log is chapter 4.7's, and the three roadmap rows are Part 4's. **If only some stories shipped, mark only those** — a review that claims more than was built is the defect this task exists to prevent.
- [ ] T061 Re-derive the files-changed count from `git diff --name-only`. **Expect it to be wrong the first time**: the plan says thirteen platform files, and the coverage ratchet in T057 makes it fourteen the way it made 3.23's 33 become 34 and 3.24's 36 become 37. (SC-009)
- [ ] T062 Run the twenty-run battery of `pnpm test:integration` from a cleared lane with the sequencer caches removed. **Nothing else runs on the machine, including your own tooling.**
- [ ] T063 Record the battery in `baseline.txt` with the mean over the green runs, the stdev, and every failure's file and message. **Report the mechanism, not the fraction and not only the interval** — a Clopper-Pearson interval assumes independent trials, and chapter 3.24's twenty runs alternated green and red for fifteen consecutive runs because the test runner reorders on failure.
- [ ] T064 Run all fourteen gates last — `typecheck`, `lint`, `build` in `relay-platform`; `check:fences`, `check:docs`, `check:figures`, `check:srs`, `check:errors` in `relay-tutorial`; and this feature's six instruments in `specs/043-fix-review-findings/` — with every exit code captured into a variable outside any pipeline.
- [ ] T065 Commit the close-out records, then trim `CLAUDE.md` and update the `SPECKIT` block to point past this feature.

---

## Dependencies

    Phase 1 (T001-T004)  ──▶ Phase 2 (T005-T006) ──┬──▶ US1 (T007-T019)  P1, MVP
                                                    ├──▶ US2 (T020-T031)  P2
                                                    ├──▶ US3 (T032-T044)  P2
                                                    └──▶ US4 (T045-T054)  P3
                                                             │
                                                             ▼
                                                    Phase 7 (T055-T065)

**No user story depends on another.** Each can be built, tested and shipped alone.

**But their verification does depend on US1**, and that is a different relationship. US2's
and US3's route tests run in the lane US1 repairs. Shipping US2 first is possible; believing
its twenty-run evidence before US1 lands is not.

**T002 precedes every task that writes `baseline.txt`** — T003, T006a, T028, T037, T059 and T063 all append to a file
T002 creates. Its `[P]` marker means "alongside T001", not "alongside T003".

**Within US1**: T008a precedes T009 — register the range before changing it, so the map records what was true. T007 and T008 must precede T009, because the harness reads the log line those
tasks make correct. T015 must precede T016 — classify before moving. Everything else marked
`[P]` is a different file.

**Within US3**: T032 precedes T036, and T034 precedes T035 and T038.

## Parallel execution

Four agents, or four sittings, one per story after Phase 2:

    US1  T014 (new file) alongside T012 — but NOT T012 with T013, nor T048 with
         T049: each of those pairs edits one file, and `[P]` means a different one
    US2  T022, T023 together (two schemas), T027 and T028 together (avatar)
    US3  T037 alongside T032-T036 (a query, not a code change)
    US4  T045 (the ledger) alongside T048 (the review) — two documents

**T058 and T059 are `[P]` against each other** and against nothing else in Phase 7 — one
reads test titles and the other greps a diff.

## Implementation strategy

**The smallest useful increment is T010, not US1.** Awaiting each child's exit instead of
sleeping 200 ms closes **10 of the last battery's 11 failures** on its own — one file, two
lines, no production code, no published prose falsified. If a sitting has room for one change,
that is the one. US1 bundles four independent pieces around it: the e2e harness (T007-T011),
the dispatcher lane (T012-T013), the container-free split (T015-T016) and a reset script
(T014). They share a theme, not a dependency, and each ships alone.

**MVP is US1 alone.** It closes two of the review's Medium findings, and it is the only
story whose absence makes the other three unverifiable. A reasonable stopping point after
US1: the lane is trustworthy, the public-boundary defects are documented and unfixed, and
the next sitting starts with an instrument that works.

**Then US2 and US3 in either order.** Both are the review's public-surface group; US2 holds
its two High findings and US3 holds the larger share of the documentation work.

**US4 last, and it is cheap.** Four of its ten tasks are edits to documents nobody's build
depends on, and two of them correct statements that are wrong today.

**Commit each phase.** `git checkout` on a file with uncommitted work has destroyed it twice
in this repository.
