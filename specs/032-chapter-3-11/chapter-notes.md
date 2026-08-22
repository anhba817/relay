# Chapter 3.11 — what the plan said, and what shipped

Written before the page, so the page has something to be honest about.

## The shape held

Connection-minutes are metered by the gateway, recorded by the api, capped at the
socket door, and FR-RTL-05 is closed on all three dimensions. The unit is a
wall-clock minute bucket charged per connection; reports carry totals rather than
deltas; the gateway gained a credential and no database. All of that is what
research settled and none of it moved.

## Where the plan was wrong

**R7 chose the wrong shape, and only a measurement said so.** It reasoned that
chapter 3.10's H2 forbade putting a usage join in `environmentLimits`, so the cap
should be "a second call on the same request rather than a heavier version of the
first". H2 is still right — `environmentLimits` has a second caller, the
rate-limit middleware, on every `/v1` request. But two calls cost what a join
would at concurrency: **15.0 ms to 17.6 ms at 32-way**, four runs clustered inside
0.7 ms. Folding the connect path into its own single read recovered 0.8 ms.
`environmentLimits` is untouched.

**R23 predicted `repository.ts` would go red and it went up.** Branches moved
90.17 → 90.57 against a ratchet of 90. The prediction was built on chapters 3.5
and 3.6, where the same file lost 7.69 and 1.20 points. The difference is not
luck: 3.5's new functions were reachable only from a suite that spawns the api as
a child, whose coverage is not attributable, so they arrived measured at zero.
`creditConnectionMinutes` is exercised by nineteen in-process tests, which is
exactly what T033b scheduled and T033d protected.

**Chapter 3.10's cost prediction was light.** It wrote, twice, that a third
dimension is "a new key plus a one-line constraint change". It is seven places,
and two of them it did not anticipate at all — including the one that mattered.

**T004a's method was wrong.** One measurement is not a baseline. The instrument
existed specifically to avoid chapter 3.10's uncontrolled-benchmark mistake, and
then it was used once, so the residual gap after the fold cannot be attributed.

## What only the battery could find

Three defects, none of them findable by reading, two older than this chapter.

**A fixed api port, wearing three disguises.** `startApi()` bound 4123 and the new
describe bound 4124 — `limits.itest.ts`'s. Vitest runs files in parallel. Worse,
back to back the previous run's child still holds the port, the new child dies on
EADDRINUSE, and `waitForHealth` gets its 200 from the OLD api with another
environment's signing secret. Three assertions failed and none named the fixture:
`expected 'internal_error' to be 'unauthorized'`, `expected 1011 to be 4001`, and
`TypeError: fetch failed`.

I diagnosed it wrong twice first, and both wrong theories reached comments before
the evidence arrived. What settled it was running one file alone five times — 2 of
5 red — which killed every cross-file theory in one measurement and should have
been the first move rather than the fifth.

**An eleven-chapter-old flake, surfacing on run twenty-one.** `credentials.itest.ts`
took an api key's secret as `credential.split("_").at(-1)`. `api-key.ts` explains
why that is wrong three lines from its own regex: base64url includes the
separator. Once in a while the last segment is a single character the stored row
contains by chance.

**My own test budget.** Six Mailpit tests waited through a 10 s helper inside a
5 s timeout.

## What chapter 3.10 left behind, and this chapter paid

Two tripwires. One was scheduled: `session.test.ts`'s "STILL emits close code
4008 from nowhere", which went red the moment `session.ts` emitted it. The other
was not: `config.test.ts` asserted `connection_minutes` is rejected "until then",
and seven analysis passes missed it because the fence table lists `config.ts`, not
its test. A red test found it in Phase 2.

And one gap: `drainQuotaNotifications` was on neither the lint restriction list
nor `exempt.ts`, whose comment says the two must agree. Added, with a comment
saying what it does not buy — this chapter's own email tests reach the drain
indirectly, where the rule cannot see.

## The page

  prose words         3,324      gate 2,000–4,000, estimate 3,000–3,600
  fences              34         25 on the page, 4 in post-series
  boxes               4 Why, 4 Trap, 1 Checkpoint, 1 ForwardRef
  figures             4          gate 2–4, ≥1 per half
  mirror              68 fence delimiters each side, bodies byte-identical

Inside the estimate, which is a first for this part. Phase 7 was sequenced last so
it could be cut and did not need to be.

## The numbers

  unit                286 → 348
  integration         256 → 330
  coverage            89.45/82.73/88.94/90.86 → 90.32/83.98/89.51/91.53
  battery             20/20 green, 330 every run, 193.30 s mean, 3 s spread
  guard refusals      0, with the guard verified armed and able to fire
  connect path        6.807 ms → ~6.4 ms at 1-way; 15.0 → 16.8 at 32-way
  dimension cost      7 places against a written prediction of 1
  fence surface       21 files, 95 chapter fences, 5 post-series entries
  chain               177 fenced files, 28 chapters, 28 translated

## What was left undone, on purpose

- **The guard does not watch the four usage tables.** Recorded with the `OLD.id`
  problem that makes the extension more than an array change, and owned by
  whichever feature next touches `packages/test-harness/`.
- **`limits.itest.ts` still binds a fixed port**, with the same lingering-child
  exposure that broke `session.itest.ts`. Another chapter's fenced file, currently
  green.
- **`CLOSE_CODES[4009]` stays unemitted**, in the chapter that gave the gateway
  its first shutdown path. Draining is a feature with its own semantics.
- **`docs_url` still resolves to nothing** for `quota_exceeded`, as it has for
  `rate_limited` since chapter 3.8. Inherited, not compounded; chapter 3.12's.

## Seven analysis passes, and what they were worth

  pass 1   documents + the published series    19 findings   1 CRITICAL
  pass 2   the code                            13           1
  pass 3   the build gates                     11           1
  pass 4   the numbers                          9           0
  pass 5   the governing documents              9           0
  pass 6   task executability                   7           0
  pass 7   the sixth pass's edits               2           0

Seventy findings, three CRITICAL, all three in the first three passes. From the
fourth onward the majority of what each pass found was what the previous passes
had written, and the seventh found nothing else at all — which is what running out
of reading looks like.

Implementation then found seven more things reading could not have: two of chapter
3.10's tripwires, three defects in the battery, one wrong plan decision corrected
by a benchmark, and one comment in a shipped chapter that had quietly stopped
being true.
