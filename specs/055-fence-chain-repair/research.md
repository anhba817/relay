# Research — feature 055, repair the fence chain

Every number here was measured on 2026-09-17 against the tree at `part4-ch9`. Where a decision
is recorded, the alternatives are the ones that were actually costed, not the ones that sound
plausible.

---

## R1 — The checker already has a way to say "this is not a file", and it is applied in both loops

**Decision**: the 11 prose-titled fences are declared as not-files using the existing mechanism.
No checker change.

`check-fence-chain.mjs:42`:

```js
/** Titles that name no real file — prose illustrations, not fences. */
const NOT_A_FILE = (title) =>
  title.includes("(excerpt)") || title.includes(".naive.");
```

It is called at `:160` inside `replay()` (every chapter) and again at `:211` for the appendix. So
a fence whose title carries `(excerpt)` is skipped everywhere, today, with no change to the
instrument.

**And all 11 are command output, which the language tag already says.** Every one is
` ```text `:

    the ladder against the registry        filter can emit : forbidden  internal_error …
    who builds a docs_url                  services/gateway/src/session.ts:47
    the typo, now                          probe.ts(2,32): error TS2345: …
    the derivation, reporting itself       gauntlet targets: 9 derived, 6 attacked, 3 exempt
    what the schema looks like from here   tenant paths: 11 tables — 3 direct, 2 hop, 6 spine
    the structural check, on the first …   these tables have no path to an environment: outbox
    the same error, from inside one pack…  duplicate key value violates unique constraint …
    the check, on the consumer's table     these tables have no path to an environment: …
    42P01                                  relation "consumed_events" does not exist
    run 11 of 20                           expected [ …(2756) ] to include '<uuid>'
    the build that added the module        gauntlet targets: 11 derived, 9 attacked… {

**Not one is a source listing.** Nothing is lost by declaring them, because nothing was ever
verifiable about them: a compiler error message is not a file the chain can replay onto.

**Alternatives considered.**

*Teach the checker that `lang=text` is never a file.* One predicate, and it fixes the class for
every future chapter. **Rejected**: it exempts a class without anybody reading its members, which
is what FR-002 forbids, and it would silently absorb a future `text` fence that genuinely should
have been checked. The eleven are declared one at a time by somebody who looked at each.

*Retitle each to the path it illustrates.* **Rejected**: a titled fence is a whole-body claim
(051-6), so `title="packages/protocol/src/codes.ts"` over four lines of compiler output is a
worse lie than the one being fixed.

*Remove the titles.* Works, and moves them into the 360 fences no gate reads — an
undeclared population rather than a declared one. `(excerpt)` says the same thing and says it
where a reader and the checker both see it.

**What this costs**: 11 title strings in `app/(en)`, and their `app/(vi)` twins, because `MIRROR`
matches fences by title and a renamed English title would leave its Vietnamese twin unpaired.

**AND THE CONVENTION IS ALREADY THE SERIES' OWN, 222 TIMES.** Measured across `app/(en)`,
`app/(vi)` and the appendix:

    2,109 opening fences · 1,749 titled · 360 with a language and no title
    222 titles already carry `(excerpt)`

So declaring these eleven is not inventing a mechanism, it is applying one the series uses in 222
places. **And `gaps.md` 043-1's figure is stale**: it recorded *"146 of 904 — 16%"* untitled; the
population is now 360 of 2,109, which is 17%. The ratio held while the absolute number more than
doubled, which is what a carried number does when nobody re-measures it — this feature's SC-008
is written against the measured figure, not 043-1's.

---

## R2 — The appendix cannot introduce a file, and that rules out the obvious home for 32 problems

**Decision**: every missing whole-body introduction goes in a chapter, at or before the first
amendment. `fences/post-series.md` is not available for this class.

`check-fence-chain.mjs` builds the chapter state first (`const en = replay("en", problems)`,
`:204`) and applies the appendix afterwards (`:207`). **The appendix is strictly last**, so it
cannot supply the predecessor state a chapter's `diff` needs. The spec's FR-010 offers the
appendix as a fallback for this class; **that fallback does not exist** and the plan carries the
correction.

**Nine files are amended without ever being shown, 32 problems across two locales.** Both
candidate sources are measured, because **which one is right depends on the design and the wrong
one fails on contact**:

    file                                            ch(N-1)   chN   today   first amended
    services/gateway/src/session.itest.ts              281    287    1626   3.3 (+4 more)
    services/api/src/fanout/fanout.itest.ts            558    559     561   3.17
    packages/test-harness/src/guard.itest.ts           333    427     442   3.23
    services/api/src/messages/history.itest.ts         102    150     150   3.11
    services/api/src/messages/idempotency.itest.ts     136    144     224   3.11
    services/api/src/outbox/event.test.ts               93    122     524   3.11 (+1)
    packages/protocol/src/internal.test.ts              49    114     253   3.20 (+1)
    packages/test-harness/src/driver-exempt.test.ts     92    104     127   3.11 (+1)
    services/dispatcher/vitest.integration.config      14     49      49   3.23
                                                     1,658  1,956   3,956

**Neither of the first two columns is "the" answer, and an earlier draft of this document named
only the middle one.** The rule is *the body is the file at the tag of the chapter that publishes
it*:

    replace chapter N's diff with a body at N   →  rework/part3-chN
    add a body at an earlier chapter M          →  rework/part3-chM   (usually N-1)

**Measured rather than reasoned about**: chapter 3.3's existing hunk for `session.itest.ts`
**applies to `rework/part3-ch2` and does not apply to `rework/part3-ch3`**, because ch3 already
contains what the hunk adds. Publishing ch3's 287 lines while keeping chapter 3.3's diff produces
`hunk pre-image matched 0 times` **after** the introduction has landed — which reads like the
defect the phase is repairing rather than the one it just caused.

Either way the last column is wrong: publishing today's 1,626-line `session.itest.ts` in chapter
3.3 would show a reader twenty chapters of future code.

**The historical content is reachable and the tag numbering is today's.** The `rework/part3-chN`
tags resolve — 27 of them — and the hunk test above is what confirms `chN` means chapter N under
Part 3's post-rework numbering, which is not something to assume in a series where twenty-one of
twenty-six numbers changed meaning. The deleted `part3-chN` tags (046) are not needed.

**Alternatives considered.**

*Replace the first `diff` with a whole body at that chapter.* The chapter shows the file as it
ends that chapter and the later hunks apply unchanged. Costs the chapter its focused listing —
the reader sees a whole test file where they saw a change.

*Add the whole body to an earlier chapter that introduces the file.* Keeps every existing diff
intact and needs a chapter that discusses the file's creation. Whether one exists is per-file and
is phase 1's work.

*Make the un-anchored diffs excerpts.* Nine files leave the chain entirely — 32 problems gone,
verification gone with them. **Rejected as a default**, available per file if no honest home
exists, and then recorded under FR-012 rather than counted as a repair.

---

## R3 — The 42 broken hunks are 12 files, and the concentration is one file

**Decision**: repair per file, first failure first, and regenerate every hunk from the checker's
own replay.

    vitest.coverage.config.mts    15     9 appendix · 3 en · 3 vi
    turbo.json                     6     3 en · 3 vi
    packages/protocol/src/codes.ts 4     2 en · 2 vi
    services/api/src/app.module.ts 4     2 en · 2 vi
    eslint.config.mjs              3     1 appendix · 1 en · 1 vi
    packages/e2e/src/harness.ts    2     1 en · 1 vi
    packages/test-harness/src/sentinel.sql  2
    services/api/src/webhooks/test-event.itest.ts  2
    services/api/package.json      1   ·  package.json 1  ·  credentials.itest.ts 1
    services/gateway/src/presence.itest.ts  1

**One file is 15 of the 42 and one hunk explains nine of them.** Feature 054 dumped the chain's
state for `vitest.coverage.config.mts` and found **no `env` block at all** — the appendix hunk
that would create it is itself failing, so the nine later hunks anchored inside that block have
nothing to attach to. Repairing the first repairs the rest by construction.

**The generator must be the checker.** Fence-chain rule 1a, and feature 054 paid for it twice in
one session: a hunk generated with `git diff` against the tree failed to apply, and the same hunk
regenerated against the dumped chain state was the only way to see why. A dumper built from a
truncated copy of `check-fence-chain.mjs` produced all 285 chain states in one run and is the
instrument this feature runs on.

---

## R4 — The 25 divergences are 2,381 lines, and 59% of them are two files

**Decision**: divergences are repaired by appending a hunk, never by regenerating an early fence.

    file                                        chain   tree   differing lines
    vitest.coverage.config.mts                    318   1182       867
    eslint.config.mjs                             206    451       540
    packages/protocol/src/codes.ts                279    429       157
    services/api/src/isolation/targets.ts         390    508       119
    services/api/src/auth/credential.guard.ts     104    179       102
    … 20 more, of which 11 differ by 20 lines or fewer …
                                                            total 2,381

`eslint.config.mjs` at 206 against 451 is `gaps.md` 047-1, which recorded *"a 243-line divergence
predating this chapter"* — measured here as 540 changed lines, because the divergence has grown.

**Appending is safe and regenerating is not.** Feature 045 measured a single foundation fence
regenerated to match the tree taking the chain from **111 problems to 203**, by unanchoring
ninety-two downstream hunks. Measured here, the files in question are chained deeply:

    packages/protocol/src/codes.ts       12 chapters fence it
    vitest.coverage.config.mts           11 chapters + 9 appendix hunks
    services/api/src/app.module.ts       11 chapters
    turbo.json                           10 chapters + 1 appendix hunk
    eslint.config.mjs                     8 chapters + 1 appendix hunk

So the repair for a divergence is a hunk **after the last existing fence** — which is what
`fences/post-series.md` is for, and what chapter 4.9 did for its own five files. That also
satisfies the spec's US3 without argument: the appendix is where changes no chapter owns go, so
no chapter acquires a listing it never discusses.

**Ordering follows from this**: a file's APPLY failures must be repaired before its HEAD
divergence can be, because the divergence is whatever is left after every hunk has applied. Fix
`vitest.coverage.config.mts`'s 15 hunks and its 867-line divergence may be a different number.

---

## R5 — The Vietnamese chain has no defects of its own

**Decision**: repair English first, then copy each repaired fence body into its Vietnamese twin.

Measured: **30 vi problems, 30 of which mirror an en problem exactly** — same chapter slug, same
line, same message — and **zero vi-only**. The `MIRROR` rule requires byte-identical fence bodies,
and there are 0 MIRROR failures today, so the vi fences are already exact copies.

This halves the diagnosis and doubles the edits. It also means **no translated prose is
touched**: the work is fence bodies, which are not translated and cannot be.

`gaps.md` 050-3 stays open and is the reason this holds: the vi chain is never compared to
`relay-platform`, only to its English twin. The 25 HEAD divergences are `(en)` only for the same
reason.

---

## R6 — The 109 that became 110, and the delta that hid it

**Recorded rather than resolved.** Feature 045 closed the rework reporting **109 problems, APPLY
74, HEAD 35** — `specs/045-part-3-rework/gaps.md:3327`, and the same three numbers in its
close-out. Feature 046's spec and quickstart were written against 109 (`spec.md:213`,
`quickstart.md:179`), and 046's own T062 measured **110, APPLY 74, HEAD 36** and reported it as
**"a delta of 0"** against its phase-1 opening.

Both statements are true. **One HEAD problem appeared between 045 closing and 046 measuring, and
the delta-of-0 convention is what kept it invisible** — 046 compared its close to its own
opening, which already contained the extra one. Every chapter since has compared to 110.

The mechanism is this project's own recorded lesson arriving from the other side: *a delta
between two totals is not a measurement of the thing that changed unless nothing else changed.*
The one extra problem is a `differs at line` in some file that moved in that window; naming it
needs the per-file lists from both moments, and only the totals were published.

**Implication for this feature**: the inventory is re-measured before any repair (FR-013), and the
number this feature reduces is the measured one rather than either published figure.

---

## R7 — What "repaired" cannot mean

Three shapes were considered and rejected as repairs, and each is available as a **recorded
exception** under FR-012 if a specific file has no honest alternative:

- **Editing a platform file so a chapter's fence becomes correct.** `docs/07` §6's third defense
  runs one way: *"the repo at tag N is the truth; prose describes it."* Forbidden by FR-009, and
  the spec makes it a success criterion (SC-010) so it is measured rather than assumed.
- **Deleting a fence to remove its problem.** A fence that names a real file and is deleted takes
  its verification with it, and the count improves. That is the baseline this feature refused,
  spelled differently.
- **Marking a real file's fence `(excerpt)`.** Same objection. `(excerpt)` is for listings that
  are not files, which is what R1 establishes about the 11.

---

## R8 — What the repair needs that does not exist yet

**Decision**: build the chain-state dumper as a checked-in script rather than a copy somebody
makes each time.

Feature 054 built it twice from a truncated copy of `check-fence-chain.mjs`, used it, and deleted
it — as fence-chain rule 1a instructs. This feature will regenerate on the order of 50 hunks and
re-dump after each repair, so the instrument is used continuously rather than once.

**What it must do**: replay exactly what `check-fence-chain.mjs` replays — same parser, same hunk
applier, same ordering including the appendix — and write the state of one or all files. A
generator that replays differently produces hunks the checker rejects for reasons neither
explains.

**The cheapest honest form is a flag on the checker itself** (`--dump <dir>`), because then there
is one replay implementation and no copy to drift. That is a change to the checker's *interface*
and not to what it accepts, which FR-002 permits — but the plan states it explicitly so it is not
mistaken for a loosening.

**AND ONE MODE IS NOT ENOUGH, WHICH THIS SECTION SAID UNTIL ANALYSIS PASS 3 WALKED A FILE.**
`turbo.json`'s replayed length, chapter by chapter:

    chapter 1.1 … 1.3   28 lines
    mid-Part 3          59
    chapter 3.22        62      ← the state its three failing hunks anchor on
    after the appendix  74      ← what a final-state dump writes
    the tree            75

A hunk generated against the final state carries twelve lines of context that do not exist at
chapter 3.22. So the flag takes `--at <page>` as well, writing the state **as that page is
reached, before its own fences apply**: the final-state mode serves the **14 appendix hunks** and
the **25 divergences**, and `--at` serves the **28 chapter hunks**. Regenerating a chapter hunk
pairs the two sources phase 4 already pairs — the pre-image from the chain, the post-image from
`rework/part3-chN`.

**AND NEITHER MODE NEEDS A LOCALE FLAG, FOR TWO DIFFERENT REASONS — ANALYSIS PASS 4.** The 110
split by class and locale:

    class                  en   vi  appendix   total
    hunk pre-image         14   14        14      42
    no earlier fence       16   16         0      32
    differs at line        25    0         0      25
    does not exist         11    0         0      11
    TOTAL                  66   30        14     110

`--at` takes a page path, and a page path begins with `app/(en)/` or `app/(vi)/vi/` — the locale
is inside the argument copied off the problem line, so a flag could only ever disagree with it.
The final-state mode has no such argument, and **all 39 of its consumers are English**: the HEAD
comparison iterates `en.state`, and `fences/post-series.md` is one file for both locales. So a
bare `--dump` writes the English chain — which it must print, because the two chains' ends are
different objects:

    paths in the chain          en 285 · vi 276
    turbo.json, final           en  75 · vi  62
    turbo.json, at 3.17 / 3.22 / 3.23 / 3.24     en 59 · 62 · 62 · 62, and vi the same at each

The mechanism is ordering: `const en = replay("en", …)` at `check-fence-chain.mjs:204`, the
appendix loop mutating `en.state` only, and `const vi = replay("vi", …)` at `:300`, after both the
appendix and the HEAD comparison. **A "vi final state" is the vi chain's own end and nothing in
this feature repairs it** — it is the measurable form of `gaps.md` 050-3.

**And the second row is why FR-011 is safe.** All 30 Vietnamese problems are chapter problems, and
at every chapter this feature touches the two chains hold identical state. Regenerating in English
and copying to Vietnamese is therefore checked against the states it actually lands on, rather
than inferred from `MIRROR` reading 0 — which would have been an argument that the two fence
*bodies* match, not that the two *chains* do.

**Alternatives considered.** *A separate script importing the checker's internals* — the checker
is a top-level program with no exports, so this means refactoring it into a module: more change,
same result. *Keep making throwaway copies* — 50 regenerations against a copy nobody reviews is
the shape feature 049 found in `check-lane-scope.py`, which pointed at a deleted worktree and
reported zero for a year.

---

## R9 — The order the repairs have to happen in

Forced by the mechanics rather than chosen:

1. **The 11 not-files first.** They are independent of everything, they touch no chain state, and
   they take the count from 110 to 99 with no risk — which also proves the measurement loop works
   before anything expensive happens.
2. **APPLY before HEAD, per file.** A divergence is what remains after every hunk applies.
3. **The first failing hunk before the rest, per file.** Nine of `vitest.coverage.config.mts`'s
   are shadows.
4. **Introductions before the hunks that depend on them.** A `diff` with no predecessor cannot be
   regenerated against a state that does not exist.
5. **English before Vietnamese, per fence.** The vi body is a copy of the repaired en body.

---

## R10 — What this feature cannot find out by reading

Recorded now so the phases do not discover it as a surprise:

- **Whether each of the nine files has a chapter that would honestly introduce it.** That is nine
  judgements about published prose, and the answer decides between R2's two designs per file.
- **What the 867-line and 540-line divergences become after their hunks are repaired.** Both
  numbers are measured against a chain state that is missing content those hunks would have
  added.
- **Whether repairing a hunk unanchors a later one.** The 111→203 measurement says it can. Only
  running the checker after each file answers it, which is why FR-003 measures per file.
