# Research: Theme Switcher and Site Favicon

**Feature**: `specs/003-theme-switcher-favicon` · **Date**: 2026-07-29

Verified against the Next.js 16.2.12 docs bundled in relay-tutorial and the existing
codebase state (features 001/002).

## R1 — Theme switching mechanism: extend the existing next-themes setup

- **Decision**: Use the already-installed **next-themes** provider (feature 001 wired
  `ThemeProvider attribute="class" defaultTheme="system" enableSystem` around the root
  layout) and add a client component calling its `useTheme()` hook with `setTheme`
  accepting `"light" | "dark" | "system"`. No provider changes are needed.
- **Rationale**: Everything the spec's FR-002/003/004 asks for is what next-themes
  already provides: class-based `.dark` switching (instant, no reload), localStorage
  persistence, system fallback when no stored choice exists, and an injected blocking
  script that applies the stored theme before first paint (the no-flash guarantee —
  `suppressHydrationWarning` is already on `<html>` from feature 001).
- **Alternatives considered**: hand-rolled localStorage + class toggling (reimplements
  next-themes including the flash-prevention script — pure waste); CSS-only
  `prefers-color-scheme` (cannot express an explicit user override).

## R2 — Switcher UI: shadcn dropdown with three modes

- **Decision**: `components/theme-toggle.tsx` (client component): a shadcn
  **DropdownMenu** triggered by an icon Button (sun/moon crossfade), offering
  **Light / Dark / System** items with the active mode indicated. Add the shadcn
  `dropdown-menu` component via the CLI (Base UI flavor, consistent with the repo);
  icons from **lucide-react** (add if not already a dependency).
- **Rationale**: This is the shadcn-documented dark-mode pattern; the Base UI menu
  primitives ship keyboard operability and ARIA state for free (FR-005, SC-005).
  Three explicit items beat a cycling button for discoverability of "system" (spec
  assumption).
- **Alternatives considered**: two-state toggle button (loses the "system" mode the
  spec commits to); segmented control (fine, but bigger visual footprint in a slim
  header); radix-flavored components (repo standardized on Base UI in feature 001).
- **Execution note (2026-07-29, converge T011)**: despite the repo's Base UI
  standardization, `shadcn add dropdown-menu` generated a **Radix-based** component
  (`components/ui/dropdown-menu.tsx` imports from the `radix-ui` package, added as a
  dependency at ^1.6.7). The theme toggle therefore composes its trigger with Radix's
  `asChild` pattern rather than Base UI's `render` prop, and uses
  `DropdownMenuRadioGroup`/`RadioItem` for the active-mode indication. Keyboard and
  ARIA guarantees are unchanged (Radix menu + radio-group semantics). Consequence:
  the repo now mixes primitive flavors per component — whatever the shadcn registry
  serves for each — which is acceptable while components stay CLI-generated.

## R3 — Placement: a slim site-wide header in the root layout

- **Decision**: New `components/site-header.tsx`: a slim sticky header rendered in
  `app/layout.tsx` above `{children}` — series title "Building Relay" linking to `/`
  on the left (from `lib/tutorial.ts`), the theme toggle on the right. Violet Bloom
  tokens only.
- **Rationale**: FR-001 demands the control on every page in a consistent location;
  the root layout is the only place that covers current and future routes with one
  component. A header also gives chapters a persistent way home (bonus to feature
  002's navigation without changing its contracts).
- **Alternatives considered**: floating corner button (overlaps chapter prose at
  narrow widths — spec edge case); per-page placement (duplication, drift);
  footer placement (fails "visible without scrolling").

## R4 — Favicon: capture the avatar into `app/icon.jpg`, delete the default

- **Decision**: Download `https://avatars.githubusercontent.com/u/19990046` (verified
  2026-07-29: HTTP 200, `image/jpeg`, ~32 KB) once, commit it as
  **`app/icon.jpg`**, and **delete the scaffold's `app/favicon.ico`**. Next's icon
  file convention (verified in the bundled v16 docs, app-icons.md: `icon.(ico|jpg|
  jpeg|png|svg)`) generates the `<link rel="icon">` tags automatically for every
  route.
- **Rationale**: File convention = zero code, served from the site's own origin
  (FR-006's third-party-independence rule and the spec's image-disappears edge case);
  deleting `favicon.ico` satisfies FR-007 (default icon no longer served). JPEG is an
  accepted extension, so no format conversion is required.
- **Alternatives considered**: referencing the GitHub URL in metadata (reader-facing
  third-party dependency — explicitly forbidden by FR-006); converting to .ico/.png
  (extra tooling for no gain — the convention accepts jpg); `public/favicon.ico`
  (bypasses the metadata convention and keeps the .ico name without benefit).

## R5 — Verification approach

- **Decision**: Reuse the project's gates: `pnpm lint && pnpm build`, plus scripted
  checks — rendered HTML contains the theme toggle on `/` and the chapter route;
  `<link rel="icon">` points at the app-served icon; `app/favicon.ico` absent;
  stored-preference behavior exercised via the dev server with a seeded
  `localStorage` (manual/visual step in quickstart for the flash check).
- **Rationale**: Matches constitution VI in spirit (scripted where scriptable) at
  this feature's scale; no test framework exists in the repo and none is warranted
  by a toggle + icon.
- **Alternatives considered**: adding Playwright for the persistence/flash checks
  (real browser automation is the *right* tool but a heavy new dependency for one
  feature — deferred until the tutorial itself introduces E2E testing in Part 2's
  chapters).
