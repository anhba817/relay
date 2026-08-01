# Data Model: Tutorial Chapter 1.4 — Walking Skeleton

No databases; the entities are content and repository artifacts.

## Entities

### Chapter 1.4 (bilingual pair)

| Field | Value / Rule |
|---|---|
| id | `1.4` |
| title (en) | Walking skeleton (docs/07 §3) |
| titleVi | Bộ khung biết đi (seeded by 013) |
| path | `/part-1/chapter-04/walking-skeleton` (seeded) |
| files | `app/(en)/part-1/chapter-04/walking-skeleton/{page.mdx,figures.ts}` + vi mirror |
| words | 2,000–4,000 canonical per locale (plan ~2,400) |
| boxes | WHY ≥2 · TRAP ≥1 · SKIP AHEAD =1 (`part1-ch4`) · FORWARD REF ≥1 · CHECKPOINT =1 |
| figures | 3 planned (skeleton map · request-id thread · Part 1 complete), captioned |
| sources | docs/04 (EIR-API-04/05, NFR-OBS-01/02/06), docs/05 (§4.1, §4.2, ADR-04/05), constitution (observability clause), docs/07 §2–3, §5 |
| discipline | every property document-cited or a recorded DECISION (research R2) |

### The three workspace members (relay-platform, all NEW)

| Member | Contents / Rules |
|---|---|
| `packages/service-kit` (`@relay/service-kit`) | structured logger with injectable sink (`time`,`level`,`service`,`msg`,`request_id?` — JSON per line), request-id helpers (`crypto.randomUUID`), `serve()` over node:http (health route wiring, X-Request-Id on every response, EIR-API-04-shaped 404); zero external deps; tests for log shape + id uniqueness |
| `services/api` (`@relay/api`) | thin main.ts on the kit: `/healthz` → `{status:"ok",service:"api",uptime_s}`; port 4000 (PORT overridable); deps `@relay/{protocol,service-kit}` workspace:*; `typecheck: tsc --noEmit` script (the root gate's `--if-present` silently skips packages without it); ephemeral-port boot test whose 404 case validates the error body against `errorFrameSchema`'s payload schema from `@relay/protocol` (H1 — the dependency is used, executably) |
| `services/gateway` (`@relay/gateway`) | same shape incl. typecheck script, port 4001; `/healthz` additionally advertises `protocol: {frames, close_codes}` derived at runtime from `@relay/protocol` (R5); boot test incl. advertisement content |

Shared rules: tsconfigs extend the base + `"erasableSyntaxOnly": true` (R3);
`dev` script `node --watch src/main.ts`; **no fenced file from 1.1/1.2/1.3 is
touched** (root manifest, compose.yaml, packages/{config,protocol} all
read-only).

### Chapter tag `part1-ch4`

| Field | Value / Rule |
|---|---|
| state | gate green (≥40 tests), Docker-free; both services start on Node ≥22.18 and answer /healthz |
| diff contract | `part1-ch3..part1-ch4` = the three new members (+ lockfile, README if touched — never-fenced) |
| prior fences | all twenty (1.1×10 + 1.2×3 + 1.3×7) still byte-match |
| milestone | Part 1 complete (docs/07 §5) — noted in handoff |
| owner | Dong (commit, tag, push) |

### Manifest entry transition (relay-tutorial `lib/tutorial.ts`)

| Field | Before (013 seed) → After |
|---|---|
| status | `forthcoming` → `published` |
| translatedIn | (absent) → `["vi"]` |
| readerMinutes | seed placeholder → `90` |
| readerProduces | placeholder → "Two running skeleton services — health-checked, request-ID'd, logging structured JSON" |
| readerProducesVi | (absent) → "Hai service bộ khung chạy được — có health check, request ID, log JSON có cấu trúc" |
| sourceDoc | seed value → `"docs/04-srs.md, docs/05-sad.md"` |
| title / titleVi / path / id | unchanged |

Derived automatically — the Part-1-complete states, all first-run: sidebar
Part 1 = 4 links + **0 forthcoming**; 1.3 footers gain next cards; 1.4
footers show prev only (empty next at the part boundary); landings render
Part 1 fully linked with Part 2 still road-ahead; sitemap 30 → 32; SEO for
two new pages; suggestions allowlist admits both paths.

### Fence map (chapter ↔ repository, both locales)

| Fence (title) | Repo file | Kind |
|---|---|---|
| `packages/service-kit/package.json` | same | file-content (byte-match) |
| `packages/service-kit/tsconfig.json` | same | file-content (byte-match) — the services' tsconfigs are stated in prose to be identical files, not re-fenced |
| `packages/service-kit/src/index.ts` | same | file-content (byte-match) |
| `packages/service-kit/src/index.test.ts` | same | file-content (byte-match) |
| `services/api/package.json` | same | file-content (byte-match) |
| `services/api/src/main.ts` | same | file-content (byte-match) |
| `services/api/src/main.test.ts` | same | file-content (byte-match) |
| `services/gateway/package.json` | same | file-content (byte-match) |
| `services/gateway/src/main.ts` | same | file-content (byte-match) |
| `services/gateway/src/main.test.ts` | same | file-content (byte-match) |
| start / curl / gate commands | — | command fences (replayable) |
| prior twenty file fences | unchanged files | must STILL byte-match |

### Battery baseline row (parent repo)

`specs/017-chapter-1-4/battery-baseline.txt`: 18 rows (9 chapters × 2
locales); the 16 pre-existing rows byte-identical to 016's baseline.

## State transitions

```text
forthcoming entry (013 seed) ──manifest flip──▶ published+translated — PART 1 COMPLETE
part1-ch3 (repo state)       ──3 new members─▶ part1-ch4 (Dong tags; docs/07 §5 milestone)
sitemap 30 URLs              ──derived───────▶ 32 URLs (+ allowlist +2)
```
