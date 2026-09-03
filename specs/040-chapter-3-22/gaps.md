# Chapter 3.22 — gaps

*Every item has an owner. Every reference names its chapter, because the numbers
collide: chapter 3.17's item 1 is a flake, 3.18's item 1 is the idempotency keys
and 3.21's item 1 is the inert module.*

**Chapter 3.21's items are carried and re-checked in the close-out (phase 11), not
copied here.** This file is opened in phase 9 because two items are findings of the
document work rather than of the code, and writing them down when they are found is
the only version of this that has ever worked.

---

## 1. EIR-WS-06 IS MET BY ONE CLOSE CODE OF SIX — NEW, OPEN, AND THIS CHAPTER WIDENS IT

The clause reads *"Close codes shall be documented and distinguish authentication
failure, quota exhaustion, server shutdown, and protocol violation"*, method:
inspection. Inspected, across the seven published documents and the one that is not:

    4001  invalid or expired token      docs/04-srs.md          x1
    4002  protocol violation            docs/08-error-reference.md  x2
    4003  banned in this environment    nowhere at all
    4004  connection limit reached      docs/08-error-reference.md  x1  (this chapter)
    4008  quota exhausted               docs/07-tutorial-plan.md    x2
    4009  server shutdown (drain)       docs/05-sad.md          x1

**The clause names four classes and the error reference documents one of them.**
Authentication failure appears in the SRS, server shutdown in the SAD — neither is
where a customer looks — and **quota exhaustion appears in no published document at
all**: `docs/07-tutorial-plan.md` is deliberately excluded from `sync-docs.sh`,
whose own comment explains why at length. `4003` is in none of the eight.

**This chapter takes the error reference from one of five to two of six**, which is
an improvement in the ratio and a widening in the count: a sixth code exists now and
four of the six are still undocumented where they are read.

**Owner: the next chapter that adds or renames a close code.** The remedy is five
lines and it is a decision rather than a drive-by, because it goes red the day it
lands: `check-error-codes.mjs` already reads `ERROR_CODES` from the built protocol
package and could read `CLOSE_CODES` beside it, requiring each close code to be
named somewhere in `docs/08-error-reference.md`. Whoever adds it owes the four
sections that make it green.

**Do not close it with a `## 4001` heading.** The same script's orphan check fails
on any `## ` heading that is not a member of `ERROR_CODES` — *"these sections name
no code in ERROR_CODES — remove them or the reference is lying"* — with no
exemption. The convention chapter 3.21 wrote is the one to follow: the close code
lives inside the `**Status:**` line of the error code that carries it.

**Two claims in this chapter's own task list were wrong about this and both were
measured rather than believed.** The task that asked for this item said
`sync-docs.sh` "publishes all eight docs" — it publishes seven, and the excluded one
is exactly where `4008` lives, so the argument got stronger rather than weaker. The
same task said `4001`, `4003`, `4008` and `4009` have "one mention each in the SRS
and the SAD"; the table above is what `grep` returns.

## 2. A PORT COLLISION WAS ELIMINATED BY A TEST THAT COULD NOT SEE IT — NEW, OPEN

Chapter 3.20's `gaps.md` item 19a lists three hypotheses measured and eliminated for
the battery's four unexplained failures. The second is *"a port collision (the
failing ports are in each file's own range)"*.

**The colliding port IS in each file's own range**, so that test cannot detect this
collision:

    presence.itest.ts     4700 + %200   ->  4700-4899
    meter.itest.ts  api   4710 + %60    ->  4710-4769

The second range sits strictly inside the first, and the gateway's integration
config sets no `fileParallelism`, so both files run at once. Neither range was on
the lane's port map in `limits.itest.ts` until this chapter added them — chapter
3.21's `gaps.md` item 4 called the map 78% complete, which counts the missing
entries without reading them.

**P = 1/200 per run.** The observed failure rate for those two files is 2.5-5%, so
this is a contributor and not the cause — and it is the first hypothesis in that
item with a number attached to it.

**Owner: the chapter that owns `presence.itest.ts` or `meter.itest.ts`.** Moving one
range is a two-character edit; it is not made here because it is another chapter's
change to another chapter's file, and because a number in `gaps.md` is what makes it
a decision rather than a tidy-up. The map is corrected in this chapter and says so
in its own comment.

## 3. AN EXCERPT-ONLY FILE IS STILL NEVER VERIFIED — CARRIED FROM 3.21 ITEM 7, OPEN

`limits.itest.ts` is titled in exactly one fence per locale, in **chapter 13**, and
both are `(excerpt)` — which `check-fence-chain.mjs:43` treats as its only skip. So
this chapter's edit to its port map costs nothing at the chain, and costs nothing
**because nothing checks it**: an excerpt-only file is never compared against the
repository at all.

**This chapter's task list got the citation wrong** and reached the right
conclusion anyway. It said the file is fenced by chapters 3.08 and 3.13 and that the
edit costs two regenerated diffs — inherited from chapter 3.21's item 4 and never
re-run. `grep` for the fence title returns chapter 13 twice, once per locale, both
excerpts. The chapter-08 hits are the path appearing inside an eslint config fence,
which is not a fence title for the file.

**Owner: unchanged from 3.21 item 7.**

## 4. `main.test.ts` CHECKS THAT A MODULE IS CLOSED, NOT THAT IT IS PASSED — NEW, OPEN

Chapter 3.21's first item is a module that was built, whose `close()` was awaited, and
which was never handed to `attachSessions`. The feature was inert in the product while
1,174 coverage tests and 174 gateway integration tests were green.

This chapter's answer to that item is two instruments, and **only one of them checks the
thing that broke**:

    main.test.ts   parses main.ts and asserts every create* module is CLOSED
    integrate.itest.ts   boots the shipped image and asserts the cap REFUSES a sixth

`main.test.ts` would have stayed green against chapter 3.21's exact defect — a module built
and closed and never passed. The outsider test is what catches it, and it is one test in one
package that needs Docker images rebuilt to mean anything.

**Owner: the next chapter that adds an `attachSessions` parameter.** The remedy is small and
this chapter did not take it: the same file already parses `main.ts` for `const x = createY(`
and could parse the `attachSessions({ … })` call for the same names, failing on a module
that is built but not passed. It goes red on the day it lands only if such a module exists —
which is the point.

## 5. THE RETRY-LOG BOUND IS NOW A FIVE-MODULE DECISION — CARRIED FROM CHAPTER 3.21 ITEM 3, OPEN AND WIDENED

Chapter 3.21's item 3 is FR-015's third clause — *"MUST be logged once with a stable event
name"* — against four fabric modules whose `error` listener logs once per reconnect attempt,
unbounded. `fanout.ts`, `presence.ts`, `membership.ts` and `typing.ts` share the shape.

**`connections.ts` is the fifth.** Its listener logs `connections.redis` on every error, for
the reason chapter 3.18's R10 gives: a client without an `error` listener turns a connection
error into an unhandled rejection that takes the process down. The listener is right; the
bound is still nobody's.

**Owner: unchanged — whoever bounds it, across all five.** Bounding it in one would diverge
from four.

## 6. FIVE FILES STILL DISCARD THEIR CHILD'S OUTPUT — CARRIED FROM CHAPTER 3.21 ITEM 9, OPEN, AND THE DECISION IS RECORDED

Chapter 3.21's item 9 is addressed to this chapter: fix them or record the decision. Re-checked
against the tree rather than copied:

    isolation.itest.ts        stdio: ["ignore", "pipe", "pipe"], nothing reads
    limits.itest.ts           stdio: ["ignore", "pipe", "pipe"], nothing reads
    public-surface.itest.ts   stdio: ["ignore", "pipe", "pipe"], nothing reads
    membership.itest.ts       stdio: "ignore"
    presence.itest.ts         stdio: "ignore"

`meter.itest.ts` is fixed and stays fixed: chapter 3.21 replaced its four `.resume()` calls
with a 300-line ring, and this chapter's own diagnosis of that battery's run 8 is why.

**The decision is NOT to fix them here, and the cost of fixing them is the reason.** Every one
is another chapter's file, and four of the five are in the fence chain:

    isolation.itest.ts        6 full fences, 2 excerpts
    public-surface.itest.ts   4 full fences
    presence.itest.ts         2 full fences
    limits.itest.ts           1 excerpt only — free at the chain, and unverified by it
    membership.itest.ts       no fences at all

So the fix is five copies of a ring buffer, twelve regenerated diffs, and five chapters shown
code they do not discuss — for a change none of those chapters is about. **This chapter is
also the wrong one to make it**: it added no spawning file, the lane's spawn count is still
seven, and its own battery is measured below with the five unchanged.

**Owner: the next chapter that spawns an api, or a tooling chapter that takes all five at
once.** The second is the better shape, and it is the same shape Part 6 is already promised
for the appendix's lint amendments.

## 7. COVERAGE STILL CANNOT SEE AN OMISSION — CARRIED FROM CHAPTER 3.21 ITEM 8, ANSWERED IN PART

`**/main.ts` is still excluded from the ratchet (`vitest.coverage.config.mts:97`), and
including it would still not have caught chapter 3.21's defect: every line executed, and the
defect was an argument that was not there.

**What this chapter added is the answer's first half**, and item 4 above is the half that is
still missing. The instrument that would have caught it — the sealed outsider — now covers
this feature: `holds five connections and is refused a sixth with 4004 (FR-RTM-09 (3.22))`
boots the shipped binaries and drives a browser `WebSocket` through a real api and a real
gateway. **It only means anything against rebuilt images**; run against stale ones it would
have tested chapter 3.21's code and passed.

**Owner: unchanged.** A chapter that adds an `attachSessions` argument owes an outsider test,
and now also owes item 4's check.

## 8. `sweep.py` AND `check-refs.py` STILL HAVE NO OWNER — CARRIED FROM CHAPTER 3.21 ITEM 6, OPEN, FOR THE FOURTH CHAPTER

Chapter 3.18's `sweep.py` died unowned; 3.19 recorded it as its item 8; 3.21 copied it again;
this chapter copied both and **improved one of them**, which is the argument for deciding.

`check-refs.py` was widened twice inside this chapter alone: once by chapter 3.21's own
lesson about `T\d{3}[a-z]?`, and once here, when it rejected a correctly-qualified citation
split across a line wrap — the second time that rule has been wrong about a healthy tree.
**Improvements made to a per-chapter copy are improvements the next chapter starts without.**

**Two candidates and no third**, unchanged from chapter 3.21's framing:

- They graduate to `relay-tutorial`'s `check:*` scripts, as the first instruments there that
  compare a claim across two documents rather than validating one. Cost: they would run on
  every chapter's records, and the first run would be red on the older `specs/` directories,
  which is a decision about scope rather than a bug.
- They stay per-chapter copies, and this file says that is a decision rather than the default
  nobody chose.

**This chapter records the second, and records that it is the fourth chapter to do so.** The
per-chapter copy is what makes an instrument free to change mid-chapter — this chapter changed
it twice and neither change could have broken another chapter's record. That is a real
property and it is the only argument the copies have ever had; it is written down here so the
fifth chapter can weigh it instead of inheriting it.
