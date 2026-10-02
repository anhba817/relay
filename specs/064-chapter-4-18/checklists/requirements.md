# Specification Quality Checklist: Chapter 4.18 — The log that cannot be edited

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-02
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

Three items failed on the first pass and were repaired rather than argued away.

**FR-009 and SC-006 named components.** They read *"MUST NOT depend on the analytical
pipeline"* and *"while the analytical pipeline is stopped"*. The obligation is a property —
recording must not depend on anything permitted to lose or delay a record — and naming the
pipeline both narrows it and dates it. Reworded to lead with the property; the pipeline is
still the thing the plan will stop, and that belongs in the plan.

**FR-012 had no success criterion.** *"MUST NOT change the behaviour of any moderation action
it records"* was unfalsifiable as written. **SC-007a** now requires the diff to be checked
rather than the constraint asserted, which is chapter 4.17's T066a applied in advance: that
feature's `git diff --name-only` returned two files and both were tests.

**Two items pass with a qualification worth stating, because a clean checklist that hides a
judgement is worse than a dirty one.**

*No implementation details* and *written for non-technical stakeholders* pass for the
**normative** text — FR-001 to FR-013 and SC-001 to SC-010 name no table, engine, language or
route. They do not pass for the **Context** section, which quotes column names, an engine, a
TTL and a method, and is deliberately concrete: it is the premise check, and this project has
found four tasks whose premise was wrong, including one that would have caused a defect. The
house style is that a chapter's context is measured against the tree and quoted, and chapters
4.16 and 4.17 both carried a Context table of exactly this shape. The one in 4.17 was
**wrong**, and reading the whole of the file it described is what found it — which is the
argument for keeping the evidence visible rather than paraphrasing it into prose a later
reader cannot check.

## Risks this spec is carrying on purpose

- **The moderation set is a rule, not a list, and the rule will misclassify.** *"Mutating
  routes an application credential can reach that act on something other than the caller"*
  admits nine routes today. The ones it gets wrong are the chapter's findings, and the spec
  says so rather than predicting the answer.
- **The structural argument for this chapter going first is the shape of two recorded
  defects.** *"Everything after it writes to it"* describes a store whose writers arrive
  later, which is chapter 4.6's rollup and chapter 4.16's column. The spec's defence is
  measured — FR-MOD-02 and the ban pair already ship — and if phase 1 finds those writers
  thinner than claimed, **the honest outcome is a different chapter order, not a louder
  argument**.
- **The read path may belong to row 23.** The spec claims it here on the grounds that a store
  with no reader is a defect this project has recorded twice. A planner who disagrees should
  move it deliberately and leave the milestone a gap it knows about.
