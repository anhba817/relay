# Feature Specification: Chapter 0 Improvement — Render the Source Documents

**Feature Branch**: `009-render-source-docs`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "Chapter 0 improvement: Render the corresponding markdown file (product vision, personas, journey map, SRS, SAD, ADR) in each chapter for user to refer. Either embed in the same file or in new page with the chapters linked to. The text format and diagram must display correctly"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Open a chapter's source document and read it correctly rendered (Priority: P1)

As the tutorial's reader, while reading any Part 0 chapter I can open the actual
project document the chapter is teaching from — the product vision (0.1), personas
(0.2), journey map (0.3), SRS (0.4), or SAD and ADR deep dives (0.5) — and read it
inside the tutorial site with everything displaying correctly: headings, tables,
code blocks, and diagrams — so that when a chapter quotes a specimen ("the D1 row",
"ADR-13's status line"), I can see it in its full original context instead of taking
the chapter's word for it.

**Why this priority**: The chapters constantly cite these documents (every `WHY` box
names a section; every fence quotes a specimen); giving the reader the primary
source is the feature's entire value. Every Part 0 chapter also ends by telling the
reader to study the real artifact — which they currently cannot do without leaving
the site.

**Independent Test**: From chapter 0.5, open the SAD reference; the drivers table
displays as a table (not raw pipe characters), all six architecture diagrams display
as diagrams (not code), and the ADR-13 record reads exactly as the repository
version — verifiable by side-by-side comparison.

**Acceptance Scenarios**:

1. **Given** a published Part 0 chapter, **When** the reader looks for the source
   material, **Then** a clearly labeled affordance leads to each document the
   chapter is based on (0.5 leads to two: the SAD and the ADR deep dives), in one
   action.
2. **Given** a rendered document page, **When** compared with the repository
   original, **Then** the content is verbatim and complete — no truncation, no
   paraphrase, no dropped sections — including the document's own version/revision
   notes.
3. **Given** the SRS reference page (the heaviest document: ~780 lines, ~400 table
   rows), **When** viewed, **Then** every table renders as a formatted table with
   its full contents, and long tables remain readable on narrow screens without
   breaking the page layout.
4. **Given** the SAD reference page, **When** viewed in both light and dark themes,
   **Then** all six diagrams render as legible diagrams in both themes, never as raw
   diagram source text.

---

### User Story 2 - Move between chapter and document without getting lost (Priority: P2)

As a reader in either language, I can move from a chapter to its source document,
read around, and come back to where I was — and inside a long document I can jump to
the section a chapter cited (e.g., "SAD §2", "SRS §4.14") without scrolling through
hundreds of lines.

**Why this priority**: The documents run 232–924 lines; without in-document
navigation and a way back, the reference pages would punish the reader for
following a citation.

**Independent Test**: From the Vietnamese chapter 0.4, open the SRS, jump to a named
section from the page top in at most two actions, and return to the chapter; the
site's standard navigation and theme remain available throughout.

**Acceptance Scenarios**:

1. **Given** a reference page, **When** the reader arrives, **Then** the site's
   standard chrome is present (a way back to the contents and to the citing
   context; the theme switcher continues to work).
2. **Given** a long document, **When** the reader wants a specific section, **Then**
   any top-level section is reachable from the page top in at most two actions
   (e.g., via an outline or section links).
3. **Given** a Vietnamese chapter, **When** the reader opens a source document,
   **Then** the same English document is reached and it is labeled as
   English-language material (the documents are the project's canonical engineering
   artifacts and exist only in English).

---

### User Story 3 - The documents stay truthful over time (Priority: P3)

As the series author, when a source document changes in the repository (as the SRS
and SAD just did in the hosted-media revision), the rendered reference pages can be
brought up to date through a defined, repeatable step — and divergence between a
rendered page and its source is detectable, never silent.

**Why this priority**: Part 0's chapters made "the paperwork never lies" a theme; a
stale rendered SRS contradicting the repository would undermine the series' own
lesson. Necessary for longevity, but not for first ship.

**Independent Test**: Modify a line in a source document, run the defined refresh
step, and confirm the reference page shows the change; run the drift check against
an unrefreshed copy and confirm it reports the divergence.

**Acceptance Scenarios**:

1. **Given** a change to any of the six documents in the repository, **When** the
   defined refresh step runs, **Then** the corresponding reference page reflects the
   change with no other pages affected.
2. **Given** a rendered copy that no longer matches its source, **When** the drift
   check runs, **Then** it fails loudly, identifying the diverged document.

---

### Edge Cases

- **Chapter integrity**: the published chapters' teaching prose is battery-verified
  (word counts, box counts, fence counts). The reference affordance must be additive
  chrome — adding it must not alter any existing chapter's measured properties.
- **Cross-references between documents**: the documents cite each other ("Companion
  to 05-sad.md §9") and cite requirement IDs across documents. Plain-text citations
  are acceptable; nothing may render as a broken link.
- **Narrow screens**: the SRS's wide requirement tables must scroll or reflow within
  their own bounds rather than forcing the whole page to overflow.
- **Diagrams and themes**: diagrams must be legible in both light and dark themes —
  a diagram rendered with light-theme colors on a dark background (or vice versa) is
  a failure.
- **The two-document chapter**: 0.5 references both the SAD and the ADR deep dives;
  the affordance must present both distinctly, matching how the manifest already
  records them.
- **Documents not tied to a chapter**: the tutorial plan (docs/07) is the series'
  own meta-document, not chapter source material — out of scope.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every published Part 0 chapter MUST offer a clearly labeled way to
  open each source document it is based on, using the mapping the series manifest
  already records: 0.1 → product vision, 0.2 → personas, 0.3 → journey map, 0.4 →
  SRS, 0.5 → SAD and ADR deep dives. Each document is reachable in one action from
  the chapter, in both locales.
- **FR-002**: Each of the six source documents MUST be readable as its own page
  within the tutorial site at a stable address (dedicated reference pages, not
  inline embedding — see Assumptions), presented under the site's standard chrome.
- **FR-003**: Reference pages MUST render the documents' full formatting correctly:
  heading hierarchy, pipe tables, fenced code blocks, inline code, blockquotes,
  emphasis, and horizontal rules — with no raw markup artifacts visible.
- **FR-004**: All diagrams contained in the documents (currently six, all in the
  SAD) MUST render as legible diagrams in both light and dark themes — never as raw
  diagram source text.
- **FR-005**: Rendered content MUST be verbatim and complete with respect to the
  current repository revision of each document — no truncation, paraphrase,
  reordering, or omission (visual presentation/styling may differ; words may not).
- **FR-006**: Long documents MUST be navigable: any top-level section reachable from
  the page top in at most two actions, so chapter citations like "SAD §9" can be
  followed directly.
- **FR-007**: The reference affordance MUST NOT alter any published chapter's
  teaching prose or its verified format properties (canonical word count, box
  counts, fence counts remain identical for all ten existing chapter files).
- **FR-008**: From Vietnamese chapters, the same English documents are reached, and
  the linking surface MUST indicate they are English-language material; all site
  chrome on reference pages remains locale-correct.
- **FR-009**: There MUST be a defined, repeatable way to bring the reference pages
  up to date when a source document changes, and a check that detects divergence
  between a reference page's content and its repository source.

### Key Entities

- **Source document**: One of the six canonical engineering artifacts (product
  vision, personas, journey map, SRS, SAD, ADR deep dives) — English, heavy
  formatting (up to ~400 table rows; six diagrams), revised over time.
- **Reference page**: The document as a readable page inside the tutorial site —
  stable address, full fidelity, site chrome, section navigation.
- **Chapter→document mapping**: Already held by the series manifest (each chapter
  records its source document(s)); the feature surfaces it to the reader rather
  than inventing a new mapping.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: From every published Part 0 chapter, in both locales, the reader
  reaches each cited source document in one action (10 chapter pages × their
  documents, including 0.5's two).
- **SC-002**: 100% of the six documents' tables and all six diagrams display
  correctly in both themes on visual inspection — zero unrendered pipe characters,
  zero raw diagram source, zero page-breaking overflow on a phone-width screen.
- **SC-003**: An automated comparison between each reference page's content source
  and its repository original shows zero textual divergence at ship time (the
  automated check runs against the page's content input; rendering fidelity on top
  of that input is verified by per-page sentinel checks and the manual spot-check).
- **SC-004**: The existing ten chapter files' battery measurements (word, box,
  fence counts) are identical before and after the feature.
- **SC-005**: Any top-level section of any document is reachable from its page top
  in at most two actions.
- **SC-006**: A deliberate one-line change to a source document is caught by the
  drift check when the refresh step is skipped, and reflected on the page when it
  is run.

## Assumptions

- **Dedicated pages, not inline embedding.** The user left the choice open ("either
  embed in the same file or in new page"). The documents run 232–924 lines (the SRS
  alone is ~780); embedding them inside chapters would bury the teaching prose and
  break the chapters' verified format battery. Dedicated reference pages linked
  from the chapters are the working decision — reversible at planning if desired.
- **Documents remain English.** They are the project's canonical engineering
  artifacts; the chapters themselves teach that identifiers and specimens stay
  English. Vietnamese surfaces link to the English documents with an
  English-language indication rather than translating ~3,600 lines of reference
  material.
- **Scope is the six chapter-source documents** (product vision, personas, journey
  map, SRS, SAD, ADR deep dives). The tutorial plan (docs/07) is out of scope.
- **The manifest's existing chapter→document mapping is authoritative**; the
  feature adds no parallel mapping.
- **The linking affordance is expected to come from the shared chapter chrome**, so
  all ten existing chapter files stay untouched (FR-007); if planning finds
  otherwise, the battery-preservation requirement still binds.
- **Current document revisions at implementation time are the content baseline**
  (the post-media-update revisions, e.g., the 224-requirement SRS).
- Commits/pushes are Dong's; nothing is committed by the implementation itself.
