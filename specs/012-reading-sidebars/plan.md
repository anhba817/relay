# Implementation Plan: Reading Sidebars — Series Navigation and On-This-Page Contents

**Branch**: `main` (no feature branch — consistent with features 001–011) | **Date**: 2026-07-31 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/012-reading-sidebars/spec.md`

## Summary

Give all 22 reading pages the hellointerview-style reading layout: a persistent
left series outline (manifest + registry driven, current page highlighted, parts
1–8 as unlinked structure, reference-docs group) and a right "on this page" rail
(DOM-derived, IntersectionObserver scrollspy) around a centered article column —
one shared `ReadingLayout` mounted in exactly three places (the two part-0 layouts
and `DocReferencePage`), chapter heading anchors injected through the empty
`mdx-components.tsx`, a hand-rolled accessible mobile drawer, zero new
dependencies, zero chapter-file edits. Decisions in [research.md](./research.md).

## Technical Context

**Language/Version**: TypeScript 5.9 / Next.js 16.2.12 (existing relay-tutorial app), Node.js 22, pnpm 10

**Primary Dependencies**: None new — `usePathname` (next/navigation),
IntersectionObserver, existing manifest/registry/i18n/token systems

**Storage**: N/A — chrome components + two layout edits + one shared-page edit

**Testing**: `pnpm lint && pnpm build`; scripted sidebar/landing/SEO/battery
greps; the manifest flip drill; browser pass for rail scrollspy, drawer,
keyboard, 375 px, both themes (quickstart)

**Target Platform**: Static prerendered pages; the sidebar server-renders (in
served HTML), the rail hydrates client-side

**Project Type**: Web app chrome feature (relay-tutorial submodule)

**Performance Goals**: No new dependencies; rail observer per page only; no
layout shift for the article column at any breakpoint

**Constraints**: Chapter `page.mdx` files byte-frozen (011 baseline holds, all
columns incl. figures); no parallel navigation data (manifest + registry only);
no dead links (parts 1–8 unlinked); SEO surfaces byte-unchanged; doc pages end
with exactly one TOC (the rail replaces the inline Contents block); drawer
keyboard-operable; article keeps the prose measure

**Scale/Scope**: 3 new components (`reading-layout`, `series-sidebar`,
`on-this-page`), 1 `mdx-components.tsx` mapping, 2 part-0 layout edits, 1
`doc-page.tsx` edit (adopt layout, drop Contents block), ~4 i18n keys

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Notes |
|---|---|---|
| I–III (isolation, message loss, data paths) | ✅ N/A | Static tutorial site; no Relay runtime. |
| IV. Single source of truth | ✅ Pass | The outline is a projection of the manifest + registry; the rail derives from the rendered article; zero parallel navigation data. |
| V. Developer/reader-first | ✅ Pass | One-click series navigation and scannable long articles — the reading experience the reference site demonstrates. |
| VI. Requirement-driven, test-verified | ✅ Pass | Tasks trace to FR-001..009; sidebar/SEO/battery checks scripted; the client-built rail and drawer get named browser checks. |
| VII. Boring by design | ✅ Pass | Zero new dependencies; the drawer is ~40 lines of standard markup instead of a new primitive; anchors reuse the existing slug rule via the already-provided MDX hook. |
| Tech & platform constraints | ✅ Pass | Unchanged stack; static output preserved. |

**Pre-Phase-0 verdict: PASS** (Complexity Tracking empty).
**Post-Phase-1 re-check: PASS** — chrome components and three mount points.

## Project Structure

### Documentation (this feature)

```text
specs/012-reading-sidebars/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── reading-sidebars-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (relay-tutorial submodule)

```text
relay-tutorial/
├── components/reading/
│   ├── reading-layout.tsx               # NEW — 3-column grid + mobile drawer host (R1, R5)
│   ├── series-sidebar.tsx               # NEW — client; manifest/registry outline + usePathname highlight (R2)
│   └── on-this-page.tsx                 # NEW — client; DOM headings + IntersectionObserver (R3)
├── mdx-components.tsx                   # MODIFIED — h2 → slugged id (R4)
├── lib/i18n.ts                          # MODIFIED — onThisPage / referenceDocs / openNav / closeNav
├── app/(en)/part-0/layout.tsx           # MODIFIED — mounts ReadingLayout (en)
├── app/(vi)/vi/part-0/layout.tsx        # MODIFIED — mounts ReadingLayout (vi)
└── components/docs/doc-page.tsx         # MODIFIED — adopts ReadingLayout; inline Contents block removed (FR-005)
```

**Structure Decision**: The reading chrome is one shared shell with two thin
mount points; heading anchors flow through the MDX hook so the ten battery-frozen
chapter files never change.

## Implementation Flow (input to /speckit-tasks)

1. **Anchors** (FR-004): `mdx-components.tsx` h2 mapping (slug rule shared with
   the doc renderer); battery freeze re-verified.
2. **Sidebar + rail components** (FR-001/002/003): `series-sidebar`,
   `on-this-page`, i18n keys.
3. **Layout shell + mounts** (FR-007/008): `reading-layout` with the grid,
   sticky columns, and drawer; mounted in both part-0 layouts and
   `DocReferencePage` (Contents block removed — FR-005).
4. **Verify** ([quickstart.md](./quickstart.md)): scripted battery + SEO
   regression + flip drill; browser pass for rail/drawer/keyboard/viewport.
5. **Handoff**: no commits — ready-to-commit report.

## Complexity Tracking

> No constitution violations — table intentionally empty.

## Notes

- The rail is client-built (R3) — curl-based checks CANNOT see it; its checks
  are explicitly browser checks, and the scripted battery asserts everything
  else.
- `slugifyHeading`/`textOf` are imported from the doc renderer, not duplicated —
  one slug algorithm site-wide.
- The 011 battery baseline (8 columns incl. figures) is the freeze reference;
  chapters must remain byte-identical.
- Consult `node_modules/next/dist/docs/` before the `usePathname`/client-nav
  code (AGENTS.md).
- Commits/pushes remain Dong's.
