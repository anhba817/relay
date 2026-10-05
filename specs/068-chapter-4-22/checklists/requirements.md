# Specification Quality Checklist: chapter 4.22, "The identifier the customer gave it"

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-05
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

**THE SCOPE IS MEASURED RATHER THAN ARGUED, WHICH IS WHY IT IS BOUNDED.** A sweep of
`information_schema` returns exactly two tables with an `external_id` column —
`channels` and `users` — so the question *"which nouns does this chapter touch?"* has
an answer from the database rather than from a judgement about what feels in scope.
Messages, media objects, webhooks and environments are excluded by construction, not
by preference.

**THE SPEC NAMES NO ROUTE COUNT IT DID NOT COUNT.** 13 channel routes and 8 user
routes come from a sweep of every `@Controller`/`@Param` pair, printed in full before
the spec was written. 41,768 channels with 0 uuid-shaped identifiers is a query.

**ONE ITEM CARRIES A JUDGEMENT A PLANNER MAY OVERTURN.** *Scope is clearly bounded*
is marked complete, and FR-002 — keep accepting the Relay identifier — is the reason
the bound holds. If the plan decides instead to deprecate the uuid, the chapter gains
a migration, a deprecation window and a client story, and the bound moves. **The spec
takes the position that a transition is not a design and says so in the Assumptions**,
so the plan can refuse it in one place.

**WHAT THIS SPEC DELIBERATELY DOES NOT DECIDE.** The resolution order when a
customer's identifier is itself a uuid. FR-003 requires that it be defined, documented
and tested; it does not say which way. The measurement that bears on it is in the
spec — **0 of 41,768** — and the decision belongs with the cost of each order, which
is `/speckit-plan`'s research.
