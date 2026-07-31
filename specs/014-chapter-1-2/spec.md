# Feature Specification: Tutorial Chapter 1.2 — One Command, Whole World

**Feature Branch**: `014-chapter-1-2`

**Created**: 2026-07-31

**Status**: Draft

**Input**: User description: "Start chapter 1.2"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read chapter 1.2 and stand up the local infrastructure alongside it (Priority: P1)

As the tutorial's reader, I open Part 1's second chapter — "One command, whole
world" (docs/07 §3) — with the chapter-1.1 workspace on my machine. The chapter
teaches NFR-MNT-03 ("the full stack shall be startable locally with a single
command") **as a day-one requirement, not an afterthought**: I add the compose
infrastructure that gives the workspace its four backing stores — Postgres,
Redis, NATS, ClickHouse — and I learn *why each store is there*, because each
one exists by a recorded architecture decision, not by habit. By the end, one
command brings the whole local world up, a verification step proves every store
is actually ready (not merely started), and the chapter-1.1 gate still passes.

**Why this priority**: The chapter is the deliverable; it is docs/07 §3's next
row, and chapters 1.3–1.4 (protocol package, walking skeleton) assume this
infrastructure exists underneath them.

**Independent Test**: A reader with the chapter-1.1 workspace (or tag
`part1-ch1` checked out) can, using only the chapter: add the compose
infrastructure, start it with one command, verify all four stores report
healthy, tear it down and bring it back without losing the workspace, and
explain which decision put each store in the stack — without consulting
docs/05/06.

**Acceptance Scenarios**:

1. **Given** the published chapter, **When** read end to end, **Then** it
   builds the local infrastructure step by step (the compose file, each store's
   configuration, the readiness verification), and closes in the format's
   mandated **runnable, tested state** — the reader can run the single startup
   command, see every store healthy, and see the toolchain gate still pass.
2. **Given** the series format rules (docs/07 §2, as amended for code
   chapters), **Then** the chapter passes the battery: 2,000–4,000 canonical
   words (prose outside fences), first-person plural present, ≥2 `WHY` (citing
   NFR-MNT-03/D8 and the per-store decisions), ≥1 `TRAP`, 1 `SKIP AHEAD` naming
   the chapter's tag, ≥1 forward reference, 2–4 captioned figures, skip-safe
   takeaways, exactly one closing `CHECKPOINT`.
3. **Given** the chapter's factual claims, **Then** 100% trace to docs/04
   (NFR-MNT-03), docs/05/06 (the SAD's deployment view and the store ADRs), or
   earlier chapters; quoted decision content follows the established verbatim
   definition; no invented identifiers.
4. **Given** the code the chapter builds, **Then** every command and
   file-content code block matches the canonical repository at this chapter's
   tag — the chapter and the code cannot drift (the 1.1 fence contract,
   continued).

---

### User Story 2 - The canonical code advances to tag `part1-ch2` (Priority: P2)

As a reader (or a stuck reader), the compose infrastructure this chapter builds
exists in the canonical `relay-platform` repository as the diff from
`part1-ch1` to `part1-ch2` — so I can check out exactly the chapter-end state,
and the tag-to-tag diff *is* the chapter.

**Why this priority**: "Ends in a runnable, tested state" and "git tag per
chapter" are docs/07 §2's core format commitments; 1.1 established the
mechanism, and this chapter is its first *increment* — the first time the
tag-to-tag diff discipline is exercised on a non-empty starting point.

**Independent Test**: Checking out `part1-ch2` yields a workspace where the
toolchain checks pass with zero errors and the single startup command brings
all four stores to a healthy state; the diff from `part1-ch1` contains the
chapter's changes and nothing else.

**Acceptance Scenarios**:

1. **Given** the repository at `part1-ch2`, **When** the toolchain checks run
   (install, lint, type check, tests), **Then** all pass — and the test suite's
   assertions cover the new infrastructure declaration, so "tested state"
   includes the world this chapter adds, not just last chapter's constants.
2. **Given** the repository at `part1-ch2` on a machine with the container
   runtime available, **When** the single startup command runs, **Then** all
   four stores reach a ready/healthy state, and the chapter's verification
   step demonstrates it.
3. **Given** the `part1-ch1..part1-ch2` diff, **Then** it contains exactly the
   chapter's content — the no-drift discipline holds on the series' first
   incremental tag.

---

### User Story 3 - The forthcoming entry flips to published, bilingually (Priority: P3)

As a reader of either language, chapter 1.2 appears everywhere the series is
navigable: the manifest entry that has stood as "forthcoming" since 1.1 shipped
flips to published, 1.1's footer gains its next-chapter card, the sidebar and
landings update, the sitemap grows by exactly the two new pages, and the
Vietnamese edition ships the same chapter under the settled translation
conventions.

**Why this priority**: Structural integration matters once content exists; this
is also the first real exercise of the manifest-flip publishing drill on an
entry that already exists as forthcoming structure.

**Independent Test**: From either landing, reach 1.2 in ≤2 steps; 1.1's footers
show a next card in both locales; the sidebar shows Part 1 with two links and
two forthcoming entries; the sitemap grows from 26 to exactly 28 URLs; the vi
chapter passes structural parity.

**Acceptance Scenarios**:

1. **Given** the series manifest, **When** 1.2's entry flips from forthcoming
   to published (with its translation flag), **Then** every navigation surface
   (landings, sidebar, footers, sitemap, SEO metadata) updates with zero manual
   edits — the publishing-is-manifest-only property, proven on a pre-existing
   entry for the first time.
2. **Given** 1.1's footers (both locales), **Then** the next card appears,
   linking 1.2; 1.2's footers link back to 1.1 and forward to nothing (1.3
   forthcoming).
3. **Given** the Vietnamese chapter, **Then** box/figure counts match the
   English chapter, code fences are byte-identical to the English chapter's,
   identifiers/status values/commands stay English, and the prose follows the
   naturalized register (the 0.5 standard — "tin nhắn", no calques).

---

### Edge Cases

- **"Runnable, tested state" now spans two machines' worth of meaning**: the
  toolchain gate (lint, typecheck, test) must stay green *without* requiring
  the container runtime — CI-style verification — while the chapter's full
  promise (stores healthy) requires it. The chapter must be explicit about
  which check proves what, and the test suite must assert what it *can* about
  the infrastructure declaration without needing containers running.
- **Started is not ready**: the naive reader (and the naive tutorial) treats
  "the containers are up" as done; the stores accept connections some seconds
  later, and 1.4's services will crash-loop against them. Readiness
  verification (healthchecks / a wait strategy) is the chapter's likely TRAP
  territory.
- **Port collisions on reader machines**: Postgres on 5432 or Redis on 6379
  may already be taken locally; the chapter must either address it or choose
  bindings that make the collision story explicit.
- **Data persistence across restarts**: volumes vs. throwaway state — the
  chapter must make the choice consciously and say what a reader loses on
  `down`.
- **The SAD's compose sentence is wider than this chapter**: the SAD's
  deployment view lists the four stores *plus MinIO and a seeded demo tenant*.
  Those depend on media handling and services that do not exist yet; the
  chapter must handle the difference honestly (a forward reference, not a
  silent omission).
- **Readers without Docker**: docs/07 §1.2 assumes "Docker exists" as
  knowledge, not that the runtime is installed/working; the chapter states its
  prerequisite and points at the official install path without becoming an
  installation guide.
- **Chapter/code drift on an incremental tag**: 1.1's fence contract must hold
  *and* the earlier chapter's fences must still match the repository at the
  new tag (the compose chapter must not silently edit 1.1's files).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Chapter 1.2 MUST exist as a published chapter titled per docs/07
  ("One command, whole world") at the manifest's established Part 1 path, in
  both locales, rendered through the existing shell (header source links,
  figures, sidebars, code-block titles/copy all functioning).
- **FR-002**: The chapter MUST teach NFR-MNT-03 as a day-one requirement — the
  docs/07 row's stated angle — including why single-command local
  reproducibility is a P1 requirement for this product (D8: one engineer runs
  and reasons about all of it) rather than developer convenience.
- **FR-003**: The chapter MUST introduce all four backing stores of docs/07's
  row — Postgres, Redis, NATS, ClickHouse — each justified by its recorded
  decision (the SAD's technology choices and their ADRs), with rejected
  alternatives named where the teaching depends on them; quoted decision
  content follows the established verbatim definition.
- **FR-004**: The chapter MUST end in the format's runnable, tested state: one
  command starts the full local infrastructure, a shown verification step
  proves every store is ready (not merely started), the toolchain gate passes,
  and a closing `CHECKPOINT` verifies the reader's state before 1.3.
- **FR-005**: The chapter MUST pass the amended code-chapter battery:
  2,000–4,000 canonical words (prose outside fences); ≥2 `WHY`; ≥1 `TRAP`; 1
  `SKIP AHEAD` naming tag `part1-ch2`; ≥1 forward reference; 2–4 captioned
  figures (per-locale `figures.ts`); skip-safe takeaways; exactly one closing
  `CHECKPOINT`.
- **FR-006**: The canonical repository MUST advance by exactly this chapter's
  content and be tagged `part1-ch2`; the toolchain checks MUST pass at that
  tag, and the test suite MUST assert meaningfully about the new
  infrastructure declaration (the day-one-test convention continued) without
  requiring a running container runtime.
- **FR-007**: The chapter's file-content code blocks MUST byte-match the
  repository at `part1-ch2` (including file-path titles per the established
  convention), commands MUST be reproducible as shown, and chapter 1.1's
  fences MUST still match the repository at the new tag.
- **FR-008**: Publishing MUST be manifest-only: 1.2's existing forthcoming
  entry flips to published+translated; all navigation surfaces (landings,
  sidebar, 1.1/1.2 footers, sitemap, SEO metadata) update automatically; the
  sitemap grows from 26 to exactly 28 URLs.
- **FR-009**: The Vietnamese chapter MUST be a faithful, structurally identical
  translation under the settled register and glossary (naturalized 0.5
  standard); code fences byte-identical to English; commands, identifiers,
  store names, and tag names stay English.
- **FR-010**: 100% of quoted decision content MUST be faithful to current
  docs/04/05/06; the invented-ID detector passes over the chapter and its
  figure labels.

### Key Entities

- **Chapter 1.2**: Second code chapter; sources docs/04 (NFR-MNT-03), docs/05
  (deployment view §deployment, technology ADRs), docs/06 (relevant deep
  dives), docs/07 §2–3; reader produces the running local infrastructure.
- **The local infrastructure declaration**: The compose definition in
  `relay-platform` — four stores, healthchecks, volumes — the chapter's
  central artifact.
- **Chapter tag `part1-ch2`**: The checkout-able chapter-end state; the series'
  first incremental tag (diff from `part1-ch1` is the chapter).
- **The manifest flip**: 1.2's forthcoming→published transition — the
  publishing mechanism's first exercise on pre-existing structure.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The chapter body is 2,000–4,000 canonical words and passes the
  full code-chapter battery (boxes, 2–4 captioned figures, takeaways, one
  checkpoint) in both locales with structural parity and byte-identical fences.
- **SC-002**: At `part1-ch2`, the toolchain checks pass with zero errors on a
  machine without the container runtime; with it, the single startup command
  brings all four stores to a verified-ready state — machine-verified.
- **SC-003**: 100% of the chapter's file-content fences match the tagged
  repository state on comparison (1.1's fences included); quoted decision
  content passes the verbatim spot-checks; the ID detector is clean.
- **SC-004**: From either locale's landing, 1.2 is reachable in ≤2 steps; 1.1's
  footers show the next card in both locales; the sidebar shows Part 1 with
  exactly two links and two forthcoming entries; the sitemap holds exactly 28
  URLs.
- **SC-005**: A test reader can go from the 1.1 checkpoint to the passing
  1.2 checkpoint within the chapter's stated time budget, using only the
  chapter.
- **SC-006**: Publishing changes only the manifest and adds content files —
  every navigation and SEO surface updates by itself, demonstrated on an entry
  that already existed as forthcoming.

## Assumptions

- **Chapter scope is docs/07's row**: the compose infrastructure with the four
  named stores, taught through NFR-MNT-03. MinIO and the seeded demo tenant —
  which the SAD's full compose sentence includes — depend on media handling
  and services that arrive in later parts; the chapter acknowledges them as a
  forward reference rather than shipping stubs. Service code and the protocol
  package remain 1.3–1.4 scope.
- **The technology facts come from the product's own documents** (the SAD's
  technology table and ADRs): the chapter teaches the stack the documents
  fixed — the spec does not re-decide versions or alternatives.
- **The repository conventions from 1.1 continue**: `relay-platform` submodule,
  tag naming per docs/07 §2 (`part1-ch2`), fence-equals-repo verification by
  comparison, the three-command gate as the definition of done.
- **The reader's machine has a working container runtime** for the chapter's
  full promise; the toolchain gate itself stays runtime-independent so the
  tested state is CI-verifiable.
- **The vi edition translates prose; code, commands, and store names stay
  English** — the settled conventions from 1.1, including byte-identical
  fences and translated figure labels.
- **Dong reviews the Vietnamese translation before committing; commits, pushes,
  and tags are Dong's** — per the standing convention.
