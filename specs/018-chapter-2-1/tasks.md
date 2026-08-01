# Tasks: Tutorial Chapter 2.1 — Schema with a Spine

**Input**: Design documents from `/specs/018-chapter-2-1/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/chapter-2-1-contract.md, quickstart.md

**Tests**: Not requested as separate tasks — verification is the contract
battery (C4's two gate lanes, C3's amended fence battery with diff-chain
verification, C2 battery v3, C5 schema fidelity, C6 Part-2-opens nav); the
isolation suite is the chapter's own artifact.

**Organization**: Part 2's opener and the fence discipline's first amendment.
Non-negotiables: **the diff-fence mechanism** (edits to fenced files ONLY as
` ```diff title=""` blocks; pre-image = the predecessor chapter's published
fence text; applying the diff must byte-equal the current file; exactly TWO
amendments this chapter — api package.json, root eslint.config.mjs);
**the unit lane stays Docker-free** (`*.itest.ts` invisible to the fenced
root vitest include); **SAD §6.1 SQL is column-exact** where defined, gaps
carry recorded-decision comments IN the SQL; **integration tests touch only
the local compose Postgres — never the tutorial site's Neon** (fail-fast
guard); **commits, pushes, AND the tag are Dong's**.

**⚠ Standing instructions**: Do NOT run `git commit` / `git push` / `git tag`
(Dong does all three). Part 0 and chapters 1.1–1.4 content files are
byte-untouched. Flag (never delete) any rows verification adds to Dong's
Neon. The compose Postgres on this machine runs remapped
(`RELAY_POSTGRES_PORT=15432`).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: US1 = the chapter, US2 = the code at `part2-ch1` + the amendment mechanism, US3 = Part 2 opens bilingually

## Path Conventions

- Platform: `/home/dong/work/relay/relay-platform/services/api/` (new files) + the two diff-fence targets
- Chapter: `relay-tutorial/app/(en)/part-2/chapter-01/schema-with-a-spine/` (+ vi mirror)
- Sources: docs/04 (FR-TEN-01..06, DR-01/02/03, NFR-SEC-09), docs/05 (§6.1 L332–380 SQL, §6.3 L450–460, D4 L63, ADR-03/04), constitution I + workflow clause, docs/07 §3 L128
- Schema: research R1's table; contract C5 makes it binding
- Battery baseline: `specs/018-chapter-2-1/battery-baseline.txt` (20 rows)

---

## Phase 1: Setup

**Purpose**: Pin the new dependency and confirm the test database reality

- [X] T001 Pin and probe: `pnpm view pg version` for the exact version the diff-fence will carry; bring up the compose Postgres (`RELAY_POSTGRES_PORT=15432 docker compose up -d --wait postgres` in relay-platform) and confirm connectivity with `DATABASE_URL=postgres://relay:relay@localhost:15432/relay` (psql or a node one-liner); verify the pg driver's API basics against the INSTALLED package after install (Pool, transactions) rather than memory; record both facts for T002–T004

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Schema, runner, layer, enforcement — everything the chapter fences

- [X] T002 Create the migration and the plumbing in /home/dong/work/relay/relay-platform/services/api/: migrations/001_core_tables.sql per data-model's schema table — dependency order applications (DECISION stub comment) → environments → users → channels → messages (each column-exact to SAD §6.1 incl. CHECKs, DR-02 UNIQUEs, DR-01 UNIQUE, the DR-03 partial unique index messages_idem, with the SAD's own comment citations) → members (DECISION comment citing docs/07's row + SAD §6.3's index anchor; channel_id/user_id FKs, joined_at, PK(channel_id,user_id)) + the two §6.3 hot-path indexes with citation comments; src/db/client.ts (lazy Pool from DATABASE_URL, default postgres://relay:relay@localhost:5432/relay); src/db/migrate.ts (~50 lines per research R3: schema_migrations bookkeeping table, filename-order apply, per-file transaction, records version, re-run no-op, importable + runnable as entry); apply the R4 diff to services/api/package.json (add pg pinned to T001's version, scripts "migrate": "tsx src/db/migrate.ts" and "test:integration": "vitest run --config vitest.integration.config.ts") — KEEP THE DIFF MINIMAL, it becomes the chapter's diff-fence; verify: migrate applies fresh, re-run is a no-op (FR-003, C4/C5)
- [X] T003 Build the repository layer + enforcement: src/db/repository.ts per research R5 — createEnvironment(pool, {name}) admin surface with the bright-line comment, ALSO inserting the stub application row that satisfies environments' NOT NULL application_id FK (U1 — one INSERT, real lifecycle is Part 3's), all ids app-generated via crypto.randomUUID (L2 — the migration adds no DEFAULTs the SAD lacks), class Repository with constructor(pool, environmentId) and methods users.create/getByExternalId, channels.create/getByExternalId/list, members.add/listForChannel/channelsForUser, every query scoped by this.environmentId (the WHERE lives HERE only), cross-tenant reads → null/empty; apply the R4 diff to /home/dong/work/relay/relay-platform/eslint.config.mjs — no-restricted-imports forbidding "pg" outside services/api/src/db/** (minimal diff, becomes the second diff-fence); then the Docker-free gate green (`pnpm lint && pnpm typecheck && pnpm test` — itest not yet present) and a scratch-violation check: a temporary pg import in src/main.ts must FAIL lint (delete after) (FR-004, C4)
- [X] T004 Write the isolation suite: services/api/vitest.integration.config.ts (include src/**/*.itest.ts only) and src/db/repository.itest.ts per research R5/R6 — setup: fail-fast unless DATABASE_URL host is localhost/127.0.0.1 (the never-Neon guard), run migrations programmatically, TRUNCATE the chapter's tables CASCADE; cases: two environments A/B via createEnvironment (each self-contained incl. its stub application — U1); users/channels/members created in A; B's Repository attacks with A's identifiers → getByExternalId null, lists empty/excluding, channelsForUser empty; DR-02 dual-tenant uniqueness (same external_id in A and B both succeed; duplicate within A rejects); with the compose Postgres up: `pnpm --filter @relay/api test:integration` green AND `pnpm test` (unit lane) provably does NOT collect the itest file; `git -C relay-platform status --porcelain` shows exactly the 6 new files + the 2 diffed files + lockfile (FR-006, C4)

---

## Phase 3: User Story 1 - Read chapter 2.1 and build the schema + repository layer alongside it (Priority: P1) 🎯 MVP

**Goal**: The English chapter live — isolation designed out on the page, the SAD's SQL quoted, the amendment mechanism taught in daylight.

**Independent Test**: A Part-1-complete reader can migrate, build the layer, run both lanes, and explain why isolation lives in data access (quickstart V1–V4 happy paths).

### Implementation for User Story 1

- [X] T005 [P] [US1] Seed Part 2 in relay-tutorial/lib/tutorial.ts per data-model + research R7: the existing Part 2 entry's chapters array gains all eight docs/07 chapters — 2.1 published + translatedIn ["vi"] with R7's full values (path /part-2/chapter-01/schema-with-a-spine, titleVi "Schema có xương sống", readerProduces/Vi, sourceDoc, readerMinutes 90); 2.2–2.8 forthcoming with reserved paths (the-write-path, send-it-twice, history-that-pages, the-socket, two-servers-one-conversation, the-tunnel, milestone-the-tuan-test), docs/07 titles, Built-column readerProduces seeds, draft vi titles ("Đường ghi tin", "Gửi hai lần", "Lịch sử biết lật trang", "Đường socket", "Hai server, một cuộc trò chuyện", "Đường hầm", "Cột mốc: bài kiểm tra Tuan"); NOTHING outside the Part 2 entry; `pnpm build` green (expected-404 window until T007) (FR-008)
- [X] T006 [P] [US1] Create relay-tutorial/app/(en)/part-2/chapter-01/schema-with-a-spine/figures.ts per research R8: figTenantSpine (the five+two tables with environment_id highlighted as the spine — direct column or one-FK-hop, constitution I's clause visualized), figTwoDoors (two Repository instances as two keyed doors into one database — A's key cannot open B's rows, the WHERE lives inside the door), figTwoLanes (the gate's two lanes: Docker-free unit lane unchanged since 1.1 · integration lane through compose Postgres — *.itest.ts as the switch); labels detector-clean, table names from R1's slice only (FR-005, C5)
- [X] T007 [US1] Author the English chapter in relay-tutorial/app/(en)/part-2/chapter-01/schema-with-a-spine/page.mdx per research R8's ten beats: metadata (title "Schema with a spine — Building Relay", description, canonical + hreflang); `<ChapterHeader id="2.1" />`; the heart-starts-here cold open (FR-TEN-05 as 0.4's most important line); `<SkipAhead>` naming part2-ch1 with both lanes' commands; `<Why>` #1 (D4 · FR-TEN-05 · constitution I — designed out vs tested out, the constitution clause quoted verbatim); the schema derivation walk (SAD §6.1 quoted; DR-01/02/03 as requirements-in-SQL; the TWO gap decisions with explicit recorded-decision sentences — applications stub anchored to environments' FK, members anchored to §6.3's index); the 001_core_tables.sql fence; the migrations-as-discipline beat (forward-only quoted from the constitution, no down path by construction) with client.ts + migrate.ts fences and the run-twice no-op shown; **the amendment moment** — the diff-fence mechanism introduced as a change to the series' contract (published code edited only in daylight), the services/api/package.json DIFF-FENCE (```diff title="services/api/package.json"), `<Why>` #2 (the fence discipline — why diffs, not silent edits or re-prints); the repository layer beat with the repository.ts fence (constructor requires environment_id; what became inexpressible; the admin bright line); `<Trap>` the tested-out world (WHERE-vigilance at call sites, one forgotten filter = Sev-0; the eslint DIFF-FENCE lands here as the mechanical backstop); the isolation-suite beat (itest naming explained — why the gate stays Docker-free; vitest.integration.config.ts + repository.itest.ts fences; the attack narrated); the three `<Figure/>`s per halves; `<ForwardRef>` (2.2's row lock in anger; endpoint-level suite with endpoints; CI runs both lanes; RLS as a possible second belt; seeded demo tenant with tenancy endpoints); your-turn exercises (comment out one WHERE → suite catches it; import pg in main.ts → lint refuses; third environment → pairwise isolation); takeaways; one closing `<Checkpoint>` (migrate idempotent + both lanes green); `<ChapterFooter id="2.1" />` — file fences pasted FROM the T002–T004 files; diff-fences derived from the ACTUAL diffs (FR-001..005, 007)
- [X] T008 [US1] Run the en battery per quickstart V5 + C5: prose-only words 2,000–4,000; boxes per battery; figures 3, halves OK; SAD-SQL fidelity spot-check (wrap-tolerant, column-exact for the four verbatim tables); recorded-decision markers present for applications/members and every other R-table DECISION; verbatim quotes (constitution I clause, FR-TEN-05, forward-only clause) checked; ID detector clean; `pnpm lint && pnpm build`; fix findings

**Checkpoint**: Part 2's opener readable end to end — MVP delivered

---

## Phase 4: User Story 2 - The code advances to `part2-ch1` and the fence discipline learns to amend (Priority: P2)

**Goal**: Both mechanisms proven: the diff-chain verifies, the two lanes hold, five chapters' promises coexist at one repo state.

**Independent Test**: Diff-fences applied to predecessors' published fences byte-equal current files; all untouched prior fences match HEAD; both lanes green (quickstart V1–V4).

### Implementation for User Story 2

- [X] T009 [US2] Prove the amended no-drift contract per quickstart V1–V4: (a) unit lane green with Docker irrelevant AND itest provably uncollected by `pnpm test`; (b) integration lane: fresh-database migrate + no-op re-run + isolation suite green; the fail-fast guard spot-checked with a fake remote DATABASE_URL (refuses before touching anything); (c) enforcement spot-checks: scratch pg-import lint failure, scratch tenant-less `new Repository(pool)` type error (both deleted after); (d) **diff-chain verification**: extract the package.json fence from 1.4's en page.mdx and the eslint fence from 1.1's en page.mdx, apply this chapter's two diff-fences, byte-compare against the current repo files; (e) all OTHER prior fences (1.1×9 remaining, 1.2×3, 1.3×7, 1.4×9 remaining) still byte-match HEAD; 2.1's own fences byte-match; en/vi fence + diff-fence identity deferred to T011's parity; (f) SkipAhead names part2-ch1; record results incl. the re-pin note for 1.1/1.4 (FR-006/007, SC-002/003)

**Checkpoint**: The amendment mechanism works; five chapters coexist honestly

---

## Phase 5: User Story 3 - Part 2 opens across the bilingual series (Priority: P3)

**Goal**: The vi chapter at the settled register; Part 2 alive on every surface.

**Independent Test**: Part 2 renders 1+7 on landings/sidebar; 1.4↔2.1 cards; sitemap 34; vi parity; allowlist POSTs 201 (quickstart V6, V7).

### Implementation for User Story 3

- [X] T010 [US3] Create the Vietnamese chapter: relay-tutorial/app/(vi)/vi/part-2/chapter-01/schema-with-a-spine/figures.ts (labels translated; table/SQL/command names English) and page.mdx translated from the FINAL en file per research R9 — settled glossary ("package"/"service"/"schema"/"migration" English, "cửa ải"+"vượt qua", "bản giao kèo", "tin nhắn", "thêm chi tiết"; no calques, hyphenated compounds, "hình hài", "thành tiếng"); ALL fences AND diff-fences byte-identical to en incl. titles; vi metadata from titleVi + " — Building Relay"; locale="vi" on shell and boxes; naturalization self-review BEFORE presenting (FR-009, C7)
- [X] T011 [US3] Run the series battery per quickstart V6 + V7 against a build: both 2.1 routes 200 with hreflang; both landings show Part 2 as a chapter section (exactly 1 link + 7 forthcoming) and drop it from road-ahead; sidebar mixed; 1.4's footers show the 2.1 next card (both locales); 2.1's footers show 1.4 prev + no next; sitemap == 34; OG/TechArticle; vi banner + invite; en/vi fence extraction diff empty (incl. diff-fences); box/figure counts equal; glossary sweep clean; `git diff` confirms the Part 2 seed is the only source edit outside the chapter dirs; allowlist: POST per new path → 201 (flag rows for Dong), 2.2's forthcoming path → 400 invalid_page; fix findings (C1, C6, C7)

**Checkpoint**: All three stories independently verified; Part 2 is open

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Full validation, the 20-row baseline, the handoff

- [X] T012 Run the complete quickstart V1–V7 end to end and record results: regenerate specs/018-chapter-2-1/battery-baseline.txt (20 rows, established formula) — 18 prior rows byte-identical to specs/017-chapter-1-4/battery-baseline.txt; `pnpm check:docs` clean; then the handoff (NO commits/tags/pushes): per-repo ready-to-commit files — relay-platform (6 new files + 2 diffed + lockfile; Dong's sequence `git add -A && git commit && git tag part2-ch1 && git push origin main --tags`), relay-tutorial (Part 2 seed + 2 page.mdx + 2 figures.ts), parent (pins + specs/018 + CLAUDE.md/feature.json) — with suggested messages; flag V8 prominently: Dong's vi read-through INCLUDING the eight seeded vi titles, the 90-minute walk, figures both themes/375 px, Neon row cleanup, post-push fresh-clone replay of BOTH lanes at the tag, site redeploy

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: T001 first (version pin + database reality)
- **Foundational (Phase 2)**: T002 after T001; T003 after T002 (layer uses client); T004 after T003 (suite attacks the layer)
- **US1 (Phase 3)**: T005 [P] ∥ T006 [P] after T004 (fences mirror real files); T007 after T005+T006; T008 after T007
- **US2 (Phase 4)**: T009 after T007 (needs the chapter's actual fences and diff-fences)
- **US3 (Phase 5)**: T010 after T008 (translates the FINAL en); T011 after T010
- **Polish (Phase 6)**: T012 last

### User Story Dependencies

- **US1 (P1)**: Setup + Foundational — the MVP
- **US2 (P2)**: needs US1's chapter text (fences are bidirectional)
- **US3 (P3)**: needs US1 final

### Parallel Opportunities

- T005 (manifest seed) ∥ T006 (figures) — different files, both downstream of T004

## Parallel Example

```bash
# Serial spine: T001 → T002 → T003 → T004
# After T004:  lane A: T005 (Part 2 seed)   lane B: T006 (figures)
# Then serial: T007 → T008 → T009 → T010 → T011 → T012
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. T001–T008 — schema, layer, suite, and the English chapter live
2. **STOP and VALIDATE**: battery + SAD-SQL fidelity + the diff-fence pair

### Incremental Delivery

1. US1 → the opener readable; everything buildable from it
2. US2 → the amendment mechanism proven; both lanes green at one repo state
3. US3 → Part 2 opens bilingually; every surface updates
4. Polish → 20-row baseline; the handoff with Dong's tag sequence

---

## Notes

- KEEP THE TWO DIFFS MINIMAL — they are chapter content; every extra hunk is
  prose the reader must justify
- Write T007's fences FROM the real files and its diff-fences FROM the real
  diffs; T009 proves both by reconstruction, not trust
- The itest file must never be named *.test.ts (that single character class
  is what keeps the fenced vitest config untouched)
- Integration anything: DATABASE_URL localhost only; the guard is code, the
  rule is absolute — Dong's Neon belongs to the tutorial site
- vi: eight seeded titles are DRAFTS for Dong; the chapter itself follows
  the settled register with self-review
- NO git commit / git push / git tag — Dong does all three
