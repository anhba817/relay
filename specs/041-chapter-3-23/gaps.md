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

## 9. A `.test.ts` IN THE DOCKER-FREE LANE NEEDS A RUNNING REDIS — NEW, OPEN

`relay-platform/services/gateway/src/connections.test.ts` calls `createConnections({ url: REDIS })`
against a real broker at six call sites. It is a `.test.ts`, so it runs in the lane chapter 2.1
built specifically to need no containers — the two-lane gate whose whole point is that `pnpm test`
is honest on a laptop with nothing running.

**Found by accident.** The compose stack went down mid-session, and `pnpm -s test` came back with
twelve failures reading `expected { kind: 'unenforced' } to deeply equal { kind: 'claimed' }` —
the connection cap failing open, correctly, because it could not reach Redis. The suite had been
green all session because a stack was up for other reasons.

**What it costs is not a broken test, it is a broken CLAIM.** The unit lane's exit code no longer
answers *"does this code work without infrastructure"*; it answers *"does this code work here,
today"*. A contributor with no Docker sees twelve failures that are not their fault, and a CI job
that skips containers for speed reports a defect that does not exist.

The fix is a rename — `connections.test.ts` -> `connections.itest.ts` — plus whatever the coverage
config pins by filename, and it is **not this chapter's to make**: chapter 3.22 wrote that file
and this chapter only ran it. Renaming it here would also move a file three chapters' fences
carry, for a reason the chapter does not teach.

**Owner: chapter 3.22's file, so the next chapter to touch the connection cap** — or whoever next
finds the unit lane red on a machine with no containers, which is how this one was found.

---

# CARRIED FROM CHAPTER 3.22, RE-CHECKED AGAINST THE TREE

Eight items closed with `part3-ch22`. **Each was re-measured here rather than copied**, which
is the discipline chapter 3.22 named as its own most common defect — a premise inherited from
a predecessor's record and never re-run. Three of the eight were addressed to this chapter.

## C1 (3.22 item 1) — EIR-WS-06 — **carried, and it is item 8 above with fresh numbers.**

Still two close codes of six documented, still one of the clause's four classes. Re-measured
across the eight documents rather than carried; `4004` gained two mentions and nothing else
moved.

## C2 (3.22 item 2) — the port collision a test could not see — **OPEN, unchanged.**

`main.test.ts` still binds port 0 and reads the assigned port back, which is what makes it
unable to see a collision on the configured one. Nothing in this chapter touches `main.ts` or
the port, so there is nothing here to re-measure and no reason the item would have moved.

## C3 (3.22 item 3) — an excerpt-only file is never verified — **OPEN, and this chapter did not widen it.**

`check-fence-chain.mjs:43` still skips a title containing `(excerpt)` or `.naive.`, and
`limits.itest.ts` and `session.itest.ts` are still the two files whose chains are excerpt-only.
**This chapter added no `(excerpt)` fence**, so the count is two, as 3.22 left it.

Worth noting for the next chapter: `session.itest.ts` is one of the three files this chapter
changed that no chapter fences, so its excerpt-only chain and this chapter's 200-line addition
to it never met.

## C4 (3.22 item 4) — `main.test.ts` checks that a module is CLOSED, not that it is PASSED — **OPEN, and addressed to this chapter.**

Re-read. The check is still about `close()`, and its own comment at `main.test.ts:81` says
what it cannot see: *"NOT awaiting it is what nothing could see."* A module built and never
handed to `attachSessions` still passes it.

**This chapter did not fix it, and it did the thing the item recommends instead**: the outsider
suite gained a test that drives an edit through the shipped binary end to end
(`packages/outsider/src/integrate.itest.ts`). That is the instrument that caught 3.21's inert
module, and it is the only one that would catch a fabric callback registered on a module
nobody passed. **A structural check would still be better** — the outsider test catches this
chapter's wiring, not the next chapter's.

## C5 (3.22 item 5) — the retry-log bound is a five-module decision — **OPEN, unchanged, and untouched here.**

## C6 (3.22 item 6) — five files discard their child's output — **OPEN, re-measured, and the number is now NINE.**

3.22 named five and recorded the decision not to fix them, with a measured cost: twelve
regenerated diffs across four chapters' fences. Re-counted here, `grep` finds **nine** files
spawning a child with its output discarded:

    pipe and never read     services/gateway/src/isolation.itest.ts
                            services/gateway/src/limits.itest.ts
                            services/gateway/src/public-surface.itest.ts
                            services/gateway/src/session.itest.ts
    stdio: "ignore"         services/gateway/src/membership.itest.ts
                            services/gateway/src/presence.itest.ts
                            services/gateway/src/meter.itest.ts
                            services/api/src/consumer/consumer.itest.ts
                            services/api/src/outbox/outbox.itest.ts

**Five was the gateway's count, not the repository's.** The api has two of its own that 3.22's
list never reached, and `meter.itest.ts` and `session.itest.ts` are gateway files it missed —
`session.itest.ts` reads its child's output only for the health-check failure message, and
discards it for every other failure.

This chapter paid the cost three times and knows the shape of it.

The coverage run that opened Phase 12 failed on `presence.itest.ts` — one of the
`stdio: "ignore"` five — with
`expected [ { type: 'presence.changed', …(1) } ] to deeply equal []`, and **the api child's
log was gone.** Two clean re-runs said flake, which is a conclusion reached by repetition
rather than by evidence.

**Then the close-out battery failed twice, on the same five tests both times**, with the
delivery describe's api child gone mid-describe — `ECONNREFUSED 127.0.0.1:4502` in run 2 and
`:4410` in run 20. `session.itest.ts` PIPES its child's output and reads it **only** to build
the health-check failure message, so 796 api log lines survive in each red log and not one of
them is from the child that died. `EADDRINUSE`, `FATAL`, `uncaught` and `ERR_SERVER` all
return zero, **and that zero proves nothing**: such a line would sit in an unread pipe.

An identical failure twice in twenty runs is not what a flake looks like, and this item is the
reason nobody can say what it is. `baseline.txt` carries the arithmetic — that file draws a
random port from one 200-slot range four times per run, which self-collides 2.96% of the time —
as a hypothesis, because a fix chosen from absent evidence is a guess.

**This battery is the occasion this item was waiting for.**

**Owner: unchanged — whoever next has a red run they cannot explain.** The list is longer than
3.22 thought, which makes the fix bigger and the argument for it stronger.

## C7 (3.22 item 7) — coverage cannot see an omission — **ANSWERED IN PART, and this chapter tested the answer.**

`**/main.ts` is still excluded from the ratchet, so the shape of 3.21's defect is still
invisible to coverage. What 3.22 added was the outsider suite as the instrument that CAN see
it, and this chapter is the first to use it for a feature rather than a fix: the edit's
end-to-end test. It found nothing wrong with the wiring, which is the outcome an instrument
should mostly produce.

## C8 (3.22 item 8) — `sweep.py` and `check-refs.py` have no owner — **OPEN, for the FIFTH chapter, and this chapter made it worse.**

Three per-chapter copies now exist — `039-`, `040-`, `041-` — and this chapter added
`check-prose.py`, a **fourth** instrument with the same no-owner problem. All four were
improved during this chapter (`check-refs.py` gained a criterion-tracing rule and had a
message corrected; `sweep.py` had a heading pattern fixed; `check-prose.py` was written and
then had an entry deleted for crying wolf), and none of those improvements will reach chapter
3.24 unless somebody copies the right one forward.

**The copy-forward is where the rot is**: this chapter's copy arrived with 31 stale `FOREIGN`
pairs from 3.22 and a docstring saying "chapter 3.21". Both were caught by running the thing;
neither would have been caught by reading it.

**Owner: still nobody, and the honest recommendation is unchanged** — move the four into a
shared `specs/_instruments/` with the per-feature configuration passed in, or accept that each
chapter re-derives the improvements it happens to need.

## THE ONE THAT IS NOT NUMBERED, BECAUSE TEN CHAPTERS HAVE NUMBERED IT

`specs/036-chapter-3-18/reader-protocol.md` — 45 minutes, six questions, one person who has not
read the chapter. **Chapters 3.14 through 3.23 have each named it and none has closed it**, and
this chapter is the tenth.

It cannot be closed from inside a session. Every check in this repository compares bytes:
`check:fences` compares a fence with a file, `check:figures` compares a prop name with a
component's, `check-prose.py` compares a fragment with a tree, and this chapter's four Python
instruments compare identifiers with identifiers. **Not one of them can answer whether a
paragraph is understandable to somebody who does not already know the answer.**

What this chapter would most want asked, if somebody did run it:

    1  Read "The fifth subject grammar" and say, without scrolling, why the edit could not
       ride the existing subject. If the answer is "because a tombstone has no text", the
       section buried its own point — that is the DELETION's reason, and the edit's is
       different and stranger.
    2  Read "The cursor's blind side". Say what a client should do about it. If the answer
       is "nothing, it is a bug", FR-016b failed: the bound is meant to read as a property
       of a cursor, not as an apology.
    3  Look at the message-life figure and say what happens to the sequence number. Every
       transition keeps it, and that one fact carries both FR-011 and FR-016a.

**An instrument that is easy to run tells you what it measures, not what you wanted to know**,
and ten chapters of that sentence have not produced the forty-five minutes.
