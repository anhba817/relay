# Quickstart Validation: Tutorial Chapter 0.1

**Feature**: `specs/002-tutorial-chapter-01` · **Date**: 2026-07-29

Contracts in [contracts/tutorial-site-contract.md](./contracts/tutorial-site-contract.md);
structure in [data-model.md](./data-model.md). All commands run in `relay-tutorial/`.

## Prerequisites

- Node.js 22+, pnpm 10+, the relay-tutorial working tree at this feature's revision
- A browser for the visual and navigation checks

## V1 — Build gate and navigation (SC-005, FR-007, US3)

```bash
pnpm install && pnpm lint && pnpm build && pnpm dev
```

1. Open http://localhost:3000 — **Expected**: series landing with the *Building Relay*
   title, the nine-part outline, Part 0 expanded showing chapters 0.1–0.5; 0.1 is a
   link, 0.2–0.5 are marked forthcoming and are not links.
2. Click chapter 0.1 — **Expected**: chapter page loads (2 steps total from entry).
3. At the chapter's end — **Expected**: footer shows "0.2 — Four people who will judge
   us" as forthcoming (non-link with badge) and a back-to-contents affordance.

## V2 — Format compliance, scripted (SC-001, SC-004, contract C5)

```bash
F=app/part-0/chapter-01/from-app-to-infrastructure/page.mdx
# word count of prose (strip imports/exports/JSX tags approximately)
grep -vE '^(import|export)' $F | sed 's/<[^>]*>//g' | wc -w        # expect 2000–4000
grep -c '<Why' $F                                                   # expect >= 2
grep -c '<Checkpoint' $F                                            # expect exactly 1
grep -c '<ForwardRef' $F                                            # expect >= 1
grep -ci 'takeaway' $F                                              # expect >= 1
```

## V3 — Content traceability spot-check (SC-002, FR-002)

Pick any 5 factual product claims in the chapter (market positioning, the
underestimation pairs, alternative products named, non-goal reasons).
**Expected**: each traces to a specific section of `docs/01-product-vision.md`; the
chapter *derives* (shows reasoning steps) rather than pastes conclusions.

## V4 — Exercise completeness (FR-003, US2)

Inspect the exercise section.
**Expected**: for/who/that/unlike positioning template present; Relay's own statement
shown as the worked example; non-goals exercise demands ≥ 3 entries each with a
reason; self-check criteria answerable yes/no; final `<Checkpoint>` names both
artifacts as required before chapter 0.2.

## V5 — Both-mode rendering (SC-006, FR-008)

With `pnpm dev` running, view the chapter in light then dark appearance.
**Expected**: prose, headings, code, links, and every box type used by the chapter
(`WHY`, `SKIP AHEAD`, `FORWARD REF`, `CHECKPOINT` at minimum) are visually distinct
from body text in both modes, using theme colors (violet primary family) with no
unthemed or hardcoded-color elements.

For the box types chapter 0.1 does not use (`TRAP`, `REVISED`): temporarily render
all six boxes on a scratch route (e.g. `app/box-preview/page.mdx`), verify both modes,
then delete the route before finishing — they ship contracted (C4) and must not ship
unseen.

## V6 — Reader dry run (SC-003 proxy)

Follow only the chapter: read, then do the exercise.
**Expected**: both artifacts producible without consulting docs/01 directly; elapsed
exercise time under 45 minutes.
