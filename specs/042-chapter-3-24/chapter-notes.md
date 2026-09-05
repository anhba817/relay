# Chapter notes — 3.24, the message that is not only text

## THE TWO FILE COUNTS ARE A PRACTICE, AND NEITHER DOES THE OTHER'S JOB

    what the chapter TEACHES     what it must FENCE
    ------------------------     ------------------
              8                            29

**Teaches — 8.** The files a reader has to see to follow the argument:

    packages/protocol/src/attachments.ts        the shape, the bound, the two arms
    packages/protocol/src/frames.ts             the required field, and the socket door
    packages/protocol/src/internal.ts           the internal hop, both directions
    services/api/src/messages/messages.schema.ts   the REST door and the pair rule
    services/api/src/db/repository.ts           the INSERT, the reads, MessageRow
    services/api/src/messages/messages.controller.ts   two payloads and a response
    services/gateway/src/session.ts             the three points a socket send drops
    services/api/src/outbox/event.ts            one payload type for two events

**Fences — 29**, measured rather than listed: every file this chapter touched that already
has a chain in an earlier chapter. `check:fences` is red on exactly those 29 until the fences are generated, and
`comm -23 <red> <touched>` is empty, which is what says none of them is a real failure.

**Seven touched files stay unfenced**, and that is a choice rather than an omission:

    attachments.ts, attachments.test.ts      NEW — no chapter has fenced them, and this
                                             one teaches `attachments.ts`, so it fences it
    fanout.itest.ts, publisher.test.ts       fenced by nobody, and 3.23 recorded that
    event.test.ts, idempotency.itest.ts      test files this chapter changes but does not
    session.itest.ts                         discuss; fencing them would add lines the
                                             chapter never explains

The count that drove the word estimate is **8**. The count that drives the chain is **29**.
Chapter 3.23's record says 33 became 34 during close-out because the coverage ratchet edited a
fenced file — the coverage ratchet in phase 12 is where that can happen here, and phase 12's own header warns about it.

## THE WORD ESTIMATE, FROM ARGUMENTS

**545 words per argument, and stop adjusting for what the argument is against.** Chapter 3.22
estimated from arguments and came in 21% over at 583 each; 3.23 predicted 420 on the theory
that arguing against published material costs more, and came in at 545 — a 9% drop where the
model predicted 28%. The instruction is to use 545 and stop modelling the subject.

**Nine arguments**, and naming them is the point:

     1  A required field is worth four production sites and 29 test ones — and the three it
        cannot name are the ones that cost the most, because `parse` takes `unknown`.
     2  NULL and `[]` are different values, and exactly one place converts.
     3  The socket path drops a field at three named points, none of which errors.
     4  A rule expressed per-schema is a rule some door does not have — three schemas, one
        definition.
     5  `media_id` is in the published contract, so refusing it as `invalid_request` would
        send a developer to check JSON that is correct.
     6  A controller cannot refuse what the validation pipe already threw on.
     7  An edit changes text; the event still carries what the message has, which is why a
        read nobody expected to change did.
     8  A deletion's payload carries no attachment field for the reason it carries no text.
     9  Two doors, two codes, one bound — and a test that asserts only "it was refused"
        cannot tell a working bound from a dropped field.

    9 x 545 = 4,905 words, and the estimate is that number rather than a range.

3.23 came in at 3,269 words for six arguments (545 each). This chapter has nine.
