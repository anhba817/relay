# Implementation Plan: repair the fence chain — 110 to 0

**Feature directory**: `specs/055-fence-chain-repair` | **Date**: 2026-09-17
**Spec**: [spec.md](./spec.md) · **Research**: [research.md](./research.md) — **read it first,
two of the specification's own assumptions are corrected there**

## Summary

`pnpm check:fences` has reported 110 problems since feature 045, and `ci.yml`'s tutorial job ends
with that command, so the workflow has been red on every push for nine chapters. Feature 054
costed five ways out; this is the one chosen — repair the chain, change nothing about what the
checker accepts.

The measured shape is smaller than the number. **110 problems are 47 targets**, the
Vietnamese chain contributes **no defects of its own**, and **one file is 16 of the 110 with one
hunk explaining nine of them.** Four classes, repaired in a forced order: 11 fences that name no
file, 32 missing introductions over 9 files, 42 broken hunks over 12 files, 25 divergences whose
repair is an appended hunk rather than a regenerated one.

**Two things in the specification are wrong and research corrects them.** `fences/post-series.md`
cannot host a missing introduction — it applies after every chapter, so it can never supply a
predecessor state (R2). And an introduction must show the file **as it stood at the chapter that
publishes it**, which cuts the listing cost from 3,956 lines to **1,658 or 1,956 depending on
which of two designs each file takes** (R2) — and getting that tag wrong fails on contact, which
analysis measured rather than predicted.

## Technical Context

**Language / runtime**: none new. The repair edits MDX chapters and one Node script.
**The instrument**: `relay-tutorial/scripts/check-fence-chain.mjs`, unchanged in what it accepts.
It gains `--dump <dir> [--at <page>]` so hunks are generated from the same replay that checks
them (R8) — an interface addition, not a loosening, and the plan says so out loud because the
distinction is the whole feature.
**And it needs both modes, which analysis measured rather than assumed.** `turbo.json` replays to
**62 lines at chapter 3.22** and **74 after the appendix**: a final-state dump serves the 14
appendix hunks and the 25 divergences, and **cannot serve the 28 chapter hunks**, which are two
thirds of phase 3's work here.
**Neither mode takes a locale, and the reasons differ.** `--at` is given a page path that begins
`app/(en)/` or `app/(vi)/vi/`, so the chain is inside the argument. The final-state mode has no
argument and writes the **English** chain, because all 39 of its consumers are English — the HEAD
comparison iterates `en.state` and `fences/post-series.md` is one file for both locales. It prints
which chain it wrote, because the two ends are 9 paths and 13 lines of `turbo.json` apart.
**Historical content**: the 27 `rework/part3-chN` tags in `relay-platform`, which resolve. The
deleted `part3-chN` tags are not needed.
**Scale**: 47 targets · **42 hunks regenerated and 25 appended** · **9 whole bodies, 1,658 or
1,956 lines depending on which tag each takes** · 2,381 differing lines · edits in `app/(en)`,
`app/(vi)` and `fences/post-series.md`.
**What is NOT in scope**: the 360 untitled fences (043-1, re-measured), the checker's exit semantics, any
platform file, and chapter renumbering.

## Constitution Check

Read the clauses, not the identifiers. Each row says what was opened.

| principle | verdict | what was read, and why |
|---|---|---|
| **I — tenant isolation** | **NOT ENGAGED** | No code path, no data access, no endpoint. The feature edits prose and fences. |
| **II — no acknowledged message is lost** | **NOT ENGAGED** | No write path. |
| **III — two data paths** | **NOT ENGAGED** | No query, no store. |
| **IV — single writer** | **NOT ENGAGED** | Nothing writes to PostgreSQL. |
| **V — API-first** | **NOT ENGAGED** | No surface. |
| **VI — requirement-driven, test-verified** | **PASS, AND ONE CLAUSE IS THE FEATURE** | *"The quickstart MUST run unmodified, verified by automated execution in CI."* A workflow that has been red for nine chapters verifies nothing by its result, which is what this feature repairs. The coverage clauses are untouched: no platform file changes, so no pinned file moves. |
| **VII — boring by design** | **PASS, WITH ONE ADR OWED** | No new service, language or dependency. **The `--dump` flag is a change to a shared instrument** and the 11 `(excerpt)` declarations set a precedent for what a title means, so VII's *"every architecture decision is recorded as an ADR stating its drivers, rejected alternatives, and reversal condition"* applies to both. One ADR, not two — they are the same decision about what the fence chain claims. |

### The clause this feature is inside

`docs/07` §6's third defense — ***"One direction of authority. The repo at tag N is the truth;
prose describes it"*** — is what makes every repair an edit to a chapter and never to
`relay-platform`. It is stated as FR-009 and measured as SC-010 rather than left as a convention,
because the cheapest repair for 25 of the 110 would be to edit the platform, and it would be
wrong.

## Phases

### Phase 1 — The inventory, re-measured, and the instrument

Re-measure all 110 rather than reading them out of `spec.md` (FR-013): the four classes, the 47
targets, the en/vi mirror, the per-file concentration. Record the divergence between what is
measured and what this specification says, because the chain moves whenever a chapter or the
platform does.

Build both dump modes into the checker and prove they agree with the checker's own replay —
dump, re-apply, compare, **and apply a hunk that works today against the state `--at` reports for
its own chapter.** Determinism is not correctness: a dump that is consistently wrong passes a
dump-twice check. **An instrument that replays differently from the checker produces hunks the
checker rejects for reasons neither of them explains**, and this feature runs it about fifty
times.

Resolve or record the **109 → 110** discrepancy (R6, FR-014).

### Phase 2 — The eleven that name no file 🎯 first, because they are free

Declare each of the 11 `text` fences with `(excerpt)`, in `app/(en)` and its `app/(vi)` twin —
**22 fences**, which is also what the declared-`(excerpt)` population moves by. Expected:
**110 → 99**, `MIRROR` still 0.

**The control is sound and that was measured rather than assumed**: each of the eleven titles
occurs exactly twice, once per locale, all `lang=text`, none repeated inside a chapter and none
in the appendix — so no later fence loses a predecessor when one is declared.

**And the pair has to land together.** `MIRROR` compares a joined title list per chapter and
`continue`s on a mismatch, so a half-applied declaration reports **one** problem and leaves that
chapter's fences uncompared — 40 of them in the largest of the six chapters involved. The total
stays at 110 through it, because a HEAD problem leaves as the MIRROR one arrives.

**This phase is the measurement loop's own positive control.** It is the only class with no
cascade risk, so if the count does not move by exactly 11, the instrument is wrong before
anything expensive has been attempted.

### Phase 3 — The twelve files with broken hunks

First failing hunk per file, regenerated from the dumped chain state, re-measured after each
file. `vitest.coverage.config.mts` first: 15 of the 42, and nine of them are shadows of one.

**Expect the count to move in both directions.** Repairing a hunk changes the state every later
hunk for that file anchors on, and feature 045 measured one regeneration taking the chain from
111 to 203. The per-file measurement is what makes that recoverable instead of a surprise at the
end.

**And this phase publishes prose risk, which the plan had assigned to phase 4 alone.** A
regenerated hunk is `diff(chain state, repo at tag)` and absorbs whatever divergence the chain was
carrying, so it can be larger than the hunk it replaces and show the reader lines the chapter
never discusses. SC-007 is read in three phases, not one — here, in the introductions, and in
whatever phase 5 appends inside a chapter rather than the appendix.

### Phase 4 — The nine files the chain never sees whole

Per file, decide between research's two designs — replace the first `diff` with a whole body at
that chapter, or add the body to an earlier chapter that introduces the file — and take the
content from `rework/part3-chN`, not from the working tree.

**This is the phase that can make a chapter worse.** 1,956 lines of listing land in published
chapters, and a chapter that shows a reader a file it never discusses has been repaired in the
checker's terms and damaged in the reader's. Where no honest home exists, the file's fences become
excerpts **and** the exception is recorded with what it costs (FR-012). Both halves: the
excerpt is what removes the problem from the count, the record is what stops it being an
exemption nobody looked at. Recording alone leaves FR-001 unreachable, because nothing reads
`gaps.md`.

### Phase 5 — The twenty-five divergences

An appended hunk per file, in `fences/post-series.md` unless a chapter genuinely discusses the
change. Never a regenerated early fence: `codes.ts` is fenced by 12 chapters, `app.module.ts` by
11, `vitest.coverage.config.mts` by 11 plus 9 appendix hunks.

Two files are 59% of the differing lines and both are measured against a chain state that phase 3
will have changed, so their real size is not yet known.

**Appendix hunks carry no prose obligation and chapter hunks do**, so the split between the two
homes is recorded: the appendix exists precisely so that a change no chapter teaches is not put in
front of a reader, and the number that goes into a chapter is the only part of this phase SC-007
has to read.

### Phase 6 — Zero, and the things zero does not mean

Confirm 0 and exit 0. Plant a regression — one line in a fenced platform file, no chapter hunk —
and confirm the run goes red and names the file (SC-003). Run the tutorial job's other gates.
Record what was repaired, what was declared, and what was recorded as unrepairable with its cost.

**And record what zero is not.** It is not a claim that the chapters are readable, that the
listings are pedagogically right, or that the 360 untitled fences mean anything. It is one
property: every titled fence replays onto the repository.

**And zero is not the exit code.** `scripts/check-fence-chain.sh` exits 0 when `relay-platform`
is absent, having replayed nothing, so the evidence is the success line — `N fenced files replay
onto relay-platform across M chapters` — which the checker prints only when the count is 0.

### Phase 7 — The record

ADR-29 for the one decision this feature makes about what a fence claims: the `--dump` flag and
the `(excerpt)` declarations, with the rejected alternatives and a reversal condition.
Constitution VII requires it and the Constitution Check above already flags it as owed — **this
phase exists because analysis found the obligation named in two places and planned in neither.**

Then `gaps.md` with every carried item re-measured rather than copied, `traceability.md`, this
repository's `CLAUDE.md` block, and the push. Plus the arithmetic that says which of the 110 were
defects and which were shadows, so the next reader of a fence-chain number knows what it counts.

**The phase count here is seven and the task list's is eight**, because `tasks.md` splits phase 1
into the inventory and the instrument — they block different things, and the instrument blocks
three later phases while the inventory blocks everything.

## Complexity tracking

| decision | why it is not simpler | what it costs |
|---|---|---|
| **A `--dump` flag on the checker** | Fifty hunks regenerated against a throwaway copy is `check-lane-scope.py`'s shape — an instrument nobody reviews, pointed at the wrong thing for a year (049-3). **And measured: the same file run from another directory prints `relay-platform not found — skipping` and exits 0**, because the platform path comes from `import.meta.url`. A moved copy is silently a no-op, and rule 1a is the instruction to move one. | An interface change to a shared gate, and an ADR, because "I changed the checker" is the sentence this feature exists to not say. |
| **Declaring 11 fences `(excerpt)` rather than teaching the checker about `text`** | The one-line predicate change exempts a class without anybody reading its members. | Eleven titles × two locales, and somebody looks at each. |
| **Whole-body introductions from `rework/part3-chN`** | Today's content in a Part 3 chapter shows the reader future code and leaves later hunks anchored on the wrong bytes. | A dependency on tags that exist now and were deleted once before for a different namespace (046). |
| **Repairing the Vietnamese chain at all** | 30 of the 110 are there, and the count is the count. | Edits in files under active translation — fence bodies only, which `MIRROR` already requires to be byte-identical copies, so no translated prose moves. |
| **Per-file measurement rather than per-phase** | One regeneration took the chain from 111 to 203. | About 47 checker runs; each is seconds. |

## Files this feature is expected to touch

    relay-tutorial/scripts/check-fence-chain.mjs         the --dump flag, and nothing else
    relay-tutorial/app/(en)/part-3/**/page.mdx           11 titles · ~9 introductions · ~20 hunks
    relay-tutorial/app/(vi)/vi/part-3/**/page.mdx        the same, as byte-identical copies
    relay-tutorial/fences/post-series.md                 ~14 hunks repaired · ~25 appended
    docs/05-sad.md, docs/06-adr-deep-dives.md            ADR-29
    specs/055-fence-chain-repair/                        baseline.txt, gaps.md, traceability.md

**No file under `relay-platform/` appears here, and that is a requirement rather than an
observation** (FR-009, SC-010).

## Open questions for `/speckit-analyze`

1. Whether each of the nine never-introduced files has a chapter that would honestly introduce
   it, or whether some become excerpts. Nine judgements about published prose; research could not
   settle them by measurement.
2. Whether `--dump` belongs on the checker or in a second script that imports it. The checker is
   a top-level program with no exports, so the second option means refactoring it — more change
   for the same result, and the plan takes the flag.
3. Whether the two large divergences (`vitest.coverage.config.mts` 867 lines,
   `eslint.config.mjs` 540) are still large after phase 3 repairs their hunks. Both are measured
   against a chain state that is missing what those hunks would have added.
4. Whether reaching 0 should be followed by making 0 enforceable — the checker already exits
   non-zero above 0, so this is a question about whether anything guards the number between
   chapters, and it is adjacent to `gaps.md` 048-5 and 054-4.
