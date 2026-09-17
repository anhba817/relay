# Quickstart — feature 054, chapter 4.9

Nine steps. Every one has been run as written at least once, and step 2 exists because chapter
4.8's step 2 caught its step 1 the first time anybody tried it.

**The lane's PostgreSQL is on 15432**, not 5432 — this machine's own PostgreSQL holds 5432 and
a bare `compose up` publishes a database the next command cannot reach.

---

## 1. Bring the stores up

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
```

`--wait` and not a bare `up -d`. Chapter 4.8 measured the difference: `docker compose up -d`
returns before ClickHouse will answer, and the positive control below is what said so.

## 2. Ask both stores a question with a known answer

```bash
curl -s "http://relay:relay@localhost:8123/?query=SELECT%201"          # -> 1
PGPASSWORD=relay psql -h localhost -p 15432 -U relay -d relay -tAc "select 1"   # -> 1
```

**Do not skip this.** `curl: (52) Empty reply from server` means the container is up and the
server is not, and every number after this step would be about that instead.

## 3. Apply both schemas

```bash
DATABASE_URL=postgres://relay:relay@localhost:15432/relay node services/api/dist/db/migrate.js
node analytics/apply.mjs
```

`pnpm build` first if `dist/` is stale — the migration runs from build output, and chapter 4.5
recorded a runtime form of the stale-`dist` trap that cost a wrong published conclusion.

## 4. See the gate as it is, before changing it

```bash
RELAY_POSTGRES_PORT=15432 pnpm test:integration
```

Expected today: `Tasks: 8 successful, 10 total` for a run that planned 18, with six failures in
the api lane and **none of them the reconciler's**. Record the six by name; they are the opening
measurement FR-004 is closed against.

## 5. See the reconciler's two sides as they are

```bash
curl -s --data-binary "SELECT count(), uniqExact(environment_id) FROM relay_analytics.daily_usage_billing FORMAT TSV" \
  "http://relay:relay@localhost:8123/"
PGPASSWORD=relay psql -h localhost -p 15432 -U relay -d relay -tAc \
  "select count(*), max(messages_sent) from usage_periods"
```

Expected today: **7 rows over 4 environment ids** analytically, and **2,317 rows with a maximum
of 1,017 messages** operationally, with no environment in both. At 1,017 the smallest
expressible drift is 0.197% — twice the bound.

## 6. Build a corpus with both sides

```bash
CORPUS_MESSAGES=350000 CORPUS_ENVIRONMENTS=2 CORPUS_DAYS=91 \
  RELAY_POSTGRES_PORT=15432 node scripts/scale/corpus.mjs
```

**Both of those numbers are floors the script enforces, and an earlier draft of this guide
violated two of the three.** `corpus.mjs:88` refuses `CORPUS_DAYS` at or below **90** — the
query window it exists to fill — and `corpus.mjs:82` refuses `CORPUS_ENVIRONMENTS` below **2**.
The draft said `CORPUS_ENVIRONMENTS=1 CORPUS_DAYS=31` and would have failed on its first line,
which is chapter 4.6's recorded defect reproduced: *"analysis pass 5 wrote 60 into the
quickstart and nobody ran it."*

**`CORPUS_MESSAGES` IS NOT A TOTAL, AND THE TWO ENVIRONMENTS ARE NOT EQUAL.** `planFor` reads
it as `messages_in_window` **for the subject environment** — the first one, the one every Part 2
suite's `createEnvironment` produces. The subject's total is `ceil(messages × days / 90)` and
each neighbour gets `NEIGHBOUR_SHARE = 0.1` of that, so the second environment exists to give
the tenant predicate something to exclude rather than to hold half the corpus.

The rule that falls out is short: **`CORPUS_MESSAGES` is the ninety-day window, so a month is a
third of it.** 350,000 gives the subject ≈**116,700 messages a month**, comfortably past the
100,000 the bound needs, and writes about 389,000 rows in total.

**Measure the subject, and take the number from the report rather than from that rule.** The
in-window/out-window split is exact by construction; the split across channels is floor division
with a remainder. The harness prints the volume per period and that printed number is what the
measurement uses (FR-014).

The build is not the slow part: 1.6M messages took **92.4 s** at chapter 4.2.

It prints the database name and, after this feature, the counter rows it wrote, the periods
covered, and the smallest drift expressible at the largest period's volume.

## 7. Load the analytical side, and check it arrived

```bash
node scripts/scale/load-analytics.mjs --corpus corpus.json
curl -s --data-binary "SELECT count(), uniqExact(environment_id) FROM relay_analytics.daily_usage_billing FORMAT TSV" \
  "http://relay:relay@localhost:8123/"
```

**Step 3 already created the materialised views, so they fire on this insert and there is no
backfill to run.** That ordering is the whole reason step 3 comes before step 7: a view is a
trigger on future inserts, not a query over history (chapter 4.6). Load first and the rollup
stays empty, and the reconciler then answers `no-data` — which reads like an absence of evidence
rather than the missing step it is.

**And do not reach for `analytics/0013_backfill_billing.sql` when something looks wrong.** An
earlier draft of this guide told you to `curl` it after the load, and that is unsafe twice over:
`daily_usage_billing` is a **`SummingMergeTree`**, so a second run adds rows that *sum* with the
first and doubles every count; and `apply.mjs`'s ledger has already recorded `0013`, so
re-running the applier does nothing and the obvious fix is silently a no-op. The backfill exists
for data that was in the store before the views were created, which is not this case.

**The second command is a positive control, not decoration.** A zero here means the load did not
reach the rollup, and every number after this step would be about that instead.

**And check the window.** `message_events` carries a 90-day TTL that removes rows **at INSERT**,
so a 91-day corpus loses its oldest day before anything queries it. The measurement's month must
sit inside 90 days — take it from the report in step 6, not from the calendar.

## 8. Reconcile, and read the verdict

```bash
node scripts/reconcile-usage.mjs \
  --environment <the corpus environment id> \
  --period <YYYY-MM-01, from step 6's report> \
  --database postgres://relay:relay@localhost:15432/<corpus database>
```

**One new argument, not two.** An earlier draft added `--analytics-database` beside it and it
could not have worked: `DB_ANALYTICS` is a constant at `reconcile.ts:110`, not a parameter, and
`apply.mjs` hardcodes the same name at line 18 — so nothing in this repository can build a
second analytical database for a flag to point at. The corpus's analytical rows live in
`relay_analytics` alongside the lane's, and the reconciler separates them by environment id,
which is what it does anyway.

Expected: a verdict of `pass` or `breach` for messages — **not `no-data` and not
`not-comparable`**, which are the two states every tenant in the platform has been in until now.
The exit code is 1 if any quantity breaches.

## 9. Clean up, because this wrote into the lane's own analytical store

```bash
ENVS="'<subject id>','<neighbour id>'"
curl -s --data-binary "ALTER TABLE relay_analytics.message_events DELETE WHERE environment_id IN (${ENVS})" "http://relay:relay@localhost:8123/"
curl -s --data-binary "ALTER TABLE relay_analytics.daily_usage_billing DELETE WHERE environment_id IN (${ENVS})" "http://relay:relay@localhost:8123/"
# poll until the mutations finish, then ASSERT the count, not the queue
curl -s --data-binary "SELECT count() FROM system.mutations WHERE database='relay_analytics' AND is_done = 0 FORMAT TSV" "http://relay:relay@localhost:8123/"
curl -s --data-binary "SELECT count() FROM relay_analytics.message_events WHERE environment_id IN (${ENVS}) FORMAT TSV" "http://relay:relay@localhost:8123/"
```

**`load-analytics.mjs` writes into `relay_analytics` — the lane's own store, not a corpus one**
(`load-analytics.mjs:14`). That is why the materialised views fire at all, and it is why this
step exists: step 7 deposits about 389,000 `message_events` rows and their rollup rows beside
chapter 4.4's request log and chapter 4.6's billing rollups, and **the analytical store has no
lane guard** (`gaps.md` 050-2). Nothing else will remove them.

**The only cleanup this repository ships is `node analytics/apply.mjs --drop-all`, and it is
`DROP DATABASE relay_analytics`** — it takes every other chapter's data with it. Do not reach
for it here.

**Assert the count, do not issue the delete and walk away.** `ALTER TABLE … DELETE` is a queued
mutation: chapter 4.6's suite trusted the bare form and read three creations where it had
planted two, and chapter 4.7 found a row from an earlier run still present. The poll checks the
queue and the count checks the outcome, which is one step further on.

The corpus's **PostgreSQL** side needs no cleanup — `corpus.mjs` builds a disposable
`relay_corpus_<timestamp>` database and never touches `relay`.

---

## What this quickstart does not prove

Both sides of the messages comparison are derived from the same `messages` rows, so they agree
by construction. That makes the figure a measurement of **the reconciler's arithmetic at volume
and the resolution of the bound at that volume**, and not of the platform agreeing with itself.

The platform's own agreement is established by a mechanism rather than by this: `sendMessage`
writes the message and increments the counter in one transaction, and chapter 4.7 checked that
across 1,385 real tenant-periods with **0 disagreements for a non-fixture reason**.

The planted drift is what makes the arithmetic falsifiable, and it is step 9 of the chapter
rather than of this guide.
