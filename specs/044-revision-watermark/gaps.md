# Gaps — feature 044, the revision watermark

**Twenty-eight items carried from feature 043, every one re-measured against the tree rather
than copied.** Feature 043 found that three of its carried items had closed without anyone
working on them, and chapter 3.24 found three that were wrong on the day they were written. So
the numbers below were taken today, and where one moved, both numbers are shown.

**One carried item was re-measured and CONFIRMED OPEN against a plausible-looking closure** — a
test file appeared that looks like it closes 3.23-4 and closes a different list. That is the
single most useful thing a re-measurement does, and it only happens if the re-measurement reads
the assertion rather than the filename.

---

## CLOSED BY THIS FEATURE — NONE

**Said plainly rather than by omission.** This feature built a signal; it closed no item on the
ledger it inherited. Two things it *did* fix were its own defects rather than carried gaps —
FR-008's client half missing from the published text, and FR-003 cited by two test titles and
asserted by neither — and both are recorded against the tasks that found them, not here.

---

## CARRIED, RE-MEASURED — THE NUMBERS THAT MOVED

### 3.22-3 (`C3`). An excerpt-only file is never verified — **OPEN. Thirteen, unchanged.**

3.22 recorded two, 3.24 corrected it to ten, 043 measured thirteen. **Thirteen today**, the same
thirteen files.

**The naive measurement said fifteen and was wrong**, which is worth recording because it is the
same shape of error the count has made three times. Two titles carry a prose suffix —
`packages/protocol/src/frames.ts, chapter 1.3` and `services/gateway/src/session.ts before this
chapter` — and both base files are fully chained elsewhere. Normalising the title before
comparing gives thirteen. A count of this class has now been wrong four times out of five, and
every error was in how the title was parsed rather than in the tree.

**This feature edited one of the thirteen, and it is the worst one to edit.**
`services/gateway/src/session.itest.ts` now holds the **only** end-to-end proof that the column,
the api and the ack are connected — `repository.itest.ts` proves the column moves,
`resume.itest.ts` proves the ack carries what a stub reports, and neither proves the two are
joined. That proof is in the one file no gate compares to anything.

### 3.22-6 (`C6`). Files that discard their child's output — **CLOSED. Still zero.**

3.22 counted nine, 3.24 re-measured eleven, 043 measured zero. **Zero today.** Two matches remain
in `meter.itest.ts` and `membership.itest.ts` and both are comments explaining why the practice
was abandoned. Re-measured rather than carried, because a closed item that quietly reopens is
exactly what this ledger exists to catch.

### 3.23-4. One authorization fact lives in two places — **OPEN, and a lookalike nearly closed it.**

`packages/test-harness/src/lists-agree.test.ts` exists and asserts that two exemption lists name
the same files — **and the pair it asserts is `DRAIN_EXEMPT_TESTS` against `EXEMPT_FILES`.**
3.23-4 is about `DRIVER_EXEMPT_TESTS`, which is declared in the same config file, spread into the
same block list, mentioned in four comments, and has **no agreement test at all**.

A filename-level re-measurement would have closed this item. Reading the assertions kept it open.
**The template for the fix is already in the repository**, sitting one `describe` away from the
list that needs it.

### 043-1. An untitled fence is never compared to anything — **OPEN. 146 of 904, unchanged.**

758 titled, 146 untitled, 16% of every opening code fence across the 41 English chapters —
identical to 043's measurement, and expected to be: this feature published no chapter, and every
fence it wrote is a titled diff in the appendix. The number moving would have been the surprise.

---

## CARRIED, RE-MEASURED — UNCHANGED

### 3.23-2. FR-MOD-03's audit log — **OPEN.** Chapter 4.7's, out of scope by name.

### 3.23-7. The tenancy catalogue's reach was fixed; the guard's coverage was not — **OPEN, untouched.**

### 3.22-4 (`C4`). `main.test.ts` checks that a module is CLOSED, not PASSED — **OPEN, untouched.**

### 3.22-5 (`C5`). The retry-log bound is a five-module decision — **OPEN, untouched.**

### 3.22-7 (`C7`). Coverage cannot see an omission — **OPEN, and this feature added a case.**

v8 records a `&&` operand as covered when it was *evaluated*. This feature's own contribution is
adjacent and worse, because it is not about coverage at all: **a test can be at 100% coverage of
a line and assert nothing about why the line is there.** The FR-003 test written by this feature's
own title audit executed every line it touched and would have passed with the property it named
inverted. Coverage saw a green file.

### 3.22-8 (`C8`). The per-chapter instruments have no owner — **OPEN for the EIGHTH feature.**

Six Python instruments in `specs/044-revision-watermark/`, copied from 043, which copied them
from 042. They will be copied into 045 and drift there.

---

## NEW — TWO

### 044-1. THE `grep` ON THIS MACHINE IS NOT THE `grep` THE SCRIPTS ASSUME — **NEW, OPEN**

`grep` on `PATH` is **ugrep 7.8.4**. `/usr/bin/grep` is **GNU grep 3.12**. They are not the same
engine, and they disagree:

    (postgres|redis)://[^:/@]+:[^@/]+@     ugrep: 0 matches    GNU grep: 1 match
    postgres://[^:/@]+:[^@/]+@             ugrep: 1 match      GNU grep: 1 match

A grouped alternation followed by two negated character classes matches nothing under ugrep and
matches under GNU grep. **No error, no warning — a zero.**

This feature's credential scan filed that zero as evidence of a clean corpus, over a corpus
containing the string twice, and the only reason it was caught is that a second pattern reported
zero on material somebody happened to remember was there.

**Measured reach:** one shipped gate uses `grep -E` with a group — `check-srs-ids.sh:49`. Its
pattern is an optional group rather than an alternation, and it was run under both engines and
produces **byte-identical output** (245 ids either way). So the exposure is real and currently
harmless.

**The cheap fix is not "use GNU grep".** It is the one this feature's re-run adopted: **give every
pattern a positive control**, and report a pattern that fails to match its own example as BROKEN
rather than as zero. That works whatever engine is underneath, and it is the only thing that
turns a `0` into a claim about the corpus.

### 044-2. SIX TASK IDS SURVIVE IN TEST TITLES — **NEW, OPEN, and it is a small number on purpose**

    services/api/src/fanout/fanout.itest.ts        T018
    services/api/src/channels/channels.itest.ts    T052, T078
    services/api/src/isolation/gauntlet.itest.ts   T031, T031b
    services/gateway/src/membership.itest.ts       T036, T086

**A task id in a test title outlives the task.** 3.22 wrote one, 3.23 fifty-two, 3.24 thirty-three
and stripped its own; these six are the residue from chapters whose audits reached only the files
they touched. Feature 044 added none.

Filed rather than fixed: editing six unrelated suites during a close-out is a change nobody asked
for, and nothing in this feature's gate set would re-verify it. **It is six lines of work for
whoever wants it**, and the reason it keeps recurring is that every audit is scoped to one
feature's files while the rule is repository-wide.

---

## THE ONE THAT IS NOT NUMBERED, BECAUSE THIRTEEN FEATURES HAVE NUMBERED IT

**USE A PERSON.** Chapters 3.14 through 3.24 each named this gap, feature 043 was the twelfth,
and this is the thirteenth. It did not close it either.

`specs/036-chapter-3-18/reader-protocol.md`: 45 minutes, six questions, one person who has not
read the work.

**And this feature has the sharpest evidence yet for why the substitute does not work.** SC-006
asks whether a client developer can implement the repair from the published text alone. The
close-out reading pass ran
the closest available approximation — read §5.2 and the three clauses with the spec and the source
closed — and it found a real hole: the *higher-than-reported* case had no client instruction at
all, only the platform's half of it.

That is a genuine finding, and it is **the only kind that exercise can produce**. It finds
information that is ABSENT. It cannot find information that is present and unclear, because the
person running it wrote the sentence and cannot unknow what it was meant to say. Every instrument
in these three repositories compares bytes — six Python checkers, five `check:*` scripts, a
compile-time assertion, and now a positive-control scanner — and not one of them, and not the
author re-reading their own paragraph, can answer the question SC-006 asks.
