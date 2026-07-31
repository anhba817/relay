# Implementation Plan: Tutorial Chapter 1.1 — The Monorepo and the Toolchain

**Branch**: `main` (no feature branch — consistent with features 001–012) | **Date**: 2026-07-31 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/013-chapter-1-1/spec.md`

## Summary

Open Part 1 with the series' first code chapter: initialize `relay-platform`
(github.com/anhba817/relay-platform, second submodule) as the pnpm workspace
ADR-01's consequences describe — strict TypeScript, one lint config, Vitest, a
shared `@relay/config` package with a smoke test — ending in the format's
runnable, tested state at tag `part1-ch1`; write the chapter (en + vi) that
builds it: the one-page decisions summary, ADR-01 taught through its deep dive,
the TRAP debut (config copy-paste drift), three figures; amend the battery for
code chapters (prose-only word counts, uncapped counted code fences, TRAP as a
counted box); and seed the manifest with all four Part 1 chapters so every
navigation surface — including 0.5's first-ever next card — updates itself.
Decisions in [research.md](./research.md).

## Technical Context

**Language/Version**: relay-platform — TypeScript 5.x / Node.js 22 (ADR-01 "Node
20+"), pnpm 10 (`packageManager`-pinned); relay-tutorial — unchanged stack

**Primary Dependencies**: relay-platform (all NEW, dev-only at this stage):
typescript, eslint + typescript-eslint (flat config), prettier, vitest. Tutorial
side: none new (shell, figures, sidebars all reused)

**Storage**: N/A — a scaffold, two chapter files, two figures.ts, one manifest
edit, one docs/07 format-row amendment

**Testing**: relay-platform: `pnpm lint && pnpm typecheck && pnpm test` green at
tag `part1-ch1` (fresh-clone replay); tutorial: battery v3 (prose-only words,
boxes incl. TRAP ≥1, figures 2–4, halves), chapter↔code fence diffs (enumerated),
ID detector + verbatim spot-checks, nav battery (0.5 next card, Part 1 mixed
sidebar, sitemap 26), vi parity incl. byte-identical code fences

**Target Platform**: relay-platform: any Node 22 machine (CI arrives in a later
chapter); tutorial: static prerendered pages, both locales

**Project Type**: Two-artifact content feature — a code scaffold + its teaching
chapter (the pattern all future code chapters follow)

**Performance Goals**: None new; the scaffold is empty by design

**Constraints**: Chapter facts verbatim to docs/05/06 (ADR-01); chapter-shown
commands/files match the tag by diff, not assertion; Part 0 chapters untouched
(baseline regenerates once under the v3 formula — counts change formula-side,
not content-side); no dead links (1.2–1.4 forthcoming); commits, pushes, AND the
`part1-ch1` tag are Dong's

**Scale/Scope**: 1 new submodule (~12 scaffold files); 2 page.mdx (~2,500 prose
words each) + 2 figures.ts (3 figures/locale); manifest +4 entries; docs/07 §2
one-row amendment; battery baseline regenerated (v3)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Notes |
|---|---|---|
| I–III (isolation, message loss, data paths) | ✅ N/A at this chapter | No services, no data paths yet — the scaffold is the ground they will be built on; the chapter *teaches from* the constitution's own ADR-01. |
| IV. Single source of truth | ✅ Pass | ADR facts quoted verbatim from docs/05/06; the manifest stays the sole navigation source; the tagged repo is the sole truth for the chapter's code (drift checked by diff). |
| V. Developer/reader-first | ✅ Pass | The chapter ends with the reader holding a working scaffold; the decisions summary makes Part 1 enterable without Part 0. |
| VI. Requirement-driven, test-verified | ✅ Pass | Tasks trace to FR-001..010; the runnable-tested state is machine-verified at the tag; the battery v3 amendment is itself scripted. |
| VII. Boring by design | ✅ Pass | Plain pnpm scripts (no Turborepo/Nx until needed); Vitest as the boring TS runner; one shared-config package instead of copies — the chapter's own TRAP enforces the principle. |
| Tech & platform constraints | ✅ Pass | TypeScript/Node per ADR-01 and the constitution's stack table; pnpm workspace per docs/07 §3. |

**Pre-Phase-0 verdict: PASS** (Complexity Tracking empty).
**Post-Phase-1 re-check: PASS** — a scaffold, a chapter pair, a manifest edit,
one format-row amendment.

## Project Structure

### Documentation (this feature)

```text
specs/013-chapter-1-1/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── chapter-1-1-contract.md
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code

```text
relay-platform/ (NEW submodule — github.com/anhba817/relay-platform)
├── package.json                 # root: scripts lint/typecheck/test; packageManager pin
├── pnpm-workspace.yaml          # packages/* , services/*
├── tsconfig.base.json           # strict compiler baseline
├── eslint.config.mjs            # flat config, typescript-eslint
├── .prettierrc / .gitignore / README.md / .nvmrc
├── packages/config/             # @relay/config — shared tsconfig/lint fragments
│   ├── package.json / tsconfig.json
│   ├── src/index.ts             # exported config constants (smoke-test target)
│   └── src/index.test.ts        # the first passing test
└── services/.gitkeep            # ghosted until 1.4

relay-tutorial/ (existing submodule)
├── lib/tutorial.ts                                   # MODIFIED — Part 1's four chapters (R5)
├── app/{(en),(vi)/vi}/part-1/layout.tsx              # NEW ×2 — reading-shell mounts (copies of part-0's)
└── app/{(en),(vi)/vi}/part-1/chapter-01/the-monorepo-and-the-toolchain/
    ├── page.mdx                                      # NEW ×2 (R2, R7)
    └── figures.ts                                    # NEW ×2 (R2 beat 6)

/home/dong/work/relay/ (parent)
├── .gitmodules                                       # MODIFIED — second submodule (R6)
├── docs/07-tutorial-plan.md                          # MODIFIED — §2 battery-v3 note (R3)
└── specs/013-chapter-1-1/battery-baseline.txt        # NEW — regenerated under the v3 formula
```

**Structure Decision**: The two-artifact pattern (scaffold + chapter) with the
tag as the bridge: the chapter's SKIP AHEAD names `part1-ch1`, and verification
diffs the chapter's fences against the tagged files.

## Implementation Flow (input to /speckit-tasks)

1. **Submodule + scaffold** (FR-006): attach relay-platform; build R1's
   workspace; all three checks green.
2. **Battery v3** (FR-005, R3): docs/07 §2 amendment; the v3 formula; regenerate
   the baseline for the existing ten chapters (formula change only).
3. **Manifest** (FR-008): Part 1's four entries; the 0.5-next-card and
   Part-1-mixed states appear.
4. **English chapter** (FR-001..005, 007): R2's beats; fences mirror the
   scaffold exactly; figures.
5. **Vietnamese chapter** (FR-009): naturalized register; byte-identical code
   fences.
6. **Verify** ([quickstart.md](./quickstart.md)): scaffold replay at HEAD (tag
   comes at commit time), fence diffs, battery v3, nav battery, SEO spot; flag
   Dong's V-checks.
7. **Handoff**: no commits — per-repo report incl. the exact
   commit/tag/push sequence for relay-platform (`git tag part1-ch1`).

## Complexity Tracking

> No constitution violations — table intentionally empty.

## Notes

- The battery v3 formula change regenerates the baseline ONCE for all chapters;
  Part 0 content is untouched — if any Part 0 file's boxes/fences/figures counts
  change, that is a defect, not drift.
- The tag is part of the definition of done but is Dong's to create — the
  quickstart verifies at HEAD and the handoff hands over the tag command.
- Chapter fences are the contract: file-content fences must diff clean against
  the repo; command fences must replay clean on a fresh clone.
- Consult `node_modules/next/dist/docs/` only if tutorial-side route work
  surprises (none expected — established patterns).
- Commits/pushes/tags remain Dong's; vi read-through requested before the
  milestone commit.
