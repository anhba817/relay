# Implementation Plan: Tutorial Chapter 0.4 — Requirements You Can Test

**Branch**: `main` (no feature branch — consistent with features 001–006) | **Date**: 2026-07-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/007-tutorial-chapter-04/spec.md`

## Summary

Publish chapter 0.4 in both locales: an English chapter that converts 0.3's journey
maps into the discipline of a real SRS — the anatomy of a requirement row, the
T/D/I/A verification vocabulary, two live journey→requirement traces, FR-TEN-05 as
the star requirement, and the fresh FR-MED section as proof that a spec absorbs
change with new IDs rather than lies — plus a Vietnamese translation that keeps every
requirement ID in English, and a one-entry manifest flip. Fourth consecutive
pure-content feature; zero component changes. Decisions in
[research.md](./research.md).

## Technical Context

**Language/Version**: TypeScript 5.9 / Next.js 16.2.12 (existing relay-tutorial app), Node.js 22, pnpm 10

**Primary Dependencies**: None new. Reused: MDX pipeline + shell + boxes (002), i18n + `/vi` mirror + hreflang (004)

**Storage**: N/A — two MDX files and one manifest entry edit

**Testing**: `pnpm lint && pnpm build`; the established scripted chapter battery + the 0.3↔0.4 navigation pair + a verbatim spot-check of quoted requirement rows against docs/04; Dong's Vietnamese read-through

**Target Platform**: Static prerendered pages, both locales

**Project Type**: Content feature inside the existing web app (relay-tutorial submodule)

**Performance Goals**: None new — two more static routes

**Constraints**: docs/04 (current, media-inclusive) frozen as the fact source — quoted rows verbatim, IDs never invented (FR-007); **no pipe tables** (MDX has no GFM — specimen rows as ≤3 fenced blocks, chapter readable without them, research R3); requirement IDs and shall-keyword stay English in the vi file (R5); 0.1–0.3 prose immutable; zero hand-edited navigation

**Scale/Scope**: 2 MDX files (~3,000 words canonical each), 1 manifest flip, 0 component changes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Notes |
|---|---|---|
| I–III (isolation, message loss, data paths) | ✅ N/A | Static content; no Relay runtime. |
| IV. Single source of truth | ✅ Pass | Requirement facts: docs/04 only, quoted verbatim. Series data: the manifest. Translation source: the final English file. |
| V. Developer/reader-first | ✅ Pass | The chapter is reader value; the exercise produces the 0.5 prerequisite. |
| VI. Requirement-driven, test-verified | ✅ Pass | Pleasingly recursive: the chapter *about* verification methods is itself verified by the scripted battery + a verbatim-quote check; the unscriptable judgment goes to the named reviewer. |
| VII. Boring by design | ✅ Pass | The R3 no-GFM decision is this feature's boring-choice moment: fenced blocks over new remark machinery. |
| Tech & platform constraints | ✅ Pass | Unchanged stack. |

**Pre-Phase-0 verdict: PASS** (Complexity Tracking empty).
**Post-Phase-1 re-check: PASS** — two content files, one manifest entry, nothing else.

## Project Structure

### Documentation (this feature)

```text
specs/007-tutorial-chapter-04/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── chapter-04-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (relay-tutorial submodule)

```text
relay-tutorial/
├── lib/
│   └── tutorial.ts                      # MODIFIED — 0.4: status published, translatedIn ["vi"] (R1)
└── app/
    ├── part-0/chapter-04/requirements-you-can-test/
    │   └── page.mdx                     # NEW — English chapter (R2–R4)
    └── vi/part-0/chapter-04/requirements-you-can-test/
        └── page.mdx                     # NEW — Vietnamese translation (R5)
```

**Structure Decision**: The 004 C5 contract, fourth exercise: same-slug mirror paths,
`locale="vi"` props, hreflang alternates; the part-0 layouts wrap both routes.

## Implementation Flow (input to /speckit-tasks)

1. **Manifest flip** (FR-009): 0.4 entry in `lib/tutorial.ts`; brief expected-404
   window until content lands.
2. **English chapter** (FR-001..007): author per the R2 arc — anatomy specimen,
   T/D/I/A vocabulary, the two traces, FR-TEN-05, the FR-MED live example — with
   R3's fenced specimen rows (verbatim) and R4's exercise incl. the opinion hunt.
3. **Vietnamese chapter** (FR-008): translate per R5 — register + glossary, IDs and
   shall-keyword in English, translated shall-statement prose inside quoted rows.
4. **Verify** ([quickstart.md](./quickstart.md)): battery + 0.3↔0.4 pair + verbatim
   spot-check; flag Dong's read-through.
5. **Handoff**: no commits — ready-to-commit report.

## Complexity Tracking

> No constitution violations — table intentionally empty.

## Notes

- The chapter's sharpest hazard is quote drift: every specimen row must survive a
  literal grep against docs/04 (SC-002). When paraphrasing for prose flow, never
  put an ID next to paraphrased text — quote exactly or drop the ID.
- The FR-MED beat closes the 0.1→0.3→0.4 thread in the product's own recent
  history — the strongest evidence Part 0 can offer that the paperwork is alive.
- Commits/pushes remain Dong's; the vi read-through is requested before committing.
