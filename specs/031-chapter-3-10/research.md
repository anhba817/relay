# Chapter 3.10 — research

Measured against the developer database this repository has been accumulating
since Part 2: 198,690 messages, 10,217 channels, 26,331 environments.

## R1 — Deriving usage on read is cheap today and will not stay cheap

The simplest design reads the answer straight from `messages`, and FR-002 —
usage must survive a counter-store flush — is satisfied for free, because the
messages *are* the record.

```
select count(*), count(distinct m.user_id)
  from messages m join channels c on c.id = m.channel_id
 where c.environment_id = $1
   and m.created_at >= date_trunc('month', now() at time zone 'utc');

Planning Time: 3.035 ms
Execution Time: 1.189 ms          -- busiest environment, 507 messages
```

One point two milliseconds. It would be easy to stop here.

The number is a measurement of a small tenant, not of the query. `messages`
carries **no `environment_id`** — it hangs off `channels` — so the plan is driven
from `channels_environment_id_external_id_unique` and then walks that
environment's messages through `messages_channel_id_sequence_unique`. **There is
no index on `messages.created_at`.** So the work is proportional to everything the
environment has ever sent, and the month predicate is a filter applied after the
rows are read, not a way of avoiding reading them.

The same query across every environment, which is what a monthly report would do:

```
Seq Scan on messages m  (actual time=0.011..25.132 rows=198690.00 loops=1)
Execution Time: 79.807 ms
```

**Decision**: a roll-up. Not because 1.189ms is slow, but because this project has
now recorded eleven occurrences of one fault — a fixed budget against a growing
shared resource, passing until the resource outgrows it — and putting a
tenant-sized scan on the send path is that fault written into the product instead
of into a test. FR-020 says so directly.

**Alternatives considered**: an index on `(channel_id, created_at)` makes the
month predicate an index condition and defers the problem rather than removing
it; the work is still proportional to one month of one tenant's traffic, on every
send.

## R2 — The distinct-user count is the part that cannot be incremented

A message count is `+1`. A distinct-user count is not: incrementing it requires
knowing whether this user has already sent this period, which is a read.

**Decision**: a membership row per user per period —
`INSERT … ON CONFLICT DO NOTHING` — and the count is the number of rows. The
insert is unconditional, the conflict clause makes it idempotent, and the count
is an index-only scan over a range that is bounded by the tenant's actual user
count rather than by their traffic.

**Alternatives considered**: HyperLogLog in Redis is the textbook answer and is
refused by FR-002 — a flush would erase the month. `count(distinct user_id)` over
messages is R1's problem again. A `last_seen_period` column on `users` avoids the
extra table and cannot answer "how many in *March*" once April starts.

## R3 — The enforcement point is not where the limiter's is

`operationsFor` returns `[]` for any path outside `/v1`, so chapter 3.8's
middleware does not see `/internal/messages` — the route the gateway posts to when
a WebSocket client sends. That is right for a *rate* limit: `/internal` is
service-to-service, and limiting it would limit the gateway rather than a tenant.

It is wrong for a quota, which is about what the tenant consumed regardless of
which door it came through.

**Decision**: enforce inside `Repository.sendMessage`. Both routes call it, and it
already opens the write transaction — so the check, the message insert and the
usage increment commit together, which is what bounds the overshoot the spec's
edge case admits to. Constitution IV: the single writer for a message is also the
single writer for the count of messages.

**An earlier draft of this section claimed a cost that does not exist**: "the
refusal is raised in the repository layer, and each controller maps it to its own
transport's shape — two mappings rather than one middleware". Neither half is
true, and both were assumed rather than checked.

The two routes converge before they reach the repository. `internal.controller.ts`
calls `this.messages.send`; `messages.service.ts:43` calls `this.repo.sendMessage`.
One service method, not two paths.

And nothing maps errors per controller. `ProtocolErrorFilter` is `@Catch()`-all and
registered globally through `APP_FILTER` in `app.module.ts`, and chapter 3.2
already established how a thrower names its own code: throw an `HttpException`
whose response object carries `code`, and the filter emits the four-field envelope
with `docs_url` derived from that code. Two hand-written envelopes would be exactly
the drift EIR-API-04 and that filter exist to prevent.

**So the refusal is one throw**, from the service boundary, and the transport shape
is somebody else's already-solved problem.

**Alternatives considered**: a second middleware covering `/internal` would put
the check outside the transaction, making the overshoot unbounded under
concurrency instead of bounded by it, and would still miss any future caller of
`sendMessage`.

## R4 — The caps are read once, inside the transaction, and nowhere else

The first version of this section proposed extending
`environmentLimits(db, environmentId)` — the per-request policy read chapter 3.8
added — to return the quota caps and current usage as well, so that "the request
path gains no query".

**It was solving a problem the design does not have, and it would have created
one.** Two things it missed:

- **`environmentLimits` has a second caller.** `internal/session.controller.ts:67`
  uses it to hand the gateway its connect and send limits on every WebSocket
  connect — the gateway has no database and must not gain one (chapter 3.8's R12).
  Extending the function makes every connect pay for a usage join it never reads,
  and renaming it edits a response shape that is a contract with another service.
- **The middleware read would be advisory anyway.** Enforcement happens inside the
  send transaction (R3), where the row is taken `FOR UPDATE` to bound the overshoot
  (R8). A cap read in middleware and re-read in the transaction is the same data
  fetched twice, and only the second one decides anything.

**Decision**: `environmentLimits` is untouched, and the caps and usage are read
exactly once — in `sendMessage`'s transaction, one indexed row taken `FOR UPDATE`
alongside the channel row it already locks.

FR-020 is satisfied on its own terms rather than by the trick: it forbids a query
that **scans the message table**, and this adds two index lookups inside a
transaction that was already open. It does add a query, and saying otherwise was
the error pass 1 caught in T018.

## R5 — There is no sweep, and that is the interesting result

The obvious shape for "email at 50%, 80% and 100%" is a periodic job that walks
every environment comparing usage to cap. That job is a global operation, which
means feature 030's trigger, an entry in `exempt.ts` with its tables, a matching
entry in the lint ignores, and a test that has to be written to survive both.

None of it is necessary. **Usage only ever increases because of a send**, and a
send already holds the transaction that increments it. The increment knows the
value before and the value after, so it knows exactly which thresholds the
increase crossed. A row is written for each, in the same transaction.

The one crossing that happens without a send is a cap *lowered* below current
usage — a configuration change, which is also a transaction, and can write the
same row.

**Decision**: no periodic quota sweep. FR-021 is satisfied vacuously and no file
joins the exemption list.

This is worth naming rather than passing over. Feature 030 spent its whole
existence on the cost of global operations in this codebase, and the first chapter
written after it turns out not to need one. The instrument changed the design, not
just the tests — which is the outcome SC-008 of that feature was hoping for and
could not measure.

## R6 — The outbox pattern, a fourth time

Chapter 3.3 published events, 3.5 dispatched webhook deliveries, 3.9 sent
disablement emails. Each is a table with a claim predicate that starts null,
drained by a relay, retried by falling due again. This chapter needs the same
thing for threshold emails.

`webhook_disable_notifications` cannot be reused: it is keyed by
`endpoint_id NOT NULL`, and a quota notification has no endpoint.

**Decision**: a fourth table, `quota_notifications`, with the same shape.

**Alternatives considered**: one generic `notifications` table with a `kind`
column and a JSON payload. It would remove the fourth migration and add a
discriminated union to every read, and the four kinds have genuinely different
columns — an endpoint url, a percentage, a period. Constitution VII asks what a
new abstraction buys; here it buys one fewer table and costs type safety at every
call site. Four concrete tables that look alike is a pattern; one abstract table
that serves four purposes is a framework.

The chapter should say the number out loud — this is the fourth — because a reader
who has seen it three times deserves to be told it is deliberate rather than
accidental.

## R7 — The period is a stored value, not a computed one

`date_trunc('month', now() at time zone 'utc')` is the period a send belongs to.
Storing it as a `date` column on the usage row rather than recomputing it in every
predicate means the primary key `(environment_id, period)` is the whole lookup, and
the month boundary is a different key rather than a different filter.

FR-003's "previous month remains readable" then costs nothing: the old row is
still there.

## R4a — The column was already there, and chapter 3.8 said so in print

Three analysis passes read these documents against each other, against the code,
and against the build gates. None read them against **the published series**, and
that is where this was:

```
app/(en)/part-3/chapter-08/limits-you-can-see-coming/page.mdx:254
  `environments` already had a column that looked right for this, and it was
  deliberately not used:

      quotaConfig: jsonb("quota_config").notNull().default({}),

  Declared in 2.1, named in SRS §6.1, empty for seventeen chapters — and named
  for **quotas**. […] Putting one into a field named for the other would collapse
  in the schema exactly what this chapter spends its length drawing.
```

And in `schema.ts`, byte-exact into that published page:

```
// DECLARED IN 2.1 AND STILL EMPTY. […] the column is named for
// quotas, quotas are a later chapter
```

This is that chapter. The plan added four typed columns beside it and left it
empty for an eighteenth, which would have made a published chapter's stated
expectation come to nothing without a word.

**Decision**: use `quota_config`. Shape:

```json
{ "messages":     { "hard": 10000, "soft": 8000 },
  "active_users": { "hard": null,  "soft": 500  } }
```

**What it buys.** Chapter 3.11 adds connection-minutes and FR-MED-12 later adds
media bytes; a new dimension is a new key rather than a table migration, which is
what `data-model.md` asked for and typed columns could not give.

**What it costs — measured, and less than expected.** The framing when this
decision was put was "no CHECK constraints possible, absent-versus-zero by
convention only". Both halves turned out to be wrong:

```
--- refuses a negative ---     ERROR: violates check constraint "environments_quota_config_shape"
--- refuses a non-number ---   ERROR: violates check constraint "environments_quota_config_shape"
--- refuses a non-object ---   ERROR: violates check constraint "environments_quota_config_shape"
--- accepts the real shape --- UPDATE 1
--- null / zero / absent ---   hard='10000' | explicit_null=t | absent=t   then  zero_reads='0'
```

`#>> '{messages,hard}'` returns SQL NULL for an absent key and for a JSON null
alike, and the string `'0'` for zero — so the null-is-not-zero rule chapter 3.8
needed nullable columns for survives intact, and non-negativity is enforced by the
schema rather than by the code.

**The real cost is one line.** The CHECK **enumerates** the two dimensions, so a
third one costs a constraint change to keep the guarantee. A constraint that
validated any dimension needs `jsonb_each`, and:

```
ERROR:  cannot use subquery in check constraint
```

which is feature 030's R37 met from the other side — there it was a trigger's
`WHEN` clause. The way around it is a PL/pgSQL validator, and a procedural
function in a **product** migration is a constitution VII argument this chapter has
not earned. Feature 030's guard is exempt precisely because it is never a
migration, and its own file says so.

**The second cost is a parser.** A jsonb column arrives as `unknown`, so
`quotas/config.ts` holds a zod schema and `capsFor()`. It **fails closed**: an
unparseable config yields no caps and an error to log, because a typo in an
operator's configuration should not suspend a tenant. `.strict()` on the shape
means a dimension nobody implemented is a parse failure rather than a cap the
operator believes in and the system silently ignores.

## R7a — `date` has no precedent in this schema, and it is a key

R7 chose to store the period rather than compute it. What it did not check is that
`date` is a type this project has never used:

```
$ grep -oE 'timestamp\(|date\(|integer\(|bigint\(' services/api/src/db/schema.ts | sort | uniq -c
     28 timestamp(
     12 integer(
      2 bigint(
```

None. And `period` is not an ordinary column — it is half the primary key of
`usage_periods` and a third of `usage_active_users`'s. Drizzle's `date` takes a
mode, string or `Date`, and a writer and a reader that disagree produce a lookup
that finds nothing rather than a type error. That is the failure shape this
project keeps meeting: correct in one place, silently different in another.

**Decision**: choose the mode explicitly, and prove the round-trip — insert with
the period the TypeScript function returns, look the row up by that same value,
get the row back — before the roll-up depends on it (T011a). `bigint` needs the
same treatment and already has an answer: both existing bigints declare
`{ mode: "number" }`.

## R8 — Overshoot is bounded, and the bound is stated

Two concurrent sends can both read usage below the cap and both commit. With the
usage row taken `FOR UPDATE` inside the send transaction they serialise per
environment, so the overshoot is at most one message — the one that crosses.

Without the lock it would be bounded by concurrency. With it, sends to one
environment serialise on one row, which is a throughput cost that has to be
measured rather than assumed. The plan schedules that measurement rather than
guessing at it.

## R9 — What "suspends the environment" is allowed to touch

FR-RTL-08 is unusually specific and the specificity is the requirement: sends
refused, history reads and existing connections unaffected. Three consequences
that are easy to get wrong:

- The refusal happens in `sendMessage`, so no read path can see it.
- The gateway holds the socket and the api refuses the send, so a refusal cannot
  close a connection — it is a message the client receives on a socket that stays
  open.
- Webhook delivery for already accepted messages continues, because constitution
  II says an acknowledged message is not lost, and a quota exceeded afterwards
  does not retroactively un-acknowledge it.

## R10 — The error code and the documentation that is not there

Chapter 3.8 shipped `rate_limited` with a `docs_url` that resolves to nothing, and
this chapter adds a second code with the same problem.

**The debt is older than 3.8 and already recorded in the code.**
`protocol-error.filter.ts` derives every `docs_url` from the code —
`` `https://relay.example/docs/errors/${code}` `` — and its header comment has said
since chapter 1.4: *"The docs_url host is a placeholder until the docs site exists
(constitution V's reachable-page promise)."* 3.8 inherited it; it did not create
it, and an earlier draft of this section said otherwise.

**Decision**: add the code, keep the `docs_url` shape consistent with 3.8, and do
not fix the underlying gap here. Chapter 3.12 is the Phase 2 exit criterion — *an
external developer integrates using only public documentation* — and a docs site
is that chapter's problem or its own feature. Recorded so it is inherited
deliberately rather than forgotten twice.

## R11 — The guard is live, and the chapter should be run against it once on purpose

Nothing in this design performs a global mutation, so nothing should trip feature
030's trigger. That is a prediction, and the way to find out it is wrong is to
have predicted it. The quickstart includes a step that runs the new suites against
a database with bait planted and asserts a green lane, which is a cheap way to
discover that some helper does sweep after all.

## R11a — The publication gate needs its own tasks, not just its own check

Six files this chapter modifies are already fenced, and they carry 47 fences
between them:

```
services/api/src/db/repository.ts             15
services/api/src/db/schema.ts                 10
services/api/src/app.module.ts                 8
services/api/src/messages/messages.service.ts  7
vitest.coverage.config.mts                     5
services/api/vitest.integration.config.mts     2
```

`check-fence-chain` replays every chapter's fences onto `relay-platform` and
compares byte for byte, so a modified fenced file with no new fence diverges the
replay. An earlier draft of the task list scheduled the check (T045) and none of
the work that satisfies it — which would have surfaced after the chapter was
written and translated, with the Vietnamese mirror to redo.

**And the fences do not all go to the same place.** A chapter may only fence a
change it discusses (chapter 3.8's T025e). The four product files are this
chapter's subject. The two vitest configs are not — adding a relay flag to a lane
is hygiene 3.10 never explains — so those extend the `post-series.md` sections
feature 030 already opened.

`app.module.ts` is on that list for a second reason: **nothing had said the module
needed registering.** The relay would have been written, unit-tested and never
started.

## R12 — Size

Chapter 3.8 measured 4,781 prose words for half its subject and was split. This
chapter has three stories, four requirement groups and one migration. The
comparable chapter is 3.9 at 2,472 words for one story and one table.

The estimate is 3,000 to 3,600 words, and the estimate is not the gate — SC-009
counts the finished page. The phase order below puts the notification story
**last** so that the decision can be made with a number, which is the sequencing
3.8 established after three splits were discovered mid-chapter.
