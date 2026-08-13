# Specification Quality Checklist: Tutorial Chapter 3.5 — Webhooks That Survive the Customer

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-10
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

**Clarification resolved (2026-08-10).** The dispatcher ships as its own
deployable service, and the chapter is narrowed to compensate: the attempt log
(FR-WHK-06) and auto-disable (FR-WHK-07) move to a follow-on chapter. The two
travel together because auto-disable needs continuous-failure history and that
history *is* the attempt log.

**The ledger question was not a choice.** Chapter 3.4's research R5 framed it as
"an internal route for its ledger or an explicit ADR amendment". Constitution
Principle IV already answers it — "Only the API service writes to PostgreSQL…
Other services obtain writes and backfill reads via the API service's internal
endpoints" — so FR-014 states the constraint rather than leaving it open. An ADR
amendment would be a constitutional act, not a planning decision.

**On "no implementation details".** Two places came close and are deliberate:

- FR-013/FR-014 name a service boundary and internal endpoints. That is a scope
  decision taken by the author and a constraint quoted from the constitution, not
  a design choice made here. The spec says nothing about how the dispatcher is
  built, packaged, or how it talks to the stream.
- The spec says "a signature computed over the request body" rather than naming
  HMAC or a hash function, "a bounded, widening schedule" rather than restating
  FR-WHK-03's delays, and "a stated timeout" rather than a number. Where a source
  requirement already fixes a value — six attempts, five endpoints — the spec
  cites the requirement rather than repeating the number as a fresh decision.

**On FR-003 and FR-018.** These are the chapter's spine and are deliberately
phrased as obligations to *state* something rather than to build something. The
delivery guarantee is a documentation act as much as an engineering one: an
at-least-once webhook that customers believe is exactly-once is worse than one
they know to deduplicate.

**On FR-029.** Carried forward from chapter 3.4's reconstruction, where two files
the prose asserted were never fenced and could not be recovered. FR-028 only
constrains fences that exist; FR-029 constrains the gap between what the prose
claims and what the chain carries.

**Three items worth watching into planning:**

1. **FR-023's "survives a restart" is the hard requirement.** A six-attempt
   schedule stretching to two hours cannot live in process memory, and the
   dispatcher cannot write its own Postgres row (FR-014). Settle where a pending
   retry lives before anything else is built — it shapes the whole service.
   SAD §4.1's phrasing ("JetStream redelivery + a scheduled-retry stream") is a
   sketch, not a decision.

2. **The first new deployable since Part 1 has a long tail.** A service means a
   container image, a compose entry, build orchestration, a CI job, and coverage
   surface. Feature 024's instrument now applies to it. Cost the fence budget
   early — 3.4 was the first chapter to land inside its estimate, and this one has
   more moving parts.

3. **The dead-letter store is the first store whose purpose is retaining
   tenant-visible content that failed to leave.** The outbox and the
   consumed-events ledger were both exempted from tenant scoping as platform
   bookkeeping; this one is not analogous. Decide its scoping and retention
   deliberately rather than by resemblance to its predecessors.
