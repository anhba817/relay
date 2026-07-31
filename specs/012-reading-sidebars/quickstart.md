# Quickstart Validation: Reading Sidebars

**Feature**: `specs/012-reading-sidebars` · **Date**: 2026-07-31

Contracts in [contracts/reading-sidebars-contract.md](./contracts/reading-sidebars-contract.md).
Commands run in `relay-tutorial/`. The right rail is client-built — curl cannot
see it; its checks are V3 browser checks by design.

## Prerequisites

- Node.js 22+, pnpm 10+, a browser (both themes, 375 px viewport); Dong for V4

## V1 — Build gate

```bash
pnpm lint && pnpm build
```

**Expected**: exit 0; same routes; zero new dependencies in package.json.

## V2 — Scripted battery (contracts C1, C2-anchors, C4)

With `pnpm dev` running:

```bash
# C1 — sidebar on all 22 reading pages, absent on landings
for u in $(curl -s localhost:3000/sitemap.xml | grep -oE '<loc>[^<]+</loc>' | sed 's/<[^>]*>//g'); do
  p=$(echo "$u" | sed -E 's|https?://[^/]+||'); p=${p:-/}
  html=$(curl -s "localhost:3000$p")
  side=$(echo "$html" | grep -o 'data-series-sidebar' | wc -l)
  case "$p" in
    /|/vi) [ "$side" = 0 ] || echo "LANDING HAS SIDEBAR: $p";;
    *) cur=$(echo "$html" | grep -o 'aria-current="page"' | wc -l)
       [ "$side" -ge 1 ] || echo "MISSING SIDEBAR: $p"
       [ "$cur" -ge 1 ] || echo "NO CURRENT MARKER: $p";;
  esac
done; echo "presence sweep done"   # covers SC-002's highlight on all 22, not just the spot matrix

# completeness + no dead links + current-page marker (spot matrix)
for p in /part-0/chapter-01/from-app-to-infrastructure /vi/part-0/chapter-05/deciding-out-loud /docs/sad /vi/docs/srs; do
  html=$(curl -s "localhost:3000$p")
  nav=$(echo "$html" | python3 -c "import sys,re; h=sys.stdin.read(); m=re.search(r'<nav[^>]*data-series-sidebar.*?</nav>', h, re.S); print(m.group(0) if m else '')")
  echo "$p chapters=$(echo "$nav" | grep -oE 'href="[^"]*/part-0/chapter-0[1-5]/[^"]*"' | sort -u | wc -l) docs=$(echo "$nav" | grep -oE 'href="[^"]*/docs/[a-z-]+"' | sort -u | wc -l) dead=$(echo "$nav" | grep -oE 'href="[^"]*part-[1-8]/' | wc -l) current=$(echo "$nav" | grep -o 'aria-current="page"' | wc -l)"
done   # chapters == 5, docs == 6, dead == 0, current == 1 each

# C2 — chapter h2 anchors in served HTML
curl -s localhost:3000/part-0/chapter-05/deciding-out-loud | grep -oE '<h2 id="[^"]+"' | wc -l   # >= 5
# doc pages: inline Contents block gone, rail's server shell may exist but no duplicate list
curl -s localhost:3000/docs/sad | grep -oc 'aria-label="Contents"'; true                          # == 0 (old block removed)
curl -s localhost:3000/docs/sad | grep -oE '<h2 id="[^"]+"' | wc -l                               # >= 10 (ids retained)

# C4 — battery freeze vs the 011 baseline (all 8 columns)
for f in app/\(en\)/part-0/chapter-0[1-5]/*/page.mdx app/\(vi\)/vi/part-0/chapter-0[1-5]/*/page.mdx; do
  echo "$f $(grep -vE '^(import|export)' "$f" | sed 's/<[^>]*>//g' | wc -w) \
$(grep -o '<Why' "$f" | wc -l) $(grep -o '<SkipAhead' "$f" | wc -l) \
$(grep -o '<ForwardRef' "$f" | wc -l) $(grep -o '<Checkpoint' "$f" | wc -l) \
$(grep -c '^```' "$f") $(grep -o '<Figure' "$f" | wc -l)"
done | diff /home/dong/work/relay/specs/011-chapter-visuals/battery-baseline.txt -   # no output

# C4 — SEO regression spot matrix
for p in / /vi /part-0/chapter-05/deciding-out-loud /vi/part-0/chapter-05/deciding-out-loud /docs/sad; do
  html=$(curl -s "localhost:3000$p")
  echo "$p canonical=$(echo "$html" | grep -o 'rel="canonical"' | wc -l) og:title=$(echo "$html" | grep -o 'property="og:title"' | wc -l) og:image=$(echo "$html" | grep -o 'property="og:image"' | wc -l)"
done   # 1 / 1 / 1 each
curl -s localhost:3000/sitemap.xml | grep -oE '<loc>' | wc -l   # == 24

# C4 — existing affordances still present (contract row; counts may GROW because
# the sidebar adds more paths to the same targets — bounds are minimums)
E5=/part-0/chapter-05/deciding-out-loud
curl -s localhost:3000$E5 | grep -o 'href="/part-0/chapter-04/requirements-you-can-test"' | wc -l   # >= 1 (footer prev survives)
curl -s localhost:3000$E5 | grep -oE 'href="/docs/(sad|adr-deep-dives)"' | wc -l                    # >= 2 (header source links survive)
curl -s localhost:3000$E5 | grep -o 'href="/vi/part-0/chapter-05/deciding-out-loud"' | wc -l        # >= 1 (switcher/hreflang survives)
```

## V3 — Browser pass (contracts C2-rail, C3)

1. **The rail**: open an en chapter and `/docs/sad` — the right rail lists every
   section; clicking lands on it; scrolling the full page walks the highlight
   through every entry. A page with <2 sections shows no rail.
2. **Desktop layout**: both sidebars visible, sticky, independently scrollable;
   the article column keeps its reading measure; current chapter highlighted in
   the left outline; parts 1–8 visible but not clickable.
3. **375 px**: no horizontal overflow anywhere; rail gone; the outline toggle
   opens the overlay, backdrop and Escape dismiss it, links work.
4. **Keyboard**: tab to the toggle, open, tab through links, Escape closes.
5. **Both themes**, en + vi pages: labels ("On this page" / "Trên trang này",
   "Reference documents" / "Tài liệu tham khảo") correct.

## V4 — Dong's pass

A skim of the reading layout on a chapter and a doc page in both locales and
themes — does the three-column reading experience feel like the reference site?

## V5 — Publish-flow drill (SC-006, once)

Flip 0.5 to `"forthcoming"` in `lib/tutorial.ts`: its sidebar entry becomes
unlinked structure and the sitemap drops to 22 `<loc>`; revert → link and 24
restored; zero other edits.
