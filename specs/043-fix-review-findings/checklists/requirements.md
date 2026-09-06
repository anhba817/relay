# Specification Quality Checklist: Fix the platform implementation review's findings

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-05
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

**Re-derived at the end of analysis pass 10, not at specification time.** This file said "All
items pass" about a specification that had since gained three requirements and two criteria
across ten analysis passes, and still described three `[NEEDS CLARIFICATION]` markers as the
live state. A checklist that certifies a document it has not read is the defect it exists to
catch.

**Current counts**: 34 functional requirements, 13 success criteria, 78 tasks, traceability
0 untraced. **Re-derived, not carried** — it read 72 until `sweep.py` measured it during
US1's verification. Six were added since, every one of them work this feature found while
testing its own fixes rather than work it planned: eight more spawn helpers on
hand-allocated ports, two health probes on a route the api has never served, a budget test
straddling a wall-clock minute, and a fence checker that could amend a published file but
never retire one.

**The ids are deliberately not named here**, and `check-refs.py` is why — it caught this
paragraph citing two of them on the run that added it. A task id in another artifact
survives a renumber as a valid id attached to unrelated work, so the rule is that task ids
live in `tasks.md` and everything else describes the task.

The three markers at FR-023, FR-024 and FR-025 were answered in the specification phase and
became eight requirements:

| Was | Answer | Now |
|---|---|---|
| FR-023 | Retire the generate step; migrations are hand-written and reviewed | FR-023, FR-023a |
| FR-024 | Split per assertion rather than move or stub the whole file | FR-024, FR-024a |
| FR-025 | Amend the two clauses to state what the platform does | FR-025, FR-025a, FR-025b, FR-025c |

**FR-025c is the guard that answer needed.** "Amend the clause" and "weaken the clause" are one
edit apart, so the requirement fixes the measured behaviour as the upper bound on what an
amended clause may permit.

### The implementation references the specification names on purpose

**Certified against 34 requirements and 13 success criteria.** Ten code-shaped references
appear in `spec.md`, each deliberately, and each belongs to one of three classes. A
specification for business stakeholders that names a file is making a claim about the tree, and
the class says which kind:

| Reference | Class | Why the spec names it |
|---|---|---|
| `codes.ts` | the error registry | new webhook codes and the close-code set live there |
| `internal.ts` | a send door | one of the three the message-length rule must reach |
| `repository.ts` | the quota path | cited to correct the review's bot finding, not to change it |
| `relay-tutorial/fences/post-series.md` | published listings | every platform change carries an amendment there |
| `docs/09-platform-implementation-review-2026-09-03.md` | the input | the document this feature is named after |
| `docs/07-tutorial-plan.md` | the schedule | where the deferred roadmap rows actually live |
| `channel.created` | an event type | declared by FR-WHK-02, unbuilt, and named by 838 stored subscriptions |
| `mesage.updated` | a typo, deliberately | the misspelling the webhook finding is actually about |
| `specs/041-chapter-3-23/gaps.md` | a predecessor's record | holds the items this feature closes |
| `specs/042-chapter-3-24/gaps.md` | a predecessor's record | same, one chapter later |

**This enumeration was missing for eleven analysis passes**, and `check-checklist.py` reported
all eight on every run from pass 9 onward. Pass 10 read one instrument's complaint carefully and
filed the other two as the predecessor's configuration without reading them. Twenty-three of
those twenty-four complaints were real.

### What ten analysis passes added after this checklist was first written

    FR-006a  the container-free lane must still exercise something
    FR-021a  the ordering gate reads this feature's own criteria too
    FR-026   the lane's port allocation is recorded where the next reader looks
    FR-027   published material this feature falsifies is amended, per story
    SC-012   the integration lane stays inside its budget, or the budget moves with a reason
    SC-013   every one of the review's twenty-one rows carries an outcome

**Two of those six were added with no task behind them** and caught one pass later. The
requirement-to-task direction was checked from the first pass; the task-to-requirement
direction was not checked until pass 3, and neither was checked mechanically until pass 9.
