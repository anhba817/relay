# Implementation Plan: Part 0 Chapter Visuals — Diagrams Where Prose Works Hardest

**Branch**: `main` (no feature branch — consistent with features 001–010) | **Date**: 2026-07-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/011-chapter-visuals/spec.md`

## Summary

Give every Part 0 chapter 2–4 purposeful, theme-aware diagrams at its
hardest-working moments — 12 figures per locale from a fixed catalog (the wedge,
the second-year cost curve, the persona quartet, the journey flows and emotional
arc, requirement anatomy, the traceability chain, the 224→8→14 funnel, ADR
anatomy) — rendered through a new `Figure` chrome component over the existing
zoomable `MermaidDiagram`, with diagram sources in colocated per-locale
`figures.ts` files so the canonical word-count formula is untouched. The first
content feature to deliberately edit all ten chapter files: verbatim specimens are
byte-diff protected, 0.3's two text-drawn flows upgrade to real diagrams, docs/07
§2 gains the visual-element rule, and the battery re-baselines once. Decisions in
[research.md](./research.md).

## Technical Context

**Language/Version**: TypeScript 5.9 / Next.js 16.2.12 (existing relay-tutorial app), Node.js 22, pnpm 10

**Primary Dependencies**: None new — reuses `MermaidDiagram` (theme-aware,
zoom/pan, lazy mermaid — features 009/diagram-zoom) and the MDX chapter pipeline

**Storage**: N/A — 1 new component, 10 colocated `figures.ts` modules, edits to
the 10 chapter `page.mdx` files, 1 row in docs/07 §2 (parent repo)

**Testing**: `pnpm lint && pnpm build`; battery v2 (words in bounds, boxes
unchanged, `<Figure` 2–4 with en==vi, specimen fences 0/0/0/3/3,
halves-distribution); specimen byte-diff baseline; invented-ID detector incl. the
new figure label text; both-theme + 375 px manual pass; Dong's vi label review

**Target Platform**: Static prerendered pages; mermaid hydrates client-side only
on pages with figures (same tradeoff already accepted for reference docs)

**Project Type**: Content feature (the first that edits published chapters) inside the relay-tutorial submodule

**Performance Goals**: No new dependencies; mermaid loads lazily per page

**Constraints**: Verbatim specimen fences byte-identical (extract-and-diff proof);
prose changes limited to lead-in sentences; canonical word counts stay within
2,000–4,000 (formula unchanged — diagram sources live outside `page.mdx`);
figure labels obey the glossary (IDs/status keywords English in vi); no binary
assets; no pipe tables and no new fence lines in chapters

**Scale/Scope**: 12 figures ×2 locales; 1 component; 10 `figures.ts`; 10 MDX
edits; 1 docs/07 row; new battery baseline

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Notes |
|---|---|---|
| I–III (isolation, message loss, data paths) | ✅ N/A | Static content; no Relay runtime. |
| IV. Single source of truth | ✅ Pass | Figures visualize what the chapters/docs already say; verbatim specimens byte-diff protected; the format rule lands in docs/07 (the format authority), not in a side convention. |
| V. Developer/reader-first | ✅ Pass | The user's own complaint ("text-only, kind of boring") is the requirement; every figure must teach, decoration is bounded out. |
| VI. Requirement-driven, test-verified | ✅ Pass | Tasks trace to FR-001..009; battery v2, specimen byte-diff, and ID detector are scripted; theme/viewport legibility is a named manual check; vi labels go to the named reviewer. |
| VII. Boring by design | ✅ Pass | Zero new dependencies; one new chrome component over the existing renderer; per-locale figure files mirror the established translation workflow. |
| Tech & platform constraints | ✅ Pass | Unchanged stack; static output preserved. |

**Pre-Phase-0 verdict: PASS** (Complexity Tracking empty).
**Post-Phase-1 re-check: PASS** — one component, data files, content edits, one
doc row.

## Project Structure

### Documentation (this feature)

```text
specs/011-chapter-visuals/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── chapter-visuals-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code

```text
relay-tutorial/
├── components/tutorial/
│   └── figure.tsx                        # NEW — <Figure caption code> over MermaidDiagram (R1)
└── app/
    ├── (en)/part-0/chapter-0X/<slug>/
    │   ├── figures.ts                    # NEW ×5 — en mermaid sources (R1, R2)
    │   └── page.mdx                      # MODIFIED ×5 — import + <Figure/> + lead-ins; 0.3 drops its 2 text flow fences
    └── (vi)/vi/part-0/chapter-0X/<slug>/
        ├── figures.ts                    # NEW ×5 — vi labels per glossary (R5)
        └── page.mdx                      # MODIFIED ×5 — same figures, vi captions

/home/dong/work/relay/ (parent repo)
├── docs/07-tutorial-plan.md              # MODIFIED — §2 gains the "Visual elements" format row (R3)
└── specs/011-chapter-visuals/
    ├── battery-baseline.txt              # NEW — post-feature baseline incl. Figure counts (R3)
    └── specimen-baseline/                # NEW — pre-edit fence extractions for the byte-diff (R4)
```

**Structure Decision**: Diagram sources colocate with each chapter as importable
modules — out of the word count by construction, translated where the chapter is
translated, reviewed like prose. The `Figure` component is series chrome in the
same family as the boxes.

## Implementation Flow (input to /speckit-tasks)

1. **Baselines first** (FR-005/008): extract all six specimen fences to
   `specimen-baseline/`; record the pre-edit battery for reference.
2. **Chrome** (FR-002/003): `components/tutorial/figure.tsx`.
3. **English chapters** (FR-001/002/006): per chapter — `figures.ts` from the R2
   catalog, `<Figure/>` placements with lead-ins/captions, 0.3's fence upgrade;
   battery v2 checks as each lands.
4. **Vietnamese chapters** (FR-004): translated `figures.ts` + captioned
   placements, from the FINAL en versions.
5. **Convention amendment** (FR-008): docs/07 §2 row; new battery baseline
   recorded.
6. **Verify** ([quickstart.md](./quickstart.md)): scripted battery v2 + specimen
   byte-diff + detector; manual theme/viewport pass; reading-time revalidation
   (FR-009); flag Dong's vi label review.
7. **Handoff**: no commits — ready-to-commit report.

## Complexity Tracking

> No constitution violations — table intentionally empty.

## Notes

- The six verbatim specimen fences (0.4 ×3, 0.5 ×3) are the untouchable class —
  the byte-diff is the proof, and a failed diff means rework, never re-baseline.
- 0.3's two text flow fences are NOT specimens (chapter-authored renditions) —
  they are the upgrade targets and leave the fence count.
- Diagram label text must pass the invented-ID detector too — a figure that
  invents "FR-MSG-99" is worse than no figure.
- Mermaid sources never appear in `page.mdx` — that invariant is what keeps the
  word-count formula stable (research R1).
- Commits/pushes remain Dong's; the vi figures go through his V4-style review.
