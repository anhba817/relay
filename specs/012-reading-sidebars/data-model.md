# Data Model: Reading Sidebars

**Feature**: `specs/012-reading-sidebars` · **Date**: 2026-07-31

No new persistent entities — both sidebars are projections of existing sources.

## E1 — ReadingLayout (components/reading/reading-layout.tsx)

| Element | Rule | Source |
|---|---|---|
| Props | `locale`, `children` (the article) | R1 |
| Grid | left `16rem` (≥ lg) · article `minmax(0,1fr)` with the existing prose measure centered · right `14rem` (≥ xl) | FR-007, R1 |
| Side columns | `sticky` below the site header; `max-h` viewport-bound; `overflow-y-auto` | FR-002 |
| Mobile | Toggle button (labeled, `aria-expanded`) → fixed overlay panel + backdrop; Escape and backdrop dismiss; focus enters panel on open | FR-007, R5 |
| Mounts | `app/(en)/part-0/layout.tsx`, `app/(vi)/vi/part-0/layout.tsx`, `components/docs/doc-page.tsx` — nowhere else (landings excluded) | FR-008 |

## E2 — SeriesSidebar (components/reading/series-sidebar.tsx, client)

| Element | Rule | Source |
|---|---|---|
| Outline | `series` (lib/tutorial): each part; published chapters as links (locale title, `localePath` href); parts with no published chapters render as unlinked structure with the established forthcoming treatment | FR-001, R2 |
| Docs group | `docs` (lib/docs) under `shell.referenceDocs`, locale titles, `/docs`-tree hrefs | FR-001 |
| Current page | `usePathname()` → `aria-current="page"` + visual highlight | FR-002 |
| Invariants | Zero part-1..8 hrefs; server-rendered into the HTML (client components SSR) — greppable | FR-001, R6 |

## E3 — OnThisPage (components/reading/on-this-page.tsx, client)

| Element | Rule | Source |
|---|---|---|
| Source | After mount: `h2[id]` elements inside the article container (stable container id) | R3 |
| Entries | `{id, text}` per heading; click → anchor jump | FR-003 |
| Active state | IntersectionObserver — topmost visible section highlighted, updates on scroll | FR-003 |
| Absence | Fewer than 2 headings → render nothing | FR-003 |
| Label | `shell.onThisPage` | FR-006 |

## E4 — Chapter heading anchors (mdx-components.tsx)

| Element | Rule | Source |
|---|---|---|
| Mapping | `h2` → id from `slugifyHeading(textOf(children))`, both imported from the doc renderer | FR-004, R4 |
| Scope | All MDX pages (chapters); doc pages already carry ids from the same rule | R4 |
| Invariant | Zero chapter `page.mdx` edits; 011 battery baseline byte-identical | FR-004 |

## E5 — Doc-page adoption (components/docs/doc-page.tsx)

| Change | Rule | Source |
|---|---|---|
| Layout | Article body renders inside `ReadingLayout` | R1 |
| Contents block | The inline "Contents" nav is REMOVED (`extractOutline` retired if unused) — the rail is the one TOC | FR-005 |
| Kept | Header (title, referenced-by, vi note), `lang="en"` article wrapper, back-to-contents footer link | FR-009 |

## E6 — Dictionary additions (lib/i18n.ts)

| Key | en | vi |
|---|---|---|
| `shell.onThisPage` | "On this page" | "Trên trang này" |
| `shell.referenceDocs` | "Reference documents" | "Tài liệu tham khảo" |
| `shell.openNav` | "Series contents" | "Mục lục loạt bài" |
| `shell.closeNav` | "Close contents" | "Đóng mục lục" |
