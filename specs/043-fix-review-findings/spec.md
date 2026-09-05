# Feature Specification: Fix the platform implementation review's findings

**Feature Branch**: `043-fix-review-findings`

**Created**: 2026-09-05

**Status**: Draft

**Input**: User description: "Fix the review"

## Context

`docs/09-platform-implementation-review-2026-09-03.md`, refreshed 2026-09-05, records ten
current findings, three roadmap items and eight amendment concerns against `part3-ch24`.
Every current finding cross-references an item in `specs/041-chapter-3-23/gaps.md` or
`specs/042-chapter-3-24/gaps.md`, so each already has evidence and an owner. This feature
closes the ones that are defects or contract gaps and states plainly which are deferred and
why.

Two things were checked before this specification was written, and one of them changed it:

- **The review's "bot sends bypass quota exhaustion" finding is wrong.**
  `assertWithinQuota` throws on the message hard cap before it consults whether the sender
  is a person; the sender test only short-circuits the unique-active-persons ceiling, 45
  lines later, which is what FR-RTL-05 says after chapter 3.17 narrowed it. A bot's send is
  refused exactly like a person's when the message quota is exhausted, and it is metered
  either way. Correcting the review is in scope; changing the quota code is not.
- **Every file these fixes touch is fenced by a published chapter** — `repository.ts` by 23
  of them, `codes.ts` by 10, `internal.ts` by 11. Part 3 is closed, so no chapter teaches
  these changes and each one costs an amendment hunk in
  `relay-tutorial/fences/post-series.md`. That is a cost, not an obstacle, and it is why
  the work is grouped by file rather than by finding.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A contributor can trust what the test lanes report (Priority: P1)

A contributor runs the integration lane and gets a result that reflects the product rather
than the order the test runner happened to choose or how much debris previous runs left in
the broker. A contributor with no containers running runs the unit lane and gets a result
that reflects the product rather than the absence of Redis. **And where the platform makes a
claim about concurrent writes, the lane can see whether it holds** — a lane that reports the
product has to be able to reach the product's harder states, not only its quiet ones.

**Why this priority**: Every other story's evidence is this lane's exit code. The most
recent measurement is 9 green of 20, where 10 of the 11 failures are one harness defect and
the pass rate alternates with a cache file. Fixing product code first means validating it
with an instrument known to be wrong.

**Independent Test**: Run twenty consecutive integration runs from a cleared lane with the
runner's result cache deleted first, and count failures attributable to harness resource
collisions. Run the unit lane with every container stopped and check the exit code. Force a
concurrent edit and deletion of one message from two clients and check that both orderings
end in a tombstone.

**Acceptance Scenarios**:

1. **Given** a lane whose previous suite has just stopped its child processes, **When** the
   next suite starts its own, **Then** the next suite binds its ports successfully rather
   than reaching a predecessor that is still exiting.
2. **Given** twenty consecutive integration runs, **When** the runs complete, **Then** no
   failure is attributable to a port collision or to accumulated broker state.
3. **Given** a machine with no containers running, **When** the unit lane runs, **Then** it
   exits zero.
4. **Given** an integration run that has completed, **When** the broker is inspected, **Then**
   the run has left no durable consumers behind.
5. **Given** a lane in any accumulated state, **When** an operator asks to reset it, **Then**
   one documented command clears the broker and the stale delivery rows.
6. **Given** an edit and a deletion of one message driven from two separate clients, **When**
   they interleave in either order, **Then** the message ends as a tombstone, and a test
   asserts it rather than the claim resting on reasoning.

---

### User Story 2 - A customer's client is refused at the boundary it wrote to (Priority: P2)

A developer integrating over the public WebSocket gets the same message-length rule the REST
API publishes, at the socket, in a refusal that names the field. A customer storing a user
profile cannot store a URL scheme their own client would execute.

**Why this priority**: These are the two findings the review rates High, and both are on the
surface an untrusted client reaches directly. Neither depends on any other story.

**Independent Test**: Send an over-long text on each of the three send paths and compare the
refusals. Attempt to store an avatar URL with a non-web scheme.

**Acceptance Scenarios**:

1. **Given** a socket client, **When** it sends a message whose text exceeds the published
   maximum, **Then** it is refused by the gateway with a registered error code that names
   the field, without an internal request being made.
2. **Given** the three send entry points, **When** each is given the same over-long text,
   **Then** all three refuse it and the published maximum is defined in exactly one place.
3. **Given** a profile update, **When** the avatar URL's scheme is not `http` or `https`,
   **Then** the update is refused and names the field.
4. **Given** a profile update whose avatar URL uses `https`, **When** it is submitted, **Then**
   it is accepted.

---

### User Story 3 - A customer can tell their own mistake from the platform's (Priority: P2)

A customer who misconfigures a webhook endpoint gets an error that says what they got wrong.
A customer who subscribes to an event type Relay does not emit finds out when they subscribe,
not by waiting for deliveries that never come. A customer whose socket is closed can look up
the close code.

**Why this priority**: Same public surface as story 2 and the same class of defect — a
refusal that misattributes the fault — but each one costs a new error code or a documentation
section, so it is separable work.

**Independent Test**: Submit each malformed webhook configuration and read the code in the
response body rather than the status. Subscribe to a misspelled event type. Look up each
close code in the published error reference.

**Acceptance Scenarios**:

1. **Given** a webhook endpoint configuration that is malformed, non-HTTPS, private-address,
   or carries an empty event set, **When** it is submitted, **Then** the response body names
   a specific error code rather than reporting that Relay failed.
2. **Given** a webhook subscription naming an event type Relay does not emit, **When** it is
   submitted, **Then** it is refused and the response names the accepted set.
3. **Given** every close code the platform can send, **When** a customer looks it up in the
   published error reference, **Then** each one is documented and distinguishable by cause.
4. **Given** a new close code added later, **When** the documentation gate runs, **Then** it
   fails until that code is documented.

---

### User Story 4 - A reader of the records finds them true (Priority: P3)

Someone reading the specification's revision history, the review, or the migration directory
finds a record that matches the tree.

**Why this priority**: No customer-visible behaviour depends on it, and none of it blocks
another story. It is cheap, and two of the items are wrong statements in published
documents.

**Independent Test**: Read the SRS revision ledger top to bottom. Read the review's quota
finding against the code it cites. Ask the repository which migration workflow applies and
check that no tool contradicts the answer.

**Acceptance Scenarios**:

1. **Given** the specification's revision history, **When** it is read in file order, **Then**
   the version column ascends.
2. **Given** a revision entry inserted out of order, **When** the documentation gate runs,
   **Then** it fails.
3. **Given** the review's quota finding, **When** it is read against `assertWithinQuota`,
   **Then** the document states what the code does.
4. **Given** the migration tooling decision, **When** a contributor next adds a table, **Then**
   the repository states which workflow to follow and the tooling matches that statement.

---

### Edge Cases

- **Stored values that the new validation would reject.** Existing rows hold avatar URLs and
  webhook event-type sets written before these rules. Validation applies to writes; existing
  rows are counted and reported, not rewritten, because rewriting a customer's stored value
  is a decision this feature does not own.
- **A subscription to an event type that exists in the requirement but is not yet emitted.**
  Five of the eight event types named in FR-WHK-02 are emitted today. The accepted set is
  what the platform emits, so a subscription to a named-but-unbuilt type is refused — and the
  refusal must say so, because that customer has not made a typo.
- **A socket text bound changes which refusal a client sees.** Applying the bound at the
  gateway moves the refusal one hop earlier, so the code on the wire changes for that case.
  The client must still receive a registered code and a named field.
- **A close code documented under a heading the existing checker rejects.** That checker
  fails on any section heading that is not a member of the error-code registry, so close
  codes are documented inside the entry of the error that carries them.
- **A test file that moves between lanes.** Its published listings are anchored to its path,
  so moving it retires one chain and joins another.

## Requirements *(mandatory)*

### Functional Requirements

**Grouped by story, not by number.** FR-024, FR-024a, FR-026 and FR-027 sit in the Verification
block because that is the story that delivers them, so the identifiers do not ascend down the
page. The grouping is the index; the numbers are only keys.

#### Verification (Story 1)

- **FR-001**: The end-to-end harness MUST wait for each child process to exit, within a
  bounded timeout, before reporting that it has stopped them.
- **FR-002**: The end-to-end harness MUST obtain a port that no other process holds, rather
  than a fixed number or a value drawn at random from a fixed range.
- **FR-003**: Every integration suite that creates a durable subscription MUST delete it when
  the suite finishes.
- **FR-004**: An integration suite MUST NOT be prevented from observing its own published
  events by messages left in the broker by earlier runs.
- **FR-005**: The repository MUST provide one documented command that returns the test lane to
  an empty state.
- **FR-006**: Every test in the container-free lane MUST pass with no containers running.
- **FR-006a**: The container-free lane MUST still exercise the logic that needs no broker.
  **FR-006 alone is satisfiable by emptying the lane** — moving every test out makes it pass —
  so the assertions that need no broker stay, and the coverage the moved assertions provided
  must still be provided from somewhere.
- **FR-007**: Concurrent editing and deletion of one message MUST have a test that forces the
  interleaving and asserts the outcome.
- **FR-024**: Every assertion that needs a running broker MUST live in the lane that runs with
  containers, and every assertion that does not MUST remain in the container-free lane.
- **FR-024a**: The split MUST be decided per assertion, and each assertion that moves MUST keep
  the behaviour it asserted.
- **FR-026**: The lane's port allocation MUST be recorded where the next reader looks for it,
  and every lane that binds a port MUST appear in that record. **The record is currently wrong
  by omission**: it registers a range to one file and does not mention the lane that hard-codes
  three ports inside it.


#### Cross-cutting (every story)

- **FR-027**: Published material this feature falsifies MUST be amended in the same phase that
  falsifies it. This covers material no gate can check — a transcript of a run, a table of port
  allocations, a paragraph describing behaviour — and it applies per story rather than once at
  the end, because the phase that breaks a claim is the phase that knows it.

**Filed here rather than under a story, because three stories deliver it** — T018a in US1,
T030 in US2 and T043 in US3. A requirement carrying one story's label while three stories
discharge it is a label that misleads, which analysis pass 1 found for FR-024 and pass 3
reintroduced here.

#### Public boundary (Story 2)

- **FR-008**: The maximum message text length MUST be defined once and applied by every entry
  point that accepts message text.
- **FR-009**: A message whose text exceeds the maximum MUST be refused at the entry point that
  received it, without a request to another service.
- **FR-010**: A refusal for over-long text MUST carry a registered error code and name the
  field.
- **FR-011**: A stored avatar URL MUST use a scheme the platform accepts, determined by
  parsing the URL rather than by matching its text.
- **FR-012**: The accepted avatar URL schemes MUST be `http` and `https`, and nothing else.
- **FR-013**: The count of stored rows that the new avatar rule would reject MUST be measured
  and recorded before the rule ships.

#### Customer-caused refusals (Story 3)

- **FR-014**: Every webhook configuration refusal caused by customer input MUST carry an error
  code that identifies the cause, and MUST NOT report an internal failure.
- **FR-015**: Each new error code MUST have a section in the published error reference reachable
  from the code's documentation link.
- **FR-016**: A webhook subscription MUST be refused if it names an event type the platform does
  not emit, and the refusal MUST name the accepted set.
- **FR-017**: The count of stored subscriptions that the new event-type rule would reject MUST
  be measured and recorded before the rule ships.
- **FR-018**: Every close code the platform can send MUST be documented in the published error
  reference, distinguishable by cause.
- **FR-019**: A gate MUST fail when a close code exists in the platform and not in the published
  error reference.

#### Records (Story 4)

- **FR-020**: The specification's revision history MUST list entries in ascending version order.
- **FR-021**: A gate MUST fail when a revision entry is out of order, **and it MUST read this
  feature's own success criteria as well as the specification's revision ledger.** This list was
  written out of order while the gate against out-of-order lists was being specified; a rule
  worth enforcing on a published document is worth enforcing on the document demanding it.
- **FR-022**: The review's finding about bot sends and quota exhaustion MUST be corrected to
  state what the code does.
- **FR-023**: The repository MUST state that migrations are hand-written and reviewed against
  the published schema, and MUST NOT retain a generator whose output contradicts that statement.
- **FR-023a**: A check MUST fail if the retired generator's snapshot directory or its build step
  returns.
- **FR-025**: The published requirement for membership revocation MUST state the bound that
  applies when the real-time fabric is unavailable, and that bound MUST match what the platform
  does.
- **FR-025a**: The published requirement for the connection limit MUST state that the limit is
  enforced on a best-effort basis and what happens when it cannot be checked.
- **FR-025b**: Each amendment MUST record which architecture decision already carried the
  behaviour, so a reader can find the argument rather than only the outcome.
- **FR-025c**: Neither amendment MUST weaken a clause beyond what the platform already does
  today; the measured behaviour is the upper bound on what the clause may permit.

### Key Entities

- **Finding**: One row of the review. Carries a priority, a cited location, and a
  cross-reference to a gaps item that holds its evidence.
- **Gaps item**: The durable record of a known defect, with an owner and a measurement. This
  feature closes some and re-points the rest.
- **Published listing chain**: The sequence of listings across chapters that reconstructs one
  file. Any change to a file that has one requires an amendment.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Twenty consecutive integration runs, started from a cleared lane with the
  runner's result cache removed, produce zero failures caused by port collisions or by state
  left behind by earlier runs.
- **SC-002**: The container-free lane exits zero on a machine with no containers running, **and
  the file that moves keeps the five assertions measured to need no broker**: a slot released
  that was never held, a release with nothing held, the unenforced answer when the registry
  cannot be reached, the heartbeat bound, and the single-definition check. Any file whose
  coverage pin was met before MUST still meet it.
- **SC-003**: An integration run creates no durable subscription that outlives it. Durables a
  service creates in normal operation are not test debris and are counted separately.
- **SC-004**: A client sending over-long message text is refused at every entry point, and the
  maximum appears in exactly one place in the published contract.
- **SC-005**: No avatar URL with a scheme other than `http` or `https` can be stored.
- **SC-006**: Every refusal a customer can cause by misconfiguring a webhook carries a code
  that names the cause, verified by a test that reads the code rather than the status.
- **SC-007**: Every close code the platform can send is documented, and the count of documented
  close codes equals the count the platform defines.
- **SC-008**: A misspelled event type is refused at subscription time rather than producing an
  endpoint that never fires.
- **SC-009**: The specification's revision history reads in ascending order, and a gate fails
  if that stops being true.
- **SC-010**: Every statement in the review matches the code or document it cites.
- **SC-011**: No published requirement describes behaviour the platform does not have, measured
  by reading each amended clause against the behaviour it now states.
- **SC-012**: The integration lane completes inside its published budget after the changes, or
  the budget is raised with the measurement that justifies it. **The changes cost time**: a
  teardown that waits for a process to exit is slower than one that sleeps a fixed 200 ms, and a
  suite that boots twice to prove the teardown works is a suite the lane did not run before. The
  most recent battery's slowest green run left 5.39 seconds of headroom.
- **SC-013**: Every finding in the review is marked with what happened to it — closed, and by
  what; or open, and whose it is. **A reader of the review learns the feature's outcome from the
  review**, not by cross-referencing a task list.

## Assumptions

- **The three roadmap rows are out of scope.** Self-service tenancy and the dashboard,
  analytics and compliance lifecycle, hosted media, emoji packs, the SDK, the reference client,
  and the public protocol reference and OpenAPI document are scheduled in
  `docs/07-tutorial-plan.md` as Part 4 and later. Listing them as findings is fair; scheduling
  them here would double-book work another plan already owns.
- **The moderation audit log is out of scope for the same reason.** FR-MOD-03 is chapter 4.7's
  row. What this feature owes it is an accurate gaps entry, not an implementation.
- **Validation applies to new writes.** Rows already stored that a new rule would reject are
  counted and reported. Rewriting them is a separate decision with a customer-visible effect.
- **Concurrent edit and delete keep their current behaviour.** Both orderings end in a
  tombstone, which the existing record already establishes; what is missing is the test, and
  FR-007 asks only for the test.
- **The five amendment concerns not named in a requirement are deferred with a reason**: the
  client-side typing expiry needs a published client contract that does not exist yet; missed
  revisions need a repair trigger that is a protocol change; consolidating the real-time
  subject grammars needs a scale measurement that has never been taken; and the duplication of
  architecture decisions across two hand-maintained documents is a tooling change with no
  behavioural effect. Each stays in the gaps record with its owner.
- **This feature publishes no chapter.** Part 3 is closed and no chapter teaches these fixes,
  so the changes land as amendments to the published listings rather than as new teaching
  material.
- **The two clause amendments are corrections, not concessions.** Both architecture decisions
  already state the behaviour and the arithmetic behind it; the clauses predate the fabric they
  describe. Amending them makes the documents true today and forecloses nothing — hardening
  either one later is a change to the platform and a further amendment, in that order.
- **Retiring the migration generator removes a tool, not a control.** The review of generated
  SQL against the published schema has been the control since chapter 3.9, and every migration
  since has been hand-written. The generator's snapshots have been wrong for five chapters and
  nothing depended on them.
- **The full gate set is fourteen commands, not eleven.** Type checking, linting and building
  the platform belong in it; chapter 3.24 tagged a tree that failed linting because they were
  missing from its list.
