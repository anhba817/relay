# Tasks: Tutorial Chapter 1.4 — Walking Skeleton

**Input**: Design documents from `/specs/017-chapter-1-4/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chapter-1-4-contract.md, quickstart.md

**Tests**: Not requested as separate tasks — verification is the contract
battery (C4 gate ≥40 + living-skeleton walk, C3 four-chapter fence diffs, C2
battery v3, C5 derivation fidelity, C6 Part-1-complete nav); the service test
suites are part of the artifact itself.

**Organization**: Part 1's finale, fourth two-artifact feature.
Non-negotiables: **zero new external dependencies** (node builtins +
`workspace:*` only, R3); **additive-only over all twenty prior fences** (root
package.json, compose.yaml, packages/{config,protocol} are read-only — start
services via per-package scripts + `pnpm --filter`, never root scripts);
research R2's derivation table is the law (derive or mark DECISIONs);
observability honesty (tenant/correlation IDs are recorded deferrals); fences
byte-match, en/vi byte-identical; publishing is the manifest flip alone —
**Part 2 is NOT seeded**; **commits, pushes, AND the tag are Dong's**.

**⚠ Standing instructions**: Do NOT run `git commit` / `git push` / `git tag`
(Dong does all three). Part 0 and chapters 1.1–1.3 content files are
byte-untouched. Flag (never delete) any rows verification adds to Dong's Neon.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = the chapter, US2 = the code at `part1-ch4`, US3 = Part 1 completes bilingually

## Path Conventions

- Platform: `/home/dong/work/relay/relay-platform/` — NEW members only: `packages/service-kit/`, `services/api/`, `services/gateway/`
- Chapter: `relay-tutorial/app/(en)/part-1/chapter-04/walking-skeleton/` (+ vi mirror)
- Sources: docs/04 (EIR-API-04 L188, EIR-API-05 L189, NFR-OBS-01/02/06 L596–601), docs/05 (§4.1 L154–172, §4.2, ADR-04/05), constitution (observability clause), docs/07 §3 L119 + §5
- Derivation: research R2; contract C5 makes it binding
- Battery baseline: `specs/017-chapter-1-4/battery-baseline.txt` (18 rows)

---

## Phase 1: Setup

**Purpose**: Pin the runtime reality the chapter's commands will claim

- [X] T001 Verify the zero-dependency run path on this machine (R3): `node --version` ≥ 22.18 (reference: 22.20); create a throwaway .ts file with an erasable-syntax type annotation in the scratchpad, run it with plain `node` to confirm type stripping executes without flags, then delete it; confirm TypeScript ~5.9 accepts `"erasableSyntaxOnly": true` (tsc --help or a scratch tsconfig check); record both facts for the chapter's prose and the R2/R3 claims — if either fails, STOP and surface (the run pattern is the chapter's spine)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The three additive workspace members every chapter fence will mirror

- [X] T002 Create packages/service-kit in /home/dong/work/relay/relay-platform/ per data-model + research R1/R2: package.json (name "@relay/service-kit", private, type module, exports "." → "./src/index.ts", typecheck script, NO dependencies), tsconfig.json (extends ../../tsconfig.base.json, compilerOptions.erasableSyntaxOnly true, include src); src/index.ts — structured logger writing one JSON object per line ({time ISO, level, service, msg, request_id?} — NFR-OBS-01 cited, tenant/correlation deferral noted in header comment) with an injectable sink (default process.stdout) for testability (R4); newRequestId() via crypto.randomUUID (EIR-API-05 uniqueness, format is a DECISION); serve() helper over node:http — takes {service, port, routes}, stamps X-Request-Id on EVERY response (EIR-API-05), logs one line per request with that id, wires GET /healthz to the provided health payload fn, answers unknown routes with the EIR-API-04-shaped 404 {code:"not_found", message, docs_url}; src/index.test.ts — log lines are valid JSON with required fields, request ids unique and UUID-shaped, sink injection works; lint+typecheck green (FR-003)
- [X] T003 Create the two services per data-model: services/api/ (@relay/api — package.json with dependencies {"@relay/protocol":"workspace:*","@relay/service-kit":"workspace:*"}, dev script "node --watch src/main.ts", tsconfig identical to service-kit's; src/main.ts — createServer() factory via the kit's serve(): service "api", default port 4000 (PORT overridable), /healthz → {status:"ok",service:"api",uptime_s}; main.ts listens only when run directly; "typecheck": "tsc --noEmit" script (U2: the root gate uses --if-present — a service without the script is silently skipped); src/main.test.ts — boot on port 0, fetch /healthz → 200 + shape + X-Request-Id UUID + distinct across two requests, /nope → 404 whose body PARSES against errorFrameSchema's payload schema imported from @relay/protocol (H1: the REST/WS error-shape alignment made executable — api's protocol dependency is real, honoring 1.3's ForwardRef)) and services/gateway/ (@relay/gateway — same pattern incl. the typecheck script, port 4001; /healthz payload additionally carries protocol:{frames, close_codes} computed at runtime from @relay/protocol — introspect the discriminated union against the INSTALLED zod 4 API (frameSchema.options → each option's type literal; verify the exact accessor in node before writing), close_codes from Object.keys(CLOSE_CODES).map(Number); test asserts the advertisement matches the package: 10 frame names incl. connection.ack, codes [4001,4002,4008,4009]); append a "Running the services" section to relay-platform/README.md (start commands, ports 4000/4001, the Node ≥ 22.18 type-stripping floor — U1; README was never fenced, the 1.2 precedent); then `pnpm install` and the full gate: `pnpm lint && pnpm typecheck && pnpm test` green with ≥40 tests, Docker-free; additive check — `git -C relay-platform status --porcelain` shows ONLY the three new members (+ lockfile); zero external deps in all three package.json files (FR-004/006, C4)

---

## Phase 3: User Story 1 - Read chapter 1.4 and stand the skeleton up alongside it (Priority: P1) 🎯 MVP

**Goal**: The English chapter live — skeleton-before-muscles taught from SAD §4.1's own division of labor, observability derived honestly, the living-skeleton walk demonstrated.

**Independent Test**: A reader with the 1.3 checkpoint can build all three members from the chapter, start both services, see health + request IDs + structured logs, and pass the gate (quickstart V1, V2, V4).

### Implementation for User Story 1

- [X] T004 [P] [US1] Flip chapter 1.4 in relay-tutorial/lib/tutorial.ts per data-model's transition table (UPDATE the 013 seed): status → "published"; add translatedIn: ["vi"]; readerMinutes → 90; readerProduces → "Two running skeleton services — health-checked, request-ID'd, logging structured JSON"; add readerProducesVi "Hai service bộ khung chạy được — có health check, request ID, log JSON có cấu trúc"; sourceDoc → "docs/04-srs.md, docs/05-sad.md"; title/titleVi/path/id untouched; NOTHING outside this one entry — Part 2 is NOT added; `pnpm build` green (expected-404 window until T006) (FR-008, R6)
- [X] T005 [P] [US1] Create relay-tutorial/app/(en)/part-1/chapter-04/walking-skeleton/figures.ts per research R7: figSkeletonMap (the SAD's six services with api + gateway SOLID and annotated healthz/request-id/logs, the other four ghosted with their parts), figRequestThread (one request: client → service → X-Request-Id response header AND the same id in the JSON log line → grep-ability, NFR-OBS-06), figPartOneComplete (the four-chapter arc: workspace → compose → protocol → skeleton, each with its tag, ending "Part 1 ✓ — Part 2 grows the muscles"); labels detector-clean, service/frame names document-derived only (FR-005, C5)
- [X] T006 [US1] Author the English chapter in relay-tutorial/app/(en)/part-1/chapter-04/walking-skeleton/page.mdx per research R7's nine beats: metadata (title "Walking skeleton — Building Relay", description, canonical + hreflang); `<ChapterHeader id="1.4" />`; the Part-1-finale cold open; `<SkipAhead>` naming part1-ch4 with the start commands + gate; `<Why>` #1 (SAD §4.1 · ADR-04/05 — why these two services first, the division-of-labor sentences quoted verbatim); the observability derivation walk (EIR-API-05 quoted, NFR-OBS-01's fields with the tenant/correlation deferral recorded out loud, NFR-OBS-06 as the why, every R2 DECISION row with its marker sentence — request-id format, /healthz path+shape, ports, not_found placement); `<Trap>` the-second-copy (paste the logger into both services → 1.1's drift disease on behavior; fix = service-kit) with the kit fences (package.json, tsconfig — noting the two services' tsconfigs are the identical file, src/index.ts); the two services' fences (package.json ×2, main.ts ×2) with the gateway's protocol advertisement and its 1.3 callback; `<Why>` #2 (Node ≥22.18 type stripping — zero dependencies to run TS, erasableSyntaxOnly as compiler-enforced guarantee, the runtime floor stated honestly against the fenced engines line); the run-it walk (command fences: pnpm --filter dev ×2, curl /healthz, curl the 404; response header + log line shown in prose/output discussion, not fake output fences); the test fences (kit + both services) and the gate command fence; the three `<Figure/>`s per halves; `<ForwardRef>` (Part 2 muscles: JWT, sessions, stores, real send path; deferred log fields arrive with features; containers in Part 6; two terminal tabs are honest at this scale); your-turn exercises (kill one service — the other keeps answering; grep one request id across interleaved logs; add a temp route and watch the 404 test object); takeaways; one closing `<Checkpoint>` (both services answer, ids thread through logs, gate ≥40 — Part 1 done); `<ChapterFooter id="1.4" />` — ALL file fences pasted from the real T002/T003 files (FR-001..005, 007)
- [X] T007 [US1] Run the en battery per quickstart V4 + C5: prose-only words 2,000–4,000; Why ≥2, Trap ≥1, SkipAhead =1 naming part1-ch4, ForwardRef ≥1, Checkpoint =1; figures 3 captioned, halves OK; verbatim spot-checks (EIR-API-05, NFR-OBS-01, SAD §4.1 sentences, EIR-WS/close-code claims) wrap-tolerant; ID detector clean; DECISION-marker sweep (each R2 DECISION row's marker present); `pnpm lint && pnpm build`; fix findings

**Checkpoint**: Part 1's finale readable end to end — MVP delivered

---

## Phase 4: User Story 2 - The canonical code advances to tag `part1-ch4` (Priority: P2)

**Goal**: The increment proven additive across four chapters, alive, and dependency-free.

**Independent Test**: Gate green ≥40 Docker-free; both services answer with threading request IDs; all twenty-plus fences diff clean at one repo state (quickstart V1–V3).

### Implementation for User Story 2

- [X] T008 [US2] Prove the four-chapter no-drift contract per quickstart V1–V3: (a) additive check + zero-external-deps check + erasableSyntaxOnly in all three new tsconfigs; (b) the living-skeleton walk (V2): start both via `pnpm --filter … dev`, curl api /healthz (200, shape, X-Request-Id UUID, unique across requests), curl gateway /healthz (advertisement matches @relay/protocol: 10 frames, [4001,4002,4008,4009]), curl a 404 (EIR-API-04 shape), confirm each request logged exactly one JSON line with the matching request_id, PORT override spot-check, stop both cleanly; (c) fence enumeration — every title'd fence from BOTH locales' 1.4 page.mdx byte-diffed, then ALL prior chapters' fences re-run (1.1×10, 1.2×3, 1.3×7), plus the services' tsconfigs diffed against the fenced kit tsconfig (the identical-in-prose claim); (d) SkipAhead names part1-ch4 exactly; record results (FR-006/007, SC-002/003)

**Checkpoint**: Four chapters' promises hold at one repo state; the skeleton lives

---

## Phase 5: User Story 3 - Part 1 completes across the bilingual series (Priority: P3)

**Goal**: The vi chapter at the settled register; the first part-completion state rendering everywhere.

**Independent Test**: Sidebar Part 1 = 4 links + 0 forthcoming; 1.3↔1.4 cards; 1.4 empty next; sitemap 32; vi parity; allowlist POSTs 201 (quickstart V5, V6).

### Implementation for User Story 3

- [X] T009 [US3] Create the Vietnamese chapter: relay-tutorial/app/(vi)/vi/part-1/chapter-04/walking-skeleton/figures.ts (labels translated; service/frame/command names English) and page.mdx translated from the FINAL en file per research R8 — meaning-first, settled glossary ("bộ khung biết đi" as the title term, "package"/"service" English, "cửa ải"+"vượt qua", "bản giao kèo", "quả ngọt", "tin nhắn"; no calques, hyphenated compounds, "hình hài", or "thành tiếng"); ALL fences byte-identical to en incl. titles (build the vi file by copying en fences verbatim); vi metadata from titleVi + " — Building Relay"; locale="vi" on shell and boxes; naturalization self-review pass BEFORE presenting (FR-009, C7)
- [X] T010 [US3] Run the series battery per quickstart V5 + V6 against a build: both 1.4 routes 200 with hreflang; sidebar Part 1 exactly 4 links + 0 forthcoming (grep the built HTML — no forthcoming badge inside Part 1); 1.3 footers show the 1.4 next card (both locales); 1.4 footers show 1.3 prev + NO next; landings render Part 1 fully linked with Part 2 still road-ahead; sitemap == 32; OG/TechArticle on the new pages; vi banner + suggest invitation; en/vi fence extraction diff empty; box/figure counts equal; glossary sweep clean; `git diff` confirms the manifest flip is the only source edit outside the chapter dirs; allowlist: POST a valid suggestion per new path → 201 (rows flagged for Dong — Neon is live in .env), noting 016's forthcoming-1.4 rejection case now inverts to 201; fix findings (C1, C6, C7)

**Checkpoint**: All three stories independently verified; Part 1 renders complete

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full validation, the 18-row baseline, the Part-1-milestone handoff

- [X] T011 Run the complete quickstart V1–V6 end to end and record results: regenerate specs/017-chapter-1-4/battery-baseline.txt across ALL 18 chapter files (established formula) — the 16 pre-existing rows MUST be byte-identical to specs/016-chapter-1-3/battery-baseline.txt; `pnpm check:docs` clean; flag V7 prominently — Dong's vi read-through, the 90-minute walk, figures both themes/375 px, Neon test-row cleanup, post-push tagged-clone replay, site redeploy (VPS or the pending Vercel migration)
- [X] T012 Handoff (NO commits/tags/pushes — standing instruction): report per-repo ready-to-commit files — relay-platform (the three new members + lockfile; Dong's sequence `git add -A && git commit && git tag part1-ch4 && git push origin main --tags`), relay-tutorial (manifest flip + 2 page.mdx + 2 figures.ts), parent (submodule pins + specs/017 incl. battery-baseline.txt + CLAUDE.md/feature.json) — with suggested messages marking the **Part 1 milestone** (docs/07 §5); note that Part 2's first feature will seed its manifest chapters, and that suggestions on the new pages flow to the live DATABASE_URL

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 first (the run pattern is load-bearing)
- **Foundational (Phase 2)**: T002 after T001; T003 after T002 (services consume the kit)
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

1. T001–T007 — the skeleton alive on this machine and the English chapter live
2. **STOP and VALIDATE**: battery + the DECISION-marker sweep (C5)

### Incremental Delivery

1. US1 → the finale readable; skeleton buildable from it
2. US2 → four chapters drift-free at one repo state; the skeleton demonstrably alive; tag ready
3. US3 → Part 1 completes bilingually; every surface incl. the allowlist updates
4. Polish → 18-row baseline; the Part-1-milestone handoff

---

## Notes

- Write T006's fences FROM the T002/T003 files, never from memory — T008
  proves them by diff
- The zod discriminated-union introspection for the gateway advertisement
  gets verified in node against the installed package BEFORE the code is
  written (T003) — no training-data API memory
- No fake output fences: curl/log output is discussed in prose or shown as
  clearly illustrative, never as a byte-contract fence
- Tests bind port 0 only; services must separate createServer() from listen
  so tests never spawn real ports/processes
- vi register: settled glossary from the first draft; self-review before
  presenting (the suggestions channel is the reader's backstop, not mine)
- NO git commit / git push / git tag — Dong does all three; Neon rows flagged,
  never deleted by me
