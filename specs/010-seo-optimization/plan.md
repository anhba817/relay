# Implementation Plan: SEO Optimization for the Existing Pages

**Branch**: `main` (no feature branch — consistent with features 001–009) | **Date**: 2026-07-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/010-seo-optimization/spec.md`

## Summary

Make the site's 24 pages fully discoverable and shareable: a manifest-derived
sitemap and robots policy; correct per-locale `<html lang>` via two root layouts
(route groups — the one structural change); per-page Open Graph/Twitter metadata
(metadata API on editable files, shell-hoisted tags on the ten battery-frozen
chapter files); a build-generated series preview image; and TechArticle/WebSite
JSON-LD — all with zero chapter-file edits, zero new dependencies, and zero visible
content changes. Decisions in [research.md](./research.md).

## Technical Context

**Language/Version**: TypeScript 5.9 / Next.js 16.2.12 (existing relay-tutorial app), Node.js 22, pnpm 10

**Primary Dependencies**: None new — `next/og` `ImageResponse` is built in; React 19
document-metadata hoisting carries the chapter OG tags (research R3)

**Storage**: N/A — metadata routes (`app/sitemap.ts`, `app/robots.ts`,
`app/opengraph-image.tsx`) + shell/layout/page metadata edits

**Testing**: `pnpm lint && pnpm build`; scripted quickstart battery (sitemap
completeness, lang matrix, OG matrix, JSON-LD validity, canonical/hreflang
regression, battery freeze with normalized paths); deploy-time validators for
link previews / rich results / Lighthouse (research R6)

**Target Platform**: Static prerendered pages, both locales; same 24 routes plus
three metadata routes (sitemap, robots, opengraph-image)

**Project Type**: Web app infrastructure feature (relay-tutorial submodule)

**Performance Goals**: No regressions — everything static; the OG image renders at
build; no client JS added

**Constraints**: Chapter `page.mdx` files byte-identical (they move between route
groups but do not change — FR-009/SC-007, proven by the path-normalized battery
diff); URLs unchanged by the route-group restructure; exactly one `og:image`
source (the file convention — nothing else may emit it); all absolute URLs from
`NEXT_PUBLIC_SITE_URL` (FR-008); the 009 doc-mirror contract untouched

**Scale/Scope**: 1 restructure (two root layouts + shared `RootShell`), 3 new
metadata routes, `ChapterHeader` gains OG/JSON-LD emission, 2 landing files + 2
doc-route files gain `openGraph`, ~4 spec-artifact greps in quickstart

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Notes |
|---|---|---|
| I–III (isolation, message loss, data paths) | ✅ N/A | Static tutorial site; no Relay runtime. |
| IV. Single source of truth | ✅ Pass | Sitemap, OG values, and JSON-LD all derive from the series manifest + doc registry — no second page list, no duplicated titles. |
| V. Developer/reader-first | ✅ Pass | Readers find and share the tutorial; shared links unfurl credibly in the page's language. |
| VI. Requirement-driven, test-verified | ✅ Pass | Tasks trace to FR-001..009; local assertions scripted; deploy-only validators named and assigned rather than skipped. |
| VII. Boring by design | ✅ Pass | Zero new dependencies; the one structural change (route groups) is the framework's documented pattern for per-locale html lang; chapter OG rides the existing shell-chrome channel. |
| Tech & platform constraints | ✅ Pass | Unchanged stack; static output preserved. |

**Pre-Phase-0 verdict: PASS** (Complexity Tracking empty).
**Post-Phase-1 re-check: PASS** — one restructure, three metadata routes, chrome
extensions; chapters untouched.

## Project Structure

### Documentation (this feature)

```text
specs/010-seo-optimization/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── seo-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (relay-tutorial submodule)

```text
relay-tutorial/
├── app/
│   ├── icon.jpg                          # stays at root segment (verify convention w/o root layout)
│   ├── sitemap.ts                        # NEW — manifest+registry derived (R2)
│   ├── robots.ts                         # NEW (R2)
│   ├── opengraph-image.tsx               # NEW — ImageResponse, 1200×630 (R4)
│   ├── (en)/
│   │   ├── layout.tsx                    # NEW root layout — <html lang="en"> (R1)
│   │   ├── page.tsx                      # MOVED from app/page.tsx (+ openGraph, WebSite JSON-LD)
│   │   ├── part-0/…                      # MOVED verbatim (incl. 5 chapter page.mdx)
│   │   └── docs/[slug]/page.tsx          # MOVED (+ openGraph in generateMetadata)
│   └── (vi)/
│       ├── layout.tsx                    # NEW root layout — <html lang="vi"> (R1; retires div-lang wrapper)
│       └── vi/
│           ├── page.tsx                  # MOVED (+ openGraph, WebSite JSON-LD)
│           ├── part-0/…                  # MOVED verbatim (incl. 5 chapter page.mdx)
│           └── docs/[slug]/page.tsx      # MOVED (+ openGraph)
├── components/
│   ├── root-shell.tsx                    # NEW — shared fonts/providers/header/globals (R1)
│   └── tutorial/chapter-shell.tsx        # MODIFIED — hoisted OG/Twitter meta + TechArticle JSON-LD (R3, R5)
└── lib/
    └── seo.ts                            # NEW — site URL helper, og:locale map, JSON-LD builders
```

**Structure Decision**: Route groups `(en)`/`(vi)` give each locale a true root
layout (URLs unchanged); everything both share lives in `RootShell` + `lib/seo.ts`.
Chapter-level SEO data flows exclusively through the shell from the manifest —
the same channel every feature since 002 has used.

## Implementation Flow (input to /speckit-tasks)

1. **Baseline** (SC-007): current battery numbers already recorded in
   specs/009…/battery-baseline.txt — re-record into this feature's own baseline
   before moving files.
2. **Restructure** (FR-003): route groups + `RootShell` + per-locale root layouts;
   retire the `div lang="vi"` wrapper; verify icon; URLs and battery counts
   unchanged (normalized-path diff).
3. **Discovery surfaces** (FR-001/002/008): `lib/seo.ts`, `app/sitemap.ts`,
   `app/robots.ts`.
4. **Preview image** (FR-006): `app/opengraph-image.tsx` via ImageResponse.
5. **Per-page OG** (FR-005): landings + doc routes via metadata API; chapters via
   shell-hoisted tags (R3 — no `og:image` from the shell).
6. **Structured data** (FR-007): TechArticle in the shell; WebSite on landings.
7. **Verify** ([quickstart.md](./quickstart.md)): scripted battery; flag
   deploy-time validators for Dong.
8. **Handoff**: no commits — ready-to-commit report.

## Complexity Tracking

> No constitution violations — table intentionally empty.

## Notes

- The verified metadata rule that shapes this design: layout-level `openGraph`
  inherits wholesale — a page without its own `openGraph` shows the layout's
  og:title, not its own (research header). Hence the shell-hoisting path for the
  ten frozen chapter files.
- Only `app/opengraph-image.tsx` may produce `og:image`/`twitter:image` — the
  shell and page metadata must not, or validators will flag duplicates.
- The chapter files move but MUST NOT change: `git diff` on their contents (after
  `git add -N`) should show pure renames; the battery diff normalizes
  `app/(en)/` → `app/` and `app/(vi)/vi/` → `app/vi/`.
- Consult `node_modules/next/dist/docs/` before the route-group and metadata-route
  code (AGENTS.md); re-verify `app/icon.jpg` resolution without a top-level
  layout.
- Commits/pushes remain Dong's.
