# Feature Specification: Chapter 3.10 — Quotas and what they cost

**Feature Branch**: `031-chapter-3-10`

**Created**: 2026-08-21

**Status**: Draft

**Input**: User description: "Start chapter 3.10"

Chapter 3.10 of the Relay tutorial, covering FR-RTL-05 to FR-RTL-08: monthly
usage quotas, hard and soft caps, the threshold email, and what a tenant that has
run out is still allowed to do.

Chapter 3.8 built the per-minute limiter. This is the other half of the same
subject and the interesting half, because the two are different problems wearing
the same word. A rate limit is about *this second* and forgets; a quota is about
*this month* and must not. A limiter that loses its counter costs a tenant one
window of over-service. A quota that loses its counter costs the month.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The month is counted, and the count survives (Priority: P1)

Priya's application sends messages all month. Every send is counted against her
environment's monthly quota, and every distinct user who sends is counted against
her active-user quota. When the counter store is restarted, wiped, or was never
warm, the numbers do not change: the month's usage is read from the same records
the messages themselves are in.

**Why this priority**: everything else in the chapter is a decision made *about* a
number. If the number is wrong, the cap suspends the wrong tenant and the email
tells them something false. This story is also the whole reason a quota cannot be
built the way chapter 3.8 built the limiter.

**Independent Test**: send a known number of messages from a known number of
users, read the usage figures, restart the counter store, read them again, and
compare. Ships alone as observability with no enforcement attached.

**Acceptance Scenarios**:

1. **Given** an environment with no usage this month, **When** N messages are sent
   by M distinct users, **Then** the reported monthly usage is exactly N messages
   and M active users.
2. **Given** recorded usage, **When** the counter store is flushed entirely,
   **Then** the reported usage is unchanged.
3. **Given** an environment with usage in the previous calendar month, **When** the
   month boundary passes, **Then** the current-month figures start from zero and
   the previous month's remain readable.
4. **Given** two environments of the same application, **When** one sends and the
   other does not, **Then** the second reports zero.

---

### User Story 2 - Running out is predictable, and it does not take the tenant down (Priority: P2)

Priya's environment reaches its message quota mid-afternoon. New sends are
refused with an error that names what happened and what to do. Her users stay
connected. Her application can still read history, still receives webhooks for
messages already accepted, and still serves every read path it served an hour ago.
When the cap is raised or the month rolls over, sends resume with no intervention.

**Why this priority**: FR-RTL-08 is the requirement that decides whether a quota is
a business control or an outage. Refusing everything is easy and wrong.

**Independent Test**: set a cap below current usage, attempt a send, attempt a
history read, and hold an open connection across the boundary. One refusal, two
successes, and the connection intact.

**Acceptance Scenarios**:

1. **Given** usage at or above the hard cap, **When** a message send is attempted,
   **Then** it is refused with a distinct error code and a message naming the
   quota, and the refusal is distinguishable from chapter 3.8's rate-limit refusal.
2. **Given** usage at or above the hard cap, **When** message history is read,
   **Then** it succeeds.
3. **Given** an open connection and usage crossing the hard cap, **When** the cap is
   crossed, **Then** the connection stays open.
4. **Given** a suspended environment, **When** the cap is raised above current
   usage, **Then** the next send succeeds with no restart or manual step.
5. **Given** an environment with no cap configured, **When** usage grows without
   bound, **Then** nothing is refused.

---

### User Story 3 - Nobody is surprised (Priority: P3)

The organisation's admins are emailed when the environment crosses 50%, 80% and
100% of a configured quota. Each threshold produces one email per quota per month,
never a repeat, and crossing 100% produces an email whether the cap is hard or
soft. An organisation nobody can be emailed still crosses its thresholds and still
gets suspended.

**Why this priority**: it depends on both stories above — there is nothing to be
warned about until usage is counted and a cap exists — and chapter 3.9 already
built the transport it needs.

**Independent Test**: drive usage across each threshold and read what arrived at
the mail server, then drive it across again and confirm nothing new arrives.

**Acceptance Scenarios**:

1. **Given** a configured quota, **When** usage first reaches 50%, **Then** each
   admin with an address receives one email naming the environment, the percentage,
   and the figure it is a percentage of.
2. **Given** a threshold already notified this month, **When** usage crosses it
   again after dipping, **Then** no further email is sent for that threshold.
3. **Given** usage that jumps from 40% to 100% in one send, **Then** the thresholds
   crossed are all notified.
4. **Given** an organisation with no addressable admin, **When** a threshold is
   crossed, **Then** the crossing is recorded, the suspension still applies, and
   the failure to notify is logged rather than swallowed.
5. **Given** a new calendar month, **When** usage crosses 50% again, **Then** an
   email is sent — thresholds reset with the period.

---

### Edge Cases

- **A send that takes usage from below the cap to above it.** The message that
  crosses the line is accepted; the next one is refused. A quota is checked against
  usage already recorded, not against usage this request is about to create, and the
  alternative — reserving before writing — is a distributed transaction across the
  send path for the sake of one message.
- **Two sends crossing the cap at the same instant.** Both may be accepted. The
  overshoot is bounded by concurrency, not unbounded, and this is stated rather
  than defended against.
- **A cap of zero.** Refuses everything, and must stay expressible — an
  environment can be switched off deliberately. Zero and "no cap configured" cannot
  share a representation, which is the rule chapter 3.8's nullable limit columns
  already established.
- **A cap lowered below current usage.** Takes effect immediately: the environment
  is over its cap from that moment. No grace, and the 100% email fires if it has
  not already this month.
- **A quota configured mid-month.** Usage already accrued counts. The month is the
  period, not the configuration.
- **Usage read for a month with no rows.** Zero, not an error and not null.
- **The distinct-user count across a month boundary.** A user active in both months
  counts once in each.
- **The soft threshold and the hard cap set to the same value.** The soft
  threshold alerts and the hard cap suspends; both happen, and the order is defined.
- **A tenant at 100% whose webhooks are still firing** for messages accepted before
  the cap. Delivery continues — the send was accepted, and constitution II says an
  acknowledged message is not lost because a quota was later exceeded.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST record, per environment and per calendar month, the
  number of messages sent and the number of distinct users who sent them.
- **FR-002**: Monthly usage figures MUST be derivable without the per-minute counter
  store. Flushing that store MUST NOT change any reported figure.
- **FR-003**: The usage period MUST be the calendar month in UTC, and the previous
  month's figures MUST remain readable after the boundary passes.
- **FR-004**: Usage MUST be counted per environment, with development and
  production independent, as chapter 3.8 established for rate limits.
- **FR-005**: An environment MUST be able to carry a hard cap and a soft threshold
  for each metered dimension, each independently configurable and each absent by
  default.
- **FR-006**: A configured cap of zero MUST be distinguishable from no cap
  configured, and MUST refuse everything.
- **FR-007**: When usage is at or above a hard cap, message sends MUST be refused.
- **FR-008**: A quota refusal MUST carry an error code distinct from the rate-limit
  refusal, and a message naming the quota, the period, and the figure.
- **FR-009**: When usage is at or above a hard cap, message history reads MUST
  succeed.
- **FR-010**: When usage is at or above a hard cap, existing connections MUST stay
  open.
- **FR-011**: When usage is at or above a hard cap, webhook delivery for already
  accepted messages MUST continue.
- **FR-012**: A suspended environment MUST resume sending, with no restart or
  manual step, when the cap is raised above usage or the period rolls over.
- **FR-013**: A soft threshold MUST alert without refusing anything.
- **FR-014**: The system MUST email organisation admins when usage first reaches
  50%, 80% and 100% of a configured quota.
- **FR-015**: Each threshold MUST produce at most one email per quota per
  environment per period.
- **FR-016**: A single usage increase that crosses more than one threshold MUST
  notify each threshold crossed.
- **FR-017**: Threshold notification state MUST reset with the period.
- **FR-018**: An organisation with no addressable admin MUST still have its
  crossings recorded and its cap enforced, and the failure to notify MUST be
  logged rather than swallowed.
- **FR-019**: Sending a threshold email MUST NOT be able to fail a message send.
- **FR-020**: Reading current usage MUST NOT add a query to the message send path
  that scans the message table.
- **FR-021**: Any test that drives a global quota sweep MUST be named in the
  test harness's exemption list with the tables it needs, and in the matching lint
  ignores list. Feature 030's guard refuses a cross-environment mutation from a
  file on neither.
- **FR-022**: The chapter MUST state what a "cap" is denominated in, and MUST NOT
  introduce a price, a currency or a unit cost.

### Key Entities

- **Usage record**: what an environment consumed in a period. Identified by
  environment and period; carries a message count and a distinct-user count.
  Additive and never revised downward except by the period changing.
- **Quota policy**: what an environment is allowed in a period. Per environment,
  per dimension, with a hard cap and a soft threshold, each optionally absent.
  Absent means unlimited; zero means none.
- **Threshold crossing**: the record that a given threshold, for a given quota, in
  a given period, has been notified. Exists to make the email at-most-once.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Reported monthly usage is byte-identical before and after the
  per-minute counter store is flushed.
- **SC-002**: With usage above a hard cap, sends are refused and history reads
  succeed — measured as one refused request and one successful request in the same
  test, against the same environment, within the same second.
- **SC-003**: A connection open before a cap is crossed is still open, and still
  receiving, sixty seconds after.
- **SC-004**: Crossing 50%, 80% and 100% produces exactly three emails per quota
  per period, verified by reading what the mail server received rather than by
  asserting on a send call.
- **SC-005**: Re-crossing an already notified threshold produces zero further
  emails.
- **SC-006**: The message send path executes no additional table scan when quota
  enforcement is active, measured against chapter 3.8's recorded send latency.
- **SC-007**: Raising a cap above current usage restores sending within one
  request, with no process restart.
- **SC-008**: The integration lane stays green across twenty consecutive runs,
  and no new file needs adding to feature 030's exemption list except ones whose
  subject is a global quota sweep.
- **SC-009**: The chapter's published page measures between 2,000 and 4,000 prose
  words, counted on the finished page rather than estimated.

## Assumptions

- **The cap is denominated in metered units — messages and active users — not in
  money.** No price, unit cost or currency appears anywhere in `docs/04-srs.md` or
  `docs/05-sad.md`; the only references to pricing are aspirations in the journey
  map. FR-RTL-06's design note calls it "a purchasing requirement, not a technical
  one", whose stated harm is *unbounded cost exposure* — which a unit cap bounds.
  Inventing a pricing primitive the SRS never specifies would be scope the
  constitution's Principle VII asks to be justified, and there is nothing to justify
  it against yet.
- **Connection-minutes, the third dimension FR-RTL-05 names, is chapter 3.11.**
  Not deferred to a promise — scheduled, with a number, and the gauntlet moved to
  3.12 to make room (`docs/07-tutorial-plan.md`). Messages and distinct users are
  both derivable from rows that already exist: `messages.user_id` has been in
  `0000_core_tables.sql` since Part 2, so counting them is an aggregation question.
  A connection-minute is a duration, nothing records it today, and the service that
  would have to record it is the gateway, **which owns no tables**. Combining the
  two would give one chapter about counting that quietly becomes a chapter about
  who is allowed to write. FR-RTL-05 is therefore two-thirds closed by 3.10 and
  fully closed by 3.11.
- **Media bytes, which FR-MED-12 folds into quota enforcement, are out of scope.**
  Media does not exist yet; it is Part 4. The quota shape should leave room for a
  further dimension without a migration that rewrites it.
- **Configuration is per environment and by the same mechanism chapter 3.8 used**
  for rate limits — nullable columns, null meaning "no override". There is no
  dashboard until FR-DSH, which is Part 4, so a self-service configuration surface
  is not part of this chapter.
- **The threshold email reuses chapter 3.9's transport**: a table with a
  `delivered_at` that starts null, drained by a relay, read in tests through
  Mailpit. Whether that becomes a fourth table or a generalisation of the third is
  a design question for the plan, not a scope question for the spec.
- **"Admins" means organisation members with the owner role**, the only role the
  schema carries today.
- **This chapter publishes** — unlike feature 030 — so its fences belong in the
  chapter that teaches them, not in `fences/post-series.md`.

## Dependencies

- Chapter 3.8's per-environment limit policy columns and its refusal shape, which
  this chapter must be distinguishable from rather than duplicate.
- Chapter 3.9's notification transport and its Mailpit-backed tests.
- Feature 030's guard, which is live in the integration lane: a quota sweep is a
  global operation, and a test that drives one is exactly the shape the guard
  refuses unless it is on the exemption list with the tables it needs.
- The unresolved `docs_url` for `rate_limited` that chapter 3.8 shipped. This
  chapter adds a second error code with the same problem, and Phase 2's exit
  criterion — an external developer integrating on public documentation alone — is
  chapter 3.12.
