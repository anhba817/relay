# Data model — feature 058, chapter 4.12

## 1. What changes

Nothing, except an index.

No table, no column, no state. `media_objects` is exactly what 4.10 created and 4.11 read;
`messages.attachments` is exactly what 4.11 writes. This chapter is the first thing that asks a
question **of** that column rather than storing a value in it, and the index is what that
question costs.

## 2. The index

```sql
-- 0017_media_reference_index.sql
CREATE INDEX messages_attachments_gin
  ON messages USING gin (attachments jsonb_path_ops);
```

**`jsonb_path_ops` and not the default `jsonb_ops`.** The only operator this chapter uses is
containment — `attachments @> '[{"type":"media","media_id":"…"}]'` — which is the one class
`jsonb_path_ops` supports and the reason it is smaller. Built and measured at T007: **136 kB
against an 8,376 kB table, 1.62%**, on 68,112 rows of which 1,329 carry attachments.

**`CREATE INDEX` and not `CONCURRENTLY`, and the choice is not open.** `migrate.ts:46` issues
`BEGIN` around every file in the directory. Asked of the server rather than quoted:

    BEGIN;
    CREATE INDEX CONCURRENTLY … ;
    ERROR:  CREATE INDEX CONCURRENTLY cannot run inside a transaction block

The cost is a lock. Asked of `pg_locks` from inside the building transaction: **`ShareLock` on
`messages`** — reads continue, writes wait. **23.301 ms** on 68,112 rows; a deploy-shaped number
on a table this platform expects to be large. The first version of that probe reported
`ShareLock` *and* `AccessExclusiveLock`, which was the probe measuring its own `DROP INDEX`
teardown — the migration contains no `DROP`, and asking again with a `CREATE` alone gave the
`ShareLock` by itself.

**It is on the whole column, not a partial index on the media arm.** A partial index
(`WHERE attachments @> '[{"type":"media"}]'`) would be smaller still and would make the planner's
choice depend on the predicate matching the index's own — which is the kind of cleverness that
works until somebody writes the query slightly differently and gets a sequential scan with no
error. 1.7% is not worth that.

## 3. The predicate, and it is TWO queries — the third design, decided by measuring

**This section has been wrong twice and the second version was the expensive one.** The first
draft described two steps with no tenant predicate; analysis pass 2 scoped it and collapsed it
into one joined query; pass 3 added a join to `media_objects` for `object_key`. Running it at
T013 showed that the collapse is what makes the new index dead.

**What ships:**

```sql
-- 1. the object, by primary key, scoped. `object_key` is what presign signs, and reading
--    the row is what makes the object's own environment_id a check this route performs.
SELECT object_key
  FROM media_objects
 WHERE id = $1 AND environment_id = $2;

-- 2. which of this environment's channels reference it. The containment operand is a
--    BOUND VALUE, which is the only form the GIN index can serve.
SELECT DISTINCT c.id
  FROM messages m
  JOIN channels c ON c.id = m.channel_id
 WHERE m.attachments @> $3::jsonb
   AND c.environment_id = $2;
```

then `channelVisibleTo` over the channels that come back.

**WHY NOT THE ONE JOINED QUERY, MEASURED RATHER THAN ARGUED.** On the lane's busiest tenant —
1,018 messages across 10 channels — with the GIN index in place:

    one joined query, a hit    Nested Loop · Rows Removed by Join Filter: 1017 ·  86 buffers · 1.109 ms
    two queries, a hit         Index Scan + Bitmap Index Scan on the gin index ·  20 buffers · 0.111 ms

The one-query form builds its containment operand from `o.id`, a column on the other side of the
join. A GIN index cannot be looked up with a value the planner does not have yet, so it narrows
to the tenant's channels and filters every message they hold. **The index is present and idle.**

**AND THE LANE'S TENANTS ARE TOO SMALL TO SHOW IT.** 68,112 messages across 11,427 environments
is six each. Pass 2 measured 13 buffers and pass 3 measured 16, both on a nine-message
environment; the one-query cost is the tenant's message count and the two-query cost is not. A
shape that does not scale is one the lane cannot fail.

**WHAT THE SPLIT DOES NOT GIVE UP.** Both repairs survive it. The scope is on step 2, so this is
still not the one read in `repository.ts` that crosses tenants — `grep -c 'environmentId,
this.environmentId'` returns **44** and this is not the exception. And step 1 still reads
`media_objects`, so the object's `environment_id` is checked here rather than inherited from
4.11's send-time predicate — a rule enforced in another route, in another chapter, at another
moment.

**AND STEP 1 FIRST IS WHAT MAKES THE COMMON REFUSAL CHEAP.** An id no object has dies at the
primary key in 3 buffers; step 2 never runs. `research.md` R3's *"the refusal is the expensive
case"* was true of the bare query and is false of this one.

**`DISTINCT`, AND THE FAN-OUT IS WHY.** One object can be referenced by any number of messages —
FR-MSG-11 has allowed the same id twice since 3.24, and forwarding a photo is how a second
reference happens. Without `DISTINCT` the disjunction is one `channelVisibleTo` per *message*,
each a query and sometimes two (`isMember`); with it, one per distinct *channel*. The lane's
current maximum is **1 reference per object**, so this costs nothing measurable today and the
shape is still wrong — the lane has never forwarded a photo.

`channelVisibleTo(channelId, userId?)` is `repository.ts:5517` and has shipped since the channel
chapter:

```ts
if (!channel) return false;
if (channel.type !== "private" || userId === undefined) return true;
return this.isMember(channelId, userId);
```

**Three behaviours this chapter needs, none of them written here:**

| caller | channel | answer |
|---|---|---|
| a user token | `public` of this environment | visible — **membership is not required** |
| a user token | `private`, member | visible |
| a user token | `private`, non-member | not visible |
| an application credential (`userId` undefined) | any of this environment | visible — the clause's *"or API key"* arm |
| anyone | another environment's | not visible — the helper is scoped to `this.environmentId` |

**THE OBVIOUS IMPLEMENTATION WOULD HAVE BEEN WRONG.** FR-MED-08 says *"channel membership"*, and
a membership check would refuse a user the photo in a message whose text they can read — 11,557
public channels on the lane against 1,016 private, so the common case is a channel where
membership is not the rule. See `research.md` R2.

## 4. Any referencing message, not the referencing message

The clause's singular does not describe the platform. FR-MSG-11 has allowed the same id twice
since 3.24 — *"the same id twice is two attachments"* — and forwarding a photo into a second
channel is the ordinary way one object gets two references.

**Authorisation is a disjunction**: the URL is issued if **any** referencing message sits in a
channel the caller may read. A caller in channel A and not B reads an object referenced from
both; a caller in neither reads nothing.

This is also why the lookup cannot stop at the first row it finds. A query returning one
reference and testing it would refuse a caller whose channel happened to be second, which is a
correctness bug that would look like flakiness.

**AND "EVERY REFERENCE" IS NOT THE SAME AS "EVERY REFERENCING CHANNEL".** §3's `DISTINCT` is
what keeps the disjunction bounded by channels rather than by messages: a photo forwarded into
one channel a hundred times is one authorisation question, not a hundred. The unbounded version
is correct and costs one `channelVisibleTo` per message, which is a query each and two when the
channel is private.

## 5. What a refusal must not distinguish

Three conditions, one answer, the same discipline 4.11 built for attaching:

    another environment's object          → 404 not_found
    referenced only where you cannot read → 404 not_found
    no object has that id                 → 404 not_found

**404 and not 422**, and the precedent is in `channelVisibleTo`'s own comment — the leak it was
written to close was a private channel answering `200, empty page` where an absent one answered
`404`, which announced the channel existed. A read of a thing you may not see answers as a thing
that is not there.

**No new error code.** `not_found` is in the registry, in the reference, and is the filter's 404
rung. `check:errors` should read **34 codes, 34 sections** at the close — unchanged from 4.11,
and asserted rather than assumed, because a chapter that adds a route usually adds vocabulary.

## 6. The response

```json
{ "url": "https://…?X-Amz-Algorithm=…&X-Amz-Expires=3600&X-Amz-Signature=…",
  "expires_at": "2026-09-19T16:04:11.000Z" }
```

**Two fields and no attachment.** This carries no member of the attachment union, which is why
4.11's `data-model.md` §4b stays at ten validators and does not gain an eleventh (`research.md`
R5). Checked rather than assumed — if the design later returns the attachment alongside the URL,
that table changes.

`expires_at` is present for the same reason the upload slot carries one: a client that has to
decide whether to re-request should not have to parse `X-Amz-Date` and add `X-Amz-Expires`.

## 7. State transitions

None. This chapter reads `state` only in as much as it does not: an object is `pending` and a
signed URL for it is well-formed whether or not bytes were ever uploaded. The store answers
**404 to the client**, and Relay never learns — which is ADR-13's design and the reason FR-MED-09's
rejection marker needs movement VI's state machine rather than this route.
