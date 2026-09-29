# Phase 0 research — Chapter 4.16, "Storage on the bill"

Seven questions. Every figure was measured on 2026-09-29 against the running lane: Postgres on
15432, MinIO on 9100, ClickHouse in the composed stack.

---

## R1 — Where the delta comes from

**Question.** FR-001 wants a signed byte change recorded when it becomes true. The platform has
three analytical producers already (webhook attempts, api requests, connection events); a fourth
is a known cost.

**What the ingester actually does.** It consumes `analytics.>` and routes on the **payload's own
`type` discriminator**, not on the subject — `shape.ts` says why: *"the PAYLOAD says what the
payload is … a router that parses subjects has to be right about tokens too."* Three types are
claimed; anything else returns `{ kind: "unclaimed" }` and is **neither acked nor
terminated** — `ingest.ts:100`, after 049's repair: *"Acking would consume a record this
consumer did not write; terminating would destroy it. Left alone it is redelivered until
something claims it or the stream's seven days expire."*

**Decision.** A fourth record type on the stream that exists, published by the api, on
`analytics.media.stored.{environment_id}`. No new service, no new consumer, no new subject
grammar beyond one token.

**Rationale.** The alternative — deriving the delta from records that already flow — does not
work. `api_requests` holds 118,238 rows and knows a slot request happened, but not how many
bytes it reserved; adding the bytes to that record would make a request log carry a billing
fact, and 4.8 already found that log serving a customer-facing read.

**The risk this inherits, and 049 already softened it.** In chapter 4.4 an unrecognised type
was **terminated**, which destroyed every record that chapter sent — *"pass 2: written 0,
malformed 0, terminated, never comes back"*, with stream depth saying the records were there
and consumer lag saying there was nothing to do. **049's repair means that no longer happens**:
the record is redelivered for up to the stream's seven days and the `unclaimed` counter is the
only signal.

**It is still a producer shipping into silence** — nothing reaches ClickHouse, nothing fails,
and only a counter nobody is watching says so. So the order holds: **the consumer learns the
new type before the producer ships**, and the probe asserts the *current* behaviour, because
one written against 4.4's transcript would look for a termination that no longer happens and
fail for the wrong reason.

**Where the bytes start and stop counting is not a choice.** FR-002 requires the metered
quantity to be the quota's, and `reserveMediaSlot` sums `declared_bytes` where
`state <> 'rejected'`. So bytes count from **slot reservation** — a `pending` object is already
charged — and stop at **rejection**. That gives three emission points and one that does not
exist yet:

    slot reserved        + declared_bytes     reserveMediaSlot
    verdict = rejected   − declared_bytes     recordMediaVerdict
    rendition written    + its own bytes      recordMediaVerdict (4.15)
    object deleted       − declared_bytes     NOTHING DOES THIS YET (R4)

---

## R2 — What the reconciliation can list

**Question.** DR-17 requires a weekly comparison against *"an object-storage inventory
listing"*. Nothing in either service can list a bucket: `ListObjects` appears nowhere.

**Measured, and better than expected — through the MEDIA WORKER's signer, which is not the one
this will use.** The reconciliation must read the rollup and the inventory together and the
worker holds no database credential (ADR-04), so the listing belongs in the api, on
`presign.ts`. That signer already takes four methods and already documents the key-less bucket
call; the figures below should carry over and **T032a re-runs them against it rather than
assuming.** The existing signer signs `/{bucket}` when given no key, and that is a bucket
listing:

    GET /{bucket}, signed by sign(store, { method: "GET" })    200, <ListBucketResult>
    keys in one response                                       1000
    IsTruncated                                                true
    a <Size> element per key                                   yes, 1000 of 1000
    response                                                   377 kB in 48 ms
    keys prefixed by an environment uuid, ON PAGE ONE          1000 of 1000 — see below
    distinct tenants on page one                               187

**Three consequences, and two of them save the design a lot of work.**

1. **The inventory needs no HEAD per object.** The listing carries a size per key. Heading the
   lane's 8,120 objects at 4.13's measured 1.412 ms is **11.5 seconds**; nine listing pages at
   48 ms is about **430 ms**, 27× cheaper.
2. **Tenant attribution is nearly free, and the first version of this paragraph said "free"
   from a sample of one page.** Every key an upload or a rendition produces is
   `${environment_id}/${id}` — `media.service.ts:108`'s layout, which chapter 4.15 deliberately
   followed for renditions rather than deriving them from the parent's key. Had it not, this
   listing would be a mix of shapes and the reconciliation would need a join.

   **But the bucket also holds keys no tenant owns.** The listing is lexicographic and page one
   ends at `a596c6f7…`, so nothing sorting later was in the sample. Across the whole bucket
   there are **four** non-tenant-prefixed top-level prefixes — `analyze-probe`, `probe`,
   `r9-measure`, `thumbnail-itest` — two of them written by this feature's own research and one
   left by 4.15's suite.

   **This was T034's warning committed in the research that wrote T034.** One page is not the
   store. The reconciliation therefore needs an explicit arm: a key that does not parse as a
   tenant is reported as its own category — *N keys, M bytes, attributable to no tenant* —
   because **skipping them silently means a bucket full of debris reports clean**, and counting
   them means a verdict for a tenant that does not exist.
3. **Pagination costs a signer change, and is not optional.** `IsTruncated` is true at 1,000
   keys against 8,120 objects. Appending `&list-type=2` outside the signature answers
   **`SignatureDoesNotMatch`**, because every query parameter has to be inside it. The signer
   builds a fixed parameter set and admits no extras.

**Decision.** Extend the signer to accept additional query parameters, and page the listing with
`marker`. **The one-page trap is 4.13's** — that chapter's sweep read one page and an object
nobody uploaded to stayed `pending` for ever — so the reconciliation pages or it is wrong, and
the test asserts more than 1,000 keys were seen.

---

## R3 — Where the daily figure is stored

**Question.** A new rollup, or a column on `daily_usage_billing`? DR-10 was amended after 4.6
measured a rollup whose key made the billing read touch **147,534 rows against 281**.

**Decision.** A new column on `daily_usage_billing`, fed by a **third** materialised view.

**Rationale, and the precedent already exists.** Two views write into that table today —
`0011_mv_billing_messages` from `message_events` and `0012_mv_billing_connection_minutes` from
`connection_events`. A third from `media_events` is the established pattern rather than a new
idea. **4.6's objection was about the KEY, not the column count**: adding a channel dimension
multiplied the rows. This adds a summed column at the same `(environment_id, day)` key, so the
row count does not move at all.

**And the column cannot be called `stored_delta`.** That name is taken, and it does not mean
what a reader would assume: `sum(multiIf(event = 'created', 1, event = 'deleted', -1, 0))` over
`message_events` is a net count of **stored messages**. The new column is `stored_bytes_delta`,
and the chapter says the two apart in prose, because the premise check found this collision by
reading the view rather than the column name.

**Alternative rejected.** A separate `daily_storage` table keeps the names clean and makes every
billing reader open two tables for one tenant-day. DR-10's whole point is that billing reads one
rollup.

---

## R4 — The delta that has no producer

**Question.** FR-001's signed quantity needs a negative arm. What emits it?

**Nothing, and chapter 4.15 established why.** No code path deletes a `media_objects` row: the
rejection path removes **bytes** and keeps the row on purpose, because migration `0018` says *"a
rejected object's row is all that survives it."* The reaper is `docs/12` row 22's.

**So the negative arm has exactly one live producer — rejection — and the reconciliation cannot
fail in the direction that matters.** Until something deletes, the metered level only rises, and
a comparison against the store agrees for a reason that will stop being true. This is 4.7's
shape: FR-ANL-06 could not pass, and the product of that chapter was a clause amendment.

**Decision.** Build the negative arm now, driven by rejection, and shape the emission so the
reaper can call it without rework — one function, taking a tenant, a byte count and a cause.
The chapter records that the `deleted` cause has no caller, using the convention `CLAUDE.md`
sets: **a comment that says when something runs names the thing that runs it**, and *"called by
the reaper"* would be false today.

---

## R5 — What a delta-summed level costs against a sampled one

**Question.** FR-012 requires the chapter to state it. The difference is not stylistic.

**A sampled level is self-correcting and a summed one is not.** Sample wrongly on Tuesday and
Wednesday's sample is right anyway. Lose one delta and **every subsequent day is wrong,
permanently**, with nothing in the system able to notice.

**The size of one loss, measured over the lane's 8,120 chargeable objects:**

    total     4,255 MB
    mean        537 kB
    p50       1,024 bytes
    max          25 MB

**The mean is the wrong statistic and the spread is the finding.** A median loss is 1 kB —
invisible against a quota in gigabytes — and the tail loss is 25 MB, which is 0.6% of the whole
lane's storage on a single dropped record. **So the damage from one lost event is not a number,
it is a distribution**, and this is the argument for DR-17's reconciliation rather than a
rhetorical point about reliability.

**Why a sampler is not the answer anyway.** A daily sample needs something to run daily, and
ADR-28 records that this platform has no runner for a recurring job, no `schedule:` trigger, and
one hand-run script. A materialised view fires on insert. **That is why DR-17 says *summing
deltas* rather than *sampling a level*** — the clause already made this trade, and this research
only prices it.

---

## R6 — The precedent, and the thing it has never done

**`ingester/src/metering.ts`'s `storedMessages` is the shape to copy**, and its own comment says
so: *"DR-17 states the technique for the media analogue: summing `media_events` deltas
(uploaded/deleted). This is the same shape one table over."*

Two details in it are worth copying with the shape:

- **No empty-result guard.** *"A bare aggregate with no `GROUP BY` always returns exactly one
  row"* — asked of the server directly. A first version guarded `rows.length === 0` under a
  comment claiming a test drove both arms; it did not, and the guard was half the file's
  branches.
- **`flat()[0]` rather than `rows[0]?.[0]`**, because the optional chain is a branch too.

**And the precedent carries a latent defect nobody has met.** `storedMessages` reads
`sum(stored_delta) … WHERE day <= asOf` over a table whose TTL is **25 months**, so the count
it returns is short by every day the TTL has removed. That has never mattered, because
`message_events` holds **0 rows** and has no producer — 4.6's finding, re-measured for this
chapter. **Copying the shape copies the defect**, which is why FR-003 is now bounded at the
horizon and FR-003a asks what re-bases it.

`daily_usage_v2` holds 39 rows and
`daily_usage_billing` 44, all from backfills and tests. So the query is correct and the pipeline
under it has never run end to end. **This chapter is the first time that shape will carry a live
producer**, which means the failure modes it has are unobserved rather than absent.

---

## R7 — Emitting exactly once

**Question.** FR-005. A verdict delivered twice must not produce two deltas.

**Decision.** Every emission hangs off a state transition that is already a compare-and-set, and
off nothing else.

**Rationale.** `recordMediaVerdict` is `UPDATE … WHERE state = 'pending'`, so a second verdict
updates zero rows and returns `applied: false`; 4.14 keyed its `media.updated` event on
`applied` for exactly this reason, and the same hook serves here. `reserveMediaSlot` inserts a
row inside a transaction holding the environment lock, so a retried request either inserts once
or fails.

**What this does not give.** The publish itself is at-least-once — the record goes to a stream —
and the ingester's idempotence is `Nats-Msg-Id`, which 4.5 established carries one id per
message. That is the existing guarantee and this chapter does not improve it; FR-005 is about
not emitting twice, not about the broker delivering once.

**The probe is a deliberate duplicate**, because 4.15's idempotence bug class was caught by
issuing one rather than reasoning that the upstream guard made it impossible.

---

## R8 — What the rollup must beat

**The read DR-10 forbids is the one the quota already does**, and it is the honest baseline:
summing `declared_bytes` per tenant in Postgres costs **252 buffers** for the lane's busiest
environment (239 hit, 13 read). That query is correct for the quota — it is an operational read
of operational data — and it is what "billing scans raw events" would look like if billing
reached for it.

**What the rollup is measured against at implementation** is its own read: one row per tenant
per day out of a `SummingMergeTree`, against accumulating the same answer from raw
`media_events`. That comparison cannot be made until the producer exists, so it is a phase-6
measurement and not a phase-0 one. Recorded here so the chapter does not publish the 252 as
though it were the comparison DR-10 asks for.
