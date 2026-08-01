# Feature Specification: Tutorial Chapter 1.3 — The Protocol Package

**Feature Branch**: `016-chapter-1-3`

**Created**: 2026-08-01

**Status**: Draft

**Input**: User description: "Chapter 1.3"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read chapter 1.3 and build the protocol package alongside it (Priority: P1)

As the tutorial's reader, I open Part 1's third chapter — "The protocol
package" (docs/07 §3) — with the 1.2 infrastructure standing. This is the
chapter where the series' longest-running promise gets paid: 1.1 argued that
one language means the wire contract can live in *one shared package* (the
chapter even drew it), and now I build that package — the frame types, error
codes, and runtime validation schemas that both ends of the WebSocket will
speak. The chapter teaches **contract-first** design: the wire format is
defined, typed, and validated before a single service exists to use it. By the
end, the workspace has its first package that actually computes something, the
test suite exercises real parse/reject behavior, and I understand why the
contract came before the code.

**Why this priority**: The chapter is the deliverable; docs/07 §3's row names
it, and 1.4's walking skeleton (and every Part 2 chapter) consumes this
package — the whole shared-types payoff of ADR-01 rides on it.

**Independent Test**: A reader with the 1.2 checkpoint state can, using only
the chapter: build the package, run the gate and watch the new schema tests
pass, and explain what contract-first buys (drift becomes a compile error) —
without consulting docs/04/05/06.

**Acceptance Scenarios**:

1. **Given** the published chapter, **When** read end to end, **Then** it
   derives the frame vocabulary from the product's own documents (the
   handshake acknowledgment and resume cursor, sends and acks with idempotency
   keys, the real-time event kinds, backfill truncation, the shutdown close),
   builds the package step by step, and closes in the format's runnable,
   tested state — the gate passes with the new tests included.
2. **Given** the series format rules (docs/07 §2, code-chapter battery),
   **Then** the chapter passes: 2,000–4,000 canonical words, ≥2 `WHY`, ≥1
   `TRAP`, 1 `SKIP AHEAD` naming tag `part1-ch3`, ≥1 forward reference, 2–4
   captioned figures, skip-safe takeaways, exactly one closing `CHECKPOINT`.
3. **Given** the chapter's factual claims, **Then** 100% trace to docs/04
   (EIR-WS, FR-MSG, FR-RTM), docs/05 (§5 runtime views, ADR-01/03/05), docs/06
   deep dives, or earlier chapters; quoted content follows the verbatim
   definition; no invented identifiers — including no invented frame names
   where the documents already name them.
4. **Given** the code the chapter builds, **Then** every file-content fence
   byte-matches the canonical repository at `part1-ch3` (the fence contract,
   third exercise) and earlier chapters' fences still hold (additive-only).

---

### User Story 2 - The canonical code advances to tag `part1-ch3` (Priority: P2)

As a reader (or a stuck reader), the protocol package exists in
`relay-platform` as the diff from `part1-ch2` to `part1-ch3` — a new workspace
package with meaningful tests, the first *runtime* dependency the workspace
has ever taken, and no edits to any file an earlier chapter fenced.

**Why this priority**: The tag discipline is the format's spine; this
increment also sets the precedent for how the workspace takes on runtime
dependencies (deliberately, one at a time, with the reasoning shown).

**Independent Test**: Checking out `part1-ch3` yields a workspace where the
gate passes with the protocol tests included; the `part1-ch2..part1-ch3` diff
contains exactly the chapter's additions; the new package is consumable by
other workspace packages (the 1.4 skeleton's prerequisite).

**Acceptance Scenarios**:

1. **Given** the repository at `part1-ch3`, **When** the gate runs, **Then**
   lint, typecheck, and tests all pass, and the test count grows by the
   protocol suite — tests that reject malformed frames, not placeholders.
2. **Given** the diff from `part1-ch2`, **Then** it is strictly additive over
   fenced files (the new package, plus never-fenced files if needed), and the
   workspace's first runtime dependency arrives pinned and justified.
3. **Given** the package boundary, **Then** it is importable by future
   workspace consumers (services, and eventually the SDK) — the one-home
   property 1.1 promised, now load-bearing.

---

### User Story 3 - The forthcoming entry flips to published, bilingually (Priority: P3)

As a reader of either language, chapter 1.3 appears everywhere the series is
navigable: the manifest entry flips to published+translated, 1.2's footer
gains its next card, the sidebar shows Part 1 with three links and one
forthcoming entry, the sitemap grows by exactly the two new pages, and the
Vietnamese edition ships at the settled naturalized register — with the
select-to-suggest capture automatically active on the new pages (the 015
allowlist derives from the manifest).

**Why this priority**: Structural integration after content exists; also the
second full exercise of the flip drill.

**Independent Test**: From either landing, reach 1.3 in ≤2 steps; 1.2↔1.3
footer cards live both locales; sidebar 3+1; sitemap 28 → exactly 30; vi
parity incl. byte-identical fences; a suggestion POST against the new vi page
path is accepted.

**Acceptance Scenarios**:

1. **Given** the manifest, **When** 1.3's entry flips (status, translation
   flag, settled reader-facing values), **Then** every navigation surface
   updates with zero manual edits, and the suggestions allowlist admits the
   two new page paths automatically.
2. **Given** 1.2's footers (both locales), **Then** the next card appears,
   linking 1.3; 1.3's footers link back to 1.2 and forward to nothing (1.4
   forthcoming).
3. **Given** the Vietnamese chapter, **Then** box/figure counts match en,
   code fences are byte-identical, and the prose follows the naturalized
   register and settled glossary ("package", "cửa ải"/"vượt qua", "bản giao
   kèo", "quả ngọt", "tin nhắn"; dev terms English; no calques, no hyphenated
   compounds).

---

### Edge Cases

- **The frame vocabulary must be derived, not invented**: the SRS and SAD name
  specific frames (`connection.ack`, `message.send`, `message.ack`,
  `server.shutdown`), events (creation, edit, deletion, membership, presence,
  typing), close codes (4009), and semantics (per-channel cursors, 24 h
  idempotency window, 500-message backfill truncation). Where the documents
  are silent on a detail the package needs (exact field spellings, an error
  code registry's shape), the chapter must *say* it is deciding — recorded
  decisions, not silent inventions the ID detector would flag.
- **Scope discipline — vocabulary for the skeleton, not the whole SRS**: the
  package covers what 1.4 and Part 2's core loop need; later capabilities
  (media, moderation, emoji) join in their own parts. The boundary must be
  stated, not implied.
- **The first runtime dependency**: everything until now was devDependencies.
  Taking one is a teachable decision (why runtime validation at all, why this
  cost is paid once in one package) — and a TRAP-shaped temptation (every
  package sprouting its own validation library).
- **Types vs. schemas duality**: the package must not let the static types and
  the runtime schemas drift from each other — the chapter must show the
  mechanism that keeps them one thing.
- **Chapter/code drift across three chapters**: 1.1's ten fences and 1.2's
  three must still byte-match at `part1-ch3`; the fence battery now spans
  three chapters.
- **Suggestion capture on new pages**: works automatically via the manifest —
  verification should prove it rather than assume it (the first flip since
  015 shipped).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Chapter 1.3 MUST exist as a published chapter titled per docs/07
  ("The protocol package") at the manifest's seeded Part 1 path, in both
  locales, rendered through the existing shell with all established chrome
  (code-block titles/copy, figures, sidebars, suggestion capture).
- **FR-002**: The chapter MUST teach contract-first design as docs/07's row
  states it — the wire contract defined, typed, and runtime-validated before
  any service exists — and MUST connect it explicitly to ADR-01's shared-types
  payoff as promised in 1.1.
- **FR-003**: The chapter MUST derive the package's frame vocabulary from the
  product documents (handshake ack + resume cursor per EIR-WS-03; send/ack
  with idempotency keys per FR-MSG-04 and SAD §5.1; the six real-time event
  kinds per FR-RTM-05; backfill truncation per FR-RTM-04; the shutdown close
  per SAD §7), quoting per the verbatim definition and explicitly marking any
  detail the documents leave open as a decision the chapter records.
- **FR-004**: The chapter MUST end in the runnable, tested state: the package
  builds, the gate passes with a meaningful new test suite (schemas reject
  malformed frames), and a closing `CHECKPOINT` verifies the reader's state.
- **FR-005**: The chapter MUST pass the code-chapter battery: 2,000–4,000
  canonical words; ≥2 `WHY`; ≥1 `TRAP`; 1 `SKIP AHEAD` naming `part1-ch3`; ≥1
  forward reference; 2–4 captioned figures; takeaways; exactly one closing
  `CHECKPOINT`.
- **FR-006**: The canonical repository MUST advance by exactly this chapter's
  content and be tagged `part1-ch3` (Dong's tag); the workspace's first
  runtime dependency MUST be pinned and its adoption reasoned in the chapter;
  the additive-only rule holds (no file fenced by 1.1 or 1.2 is modified).
- **FR-007**: The chapter's file-content fences MUST byte-match the repository
  at `part1-ch3` (with `title=""` paths); commands MUST replay; en/vi fences
  MUST be byte-identical; 1.1's and 1.2's fences MUST still match at the new
  state.
- **FR-008**: Publishing MUST be manifest-only: 1.3's entry flips
  (published + translated + settled reader-facing values); all surfaces update
  automatically; the sitemap grows from 28 to exactly 30 URLs; the suggestions
  allowlist admits the new paths with zero edits.
- **FR-009**: The Vietnamese chapter MUST be structurally identical at the
  naturalized register per the settled glossary; identifiers, frame names,
  code, and commands stay English; naturalization self-review before
  presenting.
- **FR-010**: 100% of quoted content MUST be faithful to current docs/04/05/06;
  the invented-ID detector passes over both page.mdx and figures.ts — extended
  in spirit to frame names (document-named frames only, or explicitly marked
  chapter decisions).

### Key Entities

- **Chapter 1.3**: Third code chapter; sources docs/04 (EIR-WS, FR-MSG,
  FR-RTM), docs/05 (§5 runtime views, §7 drain, ADR-01/03/05), docs/06 deep
  dives, docs/07 §2–3; reader produces the shared protocol package with a
  passing schema test suite.
- **The protocol package**: The workspace's first computing package — frame
  types, error/close codes, runtime validation schemas, cursor and
  idempotency-key semantics — one home for the wire contract, consumed by
  everything built after it.
- **Chapter tag `part1-ch3`**: The checkout-able chapter-end state; diff from
  `part1-ch2` is the chapter.
- **The manifest flip**: 1.3's forthcoming→published transition, now also
  feeding the suggestions allowlist.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The chapter body is 2,000–4,000 canonical words and passes the
  full battery in both locales with structural parity and byte-identical
  fences.
- **SC-002**: At `part1-ch3`, the gate passes with the protocol suite
  included, and the suite demonstrably rejects malformed input (not
  placeholder assertions) — machine-verified.
- **SC-003**: 100% of file-content fences (1.3's, plus 1.1's and 1.2's
  re-checked) match the repository state on comparison; verbatim spot-checks
  pass; the ID detector is clean with zero unmarked invented frame names.
- **SC-004**: From either landing, 1.3 is reachable in ≤2 steps; 1.2's footers
  show the next card; sidebar shows Part 1 as exactly 3 links + 1 forthcoming;
  the sitemap holds exactly 30 URLs; a suggestion submission against each new
  page path returns success.
- **SC-005**: A test reader can go from the 1.2 checkpoint to the passing
  1.3 checkpoint within the chapter's stated time budget, using only the
  chapter.
- **SC-006**: Publishing changes only the manifest and adds content files —
  every surface, including the 015 allowlist, updates by itself.

## Assumptions

- **Chapter scope is docs/07's row**: frame types, error codes, runtime
  schemas — the vocabulary 1.4's walking skeleton and Part 2's core loop
  consume. Service code stays in 1.4; SDK consumption is a later part;
  media/moderation/emoji vocabularies join in their parts.
- **The technology facts come from the product's documents**: the validation-
  library choice is fixed by docs/07's row itself; versions and package shape
  are plan-level decisions.
- **The repository conventions continue**: additive-only over fenced files,
  tag naming per docs/07 §2, fence-equals-repo verified by diff, the
  three-command gate as done, commits/tags/pushes are Dong's.
- **The manifest seed from 013 holds** (title, titleVi "Package protocol",
  path); the flip settles reader-facing placeholder values like 014 did.
- **The vi edition translates prose; code, frame names, and commands stay
  English** — settled conventions, including translated figure labels.
- **Dong reviews the Vietnamese translation before committing**; the
  suggestion capture gives readers a correction channel from day one.
