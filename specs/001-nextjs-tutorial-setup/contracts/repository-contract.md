# Contract: relay-tutorial Repository Interface

**Feature**: `specs/001-nextjs-tutorial-setup` · **Date**: 2026-07-29

The feature exposes no APIs. Its external interface is the repository itself — what a
developer (or CI) may rely on. Breaking any item below is a breaking change to the
tutorial series.

## C1 — Commands (from `relay-tutorial/`, documented in README)

| Command | Guarantee |
|---|---|
| `pnpm install` | Installs all dependencies from the committed lockfile, no prompts |
| `pnpm dev` | Starts the dev server; home page renders themed, zero startup errors (FR-006) |
| `pnpm build` | Production build completes with exit code 0 |
| `pnpm lint` | Lint passes on the delivered state |

## C2 — Consumption via parent repo

| Step | Guarantee |
|---|---|
| `git clone git@github.com:anhba817/relay.git` | `relay-tutorial/` exists (empty until init) |
| `git submodule update --init` | Populates `relay-tutorial/` at the exact pinned SHA (SC-004) |
| README (both repos' docs path) | States the initialization step explicitly (edge case: uninitialized clone) |

## C3 — File presence contract (stable paths)

| Path | Contract |
|---|---|
| `package.json` | `dependencies.next` = exact latest-at-creation version (16.2.12) |
| `app/globals.css` | Contains Violet Bloom `:root` (light) and `.dark` variable blocks |
| `components.json` | Valid shadcn CLI config; future `shadcn add <component>` inherits the theme with zero extra styling (acceptance 3.3) |
| `README.md` | Purpose, relationship to `relay`, install/run, submodule init |

## C4 — Visual contract

| Surface | Contract |
|---|---|
| Home page, light mode | Violet Bloom light palette (violet primary, `oklch` tokens), Plus Jakarta Sans body font |
| Home page, dark mode (system preference or `.dark` class) | Violet Bloom dark palette; no unthemed flashes of default styling |
| Any shadcn component added later | Fully themed via CSS variables with no per-component styling work |
