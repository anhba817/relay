# Tasks: Tutorial Chapter 3.12 — "Milestone: the isolation gauntlet"

**Feature**: `specs/033-chapter-3-12` | **Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

**Deliverable**: the cross-tenant attack suite constitution I has required since it was
written and the repository has never had — deriving its own targets so a new endpoint
cannot skip it, judged on indistinguishability rather than refusal, and shown to go red
for three faults before it is trusted. Plus the two public endpoints that make the SRS
Phase 2 exit criterion reachable at all, and reachable documentation for all thirteen
error codes.

## Format: `[ID] [P?] [Story] Description`

- **[P]** — parallelisable: different file, no dependency on an incomplete task
- **[US1]…[US6]** — the user story from spec.md this task serves
- Setup, Foundational, Verification, Publication and Close-out tasks carry no story
  label
- **A lettered id** (`T031a`) is a task inserted by an `/speckit-analyze` pass, numbered
  against the task it belongs beside. It may run *before* its base task where it is a
  prerequisite

## Path Conventions

Platform paths are relative to `relay-platform/`, tutorial paths to `relay-tutorial/`,
document paths to the repository root, spec paths to `specs/033-chapter-3-12/`.

**Tasks that run a command rather than edit a file carry no path** — the baseline runs,
the gates, the battery, the counts, the reintroductions.

## The plan's eleven phases are fourteen commits

Recorded so the two documents can be checked against each other rather than assumed to
agree. Plan phase 2–5 is one story across three surfaces, and each surface commits
separately because CLAUDE.md's rule is one commit per phase and a 25-task commit is not
one. Plan phase 11 is four phases in practice, the shape chapter 3.11 used.

| Plan phase | Tasks phase |
|---|---|
| 1 Baseline | 1 |
| 2 Target list | 2 (foundational) + 3 |
| 3 REST gauntlet | 3 |
| 4 Structural check | 4 |
| 5 Socket gauntlet | 5 |
| 6 Two endpoints | 6 |
| 7 Reintroductions | 7 |
| 8 Instruments | 8 |
| 9 Documentation half | 9 |
| 10 The outsider | 10 |
| 11 Close-out | 11 verification, 12 chapter, 13 publication, 14 close-out |

## Which lane, and which file

**Generated against the final numbering, not extended by hand.** Chapter 3.11's
equivalent table was wrong in every analysis pass — 12/62, then 13/66, then 17/77 — and
every error came from adding a row to a list instead of regenerating it. This one was
wrong too on its first draft, mapping the outsider tasks to `T085–T093` when they are
`T097–T104`; and analysis pass one found a row naming
`services/api/src/limits/limits.itest.ts` for a port that is in
`services/gateway/src/limits.itest.ts`.

| Tasks | File | Why there |
|---|---|---|
| T009 | `services/api/src/isolation/fixtures.ts` | two tenants, so every attack has a victim and an attacker |
| T010, T010a | `services/api/src/isolation/compare.ts` + `compare.test.ts` | the oracle, lifted out of `messages.itest.ts` |
| T011, T012, T015 | `services/api/src/isolation/targets.ts` | the shapes, the classification list, the derivation |
| T016–T020 | `services/api/src/isolation/targets.itest.ts` | the derivation's four self-checks and its counts |
| T023–T026 | `services/api/src/isolation/attack.ts` | one function per shape; not parallel with each other |
| T030a–T030d | `services/api/src/auth/` — `credential.guard.ts`, `authenticate.middleware.ts` | `AcceptSpec`, so `@Accepts("platform")` stops compiling (R24) |
| T030d | `services/api/src/internal/usage.controller.ts`, `dispatch.controller.ts` | the five platform routes declare their services |
| T027–T033, T031a, T031b, T036a | `services/api/src/isolation/gauntlet.itest.ts` | 22 routes, in process, so the coverage run sees the branches it exercises (R1) |
| T037 | `services/api/src/db/catalogue.ts` | the `information_schema` read, inside the directory where the query engine is permitted (R23) |
| T037–T041 | `services/api/src/isolation/tenant-scope.itest.ts` | the classification and its assertions, no HTTP and no raw SQL |
| T013, T044–T050, T062 | `services/gateway/src/isolation.itest.ts` and `isolation-fixtures.ts` | a socket needs a real gateway; the lane already spawns an api child |
| T052, T078a | `services/api/src/db/repository.ts` | `addMember`'s upsert, and the branches the ratchet counts |
| T053–T057 | `services/api/src/channels/` | the two endpoints |
| T058–T060 | `services/api/src/channels/channels.itest.ts` | their own isolation surface, tested here as well as through the gauntlet |
| T069–T071 | `packages/test-harness/src/sentinel.sql` | feature 030's surface — **post-series fences** |
| T072 | `packages/test-harness/src/guard.itest.ts` | driving each newly guarded table — **post-series fences** |
| T073, T074 | `packages/test-harness/src/exempt.ts` | the list and its comment — **post-series fences** |
| T069a–T069e | `eslint.config.mjs` | the itest lint ban, restored and bounded (R23) |
| T076 | `services/gateway/src/limits.itest.ts` | the random port — **fenced by nothing**, so no fence entry either way (R17) |
| T082a, T097a | `turbo.json` | env entries; strict mode filters what it does not declare |
| T117a–T117c | published chapter pages | `REVISED` notes and illustrative JSON this chapter falsifies |
| T080–T082, T030c1, T051a | `packages/protocol/src/codes.ts` | thirteen codes and one URL function |
| T091, T092 | `packages/protocol/src/codes.test.ts` | every emitted code is registered — self-contained |
| T091a | `relay-tutorial/scripts/` | registry ↔ reference, where the parent repo is in scope (R26) |
| T098c | `.github/workflows/ci.yml` | the `outsider` job: compose for everything (R25) |
| T086 | `docs/08-error-reference.md` | a source document, mirrored by the site |
| T097–T104 | `packages/outsider/` | the only package in the repository that may import nothing |

**Tasks that run a command rather than edit a file carry no path** — the baseline runs,
the gates, the battery, the counts, the three reintroductions, the two scratch probes.

---

## Phase 1: Setup & baseline

- [X] T001 Record provenance in `specs/033-chapter-3-12/baseline.txt`: the submodule commits this chapter starts from, confirmation that `relay-platform` is at `part3-ch11`, and that both parent pins match their submodule HEADs
- [X] T001a **Record the four variables the coverage lane needs, in `baseline.txt`, before T002 runs it.** `RELAY_INTERNAL_CREDENTIAL`, `RELAY_WEBHOOK_SECRET_KEY`, `RELAY_REDIS_URL`, `RELAY_NATS_URL` exist only in `.github/workflows/ci.yml`. Without them `pnpm coverage` fails 11 tests across 3 files and none of the messages names the cause — a missing platform credential fails `limits.itest.ts` and cascades into eight dispatcher assertions, and NATS returns `CONNECTION_REFUSED`. Research R22 measured this by getting it wrong first; do not spend the run again
- [X] T002 Record the pre-change platform baseline in `specs/033-chapter-3-12/baseline.txt` — unit and integration counts per package, coverage, every per-file ratchet in force, and the exit code of each gate rather than a grep over its output. Chapter 3.11 closed on **348 unit** and **330 integration**; record what this machine measures
- [X] T003 [P] Record the site baseline in `specs/033-chapter-3-12/baseline.txt`: `pnpm lint`, `pnpm build`, `pnpm check:docs` and `pnpm check:fences` in `relay-tutorial/`, with the file, chapter and locale counts the chain reports. Chapter 3.11 closed on **177 fenced files across 28 chapters**
- [X] T004 **Run the integration lane three times and record every failure.** A lane with a pre-existing intermittent failure cannot measure a new one, and this chapter's whole subject is a suite whose red means something
- [X] T005 Fix forward, with its own commit, anything T004 finds that is not this chapter's work
- [X] T006 Add `"json"` to `reporter` in `vitest.coverage.config.mts`. `json-summary` carries totals and not locations, so without this FR-040 can count the uncovered branches and not name them — found in R16 by trying to list them and getting a file that does not contain them
- [X] T007 **Record the isolation code's starting position in `baseline.txt`, by line.** `repository.ts` measures 97.50 / **90.60** / 100 / 99.45 with branches **241/266 — 25 uncovered arms** — against a pinned 97/90/100/99. Two lines are uncovered (152, 3140) and functions are at 100%, so almost all 25 are unhit arms on covered lines. Enumerate them from `coverage/coverage-final.json` now that T006 emits it; this list is what FR-040 is measured against
- [X] T007a [P] Record in `baseline.txt` that the same commit measured 90.32/83.98/89.51/91.53 at chapter 3.11's close-out and 90.37/84.17/89.51/91.58 during this chapter's research, with no code between them. The lane's coverage is mildly data-dependent on what the test database has accumulated, so a movement under 0.1 is noise rather than a result
- [X] T008 [P] **Record the route surface as it stands, generated rather than typed.** Boot the built `AppModule` and print `router.stack`'s routes into `baseline.txt`: 22 routes plus 8 middleware layers. Every later count of attacked-plus-exempt is compared against this number, and R2's probe is the only reason it is 22 rather than an estimate

**Checkpoint**: the starting numbers exist, the lane is green for a known reason, the 25 branch arms have names, and the route surface has been counted rather than remembered.

---

## Phase 2: Foundational — the fixture, the oracle, and the shape of a target

- [X] T009 Create `services/api/src/isolation/fixtures.ts`: a helper minting two environments with a key each and one channel, user, webhook endpoint and message apiece, so every attack has both a victim and an attacker. Rows are created through the repository, scoped to environments this file created, and nothing is deleted across environments (FR-011)
- [X] T010 Move the whole-body comparison out of `services/api/src/messages/messages.itest.ts` into `services/api/src/isolation/compare.ts` and have the original import it. The helper and its reasoning already exist there — "the id is the one field that reveals nothing about the resource, so it is the one field the comparison must drop" — and duplicating it into a second file is the fault this chapter is about (FR-004, R3)
- [X] T010a [P] Unit test `compare.ts` in `services/api/src/isolation/compare.test.ts`: two bodies differing only in `request_id` are equal, two differing in `message` are not, and a non-object body is handled. Pure, no database
- [X] T011 Define the target and classification shapes in `services/api/src/isolation/targets.ts` per `data-model.md` §2: `method`, `path`, `shape` in `read | list | write | credential | exempt`, and `because` required when the shape is `exempt` (FR-003)
- [X] T012 [P] Write the classification list in the same file, covering all 22 routes: three exempt with reasons (`GET /healthz`, `GET /auth/:provider/start`, `GET /auth/:provider/callback`), one `credential` (`POST /auth/dev-token`), one `list` (`GET /v1/webhooks`), two `read`, and the rest `write`. **`POST /auth/dev-token` is the shape the specification did not anticipate** — it takes no tenant-owned identifier and is still tenant-scoped, so filing it as exempt is how a route stops being attacked (R4)
- [X] T013 [P] Add the two-tenant fixture's gateway-side twin to `services/gateway/src/isolation-fixtures.ts` — two environments and a user token for each, minted through the api child the lane already spawns (FR-007, FR-011)
- [X] T014 [P] Confirm no new file needs an entry in `packages/test-harness/src/exempt.ts` or the matching `eslint.config.mjs` ignores. If one does, add it to **both** — the lists' own comments say they must agree, and chapter 3.11 found `drainQuotaNotifications` on neither (FR-042)

**Checkpoint**: two tenants can be created, their answers can be compared, and a target has a shape — and nothing attacks anything yet.

---

## Phase 3: User Story 1 — the derived list and the REST surface (Priority: P1) 🎯 MVP

**Goal**: every endpoint attacked with another tenant's identifier, from a list the suite derives rather than remembers.

**Independent test**: walk the derived list, confirm every target is attacked or exempt with a reason, then add an unclassified route and confirm the suite fails.

- [X] T015 [US1] Implement the derivation in `services/api/src/isolation/targets.ts`: filter `app.getHttpAdapter().getInstance().router.stack` to layers carrying a `route`, and expand `route.methods` into one target per verb (FR-002)
- [X] T016 [US1] Add the three assertions that keep the derivation honest, in `services/api/src/isolation/targets.itest.ts`: the count is non-zero, `POST /v1/channels/:channelId/messages` is present, and the property is read from `router` with a named fallback to `_router`. **A derivation that finds nothing and reports an empty list would pass a suite that attacks nothing**, which is worse than the hand-written list it replaces (R2, `contracts/gauntlet.md` §1)
- [X] T017 [P] [US1] Assert in the same file that every derived target matches exactly one classification entry (FR-002, SC-002)
- [X] T018 [P] [US1] Assert the reverse: every classification entry matches a derived target. A stale exemption is how a route becomes unattacked after a rename, and only this direction catches it
- [X] T019 [P] [US1] Assert that every `exempt` entry carries a non-empty `because`. Nothing may be exempt by omission (FR-003)
- [X] T020 [US1] Print the attacked and exempt counts from the suite and assert they sum to the derived total, so SC-001's number comes off a run rather than out of prose
- [X] T021 [US1] **Verify T016's assertions fire.** Comment out one classification entry, run, confirm the failure names the route; restore. Then rename `router` access to a property that does not exist, run, confirm the failure is loud rather than an empty pass. Record both in `baseline.txt` (SC-002)
- [X] T022 [P] [US1] Add a throwaway `@Get("probe")` to `services/api/src/health.controller.ts`, run the suite, confirm it fails naming `GET /probe`, and remove the route. This is quickstart V2 and it is the only evidence that FR-002 is a property rather than a sentence
- [X] T023 [P] [US1] Write the `read` attack in `services/api/src/isolation/attack.ts`: issue the foreign-identifier request and the exists-nowhere request as a pair, and compare status, code and whole body through `compare.ts` field by field (FR-004, SC-003)
- [X] T024 [P] [US1] Write the `list` attack in the same file: a credential for an environment that owns nothing gets an empty **result** rather than a 404, and no row belonging to another environment. Assert emptiness in whatever form the endpoint returns — `GET /v1/webhooks` returns a bare array, not a page, because EIR-API-06's cursor pagination is unmet there (FR-006, R27)
- [X] T025 [US1] Write the `write` attack in the same file: read the target tenant's rows through `Repository` methods before and after — **not through raw SQL**, for T037's reason: the restored lint ban forbids the query engine outside `services/api/src/db/`, and this suite should not need an exemption (FR-043), and assert both the paired-response equality and that no row moved. **The state read is the point** — a 404 that completed the write is the case no status code reveals (FR-005, SC-004)
- [X] T026 [P] [US1] Write the `credential` attack in the same file: a key for environment A mints a dev token, and that token is refused against a channel in B (FR-004, R4)
- [X] T027 [US1] Wire `services/api/src/isolation/gauntlet.itest.ts` to boot `AppModule` with `Test.createTestingModule`, as ten other api suites already do, and run every derived target through the attack for its shape
- [X] T028 [P] [US1] Cover the two `read` targets: `GET /v1/webhooks/:id` and `GET /v1/channels/:channelId/messages` (FR-004)
- [X] T029 [P] [US1] Cover the `list` target: `GET /v1/webhooks` (FR-006)
- [X] T030 [P] [US1] Cover the seven public `write` targets: `POST /v1/channels/:channelId/messages`, **`POST /v1/webhooks`**, `POST /v1/webhooks/:id/rotate-secret`, `/enable`, `/disable`, `/test`, and `DELETE /v1/webhooks/:id`. Seven, not six — the webhook **create** route was missing from an earlier draft of this task and from `data-model.md`'s shape table, whose five rows then summed to 21 against a derived 22. T017 would have caught it as an unmatched target; the arithmetic caught it first (FR-005)
- [X] T030a [US1] Derive `PlatformService` from `PLATFORM_SERVICES` in `services/api/src/auth/authenticate.middleware.ts` rather than retyping the two names, so a third internal service widens the type on its own — chapter 3.11's `Dimension` lesson (FR-044, R24)
- [X] T030b [US1] Change `Accepts` in `services/api/src/auth/credential.guard.ts` from `...kinds: PrincipalKind[]` to `...specs: AcceptSpec[]` per `data-model.md` §8, so **`@Accepts("platform")` stops compiling**. An authorization that can be omitted is one that will be, and the platform has two internal callers with unequal exposure (FR-044)
- [X] T030b1 [US1] Update the refusal's message path, which `AcceptSpec` breaks. `expectation(kinds: PrincipalKind[])` at `credential.guard.ts:30` maps `describePrincipalKind` over the accepted list and feeds two client-visible strings — "this route requires a credential: …" at `:89` and "this route expects …" at `:96`. Both signatures widen with the decorator, and `credentials.itest.ts:419`'s platform-credential describe block asserts on what they produce. FR-046 names the mistake; this is the sentence that explains it (FR-044, FR-046)
- [X] T030c [US1] Make `CredentialGuard` check `principal.service` against the route's declared services, refusing with a `403` carrying **`wrong_credential_service`** — its own code, not the status's generic `forbidden`, because the class presented was right and the service was not. That is a third mistake, distinct from lacking a permission and from presenting the wrong class, and chapter 3.2 made the same argument when it added `wrong_credential_type` rather than answering "forbidden" (FR-044, FR-046)
- [X] T030c1 [P] [US1] Add `wrong_credential_service` to `ERROR_CODES` in `packages/protocol/src/codes.ts` with its one-line meaning, beside `wrong_credential_type` where the reader will look for it. **The emittable set becomes thirteen** once T051a's code lands too, and every figure describing what ships says thirteen — six documents carry that count and the reference's two-directional test is what fails if one is missed (FR-046, FR-024)
- [X] T030c2 [P] [US1] Test the refusal's message: it names the service and the permitted set — `"gateway" is not permitted on this route (dispatcher)` — and contains no part of the credential. A service name is a deployment label; a credential is a secret (FR-046, SC-031, NFR-SEC-06)
- [X] T030d [US1] Declare the services on the five platform routes: `{ platform: ["gateway"] }` on `services/api/src/internal/usage.controller.ts`, `{ platform: ["dispatcher"] }` on the four in `services/api/src/internal/dispatch.controller.ts` (FR-044)
- [X] T030e [P] [US1] Test both directions route by route in `services/api/src/internal/usage.itest.ts` and a dispatch suite: the gateway's credential is refused on every dispatch route, the dispatcher's on `/internal/usage/connections`. State the count of platform routes (SC-029)
- [X] T030f [P] [US1] Write a route declaring `@Accepts("platform")` with no service list, confirm it fails to typecheck, and remove it. The compiler is the mechanism; a test that only checks the happy path would pass with the old signature (SC-029)
- [X] T031 [US1] Cover the **five** `@Accepts({ platform: … })` targets with the named-environment attack: a request naming environment A carrying an identifier from B. These credentials carry no environment, so a foreign-credential attack is meaningless on them (FR-008, `contracts/gauntlet.md` §3)
- [X] T031a [US1] Cover the **three** `@Accepts("user")` targets — `/internal/messages`, `/internal/session`, `/internal/backfill` — with the foreign-**credential** attack: a token minted in A used against a resource in B. Their credential **is** scoped to one environment, so this is the same shape as the socket surface. An earlier draft of this task list gave all eight the platform attack, which would have left these three unattacked in their real shape (FR-008)
- [X] T031b [P] [US1] Write in the suite's own comment what a platform credential is trusted for after T030d — it carries no environment, names one per request, and is accepted only on routes declaring its service — and what still does not protect it: there is no rotation, and `service` is self-reported by which variable matched. Distinguish `POST /internal/dispatch/replay`, unscoped **by design** because the dispatcher serves every tenant, from a route unscoped by accident (FR-009, `contracts/gauntlet.md` §3, §7)
- [X] T032 [P] [US1] Assert `POST /internal/usage/connections` still answers `409 connection_environment_conflict` for a connection first seen in another environment. Chapter 3.11 built this refusal; the gauntlet generalises its judgement to the other seven routes rather than re-deciding it (FR-008)
- [X] T033 [P] [US1] Confirm the eleven existing scattered isolation assertions still exist and still pass, counted before and after. Eleven across eight files, not the nine across nine that earlier drafts said; the count is in `baseline.txt` with the grep that produced it. The gauntlet adds to the isolation surface; it does not relocate it off the code the coverage run measures (FR-010, SC-024)
- [X] T034 [US1] Add a comment at the top of `gauntlet.itest.ts` stating what the suite does not cover, from `contracts/gauntlet.md` §7 — timing, the internal credential's holders, message wisdom beyond equality, anything not routed through the HTTP router. A defence trusted past its range is worse than none, and this is where a reader meets the suite
- [X] T035 [P] [US1] Run the lane and confirm the gauntlet's fixtures are removed only by identifiers it created, with the guard armed. No cleanup may operate across environments (FR-011, SC-025)
- [X] T036 [US1] Record the attacked and exempt counts in `baseline.txt` against T008's 22 (SC-001)
- [X] T036a [US1] Confirm the gauntlet runs under `pnpm test:integration` with no separate invocation, so it executes on every build through the existing CI job rather than needing a workflow edit. FR-001 says "on every build"; a suite that only runs when someone remembers the command satisfies NFR-SEC-09 on paper (FR-001)

**Checkpoint**: 22 routes attacked or exempt with reasons, every answer compared against its twin, and an unclassified route fails the build.

---

## Phase 4: User Story 1 continued — the structural half

**Goal**: the leak that has no endpoint yet — a table that carries no tenant.

- [X] T037 [US1] Write `services/api/src/isolation/tenant-scope.itest.ts`: for every base table in `public`, derive `direct`, `hop` or `spine` from `information_schema` per `data-model.md` §4. **Put the catalogue query behind a function in `services/api/src/db/`, where the query engine is already permitted** — not inline in the test. T069a restores the lint ban that forbids `drizzle-orm` outside that directory, and a suite written in ignorance of it becomes a repair later or an ignores entry forever. A constraint known before the code is written is cheaper than either (FR-012, FR-043, R23)
- [X] T038 [P] [US1] Assert **totality, not counts**: every base table falls into exactly one of the three classes — `direct`, `hop`, `spine` — and a table matching none fails the check until somebody classifies it. Do not add a fourth class for tables that fit none; an empty bucket waiting to receive a violation is how a finding becomes a classification. Record the counts in `baseline.txt` instead of asserting them — `__sentinel_environments` is created by the harness and exists only after the lane has run, so "12 direct" is 11 or 12 depending on how the database was built (FR-012, SC-007)
- [X] T039 [US1] Write the `spine` list explicitly with a reason each — `organisations`, `applications`, `environments`, `humans`, `memberships`, `consumed_events`, `schema_migrations`, `outbox`. A list, not a pattern, for feature 030's stated reason. `outbox` and `consumed_events` are infrastructure rather than records: neither is on a read path to any API caller, and the outbox's only reader is the global relay whose whole job is to ignore tenancy (R7)
- [X] T040 [US1] **Record the outbox RETENTION finding in the list's own comment, with its numbers** — and record that it is not a tenancy finding, because an earlier draft of this feature said it was. `drainOutbox` sets `published_at = now()` and never deletes; **nothing in the api deletes a row from any table** (the only `.delete(` in non-test source is an in-memory `Map` eviction in `limits/fallback.ts:85`); and the payload is a full copy of the message, `data.text` included. **286,871 rows** in the test lane (R7a)
- [X] T040a [US1] Name the four requirements that collide with it, in the same comment: DR-06 and FR-MSG-08 (a deleted message keeps its row with `text` cleared and hard deletion runs only through the compliance endpoint — the text survives in the payload, so a tombstone that leaves a copy behind is not a tombstone), FR-TEN-08 (30-day erasure of an application's operational data, unreachable for these rows by any mechanism that exists), and FR-MOD-06 (per-environment retention with a scheduled hard-delete job). Owned by whichever chapter builds FR-MOD-06, which is Phase 3 and Part 4 (R7a)
- [X] T040b [P] [US1] State the fix and why it is not a column: `DELETE FROM outbox WHERE published_at < now() - interval 'N days'` reaches every row this is about and needs no tenant identifier. For a rare per-tenant compliance sweep, `subject`'s last segment already carries the environment id and the payload carries the key (R7a)
- [X] T041 [P] [US1] Note why adding `environment_id` would have been the wrong fix, since the reasoning is the useful part: the outbox's legitimate mutation **is** cross-environment, so a tenant column would make feature 030's guard refuse the relay's own sweep — `exempt.ts`'s line "`outbox` is not among them and needs no entry" was right. And a foreign key to `environments` would block deleting an environment while outbox rows exist, which makes FR-TEN-08 harder rather than easier (R7)
- [X] T042 [P] [US1] Create a table with no tenant column in a scratch migration, run the check, confirm it fails naming the table, and remove the migration (quickstart V6)
- [X] T043 [US1] Record the three class counts and the outbox retention entry in `baseline.txt` (SC-007)

**Checkpoint**: every table's tenant path is derived from the catalogue, and the one that has none is named with its cost rather than skipped.

---

## Phase 5: User Story 1 continued — the socket surface

**Goal**: a credential for one environment hears, sends and resumes nothing belonging to another.

- [ ] T044 [US1] Write `services/gateway/src/isolation.itest.ts` with the gateway in process and the api as a child, the arrangement chapter 3.2 established and 3.11 chose for the same reason (FR-007, R6)
- [ ] T045 [P] [US1] Attack the session: a token minted for environment A connects, and `channel_ids` contains nothing belonging to B (FR-007)
- [ ] T046 [P] [US1] Attack the send: a frame into a channel belonging to B is refused, and B's channel gains no message — read directly, not inferred from the refusal (FR-007)
- [ ] T047 [P] [US1] Attack the resume: a cursor naming B's channel backfills nothing (FR-007)
- [ ] T048 [P] [US1] Attack the subscribe: nothing from B's channel is delivered on A's socket (FR-007)
- [ ] T049 [US1] Classify all ten members of `@relay/protocol`'s `frameSchema` as `inbound` or `outbound`, each with a reason, in `services/gateway/src/isolation.itest.ts`. **This is a classification and not a derivation**: the union carries no direction metadata — no inbound/outbound split, no client/server types — so "derive the inbound ones" is not implementable, which an earlier draft of this task and of `contracts/gauntlet.md` §4 both claimed (FR-007, R6)
- [ ] T050 [P] [US1] Run the totality check in both directions: every union member is classified exactly once, and every entry names a real member. A new frame then fails the suite until somebody classifies it — the property the derivation was supposed to give, obtained the way T017 and T018 obtain it for routes
- [ ] T051 [US1] Record the socket attack count in `baseline.txt`

**Checkpoint**: the socket surface is attacked from a list the protocol package supplies, and a new frame type joins it without an edit.

---

## Phase 6: User Story 5 — a channel and its members over the public API (Priority: P2)

**Goal**: the two endpoints without which no outsider can send a message, and both attacked by the suite on the build that adds them.

**Independent test**: with only an API key, create a channel, repeat the request, add two members, send a message, and receive it on a socket for one of those members.

- [ ] T051a [P] [US5] Add `channel_member_limit_exceeded` to `ERROR_CODES` in `packages/protocol/src/codes.ts`. A registry key with no dependency on this phase's other work — the SRS names this code in its own worked example for EIR-API-04, and with it the shipped set is **thirteen** (FR-048)
- [ ] T052 [US5] Fix `addMember` in `services/api/src/db/repository.ts`. **It cannot back an endpoint as written**: there is no `ON CONFLICT` and `members`' primary key is `(channel_id, user_id)`, so a repeat raises a unique violation that `ProtocolErrorFilter` renders as `internal_error`. Its single boolean also conflates added, channel-not-yours and user-not-yours — correct for isolation, wrong for an idempotent endpoint (R14a)
- [ ] T052a [US5] Fix `createChannel` at `repository.ts:2571` the same way and for the same reason: it is a plain `insert(channels).values(...)`, so a repeated `external_id` raises against `channels_environment_id_external_id_unique` and reaches the wire as `internal_error`. Use `ON CONFLICT (environment_id, external_id) DO NOTHING RETURNING`, falling back to `getChannelByExternalId`, which already exists and is already scoped. Widen its signature to carry `metadata`, which FR-CHN-01 requires and the column already has. **Not a read-then-insert in the service**: that races, and Principle II requires idempotency "enforced at the storage layer (unique index), not in application memory" (FR-017, R14a)
- [ ] T053 [P] [US5] Write `services/api/src/channels/channels.schema.ts`: the create body (`external_id`, `type`, optional `name`, optional `metadata` bounded at 8 KB — **all four of FR-CHN-01's elements**, and `channels.metadata` is a jsonb column with a default already) and the members body (`user_ids`, capped at 100 per FR-CHN-06), both zod and both rejecting unknown fields (FR-016, NFR-SEC-04)
- [ ] T053a [US5] Make the create schema's `type` enum **`["public"]` and nothing else**, so `private` is refused with `invalid_request` naming the field. `channels.type` has been a `"public" | "private"` column with a CHECK constraint since chapter 2.1 and **nothing reads it** — history and send scope by `environment_id` alone, with no membership check anywhere — so FR-CHN-05, a P1 clause, is unimplemented. A public endpoint accepting `private` would sell a guarantee the platform does not keep (FR-047, SC-032)
- [ ] T053b [P] [US5] Test that `private` is refused with the field named, that `public` succeeds, and that metadata round-trips and is refused over 8 KB (FR-016, FR-047, SC-014, SC-032)
- [ ] T054 [US5] Write `services/api/src/channels/channels.service.ts`: idempotent creation on the customer-supplied identifier, and a members path that reads the channel scoped first, then upserts. The scoped read is what makes a foreign channel and an absent one answer identically while "already a member" stays a success (FR-016, FR-017, FR-019)
- [ ] T054a [US5] Enforce FR-CHN-07 in `services/api/src/channels/channels.service.ts`: a channel holds at most 1,000 members, and an add that would exceed it is refused with `422` and T051a's code. **Numbered after T054 on purpose** — an earlier draft had this as T051a, five tasks before the file it edits existed (FR-048)
- [ ] T055 [US5] Write `services/api/src/channels/channels.controller.ts`: `POST /v1/channels` and `POST /v1/channels/:channelId/members`, both behind `CredentialGuard` with `@Accepts("application")`, per `data-model.md` §7 (FR-016, FR-019)
- [ ] T056 [P] [US5] Return `201` on creation and `200` on the idempotent repeat — the distinction chapter 2.3 drew for a duplicate send, and one an integrating developer can act on. FR-CHN-02 says return the existing channel, not return the same status (FR-017)
- [ ] T057 [US5] Register the controller in `services/api/src/app.module.ts` (FR-016, FR-019)
- [ ] T058 [P] [US5] Integration tests in `services/api/src/channels/channels.itest.ts`: creation, the idempotent repeat, two tenants using the same external id independently, members added, and users created on first membership (FR-016 to FR-019, SC-014)
- [ ] T058a [P] [US5] Test the member ceiling from storage: adding the 1,001st member is refused with `422` and the limit's code, and the channel still holds 1,000 afterwards — read back rather than inferred from the status (FR-048, SC-033)
- [ ] T059 [P] [US5] Test that adding the same member twice is a success naming them as already a member, not a 500 (T052's fault, asserted rather than assumed)
- [ ] T060 [P] [US5] Test the foreign cases directly here as well as through the gauntlet: another tenant's channel id answers exactly as an absent one, for both endpoints, and that channel's membership is unchanged (FR-018, US5 scenario 6)
- [ ] T061 [US5] Add the two routes to the classification list in `services/api/src/isolation/targets.ts` — as `write` — and re-run Phase 3's suite. **The routes must have appeared in the derived list on their own**; if they appear as unclassified, that is the correct failure and the classification is what changes, never the derivation (FR-021, SC-016)
- [ ] T062 [P] [US5] Test that a member added over the public API receives a message on a socket, in `services/gateway/src/isolation.itest.ts` or beside it — with no repository call and no harness fixture in the test (FR-020, SC-015)
- [ ] T063 [US5] Record the derived target count in `baseline.txt`: 22 before, 24 after
- [ ] T063a [US5] Reassess the seam in `packages/e2e/src/harness.ts`. Its comment says the suite seeds through the repository because "there is no admin API to create an environment, a user or a channel yet — that is Part 3's tenancy work"; two of those three now have one. State which repository functions the seam still needs as a difference against the list it needed before — a shorter list, or the same list with the chapter that shortens it (FR-023, SC-027)

**Checkpoint**: an integration can create a channel and add members over the public API, and the gauntlet found the new routes without being told.

---

## Phase 7: User Story 2 — the suite has been shown to catch something (Priority: P1)

**Goal**: sensitivity, measured. A suite that has never failed is an untested test.

**Independent test**: revert one scoping predicate, run, confirm red; restore, confirm green.

- [ ] T064 [US2] Reintroduction 1: drop `environment_id` from one repository `SELECT`, run the gauntlet, record which assertion fired, revert with `git checkout` (FR-013)
- [ ] T065 [US2] Reintroduction 2: drop it from one `UPDATE`, run, and confirm the failure is on the **before/after row comparison** rather than on a status. If it fails only on status, the `write` shape is not doing its job and T025 is wrong (FR-013)
- [ ] T066 [US2] Reintroduction 3: change one endpoint's 404 to a 403, run, confirm the failure is on the indistinguishability comparison (FR-013)
- [ ] T067 [US2] Record all three in `baseline.txt` with the exact assertion text, **and record which assertions stayed green**. Three faults chosen by the suite's own author measure sensitivity to three faults, not coverage of the class — the chapter says so rather than presenting three passes as proof (FR-014, SC-005)
- [ ] T068 [US2] Confirm the working tree is clean and review the phase's diff for the three touched files. FR-015 asks how "no reintroduction shipped" is verified rather than asserted; this is the verification (FR-015, SC-006)

**Checkpoint**: the suite has gone red three times for three faults, and the chapter knows which of its assertions did the work.

---

## Phase 8: User Story 6 — the instruments are themselves verified (Priority: P2)

**Goal**: the guard sees the four tables it has been blind to, no suite binds a fixed port, and the isolation code's coverage is a number rather than a restatement.

**Independent test**: plant a sentinel row in each of the four usage tables, drive a cross-environment mutation, confirm refusal.

- [ ] T069a [US6] **Restore the lint ban Principle I relies on.** `eslint.config.mjs` has two flat-config blocks naming `no-restricted-imports`, and the second — `files: ["**/*.itest.ts"]`, feature 030's global-drain restriction — **replaces** the first rather than merging with it, so the `pg` and `drizzle-orm` ban is not in force for any integration test. Measured: `npx eslint services/api/src/quotas/period.itest.ts` exits 0 while that file imports `drizzle-orm` and is not in the ignores list. Merge both restriction sets into one configuration for `**/*.itest.ts` rather than leaving two that overwrite each other (FR-043, R23)
- [ ] T069b [US6] Measure which integration tests genuinely need the driver or the query engine, and give each an ignores entry with a reason — at least `services/api/src/db/*.itest.ts`, `services/api/src/quotas/*.itest.ts` and `services/gateway/src/limits.itest.ts` today. A list with reasons, not a directory pattern, by the doctrine `exempt.ts` states. **`services/api/src/isolation/**` must not appear on it**: T025 and T037 were written to the constraint rather than around it, and this list is where that shows (FR-043, SC-028)
- [ ] T069c [US6] Correct the comment above the first block. It reads "`limits.itest.ts` is the one TEST allowed a raw client, and for a reason the rule cannot express" — every test is allowed one, and has been since the second block was added. The `ignores` entry for `services/gateway/src/limits.itest.ts` has been redundant for as long (FR-043)
- [ ] T069d [US6] Add an import of `drizzle-orm` to an integration test outside the permitted set, confirm `pnpm lint` fails, and remove it. State the count of legitimately exempted files (SC-028)
- [ ] T069e [P] [US6] State in the same comment what the restored rule does not buy: it sees an import, so a test reaching raw SQL through a helper in another file or through the repository's own `db` handle is invisible to it — the boundary feature 030's contracts already drew for this rule at a different scope (FR-043)
- [ ] T069 [US6] Add the four tables to the trigger array in `packages/test-harness/src/sentinel.sql`: `usage_periods`, `usage_active_users`, `quota_notifications`, `usage_connections` (FR-036)
- [ ] T070 [US6] Change the refusal message's key expression to `coalesce(to_jsonb(OLD) ->> 'id', to_jsonb(OLD)::text)`. **Extending the array alone produces a guard that fails on the writes it permits** — three of the four have composite primary keys and no `id`, and `OLD.id` raises `record "old" has no field "id"` at execution time. Measured on both shapes in R15 (FR-037)
- [ ] T071 [P] [US6] Add a comment beside it stating that the fallback prints the row, that these four carry counters, dates and identifiers and no message text, and that the same fallback on `messages` would be an NFR-SEC-06 violation
- [ ] T072 [US6] Drive a cross-environment mutation against each of the four and confirm the refusal names the table, in `packages/test-harness/src/guard.itest.ts`. Being in the array is not evidence of being watched — chapter 3.10's SC-008 passed by not being watched (FR-038, SC-017)
- [ ] T073 [P] [US6] Update `packages/test-harness/src/exempt.ts`'s comment: the guarded set is nine tables, not five. Its doc comment currently says "the five in `sentinel.sql`"
- [ ] T074 [P] [US6] Check whether any existing exempt entry now needs table names added, since four newly guarded tables may be written across environments by a suite already on the list — `notifications.itest.ts` drives the quota relay, which claims `quota_notifications` rows globally (FR-042)
- [ ] T075 [US6] Register `sentinel.sql` and `exempt.ts` changes in `relay-tutorial/fences/post-series.md`. Feature 030 publishes no chapter and a published chapter may only fence what it teaches (FR-039, R21)
- [ ] T076 [US6] Replace the fixed `?? 4124` in **`services/gateway/src/limits.itest.ts`** with a random high port, as `session.itest.ts:106` (`4400 + random*200`) and `meter.itest.ts:64` (`4610 + random*60`) now use. **Two files are called `limits.itest.ts`** and the api's binds no port — the earlier draft of this task, the plan and the research all named the api's, so the fix would have edited the wrong file and left the defect. **No fence work**: neither file is fenced by any chapter or by `post-series.md`, measured, against 3.11's note calling it "another chapter's fenced file" (FR-041, R17)
- [ ] T077 [P] [US6] Audit every suite that spawns an api or gateway for a fixed port and record the list in `baseline.txt`. `limits.itest.ts` is the one CLAUDE.md names; the audit is what makes SC-020 a measurement (SC-020)
- [ ] T078 [US6] Run `pnpm coverage` and record `repository.ts` against T007's 241/266. Either close constitution VI's 100% clause or name every remaining uncovered branch with the reason it is uncovered. The ratchet may not end lower than it started (FR-040, SC-018)
- [ ] T078a [US6] Cover what the gauntlet reaches in process. The suite exercises repository reads and writes with foreign ids, which is exactly the branch class the ratchet counts — measure before writing new tests, because chapter 3.11's R23 predicted a fall here and got a rise for this reason
- [ ] T079 [P] [US6] Update the ratchet entries in `vitest.coverage.config.mts` to whatever T078 measured, upward only — and **decide explicitly whether this chapter's new files get an entry**. `services/api/src/isolation/*.ts`, `channels/*.ts` and **`services/api/src/db/catalogue.ts`** are inside the coverage `include` glob and would otherwise be pinned by nothing but the global 70. The last of those matters most: it lands in `services/api/src/db/`, the one directory that already carries a per-file ratchet, and it is the directory constitution VI's 100%-branch clause is about. Chapter 3.11's T033c pinned new code deliberately, for the reason its comment gives: an unpinned file is a figure that can slide. State the decision either way

**Checkpoint**: nine guarded tables verified by driving each, no fixed ports, and the 100% clause answered with a number and a list.

---

## Phase 9: User Story 4 — the error vocabulary and its pages (Priority: P2) — separable

**Goal**: thirteen codes, one registry, one URL rule, and a page that resolves.

**Independent test**: enumerate every code the platform can emit and confirm each resolves to a section of the published reference; add a code with no entry and confirm the build fails.

- [ ] T080 [US4] Add the five missing keys to `ERROR_CODES` in `packages/protocol/src/codes.ts`: `invalid_request`, `forbidden`, `not_found`, `internal_error`, `connection_environment_conflict`, each with its one-line meaning. With `wrong_credential_service` from T030c1 the registry then holds **thirteen** — the eleven the platform can emit today plus this chapter's own (FR-024, FR-026)
- [ ] T081 [US4] Type the status ladder in `services/api/src/protocol-error.filter.ts` as `ErrorCode`, so an unregistered code stops compiling rather than reaching the wire undocumented (FR-025)
- [ ] T082 [P] [US4] Add `docsUrl(code)` beside the registry, reading a base from `RELAY_DOCS_BASE_URL` with the published reference's URL as the default, and returning base + `#` + the code verbatim (FR-027, `contracts/errors.md` §2)
- [ ] T082a [US4] Add `RELAY_DOCS_BASE_URL` to `turbo.json`'s `test:integration` env list, and to the `test` task's inputs if a unit test reads it. **Turbo's strict env mode filters what it does not declare**, so an undeclared variable is invisible to the task and the test silently exercises the default. Chapter 3.11 needed exactly this entry for the gateway's credential; the live proof that it matters is `RELAY_LIMITS_ITEST_API_PORT`, which is absent from that list and therefore unusable — which is why 4124 is the only port that ever runs (FR-027, R17)
- [ ] T083 [US4] Replace all six construction sites with `docsUrl()`: `services/api/src/protocol-error.filter.ts:73`, `services/api/src/limits/rate-limit.middleware.ts:122` and `:220`, `services/gateway/src/session.ts:72` and `:103`, and — via T084 — `packages/service-kit/src/index.ts:85`. **Full paths, not basenames**: resolving `limits.itest.ts` to the wrong one of two files is what analysis pass one found in T076 (FR-027)
- [ ] T084 [US4] Give `ServeOptions` in `packages/service-kit/src/index.ts` a required field carrying the not-found `docs_url`, and supply it from `services/gateway/src/main.ts`. **The dependency inverts rather than being added**: service-kit declares no dependencies at all and `serve()` has exactly one caller, so the compiler makes that caller supply the URL and the package stays empty (R9)
- [ ] T085 [P] [US4] Point the call sites that name their own code at the registry rather than at a string literal: `services/api/src/auth/credential.guard.ts` ×2, `services/api/src/internal/usage.controller.ts`, `services/api/src/messages/messages.service.ts`, `services/api/src/internal/session.controller.ts`, `services/api/src/limits/rate-limit.middleware.ts` ×2, `services/gateway/src/session.ts` (FR-025, FR-026)
- [ ] T086 [US4] Write `docs/08-error-reference.md`: one `h2` per code for all **thirteen**, the heading being the code verbatim, each with meaning, cause and remedy. A retryable condition says what makes it retryable; one that is not says so (FR-024, FR-028)
- [ ] T087 [US4] Add `_` to the kept character class in `slugifyHeading` in `relay-tutorial/components/docs/doc-article.tsx`, so `## quota_exceeded` anchors at `#quota_exceeded`. **Measured blast radius**: zero chapter `h2` headings contain an underscore, one docs heading does (`ADR-03 … last_sequence …`), and zero links anywhere in the site point at a `/docs/<slug>#anchor`. Without this, `docs_url` would need the same transform maintained in two repositories with no test able to see both sides (FR-027, R10)
- [ ] T088 [P] [US4] Add the seventh `DocEntry` to `relay-tutorial/lib/docs.ts` with a `titleVi`. The Vietnamese route renders the same English source under a translated title with a standing note saying so, so no translation is owed (R11)
- [ ] T089 [US4] Replace the `0[1-6]-*.md` glob with an explicit file list in **both** `relay-tutorial/scripts/sync-docs.sh` and `scripts/check-docs-drift.sh`. The range stops at 6 on purpose — `docs/07-tutorial-plan.md` is not a published reference — so `0[1-8]` would publish the tutorial plan. An explicit list is feature 030's doctrine in a shell script (FR-029, R11)
- [ ] T090 [P] [US4] Run `pnpm sync:docs` and `pnpm check:docs` and confirm the seventh document mirrors and matches. **Check this one specifically**: a document in the registry and not in the sync list renders whatever `content/docs/` last held, and the drift check does not notice, because it only walks files its own glob selects (FR-029)
- [ ] T091 [US4] Write the **platform** half in `packages/protocol/src/codes.test.ts`: every code the platform can emit is in `ERROR_CODES`. Self-contained — no file outside the workspace, so no turbo cache hole and no dependency on the parent repository (FR-025, SC-011)
- [ ] T091a [US4] Write the **tutorial** half as a check in `relay-tutorial/scripts/`: `ERROR_CODES` set-equal to the `h2` headings in `docs/08-error-reference.md`, **in both directions**. A code with no entry fails; an entry for a code that cannot be emitted also fails, because a reference documenting a retired code is how a documentation set starts lying. **Not in the platform's unit lane**, for two measured reasons: `docs/` sits above `$TURBO_ROOT$` so it cannot be a turbo input and the gate would pass stale from cache after the reference changed, and `relay-platform` is independently clonable with a README promising its checks pass from a clean checkout, where `../docs` does not exist. Skip with a warning when the parent is absent, as `check-docs-drift.sh` already does (FR-025, SC-011, SC-012, R26)
- [ ] T092 [P] [US4] Assert every entry names a cause and a client action. An entry that only restates the code's own name counts as missing (FR-028, SC-026)
- [ ] T093 [US4] Fetch a live error response's `docs_url` against the built site and confirm the anchor's `id` is present in the HTML. A URL that matches a pattern is not a URL that resolves (FR-027, SC-013)
- [ ] T094 [P] [US4] Add a twelfth registry key with no reference entry, confirm the build fails, remove it; then add an entry for a code that does not exist, confirm failure, remove it. Both directions or neither (SC-012, quickstart V10)

**Checkpoint**: thirteen codes in one registry, one URL function, and a `docs_url` that lands on a heading — the debt three chapters recorded, closed.

---

## Phase 10: User Story 3 — the outsider (Priority: P1) — separable

**Goal**: an integration built from published documentation alone, mechanically unable to know anything else.

**Independent test**: run the sealed package against a running stack; then add a workspace import and confirm the build fails.

- [ ] T095 [US3] Write `scripts/seed-demo-tenant.mjs`: create an organisation, an application, a development environment and one key, and print the key. The sealed integration cannot complete an OAuth consent screen, and there is no key-management endpoint — chapter 3.2 deferred it to "the dashboard's chapter". **It runs against an already-migrated database and before the suite**: stores, migrations, services, seed, suite — the seed writes rows the api's schema must already accept, and the suite needs a credential that must already exist (FR-032, R13, R25)
- [ ] T096 [US3] Document the seed command in `relay-platform/README.md` beside the compose and `pnpm dev` blocks, and **state which half of the constitution's clause it closes**: the clause says "`docker compose up` … including a seeded demo tenant", compose starts stores rather than services, so this closes the intent and not the letter (FR-032)
- [ ] T097 [US3] Create `packages/outsider/` with `package.json` declaring **no `@relay/*` dependency**, plus `vitest.integration.config.mts`, a `test:integration` script **and a `typecheck` script** — every other package in the workspace has one, and `pnpm typecheck` is `turbo run typecheck`, which silently skips a package that lacks the script. **Write the vitest config from scratch, not by copying a sibling.** Every other integration config points `globalSetup` and `setupFiles` at `../../packages/test-harness/src/…`, so copying one reaches into another package on its second line — and this package needs neither, because it touches no database (FR-030, R12) `vitest`, `ws` and `jose` resolve from the workspace root by the ordinary parent walk, so the package can run while declaring nothing (FR-030, R12)
- [ ] T097a [US3] Add whatever the outsider suite reads from the environment to `turbo.json`'s `test:integration` env list — the api and gateway base URLs and the seeded credential at minimum. Under strict env mode an undeclared variable does not reach the task, and this package has no fallback to a workspace constant, by design (FR-031)
- [ ] T098 [US3] Add a `no-restricted-imports` pattern rule for `packages/outsider/**` in `eslint.config.mjs`, refusing relative and absolute paths that climb out of the package. This is level 2 of three: pnpm's isolated `node_modules` already blocks `@relay/*` by package name, since `node_modules/@relay` does not exist at the workspace root (FR-030, R12)
- [ ] T098a [US3] Add a `no-restricted-syntax` rule for the same paths, banning `".."` string literals and `createRequire`. **This is level 3, and an import rule cannot reach it**: `packages/e2e/src/harness.ts:31` builds `join(HERE, "..", "..", "..")` and line 389 spawns the api's build output from it — a string, not an import specifier, so `no-restricted-imports` never sees it. The file cited as proof the hole exists is also proof the import rule does not close it. `eslint.config.mjs` has no `no-restricted-syntax` rule today (FR-030, R12)
- [ ] T098b [P] [US3] State in a comment what none of the three levels closes: reading the repository's source with human eyes. Three rules must not be left to imply a fourth (FR-034)
- [ ] T098c [US3] Add an `outsider` job to `.github/workflows/ci.yml` that uses compose for everything, in this order: checkout with submodules, pnpm setup, `pnpm install --frozen-lockfile`, `pnpm build` — **the four steps every other job in this workflow opens with, and `node services/api/dist/db/migrate.js` needs the build** — then `RELAY_POSTGRES_PORT=15432 docker compose up -d --wait` for the stores, migrations against `localhost:15432`, `RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d --wait` for the api and gateway, `node scripts/seed-demo-tenant.mjs`, then the sealed suite. **`RELAY_POSTGRES_PORT=15432` on every compose call**: `compose.yaml:22` defaults the host port to 5432 while the code defaults to 15432, so a bare `up` publishes a database the migration a line later cannot reach. **A separate job, not three lines in the platform job**: that job uses GitHub service containers on `localhost:5432` while compose's api reads `postgres:5432` on its own network, so adding `--profile services` there would start a second database, migrate the first, and leave the api serving a schema that does not exist. The job builds two Node images every run, which is the price of the target being external (FR-045, R25)
- [ ] T098d [P] [US3] Document the same sequence in `relay-platform/README.md` beside the existing compose block, including that `api`, `gateway` and `dispatcher` sit behind `profiles: ["services"]` so `docker compose up -d --wait` starts stores only (FR-045)
- [ ] T098e [P] [US3] Add `RELAY_API_URL` and `RELAY_WS_URL` to `turbo.json`'s `test:integration` env list. Strict env mode filters what it does not declare, and this package has no workspace constant to fall back to, by design (FR-045, R25)
- [ ] T099 [US3] Write `packages/outsider/src/integrate.itest.ts`: credential from the seed, `POST /v1/channels`, `POST /v1/channels/:id/members`, `POST /auth/dev-token`, `POST` a message, `GET` history, connect `ws://…/v1/ws`, receive. **It reads `RELAY_API_URL` and `RELAY_WS_URL` and starts nothing** — no `spawn`, no compose invocation, no process launch of any kind. With the platform absent it fails with a message saying so rather than trying to start one (FR-031, FR-045, SC-009, SC-030)
- [ ] T100 [P] [US3] Keep a running list of every fact the integration needed that published documentation did not contain, in `specs/033-chapter-3-12/gaps.md`, as it is written rather than afterwards (FR-033)
- [ ] T101 [US3] Give each gap a disposition — fixed here, or scheduled with a chapter number. **A list of zero is a result only if the chapter states how it was checked** (FR-033, SC-010)
- [ ] T102 [P] [US3] Demonstrate all three escapes failing, one at a time, and record each. (1) `import { ERROR_CODES } from "@relay/protocol"` — pnpm refuses to resolve it, no rule involved. (2) the same import by relative path — lint fails on T098's rule. (3) `readFileSync(join(import.meta.dirname, "..", "..", "protocol", "src", "codes.ts"))` — lint fails on T098a's rule. Remove each after measuring (SC-008, quickstart V13)
- [ ] T103 [US3] Write the paragraph FR-034 requires: the dependency rule is mechanical and not reading the source is a discipline, and content sufficiency is not comprehensibility. A person is the only instrument for the second and this chapter does not use one (FR-034)
- [ ] T104 [US3] Give the Phase 2 exit criterion a verdict — met, met in part, or not met — with the evidence for whichever it is, written into `specs/033-chapter-3-12/gaps.md` beside T100's list. **Not `chapter-notes.md` and not the page**: those are T123 and T110, four and two phases later, and an earlier draft of this task wrote into both before either existed. T110 and T123 collect it (FR-035, SC-021)

**Checkpoint**: an outsider's integration runs in CI, cannot cheat by package name, and the chapter has said what its passing does and does not prove.

---

## Phase 11: Verification

- [ ] T105 Walk every SC in spec.md and record its measurement in `baseline.txt`, including the ones that came out wrong
- [ ] T105a Build the traceability map: every one of this chapter's requirements against the SRS, constitution or ADR clause it implements, and every governing-document clause this chapter touches against the requirement that covers it. **Both directions**, because pass five found four SRS clauses the chapter touched without claiming — FR-CHN-05 contradicted, FR-CHN-07 unmentioned, FR-CHN-01 partly delivered, EIR-API-06 walked into. Eight of the chapter's requirements cited a governing id before that pass. The constitution's workflow section requires the reference; generate the map rather than extending one by hand, and mind that 3.11's traceability pass broke 36 files with a bad regex
- [ ] T106 [P] Re-derive the requirement and outcome counts — `grep -c '^- [*][*]FR-' spec.md` and the same for `SC-` — and correct plan.md's Constitution Check row if either moved. Chapter 3.11's equivalent row read "28 and 20" through three passes that each added requirements
- [ ] T107 **Run the integration lane twenty times, with a stopping rule.** Record the test count **and the wall-clock duration** for every run; a count that moves is a defect, not noise, and so is a mean that moves far. Chapter 3.11 recorded "330 every run, 193.30 s mean, 3 s spread" — the spread is how a timeout-shaped defect announces itself, and 3.11 shipped one (six Mailpit tests waiting through a 10 s helper inside a 5 s budget). This chapter adds a compose-driven job and thirty-odd suites, so state the budget a run may not exceed. **Abort on the first run whose failure is attributable to this chapter's code, fix it, and restart the count from one** — record the abandoned run's number and its cause. At roughly 193 s a run, twenty is about 64 minutes, and the rule is what saves thirteen of them. Chapter 3.11 abandoned its first attempt at run 7 (SC-019)
- [ ] T107a **Write down what twenty runs establishes and what it does not**, in `baseline.txt` and on the page. Twenty green runs give 95% confidence only against a per-run failure probability of about 14% or worse — `(1−p)²⁰ ≤ 0.05` needs `p ≥ 0.139` — and a 5% flake survives them unseen 36% of the time. **Chapter 3.11's own battery ran twenty green and an eleven-chapter-old flake surfaced on run twenty-one.** The chapter states the range of every other defence it builds; this is the one that had no range written down, and the counterexample was four commits back in this repository (SC-019)
- [ ] T108 [P] Run `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build`, `pnpm test:integration` and `pnpm coverage`, and record each exit code (SC-018, SC-019)
- [ ] T109 [P] Confirm no file was added to `packages/test-harness/src/exempt.ts` without the chapter naming the global operation that required it (SC-019, FR-042)

**Checkpoint**: every measurable outcome in spec.md has a number.

---

## Phase 12: The chapter, in English — and the size gate

- [ ] T110 Draft `relay-tutorial/app/(en)/part-3/chapter-12/milestone-the-isolation-gauntlet/page.mdx`, failure-first per Rule 1: the scattered nine assertions and what they cannot tell you, before the derived suite
- [ ] T111 [P] Write the `TRAP` box on the empty target list — a derivation that finds nothing and passes — and the `WHY` boxes citing NFR-SEC-09, FR-TEN-05, constitution I and V
- [ ] T111a Draw the chapter's figures with the series `Figure` component — **2 to 4, captioned, at least one in each half**, which is the bound `docs/07-tutorial-plan.md` has set since Part 0 and which no task made until analysis pass eight. Three subjects carry the chapter: **the derived target list** (router → 24 targets → five shapes, first half), **the two internal attack shapes** (a user token scoped to one environment against five platform routes that carry none, first half), and **the three levels of the outsider's seal** (pnpm, the import rule, the syntax rule — second half). Counted separately from specimen fences, which stay verbatim-quote territory
- [ ] T112 [P] Write the section on what the suite does not cover, from `contracts/gauntlet.md` §7. A chapter that lists its defence's range is the difference between this suite and the nine assertions
- [ ] T113 [P] Write the outbox finding into the chapter — **including the reversal**. The structural check said a constitutional clause was violated, the reasoning for the fix collapsed under a second look, and what was left was a retention problem four other requirements care about. A milestone chapter that reports only the findings that survived is reporting a tidier pass than the one that happened; the correction is the more useful half
- [ ] T114 **Count the finished page** — prose words outside fences, fences, figures, and the recurring boxes — and record it against the 2,000–4,000 bound. Two chapters in this part exceeded it and both were discovered afterwards. **Count the fences against the surface this chapter was planned to carry**: 16 new files and 21 amended — 37 — against chapter 3.11's 21 files and 34 fences, and chapter 3.5's 39 against an estimate of 22. An amended file needs a diff fence in this chapter's prose or the chain's HEAD property fails, so the fence count is a floor under the page rather than a by-product of it (SC-022, R19)
- [ ] T115 **Decide the split with the number, not with a feeling.** If the page is over, Phases 9 and 10 become chapter 3.13 and the milestone goes with them, because the Phase 2 exit criterion is the second half. Record the decision and the count either way. **State what taking it costs**, nearest first: this phase's own prose for Phases 9 and 10 has been written by the time the count exists, so the split discards sections just drafted; Phase 11's twenty-run battery, coverage figures and traceability map covered work that would no longer be in the chapter; and Phase 13's fence set would be wrong. A discard here, a Phase 11 re-run, a Phase 13 re-scope. That is an argument for forming an estimate at the phase-9 boundary rather than meeting the number here cold (R19, SC-022)

**Checkpoint**: the page exists and has been counted rather than estimated.

---

## Phase 13: Publication in both locales

- [ ] T116 Confirm the chapter's titled code fences replay byte-exact with `pnpm check:fences`. **There is no per-chapter fence file** — a fence is a titled code fence inside the page, and `relay-tutorial/fences/` holds `post-series.md` and nothing else. Every amended file needs a diff fence here, or the chain's HEAD property fails on the difference between the last fenced state and the file on disk
- [ ] T117 [P] Confirm `post-series.md` carries the `sentinel.sql`, `exempt.ts` and `limits.itest.ts` changes and that no chapter fences a file it does not discuss (FR-039)
- [ ] T117a Add a `REVISED` note to `relay-tutorial/app/(en)/part-1/chapter-04/walking-skeleton/page.mdx`, whose prose states that the `docs_url` host "is a placeholder until a docs site exists to make constitution V's promise real". After this chapter it resolves. `docs/07-tutorial-plan.md` §6's third defence requires the note — "never let prose and code disagree silently" — and chapter 3.11's close-out lists a shipped comment that had quietly stopped being true as one of the seven things implementation found
- [ ] T117b Fix the illustrative JSON in `relay-tutorial/app/(en)/part-3/chapter-02/keys-and-tokens/page.mdx:1232` and `:1480`, which shows `"docs_url": "https://relay.example/docs/errors/…"` in a response body. **No checker sees these** — they are prose examples, not fences — so they rot silently. Fifteen occurrences of `relay.example/docs/errors` exist across six published pages; the fenced ones are correct as earlier states of the chain and must not be touched
- [ ] T117c [P] Mirror T117a and T117b into the Vietnamese pages, and confirm `pnpm check:fences`'s mirror property still holds — the fence bodies are unchanged, so only prose moves
- [ ] T118 Translate to `relay-tutorial/app/(vi)/vi/part-3/chapter-12/milestone-the-isolation-gauntlet/page.mdx` with the `translate-mdx` skill. **The mirror check has three invariants before it reaches a body**: `check-fence-chain.mjs:278` joins `${f.lang} ${f.title}` for every fence in order and compares the whole list, then compares bodies positionally. So the same language tags, the same titles, in the same order — and only then identical bodies. A translator who writes ```typescript for ```ts, reorders two fences, or translates a title breaks MIRROR without touching a body, and this chapter carries the series' largest fence list at 37 files. Positional matching is also why repeated titles are safe, which matters where an amended file carries more than one diff fence
- [ ] T118a [P] **Figures are not fences and the mirror does not reach them** — which is what lets the plan's rule work: narrative labels translate, requirement, driver and ADR identifiers stay English. Stated separately from T118 so "byte-identical" is not read as freezing a figure's labels
- [ ] T119 **Update** the existing manifest entry at `relay-tutorial/lib/tutorial.ts:487` — do not add one. `id: "3.12"` is already there with the right path and title, `status: "forthcoming"`, and a `readerProduces` written before the chapter acquired two public endpoints, thirteen error codes, a sealed integration and service-scoped platform authorization. Set `status` to `published`, rewrite `readerProduces`, **add the missing `readerProducesVi`** (3.11 has one, 3.12 does not, so the Vietnamese page would render an English summary), and check `readerMinutes: 100` against the finished page — it is already Part 3's maximum, which may be right for 37 fenced files and should be measured rather than inherited. The manifest is one entry carrying both locales, not two
- [ ] T119a [P] Add `docs/08-error-reference.md` to that entry's `sourceDoc`, beside `docs/04-srs.md`. `sourceDoc` is the key `chaptersCiting()` joins on, so naming it makes the new reference page link back to the chapter that built it — and corrects research R11, which concluded the page renders cleanly because no chapter cites it. The empty-citation path still renders cleanly; this document will not be taking it
- [ ] T119b [P] Confirm the fence-delimiter count matches on both locale pages
- [ ] T120 Run `pnpm lint`, `pnpm build`, `pnpm check:docs` and `pnpm check:fences` and record the file, chapter and locale counts (SC-023)

**Checkpoint**: the chain is byte-exact in both locales and no chapter has been made to lie.

---

## Phase 14: Close-out

- [ ] T121 **Add the 3.13 row to `docs/07-tutorial-plan.md`** for the public channel and user surface — the rest of FR-CHN, FR-USR-03/04, and the key management chapter 3.2 deferred — and a paragraph recording why Part 3's milestone no longer sits last. **3.13 carries FR-CHN-03's private half and FR-CHN-05 with it**: private channels and the access control that makes the word mean something are one piece of work, and EIR-API-06's cursor pagination lands there too, since FR-CHN-08's listing needs it anyway. **Fix the section heading in the same edit**: it reads "### Part 3 — Becoming a platform (7 chapters)" against 12 rows today and 13 after this. FR-022 makes this a requirement: chapter 2.8's promise to "Part 3's tenancy work" is the eleven-chapter demonstration of what a deferral without a number costs (FR-022, R20)
- [ ] T122 [P] Update `docs/04-srs.md` if NFR-USE-05's verification note needs to name where the reference lives
- [ ] T123 Write `specs/033-chapter-3-12/chapter-notes.md`: what the plan said against what shipped, T104's exit-criterion verdict from `gaps.md`, the reintroductions and which assertions stayed green, the gap list and its dispositions, the exit-criterion verdict, the numbers, and what was left undone on purpose
- [ ] T123a [P] Restate the plan's "no ADR required" claim against FR-044, which did not exist when it was written. Constitution VII requires an ADR for an architecture decision, and narrowing platform credentials from a class to a named service touches the internal trust model. Chapter 3.11's precedent covers it — it gave each service its own credential without an ADR because that "narrows an existing mechanism rather than adding one" — and the claim should say so rather than leave the older sentence standing (R27)
- [ ] T124 [P] Record the outbox retention gap and its owner in `chapter-notes.md`'s "left undone" section — the four colliding requirements, the 286,871 rows, and the one-line prune that closes it — so FR-MOD-06's chapter inherits a number rather than a memory. Record the reversal beside it: what the first reading claimed, which three of its four arguments failed, and what testing them changed
- [ ] T125 Update `CLAUDE.md`'s managed block for whatever comes next, and tag `part3-ch12`
- [ ] T126 Commit and push all three repositories, parent pins last

---

## Dependencies

**Phase order is dependency and separability, not priority.** Two places it matters:

- **US3 (P1) depends on US5 (P2) and US4 (P2).** An outsider cannot integrate without a
  channel endpoint or reach documentation that does not exist. The priorities are about
  value and the order is about what is reachable; a P1 story sitting last is the honest
  consequence and not a mistake.
- **US2 cannot run before Phases 3 to 6 are complete.** Measuring a suite's sensitivity
  against an incomplete suite measures nothing, and running it before the two endpoints
  exist would leave two routes unprobed.

```
Phase 1 (baseline) ─┬─> Phase 2 (foundational) ─┬─> Phase 3 (US1 REST) ──┐
                    │                            ├─> Phase 4 (US1 schema)│
                    │                            └─> Phase 5 (US1 socket)┤
                    │                                                     ├─> Phase 6 (US5) ──> Phase 7 (US2)
                    └─> Phase 8 (US6) ────────────────────────────────────┘        │
                                                                                    v
                                                       Phase 9 (US4) ──> Phase 10 (US3)
                                                                                    │
                                              Phase 11 ──> 12 ──> 13 ──> 14 <───────┘
```

- **Phase 8 is independent of Phases 3 to 7** and can run any time after Phase 1. It is
  placed after Phase 7 so the coverage measurement in T078 sees the gauntlet's branches.
  **One exception, and it is a constraint rather than a reordering.** Restoring the itest
  lint ban (T069a) would fail a suite that reached the query engine directly, and the
  gauntlet's own two files are the first candidates. An earlier draft scheduled a repair
  task for that and then told the repair to run before the files it repaired existed. The
  constraint moved upstream instead: T025 reads rows through `Repository` and T037 puts the
  catalogue query behind a function in `services/api/src/db/`, so Phase 8 finds nothing
  **of this chapter's** to fix and T069b's permitted list must not name
  `services/api/src/isolation/**`. It does find work: the permitted list still owes entries
  to `services/api/src/db/*.itest.ts`, `services/api/src/quotas/*.itest.ts` and
  `services/gateway/src/limits.itest.ts`, which import the query engine and predate this
  chapter. An earlier draft of this note said "nothing to fix", which was a conclusion
  stated wider than it held — in the same note that deleted a task for the same fault.
- **Phases 9 and 10 are the separable half.** If T114's count is over the bound, they
  become chapter 3.13 and the milestone goes with them.
- T061 must run after T055, and re-runs Phase 3. T078 must run after Phase 3, or it
  measures the wrong "after".

## Parallel opportunities

- **Phase 1**: T001a comes before T002, which is why it is numbered against T001 and not
  T002 — it is the invocation T002 needs, not a note about it. T003 and T008 run alongside
  T001, T001a and T002. T006 before T007; T007a is
  a note and parallel with everything.
- **Phase 2**: T009 (fixture), T010/T010a (the oracle) and T011/T012 (the shapes) are
  three independent files. T013 is a gateway file and parallel with all of them. T014 is
  a check, not an edit.
- **Phase 3**: T030c1 and T030c2 are a registry file and a test, parallel with each other and with T030d to T030f. T017, T018 and T019 are three assertions in one file and go in any order
  once T015 lands. T022 is a scratch edit to a different file and parallel with the
  attacks. T023, T024 and T026 are independent of each other; T025 is not parallel with
  them — all four are `attack.ts`. T028 to T032 are independent once T027 exists. T030a to T030d are product code in two
  files and run in that order, before T031 and T031a; T030e and T030f are tests and
  parallel with each other. T031a is independent of T031 — different credential class,
  different routes.
- **Phase 4**: T038, T041 and T042 alongside T039 and T040. T040a is a comment on T040.
- **Phase 5**: T045 to T048 are four independent attacks once T044 exists. T050 is a
  guard on T049.
- **Phase 6**: T051a is a registry key in `packages/protocol` with no dependency on the
  rest of the phase and can go first or last. T053 is a schema file and parallel with T052
  and T052a, which are one file and go in either order. T054a follows T054; T058a follows
  T057. T058, T059,
  T060 and T062 are independent once T057 lands. T056 is not parallel with T055 — same
  file.
- **Phase 7**: none. Three reintroductions in sequence, each reverted before the next, or
  the second measures the first.
- **Phase 8**: T069a to T069e are one file and run first, in order — T069a before T069b
  because there is nothing to bound until the rule applies. T071, T073, T074 and T077
  alongside T069/T070/T072. T078 and T078a are sequential and both wait on a coverage
  run.
- **Phase 9**: T086 (the document), T087/T088/T089 (the site) and T080/T081/T082 (the
  registry) are three independent groups. T082a is a config file, parallel with all of
  them and required before T093 can read a non-default base. T083, T084 and T085 all follow T082. T090 to
  T094 follow T086 and T089.
- **Phase 10**: T095/T096 (the seed) before T098c and T099. T097, T097a, T098, T098a and T098e are parallel — three files. T098b and T098d are comments and documentation, parallel with everything. T098c must land before T099 can run anywhere, including locally. T100 runs
  alongside T099 rather than after it — a gap list written afterwards is a memory.
- **Phase 11**: T106, T108 and T109 alongside T105 and T107.
- **Phase 13**: T117a, T117b and T117c are three published pages and independent of the
  fence checks; T117c waits on the other two.

## Implementation strategy

**MVP is Phase 3.** Twenty-two endpoints attacked with foreign identifiers from a list
the suite derives, judged against the twin request, is NFR-SEC-09 and the clause
constitution I has been carrying unmet. Stopping there would leave the structural half,
the socket, and the exit criterion undone — a smaller chapter, and not a wrong one.

**Then Phases 4 and 5**, because "every endpoint" and "every record" are two different
claims and a chapter that made only the first would have tested the leak that has an
endpoint and not the one that has a table.

**Then Phase 6**, because without the two endpoints nothing downstream can run and the
exit criterion fails on a Phase 1 gap rather than on documentation.

**Then Phase 7, and it is not optional.** Constitution I says a build that fails this
suite must not ship, which is a promise about sensitivity. A suite that has never been
red is an untested test, and three reintroductions are the cheapest evidence that exists.

**Phase 8 any time**, and placed late so the coverage number includes the gauntlet.

**Phases 9 and 10 last, and separable.** They carry the milestone — the Phase 2 exit
criterion is the external developer, not the suite — so if the page runs long they
become chapter 3.13 rather than being cut. That is the difference between splitting a
chapter and dropping half of one, and it is decided by T114's count.
