# Feature Specification: Tutorial Chapter 1.1 — The Monorepo and the Toolchain

**Feature Branch**: `013-chapter-1-1`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "Start part 1 chapter 1.1"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read chapter 1.1 and build the workspace alongside it (Priority: P1)

As the tutorial's reader, I open Part 1's first chapter — "The monorepo and the
toolchain" (docs/07 §3) — and the series changes gear: after five chapters of
paperwork, I now *build*. The chapter opens with the promised one-page "the
decisions, if you skipped the reasoning" summary (so Part 0 skippers can start
here), then walks me through creating the Relay code workspace — one repository,
one language, shared tooling — teaching ADR-01 (one language everywhere) and
workspace discipline as I go. By the end I have a running, tested scaffold and I
understand *why* it is one repo and one language, not a folk-wisdom polyglot setup.

**Why this priority**: The chapter is the deliverable; it is the gateway to every
code chapter after it, and docs/07 §5 names Part 1 as the first milestone of the
writing plan's code phase.

**Independent Test**: A reader who finished Part 0 (or read the opening decisions
summary) can, using only the chapter: create the workspace, run the toolchain
checks (lint, tests, type checks) successfully at the end, and explain why ADR-01
rejected the "right tool per service" instinct — without consulting docs/05/06.

**Acceptance Scenarios**:

1. **Given** the published chapter, **When** read end to end, **Then** it opens
   with the one-page decisions summary (Part 0 compressed for skippers), builds
   the workspace step by step (workspace layout, shared configuration, lint, test
   runner), and closes in the format's mandated **runnable, tested state** — the
   reader can execute the toolchain checks and see them pass.
2. **Given** the series format rules (docs/07 §2, as amended), **Then** the
   chapter passes the battery: 2,000–4,000 canonical words, first-person plural
   present, ≥2 `WHY` (citing ADR-01 and the workspace-discipline rationale), ≥1
   `TRAP` (the format's code-chapter box, debuting here — the naive mistake the
   reader would otherwise make), 1 `SKIP AHEAD`, ≥1 forward reference, 2–4
   captioned figures, skip-safe takeaways, exactly one closing `CHECKPOINT`.
3. **Given** the chapter's factual claims, **Then** 100% trace to docs/05/06
   (ADR-01 and its deep dive), the constitution's technology constraints, or
   earlier chapters; quoted decision content follows the established verbatim
   definition; no invented identifiers.
4. **Given** the code the chapter builds, **Then** every command and file the
   chapter shows matches the canonical code repository at this chapter's tag —
   the chapter and the code cannot drift (docs/07 §6's core promise).

---

### User Story 2 - The canonical code exists at a per-chapter tag (Priority: P2)

As a reader (or a stuck reader), the code this chapter builds exists in the
canonical Relay code repository, tagged for this chapter per the format rules —
so I can check out exactly the chapter-end state, diff it against the (empty)
starting point, and `SKIP AHEAD` has a real target for the first time.

**Why this priority**: "Ends in a runnable, tested state" and "git tag per
chapter" are docs/07 §2's core format commitments; the code repository is the
mechanism, and this feature establishes it for all forty-plus code chapters that
follow.

**Independent Test**: Checking out the chapter's tag in the code repository
yields a workspace where the toolchain checks pass with zero errors; the chapter's
skip-ahead box names that tag; the repository's history is clean enough that the
tag-to-tag diff *is* the chapter's content.

**Acceptance Scenarios**:

1. **Given** the code repository at this chapter's tag, **When** its checks run
   (install, lint, type check, tests), **Then** all pass — the runnable, tested
   state is machine-verifiable, per the constitution's requirement-driven
   delivery principle.
2. **Given** the repository, **Then** it is versioned independently of the
   tutorial site and the parent documents (its own history, so per-chapter tags
   and diff links stay clean), and the tutorial's standing repository conventions
   apply (the reader-facing README, the no-drift discipline).
3. **Given** the chapter's `SKIP AHEAD` box, **Then** it points at the real tag —
   the format's "what to check out if stuck" finally has a checkout.

**Resolved**: The canonical code repository is **`relay-platform`**
(github.com/anhba817/relay-platform — already created, currently empty),
attached as a second submodule of the parent repository alongside
`relay-tutorial`, with its own independent history for per-chapter tags.

---

### User Story 3 - Part 1 opens across the bilingual series (Priority: P3)

As a reader of either language, chapter 1.1 appears everywhere the series is
navigable — and with it **Part 1 comes alive**: the landing pages and the reading
sidebar show Part 1 with its first published chapter (and its remaining chapters
as visible forthcoming structure), 0.5's footer gains a next-chapter card for the
first time since Part 0 closed, and the Vietnamese edition ships the same chapter
under the settled translation conventions.

**Why this priority**: Structural integration matters once content exists; the
Part-boundary crossing (0.5 → 1.1) is this feature's unique navigation moment.

**Independent Test**: From either landing, reach 1.1 in ≤2 steps; 0.5's footers
now show a next card in both locales; the sidebar lists Part 1 with one link and
three forthcoming entries; the sitemap grows by exactly the new pages; the vi
chapter passes structural parity.

**Acceptance Scenarios**:

1. **Given** the series manifest, **When** the chapter ships, **Then** Part 1
   carries its four docs/07 chapters (1.1 published and translated; 1.2–1.4
   forthcoming), and every navigation surface (landings, sidebar, footers,
   sitemap) updates with zero manual edits.
2. **Given** 0.5's footers (both locales), **Then** the next card appears for the
   first time, linking 1.1 — the empty-next state retires exactly as designed.
3. **Given** the Vietnamese chapter, **Then** box/figure counts match the English
   chapter, code blocks and commands stay English with the settled gloss
   conventions where needed, identifiers and tag names stay English, and the
   prose follows the established natural register (the 0.5 naturalization
   standard — "tin nhắn", no calques).

---

### Edge Cases

- **The Part 0 → Part 1 gear change**: readers arriving fresh must be caught by
  the opening decisions summary; readers from 0.5 must not be bored by it — it is
  a compressed lookup, not a re-teaching.
- **The TRAP box debuts**: its first use must match docs/07's definition (the bug
  you'd write naively) — a real mistake with a real consequence, not a styled
  tip.
- **Chapter/code drift**: every command, file path, and output the chapter quotes
  must hold at the chapter's tag; verification must compare them, not trust them.
- **Readers without the reader's-own-project**: Part 0's exercises built a
  parallel project (the vet clinic); Part 1 builds *Relay itself* — the exercise
  convention must adapt (the reader builds Relay's workspace, and the
  reader-produces artifact is the working scaffold).
- **Sidebar and landing for a part in progress**: Part 1 shows one link + three
  forthcoming entries — the first time a part renders mixed (built for this, but
  never exercised).
- **Sitemap/SEO**: only the published chapter's two pages join the sitemap
  (24→26); forthcoming chapters stay out.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Chapter 1.1 MUST exist as a published chapter titled per docs/07
  ("The monorepo and the toolchain") at a Part 1 path following the established
  URL convention, in both locales, rendered through the existing shell (header
  source links, figures, sidebars all functioning).
- **FR-002**: The chapter MUST open with the one-page "decisions, if you skipped
  the reasoning" summary docs/07 promises — Part 0's binding artifacts compressed
  to a lookup.
- **FR-003**: The chapter MUST teach ADR-01 (one language everywhere) through the
  build: the workspace layout, shared configuration, lint, and test runner —
  including the rejected polyglot alternatives and ADR-01's reversal condition,
  quoted per the established verbatim definition.
- **FR-004**: The chapter MUST end in the format's runnable, tested state: the
  reader's workspace passes the toolchain checks, and a closing `CHECKPOINT`
  verifies it before Part 1 continues.
- **FR-005**: The chapter MUST pass the amended format battery: 2,000–4,000
  canonical words; ≥2 `WHY`; **≥1 `TRAP`** (first use); 1 `SKIP AHEAD` naming the
  chapter's tag; ≥1 forward reference; 2–4 captioned figures (per-locale
  `figures.ts`, specimen rules unchanged); takeaways; exactly one `CHECKPOINT`.
- **FR-006**: The canonical code repository `relay-platform`
  (github.com/anhba817/relay-platform) MUST be initialized as a second submodule
  of the parent repository, versioned independently with its own history; the
  chapter-end state MUST be tagged `part1-ch1` per the format's naming
  convention, and the toolchain checks MUST pass at that tag.
- **FR-007**: The chapter's shown commands, files, and outputs MUST match the
  code repository at the tag — verified by comparison, not assertion.
- **FR-008**: The series manifest MUST gain Part 1's four docs/07 chapters (1.1
  published + translated; 1.2–1.4 forthcoming); all navigation surfaces
  (landings, sidebar, 0.5's footers, sitemap, SEO metadata) update automatically;
  the sitemap grows by exactly 1.1's two pages.
- **FR-009**: The Vietnamese chapter MUST be a faithful, structurally identical
  translation under the settled register and glossary (the naturalized 0.5
  standard); commands, code, identifiers, and tag names stay English.
- **FR-010**: 100% of quoted decision content MUST be faithful to current
  docs/05/06; the invented-ID detector (extended to ADR/driver IDs) passes over
  the chapter and its figure labels.

### Key Entities

- **Chapter 1.1**: First code chapter; sources docs/05 §9 (ADR-01), docs/06
  (ADR-01 deep dive), docs/07 §2–3; reader produces the running Relay workspace.
- **The Relay code repository**: The canonical implementation the whole series
  builds; independent history; per-chapter tags; checks green at every tag.
- **Chapter tag**: The named, checkout-able chapter-end state — the format's
  skip-ahead and diff-link mechanism, debuting here.
- **Decisions summary**: The one-page Part 0 compression that opens Part 1.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The chapter body is 2,000–4,000 canonical words and passes the full
  amended battery (boxes incl. ≥1 TRAP, 2–4 figures with captions, takeaways, one
  checkpoint) in both locales with structural parity.
- **SC-002**: At the chapter's tag, the code repository's toolchain checks pass
  with zero errors — machine-verified.
- **SC-003**: 100% of the chapter's shown commands and file contents match the
  tagged repository state on comparison; quoted ADR content passes the verbatim
  spot-checks; the ID detector is clean.
- **SC-004**: From either locale's landing, 1.1 is reachable in ≤2 steps; 0.5's
  footers show the next card in both locales; the sidebar shows Part 1 with
  exactly one link and three forthcoming entries; the sitemap holds exactly 26
  URLs.
- **SC-005**: A test reader can go from nothing to the passing chapter-end state
  within the chapter's stated time budget, using only the chapter.
- **SC-006**: Publishing changes only the manifest and adds content files —
  every navigation and SEO surface updates by itself (the established drill).

## Assumptions

- **Chapter scope is docs/07's row**: workspace, shared config, lint, test
  runner — teaching ADR-01 and workspace discipline. Service code, compose
  infrastructure, and the protocol package belong to 1.2–1.4.
- **The technology facts come from the product's own documents** (constitution
  technology constraints; ADR-01): the chapter teaches the stack the documents
  fixed — the spec does not re-decide it.
- **The code repository follows the relay-tutorial precedent**:
  `anhba817/relay-platform` (created by Dong, currently empty) attached as a
  second submodule of the parent repository, with its own independent history
  for clean per-chapter tags.
- **Tag naming follows docs/07 §2's convention** (`part2-ch3` style → this
  chapter: `part1-ch1`).
- **The vi edition translates prose; code and commands stay English** — the
  settled specimen/gloss conventions extended to code blocks.
- **Dong reviews the Vietnamese translation before committing; commits/pushes
  are Dong's** — including the new repository's creation and its first push.
