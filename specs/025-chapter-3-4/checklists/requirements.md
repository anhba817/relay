# Specification Quality Checklist: Tutorial Chapter 3.4 — JetStream and the First Consumer

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-09 · **Reconstructed**: 2026-08-10
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

**On "no implementation details".** The spec names "the stream", "a durable
consumer" and "the ledger". The first two are the broker's own vocabulary as
ADR-02 adopts it rather than choices made here; the third is deliberately generic
so the requirement stays testable without naming a table. The spec says "event
identity" rather than a column type, and "bounded delivery attempts" rather than
a setting name.

**On FR-013 and FR-015.** The pair is the heart of SAD risk R5 and they are
phrased as outcomes rather than as a pattern: "the runtime — not the handler —
MUST be what enforces it", and a list of what a handler cannot do. A reviewer can
test both without being told how the runtime is built.

**On FR-025.** Added during reconstruction, not present at implementation time.
It requires every file the prose asserts to be fenced. It exists because the
shipped chapter breaks it — two test files are described and never fenced — and
FR-022 as written only constrains fences that exist, so nothing caught it. See
`chapter-notes.md` finding 1.

**Three items worth watching into planning:**

1. **SC-003 asks for a real signal.** The redelivery property is "what survives
   when the process stops existing", and a test that throws an exception proves
   the error path instead. Planning should confirm the 2.8/3.3 child-process
   harness can be reused rather than rebuilt, and that the acknowledgement
   deadline is short enough for the test to be tolerable to run.

2. **FR-006 asks the chapter to admit a gap.** A message that exhausts its
   delivery attempts is caught by nothing. That is uncomfortable to write and
   easy to soften into implying a dead-letter path exists. Planning should keep
   the invariant asserting the *exhaustion behaviour* rather than the absence of
   a dead letter, so it survives 3.5 adding one.

3. **The ledger has no tenant column, and that is the second such exception.**
   3.3 made the first for `outbox`. Two exceptions form a pattern, and a pattern
   needs a stated rule — planning should record what distinguishes "platform
   bookkeeping" from tenant data, rather than leaving the next chapter to judge
   by resemblance.
