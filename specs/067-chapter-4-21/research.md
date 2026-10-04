# Research — chapter 4.21, "Erasure, and every path it must find"

Every number here came from the running stack on 2026-10-04, not from reading.
Where a measurement contradicted something already written down, the
contradiction is the entry.

## R1 — `analytical records` is four stores with four different answers

FR-MOD-04 names *messages, memberships, profile, and analytical records* in one
phrase. The last is not one thing.

```
POSTGRES
  usage_active_users     22,150 rows · 22,147 distinct users · DELETABLE,
                         and `deleteUser` keeps them ON PURPOSE

CLICKHOUSE (relay_analytics)
  api_requests          205,697 rows · NO user column at all
  connection_events       1,081 rows · user_external_id String · DELETABLE
  message_events              0 rows · user_id Nullable(UUID) · no producer
  daily_usage_billing       824 rows · AggregateFunction(uniq, Nullable(UUID))
  daily_usage_v2             56 rows · the same
```

**THE BIGGEST ANALYTICAL TABLE NEEDS NO ERASURE AND THAT IS A DESIGN RESULT, NOT
LUCK.** `api_requests` carries `principal_kind` and no identifier — chapter 4.4
decided that deliberately, and 205,697 rows are outside this clause because of
it. The chapter should say so: the cheapest erasure is the column that was never
collected.

**AND `message_events` NEEDS NONE FOR A DIFFERENT REASON.** It holds 0 rows and
nothing under `services/` writes it (`gaps.md` 051). Two tables needing no work
for two unrelated reasons is worth separating, because collapsing them into
"nothing to do" hides that one is a design and the other is a defect.

## R2 — a `uniqState` cannot have one member removed, and on this lane it holds nothing

880 rows across `daily_usage_billing` and `daily_usage_v2` carry
`AggregateFunction(uniq, Nullable(UUID))`. A `uniq` sketch is lossy by
construction: there is no operation that removes one element, and no way to ask
whether a given user is in it. **Erasing a user from those rows is not difficult;
it is undefined.**

The only repair is recomputation from the source, and the source is
`message_events` — **0 rows, no producer, and a 90-day TTL**.

**AND THE SKETCHES CLAIM ZERO DISTINCT USERS TODAY.**

```sql
SELECT uniqMerge(active_users_state) FROM relay_analytics.daily_usage_billing  -- 0
```

**BOTH HALVES HAVE TO BE PUBLISHED AND EITHER ALONE MISLEADS.** *"A user cannot
be erased from the rollups"* overstates it — there is nothing in them. *"The
rollups are empty"* hides a clause the platform cannot satisfy the day the
source gains a producer. This is chapter 4.19's shape: the boundary is two
numbers and one of them would have misled.

## R3 — ClickHouse has two deletion verbs and only one is visible to the next statement

Measured on a 1,000-row probe table, planted and dropped:

```
DELETE FROM … WHERE user_external_id='u3'      count() immediately after:  900
ALTER TABLE … DELETE WHERE user_external_id='u4'
                                                count() immediately after:  900
                                                system.mutations not done:    0
rows on disk when both had settled                                          800
```

**THE LIGHTWEIGHT `DELETE` IS VISIBLE TO THE VERY NEXT `SELECT`; THE MUTATION IS
NOT.** `ALTER TABLE … DELETE` returned with its hundred rows still countable.
That is `gaps.md` 051's finding — *a mutation is not a delete; it returns before
it acts* — and the contrast is new: this server offers a form that does not have
that property.

**THE PROBE ABOVE IS ABOUT THE VERB, NOT THE PREDICATE.** It deletes by
`user_external_id` alone because the throwaway table has one tenant's worth of nothing
in it. **The real statement carries `environment_id` as well** — R8 measures why, and a
reader copying this shape rather than that one deletes other tenants' rows.

**DECISION: lightweight `DELETE FROM`** — and the reason below was wrong on first
writing, which is worth keeping. It said *"a receipt states a count, so it must use the
verb whose count it can trust."* **Neither verb returns a count through this client.**
Measured at pass 4 in the shape `AnalyticalStore.query` actually issues: a `DELETE`
answers HTTP 200 with a **0-byte body**, so the method's `string[][]` comes back empty.

**THE COUNT IS A SEPARATE `SELECT` EITHER WAY, AND THAT IS WHAT DECIDES THE VERB.** After
the lightweight form a `SELECT count()` is accurate; after the mutation it is not, because
the rows are still there. So the receipt can **verify** with one verb and only **predict**
with the other — the same conclusion, resting on something that exists. The
mutation form would need a poll of `system.mutations` and the receipt would
still be reporting an intention rather than a result.

## R4 — FR-USR-05's deletion already exists and deliberately keeps what erasure must destroy

`Repository.deleteUser` has shipped since the user-surface chapter. Its own
comment is the clearest statement of the conflict:

> **WHAT GOES**: the profile fields, the memberships, the read positions.
> **WHAT STAYS**: the row, the messages, and every `usage_active_users` row.
>
> `usage_active_users` IS UNTOUCHED (FR-029). Billing history does not vanish
> with a profile — a customer who deleted a user in March still owes for March.

FR-MOD-04 requires erasure of *messages … and analytical records*. So on three
of the things `deleteUser` keeps, the two clauses give opposite answers, and
**both arguments are good**: billing history is a financial record and a
compliance erasure is a legal obligation.

**AND `ON DELETE SET NULL` IS THE OPTION THAT WAS ALREADY REJECTED, WITH A
MEASUREMENT.** All five foreign keys to `users` are `NO ACTION`, measured —
because nulling `messages.user_id` *"satisfies the letter of preserving their
messages and breaks delivery: the resume path drops a senderless row, so every
message a deleted user ever sent would vanish from every reconnecting client."*
**A chapter that reaches for `SET NULL` is reaching for a thing this platform
measured and refused.**

## R5 — the receipt is the clause's least defined word

FR-MOD-04 says *returning a completion receipt* and says nothing about what it
attests. A 204 satisfies the grammar and nothing else.

**DECISION: a per-store outcome with a count and a reason.** The driver is R1
and R2: this erasure genuinely cannot clear one of its stores, so a receipt that
lists only what it did would be true and misleading. A compliance officer
filing it needs to see the store that was not cleared **named**, with why.

Rejected: a boolean; a status code; a free-text note. Each of them makes the
un-erasable store indistinguishable from one that had nothing to erase, which is
precisely the distinction the receipt exists to carry.

## R6 — the route, and what it costs to add

There is no erasure endpoint and no `erase` in any controller. Chapter 4.20
added the first `environments` controller and its shape is the precedent:
`@Controller`, `@UseGuards(CredentialGuard)`, `@Accepts("application")` at class
level, with the decorator as the decision rather than a branch in the handler.

**AND THE ROUTE GOES IN THE CONTROLLER THAT ALREADY EXISTS.** `@Controller("v1/users")`
carries `@UseGuards(CredentialGuard)` and `@Accepts("application")` at class level and
already holds `@Delete(":externalId")` — FR-USR-05's deletion. Measured at analysis pass 1:
**`users.controller.ts` is 4 pages with 0 appendix hunks against `app.module.ts`'s 23 with
4**, so a new module would cost 19 extra pages to duplicate three decorators. **And the
cheaper option serves the contract better**: the two `DELETE`s must not be confused, and
side by side in one file they are harder to confuse than in two.

**THE FENCE BILL, COUNTED NOW** — 4.15's rule, and chapter 4.20's correction
that the count must be derived from what the tasks touch rather than remembered:

```
                                   pages   appendix hunks already carried
repository.ts                         52   6
schema.ts                             34   6
vitest.coverage.config.mts            23   17
targets.ts                            13   5
gauntlet.itest.ts                     13   7
users.controller.ts                    4   0
---- free, and still owed an entry
moderation-routes.ts                   0   0
---- possible
users.module.ts                        5   1   if a provider is registered
users.schema.ts                        4   0   if the profile's shape moves
---- NO LONGER TOUCHED
app.module.ts                         23   4   the route joins an existing controller
```

**COUNTED, NOT REMEMBERED.** A first draft of this section carried 8 / 8 / 4 /
17 / 5 / 8 from the shape of chapter 4.20's bill; the real appendix figures are
6 / 6 / 4 / 17 / 5 / 7. The pages are unchanged and the hunk counts were wrong
in five of six places, which is what a count taken from a pattern rather than a
`grep` is worth.

Six again, and the same six, because the shape of the work is the same shape:
a route, a classification, a repository method, a pin. **`moderation-routes.ts`
is 0 pages and still needs an entry** — the route is mutating and
tenant-reachable, so `moderation-routes.itest.ts` fails in both directions until
it has one. FR-013 says the classification is `moderation` this time, and the
cost that made chapter 4.20 answer `not-moderation` is the one to re-check: an
`audit_log` entry needs a `target_kind`, and `user` is already in the CHECK.

## R7 — DR-15's prefix is for tenants, not users

> *Object keys shall be `{environment_id}/{media_id}` — tenant-prefixed so
> bucket-level lifecycle rules and tenant export/erasure operate on prefixes.*

Verified against real keys: `186db3ef-…/27706e73-…`. **There is no user in the
path.**

**AND THE TWO CLAUSES THE PREFIX SERVES ARE BOTH UNBUILT**, which is worth naming because
the first draft of this section said only that DR-15 *"does not claim this"* — true, and
silent about which clause does. *Tenant export* is **FR-MOD-05** and *tenant erasure* is
**FR-TEN-08** (*"Deleting an application shall irreversibly delete all associated
operational data within 30 days"*). Neither exists: there is no application-delete route,
and `schema.ts:113` says so in its own words — *"Deletion (FR-TEN-08) needs machinery this
chapter does not…"*

**SO DR-15's JUSTIFICATION HAS HAD NO CALLER FOR THE WHOLE SERIES.** The key layout was
chosen for two operations nobody has built, and this chapter is the first thing to erase
anything — by a path the prefix does not help. That is `unreferencedMediaIn`'s shape one
level down: a decision taken for a caller that has not arrived, correct when written and
still waiting. The clause is right about what it claims and does not claim this, so
FR-MED-10's *a user's media objects* is a database lookup and one store request
per object — the same per-object cost chapter 4.20 measured at 2.05 ms against a
message's 0.04 ms.

**AND `a user's media objects` IS UNDEFINED FOR 73% OF THEM.** 11,050 of 15,029
rows carry `user_id IS NULL`, which chapter 4.11 established was deliberate:
FR-MED-06 made the column nullable because a server-side upload has no user. An
erasure that takes the 3,979 attributed rows is correct and incomplete, and the
receipt is where that gets said.

## R8 — external ids collide across environments, and the analytical store is the one place nothing stops it

`connection_events` carries `environment_id UUID`, and external ids are unique **per
environment** rather than globally. Measured:

```
users: external ids reused across environments             1,576
connection_events: distinct external ids                      54
connection_events: distinct (environment, external id)       460
  …of those 54 ids, used in MORE THAN ONE environment         23

the worst one — `tuan`              111 environments · 156 rows
  correct for one tenant                                       4
  WRONGLY DELETED from 110 others                            152      97.4%
```

**AN UNSCOPED DELETE IS NOT A NEAR MISS. IT IS MOSTLY WRONG.** FR-008 required the scope
from the first draft of the spec, and its own Edge Cases named this exact collision —
and `data-model.md` wrote the statement without it anyway, sixty lines below the
requirement. Nothing contradicted itself in a way a reader would notice; the requirement
and the query were both right alone.

**THE REASON IS STRUCTURAL.** Six of the traversal's seven stores are reached through
`Repository`, whose constructor requires an `environment_id` — constitution I makes
tenancy a thing you cannot forget there. **ClickHouse is the only store that class does
not mediate, and it is the only one the draft got wrong.** The mechanism stops exactly at
that boundary, which is the same boundary chapter 4.20 reasoned about from the other
side when `retention-reads.ts` had to be unscoped on purpose and asserted its signature
instead of an arm.

So the erasure's analytical function **takes `environmentId` as a parameter**, and
`erasure.itest.ts` asserts that a second tenant's identically-named user is untouched —
which is the only assertion that would have caught this, because the route can refuse
correctly while the statement destroys a third party's rows.

## R9 — the external id reaches ClickHouse as SQL, and there is no type that makes it safe

`AnalyticalStore.query` takes a SQL string and **has no parameter binding**.
`request-log.module.ts:16` states it and names `endpoint` as *"the sharpest
caller-supplied value on this surface"* — chapter 4.8's defence there was a **closed set
derived from the running router**, and its remedy for the window was *a type, not an
escape*: what left the schema was a `Date`, so there was nothing to escape.

**NEITHER DEFENCE TRANSFERS.** An external id has no closed set — `users.schema.ts`
accepts `z.string().min(1).max(255)` — and no type narrows it. It arrives from the URL
path, which is not even parsed by a body schema.

**Measured end to end:**

```
POST /v1/users  {"external_id": "ev'il OR 1=1 --"}      201, round-tripped
SELECT count() … environment_id = '<absent>' AND user_external_id = '<that>'
  interpolated                                          1,081   the whole table
  bound, {env:UUID} and {uid:String}                        0
  bound, with `tuan` scoped — the control                   4
```

**AN ERASURE FOR THAT USER DELETES `connection_events` ACROSS ALL 460 TENANT-ENVIRONMENT
PAIRS.** It is 4.8's sentence word for word — *it does not widen the window, it defeats
the tenant predicate, because `OR` binds looser than the `AND` chain the scope is written
in* — **and it defeats the `environment_id` predicate R8 added.** R8 and R9 are one
surface, and R8 alone produces a statement that looks scoped and is not.

**DECISION: extend `AnalyticalStore` with bound parameters.** ClickHouse's HTTP interface
takes `param_<name>` against `{name:Type}` placeholders and the measurement above is the
proof. **Rejected: escaping at the call site** — an escape is a thing every future caller
has to remember, and this platform has deleted hand-maintained tables for less. The
binding makes the safe form the only form the method offers.

**THIS IS T013a's ADR CANDIDATE.** A capability added to a client three feature
directories already share is an architecture decision, where a line inside one function
would not have been.
