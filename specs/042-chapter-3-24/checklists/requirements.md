# Specification Quality Checklist: Chapter 3.24 — the message that is not only text

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-04
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

**All items pass.** Both [NEEDS CLARIFICATION] markers were put to the reader and resolved;
the spec's "Decisions taken during specification" section records each answer with the
alternative that was refused and why, so the next reader inherits the argument rather than the
conclusion.

    FR-003, FR-003a, FR-003b    external URL only; `media_id` refused with a code of its own
                                until §4.14 exists, and the shape is a discriminated union
                                from the first version so Part 4 adds an arm
    FR-019, FR-019a, FR-019b    an attachments-only message stores `text = ""`, not a null,
                                so chapter 3.23's tombstone predicate is untouched

**Three implementation details are named deliberately** — `messages.attachments`,
`frames.ts:14` and `docs/05-sad.md:608`. They are the evidence that the requirement is unmet
and the record of where the existing state is, which this project's specs carry on purpose;
none of them prescribes a design.

**One requirement is about a document rather than behaviour.** FR-018 asks for a comment in
the published protocol to be corrected, because it schedules attachments for Part 4 and the
SRS marks the clause P2. Chapter 3.23 found four sentences in that state and recorded that
**no checker reads prose**, so a requirement is the only instrument that will catch it.
