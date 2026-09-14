# Feature Specification: chapter 4.5 — the gateway's first stream

**Feature**: `specs/050-chapter-4-5/` · **Part 4, movement III, chapter 5 of 22**
**Created**: 2026-09-14
**Status**: specified

## Where this ordinal comes from

`docs/12-part-4-structure.md` §3's movement map gives movement III as chapters 4–5. 4.4 built
FR-ANL-07's API request producer; this is the other half — **connection open and close**, the
last arm of FR-ANL-01 that has no producer.

§3's table describes it in one line: *"Connection open/close (FR-ANL-01). **The gateway has
never touched NATS** — verified, zero references in `services/gateway/src`. Amends ADR-07 a
second time; see §7.2."*

Two of those three claims survive contact with the tree. The third is understated.

## The premises, run rather than assumed

### 1. The gateway has never touched NATS — confirmed

```
grep -rn "nats\|jetstream" --include=*.ts services/gateway/src   ->   no matches
```

And its dependencies are `@relay/protocol`, `@relay/service-kit`, `ioredis`, `jose`, `ws`.
Five, none of them a broker client. Every other service in this platform holds one.

### 2. But the gateway already reports connection data, and it goes through the api

This is the part §3's line does not say, and it changes what the chapter is about.
`services/gateway/src/meter.ts` has been computing connection-minutes since chapter 3.24 and
shipping them to the api every sixty seconds:

```
POST /internal/usage/connections
  { connections: [ { connection_id, environment_id, period, minutes } ] }   1..5000 entries
```

So the chapter is **not** "the gateway has no way to report what it sees". It is *"the gateway
has one, it was built for a different question, and it goes through the service the analytical
path is supposed to be independent of."*

| | the existing path | what FR-ANL-01 asks for |
|---|---|---|
| shape | minutes, aggregated per connection per period | an event at open and an event at close |
| cadence | every 60 s, batched | at the moment it happens |
| destination | the api, then Postgres | the analytical store, via a durable queue |
| purpose | FR-RTL-05's monthly quota, refused synchronously | FR-ANL-05's daily metering |
| failure | a report the api refuses is a quota that undercounts | a lost event is a gap in a dashboard |

### 3. ADR-07 names its own weakest point, and this chapter spends it

`docs/12` §7.2 says giving the gateway a publisher *"amends ADR-07 a second time"*. It does
more than that. ADR-07's v1.1 amendment, verbatim:

> Core NATS pub/sub was added to the rejected list. … **That refusal is deliberately weaker
> than the others: it is an argument about how many client libraries the gateway holds, not
> about whether the mechanism fits.** A NATS-only proposal that also moves presence off Redis
> (NATS KV) would reopen it legitimately, and would be a larger decision than this ADR.

**The one argument keeping NATS out of the gateway is the count of client libraries it holds,
and this chapter increases that count by one.** After this chapter the gateway holds a NATS
client — so the stated reason for rejecting NATS as the fan-out fabric is spent, on ADR-07's
own terms, by a chapter that is not about fan-out at all.

**AND THE BODY ABOVE THAT AMENDMENT ALREADY CARRIES THE REASON THIS CHAPTER THOUGHT IT WAS
SUPPLYING.** Four artifacts quoted the v1.1 block and none opened the paragraph it amends.
ADR-07's original rejected list, verbatim:

> core NATS pub/sub (technically apt — at-most-once, subject-based, comparable latency — and
> **refused on dependency shape rather than mechanism: Redis is mandatory for the gateway
> regardless, since ADR-10 puts presence in Redis with TTLs, so fan-out on NATS would leave
> that service holding two broker clients and remove none**)

So "Redis is mandatory regardless" is not a surviving argument this chapter restores — it has
been in the record since the decision was accepted. **What this chapter falsifies is the
arithmetic in the same parenthesis.** "Would leave that service holding two broker clients and
remove none" describes a gateway that holds one client; after this chapter it holds two anyway,
so moving fan-out to NATS would **add none and still remove none**. The cost side of the
refusal goes to zero and the refusal survives on Redis's mandatory-ness alone.

That does not mean the fan-out decision should change. It means the sentence that priced the
decision stops being true, and the record has to say what it costs now — which is nothing, and
is therefore no longer an argument at all.

### 4. And 4.4's finding lands squarely on this gateway

Chapter 4.4 measured that the gateway's calls to `/internal/usage/connections` carry a
`platform` principal, which has no `environmentId` by design — so **every one of them is
tenantless in the request log**, at 18 of 18 in a stated workload. The gateway *knows* the
environment for every connection it meters. The seam it reports through cannot carry it as a
principal.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A connection opening and closing becomes two records (Priority: P1)

An operator asks how many sessions a tenant opened yesterday and how long they lasted. Today
the only answer is a monthly quota counter; there is no record that a particular connection
existed.

**Why this priority**: it is FR-ANL-01's last unbuilt arm and the chapter's reason to exist.

**Independent test**: open and close a known number of WebSocket connections, then count the
open and close records in the analytical store against them.

### User Story 2 - The gateway keeps serving when the broker is gone (Priority: P1)

Sockets connect, receive messages and close normally while the broker is unreachable.

**Why this priority**: constitution III, and the gateway is the service where it is most
expensive to get wrong — it holds long-lived connections, and a publisher that blocks a socket
handler blocks every client on that instance.

**Independent test**: stop the broker, open and close connections, and publish the
connection-level outcomes beside the latencies.

### User Story 3 - The quota path is unchanged (Priority: P1)

Connection-minutes still reach Postgres through `/internal/usage/connections`, and quota
refusals still happen synchronously.

**Why this priority**: constitution III keeps the two paths apart and FR-RTL-05's quota must
refuse a connection at the moment it is made. An analytical event cannot do that, and replacing
the meter with one would be moving a synchronous decision downstream of a lossy queue.

**Independent test**: the existing meter suite passes unchanged, and the quota counters move by
the same amounts as before.

### User Story 4 - ADR-07's record says what it now rests on (Priority: P2)

A reader of ADR-07 can tell why NATS is still not the fan-out fabric, given that the gateway now
holds a NATS client.

**Why this priority**: the ADR prices its refusal of NATS in gateway broker clients — "two …
and remove none" in the body, "how many client libraries the gateway holds" in v1.1 — and this
chapter makes both counts wrong. Leaving them is the silent divergence the governance clause
forbids.

**Independent test**: the record names the clause that stopped being true (**"remove none"**,
not merely the library count), states what the refusal now rests on, and says that the cost
side of it is now zero.

### Edge Cases

- A connection that opens and closes inside one metering tick.
- A connection open at the moment the gateway process stops — its close event has no author.
- A gateway instance killed with connections open: every one of them closes without a close
  record, so opens and closes do not balance.
- A connection that never authenticates. Not an open question: it never becomes a `Connection`,
  so it reaches neither anchor and produces no record. The socket exists; the connection does
  not.
- The broker unreachable at gateway boot. **The gateway does not create the stream** —
  `ensureAnalyticsStream` belongs to the api (`services/api/src/outbox/jetstream.publisher.ts`)
  — so there is nothing for the gateway to retry and it must serve sockets against a client
  that has never connected. Giving it an `ensureStream` of its own would also walk into 049-2:
  the containerised service asks for `replicas > 1` and is refused in non-clustered mode.
- 10,000 concurrent connections closing at once during a deploy, against the stream's
  `max_bytes`.

---

## Requirements *(mandatory)*

### Functional Requirements

**The producer**

- **FR-001**: The gateway shall emit an analytical event when a connection opens and when it
  closes (FR-ANL-01).
- **FR-002**: The record shall be assembled by naming every field individually, never by
  spreading a connection, session or socket object.
- **FR-003**: No credential, token, header or message content shall appear in the record
  (FR-ANL-11, constitution VI, NFR-SEC-06).
- **FR-004**: Publishing shall not block a socket handler, and its failure shall not close,
  refuse or delay a connection (constitution III, FR-ANL-03).
- **FR-004a**: The buffer of unpublished records shall be **bounded**, and reaching the bound
  shall drop records rather than grow. An unbounded buffer on a service holding 10,000 sockets
  satisfies FR-004 at the record level and violates it at the service level: the process dies
  and takes every connection with it.
- **FR-004b**: Drops shall be **counted and reported**, and the chapter shall state **which
  direction the loss runs** — dropping the oldest loses the earliest events, dropping the
  newest loses the ones describing the outage. `meter.ts` bounds its own retention at 4,000
  and argues the direction; this is the same problem and gets the same treatment rather than a
  new one.
- **FR-004c**: The buffer's flush interval shall be **named**, and the end-to-end budget shown:
  FR-ANL-04 allows **60 seconds** from the originating operation to the record being
  queryable, and the ingester's own batch bound spends up to 2 of them. An interval chosen for
  batching alone spends a budget nothing else in this chapter is watching.
- **FR-004d**: The end-to-end latency shall be **measured**, not derived — one connection
  closing to its row being readable — and published against FR-ANL-04's 60 seconds.
- **FR-004e**: A record whose publish **failed** shall be retained and retried on a later tick,
  within FR-004a's bound, rather than discarded at the flush. `meter.ts` drops a report that
  cannot be delivered — *"a lost report is repaired by the next one"* — and makes ONE exception:
  *"a connection that has CLOSED has no next report to repair a lost one, so its final total is
  retained until a report carrying it is accepted."* **Every connection event is in that
  exception.** An open is sent once and a close is sent once; neither has a next report
  carrying it again. So the meter's exception is this producer's rule, and that is also what
  makes FR-004a's bound bind for the meter's reason rather than for a new one.
- **FR-004f**: The flush's outcome shall be recorded **per record**, because publishing is one
  message per record and a flush of 500 has 500 outcomes rather than one. A flush that treats
  a partial failure as total loss discards records the broker accepted; one that treats it as
  total success discards records it did not.
- **FR-005a**: The open record's instant shall be the connection's own `openedAt` — the
  instant the meter uses — not the moment the record is assembled or published. Two instants
  for one open would make FR-009's reconciliation disagree for a reason that is neither of the
  two the chapter explains.
- **FR-005**: A close record shall carry the connection's duration, and the interval's two
  endpoints shall be stated rather than implied.
- **FR-006**: The chapter shall record that a connection with no resolvable environment
  **cannot reach either producer anchor**, and name the line that makes it so, rather than
  deciding a policy for it. `open()` — the only function that builds a `Connection` and the only
  caller of `registry.add` — takes a non-optional `Identity`, and its one call site reaches it
  only after every refusal has returned: 429 on the upgrade, 4001 on a bad token, 1011 when the
  api cannot answer, 4003 on a ban, 4008 on quota. An unauthenticated **socket** exists — three
  of those complete the handshake in order to close it — but it never becomes a connection.
  **4.4's `_none` arm is therefore not needed rather than not inherited.** Two earlier drafts of
  this clause mandated a policy: the first 4.4's, the second a decision of the chapter's own.

**The existing path**

- **FR-007**: `/internal/usage/connections` and the Postgres quota counters shall be unchanged
  in shape, cadence and meaning.
- **FR-008**: The chapter shall state why both paths exist rather than implying the new one
  supersedes the old, and shall name what each is unable to do.
- **FR-009**: The two shall be reconcilable: the connection-minutes derivable from open and
  close records shall be comparable to what the meter reports, and any structural reason they
  cannot agree exactly shall be published as a number rather than asserted as small.

**The broker client**

- **FR-009a**: The reconciliation shall cover **only connections with both records present**.
  The meter reports minutes for connections that are still open — `reportOnce` walks the
  registry and includes them — and a connection that has not closed has no close record. Over
  an unscoped population the two sides differ by every open connection, which is a third cause
  in a comparison built to have two.
- **FR-009b**: Derived buckets shall be **split by period** the way the meter splits them. A
  socket open across a month boundary owes minutes to two periods and each is credited
  independently; a derivation that does not split the same way disagrees for a fourth reason.
- **FR-010**: The gateway shall hold exactly one broker client, created once and shared, with a
  lazy connection.
- **FR-011**: The dependency added to `services/gateway` shall be counted and named, because
  ADR-07's rejection of NATS rests on that count.

**The records**

- **FR-012**: Connection events shall reach the analytical store through the existing ingester
  rather than a second consumer, unless a measurement says otherwise.
- **FR-013**: The record type shall be distinguishable by the mechanism 4.4 established, and an
  ingester that does not yet write it shall leave it rather than terminate it.
- **FR-014**: A redelivered connection event shall not become a second row.
- **FR-015**: The effect of a third producer on the shared stream's byte budget shall be
  measured. 4.4 measured 320 bytes a request record and a crossover at 5.5 requests/second;
  connection events arrive at a different rate and the combined figure is what matters.

**The clauses**

- **FR-016**: ADR-07's record shall be corrected where this chapter falsifies it. The clause
  that stops being true is the body's **"would leave that service holding two broker clients
  and remove none"** — after this chapter the gateway holds two regardless, so NATS fan-out
  would add none and remove none, and the cost side of the refusal is zero. "Redis is mandatory
  regardless (ADR-10)" is **not** a reason this chapter restores: the body has carried it since
  the decision was accepted, and an earlier draft of this clause said otherwise.
- **FR-016a**: The form of that correction shall be **chosen and stated**, not defaulted.
  Constitution VII says *"ADRs are immutable once accepted; superseding requires a new ADR"*,
  and ADR-07 carries both forms already — two in-place amendments (2026-08-04, 2026-09-03) and
  two extending records, **ADR-20** and **ADR-22**. VII's own closing line — *"disagreement
  attacks the driver, not the choice"* — bears on it, because what changes here is a driver's
  arithmetic rather than the choice.
- **FR-017**: Where a measurement in this chapter falsifies a published document, that document
  shall be amended in this feature.

**The chapter**

- **FR-018**: The chapter shall not re-derive the fire-and-forget argument, the subject grammar,
  or the tenantless rule — all three are 3.20's, 4.3's and 4.4's.
- **FR-019**: Prose shall stay inside the 2,000–4,000 word bound measured outside code fences,
  or split.
- **FR-020**: `pnpm check:fences` shall be reported as a delta against an opening measured in
  this feature, broken down by kind and locale — **and the chapter shall expect to owe hunks**,
  because 4.4 discovered at its close that editing a fenced file costs the chain six problems
  until the diff is published.

### Key Entities

- **Connection open event** — connection id, environment, the instant it opened, and how the
  socket was authenticated. No credential.
- **Connection close event** — the same identity, the instant it closed, the duration, and why
  it closed.
- **The meter's report** — unchanged: connection id, environment, period, minutes.
- **The gateway's publisher** — one client, lazily connected, shared.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A known number of connections opened and closed produces the same number of open
  and close records, published side by side against a non-zero floor.
- **SC-002**: With the broker stopped, connections open, carry messages and close normally; the
  per-connection outcomes are published beside the latencies, because a connection that is fast
  and refused satisfies a timing assertion.
- **SC-003**: The existing meter suite passes unchanged, and the quota counters move by the same
  amounts as before the chapter.
- **SC-004**: Connection-minutes derived from the records and connection-minutes from the meter
  are compared over one window, with the difference published and explained.
- **SC-005**: The gateway's dependency count is published before and after.
- **SC-006**: The combined byte rate of all three producers on the shared stream is measured,
  and the crossover restated.
- **SC-007**: A redelivery leaves the store's counts unchanged, published as a before-and-after
  pair with the physical count beside the collapsed one.
- **SC-008**: The tenancy branch has automated tests and its measured branch coverage is
  published beside constitution VI's 100% requirement.
- **SC-009**: ADR-07's amendment names the spent argument and the surviving one.
- **SC-010**: `check:fences` reported as a delta against an opening measured in this feature,
  broken down by kind and locale.
- **SC-011**: Prose measured outside code fences against the 2,000–4,000 bound, published
  whether or not it forced a split.

---

## Assumptions

- **The gateway keeps Redis.** This chapter adds a broker client; it does not move presence,
  the subscription fabric, or anything else off Redis. ADR-07's v1.1 amendment says a NATS-only
  proposal that also moves presence is "a larger decision than this ADR", and it is not this
  chapter's.
- **The quota path is not replaced.** Two counters of one quantity is the right answer and the
  reconciler is the price — `docs/12` §4 says so, and movement IV is where that is said out
  loud.
- **The ingester takes a third record type without a second consumer**, on the routing 4.3 and
  4.4 built. FR-012 says "unless a measurement says otherwise" because 4.4's R12 was settled
  with a number and this one should be too.
- **Connection events are lower volume than request events.** One pair per connection against
  one per request. Assumed, not measured, and FR-015 measures it.
- **This chapter adds no Vietnamese page, and the vi chain will still move.** An earlier draft
  said *"`app/(vi)/part-4/` is still empty, so … the vi fences in the opening total are not this
  chapter's to move."* **That path does not exist.** The Vietnamese tree is
  `app/(vi)/vi/part-N/`, so the check could only ever come back empty, and
  `app/(vi)/vi/part-4/` holds three chapters. Its 4.3 publishes
  `services/ingester/src/shape.ts` and `services/ingester/src/clickhouse.ts` as **whole
  bodies** — both files this chapter edits — and the gate reports part-4 contributing **0**
  problems today in either locale, so those bodies match the tree right now. Editing the files
  breaks them, a whole body cannot take a hunk, and there is no vi 4.5 to write one. The vi
  delta is this chapter's to move by up to two, and the cost is a gaps entry rather than a
  fence.
- **Constitution VII applies.** A broker client in the gateway is the same client three other
  services already hold.

## Dependencies

- Chapter 4.4's `route()`, the `_none` tenantless arm, and `api_requests` (`part4-ch4`).
- Chapter 4.3's ingester and its batching (`part4-ch3`).
- Chapter 3.24's `meter.ts` and `/internal/usage/connections`, which this chapter leaves alone.
- `ADR-07` and its two existing amendments.

## Out of scope

The reconciliation job comparing the two counters (movement IV); FR-ANL-10's latency
percentiles; the customer-facing query surface; presence, subscriptions or anything else on
Redis; and any change to how a quota refusal is decided.
