# Contract: Site Header, Theme Toggle, and Icon

**Feature**: `specs/003-theme-switcher-favicon` · **Date**: 2026-07-29

## C1 — Site header (`components/site-header.tsx`)

| Guarantee | Detail |
|---|---|
| Presence | Rendered by the root layout — appears on every current and future route with no per-page work |
| Content | Brand link ("Building Relay" → `/`, from `lib/tutorial.ts` seriesTitle) left; theme toggle right |
| Styling | Violet Bloom tokens only; correct in both modes; does not overlap content at supported viewport widths (spec edge case) |
| Visibility | Within the initial viewport (no scrolling needed) on landing and chapter pages |

## C2 — Theme toggle (`components/theme-toggle.tsx`)

| Guarantee | Detail |
|---|---|
| Modes | Exactly three options: Light, Dark, System |
| Behavior | Selection applies immediately (class swap, no reload); System follows OS live |
| Persistence | Stored per browser via the provider; absent → system (first visit) |
| Accessibility | Trigger and menu fully keyboard-operable; active mode conveyed to assistive technology (menu item state); trigger has an accessible label |
| No flash | Stored preference applied before first paint on every route |

## C3 — Icon

| Guarantee | Detail |
|---|---|
| Asset path | `app/icon.jpg`, committed to the repo |
| Head output | `<link rel="icon" href="/icon?...">` generated on every route, same-origin |
| Default retired | `app/favicon.ico` deleted; no reference to it remains |
| Third-party independence | Zero reader-facing requests to `avatars.githubusercontent.com` |

## C4 — Scripted verification (quickstart V2)

| Check | Bound |
|---|---|
| Toggle present in rendered HTML of `/` and the chapter route | ≥1 per page |
| `<link rel="icon">` present, same-origin href | every route checked |
| `app/favicon.ico` | absent |
| `githubusercontent` in built HTML | 0 occurrences |
| Hardcoded colors in new components | 0 |
