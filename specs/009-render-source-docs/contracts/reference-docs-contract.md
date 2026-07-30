# Contract: Reference Documents — Routes, Fidelity, and Chapter Links

**Feature**: `specs/009-render-source-docs` · **Date**: 2026-07-30

## C1 — Routes (12 new, all static)

| Route | Guarantee |
|---|---|
| `/docs/{product-vision,personas,journey-map,srs,sad,adr-deep-dives}` | English chrome; full document rendered; hreflang pair; outline block; stable heading anchors |
| `/vi/docs/<same six slugs>` | Vietnamese chrome inside `lang="vi"`; article wrapped `lang="en"`; English-material note; same rendered content |
| All pre-existing routes | Chapter prose unchanged; only the shared `ChapterHeader` gains the source-docs line |

## C2 — Chapter affordance

| Surface | Guarantee |
|---|---|
| Every published chapter header (10 pages) | A labeled source-documents line with one working link per mapped doc: 0.1→product-vision, 0.2→personas, 0.3→journey-map, 0.4→srs, 0.5→sad **and** adr-deep-dives (two links) |
| Locale behavior | en chapters → `/docs/…`; vi chapters → `/vi/docs/…` with the English hint; labels from the i18n dictionary |
| Failure mode | An unresolvable `sourceDoc` renders as plain text — never a dead link |
| Reverse links | Every doc page shows a "referenced by" line linking its citing chapter(s) in the page's locale (sad and adr-deep-dives → 0.5; the other four → their one chapter) |

## C3 — Rendering & content fidelity

| Item | Bound |
|---|---|
| Content | Mirrored files byte-identical to parent `docs/` at ship (drift check green); rendered article contains the full document — no truncation |
| GFM | All pipe tables render as `<table>`; heading hierarchy, fenced code, inline code, blockquotes, emphasis, rules all render; zero raw `|` table markup or `**` artifacts visible |
| Diagrams | All 6 mermaid diagrams render as SVG diagrams post-hydration, legible in BOTH themes; pre-hydration fallback is the fenced source, never a blank |
| Overflow | Wide tables scroll inside their own container; the page never overflows horizontally at 375 px width |
| Isolation | The chapter MDX pipeline gains no GFM; `pnpm build` output for chapter routes unchanged |

## C4 — Scripted verification bounds (quickstart V2)

| Check | Bound |
|---|---|
| Drift | `pnpm check:docs` exits 0; deliberate 1-line change → exits non-zero naming the file (then restored) |
| Route table | exactly 12 new `/docs` + `/vi/docs` routes in the build |
| Sentinel content | srs page contains `FR-TEN-05`; sad page contains `last_sequence` and the D1 row text; adr-deep-dives page contains `Revisit when`; product-vision/personas/journey-map pages contain a chosen sentinel each |
| Tables | `<table` count ≥1 on every table-bearing page (all except adr-deep-dives, which has 0 pipe lines) |
| Chapter links | Each published chapter page (×2 locales) contains href(s) to its mapped doc route(s); 0.5 contains both |
| hreflang | ≥2 (case-insensitive) on all 12 doc pages |
| `div lang` | vi doc pages: `lang="vi"` chrome AND `lang="en"` article wrapper; en doc pages: neither |
| Battery freeze (SC-004) | Word/box/fence counts for all ten existing chapter `page.mdx` files identical to pre-feature values |
| Build gate | `pnpm lint && pnpm build` exit 0 |
