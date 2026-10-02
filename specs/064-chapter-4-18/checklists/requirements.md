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

## Re-validated after ten analysis passes, and two of the ticks above were false when made

**The 16 items are ticked again and the ticks mean something different now.** The first
validation happened before any analysis pass; ten have run since and found **four CRITICALs**.
Two items were ticked while the thing they assert was untrue, and this section says which,
because a checklist that only records its final state is a checklist nobody can audit.

| item | was it true when first ticked? | what made it true |
|---|---|---|
| Success criteria are measurable | **No.** SC-002 demanded that *"every path that could modify or remove an entry is attempted and refused"* while research R2 had already measured two paths that modify an entry and are not refused. SC-003's equality counted the router's 33 mutating routes against a set FR-002 scopes to 25. | pass 1, F1 and F3 |
| Requirements are testable and unambiguous | **No.** FR-005 required the entry written inside the action's transaction and FR-012 forbade changing any action's behaviour; four of seven candidate methods have no transaction, so the pair was unsatisfiable for `unbanUser`, `setMemberRole`, `archiveChannel` and `unarchiveChannel`. | pass 2, G1 — FR-005a, FR-005b and FR-012's named exception |
| All functional requirements have clear acceptance criteria | Thinly. FR-012 had no success criterion at all. | pass 1, F12 — SC-007a |
| Edge cases are identified | **Yes, and identified is not handled.** Edge case 4 described a route whose answer depends on the credential, and the classification had two values until pass 7. | pass 7, M1 — `moderation-when-application` |

**The other twelve were true and are still true.**

### What ten passes cost and produced

    pass  1   9 findings   artifact against artifact
    pass  2   5            artifact against the tree                      1 CRITICAL
    pass  3   5            the tree, and pass 2's own fixes
    pass  4   4            the precedent it cites
    pass  5   3            the same, remaining citations
    pass  6   4            the artifacts' structure after five rounds of edits
    pass  7   2            the spec's Edge Cases and Independent tests     1 CRITICAL
    pass  8   3            the constitution's constraints section          1 CRITICAL
    pass  9   2            the documents cited but never opened            1 CRITICAL
    pass 10   3            ADR-26, which pass 9 cited and did not open

**Four of ten passes found a CRITICAL and three of those were consecutive, at 7, 8 and 9 —
the passes with the lowest counts.** Each came from opening something no earlier pass had: the
edge-case list, the constitution's constraints section, the ADR register. The count fell from
nine to two and the severity did not move. **A yield curve measures what is left to find only
if every pass looks in the same place**, and these did not.

**And pass 9 committed the defect pass 4 had named.** It cited ADR-26 as this chapter's mirror
on the strength of its title; opening it in pass 10 produced two more findings. *Citing a
precedent is not reading it* has now caught three artifacts and one analysis pass.

## Analysis pass 1 — what it found, and one thing it did not

Nine findings: three HIGH, four MEDIUM, two LOW, **no CRITICAL**. All nine were fixed.

The two worth remembering are both **acceptance criteria that could not be met as written**.
SC-002 said *"every path that could modify or remove an entry is attempted and refused"* while
research R2 had already measured two paths that modify an entry and are **not** refused —
`SET session_replication_role = replica` and `DROP TRIGGER`. SC-003's equality counted the
router's 33 mutating routes against a set FR-002 scopes to the 25 a tenant can reach. Both
would have been met at close-out by quiet reinterpretation, which is the shape this chapter is
about: a sentence survives because the thing beside it is right.

**AND THE MECHANICAL COVERAGE MAP RAISED FIFTEEN ALARMS AND ALL FIFTEEN WERE FALSE.** Grepping
`tasks.md` for each requirement id shows 15 of 24 uncited — FR-001, FR-002, FR-003, FR-006,
FR-007, FR-009, FR-010, FR-011, FR-013, SC-001, SC-003, SC-005 among them — and every one is
covered in substance by tasks that name the work instead of the identifier. Chapter 4.11 ran
the same instrument and got 14 of 14 false. **Recorded here so the next pass does not raise it
a third time**, and it is why `traceability.md` is built by reading.

## Risks this spec is carrying on purpose

- **The moderation set is a rule, not a list, and the rule will misclassify.** The router
  serves **24** mutating tenant-reachable routes, of which nine are the expected inclusions —
  *"mutating, tenant-reachable, acting on something other than the caller, **and where the
  caller decides, the credential decides**"*. The ones it gets wrong are the chapter's findings,
  and the spec says so rather than predicting the answer. **This entry said "admits nine routes
  today" and described a two-valued rule** until analysis pass 16: the population was corrected
  in the spec at pass 2 and the third case added at pass 7, and neither correction reached
  here. *After correcting a number, grep the feature directory for the old one.*
- **The structural argument for this chapter going first is the shape of two recorded
  defects.** *"Everything after it writes to it"* describes a store whose writers arrive
  later, which is chapter 4.6's rollup and chapter 4.16's column. The spec's defence is
  measured — FR-MOD-02 and the ban pair already ship — and if phase 1 finds those writers
  thinner than claimed, **the honest outcome is a different chapter order, not a louder
  argument**.
- **~~The read path may belong to row 23.~~ CLOSED.** It is this chapter's, on the grounds
  that a store with no reader is a defect this project has recorded twice — chapter 4.6's
  rollup and chapter 4.16's column. The contract is written, and pass 7 settled the split that
  made it work: **US1 reads through the repository and US2 owns the route**, so the MVP can
  verify itself without the next story's code.
