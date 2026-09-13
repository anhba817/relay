# Research — Chapter 4.1

Seven questions, each run against the tree rather than recalled. **Two of the answers
contradict what the plan assumed before research started**, and both are recorded with the
wrong version, because a correction nobody can see is a correction nobody can check.

---

## R1 — Is there a metering query to put under load?

**No.** `services/api/src/quotas/` holds no aggregate at all: no `count(`, no `sum(`, no
`countDistinct`. `credit.ts` is two pure functions:

    creditFor(reported, credited)      -> Math.max(0, reported - credited)
    highWaterMark(reported, credited)  -> Math.max(reported, credited)

**Decision**: the chapter's demonstration is the analytical query FR-ANL-05 and FR-ANL-09 ask
for, written against this schema for the first time. It is not a metering query and the chapter
does not call it one.

**Rationale**: a quota must refuse a send synchronously, so its counter cannot be an aggregate
and cannot be downstream of a lossy stream. Part 3 put it on the write path and was right.

**Alternatives considered**: inventing an aggregate for the chapter to benchmark — rejected as
a straw man, and the project's own rule is that a test which can only fail for somebody else's
reason proves nothing. Benchmarking the quota read path (`repository.ts:630`) — rejected: it is
a point lookup plus a `count(*)` over one period's rows, and it is fast for the same reason the
chapter is about.

---

## R2 — What does the analytical query actually have to do, and can an index serve it?

The operational table, read at `schema.ts` and not carried from any document:

    messages(id, channel_id, sequence, user_id, text, metadata, attachments,
             idempotency_key, created_at, edited_at, deleted_at)

    unique       (channel_id, sequence)                        DR-01
    uniqueIndex  (channel_id, idempotency_key) WHERE NOT NULL  DR-03

**There is no `environment_id` column and no index touching `created_at`.** Tenancy is reached
through `channels`. So FR-ANL-05's daily question is a join plus a scan:

```sql
SELECT date_trunc('day', m.created_at) AS day,
       count(*)                        AS messages,
       count(DISTINCT m.user_id)       AS active_users
FROM messages m JOIN channels c ON c.id = m.channel_id
WHERE c.environment_id = $1
  AND m.created_at >= now() - interval '90 days'
GROUP BY 1;
```

**Decision**: that query, unchanged, is what the chapter measures. SAD §6.2's ClickHouse table
is `ORDER BY (environment_id, ts)` — the two columns Postgres orders by neither of — so the
contrast is available without writing a word of ClickHouse.

**Rationale**: `sequence` is per-channel and monotonic within a channel only, so it cannot bucket
by day across an environment. `created_at` is the only temporal column and nothing indexes it.

---

## R3 — Does the analytical query count bots? **The first answer was wrong.**

**What was assumed**: that `count(DISTINCT user_id)` needed a `kind = 'person'` filter to match
the operational counterpart, because CLAUDE.md lists "bot exemption from the active-users cap"
as an open decision and FR-RTL-05 says *persons* where FR-ANL-05 says *users*.

**What is true**: the divergence is deliberate, decided, and written down twice. SRS §4.3's
chapter-3.17 amendment:

> **FR-RTL-05 is narrowed from "unique active users" to "unique active persons", and FR-ANL-05
> is deliberately unchanged.** A bot is metered like any user and is exempt from the enforced
> ceiling: the ceiling bounds a customer's human population, and a customer's own software
> should not be able to lock their people out of sending.

And the code agrees. `repository.ts:assertWithinQuota` throws on the **message** hard cap before
it consults `senderIsPerson`; the person check gates the **active-users** ceiling alone, 45 lines
later. `usage_active_users` receives a row for every sender, bot included.

**Decision**: the query counts every sender. No `kind` filter. FR-ANL-05 means what it says.

**How the wrong answer was reached, because the method is the finding**: the bot exemption was
searched for in `services/api/src/quotas/` and `services/api/src/messages/` and was not there.
It is in `repository.ts`. **A grep that covers the module named after the subject is not a grep
that covers the subject** — `docs/10-platform-review-fix-plan-2026-09-05.md` §0 had already run
this exact check and recorded the answer, and reading it would have been cheaper than four greps.

---

## R4 — Will the two sides of the reconciliation agree for the right reason?

Not in one case, and chapter 4.1 is where the Postgres side is written, so the case is recorded
here rather than discovered in movement IV.

`messages.user_id` is **nullable** — `uuid("user_id").references(() => users.id)` with no
`.notNull()`. FR-USR-05 keeps a deleted user's messages "as authored by a deleted user", and the
schema's own comment distinguishes that from "authored by nobody". Meanwhile
`repository.ts:3551` says of user deletion:

> `usage_active_users` IS UNTOUCHED (FR-029). Billing history does not vanish with a user.

So after a deletion the two sides diverge by construction: `count(DISTINCT m.user_id)` drops
NULLs silently, and the operational set keeps its row.

**Decision**: chapter 4.1 states the divergence where it writes the query, and files it for the
reconciliation chapter. It does not fix it — there is nothing yet to reconcile.

**Why it matters more than its size**: two counts that agree to 0.1% because both over-count, or
because the test corpus has no deleted users, is the vacuous-agreement shape this project has
found repeatedly. Movement IV's milestone needs to know the one input that makes the sides
disagree legitimately.

---

## R5 — How is the corpus built, and does anything in the repository build it?

**Nothing does.** `scripts/scale/seed.mjs` creates users and channels for NFR-SCL-01 through
`dist/db/repository.js` and writes no messages. The only comparable corpus this project has ever
built is the one behind the 159 ms figure, and
`specs/034-chapter-3-15/baseline.txt:153` says what became of it:

> The scratch database is not this lane and is not seeded by anything in the repository.

**Decision**: the seeder lands in `scripts/scale/`, writes messages in bulk, and is introduced by
this chapter. It does not go through the repository layer.

**Rationale**: the repository's `sendMessage` runs a transaction, an idempotency check, a quota
read and a sequence allocation per message. That path is the thing being measured, not the thing
that should build a million rows. Bulk insert must still satisfy the FKs to `channels` and
`users` and the `(channel_id, sequence)` unique constraint, so sequences are generated per
channel rather than globally.

**Alternatives considered**: reusing `seed.mjs` and looping sends — rejected on R6's arithmetic
alone. Restoring a dump — rejected: a corpus a reader cannot regenerate is not reproducible, and
SC-001 requires that they can.

---

## R6 — Can a send loop actually apply write load? **The second wrong assumption.**

**What was assumed**: that "under write load" meant saturating the write path.

**What is true**: `services/api/src/limits/policy.ts` sets `send: 600` and `rest: 600` per
environment per minute, and a REST send consumes both budgets. **That is ten sends per second**,
and the comment says the number is deliberate — *"1% of NFR-SCL-03's stated 1,000 messages per
second aggregate."*

**Decision**: the chapter measures **write latency**, not write throughput, and says so. Ten
sends per second for sixty seconds is 600 samples, which is enough to state a p95 and not enough
to call the database busy. The load that matters for the demonstration is the analytical query
itself.

**Rationale**: NFR-PRF-02 is *"REST write latency, excluding network, p95 < 150 ms"* — a latency
clause, and the comment on `rest: 600` says as much: *"no SRS requirement caps a tenant's request
rate; NFR-PRF-02's p95 under 150 ms is a latency target, not a throughput bound."* The chapter's
claim is that an analytical query makes a concurrent write slower, and that is measured with a
modest, steady send rate rather than a flood.

**Alternatives considered**: overriding the limit per environment (FR-RTL-04 permits it) —
available if 600 samples prove too few, and recorded as the escape hatch rather than taken by
default. Spreading the loop over many environments — rejected: it changes what is being measured,
since each environment has its own counters.

---

## R7 — Where do the two databases live, and how does the throwaway one stay throwaway?

**Decision**: both are databases inside the compose Postgres brought up on
`RELAY_POSTGRES_PORT=15432`, named distinctly from the lane's, and both are dropped at the end of
the chapter's work. The counterfactual database is a copy, so the two measurements run against
identical data rather than two seeded corpora that differ by chance.

**Rationale**: `docs/11-scalability-measurement-2026-09-06.md` is the precedent for measurement
outside the vitest lane — real processes against the compose stack. Keeping the corpus off the
lane keeps it out of every whole-table assertion, which is the class `check-lane-scope.py` exists
to find.

**The constraint that shapes the method**: the counterfactual adds a column and an index in order
to discard them. **It must never become a migration.** A migration file enters
`schema_migrations` and the numbering, and `gaps.md` 045-69 is what that costs — seven
byte-identical migrations under different numbers and a lane that failed in 0.6 s, three times.
So the column and index are applied as statements against the copy, and the chapter publishes the
numbers and the `EXPLAIN`, never a schema change it reverts.

**Alternatives considered**: `CREATE DATABASE … TEMPLATE …` — usable, and it requires no
connections to the template at copy time, which is a sequencing constraint on the measurement
rather than a reason to reject it. Re-running the seeder for the second database — rejected: two
corpora that differ make the four numbers incomparable.

---

## R8 — The chain was executed, and six of its seven links worked first time

R1–R7 were answered by reading. **This one was answered by bringing the stack up and running the
thing end to end**, because five of the questions above had produced specifications nobody had
executed. Postgres on `RELAY_POSTGRES_PORT=15432`, a scratch database, and one message:

    CREATE DATABASE                    ok
    migrate.js  DATABASE_URL=…         15 migrations, 23 tables
    createApiKey                       credential returned
    spawn dist/main.js  PORT=0         port read from the child's log line
    GET  /healthz                      200
    POST /v1/channels/…/messages       403  sender_not_permitted
    POST …  as a bot                   201  seq 1

**Decision**: the corpus carries a bot user and names it, alongside a channel and the credential.
An application credential may send only as a bot — FR-MSG-13 as narrowed by the bot chapter,
refused at `messages.service.ts:113` — and `repo.createUser` takes no `kind` at all, so
`upsertUser(externalId, { kind: "bot", description })` is the path and the schema's
`users_bot_description_check` makes the description mandatory.

**Rationale for running it at all**: R5 and R6 had each specified a piece of this chain and
neither had been tried. The migration runner, the key mint and the `PORT=0` spawn all worked on
the first attempt. **The only thing that failed was the only thing no document had executed**,
which is this project's own ranking of mechanisms arriving as a result rather than as advice.

**What it settled in passing**: the lane's row counts, measured rather than inherited —
31,685 environments, 46,143 channels, 303,885 messages, 487,481 outbox rows. All four are higher
than the figures carried in CLAUDE.md from 045's close-out, which is what `reset-lane.mjs` not
touching data looks like four days on.

**Alternatives considered**: specifying the sender's kind from the clause rather than from a
refusal. FR-MSG-13 is in the SRS and could have been read — and was not, through four analysis
passes, because nothing pointed at it. A 403 pointed at it in one command.

## What research did not resolve

- **The tag convention.** `part3-chN` and `rework/part3-chN` both exist and resolve to different
  commits — `part3-ch18` is `54b2cd53`, `rework/part3-ch18` is `3732d6cf`. `README.md:8` promises
  one tag per chapter and the SKIP AHEAD boxes name it, so a reader following the published
  address lands on the wrong chapter today. **Part 4's first tag cannot be cut until this is
  decided, and deciding it is not this chapter's work.** The chapter can be written and reviewed
  meanwhile.
- **Whether the measurement will show a cost worth acting on.** It is a measurement. FR-010
  states what the chapter does if it does not.

**Two items left this section when R8 ran them.** The lane's row counts were carried here as
inherited and are now measured; the question of whether a service could be pointed at a corpus
database was a specification and is now a transcript. **A list of open questions that nobody
prunes becomes a list of questions somebody answered**, which is the same defect as a checklist
nobody re-reads.
