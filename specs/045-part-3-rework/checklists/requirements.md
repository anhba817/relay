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

**Validated against 15 requirements and 9 success criteria.** Counts: 15 functional requirements,
9 success criteria, 3 user stories, 6 edge cases. **It read 14 and 8 until the first analysis pass**,
which added FR-015 and SC-009 — and the instruments caught the stale count here one paragraph after
the requirement was added, which is the whole argument for keeping them. Zero `[NEEDS CLARIFICATION]` markers — one fork
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
| **1,429** references, 166 fenced files | every fenced path resolved against the platform tree. **Read 985 until research widened the pattern** — see below |
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

**And the count itself was low.** Planning re-measured with a wider pattern and found **1,429** — the
first pattern required the word "chapter" and missed 444 references of the form `3.20's`. FR-008 and
SC-002 are amended rather than corrected quietly. **A number in a requirement that nobody re-derives
is how a count stays wrong**, which is the same failure this project recorded when a heading said
Part 3 had 21 chapters through three chapters that each added one.

### What planning overturned

**The specification assumed the existing fences could be regenerated. They cannot.** Replaying all 39
order-changing paths' per-chapter deltas in the new order lands correctly on **3**, conflicts on 31,
and on 5 merges cleanly onto **a different file** — the worst outcome, because it passes every check
until the last one. Four candidate orders were measured and the conflict rate is 79–86% for all of
them, including one built only to minimise movement.

That does not invalidate the specification: FR-006 still holds, because the re-derivation targets the
same final file by construction. It changes what the work *is* — 278 fences re-derived rather than
re-hunked — and it is the reason the plan opens with a phase that proves the generator can rebuild
today's chain before anything moves.

**And the remedy was already published.** Chapter 3.7 has a section titled *"A chapter number is a
reference that ages"*, written after an insertion invalidated three comments, one of which had been
wrong since a previous insertion. It states the rule — *the subject does not move; the ordinal
does* — and applies it three times. The specification finishes it rather than inventing it.

### The documents this specification names, and why

A specification that names a document is making a claim about the tree. Four are named and each is
deliberate:

| Reference | Class | Why the spec names it |
|---|---|---|
| `docs/07-tutorial-plan.md` | the plan being amended | it carries Part 3's chapter rows and its own admission that the count was wrong three times running; FR-012 amends it |
| `specs/044-revision-watermark/gaps.md` | the ledger | the open items this feature inherits, excluded by name in Out of Scope |
| `relay-platform` | the repository whose comments change | FR-008's 1,429 references live there |
| `relay-tutorial` | the repository whose gates verify this | `check:fences` is the test for FR-013 |
| `relay-tutorial/lib/tutorial.ts` | the chapter registry | **named only after analysis pass 1.** 810 hand-maintained lines read by the sitemap and six components; FR-015 and SC-009 exist because nothing checked it |

### What analysis pass 1 changed

**Every box above was ticked before the pass, and the pass found a requirement that did not exist.**
Not a conflict between two clauses this time — an absence. Asking *what else in this tree knows a
chapter number* turned up `lib/tutorial.ts`: 810 hand-maintained lines declaring all 41 chapters,
read by `app/sitemap.ts` and six components including the previous-and-next links on every page.

**No requirement named it, no task touched it, and no gate compares it to the filesystem.** A
renumbering that skipped it would leave `check:fences` green, `check:docs` green, and every
navigation link in the book dead. It agrees with the tree today at 41 and 41 — **unguarded rather
than broken**, which is the harder condition to see. FR-015 and SC-009 exist because of it, along with a
checker in the foundational phase, two tasks in the reorder phase, and quickstart scenario 10.

**And the headline scope number was unknowable.** The plan carried 39 paths / 278 fences, measured
with the milestone chapter moving as a unit. The design splits it, and the answer is 39/278 if its
fences land early against 44/300 if late. Both bounds were measured, the split was then decided fence
by fence at the chapter's own `## The outsider` heading — 14 to the registry, 7 to the outsider,
nothing straddling — and the re-measured answer is **42 paths and 289 fences**. A number that turns
on an undecided design question is not an estimate.

**Two draft findings were withdrawn after checking**, which is worth recording because both were
plausible: `docs/07-tutorial-plan.md` looked like it needed `pnpm sync:docs` before `check:docs`, and
`check-docs-drift.sh:31` says it is deliberately the one document not mirrored. And the registry
looked like it might already be stale; it is not.

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
