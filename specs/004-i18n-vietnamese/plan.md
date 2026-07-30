# Implementation Plan: Internationalization with Vietnamese Chapter 0.1

**Branch**: `main` (no feature branch — consistent with features 001–003) | **Date**: 2026-07-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/004-i18n-vietnamese/spec.md`

## Summary

Add a two-locale structure to the relay-tutorial site without touching a single
English URL: Vietnamese lives under a literal `/vi` mirror subtree, chrome strings
come from one dictionary module, a header language switcher maps any page to its
counterpart, and persistence is a cookie plus a no-redirect landing hint. Chapter 0.1
is authored as a faithful Vietnamese translation (`page.mdx` under `/vi`, English
slug kept), with the chapter shell and box components gaining a defaulted `locale`
prop. No i18n framework — two locales and twenty strings don't need one. Decisions in
[research.md](./research.md).

## Technical Context

**Language/Version**: TypeScript 5.9 / Next.js 16.2.12 (existing relay-tutorial app), Node.js 22, pnpm 10

**Primary Dependencies**: No new packages. Existing: MDX pipeline (feature 002), next-themes + header (feature 003), shadcn components, Violet Bloom tokens

**Storage**: `locale` cookie (1-year, SameSite=Lax), written only on explicit switch; absent = English

**Testing**: `pnpm lint && pnpm build` gate + scripted checks (English-URL regression, en/vi box-count parity, hreflang presence, `div lang="vi"`, counterpart links); manual translation-quality review by Dong

**Target Platform**: Static prerendered pages, evergreen browsers

**Project Type**: Content + i18n feature inside the existing web app (relay-tutorial submodule)

**Performance Goals**: None new — all pages remain statically prerendered; the only added client JS is the switcher (same order as the theme toggle)

**Constraints**: Every pre-existing English URL byte-stable in address and language (SC-003); no auto-redirects; no browser-locale detection; Violet Bloom tokens only; single source per concern (strings → `lib/i18n.ts`, series data → `lib/tutorial.ts`, facts → English chapter)

**Scale/Scope**: 2 locales; ~20 chrome strings; 1 translated chapter (~2,600 words); 3 new routes (`/vi`, vi chapter, vi part layout); ~5 components touched with a defaulted prop

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Notes |
|---|---|---|
| I–III (isolation, message loss, data paths) | ✅ N/A | Static site; no Relay runtime. |
| IV. Single source of truth | ✅ Pass | One dictionary module for strings; one manifest for series data (extended, not duplicated); the English chapter is the single source of the translated argument. |
| V. Developer/reader-first | ✅ Pass | The feature is reader reach — a Vietnamese reader completes Part 0's first step natively. |
| VI. Requirement-driven, test-verified | ✅ Pass | Tasks trace to FR-001..009; parity and regression checks scripted; translation quality assigned to a named human reviewer. |
| VII. Boring by design | ✅ Pass | Zero new dependencies; `/vi` mirror instead of framework machinery; explicit locale props over context magic. The next-intl rejection is reasoned (R1) with a revisit condition implicit in scale. |
| Tech & platform constraints | ✅ Pass | TypeScript/Next.js unchanged. |

**Pre-Phase-0 verdict: PASS** (Complexity Tracking empty).
**Post-Phase-1 re-check: PASS** — design adds routes and a dictionary, no new state
owners (cookie has one writer: the switcher), no dependencies.

## Project Structure

### Documentation (this feature)

```text
specs/004-i18n-vietnamese/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── i18n-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (relay-tutorial submodule)

```text
relay-tutorial/
├── lib/
│   ├── i18n.ts                          # NEW — Locale type, dictionaries, t(), path helpers (R2)
│   └── tutorial.ts                      # MODIFIED — titleVi/readerProducesVi fields + localized accessors (R2)
├── components/
│   ├── language-switcher.tsx            # NEW — client; EN/VI links to counterpart path + cookie (R3)
│   ├── site-header.tsx                  # MODIFIED — becomes locale-aware (usePathname), adds switcher (R3)
│   ├── landing.tsx                      # NEW — extracted landing UI, locale prop (R6)
│   ├── locale-hint.tsx                  # NEW — client; dismissible cross-locale hint on landings (R3)
│   └── tutorial/
│       ├── boxes.tsx                    # MODIFIED — locale prop (default "en") localizing labels (R5)
│       └── chapter-shell.tsx            # MODIFIED — locale prop; vi titles/labels from manifest (R5)
├── app/
│   ├── page.tsx                         # MODIFIED — thin wrapper over <Landing locale="en"> + alternates (R6)
│   ├── part-0/chapter-01/from-app-to-infrastructure/page.mdx  # MODIFIED — metadata alternates only (R4)
│   └── vi/
│       ├── layout.tsx                   # NEW — <div lang="vi"> subtree wrapper (R4)
│       ├── page.tsx                     # NEW — <Landing locale="vi"> + vi metadata (R6)
│       └── part-0/
│           ├── layout.tsx               # NEW — prose container (mirror of en part layout)
│           └── chapter-01/from-app-to-infrastructure/
│               └── page.mdx             # NEW — chapter 0.1 in Vietnamese (R5)
```

**Structure Decision**: All work inside relay-tutorial. English routes untouched
except additive metadata (hreflang alternates) — the one edit to an existing English
page, changing head links only, never body content or address (FR-005/SC-003 safe).

## Implementation Flow (input to /speckit-tasks)

1. **i18n foundation** (FR-001): `lib/i18n.ts` dictionaries + helpers; manifest
   vi fields.
2. **Switcher + header** (FR-002/003/004): language-switcher, locale-aware header,
   cookie, locale-hint on landings.
3. **Localized chrome** (FR-001): landing extraction with locale; shell + boxes
   locale props; `/vi` landing and layouts with `div lang="vi"`.
4. **Vietnamese chapter** (FR-006/007): author the translation `page.mdx`; parity
   with English chapter.
5. **Metadata** (FR-008): hreflang alternates on all four pages; vi titles.
6. **Verify** ([quickstart.md](./quickstart.md)): scripted regression/parity checks +
   manual translation review (Dong).
7. **Handoff**: no commits — report ready-to-commit files.

## Complexity Tracking

> No constitution violations — table intentionally empty.

## Notes

- The SC-003 ↔ SC-005 tension (no redirects vs. cross-session persistence) is
  resolved by design in research R3: cookie + dismissible landing hint, never a
  redirect. If Dong prefers auto-redirect from `/`, that is a spec change to SC-003
  first.
- Translation authorship: the agent drafts the Vietnamese chapter; Dong is the named
  quality reviewer (spec assumption) — the quickstart makes that review a first-class
  validation step, not an afterthought.
- Commits/pushes remain Dong's (standing instruction, 2026-07-29).
