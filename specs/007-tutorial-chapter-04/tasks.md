# Tasks: Tutorial Chapter 0.4 — Requirements You Can Test

**Input**: Design documents from `/specs/007-tutorial-chapter-04/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chapter-04-contract.md, quickstart.md

**Tests**: Not requested — verification is the scripted chapter battery (contract C4, now including the invented-ID detector and the no-pipe-tables check), quickstart scenarios, and `pnpm lint && pnpm build`. Vietnamese quality (quickstart V4) is Dong's read-through.

**Organization**: The proven chapter pipeline (features 005/006): US1 (body) and US2 (exercise) share one MDX file, strictly sequential; US3 (translation) starts from the final English file. This chapter's distinctive guardrails: **quote fidelity** (every requirement row verbatim from the current docs/04 — greppable; never paraphrase next to an ID) and **no pipe tables** (no GFM — specimen rows in ≤3 fenced blocks).

**⚠ Standing instructions**: Do NOT run `git commit` / `git push` (Dong commits personally). Do NOT modify any component, i18n, or styling code; gaps are surfaced, not patched.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = read the chapter, US2 = reader artifacts, US3 = bilingual series integration

## Path Conventions

- App paths relative to `/home/dong/work/relay/relay-tutorial/`
- EN chapter (NEW): `app/part-0/chapter-04/requirements-you-can-test/page.mdx`
- VI chapter (NEW): `app/vi/part-0/chapter-04/requirements-you-can-test/page.mdx`
- Content source: `/home/dong/work/relay/docs/04-srs.md` (CURRENT media-inclusive revision — quote verbatim), 0.1–0.3 artifacts (context), docs/07 §2 (format rules)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: None — zero new dependencies; features 002–006 are the baseline.

*(no tasks)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The manifest flip every navigation surface reads from

- [x] T001 Flip chapter 0.4's manifest entry in relay-tutorial/lib/tutorial.ts per data-model E1: `status: "published"`, add `translatedIn: ["vi"]`; leave path/titleVi/readerProducesVi untouched; `pnpm build` passes; the brief 404-link window is expected — do NOT hand-edit navigation (SC-006)

---

## Phase 3: User Story 1 - Read chapter 0.4 and follow the derivation (Priority: P1) 🎯 MVP

**Goal**: The English chapter — requirement anatomy, T/D/I/A, two journey traces, FR-TEN-05, and the FR-MED change beat — live at its canonical address.

**Independent Test**: A reader who finished 0.3 can answer: what makes a requirement testable, the four verification methods, how priorities map to phases, the SRS's most important requirement, and where ★ moments went — without docs/04 (quickstart V3.1).

### Implementation for User Story 1

- [x] T002 [US1] Author the English chapter body in relay-tutorial/app/part-0/chapter-04/requirements-you-can-test/page.mdx per research R2 beats 1–6: metadata (title "Requirements you can test — Building Relay", description, hreflang alternates per 004 C4); `<ChapterHeader id="0.4" />`; cold open — journey maps are stories and stories don't gate releases; thesis: *a requirement without a test plan is an opinion*; 0.3-artifact pointer + 1 `<SkipAhead>` early; the anatomy of a requirement on the FR-MSG-04 specimen (quoted VERBATIM in a fenced block: ID · shall-statement · P1 · T) then the T/D/I/A vocabulary each with a real example — FR-MSG-04 (T), FR-DSH-01 (D), EIR-API-07 (I), FR-MSG-06 (A — why "an acknowledged message shall not be lost" needs analysis, not one test run) — and the probe *how would we know?*; the ledger discipline — stable never-reused IDs, P1–P5 mapped to the phased roadmap, 224 requirements with 57 in Phase 1, "sequenced, not simultaneous"; trace one — Tuan's tunnel ★ → FR-MSG-04 / FR-RTM-03 / FR-SDK-04 with `<Why source="SRS §7 — traceability">`; trace two — Priya's reconstruct ★ → FR-MSG-07/08/10 + FR-MOD-01, then FR-TEN-05 as "the single most important requirement in this document" (Sev-0, automated cross-tenant suite on every build, NFR-MNT-02's 100%-branch-coverage trio); the change beat — FR-MED as 0.1's reversed non-goal arriving as NEW §4.14 IDs, FR-MED-09 quoted with its Priya trace, with `<Why source="SRS §4.14 — FR-MED">`; `<ForwardRef part="Part 2">` (FR-MSG-04 IS chapter 2.3; the cross-tenant suite IS 3.7's isolation gauntlet; the requirements are the series' table of contents); `<ChapterFooter id="0.4" />`; first-person plural present; ≤3 fenced specimen blocks, NO pipe tables, readable without fences (R3); every quoted ID verbatim from docs/04 (FR-007); leave ~700 words for T004
- [x] T003 [US1] Add the skip-safe takeaways block (before the footer) per FR-005, then run the body-so-far checks (C4: `<Why` ≥2, `<SkipAhead` ≥1, `<ForwardRef` ≥1, takeaways ≥1, fence lines ≤6, `grep -c '^|'` == 0, invented-ID detector clean) and `pnpm build`

**Checkpoint**: US1 readable end to end at `/part-0/chapter-04/requirements-you-can-test`

---

## Phase 4: User Story 2 - Produce the chapter's reader artifacts (Priority: P2)

**Goal**: The exercise: the reader's 8–15-row SRS slice with the opinion hunt.

**Independent Test**: The exercise alone yields a complete slice (ID, shall, priority+rationale, one T/D/I/A each; ★s on top) self-checked yes/no (quickstart V3.4).

### Implementation for User Story 2

- [x] T004 [US2] Add the exercise section to relay-tutorial/app/part-0/chapter-04/requirements-you-can-test/page.mdx per research R4 (after the FR-MED beat, before takeaways): Exercise 1 — convert the reader's two journey maps into 8–15 requirements: every ★ stage first (top priority), then supporting stages; docs/04 row format with a family-prefix ID scheme the reader invents once (e.g. VET-REM-01); shall-statement; priority with one-line phase rationale; exactly one T/D/I/A method; FR-MSG-04 as the worked example; Exercise 2 — the opinion hunt: for each row write the single test/demonstration/inspection/analysis that could FAIL it; repair the deliberately bad row "the system shall be fast" into a testable one on the page — rendered as blockquote/prose before-and-after, NOT a fence (the ≤3 fence budget stays reserved for the specimen rows — analysis I2); any row nothing could fail is an opinion — rewrite or cut; yes/no self-checks per R4 (every ★ produced a top-priority requirement; every row has exactly one method; no unfalsifiable row survives; the ID scheme could last years) (FR-006)
- [x] T005 [US2] Add the single closing `<Checkpoint>` (after takeaways, before the footer) naming the SRS slice as required before chapter 0.5 (which decides architecture against these requirements), then run the full C4 battery — canonical words 2,000–4,000, `<Why` ≥2, `<SkipAhead` ≥1, `<ForwardRef` ≥1, `<Checkpoint` exactly 1, takeaways ≥1, fences ≤6 lines, zero pipe-table lines, invented-ID detector clean — adjust prose until all pass; `pnpm lint && pnpm build`

**Checkpoint**: English chapter complete and format-verified

---

## Phase 5: User Story 3 - The chapter takes its place in the bilingual series (Priority: P3)

**Goal**: The Vietnamese chapter in the established register with English identifiers; all bilingual navigation live.

**Independent Test**: 0.4 reachable in ≤2 steps from either landing; 0.3→0.4 links live both locales; switcher maps 0.4↔0.4; parity passes (quickstart V2).

### Implementation for User Story 3

- [x] T006 [US3] Author the Vietnamese chapter in relay-tutorial/app/vi/part-0/chapter-04/requirements-you-can-test/page.mdx per research R5 and 004 C5: translate the FINAL English file in the established storytelling register with glossary continuity; **identifier discipline** — requirement IDs (FR-MSG-04, FR-TEN-05, FR-MED-09, family prefixes), the `shall` keyword, and T/D/I/A codes stay in ENGLISH (Vietnamese expansions on first use: kiểm thử tự động / trình diễn / thanh tra / phân tích); inside fenced specimen blocks translate only the shall-statement prose, never IDs/priority/method codes; persona names unchanged; `locale="vi"` on shell and every box; vi metadata title "Những yêu cầu bạn có thể kiểm chứng — Building Relay" (manifest verbatim) + description + hreflang; identical arc, box counts, fence counts (SC-005)
- [x] T007 [US3] Verify bilingual integration per quickstart V2 live checks: hreflang ≥2 (case-insensitive) both 0.4 pages; `div lang="vi"` only on vi; 0.3's footers link forward to 0.4 (both locales); 0.4's footers link back to 0.3 and show 0.5 forthcoming with `href="[^"]*chapter-05` == 0; both landings link 0.4; switcher maps 0.4↔0.4; `pnpm lint && pnpm build`; fix gaps

**Checkpoint**: All three user stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full validation and handoff

- [x] T008 Run the complete quickstart V1–V5 for specs/007-tutorial-chapter-04/quickstart.md: route table (V1), full scripted battery incl. the invented-ID detector and no-pipe-tables check (V2), manual fidelity pass — 5 quoted rows verified verbatim against docs/04, fences render light+dark and the chapter reads without them, navigation walk both locales, exercise dry-run with the opinion hunt failing at least one draft row (V3), reading-time sanity vs `readerMinutes: 100` with manifest correction if materially off (V5); record results; V4 (Vietnamese read-through) is Dong's — request prominently in the handoff
- [x] T009 Handoff (NO commits — standing instruction): report ready-to-commit files for relay-tutorial (new: both chapter-04 page.mdx files; modified: lib/tutorial.ts) with a suggested commit message; request Dong's V4 read-through before committing; note parent-repo follow-ups (spec artifacts, CLAUDE.md pointer, submodule pin)

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
# Serial by design (features 005/006 pattern):
# T001 → T002→T003 (en) → T004→T005 (exercise+checkpoint) → T006 (vi) → T007 → T008 → T009
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. T001 + T002–T003 — the testability lesson readable in English
2. **STOP and VALIDATE**: anatomy, T/D/I/A, both traces, FR-TEN-05, FR-MED beat land

### Incremental Delivery

1. US1 → the argument readable end to end
2. US2 → exercise + checkpoint → chapter complete
3. US3 → Vietnamese version + bilingual navigation live
4. Polish → full battery; request Dong's read-through; handoff

---

## Notes

- The sharpest hazard is **quote drift** (plan Notes): every specimen row must survive a literal grep against docs/04; when prose needs paraphrase, drop the ID from that sentence — quote exactly or don't attach the identifier
- **No pipe tables anywhere** in the chapter body — the MDX pipeline has no GFM; specimen rows live in ≤3 fenced blocks (research R3)
- The FR-MED beat is the emotional close of Part 0's paperwork argument: the product's own recent history proving the spec is alive
- NO git commit / git push — Dong commits personally; V4 review requested before commit
