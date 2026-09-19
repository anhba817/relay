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
- [ ] T010 Remove `media_not_available`'s section from `docs/08-error-reference.md` and write a section for **each** code this chapter adds — the media refusal and T011a's 422 rung (FR-009b). Four things `check-error-codes.mjs` enforces per section: a level-two heading that is the bare code, `**Retryable:**`, `**What to do:**`, and at least 200 characters after whitespace collapse.
  **TWO SECTIONS, NOT ONE, AND ANALYSIS PASS 1 GOT THIS WRONG.** It added the rung and wrote "the new code's" singular; the checker fails in both directions, so T074 would have gone red on a code the previous pass introduced. **The fix is where the next defect is.**
- [ ] T011 **`**Retryable:** no`, and the section must say what to do instead of retrying.** All three conditions are permanent for the id that caused them; the remedy is a different id or an upload of one's own.
- [ ] T011a0 **Name the 422 rung's code and say what a client does about it** (FR-009b), beside T006. It is a fallback with no thrower — the shape `service_unavailable` took at 4.10 — so its sentence has to carry the only two facts the status supports: the request was understood, and what it asked for cannot be done. A code nobody throws still needs a reference section a reader can act on.
- [ ] T011a **Add a 422 rung to `services/api/src/protocol-error.filter.ts`, using T011a0's code** (FR-009a). Analysis pass 1 measured the ladder: 400, 401, 402, 403, 404, 413, 415, 503 — **422 is not there**, so an unnamed one answers `internal_error`, which is the filter's own *"lie the client cannot act on"*. Chapter 4.10 closed four statuses and left this one.
  **NOTHING THROWS AN UNNAMED 422 TODAY**, and that is the argument for the rung rather than against it: `channel_member_limit_exceeded` names itself twice and `media_not_available` named itself until this chapter. The rung is for the next thrower that forgets, which is what `service_unavailable` was added for at 4.10 with nothing throwing it either.
  **Rejected: map 422 to this chapter's own code.** A channel-member-limit refusal that forgot its code would then tell a caller their media is not attachable.
- [ ] T011b Extend `services/api/src/protocol-error.filter.test.ts`'s rung table with 422, asserted **twice** the way the other eight are: the code it gives, and separately that it is not `internal_error`. Run it red by deleting the rung.
- [ ] T012a **Record why the tightening is safe, because it is safe by ordering rather than by design** (research R10). No durable row carries a media attachment — the arm has refused since 3.24 — and the read paths cast rather than parse. *"A reader of anything durable cannot require a field its writer did not have"* is the rule that would otherwise apply, and it is the one `outboxEventSchema` broke. The next tightening will not have the first reason.
- [ ] T012 Make `media_id` a UUID in the arm in `packages/protocol/src/attachments.ts`. **Research R3 measured what the looser shape costs**: `z.string().min(1)` sends `not-a-uuid` to the driver, Postgres answers `invalid input syntax for type uuid`, and the filter turns that into a **500** the caller triggered.
- [ ] T013 Remove the arm's unconditional `.refine(() => false, …)` and its `protocolCode` params, leaving `strictObject` on both arms — an unknown key stays a refusal rather than a silent drop.
- [ ] T014 Update `services/api/src/messages/zod-validation.pipe.ts:13`'s comment, which cites a code that will not exist. **Name what the mechanism is for, not who used it** — `gaps.md` 056-10's convention, and the mechanism now has no user at all (research R5).
- [ ] T015 Keep `protocolCode` in the pipe and say in the comment that nothing uses it. Chapter 4.10's `service_unavailable` precedent: a general extension point with a stated role outlives its last caller. **Rejected alternative recorded rather than implied**: deleting it to save nine lines unteaches a chapter.
- [ ] T016 **Replace** `packages/protocol/src/attachments.test.ts`'s `describe("the media arm refuses and SAYS SO (FR-003, FR-003a)")` block — it is a rewrite, not an extension, and a rewrite budgeted as an extension is how a task gets half done. What replaces it: a UUID accepted, a non-UUID refused at the schema, the discriminator still selecting the media arm, and `MAX_ATTACHMENTS` still 10 over the union.
- [ ] T017 Build `@relay/protocol` before anything reads `ErrorCode` from it. The api reads the built `dist`, and 056 lost a compile cycle to that.

- [ ] T017a **Make the outbox envelope's attachment elements permissive** (FR-018), in `services/api/src/outbox/event.ts` at both arms — `:373` and `:412`. The envelope stays `strictObject` about its OWN fields, because that is the contract between two versions of one service and a new key should be loud. The attachment ELEMENTS are payload the consumer forwards, not data it interprets.
  **THIS IS A CONSTITUTION II DEFECT AND IT WAS IN THE PLAN, NOT THE CODE.** `consumer/runtime.ts:163` parses with `safeParse` and `:204` answers a failure with `message.term()`, which stops redelivery for good. A message a new instance commits and an old one reads during a rolling deploy is destroyed **after the send was acknowledged**.
  **AND THE CONSUMER NEVER READS THE FIELD** — `grep -c attachments services/api/src/consumer/` is 0, and nothing downstream of the parse reads them either. The validation that destroys the message is validation of a field the validator ignores.
  **Rejected: rely on deploy order.** Reader-first would work and nothing enforces it; an invariant that depends on the order two processes restart in is not an invariant.
- [ ] T017b **Test it against the arm as it stands today** (FR-018a, SC-002b), in `services/api/src/consumer/consumer.itest.ts`: an envelope carrying `{ "type": "media", "media_id": "<uuid>" }` parses and is acked rather than terminated. **Run it red against the current `attachmentSchema`** — a durable-reader test that cannot go red is the class this chapter is trying not to join.
  **THE LANE CANNOT FIND THIS ON ITS OWN.** `RELAY_EVENT_CONSUMER=off`, for chapter 3.5's reason, and `outbox/event.ts`'s own header records what that cost last time: *"the api suite stayed green through 505 tests with the defect in place."*
- [ ] T017c **Budget `outbox/event.ts` (11 titled fences) and `consumer.itest.ts` (9) in the fence work.** Neither appears in any artifact before analysis pass 3, because none mentioned the consumer.

**Checkpoint**: the arm parses a media attachment and nothing refuses it yet — which is a platform
that accepts any id, and is why phase 3 is one change with phase 2 rather than a shippable state.

---

## Phase 3: A photo sends the moment its upload finishes (US1) 🎯 MVP

**Goal**: FR-MED-06's accept path. **Independently testable**: a slot, an upload, a message, and
the message reads back with its attachment.

- [ ] T018 [US1] Write the predicate in `services/api/src/db/repository.ts`, inside `sendMessage`'s existing transaction. **The query engine lives in the repository because a lint rule says so in constitution I's words** — 4.7 found that wall and 4.10 hit it again.
- [ ] T019 [US1] The predicate is the three clauses `data-model.md` §2 states, in the clause's order: environment, then uploader, then state.
- [ ] T020 [US1] **A NULL `user_id` passes for a user token** (research R1). It means the tenant uploaded it, and chapter 4.10's controller says *"a photo sent by a person and an attachment uploaded by a customer's backend are the same operation."* The specification assumed the opposite; research settled it against the specification.
- [ ] T020a [US1] **Decide in writing how the repository learns which credential class is asking**, and record the alternative. `sendMessage` already takes `senderMustBeBot`, set by the controller when the caller is an application credential — reusing it means a flag named for the SENDER answering a question about the CALLER, and adding a second parameter means two booleans that are always equal. Neither the plan nor the tasks said which until analysis pass 1 asked.
- [ ] T021 [US1] Decide one query or N, and record the reason. **Plan open question 1**: one `IN` lookup makes "which one failed" a set difference, and the refusal's `field` path needs the attachment's index — so the difference has to preserve position.
- [ ] T022 [US1] Map the repository's refusal to a `protocolError` in `services/api/src/messages/messages.service.ts`, beside the ban and quota mappings that are already there.
- [ ] T023 [US1] Return the attachment array as sent, in order, with no de-duplication. Chapter 3.24's rule, unchanged: the same id twice is two attachments.
- [ ] T024 [US1] Integration test: a slot issued to a user token, an upload to the signed URL, a message attaching the id, and the message read back with the attachment. **The suite must reach a real store** — the media configs are in both vitest configs since 4.10, and a suite that reaches nothing gets `media_storage_unavailable`, which is a correct answer to the wrong question.
- [ ] T025 [US1] Integration test: an API key's slot attached by that API key.
- [ ] T026 [US1] Integration test: **an API-key slot attached by a user token of the same tenant is accepted** — R1's case, and the one the specification would have refused.
- [ ] T027 [US1] Integration test: a message carrying one media attachment and one URL attachment stores both, in order.
- [ ] T027a [US1] Integration test: **eleven attachments are refused whichever arms they are** (FR-012). The cap is `z.array(attachmentSchema).max(10)` over the union, so it counts both by construction — and "by construction" is what T016's unit test asserts. This one asserts it on the route, because the route is where a caller meets it.
- [ ] T028 [US1] Integration test: a message with a media attachment and no text is accepted. Chapter 3.24's rule for the URL arm, asserted here because this chapter is the first thing that could have broken it.
- [ ] T028a [US1] Integration test: **a message read back carries the attachment array exactly as sent — no state, no filename, nothing resolved** (FR-013). **Three doors, not one**: history, the live socket frame, and the backfill a resuming client reads — `backfill.controller.ts:123` passes `row.attachments` straight through, which is why a replay is not a lesser message and why it is also a place this chapter could have leaked state.
  **"WE DID NOT ADD IT" IS NOT A PROPERTY ANYTHING CHECKS.** Chapter 4.10 gave FR-016 a test for the same reason and that test is what caught the arm still refusing a real id. FR-MED-07 is movement VI; the guard is that this chapter does not ship its surface early.
- [ ] T029 [US1] Convert `services/api/src/messages/messages.itest.ts`'s two `media_not_available` tests into what they become. The one that mints a real id and expects 422 is now the accept test; the one that sends `"m_1"` is now a 400 at the schema.
- [ ] T030 [US1] Assert the refusal's envelope names **this** code, and let `codes.test.ts` keep owning the URL's shape. A route test restating that shape is how the two drift; what this one is about is that a 422 whose `docs_url` points at `invalid_request` is the failure. **The both-directions check that the removed code's link stops resolving and the new one's starts is T074's**, which is the gate that compares the registry against the reference.
- [ ] T031 [US1] Re-measure and record: the send's latency with and without a media attachment, sampled rather than asserted. **State what it is a measurement of** — one read on a lane whose largest table is small, which is not a claim about production.
- [ ] T032a [US1] **Convert `services/gateway/src/session.itest.ts:415`** — *"refuses a media_id and SAYS hosted media is unavailable"* — rather than deleting it (FR-001b). It goes red on the first phase that lands, and its comment says what it is for: *"the only thing that can tell the two-arm schema from a one-arm one on this door."* The two-arm schema still needs telling apart, now by the arm accepting.
- [ ] T032b [US1] Integration test on the socket: a `message.send` frame carrying the sender's own `media_id` **commits** (FR-001a, SC-002a). The union is one definition and three doors — `messageSendSchema` embeds it and `packages/protocol/src/internal.ts` imports it — so the REST route passing says nothing about this one.
- [ ] T032c [US1] Integration test on the socket: a frame carrying a **foreign** `media_id` receives the api's own code, not `invalid_frame`. The gateway's send catch forwards any 4xx whose `code` passes `isErrorCode`, so this works by inheritance — and `sendError` fixes the code for the gateway's OWN refusals, which is why a malformed id still answers `invalid_frame` and why that distinction has to be asserted rather than assumed.
- [ ] T032d [US1] **Budget `session.itest.ts` in the fence work.** It carries **9 titled whole-body fences and 8 excerpts** across the two locales and appears in no artifact before analysis pass 2, because no artifact mentioned the socket.
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
  **TWO OF THE THREE CONDITIONS, AND THE HELPER DECIDES WHICH.** `writeAttack(baseUrl, credential, foreignReq, absentReq, readVictimState)` compares exactly two requests and asserts their answers are identical — so the victim's id against a random UUID is the pair it is built for, and `differences` being empty **is** SC-002 for those two. The third condition, another user of the same tenant, is not a cross-tenant case at all and belongs in the media suite (T034).
- [ ] T053 **The attack plants a media object for each tenant.** Both tenants' tables are otherwise empty, and *"an empty log passes a leak check for the same reason an empty page does"* (chapter 4.8).
- [ ] T054 Run the attack red by removing the environment predicate, and confirm it fails for the tenancy reason rather than a shared refusal — the trap the existing attack's own comment records.
- [ ] T055 [P] Record in `gaps.md`: **nothing counts references to a media object.** This chapter creates the first ones; FR-MED-10's sweep deletes *unreferenced* objects and the only way to answer "unreferenced" against this shape is a scan of `messages.attachments`.
- [ ] T055a [P] Record in `gaps.md` and in the chapter: **`attachment_count` changes meaning** (FR-019). `load-analytics.mjs:178,187,200` compute `JSONLength(m.attachments)`, which has counted external URLs for every row ever written and starts counting hosted media alongside them with nothing able to tell them apart. **Recorded, not split** — a second column is FR-MED-12's chapter, and adding a narrower count here would be that chapter's surface without its clause.
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
- [ ] T068a **Re-measure the dependency count and compare it to T003's opening figure** (SC-010). T003 records 29 at `part4-ch10`; a criterion measured once is asserted rather than compared, which is the thing T003's own wording says it exists to prevent.
- [ ] T069 Write `gaps.md`. **Re-measure every carried item rather than copying it**: 056-1 and 056-2 (this chapter inherits both), 056-9 and 056-10 (closed in the 056 follow-up — confirm they stayed closed), and 055-3 (`check:errors` still has no CI job, and this chapter both removes a code and adds one).
- [ ] T070 Decide whether the SRS needs a revision, and record the decision either way. **Plan open question 3**: R1 and R2 are readings rather than contradictions, so the default is no revision — but check that against FR-MED-06's exact words before defaulting.
- [ ] T070a **Amend `docs/12` row 12 with what the line did not say** (FR-017). The row reads *"this chapter fills it"*, which is true and silent about all three findings: the clause names a state the schema cannot reach, the arm ships a caller-triggered 500 the moment it accepts, and a tenant-uploaded object is attachable by a user of that tenant — the opposite of what the specification assumed, and what 4.10 made the column nullable for.
  **CHAPTERS 4.7, 4.8, 4.9 AND 4.10 EACH AMENDED THEIR OWN ROW** and this task existed in none of the three artifacts until analysis pass 1. 056 caught the same omission at pass 3, having cited `docs/12` three times without opening it.
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
T011a0 ────► T011a ────► T011b                   name it, add the rung, then probe it
T010 ────► T074                                 TWO sections now, and the gate reads both
T007 + T008 + T010 ────► T074                   check:errors fails until all three land
T017a ────► T017b                               the permissive reader before the test that proves it
T017a ────► T018                                DO NOT SHIP A PRODUCER AHEAD OF ITS DURABLE READER
T020a ────► T018                                the predicate needs to know which credential asked
T003 ────► T068a                                SC-010 is a comparison, not an assertion
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
- **Phase 2**: T009, T010 and T016 are three files; T010 is documentation beside two code changes. T011a and T011b are the filter and its test, and the test comes second.
- **Phase 4**: T033, T034 and T035 are one predicate with three fixtures, so the tests parallelise and the implementation does not.
- **Phase 6**: T055 and T056 are two records in one file.
- **Phase 3**: T032b and T032c are two socket tests against one fixture and can be written together; T032a is a conversion of an existing test and comes first.
- **Phase 7**: T061's figures are independent of the fence work.

## Implementation Strategy

**Phases 2, 3 and 4 are the increment.** The arm cannot accept before the code exists, the
predicate cannot be tested before the arm accepts, and an accept path without the predicate is a
cross-tenant hole. Committing between them is fine; shipping between them is not.

**AND T017a IS THE ONE ORDERING THAT IS NOT NEGOTIABLE.** The durable reader has to accept a media
attachment before anything can write one. Ship the producer first and a rolling deploy destroys
acknowledged messages — constitution II, permanently, silently, and on exactly the messages this
chapter exists to make possible.

**The riskiest task is T037**, and not because it is hard. Byte-identical refusals are easy to
write and easy to lose: the next person to add a helpful detail to one of the three messages
removes the property without failing a test that only checks the status. The assertion has to
compare bodies.

**The task most likely to be skipped is T051.** Eight chapters running have been told something by
the derivation, and this one will not be. A green check that was never going to be red is worth a
sentence, because the alternative is reading it as coverage.

**And seven of these tasks exist because analysis pass 1 ran something rather than read it.**
T011a and T011b come from measuring the error filter's ladder and finding 422 absent, which made
FR-009 unsatisfiable as written. T020a comes from asking how the repository would learn the
credential class and finding that nothing had said. T028a and T027a close requirements that had no
task at all. T070a is the `docs/12` amendment four consecutive chapters wrote and this one had
forgotten. **Nine of the pass's twelve findings came from reading the artifacts against each
other; three came from running them, and those three are the ones that changed the design.**

**PASS 3 FOUND THREE AND ONE WAS A CONSTITUTION VIOLATION.** The outbox envelope reads
`attachments` with the same union and the consumer terminates a failed parse. `consumer` appeared
zero times in all six artifacts and `outbox` five times, every one meaning *"a refusal writes no
outbox row"* — the sense that was already safe. **12 findings, then 7, then 3, and the severity
went the other way**: each pass asked a new question of the tree rather than re-reading, and the
count was the misleading number every time.

**PASS 2 FOUND SEVEN, ALL BY RUNNING, AND THE FIRST IS BIGGER THAN ANYTHING PASS 1 FOUND.** Zero
mentions of `gateway`, `socket` or `frame` across all six artifacts — and the union has three
doors, with a live gateway test asserting the refusal this chapter removes. T032a-T032d are that.
Pass 2 also found that **pass 1's own remediation left a gate red**: T011a added a code and T010
wrote one section. The yield fell from twelve to seven and the second pass found the larger thing,
which is why falling yield is not a reason to stop.
