# Data Model: Next.js Tutorial Repository Setup

**Feature**: `specs/001-nextjs-tutorial-setup` · **Date**: 2026-07-29

This feature has no application data layer (no database, no runtime entities). The
"entities" are configuration artifacts whose fields and invariants the implementation
and validation depend on.

## E1 — Tutorial Repository (`relay-tutorial`)

| Field | Value / Rule | Source |
|---|---|---|
| Name | `relay-tutorial` | FR-001 |
| Owner / hosting | `anhba817` on GitHub, public | FR-001, research R6 |
| Remote URL | `git@github.com:anhba817/relay-tutorial.git` | research R6/R7 |
| History | Independent; first commit is pure CLI scaffold output | FR-001, FR-003 |
| Framework version | `next@16.2.12` in `package.json` (exact, pinned) | FR-002, research R1 |
| Package manager | pnpm (lockfile: `pnpm-lock.yaml`) | research R3 |

**Invariant**: after the scaffold commit, only the R8-enumerated files may change.

## E2 — Submodule Link (in parent repo `relay`)

| Field | Value / Rule | Source |
|---|---|---|
| Path | `relay-tutorial/` at repo root | FR-004 |
| Config | `.gitmodules` entry: path + SSH URL | FR-004 |
| Pin | Gitlink records exact commit SHA of the tutorial repo | FR-004, SC-004 |

**State transitions**: uninitialized (empty dir after plain clone) → initialized
(`git submodule update --init` populates at pinned SHA). Both states are documented
(edge case: uninitialized clone).

## E3 — Theme Token Set (Violet Bloom)

| Field | Value / Rule | Source |
|---|---|---|
| Provenance | `https://tweakcn.com/r/themes/violet-bloom.json` (shadcn registry item, verified live) | research R4 |
| Variable groups | `theme` (fonts, radius, tracking), `light`, `dark` — all three merged into `app/globals.css` | FR-005 |
| Fonts | sans: Plus Jakarta Sans · serif: Lora · mono: IBM Plex Mono, loaded via `next/font/google` | research R4 |
| Mode switching | `.dark` class via next-themes, `defaultTheme="system"` | research R5 |

**Invariant**: no page may render framework-default colors (SC-002); every visible
surface consumes these variables directly or through shadcn components.
