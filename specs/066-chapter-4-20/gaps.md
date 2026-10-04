# Gaps — chapter 4.20, "The messages that expire" (feature 066)

Numbered, with what was measured rather than what was suspected. The carried
ledger is re-measured rather than copied: four of 043's twenty-three carried
items were wrong when re-measured and three had closed with nobody working on
them.

## 066-1 · An audit entry outlives the message it names, and nothing refuses it

**Measured at the open and unchanged by this chapter:**

    audit_log rows naming a message target          1,435
    audit_log rows in total                         3,477
    foreign key from audit_log to messages          NONE

An entry records that an action happened, not the thing it happened to — so
there is no constraint between the two tables and nothing in the database stops
a message being destroyed while an entry still names its id. After this chapter
the sweep destroys messages, so **an entry whose `target_id` resolves to nothing
is a state the platform now reaches on purpose rather than by accident.**

**STATED RATHER THAN FIXED, AND THE REASON IS THE OTHER CLAUSE.** Repairing it
means one of two things and both are worse than the gap:

- **Add the foreign key.** Then an audit entry refuses the deletion FR-MOD-06
  requires, and the two clauses deadlock.
- **Delete the entries whose target is gone.** That is a DELETE against
  `audit_log`, which `0021`'s `BEFORE UPDATE OR DELETE` trigger refuses — and
  the refusal is ADR-35's published guarantee, which chapter 4.18 wrote and this
  chapter has already narrowed once. Narrowing it twice in two chapters for a
  cosmetic repair is not a trade worth making.

So a reader of the audit log may find an entry naming a message that no longer
exists, and the honest answer is that the entry is the record and the message
was not. The log says what a moderator did; it was never a copy of what they did
it to.

**WHAT WOULD CHANGE THIS.** FR-MOD-05's export — unbuilt, two rows above
FR-MOD-06 — is the clause that would let a tenant hold the message beside the
entry. Until it exists, the audit log is the only durable record of a moderation
action and it carries an id rather than a payload.

## 066-2 · The delete's tenancy arm is invisible to every suite but its own

**Measured, each predicate deleted alone and together, retention suite AND
isolation gauntlet re-run each time:**

    arm 0  untouched                        71 of 71 pass
    arm A  scope off the PAGED READ          1 failed
    arm B  scope off `destroyMessages`      71 of 71 PASS
    arm C  both                              1 failed

Arm B turns nothing red because every id the sweep passes has already been
scoped by `expiredMessageIds`. **A single-mutation probe measures the defence,
not the arm** — 065-4 and 4.12, a third time.

**CLOSED IN THIS CHAPTER BY A TEST RATHER THAN A DELETION.** The arm defends a
caller that does not scope first and one refactor is all it takes to become that
caller, so `retention.itest.ts` gained *"destroyMessages refuses an id from
another tenant, on its own"* and arm B now turns 1 red.

**The reason it is still worth an entry** is the inversion: constitution I's
usual failure is a leak and the usual probe asks what came back. Here a wrong
scope DESTROYS another tenant's messages, so the assertion has to read what
survived. Any future bulk-delete path needs the probe written that way round,
and nothing enforces that.

## 066-3 · `environments_with_policy` was 22 at close-out and the premise says 0

This chapter's own tests and cost measurements left a retention policy on **22
environments**. At the open it was **0 of 33,051**, so every one of them was
debris — cleared, and re-measured at 0.

**It matters more than ordinary probe debris because of what the policy arms.**
A left-behind policy is not an inert row: the next person to run the sweep
destroys messages in 22 environments that nobody chose. `reset-lane.mjs` does
not clear it, and nothing warns.

**AND THE CLEAN-UP WAS ONLY POSSIBLE BECAUSE OF THE OPENING MEASUREMENT.** With
0 at the open, every policy at the close is this session's by construction. Had
the column been in use, there would have been no way to tell debris from data —
which is the argument for measuring a column before writing to it, not after.

## Carried, and re-measured

| carry | what it measures now |
|---|---|
| **064-1** four ADRs with a summary and no argument | **unchanged at ADR-31–34**: still in `docs/05-sad.md`, still **zero** in `docs/06`. **This chapter did not add to it** — ADR-36 went into both homes, 4 mentions and 1 |
| **065-2** the edit path writes a millisecond `Date` | **reproduces, and measured from DATA**: `ended_by='edit'` is **5,549 of 5,549** millisecond-exact on a microsecond column; `ended_by='deletion'` is 50 of 1,114, where chance predicts ~1. The 50 interleave with precise rows rather than preceding 4.19's fix, and both writers are in `repository.ts` with the deletion path using SQL `now()`. **Cause not identified; the number is recorded without a theory** |
| **058-3** a malformed path parameter answers 500 | **THE ENTRY SAYS SIXTEEN AND IT IS TWENTY-THREE.** It counted `@Param("channelId")` 13 and `@Param("messageId")` 3 across two controllers and never opened `webhooks.controller.ts`, whose **six** `@Param("id")` routes take a `uuid PRIMARY KEY` unvalidated. Twenty-two before this chapter, twenty-three with `@Param("environmentId")`. Carried, not repaired: one validating route among twenty-three makes the other twenty-two harder to sweep |
| **065-3, 065-5** shared-state suites and the outbox's size | `outbox` **400,697** at the close, against 395,452 at the open and 386,317 at 065's. `outbox.itest.ts` invariant 8 was **red at the open and is not this chapter's** |
| **050-8** nothing drains the records the stack publishes | **LIVE, AND THIS CHAPTER ADDED A PRODUCER.** `compose.yaml` still has no `ingester` service, and the sweep now publishes a `deleted` storage event into a stream nothing drains in the shipped stack |
| **062-12** files with no coverage pin | **live** — this chapter adds four files and T065 pins them |
| **063-4** feature-local ids leaking into `docs/` | swept both ways at T048: **this session added zero**. The tree-wide population is unchanged and is not this chapter's |
| **064-5** the media sweep fixture's floor | carried unchanged, not re-measured: this chapter runs no media-worker sweep. 065 found it did not fail in three lane runs on this host |
| **065-1, 065-4, 043-1, 063-2, 063-3** | checked, not live here. 065-4's shape **did** recur and is 066-2 above |

## 066-4 · The test that proves the sweep is safe creates the oldest message on the lane

**Measured at phase 9, running the quickstart as written:**

    §1 at the open, before this chapter's suites    2026-09-14  ·  0 past 30 days
    §1 at the close, after them                     2025-08-30  ·  5 past 30 days

The five are all `"a year old and indefinite"` — `retention.itest.ts`'s FR-004
fixture. The clause says an environment with **no** policy loses nothing **at
any age**, and the only way to test *any age* is to plant a message a year old.
So the test that proves the sweep is safe is also the thing that falsifies the
chapter's headline measurement.

**IT IS NOT DRIFT AND IT IS NOT REAL TRAFFIC**, which is exactly why it is worth
an entry: a reader running §1 after the suite sees a number the chapter does not
publish and has no way to tell a fixture from a message. The quickstart now says
so, and the fix is the same shape 043 and 045 kept finding — **§1 asks a
whole-table question and the thing it is about is per environment.**

**The five survivors are harmless and the reason matters**: they sit in
environments with **no policy**, so no sweep reaches them. §3's guard is scoped
to the tenant about to be given a policy, which is the number that decides
whether §5 is safe. A whole-table guard would have been both alarming and wrong.

`reset-lane.mjs` does not clear them, by design.
