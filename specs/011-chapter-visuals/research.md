# Research: Part 0 Chapter Visuals

**Feature**: `specs/011-chapter-visuals` · **Date**: 2026-07-30

Audit grounding: 0.1/0.2 have zero visual elements; 0.3 has two text-drawn flow
fences (the chapter's own renditions); 0.4/0.5 hold six verbatim specimen fences
(untouchable). The theme-aware, zoomable `MermaidDiagram` component already exists
(features 009/diagram-zoom) — chapters just can't reach it yet.

## R1 — Rendering: a `Figure` chrome component over the existing MermaidDiagram

- **Decision**: New `components/tutorial/figure.tsx`: `<Figure caption="…" code={…} />`
  renders `<figure>` → the existing `MermaidDiagram` (theme-aware, zoom/pan,
  lazy-loaded mermaid) → `<figcaption>` styled like the series chrome. Diagram
  sources live in a colocated `figures.ts` module next to each `page.mdx`
  (exported template-literal constants); the MDX file adds one import line and
  `<Figure … />` tags.
- **Rationale**: Reuses the proven renderer (both-themes legibility and phone
  overflow already solved — FR-003); keeps diagram source OUT of the chapters'
  canonical word count (import lines and JSX tags are already stripped by the
  established formula, and the mermaid text sits in a sibling `.ts` file), so
  FR-008's "additions limited to captions and lead-ins" is mechanically true.
  Colocated per-locale `figures.ts` files give the vi translation a natural home
  (translate labels in the vi copy — same workflow as prose).
- **Alternatives considered**: inline mermaid fences in MDX (the chapter pipeline
  has no mermaid handling, and fence lines would corrupt both the word count and
  the specimen-fence counts); images/SVG assets (violates FR-007's no-binaries,
  loses theme awareness); a new diagram library (violates boring — mermaid is
  already in the bundle).

## R2 — The figure catalog (what actually gets drawn)

- **Decision**: 12 figures per locale, 2–4 per chapter, each visualizing an
  argument the prose already makes:
  - **0.1 (3)**: the wedge — where Relay sits (your app ↔ Relay API ↔ not-a-chat-app);
    the second-year cost curve (xychart: naive build cost vs buy over time — "the
    cost is the second year"); the non-goals fence (kept vs excluded, the v1.0
    exclusion marked — it gets reversed later, and the diagram plants that seed).
  - **0.2 (2)**: the quartet around the product (Mai/David/Priya/Tuan with their
    one-line stakes); the conflicting pulls (each persona's demand tugging the
    design a different direction — why "everyone's happy" is not a requirement).
  - **0.3 (3)**: Mai's stage flow and Tuan's flow upgraded from text fences to
    real diagrams (★ markers preserved — FR-006); the emotional arc as a chart
    (mirrors what docs/03 itself now renders).
  - **0.4 (2)**: anatomy of a requirement (ID · shall-statement · priority ·
    verification method as labeled blocks around the FR-MSG-04 example); the
    traceability chain (persona → journey ★ → requirement ID → the test that can
    fail it).
  - **0.5 (2)**: the distillation funnel (224 requirements → 8 drivers → 14 ADRs
    → 6 services — the chapter's whole argument in one shape); ADR anatomy
    (status/drivers/decision/trade-offs/rejected×N/reversal as the record's
    skeleton, ADR-03's values as the worked example).
- **Rationale**: FR-001/002 — every figure reinforces an existing argument;
  distribution puts at least one figure in each half of every chapter. 0.3's two
  text fences are REMOVED in the upgrade (their content moves into real
  diagrams), taking its specimen-fence count to zero — correct, since they were
  never verbatim quotes.
- **Alternatives considered**: more figures (decoration risk; the 2–4 bound is
  the spec's own guard); persona portraits/illustrations (photos/mood imagery
  explicitly out of scope).

## R3 — The format-convention amendment (docs/07 §2 + the battery)

- **Decision**: Add a "Visual elements" row to docs/07 §2's format table:
  2–4 diagrams per chapter via the series `Figure` component, captioned in the
  page's language, theme-legible, counted separately from specimen fences;
  specimen fences remain verbatim-quote territory. The measured battery gains a
  `<Figure` count column (en == vi, 2–4); the canonical word-count formula is
  UNCHANGED; specimen-fence counts move to their new expected values (0.3: 2→0;
  0.4/0.5: 3 unchanged) and a new baseline is recorded in this feature's
  directory.
- **Rationale**: FR-008; US3's "conventions absorb the new element without losing
  their teeth". Amending docs/07 in the parent repo is the sanctioned move — it
  is the series' own meta-document and the format authority every chapter feature
  has cited.

## R4 — Specimen integrity proof

- **Decision**: Before editing, extract every specimen fence's exact content
  (0.4 ×3, 0.5 ×3) to a baseline file; after editing, extract again and
  byte-diff. The invented-ID detector and the wrap-tolerant quote spot-checks
  run unchanged. 0.3's two flow fences are explicitly excluded from the specimen
  baseline (they are the upgrade targets).
- **Rationale**: FR-005/SC-004 — "quote fidelity outranks prettiness" needs a
  mechanical proof, not a promise.

## R5 — Vietnamese figures

- **Decision**: Each vi chapter gets its own colocated `figures.ts`: narrative
  labels translated in the settled register/glossary; requirement/driver/ADR IDs
  and status keywords stay English (the 006 flow-fence convention, now applied to
  real diagrams); captions translated in the vi `page.mdx` props. Counts and
  positions mirror en exactly.
- **Rationale**: FR-004/SC-003; per-locale files make Dong's V4 label review a
  normal file read.

## R6 — Verification

- **Decision**: Scripted: battery v2 per chapter (canonical words 2,000–4,000;
  box counts unchanged from the current baseline; `<Figure` 2–4 with en==vi;
  specimen fences 0/0/0/3/3; halves-distribution check via the Figure tags' line
  positions vs file midpoint); specimen byte-diff (R4); invented-ID detector on
  the edited files AND the new `figures.ts` label text; `pnpm lint && pnpm
  build`. Manual: every figure in both themes at desktop and 375 px; captions
  language-correct; reading-time sanity vs the manifest (FR-009). Dong: vi label
  read-through (V4).
- **Rationale**: SC-001..007 split between what scripts prove and what needs
  eyes.
