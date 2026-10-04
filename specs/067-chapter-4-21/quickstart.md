# Quickstart — chapter 4.21, "Erasure, and every path it must find"

**§0 and §1 are MEASURED. §2 onward are predictions** until phase 9 runs them,
and the last seven chapters' predictions were wrong 3, 4, 3, 5, 2, 0 and 5
times. Run §0 first in the same shell: chapter 4.19's only phase-9 failure was
an operator running a later section without the earlier section's variables.

## 0 · Prerequisites

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
pnpm build
DATABASE_URL=postgres://relay:relay@localhost:15432/relay node services/api/dist/db/migrate.js
RELAY_POSTGRES_PORT=15432 docker compose --profile services build api
RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d --wait
```

**THE IMAGE REBUILD IS NOT OPTIONAL AND IT IS THE STEP THAT GETS SKIPPED.** §2
onward talk to `localhost:4000`, which is the composed **container**, so a route
this chapter adds answers **404** against an image built before it — and the
failure reads as a missing route rather than a stale build. Chapter 4.11 named
this as the third kind of stale build and 4.19 and 4.20 both met it again.

## 1 · MEASURED on 2026-10-04 — where a user is named, and in how many places

```bash
docker compose exec -T postgres psql -U relay -d relay -t -A -F' | ' -c "
select 'users', count(*)::text from users
union all select 'members', count(*)::text from members
union all select 'messages naming a user', count(*)::text from messages where user_id is not null
union all select 'media_objects WITH an uploader', count(*)::text from media_objects where user_id is not null
union all select 'media_objects WITHOUT one', count(*)::text from media_objects where user_id is null
union all select 'usage_active_users', count(*)::text from usage_active_users;"

docker compose exec -T clickhouse clickhouse-client --query "
SELECT 'api_requests' t, toString(count()) c FROM relay_analytics.api_requests
UNION ALL SELECT 'connection_events', toString(count()) FROM relay_analytics.connection_events
UNION ALL SELECT 'message_events', toString(count()) FROM relay_analytics.message_events
UNION ALL SELECT 'daily_usage_billing', toString(count()) FROM relay_analytics.daily_usage_billing
UNION ALL SELECT 'distinct users the sketches claim',
  toString((SELECT uniqMerge(active_users_state) FROM relay_analytics.daily_usage_billing))
FORMAT TSV"
```

**Measured**: 192,641 · 172,965 · 205,628 · 3,979 · **11,050** · 22,150, and
205,697 · 1,081 · **0** · 824 · **0**.

**THE DATABASE IS `relay_analytics`, NOT `relay`.** A first attempt queried
`relay` and got nothing back — silently, because an empty result from
`system.columns` looks like *no such column* rather than *no such database*.
Chapter 4.2 spent eight analysis passes measuring the wrong one.

## 2 · MEASURED — two deletion verbs, and only one is visible to the next statement

```bash
docker compose exec -T clickhouse clickhouse-client --query "
CREATE TABLE relay_analytics.erase_probe (env UUID, user_external_id String, ts DateTime)
  ENGINE=ReplacingMergeTree ORDER BY (env, ts);
INSERT INTO relay_analytics.erase_probe
  SELECT generateUUIDv4(), concat('u', toString(number % 10)), now() FROM numbers(1000);

DELETE FROM relay_analytics.erase_probe WHERE user_external_id = 'u3';
SELECT 'after lightweight DELETE', count() FROM relay_analytics.erase_probe;

ALTER TABLE relay_analytics.erase_probe DELETE WHERE user_external_id = 'u4';
SELECT 'immediately after ALTER … DELETE', count() FROM relay_analytics.erase_probe;

SELECT 'rows on disk once both settled', sum(rows) FROM system.parts
  WHERE database='relay_analytics' AND table='erase_probe' AND active;
DROP TABLE relay_analytics.erase_probe;"
```

**Measured**: `900`, then `900`, then `800`.

**THE MUTATION RETURNED WITH ITS HUNDRED ROWS STILL COUNTABLE.** That is
`gaps.md` 051's *a mutation is not a delete* — and the lightweight form does not
have that property, which is new. **A receipt states a count, so it must use the
verb whose count it can trust.**

## 3 · Erase a user (after the chapter)

```bash
export K=$(RELAY_POSTGRES_PORT=15432 node scripts/seed-demo-tenant.mjs 2>/dev/null | tail -1)

curl -s -X DELETE "localhost:4000/v1/users/qs-bot/data" \
  -H "authorization: Bearer $K" | python3 -m json.tool
```

**Expected after the chapter**: a receipt with one entry per store. **Check that
`api_requests` reads `nothing_to_erase` and `daily_usage` reads `cannot_erase`
— if both say `erased: 0` the receipt has collapsed the distinction it exists
to carry.**

## 4 · And again, which must be a receipt rather than a 404 (after the chapter)

```bash
curl -s -o /dev/null -w "second erasure: %{http_code}\n" \
  -X DELETE "localhost:4000/v1/users/qs-bot/data" -H "authorization: Bearer $K"
```

**Expected**: `200`, with every store reporting zero. Two 404s would prove
nothing — idempotence is a claim about what the second call DID.

## 5 · And what this still cannot show

- **Whether the sketches would have been a problem.** They claim 0 distinct
  users, because `message_events` has never received a row. The obligation is
  unmeetable in principle and vacuous in practice, and **both halves have to be
  said**: either alone misleads.
- **What erasure costs at scale.** The media half dominates at ~2 ms an object
  (chapter 4.20), and no user on this lane owns many.
- **Whether thirty days is enough.** The erasure is synchronous, so the bound is
  satisfied trivially and never exercised.
