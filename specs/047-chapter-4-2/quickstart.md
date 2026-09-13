# Quickstart — reproducing chapter 4.2's comparison

Everything the chapter publishes is reproducible from here. The predecessor's numbers are
quoted from `specs/046-chapter-4-1/baseline.txt` with the corpus and machine they were taken
on; **this guide does not re-run 4.1's Postgres measurement**, and says so where it quotes it.

**Budget:** the corpus takes about 83 s to build and the load is one statement. Each query is
sub-second.

---

## Before anything

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
pnpm build          # the corpus builder migrates through services/api/dist
```

**If `docker compose` cannot reach a daemon**, check `docker context ls`. A selected `rootless`
context against a root-socket daemon needs `DOCKER_HOST=unix:///var/run/docker.sock`.

---

## 1. Confirm ClickHouse is reachable — it was not before this chapter

```bash
curl -s "http://localhost:${RELAY_CLICKHOUSE_HTTP_PORT:-8123}/ping"
curl -s "http://localhost:${RELAY_CLICKHOUSE_HTTP_PORT:-8123}/?query=SELECT+version()"
```

**Expected after this chapter's compose amendment:** `Ok.` and a version string.

**Expected before it:** `Ok.` and

```
Code: 194. Authentication failed: password is incorrect, or there is no user with
such name. (REQUIRED_PASSWORD)
```

The image ships a `default` user restricted to `::1` and `127.0.0.1`, and the old health check
ran `/ping`, which neither authenticates nor is network-restricted. **The check was green and
nothing outside the container could query the store**, from chapter 1.2 until this one.

---

## 2. Apply the schema

```bash
node analytics/apply.mjs
```

**Expected:** the database, the ledger, then the three files named as applied — the first two
are the script's bootstrap and are not files in the directory. Run it again and **expect it to say it applied
nothing** — see [contracts/schema.md](./contracts/schema.md). A run that is silent about having
done nothing is the zero that means two things.

---

## 3. Build the corpus and load it

```bash
node scripts/scale/corpus.mjs | tee corpus.json
node scripts/scale/load-analytics.mjs --corpus corpus.json
```

**The load reads Postgres from inside ClickHouse.** No client, no export:
`postgresql('postgres:5432', …)` was checked before it was planned and returned the lane's
exact message count.

**Expected:** fewer rows in ClickHouse than the corpus reports. **That is the TTL, and it is
not an error.** `CORPUS_DAYS` is 120 and DR-09 retains 90, so about a quarter is dropped **at
insert**, not at merge — 120,000 rows became 90,000 immediately in the probe, with no error and
no report. The loader prints what the table holds rather than what it sent.

---

## 4. Ask 4.1's question of the second store

```bash
node analytics/query.mjs --environment "$(jq -r .subject_environment_id corpus.json)"
```

**Expected:** four things.

| | |
|---|---|
| the duration | published beside 4.1's **585.9 ms** |
| the rows scanned | beside 4.1's **1,000,000** |
| `EXPLAIN indexes=1` | the parts and granules line |
| the rollup's answer | the same daily figures **over the same ninety days**, from a few dozen rows instead of a million |

**The parts line is the point, not the duration.** At this size ClickHouse answers a full scan
quickly enough to look ordered. Only

```
Condition: and(ts …, environment_id in ['…','…'])   Parts: 4/12   Granules: 49/147
```

distinguishes a store that skipped two-thirds from one that read everything fast.
`ProfileEvents['SelectedParts']` in `system.query_log` returned **0** for the same query, so the
obvious instrument reports nothing and reports it silently.

---

## 5. Check the rollup against an exact count

```bash
node analytics/query.mjs --environment "$ENV" --compare-exact
```

**Expected at the corpus's shape:** agreement. `uniqExact`, `uniq` and
`uniqMerge(active_users_state)` all returned **5000** for 5,000 distinct users over a million
rows.

**And expect that to stop being true.** Measured on this machine:

```
distinct     uniqExact      uniq       divergence
  60,000        60,000    60,000       exact
  70,000        70,000    70,359       +0.51%
```

**FR-ANL-06's reconciliation bound is 0.1%.** Above roughly 65,000 distinct senders in a
period, the rollup's own error exceeds it — and DR-10 forbids the reconciliation from reading
raw events instead. **The conflict is filed for movement IV**, not resolved here. Record the
threshold; do not tune the query until the numbers agree.

---

## 6. Clean up before counting anything

```bash
node analytics/apply.mjs --drop-all
node scripts/scale/measure.mjs --drop-all
psql -h 127.0.0.1 -p 15432 -U relay -d relay -tAc \
  "select count(*) from pg_database where datname like 'relay_corpus%'"
```

**Expected:** `0`, and the lane's row counts unchanged from
`specs/046-chapter-4-1/baseline.txt` — 31,685 environments, 46,143 channels, 303,885 messages.
**A red probe writes to the lane**, and 043's two leftover rows were read as contradicting data
by the next measurement.

---

## 7. Gates

```bash
# relay-platform FIRST — check:errors reads packages/protocol/dist
pnpm lint && pnpm typecheck && pnpm test && pnpm build
cd ../relay-tutorial && pnpm check:fences && pnpm check:docs && pnpm check:srs \
  && pnpm check:figures && pnpm check:errors
```

**`check:fences` opens where 4.1 closed it — 110, APPLY 74, HEAD 36 — and that is re-measured
rather than carried.** 046 found the inherited 109 already stale by one. This chapter amends
`compose.yaml`, which chapter 1.2 fences as a whole body, so **it does contribute to the chain**
and its delta will not be 0. Report the delta; the total is not claimed green.

---

## What no command here checks

Whether the schema is the one the ingester will want. It is written two chapters before its
only consumer, and [contracts/schema.md](./contracts/schema.md) ends by saying that if movement
II needs a column this does not have, the finding is that the contract was written by one
caller.
