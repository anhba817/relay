# Tasks: Tutorial Chapter 0.3 — Journeys, Where Products Die

**Input**: Design documents from `/specs/006-tutorial-chapter-03/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chapter-03-contract.md, quickstart.md

**Tests**: Not requested — verification is the scripted chapter battery (contract C4), quickstart scenarios, and `pnpm lint && pnpm build`. Vietnamese quality (quickstart V4) is Dong's read-through.

**Organization**: Tasks grouped by user story, on the pattern proven by feature 005: US1 (body) and US2 (exercise) share one MDX file, strictly sequential; US3 (translation) starts only from the final English file. The editorial guardrail this time: **compression** — 23 documented stages become a lesson about three ★s; cut breadth before cutting the anatomy or the ★ arguments (research R2).

**⚠ Standing instructions**: Do NOT run `git commit` / `git push` (Dong commits personally). Do NOT modify any component, i18n, or styling code — content + one manifest entry only; gaps are surfaced, not patched.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = read the chapter, US2 = reader artifacts, US3 = bilingual series integration

## Path Conventions

- App paths relative to `/home/dong/work/relay/relay-tutorial/`
- EN chapter (NEW): `app/part-0/chapter-03/journeys-where-products-die/page.mdx`
- VI chapter (NEW): `app/vi/part-0/chapter-03/journeys-where-products-die/page.mdx`
- Content sources: `/home/dong/work/relay/docs/03-journey-map.md` (journey facts), 0.1/0.2 artifacts (context), `docs/07` §2 (format rules)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: None — zero new dependencies; features 002–005 are the baseline.

*(no tasks)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The manifest flip every navigation surface reads from

- [x] T001 Flip chapter 0.3's manifest entry in relay-tutorial/lib/tutorial.ts per data-model E1: `status: "published"`, add `translatedIn: ["vi"]`; leave path/titleVi/readerProducesVi untouched (the vi title is the user-approved retranslation — binding); `pnpm build` passes; the brief 404-link window until content lands is expected — do NOT hand-edit navigation (SC-006)

---

## Phase 3: User Story 1 - Read chapter 0.3 and follow the derivation (Priority: P1) 🎯 MVP

**Goal**: The English chapter — stage anatomy, four journeys, and the three ★ moments deep-walked — live at its canonical address.

**Independent Test**: A reader who finished 0.2 can answer: the four journeys, why non-buyers get journeys, Mai's killer stage, and what a ★ moment is — without docs/03 (quickstart V3.1).

### Implementation for User Story 1

- [x] T002 [US1] Author the English chapter body in relay-tutorial/app/part-0/chapter-03/journeys-where-products-die/page.mdx per research R2 beats 1–7: metadata (title "Journeys — where products die — Building Relay", description, hreflang alternates per 004 C4); `<ChapterHeader id="0.3" />`; cold open (a persona is a portrait, a journey is that person in motion; 0.2-artifact pointer) + 1 `<SkipAhead>` early; the anatomy of a stage taught on Mai's Stage-2 Evaluate specimen (Doing/Thinking/Feeling/pain/opportunity/measure; reconnection-and-ordering docs as the strongest signal); Mai's eight stages compressed with ONE fenced flow diagram (★ under FIRST MESSAGE) and the emotional arc in prose, then the Stage-4 ★ deep-walk (under-ten-minutes, key-vs-token as the most common failure, live event stream converting anxiety to confidence, >60% target) with `<Why source="journeys — stage 4">`; David's approval path compressed (runs alongside, can stop the project; analytics gets the purchase approved) INCLUDING the mandatory exception note per research R2 beat 4 / analysis A1 — David's journey carries no ★ because his veto is continuous, which is why it maps as gates rather than stages; Priya's Tuesday with her ★ Reconstruct (never-sent / deleted / edited — and the four SRS decisions this stage justifies); Tuan's two minutes with ONE fenced flow diagram (★ under LOSE SIGNAL) and the ★ deep-walk ("the moment the platform was actually built for", the consumer-messenger expectation, jitter and the forty-driver herd, the no-feeling/one-star-review asymmetry) with `<ForwardRef part="Part 2">` (this journey scripted IS the Phase 1 exit criterion — the Tuan test, 2.8; Priya's Tuesday becomes the Part 4 milestone); the effort ranking + the closing distinction (adopts vs. deserves adoption) with `<Why source="journeys — closing">`; `<ChapterFooter id="0.3" />`; first-person plural present; every fact traceable to docs/03 (FR-006); ≤2 fenced blocks total, chapter readable without them (R3); leave ~700 words of budget for T004
- [x] T003 [US1] Add the skip-safe takeaways block (before the footer) per FR-004, then run the body-so-far checks (C4: `<Why` ≥2, `<SkipAhead` ≥1, `<ForwardRef` ≥1, takeaways ≥1, fence lines ≤4) and `pnpm build`

**Checkpoint**: US1 readable end to end at `/part-0/chapter-03/journeys-where-products-die`

---

## Phase 4: User Story 2 - Produce the chapter's reader artifacts (Priority: P2)

**Goal**: The exercise: the reader maps ≥2 journeys with one ★ each — including a single-interaction journey for an invisible persona.

**Independent Test**: The exercise alone yields two journey maps with ★s and reasons, self-checked yes/no (quickstart V3.4).

### Implementation for User Story 2

- [x] T004 [US2] Add the exercise section to relay-tutorial/app/part-0/chapter-03/journeys-where-products-die/page.mdx per research R4 (after the effort-ranking section, before takeaways): Exercise 1 — map the primary persona's journey from the reader's 0.2 set (5–8 named stages; per stage Doing/Thinking/Feeling + one pain point + one measure; the Stage-2 specimen as template); Exercise 2 — map ONE journey for a persona who never chooses the product, at single-interaction granularity (Tuan's tunnel as worked example: seconds, not weeks); then the ★ rule — exactly one per journey with the written reason "if this stage fails, the rest never happens"; yes/no self-checks per R4 (every stage has a feeling; exactly one ★ each with written reason; ≥1 journey for a persona who never signs up; ≥1 pain point per journey the reader's team could cause this quarter) (FR-005)
- [x] T005 [US2] Add the single closing `<Checkpoint>` (after takeaways, before the footer) naming the journey maps + ★ moments as required before chapter 0.4 (which turns them into requirements with IDs and verification methods), then run the full C4 file battery — canonical words 2,000–4,000, `<Why` ≥2, `<SkipAhead` ≥1, `<ForwardRef` ≥1, `<Checkpoint` exactly 1, takeaways ≥1 — adjust prose until all pass; `pnpm lint && pnpm build`

**Checkpoint**: English chapter complete and format-verified

---

## Phase 5: User Story 3 - The chapter takes its place in the bilingual series (Priority: P3)

**Goal**: The Vietnamese chapter in the established register; all bilingual navigation live.

**Independent Test**: 0.3 reachable in ≤2 steps from either landing; 0.2→0.3 links live both locales; switcher maps 0.3↔0.3; parity passes (quickstart V2).

### Implementation for User Story 3

- [x] T006 [US3] Author the Vietnamese chapter in relay-tutorial/app/vi/part-0/chapter-03/journeys-where-products-die/page.mdx per research R5 and 004 C5: translate the FINAL English file in the established storytelling register with glossary continuity (tuyên ngôn định vị, mũi nêm (wedge), đẳng xâm (idempotent), nhật ký vết (audit trail); dev terms English: backfill, cursor, retry, jitter, idempotency key — thundering herd with a Vietnamese gloss); translate the stage labels INSIDE the two fenced flow diagrams (display strings, not code — e.g. KHÁM PHÁ → ĐÁNH GIÁ → …, ★ positions preserved); persona names unchanged; `locale="vi"` on shell and every box; vi metadata title "Hành trình — nơi những sản phẩm gục ngã — Building Relay" (manifest title verbatim) + description + hreflang alternates; identical section arc, box counts, and fence counts (SC-005)
- [x] T007 [US3] Verify bilingual integration per quickstart V2 live checks: hreflang ≥2 (case-insensitive) on both 0.3 pages; `div lang="vi"` only on vi; 0.2's footers link forward to 0.3 in matching locales; 0.3's footers link back to 0.2 and show 0.4 as forthcoming with `href="[^"]*chapter-04` count == 0; both landings link 0.3; switcher maps 0.3↔0.3; `pnpm lint && pnpm build`; fix gaps

**Checkpoint**: All three user stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full validation and handoff

- [x] T008 Run the complete quickstart V1–V5 for specs/006-tutorial-chapter-03/quickstart.md: route table (V1), full scripted battery incl. fence parity (V2), manual fidelity pass — 5 journey facts spot-checked, diagrams render light+dark AND the chapter reads with them skipped, navigation walk both locales, exercise dry-run (V3), reading-time sanity vs `readerMinutes: 90` with manifest correction if materially off (V5); record results; V4 (Vietnamese read-through) is Dong's — request prominently in the handoff
- [x] T009 Handoff (NO commits — standing instruction): report ready-to-commit files for relay-tutorial (new: both chapter-03 page.mdx files; modified: lib/tutorial.ts) with a suggested commit message; request Dong's V4 read-through before committing; note parent-repo follow-ups (spec artifacts, CLAUDE.md pointer, submodule pin)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: empty
- **Foundational (Phase 2)**: T001 first (2-minute flip; brief expected-404 window)
- **US1 (Phase 3)**: T002 → T003 (same file)
- **US2 (Phase 4)**: T004 → T005 (same file, after US1)
- **US3 (Phase 5)**: T006 strictly after T005 (final en file = translation source); T007 after T006
- **Polish (Phase 6)**: T008 after all; T009 last

### User Story Dependencies

- **US1 (P1)**: T001 only — the MVP
- **US2 (P2)**: US1 (same file, shared arc and word budget)
- **US3 (P3)**: US2 complete

### Parallel Opportunities

None — the proven single-narrative content pipeline. Honest schedule: T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009.

## Parallel Example

```bash
# Serial by design (same as feature 005):
# T001 → T002→T003 (en) → T004→T005 (exercise+checkpoint) → T006 (vi) → T007 → T008 → T009
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. T001 + T002–T003 — the ★-lesson chapter readable in English
2. **STOP and VALIDATE**: anatomy + three ★ deep-walks land

### Incremental Delivery

1. US1 → the argument readable end to end
2. US2 → exercise + checkpoint → chapter complete per docs/07's contract
3. US3 → Vietnamese version + bilingual navigation live
4. Polish → full battery; request Dong's read-through; handoff

---

## Notes

- The hardest constraint is compression (research R2): 23 stages → three ★ deep-walks + anatomy. If the draft runs past ~3,200 words, cut journey breadth — never the anatomy specimen, the ★ arguments, or the closing distinction
- Diagram discipline (R3): exactly the two stage-flow fences, ★ marked; the ASCII emotional-arc plot stays in docs/03; the chapter must read with all fences skipped
- The manifest's vi title is binding — do not re-translate it in the chapter files
- NO git commit / git push — Dong commits personally; V4 review requested before commit
