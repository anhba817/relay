# Research — chapter 3.7, "Commit and publish are two instants"

Phase 0. Six items. R1 establishes the defect by reading rather than by guessing,
R3 **overturns an assumption the spec made**, and R4 is the reason this chapter can
have a test that fails on demand rather than one that fails on average.

---

## R1 — Where the duplicate comes from, established by elimination

**The question.** A client's timeline read `[1, 2, 3, 4, 4]`. Which two code paths
emitted sequence 4?

**There are exactly two.** A `message.created` frame reaches a socket either from
the backfill loop inside `resume()` or from `deliver()` on the live path. The
backfill emits each message in its page once, so one copy came from each.

**How a live delivery can carry an already-backfilled sequence.** The gateway's
send path, `session.ts`:

```text
committed = await api.sendMessage(...)   // the api commits; the seq now exists in Postgres
…
await fanout?.publish({ … })         // only now does Redis hear about it
```

Between those two statements the message is durable, visible to any backfill
query, and unknown to the fabric. A resuming connection whose backfill lands in
that interval receives the message from the backfill and sets its high-water mark
to that sequence. It then flushes, goes live, and the publish finally happens —
delivering the same message a second time.

The e2e journey drives a send straight into the interval. Its own comment says so:
*"This send goes out WHILE the resume is in flight … the frame may be in the
backfill, in the buffer, or both, and the outcome must be identical either way."*
The three cases it names are handled. The fourth — in the backfill, and delivered
live *after* the flush — is not enumerated, because the sentence treats a message
as existing at one instant.

**Why the dedup does not catch it.** `marks` is a local variable inside `resume()`,
used once by `flushable` and discarded. `Connection` has no field for it, and
`deliver()` consults `phase` and nothing else — the comment on that field states
the design as a virtue: *"Delivery reads this field and nothing else — the resume
machinery is invisible to it."* That simplicity is the defect. Frames published
before the flush are compared against the mark; frames published after it are
compared against nothing.

**Status.** Established by reading, after observing the failure once in six runs.
Not reproduced under instrumentation — R4 is how this chapter makes it
reproducible on demand, and that test is the real proof.

---

## R2 — The existing suite covers three of four quadrants

`resume.itest.ts` has three tests, and the case that fails is the one it does not
have. The matrix has two axes: when the frame was published, and whether its
sequence is at or below the backfill's high-water mark.

| | seq ≤ mark | seq > mark |
|---|---|---|
| **published while buffering** | test 1 — suppressed by `flushable` | test 2 — delivered by the flush |
| **published after going live** | **no test** ← the defect | test 3 — delivered live |

Test 3 publishes `frame(44)` after the resume finishes and asserts it arrives;
the missing test publishes `frame(42)` — a sequence the backfill already sent —
and asserts it does not. One number apart.

**Why this is worth stating in the chapter.** The gap is not carelessness; it is
what happens when a test suite is written from a model. The model had three cases
and the suite has three tests. A matrix drawn from the two axes has four cells,
and the empty one is where the bug lived for seven chapters.

---

## R3 — The mark must NOT be retired. The spec assumed otherwise.

**What the spec assumed.** FR-007 asks for the retained state to be bounded, and
the spec's Assumptions proposed retiring the mark per channel once the connection
observes a sequence above it — "the window that produced the duplicate has closed
for that channel". The checklist flagged it for the plan to confirm.

**It is wrong, and it reintroduces the bug it is meant to bound.**

Sequences are assigned under a channel row lock (chapter 2.2), so sequence 4
commits before sequence 5. **Publication order is not so constrained.** The two
sends may be handled by different gateway instances, and each publishes after its
own api call returns. Instance A can commit seq 4 and stall before publishing
while instance B commits seq 5 and publishes immediately.

Under observation-based retirement:

```text
resume completes, mark = 4
seq 5 arrives  → above the mark → deliver, and RETIRE the mark
seq 4 arrives  → no mark left   → deliver  ← the duplicate, again
```

The retirement rule hands the window straight back.

**Decision: keep the mark for the life of the connection. Never retire it.**

**Why that is safe rather than merely cautious.** A frame with a sequence at or
below the mark can never be one the client has not already seen. The backfill
delivered everything above the presented cursor and up to the mark; anything at or
below the cursor the client had before it disconnected. Sequences are monotonic
per channel and never reused. So suppression at or below the mark is correct
forever, not just during a window.

**Why it is bounded without retirement.** The mark set starts from the resume
cursors, and those are capped: `internalBackfillRequestSchema` refuses more than
`MAX_RESUME_CHANNELS` (200) and the api enforces it, so a larger cursor map
degrades the resume rather than growing the map.

**That is not sufficient on its own, and the first version of this section said it
was.** `highWaterMarks` seeds from the cursors and then adds a key for every
channel the backfill returned, so the mark set is bounded by the cursor cap only
because the api happens to key its response off the cursors it was given. That is
true today — the backfill controller builds its response from the request — but it
is another service's response shape holding a bound this service claims. The marks
are therefore scoped to the presented cursor keys before they are stored, by a
pure function in `resume.ts` beside `scopeCursors`: the same filter, one step
later, in the file where a unit test can reach it.

With that scoping the retained state is at most 200 integers per resumed
connection — the same order as the cursor map the connection already accepted,
constant in the connection's lifetime, and bounded by this file rather than by a
promise made elsewhere.

**This section produced two requirements.** FR-007 is the bound just stated.
FR-007a is the prohibition this section opens with — the mark must not be retired
while the connection lives. The spec originally required the opposite, and
correcting that is what this research was for.

**Cost per frame.** One dictionary lookup and one integer comparison, on a path
that already serialises a frame to JSON and writes it to a socket.

**Alternatives considered.** A time-based window ("suppress for 5 seconds after
resume") — rejected: it is a guess about the length of the publish gap, and a
guess that is wrong in the unsafe direction produces exactly the bug being fixed.
Deduplicating on message id with a bounded set — rejected: it costs more memory
for a weaker guarantee, since a sequence comparison covers every message below the
mark including ones this connection never enumerated.

---

## R4 — The defect can be made deterministic without touching the api

**The question.** SC-002 asks for a test that fails against today's code every
time, not once in six runs. The window it needs is between an api commit and a
Redis publish, which sounds like it needs both services and precise timing.

**It needs neither.** `resume.itest.ts` boots the gateway with a **stubbed api**
and a **real Redis fabric**, and has a `publishFromElsewhere` helper that publishes
as a different gateway instance would. The test controls both halves directly:

- what the backfill returns — so the mark is whatever the test says;
- when the fabric publishes — so "after the resume completed" is a statement the
  test makes, not a race it hopes for.

The failing case is test 3 with one number changed: publish `frame(42)` instead of
`frame(44)` after the resume finishes, and assert the timeline is `[42]` rather
than `[42, 42]`.

**Decision.** The deterministic test lives in `resume.itest.ts` beside the three
that already draw the matrix. The e2e journey keeps its assertion — it is what
found the defect and it is the only test exercising the real commit-to-publish gap
— but it is not the proof, because a test that fails one run in six cannot tell
anyone whether a fix worked.

**On proving the fix.** Twenty consecutive lane runs (SC-001) is evidence about
the flake; the deterministic test is evidence about the mechanism. Both, and the
sabotage battery removes the suppression to confirm the deterministic test fails
without it.

---

## R5 — Where the code goes, and what stays pure

`resume.ts` is deliberately pure: parsing, marks, partitioning, with the
orchestration in `session.ts` "where the socket is". That division is worth
keeping, so the change splits the same way:

- **`resume.ts`** gains two pure functions. The predicate — given the marks and a
  frame, is this a duplicate? — which sits next to `flushable`, the function it
  generalises. And the scoping that drops any channel the presented cursors did not
  name, which sits next to `scopeCursors`, the filter it echoes. Both are
  unit-testable with no socket, no broker and no clock, and both are here rather
  than in `session.ts` for that reason: a filter written inline in the
  orchestration could not be reached by a test in `resume.test.ts`.
- **`registry.ts`** gains one field on `Connection`: the marks a resumed connection
  retains, null for a fresh connect and null after a degraded resume.
- **`session.ts`** does two things: sets the field when a resume succeeds, and
  consults it in `deliver()` before sending.

`deliver()`'s comment — "Delivery reads this field and nothing else" — becomes
false and must be rewritten rather than left. It is the sentence that documented
the defect as a design principle.

**Nothing in the api changes.** Its commit-then-return is correct. Moving fan-out
publication into the api would close the gap by making the announcement
transactional, and would reintroduce the dual write chapter 3.3 spent itself
removing — the api would then be writing to Postgres and Redis in one breath, with
no outbox between them.

---

## R6 — The renumbering, and the reference that is already stale

Inserting a chapter moves quotas to 3.8 and the gauntlet to 3.9. Four kinds of
reference have to move with it, and they are not equally easy.

| Where | Difficulty |
|---|---|
| `docs/07-tutorial-plan.md` | trivial — done during `/speckit-specify` |
| `lib/tutorial.ts` registry | trivial — done during `/speckit-specify` |
| Prose in published pages, both locales | easy — prose is not fence-checked |
| **Comments inside fenced source files** | **the hard one** |

Three source comments name chapter numbers:

```text
services/api/src/db/schema.ts:375   "chapter 3.7's cross-tenant gauntlet"   ← ALREADY STALE
services/api/src/db/schema.ts:596   "Chapter 3.7 needs the same transport for quotas"
scripts/webhook-walk.mjs:453        "Chapter 3.7 needs the same transport for quotas"
```

The first is stale **now**. The gauntlet became 3.8 when chapter 3.6 was inserted
during 3.5's own work, and that comment was never carried. It is byte-fenced into
published chapter 3.5, so the mechanism that guarantees the book matches the code
is the same mechanism that makes the correction cost a fence amendment.

**Decision: stop citing numbers that can move.** All three comments are rewritten
to name the subject rather than the ordinal — "the cross-tenant gauntlet",
"a later chapter needs the same transport for quotas". A chapter number in a source
comment is a reference that ages every time the plan changes, and the plan has now
changed twice in three chapters.

**Where the amendments are fenced.** `schema.ts`'s chain currently ends in chapter
3.6 and `webhook-walk.mjs`'s in 3.6, so both amendments can be fenced in this
chapter, which is the next link and which does discuss why the references were
fragile. The `schema.ts:375` correction rides the same diff. Nothing needs the
post-series file, and no published chapter is made to show code it does not
discuss.

**Alternatives considered.** Leaving the stale reference — rejected: a third
insertion would then be compounding two. Fixing only the numbers and keeping the
ordinal form — rejected: it survives until the next insertion and no further.

---

## What this chapter does NOT do

- Rewrite chapter 2.7 or 2.8. They show the platform at their own time; the fence
  chain's whole premise is that a later amendment does not make an earlier chapter
  a liar.
- Deduplicate in the SDK. A platform that needs a correct client to keep its own
  guarantee has not kept it.
- Touch the api, the sequence assignment, or the outbox.
