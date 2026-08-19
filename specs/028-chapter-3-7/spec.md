# Feature Specification: Tutorial Chapter 3.7 — "Commit and publish are two instants"

**Feature Branch**: `028-chapter-3-7`

**Created**: 2026-08-19

**Status**: Draft

**Input**: User description: "Start chapter 3.7 for the resume duplicate fix, update the tutorial plan also"

Chapter 2.7 is described in the tutorial plan as building "the tutorial's flagship
bug" — the duplicate/gap race in the resume protocol — and closing it. It did not
close it. A client that reconnects can be delivered the same message twice, and
the platform's headline guarantee (FR-RTM-03: "no gap and no double") is false
about once in every six runs of the journey that asserts it.

The defect was found by chapter 3.6's baseline measurement, in a lane that was
failing for three other unrelated reasons at the same time. It is recorded in
`specs/027-chapter-3-6/baseline.txt` as flake 4, and deliberately left unfixed
there because it is chapter 2.7's code and belongs in a chapter that can explain
it.

**The cause is a seam Part 3 has already taught three times.** A message becomes
durable and a message becomes announced at two different instants, and everything
that reads between them sees a state neither instant describes. Chapter 3.3 built
the outbox to make those two instants atomic. Chapter 3.5 chose to post before
recording and let the customer absorb a duplicate. Chapter 3.6 chose to publish
after committing and let the record be lost. The fan-out path is the fourth
instance of the same seam and the only one built before the reader had the
concept — in chapter 2.6, before the outbox existed.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reconnecting client is never shown a message twice (Priority: P1)

An end user's connection drops mid-conversation. While they are away, other
people keep talking. When their client reconnects and presents the cursor it had
applied, it receives everything it missed, in order, exactly once — including
messages that were written during the reconnection itself.

**Why this priority**: It is the requirement the platform is sold on. FR-RTM-03
and the SAD's §5.2 both state it, chapter 2.8's milestone suite asserts it, and it
is currently false. Nothing else in this chapter matters if this is not fixed.

**Independent test**: Drive the reconnection with a message written into the
window between the api's commit and the fabric's publish; confirm the client's
timeline contains that message once, in sequence order, with no gap.

**Acceptance scenarios**:

1. **Given** a client resuming from a cursor, **when** a message is committed
   before its backfill query runs and published to the fabric after its resume
   completes, **then** the client receives that message exactly once.
2. **Given** a client resuming from a cursor, **when** a message is both returned
   by the backfill and delivered live during the buffering window, **then** the
   client receives it exactly once (the behaviour chapter 2.7 already has, which
   must not regress).
3. **Given** a client that has resumed and is live, **when** a message with a
   sequence at or below what its backfill already delivered arrives from the
   fabric, **then** it is not delivered a second time.
4. **Given** a client that has resumed and is live, **when** a message with a
   sequence above its backfill's high-water mark arrives, **then** it is
   delivered — the fix must not turn a duplicate problem into a gap.
5. **Given** a fresh connect presenting no cursor, **when** messages arrive,
   **then** delivery is unchanged from chapter 2.6's behaviour.

### User Story 2 - The chapter explains why the first solution was incomplete (Priority: P2)

A reader who has finished chapter 2.7 believes the resume race is closed, because
that chapter says so and proves it with a test. This chapter shows them the case
the proof did not cover, why the model admitted it, and what the corrected model
is.

**Why this priority**: The teaching value is the reason this is a chapter rather
than a patch. A reader who takes chapter 2.7's reasoning as complete will build
the same defect into their own system, because the reasoning is persuasive and
almost right.

**Independent test**: The chapter states the two instants explicitly, shows the
failing timeline from a real run, and names why chapter 2.7's own analysis
("in the backfill, in the buffer, or both") does not enumerate the failing case.

**Acceptance scenarios**:

1. **Given** the chapter, **when** a reader looks for what chapter 2.7 got wrong,
   **then** the chapter states it plainly and without treating the earlier chapter
   as careless.
2. **Given** the chapter, **when** a reader asks how it was found, **then** the
   chapter records that it was an intermittent failure in a suite that was already
   red for unrelated reasons, and what that cost.
3. **Given** the chapter, **when** a reader compares it to chapters 3.3, 3.5 and
   3.6, **then** the same seam is identified in all four with the different answer
   each one chose.

### User Story 3 - Part 3's numbering absorbs a new chapter without leaving lies behind (Priority: P3)

Inserting a chapter shifts every chapter after it. Cross-references in published
prose, in the plan, in the site's registry, and — the hard case — inside source
code comments that are byte-fenced into published chapters, all have to end up
consistent.

**Why this priority**: It is bookkeeping, but it is bookkeeping with a trap in it,
and the trap has already been sprung once. `services/api/src/db/schema.ts` says
"chapter 3.7's cross-tenant gauntlet"; the gauntlet became 3.8 when chapter 3.6
was inserted, and that comment was never carried. It is fenced byte-exact into
published chapter 3.5, so the mechanism that guarantees the book matches the code
is the same mechanism that makes the stale reference awkward to correct.

**Independent test**: After the renumbering, no document, page or source comment
cites a chapter number that does not name what it claims to name.

**Acceptance scenarios**:

1. **Given** the renumbering, **when** the plan, the site registry and the
   published chapters are read together, **then** quotas is 3.8, the isolation
   gauntlet is 3.9, and this chapter is 3.7 everywhere.
2. **Given** a source comment that cited a chapter number, **when** the
   renumbering happens, **then** the comment is either corrected or rewritten to
   stop citing a number that can move.
3. **Given** the fence chain, **when** any fenced source file is corrected,
   **then** the chain still replays onto the platform repository byte for byte.

### Edge Cases

- A message committed before the backfill and published after the flush — the
  failing case, and the reason this chapter exists.
- A message committed and published entirely within the buffering window — chapter
  2.7's case, which must keep working.
- A resume that degrades (`resume_ok: false`) after the buffer overflows or the
  backfill fails: the client is told to page history, so no mark can be trusted
  and none may be retained.
- A channel absent from the backfill because nothing new arrived: its mark is the
  presented cursor, not zero.
- A client that resumes, goes live, and stays connected for hours — the retained
  mark must not grow without bound, and must never suppress a message the client
  has not already been given or already claimed to hold.
- Two connections for the same user on the same gateway instance, one resuming and
  one live.
- A message whose sequence is below the mark because it was *edited* or
  tombstoned rather than created (a later chapter's frame types).
- A client presenting a cursor far above anything the channel holds. The cursor is
  client-supplied and checked only for being a non-negative integer, so the mark it
  seeds suppresses every live frame on that channel for the life of the connection
  — where before this change it only emptied the backfill. This does not contradict
  the case above: the client asserted it holds those sequences, and the backfill has
  always taken that assertion at face value. The blast radius is one connection, it
  is self-inflicted, and reconnecting with a correct cursor recovers it.
  `contracts/resume.md` records why the platform does not second-guess the claim.

## Requirements *(mandatory)*

### Functional Requirements

**The defect**

- **FR-001**: A resumed connection MUST NOT deliver a message whose sequence is at
  or below the highest sequence its backfill already delivered for that channel.
- **FR-002**: A resumed connection MUST deliver every message whose sequence is
  above that mark. Suppressing a duplicate MUST NOT create a gap.
- **FR-003**: The suppression MUST apply after the resume completes, not only
  while the connection is buffering. The window in which a duplicate can arrive
  extends past the moment the connection goes live, and that is the whole defect.
- **FR-004**: The mark MUST be per channel. A duplicate on one channel MUST NOT
  suppress a legitimate message on another.
- **FR-005**: A connection that resumed with `resume_ok: false` MUST NOT retain
  any mark: it has been told to page history, and a mark taken from an incomplete
  backfill would suppress messages the client never received.
- **FR-006**: A fresh connection presenting no cursor MUST behave exactly as it
  does today, with no suppression and no retained state.
- **FR-007**: The retained state MUST be bounded: at most one sequence per channel
  in the resume cursor set, which the resume contract already caps at
  `MAX_RESUME_CHANNELS`. It MUST NOT grow with the connection's lifetime. The
  gateway MUST enforce this itself by scoping the marks to the channels it presented
  cursors for, rather than inheriting the bound from the api's response shape.
- **FR-007a**: A mark MUST NOT be retired while the connection lives. Observing a
  sequence above the mark MUST NOT clear it.

  This replaces an earlier version of FR-007 that required the opposite.
  Retirement on observation looks like the natural way to bound the state, and it
  reintroduces the defect: sequences commit in order under a channel row lock, but
  they are published by whichever gateway instance handled each send, and those do
  not coordinate. A prompt publish of sequence 5 can precede a stalled publish of
  sequence 4, and a rule that retired the mark on 5 would then deliver the 4.
  Research R3 has the timeline; FR-007's bound is what makes retirement
  unnecessary.
- **FR-008**: Delivery MUST remain correct when the platform is running more than
  one gateway instance: the mark belongs to a connection, not to an instance.

**The chapter**

- **FR-009**: The chapter MUST state the two instants — durable and announced —
  and show where the gateway's send path separates them.
- **FR-010**: The chapter MUST show the failing timeline from a captured run
  rather than describing it.
- **FR-011**: The chapter MUST name why chapter 2.7's analysis did not cover the
  case, quoting that chapter's own reasoning, without rewriting chapter 2.7.
- **FR-012**: The chapter MUST connect the seam to chapters 3.3, 3.5 and 3.6 and
  state the different answer each chose.
- **FR-013**: The chapter MUST record how the defect was found, including that it
  reproduced roughly once in six runs and survived inside a lane that was red for
  three unrelated reasons.
- **FR-014**: The chapter MUST be published in English and Vietnamese, with fences
  mirrored byte for byte.
- **FR-015**: Every file the chapter's prose asserts MUST be fenced, including
  test files, and the fence chain MUST replay onto the platform repository.
- **FR-016**: Every transcript the chapter quotes MUST be captured from a real run.

**The renumbering**

- **FR-017**: Limits and quotas MUST become 3.8 and the isolation gauntlet MUST
  become 3.9, in `docs/07-tutorial-plan.md` and in the site's chapter registry.
- **FR-018**: Cross-references in published pages that name a moved chapter MUST
  be corrected, in every locale that page has.
- **FR-019**: Source comments that cite a chapter number MUST NOT be left stale.
  This includes the reference that is already stale from the previous insertion.
- **FR-020**: Any correction to a fenced source file MUST leave the fence chain
  replaying byte for byte, either by amending the chain where the file's chain
  currently ends or through the post-series mechanism.

### Key Entities

- **High-water mark**: The highest sequence a resuming connection's backfill
  delivered for one channel. Computed today, used once, and discarded; this
  chapter gives it a lifetime.
- **Resume phase**: Whether a connection is holding frames back or handing them
  over. Today it is the only thing delivery consults, which is why the dedup stops
  when it flips.
- **The publish gap**: The interval between the api committing a message and the
  gateway announcing it on the fabric. Not a stored thing — a window, and the
  subject of the chapter.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The journey that currently fails intermittently passes on twenty
  consecutive runs of the integration lane.
- **SC-002**: A test exists that fails deterministically against the current code
  and passes against the fixed code, driving the commit-to-publish window directly
  rather than waiting for it to occur by chance.
- **SC-003**: No message is lost in any resume scenario the existing suites cover:
  every assertion in chapters 2.6, 2.7 and 2.8's suites passes unchanged in
  substance.
- **SC-004**: Both lanes pass and coverage exits 0 with every ratchet intact.
- **SC-005**: Every claimed invariant fails when its mechanism is removed, verified
  by sabotage with files restored byte-identical.
- **SC-006**: The chapter is reachable in both locales and its figures render.
- **SC-007**: After the renumbering, a search for chapter-number cross-references
  across the plan, the registry, the published pages and the platform source finds
  none that name the wrong chapter.
- **SC-008**: The chapter states which part of chapter 2.7 was incomplete and does
  not require the reader to have noticed the defect themselves.

## Assumptions

- **The fix belongs in the gateway, not the api.** The api's commit-then-return is
  correct and the gateway's publish-after-response is correct; what is missing is
  that the reader of both does not account for the interval between them. Moving
  the publish into the api would be a larger change that trades this defect for a
  dual write chapter 3.3 spent itself removing.
- **The mark is retained on the connection, not in Redis.** It describes what one
  socket has been shown, it dies with that socket, and putting it in shared state
  would make it a source of truth, which constitution IV forbids for Redis.
- **The suppression is bounded by the cursor cap, and the mark is never retired.**
  This spec first assumed the opposite — that a mark could be dropped once a higher
  sequence arrived — and asked the plan to confirm the bound. Research R3 found the
  assumption unsafe and unnecessary: unsafe because two gateway instances publish
  without coordinating, so a higher sequence can arrive before a delayed lower one;
  unnecessary because the mark set is already capped at 200 by
  `MAX_RESUME_CHANNELS`, which the api enforces. Recorded as a correction rather
  than edited away, because the reasoning that made retirement look right is the
  same reasoning that made the original defect look closed.

- **Chapter 2.7 is not rewritten.** It shows the state of the platform at its own
  time, which is the fence chain's premise. This chapter amends the code and
  explains the amendment; the earlier chapter stays as published.
- **The chapter is short.** The defect is one field and one comparison. The
  chapter's length should come from the explanation, not the diff, and it is
  expected to land near the lower half of the 2,000–4,000 word bound rather than
  the upper.
- **Part 3 gains a chapter for the second time.** Chapter 3.5's split already did
  this once and the plan records why. The same renumbering discipline applies.
- **The already-stale reference is fixed by this feature**, not left for a third
  insertion to compound. Source comments that name chapter numbers are the
  fragile case, and the durable answer is for them to stop naming numbers that can
  move.

## Out of Scope

- Rewriting chapter 2.7 or chapter 2.8.
- Any change to the api's write path, the sequence assignment, or the outbox.
- Moving fan-out publication into the api, or making it transactional.
- The reconnection storm at fleet scale, which remains chapter 7.5's subject.
- Client-side deduplication in the SDK — the platform must not require a correct
  client in order to keep its own guarantee.
- The other flakes chapter 3.6 recorded and fixed; they are already done.

## Dependencies

- Chapter 2.6's fan-out fabric and chapter 2.7's resume protocol, unchanged in
  design.
- Chapter 2.8's journey suite, which is the test that caught this and which must
  keep asserting it.
- The compose stores. No new infrastructure.
