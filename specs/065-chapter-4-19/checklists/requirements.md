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

## Analysis pass 1 — eight findings, two CRITICAL, all fixed

The pass ran before any code existed, which is where it is cheapest. Two of the findings are
hazards this project has already paid for once, arriving in a new place.

**A1, CRITICAL — one migration file written across two phases.** T015 (phase 3) added the
column and T030 (phase 5) appended the trigger to the same `0022`. `migrate.ts` records
`schema_migrations.version` **by filename with no checksum**, so by phase 5 that file has
already applied on the lane and **the trigger would never run there while the ledger reported
the migration done**. Chapter 4.18 wrote that hazard down as something to check for; this task
structure would have turned a risk into a certainty. Split into `0022` (column, backfill) and
`0023` (trigger) — and the order between them is load-bearing in its own right, because
`0022`'s backfill is an `UPDATE` on the table `0023` makes append-only.

**A2, CRITICAL — the task did not say which clock the version row takes.** `deleteMessage`
sets `deletedAt` from the database clock and reads it back; a second reading would give the version row a
primary key the tombstone's instant does not match. **`editMessage` carries the argument in a
comment at `repository.ts:5325`** — *"ONE CLOCK READING FOR BOTH WRITES… two `now()` calls
would be two instants"* — written by the chapter that built the edit path. The task now says
reuse the returned value, and the data model says why.

**A3, HIGH — the spec asked for something the contract cannot return.** US1 scenario 3 wanted
the current text *identified as current* in the version list, and FR-002 claimed one request
instead of two. The contract returns only versions that **ended**, so a live message's current
text is not in the list at all. The task list had silently resolved this in the contract's
favour. Both are corrected, and the contract now has a section saying what is not in the list
and why the asymmetry is the shape of the data: after a deletion there is no current text.

**A4, HIGH — SC-006 was measured and asserted nowhere.** T005 recorded the 403 into
`baseline.txt`; no task put it in a suite. **This chapter adds rows to that route.** T024a
asserts it by code and runs it red by deleting the decorator — which is chapter 4.18's arm-3
finding, one chapter old, where the 403 branch was unreachable and the decorator beside it was
the whole defence and had no test.

**A5, HIGH — a success criterion that could not fail for its own reason.** SC-005 read *"sees
its own and zero of a second tenant's, measured against a second environment that performed
the same actions"* — carried over from chapter 4.18's audit log, which is a **list** route.
This route returns one message's versions by id, so the only cross-tenant shape is a foreign
id, and `gauntlet.itest.ts:242` already attacks it. Restated as *the existing attack still
passes with version rows present*.

**A6, MEDIUM — FR-006 is covered by a test that predates the feature and nothing said so.**
T038 names it now. Without the citation it reads as uncovered, which is how a later chapter
adds a second attack for the same property.

**A7, MEDIUM — `targets.ts:208` already names the hazard A4 is about**: *"THE TWO VALUES MUST
AGREE AND NOTHING COMPARES THEM. This entry and the decorator are the same authorisation fact
written twice."* Cited where the new assertion lands.

**A8, LOW — FR-010 is a process requirement among functional ones.** Left alone: renumbering
ten requirements to relocate one costs more than it buys, and the SRS keeps governance clauses
in its own requirement tables.

### What found them

Three of the five serious ones came from **opening a file the artifacts cite and reading past
the line they quote** — `repository.ts:5325`'s clock comment, `migrate.ts`'s ledger, and
`targets.ts:208`'s own warning. The other two came from **asking what a criterion would have
to see to fail**, which is how SC-005 turned out to describe a leak this route cannot have.

Neither mechanism is new. Both are in `CLAUDE.md` and both needed a pass to apply.

## Notes

- Items marked incomplete require spec updates before `/speckit-clarify` or `/speckit-plan`
