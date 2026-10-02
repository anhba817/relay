# Research — chapter 4.18, the log that cannot be edited

Every measurement below was taken on 2026-10-02 against the running stack, except where it
says otherwise. Where a question was answered by reading rather than running, it says that
too, because this project has found that the passes that RUN find the most.

---

## R1 — Which store holds the log?

**Decision: Postgres, the operational store.**

FR-005 settles it before any argument about query shape. An entry must be written as part of
the action it records, so that an action with no entry is unreachable — and the actions are
Postgres transactions. `banUser` is `this.db.transaction(async (tx) => …)`; so is
`deleteMessage`. A record written to another store cannot join a transaction in this one, so
the analytical path makes FR-001's *every* unachievable by construction rather than by
accident.

Constitution III points the same way and is worth stating explicitly, because a reader who
knows chapter 4.8 put the request log in ClickHouse will expect this one to go there too.
III's second bullet is *"Analytical events are emitted asynchronously — never synchronously on
the request path. Failure or backlog of the analytical pipeline MUST NOT affect … API
availability."* That is a promise the analytical path makes **and a licence it takes**: chapter
4.16 wrote *"a lost record is the accepted cost"* in as many words. A clause that says *every*
moderation action is recorded cannot be built on a path licensed to lose.

**And III is not engaged here**, which the plan says rather than leaves to inference. III
forbids *analytical queries against the operational database*. An audit log is neither — it is
operational data about operational actions, read the way a tenant reads its own channels.
Chapter 4.7 found the symmetric mistake: a Postgres read placed in `metering/` was refused by
a lint rule, because *the query engine lives inside the repository layer only*. The rule that
bites here is the same one, and it puts the write where FR-005 already needs it.

**Alternatives considered.** ClickHouse, rejected on FR-005 and on `ReplacingMergeTree`'s
semantics — chapter 4.8's table replaces a row with the same sort key, which is the opposite
of append-only. A second Postgres database, rejected: it moves the transaction problem without
solving it and adds a container, against constitution VII.

---

## R2 — What makes a table immutable, measured rather than assumed?

**Decision: a `BEFORE UPDATE OR DELETE` trigger that raises. Measured, including its two
bypasses, because the claim is only worth what the probe says.**

The api connects as `relay`, and `relay` is a **superuser** — `select usesuper from pg_user`
answers `t`. That matters more than any design preference:

    revoke update, delete on probe_immutable from relay;
    update probe_immutable set v='b' where id=1;        -->  UPDATE 1      the value changed

**`REVOKE` does nothing at all here.** A superuser bypasses privilege checks, so the obvious
mechanism is not a mechanism on this deployment. Nothing in the schema would look wrong; the
grant would be in the migration and the table would be mutable.

    create trigger probe_guard before update or delete on probe_immutable
      for each row execute function probe_refuse();
    update probe_immutable set v='c' where id=1;   -->  ERROR: audit entries are append-only
    delete from probe_immutable where id=1;        -->  ERROR: audit entries are append-only
                                                        rows after delete attempt: 1

A trigger fires for a superuser and refuses both verbs. **This would be the first trigger in
this schema** — `grep -rl "CREATE TRIGGER\|CREATE FUNCTION" services/api/migrations/` returns
nothing across twenty migrations — so it is a new mechanism and constitution VII asks for a
justification, which is R2 itself.

**AND THE TWO BYPASSES WERE MEASURED, BECAUSE A SECURITY CLAIM WITH NO ATTACK AGAINST IT IS A
COMMENT.**

    set session_replication_role = replica;
    update probe_immutable set v='d' where id=1;   -->  UPDATE 1      the trigger did not fire

    drop trigger probe_guard on probe_immutable;
    delete from probe_immutable where id=1;        -->  DELETE 1      the row is gone

One `SET` disables every trigger in the session, and a superuser may issue it. So the honest
claim — the one the chapter publishes — is: **the log is immutable to the application and to
accident, and it is not immutable to somebody holding the database password.** This platform's
api holds that password, which is the thing worth saying: a separate, non-superuser role for
the application would make the claim much stronger, and that is a deployment change rather
than a chapter. It is recorded as a gap with its cost.

The probe table and function were dropped before anything else was counted (043: *a red probe
writes to the lane, and the next measurement reads it as pre-existing data*).

**Alternatives considered.** Revoked grants — measured above, inert. Row-level security — a
superuser bypasses it too unless `FORCE ROW LEVEL SECURITY` is set, and it answers a different
question. Hash-chaining each entry to its predecessor — it detects tampering rather than
preventing it, which is a different and larger clause than FR-MOD-03 asks for; recorded as the
thing to reach for if the gap above is ever closed properly.

---

## R3 — What is the moderation set, and what keeps it honest?

**Decision: classify on the derivation that already exists, rather than build a second one.**

`services/api/src/isolation/targets.ts` already solves FR-003's exact problem for the
isolation gauntlet, and its own header says so:

> A LIST OF CLASSIFICATIONS, NOT A LIST OF TARGETS. The targets themselves are derived from
> the running application — `app.getHttpAdapter().getInstance().router.stack` — because the
> fault this suite exists to prevent is a route that exists and is unattacked, and only the
> router knows what exists. … **NOTHING MAY BE EXEMPT BY OMISSION.** A derived target matching
> no entry fails the suite, and an entry matching no derived target fails it too.

That pair of assertions is FR-003, already built and already passing. Writing a second
derivation would be a second thing to keep in step with the router.

**THE POPULATION IS 25, NOT NINE.** The spec's Context said *nine mutating routes a tenant can
reach* from a hand count. Parsing the table gives **33 mutating entries, 8 of them `/internal/`
— so 25 tenant-reachable routes to decide about.** The spec was counting the ones it expected
to include; the number that matters is the one the derivation will hand the checker, and a
decision is owed for every one of them.

**AND THE PARSE THAT PRODUCED 33 IS NOT THE DERIVATION EITHER.** A regex over the source found
**47** entries where `grep -c "method:"` counts **51** — four entries are shaped in a way the
pattern missed. Both numbers are estimates of a thing only the running router can state, and
the plan treats them as such: phase 1 derives the list from a booted application and writes
the real number down before any classification is made.

**Open, and the plan's first real decision:** whether the moderation flag is a field on
`targets.ts`'s existing entries or a sibling table with its own both-directions check. The
first keeps one list and couples two concerns — a security classification and a compliance
one — in a file 12 chapters publish. The second keeps them apart and gives the router two
tables to fall out of step with. **Deciding it needs the fence bill, which is R6.**

---

## R4 — How do the actor and the request id reach the write?

**Decision: a third constructor argument on `Repository`, not a parameter on every method.**

`Repository` is constructed with `(db, environmentId)` and has **six construction sites**, of
which five already hold the request:

    services/api/src/users/users.module.ts:33       new Repository(db, req.principal?.environmentId ?? "")
    services/api/src/media/media.module.ts:47       …
    services/api/src/messages/messages.module.ts:86 …
    services/api/src/webhooks/webhooks.module.ts:72 …
    services/api/src/channels/channels.module.ts:29 …
    services/api/src/auth/dev-token.controller.ts:119  new Repository(this.db, principal.environmentId)

So the actor and the request id arrive the way the environment already does: resolved once, at
construction, from `req.principal` and `req.requestId`. Every method keeps its signature, and
a method that writes an entry reads the context the way it already reads `this.environmentId`.

The alternative — threading `{actor, requestId}` through each method that records an action —
touches `repository.ts`, which **51 chapters publish**, once per method plus once per caller.
The constructor change touches it once.

**And the fields are already resolved.** `ApplicationPrincipal` carries `keyId`,
`UserPrincipal` carries `userExternalId`, `RequestWithPrincipal` carries `requestId`. Nothing
in FR-MOD-03's field list needs inventing, which is chapter 3.2's and 3.8's work being spent
rather than repeated.

**AND THE "CHANGED NOTHING" EDGE CASE FALLS OUT OF CODE THAT ALREADY EXISTS.** `banUser`'s
transaction reads:

    if (banned.length === 0) return [];

`isNull(users.bannedAt)` already makes a re-ban touch no row, and the guard already stops the
events. An entry written after that guard is written exactly when the state changed, so
FR-008's *"an action that changes nothing"* is answered by placement rather than by a new
branch. Expect the other actions to differ; the plan checks each rather than assuming this one
generalises.

---

## R5 — What does the read path look like?

**Decision: `GET /v1/audit-log`, modelled line for line on chapter 4.8's request log.**

`RequestLogController` is the precedent and it is close enough to copy the shape rather than
the code: `@UseGuards(CredentialGuard)`, `@Accepts("application")`, a **403 rather than an
empty page** for a principal carrying no environment — *"answering it with `[]` would say that
a tenant made no requests when there is no tenant in the question at all"* — and a query
schema built per request from an injected set rather than at import time, so it validates
against the router as it is now.

The same three decisions apply here, and the third one matters more: the audit log's filter is
an **action**, and the set of actions is R3's derived list. Building the schema per request
from the injected set is what stops the filter and the set drifting apart.

**Alternatives considered.** No read path at all, deferring it to the milestone at row 23 —
rejected on two recorded defects: chapter 4.6's rollup that nothing read and chapter 4.16's
column with one writer and no reader. A read path only for platform principals, rejected
because FR-006 is a tenant's own history and the milestone's audit step is Priya's, not an
operator's.

---

## R6 — What does this chapter cost the fence chain?

**Counted now, in research, because chapter 4.15's rule is that counting it after the work is
too late to change how the work is sequenced.**

    services/api/src/db/repository.ts        51 pages publish it
    services/api/src/db/schema.ts            33
    services/api/src/messages/messages.service.ts   27
    packages/protocol/src/codes.ts           24
    services/api/src/isolation/targets.ts    12
    services/api/src/messages/messages.module.ts     8
    services/api/src/users/users.service.ts          6
    services/api/src/users/users.module.ts           4
    services/api/src/channels/channels.module.ts     4

A titled fence is a whole-body claim (051-6), so every page above is a place the chain compares
this file. The chain holds one end state per file, so the bill is **one hunk set per file, not
per page** — but the files are the expensive ones, and the ordering follows:

1. **Concentrate the writes in `repository.ts`.** The lint rule requires it and the bill
   rewards it: entries written in six services would spread the change across six fenced files
   instead of one.
2. **Prefer the constructor to the signatures** (R4), for the same reason.
3. **Expect `codes.ts` and the appendix.** Chapter 4.11 found `codes.ts` hunks must go to
   `fences/post-series.md` because the appendix already amends that file twice, and chapter
   4.12 paid the same on `targets.ts`, whose entry sits next to a row the appendix adds.
4. **Count again after the repairs.** Chapter 4.17's bill was six files when the task list said
   one, and 4.15's was 19 hunks where the plan said six; the files that arrive late are the
   ones a list written once always misses.

---

## R7 — Retention, and the clause this chapter cannot discharge

**Decision: the year is stated and not enforced, and FR-MOD-03 is amended to say so.**

Nothing prunes an operational table in this platform. `schema.ts:867` already records pruning
as *named and deferred*, and FR-MOD-06's retention job is row 21 — three chapters away, and
the first thing that will need a scheduler. ADR-28 is the precedent and it is exact: chapter
4.9 recorded FR-ANL-06's *daily* as unmet by decision because **no scheduler of any kind
exists**, rather than building a sixth relay to satisfy an adverb.

So FR-MOD-03's *"retained for 1 year"* is met in the weak sense that nothing deletes an entry,
and unmet in the sense the clause means: there is no mechanism that would delete one at a year
and one day, and no mechanism that guarantees one survives to a year minus a day either. The
amendment names what would close it.

**And the log begins now.** Chapter 4.6's sentence is the one to borrow: *a rollup created late
is permanently short.* No entry exists for any moderation action taken before this chapter
shipped, and a reader of an empty window must not be left to conclude that nothing happened.
FR-011 is that sentence as a requirement.

---

## R8 — What erasure does to an entry naming an erased user

**Not decided here, and not this chapter's.**

FR-MOD-04 (row 22) permanently erases all data for a specified end user. An audit entry naming
that user is a record of a **moderator's** action, not the user's data — and the two clauses
point in opposite directions with no text in either acknowledging the other. Chapter 4.18
records the tension and ships the log; row 22 owns the resolution and will have the harder
half, because by then the entries exist.

What this chapter owes is that the tension is written down where row 22 will find it, rather
than discovered by the chapter that has to solve it. The spec's Out of Scope says so and the
clause record repeats it.
