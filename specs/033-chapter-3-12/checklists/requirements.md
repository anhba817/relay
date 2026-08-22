# Specification Quality Checklist: Chapter 3.12 — Milestone: the isolation gauntlet

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-22
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

Every box is ticked and three of them are ticked against a reading that should be
stated rather than assumed, because a checklist that quietly redefines its own items
is worse than one that fails.

**"No implementation details" and "technology-agnostic", read as: prescribes no
design, names the state that exists.** The spec names `usage_periods`,
`packages/e2e`, `scripts/sync-docs.sh`, `docs_url`, PL/pgSQL, the figure 90.57%, and
close to thirty other artifacts. All of them exist today and none is a decision this
spec is making — they are the repository this chapter is about, at the commit it starts
from. Where the spec reaches a genuine design choice it declines to make it: FR-002
requires the target list to be derived and does not say from what; FR-040 requires the
coverage figure to be measured somewhere the run can see and leaves the location to
the plan; FR-032 requires a documented credential path and names two acceptable
answers without choosing. This is the same reading chapters 3.10 and 3.11 shipped
under, and applying the generic rule literally would produce a specification that
cannot say which port a fixed port is.

**"Written for non-technical stakeholders" is false in the ordinary sense and true in
this project's.** The stakeholder is the series' author and the reader who checks the
chapter against the requirements. A version of this document readable by someone who
does not know what a tenant identifier is could not state FR-004.

**Requirements verified by inspection rather than by test.** Seven — FR-009, FR-014,
FR-015, FR-022, FR-034, FR-035, and the "state the number" clause in FR-040 — require
the chapter to write something down. The SRS's own verification vocabulary allows
inspection alongside test, and the alternative is a chapter that measures honestly and
publishes selectively. Each names what has to be written and what would make it wrong.

**One thing the spec asserts and cannot yet prove.** FR-022 defers the rest of the
public channel and user surface to chapter 3.13, and no such chapter exists in
`docs/07-tutorial-plan.md` yet. The deferral is a promise until that table is edited,
which is planning work, not specification work — recorded here so it is not discovered
later as a gap.

**Two findings this specification is built on came from reading the code rather than
the documents, and both changed the chapter's scope.** There is no public endpoint to
create a channel or add a member, which makes the Phase 2 exit criterion unreachable
for reasons that have nothing to do with documentation; and the set of error codes the
platform can emit is larger than the registry that is supposed to hold it, so
"document every code" could not have been done from the registry alone. Neither is
visible in the SRS, the SAD, or the tutorial plan.
