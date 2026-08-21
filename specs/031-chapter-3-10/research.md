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

The consequence, stated because it is a cost: the refusal is raised in the
repository layer, and each controller maps it to its own transport's shape. Two
mappings rather than one middleware.

**Alternatives considered**: a second middleware covering `/internal` would put
the check outside the transaction, making the overshoot unbounded under
concurrency instead of bounded by it, and would still miss any future caller of
`sendMessage`.

## R4 — The caps ride a query the request already makes

`environmentLimits(db, environmentId)` already reads the environment row on every
`/v1` request, for chapter 3.8's policy. The quota caps belong on the same row —
the shape 3.8 chose, nullable columns where null means "no override" — and the
usage row joins to it by `(environment_id, period)`.

**Decision**: one query returning limits, caps and current usage. FR-020 is then
satisfied by construction rather than by care: the send path gains no query, only
columns and a join on two primary keys.

The send path proper still needs the numbers inside the transaction, so the
transaction reads the usage row it is about to update — one indexed row, taken
`FOR UPDATE` alongside the channel row `sendMessage` already locks.

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

Chapter 3.8 shipped `rate_limited` with
`docs_url: "https://relay.example/docs/errors/rate_limited"`, which resolves to
nothing. This chapter adds a second code with the same problem.

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

## R12 — Size

Chapter 3.8 measured 4,781 prose words for half its subject and was split. This
chapter has three stories, four requirement groups and one migration. The
comparable chapter is 3.9 at 2,472 words for one story and one table.

The estimate is 3,000 to 3,600 words, and the estimate is not the gate — SC-009
counts the finished page. The phase order below puts the notification story
**last** so that the decision can be made with a number, which is the sequencing
3.8 established after three splits were discovered mid-chapter.
