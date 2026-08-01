# Data Model: Tutorial Chapter 2.1 — Schema with a Spine

This feature's "data model" is twofold: the actual database schema the
chapter migrates (the product's first), and the content/repository entities.

## The database schema (migration 001, per research R1)

| Table | Source | Tenant column | Key constraints |
|---|---|---|---|
| applications | **DECISION** (stub: id, name) | — (above tenancy) | PK id |
| environments | SAD §6.1 verbatim | is the tenant | PK id; FK application_id; kind CHECK; signing_secret (NFR-SEC-02 comment); retention_days; quota_config |
| users | SAD §6.1 verbatim | environment_id NOT NULL FK | UNIQUE (environment_id, external_id) — DR-02 |
| channels | SAD §6.1 verbatim | environment_id NOT NULL FK | UNIQUE (environment_id, external_id) — DR-02; last_sequence (ADR-03); type CHECK |
| messages | SAD §6.1 verbatim | via channel_id FK (one hop — constitution I's allowance) | UNIQUE (channel_id, sequence) — DR-01; partial unique messages_idem — DR-03; text NULL ⇒ tombstone |
| members | **DECISION** (docs/07 row + SAD §6.3 index anchor) | via channel_id (one hop) | PK (channel_id, user_id); joined_at |
| schema_migrations | runner bookkeeping (R3) | — | PK version |

Indexes: `messages (channel_id, sequence DESC)` and `members (user_id,
channel_id)` — both SAD §6.3 hot-path indexes, cited in SQL comments.

Deferred (named arrivals): message_edits, outbox, emoji/media tables,
partitioning.

## Content & repository entities

### Chapter 2.1 (bilingual pair)

| Field | Value / Rule |
|---|---|
| id / title / path | `2.1` · Schema with a spine · `/part-2/chapter-01/schema-with-a-spine` |
| titleVi | Schema có xương sống (new seed, Dong-reviewable) |
| words / boxes / figures | 2,000–4,000 per locale · WHY ≥2, TRAP ≥1, SKIP=1 (`part2-ch1`), FWD ≥1, CHK=1 · 3 planned |
| sources | docs/04 (FR-TEN-01..06, DR-01/02/03, NFR-SEC-09), docs/05 (§6.1 SQL, §6.3, §8, D4, ADR-03/04), constitution I + workflow clause, docs/07 §2–3 |
| discipline | SAD SQL column-exact where defined; gaps carry recorded-decision comments IN the SQL; R4's diff-fences for the two amended files |

### The repository layer (services/api/src/db/)

| Piece | Rule |
|---|---|
| client.ts | lazy pool from DATABASE_URL (default compose dev URL) |
| migrate.ts | ~50 lines; schema_migrations table; filename order; transactional; forward-only; re-run = no-op; importable by tests, runnable via the api `migrate` script |
| repository.ts | `createEnvironment(pool, { name })` admin surface (documented bright line) — also inserts the stub application row satisfying environments' NOT NULL FK (U1; real application lifecycle = Part 3); all ids app-generated via crypto.randomUUID (no SQL DEFAULTs beyond the SAD's — L2) + `class Repository(pool, environmentId)` — users create/getByExternalId; channels create/getByExternalId/list; members add/listForChannel/channelsForUser; all SQL scoped by the instance's environment_id; cross-tenant reads → null/empty (no existence reveal) |
| repository.itest.ts | two environments; A's data attacked via B's Repository; DR-02 dual-tenant uniqueness; TRUNCATE-based setup; fail-fast if DATABASE_URL host isn't local |
| vitest.integration.config.ts | include `src/**/*.itest.ts` only |

### The fence amendments (R4 — the mechanism's debut)

| File | Predecessor fence | This chapter's diff adds |
|---|---|---|
| services/api/package.json | chapter 1.4 | `pg` dependency (pinned); `migrate` + `test:integration` scripts |
| eslint.config.mjs | chapter 1.1 | no-restricted-imports: `pg` forbidden outside `services/api/src/db/**` |

Verification: apply each diff-fence to its predecessor's published fence
text → must byte-equal the current repo file. Predecessors' direct checks
for exactly these paths re-pin to their tags; all other prior fences
(1.1×9 remaining, 1.2×3, 1.3×7, 1.4×9 remaining) still match HEAD.

### Manifest seed (relay-tutorial `lib/tutorial.ts`, Part 2 entry)

2.1 published+translated per R7's values; 2.2–2.8 forthcoming with reserved
paths, docs/07 titles, Built-column readerProduces seeds, and draft vi
titles ("Đường ghi tin", "Gửi hai lần", "Lịch sử biết lật trang", "Đường
socket", "Hai server, một cuộc trò chuyện", "Đường hầm", "Cột mốc: bài kiểm
tra Tuan"). Derived: landing Part 2 section (1 link + 7 forthcoming), 1.4
footer next card, sidebar, sitemap 32 → 34, SEO, suggestions allowlist +2.

### Chapter tag `part2-ch1`

Gate green Docker-free; with compose: migrate idempotent + itest suite
green; diff from `part1-ch4` = the six new files + the two diffed files
(+ lockfile); Dong tags.

### Battery baseline

20 rows (10 chapters × 2 locales); 18 prior rows byte-identical to 017's.

## State transitions

```text
Part 2 chapters: []            ──seed──▶  8 entries (1 published, 7 forthcoming)
part1-ch4                      ──schema+layer──▶ part2-ch1 (Dong tags)
fence discipline: additive-only ──▶ additive + diff-fence amendments (permanent)
gate: one lane                 ──▶ two named lanes (unit Docker-free · integration on compose)
```
