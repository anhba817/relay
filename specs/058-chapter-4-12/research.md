# Research — feature 058, chapter 4.12, "a link that expires, and who may hold it"

Every row here was checked against the tree or the database. Where a figure appears, it is what
came back.

---

## R1 · The flagged assumption is wrong, and the clause's own note is why

**The assumption, as the spec states it**: an object with no referencing message should be
readable by its uploader — the permissive reading — because otherwise a client cannot preview
the file it just uploaded.

**Settled against it.** Two arguments, and the second is decisive.

**The weak one first: the case barely exists.** The only party that could want the bytes of an
unreferenced object is the one that just uploaded them, and it has them. The window between
"upload finished" and "message sent" is the client's own, and the client is holding the file.

**The decisive one: the permissive reading IS the thing FR-MED-08's note forbids.** The note
under the SRS table reads *"media access control inherits channel membership rather than
inventing a parallel ACL system."* Granting the uploader access to an object with no message is
a second way to be authorised — one that does not follow a message — which is a parallel rule
however small it is. The clause has exactly one authorisation source and this would add another.

**And the object is scheduled for deletion anyway.** FR-MED-10: *"unreferenced media objects
shall be hard-deleted by a scheduled job after 24 hours."* An unreferenced object is one the
platform has already decided to destroy; building a read path to it means building access to a
thing whose own requirement calls it garbage.

**Decision**: an object with no referencing message is readable by **nobody**, including its
uploader and including an application credential. The refusal is the same one FR-005 requires
for every other case, so it costs no new vocabulary.

**What is given up, said rather than hidden**: a support tool that wants to look at a tenant's
orphaned uploads cannot. That is the dashboard's chapter, it would be a deliberate
administrative surface, and inventing it here as a side effect of a delivery route is how a
parallel ACL gets built by accident.

---

## R2 · "Channel membership" is not what this platform means by *authorised to read*

FR-MED-08 says *"callers authorised to read the referencing message (channel membership or API
key)"*, and the obvious implementation is a membership check. **That would make media less
readable than the message carrying it.**

`repository.ts:5589` — history's own authorisation, which has shipped since the channel chapter:

```ts
if (channel?.type === "private" && !(await this.isMember(channelId, userId))) {
  return [];
}
```

**Membership is checked for `private` channels only.** A public channel's messages are readable
by any user of the environment. On the lane: **11,289 public channels against 995 private** —
so the common case is a channel where membership is not the rule at all.

A delivery route demanding membership would refuse a user who can read the message, its text and
the fact that it has an attachment, but not the attachment. That contradicts the clause's own
principle more precisely than it implements its words.

**And the predicate already exists**, written by the chapter that found this exact leak:

```ts
async channelVisibleTo(channelId: string, userId?: string): Promise<boolean>
```

Its comment: *"`userId` absent means the tenant is reading, which sees everything it owns"* —
which is the clause's *"or API key"* arm, already built. So the authorisation rule for this
chapter is **not a new one**: it is `channelVisibleTo`, asked of whichever channel carries the
reference.

**Decision**: authorisation is `channelVisibleTo`, and the chapter says out loud that it reused
the predicate rather than writing one. The "no parallel ACL" note is satisfied by construction
rather than by discipline.

---

## R3 · The lookup is a sequential scan, and this is the opposite of 4.1's answer

Measured on the lane before the specification was written — **66,516 messages, 1,580 with
attachments**, `EXPLAIN (ANALYZE, BUFFERS)`:

    the lookup                          time      buffers   rows filtered
    a hit, sequential scan            2.132 ms       806        53,074
    a MISS, sequential scan           2.886 ms     1,016        66,516
    a hit, GIN jsonb_path_ops         0.082 ms         6             —
    a miss, GIN jsonb_path_ops        0.018 ms         5             —

    index size 136 kB · table 8,128 kB · 1.7%

**The refusal is the expensive case.** An id nobody references has to be searched for through the
whole table before the platform can say no — so the cheapest request to make is the one that
costs the most to answer, which is the shape an attacker probes with.

**CHAPTER 4.1 CONCLUDED THE OPPOSITE ABOUT AN INDEX AND BOTH ARE RIGHT.** There: *"the index
that should fix the query buys a gap inside the run-to-run spread for +49% storage … you cannot
index your way out of an analytical question when the cost is the aggregation."* Here the cost
is a lookup by value, 26× to 160× for 1.7%. The chapter publishes them side by side, because the
transferable lesson is **which kind of cost you are looking at** and not whether indexes help.

**`jsonb_path_ops` and not the default `jsonb_ops`**, measured rather than assumed: the query is
`attachments @> '[{"type":"media","media_id":"…"}]'`, containment only, which is the one operator
class `jsonb_path_ops` supports and the reason it is smaller.

**AND THE FIGURES SURVIVE A BOUND PARAMETER, WHICH IS WHAT THE DRIVER SENDS.** Everything above
was measured with a literal, and a literal is not what the code will issue — the classic way a
planning number stops describing the shipped query. Checked at analysis pass 2:

    PREPARE p(jsonb) AS SELECT id FROM messages WHERE attachments @> $1 LIMIT 1;
    EXECUTE p('[{"type":"media","media_id":"…"}]'::jsonb);

    Bitmap Index Scan on the gin index · 6 buffers

Identical to the literal.

---

### R3a · AND THE HEADLINE WAS STILL A MEASUREMENT OF A QUERY THIS CHAPTER DOES NOT SEND

**Amended at T005/T013, by running it.** Everything above is the BARE query —
`SELECT id FROM messages WHERE attachments @> …` — and by the time the analysis passes had
finished with it, the route's query was not that. Pass 2 added an environment scope; pass 3
added a join to `media_objects` for `object_key`. Re-measured on the lane's **busiest tenant**,
1,018 messages across 10 channels, `EXPLAIN (ANALYZE, BUFFERS)` with bound parameters:

    shape                                    plan                              buffers    time

    --- no index at all ---
    bare `messages @> …`, a hit              Seq Scan, 68,111 removed            1,042   2.47 ms
    bare, a miss                             Seq Scan, 68,112 removed            1,042   2.32 ms
    one joined+scoped query, a hit           Nested Loop, join filter over          84   0.99 ms
                                             the tenant's 1,018 rows
    one joined+scoped query, a miss          same plan, 1,018 removed               84   0.94 ms

    --- with the GIN index ---
    bare, a hit                              Bitmap Index Scan                       6   0.028 ms
    bare, a miss                             Bitmap Index Scan                       6   0.023 ms
    one joined+scoped query, a hit           UNCHANGED — the index is not used      86   1.109 ms
    two queries: the object row              Index Scan on media_objects             3   0.034 ms
                 the reference lookup        Bitmap Index Scan on the gin index     17   0.077 ms
                 the reference lookup, miss  Bitmap Index Scan, channels             6   0.046 ms
                                             `never executed`

**THE SCOPE ALONE IS 12.4× AND NEEDS NO INDEX.** Adding `c.environment_id = $env` turns a
68,112-row sequential scan into a nested loop over one tenant's rows: 1,042 buffers to 84.

**AND THE ONE-QUERY SHAPE MAKES THE INDEX UNUSABLE.** The containment operand is built from
`o.id`, a value from the other side of the join, so the planner cannot look it up — it narrows
to the tenant's channels and applies containment as a join filter over every message they hold.
`Rows Removed by Join Filter: 1017`, with the index present and idle. Splitting the question in
two makes the operand a bound value, which is the only form a GIN index can serve: **20 buffers
against 86, 0.111 ms against 1.109.**

**THE SMALL TENANT HID IT, AND THAT IS WHY BOTH ANALYSIS PASSES READ CLEAN.** Pass 2 measured
13 buffers and pass 3 measured 16, both on a nine-message environment. The one-query plan's cost
is the TENANT's message count; the two-query plan's is not. The lane holds 68,112 messages across
11,427 environments — six messages each — so the shape that does not scale is the shape the lane
cannot fail.

**AND "THE REFUSAL IS THE EXPENSIVE CASE" IS FALSE FOR THE SHIPPED QUERY.** That sentence is true
of the bare query, where an id nobody references is searched for through the whole table. Of the
two refusals the route can give, the commoner — no object has that id — is the **cheapest thing
it does**: 3 buffers, everything after the primary key `never executed`. Only the refusal where
the object exists and nothing references it costs what a grant costs.

**What survives of the comparison with 4.1.** That chapter's index bought *"a gap inside the
run-to-run spread for +49% storage"*; this one buys 4.3× fewer buffers for **1.62%** — 136 kB
against 8,376 kB. Still the opposite answer, still for the reason R3 gave. What changed is that
the multiplier is 4.3× rather than 26–160×, and that **the query has to be written so the planner
can use the index** before any of it is true.

---

## R4 · The chapter adds no error code, and 404 is the answer

4.11 added `media_not_attachable` (422) because a well-formed id the caller may not use is a
request the platform understood and could not carry out. **A read is a different question and
this platform already has its answer.**

`channelVisibleTo`'s own comment records the precedent, from the leak it was written to close:

    a channel that does not exist   → 404
    a private channel, non-member   → 200, empty page   ← the leak

The fix there was to make both answer identically. The same applies here: an object of another
tenant, an object referenced only where the caller cannot read, and an id no object has are
**one answer — 404 `not_found`** — and the code already exists, is already in the reference, and
is already the filter's 404 rung.

**Decision**: no new code. `pnpm check:errors` should read **34 codes, 34 sections** at the close,
unchanged from 4.11 — and that number being unchanged is itself worth asserting, because a
chapter that adds a route usually adds vocabulary.

---

## R5 · No new validator, checked rather than assumed

4.11's `data-model.md` §4b enumerated **ten** validators of the attachment union and was wrong
at seven until analysis pass 6 asked what `messageSchema` was embedded in.

This chapter's response body is `{ url, expires_at }`. It carries no attachment, no message and
no union member, so it adds nothing to that table. **The request carries a `media_id` in the
path**, which is a `z.uuid()` in a param schema and not a member of the union either.

**Checked, not assumed**: the route returns a URL and an instant. If the design changes to
return the attachment alongside it, this row changes and §4b gains an eleventh entry.

---

## R6 · The signer already does this, and 4.10 already proved the precondition

`presign.ts:33` has taken `"GET" | "PUT" | "HEAD" | "DELETE"` since 4.10, and `expiresIn` is
seconds. One hour is `expiresIn: 3600` against the upload slot's `900`.

`presign.itest.ts:53` is titled *"refuses an unsigned GET of that object — FR-MED-08's
precondition"*. **Half this chapter's clause was built and proven two chapters ago**, from
outside the container: signed GET 200, unsigned GET 403, tampered 403. The chapter cites that
test rather than writing another, and says which half it did not build.

**Dependency count: unchanged.** No S3 client, no URL library. ADR-30's argument is not reopened
because nothing asks it a new question.

---

## R7 · The URL outlives the authorisation, and nothing can fix that here

A caller issued a URL at minute 0 and removed from the channel at minute 1 holds a working link
until minute 60. The store checks a signature; it has never heard of a channel.

This is not a defect this chapter can close. Shortening the hour trades one exposure for
another — a URL that expires while a page is still rendering is a broken image — and the clause
names the hour. Revocation would mean the api standing in front of the bytes, which is exactly
what ADR-13 was decided against.

**Decision**: published as a cost with the window named, in the chapter and in `gaps.md`. The
same shape as 4.10's *"a slot issued into an outage is byte-identical to a good one"*.

---

## R8 · Every delivery spends the tenant's REST budget

`rate-limit.middleware.ts:79`:

```ts
export function operationsFor(method: string, path: string): LimitedOperation[] {
  if (!path.startsWith(PUBLIC_PREFIX)) return [];
  if (method === "POST" && SEND_PATH.test(path)) return ["rest", "send"];
  return ["rest"];
}
```

Every `/v1` path costs one `rest` operation. A client rendering a gallery of fifty images asks
for fifty URLs and spends fifty. **Left counted**, for 4.8's reason: an exemption list is a
hand-maintained table, and this project deletes those rather than growing them.

**And it argues for one shape over another.** A route that answers one id per request makes the
budget cost linear in images; a route that takes several would not. That is a design question
for `data-model.md` rather than a research finding, but the budget is the reason it is a question
at all.

---

## R9 · What held

- **`channelVisibleTo` handles the API-key arm already** — `userId === undefined` returns true
  for any channel of the environment. No second path.
- **The migration tail is `0016_storage_quota.sql`**, so this chapter's index is `0017`.
- **`messages` carries no index touching `attachments`** — only `(channel_id, sequence)` and
  `(channel_id, idempotency_key)`, both unique constraints.
- **A deleted message unlinks its attachments** (4.11's FR-024, verified there), so a tombstone
  removes the reference and the object stops being readable by this route. Nothing extra is
  needed for that and the chapter should assert it rather than assume it.
