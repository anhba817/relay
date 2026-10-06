# Tasks — chapter 4.22, "The identifier the customer gave it"

**Feature**: `specs/068-chapter-4-22/` · **Plan**: [plan.md](./plan.md) ·
**Research**: [research.md](./research.md) · **Contract**: [contracts/addressing.md](./contracts/addressing.md)

**The chapter builds; 069 / chapter 4.23 verifies.** That ordering is `docs/12` §5
rule 4 and it is why this chapter exists apart from the milestone that found it.

---

## Phase 1: Baseline

- [X] T001 Pin the lane in `specs/068-chapter-4-22/baseline.txt`: `RELAY_POSTGRES_PORT=15432`, the services up, and the row counts (`channels`, `users`, `messages`, `audit_log`). **Record them beside every later timing** — they are part of the instrument.
- [X] T002 Record every lane's opening exit code, **each with its `Cached:` line and elapsed time, or under `pnpm exec turbo run <task> --force`** — `pnpm test -- --force` forwards the flag to VITEST, which rejects it, and prints `Tasks: 0 successful` with `Cached: 0`, which reads like a cache bypass and is six tasks failing to start. Feature 069's T002 opened with **all three lanes FULL TURBO** — `Cached: N of N`, 10ms, every counted line replayed. **`turbo run lint` is not a task**; the root task is `lint:root`.
- [X] T003 Run all six tutorial gates from `relay-tutorial` and record each counted line. **Measured at analysis pass 10, all six EXIT 0** — and 069's three inherited figures all matched, so these are current rather than carried:

```
check:fences   291 fenced files across 64 chapters (46 translated, 2 retired)
check:figures  326 figures · 328 imported bindings resolve · 3 export(s) unused
check:docs     all mirrored docs match · 29 revisions ascend, 1.0 to 1.28
check:srs      245 clause rows, 245 unique identifiers, no duplicates
check:errors   34 codes, 34 sections, 6 close codes
```

**`pnpm -s <script>` is not a way to run any of these.** This pnpm rejects `-s` with `error: unexpected argument '-s' found` and **EXIT 2 without running the script** — an exit code with no gate behind it, measured on all five.
- [X] T003a **Write the four gate deltas this chapter predicts, before it starts.** Each is falsifiable and each belongs to one task:

```
check:fences   chapters  64 -> 65    the walker found the page     T044's registration
check:fences   files    291 -> 291   the chapter titled no fence   T051's precedent
check:docs     revisions 29 -> 30    1.29                          T036
check:srs      rows     245 -> 246   FR-CHN-11, and unique         T027
```

**The two halves of the fence line check different things.** `en.perChapter.size` is set once per page the walker visits (`check-fence-chain.mjs:272`, outside the fence loop), so a chapter contributing **0** titled fences still moves it — which is how 4.19, 4.20 and 4.21 each moved it by one. `en.state.size` counts distinct fenced files and moves only if this chapter titles a fence. **A chapter count that does not move means the page was not found** — 051's `Error: Unknown chapter id: 4.6`, which was the manifest step failing first.
- [X] T004 Capture the CI error-set baseline for the per-error comparison at close (SC-010). 069's T004 read **0 distinct errors** on a green run; an empty diff between two green runs carries nothing and the record should say so.
- [X] T005 **Re-derive the fence bill** rather than copy R6's. R6 says **8 files · 53 English pages · 46 Vietnamese · 17 appendix blocks to regenerate · 3 to CREATE**, and it carries the method, because the number moved five times and nobody could reproduce it. **Count the two language trees separately**: `app/(en)` is what `check:fences` replays onto `relay-platform`, `app/(vi)` is mirror-compared against the English chapter and never against the tree (050-3), and every figure before pass 9 added them together. **And count blocks to CREATE, which a sweep of what exists cannot see** — `channels.controller.ts`, `users.schema.ts` and `media/media.controller.ts` are edited by this chapter and have no appendix block at all. `grep -rl 'title="[^"]*<file>"' app/(en) app/(vi) fences/` for pages; blocks and `@@` lines from `fences/post-series.md`.
- [X] T006 **Re-measure R1–R3 before trusting them**: the 500 on `GET /v1/channels/{externalId}`, the `invalid input syntax for type uuid` from Postgres, both lookups' buffers and timings, **0 of 41,772** uuid-shaped external ids, and the **173** call sites. They were taken on 2026-10-05, re-taken on 2026-10-06, and the lane moves: **channels went 41,768 → 41,772 and reused user external ids 1,576 → 1,597 in one day.** (And the sweep that propagated the new figure overwrote this line's own history on its first run — a find-and-replace cannot see which occurrence is deliberately the old value. 4.17's trap, from the other side.) The conclusions held — 0 uuid-shaped either time.
- [X] T006a **Propagate whatever T006 measures to every place that quotes it**, which T006 does not say and is the half that goes stale. `41,772` appears **9 times across 7 files** — spec, research, data-model, contract, quickstart, tasks, checklist. **Match both spellings**: 4.17's find-and-replace keyed on `447,377` could not see the `447377` a program printed. A denominator that moves by four changes no conclusion here, which is exactly what makes it easy to leave wrong.

---

## Phase 2: The decisions (BLOCKING)

- [X] T007 **Confirm pass 3's finding against a running api before anything rests on it**: there is no `GET /v1/users` route, `listingQuerySchema`'s one consumer is `GET /v1/users/{externalId}/channels`, and the cursor carries `channels.id`. Pass 3 read the controller and `targets.ts` with the lane down. **A published ADR is about to be amended on this**, so it is measured first.
- [X] T008 **Decide the compatibility path ONLY IF T026's sweep gives a reason to change an opaque token** (FR-007). Two shapes: a **version field** in the payload, or a **dual-read** that accepts either. **A silently wrong page is the forbidden outcome** — a cursor the new reader misinterprets skips or repeats rows and the caller cannot see it. **The default is to change nothing**, which is the only option with no silently-wrong-page risk at all.
- [X] T009 **Decide the PROCEDURE behind the tie-break, and whether the OUTCOME is a clause or a comment.** The outcome is settled: **the identity wins**. The procedure is not, and R2's two candidates are one query with `order by (external_id = $2) desc` — **which needs `EXPLAIN` first, because 4.18 found an `OR` can land in a `Filter:`** — or the identity looked up before the key, costing a second round trip on all 173 uuid call sites. **Constitution VI's first bullet**: which identifier wins is behaviour a customer can observe, **so if it is a clause, T027 writes it before T013 is coded** — T027, not T034: T034 is the READ task and T027 is the amendment, two phases earlier. That is a Phase 5 task blocking a Phase 3 one, which the dependency graph now shows.
- [X] T010 **Decide whether this chapter needs an ADR**, and record the reasoning either way. Predicted **yes**: *which identifier addresses a noun* has a reversal condition, will be cited by every future table carrying a customer identifier, and extends ADR-18 from users to channels. **4.21's plan predicted no and was wrong; 4.23's predicted yes.** A prediction is worth nothing without the check.
- [X] T011 **Check the plan's premise by reading, not grepping.** Open `channels.controller.ts`, `messages.controller.ts`, `users.controller.ts`, `users.schema.ts` and the repository methods behind each, and confirm the 13 `@Param` sites and what the pipe must return. **065's T007 said fourteen sites and the real number was five, because a grep counts mentions.**
- [X] T011a **Confirm an injectable pipe can take the request-scoped `Repository`** — by writing the smallest one that compiles and boots, not by reasoning about Nest's scope bubbling. **`MediaModule` declared a service it did not provide, compiled, typechecked, linted, and failed at the first request** (4.10). **Only a running app answers this.** R4's probe got a request-scoped dependency into a param-level pipe and read it back through a real request — **so what is left is the real `Repository`, not the shape.**

---

## Phase 3: User Story 1 — the identifier works on every channel route (P1) 🎯 MVP

**Goal**: thirteen routes accept the customer's identifier, and the uuid keeps working.

**Independent test**: create a channel under a customer identifier and exercise every
route beneath that prefix with it.

- [X] T012 [US1] **Write the red assertion FIRST**, in `relay-platform/services/api/src/channels/addressing.itest.ts`: `GET /v1/channels/{an identifier nobody used}` must answer **404 with a named cause**. **It is 500 today** — measured — and it is the only assertion in this feature that can fail before a line is written.
- [X] T013 [US1] Add the scoped resolution to `relay-platform/services/api/src/db/repository.ts`: given a path segment, return the channel's key or nothing, **scoped to the repository's own `environment_id`**. **Two independent rules, which the first draft of four artifacts ran together into a contradiction.** (1) A value that cannot parse as a uuid is resolved as an identity and **the cast never happens** — that is what removes the 500. (2) For a uuid-shaped value the **identity wins a true tie**, by whichever procedure T009 chose. **Do not write "key then identity"**: that makes the key win, which is the outcome R2 rejected and which T021 asserts against.
- [X] T014 [US1] Write `relay-platform/services/api/src/channels/channel-id.pipe.ts` — an injectable `PipeTransform` taking the request-scoped `Repository`. **The scope comes from the constructor, not from a predicate somebody wrote** (4.21's mechanism). A value that resolves to nothing throws the route's 404. **No module file is edited and that was measured** (R4): a param-level pipe is instantiated from the module's injector without being in `providers`. **What must be resolvable is `Repository`, which already is a provider in all three** — assert that rather than assume it, because it is what a future module split would quietly break.
- [X] T015 [US1] Apply the pipe to all **7** `@Param("channelId")` sites in `relay-platform/services/api/src/channels/channels.controller.ts`. **Seven, not eight** — counted from the decorators at analysis pass 1, where three artifacts said eight and reached a total of fourteen while calling it thirteen.
- [X] T016 [US1] Apply it to all **5** sites in `relay-platform/services/api/src/messages/messages.controller.ts`. **The `:channelId` token stays** — renaming it would touch every `@Param` string twice and the documentation is where the name changes.
- [X] T017 [US1] Apply it to the read-position route in `relay-platform/services/api/src/users/users.controller.ts`, which mixes both conventions in one path today.
- [X] T017a [US1] **Boot the composed api and make one request to each of the three controllers** before asserting anything. **Not to check three edits happened — there are none — but because whether the pipe resolves is a property of each module's own injector**, and the compiler, the typechecker and the linter all accept its absence. R4's case `C` is the failure this would catch, by name.
- [X] T018 [US1] **Assert all 13 routes with the customer's identifier, per route rather than in aggregate** (SC-001). A loop that reports one number hides which route regressed.
- [X] T019 [US1] **Assert all 13 with the uuid, the same way** (SC-002, FR-002). **This is 173 existing call sites' insurance** and the reason R2 chose a shape test: a uuid takes the path it takes today.
- [X] T020 [US1] **Assert no input produces a 5xx, in any path parameter** (SC-003): a malformed value, an absent identifier, an absent uuid, and one belonging to another tenant — on every route. **Include a percent-encoded slash and a percent sign**, which are legal in a 255-character `external_id` and were only ever a request body before. **The 500 is the chapter's subject and a single route's fix is not the claim.**
- [X] T020b [US1] **Validate `:messageId` on the three routes that take one**, which closes 058-3 rather than documenting it. `PATCH` and `DELETE …/messages/{messageId}` and `GET …/messages/{messageId}/edits` hand a second path parameter to `messages.id`, a uuid column with **no shape check** (`repository.ts:6034`), so a valid channel identifier plus `messages/not-a-uuid` is a **500** today. **Follow `media/media.controller.ts:60`'s precedent exactly** — an inline `z.uuid().safeParse` throwing `protocolError("invalid_request", "messageId must be a uuid", 400, "messageId")`, and **not `ZodValidationPipe`**, whose `field` comes from the zod issue's `path`, which is empty for a scalar and then omitted: the reuse would answer 400 without saying which parameter was wrong. **All three are in `messages.controller.ts`, which the chapter is already editing**, so the fence bill gains no file.
- [X] T020c [US1] **Assert all three answer 400 with `field: "messageId"`**, and that a well-formed but absent message id still answers 404 — the control that makes it a claim about the SHAPE rather than about the id being unknown, which is how 058-3 measured it in the first place.
- [X] T020d [US1] **Repair `media/media.controller.ts:48–54`'s comment, which this chapter falsifies.** It reads *"a caller-triggered 500 on sixteen shipped routes, thirteen taking `channelId` and three taking `messageId` … the other sixteen are recorded in `gaps.md` with their measurement rather than repaired here."* After this chapter there are none. **2 fence pages, 0 appendix blocks** — the file is published and must join T005's bill. 4.19's rule: a comment true when it was written and false now is a repair; 4.20's other half: one still accurate is left alone.
- [X] T020a [US1] **Assert the two refusals the pipe REORDERS, rather than discovering them at T023.** Measured: `@Param("channelId")` sits at index 0 in all 13 signatures and Nest runs the HIGHER index first, so every `@Body`/`@Query` 400 still wins — that one is unchanged and worth an assertion saying so. **The one that does move**: `GET /v1/channels/{absent}` with a user token whose external id has no row is `400 "unknown user"` today (`channels.controller.ts:126`) and `404` after the pipe. Decide it, record it under FR-009, and assert whichever answer is chosen.
- [X] T021 [US1] **Assert the collision**, which is constructed rather than observed: a channel whose `external_id` is another channel's uuid. **0 of 41,772 have one.** The identity wins — **this is the assertion T013 must be written against, not the other way round.**
- [X] T022 [US1] **Assert tenancy twice** (SC-004): the same identifier in two environments resolves to the caller's own, and a uuid belonging to another tenant answers 404 **indistinguishably from absent** once `request_id` is stripped (4.11's rule).
- [X] T023 [US1] **Check FR-009 per action**: re-run `channels`, `messages`, `membership` and `users` suites **unedited**, and the api integration lane. **173 call sites are the regression surface** and this is what measures it.

---

## Phase 4: User Story 2 — the internal key stops reaching the customer (P2)

**Goal**: nothing a customer receives carries an identifier they cannot use.

- [X] T023a [US1] **Measure what the resolution costs** (SC-011): the added scoped `SELECT` per route, with and without the pipe, on at least a read and a write. **The handler's own `getChannelById` / `channelExists` / `channelVisibleTo` is NOT replaced** — the resolution is a second round trip, and the ordering probe showed it fires even on requests refused for a bad body. Publish the figure; every other Part 4 chapter priced its instrument.

- [X] T026 [US2] **FIRST, AND THE PHASE DEPENDS ON IT: sweep what the user surface returns and count the internal keys** (SC-006). Enumerate every response shape a customer can reach — not every repository method — and state the number **including when it is zero**. **The first entry is already measured and the count is not zero** (R5, pass 6): **367 users carry `external_id = 'erased:' || id::text`** and **290 messages in readable history return it as `user`** — a `users.id` in the field FR-USR-01 reserves for the customer's string. **So this task finds what ELSE there is**, not whether there is anything. Other starting points: `users.id` is selected at eight sites in `repository.ts`, all read so far internal; the channel listing's `last_message.user.id` is a user **external** id; `upsertUser`'s row carries `id` that the service strips. **Pass 3 read the code with the lane down and concluded zero — a reading is not a measurement, and it was wrong by 367 rows.** The channel create still returns `id`, which is now information a customer may keep and no longer must.
- [X] T024 [US2] **Only if T026 found something**: close it, and if that means changing an opaque token, take T008's compatibility path. **An empty sweep closes this task with its count, not with an invented edit.**
- [X] T025 [US2] **Only if T024 changed a token**: assert one issued before this chapter either works or is refused by name — **never a silently wrong page**. Construct the old payload by hand; a test that only round-trips the new one cannot see this.
- [X] T026a [US2] **Amend ADR-37 in BOTH homes regardless of what the sweep finds** (FR-010) — `docs/05-sad.md:747` and the argument in `docs/06-adr-deep-dives.md`. Its reversal condition names *"the `GET /v1/users` listing cursor"* as its one live edge and **there is no such route**; the cursor that exists carries a channel uuid every one of the 13 routes accepts. **Replace it with the real one rather than claiming none** (R5): **367 users carry `erased:<users.id>` and 290 retained messages return it as `user`.** ADR-37's own argument disposes of it — a key into an erased row names nobody, and the reversal condition asks whether `users.id` becomes resolvable **to a person**. **An exception a reader can check beats a claim of none**, and this one is a query. 4.5's rule — an ADR lives in two documents and ten passes amended only the summary.

---

## Phase 5: User Story 3 — the rule, written down (P3)

- [X] T027 [US3] **Add FR-CHN-11 to `docs/04-srs.md` — a NEW clause, not an amendment**: a channel is addressed by the identifier the customer supplied, and the Relay identifier is also accepted. **Nothing in the SRS says a channel can be named by its customer identifier** — FR-CHN runs 01 to 10, 01 is creation, 02 is idempotent creation, 08 is listing, and none of them covers addressing (analysis pass 7). **So this is new behaviour with no requirement, which constitution VI's first bullet forbids**, and widening a creation clause to carry a retrieval rule is the wrong repair. **FR-CHN-11, because identifiers are never reused** and the family tops out at 10. **Write it BEFORE T013 is merged**, and T009 decides whether the tie-break joins it.
- [X] T028 [P] [US3] Write `specs/068-chapter-4-22/clauses.md`: FR-USR-01, FR-CHN-01/02/08, **FR-CHN-11** and ADR-18, each **met / demonstrated / unmet by decision / unreachable**, with where. **CON-04 was on this list and is about timestamps** — *"stored and transmitted in UTC, RFC 3339 format, with millisecond precision"* — so it is struck rather than answered. CON-06 is passwords; **no CON clause bears on who owns an identifier**, and the two that do are already here.
- [X] T029 [US3] Record the rule a future noun needs: **a noun with a customer-supplied identifier is addressed by it; a noun with only a Relay identifier is addressed by that.** Name the four nouns the second half covers and why — they have no `external_id` column, measured.

---

## Phase 6: The probes

- [ ] T030 **Delete the tenancy scope from the resolution and re-run** both the addressing suite and `gauntlet.itest.ts`, recording which turn red (SC-005). **4.21 found three of four scoped arms invisible to a single-mutation probe** — if nothing goes red, the missing thing is a test.
- [ ] T031 **Add the gauntlet attack for the new form** in `relay-platform/services/api/src/isolation/gauntlet.itest.ts`: another tenant's channel identifier must not resolve. Constitution VI's third bullet names that suite as gating releases, and a new way to name a channel is a new way to name somebody else's. **This file is 13 fence pages and 8 appendix blocks** — three bills in a row omitted it, and T005 now carries it.
- [ ] T032 Run `python3 specs/045-part-3-rework/check-lane-scope.py` and record its **counted line**. 78 files at 4.21's close; this chapter adds one.
- [ ] T033 **Re-measure the coverage pins this chapter's edits could move**, then **probe both halves through `pnpm coverage`** — a key matching no file must be silent, an impossible pin on a real file must fire. **4.23's probe caught its own pin that way.**
- [ ] T033a **Pin `channel-id.pipe.ts` at 100 branches, which is the opposite of the usual rule, and the reason is the file.** "Pin below the measured value" exists because coverage is not reproducible run to run — `session.ts` read 87.80 and 85.36 on identical code, about one function of forty. **That argument needs a moving denominator**, and a file whose whole body is one scoped resolution does not have one. NFR-MNT-02 puts tenant isolation at 100% branches and `plan.md`'s constitution check already claims this file for that population. **If it measures below 100, the missing thing is a test and not a lower pin.** Precedent runs both ways, which is why this is written down: `repository.ts` 92, `channels.service.ts` 75, `isolation/targets.ts` 100.
- [ ] T033b **Check for the pins that are NOT there**, which a re-measure cannot see. **`channels.controller.ts` and `users.schema.ts` have no per-file entry in `vitest.coverage.config.mts`** and this chapter edits both — 7 `@Param` sites and the cursor payload. 062-12 is the precedent: 68 of 139 files unpinned, the lowest at 20.00%, found by a human comparing one chapter to another and by no instrument. Decide per file whether to add one, and record the decision either way.

---

## Phase 7: The documents

- [ ] T034 **Read all ten FR-CHN clauses and FR-USR-01 before editing any**, and record what the reading found — **including *nothing to amend* if that is the answer**. Pass 7 read 01, 02 and 08 and found the gap T027 now fills; **03 through 07, 09 and 10 have not been read by anyone on this feature**, and the reason to read them is that one of them may already say something about addressing that would make FR-CHN-11 a duplicate.
- [ ] T035 Read the clauses **beside** them while the file is open. 4.21's T041 found FR-MOD-03 one row above FR-MOD-04 and in direct tension with it, which nobody had written down.
- [ ] T036 Add revision row **1.29** to `docs/04-srs.md`. **Newest LAST** — `check-revision-order` caught 1.28 inserted before 1.27 on the first run after the edit.
- [X] T037 **If T010 decided a NEW ADR is needed, write it into BOTH homes** — the summary in `docs/05-sad.md` and the argument in `docs/06-adr-deep-dives.md`. 4.5 found an ADR lives in two documents and ten passes amended only the summary. **If none, record that as DONE with the reason.** **T026a's amendment to ADR-37 happens either way** and is not this task.
- [ ] T038 Amend `docs/05-sad.md` where this chapter changes what a section claims — **and check every sentence in the section you edit** (4.21 found three of four false). **ADR-37's block at :730–752 is the one already known to be wrong**, and T026a owns it; this task is for everything else, which includes any section asserting a channel is addressed by a uuid.
- [ ] T038a **Fix FR-USR-01's misquote inside the SRS**, which is this chapter's own central word. `docs/04-srs.md:293` is the clause — *"Relay shall not generate end-user **identities**"* — and the bot note at `:345` quotes it in quotation marks as *"end-user **identifiers**"*. **Under the note's spelling `users.id` and `channels.id` would themselves violate it**, which is the evidence for which one is wrong. One word. **It goes in with T036's revision row and not before**: an SRS edit without its revision entry is what `check-revision-order` and the governance clause exist to catch, so this is Phase 7's and was deliberately not done during analysis.
- [ ] T039 **Amend `docs/03-journey-map.md` Stage 2**, which asserts *"channel retrieval by external ID"* and cited no clause. After this chapter it has one. **That is the predicate 4.23 publishes, moving by one.**
- [ ] T040 Amend **both** Part 4 tables — `docs/12` and `docs/07`, this chapter's row, marked CLOSED and SHIPPED. **Match on the title**; this chapter's row has `—` in `docs/12`'s first column by design.
- [ ] T041 [P] Sweep `docs/` for feature-local ids **both ways**. **Use `git diff <tag> -- docs/`, not `<tag>..HEAD`** — the two-dot form reads committed state and reported a confident 0 for 4.21 while two leaked ids sat in the working tree.
- [ ] T042 Run `pnpm sync:docs` then `pnpm check:docs` from `relay-tutorial`.
- [ ] T043 [P] Write `specs/068-chapter-4-22/traceability.md` by **reading**, not grep — including what is in the feature with no requirement behind it, and the clauses deliberately not amended.

---

## Phase 8: The chapter

- [ ] T044 Register 4.22 in `relay-tutorial/lib/tutorial.ts` at `/part-4/chapter-22/the-identifier-the-customer-gave-it`. **Not a milestone**, so no `milestone-` prefix — that convention is 4.9's, 4.17's and 4.23's.
- [ ] T045 **Open on the 500** — `docs/07` §4 rule 1. The reader creates a channel with their own identifier, asks for it back, and gets an internal error. **One command, and the chapter's whole subject is in the response.**
- [ ] T046 Write the chapter at `relay-tutorial/app/(en)/part-4/chapter-22/the-identifier-the-customer-gave-it/page.mdx`, 2,000–4,000 prose words counted outside fences and tables, English only.
- [ ] T047 [P] Write the figures in that directory's `figures.ts`, passed as `code` and not `chart` — `check:figures` caught three dead diagrams `pnpm build` did not. **And check the soft count: the gate exits 0 while reporting `3 export(s) unused`**, two of them Vietnamese. An export this chapter adds and never names takes it to 4 and the gate still passes, so the figure to compare is that one and not the 326.
- [ ] T048 Write the TRAP box. The candidate is **the cast**: a reader assumes the 500 is a missing route or a bad guard, and it is Postgres refusing `'order-88412'::uuid` three layers down — **which is also why one query cannot resolve both forms.**
- [ ] T049 Write at least one `WHY` box. The candidate is **why a middleware cannot do this**: it is the cheapest design, Nest runs it before guards, and an unscoped resolution is a cross-tenant read. `docs/07` §4 rule 3.
- [ ] T050 Publish what the chapter could not do: the uuid is not retired, the 500's cause is still unlogged on every route that can produce one, the collision is constructed rather than observed, and the other four nouns have no identity to honour. **And what it DID do that its brief did not ask for**: 058-3 is closed. That gap counted sixteen routes where a malformed uuid in a path is a caller-triggered 500 — thirteen taking `channelId`, three taking `messageId`, one `mediaId` already validated at 4.12. **The pipe closes the thirteen as a side effect of never casting, and T020b closes the last three deliberately.** Publish that it was 16 and is 0, and that the chapter nearly left the last three open on a misread of its own citation (analysis pass 8). **And the larger one, which a reader on the socket finds first**: every gateway frame carries `channel: <uuid>`, the session response hands a connecting client a list of channel uuids, and a socket send goes to a door typed `z.string().uuid()`. **The lookup table is gone from REST and still there on the real-time surface** — Journey 3 Stage 5, the same journey whose Stage 1 promises zero of them. Quote `internal.ts`'s own line about `user` being the external id *"as everywhere else on this contract"*: the principle is stated there and applied to one field of two.
- [ ] T051 Write the chapter's fences. **A titled fence is a whole-body claim** (051-6); an excerpt must be untitled. 4.19, 4.20 and 4.21 each contributed **0 titled fences**.
- [ ] T052 Generate hunks from `pnpm check:fences --dump <dir>`, then diff at `-U6`. **Verify every pre-image matches exactly once before pasting**; widen only where it does not. **Strip the `--- a/` and `+++ b/` headers.**
- [ ] T053 Put every hunk in `relay-tutorial/fences/post-series.md`, **placed last**, biggest-first from T005's table.
- [ ] T053a **Create the three appendix blocks that do not exist** — `channels.controller.ts`, `users.schema.ts`, `media/media.controller.ts`. **This is not T052's dump-and-paste**, which assumes a hunk with a home: a first block needs its position chosen and its base established, and these sit at very different depths — `channels.controller.ts` was last fenced in Part 3 chapter 14, twelve chapters back. **If choosing a base turns into archaeology, publish the file whole instead** and record which of the two it took. A new source file needs nothing at all: 4.21's `erasure.ts` is fenced nowhere, so `channel-id.pipe.ts` gets no block either.
- [ ] T054 Run **all six tutorial gates** green **after** every source edit, comparing each counted line against T003's **and against T003a's four predicted deltas**. A line that moved where nothing was predicted, or held where a delta was, is the finding — **not the exit code**, which five of the seven gate scripts give you for free (055-4).
- [ ] T055 [P] Count the prose words and confirm the bound.

---

## Phase 9: The record and the close

- [ ] T056 Write `specs/068-chapter-4-22/baseline.txt` phase by phase, **in the order the measurements were taken, including the ones that were wrong first**.
- [ ] T057 [P] Write `specs/068-chapter-4-22/gaps.md`, numbered, carried ledger **re-measured**. Known carries: **the unlogged 500 cause** (new — and it is NOT 058-3's population: that gap counts routes where a malformed uuid produces a 500, and this is every route whose 500 is logged without its cause, which nobody has counted), 067-1, 067-2, 067-3, 066-1, 065-2, 063-4, 062-12, 050-8, 043-1. **And one to mark CLOSED: 058-3**, 16 routes to 0.
  **AND ONE THIS CHAPTER OPENS**: the channel create still returns `id` first. It is no longer required and it is still the first thing a reader sees.
- [ ] T058 **Rebuild the api image before the quickstart** — `pnpm build`, `docker compose --profile services build api`, `up -d --wait`. Then run `specs/068-chapter-4-22/quickstart.md` end to end and correct it in place, **recording each wrong version**. §1 and §2 are measured; **§3 and §4 are predictions**.
- [ ] T059 **Check FR-009 rather than trusting it** (SC-008): `git diff --name-only part4-ch21 --` and confirm every file is one this chapter is for. **One dot form, not `..HEAD`** — the two-dot form reads committed state, and this is the one check where uncommitted work is exactly what you are hunting (067-3, and T041 carries the same correction eighteen lines up).
- [ ] T060 Stop the composed services **by name** — `docker compose stop api gateway dispatcher media-worker`, **not `ingester`**.
- [ ] T061 Run the full lane set with nothing else against the stack, every REAL exit code with its `Cached:` line or under `--force`, compared against T002. **Compare CLASS BY CLASS**, not test by test.
- [ ] T062 **Run the sealed suite** — `pnpm test:outsider`, the form `ci.yml:360` runs — with the three environment variables exported. It was 21 of 21 at 4.21's close.
- [ ] T063 Confirm every phase was committed as it closed, **submodule before pointer**.
- [ ] T064 **Push submodules first, then the superproject** — `relay-platform`, `relay-tutorial`, root. **Confirm with the user before pushing.**
- [ ] T065 Compare the CI error set **per error** against T004's, both directions (SC-010). **If both runs are green the diff carries nothing** — say so.
- [ ] T066 If CI is red, fix the platform, then **re-dump, re-hunk and push both** — repairing a platform file invalidates the appendix hunks that publish it (060).
- [ ] T067 Tag `part4-ch22` in `relay-platform` and the superproject, annotated, on a commit CI proved green.
- [ ] T068 Write the `CLAUDE.md` entry under 067's convention — headline, measurement block, cited findings, and a one-line digest of the rest. Headroom was **56,133** at analysis pass 3; re-measure, because it has moved every time anyone looked.
- [ ] T069 **Hand off to 069 / chapter 4.23.** Its Stage 2 assertion, its T007 (four options for a lookup that now exists) and its quickstart §3 were all written against a platform where this chapter had not shipped. **Update 069's spec, research R2 and tasks to match what is now true**, and record in both features' baselines that the milestone's premise moved. **AND WARN IT OFF STAGE 5.** Journey 3's Stage 5 reaches the real-time surface (FR-RTM-05) and every frame there still carries a channel uuid, so a milestone scripting *"the order number alone, end to end"* fails at the socket for a reason this chapter deliberately did not fix. Stage 2 is the claim SC-007 makes; **4.23 must either scope its script to REST or assert the uuid at Stage 5 on purpose.** **069 does NOT reference ADR-37 or the cursor** — grepped at analysis pass 3, against `CLAUDE.md`'s claim that 4.23's reversal condition rests on it — so T026a's amendment needs no handoff. **`CLAUDE.md`'s 068 block carries the false cursor claim and is corrected there**, not here.

---

## Dependencies

```
Phase 1 (T001–T006)   baseline
      ↓
Phase 2 (T007–T011a)  BLOCKING. T011a gates the whole design: if a pipe cannot take
                      the request-scoped Repository, Phase 3 is a different shape.
                      **Answer it the way pass 2 answered R4: boot an app and send a
                      request.** Pass 1 answered the neighbouring question by
                      reasoning from a rule that was real and did not apply, and
                      prescribed three module edits that do nothing
      ↓
Phase 3 (T012–T023a)  US1 — the MVP. T012 first; it is the only red one
      ↓
Phase 4 (T026 → T024  US2 — independent of US1. T026's SWEEP RUNS FIRST and decides
          → T025,      whether T024 and T025 exist at all; T026a is unconditional,
          T026a)       because the ADR is wrong either way
      ↓
Phase 5 (T027–T029)   US3 — T027 before T013 MERGES (constitution VI bullet 1), and
                      before T013 is CODED if T009 made the tie-break a clause.
                      A Phase 3 task waiting on a Phase 5 one is what that bullet
                      asks for, not an accident
      ↓
Phases 6–9            probes, documents, chapter, close
```

**T011a is the hinge.** The entire design rests on an injectable pipe reaching a
request-scoped provider. If it cannot, the fallback is the service layer at 91 pages
and ~13 call sites, and Phase 3 changes shape. **Answer it with a running app**, not
with reasoning about scope bubbling.

## Parallel opportunities

- **Phase 1**: T003, T004 and T005 are independent.
- **Phase 3**: T015, T016 and T017 touch three different controllers — **[P] once
  T014 has written the pipe**, and not before.
- **Phase 4**: T026a is [P] with everything — it amends a document and waits on no
  measurement.
- **Phase 5**: T028 is [P].
- **Phase 7**: T041 and T043 are [P].
- **Phase 8**: T047 and T055 are [P].

## Independent test criteria

| story | independently testable by |
|---|---|
| **US1** | create a channel under a customer identifier; exercise all 13 routes with it and with the uuid |
| **US2** | sweep the user surface's response shapes, state the internal-key count, and show each one closed or recorded |
| **US3** | read the amended clauses and answer *which identifier addresses this noun* without reading code |

## MVP

**User Story 1 alone.** Thirteen routes accepting the identity is the chapter; the
cursor and the clause are what make it complete and honest.

---

## The mechanical coverage check, run and its result recorded

`grep` for each identifier: **3 of 10 FR and 8 of 10 SC cited by id.** Read rather
than grepped, **all twenty are covered in substance**:

```
FR-001 every channel route    T013–T018    FR-006 sweep and count            T026·T024
FR-002 the uuid still works   T019·T020a   FR-007 old tokens, IF any change  T008·T025
FR-003 order defined+tested   T009·T013·T021·T027             FR-008 the rule  T027·T029
FR-004 no 5xx                 T012·T020    FR-009 nothing else changes       T020a·T023·T059
FR-005 tenancy, demonstrated  T013·T022·T030  FR-010 amend what is falsified T026a·T034–T040

SC-006  T026, and the count is stated even when it is zero
SC-007  T018 asserts the GET Stage 2 needs; T069 hands the assertion to 4.23
SC-009  T054
SC-011  T023a
```

**TWENTY ALARMS, TWENTY FALSE** — 4.11's pass 10 got fourteen of the same, 4.23's got
twenty-two. **And the mechanical check would have passed on FR-006 and FR-007 while
both pointed at a leak that does not exist**, which is the limit of counting ids
rather than reading them. **The repair is not to sprinkle identifiers**: a task citing an id it does
not discharge makes the next mechanical check pass and the reading never happen.

## And one task that is not about this chapter

**T069 exists because feature 069's artifacts were written against a platform where
Stage 2 was broken.** Its spec says *"no SRS clause requires the lookup"*, its R2
prices four options for building one, and its quickstart §3 predicts a 500. **After
this chapter all three are false.** Leaving them would start the milestone from a
premise this chapter deleted — which is the failure this project names most often.
The handoff is a task, not a courtesy.
