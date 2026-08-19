# Feature Specification: Tutorial Chapter 3.8 — "Limits you can see coming"

**Feature Branch**: `029-chapter-3-8`

**Created**: 2026-08-19

**Status**: Draft

**Input**: User description: "Start chapter 3.8"

The platform has had the vocabulary for limits since chapter 1.3 and has never
enforced one. `ERROR_CODES.rate_limited` reads *"too many frames; slow down and
retry"* and nothing emits it. `CLOSE_CODES[4008]` reads *"quota exhausted"* and
nothing closes with it. Twenty-two chapters have shipped past two constants that
describe a mechanism nobody built.

This chapter builds it, for the half of FR-RTL that does not need a metering
pipeline: per-environment fixed-window counters on REST requests, message sends
and connection establishment, with the three standard headers on **every** response
rather than only on the rejection.

**The chapter's argument is what happens when the limiter breaks.** Rate limits
live in Redis, and the SAD's §6.3 is unambiguous that *"nothing in Redis is a
source of truth"* — total Redis loss means clients reconnect and resume, with no
data lost. So when Redis is gone the tenant limiter must let traffic through: a
cache outage is not a reason to reject a paying customer's messages. The same
sentence, applied to the limiter that throttles failed logins, gives the opposite
answer — failing open there opens a brute-force window on the way past. One
mechanism, two failure directions, and the difference is what the limit is
protecting.

**It also closes a debt.** Chapter 3.6 built automatic endpoint disablement and
wrote a `webhook_disable_notifications` row for every disablement with
`delivered_at` null, above a comment reading *"NULL THROUGHOUT THIS CHAPTER. Set
by whatever chapter builds a transport."* The plan named this chapter as the one
that builds it. FR-WHK-07 requires the organisation be notified by email, and it
has been half-delivered since 3.6 shipped.

The two halves share a subject rather than sitting in one chapter by accident.
Constitution V requires that *"usage is observable, not a surprise: every metered
unit is visible in the dashboard the moment it is counted."* A header on a
successful response and an email about an endpoint that has been switched off are
the same commitment: the platform tells you about a limit **before** the limit is
the reason something stopped working.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A developer can see the limit before hitting it (Priority: P1)

An integrating developer's backend sends messages through the REST API. Every
response — not only the ones that are refused — tells them how much of their
allowance is left and when it resets. When they do exceed it, the refusal says
how long to wait, and honouring that wait is enough to recover.

**Why this priority**: It is the whole mechanism, and FR-RTL-02's "headers shall
be present on successful responses, not only on `429`" is the part that
distinguishes a limiter a developer can build against from one that ambushes them.
Nothing else in this chapter matters if this is not working.

**Independent test**: Drive one environment past its send limit over the REST
API; confirm the headers count down across the successful responses, the refusal
is a `429` carrying `Retry-After`, and a request issued after that interval
succeeds.

**Acceptance scenarios**:

1. **Given** an environment inside its limit, **when** any REST request succeeds,
   **then** the response carries `X-RateLimit-Limit`, `X-RateLimit-Remaining` and
   `X-RateLimit-Reset`, and `Remaining` is one lower than the previous response's.
2. **Given** an environment that has consumed its allowance, **when** it issues
   another request, **then** the response is `429` with `Retry-After` and an error
   body carrying a machine-readable code, a message, a `docs_url` and the
   `request_id` (constitution V).
3. **Given** a `429` with `Retry-After: N`, **when** the client waits N seconds
   and retries, **then** the request succeeds.
4. **Given** a WebSocket connection sending frames above its limit, **when** a
   frame is refused, **then** the client receives an `error` frame carrying the
   `rate_limited` code that has existed unused since chapter 1.3, and the
   connection stays open.
5. **Given** an environment at its connection-establishment limit, **when**
   another handshake is attempted, **then** it is refused before the socket is
   accepted, and existing connections are unaffected.
6. **Given** two environments of the same application, **when** one is driven to
   its limit, **then** the other's allowance is untouched (FR-RTL-04).

---

### User Story 2 - A cache outage does not become an outage, or a security hole (Priority: P2)

The Redis instance holding the buckets is stopped mid-traffic. Customer requests
keep being served, because the store that was counting them was never the source
of truth for whether they are allowed. In the same outage, an attacker
password-spraying the auth endpoint does not get an unlimited window.

**Why this priority**: The failure direction is the chapter's central decision and
it is a correctness question, not an operational nicety. A limiter that fails
closed turns a Redis restart into a platform outage. A limiter that fails open
everywhere turns a Redis restart into a free brute-force window. Both are wrong,
and they are wrong in opposite directions for the same code.

**Independent test**: Stop Redis with traffic in flight. Confirm tenant requests
continue to be served and are still answered with headers that say something
truthful; confirm failed authentication attempts are still refused after the
threshold; confirm the degradation is visible in logs rather than silent.

**Acceptance scenarios**:

1. **Given** an environment under its limit, **when** the bucket store is
   unreachable, **then** the request is served rather than refused.
2. **Given** the bucket store is unreachable, **when** a response is returned,
   **then** a client can tell from it that counting is not happening, rather than
   reading a `Remaining` value that was never counted.
3. **Given** the bucket store is unreachable, **when** an IP submits failed
   authentication attempts past the threshold, **then** they are still refused —
   the limiter that protects a credential does not fail open.
4. **Given** the bucket store is unreachable, **when** any request is degraded,
   **then** the platform emits a log line naming the degradation, carrying no
   credential (NFR-SEC-06).
5. **Given** the bucket store returns, **when** the next request arrives, **then**
   counting resumes without an operator intervening.

---

### User Story 3 - An organisation is told its endpoint was switched off (Priority: P2)

An organisation's webhook endpoint has been failing for over an hour and chapter
3.6's sweep disabled it. An admin receives an email saying which endpoint, when,
what the last response was, and how to re-enable it. The notification rows that
have been accumulating since 3.6 shipped are sent too.

**Why this priority**: FR-WHK-07 is half-delivered and the plan says so in
writing. An automatic disablement nobody is told about is a silent outage a
customer discovers from their own users — which is the failure chapter 3.5 and 3.6
spent themselves avoiding.

**Independent test**: Drive an endpoint to automatic disablement, then confirm a
message arrives at a local mail service naming the endpoint and carrying no
signing secret, and that the notification row's `delivered_at` is set only after
the transport accepted it.

**Acceptance scenarios**:

1. **Given** an endpoint disabled by the sweep, **when** the transport runs,
   **then** an email is delivered to the organisation's admins and the row's
   `delivered_at` is set.
2. **Given** a notification whose send fails, **when** the transport runs again,
   **then** it is retried and `delivered_at` remains null in the meantime — the
   obligation is not lost.
3. **Given** a notification already delivered, **when** the transport runs again,
   **then** it is not sent a second time.
4. **Given** the rows chapter 3.6 accumulated before a transport existed, **when**
   the transport first runs, **then** they are sent.
5. **Given** any notification email, **when** its content is inspected, **then**
   it contains no signing secret, no API key and no customer credential of any
   kind (NFR-SEC-06).
6. **Given** the mail service is unreachable, **when** the transport runs,
   **then** no `delivered_at` is set and nothing else in the platform is affected
   — webhook dispatch, message delivery and the API stay up (constitution III's
   separation applied to a third path).

---

### User Story 4 - Part 3 absorbs another chapter, cheaply this time (Priority: P3)

Quotas move to 3.9 and the isolation gauntlet to 3.10. A reader following any
published chapter finds every cross-reference naming the chapter it means.

**Why this priority**: The bookkeeping is not the chapter's value, but getting it
wrong makes an earlier chapter lie. It is P3 because chapter 3.7 already paid for
the expensive half of this problem.

**Independent test**: After the renumbering, search the plan, the site registry,
every published page in both locales and the platform's source for chapter-number
references; confirm none names the wrong chapter and that no live source file
names a chapter that has not happened yet.

**Acceptance scenarios**:

1. **Given** the renumbering, **when** the plan and the site registry are
   compared, **then** both say quotas 3.9 and the gauntlet 3.10.
2. **Given** a published page in either locale naming a moved chapter in prose,
   **when** it is read, **then** the number is correct.
3. **Given** the platform's source, **when** it is searched for forward chapter
   references, **then** there are none — the count chapter 3.7 drove to zero stays
   at zero, and this renumbering costs no fence amendment as a result.

---

### Edge Cases

- **A bucket that has never been written.** A brand-new environment's first
  request must be allowed and must return headers showing a full allowance rather
  than an empty one.
- **Clock skew between instances.** Two api instances sharing a bucket must not
  disagree about the reset time by enough to make `Retry-After` wrong. The window
  is Redis's, not each process's.
- **A request that consumes more than one token.** A batch send is one request and
  more than one message; the spec must be explicit about which the limit counts.
- **The limit changed while a window was open.** Lowering an environment's limit
  must not produce a negative `Remaining` or a `Reset` in the past.
- **An organisation with no admin email on record.** A notification that cannot be
  addressed must not be silently marked delivered.
- **An admin who has been removed** between the disablement and the send. The row
  records the obligation as it stood (3.6 denormalised `organisation_id` for
  exactly this reason); the recipient list must be resolved at send time.
- **The same endpoint disabled, re-enabled, and disabled again.** Two rows, two
  emails, and neither suppresses the other.
- **A limiter applied to the internal seam.** Dispatcher-to-api and
  gateway-to-api calls must not be throttled as though they were customer traffic.

## Requirements *(mandatory)*

### Functional Requirements

#### Rate limiting

- **FR-001**: The platform MUST enforce per-environment rate limits on REST
  requests, message sends and connection establishment (FR-RTL-01).
- **FR-002**: Every response subject to a limit MUST carry
  `X-RateLimit-Limit`, `X-RateLimit-Remaining` and `X-RateLimit-Reset`, on
  successful responses as well as refusals (FR-RTL-02). Where a request is counted
  against more than one limit, the headers MUST describe the limit with the fewest
  remaining — the only one a client can schedule against — and `Reset` MUST be that
  same limit's (research R11).
- **FR-003**: A refused REST request MUST return `429` with a `Retry-After` header
  and an error body carrying `code`, `message`, `docs_url` and `request_id`
  (FR-RTL-03, constitution V).
- **FR-004**: A refused WebSocket frame MUST produce an `error` frame carrying the
  `rate_limited` code, and MUST NOT close the connection.
- **FR-005**: A refused connection establishment MUST be rejected before the
  socket is accepted, and MUST NOT affect connections already open.
- **FR-006**: Counters MUST be independent per environment, so that a development
  environment driven to its limit leaves the production environment of the same
  application unaffected (FR-RTL-04).
- **FR-007**: Limits MUST be configurable per environment, with a documented
  default that applies when nothing is configured.
- **FR-008**: The limit MUST count a unit named in the chapter's own prose, and a
  test MUST assert the count against that unit. Where one request carries more than
  one message, whichever of the two is counted, the test MUST distinguish it from
  the other — a limiter that counts requests and a limiter that counts messages
  behave identically on single-message traffic, so single-message traffic cannot
  verify either. With FR-036 in force the distinguishing case is concrete: ten
  messages in one request decrement the request limit by one and the send limit by
  ten.
- **FR-009**: Calls arriving over the internal service seam MUST NOT be subject to
  customer rate limits.
- **FR-036**: A message sent over the REST path MUST be counted against both the
  request limit and the send limit, and a refusal MUST name which of the two was
  reached. A limit a client can lift by moving the same traffic to the socket is not
  a limit; a refusal that does not say whether to batch or to slow down is not
  actionable (research R11).
- **FR-037**: The gateway MUST enforce the environment's configured connect and send
  limits without reading the database. It has no database client and MUST NOT gain
  one; the limits MUST reach it on the internal authentication response it already
  makes, and MUST be retained for the life of the connection. A limit changed while
  a socket is open MUST NOT be expected to apply until that socket reconnects, and
  the chapter MUST state this (research R12).
- **FR-038**: Every `error` frame MUST carry a `request_id`, minted by the gateway
  per answered frame, or the connection's own id where no frame was being answered.
  The field MUST NOT be optional on the frame schema (research R13).
- **FR-039**: A failed authentication arriving through the gateway MUST be counted
  against **the client's** source address, not the gateway's. The gateway MUST
  forward that address on the internal authentication call, and the api MUST count
  against it. Exemption from customer rate limits (FR-009) MUST NOT exempt a call
  from identifying whose failure it carried (research R14).

#### Failure behaviour

- **FR-010**: When the bucket store is unreachable, a tenant-scoped limiter MUST
  allow the request. Redis is not a source of truth (SAD §6.3), and a cache
  outage MUST NOT become a refusal of paid traffic.
- **FR-011**: When the bucket store is unreachable, the limiter protecting
  authentication MUST NOT allow unlimited attempts. Failing open on a credential
  limiter opens a brute-force window, which is a security regression rather than a
  degradation.
- **FR-012**: Failed authentication attempts MUST be rate limited per source IP
  address (FR-AUT-12). The threshold MUST be configuration with an enforcing
  default, so a suite that deliberately submits bad credentials can raise it
  explicitly rather than the default being chosen to suit the suite (research R15).
- **FR-013**: Degradation of the limiter MUST be observable in logs, and the log
  line MUST NOT carry a credential or a key (NFR-SEC-06).
- **FR-014**: While the limiter is degraded, a response MUST NOT carry an
  `X-RateLimit-Remaining` value that implies counting took place. A client MUST be
  able to distinguish "you have N left" from "we are not counting right now", and
  the chapter MUST state which of the two the platform sends.
- **FR-015**: Counting MUST resume without operator action once the store returns.

#### The notification transport

- **FR-016**: The platform MUST deliver an email to an organisation's admins when
  one of its endpoints is automatically disabled (FR-WHK-07).
- **FR-017**: `delivered_at` MUST be set only after the transport has accepted the
  message, and MUST NOT be set on failure.
- **FR-018**: A failed send MUST be retried and MUST NOT lose the obligation.
- **FR-019**: A notification MUST NOT be sent twice.
- **FR-020**: Notification rows written before a transport existed MUST be
  delivered rather than abandoned.
- **FR-021**: No notification MUST contain a signing secret, an API key, or any
  customer credential (NFR-SEC-06).
- **FR-022**: Recipients MUST be resolved at send time from the organisation the
  row records, not from the endpoint's current owner.
- **FR-023**: A notification that cannot be addressed MUST NOT be marked
  delivered, and the condition MUST be visible.
- **FR-024**: Failure of the mail path MUST NOT affect message delivery, API
  availability or webhook dispatch.
- **FR-025**: Local development MUST be able to receive and inspect these emails
  without an external account or outbound internet access.

#### The chapter

- **FR-026**: The chapter MUST state why the two limiters fail in opposite
  directions, and MUST NOT present the choice as a matter of taste.
- **FR-027**: The chapter MUST explain why headers on successful responses are a
  requirement rather than a courtesy.
- **FR-028**: The chapter MUST record that the vocabulary for this mechanism —
  `rate_limited` and close code 4008 — has existed unused since chapter 1.3, and
  what that says about declaring a contract before enforcing it.
- **FR-029**: The chapter MUST state which parts of FR-RTL it does not deliver and
  why, naming the metering dependency rather than leaving the gap silent.
- **FR-030**: Every transcript the chapter quotes MUST come from a real run.
- **FR-031**: Every file the chapter's prose asserts MUST be fenced, and
  `pnpm check:fences` MUST replay the chain onto the platform.
- **FR-032**: The chapter MUST be published in English and Vietnamese, with every
  fence byte-identical between locales.

#### The renumbering

- **FR-033**: Quotas MUST become 3.9 and the isolation gauntlet MUST become 3.10,
  in `docs/07-tutorial-plan.md` and the site registry.
- **FR-034**: Prose cross-references naming a moved chapter MUST be corrected in
  every locale.
- **FR-035**: No live source file under `services/*/src` or `scripts/` MUST name a
  chapter that has not happened yet. The count is zero as of chapter 3.7 and MUST
  stay zero.

### Key Entities

- **Bucket**: a per-environment, per-limited-operation counter with a window,
  held in the ephemeral store under the key shape the SAD already specifies
  (`rl:{env}:{bucket}`). Not a source of truth; survives nothing.
- **Limit policy**: the allowance and window for an environment and operation,
  durable, with a documented default.
- **Disable notification**: the row chapter 3.6 already writes — environment,
  organisation, endpoint, the run that triggered it, the last status, and
  `delivered_at`. This chapter sets the last field and adds nothing to the row.
- **Recipient**: an organisation admin, resolved at send time from the
  organisation the notification row names.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A client driven past its limit receives `429` with `Retry-After`,
  and a request issued after that interval succeeds — demonstrated end to end, not
  asserted from a unit test alone.
- **SC-002**: Every successful response to a limited operation carries all three
  headers, and `Remaining` decreases monotonically across a run inside one window.
  Where a request is counted against two limits, the headers describe the one with
  fewer remaining, demonstrated with a batch rather than with single-message
  traffic.
- **SC-003**: Two environments of one application are driven independently: one at
  its limit, the other unaffected.
- **SC-004**: With the bucket store stopped mid-run, customer traffic continues to
  be served and failed authentication is still refused past the threshold. Both
  halves demonstrated in the same outage.
- **SC-005**: An automatic disablement produces an inspectable email in local
  development, carrying no secret, with `delivered_at` set only after acceptance;
  and the rows accumulated since chapter 3.6 are drained.
- **SC-006**: Both lanes pass and coverage exits 0 with every ratchet intact, and
  any ratchet the chapter's own files can raise is raised.
- **SC-007**: Every claimed invariant fails when its mechanism is removed, verified
  by sabotage with files restored byte-identical — including one mutation that
  makes the auth limiter fail open, because that is the decision with no code of
  its own to point at.
- **SC-008**: The chapter is reachable in both locales and its figures render as
  laid-out SVG in a headless browser.
- **SC-009**: After the renumbering, a search across the plan, the registry, both
  locales' pages and the platform source finds no reference naming the wrong
  chapter, and no forward chapter reference in live source.
- **SC-010**: The chapter's prose is inside the 2,000–4,000 word bound, or the
  overrun is recorded with the reason — three of the last four Part 3 chapters
  have exceeded it and two were not noticed at the time.
- **SC-011**: The gateway enforces a configured (non-default) connect limit with no
  database client added to it, and ten failed handshakes from ten different client
  addresses are counted as ten addresses rather than as ten failures by the gateway.
- **SC-012**: Every pre-existing integration suite passes with the auth limiter
  enforcing, and the number of failed authentications the lane produces per minute is
  recorded — measured, not inferred from a count of assertions.

## Assumptions

- **Rate limits and quotas are two features, and this chapter is the first one.**
  FR-RTL reads as one family but splits cleanly on where the count lives. A rate
  limit is ephemeral, per-window, and may be lost — Redis is the right store and
  failing open is the right default. A quota is money: it must be durable, it must
  reconcile against Postgres, and the deep dive on ADR-06 is explicit that
  *"billing accuracy cannot rest on any pipeline's promises"*. Putting both in one
  chapter would teach one storage decision as though it covered both.
- **Quotas are deferred because their input does not exist yet.** FR-RTL-05 meters
  messages sent, unique active users and connection-minutes. That is FR-ANL-05,
  which arrives in Part 4 with the analytical store. Building per-tenant monthly
  counters now means building them in Postgres and then again in ClickHouse, or
  building them once in the wrong place. Deferred to 3.9 with the dependency
  named.
- **Part 3 gains a chapter for the third time.** 3.5's split created 3.6 and 3.7's
  insertion moved quotas once already. The discipline is the same, and it should
  cost less this time: chapter 3.7 removed every forward chapter reference from
  live source, so this renumbering touches prose, the plan and the registry but no
  fenced file. If that turns out to be false, it is a finding worth recording —
  the rule was adopted one chapter ago specifically to make this cheap.
- **The email transport is built here rather than deferred again.** It is needed by
  FR-WHK-07 now and by FR-RTL-07 later, and the notification rows have been
  accumulating with `delivered_at` null since 3.6. Deferring a second time would
  mean a third chapter explaining why the column is still null.
- **The transport is a fourth path, and it fails alone.** Constitution III forbids
  crossing the operational and analytical paths; the same reasoning applies to a
  notification path. A mail server being down must not affect message delivery,
  webhook dispatch or the API, which means the send does not happen on a request
  path and its failure is recorded rather than raised.
- **Local mail is a container, not an account.** Development must not require an
  outbound SMTP credential or internet access, which means a mail service in
  `compose.yaml` alongside Postgres, Redis, NATS and ClickHouse. This is the first
  new infrastructure since chapter 3.4 and it needs justification against
  constitution VII's "boring by design" — the justification is that the
  alternative is either an unverifiable transport or a real credential in a
  tutorial.
- **The default limits are chosen, not derived.** The SRS specifies no numbers for
  FR-RTL-01. Whatever this chapter picks is a decision to record with its
  reasoning, not a value to present as obvious, and it must be configurable
  because the right number is a business question.
- **FR-RTM-09's five-concurrent-connection cap is not in scope.** It reads like a
  limit but it needs the connection registry the SAD specifies at
  `conn:{env}:{user}`, which does not exist yet — the gateway currently uses Redis
  for fan-out and nothing else. Rate limiting connection *establishment*
  (FR-RTL-01) needs no registry and is in scope; capping *concurrent* connections
  is a different mechanism and belongs with presence.
- **This chapter is two mechanisms and that is a size risk.** 3.5 ran 4,952 prose
  words and 3.6 ran 5,273 against a 2,000–4,000 bound. A chapter carrying both a
  limiter and a mail transport could be the third overrun. The plan should decide
  early whether the transport is a section or a split, and the fence budget should
  be estimated before the prose is written rather than measured after.

## Out of Scope

- **FR-RTL-05, -06, -07 and -08** — monthly usage quotas, hard and soft spending
  caps, the 50/80/100% threshold emails, and quota-exhaustion degradation. All
  P3, all dependent on metering, all deferred to chapter 3.9.
- **FR-RTM-09** — the five-concurrent-connection cap, which needs a connection
  registry.
- **Presence** (FR-RTM-06), which shares that registry.
- **Shedding a handshake flood before the authentication lookup.** After FR-039 the
  api refuses past the threshold instead of never, but it still performs a lookup per
  bad handshake. Doing better needs a per-IP check inside the gateway with its own
  store and its own failure direction — a third limiter in a chapter already carrying
  two. Named in research R14 and left for the connection-registry work FR-RTM-09
  needs.
- **Any change to the analytical path.** Chapter 3.6's attempt records stay as
  they are; this chapter reads no analytics and writes none.
- **A dashboard view of remaining allowance.** Constitution V requires usage be
  visible in the dashboard; there is no dashboard yet, and the headers are the
  API-side half of that commitment.
- **Rate limiting by API key rather than by environment.** The SRS says per-tenant
  and the environment is the tenant boundary this platform enforces (constitution
  I). Per-key limits are a finer cut nobody has asked for.
- **A limiter that smooths instantaneous rate.** A fixed window allows up to
  twice the limit across a boundary and the chapter states the number rather than
  claiming otherwise. Sliding windows and leaky buckets buy that smoothing with an
  `X-RateLimit-Reset` that cannot be computed honestly (research R1).

## Dependencies

- **Chapter 3.6's disablement sweep and its notification rows**, unchanged in
  shape. This chapter sets `delivered_at` and adds no column.
- **Chapter 3.2's credential handling**, which is where failed authentication is
  counted, and whose error-code discipline the `429` body must match.
- **Chapter 3.1's environments**, which are the boundary the counters are keyed on.
- **Chapter 1.3's protocol codes** — `rate_limited` and close code 4008, declared
  there and enforced for the first time here.
- **Redis**, already in `compose.yaml` for fan-out, used here for the first time
  as something other than pub/sub.
- **A mail service in `compose.yaml`** — new infrastructure, justified above.
