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
