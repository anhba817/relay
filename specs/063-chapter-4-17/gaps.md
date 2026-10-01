# Gaps — feature 063, chapter 4.17

Numbered as they are found, not as they are fixed. An entry here is something measured and
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
