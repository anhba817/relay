# Specification Quality Checklist: Chapter 4.19 — Everything, including what was deleted

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-03
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

## What the validation pass actually changed

Three items failed on the first read and the spec was rewritten for each.

**"No implementation details" failed twice.** The first draft named
`message_edits`, `messages.deleted_at` and `GET …/edits` in the requirements rather than in
the Context. Table and column names are the plan's business; FR-001 now says *the text a
message held at the moment it was deleted* and the Assumptions carry the one structural
preference — a row in the existing table rather than a column on `messages` — as a preference
with its reason, which is where a guess belongs.

**"Success criteria are measurable" failed on SC-001.** It read *"the full version history is
recoverable"*. *Full* is the adjective this project's own style note names. It says **three
texts, in order, each with the instant it stopped being current** now, and names the
two-of-three the probe measured so the criterion has something to be better than.

**"Scope is clearly bounded" failed on the retention question.** An early draft had the
recovered versions expiring with the message, which is row 21's clause and a job nothing runs.
Out of Scope names both and the Assumptions say the same absent scheduler bounds them (ADR-28).

## What the premise check changed about the feature itself

`docs/12` §7.5 attaches a warning to this row: *"Check ch 20's premise before writing it…
Some of this chapter may already exist."* It was run before a line of the spec was written,
and it moved the subject.

**Two of the row's three clauses are met.** FR-MOD-02 returned 204 deleting another author's
message with a tenant key. FR-MOD-01's tombstone half and edit-history half both work, and
`/edits` is already API-key only — 403 for a user token, which is the access decision the
clause's *"via API key"* asks for.

**What the check found instead is at the join**: a message edited twice and then deleted
yields two recoverable texts out of three, because an edit records the text it replaced and a
deletion records nothing. That is now the chapter, and it is smaller and sharper than *build
FR-MOD-01 and FR-MOD-02* would have been.

**This is the fourth feature running where the premise check moved the chapter.** 4.17's made
it smaller after reading the whole of a test rather than the line that had been quoted; 4.18's
found FR-MOD-02 already met; this one found most of a row already shipped. The habit the
sequence argues for is that **the check is worth running even when the brief is confident** —
especially then, because §7.5's warning was written three features before anybody could act
on it and it was still right.

## Notes

- Items marked incomplete require spec updates before `/speckit-clarify` or `/speckit-plan`
