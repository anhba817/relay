# Chapter 3.23 — notes

## THE TWO FILE COUNTS, KEPT AS TWO COLUMNS

The practice 3.17 established and 3.20/3.21/3.22 kept: **neither number is ever asked to do
the other's job.**

    what the chapter TEACHES      9   -> drives the word estimate
    what the chapter must FENCE  33   -> drives the chain
    files changed                36   re-derived from `git diff` against
                                      `git rev-parse part3-ch22^{commit}`, +3869 -64

**The nine it teaches**, which is the list the prose is built from:

    packages/protocol/src/revision.ts            the fifth subject grammar (ADR-24)
    packages/protocol/src/codes.ts               two codes, and why not `forbidden`
    packages/protocol/src/frames.ts              `message.deleted`'s own payload
    services/api/migrations/0014_message_edits.sql   the table the SAD published
    services/api/src/db/schema.ts                and its TS twin
    services/api/src/db/repository.ts            `editMessage`, `deleteMessage`
    services/api/src/messages/messages.controller.ts   three routes, three declarations
    services/gateway/src/session.ts              the kind comes off the payload now
    services/api/src/db/catalogue.ts             the check that only counted one hop

**The thirty-three it must fence** = 30 paths already in a chain that this chapter changed,
plus 3 new files it teaches. Three changed files stay UNFENCED because no chapter has ever
fenced them, and this one does not teach them either:

    services/api/src/fanout/fanout.itest.ts       559 lines
    services/api/src/outbox/event.test.ts         413 lines
    services/gateway/src/session.itest.ts       1,279 lines

**33, not 36.** Fencing them would add 2,251 lines the chapter never discusses, which is
exactly what fence-chain rule 6 warns about — *"prose fences are not the chain's requirement"*
— pointed the other way.

## FENCE EXPOSURE, PER FILE

    30 diff fences                                     3,951 lines
     3 whole-file fences (revision.ts, its test, 0014)   221 lines
    total the chapter owes                             4,172 lines

The five heaviest are the ones to watch, because a diff fence that large is a chapter showing
a reader more code than it can discuss:

    services/api/src/db/repository.itest.ts     577
    services/api/src/db/repository.ts           567
    services/api/src/messages/messages.itest.ts 561
    services/api/src/messages/messages.controller.ts 288
    services/gateway/src/session.test.ts        208

**Every one of the 30 lives in a CHAPTER's chain, not in `fences/post-series.md`** — checked
rather than assumed, which is the check chapter 3.22 lost half a phase to. Three of them are
carried by `post-series.md` as well (`repository.ts`, `resume.itest.ts`,
`deliveries.itest.ts`), so their chains end there and this chapter's hunks must apply after
that file's.

The predecessor is `23a85c5e3d5f6d0dc1d80fd41b9701daa450bf56`, which is
`git rev-parse part3-ch22^{commit}` and **not** the tag — `part3-ch22` is annotated.

## THE WORD ESTIMATE, FROM ARGUMENTS

3.15 and 3.16 agreed on ~154 words per taught file and 3.17 came in at 84.7, because prose
tracks the number of **arguments** a chapter makes and not the number of paths it touches.
3.22 estimated 2,400 from five arguments and wrote 2,914 — 21% over — and its own note said
why: three of its five argued against something already published, which costs more words
than arguing for something new.

**This chapter's arguments, counted before writing:**

    1  A kind that cannot share a payload type cannot share a subject.        (ADR-24)
       The fifth grammar, and why widening `chan:`'s payload was refused.
    2  `forbidden`'s published remedy is advice nobody can act on when the
       fact is authorship. Two codes rather than one.
    3  A cursor orders creations, so it cannot address an edit — and the
       absent GAP is what makes that invisible. Slack, Matrix, IMAP.
    4  A published DDL is a decision until an ADR supersedes it: three
       columns and a composite key, and what the key costs.
    5  The check that only counted one hop. Reachability is not adjacency.
    6  Two 204s prove nothing; the event count carries idempotence.

Six arguments. **Two of them argue against something published** — the data model's invented
`id` column (4) and the contract's 404 for a tombstone edit — which is a smaller fraction
than 3.22's three of five, so the rate should fall between 3.22's 583 words/argument and
3.17's leaner figure.

    estimate  2,400 - 2,700 words, from six arguments at ~420 each

Recorded before writing so the check is a check.

## WHAT THE CHAPTER ACTUALLY CAME TO

    prose words, en    3,269     predicted 2,400 - 2,700
    prose words, vi    4,236     Vietnamese runs longer; every chapter's does
    fenced files         240     predicted "rises from 237" — +3, the new module,
                                 its test, and the migration
    fences in the page    34     33 at the end of the chapter phase, and a 34th after
                                 close-out edited `vitest.coverage.config.mts`
    figures              254     +8, four per locale
    page lines, en     4797
    page lines, vi     4803

**THE WORD ESTIMATE WAS 19% TO 33% LOW, AND THE HYPOTHESIS BEHIND IT WAS WRONG.**

The prediction reasoned that this chapter argues against something published in only two of
its six arguments, where 3.22 did so in three of five, so the per-argument rate should fall
below 3.22's 583. It did not fall much:

    3.22   five arguments,  2,914 words   583 per argument
    3.23   six arguments,   3,269 words   545 per argument

**545, not the ~420 predicted.** The "arguing against published material costs more" reading
holds directionally and is far weaker than the estimate assumed — a 9% drop where the model
predicted 28%. What the two chapters actually share is a floor of roughly 545 to 580 words per
argument, whatever the argument is about, and the honest reading is that **an argument costs
what it costs**: setting up the alternative, saying why it was refused, and showing the
evidence takes about the same space whether the alternative was somebody else's or nobody's.

The next chapter should estimate at **545 words per argument** and stop adjusting for what the
argument is against.

## THE EXPECTED FIGURE COUNT WAS STALE BY FOUR

The fence-and-figure task said to expect the figure count to rise from **242**. Measured at `part3-ch22`:
**246**. The fenced-file baseline in the same sentence — 237 — was right.

Not worth chasing where the four came from; worth recording that **a number carried into a
task from a predecessor's record was wrong for the fourth time in this chapter**, and that the
task said "rise from" rather than "be", so it passed anyway. A prediction stated as a direction
survives a stale baseline; one stated as a value does not.

## THE VIETNAMESE MIRROR HAD TO REUSE THE ENGLISH FENCES, NOT REGENERATE THEM

The first attempt ran the same generator against the tree for both locales and produced three
`[APPLY]` failures plus a `[MIRROR]` one:

    diff for packages/protocol/src/revision.ts with no earlier fence to amend

**Because the English page had already been written.** The generator asks "does any chapter
already fence this path?" to decide between a whole-file fence and a diff — and by the time it
ran for Vietnamese, the answer for `revision.ts` was yes: the English chapter fenced it. So it
emitted a diff of the file against itself, with nothing to amend.

The fix is what the translation task asked for in the first place — **split on the fence regex and reuse the
English blocks verbatim** — which makes the mirror byte-identical by construction rather than
by review. Recorded because the generator is the obvious thing to reach for twice, and the
second reach is wrong for a reason that only shows up after the first one succeeds.

## THE FILE COUNT MOVED IN CLOSE-OUT, AND THAT IS WHAT PHASE 12'S WARNING IS ABOUT

    at the end of the chapter phase   36 files, 33 fences
    re-derived at close-out           37 files, 34 fences

`vitest.coverage.config.mts` joined because the ratchet fired, and it is a fenced file — so
this chapter's diff for it had to be generated and a thirty-fourth fence added to both
locales. **Phase 12's own header says this in advance**, which is the reason it was cheap
rather than a surprise: *"any late edit forces this chapter's diff for that file to be
regenerated before the gates run — not a predecessor's."*

Six test files also changed during close-out, when the title audit stripped 52 task ids out of
test names. Those regenerate the same way, and the generator's idempotence fix is what made
the second regeneration a one-line command.

    37 files changed, 3,976 insertions, 72 deletions
