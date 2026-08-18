# Chapter 3.6 — notes, written from what happened

Not a summary of the plan. The plan is in `plan.md` and it was incomplete in
places; this is the record of what the work actually did, including the parts
that were discovered rather than designed, and the parts that went badly.

---

## The baseline was red before this chapter touched anything

The first task was to measure the starting state. It failed, and then it kept
failing differently. `pnpm test:integration` at tag `part3-ch5` failed on two of
three runs, with three unrelated causes, and a fourth appeared later.

**1. One suite's teardown deleted another suite's live consumer.** Chapter 3.4's
`consumer.itest.ts` cleaned up by deleting every durable consumer on `EVENTS`
whose name began with `itest-`. Chapter 3.5's dispatcher suite named its expand
consumer `itest-expand-<run>`, on that same stream, and Turborepo runs the two
packages' lanes at once.

Proved rather than inferred: a decoy consumer named `itest-expand-PROBE0001` was
created by hand, the api suite was run alone, and the decoy was gone afterwards.

The file already contained the rule that would have prevented it. Its comment on
`spawnedDurables` explains that a prefix sweep would delete a reader's walk
running alongside it — reasoning applied to the walk's durables and not to the
suite's own names.

**2. A wildcard consumer eating another suite's events.** The dispatcher's expand
consumer filters `events.>`, every environment, as it must in production. Run
beside the api's consumer suite it also consumed that suite's events and garbage,
and a test whose own message queued behind that traffic timed out at 60 seconds.
Fixed by serialising the lane (`--concurrency=1`), which is what
`vitest.coverage.config.mts` already did with `fileParallelism: false`. The
precedent was in the repository; it had only been applied to one lane.

**3. A security assertion with a one-character needle.** `credentials.itest.ts`
derived the secret to search for with `key.credential.split("_").at(-1)`. A
credential is `rk_dev_<32 hex>_<32 bytes base64url>`, and base64url's alphabet
contains `_`. `api-key.ts` carries a paragraph explaining exactly this, and even
records that an earlier document said "split on the last separator" until the
first mint that produced a secret with an underscore said otherwise.

It failed when a mint ended `…_I`: the assertion had become "no log line contains
the letter I", and the error body for a misused key says "this route expects an
API key". **The invisible half was worse and was true on most runs** — whenever
the secret contained an underscore, only the fragment after the last one was
checked, so a log line leaking the first thirty characters of a signing secret
would have passed. The one test standing between a credential and a log file was
weaker than it looked.

**4. A real duplicate on the resume boundary. NOT FIXED.** `packages/e2e`
journey 4 produced `[1, 2, 3, 4, 4]` — the resume backfill and the live flush
both delivered sequence 4. That is the "no gap and no double" property FR-RTM-03
claims, failing once in six runs. It is the gateway's resume path, chapter 2.7's
subject, and a fix belongs in a chapter that can explain it. Recorded with its
reproduction rate in `baseline.txt` so it is a known defect rather than folklore
about a flaky e2e suite.

The three fixes went to `relay-tutorial/fences/post-series.md` rather than into a
chapter: 3.4 and 3.5 own those files and neither discusses test-harness hygiene,
and Part 6 owns CI.

**What this cost.** Roughly a third of the chapter's implementation time went to
work that was not the chapter. It was not optional — every verification task here
runs that lane, and a lane that fails two runs in three cannot tell this
chapter's breakage from the noise it inherited.

---

## What R1's measurement changed, and what it did not

R1 computed the attempt timeline against 3.5's tier table before anything was
built: six attempts inside the first hour, the seventh at +2h35m36s, nothing at
the hour itself. That disqualified the single-trigger design the rest of the
chapter would have rested on and produced the sweep.

That much was planning. What running it added was the transcript: with
`RELAY_DISABLE_SWEEP=off`, the walk shows seven failures, a dead-lettered
delivery, a run more than an hour old, and `enabled=true`. The arithmetic said it
would happen; watching it happen is what the chapter can show a reader.

---

## Defects and gaps this chapter found in its own work

Every one was found by running something.

**1. The sabotage battery contradicted a comment, and the comment was wrong.**
`applyFailureRun` claimed `SELECT … FOR UPDATE` was "the whole of FR-008's
concurrency story" — that without it, two concurrent outcome reports would both
disable and both notify. The mutation removed the lock and **46 tests passed**.

The `enabled = true` predicate is sufficient for at-most-once on its own. What
the lock protects is the counter: under `READ COMMITTED` both transactions read
4, both write 5, and the run undercounts by one per collision, quietly making
FR-007's floor harder to reach than the requirement says. There is now a test for
the counter and the comment says what the lock does.

**2. The sweep was tested and its place in the loop was not.** Deleting
`await sweepOnce()` from the relay's `run()` broke nothing — every test called
`sweepOnce` or `sweepDisabledEndpoints` directly. Same shape as 3.5's
unfalsifiable "terminated, not retried" assertion: the mechanism covered, the
wiring not. A test that calls `start()` and then only waits now covers it.

**3. A mutation that could not compile.** The first version of sabotage 4 replaced
`try {` with `{` and left a dangling `catch`. The battery reported it caught; it
was caught by `tsc`, which says nothing about whether a test holds the property.
Rewritten to remove the swallow instead.

**4. The battery ate an uncommitted fix.** Its revert step is `git checkout --`,
so a re-run silently discarded a comment correction that had not been committed,
and the byte-identical check failed against the previous run's hashes. Commit
before running a battery that reverts by checkout.

**5. `deliveryMaterial` refused test events.** Invariant 9 (a disabled endpoint
receives no attempts) was enforced where the dispatcher asks for material, and
FR-WHK-09 says a test event reaches a disabled endpoint. The first run of
`test-event.itest.ts` failed there. `synthetic` is the discriminator — the reason
that column exists rather than a `payload->>'type'` comparison.

**6. New suites starved an old one.** Four `dispatcher.itest.ts` tests failed
under the coverage lane with `expected 0 to be greater than 0` — nothing
delivered, no error. This chapter's tests report failures, so their deliveries
reschedule and stay due for ever; a few hundred of them sat at the front of the
relay's 50-row global window and the dispatcher suite's own delivery never got
claimed. The suite that caused it passed. Both new suites now settle what they
create.

**7. The test suite defined a stream the api owns.** `attempts.itest.ts` deletes
the `ANALYTICS` stream to prove a delivery survives without it, and its teardown
recreated the stream from a hand-written configuration that omitted `max_bytes`.
For two hours the stream a reader would have inspected with `stream-info.mjs` was
the test's stream wearing the api's name — unbounded where the api bounds it at a
gigabyte. The teardown now calls `ensureAnalyticsStream`.

**8. The api does not recreate a stream deleted underneath it.** Its publisher
ensures the stream when it opens a connection, and that connection is cached for
the process's life. An operator who deletes `ANALYTICS` loses attempt records
until the api restarts. Left as it is — the failure is swallowed by design and
costs analytics rather than deliveries — and stated in the test that discovered
it rather than left for somebody to find.

---

## Corrections to this feature's own artifacts

- **`contracts/attempts.md` listed `skipped` as an attempt outcome.** It is a
  dispatcher decision reported to nobody, so no outcome is recorded and no event
  is published. A consumer switching on four values would have written a branch
  that can never execute.
- **`data-model.md`'s four columns became eight.** FR-WHK-09's response and the
  sweep's notification both need the last outcome persisted, and the sweep fires
  precisely when no outcome is in hand. Recorded in the file with the reason for
  each, rather than folded in silently.
- **`contracts/webhooks.md` documented `/v1/webhook-endpoints/…`.** The
  management surface is at `/v1/webhooks`, where 3.5 put it.
- **The contract did not say what a test returns when nothing makes the attempt.**
  It answers `200` with `delivered: false` and an error naming the platform, not
  the customer.
- **Quickstart V8 said five mutations.** Seven shipped; the two added are 3.5's
  deduplication bug aimed at the new publisher, and the row lock.
- **Invariant 1 needed a second sentence.** A repeated outcome report records
  nothing and must publish nothing, or a dashboard shows a retry that never
  happened.

---

## What it exposed in earlier work

Three fixes, all recorded in `fences/post-series.md`: the consumer teardown, the
credential assertion, and the serialised lane. All three are chapter 3.4's and
3.5's files and none of those chapters discusses what was changed.

The e2e resume duplicate is the fourth and is left alone deliberately.

The two Redis knobs are still two knobs. `RELAY_REDIS_URL` for production code,
`RELAY_REDIS_PORT` for the integration tests. Chapters 3.4, 3.5 and now 3.6 have
recorded it. Recording it a fourth time is not the fix.

One new entry for that list: **`RELAY_WEBHOOK_SECRET_KEY` is base64, not hex.** A
64-character hex string decodes to 48 bytes and every webhook suite fails with
"must decode to 32 bytes, got 48". It cost an hour here.

---

## The chapter is over its word bound

`docs/07-tutorial-plan.md` sets 2,000–4,000 words of prose outside code fences.
This chapter is 5,346 and chapter 3.5 was 4,996. Nothing enforces the bound, so
neither was caught when it shipped.

Not fixed here, because trimming a quarter of a finished chapter or splitting it
in two is a scope decision rather than an implementation one. The seam, if it
splits, is at "Now the decision": everything before is the attempt record and
everything after is auto-disable, and the chapter already argues they are
separable in exactly that place. Recorded in `battery.txt` with the three options
and in `docs/07-tutorial-plan.md` where the rule lives.

---

## Final state

```text
lint · typecheck · build            exit 0
unit                                184   (config 6 · service-kit 3 · protocol 37 ·
                                           api 96 · dispatcher 8 · gateway 34)
integration                         188   (api 150 · dispatcher 16 · gateway 13 · e2e 9)
coverage                            363 passed, every ratchet green
sabotage                            7 mutations, 7 caught, files byte-identical after
tutorial: lint · build · docs · fences   exit 0
fence chain                         153 files across 23 chapters, 23 translated
chapter fences                      21   (R10 budget 18–22)
figures                             3 per locale, all SVG in a headless browser
```

`repository.ts` finished at 97.09 / 90.41 / 100 / 99.19 against a ratchet raised
to 97 / 90 / 100 / 99 — a tenth of a point of branch headroom, tighter than the
half point this chapter started with. The next chapter to touch that file should
expect to earn the raise before it lands.
