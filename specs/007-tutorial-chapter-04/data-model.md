# Data Model: Tutorial Chapter 0.4

**Feature**: `specs/007-tutorial-chapter-04` · **Date**: 2026-07-30

No new entities — fourth exercise of the series data model.

## E1 — Manifest entry for chapter 0.4 (lib/tutorial.ts, one entry)

| Field | Before | After | Source |
|---|---|---|---|
| `status` | `"forthcoming"` | `"published"` | FR-009 |
| `translatedIn` | absent | `["vi"]` | FR-008/009 |
| `readerMinutes` | 100 | validated against the finished chapter | spec assumption |
| all other fields | — | unchanged (path, titleVi "Những yêu cầu bạn có thể kiểm chứng", readerProducesVi) | R1 |

**Downstream (automatic)**: both landings link 0.4; 0.3's footers gain the live
next-link; 0.4's footers show 0.3 previous and 0.5 forthcoming.

## E2 — Chapter 0.4 content structure (both page.mdx files)

| Element | Rule | Source |
|---|---|---|
| Metadata | en title "Requirements you can test — Building Relay"; vi title from manifest verbatim + " — Building Relay"; per-locale descriptions; hreflang both directions | FR-001/008 |
| Shell | `<ChapterHeader id="0.4" [locale="vi"] />` / `<ChapterFooter id="0.4" [locale="vi"] />` | 002 C3, 004 C5 |
| Body arc | R2's eight beats: cold open (testable-or-opinion) → row anatomy on FR-MSG-04 + T/D/I/A vocabulary → ledger discipline (IDs, P1–P5, 224 sequenced) → Tuan trace → Priya trace + FR-TEN-05 → FR-MED change beat → exercise → takeaways | FR-002..005 |
| Specimen rows | Quoted verbatim from docs/04, rendered in ≤3 fenced blocks; NO pipe tables (no GFM); chapter readable without fences; IDs never invented or renumbered | FR-007, R3, spec edge case |
| Boxes | WHY ≥2 (traceability tables; the FR-MED/change argument), SKIP AHEAD ≥1, ForwardRef ≥1 (requirements → Part 2 chapters + milestone tests), CHECKPOINT exactly 1; vi adds `locale="vi"` | FR-005 |
| Exercise | 8–15-row slice from the reader's journey maps (★ → top priority; family-prefix ID scheme; shall; priority+rationale; one T/D/I/A each) + the opinion hunt (a test that could fail each row; the "shall be fast" repair) + yes/no self-checks | FR-006, R4 |
| Word count | 2,000–4,000 canonical (en) | FR-005, SC-001 |
| Parity | vi box/fence counts == en; same arc; IDs + `shall` + T/D/I/A codes in English in vi | SC-005, R5 |

## E3 — Requirement (the concept the chapter teaches — content, not code)

| Field | Rule | Source |
|---|---|---|
| ID | Stable, never reused; family prefix groups related requirements | docs/04 §1.4 |
| Statement | Uses **shall** for obligations; concrete object and outcome | docs/04 §1.4 |
| Priority | P1–P5 aligned to the phased roadmap ("sequenced, not simultaneous") | docs/04 §1.4, Appendix A |
| Verification | Exactly one primary method: T / D / I / A — the answer to "how would we know?" | docs/04 §1.4 |
| Traceability | Maps to personas (§7.1) and journey stages (§7.2); ★ stages produce the P1s | docs/04 §7, chapter 0.3 |
