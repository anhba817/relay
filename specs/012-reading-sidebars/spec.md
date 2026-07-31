# Feature Specification: Reading Sidebars — Series Navigation and On-This-Page Contents

**Feature Branch**: `012-reading-sidebars`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "Add left sidebar and right sidebar like the https://www.hellointerview.com page"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navigate the whole series from a persistent left sidebar (Priority: P1)

As the tutorial's reader on any reading page (a chapter or a reference document), I
see the series' structure in a persistent left sidebar — the parts, their chapters,
and the reference documents — with my current location clearly highlighted, so I can
jump anywhere in one click and always know where I am in the fifty-chapter arc,
exactly the way the reference site keeps its course outline beside the article.

**Why this priority**: This is the feature's core value. Today the only navigation
is the chapter footer (previous/next/contents) — moving from chapter 0.2 to 0.5, or
from any chapter to a reference document not cited by it, takes multiple hops
through the landing page.

**Independent Test**: From any of the 22 reading pages (10 chapters + 12 reference
documents, both locales), every published chapter and every reference document is
reachable in one click from the left sidebar; the current page's entry is visually
distinct; future parts appear as structure, never as dead links.

**Acceptance Scenarios**:

1. **Given** any reading page on a wide screen, **When** it loads, **Then** a left
   sidebar shows the series outline — Part 0 with its five chapters as links, the
   later parts as visible-but-unlinked structure (they hold no published
   chapters), and a reference-documents group with the six documents — with the
   current page highlighted.
2. **Given** the sidebar's outline, **Then** it derives entirely from the same
   sources that drive all existing navigation (the series manifest and the
   document registry) — publishing a future chapter adds it to the sidebar with
   zero manual edits, and nothing unpublished is ever a link.
3. **Given** a Vietnamese reading page, **Then** the sidebar shows Vietnamese
   chapter/document titles and links to Vietnamese pages; group labels come from
   the locale dictionary.
4. **Given** a long outline and a long article, **Then** the sidebar stays
   available while reading (it does not scroll away with the article) and
   scrolls independently if its own content overflows.

---

### User Story 2 - See and use an on-this-page contents rail on the right (Priority: P2)

As a reader inside a long chapter or reference document, I see a right-hand
"on this page" rail listing the article's sections; clicking an entry jumps to that
section, and as I scroll, the rail highlights the section I am currently in — the
reference site's reading pattern.

**Why this priority**: Chapters run 2,000–4,000 words and documents up to ~900
lines; the right rail is what makes them scannable. Depends visually on the same
layout as US1 but delivers separate value.

**Independent Test**: On every reading page, the rail lists 100% of the article's
top-level sections; each entry jumps to its section; scrolling through the article
moves the highlight through the entries in order.

**Acceptance Scenarios**:

1. **Given** any chapter page, **Then** the rail lists the chapter's top-level
   sections (the same headings a reader sees), each entry jumping to an anchored
   heading — and the chapters' own files are not edited to make this possible
   (anchors and the rail are chrome, and the chapters' verified format battery is
   unchanged).
2. **Given** any reference-document page, **Then** the rail carries the document's
   top-level sections and REPLACES the existing inline "Contents" block — one
   table of contents per page, never two.
3. **Given** a reader scrolling an article, **Then** the entry for the section
   currently in view is visually active, updating as sections pass.
4. **Given** a page whose article has fewer than two top-level sections, **Then**
   the rail is simply absent — no empty chrome.

---

### User Story 3 - The layout adapts: phones lose no function (Priority: P3)

As a phone reader, the article keeps its full width and comfort: the right rail
disappears, and the left outline collapses behind an accessible toggle that opens
it as an overlay — so small screens lose the persistent chrome but keep every
navigation ability.

**Why this priority**: Most reading happens on desktop, but the series has always
held a no-horizontal-overflow bar at phone width; the sidebars must meet it.

**Independent Test**: At phone width, no reading page overflows horizontally; the
series outline opens from a visible control and can be dismissed; every link
reachable on desktop is reachable on the phone. At desktop width, both sidebars
are present without shrinking the article below a comfortable reading measure.

**Acceptance Scenarios**:

1. **Given** a reading page at phone width, **Then** no horizontal page overflow
   exists; the right rail is hidden; a visible, labeled control opens the series
   outline as a dismissible overlay with the same content and highlighting.
2. **Given** a reading page at desktop width, **Then** article, left sidebar, and
   right rail are all visible, and the article column keeps a comfortable reading
   measure (no full-width sprawl, no crushed column).
3. **Given** the keyboard, **Then** the mobile toggle and both sidebars' links are
   focusable and operable without a pointer.

---

### Edge Cases

- **Landing pages are not reading pages**: `/` and `/vi` keep their current layout
  (the reference site's landing differs from its article pages too); the sidebars
  appear on chapter and document pages only.
- **Battery-frozen chapters**: heading anchors and both sidebars must arrive
  without editing any chapter `page.mdx` — the format battery (words, boxes,
  fences, figures) stays byte-frozen for all ten files.
- **Future parts**: parts 1–8 have no published chapters; they appear as
  structure (so the arc is visible) but never as links — the no-dead-link rule.
- **The two-document chapter and referenced-by links**: existing chapter↔document
  affordances (header source links, referenced-by lines, footers) remain; the
  sidebar adds, never replaces them.
- **Anchor collisions and stability**: section anchors must be stable across
  builds and unique within a page (documents already have slugged heading ids —
  chapters gain them by the same rule).
- **No SEO regression**: canonical/hreflang/OG/JSON-LD surfaces and the sitemap
  are untouched; the sidebars are same-page chrome.
- **Diagram zoom vs rail**: the figures' zoom/pan frames and wide tables must not
  collide with the new columns at any width — content containers keep their own
  scroll behavior.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every reading page (chapter or reference document, both locales)
  MUST show a left sidebar with the series outline: parts and their published
  chapters as links, unpublished structure visibly present but never linked, and
  a reference-documents group — derived from the series manifest and document
  registry with zero parallel navigation data.
- **FR-002**: The left sidebar MUST highlight the current page's entry and remain
  available while the article scrolls, scrolling independently when its own
  content overflows.
- **FR-003**: Every reading page whose article has two or more top-level sections
  MUST show a right "on this page" rail listing those sections; entries jump to
  anchored headings; the entry for the section in view is visually active and
  tracks scrolling.
- **FR-004**: Chapter heading anchors and both sidebars MUST arrive as chrome —
  zero edits to any chapter `page.mdx`; the chapters' battery measurements
  (words, boxes, fences, figures) stay identical.
- **FR-005**: On reference-document pages the right rail MUST replace the inline
  "Contents" block — exactly one table of contents per page.
- **FR-006**: All sidebar labels MUST come from the locale dictionary; Vietnamese
  pages show Vietnamese titles and link within the Vietnamese tree; existing
  hreflang/canonical/OG/JSON-LD surfaces and the sitemap are byte-unchanged.
- **FR-007**: At phone width: no horizontal overflow, right rail hidden, and the
  series outline reachable through a visible, keyboard-operable toggle as a
  dismissible overlay. At desktop width: both sidebars visible with the article
  keeping a comfortable reading measure.
- **FR-008**: Landing pages keep their current layout — sidebars appear on
  reading pages only.
- **FR-009**: All existing navigation affordances (chapter footers, header source
  links, referenced-by lines, language switcher) keep working unchanged alongside
  the sidebars.

### Key Entities

- **Series outline (left sidebar)**: The parts → chapters tree plus the
  reference-documents group; a projection of the manifest + registry with a
  current-page marker.
- **On-this-page rail (right sidebar)**: The current article's top-level section
  list with anchors and a scroll-tracked active entry.
- **Reading page**: A chapter or reference-document page — the 22 pages (×2
  locales counted) that receive the new layout; landings excluded.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: On desktop, 22/22 reading pages show both sidebars; 2/2 landing
  pages are unchanged.
- **SC-002**: From any reading page, every published chapter and every reference
  document is reachable in exactly one click; the current page is highlighted on
  22/22; zero dead links (parts 1–8 render as structure only).
- **SC-003**: The rail lists 100% of each article's top-level sections; every
  entry lands on its section; the active highlight moves through all entries
  during a full-page scroll; reference pages show exactly one table of contents.
- **SC-004**: At 375 px, 22/22 reading pages have zero horizontal overflow and a
  working outline toggle; the toggle and sidebar links are keyboard-operable.
- **SC-005**: The ten chapter files' battery measurements are identical before
  and after; the SEO battery (canonicals, hreflang, OG counts, JSON-LD types,
  sitemap) reports the same values as pre-feature.
- **SC-006**: Publishing a chapter (manifest flip) adds it to the sidebar with
  zero manual edits — verified by the established flip-and-revert drill.

## Assumptions

- **"Like hellointerview"** is read as the reading-page pattern: persistent
  left course-outline, right on-this-page rail with scroll tracking, article
  centered — not a pixel-for-pixel copy; styling stays in the site's own
  Violet Bloom token system.
- **Reading pages only** (10 chapters + 12 documents per the current site);
  landings keep their purpose-built layout.
- **Top-level sections** means the headings a reader already sees as section
  titles (the same granularity the reference pages' Contents block uses today).
- **Parts 1–8 appear as unlinked structure** so the series' shape stays visible —
  consistent with the landing page's treatment of forthcoming parts.
- The site header (theme + language switcher) stays as is; the left sidebar sits
  below it, in the established chrome family.
- Commits/pushes are Dong's; nothing is committed by the implementation itself.
