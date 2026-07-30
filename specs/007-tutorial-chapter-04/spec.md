# Feature Specification: Tutorial Chapter 0.4 — Requirements You Can Test

**Feature Branch**: `007-tutorial-chapter-04`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "chapter 0.4"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read chapter 0.4 and follow the derivation (Priority: P1)

As the tutorial's reader, I read chapter 0.4 — "Requirements you can test" — and watch
journey maps (0.3) being converted into a real requirements specification: stable
IDs that are never reused, priorities aligned to delivery phases, a verification
method on every requirement, shall-language that removes argument, and traceability
back to the personas and journeys that justify each line — so I understand why a
requirement without a test plan is an opinion.

**Why this priority**: The chapter's prose is the deliverable; it is Part 0's fourth
step (docs/07 §3: "Requirements you can test — an SRS slice with IDs, priorities,
verification methods") and the direct feeder of the SAD/ADR chapter (0.5).

**Independent Test**: A reader who finished 0.3 can answer: what makes a requirement
testable, what the verification methods are (test / demonstration / inspection /
analysis), how priorities map to phases, which single requirement the SRS calls its
most important (tenant isolation, Sev-0), and where ★ moments went (they became the
P1s) — without consulting docs/04.

**Acceptance Scenarios**:

1. **Given** the published chapter, **When** read end to end, **Then** it presents
   requirement-writing as a derivation from the 0.3 journey maps — showing at least
   two concrete journey-stage → requirement traces (e.g., Priya's reconstruction →
   tombstones/edit-history requirements; Tuan's tunnel → idempotency/backfill
   requirements) using real IDs from docs/04.
2. **Given** the chapter, **When** checked against the series format rules, **Then**
   it is 2,000–4,000 words (canonical measure), first-person plural present tense,
   with the box conventions (≥2 `WHY` citing docs/04, 1 `SKIP AHEAD`, ≥1 forward
   reference, skip-safe takeaways, exactly one closing `CHECKPOINT`).
3. **Given** the SRS's own machinery, **When** the reader finishes, **Then** they
   have seen: the anatomy of a requirement row (ID, shall-statement, priority,
   verification method); the ID discipline (stable, never reused); the priority
   ladder tied to the phased roadmap; the verification vocabulary (T/D/I/A); and the
   "single most important requirement" argument (FR-TEN-05, Sev-0, tested on every
   build).
4. **Given** the SRS's recent hosted-media update, **When** the chapter teaches
   change over time, **Then** it uses the FR-MED section as the live example: a
   reversed non-goal (0.1's lesson) entering the spec as *new* numbered requirements
   with their own verification methods — including FR-MED-09's explicit trace back
   to Priya's reconstruction — rather than edits to existing IDs.
5. **Given** the chapter's factual claims, **Then** 100% trace to docs/04 (current,
   media-inclusive revision) or earlier Part 0 artifacts — no invented requirements
   or IDs.

---

### User Story 2 - Produce the chapter's reader artifacts (Priority: P2)

As the reader, I finish the chapter by producing its assigned artifact — **an SRS
slice for my own product: 8–15 requirements with IDs, priorities, and verification
methods** (docs/07 §3) — derived from my journey maps, with my ★ moments becoming
the highest priorities.

**Why this priority**: "Reader produces" is the tutorial plan's contract; the slice
is the input chapter 0.5 tests architecture decisions against.

**Independent Test**: The exercise alone suffices to produce a requirement table
(8–15 rows) where every row has a stable ID, a shall-statement, a priority with a
phase rationale, and a T/D/I/A verification method — self-checked yes/no.

**Acceptance Scenarios**:

1. **Given** the exercise, **When** followed, **Then** the reader converts their two
   journey maps into 8–15 requirements using the docs/04 row format, with at least
   one requirement traced explicitly from each journey's ★ moment (and those carry
   the top priority).
2. **Given** the verification discipline, **When** the reader assigns methods,
   **Then** every requirement carries exactly one primary method (T/D/I/A) and the
   self-checks force the question "how would we know?" onto each row (e.g., a
   requirement no test could fail must be rewritten or cut).
3. **Given** the chapter's end, **Then** exactly one `CHECKPOINT` names the SRS
   slice as required in hand before chapter 0.5, which decides architecture against
   these requirements.

---

### User Story 3 - The chapter takes its place in the bilingual series (Priority: P3)

As a reader of either language, chapter 0.4 appears as a published chapter everywhere
the series is navigable — both landings link it, 0.3's "next" goes live in both
locales, 0.5 becomes the forthcoming next — and the chapter exists in Vietnamese as a
faithful translation in the established storytelling voice, using the manifest's
approved Vietnamese title.

**Why this priority**: Structural integration and translation matter once the content
exists.

**Independent Test**: From either landing, reach 0.4 in ≤2 steps in that language;
0.3→0.4 forward links live in both locales; the switcher maps 0.4↔0.4; structural
parity passes.

**Acceptance Scenarios**:

1. **Given** the series manifest, **When** the chapter ships, **Then** 0.4 is
   published and marked translated; both landings list it; 0.3's footers link
   forward; 0.4's footers show 0.3 previous and 0.5 forthcoming (non-link).
2. **Given** the Vietnamese chapter, **When** compared structurally, **Then** box
   counts per type match, the exercise structure is preserved, requirement IDs and
   shall-statement examples remain recognizably tied to the English SRS (IDs never
   translated), and the prose follows the established register and glossary.
3. **Given** both versions, **Then** language/counterpart metadata follows the
   established mechanism with zero hand-edited navigation.

---

### Edge Cases

- What happens for a reader who skipped earlier chapters? Inputs stated early (the
  journey maps and ★ moments) with pointers back; skip-safe takeaways at the end.
- How much of the 205-requirement SRS does the chapter reproduce? Selected specimen
  rows only — the chapter teaches the machinery, not the catalog; every quoted row
  uses its real ID verbatim (IDs are never invented or renumbered for prose
  convenience).
- How do requirement tables render? The chapter may use small markdown tables or
  fenced blocks for specimen rows, but must remain readable without them and render
  correctly in both locales and themes; requirement IDs and shall-keywords stay in
  English in the Vietnamese version (they are identifiers, not prose).
- What if docs/04 changes again mid-implementation? The chapter reflects docs/04 as
  of authoring; later SRS revisions enter via `REVISED` notes per the series'
  one-direction-of-authority rule.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Chapter 0.4 MUST exist as a published chapter titled "Requirements you
  can test" at the manifest's reserved path
  (`/part-0/chapter-04/requirements-you-can-test`), rendered through the existing
  chapter shell.
- **FR-002**: The chapter MUST teach the anatomy and discipline of the SRS from
  docs/04: stable never-reused IDs; shall-statements; the P1–P5 priority ladder
  aligned to the phased roadmap; the four verification methods (T/D/I/A); and
  grouped requirement families — presented as a derivation from the 0.3 journey
  maps, with at least two explicit journey→requirement traces using real IDs.
- **FR-003**: The chapter MUST make the "testable or it's an opinion" argument
  concretely, including the SRS's own centerpiece: FR-TEN-05 (tenant isolation) as
  the single most important requirement, Sev-0 on violation, verified by an
  automated cross-tenant suite on every build.
- **FR-004**: The chapter MUST use the hosted-media section (FR-MED, §4.14) as the
  live example of a spec absorbing change: 0.1's reversed non-goal arriving as new
  numbered requirements with verification methods, and FR-MED-09's explicit trace to
  Priya's reconstruction as journeys→requirements working in real time.
- **FR-005**: The chapter MUST comply with the series format rules: 2,000–4,000
  words (canonical measure); first-person plural present tense; ≥2 `WHY` boxes
  citing docs/04; 1 `SKIP AHEAD`; ≥1 forward reference (the requirements become
  Part 2+'s implementation chapters and the milestone tests); skip-safe takeaways;
  exactly one closing `CHECKPOINT`.
- **FR-006**: The chapter MUST include a reader exercise producing an SRS slice:
  8–15 requirements derived from the reader's journey maps, each with a stable ID,
  a shall-statement, a priority with phase rationale, and one T/D/I/A verification
  method; ★ moments MUST surface as the top priorities; worked examples from
  docs/04; yes/no self-checks including the "what test could fail this?" probe.
- **FR-007**: 100% of quoted requirements MUST be faithful to the current
  (media-inclusive) docs/04, with "verbatim" defined precisely (analysis A1,
  2026-07-30): the **ID, shall-statement text, priority, and verification-method
  values** match the source exactly — the statement text must be greppable in
  docs/04 — while table decoration and layout separators are free, so re-rendering
  a row outside its source table is permitted but altering its words is not. No
  invented IDs.
- **FR-008**: The chapter MUST exist in Vietnamese as a faithful, structurally
  identical translation in the established register and glossary, using the
  manifest's approved title ("Những yêu cầu bạn có thể kiểm chứng"); requirement IDs
  and shall-keywords remain in English; parallel `/vi` address with correct
  language/counterpart metadata.
- **FR-009**: The series manifest MUST mark 0.4 published and translated with a
  validated reading-time estimate; all navigation updates automatically with zero
  hand-edited navigation.

### Key Entities

- **Chapter 0.4**: Fourth Part 0 chapter; source docs/04-srs.md (current revision);
  reader produces an SRS slice (docs/07 §3).
- **Requirement (as taught)**: A row with stable ID, shall-statement, priority tied
  to a phase, and a verification method — traceable to a persona/journey.
- **Verification method**: T (automated test), D (demonstration), I (inspection),
  A (analysis) — the answer to "how would we know?".
- **Reader artifact**: The reader's SRS slice (8–15 rows); prerequisite for chapter
  0.5.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The chapter body is 2,000–4,000 words (canonical measure); box checks
  pass (WHY ≥2, SKIP AHEAD ≥1, forward reference ≥1, CHECKPOINT exactly 1, takeaways
  present).
- **SC-002**: 100% of quoted requirement IDs and row contents match the current
  docs/04 — spot-checking any 5 quoted rows finds them verbatim.
- **SC-003**: A test reader can produce an 8–15-row SRS slice with complete rows
  (ID, shall, priority+rationale, method) using only the chapter, within the
  chapter's stated time budget.
- **SC-004**: From either locale's landing, 0.4 is reachable in ≤2 steps; 0.3→0.4
  navigation works in both locales; the switcher maps the two versions in 100% of
  attempts.
- **SC-005**: The Vietnamese version matches the English structurally (box counts,
  arc, exercise) in the established voice, with all requirement IDs preserved in
  English.
- **SC-006**: Publishing 0.4 changes only the manifest entry and adds chapter
  files — every navigation surface updates by itself.

## Assumptions

- Scope is chapter 0.4 in both locales (bilingual by default — series property).
- docs/04-srs.md **as updated by the hosted-media commit** is the frozen content
  source for this feature; docs/07 §3 fixes title and reader artifact. The media
  update is treated as an asset (FR-004), not a complication.
- The manifest path, Vietnamese title ("Những yêu cầu bạn có thể kiểm chứng"), and
  reader-artifact labels already exist; publishing is a status/translatedIn flip
  plus reading-time validation (currently 100 minutes).
- Existing shell/boxes/i18n reused as-is; gaps surfaced, not patched.
- Specimen-row rendering form (small tables vs. fenced blocks) is a planning
  decision bounded by the edge case (readable without them, both locales/themes,
  IDs verbatim).
- Dong reviews the Vietnamese translation before committing; commits/pushes are
  Dong's.
