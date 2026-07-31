# Tasks: Reading Sidebars — Series Navigation and On-This-Page Contents

**Input**: Design documents from `/specs/012-reading-sidebars/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/reading-sidebars-contract.md, quickstart.md

**Tests**: Not requested — verification is the contract battery (quickstart V2
scripted + V3 browser: the rail is client-built and invisible to curl by design),
`pnpm lint && pnpm build`, and the V5 publish drill.

**Organization**: Chrome feature over all 22 reading pages. Non-negotiables:
**zero chapter `page.mdx` edits** (anchors arrive via `mdx-components.tsx`; the
011 battery baseline stays byte-identical); **no parallel navigation data** (the
sidebar projects the manifest + registry); **no dead links** (parts 1–8 unlinked
structure); **SEO surfaces byte-unchanged**; **exactly one TOC on doc pages** (the
rail replaces the inline Contents block); **zero new dependencies** (the drawer is
hand-rolled).

**⚠ Standing instructions**: Do NOT run `git commit` / `git push` (Dong commits
personally). Consult `node_modules/next/dist/docs/` before the client-navigation
code (AGENTS.md).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = left series outline, US2 = on-this-page rail, US3 = responsive/mobile

## Path Conventions

- App paths relative to `/home/dong/work/relay/relay-tutorial/`
- Reading pages: 10 chapters (`app/(en)/part-0/…`, `app/(vi)/vi/part-0/…`) + 12 docs (via `components/docs/doc-page.tsx`)
- Freeze reference: `/home/dong/work/relay/specs/011-chapter-visuals/battery-baseline.txt` (8 columns incl. figures)

---

## Phase 1: Setup

*(no tasks — no new dependencies, no baselines to record: the 011 baseline is the freeze reference)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Dictionary strings and heading anchors both stories need

- [X] T001 [P] Add the sidebar dictionary keys to relay-tutorial/lib/i18n.ts per data-model E6: `shell.onThisPage` ("On this page" / "Trên trang này"), `shell.referenceDocs` ("Reference documents" / "Tài liệu tham khảo"), `shell.openNav` ("Series contents" / "Mục lục loạt bài"), `shell.closeNav` ("Close contents" / "Đóng mục lục"); `pnpm lint` green
- [X] T002 [P] Give chapter h2s stable anchors in relay-tutorial/mdx-components.tsx per data-model E4: map `h2` to a component assigning `id={slugifyHeading(textOf(children))}` using the helpers imported from @/components/docs/doc-article (do NOT duplicate the slug rule); verify with the dev server that a chapter's served HTML carries `<h2 id="…">` for every section, and run the C4 battery-freeze diff against specs/011-chapter-visuals/battery-baseline.txt — MUST be empty (FR-004)

---

## Phase 3: User Story 1 - Navigate the whole series from a persistent left sidebar (Priority: P1) 🎯 MVP

**Goal**: The series outline beside every reading page — current page highlighted, one click to anywhere published.

**Independent Test**: On all 22 reading pages the served HTML contains the sidebar with 5 chapter + 6 doc links (locale-correct), `aria-current` on the current entry, zero part-1..8 hrefs; landings unchanged (quickstart V2 C1).

### Implementation for User Story 1

- [X] T003 [US1] Create relay-tutorial/components/reading/series-sidebar.tsx per data-model E2: client component (`"use client"`); props `{ locale }`; renders `<nav data-series-sidebar aria-label={d.shell.openNav}>` (the "Series contents" label — NOT `shell.contents`, whose rendered string "Contents" would trip C2's proof that the doc pages' inline Contents block was removed) with — per part from lib/tutorial `series`: the part title (locale-aware); published chapters as `<Link>` (locale title, `localePath` href); parts whose chapters are all unpublished/empty as unlinked list items with the muted/forthcoming treatment; then a `d.shell.referenceDocs` group from lib/docs `docs` (locale titles, locale-prefixed hrefs); `usePathname()` marks the current entry with `aria-current="page"` + highlight classes (token styling, consistent with the landing's card language) (FR-001/002/006)
- [X] T004 [US1] Create relay-tutorial/components/reading/reading-layout.tsx per data-model E1 (consult node_modules/next/dist/docs/ for client-nav conventions first): server component `{ locale, children }`; three-column grid — `lg:` shows a 16rem left column hosting SeriesSidebar (sticky below the header, `max-h-[calc(100vh-…)]`, `overflow-y-auto`), center `minmax(0,1fr)` hosting `{children}`, `xl:` shows a 14rem right column (empty slot until US2); below `lg` only the article renders (drawer arrives in US3); article keeps the existing `prose mx-auto` measure inside its column
- [X] T005 [US1] Mount the layout on all reading pages: relay-tutorial/app/(en)/part-0/layout.tsx and app/(vi)/vi/part-0/layout.tsx wrap their prose container in `<ReadingLayout locale=…>`; components/docs/doc-page.tsx renders its existing header/article/footer inside `<ReadingLayout locale={locale}>` (keep the inline Contents block for now — US2 removes it); landings untouched (FR-008); `pnpm lint && pnpm build`
- [X] T006 [US1] Run the C1 battery per quickstart V2 with the dev server: sidebar present in served HTML on all 22 reading pages and absent on `/` and `/vi`; the spot matrix shows chapters == 5, docs == 6, dead == 0, `aria-current` == 1 per page with locale-correct titles; plus the C4 SEO spot matrix (canonical/og:title/og:image == 1 each) and sitemap still 24; fix findings

**Checkpoint**: One-click series navigation live everywhere — MVP delivered

---

## Phase 4: User Story 2 - See and use an on-this-page contents rail on the right (Priority: P2)

**Goal**: The scroll-tracked section rail on every reading page; doc pages down to exactly one TOC.

**Independent Test**: Browser — the rail lists 100% of sections on a chapter and a doc page, click lands, highlight tracks a full scroll; scripted — doc pages have zero inline Contents blocks while keeping h2 ids (quickstart V2 C2 + V3.1).

### Implementation for User Story 2

- [X] T007 [US2] Create relay-tutorial/components/reading/on-this-page.tsx per data-model E3: client component; after mount queries `h2[id]` inside the article container (give the article a stable `id`/data attribute in ReadingLayout's center column); renders the `d.shell.onThisPage` heading + entry list (anchor links); IntersectionObserver drives the active entry (topmost visible section); renders nothing when fewer than 2 headings; wire it into reading-layout.tsx's right column (FR-003)
- [X] T008 [US2] Remove the inline Contents block from relay-tutorial/components/docs/doc-page.tsx (the rail is now the one TOC — FR-005): delete the Contents `<nav>` and the `extractOutline` usage (retire the helper from components/docs/doc-article.tsx if nothing else imports it); keep heading ids, header, referenced-by, vi note, back link; then verify per quickstart V2 C2 — chapter h2 ids ≥5 on 0.5, doc pages `aria-label="Contents"` == 0 with h2 ids retained — and per V3.1 in the browser: rail content, click-lands, scrollspy on one chapter + /docs/sad; `pnpm lint && pnpm build`

**Checkpoint**: Long articles scannable; single TOC everywhere

---

## Phase 5: User Story 3 - The layout adapts: phones lose no function (Priority: P3)

**Goal**: Phone width keeps every capability behind an accessible toggle; desktop keeps the reading measure.

**Independent Test**: 375 px — zero horizontal overflow on reading pages, rail hidden, toggle opens/dismisses the outline (backdrop + Escape), keyboard-operable (quickstart V3.3–V3.4).

### Implementation for User Story 3

- [X] T009 [US3] Add the mobile drawer to relay-tutorial/components/reading/reading-layout.tsx per research R5: below `lg`, a labeled toggle button (`d.shell.openNav`, `aria-expanded`) above the article opens a fixed overlay panel hosting the same SeriesSidebar with a close button (`d.shell.closeNav`) and backdrop; Escape and backdrop dismiss; focus moves into the panel on open; right column hidden below `xl`; then the V3.3–V3.4 browser pass — 375 px overflow sweep on a chapter, a doc page, and a vi page; keyboard walk (tab to toggle, open, tab links, Escape); both themes (FR-007)

**Checkpoint**: All three stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full validation, the publish drill, handoff

- [X] T010 Run the complete quickstart V1–V3 + V5 for specs/012-reading-sidebars/quickstart.md and record results: build gate (V1 — zero new deps), full scripted battery (V2 — C1 presence sweep over all 24 sitemap URLs, spot matrix, anchors, single-TOC, battery freeze vs the 011 baseline, SEO matrix + sitemap 24), browser pass (V3 — rail/scrollspy, desktop stickiness and reading measure, 375 px, keyboard, both themes, en + vi labels), publish drill (V5 — flip 0.5 forthcoming: sidebar entry unlinks and sitemap drops to 22, then revert); flag V4 (Dong's skim: does the reading layout feel like the reference site?)
- [X] T011 Handoff (NO commits — standing instruction): report ready-to-commit files for relay-tutorial (new: components/reading/ ×3; modified: mdx-components.tsx, lib/i18n.ts, both part-0 layouts, components/docs/doc-page.tsx, possibly components/docs/doc-article.tsx) with a suggested commit message; note parent-repo follow-ups (spec artifacts, CLAUDE.md pointer, feature.json, submodule pin); request Dong's V4 pass before committing

---

## Dependencies & Execution Order

### Phase Dependencies

- **Foundational (Phase 2)**: T001 ∥ T002 first (different files)
- **US1 (Phase 3)**: T003 after T001; T004 after T003 (imports it); T005 after T004; T006 after T005
- **US2 (Phase 4)**: T007 after T004 (wires into the layout); T008 after T007
- **US3 (Phase 5)**: T009 after T005 (extends the mounted layout)
- **Polish (Phase 6)**: T010 after all; T011 last

### User Story Dependencies

- **US1 (P1)**: Foundational only — the MVP
- **US2 (P2)**: needs US1's layout shell (the rail lives in its right column)
- **US3 (P3)**: needs US1's mounted layout (the drawer extends it)

### Parallel Opportunities

- T001 ∥ T002 (i18n keys / MDX anchors — disjoint files)
- T007 could be developed alongside T005/T006 (its own file; wiring lands with it)

## Parallel Example

```bash
# Phase 2: T001 | T002
# Then: T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. T001–T006 — the series outline beside every reading page, scripted battery green
2. **STOP and VALIDATE**: C1 sweep + SEO matrix + battery freeze

### Incremental Delivery

1. US1 → one-click navigation everywhere
2. US2 → the scroll-tracked rail; doc pages to one TOC
3. US3 → phones keep everything behind an accessible toggle
4. Polish → full battery + publish drill; Dong's V4; handoff

---

## Notes

- The rail is client-built: curl-based checks CANNOT see its content — V3 browser
  checks carry that weight, V2 carries everything else
- `slugifyHeading`/`textOf` come from the doc renderer — never duplicate the slug
  rule
- A non-empty battery-freeze diff means the anchors leaked into chapter files —
  rework, never re-baseline
- The sidebar must never contain a part-1..8 href — the no-dead-link rule is a
  scripted bound, not a style preference
- NO git commit / git push — Dong commits personally
