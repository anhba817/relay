# Tasks — chapter 4.22, "The identifier the customer gave it"

**Feature**: `specs/068-chapter-4-22/` · **Plan**: [plan.md](./plan.md) ·
**Research**: [research.md](./research.md) · **Contract**: [contracts/addressing.md](./contracts/addressing.md)

**The chapter builds; 069 / chapter 4.23 verifies.** That ordering is `docs/12` §5
rule 4 and it is why this chapter exists apart from the milestone that found it.

---

## Phase 1: Baseline

- [ ] T001 Pin the lane in `specs/068-chapter-4-22/baseline.txt`: `RELAY_POSTGRES_PORT=15432`, the services up, and the row counts (`channels`, `users`, `messages`, `audit_log`). **Record them beside every later timing** — they are part of the instrument.
- [ ] T002 Record every lane's opening exit code, **each with its `Cached:` line and elapsed time, or under `--force`**. Feature 069's T002 opened with **all three lanes FULL TURBO** — `Cached: N of N`, 10ms, every counted line replayed. **`turbo run lint` is not a task**; the root task is `lint:root`.
- [ ] T003 Run all six tutorial gates from `relay-tutorial` and record each counted line. At 069's Phase 1: `check:fences` **291 files across 64 chapters**, `check:figures` **326 figures**, `check:docs` 29 revisions to 1.28.
- [ ] T004 Capture the CI error-set baseline for the per-error comparison at close (SC-010). 069's T004 read **0 distinct errors** on a green run; an empty diff between two green runs carries nothing and the record should say so.
- [ ] T005 **Re-derive the fence bill** rather than copy R6's. R6 says **88 pages across 10 hunks across 6 files** — the figure moved to 107/14/9 at analysis pass 1 and back at pass 2, which measured that the pipe needs no module registration; 069's T005 found two of its inherited figures already stale by one hunk each. `grep -rl 'title="[^"]*<file>"' app/ fences/` is the instrument.
- [ ] T006 **Re-measure R1–R3 before trusting them**: the 500 on `GET /v1/channels/{externalId}`, the `invalid input syntax for type uuid` from Postgres, both lookups' buffers and timings, **0 of 41,768** uuid-shaped external ids, and the **157** call sites. They were taken on 2026-10-05 and the lane moves.

---

## Phase 2: The decisions (BLOCKING)

- [ ] T007 **Decide what replaces `users.id` in the listing cursor** in `specs/068-chapter-4-22/baseline.txt`, with the losing argument written out. A keyset tiebreak must be unique and ordered. `external_id` is both **within an environment**, and the cursor is already environment-scoped — a candidate, not a conclusion. **Price the alternative**: keep the uuid and accept that ADR-37's reversal condition stays live.
- [ ] T008 **Decide the cursor's compatibility path** (FR-007). A cursor issued before this chapter must keep working or be refused by name. Two shapes: a **version field** in the payload, or a **dual-read** that accepts either. **A silently wrong page is the forbidden outcome** — a cursor the new reader misinterprets skips or repeats rows and the caller cannot see it.
- [ ] T009 **Decide whether the tie-break is a clause or a comment.** R2 chose identity-wins. **Constitution VI's first bullet says new behaviour gets a requirement first**, and "which identifier wins when both could match" is behaviour a customer can observe. If it is a clause, T034 writes it before T013 is coded.
- [ ] T010 **Decide whether this chapter needs an ADR**, and record the reasoning either way. Predicted **yes**: *which identifier addresses a noun* has a reversal condition, will be cited by every future table carrying a customer identifier, and extends ADR-18 from users to channels. **4.21's plan predicted no and was wrong; 4.23's predicted yes.** A prediction is worth nothing without the check.
- [ ] T011 **Check the plan's premise by reading, not grepping.** Open `channels.controller.ts`, `messages.controller.ts`, `users.controller.ts`, `users.schema.ts` and the repository methods behind each, and confirm the 13 `@Param` sites and what the pipe must return. **065's T007 said fourteen sites and the real number was five, because a grep counts mentions.**
- [ ] T011a **Confirm an injectable pipe can take the request-scoped `Repository`** — by writing the smallest one that compiles and boots, not by reasoning about Nest's scope bubbling. **`MediaModule` declared a service it did not provide, compiled, typechecked, linted, and failed at the first request** (4.10). **Only a running app answers this.** R4's probe got a request-scoped dependency into a param-level pipe and read it back through a real request — **so what is left is the real `Repository`, not the shape.**

---

## Phase 3: User Story 1 — the identifier works on every channel route (P1) 🎯 MVP

**Goal**: thirteen routes accept the customer's identifier, and the uuid keeps working.

**Independent test**: create a channel under a customer identifier and exercise every
route beneath that prefix with it.

- [ ] T012 [US1] **Write the red assertion FIRST**, in `relay-platform/services/api/src/channels/addressing.itest.ts`: `GET /v1/channels/{an identifier nobody used}` must answer **404 with a named cause**. **It is 500 today** — measured — and it is the only assertion in this feature that can fail before a line is written.
- [ ] T013 [US1] Add the scoped resolution to `relay-platform/services/api/src/db/repository.ts`: given a path segment, return the channel's key or nothing, **scoped to the repository's own `environment_id`**. R2's order: **parses as a uuid → key then identity; otherwise identity only, and the cast never happens.** That last clause is what removes the 500.
- [ ] T014 [US1] Write `relay-platform/services/api/src/channels/channel-id.pipe.ts` — an injectable `PipeTransform` taking the request-scoped `Repository`. **The scope comes from the constructor, not from a predicate somebody wrote** (4.21's mechanism). A value that resolves to nothing throws the route's 404. **No module file is edited and that was measured** (R4): a param-level pipe is instantiated from the module's injector without being in `providers`. **What must be resolvable is `Repository`, which already is a provider in all three** — assert that rather than assume it, because it is what a future module split would quietly break.
- [ ] T015 [US1] Apply the pipe to all **7** `@Param("channelId")` sites in `relay-platform/services/api/src/channels/channels.controller.ts`. **Seven, not eight** — counted from the decorators at analysis pass 1, where three artifacts said eight and reached a total of fourteen while calling it thirteen.
- [ ] T016 [US1] Apply it to all **5** sites in `relay-platform/services/api/src/messages/messages.controller.ts`. **The `:channelId` token stays** — renaming it would touch every `@Param` string twice and the documentation is where the name changes.
- [ ] T017 [US1] Apply it to the read-position route in `relay-platform/services/api/src/users/users.controller.ts`, which mixes both conventions in one path today.
- [ ] T017a [US1] **Boot the composed api and make one request to each of the three controllers** before asserting anything. **Not to check three edits happened — there are none — but because whether the pipe resolves is a property of each module's own injector**, and the compiler, the typechecker and the linter all accept its absence. R4's case `C` is the failure this would catch, by name.
- [ ] T018 [US1] **Assert all 13 routes with the customer's identifier, per route rather than in aggregate** (SC-001). A loop that reports one number hides which route regressed.
- [ ] T019 [US1] **Assert all 13 with the uuid, the same way** (SC-002, FR-002). **This is 157 existing call sites' insurance** and the reason R2 chose a shape test: a uuid takes the path it takes today.
- [ ] T020 [US1] **Assert no input produces a 5xx** (SC-003): a malformed value, an absent identifier, an absent uuid, and one belonging to another tenant — on every route. **The 500 is the chapter's subject and a single route's fix is not the claim.**
- [ ] T021 [US1] **Assert the collision**, which is constructed rather than observed: a channel whose `external_id` is another channel's uuid. **0 of 41,768 have one.** The identity wins, and the other channel stays reachable by its uuid.
- [ ] T022 [US1] **Assert tenancy twice** (SC-004): the same identifier in two environments resolves to the caller's own, and a uuid belonging to another tenant answers 404 **indistinguishably from absent** once `request_id` is stripped (4.11's rule).
- [ ] T023 [US1] **Check FR-009 per action**: re-run `channels`, `messages`, `membership` and `users` suites **unedited**, and the api integration lane. **157 call sites are the regression surface** and this is what measures it.

---

## Phase 4: User Story 2 — the internal key stops reaching the customer (P2)

**Goal**: nothing a customer receives carries an identifier they cannot use.

- [ ] T024 [US2] Change the listing cursor in `relay-platform/services/api/src/users/users.schema.ts` per T007, with T008's compatibility path.
- [ ] T025 [US2] **Assert a cursor issued before this chapter** either works or is refused by name — **never a silently wrong page**. Construct the old payload by hand; a test that only round-trips the new one cannot see this.
- [ ] T026 [US2] **Count what the API returns that a caller cannot use** (SC-006) and state the number. The channel create still returns `id`; decide whether that stays — it is information a customer may keep and no longer must.

---

## Phase 5: User Story 3 — the rule, written down (P3)

- [ ] T027 [US3] Amend **FR-CHN** in `docs/04-srs.md`: a channel is addressed by the identifier the customer supplied, and the Relay identifier is also accepted. **Write this BEFORE T013 is merged** — constitution VI's first bullet, and T009 decides whether the tie-break joins it.
- [ ] T028 [P] [US3] Write `specs/068-chapter-4-22/clauses.md`: FR-USR-01, FR-CHN-01/02/08, ADR-18 and CON-04, each **met / demonstrated / unmet by decision / unreachable**, with where.
- [ ] T029 [US3] Record the rule a future noun needs: **a noun with a customer-supplied identifier is addressed by it; a noun with only a Relay identifier is addressed by that.** Name the four nouns the second half covers and why — they have no `external_id` column, measured.

---

## Phase 6: The probes

- [ ] T030 **Delete the tenancy scope from the resolution and re-run** both the addressing suite and `gauntlet.itest.ts`, recording which turn red (SC-005). **4.21 found three of four scoped arms invisible to a single-mutation probe** — if nothing goes red, the missing thing is a test.
- [ ] T031 **Add the gauntlet attack for the new form** in `relay-platform/services/api/src/isolation/gauntlet.itest.ts`: another tenant's channel identifier must not resolve. Constitution VI's third bullet names that suite as gating releases, and a new way to name a channel is a new way to name somebody else's.
- [ ] T032 Run `python3 specs/045-part-3-rework/check-lane-scope.py` and record its **counted line**. 78 files at 4.21's close; this chapter adds one.
- [ ] T033 **Re-measure the coverage pins this chapter's edits could move**, then **probe both halves through `pnpm coverage`** — a key matching no file must be silent, an impossible pin on a real file must fire. **4.23's probe caught its own pin that way.** `channel-id.pipe.ts` is new and needs one; pin **below** the measured value.

---

## Phase 7: The documents

- [ ] T034 **Read FR-CHN-01, FR-CHN-02, FR-CHN-08 and FR-USR-01 before editing any**, and record what the reading found — **including *nothing to amend* if that is the answer**.
- [ ] T035 Read the clauses **beside** them while the file is open. 4.21's T041 found FR-MOD-03 one row above FR-MOD-04 and in direct tension with it, which nobody had written down.
- [ ] T036 Add revision row **1.29** to `docs/04-srs.md`. **Newest LAST** — `check-revision-order` caught 1.28 inserted before 1.27 on the first run after the edit.
- [ ] T037 **If T010 decided an ADR is needed, write it into BOTH homes** — the summary in `docs/05-sad.md` and the argument in `docs/06-adr-deep-dives.md`. 4.5 found an ADR lives in two documents and ten passes amended only the summary. **If none, record that as DONE with the reason.**
- [ ] T038 Amend `docs/05-sad.md` where this chapter changes what a section claims — **and check every sentence in the section you edit** (4.21 found three of four false).
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
- [ ] T047 [P] Write the figures in that directory's `figures.ts`, passed as `code` and not `chart` — `check:figures` caught three dead diagrams `pnpm build` did not.
- [ ] T048 Write the TRAP box. The candidate is **the cast**: a reader assumes the 500 is a missing route or a bad guard, and it is Postgres refusing `'order-88412'::uuid` three layers down — **which is also why one query cannot resolve both forms.**
- [ ] T049 Write at least one `WHY` box. The candidate is **why a middleware cannot do this**: it is the cheapest design, Nest runs it before guards, and an unscoped resolution is a cross-tenant read. `docs/07` §4 rule 3.
- [ ] T050 Publish what the chapter could not do: the uuid is not retired, the 500's cause is still unlogged on 22 routes, the collision is constructed rather than observed, and the other four nouns have no identity to honour.
- [ ] T051 Write the chapter's fences. **A titled fence is a whole-body claim** (051-6); an excerpt must be untitled. 4.19, 4.20 and 4.21 each contributed **0 titled fences**.
- [ ] T052 Generate hunks from `pnpm check:fences --dump <dir>`, then diff at `-U6`. **Verify every pre-image matches exactly once before pasting**; widen only where it does not. **Strip the `--- a/` and `+++ b/` headers.**
- [ ] T053 Put every hunk in `relay-tutorial/fences/post-series.md`, **placed last**, biggest-first from T005's table.
- [ ] T054 Run **all six tutorial gates** green **after** every source edit, comparing each counted line against T003's.
- [ ] T055 [P] Count the prose words and confirm the bound.

---

## Phase 9: The record and the close

- [ ] T056 Write `specs/068-chapter-4-22/baseline.txt` phase by phase, **in the order the measurements were taken, including the ones that were wrong first**.
- [ ] T057 [P] Write `specs/068-chapter-4-22/gaps.md`, numbered, carried ledger **re-measured**. Known carries: **the unlogged 500 cause** (new, and 058-3's 22 routes), 067-1, 067-2, 067-3, 066-1, 065-2, 063-4, 062-12, 050-8, 043-1.
  **AND ONE THIS CHAPTER OPENS**: the channel create still returns `id` first. It is no longer required and it is still the first thing a reader sees.
- [ ] T058 **Rebuild the api image before the quickstart** — `pnpm build`, `docker compose --profile services build api`, `up -d --wait`. Then run `specs/068-chapter-4-22/quickstart.md` end to end and correct it in place, **recording each wrong version**. §1 and §2 are measured; **§3 and §4 are predictions**.
- [ ] T059 **Check FR-009 rather than trusting it** (SC-008): `git diff --name-only part4-ch21..HEAD` and confirm every file is one this chapter is for.
- [ ] T060 Stop the composed services **by name** — `docker compose stop api gateway dispatcher media-worker`, **not `ingester`**.
- [ ] T061 Run the full lane set with nothing else against the stack, every REAL exit code with its `Cached:` line or under `--force`, compared against T002. **Compare CLASS BY CLASS**, not test by test.
- [ ] T062 **Run the sealed suite** — `pnpm test:outsider`, the form `ci.yml:360` runs — with the three environment variables exported. It was 21 of 21 at 4.21's close.
- [ ] T063 Confirm every phase was committed as it closed, **submodule before pointer**.
- [ ] T064 **Push submodules first, then the superproject** — `relay-platform`, `relay-tutorial`, root. **Confirm with the user before pushing.**
- [ ] T065 Compare the CI error set **per error** against T004's, both directions (SC-010). **If both runs are green the diff carries nothing** — say so.
- [ ] T066 If CI is red, fix the platform, then **re-dump, re-hunk and push both** — repairing a platform file invalidates the appendix hunks that publish it (060).
- [ ] T067 Tag `part4-ch22` in `relay-platform` and the superproject, annotated, on a commit CI proved green.
- [ ] T068 Write the `CLAUDE.md` entry under 067's convention — headline, measurement block, cited findings, and a one-line digest of the rest. Headroom was **56,799** after the plan.
- [ ] T069 **Hand off to 069 / chapter 4.23.** Its Stage 2 assertion, its T007 (four options for a lookup that now exists) and its quickstart §3 were all written against a platform where this chapter had not shipped. **Update 069's spec, research R2 and tasks to match what is now true**, and record in both features' baselines that the milestone's premise moved.

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
Phase 3 (T012–T023)   US1 — the MVP. T012 first; it is the only red one
      ↓
Phase 4 (T024–T026)   US2 — independent of US1
      ↓
Phase 5 (T027–T029)   US3 — T027 before T013 merges (constitution VI bullet 1)
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
- **Phase 5**: T028 is [P].
- **Phase 7**: T041 and T043 are [P].
- **Phase 8**: T047 and T055 are [P].

## Independent test criteria

| story | independently testable by |
|---|---|
| **US1** | create a channel under a customer identifier; exercise all 13 routes with it and with the uuid |
| **US2** | page the user listing; decode the cursor and find nothing a caller cannot use |
| **US3** | read the amended clauses and answer *which identifier addresses this noun* without reading code |

## MVP

**User Story 1 alone.** Thirteen routes accepting the identity is the chapter; the
cursor and the clause are what make it complete and honest.

---

## The mechanical coverage check, run and its result recorded

`grep` for each identifier: **3 of 10 FR and 8 of 10 SC cited by id.** Read rather
than grepped, **all twenty are covered in substance**:

```
FR-001 every channel route    T013–T018    FR-006 nothing unusable returned  T024·T026
FR-002 the uuid still works   T019         FR-007 old cursors                T008·T025
FR-003 order defined+tested   T009·T021·T027  FR-008 the rule written        T027·T029
FR-004 no 5xx                 T012·T020    FR-009 nothing else changes       T023·T059
FR-005 tenancy, demonstrated  T013·T022·T030  FR-010 amend what is falsified T034–T040

SC-007  T018 asserts the GET Stage 2 needs; T069 hands the assertion to 4.23
SC-009  T054
```

**TWENTY ALARMS, TWENTY FALSE** — 4.11's pass 10 got fourteen of the same, 4.23's got
twenty-two. **The repair is not to sprinkle identifiers**: a task citing an id it does
not discharge makes the next mechanical check pass and the reading never happen.

## And one task that is not about this chapter

**T069 exists because feature 069's artifacts were written against a platform where
Stage 2 was broken.** Its spec says *"no SRS clause requires the lookup"*, its R2
prices four options for building one, and its quickstart §3 predicts a 500. **After
this chapter all three are false.** Leaving them would start the milestone from a
premise this chapter deleted — which is the failure this project names most often.
The handoff is a task, not a courtesy.
