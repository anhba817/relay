# Specification Quality Checklist: chapter 4.3 — the consumer that was promised

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-13
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

**Two items were failed on the first pass and fixed rather than argued.**

**"No implementation details"** — the spec named `analytics/apply.mjs`, the `ANALYTICS`
stream, `services/api/src/consumer/runtime.ts` and `publishAttempt`. Kept. This is a
specification for a **tutorial chapter**, and the premise it rests on is which code exists
and what it does: the chapter's whole opening is that a named publisher has been filling a
named stream that nothing reads. A spec that said "an existing producer writes to a queue"
would be unfalsifiable, and this project's most expensive defects have all been artifacts
agreeing with each other and not with the tree. The named paths were each verified by
running or reading them, and every one is a dependency rather than a design choice.

**"Success criteria are technology-agnostic"** — SC-005 and SC-006 name PostgreSQL and
`analytics/apply.mjs`. Kept for the same reason, and because constitution III's two-paths
rule is a claim about named stores; stating it abstractly would make it untestable.

**The scope decision was not guessed.** Chapter 3's planned subject shipped in 4.2, checked
item by item, so 4.3's identity was a real fork. It was put to the user, who chose one
chapter with Part 4 contracting 23 → 22 rather than a pre-emptive split.
