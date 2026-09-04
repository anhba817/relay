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

**All items pass, re-validated at analysis pass 14** against a spec that now carries 27
requirements, 6 success criteria, 8 edge cases and 9 acceptance scenarios. It was first
validated when the spec held twenty-four of them, and thirteen analysis passes edited it
in between without anyone re-reading this file — which is worth recording here because
`/speckit-implement` gates on these boxes, so an unre-validated checklist is an approval
nobody re-earned.

Both [NEEDS CLARIFICATION] markers were put to the reader and resolved; the spec's "Decisions
taken during specification" section records each answer with the alternative that was refused
and why, so the next reader inherits the argument rather than the conclusion.

    FR-003, FR-003a, FR-003b    external URL only; `media_id` refused with a code of its own
                                until §4.14 exists, and the shape is a discriminated union
                                from the first version so Part 4 adds an arm
    FR-019, FR-019a, FR-019b    an attachments-only message stores `text = ""`, not a null,
                                so chapter 3.23's tombstone predicate is untouched

**Eight implementation details are named deliberately, in three classes.** This note said
*three* and enumerated them. It was wrong on the day it was written — `docs/05-sad.md:342` was
already in the spec and undeclared — and four more arrived through later analysis passes. None
prescribes a design; each is evidence of where the existing state is.

    an existing column          `messages.attachments`, `users.avatar_url`
    a published source          `docs/05-sad.md:608`, `docs/05-sad.md:342`,
                                `packages/protocol/src/frames.ts:14`
    domain vocabulary and       `message.created`, `message.ack`, and two pointers to
    a sibling artifact          `data-model.md` where a decision is recorded

**Two boxes deserve a reading rather than a tick, and get one here.**

*"Written for non-technical stakeholders"* is checked in the sense this project means it: the
reader is a developer following a build, and the spec cites DDL and file lines because that is
the evidence a requirement is unmet. A reader with no code in front of them would not get far.

*"Success criteria are technology-agnostic"* is checked with one strain named: SC-003 counts
**six read shapes** and SC-004 names `http` and `https`. Both are closer to the implementation
than the guidance likes. Both stay, because a criterion that said "all read paths" could be
satisfied by whichever paths somebody remembered, and that is the failure SC-003 exists to
prevent — the count is the assertion.

**One requirement is about a document rather than behaviour.** FR-018 asks for a comment in
the published protocol to be corrected, because it schedules attachments for Part 4 and the
SRS marks the clause P2. Chapter 3.23 found four sentences in that state and recorded that
**no checker reads prose**, so a requirement is the only instrument that will catch it.
