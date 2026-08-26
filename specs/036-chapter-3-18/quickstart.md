# Validation guide — chapter 3.18

Five scenarios. The first is the feature; the second is the constitution's gate; the third is the
one that proves the tests are not lying; the fourth and fifth are the risks this plan could not
close by reading.

## Prerequisites

    docker compose up -d          # Postgres on 15432, Redis on 16379 — not 5432/6379,
                                  # this machine's own Postgres holds 5432
    pnpm install && pnpm build    # check:errors reads packages/protocol/dist — BUILT, not src

Nothing else runs on the machine during a timing battery.

## 1 — the feature: a REST send reaches a socket

The scenario chapter 3.14 recorded as failing. It belongs in the **outsider** lane — and analysis
established that it has nowhere else to go. **No suite in this repository boots a real api with a
real gateway**: the gateway's suites stub `ApiClient` because the gateway has no database (ADR-05),
and no api-side suite opens a socket. `packages/outsider/` reads `RELAY_API_URL` *and*
`RELAY_WS_URL` and runs against a platform it did not start, so it is the only place where a real
REST send and a real socket meet.

Everything else is proven at a seam: the api publishes the right payload to the right subject
(`services/api/src/fanout/fanout.itest.ts`, a real Redis subscriber), and a frame on `chan:{id}`
reaches the right sockets (gateway suites, publishing to the subject directly — no api needed).

    open a socket as user A, subscribed to channel C
    POST /v1/channels/C/messages with an API key, sender B
    -> the socket receives message.created with seq, user B, and the text

    pnpm test:outsider

**Expected before the work: a timeout.** Confirm that first. A scenario that passes before the
feature is written is testing something else — 3.17's T047c passed with half its subject applied.

## 2 — the constitutional gate: a lost publish is recoverable

Principle IV: *"Any new delivery mechanism MUST preserve this recovery property."*

    stop Redis (or point the publisher at a dead port)
    POST /v1/channels/C/messages  -> 201, and the response is not slow (see 5)
    read the channel's history
    -> the message is there

No socket is needed for this one: resume reads Postgres, so the recovery property is provable
api-side. The message must be reachable even though no frame was ever published.

The message must be reachable by resume even though no frame was ever published. This is FR-010 and
FR-011's test as well as the constitution's.

## 3 — the assertion that distinguishes anything

**Scenario 2 passes with the publisher deleted.** `publish` swallows its own errors and resolves
(R8), so "the send returned 201 while Redis was down" is true of a no-op. Run this to prove the
suite can tell:

    delete the publish call, or point it at a dead port with the log assertion removed
    -> scenario 2 stays green

The assertion that carries FR-010 is the **`fanout.publish_failed` log line**, and the one that
carries the feature is scenario 1. Any new test on this path states what would have to be false for
it to fail; this suite's central mechanism is designed to be invisible when it breaks.

## 4 — the two guards mirrored from the gateway

    send twice with the same idempotency_key   -> the socket receives ONE frame  (FR-006)
    recover a tombstone with an old key        -> the socket receives NO frame   (FR-007)
    send to a channel the key may not write    -> 403, and NO frame              (FR-008)

FR-008 is the one with no precedent in the gateway, and the one a `finally` gets wrong.

## 5 — the measurements to take rather than assume

Record every number in `baseline.txt`. Four of them are decisions in this plan, not observations.

| measurement | why it is here |
|---|---|
| `PUBLISH` latency, Redis live, p50/p95 | the contract claims sub-millisecond against a 150 ms budget |
| REST send latency with Redis **dead**, p95 | R10's hazard: does the send stay fast, or wait out a connect timeout? NFR-PRF-02 is 150 ms |
| the same, with `createFanout`'s default options | the number that justifies not copying the gateway's client |
| the integration lane, 20+ runs | 589 tests at 3.17's close, mean 193.55 s, 240 s budget |

**And the two premises to test rather than believe:**

- **R10 — does a listener-less ioredis client take the process down?** Stop Redis, send on a
  *socket*, watch the gateway. `createFanout` has no `error` listener and no test covers a dead
  fan-out. If it dies, that is pre-existing and this chapter surfaced it.
- **R5 — FR-RTM-10's five seconds.** Remove a member while their socket is open, then send to the
  channel over REST. Nothing in the delivery path re-reads membership; the subscription is a
  snapshot taken at connect. Try it on the socket path too — if neither path meets the window, the
  honest outcome is a recorded gap, not a quiet claim.

## Gates before close-out

    pnpm turbo run test          pnpm test:integration       pnpm test:outsider
    pnpm coverage                pnpm check:fences           pnpm check:figures
    pnpm check:errors            pnpm check:srs              pnpm check:docs

`git diff --name-only` against `check:fences` at the very end, both repositories. That comparison
split the file count in 3.16 and found two files in no bucket; the plan's twelve-path fence column
is a first count and is expected to be wrong.
