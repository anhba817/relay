# Research: Tutorial Chapter 0.3 — Journeys, Where Products Die

**Feature**: `specs/006-tutorial-chapter-03` · **Date**: 2026-07-30

Grounded in docs/03-journey-map.md (read in full; unchanged by the product-vision
commit), docs/07 §3, and the pattern proven by features 005 (chapter 0.2). The
machinery exists; the decisions are editorial.

## R1 — Manifest: one entry flip, everything else reserved

- **Decision**: Flip 0.3 to `status: "published"`, add `translatedIn: ["vi"]`,
  validate `readerMinutes` (90). Path
  (`/part-0/chapter-03/journeys-where-products-die`), `titleVi` ("Hành trình — nơi
  những sản phẩm gục ngã", user-approved retranslation), and `readerProducesVi` are
  already in the manifest — binding, not re-translated (spec edge case).
- **Rationale**: The 004 C5 contract, third exercise of it.
- **Alternatives considered**: none needed.

## R2 — English chapter: teach the method deep, the map wide

docs/03 is 546 lines — 8+4+6+5 stages. A 2,000–4,000-word chapter cannot walk them
all at depth and must not try (it would become a summary, not a lesson).

- **Decision**: The chapter teaches the *anatomy* and the *★ discipline* by walking
  three stages deeply and compressing the rest:
  1. **Cold open** — a persona is a portrait; a journey is that person in motion.
     0.2-artifact pointer for skippers; SKIP AHEAD box early.
  2. **The anatomy of a stage** — Doing / Thinking / Feeling / pain points /
     opportunities / a measure — using Mai's Stage 2 (Evaluate, "the most
     under-served stage in this category") as the specimen: skeptical reading,
     reconnection-and-ordering docs as the strongest signal, publish-the-reference
     opportunity.
  3. **Mai, compressed + her ★** — the eight stages as a one-line flow with the
     emotional arc described in prose (two dips: pricing reality, first-message
     anxiety); then the Stage 4 ★ deep-walk: "the stage that decides everything",
     under-ten-minutes target, the key-vs-token confusion as the single most common
     failure, the live event stream converting anxiety into confidence, the >60%
     first-message target. First WHY box (journeys — stage 4).
  4. **David, briefly** — the journey that runs alongside and can stop the project;
     his four phases as a compact table-in-prose; the design implication that
     analytics features get the purchase approved.
     **Mandatory exception note (analysis A1)**: the chapter MUST address why
     David's journey carries no ★ where the other three do — his power is a
     continuous veto across every phase, not a single deciding moment, which is
     exactly why docs/03 maps his journey as *gates* (blocks-on / unblocked-by)
     rather than stages. Naming the exception preempts the sharp reader's "what's
     David's ★?" and deepens the lesson: some stakeholders decide at a moment;
     buyers decide continuously.
  5. **Priya's Tuesday + her ★** — the dispute scenario; ★ = Reconstruct: three
     possibilities (never sent / sent-and-deleted / sent-and-edited) and why a
     history model that cannot distinguish them is useless; the four SRS decisions
     this one stage justifies (tombstones, immutable edit history, server sequence
     numbers, moderator history access).
  6. **Tuan's two minutes + his ★** — "B2, north ramp" as the signal dies; ★ = Lose
     Signal, "the moment the platform was actually built for"; the consumer-messenger
     expectation held against a two-person team; the invisible reconnect (jitter and
     the forty-driver thundering herd, cursor backfill, idempotent flush); the
     asymmetry — perfect execution produces no feeling, bad execution produces a
     one-star review of *someone else's app*. ForwardRef → Part 2: this journey,
     scripted, is the Phase 1 exit criterion (the Tuan test, 2.8); Priya's Tuesday
     becomes the Part 4 milestone.
  7. **Where to concentrate effort** — the ranking (first message, public docs,
     request log, usage attribution, environment isolation) and the closing
     distinction: Mai's journey decides whether anyone adopts; Priya's and Tuan's
     decide whether it *deserves* adoption. Second WHY box (journeys — closing).
  8. **Exercise** (R4), **takeaways**, **CHECKPOINT**.
- **Rationale**: FR-002/003 require the four journeys and the ★ concept, not stage
  completeness; the three deep-walked stages are exactly the three ★s (SC-001's box
  economy also fits this shape). Budget ~2,300 body + ~700 exercise.
- **Alternatives considered**: walking all stages (a 6,000-word summary — fails both
  the word budget and the pedagogy); teaching only Mai's journey (loses the
  chapter's distinctive lesson, the non-buyer journeys).

## R3 — Diagrams: monospace stage-flows, prose for the emotional arc

- **Decision**: Reproduce the compact stage-sequence diagrams as fenced code blocks
  (Mai's eight-stage flow with the ★ under FIRST MESSAGE; Tuan's five-stage flow
  with the ★ under LOSE SIGNAL) — language-neutral arrows, stage labels translated
  in the vi file. Do NOT reproduce the ASCII emotional-arc plot; describe the arc in
  one prose sentence per dip. The chapter must read correctly with all code blocks
  skipped (spec edge case).
- **Rationale**: Fenced blocks render in `prose` styling in both themes with zero
  new machinery; the emotional-arc plot is too wide/fragile for mobile and adds
  nothing prose can't carry.
- **Alternatives considered**: SVG/image figures (asset pipeline + bilingual
  variants for decoration — violates the no-new-machinery rule); reproducing all
  four docs/03 diagrams (clutter).

## R4 — Exercise: map two journeys, one ★ each, invisible persona required

- **Decision**: Exercise 1 — pick the primary persona from the reader's 0.2 set and
  map their journey: name 5–8 stages, and for each record Doing / Thinking /
  Feeling / one pain point / one measure (the Stage-2 specimen as the worked
  template). Exercise 2 — map one journey for a persona who never chooses the
  product (Tuan's tunnel as the worked example), at the granularity where the
  product earns or loses trust (a single interaction, not a lifecycle). Then the ★
  rule: mark exactly one stage per journey with the stated reason "if this stage
  fails, the rest never happens". Self-checks (yes/no): every stage has a
  feeling, not just actions; each journey has exactly one ★ with a written reason;
  ≥1 journey belongs to a persona who never signs up; at least one pain point per
  journey is something the reader's team could cause this quarter.
- **Rationale**: FR-005's fields; the single-interaction granularity for the
  invisible journey is docs/03's own move (Tuan's journey "is measured in seconds")
  and the thing readers won't do instinctively.
- **Alternatives considered**: full 8-stage maps for every persona (hours of
  homework; the chapter's stated budget is ~90 minutes total).

## R5 — Vietnamese translation: established register, translated stage labels

- **Decision**: Translate the final English file per the established storytelling
  register and glossary (tuyên ngôn định vị, non-goals, đẳng xâm (idempotent), nhật
  ký vết (audit trail); dev terms English: backfill, cursor, retry, jitter,
  idempotency key, thundering herd với giải nghĩa). Stage labels inside the fenced
  flow diagrams are translated (KHÁM PHÁ → ĐÁNH GIÁ → …) since they are reader-facing
  labels, not code. Manifest `titleVi` used as-is. Persona names unchanged.
- **Rationale**: FR-007; the diagram-label rule follows the translate-mdx guide's
  "translate display strings, preserve syntax".
- **Alternatives considered**: keeping English stage labels in vi diagrams
  (undermines FR-007's no-mixed-chrome spirit inside content).

## R6 — What does NOT change

- **Decision**: No component/i18n/styling changes; 0.1/0.2 prose immutable; only
  the manifest entry plus two new MDX files. Gaps surfaced, not patched.
- **Rationale**: SC-006; third consecutive proof of the machinery.

## R7 — Verification: the chapter battery + the 0.2→0.3 pair

- **Decision**: The established scripted battery (canonical word count, box counts
  en=vi with Checkpoint=1, hreflang, `div lang="vi"` scoping) plus: 0.2's footers
  link forward to 0.3 in both locales; 0.3's footers link back to 0.2 and show 0.4
  forthcoming with zero `href` links (the C4-aligned grep from feature 005's I1
  remediation); both landings link 0.3. Manual: Dong's vi read-through; reading-time
  sanity vs 90 minutes.
- **Rationale**: Same rigor as 005; the new pair tests what publishing 0.3 changes.
