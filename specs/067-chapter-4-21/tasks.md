# Tasks — chapter 4.21, "Erasure, and every path it must find"

**Feature**: 067 · **Spec**: [spec.md](./spec.md) · **Plan**: [plan.md](./plan.md)
**Research**: [research.md](./research.md) · **Contract**: [contracts/erasure.md](./contracts/erasure.md)

**COMMIT AT EVERY PHASE BOUNDARY, SUBMODULE BEFORE POINTER.** `git add -A` from
the superproject stages a gitlink, not the submodule's working tree — feature
065 produced three phase commits carrying only specs that way, and 066 reproduced
the check rather than the defect. `git -C relay-platform log --oneline -1` is the
check.

---

## Phase 1: Setup and measurement

**Purpose**: every number this chapter is compared against, taken before
anything changes. All append to one file, so none is parallel however
independent the measurement is.

- [X] T001 Pin the lane environment in `specs/067-chapter-4-21/baseline.txt` — compose services, `RELAY_POSTGRES_PORT=15432`, node and Postgres and ClickHouse versions, and the row counts that make a lane an instrument: `users`, `members`, `messages`, `media_objects`, `usage_active_users`, and **the outbox**, which feature 065 found is now large enough to fail a suite on its own (`gaps.md` 065-5, re-measured at 400,697 by 066).
- [X] T002 Record every lane's REAL exit code in `specs/067-chapter-4-21/baseline.txt` — `pnpm lint`, `pnpm exec turbo run typecheck`, `pnpm test`, the api `test:integration` lane, `pnpm coverage` — **with the `Cached:` line and the elapsed time beside each**. Chapter 4.20 measured `pnpm test` answering **EXIT 0 with every counted line in 17 ms and `Cached: 13 of 13`** — nothing ran. **055-4's *assert the counted line, not the exit code* is necessary and NOT sufficient against a cache**, because turbo replays the line from it. Run under `--force` or quote `Cached:`. Capture `$?` **outside** the pipeline.
  **AND KEEP THE FULL LOG OF ANY RED LANE.** 065's first attempt grepped each log for its counted line and deleted the rest, which is enough for a green lane and useless for a red one. **The api lane was red at 066's open** with two pre-existing classes — `outbox.itest.ts` invariant 8 and the quotas drain pair — and the second went green with nobody working on it. Expect neither and record both.
  **`pnpm lint` IS `turbo run //#lint:root`**, not `turbo run lint`: the latter exits 1 in 0.20 s with `Could not find task 'lint'`, which is indistinguishable from a red lane except by the elapsed time.
- [X] T003 Record `check:fences` in `specs/067-chapter-4-21/baseline.txt` as an **absolute number**, not a delta (055's rule). A clean run prints no problem line, so assert the `replay onto` line. It was **291 files across 63 chapters, 0 problems** at 066's close.
- [X] T003a **Record all six tutorial gates by name**, run from `relay-tutorial`, each **outside a pipe** with its **counted line** quoted: `pnpm lint`, `pnpm build`, `pnpm check:docs`, `pnpm check:srs`, `pnpm check:figures`, `pnpm check:fences`. **Read the list off `ci.yml`, not off memory**; `check:errors` is not one of them — it runs by path from the lanes job (062's correction to 055-3).
- [X] T004 Record the CI baseline in `specs/067-chapter-4-21/baseline.txt`: the last pushed run's four job conclusions and its `##[error]` set, normalised. **The current baseline is an empty set** — run 37199508332 at 066's close, four green jobs, 0 error lines — which cannot be matched by introducing something and removing something else.
- [X] T005 **Re-run the premise against the platform, not against `research.md`.** Re-measure R1's four stores, R2's two sketch figures and R3's two deletion verbs, each with its control, and record in `specs/067-chapter-4-21/baseline.txt`. *An artifact agreeing with another artifact is what fifteen analysis passes found in 4.9.*
  **AND THE CLICKHOUSE DATABASE IS `relay_analytics`, NOT `relay`.** A query against `relay` returns an empty result that reads as *no such column* rather than *no such database*. Chapter 4.2 spent eight analysis passes measuring the wrong one.
- [X] T006 **Count the fence bill against the tree**, from `relay-tutorial`: `grep -rl 'title="<path>"' app/ fences/` and `grep -c` in `fences/post-series.md` for `repository.ts`, `schema.ts`, `vitest.coverage.config.mts`, `targets.ts`, `gauntlet.itest.ts` and **`users.controller.ts`**. `research.md` R6 has **52 / 34 / 23 / 13 / 13 / 4 pages** and **6 / 6 / 17 / 5 / 7 / 0 appendix hunks** to check against. **`app.module.ts` is NOT in the bill** — it was, until analysis pass 1 found the route joins an existing controller, which took 23 pages and 4 hunks off it.
  **R6 WAS WRONG BEFORE IT WAS RIGHT, WHICH IS WHY THIS TASK STILL EXISTS.** A first draft carried the hunk counts from the shape of chapter 4.20's bill and was wrong in five of six places; the pages were right. **A count taken from a pattern is not a count.** Count the rest of the isolation family too — `attack.ts`, `targets.itest.ts`, `attack.test.ts` — because a new route touched four files in that directory at 4.18.
- [X] T007 Record where a user is named, in `specs/067-chapter-4-21/baseline.txt`: the seven Postgres sites and the five analytical ones from `data-model.md`, each with a row count and what erasure can do to it. **This is SC-012's open figure** and T063a re-measures it at the close.
- [X] T008 Record the media linkage in `specs/067-chapter-4-21/baseline.txt`: **3,979 objects with a `user_id` and 11,050 without**, DR-15's `{environment_id}/{media_id}` key verified against real keys, and that there is no user in the path. **A user's objects are not a prefix and never were.**
- [X] T009 Record what `deleteUser` already does, quoting its own comment: **what goes, what stays, and the billing argument for `usage_active_users`.** This is the chapter's central conflict and the quotation is the evidence.

---

## Phase 2: Foundational — the decisions, before any route

**Purpose**: the two decisions with a clause on each side, settled before code
exists. The alternative is a spec question with a route already shipped.

- [X] T010 **Decide whether erasure destroys the user's MESSAGES** in `specs/067-chapter-4-21/baseline.txt`. FR-MOD-04 says *messages*; FR-USR-05 preserves them *"unless message deletion is explicitly requested"* and FR-MOD-04 is arguably that request. Against: a channel's history losing every message one participant sent is visible to everyone else in it, and `deleteUser`'s comment records that *"authored by a deleted user" and "authored by nobody" are different states.* **Record the argument both ways and name which clause the chapter is choosing to satisfy.**
- [X] T011 **Decide whether erasure destroys `usage_active_users`** in `specs/067-chapter-4-21/baseline.txt`. **22,150 rows naming 22,147 users**, kept on purpose by FR-029: *"a customer who deleted a user in March still owes for March."* FR-MOD-04 calls it an analytical record. **This is the strongest counter-argument in the platform to the clause's own wording** and there is money on one side. If it is kept, FR-MOD-04 is partly unmet and the SRS needs amending; if it is erased, an invoice loses its basis.
- [X] T012 **Decide the receipt's shape** in `specs/067-chapter-4-21/baseline.txt` and amend `contracts/erasure.md` if it moves. Four outcomes, and the decision to record is **why `nothing_to_erase` and `cannot_erase` must not collapse**: 205,697 rows that never named a person against 880 that do, unremovably.
- [X] T013 **Decide the route's shape**: `DELETE /v1/users/{externalId}/data` rather than `DELETE /v1/users/{externalId}`, because the second is FR-USR-05's deletion and already exists with the opposite semantics. **Two verbs that differ only in what they preserve must not differ only in a flag** — a mistyped one would be an irreversible erasure.
- [X] T013a **Decide whether this chapter needs an ADR**, and record the reasoning either way. `plan.md` says *probably not* because ADR-36 already named FR-MOD-04's endpoint as one of two compliance paths — **and chapter 4.20's plan predicted an ADR and was right, so a prediction here is worth nothing without the check.** Constitution VII requires one for every architecture decision; the live candidate is what erasure means for a store that cannot erase.
- [X] T014 **Decide the ClickHouse deletion verb** in `specs/067-chapter-4-21/baseline.txt`, with R3's measurement beside it. `DELETE FROM` is visible to the next `SELECT`; `ALTER TABLE … DELETE` **returned with its hundred rows still countable**. **A receipt states a count, so it uses the verb whose count it can trust.**
- [X] T014a **Check T013's premise by reading, not by grepping.** Open every file the route touches — **`users.controller.ts` and `users.module.ts`**, `targets.ts`, `moderation-routes.ts`, `users.schema.ts` — and confirm what adding this route actually costs. **`app.module.ts` is NOT on the list any more** (T020), which is the kind of thing a plan carried across from the chapter before it and a reading corrects. 065's T007 said fourteen `MessageRow` sites and the real number was five, because a grep counts mentions.

---

## Phase 3: User Story 1 — a tenant erases an end user (P1) 🎯 MVP

**Goal**: one route that removes a user from every store that can remove them.

**Independent test**: create a user with messages, memberships, a profile and an
uploaded object; erase them; assert each store no longer identifies them.

- [X] T015 [US1] **Write the red probe FIRST**, in `relay-platform/services/api/src/users/erasure.itest.ts` — **a new file in the EXISTING `users/` directory, not a new module**, see T020. **Assert that the `users` row CANNOT BE DELETED while its children exist**, and pair it with a control. Measured at analysis pass 3:

      DELETE FROM users WHERE id = <one with memberships>
        ERROR: violates foreign key constraint "members_user_id_users_id_fk"
      DELETE FROM users WHERE id = <one with no children anywhere>
        DELETE 1                                       <- the control

  All five foreign keys to `users` are `NO ACTION`, so the row is unreachable until every child is gone — which is exactly what T016's *children first, the row last* exists to traverse. **The control is what makes the refusal mean the keys rather than a broken call.**
  **AND THE FIRST DRAFT OF THIS TASK ASSERTED SOMETHING THAT COULD NEVER FLIP.** It called `deleteUser` and asserted what survives — the row, the messages, the billing rows — which this chapter **preserves on purpose**, because erasure is a separate verb. That probe would have been green at the open, green after the traversal and green at close-out, and read as evidence three times. **A probe that was never green proves nothing about the fix, and a probe that can never go red proves nothing either.**
- [X] T016 [US1] Add the erasure traversal to `relay-platform/services/api/src/db/repository.ts` in `data-model.md`'s order. **CHILDREN FIRST, THE ROW LAST** — all five foreign keys to `users` are `NO ACTION`, so the row cannot go until they do, which makes the order a correctness property rather than a preference.
  **AND READ THE EXTERNAL ID BEFORE DELETING THE ROW THAT HOLDS IT.** `connection_events` keys on `user_external_id` and the Postgres row is gone by then — the same ordering trap chapter 4.20 hit with `media_id` values that vanish with the messages naming them.
- [X] T017 [US1] Collect the user's `media_id` values **before** any deletion, then destroy the attributed objects, their renditions and their stored bytes — **reusing chapter 4.20's `destroyMediaObjects` and `deleteObjectWithRenditions`.** **THIS IS ENFORCED, NOT PREFERRED**: `rendition.itest.ts:282` asserts `toHaveLength(1)` on row-deletion paths — chapter 4.15 wrote it as `toHaveLength(0)` and 4.20 moved it to 1 when it created the first — so **a second `delete(mediaObjects)` turns it red**, with the message *"row-deletion paths changed … Wire deleteObjectWithRenditions into the new one."* The companion assertion requires more than one caller of the byte deletion, so this chapter adding one is expected.
- [X] T018 [US1] Publish the `deleted` storage event for every object destroyed, with a **negative** `bytesDelta`, via `publishStorageDelta`. Chapter 4.20 wired the first caller; this is the second. **The operational quota self-corrects and the analytical meter does not**, which is why this is easy to skip and expensive to skip.
- [X] T019 [US1] Add the ClickHouse erasure for `connection_events` in **`relay-platform/services/api/src/users/`**, which is where this platform puts ClickHouse code — `metering/`, `request-log/` and `audit/` each hold their own and **`db/` holds none**. A first draft put it in `db/` citing `eslint.config.mjs`; that rule restricts **`drizzle-orm`, `ioredis` and `pg`** and says nothing about a ClickHouse client, so the stated reason was wrong and the placement with it.
  **AND THE STATEMENT MUST USE BOUND PARAMETERS, NOT INTERPOLATION (T019a).** This is the one that matters.
  **SCOPE IT BY `environment_id` AS WELL AS BY `user_external_id`, AND TAKE THE ENVIRONMENT AS A PARAMETER.** External ids are unique per environment, not globally: **1,576 are reused across environments in `users`**, and in `connection_events` **23 of 54 span more than one**. Measured on the worst — `tuan`, in **111 environments** — an unscoped delete removes **152 rows from 110 other tenants** and 4 correctly, **97.4% wrong**. FR-008 requires the scope and `data-model.md` wrote the statement without it until analysis pass 2.
  **THE SIGNATURE IS THE MECHANISM HERE.** Six of the seven stores are reached through `Repository`, whose constructor requires an `environment_id`, so they are scoped by construction. **ClickHouse is the only one that class does not mediate** — constitution I's mechanism stops at exactly the boundary where the predicate went missing — so the function takes `environmentId` explicitly and `erasure.itest.ts` asserts a second tenant's identically-named user is untouched.
- [X] T019a [US1] **(FR-014) Give `AnalyticalStore` bound parameters, because the erasure interpolates a URL path value into SQL and that is an injection.** `AnalyticalStore.query` takes a SQL string and **has no parameter binding** — `request-log.module.ts:16` says so in as many words, and names `endpoint` as *"the sharpest caller-supplied value on this surface"* because 4.8 defended it with a closed derived set. **An external id has no closed set**: `users.schema.ts` accepts `z.string().min(1).max(255)`, any 255 characters.
  **MEASURED END TO END AT ANALYSIS PASS 4.** The platform accepts a user with `external_id = "ev'il OR 1=1 --"` — 201, round-tripped in the response — and interpolating that value into the scoped statement turns a count of **0 into 1,081, the whole table**. An erasure for that user would delete `connection_events` across all **460** tenant-environment pairs. It is 4.8's finding word for word: *it does not widen the window, it defeats the tenant predicate, because `OR` binds looser than the `AND` chain the scope is written in* — **and it is what defeats the `environment_id` predicate analysis pass 2 added.** The two are one surface.
  **THE REMEDY IS MEASURED AND 4.8's DOES NOT TRANSFER.** That chapter's answer was *a type, not an escape*: what left the schema was a `Date` and there was nothing to escape. A free-text external id has no such type. ClickHouse's HTTP interface takes `param_<name>` query parameters against `{name:Type}` placeholders, and it works:

      bound, with ev'il OR 1=1 --     ->  0        (interpolated: 1,081)
      bound, with `tuan` scoped       ->  4        the control

  **Extend the interface rather than escaping at the call site** — an escape is a thing every future caller must remember and this platform has deleted hand-maintained tables for less. **T013a's ADR question now has a live candidate**: this is a capability added to a shared client, not a line in one function.
- [X] T020 [US1] **Add the route to the EXISTING `relay-platform/services/api/src/users/users.controller.ts`**, beside `@Delete(":externalId")`. **Not a new module** — `plan.md` and `contracts/erasure.md` assumed one by carrying chapter 4.20's shape across, and that chapter needed a module because `v1/environments` had no controller at all. This one does.
  **MEASURED AT ANALYSIS PASS 1, AND THE BILL DIFFERS BY 19 PAGES.** `users.controller.ts` is **4 pages with 0 appendix hunks**; a new module would edit `app.module.ts` at **23 pages with 4 hunks already**, and add a second `@Controller("v1/users")` on the same prefix. **The existing class already carries all three decorators the plan specified** — `@Controller("v1/users")`, `@UseGuards(CredentialGuard)`, `@Accepts("application")` — so the route inherits them and no registration is needed.
  **AND THE BILL IS NOT THE MAIN ARGUMENT.** `contracts/erasure.md`'s central worry is that erasure and FR-USR-05's deletion must not be confused, because *"two verbs that differ only in what they preserve must not differ only in a flag."* **Two `DELETE`s side by side in one file make that distinction more visible than two files do**, and the next reader meets both at once.
- [X] T020a [US1] **Record constitution VI's fifth bullet as NOT ENGAGED by this route, with the measurement.** The route is a `DELETE` taking one path parameter and no body, so there is no input to validate and nothing for `z.strictObject` to be strict about. Measured at analysis pass 3 against the existing bodyless `DELETE /v1/users/:externalId`: a body of `{"totally":"unknown"}` and a body of `{}` both answer **404** — identical, because no `@Body()` decorator exists to parse either.
  **ADDING ONE PURELY TO REJECT WOULD BE WORK WITH NO CLAUSE BEHIND IT.** The bullet governs endpoints that take input; chapter 4.20's route was a `PATCH` with a body and the sentence was carried across to a route without one. **Assert instead that the route declares no `@Body()`**, which is the property that makes the bullet inapplicable rather than unmet.
- [X] T021 [US1] **Run T015's probe again and watch it go red**, then invert it: with the traversal in place the same user's row deletes cleanly, because the children went first. Record both states in `specs/067-chapter-4-21/baseline.txt`.
  **AND ADD THE CHARACTERISATION TEST THE FIRST DRAFT OF T015 WAS REACHING FOR**, which is worth having for a different reason: `deleteUser` keeps the row, the messages and the `usage_active_users` rows, and **erasure does not**. Assert both in one test, side by side. It is green today and green forever — its value is that it goes red the day somebody collapses the two verbs into one, which is the confusion `contracts/erasure.md` exists to prevent.
- [X] T022 [US1] Assert the per-store outcome in `relay-platform/services/api/src/users/erasure.itest.ts`: after erasure, a count of rows naming the user is **zero** in every operational store that can remove them, counted **absolutely** rather than as a delta.
- [X] T023a [US1] **(SC-014) Erase a user whose external id is `ev'il OR 1=1 --` and assert every other tenant's `connection_events` rows survive.** Create the user — the platform accepts it, 201 — give it a connection event, and count the table before and after. **Interpolated the count goes to 0 from 1,081; bound it goes to 1,080.** This is the only assertion that distinguishes a scoped statement from one that merely looks scoped.
- [X] T023 [US1] Assert FR-008's tenancy **twice, because the route and the statements fail differently**. (a) An external id belonging to another tenant answers 404, **byte-identical to one that does not exist** once `request_id` is removed. (b) **Two environments holding a user with the SAME external id**: erase one and assert the other's rows survive in **both** Postgres and `connection_events`. The second is the one the measurement demands — the route can refuse correctly while an unscoped analytical statement destroys a third party's rows, and no read-shaped assertion would see it. 4.11's rule, and chapter 4.20's route test needed exactly this correction after comparing whole bodies.
- [X] T024 [US1] Assert FR-007's idempotence: the second erasure reports **zero erased and 200**, not 404. *Two 404s prove nothing — idempotence is about what the second call DID.*
- [X] T025 [US1] Classify the new route in `relay-platform/services/api/src/isolation/targets.ts` **and** write the gauntlet attack for it, **in `relay-platform/services/api/src/isolation/gauntlet.itest.ts`** — attacks live inside that file, 13 pages with 7 appendix hunks. **THE ATTACK MUST ASK WHAT SURVIVED**: constitution I's usual failure is a leak and this one is a loss, so a forged erasure that answers 404 and deletes anyway leaves no trace in any read-shaped assertion.
- [X] T025a [US1] **Add the route's entry to `relay-platform/services/api/src/audit/moderation-routes.ts`** (FR-013). `moderation-routes.itest.ts` fails in **both** directions until it has one. **IT IS NOT A NEW JUDGEMENT AND THE FILE ALREADY CONTAINS THE ANSWER FOR THE ADJACENT ROUTE.** `"DELETE /v1/users/:externalId": "moderation"` is there, with the reason *"removes a person's profile and memberships"* — so erasure is the same judgement applied to a strictly larger action. **Model the new `ACTION` entry on `ACTION.deleteUser`**, which exists at the bottom of that file. 4.18's *standing, not data* points the same way here as it did there, and unlike chapter 4.20's policy route this actor acts directly on somebody else's data. Zero fence cost: that file is titled on 0 pages.
- [X] T025b [US1] **Write the `audit_log` entry for an erasure** (FR-013), with `target_kind: "user"` — **which is already in `audit_log_target_kind_check`**, so unlike chapter 4.20's abandoned option this costs no migration and no `schema.ts` hunk. Check that before writing it, because it is the whole reason the classification differs.
- [X] T026 [US1] **Check FR-011 per action**: re-run `users.itest.ts`, `repository.itest.ts`, `messages.itest.ts` and the member suites **unedited**, and record the result. **`repository.itest.ts` IS ON THIS LIST BECAUSE IT WALKS THE SOURCE** — its *"gives each one an actor or the named absence"* test caught chapter 4.20 constructing a `Repository` with two arguments, and this chapter constructs more.

---

## Phase 4: User Story 2 — the receipt is evidence (P2)

**Goal**: a document a compliance officer can file, naming what could not be erased.

**Independent test**: read the receipt alone, with no access to the platform, and
say which stores were cleared and which were not.

- [X] T027 [US2] Build the receipt in `relay-platform/services/api/src/users/`, per store, per `contracts/erasure.md`'s four outcomes.
  **THE ANALYTICAL COUNT IS A SECOND STATEMENT AND THE DELETE CANNOT SUPPLY IT.** Measured at pass 4 through the client's exact request shape: a `DELETE` answers **HTTP 200 with a 0-byte body**, so `query()` yields `[]`. Take the count with a bound `SELECT count()` **after** the delete — which is the real reason T014 chose the lightweight verb, because after `ALTER … DELETE` that count is still wrong.
- [X] T028 [US2] Assert that `api_requests` reports **`nothing_to_erase`** and `daily_usage` reports **`cannot_erase`**, and that the two are distinguishable in the response body. **If both say `erased: 0` the receipt has collapsed the distinction it exists to carry** — 205,697 rows that never named a person against 880 that do, unremovably.
- [X] T029 [US2] Assert the `not_reached` outcome by stopping ClickHouse and erasing a user: **the operational erasure must still commit** and the receipt must say the analytical store was not reached. Constitution III forbids rolling back a compliance erasure because a metering pipeline is unwell.
  **AND STOP IT BY NAME.** `docker compose stop clickhouse` takes a shared service away from every suite running beside it — 4.10 found an isolation suite answering 503 because a media test stopped MinIO, and `check-lane-scope.py` cannot see an ACTION scoped too wide.
- [X] T030 [US2] Assert the receipt's media note names the **73%**: an erasure that takes the 3,979 attributed objects is correct and incomplete, and the receipt is where that gets said rather than in a comment nobody reads.
- [X] T031 [US2] Assert the second erasure's receipt reports every store with zero and **200**, which is T024 read from the receipt's side rather than the status code's.

---

## Phase 5: User Story 3 — the bounds, published (P3)

**Goal**: a verdict per obligation, and nobody reads a promise into a mechanism
that does not exist.

**Independent test**: read `clauses.md` and find a verdict for each of
FR-MOD-04's four obligations and FR-MED-10's three, each with where.

- [X] T032 [P] [US3] Write `specs/067-chapter-4-21/clauses.md`: FR-MOD-04's four obligations and FR-MED-10's three, each **met / demonstrated / unmet by decision / unreachable** with where. **And FR-MOD-05 beside them**, still unbuilt — the export that would let a tenant hold a copy first, named for the third chapter running.
- [X] T033 [US3] Record in `specs/067-chapter-4-21/clauses.md` that **`within 30 days` is satisfied trivially and therefore unexercised**: the erasure is synchronous, so the bound is met and never tested. The fifth clause bounded by ADR-28's absent scheduler, and the second — after FR-MOD-06's — whose absence is a compliance promise rather than a reporting one.
- [X] T034 [US3] Record the FR-MED-10 split: **the unlink is already met** (`deleteMessage` writes `attachments: []`), **the 30-day erasure bound is this chapter's**, and **the 24-hour orphan reaper is not** — `unreferencedMediaIn` has had no caller since chapter 4.15 and chapter 4.20 declined it deliberately, because its population is objects nothing ever attached. Say which of the three this chapter moved.
- [X] T035 [US3] Record the audit-log consequence in `specs/067-chapter-4-21/gaps.md`: 1,324 entries name a user target, the log is append-only, and an erasure **writes** one rather than removing any. An entry recording that somebody was banned is itself a record of that person, and repairing that means narrowing ADR-35 a second time in two chapters.

---

## Phase 6: The probes

- [X] T036 **Probe every tenancy arm, alone and in combination**, re-running the erasure suite AND the isolation gauntlet each time, and record which turn anything red in `specs/067-chapter-4-21/baseline.txt`. **065 measured three scoped reads where removing any TWO was invisible**, and chapter 4.20 found a bulk-delete arm that was invisible on its own. **A single-mutation probe measures the DEFENCE, not the arm** — and when an arm turns nothing red, **the answer is the test that makes it visible, not the deletion that makes it honest.**
- [X] T036a **Delete `@Accepts("application")` from the erasure route and re-run.** Chapter 4.18 found that deleting it from a READ route answered an end-user token 200 with the tenant's whole moderation history, and nothing was red. **Here an end-user token that can erase destroys a person's data**, so if nothing goes red the chapter has a route whose only real defence is untested.
- [X] T037 Run the isolation gauntlet and record its counted figures, **derived from `targets.ts` rather than expecting a printed line** — that suite asserts emptiness and prints no count of its own. It was **49 classifications and 25 moderation-route entries** at 066's close.
- [X] T038 Measure what an erasure costs in `specs/067-chapter-4-21/baseline.txt`, per user and **split by half**: chapter 4.20 measured a message at 0.04 ms and a media object at 2.05 ms, about 48×, because the object store has no foreign keys. **Name which half each figure came from**, and say plainly that no user on this lane owns many objects.
- [X] T039 Run `python3 specs/045-part-3-rework/check-lane-scope.py` and record its **counted line**, not its exit code. It was **77 integration files, 0 unscoped reads, 10 of 10 controls firing** at 066's close; this chapter adds one file.

---

## Phase 7: The documents

- [X] T040 **Read FR-MOD-04 and FR-MED-10 before editing either**, and record what the reading found — including *nothing to amend* if that is the answer.
- [X] T041 Read the clauses **beside** them while `docs/04-srs.md` is open. **FR-MED-10 sits directly above FR-MED-11 and is the clause chapter 4.20 nearly enforced by accident**; FR-MOD-05 sits two above FR-MOD-06. 065's T042 found FR-MSG-10 two rows from the one it opened the file to edit.
- [X] T042 Amend **FR-MOD-04** in `docs/04-srs.md`: four obligations with their verdicts, that *analytical records* is four stores with four answers, and that one of them cannot comply by construction.
- [X] T043 Amend **FR-MED-10** in `docs/04-srs.md` if the measurement warrants it — in particular that its unlink was already met, that its 24-hour reaper is still unbuilt, and that *a user's media objects* is undefined for 73% of them.
- [X] T043a Amend **FR-USR-05** or **FR-MOD-04** with whichever way T010 and T011 decided, **naming the clause that lost**. If `usage_active_users` is kept, FR-MOD-04's *analytical records* is partly unmet by decision and must say so.
- [X] T044 Add revision row **1.28** to `docs/04-srs.md`, stating what the chapter demonstrated and what it could not.
- [X] T045 **If T013a decided an ADR is needed, write it into BOTH homes** — the summary in `docs/05-sad.md` and the argument in `docs/06-adr-deep-dives.md`. 4.5 found an ADR lives in two documents and ten passes amended only the summary. **If it decided none is needed, record that as DONE with the reason** rather than leaving the task unticked.
- [X] T046 Amend `docs/05-sad.md` where the erasure changes what a section claims — **and check every sentence in the section you edit**, because 4.19 found three sites where a task naming one would have reached one.
- [X] T047 Amend **both** copies of the Part 4 table — `docs/12-part-4-structure.md` row 22 CLOSED and **`docs/07-tutorial-plan.md`'s PART 4 row 22** SHIPPED. **Match on the title, not the number**: `docs/07` holds two rows numbered 22, Part 3's and Part 4's, hundreds of lines apart.
- [X] T048 [P] Sweep `docs/` for feature-local ids **both ways**: diff-scoped for what this session added, and tree-wide with every hit classified. Chapter 4.20 added zero; the tree-wide population is 063-4's and is not this chapter's.
- [X] T049 Run `pnpm sync:docs` then `pnpm check:docs` from `relay-tutorial`.
- [X] T050 [P] Write `specs/067-chapter-4-21/traceability.md` by **reading**, not by grep — including the two sections a grep cannot produce: what is in the feature with no requirement behind it, and the clauses deliberately not amended.

---

## Phase 8: The chapter

- [X] T051 Register 4.21 in `relay-tutorial/lib/tutorial.ts` with all seven fields, at `/part-4/chapter-21/erasure-and-every-path-it-must-find`. An unregistered id throws at build.
- [X] T052 **Open the chapter with the refusal** — `docs/07` §4 rule 1. The reader deletes a user the way FR-USR-05 does, and finds the row, the messages and the billing rows still there. **That is the gap, and it is a behaviour rather than an error**, which makes it a different opening from 4.20's and worth writing as one.
- [X] T053 Write the chapter at `relay-tutorial/app/(en)/part-4/chapter-21/erasure-and-every-path-it-must-find/page.mdx`, 2,000–4,000 prose words counted outside fences and tables, English only.
- [X] T054 [P] Write the figures in that directory's `figures.ts`, passed as `code` and not `chart` — `check:figures` caught three dead diagrams `pnpm build` did not.
- [X] T055 Write the TRAP box. The candidate is **`nothing_to_erase` against `cannot_erase`**: a reader will assume both mean *no rows removed*, and the difference is the only thing the receipt exists to carry.
- [X] T056 Write at least one `WHY` box. The candidate is **why the analytical half is reported rather than rolled back** — constitution III cuts the opposite way from the instinct, and a reader who skips it will think the erasure is sloppy. `docs/07` §4 rule 3; 4.16 through 4.20 carry 2, 3, 1, 2 and 2.
- [X] T057 Publish what the chapter could not do: no scheduler, no undo, no cross-environment erasure, nothing removable from a `uniq` sketch, and **nothing measurable about a user who owns a lot of media**, because none on this lane does.
- [X] T058 Write the chapter's fences. **A titled fence is a whole-body claim** (051-6); an excerpt must be untitled. Chapters 4.19 and 4.20 both contributed **0 titled fences** and put every diff in the appendix.
- [X] T059 Generate hunks from the checker's own replay — `pnpm check:fences --dump <dir>` — then diff against `relay-platform` at `-U6`. **Verify every pre-image matches exactly once before pasting**, widening only where it does not, because widening merges adjacent hunks and a merged hunk can span more repetition than either half. **Strip the `--- a/` and `+++ b/` headers**: a `diff` fence carries the `@@` hunks only, and 052 spent 112 problems learning it.
- [X] T060 Put every hunk in `relay-tutorial/fences/post-series.md`, **placed last**, working biggest-first from T006's table.
- [X] T061 Run **all six tutorial gates** green from `relay-tutorial`, **after** every source edit, and compare each counted line against T003a's.
- [X] T062 [P] Count the prose words and confirm the bound.

---

## Phase 9: The record and the close

- [X] T063 Write `specs/067-chapter-4-21/baseline.txt` phase by phase, **in the order the measurements were taken, including the ones that were wrong first**.
- [X] T063a **Re-measure T007's map and publish both figures** (SC-012) — the open's and the close's. The counts move as the chapter's own fixtures run, which chapter 4.20 learned the hard way when its tests moved the lane's oldest message by a year.
- [X] T064 [P] Write `specs/067-chapter-4-21/gaps.md`, numbered, with the carried ledger **re-measured** rather than copied. Known carries: **066-1** (an audit entry outlives its target), **066-2** (the invisible bulk-delete arm), **066-4** (a test fixture that moves a headline measurement), 065-2, 065-3, 065-5, 064-1, 063-4, 058-3 (**twenty-three routes, not sixteen**), 062-12, 050-8, 043-1.
  **AND ONE CARRY THIS CHAPTER MUST NOT DROP**: constitution VI's third bullet gates releases on three mechanisms and **two of them do not exist** — no dependency vulnerability scan and no OWASP scan anywhere in the workspace.
- [X] T065 **Re-measure the coverage pins this chapter's edits could move**, in `relay-platform/vitest.coverage.config.mts`, **after** the fence chain is at zero — and add pins for the new files. **Pin BELOW the measured value**, because `session.ts` measured 87.80% and 85.36% on identical code twenty minutes apart and a floor at the measurement teaches people to lower floors.
  **AND IF A NEW FILE MEASURES THIN, THE ANSWER IS A TEST.** Chapter 4.20's `sweep.ts` came in at 63.79% and the largest uncovered arm was the dry run the quickstart tells an operator to run first.
- [X] T065a **Re-run `check:fences` to 0 after T065 and re-hunk if the pin file moved.** **23 pages publish `vitest.coverage.config.mts`**, it is the sixth billed file, and chapter 4.20's chain went red here exactly as predicted. Run it even when nothing changed — the control is what tells a clean chain from an unchecked one.
- [X] T066 Probe the pins **both ways** in `specs/067-chapter-4-21/baseline.txt`: a pin on a path that matches no file is silent, and an impossible pin on a real file must FIRE. **Run the positive control through `pnpm coverage` and not through a filtered `vitest run`** — chapter 4.20 found that a filtered run does not evaluate per-file thresholds, so the positive control looked exactly like the negative one and would have been recorded as *pins do not bind*.
- [X] T067 **Rebuild the api image before running the quickstart** — `pnpm build`, then `docker compose --profile services build api`, then `up -d --wait`. §3 onward hit `localhost:4000`, which is the composed container, and a new route answers **404** against a stale image. Then run `specs/067-chapter-4-21/quickstart.md` end to end and correct it in place, **recording each wrong version**. The last seven chapters' were wrong 3, 4, 3, 5, 2, 0 and 5 times.
- [X] T068 **Check FR-011 rather than trusting it** (SC-008): `git diff --name-only part4-ch20..HEAD` and confirm every file outside tests and documents is one the chapter is for.
- [X] T069 Stop the composed services **by name** from `relay-platform` — `docker compose stop api gateway dispatcher media-worker`, and **not `ingester`**.
- [X] T070 Run the full lane set with nothing else against the stack and record every REAL exit code, **each with its `Cached:` line and elapsed time or under `--force`**, compared against T002. **Compare CLASS BY CLASS, not test by test.** **And do not edit source while the battery runs** — 065 did and had to discard it.
- [X] T070a **Run the sealed suite** — `RELAY_API_URL=… RELAY_WS_URL=… RELAY_DEMO_CREDENTIAL=… pnpm test:outsider` from `relay-platform` — and record its counted line. **It is the only thing that boots the composed api and asks it a question**, which is the risk T020's new module carries: a module that declares a service it does not provide compiles, typechecks and lints, and fails on the first request. It was **21 of 21** at 066's close.
- [X] T071 Confirm every phase was committed as it closed, **submodule before pointer**, checked with `git -C relay-platform log --oneline -1`.
- [X] T072 **Push submodules first, then the superproject** — `relay-platform`, then `relay-tutorial`, then the root. CI is the superproject's and the other two are submodules checked out `submodules: recursive`.
- [X] T073 Compare the CI error set **per error** against T004's baseline, in both directions, and record it (SC-009). **The baseline is empty**, which is the hardest kind to match.
- [X] T074 If CI is red, fix the platform, then **re-dump, re-hunk `relay-tutorial/fences/post-series.md` and push both** — repairing a platform file invalidates the appendix hunks that publish it. **Record it as NOT RUN with the condition if CI is green**, rather than silently skipping. **NOT NEEDED: CI was green on all four jobs on the first push.**
- [X] T075 Tag `part4-ch21` in `relay-platform` and the superproject, annotated, on a commit CI has proved green.
- [X] T076 **`CLAUDE.md` HAS 791 BYTES OF HEADROOM AND THIS ENTRY WILL NOT FIT.** Compressing 066's entry recovers roughly 3 KB and a new one costs roughly 6 KB, so the convention no longer keeps pace: **the 046–063 tail is 107,052 bytes across 17 closed features and has never been revisited.** Decide with the user what stays citable before writing, then compress and add. **`wc -c` before and after.**
- [ ] T077 Remove the active-plan line from between the `SPECKIT` markers in `CLAUDE.md` when the feature closes. **The markers now span only that block** — they were moved during planning, when they enclosed 118,636 bytes and the agent-context hook would have replaced all of it with three sentences.

---

## Dependencies & Execution Order

```
Phase 1  →  Phase 2 (the decisions, which the route needs)
Phase 2  →  Phase 3 (US1)  →  Phase 4 (US2)
Phase 3  →  Phase 5 (US3)
Phases 3-5  →  Phase 6  →  Phase 7  →  Phase 8  →  Phase 9
```

**T005 BLOCKS EVERYTHING.** If the premise has moved since 2026-10-04 the chapter
has moved with it — and two of its numbers are already known to drift: the
outbox grows, and the sketches become non-empty the day `message_events` gains a
producer.

**T010 AND T011 BLOCK T016.** Whether erasure destroys messages and billing rows
decides what the traversal does, and taking that decision with the route already
written means taking it under pressure to keep what is there.

**T013a BLOCKS T045.** Whether an ADR exists decides whether phase 7 writes one.

**T014 BLOCKS T019.** The deletion verb decides whether the receipt's count can
be trusted.

**T015 BLOCKS T016.** The probe must be green against today's platform before the
traversal exists, because the behaviour it asserts is the premise.

**T025b DEPENDS ON `target_kind` ALREADY ADMITTING `user`.** Check it in T014a:
it is the reason this chapter's classification can be `moderation` where chapter
4.20's was not, and if the check is wrong the cost is a migration and 34 pages.

**T065a COMES AFTER T065.** A final `check:fences` has to follow the last edit to
any file the chain publishes, and the pin file is published by 23 pages.

**T003a BLOCKS T061.** The six gates have to be recorded before the chapter
changes anything, because T061 compares counted lines against them.

### Parallel opportunities

Five, marked `[P]`: T032, T048, T050, T054, T062, T064. **The number is small for
the usual reason** — every task in phases 1, 6 and 9 appends to one
`baseline.txt`, so they are sequential however independent the measurement is.

### Suggested MVP

**Phase 1 → Phase 2 → Phase 3.** US1 alone is a shippable chapter: a route that
erases a user from every store that can erase them. US2's receipt is what makes
it honest and US3's verdicts are what make it publishable, but a reader who
stopped after US1 would have a working erasure.
