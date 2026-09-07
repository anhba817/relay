# Implementation Plan: Part 3, reorganised by subject

**Branch**: `045-part-3-rework` | **Date**: 2026-09-07 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/045-part-3-rework/spec.md`

## Summary

Twenty-four chapters regrouped into eight contiguous subject movements, renumbered, with every
chapter reference in platform source rewritten to name its subject instead of its ordinal. English
prose moves unchanged; Vietnamese pages keep their fences and lose their prose to a placeholder.

**Research overturned the specification's central assumption, and the plan is shaped around the
correction.** The specification said 39 of 207 fenced paths change chain order and implied their diff
hunks could be regenerated. They cannot: replaying the existing per-chapter deltas in the new order
succeeds on **3 of 39**, conflicts on 31, and on 5 more merges cleanly onto **a different file** —
the dangerous outcome, because it passes every check until the final comparison. The fences on those
paths are not re-hunked. They are **re-derived**, and there are 278 of them.

**Four measurements decided the design:**

- **No order is cheaper.** Four candidate orders were replayed against the real chain. The conflict
  rate is 79–86% for all of them, including one built solely to minimise movement. The order is
  therefore chosen on pedagogy, since choosing it on cost is choosing between 24 conflicts and 31.
- **The platform cannot be reorganised to make the chain mechanical.** `repository.ts` holds **124
  interleaved cluster runs across 7 clusters** in 5,533 lines, `session.ts` 85 runs, and
  `app.module.ts` 21 runs in 71 lines. Making each cluster contiguous means refactoring the
  platform's largest file for the book's convenience.
- **Each chapter's state can be synthesised from the final file**, by attributing every line to the
  chapter that introduced it and removing what later clusters own. The chain lands on the final file
  by construction rather than by luck.
- **6% of the 1,429 source references need a person.** 29% sit beside a requirement id and lose only
  the ordinal; 64% take a name from a 24-entry table.

**One thing the specification got wrong and this plan amends**: it counted 985 source references. The
real number is **1,429** — a narrower pattern missed `3.20's` without the word "chapter". Recorded
here rather than corrected silently.

## Technical Context

**Language/Version**: MDX for chapters, TypeScript 5.x for the platform being fenced, Node.js 22.
Python 3 for this feature's instruments.

**Primary Dependencies**: `check-fence-chain.mjs`, which is both the gate and — copied and truncated —
the generator. `next.config.ts` for redirects, currently configuring none.

**Storage**: none. This feature changes no schema, no migration, no runtime behaviour.

**Testing**: the fence chain is the test. `check:fences` replays 240 fenced files across 41 chapters
and fails byte-exact. The platform's own suites are the control: **they must not change**, and the
battery's duration is a tripwire on that.

**Target Platform**: unchanged.

**Project Type**: three repositories — records at the root, code in `relay-platform`, the published
book and the gates in `relay-tutorial`.

**Performance Goals**: SC-007 keeps the battery within 10% of 225.45 s, the mean over twenty runs at
feature 044's close-out. This is not a performance target. **The platform is not supposed to change,
so a moved duration means something changed that should not have.**

**Constraints**: the final state of every platform file is fixed except where a comment is rewritten.
Vietnamese pages must keep fence lists and bodies byte-identical to English, because the mirror check
compares them and skips only chapters that do not exist.

**Scale/Scope**: **169 fenced files, 278 fences, 1,429 source references, 48 directory renames, 48
canonical URLs.** Feature 043 estimated 17 files and changed 58; feature 044 estimated 12, then 15,
then 17, and closed at 17 with five more found at the gate. **This estimate counts the fix and not
what the fix drags with it**, and the largest unknown is how many of the 278 re-derived fences carry
prose that walks through a diff that no longer looks the same.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Bearing on this feature | Verdict |
|---|---|---|
| **I. Tenant isolation** | No route, no query, no credential changes. The isolation gauntlet moves position and keeps its derived target list, which extends itself from the running router. | **Pass.** |
| **II. No acknowledged message is lost** | Nothing on any delivery path changes. | **Pass.** |
| **III. Two data paths, never crossed** | Untouched. | **Pass.** |
| **IV. Single writer, single source of truth** | The chapter mapping becomes a single source with two consumers — the published mapping page and the redirect table — rather than a hand-maintained pair. | **Pass, and the feature applies the principle to itself.** |
| **V. API-first, developer-first** | The whole feature is this principle applied to the documentation a developer reads. | **Pass, and it advances it.** |
| **VI. Requirement-driven, test-verified** | The fence chain verifies every claim about code. It cannot verify that prose still matches the diff beneath it, and this plan says so rather than implying coverage it does not have. | **Pass, with a stated limit.** |
| **VII. Boring by design — scope is a commitment** | This is a large change with no functional gain, which is exactly what this principle guards against. Compression is excluded, the platform's behaviour is unchanged, and Parts 0, 1, 2 and 4 are untouched. | **Pass, and the exclusions are the argument.** |

**Two clauses bear directly.**

- **Governance**: *"where it conflicts with the SRS or SAD, the conflict MUST be resolved explicitly
  by amendment rather than ignored."* No SRS clause conflicts. The specification's own reference count
  does, and is amended in the Summary above rather than quietly corrected.
- **Technology constraints**: no new language, no new dependency. This feature's instruments are
  Python, as every prior feature's have been.

**No violations. Complexity Tracking is empty.**

## Phases

**Phase 1 — Setup, and proving the instrument on today's chain.**
Build the attribution and synthesis tools, then point them at the **current** order and require a
byte-exact reproduction of today's chain. A generator that cannot rebuild what exists cannot be
trusted to build what does not. This is the control, and it comes before anything moves.

**Phase 2 — Foundational: the three tables.**
The 24-entry subject-name table, the old-to-new chapter map, and the reference classification.
Blocking: every later phase consumes one. The map is one file with two consumers, the published page
and the redirects.

**Phase 3 — User Story 3: the references, before anything moves.**
Rewrite all 1,429 source references and regenerate the fences carrying them. **US3 is P2 and runs
first on purpose**: once no comment names an ordinal, moving a chapter cannot invalidate one, and the
two large changes stay separately verifiable.

**Phase 4 — User Story 1: the reorder. This is the MVP.**
Rename, renumber, split the milestone chapter, synthesise the 39 affected chains and regenerate 278
fences. The defect is closed at the end of this phase.

**Phase 5 — User Story 2: proving nothing is taught before its subject exists.**
Mostly verification of Phase 4's arrangement, and said plainly rather than padded: FR-002 is satisfied
by the order, not by work done here. What this phase adds is a proof that can fail — every synthesised
state is typechecked, and a state that will not compile is a finding about the order.

**Phase 6 — The Vietnamese placeholders.**
Prose replaced, fences copied byte-identical, mirror green at 24 chapters.

**Phase 7 — The published surfaces.**
`docs/07-tutorial-plan.md`, the mapping page, the 48 redirects, and the references into Part 3 from
the parts that do not move.

**Phase 8 — Polish and close-out.**
Gates, battery, the ledger, `CLAUDE.md`.

## Project Structure

### Documentation (this feature)

```text
specs/045-part-3-rework/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
├── checklists/
│   └── requirements.md  # written by /speckit-specify
└── tasks.md             # /speckit-tasks output — NOT created here
```

### Source (three repositories)

```text
relay-tutorial/
├── app/(en)/part-3/chapter-NN/<slug>/page.mdx     24 directories renamed, prose moved
├── app/(vi)/vi/part-3/chapter-NN/<slug>/page.mdx  24 renamed, prose replaced, fences kept
├── fences/post-series.md                          amendments for every re-derived path
├── next.config.ts                                 redirects, from the mapping
└── scripts/check-fence-chain.mjs                  unchanged; copied and truncated as the generator

relay-platform/
└── services, packages                             1,429 comment references rewritten,
                                                   166 fenced files, 49 unfenced

docs/07-tutorial-plan.md                           Part 3's rows, in the new order
```

**169 fenced files, and the count will be wrong.** It is the union of 166 files whose comments change
and 39 whose chain order changes. It excludes the thirteen excerpt-only files, which no gate compares
to anything and which therefore need checking by another means.

## Complexity Tracking

Empty. No principle is violated and no deviation is proposed.
