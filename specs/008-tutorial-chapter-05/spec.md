# Feature Specification: Tutorial Chapter 0.5 — Deciding Out Loud

**Feature Branch**: `008-tutorial-chapter-05`

**Created**: 2026-07-30

**Status**: Draft

**Input**: User description: "chapter 0.5"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read chapter 0.5 and follow the derivation (Priority: P1)

As the tutorial's reader, I read chapter 0.5 — "Deciding out loud — the SAD and the
ADR habit" — and watch requirements (0.4) being converted into defensible
architecture decisions: the handful of architectural drivers distilled from 224
requirements, and the ADR form that records each choice with its drivers, its
rejected alternatives, and its reversal condition — so I understand that an
architecture is not a diagram but a set of decisions you can argue with.

**Why this priority**: The chapter's prose is the deliverable; it is Part 0's final
step (docs/07 §3: "Deciding out loud — drivers table; two ADRs written from
scratch") and the gateway to the code parts.

**Independent Test**: A reader who finished 0.4 can answer: what an architectural
driver is and why 224 requirements distill to a handful, what the parts of an ADR
are (status, drivers, decision, trade-offs, rejected alternatives, reversal
condition), why rejected alternatives are recorded, and what "attack the driver, not
the choice" means — without consulting docs/05/06.

**Acceptance Scenarios**:

1. **Given** the published chapter, **When** read end to end, **Then** it presents
   the drivers table (docs/05 §2, D1–D8) as a distillation of the SRS — showing at
   least two driver derivations explicitly (e.g., "no acknowledged message may be
   lost" from FR-MSG-05/06; "one engineer must be able to run and reason about it"
   as the non-obvious portfolio driver) — and the ADR form as the unit of decision
   record.
2. **Given** the chapter, **When** checked against the series format rules, **Then**
   it is 2,000–4,000 words (canonical measure), first-person plural present tense,
   with the box conventions (≥2 `WHY` citing docs/05/06, 1 `SKIP AHEAD`, ≥1 forward
   reference, skip-safe takeaways, exactly one closing `CHECKPOINT`).
3. **Given** the ADR discipline, **When** the reader finishes, **Then** they have
   walked at least one real ADR in full anatomy (a strong candidate: ADR-03,
   per-channel sequences — the decision that resolves an SRS open question) and seen
   the two-document split (terse ADR in the SAD; full deep-dive in docs/06),
   including the rule that ADRs are immutable once accepted and superseding requires
   a new ADR.
4. **Given** the recent product update, **When** the chapter teaches decisions
   absorbing change, **Then** it uses ADR-13 ("media bytes never transit Relay
   compute") and ADR-14 as the live example (both, per FR-004) — the 0.1 non-goal reversal arriving
   in architecture as *new* ADRs defending the design that answered the original
   objections — closing the 0.1→0.3→0.4→0.5 paperwork chain.
5. **Given** the chapter's factual claims, **Then** 100% trace to docs/05/06
   (current revisions) or earlier Part 0 artifacts; ADR numbers, driver IDs, and
   decision content are never invented.

---

### User Story 2 - Produce the chapter's reader artifacts (Priority: P2)

As the reader, I finish Part 0 by producing its final artifacts — **a drivers table
distilled from my SRS slice, and two ADRs written from scratch** (docs/07 §3) — so I
have practiced the full paperwork chain end to end before any code exists.

**Why this priority**: "Reader produces" is the tutorial plan's contract; these
artifacts complete the reader's Part 0 portfolio (positioning statement, non-goals,
personas, journeys, SRS slice, drivers, ADRs).

**Independent Test**: The exercise alone suffices to produce (a) a drivers table of
3–6 drivers, each tracing to specific requirements from the reader's 0.4 slice with
an architectural consequence, and (b) two complete ADRs — each with status,
drivers, decision, trade-offs accepted, at least two rejected alternatives with
reasons, and a reversal condition — self-checked yes/no.

**Acceptance Scenarios**:

1. **Given** the exercise, **When** followed, **Then** the reader distills 3–6
   drivers from their 8–15 requirements (not one driver per requirement — the
   distillation is the skill), each with a stated architectural consequence, using
   Relay's D1–D8 as the worked example.
2. **Given** the ADR exercise, **When** completed, **Then** each of the two ADRs
   names the drivers it serves, records ≥2 rejected alternatives *with the reason
   for rejection*, and states a reversal condition ("revisit when…") — the
   self-checks force each element (e.g., "could a new teammate reconstruct why you
   didn't choose the obvious alternative?").
3. **Given** the chapter's end, **Then** exactly one `CHECKPOINT` closes Part 0:
   naming the complete artifact portfolio the reader now holds and pointing forward
   to Part 1, where the building begins.

---

### User Story 3 - The chapter completes Part 0 in the bilingual series (Priority: P3)

As a reader of either language, chapter 0.5 appears as a published chapter
everywhere the series is navigable — and with it **Part 0 becomes fully published**:
both landings show all five chapters as links, 0.4's "next" goes live in both
locales, and 0.5's footer gracefully handles being the last published chapter (no
next-chapter card, since no further chapters exist in the manifest yet).

**Why this priority**: Structural integration matters once content exists; the
Part 0 completion state is this feature's unique navigation situation.

**Independent Test**: From either landing, reach 0.5 in ≤2 steps; 0.4→0.5 forward
links live in both locales; 0.5's footer shows 0.4 as previous and renders correctly
with no next chapter; the switcher maps 0.5↔0.5; structural parity passes.

**Acceptance Scenarios**:

1. **Given** the series manifest, **When** the chapter ships, **Then** 0.5 is
   published and marked translated; both landings list all five Part 0 chapters as
   links with zero forthcoming badges in Part 0.
2. **Given** 0.5's footer (both locales), **Then** it shows 0.4 as previous, no next
   card (the manifest has no chapter after 0.5), and the back-to-contents link —
   rendering cleanly, not brokenly, in this end-of-series state.
3. **Given** the Vietnamese chapter, **Then** box counts match, the exercise
   structure is preserved, ADR/driver identifiers stay in English, and the prose
   follows the established register using the manifest's approved title
   ("Quyết định thành tiếng — bản SAD và thói quen viết ADR").

---

### Edge Cases

- What happens for a reader who skipped earlier chapters? Inputs stated early (the
  SRS slice) with pointers back; skip-safe takeaways.
- How does the last-chapter footer behave? The shell already renders a missing next
  chapter as an empty slot (nextChapter returns nothing beyond 0.5) — this feature
  must *verify* that end-state renders acceptably in both locales, not assume it;
  if it renders poorly, that is surfaced as an infrastructure gap, not silently
  patched here.
- How much of docs/05/06 does the chapter cover? The drivers table and the ADR
  discipline with 1–2 specimen ADRs — not the service views, deployment topology,
  or all 14 ADRs; the SAD's descriptive sections belong to later parts where the
  systems get built.
- Specimen rendering: fenced blocks (≤3), verbatim per the feature-007 definition
  (words exact, layout separators free); no pipe tables (no GFM); IDs (ADR-03,
  D1–D8) never invented; readable without fences; both locales/themes.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Chapter 0.5 MUST exist as a published chapter titled "Deciding out
  loud — the SAD and the ADR habit" at the manifest's reserved path
  (`/part-0/chapter-05/deciding-out-loud`), rendered through the existing shell.
- **FR-002**: The chapter MUST teach the drivers discipline from docs/05 §2: a
  handful of drivers (D1–D8) distilled from 224 requirements, each with an
  architectural consequence; at least two derivations shown explicitly, including
  D8 ("one engineer must be able to run and reason about it") as the driver that
  isn't a requirement at all.
- **FR-003**: The chapter MUST teach the ADR form and its discipline: status,
  drivers, decision, accepted trade-offs, rejected alternatives with reasons, and
  reversal condition; the terse-ADR/deep-dive split between docs/05 §9 and docs/06;
  immutability once accepted (superseding = new ADR); and the review rule "attack
  the driver, not the choice" — walking at least one real ADR in full anatomy.
- **FR-004**: The chapter MUST use ADR-13/ADR-14 as the live change example: the
  0.1 media reversal arriving in architecture as new ADRs whose decisions answer
  the original exclusion's stated reasons — explicitly closing the
  0.1→0.3→0.4→0.5 chain that previous chapters built.
- **FR-005**: The chapter MUST comply with the series format rules: 2,000–4,000
  words (canonical); first-person plural present; ≥2 `WHY` boxes; 1 `SKIP AHEAD`;
  ≥1 forward reference (the ADRs become Part 1–7's implementation reality — e.g.,
  ADR-03 is chapter 2.2's row lock); skip-safe takeaways; exactly one closing
  `CHECKPOINT` that closes Part 0 and points to Part 1.
- **FR-006**: The chapter MUST include the reader exercise producing (a) a 3–6-row
  drivers table distilled from the reader's SRS slice, each driver with source
  requirement IDs and an architectural consequence, and (b) two from-scratch ADRs
  with all anatomy elements including ≥2 rejected alternatives with reasons and a
  reversal condition; Relay specimens as worked examples; yes/no self-checks.
- **FR-007**: 100% of quoted drivers, ADR numbers, and decision content MUST be
  faithful to the current docs/05/06 per the established verbatim definition (words
  exact, layout free); no invented identifiers.
- **FR-008**: The chapter MUST exist in Vietnamese as a faithful, structurally
  identical translation in the established register and glossary, using the
  manifest's approved title; ADR/driver identifiers and specimen fences stay in
  English with Vietnamese glosses (the feature-007 pattern).
- **FR-009**: The series manifest MUST mark 0.5 published and translated with a
  validated reading-time estimate; all navigation updates automatically; the
  last-chapter footer state MUST be verified to render acceptably in both locales.

### Key Entities

- **Chapter 0.5**: Final Part 0 chapter; sources docs/05-sad.md + docs/06-adr-deep-dives.md
  (current revisions); reader produces a drivers table + two ADRs (docs/07 §3).
- **Architectural driver (as taught)**: One of the few requirements that actually
  shapes the architecture, with its consequence; everything else is implementation.
- **ADR (as taught)**: An immutable decision record — status, drivers, decision,
  trade-offs, rejected alternatives with reasons, reversal condition.
- **Reader artifact**: The drivers table (3–6 rows) + two ADRs; completes the Part 0
  portfolio.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The chapter body is 2,000–4,000 words (canonical); box checks pass
  (WHY ≥2, SKIP AHEAD ≥1, forward reference ≥1, CHECKPOINT exactly 1, takeaways
  present).
- **SC-002**: 100% of quoted driver/ADR content is faithful to current docs/05/06 —
  spot-checking any 5 quoted items finds them; an ID detector finds no invented
  ADR-nn or D-n identifiers.
- **SC-003**: A test reader can produce the drivers table and two complete ADRs
  using only the chapter, within the chapter's stated time budget.
- **SC-004**: From either locale's landing, 0.5 is reachable in ≤2 steps; 0.4→0.5
  navigation works in both locales; the switcher maps the versions in 100% of
  attempts; the last-chapter footer renders acceptably (previous card + contents
  link, no broken next slot) in both locales.
- **SC-005**: Part 0 completion is visible: both landings show five linked chapters
  and zero forthcoming badges within Part 0.
- **SC-006**: Publishing 0.5 changes only the manifest entry and adds chapter
  files — every navigation surface updates by itself.

## Assumptions

- Scope is chapter 0.5 in both locales (bilingual by default — series property).
- docs/05-sad.md and docs/06-adr-deep-dives.md **as updated by the media commit**
  (including ADR-13/14) are the frozen sources; docs/07 §3 fixes title and reader
  artifacts.
- The manifest path, Vietnamese title, and reader-artifact labels already exist
  (including the approved retranslations); publishing is a status/translatedIn flip
  plus reading-time validation (currently 110 minutes).
- The feature-007 conventions carry forward: verbatim definition (words exact,
  layout free), English-fence-with-Vietnamese-gloss pattern, ≤3 fences, no pipe
  tables, identifier discipline in the Vietnamese file.
- Existing shell/boxes/i18n reused as-is; the last-chapter footer state is verified
  and any gap surfaced, not patched (spec edge case).
- Dong reviews the Vietnamese translation before committing; commits/pushes are
  Dong's.
