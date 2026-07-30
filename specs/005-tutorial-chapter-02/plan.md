# Implementation Plan: Tutorial Chapter 0.2 — Four People Who Will Judge Us

**Branch**: `main` (no feature branch — consistent with features 001–004) | **Date**: 2026-07-30 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/005-tutorial-chapter-02/spec.md`

## Summary

Publish chapter 0.2 in both locales: an English chapter authored from
docs/02-personas.md (personas derived from 0.1's artifacts; the influence ordering;
the invisible end user as a protocol constraint; the trade-off resolution order), a
Vietnamese translation in the series' established storytelling register, and a
one-entry manifest flip that lets every navigation surface update itself. This is the
first pure-content feature on the finished 002/004 infrastructure — it deliberately
changes zero components. Decisions in [research.md](./research.md).

## Technical Context

**Language/Version**: TypeScript 5.9 / Next.js 16.2.12 (existing relay-tutorial app), Node.js 22, pnpm 10

**Primary Dependencies**: None new. Reused as-is: MDX pipeline + chapter shell + boxes (002), i18n dictionaries/helpers + `/vi` mirror + hreflang pattern (004)

**Storage**: N/A — two MDX files and one manifest entry edit

**Testing**: `pnpm lint && pnpm build` gate; the established scripted chapter battery (word count, box counts, en↔vi parity, hreflang, lang scoping) plus the new bidirectional 0.1→0.2 navigation checks; Dong's manual Vietnamese read-through

**Target Platform**: Static prerendered pages in relay-tutorial (both locales)

**Project Type**: Content feature inside the existing web app (relay-tutorial submodule)

**Performance Goals**: None new — two more statically prerendered routes

**Constraints**: Content sources frozen — docs/02 (persona facts), docs/01 + chapter 0.1 (positioning context); format rules docs/07 §2; chapter 0.1 prose immutable; zero hand-edited navigation (SC-006); no infrastructure changes (research R5); glossary continuity with the approved 0.1 Vietnamese translation

**Scale/Scope**: 2 MDX files (~2,900 words each by the canonical count), 1 manifest entry flip, 0 component changes

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Notes |
|---|---|---|
| I–III (isolation, message loss, data paths) | ✅ N/A | Static content; no Relay runtime. |
| IV. Single source of truth | ✅ Pass | Persona facts have one source (docs/02); series data one source (the manifest — publishing is a one-entry flip); the en chapter is the single source for the vi translation. |
| V. Developer/reader-first | ✅ Pass | The chapter *is* reader value; the exercise produces the reader's own artifact. |
| VI. Requirement-driven, test-verified | ✅ Pass | Tasks trace to FR-001..008; the scripted battery covers every SC that scripts can reach; the one unscriptable judgment (translation quality) is assigned to a named reviewer. |
| VII. Boring by design | ✅ Pass | Zero new machinery; the feature exists to prove the existing machinery's "add a chapter" contract. |
| Tech & platform constraints | ✅ Pass | Unchanged stack. |

**Pre-Phase-0 verdict: PASS** (Complexity Tracking empty).
**Post-Phase-1 re-check: PASS** — design adds two content files and edits one
manifest entry; nothing else.

## Project Structure

### Documentation (this feature)

```text
specs/005-tutorial-chapter-02/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── chapter-02-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code (relay-tutorial submodule)

```text
relay-tutorial/
├── lib/
│   └── tutorial.ts                      # MODIFIED — chapter 0.2 entry: status published,
│                                        #   translatedIn ["vi"], readerMinutes validated (R1)
└── app/
    ├── part-0/chapter-02/four-people-who-will-judge-us/
    │   └── page.mdx                     # NEW — English chapter (R2, R3)
    └── vi/part-0/chapter-02/four-people-who-will-judge-us/
        └── page.mdx                     # NEW — Vietnamese translation (R4)
```

**Structure Decision**: Exactly the feature-004 C5 contract: same-slug mirror paths,
`locale="vi"` props in the vi file, hreflang alternates in both files' metadata, and
the part-0 layouts (en and vi) already in place wrap both routes automatically.

## Implementation Flow (input to /speckit-tasks)

1. **Manifest flip** (FR-008): update the 0.2 entry in `lib/tutorial.ts`; verify both
   landings and 0.1's footers react (this proves SC-006 before any content exists —
   the link will 404 until step 2, which is expected mid-implementation).
2. **English chapter** (FR-001..006): author `page.mdx` per the R2 arc with the R3
   exercise; run the scripted battery.
3. **Vietnamese chapter** (FR-007): translate per R4 (storytelling register,
   glossary continuity, names unchanged); parity checks.
4. **Metadata** (FR-007): hreflang alternates + vi title/description in both files
   (same pattern as 0.1).
5. **Verify** ([quickstart.md](./quickstart.md)): full battery + the new 0.1↔0.2
   navigation pair in both locales; flag Dong's read-through.
6. **Handoff**: no commits — ready-to-commit report with suggested messages.

## Complexity Tracking

> No constitution violations — table intentionally empty.

## Notes

- Chapter 0.1's rendered footers change (next-card becomes a link) with zero edits to
  0.1's files — that is the manifest doing its job, not a violation of 0.1's
  immutability.
- The recent product update (hosted media) did not touch docs/02; if persona nuance
  for media arrives later, it enters via a docs/02 revision and a `REVISED` note,
  never via invention here (spec edge case).
- Commits/pushes remain Dong's (standing instruction); the Vietnamese read-through is
  requested before committing.
