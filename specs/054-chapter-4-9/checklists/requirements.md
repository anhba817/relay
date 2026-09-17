# Specification Quality Checklist: chapter 4.9 — "Milestone: the meter agrees"

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-17
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

**This project's specs name files and clauses on purpose, and that is not a checklist
failure.** The "no implementation details" item is read here as *no decisions the plan should
make* — no chosen algorithm, no chosen library, no chosen file layout for new work. Existing
artifacts are named because a requirement about a thing that already exists is untestable
without saying which thing: `usage_periods`, `daily_usage_billing` and `scripts/scale/` are
the subjects of the measurements, not proposed designs. The same reading was applied to
features 046 through 053.

**Every number in the "What was measured" section was taken on 2026-09-17**, before the
requirements were written, against the running lane. Two of them falsify the brief this
chapter inherits:

- `docs/12` §2.3 says `scripts/scale/` *"has no analytical-volume mode and needs one"*.
  It has had one since chapter 4.2. What it does not have is the **operational counter**
  side, which §2.3 did not anticipate because chapter 4.7 had not yet found that every
  tenant in the platform is one-sided.
- The brief's *"the planted drift is caught"* is already true as a test and has never been
  true as a gate: the gate stops at the first failure and the api lane carries six, none of
  them the reconciler's.

**Three scope questions were resolved by measurement rather than left as clarifications**:
whether the milestone verifies the original or the amended FR-ANL-06 (the amended one — the
original's bound is unreachable for three of four quantities), which quantity the figure is
about (messages sent, the only one that can meet 0.1%), and what volume the measurement needs
(100,000 per tenant-period, from the smallest-expressible-drift table).
