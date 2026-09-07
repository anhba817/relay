# Specification Quality Checklist: Part 3, reorganised by subject

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-07
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

**Validated against 14 requirements and 8 success criteria.** Counts: 14 functional requirements,
8 success criteria, 3 user stories, 6 edge cases. Zero `[NEEDS CLARIFICATION]` markers — one fork
was genuinely the user's and was put to them before the specification was written rather than marked
inside it.

### Every number in this specification was measured, not estimated

This is the item most worth checking on a specification about restructuring, because the argument
for restructuring is usually taste. It is not here:

| Claim | How it was measured |
|---|---|
| 447,394 words, 24 chapters | `wc -w` over the English Part 3 pages |
| five of eight clusters discontiguous | chapters grouped by subject, spans compared against membership |
| 70,558 words teaching delivery for absent producers | chapters 5 and 6 measured; producers traced to chapter 20 in the plan |
| outbox taught four times, grammar derived five | section headings and the plan's own admission |
| 54 forward against 522 backward references | every `chapter 3.N` mention classified by direction |
| 985 references in 166 fenced files | every fenced path resolved against the platform tree |
| 169 of 242 fenced files need regeneration | union of content changes and chain-order changes |

**The forward/backward ratio is the one that decided the shape of the feature.** Had it been the
other way round, the dependency order would have been broken and this would be a rewrite. At 54
against 522 the chapters build on what came before, so the grouping can be fixed by moving whole
chapters — which is mechanically verifiable in a way that rewriting is not.

### What the measurement changed about this specification

**FR-008 exists because of a `grep`, and it doubled the feature.** The first draft assumed
renumbering was a book-only change. Counting the references found 985 inside fenced platform source,
which means renumbering edits the code the book teaches, which means every one of those files needs
a fence amendment. The scope estimate went from 39 affected files to 169 on that one measurement.

**And the remedy was already published.** Chapter 3.7 has a section titled *"A chapter number is a
reference that ages"*, written after an insertion invalidated three comments, one of which had been
wrong since a previous insertion. It states the rule — *the subject does not move; the ordinal
does* — and applies it three times. The specification finishes it rather than inventing it.

### The one item that could still be wrong

**FR-009 says prose is preserved, and a moved chapter's prose may not survive the move unchanged.**
A chapter that currently opens by referring to what the reader just finished will be wrong when
something else precedes it. The requirement is written as preservation because the alternative —
licence to rewrite — is what turns a verifiable change into an unverifiable one. Expect a bounded
number of transition sentences to need editing, and expect them to be found by reading, not by a
gate. This is recorded here rather than discovered at close-out.

### Why "reorganise, not rewrite" is an assumption and not a requirement

The 6× size variance and the four outbox explanations are real defects and this feature does not fix
them. That is deliberate: a reorder can be checked byte-exact by an instrument that already exists,
and a compression cannot be checked at all. Doing both at once means no gate can say which one broke
a chapter. It is in Assumptions and Out of Scope rather than left implicit.
