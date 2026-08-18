# Feature Specification: Tutorial Chapter 3.6 — "When to stop trying"

**Feature Branch**: `027-chapter-3-6`

**Created**: 2026-08-18

**Status**: Draft

**Input**: User description: "Start chapter 3.6"

Chapter 3.5 shipped a dispatcher that never gives up on an *endpoint* — only on a
*delivery*. A customer whose server has been returning 500 for three days keeps
receiving seven attempts per event, forever, and nobody is told. This chapter adds
the record of what happened and the decision to stop, in that order, because the
second is indefensible without the first.

FR-WHK-06 and FR-WHK-07 were deliberately deferred out of 3.5 rather than dropped;
the deferral and its reason are recorded in `specs/026-chapter-3-5/chapter-notes.md`.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Every attempt leaves a record (Priority: P1)

A customer integration engineer's webhooks "stopped working". Somewhere in the
platform there is now a complete account of what happened to each event: when
every attempt was made, what the endpoint answered, how long it took, and what
went wrong when nothing answered at all.

**They cannot read it yet, and that is the shape of this chapter.** The account is
emitted onto the analytical stream; the surface a customer reads it through is
Part 4's ingester. What this story delivers is that the evidence exists and is
complete — because the two stories after it spend that evidence, and a platform
that disables a paying customer's endpoint without it is one that cannot explain
itself afterwards.

**Why this priority**: It is the evidence every other story depends on. Disabling
an endpoint, explaining the disablement, and reasoning about a flaky customer are
all impossible without a per-attempt record, which is exactly why auto-disable was
deferred out of 3.5 rather than shipped without it.

**Independent test**: Drive an endpoint through a mix of success, failure and
timeout; consume the analytical stream and confirm one record per attempt carrying
timestamp, status, latency and error, and that a timeout is recorded with no
status rather than being omitted.

**Acceptance scenarios**:

1. **Given** an endpoint that answers 200, **when** an event is delivered, **then**
   one attempt record exists with the status and a latency.
2. **Given** an endpoint that never answers, **when** the attempt times out,
   **then** a record exists with no status, a latency equal to the timeout, and an
   error naming the failure.
3. **Given** a delivery that exhausts its schedule, **when** the analytical stream
   is consumed, **then** all seven attempts are present with their individual
   outcomes and attempt numbers.
4. **Given** two environments, **when** the stream is consumed, **then** every
   attempt carries the environment it belongs to, on the subject and in the
   payload, and no attempt from one appears under the other (constitution I).

### User Story 2 - An endpoint that has been failing for an hour is switched off (Priority: P2)

An endpoint has returned nothing but failures for over an hour. The platform stops
delivering to it, records why, and produces a notification the organisation can be
told about. The customer's other endpoints are unaffected.

**Why this priority**: This is the requirement the chapter is named for, and it
depends on Story 1's record. It ranks below it because a platform with the record
and no auto-disable is merely inefficient, while auto-disable without the record
is a customer-visible action nobody can justify afterwards.

**Independent test**: Drive an endpoint into continuous failure spanning more than
the threshold; confirm it is disabled exactly once, a reason is recorded, deliveries
stop, and a second healthy endpoint in the same environment keeps receiving.

**Acceptance scenarios**:

1. **Given** an endpoint failing continuously for longer than the threshold,
   **when** the next failure is recorded, **then** the endpoint is disabled and a
   notification record is written naming the endpoint, the window and the last error.
2. **Given** an endpoint that fails, succeeds, then fails again, **when** the
   threshold elapses, **then** it is NOT disabled — the success broke the streak.
3. **Given** an endpoint already disabled, **when** further failures are recorded,
   **then** it is not disabled again and no second notification is produced.
4. **Given** a disabled endpoint, **when** new events match its subscriptions,
   **then** no deliveries are created for it and no attempts are made.
5. **Given** an endpoint disabled automatically, **when** a customer inspects it,
   **then** they can tell it was disabled by the platform rather than by a person.

### User Story 3 - A customer proves the endpoint is fixed and turns it back on (Priority: P3)

Having repaired their server, the customer sends a synthetic test event to it,
sees it succeed, and re-enables the endpoint themselves.

**Why this priority**: It closes the loop the first two stories open. Without it a
disabled endpoint is re-enabled on hope, and the first real event is the
experiment — which is how an endpoint gets disabled twice in a day.

**Independent test**: Disable an endpoint, send a test event, confirm it is
delivered and recorded and distinguishable from a real event, then re-enable and
confirm delivery resumes with a cleared failure streak.

**Acceptance scenarios**:

1. **Given** any endpoint, **when** a test event is requested, **then** a synthetic
   event is signed and delivered exactly as a real one, and the caller is told what
   the endpoint answered.
2. **Given** a disabled endpoint, **when** a test event is requested, **then** it is
   still delivered — testing is how a customer establishes the endpoint is fixed.
3. **Given** a test event, **when** a recipient inspects it, **then** it is
   identifiable as synthetic and cannot be mistaken for a real platform event.
4. **Given** a re-enabled endpoint, **when** it next fails, **then** the hour is
   measured from that new failure rather than from the old streak.

### Edge Cases

- An endpoint failing for an hour with only two attempts in that window (a long
  retry schedule) — is that "continuous failure"? See FR-007's minimum-attempts rule.
- An endpoint whose very first attempt fails and is never retried before the
  threshold elapses.
- Clock movement between attempts: the window must not be computable as a negative
  duration.
- A disabled endpoint that still has deliveries pending in the schedule from before
  the disablement.
- Two dispatcher instances recording the failure that crosses the threshold at the
  same moment — the endpoint must be disabled once, not twice.
- A test event sent to an endpoint whose URL no longer resolves.
- An attempt whose error message is enormous, or contains a customer's payload.

## Requirements *(mandatory)*

### Functional Requirements

**The attempt record (FR-WHK-06)**

- **FR-001**: Every delivery attempt MUST be emitted with the time it was made,
  the response status when there was one, the latency, and the error when there was
  no response. Emission is best effort: a record MAY be lost when the analytical
  path is unavailable, and MUST NOT be retried at the cost of the delivery path
  (see FR-003 and FR-005). No other loss is acceptable.
- **FR-002**: An attempt record MUST identify the delivery, the endpoint, the event
  and the attempt number, so one event can be followed across its schedule by
  whoever is consuming the stream.
- **FR-003**: Attempt records MUST be emitted on the analytical path as the SAD
  describes, published asynchronously to the durable queue, and MUST NOT be written
  synchronously on the delivery path.
- **FR-004**: An attempt record MUST NOT contain the event payload, a signing
  secret, or a signature. Sizes, identifiers, statuses and durations only.
- **FR-005**: The platform MUST state plainly, in the chapter and in the contract,
  that attempt records are not yet queryable by a customer, and MUST name the
  chapter that makes them so.

**Deciding to stop (FR-WHK-07)**

- **FR-006**: The platform MUST track, per endpoint, the start of the current
  unbroken run of failures, and MUST clear it on any successful delivery.
- **FR-007**: An endpoint MUST be disabled automatically when its unbroken failure
  run has lasted longer than **one hour** AND has contained at least **five**
  attempts, so that a single failure followed by a long retry gap cannot trigger a
  disablement on its own. Both are fixed values, not configuration: an operator who
  can lower the floor to one has an operator who can disable a customer's endpoint
  on a single bad response.
- **FR-008**: Disabling MUST happen at most once per run of failures: an endpoint
  already disabled MUST NOT be disabled again, and MUST NOT produce a second
  notification.
- **FR-009**: An automatic disablement MUST be distinguishable from a customer
  disabling their own endpoint, and MUST record the reason, the window and the
  last observed error.
- **FR-010**: A disabled endpoint MUST receive no new deliveries, and deliveries
  already scheduled for it MUST NOT be attempted.
- **FR-011**: Disablement MUST write a notification record naming the organisation
  to be told, the endpoint, and why. The platform MUST NOT claim the organisation
  has been notified until a transport exists.
- **FR-012**: Disabling one endpoint MUST NOT affect any other endpoint, in the
  same environment or any other.

**Proving it works again (FR-WHK-09)**

- **FR-013**: A customer MUST be able to send a synthetic test event to any of
  their endpoints, including a disabled one.
- **FR-014**: A test event MUST be signed and delivered by the same path a real
  event takes, so that a success proves something about real deliveries.
- **FR-015**: A test event MUST be identifiable as synthetic by its recipient and
  MUST NOT be confusable with a real platform event.
- **FR-016**: The result of a test event MUST be reported back to the caller,
  including what the endpoint answered.
- **FR-017**: Re-enabling an endpoint MUST clear its failure run, so the hour is
  measured from the next failure rather than from the old one.

**Everywhere**

- **FR-018**: Every operation MUST be scoped to one environment; no attempt record,
  notification or endpoint MUST be reachable from another tenant.
- **FR-019**: The chapter MUST be published in English and Vietnamese, with fences
  mirrored byte for byte.
- **FR-020**: Every file the chapter's prose asserts MUST be fenced, including test
  files, and the fence chain MUST replay onto the platform repository.
- **FR-021**: Every transcript the chapter quotes MUST be captured from a real run.

### Key Entities

- **Attempt record**: One try at one delivery. Carries when, what status, how long,
  and what error — never the payload. Emitted analytically; not queryable in this
  chapter.
- **Failure run**: The current unbroken sequence of failures for one endpoint, with
  the time it started and how many attempts it contains. Cleared by any success and
  by re-enablement. This is the operational state auto-disable reads.
- **Disablement notification**: The record that an endpoint was switched off, who
  should be told, and why. Written now; delivered by a transport a later chapter
  builds.
- **Test event**: A synthetic event a customer sends to their own endpoint, signed
  and delivered like a real one, and marked so nobody mistakes it for one.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: For any event a customer names, every attempt made on their behalf
  has been emitted with its outcome and duration, and can be read off the
  analytical stream without the platform consulting logs. **Being shown it —
  a query surface a customer can use — is Part 4's ingester, not this chapter.**
- **SC-002**: An endpoint failing continuously for more than an hour is switched off
  without anybody intervening, and exactly once.
- **SC-003**: An endpoint that fails intermittently but succeeds at least once an
  hour is never switched off.
- **SC-004**: Switching off one endpoint changes nothing for any other endpoint, in
  the same environment or another.
- **SC-005**: A customer can establish that a repaired endpoint works before
  re-enabling it, and re-enabling starts the clock fresh.
- **SC-006**: No attempt record, in any store or transcript, contains a payload, a
  signing secret or a signature.
- **SC-007**: The chapter states which part of FR-WHK-06 and FR-WHK-07 it does not
  yet deliver, and names where each is finished.
- **SC-008**: Both lanes pass with every pre-existing suite unchanged in substance,
  and coverage exits 0 with every ratchet intact.
- **SC-009**: Every claimed invariant fails when its mechanism is removed, verified
  by sabotage with files restored byte-identical.
- **SC-010**: The chapter is reachable in both locales and its figures render.

## Assumptions

- **The attempt log is published, not queried, in this chapter.** Attempts are
  emitted as analytical events onto the durable queue exactly as the SAD describes.
  No ClickHouse writer and no query surface are built here; FR-WHK-06's "queryable
  for 30 days" is therefore **half-delivered on purpose**, and the chapter must say
  so and name Part 4's ingester as where it is finished. Auto-disable does not wait
  for that pipeline — it reads a small operational failure-run state instead, which
  keeps constitution III intact: no analytical query runs against PostgreSQL, and a
  backlogged analytics path cannot stop an endpoint being disabled.
- **The notification is recorded, not sent.** This platform has no email capability
  of any kind. FR-RTL-07 (chapter 3.7, quotas) needs the same transport, so building
  one here would mean building it for its second consumer first. The disablement
  writes a notification record; the chapter states plainly that FR-WHK-07's "and the
  organisation notified by email" is not yet met.
- **The synthetic test event (FR-WHK-09) is in scope**, because it closes the
  disable-repair-re-enable loop that the other two requirements open. Without it a
  customer re-enables on hope and the first real event is the experiment.
- **Re-enablement is manual.** The platform does not probe a disabled endpoint to
  see whether it recovered; automatic probing would re-introduce, on a timer, the
  capacity drain that disabling was meant to stop. The customer re-enables, and
  FR-WHK-09 is how they can be confident before doing so.
- **"Continuous failure" is a run, not a rate.** Any success clears it. This is the
  simplest rule that matches the requirement's wording, and it is deliberately
  generous to a flaky customer: an endpoint succeeding once an hour is never
  disabled, on the grounds that a platform switching off endpoints that sometimes
  work is a worse failure than one that keeps trying.
- **The minimum-attempts floor exists because an hour is not enough on its own.**
  The 3.5 schedule reaches two hours between attempts, so an endpoint could satisfy
  "failing for more than an hour" with a single failure. The floor is what stops one
  bad response from disabling an endpoint.
- **No new runtime dependency**, per constitution VII. The attempt event uses the
  existing publisher; the failure run is a column; the test event uses the existing
  delivery path.
- **The dispatcher still writes nothing to PostgreSQL** (constitution IV). Failure
  runs, disablement and notification records are api-side writes reached over the
  internal seam 3.5 built.
- **Chapter numbering**: Part 3 was renumbered when 3.5 shipped. This is 3.6; Limits
  and quotas is 3.7; the isolation gauntlet is 3.8.

## Out of Scope

- Sending email, or any transport for the notification record.
- Querying attempt records — the analytics ingester and the ClickHouse schema are
  Part 4's subject.
- A dashboard or any UI. Every surface here is API-first (constitution V).
- Automatic re-enablement or health probing of disabled endpoints.
- Changing the retry schedule, the signature scheme, or anything else 3.5 settled.

## Dependencies

- Chapter 3.5's delivery path, dispatcher service and internal seam (`part3-ch5`).
- Chapter 3.3's outbox relay and publisher, for emitting analytical events.
- Chapter 3.4's claim ledger, unchanged.
- The compose stores. No new infrastructure.
