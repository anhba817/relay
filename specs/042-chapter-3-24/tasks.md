# Tasks — chapter 3.24, the message that is not only text

**Feature**: `specs/042-chapter-3-24/` · **Plan**: [plan.md](./plan.md) · **Spec**: [spec.md](./spec.md)

**One field follows `text` through every door a message has.** The doors were counted, not
guessed — research R3 and R4: four writers, six read shapes, three event types, 70 occurrences
of `text` on non-comment lines across the ten files that carry a message payload.

**Tests are requested.** This project's constitution requires every behaviour to trace to a
requirement with a stated verification method (VI), and every phase below carries the tests
that verify what it builds.

---

## Phase 1: Premises, instruments, and the reader test

**Everything blocks on this.** Chapter 3.23 recorded that a premise inherited from a
predecessor's record and never re-run was its single most common defect — three times, each
settled by one `grep`.

- [X] T001 **DONE DURING PLANNING**, because the instruments are what the rest of the phase is checked by. `specs/042-chapter-3-24/check-prose.py` is written with its claim list emptied and this chapter's one entry added; `check-refs.py` and `sweep.py` are copied with `FOREIGN` cleared. **The copy carried a third stale field nobody had found before**: `\(3\.23\)` hard-coded in the citation rule, which reported all twenty-four requirements as untraced on its first run. It is now derived from the directory name, so the next copy cannot inherit it. The copies of `check-refs.py` and `sweep.py` are already in place with `FOREIGN` cleared; that clearing is a step, not an oversight, and chapter 3.23's copy arrived carrying thirty-one stale pairs and a docstring naming the wrong chapter.
- [X] T002 [P] **DONE DURING PLANNING.** `specs/042-chapter-3-24/check-prose.py` holds one entry and is **RED**: `packages/protocol/src/frames.ts`'s *"metadata/attachments/edit/tombstone fields arrive with Part 2/4"* (FR-018 (3.24)), and `services/api/src/db/schema.ts`'s comment listing what is deliberately absent if it names attachments — **read before adding**, because chapter 3.23 added an entry for a sentence that was true and had to delete the gate rather than satisfy it. `schema.ts`'s absence comment was read and names no attachments, so it gets no entry.
- [X] T003 [P] **DONE DURING PLANNING**, with the instruments. `specs/042-chapter-3-24/baseline.txt` holds the nine variables, the compose line, the counts named in T005 and T006, and what the instruments found before any code was written.
- [ ] T004 **Write the reader test and run it against unchanged code** in `relay-platform/services/api/src/db/repository.itest.ts`: plant a row with `text = ''` using raw SQL and assert every read path returns it as a **live message** — history in both directions, the channel listing's preview, and the tombstone predicate not firing. **This must pass today.** If it fails, FR-019 (3.24)'s empty-string decision is wrong and the plan changes before a line of production code is written. Chapter 3.23's equivalent proved its read path was already correct and stopped a later phase "fixing" what worked.
- [X] T005 **DONE DURING PLANNING.** The counts are in `specs/042-chapter-3-24/baseline.txt` with their definition stated: occurrences of `text` on non-comment lines in the ten files research R3 names, totalling 70, plus the six read shapes R4 names. **State the counting definition** — chapter 3.23 lost a re-count to a number whose definition was never written down, and its own research note claimed the count was "unchanged" when it could not have been checked.
- [X] T006 **DONE DURING PLANNING**: 45 declared paths, recorded in `specs/042-chapter-3-24/baseline.txt`. Verify against the tree that this chapter adds **no route**, so `relay-platform/services/api/src/isolation/targets.ts` and its derived-count test do not move. Record the current count (45 paths) in `specs/042-chapter-3-24/baseline.txt` so a phase that accidentally adds a route is caught by the number rather than by a reading.
- [X] T007 [P] **DONE DURING PLANNING**: the prediction is **four**, in `specs/042-chapter-3-24/baseline.txt`. Count the pinned places a new error code moves, in `relay-platform/packages/protocol/src/codes.test.ts` and wherever else the total is named, and predict the number in `specs/042-chapter-3-24/baseline.txt`. Chapter 3.22 predicted two and found four; 3.23 predicted four for the outbox types and found five and a half. **The prediction is the point, not the number.**
- [ ] T008 Commit phase 1 in `relay` — `specs/042-chapter-3-24/baseline.txt`, the four instruments, and the reader test. Gates first.

---

## Phase 2: The shape

**Its own module, and the tree's practice is why.** `presence.ts`, `typing.ts`,
`membership.ts` and `revision.ts` each own their shape and their test; `fanout.ts` holds a
subject function and nothing else. Chapter 3.23's task list named `fanout.ts` for its new
grammar and was wrong for exactly this reason.

- [ ] T009 Create `relay-platform/packages/protocol/src/attachments.ts` with the shape `contracts/attachments.md` names (FR-002 (3.24), FR-003 (3.24), FR-003b (3.24), FR-020 (3.24)): a `discriminatedUnion` on `type` with one arm — `{ type: "url", kind: "image"|"audio"|"video", url }` — each arm a `strictObject`. **Export the bound and the allowed schemes as named constants**, because both doors import them and two schemas that happen to agree are the defect this chapter is trying not to repeat.
- [ ] T010 [P] Write `relay-platform/packages/protocol/src/attachments.test.ts` asserting the exact key set of the arm, the three kinds and **refusal of a fourth**, the 10-item bound, the 2048-character URL bound, and the scheme rule. **Assert `javascript:`, `data:`, `file:` and `vbscript:` are all refused** — research R7 measured that `z.url()` accepts every one of them, so a test that only tries `https:` proves nothing.
- [ ] T011 Add the falsification to `relay-platform/packages/protocol/src/attachments.test.ts`: replace the scheme rule with a bare `z.url()` and watch the four refusals go red. **A validator nobody has seen refuse is a validator nobody has checked**, and this one is the whole of FR-004 (3.24)'s protection.
- [ ] T012 Export the module from `relay-platform/packages/protocol/src/index.ts`.
- [ ] T013 Commit phase 2 in `relay-platform`, naming FR-002 (3.24), FR-003 (3.24), FR-003b (3.24), FR-004 (3.24). Gates first.

---

## Phase 3: The wire

**This blocks every route below it.** No read path can return an attachment the frame cannot
express, and `messageSchema` is a `strictObject`.

- [ ] T014 Add `attachments` to `messageSchema` in `relay-platform/packages/protocol/src/frames.ts` (FR-008 (3.24), FR-015 (3.24)). **Decide and record whether this needs an ADR against chapter 3.23's ADR-24**, which refused to widen the same object's `text`. The plan predicts one; the argument to make or refuse is that adding an optional field and loosening a required one's type are different acts. **A prediction that turns out wrong is worth recording either way.**
- [ ] T015 [P] Add `attachments` to `messageSendSchema`'s payload in `relay-platform/packages/protocol/src/frames.ts` (the socket's door) and to `internalSendRequestSchema` in `relay-platform/packages/protocol/src/internal.ts` (the internal hop), both importing the bound from `attachments.ts`. **The two doors disagree about the idempotency key already** — `idem_key: z.string().min(1).max(255)` against `idempotency_key: z.string().uuid()` — and `packages/outsider/src/integrate.itest.ts` records the cost of that in its own comment.
- [ ] T016 [P] Update the frame tests in `relay-platform/packages/protocol/src/frames.test.ts`: the exact key set of `messageSchema` moves from six keys to seven, and `message.deleted`'s payload must still refuse an attachments field (FR-013 (3.24)). **Chapter 3.23 changed that payload and turned two direction tests red in two files** — `session.itest.ts` and `isolation.itest.ts` both build a forged frame from the same object; grep for `case "message.deleted":` before assuming one.
- [ ] T017 Confirm by reading `relay-platform/services/gateway/src/session.ts` that the gateway forwards the widened payload without a line changing, and **record the answer either way** in `specs/042-chapter-3-24/baseline.txt`. The plan predicts no change; chapter 3.23 predicted the same about a different file and was wrong.
- [ ] T018 Commit phase 3 in `relay-platform`, naming FR-008 (3.24), FR-015 (3.24). Gates first.

---

## Phase 4: The writer

- [ ] T019 Add `attachments` to the send body in `relay-platform/services/api/src/messages/messages.schema.ts` (FR-001 (3.24), FR-005 (3.24)), optional, bounded by the constant `attachments.ts` exports.
- [ ] T020 Relax the text bound in `relay-platform/services/api/src/messages/messages.schema.ts` (FR-019 (3.24), FR-019b (3.24)): text may be empty **when at least one attachment is present**, and a body with neither is still refused. **A `superRefine` or equivalent, not two schemas** — the rule is about the pair, and expressing it as two schemas puts the decision in whichever one the caller happened to hit.
- [ ] T021 Thread attachments through `relay-platform/services/api/src/messages/messages.service.ts` to the repository (FR-001 (3.24)).
- [ ] T022 Write attachments in `sendMessage`'s INSERT in `relay-platform/services/api/src/db/repository.ts` (FR-001 (3.24), FR-006 (3.24)): the array as sent, in order, or `NULL` when there are none. **`NULL` and `[]` are different values** and `data-model.md` says which the column stores — every row written before this chapter is `NULL` and stays valid without a backfill.
- [ ] T023 [P] Write the writer test in `relay-platform/services/api/src/db/repository.itest.ts` (FR-001 (3.24), FR-006 (3.24)): two attachments survive the round trip in order, and a message sent without them stores `NULL`.
- [ ] T024 Write the empty-text test in `relay-platform/services/api/src/db/repository.itest.ts` (FR-019 (3.24), FR-019a (3.24)): a message with `text = ''` and one attachment is stored, read back as a live message, and **is not a tombstone to any of the five places that test for one**. Assert the predicate, not the absence of a crash.
- [ ] T025 Commit phase 4 in `relay-platform`, naming FR-001 (3.24), FR-005 (3.24), FR-006 (3.24), FR-019 (3.24), FR-019a (3.24), FR-019b (3.24). Gates first.

---

## Phase 5: User Story 1 — a message carries a picture somebody else is hosting (P1) 🎯 MVP

**Goal**: FR-MSG-11's P2 half, reaching a socket and a history read.

**Independent test**: send a message with one external-URL attachment, assert a connected
member's socket receives it with the attachment, and assert the history route returns the same
attachment for a client that was not connected.

- [ ] T026 [US1] Return attachments from the send route in `relay-platform/services/api/src/messages/messages.controller.ts` (FR-001 (3.24)), and **spell the field list out** rather than spreading the row — that controller's own comment says why: a new column joins the public response only when somebody decides it should.
- [ ] T027 [US1] Add attachments to the published `message.created` payload in `relay-platform/services/api/src/messages/messages.controller.ts` (FR-008 (3.24)).
- [ ] T028 [US1] Add attachments to `listMessages`'s column list in `relay-platform/services/api/src/db/repository.ts` (FR-009 (3.24)), mapping `NULL` to `[]` (FR-007 (3.24)). **`?? []` in the map, not in the caller** — chapter 3.23 shipped a control test that was green before its field existed because an absent key and a null one read the same through `??`.
- [ ] T029 [US1] Write the route test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-001 (3.24), FR-009 (3.24), SC-001 (3.24)): send with an attachment, read it back through the history route, assert the kind and the URL.
- [ ] T030 [US1] Write the delivery test in `relay-platform/services/gateway/src/session.itest.ts` (FR-008 (3.24), SC-001 (3.24)): a connected member receives `message.created` carrying the attachment. **Two members and a count, not a first match** — a `waitFor` that resolves on the first match cannot see a duplicate.
- [ ] T031 [US1] Write the empty-list test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-007 (3.24)): a message sent without attachments reads back with `attachments: []`, asserted with `toHaveProperty("attachments", [])` so an **absent** field fails. The `??` trap again, in the shape that already caught this project once.
- [ ] T032 [US1] Falsify the empty-list mapping: remove the `?? []` from `listMessages` in `relay-platform/services/api/src/db/repository.ts`, watch the empty-list test in `relay-platform/services/api/src/messages/messages.itest.ts` go red, and put it back.
- [ ] T032a [US1] Write the isolation test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-014 (3.24)): a non-member of a private channel reading its history receives **no message and therefore no attachment**, and the answer is byte-identical to a channel that does not exist. **The attachment rides the message's own predicate** — chapter 3.15's `channelVisibleTo`, which chapter 3.23's falsification proved is only observable through a private channel of the same tenant. This test is what says the attachment adds no second surface.
- [ ] T033 [US1] Write the outsider test in `relay-platform/packages/outsider/src/integrate.itest.ts` (SC-001 (3.24)): send a message with an attachment over REST as a customer would, and assert a member's socket hears it with the attachment. **This is the only instrument that boots the shipped binary**, and chapter 3.23's plan scheduled an audit over this file without any task writing to it. **Rebuild the compose images with `--build`** before believing a field is missing.
- [ ] T034 [US1] Commit phase 5 in `relay-platform`, naming FR-001 (3.24), FR-007 (3.24), FR-008 (3.24), FR-009 (3.24), SC-001 (3.24). Gates first.

**Checkpoint**: a message carries a picture and everyone watching sees it. This is the MVP.

---

## Phase 6: User Story 2 — ten is a limit and eleven is a refusal (P1)

**Goal**: FR-MSG-11's bound, enforced at the boundary like every other list bound here.

**Independent test**: send eleven attachments, assert the refusal names the field and the
bound, and assert no message row was written.

- [ ] T035 [US2] Write the over-the-bound test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-005 (3.24), SC-002 (3.24)): eleven attachments are refused with `invalid_request` naming the field, **and the channel's message count is unchanged afterwards**. The second half is the assertion — a 400 raised after the write passes the first.
- [ ] T036 [US2] Write the exactly-ten test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-005 (3.24)): ten succeed and all ten come back. A bound tested only from above is a bound that could be nine.
- [ ] T037 [US2] Write the bad-kind test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-002 (3.24)): a kind outside the three is refused rather than stored.
- [ ] T038 [US2] Write the scheme tests in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-004 (3.24), SC-004 (3.24)): `javascript:`, `data:`, `file:` and `vbscript:` are each refused **through the route**, not only at the schema. A schema test proves the rule exists; only a route test proves it fires.
- [ ] T039 [US2] Add the `media_not_available` refusal for a `{"type": "media"}` attachment (FR-003 (3.24), FR-003a (3.24)) — a new error code in `relay-platform/packages/protocol/src/codes.ts` with the argument for its own code written at the entry, and the pinned count in `codes.test.ts` moved. **Compare the measured number of pinned places against T007's prediction and record both.**
- [ ] T040 [US2] Write the media-refusal test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-003a (3.24)): the refusal says hosted media is unavailable rather than that the field is invalid, and its status is 422.
- [ ] T041 [US2] Write the same-bound-on-both-doors test in `relay-platform/services/gateway/src/session.itest.ts` (FR-005 (3.24)): eleven attachments through the socket's `message.send` are refused too. **A message sent through a socket and a message sent through REST must be the same message**, and the two doors already disagree about the idempotency key.
- [ ] T042 [US2] Commit phase 6 in `relay-platform`, naming FR-002 (3.24), FR-003 (3.24), FR-003a (3.24), FR-004 (3.24), FR-005 (3.24), SC-002 (3.24), SC-004 (3.24). Gates first.

---

## Phase 7: User Story 3 — the moderator, the tombstone, and what an edit leaves alone (P2)

**Goal**: the interaction between attachments and the two mutations chapter 3.23 built.

**Independent test**: send a message with attachments, delete it, and assert the history route
returns the tombstone with an empty attachment list.

- [ ] T043 [US3] Write the tombstone test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-012 (3.24), SC-003 (3.24)): a deleted message reads back with `text: null` and `attachments: []` on every read path that returns it. **The deletion already nulls the column** — chapter 3.23 wrote that line following SAD §342 — so this tests the read path's mapping, not the writer.
- [ ] T044 [US3] Write the deletion-event test in `relay-platform/services/gateway/src/session.itest.ts` (FR-013 (3.24)): the `message.deleted` frame carries no attachment field at all, asserted as an exact key set rather than as `payload.attachments === undefined`.
- [ ] T045 [US3] Write the edit test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-016 (3.24)): editing a message's text leaves its attachments unchanged, in order. **The failure this catches is silent** — an `UPDATE … SET text = ?, attachments = ?` written without care drops the photograph and returns 200.
- [ ] T046 [US3] Falsify T045: add `attachments` to `editMessage`'s `SET` list in `relay-platform/services/api/src/db/repository.ts`, watch T045 go red, and take it out.
- [ ] T047 [US3] Write the edit-history test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-016 (3.24)): `message_edits` gains no attachment column and the edit-history route says nothing about attachments. Chapter 3.23 built that table to the SAD's published DDL; **this chapter does not add to it**, and the test is what stops a later reader assuming it did.
- [ ] T048 [US3] Commit phase 7 in `relay-platform`, naming FR-012 (3.24), FR-013 (3.24), FR-016 (3.24), SC-003 (3.24). Gates first.

---

## Phase 8: The read paths

**Six shapes, and research R4 says only two of them change.** Naming the four that do not is
what stops a later reader treating an omission as a bug.

- [ ] T049 Add attachments to `getMessageByIdempotencyKey` in `relay-platform/services/api/src/db/repository.ts` (FR-011 (3.24)). **That read already omits `user`, which the others carry** — a pre-existing difference this chapter records and does not fix.
- [ ] T050 Write the idempotent-retry test in `relay-platform/services/api/src/messages/idempotency.itest.ts` (FR-011 (3.24)): a repeated send with the same key returns the original message's attachments and **writes no second row**, read from the database rather than from the response.
- [ ] T051 Add attachments to the resume backfill's mapping in `relay-platform/services/api/src/internal/backfill.controller.ts` (FR-010 (3.24)).
- [ ] T052 Write the resume test in `relay-platform/services/api/src/internal/backfill.itest.ts` (FR-010 (3.24), SC-005 (3.24)): a client away across a send with attachments receives them in the replay. **That file is where chapter 3.23's US4 tests live**, because `services/gateway/src/resume.itest.ts` boots against a stubbed api and has no rows.
- [ ] T053 [P] Record in `specs/042-chapter-3-24/baseline.txt` the four read shapes that do **not** change and why: `listChannelsForUser.last_message` (a preview shows what was said), `listMessagesRaw` (a test-only helper, five call sites), and the two internal reads inside `editMessage` and `deleteMessage`.
- [ ] T054 Commit phase 8 in `relay-platform`, naming FR-010 (3.24), FR-011 (3.24), SC-005 (3.24). Gates first.

---

## Phase 9: The events

- [ ] T055 Add attachments to `MessageCreatedData` in `relay-platform/services/api/src/outbox/event.ts`. **This lands on `message.created` AND `message.updated` at once** — chapter 3.23's FR-008a (3.24) requires those two payloads to stay identical — and on neither `message.deleted` nor the membership events.
- [ ] T056 Update the consumer-side union branches in the same file for both types, and the pinned key-set assertions in `relay-platform/services/api/src/outbox/event.test.ts`. **`consumer/runtime.ts` answers a failed parse with `message.term()`**, which stops redelivery for good, so a branch not widened is a row destroyed at the consumer — and the lane cannot see it, because it runs `RELAY_EVENT_CONSUMER=off`.
- [ ] T057 [P] Write the payload tests in `relay-platform/services/api/src/outbox/event.test.ts` (FR-015 (3.24)): the creation and edit payloads carry attachments **identically**, compared as key sets, and the deletion payload has no such key.
- [ ] T058 [P] Confirm the count required by FR-017 (3.24) is derivable from what this chapter writes, and record the one-line answer in `specs/042-chapter-3-24/baseline.txt`. §4.14's `attachment_count UInt8` is Part 4's and unbuilt; nothing is owed here beyond the array having a length.
- [ ] T059 Verify that no attachment URL reaches the platform's own logs (NFR-SEC-06) by grepping the log-emitting call sites in `relay-platform/services/api/src/consumer/recorder.ts` and `relay-platform/services/api/src/messages/messages.controller.ts`, and record the finding in `specs/042-chapter-3-24/baseline.txt`. `recorder.ts:25` states the rule for message text; **a URL is closer to a body than to an identifier.**
- [ ] T060 Commit phase 9 in `relay-platform`, naming FR-015 (3.24), FR-017 (3.24). Gates first.

---

## Phase 10: The documents

- [ ] T061 Correct `packages/protocol/src/frames.ts`'s comment scheduling attachments for Part 4 (FR-018 (3.24)), which turns one of `check-prose.py`'s claims green.
- [ ] T062 [P] Add the `media_not_available` section to `docs/08-error-reference.md` with a cause and a client action — the gate requires both and a body over 200 characters. **This turns `check:errors` green**, red on purpose since phase 6. **Do not add a heading that is not a member of `ERROR_CODES`**; the orphan check fails on it with no exemption.
- [ ] T063 [P] Document the attachment shape in `docs/05-sad.md` §6.1 beside `messages.attachments`, which the document declares and says nothing about — the same omission chapter 3.23 filled for `messages.metadata` — **and state what every read path does with an attachment** (SC-006 (3.24)), derived from the code at the time of writing rather than from this task list. Chapter 3.23's equivalent counted three read paths until somebody measured a fourth.
- [ ] T064 [P] Add the revision row to `docs/04-srs.md` Appendix D: FR-MSG-11's external-URL half built, the `media_id` half deferred to §4.14 with the refusal that names it. **Say that no clause changed**, the way rows 1.4 through 1.6 do.
- [ ] T065 [P] Add the chapter 3.24 row to the published chapter table in `docs/07-tutorial-plan.md`, after 3.23's. **`sync-docs.sh` does NOT publish that file** — its own comment explains why at length.
- [ ] T066 Run `pnpm -s sync:docs` from `relay-tutorial`. The mirror is machine-written and drifts the moment a canonical document is edited.
- [ ] T067 Commit phase 10 in `relay`, `relay-tutorial`, naming FR-018 (3.24), SC-006 (3.24). Gates first, `pnpm build` before `check:errors` because that gate reads the built `dist`.

---

## Phase 11: The chapter

- [ ] T068 Count what the chapter **teaches** and what it must **fence**, as two columns in `specs/042-chapter-3-24/chapter-notes.md`, and never ask either number to do the other's job.
- [ ] T069 Estimate the word count in `specs/042-chapter-3-24/chapter-notes.md` from the number of **arguments**, and say which. **Estimate at 545 words per argument and stop adjusting for what the argument is against** — chapter 3.23 predicted 420 on the theory that arguing against published material costs more, and came in at 545 against 3.22's 583.
- [ ] T070 Write the chapter page at `relay-tutorial/app/(en)/part-3/chapter-24/<slug>/page.mdx`. **MDX is not markdown**: an indented block containing braces is a JSX expression.
- [ ] T071 [P] Write `relay-tutorial/app/(en)/part-3/chapter-24/<slug>/figures.ts` — the attachment shape with its future arm, the six read shapes and which two change, and what a tombstone leaves behind.
- [ ] T072 Check the fence exposure of every file this chapter touches and record it per locale in `specs/042-chapter-3-24/baseline.txt`. **A file whose chain lives entirely in the appendix cannot be fenced by a chapter.**
- [ ] T073 Generate the fences with the predecessor `git rev-parse part3-ch23^{commit}`, **a commit and not the tag**, and **against the working tree rather than `HEAD`**. **Exclude this chapter's own pages from the "is it already fenced" question** — chapter 3.23's generator read its own output twice and produced a diff of a file against itself.
- [ ] T074 Translate the page to `relay-tutorial/app/(vi)/vi/part-3/chapter-24/<slug>/page.mdx` **by splitting on the fence regex and reusing the English fence blocks verbatim**, so the mirror is byte-identical by construction. Regenerating them against the tree does not work: by then the English page has fenced the new files.
- [ ] T075 [P] Mirror `figures.ts` into the `(vi)` route.
- [ ] T076 Register the chapter in `relay-tutorial/lib/tutorial.ts` with `status: "published"` and `translatedIn: ["vi"]`. **Not the sitemap**, which derives every entry from that registry.
- [ ] T077 Run `check:fences` and `check:figures` from `relay-tutorial` with exit codes captured, and expect the fenced-file count to rise from **240** and the figure count from **254**. Both numbers were measured at the close of 3.23; the figure baseline that chapter inherited was stale by four.
- [ ] T078 Commit phase 11 in `relay-tutorial` and `relay-platform`. Gates first, in both.

---

## Phase 12: Polish and close-out

**Three tasks below can edit a fenced file after T077 ran the fence check.** Any late edit
forces **this chapter's** diff for that file to be regenerated before T088 — not a
predecessor's, which describe earlier states and must not be touched.

- [ ] T079 Read every new test's title against its assertion, one at a time, in **every file this chapter adds tests to, named rather than described**: `relay-platform/packages/protocol/src/attachments.test.ts`, `relay-platform/packages/protocol/src/frames.test.ts`, `relay-platform/services/api/src/db/repository.itest.ts`, `relay-platform/services/api/src/messages/messages.itest.ts`, `relay-platform/services/api/src/messages/idempotency.itest.ts`, `relay-platform/services/api/src/internal/backfill.itest.ts`, `relay-platform/services/api/src/outbox/event.test.ts`, `relay-platform/services/gateway/src/session.itest.ts`, `relay-platform/packages/outsider/src/integrate.itest.ts`. **Nine, and expect the count to be wrong** — chapter 3.23's task named eleven files and the tree had fourteen. **Strip any task id from a title before it ships**: chapter 3.23 wrote fifty-two `T0xx:` prefixes and its own audit removed them, because a task id in a title outlives the task. Requirement ids belong there; task ids do not.
- [ ] T080 Run the coverage lane with the nine pinned variables and pin the new production paths in `relay-platform/vitest.coverage.config.mts`. **Read `coverage-summary.json`, not the text table** — the text reporter omits a file at 100% on all four metrics, and the run writes no report at all if a test fails.
- [ ] T081 If any arm of `relay-platform/services/api/src/db/repository.ts`, `relay-platform/services/api/src/messages/messages.schema.ts`, `relay-platform/services/api/src/messages/messages.controller.ts` or `relay-platform/packages/protocol/src/attachments.ts` is uncovered, ask whether the code should be **deleted** before asking for a test, and pin the result in `relay-platform/vitest.coverage.config.mts`. The ratchet has removed code five times; chapter 3.23 removed a `?? "unknown"` that was unreachable **and** would have put that word on the wire as somebody's name.
- [ ] T082 [P] Re-derive the files-changed count from `git diff --name-only` and compare it with T068's prediction in `specs/042-chapter-3-24/chapter-notes.md`. A first count is expected to be wrong; chapter 3.23's moved from 36 to 37 during close-out.
- [ ] T083 [P] Re-derive `specs/042-chapter-3-24/traceability.md` against the shipped tree, both directions, checking **every quoted test title as an exact string** rather than by eye.
- [ ] T084 Run the credential scan over the chapter's diff and record the patterns searched and every hit classified in `specs/042-chapter-3-24/baseline.txt`. **Widen each pattern past the examples in front of you**, and expect the scan to match its own paragraph — chapter 3.23's did.
- [ ] T085 Complete `specs/042-chapter-3-24/gaps.md`, carrying chapter 3.23's items with their status **re-checked against the tree rather than copied**. Its item 9 is addressed to whoever next finds the unit lane red with no containers, and its C6 — nine files that discard their child's output — is the reason that chapter's two battery failures have no cause. **Add `avatar_url` accepting `javascript:`** (research R7), found by running the validator rather than reading it.
- [ ] T086 Stop the api, gateway and dispatcher containers, then run the twenty-run battery of `pnpm test:integration` in `relay-platform`. **Nothing else runs on the machine, and that includes your own tooling.**
- [ ] T087 Record the battery in `specs/042-chapter-3-24/baseline.txt` with the mean over the **green** runs, the stdev, and every failure's file and message. **A red run is short because turbo abandons the remaining packages.** Report the confidence interval, not the fraction: chapter 3.23's 18 of 20 is `[1.23%, 31.70%]` at 95%, and twenty runs cannot separate a 5% lane from a 10% one.
- [ ] T088 **Run all gates LAST**, after every record is written: `check:fences`, `check:docs`, `check:figures`, `check:srs`, `check:errors` from `relay-tutorial`, plus this chapter's four Python instruments. Capture every exit code into a variable; **do not pipe into `tail`**.
- [ ] T089 Commit the close-out records in `specs/042-chapter-3-24/` **before anything is tagged**.
- [ ] T090 Tag `part3-ch24` in all three repositories with `git tag -a`, **submodules first**, and verify with `git ls-tree part3-ch24^{commit} relay-platform relay-tutorial` that the root's tree names exactly the two submodule tag commits.
- [ ] T091 Trim `CLAUDE.md`. It is 220 lines after chapter 3.23's trim and is loaded into every session.
- [ ] T092 Hand `specs/036-chapter-3-18/reader-protocol.md` to a second person. **Named by ten chapters and closed by none.** No command in this repository discharges it.

---

## Dependencies and execution order

    Phase 1   premises, instruments, the READER test   blocks everything
    Phase 2   the shape                                blocks the wire
    Phase 3   the wire                                 blocks every route below it
    Phase 4   the writer                               needs Phases 2 and 3
    Phase 5   US1, a picture reaches a socket          needs Phase 4   🎯 MVP
    Phase 6   US2, the bound and the refusals          needs Phase 4
    Phase 7   US3, the tombstone and the edit          needs Phase 5
    Phase 8   the read paths                           needs Phase 4
    Phase 9   the events                               needs Phase 4
    Phase 10  the documents                            needs everything above
    Phase 11  the chapter                              needs Phase 10
    Phase 12  close-out                                gates LAST

**T004 must pass against unchanged code or the plan changes.** That is Phase 1's whole point.

**Parallel opportunities, and there are fewer than the phase count suggests.** `[P]` means a
different file, and this chapter's tests concentrate in four: `messages.itest.ts` carries
eleven tasks across four phases, `repository.itest.ts` four, `repository.ts` five, and
`event.ts` and `event.test.ts` two each. Every one of those runs in sequence.

What genuinely parallelises: T002 and T003 in Phase 1, two different files; T037 and T038 in
Phase 6, though both land in `messages.itest.ts` and must therefore go in sequence — **noted
here as a correction to the marker rather than left to be discovered**; T062 through T065 in
Phase 10, four different documents; T071 and T075 in Phase 11, the figures and their mirror;
T082 and T083 in Phase 12, two different records.

**Four `[P]` markers were written and stripped before this file shipped.** T037 and T038 both
edit `relay-platform/services/api/src/messages/messages.itest.ts`, and `[P]` means a different
file. Chapter 3.23 lost eleven markers to the same check and recorded that **no instrument
compares a task's `[P]` with its file path** — so the check is a person reading the two columns
against each other, and it was run here rather than deferred to an analysis pass.

T011 edits `relay-platform/packages/protocol/src/attachments.test.ts`, which T010 writes; T024
edits `relay-platform/services/api/src/db/repository.itest.ts`, which T023 writes. **Both were
found by listing every `[P]` task's file paths and looking for a name appearing twice** — a
five-line check, and the reason it is worth writing down is that reading the markers one at a
time finds neither.

**T003, T007, T053 and T058 keep their markers and all four append to
`specs/042-chapter-3-24/baseline.txt`.** That is the same exception chapter 3.23 made and
stated: appending a paragraph to a record is not the hazard two edits to a test file are. The
exception is visible here rather than left to look like an inconsistency.

**Nine tasks also said "in the same file" instead of naming one.** A relative reference makes a
task unexecutable on its own, which is the property this file exists to have. All nine now
carry the path.

**MVP**: Phases 1–5. A message carries a picture somebody else is hosting, and everyone
watching sees it — FR-MSG-11's P2 half with `messages.attachments` written for the first time
since chapter 2.1 declared it.
