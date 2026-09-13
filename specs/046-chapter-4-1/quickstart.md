# Quickstart — reproducing chapter 4.1's four numbers

Everything the chapter publishes is reproducible from here. SC-001 says a reader who runs this
gets the row counts the chapter prints; if they do not, the chapter is wrong, not the reader.

**Budget:** the corpus takes minutes, not seconds. Each measurement run is about two minutes.

**If `docker compose` cannot reach a daemon**, check `docker context ls`. A selected `rootless`
context against a root-socket daemon fails here with *"failed to connect to the docker API at
unix:///run/user/1000/docker.sock"*; `DOCKER_HOST=unix:///var/run/docker.sock` settles one
invocation without changing the context.

---

## Before anything

**Nothing else runs on the machine, and nothing touches the repository.** A battery run beside a
few hundred `git show` calls in a sibling worktree cost one run 768 seconds while its per-suite
times stayed identical. Interference and a defect look the same in a single number.

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
pnpm build          # the scripts load services/api/dist — a stale dist measures the wrong tree
```

**Build before believing anything.** The stale-`dist` trap has cost this project a published
conclusion once already (045-77): the harness spawns `dist`, so a `dist` from another tag gives
errors that read like a broken chain.

---

## 1. Confirm the premise before measuring it

FR-014: the chapter's argument rests on two claims about `messages`, and they are re-derived
here rather than carried from `docs/12-part-4-structure.md`.

```bash
sed -n '/export const messages = pgTable/,/^);/p' services/api/src/db/schema.ts
```

**Expected:** no `environment_id` column; no index naming `created_at`; the indexes present are
`(channel_id, sequence)` and the partial `(channel_id, idempotency_key)`.

**If either claim is false, stop.** The chapter's argument changes, and that is the finding.

---

## 2. Build the corpus

```bash
RELAY_POSTGRES_PORT=15432 node scripts/scale/corpus.mjs | tee corpus.json
```

**It creates the database, migrates it, and mints a key.** The migration is the repository's own
runner — `services/api/dist/db/migrate.js` with `DATABASE_URL` pointed at the new database — which
is why §Before's `pnpm build` is a prerequisite and not a courtesy. Nothing here hand-writes DDL:
the corpus carries the schema the platform ships.

**Expected:** a JSON block reporting the database name, the subject environment, **the credential
the send loop authenticates with**, a **`send_target`** naming the bot it sends as and the channel
it sends to, a **`subject`** block holding what the analytical query will actually scan, and a
`created` block counting every row in the database — see [contracts/seeder.md](./contracts/seeder.md). Every
number below is quoted beside this block.

**If `send_target.bot` is missing, §3 will return 403.** An application credential may send only
as a bot; a `kind = 'person'` sender is refused `sender_not_permitted`. This was found by running
the chain, not by reading it.

Run it twice **with the same `CORPUS_DATABASE`** and the second refuses, naming what it found.
That is the contract, not a bug — and passing the name is the only way to reach it, since the
default is date-stamped and an unparameterised second run just builds another corpus.

---

## 3. M1 and M2 — the analytical question, and the neighbour

```bash
node scripts/scale/measure.mjs --db "$(jq -r .database corpus.json)" --phase baseline
```

**It spawns the api itself.** The corpus lives in a database no running service is pointed at, so
`measure.mjs` starts `services/api/dist/main.js` with `PORT=0` and a `DATABASE_URL` naming the
corpus database, and reads the bound port from the child's own log line — the pattern
`scripts/scale/load.mjs:46` already uses. It refuses to start if `dist` is older than `src`,
because the harness spawns `dist` and a stale one measures another tag (045-77).

**Expected output:** four things.

| | |
|---|---|
| **M1** | the query's duration and its `EXPLAIN (ANALYZE, BUFFERS)` plan. The plan should name a scan and a join rather than an index seek — if it names an index, §1's premise is false |
| **M2a** | send-path p95 with no analytical query running |
| **M2b** | send-path p95 with M1 running beside it |
| | both stated against NFR-PRF-02's published 150 ms |

**The send loop runs at ten sends per second and that is the ceiling, not a choice.**
`DEFAULT_LIMITS.send` is 600 per environment per minute and a REST send spends both the `send`
and `rest` budgets. Sixty seconds gives 600 samples, enough for a p95 and not enough to call the
database busy — **this measures latency, not throughput**, and the chapter says so (R6).

### Also run it against the lane, and publish both

```bash
# the lane's busiest environment — an unnamed pick over 31,685 of them means nothing
ENV=$(psql -h 127.0.0.1 -p 15432 -U relay -d relay -tAc "
  select c.environment_id from messages m join channels c on c.id = m.channel_id
  group by 1 order by count(*) desc limit 1")
node scripts/scale/measure.mjs --db relay --environment "$ENV" --query-only
```

**Expected:** a much smaller number, published **with that environment's own message count** —
a duration without its scope is not comparable to anything. FR-009 requires both figures with a
statement of which one would have decided the question wrongly. The precedent is the chapter on what a user
sees: the lane answered 0.87 ms where the real corpus answered 159 ms, and the lane would have
settled that question in favour of doing nothing.

---

## 4. M3 and M4 — the fix that costs more

```bash
node scripts/scale/measure.mjs --db "$(jq -r .database corpus.json)" --phase counterfactual
```

This copies the corpus database, applies the column and the index to the **copy**, respawns the api
against it, and re-runs both measurements. **The respawn is the part that is easy to leave out**:
an api still pointed at the scratch database reports M4 as a latency measured against the schema
the index was supposed to change.

**Expected:** M3 far below M1. M4 above M2a. A storage figure for the column and the index from
`pg_total_relation_size`.

**If M4 is not above M2a, that is the chapter's most interesting result and it gets published.**
The claim being tested is that the index taxes the write path; a measurement that refuses it is
worth more than one that confirms it, and FR-010 says what the chapter falls back to.

**The column and index never become a migration.** No file, no `schema_migrations` row, no
number in the sequence (045-69). They are statements against a copy that is dropped in §5.

---

## 5. Clean up before counting anything

```bash
node scripts/scale/measure.mjs --drop-all
psql -p 15432 -c '\l' | grep relay_corpus || echo "clean"
```

**Expected:** `clean`. SC-005 requires **every** database any step created to be gone — the corpus,
the throwaway copy, and the ones the three-volume run and the falsification each make — plus a
repository carrying no migration, column or index from the experiment. `--drop-all` drops every
`relay_corpus*` database rather than the two this section happens to know about.

**A red probe writes to the lane.** 043 reverted a rule to check the tests could see its absence
and left two `javascript:alert(1)` rows behind; the next measurement read them as pre-existing
data contradicting the plan. Clean up before anything is counted.

```bash
git -C . status --short     # expected: scripts/scale/ additions only, no migration
```

---

## 6. Gates

```bash
# relay-platform FIRST — check:errors reads packages/protocol/dist/codes.js
pnpm lint && pnpm typecheck && pnpm test && pnpm build
cd ../relay-tutorial && pnpm check:fences && pnpm check:docs && pnpm check:srs \
  && pnpm check:figures && pnpm check:errors
```

**The order is load-bearing, not tidiness.** `check-error-codes.mjs:30` resolves
`../relay-platform/packages/protocol/dist/codes.js`; run before a build it reports on the previous
build's registry. And every `check:*` lives in `relay-tutorial` — `pnpm check:fences` in the wrong
repository exits without running anything, which reads as green.

**`check:fences` opens Part 4 at 109 problems** (APPLY 74, HEAD 35) inherited from Part 3's
close-out. FR-015 requires this chapter's contribution to be reported **separately** from that
backlog — the number to publish is the delta, not the total, and the total is not claimed to be
green.

---

## 7. The one thing no command here checks

SC-007 is a person: one reader who has not read this specification, given the published chapter
and nothing else, answering three questions in their own words — which question Postgres answered
slowly, what the index fixed and what it cost, and what the chapter did not do. The procedure is
`specs/036-chapter-3-18/reader-protocol.md`.

Every check above compares bytes. None of them can say whether the chapter's argument lands, and
fourteen records have now named that gap.
