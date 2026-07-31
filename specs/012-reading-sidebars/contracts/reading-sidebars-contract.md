# Contract: Reading Sidebars — Layout, Navigation, and Regressions

**Feature**: `specs/012-reading-sidebars` · **Date**: 2026-07-31

## C1 — Left sidebar (served HTML — scriptable)

| Check | Bound |
|---|---|
| Presence | Sidebar nav in the served HTML of all 22 reading pages; absent on `/` and `/vi` |
| Completeness | 5 chapter hrefs + 6 doc hrefs per page, locale-prefixed on vi pages |
| No dead links | Zero hrefs matching `part-[1-8]/` in the sidebar; parts 1–8 appear as text |
| Current page | The page's own path carries `aria-current="page"` on 22/22 |
| Labels | Dictionary-driven; vi pages show vi titles/labels |

## C2 — Right rail and anchors

| Check | Bound |
|---|---|
| Chapter anchors | Every chapter h2 in served HTML carries a slugged `id` (scriptable) |
| Rail content (browser) | Lists 100% of the article's top-level sections; click lands on the section |
| Scrollspy (browser) | Active entry tracks a full-page scroll through every section |
| Absence | Pages with <2 sections show no rail |
| One TOC | Doc pages: inline Contents block gone (0 occurrences), rail present; heading ids retained |

## C3 — Responsive & accessibility (browser)

| Check | Bound |
|---|---|
| 375 px | Zero horizontal overflow on 22/22; rail hidden; toggle visible and opens/dismisses the outline (button, backdrop, Escape) |
| Desktop | Both sidebars visible; article keeps the prose measure; sticky side columns scroll independently |
| Keyboard | Toggle and all sidebar links focusable/operable; `aria-expanded`/`aria-current` correct |

## C4 — Freeze and regressions (scriptable)

| Check | Bound |
|---|---|
| Battery freeze | All 10 chapter files byte-identical to the 011 baseline (all 8 columns incl. figures) |
| SEO | canonical=1, hreflang≥2, og:title=1, og:image=1 per page; JSON-LD types unchanged (10× TechArticle, 2× WebSite, 0 docs); sitemap still exactly 24 |
| Existing affordances | Chapter footers, header source links, referenced-by lines, switcher hrefs all still present (minimum bounds — absolute counts may grow, since the sidebar adds more paths to the same targets) |
| Publish drill | Flip 0.5 → forthcoming: its sidebar entry becomes unlinked structure and sitemap drops to 22; revert restores both (SC-006) |
| Build gate | `pnpm lint && pnpm build` exit 0; zero new dependencies |
