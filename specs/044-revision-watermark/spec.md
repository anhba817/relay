# Feature Specification: A reconnecting client can tell it missed a revision

**Feature Branch**: `044-revision-watermark`

**Created**: 2026-09-06

**Status**: Draft

**Input**: User description: "build the watermark"

## Context

Resume is ordered by the channel sequence. A client reconnects with the highest sequence it
holds per channel, and receives everything above it. An edit or a deletion carries **the
sequence of the message it changes**, not a new one — so a message revised below the client's
cursor is in neither the replay nor the live stream, and **no sequence is consumed, so no gap
appears**.

Two published clauses already describe this exactly:

- **FR-016a** says a message older than the cursor that was edited or deleted during the
  absence must not be replayed, and the client's stale copy "MUST be repairable by re-reading
  that range of history."
- **FR-016b** says that limit must be documented rather than discovered, "including the fact
  that it produces no sequence gap and therefore trips no existing client-side detector."

**The repair exists and is documented. Nothing tells a client to perform it.** A client has no
reason to re-read history, so it does not, and it renders text that changed while it was away
for as long as that message stays on screen.

Two measurements taken before this specification was written decide its shape:

- **The window is routine, not exotic.** `docs/11-scalability-measurement-2026-09-06.md`
  measured the default connect limit at 3,000 per minute against a gateway that accepts
  1,125-1,675 per second. On a rolling restart the last client to reconnect waits **3 minutes
  20 seconds**. Every revision in that window, below that client's cursor, is permanently
  invisible to it. This is not an edge case reachable only by a client that goes offline for a
  day; it is what a deploy does.
- **The channel row is not on the revision path.** The send path already updates the channel
  row, so its activity column "costs an extra assignment rather than an extra round trip". The
  edit and delete paths touch the message and the edit history only. A per-channel signal
  therefore costs **one write per revision** — which is the right side of the trade, because
  revisions are rare and reconnects are not.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reconnecting client learns which channels changed behind it (Priority: P1)

A customer's client reconnects after a network drop or a platform restart. For every channel it
belongs to, it is told the current revision count. Where that count is higher than the one it
holds, it knows a message it already has was edited or deleted while it was away.

**Why this priority**: This is the whole feature. Everything else is a refinement of the signal
or the documentation of it. Without it the defect is silent, and silence is what makes it a
defect rather than a limit.

**Independent Test**: Connect a client, note a message. Disconnect it. Edit that message. Reconnect
and check that the channel reports a higher revision count than the client holds.

**Acceptance Scenarios**:

1. **Given** a client holding a message, **When** that message is edited while the client is
   disconnected and the client reconnects, **Then** the reconnect response reports a revision
   count for that channel higher than the one the client presented.
2. **Given** a client that was disconnected while nothing was revised, **When** it reconnects,
   **Then** the reported count equals the one it presented and no repair is indicated.
3. **Given** a message deleted rather than edited during the absence, **When** the client
   reconnects, **Then** the count rises exactly as it does for an edit — a deletion is a
   revision.
4. **Given** a client connecting for the first time with no stored count, **When** it connects,
   **Then** it is told the current count and no repair is indicated, because it holds nothing
   that can be stale.

---

### User Story 2 - The repair is bounded rather than total (Priority: P2)

A client that learns it missed revisions repairs only the channels that changed, and knows how
many revisions it missed in each.

**Why this priority**: A signal that says only "something, somewhere, changed" makes every
reconnect after a busy period a full refresh. The difference between "this channel changed" and
"something changed" is the difference between a bounded repair and a thundering herd — and the
herd would arrive at exactly the moment a rolling restart is already at its most loaded.

**Independent Test**: Belong to several channels, have one of them revised during an absence, and
check that the reconnect identifies that channel and not the others.

**Acceptance Scenarios**:

1. **Given** a client in several channels with revisions in one of them, **When** it reconnects,
   **Then** only that channel reports a raised count.
2. **Given** three revisions to one channel during an absence, **When** the client reconnects,
   **Then** the difference between the reported and presented counts is three.
3. **Given** a channel the client joined during its absence, **When** it reconnects, **Then**
   that channel's messages arrive by the ordinary replay and the channel is not reported as
   needing repair, because the client held nothing in it to be stale.

---

### User Story 3 - A client developer can find the obligation (Priority: P3)

Someone building against the public contract can read what the signal means and what to do
about it, without inferring it from behaviour.

**Why this priority**: The obligation is the client's, and an obligation nobody published is one
nobody meets. FR-016b already requires the limit to be documented; this extends that to the
remedy. It ships last because the signal has to exist before it can be described, and it is
separable work.

**Independent Test**: Read the published contract and implement the repair from it alone, without
reading platform source.

**Acceptance Scenarios**:

1. **Given** the published protocol documentation, **When** a developer reads the reconnect
   response, **Then** the revision count's meaning and the repair it implies are stated.
2. **Given** the published documentation, **When** a developer looks for what happens to a
   message revised below their cursor, **Then** they find it stated rather than implied.

---

### Edge Cases

- **A channel that has never been revised.** Reports a count of zero, which every client can
  compare against. Absent and zero must not be distinguishable in effect — a client that stores
  nothing is treated as holding zero.
- **A client that presents a count higher than the platform's.** Impossible unless a client
  fabricates one or a channel's history is rebuilt. Treated as "no repair needed" rather than as
  an error: a wrong repair signal is worse than a missing one, and refusing the connection over
  a number the client made up would be a denial of service the client controls.
- **A message revised more than once during one absence.** The count rises once per revision, so
  the client learns three edits happened rather than that one did. The repair is the same.
- **A revision to a message ABOVE the cursor.** Already covered by the ordinary replay, which
  reads current state — the count rises, and the repair the client performs is redundant but
  harmless. This feature does not attempt to distinguish the two.
- **A client with no channels.** Reports an empty set, exactly as the existing per-channel
  fields do.
- **A very long absence.** The count differs by a large number and the client re-reads history
  for that channel, which is bounded by the history endpoint's own paging rather than by this
  feature.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Every channel MUST carry a count of the revisions applied to its messages, where a
  revision is an edit or a deletion.
- **FR-002**: The count MUST rise by exactly one per revision, and MUST NOT fall.
- **FR-003**: The count MUST rise within the same transaction that applies the revision, so a
  revision that commits is never invisible to the count and a count that rises never describes a
  revision that did not commit.
- **FR-004**: A reconnecting client MUST be told the current count for every channel it belongs
  to.
- **FR-005**: A reconnecting client MUST be able to present the counts it holds, per channel.
- **FR-006**: A client presenting a count lower than the platform's for a channel MUST be able to
  determine that from the reconnect response alone, without a further request.
- **FR-007**: A client presenting no count MUST be treated as presenting zero, and MUST NOT be
  told a repair is needed on a first connection.
- **FR-008**: A client presenting a count higher than the platform's MUST be treated as needing
  no repair, and MUST NOT be refused.
- **FR-009**: The signal MUST be per channel. A single connection-wide indicator does not satisfy
  FR-006, because it cannot say which channel to repair.
- **FR-010**: The count MUST be comparable without reference to a clock, so that a client and the
  platform disagreeing about the time cannot produce a wrong repair decision in either direction.
- **FR-011**: Sending a message MUST NOT raise the count. A new message is delivered by the
  ordinary replay and is not a revision; raising the count for it would make every active channel
  report a repair after every absence.
- **FR-012**: The published protocol documentation MUST state what the count means and what a
  client does when it rises.
- **FR-013**: FR-016a's and FR-016b's clauses MUST be amended to name the signal, so the
  documented limit and the documented remedy are in the same place.
- **FR-014**: The reconnect path MUST NOT require a per-channel query per connection to produce
  the counts. At 10,000 connections a per-channel read per handshake is the cost this feature
  cannot pay.

### Key Entities

- **Channel revision count** — a per-channel, monotonically increasing whole number. Rises once
  per edit and once per deletion of any message in that channel. Never falls, never resets, and
  carries no meaning beyond "how many revisions this channel has seen".
- **Client-held count** — what a client last saw for a channel, presented on reconnect. Absent is
  equivalent to zero.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A client that missed a revision while disconnected can determine, from its reconnect
  alone, which of its channels hold revisions it has not seen — in 100% of cases where a revision
  occurred below its cursor.
- **SC-002**: A client that missed no revisions is told to repair nothing, in 100% of cases. No
  client performs a repair read it did not need.
- **SC-003**: The signal reports how many revisions were missed per channel, not merely that some
  were.
- **SC-004**: Reconnecting 10,000 clients stays within 10% of the rate measured before this
  feature — 1,125 to 1,675 connections per second — so the signal costs nothing a reconnection
  storm can feel.
- **SC-005**: Applying a revision stays within 10% of its current cost.
- **SC-006**: A developer can implement the repair from the published documentation alone,
  without reading platform source.
- **SC-007**: The two clauses that describe the limit also name the remedy, so a reader who finds
  one finds the other.

## Assumptions

- **The repair itself stays the client's**, as FR-016a already says. This feature builds the
  trigger, not the repair: no revision is replayed and no reconciliation is pushed. Including
  revisions in the replay is a larger change with a cap to size, and it would need this signal as
  its overflow indicator regardless — so it is deliberately out of scope and better informed once
  a real client exists.
- **A counter rather than a timestamp.** FR-010 states the requirement; the assumption is that a
  counter satisfies it more simply than a clock does, and it also answers "how many" for free.
- **Per channel rather than per message.** Per-message precision would let a client repair
  exactly the messages that changed and needs an index on revision time to produce, which is the
  cost the larger change carries. Per-channel is one number and bounds the repair to a channel's
  history, which FR-016a already names as the repair.
- **The count is public.** It appears in a response a customer's client reads, so it is contract,
  not diagnostics, and it cannot be renamed later without a version.
- **Existing channels start at zero** rather than at a count reconstructed from history. Their
  revisions predate every client's stored count, so reconstructing one would tell every client to
  repair every channel on its first reconnect after the change ships.
- **The measurement's numbers are this machine's.** SC-004's range comes from one gateway on a
  28-core host with the load generator beside it. A deployment's absolute rate will differ; the
  10% is against a baseline re-measured on the same lane, not against these figures.

## Out of Scope

- Replaying revisions during resume, or any server-pushed reconciliation.
- A revision cursor at message granularity.
- Changing the connect rate limit, which the measurement showed is 25 times below the gateway's
  capacity. That is a separate product decision, recorded in SRS revision 1.9.
- The typing-expiry client obligation, which is blocked on the same missing protocol reference as
  FR-012 but is a different clause and a different fabric.
