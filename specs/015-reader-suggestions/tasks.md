# Tasks: Reader Suggestions — Select, Right-Click, Improve

**Input**: Design documents from `/specs/015-reader-suggestions/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/suggestions-api.md, quickstart.md

**Tests**: No test runner exists in relay-tutorial (unchanged, R8) — verification
is the quickstart battery: V1 curl contract tests, V2/V3 capture walks, V4
failure honesty, V5 no-regression build, V6 standalone-image replay.

**Organization**: The site's first server-side write. Non-negotiables:
`DATABASE_URL` is runtime-only (never a build arg, never in a bundle or image
layer); right-click without a selection stays native; reading never degrades on
DB failure; nothing personal is stored; vi strings at the naturalized register;
**commits, Neon provisioning, and deploys are Dong's**.

**⚠ Standing instructions**: Do NOT run `git commit` / `git push` (Dong does).
Do NOT create or modify anything in Dong's Neon account — implementation
verifies against the `DATABASE_URL` Dong provides in `relay-tutorial/.env` (or
a local Postgres fallback), production migration is Dong's V7 step.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = capture path, US2 = durable useful storage, US3 = bounded write path

## Path Conventions

- All changes in `/home/dong/work/relay/relay-tutorial/` (site submodule only — C6)
- Contract: contracts/suggestions-api.md C1–C6; numbers from research R5; fields from data-model
- Per AGENTS.md: consult `node_modules/next/dist/docs/` before route-handler code

---

## Phase 1: Setup

**Purpose**: The new dependency and the database connection to verify against

- [X] T001 Add Prisma to relay-tutorial: `pnpm add -D prisma && pnpm add @prisma/client` (current stable, pinned by the lockfile); add `"postinstall": "prisma generate"` to package.json scripts (R1); create relay-tutorial/.env.example documenting `DATABASE_URL="postgresql://user:password@host/db?sslmode=require"` with a note that dev uses .env (gitignored) and prod uses compose env; establish the verification database — if Dong has provided a Neon `DATABASE_URL` in relay-tutorial/.env use it, otherwise start a disposable local Postgres (e.g. `docker run -d --name suggestions-dev -e POSTGRES_PASSWORD=dev -p 15433:5432 postgres:18-alpine`) and write its URL to .env, flagging in the handoff that Neon replaces it (quickstart prerequisites)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema, client, and the validation core every story consumes

- [X] T002 Create relay-tutorial/prisma/schema.prisma per data-model: `Suggestion` model (id cuid pk, pagePath, locale enum en/vi, selectedText, contextBefore, contextAfter, suggestion, status enum NEW/HANDLED default NEW, createdAt default now) with `@@index([pagePath, status])` and `@@index([createdAt])`; NO personal fields (FR-009); run `pnpm prisma migrate dev --name suggestions` against the T001 database; create relay-tutorial/lib/prisma.ts as the globalThis-cached client singleton (R1); `pnpm build` still green
- [X] T003 Create relay-tutorial/lib/suggestions.ts (R3, R5): export the caps (SELECTION_MAX 1000, CONTEXT_MAX 250, SUGGESTION_MAX 2000, BODY_MAX 8192, RATE_PER_MIN 5, RATE_PER_DAY 30); build the page-path allowlist at module load from lib/tutorial.ts (published chapters → path, + `/vi${path}` when translatedIn includes vi) and lib/docs.ts (`/docs/<slug>` + `/vi/docs/<slug>`); export pure `validateSuggestion(raw: unknown)` returning `{ ok: true, data }` or `{ ok: false, code }` with the data-model error codes — exact field set (unknown fields → invalid_body), types, trims, caps, locale/pagePath prefix agreement, honeypot `website` must be empty (signalled distinctly so the route can fake success)

---

## Phase 3: User Story 1 - A reader flags a rough sentence in place (Priority: P1) 🎯 MVP

**Goal**: Select → right-click → localized dialog → submitted and persisted, both locales, desktop and touch; right-click stays native everywhere else.

**Independent Test**: On a chapter and a docs page in each locale, submit a suggestion end to end and find the row in the database; verify native right-click without selection (quickstart V2, V3 happy paths).

### Implementation for User Story 1

- [X] T004 [US1] Create relay-tutorial/app/api/suggestions/route.ts (C1): FIRST consult node_modules/next/dist/docs/ on route handlers + request IP/headers in this Next version (AGENTS.md); export POST — enforce BODY_MAX before JSON parse, `validateSuggestion`, honeypot → return 201-shaped `{ok:true}` storing nothing, in-memory sliding-window rate limit per IP counting EVERY POST — accepted, rejected, and honeypot alike (R5; first `x-forwarded-for` hop, fallback connection; 5/min + 30/day; 429 `rate_limited`), then `prisma.suggestion.create` → 201 `{ok:true}` only after commit; Prisma failure → 503 `storage_unavailable`; no suggestion bodies/IPs/secrets in logs; non-POST → 405; verify with a happy-path curl in each locale
- [X] T005 [P] [US1] Add the `suggest` namespace to relay-tutorial/lib/i18n.ts, en + vi (R7, C3): menu action ("Suggest an improvement" / "Góp ý cải thiện"), dialog title, selected-text label, textarea placeholder, character counter, submit/cancel, submitting, thank-you, and error messages for invalid/too-long/rate_limited/storage_unavailable — vi at the naturalized register (no calques; "package"-rule glossary applies), self-reviewed before presenting
- [X] T006 [US1] Create relay-tutorial/components/reading/suggestion-capture.tsx (R4, C2): client component taking `locale`; contextmenu listener scoped to `#reading-article` — preventDefault ONLY when the selection is non-collapsed and its range is inside the article, then render the one-item custom menu at the cursor (Esc/click-away dismiss, no trapping); debounced selectionchange → floating suggest button near `range.getBoundingClientRect()` for touch (FR-002); on coarse-pointer devices (`matchMedia("(pointer: coarse)")`) the contextmenu handler stands down completely — Android long-press fires contextmenu, and the native selection toolbar must survive (A1 remediation: floating button is the ONLY touch affordance); accessible dialog (role="dialog", focus trap, Esc) with read-only selected passage, textarea + live counter (client-side caps mirror lib/suggestions.ts), submit via fetch POST /api/suggestions with pagePath (usePathname), locale, selection, contextBefore/After (enclosing block textContent, CONTEXT_MAX each side), honeypot field; states submitting/success(auto-dismiss)/error(localized, retry); fresh state per new selection; renders null with no selection; mount it once in relay-tutorial/components/reading/reading-layout.tsx inside the article wrapper passing `locale`
- [X] T007 [US1] Run quickstart V2 + V3 happy paths on the dev server: desktop capture walk on a chapter + docs page × en/vi (menu appears only with in-article selection; native menu otherwise incl. sidebar/header; Esc/click-away; fresh dialog after submit; all strings localized), touch emulation walk (floating button → dialog → 201); confirm rows in the database for each submission; fix findings

**Checkpoint**: The capture path works end to end in both locales — MVP delivered

---

## Phase 4: User Story 2 - Suggestions survive and stay useful to the author (Priority: P2)

**Goal**: Every acknowledged submission is a complete, locatable, reviewable record.

**Independent Test**: Rows from V2/V3 contain all data-model fields with sane context; a lightly-edited passage remains locatable; status flips work via SQL (quickstart V1 happy-path inspection + SC-005 demo).

### Implementation for User Story 2

- [X] T008 [US2] Verify storage completeness against the data-model contract (C4): inspect the T007 rows via `pnpm prisma studio` or psql — all fields present and verbatim (selection with code content stays unnormalized), status NEW, timestamps sane, both indexes exist in the migration SQL; demonstrate SC-005 by lightly editing a local copy of one passage and locating it via stored contextBefore/After; flip one row NEW→HANDLED via SQL to prove the author workflow; document the two review queries (open-by-page, recent) in the task record for Dong; fix any field/index gaps found

**Checkpoint**: Records are complete and actionable from the Neon console

---

## Phase 5: User Story 3 - The door is open but the house doesn't burn (Priority: P3)

**Goal**: The write path rejects garbage, floods, and bots; failure never degrades reading.

**Independent Test**: The full V1 curl battery is exact; V4 failure honesty passes (quickstart V1, V4).

### Implementation for User Story 3

- [X] T009 [US3] Script and run the full endpoint battery per quickstart V1 against the dev server (write the script to the scratchpad, not the repo): RESTART the dev server first — the in-memory limiter counts every POST (R5), so the battery needs fresh windows and must run as one deliberate sequence with the rate-limit case LAST (its own restart, then 6 rapid POSTs → sixth is 429), spacing earlier cases to stay under 5/min; cases: happy en+vi (201 + rows), honeypot (201, no row), each cap violation → 400 with the exact code, allowlist cases (unknown path, forthcoming-chapter path, locale/path mismatch → invalid_page), shape cases (unknown field, non-JSON, 9 KB → invalid_body), GET → 405; assert final row count equals happy-path count; fix findings in lib/suggestions.ts or the route
- [X] T010 [US3] Run quickstart V4 failure honesty: stop the T001 database container (or point DATABASE_URL at a dead host and restart dev) — reading pages render and navigate normally, POST → 503 storage_unavailable, dialog shows the localized failure with retry, no unhandled rejections in the console; restore the database; fix findings

**Checkpoint**: All three stories independently verified

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Deployment truth, no-regression proof, handoff

- [X] T011 Update the deployment for the first dynamic route (C5, R6): relay-tutorial/Dockerfile — ensure the build stage generates the Prisma client (postinstall covers it; verify) and the standalone runtime stage carries the engine; relay-tutorial/docker-compose.yml — add `DATABASE_URL: ${DATABASE_URL}` passthrough under environment (no default containing credentials); then run quickstart V6: `docker build`, `docker run -e DATABASE_URL=...`, chapter page renders AND a curl POST returns 201 with a row landing — if the engine is missing apply R6's `outputFileTracingIncludes` fallback (consult the bundled Next docs first) and re-run
- [X] T012 Run quickstart V5 no-regression + handoff (NO commits — standing instruction): `pnpm lint && pnpm build` green; 34 static pages unchanged with only /api/suggestions dynamic; sitemap still exactly 28 URLs; `grep -r` proves DATABASE_URL absent from .next/static and client bundles; landings have no capture affordance; then report per-repo ready-to-commit files (relay-tutorial: prisma/, lib/prisma.ts, lib/suggestions.ts, route, component, reading-layout, i18n, package.json/lockfile, Dockerfile, compose, .env.example; parent: specs/015 + CLAUDE.md/feature.json) with a suggested commit message, and Dong's V7 runbook: provision Neon, `pnpm prisma migrate deploy` against it, set DATABASE_URL on the server, `docker compose up -d --build`, live happy-path check both locales, vi read-through of the new strings

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 first (dependency + database)
- **Foundational (Phase 2)**: T002 after T001; T003 independent of T002 (different files) but both block Phase 3
- **US1 (Phase 3)**: T004 after T002+T003; T005 [P] anytime after Setup; T006 after T004+T005; T007 after T006
- **US2 (Phase 4)**: T008 after T007 (inspects its rows)
- **US3 (Phase 5)**: T009 after T004 (batters the real endpoint); T010 after T009
- **Polish (Phase 6)**: T011 after all US phases; T012 last

### User Story Dependencies

- **US1 (P1)**: Setup + Foundational — the MVP
- **US2 (P2)**: needs US1's submissions to inspect
- **US3 (P3)**: needs US1's endpoint; independent of US2

### Parallel Opportunities

- T002 ∥ T003 (schema/client vs validation module — different files)
- T005 (i18n strings) ∥ T004 (route handler) — different files
- T008 (US2) ∥ T009 (US3) both follow T007 if run carefully (T009's rate-limit
  burst pollutes counts — run T008's inspection first or use distinct pages)

## Parallel Example

```bash
# Serial spine: T001 → (T002 ∥ T003) → T004 (∥ T005) → T006 → T007
# Then: T008 (inspect) → T009 (batter) → T010 → T011 → T012
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. T001–T007 — capture path live in both locales against a real database
2. **STOP and VALIDATE**: a suggestion submitted from each locale, rows inspected

### Incremental Delivery

1. US1 → readers can suggest; rows land
2. US2 → rows proven complete, locatable, reviewable
3. US3 → the endpoint proven hostile-input-safe; failure honesty
4. Polish → deployment truth (standalone + runtime env), no-regression, handoff

---

## Notes

- The route handler is the ONLY writer; validation lives in lib/suggestions.ts
  so the battery's findings have one place to fix (constitution IV's spirit)
- preventDefault discipline is the feature's reputation: when in doubt, let
  the native menu through (FR-001 outranks affordance discoverability)
- vi strings get the same register care as chapter prose — glossary applies,
  self-review before presenting
- The T009 battery script lives in the scratchpad, not the repo (the site
  gains no test infrastructure this feature, R8)
- NO git commit / git push; NO Neon account operations — Dong provisions,
  migrates production, deploys
