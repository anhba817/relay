# Specification Quality Checklist: Chapter 3.17 — the message that never arrived

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-25
**Feature**: [spec.md](../spec.md)

## Content Quality

- [X] No implementation details (languages, frameworks, APIs)
- [X] Focused on user value and business needs
- [X] Written for non-technical stakeholders
- [X] All mandatory sections completed

## Requirement Completeness

- [ ] No [NEEDS CLARIFICATION] markers remain
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

**One marker remains, on FR-006, and it is the chapter's actual decision** rather than an
underspecified detail. A key-authenticated REST send carries no user by design (chapter 3.3),
and the frame contract requires one — so "deliver it" and "do not deliver it" are both
coherent and lead to different chapters. No reasonable default exists: one changes a published
protocol shape, one leaves an integration path permanently broken-by-design and documents it.

**On "no implementation details":** the spec names `toFrame`, `messageSchema`,
`public-surface.itest.ts` and the SAD's C4 arrow. Retained deliberately — this is a
specification for a *tutorial chapter about a specific codebase*, and the series' convention
(chapters 3.10 through 3.16) is that a spec cites the artifact whose behaviour it is changing.
A reader who cannot see which test pins the current behaviour cannot check the claim.

**Two claims in this spec were measured rather than carried**, and both corrected the record:
- chapters 3.12/3.13 recorded **two** independent causes; there is now **one**, because
  chapter 3.15's attributed public send closed the other without anyone noticing
- `public-surface.itest.ts`'s name claims more than the test proves — it pins the
  application-credential path only
