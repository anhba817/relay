# Quickstart — chapter 4.21, "Erasure, and every path it must find"

**EVERY SECTION IS MEASURED.** §0 to §2 were measured before the chapter was
written; §3 and §4 were predictions and **both were wrong**, which makes this
chapter's tally **two** against the last seven's 3, 4, 3, 5, 2, 0 and 5. Both were
wrong for the same reason and it is worth naming: they were written before T010
and T011 were decided, and those two decisions changed what the receipt says and
what a second call answers. **A prediction written before a decision is a
prediction about the draft.**

Run §0 first in the same shell: chapter 4.19's only phase-9 failure was an operator
running a later section without the earlier section's variables.

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

**MEASURED on 2026-10-05** — ten entries, and **the prediction above was wrong
about one of them**:

```
profile              erased              display_name, avatar_url, metadata AND external_id
memberships          erased       0
read_positions       erased       0
media_objects        erased       0      73.6% of objects record no uploader
messages             retained_anonymous
usage_active_users   retained_anonymous
connection_events    erased
api_requests         nothing_to_erase    this table records no user identifier
daily_usage          retained_anonymous  <- the prediction said `cannot_erase`
audit_log            cannot_erase        target_id holds the external id, append-only
```

**`daily_usage` READS `retained_anonymous`, NOT `cannot_erase`, AND THE RECEIPT
GAINED A FIFTH OUTCOME TO SAY SO.** The sketches are keyed on the internal uuid,
and a key into an erased row names nobody (ADR-37) — so there is nothing to
subtract and nothing identifying, which is a different fact from *this store holds
their identity and no operation removes it*. **The store that fits that sentence is
`audit_log`**, which this quickstart did not predict at all.

**The check the prediction was reaching for still holds and is now three-way**: if
`api_requests`, `daily_usage` and `audit_log` all read the same word, the receipt
has collapsed the distinction it exists to carry.

## 4 · And again, which must be a receipt rather than a 404 (after the chapter)

```bash
curl -s -o /dev/null -w "second erasure: %{http_code}\n" \
  -X DELETE "localhost:4000/v1/users/qs-bot/data" -H "authorization: Bearer $K"
```

**MEASURED: `404`, and the prediction was wrong.** Erasure replaces `external_id`
with `erased:<users.id>`, so after the first call no user has the id in the path
and the resolve step genuinely finds nothing. **404 is the honest answer here, not
a missing idempotence.**

The prediction was written against a draft in which `external_id` survived. What it
costs is real and is published rather than engineered around: a support tool
retrying after a timeout cannot tell *already erased* from *never existed*. A hash
of the external id kept on the tombstone would answer that — and `u-4821` and an
email address are both brute-forceable, so a hash is the identity wearing a
disguise. **The operator's proof is the audit entry**, which is the one record this
chapter deliberately could not remove.

## 5 · And what this still cannot show

- **Whether the sketches would have been a problem.** They claim 0 distinct
  users, because `message_events` has never received a row. The obligation is
  unmeetable in principle and vacuous in practice, and **both halves have to be
  said**: either alone misleads.
- **What erasure costs at scale.** The media half dominates at ~2 ms an object
  (chapter 4.20), and no user on this lane owns many.
- **Whether thirty days is enough.** The erasure is synchronous, so the bound is
  satisfied trivially and never exercised.
