# Implementation Plan: Tutorial Chapter 1.3 — The Protocol Package

**Branch**: `main` (no feature branch — consistent with features 001–015) | **Date**: 2026-08-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/016-chapter-1-3/spec.md`

## Summary

Ship Part 1's third code chapter: build `@relay/protocol` in relay-platform —
the shared wire contract 1.1 promised. The frame vocabulary is *derived* from
the documents (EIR-WS-02's `{type, payload}` envelope, EIR-WS-03's
`connection.ack` with resume cursor, SAD §5.1's `message.send`/`message.ack`,
FR-RTM-05's six event kinds, FR-RTM-04's truncation flag, close codes 4001/4009
plus the two classes EIR-WS-06 names without numbering — every gap the
documents leave is a **recorded chapter decision**, never a silent invention).
Zod schemas are the single source of truth; the static types are inferred from
them, so types and validation cannot drift (R3). Zod is the workspace's first
runtime dependency — taken deliberately, pinned, and taught (the chapter's
TRAP is validation-library sprawl). Additive-only continues: new package
directory only, all thirteen prior fences hold at tag `part1-ch3`. Tutorial
side: chapter en+vi at the settled register, manifest flip (sitemap 28 → 30),
and the 015 suggestions allowlist proven to admit the new pages automatically.
Decisions in [research.md](./research.md).

## Technical Context

**Language/Version**: relay-platform — TypeScript ~5.9 / Node 22 / pnpm 10
(unchanged); NEW runtime dependency: `zod` (current stable major, pinned by
lockfile at install — the library itself is fixed by docs/07 §3's row);
relay-tutorial — unchanged stack

**Primary Dependencies**: relay-platform: zod (the first non-dev dependency in
the workspace — R1); everything else reused. Tutorial side: none new

**Storage**: N/A — a workspace package, two chapter files, two figures.ts, one
manifest flip

**Testing**: relay-platform: the gate (`pnpm lint && pnpm typecheck && pnpm
test`) green at `part1-ch3`, with a real protocol suite — table-driven
accept/reject cases per schema, round-trip type inference checks (R4); test
count grows from 6 to ≥12. Tutorial: battery v3 (baseline 14 → 16 rows), fence
diffs across THREE chapters (1.1's ten + 1.2's three + 1.3's new set), ID
detector extended to frame names (document-derived or marked decisions), nav
battery (footers 1.2↔1.3, sidebar 3+1, sitemap 30), vi parity incl.
byte-identical fences, suggestions-allowlist admission check (R6)

**Target Platform**: any Node 22 machine for the gate (no Docker needed — the
package is pure computation); tutorial: static prerendered pages, both locales

**Project Type**: Two-artifact content feature (code increment + teaching
chapter) — third iteration of the 013 pattern

**Performance Goals**: None new — schema validation cost is not at issue at
this stage (services arrive in 1.4)

**Constraints**: Frame vocabulary derived from docs/04/05 with gaps explicitly
marked as recorded decisions (FR-003/FR-010); zod pinned and justified in
prose; **no file fenced by 1.1 or 1.2 may be modified** (additive-only, R2);
chapter fences byte-match the repo; Part 0–1.2 content untouched; commits,
pushes, AND the `part1-ch3` tag are Dong's

**Scale/Scope**: relay-platform: `packages/protocol/` (~6 source files +
tests, ~250 lines); tutorial: 2 page.mdx (~2,400 prose words each) + 2
figures.ts (3 figures/locale), manifest flip (1 entry), battery baseline
regenerated (16 rows)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Notes |
|---|---|---|
| I. Tenant isolation | ✅ N/A at this chapter | No data access yet — but the frame schemas the chapter defines are the vocabulary Principle I's cross-tenant suite will later attack through; nothing here weakens it. |
| II. No acknowledged loss | ✅ Pass (teaching) | The chapter *teaches* the ack-after-commit frame flow (SAD §5.1 quoted) and the cursor/sequence semantics that make ADR-07's lossy fan-out safe — the package encodes `message.ack {seq}` and per-channel cursors exactly as the documents define them. |
| III. Two data paths | ✅ N/A | No analytics involvement. |
| IV. Single source of truth | ✅ Pass | The package IS the principle applied to the wire: one home for the contract (ADR-01's consequence); zod schemas as the single source with types inferred (R3) extends it inside the package. |
| V. Developer/reader-first | ✅ Pass | Contract-first with runtime validation is what makes SDK ergonomics and error clarity possible later; the chapter's error-code registry mirrors EIR-API-04's shape. |
| VI. Requirement-driven, test-verified | ✅ Pass | Every frame traces to an EIR/FR/SAD source or a marked decision; "input validated against a schema before processing" is this chapter's literal subject; the suite is meaningful (reject cases). |
| VII. Boring by design | ✅ Pass | One package, one validation library for the whole workspace (the TRAP warns against sprawl); zod is the stated choice in docs/07's row — no bespoke validators, no codegen. |
| Tech & platform constraints | ✅ Pass | TypeScript everywhere (ADR-01); the package is exactly the shared-types mechanism the constitution's ADR-01 clause names. |

**Pre-Phase-0 verdict: PASS** (Complexity Tracking empty).
**Post-Phase-1 re-check: PASS** — one new package, a chapter pair, one flip.

## Project Structure

### Documentation (this feature)

```text
specs/016-chapter-1-3/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── chapter-1-3-contract.md
├── battery-baseline.txt # regenerated (16 rows) at implementation
└── tasks.md             # Phase 2 output (/speckit-tasks — NOT created by /speckit-plan)
```

### Source Code

```text
relay-platform/ (submodule — advances part1-ch2 → part1-ch3, ADDITIVE ONLY)
└── packages/protocol/                # NEW — @relay/protocol (R1)
    ├── package.json                  # private, type module, zod pinned
    ├── tsconfig.json                 # extends ../../tsconfig.base.json
    └── src/
        ├── frames.ts                 # envelope + frame schemas (R2), types inferred (R3)
        ├── codes.ts                  # close codes + error-code registry (R2)
        ├── index.ts                  # public surface re-exports
        ├── frames.test.ts            # accept/reject tables per frame (R4)
        └── codes.test.ts             # registry integrity checks (R4)

relay-tutorial/ (existing submodule)
├── lib/tutorial.ts                                   # MODIFIED — 1.3 flips to published+translated (R6)
└── app/{(en),(vi)/vi}/part-1/chapter-03/the-protocol-package/
    ├── page.mdx                                      # NEW ×2 (R5, R7)
    └── figures.ts                                    # NEW ×2 (R5 beat 8)

/home/dong/work/relay/ (parent)
└── specs/016-chapter-1-3/battery-baseline.txt        # NEW — 16 rows
```

**Structure Decision**: The 013 pattern, third pass. The package lands under
the existing `packages/*` glob, the vitest include pattern, and the shared
tsconfig — zero edits to any fenced file (root `package.json` is untouched
because zod is a *package-level* dependency of `@relay/protocol`, not a
workspace-root one — which is itself a teaching point: dependencies live where
they're used).

## Implementation Flow (input to /speckit-tasks)

1. **The package** (FR-002..004, R1–R4): scaffold `packages/protocol`; zod
   pinned at current stable; schemas for the derived vocabulary with inferred
   types; close-code + error-code registries; accept/reject test suite; gate
   green; additive-only check.
2. **Manifest flip** (FR-008, R6): 1.3 published+translated, placeholders
   settled; build green.
3. **English chapter** (FR-001..005, 007, R5): the beats; fences byte-match
   the package files; three figures; verbatim quotes from SAD §5.1/§5.2 and
   the EIR-WS rows; every non-document frame name introduced with its
   "recorded decision" marker.
4. **Vietnamese chapter** (FR-009, R7): settled register, byte-identical
   fences, naturalization self-review.
5. **Verify** ([quickstart.md](./quickstart.md)): gate + new suite, three-
   chapter fence battery, battery v3 (16 rows, 14 prior unchanged), nav
   battery incl. sitemap 30 and the suggestions-allowlist admission POST, ID
   detector incl. frame-name discipline, vi parity.
6. **Handoff**: no commits — per-repo report incl. Dong's
   commit + `git tag part1-ch3` + push sequence.

## Complexity Tracking

> No constitution violations — table intentionally empty.

## Notes

- The vocabulary derivation table in research R2 is the chapter's factual
  backbone — every frame/type/code row cites its source or says "decision";
  implementation must keep that table and the chapter in lockstep.
- Zod's major version at install time is whatever current stable is — pin it,
  show the pin in the fence, and repeat 1.1's tag-is-truth caveat.
- The suggestions-allowlist admission check (quickstart) needs the local
  verification database from 015 or a `.env` URL — if neither is present at
  implementation time, validate the allowlist function directly (unit-level)
  and flag the live POST for Dong.
- Commits/pushes/tags remain Dong's; vi read-through before the milestone
  commit.
