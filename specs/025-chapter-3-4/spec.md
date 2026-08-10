# Feature Specification: Tutorial Chapter 3.4 — JetStream and the First Consumer

**Feature Branch**: `025-chapter-3-4`

**Created**: 2026-08-09 (implemented) · **Reconstructed**: 2026-08-10

**Status**: Implemented — artifacts reconstructed after hardware loss

**Input**: User description: "Building part 3 chapter 3.4"

> **Provenance.** The chapter shipped on 2026-08-09 (`relay-tutorial@2e5f3e3`,
> both locales). The machine holding the unpushed `relay-platform` work and this
> spec directory failed before either was pushed. The platform code was
> reconstructed from the chapter's own fences — 9 unified diffs that applied
> with zero fuzz and 8 whole-file listings — and verified against both lanes and
> the chapter's checkpoint numbers. **These artifacts are written after the
> fact**, from the shipped chapter and the verified code, rather than before
> implementation as the series' practice requires. Where a decision's *reason*
> survives only in a code comment or the prose, this document says so rather
> than inventing a deliberation. See `chapter-notes.md` for what the
> reconstruction could and could not recover.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read chapter 3.4 and make the events readable, exactly once (Priority: P1)

A reader arrives at the `part3-ch3` checkpoint with a platform that commits an
event beside every message and a relay that moves it to a broker. Nothing has
ever read one. The stream holds twelve thousand events, three of whose settings
were chosen by a person and the rest inherited from whatever NATS does when you
do not say.

The chapter closes both halves. Every stream setting becomes a decision with a
reason attached, and the stream gets its first reader — which reintroduces, one
hop further along, exactly the failure chapter 3.3 spent a chapter removing.
Between doing the work and admitting it there is a window, and a process that
dies in that window has done work the broker will hand out again.

**Why this priority**: the chapter is the deliverable. It is also the chapter
where the reader learns that the outbox did not *remove* the dual-write problem —
it moved it — and that the answer on the receiving end is not a better protocol
but a ledger.

**Independent Test**: a reader at `part3-ch3` can follow the chapter to a
platform where killing a consumer between the effect and the acknowledgement
results in a redelivery that is handled exactly once, verified by running the
chapter's own kill test.

**Acceptance Scenarios**:

1. **Given** a reader at `part3-ch3`, **When** they ask the broker what it is
   holding, **Then** they find a stream whose retention, size bound, age bound
   and duplicate window nobody chose, and the chapter names which three settings
   were deliberate.
2. **Given** the reader after applying the chapter's configuration, **When** they
   read the stream back from the broker, **Then** every setting matches what was
   asked for, and applying the same configuration a second time is a no-op rather
   than an error.
3. **Given** a running consumer, **When** it is killed between committing its
   effect and acknowledging the message, **Then** the broker redelivers, the
   handler does not run a second time, and the ledger still records exactly one
   handling.
4. **Given** two api instances started together, **When** both run the same
   durable consumer, **Then** they divide the stream between them rather than
   each receiving everything.
5. **Given** a reader who wants to know why the broker's own duplicate window is
   not the answer, **When** they read the chapter, **Then** they find why a
   window measured in hours is not a safe guess and where the guarantee actually
   belongs.
6. **Given** a reader following the chapter, **When** they reach the end, **Then**
   they can state what happens to a message that exhausts its delivery attempts,
   and that nothing catches it yet.

---

### User Story 2 - The canonical code advances to tag `part3-ch4` (Priority: P2)

The repository gains a deliberately configured stream, a subject grammar both
sides share, a durable pull consumer with deduplication built into the runtime
rather than left to the handler, and twelve invariants that hold.

**Why this priority**: the chapter's fences must byte-match a repository that
runs. As in 3.1, 3.2 and 3.3, the code is written and proven before the prose.

**Independent Test**: at `part3-ch4` the Docker-free gate passes; with the stores
up every integration lane passes including chapter 2.8's journey; removing the
ledger claim from the runtime fails three of the ten broker-backed invariants.

**Acceptance Scenarios**:

1. **Given** the stream at `part3-ch3`, **When** the chapter's configuration is
   applied, **Then** every setting reads back from the broker as configured, and
   the two settings that are immutable on an existing stream are carried through
   untouched rather than resubmitted.
2. **Given** two api instances starting together, **When** both apply the stream
   configuration, **Then** the second is a no-op and neither errors.
3. **Given** a consumed event, **When** the handler returns, **Then** exactly one
   ledger row records it, written in the same transaction as the effect.
4. **Given** a consumer killed between the effect and the acknowledgement,
   **When** the broker redelivers, **Then** the handler runs zero further times
   and the ledger still says one.
5. **Given** a handler that always throws, **When** it has thrown on every
   permitted attempt, **Then** the broker stops delivering and the chapter says
   plainly that nothing catches what falls out.
6. **Given** a payload that cannot be parsed, **When** it is delivered, **Then**
   it is terminated on the first attempt rather than consuming every attempt to
   reach the same conclusion.
7. **Given** the suite at `part3-ch4`, **When** the ledger claim is removed from
   the runtime, **Then** at least three broker-backed invariants fail.

---

### User Story 3 - The chapter publishes in English and Vietnamese (Priority: P3)

3.4 becomes reachable in both locales. Unlike 3.3, which shipped English-only and
was translated afterwards, this chapter ships with its Vietnamese edition.

**Why this priority**: publication is mechanical once the chapter exists, but the
listing must match what is actually reachable, and a translated chapter's fences
must mirror the English ones exactly.

**Independent Test**: the site builds; both locale paths return 200; the listing
shows 3.4 published and translated; the fence chain replays every published
chapter with no drift.

**Acceptance Scenarios**:

1. **Given** the built site, **When** the English 3.4 path is requested, **Then**
   it returns 200 and all three figures render.
2. **Given** the built site, **When** the Vietnamese 3.4 path is requested,
   **Then** it returns 200 and its fences match the English chapter's byte for
   byte.
3. **Given** the fence-chain check, **When** it runs, **Then** every fenced file
   in every published chapter replays onto the repository byte-for-byte.

---

### Edge Cases

- **A setting that cannot be changed.** Retention and storage are fixed once a
  stream exists. The chapter must state which settings are immutable and what the
  broker does when you try — an error it refuses, not a difference it reconciles.
- **Two instances, one configuration.** Two api processes start together and both
  apply the stream configuration. The second must be a no-op, not a race.
- **Two instances, one durable.** A durable name is a position in the stream.
  Two consumers sharing one must divide the work rather than each receiving
  everything, and neither may create a second position by accident.
- **A message that will never parse.** The same bytes fail the same way every
  time. It must not consume every delivery attempt before being dropped anyway,
  and it must not write a ledger row it could never earn.
- **A handler that always throws.** Delivery attempts are bounded, so the message
  eventually leaves the consumer's view. The chapter must say where it goes —
  which today is nowhere — rather than imply a dead-letter path that does not
  exist.
- **An effect that cannot be rolled back.** The ledger and the effect share a
  transaction only because the effect is in Postgres. Chapter 3.5's dispatcher
  calls a customer's HTTP endpoint and cannot. The limit must be stated here, in
  the chapter that establishes the pattern.
- **The broker is unreachable at startup.** The consumer must not take the write
  path down with it; the api starts and serves writes with no broker.

## Requirements *(mandatory)*

### Functional Requirements

**The chapter**

- **FR-001**: The chapter MUST be written at
  `/part-3/chapter-04/jetstream-and-the-first-consumer` and MUST ship both an
  English and a Vietnamese edition whose fences match byte for byte.
- **FR-002**: The chapter MUST show the stream's inherited defaults before
  changing them, and MUST distinguish the settings chapter 3.3 chose from the
  ones NATS supplied.
- **FR-003**: Every stream setting the chapter applies MUST carry a reason, and
  any setting derived from no source document MUST carry a `DECISION` note.
- **FR-004**: The chapter MUST demonstrate the consumer's gap — the window
  between doing the work and acknowledging it — as a reproducible run rather than
  a description.
- **FR-005**: The chapter MUST state that the broker's own duplicate window is
  not the deduplication guarantee, and name where the guarantee actually lives.
- **FR-006**: The chapter MUST state what happens to a message that exhausts its
  delivery attempts, including that nothing catches it yet.
- **FR-007**: The chapter MUST name the limit of the shared-transaction pattern —
  that it requires the effect to be transactional — and name the chapter that
  meets that limit.
- **FR-008**: The chapter MUST name what it does not build: webhook delivery and
  its dead-letter store (3.5), the analytics ingester (Part 4), ledger pruning,
  and the reconciliation job FR-ANL-06 will need.

**The code**

- **FR-009**: Every setting on the `EVENTS` stream MUST be applied deliberately,
  and applying the configuration MUST be idempotent — safe for two instances
  starting together.
- **FR-010**: Settings that are immutable on an existing stream MUST be carried
  through rather than resubmitted, so that applying a configuration to a stream
  that already exists does not fail.
- **FR-011**: Stream replication MUST be derived from the environment rather than
  hardcoded, so that the local single node and ADR-02's R3 production target are
  both reachable without editing code.
- **FR-012**: The event subject grammar MUST live in the package both the
  producing and consuming sides share, and MUST be built in exactly one place.
- **FR-013**: A consumer MUST deduplicate on event identity, and the runtime —
  not the handler — MUST be what enforces it (SAD risk R5).
- **FR-014**: The deduplication claim and the handler's effect MUST commit in one
  transaction, so that a handler that throws leaves no claim behind.
- **FR-015**: A handler MUST have no way to acknowledge, negatively acknowledge,
  retry, deduplicate, or see the raw message. It returns, or it throws.
- **FR-016**: A payload that cannot be parsed MUST be terminated on its first
  delivery rather than retried, and MUST NOT write a ledger row.
- **FR-017**: Delivery attempts MUST be bounded, and back-pressure MUST bound the
  quantity of unacknowledged work a stalled consumer can accumulate.
- **FR-018**: The consumer MUST connect lazily: an unreachable broker MUST leave
  the api serving writes.
- **FR-019**: An automated test MUST prove the redelivery property by killing the
  process between the effect and the acknowledgement, rather than by asserting it
  in prose.
- **FR-020**: The existing suites — including chapter 2.8's journey and 3.3's
  outbox suite — MUST keep passing with their assertions unchanged in substance.
- **FR-021**: No credential and no message body belonging to a tenant MUST appear
  in any log line the consumer emits.

**Publication and provenance**

- **FR-022**: Every code fence MUST byte-match the repository at this chapter's
  state, with amendments to previously-fenced files expressed as hunked diffs.
- **FR-023**: Every requirement identifier cited in the chapter MUST exist in
  `docs/04-srs.md`, `docs/05-sad.md` or `docs/06-adr-deep-dives.md`, and every
  table and column named in prose MUST exist in the schema.
- **FR-024**: The chapter MUST quote only measured output — transcripts, counts
  and timings from real runs.
- **FR-025**: Every file the chapter's own prose asserts the existence of MUST be
  fenced, so that the fence chain can replay it. *(Added in reconstruction: the
  shipped chapter violates this — see `chapter-notes.md` finding 1.)*

### Key Entities

- **Stream**: the durable log of events. Named `EVENTS`, covering `events.>`,
  file-backed. Two of its settings can never be changed once it exists; the rest
  are decisions this chapter makes.
- **Durable consumer**: a named position in the stream, shared by every instance
  using that name. Not a process — a cursor the broker keeps on the consumer's
  behalf.
- **Consumed-events ledger**: a record that a named consumer handled a given
  event id. Carries no tenant column, no event body, and no pruning. It is
  platform bookkeeping, like the outbox.
- **Handler**: what a consumer does with an event. Can return or throw, and
  nothing else. Its correctness comes from the runtime around it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader at `part3-ch3` can follow the chapter and reach a
  configured stream and a working consumer using only the chapter.
- **SC-002**: Every stream setting reads back from the broker exactly as
  configured, verified by an automated test.
- **SC-003**: A kill between handling and acknowledgement is redelivered and
  handled exactly once, verified by an automated test that sends a real signal.
- **SC-004**: Deduplication survives a process restart, verified by an automated
  test.
- **SC-005**: Two instances sharing a durable name divide the work, verified by
  an automated test.
- **SC-006**: A handler that always throws stops being retried after the bounded
  number of attempts, verified by an automated test.
- **SC-007**: An unparseable payload is terminated on the first attempt, verified
  by an automated test.
- **SC-008**: A consumer stopped for N publishes receives all N on restart,
  verified by an automated test.
- **SC-009**: No consumer log line contains a tenant's message body, verified by
  an automated test.
- **SC-010**: Applying the stream configuration twice is a no-op rather than an
  error, verified by an automated test.
- **SC-011**: Every pre-existing suite passes unchanged in substance, and the
  chapter-end lane counts are recorded.
- **SC-012**: Every `FR-*`/`NFR-*`/`DR-*`/`ADR-*` cited in the chapter exists in a
  source document, with zero invented identifiers.
- **SC-013**: Both locale paths are reachable and the listing shows 3.4 published
  and translated.

## Assumptions

- **The stream already exists.** Chapter 3.3 created it with a name, its subjects
  and file storage, and left everything else at NATS's defaults. This chapter
  configures a stream that exists rather than creating one — which is why the
  immutability of `retention` and `storage` is a finding rather than a footnote.
- **`message.created` is still the only event with a producer.** FR-WHK-02 names
  eight types; the platform has one public state change. The consumer reads the
  wildcard, so the remaining seven need no consumer change when they arrive.
- **The consumer lives inside the api service**, for the same reason ADR-06 put
  the relay there. Chapter 3.5's dispatcher is meant to be its own service and
  will need either an internal route for its ledger or an ADR amendment; that is
  named, not solved.
- **The first handler does almost nothing on purpose.** Every consumer the SAD
  names belongs to a later chapter. Giving this one a job would mean stealing
  3.5's subject or inventing product (Principle VII), so it records that an event
  arrived and the runtime around it carries the correctness.
- **Coverage tooling and CI now exist.** Feature 024 landed both after 3.3.
  Principle VI's bar is measurable here for the first time in Part 3 — see
  research R10 for what the measurement says about the code this chapter adds.
- **Both locales ship together.** 3.3 shipped English-only and was translated
  afterwards; by this chapter the Vietnamese edition is produced alongside.

## Out of Scope

- Webhook delivery, HMAC signing, retry tiers, dead-lettering and auto-disable
  (chapter 3.5).
- The analytics ingester and ClickHouse (Part 4).
- The dashboard's live stream (Part 5).
- Ledger pruning, and the FR-ANL-06 reconciliation job that compares message
  counts against handled events.
- Promoting the consumer to its own deployable service.
- A dead-letter store for messages that exhaust their delivery attempts.
