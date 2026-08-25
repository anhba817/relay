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

**FR-006 was the chapter's real decision and it is now made: deliver.** A key-authenticated
REST send reaches the channel's connected members, with a null sender in the frame.

The deciding fact was found while asking the question rather than while answering it:
`MessageWithSender.user` is already `string | null`, and `GET /v1/channels/:channelId/messages`
already returns `user: null` for exactly these rows. **The socket frame is the only
representation in the platform that cannot express a message the REST API already returns** —
so nullable is alignment rather than novelty, and a synthetic sender would have created a
second spelling of "no author" alongside the one chapter 3.16 depends on.

The decision carries a published protocol change, and FR-006c requires the chapter to name it
rather than let it land quietly. Three assertions are known to fail on the build that makes it,
including one written in chapter 3.16 three days ago — that is the exact-shape instrument doing
its job, the same way `codes.test.ts` failed when close code 4003 was added.

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
