# Specification Quality Checklist: Chapter 4.11 — the half of the union that was refused

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

**Named artifacts are not implementation details here, and the distinction is worth stating.**
`media_not_available`, `media_objects_state_check` and `FR-MED-06` are quoted because they are
the published contract this chapter changes — the code is in a customer-facing error reference,
the constraint is what makes one of the clause's states unreachable, and neither claim survives
being paraphrased. What is absent is how any of it is built: no table shape, no route, no
library, no query.

**One assumption is flagged rather than marked.** FR-MED-06's treatment of a tenant-uploaded
object attached by a user token has two readings with different consequences for what customers
can build. The specification takes the strict one and says why, and says what the permissive one
would permit. It is an assumption rather than a `[NEEDS CLARIFICATION]` marker because a
defensible default exists and because this project settles exactly this shape in `research.md` —
`CLAUDE.md` records the pattern from the previous chapter: *"`research.md` first — it settles the
specification's one flagged assumption against the assumption."*

**SC-002 is the criterion most likely to be weakened during planning.** "Byte-identical bodies
apart from the request id" is what makes FR-005 testable; a plan that reduces it to "all three
return 422" would satisfy the letter and lose the property, which is a cross-tenant existence
oracle. The wording is deliberate.

**Two inherited gaps bound what this chapter can claim** and are named in Dependencies rather
than left to be rediscovered: a slot nobody uploaded to is indistinguishable from one that was
(`gaps.md` 056-1), and the storage quota counts declarations rather than bytes (056-2).

---

## Analysis pass 1 (2026-09-19)

Twelve findings, no CRITICAL, all twelve applied. Three came from running something rather than
reading it, and those three changed the design:

- **422 is not in the error filter's ladder.** Measured at `protocol-error.filter.ts:67-81` —
  eight rungs and 422 is not one, so FR-009's *"a status the ladder maps"* was unsatisfiable as
  written. The chapter adds the rung (FR-009a) rather than softening the clause. Nothing throws an
  unnamed 422 today, which is the argument for the rung and not against it.
- **Nothing said how the repository learns the credential class**, which the predicate's second
  clause needs. `senderMustBeBot` exists and reusing it overloads a flag named for the sender;
  T020a decides it in writing.
- **The plan's fenced-file list was six and the tasks named nine.** Counted:
  `messages.service.ts` 26 titled fences, `codes.test.ts` 17, `vitest.coverage.config.mts` 33 —
  the last two being among the most expensive files in the chain. Wrong before a line was written,
  which is the direction 050 and 056 both recorded.

And three requirements had no task: FR-013 (delivery carries nothing new), FR-012's route-level
half, and the `docs/12` row-12 amendment that four consecutive chapters wrote. The UUID tightening
was the reverse — two tasks implementing something no requirement stated, now FR-008a.

**Requirement count moved 26 → 30** (FR-008a, FR-009a, FR-017 added; SC-002, SC-010 and FR-013
sharpened) and **task count 76 → 83**. New tasks carry suffixed ids so numbering a reader has
already seen does not move.
