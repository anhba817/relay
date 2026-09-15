# Specification Quality Checklist: chapter 4.6, "metering you can bill on"

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-15 · **Re-run after analysis pass 6**
**Feature**: [spec.md](../spec.md)

**Measured, not asserted**: 23 FR · 13 SC · 5 user stories, all with acceptance scenarios ·
7 edge cases · 0 placeholders · 0 vague adjectives · every FR and SC cited by a task.

## Content Quality

- [X] No implementation details (languages, frameworks, APIs) — **with a stated exception**
- [X] Focused on user value and business needs
- [X] Written for non-technical stakeholders
- [X] All mandatory sections completed

## Requirement Completeness

- [X] No [NEEDS CLARIFICATION] markers remain
- [X] Requirements are testable and unambiguous
- [X] Success criteria are measurable
- [ ] Success criteria are technology-agnostic (no implementation details) — **see note**
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

**The two technology items are failed deliberately, and the reason is what this project is.**
The deliverable is a tutorial chapter about a specific store. A criterion reading *"users see
their usage instantly"* would be untestable here and would describe nothing a reader builds;
`sum()` with `GROUP BY` over a `SummingMergeTree` **is** the subject, and SC-005 exists because
047 measured that view returning `1000 1000 1000` where the truth was 3000. Every spec in this
series (046 through 050) fails the same two items for the same reason and records it rather
than rewording until they pass.

## What six analysis passes changed, and why this file was rewritten rather than ticked

**This checklist was five passes stale when pass 6 found it.** It certified a spec with 21 FR
and 11 SC — a green tick on a document that no longer existed. Re-run against the current one,
with the history rather than only the verdict:

| Pass | Found | Spec effect |
|---|---|---|
| 1 | 10, incl. the plan citing the weaker half of constitution III | FR-018a, SC-012 added |
| 2 | 6, incl. **no task loaded a corpus** and the loader is the prohibition | FR-001 split, FR-001b added |
| 3 | 4, incl. US1 still claiming all four quantities after that split | US1 retitled, **US1a** added |
| 4 | 4, incl. a numbering claim that its own document had broken | US1a scenario 4 corrected |
| 5 | 3 — four passes of fixes had never left three files | quickstart and contract rebuilt |
| 6 | 3, incl. **a superseded probe still in `baseline.txt`** | Dependencies and Edge Cases |

**The three premises checked before the spec was written all still hold**, re-verified: the
brief asks for a view that has existed since 4.2; FR-ANL-05 names four quantities and
FR-ANL-09 four dimensions where the shipped view carries two of each; and `analytics/query.mjs`
is referenced by no script, service or config.

**Two open items nobody had claimed remain this chapter's**: SRS Appendix C question 4, and
`docs/12` §7.1 — the defect 4.5 found at §7.2, one entry over, which survived the chapter that
found it.

**What the passes added that the first draft could not have known**, all measured: the rollup's
source has no producer at all (R9); two views with disjoint columns do merge into one row, and
the first probe of that did not test it; 44 of 99 connections have no close record; and the
only way to demonstrate the rollup is to run the cross-path read the chapter is amending.

**Yield fell 10, 6, 4, 4, 3, 3 and never to zero.** Three of pass 4's four were downstream of
pass 3's repair, and pass 5's finding was that the repairs had stayed inside three files.
