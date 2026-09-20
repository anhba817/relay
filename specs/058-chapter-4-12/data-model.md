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
`jsonb_path_ops` supports and the reason it is smaller. Measured at **136 kB against an 8,128 kB
table, 1.7%**, on 66,516 rows of which 1,580 carry attachments.

**It is on the whole column, not a partial index on the media arm.** A partial index
(`WHERE attachments @> '[{"type":"media"}]'`) would be smaller still and would make the planner's
choice depend on the predicate matching the index's own — which is the kind of cleverness that
works until somebody writes the query slightly differently and gets a sequential scan with no
error. 1.7% is not worth that.

## 3. The predicate, and it is one that already exists

For a `media_id` and a caller, **in one query**:

```sql
SELECT DISTINCT c.id, c.type
  FROM messages m
  JOIN channels c ON c.id = m.channel_id
 WHERE m.attachments @> '[{"type":"media","media_id":<id>}]'::jsonb
   AND c.environment_id = <this environment>
```

then `channelVisibleTo` over the rows that come back.

**AND IT JOINS `media_objects`, BECAUSE THE ROUTE CANNOT SIGN WITHOUT `object_key`** — a need
no artifact named until analysis pass 3. `presign` takes a bucket and a key; the key is
`media_objects.object_key`, which `media.service.ts:92` computes as `` `${environment}/${id}` ``
when the slot is issued. So the full query is:

```sql
SELECT DISTINCT o.object_key, c.id, c.type
  FROM media_objects o
  JOIN messages m
    ON m.attachments @> jsonb_build_array(
         jsonb_build_object('type', 'media', 'media_id', o.id::text))
  JOIN channels c ON c.id = m.channel_id
 WHERE o.id = <media_id>
   AND o.environment_id = <this environment>
   AND c.environment_id = <this environment>
```

    Index Scan using media_objects_pkey · 16 buffers · no sequential scan

**READ THE ROW RATHER THAN RECONSTRUCT THE KEY, AND THE DIFFERENCE IS WHOSE INVARIANT YOU ARE
STANDING ON.** The key is deterministic, so `` `${caller_env}/${media_id}` `` would sign
correctly without touching `media_objects` at all — one fewer join. It would also mean the
object's own `environment_id` is **never checked by this chapter**: the tenancy would rest
entirely on 4.11's send-time predicate refusing to store a foreign `media_id` in the first
place. That predicate holds, and no stored attachment predates it, so reconstruction is safe
today. It is safe because of a rule enforced in a different route, in a different chapter, at a
different moment — and the join costs one primary-key lookup to stop depending on it.

**THE TENANT PREDICATE IS NOT DECORATION, AND THE FIRST DRAFT OF THIS SECTION DID NOT HAVE
IT.** It described two steps — find any message containing the id, then ask about its channel —
which is correct, because `channelVisibleTo` is itself scoped and refuses another tenant's
channel. It is also **the only read in this repository that would scan every tenant's rows**:
`grep -c 'environmentId, this.environmentId'` in `repository.ts` returns **44**. A query whose
safety depends on a later call is a query somebody will reuse without the later call.

**`DISTINCT`, AND THE FAN-OUT IS WHY.** One object can be referenced by any number of messages —
FR-MSG-11 has allowed the same id twice since 3.24, and forwarding a photo is how a second
reference happens. Without `DISTINCT` the disjunction is one `channelVisibleTo` per *message*,
each a query and sometimes two (`isMember`); with it, one per distinct *channel*. The lane's
current maximum is **1 reference per object**, so this costs nothing measurable today and the
shape is still wrong — the lane has never forwarded a photo.

    the joined, scoped, de-duplicated query   Bitmap Index Scan · 13 buffers

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
a membership check would refuse a user the photo in a message whose text they can read — 11,289
public channels on the lane against 995 private, so the common case is a channel where
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
