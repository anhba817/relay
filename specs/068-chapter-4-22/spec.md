# Feature Specification: chapter 4.22, "★ Milestone: the Priya test"

**Feature directory**: `specs/068-chapter-4-22/`
**Created**: 2026-10-05
**Chapter**: Part 4, movement VII, the third milestone and the last chapter of Part 4
**Source**: `docs/12-part-4-structure.md` row 23 · `docs/07-tutorial-plan.md` row 23 ·
`docs/03-journey-map.md` Journey 3 · `docs/04-srs.md` §7.3 Phase 3

**Name a chapter, never number it.** `docs/12` §3's table keeps pre-contraction
ordinals in column one on purpose: **row 23 is chapter 4.22**, one row after 4.21's.

---

## What this chapter is

Journey 3 — *Priya resolves a dispute* — made executable, as `tuan.itest.ts` made
Journey 4 executable at chapter 2.8. That file states the rule this chapter inherits:

> **the journeys are the milestones. These aren't metaphors — they are the
> integration suites, and they are the SRS phase exit criteria.**
> …Read the right margin: each step names the chapter that made it possible.
> **Remove that chapter's work and a named assertion here fails.**

A milestone verifies work other chapters did. Its product is a path walked end to
end, not a mechanism — and chapter 4.17 recorded what that is worth: *seven chapters
built the path and no test joined them, because every suite stood in for the step
beside it.* **Nothing in a codebase measures aggregates.**

## The premise check, measured before this was written

Journey 3's six stages, walked against the composed api on 2026-10-05.

| stage | what `docs/03` says Relay must provide | measured |
|---|---|---|
| 1 Ticket | external ids on users and channels | **200 / 201** |
| 2 Locate | **channel retrieval by external ID** | **500** — see below |
| 3 Reconstruct ★ | tombstones, edit history, sequence, history via API key | routes exist; see below |
| 4 Judge | unambiguous timestamps (CON-04) | human work |
| 5 Act | moderator delete, tenant ban, both in real time | **200** |
| 6 Record | audit log with request id; erasure receipt | **200**, `request_id` present |

**STAGE 2 IS THE HOLE AND IT IS NOT A MISSING FEATURE, IT IS A 500.**
`GET /v1/channels/{externalId}` answers **500** where `GET /v1/channels/{uuid}`
answers 200, because the route takes a uuid and an external id is not one — 058-3's
caller-triggered internal error, on the one route this journey opens with. And **no
SRS clause requires the lookup at all**: FR-CHN-01 creates a channel with a
customer-supplied identifier, FR-CHN-02 makes *creation* idempotent on it, FR-CHN-08
lists a user's channels. None of them says a channel can be read by it.

**THE ONLY WORKING RESOLUTION IS A WRITE.** Re-POSTing the create with the same
external id returns the same channel — measured, `same channel: True` — so a support
tool resolving `order-88412` today performs a channel creation. That satisfies the
journey's *"zero lookup tables"* and violates every expectation a reader has of a
lookup.

**AND AN APPLICATION CREDENTIAL CANNOT CREATE THE CONVERSATION IT INVESTIGATES.**
A send as a `person` is refused: *"an application credential may send only as a bot
user; name one in `user`"*. Priya's key moderates; the dispatcher and the driver need
their own tokens. The harness at `packages/e2e/src/harness.ts` already provides both.

**AND PHASE 3's EXIT CRITERION HAS AN ARROW NOBODY HAS WALKED.** SRS §7.3:
*"an image survives upload → scan → send → signed delivery → **erasure**"*. Chapter
4.17 demonstrated the first four and `docs/12` row 18 names exactly those four;
chapter 4.21 built erasure and never joined it to the image path.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Priya's Tuesday, executable (Priority: P1)

A support engineer resolves a dispute from the record alone: she finds the
conversation from an order number, reads what happened including what was edited and
what was deleted, removes abusive content, restricts its sender, and leaves a trail
an auditor can follow six months later.

**Why this priority**: it is the milestone. Every other story here exists because
walking this one exposes something.

**Independent test**: boot the system, seed a dispute, and run the six stages in
order with no database access and no engineering assistance.

**ONE SPLIT, STATED RATHER THAN GLOSSED.** *Priya's six stages* use only routes that
exist in production, with an application credential a customer really holds. *The
fixture that sets them up* mints user tokens through `POST /auth/dev-token`, which
404s outside a development environment — *"a development affordance that does not
exist in production"*, in its own words. It stands in for the customer's identity
provider, which is Part 2's subject and not something a sealed suite can exercise.

**Acceptance scenarios**

1. **Given** a channel created with external id `order-N`, **when** the support tool
   presents that external id, **then** it reaches the conversation without holding a
   lookup table of its own and without a 5xx.
2. **Given** a message edited eleven minutes after it was sent, **when** the history
   is read with an application credential, **then** the current text, the prior text
   and both timestamps are all present.
3. **Given** a message deleted by its author, **when** the history is read, **then**
   the deletion is visible in place and in order, distinguishable from a message that
   was never sent.
4. **Given** an abusive message and a connected recipient, **when** Priya deletes it,
   **then** the recipient's client is told, and the deletion is in the audit log with
   the request id of the call that made it.
5. **Given** the ban of its sender, **when** that user attempts to connect or send,
   **then** both are refused and their history is intact.

### User Story 2 - The arrow nobody walked (Priority: P2)

Phase 3's exit criterion ends `→ erasure`, and no test carries an image across that
arrow.

**Independent test**: upload an image, let the deployed scanner pass it, send it,
fetch the signed bytes, erase the uploader, and assert the object and its renditions
are gone from the store and the row from the database.

**Acceptance scenarios**

1. **Given** a delivered image, **when** its uploader is erased, **then** the stored
   bytes and every derived rendition are destroyed and the receipt says how many.
2. **Given** that erasure, **when** the message carrying the attachment is read,
   **then** it renders as a message whose attachment is gone rather than as an error.

### User Story 3 - What the milestone cannot claim (Priority: P3)

A milestone that reports only its green path is one nobody trusts.

**Independent test**: read the chapter's published limits and find, for each, the
measurement or the clause behind it.

**Acceptance scenarios**

1. **Given** the chapter's close, **when** a reader asks which of Journey 3's six
   stages are demonstrated end to end, **then** a per-stage verdict exists with the
   assertion that discharges each.
2. **Given** Phase 3's three-clause exit criterion, **when** a reader asks whether
   Phase 3 can be exited, **then** each clause has a verdict and the ones that cannot
   be met name the obstacle.

### Edge Cases

- A channel external id that is also a valid uuid — two resolutions, one input.
- An external id reused across environments: 1,576 are, and the lookup must be
  tenant-scoped like every other read.
- A dispute whose decisive message was deleted **before** chapter 4.19 shipped: 5,060
  tombstones predate it and no migration recovers their text.
- A banned user who was already disconnected — the ban must still hold at reconnect.
- **A banned user who is still connected.** `docs/03` says their connections drop;
  FR-USR-06 says *preventing connection and message send*. The platform does the
  second and not the first, and the chapter publishes the bound rather than the alarm.
- An erasure performed between the ticket and the investigation: the conversation
  survives and its author does not, which is 4.21's decision seen from Priya's side.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Journey 3 MUST be executable as one test that performs all six stages
  in order against a booted system through the published API.
- **FR-002**: Each assertion MUST name the chapter whose work it verifies, so that
  removing that chapter's work fails a named assertion.
- **FR-003**: A conversation MUST be reachable from its customer-supplied channel
  identifier without the caller holding a mapping of its own.
- **FR-004**: Presenting a channel identifier that resolves to nothing MUST produce a
  refusal that names the cause, never a 5xx.
- **FR-005**: Reconstruction MUST distinguish three outcomes for a message that is
  not visible: never sent, sent and deleted, sent and edited.
- **FR-006**: A moderator action MUST reach a connected recipient and MUST appear in
  the audit trail with the identifier of the request that caused it.
- **FR-007**: The chapter MUST carry an image across the full Phase 3 arrow,
  including erasure, or record which segment it could not and why.
- **FR-008**: Every claim the chapter publishes MUST be a measurement taken on the
  system it describes, with the figure given rather than an adjective.
- **FR-009**: The chapter MUST publish a per-stage verdict for Journey 3 and a
  per-clause verdict for Phase 3's exit criterion, including the unmet ones.
- **FR-010**: Any capability this journey needs that no requirement carries MUST be
  resolved by amending the requirement, not by building past it.
- **FR-011**: Nothing outside this chapter's subject may change behaviour.
- **FR-012**: Where measurement falsifies a published clause or document, the
  document MUST be amended rather than left to diverge.

### Key Entities

- **The journey test** — one file, six stages, each assertion annotated with the
  chapter it verifies. Lives beside `tuan.itest.ts`.
- **A dispute fixture** — two participants, a channel named by an order number, a
  message that was edited, a message that was deleted, and an attachment.
- **The per-stage verdict** — demonstrated / met / unmet by decision / unreachable,
  with where, for each of Journey 3's six stages and Phase 3's three clauses.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All six stages of Journey 3 run in one test and pass.
- **SC-002**: Removing the **mechanism** any one of the test's margin entries names
  turns at least one named assertion red — demonstrated for three of them, each by a
  single surgical edit that is restored afterwards. **Not by reverting the chapter**:
  a tag names one commit where a chapter is three to seven, and later chapters share
  its files.
- **SC-003**: A conversation is reached from an order number in one request, and the
  request that fails to reach one returns a named refusal rather than a 5xx.
- **SC-004**: The three not-visible outcomes are distinguishable from the record
  alone, asserted separately.
- **SC-005**: A deletion reaches a connected recipient, and the same action is found
  in the audit trail by the request identifier returned to the caller.
- **SC-006**: An image is carried from upload to erasure in one test, or the segment
  that could not be is named with its obstacle.
- **SC-007**: Journey 3's six stages and Phase 3's three exit clauses each carry a
  published verdict; the count of demonstrated stages is stated as a number.
- **SC-007a**: Every capability Journey 3's *"What Relay must provide"* blocks assert
  is classified as holding or not, with the clause it cites or the absence of one —
  **fourteen of fourteen**, published as a table.
- **SC-008**: `git diff --name-only part4-ch21..HEAD` contains no file outside this
  chapter's subject, tests and documents.
- **SC-009**: The fence chain reports 0 and every tutorial gate exits 0.
- **SC-010**: The CI error set is compared per error against the pre-chapter
  baseline, in both directions.

---

## Assumptions

- **The test belongs in `packages/e2e`**, beside `tuan.itest.ts`, because that is
  where a journey test already lives and its harness already seeds a conversation
  with two client identities and a tenant credential.
- **Priya's credential is the application key** and the conversation's participants
  need their own tokens — measured: an application credential may send only as a bot.
- **Stage 4 is human work** and the chapter asserts only CON-04's timestamp property.
- **The lookup gap is this chapter's to resolve**, because the journey names it and
  no clause carries it; whether that means a route, a query parameter, or an SRS
  amendment recording the re-POST as the supported path is the plan's question.
- **The milestone does not build new product surface beyond what the journey needs.**
  Rule 4 of `docs/12` §5: a milestone appears after all the work it verifies.
