# Chapter 3.22 — notes

## The two counts, kept apart

Chapters 3.15 and 3.16 revised one conflated count eight times. Chapter 3.17 kept two
columns and neither number was ever asked to do the other's job. Three columns here,
because this chapter has a third that differs from both.

    10   what the chapter TEACHES        -> drives the word estimate
    11   what the chapter must FENCE     -> drives the chain
    13   files CHANGED in the platform   -> re-derived from `git diff` in phase 11

**The three differ for reasons worth stating.** Two changed files are taught but not
fenced by this chapter — `limits.itest.ts` and `session.itest.ts` are titled only as
`(excerpt)`, which `check-fence-chain.mjs:43` treats as its one skip, so their edits are
free at the chain and unverified by it. One file is fenced and barely taught:
`presence.itest.ts` changed by one line and appears in the chain because it is in the
chain, not because the chapter has anything to say about it.

**The fence list, measured rather than assumed.** Eight files are already in the chain and
have drifted — the eight `[HEAD]` anchors `check:fences` reports — and three are new:

    eslint.config.mjs                          drifted (amended by the appendix)
    packages/protocol/src/codes.ts             drifted
    packages/protocol/src/codes.test.ts        drifted
    packages/outsider/src/integrate.itest.ts   drifted
    services/gateway/src/main.ts               drifted
    services/gateway/src/main.test.ts          drifted
    services/gateway/src/session.ts            drifted
    services/gateway/src/presence.itest.ts     drifted
    services/gateway/src/connections.ts        new
    services/gateway/src/connections.test.ts   new
    services/gateway/src/connections.itest.ts  new

Phase 11 adds a twelfth, `vitest.coverage.config.mts`, when the ratchet is pinned — which
is why phase 10's fence run is not the last one.

## The word estimate, from arguments

**Prose tracks the number of arguments a chapter makes, not the number of files it
touches.** Chapters 3.15 and 3.16 agreed on 153.5 and 154.3 words per taught file to within
1%, and 3.17 came in at 84.7 — 45% below — because it taught sixteen files to make one
argument.

This chapter makes **five**:

1. **Where a refusal goes.** A browser cannot read the body of a failed upgrade, so the
   handshake completes in order to be closed.
2. **Why a sixth close code.** All five existing ones send a client to the wrong remedy,
   and this is the only refusal in the set whose correct handling is not a retry.
3. **Why five keys and not the sorted set the SAD published.** Atomicity, Lua, and evidence
   this lane cannot gather.
4. **Why failing open is right for a cap and wrong for a lock.**
5. **What a connection does when it loses its place.** Added by analysis pass 5 with
   FR-011b, and the one that carries the FR-005 tension a reader would otherwise trip over.

**Estimate: 2,400 words, ±400.** The basis is the predecessor rather than a rate per file:
chapter 3.21 made five arguments in 2,181 prose words, measured by `scripts/prose-words.mjs`
— 436 words each. Five arguments here, heavier on argument and lighter on code paths, so
the same order with a little more room. The actual is recorded in phase 11 beside this
number, whichever way it goes.

**The first version of this count said four.** It was written before FR-011b existed and
never re-derived, which is this chapter's most common single defect one level up.

## The widest seam in the gateway, and nobody has named a limit

`attachSessions` now destructures **fourteen** named parameters, and the task list said
nine. Both are right about different sets, and the difference is worth keeping:

    9   MODULES        server api logger fanout limits presence membership typing
                       connections          <- this chapter's, up from eight
    5   TUNING KNOBS   pingIntervalMs resumeDeadlineMs meterIntervalMs
                       renewalIntervalMs heartbeatMs   <- heartbeatMs is this chapter's

Constitution VII's "boring by design" governs services rather than parameter lists, so
there is no violation to report. But this is the widest seam in the gateway and **no
document names a point at which the list becomes an options object**. Naming one:

**When a caller has to read the function's source to know which parameters are optional.**
Every module here is optional and every fixture passes a different subset — this chapter's
own integration file passes five in one test and seven in another. That is already true, so
the threshold has already been crossed and the answer is that nothing is done about it,
deliberately: an options object would be the same fourteen names one level deeper, and the
cost of the change is every call site in twenty-two chapters' fences.

**The real limit is the one the previous chapter found.** A parameter that is not passed is
invisible — no type error, no lint error, no coverage gap — and chapter 3.22's `gaps.md` item 4 says the
instrument that would see it does not exist yet. The list's length is not what hurts; its
optionality is.

## What shipped

    the module         services/gateway/src/connections.ts, 100/100/100/100
    the seam           the claim after authenticate and after the limiter, the
                       refusal inside handleUpgrade
    the protocol       close code 4004 and error code connection_limit_reached
    the wiring         main.ts builds it, passes it, and closes it
    the documents      ADR-23 in both homes, both SAD `conn:` rows, the SRS
                       revision row, the error reference, the chapter table
    40 new tests       17 in connections.test.ts, 20 in connections.itest.ts, and
                       one each in session.itest.ts, main.test.ts and
                       integrate.itest.ts — plus two CHANGED in codes.test.ts,
                       which are not new and are not counted here

## The five arguments, and how they came out

1. **Where a refusal goes** — settled by reading chapter 3.11's `session.ts:715` rather
   than deriving it. A browser cannot read the body of a failed upgrade.
2. **Why a sixth close code** — settled by `codes.ts:10`'s own test, which all four
   candidate reuses fail.
3. **Why five keys and not the published sorted set** — the only argument this chapter had
   to make from scratch, and the one that needed an ADR. It shipped with a **false driver**
   in its first draft and the decision survived it.
4. **Why failing open is right for a cap** — Principle IV, and the log line is the whole of
   the evidence.
5. **What a connection does when it loses its place** — added by analysis pass 5 with
   FR-011b, and it carried the FR-005 tension the other four would have left a reader to
   trip over.

## What went wrong

- **The hand-off assigned a decision that had already been published.** Three of the four
  design decisions were in the tree; reading beat deriving by about a day.
- **A flaky test was a product defect.** 2 runs in 6, reported as `no connection.ack within
  5s`, and the message was true of a socket refused 4004 half a second earlier. `releaseAll`
  tombstoned all five places and the walk stepped over every one.
- **A falsification said "not observable" and was wrong**, because the test that could see
  the race had not been written yet.
- **Three task premises were inherited from a predecessor's record and never re-run**: the
  fence cost of `limits.itest.ts`, `sync-docs.sh`'s document count, and which test catches
  `IFEQ` becoming `XX`. This is the chapter's single most common defect.
- **Two of my own comments were backwards** and were corrected by measurement rather than
  by review: the before-the-bound test's TTL argument, and an assertion that pinned a slot number the
  one-millisecond tombstone cannot guarantee.
