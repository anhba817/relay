# Tasks: chapter 4.11 — the half of the union that was refused

**Input**: `specs/057-chapter-4-11/` — spec, plan, research, data-model, contracts, quickstart
**Prerequisites**: chapter 4.10 shipped and tagged `part4-ch10`

**Tests are requested.** Constitution VI makes FR-MED-06 a `T` clause, and this chapter's central
finding is that one of its two states cannot be tested — which is a claim about tests and has to
be made with them.

## Format: `[ID] [P?] [Story] Description`

- **[P]** — different files, no dependency on an incomplete task
- **[US1] [US2] [US3]** — the user story the task serves; setup, foundational and polish carry none

## Path Conventions

`relay-platform/` is the platform, `relay-tutorial/` the chapter, `docs/` the published documents.
Paths below are relative to the repository that owns them.

---

## Phase 1: Setup — the measurements this chapter is compared against

- [ ] T001 Bring the stack up on its documented ports and record what answers: `RELAY_POSTGRES_PORT=15432 docker compose up -d --wait postgres redis nats clickhouse minio mailpit`. **MinIO is 9100, not 9000** — ClickHouse's native port has held 9000 since chapter 1.2 and the two cannot both bind it (`gaps.md` 056-3).
- [ ] T002 Record the opening `check:fences` figure as an **absolute number**, not a delta. It is 0 today. A delta of zero is what hid a problem for nine chapters.
- [ ] T003 [P] Record the opening dependency count across every `package.json` in `relay-platform` — 29 at `part4-ch10` — so SC-010 is a comparison rather than an assertion.
- [ ] T004 [P] Record the opening state of the three lanes: `pnpm test` (Docker-free since the 056 follow-up), `pnpm test:integration` (12 of 12 tasks), and `pnpm check:errors` (33 codes, 33 sections). **Read each one's counted line, not its exit code** (`gaps.md` 055-4).
- [ ] T005 **Count the fenced files this chapter will touch, against the checker.** The plan lists six as a starting point and says so; 056's table said twelve and the checker said seventeen. `pnpm check:fences --dump` after the first source edit is what answers it.

---

## Phase 2: Foundational — the registry and the arm, which move together

**Blocking.** `check:errors` fails in both directions until the code is gone, its section is gone,
and the new code has one. The arm cannot accept before the predicate exists and the predicate
cannot be tested before the arm accepts.

- [ ] T006 Choose the new code's name and record the argument in one comment. `media_not_attachable` names the operation; the registry's style is that a code says what a client does about it, and all three conditions have the same answer — stop using that id. **Plan open question 2.**
- [ ] T007 Add the new code to `relay-platform/packages/protocol/src/codes.ts` with the comment the registry's style requires, **naming its near-neighbour**: it is not `not_found` (that is a route), not `forbidden` (that is a permission), and not `invalid_request` (the id is well-formed).
- [ ] T008 Delete `media_not_available` from `codes.ts`, on its own entry's instruction — *"§4.14 replaces the arm rather than this code … at which point it is deleted, not repurposed."*
- [ ] T009 Remove the three `media_not_available` assertions from `packages/protocol/src/codes.test.ts:244-246` and write the equivalents for the new code.
- [ ] T010 Remove `media_not_available`'s section from `docs/08-error-reference.md` and write the new code's, with the four things `check-error-codes.mjs` enforces: a level-two heading that is the bare code, `**Retryable:**`, `**What to do:**`, and at least 200 characters after whitespace collapse.
- [ ] T011 **`**Retryable:** no`, and the section must say what to do instead of retrying.** All three conditions are permanent for the id that caused them; the remedy is a different id or an upload of one's own.
- [ ] T012 Make `media_id` a UUID in the arm in `packages/protocol/src/attachments.ts`. **Research R3 measured what the looser shape costs**: `z.string().min(1)` sends `not-a-uuid` to the driver, Postgres answers `invalid input syntax for type uuid`, and the filter turns that into a **500** the caller triggered.
- [ ] T013 Remove the arm's unconditional `.refine(() => false, …)` and its `protocolCode` params, leaving `strictObject` on both arms — an unknown key stays a refusal rather than a silent drop.
- [ ] T014 Update `services/api/src/messages/zod-validation.pipe.ts:13`'s comment, which cites a code that will not exist. **Name what the mechanism is for, not who used it** — `gaps.md` 056-10's convention, and the mechanism now has no user at all (research R5).
- [ ] T015 Keep `protocolCode` in the pipe and say in the comment that nothing uses it. Chapter 4.10's `service_unavailable` precedent: a general extension point with a stated role outlives its last caller. **Rejected alternative recorded rather than implied**: deleting it to save nine lines unteaches a chapter.
- [ ] T016 Extend `packages/protocol/src/attachments.test.ts` for the arm's new shape — a UUID accepted, a non-UUID refused at the schema, the discriminator still selecting the media arm, and `MAX_ATTACHMENTS` still 10 over the union.
- [ ] T017 Build `@relay/protocol` before anything reads `ErrorCode` from it. The api reads the built `dist`, and 056 lost a compile cycle to that.

**Checkpoint**: the arm parses a media attachment and nothing refuses it yet — which is a platform
that accepts any id, and is why phase 3 is one change with phase 2 rather than a shippable state.

---

## Phase 3: A photo sends the moment its upload finishes (US1) 🎯 MVP

**Goal**: FR-MED-06's accept path. **Independently testable**: a slot, an upload, a message, and
the message reads back with its attachment.

- [ ] T018 [US1] Write the predicate in `services/api/src/db/repository.ts`, inside `sendMessage`'s existing transaction. **The query engine lives in the repository because a lint rule says so in constitution I's words** — 4.7 found that wall and 4.10 hit it again.
- [ ] T019 [US1] The predicate is the three clauses `data-model.md` §2 states, in the clause's order: environment, then uploader, then state.
- [ ] T020 [US1] **A NULL `user_id` passes for a user token** (research R1). It means the tenant uploaded it, and chapter 4.10's controller says *"a photo sent by a person and an attachment uploaded by a customer's backend are the same operation."* The specification assumed the opposite; research settled it against the specification.
- [ ] T021 [US1] Decide one query or N, and record the reason. **Plan open question 1**: one `IN` lookup makes "which one failed" a set difference, and the refusal's `field` path needs the attachment's index — so the difference has to preserve position.
- [ ] T022 [US1] Map the repository's refusal to a `protocolError` in `services/api/src/messages/messages.service.ts`, beside the ban and quota mappings that are already there.
- [ ] T023 [US1] Return the attachment array as sent, in order, with no de-duplication. Chapter 3.24's rule, unchanged: the same id twice is two attachments.
- [ ] T024 [US1] Integration test: a slot issued to a user token, an upload to the signed URL, a message attaching the id, and the message read back with the attachment. **The suite must reach a real store** — the media configs are in both vitest configs since 4.10, and a suite that reaches nothing gets `media_storage_unavailable`, which is a correct answer to the wrong question.
- [ ] T025 [US1] Integration test: an API key's slot attached by that API key.
- [ ] T026 [US1] Integration test: **an API-key slot attached by a user token of the same tenant is accepted** — R1's case, and the one the specification would have refused.
- [ ] T027 [US1] Integration test: a message carrying one media attachment and one URL attachment stores both, in order.
- [ ] T028 [US1] Integration test: a message with a media attachment and no text is accepted. Chapter 3.24's rule for the URL arm, asserted here because this chapter is the first thing that could have broken it.
- [ ] T029 [US1] Convert `services/api/src/messages/messages.itest.ts`'s two `media_not_available` tests into what they become. The one that mints a real id and expects 422 is now the accept test; the one that sends `"m_1"` is now a 400 at the schema.
- [ ] T030 [US1] **Check `docs_url` resolves.** `codes.test.ts` owns the URL rule and a route test restating it is how the two drift — but the removed code's link must stop being generated and the new one's must start.
- [ ] T031 [US1] Re-measure and record: the send's latency with and without a media attachment, sampled rather than asserted. **State what it is a measurement of** — one read on a lane whose largest table is small, which is not a claim about production.
- [ ] T032 [US1] Commit phase 3.

**Checkpoint**: a client can send a message carrying a `media_id` it uploaded.

---

## Phase 4: Somebody else's media cannot be attached (US2)

**Goal**: FR-MED-06's second sentence, with one answer for three conditions.
**Independently testable**: four sends, one accepted and three refused identically.

- [ ] T033 [US2] Refuse a `media_id` in another environment (FR-002).
- [ ] T034 [US2] Refuse a `media_id` belonging to another user of the same environment, for a user token (FR-003).
- [ ] T035 [US2] Refuse a `media_id` no media object has (FR-004).
- [ ] T036 [US2] **One code and one message for all three** (FR-005). The send path already argues it: `messages.service.ts` records that the ban refusal *"is the same for a channel that exists, one that belongs to another tenant, and one that was invented."*
- [ ] T037 [US2] Integration test: the three refusals return **byte-identical bodies apart from `request_id`** (SC-002). Not three 422s — three identical bodies, compared as bodies.
  **THIS IS THE ASSERTION A LATER EDIT WEAKENS.** "All three return 422" satisfies the letter and loses the property, and the property is that a caller cannot use the refusal as an existence oracle for a guessable UUID.
- [ ] T038 [US2] Integration test: a refused send writes **no message row and no outbox row** and does not advance the channel's sequence (FR-006). Scoped to the test's own channel — a whole-table count is a neighbour's problem in a lane that runs two files at a time (045-74).
- [ ] T039 [US2] Integration test: a message whose tenth attachment is foreign refuses the whole message and stores none of the other nine (FR-007).
- [ ] T040 [US2] Integration test: the refusal's `field` names the attachment's index, so a caller with ten attachments is told which one.
- [ ] T041 [US2] **Run the refusal red by deleting the environment predicate**, and confirm the cross-tenant test fails rather than the shape test. A refusal that can only fail for somebody else's reason is 043's recorded class.
- [ ] T042 [US2] Integration test: a non-UUID `media_id` is a **400 `invalid_request`** naming `attachments.<n>.media_id`, and not a 500. R3's measurement is the reason this test exists; without T012 it is the driver's error wearing `internal_error`.
- [ ] T043 [US2] Commit phase 4.

**Checkpoint**: a refused client learns that the id is not theirs to use, and nothing else.

---

## Phase 5: The clause's unreachable half, recorded rather than faked (US3)

**Goal**: build the state predicate as FR-MED-06 reads and publish which arm no fixture can reach.

- [ ] T044 [US3] The state predicate admits `pending` and `ready` and refuses anything else (FR-010).
- [ ] T045 [US3] **Name the unreachable arms in the code.** `ready` cannot occur and `rejected` cannot occur, because `CHECK (state = 'pending')`. Chapter 4.10's precedent is `RESUMES`' fourth entry, which no caller reaches and whose comment says so.
- [ ] T046 [US3] Integration test: an attempt to store a media object in state `ready` is refused by the database, **and the refusal's text is the assertion** — `violates check constraint "media_objects_state_check"`. That test is the chapter's evidence, and it passes for the reason the chapter is about.
- [ ] T047 [US3] Do **not** widen the CHECK so a fixture can plant `ready`. It would be a schema claiming a state nothing produces, which is what 4.10 refused, and it would buy a green assertion about a transition no code performs.
- [ ] T048 [US3] Pin the new files and the changed ones in `vitest.coverage.config.mts`, and **probe both halves**: demand an impossible figure of each new key and confirm it fires, then confirm the measured pins pass. A pin whose key matches no file is silent.
- [ ] T049 [US3] **Read `coverage-summary.json`, not the text table**, to find which files were measured. v8's text reporter omits a file at 100/100/100/100 — 056 lost three of five new files to that.
- [ ] T050 [US3] Commit phase 5.

**Checkpoint**: the clause's testable half is tested and its untestable half is named.

---

## Phase 6: The gauntlet, and what this chapter cannot fix

- [ ] T051 **Run the derivation first and record that it finds nothing.** This chapter adds no route, so `targets.itest.ts` will be green — which breaks a streak of eight chapters where it found the new route before the classification did. Say so rather than letting a green check read as coverage.
- [ ] T052 Extend the existing `POST /v1/channels/:channelId/messages` attack in `services/api/src/isolation/gauntlet.itest.ts` with a forged **`media_id`**. The existing attack forges a channel id; this is a second identifier on the same route, and `attacked.add` already covers the route name.
- [ ] T053 **The attack plants a media object for each tenant.** Both tenants' tables are otherwise empty, and *"an empty log passes a leak check for the same reason an empty page does"* (chapter 4.8).
- [ ] T054 Run the attack red by removing the environment predicate, and confirm it fails for the tenancy reason rather than a shared refusal — the trap the existing attack's own comment records.
- [ ] T055 [P] Record in `gaps.md`: **nothing counts references to a media object.** This chapter creates the first ones; FR-MED-10's sweep deletes *unreferenced* objects and the only way to answer "unreferenced" against this shape is a scan of `messages.attachments`.
- [ ] T056 [P] Record in `gaps.md`: **a message can attach an object nobody uploaded to.** `state` is `pending` whether the client uploaded or not (`gaps.md` 056-1), so a message may name a slot that holds no bytes, and no client can tell.
- [ ] T057 Run `check-lane-scope.py` and record the file count. It read 59 files at 056's close; this chapter adds integration tests and the number must rise. A run that reads nothing exits 2.

---

## Phase 7: The chapter

- [ ] T058 Write `relay-tutorial/app/(en)/part-4/chapter-11/…/page.mdx`, **2,000–4,000 words outside code fences**, measured with `node relay-tutorial/scripts/prose-words.mjs <page>`. 4.10 came in at 3,998 after four rounds of trimming; leave margin.
- [ ] T059 **At least one `TRAP` box.** The candidates are measured rather than invented: the 500 a looser schema ships (R3), the specification's own assumption settled against it (R1), and the three-refusals-one-answer argument, which reads like over-caution until the existence oracle is spelled out.
- [ ] T060 Register the chapter in `relay-tutorial/lib/tutorial.ts`. `<ChapterHeader id="4.11" />` throws on an unregistered id, so `pnpm build` exits 1 from the moment the page exists — a cost two chapters have already paid.
- [ ] T061 [P] Figures in `figures.ts`, each named by a `<Figure>`. `check:figures` reports an unused export as a note rather than a failure, so the note is the check.
- [ ] T062 A hunk per fenced file this chapter edits, **counted at T005 rather than remembered**. Generate each with `pnpm check:fences --dump <dir>`, never with `git diff` against the working tree.
- [ ] T063 **Test each hunk's anchoring with an exact-match count, not `patch --dry-run`** (`gaps.md` 056-7). `patch` applies with fuzz and offset and said yes to seven hunks the checker refused.
- [ ] T064 For each file, use the widest context that anchors — and where `-U6` reaches an appendix-added line, trim rather than widen. Keep the chapter's change and trim the context the chain does not carry.
- [ ] T065 A hunk that cannot anchor at any width goes in `fences/post-series.md`, and one that anchors **and unanchors an existing appendix hunk** goes there too, placed after the hunks it would otherwise have invalidated.
- [ ] T066 **There is no Vietnamese twin to write.** `app/(vi)/vi/part-4/` holds chapters 1-3; the translation lags by eight. Check it rather than assume it — 050 and 056 both recorded a task that described a corpus instead of checking one.
- [ ] T067 Run `pnpm check:fences` and report the **absolute number**.

---

## Phase 8: The record

- [ ] T068 Write `baseline.txt` carrying every phase's measurements in the order they were taken, and the pinned lane environment.
- [ ] T069 Write `gaps.md`. **Re-measure every carried item rather than copying it**: 056-1 and 056-2 (this chapter inherits both), 056-9 and 056-10 (closed in the 056 follow-up — confirm they stayed closed), and 055-3 (`check:errors` still has no CI job, and this chapter both removes a code and adds one).
- [ ] T070 Decide whether the SRS needs a revision, and record the decision either way. **Plan open question 3**: R1 and R2 are readings rather than contradictions, so the default is no revision — but check that against FR-MED-06's exact words before defaulting.
- [ ] T071 Write `traceability.md`, and **name anything discharged in a weaker form than its words suggest.** FR-010 is the first candidate: the predicate is built and half of it cannot run.
- [ ] T072 Update `CLAUDE.md`'s `<!-- SPECKIT -->` block for the close, including every task premise this chapter falsified by running it.
- [ ] T073 Run the tutorial job's six gates, named from `ci.yml` rather than memory, and **read each one's counted success line**. `lint` is the one with no counted line at all — eslint prints nothing on success.
- [ ] T074 Run `pnpm check:errors` by hand, in **both directions**. It is a script no CI job runs (055-3), and this chapter is the first to both delete a code and add one.
- [ ] T075 Tag `part4-ch11` on `relay-platform`, commit, and push all three repositories.
- [ ] T076 After the push, confirm CI. **Compare per error, not per colour** — the `lanes` job's error set is the baseline, and 056 pushed two failures into a red job that its colour could not report.

**Checkpoint**: the published union has both arms, and what the chapter could not verify is written
down.

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 (setup) ─────────────► everything
Phase 2 (registry + arm) ────► US1, US2, US3   — the arm cannot accept before the code exists
Phase 3 (US1) ───────────────► US2             — there is no accept path to refuse against
Phase 5 (US3) ───────────────► independent of US2
T012 ────► T042                                 the 500 test needs the tightened schema
T007 + T008 + T010 ────► T074                   check:errors fails until all three land
T060 ────► T067                                 an unregistered chapter fails the build first
T005 ────► T062                                 a hunk list counted, not remembered
T075 ────► T076                                 CI is only observable after a push
```

### User Story Dependencies

**US1 is the MVP and it is not independently shippable**, which is unusual for this project and
worth stating. An accept path with no predicate accepts any id, including another tenant's — so
phases 2, 3 and 4 are one shippable increment. US3 is independent of both and could ship alone,
because it is a test and a comment about a state nothing reaches.

### Parallel Opportunities

- **Phase 1**: T003 and T004 read different things.
- **Phase 2**: T009, T010 and T016 are three files; T010 is documentation beside two code changes.
- **Phase 4**: T033, T034 and T035 are one predicate with three fixtures, so the tests parallelise and the implementation does not.
- **Phase 6**: T055 and T056 are two records in one file.
- **Phase 7**: T061's figures are independent of the fence work.

## Implementation Strategy

**Phases 2, 3 and 4 are the increment.** The arm cannot accept before the code exists, the
predicate cannot be tested before the arm accepts, and an accept path without the predicate is a
cross-tenant hole. Committing between them is fine; shipping between them is not.

**The riskiest task is T037**, and not because it is hard. Byte-identical refusals are easy to
write and easy to lose: the next person to add a helpful detail to one of the three messages
removes the property without failing a test that only checks the status. The assertion has to
compare bodies.

**The task most likely to be skipped is T051.** Eight chapters running have been told something by
the derivation, and this one will not be. A green check that was never going to be red is worth a
sentence, because the alternative is reading it as coverage.
