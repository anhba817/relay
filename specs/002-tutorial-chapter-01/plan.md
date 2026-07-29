# Implementation Plan: Tutorial Chapter 0.1 — From App to Infrastructure

**Branch**: `main` (no feature branch — consistent with feature 001) | **Date**: 2026-07-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/002-tutorial-chapter-01/spec.md`

## Summary

Author and publish chapter 0.1 of the *Building Relay* series ("From app to
infrastructure — finding the real product") inside the relay-tutorial Next.js app,
together with the minimal reusable series shell: MDX-based chapter pages, a typed
series manifest driving a landing/table-of-contents at `/`, a chapter header/footer
shell, and Violet Bloom-themed components for the tutorial's recurring box
conventions. Content derives exclusively from `docs/01-product-vision.md`; shape and
format rules from `docs/07-tutorial-plan.md`. Decisions in [research.md](./research.md).

## Technical Context

**Language/Version**: TypeScript 5.9 / Next.js 16.2.12 (existing relay-tutorial app), Node.js 22, pnpm 10

**Primary Dependencies**: Existing: React 19, Tailwind CSS v4, shadcn (Base UI) with Violet Bloom theme, next-themes. New: `@next/mdx` 16.2.12 + `@mdx-js/loader` + `@mdx-js/react` + `@types/mdx` (MDX pages, per bundled v16 docs), `@tailwindcss/typography` 0.5.20 (long-form prose, via Tailwind v4 `@plugin`)

**Storage**: N/A — chapter content is statically compiled MDX; series structure is a typed in-repo manifest (`lib/tutorial.ts`)

**Testing**: `pnpm lint && pnpm build` as the gate; scripted format checks (word count, box-presence counts) per research R7; quickstart scenarios for navigation and both-mode rendering

**Target Platform**: Static pages in the relay-tutorial Next.js app (evergreen browsers)

**Project Type**: Content + presentation feature inside an existing web app (the relay-tutorial submodule)

**Performance Goals**: None feature-specific — chapter and landing prerender statically; no client JS beyond the existing theme provider

**Constraints**: Format rules from docs/07 §2 (2,000–4,000 words; first-person plural present tense; box conventions; chapter = a sitting); factual claims trace 100% to docs/01 (SC-002); theme tokens only — no hardcoded colors (SC-006); series data lives in exactly one place (research R3)

**Scale/Scope**: One chapter (~3,000 words of MDX), one manifest, ~4 new components, one rewritten landing page, one config change

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The constitution (v1.0.0) governs the Relay platform; this feature is tutorial content
and site shell in the companion app — no Relay runtime, data path, or API is touched.

| Principle | Verdict | Notes |
|---|---|---|
| I. Tenant isolation | ✅ N/A | Static content; no tenant data or endpoints. |
| II. No message loss | ✅ N/A | No messaging surface. |
| III. Two data paths | ✅ N/A | No storage. |
| IV. Single writer / source of truth | ✅ Pass (in spirit) | Series structure has exactly one source (the R3 manifest); chapter facts have exactly one source (docs/01). |
| V. API-first, developer-first | ✅ Pass | The reader is the user; the chapter's exercise, checkpoint, and skip-safe takeaways are the DX surface. |
| VI. Requirement-driven, test-verified | ✅ Pass | Tasks trace to FR-001..008; SC-001/004 verified by script, SC-005/006 by quickstart scenarios. Coverage floors target Relay business logic — none exists here. |
| VII. Boring by design, scope commitment | ✅ Pass | MDX via the framework's own plugin, standard typography plugin, no CMS/docs framework; scope bounded to one chapter + minimal shell; tutorial plan treated as frozen contract (risk T1). |
| Tech & platform constraints | ✅ Pass | Constraints bind Relay services; the app remains TypeScript/Next.js, consistent with the stack. |

**Pre-Phase-0 verdict: PASS** (Complexity Tracking empty).
**Post-Phase-1 re-check: PASS** — design adds no runtime services, no storage, one
content pipeline (MDX) native to the framework.

## Project Structure

### Documentation (this feature)

```text
specs/002-tutorial-chapter-01/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── tutorial-site-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (relay-tutorial submodule)

```text
relay-tutorial/
├── next.config.ts                        # MODIFIED — withMDX + pageExtensions (R1)
├── mdx-components.tsx                    # NEW — required by @next/mdx App Router (R1)
├── package.json                          # MODIFIED — new deps (R1, R5)
├── app/
│   ├── globals.css                       # MODIFIED — @plugin typography + prose→token mapping (R5)
│   ├── page.tsx                          # REWRITTEN — series landing / ToC from manifest (R8)
│   └── part-0/
│       └── chapter-01/
│           └── from-app-to-infrastructure/
│               └── page.mdx              # NEW — chapter 0.1 content (R7)
├── lib/
│   └── tutorial.ts                       # NEW — typed series manifest + helpers (R3)
└── components/
    └── tutorial/
        ├── boxes.tsx                     # NEW — Why/Trap/Checkpoint/SkipAhead/Revised/ForwardRef (R4)
        └── chapter-shell.tsx             # NEW — ChapterHeader / ChapterFooter (R6)
```

**Structure Decision**: All source work happens inside the relay-tutorial submodule
(user decision in spec FR-001). The parent repo gains only this feature's spec
artifacts and, at the end, an updated submodule pin. Content routes follow
the canonical `/part-<n>/chapter-<nn>/<slug>` pattern (R2, spec clarification 2026-07-29).

## Implementation Flow (input to /speckit-tasks)

1. **MDX plumbing** (FR-001): install deps; `next.config.ts` + `mdx-components.tsx`;
   verify a trivial MDX route builds.
2. **Series manifest** (FR-007): `lib/tutorial.ts` with parts 0–8, Part 0's five
   chapters, helpers.
3. **Shell components** (FR-008): typography plugin + prose/token mapping; box
   components; ChapterHeader/ChapterFooter.
4. **Landing page** (FR-007, SC-005): rewrite `app/page.tsx` from the manifest.
5. **Chapter 0.1 content** (FR-002..006, SC-001..004): author `page.mdx` per the R7
   section arc with boxes, exercise, worked example, takeaways, CHECKPOINT.
6. **Validate** ([quickstart.md](./quickstart.md)): scripted format checks, navigation
   steps, both-mode rendering, lint/build.
7. **Pin**: update the parent repo's submodule pointer (commit left to Dong).

## Complexity Tracking

> No constitution violations — table intentionally empty.

## Notes

- Commits and pushes are **not** performed by the implementing agent — Dong commits
  personally (standing instruction, 2026-07-29). Tasks will stage nothing; completion
  reports will list what is ready to commit with suggested messages.
- The feature-001 scaffold-purity boundary is retired by this feature's spec
  (Assumptions): relay-tutorial now intentionally grows tutorial-site functionality.
