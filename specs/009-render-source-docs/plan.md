# Implementation Plan: Chapter 0 Improvement — Render the Source Documents

**Branch**: `main` (no feature branch — consistent with features 001–008) | **Date**: 2026-07-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/009-render-source-docs/spec.md`

## Summary

Give readers the primary sources: the six engineering documents behind Part 0
(product vision, personas, journey map, SRS, SAD, ADR deep dives) become reference
pages inside the tutorial site — verbatim mirrors rendered with full GFM fidelity
(~590 table lines) and the SAD's six mermaid diagrams theme-aware — linked from
every chapter's header via the manifest's existing `sourceDoc` mapping, in both
locales, with a sync script + drift check keeping the mirrors truthful. First
infrastructure feature since 004; zero chapter `page.mdx` files change and the
chapter battery is frozen by check. Decisions in [research.md](./research.md).

## Technical Context

**Language/Version**: TypeScript 5.9 / Next.js 16.2.12 (existing relay-tutorial app), Node.js 22, pnpm 10

**Primary Dependencies**: NEW — `react-markdown` + `remark-gfm` (GFM rendering of raw
markdown strings; the docs are MDX-hostile, research R2) and `mermaid`
(client-side, dynamically imported only on diagram-bearing pages, research R3).
Reused: shell/i18n/theme systems (002/003/004), @tailwindcss/typography.

**Storage**: Six mirrored markdown files in `relay-tutorial/content/docs/` (committed;
synced from the parent repo's canonical `docs/` — research R1)

**Testing**: `pnpm lint && pnpm build`; drift check (`pnpm check:docs`); scripted
route/link/hreflang/sentinel-content greps; **battery-freeze check** proving all ten
existing chapter files' counts unchanged (SC-004); manual both-theme diagram and
mobile-table inspection (quickstart)

**Target Platform**: Static prerendered pages, both locales (12 new routes);
diagrams hydrate client-side with a `<pre>` source fallback

**Project Type**: Web app infrastructure feature (relay-tutorial submodule)

**Performance Goals**: mermaid loaded lazily and only on pages containing diagrams;
all reference pages statically generated

**Constraints**: Documents render **verbatim** (FR-005 — mirror files byte-identical
to parent docs, enforced by drift check); GFM stays isolated to reference pages —
the chapters' no-GFM MDX pipeline is untouched; chapter `page.mdx` files untouched
(FR-007); every page keeps the 004 i18n invariants (counterpart route, hreflang
pair, switcher); no dead links (002 rule)

**Scale/Scope**: 6 mirrored docs (~3,570 lines), 1 registry (`lib/docs.ts`), 2 route
files + 1 shared renderer component + 1 mermaid component, 1 `ChapterHeader`
augmentation, 2 i18n dictionary keys, 2 scripts, 12 new routes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Notes |
|---|---|---|
| I–III (isolation, message loss, data paths) | ✅ N/A | Static tutorial site; no Relay runtime. |
| IV. Single source of truth | ✅ Pass | The parent `docs/` stays canonical; the in-app mirror is a declared build input with a sync step and a loud drift check (R1) — divergence is detectable, never silent (FR-009/SC-006). Chapter→doc mapping: the manifest's existing `sourceDoc`, no parallel mapping. |
| V. Developer/reader-first | ✅ Pass | Readers get the primary sources the chapters cite, one action away. |
| VI. Requirement-driven, test-verified | ✅ Pass | Tasks trace to FR-001..009; drift, routes, links, sentinels, and the battery freeze are scripted; diagram/theme legibility is a named manual check. |
| VII. Boring by design | ✅ Pass | Three focused dependencies doing exactly what the feature needs (GFM + diagrams); mermaid is lazy-loaded; no new services, no CMS, no build-time browser. |
| Tech & platform constraints | ✅ Pass | Same stack; static output preserved. |

**Pre-Phase-0 verdict: PASS** (Complexity Tracking empty).
**Post-Phase-1 re-check: PASS** — the design adds a rendering path for reference
pages and one shell line; chapters and their pipeline are untouched.

## Project Structure

### Documentation (this feature)

```text
specs/009-render-source-docs/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── reference-docs-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (relay-tutorial submodule)

```text
relay-tutorial/
├── content/docs/                        # NEW — verbatim mirrors (R1)
│   ├── 01-product-vision.md … 06-adr-deep-dives.md
├── scripts/
│   ├── sync-docs.sh                     # NEW — copy parent docs/ → content/docs/
│   └── check-docs-drift.sh              # NEW — diff mirror vs parent; loud failure
├── lib/
│   ├── docs.ts                          # NEW — six-entry registry (R5)
│   └── i18n.ts                          # MODIFIED — sourceDocs label + English hint
├── components/
│   ├── docs/
│   │   ├── doc-article.tsx              # NEW — react-markdown renderer (R2, R4)
│   │   └── mermaid-diagram.tsx          # NEW — client, theme-aware (R3)
│   └── tutorial/chapter-shell.tsx       # MODIFIED — header source-docs line (R5)
├── app/
│   ├── docs/[slug]/page.tsx             # NEW — en reference pages (R2)
│   └── vi/docs/[slug]/page.tsx          # NEW — vi chrome, English article (R6)
└── package.json                         # MODIFIED — deps + check:docs/sync:docs
```

**Structure Decision**: Reference pages live outside the `part-*` chapter trees at
`/docs/[slug]` with a full `/vi` mirror (R6), preserving every 004 i18n invariant.
The chapter affordance is pure manifest-driven chrome (R5) — the ten existing
chapter files stay byte-identical.

## Implementation Flow (input to /speckit-tasks)

1. **Mirror + scripts** (FR-005/009): `content/docs/` populated by `sync-docs.sh`;
   `check-docs-drift.sh` + npm scripts; drift check green.
2. **Registry + rendering** (FR-002/003/004/006): `lib/docs.ts`; `doc-article.tsx`
   (react-markdown + remark-gfm, table overflow wrapper, heading ids, top
   outline); `mermaid-diagram.tsx`; `app/docs/[slug]/page.tsx` with
   `generateStaticParams` + metadata/hreflang.
3. **Locale mirror** (FR-008): `app/vi/docs/[slug]/page.tsx` — vi chrome,
   `lang="en"` article wrap, English-material note; switcher/hreflang pairs.
4. **Chapter affordance** (FR-001/007): i18n keys; `ChapterHeader` source-docs
   line resolving the manifest's `sourceDoc` through the registry; battery-freeze
   verification of all ten chapter files.
5. **Verify** ([quickstart.md](./quickstart.md)): scripted battery + manual
   diagram/theme/mobile pass.
6. **Handoff**: no commits — ready-to-commit report.

## Complexity Tracking

> No constitution violations — table intentionally empty.

## Notes

- The renderer choice is load-bearing: MDX cannot host these documents (JSX-hostile
  `{…}`/`<…>` in prose) — do not attempt to convert them to `.mdx` (R2).
- All raw HTML in the docs sits inside mermaid fences, so the markdown renderer
  needs no raw-HTML handling (verified during research).
- AGENTS.md rule applies at implementation: consult `node_modules/next/dist/docs/`
  before writing the dynamic-route/`generateStaticParams` code.
- Commits/pushes remain Dong's.
