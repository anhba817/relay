# Data model — chapter 3.7

No table, no column, no migration. The only new state is one field on a struct
that lives in a gateway process's memory and dies with a socket.

---

## `Connection` — amended

`services/gateway/src/registry.ts`, which today holds `id`, `identity`, `socket`,
`channelIds`, `missedPings`, `phase`, `buffer` and `overflowed`.

| Field | Type | Null | Meaning |
|---|---|---|---|
| `marks` | `Record<string, number>` | yes | Per channel, the highest sequence this connection's backfill delivered. Null for a connection that never resumed, and null after a resume that degraded. |

**Why it is on the connection and not in Redis.** It describes what one socket has
been shown. Two sockets for the same user resuming from different cursors have
different marks, and neither is a fact about the user. Constitution IV also
forbids Redis holding anything that is a source of truth, and a shared mark would
be exactly that: a value whose loss would change what a client receives.

**Why it is nullable rather than an empty object.** Three states have to be
distinguishable and only two of them are "no suppression":

```text
null           a fresh connect, or a degraded resume — suppress nothing
{}             a resume whose cursor set was empty after scoping — suppress nothing
{ chan: 42 }   a completed resume — suppress at or below 42 on that channel
```

The middle case is reachable (a client presents cursors only for channels it has
since left) and behaves like the first. Keeping them distinct costs nothing and
makes the degraded path explicit rather than incidental.

---

## The lifetime, which is the whole design

```text
fresh connect            marks = null
resume, degraded         marks = null        ← FR-005: told to page history,
                                               so no mark can be trusted
resume, ok               marks = highWaterMarks(cursors, backfilled)
live delivery            marks are READ and never written
socket closes            marks go with it
```

**Never retired, and that is the correction research R3 made to the spec.** The
spec assumed the mark for a channel would be dropped once a higher sequence
arrived. Sequences commit in order under a channel row lock, but they are
*published* by whichever gateway instance handled each send, and those two
instances do not coordinate. A stalled publish of sequence 4 can land after a
prompt publish of sequence 5, so retiring on 5 would hand the duplicate window
straight back.

**Bounded without retirement.** `marks` is derived from the resume cursors, and
those are capped at `MAX_RESUME_CHANNELS` (200) by
`internalBackfillRequestSchema` — a larger map is refused by the api and the
resume degrades, which sets `marks` to null. So the retained state is at most 200
integers per resumed connection, constant in the connection's lifetime, and the
same order as the cursor map the connection already accepted. FR-007 is satisfied
by a cap that already existed.

---

## The predicate

A frame is suppressed when its channel has a mark and its sequence is at or below
it.

```text
suppress  ⟺  marks !== null  ∧  marks[frame.channel] !== undefined
                             ∧  frame.seq <= marks[frame.channel]
```

**Why `<=` and not `<`.** The mark IS a sequence the backfill delivered, not the
one after it. `flushable` already makes this comparison for the buffered case and
its comment records the same reasoning — "off-by-one here is user-visible" — which
is why the new predicate is written beside it rather than somewhere else.

**Why no legitimate frame lives at or below the mark.** The backfill delivered
every message with a sequence above the presented cursor and up to the mark.
Anything at or below the cursor the client already had before it disconnected.
Sequences are monotonic per channel and never reused. So a frame arriving at or
below the mark is a frame the client has seen, in every case, for as long as the
connection lives.

That argument is the reason suppression is safe and it is also the thing most
worth attacking: it is the only place this chapter could turn a duplicate into a
gap, which is a worse failure. Constitution II is why the quickstart spends two
scenarios and a sabotage mutation on it.

---

## What deliberately does not change

- **`phase`** keeps its meaning and its two values. The mark is not a third phase;
  a connection with marks is fully live and delivering.
- **`buffer`** and `overflowed` are untouched. The buffering window still exists
  and still does its job for frames published inside it.
- **`flushable`** is untouched. The new predicate generalises it rather than
  replacing it, and both stay.
- **Nothing in the api.** No column, no query, no contract field.
