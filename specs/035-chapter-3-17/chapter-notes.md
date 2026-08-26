# Chapter 3.17 — the plan against what shipped

One feature, one chapter, 153 tasks, sixteen analysis passes. The chapter's claim is one
sentence: a message sent by a customer's server had no sender, and now it has one the customer
chose. Most of the work was not the sender.

## What shipped

    3.17 "the sender a message never had"    16 files taught, 2,962 words, 27 fences
                                             + 7 files changed and claimed by no chapter

    589 integration tests, 25 of 26 full-lane runs green, mean 193.55 s, stdev 0.99
    coverage: repository.ts branches 91 -> 92, functions 100% (115/115)
    212 fenced files across 34 chapters, 34 translated · 212 figures · 91 static pages
    the sealed outsider 11/11, following the README

## THE FILE COUNT DID NOT MOVE, and that is the headline

The last feature revised its file count eight times and the eighth revision was the one that
mattered: what a chapter teaches is not what it must fence. This feature kept two columns from
T080 to T085:

    16   what the chapter teaches      -> drove the word estimate (185 words/file)
    27   what the chapter must fence   -> drove the chain
    35   files changed, re-derived from `git diff` at the end
    35   what T080 said before a word was written

**Neither number was ever asked to do the other's job**, and the re-derivation agreed with the
prediction. The word estimate came from 3.16's measured rate rather than the nominal one, and
landed at 2,962 against a 2,000–4,000 bound.

## SIXTEEN ANALYSIS PASSES, AND WHERE EACH CRITICAL CAME FROM

    pass    CRITICAL  source
    1-2        4      artifacts read against each other
    3-4        2      asking the repository a yes-or-no question
    5          1      checking a task's premise
    6          1      a question the previous pass wrote down and did not act on
    7          2      running the command a task tells someone to run
    8          1      following a constraint into the paths that can reach it
    9          2      auditing the gate task itself
    10         2      reading the authority that was being quoted
    11         0      structural checks: [P] markers, id order, phase dependencies
    12         0      coverage in the reverse direction
    13         1      reading a section's CLAUSES instead of its identifiers
    14         1      the same, applied to all seven cited families
    15         1      the published prose, which no checker reads
    16         0      nothing consequential

Twenty CRITICALs. **The two most expensive findings came from reading a governing document's
clauses rather than its identifiers** — FR-MSG-13, which had required this chapter's capability
since v1 and had been satisfied backwards for eleven chapters; and FR-TEN-08, cited three times
as the billing authority when it governs application deletion.

**Pass 12 recommended stopping and was wrong.** It reasoned from two passes of falling yield,
which measures the questions being asked rather than the defects present — an error pass 9 had
already recorded and pass 12 repeated.

## WHAT THE INSTRUMENTS CAUGHT THAT READING DID NOT

- **The compiler named 28 call sites against a predicted 27.** The 28th was the only production
  caller, and the prediction could not see it: it counted sites that OMIT `userId`, and the
  service passes `string | undefined`.
- **The coverage ratchet caught a third unreachable throw** in a method whose own comment
  predicts that exact failure to within 0.03 percentage points. Deleted rather than tested —
  third time this project has answered the ratchet by removing code.
- **`codes.test.ts`'s exact-set assertion failed on the build that added `sender_not_permitted`**
  — "expected 16 but got 17", the third time that line has turned a new code into a decision.
- **`sweep.py` failed the moment a new requirement had no task**, before anyone noticed.
- **The `[P]`-collision check, added in pass 11, found twenty mismarked tasks** — eight of them
  writing one test file concurrently.

## THE PHASES THAT WENT BADLY

**Phase 2 committed two broken tests.** The planted senderless rows named an `environment_id`
column on `messages`; that column does not exist. Both typechecked, because raw `sql` is a
template string, and the phase ran `typecheck`, the unit lane and `tenant-scope` but never
`repository.itest.ts`. Green by every instrument that was run. **Rule: a phase that adds raw
SQL must run the suite that executes it.**

**Phase 5's own ceiling test proved nothing.** T047c set the ceiling to the number of people
who had already sent, so the next person was over the limit either way — it passed with half of
T047b applied, verified by removing the other half and watching all 26 quota tests stay green.
Rebuilt with a ceiling of 2, which is the arithmetic that separates the versions. Sixth entry in
this project's family of green-but-vacuous tests, and the first written by someone who had read
the other five.

**Phase 5 also broke a shared fixture for the fifth time in two features.** T040b promoted the
gateway fixture's own user to a bot, taking the control and four isolation tests down with it.
Fixed with a `disposable()` capability — a fixture nobody else depends on beats a rule nobody
remembers.

**Phase 9's fence chain cost five wrong answers.** The predecessor is not the previous
chapter's tag (feature 034's tail amended both a platform file and 3.16's fence for it, after
the tag); a diff body in a `ts` fence is read as a whole file; prose fences are not the chain's
requirement; a path the appendix owns cannot be fenced by a chapter; and one word — "that
chapter" against "this chapter" — is a failure, because the chain compares bytes.

**Phase 7's work list was not the task list.** Six files were named; the lane found eight, and
seven of the first run's 22 failures were lane environment rather than code: an unset
`RELAY_INTERNAL_CREDENTIAL`, NATS absent, NATS on the wrong port, and the compose `services`
profile competing for the outbox a test was counting.

## WHAT THE NEXT FEATURE SHOULD DO DIFFERENTLY

1. **Read the clauses, not the identifiers.** Two of the three most expensive findings were a
   governing document saying something the feature had assumed it did not say. Enumerating ids
   answers *is this number free*; it never answers *does a clause already say this*. `check:srs`
   now enforces uniqueness and says in its own comment that it does not read meaning.
2. **Run the command a task tells someone to run, in the pass that writes it.** Pass 6 wrote a
   `grep` into T012a and pass 7 ran it: seven hits, three dead, two do-not-touch, and one that
   would have deleted a capability chapter 3.15 shipped. A generalisation needs its own
   verification step.
3. **Pin the lane environment where the tasks can see it.** Four variables and one stopped
   compose profile stood between a red lane and a green one, and none of them was in a task.
   They are in `baseline.txt` now.
4. **A checker's blind spot is worse than its absence.** `check:srs` shipped covering 192 of 243
   clause rows and printed "192 clause rows" as though that were the document. Three of this
   feature's instruments were wrong in the same way — a pattern matching the examples in front
   of me rather than the set the rule names.
5. **Use a person.** Chapters 3.14, 3.15 and 3.16 named this gap and so does this one. The
   sealed outsider had been wrong about the API for two chapters because nobody ran it, and the
   published Trap contradicting this chapter survived fifteen analysis passes because no checker
   reads prose.
