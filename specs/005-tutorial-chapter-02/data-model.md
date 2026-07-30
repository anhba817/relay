# Data Model: Tutorial Chapter 0.2

**Feature**: `specs/005-tutorial-chapter-02` · **Date**: 2026-07-30

No new entities — this feature exercises the existing series data model
(feature 002 E1/E2, extended by 004 E3). What changes and what the content must
contain:

## E1 — Manifest entry for chapter 0.2 (lib/tutorial.ts, one entry)

| Field | Before | After | Source |
|---|---|---|---|
| `status` | `"forthcoming"` | `"published"` | FR-008 |
| `translatedIn` | absent | `["vi"]` | FR-007/008 |
| `readerMinutes` | 75 | validated against the finished chapter (correct if off) | spec assumption |
| all other fields | — | unchanged (path/title/titleVi/readerProducesVi already reserved by 004) | research R1 |

**Downstream (automatic, zero edits)**: both landings render 0.2 as a link; 0.1's
footers (both locales) turn their next-card into a link; 0.2's footers show 0.1 as
previous and 0.3 as forthcoming next.

## E2 — Chapter 0.2 content structure (both page.mdx files)

| Element | Rule | Source |
|---|---|---|
| Metadata | title "Four people who will judge us — Building Relay" / vi: "Bốn người sẽ phán xét chúng ta — Building Relay"; descriptions per locale; hreflang alternates both directions | FR-001/007, 004 C4 |
| Shell | `<ChapterHeader id="0.2" [locale="vi"] />` first, `<ChapterFooter id="0.2" [locale="vi"] />` last | 002 C3, 004 C5 |
| Body arc | research R2's nine beats: cold open w/ 0.1 pointer → influence ordering → Mai → David → Priya → Tuan → trade-off resolution + E2E worked example → exercise → takeaways | FR-002/003 |
| Boxes | WHY ≥2 (citing "personas §…" sources), SKIP AHEAD ≥1 (early), ForwardRef ≥1 (Tuan's constraints → Part 2), CHECKPOINT exactly 1 (end; names the persona set before 0.3); vi file adds `locale="vi"` on every box | FR-004 |
| Exercise | derivation from reader's positioning statement; ≥3 personas with docs/02 field set; influence ordering with reasons; invisibility test; yes/no self-checks | FR-005, research R3 |
| Word count | 2,000–4,000 by the canonical procedure (en); vi mirrors structure, not count | FR-004, SC-001 |
| Parity | vi box counts per type == en; same section arc; exercise components preserved | SC-005 |

## E3 — Persona (the concept the chapter teaches — content, not code)

| Field | Rule | Source |
|---|---|---|
| Role in the product | user / buyer / operator / constraint — not a job title | docs/02 |
| Influence rank | explicit, with a stated reason per rank | docs/02 intro + trade-off section |
| Goals / frustrations / wins / loses | concrete, decision-relevant, no demographic filler | docs/02 field set |
| Invisibility flag | ≥1 persona never chooses or sees the product; their needs appear as design constraints | docs/02 persona 4 |
