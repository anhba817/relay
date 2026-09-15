# Specification Quality Checklist: chapter 4.7, "the job that checks the meter"

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-15
**Feature**: [spec.md](../spec.md)

**Measured, not asserted**: 23 FR · 13 SC · 4 user stories, all with acceptance scenarios ·
6 edge cases · 0 placeholders · 0 vague adjectives.

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

**The two technology items are failed deliberately**, as in every spec of this series (046
through 051). The deliverable is a tutorial chapter about a specific store, and a criterion
reading *"users trust their invoice"* would be untestable and would describe nothing a reader
builds. Each spec records the failure rather than rewording until it passes.

**Four premises were measured against the tree before this spec was written**, and the fourth
is the one that reframed the chapter:

1. `docs/12` §3 row 8 is *"The job that checks the meter"*, movement IV, and **no §7 open
   question owns it** — 7.3 is ch 14, 7.4 ch 15, 7.5 ch 20.
2. `message_events` still holds **0 rows** while the operational side holds 9,624. The first
   quantity the job compares disagrees by **100%**, and chapter 4.6's `gaps.md` 051-1 says why.
3. §2.3 has already split the milestone — a planted-drift CI gate, and the 0.1% figure
   measured once at real volume — with the reason: *"0.1% of a small number is an assertion
   that cannot fail for its own reason."*
4. **`messages` holds 9,650 and `usage_periods.messages_sent` holds 9,624 — a 0.2694% gap
   between two operational counters**, nearly three times the bound FR-ANL-06 sets for the
   analytical comparison. *"Counts derived from operational data"* is not one number, and
   nothing in the clause says which.

**Two carried items are this chapter's to settle.** `gaps.md` 047-1 and 048-1 — DR-10 and
FR-ANL-06 cannot both hold, for two independent reasons — were filed *for movement IV* and
have been carried through four features. FR-015 and SC-010 require them re-measured and either
closed or restated.

**What the chapter is expected to find**: that the reconciler's first honest run fails four
ways, and that three of the four are not the analytical path's fault. A chapter that published
a green percentage here would be the most misleading artifact in the series.

**Expect `/speckit-analyze` to find more.** 051 ran seven passes at 10, 6, 4, 4, 3, 3, 2 — and
the finding that mattered most, the channel key costing the billing read 525×, arrived in
implementation rather than analysis, because no pass loaded a corpus.
