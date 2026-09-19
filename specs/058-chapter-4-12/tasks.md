# Tasks: chapter 4.12 — a link that expires, and who may hold it

**Input**: `specs/058-chapter-4-12/` — spec, plan, research, data-model, contracts, quickstart
**Prerequisites**: chapter 4.11 shipped and tagged `part4-ch11`

**Tests are requested.** Constitution VI makes FR-MED-08 a `T` clause, and the chapter's central
property — three refusals that cannot be told apart — is a claim about a set of responses that
only a test comparing them can make.

## Format: `[ID] [P?] [Story] Description`

- **[P]** — different files, no dependency on an incomplete task
- **[US1] [US2] [US3]** — the user story the task serves; setup, foundational and polish carry none

## Path Conventions

`relay-platform/` is the platform, `relay-tutorial/` the chapter, `docs/` the published documents.
Paths below are relative to the repository that owns them.

---

## Phase 1: Setup — the measurements this chapter is compared against

- [ ] T001 Bring the stores up and record what answers: `RELAY_POSTGRES_PORT=15432 docker compose up -d --wait`. **No service list starts the stores and nothing else** — `api`, `gateway` and `dispatcher` carry `profiles: ["services"]`, so a list of store names and no list do the same thing.
- [ ] T002 Record the opening `check:fences` figure as an **absolute number**. It is 0 at `part4-ch11`. A delta of zero is what hid a problem for nine chapters.
- [ ] T003 [P] Record the opening dependency count across every `package.json` in `relay-platform` — **29** at `part4-ch11` — so SC-009 is a comparison rather than an assertion. **Write the counter as a file, not a shell one-liner**: 057's first attempt summed eleven quoting errors to `TOTAL 0` and printed it on stdout with the errors on stderr.
- [ ] T004 [P] Record the opening state of the lanes: `pnpm test`, `pnpm test:integration`, `pnpm test:outsider` and `pnpm check:errors` (**34 codes, 34 sections**). **Read each one's counted line, not its exit code.**
- [ ] T004a **Stop the composed services before any lane runs** (`gaps.md` 057-5). `docker compose --profile services` is a second set of relays on the same `outbox` and turns `outbox.itest.ts > invariant 8` red — 11 of 12 with them up, 12 of 12 with them stopped. Record which state each measurement was taken in.
- [ ] T005 **Re-measure the reference lookup before the index exists**, and keep the numbers: `EXPLAIN (ANALYZE, BUFFERS)` for a hit and for a **miss**. The planning figures were 2.132 ms / 806 buffers and 2.886 ms / 1,016 on 66,516 messages. **The lane moves between chapters** — 4.8 watched a median shift because the feature itself changed the population — so a figure carried from `research.md` into the chapter without re-measurement is a figure about a different database.
- [ ] T006 **Count the fenced files this chapter will touch, against the checker.** `plan.md` lists eight as a starting point and says so. **The list has been low at every chapter**: 056 said twelve and the checker said seventeen; 057 said thirteen and the checker said twenty-two. `pnpm check:fences --dump` after the first source edit is what answers it.

---

## Phase 2: Foundational — the lookup and its index

**Blocking.** Every story asks the same question of `messages.attachments`, and the answer's cost
is the chapter's central measurement.

- [ ] T007 Write `services/api/migrations/0017_media_reference_index.sql` — `CREATE INDEX messages_attachments_gin ON messages USING gin (attachments jsonb_path_ops)`. The tail is `0016_storage_quota.sql`, checked rather than remembered.
- [ ] T008 **`CREATE INDEX` and NOT `CONCURRENTLY`, decided by reading the runner** (plan open question 3). `migrate.ts:46` issues `BEGIN` around every file, and `CREATE INDEX CONCURRENTLY` cannot run inside a transaction — so the choice is not open, it is made. **Record what that costs**: a plain build takes a lock that blocks writes to `messages` for its duration. Milliseconds on the lane; a deploy-shaped number at a million rows, and the chapter says which it measured.
- [ ] T009 Declare the index in `services/api/src/db/schema.ts` so drizzle's type and the migration agree. **The migration is the source of truth** (ADR-16: forward-only hand-reviewed SQL); the declaration is what stops the next generator run proposing to drop it.
- [ ] T010 Add the reference lookup to `services/api/src/db/repository.ts`, beside `channelVisibleTo`. **The query engine lives in the repository because a lint rule says so in constitution I's words** — 4.7 found that wall and 4.10 and 4.11 both hit it.
- [ ] T011 **Return every referencing channel, not the first** (`data-model.md` §4). Authorisation is a disjunction over them: a query that stopped at one row would refuse a caller whose channel happened to be second, which is a correctness bug that presents as flakiness.
- [ ] T012 **Reuse `channelVisibleTo` rather than writing a membership check** (research R2). `repository.ts:5517` already handles the three cases this clause needs, including *"userId absent means the tenant is reading"* — which is FR-MED-08's own *"or API key"* arm. Say in a comment that it was reused and why: the SRS note's *"rather than inventing a parallel ACL system"* is satisfied by construction only if nothing new is written.
- [ ] T012a **RESOLVE THE EXTERNAL ID TO THE INTERNAL ONE FIRST, AND THE MEDIA CONTROLLER'S OWN PATTERN IS THE TRAP.** `media.controller.ts:12` computes `req.principal.userExternalId` and hands it to the service; `channelVisibleTo(channelId, userId)` takes the **internal UUID**, because `isMember` compares against `members.user_id`, a `uuid` column. External ids on this platform are `tuan`, `linh`, `delivery-bot` — **plain strings**.
  **HANDING ONE STRAIGHT THROUGH IS T016a's 500 AGAIN**, from inside the authorisation check rather than from the path. Two places already do it right and either is the shape to copy: `media.service.ts:89` (`getUserByExternalId`) and `messages.controller.ts:526-530`, which resolves and answers **400 `unknown user`** when the id names nobody.
  **AND THE SILENT VERSION IS THE ONE THAT SHIPS.** Where a tenant's external ids happen to be UUID-shaped, no parse fails — `isMember` simply returns false, and **every private channel refuses every member** while every public channel still works. On this lane that is a 500; on a customer's it is a quiet refusal.
- [ ] T013 **Measure the lookup again with the index in place**, same two queries against `messages`, same shape: time **and buffers**. Milliseconds alone let a warm cache report a win a cold one does not.
- [ ] T014 Commit phase 2.

---

## Phase 3: A recipient opens the photo (US1) 🎯 MVP

**Goal**: FR-MED-08's delivery path. **Independently testable**: a member asks, gets a URL, and
the bytes come back.

- [ ] T015 [US1] Add `GET /v1/media/:mediaId` to `services/api/src/media/media.controller.ts`, beside the existing `@Post()`. The class already carries `@Accepts("application", "user")`.
- [ ] T016 [US1] Validate the path parameter as a UUID, refusing a malformed one with **400 `invalid_request`** naming `mediaId`. **There is no precedent for this anywhere in the api** — no route validates a path param today — so this route is the first, and T016a is why that is not merely tidy.
- [ ] T016a **MEASURE THE CLASS THIS ROUTE IS THE FIRST TO ESCAPE, AND PUBLISH IT.** Against the composed api, before writing anything:

        GET /v1/channels/not-a-uuid/messages  ->  500
        {"code":"internal_error","message":"unexpected internal error"}

  **A caller-triggered 500 on a shipped route, reachable by anyone with a credential.** It is 4.11's research R3 exactly — a value of the wrong type reaching the driver, `invalid input syntax for type uuid`, which the filter has no rung for. That chapter found it in a request BODY, measured it, and fixed it with `z.uuid()`; **nobody looked at the path.** 13 routes take `@Param("channelId")` and 3 take `@Param("messageId")`.
- [ ] T016b **Decide in writing whether this chapter fixes the sixteen, and record the cost either way** (`contracts/media-delivery.md`). The fence bill is the input: `messages.controller.ts` **18** titled fences, `channels.controller.ts` **8**, `users.controller.ts` **4** — thirty fences across three published files for a change that is one pipe per parameter.
  **THE ARGUMENT FOR FIXING IT HERE**: it is one line per route, this chapter found it, and *"a measurement is not a repair"* is what 049 wrote about `check-lane-scope.py` after measuring a retarget and not landing it.
  **THE ARGUMENT AGAINST**: a chapter about signed delivery that rewrites three controllers is teaching two things badly. 4.11 filed 057-1 rather than building a reference count for the same reason, and its one-line CI fix was one line.
  **Whichever is chosen, `gaps.md` carries the measurement**, so the next chapter to touch a controller inherits a number rather than a suspicion.
- [ ] T017 [US1] Sign a **GET** with `expiresIn: 3600` in `services/api/src/media/media.service.ts`. `presign.ts` has taken `"GET"` since 4.10 and needs no change — assert that it needs none rather than editing it to be sure.
- [ ] T018 [US1] **Sign with `endpoint`, not `internalEndpoint`** (4.11's FR-026). This URL is handed to a client outside the network; the probe's address is the api's own. The host is inside the SigV4 signature, so signing with the wrong one produces a URL that is refused rather than one that is slow.
- [ ] T019 [US1] Return `{ url, expires_at }` and nothing else. `expires_at` exists so a client need not parse `X-Amz-Date` and add `X-Amz-Expires`, which is the same courtesy the upload slot gives.
- [ ] T020 [US1] Integration test in a **new file**, `services/api/src/media/delivery.itest.ts`: a member of the referencing channel gets a URL and fetches the bytes, and the bytes are **byte-identical** to what was uploaded (SC-001). A new file costs the fence chain nothing, which is the cheap direction 051 recorded and 4.11 used.
- [ ] T021 [US1] **The store enforces the expiry, and the test proves it from the store's clock** (SC-003). Sign with `expiresIn: 1` and `now` ten seconds in the past; the store answers **403** with `Request has expired`. Asserting that our own arithmetic produced an earlier timestamp proves nothing about the store.
- [ ] T022 [US1] Integration test: a tampered signature is refused. **Map the changed character to a different one and assert the URL actually changed** — 4.10's tamper probe replaced the first character with `f` and was a no-op on 255 of 4,096 runs, reporting the store's honest 200 as an acceptance.
- [ ] T023 [US1] Integration test in `services/api/src/media/delivery.itest.ts`: an **application credential** gets a URL for any object of its environment, whatever the memberships are (FR-006).
- [ ] T023a [US1] Integration test in `services/api/src/media/delivery.itest.ts`: a **member of a PRIVATE channel** gets a URL. **This is the only test that reaches `isMember` at all**, and without it the whole membership path can be broken while every other test passes: T024's public channel returns true before `isMember` is consulted, and T028's private non-member expects a refusal, which a broken predicate also produces. **The grant exercises membership; the refusal does not.**
- [ ] T024 [US1] Integration test in `services/api/src/media/delivery.itest.ts`: a **public** channel's referencing message authorises a user token **without membership** (research R2). This is the case a literal reading of *"channel membership"* would have refused, and the lane holds 11,289 public channels against 995 private — so it is the common case, not the edge.
- [ ] T025 [US1] Re-measure and record the route's latency, sampled rather than asserted. **Pause BEFORE each pair and alternate the order within it** — 4.11's first measurement reported the media send 35.4% *faster* because the pause sat after the pair and only one side ever followed a quiet gap. And **the tenant's own limiter bounds the sample**: 600 requests answered `429 … retry after 34 seconds`.
- [ ] T026 [US1] Commit phase 3.

**Checkpoint**: a client that can read the message can fetch the photo.

---

## Phase 4: Somebody who cannot read the message cannot read the file (US2)

**Goal**: FR-MED-08's authorisation, with one answer for three conditions.

- [ ] T027 [US2] Refuse an object of another environment (FR-005). `channelVisibleTo` is already scoped to `this.environmentId`, so this should hold without new code — **assert it rather than assuming the scoping covers a path it has never been asked about.**
- [ ] T028 [US2] Refuse an object referenced only in a **private** channel the caller does not belong to (FR-004), tested in `services/api/src/media/delivery.itest.ts`.
- [ ] T029 [US2] Refuse a `media_id` no object has (FR-005).
- [ ] T030 [US2] **Refuse an object with no referencing message at all**, tested in `services/api/src/media/delivery.itest.ts` — including to the credential that uploaded it (research R1). This is the case the specification assumed the other way, and the argument is the clause's own note: granting the uploader access is a second authorisation rule that does not follow a message, which is the parallel ACL FR-MED-08 forbids. FR-MED-10 hard-deletes unreferenced objects after 24 hours, so it would be a read path to a thing already scheduled for destruction.
- [ ] T031 [US2] **One code, one message, one body for all four** — 404 `not_found`. Integration test comparing the **whole body** with `request_id` removed, not the code: a message or a field leaks an existence oracle exactly as well as a code does.
- [ ] T032 [US2] **No new error code, and assert that.** `pnpm check:errors` must read **34 codes, 34 sections** at the close, unchanged from 4.11. A chapter that adds a route usually adds vocabulary; this one reuses `not_found` on `channelVisibleTo`'s own precedent, and the unchanged number is the evidence.
- [ ] T033 [US2] **Run the refusal red by removing the `channelVisibleTo` call**, and confirm the private-channel test fails rather than the shape test. A refusal that can only fail for somebody else's reason is the class 043 named and 4.11 re-ran at every phase.
- [ ] T034 [US2] Integration test in `services/api/src/media/delivery.itest.ts`: a **deleted** message's attachment stops being readable (research R9). 4.11's FR-024 nulls the column on delete, so the reference disappears and this route refuses — **asserted rather than assumed**, because nothing else in the platform connects those two facts.
- [ ] T035 [US2] Commit phase 4.

---

## Phase 5: One object, two channels, two answers (US3)

**Goal**: the case the clause's singular *"the referencing message"* does not describe.

- [ ] T036 [US3] Integration test in `services/api/src/media/delivery.itest.ts`: one object, two messages, two channels. A member of either gets a URL; a member of neither is refused.
- [ ] T037 [US3] **Run it red by making `repository.ts`'s lookup return one reference** (T011's inverse). The test must fail for the caller whose channel is second, which is what proves the disjunction is real rather than incidental.
- [ ] T038 [US3] Record in `page.mdx` that FR-MSG-11 has allowed the same id twice since 3.24 — *"the same id twice is two attachments"* — so two references is the ordinary consequence of forwarding a photo, not an edge case.
- [ ] T039 [US3] Pin the new and changed files in `vitest.coverage.config.mts`, and **probe both halves**: demand an impossible figure of each new key and confirm it fires, then confirm the measured pins pass. A pin whose key matches no file is silent.
- [ ] T040 [US3] **Read `coverage-summary.json`, not the text table.** v8's text reporter omits a file at 100/100/100/100, which cost 056 three of five new files.
- [ ] T041 [US3] **Answer constitution VI's 100%-branch clause for the authorisation path, per arm** (SC-004's sibling). The clause names tenant isolation and this is tenant-isolation code. `repository.ts` is pinned at 92 branches against hundreds, so **the pin is not the instrument** — delete each arm and re-run, as 4.11 did. Two of its four probes said something a number could not.
- [ ] T042 [US3] Commit phase 5.

---

## Phase 6: The gauntlet, the budget, and what this chapter cannot fix

- [ ] T043 **Run the derivation first and record what it says.** This chapter **adds a route**, so `targets.itest.ts` should name `GET /v1/media/:mediaId` as unclassified — breaking 4.11's streak of one chapter that added none. If it comes back green, the derivation did not see the route and that is the finding.
- [ ] T044 Add the route to the classification in `services/api/src/isolation/targets.ts`, then expect the gauntlet to go red with **"classified but never attacked"** — the third accounting direction 4.8 found after the plan named two.
- [ ] T045 Extend `services/api/src/isolation/gauntlet.itest.ts` with a **forged `media_id` READ** attack. 4.11 added a forged-`media_id` write on the send route; this is the same id against a different verb, and a platform could hold one and not the other.
- [ ] T046 **The attack in `services/api/src/isolation/gauntlet.itest.ts` plants a media object for each tenant and runs a control first.** Both tables are otherwise empty and an empty table passes a leak check for the same reason an empty page does. The control — the attacker reading its **own** object — must answer 200, or the refusal below means the feature is broken rather than that the boundary holds.
- [ ] T047 Run the attack red by removing the environment scope from `services/api/src/db/repository.ts`, and confirm it fails for the tenancy reason rather than a shared refusal.
- [ ] T048 [P] Record in `gaps.md`: **a signed URL outlives the authorisation that produced it** (FR-010, research R7). A caller removed from the channel at minute 1 holds a working link until minute 60. Nothing here can fix it — the store checks a signature and has never heard of a channel — and shortening the hour trades one exposure for a broken image. Name the window.
- [ ] T049 [P] Record in `gaps.md` and the chapter: **every delivery spends one `rest` operation** (FR-011, research R8). A gallery of fifty images spends fifty of the tenant's budget. Left counted, for 4.8's reason — an exemption list is a hand-maintained table.
- [ ] T050 [P] **Re-measure `gaps.md` 057-1 and close or narrow it in writing** (FR-012). It was filed as *"nothing counts references to a media object"*; this chapter is its first consumer. It is narrower now — there is a query and an index — and it is not closed, because FR-MED-10's sweep needs the opposite question (*which objects have NO reference*) and an index that answers containment does not answer absence.
- [ ] T051 **Decide plan open question 1 in writing, in `contracts/media-delivery.md`**: one id per request, or several. The budget argues for a batch; the existence oracle argues against, because a batch refusal has to say which ids failed without saying why. Record the decision and the rejected alternative either way.
- [ ] T052 **Decide plan open question 2 in writing**: whether the response carries the object's `state`. 4.11's FR-013 asserted delivery carries no state and that was about the message; this is the same smell one route over.
- [ ] T053 Run `check-lane-scope.py` and record the file count. It read **60** at 057's close; this chapter adds integration tests and the number must rise. A run that reads nothing exits 2.
- [ ] T054 Commit phase 6.

---

## Phase 7: The chapter

- [ ] T055 Write `relay-tutorial/app/(en)/part-4/chapter-12/…/page.mdx`, **2,000–4,000 words outside code fences**, measured with `node relay-tutorial/scripts/prose-words.mjs <page>`.
- [ ] T056 **At least one `TRAP` box.** The candidates are measured rather than invented: the index that cannot be built `CONCURRENTLY` because the runner opens a transaction (T008), the refusal being the expensive lookup, and *"channel membership"* read literally being stricter than the message it guards.
- [ ] T057 **Publish the index measurement in `page.mdx` beside 4.1's opposite conclusion.** That chapter found an index buying *"a gap inside the run-to-run spread for +49% storage"*; this one buys 26× to 160× for 1.7%. **Both are right** — the transferable lesson is which kind of cost you are looking at, and a chapter that published only its own half would teach the wrong rule.
- [ ] T058 **Say which half of FR-MED-08 this chapter did not build** (FR-009). *"Object storage shall not be publicly readable"* is `presign.itest.ts:53`, whose title already names this clause. Re-proving it would claim work 4.10 did.
- [ ] T059 Register the chapter in `relay-tutorial/lib/tutorial.ts`. `<ChapterHeader id="4.12" />` throws on an unregistered id, so `pnpm build` exits 1 from the moment the page exists.
- [ ] T060 [P] Figures in `figures.ts`, each named by a `<Figure>`. **Pass each diagram as `code`, not `chart`** — 4.11 used `chart` and all three rendered nothing on a page that built and served 125 pages green. `check:figures` is the only thing that asks.
- [ ] T061 A hunk per fenced file this chapter edits, **counted at T006 rather than remembered**. Generate each with `pnpm check:fences --dump`, never with `git diff` against the working tree.
- [ ] T062 **Verify each hunk by exact occurrence count, not `patch --dry-run`** (`gaps.md` 056-7). `patch` applies with fuzz and offset and said yes to seven hunks the checker refused.
- [ ] T063 **Check which state each hunk is written against** before blaming it. `fences/post-series.md` applies after every chapter, so a hunk for a file the appendix also amends is written against a state no reader sees — 4.8 found it, 4.11 paid it on `codes.ts` and moved the hunk to the appendix.
- [ ] T064 **Decide the chapter/appendix split before the prose is written.** `repository.ts` carries 49 fences and 4.11 published a 201-line hunk for it; deciding afterwards is how a chapter ends up showing a reader 1,576 diff lines to make one point.
- [ ] T065 **There is no Vietnamese twin to write** — check it rather than assume it. `app/(vi)/vi/part-4/` held chapters 1-3 at 4.11's close against en's 11, a lag of eight. 050 and 056 both recorded a task that described a corpus instead of checking one, and 4.11's own task said eight when the tree said seven.
- [ ] T066 Run `pnpm check:fences` and report the **absolute number**.

---

## Phase 8: The record

- [ ] T067 Write `baseline.txt` carrying every phase's measurements in the order they were taken, and the pinned lane environment.
- [ ] T068 **Re-measure the dependency count across every `package.json` and compare it to T003's opening figure** (SC-009).
- [ ] T069 Write `gaps.md`. **Re-measure every carried item rather than copying it**: 057-1 (T050), 057-2, 057-4, 057-5, 056-1, 056-2, 055-3. **And record T016a's class with its measurement** — a malformed UUID path parameter is a caller-triggered 500 on 16 shipped routes, found by this chapter and fixed on one of them at most.
- [ ] T070 **Decide whether the SRS needs a revision, and write it if it does.** The candidate is research R2: FR-MED-08's *"(channel membership or API key)"* is a gloss on *"authorised to read the referencing message"*, and this platform's answer to that question is `channelVisibleTo` — membership for private channels only. **A literal reading is stricter than the message it guards**, which is a clause falsified by the platform's behaviour rather than by a measurement. Five of the last six chapters amended; 4.11's default of "no revision" was flipped by reading the clause verbatim.
- [ ] T071 **Amend BOTH copies of the Part 4 table** — `docs/12` §3 row 13 **and** `docs/07-tutorial-plan.md`'s copy. Chapters 4.7 through 4.10 each amended one of the two and 4.11 was the first to find the other had received none of them.
- [ ] T072 Write `traceability.md`. **Enumerate the ids and read each row** — a literal grep produced fourteen alarms at 4.11 and all fourteen were false, so the sweep cannot build the table and neither can memory.
- [ ] T073 Update `CLAUDE.md`'s `<!-- SPECKIT -->` block for the close, including every task premise this chapter falsified by running it.
- [ ] T074 Run the tutorial job's six gates, named from `ci.yml` rather than memory, and **read each one's counted success line**. `lint` is the one with no counted line at all.
- [ ] T075 Run `pnpm test:outsider` with the outsider job's own preconditions, and extend the sealed suite to fetch a media object's bytes from outside (SC-010). **That suite ran in CI for the first time at 4.11**, after a one-line fix to a migrate step that had no `working-directory`.
- [ ] T076 **Rebuild in all three senses before believing a run.** `pnpm build` for the spawned `dist`, `docker compose --profile services build` for the container image, and the protocol package before anything reads a type from it. 4.11 lost a confusing failure to each of the first two.
- [ ] T077 Run the quickstart **unmodified**, and only then let it say every command was run before it was written. NFR-USE-03 is a `T` clause at 100% and `ci.yml` contains the word `quickstart` zero times, so this run is its whole verification. 4.11's was wrong five times and **four produced a red that looked like a platform defect**.
- [ ] T078 Run `pnpm check:errors` by hand, in both directions, and assert **34/34 unchanged**. It is a script no CI job runs (055-3).
- [ ] T079 Tag `part4-ch12` on `relay-platform`, commit, and push all three repositories.
- [ ] T080 After the push, confirm CI. **Compare per error, not per colour** — and **over more than one run**. 4.11 compared a single run and called the error set identical; three runs read 3, 6, 3, where the middle one's extras were absent from both neighbours. One comparison supports *"this run introduced nothing new"*, not *"the set is stable"* (`gaps.md` 057-8).

**Checkpoint**: a `media_id` is a URL, and the record says what the URL cannot promise.

---

## Dependencies & Execution Order

### Phase Dependencies

```text
Phase 1 (setup) ─────────────► everything
Phase 2 (lookup + index) ────► US1, US2, US3   — every story asks the same question
Phase 3 (US1) ───────────────► US2             — there is no grant to refuse against
Phase 5 (US3) ───────────────► independent of US2
T005 ────► T013                 the before figure must exist before the after one
T008 ────► T007                 read the runner, then write the migration
T011 ────► T037                 the disjunction before the test that proves it
T043 ────► T044 ────► T045      derive, classify, attack — in that order
T006 ────► T061                 a hunk list counted, not remembered
T064 ────► T055                 the split decided before the prose
T070 ────► T071                 write the amendment once, apply it to both copies
T076 ────► T075, T077           three kinds of stale build, before anything is believed
T079 ────► T080                 CI is only observable after a push
```

### User Story Dependencies

**US1 is the MVP and it is not independently shippable**, which is worth stating. A delivery
route with no authorisation hands any caller any object of any tenant — so phases 2, 3 and 4 are
one shippable increment. US3 is independent of US2 and could ship alone, because it widens a
grant rather than adding a refusal.

### Parallel Opportunities

- **T003, T004** — different commands, no shared state.
- **T048, T049, T050** — three `gaps.md` entries, written independently.
- **T060** — figures, while the prose is drafted.
- **Nothing in phase 2 is parallel.** The migration, the declaration, the lookup and the two
  measurements are one chain, and the measurements bracket the change.

---

## Implementation Strategy

**MVP is phases 2 through 4**, not phase 3 alone, for the reason above: a route that hands out
URLs without checking who is asking is worse than no route.

**The chapter's argument is already measured.** The index comparison, the seq-scan buffers and
the public/private split were taken before the specification was written — so phase 7 is writing
rather than discovering, and phase 1's T005 exists to catch the case where the lane has moved
underneath them.

**What this chapter could get wrong, ranked by how quietly it would happen:**

1. **Handing an external id to a predicate that wants a UUID.** Silent where a tenant's ids are
   UUID-shaped — every private channel refuses every member while every public one works — and a
   500 where they are not. **T023a is the only test that would notice**, because it is the only
   one that asks for a grant through `isMember`. T012a, T023a.
2. **Implementing the clause's words instead of the platform's rule.** A membership check passes
   every test somebody would think to write and refuses the photo in a message the caller can
   read. T024 is the test that catches it and it is in US1 rather than US2 on purpose.
3. **Stopping the lookup at the first reference.** Correct for one reference, wrong for two, and
   it presents as flakiness rather than as a refusal. T037.
4. **Measuring only the hit.** The refusal is the expensive path and the cheap request to make.
   T005 and T013 both say *a hit and a miss*.
5. **Believing a green run against a stale build.** Three kinds, and 4.11 lost time to two of
   them in one phase. T076.
