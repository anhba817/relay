# Specification Quality Checklist: Chapter 4.2 — ClickHouse from zero

**Purpose**: Validate specification completeness and quality before `/speckit-plan`
**Created**: 2026-09-13
**Feature**: [spec.md](../spec.md)

**Counts, stated so drift is detectable.** 046's first checklist ticked sixteen boxes and
stated no numbers, which made it impossible to compare against the document it certified —
and the spec then moved underneath it four times.

    functional requirements      16   FR-001 … FR-015, with FR-006a
    success criteria              8   SC-001 … SC-008
    user stories                  3   P1, P2, P3
    acceptance scenarios         10   3 + 4 + 3
    edge cases                    5

## Content Quality

- [x] No implementation details (languages, frameworks, APIs) — *interpreted; see Note 1*
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders — *interpreted; see Note 1*
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic — *see Note 1*
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification — *see Note 1*
- [x] Every functional requirement is cited by a scenario or a criterion

## Notes

**1. Four items are marked against this project's convention rather than the template's
literal reading**, for the reason 046's checklist gives: a chapter specification's subject is
**the repository**, and a version stripped of `message_events`, `ORDER BY (environment_id, ts)`
and the plan's parts-skipped figure would describe nothing a writer could act on.
`specs/042-chapter-3-24/spec.md` is the published precedent.

**2. THE FEATURE'S PREMISE CHANGED BEFORE THE SPEC WAS WRITTEN, AND THAT IS RECORDED IN IT.**
`docs/12-part-4-structure.md` called 4.2 "The index that would fix it". Chapter 4.1 shipped
with that material — its published sections include *The index that should fix it* and *And
what it costs to keep* — at 2,132 prose words, inside the bound. Movement I is one chapter,
Part 4 is 23, and both records were amended before this spec existed rather than after it
disagreed with them.

**This is the first estimate in the project that was too high.** Every prior correction ran
the other way: Part 3 planned as seven and shipped 26. `docs/12` §3 still warns that 23 will
not be 23, and it is now warning in both directions.

**3. Four requirements exist because 046 was measured rather than assumed.**

- **FR-010** asks for parts read and skipped, not just a duration — because a store that
  scans everything still answers a million rows quickly, and **fast is not the same as
  ordered**.
- **FR-009** asks for the rollup's distinct count against an exact one, because `uniqState` is
  approximate by construction and an error of zero at a million rows will not stay zero.
- **FR-006a** asks for columns with no producer to be named, because SAD §6.2 publishes
  `delivery_latency_ms` and nothing in the operational store records it. 3.24 and 3.23 both
  found readers with no writers; this is the reverse and the same defect.
- **FR-012** separates the two stores' ledgers, because `gaps.md` 045-69 is what one identity
  scheme going wrong cost.

**4. Three things are inherited and re-measured rather than carried.** `check:fences` opens
where 4.1 closed it (110, APPLY 74, HEAD 36) and the assumptions say to re-measure it; 4.1's
585.9 ms is quoted **with the corpus and machine it was taken on**, from
`specs/046-chapter-4-1/baseline.txt`; and the tag convention is `part4-chN`, settled in 046.

**5. No [NEEDS CLARIFICATION] markers.** The decisions that would have produced them — one
node (ADR-08), `message_events` first (SAD §6.2), no ingester (movement II's boundary) — are
settled in published documents and cited rather than reopened.
