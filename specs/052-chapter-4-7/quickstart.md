# Quickstart — chapter 4.7, "the job that checks the meter"

**Feature**: `specs/052-chapter-4-7/` · **Date**: 2026-09-15

**Constitution VI requires this to run unmodified.** Every block below was executed while this
file was written, except those marked **after phase N**. Chapter 4.6 shipped two commands in
its quickstart that had never been run — a `CORPUS_DAYS` value the script refuses and a
`load-analytics.mjs` call missing a required flag — so each block here was pasted and its
output copied back.

Paths are relative to `relay-platform/` unless stated.

---

## 0. The stack

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d
```

```bash
curl -s localhost:4000/healthz
curl -s -X POST http://localhost:8123/ -u relay:relay --data-binary "SELECT 1"
```

The second is a positive control. 047 read three `curl` outputs as data when all three were
authentication errors.

**Do not start an ingester for §1 and §2.** Nothing drains by default, and that is what makes
the counts below hold still while you read them.

## 1. The question FR-ANL-06 does not answer

The clause compares metered totals against *"counts derived from operational data"*. There are
two such counts, and they disagree.

```bash
PGPASSWORD=relay psql -h 127.0.0.1 -p 15432 -U relay -d relay -At -c \
  "select (select count(*) from messages)||' / '||(select coalesce(sum(messages_sent),0) from usage_periods)"
```

```
9650 / 9624
```

**Both are operational.** 26 apart — **0.2694%**, nearly three times FR-ANL-06's own bound,
before the analytical store is consulted at all.

And the aggregate hides the shape. Per tenant:

```bash
PGPASSWORD=relay psql -h 127.0.0.1 -p 15432 -U relay -d relay -At -c "
with m as (select c.environment_id, count(*) n from messages me join channels c on c.id=me.channel_id group by 1),
     u as (select environment_id, sum(messages_sent) n from usage_periods group by 1),
     j as (select coalesce(m.n,0) msgs, coalesce(u.n,0) cnt from m full outer join u using (environment_id))
select 'aggregate '||round(100.0*(sum(msgs)-sum(cnt))/sum(msgs),4)||'%'
    || ' | worst tenant '||round(max(case when msgs>0 then 100.0*(msgs-cnt)/msgs else 0 end),4)||'%'
    || ' | tenants over 0.1%: '||count(*) filter (where msgs>0 and 100.0*(msgs-cnt)/msgs > 0.1) from j"
```

```
aggregate 0.2694% | worst tenant 100.0000% | tenants over 0.1%: 19
```

**A reconciler that aggregates before its verdict reports 0.2694% while 19 tenants breach and
one is wrong by everything it has.** That is why the job compares one tenant at a time.

## 2. The other side, and how much of it there is

```bash
curl -s -X POST http://localhost:8123/ -u relay:relay --data-binary \
  "SELECT uniqExact(environment_id) FROM relay_analytics.daily_usage_billing FORMAT TSV"
PGPASSWORD=relay psql -h 127.0.0.1 -p 15432 -U relay -d relay -At -c \
  "select count(distinct environment_id) from usage_periods"
```

```
4
675
```

Four against 675 — and **the four are not tenants.** Attribute them before believing the
number:

```bash
curl -s -X POST http://localhost:8123/ -u relay:relay --data-binary \
  "SELECT DISTINCT environment_id FROM relay_analytics.daily_usage_billing FORMAT TSV" |
while read e; do
  echo -n "$e -> "
  PGPASSWORD=relay psql -h 127.0.0.1 -p 15432 -U relay -d relay -At -c \
    "select coalesce((select a.name from environments e join applications a on a.id=e.application_id
                       where e.id='$e'),'NOT IN POSTGRES')"
done
```

All four come back `NOT IN POSTGRES` — executed, not assumed: they are `metering.itest.ts`'s
and `ingest.itest.ts`'s fixtures. **So every one of the 675 operational tenants is one-sided, not 671.** Chapter 4.6
measured the reason: `message_events` has no producer, so three of FR-ANL-05's four quantities
have nothing on the analytical side to compare.

**Run that join before believing any count in this chapter.** Three numbers in this feature
were about the lane rather than the platform, and this one query settled all three.

That is why `not-comparable` and `no-data` are separate verdicts from `breach`. Collapsing
them would let the platform's largest defect read as an absence of data.

## 3. What each quantity can be compared against

```bash
PGPASSWORD=relay psql -h 127.0.0.1 -p 15432 -U relay -d relay -At -c \
  "select string_agg(column_name,', ' order by ordinal_position)
     from information_schema.columns where table_name='usage_periods'"
```

```
environment_id, period, messages_sent, created_at, connection_minutes
```

Messages and connection-minutes have an operational counterpart here; unique active users has
`usage_active_users`; **the stored message count has none**, permanently. See
`data-model.md` for the mapping and `contracts/reconcile.md` for what the job may not touch.

## 4. Pick a closed period

```bash
PGPASSWORD=relay psql -h 127.0.0.1 -p 15432 -U relay -d relay -At -c \
  "select to_char(date_trunc('month', now() - interval '1 month'),'YYYY-MM-DD')"
```

```
2026-08-01
```

**Never reconcile the current month.** Its rollup is still being written and its counter still
being incremented, so the comparison measures the clock. `periodOf` in
`services/api/src/quotas/period.ts` is the one definition of what a period is, and the job
takes one explicitly rather than reading a clock of its own.

## 5. After phase 4 — the job

```bash
node scripts/reconcile-usage.mjs --environment <uuid> --period 2026-08-01
```

Four rows, one per quantity, each with both totals, the named operational source, the
percentage and a verdict. Non-zero exit on any breach — which is the whole of what "raises an
alert" can mean on a platform with no alerting integration. `contracts/reconcile.md` says what
a real one would cost.

## 6. The eleven gates

```bash
cd relay-tutorial
pnpm check:fences && pnpm check:docs && pnpm check:srs && pnpm check:figures
pnpm build          # 90 s; the gate that caught 4.4 and 4.6
pnpm check:errors   # reads the BUILT dist — build first
```

```bash
cd relay-platform
pnpm build && pnpm lint && pnpm typecheck && pnpm test
pnpm test:integration
pnpm coverage
```

**`pnpm test:integration` reports one failure where three lanes fail** (`gaps.md` 051-3): its
log holds one `FAIL` line against `Tasks: 6 successful, 9 total`, and the api lane prints no
test output at all. **Take the opening by running the suites directly**, or an inherited red
will be invisible and a new one will be blamed on the wrong chapter.

Known inherited at 4.6's close: `request-log.itest.ts` 5 of 5 (needs an ingester, 050-8),
`limits.itest.ts` (`RELAY_INTERNAL_CREDENTIAL` unset), and `reset-lane.itest.ts` under load
(passes 3 of 3 alone).

## 7. The fence chain

```bash
cd relay-tutorial && pnpm check:fences
```

Report the close as a delta against an opening measured in this feature, **by kind and
locale**, and **split the two HEAD classes** — 11 of the inherited 36 are
`<title> does not exist`, fences titled with a prose phrase that can never be repaired by
editing the platform (050-4). The other 25 are real divergences.

**A titled fence is a whole-body claim.** Chapter 4.6 published two partial quotes with a
`title=` and the chain went 110 → 113. Quote partially only without a title.
