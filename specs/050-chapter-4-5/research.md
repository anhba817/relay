# Research — chapter 4.5, the gateway's first stream

**Feature**: `specs/050-chapter-4-5/` · **Date**: 2026-09-14
**Method**: the stack up on its documented ports. Every probe that reports a number was run;
every claim about the tree was read from the tree rather than from `docs/12`.

---

## R1 — The gateway holds no broker client, and that is the whole of the claim

```
grep -rn "nats\|jetstream" --include=*.ts services/gateway/src   ->   no matches
dependencies: @relay/protocol, @relay/service-kit, ioredis, jose, ws       (5)
```

**Decision**: the count is the finding, not the absence. ADR-07 rests its rejection of NATS on
how many client libraries the gateway holds (R8), so **5 → 6** is the number this chapter
changes and it is recorded before and after.

---

## R2 — The close handler already refused to report, for this chapter's reason

`services/gateway/src/session.ts:1140`, in the `socket.on("close")` handler:

> Handing over totals rather than reporting them. This handler is already documented as the
> last place that should throw, and **a mass disconnect would turn one event into a burst of
> HTTP requests.**

So chapter 3.24 asked "should the close handler report?" and answered no. It calls
`meter.closed(connection, new Date())` and lets a sixty-second tick do the reporting.

**This chapter wants to emit an event at close, which is the thing that handler declined to
do.** The argument 3.24 made was about HTTP. Whether it survives a broker is R3's job.

---

## R3 — A publish per close is the same burst on a different transport

**Probe**: 2,000 connection-close records, three ways, against a stream of their own.

```
awaited, one at a time   : 2000 publishes in 458 ms  -> 0.229 ms each
  extrapolated to 10,000 closing at once: 2.3 s of awaited publishes
core publish + flush     : 2000 publishes in   6 ms  -> 0.0030 ms each
pipelined, 500 in flight : 2000 publishes in   7 ms  -> 0.0034 ms each
```

**Decision**: buffer in the gateway and publish on a tick, exactly as `meter.ts` already does —
**one JetStream message per record**, with up to 500 publishes in flight and their acks
collected together.

**A JetStream publish awaits an ack.** At 0.229 ms each, a deploy that closes NFR-SCL-01's
10,000 connections serialises **2.3 seconds** of awaited publishes through close handlers —
which is 3.24's burst argument arriving on a new transport, and its answer is the same one.

**Pipelining is 67× faster than awaiting per close and keeps what core publish gives up.** Core
`nc.publish` is faster still — 0.0030 ms — but it is at-most-once with no ack and no
deduplication id, so a record lost in the gap is lost silently. Pipelined JetStream publishes
are within 13% of core speed and keep the ack and the deduplication id on **every** record.

### CORRECTED IN ANALYSIS PASS 5 — THE THIRD ROW READ "batched 500 per publish"

That phrase reads as **500 records inside one message**, and three artifacts adopted it in that
form. The number is unaffected; the shape is not, and the batched-payload reading breaks three
claims this feature has already published.

**The current ingester TERMINATES it, and that needs no broker to check.** `route()` tests
`typeof raw === "object"` and then `raw.type`. An array passes the first and has no `type`, so
it takes the attempt arm, `shape()` returns `null`, and `ingest.ts` calls **`m.term()`**:

```
route([{type:"connection.opened",…}, …])
  typeof raw === "object" && raw !== null   -> passes
  raw.type === undefined                    -> the attempt arm
  shape(raw) -> null                        -> {kind:"malformed"} -> m.term()
```

One message of 500 records is destroyed as **one** malformed record. That also kills R8: a
batched record never reaches the `unclaimed` arm that retains it, so the phase 2 / phase 3
window would prove the opposite of what it was built to prove.

**One message carries one `Nats-Msg-Id`**, so the contract's `{connection_id}:{event}` cannot
hold across 500 records. Whatever id a batch carries is batch-derived — which is 048's measured
finding verbatim: *"the same token with 500 different rows dropped all 500 and reported
success. A token that is not provably unique per batch is not weak deduplication — it is silent
data loss."*

**One message carries one subject**, and the subject is
`analytics.connection.{opened|closed}.{environment_id}`. A batch from a gateway holding 10,000
sockets spans many tenants and both events, so it has no subject to be published on —
and `analyticsSubjectFor`'s own comment calls a mis-addressed subject *"constitution I stated as
a parsing problem."*

**So the surviving reading is pipelining**, which is also the only one compatible with the rest
of the feature: per-record subject, per-record dedup id, one record per `route()` call. T004
re-runs the probe and records **which shape it measured**, because the units in the original
three rows differ — two say *publishes* and the third said *records* — and nothing in the
artifacts disambiguated them.

**Alternatives considered**: publish per close and accept the burst (rejected by the number
above); core publish per close (rejected — this stream's whole value is that a consumer can
recover it, and 3.20 chose JetStream over core for that reason); 500 records in one message
(rejected by the three reasons above, not by a measurement).

---

## R4 — The two counters measure different quantities and share a name

`meter.ts:56`:

> **A CONNECTION IS CHARGED FOR EVERY CALENDAR MINUTE IT WAS OPEN FOR ANY PART OF.** Open at
> 00:00:59 and closed at 00:01:01 is two seconds of wall clock and TWO connection-minutes,
> because it was present in both minutes.

So the meter counts **minute buckets touched**. Connection-minutes derived from an open and a
close record would be **elapsed duration**. For the example above: 2 against 0.03.

**Decision**: FR-009's reconciliation compares them **with the rule stated**, and the chapter
publishes the disagreement as a number rather than calling it small. The two are not the same
quantity and no amount of care makes them agree; what can be checked is that
buckets-derived-from-records equals buckets-from-the-meter, which is a comparison of one
quantity computed twice.

**This is 4.2's boundary-day finding one domain over.** There a daily rollup and a
timestamp TTL disagreed on the oldest day by 4,941 and always would. Here a wall-clock bucket
and an elapsed duration disagree by up to a minute per connection, and always will.

---

## R5 — Where open and close are visible

Open: the session handshake, where `identity` is resolved — so the environment is available.
Close: `socket.on("close", (code) => …)`, which carries the close **code** and runs before
`registry.remove`.

**Decision**: the open record is written beside `registry.add(connection)` (`session.ts:959`)
and the close beside `meter.closed(...)` (`session.ts:1146`).

**CORRECTED IN ANALYSIS PASS 1 — THERE IS NO `meter.opened`.** This item first said both records
sit beside an existing meter hand-over. The `Meter` interface is `closed`, `reportOnce`,
`retained`, `dropped` and `stop`, and its comment says why: *"A socket closed. Its final totals
are handed over here, because the registry has already forgotten it by the time anything else
could ask."* **The meter is told about closes and walks the registry for opens**, so the
symmetry this item assumed is not there and the two records take two different anchors.

**Open**: whether a connection that never authenticates has an open event at all. It has no
environment and no identity, and the `_none` arm 4.4 built is for requests rather than
connections. Left to the plan's phase 1 rather than assumed here.

---

## R6 — ADR-07 names the argument this chapter spends

v1.1, verbatim:

> Core NATS pub/sub was added to the rejected list. … **That refusal is deliberately weaker
> than the others: it is an argument about how many client libraries the gateway holds, not
> about whether the mechanism fits.**

**Decision**: amend ADR-07 a third time, and the amendment's job is to say what the fan-out
decision now rests on — not to change it.

**What survives once the library count is spent**: ADR-10 puts presence in Redis, so Redis is
mandatory for the gateway regardless; the v1.1 text says a NATS-only proposal would have to
move presence too and would be "a larger decision than this ADR". That is the surviving
argument, and it was always the stronger one. The chapter's job is to make the record rest on
it explicitly, because a reason that no longer holds is worse than no reason: it reads as
settled.

---

## R7 — A third producer on the shared stream

4.4 measured 320 bytes per request record and a crossover where `max_bytes` binds before
`max_age`: **5.5 requests/second** for seven days, **38.8** for the SAD's 24 h.

Connection events are assumed lower volume — one pair per connection against one per request —
and **that assumption is not measured yet**. FR-015 measures it. The figure that matters is the
combined rate of all three producers, not this one's alone.

**Decision**: deferred to implementation with a number attached, the way 4.4's R12 was. 4.4
found its own carried figure 2% light for including the probe's subject; this one measures
against a length-matched subject from the start.

---

## R8 — The ingester's third record type

4.4 built `route()` with an `unclaimed` arm that leaves a record it does not write rather than
terminating it, and an integration test that proves the record comes back. So a connection
event published before the ingester writes it is **safe** — it accumulates and is redelivered.

**Decision**: publish first, teach the ingester second, and use the window between them as the
proof that `unclaimed` works on a real record rather than a synthetic one.

---

## R9 — What the close code can and cannot say

The handler receives a WebSocket close code. `CLOSE_CODES` is a published registry — `check:errors`
compares it in both directions — so the code is a controlled vocabulary rather than free text.

**Decision**: record the code, not a reason string. A reason is a sentence somebody writes; a
code is a value a checker already guards.

---

## R10 — The deploy case, which produces records that do not balance

`releaseAll` in the session module handles a gateway stopping with connections open. Whatever
this chapter does, a killed instance produces opens with no closes.

**Decision**: state it rather than engineer around it. The chapter publishes the open/close
balance for a clean run and for a killed one, and the difference is the number that says what
a dashboard built on these records must tolerate.
