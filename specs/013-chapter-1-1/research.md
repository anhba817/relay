# Research: Tutorial Chapter 1.1 — The Monorepo and the Toolchain

**Feature**: `specs/013-chapter-1-1` · **Date**: 2026-07-31

Grounded in docs/05 §9 (ADR-01 terse: drivers D7/D8, the Go and polyglot
rejections), docs/06 (ADR-01 deep dive: "the SDK must be TypeScript regardless";
protocol drift "becomes a compile error instead of a production incident"; the
decision "TypeScript/Node 20+ everywhere"; consequences "one `pnpm` workspace, one
test runner, one lint config"; revisit-when: >20% event-loop time in crypto),
docs/07 §2–3, and the constitution's technology constraints.

## R1 — The relay-platform scaffold (what the chapter builds)

- **Decision**: `relay-platform` initialized as a pnpm workspace shaped for the
  series' future: `pnpm-workspace.yaml` covering `packages/*` and `services/*`
  (services stay empty until 1.4); Node 22 (satisfies ADR-01's "Node 20+"),
  `packageManager`-pinned pnpm; a strict root `tsconfig.base.json`; ESLint (flat
  config, typescript-eslint) + Prettier config at the root; **Vitest** as the
  test runner; one real package — `packages/config` (`@relay/config`) — holding
  the shared tsconfig/lint fragments other packages extend, plus a smoke test
  that proves the runner and the strict compiler settings actually bite. Root
  scripts: `lint`, `typecheck`, `test` — the chapter's "toolchain checks".
- **Rationale**: docs/07's 1.1 row verbatim (workspace, TS config, lint, test
  runner); ADR-01's consequences line is the shape ("one pnpm workspace, one test
  runner, one lint config"); a shared-config package is the smallest artifact
  that makes workspace discipline *demonstrable* rather than asserted — and it
  sets up the TRAP (R3). Vitest: the boring modern TS runner (fast, zero-config
  TS, workspace-aware); the constitution fixes the language and runtime, not the
  runner.
- **Alternatives considered**: no packages until 1.3 (then the test runner has
  nothing to run and "tested state" is hollow); Jest (heavier TS story for no
  gain); Turborepo/Nx (machinery 1.1 doesn't need — plain pnpm scripts suffice
  until there's something to orchestrate; adding later is one chapter's honest
  work).

## R2 — Chapter arc (eight beats)

- **Decision**:
  1. **Cold open — the gear change**: five chapters of paperwork ended with
     "the building begins"; here is the first commit. What we build today is
     deliberately humble: an empty workspace that already enforces its rules.
  2. **The decisions summary** (FR-002): the docs/07-promised one-page lookup —
     the positioning sentence, the resolution order, the ★s, the eight drivers,
     the fourteen ADRs in one breath each — as a compact list, linking back.
  3. **ADR-01, taught through its deep dive**: the "right tool per service"
     instinct; the decisive observation (the SDK must be TS regardless — so
     sharing `@relay/protocol` makes drift a compile error, quoted verbatim);
     Go's real-but-not-binding advantages; the polyglot showcase read by
     reviewers as "five half-maintained toolchains"; the revisit-when.
  4. **The build**: init repo → `pnpm-workspace.yaml` → strict base tsconfig →
     flat ESLint config → Vitest → `packages/config` + the smoke test → all
     three checks green. Each step shows the command and the file, and each
     file's *why* ties to a driver (D8 throughout).
  5. **TRAP debut** (FR-005): the naive move — copy-pasting tsconfig/eslint
     fragments per package "to keep them independent". The bug: configs drift
     silently; six months later one package compiles what another rejects, and
     the shared-types payoff quietly dies. The fix the chapter already built:
     one config package, everything extends it.
  6. **Figures (3)**: the workspace map (root → packages/* → services/* with
     what will live where, 1.2–1.4 ghosted); the ADR-01 payoff diagram
     (`@relay/protocol` consumed by gateway + API + SDK — "one commit, not a
     production incident"); the toolchain pipeline (lint → typecheck → test as
     the gate every future chapter passes).
  7. **Boxes**: WHY ×2 (ADR-01/D8 — why one language; why a config package
     instead of copies), SkipAhead (naming tag `part1-ch1`), ForwardRef (1.3
     builds `@relay/protocol` on this workspace; 2.x chapters run these same
     three checks).
  8. **Exercise + takeaways + CHECKPOINT**: the exercise IS the build (Part 1
     convention shift — the reader builds Relay itself); the checkpoint is the
     three checks passing + the tag existing.
- **Rationale**: FR-001..005; the beats map docs/07's row plus the format's
  code-chapter obligations.

## R3 — The battery evolves for code chapters (battery v3)

- **Decision**: Code chapters count differently, faithfully to docs/07's
  "2,000–4,000 words **+ code**":
  - **Canonical words = prose outside fences** — the formula gains an awk strip
    of fenced blocks before the word count (Part 0 chapters are unaffected in
    bound terms: their specimen fences were tiny; the baseline is regenerated
    once with the v3 formula for all chapters).
  - **Fences = code blocks, uncapped** but counted (the ≤3 rule was Part 0's
    specimen economy, not a series law; specimen-fence verbatim rules still
    apply to any quoted document content).
  - **Boxes gain TRAP** as a counted class (≥1 in code chapters).
  - Figures rule (2–4, halves) unchanged.
- **Rationale**: Without the fence strip, code volume corrupts the word measure;
  docs/07's own phrasing ("+ code") says code was never meant to count. The
  amendment lands in docs/07 §2's format table (one row edit extending the
  battery note) and the new baseline.
- **Alternatives considered**: keeping the old formula (word counts become
  meaningless for code chapters); capping code fences (fights the medium).

## R4 — Chapter/code no-drift verification (FR-007)

- **Decision**: The chapter shows two kinds of fences: **commands** (start with
  `$ ` or are single commands) and **file contents** (each introduced by prose
  naming the path). Verification enumerates the file-content fences in the
  quickstart and diffs each against the tagged repo file; commands are replayed
  against a fresh clone at the tag (install → lint → typecheck → test) proving
  SC-002 and SC-005's path. Enumerated, not auto-discovered — honest and cheap;
  auto-matching fence-to-file is machinery this feature doesn't need.
- **Rationale**: FR-007 says compared, not asserted; enumeration keeps the
  comparison reviewable.

## R5 — Manifest: Part 1's four chapters

- **Decision**: Add all four docs/07 Part 1 chapters (mirroring how 002 seeded
  all of Part 0): 1.1 `The monorepo and the toolchain` (published,
  translatedIn vi, path `/part-1/chapter-01/the-monorepo-and-the-toolchain`,
  readerProduces "A running pnpm workspace — TypeScript, lint, and a passing
  test suite", sourceDoc "docs/05-sad.md, docs/06-adr-deep-dives.md",
  readerMinutes 90) and 1.2–1.4 forthcoming with docs/07 titles. Draft vi
  titles for Dong's review: 1.1 "Monorepo và bộ công cụ", 1.2 "Một câu lệnh,
  cả thế giới", 1.3 "Gói protocol", 1.4 "Bộ khung biết đi"; 1.1
  readerProducesVi "Một pnpm workspace chạy được — TypeScript, lint, và bộ test
  xanh".
- **Rationale**: FR-008; forthcoming entries render as unlinked sidebar/landing
  structure (built in 012, exercised for real here).

## R6 — Submodule and hand-off discipline

- **Decision**: `git submodule add https://github.com/anhba817/relay-platform`
  beside `relay-tutorial` (the repo exists, empty); all scaffold work happens
  inside; **Dong commits, pushes, and creates the `part1-ch1` tag** (tags are
  git writes — same standing rule as commits). The handoff supplies the exact
  tag command. The parent gains `.gitmodules` + the pin.
- **Rationale**: FR-006 + the 001 precedent + the no-commit standing
  instruction extended explicitly to tags.

## R7 — Vietnamese edition

- **Decision**: Prose translated in the naturalized register (the 0.5 standard:
  "tin nhắn", no calques); ALL code fences byte-identical to English (commands,
  file contents — no glosses inside code; a "(Dịch nghĩa:)" paragraph only where
  a fence's *output* needs explaining); identifiers, tag names, package names,
  file paths English; figures via the colocated vi `figures.ts` with translated
  labels. Byte-identical fences double as a parity check (en/vi fence diff must
  be empty).
- **Rationale**: FR-009; code that differs between locales would be drift by
  construction.
