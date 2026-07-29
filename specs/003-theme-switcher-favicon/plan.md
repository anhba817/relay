# Implementation Plan: Theme Switcher and Site Favicon

**Branch**: `main` (no feature branch — consistent with features 001/002) | **Date**: 2026-07-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/003-theme-switcher-favicon/spec.md`

## Summary

Add explicit theme control to the relay-tutorial site: a light/dark/system switcher in
a new slim site-wide header (rendered from the root layout), backed by the
already-installed next-themes provider — which also supplies persistence and no-flash
behavior for free. Replace the scaffold's default favicon with the project avatar,
captured into the repo as `app/icon.jpg` via Next's icon file convention. Decisions in
[research.md](./research.md).

## Technical Context

**Language/Version**: TypeScript 5.9 / Next.js 16.2.12 (existing relay-tutorial app), Node.js 22, pnpm 10

**Primary Dependencies**: Existing: next-themes (provider already wired, feature 001), shadcn Base UI + Violet Bloom tokens, Tailwind v4. New: shadcn `dropdown-menu` component (CLI-generated), `lucide-react` icons (add only if not already present)

**Storage**: Reader's theme preference in browser localStorage (managed entirely by next-themes; key default `theme`)

**Testing**: `pnpm lint && pnpm build` gate + scripted HTML checks (toggle present on all routes, icon link served from own origin, no favicon.ico); manual visual pass for flash/persistence per quickstart

**Target Platform**: relay-tutorial Next.js app (evergreen browsers)

**Project Type**: Small UI/asset feature inside the existing web app (the relay-tutorial submodule)

**Performance Goals**: Theme applies instantly (<1 s per SC-001, in practice one class swap); no added client JS beyond the toggle and menu components

**Constraints**: Violet Bloom tokens only (SC-002 inherits feature 002's no-hardcoded-colors rule); no reader-facing dependency on the GitHub avatar URL (FR-006); preserve first-visit system-preference behavior (FR-003)

**Scale/Scope**: 2 new components, 1 layout edit, 1 asset swap (+1 deletion), ~1 CLI-generated component

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Notes |
|---|---|---|
| I–III (isolation, message loss, data paths) | ✅ N/A | Static site UI + asset; no Relay runtime. |
| IV. Single source of truth | ✅ Pass | Theme state has exactly one owner (next-themes); header renders series identity from the existing manifest. |
| V. Developer/reader-first | ✅ Pass | The whole feature is reader ergonomics (manual mode choice, tab identity). |
| VI. Requirement-driven, test-verified | ✅ Pass | Tasks trace to FR-001..007; scripted checks where scriptable, manual steps named explicitly in quickstart. |
| VII. Boring by design | ✅ Pass | Extends installed libraries (next-themes, shadcn CLI); zero new architecture; Playwright deliberately rejected as premature (research R5). |
| Tech & platform constraints | ✅ Pass | TypeScript/Next.js unchanged. |

**Pre-Phase-0 verdict: PASS** (Complexity Tracking empty).
**Post-Phase-1 re-check: PASS** — design adds two components and an asset; no new state owners, no new dependencies beyond an icon package and a CLI-generated component.

## Project Structure

### Documentation (this feature)

```text
specs/003-theme-switcher-favicon/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── ui-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (relay-tutorial submodule)

```text
relay-tutorial/
├── app/
│   ├── layout.tsx                       # MODIFIED — render <SiteHeader /> above children (R3)
│   ├── icon.jpg                         # NEW — captured avatar, Next icon convention (R4)
│   └── favicon.ico                      # DELETED — default icon retired (FR-007)
├── components/
│   ├── site-header.tsx                  # NEW — slim sticky header: brand link + toggle (R3)
│   ├── theme-toggle.tsx                 # NEW — client component, useTheme + DropdownMenu (R1/R2)
│   └── ui/dropdown-menu.tsx             # NEW — shadcn CLI-generated (R2)
└── package.json                         # MODIFIED — lucide-react (only if absent)
```

**Structure Decision**: All work inside the relay-tutorial submodule (the established
home of site functionality, spec assumption). Parent repo gains only spec artifacts
and, after Dong's submodule commit, an updated pin.

## Implementation Flow (input to /speckit-tasks)

1. **Components** (FR-001/002/005): add shadcn `dropdown-menu` (+ lucide-react if
   needed); build `theme-toggle.tsx`; build `site-header.tsx`; mount in root layout.
2. **Favicon** (FR-006/007): download avatar → `app/icon.jpg`; delete
   `app/favicon.ico`.
3. **Verify** ([quickstart.md](./quickstart.md)): scripted route/HTML checks; manual
   flash + persistence + keyboard pass; both-mode rendering of the header itself.
4. **Handoff**: no commits (standing instruction) — report ready-to-commit files.

## Complexity Tracking

> No constitution violations — table intentionally empty.

## Notes

- FR-004 (no flash) is satisfied by next-themes' injected pre-paint script — already
  active since feature 001. The quickstart still verifies it observationally: claims
  inherited from a library are still claims.
- Commits/pushes remain Dong's (standing instruction, 2026-07-29).
