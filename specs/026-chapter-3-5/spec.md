# Feature Specification: Tutorial Chapter 3.5 — Webhooks That Survive the Customer

**Feature Branch**: `026-chapter-3-5`

**Created**: 2026-08-10

**Status**: Draft

**Input**: User description: "Continue with chapter 3.5"

**Scope decision (2026-08-10)**: the dispatcher ships as its own deployable
service, and the chapter is narrowed to compensate — the attempt log (FR-WHK-06)
and auto-disable (FR-WHK-07) move to a follow-on chapter. See Assumptions.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read chapter 3.5 and deliver events to an endpoint you do not control (Priority: P1)

A reader arrives at the `part3-ch4` checkpoint with a configured stream and a
consumer whose runtime deduplicates in the same transaction as its effect. Every
consumer so far has had one thing in common: its effect was a row in a database
it could roll back.

This chapter's consumer calls someone else's HTTP endpoint, and it breaks that
pattern twice. The effect cannot be rolled back, because it already happened on a
machine the platform does not own. And the claim cannot join it in a transaction
anyway, because the dispatcher is a separate service and only the API service
writes to the database.

The reader learns that the honest answer is not a cleverer protocol. It is
choosing which way to be wrong, saying so in the documentation, and giving the
customer the identifier that makes the choice survivable on their end. Then the
machinery that makes an unreliable endpoint the customer's problem rather than the
platform's: a signature they can verify, a bounded retry schedule that outlives
the process running it, and a place for what never succeeds.

**Why this priority**: the chapter is the deliverable. It is also the first
chapter where the platform's correctness depends on a system nobody on the team
controls, which is the defining property of infrastructure as opposed to an
application.

**Independent Test**: a reader at `part3-ch4` can follow the chapter to a platform
that signs and delivers an event to a local endpoint, retries a failing one on a
bounded schedule that survives a restart, and dead-letters what never succeeds —
verified by running the chapter's own tests against a deliberately hostile
endpoint.

**Acceptance Scenarios**:

1. **Given** a reader at `part3-ch4`, **When** they read the chapter's opening,
   **Then** they find 3.4's pattern applied to an HTTP effect and shown to fail,
   before any replacement is offered.
2. **Given** a configured endpoint, **When** an event it subscribes to occurs,
   **Then** a signed request arrives and the reader can verify the signature by
   hand from the chapter's own instructions.
3. **Given** an endpoint that returns errors, **When** the dispatcher retries,
   **Then** the attempts follow a bounded, widening schedule the chapter states as
   numbers with reasons.
4. **Given** a pending retry, **When** the dispatching process is restarted,
   **Then** the retry still happens at its scheduled time — the chapter shows
   this rather than asserting it.
5. **Given** an endpoint that never succeeds, **When** the attempts are exhausted,
   **Then** the event is in a place a human can inspect and replay — the promise
   chapter 3.4 explicitly could not make.
6. **Given** a customer's endpoint that is slow, **When** it is slow, **Then**
   message delivery to end users is unaffected, and the chapter demonstrates it.
7. **Given** a reader following the chapter, **When** they reach the end, **Then**
   they can state why a duplicate webhook is possible, what identifier absorbs it,
   and why the platform chose that failure over the alternative.

---

### User Story 2 - The canonical code advances to tag `part3-ch5` (Priority: P2)

The repository gains webhook endpoints with independently rotatable signing
secrets, and a **new deployable service** that consumes the event stream, signs,
posts, retries on a durable schedule, and dead-letters what never succeeds.

**Why this priority**: the chapter's fences must byte-match a repository that
runs. As in every chapter since 3.1, the code is written and proven before the
prose.

**Independent Test**: at `part3-ch5` the Docker-free gate passes; with the stores
up every integration lane passes including 2.8's journey, 3.3's outbox suite and
3.4's consumer suite; an endpoint that fails on command drives the retry schedule
and the dead-letter path; stopping the dispatcher leaves message delivery
untouched.

**Acceptance Scenarios**:

1. **Given** an environment, **When** more endpoints are configured than the limit
   allows, **Then** the request is refused with an error that names the limit.
2. **Given** an endpoint with a signing secret, **When** a delivery is made,
   **Then** the request carries a signature a recipient can verify without
   contacting the platform, and the secret is never recoverable from anything the
   platform stores or logs.
3. **Given** an endpoint whose secret is rotated, **When** the rotation happens,
   **Then** deliveries continue without interruption and the old secret stops
   verifying after a stated window.
4. **Given** an endpoint subscribed to a subset of event types, **When** an event
   outside that subset occurs, **Then** no delivery is attempted.
5. **Given** the dispatcher running as its own service, **When** it needs to
   record that it has handled an event, **Then** it does so through the API
   service rather than by writing to the database itself.
6. **Given** the dispatcher stopped entirely, **When** messages are sent, **Then**
   they are delivered to end users normally and events accumulate for the
   dispatcher to drain on return.
7. **Given** a delivery that fails, **When** each retry falls due, **Then** the
   attempt happens no earlier than its scheduled delay, and the total number of
   attempts is bounded.
8. **Given** an event whose attempts are exhausted, **When** the last one fails,
   **Then** it is retained in the dead-letter store for a stated period and can be
   replayed.
9. **Given** a customer endpoint that hangs, **When** it hangs, **Then** the
   dispatcher abandons that attempt on a stated timeout and other endpoints
   continue to be served.
10. **Given** the suite at `part3-ch5`, **When** the signature is computed over the
    wrong bytes, **Then** at least one test fails.

---

### User Story 3 - The chapter publishes in English and Vietnamese (Priority: P3)

3.5 becomes reachable in both locales, as 3.4 was.

**Why this priority**: publication is mechanical once the chapter exists, but the
listing must match what is reachable and a translated chapter's fences must
mirror the English ones exactly.

**Independent Test**: the site builds; both locale paths return 200; the listing
shows 3.5 published and translated; the fence chain replays every published
chapter with no drift.

**Acceptance Scenarios**:

1. **Given** the built site, **When** either locale path is requested, **Then** it
   returns 200 with the reading shell and every figure rendered.
2. **Given** the fence-chain check, **When** it runs, **Then** every fenced file in
   every published chapter replays onto the repository byte-for-byte — including
   every file this chapter's prose asserts the existence of.

---

### Edge Cases

- **The effect that cannot be undone.** An HTTP request that times out may still
  have been received and acted upon. The dispatcher cannot know. The chapter must
  say which way it chooses to be wrong rather than implying the ambiguity is
  resolvable.
- **The claim that cannot join the effect.** The dispatcher does not own the
  database, so its record of having handled an event is a separate call that can
  fail independently of the delivery. The chapter must state what happens when the
  delivery succeeds and the record does not.
- **A customer who is slow rather than broken.** One endpoint taking a long time
  must not delay deliveries to other endpoints, and must not delay message
  delivery to end users at all.
- **A customer who returns success and means failure.** The platform can only
  believe the status code. The chapter should say so.
- **An endpoint that recovers during the retry schedule.** A later attempt
  succeeding must stop the schedule cleanly.
- **An endpoint deleted mid-flight.** Events already scheduled for a removed
  endpoint must not be delivered and must not accumulate forever.
- **A secret rotated mid-flight.** A retry scheduled before a rotation must be
  signed with a secret the recipient can still verify, or the rotation window must
  be stated.
- **A dead-letter replay of an event whose endpoint has changed.** Replay must use
  current configuration, or state that it does not.
- **The dead-letter store as a liability.** It is the first store in the platform
  whose purpose is to retain tenant-visible content that failed to leave.
  Retention must be bounded and stated.
- **The dispatcher is down.** Message delivery must be entirely unaffected, and
  the backlog must drain on return without intervention.

## Requirements *(mandatory)*

### Functional Requirements

**The chapter**

- **FR-001**: The chapter MUST be written at a path under `/part-3/chapter-05/`
  and MUST ship both an English and a Vietnamese edition whose fences match byte
  for byte.
- **FR-002**: The chapter MUST demonstrate that chapter 3.4's shared-transaction
  pattern cannot hold for a non-transactional effect, as a reproducible run rather
  than an assertion.
- **FR-003**: The chapter MUST state which delivery guarantee the platform
  chooses, name the failure that choice accepts, and name the identifier a
  recipient uses to absorb it.
- **FR-004**: The chapter MUST give a recipient enough detail to verify a
  signature independently, and MUST show the verification being performed.
- **FR-005**: The chapter MUST state the retry schedule as numbers with reasons,
  and state what happens after the last attempt.
- **FR-006**: The chapter MUST state the dead-letter retention period and what a
  human can do with its contents.
- **FR-007**: The chapter MUST explain why the dispatcher is a separate service
  when the relay and the recorder were not, and what that costs.
- **FR-008**: The chapter MUST carry a `DECISION` note for any shape it derives
  that no source document defines, MUST NOT invent a requirement identifier, and
  MUST name what it does not build with the chapter that owns it.

**The code — endpoints and secrets**

- **FR-009**: An environment MUST support configuring webhook endpoints up to a
  stated maximum, each subscribing to a selected set of event types (FR-WHK-01).
- **FR-010**: Each endpoint MUST have an independently rotatable signing secret
  (FR-WHK-08), stored so it is never recoverable in plaintext from the platform's
  storage or logs (NFR-SEC-02, NFR-SEC-06).
- **FR-011**: Configuring, listing, rotating and removing endpoints MUST be
  tenant-isolated: no environment may observe or affect another's endpoints
  (constitution I, NFR-SEC-09).
- **FR-012**: An endpoint MUST carry an enabled state that its owner can set, and
  a disabled endpoint MUST receive no deliveries.

**The code — the dispatcher as a service**

- **FR-013**: The dispatcher MUST be a separately deployable service, buildable
  and runnable independently of the API service (SAD §4.1).
- **FR-014**: The dispatcher MUST NOT write to PostgreSQL directly. Any state it
  records MUST be obtained through the API service's internal endpoints
  (constitution IV, ADR-04).
- **FR-015**: The dispatcher MUST deduplicate on event identity, as every consumer
  must (constitution IV).
- **FR-016**: The API service MUST start, serve writes and deliver messages with
  the dispatcher absent; events MUST accumulate and drain when it returns
  (FR-WHK-05).

**The code — delivery**

- **FR-017**: Every delivery MUST carry a signature computed over the request
  body, verifiable by the recipient using only the shared secret and the request
  itself.
- **FR-018**: Every delivery MUST carry the event identifier a recipient
  deduplicates on, documented as the deduplication key.
- **FR-019**: Delivery MUST be asynchronous and MUST NOT delay or block message
  delivery to end users (FR-WHK-05).
- **FR-020**: A delivery attempt MUST abandon on a stated timeout, and one slow
  endpoint MUST NOT delay deliveries to other endpoints.
- **FR-021**: An endpoint MUST receive only the event types it subscribes to.

**The code — failure**

- **FR-022**: Failed deliveries MUST be retried on a bounded, widening schedule
  totalling six attempts (FR-WHK-03).
- **FR-023**: A retry MUST NOT occur earlier than its scheduled delay, and a
  pending retry MUST survive a restart of the dispatching process.
- **FR-024**: After the attempts are exhausted, the event MUST be moved to a
  dead-letter store, retained for a stated period, and replayable (FR-WHK-04).

**The code — everything else**

- **FR-025**: No signing secret and no tenant message body MUST appear in any log
  line the dispatcher emits (NFR-SEC-06).
- **FR-026**: An automated test MUST drive the retry schedule and the dead-letter
  path against an endpoint that fails on command, rather than asserting them in
  prose.
- **FR-027**: The existing suites — including 2.8's journey, 3.3's outbox suite
  and 3.4's consumer suite — MUST keep passing with their assertions unchanged in
  substance.

**Publication and provenance**

- **FR-028**: Every code fence MUST byte-match the repository at this chapter's
  state, with amendments to previously-fenced files expressed as hunked diffs.
- **FR-029**: Every file whose existence the chapter's prose asserts MUST be
  fenced, so the fence chain can replay the repository the chapter describes.
- **FR-030**: Every requirement identifier cited in the chapter MUST exist in
  `docs/04-srs.md`, `docs/05-sad.md` or `docs/06-adr-deep-dives.md`, and every
  table and column named in prose MUST exist in the schema.
- **FR-031**: The chapter MUST quote only measured output.
- **FR-032**: If the work exposes a defect in an earlier chapter, it MUST be fixed
  forward in every locale that chapter has, and recorded.
- **FR-033**: `docs/07-tutorial-plan.md` MUST be amended to reflect the narrowed
  scope and the follow-on chapter, so the plan of record matches what shipped.

### Key Entities

- **Webhook endpoint**: a customer-configured destination. Belongs to exactly one
  environment, carries a signing secret, a set of subscribed event types, and an
  enabled state.
- **Signing secret**: a per-endpoint credential, independently rotatable, never
  recoverable in plaintext from the platform.
- **Delivery**: one event bound for one endpoint. Has a bounded series of attempts
  and a terminal outcome — delivered, or dead-lettered.
- **Dead letter**: a delivery whose attempts were exhausted. Retained for a stated
  period, inspectable, replayable.
- **Dispatcher**: the service that consumes events, signs and posts them. Owns no
  database of its own.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader at `part3-ch4` can follow the chapter and receive a signed
  event at an endpoint of their own, using only the chapter.
- **SC-002**: A recipient can verify a delivery's signature using only the shared
  secret and the request, verified by an automated test that performs the
  verification independently of the signing code.
- **SC-003**: A delivery to a failing endpoint is attempted exactly six times on
  the stated widening schedule, verified by an automated test.
- **SC-004**: No retry occurs earlier than its scheduled delay, verified by an
  automated test.
- **SC-005**: A pending retry survives a restart of the dispatching process,
  verified by an automated test.
- **SC-006**: An event whose attempts are exhausted is retrievable from the
  dead-letter store and can be replayed, verified by an automated test.
- **SC-007**: A slow endpoint does not delay deliveries to other endpoints,
  verified by an automated test.
- **SC-008**: An endpoint receives only its subscribed event types, verified by an
  automated test.
- **SC-009**: With the dispatcher stopped, messages are delivered to end users
  normally and the backlog drains on its return, verified by an automated test.
- **SC-010**: No environment can observe or affect another's endpoints, verified by
  the cross-tenant suite.
- **SC-011**: No signing secret appears in any log line or captured transcript,
  verified by an automated scan.
- **SC-012**: Every pre-existing suite passes unchanged in substance, the
  chapter-end lane counts are recorded, and the coverage run exits 0 with every
  ratchet intact.
- **SC-013**: Every `FR-*`/`NFR-*`/`DR-*`/`ADR-*` cited in the chapter exists in a
  source document, with zero invented identifiers.
- **SC-014**: Both locale paths are reachable and the listing shows 3.5 published
  and translated.

## Assumptions

- **The dispatcher is its own deployable service** (decided 2026-08-10). SAD §4.1
  specifies it as a separate component, and chapter 3.4's research R5 recorded
  that the question would be answered here. This makes 3.5 the first chapter since
  Part 1 to add a deployable — with its own build, container image, compose entry
  and CI job.
- **Constitution IV decides the ledger question; the plan does not.** "Only the
  API service writes to PostgreSQL… Other services obtain writes and backfill
  reads via the API service's internal endpoints." The dispatcher therefore
  records what it has handled through an internal endpoint, not a direct write.
  The alternative — amending ADR-04 — is a constitutional act and is not this
  chapter's to take.
- **This is why the chapter's spine works.** 3.4's mechanism was a claim and an
  effect in one transaction. Here the effect is on a machine the platform does not
  own *and* the claim is across a service boundary. The pattern does not degrade;
  it stops applying, and the chapter is about what replaces it.
- **The chapter is narrowed to compensate for the service split.** The attempt log
  (FR-WHK-06) and auto-disable (FR-WHK-07) move to a follow-on chapter, because
  auto-disable needs continuous-failure history and that history is the attempt
  log — they are one piece of work, not two. Without this, 3.5 would carry
  endpoints, secrets, signing, a new deployable, retry tiers, a dead-letter store,
  an attempt log and an auto-disable rule, which is more than any chapter in the
  series has attempted.
- **`docs/07-tutorial-plan.md` needs amending** and FR-033 requires it. Part 3's
  remaining chapters shift: the follow-on chapter takes 3.6, limits and quotas
  becomes 3.7, and the isolation gauntlet becomes 3.8. Naming and numbering are
  the plan's to finalise.
- **The enabled state ships without the automatic rule.** An owner can disable an
  endpoint here; what disables one automatically is the follow-on chapter's. The
  state exists now so that chapter adds a rule rather than a migration, and manual
  pause is a real capability in its own right.
- **Email notification is deferred with its own owner.** FR-WHK-07 asks that the
  organisation be notified by email. The workspace has no email infrastructure and
  no chapter has introduced any. Introducing a mail provider as a side effect of a
  webhook chapter is exactly what Principle VII forbids; FR-RTL-07 will need the
  same infrastructure, so it wants a home of its own.
- **`message.created` is still the only event with a producer.** FR-WHK-02 names
  eight types. The dispatcher filters by subscription and is built for the full
  set; only one type can currently be produced, and the chapter says so.
- **Coverage and CI are in force.** Feature 024's instrument exists and 3.4 was the
  first chapter measured by it. A new service means a new CI job and new coverage
  surface, both of which must be wired rather than left implicit.
- **Both locales ship together**, as 3.4 did.

## Out of Scope

- **The attempt log (FR-WHK-06) and auto-disable (FR-WHK-07)** — the follow-on
  chapter, provisionally 3.6.
- Email notification infrastructure — deferred, unowned, needed by FR-RTL-07 too.
- The dashboard's dead-letter inspection and replay screens, and the synthetic
  test-event button (FR-WHK-09) — Part 5.
- The 30-day analytical attempt log and its query surface — Part 4.
- Rate limiting and quotas, including per-endpoint delivery limits — limits and
  quotas chapter.
- The cross-tenant attack suite as a whole — the isolation gauntlet chapter (this
  chapter contributes its endpoints to it).
- Event types whose producers do not exist yet.
- Customer-facing SDK helpers for verifying signatures — chapter 5.1.
