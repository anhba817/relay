# Tasks: Chapter 4.18 — The log that cannot be edited

**Input**: Design documents from `specs/064-chapter-4-18/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/audit-log.md`, `quickstart.md`

## Format: `[ID] [P?] [Story] Description`

`[P]` means **a different file and no dependency on an incomplete task**. Chapter 4.17's task
list marked eight tasks parallel because they were separate `it(...)` blocks in one file, which
is not what the marker means. Most of phase 3 touches `relay-platform/services/api/src/db/repository.ts`
and is therefore serial.

**EIGHT MARKERS WERE DROPPED FROM THIS LIST BEFORE IT SHIPPED, FOR ONE REASON EACH TIME: THEY
ALL APPEND TO `baseline.txt`.** A measurement being independent is not the same as a task being
parallel — phase 1's measurements are independent and their recording is one file. Two of them,
T048 and T049, are worse than that: each needs the composed stack to itself, and chapter 4.17
discarded an entire battery after walking a quickstart beside it. **Ask what a task WRITES, not
what it reads.**

## Path Conventions

Paths are from the repository root. `relay-platform/` and `relay-tutorial/` are git submodules;
**push submodules first, then the superproject**, or CI checks out gitlinks no remote has.

## Standing rules this list assumes

- **Commit each phase as it closes.** `git checkout` on a file with uncommitted work has
  destroyed work twice in this project.
- **Capture an exit code outside the pipeline.** `cmd > out.log 2>&1; echo "EXIT=$?"` — `$?`
  after a pipe is the last stage's, and this project has made that mistake **seven** times.
- **`pnpm -s <script>` reports red for a green gate.** Drop the `-s`.
- **Assert a gate's counted line, not its exit code** (055-4): five of seven gate scripts exit
  0 over an absent corpus.
- **Bring the stack up with `RELAY_POSTGRES_PORT=15432`.** This machine's own Postgres holds 5432.
- **Run a lane with nothing else against the stack.** Chapter 4.17 broke its own battery by
  walking a quickstart beside it and had to discard the run.
- **Clean up a probe before anything is counted** (043).
- **Run `check:fences` after ANY source edit**, not only after the chapter.
- **Do not run `prettier --write` over a fenced file.** Chapter 4.17 turned six edits into 23
  published hunks that way; the file had never been Prettier-clean and nothing requires it to be.
- **Before regenerating a measurement, grep this directory for the number.** Chapter 4.17 spent
  a phase rebuilding a fixture whose recipe was in its own `quickstart.md`.

---

## Phase 1: Setup — the baseline, measured before anything is edited

- [ ] T001 Read `docs/12-part-4-structure.md` row 19 and §7.5 against the tree, and record in `specs/064-chapter-4-18/baseline.txt` whether the brief still describes the platform. **Check a task's premise before executing it** — this project has found four tasks whose premise was wrong, including one that would have caused a defect.
- [ ] T002 Record every lane's REAL exit code in `specs/064-chapter-4-18/baseline.txt`, each captured outside a pipe: `pnpm lint`, `pnpm exec turbo run typecheck --force`, `pnpm build`, `pnpm exec turbo run test --force`, `pnpm test:integration`, `pnpm coverage`, `pnpm test:outsider`. **A red baseline is a measurement, not a blocker** — chapter 4.17 opened on three red integration suites and closed on three different ones, and only the per-test comparison could say so.
- [ ] T003 Record the five tutorial gates in `specs/064-chapter-4-18/baseline.txt` with each **counted line** quoted, run from `relay-tutorial` and outside a pipe: `check:docs`, `check:errors`, `check:fences`, `check:figures`, `check:srs`.
- [ ] T004 Record the CI baseline in `specs/064-chapter-4-18/baseline.txt`: the run id, the four jobs' conclusions, and the count of `##[error]` lines over the whole run. Chapter 4.17 opened and closed on **zero**, which is the hardest baseline to match.
- [ ] T005 **Derive the route list from a booted application and write the real number down**, in `specs/064-chapter-4-18/baseline.txt`. Run `services/api/src/isolation/targets.itest.ts` and quote its printed line, `gauntlet targets: N derived, M attacked, …`. **Research R3's 33-of-51 is a parse, not the derivation**: a regex over `targets.ts` found 47 entries where the file's own `method:` count is 51, and only the router knows what exists.
- [ ] T006 Count the fence bill in `specs/064-chapter-4-18/baseline.txt` for every file the plan names, with `grep -rl 'title="<path>"' app/` from `relay-tutorial`. Research R6 has the numbers to check against — `repository.ts` 51 pages, `schema.ts` 33, `codes.ts` 24, `targets.ts` 12. **Counting it now is the point**: it decides T011, and chapter 4.15's rule is that a bill counted after the work can no longer change how the work is sequenced.
- [ ] T007 Re-verify the chapter's opening fact and record it in `specs/064-chapter-4-18/baseline.txt`: ban a user, lift the ban, and show `banned_at` is `NULL` again. Use `coalesce(banned_at::text,'<NULL>')` — the bare column prints an empty trailing field, and the point of the measurement is an absence.
- [ ] T008 Confirm FR-MOD-02's premise in `specs/064-chapter-4-18/baseline.txt` by running it, not by reading it: an application credential deleting a message authored by somebody else. `docs/12` §7.5 says to check this before chapter 4.19 is written, and this chapter needs the answer because **it decides whether the log has a writer on day one**. `messages.service.ts` skips the authorship comparison when the principal carries no user; confirm the route agrees.
- [ ] T009 Record in `specs/064-chapter-4-18/baseline.txt` what the platform holds about a ban today, as a sweep with every hit classified: `select table_name||'.'||column_name from information_schema.columns where column_name ~ 'ban|moderat|actor|audit'`. **Classify both hits** — `pg_stat_database.sessions_abandoned` matches on a substring and is a statistics catalogue, and a sweep that reported only a count would have looked the same and proved less.

---

## Phase 2: Foundational — the decision, which everything else is built on

**Purpose**: the moderation set. Blocking, because a write cannot be added for an action nobody
has decided is in.

**AND THIS PHASE IS USER STORY 3's SUBSTANCE ARRIVING FIRST, WHICH IS NOT A MISLABEL.** US3 is
P3 by user value — a reader wants to know what is not covered — and first by dependency, because
US1 writes entries for the set this phase defines. The decision is foundational; its published
form and its checks are phase 5.

- [ ] T010 Write every derived route — method and path — into `specs/064-chapter-4-18/routes.md` from T005's booted run, not from the source text. **Derive, don't list**, and the precondition chapter 4.8 attached to that rule applies: the derived version must not be weaker than the thing it replaces, so the count has to match T005's printed line exactly.
- [ ] T011 **Decide research R3's open question** and write the decision with its reason in `specs/064-chapter-4-18/baseline.txt`: the moderation flag as a field on `services/api/src/isolation/targets.ts`'s existing entries, or a sibling table with its own both-directions check. T006 has the bill — `targets.ts` is published by 12 pages — and the trade is one list coupling a security classification to a compliance one against two lists that can fall out of step with the router independently.
- [ ] T012 Classify every tenant-reachable mutating route in `specs/064-chapter-4-18/routes.md` as `moderation` or `not-moderation`, **each with a reason**. The rule the spec proposes is *mutating, application-reachable, and acting on something other than the caller*; where the rule and the right answer disagree, **the disagreement is a finding and the route's row records both**.
- [ ] T013 Record in `specs/064-chapter-4-18/routes.md` that every `/internal/` route is outside the set **by construction rather than by decision** — a platform principal carries `environmentId?: undefined`, so its action cannot be scoped to a tenant and cannot appear in a tenant's read. *Outside by construction* and *decided to be outside* are different claims and only one needs a reason.
- [ ] T014 Decide FR-008 in `specs/064-chapter-4-18/baseline.txt`, per action rather than globally: does a **refused** action earn an entry, and does one that **changes no state**? `banUser`'s transaction already answers the second for itself — `if (banned.length === 0) return []` after a guard that makes a re-ban touch nothing — so check whether the other actions have the same shape rather than assuming this one generalises.
- [ ] T014a Decide the audit table's `ON DELETE` behaviour in `specs/064-chapter-4-18/baseline.txt` and amend `specs/064-chapter-4-18/data-model.md` §1 to match. The draft says *"a tenant's entries die with the tenant"* as a **consequence** of following the schema's usual foreign key, and for an audit log that is a decision with weight: cascading means a deleted environment takes its moderation history with it. **It also collides with row 22**, where erasure deletes a user's data and an entry naming that user is a moderator's action rather than the user's. Decide the environment case here with its reason; the user case stays row 22's (research R8).
- [ ] T014b **Resolve FR-005 against FR-012 in `specs/064-chapter-4-18/baseline.txt`, before any code is written.** They cannot both hold for four methods: `unbanUser`, `setMemberRole`, `archiveChannel` and `unarchiveChannel` perform their action outside a transaction, so writing an entry atomically with them means adding one. FR-005a permits it and FR-012 now names the exception; this task records **which four actions took it and what each gained** — a transaction, the ability to report whether a row changed, and a new way to fail. **The first one phase 3 reaches is `unbanUser` at T026, which is half the chapter's opening demonstration**, so deciding it here is the difference between a spec question and a spec question with a half-built migration in the tree.
- [ ] T015 Fix the action naming scheme in `specs/064-chapter-4-18/data-model.md`: what string goes in the entry's `action` column, and how a reader joins it to the route. **One name, used by the column, the filter and the derivation** — chapter 4.16 lost a day to a field renamed between its producer and its reader (`Code: 47`).

---

## Phase 3: User Story 1 — a moderation action leaves a record nothing can change (P1) 🎯 MVP

**Goal**: the table, the trigger, and the writes, so that a ban and its reversal leave two
entries that nothing in the application can alter.

**Independent test**: ban a user and lift the ban; read two entries with the right actor, target
and order; attempt `UPDATE` and `DELETE` on an entry and be refused.

- [ ] T016 [US1] Write migration `relay-platform/services/api/migrations/0021_audit_log.sql`: the table of `data-model.md` §1, the foreign key to `environments`, the two check constraints, and the index `(environment_id, occurred_at DESC)`.
- [ ] T017 [US1] Add the trigger function and the `BEFORE UPDATE OR DELETE` trigger to `relay-platform/services/api/migrations/0021_audit_log.sql`. **This is the schema's first trigger** — `grep -rl "CREATE TRIGGER\|CREATE FUNCTION" services/api/migrations/` returns nothing across twenty migrations — so the migration carries the justification research R2 measured, in a comment: `REVOKE UPDATE, DELETE` was run and does nothing, because the api connects as a superuser.
- [ ] T018 [US1] Declare the table in `relay-platform/services/api/src/db/schema.ts` with the comment conventions that file uses, **including why the column is `occurred_at` and not `created_at`** — `data-model.md` §1 has the reason and the schema is where the next reader will look for it. The two instants are identical by construction because the row is written inside the action's transaction, and that is exactly why the familiar name would mislead. **33 pages publish this file**; the edit is one block and the fence hunk is one.
- [ ] T019 [US1] **Run the trigger red before anything depends on it**: apply the migration, insert a row by hand, and attempt `UPDATE` and `DELETE` through `psql`. Record both refusals in `specs/064-chapter-4-18/baseline.txt`. A mechanism believed rather than attempted is the thing this chapter is about. **Assert the trigger exists first** — `select tgname from pg_trigger where tgrelid = 'audit_log'::regclass` — because `schema_migrations` records **filenames only, with no checksum**: an apply that happened between T016 and T017 lands the table without the trigger and the ledger says the migration is done. The ClickHouse ledger checksums and chapter 4.16 met its refusal; this one does not, and the asymmetry is worth a line in the chapter.
- [ ] T020 [US1] **Run the two bypasses and record them**, in `specs/064-chapter-4-18/baseline.txt`: `SET session_replication_role = replica` then the same `UPDATE`, and `DROP TRIGGER` then the same `DELETE`. Research R2 measured both succeeding. **The chapter's claim is scoped to what this probe shows**, and the scope goes in the prose rather than in a footnote.
- [ ] T021 [US1] Clean up T019's and T020's rows before anything else is counted, and say so in `specs/064-chapter-4-18/baseline.txt` (043: a red probe writes to the lane, and the next measurement reads it as pre-existing data).
- [ ] T022 [US1] Add the actor and request id to `Repository`'s constructor in `relay-platform/services/api/src/db/repository.ts`, beside `environmentId`. **A third argument, not a parameter on every method** — research R4 — so a method that records an entry reads context the way it already reads `this.environmentId`. **The parameter is OPTIONAL and research R4 says why**: a required one edits **110 call sites across 32 test files**, 17 of them fenced across 131 pages, which R6's bill did not list until R4 was measured. **And the absent case is a NAMED VALUE, not an omission** — one construction site records nothing and must say so in a way a check can see, because *nothing may be exempt by omission* is the rule `targets.ts` already states and an exemption list is what this project refuses (056-10). **Not `?? ""`**: `environmentId` already does that and chapter 4.4 recorded what an empty string costs, a value that keeps compiling and keeps meaning nothing.
- [ ] T022a [US1] Assert what the compiler no longer can, in `relay-platform/services/api/src/db/repository.itest.ts`: **every `new Repository(` outside a test file supplies the actor context or T022's named absence.** Derived from the source, both directions — a production site that supplies neither fails, and the assertion failing to find any site fails too. **The named absence is why this reads "or"**: `dev-token.controller.ts` records nothing and an assertion demanding context from all six would be satisfied only by an exemption list. T022 made the parameter optional to keep 32 test files off the fence bill, and **an optional parameter is a check the compiler stopped doing**; this is what replaces it. Without it, a repository built without an actor writes entries with no actor and nothing says so.
- [ ] T023 [US1] Update the six construction sites: `relay-platform/services/api/src/{users,media,messages,webhooks,channels}/*.module.ts` and `relay-platform/services/api/src/auth/dev-token.controller.ts`. Five already hold `req`. **The sixth records nothing** — `POST /auth/dev-token` is not a moderation action — so it supplies a value it will never use, in T022's shape. Say so in a comment at that site rather than leaving the next reader to wonder what a dev-token repository would audit.
- [ ] T023a [US1] Thread `userExternalId` into `banUser` and `unbanUser` in `relay-platform/services/api/src/db/repository.ts`, and pass it from `relay-platform/services/api/src/users/users.service.ts`, which already holds it — `setBanned` calls `requireUser(externalId)` and then hands the repository `user.id` alone. **`target_id` stores the identifier a customer uses** (`data-model.md` §3a), and for a user that is the external id; a uuid would publish a value no customer has seen and need a join on every read. **The precedent is in the file already**: `deleteMessage` takes `userExternalId` for `metadata.deleted_by`, *"threaded rather than looked up… a SELECT inside the write transaction is a query every deletion would pay to learn something the controller already holds."* **A signature change, not a behaviour change** — FR-012's exception is not engaged. Only the user case needs this: channels and messages are named by uuid on the routes that act on them.
- [ ] T024 [US1] Write the entry-insert in `relay-platform/services/api/src/db/repository.ts` as one private method the recording transactions call. The lint rule puts every query here, and FR-005 needs it inside the action's transaction.
- [ ] T025 [US1] Record the ban in `banUser` in `relay-platform/services/api/src/db/repository.ts`, **after** the `if (banned.length === 0) return []` guard, so an action that changed nothing writes nothing. This is the pair with no trace today and it is the chapter's opening demonstration.
- [ ] T026 [US1] Give `unbanUser` a transaction and a `RETURNING` in `relay-platform/services/api/src/db/repository.ts`, then record the unban inside it. **It has neither today** (FR-005a, FR-005b): a bare `this.db.update(...)` with no `isNull` guard, so lifting a ban and unbanning somebody who was never banned are the same call with the same result, and T014's no-op decision cannot be applied to it until it can tell the two apart. **The ban and the unban are not the same shape** — `banUser` is 43 lines in a transaction with a guard, `unbanUser` is a bare update — and the chapter's opening demonstration is the pair.
- [ ] T027 [US1] Record the remaining phase-2 `moderation` actions in `relay-platform/services/api/src/db/repository.ts`, one at a time, each inside the transaction it already has.
- [ ] T028 [US1] Write the write-side suite at `relay-platform/services/api/src/audit/audit.itest.ts`: a ban and an unban produce two entries with the right actor, action, target and order.
- [ ] T029 [US1] Assert the request id joins the two logs, in `relay-platform/services/api/src/audit/audit.itest.ts`: the entry's `request_id` is the one the api assigned the request. **The two logs answer different questions about one request and the id is the join**; nothing asserts that today.
- [ ] T030 [US1] Add the refusal probe to `relay-platform/services/api/src/audit/audit.itest.ts`: attempt `UPDATE` and `DELETE` on a written entry and expect the refusal. FR-004 says demonstrated, not asserted — **a comment is not a test**, which is chapter 4.17's finding applied to the mechanism this chapter exists to build.
- [ ] T031 [US1] **Check FR-012 per action, not globally**: re-run each recorded action's own existing suite unedited and record the result in `specs/064-chapter-4-18/baseline.txt`. A suite that needed editing to stay green is a behaviour change, and the chapter says so rather than editing it.

---

## Phase 4: User Story 2 — an investigator reads a tenant's moderation history (P2)

**Goal**: `GET /v1/audit-log`, scoped to the caller's environment.

**Independent test**: perform moderation actions in two environments; read as the first and find
exactly its own, in order, with no entry of the second reachable by any parameter.

- [ ] T032 [US2] Write the reader in `relay-platform/services/api/src/audit/audit.reader.ts` — one keyset page over `(environment_id, occurred_at DESC)`, the shape `contracts/audit-log.md` publishes.
- [ ] T033 [US2] Write the query schema in `relay-platform/services/api/src/audit/audit.schema.ts`, with the `action` enum **built per request from the injected set** rather than frozen at import time. Chapter 4.8's `buildRequestLogQuerySchema(this.endpoints.get())` is the shape; a vocabulary frozen at import drifts from the router that produces the values, silently and in the direction that matters.
- [ ] T034 [US2] Write `relay-platform/services/api/src/audit/audit.controller.ts`: `@UseGuards(CredentialGuard)`, `@Accepts("application")`, and **403 rather than an empty page** for a principal with no environment — chapter 4.8's reason, which reads worse here: `[]` would say nobody moderated anything.
- [ ] T035 [US2] Wire `relay-platform/services/api/src/audit/audit.module.ts` and register it. **Only a running app asks whether a module provides what it declares** — chapter 4.10 shipped a `MediaModule` that compiled, typechecked and linted, and answered `Nest can't resolve dependencies` on the first request.
- [ ] T036 [US2] Add the route to `relay-platform/services/api/src/isolation/targets.ts` with its classification. Chapter 4.8 found that adding an entry turned the gauntlet red with *"classified but never attacked"* — **naming a route is not covering it**, and the attack is owed in the same change.
- [ ] T037 [US2] Write the isolation test in `relay-platform/services/api/src/audit/audit.itest.ts`: two environments, the same actions, and a read that returns exactly one tenant's. **Plant the rows the assertion counts** — an empty log passes a leak check for the same reason an empty page does.
- [ ] T038 [US2] Assert the filter's complement in `relay-platform/services/api/src/audit/audit.itest.ts`: what a filter promises is that **nothing else** comes back, and the count of what does is the plant's business (chapter 4.8).
- [ ] T039 [US2] Assert the refusals in `relay-platform/services/api/src/audit/audit.itest.ts` **by code and not by status alone**: a `limit` outside the bound, an `action` outside the set, a malformed cursor. `webhooks.itest.ts` asserted status and message text and passed for three chapters while the body said `internal_error`.
- [ ] T040 [US2] Add an error code to `relay-platform/packages/protocol/src/codes.ts` only if the refusals need one that does not exist. **Check first** — `codes.ts` is published by 24 pages and chapter 4.11 had to move its hunk to the appendix because `fences/post-series.md` already amends that file twice. A second code for a distinction with no different action behind it is what `codes.ts:10`'s own test refuses.

---

## Phase 5: User Story 3 — the actions that are not recorded are named, not forgotten (P3)

**Goal**: the set is published with reasons, derived from the router, and a route added without a
decision fails a check.

**Independent test**: add a route to the application, run the suite, watch it go red; remove it.

- [ ] T041 [US3] Publish the classification in the form T011 chose — `relay-platform/services/api/src/isolation/targets.ts` or its sibling — with a reason on every entry.
- [ ] T042 [US3] Assert both directions in `relay-platform/services/api/src/isolation/targets.itest.ts`, or in the sibling suite T011 chose: a derived route matching no entry fails, and an entry matching no derived route fails. **The second direction is the one that catches a stale exemption after a rename**, and it is the half a new mechanism usually forgets.
- [ ] T043 [US3] **Run SC-004 red**: add a throwaway mutating route to the api, run the suite, record the failure and its message in `specs/064-chapter-4-18/baseline.txt`, then remove the route. A check that has never failed has not been checked, and this one's whole value is what it does to a route nobody classified.
- [ ] T044 [US3] Record in `specs/064-chapter-4-18/baseline.txt` every route whose classification the spec's rule got wrong, with what the rule said and what the right answer is. **The rule will misclassify** — the spec says so in advance — and the misclassifications are the chapter's findings rather than an embarrassment to tidy away.
- [ ] T044a [US3] Publish **how an action is added to the set** in `relay-tutorial/app/(en)/part-4/chapter-18/the-log-that-cannot-be-edited/page.mdx` — the procedure a later chapter follows: classify the route, write the entry inside the action's transaction, and the check that goes red if either step is skipped. **`docs/12` row 19 says this chapter is *"Registry-shaped, the same shape as Errors that resolve"*, and §5 rule 5 is *"A registry appears before the first chapter that adds to it"*** — the same document pairs the error registry with *"how a code is added to it"*. Rows 20, 21 and 22 all write to this log and are the readers.
- [ ] T044b [US3] Put the same procedure **where the classification lives** — a header comment in `relay-platform/services/api/src/isolation/targets.ts` or in the sibling T011 chose — and name T042's both-directions check as what enforces it. **The registry this chapter is modelled on keeps its procedure in code**: `packages/protocol/src/codes.ts` argues its own convention inline (*"every reuse fails this file's own test"*, *"the way chapter 1.3 numbered 4002 and 4008"*) and `check-error-codes.mjs` enforces it. Rows 20, 21 and 22's implementers read the classification; T044a's prose is for a reader of the chapter and these are not the same person.
- [ ] T045 [P] [US3] Write `specs/064-chapter-4-18/clauses.md`: FR-MOD-03's obligations counted, each marked met, demonstrated, unmet by decision or unreachable, with where. SC-007 wants a count, not an adjective.

---

## Phase 6: The probes — making the silent failures loud

- [ ] T046 Delete each tenancy predicate in the read path one at a time, re-run both the audit suite and the gauntlet, and record in `specs/064-chapter-4-18/baseline.txt` which arms turn anything red. Chapters 4.11 and 4.12 both measured that **an SQL clause carries no JavaScript branch**, so a coverage number reports a scope as covered whether or not it is there — and 4.12 found three scopes where deleting any one changed nothing because of the other two.
- [ ] T047 Run the isolation gauntlet and record its own counted line in `specs/064-chapter-4-18/baseline.txt`. Constitution VI names it as gating releases, and chapter 4.9 found three of its attacks returning at their first line and reporting green.
- [ ] T048 Perform a moderation action with the analytical pipeline stopped and assert the entry exists (SC-006), recorded in `specs/064-chapter-4-18/baseline.txt`. **`docker compose stop nats clickhouse`, with no profile flag** — both are base services in `relay-platform/compose.yaml`, and only `api`, `gateway`, `dispatcher` and `media-worker` carry `profiles: ["services"]`, so the `--profile services` form stops the wrong containers. (That form belongs to T076.) **And choose the subject deliberately: the UNBAN.** `setBanned(externalId, false)` returns straight to the controller with no publish, so it needs nothing but Postgres — where a ban of a user **with** channels commits and then throws at `membership.publish`, giving a 500 for an action that succeeded. Run it with nothing else against the stack.
- [ ] T049 Measure what the entry costs the action it records, in `specs/064-chapter-4-18/baseline.txt`: the ban's latency with the insert and without, same method, sample size stated, min/p50/max rather than a mean. Chapter 4.16 published a distribution whose mean was 509× its median.
- [ ] T050 Add per-file coverage pins for the new files to `relay-platform/vitest.coverage.config.mts`, **after** the fence chain is taken to zero, not before — chapter 4.16's CI failure was a coverage pin added after the chain was zeroed, and the edit that broke it was the ratchet being tightened. Pin below the lower observation by the observed swing and put both numbers in the config.
- [ ] T051 Probe the pins both ways in `specs/064-chapter-4-18/baseline.txt`: a pin on a path that matches no file is **silent**, and a pin on a real file no lane includes is silent too. Both halves, every time the ratchet is re-pinned.

---

## Phase 7: The documents

- [ ] T052 Amend **FR-MOD-03** in `docs/04-srs.md`: what ships, the retention it cannot enforce and why (research R7, ADR-28's precedent), and that the actor is a credential rather than a person. **Read the clause before editing it** — four documents once agreed on two clauses that do not exist.
- [ ] T053 Read the clauses **beside** FR-MOD-03 while `docs/04-srs.md` is open and record what was found in `specs/064-chapter-4-18/baseline.txt`, including *nothing to amend* if that is the answer. Chapter 4.16 found a data-dictionary row describing a table nobody built, two rows from the one it opened the file to edit.
- [ ] T054 Add revision row **1.25** to `docs/04-srs.md`, stating what the chapter demonstrated and what it could not.
- [ ] T055 **Correct `docs/05-sad.md:430`, which this chapter makes false.** It reads *"**There is no `audit_log` table**, in §6.1 or anywhere in the schema"*, and the paragraph around it explains why `metadata.deleted_by` is not FR-MOD-03's log. The explanation stays and the sentence changes. **Two documents carried a dead fence-chain number for eight chapters** because nobody re-read a sentence whose subject had moved; this one is known in advance and has a task.
- [ ] T056 [P] Add the table to `docs/05-sad.md` §6.1's data view, with the trigger and the scope of what it enforces.
- [ ] T057 Amend **both** copies of the Part 4 table — `docs/12-part-4-structure.md` row 19 CLOSED and `docs/07-tutorial-plan.md` row 19 SHIPPED. Two copies, and amending one is how they drift.
- [ ] T058 [P] Sweep `docs/` for feature-local ids **tree-wide, not by diff**: `grep -rnE 'FR-0[0-9][0-9]' docs/` with every hit classified. `gaps.md` 063-4 found the diff-scoped version fires on its own repairs and cannot see a leak already in the tree, and it found three ids meaning two different things each.
- [ ] T059 Run `pnpm sync:docs` then `pnpm check:docs` from `relay-tutorial`, which rewrites `relay-tutorial/content/docs/*`.
- [ ] T060 [P] Write `specs/064-chapter-4-18/traceability.md` by **reading**, not by grep. Chapter 4.11's mechanical map raised fourteen alarms and all fourteen were false.

---

## Phase 8: The chapter

- [ ] T061 Register 4.18 in `relay-tutorial/lib/tutorial.ts` with all seven fields, at `/part-4/chapter-18/the-log-that-cannot-be-edited`. An unregistered id throws at build; `path` is checked by no gate.
- [ ] T062 Write the chapter at `relay-tutorial/app/(en)/part-4/chapter-18/the-log-that-cannot-be-edited/page.mdx`, 2,000–4,000 prose words counted outside fences and tables, English only.
- [ ] T063 [P] Write the figures in `relay-tutorial/app/(en)/part-4/chapter-18/the-log-that-cannot-be-edited/figures.ts`, passed as `code` and not `chart` — `check:figures` caught three dead diagrams `pnpm build` did not.
- [ ] T064 Write the TRAP box in `relay-tutorial/app/(en)/part-4/chapter-18/the-log-that-cannot-be-edited/page.mdx`. The candidate is research R2's: **the obvious immutability mechanism does nothing on this deployment, and nothing about the migration would have looked wrong.**
- [ ] T065 Publish the scope of the immutability claim in `relay-tutorial/app/(en)/part-4/chapter-18/the-log-that-cannot-be-edited/page.mdx`: what the trigger refuses and what one `SET` undoes. **A chapter that says "immutable" without this paragraph is writing the comment its own TRAP box is about.**
- [ ] T066 Publish what the chapter could not demonstrate in `relay-tutorial/app/(en)/part-4/chapter-18/the-log-that-cannot-be-edited/page.mdx`: no year, no person, no history before the migration, and the erasure tension row 22 inherits.
- [ ] T067 Write the chapter's fences in `relay-tutorial/app/(en)/part-4/chapter-18/the-log-that-cannot-be-edited/page.mdx`. **A titled fence is a whole-body claim** (051-6); an excerpt must be untitled, and chapter 4.14 paid three fences for forgetting it.
- [ ] T068 Generate hunks from the checker's own replay — `pnpm check:fences --dump <dir>` in `relay-tutorial`, then diff against `relay-platform`. Verify every pre-image matches the dumped state **exactly once** before pasting, widening past `-U6` only when it does not.
- [ ] T069 Put hunks in `relay-tutorial/fences/post-series.md` for any file the appendix already amends — `codes.ts` and `targets.ts` are both known (chapters 4.11 and 4.12) — and work the bill biggest-first from T006's table.
- [ ] T070 Run `check:fences` to 0 and `pnpm build` green from `relay-tutorial` (SC-009), **after** every source edit including T050's pins.
- [ ] T071 [P] Count the prose words in `relay-tutorial/app/(en)/part-4/chapter-18/the-log-that-cannot-be-edited/page.mdx` and confirm the bound (SC-010).

---

## Phase 9: The record and the close

- [ ] T072 Write `specs/064-chapter-4-18/baseline.txt` phase by phase, **in the order the measurements were taken, including the ones that were wrong first**.
- [ ] T073 [P] Write `specs/064-chapter-4-18/gaps.md`, numbered, with the carried ledger **re-measured** rather than copied. Known carries: 063-2 (one upload in six waits five or six sweeps), 063-3 (the worker's log cannot say it is alive), 063-4 (three feature-local ids with two meanings each), 063-7 (`psubscribe("revision:*")` counts everybody's frames), 050-8, 062-12, 043-1. Open here: the api connects as a superuser, and a non-superuser role is what would make the immutability claim strong.
- [ ] T074 Run `specs/064-chapter-4-18/quickstart.md` end to end and correct it in place, recording each wrong version. **Four of its sections are marked MEASURED and were run at plan time; the rest are predictions** — the last four chapters' quickstarts were wrong three, four, three and five times at exactly this point.
- [ ] T075 **Check FR-012 rather than trusting it** (SC-007a): `git diff --name-only` the platform changes and confirm in `specs/064-chapter-4-18/baseline.txt` that every file outside tests and documents is one the chapter is for. Chapter 4.17's came back two files, both tests.
- [ ] T076 Stop the composed services **by name** — `api gateway dispatcher media-worker`, and **not `ingester`**, which has no Dockerfile and makes the whole command fail.
- [ ] T077 Run the full lane set once more with nothing else against the stack and record every REAL exit code in `specs/064-chapter-4-18/baseline.txt`, compared **per test** against T002's baseline rather than by colour.
- [ ] T078 Confirm every phase was committed as it closed, in `specs/064-chapter-4-18/baseline.txt`.
- [ ] T079 **Push submodules first, then the superproject** — `relay-platform`, then `relay-tutorial`, then the repository root. `.github/workflows/ci.yml` is the outer repository's and the other two are gitlinks, so the reverse order checks out commits no remote has.
- [ ] T080 Compare the CI error set **per error** against T004's baseline, in both directions, and record it in `specs/064-chapter-4-18/baseline.txt` (SC-008). One comparison supports *"this run introduced nothing new"*, not *"the set is stable"*.
- [ ] T081 If CI is red, fix the platform, then **re-dump, re-hunk `relay-tutorial/fences/post-series.md`, and push both** — repairing a platform file invalidates the appendix hunks that publish it.
- [ ] T082 Tag `part4-ch18` in `relay-platform`, annotated, on a commit CI has proved green.
- [ ] T083 Compress 063's `CLAUDE.md` entry to its headline, measurement block and still-cited findings, and add this one. **`wc -c CLAUDE.md` before and after** against the 150,000 budget, rather than a figure carried from a task written days earlier.
- [ ] T084 Remove the active-plan line from between the `SPECKIT` markers in `CLAUDE.md` when the feature closes, so the next feature's line replaces a plan rather than joining a list.

---

## Dependencies & Execution Order

```
Phase 1  →  Phase 2 (the set, which the writes need)
Phase 2  →  Phase 3 (US1)  →  Phase 4 (US2)
Phase 2  →  Phase 5 (US3)          the publication, not the decision
Phases 3-5  →  Phase 6  →  Phase 7  →  Phase 8  →  Phase 9
```

**T005 blocks T010, and T006 blocks T011.** A classification written against a parsed route list
is a classification of the wrong set, and a decision about where the classification lives,
taken without the fence bill, is a guess about the expensive half.

**T019 and T020 block T030, and both block the close.** A mechanism that has not been attacked
has not been checked, and SC-002 is the criterion that cannot be satisfied by writing code.

**T070 comes after T050**, not before. Chapter 4.16's CI went red on a coverage pin added after
the chain was taken to zero — and the edit that broke it was the ratchet being tightened, which
is the version of that mistake that feels safest to make.

**US2 depends on US1** for the entries to read. **US3 depends on phase 2's decision, not on US1
or US2** — its checks run against the classification, which exists before any entry does.

### Parallel opportunities

**Seven, and the number is small on purpose.** Every task in phases 1 and 6 appends to
`specs/064-chapter-4-18/baseline.txt`, so none of them is parallel however independent the
measurement behind it is.

- **Phase 1**: none. The nine measurements are independent and the file they write is one.
  T002 and T005 additionally run lanes and must not overlap each other or anything else
  against the stack.
- **Phase 2**: none. Every task writes `routes.md` or decides something the next task uses.
- **Phase 3**: none. T016–T018 look parallel and are not — the migration, the trigger and the
  schema declaration are one change across three files, and the first failure is what tells you
  the other two are wrong.
- **Phase 4**: none marked. T032 and T033 are separate files and could overlap; T034 needs both,
  and the sequence is short enough that the marker would buy nothing.
- **Phase 5**: T045 writes `clauses.md` and nothing else does.
- **Phase 6**: none. T046 and T047 run suites; T048 and T049 each need the composed stack to
  themselves; T051 writes the same file as the rest.
- **Phase 7**: T056, T058 and T060 touch `docs/05-sad.md`, `docs/` and `traceability.md`
  respectively. T053 writes `baseline.txt` and is not among them.
- **Phase 8**: T063 writes `figures.ts` and T071 writes nothing.
- **Phase 9**: T073 writes `gaps.md`.

---

## Implementation Strategy

### MVP

**Phase 1 + Phase 2 + Phase 3.** US1 alone is the clause: a moderation action leaves a record
nothing in the application can change. US2 makes it readable and US3 makes it checkable, and
neither is worth building against a set nobody decided or a table nobody attacked.

### What this feature must not do

- **Change the behaviour of any action it records.** FR-012, checked at T031 per action and at
  T075 against the diff. Chapter 4.2 built four items of a later chapter's brief and that
  chapter ceased to exist; the way that happens is one useful addition at a time.
- **Claim immutability the probe does not support.** One `SET` disables every trigger in the
  session and the api connects as the role that may issue it.
- **Build FR-MOD-01, FR-MOD-02 or the retention job.** Rows 20 and 21 own them.
- **Resolve what erasure does to an entry naming an erased user.** Row 22 owns it; this chapter
  writes the tension down where that chapter will find it.
- **Absorb a repair.** A defect found in an earlier chapter's work is recorded with its bill and
  scoped deliberately.
