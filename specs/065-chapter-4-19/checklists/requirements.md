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

## Analysis pass 2 — six findings, one CRITICAL, all fixed

Pass 1 found things by opening files the artifacts cite. Pass 2 found its CRITICAL by
**grepping this feature's own spec for a word four other documents use constantly**.

**B1, CRITICAL — the immutability decision was in five tasks and no requirement.** The words
`immutable`, `append-only`, `trigger` and `rewrite` appeared **zero times in `spec.md`**,
while the decision was in `research.md` R5, the plan's summary, constitution check, file list,
phase list, complexity table and risks, the data model, the contract's `DELETE` refusal, and
tasks T030–T034. **Five unmapped tasks** — the first this feature had produced — and no
success criterion that could have told you if they were dropped. The plan's own risk said
*"if it needs anything beyond what ADR-35 licenses, it comes out and becomes a gap"*, which is
a sentence with nothing behind it when no criterion names the thing.

The fix was not to bolt on a requirement. The value is **US1's**: a recovered text the
application can rewrite is not an answer to *what did it say*, it is a note. So FR-011,
FR-012 and SC-012 are in the spec, US1 gains a fifth acceptance scenario, and T030–T034 moved
into phase 3 relabelled `[US1]`. **That move also tightens pass 1's A1** — both migration
files are now authored in one phase, before either applies, where two phases apart was the
hazard A1 was about.

The ids jump (T025 then T030) and they were not renumbered, because five renumberings would
move every cross-reference between them. Execution order is correct; the numbers are not
contiguous and the phase header says why.

**B2, HIGH — one existing assertion must change and the task list would have misread it.**
`messages.itest.ts:1416` asserts an **exact key set** on the `/edits` response, with a comment
saying why it is exact. This chapter adds two fields, so it moves — a contract test doing its
job. T025's rule is *"a suite that needed editing to stay green is a behaviour change and the
chapter says so rather than editing it"*, which would have classified it as an FR-008
violation. T025 now names it as the one expected edit, and notes that `toHaveLength(1)` eight
lines above does **not** move, because that message is edited rather than deleted.

**B3, HIGH — FR-008 did not cover the surface whose content changes.** It read *"MUST NOT
change the behaviour of sending, editing or deleting a message"* — three verbs, and the
version list is a fourth surface whose content changes by design. A no-change clause that does
not mention the one thing that changes.

**B4, MEDIUM — the fence bill missed the file B2 names.** `messages.itest.ts` is published by
18 pages and was not among the six. The bill had been written from the plan's own file list
rather than from what the work touches, which is exactly what 4.15's rule predicts and 4.18
paid six files for.

**B5, MEDIUM — US3 was not independently testable**, because five of its seven tasks built
something its independent test did not exercise. Resolved by B1's move; US3 is two tasks now
and its test is the clause count.

**B6, LOW — `docs/07` §4 rule 2 checked.** *"The journeys are the milestones."* Part 4's is
Priya's and this chapter's reader is Priya, but the milestones are rows 9, 17 and 22. Recorded
in Assumptions so a later pass does not re-walk it.

### Checked and clean, recorded so a later pass does not repeat them

`row.text` is read into a local about eighty-five lines before the `UPDATE` that nulls the
column, so the version row can be written from it — **the chapter's correctness core holds**.
The edit path refuses an edit on a tombstone, so *every edit precedes every deletion* is true
rather than hoped. The tombstone-as-empty-list test is about attachments, not versions.

### What found them

Pass 1's mechanism was opening cited files. Pass 2's was **asking what a document does not
contain** — one grep of `spec.md` for a word the other four documents use on every page. The
yield argues for varying the question rather than repeating the pass: the same mechanism run
twice would have found B2 and nothing else.

## Analysis pass 3 — five findings, none CRITICAL, all fixed

Pass 1 opened files the artifacts cite. Pass 2 asked what a document does not contain. **Pass
3 ran SQL against the real table**, and everything it found came from that — nothing in this
pass was visible by reading.

**C1, HIGH — the erasure collision is two obstacles and three artifacts described one.**
`message_edits_message_id_fkey` is `NO ACTION`, so deleting a message that has version rows is
refused by the **foreign key**, before any trigger is consulted. Run in a rolled-back
transaction:

    ERROR:  update or delete on table "messages" violates foreign key constraint
            "message_edits_message_id_fkey" on table "message_edits"

The spec's edge case, T014 and the data model all said this collides *"exactly as the audit
log does"*. **It does not**: that table's foreign key points at `environments` and nothing
deletes those, so it has one obstacle and this one has two — and the one that was already
there is the cheaper to miss.

**C2, HIGH — and this chapter nearly doubles the population it affects.** Measured: **4,039
messages cannot be hard-deleted today, 7,649 after**, because every deletion now leaves a
version row where only edits did. 3,610 existing tombstones gain one and the count grows by
one per deletion. T036 counted what this chapter cannot recover; nothing counted what it hands
forward. It does now.

**C3, MEDIUM — one test survives on a one-edit margin.** `history-drift.itest.ts:85` is the
only path in the repository that hard-deletes a `messages` row. It passes today and after this
chapter for the same reason — its fixture is 60 fresh sends with no edits — and **any later
change that edits or deletes a message in that fixture turns it red with an FK error naming
neither this chapter nor that test**. Recorded as checked-and-clean with the reason.

**C4, LOW — the risk register had no entry for a consequence outside the chapter.** Six risks,
all about this feature's own work. Added, with the number.

**C5, LOW — a clause citation had drifted.** The contract cited **FR-004** for the demonstrated
refusal; FR-004 is the no-op rule. The citation was written before pass 2 gave immutability a
requirement and pointed at the nearest clause that sounded right. It is **FR-011** now.

### Checked by running, and clean

- **T015's migration sequence works exactly as written**, run against the real table and
  rolled back: `ADD COLUMN` 2.2 ms, the `CHECK` added while all 4,859 rows are `NULL` **passes**
  — a `CHECK` on `NULL` is unknown, not false — `UPDATE 4859` in 19.7 ms, `SET NOT NULL` clean.
  The ordering claim is measured now rather than reasoned.
- **`migrate.ts` wraps each file in `BEGIN`/`COMMIT`**, so a half-applied migration is not a
  state this feature can reach.
- **Nothing in production hard-deletes a `messages` row.** One test does; C3 covers it.
- The probe left nothing behind — `information_schema` reports the column absent after rollback.

### The yield, and what it says about the passes

    pass 1   8 findings   2 CRITICAL   opening files the artifacts cite
    pass 2   6 findings   1 CRITICAL   asking what a document does not contain
    pass 3   5 findings   0 CRITICAL   running SQL against the real table

**The count fell and the character changed every time.** Nothing in pass 3 was reachable by
reading, and nothing in pass 2 was reachable by running — so the falling number is not
evidence that the artifacts are converging, only that each question has been asked once.

## Analysis pass 4 — four findings, none CRITICAL, all fixed

The question none of the first three asked: **walk the tasks in execution order and ask, at
each step, whether everything that task needs is already true** — then, of each planned test,
*what would have to be false for this to fail*.

**D1, HIGH — no task applies the migration, and it works anyway.** T015 writes `0022`; the
first task that says *apply the migration* is T031, fourteenth in the phase, after seven tests
that need the column. It is not broken, because `global-setup.ts` runs `migrate(pool)` before
every suite, so the phase-3 tests apply it as a side effect. **Nothing said so** — and T031's
probe is `psql`, not a suite, so running it before any test since T030 would measure a
database `0023` has not reached. T015 states the mechanism; T031 migrates explicitly and says
why.

**D2, HIGH — a broken migration will not look like a broken migration.** `globalSetup`
throwing makes the lane print `No test files found, exiting with code 1`. Chapter 4.14 traced
that exact string to a swallowed `globalSetup` failure and the rule is in `CLAUDE.md`: *when a
lane reports an empty corpus, ask a lister rather than a runner.* **This is the first feature
in five to add a migration**, so it is the first in five where that failure mode is live, and
no task mentioned it.

**D3, MEDIUM — T023 could pass with FR-001 unimplemented.** It asserted *a second deletion
adds no version, counted before and after*, and **0 → 0 satisfies a delta of zero**. Only T021
in the same file would have been red. It asserts the absolute count now — three both times —
because a test whose subject is *the second call changed nothing* has to pin what the first
call left.

**D4, LOW — the version tests need an author the credential cannot be.** An application
credential sending a message answers `sender_not_permitted`; the fixture has to mint a dev
token, which the editing half needs anyway because FR-013a gives the edit to the author. The
premise check found it and `quickstart.md` carries it; `versions.itest.ts` is a new file whose
author had no reason to know.

### Checked and clean

- **T020 is not a vacuous assertion.** *Cannot collide by construction* could have produced a
  test that cannot fail; as written it performs an edit and a deletion and asserts two rows at
  distinct instants, which fails if the deletion reuses the edit's instant.
- **T022 cannot pass vacuously** — it asserts one version where zero exist today.
- **T034 passes genuinely.** `0023`'s trigger statement contains no `__sentinel` before its
  semicolon, so 064's narrowed pattern does not match it, and the `CREATE FUNCTION` body's
  semicolons are irrelevant because the pattern anchors on `CREATE TRIGGER`.
- **`message_edits` is not in the sentinel guard's table list**, so the lane's triggers and
  this chapter's do not interact.

### The four passes

    pass 1   8 findings   2 CRITICAL   opening files the artifacts cite
    pass 2   6 findings   1 CRITICAL   asking what a document does not contain
    pass 3   5 findings   0 CRITICAL   running SQL against the real table
    pass 4   4 findings   0 CRITICAL   walking the tasks in execution order

**No pass has repeated another's mechanism and the count has fallen every time.** That is a
fact about the questions, not about the artifacts: nothing pass 3 found was reachable by
reading, nothing pass 2 found was reachable by running, and pass 4's two best findings are
about **what the executor sees when something goes wrong**, which none of the first three
asked. `CLAUDE.md`'s rule is *do not stop on falling yield*; the corollary this feature
suggests is that the yield measures the question.

## Notes

- Items marked incomplete require spec updates before `/speckit-clarify` or `/speckit-plan`
