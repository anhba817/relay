# Relay — Scalability Measurement

**Date:** 2026-09-06
**Subject:** NFR-SCL-01, and the two review rows that were waiting on it
**Method:** `A` — analysis, including load testing, which is the verification method the
clause itself specifies
**Harness:** `relay-platform/scripts/scale/`

---

## Why this exists

Two rows of `docs/09-platform-implementation-review-2026-09-03.md` were open for the same
reason, and neither was a defect:

- **"One subject grammar per real-time kind is becoming a default rather than a measured
  decision."** The recommendation was to define a consolidation threshold. A threshold is a
  number, and there was none.
- NFR-SCL-01 — *"The system shall sustain 10,000 concurrent WebSocket connections per gateway
  instance"* — is **P1** and had never been verified.

One measurement answers both.

## What was measured

One api and one gateway, each spawned with `PORT=0`, against the compose stack. Real client
sockets, not simulated. The gateway's own RSS from `/proc/<pid>/status`, and the broker's
subscription count from `PUBSUB CHANNELS` — the subscriptions are only visible from Redis's
side, so inferring them from the source would not have been a measurement.

**The shape is forced by two platform rules rather than chosen.** `MAX_CONNECTIONS_PER_USER`
is 5, so N connections need at least N/5 users; and a gateway's subscription cost is per
CHANNEL, not per connection, so channels and connections have to vary independently or the
two are conflated.

## Results

    connections  channels  survived  gateway RSS  redis subjects  redis mem  connect rate
    ----------   --------  --------  -----------  --------------  ---------  ------------
         1,000       200     1,000        133 MB           2,000              1,230/s
         2,500       200     2,500        171 MB           3,500              1,363/s
         5,000       200     5,000        207 MB           6,000              1,441/s
        10,000       200    10,000        160 MB          11,000       7 MB   1,296/s
        10,000    10,000    10,000        157 MB          60,000      18 MB   1,675/s
        20,000       200    20,000        371 MB          11,000       9 MB   1,125/s

**Zero failures and zero closures in every row above.**

### NFR-SCL-01 is met, and the verb matters

The clause says **sustain**, not accept. A socket that is accepted and then dropped satisfies
"open" while failing the clause, so 10,000 connections were held for **90 seconds** — past two
of the gateway's 30-second ping intervals, with `MAX_MISSED_PINGS = 2`. All 10,000 survived;
`closeCodes` was empty.

**And the headroom is real**: 20,000 connections — twice the clause — opened and survived on
one instance at 371 MB.

### The subscription law

    redis subjects = 5 × channels + 1 × connected users

Every row above satisfies it exactly. The five per channel are `chan`, `revision`, `presence`,
`typing` and `member`; the one per user is `member:{env}:{user}`.

    10,000 connections, 10,000 channels →  chan 10,000 · revision 10,000 · presence 10,000
                                           typing 10,000 · member 20,000  = 60,000

**The per-user term dominates at realistic channel ratios and vanishes at 1:1.** At 200
channels, the five grammars cost 1,000 subjects of 11,000 — 9%. At one channel per user they
cost 50,000 of 60,000 — 83%. **Which term dominates is a property of the customer's data, not
of the platform**, and that is the fact a consolidation threshold has to be written against.

## What this says about consolidating the subject grammars

**A sixth grammar costs 10,000 subjects and about 3 MB of Redis at NFR-SCL-01's stated scale,
in the worst channel ratio.** Redis holds 60,000 subscriptions in 18 MB — roughly 300 bytes
each — and the gateway's RSS is unchanged between 11,000 and 60,000 subjects (160 MB against
157 MB, which is noise).

**So the answer is: not yet, and here is the number to revisit it at.**

Proposed threshold, to be recorded as an ADR:

> Consolidate onto a typed envelope when either holds:
>
>   - per-channel SUBSCRIBEs would exceed **six**, or
>   - a gateway instance's projected subject count exceeds **250,000**, which is 10,000
>     connections at one channel each with six grammars plus a 50% margin.
>
> Below that, a new kind takes its own subject when it cannot share an existing payload type —
> the rule `revision.ts` states and ADR-19, 20 and 21 reached independently.

**The rule was already being applied rather than followed.** Chapter 3.24 had grounds for two
new subjects and took one, putting edits and deletions under a discriminator on `revision:`,
and rode `fanout.ts`'s existing subscriber rather than adding a tenth Redis client. That is
what "measured decision" looks like; what was missing was the number to measure against.

## The finding nobody was looking for

**The platform's own connect limiter is 25 times below what the gateway can accept.**

`DEFAULT_LIMITS.connect` is **3,000 per minute** — 50 per second — and its comment derives it
from this very clause: *"NFR-SCL-01's ten thousand connections per gateway instance, divided
by one reconnection cycle"*. The gateway accepts at **1,125-1,675 per second**.

    filling one gateway to 10,000 from cold
      at the gateway's measured rate      7.7 seconds
      at the default connect limit        3 minutes 20 seconds

That is not a defect — the limiter exists to stop a client reconnecting in a tight loop, and
the comment says so. **But it means a reconnection storm after a gateway restart is bounded by
policy, not by capacity**, and the two numbers had never been put beside each other. An
operator planning a rolling restart needs the second number, and nothing in the platform
states it.

## What went wrong while measuring, and why the numbers still stand

**The first ladder measured the harness, not the gateway.** It reported `4004
connection_limit_reached` and HTTP `429`, which read like capacity limits and were neither:

- the shape put exactly five connections on each user, sitting precisely on
  `MAX_CONNECTIONS_PER_USER` with no headroom for a slot claim that races;
- **`redis-cli` is not installed on this machine**, so the `redis-cli flushall` between runs
  was a silent no-op for the whole first ladder, and slot claims from earlier runs persisted;
- the connect limiter refused the rest, exactly as designed.

Re-shaped to one connection per user across 10,000 distinct users, with the limiter lifted on
the test environment only, every run came back clean. **The corrected numbers are internally
checkable**: `5 × channels + 1 × users` holds to the unit in all six rows, which a
contaminated run would not do.

**A no-op that looks like a step is worse than a missing step.** `redis-cli flushall` printed
nothing and returned success-shaped silence because the shell reported `command not found` to
a stream nobody was reading — the same shape as a child's `EADDRINUSE` going to an unread pipe.

## Reproducing

    cd relay-platform
    SCALE_USERS=10000 SCALE_CHANNELS=200 node scripts/scale/seed.mjs > /tmp/seed.json
    # lift the connect limiter on the seeded environment only
    SCALE_SEED=/tmp/seed.json SCALE_CONNECTIONS=10000 SCALE_HOLD_MS=90000 \
      node scripts/scale/load.mjs

`SCALE_CHANNELS` varies the subscription cost, `SCALE_CONNS_PER_USER` the cap pressure, and
`SCALE_HOLD_MS` the difference between "opened" and "sustained".

## What this left in the lane

    channels named scale-c-*   10,604
    users named scale-u-*      24,020

**Left in place deliberately, and identifiable on purpose.** `reset-lane.mjs` clears broker
debris and stale delivery rows and touches no organisation, user or channel — by design, since
the constitution requires the seeded demo tenant to survive. Deleting 24,000 users would cascade
through memberships and messages and needs the global-operation guard's exemption, which is more
risk than a tidy row count is worth today.

**It does change the lane's shape**, and the next person taking a measurement should know: this
lane's largest channel population used to be small enough that `CLAUDE.md` recorded "the lane's
largest membership set is FIVE channels — it cannot see any of this". It can see rather more now.
The rows are prefixed so they can be found and removed in one statement when someone wants them
gone.

**These numbers are this machine's**: 28 cores, 30 GB, 524k file descriptors, one gateway and
one Redis on the same host as the load generator. A deployment's numbers will differ; the
subscription law will not.
