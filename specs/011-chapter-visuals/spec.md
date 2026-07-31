# Feature Specification: Part 0 Chapter Visuals — Diagrams Where Prose Works Hardest

**Feature Branch**: `011-chapter-visuals`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "Improve the Phase 0 chapters with more images and diagrams, currently it's only text and kind of boring"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read a chapter with visual explanations at its hardest moments (Priority: P1)

As the tutorial's reader, each Part 0 chapter gives me diagrams at the places where
the prose is doing its heaviest lifting — the paperwork chain unfolding across
chapters, a journey's emotional arc, 224 requirements funneling into eight drivers,
the anatomy of an ADR — so I can *see* the argument, not just read it, and long
stretches of unbroken text no longer make the chapters feel like a wall of words.

**Why this priority**: This is the user's stated problem — the chapters are
text-only today (0.1 and 0.2 contain not a single visual element; every existing
fence is a text specimen or a text-drawn flow). Purposeful diagrams are the fix;
everything else in this feature exists to support them.

**Independent Test**: Open each English chapter: at least two rendered diagrams
appear at concept-bearing moments (not decoration), each teaching something the
surrounding prose argues; no diagram-free stretch dominates a chapter (both halves
of every chapter contain at least one visual element).

**Acceptance Scenarios**:

1. **Given** any of the five English chapters, **When** read end to end, **Then**
   it contains 2–4 explanatory diagrams placed at key-concept moments (e.g., 0.1's
   build-vs-buy cost argument and non-goals fence line; 0.2's persona quartet and
   their conflicting pulls; 0.3's journey flows and emotional arc as real
   diagrams; 0.4's requirement-anatomy and the ★→requirement traceability chain;
   0.5's 224→8→14 distillation funnel and the ADR anatomy).
2. **Given** any diagram, **When** examined against the surrounding prose,
   **Then** it visualizes a concept the prose already argues — a reader who
   cannot see the diagram loses reinforcement, never required information — and
   it carries a caption or accessible description in the page's language.
3. **Given** chapter 0.3's existing text-drawn flow depictions (the chapter's own
   renditions, not verbatim quotes), **Then** they are upgraded to real rendered
   diagrams — consistent with what the source journey-map document itself now
   uses.
4. **Given** the chapters' verbatim specimen fences (quoted requirement rows, ADR
   records, D-rows in 0.4/0.5), **Then** they remain exactly as they are — text,
   greppable, never converted to diagrams (quote fidelity outranks prettiness).

---

### User Story 2 - The Vietnamese chapters get the same visuals, in Vietnamese (Priority: P2)

As a Vietnamese reader, every diagram the English chapter has, my chapter has too —
with labels translated under the series' settled glossary conventions (English
identifiers like FR-MSG-04, D1, ADR-03 stay English; narrative labels translate) —
so the visual experience is equal, not a downgrade.

**Why this priority**: Bilingual parity is a series property; a visuals upgrade
that only lands in English would make the Vietnamese edition the boring one.

**Independent Test**: For each chapter, the vi page's diagram count equals the en
page's; sampled diagrams show translated narrative labels with identifiers left in
English; captions are in Vietnamese.

**Acceptance Scenarios**:

1. **Given** any chapter pair, **Then** en and vi contain the same number of
   diagrams, in the same locations in the argument.
2. **Given** any vi diagram, **Then** its narrative labels are Vietnamese (settled
   register and glossary), its requirement/driver/ADR identifiers and status
   keywords are English, and its caption is Vietnamese.
3. **Given** both themes, **Then** every diagram on every page in both locales is
   legible in light and dark, and no page overflows horizontally at phone width.

---

### User Story 3 - The series' conventions absorb the new element without losing their teeth (Priority: P3)

As the series author, the format discipline that has protected the chapters
(canonical word bounds, box counts, specimen-fence budget, verbatim greppability)
gains a visual-element class rather than being quietly broken — so future chapters
and future verification runs know exactly what is allowed and what is measured.

**Why this priority**: This feature deliberately edits all ten battery-verified
chapter files — the first content feature to do so since they shipped. Without an
updated convention and a new baseline, every future check would cry wolf.

**Independent Test**: The format conventions document the visual-element class
(diagram fences counted separately from specimen fences); the specimen battery
still passes untouched (verbatim quotes greppable, specimen-fence counts
unchanged); a new battery baseline reflecting the edited chapters is recorded; all
canonical word counts remain within the series' 2,000–4,000 bound.

**Acceptance Scenarios**:

1. **Given** the updated chapters, **Then** specimen-fence counts and their quoted
   text are byte-identical to before (0.4's three, 0.5's three, 0.3's non-flow
   content), while diagram elements are counted as their own class.
2. **Given** the canonical word-count rule, **Then** every chapter stays within
   2,000–4,000 words after captions and lead-in sentences are added; the prose's
   meaning and voice are otherwise unchanged (additions, not rewrites).
3. **Given** the manifest's reading-time estimates, **Then** they are revalidated
   after the visuals land and corrected if materially off.

---

### Edge Cases

- **Verbatim specimens are sacrosanct**: the six specimen fences in 0.4/0.5 (and
  any quoted rows elsewhere) must survive byte-identical — the chapters' fidelity
  battery (greppable quotes, invented-ID detector) must pass before and after.
- **Skip-safety**: SkipAhead readers and screen-reader users must lose nothing
  required — diagrams reinforce; captions and accessible descriptions carry their
  point in text.
- **Theme and viewport**: a diagram legible only in light mode, or one that forces
  horizontal page scroll on a phone, is a defect (same bar as the reference-doc
  diagrams).
- **Translation drift**: vi diagram labels must follow the settled glossary — a
  diagram is not an excuse to re-translate settled terms differently.
- **Maintainability**: every visual must be editable and translatable as text in
  the repository, diffable in review like prose — no opaque binary assets that
  future doc revisions cannot amend.
- **Reading rhythm, not decoration**: a diagram that repeats an adjacent diagram's
  content, or illustrates nothing the chapter argues, should not exist; density is
  bounded (2–4 per chapter) precisely to keep visuals meaningful.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Each of the five Part 0 chapters MUST gain 2–4 explanatory diagrams
  at key-concept moments, distributed so each half of every chapter contains at
  least one visual element.
- **FR-002**: Every diagram MUST visualize a concept the surrounding prose argues
  (reinforcement, never the sole carrier of required information) and MUST carry a
  caption or accessible description in the page's language.
- **FR-003**: Every diagram MUST be legible in both light and dark themes and MUST
  NOT cause horizontal page overflow at phone width.
- **FR-004**: The Vietnamese chapters MUST carry the same diagrams in the same
  argumentative locations, with narrative labels translated per the settled
  register and glossary; requirement/driver/ADR identifiers and status keywords
  stay English.
- **FR-005**: All verbatim specimen fences MUST remain byte-identical text —
  greppable against their source documents; the invented-ID detector and quote
  spot-checks pass unchanged.
- **FR-006**: Chapter 0.3's existing text-drawn flow depictions MUST be upgraded
  to rendered diagrams (they are the chapter's own renditions, not verbatim
  quotes — and their source document already made this move).
- **FR-007**: Every visual MUST be maintainable as reviewable text in the
  repository (translatable, diffable) — no opaque binary image assets.
- **FR-008**: The series format conventions MUST be amended to define the
  visual-element class (counted separately from the specimen-fence budget), and a
  new battery baseline MUST be recorded for the edited chapters; canonical word
  counts stay within 2,000–4,000 with prose additions limited to captions and
  lead-ins.
- **FR-009**: The manifest's reading-time estimates MUST be revalidated after the
  visuals land and corrected if materially off.

### Key Entities

- **Chapter diagram**: A rendered visual in a chapter — has a location in the
  argument, a taught concept, per-locale labels, a caption/accessible description,
  and both-theme legibility.
- **Specimen fence (existing)**: A verbatim quoted text block — explicitly NOT a
  diagram and untouchable by this feature.
- **Format convention (amended)**: The series' measured rules — gains a
  visual-element class with its own counts alongside words, boxes, and specimen
  fences.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 10/10 chapter pages contain 2–4 diagrams; per-chapter counts equal
  across locales; each half of every chapter contains ≥1 visual element.
- **SC-002**: 100% of diagrams legible in both themes on inspection; zero
  horizontal page overflow at 375 px on all 10 pages.
- **SC-003**: 100% of diagrams captioned in the page's language; sampled vi
  diagrams show translated narrative labels with English identifiers.
- **SC-004**: The specimen battery is unchanged: specimen-fence counts and quoted
  text byte-identical; invented-ID detector clean; quote spot-checks pass.
- **SC-005**: All ten canonical word counts remain within 2,000–4,000; a new
  battery baseline (including the diagram-element class) is recorded.
- **SC-006**: Chapter 0.3's flow depictions render as diagrams (zero text-drawn
  flow fences remain in it).
- **SC-007**: Reading-time estimates revalidated; manifest corrected where
  materially off.

## Assumptions

- **Diagrams, not photographs or illustrations-for-mood** — this is a technical
  tutorial; the fix for "boring" is concepts made visible, in the site's own
  visual language (same theme-aware rendering the reference documents already
  use), not stock imagery.
- **Density 2–4 per chapter** balances rhythm against decoration; the existing
  boxes (Why/SkipAhead/Checkpoint) already break text and are not counted as
  diagrams.
- **This is a content feature that deliberately edits all ten chapter files** —
  the battery freeze that protected chapters from *infrastructure* features does
  not apply; instead the battery itself evolves (FR-008) and is re-baselined once,
  as part of the feature.
- **The 007 verbatim-quote definition continues to govern specimens**; nothing in
  this feature touches quoted text.
- **Dong reviews the Vietnamese diagrams** (labels and captions) with the same V4
  read-through discipline as chapter translations; commits/pushes are Dong's.
