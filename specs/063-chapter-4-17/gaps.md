# Gaps — feature 063, chapter 4.17

Numbered as they are found, not as they are fixed. **Seven entries**, then the carried ledger. An entry here is something measured and
left open on purpose, with the cost of closing it attached so nobody has to re-derive it.

## 063-1 — `integrate.itest.ts` has four poll-to-deadline helpers and should have one

**Measured.** `waitFor` is defined **three times** in
`relay-platform/packages/outsider/src/integrate.itest.ts` — lines 476, 348 and 423 before this
chapter, one per test, each a 10-second deadline over a frame array — and chapter 4.17 adds a
fourth waiter, `waitForAttachmentState`, over a different thing (an attachment's state read
back through history). The three frame waiters differ only in the payload type they name.

**Why it is left open.** Consolidating is the better code and this is the wrong chapter to pay
for it. The file is titled in **five fences — two whole bodies and six diffs** — across
`part-3/chapter-26` in both locales, `part-4/chapter-08`, `part-4/chapter-09` and the appendix.
**A titled fence is a whole-body claim** (051-6), so lifting a helper touches four regions of a
file whose every published copy would then need regenerating: two whole bodies and six
re-anchored hunks, in a milestone chapter whose own line says it adds no product surface.

**How to apply it.** The next chapter that edits this file for its own reasons should lift all
four at once, and pay the fence bill once rather than twice. The bill above is the number to
budget with.

**AND THE ONE HELPER THIS CHAPTER DID ADD IS AT DESCRIBE SCOPE, WHICH REFINES T010a's
DECISION.** That decision — *"a local helper, and no consolidation"* — was taken about the three
frame waiters, each of which has exactly one caller. `waitForAttachmentState` has **three**, in
three different `it(...)` blocks: the existing media test (whose false comment this chapter
corrects), the journey, and the rejection. A local copy would therefore have been three copies,
which is the thing this entry exists to stop. **One caller is a judgement; three is the answer.**

## 063-2 — one upload in six waits five or six sweeps for a verdict, and nothing says why

**Measured, over three batteries with independent phase** (a uniform random 0–5,000 ms
sleep before each trial, so the upload lands at a uniform point in the cycle):

    n = 25    verdict  min 1,097 · p50 3,398 · max 36,164 ms
    n = 12    verdict  min   433 · p50 3,871 · max 32,247 ms

4 of 25 and 1 of 12 landed at **19.3 / 30.2 / 32.2 / 32.2 / 36.2 seconds** — five or six
whole passes during which the object was `pending`, in the bucket, inside the 24-hour
window, and not decided. The body of the distribution is exactly what the design predicts:
uniform on [0, 5,000] plus work under half a second.

**Three explanations eliminated by measurement, not by argument.**

    the sweep stopped     NO   twelve consecutive passes at 5.36–5.41 s, read off the
                               api's access log (nine `GET /internal/media/pending` each)
    the scan was slow     NO   20 INSTREAM scans of the same fixture: min 2 · p50 2 ·
                               max 4 ms, 20 of 20 `OK`
    the worker had died   NO   it was serving nine pending pages every 5.4 s throughout

`verify` returns `null` — counted as `waiting`, logged nowhere — on three paths: a `HEAD`
that finds nothing, a ranged `GET` that finds nothing, and a scanner that could not answer.
All three are correct refusals under FR-009 and **all three are silent**, so a pass that
skipped this object looks identical to a pass over an empty backlog.

**The one clue is the column beside it.** `link` (`GET /v1/media/{id}`, pure Postgres plus
a signature) reads **11–12 ms on exactly the tail trials and 4–6 ms on every other one**.
Whatever delays the worker delays the api in the same window, which points at something
shared rather than at the media path.

**Why it is left open.** Chapter 4.17 adds no mechanism (FR-012) and the sweep is 4.13's.
Diagnosing this means instrumenting `verify`'s three null paths, which is a product change
in a milestone chapter whose own line says it makes none. **What the chapter does instead
is publish the distribution with its tail**, because a p50 of 3,398 ms alone would claim
the path is reliably under four seconds and one upload in six is not.

**How to apply it.** The first useful instrument is a counter per null path in the sweep's
summary — `waiting` is currently one number covering three different facts. That is a
one-line change to a log line and it would turn this entry into a diagnosis.

## 063-3 — the worker's log cannot say "alive, nothing to do", and I misread it for ten minutes

`services/media-worker/src/main.ts` logs a sweep **only when `ready > 0 || rejected > 0`**,
deliberately: *"a sweep over an empty backlog every five seconds would otherwise be the
loudest thing in the log."* The reasoning is sound and the consequence was not written
down — **an idle worker is byte-identical, in the log, to a stopped one.**

**Measured.** Four minutes of `docker compose logs media-worker --tail 1` returning the
same line, with `docker compose ps` saying `running`, produced a confident and wrong
conclusion that the worker had hung. 62 seconds of deliberate idle then gave **0 sweep
lines and 0 change in the ready count**, while the api's access log showed **nine
`/internal/media/pending` requests every 5.4 s** for the whole period.

**Every inference drawn from the gaps was wrong** — a 27-second stall, a 91-second stall, a
hung process — and the instrument that corrected all of them was **a different process's
log of the first one's requests.** This is the fifth time this series has met a check that
cannot report the thing it is read for (4.2's `/ping`, 4.9's unset credential, 4.10's
bucket, 4.13's signature age), with the polarity reversed: not a check that cannot fail,
but a log that cannot say it is working.

**How to apply it.** A heartbeat at a lower rate — one line a minute carrying the pass
count and the backlog — costs almost nothing and makes liveness readable. Left unbuilt here
for FR-012's reason; recorded so the next chapter that opens this file does not re-derive
it. **And meanwhile: for liveness, read the log of whatever the process TALKS to.**

## 063-4 — three feature-local ids mean two different things each inside `docs/`, and the check that would find it is diff-scoped

**Measured tree-wide.** `docs/` holds 22 distinct `FR-0NN` ids. Most are correctly qualified
(*"FR-013 of chapter 3.23"*, *"043's own FR-016"*) or are the SRS correcting an earlier leak.
**Five were unqualified and are fixed in this chapter**, by feature number:

    docs/04-srs.md:941                (FR-009)                feature 059's
    docs/05-sad.md:1736               FR-013 requires …       feature 040's
    docs/05-sad.md:2003               FR-017's refusal        feature 056's
    docs/12-part-4-structure.md:241   now FR-017              feature 056's
    docs/12-part-4-structure.md:407   FR-008 states the rule  045's

**What is left open is the collision.** `FR-009`, `FR-013` and `FR-017` each name two unrelated
things across these documents — a scanner that cannot answer and an idempotent delete; a
connection-cap race and a deletion grant; a store outage and a tombstone read path. Qualifying
each citation makes every individual sentence correct and does nothing about a reader who greps.

**And the instrument cannot find any of it.** The check `gaps.md` 052-7 produced is
`git diff HEAD -- docs/ | grep '^+' | grep -oE 'FR-0[0-9][0-9]'`. It is **diff-scoped**, so it
catches a leak being made and never one already in the tree — this chapter's diff is clean while
five leaks sat in the files it was editing. **Nothing runs either version**, five features on
from 052-7.

**How to apply it.** A tree-wide version is three lines and would have to allow the qualified
spellings, which is a pattern rather than a list: an `FR-0NN` is acceptable when "feature", a
four-digit feature number, or "chapter" appears within about forty characters of it. That is a
checker somebody can write; what it must not become is a hand-maintained allow-list, which is
the thing this project refuses (056-10).

**AND THE QUALIFIER MUST BE A FEATURE NUMBER.** The connection-cap feature is
`specs/040-chapter-3-22/` and its chapter is now **3.16, "the sixth connection"** — feature 045
renumbered 21 of Part 3's 26 chapters. The existing *"of chapter 3.23"* spellings in
`docs/05-sad.md` are therefore the next instance of this entry, pointing at chapters that have
moved. **Name a chapter, never number it** applies to citations too.

---

## The carried ledger, re-measured

**Re-measured, not copied.** 043 found four of twenty-three carried items wrong when they were
measured again, and three had closed with nobody working on them.

### 050-8 — the ingester has no deployment, and the count is **two**, not three

    services/api/src/request-log/request-log.itest.ts   spawns services/ingester/dist/main.js
    services/api/src/media/media.itest.ts               spawns the same

    compose.yaml services named `ingester`              0
    services/ingester/Dockerfile                        does not exist

**Narrower than the entry said and still open.** Two test files starting a process is not a
deployment. On the stack this series ships, nothing drains the analytical streams, so a customer
reading their own request log finds it empty — and `gauntlet.itest.ts:1326` now has a comment
relying on that, which is the shape of a defect becoming load-bearing.

### 062-7 — a coverage number is a claim about what ran in *this* process, and 4.17 is the same thing one step out

062 measured three symbols at 78.57 / 81.37 / 83.78 against pins of 100 and 84, because the
suite exercising them **spawns the ingester as a child process**. This chapter's suite is that
finding one level further out: `packages/outsider` talks to a composed stack over HTTP, so
nothing it exercises is instrumented by anything — and the package is excluded from the coverage
lane outright at `vitest.coverage.config.mts:98`.

**What is new is the consequence, which is now written in `docs/05-sad.md`** (T047): the
deployed media worker has exactly one automated consumer, it runs only in CI's sealed job, and
it contributes nothing to the coverage number. Still open: nothing measures coverage of code
executed in a container.

### 062-12 — per-file pins: **75**, from 74

One pin added since 062's close. The entry's point stands: the ratchet holds a minority of the
files it could, so a file with no pin can fall to any number and nothing says so. Both instances
of that class were found by a human comparing one chapter to another.

### 055-3 — corrected at 062, and the correction holds

`check:errors` has no job under that name, and the check runs: `ci.yml:211` is
`node ../relay-tutorial/scripts/check-error-codes.mjs`, by path. **A check with two spellings,
and a sweep for either finds half the truth.** Re-measured this chapter: unchanged.

### 043-1 — untitled fences, and the class has grown by 2.6× since it was opened

    043's measurement     146 of 904 fences untitled    16.2%
    this chapter          387 of 2,158 untitled         17.9%

An untitled fence is compared to nothing — `check-fence-chain.mjs:77` collects a fence only when
it matches `title="…"`. **This chapter added two of them on purpose**, which is the right use:
an excerpt must be untitled, because a titled fence is a whole-body claim on a 1,677-line file.
The entry is about the ones nobody decided, and it is still nobody's.

---

## 063-5 — `echo "EXIT=$?"` after a pipeline, for the seventh time, and the second by me

    python3 relay-tutorial/scripts/check-lane-scope.py 2>&1 | tail -6; echo "T040 EXIT=$?"

printed **`T040 EXIT=0`** for a path that does not exist. `$?` after a pipeline is the LAST
command's status, and `tail` succeeded at reading nothing. The script is at
`specs/045-part-3-rework/check-lane-scope.py`.

**Seventh occurrence in this project**, and the first six were other people's. The shape that
keeps producing it is a gate run for its counted line — the pipe exists to trim the output, and
the status check is bolted on after it. **Capture the exit code outside the pipeline, or write
the output to a file and read it**, which is what the rest of this feature's runs did:

    pnpm <gate> > out.log 2>&1; echo "EXIT=$?"; tail -3 out.log

**And the control that caught it was 055-4's rule, not the exit code**: *assert the counted
line, not the exit code.* The line said `can't open file`, which no status would have.

## 063-6 — `check-lane-scope.py` reads this chapter's suite and has nothing to say about it

    check-lane-scope: 71 integration files, 0 unscoped read(s) of a shared table in 0 file(s)
    controls: 10 of 10 fired

**71 files, up from 55 at feature 055**, and `packages/outsider/src/integrate.itest.ts` is one
of them — its glob is `packages/*/src/**/*.itest.ts`. The file contains **no SQL at all**,
because the seal forbids a database client, so the zero it contributes is a true statement about
a file the instrument cannot examine.

This is not the 049 failure (a checker reading a deleted worktree and exiting 0 over nothing):
the corpus is real and the count proves it looked. It is the weaker thing the script's own last
line admits — *"SQL text only — a scope applied in JavaScript is invisible to it"* — with a new
case: **a suite whose scoping is entirely in HTTP paths and bearer tokens.** Recorded as a limit
so a later chapter does not read `71 files, 0 unscoped` as covering the sealed suite.

## 063-7 — `media-updated.itest.ts` subscribes to `revision:*` and counts, so it fails for somebody else's reason

**Found by running the quickstart against the composed stack while `pnpm test:integration` was
running** — which is a thing the tasks tell you not to do (T024, after 056), and doing it is what
exposed this:

    FAIL  src/media/media-updated.itest.ts > publishes once per referencing channel
          when an object is in two
    AssertionError: expected [ {…}, {…}, {…} ] to have a length of 2 but got 3

The suite's `beforeAll` runs `sub.psubscribe("revision:*")` and pushes **every** frame on that
pattern into one array. Three tests then clear the array, trigger a verdict, and assert the
array's length. The pattern is not scoped to the test's environment, its channels or its object:
**any `media.updated` published by anything else sharing that Redis lands in the count.**

**This is 043's class — an assertion scoped wider than the thing it tests — and
`check-lane-scope.py` cannot see it.** That instrument reads SQL text and reports *"71
integration files, 0 unscoped reads"*; this scope is a **Redis pattern subscription**, which it
has no opinion about. 063-6 records the limit abstractly and this is the instance.

**The repair is small and is not this chapter's**: the frames are already tagged with a subject,
so the three assertions can filter to the channels the test created. Recorded with its bill
rather than applied, because a milestone that fixes things stops being a measurement of what was
already there — and because it was my own interference that surfaced it, which makes "it is
flaky" the wrong conclusion and "it is scoped to the whole instance" the right one.

**AND THE SAME RUN TOOK DOWN `outbox.itest.ts`'s *"invariant 1: a committed message leaves
exactly one outbox row"***, which is 043's original whole-table count at a different address.
Both failures vanish when the lane runs alone — so the lane's green is conditional on nothing
else touching the stack, and nothing anywhere says so.
