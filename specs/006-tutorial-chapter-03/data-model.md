# Data Model: Tutorial Chapter 0.3

**Feature**: `specs/006-tutorial-chapter-03` · **Date**: 2026-07-30

No new entities — the third exercise of the series data model (002 E1/E2, 004 E3).

## E1 — Manifest entry for chapter 0.3 (lib/tutorial.ts, one entry)

| Field | Before | After | Source |
|---|---|---|---|
| `status` | `"forthcoming"` | `"published"` | FR-008 |
| `translatedIn` | absent | `["vi"]` | FR-007/008 |
| `readerMinutes` | 90 | validated against the finished chapter | spec assumption |
| all other fields | — | unchanged (path, titleVi "Hành trình — nơi những sản phẩm gục ngã", readerProducesVi — all reserved/approved) | R1, spec edge case |

**Downstream (automatic)**: both landings link 0.3; 0.2's footers gain the live
next-link; 0.3's footers show 0.2 previous and 0.4 forthcoming.

## E2 — Chapter 0.3 content structure (both page.mdx files)

| Element | Rule | Source |
|---|---|---|
| Metadata | en title "Journeys — where products die — Building Relay" (main clause + series); vi title "Hành trình — nơi những sản phẩm gục ngã — Building Relay"; per-locale descriptions; hreflang alternates both directions | FR-001/007 |
| Shell | `<ChapterHeader id="0.3" [locale="vi"] />` / `<ChapterFooter id="0.3" [locale="vi"] />` | 002 C3, 004 C5 |
| Body arc | R2's nine beats: cold open → stage anatomy (Mai Stage-2 specimen) → Mai compressed + ★ first message → David briefly → Priya + ★ reconstruct → Tuan + ★ lose signal → effort ranking + adoption/deserving close → exercise → takeaways | FR-002/003 |
| Diagrams | ≤2 fenced code blocks (Mai's 8-stage flow, Tuan's 5-stage flow), ★ marked; emotional arc in prose only; chapter readable with blocks skipped; vi file translates stage labels | R3, spec edge case |
| Boxes | WHY ≥2 (stage-4 argument; the closing adoption/deserving argument), SKIP AHEAD ≥1 early, ForwardRef ≥1 (journeys → the Tuan test 2.8 / Priya milestone Part 4), CHECKPOINT exactly 1; vi adds `locale="vi"` everywhere | FR-004 |
| Exercise | primary-persona journey map (5–8 stages, anatomy fields) + single-interaction journey for an invisible persona + the one-★-per-journey rule with written reason + yes/no self-checks | FR-005, R4 |
| Word count | 2,000–4,000 canonical (en); vi mirrors structure | FR-004, SC-001 |
| Parity | vi box counts == en per type; same arc; exercise preserved | SC-005 |

## E3 — Journey map (the concept the chapter teaches — content, not code)

| Field | Rule | Source |
|---|---|---|
| Stages | Named sequence; per stage: Doing / Thinking / Feeling / pain / opportunity / measure | docs/03 stage anatomy |
| Granularity | Lifecycle for choosers (Mai); a single interaction for the invisible persona (Tuan: one message under bad conditions) | docs/03 journeys 1 & 4 |
| ★ moment | Exactly one per journey; the stage where the journey is decided; stated reason | docs/03 ★ convention + closing |
| Non-buyer journeys | Mapped even though they never purchase — they are where the hard requirements come from | docs/03 intro |
