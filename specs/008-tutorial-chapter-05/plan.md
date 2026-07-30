# Implementation Plan: Tutorial Chapter 0.5 — Deciding Out Loud

**Branch**: `main` (no feature branch — consistent with features 001–007) | **Date**: 2026-07-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/008-tutorial-chapter-05/spec.md`

## Summary

Publish the Part 0 finale in both locales: an English chapter that distills 224
requirements into the drivers table, walks the full ADR anatomy on ADR-03, teaches
the review discipline ("attack the driver, not the choice"), and closes the
0.1→0.3→0.4→0.5 paperwork chain with ADR-13/14 — the reversed non-goal now defended
in architecture — plus a Vietnamese translation under the settled conventions, and
the final Part 0 manifest flip. Fifth consecutive pure-content feature; zero
component changes; one new verification obligation (the last-published-chapter
footer state). Decisions in [research.md](./research.md).

## Technical Context

**Language/Version**: TypeScript 5.9 / Next.js 16.2.12 (existing relay-tutorial app), Node.js 22, pnpm 10

**Primary Dependencies**: None new. Reused: MDX pipeline + shell + boxes (002), i18n + `/vi` mirror + hreflang (004)

**Storage**: N/A — two MDX files and one manifest entry edit

**Testing**: `pnpm lint && pnpm build`; the settled scripted battery with the ID detector extended to `ADR-nn`/`D1–D8` (checked against docs/05); the 0.4↔0.5 pair; the Part 0 completion checks (five links, zero forthcoming); the last-chapter footer verification; Dong's Vietnamese read-through

**Target Platform**: Static prerendered pages, both locales

**Project Type**: Content feature inside the existing web app (relay-tutorial submodule)

**Performance Goals**: None new — two more static routes

**Constraints**: docs/05 + docs/06 (current, ADR-13/14-inclusive) frozen as fact sources — the 007 verbatim definition applies (words exact, layout free); ≤3 fences, no pipe tables; identifier discipline in the vi file; 0.1–0.4 prose immutable; zero hand-edited navigation; the empty-next footer state is verified, and any gap is surfaced rather than patched (research R6)

**Scale/Scope**: 2 MDX files (~3,000 words canonical each), 1 manifest flip, 0 component changes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Notes |
|---|---|---|
| I–III (isolation, message loss, data paths) | ✅ N/A | Static content; no Relay runtime. |
| IV. Single source of truth | ✅ Pass | Driver/ADR facts: docs/05/06 only, quoted per the verbatim definition. Series data: the manifest. Translation source: the final English file. |
| V. Developer/reader-first | ✅ Pass | The chapter completes the reader's Part 0 portfolio. |
| VI. Requirement-driven, test-verified | ✅ Pass | Tasks trace to FR-001..009; the extended ID detector, completion checks, and footer verification are scripted; the unscriptable judgment goes to the named reviewer. |
| VII. Boring by design | ✅ Pass | Zero new machinery, fifth consecutive proof; fittingly, the chapter *teaches* the constitution's own ADR habit. |
| Tech & platform constraints | ✅ Pass | Unchanged stack. |

**Pre-Phase-0 verdict: PASS** (Complexity Tracking empty).
**Post-Phase-1 re-check: PASS** — two content files, one manifest entry, nothing else.

## Project Structure

### Documentation (this feature)

```text
specs/008-tutorial-chapter-05/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── chapter-05-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (relay-tutorial submodule)

```text
relay-tutorial/
├── lib/
│   └── tutorial.ts                      # MODIFIED — 0.5: status published, translatedIn ["vi"] (R1)
└── app/
    ├── part-0/chapter-05/deciding-out-loud/
    │   └── page.mdx                     # NEW — English chapter (R2–R4)
    └── vi/part-0/chapter-05/deciding-out-loud/
        └── page.mdx                     # NEW — Vietnamese translation (R5)
```

**Structure Decision**: The 004 C5 contract, fifth and final Part 0 exercise:
same-slug mirror paths, `locale="vi"` props, hreflang alternates; part-0 layouts wrap
both routes.

## Implementation Flow (input to /speckit-tasks)

1. **Manifest flip** (FR-009): 0.5 entry in `lib/tutorial.ts` — the flip that
   completes Part 0; brief expected-404 window.
2. **English chapter** (FR-001..007): author per the R2 arc — drivers distillation
   (D1/D8), ADR anatomy on ADR-03, the review discipline, ADR-13/14 closing the
   chain, "reading the fourteen together" — with R3's three fences and R4's
   exercise (drivers table + two ADRs).
3. **Vietnamese chapter** (FR-008): translate per R5 under the settled conventions.
4. **Verify** ([quickstart.md](./quickstart.md)): battery + extended detector +
   0.4↔0.5 pair + Part 0 completion checks + the last-chapter footer state in both
   locales/themes; flag Dong's read-through.
5. **Handoff**: no commits — ready-to-commit report, noting Part 0 completion.

## Complexity Tracking

> No constitution violations — table intentionally empty.

## Notes

- 0.5 is the first page to exercise the shell's empty-next footer path (built in
  feature 002 with `next && …` guards). Expected: a clean single-card grid +
  contents link. If it renders poorly, report it as an infrastructure finding for
  its own feature — do not patch the shell here (research R6).
- The chapter's close is Part 0's close: the reader now holds the full paperwork
  chain their next forty-four chapters will keep citing.
- Commits/pushes remain Dong's; the vi read-through is requested before committing.
