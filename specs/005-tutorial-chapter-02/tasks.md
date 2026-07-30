# Tasks: Tutorial Chapter 0.2 — Four People Who Will Judge Us

**Input**: Design documents from `/specs/005-tutorial-chapter-02/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chapter-02-contract.md, quickstart.md

**Tests**: Not requested — verification is the scripted chapter battery (contract C4), quickstart scenarios, and `pnpm lint && pnpm build`. Vietnamese quality (quickstart V4) is Dong's read-through.

**Organization**: Tasks grouped by user story. US1 (chapter body) and US2 (exercise) share one MDX file — sequential by design, one narrative arc, one word budget. US3 (translation + bilingual integration) starts only after the English chapter is final: the en file is the translation's single source.

**⚠ Standing instructions**: Do NOT run `git commit` / `git push` (Dong commits personally). Do NOT modify any component, i18n, or styling code — this feature is content + one manifest entry (research R5); a discovered infrastructure gap is surfaced, not patched here.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = read the chapter, US2 = reader artifacts, US3 = bilingual series integration

## Path Conventions

- App paths relative to `/home/dong/work/relay/relay-tutorial/`
- EN chapter (NEW): `app/part-0/chapter-02/four-people-who-will-judge-us/page.mdx`
- VI chapter (NEW): `app/vi/part-0/chapter-02/four-people-who-will-judge-us/page.mdx`
- Content sources: `/home/dong/work/relay/docs/02-personas.md` (persona facts), `docs/01` + chapter 0.1 (positioning context), `docs/07` §2 (format rules)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: None — zero new dependencies; features 002–004 are the baseline.

*(no tasks)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The manifest flip every navigation surface and both chapter shells read from

- [x] T001 Flip chapter 0.2's manifest entry in relay-tutorial/lib/tutorial.ts per data-model E1: `status: "published"`, add `translatedIn: ["vi"]`; leave path/title/titleVi/readerProducesVi untouched; `pnpm build` passes; note (expected, temporary): both landings and 0.1's footers now link to a route that 404s until T002/T006 land — verify the links appear (SC-006 proof) and move on immediately

---

## Phase 3: User Story 1 - Read chapter 0.2 and follow the derivation (Priority: P1) 🎯 MVP

**Goal**: The English chapter — personas derived from 0.1's artifacts, the influence ordering with reasons, the invisible end user as protocol constraints — live at its canonical address.

**Independent Test**: A reader who finished 0.1 can answer who the four people are, who is primary and why, who the buyer is, and why the end user is a constraint — without docs/02 (quickstart V3.1).

### Implementation for User Story 1

- [x] T002 [US1] Author the English chapter body in relay-tutorial/app/part-0/chapter-02/four-people-who-will-judge-us/page.mdx per research R2 beats 1–7: metadata (title "Four people who will judge us — Building Relay", description, hreflang alternates en/vi both paths per 004 C4); `<ChapterHeader id="0.2" />` first; cold open with the 0.1 pointer for skippers + 1 `<SkipAhead>` early; the influence-ordering argument (user/payer/beneficiary are three different people — docs/02 intro); Mai (primary-persona rule, evaluation ritual as requirements-in-disguise) with a `<Why source="personas §1">` box; David (buy-versus-regret, veto power); Priya (served through Mai; tombstones/edit history exist because of her); Tuan (never hears the name Relay; his five protocol constraints) with a `<ForwardRef part="Part 2">` box tying the constraint list to chapters 2.3/2.7/2.8; the trade-off resolution order + the E2E worked example with a second `<Why source="personas — trade-offs">` box echoing 0.1's reasons-recorded lesson — and the MANDATORY reconciliation of the two orderings (influence: Tuan last; conflict resolution: Tuan first) per research R2 beat 7 / analysis A1: the invisible user has no voice, so his needs are promoted to constraints that win every conflict; close with `<ChapterFooter id="0.2" />`; first-person plural present tense; every persona fact traceable to docs/02 (FR-006); leave ~700 words of the 2,000–4,000 budget for T004's exercise
- [x] T003 [US1] Add the skip-safe takeaways block to the same file (before the footer) per FR-004, then run the body-so-far scripted checks (contract C4: `<Why` ≥2, `<SkipAhead` ≥1, `<ForwardRef` ≥1, takeaways present) and `pnpm build` — the en route renders

**Checkpoint**: US1 readable end to end at `/part-0/chapter-02/four-people-who-will-judge-us`

---

## Phase 4: User Story 2 - Produce the chapter's reader artifacts (Priority: P2)

**Goal**: The exercise that turns the essay into a chapter: the reader derives their own persona set, including the invisible persona.

**Independent Test**: The exercise alone suffices to produce ≥3 personas (one invisible) with an influence ordering, self-checked yes/no (quickstart V3.3).

### Implementation for User Story 2

- [x] T004 [US2] Add the exercise section to relay-tutorial/app/part-0/chapter-02/four-people-who-will-judge-us/page.mdx per research R3 (after the trade-off section, before takeaways): Exercise 1 — derive candidate people from the reader's own 0.1 positioning statement (who integrates / pays / operates / merely experiences), write ≥3 personas with the docs/02 field set (role in the product, goals, frustrations, wins/loses) plus an influence ordering with a stated reason per rank, Relay's four as the worked example; Exercise 2 — the invisibility test: name the persona who never chooses the product and write the constraints they impose (Tuan's list as the worked example); yes/no self-checks per R3 (ordering has reasons not seniority; personas derivable from positioning; ≥1 never signs up; each "loses them" is an accident the team could actually commit) (FR-005)
- [x] T005 [US2] Add the single closing `<Checkpoint>` (after takeaways, before the footer) naming the persona set as required in hand before chapter 0.3 (which derives journeys from it), then run the full contract C4 file battery — canonical word count 2,000–4,000, `<Why` ≥2, `<SkipAhead` ≥1, `<ForwardRef` ≥1, `<Checkpoint` exactly 1, takeaways ≥1 — adjusting prose until all pass; `pnpm lint && pnpm build`

**Checkpoint**: English chapter complete and format-verified — US1 and US2 testable

---

## Phase 5: User Story 3 - The chapter takes its place in the bilingual series (Priority: P3)

**Goal**: The Vietnamese chapter in the established storytelling register; all bilingual navigation live.

**Independent Test**: From either landing reach 0.2 in ≤2 steps in that language; 0.1→0.2 forward links work in both locales; vi↔en switcher maps 0.2 to 0.2; parity checks pass (quickstart V2).

### Implementation for User Story 3

- [x] T006 [US3] Author the Vietnamese chapter in relay-tutorial/app/vi/part-0/chapter-02/four-people-who-will-judge-us/page.mdx per research R4 and 004 contract C5: translate the FINAL English file (single source) in the storytelling register established by the approved 0.1 translation — expressive narrative Vietnamese, dev terms in English (non-goals, threads, retry, backfill, scope), glossary continuity (tuyên ngôn định vị, mũi nêm (wedge), đẳng xâm (idempotent), nhật ký vết (audit trail)); persona names Mai/David/Priya/Tuan unchanged (spec edge case); `locale="vi"` on ChapterHeader/ChapterFooter and every box; vi metadata (title "Bốn người sẽ phán xét chúng ta — Building Relay", description) + hreflang alternates; identical section arc and box counts per type (SC-005)
- [x] T007 [US3] Verify bilingual integration per quickstart V2's live checks: hreflang (case-insensitive grep) ≥2 on both 0.2 pages; `div lang="vi"` only on the vi page; 0.1's footers link forward to 0.2 in the matching locale (both); 0.2's footers link back to 0.1 and show 0.3 as a forthcoming NON-link (zero chapter-03 hrefs); both landings link 0.2; language switcher maps 0.2↔0.2; `pnpm lint && pnpm build`; fix gaps found

**Checkpoint**: All three user stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full validation and handoff

- [x] T008 Run the complete quickstart V1–V5 for specs/005-tutorial-chapter-02/quickstart.md: route table (V1), full scripted battery (V2), manual content-fidelity pass — 5 persona facts spot-checked against docs/02, derivation-not-profile-cards, navigation walk in both locales (V3), reading-time sanity vs `readerMinutes: 75` and correct the manifest if materially off (V5); record results; V4 (Vietnamese read-through) is Dong's — request it prominently in the handoff
- [x] T009 Handoff (NO commits — standing instruction): report ready-to-commit files for relay-tutorial (new: both chapter page.mdx files; modified: lib/tutorial.ts) with a suggested commit message; request Dong's V4 read-through before committing; note parent-repo follow-ups (spec artifacts, CLAUDE.md pointer, then the submodule pin)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: empty
- **Foundational (Phase 2)**: T001 first — quick, and its temporary-404 window ends as soon as T002 lands
- **US1 (Phase 3)**: T002 → T003 (same file)
- **US2 (Phase 4)**: T004 → T005 (same file, after US1 — shared narrative arc and word budget)
- **US3 (Phase 5)**: T006 strictly after T005 (the final English file is the translation's single source); T007 after T006
- **Polish (Phase 6)**: T008 after all; T009 last

### User Story Dependencies

- **US1 (P1)**: T001 only — the MVP
- **US2 (P2)**: US1 (same file, same arc)
- **US3 (P3)**: US2 complete (translation source must be final)

### Parallel Opportunities

Effectively none — this feature is a single-narrative content pipeline: one English file written in order, then its translation. T001 is the only task that could interleave (it's a 2-minute flip; do it first). The honest schedule is strictly serial: T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009.

## Parallel Example

```bash
# Serial by design:
# T001 (manifest flip) → T002→T003 (en body) → T004→T005 (exercise+checkpoint)
#   → T006 (vi translation of the FINAL en file) → T007 (bilingual verify)
#   → T008 (full quickstart) → T009 (handoff)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. T001 (manifest flip) + T002–T003 (English body + takeaways)
2. **STOP and VALIDATE**: the derivation chapter renders and reads — demonstrable MVP (en only, exercise pending)

### Incremental Delivery

1. US1 → the argument readable end to end
2. US2 → exercise + checkpoint → chapter complete per docs/07's "reader produces" contract
3. US3 → Vietnamese version + all bilingual navigation live
4. Polish → full battery; request Dong's read-through; handoff for commits

---

## Notes

- The hardest constraints are editorial: FR-006 (100% persona-fact traceability to docs/02) and US1/AC1's "derivation, not four pasted profile cards" — the personas must *emerge* from 0.1's positioning statement
- T001's temporary-404 window is deliberate and brief; do not "fix" it by hand-editing navigation (SC-006 forbids exactly that)
- Chapter 0.1's prose files are immutable; its footers updating is the manifest working as designed
- NO git commit / git push anywhere — Dong commits personally; Vietnamese quality review (V4) is requested before commit
