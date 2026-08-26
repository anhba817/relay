<!-- SPECKIT START -->
**CHAPTER 3.17 IS CLOSED.** One feature, one published chapter, 153 tasks, checklist 16/16,
both locales, **`check:fences` clean — 212 fenced files across 34 chapters, all 34
translated.** Its record is `specs/035-chapter-3-17/` — read `chapter-notes.md` first (the
plan against what shipped, and the five phases that went badly), then `gaps.md` (nine open
things, each with an owner), `traceability.md` (both directions, and FR-CHN-05 corrected a
third time) and `baseline.txt` for every measurement.

    3.17 "the sender a message never had"   16 files taught, 2,962 words, 27 fences
                                            + 7 files changed and claimed by no chapter
    589 tests, 25 of 26 full-lane runs green, mean 193.55 s, stdev 0.99, budget 240 s
    coverage: repository.ts branches 91 -> 92, functions 100% (115/115)
    212 figures, 91 static pages, the sealed outsider 11/11

## THE REQUIREMENT WAS ALREADY THERE, SATISFIED BACKWARDS FOR ELEVEN CHAPTERS

    | FR-MSG-13 | The system shall support sending a message on behalf of any user
                  via API key, for backend-originated messages. | P2 | T |

P2, verification by test, on the books since v1. Chapter 3.3 satisfied it by sending
unattributed, and `messages.controller.ts` recorded that reading in a comment a reader would
believe: *"A tenant's own server sending on a customer's behalf is FR-MSG-13, not a mistake."*
The plan for 3.17 said the SRS had no such requirement. **Thirteen analysis passes read that
sentence. Pass 13 opened §4.5 and read the clauses instead of the identifiers.**

**A missing requirement fails a coverage check. A requirement satisfied backwards traces to
code, cites itself in a comment, and passes every gate.** Pass 14 then found `FR-TEN-08` cited
three times as the billing authority when it governs application deletion — and the clauses
that do apply, `FR-ANL-05` (meters) and `FR-RTL-05` (enforces), had separated metering from
enforcement years before pass 6 spent a pass deriving that split from `repository.ts`.

**Read the clauses, not the identifiers.** `check:srs` enforces uniqueness and says in its own
comment that it does not read meaning; T000 carries the semantic half, and it is a human read.

## SIXTEEN ANALYSIS PASSES, TWENTY CRITICALS, AND THE SOURCE MOVED EVERY TIME

    1-2   artifacts against each other        9    auditing the gate task
    3-4   asking the repository               10   reading the authority being quoted
    5     checking a task's premise           11   structural: [P], id order, phases
    6     a question the last pass wrote down 12   coverage in the reverse direction
    7     running the command a task names    13   a section's CLAUSES, not its ids
    8     a constraint's reachable paths      14   the same, all seven cited families
                                             15   the published prose, which nothing checks

**Pass 12 recommended stopping and was wrong** — it reasoned from falling yield, which measures
the questions being asked rather than the defects present. Pass 9 had already recorded that
error; pass 12 repeated it.

## FIVE INSTRUMENTS CAUGHT WHAT READING DID NOT

- **The compiler named 28 call sites against a predicted 27.** The 28th was the only production
  caller: the count measured sites that OMIT `userId`, and the service passes `string |
  undefined`, which `exactOptionalPropertyTypes` refuses just as firmly.
- **The coverage ratchet caught a third unreachable throw** in a method whose own comment
  predicts that failure to within 0.03 points. Deleted, not tested — third time.
- **`codes.test.ts`'s exact-set assertion failed on the build that added the code.** Third time.
- **`sweep.py` failed the moment a requirement had no task**, mid-edit.
- **A `[P]`-collision check found twenty mismarked tasks**, eight writing one file at once.

## AND THREE OF MY OWN INSTRUMENTS WERE WRONG THE SAME WAY

`check:srs` shipped covering **192 of 243 clause rows** — its regex matched three-part ids, so
it skipped `DR-01`, `CON-06` and all 22 `EIR-*` — and printed "192 clause rows" as though that
were the document. The `[P]` collision check's extension list omitted `.txt`. A prose matcher
cried wolf nine times. **Each matched the examples in front of me rather than the set the rule
names**, and `check-docs-drift.sh` has a comment about exactly that: *"A range stops where it
stops for a reason nobody records."*

## THE PHASES THAT WENT BADLY

**Phase 2 committed two broken tests.** Planted rows named an `environment_id` column
`messages` does not have. Both typechecked — raw `sql` is a template string — and the phase ran
`typecheck`, the unit lane and `tenant-scope` but never `repository.itest.ts`. **A phase that
adds raw SQL must run the suite that executes it.**

**Phase 5's own ceiling test proved nothing.** It set the ceiling to the number of people who
had already sent, so the next person was over it either way; it passed with half the fix
applied, proven by removing the other half and watching 26 tests stay green. Sixth entry in the
green-but-vacuous family, and the first written by someone who had read the other five.

**Phase 5 broke a shared fixture, fifth time in two features** — promoting the gateway
fixture's own user took the control down. Fixed with a `disposable()` capability: a fixture
nobody depends on beats a rule nobody remembers.

**Phase 9's fence chain cost five wrong answers.** The predecessor is not the previous
chapter's tag — feature 034's tail amended a platform file AND 3.16's fence for it after the
tag was placed. A diff body in a ```ts fence is read as a whole file. Prose fences are not the
chain's requirement. **A path the appendix owns cannot be fenced by a chapter.** And one word,
"that chapter" against "this chapter", is a failure, because the chain compares bytes.

**Phase 7's work list was not the task list**: six files named, eight found, and seven of the
first run's 22 failures were lane environment rather than code.

## THE LANE ENVIRONMENT, WHICH IS NOT IN ANY TASK

    DATABASE_URL=postgres://relay:relay@localhost:15432/relay
    RELAY_INTERNAL_CREDENTIAL=rk_svc_local_development_credential_0000
    RELAY_INTERNAL_CREDENTIAL_GATEWAY=rk_svc_local_development_gateway_00000
    RELAY_NATS_URL=nats://localhost:4222
    docker compose up postgres redis mailpit nats — and the `services` profile STOPPED

The api container drains the outbox a test is counting. Postgres 5432 is this machine's own.

## MEASUREMENTS WORTH NOT RE-TAKING

    the lane, 589 tests            mean 193.55 s, stdev 0.99 across 19 green runs
    the lane, 550 tests (3.16)     mean 193.55 s   -> IT COSTS PER SUITE, NOT PER TEST
    the promotion's scan, HIT      0.321 ms   (stops at the first row)
    the promotion's scan, MISS    14.120 ms   (394,142 rows, to prove a negative)
    ADD COLUMN NOT NULL DEFAULT    4.721 ms on 134,067 rows — metadata only
    each CHECK constraint         ~14 ms      — O(n), and "no backfill" does not cover it
    senderless rows in the lane    121,250 of 394,808, across 10,077 environments
    billed vs enforced counters    8,553 vs 8,538 — they differ by the bot population

**Twenty-five of twenty-six is not twenty green.** One run failed in a mail-relay test this
chapter never touched, at a rate near 3.8%, and the mechanism is not identified. It is
`gaps.md` item 1, unfixed on purpose: changing code until a symptom stops, with no mechanism in
hand, is how a real defect gets buried.

## WHAT 3.17 DID NOT DELIVER

**Chapter 3.18 — the fan-out.** Chapter 3.12's gap G1 listed two mechanisms for "a REST-sent
message reaches no socket". This chapter removed one: every send carries a sender, so `toFrame`
keeps the row and **a resume now delivers it**. Live delivery still reaches nothing, because
only the gateway publishes. G1 is amended in place.

**Chapter 3.19 — presence.** FR-CHN-05's third verb, checked again rather than assumed: the
only "presence" in `services/gateway/src` is the English word, in a comment about cursors.

## THE CHAPTER CYCLE THIS PROJECT USES

`/speckit-specify` -> `/speckit-plan` -> `/speckit-tasks` -> `/speckit-analyze` (repeatedly) ->
`/speckit-implement` (once per phase). **Commit each phase.** Nothing else runs on the machine
during a battery. And `sweep.py` / `sweep-sources.py` in the feature directory re-run 33
mechanical checks in seconds — start from those rather than from re-reading.

<!-- SPECKIT END -->
