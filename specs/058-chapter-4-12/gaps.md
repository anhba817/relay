# Gaps — feature 058, chapter 4.12, "a link that expires, and who may hold it"

Everything here was measured during this feature. Carried items are **re-measured**, never
copied: four of 043's twenty-three carried items were wrong when re-measured and three had
closed with nobody working on them.

---

## New

### 058-1 · A signed URL outlives the authorisation that produced it

**FR-010, `research.md` R7, and it is a cost rather than a defect.** A caller issued a URL at
minute 0 and removed from the channel at minute 1 holds a working link until **minute 60**. The
store checks a signature; it has never heard of a channel.

**Nothing in this chapter can close it.** Shortening the window trades one exposure for another
— a URL that expires while a page is still rendering is a broken image — and the clause names
the hour. Revocation would mean the api standing in front of the bytes, which is exactly what
ADR-13 was decided against.

**The window, named**: 3,600 seconds, asserted in `delivery.itest.ts` as
`X-Amz-Expires=3600`. Same shape as 4.10's *"a slot issued into an outage is byte-identical to a
good one"*: the api signs arithmetic and never contacts the store, so it cannot know and does
not guess.

### 058-2 · Every delivery spends one `rest` operation

**FR-011, `research.md` R8.** `rate-limit.middleware.ts:79` returns `["rest"]` for every `/v1`
path, so a client rendering a gallery of fifty images asks for fifty URLs and spends fifty of the
tenant's budget.

**Left counted**, for 4.8's reason: an exemption list is a hand-maintained table and this project
deletes those rather than growing them. The batch shape that would spend one was considered and
rejected in `contracts/media-delivery.md` — a batch refusal has to name which ids failed, which
is the existence oracle phase 4 spent itself collapsing into a single 404.

### 058-3 · A malformed uuid in a PATH parameter is a caller-triggered 500 on sixteen routes

**Measured against the composed api, with a control:**

    GET /v1/channels/not-a-uuid/messages       500 internal_error
    GET /v1/channels/not-a-uuid                500 internal_error
    GET /v1/channels/<a random uuid>/messages  404 not_found          ← the control

The value reaches the driver, Postgres answers `invalid input syntax for type uuid`, and
`ProtocolErrorFilter` has no rung for it. The control is what makes this a claim about the SHAPE
of the id rather than about the id being unknown.

    @Param("channelId")  13 routes    messages.controller.ts  8 of the 16, 18 titled fences
    @Param("messageId")   3           channels.controller.ts  7 of the 16,  8 titled fences
    @Param("mediaId")     1  (this    users.controller.ts     1 of the 16,  4 titled fences
                             chapter's, validated)
                         --                                            --
                         16 unvalidated before this chapter and after   30 fences

**It is 4.11's research R3 exactly.** That chapter found the same defect in a request BODY,
measured it and fixed it with `z.uuid()` — while nobody looked at the path.

**Recorded, not repaired**, argued in full in `contracts/media-delivery.md`: thirty hunks across
three published controllers, each anchored against the chain's state at its own chapter, for a
change that teaches nothing this chapter is about. The next chapter to open a controller inherits
a number rather than a suspicion.

### 058-4 · Three tenancy predicates guard this route and no single-mutation probe sees any

Constitution VI's 100%-branch clause names tenant isolation, so each arm was deleted and the
suites re-run (T041, T047):

    mutation                                   delivery.itest.ts   gauntlet.itest.ts

    remove the scope from the REFERENCE LOOKUP  16 of 16 GREEN      60 of 60 GREEN
    remove the scope from the OBJECT READ       16 of 16 GREEN      60 of 60 GREEN
    remove the scope from `channelVisibleTo`    16 of 16 GREEN      5 red, NONE of them
                                                                    the media read attack
    remove ALL THREE                             2 of 16 red         —

**The gauntlet is the suite constitution VI names as gating releases**, and it reports nothing
when either of this chapter's two scopes is deleted. A coverage number reports less than that:
an SQL clause carries no JavaScript branch at all (048's shape, 4.11's finding).

**The reading is not "delete two of them".** 4.6 reached 100/100/100/100 by deleting unreachable
arms and 4.11 deleted an early return that was *"an optimisation wearing a branch's clothes"* —
both were arms whose removal changed nothing. These are arms whose removal changes nothing TODAY
**because of each other**, and `channelsReferencingMedia` is one refactor away from a caller that
does not ask `channelVisibleTo` afterwards. `grep -c 'environmentId, this.environmentId'` in
`repository.ts` returns **44**: scoping every read is the convention, and an exception is what
somebody copies.

**What is open** is the instrument, not the decision. A single-mutation probe reports a redundant
safety predicate exactly as it reports dead code, and the difference is not in the number.

### 058-5 · The chapter's own index does not help the chapter's own query, and the lane cannot say so

**Measured at T005 and T013**, busiest tenant, 1,018 messages:

    shape                                  before the index   after the index

    bare `messages @> …`                   1,042 buffers      6 buffers
    one joined+scoped query (the plan's)      84 buffers     86 buffers — unused
    two queries (what shipped)                 —             20 buffers

The one-query form builds its containment operand from `o.id`, a column on the other side of the
join, and a GIN index cannot be looked up with a value the planner does not have yet.

**The lane cannot fail the shape that does not scale.** 68,112 messages across 11,427
environments is six each; analysis pass 2 measured 13 buffers and pass 3 measured 16, both on a
nine-message environment. The one-query cost is the tenant's message count and the two-query cost
is not.

**Open for the next chapter that indexes something**: nothing in this repository measures a query
against a tenant of realistic size. `scripts/scale/corpus.mjs` builds a corpus for the analytical
store and the operational lane has no equivalent, so every operational index decision from here
is made against six-row tenants.

### 058-6 · The `request-log` suite's ingester reported 51 batches and zero records, and it does not reproduce

    in the full lane        5 of 5 red · "the ingester drained 51 batches, 0 records"
    alone                   5 of 5 green · 1,696 records, 1,634 of them requests
    beside media.itest.ts   11 of 11 green · 6 batches, 12 records

The 1,696 is the backlog the red run left behind. The condition unique to it: both JetStream
streams had been cleared and recreated empty an hour earlier, after the broker refused to recover
them (048-6/049-1's documented condition), and the api logged
`analytics.attempt_publish_failed … NatsError: 503` during the run.

**Filed rather than diagnosed**, because three attempts to reproduce it produced green. What was
checked and came back almost clean: `main.ts:53` reads

    await jsm.consumers.add(ANALYTICS_STREAM, {…})
      .catch(() => undefined); // already there; leave it alone

— a catch written for one cause. Probed: `consumers.add` against an absent stream throws `stream
not found`, which that catch swallows. It costs nothing today, because the next line is
`js.consumers.get(stream, durable)` and that throws the same error unswallowed, so the process
exits 1 loudly. **The comment is narrower than the catch**, and only the loud failure downstream
saves it.

### 058-7 · The JetStream health check names one unrecoverable stream at a time

NATS came up unhealthy after an overnight restart:

    [WRN] Healthcheck failed: "JetStream stream '$G > ANALYTICS' could not be recovered"

Clearing that stream's store and restarting produced:

    {"status":"unavailable","error":"JetStream stream '$G > EVENTS' could not be recovered"}

**This is *a checker reports the first failure per file*, one level out in the lane.** A run of
N corrupt streams costs N restarts and each one looks like the last, so an operator who clears
one and sees the broker still unhealthy reads it as the clear having failed.

**And the bulk form of a permitted operation is not automatically permitted**: a loop clearing
each corrupt stream in turn was refused by this environment's guard ("Interfere With
Workloads"), where the same clear issued one stream at a time was allowed.

---

## Carried, and re-measured

### 057-1 · Nothing counts references to a media object — **NARROWER, NOT CLOSED**

**Re-measured.** `grep -rn media_id` across `services/`, `scripts/` and `analytics/`, filtered
for `count` or `refer`, now finds **two hits and both are this chapter's migration comment**.
There is still no counter.

**What changed**: there is now a query that answers *"which channels reference this object"* and
an index that makes it cheap — `messages_attachments_gin`, 136 kB, `Bitmap Index Scan` at 6
buffers.

**Why it is not closed.** FR-MED-10's sweep needs the **opposite** question — *which objects have
NO reference* — and a containment index does not answer absence. Asking it object by object is
one index probe per object; asking it set-wise is a scan of `messages.attachments` across the
environment. The sweep is movement VI's and the bill it inherits is now measured rather than
guessed.

### 057-2 · A message can attach an object nobody uploaded to — OPEN, and this chapter ships a URL for it

Unchanged in mechanism. **Made concrete by this route**: a delivery URL for an object whose bytes
never arrived is well-formed, signed, and fetches a **404 from the store**. Relay never contacts
the store on this path, so it does not know and — decided in `contracts/media-delivery.md` — does
not guess by putting a `state` in the response. FR-MED-03 and FR-MED-09 are still movement VI's.

### 057-4 · `zod-validation.pipe.ts` has an arm with no producer and no pin — OPEN, unchanged

**Re-measured**: `grep -n zod-validation vitest.coverage.config.mts` is still **0 hits**. The
file carries no pin, so nothing reports the dead `protocolCode` arm either way.

**And this chapter declined to use it**, which is a third data point rather than a change. The
delivery route validates its path parameter with three lines in the controller instead, because
the pipe names its `field` from the zod issue's `path` and a scalar's path is empty — so the
reuse would have answered 400 without saying which parameter was wrong.

### 057-5 · The composed stack and the integration lane cannot both run — OPEN, confirmed again

Every lane measurement in this feature was taken with `api`, `gateway` and `dispatcher` stopped,
and the one measurement that needed them (T016a, the malformed-path-param class) was taken with
them up and the lanes stopped. **The state each figure was taken in is recorded in
`baseline.txt`** rather than left to be inferred, which is all this chapter could add.

### 056-1 · An unused slot holds its bytes forever — OPEN, unchanged

No sweep exists. FR-MED-10's twenty-four hours is movement VI's, and 057-1 above is the shape of
what it will cost.

### 056-2 · The quota counts declarations — OPEN, unchanged

`declared_bytes` is what the caller said. Nothing in this chapter verifies bytes either; the
delivery route reads a row and signs a string.

### 055-3 · `check:errors` has no CI job — OPEN, re-measured

**`grep -c 'check:errors' .github/workflows/ci.yml` returns 0.** The tutorial job's gates, read
off `ci.yml:220-241` rather than off memory:

    lint · build · check:docs · check:srs · check:figures · check:fences

Six, and `check:errors` is not among them. This chapter asserts **34 codes, 34 sections** at the
open and the close by running the script by hand, in both directions — which is the only reason
a discrepancy would have been caught, and the same sentence 4.11 wrote.
