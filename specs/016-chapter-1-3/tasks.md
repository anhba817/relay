# Tasks: Tutorial Chapter 1.3 — The Protocol Package

**Input**: Design documents from `/specs/016-chapter-1-3/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chapter-1-3-contract.md, quickstart.md

**Tests**: Not requested as separate tasks — verification is the contract
battery (C4 gate with ≥12 tests, C3 three-chapter fence diffs, C2 battery v3,
C5 vocabulary fidelity, C6 nav + suggestions integration); the protocol test
suite is part of the artifact itself.

**Organization**: The third two-artifact feature. Non-negotiables: the R2
**derivation table is the law** — every frame/code cites a document source or
carries the chapter's recorded-decision marker; **additive-only** over all
thirteen prior fences (zod lands package-local, root package.json untouched);
schemas are the single source with types inferred (R3); fences byte-match, en/vi
byte-identical; publishing is the manifest flip alone; **commits, pushes, AND
the tag are Dong's**.

**⚠ Standing instructions**: Do NOT run `git commit` / `git push` / `git tag`
(Dong does all three). Part 0, 1.1, and 1.2 content files are byte-untouched.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = the chapter, US2 = the code at `part1-ch3`, US3 = the bilingual flip

## Path Conventions

- Platform: `/home/dong/work/relay/relay-platform/packages/protocol/` (NEW package, additive only)
- Chapter: `relay-tutorial/app/(en)/part-1/chapter-03/the-protocol-package/` (+ vi mirror)
- Sources: docs/04 (EIR-WS-01..07 L210–217, EIR-API-04 L188, FR-MSG-03/04, FR-RTM-01..09 L343–351, FR-SDK-06), docs/05 (§5.1 L224–263, §5.2 L265–297, §7 L570–573, ADR-01/03/05), docs/07 §2–3
- Vocabulary: research R2's derivation table; contract C5 makes it binding
- Battery baseline: `specs/016-chapter-1-3/battery-baseline.txt` (16 rows)

---

## Phase 1: Setup

**Purpose**: Pin the new dependency's reality before it becomes a fence

- [X] T001 Verify the zod current-stable version to pin: `pnpm view zod version` (or registry check); record the exact version for the package.json fence — a version in prose that doesn't install is a broken chapter; note zod's current import convention for the schemas task (T002) by checking the installed package's own docs/types after install (no relying on training-data API memory — same discipline as AGENTS.md for Next)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The package every chapter fence will mirror — built additive-only

- [X] T002 Scaffold and implement @relay/protocol in /home/dong/work/relay/relay-platform/packages/protocol/ per data-model + research R1–R3: package.json (name "@relay/protocol", private, "type": "module", exports "." → "./src/index.ts", typecheck script "tsc --noEmit", dependency zod pinned to T001's version — PACKAGE-LOCAL, root package.json untouched), tsconfig.json (extends ../../tsconfig.base.json, include src); src/frames.ts — the R2 vocabulary as zod schemas: the `{type, payload}` envelope discipline (EIR-WS-02), connection.ack (identity + per-channel cursor map + resume_ok), message.send ({idem_key non-empty ≤255, channel, text}), message.ack ({seq positive int}), the six event frames (message.created/updated/deleted, membership.changed, presence.changed, typing) with payload shapes per R2's payload table (Message = {id, channel, seq, user, text, created_at} derived from SAD §6.1 with deferred fields named; membership/presence/typing per their DECISION rows), backfill truncation flag, error frame ({code, message, docs_url, field?} per EIR-API-04's full shape, request_id explicitly deferred to Part 2 per R2); a zod discriminated union over `type` + `parseFrame(raw: unknown)`; EVERY exported static type via z.infer (no hand-written frame interfaces — R3); src/codes.ts — close-code registry (4001 auth per EIR-WS-05, 4002 protocol violation DECISION, 4008 quota DECISION, 4009 shutdown per SAD §7) and the error-code registry (unique, non-empty, EIR-API-04 shape); src/index.ts re-exports the public surface; header comments carry the source citations so the code itself shows the derivation; `pnpm install` then gate compiles (tests come in T003)
- [X] T003 Write the protocol test suites in /home/dong/work/relay/relay-platform/packages/protocol/src/: frames.test.ts — table-driven per research R4: for each frame schema one valid specimen parses + round-trips through parseFrame, and a malformed table (wrong type string, missing payload field, wrong primitive, negative/zero seq, empty idem_key, >255-char idem_key, extra unknown field where strict) each REJECTS; codes.test.ts — close codes exactly {4001, 4002, 4008, 4009} with distinct non-empty meanings, error codes unique and non-empty; then the full gate green with ≥12 total tests (`pnpm lint && pnpm typecheck && pnpm test`) and the additive check: `git -C relay-platform status --porcelain` shows ONLY packages/protocol/ paths (FR-006, C4)

---

## Phase 3: User Story 1 - Read chapter 1.3 and build the protocol package alongside it (Priority: P1) 🎯 MVP

**Goal**: The English chapter live — contract-first taught, the vocabulary derived on the page, 1.1's promise explicitly paid, the gate growing real teeth.

**Independent Test**: A reader with the 1.2 checkpoint can build the package from the chapter alone and watch the new suite pass; battery green; every frame name traceable (quickstart V1, V2, V4).

### Implementation for User Story 1

- [X] T004 [P] [US1] Flip chapter 1.3 in relay-tutorial/lib/tutorial.ts per data-model's transition table (UPDATE the 013-seeded placeholders): `status` → "published"; add `translatedIn: ["vi"]`; `readerMinutes` 90 → 75; `readerProduces` → "The shared wire contract — frame types, error codes, and schemas that reject bad input"; add `readerProducesVi` "Bản giao kèo đường truyền dùng chung — kiểu frame, mã lỗi, và schema biết từ chối dữ liệu hỏng"; `sourceDoc` → "docs/04-srs.md, docs/05-sad.md"; title/titleVi/path/id untouched; NOTHING outside this one entry; `pnpm build` green (expected-404 window until T006) (FR-008, R6)
- [X] T005 [P] [US1] Create relay-tutorial/app/(en)/part-1/chapter-03/the-protocol-package/figures.ts per research R5: figFrameMap (frames grouped by direction — client→server: message.send; server→client: connection.ack, message.ack, the six events, error; close codes at the edge), figOneSource (one zod schema → BOTH the runtime parse/reject path AND the z.infer static type — the no-drift mechanism), figPayoffRevisited (1.1's protocol-payoff figure updated: @relay/protocol now SOLID, gateway/API/SDK consumers still ghosted with "1.4 →" on two of them); labels detector-clean, frame names only from the R2 table (FR-005, C5)
- [X] T006 [US1] Author the English chapter in relay-tutorial/app/(en)/part-1/chapter-03/the-protocol-package/page.mdx per research R5's nine beats: metadata (title "The protocol package — Building Relay", description, canonical + hreflang); `<ChapterHeader id="1.3" />`; the promise-comes-due cold open (1.1's figure and its "compile error instead of a production incident" quote called back); `<SkipAhead>` naming part1-ch3; `<Why>` #1 contract-first · ADR-01; the vocabulary derivation walk — EIR-WS-02 quoted verbatim, SAD §5.1's frame lines quoted, Tuan's resume for cursor + truncation, EVERY R2 DECISION row introduced with its explicit recorded-decision sentence (FR-003); the first-runtime-dependency beat with the packages/protocol/package.json AND packages/protocol/tsconfig.json fences (title'd, byte-match — the full scaffold pair, 1.1's precedent); `<Why>` #2 (docs/07 §3 · EIR-WS-02 — schemas are types that survive runtime); the frames.ts fence walked (envelope → discriminated union → z.infer → parseFrame); `<Trap>` validation sprawl (per-service re-validation / `as Frame` casts; the structural fix is one home for types AND validation); the codes.ts fence; the test-suite beat with frames.test.ts + codes.test.ts fences (full-file with titles, per C3 — no gray-zone excerpts) and the gate run; the three `<Figure/>`s per the halves rule; `<ForwardRef>` (1.4 consumes; SDK later part; Part 2 extends the vocabulary; media/moderation/emoji vocabularies in their parts); your-turn exercises (add a malformed specimen → watch it reject; hand-write a frame type → compare with z.infer); takeaways; one closing `<Checkpoint>` (package present, gate ≥12 green); `<ChapterFooter id="1.3" />` — ALL file fences pasted from the real T002/T003 files (FR-001..005, 007)
- [X] T007 [US1] Run the en battery per quickstart V2 + V4: prose-only words 2,000–4,000; Why ≥2, Trap ≥1, SkipAhead =1 naming part1-ch3, ForwardRef ≥1, Checkpoint =1; figures 3 captioned, halves OK; verbatim spot-checks (EIR-WS-02/03, SAD §5.1 frame lines, FR-RTM rows) wrap-tolerant; ID detector clean; frame-name sweep: the set of frame names in page.mdx + figures.ts EQUALS the R2 table's set, and each DECISION item's marker sentence is present (C5); `pnpm lint && pnpm build`; fix findings

**Checkpoint**: The contract chapter readable end to end — MVP delivered

---

## Phase 4: User Story 2 - The canonical code advances to tag `part1-ch3` (Priority: P2)

**Goal**: The increment proven additive, drift-free across three chapters, and consumable.

**Independent Test**: Gate green with ≥12 tests; all sixteen file fences (10+3+1.3's) diff clean at one repo state; the package resolves from a sibling (quickstart V1, V3).

### Implementation for User Story 2

- [X] T008 [US2] Prove the three-chapter no-drift contract per quickstart V1 + V3: (a) additive check — `git -C relay-platform status --porcelain` shows only packages/protocol/ (any other modification violates R2/additive-only: STOP and surface); (b) zod pinned and present ONLY in packages/protocol/package.json; (c) fence enumeration — extract every title'd fence from BOTH locales' 1.3 page.mdx, byte-diff against the repo, then RE-RUN 1.1's ten and 1.2's three diffs; (d) consumability — from a scratch (uncommitted) sibling check, confirm `@relay/protocol` resolves via the workspace (delete the scratch after); (e) R3 spot-check: grep frames.ts for `interface`/hand-written frame types (must be none — all z.infer); (f) SkipAhead names part1-ch3 exactly; record the diff list (FR-006/007, SC-002/003)

**Checkpoint**: Chapter, package, and both previous chapters' promises hold at one repo state

---

## Phase 5: User Story 3 - The forthcoming entry flips to published, bilingually (Priority: P3)

**Goal**: The vi chapter at the settled register; every surface reflecting the flip — including the 015 suggestions allowlist.

**Independent Test**: 1.3 reachable ≤2 steps both locales; 1.2↔1.3 footer cards; sidebar 3+1; sitemap 30; vi parity; suggestion POSTs against both new paths accepted (quickstart V5, V6).

### Implementation for User Story 3

- [X] T009 [US3] Create the Vietnamese chapter: relay-tutorial/app/(vi)/vi/part-1/chapter-03/the-protocol-package/figures.ts (labels translated; frame/code/command names English) and page.mdx translated from the FINAL en file per research R7 — meaning-first, no calques or hyphenated compounds; glossary: "package" never "gói", "cửa ải"+"vượt qua", "bản giao kèo" (the chapter's central metaphor — use it), "quả ngọt", "tin nhắn"; ALL fences byte-identical to en incl. titles; vi metadata from titleVi + " — Building Relay"; `locale="vi"` on shell and boxes; naturalization self-review pass BEFORE presenting (FR-009, C7)
- [X] T010 [US3] Run the series battery per quickstart V5 + V6 against a build/dev server: both 1.3 routes 200 with hreflang; 1.2's footers show the 1.3 next card (both locales) and 1.3's footers show 1.2 prev + no next; sidebar Part 1 exactly 3 links + 1 forthcoming; both landings link 1.3; sitemap == 30; OG/TechArticle on the new pages; vi banner with suggest invitation present on the vi page; en/vi fence extraction diff empty; box/figure counts equal; glossary sweep clean; `git diff` confirms the manifest flip is the only source edit outside the two chapter directories; **suggestions admission**: with the 015 verification DB up, POST a valid suggestion for each new path → 201 + rows (fallback: unit-check the allowlist admits both paths and flag the live POST for Dong); fix findings (C1, C6, C7)

**Checkpoint**: All three stories independently verified

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full validation, the 16-row baseline, the three-repo handoff

- [X] T011 Run the complete quickstart V1–V6 end to end and record results: regenerate specs/016-chapter-1-3/battery-baseline.txt across ALL 16 chapter files with the established formula — the 14 pre-existing rows MUST be byte-identical to specs/014-chapter-1-2/battery-baseline.txt (any change = defect); re-verify `pnpm check:docs` (mirror drift); flag V7 prominently — Dong's vi read-through, the 75-minute walk, figures both themes/375 px, post-push tagged-clone replay, and the site redeploy (VPS rebuild or the pending Vercel migration)
- [X] T012 Handoff (NO commits/tags/pushes — standing instruction): report per-repo ready-to-commit files — relay-platform (packages/protocol/* only; Dong's sequence `git add -A && git commit && git tag part1-ch3 && git push origin main --tags`), relay-tutorial (manifest flip + 2 page.mdx + 2 figures.ts), parent (submodule pins + specs/016 incl. battery-baseline.txt + CLAUDE.md/feature.json) — with suggested messages; remind about the redeploy and that suggestions on the new pages start flowing to whichever database the live site points at

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 first (the pinned version becomes a fence)
- **Foundational (Phase 2)**: T002 after T001; T003 after T002 (tests exercise the schemas)
- **US1 (Phase 3)**: T004 [P] ∥ T005 [P] after T003 (figures/fences mirror real files); T006 after T004+T005; T007 after T006
- **US2 (Phase 4)**: T008 after T006 (needs the chapter's actual fences)
- **US3 (Phase 5)**: T009 after T007 (translates the FINAL en); T010 after T009
- **Polish (Phase 6)**: T011 after all; T012 last

### User Story Dependencies

- **US1 (P1)**: Setup + Foundational — the MVP
- **US2 (P2)**: needs US1's chapter text (the fence contract is bidirectional)
- **US3 (P3)**: needs US1 final

### Parallel Opportunities

- T004 (manifest flip) ∥ T005 (figures) — different files, both downstream of T003

## Parallel Example

```bash
# Serial spine: T001 → T002 → T003
# After T003:  lane A: T004 (manifest flip)   lane B: T005 (figures)
# Then serial: T006 → T007 → T008 → T009 → T010 → T011 → T012
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. T001–T007 — the package green with real reject tests and the English chapter live
2. **STOP and VALIDATE**: battery + the frame-name/derivation sweep (C5)

### Incremental Delivery

1. US1 → the contract chapter readable; package buildable from it
2. US2 → three chapters drift-free at one repo state; tag ready
3. US3 → bilingual flip; every surface incl. the suggestions allowlist updates
4. Polish → 16-row baseline; three-repo handoff with Dong's tag sequence

---

## Notes

- Write T006's fences FROM the T002/T003 files, never from memory — T008
  proves them by diff
- The R2 derivation table is binding: a frame name in prose or figures that
  is neither document-sourced nor a marked DECISION is a C5 failure
- zod's API comes from the installed package (T001), not training-data
  memory — same rule as the bundled Next docs
- Test-file fences are full files with title="" (C3's no-gray-zone rule)
- vi register: settled glossary from the start; "bản giao kèo" is this
  chapter's home turf — the package IS the contract
- NO git commit / git push / git tag — Dong does all three
