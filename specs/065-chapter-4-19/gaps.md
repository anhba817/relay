# Gaps — chapter 4.19, "Everything, including what was deleted" (feature 065)

Numbered, with what was measured rather than what was suspected. The carried ledger is
at the end and is **re-measured rather than copied** — four of 043's twenty-three
carried items were wrong when re-measured and three had closed with nobody working on
them.

---

## 065-1 · The history row and `messageSchema` are three different shapes, and nothing parses one against the other

Recorded rather than fixed (T029). Measured against the composed api at analysis pass 7,
from the live key set of a history row:

    ['attachments', 'channel_id', 'created_at', 'edited_at', 'id', 'seq', 'text', 'user']

Against `messageSchema`, three disagreements:

| the response | the schema |
|---|---|
| `channel_id` | declares `channel` |
| carries `edited_at` | does not declare it |
| `text: null` on a tombstone | `z.string()` |

**NOTHING PARSES THE HISTORY RESPONSE AGAINST THAT SCHEMA**, so the divergence costs
nothing today and no instrument can see it — not the compiler, not a test, not
`check:docs`. It is a documentation question rather than a defect, and which document
is wrong is the thing somebody has to decide.

**WHY THIS CHAPTER DID NOT CONVERGE THEM.** Everything else here is an addition and
this would be a reshape of a published response. Chapter 4.14 measured what making one
field required costs across construction sites before concluding it was worth it there;
the same measurement is owed here and is not this chapter's. `deleted_at` was added to
the row without touching the three, which widens the gap by one field and is stated
rather than hidden.

---

## 065-2 · The edit path still writes a millisecond `Date` into a microsecond column

**Measured, and it is the half of a real defect that this chapter did not fix.**

`message_edits.edited_at` is `timestamptz` at precision 6. Every value ever written to
it arrived through the driver as a JavaScript `Date`, which holds milliseconds:

    rows whose edited_at is millisecond-exact     5,149
    total rows                                    5,149

So the primary key `(message_id, edited_at)` has a collision window **one thousand times
wider** than `schema.ts` claimed — *"Postgres holds microseconds, so that needs two
edits inside one microsecond on one message"*. That sentence is corrected in this
chapter; the edit path's write is not.

**HOW IT SURFACED.** This chapter gave the table a second writer, and
`repository.itest.ts`'s concurrent edit-and-deletion race failed on attempt 1 of 10:

    23505  message_edits_message_id_edited_at_pk
    Key (message_id, edited_at)=(6254a80e-…, 2026-10-03 11:10:28.806+00) already exists.

The deletion's transaction rolled back and the message was left **un-tombstoned**, which
is feature 043's FR-007. The deletion now writes `sql\`now()\``, which keeps full
precision and is the same instant the tombstone carries; 80 races green after.

**WHAT IS LEFT.** Two concurrent edits of one message inside the same millisecond still
collide, and the second one's whole edit fails. That is pre-existing, FR-008 says this
chapter does not change the edit path's behaviour, and the fix is the same one
expression. **The reason to write it down rather than do it**: changing `editMessage`'s
clock is a behaviour change on the platform's busiest write path, and it deserves the
measurement this chapter gave the deletion rather than a drive-by.

---

## 065-3 · `outbox.itest.ts` fails for its neighbours' reasons, and the checker built to find that cannot see it

**063-7 reproduced with a control**, during this chapter's own T002 baseline.

    run 1   test:integration  gateway 1 of 12 failed
            coverage          2 files, 4 tests failed
    run 2   test:integration  api outbox.itest.ts "invariant 8", expected [] to have length 20
            coverage          outbox.itest.ts "invariant 1", expected 1 to be 2
    run 3   the outbox suite ALONE                 EXIT 0 · 18 of 18

Three runs of an unchanged tree, three different failure sets, and the suite carrying
two of them is green on its own. The assertions are whole-table counts over a shared
table, which 043 found and 063-7 named at this exact address.

**AND `check-lane-scope.py` REPORTS IT CLEAN**: 74 integration files, 0 unscoped reads,
10 of 10 controls firing (T040a). It reads SQL text and invariant 1 applies its scope in
JavaScript, so the instrument cannot see the class that produced three different red
runs. Its own last line says so.

**THE CONSEQUENCE FOR ANY CHAPTER THAT FOLLOWS**: a red `test:integration` is not
evidence of a regression until the lane has been run with nothing else against the
stack. This feature's own analysis passes contributed — pass 7 and T005 each sent,
edited and deleted a message in the seeded tenant, four outbox rows apiece.

---

## 065-4 · The edits route has three scoped reads and removing any two is invisible

**Measured, each arm deleted alone and then in combination, the file restored between
every run.**

    arm                              versions.itest.ts    gauntlet.itest.ts
    A  listMessageEdits env scope    6 of 6 GREEN         62 of 62 GREEN
    B  messageExistsIn env scope     6 of 6 GREEN         62 of 62 GREEN
    C  the channelVisibleTo call     6 of 6 GREEN         62 of 62 GREEN
    A+B both environment scopes      6 of 6 GREEN         62 of 62 GREEN
    A+B+C all three                  6 of 6 GREEN         1 FAILED of 62
    control, restored                6 of 6               62 of 62

Only all three together move anything, and what they move is **one test of 62**. This
chapter's own suite is blind to the entire class.

**THIS IS 4.12's FINDING AND IT IS WORSE HERE.** That chapter had three scopes where
deleting all three turned 2 of 16 red. The reading is not *delete two of them*: they are
arms whose removal changes nothing **because of each other**, and the route is one
refactor from a real leak behind a green lane — a caller that stops asking
`channelVisibleTo`, an early return moved, a helper inlined.

**AND NO COVERAGE NUMBER REPORTS ANY OF IT.** An SQL clause carries no JavaScript
branch, so constitution VI's 100%-branch requirement for tenant isolation would read
100% with all three predicates deleted. The gauntlet is the only instrument that fires
at all, and it fires once.

**Why this is a gap rather than a fix**: the defences are correct and the redundancy is
deliberate. What is missing is any instrument that would notice one of them being
removed. Recorded for whoever builds that.

## 065-5 · `outbox.itest.ts` is sensitive to the SIZE of a shared table, not only to a neighbour

065-3 says the suite fails when something else touches the stack. **It is worse than
that, measured twice in one day on the same commit:**

    11:00   the outbox suite ALONE    18 of 18, EXIT 0
    14:20   the outbox suite ALONE    17 of 18 — invariant 8, expected 20, got 13

Between the two readings this feature's own T039 probe wrote 400 messages and 400
deletions, and the lane ran several times. The table now holds **386,317 rows with 0
pending**. Invariant 8 plants twenty rows and asks two concurrent relays to publish all
twenty; within its window only thirteen were drained.

**`reset-lane.mjs` does not touch `outbox` by design** — it clears JetStream debris and
`webhook_deliveries`, and the rows that accumulate in Postgres are data rather than
debris. So this table grows monotonically for the life of the lane, and the suite has a
threshold somewhere above 386,317 rows that it has now crossed.

**This is not a flake and it is not a neighbour.** It is a test whose fixture assumes a
small table, on a lane that has been accumulating for sixty-five features. It will fail
for everybody eventually, it passes in CI because CI starts empty, and the fix is the
suite's fixture rather than the lane — which is why it is recorded rather than worked
around here.

## Carried, and re-measured

| item | measured here |
|---|---|
| 064-1 four ADRs with a summary and no argument | still true; ADR-35 is in both documents and 31–34 are not |
| 064-5 the media sweep fixture's floor | **did not fail in any of three lane runs** on this host — T072 expected it |
| 063-7 whole-table assertions in `outbox.itest.ts` | **reproduced with a control**, see 065-3 |
| 063-4 feature-local ids leaking into `docs/` | phase 7's T049 sweeps it tree-wide |
| 058-3 a malformed path parameter answers 500 | **live on this chapter's own route**, measured with a control at pass 5 and carried with its bill |
| 062-12, 050-8, 063-2, 063-3, 043-1 | checked, not live here |
