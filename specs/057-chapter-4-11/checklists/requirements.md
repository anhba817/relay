# Specification Quality Checklist: Chapter 4.11 — the half of the union that was refused

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-19
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

**Named artifacts are not implementation details here, and the distinction is worth stating.**
`media_not_available`, `media_objects_state_check` and `FR-MED-06` are quoted because they are
the published contract this chapter changes — the code is in a customer-facing error reference,
the constraint is what makes one of the clause's states unreachable, and neither claim survives
being paraphrased. What is absent is how any of it is built: no table shape, no route, no
library, no query.

**One assumption is flagged rather than marked.** FR-MED-06's treatment of a tenant-uploaded
object attached by a user token has two readings with different consequences for what customers
can build. The specification takes the strict one and says why, and says what the permissive one
would permit. It is an assumption rather than a `[NEEDS CLARIFICATION]` marker because a
defensible default exists and because this project settles exactly this shape in `research.md` —
`CLAUDE.md` records the pattern from the previous chapter: *"`research.md` first — it settles the
specification's one flagged assumption against the assumption."*

**SC-002 is the criterion most likely to be weakened during planning.** "Byte-identical bodies
apart from the request id" is what makes FR-005 testable; a plan that reduces it to "all three
return 422" would satisfy the letter and lose the property, which is a cross-tenant existence
oracle. The wording is deliberate.

**Two inherited gaps bound what this chapter can claim** and are named in Dependencies rather
than left to be rediscovered: a slot nobody uploaded to is indistinguishable from one that was
(`gaps.md` 056-1), and the storage quota counts declarations rather than bytes (056-2).
