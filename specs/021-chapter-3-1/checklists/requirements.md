# Specification Quality Checklist: Tutorial Chapter 3.1 — Tenants All the Way Down

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-04
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

Validation ran in two passes.

**First pass — three issues found and fixed:**

1. *Implementation detail leak.* FR-009 originally said the two-environment
   rule must be enforced "by a database constraint", and SC-004 named the
   table. Both were rewritten to state the behaviour ("enforced at the storage
   layer, not only in application code"; "an attempt to give an application a
   third environment fails") and leave the mechanism to planning.
2. *Untestable success criterion.* An earlier SC read "signup feels
   effortless". Replaced by SC-001/SC-002, which name what must be observable
   without measuring a feeling.
3. *Unbounded scope.* The first draft did not say whether roles, invitations,
   deletion, API keys or the dashboard were included. Five explicit assumptions
   now bound the chapter against docs/07's Part 3 table, and Edge Cases names
   the seams that stay.

**Second pass — clean.** All items pass.

**Clarifications considered and resolved by informed default** (recorded in
Assumptions rather than asked, per the ≤3 rule and the "reasonable default"
test):

- *Real OAuth provider vs. a stand-in.* Resolved to "teach the real flow,
  test through a local stand-in", matching how the series already handles
  dev-secret JWTs (2.5) and the environment header (2.2). Both readings were
  reasonable; the series' own precedent settles it.
- *Where the signup surface lives.* No dashboard exists until Part 5, so the
  chapter builds a backend surface exercised by tests and a walk script.
- *Whether 3.1 retires the `x-relay-environment` seam.* docs/07 assigns
  credentials to 3.2; the seam stays, and the chapter must say so (FR-006).

**Open risk for planning, not a spec gap:** the source documents contain no
ADR for the identity provider or the tenancy hierarchy. If chapter 3.1 makes a
decision of that weight, `/speckit-plan` should schedule an ADR in docs/05 plus
a docs/06 deep dive, as ADR-15/16/17 did during the stack re-foundation.
