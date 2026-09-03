# Specification Quality Checklist: Chapter 3.23 — editing and deleting a message

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-03
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

**All three markers are resolved and recorded in the spec's Clarifications section**, with
the reasoning rather than only the outcome:

1. The deletion event carries no text; the message payload published since chapter 1.3 is
   untouched.
2. Resume stays ordered by the channel sequence alone and the REST history is the repair —
   **the Slack model**, with Matrix's append-only timeline and IMAP's modification sequence
   both considered and rejected for stated reasons.
3. A tenant API key may delete any message and may edit none.

**Two names in this spec are the spec's, not the code's**, and the plan will reconcile them:
what the spec calls an *edit history entry* the SAD's DDL calls `message_edits`, and what it
calls a *tombstone* is a state of `messages` rather than a table. The drift is deliberate —
the spec should not name a table — and it is written here so the plan does not treat it as a
discovery.

**Four things this chapter did not have to decide, because the tree already had them.** They
are stated in the spec's opening and are the reason it is shorter than it might have been:
both frame kinds exist and carry a message payload; the columns exist; the SAD publishes both
the deletion's shape and the `message_edits` DDL; and `schema.ts` names that table as an
absence awaiting *"the edit chapter"*. Chapter 3.22's most expensive lesson was that reading
beats deriving; applying it before writing the spec is where it is cheapest.

**The spec grew during planning, and it says so.** Research found FR-WHK-02's event spine —
a third surface the first draft missed entirely — and FR-019, FR-020 and SC-011 were added
with the reason recorded in the Clarifications section rather than folded in quietly.

**One risk this checklist cannot discharge.** The spec asserts that the REST history path
already carries tombstones and edited text unchanged, which makes the chosen repair path
free. That was read from the code, and it is the single assumption the whole resume decision
rests on. **The plan must verify it with a test against the running endpoint rather than
carrying it forward as a citation** — this chapter's predecessor recorded three separate
premises that were inherited from a record and never re-run.

## What five analysis passes changed, and one thing they got wrong the whole time

The spec grew from twenty-one requirements to thirty and from eleven criteria to thirteen — **spelled out, because `sweep.py` reads a digit beside the word "requirements" as a claim about the current count and was right to.** Every addition came from
a pass reading something rather than deriving it:

    pass 1   the fan-out cannot carry either kind          -> a phase, and ADR-24
    pass 2   a task that could not run in its own phase    -> and 7 stale phase numbers
    pass 3   the non-author refusal's code was undecided   -> FR-022
    pass 4   four documents summarised themselves wrong    -> FR-017a
    pass 5   FR-MSG-08 asks for the deletion's actor       -> FR-006a
             three sentences assumed a read surface        -> FR-023, FR-023a
    pass 6   three routes, three accepted-credential sets  -> method-level @Accepts
             a comment 25 lines from the code it denies    -> a correction task
    pass 7   the derived target list goes red on a route   -> three declared targets
             one authorization fact in two homes           -> gaps item 4
    pass 8   five tasks named no file or command           -> all five named
             sweep could not see the plan's phases at all  -> 12 headings restored
    pass 9   the one document a person runs was untouched  -> quickstart P6, P7, P8

**Four of nine passes found the instrument wrong rather than the artifact**, which is the
single most useful thing this sequence produced. The coverage grep counted commit tasks; the
id-format claim was itself wrong — a malformed id fails the checklist-format rule and was
never silent, which pass 11 found by testing the rule it had asked for; my phase-heading pattern was
fitted to my own output rather than to `sweep.py`'s; and `sweep.py` prints eleven success
criteria where there are thirteen because its pattern has no optional letter. **Three of those four are now
rules in this chapter's own instruments, tested red; the fourth was my own verification
pattern, and its fix is a note at the top of `quickstart.md` saying the premise list is derived
rather than maintained.**

**And the coverage number reported by passes 1 to 4 was measured with a broken instrument.**
`grep "<id> (3.23)" tasks.md` counted a commit task's citation as coverage. Eleven of the
tasks are commit lines that name every id in their phase, so three criteria read as covered
while one of them — SC-002, *"all three superseded texts are retrievable"* — had no surface in
the platform at all. **The number was right four times and meant nothing four times.** this chapter's own `check-refs.py`
puts the rule into this chapter's own `check-refs.py` and tests it red, which is the only
version of this that survives the next chapter.
