# Implementation Plan: Tutorial Chapter 0.3 — Journeys, Where Products Die

**Branch**: `main` (no feature branch — consistent with features 001–005) | **Date**: 2026-07-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/006-tutorial-chapter-03/spec.md`

## Summary

Publish chapter 0.3 in both locales: an English chapter that teaches journey mapping
by anatomy and by ★ — walking the three ★ stages deeply (Mai's first message, Priya's
reconstruction, Tuan's lost signal) while compressing the remaining twenty — plus a
Vietnamese translation in the established register, and a one-entry manifest flip.
Third consecutive pure-content feature on the finished infrastructure; zero component
changes. Decisions in [research.md](./research.md).

## Technical Context

**Language/Version**: TypeScript 5.9 / Next.js 16.2.12 (existing relay-tutorial app), Node.js 22, pnpm 10

**Primary Dependencies**: None new. Reused: MDX pipeline + shell + boxes (002), i18n + `/vi` mirror + hreflang (004)

**Storage**: N/A — two MDX files and one manifest entry edit

**Testing**: `pnpm lint && pnpm build`; the established scripted chapter battery + the new 0.2↔0.3 navigation pair; Dong's Vietnamese read-through

**Target Platform**: Static prerendered pages, both locales

**Project Type**: Content feature inside the existing web app (relay-tutorial submodule)

**Performance Goals**: None new — two more static routes

**Constraints**: docs/03 frozen as the fact source; format rules docs/07 §2; 0.1/0.2 prose immutable; zero hand-edited navigation (SC-006); diagrams as fenced code blocks only, chapter readable without them (spec edge case, research R3); manifest's existing Vietnamese title binding (spec edge case)

**Scale/Scope**: 2 MDX files (~3,000 words canonical count each), 1 manifest flip, 0 component changes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Notes |
|---|---|---|
| I–III (isolation, message loss, data paths) | ✅ N/A | Static content; no Relay runtime. |
| IV. Single source of truth | ✅ Pass | Journey facts: docs/03 only. Series data: the manifest flip. Translation source: the final English file. |
| V. Developer/reader-first | ✅ Pass | The chapter is reader value; the exercise produces the 0.4 prerequisite. |
| VI. Requirement-driven, test-verified | ✅ Pass | Tasks trace to FR-001..008; scripted battery + named human reviewer for the unscriptable judgment. |
| VII. Boring by design | ✅ Pass | Zero new machinery; fenced code blocks over an image/diagram pipeline (R3) is this feature's boring-choice moment. |
| Tech & platform constraints | ✅ Pass | Unchanged stack. |

**Pre-Phase-0 verdict: PASS** (Complexity Tracking empty).
**Post-Phase-1 re-check: PASS** — two content files, one manifest entry, nothing else.

## Project Structure

### Documentation (this feature)

```text
specs/006-tutorial-chapter-03/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── chapter-03-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (relay-tutorial submodule)

```text
relay-tutorial/
├── lib/
│   └── tutorial.ts                      # MODIFIED — 0.3: status published, translatedIn ["vi"] (R1)
└── app/
    ├── part-0/chapter-03/journeys-where-products-die/
    │   └── page.mdx                     # NEW — English chapter (R2–R4)
    └── vi/part-0/chapter-03/journeys-where-products-die/
        └── page.mdx                     # NEW — Vietnamese translation (R5)
```

**Structure Decision**: Exactly the 004 C5 contract, as exercised by 005: same-slug
mirror paths, `locale="vi"` props in the vi file, hreflang alternates in both files;
the part-0 layouts already wrap both routes.

## Implementation Flow (input to /speckit-tasks)

1. **Manifest flip** (FR-008): 0.3 entry in `lib/tutorial.ts`; expect the brief
   404-link window until content lands (established pattern; do not hand-edit
   navigation).
2. **English chapter** (FR-001..006): author per the R2 arc — anatomy specimen, three
   ★ deep-walks, compressed maps, effort ranking + the adoption/deserving close —
   with R3's fenced flow diagrams and R4's exercise.
3. **Vietnamese chapter** (FR-007): translate the final English file per R5,
   including translated stage labels in the flow diagrams.
4. **Verify** ([quickstart.md](./quickstart.md)): battery + 0.2↔0.3 pair; flag
   Dong's read-through.
5. **Handoff**: no commits — ready-to-commit report.

## Complexity Tracking

> No constitution violations — table intentionally empty.

## Notes

- The chapter's hardest editorial constraint is compression: 23 documented stages
  into a lesson about three ★s. When in doubt, cut breadth, keep the anatomy and the
  ★ arguments (research R2's rationale).
- 0.2's footers gaining a live next-link is the manifest working; 0.2's prose is
  untouched.
- Commits/pushes remain Dong's; the vi read-through is requested before committing.
