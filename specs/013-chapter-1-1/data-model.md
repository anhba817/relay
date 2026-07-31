# Data Model: Tutorial Chapter 1.1 — The Monorepo and the Toolchain

**Feature**: `specs/013-chapter-1-1` · **Date**: 2026-07-31

## E1 — relay-platform scaffold (the code artifact)

| Element | Rule | Source |
|---|---|---|
| Repo | github.com/anhba817/relay-platform, second submodule beside relay-tutorial, own history | FR-006, R6 |
| Workspace | `pnpm-workspace.yaml`: `packages/*`, `services/*` (services empty + .gitkeep until 1.4) | R1 |
| Toolchain | Node 22 + pinned pnpm (`packageManager`); strict `tsconfig.base.json`; flat ESLint (typescript-eslint) + Prettier; Vitest | R1, ADR-01 |
| First package | `packages/config` (`@relay/config`): shared tsconfig/lint fragments + `src/index.ts` + one passing smoke test | R1 |
| Checks | Root scripts `lint` / `typecheck` / `test` — all green at HEAD and at the tag | FR-004/006, SC-002 |
| Tag | `part1-ch1` (docs/07 §2 convention) — created by Dong at commit time | FR-006, R6 |

## E2 — Manifest additions (lib/tutorial.ts, four entries under Part 1)

| Field | 1.1 | 1.2–1.4 |
|---|---|---|
| `id` / `title` | "1.1" / "The monorepo and the toolchain" | docs/07 titles ("One command, whole world" / "The protocol package" / "Walking skeleton") |
| `status` | `published` + `translatedIn: ["vi"]` | `forthcoming` |
| `path` | `/part-1/chapter-01/the-monorepo-and-the-toolchain` | reserved per URL convention |
| `titleVi` | "Monorepo và bộ công cụ" (Dong reviews) | "Một câu lệnh, cả thế giới" / "Gói protocol" / "Bộ khung biết đi" (Dong reviews) |
| `readerProduces` | "A running pnpm workspace — TypeScript, lint, and a passing test suite" (+ vi) | per docs/07 Built column |
| `sourceDoc` | "docs/05-sad.md, docs/06-adr-deep-dives.md" | ditto/appropriate |
| `readerMinutes` | 90 | docs/07 estimates |

**Downstream (automatic)**: 0.5 footers gain the next card (both locales);
sidebar/landing show Part 1 mixed (1 link + 3 forthcoming); sitemap 24 → 26;
SEO/JSON-LD for the new pages from the manifest.

## E3 — Chapter 1.1 content structure (both page.mdx files)

| Element | Rule | Source |
|---|---|---|
| Metadata | Established pattern (title + " — Building Relay", description, hreflang pair) | FR-001 |
| Arc | R2's eight beats: gear-change open → decisions summary → ADR-01 (deep-dive quotes verbatim) → the build (commands + files) → TRAP → figures ×3 → boxes → exercise-is-the-build + takeaways + CHECKPOINT | FR-002..005 |
| Fences | Two kinds — commands and file contents; file fences byte-match the tagged repo; en/vi fences byte-identical | FR-007, R4, R7 |
| Boxes | WHY ≥2, **TRAP ≥1 (debut)**, SkipAhead =1 (names `part1-ch1`), ForwardRef ≥1 (1.3 protocol package; 2.x reuse of the checks), CHECKPOINT =1 (the three checks green) | FR-005 |
| Figures | 3/locale (workspace map; ADR-01 shared-protocol payoff; toolchain pipeline) via colocated figures.ts; halves rule | FR-005, R2 |
| vi register | Naturalized (0.5 standard); code/commands/identifiers/tag English | FR-009, R7 |

## E4 — Battery v3 (the amended measured rules)

| Measure | v3 rule | Change from v2 |
|---|---|---|
| Canonical words | Prose OUTSIDE fences only (awk fence-strip before count), 2,000–4,000 | fences no longer counted as words |
| Fences | Counted, uncapped for code chapters; specimen verbatim rules unchanged for quoted document content | cap removed (was Part 0 specimen economy) |
| Boxes | Why/SkipAhead/ForwardRef/Checkpoint **+ Trap** | TRAP added as counted class |
| Figures | 2–4, en==vi, captions, halves | unchanged |
| Baseline | Regenerated once for all 12 chapter files under v3; recorded in specs/013-chapter-1-1/battery-baseline.txt | formula-side change only for Part 0 |
| Authority | docs/07 §2 format table gains the code-chapter note (words exclude code; TRAP counted; fences uncapped) | R3 |

## E5 — Chapter/code comparison set (FR-007, enumerated)

The quickstart enumerates every file-content fence in the chapter and its repo
path; verification diffs each pair at the tag and replays the command fences on
a fresh clone. The enumeration lives in the quickstart, not in machinery.
