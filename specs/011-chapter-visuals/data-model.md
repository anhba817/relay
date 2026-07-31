# Data Model: Part 0 Chapter Visuals

**Feature**: `specs/011-chapter-visuals` · **Date**: 2026-07-30

## E1 — Figure component (components/tutorial/figure.tsx)

| Field | Rule | Source |
|---|---|---|
| `code` | Mermaid source string (imported from the chapter's `figures.ts`) | R1 |
| `caption` | Reader-visible caption in the page's language; also the accessible description (rendered `<figcaption>`, referenced for assistive tech) | FR-002 |
| Rendering | `<figure>` → existing `MermaidDiagram` (theme-aware, zoom/pan, `<pre>` fallback) → `<figcaption>`; series-chrome styling; `not-prose`-safe inside the prose container | FR-003, R1 |

## E2 — Figure source module (figures.ts, one per chapter per locale — 10 files)

| Property | Rule | Source |
|---|---|---|
| Shape | Named exported template-literal constants, one per figure (e.g. `figWedge`, `figCostCurve`) | R1 |
| en labels | English narrative labels; requirement/driver/ADR IDs verbatim (detector-checked) | FR-002/005 |
| vi labels | Narrative labels translated (register + glossary); IDs and status keywords English; persona names unchanged | FR-004, R5 |
| Placement | Colocated next to its `page.mdx`; imported with a single import line (stripped by the word-count formula) | R1, FR-008 |

## E3 — The figure catalog (12 per locale)

| Chapter | Figures | Both-halves rule |
|---|---|---|
| 0.1 | wedge/positioning; second-year cost curve; non-goals fence (exclusion marked — seeds the later reversal) | 3 figures span open→close |
| 0.2 | quartet around the product; conflicting pulls | 1 per half |
| 0.3 | Mai stage flow ★ (upgrade); emotional arc chart; Tuan flow ★ (upgrade) | replaces the 2 text fences |
| 0.4 | requirement anatomy (FR-MSG-04 worked example); traceability chain (persona → ★ → ID → failing test) | 1 per half |
| 0.5 | 224→8→14→6 distillation funnel; ADR anatomy (ADR-03 values) | 1 per half |

## E4 — Battery v2 (the amended measured rules)

| Measure | Expected after this feature | Change |
|---|---|---|
| Canonical words (en) | 2,000–4,000 per chapter; formula UNCHANGED | prose grows only by lead-ins |
| Boxes (Why/SkipAhead/ForwardRef/Checkpoint) | unchanged per chapter | none |
| `<Figure` count | 2–4 per chapter; en == vi | NEW class |
| Specimen fences (```` ``` ```` pairs) | 0.1: 0 · 0.2: 0 · 0.3: **0** (was 2) · 0.4: 3 · 0.5: 3 | 0.3's flows upgraded |
| Distribution | ≥1 `<Figure` in each half of every chapter (line position vs midpoint) | NEW check |
| Baseline | Recorded to specs/011-chapter-visuals/battery-baseline.txt after the feature | re-baseline (sanctioned once, FR-008) |

## E5 — Specimen integrity baseline (specs/011-chapter-visuals/specimen-baseline/)

| Property | Rule | Source |
|---|---|---|
| Contents | The exact text of every verbatim specimen fence, extracted per chapter BEFORE any edit (0.4 en/vi ×3, 0.5 en/vi ×3; 0.3's flow fences excluded — they are upgrade targets) | FR-005, R4 |
| Proof | Post-edit extraction byte-diffs empty; invented-ID detector and wrap-tolerant quote spot-checks unchanged | SC-004 |

## E6 — Format-convention amendment (docs/07 §2, parent repo)

One new row in the format table: **Visual elements** — 2–4 captioned,
theme-legible diagrams per chapter via the series `Figure` component; counted
separately from specimen fences (which remain verbatim-quote territory); labels
translated in vi with identifiers in English.
