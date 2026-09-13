# Data model — Chapter 4.1

This chapter adds no table, no column and no migration. What it has instead are three things
that need defining because measurements are worthless without them: the corpus, the record of a
measurement, and the two databases.

---

## 1. The corpus

Rows the seeder creates, in dependency order. Every one is an existing table written through its
existing columns.

| table | how many | shape |
|---|---|---|
| `organisations` | 1 | the seeder's own, named so it is recognisable and droppable |
| `applications` | one per environment | **not one.** `unique (application_id, kind)` is FR-TEN-04 — an application holds at most one `development` and one `production` — so three environments need three applications. The schema said so by refusing the first run with 23505 |
| `environments` | `ENVIRONMENTS` (default 3) | one is the subject of every measurement; the others exist so the tenant predicate has something to exclude |
| `api_keys` | 1, on the subject environment | **the send loop has to authenticate.** The precedent emits one for the same reason — `scripts/scale/seed.mjs:22` mints a key and its output block carries `credential`, because a harness that spawns an api and cannot call it measures nothing |
| `users` | `USERS` (default 5,000) **in the subject environment** | `kind = 'person'`; each neighbour environment gets a tenth |
| `users` — the sender | 1, on the subject environment | **`kind = 'bot'`, with a description.** `repo.createUser` takes no `kind` and cannot make one; `repo.upsertUser(externalId, { kind: "bot", description })` is the path, and the schema's `users_bot_description_check` requires the description |
| `channels` | `CHANNELS` (default 2,000) **in the subject environment** | neighbours get a tenth |
| `members` | `MEMBERSHIPS_PER_USER` (default 2) per user | the FK the send path needs. **Not read by the analytical query**, which joins `messages` to `channels` only — it is a parameter because the bot must belong to the channel it sends to, and it arrived with the opposite reason written beside it |
| `messages` | `MESSAGES` (default 1,000,000) **inside the subject's 90-day window** | the seeder writes `DAYS / 90` times that many — 1,333,334 at the defaults — across the full span, so the date predicate excludes a quarter and the variable still means what the query scans. Neighbours get a tenth of the subject's total |

**Every volume above is what the query SCANS, and getting there took two passes finding the same
defect two lines apart.** The query carries two predicates. When the variables meant database
totals, `WHERE c.environment_id = $1` left it **333,000 rows** of a stated million (pass 7); when
they meant the environment's total, `AND m.created_at >= now() - interval '90 days'` left it
**750,000** (pass 8). They now mean the rows inside both predicates. The neighbours and the extra
thirty days still exist, because a predicate that excludes nothing is not being tested either.

**The volume floor is not arbitrary.** 1,000,000 messages across 2,000 channels is the corpus the
chapter on what a user sees already published a 159 ms figure against, so the chapter's number is
comparable to one this project has published rather than to nothing.

**A corpus of people alone is a corpus nothing can write to.** An application credential may send
only as a bot — FR-MSG-13 as narrowed by the bot chapter, refused at `messages.service.ts:113`
with `sender_not_permitted`:

    403 an application credential may send only as a bot user; name one in `user`

That was found by sending one message rather than by reading, and it is the reason the corpus
carries a bot and names it in its output alongside a channel the bot belongs to.

**The database arrives empty and stays useless until it is migrated.** `corpus.mjs` creates it and
then runs the repository's own migration runner against it — `services/api/dist/db/migrate.js`,
with `DATABASE_URL` naming the corpus database, which `client.ts:18` reads as
`process.env.DATABASE_URL ?? DEFAULT_DATABASE_URL`. **That is a build dependency, not only a
runtime one**: the runner is `dist`, so `pnpm build` comes first.

Nothing here hand-writes DDL. The corpus carries the schema the platform ships, which is what
makes a measurement taken against it a measurement of this platform.

### Constraints the seeder must satisfy, and they shape it

- **`(channel_id, sequence)` is unique** (DR-01). Sequences are allocated per channel, so the
  seeder tracks a counter per channel rather than a global one.
- **`channel_id` and `user_id` are foreign keys.** Channels and users exist before messages.
- **`user_id` is nullable and the seeder leaves some null.** A corpus with no null senders cannot
  exhibit R4's divergence, and a chapter that writes the analytical query without ever seeing it
  would hand movement IV a surprise.
- **`created_at` spreads across `CORPUS_DAYS`, ending at seed time.** A 90-day query over a corpus
  written in one minute measures nothing about a range scan. **The query anchors on `now()` and
  the corpus does not**, so a measurement taken a week after seeding scans 83 days of corpus
  rather than 90 — seed and measure on the same day, and record both dates.

### What the seeder does not do

It does not go through `sendMessage`. That path runs a transaction, an idempotency check, a
quota read and a sequence allocation per message — it is the thing being measured, not the thing
that builds a million rows (R5). No outbox row is written, no event is published, and no quota
counter moves: **the corpus is data, not history**, and the chapter says so where it introduces
it, because a reader who assumes otherwise will expect `usage_periods` to agree with it.

---

## 2. A measurement

Four fields, and any one missing makes the other three uninterpretable. This is the shape every
number the chapter publishes carries.

| field | why it is not optional |
|---|---|
| **duration** | the number being claimed |
| **plan** | `EXPLAIN (ANALYZE, BUFFERS)`. A duration says a query was slow; the plan says why, and distinguishes a scan from a cold cache |
| **corpus** | the row counts of the database it ran against. 045's close-out records them beside its timings for this reason |
| **condition** | what else was running. A battery run beside a few hundred `git show` calls cost one run 768 seconds while its per-suite times stayed identical — interference is separable from a defect only if it was recorded |

**The send loop contaminates the corpus it is measured beside, and the amount is small enough to
state rather than engineer around.** Its messages are written into the same tables M1 counts, and
FR-ANL-05 meters users including bots — `repository.ts:4032`'s `senderIsPerson = sender?.kind !==
"bot"` gates only the enforced ceiling, not the metering. At ten sends per second for sixty
seconds that is 600 rows against 1,000,000, about **0.06%**. The chapter publishes counts, so it
publishes this too.

The four numbers the chapter publishes:

    M1  analytical query, baseline          duration + plan
    M2  send-path p95, with M1 running      and the same loop with it absent
    M3  analytical query, counterfactual    duration + plan, after the column and index
    M4  send-path p95, counterfactual       plus the storage cost of the column and index

**M2 is two numbers, not one.** A p95 beside a running query means nothing without the p95
without it, and the chapter reports the pair and the difference rather than the direction.

---

## 3. The two databases

| | purpose | lifetime |
|---|---|---|
| **scratch** | the corpus; M1 and M2 | created by the seeder, dropped by the phase that created it |
| **counterfactual** | a copy carrying `messages.environment_id` and `(environment_id, created_at)`; M3 and M4 | created from scratch by copy, dropped with it |
| **the short-lived ones** | the three-volume run and the three falsifications | six more, each dropped by the phase that made them. `--drop-all` takes every `relay_corpus*` database rather than an enumerated two |

**The api follows the database.** M2 runs against an api spawned on the scratch database and M4
against one spawned on the copy. An api left pointed at the scratch database would report M4 as a
send latency measured against the schema the index was supposed to change — a number that looks
like a result and is a measurement of the wrong thing.

Both live in the compose Postgres on `RELAY_POSTGRES_PORT=15432`, named distinctly from the
lane's database. **Neither is ever the lane.** A million-row corpus inside the lane would break
the whole-table assertions 045-74 spent a feature finding, and `check-lane-scope.py` exists
because that class is hard to see one failure at a time.

**The counterfactual is a copy rather than a second seeded corpus.** Two corpora that differ by
chance make the four numbers incomparable, which would leave the chapter's central claim resting
on a difference nobody can attribute.

### The column and index that must never become a migration

    ALTER TABLE messages ADD COLUMN environment_id uuid;     -- backfilled from channels
    CREATE INDEX ON messages (environment_id, created_at);

Applied as statements against the counterfactual database. **Not a migration file, not in
`schema_migrations`, not in the numbering.** `gaps.md` 045-69 is what a migration identity going
wrong costs: seven byte-identical migrations under different numbers and a lane that failed in
0.6 s, three times. And the chapter's own subject is that this column should not exist, so
shipping it would contradict the thing it argues.

---

## 4. What FR-014 forbids inheriting

The chapter's argument rests on two claims about `messages`: nothing indexes `created_at`, and
nothing reaches a tenant without a join. Both were true at commit `52766091`. **Neither may be
copied from this feature's documents into the chapter.** They are re-derived at the chapter's own
tag from:

    sed -n '/export const messages = pgTable/,/^);/p' services/api/src/db/schema.ts

A hand-carried count is the failure the nine api ports and 045-49 both record — a number correct
for exactly one commit, sitting in prose where nothing checks it. If the derivation disagrees
with this document, **the derivation is right and the chapter's argument changes**, which is a
finding rather than an inconvenience.
