# Tasks: Tutorial Chapter 0.1 — From App to Infrastructure

**Input**: Design documents from `/specs/002-tutorial-chapter-01/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/tutorial-site-contract.md, quickstart.md

**Tests**: Not requested in the spec — no test-framework tasks. Verification is scripted format checks (contract C5), the quickstart scenarios, and the `pnpm lint && pnpm build` gate.

**Organization**: Tasks are grouped by user story. US1 (read the chapter) and US2 (exercise artifacts) both live in the same `page.mdx` file — they are sequential, not parallel. All stories consume the Phase 2 shell.

**⚠ Standing instruction**: Do NOT run `git commit` or `git push` — Dong commits personally. Tasks end with files ready to commit; the completion report lists suggested commit messages.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = read chapter 0.1, US2 = exercise artifacts, US3 = navigation

## Path Conventions

- All application paths relative to `/home/dong/work/relay/relay-tutorial/` (the submodule)
- Content sources: `/home/dong/work/relay/docs/01-product-vision.md` (facts), `/home/dong/work/relay/docs/07-tutorial-plan.md` (format rules §2, Part 0 table §3)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Install the dependencies every later task needs

- [x] T001 Install MDX and typography dependencies in relay-tutorial/: `pnpm add @next/mdx @mdx-js/loader @mdx-js/react @tailwindcss/typography` and `pnpm add -D @types/mdx` (versions per research R1/R5: @next/mdx 16.2.12, typography 0.5.20); verify lockfile updated and `pnpm lint` still passes

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The MDX pipeline and the reusable series shell that every story renders through

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Enable MDX pages in relay-tutorial/next.config.ts: wrap the config with `createMDX()` from `@next/mdx` and add `pageExtensions: ['ts', 'tsx', 'md', 'mdx']` (pattern per the bundled v16 MDX guide, research R1)
- [x] T003 Create relay-tutorial/mdx-components.tsx (repo root — REQUIRED for App Router per v16 docs): export `useMDXComponents` returning base HTML element mappings only (headings/links may be lightly styled; box components are NOT injected here per research R4)
- [x] T004 Verify the MDX pipeline: create a throwaway `app/mdx-smoke/page.mdx` with one heading, confirm `pnpm build` compiles it as a route, then delete it before proceeding
- [x] T005 [P] Create the series manifest in relay-tutorial/lib/tutorial.ts per data-model E1/E2 and contract C2: types `Part`/`Chapter`, `series` covering parts 0–8 with titles from docs/07 §3, Part 0 populated with chapters 0.1–0.5 (id; `path` — full route, e.g. `/part-0/chapter-01/from-app-to-infrastructure`, whose final segment is the slug: kebab-case of title main clause, subtitle dropped; title; status — 0.1 `published`, rest `forthcoming`; readerProduces; sourceDoc; readerMinutes — estimated reading+exercise minutes, 0.1: 90), helpers `getChapter` (throws on unknown id), `nextChapter`, `prevChapter`
- [x] T006 [P] Wire long-form typography in relay-tutorial/app/globals.css: `@plugin "@tailwindcss/typography";` and map the `prose` palette to Violet Bloom variables (body/headings→foreground, links→primary, code→accent-foreground, blockquote→muted-foreground, dark mode via the same tokens — no `prose-invert` with hardcoded colors), per research R5 and SC-006
- [x] T007 [P] Create box-convention components in relay-tutorial/components/tutorial/boxes.tsx per contract C4 and data-model E4: server components `Why` (optional `source` prop, accent family), `Trap` (destructive-tinted), `Checkpoint` (primary), `SkipAhead` (muted), `Revised` (`note` prop, secondary), `ForwardRef` (`part` prop, accent with part label) — each a labeled callout styled ONLY with theme token classes, distinct in both modes
- [x] T008 Create the chapter shell in relay-tutorial/components/tutorial/chapter-shell.tsx per research R6: `ChapterHeader` (props `{id}`; renders breadcrumb to `/`, "Part N · Chapter id" identity, title, readerProduces + reading-time note from the manifest) and `ChapterFooter` (props `{id}`; renders prev/next from `nextChapter`/`prevChapter` — published chapters as links, forthcoming as non-link with a "forthcoming" badge — plus back-to-contents link); depends on T005, T007 conventions

**Checkpoint**: Foundation ready — `pnpm build` passes with the manifest, boxes, and shell compiled

---

## Phase 3: User Story 1 - Read chapter 0.1 and follow the derivation (Priority: P1) 🎯 MVP

**Goal**: The chapter's body prose — the app→infrastructure derivation — published at `/part-0/chapter-01/from-app-to-infrastructure`, format-compliant.

**Independent Test**: A reader with no prior project exposure reads the page and can answer what Relay is, what it is not, and why "just a chat feature" fails; scripted checks confirm word count and box counts (quickstart V2/V3).

### Implementation for User Story 1

- [x] T009 [US1] Author the chapter body in relay-tutorial/app/part-0/chapter-01/from-app-to-infrastructure/page.mdx: export `metadata` (title "From app to infrastructure — Building Relay", description); open with `<ChapterHeader id="0.1" />`; write the prose per research R7's section arc — (1) the naïve chat-app premise, (2) the underestimation table as a walked derivation (docs/01 §2), (3) the alternatives and the gap (docs/01 §2), (4) finding the wedge (docs/01 §4) — first-person plural present tense, every factual claim traceable to docs/01 (SC-002), ≥2 `<Why source="…">` boxes, ≥1 `<ForwardRef part="…">` (e.g. non-goals → FR-MSG-14 in Part 2), 1 `<SkipAhead>` early (Part 0 is skippable by design); close with `<ChapterFooter id="0.1" />`; target total body 2,000–4,000 words INCLUDING the Phase 4 exercise section (leave ~800 words of budget for it)
- [x] T010 [US1] Add the skip-safe takeaways block near the end of relay-tutorial/app/part-0/chapter-01/from-app-to-infrastructure/page.mdx (before the footer): compact statement of the chapter's conclusions usable by a Part 0 skipper (FR-006), and verify the body-so-far against quickstart V2's scripted checks (word count in range once Phase 4 lands, `<Why>` ≥ 2, `<ForwardRef>` ≥ 1)

**Checkpoint**: Chapter renders at `/part-0/chapter-01/from-app-to-infrastructure` with compliant prose — US1 independently testable

---

## Phase 4: User Story 2 - Produce the chapter's reader artifacts (Priority: P2)

**Goal**: The exercise section that turns the essay into a tutorial chapter: reader produces a positioning statement + non-goals list.

**Independent Test**: Quickstart V4/V6 — a reader following only the chapter produces both artifacts in under 45 minutes and can self-check them yes/no.

### Implementation for User Story 2

- [x] T011 [US2] Add the exercise section to relay-tutorial/app/part-0/chapter-01/from-app-to-infrastructure/page.mdx (after the wedge section, before takeaways): the for/who/that/unlike positioning template with Relay's own statement (docs/01 §1) walked as the worked example; the non-goals exercise requiring ≥3 entries each with a reason, with Relay's non-goals (docs/01 §6) as the worked example; yes/no self-check criteria for both artifacts (FR-003, US2/AC1-2)
- [x] T012 [US2] Add the final `<Checkpoint>` block at the end of relay-tutorial/app/part-0/chapter-01/from-app-to-infrastructure/page.mdx (exactly one in the file, after takeaways, before `<ChapterFooter>`): names both reader artifacts as required in-hand before chapter 0.2 (US2/AC3); then run the full contract C5 scripted checks (word count 2,000–4,000 total, `<Why` ≥2, `<Checkpoint` =1, `<ForwardRef` ≥1, takeaways present) and adjust prose until all pass

**Checkpoint**: Chapter is complete and format-verified — US1 and US2 both testable

---

## Phase 5: User Story 3 - Navigate to and within the chapter (Priority: P3)

**Goal**: `/` becomes the series landing/ToC; the chapter is discoverable in ≤2 steps and shows its place in the series.

**Independent Test**: Quickstart V1 — from `/`, reach the chapter in 2 steps; chapter header shows identity; footer shows 0.2 as forthcoming non-link.

### Implementation for User Story 3

- [x] T013 [US3] Rewrite relay-tutorial/app/page.tsx as the series landing per research R8: series title "Building Relay", the one-sentence pitch (docs/07 §1.1), the nine-part arc rendered from the `series` manifest (parts 1–8 compact with "forthcoming"), Part 0 expanded listing all five chapters with readerProduces — 0.1 as a link to its manifest `path`, 0.2–0.5 as non-links with forthcoming badges; update `metadata`; Violet Bloom tokens only; keep or adapt the existing Button usage where it serves the layout (FR-007, SC-005)
- [x] T014 [US3] Verify navigation end-to-end per quickstart V1: `pnpm dev`, confirm `/` → chapter link → chapter page is 2 steps; chapter header shows "Part 0 · Chapter 0.1" + title + breadcrumb; footer shows "0.2 — Four people who will judge us" as forthcoming non-link and back-to-contents; fix any gaps

**Checkpoint**: All three user stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full validation and handoff

- [x] T015 Run the full quickstart validation V1–V6 for specs/002-tutorial-chapter-01/quickstart.md: build gate + navigation (V1), scripted format checks (V2), traceability spot-check of 5 claims against docs/01 (V3), exercise completeness (V4), both-mode rendering of prose and every box type — including the V5 scratch-route check of the unused `Trap`/`Revised` boxes, deleted afterward (V5), reader dry-run assessment (V6); record results
- [x] T016 Handoff (NO commits — standing instruction): leave both working trees as-is; report the ready-to-commit file list for relay-tutorial (new: mdx-components.tsx, lib/tutorial.ts, components/tutorial/*, app/part-0/**; modified: next.config.ts, package.json, pnpm-lock.yaml, app/globals.css, app/page.tsx) and for the parent repo (specs/002-tutorial-chapter-01/, CLAUDE.md, and the submodule pin once Dong commits the submodule first), each with a suggested commit message

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: none — start immediately
- **Foundational (Phase 2)**: T002–T004 depend on T001; T005/T006/T007 are mutually parallel [P] (different files, no interdependency); T008 depends on T005 + T007
- **US1 (Phase 3)**: depends on Phase 2 complete (renders through shell + boxes + MDX pipeline)
- **US2 (Phase 4)**: depends on US1 (same file — the exercise extends the chapter body; word budget shared)
- **US3 (Phase 5)**: T013 depends only on T005 (manifest) — can run in parallel with Phases 3–4; T014 needs T009 + T013
- **Polish (Phase 6)**: T015 depends on everything; T016 last

### User Story Dependencies

- **US1 (P1)**: foundation only — the MVP
- **US2 (P2)**: US1 (structural: same MDX file, shared word budget)
- **US3 (P3)**: manifest only for the landing; final verification needs the chapter to exist

### Parallel Opportunities

- **T005, T006, T007** [P]: manifest, typography wiring, and box components are three independent files
- **T013 (landing rewrite)** can proceed in parallel with the chapter authoring (T009–T012) — different files, both consuming the T005 manifest
- Chapter authoring itself (T009→T012) is deliberately sequential: one file, one narrative arc, one word budget

## Parallel Example

```bash
# After T004 (MDX pipeline verified):
#   Track A: T005 manifest ─┬─→ T008 shell → T009 → T010 → T011 → T012
#   Track B: T006 typography┤
#   Track C: T007 boxes ────┘
#   Track D: T013 landing (after T005) — runs alongside Track A's authoring
# Then: T014 → T015 → T016
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Phase 1 + Phase 2 (pipeline + shell)
2. Phase 3 (chapter body)
3. **STOP and VALIDATE**: the derivation chapter renders, format checks pass minus the exercise-dependent word floor — demonstrable MVP

### Incremental Delivery

1. Setup + Foundational → shell ready (reusable by all 49 future chapters — this is most of this feature's lasting value)
2. US1 → the chapter's argument readable end-to-end
3. US2 → exercise + checkpoint → chapter complete per docs/07's "reader produces" contract
4. US3 → landing/ToC → series entry point live
5. Polish → full quickstart validation → handoff for Dong's commits

---

## Notes

- The single hardest constraint is editorial, not technical: SC-002 (100% claim traceability to docs/01) plus FR-002's "derivation, not conclusions" framing — T009/T011 must show the reasoning steps, quoting docs/01's argument structure rather than copying its text
- Box components must never receive hardcoded colors — theme tokens only (SC-006); if a box looks wrong in dark mode, fix the token choice, not the component
- Word budget: body (T009) ~2,200 + exercise (T011) ~800 keeps total safely inside 2,000–4,000 with takeaways/checkpoint included
- NO git commit / git push anywhere in this feature — Dong commits personally
