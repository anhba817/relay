# Contract — the resume sequence, amended

Chapter 2.7 defined five steps. This chapter changes what happens after the fifth,
and changes nothing a client can observe except that it stops receiving a frame
twice.

## The sequence, with the amendment

```text
1 subscribe   from this instant no frame can be missed
2 buffer      hold live frames; they might duplicate the backfill
3 backfill    seq > cursor per channel, in order; note the high-water mark H
4 flush       emit buffered frames with seq > H; discard seq <= H
5 live        normal delivery — AND KEEP H, discarding frames at or below it
                                 ^^^^^^^^^^^^ chapter 3.7
```

Steps 1 to 4 are unchanged. Step 5 previously discarded `H`.

## Why step 5 needed it

A message is durable and a message is announced at two different instants. The
gateway commits through the api and publishes to the fabric afterwards:

```text
committed = await api.send(...)   ← durable here; a backfill query can see it
await fanout.publish(...)         ← announced here
```

A resuming connection whose backfill lands between those two instants receives the
message from the backfill, sets `H` to its sequence, flushes, goes live — and then
the publish arrives. Before this chapter, step 5 had nothing to compare it
against.

## Suppression

| Rule | |
|---|---|
| A frame is suppressed when its channel has a mark and `seq <= mark` | FR-001 |
| A frame with `seq > mark` is always delivered | FR-002 |
| A frame on a channel with no mark is always delivered | FR-004 |
| The mark is retained for the life of the connection and never retired | research R3 |
| A connection that never resumed has no marks | FR-006 |
| A connection whose resume degraded has no marks | FR-005 |

**`resume_ok: false` retains nothing.** A degraded resume tells the client to page
history for every channel, so the backfill it received is an arbitrary fragment or
none at all. A mark taken from it would suppress messages the client never got —
turning a duplicate defect into a gap defect, which is worse. The degrade path
clears the buffer today; it must clear the marks for the same reason.

## Invariants

| # | Invariant |
|---|---|
| 1 | A resumed connection is never delivered a message whose sequence is at or below its backfill's high-water mark for that channel. |
| 2 | A resumed connection is delivered every message whose sequence is above that mark. Suppression never creates a gap. |
| 3 | Suppression applies after the connection goes live, not only while it is buffering. |
| 4 | The mark is per channel: a mark on one channel never suppresses a frame on another. |
| 5 | A connection that resumed with `resume_ok: false` suppresses nothing. |
| 6 | A connection that never resumed suppresses nothing and retains no state. |
| 7 | The retained state is at most one integer per channel in the resume cursor set, which the resume contract already caps at `MAX_RESUME_CHANNELS`. |
| 8 | Two frames published out of order by different gateway instances are both handled correctly: the later-arriving lower sequence is still suppressed. |

Invariant 8 is the one the spec's original design would have failed, and it is the
reason the mark is never retired. Sequences commit in order under a channel row
lock; they are published by whichever instance handled each send, and those do not
coordinate.

## What a client observes

Nothing new. The wire contract is unchanged — no new frame type, no new field, no
change to the resume ack. A client that was correct before this chapter is correct
after it and receives strictly fewer frames.

That is worth stating because it bounds the blast radius: this cannot break an
SDK, a reference client or a customer integration, because there is nothing new
for them to understand.

## What is NOT promised

- **Ordering across gateway instances on the live path.** Two instances publishing
  concurrently can still deliver sequence 5 before sequence 4 to a connection with
  no mark on that channel — a fresh connect, for instance. That is chapter 2.6's
  at-most-once fabric behaving as designed, and the client's own sequence handling
  is what resolves it. This chapter fixes duplication against the backfill, not
  fabric ordering in general.
- **Deduplication of anything but `message.created`.** Later frame types that
  carry an original sequence — an edit, a tombstone — are not covered by a
  sequence floor and must not be, since their sequence is deliberately old. The
  suppression is keyed to the frame type that carries a new sequence.
