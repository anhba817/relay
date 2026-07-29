# Data Model: Theme Switcher and Site Favicon

**Feature**: `specs/003-theme-switcher-favicon` · **Date**: 2026-07-29

## E1 — Theme preference

| Field | Rule | Source |
|---|---|---|
| Value | `"light"` \| `"dark"` \| `"system"` | FR-001 |
| Storage | Browser localStorage, next-themes default key (`theme`); per-browser, per-device | FR-003, spec assumption |
| Absent | Treated as `system` (first-visit behavior preserved) | FR-003, US2/AC4 |
| Owner | next-themes provider exclusively — no other code reads/writes the stored value | constitution IV (in spirit) |

**State transitions**: any value → any value via the toggle; `system` resolves to the
OS preference at render time and re-resolves live on OS changes (US1/AC3).

**Effective theme resolution**: stored explicit choice > OS preference. Applied
before first paint by the provider's blocking script (FR-004).

## E2 — Site icon

| Field | Rule | Source |
|---|---|---|
| Asset | `app/icon.jpg` — the captured avatar (source URL verified 2026-07-29: HTTP 200, image/jpeg, ~32 KB) | FR-006, research R4 |
| Serving | Next icon file convention generates `<link rel="icon">` for all routes, served from the site origin | FR-006, v16 docs (app-icons.md) |
| Replaces | `app/favicon.ico` (scaffold default) — deleted | FR-007 |

**Invariant**: no reader-facing request to `avatars.githubusercontent.com` anywhere
in the site (spec edge case: source image may change or vanish without effect).
