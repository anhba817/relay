# Feature Specification: Tutorial Chapter 0.1 — From App to Infrastructure

**Feature Branch**: `002-tutorial-chapter-01`

**Created**: 2026-07-29

**Status**: Draft

**Input**: User description: "Start Part 0 chapter 0.1"

## Clarifications

### Session 2026-07-29

- Q: What is the chapter URL scheme in the browser? → A: `/part-<n>/chapter-<nn>/<slug>` with no site-wide prefix; the series landing (entry point) remains at the site root `/`. (Supersedes an earlier `/relay-chat-service-tutorial/...` prefix proposal from the same session.)
- Q: What slug does chapter 0.1 use (and what is the slug rule)? → A: `from-app-to-infrastructure` — kebab-case of the chapter title's main clause, subtitle dropped; future chapters follow the same rule.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read chapter 0.1 and follow the derivation (Priority: P1)

As the tutorial's reader (Mai — a mid-level full-stack developer, per docs/02), I read
chapter 0.1, "From app to infrastructure — finding the real product", and follow the
derivation of how a naïve chat-app idea becomes an infrastructure product: why the
two-week feature turns into a six-month system, who the alternatives serve, and where
the market gap is — so that every later architectural decision in the series has a
product-level "why" I actually watched happen.

**Why this priority**: The chapter's prose is the deliverable. Part 0's design note
(docs/07 §3) says this part is what most distinguishes the series; 0.1 is its opening
argument.

**Independent Test**: A reader with no prior exposure to the project can read the
chapter start to finish and correctly answer: what Relay is, what it is not, and why
building "just a chat feature" fails — without consulting any other document.

**Acceptance Scenarios**:

1. **Given** the published chapter, **When** a reader finishes it, **Then** they have
   encountered the derivation from "chat app idea" to "chat infrastructure product",
   including the cost-of-the-second-year argument and the incumbent/transport gap
   analysis from the vision document (docs/01 §2).
2. **Given** the chapter text, **When** checked against the tutorial format rules
   (docs/07 §2), **Then** it is 2,000–4,000 words, written in first-person plural
   present tense, and uses the recurring box conventions (at minimum `WHY` and
   forward-reference callouts appropriate to a prose chapter).
3. **Given** Part 0's skip-risk mitigation (docs/07 §3 design note), **When** the
   reader scans the chapter, **Then** at least one forward reference of the form "this
   becomes a test/decision in Part N" is present, tying the prose to future code.

---

### User Story 2 - Produce the chapter's reader artifacts (Priority: P2)

As the reader, I finish chapter 0.1 by producing the two artifacts the tutorial plan
assigns to it — a **positioning statement** and a **non-goals list** for the product I
am about to build — following worked guidance in the chapter, so that I have practiced
the specification skill rather than only read about it.

**Why this priority**: "Reader produces" is the tutorial plan's contract for every
Part 0 chapter (docs/07 §3, chapter table). Without the exercise, 0.1 is an essay, not
a tutorial chapter.

**Independent Test**: The chapter contains an exercise section with enough scaffolding
(template, worked example drawn from Relay's own positioning statement, and evaluation
criteria) that a reader can produce both artifacts and self-check them.

**Acceptance Scenarios**:

1. **Given** the chapter's exercise section, **When** the reader follows it, **Then**
   they produce a positioning statement in the named-template form used by the vision
   document (for/who/the-product-is/that/unlike/our-product) and a non-goals list of
   at least three entries, each with a reason.
2. **Given** the completed artifacts, **When** the reader applies the chapter's
   self-check criteria, **Then** each criterion is stated concretely enough to be
   answered yes/no (e.g., "does every non-goal name a real product you are choosing
   not to be?").
3. **Given** the chapter's `CHECKPOINT` convention, **When** the reader reaches the
   chapter end, **Then** a checkpoint block states what they must have in hand before
   starting chapter 0.2.

---

### User Story 3 - Navigate to and within the chapter (Priority: P3)

As the reader, I can discover chapter 0.1 from the tutorial's entry point (as the
first chapter of Part 0), see where I am in the series, and move on to chapter 0.2
when it exists — so the chapter reads as the opening of a series rather than a
stranded document.

**Why this priority**: Discoverability matters for the published series but the
chapter content is valuable standalone; series navigation will grow with each chapter.

**Independent Test**: From the tutorial's entry point, a reader can reach chapter 0.1
in at most two navigation steps, and the chapter displays its identity (Part 0,
chapter 0.1, title) and its place in the Part 0 sequence.

**Acceptance Scenarios**:

1. **Given** the tutorial entry point, **When** the reader looks for the beginning of
   the series, **Then** Part 0 / chapter 0.1 is reachable and labeled with its title.
2. **Given** the chapter, **When** the reader reaches its end, **Then** a pointer to
   the next chapter (0.2 — "Four people who will judge us") exists, marked as
   forthcoming if not yet written.

---

### Edge Cases

- What happens when the reader skips Part 0 entirely (the documented "Part 0 bounce"
  risk, docs/07 §7 T2)? Chapter 0.1 must still be skip-safe: its essential conclusions
  must be recoverable later, so the chapter states its takeaways compactly at the end.
- How does the chapter handle a reader who has already read the vision document
  (docs/01)? The chapter is a derivation of that document, not a copy — it must show
  how the positioning was arrived at, so it adds value even for that reader.
- What happens when later chapters revise Part 0 claims? The chapter follows the
  tutorial's one-direction-of-authority rule (docs/07 §6): if a revision lands, the
  chapter gets a visible `REVISED` note rather than silent edits.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Chapter 0.1 MUST exist as a readable, published artifact titled "From
  app to infrastructure — finding the real product", identified as Part 0, chapter 1
  of the *Building Relay* series. Its home is the **relay-tutorial application**:
  chapter content is authored as prose source within that repository and rendered as
  a page of the tutorial site (user decision, 2026-07-29 — supersedes docs/07 §2's
  original chapters-beside-code monorepo layout for content location; all other
  format rules from docs/07 §2 still apply).
- **FR-002**: The chapter MUST teach the derivation from chat-app idea to
  infrastructure product using the vision document (docs/01) as its source: the
  underestimation table (§2), the build/incumbent/transport alternatives analysis, and
  the wedge-market argument (§4) — presented as reasoning the reader watches unfold,
  not as conclusions pasted in.
- **FR-003**: The chapter MUST include a reader exercise producing (a) a positioning
  statement in the for/who/that/unlike template and (b) a non-goals list with at least
  three reasoned entries, with a worked example (Relay's own) and yes/no self-check
  criteria.
- **FR-004**: The chapter MUST comply with the series format rules (docs/07 §2):
  2,000–4,000 words; first-person plural, present tense; recurring boxes used where
  applicable (`WHY` linking claims to the vision document; `CHECKPOINT` at the end;
  `SKIP AHEAD` guidance since Part 0 is skippable by design).
- **FR-005**: The chapter MUST contain at least one explicit forward reference tying a
  Part 0 claim to a concrete later artifact (e.g., "this non-goal becomes a rejected
  requirement in the SRS; you will meet it again as FR-MSG-14 in Part 2").
- **FR-006**: The chapter MUST end with a compact takeaways block (the skip-safe
  summary seed) stating the chapter's conclusions in a form usable by a reader who
  reads nothing else in Part 0.
- **FR-007**: The chapter MUST be reachable from the tutorial's entry point, display
  its series identity (part, chapter number, title), and point to the next chapter
  (marked forthcoming if 0.2 does not yet exist). Chapter browser addresses MUST
  follow the canonical pattern `/part-<n>/chapter-<nn>/<slug>` with no additional
  site prefix — chapter 0.1 is `/part-0/chapter-01/from-app-to-infrastructure` — and
  the entry point remains at the site root (clarification, 2026-07-29).
- **FR-008**: The feature MUST deliver, alongside the chapter content, the **minimal
  reusable series reading experience** (user decision, 2026-07-29): a tutorial landing
  view acting as the series table of contents (showing at least Part 0 and its five
  chapters, with unwritten chapters marked forthcoming), a chapter reading layout that
  displays series identity and next/previous affordances, and visually distinct
  styling for the recurring box conventions (`WHY`, `TRAP`, `CHECKPOINT`,
  `SKIP AHEAD`, `REVISED`, forward references) — all consistent with the established
  Violet Bloom theme in both light and dark modes, and reusable by every subsequent
  chapter without per-chapter styling work.

### Key Entities

- **Chapter**: A unit of the tutorial series with identity (part number, chapter
  number, title), a URL slug (kebab-case of the title's main clause, subtitle
  dropped — clarification 2026-07-29), body prose, recurring boxes (`WHY`,
  `CHECKPOINT`, `SKIP AHEAD`, forward references), an exercise section, and a
  takeaways block.
- **Reader artifact**: The output the reader produces from a chapter's exercise — for
  0.1: a positioning statement and a non-goals list. Owned by the reader, not stored
  by the tutorial.
- **Series structure**: The part/chapter hierarchy from docs/07 §3 that gives each
  chapter its place and its next/previous relationships.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The chapter body is between 2,000 and 4,000 words (tutorial format
  rule), verified by word count. The count covers all reader-facing chapter text —
  including box contents and the exercise section — and the feature's quickstart
  defines the canonical measurement procedure.
- **SC-002**: 100% of factual product claims in the chapter trace to the vision
  document (docs/01) — no invented positioning, metrics, or market claims.
- **SC-003**: A test reader can produce both exercise artifacts (positioning statement
  + non-goals list with ≥3 reasoned entries) using only the chapter, in under 45
  minutes of the chapter's stated 60–120 minute budget.
- **SC-004**: The chapter contains at least 2 `WHY` boxes, exactly 1 `CHECKPOINT`
  block (at the end), at least 1 forward reference to a later part, and 1 takeaways
  block — verified by inspection.
- **SC-005**: A reader can reach the chapter from the tutorial entry point in at most
  2 navigation steps.
- **SC-006**: All recurring box types used by the chapter render visually distinct
  from body prose in both light and dark appearance modes, with zero per-chapter
  styling effort required for future chapters (the shell provides it).

## Assumptions

- Chapter 0.1's content source is `docs/01-product-vision.md`; its shape and reader
  deliverables come from `docs/07-tutorial-plan.md` (§2 format rules, §3 Part 0
  table). Both are treated as frozen inputs (tutorial risk T1: the SRS/docs are the
  tutorial's contract).
- "Start" in the feature description means author and publish the complete chapter,
  not an outline — a chapter is a sitting (docs/07 §2) and Part 0 chapters have no
  code dependency blocking completion.
- The chapter's *content* is prose-only (Part 0 precedes the code parts). Application
  work in this feature is limited to the FR-008 series shell (landing/table of
  contents, chapter layout, box styling) — no chat/product functionality.
- The scaffold-purity boundary from feature 001 (FR-003 there) ends where this feature
  begins: relay-tutorial now intentionally grows tutorial-site functionality. The 001
  boundary remains a historical record of the baseline, not an ongoing constraint.
- The git-tag-per-chapter and CI-checkpoint disciplines (docs/07 §6) apply to *code*
  chapters; for Part 0 prose chapters, the checkpoint is the reader-artifact check,
  and no CI work is assumed in this feature.
- English is the series language, matching all existing docs.
