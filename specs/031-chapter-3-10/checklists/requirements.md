# Specification Quality Checklist: Chapter 3.10 — Quotas and what they cost

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-21
**Feature**: [spec.md](../spec.md)

## Content Quality

- [X] No implementation details (languages, frameworks, APIs)
- [X] Focused on user value and business needs
- [X] Written for non-technical stakeholders
- [X] All mandatory sections completed

## Requirement Completeness

- [X] No [NEEDS CLARIFICATION] markers remain
- [X] Requirements are testable and unambiguous
- [X] Success criteria are measurable
- [X] Success criteria are technology-agnostic (no implementation details)
- [X] All acceptance scenarios are defined
- [X] Edge cases are identified
- [X] Scope is clearly bounded
- [X] Dependencies and assumptions identified

## Feature Readiness

- [X] All functional requirements have clear acceptance criteria
- [X] User scenarios cover primary flows
- [X] Feature meets measurable outcomes defined in Success Criteria
- [X] No implementation details leak into specification

## Notes

Two items were argued rather than waved through, and both are recorded in
Assumptions with the evidence:

- **The cap is denominated in metered units, not money.** No price, unit cost or
  currency appears in `docs/04-srs.md` or `docs/05-sad.md`. FR-RTL-06's design note
  calls it a purchasing requirement whose harm is unbounded exposure, which a unit
  cap bounds.
- **Connection-minutes is chapter 3.11, not "later".** Scheduled with a number, and
  the gauntlet moved to 3.12 to make room.

Three items sit close to the "no implementation details" line and are kept because
removing them would remove the constraint rather than the detail:

- **FR-021** names feature 030's exemption list. That is a property of the test
  lane the chapter has to satisfy, not a design choice it gets to make, and a
  chapter that discovers it during implementation discovers it as a red lane.
- **FR-002** says usage must be derivable without the per-minute counter store.
  This reads as an implementation constraint and is the chapter's central
  requirement — a quota that a cache flush can erase is not a quota.
- **SC-006** references chapter 3.8's recorded send latency. It is a comparison
  against a measurement this project already holds, which is what makes it
  checkable.

## Analysis pass, 2026-08-21

Thirteen findings, no CRITICAL, no constitution violation. All thirteen applied.

Three were worth the pass on their own:

- **F1** — T018 said "the request path must gain no query", which is stronger than
  FR-020 and false of the design it verified. The send transaction *does* gain a
  query; what FR-020 forbids is one that scans. A task that fails against its own
  plan is a task that gets argued with at implementation time instead of read.
- **C1** — SC-006 measured "no additional table scan" against "chapter 3.8's
  recorded send latency". Chapter 3.8 records no send latency, and a clock cannot
  show a scan. Two errors in one clause, both from reusing a sentence rather than
  checking it.
- **G1** — FR-019, the email must not be able to fail a send, had no task. It is
  satisfied structurally by writing a row instead of sending one, which is exactly
  the kind of "obviously fine" that goes unverified until it is not.

And one the pass created and then caught: fixing U1 introduced FR-013a, whose
ordering constraint was first hung on T020 — a US2 task — which would have made
US2 depend on US3 and broken the independence the phase structure exists for. It
belongs to T028, which is where the crossing write is introduced.

The counts moved: 75 tasks to 78, 22 requirements to 23.

## Second analysis pass, 2026-08-21

Seven findings, three HIGH, no CRITICAL, no constitution violation. All seven
applied.

**Pass 1 read the documents against each other and found thirteen things. This
pass read them against the code and found seven, and every HIGH was a claim the
plan made confidently about architecture nobody had opened.**

- **H1** — the plan costed "two controller mappings". This service has none:
  `ProtocolErrorFilter` is `@Catch()`-all and globally registered, and both send
  routes converge on one `messages.send`. The refusal is one throw.
- **H2** — extending `environmentLimits` would have made every WebSocket connect
  pay for a usage join, because `internal/session.controller.ts:67` uses it to hand
  the gateway its limits. Removing the extension made the design smaller: the caps
  are read once, inside the transaction that enforces them.
- **H3** — an unnamed `402` emits `code: "internal_error"`. The envelope infers a
  code for four statuses and calls everything else internal. Nothing said the
  thrower must name its code.

Two of the three made the plan simpler rather than larger, which is the argument
for running this pass before implementation rather than discovering it there.

The counts moved: 78 tasks to 79, and one task (T013a) inverted — it used to say
"rename it", it now says "leave it alone and confirm both call sites are
untouched".

**SC-009 cannot be evaluated until the chapter is written.** It is the size gate,
and chapter 3.8 established that it is counted on the finished page rather than
estimated — three of Part 3's four splits were discovered mid-chapter.
