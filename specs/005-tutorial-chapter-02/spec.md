# Feature Specification: Tutorial Chapter 0.2 — Four People Who Will Judge Us

**Feature Branch**: `005-tutorial-chapter-02`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "chapter 0.2"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read chapter 0.2 and follow the derivation (Priority: P1)

As the tutorial's reader, I read chapter 0.2 — "Four people who will judge us" — and
watch personas being *derived* from chapter 0.1's artifacts (the positioning statement
and non-goals): who the product's people are, why they are ordered by influence rather
than by headcount, and why the person who benefits most (the end user) never knows the
product exists — so that when requirements appear in chapter 0.4, I already know whose
pain each one traces to.

**Why this priority**: The chapter's prose is the deliverable; it is the second step
of Part 0's spine (docs/07 §3: "how personas generate requirements").

**Independent Test**: A reader who finished 0.1 can read this chapter and correctly
answer: who the four people are, which one is the primary persona and why, which one
is the buyer, and why the end user is a *constraint* rather than a customer — without
consulting docs/02.

**Acceptance Scenarios**:

1. **Given** the published chapter, **When** read end to end, **Then** it presents the
   four personas from docs/02 (integrating developer, engineering lead, support &
   operations, end user) as a derivation from the 0.1 artifacts — showing *why* each
   exists — not as four pasted profile cards.
2. **Given** the chapter, **When** checked against the series format rules (docs/07
   §2), **Then** it is 2,000–4,000 words, first-person plural present tense, and uses
   the box conventions (at minimum `WHY` boxes citing docs/02, one `SKIP AHEAD`, and
   forward references).
3. **Given** the docs/02 teaching that the user, the buyer, and the beneficiary are
   three different people, **When** the reader finishes, **Then** the chapter has made
   the "invisible end user" argument concretely (the end user feels every defect but
   never sees the product) and tied it to at least one future engineering consequence.
4. **Given** the chapter, **When** its factual claims are checked, **Then** 100% trace
   to docs/02 (persona details) or chapter 0.1/docs/01 (positioning context) — no
   invented personas or attributes.

---

### User Story 2 - Produce the chapter's reader artifacts (Priority: P2)

As the reader, I finish the chapter by producing its assigned artifact — **a persona
set for my own product, including the invisible end user** (docs/07 §3: "Reader
produces") — following worked guidance, so I have practiced deriving people from
positioning rather than inventing demographic fiction.

**Why this priority**: "Reader produces" is the tutorial plan's contract for every
Part 0 chapter; without the exercise it is an essay.

**Independent Test**: The exercise section alone is sufficient for a reader to produce
a persona set (at least three personas including one invisible/indirect persona) and
self-check it with yes/no criteria.

**Acceptance Scenarios**:

1. **Given** the exercise, **When** followed, **Then** the reader produces at least
   three personas for their own product, each with: role in the product (not job
   title alone), a priority/influence ordering with reasons, goals, frustrations, and
   what wins/loses them — using Relay's set as the worked example.
2. **Given** the exercise, **When** the reader checks their set, **Then** at least one
   persona is the invisible/indirect kind (benefits or suffers without ever choosing
   the product), and the self-checks are answerable yes/no (e.g., "does your ordering
   name a reason, or is it just org-chart seniority?").
3. **Given** the chapter's end, **Then** exactly one `CHECKPOINT` block names the
   persona set as required in hand before chapter 0.3, which derives journeys from
   these personas.

---

### User Story 3 - The chapter takes its place in the bilingual series (Priority: P3)

As a reader of either language, chapter 0.2 appears as a published chapter everywhere
the series is navigable — the landing lists it as a link (both locales), chapter 0.1's
"next" affordance goes live, and the chapter exists in Vietnamese as a faithful
translation in the series' established storytelling voice — so the bilingual structure
built in feature 004 keeps its promise with the first post-i18n chapter.

**Why this priority**: Structural integration and translation matter once the content
exists; the English chapter is independently valuable.

**Independent Test**: From either landing, reach chapter 0.2 in ≤2 steps in that
language; 0.1's footer links forward to 0.2 in both locales; the Vietnamese version
passes the same structural-parity checks as chapter 0.1's translation did.

**Acceptance Scenarios**:

1. **Given** the series manifest, **When** the chapter ships, **Then** 0.2 is
   `published` (and marked translated), both landings list it as a link, and 0.3
   becomes the next forthcoming chapter shown in 0.2's footer.
2. **Given** chapter 0.1 (either locale), **When** the reader reaches its footer,
   **Then** the "next" card is now a live link to 0.2 in the same locale.
3. **Given** the Vietnamese chapter, **When** compared structurally to the English
   one, **Then** box counts per type match, the exercise structure is preserved, and
   the prose follows the established storytelling register (per the voice set in
   chapter 0.1's approved translation).
4. **Given** both versions, **Then** each declares its language and its counterpart
   (same mechanism as existing pages), and the language switcher maps 0.2 ↔ 0.2.

---

### Edge Cases

- What happens for a reader who skipped chapter 0.1 (the "Part 0 bounce")? The chapter
  must state its inputs early (the positioning statement and non-goals) with a pointer
  back to 0.1, and remain skip-safe: a compact takeaways block at the end.
- What happens to 0.1's content when 0.2 ships? Nothing — 0.1 is only touched by
  automatic manifest-driven navigation (its footer next-card); its prose is immutable
  per the series' one-direction-of-authority rule.
- How does the chapter handle docs/02's Vietnamese names (Mai, Tuan) in the Vietnamese
  translation? Names stay as-is; the translation must not localize or alter persona
  identities.
- What if the recent product update (hosted media, docs/01) touches persona content?
  docs/02 was not changed by that commit; the chapter reflects docs/02 as-is, and any
  media-related persona nuance belongs to a future docs/02 revision, not to this
  chapter's invention.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Chapter 0.2 MUST exist as a published chapter titled "Four people who
  will judge us", at the canonical address pattern established for the series
  (`/part-0/chapter-02/<slug>` with slug = kebab-case main clause), rendered through
  the existing chapter shell with series identity and navigation.
- **FR-002**: The chapter MUST teach the derivation of Relay's four personas from
  docs/02 — Mai (integrating developer, primary), David (engineering lead,
  buyer/blocker), Priya (support & operations, daily operator), Tuan (end user,
  constraint) — including the influence ordering and its reasons, presented as
  reasoning the reader watches unfold from chapter 0.1's artifacts.
- **FR-003**: The chapter MUST make the "invisible end user" argument explicitly: the
  person who benefits never knows the product exists, feels every defect, and
  therefore acts as a constraint on engineering decisions — tied to at least one
  concrete future consequence (e.g., the reconnection/ordering machinery of Part 2).
- **FR-004**: The chapter MUST comply with the series format rules: 2,000–4,000 words
  (measured per the established procedure — all reader-facing text including boxes
  and exercise); first-person plural, present tense; ≥2 `WHY` boxes citing sources;
  1 `SKIP AHEAD`; ≥1 forward reference to a later part; a skip-safe takeaways block;
  exactly one closing `CHECKPOINT`.
- **FR-005**: The chapter MUST include a reader exercise producing a persona set for
  the reader's own product: ≥3 personas, each with role-in-product, influence
  ordering with reasons, goals, frustrations, and win/lose conditions; at least one
  invisible/indirect persona; Relay's personas as the worked example; yes/no
  self-checks.
- **FR-006**: 100% of factual persona claims MUST trace to docs/02 (with positioning
  context from docs/01/chapter 0.1); no invented attributes.
- **FR-007**: The chapter MUST exist in Vietnamese as a faithful, structurally
  identical translation following the series' established storytelling register and
  terminology conventions (technical terms in English; established glossary from
  chapter 0.1 reused), at the parallel `/vi` address, with correct language
  declaration and counterpart metadata in both directions.
- **FR-008**: The series manifest MUST mark 0.2 published and translated, with its
  actual reading-time estimate; all navigation (both landings, 0.1's footers, 0.2's
  footers showing 0.3 forthcoming) MUST follow automatically with no hand-edited
  navigation anywhere.

### Key Entities

- **Chapter 0.2**: The second Part 0 chapter; source docs/02-personas.md; reader
  produces a persona set including the invisible end user (docs/07 §3).
- **Persona (as taught)**: A person with a role *in the product* (user, buyer,
  operator, constraint), an influence ordering with reasons, goals, frustrations, and
  win/lose conditions — derived from positioning, not demographics.
- **Reader artifact**: The reader's own persona set (≥3, incl. one invisible persona);
  owned by the reader, prerequisite for chapter 0.3.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The chapter body is 2,000–4,000 words by the established measurement;
  box-presence checks pass (WHY ≥2, SKIP AHEAD ≥1, forward reference ≥1, CHECKPOINT
  exactly 1, takeaways present).
- **SC-002**: 100% of persona facts trace to docs/02; spot-checking any 5 claims finds
  their source section.
- **SC-003**: A test reader can produce their persona set (≥3 personas, one invisible)
  using only the chapter, within the chapter's stated time budget.
- **SC-004**: From either locale's landing, chapter 0.2 is reachable in ≤2 steps;
  0.1 → 0.2 forward navigation works in both locales; the language switcher maps the
  two 0.2 versions to each other in 100% of attempts.
- **SC-005**: The Vietnamese version matches the English structurally (equal box
  counts per type; same section arc; exercise components preserved) and uses the
  established voice and glossary.
- **SC-006**: Zero hand-edited navigation: publishing 0.2 changes only the manifest
  entry and adds chapter files; every navigation surface updates by itself.

## Assumptions

- Scope is chapter 0.2 in both locales (English authored from docs/02; Vietnamese
  translated in the storytelling register established by the approved 0.1
  translation). Bilingualism is now a series property (feature 004), so a new chapter
  ships bilingual by default.
- docs/02-personas.md is the frozen content source (unchanged by the recent
  product-vision commit); docs/07 §3 fixes the title and reader artifact.
- The slug follows the established rule (kebab-case of the title's main clause):
  planning confirms the exact string; the manifest already reserves the path.
- The existing shell, boxes, i18n, and manifest infrastructure (features 002–004) is
  reused as-is; no new components or plumbing are expected. If a gap appears, it is
  surfaced rather than worked around.
- Reading-time estimate (~75 minutes) from the manifest is validated against the
  actual chapter during implementation and corrected if needed.
- Dong reviews the Vietnamese translation quality before committing (standing
  practice from feature 004); commits/pushes are Dong's.
