# Captured output — chapter 3.4

Everything the chapter quotes should come from here. **The original captures were
lost with the machine**; every transcript below was re-captured on 2026-08-10
from the reconstructed code, against the compose stores, and is therefore a fresh
run rather than the one the chapter's prose was written from.

Where the chapter quotes a number that is a property of the author's database
rather than of the code — the stream's message count — this file records what the
number is *here* and flags the discrepancy rather than pretending to reproduce
it. See "Numbers that cannot be reproduced" at the end.

No credential and no tenant message body appears (spec FR-021, quickstart V8).

---

## Lane counts

| Lane | Before (baseline.txt) | After |
|---|---|---|
| `pnpm test` (Docker-free) | 120 | **133** |
| `pnpm test:integration` | 87 | **97** |

New: `internal.test.ts` (5), `runtime.test.ts` (8), `consumer.itest.ts` (10).
Every pre-existing suite passes with its assertions unchanged. Both lanes exit 0.

Per package, after:

```text
unit          @relay/service-kit  3   @relay/config  6   @relay/protocol 31
              @relay/api         59   @relay/gateway 34          TOTAL 133
integration   @relay/api         76   @relay/gateway 13   @relay/e2e  8   TOTAL 97
```

---

## The ten broker-backed invariants, as the runner prints them

```text
✓ invariant 1: the stream's settings read back exactly as configured
✓ invariant 2: applying the configuration twice is a no-op, not an error
✓ invariant 3: an event is delivered, handled once, and acknowledged
✓ invariant 4: a kill between handling and acknowledgement is redelivered — and handled once (SC-003)
✓ invariant 5: deduplication survives a restart
✓ invariant 6: two instances sharing a durable name divide the work
✓ invariant 7: a handler that always throws stops being retried
✓ invariant 8: an unparseable payload is terminated on the first attempt
✓ invariant 9: a consumer stopped for N publishes receives all N on restart
✓ invariant 12: a consumer log line carries counts, never payloads

Test Files  1 passed (1)
     Tests  10 passed (10)
  Duration  102.47s
```

Invariant 4 takes 30.3 s and invariant 7 takes 63.3 s. Those are the
acknowledgement deadline and the delivery bound being real.

## The two pure invariants

```text
✓ invariant 10: a handler that throws is retried, never acknowledged
✓ invariant 11: a duplicate claim is acknowledged, not handled again
✓ terminates an unparseable payload instead of retrying it
✓ never lets an unparseable payload reach the claim or the handler
✓ acknowledges an event whose claim and handler both succeed
✓ runs the handler INSIDE the claim, so the two share a fate
✓ passes the broker's delivery count to the handler
✓ treats a delivery with no stated attempt as the first one

     Tests  8 passed (8)
```

---

## The sabotage check (quickstart V3)

Three mutations to `runtime.ts`, each reverted afterwards and the file verified
byte-identical to its fence:

| Mutation | Failed |
|---|---|
| `catch` returns `acknowledge` instead of `retry` | **1** — invariant 10, alone |
| the unparseable early-return removed | **2** — both poison-message cases |
| the handler run *outside* the claim | **2** — invariant 11 and the shared-fate case |

The third is the one worth keeping: moving the handler out of the claim breaks
invariant 11, because a duplicate then re-runs the effect — which is exactly the
double-webhook, double-metering failure SAD risk R5 names.

---

## What the broker actually holds

```text
stream EVENTS
  messages           14
  consumers          9
configuration
  subjects           ["events.>"]
  retention          limits   (immutable once created)
  storage            file    (immutable once created)
  replicas           1
  max_age            604800s   (NFR-REL-08 floor: 86400s)
  max_bytes          1.00 GiB
  discard            old     (at the bound, drop the OLDEST)
  duplicate_window   120s   (the broker's dedupe, not ours)
```

The configuration block matches the chapter line for line. The counts do not —
see below.

---

## The walk, both ways

```console
$ node scripts/consumer-walk.mjs
durable consumer           walk-5792195b
environment                5e0c0ec6-5733-41a1-b988-29d058d15e07
published                  173888c2-3ab7-4f69-8999-f636d0add1e0
delivered                  173888c2-3ab7-4f69-8999-f636d0add1e0 attempt=1 redelivered=false
claim                      handled
acknowledged               173888c2-3ab7-4f69-8999-f636d0add1e0
```

```console
$ node scripts/consumer-walk.mjs --kill-before-ack
durable consumer           walk-87ddfbec
environment                b12439b3-0960-4cf4-9794-997b3ecd6ca7
published                  aa03e7eb-1a8c-4863-b066-828c3796ec3c
delivered                  aa03e7eb-1a8c-4863-b066-828c3796ec3c attempt=1 redelivered=false
claim                      handled
times handled              1
MARKER kill-me-now
```

The second stops with the claim committed and no acknowledgement sent. That is
the state the test's `SIGKILL` freezes, and the state the redelivery has to be
safe against.

---

## Coverage — the measurement three chapters deferred

```text
Statements   : 88.22% ( 809/917 )
Branches     : 79.01% ( 369/467 )
Functions    : 89.35% ( 193/216 )
Lines        : 89.67% ( 756/843 )

services/api/src/consumer     93.50 stmt   86.11 branch   93.33 func   94.36 line
services/api/src/db/repository.ts
                              96.18 stmt   86.30 branch  100.00 func   98.33 line
```

Exit 0. Feature 024's per-file ratchet on `repository.ts` is 85% branches; this
chapter adds `claimEvent` and `timesHandled` to that file and the figure moves
**up**, 85.91% → 86.30%. Workspace statements 86.55% → 88.22%, branches 78.07% →
79.01%.

NFR-MNT-02 asks for 100% branch coverage on ordering, idempotency and isolation
code. `repository.ts` holds all three and is at 86.30%. That gap is now a
measured number with named uncovered branches rather than an unknown.

---

## Numbers that cannot be reproduced

The chapter opens and closes on the stream's message count — "12,930" in the
opening transcript and "12,941" in the checkpoint. Those came from the author's
database after a chapter's worth of running, and that database is gone. A fresh
stack reports 14.

**This is not a defect in the code and it is not fixable by re-running.** The
options are to leave the numbers as historical transcripts, or to re-capture the
opening and closing blocks against a stack that has been run for a while. The
recommendation is the latter, because the chapter's argument in the opening
paragraph — "twelve thousand nine hundred and thirty events, and not one of them
has ever been read" — depends on the number being large enough to feel like a
backlog. Recorded in `chapter-notes.md` finding 2 as an open item rather than
silently corrected.

The consumer count of 9 in the block above is this session's test durables
(`itest-basic-*`, `itest-poison-*`, `itest-shared-*`, `recorder`, three `walk-*`)
and is likewise an artifact of the run, not a property of the chapter.
