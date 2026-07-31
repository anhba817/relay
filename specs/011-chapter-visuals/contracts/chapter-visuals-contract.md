# Contract: Chapter Visuals — Figures, Specimens, and the Amended Battery

**Feature**: `specs/011-chapter-visuals` · **Date**: 2026-07-30

## C1 — Figures

| Check | Bound |
|---|---|
| Count | 2–4 `<Figure` per chapter page; en count == vi count per chapter (catalog: 3/2/3/2/2) |
| Placement | ≥1 `<Figure` in each half of every chapter (tag line number vs file midpoint) |
| Caption | Every `<Figure` carries a non-empty `caption` in the page's language |
| Source | Every `code` value imports from the chapter's colocated `figures.ts`; zero mermaid text inside any `page.mdx` |
| Rendering | Diagram (not raw source) post-hydration; `<pre>` source fallback pre-hydration; legible both themes; no horizontal page overflow at 375 px |

## C2 — Specimen integrity (the untouchable class)

| Check | Bound |
|---|---|
| Fence counts | 0.1: 0 · 0.2: 0 · 0.3: 0 · 0.4: 3 · 0.5: 3 (per locale) |
| Byte-diff | Post-edit specimen extraction identical to specs/011-chapter-visuals/specimen-baseline/ (0.4/0.5, both locales) |
| Quotes | Wrap-tolerant spot-checks against docs/04/05 pass unchanged |
| Detector | Invented-ID detector clean over the edited `page.mdx` files AND all `figures.ts` label text (`ADR-[0-9]+`, `\bD[1-8]\b` vs docs/05; FR/NFR/EIR/DR/CON/ASM vs docs/04) |

## C3 — Prose discipline

| Check | Bound |
|---|---|
| Canonical words (en) | Every chapter within 2,000–4,000 after edits; formula unchanged |
| Boxes | Why/SkipAhead/ForwardRef/Checkpoint counts per chapter identical to pre-feature values |
| Voice | Additions are lead-in sentences and captions only — no rewrites of existing arguments (reviewed, not scripted) |
| vi labels | Narrative labels translated per register/glossary; IDs and status keywords English; persona names unchanged |

## C4 — Conventions and follow-through

| Check | Bound |
|---|---|
| docs/07 §2 | Contains the Visual-elements format row |
| New baseline | specs/011-chapter-visuals/battery-baseline.txt records words/boxes/fences/figures for all 10 pages post-feature |
| Reading time | Manifest `readerMinutes` revalidated; corrected if materially off |
| Build gate | `pnpm lint && pnpm build` exit 0; zero new dependencies; SEO battery (feature 010) unaffected — og/JSON-LD counts unchanged |
