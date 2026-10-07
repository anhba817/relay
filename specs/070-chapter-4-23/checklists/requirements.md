# Specification Quality Checklist: chapter 4.23, "The channel a socket names"

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-06
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

**EVERY NUMBER IN THIS SPEC WAS MEASURED BEFORE IT WAS WRITTEN**, not carried from
the chapter that found the gap. Re-run at specification time, 2026-10-06:

    frame schemas carrying `channel`                        7
    gateway sites writing `channel:` onto a frame          21
    the gateway's references to a channel's external id     0
    internalSendRequestSchema.channel_id            z.string().uuid()
    FR-RTM clauses naming an identifier                 0 of 10

**TWO ITEMS CARRY A JUDGEMENT A PLANNER MAY OVERTURN.**

*No implementation details* is marked complete, and the spec does name
`internal.ts`, `session.controller.ts` and the seven schemas. That is deliberate
and it is the same call 068's spec made: **the defect is a field in a published
contract**, and a specification that described it without naming it would be
unverifiable. The requirements themselves name no mechanism — FR-004 says *the
gateway's client edge* and not how the map is built.

*Scope is clearly bounded* rests on FR-004, the assumption that 4.22's division
holds here. **If the premise check finds that the subjects or the resume cursors
have to move**, the bound moves with them and this becomes a larger chapter than
~50 fence pages. **MEASURED TWICE SINCE: 83 English pages across 9 files at
`/speckit-plan`, then 11 files at analysis pass 1, which found the gateway calling
a second api→gateway contract this bill had never counted.** The subjects and the
cursor storage did not have to move; the estimate was wrong for a different
reason, which is that it was a list rather than a trace. The plan should check that before it believes the estimate — 4.15's
rule, and 068 charged 9 files against a bill of 8.

**WHAT THIS SPEC DELIBERATELY DOES NOT DECIDE.** Whether the Relay identifier is
accepted on the socket forever, refused later, or refused now. FR-003 requires only
that it not misroute silently; which of *keeps working* or *named refusal* is right
belongs with the cost of each, which is `/speckit-plan`'s research.
