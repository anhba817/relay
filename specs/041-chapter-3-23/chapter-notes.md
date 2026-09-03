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
