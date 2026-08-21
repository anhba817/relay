# Feature Specification: Chapter 3.11 — Counting a connection

**Feature Branch**: `032-chapter-3-11`

**Created**: 2026-08-22

**Status**: Draft

**Input**: User description: "start chapter 3.11"

Chapter 3.11 of the Relay tutorial, closing the third dimension FR-RTL-05 names:
connection-minutes. Chapter 3.10 metered messages sent and distinct active users
and stopped there, because those two are the same kind of problem and this one is
not.

Messages and users were already rows. `messages.user_id` has been in
`0000_core_tables.sql` since Part 2, so counting them was an aggregation question
answered inside a transaction the api already owned. A connection-minute is a
duration. Nothing records it, no row exists to count, and the only process that
can see a connection at all is the gateway — **which owns no tables**, by ADR-05,
enforced since chapter 2.1 by a lint ban that makes a database import a build
failure rather than a review comment.

So the subject is not counting. The subject is metering from a service that
cannot write: what it has to say, how often it has to say it, and what happens to
the number when the thing saying it dies mid-sentence.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A duration becomes a number, from a service that cannot write it (Priority: P1)

Priya's application holds WebSocket connections open all month. Every minute a
connection is open is counted against her environment's monthly
connection-minutes figure, and the figure is durable: it is in the same store the
message counts are in, and flushing the per-minute counter store does not change
it.

The gateway holds the connections and gains no database. It reports what it can
see; the api records it. The count is per connection — one hundred sockets open
for one minute is one hundred connection-minutes, not one.

**Why this priority**: without a recorded figure there is nothing to cap, nothing
to alert on, and FR-RTL-05 stays two-thirds closed. Every other story in this
chapter reads this number.

**Independent Test**: open a connection, hold it across several minute
boundaries, close it, and read the environment's connection-minutes for the
period. Repeat with two concurrent connections and confirm the figure doubles.

**Acceptance Scenarios**:

1. **Given** an environment with no recorded usage, **When** one connection is
   held open across three calendar-minute boundaries, **Then** the environment's
   connection-minutes for the period counts every minute in which the connection
   was open.
2. **Given** two connections open simultaneously for the same minute, **When**
   usage is read, **Then** that minute contributes two connection-minutes.
3. **Given** a recorded figure, **When** the per-minute counter store is flushed,
   **Then** the figure is unchanged.
4. **Given** a connection open when a calendar month ends, **When** usage is read
   for both periods, **Then** the minutes before the boundary are in the old
   period and the minutes after it are in the new one.
5. **Given** a socket that opens and closes inside a single reporting interval,
   **When** usage is read, **Then** it has been counted.

### User Story 2 - The report is unreliable, and the number is not (Priority: P1)

The gateway talks to the api over a network. A report can be lost, delivered
twice, or delivered after the process that sent it has already died. None of
those may produce a wrong bill.

A report delivered twice credits its minutes once. A report lost is recovered by
the next one, because a report says what a connection has consumed in total
rather than what it consumed since last time. A gateway killed without warning
stops reporting, and the connections it was holding stop accruing — the figure
freezes within one reporting interval of the truth rather than growing forever
against sockets nobody is holding.

**Why this priority**: this is the chapter. Metering an event is a write in the
transaction that caused it; metering a duration is a claim from another process
about time that has already passed, and every failure mode of that claim shows up
as money.

**Independent Test**: replay the same report and confirm the figure does not
move. Drop a report and confirm the next one restores the figure. Kill the
gateway mid-connection, wait past several reporting intervals, and confirm the
figure stopped where the last report left it.

**Acceptance Scenarios**:

1. **Given** a report the api has already recorded, **When** the identical report
   is delivered again, **Then** the recorded figure is unchanged.
2. **Given** a report that never reached the api, **When** the next report for
   the same still-open connection arrives, **Then** the figure includes the
   minutes the lost report carried.
3. **Given** an open connection, **When** the gateway process is killed without
   closing its sockets, **Then** the figure for that connection stops advancing
   and does not advance further while the period runs.
4. **Given** two reports for one connection that arrive out of order, **When**
   both have been processed, **Then** the figure reflects the later one and is
   not reduced by the earlier one.
5. **Given** the api is unreachable when a report falls due, **When** it becomes
   reachable again, **Then** connections still open are counted correctly and no
   connection is closed because of the outage.

### User Story 3 - The cap brakes the thing it meters (Priority: P2)

Priya's environment carries a hard cap on connection-minutes. When the figure
reaches it, new connections are refused at the door with the quota error code —
not the rate-limit one, because retrying in thirty seconds is right for a rate
limit and wrong for a quota that will still be exceeded in an hour.

Sockets already open stay open and keep delivering, which is what FR-RTL-08
promises. They also keep accruing minutes, so the cap is a brake and not a wall,
and the overshoot is bounded by how long the open sockets live rather than being
unbounded.

**Why this priority**: FR-RTL-05 says enforce, not meter. A cap that refuses
sends for a connection-minutes breach would leave an idle listener burning the
metered resource with nothing to stop it.

**Independent Test**: set a cap below current usage, attempt a new connection,
and confirm it is refused with the quota code. In the same test, confirm a
connection opened before the breach is still open and still receiving.

**Acceptance Scenarios**:

1. **Given** connection-minutes usage at or above the hard cap, **When** a client
   attempts a new connection, **Then** it is refused and the refusal carries the
   quota error code rather than the rate-limit one.
2. **Given** the same state, **When** a connection opened before the breach sends
   and receives, **Then** both succeed.
3. **Given** the same state, **When** message history is read over REST, **Then**
   it succeeds.
4. **Given** a refused connect, **When** the cap is raised above current usage,
   **Then** the next connect attempt succeeds with no restart and no manual step.
5. **Given** a cap configured as zero, **When** any connect is attempted, **Then**
   it is refused.
6. **Given** no cap configured for connection-minutes, **When** any connect is
   attempted, **Then** it succeeds and the minutes are still recorded.

### User Story 4 - Nobody is surprised by a third dimension (Priority: P3)

The 50%, 80% and 100% emails FR-RTL-07 requires arrive for connection-minutes as
they do for the other two dimensions, at most once per threshold per period, from
the same table and the same relay chapter 3.10 built.

**Why this priority**: the transport exists. What this story tests is whether
adding a dimension to it costs what chapter 3.10 predicted it would cost.

**Independent Test**: cross each threshold and read what the mail server
received. Re-cross an already notified threshold and confirm nothing further
arrives.

**Acceptance Scenarios**:

1. **Given** a configured connection-minutes quota, **When** usage first reaches
   50%, 80% and 100%, **Then** three emails are sent, each naming
   connection-minutes as the dimension.
2. **Given** a threshold already notified this period, **When** usage crosses it
   again, **Then** no further email is sent.
3. **Given** a single report that carries usage past two thresholds at once,
   **When** it is processed, **Then** both thresholds are notified.
4. **Given** notifications sent in one period, **When** the period rolls over,
   **Then** the thresholds are notifiable again.

### Edge Cases

- **A test cannot wait a minute.** Every acceptance scenario above is stated in
  calendar minutes, and an integration suite that slept through them would take
  longer than the twenty-run battery. The unit of time must be injectable, and
  the definition of "which minute is it" must live in one place that tests can
  drive — the same shape chapter 3.10 used for "which month is it".
- **A socket open across a month boundary.** Minutes land in the period they
  occurred in. A single report may therefore have to credit two periods.
- **A report for a period that has already rolled over.** A report that was
  delayed can name minutes in a period that is no longer current. It must still
  land in the period it names.
- **A report naming a connection the api has never heard of.** The api is not
  told when a connection opens; the first it hears of one is a report. Whether
  that is accepted as the connection's first report or refused as unknown is a
  decision the plan must make and state.
- **A report naming an environment the caller may not meter.** A metering route
  that any caller can reach is a billing forgery. The report path must
  authenticate, and an unauthenticated or wrongly scoped report must change no
  figure.
- **Clock skew between gateway instances.** Two instances disagreeing about the
  wall clock will disagree about which minute a connection was open in. The bound
  on the resulting error must be stated rather than assumed to be zero.
- **A graceful shutdown.** A gateway told to stop knows its sockets are about to
  die and can report before it goes, which is the difference between a bounded
  loss and no loss at all. A crash cannot.
- **The cap is crossed while five hundred sockets are open.** All five hundred
  stay open and keep accruing. The overshoot is real and must be bounded and
  named, not discovered on a bill.
- **A browser cannot read the refusal.** Chapter 3.8 met this with the 429 at the
  same door: a browser `WebSocket` gives the page no status code and no body from
  a failed upgrade. Whatever this chapter does about the 402 must be the same
  answer 3.8 gave about the 429, or an explicit change to it.
- **Accounting state that grows with time rather than with connections.** The
  naive record of "which minutes have I already credited" is one row per
  connection per minute, which is tens of millions of rows a month for a
  thousand concurrent sockets. Chapter 3.10 refused the same shape for distinct
  users and bounded it by users instead of traffic; the same bound is required
  here.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST record, per environment and per calendar month, the
  connection-minutes consumed.
- **FR-002**: A connection-minute MUST be defined as one calendar minute during
  which one connection was open for any part of that minute, counted per
  connection. One hundred concurrent connections open for one minute MUST count
  one hundred.
- **FR-003**: The definition of which minute an instant belongs to MUST live in
  one place **per service**, be usable from tests without waiting in real time,
  and match the existing definition of which month an instant belongs to. Where
  two services cannot share the definition, a test MUST assert that both
  implementations agree on the same instants.
- **FR-004**: The service that observes connections MUST NOT gain database
  access. Recording MUST be performed by the service that owns the tables.
- **FR-005**: Minutes MUST be reported while a connection is open, and again when
  it closes. A connection whose whole life falls between two reports MUST still be
  counted.
- **FR-006**: A report delivered more than once MUST credit its minutes exactly
  once.
- **FR-007**: The loss of a single report MUST NOT permanently under-count a
  connection that is still open; a later report MUST restore the figure.
- **FR-008**: When the observing service stops without closing its connections,
  the minutes not yet reported MUST be bounded by the reporting interval, and the
  affected connections MUST NOT continue to accrue afterwards.
- **FR-009**: A connection open across a period boundary MUST have each minute
  attributed to the period in which that minute fell.
- **FR-010**: The state that makes a repeated report idempotent MUST be bounded by
  the number of connections, not by elapsed time. Storage MUST NOT grow
  proportionally to the number of minutes in the period.
- **FR-011**: The report path MUST authenticate the caller. An unauthenticated or
  wrongly scoped report MUST change no recorded figure.
- **FR-012**: A failure to report MUST NOT close a connection, refuse a connect,
  or fail a send.
- **FR-013**: An environment MUST be able to carry a hard cap and a soft threshold
  for connection-minutes, configured by the same mechanism as the other two
  dimensions, each absent by default.
- **FR-014**: A connection-minutes cap of zero MUST be distinguishable from no cap
  configured, and MUST refuse every connect.
- **FR-015**: When connection-minutes usage is at or above the hard cap, new
  connections MUST be refused.
- **FR-016**: A connect refused for quota MUST carry the quota error code, not the
  rate-limit code, and MUST NOT carry a retry hint that implies the condition
  clears on a timer.
- **FR-017**: When connection-minutes usage is at or above the hard cap, existing
  connections MUST stay open, MUST continue to deliver, and MUST continue to be
  metered.
- **FR-018**: When connection-minutes usage is at or above the hard cap, message
  sends over REST and message history reads MUST succeed.
- **FR-019**: The chapter MUST state the bound on cap overshoot in terms of the
  connections still open and the reporting interval.
- **FR-020**: A refused environment MUST resume accepting connections, with no
  restart and no manual step, when the cap is raised above usage or the period
  rolls over.
- **FR-021**: A soft threshold on connection-minutes MUST alert without refusing
  anything.
- **FR-022**: The system MUST email organisation admins when connection-minutes
  usage first reaches 50%, 80% and 100% of a configured quota, at most once per
  threshold per environment per period, resetting with the period.
- **FR-023**: A single report that carries usage past more than one threshold MUST
  notify each threshold crossed.
- **FR-024**: Adding this dimension MUST NOT require rewriting the usage tables.
  Chapter 3.10 predicted the cost as one new key in the policy shape plus a
  one-line change to each constraint that enumerates dimensions. The chapter MUST
  record the cost that was actually paid against that prediction, including if it
  was higher.
- **FR-025**: The connect path MUST NOT gain work proportional to the tenant's
  traffic, connection history, or elapsed minutes in the period.
- **FR-026**: Reported figures MUST be derivable without the per-minute counter
  store. Flushing that store MUST NOT change any figure.
- **FR-027**: Any test that drives a global operation MUST be named in the test
  harness's exemption list with the tables it needs, and in the matching lint
  ignores list. Feature 030's guard refuses a cross-environment mutation from a
  file on neither.
- **FR-028**: The chapter MUST answer the question `docs/04-srs.md` records as
  open — whether connection-minute metering needs per-second precision — and MUST
  state the rounding rule and who it charges.
- **FR-029**: A closed connection's final figure MUST be retried until a report
  carrying it is accepted, because no later report will carry it. The retained
  set MUST be bounded, and discarding an entry because the bound was reached MUST
  be logged and counted rather than silent.

### Key Entities

- **Connection-minute**: the unit. One calendar minute during which one
  connection was open for any part of it. Not divisible, not pro-rated, and
  charged per connection rather than per environment.
- **Usage report**: what the observing service claims about a connection. Names
  the connection, the environment, and the minutes consumed, and says what has
  been consumed in total rather than what has been consumed since last time — the
  property that makes a lost report recoverable and a repeated one harmless.
- **Connection accounting record**: the state that makes a repeated report credit
  nothing. One per connection, not one per minute.
- **Usage record**: extended from chapter 3.10 with a third figure for the same
  environment and period.
- **Quota policy**: extended from chapter 3.10 with a third dimension, hard and
  soft, each optionally absent. Absent means unlimited; zero means none.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A connection held open across N minute boundaries records N+1
  connection-minutes, measured with a driven clock rather than by sleeping.
- **SC-002**: Two connections held open across the same minute record two
  connection-minutes for that minute.
- **SC-003**: Replaying an identical report leaves the recorded figure
  numerically unchanged, verified by reading the figure before and after.
- **SC-004**: Discarding one report and delivering the next restores the figure
  to the value it would have had if neither had been lost.
- **SC-005**: After the observing process is killed with an open connection, the
  figure advances by no more than one reporting interval's worth of minutes, and
  is identical when read again after ten further intervals.
- **SC-006**: With usage above a hard cap, a new connect is refused and a
  connection opened before the breach is still open and still receiving sixty
  seconds later — measured in the same test, against the same environment.
- **SC-007**: With usage above a connection-minutes hard cap, a REST send and a
  history read both succeed.
- **SC-008**: Raising the cap above current usage restores connecting within one
  attempt, with no process restart.
- **SC-009**: Crossing 50%, 80% and 100% produces exactly three emails for the
  connection-minutes dimension per period, verified by reading what the mail
  server received rather than by asserting on a send call.
- **SC-010**: A report presented without a valid internal credential changes no
  figure, verified by reading the figure before and after the refused call.
- **SC-011**: A connection spanning a period boundary places its minutes in both
  periods, with the two figures summing to the connection's total.
- **SC-012**: The connect path executes no scan proportional to the tenant's
  traffic or connection history, shown by `EXPLAIN (ANALYZE, BUFFERS)` for the
  connect-time read.
- **SC-013**: The cost of the third dimension is counted and written down —
  migrations, constraint lines, and columns — and compared against chapter 3.10's
  prediction of "a new key plus a one-line constraint change". A higher number is
  a result, not a failure.
- **SC-014**: The integration lane stays green across twenty consecutive runs,
  and no new file is added to feature 030's exemption list. If one is added, the
  chapter states which global operation required it.
- **SC-015**: The chapter's published page measures between 2,000 and 4,000 prose
  words, and its fence count is derived by reading the page, both counted on the
  finished page rather than estimated.

- **SC-016**: Reported connection-minutes are numerically identical before and
  after the per-minute counter store is flushed.
- **SC-017**: The accounting state's row count is a function of concurrent
  connections and not of elapsed minutes — ten connections driven through one
  minute and ten driven through sixty produce the same number of rows.
- **SC-018**: The observing service still imports no database client after this
  chapter, verified by the lint rule that has banned it since chapter 2.1.
- **SC-019**: With every report failing, connections stay open, new connects
  succeed while under cap, and sends succeed — measured with the report path
  forced to error.
- **SC-020**: A soft threshold configured with no hard cap sends its email and
  refuses no connect, verified by a successful connect after the email arrives.
- **SC-021**: A connection opened and closed entirely between two reports is
  counted — one socket living five seconds inside a sixty-second interval records
  one connection-minute, not zero.

## Assumptions

- **The gateway owns no tables and does not gain any.** ADR-05 says the api is
  the only writer, chapter 2.1 turned that into a lint ban, and chapter 3.8
  already resolved the gateway's rate limits at `/internal/session` rather than
  giving the gateway a database to read them from. This chapter is the hardest
  case for that rule — the gateway is the only process that can see the thing
  being metered — and the rule does not bend.
- **Metering is per wall-clock minute, not per second.** `docs/04-srs.md` records
  this as an open question addressed to Product and Billing: "does connection-minute
  metering need per-second precision, or is per-minute rounding acceptable?" The
  answer taken here is per-minute, on calendar minute boundaries, charged per
  connection. A five-second socket therefore costs one minute and a socket open
  from 00:00:59 to 00:01:01 costs two. This charges reconnect churn, which the
  alternatives do not, and it makes the identity of a minute the natural key for
  deduplicating a repeated report.
- **The cap is denominated in metered units, not money.** Inherited from chapter
  3.10 and unchanged: no price, unit cost or currency appears in `docs/04-srs.md`
  or `docs/05-sad.md`, and inventing a pricing primitive is scope the
  constitution's Principle VII asks to be justified.
- **A hard cap refuses the operation that consumes the dimension.** The messages
  cap refuses sends; the connection-minutes cap refuses connects. FR-RTL-08's
  "sends rejected, existing connections and history reads unaffected" is read as a
  promise about what stays working, not as a rule that sends are the only thing a
  cap may ever refuse — a connection-minutes cap that only refused sends would
  leave an idle listener consuming the metered resource with no brake at all.
- **Per-day metering is not this chapter.** FR-ANL-05 meters the same three
  dimensions per tenant per day into the analytical store, which is Part 4. This
  chapter records per environment per month in the operational store, as chapter
  3.10 did, and closes FR-RTL-05 rather than FR-ANL-05.
- **Media bytes remain out of scope.** FR-MED-12 folds stored media bytes into
  quota enforcement; media does not exist yet.
- **The threshold email reuses chapter 3.10's table and relay.** A third
  dimension is a new value in an existing column, not a fifth outbox.
- **There is no dashboard.** FR-DSH-04/05 show usage to a customer, which is Part
  4. Caps are configured the way chapter 3.10 configures them.
- **This chapter publishes**, so its fences belong in the chapter that teaches
  them, not in `fences/post-series.md`.

## Dependencies

- Chapter 3.10's usage tables, its policy shape, its `quota_exceeded` code and
  402 status, and its notification table and relay. This chapter extends all of
  them and is the first test of whether they were extensible.
- Chapter 3.8's refusal at the socket door. The upgrade path already writes a raw
  HTTP response by hand for a connect rate limit; a quota refusal is a second
  shape at the same door, and the two must be distinguishable by a client.
- Chapter 3.2's `POST /internal/session`, which the gateway already calls before
  the upgrade completes, and which already carries per-environment limits back to
  a service that cannot read them itself.
- Chapter 2.5's session lifecycle and its heartbeat, which is the only existing
  periodic timer in the gateway.
- ADR-05 and the chapter 2.1 lint ban, which are the constraint the chapter is
  about rather than a background detail.
- Feature 030's guard, live in the integration lane.
- The unresolved `docs_url` shipped by chapter 3.8 for `rate_limited` and by
  chapter 3.10 for `quota_exceeded`. Chapter 3.12 owns it; this chapter must not
  add a third.
