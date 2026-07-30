# Tasks: Tutorial Chapter 0.5 — Deciding Out Loud

**Input**: Design documents from `/specs/008-tutorial-chapter-05/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chapter-05-contract.md, quickstart.md

**Tests**: Not requested — verification is the settled chapter battery (contract C4, with the ID detector extended to `ADR-nn`/`D1–D8` against docs/05), quickstart scenarios, and `pnpm lint && pnpm build`. Vietnamese quality (quickstart V4) is Dong's read-through.

**Organization**: The settled chapter pipeline (features 005–007), fifth and final Part 0 run. This feature's distinctive obligations: **the chain close** (ADR-13's "reverses the v1.0 file-storage exclusion" quoted, the 0.1→0.3→0.4→0.5 chain named), **Part 0 completion** (five links, zero forthcoming badges in Part 0 on both landings), and **the last-chapter footer** — 0.5 is the first page to exercise the shell's empty-next path; verify it, and surface any gap as an infrastructure finding, never patch the shell here.

**⚠ Standing instructions**: Do NOT run `git commit` / `git push` (Dong commits personally). Do NOT modify any component, i18n, or styling code.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = read the chapter, US2 = reader artifacts, US3 = Part 0 completion in the bilingual series

## Path Conventions

- App paths relative to `/home/dong/work/relay/relay-tutorial/`
- EN chapter (NEW): `app/part-0/chapter-05/deciding-out-loud/page.mdx`
- VI chapter (NEW): `app/vi/part-0/chapter-05/deciding-out-loud/page.mdx`
- Content sources: `/home/dong/work/relay/docs/05-sad.md` + `docs/06-adr-deep-dives.md` (CURRENT revisions incl. ADR-13/14 — the 007 verbatim definition applies), 0.1–0.4 artifacts (context), docs/07 §2 (format rules)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: None — zero new dependencies; features 002–007 are the baseline.

*(no tasks)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The manifest flip that completes Part 0

- [X] T001 Flip chapter 0.5's manifest entry in relay-tutorial/lib/tutorial.ts per data-model E1: `status: "published"`, add `translatedIn: ["vi"]`; leave path/titleVi/readerProducesVi untouched; `pnpm build` passes; brief expected-404 window — do NOT hand-edit navigation; note this flip makes `nextChapter("0.5")` the first-ever empty next (verified in T007)

---

## Phase 3: User Story 1 - Read chapter 0.5 and follow the derivation (Priority: P1) 🎯 MVP

**Goal**: The English chapter — drivers distillation, full ADR anatomy on ADR-03, the review discipline, and ADR-13/14 closing the paperwork chain — live at its canonical address.

**Independent Test**: A reader who finished 0.4 can answer: what a driver is and why 224 requirements distill to a handful, the parts of an ADR, why rejected alternatives are recorded, and what "attack the driver, not the choice" means — without docs/05/06 (quickstart V3.1).

### Implementation for User Story 1

- [X] T002 [US1] Author the English chapter body in relay-tutorial/app/part-0/chapter-05/deciding-out-loud/page.mdx per research R2 beats 1–6: metadata (title "Deciding out loud — Building Relay", description, hreflang alternates per 004 C4); `<ChapterHeader id="0.5" />`; cold open — the SRS slice is a list of promises, an architecture is how we intend to keep them; 224 requirements cannot each drive a design; 0.4-artifact pointer + 1 `<SkipAhead>` early; the drivers table taught on D1 (derived from FR-MSG-05/06, consequence: ack after durable commit, one transactional store) and D8 (the driver that is NOT a requirement — portfolio reality, the anti-sprawl force) with fence 1 quoting the D1+D8 rows per the 007 verbatim definition; the ADR form walked in full anatomy on ADR-03 (resolves SRS Open Question 1; drivers D1/D3; "the lock is not a cost, it is the mechanism"; trade-offs; the three rejected alternatives WITH reasons; reversal framing) with fence 2 quoting ADR-03's core, plus the two-document split (terse in SAD §9, deep dive in docs/06: Problem → Options → analysis → consequences) and the immutability rule (superseding = new ADR); the review discipline with `<Why source="SAD §2/§9">` — "attack the driver, not the choice; the choices follow from D1–D8 fairly mechanically"; the chain close — ADR-13 with fence 3 quoting its status line ("reverses the v1.0 file-storage exclusion") and core decision (bytes never transit Relay compute; the exclusion's cost argument answered "by not building any of it"), ADR-14's gates-bytes-never-messages and one-mental-model-twice-applied, naming the 0.1→0.3→0.4→0.5 chain explicitly, with `<Why source="docs/06 — reading the fourteen together">` on "every decision names its own undoing"; the three docs/06 themes as the architecture's character; `<ForwardRef part="Parts 1–7">` (ADR-01 is chapter 1.1, ADR-03 is 2.2's row lock, ADR-06 is 3.3's outbox, ADR-13/14 are Part 4's media chapters); `<ChapterFooter id="0.5" />`; first-person plural present; ≤3 fences, NO pipe tables, readable without fences; every ADR-nn/D-n/requirement ID real (FR-007); leave ~700 words for T004
- [X] T003 [US1] Add the skip-safe takeaways block (before the footer) per FR-005, then run the body-so-far checks (C4: `<Why` ≥2, `<SkipAhead` ≥1, `<ForwardRef` ≥1, takeaways ≥1, fence lines ≤6, zero pipe lines, extended ID detector clean) and `pnpm build`

**Checkpoint**: US1 readable end to end at `/part-0/chapter-05/deciding-out-loud`

---

## Phase 4: User Story 2 - Produce the chapter's reader artifacts (Priority: P2)

**Goal**: The Part 0-completing exercise: the reader's drivers table and two from-scratch ADRs.

**Independent Test**: The exercise alone yields a 3–6-row drivers table (requirement-sourced, consequences) and two complete ADRs (≥2 rejected-with-reasons, observable reversal conditions), self-checked yes/no (quickstart V3.4).

### Implementation for User Story 2

- [X] T004 [US2] Add the exercise section to relay-tutorial/app/part-0/chapter-05/deciding-out-loud/page.mdx per research R4 (after the themes section, before takeaways): Exercise 1 — distill 3–6 drivers from the reader's 8–15-row slice (the compression IS the skill: a driver shapes structure, not merely exists); each row: driver statement, source requirement IDs from their own slice, one-line architectural consequence; D1/D8 as worked examples, with explicit permission for one D8-style context driver (team size, deadline) that is not a requirement; Exercise 2 — write two ADRs from scratch against those drivers using the taught template (status · drivers · decision · trade-offs accepted · ≥2 rejected alternatives WITH reasons · reversal condition), ideally one per ★-derived requirement; yes/no self-checks per R4 (every driver cites their own requirement IDs or is declared context; each ADR names ≥1 driver from their table; each rejection passes the teammate-reconstruction test; each reversal condition is observable — "revisit when X exceeds Y", never "revisit if needed") (FR-006)
- [X] T005 [US2] Add the single closing `<Checkpoint>` (after takeaways, before the footer) that CLOSES PART 0: recap the complete portfolio the reader now holds (positioning statement, non-goals, personas, journey maps + ★s, SRS slice, drivers table, two ADRs) and point forward to Part 1 where the building begins; then run the full C4 battery — canonical words 2,000–4,000, boxes, fences ≤6 lines, zero pipes, extended ID detector clean — adjust until all pass; `pnpm lint && pnpm build`

**Checkpoint**: English chapter complete and format-verified

---

## Phase 5: User Story 3 - The chapter completes Part 0 in the bilingual series (Priority: P3)

**Goal**: The Vietnamese chapter under the settled conventions; Part 0 fully published; the last-chapter footer verified.

**Independent Test**: 0.5 reachable in ≤2 steps both locales; 0.4→0.5 live; switcher maps 0.5↔0.5; both landings show five linked Part 0 chapters with zero forthcoming badges; 0.5's footer renders cleanly with no next card (quickstart V2/V3.2).

### Implementation for User Story 3

- [X] T006 [US3] Author the Vietnamese chapter in relay-tutorial/app/vi/part-0/chapter-05/deciding-out-loud/page.mdx per research R5 and 004 C5: translate the FINAL English file in the settled register with glossary continuity; identifier discipline — ADR numbers, D1–D8, requirement IDs, and status keywords stay ENGLISH; the three specimen fences stay fully English-verbatim with "(Dịch nghĩa: …)" glosses after each (the approved 007 pattern); `locale="vi"` on shell and every box; vi metadata title "Quyết định thành tiếng — bản SAD và thói quen viết ADR — Building Relay" (manifest verbatim) + description + hreflang; identical arc, box counts, fence counts (FR-008 / US3 acceptance scenario 3 — the spec's structural-parity criterion)
- [X] T007 [US3] Verify Part 0 completion and the last-chapter state per quickstart V2/V3.2: hreflang ≥2 both 0.5 pages; `div lang="vi"` only on vi; 0.4's footers link forward to 0.5 (both locales); 0.5's footers link back to 0.4 with ZERO hrefs matching `chapter-0[6-9]` or `part-[1-8]/chapter`; both landings show exactly 5 Part 0 chapter links and zero forthcoming badges within Part 0; switcher maps 0.5↔0.5; **the empty-next footer renders acceptably in both locales and both themes** — if it looks broken, record an infrastructure finding (do NOT patch chapter-shell.tsx); `pnpm lint && pnpm build`; fix content gaps found

**Checkpoint**: All three user stories independently functional — Part 0 complete

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full validation and the Part 0-closing handoff

- [X] T008 Run the complete quickstart V1–V5 for specs/008-tutorial-chapter-05/quickstart.md: route table (V1), full scripted battery incl. the extended ID detector against docs/05 AND docs/04 (V2), manual fidelity pass — 5 quoted items spot-checked against docs/05/06, the last-chapter footer visual check both themes, navigation walk both locales, exercise dry-run (V3), reading-time sanity vs `readerMinutes: 110` with manifest correction if materially off (V5); record results incl. any infrastructure finding from the footer check; V4 (Vietnamese read-through) is Dong's — request prominently
- [X] T009 Handoff (NO commits — standing instruction): report ready-to-commit files for relay-tutorial (new: both chapter-05 page.mdx files; modified: lib/tutorial.ts) with a suggested commit message that marks the milestone (Part 0 complete, both locales); request Dong's V4 read-through before committing; note parent-repo follow-ups (spec artifacts, CLAUDE.md pointer, submodule pin)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: empty
- **Foundational (Phase 2)**: T001 first
- **US1 (Phase 3)**: T002 → T003 (same file)
- **US2 (Phase 4)**: T004 → T005 (same file, after US1)
- **US3 (Phase 5)**: T006 strictly after T005 (final en file = translation source); T007 after T006
- **Polish (Phase 6)**: T008 after all; T009 last

### User Story Dependencies

- **US1 (P1)**: T001 only — the MVP
- **US2 (P2)**: US1 (same file)
- **US3 (P3)**: US2 complete

### Parallel Opportunities

None — the settled serial content pipeline: T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009.

## Parallel Example

```bash
# Serial by design (the 005–007 pattern, final Part 0 run):
# T001 → T002→T003 (en) → T004→T005 (exercise + Part 0-closing checkpoint) → T006 (vi) → T007 → T008 → T009
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. T001 + T002–T003 — the deciding-out-loud lesson readable in English
2. **STOP and VALIDATE**: drivers, ADR anatomy, the discipline, and the chain close all land

### Incremental Delivery

1. US1 → the argument readable end to end
2. US2 → exercise + the Part 0-closing checkpoint
3. US3 → Vietnamese version; Part 0 fully published; last-chapter footer verified
4. Polish → full battery; request Dong's read-through; the milestone handoff

---

## Notes

- Quote fidelity per the 007 verbatim definition: words exact and greppable in docs/05; middot layout sanctioned; never paraphrase next to an identifier
- The three fences are fixed: D1+D8 rows, ADR-03 core, ADR-13 core; everything else (ADR-14, docs/06 themes) is faithful prose without fences
- The last-chapter footer is a VERIFICATION obligation, not a license to touch chapter-shell.tsx — any gap becomes an infrastructure finding for its own feature
- NO git commit / git push — Dong commits personally; V4 review requested before the milestone commit
