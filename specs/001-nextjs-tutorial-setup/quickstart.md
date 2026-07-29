# Quickstart Validation: Next.js Tutorial Repository Setup

**Feature**: `specs/001-nextjs-tutorial-setup` · **Date**: 2026-07-29

Runnable scenarios proving the feature works end-to-end. Contracts referenced from
[contracts/repository-contract.md](./contracts/repository-contract.md); configuration
facts from [data-model.md](./data-model.md).

## Prerequisites

- Node.js 22+, pnpm 10+, git with SSH access to GitHub as `anhba817`
- A browser (for the visual light/dark checks)

## V1 — Fresh consumer path (validates SC-001, SC-004, User Story 2)

```bash
git clone git@github.com:anhba817/relay.git /tmp/relay-validate
cd /tmp/relay-validate
git submodule update --init
cd relay-tutorial
pnpm install
pnpm dev
```

**Expected**: total elapsed time under 5 minutes; `relay-tutorial/` populated at the
SHA recorded by the parent (`git -C .. submodule status` shows no `+` prefix, i.e. the
checked-out commit matches the pin); dev server starts and http://localhost:3000
renders without errors.

## V2 — Version pin (validates SC-003, FR-002)

```bash
cd relay-tutorial
node -p "require('./package.json').dependencies.next"
```

**Expected**: `16.2.12` (latest stable on the creation date, research R1).

## V3 — Theme, light and dark (validates SC-002, FR-005, User Story 3)

With `pnpm dev` running:

1. Open http://localhost:3000 with OS/browser in **light** appearance.
   **Expected**: Violet Bloom light palette (violet primary, warm near-white
   background), Plus Jakarta Sans typography — not the scaffold's default styling.
2. Switch the OS/browser to **dark** appearance and reload.
   **Expected**: Violet Bloom dark palette (deep indigo-tinted background per the
   `.dark` variables), all text legible, no unthemed elements.
3. Inspect `app/globals.css`.
   **Expected**: `:root` and `.dark` blocks containing the Violet Bloom `oklch`
   variables (contract C3).

## V4 — Scaffold integrity and build gate (validates FR-003, FR-006, contract C1)

```bash
cd relay-tutorial
git log --oneline            # expect: scaffold commit first, then theme, then docs
pnpm lint && pnpm build
```

**Expected**: first commit contains only CLI output; lint and build both exit 0.

## V5 — Documentation completeness (validates FR-007, User Story 2 scenario 3)

Open `relay-tutorial/README.md`.

**Expected**: states the repo's purpose (application for the *Building Relay* tutorial
series), its relationship to `relay` (submodule of), install/run commands matching
contract C1, and the `git submodule update --init` step for consumers arriving via the
parent repo.

## Cleanup

```bash
rm -rf /tmp/relay-validate
```
