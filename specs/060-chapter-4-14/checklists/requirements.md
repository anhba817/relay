# Specification Quality Checklist: Chapter 4.14 — "Pending, ready, rejected"

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-28
**Feature**: [spec.md](../spec.md)

## Content Quality

- [X] No implementation details (languages, frameworks, APIs) — **argued, see Notes**
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

**16 of 16, and three were argued rather than ticked.**

**"No implementation details" against a specification that names subject grammars,
`channelsReferencingMedia` and `revisionFabricSchema`.** They stay for the reason 059's
checklist kept ClamAV: the chapter's open question — `docs/12` §7.4 — **is about the subject
grammars**, and the argument cannot be made about an unnamed fabric. The three-row table in Q1
is the requirement, not decoration: it names the payload types because ADR-19's rule is stated
in terms of payload types. Removing the names would leave FR-008 untestable.

**"Requirements are testable" against FR-008 and FR-012, which require an argument.** Both are
prose obligations — record an ADR that runs ADR-25's arithmetic, and amend SRS FR-MED-07. They
are testable in the way this project tests prose obligations: the artifact exists, it states the
two numbers, and a reviewer can recompute them. 059 carried FR-013 and FR-014 on the same terms.

**"Scope is clearly bounded" against a chapter whose brief is one clause.** The bound that
matters is what this chapter does *not* do, and it is stated twice: the state machine is 4.13's
and is not rebuilt, and `media_events` stays deferred to the erasure chapter for the reason
059's `gaps.md` 059-11 gave — its sum reads `deleted`, which has no producer until FR-MED-10.

## What the premise check changed before the first draft

Recorded because a premise that held is only evidence if you say you checked it.

- **Two findings the brief did not contain.** FR-MED-07 is two sentences, not one; and the
  attachment shape has no `state` field, so the *first* sentence is unmet as well. No artifact
  had recorded the second — SRS 1.20 says the clause is "unmet with a reachable subject" and
  reads as though the event were the only gap.
- **One finding that narrows the open question.** §7.4 reads as undecided. **ADR-25 decided the
  policy** and left the arithmetic; the chapter runs a rule rather than writing one.
- **One finding that makes the two sentences non-redundant.** FR-MED-06 permits attaching an
  object already `ready`, so an event can never fire for it. This is what stops story 1 being a
  weaker version of story 2, and it is the case FR-009 and SC-006 exist to hold.
- **Premises that held.** `channelsReferencingMedia` exists (4.12) and returns a list;
  migration `0018` constrains the three states; the verdict seam is a compare-and-set that
  already distinguishes *a transition happened* from *a verdict arrived*, which is what FR-005
  needs and what makes SC-005 assertable without new machinery.
