# Chapter 3.23 — gaps

*Every item has an owner. Every reference names its chapter, because the numbers collide.*

**Opened during analysis rather than at close-out**, because two items are findings of the
analysis passes and writing them down when they are found is the only version of this that has
ever worked. Chapter 3.22's eight items are carried and re-checked in the close-out phase, not
copied here.

---

## 1. A CUSTOMER CAN SUBSCRIBE TO AN EVENT TYPE THAT DOES NOT EXIST — NEW, OPEN

FR-WHK-01 says an endpoint subscribes to *"a selected set of event types"*.
`services/api/src/webhooks/webhooks.service.ts:208`'s `assertEventTypes` checks one thing:

    if (!Array.isArray(types) || types.length === 0)

**Membership is never checked.** A customer who posts `"mesage.updated"` gets a 201, an
endpoint that will never fire, and no signal that anything is wrong. Delivery filtering is
`(e.eventTypes as string[]).includes(event.type)` in the repository, so a typo simply never
matches.

**The gap predates this chapter and this chapter changes its character.** Before it, two of
FR-WHK-02's eight named types were emitted by nothing, so silence was the expected answer for
them and a typo was indistinguishable from a correct subscription to an unbuilt event. After
it, five of eight are emitted, and the remaining silence is more likely to be a mistake than a
feature.

**Owner: the chapter that adds the sixth event type, or a webhook chapter.** The remedy is one
`includes` against `OUTBOX_EVENT_TYPES` at create and update time — and **it goes red for any
customer already storing a bad value**, which is why it is a decision rather than a drive-by.

## 2. FR-MOD-03's AUDIT LOG IS WIDENED BY THIS CHAPTER AND NOT BUILT — NEW, OPEN

FR-MOD-02 permits a tenant API key to delete any message irrespective of author, and this
chapter builds it. FR-MOD-03 requires *"every moderation action recorded in an immutable audit
log with actor, action, target, timestamp, and request ID, retained for 1 year"* — P3, and not
built.

**RE-POINTED BY ANALYSIS PASS 5, AND THE FIRST VERSION BLAMED THE WRONG CLAUSE.** This item
said the tombstone kept the author of the message rather than the remover, and attributed the
whole gap to FR-MOD-03's unbuilt audit log. Reading FR-MSG-08 instead of its identifier says
otherwise: it itemises *"sequence number, author, timestamps, and deletion metadata"*, with
timestamps listed separately, so **the actor was already this chapter's to record** and it now
is — FR-006a, in `messages.metadata`, no migration.

**What remains FR-MOD-03's** is narrower and still real: an immutable log with actor, action,
target, timestamp and request id, retained a year, **across every moderation action** rather
than one fact on one row. A tombstone that names its remover is not an audit log — it can be
overwritten by the next writer of that row, it holds no request id, and it says nothing about
actions that leave no row.

**RE-CHECKED AGAINST WHAT SHIPPED IN PHASE 7, and there is one more fact than the analysis
pass could have had.** `metadata.deleted_by` is written and **no read path exposes it.** Not
the history route, not the listing, not the frame, not the webhook event — the frame and the
event both carry the message's AUTHOR, deliberately (FR-008), because a client already holds
that name beside the message and who removed it is a different question.

So the actor is recorded and unreadable. That is the right place to stop for this chapter —
inventing a read surface for it would be deciding, without a requirement, who may learn that
an operator removed somebody's message — but it means **the only way to answer "who deleted
this" today is a database query**, and a test asserts the column rather than an answer anybody
can get.

The re-check also confirms the sharper half of this item: `metadata` is a single jsonb column
on a mutable row. A second deletion cannot overwrite `deleted_by` — FR-009 returns before the
write — but nothing stops a later chapter's writer of that column from replacing the object
wholesale. `deleteMessage` merges rather than replaces, and there is no test anywhere that a
future writer must.

**Owner: FR-MOD-03's chapter.** Named here because this chapter makes the gap reachable and
because the boundary between the two is now written down rather than assumed.

## 3. A CONCURRENT EDIT AND DELETION OF ONE MESSAGE IS NOT TESTED — NEW, OPEN

**RE-CHECKED AGAINST THE SHIPPED ROUTES IN PHASE 6, and the transaction shape turned
out to matter more than the analysis note expected.** Both writes read the row and then write
it inside one transaction, and **neither takes a row lock** — no `FOR UPDATE`, following
`assertWithinQuota`'s recorded decision to state an overshoot rather than engineer around it.
The two orderings that follow are not symmetrical:

    delete, then edit    the edit's SELECT sees `text = NULL` and refuses with
                         `message_deleted` (FR-010). Correct, and tested.
    edit, then delete    the deletion's SELECT sees the pre-edit row. It writes
                         `text = NULL` and the tombstone is right, but the EDIT'S HISTORY
                         ROW holds the text the edit superseded — which is the correct
                         history either way, because that edit did happen.

**Both interleavings end in a tombstone**, which is what makes this a gap rather than a
defect: there is no order of the two that leaves a message saying something nobody wrote. The
untested part is that claim, not the outcome.

The one state worth naming: an edit that commits **between** the deletion's SELECT and its
UPDATE loses its text with no `message.updated`-then-`message.deleted` ordering guarantee on
the wire — the two frames can arrive in either order. A client that applies them in arrival
order can end up showing the edited text after the tombstone. **Repaired by a history
re-read, which is the same bound FR-016a already states for a missed revision.**

**And forcing it is harder than it looks.** Chapter 3.22 spent a phase learning that
`Promise.all` of two operations against one client does not force a race — the commands
serialise at the socket — and that seeing one needed two separate clients. The same is true
here: two requests through one api process share a connection pool.

**Owner: whoever needs it.** The shape a real test would need is recorded so the next person
does not start from `Promise.all`. The cheap alternative, if the frame ordering ever matters
to a customer: `SELECT … FOR UPDATE` in both methods, which serialises the pair at the cost
`assertWithinQuota` declined to pay on the send path.

## 4. ONE AUTHORIZATION FACT LIVES IN TWO PLACES AND NOTHING COMPARES THEM — NEW, OPEN

Which credential class may call a route is declared twice:

    messages.controller.ts   @Accepts("user") / @Accepts("application")   the guard reads it
    isolation/targets.ts     accepts: "user" | "application" | "either"   a declared list

`targets.ts:24` says what its field is for — *"Which credential class the route accepts, and
therefore which attack applies"* — and the derived-versus-declared comparison in
`targets.itest.ts` covers the route's **existence**. **Searching for a consumer of
`target.accepts` outside prose returns nothing**, so the field is a hand-maintained annotation
that can disagree with the decorator without anything noticing.

**The consequence if it ever does drive the attack**: a route attacked with the wrong
credential class passes isolation for the wrong reason, which is the failure mode the gauntlet
exists to prevent. **The consequence today**: a reader of `targets.ts` learns something about
a route that may not be true.

**This chapter widens it by three**, and it widened it while deciding the decorators — analysis
pass 6 chose the `@Accepts` values and created a second home for them in the same breath,
without noticing the first home already existed. Pass 7 found that.

**Owner: whoever adds a route with a non-default accepted set, or an isolation chapter.** The
remedy is a test that reads the reflector metadata for each controller method and compares it
with the declared entry — the same shape `targets.itest.ts` already uses for existence, one
field over. It goes red on any entry that is already wrong, which is why it is a decision.

**The same shape as two recorded defects**: chapter 3.22's `policy.ts`, where a stated
derivation and a shipped constant disagreed by a factor of three, and `eslint.config.mjs`'s
two lists whose own comment says *they MUST AGREE* and which nothing compares.

## 5. A CLOSED CHAPTER'S TWO RECORDS DISAGREE, AND THIS CHAPTER ALMOST INHERITED IT — NEW, OPEN

Chapter 3.22's own close-out records give two different numbers for the same thing:

    specs/040-chapter-3-22/baseline.txt      "Thirty-seven new tests read one at a time"
    specs/040-chapter-3-22/chapter-notes.md  "40 new tests"

Forty is right. That chapter's **last commit before tagging** was *"40 new tests, not 37 — 17
plus 20 plus three, and two changed"* — it corrected `chapter-notes.md` and left `baseline.txt`
standing, then tagged and pushed.

**This chapter cited the uncorrected one** in its title-reading task for eleven analysis passes,
which is exactly the class chapter 3.22 recorded as *its own most common defect*: a premise
inherited from a predecessor's record and never re-run. Found in pass 11 by taking every number
this chapter attributes to another chapter and reading it in that chapter's files. Six of seven
held; this was the seventh.

**Owner: whoever amends a closed chapter's records, or nobody.** The uncomfortable part is that
`part3-ch22` is tagged and pushed in three repositories, so correcting it edits a published
record — which the series does do, for published *chapters*, and has no convention for doing to
a `specs/` ledger.

**The instrument that could catch it is this chapter's**: `check-prose.py` fails on a superseded
sentence, and *"Thirty-seven new tests read one at a time"* is one. Adding the fragment costs a
line and makes the next chapter's inheritance impossible rather than unlikely.

**CLOSED IN PHASE 8, AND THE CONVENTION IS NOW ON RECORD.** The line was amended in place with
a bracketed note naming chapter 3.23 as the amender and saying what it said before — not
silently overwritten. That is the convention this item said did not exist: **a closed ledger's
factual error is corrected by annotation, so the correction is auditable and the original claim
is still readable.** A published chapter would take an errata note in its own prose; a `specs/`
record takes this.

**The other half stands.** `part3-ch22` is tagged and pushed in three repositories, so the tag
points at a commit whose `baseline.txt` still says thirty-seven. Nothing rewrites history to
fix that, and nothing should — the amendment lands on `main` after the tag, which is where the
next reader is.

## 6. drizzle-kit's SNAPSHOT IS SIX MIGRATIONS BEHIND THE DIRECTORY — NEW, OPEN

`services/api/migrations/meta/` holds snapshots through `0007_snapshot.json` while the
directory holds `0013_bot_users.sql`. Migrations 0008 to 0013 were hand-written and no
snapshot was regenerated, so **every `drizzle-kit generate` from chapter 3.9 onward has
produced a colliding number and a body that replays six tables and fourteen alters.** This
chapter's generation came out as `0008_message_edits.sql`, against an existing
`0008_limit_policy.sql`, and would have failed on `CREATE TABLE "quota_notifications"` had
anybody applied it.

It caused no damage in four chapters because ADR-16 requires the generated SQL to be reviewed
before it is applied, and every chapter since 3.9 has hand-written the file instead. **The
review is the control, and it worked here** — which is also why this is a gap and not a
defect: the safety net is doing the whole job, and the tool underneath it has been useless
since 3.9.

Two ways to close it, and they are not equivalent:

- **Regenerate the snapshots** from 0008 forward so `drizzle-kit generate` produces a correct
  diff again. Reconciles six migrations across four chapters, and the snapshot format is
  drizzle-kit's, so the work is not reviewable by reading §6.1.
- **Delete `meta/` and the `drizzle-kit generate` step**, and say in `drizzle.config.ts` that
  migrations here are hand-written and reviewed against SAD §6.1. That is what the last four
  chapters have actually done; the config's own comment already calls drizzle-kit's migrator
  and journal "deliberately unused".

**Owner: whichever chapter next adds a table.** It will run `generate`, get a colliding
number, and either discover this from scratch or read this item.

## 7. THE TENANCY CATALOGUE'S REACH WAS FIXED; THE GUARD'S COVERAGE WAS NOT — NEW, OPEN

`db/catalogue.ts` now follows foreign-key chains, so `message_edits` classifies as `hop`
through `messages`. That answers *can this table's rows be traced to one tenant*. It does not
answer the other half, which feature 030's trigger asks: **a table without an
`environment_id` has no trigger protecting it from a cross-environment write.**

`members` has been in that position since chapter 2.1 and migration 0011 names it as the
counter-example in writing. `message_edits` joins it, and the argument for leaving it there is
narrower than it looks: the table is append-only (FR-004 (3.23)), so there is no update or
delete for a trigger to refuse. **That argument is a claim about the code, not about the
schema** — nothing stops a later chapter writing an `UPDATE message_edits`, and the day one
does, the append-only justification is gone and no test says so.

The cheap instrument: a check that every table classified `hop` is either in a declared
append-only list or protected, red on an unknown member. **Owner: whichever chapter first
needs to mutate a `hop` table** — or the retention chapter, which will delete from several.

## 8. EIR-WS-06 IS STILL MET BY TWO CLOSE CODES OF SIX — CARRIED FROM 3.22, RE-MEASURED, OPEN

Chapter 3.22 left this at *"two of six"* in the error reference. **Re-measured across the
eight documents rather than carried**, and the count is unchanged — this chapter added no
close code, so the ratio held while nothing improved:

    4001  invalid or expired token      docs/04-srs.md              x1
    4002  protocol violation            docs/08-error-reference.md  x2
    4003  banned in this environment    nowhere at all
    4004  connection limit reached      docs/08-error-reference.md  x1
                                        docs/05-sad.md              x1  (new since 3.22)
                                        docs/07-tutorial-plan.md    x1
    4008  quota exhausted               docs/07-tutorial-plan.md    x2
    4009  server shutdown (drain)       docs/05-sad.md              x1

`CLOSE_CODES` has exactly these six, verified against
`relay-platform/packages/protocol/src/codes.ts` rather than against the predecessor's list.

**One thing did change and it is not an improvement in the clause's terms.** `4004` picked up
a second and third mention — chapter 3.22's ADR-23 in the SAD, and its row in the tutorial
plan — so the code a customer is least likely to hit is now the best documented, while
**quota exhaustion still appears in no published document** (`docs/07-tutorial-plan.md` is
deliberately excluded from `sync-docs.sh`) and `4003` appears in none of the eight.

The clause names four classes: authentication failure, quota exhaustion, server shutdown,
protocol violation. The error reference documents **one** of the four. That number has not
moved since 3.22 measured it.

**Owner: the next chapter that adds or renames a close code**, and the remedy 3.22 wrote is
still the right one — teach `check-error-codes.mjs` to read `CLOSE_CODES` beside `ERROR_CODES`
and require each to be named in `docs/08-error-reference.md`, then write the four sections
that make it green. **Do not close it with a `## 4001` heading**: that script's orphan check
fails on any `## ` heading that is not a member of `ERROR_CODES`, with no exemption. The
convention is chapter 3.21's — the close code lives inside the `**Status:**` line of the error
code that carries it.

**Why this chapter did not close it.** It added two ERROR codes and no close code, so the
work is entirely somebody else's clause, and the four sections it would owe are about
authentication, quota, drain and protocol violation — none of which this chapter touched.
Recorded rather than done, with the numbers re-taken so the next reader inherits a
measurement rather than a claim.
