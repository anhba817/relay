# Specification Quality Checklist: Chapter 4.12 — a link that expires, and who may hold it

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

**16 of 16, and two of them were argued rather than ticked.**

**"No implementation details" against a specification naming GIN `jsonb_path_ops`.** FR-008
requires the lookup to be indexed and the Assumptions name the index type, which is closer to
implementation than this checklist likes. It stays because **the numbers were measured before
the specification was written** and a figure without the thing that produced it is not
reproducible: 0.082 ms against 2.132 ms means nothing unless the reader knows what was built.
The requirement is *"indexed, with the before-and-after published"*; the index type is recorded
as an assumption a later chapter may overturn by re-measuring, which is the honest shape.

**"Success criteria are technology-agnostic" against SC-004, which names buffers.** Milliseconds
alone would have let a warm cache report a win that a cold one does not — 4.1 spent three
measurements learning that a delta between two totals is not a measurement of the thing that
changed. `Buffers: shared hit` is what makes the comparison a fact about the query plan rather
than about the machine, so the criterion names it.

**No `[NEEDS CLARIFICATION]` markers, and one flagged assumption instead.** The object with no
referencing message is a real hole in FR-MED-08 and the specification takes a position on it
rather than asking, for the reason 4.11 established: the same shape there was settled **against**
the specification by `research.md`, producing SRS 1.18. A flagged assumption gives research
something to attack; a clarification marker gives it something to wait for.

**What this checklist cannot say.** It cannot say whether the permissive reading is right, and
it cannot say whether ten validators is still ten now that a read path joins them — 4.11's
`data-model.md` §4b was complete when it was written and wrong two passes later. Both are
`/speckit-plan`'s and `research.md`'s to answer.
