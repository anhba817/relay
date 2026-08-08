# Specification Quality Checklist: Tutorial Chapter 3.2 — Keys and Tokens

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

Validation ran in two passes over 24 functional requirements and 10 success
criteria. All 12 requirement identifiers cited (FR-AUT-01…12, NFR-SEC-02/06,
FR-TEN-05, EIR-API-04, FR-DSH-01) were verified to exist in `docs/04-srs.md`.

**First pass — three issues found and fixed:**

1. *Implementation detail leak.* Draft FR-008 named a specific hashing
   algorithm and FR-014 named the guard class to delete. Both rewritten to
   state the property — "persisted only as a salted hash", "the header MUST no
   longer determine any tenant scope" — leaving the mechanism to planning.
2. *Untestable criterion.* An earlier SC read "the two credentials are hard to
   confuse". Replaced by SC-004, which asserts the error text names what was
   presented and what was expected, and by SC-008, which is mechanically
   checkable.
3. *Unbounded scope.* The first draft did not say what happened to FR-AUT-11 and
   FR-AUT-12, nor where the first key came from. All three are now explicit
   assumptions, and the first-key question also appears in Edge Cases because a
   reader will hit it immediately.

**Second pass — clean.** All 16 items pass.

**Decisions taken by informed default rather than by asking** (each grounded in
docs/07, the SRS, or series precedent, so none met the bar for a clarification):

- *The console session is not in this chapter.* docs/07 gives 3.2 two
  credentials; the SAD's context view gives dashboard users an OAuth session,
  which is Part 5's material alongside FR-DSH-01.
- *The first key comes from signup*, since no session exists to authenticate a
  request for one — and FR-AUT-02's "displayed exactly once" fits the signup
  response precisely.
- *Key management endpoints are deferred*, not half-built: the capability is
  tested at the layer, the authenticated surface waits for the dashboard, the
  same treatment 3.1 gave a second application.
- *FR-AUT-11's second clause is deferred* because the protocol's frame union has
  no refresh message — verified: zero matches for "refresh" in `frames.ts`.

**Carried into planning as a real constraint, not a spec gap:** FR-015 says the
gateway must keep its hands off the database (ADR-05), but it now has to verify
tokens signed with a per-environment secret it cannot read. How that secret (or
the verification itself) reaches the gateway is a design decision with security
consequences — shipping the secret to the gateway versus asking the api to
verify — and `/speckit-plan` should decide it explicitly.

**One correction this feature owes an earlier chapter:** 3.1's SkipAhead tells
readers "no session — that is 3.2's". FR-024 requires that be fixed forward.
