# Implementation Plan: Reader Suggestions — Select, Right-Click, Improve

**Branch**: `main` (no feature branch — consistent with features 001–014) | **Date**: 2026-07-31 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/015-reader-suggestions/spec.md`

## Summary

Give both editions a friction-free feedback path: selecting text inside the
article column and right-clicking offers "Suggest an improvement" (touch
devices get a floating button on selection); a localized dialog shows the
selection read-only, takes a suggestion, and POSTs it to the site's first
server-side write — `app/api/suggestions/route.ts` — which validates against
hard caps and a page-path allowlist derived from the manifest/docs registry,
rate-limits per IP in memory, and persists via Prisma to a NeonDB Postgres
(runtime `DATABASE_URL`, never build-time). One new table, no auth, no admin
UI (Neon's SQL editor is the v1 review tool). The capture component mounts
once in `ReadingLayout`, so every chapter and reference doc in both locales is
covered with zero per-page edits. Decisions in [research.md](./research.md).

## Technical Context

**Language/Version**: relay-tutorial's existing stack — Next.js 16.2 App
Router, React 19, TypeScript 5.9, pnpm 10; Node 22 runtime container

**Primary Dependencies**: NEW: `prisma` (dev) + `@prisma/client` (runtime),
current stable pinned at install (R1). No zod/no UI libs — hand-rolled
validation and dialog (R3, R4). Everything else reused (i18n dictionary,
ReadingLayout, theme tokens)

**Storage**: PostgreSQL on NeonDB (user-fixed): one `Suggestion` table via
Prisma schema + migration; connection string `DATABASE_URL` provided by Dong
at runtime (dev: `.env`, prod: compose environment). Pooled (`-pooler`) Neon
string recommended (R2)

**Testing**: No test runner exists in relay-tutorial (unchanged) — the
verification battery is quickstart V1–V7: curl contract tests against the
endpoint (caps, allowlist, rate limit, honeypot), a manual UI walk on desktop
+ touch emulation, both locales, plus the standalone-image replay proving the
Prisma engine ships (R6)

**Target Platform**: The existing Docker standalone deployment (long-running
container behind the HTTPS proxy — NOT serverless), so standard Prisma over
TCP works; reading pages stay statically prerendered, only the API route is
dynamic (R2, R6)

**Project Type**: Web feature in the tutorial site (client capture component +
one route handler + one table)

**Performance Goals**: Zero impact on readers who never select text (the
capture component renders nothing until selection); submission round-trip
< 1 s perceived on the reference deployment

**Constraints**: Right-click stays native without a selection (FR-001);
reading never degrades on DB outage (FR-008); no PII, no request bodies in
logs; `DATABASE_URL` is server-only (never `NEXT_PUBLIC`, never baked at
build); caps/limits from R5; commits, Neon provisioning, and deploys are
Dong's

**Scale/Scope**: 1 Prisma schema + 1 migration; 1 route handler; 1 client
component (menu + dialog + touch button); `lib/prisma.ts` + `lib/suggestions.ts`;
i18n keys ×2 locales; ReadingLayout one-line mount; Dockerfile/compose updates
for Prisma + `DATABASE_URL`; no new pages (sitemap stays 28)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The constitution governs the Relay product; this is a tutorial-site feature
(the 010/012 precedent) — its correctness principles apply where the feature
touches their subject matter, and its spirit applies everywhere.

| Principle | Verdict | Notes |
|---|---|---|
| I. Tenant isolation | ✅ N/A | Single-tenant site; the one table holds anonymous public feedback, no tenant data. |
| II. No acknowledged loss | ✅ Pass (spirit) | The dialog confirms success only after the DB insert commits — ack-after-commit, the constitution's own discipline, applied to a suggestion (FR-005/US2-AC3). |
| III. Two data paths | ✅ N/A | No analytics path involved. |
| IV. Single source of truth | ✅ Pass | The page-path allowlist derives from the existing manifest + docs registry — no second list to drift (R3); one write path through one route handler. |
| V. Developer/reader-first | ✅ Pass | Reader experience is the feature; localized errors; reading never degrades on backend failure (FR-008). |
| VI. Requirement-driven, test-verified | ✅ Pass | Input validated against explicit caps before processing; unknown fields rejected; secrets and suggestion bodies never logged; endpoint battery in quickstart. |
| VII. Boring by design | ✅ Pass | One table, one endpoint, one component; no auth system, no admin UI, no queue; in-memory rate limit is honest for a single-container deployment (R5 records the multi-instance caveat). |
| Tech & platform constraints | ✅ Pass (site scope) | Postgres via Prisma per the user's fixed stack; TLS via the existing proxy; the *product's* compose file (relay-platform) is untouched. The unauthenticated endpoint is deliberate and within the letter ("no unauthenticated endpoint returns tenant data"): it is write-only, returns nothing but `{ok}`, and is bounded by R5. |

**Pre-Phase-0 verdict: PASS** (Complexity Tracking empty).
**Post-Phase-1 re-check: PASS** — one migration, one route, one component.

## Project Structure

### Documentation (this feature)

```text
specs/015-reader-suggestions/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── suggestions-api.md
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code

```text
relay-tutorial/ (existing submodule — all changes here)
├── prisma/
│   ├── schema.prisma                       # NEW — Suggestion model (R1, data-model)
│   └── migrations/…                        # NEW — generated by prisma migrate dev
├── lib/
│   ├── prisma.ts                           # NEW — client singleton (R1)
│   └── suggestions.ts                      # NEW — caps, validation, page-path allowlist (R3, R5)
├── app/api/suggestions/route.ts            # NEW — POST handler: validate → rate-limit → insert (R2–R5)
├── components/reading/
│   ├── suggestion-capture.tsx              # NEW — selection watcher, context menu, touch button, dialog (R4)
│   └── reading-layout.tsx                  # MODIFIED — one-line mount inside the article wrapper
├── lib/i18n.ts                             # MODIFIED — suggest.* strings, en + vi (R7)
├── package.json / pnpm-lock.yaml           # MODIFIED — prisma, @prisma/client
├── Dockerfile                              # MODIFIED — prisma generate; engine present in standalone (R6)
├── docker-compose.yml                      # MODIFIED — DATABASE_URL passthrough (runtime env)
└── .env.example                            # NEW — documents DATABASE_URL shape (no secret committed)
```

**Structure Decision**: One mount point (`ReadingLayout`) covers every reading
page in both locales — the same leverage the manifest gives navigation. The
write path is a single route handler so validation, rate limiting, and
persistence live in one place (constitution IV's spirit).

## Implementation Flow (input to /speckit-tasks)

1. **Foundation** (FR-005): Prisma init — schema, migration (Dong provides the
   Neon `DATABASE_URL` first; a local fallback documented), `lib/prisma.ts`,
   generate wired into build; consult `node_modules/next/dist/docs/` for route
   handler + standalone specifics before writing route code (AGENTS.md).
2. **Write path** (FR-005..009): `lib/suggestions.ts` (caps R5, allowlist from
   manifest+docs registry) + `app/api/suggestions/route.ts` (validate →
   honeypot → rate limit → insert → 201/4xx/503); curl battery green locally.
3. **Capture UI** (FR-001..004): i18n keys; `suggestion-capture.tsx` (desktop
   context menu on selection, touch floating button, dialog, fetch, states);
   mount in ReadingLayout.
4. **Deployment** (edge case "static pages, dynamic write"): Dockerfile prisma
   generate + standalone engine verification; compose `DATABASE_URL`
   passthrough; reading pages still statically prerendered (build output
   check).
5. **Verify** ([quickstart.md](./quickstart.md)): endpoint battery, UI walk
   (desktop/touch × en/vi), DB-outage behavior, standalone image replay,
   no-regression build (34 pages, sitemap 28).
6. **Handoff**: no commits; Dong provisions Neon, runs `prisma migrate deploy`,
   sets `DATABASE_URL` on the server, redeploys.

## Complexity Tracking

> No constitution violations — table intentionally empty.

## Notes

- `DATABASE_URL` must never be baked at build: the route handler reads it at
  runtime; the standalone image gets it from compose. `.env` stays untracked
  (already gitignored); `.env.example` documents the shape.
- The in-memory rate limiter is per-container and resets on deploy — recorded
  as accepted (R5); revisit only if the site ever runs multiple replicas.
- Prisma engine in the standalone output is the known deployment landmine —
  quickstart V6 replays the built image with a real POST before handoff (R6).
- The capture component must be a no-op for keyboard-only and non-selecting
  readers; right-click without selection is untouched (FR-001, SC-003).
- Commits/pushes/deploys and all Neon operations are Dong's.
