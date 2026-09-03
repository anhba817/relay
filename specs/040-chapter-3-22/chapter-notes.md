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
