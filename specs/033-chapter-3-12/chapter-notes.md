# Chapter 3.12 — what the plan said, and what shipped

Written before the pages, so the pages have something to be honest about.

**The first thing that shipped differently is the chapter itself.** The plan was one
chapter. The surface came to 61 changed files against an estimate of 37, so it is
three: **3.12** the gauntlet, **3.13** the endpoints and the instruments, **3.14**
the errors, the outsider and the Phase 2 verdict. The deferred public surface —
promised a number as 3.13 — became **3.15**.

The split was taken at the phase-11 boundary, before any chapter prose existed,
which is what the task arguing for it asked for. Nothing was discarded. Had it been
taken at the counting step where the tasks put it, three sections would have been
written and thrown away.

## The shape held

The suite derives its target list from the running router, classifies every route
as attacked or exempt-with-a-reason, and fails the build on a route that matches
neither. Four attack shapes, one indistinguishability oracle, the socket surface
attacked from the protocol's own frame union, and a structural check over the live
catalogue. Three reintroductions. All of that is what research settled and none of
it moved.

## Where the plan was wrong

**The count of what existed was wrong, and it was the chapter's own premise.** The
spec said "nine isolation assertions across nine files". Counted: **eleven across
eight**. A chapter whose argument is that nobody could say which endpoints were
attacked opened by not being able to say how many assertions there were.

**`data-model.md`'s `hop` rule would have classified neither hop table.** It said a
hop was a table where *exactly one* foreign key reaches a table carrying
`environment_id`. Both reach **two** — `channels` and `users` are each `direct` — so
the uniqueness reading fails totality on the two tables it was written to describe.
The rule is existence. Writing the query is what found it.

**T045 named a field the frame does not have.** It asked that `connection.ack`'s
`channel_ids` contain nothing of the other tenant's. The ack carries `user`,
`cursor`, `resume_ok` and `truncated`. `channel_ids` is the api's
`/internal/session` response, which the gateway turns into the subscription set —
so that IS where a leak would start, and the assertion moved there.

**T049 asked for a derivation that is not implementable.** "Derive the inbound
frames" — the frame union carries no direction metadata at all. The member list is
derivable and the direction is a classification, and the distinction had to be
written into the task before the test could be written.

**T074's premise named the wrong file.** It said `notifications.itest.ts` drives the
quota relay. It does not; `quotas.itest.ts` and `connections.itest.ts` do.

**T075 and T117 asked about fences that do not exist.** No titled fence anywhere
names any file under `packages/test-harness/`, and `sentinel.sql`, `exempt.ts` and
`limits.itest.ts` are in `post-series.md` nowhere. The whole package is outside the
fence chain, because feature 030 published no chapter and never fenced its own
files.

**T076's file was right and the plan's three other mentions of it were wrong.**
Research R17, plan R21 and an assumption all named
`services/api/src/limits/limits.itest.ts`. The `?? 4124` is in
`services/gateway/src/limits.itest.ts`. Two files share a basename and the api's
binds no port.

**The plan said "no ADR required", and FR-044 is why that needs restating** (T123a).
That claim was made before `@Accepts` grew a service argument. FR-044 changes what a
platform credential means at a route boundary: authorization by class becomes
authorization by class **and** service, and a thirteenth error code exists because
of it. It is still not an ADR — it narrows an existing decision (ADR-15's guard
boundary) rather than choosing between alternatives, and the alternative it rejects
(a generic `forbidden`) was already rejected by chapter 3.2 for
`wrong_credential_type`. But the claim should be read as *"no ADR required, and the
one candidate was FR-044, narrowing rather than deciding"* rather than as a survey
that found nothing.

## What implementation found that reading could not

**Fourteen passing tests meant nothing.** Every assertion in the gauntlet compares
two refusals for sameness, and two refusals for an unrelated reason are also
indistinguishable. Three control tests now prove the attacker's credential works
before anything asserts that it fails.

**The first reintroduction stayed green.** `environment_id` dropped from
`listMessages` changed nothing observable, because `channelExists` is scoped and
runs first. The suite is sensitive to the outermost check on a path and blind to an
inner one a live outer check masks — a fact about its range that no amount of
reading produced, and the reintroduction was not reshaped until it failed.

**Breaking indistinguishability takes an unscoped read.** The task said "change one
endpoint's 404 to a 403"; doing that at the route level moves both halves of the
pair and the oracle cannot see it. The realistic fault is a "helpful" unscoped
existence check.

**FR-044's hole was inside the chapter's own test suite.** `usage.itest.ts`
presented the dispatcher's credential to the gateway's route for a whole chapter and
passed. Nine of its fifteen tests turned 403 the moment the route declared its
service.

**A REST-sent message reaches no socket, ever.** Two independent mechanisms: the api
publishes to no fan-out, and the public send attributes no user so `toFrame` drops
the row from resume. `packages/e2e` never noticed because every message in it is
socket-sent. Recorded as gap G1 with both candidate fixes named as product
decisions.

**No validation error in the api had ever named its field.** EIR-API-06 has asked
since chapter 1.3 and `errorFrameSchema` declares `field`; `ZodValidationPipe` threw
`issues[0].message` and discarded `issues[0].path` for twenty-two chapters.

**`createUser` had `createChannel`'s fault and R14a named neither.** Third function
on the same request path, same unique violation, same `internal_error`.

**The lint ban was off for every integration test, and then off again for the
outsider.** R23 found the first instance. The second was in the seal written by
whoever had just finished fixing the first: the outsider's block sat before the
`**/*.itest.ts` blocks, and its only file is an `.itest.ts`, so a later block set
the rule again and won. `npx eslint` on a file importing `@relay/protocol` reported
nothing.

**Three instruments had never produced output.** `attack.ts` at 61% branches,
`targets.ts` at 50%, `catalogue.ts` at 87.5% — every uncovered arm in code that runs
only when the platform is broken. Closing them meant separating the decision from
the transport in three places.

**The fence chain taught three things about itself.** A titled fence states the
whole file, not an excerpt (26 excerpts produced 43 problems). One full fence per
path (replacing all of them gave 4,995 lines because six paths were fenced twice). A
diff fence needs a predecessor in the chain, and `usage.itest.ts` had never been
fenced by anything.

**A reverted reintroduction must not be fenced with a title.** The chain replays
titled fences onto the canonical tree, so a title on the T066 specimen would have
put a reintroduction into the repository — which is what FR-015 forbids.

**`docker compose --profile services up` serves whatever was last built**, and the
sealed suite reported six failures against a healthy stale stack: 404s for routes
that exist and a `docs_url` from two chapters earlier. `--build` is now its own line
in the README, the quickstart and the CI job.

**The bait for a new guarded table must not be claimable.** Extending the guard to
`quota_notifications` with an undelivered bait row failed thirteen tests in two
unrelated files. Fourth measurement of the same law.

## Two mistakes of process, both recorded because they recur

**`git checkout` on a file with uncommitted work destroyed it, twice.** Phase 3's
`deriveTargets` and Phase 9's five error codes plus `docsUrl`. Phase 7's
reintroductions were safe because the tree was committed first, which is this
project's own written rule.

**The twenty-run battery failed on run 11 and the cause was the operator.** Two
Next.js dev servers were compiling a 3,000-line MDX page on the same machine while
the api child had 30 seconds to boot NestJS. Nothing held a port in the range, no
`EADDRINUSE` appeared, and the run finished 57 seconds short of the mean. Restarted
on a quiet machine.

## Left undone, with owners

**The outbox keeps message text for ever** (T124). `drainOutbox` sets `published_at`
and never deletes; nothing in the api deletes a row from any table; the payload is a
full copy of the message including `data.text`; **286,871 rows** in the test lane.
It collides with DR-06, FR-MSG-08, FR-TEN-08 and FR-MOD-06. The fix is
`DELETE FROM outbox WHERE published_at < now() - interval 'N days'` and needs no
tenant identifier. **Owner: whichever chapter builds FR-MOD-06** — Phase 3's
retention work and Part 4.

This was reported as a tenancy violation first and the reversal is the useful half:
three of the four arguments for that reading collapsed on checking. Adding
`environment_id` would have been the wrong fix, because the outbox's legitimate
mutation *is* cross-environment and a tenant column would make feature 030's guard
refuse the relay's own sweep.

**A REST-sent message reaching a socket** (gaps.md G1). Owner: FR-RTM-05's chapter.

**`POST /auth/dev-token`'s status is documented nowhere** (gaps.md G5). Owner: 3.15,
with the rest of the public surface.

**The series documents two ports for each of Postgres, NATS and Redis**, sometimes
inside one chapter. Out of scope here — a documentation pass with a fence chain
behind it. Recorded in `baseline.txt` with the chapter-by-chapter inventory.

**A human external-developer run.** This chapter measured whether the documentation
*contains* what an integration needs. Whether a person reading it unaided can build
one is a different question, and a person is the only instrument for it.
