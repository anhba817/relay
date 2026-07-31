# Data Model: Tutorial Chapter 1.2 — One Command, Whole World

No databases are consumed by this feature; the "data model" is the set of
content and repository entities and their invariants.

## Entities

### Chapter 1.2 (bilingual pair)

| Field | Value / Rule |
|---|---|
| id | `1.2` |
| title (en) | One command, whole world (docs/07 §3 row) |
| titleVi | Một câu lệnh, cả thế giới (already in manifest) |
| path | `/part-1/chapter-02/one-command-whole-world` (already in manifest) |
| files | `app/(en)/part-1/chapter-02/one-command-whole-world/{page.mdx,figures.ts}` + vi mirror under `app/(vi)/vi/…` |
| words | 2,000–4,000 canonical (prose outside fences), per locale |
| boxes | WHY ≥2 · TRAP ≥1 · SKIP AHEAD =1 (names `part1-ch2`) · FORWARD REF ≥1 · CHECKPOINT =1 (closing) |
| figures | 2–4 (plan: 3), captioned, per-locale `figures.ts`, PlantUML-palette mermaid |
| structural parity | vi mirrors en boxes/figures/fences exactly; fences byte-identical |
| sources | docs/04 (NFR-MNT-03), docs/05 §9 (ADR-02/03/04/06/07/08/10, CON-01), docs/06 deep dives, docs/07 §2–3 |

### The infrastructure declaration (relay-platform)

| Field | Value / Rule |
|---|---|
| file | `compose.yaml` (repo root, NEW) |
| project name | `relay` |
| services | exactly `postgres`, `redis`, `nats`, `clickhouse` — pinned image tags |
| healthchecks | one per service (R6); `up -d --wait` blocks on them |
| volumes | `postgres-data`, `nats-data`, `clickhouse-data`; **Redis: none** (invariant — the smoke test asserts its absence) |
| ports | 5432, 6379, 4222/8222, 8123/9000 (defaults; collisions handled in prose) |
| credentials | dev-only `relay/relay/relay`, labeled as such in prose |

### The gate extension (relay-platform)

| Field | Value / Rule |
|---|---|
| files | `packages/config/src/infra.ts`, `packages/config/src/infra.test.ts` (both NEW — additive-only, R3) |
| exports | `INFRA_SERVICES` (4 names, `as const`), `COMPOSE_FILE` |
| test contract | reads `compose.yaml` as text; asserts service names present, healthcheck count ≥ 4, durable volumes present, `redis-data` absent |
| constraint | passes with Docker daemon stopped |

### Chapter tag

| Field | Value / Rule |
|---|---|
| name | `part1-ch2` (docs/07 §2 convention) |
| state | gate green; compose up --wait → 4× healthy on a Docker machine |
| diff contract | `part1-ch1..part1-ch2` = exactly this chapter's additions (no 1.1-fenced file modified) |
| owner | Dong (commit, tag, push) |

### Manifest entry transition (relay-tutorial `lib/tutorial.ts`)

013 seeded 1.2 as a full forthcoming entry (placeholder reader-facing values
included); the flip both publishes it and settles those placeholders:

| Field | Before → After |
|---|---|
| status | `forthcoming` → `published` |
| translatedIn | (absent) → `["vi"]` |
| readerMinutes | `90` (013 placeholder) → `60` (deliberate: shorter chapter than 1.1; image pulls overlap reading) |
| readerProduces | "A one-command local stack: Postgres, Redis, NATS, ClickHouse" → "A one-command local infrastructure — four stores, healthchecked and verified" |
| readerProducesVi | (absent) → "Hạ tầng local một câu lệnh — bốn store, có healthcheck và đã kiểm chứng" |
| sourceDoc | `"docs/05-sad.md"` → `"docs/04-srs.md, docs/05-sad.md"` (NFR-MNT-03 is the chapter's spine) |
| title / titleVi / path / id | unchanged (seeded by 013) |

All changes stay inside the single 1.2 entry — C5's manifest-only promise is
about the edit's blast radius, not its field count.

Derived (zero manual edits): 1.1 footer next card, 1.2 footer prev card,
sidebar Part 1 = 2 links + 2 forthcoming, landings, sitemap 26 → 28 URLs,
SEO/OG/JSON-LD for the two new pages.

### Fence map (chapter ↔ repository, both locales)

| Fence (title) | Repo file | Kind |
|---|---|---|
| `compose.yaml` | `relay-platform/compose.yaml` | file-content (byte-match) |
| `packages/config/src/infra.ts` | same | file-content (byte-match) |
| `packages/config/src/infra.test.ts` | same | file-content (byte-match) |
| startup / verify / teardown commands | — | command fences (replayable) |
| 1.1's ten file fences | unchanged files | must STILL byte-match at `part1-ch2` |

### Battery baseline row (parent repo)

`specs/014-chapter-1-2/battery-baseline.txt`: 14 rows (7 chapters × 2 locales);
the 12 pre-existing rows must be identical to 013's baseline — any change is a
defect.

## State transitions

```text
forthcoming entry (013)  ──manifest flip──▶  published+translated (this feature)
part1-ch1 (repo state)   ──additive files──▶  part1-ch2 (Dong tags)
sitemap 26 URLs          ──derived──▶         28 URLs
```
