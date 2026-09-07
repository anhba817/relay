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

## CLOSED BY THIS FEATURE — TWO, BOTH AFTER THE CLOSE-OUT

The feature itself closed none: it built a signal, and the two things it fixed on the way —
FR-008's client half missing from the published text, and FR-003 cited by two test titles and
asserted by neither — were its own defects rather than carried gaps.

**044-2 and 3.23-4 were then taken deliberately, as work of their own**, after the close-out and
against this ledger rather than against a task list. Both are below with what the fix cost and
what re-measuring found.

### 044-2. Task ids in test titles — **CLOSED**

Seven ids across six titles in four suites, gone. Each replacement says what the title already
proved; none points at a plan.

**Two of the seven could not be removed on their own**, and both are the reason this was worth
doing rather than tidying:

- `fanout.itest.ts` carried a comment fifty lines above the test — *"Raw is kept because T018
  asserts on the exact key set"* — **a reference pointing at the title by its id**. Removing the
  id from the title alone would have left a comment citing something no longer findable, which
  is worse than the id was.
- `membership.itest.ts` printed `[T066] request-return to notice: … ms` **to standard output**.
  That is the title problem in its purest form: it lands in CI with no file, no line and no way
  back to what `T066` asked for.

**AND THE SCOPE IS NARROWER THAN THE RULE.** Counting ids anywhere in test files gives **330
occurrences of 170 distinct ids across 46 files** — comments, section rules, fixture strings.
That is a different item and a much weaker one, so it is filed below as 044-3 rather than folded
into this fix. **A title is read detached from its file; a comment is read by somebody who
already has the file open**, and that difference is the whole argument for doing one and not the
other.

The boundary taken: each title fixed, plus every id inside that same test's own body or preamble,
plus any reference elsewhere pointing at the title being changed. Nothing else.

### 3.23-4. One authorization fact lives in two places — **CLOSED, and the item's premise was wrong**

The item said `DRIVER_EXEMPT_TESTS` and "the harness's own list" agree by somebody remembering.
**There is no second list.** `EXEMPT_FILES` in `exempt.ts` is the DRAIN counterpart, already
asserted; the driver list is a single declaration in `eslint.config.mjs`, and what it must agree
with is **the tree**.

Which makes the real defect sharper than the one filed. **The linter checks one direction only:**
a file that imports `pg` and is not listed fails loudly; a file that IS listed and imports nothing
restricted passes forever and says nothing. So the list can only grow, and a stale entry is not
cosmetic — it holds a standing exemption over a file that no longer needs one, and the next edit
reintroducing raw access to that file goes through unremarked. This is
`check-error-codes.mjs`'s lesson in a second place: **compare both directions, and the direction
nobody enforces is the one that rots.**

`packages/test-harness/src/lists-agree.test.ts` gains a second describe asserting every entry
exists and still imports something the rule restricts — with the restricted module names **read
from the rule** rather than restated, because restating them would be this file's own defect one
file over. Tested red three ways: a stale entry, an entry for a deleted file, and the list
declared but not wired into any `files:` block. All 16 entries are live today.

**The detector was wrong on its first run and the control is what caught it.** It looked for `pg`
and `drizzle-orm` and reported **seven of sixteen** entries as stale — because the rule also
restricts `ioredis`, which those seven gateway suites import. A pattern that fails its own example
is broken, not evidence. Both controls are now assertions in the test: a file that must read as
needing the exemption, and one that must read as not.

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

### 3.23-4. One authorization fact lives in two places — **CLOSED after the close-out. This is where the re-measurement happened; the fix is at the top of this file.**

`packages/test-harness/src/lists-agree.test.ts` exists and asserts that two exemption lists name
the same files — **and the pair it asserts is `DRAIN_EXEMPT_TESTS` against `EXEMPT_FILES`.**
3.23-4 is about `DRIVER_EXEMPT_TESTS`, which is declared in the same config file, spread into the
same block list, mentioned in four comments, and has **no agreement test at all**.

A filename-level re-measurement would have closed this item. Reading the assertions kept it open —
and the fix then went **into that same file**, one `describe` below the list that misled the
count. The file's header now says which describe covers which pair, so the next reader does not
have to make the same mistake to find out.

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

## NEW — THREE, ONE OF THEM ALREADY CLOSED

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

### 044-2. Task ids in test titles — **CLOSED after the close-out. Measurement below; fix at the top of this file.**

    services/api/src/fanout/fanout.itest.ts        T018
    services/api/src/channels/channels.itest.ts    T052, T078
    services/api/src/isolation/gauntlet.itest.ts   T031, T031b
    services/gateway/src/membership.itest.ts       T036, T086

**A task id in a test title outlives the task.** 3.22 wrote one, 3.23 fifty-two, 3.24 thirty-three
and stripped its own; these seven were the residue from chapters whose audits reached only the
files they touched. Feature 044 added none.

**The count was right, which is worth recording** — this project's counts of this kind have been
wrong four times out of five. Seven ids, six titles, four files, confirmed on re-measurement
before the fix.

### 044-3. TASK IDS EVERYWHERE ELSE IN THE TEST TREE — **NEW, OPEN, and deliberately not fixed**

    ids in test TITLES       0     (was 7 — closed above as 044-2)
    ids anywhere in tests   330 occurrences, 170 distinct, across 46 files

Comments, section rules, fixture strings. **The same rule applies and the argument is much
weaker**, which is why this is a separate item rather than a bigger version of 044-2: a comment
is read by somebody who already has the file open and can `git log` it, while a title arrives in
a CI summary with nothing attached.

Two shapes inside the 330 are worth more than the rest and would make a decent first pass:
ids in **section-rule comments** (`// ── T028: read ───`), which are load-bearing navigation and
name nothing a reader can look up; and ids in **`console.log` output**, of which there are now
zero, having been the one instance 044-2 caught.

**Filed rather than fixed.** Rewriting 330 comments across 46 suites is a change nobody asked for,
touching every suite in the platform, that no gate would re-verify — and the fence chain would
carry an amendment hunk for each fenced one. The cheap version is a rule for new tests plus
opportunistic cleanup, not a sweep.

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
