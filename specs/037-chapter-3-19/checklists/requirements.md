# Specification Quality Checklist: chapter 3.19 — presence, and who is allowed to see it

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-27
**Last re-run**: after analysis pass 5
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

**This file is a gate, and for four analysis passes it was a fossil.** It was written before pass 1
and still said *"All items pass"* while the spec grew from 31 requirements to 38 under two CRITICAL
remediations. Two of its ticks were false when pass 2 read them: *"requirements are testable and
unambiguous"* held only because two behaviours the design already had — the log vocabulary and the
self-healing duplicate `online` — were required by nothing at all. Re-run at pass 5, and the
re-running is the point.

### What the spec looked like at each pass

    pass 0   31 requirements   two clarifications put to the author, both answered
    pass 1   34                +FR-027/028/029, from reading traceability the second way
    pass 2   36                +FR-030/031, behaviours in the design that no clause allowed
    pass 4   37                +FR-016c, NFR-SCL-01 — half of the SRS row being closed
    pass 5   38                +FR-032, NFR-MNT-02's coverage class

Every one of those five was a requirement for behaviour that already existed somewhere in the
design. None came from new scope.

### The two decisions the author made, still standing

- **Open question 3 closes as *not opt-in per channel***, confirming ADR-10, with the revisit
  trigger and NFR-SCL-01 both named as undischarged.
- **FR-RTM-10 stays out**, and chapter 3.18's `gaps.md` item 4's stated premise for assigning it here is corrected
  rather than inherited.

### What no checklist item covers

**FR-021 is a claim in chapter prose, and no checker in this repository reads prose.** It is the
sixth chapter to carry chapter 3.18's `gaps.md` item 6, and the only verification it has is a person. The ticks
above are all satisfiable by byte comparison; that one is not.

### Running the mechanical half

    python3 specs/037-chapter-3-19/check-refs.py

Checklist format, sequential task ids, no task id cited outside `tasks.md`, and every requirement
traced. Ten red tests. Its own blind spot is in its header: **it compares ids, never claims.**
