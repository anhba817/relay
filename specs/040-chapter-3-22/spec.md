# Feature Specification: Chapter 3.22 — the five-connection cap

**Feature Branch**: `040-chapter-3-22`

**Created**: 2026-09-01

**Status**: Draft

**Input**: User description: "chapter 3.22"

## What this chapter is, after the premises were checked

The hand-off from chapter 3.21 says this chapter's first job is a decision: *"the
SRS describes `conn:{env}:{user}` as a Redis set with one TTL, and a TTL is per key
rather than per member. What that chapter must decide is how a per-member expiry is
expressed."* **That decision was already made and published**, and the real first
job is a different one the hand-off does not name. Both were checked by command
before a requirement was written.

**THE STRUCTURE IS NOT OPEN — IT IS PRESCRIBED IN THE SAME ROW THAT RECORDS THE
DEFECT.** `docs/05-sad.md:574` reads: *"Not built, and this shape does not work: a
Redis TTL is per key, not per set member... **A sorted set scored by heartbeat
time, pruned with `ZREMRANGEBYSCORE` on read, is the correct version.**"* Chapter
3.20 wrote the diagnosis and the remedy together. So this chapter does not choose a
structure; it either implements that one or argues in writing against a published
decision. **A ForwardRef that assigns a decision already taken sends the next
chapter to re-derive an answer it could have read** — the same class as chapter
3.20's ForwardRef, one turn on.

**THE SAD SAYS TWO DIFFERENT THINGS ABOUT ONE KEY, AND ONE OF THEM IS PRESENT
TENSE.** The architecture overview at `docs/05-sad.md:167` says the gateway
*"registers the connection in Redis (`conn:{env}:{user}` → instance ID,
TTL-refreshed)"* — stated as something the service does, with the value a **single
instance ID**. The key table 407 lines later says **set of instance IDs** and
**"Not built"**. Two shapes and two tenses for one key in one published document.
`grep` finds `conn:` in exactly one place in the platform: a comment at
`services/gateway/src/presence.ts:351` explaining that presence does **not** need
it. Nothing registers anything.

**THE REAL FIRST DECISION IS WHERE THE REFUSAL HAPPENS, AND NOTHING HAS NAMED IT.**
The gateway already refuses connections. `refuseUpgrade` at
`services/gateway/src/session.ts:158` — chapter 3.8 — writes an HTTP response onto
the raw upgrade socket by hand: `429`, `code: "rate_limited"`, `Retry-After`, and
the three `X-RateLimit-*` headers, then destroys the socket. **No WebSocket ever
exists.** So a sixth connection can be refused there, or it can be allowed to open
and then closed with a close code, and those are different products: one gives the
client an HTTP body it can read with no protocol negotiated, the other gives it a
close code and a frame.

**AND THE VOCABULARY DOES NOT TRANSFER.** `packages/protocol/src/codes.ts` states
the test twice in its own words — *"a client that cannot tell them apart retries the
wrong one for ever"* — and chapter 3.15 applied it to add a fifth close code rather
than reuse `4001`. `Retry-After` on a cap refusal is false: waiting never helps,
and closing another connection helps immediately. Whether that means a sixth close
code, a distinct error code on the existing 429 path, or something else is this
chapter's argument to make. It is a decision, not a lookup.

**TWO LIMITS, TWO SUBJECTS, TWO REMEDIES — AND ONE OF THEM IS BUILT.** FR-RTL-01
governs *"per-tenant rate limits on... connection establishment"*: a **rate**,
per **environment**, already shipped as `operation: "connect" | "send"` in
`services/gateway/src/limits.ts` against `rl:{env}:connect:{window}` with a default
of 3,000 a minute. FR-RTM-09 is a **ceiling on concurrency**, per **user**. A rate
limit asks how fast; a cap asks how many at once. Chapter 3.19 paid for conflating
three 30-second numbers that were three quantities; these are two.

**THE NUMBER FIVE IS ALREADY LOAD-BEARING AND ENFORCED NOWHERE.**
`services/api/src/limits/policy.ts:36` derives its shipped `connect: 3_000` from
*"NFR-SCL-01's ten thousand connections per gateway instance, divided by
FR-RTM-09's five per user"*. A constant in production rests on a cap nothing
counts. `services/gateway/src/presence.itest.ts:728` says so and then exploits it:
*"FR-RTM-09's five is enforced NOWHERE — `policy.ts:13` mentions it in a comment
and nothing counts"*, immediately before a test that opens five connections for one
user because nothing stops it. **When this chapter enforces the cap, that
derivation stops being an estimate and becomes a dependency**, and any number other
than five changes the meaning of a shipped limit without touching its value.

**THE PER-INSTANCE HALF IS ALREADY BUILT AND IT IS THE EASY HALF.**
`registry.connectionsFor(user)` (chapter 3.20) filters a local map, so counting a
user's connections **on one instance** is free. NFR-SCL-01 puts ten thousand
connections on an instance, which means a user's five can sit on five instances,
and the cross-instance count is the entire problem. A cap enforced per instance is
a cap of five times the instance count.

**AND THE EXISTING LIMITER FAILS OPEN, WHICH A CAP CANNOT SIMPLY COPY.**
`services/gateway/src/limits.ts:35` says it plainly: *"limits are tenant limits, so
they fail open like the api's"*. For a rate limiter, failing open lets a burst
through and the next window recovers. For a concurrency cap there is no next
window: while the registry is unreachable, failing open means **the cap does not
exist**, and failing closed means **nobody connects at all**. Chapter 3.21 recorded
the asymmetry that makes this visible — *a lost typing frame converges on the
truth; a lost revocation converges on a lie* — and a cap is the case where
**neither** direction self-corrects. This chapter owes the argument, not a copied
default.

**THE CAP IS PER USER PER ENVIRONMENT, AND THAT IS THIS CHAPTER'S DECISION RATHER
THAN THE CLAUSE'S.** FR-RTM-09 reads *"A user shall be permitted up to 5 concurrent
connections"* and says nothing about environments. The first draft of this section
called the question settled and cited `conn:{env}:{user}` — **a key `docs/05-sad.md`
says is not built**, so citing it is citing a shape this chapter is choosing.

The reason to choose per-environment is not the key: **a user identifier is
environment-scoped in this platform, so a global cap would let two different people
who happen to share an external id compete for one allowance.** That is a
correctness argument. It is recorded here as a decision with that reason, and
FR-012 tests it.

## Clarifications

### Session 2026-09-01

**Q1 — FR-RTM-09 permits five and is silent on the sixth. What happens to it?**
**Refuse the newest.** The sixth attempt is refused and the five already open are
untouched: they keep their subscriptions and their cursors, and none is closed as a
side effect of somebody opening a tab. Eviction was considered and rejected on one
ground that is not a preference: **a client that reconnects on close turns eviction
into a loop.** Evict the oldest, the evicted client reconnects, it evicts the
next-oldest, and two devices trade the same slot indefinitely — the same shape as
`codes.ts`'s standing argument that a client which cannot tell two refusals apart
"retries the wrong one for ever", one level up. Refusing the newest makes the client
that just acted the one that learns, and it is the seam the gateway already refuses
at.

The cost is real and stated: a crashed tab holds a slot until the bound
expires, and the person sees "too many connections" for a connection they no longer
have. That is what FR-007's bound is for, and it is why the interval is a number
this chapter argues rather than inherits.

**Q2 — The shipped rate limiter fails open. What does the cap do when the registry
is unreachable?** **Fail open — accept the connection, and log it.** The cap is a
P2 abuse control; real-time delivery is P1. Failing closed turns a Redis outage
into a total connect outage for every user in every environment, including every
reconnect after a deploy, which is a P2 control taking down a P1 path.

Two things follow and both are requirements below. **The cap silently not existing
is the one failure mode nobody can see from the outside**, so it is logged on every
occurrence rather than sampled — the same reasoning as chapter 3.18's finding that a
fan-out publish which swallows its errors makes the log line the only thing carrying
the requirement. And falling back to the per-instance count was rejected: it is a
cap of five times the instance count wearing the label "five", and a wrong number
that looks right is worse than a stated absence — this project's own recorded rule
about a 78%-complete port registry being worse than none.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A person's sixth connection is refused while five keep working (Priority: P1)

A developer's user opens the app on a laptop, a phone, a tablet and two browser
tabs. All five receive messages. A sixth tab is opened and is refused, with a
reason the client can act on, and **the five that were already working are
undisturbed** — no frame is dropped, no subscription is lost, and none of the five
is closed as a side effect of refusing the sixth.

**Why this priority**: It is the clause. FR-RTM-09's first half is the permission
("up to 5") and its enforcement is the whole feature; everything else in this
chapter exists to make the count correct.

**Independent Test**: Open five connections for one user, assert all five receive a
message published to a shared channel, open a sixth, assert it is refused with the
documented reason, then assert the original five each still receive a subsequent
message. Fully testable against one gateway with no api spawn.

**Acceptance Scenarios**:

1. **Given** a user holding four connections, **When** a fifth is opened, **Then**
   it is accepted and receives events.
2. **Given** a user holding five connections, **When** a sixth is opened, **Then**
   it is refused with a reason distinguishable from an authentication failure, from
   a tenant rate limit, and from a quota exhaustion.
3. **Given** a user holding five connections, **When** a sixth is refused, **Then**
   all five remain open and each receives the next event published to a channel it
   subscribes to.
4. **Given** a user holding five connections, **When** one of the five closes,
   **Then** a new connection is accepted without waiting for any window to reset.

### User Story 2 - The count survives the gateway it was counted on (Priority: P1)

A user's five connections are spread across gateway instances behind a load
balancer. The cap holds across all of them: the sixth is refused wherever it
lands. When an instance is lost — a crash, a deploy, a network partition — the
connections it held stop counting against the user within the stated bound, without
any instance being asked to clean up after another.

**Why this priority**: A cap that only counts locally is not the specified cap, and
this is the half the SAD calls "not built". It is also the half where the published
shape was wrong, which is why it is P1 rather than a refinement of Story 1.

**Independent Test**: Boot two gateways in process against one registry, put three
connections on one and two on the other, assert the sixth is refused on both, then
kill one instance without letting it close its sockets cleanly and assert that a
new connection is accepted after the bound and not before.

**Acceptance Scenarios**:

1. **Given** three connections on instance A and two on instance B, **When** a
   sixth is opened on either instance, **Then** it is refused.
2. **Given** five connections held by an instance that dies without closing them,
   **When** the bound has passed, **Then** a new connection is accepted.
3. **Given** five connections held by an instance that dies without closing them,
   **When** the bound has **not** passed, **Then** a new connection is
   still refused — the count does not clear early.
4. **Given** a connection that is open and healthy, **When** more than the bound
   passes, **Then** it still counts — a live connection is never pruned.

### User Story 3 - Every one of the five is a first-class recipient (Priority: P2)

FR-RTM-09's second clause: *"each shall receive all events independently."* A user
reading on a phone and a laptop sees each message on both, each membership change on
both, each presence change and each typing indicator on both — and one connection
falling behind or dropping does not cost the others anything.

**Why this priority**: The clause is half of FR-RTM-09 and cannot be left
unverified, but it is a claim about code that already exists rather than code this
chapter writes: delivery walks connections, not users. It is P2 because its likely
outcome is a test that names an existing guarantee, and a P1 label would overstate
the work.

**Independent Test**: With two connections of one user subscribed to one channel,
publish one message and assert both receive it exactly once; then close one
uncleanly and assert the other still receives the next.

**Acceptance Scenarios**:

1. **Given** two connections of one user in a channel, **When** a message is
   published, **Then** both receive it, and each receives it once.
2. **Given** two connections of one user, **When** one is closed, **Then** the other
   receives the next event.
3. **Given** two connections of one user, **When** an event is delivered, **Then**
   neither connection's delivery depends on the other's success.

### Edge Cases

- A sixth connection arrives while a fifth is mid-handshake — two arrivals racing
  for the last slot, on two instances. Exactly one is accepted.
- A connection's renewal is refused because a Redis outage outlasted the bound and
  nothing else took its place. **This is the common case after any brief outage**, and
  the connection must end up still working — a design that closes it here punishes a
  user who is under the limit for the registry's downtime.
- A connection's renewal is refused because another connection took its place while
  the user was at the limit. The cap is genuinely exceeded and this connection is the
  one that must go, because the alternative is six open connections against a count
  of five (FR-011b).
- A connection is refused and the client immediately retries in a loop. The refusal
  must not itself consume the tenant's connection-rate budget in a way that turns
  one user's misbehaviour into a tenant-wide outage, and must not be free either.
- The registry is unreachable at the moment a connection arrives. The connection is
  accepted and the fact is logged (FR-016, FR-016a). The case worth testing is not
  the acceptance but the log line, because it is the only externally visible
  evidence that the cap stopped existing.
- A user closes all five connections. Nothing is left behind that would refuse
  their next connection, and nothing is left behind at all after the bound.
- The same connection is counted twice because a heartbeat wrote a second member
  for it. A connection has one identity in the registry for its whole life.
- A user's connections span two environments. Five in each; they never share a
  count.
- An instance is deployed over. Its connections must stop counting as it goes down
  rather than at the end of the bound, or every deploy refuses that user's next
  connection for a full bound. **The first draft of this bullet named close code
  4009 as the mechanism and no such path exists** — `session.test.ts:982` asserts
  the gateway never sends 4009 — so FR-011a states the obligation and leaves the
  mechanism to the plan.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST refuse a user's connection attempt when that user
  already holds the maximum permitted number of concurrent connections in that
  environment.
- **FR-002**: The maximum MUST be five, and it MUST be stated in exactly one place,
  so that any other published figure derived from it cannot drift away from it
  silently.
- **FR-003**: The refusal MUST be distinguishable by a client from an
  authentication failure, from a tenant rate limit, and from a quota exhaustion —
  distinguishable meaning a client acting on the refusal alone chooses the right
  remedy.
- **FR-004**: The refusal MUST NOT instruct the client to retry after an interval,
  because no interval makes a cap refusal succeed.
- **FR-005**: Refusing a connection MUST NOT close, disturb, or drop a frame from
  any connection the user already holds.
- **FR-006**: The count MUST include a user's connections on every gateway
  instance, not only the instance receiving the attempt.
- **FR-007**: A connection MUST stop counting against its user within a stated
  **bound** after the instance holding it stops renewing, without any other instance
  performing a cleanup action addressed to it.
- **FR-008**: A connection that is open and renewing MUST NOT stop counting,
  however long it stays open.
- **FR-009**: The **bound** and the **heartbeat interval** MUST be two distinct
  quantities, with the heartbeat interval strictly smaller by a stated margin, so
  that a single missed heartbeat does not release a place.
- **FR-010**: A connection closing cleanly MUST stop counting immediately rather
  than at the end of the bound.
- **FR-011**: A connection MUST occupy exactly one place in the registry for its
  lifetime, so that renewal cannot inflate a user's count. **A renewal MUST NOT be
  able to take a place another connection holds**, however long this connection was
  unable to renew.
- **FR-011a**: A service instance shutting down MUST release the places its
  connections hold, rather than leaving them to the bound. NFR-REL-03 permits a
  deployment no more than a single client reconnection cycle, and a bound's worth of
  refusals after every deploy is more than one.
- **FR-011b**: A connection whose renewal is refused MUST NOT continue as though it
  still held a place. It MUST try once to claim a place again; if it obtains one it
  continues; if every place is held by another connection it MUST be closed and told
  the same thing a refused sixth connection is told; and if the registry cannot be
  reached FR-016 applies and the connection is kept.
- **FR-012**: Counts MUST be independent per environment for the same user
  identifier.
- **FR-013**: When two attempts race for the last remaining slot, at most one MUST
  be accepted.
- **FR-014**: Every event a user's channel produces MUST be delivered to each of
  that user's connections independently, and one connection's delivery failure MUST
  NOT prevent another's.
- **FR-015**: The system MUST log a refusal with the user, the environment and the
  observed count, and MUST NOT log the credential presented.
- **FR-016**: When the connection registry is unreachable, the system MUST accept
  the connection rather than refuse it, leaving the cap unenforced for the duration.
- **FR-016a**: Every connection accepted with the cap unenforced MUST be logged, on
  every occurrence, in a form that distinguishes "the cap was not enforced" from
  "the cap was enforced and the user was under it".
- **FR-016b**: The system MUST NOT substitute a per-instance count for the
  cross-instance count when the registry is unreachable.
- **FR-017**: The published description of the connection registry MUST match what
  the system does, in both places `docs/05-sad.md` describes it, including its
  value shape and whether it exists.

### Key Entities

- **Connection registry** — the record of which connections a user currently holds
  in an environment, readable by any gateway instance, from which a count is
  derived. Its members expire independently of one another; its shape is prescribed
  by `docs/05-sad.md:574`.
- **Connection identity** — the one value that stands for a connection in the
  registry for its whole life, distinct from the instance that holds it, so that a
  repeated report updates rather than adds.
- **Heartbeat interval** — how often a live connection renews its place.
- **Bound** — how long after the last successful renewal a connection's place stops
  counting. Strictly greater than the heartbeat interval.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can hold five simultaneous connections and every one receives
  every event for the channels it subscribes to.
- **SC-002**: A sixth simultaneous connection is refused, and the five already open
  continue to receive events with no gap.
- **SC-003**: A user whose sixth connection is refused can free a slot by closing
  any one of the five and connect immediately, with no waiting period.
- **SC-004**: The cap holds however a user's connections are distributed across the
  servers answering them — a user cannot gain a sixth connection by reaching a
  different server.
- **SC-005**: When an instance is lost without closing its connections, the slots
  it held become available within the bound and not before it.
- **SC-006**: A connection held open for at least three consecutive bounds never
  loses its place.
- **SC-007**: A client can tell a cap refusal apart from an expired token, a tenant
  rate limit and an exhausted quota, using only what the refusal carries.
- **SC-008**: A refusal is recorded with enough detail to answer "why was I
  refused" from server-side logs alone, and carries no credential.
- **SC-009**: No published description of the connection registry contradicts
  another or contradicts the code.
- **SC-010**: The integration lane's full-run mean stays inside its 240-second
  budget.
- **SC-011**: With the registry unreachable, a user can still connect, and each
  such connection leaves a log line saying the cap was not enforced.
- **SC-012**: No connection is ever closed as a consequence of another connection
  being opened.
- **SC-013**: After a deployment, a user whose connections were on the replaced
  instance can reconnect immediately rather than waiting out the bound.
- **SC-014**: A connection that loses its place while the user is under the limit
  keeps working; one that loses it while the limit is full is closed rather than left
  serving uncounted.

## Assumptions

- **The structure is this chapter's, and it contradicts a published row.** This
  assumption was written before research and said the opposite: that the sorted set
  at `docs/05-sad.md:574` was taken as decided, with a clause allowing the chapter to
  record a contradiction if implementation forced one. **The contradiction came from
  design rather than implementation.** A sorted set cannot do check-and-insert in one
  command, its atomicity needs Lua, and Constitution VII requires a superseding ADR
  with profiling evidence for a second language that this lane cannot produce. So the
  structure is five slot keys, ADR-23 states the drivers and the reversal condition,
  and FR-017 covers the SAD amendment. **The escape clause was used, which makes the
  old heading false rather than the old paragraph wrong.**
- **The heartbeat is a new timer, and deliberately not the ping.** The old heading
  said it already existed, which its own last sentence contradicts.
  `PING_INTERVAL_MS` is 30,000 in
  `services/gateway/src/session.ts:48`, and chapter 3.19 established that a TTL
  equal to its own refresh interval expires a live user — presence uses 30,000 with
  a 10,000 refresh, three per window. The reporting and bounds here are
  derived the same way, and neither is assumed equal to `PING_INTERVAL_MS` merely
  because the number is available.
- **The per-instance count is not the cap.** `registry.connectionsFor(user)` is
  used where a local answer is sufficient and is never treated as the count.
- **FR-RTM-09's second clause is a claim about existing code.** Delivery walks
  connections rather than users, so Story 3 is expected to add tests rather than
  behaviour. If a test finds otherwise, that is a defect this chapter fixes and
  records.
- **`policy.ts`'s derivation becomes a dependency.** `connect: 3_000` rests on five
  per user; the chapter checks that arithmetic against the constant it ships rather
  than leaving two numbers to drift.
- **No api spawn is needed.** As in chapter 3.21, gateways can be booted in process
  with a stubbed api client, so the lane's spawn count does not rise.
- **The port map is fixed although this chapter takes no range.** The old heading
  made it conditional on taking one. This chapter takes none — its fixture boots on
  `server.listen(0)` — so the rule chapter 3.21's fourth gaps item states ("the next
  chapter that takes a range owns it") does not oblige anything here. **It is fixed
  regardless, because this chapter is the one holding the measurement**: the map
  lists seven ranges for nine files, and one unregistered range strictly contains a
  registered one. Two claims in that gaps item turned out wrong when re-run, so the
  values come from the allocation lines rather than from the item.

## Out of scope

- Raising, lowering or making the cap configurable per environment or per plan.
  FR-RTM-09 states one number.
- Evicting an existing connection to admit a new one. Decided against in Q1, and
  out of scope for this chapter rather than deferred: admitting it later would
  change FR-005 from a guarantee into a default.
- NFR-SCL-01's ten thousand connections per instance, which is verified by analysis
  and remains undischarged per the SRS's Appendix C.
- FR-RTL-05's connection-minutes quota, which counts time rather than concurrency.
- The connection-rate limit itself (FR-RTL-01), already shipped.
