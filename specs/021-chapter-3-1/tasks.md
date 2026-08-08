---

description: "Task list for chapter 3.1 — Tenants all the way down"
---

# Tasks: Tutorial Chapter 3.1 — Tenants All the Way Down

**Input**: Design documents from `/specs/021-chapter-3-1/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/tenancy.md, quickstart.md

**Tests**: Test tasks ARE included. The spec requires them explicitly (FR-012) and four success criteria are worded "verified by an automated test" (SC-002…SC-005).

**Organization**: Tasks are grouped by user story. Note the execution order below — the code story (US2) runs before the chapter story (US1), for the reason given in Dependencies.

> **Post-implementation note (2026-08-04).** Tasks below name a draft at
> `relay-tutorial/drafts/part-3/chapter-01-tenants-all-the-way-down/`. That draft
> no longer exists. It was inherited from feature 020, which needed drafts
> because it wrote chapters *ahead of* their code; this chapter was written after
> its code (see "Why the P1 story runs second") and published the same day, so
> the draft was a byte-identical duplicate that no checker validated. It was
> deleted and its `DRAFT-HEADER` metadata moved to `chapter-notes.md` in this
> directory. The task text is left as written — it records what was done — and
> the live files are:
>
> - the chapter: `relay-tutorial/app/(en)/part-3/chapter-01/tenants-all-the-way-down/`
> - its provenance: `specs/021-chapter-3-1/chapter-notes.md`
> - its measurement: `specs/021-chapter-3-1/battery.txt`

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: US1 = the chapter, US2 = the canonical code, US3 = English publication

## Path Conventions

Three roots, all repo-relative: `relay-platform/` (the canonical monorepo),
`relay-tutorial/` (the site), `docs/` (the source documents). Paths below are
written from the repository root.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish and record the baseline before anything changes, so that a later failure can be attributed.

- [X] T001 Record the pre-change baseline: run `pnpm lint && pnpm typecheck && pnpm test` in `relay-platform/` and save the per-package test counts into `specs/021-chapter-3-1/baseline.txt`
- [X] T002 [P] Bring the stores up with the mapped ports (`RELAY_POSTGRES_PORT=15432 RELAY_REDIS_PORT=16379 docker compose up -d --wait postgres redis` in `relay-platform/`) and apply existing migrations with `services/api/dist/db/migrate.js`
- [X] T003 [P] Confirm the site baseline: `pnpm lint`, `pnpm build`, `pnpm check:docs`, `pnpm check:fences` in `relay-tutorial/` — all green before any chapter edits

**Checkpoint**: Baseline recorded; any later regression is attributable to this feature.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The tenancy substrate every story depends on — the schema and its migration. Nothing in US1, US2 or US3 can proceed without it.

**⚠️ CRITICAL**: No user story work begins until this phase is complete.

- [X] T004 Add `organisations`, `humans` and `memberships` tables to `relay-platform/services/api/src/db/schema.ts` per `data-model.md`, including the `UNIQUE (provider, provider_account_id)` and role CHECK constraints
- [X] T005 Amend `applications` in `relay-platform/services/api/src/db/schema.ts` to carry `organisation_id` (NOT NULL, FK) and `created_at`, replacing chapter 2.1's stub and removing its DECISION comment
- [X] T006 Add `UNIQUE (application_id, kind)` to `environments` in `relay-platform/services/api/src/db/schema.ts` — the constraint that caps an application at two environments (FR-TEN-04, research R3)
- [X] T007 Generate `relay-platform/services/api/migrations/0002_tenancy.sql` with drizzle-kit, then review it line by line against `data-model.md` before applying — it must ALTER the existing `applications` table rather than drop it, and it must state how rows that already exist acquire an `organisation_id`: add the column nullable, backfill each orphan application with its own generated organisation, then set NOT NULL (three statements, in that order, in one migration)
- [X] T008 Amend `createEnvironment` in `relay-platform/services/api/src/db/repository.ts` so the admin surface also creates the organisation its application belongs to. **This is not optional and cannot wait for Phase 3**: `createEnvironment` inserts into `applications` with raw SQL, and six api integration suites, `packages/e2e/src/harness.ts` and three walk scripts call it — a NOT NULL `organisation_id` breaks all of them the moment T007 applies
- [X] T009 Apply the migration to the compose Postgres and verify with `psql \d applications` and `\d environments` that the stub shape is gone, both new constraints exist, and pre-existing application rows survived with an organisation (quickstart V3)
- [X] T010 Prove the foundation did not break Part 2: run `pnpm test` and `pnpm test:integration` in `relay-platform/` and confirm every existing suite — including the 2.8 journey — still passes against the migrated schema (spec FR-013)

**Checkpoint**: The schema tells the truth about tenancy, and every Part 2 suite still passes against it. User story work can begin.

---

## Phase 3: User Story 2 — The canonical code advances to `part3-ch1` (Priority: P2)

**Goal**: Provisioning and OAuth signup exist, work, and are held by tests — the answer key the chapter will quote.

**Independent Test**: With the compose stores up, the api's integration lane proves all seven invariants and every Part 1/Part 2 suite still passes; `scripts/signup-walk.mjs` completes a signup and a repeat signup.

### Tests for User Story 2 ⚠️

> Write these first and watch them fail — the invariants are the point of the chapter, and a test that never failed proves nothing (chapter 2.8's rule).

- [X] T011 [US2] Create the local stand-in provider and the integration suite in `relay-platform/services/api/src/tenancy/signup.itest.ts` covering invariants 1–4: the full row set for the call or none (five for a new identity, four for a known one), second-authentication-creates-nothing, third-environment-refused, and two organisations cannot see each other's containers or messages
- [X] T012 [P] [US2] Create `relay-platform/services/api/src/tenancy/oauth.test.ts` covering invariants 5–6: a callback whose `state` does not match the cookie is refused *before* any provider call, and a provider response that breaks the contract yields 502 rather than a crash

- [X] T013 [US2] Assert invariant 7 in `relay-platform/services/api/src/tenancy/signup.itest.ts`: provisioning is reachable only through the signup path — no request-scoped provider exposes it, and no controller outside `tenancy/` can call it (spec FR-011, contracts §Invariants)

### Implementation for User Story 2

- [X] T014 [US2] Implement `provisionOrganisation()` in `relay-platform/services/api/src/db/repository.ts`, growing the existing admin surface: one transaction, the full row set or none, and `created` reporting whether an organisation was created on this call — not whether the identity was new (contracts §Provisioning; research R1, R4, R5)
- [X] T015 [P] [US2] Create `relay-platform/services/api/src/tenancy/oauth.schema.ts` — zod contracts for the provider's token and profile responses, plus the provider-error shape
- [X] T016 [P] [US2] Create `relay-platform/services/api/src/tenancy/state-cookie.ts` — mint a 128-bit state, set it `httpOnly`/`SameSite=Lax`/short-lived, verify it on return, and parse the cookie header without adding a dependency (research R7)
- [X] T017 [US2] Create `relay-platform/services/api/src/tenancy/oauth.provider.ts` — the authorization-code exchange and profile fetch over Node's `fetch`, with endpoints read from configuration so tests can point at the stand-in (research R6, R8; contracts §Configuration)
- [X] T018 [US2] Create `relay-platform/services/api/src/tenancy/signup.controller.ts` — `GET /auth/:provider/start` and `GET /auth/:provider/callback` per `contracts/tenancy.md`, with NO `EnvironmentContextGuard` and the 1.4 error envelope for failures
- [X] T019 [US2] Create `relay-platform/services/api/src/tenancy/tenancy.module.ts` and register it in `relay-platform/services/api/src/app.module.ts`
- [X] T020 [US2] Create `relay-platform/scripts/signup-walk.mjs` — drives a signup against the stand-in, prints the created trio, then repeats the same identity and prints `created: false` with the same organisation id
- [X] T021 [US2] Run `pnpm test` and `pnpm test:integration` in `relay-platform/`; confirm the seven invariants pass, the 2.8 journey suite still passes, and the counts match `specs/021-chapter-3-1/baseline.txt` plus this chapter's additions (spec FR-013)

**Checkpoint**: The code is real and measured. Whatever the chapter says next has to match this.

---

## Phase 4: User Story 1 — The chapter (Priority: P1) 🎯 the deliverable

**Goal**: A published-quality English chapter that derives the hierarchy, shows the signup path, records every decision the documents do not settle, and quotes only output captured in Phase 3.

**Independent Test**: A reader at the Part 2 checkpoint can follow the chapter alone to a working signup, and every claim traces to a document, an earlier chapter, or a recorded decision.

- [X] T022 [US1] Capture the real output the chapter will quote — walk transcript (both runs), migration application, `psql \d` shapes, and the test names as they print — into `specs/021-chapter-3-1/captured-output.md`
- [X] T023 [US1] Scaffold `relay-tutorial/drafts/part-3/chapter-01-tenants-all-the-way-down/page.mdx` with a DRAFT-HEADER carrying tag, fences, amendments, commands and any remaining `«TBV»` markers, plus `figures.ts`
- [X] T024 [P] [US1] Write ADR-18 ("Two user populations: platform humans and tenant end users, never merged") in `docs/05-sad.md` and its deep dive in `docs/06-adr-deep-dives.md`, then re-sync the mirror with `relay-tutorial/scripts/sync-docs.sh` (research R2, R10)
- [X] T025 [US1] Write the chapter body in `relay-tutorial/drafts/part-3/chapter-01-tenants-all-the-way-down/page.mdx`: the derivation of organisation → application → environment from FR-TEN-01/02/03/04, explicit DECISIONs for every table the SAD does not define, the OAuth flow end to end, and the TRAP drawn from a real failure met in Phase 3 (spec FR-002…FR-005)
- [X] T026 [US1] Add to `relay-tutorial/drafts/part-3/chapter-01-tenants-all-the-way-down/page.mdx` the seam statement required by spec FR-006: which dev-mode seams survive this chapter (`x-relay-environment`, dev-secret JWTs), and that 3.2 retires them — plus the forward references for sessions, roles, deletion and the dashboard
- [X] T027 [US1] Write the reader-configuration section into `relay-tutorial/drafts/part-3/chapter-01-tenants-all-the-way-down/page.mdx`: registering a provider application, the six variables in `contracts/tenancy.md` §Configuration, the callback URL, and the rule that these secrets are runtime-only — never a build argument, never in an image layer (spec FR-003)
- [X] T028 [US1] Generate the chapter's fences: plain fences for new files, hunked diff fences for `schema.ts`, `repository.ts` and `app.module.ts`, each verified to apply cleanly to the published predecessor state (docs/07 §2, convention from 2.7)
- [X] T029 [P] [US1] Write 2–4 mermaid figures into `relay-tutorial/drafts/part-3/chapter-01-tenants-all-the-way-down/figures.ts` and validate each parses with mermaid's own parser
- [X] T030 [US1] Measure the battery on `relay-tutorial/drafts/part-3/chapter-01-tenants-all-the-way-down/page.mdx` — 2,000–4,000 canonical words, ≥2 `WHY`, ≥1 `TRAP`, exactly one `SKIP AHEAD` naming `part3-ch1`, ≥1 forward reference, 2–4 figures, one closing `CHECKPOINT` — and adjust the prose until every threshold is met

- [X] T031 [US1] Verify traceability (spec SC-006) on the draft, BEFORE it is published: extract every `FR-*`, `NFR-*`, `DR-*` and `EIR-*` identifier from `relay-tutorial/drafts/part-3/chapter-01-tenants-all-the-way-down/page.mdx` and confirm each exists in `docs/04-srs.md` or `docs/05-sad.md`, and that every table and column named in prose exists in `relay-platform/services/api/src/db/schema.ts` — zero invented identifiers

**Checkpoint**: The chapter exists, quotes only measured output, passes the format gate, and every identifier in it is real — checked before anything is published.

---

## Phase 5: User Story 3 — English publication (Priority: P3)

**Goal**: The chapter is reachable on the site, in English, with the Vietnamese edition honestly marked absent.

**Independent Test**: The site builds; the English path returns 200 and the Vietnamese path 404; the chapter listing shows 3.1 published-untranslated and 3.2–3.7 forthcoming.

- [X] T032 [US3] Publish the draft to `relay-tutorial/app/(en)/part-3/chapter-01/tenants-all-the-way-down/page.mdx` and `figures.ts`, stripping the DRAFT-HEADER
- [X] T033 [US3] Flip the manifest entry in `relay-tutorial/lib/tutorial.ts` to `status: "published"` with `translatedIn: []`, and confirm 3.2–3.7 remain `forthcoming`
- [X] T034 [US3] Run `pnpm lint`, `pnpm build`, `pnpm check:docs` and `pnpm check:fences` in `relay-tutorial/`; the fence chain must replay every published chapter onto the repository with no drift
- [X] T035 [US3] Serve the build (`pnpm start` in `relay-tutorial/`) and verify `/part-3/chapter-01/tenants-all-the-way-down` returns 200, `/vi/part-3/chapter-01/tenants-all-the-way-down` returns 404, and the new figures render (spec FR-015)

**Checkpoint**: Chapter 3.1 is live in English and the site's own checks agree with the repository.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [X] T036 Run the whole of `quickstart.md` V1–V7 as written, from the repository root, and fix anything that does not reproduce
- [ ] T037 **DEFERRED — see the draft header.** The workspace has no coverage tooling, and adding `@vitest/coverage-v8` changes `services/api/package.json`, which three published chapters fence; that is a toolchain decision for its own chapter. Measure branch coverage over the isolation-relevant code the chapter adds (`provisionOrganisation` and the membership queries in `relay-platform/services/api/src/db/repository.ts`) and confirm it meets the constitution's 100% bar for tenant isolation (Principle VI, NFR-MNT-02)
- [X] T038 [P] Resolve the draft's `«TBV»` markers into a `tbv-resolved` header block in `relay-tutorial/drafts/part-3/chapter-01-tenants-all-the-way-down/page.mdx`, recording measured counts and any finding that was not in the plan
- [X] T039 [P] Record the chapter's battery row in `specs/021-chapter-3-1/battery.txt` alongside the Part 2 rows' format
- [X] T040 If Phase 3 or Phase 4 exposed a defect in an earlier chapter, fix it forward in the affected file under `relay-platform/`, amend the affected chapter's `page.mdx` in every locale that has one, say so in `relay-tutorial/drafts/part-3/chapter-01-tenants-all-the-way-down/page.mdx`, and record it in the draft header (spec FR-017)
- [X] T041 Remove temporary scripts and helpers that were not intended to ship, and confirm `git status` in both submodules shows only intended files

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (Phase 1)** → no dependencies.
- **Foundational (Phase 2)** → after Setup. Blocks every story.
- **US2 (Phase 3)** → after Foundational.
- **US1 (Phase 4)** → **after US2**, see below.
- **US3 (Phase 5)** → after US1.
- **Polish (Phase 6)** → after US3.

### Why the P1 story runs second

US1 is the feature's deliverable and keeps its P1 priority, but it cannot be
executed first. Its acceptance requires the chapter to quote captured output
and to fence code that byte-matches the repository, so the code must exist and
run before the prose is written. This is a real dependency, not a preference:
chapters 2.4, 2.6, 2.7 and 2.8 each changed a claim once their code was real —
2.8's own suite passed while the platform was broken, until the script was made
honest. Writing prose first would reintroduce exactly that failure.

### Within each story

- Tests before implementation (T011–T013 before T014–T019).
- Schema before provisioning; provisioning before the controller.
- The admin surface is fixed in the SAME increment as the schema (T007–T008), because the migration breaks every caller of `createEnvironment` the moment it applies.
- Captured output (T022) before chapter prose (T025).
- ADR-18 (T024) before the traceability check (T031): T031 verifies identifiers against `docs/05-sad.md`, so the ADR must be written and mirrored first. T024 may still run alongside the prose tasks — the ordering constraint belongs to T031.
- Chapter complete before publication (Phase 4 before Phase 5).

### Parallel opportunities

- **Phase 1**: T002 and T003 are different repositories — parallel.
- **Phase 3**: T012 is a different file from T011 — parallel. T015 and T016 are independent modules — parallel with each other, both before T017.
- **Phase 4**: T024 (ADR + deep dive, in `docs/`) is parallel with the chapter prose; T029 (figures) is parallel with T025–T028. T031 is the phase's sequential gate — it reads what T024 wrote and must run last.
- **Phase 6**: T038, T039 and T041 touch different files — parallel. T037 (coverage) is verification and may follow publication; traceability deliberately does not — it runs as T031, before the chapter goes out.
- **Phase 2 has no parallelism**: T004–T010 are one atomic change to the schema and its only writer.

Everything else is sequential because it shares a file or consumes the previous
task's output.

---

## Parallel Example: User Story 2

```
# after T011 is underway, these three can proceed together:
T012  oauth.test.ts          (unit: state binding, provider contract)
T015  oauth.schema.ts        (zod provider contracts)
T016  state-cookie.ts        (mint / verify / parse)

# then, in order:
T014  provisionOrganisation()  →  T017  oauth.provider.ts  →  T018  signup.controller.ts  →  T019  module wiring
```

---

## Implementation Strategy

**MVP scope**: US2 + US1 together — the code at `part3-ch1` and the chapter
that documents it. Unlike a product feature, US1 alone is not shippable: a
chapter whose fences match nothing is exactly the drift this series exists to
prevent. US3 (publication) is a thin finishing increment, and is the only part
that can be deferred without leaving something dishonest behind.

**Increment 1 — the tenancy substrate (Phases 1–2).** The schema tells the
truth about organisations, applications and environments; the 2.1 stub is gone;
`createEnvironment` mints an organisation alongside the application it always
created. Stops cleanly — but only because T008 and T010 are inside this
increment: the migration and its only writer must land together, and T010 is
what proves it.

**Increment 2 — signup works (Phase 3).** Provisioning and OAuth exist and are
held by seven invariants. Stops cleanly: a reader could use the code without the
chapter.

**Increment 3 — the chapter (Phase 4).** Written against captured output, with
ADR-18 recorded. Stops cleanly as an unpublished draft, which is exactly how
chapters 2.2–2.8 were staged.

**Increment 4 — publication and polish (Phases 5–6).**

**Standing rule for every phase**: if the work exposes a defect in an earlier
chapter, fix it forward and say so in the chapter (spec FR-017). Four of the
last five chapters did this, and it is the mechanism that keeps the series
honest rather than accumulating quiet contradictions.
