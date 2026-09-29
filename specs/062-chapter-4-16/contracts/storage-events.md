# Contract — the storage record, and the consumer that must know it first

## The record

Published by the api on `analytics.media.stored.{environment_id}`, consumed by the ingester.

```
{
  type: "media.stored",
  environment_id: uuid,
  media_id: uuid,
  event: "reserved" | "rejected" | "rendition" | "deleted",
  kind: "image" | "audio" | "video",
  bytes_delta: integer,          // signed; carried, never inferred from `event`
  occurred_at: RFC3339 with milliseconds
}
```

## The order this ships in, and why it is not a preference

**THE CONSUMER LEARNS THE TYPE BEFORE THE PRODUCER EXISTS.** `route()` returns
`{ kind: "unclaimed" }` for a type it does not know, and what happens next is **not** what
chapter 4.4 measured — 049 repaired it. `ingest.ts:100` is the current behaviour:

> NEITHER ACKED NOR TERMINATED. Acking would consume a record this consumer did not write;
> terminating would destroy it. Left alone it is redelivered until something claims it or the
> stream's seven days expire — and the count below is the only way anyone finds out.

So a record from an unknown producer is **not destroyed** — it is redelivered for up to seven
days, and the `unclaimed` counter is the only signal. That is better than 4.4's outcome, where
records were terminated and both instruments reported health (*"depth said the records were
there and lag said there was nothing to do"*), and it is still a producer shipping into
silence: nothing lands in ClickHouse and nothing fails.

**The red probe asserts the current behaviour**: publish a `media.stored` record against the
consumer as it stands, confirm it comes back `unclaimed` and is redelivered, then ship the arm
and watch the count go to zero. **Asserting termination would fail for the wrong reason**, and
the likely response to that is to conclude the probe is broken.

## Invariants

1. **`bytes_delta` is the quota's quantity.** The quota sums `declared_bytes` where
   `state <> 'rejected'`, so a `reserved` event carries `declared_bytes` and a `rejected` event
   carries its negation. A verified size that differs from the declared one does not change
   this, because FR-002 requires the meter and the quota to agree about what a byte is.
2. **One transition, one record.** Every emission hangs off a compare-and-set that already
   exists, so a retried verdict emits nothing. Asserted with a deliberate duplicate.
3. **Publishing cannot fail the request.** Constitution III: a slot request succeeds with the
   analytical store stopped. Whether the record is then lost or retained is stated explicitly
   rather than left to be discovered — SC-005 makes the chapter say which.
4. **The sign is carried, not inferred.** A reader that derives it from `event` puts the rule
   in two places.
5. **`kind` is present on every record, including `deleted`**, so the per-kind counts can be
   reversed by the same view that builds them.

## What does not change

- **The quota.** It reads Postgres and will keep reading Postgres (`data-model.md` §4).
- **The subject grammar.** `analytics.media.stored.{env}` is one more token under
  `analytics.>`, which the ingester already consumes. Verified: `ALL_ANALYTICS_SUBJECT` is
  `analytics.>` and is used for both the stream's `subjects` and the consumer's
  `filter_subject`, so there is **no stream or consumer change**.
- **The listing's API version.** The inventory uses the **V1** bucket listing, which pages with
  `marker`. V2 (`list-type=2`) pages with `continuation-token` and was not what the research
  measured working.
- **`stored_delta`.** A different column, counting a different thing, left alone.
