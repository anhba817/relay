# Feature Specification: Chapter 4.17 — ★ Milestone: an image, end to end

**Feature Branch**: `063-chapter-4-17`

**Created**: 2026-10-01

**Status**: Draft

**Input**: User description: "chapter 4.17"

---

## Context

`docs/12-part-4-structure.md` row 18, movement VI's milestone:

> **★ Milestone: an image, end to end.** Upload → scan → send → signed delivery.
> FR-MED-09's rejection marker renders as rejected, never as broken.

Seven chapters built that path. 4.10 issues the slot and charges the quota, 4.11 refuses an
attachment nobody may attach, 4.12 signs the delivery and decides who may hold the link, 4.13
scans the bytes, 4.14 gives the attachment a state, 4.15 derives the thumbnail, 4.16 puts the
bytes on the bill. **Each half is tested. The join is not.**

A premise check before this spec was written, against the tree rather than against the plan:

| suite | how far it walks | what it stops short of |
|---|---|---|
| `media-worker/src/verify.itest.ts` | slot → PUT → sweep → `ready` | the worker runs **in process**; no send, no delivery |
| `outsider/src/integrate.itest.ts` | slot → PUT → send → **a real verdict** → signed GET → bytes compared | never re-reads the state; no thumbnail; no `media.updated` |
| `api/src/media/attachment-state.itest.ts` | send → verdict → history | the verdict is called **by the test**, not by a worker |
| `api/src/media/delivery.itest.ts` | the gate's six refusals | states are set by SQL |

**CORRECTED IN PHASE 2, AND THE CORRECTION IS THIS CHAPTER'S SUBJECT.** The row above
first read *"asserts `state: "pending"` — no verdict in the picture"*, and the sentence
under the table read *"no test in this repository lets a real scan decide what a recipient
can fetch."* **Both were false, and reading the whole test rather than the assertion the
premise check had quoted is what showed it**: sixty lines later the sealed suite polls
`GET /v1/media/{id}` to a 30-second deadline, which cannot answer 200 until the deployed
worker has marked the object `ready`, then fetches the signed URL and compares the bytes.
**A real scan has been deciding what that test can fetch since 4.13.**

What stays true is narrower and is still the chapter: **nothing asserts that the state a
recipient sees ever changes** — the `pending` assertion is never followed by a second read
— **nothing fetches a thumbnail**, and **no test anywhere watches a `media.updated` frame
arrive**. The milestone is the join, not the verdict.

Two further findings shaped this specification, both from reading the tree:

**Nothing drives the composed `media-worker` container.** It carries `profiles: ["services"]`,
CI starts it for the sealed job, and no assertion anywhere depends on it doing work. Chapter
4.13 met the consequence once — the container could not reach the scanner, every object stayed
`pending`, and **nothing failed**, because a worker that produces no verdict is FR-009 working
as designed and is indistinguishable from an object nobody uploaded to. The repair was a boot
line. A boot line is not a test.

**And the sealed suite's comment is false in the job that runs it.** It asserts
`state: "pending"` under the words *"this suite runs no media worker, which is what makes the
value stable rather than timing-dependent."* CI's sealed job runs
`docker compose --profile services up -d --wait`, and the worker is in that profile. The sweep
interval is 5,000 ms. So the assertion is either a race that keeps winning or a true reading of
a worker that is not working, and the comment explaining it is wrong either way. **Which of
those it is must be measured before anything is built on top of it.**

**MEASURED IN PHASE 2: it is a race that keeps winning, with about four seconds of margin.**
Ten independent trials from PUT to verdict gave **min 1,861 · p50 3,993 · max 5,568 ms**
against three steps between the PUT and the assertion that take milliseconds. So the value is
stable and timing-dependent at the same time, which the comment treated as alternatives. The
comment is replaced with the measurement, and — because a comment is not a test — the reason
is now checked: the suite waits past the window and asserts the verdict it claimed was absent.

This is a milestone chapter, so it follows `docs/12` §2.3's split: a falsifiable claim the lane
checks on every run, and a measurement recorded once. It is not a chapter that adds product
surface.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — One image, through the worker that ships, to a recipient (Priority: P1)

A customer's backend takes an upload slot, PUTs an image, and sends a message naming it. The
media worker — the one a deployment runs, not a function a test calls — scans the bytes,
verifies the declaration, and records a verdict. A reader of that channel sees the message with
the attachment marked `ready`, asks for a link, and fetches the bytes. They are the bytes that
were uploaded.

**A reader, not a second credential.** The sealed lane holds exactly one
(`RELAY_DEMO_CREDENTIAL`), and the seeder mints one on purpose — its own comment records that a
second key under the same demo organisation would leave two credentials where the printed one is
whichever came last. Minting another is product-adjacent work this feature forbids itself
(FR-012), and the claim does not need it: what the milestone asserts is that the state and the
bytes reach a *reader*, which is a socket subscriber or a second read through history.

**Why this priority**: it is the milestone's whole claim, and it is the only one that can fail
for its own reason. Every other story in this feature is a statement about something that has
already happened in this one.

**Independent Test**: run the suite against the composed stack. Remove any one of the seven
chapters' contributions and a named assertion fails.

**Acceptance Scenarios**:

1. **Given** a slot issued for a real PNG, **When** the bytes are PUT and the deployed worker
   runs, **Then** the object reaches `ready` without any test calling the verdict route.
2. **Given** that object attached to a message in a channel, **When** the channel is read —
   over a socket as a subscriber, or through history — **Then** the attachment carries `ready`
   and not `pending`.
3. **Given** the recipient holds only the media id, **When** they ask for a link and follow it,
   **Then** the bytes they receive are byte-identical to the bytes uploaded.
4. **Given** an image **above 320 px on its long edge**, **When** the reader asks for the
   thumbnail the platform derived, **Then** they are served it, and the chapter states the
   bound that made it exist.
5. **Given** a subscriber that received the message while the attachment was `pending`, **When**
   the verdict lands, **Then** a `media.updated` frame reaches them carrying `ready` — the
   placeholder becoming a picture, which is the frame a client actually waits on.
6. **Given** the worker is stopped, **When** the same sequence runs, **Then** a named assertion
   fails rather than the suite passing on a `pending` attachment.

---

### User Story 2 — A rejected upload arrives as a marker, not a gap (Priority: P2)

A customer's backend uploads a file whose bytes contradict what it declared. The scan or the
verification refuses it. The message that named it is still in history, still readable, and the
attachment says it was rejected — which a person reconstructing the conversation can tell apart
from a message that was deleted and from a message that never had an attachment.

**Why this priority**: FR-MED-09 is the clause the milestone's own line names. Its data half is
built and its evidence is spread across two suites that never see a real refusal.

**Independent Test**: upload bytes that contradict the declaration, let the deployed worker
refuse them, and read the channel as a recipient.

**Acceptance Scenarios**:

1. **Given** an object the worker rejects, **When** a recipient reads the channel, **Then** the
   message is present and its attachment carries `rejected`.
2. **Given** the same message, **When** a recipient asks for a link to the rejected object,
   **Then** they are refused, and the refusal is indistinguishable from the refusal for an id
   no object has.
3. **Given** a rejected attachment and a deleted message in the same channel, **When** a
   recipient reads history, **Then** the two are distinguishable without reading any field the
   platform does not publish.
4. **Given** a recipient already holds a frame saying `pending`, **When** the worker then
   rejects the object, **Then** a `media.updated` frame reaches that recipient carrying the new
   state.
5. **Given** no renderer exists in this repository, **When** FR-MED-09's *"renders as"* half is
   assessed, **Then** it is recorded as unmet with the reason rather than reported as met.

---

### User Story 3 — What the path costs, measured once (Priority: P3)

The chapter publishes how long one image takes to travel the whole path, decomposed into the
steps that own the time, with the volume and the machine stated beside it.

**Why this priority**: `docs/12` §2.3 makes the recorded measurement the milestone's second
half, following `docs/11`'s precedent. It is the half that cannot be a CI gate, because the
figure is about a machine rather than about a defect.

**Independent Test**: run the path a stated number of times and publish the distribution.

**Acceptance Scenarios**:

1. **Given** the composed stack, **When** one image is carried from slot to delivered bytes,
   **Then** the elapsed time is reported per step and summed.
2. **Given** the sweep runs on a 5,000 ms timer, **When** the end-to-end figure is published,
   **Then** the part of it that is the timer is named separately from the part that is work.
3. **Given** a single sample, **When** any figure is published, **Then** it carries the number of
   runs behind it.

---

### Edge Cases

- **What does the sealed suite assert once a worker is actually running beside it?** Its current
  expectation of `pending` may stop holding, and the comment explaining why it holds is already
  false. Whatever it becomes, it must be stable for a stated reason rather than for a timing one.
- **What happens when the recipient asks for the thumbnail by its own id?** A rendition is named
  by no message, and 4.15 made its reachability its parent's. The milestone is where a recipient
  first holds both ids.
- **What happens when the worker is running but cannot reach the scanner?** 4.13's case: every
  object stays `pending` and nothing fails. The milestone must make that state loud.
- **What happens when the bytes are uploaded but no verdict has been reached yet?** `pending` is
  a legitimate steady state for up to one sweep interval, so an assertion that waits must wait
  for a condition rather than for a duration.
- **What happens to a message whose attachment is rejected after the message was delivered?** The
  recipient already holds a frame saying `pending`, and 4.14 built `media.updated` for exactly
  this. **The sealed suite mentions that frame zero times**, so the journey is the first place it
  would be observed from outside — which makes it the only end-to-end evidence 4.14's work has.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: One suite MUST carry a single image from upload slot to bytes a recipient fetches,
  with the deployed worker — the composed container — running it rather than a function the test calls.
- **FR-002**: Each assertion this feature adds MUST name the chapter whose work it depends on,
  so removing that work fails an assertion that says which. **The convention is borrowed and is
  new to this file**: `packages/e2e/src/tuan.itest.ts` carries it (*"Read the right margin: each
  step names the chapter that made it possible"*) and `integrate.itest.ts` has three chapter
  mentions across nineteen tests. Adopting it here applies to what this feature writes, not
  retroactively to its neighbours.
- **FR-003**: The suite MUST fail when the media worker is not working, and MUST NOT pass by
  observing a state that an unworked object and a worked one share.
- **FR-004**: A reader MUST be able to obtain the bytes of a `ready` attachment, and the bytes
  MUST equal the bytes uploaded.
- **FR-004a**: The journey's image MUST exceed **320 px on its long edge**, because at or below
  it `thumbnailOf` answers `within-bound` and the worker writes **no rendition at all** (4.15).
  A journey that asserts a thumbnail under a smaller image asserts an id the payload never
  carries.
- **FR-005**: A rejected attachment MUST reach a recipient as an explicit state on a message that
  remains in history, distinguishable from a deleted message and from a message with no
  attachment.
- **FR-006**: A link to a rejected object MUST be refused, and the refusal MUST be
  indistinguishable from the refusal for an object that does not exist.
- **FR-006a**: A recipient holding a frame that says `pending` MUST receive the state change when
  the verdict lands, through the frame 4.14 built for it, **on both paths**. `announce` returns
  early unless the state is `ready` or `rejected`, so the platform treats them alike and the
  journey does too — the ready frame is the commoner case and the one a client waits on.
- **FR-007**: Where a clause of FR-MED-09 cannot be discharged because no artifact in this
  repository can render anything, it MUST be recorded in the SRS as unmet with the reason.
- **FR-008**: The chapter MUST state which half of the milestone runs in the lane and which half
  is a recorded measurement, and MUST NOT present the second as the first.
- **FR-009**: The published end-to-end figure MUST separate waiting on a timer from work, and MUST
  carry its sample size.
- **FR-010**: The suite MUST assert on a condition rather than on elapsed time wherever it waits
  for the worker, and any quiet window MUST follow an arrival wait rather than replace it.
- **FR-011**: Where an existing suite's stated reason for an assertion is false, the reason MUST
  be corrected or the assertion changed — a green assertion with a wrong explanation is the
  defect this chapter exists to find.
- **FR-012**: This feature MUST NOT add product surface. Where the milestone wants something the
  platform does not expose, it is recorded rather than invented. **Checked at the close rather
  than promised**: every platform file this feature changes is a test, a comment or a document,
  and the diff is read to confirm it.
- **FR-013**: The chapter MUST state what the development lane cannot demonstrate about this path.

### Key Entities

- **The journey**: one image and one message, carried by the published surface only — a slot, a
  PUT, a send, a read, a link, a GET.
- **The deployed worker**: the composed `media-worker` container, called that throughout. No assertion anywhere currently depends on it.
- **The attachment state**: `pending`, `ready` or `rejected` as a recipient sees it, which is the
  only thing FR-MED-09 can be tested against in a repository with no client.
- **The rendition**: the thumbnail 4.15 derives, which the recipient may or may not be able to
  reach, and which the milestone is the first place anyone asks about from the outside.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: One image travels from slot to delivered bytes in a single automated run, with the
  worker deployed rather than called, and the delivered bytes equal the uploaded bytes.
- **SC-002**: FR-003's measurement — stopping the deployed worker turns the suite red, and the
  failure names the worker rather than reporting an attachment in a legitimate state.
- **SC-003**: A rejected upload leaves a readable message whose attachment says `rejected`, and a
  link to it is refused identically to a link to an id no object has.
- **SC-003a**: A subscriber that received the message while the attachment was `pending` receives
  a `media.updated` frame carrying the verdict — **`ready` on one path and `rejected` on the
  other, both asserted** — observed from outside the platform for the first time.
- **SC-004**: Every assertion **this feature adds** names the chapter it depends on, and the
  count of added assertions with no such name is zero. The nineteen tests already in that file
  are not in scope — renaming them is another chapter's work.
- **SC-005**: The end-to-end elapsed time is published with its decomposition, its sample size and
  the number of sweep intervals inside it.
- **SC-006**: The number of clauses this chapter can and cannot discharge is published as a count,
  not as an adjective.
- **SC-007**: The sealed suite's media expectation is either unchanged with a true explanation or
  changed with a stated reason, and in both cases it is stable for a reason the suite can name.
- **SC-008**: The CI error set after this chapter is compared per error against the set before it,
  in both directions.
- **SC-009**: `check:fences` reports zero and the tutorial builds.
- **SC-010**: The chapter is between 2,000 and 4,000 prose words, counted outside fences and
  tables.

---

## Assumptions

- **The milestone adds no product surface.** Row 18's line is a claim about what already works;
  everything this feature writes is a test, a measurement or a document. Chapter 4.2 is the
  counter-example that makes this worth stating — it built all four items of a later chapter's
  brief and that chapter ceased to exist.
- **"End to end" ends at the bytes, not at a screen.** This repository has no client and no
  renderer, and FR-MED-14's reference client is P4 and unbuilt. The furthest a test can follow an
  image is the response to a signed GET.
- **The fixture is generated, not carried, and it needs `node:zlib`.** The sealed suite's
  existing image is a **1×1 PNG written as a 67-byte literal**, which produces no rendition —
  and the journey's 800×600 image deflates to 447,345 bytes, so a literal is not available. A
  Node builtin is not a workspace path, which is the seal's actual rule; the file's header
  sentence claiming it imports nothing beyond `vitest` is already false (line 1 is
  `node:crypto`) and is corrected rather than worked around. The alternative considered was a
  **321×1** strip, which deflates to 281 bytes and would fit a literal — rejected because every
  figure this chapter publishes would then describe a one-pixel-tall image and could not be
  compared with the measurements already taken at 447,377 bytes.
- **The deployed worker means the composed container**, built from its own Dockerfile and started
  under the `services` profile — which is what CI's sealed job already starts and what no
  assertion currently depends on.
- **The ingester is not in the path.** Metering is 4.16's and its records travel a different
  route; the milestone does not wait on a process no deployment starts (050-8).
- **The lane's scale is not the subject.** The development lane holds 6,535 media objects and
  four images above the thumbnail bound; this chapter carries one image and says so.
- **Vietnamese is out of scope.** The translation lags thirteen chapters in Part 4 and is the
  user's own editing pass.

---

## Out of Scope

- Any renderer, client or dashboard. FR-MED-09's *"renders as"* and FR-MED-12's *"visible in the
  dashboard"* are both recorded as unmet rather than built.
- Changes to the path itself. If the journey finds a defect, the defect is recorded and the fix is
  scoped deliberately rather than absorbed into a milestone.
- The video half of FR-MED-05, recorded unmet by decision at 4.15.
- A scheduler for DR-17's weekly reconciliation, recorded unmet by decision at 4.16.
