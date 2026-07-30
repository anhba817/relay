# Research: Tutorial Chapter 0.4 — Requirements You Can Test

**Feature**: `specs/007-tutorial-chapter-04` · **Date**: 2026-07-30

Grounded in the current (media-inclusive) docs/04-srs.md — read in full, including the
new §4.14 (FR-MED-01..14) and the updated totals (224 requirements) — docs/07 §3, and
the pattern proven by features 005/006.

## R1 — Manifest: one entry flip

- **Decision**: Flip 0.4 to `status: "published"`, add `translatedIn: ["vi"]`,
  validate `readerMinutes` (100). Path
  (`/part-0/chapter-04/requirements-you-can-test`), `titleVi` ("Những yêu cầu bạn có
  thể kiểm chứng", user-approved), and `readerProducesVi` already reserved — binding.
- **Rationale**: Fourth exercise of the 004 C5 contract.

## R2 — English chapter: anatomy → traces → the star requirement → change

- **Decision**: Eight beats:
  1. **Cold open** — journey maps are still stories, and stories don't gate
     releases; the chapter's thesis: *a requirement without a test plan is an
     opinion*. Inputs pointer (0.3 maps + ★s); SKIP AHEAD early.
  2. **The anatomy of a requirement** — specimen: FR-MSG-04 (idempotency key,
     straight out of Tuan's tunnel): a stable ID, a shall-statement, a priority, a
     verification method. Then the verification vocabulary T/D/I/A with one real
     example each: FR-MSG-04 (T — automated), FR-DSH-01 (D — demonstration,
     dev-key-on-first-screen), EIR-API-07 (I — inspection, OpenAPI completeness),
     FR-MSG-06 (A — analysis: "an acknowledged message shall not be lost" cannot be
     proven by one test run). The probe every row must survive: *how would we
     know?*
  3. **The ledger discipline** — stable IDs never reused (identifiers are
     promises); the P1–P5 ladder mapped to the phased roadmap; 224 requirements
     total, 57 in Phase 1 — "sequenced, not simultaneous" (Appendix A's own
     argument); shall-language removing argument.
  4. **Journeys → requirements, trace one (Tuan)** — his tunnel ★ becomes
     FR-MSG-04 (idempotent send), FR-RTM-03 (cursor backfill), FR-SDK-04 (jittered
     backoff): each line of the ★ stage has an ID now. First WHY box (SRS §7
     traceability — the persona/journey tables exist so no requirement is an
     orphan).
  5. **Journeys → requirements, trace two (Priya) + the star requirement** — her
     reconstruct ★ becomes FR-MSG-07/08/10 and FR-MOD-01; then the SRS's own
     centerpiece: FR-TEN-05, "the single most important requirement in this
     document", Sev-0 on violation, verified by an automated cross-tenant suite on
     every build — and its companion NFR-MNT-02 (ordering/idempotency/isolation at
     100% branch coverage). Testability at maximum stakes.
  6. **A spec absorbs change without lying** — the hosted-media update as the live
     example: 0.1's reversed non-goal arrives as §4.14's *new* IDs
     (FR-MED-01..14), never edits to old ones; FR-MED-09 quoted — a rejected upload
     renders as a rejection marker, never a broken link, *because Priya's
     reconstruction must distinguish "rejected upload" from "deleted message"* —
     journeys→requirements working in real time, months after the journey was
     mapped. Second WHY box.
  7. **Exercise** (R4), **takeaways**, **CHECKPOINT** (slice required before 0.5,
     which decides architecture against it). ForwardRef: these requirements become
     Part 2's chapters — FR-MSG-04 *is* chapter 2.3, the cross-tenant suite *is*
     chapter 3.7's isolation gauntlet.
- **Rationale**: FR-002..005 mapped beat-for-beat; specimen rows are quoted
  verbatim (FR-007/SC-002); budget ~2,300 body + ~700 exercise.
- **Alternatives considered**: surveying all requirement families (a catalog, not a
  lesson); teaching on invented toy requirements (violates FR-007 and wastes the
  real SRS's authority).

## R3 — Specimen rendering: fenced blocks, never pipe tables

- **Decision**: Quoted requirement rows render as fenced code blocks (monospace
  `ID · shall-statement · priority · verification` layout), ≤3 fences per file,
  chapter readable without them. **Pipe tables are prohibited**: the MDX pipeline
  has no GFM plugin (established in feature 002) — a markdown table would render as
  literal pipes.
  **"Verbatim", defined (analysis A1)**: the ID, shall-statement text, priority,
  and method values match docs/04 exactly (statement text greppable in the source);
  the middot layout is the sanctioned re-rendering — separators and table
  decoration are free, words are not. This is what keeps SC-002's grep meaningful
  AND the quickstart's zero-`^|` check valid simultaneously.
- **Rationale**: Fenced blocks render correctly in both themes/locales with zero
  new machinery; adding remark-gfm for one chapter violates the no-infrastructure
  rule and betrays the constitution's boring-choice bias.
- **Alternatives considered**: adding remark-gfm (infrastructure change inside a
  content feature — forbidden by the feature's own rules; if tables become a
  recurring need, that is a separate feature); HTML `<table>` in MDX (verbose,
  fights prose styling).

## R4 — Exercise: the reader's SRS slice

- **Decision**: Exercise 1 — from the reader's two journey maps, extract candidate
  requirements: every ★ stage first (those become the top priorities), then
  supporting stages, into 8–15 rows using the docs/04 row format: stable ID with a
  family prefix the reader invents once (e.g. `VET-REM-01`), a shall-statement, a
  priority with a one-line phase rationale, exactly one T/D/I/A method. Exercise
  2 — the opinion hunt: for each row, write the single test/demonstration/
  inspection/analysis that could *fail* it; any row where nothing could fail is an
  opinion — rewrite or cut it. Worked examples: FR-MSG-04 (from Tuan) and a
  deliberately bad row ("the system shall be fast") repaired into a testable one.
  Self-checks (yes/no): every ★ produced a requirement with the top priority; every
  row has exactly one verification method; no row survives that nothing could fail;
  IDs form a stable scheme the reader could keep for years.
  **Rendering note (analysis I2)**: the bad-row repair renders as blockquote/prose
  before-and-after — never a fence; the ≤3 fence budget (R3) is reserved for the
  quoted specimen rows.
- **Rationale**: FR-006's fields; the "opinion hunt" operationalizes the chapter's
  thesis; the bad-row repair is the docs/07 failure-before-machinery rule applied
  to prose.
- **Alternatives considered**: asking for a full SRS (hours; the chapter budget is
  100 minutes); skipping the repair example (loses the most teachable moment).

## R5 — Vietnamese translation: register + identifier discipline

- **Decision**: Translate the final English file in the established register and
  glossary. **Requirement IDs, family prefixes, and the shall-keyword stay in
  English** (identifiers, not prose — spec FR-008): quoted rows keep `shall`
  with the Vietnamese gloss carried by surrounding prose; T/D/I/A named in English
  with Vietnamese expansions on first use (kiểm thử tự động / trình diễn / thanh
  tra / phân tích). Manifest vi title verbatim. Fence contents: the shall-statement
  *prose* inside quoted rows is translated, IDs/priority/method codes are not.
- **Rationale**: FR-008/SC-005; readers will meet these exact IDs in docs/04 and in
  Part 2's code — translating them would break the traceability the chapter
  teaches.
- **Alternatives considered**: fully translating quoted rows (breaks verbatim
  traceability; the reader could never grep docs/04 for what they read).

## R6 — What does NOT change

- **Decision**: No component/i18n/styling changes; 0.1–0.3 prose immutable; only
  the manifest entry plus two MDX files. Gaps surfaced, not patched.

## R7 — Verification: the chapter battery + the 0.3→0.4 pair

- **Decision**: The established battery (canonical word count, box counts en=vi,
  Checkpoint=1, hreflang, `div lang="vi"`, fence parity ≤3 blocks) plus: 0.3's
  footers link forward to 0.4 in both locales; 0.4's footers link back and show
  0.5 forthcoming with zero `href="[^"]*chapter-05` links; both landings link 0.4;
  quoted-row verbatim spot-check against docs/04 (SC-002). Manual: Dong's vi
  read-through; reading-time sanity vs 100 minutes.
