# Specification Quality Checklist: chapter 4.22, "The identifier the customer gave it"

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-05
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

**THE SCOPE IS MEASURED RATHER THAN ARGUED, WHICH IS WHY IT IS BOUNDED.** A sweep of
`information_schema` returns exactly two tables with an `external_id` column —
`channels` and `users` — so the question *"which nouns does this chapter touch?"* has
an answer from the database rather than from a judgement about what feels in scope.
Messages, media objects, webhooks and environments are excluded by construction, not
by preference.

**THE SPEC NAMES NO ROUTE COUNT IT DID NOT COUNT.** 13 channel routes and 8 user
routes come from a sweep of every `@Controller`/`@Param` pair, printed in full before
the spec was written. 41,772 channels with 0 uuid-shaped identifiers is a query.

**ONE ITEM CARRIES A JUDGEMENT A PLANNER MAY OVERTURN.** *Scope is clearly bounded*
is marked complete, and FR-002 — keep accepting the Relay identifier — is the reason
the bound holds. If the plan decides instead to deprecate the uuid, the chapter gains
a migration, a deprecation window and a client story, and the bound moves. **The spec
takes the position that a transition is not a design and says so in the Assumptions**,
so the plan can refuse it in one place.

**WHAT THIS SPEC DELIBERATELY DOES NOT DECIDE.** The resolution order when a
customer's identifier is itself a uuid. FR-003 requires that it be defined, documented
and tested; it does not say which way. The measurement that bears on it is in the
spec — **0 of 41,772** — and the decision belongs with the cost of each order, which
is `/speckit-plan`'s research.

## Re-validated 2026-10-05 after four analysis passes

**Every box above was ticked against a spec that has since changed in four places**,
which is the half of a checklist nobody re-runs. Re-read and re-ticked:

| | what moved | pass |
|---|---|---|
| FR-004 | the **code** names the cause; the message stays constant under FR-TEN-05 | 3 |
| FR-006 | from *"no value may contain an internal key"* to *"sweep, count, dispose"* | 3 |
| FR-007 | conditional on FR-006's sweep finding something to change | 3 |
| SC-003 | scoped to the **channel segment**; `:messageId` is still a 500 | 4 |
| SC-006 | the count is stated even when it is zero | 3 |
| SC-008 | `git diff <tag> --`, not `<tag>..HEAD` | 4 |
| SC-011 | new — the resolution's added query is measured | 3 |

**Two boxes are weaker than they were and stay ticked, with the reason.**
*Requirements are testable and unambiguous*: FR-007 is now conditional, so its
applicability is unknown until T026 runs — a conditional requirement is still
testable, and the alternative was leaving it asserting a leak that does not exist.
*Success criteria are technology-agnostic*: SC-003's scope note names a path segment,
which is closer to the implementation than the rest, and the claim is false without
it.

**And the paragraph above is now half stale.** The resolution order's **outcome** is
settled — the identity wins — and it is in `contracts/addressing.md`. Only the
procedure is open, and T009 owns it. The paragraph is kept rather than rewritten
because it records what the spec was willing to leave open, which is the thing a
checklist is for.
