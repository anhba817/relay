# Tasks: Tutorial Chapter 1.1 — The Monorepo and the Toolchain

**Input**: Design documents from `/specs/013-chapter-1-1/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chapter-1-1-contract.md, quickstart.md

**Tests**: Not requested as separate tasks — verification is the contract battery
(C1 fresh-clone replay, C3 battery v3, C4 enumerated fence diffs, C2 nav/SEO),
plus the scaffold's own smoke test (part of the artifact, not test scaffolding).

**Organization**: The series' first two-artifact feature: a code scaffold
(relay-platform) + the chapter that builds it. Non-negotiables: **the chapter's
fences ARE the contract** (file fences diff clean against the repo; command
fences replay clean; en/vi fences byte-identical); **battery v3** (prose-only
word counts — fences stripped; TRAP counted; fence cap lifted for code
chapters); **the runnable-tested end state** (three checks green at HEAD, then
at `part1-ch1` once tagged); **commits, pushes, AND the tag are Dong's**.

**⚠ Standing instructions**: Do NOT run `git commit` / `git push` / `git tag`
(Dong does all three). Part 0 chapter files are byte-untouched.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files/repos, no dependencies)
- **[Story]**: US1 = the chapter, US2 = canonical code at the tag, US3 = Part 1 opens bilingually

## Path Conventions

- Scaffold: `/home/dong/work/relay/relay-platform/` (new submodule)
- Chapter: `relay-tutorial/app/(en)/part-1/chapter-01/the-monorepo-and-the-toolchain/` (+ vi mirror)
- Sources: docs/05 §9 ADR-01, docs/06 ADR-01 deep dive, docs/07 §2–3
- Battery reference: contracts C3/C5; baseline lands at `specs/013-chapter-1-1/battery-baseline.txt`

---

## Phase 1: Setup

**Purpose**: Attach the second submodule

- [X] T001 Add the relay-platform submodule at the parent repo root: `git submodule add https://github.com/anhba817/relay-platform relay-platform` (repo exists, empty — clone warning expected); confirm `.gitmodules` gains the entry beside relay-tutorial and `relay-platform/` is an empty work tree with its own `.git` link (FR-006, research R6)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The scaffold (every chapter fence mirrors it) and the amended format authority

- [X] T002 [P] Amend /home/dong/work/relay/docs/07-tutorial-plan.md §2's format table for code chapters per data-model E4: extend the Visual-elements/format rows with the code-chapter battery note — canonical words count prose OUTSIDE code fences ("2,000–4,000 words + code" made mechanical), code fences uncapped but counted, `TRAP` a counted box class (≥1 in code chapters), specimen verbatim rules unchanged; then `pnpm check:docs` in relay-tutorial (mirror drift) and `pnpm sync:docs` + note the mirror refresh for the commit (FR-005, research R3)
- [X] T003 Build the scaffold in /home/dong/work/relay/relay-platform per data-model E1 and research R1: root package.json (`packageManager` pnpm pin, engines node >=22, scripts `lint`/`typecheck`/`test`), pnpm-workspace.yaml (`packages/*`, `services/*`), strict tsconfig.base.json, flat eslint.config.mjs (typescript-eslint) + .prettierrc, vitest config, .gitignore/.nvmrc/README.md (reader-facing: what this repo is, the tag convention, the three checks), packages/config as `@relay/config` (package.json, tsconfig extending base, src/index.ts, src/index.test.ts — one meaningful passing smoke test); config ownership is SINGLE-HOMED per the chapter's own TRAP: the root tsconfig.base.json is the one compiler source (packages extend it by relative path), while `@relay/config` exports runtime constants the smoke test exercises and is the designated future home for lint/test fragments as packages multiply — the chapter narrates exactly this split; services/.gitkeep; then `pnpm install && pnpm lint && pnpm typecheck && pnpm test` all green; NO Turborepo/Nx (C1 discipline)

---

## Phase 3: User Story 1 - Read chapter 1.1 and build the workspace alongside it (Priority: P1) 🎯 MVP

**Goal**: The English chapter live — decisions summary, ADR-01 through the build, TRAP debut, three figures, runnable-tested close.

**Independent Test**: A Part 0 reader (or a skipper via the opening summary) can build the workspace from the chapter alone and see the three checks pass; battery v3 green (quickstart V2, V5.1).

### Implementation for User Story 1

- [X] T004 [P] [US1] Add Part 1's four chapters to relay-tutorial/lib/tutorial.ts per data-model E2: 1.1 published + `translatedIn: ["vi"]` (path `/part-1/chapter-01/the-monorepo-and-the-toolchain`, title "The monorepo and the toolchain", titleVi "Monorepo và bộ công cụ", readerProduces "A running pnpm workspace — TypeScript, lint, and a passing test suite" + readerProducesVi "Một pnpm workspace chạy được — TypeScript, lint, và bộ test xanh", sourceDoc "docs/05-sad.md, docs/06-adr-deep-dives.md", readerMinutes 90); 1.2–1.4 forthcoming with docs/07 titles + draft vi titles ("Một câu lệnh, cả thế giới" / "Gói protocol" / "Bộ khung biết đi") and reserved paths; ALSO create the part-1 reading-shell layouts — relay-tutorial/app/(en)/part-1/layout.tsx and app/(vi)/vi/part-1/layout.tsx as byte-level copies of the part-0 mounts (ReadingLayout + prose container; without them 1.1 renders bare — FR-001); `pnpm build` green (expected-404 window for 1.1 until T006) (FR-008)
- [X] T005 [P] [US1] Create relay-tutorial/app/(en)/part-1/chapter-01/the-monorepo-and-the-toolchain/figures.ts per research R2 beat 6: figWorkspaceMap (root → packages/* → services/* with 1.2–1.4 ghosted), figProtocolPayoff (`@relay/protocol` consumed by gateway + API + SDK — "one commit, not a production incident"), figToolchainGate (lint → typecheck → test as the gate every chapter passes); labels detector-clean (FR-005)
- [X] T006 [US1] Author the English chapter in relay-tutorial/app/(en)/part-1/chapter-01/the-monorepo-and-the-toolchain/page.mdx per research R2's eight beats: metadata (title "The monorepo and the toolchain — Building Relay", description, hreflang pair); `<ChapterHeader id="1.1" />`; the gear-change cold open; the one-page decisions summary (FR-002 — compact list, links back to Part 0); ADR-01 taught with verbatim deep-dive quotes ("the SDK must be TypeScript regardless"; drift "becomes a compile error instead of a production incident"; the polyglot rejection; revisit-when); the build walk — every command fence and file fence EXACTLY matching T003's scaffold (FR-007); `<Trap>` debut (config copy-paste drift per R2 beat 5); the three `<Figure/>`s placed per the halves rule; `<Why>` ×2 (ADR-01/D8; the config-package rationale); `<SkipAhead>` naming tag `part1-ch1`; `<ForwardRef part="Parts 1–2">` (1.3's protocol package; 2.x reusing the checks); exercise-is-the-build note; takeaways; one closing `<Checkpoint>` (the three checks green); `<ChapterFooter id="1.1" />` (FR-001..005)
- [X] T007 [US1] Run the en battery per quickstart V2: prose-only words 2,000–4,000; Why ≥2, Trap ≥1, SkipAhead =1, ForwardRef ≥1, Checkpoint =1; figures 3 with captions and halves OK; ADR-01 wrap-tolerant spot-checks; ID detector clean over page.mdx + figures.ts; `pnpm lint && pnpm build` (both 1.1 routes appear); fix findings

**Checkpoint**: The first code chapter readable end to end — MVP delivered

---

## Phase 4: User Story 2 - The canonical code exists at a per-chapter tag (Priority: P2)

**Goal**: The scaffold proven from a fresh clone; the chapter↔code contract enumerated and green; the tag handed to Dong.

**Independent Test**: Fresh clone → install → lint → typecheck → test, all exit 0; every enumerated file fence diffs clean; SKIP AHEAD names `part1-ch1` (quickstart V1, V3).

### Implementation for User Story 2

- [X] T008 [US2] Prove the no-drift contract: run quickstart V1's PRE-COMMIT stage (clean work-tree copy → `pnpm install && pnpm lint && pnpm typecheck && pnpm test` all green — a git clone is impossible until Dong's first commit; the true tagged-clone replay is a post-push follow-up named in the handoff); complete quickstart V3's enumeration — one diff line per file-content fence in the chapter (pnpm-workspace.yaml, tsconfig.base.json, eslint.config.mjs, packages/config/*, root package.json scripts — whatever T006 shows) — and run every diff (must be empty) plus the command-fence replay order; confirm the SkipAhead text names `part1-ch1` exactly (FR-006/007, SC-002/003)

**Checkpoint**: Chapter and code cannot drift; the tag command is ready for Dong

---

## Phase 5: User Story 3 - Part 1 opens across the bilingual series (Priority: P3)

**Goal**: The vi chapter; every navigation surface reflecting the Part boundary.

**Independent Test**: 1.1 reachable ≤2 steps both locales; 0.5's next card live; sidebar Part 1 = 1 link + 3 forthcoming; sitemap 26; vi parity incl. byte-identical fences (quickstart V2 fence-diff, V4).

### Implementation for User Story 3

- [X] T009 [US3] Create the Vietnamese chapter: relay-tutorial/app/(vi)/vi/part-1/chapter-01/the-monorepo-and-the-toolchain/figures.ts (labels translated per glossary; package/tool names English) and page.mdx translated from the FINAL en file in the naturalized register (the 0.5 standard — "tin nhắn", no calques); ALL code fences byte-identical to en; identifiers/tag/package names English; vi metadata title from the manifest + " — Building Relay"; `locale="vi"` on shell and boxes (FR-009)
- [X] T010 [US3] Run the series battery per quickstart V4 + V2's parity checks with the dev server: both 1.1 routes 200 with hreflang ≥2; 0.5's footers show the next card (both locales — the empty-next state retires); sidebar shows Part 1 with exactly 1 link + 3 forthcoming entries; sitemap == 26; og:title/TechArticle on the new pages; en/vi fence extraction diff empty; box/figure counts en == vi; fix findings

**Checkpoint**: All three stories independently verified

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full validation, the v3 baseline, the three-repo handoff

- [X] T011 Run the complete quickstart V1–V6 for specs/013-chapter-1-1/quickstart.md and record results: scaffold replay (V1), full battery v3 across ALL 12 chapter files writing specs/013-chapter-1-1/battery-baseline.txt (V2 — Part 0 rows must match the 011 baseline on every column except words, which shifts formula-side only), fence enumeration diffs (V3), nav/SEO (V4), docs/07 note + mirror drift (V6); flag V5 prominently — the reader-path walkthrough against readerMinutes 90, figures in both themes/375 px, and Dong's vi read-through incl. the four new manifest vi titles
- [X] T012 Handoff (NO commits/tags/pushes — standing instruction): report per-repo ready-to-commit files — relay-platform (the entire scaffold; include Dong's exact sequence `git add -A && git commit && git tag part1-ch1 && git push origin main --tags`), relay-tutorial (manifest + 2 page.mdx + 2 figures.ts + refreshed content/docs mirror if docs/07 changed), parent (.gitmodules + both submodule pins + docs/07 + specs/013 incl. battery-baseline.txt + CLAUDE.md/feature.json) — with suggested messages marking the Part 1 opening milestone; request Dong's V5 items before the push

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 first (the work tree must exist)
- **Foundational (Phase 2)**: T002 [P] ∥ T003 (different repos); T003 after T001
- **US1 (Phase 3)**: T004 [P] ∥ T005 [P] after T003 (fences/figures mirror the real scaffold); T006 after T004+T005; T007 after T006
- **US2 (Phase 4)**: T008 after T006 (the enumeration needs the chapter's actual fences)
- **US3 (Phase 5)**: T009 after T007 (translates the FINAL en); T010 after T009
- **Polish (Phase 6)**: T011 after all; T012 last

### User Story Dependencies

- **US1 (P1)**: Setup + Foundational — the MVP
- **US2 (P2)**: needs US1's chapter text (the fence contract is bidirectional)
- **US3 (P3)**: needs US1 final

### Parallel Opportunities

- T002 (docs/07) ∥ T003 (scaffold) — different repos
- T004 (manifest) ∥ T005 (figures) — different files, both downstream of T003

## Parallel Example

```bash
# After T001:  lane A: T003 (scaffold)   lane B: T002 (docs/07 amendment)
# After T003:  lane A: T004 (manifest)   lane B: T005 (figures)
# Then serial: T006 → T007 → T008 → T009 → T010 → T011 → T012
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. T001–T007 — the scaffold green and the English chapter live
2. **STOP and VALIDATE**: battery v3 + a manual read of the build walk

### Incremental Delivery

1. US1 → the first code chapter readable, workspace buildable from it
2. US2 → chapter↔code proven drift-free; tag ready
3. US3 → Part 1 opens bilingually; every surface updates
4. Polish → v3 baseline; the three-repo handoff with Dong's tag sequence

---

## Notes

- The fences are the contract: write T006 FROM the scaffold files, never from
  memory — then T008 proves it by diff
- Battery v3's fence-strip is a FORMULA change: if any Part 0 row changes in a
  non-words column, that is a defect, not drift
- The tag `part1-ch1` is Dong's to create — SkipAhead references it before it
  exists; the handoff makes that explicit
- vi code fences byte-identical to en — translation applies to prose only
- NO git commit / git push / git tag — Dong does all three
