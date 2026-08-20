# Chapter 3.8 — notes

Written from what happened. The plan is in `plan.md`; this is the difference.

---

## It became two chapters, and the number decided

The scope call at `/speckit-specify` was one chapter carrying both the limiter
and the email transport chapter 3.6 deferred. The phase order put the transport
**last** so the size gate could be run with a real measurement instead of an
estimate — and that is the only reason this went differently from 3.5 and 3.6,
both of which discovered they were oversized after shipping.

The limiter half alone measured **4,700 prose words** against a 2,000–4,000
bound, with the transport's sections unwritten. Adding them reached roughly
6,300, past 3.6's 5,346 and past anything the series has published. So the
transport's prose became chapter 3.9, quotas moved to 3.10 and the gauntlet to
3.11.

Two things worth separating. The **code** shipped either way — it closes
FR-WHK-07 whichever chapter explains it, and both chapters point at the same
tree. And 3.9 was written in this cycle rather than deferred, because deferring
it would have put about a dozen files into `fences/post-series.md`, a file whose
purpose is small amendments no chapter teaches, not a subsystem.

R10 recommended this split when the chapter was planned. It was overruled by the
scope decision and then confirmed by a measurement, which is the first time an
R10-style size warning in this series has been checked rather than absorbed.

3.8 still shipped at **4,781 words**, 780 over the bound. Six tightening passes
took it from 4,700 to 4,499 and the last three returned about forty words each;
T053's and T063's corrections then added 280 back. What remains is not padding —
three findings from the sabotage battery at 150–250 words each, and the two
failure directions the chapter is named for.

---

## What the work found that the plan did not

**A limiter that counted nothing.** `req.url` is `/` inside a middleware mounted
at the app root, because Express rewrites it relative to the mount point. The
same bug turned out to be in `RequestContextMiddleware` — so every structured log
line since chapter 2.2 recorded `path: "/"`. Nothing failed and no test noticed,
because a bug in an observability field is invisible by construction.

**A header that contradicted its own body.** Captured for the chapter, not caught
by a test: a 429 printed `X-RateLimit-Limit: 3` above "too many messages" on an
environment whose send limit was 2. Both budgets reach zero remaining while only
one is over, and the tie went to the wrong one. Eighteen integration tests
covered that middleware; each asserted one field and nobody had looked at a whole
response. Research R41.

**A tenant-isolation test that was not testing tenant isolation.** The mutation
that shares one counter across environments left it passing. It asserts a
consequence that survives the fault it is named after. What caught the mutation
was T017a — added at the eighth analysis pass on a reading of the journey map,
with no mutation to point at. An argument for the analysis passes, not just for
the battery. Research R42.

**A mutation that could not fail.** The transport's batch was one transaction, so
a throwing send rolled back the `finally`'s mark and made the send/mark ordering
unobservable. Behind it: rows are claimed oldest-first, so one permanently
undeliverable address blocked the entire notification queue for ever. Per-row
isolation fixed both. Research R44 — the best thing the battery produced.

**The lane's failed-auth isolation was two address formats.** T004a measured it:
`credentials.itest.ts` and `signup.itest.ts` raise the threshold to 10,000 and
kept the default key prefix, pushing a shared bucket to 8 and 13 against a
threshold of 10. Nothing was refused only because those suites reach the api over
`::1` while the child-spawning ones use `::ffff:127.0.0.1`. Both now take their
own prefix.

---

## Three times a rule failed the person who wrote it

**`git checkout --` ate the fix.** T037 says commit before the battery, in bold,
because 3.6 lost a correction to the revert step. It happened again — to a fix
written *during* the battery, in response to a mutation that had just passed.
"Commit before the battery" is satisfiable once and the battery is a loop. The
quickstart now says **before every mutation**. Research R45.

**The comment about stale chapter numbers went stale.** Chapter 3.7 wrote a
comment in `schema.ts` explaining that a chapter number in source is a reference
that ages, and made its point by listing the ordinals the gauntlet had passed
through. The plan moved again while this chapter was being written. It now names
none.

**The sweep this chapter must not run, it ran.** Five instances of "a test
asserting a local fact about a global operation" were inherited. The sixth was
written here, from scratch, by someone who had recorded the other five and cited
them in the chapter — because `sweepDisabledEndpoints` was the most honest-looking
way to drive the real disablement path, and nobody checked its scope. Research
R46.

There is a pattern in those three and it is not carelessness. Each rule was known,
written down, and cited. What defeated them was that each was stated for a
situation slightly narrower than the one it met.

---

## Where the numbers landed

|  | before | after |
|---|---|---|
| unit tests | 229 | 242 |
| integration tests | 213 | 223 |
| coverage, statements | 86.55% | 89.50% |
| coverage, branches | 78.07% | 82.73% |
| fenced files in the chain | 165 | 165 |

Coverage went **up** for a chapter that added ten files, which is not the usual
direction. `bucket.ts`, `policy.ts` and `fallback.ts` are at 100 on every metric;
`fallback.ts` earns that because it is the mechanism the auth limiter degrades to,
and an unmeasured branch in it is a hole in the thing the chapter is about.

The renumbering cost **no new fence amendment**. One file needed a comment
corrected and it was already being amended for other reasons — so 3.7's
"cite what a thing is, never where it will be" rule paid for itself, with the
caveat that the comment stating the rule was the thing that had aged.

---

## What is still owed

- `docs_url` resolves to nothing, and this chapter ships the first error code a
  working integration meets routinely. Stated in the chapter rather than left for
  a reader to find by clicking.
- SRS Appendix C question 5 is still open, and this chapter closed off the shape
  that would have answered it: the policy has a slot for an environment and none
  for a route.
- Close codes `4008` and `4009` are declared and emitted by nothing, on purpose,
  with a test that says so and can fail.
- The connect limit and NFR-REL-03 half agree until something builds a drain.
- Whether `drainOutbox` has the head-of-line problem its neighbour just had is a
  real question this chapter does not answer.
