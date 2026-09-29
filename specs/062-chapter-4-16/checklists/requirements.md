# Specification Quality Checklist: Chapter 4.16 — "Storage on the bill"

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-29
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

Three items pass under this project's conventions rather than the generic reading, the same
three as 061 and for the same reasons:

- **"No implementation details" / "non-technical stakeholders".** The premise-check table names
  columns, files and row counts — `stored_delta`'s definition, `message_events` at 0 rows,
  8,120 objects across 1,576 environments. That section is *evidence for the scope*, and this
  series carries one because artifacts here have agreed with each other and not with the tree.
  FR-001 through FR-012 and every acceptance scenario are free of it.
- **"Technology-agnostic success criteria".** SC-010 names `pnpm check:fences`, `pnpm lint` and
  the CI comparison. The deliverable is a tutorial chapter whose code must replay onto a
  repository, so those are outcomes rather than techniques. SC-010 gained `pnpm lint` and
  `turbo run typecheck` by name because **061's CI failed on a lint that no task listed**.
- **Two requirements are met by a document.** FR-011 (record what cannot be discharged) and
  FR-012 (state what the delta approach costs) are discharged in writing. Both carry a
  measurable outcome — SC-008 and SC-009 — so neither can be satisfied by silence.

Defects found by running this checklist and fixed before it was marked complete:

1. **The vocabulary section was added because the premise check found a name collision.**
   `stored_delta` counts stored *messages*. Without stating "level" and "delta" separately up
   front, FR-001 and FR-003 read as the same requirement.
2. **FR-010 exists because the assumptions contradicted themselves.** A rendition is not an
   upload but its bytes are in the level — two different answers about one object, which is how
   a count and a sum drift apart. The requirement forces one answer per question and the same
   answer at every reader.
3. **SC-004's duplicate scenario was implicit in an edge case.** Promoted, because 4.15's
   idempotence bug class was caught by issuing a deliberate duplicate rather than reasoning that
   the guard upstream made it impossible.

Four open questions go to planning rather than becoming [NEEDS CLARIFICATION] markers. Each
needs a measurement — what the reconciliation can list, what widening an existing rollup costs
to read, whether a third analytical producer is affordable — and `research.md` is where this
project answers that kind of question. None blocks planning.
