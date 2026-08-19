# Chapter notes — 3.7, "Commit and publish are two instants"

Written from what happened, not from what was planned. The parts that went badly
are the parts worth keeping.

---

## What shipped

Four lines of logic. A `marks` field on `Connection`, two pure functions in
`resume.ts`, and a call to one of them in `deliver()`. Nine diff fences, three
figures, 2,244 prose words in English and 2,798 in Vietnamese, tagged
`part3-ch7`.

No migration, no column, no dependency, no api change — which is what the plan
predicted, and one of the few predictions in this feature that held.

---

## The spec was wrong about its central decision, and research caught it

FR-007 asked for the retained state to be bounded and the spec's Assumptions
proposed retiring a channel's mark once a sequence above it arrives: the window
that produced the duplicate has closed, so stop paying for it.

Research R3 established that this reintroduces the bug. Sequences are assigned
under a channel row lock, so 4 commits before 5 — but the two sends may be handled
by *different gateway instances*, and each publishes after its own api call
returns. Instance A commits 4 and stalls; instance B commits 5 and publishes at
once. Under retirement, 5 arrives, is delivered, retires the mark; then 4 arrives
against nothing and is delivered a second time.

The correction became FR-007a, a prohibition rather than a bound, and it
propagated through the spec, the plan, the data model, the contract, the tasks and
the checklist across six `/speckit-analyze` passes. **The spec is not the
authority on a mechanism it has not reasoned through.** It took a research task
to see it, and the sabotage battery to prove the test behind it worked.

---

## The measurement that removed its own success criterion

SC-001 asked for twenty consecutive lane passes after the fix. T004 ran twenty
lane passes *before* the fix and saw zero failures.

Chapter 3.6 observed one failure in six runs and this chapter's spec repeated
that figure. Twenty at zero says the rate is lower — six runs is a thin sample
and one failure in it supports anything from 2% to 40%.

There is a better explanation than bad luck, and it is about the defect rather
than the statistics. The race needs a backfill query to land inside the gap
between an api commit and a Redis publish, and that gap widens under load. When
3.6 measured, the lane took nine minutes because the database held 4,068 pending
webhook deliveries being retried against dead endpoints at three seconds each.
That backlog was cleared at the end of 3.6, the lane now takes about three
minutes, and the gap is correspondingly narrow. **The defect did not get rarer.
The conditions that exposed it went away.**

SC-001 was kept and demoted in writing rather than deleted: twenty post-fix runs
still show the change causes no regression, which is worth having when the change
suppresses frames and its failure mode is a gap. What it no longer does is provide
evidence that the duplicate is gone. SC-002's deterministic test carries the whole
proof — it fails every time against the old code, in four seconds, with no race to
wait for.

This is the third success criterion in three chapters that could not fail: 3.5's
"terminated, not retried" at a 30-second ack wait, 3.6's mutation that could not
compile, and now this. The pattern is a criterion written before the thing it
measures exists.

---

## The sabotage battery changed the mutation list and then found a bad test

**Mutation 4 as planned could not fail.** It was to be "retain the marks through a
degraded resume". Reading the code before running it: every `return degrade(...)`
sits at lines 300-331 and the marks are assigned at line 360, so on every degrade
path they are still `null` and the clear inside `degrade` changes nothing. The
requirement holds *structurally* — marks are only ever set on the success path —
rather than because that line runs. The line stays as a guard for a future path
that degrades after computing marks; the mutation was replaced with one attacking
the scoping.

**Mutation 5 survived, and the fault was in the test.** The out-of-order case
published 43 then 42 against a mark of 43. Both are at or below it, so the
retirement the mutation adds never fired. The scenario needs a frame *above* the
mark first. The test had the right name, sat in the right file, and never touched
the mechanism it existed to protect — and it would have passed for ever.

Nothing but a mutation finds that. Reading does not: the name describes the intent
and the assertions are consistent with the intent. Running does not: it passes.
The chapter's central design decision had no test behind it until the battery said
so.

---

## Three faults found in other people's chapters

### The sweep test that depended on a clean database (T002a)

3.6's `deliveries.itest.ts` aged its own endpoint by 64 minutes and called the
global sweep with the default limit of 100. By this chapter's baseline, 781
endpoints had accumulated an open failure run; they are older, they fill the
batch, and the test's own endpoint is never reached.

**Which assertion caught it is the part worth keeping.** The test checks
`disabled >= 1` first, and that PASSED — the sweep had just disabled a hundred
endpoints belonging to nobody in particular. Only the assertion about *this*
endpoint could tell "the sweep works" from "the sweep did something". A count is
not a proof of effect.

Fixed ahead of schedule because T004's measurement depended on it: a lane with two
intermittent failures cannot measure the rate of either.

### The drain that looked like a relay refusing to publish (T021, run 2)

Found on run 2 of the twenty post-fix runs, in the same file:
`expected null not to be null` for a delivery that was unambiguously due.

`drainDueDeliveries` claims `FOR UPDATE SKIP LOCKED`. A suite in a parallel vitest
worker holding that row inside an open transaction makes the call skip it, and one
call is then indistinguishable from the relay declining to publish something due —
which is the exact failure the test exists to report. The helper's own comment
already had the principle right (*assert the property, not the observer*) and the
implementation was one call short of it. It now drains until the row settles,
bounded at ten passes.

**This forced the twenty runs to be restarted.** The fix landed at run 7 of the
first attempt, and twenty runs measuring two different trees is not a measurement.
The first seven were preserved and abandoned; the count in `baseline.txt` is from
a clean start on one commit.

### Six identifiers that were about to leak (T039)

Six comments this chapter added to gateway source cited FR-001…FR-007 — this
feature's own spec identifiers, which no reader of the published book can look up.
They were about to be fenced verbatim. Rewritten to cite FR-RTM-03 where a
documented requirement covers the same property, and to say the thing plainly
where none does.

3.6 shipped fourteen of these. They are not fixed here: they sit inside published
fences in two locales, and correcting them costs an amendment fenced in a later
chapter that discusses them.

---

## The already-stale chapter reference (T025)

`services/api/src/db/schema.ts:375` said "chapter 3.7's cross-tenant gauntlet".
The gauntlet was 3.7 when that was written; it became 3.8 when chapter 3.6 was
inserted during 3.5's own work, and nobody carried the comment. It was wrong
before this chapter existed, and this chapter's insertion would have made it wrong
by two.

It is byte-fenced into published chapter 3.5, so the mechanism that guarantees the
book matches the code is the same mechanism that makes the correction cost a fence
amendment. All three chapter-citing comments now name the subject rather than the
ordinal.

**The rule that came out of it**, and the reason V9's own check had to be
rewritten: the problem is not chapter numbers in comments, it is *forward*
references. "Chapter 3.6 added this field" is a provenance stamp and stays true
for ever, because chapters do not renumber backwards. "Chapter 3.7 will build the
transport for quotas" is a promise, and it goes stale the moment anything is
inserted ahead of it.

---

## What the quickstart got wrong about itself

V0 estimated twenty lane runs at "about nine minutes each, so this is three hours
of wall clock". Measured: 183 seconds. The nine-minute figure came from 3.6, when
the pending-delivery backlog was saturating the machine, and nobody remeasured
after clearing it.

Corrected to ~62 minutes, because a three-hour price tag is the kind of number
that gets a measurement cut — and cutting this one would have hidden the fact that
SC-001 could not fail.

---

## What this chapter did not do

- Rewrite chapter 2.7 or 2.8. They show the platform at their own time.
- Deduplicate in the SDK. A platform that needs a correct client to keep its own
  guarantee has not kept it.
- Move fan-out publication into the api. It would make the announcement
  transactional and reintroduce the dual write chapter 3.3 spent itself removing.

---

## Every requirement checked against the code, not against the tasks

A task marked `[X]` is a claim that something was done. This is the claim checked
against the file.

| | Where it lives | Verified by |
|---|---|---|
| FR-001, FR-003 | `session.ts:105` — `if (suppressed(connection.marks, message)) continue;` inside `deliver()` | the call is on the live path, after the flush |
| FR-002 | the same predicate returns false above the mark | `session.test.ts`, "a frame above the mark … IS delivered" |
| FR-004 | `suppressed` indexes `marks[frame.channel]` | `resume.test.ts`, "keeps channels apart" |
| FR-005 | `session.ts:282` — `connection.marks = null` inside `degrade` | and structurally: every `degrade` returns before line 360 |
| FR-006 | `session.ts:175` — `marks: null` at creation | `session.test.ts`, "a connection that never resumed suppresses nothing" |
| FR-007 | `session.ts:360` — `scopeMarks(marks, cursors)` | `resume.test.ts`, "never exceeds the cursor set" |
| FR-007a | **nothing** | see below |

**FR-007a is verified by exhaustion, which is the only way to verify an absence.**
`session.ts` refers to `.marks` exactly three times — one read at 105 and two
writes at 282 and 360 — plus the `marks: null` in the connection literal at 175.
None of the four retires anything, and there is no fifth. The requirement is a
prohibition, so no line of code satisfies it; what satisfies it is that the set of
lines touching the field is small enough to enumerate.

That is also why the fifth sabotage mutation matters more than the other four. It
is the only one that has to ADD code rather than remove it, because it attacks a
decision whose implementation is nothing at all.
