# Quickstart Validation: Internationalization with Vietnamese Chapter 0.1

**Feature**: `specs/004-i18n-vietnamese` · **Date**: 2026-07-29

Contracts in [contracts/i18n-contract.md](./contracts/i18n-contract.md). Commands run
in `relay-tutorial/`.

## Prerequisites

- Node.js 22+, pnpm 10+, a browser
- A Vietnamese-speaking reviewer for V5 (Dong)

## V1 — Build gate and route table

```bash
pnpm lint && pnpm build
```

**Expected**: exit 0; route table now contains `/`, `/vi`, both chapter routes, and
`/_not-found` — nothing else.

## V2 — Scripted contract checks (C6)

With `pnpm dev` running:

```bash
EN=/part-0/chapter-01/from-app-to-infrastructure; VI=/vi$EN
# English regression: address + content unchanged, no vi leakage
curl -s localhost:3000/ | grep -c 'Building <!-- -->Relay\|Building Relay'          # >=1
curl -s localhost:3000$EN | grep -c 'lang="vi"'                                      # == 0
# Vietnamese declaration + hreflang on all four pages
for r in / /vi $EN $VI; do
  html=$(curl -s "localhost:3000$r")
  echo "$r  hreflang=$(echo "$html" | grep -oic 'hreflang')  viDecl=$(echo "$html" | grep -oc 'lang="vi"')"
done   # hreflang >= 2 everywhere (case-insensitive: React serializes hrefLang); viDecl >= 1 only on /vi routes
# Structural parity of the chapter translation
for b in Why SkipAhead ForwardRef Checkpoint; do
  e=$(grep -o "<$b" app$EN/page.mdx | wc -l); v=$(grep -o "<$b" app$VI/page.mdx | wc -l)
  echo "$b en=$e vi=$v"   # vi >= en; Checkpoint exactly 1 both
done
# Switcher maps to counterparts
curl -s localhost:3000$EN | grep -oc "href=\"$VI\""                                  # >=1
curl -s localhost:3000$VI | grep -oc "href=\"$EN\""                                  # >=1
```

## V3 — Manual: switching and chrome coverage (US1, SC-001)

1. On `/`, find the language control beside the theme toggle; select Tiếng Việt →
   land on `/vi`; every chrome string (pitch, part titles, chapter labels,
   forthcoming badges, "the road ahead" equivalent) is Vietnamese — nothing mixed.
2. Open the vi chapter from the vi landing → chapter shell (breadcrumb, "Bạn sẽ tạo
   ra", minutes, footer, forthcoming next-chapter card) is Vietnamese.
3. Switch back to English from the vi chapter → land on the en chapter (not the
   landing) — and vice versa (SC-004, both directions).
4. Keyboard-only: reach and operate the switcher; active language discernible.

## V4 — Manual: persistence semantics (FR-004, SC-005, edge cases)

1. Switch to Vietnamese (sets cookie). Close the browser fully, reopen, visit `/` →
   English renders as always, plus the dismissible "Đọc bằng tiếng Việt →" hint;
   following it lands on `/vi`. No auto-redirect occurred.
2. In a private window (no cookie), open the shared vi chapter link directly →
   renders Vietnamese; verify no `locale` cookie was written by the visit.
3. With cookie=vi, browse en pages via direct URLs → they render English unchanged.

## V5 — Manual: translation quality (US2/AC3, Dong reviews)

Read the Vietnamese chapter end to end. **Expected**: natural Vietnamese carrying the
argument; established terms (WebSocket, API, SDK) in English; the positioning-template
worked example preserves the for/who/that/unlike slots; the exercise and self-checks
are actionable in Vietnamese; nothing reads as machine translation.

## V6 — Theme + favicon interplay (edge case)

On `/vi` pages: theme switcher works identically in both modes; tab icon unchanged.
