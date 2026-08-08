---

description: "Task list for chapter 3.2 — Keys and tokens, two credentials and one mistake"
---

# Tasks: Tutorial Chapter 3.2 — Keys and Tokens, Two Credentials and One Mistake

**Input**: Design documents from `/specs/022-chapter-3-2/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/credentials.md, quickstart.md

**Tests**: Test tasks ARE included. The spec requires them (FR-019) and eight success criteria are worded "verified by an automated test".

**Organization**: Grouped by user story. As in 3.1, the code story (US2) executes before the chapter story (US1) — see Dependencies for why that is a real constraint rather than a preference.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on incomplete work)
- **[Story]**: US1 = the chapter, US2 = the canonical code, US3 = English publication

## Path Conventions

Paths are written from the repository root across three trees: `relay-platform/`
(the monorepo), `relay-tutorial/` (the site), `docs/` (the source documents).

---

## Phase 1: Setup

**Purpose**: Record the starting state so any later failure is attributable.

- [X] T001 Record the pre-change baseline: run `pnpm lint && pnpm typecheck && pnpm test` then `pnpm test:integration` in `relay-platform/`, and save the per-package counts to `specs/022-chapter-3-2/baseline.txt` (expected: 86 unit, 60 integration)
- [X] T002 [P] Bring the stores up (`RELAY_POSTGRES_PORT=15432 RELAY_REDIS_PORT=16379 docker compose up -d --wait postgres redis`), then `pnpm build` and apply existing migrations with `services/api/dist/db/migrate.js`
- [X] T003 [P] Confirm the site baseline in `relay-tutorial/`: `pnpm lint`, `pnpm build`, `pnpm check:docs`, `pnpm check:fences` — all green before any edit

**Checkpoint**: baseline recorded.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Settle the one unknown that decides the design, then put the schema, the dependency and the error code in place.

**⚠️ CRITICAL**: T004 comes first because its answer changes where authentication lives. Chapter 2.6 lost time to guessing Nest's resolution order; this time the experiment runs before the code.

- [X] T004 Determine empirically whether Nest middleware runs before request-scoped providers are constructed: add a temporary diagnostic that logs from `RequestContextMiddleware` and from the request-scoped factory in `relay-platform/services/api/src/messages/messages.module.ts`, hit any authenticated route, record the observed order in `specs/022-chapter-3-2/research.md` under R5, then remove the diagnostic. If middleware runs too late, take R5's named fallback (an async factory plus a guard that converts failures into the EIR-API-04 envelope) and record that instead
- [X] T005 Add `jose` (`^6.2.7`, the version the workspace already resolves) to `relay-platform/services/api/package.json` and install; confirm `pnpm typecheck` still passes across all packages
- [X] T006 Add the `api_keys` table to `relay-platform/services/api/src/db/schema.ts` per `data-model.md`, including `UNIQUE (public_id)`, the prefix CHECK, and a DECISION comment recording that no source document defines this table
- [X] T007 Generate `relay-platform/services/api/migrations/0003_api_keys.sql` with drizzle-kit and review it line by line before applying — the table is new so no backfill is expected, but read the generated SQL rather than trusting it (3.1's migration needed a hand-written rewrite)
- [X] T008 Apply the migration and verify with `psql \d api_keys` that the unique index and the prefix CHECK exist
- [X] T009 Add the `wrong_credential_type` code to `relay-platform/packages/protocol/src/codes.ts` with a message naming presented-versus-expected, and confirm the registry's existing uniqueness test still passes
- [X] T010 Prove the foundation changed nothing yet: run both lanes in `relay-platform/` and confirm the counts match `specs/022-chapter-3-2/baseline.txt`

**Checkpoint**: the schema, the dependency and the error code are in place, the DI question is answered, and nothing has regressed.

---

## Phase 3: User Story 2 — The canonical code advances to `part3-ch2` (Priority: P2)

**Goal**: Both credentials work, both dev-mode seams are gone, and twelve invariants hold.

**Independent Test**: At `part3-ch2` the Docker-free gate passes; with the stores up every integration lane passes including the 2.8 journey; `credential-walk.mjs` shows a key sending a message, a token opening a socket, and each credential refused where the other belongs; and grepping production code for the retired header or the dev secret returns nothing.

### Tests for User Story 2 ⚠️

> Write these before the implementation and watch them fail. Every refusal below is a requirement, and a refusal test that never failed proves nothing (2.8's rule).

- [X] T011 [P] [US2] Create `relay-platform/services/api/src/auth/api-key.test.ts` — parsing the credential format, prefix matching the environment kind (invariant 12), salted hashing, constant-time comparison, and the rule that no error string contains the secret
- [X] T012 [P] [US2] Create `relay-platform/services/api/src/auth/user-token.test.ts` — required claims, the 24-hour lifetime bound (invariant 7), and refusal of `alg: none` and asymmetric-`alg` tokens (invariant 8, the algorithm-confusion case)
- [X] T013 [US2] Create `relay-platform/services/api/src/auth/credentials.itest.ts` covering invariants 1–7, 9 and 11 over HTTP: secret shown once and unrecoverable, 401 with no credential, 403 `wrong_credential_type` with the message asserted, a foreign key seeing nothing, a revoked key refused on the next request, two active keys working at once, token refusals, the dev-token endpoint in development and its 404 in production, and no credential in any log line. Include FR-012's rule against a real target: a user-class principal presented to an application-only route (the dev-token endpoint) MUST be refused with `wrong_credential_type`, since FR-AUT-10's named administrative operations have no public routes yet (research R6)

### Implementation for User Story 2

- [X] T014 [P] [US2] Create `relay-platform/services/api/src/auth/principal.ts` — the two credential classes and the resolved principal shape from `data-model.md`
- [X] T015 [P] [US2] Create `relay-platform/services/api/src/auth/api-key.ts` — mint (`rk_dev_`/`rk_live_` + public id + secret), split, salted SHA-256 via `node:crypto`, and `timingSafeEqual` comparison (research R2, R3)
- [X] T016 [US2] Create `relay-platform/services/api/src/auth/user-token.ts` — verify and mint HS256 with `jose`, passing an explicit algorithm allow-list, checking `sub`/`env`/`iat`/`exp` and the 24-hour bound (research R4)
- [X] T017 [US2] Extend the repository in `relay-platform/services/api/src/db/repository.ts`: mint, verify and revoke keys, and make `provisionOrganisation` mint the environment's first key inside the same transaction, returning its secret once (research R8, FR-AUT-02)
- [X] T018 [US2] Create `relay-platform/services/api/src/auth/authenticate.middleware.ts` (or the T004 fallback) resolving a bearer credential to a principal, plus `relay-platform/services/api/src/auth/credential.guard.ts` declaring what a route accepts
- [X] T019 [US2] Create `relay-platform/services/api/src/auth/auth.module.ts` and wire it in `relay-platform/services/api/src/app.module.ts`
- [X] T020 [US2] **Retire the header seam in ONE increment**, across the eight files that carry it — measured, not guessed: delete `relay-platform/services/api/src/messages/environment-context.guard.ts`; take the environment from the principal in `relay-platform/services/api/src/messages/messages.module.ts`; stop sending the header from `relay-platform/services/gateway/src/api-client.ts`; and update the five suites that present it — `relay-platform/services/api/src/messages/messages.itest.ts`, `relay-platform/services/api/src/internal/internal.itest.ts`, `relay-platform/services/api/src/internal/backfill.itest.ts`, `relay-platform/services/api/src/tenancy/signup.itest.ts` and `relay-platform/packages/e2e/src/tuan.itest.ts` — via a key-minting test helper. (The walk scripts under `relay-platform/scripts/` do NOT carry this seam; they carry the token seam, retired in T025.)
- [X] T021 [US2] Prove nothing broke: run `pnpm test` and `pnpm test:integration` in `relay-platform/` and confirm every pre-existing suite passes with credentials, matching the counts in `specs/022-chapter-3-2/baseline.txt` plus this chapter's additions, with assertions unchanged in substance (spec FR-020)
- [X] T022 [US2] Create `relay-platform/services/api/src/internal/session.controller.ts` — `POST /internal/session` verifying a token and returning environment, user and memberships in one answer, replacing `GET /internal/memberships` (research R1, contracts §internal) — and move that route's two contract cases in `relay-platform/services/api/src/internal/internal.itest.ts` (lines ~108–120) onto the new route, so replacing the endpoint does not orphan the tests that hold its contract
- [X] T023 [US2] Retire the gateway's local verification: `relay-platform/services/gateway/src/auth.ts` stops verifying and stops holding `DEV_JWT_SECRET`, `relay-platform/services/gateway/src/api-client.ts` calls the session route, and `relay-platform/services/gateway/src/session.ts` takes identity and memberships from the answer
- [X] T024 [US2] Rewrite `relay-platform/services/gateway/src/session.test.ts` against an api stub that returns a session: the file mints dev-secret tokens in 20 places across 19 tests, and once verification moves to the api none of them can verify locally. This is a task, not a clause — 2.5, 2.6 and 2.7 all added cases to this file and every one must keep asserting what it asserted
- [X] T025 [US2] **Retire the token seam in the remaining callers**, the second measured blast radius (seven files, different from T020's eight): `relay-platform/services/gateway/src/auth.ts` (done in T023), `relay-platform/services/gateway/src/resume.itest.ts`, `relay-platform/packages/e2e/src/harness.ts`, and the three walk scripts `relay-platform/scripts/ws-walk.mjs`, `relay-platform/scripts/split-brain.mjs`, `relay-platform/scripts/tunnel-walk.mjs` — each of which mints a dev-secret token today. Then run `pnpm test` and `pnpm test:integration` in `relay-platform/` and confirm every suite passes, matching `specs/022-chapter-3-2/baseline.txt` plus this chapter's additions
- [X] T026 [US2] Create `relay-platform/services/api/src/auth/dev-token.controller.ts` — FR-AUT-09's endpoint, application credential only, minting a token in a `development` environment and answering 404 in `production` (contracts explains why 404 and not 403)
- [X] T027 [US2] Add the socket cases to `relay-platform/services/gateway/src/session.itest.ts` (new file): a real token opens a connection, a key presented as a token closes 4001, and an established connection survives its token's expiry (invariant 10, FR-AUT-11)
- [X] T028 [US2] Create `relay-platform/scripts/credential-walk.mjs` — a key sends a message, mints a token, the token opens a socket and receives it, then each credential is refused where the other belongs, printing both refusals
- [X] T029 [US2] Run the mechanical seam check from `quickstart.md` V3: grep `relay-platform/services` and `relay-platform/packages` for `x-relay-environment` and `DEV_JWT_SECRET` outside test files — expect zero matches (spec SC-008)

**Checkpoint**: both credentials are real, both seams are gone, and the platform refuses ten things it used to accept.

---

## Phase 4: User Story 1 — The chapter (Priority: P1) 🎯 the deliverable

**Goal**: A chapter that teaches the two credentials, shows the mistake being named, and quotes only measured output.

**Independent Test**: A reader at the `part3-ch1` checkpoint reaches a first authenticated message and socket using only the chapter, and every claim traces to a document, an earlier chapter, or a recorded decision.

- [X] T030 [US1] Capture what the chapter will quote into `specs/022-chapter-3-2/captured-output.md` — both walk transcripts, the invariant test names as they print, the lane counts, and the wrong-credential error body — **redacting every live secret and token** before saving (spec SC-007)
- [X] T031 [P] [US1] Write 2–4 mermaid figures into `relay-tutorial/app/(en)/part-3/chapter-02/keys-and-tokens/figures.ts` and validate each parses with mermaid's own parser
- [X] T032 [US1] Write the chapter body in `relay-tutorial/app/(en)/part-3/chapter-02/keys-and-tokens/page.mdx`: what each credential authenticates before any mechanics, the visible prefix, the once-shown secret, a WHY box on hashing a 256-bit secret without a password KDF (research R3), a TRAP from a real failure met in Phase 3, and the three DECISIONs spec FR-006 requires — the key table's shape (no document defines it), the hashing choice, and where the first key comes from
- [X] T033 [US1] Add the wrong-credential section to `relay-tutorial/app/(en)/part-3/chapter-02/keys-and-tokens/page.mdx`: the error that names presented-versus-expected, why it names the class and never the credential (NFR-SEC-06), and the honest note that the socket's token rides in a query string because a browser cannot set headers on an upgrade
- [X] T034 [US1] Add the seam-retirement section and the deferrals to `relay-tutorial/app/(en)/part-3/chapter-02/keys-and-tokens/page.mdx`: both seams gone, FR-AUT-11's second clause deferred for want of a protocol frame, FR-AUT-12 belonging to 3.6, key management waiting for the dashboard's session, and the internal hop's trust model unchanged since 2.5
- [X] T035 [US1] Fix chapter 3.1 forward in `relay-tutorial/app/(en)/part-3/chapter-01/tenants-all-the-way-down/page.mdx`: correct "no session — that is 3.2's" to name the dashboard's chapter, and update the signup response's field list to include the first key (spec FR-024; 3.1 has no Vietnamese edition to mirror)
- [X] T036 [US1] Generate the chapter's fences: whole-file fences for the new `auth/` files, the migration, the session controller and the walk script; hunked diff fences for `services/api/package.json`, `packages/protocol/src/codes.ts`, `schema.ts`, `repository.ts`, `messages.module.ts` and the three gateway files — each verified to apply cleanly to its published predecessor
- [X] T037 [US1] Measure the battery on `relay-tutorial/app/(en)/part-3/chapter-02/keys-and-tokens/page.mdx` — 2,000–4,000 canonical words, ≥2 `WHY`, ≥1 `TRAP`, exactly one `SKIP AHEAD` naming `part3-ch2`, ≥1 forward reference, 2–4 figures, one closing `CHECKPOINT` — and adjust the prose until every threshold is met
- [X] T038 [US1] Verify traceability BEFORE publication (spec SC-009): every `FR-*`/`NFR-*`/`DR-*`/`EIR-*` in `relay-tutorial/app/(en)/part-3/chapter-02/keys-and-tokens/page.mdx` exists in `docs/04-srs.md` or `docs/05-sad.md`, and every table and column named in prose exists in `relay-platform/services/api/src/db/schema.ts`

**Checkpoint**: the chapter is written against measured output, its identifiers are real, and 3.1 no longer promises something this chapter does not deliver.

---

## Phase 5: User Story 3 — English publication (Priority: P3)

**Goal**: 3.2 is reachable in English, with the Vietnamese edition honestly absent.

**Independent Test**: The site builds; the English path returns 200 and the Vietnamese 404; the listing shows 3.2 untranslated and 3.3–3.7 forthcoming.

- [X] T039 [US3] Flip the 3.2 entry in `relay-tutorial/lib/tutorial.ts` to `status: "published"` with `translatedIn: []`, and confirm 3.3–3.7 remain `forthcoming`
- [X] T040 [US3] Run `pnpm lint`, `pnpm build`, `pnpm check:docs` and `pnpm check:fences` in `relay-tutorial/`; the fence chain must replay every published chapter with no drift, including the two edits to 3.1
- [X] T041 [US3] Serve the build (`pnpm start` in `relay-tutorial/`) and verify `/part-3/chapter-02/keys-and-tokens` returns 200, `/vi/part-3/chapter-02/keys-and-tokens` returns 404, and every figure renders with no page errors

**Checkpoint**: chapter 3.2 is live in English and the site's checks agree with the repository.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T042 Run the whole of `quickstart.md` V1–V8 as written from the repository root and fix anything that does not reproduce
- [X] T043 Scan for leaked credentials one last time (spec SC-007, quickstart V7): search `specs/022-chapter-3-2/captured-output.md` and the published `page.mdx` for `rk_dev_`/`rk_live_` secrets and JWT bodies; only deliberately truncated shape examples may remain
- [X] T044 [P] Write `specs/022-chapter-3-2/chapter-notes.md` — tag, fences, amendments, documents touched, commands, verification results, findings the plan did not anticipate, and anything deferred with its reason (the shape 3.1's notes established)
- [X] T045 [P] Record the chapter's battery row in `specs/022-chapter-3-2/battery.txt`, measured on the published page
- [X] T046 If Phase 2 or Phase 3 exposed a defect in an earlier chapter beyond the two known 3.1 edits, fix it forward in `relay-platform/`, amend the affected chapter's `page.mdx` in every locale that has one, and record it in `chapter-notes.md` (spec FR-024)
- [X] T047 Remove temporary diagnostics and helpers not intended to ship (including T004's), and confirm `git status` in both submodules shows only intended files

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (Phase 1)** → no dependencies.
- **Foundational (Phase 2)** → after Setup. Blocks every story. T004 blocks T018.
- **US2 (Phase 3)** → after Foundational.
- **US1 (Phase 4)** → after US2.
- **US3 (Phase 5)** → after US1.
- **Polish (Phase 6)** → after US3.

### Why the P1 story runs second

US1 is the deliverable and keeps its priority, but its acceptance requires
quoting captured output and fencing code that byte-matches the repository, so
the code must exist and run first. Four of the last five chapters changed a claim
once their code was real; 2.8's suite passed while the platform was broken until
its script was made honest. This ordering is a constraint, not a preference.

### Within each story

- T004 before T018: the DI ordering decides where authentication lives.
- Tests (T011–T013) before implementation (T014–T019).
- T017 before T020: the key-minting path must exist before the header can be retired.
- **T020 and T021 are one increment**, and **T023–T025 are another.** There are TWO seams with different blast radii, measured rather than assumed: the header is in eight files, the dev-secret token in seven, and only `gateway/src/auth.ts` sits in both. Each seam dies with its callers in the same increment and is followed immediately by a lane run — the shape 3.1's `createEnvironment` taught, applied twice.
- T022 before T023: the session route must exist before the gateway calls it, and T022 also rehouses the two contract cases the replaced route leaves behind.
- T024 before T025: `session.test.ts` is the largest single consumer of the dev secret (20 mints across 19 tests), so it moves first and the smaller callers follow.
- T030 (captured output) before T032–T034 (prose).
- T038 is Phase 4's gate: traceability is checked before anything is published.

### Parallel opportunities

- **Phase 1**: T002 and T003 are different repositories — parallel.
- **Phase 2**: none. T004–T010 are one ordered change to the platform's foundations.
- **Phase 3**: T011 and T012 are different files — parallel with each other and with T013's authoring. T014 and T015 are independent modules, both before T018. Nothing in T020–T025 is parallel: both seam retirements are atomic by design.
- **Phase 4**: T031 (figures) is parallel with the prose tasks; T035 (3.1's edits) touches a different page and is parallel with T032–T034.
- **Phase 6**: T044 and T045 touch different files — parallel.

Everything else shares a file or consumes the previous task's output.

---

## Parallel Example: User Story 2

```
# tests first, and these two are independent files:
T011  api-key.test.ts     (format, prefix, hashing, timing)
T012  user-token.test.ts  (claims, 24h bound, alg allow-list)

# then the two leaf modules, in parallel:
T014  principal.ts        T015  api-key.ts

# then, strictly in order — note the two atomic seam retirements:
T016  user-token.ts → T017  repository (mint/verify/revoke + signup bootstrap)
    → T018  middleware + guard → T019  module wiring
    → T020  RETIRE THE HEADER SEAM (8 files) → T021  prove green
    → T022  internal session route (+ rehome its contract tests)
    → T023  gateway stops verifying
    → T024  rewrite session.test.ts (19 tests)
    → T025  RETIRE THE TOKEN SEAM in the rest (7 files) + prove green
```

---

## Implementation Strategy

**MVP scope**: US2 + US1 — the code at `part3-ch2` and the chapter documenting
it. As in 3.1, US1 alone is not shippable: a chapter whose fences match nothing
is the drift this series exists to prevent. US3 is a thin finishing increment.

**Increment 1 — foundations (Phases 1–2).** The DI question is answered, the key
table and error code exist, `jose` is in. Stops cleanly: nothing authenticates
differently yet and every suite still passes (T010).

**Increment 2 — credentials (Phase 3).** Both classes work, both seams are gone,
twelve invariants hold. Stops cleanly: a reader could use the code without the
chapter. There are two risky moments, not one — T020 (the header, 8 files) and
T025 (the token, 7 files) — each paired with an immediate lane run. Between them
sits T024, the rewrite of 19 gateway unit tests that can no longer verify a token
locally; it is the single largest piece of adaptation in this chapter and is
sized as its own task rather than buried in a clause.

**Increment 3 — the chapter (Phase 4).** Written against captured output, with
3.1's two stale statements corrected. Stops cleanly as an unpublished page.

**Increment 4 — publication and polish (Phases 5–6).**

**Standing rule**: if the work exposes a defect in an earlier chapter, fix it
forward and say so (spec FR-024). Every chapter since 2.4 has done this.

**Not scheduled here — deferred by decision, with the follow-up feature now
committed (2026-08-08)**: the constitution's 100% branch-coverage bar for
ordering, idempotency and tenant isolation (Principle VI, NFR-MNT-02) is
unmeasurable in this workspace — there is no coverage tooling, and adding
`@vitest/coverage-v8` changes `services/api/package.json`, which three published
chapters fence (1.4, 2.1, 2.2). The same principle's CI clause ("the quickstart
MUST run unmodified, verified by automated execution in CI") is unmet for the
same kind of reason: no CI exists.

Chapter 3.1 deferred the coverage task (021's T037). This is the **second**
recorded deferral and the last one: a small feature covering coverage tooling, a
CI workflow, and hunked-diff amendments to the three fenced chapters runs
**immediately after 3.2, before 3.3**. It lands on the most isolation-critical
code the platform has yet had — the path that resolves a tenant from a
credential — which is why it is the next thing measured rather than a standing
recommendation.

Chapter 3.2 proceeds on the explicit understanding that its isolation code is
tested by name (the twelve invariants) but its branch coverage is unmeasured, and
that this is recorded with a scheduled remedy, not overlooked.
