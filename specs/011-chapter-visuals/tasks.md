# Tasks: Part 0 Chapter Visuals — Diagrams Where Prose Works Hardest

**Input**: Design documents from `/specs/011-chapter-visuals/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chapter-visuals-contract.md, quickstart.md

**Tests**: Not requested — verification is the contract's battery v2 (quickstart
V2: figure counts + halves distribution + specimen byte-diff + invented-ID
detector over figure labels), `pnpm lint && pnpm build`, the both-themes/375 px
manual pass (V3), and Dong's vi label review (V4).

**Organization**: The first content feature that deliberately edits all ten
published chapter files. Non-negotiables: **specimen fences byte-identical**
(extracted to a baseline BEFORE any edit; a failed diff means rework, never
re-baseline); **mermaid sources never in page.mdx** (colocated `figures.ts`
modules keep the word-count formula stable); **prose additions are lead-ins and
captions only**; figure catalog fixed at 3/2/3/2/2 per chapter (data-model E3).

**⚠ Standing instructions**: Do NOT run `git commit` / `git push` (Dong commits
personally).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = en chapters with diagrams, US2 = vi parity, US3 = conventions absorb the new element

## Path Conventions

- App paths relative to `/home/dong/work/relay/relay-tutorial/`
- en chapters: `app/(en)/part-0/chapter-0X/<slug>/` · vi: `app/(vi)/vi/part-0/chapter-0X/<slug>/`
- Baselines: `/home/dong/work/relay/specs/011-chapter-visuals/{specimen-baseline/,battery-baseline.txt}`
- Sources for detector checks: `/home/dong/work/relay/docs/04-srs.md`, `docs/05-sad.md`

---

## Phase 1: Setup

**Purpose**: The untouchability proof's before-picture (must precede all edits)

- [X] T001 Extract the specimen-fence baseline per quickstart V0: fence contents of app/(en)/part-0/chapter-0[45]/*/page.mdx and app/(vi)/vi/part-0/chapter-0[45]/*/page.mdx into /home/dong/work/relay/specs/011-chapter-visuals/specimen-baseline/ (4 files — 0.3's flow fences are upgrade targets and are deliberately NOT baselined); the pre-edit box counts per chapter for C3's boxes-unchanged check are the ones already recorded in /home/dong/work/relay/specs/010-seo-optimization/battery-baseline.txt (columns 3–6; paths in pre-restructure form) — no new recording needed, V2 diffs against that file

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The chrome every figure renders through

- [X] T002 Create relay-tutorial/components/tutorial/figure.tsx per data-model E1: `<Figure caption code>` rendering `<figure>` → the existing MermaidDiagram (import from @/components/docs/mermaid-diagram) → `<figcaption>` in series chrome styling (muted, small, centered); `not-prose`-safe inside the chapter prose container; `pnpm lint` green

---

## Phase 3: User Story 1 - Read a chapter with visual explanations at its hardest moments (Priority: P1) 🎯 MVP

**Goal**: All five English chapters carry their catalog figures (3/2/3/2/2), placed where the argument needs them.

**Independent Test**: Each en chapter shows 2–4 rendered, captioned diagrams at concept-bearing moments, ≥1 per half; specimens byte-identical; words in bounds (quickstart V2 + V3.1–V3.3).

### Implementation for User Story 1

- [X] T003 [P] [US1] Chapter 0.1: create app/(en)/part-0/chapter-01/from-app-to-infrastructure/figures.ts (3 mermaid consts per data-model E3 — figWedge: your app ↔ Relay API ↔ what it is not; figCostCurve: xychart of naive-build cost vs buy across year 1→2, the "cost is the second year" shape; figNonGoals: kept vs excluded lists with the v1.0 file-storage exclusion visibly marked) and edit page.mdx: import + three `<Figure caption="…" code={…} />` placements with one-sentence lead-ins at the matching arguments; prose otherwise untouched (FR-001/002)
- [X] T004 [P] [US1] Chapter 0.2: create app/(en)/part-0/chapter-02/four-people-who-will-judge-us/figures.ts (figQuartet: Mai/David/Priya/Tuan around the product with one-line stakes; figPulls: the four demands tugging the design in different directions) and edit page.mdx with two placements + lead-ins, one per half (FR-001/002)
- [X] T005 [P] [US1] Chapter 0.3: create app/(en)/part-0/chapter-03/journeys-where-products-die/figures.ts (figMaiFlow and figTuanFlow upgraded FROM the chapter's two text-drawn flow fences — stage names and ★ markers preserved exactly; figEmotionalArc: the xychart mirroring docs/03's) and edit page.mdx: REMOVE the two text fences, place the three `<Figure/>`s in their argumentative positions with captions; chapter fence count drops to 0 (FR-006)
- [X] T006 [P] [US1] Chapter 0.4: create app/(en)/part-0/chapter-04/requirements-you-can-test/figures.ts (figAnatomy: ID · shall-statement · priority · verification blocks around the FR-MSG-04 example; figTraceChain: persona → journey ★ → requirement ID → the test that can fail it) and edit page.mdx with two placements + lead-ins, one per half; the three specimen fences byte-untouched (FR-001/002/005)
- [X] T007 [P] [US1] Chapter 0.5: create app/(en)/part-0/chapter-05/deciding-out-loud/figures.ts (figFunnel: 224 requirements → 8 drivers → 14 ADRs → 6 services; figAdrAnatomy: status/drivers/decision/trade-offs/rejected×3/reversal skeleton with ADR-03's values) and edit page.mdx with two placements + lead-ins, one per half; the three specimen fences byte-untouched (FR-001/002/005)
- [X] T008 [US1] Run the en half of the V2 battery per quickstart: figures 3/2/3/2/2 with halves OK; fences 0/0/0/3/3; en canonical words 2,000–4,000; box counts equal T001's record; specimen byte-diff empty (en files); zero mermaid text in any page.mdx; invented-ID detector clean over en page.mdx + figures.ts; `pnpm lint && pnpm build`; fix findings

**Checkpoint**: The English chapters are no longer text-only — MVP delivered

---

## Phase 4: User Story 2 - The Vietnamese chapters get the same visuals, in Vietnamese (Priority: P2)

**Goal**: Same figures, same positions, translated labels and captions.

**Independent Test**: Per-chapter figure counts equal en; sampled vi diagrams show glossary-correct Vietnamese narrative labels with English IDs; captions Vietnamese (quickstart V2 + V3.1).

### Implementation for User Story 2

- [X] T009 [P] [US2] Chapter 0.1 vi: create app/(vi)/vi/part-0/chapter-01/from-app-to-infrastructure/figures.ts translated from the FINAL en figures (register + glossary; product/persona names unchanged) and edit page.mdx with the three placements + vi captions/lead-ins (FR-004)
- [X] T010 [P] [US2] Chapter 0.2 vi: same for app/(vi)/vi/part-0/chapter-02/four-people-who-will-judge-us/ (2 figures) (FR-004)
- [X] T011 [P] [US2] Chapter 0.3 vi: same for app/(vi)/vi/part-0/chapter-03/journeys-where-products-die/ (3 figures; REMOVE the vi text flow fences; translated stage labels — the 006 convention — with ★ preserved) (FR-004/006)
- [X] T012 [P] [US2] Chapter 0.4 vi: same for app/(vi)/vi/part-0/chapter-04/requirements-you-can-test/ (2 figures; FR-MSG-04 and T/D/I/A markers English); specimen fences byte-untouched (FR-004/005)
- [X] T013 [P] [US2] Chapter 0.5 vi: same for app/(vi)/vi/part-0/chapter-05/deciding-out-loud/ (2 figures; ADR-03/D-IDs/status keywords English); specimen fences byte-untouched (FR-004/005)
- [X] T014 [US2] Run the full V2 battery per quickstart (both locales): figure counts en==vi per chapter; halves OK ×10; fences 0/0/0/3/3 per locale; specimen byte-diff empty (all 4 baseline files); detector clean over all 20 files; `pnpm lint && pnpm build`; fix findings

**Checkpoint**: Bilingual parity — the vi edition is not the boring one

---

## Phase 5: User Story 3 - The series' conventions absorb the new element (Priority: P3)

**Goal**: The format rules say what the chapters now do; the battery has its new baseline.

**Independent Test**: docs/07 §2 contains the Visual-elements row; battery-baseline.txt records words/boxes/fences/figures for all 10 pages (quickstart V6 + V2's baseline step).

### Implementation for User Story 3

- [X] T015 [US3] Amend /home/dong/work/relay/docs/07-tutorial-plan.md §2's format table with the "Visual elements" row per data-model E6 (2–4 captioned theme-legible diagrams per chapter via the series Figure component; counted separately from specimen fences; vi labels translated, identifiers English); then generate /home/dong/work/relay/specs/011-chapter-visuals/battery-baseline.txt per quickstart V2's baseline step (words/boxes/fence-lines/figures for all 10 pages) (FR-008)

**Checkpoint**: All three user stories independently verified

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full validation, reading-time revalidation, handoff

- [X] T016 Run the complete quickstart V1–V3 + V5 + V6 for specs/011-chapter-visuals/quickstart.md and record results: build gate (V1 — zero new deps), full scripted battery (V2), manual pass (V3 — every figure both themes at desktop and 375 px on all 10 pages; captions language-correct; 0.3's ★ survived; 0.5's funnel reads 224→8→14→6; SEO spot-check unchanged), reading-time re-estimate vs manifest with corrections if materially off (V5, FR-009), docs/07 grep (V6); flag V4 prominently — Dong's review of the 5 vi figures.ts files + captions, and the "less boring or just busier?" judgment call
- [X] T017 Handoff (NO commits — standing instruction): report ready-to-commit files for relay-tutorial (new: components/tutorial/figure.tsx + 10 figures.ts; modified: 10 page.mdx, possibly lib/tutorial.ts readerMinutes) and the parent repo (docs/07 §2 row; specs/011 artifacts incl. both baselines; CLAUDE.md pointer; feature.json; submodule pin) with suggested commit messages; request Dong's V4 review before committing

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 strictly first — the byte-diff proof depends on it
- **Foundational (Phase 2)**: T002 after T001
- **US1 (Phase 3)**: T003–T007 [P] after T002 (five independent chapter-file pairs); T008 after all five
- **US2 (Phase 4)**: T009–T013 [P] after T008 (vi translates the FINAL en figures); T014 after all five
- **US3 (Phase 5)**: T015 after T014 (the baseline must capture final content)
- **Polish (Phase 6)**: T016 after T015; T017 last

### User Story Dependencies

- **US1 (P1)**: Setup + Foundational only — the MVP
- **US2 (P2)**: en figures final (post-T008)
- **US3 (P3)**: all content final (post-T014)

### Parallel Opportunities

- T003–T007: five chapters, disjoint files — genuinely parallel
- T009–T013: five vi chapters, disjoint files — genuinely parallel

## Parallel Example

```bash
# After T002:
#   lanes A–E: T003 | T004 | T005 | T006 | T007   (en chapters)
# After T008:
#   lanes A–E: T009 | T010 | T011 | T012 | T013   (vi chapters)
# Then: T014 → T015 → T016 → T017
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. T001–T008 — the English chapters carry their 12 figures, specimens proven intact
2. **STOP and VALIDATE**: V2's en half + a browser pass on both themes

### Incremental Delivery

1. US1 → the en chapters stop being text-only
2. US2 → vi parity with translated labels
3. US3 → the conventions and baseline catch up
4. Polish → full battery; Dong's V4; the handoff

---

## Notes

- A failed specimen byte-diff is ALWAYS rework, never a re-baseline — the six
  quoted fences are the feature's hard wall
- Figure labels are detector territory: an invented FR/D/ADR id in a diagram
  fails the battery exactly like one in prose
- 0.3 is the only chapter whose fence count changes (2 → 0) — its flows were
  chapter-authored renditions, not quotes
- Lead-ins are one sentence; if a figure needs a paragraph of setup, the figure
  is wrong, not the prose
- NO git commit / git push — Dong commits personally
