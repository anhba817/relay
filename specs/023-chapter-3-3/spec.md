# Feature Specification: Tutorial Chapter 3.3 — The Outbox

**Feature Branch**: `023-chapter-3-3`

**Created**: 2026-08-08

**Status**: Draft

**Input**: User description: "Building part 3 chapter 3.3 english only"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Read chapter 3.3 and make every state change produce an event that cannot be lost (Priority: P1)

A reader arrives at the `part3-ch2` checkpoint with a platform that authenticates
two kinds of caller and writes messages durably. Nothing outside the request
knows a message happened. The reader wants webhooks, analytics and a live
dashboard eventually — all of which need an event per state change — and wants
to understand why the obvious way to produce one is wrong before being shown the
right one.

The chapter shows them the dual-write problem as a failure they can reproduce:
write the row, publish the event, crash in the gap, and watch a message exist
with no event to match it. It then builds the answer — the event row commits
inside the same transaction as the state change, and a separate relay moves it
to the broker — and re-runs the same crash to show the event surviving.

**Why this priority**: the chapter is the deliverable. It is also the first
chapter in the series where the *demonstration of the bug* is as important as
the fix: a reader who has not seen an event vanish has no reason to accept a
table, a relay loop and at-least-once delivery.

**Independent Test**: a reader at `part3-ch2` can follow the chapter to a
platform where killing the process between the commit and the publish loses
nothing, verified by running the chapter's own crash test.

**Acceptance Scenarios**:

1. **Given** a reader at `part3-ch2`, **When** they run the chapter's naive
   publish-after-commit demonstration and kill the process in the gap, **Then**
   they observe a committed message with no corresponding event, and the failure
   is silent — nothing errored.
2. **Given** the same reader after building the outbox, **When** they repeat the
   identical crash, **Then** the event is present in the outbox after restart and
   the relay publishes it, with no message left unaccounted for.
3. **Given** a running platform, **When** the broker is stopped, **Then** writes
   continue to succeed, events accumulate unpublished, and the relay drains them
   when the broker returns — without operator intervention.
4. **Given** a reader who wants to know why this is not simply "publish twice",
   **When** they read the chapter, **Then** they find the four options ADR-06
   considered, why publish-before-commit is worse than publish-after-commit, and
   why change-data-capture was rejected on operational-cost grounds rather than
   correctness.
5. **Given** a reader following the chapter, **When** they reach the end, **Then**
   they can state what "at-least-once" costs them and where the duplicate is
   absorbed.

---

### User Story 2 - The canonical code advances to tag `part3-ch3` (Priority: P2)

The repository gains an `outbox` table, an event written inside the message
transaction, a relay that drains it to the broker, and a test that proves the
crash-in-the-gap property rather than asserting it.

**Why this priority**: the chapter's fences must byte-match a repository that
runs. As in 3.1 and 3.2, the code is written and proven before the prose that
describes it.

**Independent Test**: at `part3-ch3` the Docker-free gate passes; with the stores
up every integration lane passes including chapter 2.8's journey; the crash test
fails when the outbox write is moved outside the transaction.

**Acceptance Scenarios**:

1. **Given** the schema at `part3-ch2`, **When** the migration is applied,
   **Then** an `outbox` table exists matching SAD §6.1 — id, subject, payload,
   created_at, published_at — with an index that makes "unpublished, oldest
   first" cheap.
2. **Given** a message written through either door (REST or socket), **When** the
   write commits, **Then** exactly one outbox row exists for it, because both
   doors share one write path.
3. **Given** a message write that fails after the outbox insert, **When** the
   transaction rolls back, **Then** no outbox row survives — the event and the
   state change share a fate.
4. **Given** unpublished outbox rows and two relay instances, **When** both run
   concurrently, **Then** no row is published twice by the pair, and neither
   blocks the other.
5. **Given** a relay that crashes after publishing but before marking a row
   published, **When** it restarts, **Then** the row is published again — and the
   chapter states this as the accepted cost, not a defect.
6. **Given** the suite at `part3-ch3`, **When** the outbox insert is deliberately
   moved outside the transaction, **Then** at least one test fails.

---

### User Story 3 - The chapter publishes in English, and the site stays honest (Priority: P3)

3.3 becomes reachable in English. The Vietnamese edition is honestly absent
rather than machine-translated, and the listing says so.

**Why this priority**: publication is mechanical once the chapter exists, but the
site must not claim a translation that does not exist.

**Independent Test**: the site builds; the English path returns 200 and the
Vietnamese 404; the listing shows 3.3 untranslated and 3.4–3.7 forthcoming; the
fence chain replays every published chapter with no drift.

**Acceptance Scenarios**:

1. **Given** the built site, **When** the English 3.3 path is requested, **Then**
   it returns 200 and every figure renders.
2. **Given** the built site, **When** the Vietnamese 3.3 path is requested,
   **Then** it returns 404.
3. **Given** the fence-chain check, **When** it runs, **Then** every fenced file
   in every published chapter replays onto the repository byte-for-byte.

---

### Edge Cases

- **The relay is behind.** Outbox depth grows faster than the relay drains. The
  chapter must say what is observable (depth) and what the operator would do,
  without building alerting this chapter does not own.
- **A payload that cannot be published.** A row whose subject or payload the
  broker rejects must not block every row behind it forever; the chapter must
  state what happens and, if the answer is "it retries indefinitely", say so
  plainly rather than implying a dead-letter path that does not exist yet.
- **Two relays, one row.** Competing relays must not double-publish through
  ordinary operation; the mechanism that prevents it must be visible in the query
  rather than assumed from timing.
- **The broker is down at startup.** The service must start and accept writes;
  an event spine that makes the write path unavailable has inverted the
  dependency the outbox exists to remove.
- **Ordering.** Two messages in one channel produce two events; the chapter must
  state whether their relative order is guaranteed at the broker, and not claim
  more than the design delivers.
- **A message that never gets an event.** The reconciliation question — how would
  anyone know? — must be answerable, because FR-ANL-06 will eventually demand it.

## Requirements *(mandatory)*

### Functional Requirements

**The chapter**

- **FR-001**: The chapter MUST be written in English at
  `/part-3/chapter-03/the-outbox` and MUST NOT ship a Vietnamese edition.
- **FR-002**: The chapter MUST demonstrate the dual-write failure as a
  reproducible run before presenting the outbox, and the demonstration MUST show
  the failure being silent — no error, no exception, just a missing event.
- **FR-003**: The chapter MUST record the options ADR-06 weighed (outbox,
  publish-after-commit, publish-before-commit, change-data-capture) and why the
  rejected ones were rejected, including why publish-before-commit is worse than
  publish-after-commit.
- **FR-004**: The chapter MUST state that delivery is at-least-once, name where
  the resulting duplicate is absorbed, and MUST NOT imply exactly-once.
- **FR-005**: The chapter MUST explain why this event path exists alongside
  chapter 2.6's Redis fan-out rather than replacing it, in terms of the two
  different guarantees (at-most-once live delivery, at-least-once durable events).
- **FR-006**: The chapter MUST carry a `DECISION` note for any shape it derives
  that no source document defines, and MUST NOT invent a requirement identifier.
- **FR-007**: The chapter MUST name what it does not build — subjects taxonomy,
  streams and durable consumers (3.4), webhook delivery (3.5), outbox pruning,
  and the reconciliation job FR-ANL-06 will need — each with the chapter that
  owns it.

**The code**

- **FR-008**: An `outbox` table MUST exist matching SAD §6.1's definition, with
  an index supporting "unpublished, oldest first".
- **FR-009**: Writing a message MUST insert exactly one outbox row in the same
  transaction as the message, through the single write path both doors share.
- **FR-010**: A rolled-back state change MUST leave no outbox row.
- **FR-011**: A relay MUST drain unpublished rows to the broker and mark them
  published, and MUST be safe to run as more than one instance without
  double-publishing through ordinary operation.
- **FR-012**: The relay MUST NOT be on the request path: a write MUST succeed
  while the broker is unavailable, and pending events MUST publish once it
  returns.
- **FR-013**: The event payload MUST carry a stable event identity that a
  consumer can deduplicate on.
- **FR-014**: The publishing destination MUST be replaceable without changing
  the code that produces events, so that ADR-02's broker choice stays a
  configuration decision.
- **FR-015**: An automated test MUST prove the crash-in-the-gap property by
  interrupting the process between commit and publish, rather than by asserting
  the property in prose.
- **FR-016**: The existing suites — including chapter 2.8's journey — MUST keep
  passing with their assertions unchanged in substance.
- **FR-017**: No credential, and no message body belonging to a tenant, MUST
  appear in any log line the relay emits.

**Publication and provenance**

- **FR-018**: Every code fence MUST byte-match the repository at this chapter's
  state, with amendments to previously-fenced files expressed as hunked diffs.
- **FR-019**: Every requirement identifier cited in the chapter MUST exist in
  `docs/04-srs.md` or `docs/05-sad.md`, and every table and column named in prose
  MUST exist in the schema.
- **FR-020**: The chapter MUST quote only measured output — transcripts, counts
  and timings from real runs.
- **FR-021**: If the work exposes a defect in an earlier chapter, it MUST be
  fixed forward in every locale that chapter has, and recorded.

### Key Entities

- **Outbox row**: an event awaiting publication. Carries a monotonic id, the
  subject it belongs on, the payload a consumer will read, the time it was
  created, and the time it was published (absent until it is). Lives below the
  tenant boundary; every row belongs to exactly one environment by virtue of its
  payload.
- **Relay**: the process that moves rows to the broker. Owns no state of its own;
  its progress is entirely visible in the table it drains.
- **Event**: what a consumer eventually receives. Has an identity stable across
  redeliveries, a subject, and a payload shaped by the state change that produced
  it.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A reader at `part3-ch2` can follow the chapter and reproduce both
  runs — the lost event and the surviving one — using only the chapter.
- **SC-002**: Killing the process between commit and publish loses zero events,
  verified by an automated test.
- **SC-003**: The naive implementation the chapter demonstrates loses at least
  one event under the same test, verified by running it.
- **SC-004**: A rolled-back write leaves zero outbox rows, verified by an
  automated test.
- **SC-005**: Both doors (REST and socket) produce exactly one event per message,
  verified by an automated test.
- **SC-006**: Two concurrent relays publish every row exactly once through
  ordinary operation, verified by an automated test.
- **SC-007**: With the broker stopped, writes continue to succeed and events
  accumulate; when it returns, the backlog drains without intervention, verified
  by an automated test.
- **SC-008**: Every pre-existing suite passes unchanged in substance, and the
  chapter-end lane counts are recorded.
- **SC-009**: Every `FR-*`/`NFR-*`/`DR-*`/`ADR-*` cited in the chapter exists in a
  source document, with zero invented identifiers.
- **SC-010**: The English chapter is reachable and the Vietnamese path returns
  404, with the listing showing 3.3 untranslated.

## Assumptions

- **The broker is already in the stack.** `compose.yaml` has run NATS with
  JetStream and file storage since Part 1, so this chapter connects to a broker
  that exists rather than introducing one.
- **3.4 owns the consumer side.** Per `docs/07`, subjects taxonomy, stream
  configuration, durable pull consumers and the first consuming service belong to
  chapter 3.4. This chapter publishes; nothing consumes yet, and the chapter says
  so.
- **`message.created` is the only event with a real producer today.** FR-WHK-02
  names eight event types, but the platform's only public state change is a
  message write. The chapter emits that one and shapes the envelope for the rest
  rather than inventing producers for state changes no route can make yet.
- **The relay lives inside the api service**, per ADR-06's decision ("a small loop
  inside the API service initially, promotable to its own deployment"). Promoting
  it is a later operational decision, not this chapter's.
- **The outbox table is documented.** Unlike 3.1's tenancy containers and 3.2's
  key table, SAD §6.1 defines `outbox` — so the schema is quoted, not derived,
  and any addition to it (such as an index) is the only part needing a DECISION.
- **Pruning is named, not built.** ADR-06 calls deleting published rows "trivial"
  and it needs a scheduler this platform does not have; it is named as deferred.
- **English only.** No Vietnamese edition is produced. Existing translated
  chapters keep their fences mirrored.
- **Coverage tooling and CI remain absent.** The feature that adds them was
  scheduled after 3.2; if it has not run before this chapter, constitution VI's
  branch-coverage bar is unmeasurable here for the third recorded time.

## Out of Scope

- Subjects taxonomy, stream configuration, durable pull consumers, and the first
  consuming service (chapter 3.4).
- Webhook delivery, signing, retry tiers and dead-lettering (chapter 3.5).
- The analytics ingester and ClickHouse (Part 4).
- Outbox pruning and the FR-ANL-06 reconciliation job.
- Promoting the relay to its own deployable service.
- Emitting the remaining FR-WHK-02 event types whose state changes have no route
  yet.
