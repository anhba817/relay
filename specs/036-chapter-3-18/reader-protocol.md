# The reader protocol — what T058 needs a person for

Chapters 3.14, 3.15, 3.16, 3.17 and now 3.18 have each named this gap. **3.18 did not close
it either.** What is different is that it is written down as something a person can be handed
in one sitting, with a place to record the answer, instead of a sentence in a close-out note.

The criterion it serves is the SRS Phase 2 exit criterion's harder half, which 3.12 stated as
**content sufficiency is not comprehensibility**. No test reaches it. Every check in this
repository compares bytes: `check:fences` compares a fence to a file, `check:srs` compares an
id to a table, `prose-words.mjs` counts words. None of them can tell whether a chapter is
comprehensible to somebody who has not read the plan that produced it.

## Who

One engineer who has **not** read `specs/036-chapter-3-18/`, has not seen this chapter's
diffs, and ideally has not read chapters 3.12–3.17. They do not need to know Relay. They do
need to read TypeScript.

Not the author. The author cannot un-know the plan, and that is the whole failure mode: the
sealed outsider package was wrong about the API for two chapters because nobody outside ran
it, and a published Trap contradicted 3.17's own chapter through fifteen analysis passes
because no checker reads prose.

## What they get

The published chapter at `/part-3/chapter-18/the-message-that-never-arrived`, and nothing
else. No spec, no tasks, no plan, no `chapter-notes.md`. If they need the platform source to
answer a question below, that is the finding — write down which question and stop.

## Time box

45 minutes reading, 15 minutes answering. If they run over, record where the clock ran out;
that is more useful than a complete answer taken at leisure.

## The six questions

Answered in their own words, without quoting the chapter back:

1. **Before this chapter, what happened when a message was sent over REST?** (The expected
   answer names two things: it committed, and nothing published.)
2. **Which requirement did the platform fail to satisfy, and where is it written down?**
   The chapter cites FR-RTM-01 and states that no SRS clause changed. A reader arriving from
   3.17 — where the amendment *was* the gate — is the specific person most likely to go
   looking for an amendment and not find one. **If they say FR-RTM-05, the chapter has not
   done its job**: that is the misattribution `docs/07-tutorial-plan.md` carried from 3.14 to
   3.18, and correcting the row does not correct a reader.
3. **Why does the api publish rather than the gateway?** The chapter has to answer this
   against ADR-07's "clean mapping — gateway to Redis, api and workers to NATS", which the
   chapter's own amendment says stopped being exactly true in chapter 3.8.
4. **What happens to a send when Redis is down, and how would you know it happened?**
   The answer is: the send still returns 201, and the only evidence is a log line. If they
   say "the send fails" or "you would see an error response", the chapter's account of
   FR-010/FR-011 has not landed. This is the chapter's most load-bearing claim, because the
   publisher swallows its own errors — a publisher that does nothing at all satisfies every
   weaker assertion.
5. **A member is removed from a channel while their socket is open. Do they still receive
   messages?** The honest answer is yes, they do, and the chapter says so. A reader who
   reports this as a bug in the chapter has read it correctly and is reacting to FR-RTM-10
   being pinned as unmet — record that reaction, it is the intended one.
6. **What did this chapter NOT do?** Presence, FR-RTM-05's other five event kinds, and
   FR-RTM-10's five-second window. All three are in the chapter's `<ForwardRef>`.

## What to record

In `chapter-notes.md`, under a heading naming the reader and the date:

    - every question they could not answer from the chapter alone, verbatim
    - every place they had to open the platform source, and what they were looking for
    - anything they read as a contradiction, whether or not it is one
    - the two or three sentences they had to read twice

A reader who answers all six is a result worth recording too — five chapters have assumed it
without evidence.

## What this protocol cannot do

It measures one person on one chapter. It cannot tell you whether the series reads as a
series, which is the version of this question chapter 4.1 will face with thirty-five chapters
behind it. And a reader recruited by the author is not the external developer the criterion
names; they are the closest available approximation, and the gap between the two should be
recorded rather than rounded off.
