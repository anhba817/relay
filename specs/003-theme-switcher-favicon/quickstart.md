# Quickstart Validation: Theme Switcher and Site Favicon

**Feature**: `specs/003-theme-switcher-favicon` · **Date**: 2026-07-29

Contracts in [contracts/ui-contract.md](./contracts/ui-contract.md). All commands run
in `relay-tutorial/`.

## Prerequisites

- Node.js 22+, pnpm 10+, a browser (several checks are visual/interactive)

## V1 — Build gate

```bash
pnpm lint && pnpm build
```

**Expected**: both exit 0; route table unchanged (`/`, `/_not-found`, chapter route).

## V2 — Scripted contract checks (C4)

With `pnpm dev` running:

```bash
for r in / /part-0/chapter-01/from-app-to-infrastructure; do
  html=$(curl -s "http://localhost:3000$r")
  echo "$r toggle:  $(echo "$html" | grep -c 'theme-toggle\|Toggle theme')"   # >=1
  echo "$r icon:    $(echo "$html" | grep -c 'rel="icon"')"                    # >=1, same-origin href
  echo "$r 3rdpty:  $(echo "$html" | grep -c 'githubusercontent')"             # == 0
done
ls app/favicon.ico 2>/dev/null && echo "FAIL: default icon still present" || echo "OK: favicon.ico gone"
ls -la app/icon.jpg                                                            # exists, ~32 KB
grep -cE '#[0-9a-fA-F]{3,8}|rgb\(|oklch\(' components/site-header.tsx components/theme-toggle.tsx  # 0 each
```

## V3 — Manual: switching and coverage (US1, SC-001, SC-002)

1. Open `/` with OS in light mode. Header visible without scrolling; toggle at right.
2. Select **Dark** → landing renders dark palette instantly, no reload.
3. Navigate to the chapter → prose, all boxes, header/footer shell all dark; nothing
   stuck light.
4. Select **Light** → everything back. Select **System** → follows OS again; flip the
   OS setting live and watch the page follow.

## V4 — Manual: persistence and no-flash (US2, SC-003)

1. Select Dark. Navigate landing ↔ chapter several times → stays dark.
2. Hard-refresh (Ctrl+Shift+R) on each route → **no light flash** before dark paints.
3. Close the browser entirely, reopen, revisit → still dark.
4. Clear site data (or private window) → site follows OS preference (first-visit
   behavior).

## V5 — Manual: keyboard and assistive state (SC-005, FR-005)

1. Tab to the toggle trigger (focus visible) → Enter/Space opens the menu.
2. Arrow keys move between Light/Dark/System; Enter selects; Escape closes.
3. The currently active mode is indicated on the menu items (checked state).

## V6 — Favicon in the tab (US3, SC-004)

1. Open any page → browser tab shows the avatar icon (not the framework triangle).
2. Verify in both light and dark browser chrome (icon legibility).
3. DevTools → Network: the icon request is same-origin (`/icon?...`), and no request
   goes to `avatars.githubusercontent.com`.
