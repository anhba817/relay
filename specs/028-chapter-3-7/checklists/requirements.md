# Specification Quality Checklist: Tutorial Chapter 3.7 — "Commit and publish are two instants"

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-19
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

**Validated.** Three passes were needed and each found something.

**Pass 1 — implementation detail in the requirements.** FR-001 named the field the
mark would be stored on and FR-003 described the phase flag. Both were rewritten
to state the behaviour: what must not be delivered, and that the rule outlives the
buffering window. The distinction matters here more than usual, because the fix is
small enough that a spec written in terms of the fix would just be the patch with
worse formatting.

**Pass 2 — a success criterion that could not fail.** SC-001 originally said "the
journey passes", which it already does five runs in six. Twenty consecutive runs
is a real bar for a defect that reproduces at that rate, and SC-002 was added
because a passing flaky test proves nothing: the chapter needs a test that fails
deterministically against today's code. That is the difference between fixing this
and waiting for it to stop happening.

**Pass 3 — the renumbering was underspecified.** The first draft asked for the
plan and the registry to be updated and stopped there. It missed that chapter
numbers are cited inside source-code comments which are byte-fenced into published
chapters, so correcting one means touching the fence chain. FR-019 and FR-020 were
added, and FR-019 deliberately covers the reference that is **already** stale from
the previous insertion — the gauntlet moved to 3.8 during chapter 3.6's work and
`schema.ts` still calls it 3.7.

**One judgement recorded rather than resolved.** The spec assumes the suppression
is retired by observation (a sequence above the mark) rather than by a timer. A
timer would be a guess about the length of the publish gap; observation is exact
but keeps a small amount of state on a quiet channel for as long as the channel is
quiet. FR-007 bounds it; the plan should confirm the bound is genuinely constant
before implementation.

Items marked incomplete require spec updates before `/speckit-clarify` or
`/speckit-plan`. None are.
