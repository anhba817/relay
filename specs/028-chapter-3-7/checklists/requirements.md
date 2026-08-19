# Specification Quality Checklist: Tutorial Chapter 3.7 — "Commit and publish are two instants"

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-19
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

**Validated.** Three passes were needed and each found something.

**Pass 1 — implementation detail in the requirements.** FR-001 named the field the
mark would be stored on and FR-003 described the phase flag. Both were rewritten
to state the behaviour: what must not be delivered, and that the rule outlives the
buffering window. The distinction matters here more than usual, because the fix is
small enough that a spec written in terms of the fix would just be the patch with
worse formatting.

**Pass 2 — a success criterion that could not fail.** SC-001 originally said "the
journey passes", which it already does five runs in six. Twenty consecutive runs
is a real bar for a defect that reproduces at that rate, and SC-002 was added
because a passing flaky test proves nothing: the chapter needs a test that fails
deterministically against today's code. That is the difference between fixing this
and waiting for it to stop happening.

**Pass 3 — the renumbering was underspecified.** The first draft asked for the
plan and the registry to be updated and stopped there. It missed that chapter
numbers are cited inside source-code comments which are byte-fenced into published
chapters, so correcting one means touching the fence chain. FR-019 and FR-020 were
added, and FR-019 deliberately covers the reference that is **already** stale from
the previous insertion — the gauntlet moved to 3.8 during chapter 3.6's work and
`schema.ts` still calls it 3.7.

**The judgement that was recorded rather than resolved is now resolved, against
the spec.** The spec assumed suppression would be retired by observation — a
sequence above the mark clears it — and asked the plan to confirm the bound.
Research R3 found the rule unsafe: two gateway instances publish without
coordinating, so a prompt sequence 5 can precede a stalled sequence 4, and
retiring on the 5 delivers the 4. FR-007 now states the real bound (the
`MAX_RESUME_CHANNELS` cap) and FR-007a forbids retirement outright.

Caught by `/speckit-analyze`, not by the plan. The plan and the data model were
both corrected when R3 landed; the spec was not, so for one commit the
requirements mandated the behaviour the design refused to build. That is the same
drift chapter 3.6's analysis passes found three times — a fix applied to one
artifact and not to its source.

**Pass 5 — the second analysis round, and three of its five findings came from
the first round's fixes.** A half-applied recommendation (the bogus-cursor case
was documented and never tested), a new edge case that collided with one already
there, and a sabotage gap that only opened once FR-007a made "never retire" an
explicit requirement — an absence needs a mutation that ADDS something, and the
battery had none. Also caught: FR-007 asserted a 200-item bound that
`highWaterMarks` does not enforce, since it adds a key for every channel the
backfill returns. The bound now belongs to the gateway.

That is three consecutive chapters where each analysis pass finds defects the
previous remediation introduced. The lesson is not that remediation is dangerous;
it is that one pass is never enough, and a clean round is evidence about the round
rather than about the spec.

**Pass 6 — the third analysis round, and the findings have shrunk to mechanics.**
All three were residue from round 2: a fix split across two tasks so that the
scoping was implemented in `session.ts` and unit-tested in `resume.test.ts`, which
cannot reach it; a lifetime table still showing the unscoped derivation the prose
below it had corrected; and a file list still saying "one pure predicate" when
there are two.

The first is the one worth naming. It is the same failure this project has hit
twice already in a different costume — chapter 3.5's assertion that could not
fail, chapter 3.6's mutation that could not compile, and now a test that could not
reach the code it names. An implementer meeting it would have moved the assertion
somewhere weaker and nobody would have noticed.

Three rounds, decaying: CRITICAL (the spec mandated the rule that recreates the
bug) → HIGH (no sabotage mutation for the central decision) → HIGH (a test aimed
at the wrong file). Six findings, then five, then three. Convergence rather than
churn, and the point to stop is when a pass returns only stale words in a file
list.

Items marked incomplete require spec updates before `/speckit-clarify` or
`/speckit-plan`. None are.
