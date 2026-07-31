# Tasks: Tutorial Chapter 1.2 — One Command, Whole World

**Input**: Design documents from `/specs/014-chapter-1-2/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chapter-1-2-contract.md, quickstart.md

**Tests**: Not requested as separate tasks — verification is the contract battery
(C4 Docker-free gate + compose replay, C3 fence diffs across BOTH chapters, C2
battery v3, C5 nav), plus `infra.test.ts` which is part of the artifact itself.

**Organization**: The second two-artifact feature (code increment + chapter),
adding one rule to 013's pattern: **additive-only** — no file fenced by chapter
1.1 may be modified (that is what keeps 1.1's published fences valid at
`part1-ch2`). Non-negotiables: the fences ARE the contract (file fences diff
clean, en/vi byte-identical, commands replay); the gate stays green **without
Docker**; `up -d --wait` reaches 4× healthy **with** Docker; publishing is the
manifest flip alone; **commits, pushes, AND the tag are Dong's**.

**⚠ Standing instructions**: Do NOT run `git commit` / `git push` / `git tag`
(Dong does all three). Part 0 and chapter 1.1 content files are byte-untouched.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files/repos, no dependencies)
- **[Story]**: US1 = the chapter, US2 = the code at `part1-ch2`, US3 = the bilingual flip

## Path Conventions

- Platform: `/home/dong/work/relay/relay-platform/` (existing submodule, additive changes only)
- Chapter: `relay-tutorial/app/(en)/part-1/chapter-02/one-command-whole-world/` (+ vi mirror)
- Sources: docs/04 NFR-MNT-03 (L609), docs/05 §8 deployment sentence (L567) + §9 ADR-02/03/04/06/07/08/10 + CON-01, docs/06 deep dives, docs/07 §2–3
- Battery reference: contracts C2; baseline lands at `specs/014-chapter-1-2/battery-baseline.txt` (14 rows)

---

## Phase 1: Setup

**Purpose**: Pin the image reality the compose file and chapter prose will quote

- [X] T001 Verify the container toolchain and pin the four image tags (research R1): `docker compose version` confirms Compose v2 with `--wait`; `docker pull` the current stable candidates — `postgres:<major>-alpine`, `redis:<major>-alpine`, `nats:<2.x>-alpine`, `clickhouse/clickhouse-server:<current LTS>` — and record the exact pullable tags (these become fences; a nonexistent tag in prose is a broken chapter); pinned tags MUST satisfy the constitution's floors (PostgreSQL 15+, ClickHouse 24+ — Technology & Platform Constraints); note each image's in-container probe tooling for R6 (pg_isready present, redis-cli present, wget/curl availability in nats and clickhouse images) in the task record for T002

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The platform increment every chapter fence will mirror — built additive-only

- [X] T002 Create /home/dong/work/relay/relay-platform/compose.yaml per research R1 + data-model (infrastructure declaration): project `name: relay`; services `postgres` (T001's tag, env POSTGRES_USER/PASSWORD/DB relay/relay/relay, volume postgres-data, port 5432, healthcheck `pg_isready -U relay -d relay`), `redis` (NO volume — deliberate, ADR-07/10), `nats` (command `-js -sd /data -m 8222`, volume nats-data, ports 4222+8222, HTTP healthz probe), `clickhouse` (volume clickhouse-data, ports 8123+9000, HTTP /ping probe); healthcheck timings per R6 (5s/3s/5 retries, generous start_period for postgres); then verify on this machine: `docker compose up -d --wait` exits 0, `docker compose ps` shows all four `(healthy)`, `docker compose down` and `down -v` both clean (FR-002..004, C4); adjust probe syntax to in-image reality from T001, the file is truth
- [X] T003 Extend the gate additively in /home/dong/work/relay/relay-platform/packages/config/src/: NEW infra.ts (`INFRA_SERVICES = ["postgres", "redis", "nats", "clickhouse"] as const`, `COMPOSE_FILE = "compose.yaml"`, header comment naming the additive-only rule) and NEW infra.test.ts (readFileSync the repo-root compose.yaml as text — same repoRoot pattern as index.test.ts; assert every INFRA_SERVICES name appears as a `  <name>:` service key, `healthcheck:` occurrences ≥ 4, `postgres-data`/`nats-data`/`clickhouse-data` present, `redis-data` ABSENT); also append the infra section to relay-platform/README.md (never fenced — safe to edit); DO NOT touch any 1.1-fenced file (root package.json, pnpm-workspace.yaml, tsconfig.base.json, eslint.config.mjs, vitest.config.ts, packages/config/{package.json,tsconfig.json,src/index.ts,src/index.test.ts}, .gitignore); then with the Docker daemon STOPPED: `pnpm install && pnpm lint && pnpm typecheck && pnpm test` all green (FR-006, R3/R4, C4)

---

## Phase 3: User Story 1 - Read chapter 1.2 and stand up the local infrastructure alongside it (Priority: P1) 🎯 MVP

**Goal**: The English chapter live — NFR-MNT-03 as a day-one requirement, the four stores each argued from its ADR, the started≠ready TRAP, one honest command.

**Independent Test**: A reader with the 1.1 workspace can add the infrastructure from the chapter alone, see `up -d --wait` return healthy, and the gate still pass; battery v3 green (quickstart V2, V4).

### Implementation for User Story 1

- [X] T004 [P] [US1] Flip chapter 1.2 in relay-tutorial/lib/tutorial.ts per data-model's manifest-entry-transition table (013 seeded the entry with placeholders — this task UPDATES them, it does not add a new entry): `status` forthcoming → `"published"`; add `translatedIn: ["vi"]`; `readerMinutes` 90 → 60 (deliberate); `readerProduces` reworded to "A one-command local infrastructure — four stores, healthchecked and verified"; add `readerProducesVi` "Hạ tầng local một câu lệnh — bốn store, có healthcheck và đã kiểm chứng"; `sourceDoc` "docs/05-sad.md" → "docs/04-srs.md, docs/05-sad.md"; title/titleVi/path/id untouched; NOTHING outside this one entry changes in the file; `pnpm build` green (expected-404 window for 1.2 until T006) (FR-008, R5)
- [X] T005 [P] [US1] Create relay-tutorial/app/(en)/part-1/chapter-02/one-command-whole-world/figures.ts per research R2: figStoreMap (the four stores with their ADR labels + ghosted future services above them), figStartedVsReady (two timelines — container start events vs. healthcheck-ready events; the gap is the TRAP), figComposeGate (compose up --wait → 4× healthy → lint/typecheck/test → tag `part1-ch2`); labels detector-clean, PlantUML palette via the shared MermaidDiagram (FR-005)
- [X] T006 [US1] Author the English chapter in relay-tutorial/app/(en)/part-1/chapter-02/one-command-whole-world/page.mdx per research R2's nine beats: metadata (title "One command, whole world — Building Relay", description, canonical + hreflang pair); `<ChapterHeader id="1.2" />`; cold open from the 1.1 checkpoint; NFR-MNT-03 quoted verbatim ("The full stack shall be startable locally with a single command", P1) with D8 as the why; `<SkipAhead>` naming tag `part1-ch2`; the tools-check paragraph (Docker Engine + Compose v2 via `docker compose version`, `--wait` required, one official-install-docs pointer — the readers-without-Docker edge case, R2 beat 4); the four-store WHY tour with verbatim ADR quotes (ADR-02 "a fraction of Kafka's operational mass"; ADR-07's lossy-by-design; ADR-10 "the correct amount of durability"; ADR-08 + CON-01; ADR-03/04 for Postgres's seat); the full compose.yaml fence (title="compose.yaml", byte-identical to T002's file); the volume-asymmetry paragraph; `<Trap>` started-is-not-ready (naive `up -d`, depends_on orders starts not readiness, healthchecks + `--wait` as the structural fix); the verified-startup walk (command fences: `docker compose up -d --wait`, `docker compose ps`, teardown semantics down vs down -v); `<Why>` #2 (NFR-MNT-03 · D8 — verification is part of the requirement); the gate-learns-the-world section (infra.ts + infra.test.ts fences with title paths, the additive-only rule taught); `<ForwardRef>` (MinIO + seeded tenant per the SAD's full sentence; 1.3 protocol package; 1.4 walking skeleton plugs in); the three `<Figure/>`s per the halves rule; your-turn exercises (incl. "kill a healthcheck and watch --wait hang" style probes); takeaways; one closing `<Checkpoint>` (workspace + 4× healthy + gate green); `<ChapterFooter id="1.2" />` (FR-001..005, 007)
- [X] T007 [US1] Run the en battery per quickstart V4: prose-only words 2,000–4,000; Why ≥2, Trap ≥1, SkipAhead =1 naming part1-ch2, ForwardRef ≥1, Checkpoint =1; figures 3 captioned, halves OK; verbatim spot-checks (NFR-MNT-03, ADR quotes) wrap-tolerant against docs/04/05; ID detector clean over page.mdx + figures.ts; `pnpm lint && pnpm build` (both 1.2 routes appear); fix findings (C2, C6)

**Checkpoint**: The infrastructure chapter readable end to end — MVP delivered

---

## Phase 4: User Story 2 - The canonical code advances to tag `part1-ch2` (Priority: P2)

**Goal**: The increment proven additive and drift-free; the first incremental tag ready for Dong.

**Independent Test**: Gate green Docker-free; compose replay healthy with Docker; every 1.2 fence AND every 1.1 fence diffs clean at HEAD (quickstart V1–V3).

### Implementation for User Story 2

- [X] T008 [US2] Prove the two-chapter no-drift contract per quickstart V1–V3: (a) `git -C relay-platform status --porcelain` shows ONLY new/untracked compose.yaml + infra.ts + infra.test.ts + modified README.md — any other modification violates R3, STOP and redesign; (b) Docker daemon stopped → full gate green (V1); (c) daemon up → `up -d --wait` / `ps` 4× healthy / `down`, plus the `down -v` reset path (V2); (d) fence enumeration: extract every title'd file fence from BOTH locales' 1.2 page.mdx and byte-diff against relay-platform files, then RE-RUN 1.1's ten fence diffs unchanged (V3); (e) SkipAhead names `part1-ch2` exactly; record the diff list in the task record (FR-006/007, SC-002/003)

**Checkpoint**: Chapter, code, and the previous chapter's promises all hold at one repo state

---

## Phase 5: User Story 3 - The forthcoming entry flips to published, bilingually (Priority: P3)

**Goal**: The vi chapter at the corrected register; every navigation surface reflecting the flip.

**Independent Test**: 1.2 reachable ≤2 steps both locales; 1.1↔1.2 footer cards live; sidebar 2+2; sitemap 28; vi parity incl. byte-identical fences (quickstart V5, V7).

### Implementation for User Story 3

- [X] T009 [US3] Create the Vietnamese chapter: relay-tutorial/app/(vi)/vi/part-1/chapter-02/one-command-whole-world/figures.ts (labels translated; store/service/command names English) and page.mdx translated from the FINAL en file per research R7 — meaning-first, no structural calques, no hyphenated compounds; glossary: "cửa ải"+"vượt qua", "package" never "gói", "quả ngọt", "bản giao kèo", "tin nhắn"; dev terms English (healthcheck, volume, image, container, compiler, test runner); ALL 1.2 code fences byte-identical to en incl. title attributes; vi metadata from the manifest titleVi + " — Building Relay"; `locale="vi"` on shell and boxes; finish with a naturalization self-review pass BEFORE presenting (FR-009, C7)
- [X] T010 [US3] Run the series battery per quickstart V5 + V7 against a build/dev server: both 1.2 routes 200 with hreflang; 1.1's footers (both locales) show the 1.2 next card and 1.2's footers show 1.1 prev + no next; sidebar Part 1 exactly 2 links + 2 forthcoming; both landings link 1.2; sitemap == 28 URLs; og/TechArticle on the new pages; en/vi fence extraction diff empty; box/figure counts en == vi; glossary sweep clean ("gói", "cánh cổng", "trình biên dịch/trình chạy test", calque hyphens all absent from the new chapter); `git diff` confirms the manifest flip is the only source edit outside the two new chapter directories; fix findings (C1, C5, C7)

**Checkpoint**: All three stories independently verified

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full validation, the 14-row baseline, the three-repo handoff

- [X] T011 Run the complete quickstart V1–V7 for specs/014-chapter-1-2/quickstart.md end to end and record results: regenerate the battery baseline across ALL 14 chapter files writing specs/014-chapter-1-2/battery-baseline.txt — the 12 pre-existing rows MUST be byte-identical to specs/013-chapter-1-1/battery-baseline.txt (any change = defect); re-verify the docs mirror is drift-free (`pnpm check:docs`); flag V8 prominently — Dong's vi read-through, the 60-minute reader-path walk, figures both themes/375 px, and the post-push tagged-clone replay
- [X] T012 Handoff (NO commits/tags/pushes — standing instruction): report per-repo ready-to-commit files — relay-platform (compose.yaml, infra.ts, infra.test.ts, README.md; Dong's exact sequence `git add -A && git commit && git tag part1-ch2 && git push origin main --tags`), relay-tutorial (manifest flip + 2 page.mdx + 2 figures.ts), parent (both submodule pins + specs/014 incl. battery-baseline.txt + CLAUDE.md/feature.json) — with suggested messages; remind that the live site needs `docker compose up -d --build` to redeploy; request Dong's V8 items before the push

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 first (tags and probe reality feed T002)
- **Foundational (Phase 2)**: T002 after T001; T003 after T002 (the test reads the compose file)
- **US1 (Phase 3)**: T004 [P] ∥ T005 [P] after T003 (fences/figures mirror the real files); T006 after T004+T005; T007 after T006
- **US2 (Phase 4)**: T008 after T006 (the enumeration needs the chapter's actual fences)
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

1. T001–T007 — the infrastructure healthy on this machine and the English chapter live
2. **STOP and VALIDATE**: battery v3 + a manual read of the compose walk

### Incremental Delivery

1. US1 → the chapter readable; infrastructure buildable from it
2. US2 → additive-only proven; both chapters drift-free at one repo state; tag ready
3. US3 → the flip drill demonstrated bilingually; every surface updates
4. Polish → 14-row baseline; the three-repo handoff with Dong's tag sequence

---

## Notes

- Write T006's fences FROM the repo files (T002/T003 outputs), never from
  memory — T008 proves them by diff
- The additive-only check (T008a) is a hard gate: if implementation needs to
  edit a 1.1-fenced file, that is a surfaced design change, not a silent edit
- Image tags in compose.yaml are fences — only tags T001 actually pulled
- The gate must be demonstrated with the Docker daemon STOPPED (V1) — "green
  because containers happened to be up" proves nothing
- vi register: the July 2026 corrections are the starting standard, not a
  post-hoc fix ("cửa ải", "package", meaning-first)
- NO git commit / git push / git tag — Dong does all three
