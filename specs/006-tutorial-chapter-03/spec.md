# Feature Specification: Tutorial Chapter 0.3 — Journeys, Where Products Die

**Feature Branch**: `006-tutorial-chapter-03`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "chapter 0.3"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read chapter 0.3 and follow the derivation (Priority: P1)

As the tutorial's reader, I read chapter 0.3 — "Journeys — where products die" — and
watch journey maps being built from chapter 0.2's personas: the four journeys in order
of how directly each person touches the product, the emotional arcs, and above all the
**★ moments** — the single stages where each journey is won or lost — so I understand
where a product actually dies and why requirements cluster there.

**Why this priority**: The chapter's prose is the deliverable; it is Part 0's third
step (docs/07 §3: "Journeys — where products die; the ★ moments") and the bridge from
people (0.2) to testable requirements (0.4).

**Independent Test**: A reader who finished 0.2 can answer: what the four journeys
are, why an infrastructure product maps journeys for people who never buy it (Priya,
Tuan), which stage kills adoption in Mai's journey (the first message, Stage 4 ★),
and what a ★ moment is — without consulting docs/03.

**Acceptance Scenarios**:

1. **Given** the published chapter, **When** read end to end, **Then** it presents
   the four journeys from docs/03 (Mai's problem-to-production, David's approval
   path, Priya's dispute resolution, Tuan's message through a tunnel) as derivations
   from the 0.2 personas — including why journeys 3 and 4 are unusual inclusions and
   the docs/03 claim that mapping them is how the hard requirements were found.
2. **Given** the chapter, **When** checked against the series format rules (docs/07
   §2), **Then** it is 2,000–4,000 words by the canonical measure, first-person
   plural present tense, with the box conventions (≥2 `WHY` citing docs/03, 1
   `SKIP AHEAD`, ≥1 forward reference, skip-safe takeaways, exactly one closing
   `CHECKPOINT`).
3. **Given** the ★ concept, **When** the reader finishes, **Then** they have seen
   each journey's ★ moment named and argued (Mai: first message; Priya:
   reconstruction; Tuan: losing signal) and understand that ★ moments are where
   effort concentrates (docs/03's closing section).
4. **Given** the chapter's factual claims, **Then** 100% trace to docs/03 (journey
   content) or 0.1/0.2 artifacts (context) — no invented stages, emotions, or
   moments. The tutorial plan's forward promise (docs/07: the journeys become
   executable tests — the Tuan test, the Priya test) is carried by at least one
   forward reference.

---

### User Story 2 - Produce the chapter's reader artifacts (Priority: P2)

As the reader, I finish the chapter by producing its assigned artifacts — **journey
maps for my own product's personas, with each journey's ★ moment identified**
(docs/07 §3) — following worked guidance, so I have practiced finding where my
product can die before writing any requirement.

**Why this priority**: "Reader produces" is the tutorial plan's contract; the
artifacts feed chapter 0.4 (journeys → testable requirements).

**Independent Test**: The exercise alone suffices to produce at least two journey
maps (one for the primary persona, one for an indirect/invisible persona) with
stages, an emotional arc judgment, and exactly one ★ per journey, self-checked
yes/no.

**Acceptance Scenarios**:

1. **Given** the exercise, **When** followed, **Then** the reader maps at least two
   journeys for personas from their 0.2 set — each with named stages, what the
   person does/feels per stage, and where it can fail — using Relay's journeys as
   worked examples.
2. **Given** the ★ discipline, **When** the reader marks moments, **Then** each
   journey has exactly one ★ with a stated reason ("if this stage fails, the rest
   never happens"), and at least one mapped journey belongs to a persona who never
   chooses the product.
3. **Given** the chapter's end, **Then** exactly one `CHECKPOINT` names the journey
   maps and ★ moments as required in hand before chapter 0.4, which turns them into
   requirements with IDs and verification methods.

---

### User Story 3 - The chapter takes its place in the bilingual series (Priority: P3)

As a reader of either language, chapter 0.3 appears as a published chapter everywhere
the series is navigable — both landings link it, 0.2's "next" affordance goes live in
both locales, 0.4 becomes the forthcoming next — and the chapter exists in Vietnamese
as a faithful translation in the series' established storytelling voice.

**Why this priority**: Structural integration and translation matter once the content
exists; the English chapter is independently valuable.

**Independent Test**: From either landing, reach 0.3 in ≤2 steps in that language;
0.2→0.3 forward links live in both locales; the language switcher maps 0.3↔0.3;
structural-parity checks pass.

**Acceptance Scenarios**:

1. **Given** the series manifest, **When** the chapter ships, **Then** 0.3 is
   published and marked translated; both landings list it as a link; 0.2's footers
   link forward to it; 0.3's footers show 0.2 as previous and 0.4 as forthcoming.
2. **Given** the Vietnamese chapter, **When** compared structurally to the English
   one, **Then** box counts per type match, the exercise structure is preserved, and
   the prose follows the established storytelling register and glossary (including
   the already-published Vietnamese title "Hành trình — nơi những sản phẩm gục ngã").
3. **Given** both versions, **Then** each declares its language and counterpart via
   the established mechanism, and no navigation surface anywhere is hand-edited.

---

### Edge Cases

- What happens for a reader who skipped 0.1/0.2? The chapter states its inputs early
  (the persona set) with pointers back, and remains skip-safe via the takeaways
  block.
- How do docs/03's ASCII diagrams (stage timelines, emotional arcs) translate to the
  chapter? The chapter may reproduce or restate them, but must remain readable
  without them — diagrams support the prose, never replace the argument; whatever
  form is chosen must render correctly in both locales and both themes.
- What happens to 0.2's content when 0.3 ships? Nothing — only manifest-driven
  navigation updates; 0.2's prose is immutable.
- Does the hosted-media product update (docs/01, recent commit) affect this chapter?
  docs/03 was not changed by that commit; the chapter reflects docs/03 as-is.
- Vietnamese title consistency: the manifest already carries the refreshed title
  "Hành trình — nơi những sản phẩm gục ngã" (user-approved retranslation); the
  chapter must use it, not re-translate.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Chapter 0.3 MUST exist as a published chapter titled "Journeys — where
  products die" at the series' canonical address pattern (path already reserved in
  the manifest: `/part-0/chapter-03/journeys-where-products-die`), rendered through
  the existing chapter shell.
- **FR-002**: The chapter MUST teach the four journeys from docs/03 — Mai
  (problem → production, eight stages), David (approval path), Priya (dispute
  resolution), Tuan (a message through a tunnel) — as derivations from the 0.2
  persona set, ordered by how directly each person touches the product, including
  why an infrastructure product maps journeys for people who never buy it.
- **FR-003**: The chapter MUST establish the ★-moment concept: the three mapped
  journeys each carry one stage that decides them (Mai: first message — nearly all
  abandonment happens before it; Priya: reconstructing what happened; Tuan: losing
  signal), and effort concentrates on ★ stages (docs/03's closing argument). The
  chapter MUST also name the exception explicitly: David's approval path carries no
  ★ — his power is a continuous veto ("he can stop the project at any point"), which
  is why his journey maps as gates rather than stages. The exception is a teaching
  point, not a gap (analysis A1, 2026-07-30).
- **FR-004**: The chapter MUST comply with the series format rules: 2,000–4,000
  words (canonical measure); first-person plural, present tense; ≥2 `WHY` boxes
  citing sources; 1 `SKIP AHEAD`; ≥1 forward reference (the journeys become the
  milestone test suites — the Tuan test, the Priya test); skip-safe takeaways;
  exactly one closing `CHECKPOINT`.
- **FR-005**: The chapter MUST include a reader exercise producing journey maps for
  the reader's own product: ≥2 journeys from their 0.2 persona set (one for the
  primary persona, one for an indirect/invisible persona), each with named stages,
  per-stage action/feeling/failure, and exactly one ★ with a stated reason; Relay's
  journeys as worked examples; yes/no self-checks.
- **FR-006**: 100% of journey facts MUST trace to docs/03 (with persona/positioning
  context from 0.1/0.2); no invented stages or moments.
- **FR-007**: The chapter MUST exist in Vietnamese as a faithful, structurally
  identical translation in the established storytelling register and glossary, using
  the manifest's existing Vietnamese title, at the parallel `/vi` address with
  correct language/counterpart metadata.
- **FR-008**: The series manifest MUST mark 0.3 published and translated with a
  validated reading-time estimate; all navigation surfaces MUST update automatically
  with zero hand-edited navigation.

### Key Entities

- **Chapter 0.3**: Third Part 0 chapter; source docs/03-journey-map.md; reader
  produces journey maps + ★ moments (docs/07 §3).
- **Journey map (as taught)**: A persona's path through the product as stages, each
  with actions, feelings, and failure modes; ordered by directness of contact.
- **★ moment**: The one stage per journey where the journey is decided — the
  concentration point for effort and, later, requirements.
- **Reader artifact**: The reader's own journey maps (≥2, one for an invisible
  persona) with one ★ each; prerequisite for chapter 0.4.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The chapter body is 2,000–4,000 words (canonical measure); box checks
  pass (WHY ≥2, SKIP AHEAD ≥1, forward reference ≥1, CHECKPOINT exactly 1, takeaways
  present).
- **SC-002**: 100% of journey facts trace to docs/03 — spot-checking any 5 claims
  finds their source stage/section.
- **SC-003**: A test reader can produce ≥2 journey maps with one ★ each (one journey
  for an invisible persona) using only the chapter, within the chapter's stated time
  budget.
- **SC-004**: From either locale's landing, 0.3 is reachable in ≤2 steps; 0.2→0.3
  forward navigation works in both locales; the switcher maps the two 0.3 versions
  to each other in 100% of attempts.
- **SC-005**: The Vietnamese version matches the English structurally (equal box
  counts per type, same section arc, exercise preserved) in the established voice
  and glossary.
- **SC-006**: Publishing 0.3 changes only the manifest entry and adds chapter files —
  every navigation surface updates by itself.

## Assumptions

- Scope is chapter 0.3 in both locales (bilingual by default — a series property
  since feature 004, per-chapter translation owned by the chapter's feature).
- docs/03-journey-map.md is the frozen content source (unchanged by the recent
  product-vision commit); docs/07 §3 fixes the title and reader artifacts.
- The manifest path, Vietnamese title, and reader-artifact labels for 0.3 already
  exist (features 004/005 + the approved retranslation); publishing is a
  status/translatedIn flip plus reading-time validation (currently 90 minutes).
- The existing shell, boxes, and i18n infrastructure are reused as-is; gaps are
  surfaced, not patched, inside this content feature.
- How to render the journey/emotional-arc structure (prose, lists, simple figures)
  is a planning decision bounded by the edge case above (readable without diagrams,
  correct in both locales/themes).
- Dong reviews the Vietnamese translation before committing; commits/pushes are
  Dong's.
