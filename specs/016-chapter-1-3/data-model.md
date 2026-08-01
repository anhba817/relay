# Data Model: Tutorial Chapter 1.3 — The Protocol Package

No databases; the entities are content and repository artifacts.

## Entities

### Chapter 1.3 (bilingual pair)

| Field | Value / Rule |
|---|---|
| id | `1.3` |
| title (en) | The protocol package (docs/07 §3) |
| titleVi | Package protocol (seeded by 013, post-glossary correction) |
| path | `/part-1/chapter-03/the-protocol-package` (seeded) |
| files | `app/(en)/part-1/chapter-03/the-protocol-package/{page.mdx,figures.ts}` + vi mirror |
| words | 2,000–4,000 canonical per locale (plan ~2,400) |
| boxes | WHY ≥2 · TRAP ≥1 · SKIP AHEAD =1 (`part1-ch3`) · FORWARD REF ≥1 · CHECKPOINT =1 |
| figures | 3 planned (frame map · one-source mechanism · payoff revisited), captioned, per-locale figures.ts |
| sources | docs/04 (EIR-WS-01..07, EIR-API-04, FR-MSG-03/04, FR-RTM-01..09, FR-SDK-06), docs/05 (§5.1, §5.2, §7, ADR-01/03/05), docs/06 (ADR-01 deep dive), docs/07 §2–3 |
| discipline | every frame/code either cites a source or carries the chapter's recorded-decision marker (research R2 table) |

### The protocol package (relay-platform)

| Field | Value / Rule |
|---|---|
| location | `packages/protocol/` (NEW — additive-only holds) |
| name | `@relay/protocol`, private, `"type": "module"` |
| dependency | zod, pinned, package-local (root package.json untouched) |
| modules | `src/frames.ts` (envelope, frame schemas, inferred types, `parseFrame`), `src/codes.ts` (close codes 4001/4002/4008/4009, error-code registry per EIR-API-04 shape), `src/index.ts` (public surface) |
| invariant | zero hand-written types duplicating a schema — all static types are `z.infer` (R3) |
| tests | `frames.test.ts` (accept/reject tables per frame), `codes.test.ts` (registry integrity); ≥6 new tests, gate total ≥12 |

### Chapter tag `part1-ch3`

| Field | Value / Rule |
|---|---|
| state | gate green incl. protocol suite; no Docker required |
| diff contract | `part1-ch2..part1-ch3` = the new package + chapter-external never-fenced files only |
| prior fences | 1.1's ten + 1.2's three still byte-match at this state |
| owner | Dong (commit, tag, push) |

### Manifest entry transition (relay-tutorial `lib/tutorial.ts`)

| Field | Before (013 seed) → After |
|---|---|
| status | `forthcoming` → `published` |
| translatedIn | (absent) → `["vi"]` |
| readerMinutes | `90` (placeholder) → `75` |
| readerProduces | placeholder → "The shared wire contract — frame types, error codes, and schemas that reject bad input" |
| readerProducesVi | (absent) → "Bản giao kèo đường truyền dùng chung — kiểu frame, mã lỗi, và schema biết từ chối dữ liệu hỏng" |
| sourceDoc | seed value → `"docs/04-srs.md, docs/05-sad.md"` |
| title / titleVi / path / id | unchanged |

Derived automatically: footers 1.2↔1.3, sidebar Part 1 = 3 links + 1
forthcoming, landings, sitemap 28 → 30, SEO for two new pages, **and the 015
suggestions allowlist** (published + translated ⇒ both paths admitted).

### Fence map (chapter ↔ repository, both locales)

| Fence (title) | Repo file | Kind |
|---|---|---|
| `packages/protocol/package.json` | same | file-content (byte-match) |
| `packages/protocol/tsconfig.json` | same | file-content (byte-match) |
| `packages/protocol/src/frames.ts` | same | file-content (byte-match) |
| `packages/protocol/src/codes.ts` | same | file-content (byte-match) |
| `packages/protocol/src/index.ts` | same | file-content (byte-match) |
| test fences (full files or clearly-scoped excerpts — excerpt fences carry no `title=` and are exempt from byte-match, stated in prose) | `frames.test.ts`, `codes.test.ts` | per implementation choice, recorded in the contract check |
| install/gate commands | — | command fences (replayable) |
| 1.1's ten + 1.2's three file fences | unchanged files | must STILL byte-match |

### Battery baseline row (parent repo)

`specs/016-chapter-1-3/battery-baseline.txt`: 16 rows (8 chapters × 2
locales); the 14 pre-existing rows must be byte-identical to 014's baseline.

## State transitions

```text
forthcoming entry (013 seed) ──manifest flip──▶ published+translated
part1-ch2 (repo state)       ──new package────▶ part1-ch3 (Dong tags)
sitemap 28 URLs              ──derived────────▶ 30 URLs (+ allowlist +2)
```
