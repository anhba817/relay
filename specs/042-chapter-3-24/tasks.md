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

- [X] T001 **DONE DURING PLANNING**, because the instruments are what the rest of the phase is checked by. **Seven instruments, not four**: `regen-traceability.py` joined them in analysis pass 3, after the map was retyped by hand three times and had a different bug each time — a stale count, then a quoted figure the sweep read as a fresh claim, then a duplicated footer. `sweep.py` caught all three, which is the system working; retyping a generator three times is not. `specs/042-chapter-3-24/check-prose.py` is written with its claim list emptied and this chapter's one entry added; `check-refs.py` and `sweep.py` are copied with `FOREIGN` cleared. **The copy carried a third stale field nobody had found before**: `\(3\.23\)` hard-coded in the citation rule, which reported all twenty-four requirements as untraced on its first run. It is now derived from the directory name, so the next copy cannot inherit it. The copies of `check-refs.py` and `sweep.py` are already in place with `FOREIGN` cleared; that clearing is a step, not an oversight, and chapter 3.23's copy arrived carrying thirty-one stale pairs and a docstring naming the wrong chapter. `check-quickstart.py` joined them in analysis pass 13, and its subject is the blind spot every earlier pass shared: `quickstart.md` was read as an output, not as a source, so P3a's plain-language naming of the socket path's third drop point sat unread while twelve passes compared identifiers between the other three artifacts. It checks that every production file the guide names is covered by a task or **declared** as a warning, and that every success criterion is named by a scenario's `**Expected**` line. Its first version searched the whole file for the criterion, which passed on a criterion merely discussed — the probe meant to prove it red stayed green, and narrowing it to the `**Expected**` lines is what made the probe work. `check-checklist.py` joined them at pass 14, holding `checklists/requirements.md` to the spec it certifies: every code-shaped reference in `spec.md` enumerated, the requirement and criterion counts stated rather than assumed, and no open box. **`sweep.py` could always have caught the count** — it compares a stated figure against the measured one — but the checklist never stated a figure, so there was nothing to compare. A gate that certifies silently cannot be checked.
- [X] T002 [P] **DONE DURING PLANNING.** `specs/042-chapter-3-24/check-prose.py` holds two entries and is **RED**: `packages/protocol/src/frames.ts`'s *"metadata/attachments/edit/tombstone fields arrive with Part 2/4"* (FR-018 (3.24)), and `services/api/src/db/schema.ts`'s comment listing what is deliberately absent if it names attachments — **read before adding**, because chapter 3.23 added an entry for a sentence that was true and had to delete the gate rather than satisfy it. `schema.ts`'s absence comment was read and names no attachments, so it gets no entry. **The second was added at analysis pass 15**: `relay-platform/services/api/src/messages/messages.controller.ts` says the REST body and the WebSocket frame payload "cannot drift" because they are the same schema family. They are two schemas validated at two controllers, and they have drifted three times — `idem_key` against `idempotency_key`, the text bound, and FR-019b (3.24)'s pair rule, which this chapter had to be told to carry across. **No checker reads prose**, so the comment has outlived its truth in a file this chapter fences.
- [X] T003 [P] **DONE DURING PLANNING**, with the instruments. `specs/042-chapter-3-24/baseline.txt` holds the nine variables, the compose line, the counts named in T005 and T006, and what the instruments found before any code was written.
- [X] T004 **Write the reader test and run it against unchanged code** in `relay-platform/services/api/src/db/repository.itest.ts`: plant a row with `text = ''` using raw SQL and assert every read path returns it as a **live message** — history in both directions, the channel listing's preview, and the tombstone predicate not firing. **This must pass today.** If it fails, FR-019 (3.24)'s empty-string decision is wrong and the plan changes before a line of production code is written. Chapter 3.23's equivalent proved its read path was already correct and stopped a later phase "fixing" what worked. **Plant a valid attachments value, not garbage** — `NULL` or a well-formed array. The read paths do not re-validate (spec.md's stored-value edge case), so a malformed array planted by raw SQL reaches the gateway's strict parse and closes the socket 1011 rather than failing this test where you can read it. **DONE: it passes.** 49 of 49 in `repository.itest.ts`, and the falsification — planting `NULL` instead of `''` — goes red with `expected null to be ''`. FR-019 (3.24) stands. Recorded in `specs/042-chapter-3-24/baseline.txt`.
- [X] T005 **DONE DURING PLANNING.** The counts are in `specs/042-chapter-3-24/baseline.txt` with their definition stated: occurrences of `text` on non-comment lines in the ten files research R3 names, totalling 70, plus the six read shapes R4 names. **State the counting definition** — chapter 3.23 lost a re-count to a number whose definition was never written down, and its own research note claimed the count was "unchanged" when it could not have been checked.
- [X] T006 **DONE DURING PLANNING**: 45 declared paths, recorded in `specs/042-chapter-3-24/baseline.txt`. Verify against the tree that this chapter adds **no route**, so `relay-platform/services/api/src/isolation/targets.ts` and its derived-count test do not move. Record the current count (45 paths) in `specs/042-chapter-3-24/baseline.txt` as a record — **and credit the check that actually catches a stray route, which is not the number.** No test pins 45. `relay-platform/services/api/src/isolation/targets.itest.ts` walks the live router and asserts *"classifies every derived target exactly once"*: a new route appears in the derived list, has no entry in `CLASSIFICATIONS`, and `unclassified` is no longer empty. The next test is its converse, so a removed route fails too. **Membership in both directions, and the count is incidental** — which matters because this chapter teaches that file and a reader would otherwise take the wrong lesson about the highest-yield check here.
- [X] T007 [P] **DONE DURING PLANNING**: the prediction is **four**, in `specs/042-chapter-3-24/baseline.txt`. Count the pinned places a new error code moves, in `relay-platform/packages/protocol/src/codes.test.ts` and wherever else the total is named, and predict the number in `specs/042-chapter-3-24/baseline.txt`. Chapter 3.22 predicted two and found four; 3.23 predicted four for the outbox types and found five and a half. **The prediction is the point, not the number.**
- [X] T008 Commit phase 1 in `relay` — `specs/042-chapter-3-24/baseline.txt`, the seven instruments, and the reader test. Gates first. **Six, not four** — T001 had already corrected this to five and this line was never re-read; `check-quickstart.py` makes six. A count in one task and a different count in its own phase's commit task is the smallest version of the thing this chapter keeps finding. **`check:fences` IS RED FROM THIS PHASE AND STAYS RED UNTIL T073**, and every phase-commit task below inherits that. T004 appends to `relay-platform/services/api/src/db/repository.itest.ts`, which chapter 3.23's page fences with a hunk running to the file's end, so the chain reconstructs a shorter file than disk holds and the checker says: `[HEAD] …chapter-23/the-words-somebody-wants-back/page.mdx:2689 · repository.itest.ts differs at line 0`. **"Gates first" means the other four**, plus `typecheck`, `lint` and `build`. Check `check:fences` against that exact message rather than for green: a fence failure naming a DIFFERENT file or a different page is a real problem, and a checker crying wolf is how one hides. `check:errors` already carries the same shape of note.

---

## Phase 2: The shape

**Its own module, and the tree's practice is why.** `presence.ts`, `typing.ts`,
`membership.ts` and `revision.ts` each own their shape and their test; `fanout.ts` holds a
subject function and nothing else. Chapter 3.23's task list named `fanout.ts` for its new
grammar and was wrong for exactly this reason.

- [X] T009 Create `relay-platform/packages/protocol/src/attachments.ts` with the shape `contracts/attachments.md` names (FR-002 (3.24), FR-003 (3.24), FR-003b (3.24), FR-020 (3.24), FR-023 (3.24)): a `discriminatedUnion` on `type` with **two** arms, each a `strictObject`: `{ type: "url", kind: "image"|"audio"|"video", url }`, and a `{ type: "media", … }` arm that **always refuses**, carrying FR-003a (3.24)'s message. **The second arm is what puts FR-003a on both doors.** Measured against the pinned zod 4.4.3: a one-arm union answers `{"type":"media"}` with `"Invalid discriminator value. Expected 'url'"` — *that the field is invalid*, which FR-003a (3.24) forbids by name — while two arms answer with the arm's own message, and `services/gateway/src/session.ts:1447` already forwards `issues[0].message`. **The cost is one word of FR-003b (3.24)**: §4.14 now CHANGES this arm rather than adding one. That is a smaller change than adding a discriminator, and stating the trade is better than leaving the next reader to find a contradiction. **Export all five names `contracts/attachments.md` publishes** — `attachmentSchema`, `Attachment` (its `z.infer`), `MAX_ATTACHMENTS`, `ATTACHMENT_URL_MAX` and `ATTACHMENT_SCHEMES` — rather than choosing names here, because both doors import them and two schemas that happen to agree are the defect this chapter is trying not to repeat. `Attachment` is the type the read paths cast the column to, so it is load-bearing outside this package as well as in it. **DONE.** Two arms, five exports, and `new URL(...).protocol` rather than a prefix match.
- [X] T009a Export the **text-and-attachments pair rule** from `relay-platform/packages/protocol/src/attachments.ts` (FR-019 (3.24), FR-019b (3.24)) as a named refinement both send schemas apply — text may be empty when at least one attachment is present, and neither together is a refusal. **One rule, one definition, two callers.** T020's instruction is "a `superRefine` or equivalent, **not two schemas**", and a `superRefine` written into `relay-platform/services/api/src/messages/messages.schema.ts` alone is two schemas by a longer route: `messages.controller.ts:111` validates with `sendMessageBodySchema` and `internal.controller.ts:58` with `internalSendRequestSchema`, and **`messages.schema.ts` is imported by exactly one file** — never by the socket path. **DONE** as `refineTextAndAttachments`. Its first signature would have rejected both callers — `exactOptionalPropertyTypes` means `attachments?: T[]` refuses a caller typed `T[] | undefined`, and the compiler said so before either caller existed.
- [X] T010 [P] Write `relay-platform/packages/protocol/src/attachments.test.ts` asserting the exact key set of the arm, the three kinds and **refusal of a fourth**, the 10-item bound (FR-005 (3.24)), the 2,048-character URL bound (FR-023 (3.24)), and the scheme rule (FR-004 (3.24)). **Assert `javascript:`, `data:`, `file:` and `vbscript:` are all refused** — research R7 measured that `z.url()` accepts every one of them, so a test that only tries `https:` proves nothing. **DONE.** 15 passed, including the four schemes R7 measured `z.url()` accepting, and the media arm's MESSAGE rather than its failure.
- [X] T011 Add the falsification to `relay-platform/packages/protocol/src/attachments.test.ts`: replace the scheme rule with a bare `z.url()` and watch the four refusals go red. **A validator nobody has seen refuse is a validator nobody has checked**, and this one is the whole of FR-004 (3.24)'s protection. **DONE, and it turned three tests red rather than two.** The third is the probe's breadth: replacing the whole chain dropped `.max(2048)` with the scheme rule. Recorded in `specs/042-chapter-3-24/baseline.txt`.
- [X] T012 Export the module from `relay-platform/packages/protocol/src/index.ts`. **DONE**, and verified by requiring the built barrel rather than by reading the export line.
- [X] T013 Commit phase 2 in `relay-platform`, naming FR-002 (3.24), FR-003 (3.24), FR-003b (3.24), FR-004 (3.24). Gates first.

---

## Phase 3: The wire

**This blocks every route below it.** No read path can return an attachment the frame cannot
express, and `messageSchema` is a `strictObject`.

- [ ] T014 Add `attachments` to `messageSchema` in `relay-platform/packages/protocol/src/frames.ts` as a **REQUIRED array, not an optional field** (FR-008 (3.24), FR-015 (3.24), FR-022 (3.24)).

  **Required is a decision with a cost, and both halves belong in the chapter.** FR-022 (3.24) asks a reader to need no special case, and `messageSchema` is a `strictObject` — so required means the compiler names every producer that forgets, at all five construction points, and a message with no attachments carries `[]`. Optional would let the wire omit the key on the one path a client cannot re-read.

  **What it costs is a rolling deploy.** `messageCreatedSchema.shape.payload` is what `services/gateway/src/fanout.ts` parses arrivals with, so during a deploy an old instance publishes a payload with no attachments and a new instance **drops the frame**. That is ADR-24's own argument — a field added on one side of a rolling deploy fails loudly on the other — and it is acceptable here for the reason ADR-07 states: a dropped fabric frame is not a lost message, because the cursor recovers it. **Say so in the chapter rather than discovering it in a deploy.**

  **And decide whether this needs an ADR against chapter 3.23's ADR-24**, which refused to widen the same object's `text`. The plan predicts one; the argument to make or refuse is that adding a field and loosening an existing one's type are different acts. **A prediction that turns out wrong is worth recording either way.**

  `messages.controller.ts:228`'s guard comment says a tombstone *"could not be published anyway"* because `messageSchema.text` is `z.string()`. That stays true — this task adds a field and does not touch `text` — and it is now a sentence beside an edit, which is how the four this chapter's predecessor had to correct got there.
- [ ] T014a Set `attachments` at **every** place that constructs a `messageSchema` payload, immediately after T014 and **in this phase** (FR-022 (3.24)). **Build the protocol package first, then typecheck** — `pnpm --filter @relay/protocol build`, then `npx tsc -p services/api/tsconfig.json --noEmit` and the same for the gateway. The compiler is the instrument, not a reading, **and it answers "nothing to do" in the obvious order**: `tsconfig.base.json` sets `"noEmit": true` so `tsc -p` emits nothing, the emitting config is `tsconfig.build.json`, and the consumers resolve `@relay/protocol` through its `exports.types` at `dist`. Analysis pass 18 ran this probe against a `dist` a day old and believed the zero. Same shape as `check:errors`, which the chapter already warns about. **It names 4 of the 7 sites `plan.md` lists** — the other three are not `messageSchema` payloads and no command will name them.

  **THIS IS WHY IT IS HERE AND NOT LATER.** T014 makes the field required, so from that line until this one **`typecheck` is red across the whole workspace** — and T018 and T025 both say "Gates first". The first draft put this in Phase 5, which would have committed two phases with a broken typecheck. Every chapter in this series commits each phase green.

  **The set is larger than the production sites.** Fifteen files import the `Message` type and **eight of them build a literal — eighteen in all**: `session.test.ts`, `isolation.itest.ts`, `connections.itest.ts`, `typing.itest.ts`, `resume.test.ts`, `resume.itest.ts`, and both `fanout.itest.ts`. Research R13 counts four DOORS that write a message, which is a different set; **the first draft of this task borrowed that number and applied it here**, which is this chapter's fourth premise inherited without re-running it. Count with the compiler and record what it says.
- [ ] T015 [P] Add `attachments` to `messageSendSchema`'s payload in `relay-platform/packages/protocol/src/frames.ts` (the socket's door) and to `internalSendRequestSchema` in `relay-platform/packages/protocol/src/internal.ts` (the internal hop), both importing the bound from `attachments.ts`. **The two doors disagree about the idempotency key already** — `idem_key: z.string().min(1).max(255)` against `idempotency_key: z.string().uuid()` — and `packages/outsider/src/integrate.itest.ts` records the cost of that in its own comment.
- [ ] T016 [P] Update the frame tests in `relay-platform/packages/protocol/src/frames.test.ts`: the exact key set of `messageSchema` moves from six keys to seven, and `message.deleted`'s payload must still refuse an attachments field (FR-013 (3.24)). **Chapter 3.23 changed that payload and turned two direction tests red in two files** — `session.itest.ts` and `isolation.itest.ts` both build a forged frame from the same object; grep for `case "message.deleted":` before assuming one.
- [ ] T015a Widen `internalSendResponseSchema` in `relay-platform/packages/protocol/src/internal.ts` with attachments (FR-001 (3.24)). **This one is not symmetry, it is a break waiting to happen.** That schema is a `strictObject` and `services/gateway/src/api-client.ts:248` **parses the api's response with it**; `services/api/src/internal/internal.controller.ts:84` returns `{ ...message, user }`, a spread. The moment `sendMessage` returns an attachments key, the spread carries it and the strict parse rejects it — **every socket send fails**, not just one without attachments. **Required, not optional** (FR-022 (3.24)): this is a payload that carries a message. That makes T015b an obligation in *this* phase rather than a later improvement. Measured against the pinned zod 4.4.3, all three combinations: the schema without the key rejects a value carrying it (the mode described above), a **required** key rejects a value missing it — `false` — and an optional key accepts that value, which parses green while putting the wire in breach of FR-022 (3.24) with nothing red to say so. Only the required field and T015b landing together is honest.
- [ ] T015b Carry `attachments` on **both** of `sendMessage`'s return paths in `relay-platform/services/api/src/db/repository.ts` (FR-001 (3.24), FR-022 (3.24)), in this phase, immediately after T015a — the same schema-and-its-values pairing T014 and T014a make. Today `repository.ts:457` builds the insert branch from locals and `repository.ts:278` spreads `getMessageByIdempotencyKey` into the `duplicate: true` branch, and **neither carries the key**; the second needs that read's select widened here too, because a required field cannot wait for T049 five phases away. In this phase the value is the no-attachments representation `data-model.md` names, and that is **true rather than a placeholder**: T019 does not open the door until phase 4. Type the column at each site with `sql<Attachment[] | null>` per `data-model.md`'s "What the reader gets" — a bare `jsonb()` infers as `unknown` and will not assign.

  **It is latent today for a reason worth knowing**: `MessageRow` already carries `edited_at?` from chapter 3.23, which that same schema does not list — and nothing breaks because `sendMessage`'s two return paths never set the key. A field on the type and never on the value is a trap that springs the day somebody sets it.
- [ ] T017 Record in `specs/042-chapter-3-24/baseline.txt` that **the plan's prediction was wrong in both directions**, which analysis found by reading `relay-platform/services/gateway/src/session.ts` rather than assuming it. The plan said the gateway "forwards the widened payload without a line changing". Half of that is true — an arriving `message.created` is forwarded whole. The other half is not:

      session.ts:1512   const { channel, text, idem_key } = frame.data.payload
                        a NAMED destructure: a field added to the inbound frame
                        is parsed and dropped
      session.ts:1534   the gateway BUILDS the outbound payload field by field
                        after a socket send, so a field the api returns is absent
                        from the frame every member receives

  **The prediction is what made this cheap.** The plan said "verify, do not assume" and named the file; verifying took one `sed`.
- [ ] T017a Record the decision about `messageSendSchema.payload.text` in `specs/042-chapter-3-24/baseline.txt` and **do not change it**. That field is `z.string()` — **no minimum and no maximum** — while REST and `internalSendRequestSchema` both bound it 1 to 8,000 (FR-MSG-01). A socket client can send 100,000 characters and be refused one hop later by the api.

  **Not fixed here, and the reason is scope rather than effort.** Tightening it is one line, and it is FR-MSG-01's bound, not FR-MSG-11's: a chapter about attachments that quietly narrows what a text frame may carry is changing a published contract under cover of a different requirement. **This chapter is editing that exact schema**, which is what makes the omission worth stating rather than leaving — `gaps.md` gets it, with the one-line fix named so the next chapter to touch FR-MSG-01 does not rediscover it.
- [ ] T017b Relax the same bound in `relay-platform/packages/protocol/src/internal.ts`'s `internalSendRequestSchema` (FR-019 (3.24)), which is `z.string().min(1).max(8000)` and is **the door every socket send goes through**. Without it FR-019 is met on one of two doors: a REST client may send a photograph with no caption and a socket client may not, with no requirement anywhere saying so. **Apply T009a's refinement here too, in the same task.** Relaxing `min(1)` alone carries the PERMISSION across and leaves the REFUSAL behind: FR-019b (3.24) is a MUST — a message with no text and no attachments must still be refused — and after this relaxation nothing on this door enforces it, so `{"text": "", "attachments": []}` over the socket commits.
- [ ] T018 Commit phase 3 in `relay-platform`, naming FR-008 (3.24), FR-015 (3.24). Gates first.

---

## Phase 4: The writer

- [ ] T019 Add `attachments` to the send body in `relay-platform/services/api/src/messages/messages.schema.ts` (FR-001 (3.24), FR-005 (3.24)), optional, bounded by the constant `attachments.ts` exports.
- [ ] T020 Relax the text bound in `relay-platform/services/api/src/messages/messages.schema.ts` (FR-019 (3.24), FR-019b (3.24)): text may be empty **when at least one attachment is present**, and a body with neither is still refused. **Apply T009a's exported refinement rather than writing the rule here** — the rule is about the pair, and expressing it per-schema puts the decision in whichever one the caller happened to hit. This door and the socket's are validated by different schemas, so a rule written into this file is a rule the socket does not have.

  **AND `ctx.addIssue` MUST CARRY `path: ["text"]`.** Measured against the repository's own zod: an object-level refinement produces `path = []`, and `zod-validation.pipe.ts:33` omits `field` when the path is empty — correctly, by its own comment, because a whole-body failure has no field to name. **FR-019b's failure is about two named fields**, so without a path this is the one refusal in the chapter that cannot tell a caller which key to fix, and EIR-API-04 makes `field` the thing an integrator acts on.

      addIssue({ code: "custom", path: ["text"], message: "…" })

  `text` rather than `attachments` because supplying a text is the repair a caller who sent neither almost always wants; the message names both.
- [ ] T020b Assert the refusal's `field` in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-019b (3.24)): a body with no text and no attachments is refused with `field` reading **`text`**, not absent. Measured shapes for the sibling refusals, so the three assertions do not drift apart:

      neither text nor attachments   field = text            <- only if the path is set
      eleven attachments             field = attachments
      a bad kind at index 3          field = attachments.3.kind
- [ ] T020a Write the both-doors test for the empty text in `relay-platform/services/gateway/src/session.itest.ts` (FR-019 (3.24)): an attachments-only message sent **over the socket** is accepted (FR-019 (3.24)) **and one with neither text nor attachments is refused** (FR-019b (3.24)). Both halves, because the acceptance passes the moment the bound is relaxed and the refusal needs a rule the relaxation removes. **A rule expressed in two schemas is two rules**, and the two doors already disagree about `idem_key` and about the text bound itself — see the record in `specs/042-chapter-3-24/baseline.txt`.
- [ ] T021 Thread attachments through `relay-platform/services/api/src/messages/messages.service.ts` to the repository (FR-001 (3.24)).
- [ ] T022 Write attachments in `sendMessage`'s INSERT in `relay-platform/services/api/src/db/repository.ts` (FR-001 (3.24), FR-006 (3.24)): the array as sent, in order, or `NULL` when there are none. **`NULL` and `[]` are different values** and `data-model.md` says which the column stores — every row written before this chapter is `NULL` and stays valid without a backfill. **The return paths already carry the key from T015b**; this task makes the value real instead of empty. The INSERT and the return are two changes, not one.
- [ ] T023 [P] Write the writer test in `relay-platform/services/api/src/db/repository.itest.ts` (FR-001 (3.24), FR-006 (3.24), FR-017 (3.24)): two attachments survive the round trip **in order**, and a message sent without them stores `NULL`. The ordered round trip is what makes §4.14's `attachment_count` derivable — an array with a length — so FR-017 (3.24) is verified here rather than asserted in a record.
- [ ] T024 Write the empty-text test in `relay-platform/services/api/src/db/repository.itest.ts` (FR-019 (3.24), FR-019a (3.24)): a message with `text = ''` and one attachment is stored, read back as a live message, and **is not a tombstone to any of the five places that test for one**. Assert the predicate, not the absence of a crash.
- [ ] T022a Thread attachments through the gateway's inbound destructure at `relay-platform/services/gateway/src/session.ts:1512` (FR-001 (3.24)). **`const { channel, text, idem_key } = frame.data.payload` is a named destructure**, so widening `messageSendSchema` puts the field on the wire and nothing carries it further: the message commits without attachments and the client is acked as though it worked.
- [ ] T022b Thread attachments through `relay-platform/services/api/src/internal/internal.controller.ts:68` (FR-001 (3.24)). The handler builds `{ text: body.text, …(idempotency_key) }` by name, so a field on `internalSendRequestSchema` reaches this line and stops.
- [ ] T022c Write the socket-door test in `relay-platform/services/gateway/src/session.itest.ts` (FR-001 (3.24), FR-005 (3.24)): a message sent **over the socket** with **two** attachments commits with them and comes back from history **in order** (FR-006 (3.24)). **Every other test in this chapter enters through REST**, including the outsider one — so this is the only test that can see the three named points above, and without it they fail silently while the suite stays green. That is chapter 3.21's inert module in a new place: parsed, ignored, invisible.
- [ ] T025 Commit phase 4 in `relay-platform`, naming FR-001 (3.24), FR-005 (3.24), FR-006 (3.24), FR-019 (3.24), FR-019a (3.24), FR-019b (3.24). Gates first.

---

## Phase 5: User Story 1 — a message carries a picture somebody else is hosting (P1) 🎯 MVP

**Goal**: FR-MSG-11's P2 half, reaching a socket and a history read.

**Independent test**: send a message with one external-URL attachment, assert a connected
member's socket receives it with the attachment, and assert the history route returns the same
attachment for a client that was not connected.

- [ ] T026 [US1] Return attachments from the send route in `relay-platform/services/api/src/messages/messages.controller.ts` (FR-001 (3.24)), and **spell the field list out** rather than spreading the row — that controller's own comment says why: a new column joins the public response only when somebody decides it should.
- [ ] T027 [US1] Add attachments to the published `message.created` payload in `relay-platform/services/api/src/messages/messages.controller.ts` (FR-008 (3.24), FR-022 (3.24)), **always an array and `[]` when there are none** — T014 makes the field required, so the compiler names this site if it is missed.
- [ ] T027a [US1] Add attachments to the gateway's published `message.created` payload at `relay-platform/services/gateway/src/session.ts:1535` (FR-008 (3.24), FR-022 (3.24)) — the socket twin of T027, `attachments: committed.attachments`. That payload spells out six fields (`id, channel, seq, user, text, created_at`) and `services/gateway/src/fanout.ts:51` types the argument as `Message`, so T014 makes the compiler name the site — **and T014a will already have filled it with an empty array**, which compiles, delivers, and is wrong. T022a threads the *inbound* destructure 23 lines above this and stops there.
- [ ] T028 [US1] Add attachments to `listMessages`'s column list in `relay-platform/services/api/src/db/repository.ts` (FR-009 (3.24)), mapping `NULL` to `[]` (FR-007 (3.24)). **`?? []` in the map, not in the caller** — chapter 3.23 shipped a control test that was green before its field existed because an absent key and a null one read the same through `??`.
- [ ] T028a [US1] Add attachments to the payload the gateway BUILDS after a socket send, at `relay-platform/services/gateway/src/session.ts:1534` (FR-008 (3.24)). **The api constructs the fan-out payload for a REST send and the gateway constructs it for a socket send** — two builders for one frame, and T027 only covers the first. A message sent over a socket would otherwise reach every member with its attachments missing.
- [ ] T028b [US1] Write the socket-delivery test in `relay-platform/services/gateway/src/session.itest.ts` (FR-008 (3.24), SC-001 (3.24)): a message sent over one member's socket reaches another member's socket **with its attachments, in order** (FR-006 (3.24)). The REST delivery test at T030 cannot see this path.
- [ ] T028c [US1] Falsify T028b and T030: replace the attachments on the gateway's publish payload at `relay-platform/services/gateway/src/session.ts:1535` with `[]`, watch both go red, and put it back. **This is the only falsification in the chapter aimed at a payload rather than a rule**, and it is the one that answers the question the other three cannot: a field that is present and empty compiles, parses, delivers, and satisfies every assertion written about its key.
- [ ] T029 [US1] Write the route test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-001 (3.24), FR-006 (3.24), FR-009 (3.24), SC-001 (3.24)): send with **two** attachments, read them back through the history route, and assert both kinds and both URLs **in the order they were sent**. **One attachment cannot see an order**, which is T052's argument about its own design and applies here identically. This is FR-006 (3.24)'s only assertion on the REST history path.
- [ ] T030 [US1] Write the **REST-send** delivery test in `relay-platform/services/gateway/src/session.itest.ts` (FR-008 (3.24), SC-001 (3.24)): a message sent **over REST** with **two** attachments reaches a connected member as `message.created`, and the frame's list equals what the history route returns for the same message — **compared as ordered lists**. SC-001 (3.24) is a claim that two readers agree, so a test watching one of them proves half of it; this is the only task positioned to compare both. **Two members and a count, not a first match** — a `waitFor` that resolves on the first match cannot see a duplicate.

  **The door is named because it stopped being obvious.** When this task was written there was one door; analysis pass 1 added the socket path and T028b, and "the delivery test" then described two tasks in the same file citing the same requirement and criterion. A reader could have written the same test twice.
- [ ] T029a [US1] Write the socket-ack test in `relay-platform/services/gateway/src/session.itest.ts` (FR-008 (3.24)): a socket sender's `message.ack` carries **only `seq`**, and the sender learns its attachments landed from the `message.created` frame the fan-out delivers to it like any other member. **Assert the ack's exact key set**, so a later chapter widening `messageAckSchema` has to change this test on purpose.

  **The spec's first draft asked for the ack to carry the attachments** and did not say which door it meant. `messageAckSchema`'s payload has been `{ seq }` since chapter 2.2; widening it is a protocol change no requirement asks for. The scenario was narrowed and this test is what keeps the narrowing honest rather than quiet.
- [ ] T030a [US1] Write the both-branches test in `relay-platform/services/api/src/db/repository.itest.ts` (FR-006 (3.24), FR-009 (3.24)): `listMessages` is a **ternary over two separate queries** — one ordered `desc` for a backward page, one `asc` for a forward one — and attachments must come back in order from **both**. Assert them in one labelled loop, the way chapter 3.23's tombstone test does.

  **Without this the two branches are covered by accident.** T029 takes the backward branch and T052 the forward one, and nothing says so — so a change to either test silently drops a branch. That chapter recorded the exact failure: adding a predicate to the forward branch alone left the suite green, because the test that should have caught it called the function with no cursor.
- [ ] T031 [US1] Write the empty-list test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-007 (3.24)): a message sent without attachments reads back with `attachments: []`, asserted with `toHaveProperty("attachments", [])` so an **absent** field fails. The `??` trap again, in the shape that already caught this project once.
- [ ] T032 [US1] Falsify the empty-list mapping: remove the `?? []` from `listMessages` in `relay-platform/services/api/src/db/repository.ts`, watch the empty-list test in `relay-platform/services/api/src/messages/messages.itest.ts` go red, and put it back.
- [ ] T032a [US1] Write the isolation test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-014 (3.24)): a non-member of a private channel reading its history receives **no message and therefore no attachment**, and the answer is byte-identical to a channel that does not exist. **State plainly what this test does NOT prove.** The attachment adds no second surface **by construction, not by assertion**: `channelVisibleTo` runs as a gate BEFORE the read — `messages.service.ts:208`, argued at `:178` as "THE VISIBILITY CHECK FIRST, AND IT IS THE SAME ONE `history` uses" — the refusal is a 404, and no attachment column ever enters the path. Both halves of the pair return no message, so the assertion holds whatever attachments do. **Chapter 3.23's falsification is the evidence against this shape, not for it**: it proved that removing `channelVisibleTo` from the edit path left the foreign-versus-missing pair green. Keep the test — it guards the byte-identical answer, which is chapter 3.15's property and worth a regression — and do not credit it with the attachment claim.
- [ ] T032b [US1] **Falsify T032a and expect it to STAY GREEN.** Remove attachments from `listMessages`'s column list in `relay-platform/services/api/src/db/repository.ts`, run T032a, and record in `specs/042-chapter-3-24/baseline.txt` that it passed anyway. **A green falsification is a finding, not a formality** — chapter 3.23 spent a phase on one and wrote down why: it is the only thing that distinguishes a test that guards a property from a test that cannot fail for the reason it was written. Then put the column back. **If it goes red, this task's premise is wrong** and the attachment reaches a surface the gate does not cover, which is a larger finding than the test.
- [ ] T033 [US1] Write the outsider test in `relay-platform/packages/outsider/src/integrate.itest.ts` (SC-001 (3.24)): send a message with **two** attachments over REST as a customer would, and assert a member's socket hears them **in order**. **This is the only instrument that boots the shipped binary**, and chapter 3.23's plan scheduled an audit over this file without any task writing to it. **Rebuild the compose images with `--build`** before believing a field is missing.
- [ ] T034 [US1] Commit phase 5 in `relay-platform`, naming FR-001 (3.24), FR-007 (3.24), FR-008 (3.24), FR-009 (3.24), SC-001 (3.24). Gates first.

**Checkpoint**: a message carries a picture and everyone watching sees it. This is the MVP.

---

## Phase 6: User Story 2 — ten is a limit and eleven is a refusal (P1)

**Goal**: FR-MSG-11's bound, enforced at the boundary like every other list bound here.

**Independent test**: send eleven attachments, assert the refusal names the field and the
bound, and assert no message row was written.

- [ ] T035 [US2] Write the over-the-bound test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-005 (3.24), SC-002 (3.24)): eleven attachments are refused with `invalid_request` and a `field` of **`attachments`** — the bound is on the array, not on an item — **and `channels.last_sequence` is unchanged afterwards**. The second half is the assertion — a 400 raised after the write passes the first — and the column is the one chapter 2.2 made the sequencing authority, which is what the acceptance scenario names. A row count is a weaker claim about a different thing.
- [ ] T036 [US2] Write the exactly-ten test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-005 (3.24)): ten succeed and all ten come back. A bound tested only from above is a bound that could be nine.
- [ ] T036a [US2] Write the duplicate-URL test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-021 (3.24)): the same URL attached twice to one message is stored twice and returned twice. **The spec asked this as an open question and it was answered rather than left** — nothing deduplicates, for the reason chapter 3.23 gave about comparing texts: every definition of sameness is a decision a customer would have to be told about.
- [ ] T037 [US2] Write the bad-kind test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-002 (3.24)): a kind outside the three is refused rather than stored.
- [ ] T038 [US2] Write the scheme tests in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-004 (3.24), SC-004 (3.24)): `javascript:`, `data:`, `file:` and `vbscript:` are each refused **through the route**, not only at the schema. A schema test proves the rule exists; only a route test proves it fires.

  **Assert the `field`, and put the bad one at index 3** so the path is not `attachments.0`. EIR-API-04 makes `field` the thing an integrator acts on, and a caller sending ten attachments needs to know which one — `attachments.3.url` and `attachments.3.kind` are different repairs. **Decide the shape and pin it**: zod's path is an array and whatever joins it is this chapter's choice, made once here rather than per call site.
- [ ] T039 [US2] Add the `media_not_available` refusal for a `{"type": "media"}` attachment (FR-003 (3.24), FR-003a (3.24)): a new error code in `relay-platform/packages/protocol/src/codes.ts` with the argument for its own code written at the entry, and the pinned count in `codes.test.ts` moved. **Compare the measured number of pinned places against T007's prediction and record both.** **And name what the socket cannot do.** `sendError` fixes its code at the call site, so the REST door answers `media_not_available` and the socket answers `invalid_frame` carrying T009's message. That is T041's pattern — two doors, two codes, one rule — and it belongs on the record here rather than in whoever's head first notices.

  **THROW IT WITH `protocolError`, NOT WITH A NEST EXCEPTION**, in `relay-platform/services/api/src/messages/messages.service.ts`:

      protocolError("media_not_available", "…", HttpStatus.UNPROCESSABLE_ENTITY)

  Registering a code is not the same as putting it on the wire. `ProtocolErrorFilter`'s ladder covers **400, 401, 403 and 404 only** — everything else falls to `internal_error` — and a code survives only when the thrower names it. `throw new UnprocessableEntityException("…")` here ships **`code: "internal_error"` with a 422 status** and a `docs_url` pointing at `#internal_error`, which is the lie chapter 2.2 fixed for 400, chapter 3.2 for 403 and chapter 3.10 for 402.
- [ ] T039a [US2] Assert the refusal's **body**, not only its status, in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-003a (3.24)): `code` is `media_not_available` and `docs_url` ends in `#media_not_available`. **A status assertion cannot see this defect** — `webhooks.itest.ts:90` asserts a 422 and its message text, and the five bare 422s behind it have been emitting `internal_error` for four chapters.
- [ ] T040 [US2] Write the media-refusal test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-003a (3.24)): the refusal says hosted media is unavailable rather than that the field is invalid, and its status is 422.
- [ ] T040a [US2] Write the socket media-refusal test in `relay-platform/services/gateway/src/session.itest.ts` (FR-003a (3.24)): a `message.send` frame carrying a `{"type": "media"}` attachment is refused with a message that **says hosted media is not available**, and the code is `invalid_frame` rather than `media_not_available`. **Assert the message, because the code is the same one every malformed frame gets** — this is the only assertion that can tell T009's second arm from a bare discriminator error, and the discriminator error is what a one-arm union produces.
- [ ] T041 [US2] Write the same-bound-on-both-doors test in `relay-platform/services/gateway/src/session.itest.ts` (FR-005 (3.24)): eleven attachments through the socket's `message.send` are refused. **Name the layer and the code the test expects**: the bound is on `messageSendSchema`, so the **gateway** refuses the frame before the api sees it, and the client receives `invalid_frame` rather than the api's `invalid_request`. Two doors, two refusals, one bound — and a test that asserts only "it was refused" cannot tell a working bound from a socket that dropped the field entirely (see T022c). **Assert `field` names the attachments key** once T041a lands: the joined path is what a developer reading their own frame sees.
- [ ] T041a [US2] Give `sendError` an optional `field` in `relay-platform/services/gateway/src/session.ts` and pass zod's joined path at the frame-refusal site (`session.ts:1447`), mirroring `services/api/src/messages/zod-validation.pipe.ts`. **The frame contract has published this key since chapter 1.3** — `packages/protocol/src/frames.ts:182` declares `field` optional — and **no gateway code path has ever set it**. Chapter 3.14 ended that habit for the api and its own comment cites `errorFrameSchema`, the socket's frame, while fixing only the pipe. This chapter asserts a field-level refusal on one door (T020b) and proves the other refuses the same input, so the asymmetry is this chapter's to decide. **Omit the key when the path is empty**, as the pipe does — a top-level refinement like T009's media arm has no path, so this does not rescue T040a.
- [ ] T042 [US2] Commit phase 6 in `relay-platform`, naming FR-002 (3.24), FR-003 (3.24), FR-003a (3.24), FR-004 (3.24), FR-005 (3.24), SC-002 (3.24), SC-004 (3.24). Gates first.

---

## Phase 7: User Story 3 — the moderator, the tombstone, and what an edit leaves alone (P2)

**Goal**: the interaction between attachments and the two mutations chapter 3.23 built.

**Independent test**: send a message with attachments, delete it, and assert the history route
returns the tombstone with an empty attachment list.

- [ ] T043 [US3] Write the tombstone test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-012 (3.24), SC-003 (3.24)): a deleted message is unreachable through **each of the six read shapes `data-model.md`'s table names, one at a time and by name**, and the assertion differs by shape because the shapes do: 

      `listMessages`                      attachments: []      history AND resume
      `getMessageByIdempotencyKey`        attachments: []      the retry replay
      `editMessage`'s internal read       field absent
      `deleteMessage`'s internal read     field absent
      `listMessagesRaw`                   field absent         test-only, five call sites
      `listChannelsForUser.last_message`  field absent         the preview

  **`listMessages` serves history AND resume** — `data-model.md` annotates it "(history, resume)" — so those are one shape and not two, and the resume backfill's own mapping in `relay-platform/services/api/src/internal/backfill.controller.ts` is a **seventh assertion worth making and not one of the six**: `toFrame` maps a row it is handed rather than reading. **Four of the six carry no attachments column and this chapter does not add one**, so `[]` is the wrong assertion for them and absence is the right one — which is what T053 asserts for the preview, and the two tasks must not disagree. **Six is the number this chapter's research took from the code**: a seventh READ SHAPE appearing is the finding.
- [ ] T044 [US3] Write the deletion-event test in `relay-platform/services/gateway/src/session.itest.ts` (FR-013 (3.24)): the `message.deleted` frame carries no attachment field at all, asserted as an exact key set rather than as `payload.attachments === undefined`.
- [ ] T045 [US3] Write the edit test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-016 (3.24)): editing a message's text leaves its attachments unchanged, in order. **The failure this catches is silent** — an `UPDATE … SET text = ?, attachments = ?` written without care drops the photograph and returns 200.
- [ ] T046 [US3] Falsify T045: add `attachments` to `editMessage`'s `SET` list in `relay-platform/services/api/src/db/repository.ts`, watch T045 go red, and take it out.
- [ ] T046a [US3] Add attachments to the edit route's **two** payloads in `relay-platform/services/api/src/messages/messages.controller.ts` (FR-015 (3.24), FR-022 (3.24)): the published `message.updated` at `:335` and the 200 response at `:356`, both carrying the message's current attachments, which an edit does not change (T045). FR-015 (3.24) names the edit event and T055 covers only its outbox half; these are the fanout and REST halves. **T014a fills both with an empty array in phase 3**, so nothing is red before this task and nothing after it unless T046b exists.
- [ ] T046b [US3] Write the edit-event test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-015 (3.24)): an edit to a message with two attachments publishes a `message.updated` whose payload carries **the same two, in order**, and returns them on the 200. T045 asserts the database kept them; this asserts the wire reports them. **Neither assertion implies the other** — an empty array on the payload passes T045 and fails this.
- [ ] T047 [US3] Write the edit-history test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-016 (3.24)): `message_edits` gains no attachment column and the edit-history route says nothing about attachments. Chapter 3.23 built that table to the SAD's published DDL; **this chapter does not add to it**, and the test is what stops a later reader assuming it did.
- [ ] T048 [US3] Commit phase 7 in `relay-platform`, naming FR-012 (3.24), FR-013 (3.24), FR-016 (3.24), SC-003 (3.24). Gates first.

---

## Phase 8: The read paths

**Six shapes, and research R4 says only two of them change.** Naming the four that do not is
what stops a later reader treating an omission as a bug.

- [ ] T049 Confirm `getMessageByIdempotencyKey` carries attachments in `relay-platform/services/api/src/db/repository.ts` (FR-011 (3.24)) — **the select change moved to T015b in phase 3**, because `internalSendResponseSchema`'s required field feeds off this read by spread and could not wait five phases. What remains here is the check and the record: **that read already omits `user`, which the others carry** — a pre-existing difference this chapter records and does not fix.
- [ ] T050 Write the idempotent-retry test in `relay-platform/services/api/src/messages/idempotency.itest.ts` (FR-011 (3.24)): a repeated send with the same key returns the original message's attachments and **writes no second row**, read from the database rather than from the response.
- [ ] T051 Add attachments to the resume backfill's mapping in `relay-platform/services/api/src/internal/backfill.controller.ts` (FR-010 (3.24)). Type the column with `sql<Attachment[] | null>` here as well — this is the third and last unchecked assertion `data-model.md` counts.
- [ ] T052 Write the resume test in `relay-platform/services/api/src/internal/backfill.itest.ts` (FR-010 (3.24), SC-005 (3.24)): a client away across a send with **two** attachments receives them in the replay **in the order they were sent** (FR-006 (3.24)). FR-006 (3.24) says order holds on every path that returns a message, and a single-attachment test cannot see an order at all. **That file is where chapter 3.23's US4 tests live**, because `services/gateway/src/resume.itest.ts` boots against a stubbed api and has no rows.
- [ ] T053 Record in `specs/042-chapter-3-24/baseline.txt` the four read shapes that do **not** change and why: `listChannelsForUser.last_message` (a preview shows what was said), `listMessagesRaw` (a test-only helper, five call sites), and the two internal reads inside `editMessage` and `deleteMessage`. **Then assert it** in `relay-platform/services/api/src/db/repository.itest.ts`: the channel listing's preview carries no attachments field. **A record says "decided"; only an assertion tells the next reader that from "forgotten"** — and this chapter's own predecessor left four sentences that had stopped being true because nothing compared them with the code. **This is the same claim T043 makes for four of its six**, and the two must agree: absence, not an empty list, on the shapes that never carried the column.
- [ ] T050a Write the recovered-tombstone test in `relay-platform/services/api/src/messages/idempotency.itest.ts` (FR-011 (3.24), FR-012 (3.24)): a send that recovers a **tombstone** through an old idempotency key returns `attachments: []`, and **publishes nothing** — the two guards at `messages.controller.ts:234` and `session.ts:1533` both read `text !== null`.

  **This chapter changes what a non-null text means**, so those two lines now hold for a reason they were not written for: an attachments-only message carries `""`, which is not null, and a tombstone carries null. The guards are right and nothing asserts it. The spec names this in Edge Cases and, until now, no task did.
- [ ] T054 Commit phase 8 in `relay-platform`, naming FR-010 (3.24), FR-011 (3.24), FR-012 (3.24), SC-005 (3.24). Gates first.

---

## Phase 9: The events

- [ ] T055 Add attachments to `MessageCreatedData` in `relay-platform/services/api/src/outbox/event.ts`. **This lands on `message.created` AND `message.updated` at once** — FR-015 (3.24) requires the creation and edit payloads to carry attachments identically — and on neither `message.deleted` nor the membership events. **The authority here was wrong for eleven passes**: this cited `FR-008a` suffixed to this chapter, which declares no such id — writing the suffixed form here would trip the very check that found it. It is chapter 3.23's, and it reads "MUST be left unchanged" — that chapter promising not to touch this payload, which this chapter deliberately does.
- [ ] T056 Update the consumer-side union branches in the same file for both types, and the pinned key-set assertions in `relay-platform/services/api/src/outbox/event.test.ts`. **`consumer/runtime.ts` answers a failed parse with `message.term()`**, which stops redelivery for good, so a branch not widened is a row destroyed at the consumer — and the lane cannot see it, because it runs `RELAY_EVENT_CONSUMER=off`.
- [ ] T057 [P] Write the payload tests in `relay-platform/services/api/src/outbox/event.test.ts` (FR-006 (3.24), FR-015 (3.24)): the creation and edit payloads carry attachments **identically**, compared as key sets, and the deletion payload has no such key. **Then assert the values too, with two attachments in order.** Key sets answer FR-015 (3.24) — one shape for both — and cannot answer FR-006 (3.24), which holds on every path that returns a message and this is one. Two payloads both carrying `[]` have identical key sets.
- [ ] T058 [P] Record in `specs/042-chapter-3-24/baseline.txt` that §4.14's `attachment_count UInt8` is Part 4's and unbuilt, and that nothing is owed here beyond the array having a length. **This task verifies nothing and no longer claims to** — FR-017 (3.24) is carried by T023, whose round-trip assertion is what makes a count derivable. A record task citing a requirement is the shape `check-refs.py` refuses for commits, and it is the same mistake one step to the left.
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

  **NINE FILES JOIN THE FENCE COLUMN AND NONE OF THEM IS TAUGHT**, because making the frame's field required means every construction the compiler types must set it. Measured, not listed from memory — the same probe as T014a, after the build:

        14  services/api/src/fanout/publisher.test.ts        fenced by nobody
         4  services/gateway/src/connections.itest.ts
         3  services/gateway/src/session.itest.ts
         2  services/gateway/src/resume.test.ts
         1  services/gateway/src/session.test.ts
         1  services/gateway/src/resume.itest.ts
         1  services/gateway/src/presence.itest.ts
         1  services/gateway/src/fanout.itest.ts
         1  services/api/src/fanout/fanout.itest.ts          fenced by nobody

  **This list was wrong in both directions until analysis pass 18 measured it.** It claimed `isolation.itest.ts` and `typing.itest.ts`, which the compiler does not name, and missed `publisher.test.ts` — 14 of the 32 errors, the largest single file — along with `presence.itest.ts` and `session.itest.ts`. **28 literals across nine files**, where analysis pass 4 costed it at eighteen across eight.
  **That is a cost of the required-field decision that no earlier pass counted, and the two passes that tried both got it wrong.** Chapter 3.23 recorded the same shape from the other side: fencing a file a chapter does not discuss adds lines the chapter never explains, and it declined to fence three for exactly that reason. **Seven of these nine have no such choice**: their chains exist, so a changed line must appear or `check:fences` goes red. The two marked *fenced by nobody* stay that way.
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

  **AND SAY THAT THIS CHAPTER ENLARGES A KNOWN CONSTITUTION GAP BY ONE BRANCH.** Constitution VI requires 100% branch coverage for **message ordering, idempotency and tenant isolation**. `services/api/src/db/repository.ts` holds all three and is pinned at **92**, deliberately — that config's own comment says the per-file numbers *"are deliberately not the 100% the constitution asks for, because a threshold nothing can pass"* is worse than a ratchet. This chapter adds an idempotency branch (the retry replay's attachments, FR-011 (3.24)). **The gap is older than this chapter and is one branch larger because of it**, which is a sentence in the record rather than a number to chase.
- [ ] T081 If any arm of `relay-platform/services/api/src/db/repository.ts`, `relay-platform/services/api/src/messages/messages.schema.ts`, `relay-platform/services/api/src/messages/messages.controller.ts` or `relay-platform/packages/protocol/src/attachments.ts` is uncovered, ask whether the code should be **deleted** before asking for a test, and pin the result in `relay-platform/vitest.coverage.config.mts`. The ratchet has removed code five times; chapter 3.23 removed a `?? "unknown"` that was unreachable **and** would have put that word on the wire as somebody's name.
- [ ] T082 [P] Re-derive the files-changed count from `git diff --name-only` and compare it with T068's prediction in `specs/042-chapter-3-24/chapter-notes.md`. A first count is expected to be wrong; chapter 3.23's moved from 36 to 37 during close-out.
- [ ] T083 [P] Re-derive `specs/042-chapter-3-24/traceability.md` against the shipped tree, both directions, checking **every quoted test title as an exact string** rather than by eye.
- [ ] T084 Run the credential scan over the chapter's diff and record the patterns searched and every hit classified in `specs/042-chapter-3-24/baseline.txt`. **Widen each pattern past the examples in front of you**, and expect the scan to match its own paragraph — chapter 3.23's did.
- [ ] T085 Complete `specs/042-chapter-3-24/gaps.md`, carrying chapter 3.23's items with their status **re-checked against the tree rather than copied**. Its item 9 is addressed to whoever next finds the unit lane red with no containers, and its C6 — nine files that discard their child's output — is the reason that chapter's two battery failures have no cause. **Add three found during specification and analysis**: `avatar_url` accepting `javascript:` (research R7), found by running the validator rather than reading it; `messageSendSchema.payload.text` carrying no bound at all while the other two doors bound it 1 to 8,000, found by comparing the three schemas rather than reading one; and **five bare 422s in `relay-platform/services/api/src/webhooks/webhooks.service.ts` at lines 88, 193, 196, 202 and 210** that name no code, so every one emits `code: "internal_error"` with a `docs_url` pointing at `#internal_error` — measured against the filter's ladder, not inferred. `webhooks.itest.ts:90` asserts the status and the message text, so nothing catches it. **Not this chapter's file**; the fix is `protocolError` at five call sites and one new code. **And C8, which this chapter made worse in a way no other task records.** That item tracks per-chapter instruments with no owner; the predecessor carried three files and called it open for the fifth chapter. This feature carries **six** — one added while planning and two more during analysis — so the copy-forward is now twice the size, and against the predecessor's copies `check-refs.py` differs by 50 lines, `sweep.py` by 2, and `check-prose.py` by 108. The recommendation there — a shared directory with per-feature configuration, or accept the re-derivation — was not taken, and choosing the second option silently is what needs recording. **Re-measure C8's own count while re-checking it**: it says "a fourth instrument" and "all four were improved", then lists three, and the predecessor's tree holds three.
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
different file, and this chapter's work concentrates in five. **Measured at analysis pass 20,
after analysis grew the list by twenty-five entries** — with the command, because a count without one has
been wrong every time in this feature:

    grep -oE '^- \[[ X]\] T[0-9]+[a-z]? ' tasks.md   # then group by the file paths on each line

        tasks  spanning  file
           17         5  services/api/src/messages/messages.itest.ts
            9         5  services/gateway/src/session.itest.ts
            8         6  services/api/src/db/repository.ts
            6         5  services/api/src/messages/messages.controller.ts
            6         5  services/api/src/db/repository.itest.ts
            3         1  services/api/src/outbox/event.test.ts
            1         1  services/api/src/outbox/event.ts

Every one of those runs in sequence. **The previous version of this paragraph said four files
and got all five of its numbers wrong** — eleven, four, five, two and two. Four were understated,
which task growth explains; `event.ts` was OVERSTATED, two against one, and growth cannot lower
a count. And `session.itest.ts`, the second-heaviest file here, was not in the list at all, so a
reader planning from this section would have scheduled nine tasks across five phases as parallel
work.

**What genuinely parallelises — all 17 `[P]` markers, not the twelve this paragraph used to
name.** T002, T003 and T007 in Phase 1; T010 in Phase 2; T015 and T016 in Phase 3; T023 in
Phase 4; T057 and T058 in Phase 9; T062 through T065 in Phase 10, four different documents;
T071 and T075 in Phase 11, the figures and their mirror; T082 and T083 in Phase 12, two
different records.

**T037 and T038 are NOT among them**, and the old version of this paragraph listed them here
before withdrawing them two clauses later. They carry no `[P]`, both edit
`relay-platform/services/api/src/messages/messages.itest.ts`, and they run in sequence. The
correction below is where they belong.

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
