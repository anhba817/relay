# Tasks: Theme Switcher and Site Favicon

**Input**: Design documents from `/specs/003-theme-switcher-favicon/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ui-contract.md, quickstart.md

**Tests**: Not requested — verification is the quickstart's scripted checks (contract C4) plus its explicitly manual scenarios (flash, persistence, keyboard), and the `pnpm lint && pnpm build` gate.

**Organization**: Tasks grouped by user story. US2 (persistence/no-flash) is intentionally verification-heavy: research R1 established that next-themes already provides the behavior — the story's job is to prove it, not rebuild it. US3 (favicon) is fully independent of the theme work.

**⚠ Standing instruction**: Do NOT run `git commit` or `git push` — Dong commits personally. The final task is a handoff report with suggested commit messages.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = manual theme switching, US2 = persistence without flicker, US3 = favicon

## Path Conventions

- All paths relative to `/home/dong/work/relay/relay-tutorial/` (the submodule)
- Favicon source URL (user-provided, verified): `https://avatars.githubusercontent.com/u/19990046`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: The CLI-generated component and icon dependency US1 builds on

- [x] T001 Add the dropdown-menu component and icons in relay-tutorial/: `pnpm dlx shadcn@latest add dropdown-menu` (Base UI flavor, consistent with the repo — creates components/ui/dropdown-menu.tsx); check whether `lucide-react` is already in package.json (shadcn may have added it) and `pnpm add lucide-react` only if absent; `pnpm lint && pnpm build` still pass

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: None — the provider infrastructure (next-themes, `.dark` tokens, suppressHydrationWarning) already exists from features 001/002. US1 builds directly on Phase 1.

*(no tasks)*

---

## Phase 3: User Story 1 - Switch the theme manually (Priority: P1) 🎯 MVP

**Goal**: A light/dark/system control visible on every page, applying the Violet Bloom palettes instantly.

**Independent Test**: On landing and chapter pages, the control is visible without scrolling; selecting Dark/Light/System each renders the corresponding palette immediately with no reload (quickstart V3).

### Implementation for User Story 1

- [x] T002 [US1] Create the theme toggle in relay-tutorial/components/theme-toggle.tsx per contract C2: a `"use client"` component using `useTheme()` from next-themes; a shadcn Button (ghost/icon variant) trigger with lucide Sun/Moon icons (CSS crossfade between modes) and an accessible label (e.g. sr-only "Toggle theme"); a DropdownMenu with exactly three items — Light, Dark, System — calling `setTheme`, with the active mode indicated (checked state readable by assistive tech); Violet Bloom token classes only, no hardcoded colors
- [x] T003 [US1] Create the site header in relay-tutorial/components/site-header.tsx per contract C1: slim sticky top bar (token classes: bg-background/border-border, e.g. backdrop-blur optional) with `seriesTitle` from lib/tutorial.ts as a link to `/` on the left and `<ThemeToggle />` on the right; must not overlap content at 768–1280px+ viewports (spec edge case)
- [x] T004 [US1] Mount the header in relay-tutorial/app/layout.tsx: render `<SiteHeader />` inside the ThemeProvider, above `{children}`; verify the existing landing (app/page.tsx) and chapter layout (app/part-0/layout.tsx) still read correctly beneath a sticky header — "needed" means no content is occluded at the initial scroll position (analysis A1); also check that the header's brand link and the chapter breadcrumb's existing "Building Relay" link read acceptably together on chapter pages (analysis I1 — both may stay; the breadcrumb carries part context)
- [x] T005 [US1] Verify switching and coverage per quickstart V3 + scripted C4 subset: `pnpm dev`; rendered HTML of `/` and `/part-0/chapter-01/from-app-to-infrastructure` contains the toggle (≥1 each); manually select Dark → landing, chapter prose, all tutorial boxes, and header/footer shell render dark with nothing stuck light (SC-002); Light and System behave per US1 acceptance scenarios; fix any gaps

**Checkpoint**: US1 fully functional — the MVP

---

## Phase 4: User Story 2 - The choice sticks, without flicker (Priority: P2)

**Goal**: Prove persistence across navigation and restarts, zero wrong-theme flash, and preserved first-visit system behavior.

**Independent Test**: Quickstart V4 — choose dark, navigate, hard-refresh, restart browser: dark persists with no light flash; a fresh/private session follows the OS.

### Implementation for User Story 2

- [x] T006 [US2] Verify the provider guarantees per quickstart V4 and contract C2: confirm structurally that relay-tutorial/app/layout.tsx retains `suppressHydrationWarning` on `<html>` and the ThemeProvider props (`attribute="class" defaultTheme="system" enableSystem`) are unchanged; then run V4's manual pass — persistence across navigations (V4.1), no-flash on hard refresh of both routes (V4.2), survival of full browser restart (V4.3), first-visit system fallback in a private window (V4.4); if any check fails, fix the provider wiring (this story owns FR-003/FR-004) and re-run

**Checkpoint**: US1 AND US2 verified — theme behavior complete

---

## Phase 5: User Story 3 - The site has its own favicon (Priority: P3)

**Goal**: The avatar-derived icon in every browser tab, served from the site's own origin; framework default gone.

**Independent Test**: Quickstart V6 — any page's tab shows the avatar icon; the icon request is same-origin; no request to githubusercontent.

### Implementation for User Story 3

- [x] T007 [P] [US3] Capture the icon: `curl -sL https://avatars.githubusercontent.com/u/19990046 -o app/icon.jpg` in relay-tutorial/; verify it is a valid JPEG ~32 KB (`file app/icon.jpg`); per data-model E2 this is the committed asset — readers never touch the source URL
- [x] T008 [US3] Retire the default and verify per contract C3/C4: delete relay-tutorial/app/favicon.ico; `pnpm build` passes; rendered HTML of both routes contains `<link rel="icon">` with a same-origin href and zero occurrences of `githubusercontent`; browser tab shows the avatar icon (quickstart V6)

**Checkpoint**: All three user stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full validation and handoff

- [x] T009 Run the complete quickstart V1–V6 for specs/003-theme-switcher-favicon/quickstart.md, including V2's full scripted block (toggle presence, icon link, no third-party host, favicon.ico absent, zero hardcoded colors in the two new components) and V5's keyboard/assistive pass (tab to trigger, arrow navigation, active-mode indication); record results
- [x] T010 Handoff (NO commits — standing instruction): report the ready-to-commit file list for relay-tutorial (new: components/theme-toggle.tsx, components/site-header.tsx, components/ui/dropdown-menu.tsx, app/icon.jpg; modified: app/layout.tsx, package.json, pnpm-lock.yaml; deleted: app/favicon.ico) with a suggested commit message, and note the parent-repo follow-ups (spec artifacts + submodule pin after Dong's submodule commit)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 first — US1's toggle imports the dropdown-menu component
- **Foundational (Phase 2)**: empty — provider infrastructure predates this feature
- **US1 (Phase 3)**: T002 → T003 → T004 → T005 (toggle → header imports toggle → layout mounts header → verify)
- **US2 (Phase 4)**: after US1 (verifying persistence requires the switcher to set a preference)
- **US3 (Phase 5)**: independent of everything — T007 can run any time (marked [P]); T008 after T007
- **Polish (Phase 6)**: T009 after all stories; T010 last

### User Story Dependencies

- **US1 (P1)**: Phase 1 only — the MVP
- **US2 (P2)**: US1 (needs the control to create a stored preference); otherwise pure verification
- **US3 (P3)**: none — fully parallel with US1/US2

### Parallel Opportunities

- **T007 (favicon download)** is parallel with all of Phase 3 — different files, no dependencies
- Within US1 the chain is strictly sequential (each file imports the previous)
- **US3 (T007–T008)** can interleave with US2's manual verification passes

## Parallel Example

```bash
# After T001:
#   Track A (US1→US2): T002 → T003 → T004 → T005 → T006
#   Track B (US3):     T007 → T008
# Then: T009 → T010
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. T001 (dropdown-menu + icons)
2. T002–T005 (toggle → header → mount → verify)
3. **STOP and VALIDATE**: manual switching works on every page — demonstrable MVP

### Incremental Delivery

1. US1 → the switcher works everywhere
2. US2 → persistence/no-flash/first-visit proven (library-provided, but proven)
3. US3 → favicon swapped, default retired
4. Polish → full quickstart, keyboard pass, handoff for Dong's commits

---

## Notes

- SC-002's "nothing stuck light" check matters most inside the chapter: the tutorial boxes and prose mapping were built token-only in feature 002 precisely so this feature needs zero changes there — T005 confirms that promise held
- next-themes provides FR-003/FR-004; T006 verifies rather than reimplements (research R1). If verification fails, the fix belongs in provider wiring, not in new persistence code
- No hardcoded colors in any new component (contract C4, constitution VII in spirit)
- NO git commit / git push anywhere — Dong commits personally

---

## Phase 7: Convergence

- [x] T011 Append an execution note to research R2 in specs/003-theme-switcher-favicon/research.md recording the actual implementation: the shadcn CLI generated a Radix-based dropdown-menu (imports from the `radix-ui` package, now a dependency at ^1.6.7) rather than the Base UI flavor the decision anticipated; the theme toggle therefore composes its trigger with Radix's `asChild` pattern; keyboard/ARIA guarantees are unchanged (Radix menu + radio-group semantics) per plan: R2 menu-primitive decision (partial)
