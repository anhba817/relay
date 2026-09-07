# Implementation Plan: Part 3, reorganised by subject

**Branch**: `045-part-3-rework` | **Date**: 2026-09-07 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/045-part-3-rework/spec.md`

## Summary

Twenty-four chapters regrouped into eight contiguous subject movements and renumbered to **25** —
one splits — with every chapter reference in platform source rewritten to name its subject instead
of its ordinal. English
prose moves unchanged; Vietnamese pages keep their fences and lose their prose to a placeholder.

**Research overturned the specification's central assumption, and the plan is shaped around the
correction.** The specification said 39 of 207 fenced paths change chain order and implied their diff
hunks could be regenerated. They cannot: replaying the existing per-chapter deltas in the new order
succeeds on **3 of 39**, conflicts on 31, and on 5 more merges cleanly onto **a different file** —
the dangerous outcome, because it passes every check until the final comparison. The fences on those
paths are not re-hunked. They are **re-derived**.

**The count is 42 paths and 289 fences, not the 39 and 278 this plan first carried.** That estimate
assumed the milestone chapter moved as a unit; the design splits it, and the answer depends on where
its fences land — 39/278 if early, 44/300 if late. Analysis measured both bounds, the split was then
decided fence by fence in `contracts/chapter-map.md` at the chapter's own `## The outsider` heading,
and the number was re-measured. **A scope estimate that turns on an undecided design question is not
an estimate**, and this one was the headline.

**Four measurements decided the design:**

- **No order is cheaper.** Four candidate orders were replayed against the real chain. The conflict
  rate is 79–86% for all of them, including one built solely to minimise movement. The order is
  therefore chosen on pedagogy, since choosing it on cost is choosing between 24 conflicts and 31.
- **The platform cannot be reorganised to make the chain mechanical.** `repository.ts` holds **124
  interleaved cluster runs across 7 clusters** in 5,533 lines, `session.ts` 85 runs, and
  `app.module.ts` 21 runs in 71 lines. Making each cluster contiguous means refactoring the
  platform's largest file for the book's convenience.
- **Each chapter's state comes from a three-way merge of the existing deltas, not from filtering the
  final file.** The first design attributed every line to a chapter and dropped what later clusters
  owned; analysis pass 2 built it and it produced files that **do not parse** — 52 errors on
  `repository.ts`, 59 on `session.ts`. Cherry-picking the deltas onto the new order gives states that
  are real files: **56 intermediate states measured, 0 parse failures.** The cost is 31 conflicts to
  resolve by hand.
- **6% of the 1,429 source references need a person.** 29% sit beside a requirement id and lose only
  the ordinal; 64% take a name from a 24-entry table.

**One thing the specification got wrong and this plan amends**: it counted 985 source references. The
real number is **1,429** — a narrower pattern missed `3.20's` without the word "chapter". Recorded
here rather than corrected silently.

## Technical Context

**Language/Version**: MDX for chapters, TypeScript 5.x for the platform being fenced, Node.js 22.
Python 3 for this feature's instruments.

**Primary Dependencies**: `check-fence-chain.mjs`, which is both the gate and — copied and truncated —
the generator. **`fences/post-series.md`, which is part of the chain and which the first tooling
forgot**: it applies after the last chapter, amends 49 paths, and its omission showed as 70 lines
present in the platform file and in no snapshot. `next.config.ts` for redirects, currently
configuring none.

**Storage**: none. This feature changes no schema, no migration, no runtime behaviour.

**Testing**: the fence chain is the test. `check:fences` replays 240 fenced files across **42**
chapters after the split — 41 today — and fails byte-exact. The platform's own suites are the control: **they must not change**, and the
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

**Scale/Scope**: **184 fenced files, 289 fences across 42 re-derived paths, 1,429 source references
(1,298 of them inside 183 fenced paths), 48 existing appendix hunks to re-verify, 50 directory
renames, 50 canonical URLs, 48 redirects**, plus an 810-line chapter registry no requirement named
until analysis went looking for what else knows a chapter number.

**Every one of those numbers has moved at least once**, and two moved because a correction was
applied to one figure and not its neighbour: the reference count went 985 → 1,429 when the pattern
gained a capital `C`, and the file count stayed at 166 until pass 3 applied the same fix — 183. Feature 043 estimated 17 files and changed 58; feature 044 estimated 12, then 15,
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
| **IV. Single writer, single source of truth** | The chapter mapping becomes a single source with **three** consumers — the published page, the redirects, and the chapter registry the sitemap and six components read. Analysis found the third; the plan had said two. | **Pass, and the feature applies the principle to itself — after failing to apply it to its own consumer list.** |
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
Build the replay-and-merge pipeline, then point it at the **current** order and require a byte-exact
reproduction of today's chain. A generator that cannot rebuild what exists cannot be trusted to build
what does not. This is the control, and it comes before anything moves.

**It has already earned its place.** The first mechanism this plan specified — filtering the final
file by line attribution — reproduced **17 of 96** states under exactly this control, and produced
unparseable files besides. The control fired in analysis rather than in implementation only because
somebody built the tool early; the plan is written so that it fires either way.

**Phase 2 — Foundational: the three tables.**
The 24-entry subject-name table, the old-to-new chapter map, and the reference classification.
Blocking: every later phase consumes one. The map is one file with **three** consumers — the
published page, the redirects, and the chapter registry — and this phase also builds the checker that
compares that registry against the filesystem in both directions, because nothing does today.

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
├── app/(en)/part-3/chapter-NN/<slug>/page.mdx     25 directories, 24 renamed and 1 new
├── lib/tutorial.ts                                the chapter registry — 810 lines, hand-kept,
│                                                  read by the sitemap and six components
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
