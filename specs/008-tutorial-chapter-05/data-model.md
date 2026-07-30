# Data Model: Tutorial Chapter 0.5

**Feature**: `specs/008-tutorial-chapter-05` · **Date**: 2026-07-30

No new entities — the fifth and final Part 0 exercise of the series data model.

## E1 — Manifest entry for chapter 0.5 (lib/tutorial.ts, one entry)

| Field | Before | After | Source |
|---|---|---|---|
| `status` | `"forthcoming"` | `"published"` | FR-009 |
| `translatedIn` | absent | `["vi"]` | FR-008/009 |
| `readerMinutes` | 110 | validated against the finished chapter | spec assumption |
| all other fields | — | unchanged (path, titleVi "Quyết định thành tiếng — bản SAD và thói quen viết ADR", readerProducesVi) | R1 |

**Downstream (automatic)**: both landings show five linked Part 0 chapters, zero
forthcoming badges in Part 0; 0.4's footers gain the live next-link; 0.5's footers
show 0.4 previous and **no next card** (`nextChapter("0.5")` is empty — the
last-chapter state, verified per R6).

## E2 — Chapter 0.5 content structure (both page.mdx files)

| Element | Rule | Source |
|---|---|---|
| Metadata | en title "Deciding out loud — Building Relay" (main clause + series); vi title from manifest verbatim + " — Building Relay"; per-locale descriptions; hreflang both directions | FR-001/008 |
| Shell | `<ChapterHeader id="0.5" [locale="vi"] />` / `<ChapterFooter id="0.5" [locale="vi"] />` | 002 C3, 004 C5 |
| Body arc | R2's beats: cold open (promises → how we keep them) → drivers distillation (D1, D8) → ADR anatomy on ADR-03 + two-document split + immutability → "attack the driver, not the choice" → ADR-13/14 chain-close → "reading the fourteen together" → exercise → takeaways → Part 0-closing checkpoint | FR-002..006 |
| Specimen fences | ≤3 (D1+D8 rows; ADR-03 core; ADR-13 core), the 007 verbatim definition; no pipe tables; readable without fences | FR-007, R3 |
| Boxes | WHY ≥2 (the drivers-mechanical argument; every-decision-names-its-own-undoing), SKIP AHEAD ≥1, ForwardRef ≥1 (ADRs → Parts 1–7 chapters), CHECKPOINT exactly 1 (closes Part 0, points to Part 1); vi adds `locale="vi"` | FR-005 |
| Exercise | 3–6-row drivers table (requirement-ID-sourced, consequence per row, one D8-style context driver permitted) + two from-scratch ADRs (full anatomy, ≥2 rejected-with-reasons, observable reversal condition) + yes/no self-checks | FR-006, R4 |
| Word count | 2,000–4,000 canonical (en) | FR-005, SC-001 |
| Parity | vi box/fence counts == en; identifiers English; fences English + gloss | FR-008 / US3-AS3, R5 |

## E3 — Architectural driver (the concept taught — content, not code)

| Field | Rule | Source |
|---|---|---|
| Statement | The requirement (or honest context) that shapes structure | docs/05 §2 |
| Source | Requirement IDs it distills — or declared context (D8 pattern) | docs/05 §2 |
| Consequence | The architectural shape it forces, in one line | docs/05 §2 table |

## E4 — ADR (the concept taught — content, not code)

| Field | Rule | Source |
|---|---|---|
| Status + immutability | accepted/superseded; accepted ADRs never edited — superseding = new ADR | docs/05 §1.4 |
| Drivers | Named D-references the decision serves | docs/05 §9 |
| Decision + trade-offs | What was chosen and what cost was knowingly accepted | docs/05 §9 |
| Rejected alternatives | ≥2, each with the reason — the teammate-reconstruction test | docs/06 |
| Reversal condition | Observable trigger; "every decision names its own undoing" | docs/06 closing |
