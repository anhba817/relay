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

**SC-009 cannot be evaluated until the chapter is written.** It is the size gate,
and chapter 3.8 established that it is counted on the finished page rather than
estimated — three of Part 3's four splits were discovered mid-chapter.
