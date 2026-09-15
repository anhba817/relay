# Specification Quality Checklist: chapter 4.6, "metering you can bill on"

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-15
**Feature**: [spec.md](../spec.md)

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

**The two technology items are failed deliberately, and the reason is what this project
is.** The deliverable is a tutorial chapter about a specific store. A success criterion
reading *"users see their usage instantly"* would be untestable here and would describe
nothing a reader builds; `sum()` with `GROUP BY` over a `SummingMergeTree` **is** the
subject, and SC-005 exists because 047 measured that view returning `1000 1000 1000` where
the truth was 3000. Every spec in this series (046 through 050) fails the same two items for
the same reason, and each records it rather than rewording the criteria until they pass.

**What the spec does keep technology-free**: every criterion is a quantity somebody can
measure and disagree with — rows read, a gap between two figures, a count of dimensions
answered — rather than a claim that a mechanism works.

**Three premises were checked against the tree rather than the structure document before
this spec was written**, and all three changed what the chapter is:

1. `docs/12` §3's brief says *"daily rollup materialised views (DR-10)"*. One has existed
   since chapter 4.2.
2. FR-ANL-05 names **four** quantities; the shipped view carries two. FR-ANL-09 names four
   dimensions; the view's key has two.
3. `analytics/query.mjs` is referenced by no script, service or config — the only file that
   has ever asked FR-ANL-05's question of the analytical store is one nothing runs.

**And two open items were found that no chapter had claimed**: SRS Appendix C question 4
(connection-minute precision, owner *Product / Billing*, still open, and chapter 4.5
measured the number that decides it), and `docs/12` §7.1, which still reads as open while
§3's own amendment records chapter 4.2 building all four items of its brief. The second is
the defect chapter 4.5 found at §7.2 — **it survived the chapter that learned the lesson**,
which is why FR-016 names it rather than leaving it to a later pass.

**Expect `/speckit-analyze` to find more.** Every feature in this series has: 046 ran nine
passes, 047 nine, 049 several, 050 sixteen, and in each the passes that ran a premise found
what reading could not.
