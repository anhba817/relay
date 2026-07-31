# Research: Reading Sidebars

**Feature**: `specs/012-reading-sidebars` · **Date**: 2026-07-31

Grounding: reading pages are the chapter tree (wrapped by the two `part-0`
layouts) and the doc routes (both render through `DocReferencePage`);
`mdx-components.tsx` exists and is empty — the sanctioned injection point for
chapter heading anchors; the doc renderer already gives h2s slugged ids and
exports `slugifyHeading`; no drawer/sheet primitive exists in the component
library.

## R1 — One `ReadingLayout` shell for all 22 reading pages

- **Decision**: A shared `components/reading/reading-layout.tsx` (server
  component): a three-column grid — left sidebar (visible ≥ `lg`), centered
  article column (keeps the prose measure via `minmax(0,1fr)` + the existing
  `prose mx-auto`), right rail (visible ≥ `xl`) — with both side columns
  `sticky` under the site header and independently scrollable. Mounted in
  exactly three places: the two `part-0` layouts (en/vi) and `DocReferencePage`.
  Landings untouched (FR-008).
- **Rationale**: One layout = the two page families cannot drift; mounting in
  layouts/shared page body means zero chapter-file edits (FR-004).
- **Alternatives considered**: per-page wrappers (10 MDX edits — battery
  violation); a route-group `(reading)` restructure (URLs same but another file
  migration for no gain — the two mount points already cover every reading
  page).

## R2 — Left sidebar: a client component over the manifest, `usePathname` for the highlight

- **Decision**: `components/reading/series-sidebar.tsx` (client): renders the
  outline directly from `lib/tutorial.ts` (parts → published chapters as links,
  parts with no published chapters as unlinked structure with the forthcoming
  badge treatment) plus a reference-documents group from `lib/docs.ts`;
  `usePathname()` marks the current entry (`aria-current="page"`). Locale-aware
  via a `locale` prop: titles via `chapterTitle`/`titleVi`, hrefs via
  `localePath`. Client components server-render, so the sidebar links are in
  the served HTML (greppable, crawlable).
- **Rationale**: FR-001/002/006; the manifest/registry stay the only navigation
  sources (constitution IV); `usePathname` is the one piece of state the server
  layout cannot know.
- **Alternatives considered**: server component + per-page current-prop
  (requires page edits); duplicating an outline constant (parallel data —
  forbidden).

## R3 — Right rail: DOM-derived "on this page" with IntersectionObserver

- **Decision**: `components/reading/on-this-page.tsx` (client): after mount,
  query the article container (a stable `id` on the article element) for `h2`
  elements; build the entry list from their ids/text; highlight the active
  section with an `IntersectionObserver` (topmost heading in view wins); hide
  entirely when fewer than two sections (FR-003's absence rule). Smooth-scroll
  on click via the anchors.
- **Rationale**: The rail works identically for chapters and docs with zero
  per-page data plumbing; a TOC is chrome, not SEO content, so client-side
  construction is fine (and is the standard scrollspy pattern). The absence
  pre-hydration is invisible (the rail column is empty until it fills).
- **Alternatives considered**: build-time heading extraction per page (needs
  page-level data the layouts don't have, or MDX exports — chapter edits);
  scroll-event math (IntersectionObserver is the boring standard).

## R4 — Chapter heading anchors via `mdx-components.tsx`

- **Decision**: Populate the currently-empty `useMDXComponents` with an `h2`
  mapping that assigns `id={slugifyHeading(textOf(children))}` — the exact
  slug rule the doc renderer uses (import both helpers from `doc-article`).
  Chapters gain stable, unique-per-page anchors with zero MDX edits; doc pages
  already have them.
- **Rationale**: FR-004; one slug algorithm site-wide keeps anchors predictable.
- **Alternatives considered**: rehype-slug in the MDX pipeline (a new dependency
  for something two lines of existing code already do); editing headings in
  chapters (battery violation).

## R5 — Mobile: a hand-rolled drawer, no new primitives

- **Decision**: Below `lg`, the layout shows a labeled toggle button (in the
  reading area, under the header) that opens the series outline as a fixed
  overlay panel with a backdrop: `useState` open/close, Escape closes, backdrop
  click closes, focus moves into the panel on open, `aria-expanded`/dialog
  semantics. The right rail is simply hidden below `xl` (FR-007). No page
  overflow at 375 px — both side columns are out of flow on mobile.
- **Rationale**: The component library has no sheet/dialog primitive; pulling
  Radix Dialog in for one drawer fails the boring bar. ~40 lines of standard
  markup covers FR-007's keyboard and dismissal requirements.
- **Alternatives considered**: shadcn Sheet (new primitive + dependency
  surface); CSS-only details/summary (poor focus semantics for an overlay).

## R6 — i18n and verification

- **Decision**: New dictionary keys: `shell.onThisPage` ("On this page" /
  "Trên trang này"), `shell.referenceDocs` ("Reference documents" / "Tài liệu
  tham khảo"), `shell.openNav`/`closeNav` ("Series contents…" / "Mục lục loạt
  bài…") — reuse existing `shell.contents` where it fits. Verification split:
  **scripted** — sidebar present in served HTML on all 22 reading pages with 5
  chapter + 6 doc hrefs and zero part-1..8 hrefs, absent on both landings;
  battery freeze (the 011 baseline, all 8 columns); SEO regression (canonical/
  hreflang/og counts, JSON-LD types, sitemap 24); doc pages contain exactly
  zero inline Contents blocks (the rail replaced them — FR-005) while h2 ids
  remain; the manifest flip drill (SC-006). **Manual/browser** — the rail's
  content and scrollspy (client-built), drawer behavior, keyboard pass, 375 px
  overflow, both themes.
- **Rationale**: The rail is invisible to curl by design (R3); everything else
  scripts.
