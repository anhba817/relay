# Tasks — chapter 3.23, editing and deleting a message

**Spec**: [spec.md](./spec.md) · **Plan**: [plan.md](./plan.md) · **Research**: [research.md](./research.md) · **Contract**: [contracts/edit-and-delete.md](./contracts/edit-and-delete.md)

**EVERY PHASE RUNS `pnpm lint`, `pnpm typecheck` AND `pnpm turbo run test` IN
`relay-platform` BEFORE ITS COMMIT**, from the repository root and not from a package
subdirectory — `pnpm turbo run test` from `services/gateway/src` ran 4 tasks of 11 and printed
green, which is the one failure in that family that is silent.

**THE READER TEST COMES BEFORE THE WRITER, AND THAT IS PHASE 1.** The spec chose Slack's model
for resume: a client repairs a stale message by re-reading history. That works only because
the REST history route returns tombstones and edited text unchanged — which research R5
established **by inspection and by no test at all**. Chapter 3.15 wrote exactly this test for
the channel *listing* and said why: *"so the day FR-MSG-08's chapter ships, the count and the
preview already agree."* History never got one. **If T009 is red, the spec's resume decision
is wrong and the plan changes rather than the code.**

**EVERY REQUIREMENT ID THIS CHAPTER WRITES INTO CODE NAMES ITS CHAPTER.** Write
`FR-011 (3.23)`, or spell the requirement. The ids are per feature and the files are shared:
`messages.controller.ts` already carries FR-002 and FR-003 meaning chapter 3.15's visibility
rules, and this chapter's FR-002 is an edit preserving a sequence number. Chapter 3.22 found
ten such collisions in one file and this one starts by assuming there are more.

**THE FALSIFICATION COMES BEFORE THE TEST, EVERY TIME.** Chapter 3.20 specified two orderings
as requirements and neither was observable. Chapter 3.22 found that a falsification can only
see the tests that already exist — replacing `SET NX` with a check-then-act left sixteen tests
green and the seventeenth caught it every run. Tasks below that say "break X, watch this test
go red, put X back" are not steps inside a task; they are the task.

**AND THIS CHAPTER EXPECTS NO ADR.** `docs/05-sad.md` publishes the deletion's shape at :342
and the `message_edits` DDL at :435, and `schema.ts:26` names that table as an absence
awaiting *"the edit chapter"*. **If an ADR turns out to be necessary, something in the plan is
wrong** — stop and find out what rather than writing one.

**Eleven phases, and `plan.md` lists the same eleven.** Chapter 3.21 left its plan saying
something else and made a reader hold the correction in their head.

---

## Phase 1: Setup, the premises, and the reader test that must pass first

- [X] T001 Copy `specs/040-chapter-3-22/check-refs.py` to `specs/041-chapter-3-23/check-refs.py` and re-point its paths. **The per-chapter copy is a decision, not a default** — chapter 3.22's `gaps.md` item 8 recorded it for the fourth chapter running, and its one argument is that an instrument can be changed mid-chapter without breaking another chapter's record. That chapter changed it twice.
- [X] T001b Improve the checklist-format message in `specs/041-chapter-3-23/check-refs.py` to name the id grammar. **Analysis pass 7's finding was wrong and this task records the correction**: it claimed a malformed id like `T033c1` would slip past the checker with "ids sequential" printed. It does not — `TASK.match` fails, the format problem is appended, and the line `continue`s before the id list is built, so the run fails either way. A rule iterating that id list could never see such an id; it was written, tested, found to be dead code, and **removed rather than covered**. What was kept is the message, which now names `- [ ] Tnnn` / `- [ ] Tnnna` instead of saying only that the format is wrong.
- [X] T001a Extend the copied `specs/041-chapter-3-23/check-refs.py` with a rule the four analysis passes needed and did not have: **every requirement and criterion in `spec.md` must be cited by at least one task that is not a commit task.** Test it red three ways. **The check those passes actually ran counted a commit-task citation as coverage**, reported 100% four times, and hid three criteria — SC-002 (3.23), SC-004 (3.23) and SC-006a (3.23) — one of which had no surface at all. Chapter 3.22's `gaps.md` item 8 argued the per-chapter copy earns its keep because an instrument can be improved mid-chapter; this is that argument being cashed.
- [X] T002 [P] Copy `specs/040-chapter-3-22/sweep.py` to `specs/041-chapter-3-23/sweep.py` and re-point it at this chapter's counts.
- [X] T002a Widen `specs/041-chapter-3-23/sweep.py`'s id patterns when it is copied. Its success-criteria extractor is `\*\*(SC-\d+)\*\*:` with **no optional letter**, so it counted 11 where `spec.md` has 13 — `SC-002a` and `SC-006a` were invisible and the wrong number printed as a fact. **Check the FR pattern for the same hole**, and widen the plan-phase extractor only if the plan is the thing that is right. This is chapter 3.21's `check-refs.py` widening (`T\d{3}` → `T\d{3}[a-z]?`) in a second instrument, and that one surfaced six live citations in one run.
- [X] T003 [P] Write `specs/041-chapter-3-23/check-prose.py` listing the published sentences this chapter falsifies, and leave it **RED**. **Include `messages.controller.ts:89`'s claim** — see T029a — because it is a sentence that stopped being true and no gate reads prose. **And include chapter 3.22's `baseline.txt` sentence *"Thirty-seven new tests read one at a time"***, which that chapter corrected to forty in its other record and left standing in this one (chapter 3.23's `gaps.md` item 5). Chapter 3.22's went green only at its final gate, when it caught a claim corrected in one half and left standing in the other.
- [X] T004 Record the lane environment in `specs/041-chapter-3-23/baseline.txt` — the nine variables and the compose line from `quickstart.md`. Chapter 3.22 spent two full lane runs learning they apply to `pnpm coverage` as well as `test:integration`.
- [X] T005 Verify premise P1 in `specs/041-chapter-3-23/baseline.txt`: `grep -n "text" services/api/src/db/repository.ts` around `listMessages` returns **no predicate on `messages.text`**, and `messages.service.ts` maps rows straight through. Record the line numbers, not the conclusion.
- [X] T006 [P] Verify premise P2: `grep -c "z.string()" packages/protocol/src/frames.ts` and read `messageSchema.text`. Record that it is **not** nullable and that two comments already say so — `messages.controller.ts:194` and `backfill.controller.ts:83`.
- [X] T007 [P] Verify premise P3: `grep -n "OUTBOX_EVENT_TYPES" -r services packages --include=*.ts` and count the pinned places. **Predicted four.** Chapter 3.22 predicted two for one close code and found four.
- [X] T008 [P] Verify premise P4: `grep -rn "message_edits" relay-platform` returns **only** `schema.ts:26`'s absence note, and `docs/05-sad.md:435` holds the DDL. If a table already exists somewhere, the plan is wrong.
- [X] T009 Write the history-tombstone test in `relay-platform/services/api/src/db/repository.itest.ts` (FR-011 (3.23), SC-003 (3.23)): plant a tombstone with raw SQL as that suite already does for the listing, read the channel's history, and assert the message returns in its original position with a null text and unbroken positions either side. **This runs against unchanged code and must pass.**
- [X] T010 Falsify T009 before trusting it: add `AND text IS NOT NULL` to the history query in `relay-platform/services/api/src/db/repository.ts`, watch T009 go red, and put it back. A reader test that cannot fail is a reader test that proves the reader was never checked.
- [X] T011 Build `specs/041-chapter-3-23/traceability.md` **now, both directions**, mapping **every** requirement and criterion in `spec.md` against the phases below — read the counts from the file rather than writing a literal here, because two analysis passes added requirements after this task was written. Chapter 3.18 ran this only at close-out and found a MUST with no test after eight phases; chapter 3.22 ran it during planning and found two orphans before a line of code existed.
- [X] T012 Commit phase 1 in `relay-platform` and `relay` — the reader test and the records. Gates first.

**Checkpoint**: history is proven to carry tombstones before anything writes one.

---

## Phase 2: The protocol — the one schema this chapter changes

- [X] T013 Give `message.deleted` its own payload in `relay-platform/packages/protocol/src/frames.ts` (FR-008 (3.23)): `id`, `channel`, `seq`, `user`, `deleted_at`, and **no `text` field**. Leave `messageSchema` untouched — it is published since chapter 1.3 and `message.created` and `message.updated` keep it (FR-008a (3.23)).
- [X] T014 Count the pinned places in `relay-platform/packages/protocol/src/frames.test.ts` **before editing it** and write the number into `specs/041-chapter-3-23/baseline.txt`. **The `valid` fixture table at :30 is the one that breaks** — it maps `message.deleted` to the shared `message` object, which stops being a valid example the moment the payload changes. The union's exact-count and exact-set assertions at :148-152 do **not** move, because the union's membership is unchanged, and the first draft of this task named those two and missed the fixture.
- [X] T015 Update those places in `relay-platform/packages/protocol/src/frames.test.ts` and assert the deleted payload's exact key set, the way `codes.test.ts` asserts an exact close-code set — which is what makes a payload change a decision rather than an accident.
- [X] T016 Write the tombstone-cannot-fit test in `relay-platform/packages/protocol/src/frames.test.ts`: `messageSchema` refuses a row with `text: null`, and `messageDeletedSchema` accepts the same row's identity without one. **This is quickstart P2 as an assertion** and it is the reason the payload changed.
- [X] T017 Re-measure the pinned places actually touched and compare with T014's number in `specs/041-chapter-3-23/baseline.txt`. Record both, whichever way it goes.
- [X] T017a Add `not_message_author` to `ERROR_CODES` in `relay-platform/packages/protocol/src/codes.ts` (FR-022 (3.23)), with a comment naming why the generic 403 is wrong here: authorship is a fact about the message and no credential grants it, so that code's published remedy — *a change of credential or of permission* — is advice nobody can act on. `codes.ts` makes this argument twice already, for `wrong_credential_type` and `wrong_credential_service`.
- [X] T017b Update every pinned place the new code moves in `relay-platform/packages/protocol/src/codes.test.ts` — the exact-set assertion and the count. **Chapter 3.22's one close code moved four pinned places and the task that specified it found two**; count them before editing and record the number.
- [X] T017c Note in `specs/041-chapter-3-23/baseline.txt` that `check:errors` is now **RED on purpose** until the reference section lands in Phase 10, and that it reads the built `dist` so a stale build makes it green for the wrong reason. Chapter 3.22 ran the same deliberate red from its Phase 3 to its Phase 9.
- [X] T018 Commit phase 2 in `relay-platform`, naming FR-008 (3.23), FR-008a (3.23). Gates first.

---

## Phase 3: The fabric, and the fifth subject grammar

**ADDED BY ANALYSIS PASS 1, AND THE PLAN'S OWN DETECTOR IS WHAT FOUND IT.** The first draft
had eleven phases and said no ADR was expected. `chan:{channel_id}` carries a `Message` —
`packages/protocol/src/fanout.ts:18` says so in its own words — and
`services/gateway/src/session.ts:347` stamps every arrival `message.created` at the call
site. **A deletion is not a `Message` and cannot ride that subject at all; an edit is one and
cannot be told apart from a creation on it.** This repository's rule, reached independently
by three chapters: a kind that cannot share a payload type cannot share a subject.

**This phase blocks US1 and US2.** Neither frame reaches a socket without it.

- [X] T018a Re-count the message fabric's typed points and write the numbers into `specs/041-chapter-3-23/baseline.txt` before changing anything. Research R13 measured 1 in `packages/protocol/src/fanout.ts`, 3 in `services/api/src/fanout/publisher.ts`, 7 in `services/gateway/src/fanout.ts` and 4 in `services/gateway/src/session.ts`. **ADR-19's record said three typed points and a re-derivation found eight over seven places** — carry nothing.
- [X] T018b Decide the grammar and record the decision in `specs/041-chapter-3-23/research.md`: one subject carrying both mutations with a discriminator in the payload, following ADR-20's `membership.changed` and its `change: "added" | "removed"`, **or** two subjects. Name it beside the four that exist — `chan:`, `member:` (two shapes), `presence:`, `typing:`.
- [X] T018c Add the subject function to `relay-platform/packages/protocol/src/revision.ts` — **a module of its own, not `fanout.ts`**, because `presence.ts`, `typing.ts` and `membership.ts` each declare their own subject function and fabric schema and `fanout.ts` holds `subjectForChannel` and nothing else. Export the prefix too: the gateway subscribes both subjects on one client and has to route on the subject, and a literal in the gateway is a second place that knows the grammar. **`subjectFor` is already taken** by the event spine's `events.{domain}.{action}.{env}`, and the compiler said so the last time two wanted the name.
- [X] T018d Write the subject test in `relay-platform/packages/protocol/src/revision.test.ts` asserting the subject string, the routing predicate's negative cases, and each arm's exact key set, the way `codes.test.ts` asserts an exact set.
- [X] T018e Declare `### ADR-24 — …` in `docs/05-sad.md` following ADR-23's section, with `**Status:** accepted (chapter 3.23) · **Drivers:** D<n>…` and the argument in roughly thirty lines. **An ADR has two homes** and chapter 3.22 tasked only one until its thirteenth analysis pass.
- [X] T018f Write the ADR-24 deep dive in `docs/06-adr-deep-dives.md`, the second half of T018e and not a substitute: drivers, rejected alternatives, reversal condition (Constitution VII). The rejected alternative worth stating is **widening `chan:`'s payload to a discriminated union** — which the three prior grammars each declined for the same reason.
- [X] T018g Update the count in the heading `docs/06-adr-deep-dives.md` reads *"Reading the twenty-three together"*. **A count in a heading is a claim** and `sweep.py` compares it.
- [X] T018h Add the publisher side in `relay-platform/services/api/src/fanout/publisher.ts` and the subscriber side in `relay-platform/services/gateway/src/fanout.ts`, and **stop `relay-platform/services/gateway/src/session.ts:347` deciding the kind at the call site** — the payload carries it now.
- [X] T018i Record the falsifications in `specs/041-chapter-3-23/baseline.txt`. **The premise that they were deferred to T033a stopped being true inside this phase**: T018h added three unit tests to `session.test.ts`, so the distinction became observable two phases early, and seven falsifications ran red for their stated reason. T033a still stands — it falsifies the kind against two sockets and a real Redis, where a shared reference count or a mis-scoped subject would show, and chapter 3.21's inert module passed 1,174 unit tests. **A falsification can only see the tests that exist** — chapter 3.22 concluded a race was unobservable when the test that could see it had not been written. The first draft put the falsification in this phase and its own text said to run it two phases later.
- [X] T018j Commit phase 3 in `relay-platform` and `relay`, naming the new grammar and ADR-24. Gates first.

---

## Phase 4: Foundational — the table the SAD published and nobody built

- [X] T019 Add `message_edits` to `relay-platform/services/api/src/db/schema.ts` **column for column from `docs/05-sad.md:435`**, which is `message_id` referencing `messages(id)`, `edited_at TIMESTAMPTZ NOT NULL`, `prior_text TEXT NOT NULL`, and `PRIMARY KEY (message_id, edited_at)` — **three columns and a composite key, no surrogate `id`**. This task and `data-model.md` both named a fourth column the SAD does not publish and claimed to be quoting it; `members` is the composite-key precedent in the same file. Remove the table's name from the "deliberately absent, with named arrivals" comment at :26 in the same edit, or that comment becomes a lie the moment this lands.
- [X] T020 Generate the migration with drizzle-kit and **review the generated SQL against `docs/05-sad.md` §6.1 before applying it**, which is the discipline ADR-16 names: the schema exists twice and the drift is checked rather than assumed away. **The review is not a formality here** — drizzle-kit's snapshot sits at 0007 while the directory sits at 0013, so it generates a colliding number and replays six tables from migrations it cannot see. Hand-write `0014_message_edits.sql`; chapter 3.23's `gaps.md` item 6 owns the tool.
- [X] T021 Run `relay-platform/services/api/src/db/repository.itest.ts` **and `src/isolation/tenant-scope.itest.ts`** with the nine pinned variables from `specs/041-chapter-3-23/baseline.txt`. The second is the one that executes anything about the new table this phase: it reads `information_schema`, and **it refuses a table it cannot trace to an environment** — `message_edits` is two foreign-key links from one, which the catalogue's one-hop query could not see. **A phase that adds raw SQL must run the suite that executes it** — chapter 3.17 committed two broken tests that typechecked, because a raw `sql` template is just a string.
- [X] T022 Note in `specs/041-chapter-3-23/baseline.txt` that `prior_text` is `NOT NULL` and what follows from it: a deletion writes no edit-history row, which is why FR-010 (3.23) refuses an edit on a tombstone rather than defining what its history would say.
- [X] T023 Commit phase 4 in `relay-platform`. Gates first, and the migration applied.

---

## Phase 5: User Story 1 — an author corrects what they said (P1) 🎯 MVP

**Goal**: FR-MSG-07, and `message.updated`'s first producer.

**Independent test**: send a message, edit it through the route, and assert a second connected member receives `message.updated` with the new text and the original sequence number, and that the prior text is retrievable.

- [X] T024 [US1] Write the failing route test in `relay-platform/services/api/src/messages/messages.itest.ts`: `PATCH /v1/channels/:channelId/messages/:messageId` returns 404 today because the route does not exist. **RED on purpose**, and the phase is done when it is green for the right reason.
- [X] T025 [US1] Add the edit body schema to `relay-platform/services/api/src/messages/messages.schema.ts` — a text, validated the way the send body's is.
- [X] T026 [US1] Add `editMessage` to `relay-platform/services/api/src/db/repository.ts` (FR-001 (3.23), FR-002 (3.23), FR-003 (3.23), FR-004 (3.23)): update the text, set `edited_at`, append one `message_edits` row with the superseded text, **in one transaction**. The sequence number, channel, author and `created_at` are not in the UPDATE's SET list at all.
- [X] T027 [US1] Write the repository test in `relay-platform/services/api/src/db/repository.itest.ts` asserting the sequence number, channel, author and creation timestamp are **unchanged** across an edit (FR-002 (3.23)). A thing-not-done is harder to test than a thing done: assert the values, not the absence of a statement.
- [X] T028 [US1] Write the append-only test in `relay-platform/services/api/src/db/repository.itest.ts` (FR-004 (3.23)): three edits leave three rows, oldest first, and none has been overwritten.
- [X] T029a [US1] Correct the stale comment at `relay-platform/services/api/src/messages/messages.controller.ts:89`. It reads *"`MessagesController` declares no `@Accepts`, so the guard falls back to `EITHER` and a user token is accepted here"* — and line 64 is `@Accepts("application", "user")`. **Chapter 3.17 added the declaration and left the sentence describing its absence**, twenty-five lines apart in the same file, and this chapter edits that file in five tasks. Not this chapter's defect; this chapter is the one with the file open. **There are THREE copies, not one** — `messages.controller.ts:89`, `messages.itest.ts:161` and `repository.ts:3999` — found by grepping the claim rather than the line the task named.
- [X] T028a [US1] **THE PREMISE IS WRONG AND THE TASK IS TO DELETE A GATE.** `relay-platform/services/gateway/src/public-surface.itest.ts:30-32` does not enumerate the public surface — it lists what THAT TEST calls, and this chapter's routes are not on its path, so the sentence was true before and after. Remove the entry from `specs/041-chapter-3-23/check-prose.py` rather than satisfy it: a gate failing on a true sentence is a checker crying wolf, which is how a real problem hides. Add one line to the comment saying the list is the test's own calls, and note that the surface's inventory is `relay-platform/services/api/src/isolation/targets.ts`, derived from the running application.
- [X] T029 [US1] Add `edit` to `relay-platform/services/api/src/messages/messages.service.ts`, resolving the message through the channel's visibility predicate so another tenant's message is a 404 (FR-014 (3.23)) — the same predicate `history` uses, which chapter 3.15 corrected for exactly this.
- [X] T030 [US1] Add the `PATCH` route to `relay-platform/services/api/src/messages/messages.controller.ts` with **`@Accepts("user")` on the method** (FR-013a (3.23)), and refuse a caller who is not the author with 403 (FR-013 (3.23)). **The class declares `@Accepts("application", "user")` at :64, so a route added without a declaration inherits BOTH** — and an application principal has no author to check against. The guard reads `getAllAndOverride`, so a method-level declaration wins; `dev-token.controller.ts:51` is the precedent.

  **The credential class is DECLARED and the authorship is CHECKED, and the split is not arbitrary.** `credential.guard.ts:31` argues the first — *"`@Accepts("platform")` DOES NOT COMPILE, and that is the point"* — and `messages.controller.ts:59` names the alternative as the defect that let the gateway's credential reach `POST /internal/dispatch/replay`. Authorship cannot be declared: it is a fact about a row.
- [X] T031 [US1] Publish `message.updated` from `relay-platform/services/api/src/messages/messages.controller.ts` (FR-005 (3.23)), following the send path's publish at :199. **The double-publish hazard the send path guards against does not exist here** — an edit has one entry path, not two — and research R8 says so, so do not copy the `duplicate` guard without reading it.
- [X] T032 [US1] Confirm the gateway delivers the new kind in `relay-platform/services/gateway/src/session.ts`, and `grep` for how `message.created` reaches a socket rather than assuming a symmetrical path exists. Chapter 3.21 re-derived a count of typed points and found seven where the record said three.
- [X] T033 [US1] Write the delivery test in `relay-platform/services/gateway/src/session.itest.ts` (FR-005 (3.23), SC-001 (3.23)): two connected members, one edit, each receives `message.updated` **exactly once** — a count, not a first match, because a `waitFor` that resolves on the first match cannot see a duplicate.
- [X] T033a [US1] Falsify the discriminator **at the integration seam**: make `relay-platform/services/gateway/src/session.ts` stamp every fabric arrival `message.created` as it did before Phase 3, watch T033 go red, and put it back. Phase 3 already ran this against `session.test.ts`'s stub fanout (F4, `baseline.txt`) — this one runs it against two sockets and a real Redis, which is where a shared reference count or a mis-scoped subject would show. **If nothing goes red here, T033 is not testing the fabric**, only the stub.
- [X] T030a [US1] Declare the edit route in `relay-platform/services/api/src/isolation/targets.ts`: `{ method: "PATCH", path: "/v1/channels/:channelId/messages/:messageId", accepts: "user", shape: "write" }`. **`targets.itest.ts:39` derives the live route table from the adapter and compares it with that hand-maintained list, so it goes red on the build that adds a route** — `CLAUDE.md` records that happening five times over two features and calls it the highest-yield check in the repository. Use the **controller's** parameter names, not the contract's; `targets.ts:197` says so.

  **`accepts` must equal the method's `@Accepts`** (T030). It is the same authorization fact in a second place and **nothing compares the two** — see chapter 3.23's `gaps.md` item 4.
- [X] T033b [US1] Add `listMessageEdits` to `relay-platform/services/api/src/db/repository.ts` (FR-023 (3.23)): a message's edit history, **oldest first**, resolved through the same channel-visibility predicate the other reads use.
- [X] T033c [US1] Add the `GET :messageId/edits` route to `relay-platform/services/api/src/messages/messages.controller.ts` (FR-023 (3.23), FR-023a (3.23)) with **`@Accepts("application")` on the method** — not an `if` in the handler. **Without a declaration it inherits the class's `("application", "user")` and a user token reads what a message used to say**, which is the one thing FR-023a (3.23) exists to forbid. FR-MOD-01 names this audience; nothing in the SRS asks for an end-user surface.
- [X] T033h [US1] Declare the edits route in `relay-platform/services/api/src/isolation/targets.ts`: `{ method: "GET", path: "/v1/channels/:channelId/messages/:messageId/edits", accepts: "application", shape: "read" }`, matching T033c's `@Accepts("application")`.
- [X] T033d [US1] Write the read-route test in `relay-platform/services/api/src/messages/messages.itest.ts` (SC-002 (3.23)): three edits, three prior texts, oldest first, **through the route rather than through the database**. A repository test proves the rows exist; only a route test proves anybody can retrieve them.
- [X] T033e [US1] Write the end-user refusal test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-023a (3.23), SC-002a (3.23)): the author reading their own message's edit history is refused. **That a message was edited is public; what it used to say is not.**
- [X] T033f [US1] Write the empty-history test in `relay-platform/services/api/src/messages/messages.itest.ts`: a message with no edits answers 200 with an empty list, not 404 — the absence of edits is a fact about the message rather than the absence of a resource.
- [X] T033g [US1] Falsify the declaration: remove `@Accepts("application")` from the edits route in `relay-platform/services/api/src/messages/messages.controller.ts`, watch T033e go red — **it should, because the class-level declaration accepts a user token** — and put it back. A declaration nobody has seen bite is a declaration nobody has checked.
- [X] T034 [US1] Write the listing-order test in `relay-platform/services/api/src/db/repository.itest.ts` (FR-015 (3.23)): an edit does not move the channel in the activity ordering.
- [X] T035 [US1] Falsify T034: set `last_activity_at` inside `editMessage` in `relay-platform/services/api/src/db/repository.ts`, watch T034 go red, and take it out.
- [X] T036 [US1] Write the senderless-row test in `relay-platform/services/api/src/db/repository.itest.ts` (FR-018 (3.23)): an edit on a row with a null author is refused. Plant the row with raw SQL — 121,250 of them exist in the lane and none can be created through the API any more.
- [X] T036a [US1] Write the identical-edit test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-021 (3.23)): editing a message to the text it already has records an edit, appends a history row and emits an event. **The platform does not compare texts**, and the spec says why — every definition of equality is a decision a customer would have to be told about.
- [X] T036b [US1] Write the archived-channel and deleted-author test in `relay-platform/services/api/src/db/repository.itest.ts`: a message's edit history survives its channel being archived and its author being deleted, because `message_edits` references the message and both of those keep their rows (FR-USR-05 and the archive's own decision).
- [X] T036c [US1] Write the outsider test in `relay-platform/packages/outsider/src/integrate.itest.ts`: edit a message over REST as a customer would and assert a member's socket hears `message.updated` with the original sequence, exactly once, and **no second `message.created`**. **T090 audits this file and no task wrote to it** — an audit scheduled over work no task did. CLAUDE.md's rule applies one level up: this is the only instrument that boots the shipped binary, and chapter 3.21's worst defect was a module built, awaited and never wired. Rebuild the compose images (`--build`) before believing a 404 from a route added since the last build.
- [X] T037 [US1] Commit phase 5 in `relay-platform`, naming FR-001 (3.23), FR-002 (3.23), FR-003 (3.23), FR-004 (3.23), FR-005 (3.23), FR-013 (3.23), FR-013a (3.23), FR-015 (3.23), FR-018 (3.23), SC-001 (3.23), SC-002 (3.23). Gates first.

**Checkpoint**: an author can correct a message and everyone watching sees it. This is the MVP.

---

## Phase 6: User Story 2 — a message is deleted and the conversation keeps its shape (P1)

**Goal**: FR-MSG-08 and FR-MSG-10, and `message.deleted`'s first producer.

**Independent test**: delete a message, assert a connected member receives `message.deleted`, and assert the row survives with its sequence number and author while history still returns its position.

- [X] T038 [US2] Write the failing route test in `relay-platform/services/api/src/messages/messages.itest.ts`: `DELETE /v1/channels/:channelId/messages/:messageId`. **RED on purpose.**
- [X] T039 [US2] Add `deleteMessage` to `relay-platform/services/api/src/db/repository.ts` (FR-006 (3.23)) as `docs/05-sad.md:342` publishes it: `text = NULL`, `attachments = NULL`, `deleted_at = now()`, everything else untouched.
- [X] T039a [US2] Record the deletion's actor in `relay-platform/services/api/src/db/repository.ts` (FR-006a (3.23)) as `metadata.deleted_by` — the shape is named in `data-model.md` and is `{ kind: "user", user }` or `{ kind: "application" }`, because an application principal has no user of its own. `messages.metadata` is `jsonb NOT NULL DEFAULT '{}'` and needs **no migration**, and **this chapter is its first writer anywhere in the platform**. FR-MSG-08 itemises *"sequence number, author, timestamps, and deletion metadata"*, and with timestamps listed separately the last item cannot be `deleted_at`.
- [X] T040 [US2] Write the tombstone test in `relay-platform/services/api/src/db/repository.itest.ts` (FR-006 (3.23)) asserting sequence number, author and `created_at` survive, text and attachments do not, and **the deletion's actor is recorded** (FR-006a (3.23)) — for an author's deletion and for a tenant key's, which are two different actors on the same route. **The suite already contains a hand-planted tombstone from chapter 3.15** — this is the first one the platform writes, and the two should agree column for column.
- [X] T041 [US2] Add `remove` to `relay-platform/services/api/src/messages/messages.service.ts` and the `DELETE` route to `relay-platform/services/api/src/messages/messages.controller.ts`, returning 204 (FR-006 (3.23)).
- [X] T041a [US2] Declare the delete route in `relay-platform/services/api/src/isolation/targets.ts`: `{ method: "DELETE", path: "/v1/channels/:channelId/messages/:messageId", accepts: "either", shape: "write" }`. **`"either"` is an existing value** (`targets.ts:171`) and it is the right one — the author or a tenant key may delete (FR-012 (3.23)), which is the class-level declaration this route correctly inherits.
- [X] T042 [US2] Make the second deletion a no-op in `relay-platform/services/api/src/db/repository.ts` (FR-009 (3.23)): the row is already a tombstone, nothing changes, and **no second event is emitted**.
- [X] T049a [US2] Write the six-producers test in `relay-platform/services/gateway/src/session.test.ts` (SC-008 (3.23)): read `session.ts` as text and assert each of FR-RTM-05's six kinds appears as a `type:` literal, with **the six names written out explicitly and an unknown member failing** rather than being skipped. `main.test.ts` established this shape in chapter 3.22 — it parses `main.ts` and asserts every module it builds is closed — and it is the only kind of check that can see a producer at all.

  **The first draft put this in `packages/protocol/src/frames.test.ts`, where it cannot be written.** That file tests schemas; a zod union has no notion of what emits it, and `grep` for `producer` in it returns nothing. SC-008 is a claim about the api and the gateway. Analysis pass 2 created the task and pass 3 found it unimplementable.
- [X] T042a [US2] Write the senderless-DELETION test in `relay-platform/services/api/src/db/repository.itest.ts` (FR-018 (3.23)): a deletion of a row with a null author is refused. **FR-018 (3.23) says "an edit OR deletion" and the first draft tested only the edit** — and the deletion is the half a tenant API key can reach, so it is the more exposed one.
- [X] T043 [US2] Write the idempotent-delete test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-009 (3.23), SC-007 (3.23)) asserting 204 twice, one tombstone, and **one** event — the event count is the assertion that carries the requirement, because two 204s prove nothing.
- [X] T044 [US2] Write the edit-a-tombstone test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-010 (3.23)): refused with **403 `message_deleted`**, and a non-author asking the same thing gets `not_message_author` instead — the authorship check runs first, which is what keeps the tombstone answer from telling a stranger the message exists. The guard ships in Phase 5 with `editMessage`, because `prior_text TEXT NOT NULL` makes the alternative a 500. The contract said 404 and was amended in Phase 5; see `contracts/edit-and-delete.md`.
- [X] T045 [US2] Publish `message.deleted` from `relay-platform/services/api/src/messages/messages.controller.ts` (FR-007 (3.23)) with the payload T013 defined — identity and position, no text.
- [X] T046 [US2] Write the delivery test in `relay-platform/services/gateway/src/session.itest.ts` (FR-007 (3.23)): a connected member receives `message.deleted` identifying the message, and the frame **has no text field at all**.
- [X] T047 [US2] Write the history-keeps-the-position test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-011 (3.23), SC-003 (3.23)) — the route-level twin of T009's repository-level one. **T009 proved the reader; this proves the writer and the reader agree.**
- [X] T048 [US2] Write the unread-count test in `relay-platform/services/api/src/db/repository.itest.ts`: a deleted message still counts as one unread, which chapter 3.15 decided and tested against a planted tombstone. This is the same assertion with a real writer behind it.
- [X] T049 [US2] Write the deleted-newest-message test in `relay-platform/services/api/src/db/repository.itest.ts`: deleting the newest message leaves the listing's preview reporting a null text at the same sequence, not the message before it.
- [X] T049b [US2] Re-check `specs/041-chapter-3-23/gaps.md` item 3 — the untested concurrent edit and deletion — **against the shipped routes** rather than against the plan, and correct it if the transaction shape turned out differently. The item was written during analysis from the intended design.
- [X] T049c [US2] Run the isolation gauntlet — `relay-platform/services/api/src/isolation/gauntlet.itest.ts` — and confirm all three new routes are attacked and hold. **The fixtures already seed a message per tenant** (`fixtures.ts:66`, exposed at `:85`, and its comment says *"A message the member wrote, so a read attack has something to fail to find"*), so a foreign-id attack on a `:messageId` route is real rather than a 404 for the wrong reason. **Nothing to build; confirm it ran.**
- [X] T050 [US2] Commit phase 6 in `relay-platform`, naming FR-006 (3.23), FR-007 (3.23), FR-009 (3.23), FR-010 (3.23), FR-011 (3.23), SC-003 (3.23), SC-004 (3.23), SC-007 (3.23). Gates first.

---

## Phase 7: User Story 3 — a moderator removes somebody else's message (P2)

**Goal**: FR-MOD-02, and the asymmetry the spec decided — delete anything, edit nothing.

**Independent test**: delete a message authored by one user with a tenant API key that acts as no user, and assert the same tombstone and the same event.

- [X] T051 [US3] **ALREADY TRUE AT THE END OF PHASE 6, AND BY DECLARATION RATHER THAN BY CODE.** The DELETE route in `relay-platform/services/api/src/messages/messages.controller.ts` carries no method-level `@Accepts`, so it inherits the class's `("application", "user")` (:64) — which is what FR-012 (3.23) asks for and what `targets.ts`'s `accepts: "either"` records. `deleteMessage` skips the authorship comparison when there is no user. Nothing to add; confirm the entry and the inheritance are both deliberate.
- [X] T052 [US3] Write the key-deletes-another's-message test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-012 (3.23), SC-005 (3.23)): the same tombstone an author's deletion produces.
- [X] T053 [US3] Write the key-cannot-edit test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-013a (3.23)): 403. **FR-MOD-02 grants deletion and is silent on editing, and silence is not permission** — the test is what stops that reading drifting.
- [X] T054 [US3] Write the other-user-refused test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-013 (3.23)): an end user who is not the author gets 403 for both routes.
- [X] T055 [US3] Write the cross-tenant test in `relay-platform/services/api/src/messages/messages.itest.ts` (FR-014 (3.23)): another environment's message is 404 and not 403, so existence does not leak.
- [X] T056 [US3] Re-check `specs/041-chapter-3-23/gaps.md` item 2 — FR-MOD-03's audit log, widened by this chapter and not built — against what shipped, and add the detail the analysis pass could not have: **the tombstone keeps the author of the message, which is the wrong person.** It says who wrote it, not who removed it.
- [X] T057 [US3] Commit phase 7 in `relay-platform`, naming FR-012 (3.23), FR-013 (3.23), FR-013a (3.23), FR-014 (3.23), SC-005 (3.23). Gates first.

---

## Phase 8: User Story 4 — what a client that was away can and cannot learn (P2)

**Goal**: the one soft edge in the contract, demonstrated rather than asserted.

**Independent test**: connect, disconnect, edit one message above the cursor and one below it, reconnect, and assert exactly what arrives — then assert history repairs the rest.

- [X] T057a [US4] **A NO-OP, AND THE PREMISE IS WHY.** The task asked for a per-run environment in `relay-platform/services/gateway/src/resume.itest.ts` because T058-T061 would mutate rows its neighbours share. **That file has no rows**: it boots the gateway against a stubbed api, so `environment_id: "env-1"` and `user: "tuan"` are stub return values and there is no database behind it (ADR-05). Nothing there can edit or delete a message, which is also why T058-T061 moved to `relay-platform/services/api/src/internal/backfill.itest.ts`.
- [X] T058 [US4] Write the above-the-cursor test in `relay-platform/services/api/src/internal/backfill.itest.ts` (**moved from the gateway's `resume.itest.ts`, which has no database**) (FR-016 (3.23)): a message newer than the cursor, edited during the absence, is replayed **with its current text** — because the backfill reads rows at reconnect time rather than replaying a log.
- [X] T059 [US4] Write the deleted-above-the-cursor test in `relay-platform/services/api/src/internal/backfill.itest.ts` (**moved from the gateway's `resume.itest.ts`, which has no database**) (FR-016 (3.23)): the replay does not present the deleted content. `backfill.controller.ts:92` already drops a null-text row; this asserts the behaviour rather than the line.
- [X] T059a [US4] Write the truncation guard in `relay-platform/services/api/src/internal/backfill.itest.ts` (**moved from the gateway's `resume.itest.ts`, which has no database**): a backfill page whose rows include tombstones reports `truncated` **as the read found it**, not as the mapping left it — so a page of 500 rows containing tombstones returns fewer frames and still says `truncated: true`. `backfill.controller.ts:64` already decided this and says why; `repository.ts:4835` computes it as `rows.length > limit`. **The decision is not this chapter's and the exercise is** — no writer existed, so the path has never run.
- [X] T060 [US4] Write the below-the-cursor test in `relay-platform/services/api/src/internal/backfill.itest.ts` (**moved from the gateway's `resume.itest.ts`, which has no database**) (FR-016a (3.23)): a message older than the cursor, edited during the absence, produces **no frame and no sequence gap**. Assert both — the absent gap is the half that makes this invisible to every existing client-side detector.
- [X] T061 [US4] Write the repair test in `relay-platform/services/api/src/internal/backfill.itest.ts` (**moved from the gateway's `resume.itest.ts`, which has no database**) (SC-006 (3.23)): after re-reading that range through history, the client's view matches a client that never disconnected.
- [X] T062 [US4] Correct `relay-platform/services/api/src/internal/backfill.controller.ts:83`'s comment, which promises *"when deletes arrive in Part 4 they get `message.deleted`, and resume will carry that frame instead"*. **Resume does not carry it**, by decision. The comment was written before the decision existed and is now half true; leaving it is how a published sentence stops being true and no checker sees it.
- [X] T063 [US4] Record the bound in `specs/041-chapter-3-23/baseline.txt` and in the chapter: what Slack does, what Matrix does instead, what IMAP's `MODSEQ` did, and why this platform is already the first shape.
- [X] T064 [US4] Commit phase 8 in `relay-platform`, naming FR-016 (3.23), FR-016a (3.23), FR-016b (3.23), SC-006 (3.23), SC-006a (3.23). Gates first.

---

## Phase 9: The webhook events FR-WHK-02 has named since the first draft

- [X] T065 **DONE IN PHASE 6, AND IT HAD TO BE.** `message.updated` and `message.deleted` joined `OUTBOX_EVENT_TYPES` in `relay-platform/services/api/src/outbox/event.ts` (FR-019 (3.23)) three phases early, because `repository.deleteMessage` writes its event INSIDE the tombstone's transaction (ADR-06) and T043's "one event" assertion has nothing to count without it. Spelled as FR-WHK-02 spells them — a customer's subscription filters on those exact strings.
- [X] T066 **DONE IN PHASE 6** with T065. T007 predicted four pinned places and there were **five**, plus a sixth the prediction could not name: the exhaustiveness test's `else` branch handed the membership payload to `message.deleted`. `specs/041-chapter-3-23/baseline.txt` has both numbers.
- [X] T067 **DONE IN PHASE 6** with T065: both builders in `relay-platform/services/api/src/outbox/event.ts`, the deleted one carrying no text (FR-020 (3.23)) for the same reason the frame does not, and the payload key-set tests with them. **What Phase 9 still owes is the EDIT'S outbox insert** — `repository.editMessage` writes no event yet — and the webhook end-to-end.
- [X] T068 Write the event-payload tests in `relay-platform/services/api/src/outbox/event.test.ts` asserting each payload's **exact key set**, which is how that file already tests `channel.member_added`.
- [ ] T069 Write the end-to-end webhook test in `relay-platform/services/api/src/webhooks/deliveries.itest.ts` (SC-011 (3.23)): a subscriber to message events is told about an edit and a deletion. **Pass the new types to `seedEndpoint(eventTypes)` explicitly** — that helper is parameterised and all three existing call sites pass `["message.created"]`, so a test that forgets receives nothing and looks like a delivery failure.
- [ ] T070 Re-measure the pinned places against T007's prediction of four and record both numbers in `specs/041-chapter-3-23/baseline.txt`.
- [ ] T071 Commit phase 9 in `relay-platform`, naming FR-019 (3.23), FR-020 (3.23), SC-011 (3.23). Gates first.

---

## Phase 10: The documents

- [ ] T072 Add the revision row to `docs/04-srs.md` Appendix D: FR-MSG-07, FR-MSG-08 and FR-MSG-10 built; FR-RTM-05's six kinds all have producers; FR-WHK-02 goes from three of eight to five of eight. **No clause changes** — say so, the way row 1.4 and row 1.5 do.
- [ ] T073 Update `docs/05-sad.md` §6.1 so `message_edits` reads as built rather than promised, **and amend `:342`'s sequence diagram** — it shows `text=NULL, attachments=NULL, deleted_at=now()` and the platform now writes a fourth thing, `metadata.deleted_by` (FR-006a (3.23)). **Say what the column holds**, which that DDL documents for none of the three tables that declare it. The first version of this task said to *check whether the diagram still matches*; it is already known not to, and a check where an addition is owed is how a published sentence stays wrong.
- [ ] T074 [P] Add the chapter 3.23 row to the published chapter table in `docs/07-tutorial-plan.md`, after 3.22's. **`sync-docs.sh` does NOT publish this file** — its own comment explains why at length, and chapter 3.22 corrected two task lines that claimed otherwise. The row belongs there because the table is the series' index, not because it is published.
- [ ] T075 [P] Add the `not_message_author` section to `docs/08-error-reference.md` (FR-022 (3.23)), naming the status in its `**Status:**` line, a cause, and a client action — the gate requires the last two and a body over 200 characters. **The client action is the interesting part**: there is nothing to retry and no credential to change, which is exactly why the generic code was wrong. **This turns `check:errors` green**, and it has been red on purpose since T017a. **Do not add a heading that is not a member of `ERROR_CODES`** — the orphan check fails on it with no exemption.
- [ ] T075a [P] Write the resume bound into `docs/05-sad.md` beside ADR-07's fabric clause, and into `docs/06-adr-deep-dives.md` if that record's deep dive is where the reader is sent (FR-016b (3.23), SC-006a (3.23)): a message older than a client's cursor that changed during a disconnect produces no frame **and no sequence gap**, and history is the repair. **SC-006a (3.23) is this task's too, and FR-016b (3.23) was named only by a commit task in the first draft** — the exact shape chapter 3.22's traceability caught for its own FR-002 (3.22), where a requirement's only mention was the commit that claimed it.
- [ ] T076 Run `pnpm -s sync:docs` from `relay-tutorial` **again** — phase 3 already ran it for ADR-24 rather than leave `check:docs` red for eight phases, and it is idempotent. **No task in chapter 3.22 named this step and `check:docs` caught it** — the mirror is machine-written and drifts the moment a canonical document is edited.
- [ ] T076a Write the read-path statement in `docs/05-sad.md` §6.3 or beside it (FR-017 (3.23), FR-017a (3.23), SC-009 (3.23)), **derived from the code at the moment of writing rather than from this task list**: history passes a tombstone through, resume drops it, the listing reports it with a null text and still counts it, and the backfill's `truncated` flag is computed from rows read rather than frames delivered. **Re-read all four before writing them** — the requirement counted three until analysis pass 4 measured a fourth, and the whole point of FR-017a (3.23) is that a list goes stale and the code does not.
- [ ] T077 Record EIR-WS-06's state in `specs/041-chapter-3-23/gaps.md`, re-measured rather than carried: chapter 3.22 left the error reference documenting two close codes of six.
- [ ] T078 Commit phase 10 in `relay`, `relay-tutorial`, naming FR-017 (3.23), SC-009 (3.23). Gates first, `pnpm build` before `check:errors` because that gate reads the built `dist`.

---

## Phase 11: The chapter

- [ ] T079 Count what the chapter **teaches** and what it must **fence**, as two columns in `specs/041-chapter-3-23/chapter-notes.md`, and never ask either number to do the other's job.
- [ ] T080 Estimate the word count in `specs/041-chapter-3-23/chapter-notes.md` from the number of **arguments**, and say which. Chapter 3.22 estimated 2,400 from five arguments and wrote 2,914, because three of its five argued against something already published. **This chapter argues against nothing**, so the rate should fall — predict it and check.
- [ ] T081 Write the chapter page at `relay-tutorial/app/(en)/part-3/chapter-23/<slug>/page.mdx`. **MDX is not markdown**: an indented block containing braces is a JSX expression.
- [ ] T082 [P] Write `relay-tutorial/app/(en)/part-3/chapter-23/<slug>/figures.ts` — the message's life as a state diagram, the three read paths and what each does with a tombstone, and the cursor with its blind side.
- [ ] T083 Check the fence exposure of every file this chapter touches and record it per locale in `specs/041-chapter-3-23/baseline.txt`. **A file whose chain lives entirely in the appendix cannot be fenced by a chapter** — chapter 3.22 lost half a phase to that, and chapter 3.19 had written the rule down two chapters earlier.
- [ ] T084 Generate the fences with the predecessor `git rev-parse part3-ch22^{commit}`, **a commit and not the tag**, and **against the working tree rather than `HEAD`** if anything is uncommitted — chapter 3.22 shipped a fence showing a test title the repository no longer had.
- [ ] T085 Translate the page to `relay-tutorial/app/(vi)/vi/part-3/chapter-23/<slug>/page.mdx` **by splitting on the fence regex**, so the fences are byte-identical by construction rather than by review.
- [ ] T086 [P] Mirror `figures.ts` into the `(vi)` route.
- [ ] T087 Register the chapter in `relay-tutorial/lib/tutorial.ts` with `status: "published"` and `translatedIn: ["vi"]`. **Not the sitemap**, which derives every entry from that registry.
- [ ] T088 Run `check:fences` and `check:figures` from `relay-tutorial` with exit codes captured, and expect the fenced-file count to rise from 237 and the figure count from 242.
- [ ] T089 Commit phase 11 in `relay-tutorial` and `relay-platform`. Gates first, in both.

---

## Phase 12: Polish and close-out

**T088 RAN THE FENCE CHECK AND THREE TASKS BELOW CAN EDIT A FENCED FILE AFTER IT.** Any late
edit forces **this chapter's** diff for that file to be regenerated before T099 — not a
predecessor's, which describe earlier states and must not be touched.

- [ ] T090 Read every new test's title against its assertion, one at a time, in **all eleven files this chapter adds tests to**, named rather than described: `relay-platform/packages/protocol/src/frames.test.ts`, `relay-platform/packages/protocol/src/fanout.test.ts`, `relay-platform/packages/protocol/src/codes.test.ts`, `relay-platform/services/api/src/db/repository.itest.ts`, `relay-platform/services/api/src/messages/messages.itest.ts`, `relay-platform/services/api/src/outbox/event.test.ts`, `relay-platform/services/api/src/webhooks/deliveries.itest.ts`, `relay-platform/services/gateway/src/session.test.ts`, `relay-platform/services/gateway/src/session.itest.ts`, `relay-platform/services/gateway/src/resume.itest.ts`, `relay-platform/packages/outsider/src/integrate.itest.ts`. Chapter 3.22 read **forty** and corrected three, all in one direction: a title describing the data where the assertion described the promise. **Forty, not thirty-seven** — its `baseline.txt` still says thirty-seven and its `chapter-notes.md` says forty, because its last commit before tagging was *"40 new tests, not 37"* and it fixed one record of the two. See chapter 3.23's `gaps.md` item 5.
- [ ] T091 Run the coverage lane with the nine pinned variables and pin the new production paths in `relay-platform/vitest.coverage.config.mts`. **Read `coverage-summary.json`, not the text table** — the text reporter omits a file at 100% on all four metrics.
- [ ] T092 If any arm of `relay-platform/services/api/src/db/repository.ts`, `relay-platform/services/api/src/messages/messages.service.ts` or `relay-platform/packages/protocol/src/fanout.ts` is uncovered, ask whether the code should be **deleted** before asking for a test, and pin the result in `relay-platform/vitest.coverage.config.mts`. The ratchet has removed code four times; chapter 3.22 removed three arms and wrote one test.
- [ ] T093 [P] Re-derive the files-changed count from `git diff --name-only` and compare it with T079's prediction in `specs/041-chapter-3-23/chapter-notes.md`. A first count is expected to be wrong.
- [ ] T094 [P] Re-derive `specs/041-chapter-3-23/traceability.md` against the shipped tree, both directions, checking **every quoted test title as an exact string** rather than by eye.
- [ ] T095 Run the credential scan over the chapter's diff and record the patterns searched and every hit classified in `specs/041-chapter-3-23/baseline.txt`. **Widen each pattern past the examples in front of you** — chapter 3.22's first `rk_` pattern could not cross an underscore and read zero where the answer was four.
- [ ] T096 Complete `specs/041-chapter-3-23/gaps.md`, carrying chapter 3.22's eight items with their status **re-checked against the tree rather than copied**. Its items 4, 6 and 8 are addressed to this chapter: the `main.ts` check that tests closing rather than passing, the five files that discard their child's output, and the two unowned instruments.
- [ ] T097 Stop the api, gateway and dispatcher containers, then run the twenty-run battery of `pnpm test:integration` in `relay-platform`. **Nothing else runs on the machine, and that includes your own tooling.**
- [ ] T098 Record the battery in `specs/041-chapter-3-23/baseline.txt` (SC-010 (3.23)) with the mean over the **green** runs, the stdev, and every failure's file and message. **A red run is short because turbo abandons the remaining packages** — chapter 3.22 measured 104 s against a 229 s green mean, with the gateway suite never running.
- [ ] T099 **Run all gates LAST**, after every record is written: `check:fences`, `check:docs`, `check:figures`, `check:srs`, `check:errors` from `relay-tutorial`, plus this chapter's three Python instruments. Capture every exit code into a variable; **do not pipe into `tail`**.
- [ ] T100 Commit the close-out records in `specs/041-chapter-3-23/` **before anything is tagged**.
- [ ] T101 Tag `part3-ch23` in all three repositories with `git tag -a`, **submodules first**, and verify with `git ls-tree part3-ch23^{commit} relay-platform relay-tutorial` that the root's tree names exactly the two submodule tag commits.
- [ ] T102 Trim `CLAUDE.md`. It is 231 lines after chapter 3.22's trim and is loaded into every session.
- [ ] T103 Hand `specs/036-chapter-3-18/reader-protocol.md` to a second person. **Named by nine chapters and closed by none.** No command in this repository discharges it.

---

## Dependencies and execution order

    Phase 1   setup, premises, the READER test  blocks everything
    Phase 2   the protocol, and one error code  blocks Phases 6 and 9's frames
    Phase 3   the fabric, the fifth grammar     blocks BOTH P1 stories — no frame reaches a socket
    Phase 4   the table                         blocks Phase 5's history append
    Phase 5   US1, the edit                     needs Phases 2, 3 and 4  🎯 MVP
    Phase 6   US2, the deletion                 needs Phases 2, 3 and 5's route shape
    Phase 7   US3, moderation                   needs Phase 6
    Phase 8   US4, the resume bound             needs Phases 5 and 6
    Phase 9   the webhook events                needs Phases 5 and 6
    Phase 10  the documents                     needs everything above; turns check:errors green
    Phase 11  the chapter                       needs Phase 10
    Phase 12  close-out                         gates LAST


**Parallel opportunities, and there are fewer than the first draft claimed.** Eleven tasks
lost their `[P]` when the file paths were checked against each other: `[P]` means a different
file, and this chapter's tests concentrate in four of them. `repository.itest.ts` carries
seven tasks across two phases, `messages.itest.ts` eight across three, and `event.ts` and
`event.test.ts` two each — every one of those must go in sequence.

What genuinely parallelises: T002 and T003 in Phase 1, two different instruments; T074 and
T075 in Phase 9, two different documents; T082 and T086 in Phase 10, the figures and their
mirror; T093 and T094 in Phase 11, two different records.

**T006, T007 and T008 all append to `baseline.txt`** and were marked `[P]` in the first draft
for the same reason the others were — the tasks are independent and the file is not. They
keep their marker because appending four lines to a record is not the same hazard as two
edits to a test file, and this sentence is here so the exception is visible rather than
inconsistent.

**MVP**: Phases 1–5. An author can correct a message, everyone watching sees it, and the
prior text is kept — FR-MSG-07 closed with `message.updated` producing for the first time.

**T009 must pass against unchanged code or the plan changes**, which is Phase 1's whole
point.

**This block was regenerated from the phase headers, not edited.** It said eleven phases with
the pre-fabric numbering for two analysis passes — "Phase 4 US1 🎯 MVP" when US1 had become
Phase 5 — and it omitted the fabric phase entirely, the one that blocks both P1 stories. A
reader following it would have built the table, called it the MVP, and found no route to edit
a message. Nothing in this repository reads prose, so four passes went by.
