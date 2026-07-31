# Implementation Plan: Tutorial Chapter 1.2 — One Command, Whole World

**Branch**: `main` (no feature branch — consistent with features 001–013) | **Date**: 2026-07-31 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/014-chapter-1-2/spec.md`

## Summary

Ship Part 1's second code chapter: add the compose infrastructure to
`relay-platform` — Postgres, Redis, NATS (JetStream), ClickHouse, each with a
healthcheck, volumes aligned with each store's durability semantics — so that
`docker compose up -d --wait` starts the whole local world and returns only
when every store is *ready*, teaching NFR-MNT-03 as a day-one requirement and
each store's ADR as the reason it exists. The chapter-end state is tag
`part1-ch2` (the series' first incremental tag); the toolchain gate stays green
without Docker via a new string-assertion smoke test over `compose.yaml` in a
**new** file (1.1's fenced files are never edited — the additive-only fence
discipline debuts here). Tutorial side: write the chapter (en + vi, settled
register — "cửa ải", "package", "quả ngọt"), flip 1.2's manifest entry to
published+translated (the first real exercise of the flip drill), and let every
navigation surface update itself (sitemap 26 → 28). Decisions in
[research.md](./research.md).

## Technical Context

**Language/Version**: relay-platform — TypeScript ~5.9 / Node 22 / pnpm 10
(unchanged from 1.1); infra containers — Postgres, Redis, NATS, ClickHouse
images pinned to explicit tags (exact tags verified pullable at implementation;
R1); relay-tutorial — unchanged stack

**Primary Dependencies**: relay-platform: NONE new in package.json (the smoke
test uses string assertions over `compose.yaml` — no YAML parser; R4). New
runtime prerequisite documented for the chapter's full promise: Docker Engine +
Compose v2 (`--wait` support). Tutorial side: none new

**Storage**: The chapter's *subject*, not the feature's: named volumes for
Postgres/NATS/ClickHouse, none for Redis (ephemeral by design — ADR-07/10
made teachable; R1)

**Testing**: relay-platform: `pnpm lint && pnpm typecheck && pnpm test` green
at `part1-ch2` **without Docker** (new `infra.test.ts` asserts compose
declaration facts); with Docker: `docker compose up -d --wait` exits 0, all
four `docker compose ps` states healthy, `down` clean. Tutorial: battery v3
(baseline grows 12 → 14 rows), fence↔repo diffs (1.2's new fences AND 1.1's
ten — additive-only makes both hold at the new tag), ID detector + verbatim
spot-checks, nav battery (footers 1.1↔1.2, sidebar 2 links + 2 forthcoming,
sitemap 28), vi parity incl. byte-identical fences

**Target Platform**: relay-platform: any Node 22 machine for the gate; any
Docker-Compose-v2 machine for the infrastructure; tutorial: static prerendered
pages, both locales

**Project Type**: Two-artifact content feature (code increment + teaching
chapter) — the 013 pattern, second iteration

**Performance Goals**: `up -d --wait` from pulled images to all-healthy well
under the chapter's stated wait expectation (~30 s cold on the reference
machine); no tutorial-side changes

**Constraints**: Chapter facts verbatim to docs/04/05/06; fences byte-match the
repo by diff, not assertion; **no file fenced by 1.1 may be modified** (R3);
Part 0 + 1.1 chapter content untouched (baseline rows must not change); dev-only
credentials clearly marked as such; commits, pushes, AND the `part1-ch2` tag
are Dong's

**Scale/Scope**: relay-platform: 1 new `compose.yaml` (~60 lines), 2 new source
files in `@relay/config` (`infra.ts`, `infra.test.ts`), README section; tutorial:
2 page.mdx (~2,300 prose words each) + 2 figures.ts (3 figures/locale), manifest
flip (1 entry), battery baseline regenerated (14 rows)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Notes |
|---|---|---|
| I–III (isolation, message loss, data paths) | ✅ N/A at this chapter | No services or data paths yet — this chapter erects the stores those principles will govern; the chapter *teaches* the data-path split (CON-01: analytics never in Postgres → ClickHouse's seat at the table). |
| IV. Single source of truth | ✅ Pass | Store facts quoted verbatim from docs/05 §9 / docs/06; the manifest remains the sole navigation source; the tagged repo is the sole truth for shown code (diff-verified, now across two chapters). |
| V. Developer/reader-first | ✅ Pass | The reader ends with one command that stands up the whole world and a shown way to *verify* readiness; port collisions and teardown are addressed, not hidden. |
| VI. Requirement-driven, test-verified | ✅ Pass | The chapter exists to implement NFR-MNT-03 (P1); the gate is machine-verified at the tag without Docker; the compose declaration is itself test-asserted. |
| VII. Boring by design | ✅ Pass | Plain compose file, official images, no wrapper scripts, no YAML-parsing test dependency — string assertions like 1.1's workspace-glob check (R4). |
| Tech & platform constraints | ✅ Pass (trajectory noted) | Exactly the constitution's store list (Postgres, Redis, NATS JetStream, ClickHouse); pinned versions respect the stated floors (PostgreSQL 15+, ClickHouse 24+). The constitution's full single-command constraint **includes a seeded demo tenant** — impossible at this increment (no schema, no services); this chapter delivers the single-command property for the stores, and the tenant lands with schema/services (named in the chapter's FORWARD REF, R8), completing the constraint. The constitution's legacy `docker-compose up` spelling is a PATCH-amendment candidate alongside the known stale items. |

**Pre-Phase-0 verdict: PASS** (Complexity Tracking empty).
**Post-Phase-1 re-check: PASS** — one compose file, two additive source files,
a chapter pair, one manifest flip.

## Project Structure

### Documentation (this feature)

```text
specs/014-chapter-1-2/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── chapter-1-2-contract.md
├── battery-baseline.txt # regenerated (14 rows) at implementation
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code

```text
relay-platform/ (submodule — advances part1-ch1 → part1-ch2, ADDITIVE ONLY)
├── compose.yaml                  # NEW — the chapter's central artifact (R1)
├── README.md                     # MODIFIED (not a 1.1 fence) — infra section
└── packages/config/src/
    ├── infra.ts                  # NEW — INFRA_SERVICES/ports constants (R4)
    └── infra.test.ts             # NEW — compose declaration assertions (R4)

relay-tutorial/ (existing submodule)
├── lib/tutorial.ts                                   # MODIFIED — 1.2 flips to published+translated, readerMinutes (R5)
└── app/{(en),(vi)/vi}/part-1/chapter-02/one-command-whole-world/
    ├── page.mdx                                      # NEW ×2 (R2, R7)
    └── figures.ts                                    # NEW ×2 (R2 beat 7)

/home/dong/work/relay/ (parent)
└── specs/014-chapter-1-2/battery-baseline.txt        # NEW — 14 rows
```

**Structure Decision**: The 013 two-artifact pattern with one new rule made
explicit: a code chapter may only ADD files — files fenced by earlier chapters
are read-only from then on, which is what keeps every prior chapter's fence
contract valid at every later tag (R3). Part-1 layouts, reading shell, SEO —
all already in place; publishing is the manifest flip alone.

## Implementation Flow (input to /speckit-tasks)

1. **Compose infrastructure** (FR-002..004, R1): `compose.yaml` with four
   pinned-image services, healthchecks, semantic volumes; verify
   `up -d --wait` / `ps` healthy / `down` on the reference machine.
2. **Test extension** (FR-006, R4): `infra.ts` constants + `infra.test.ts`
   string assertions; gate green with Docker stopped.
3. **Manifest flip** (FR-008, R5): 1.2 → published+translated; nav surfaces
   self-update (footers, sidebar, sitemap 28).
4. **English chapter** (FR-001..005, 007, R2): the beats; fences mirror the
   repo files byte-for-byte with `title=""` paths; three figures.
5. **Vietnamese chapter** (FR-009, R7): settled register; byte-identical
   fences; naturalization self-review before presenting.
6. **Verify** ([quickstart.md](./quickstart.md)): gate w/o Docker, compose
   replay with Docker, fence diffs (1.1 + 1.2), battery v3 (14 rows,
   prior rows unchanged), nav battery, ID detector, vi parity.
7. **Handoff**: no commits — per-repo report incl. relay-platform's
   commit + `git tag part1-ch2` + push sequence for Dong.

## Complexity Tracking

> No constitution violations — table intentionally empty.

## Notes

- The additive-only rule is the load-bearing novelty: if implementation finds a
  genuine need to edit a 1.1-fenced file, STOP — that is a design change to
  surface, not a silent edit (it would invalidate 1.1's published fences at the
  new tag).
- Image tags are pinned in `compose.yaml` and become chapter fences — verify
  each tag is pullable before writing it into prose; the tag-is-truth caveat
  from 1.1 (versions drift, the chapter tag holds the exact state) repeats in
  the chapter.
- `--wait` only means "healthy" because we define healthchecks — that causal
  link is the chapter's TRAP and must survive editing.
- The gate must never require Docker: run the full toolchain with the daemon
  stopped as an explicit verification step.
- Commits/pushes/tags remain Dong's; vi read-through requested before the
  milestone commit.
