# Implementation Plan: Chapter 4.19 — Everything, including what was deleted

**Branch**: `065-chapter-4-19` | **Date**: 2026-10-03 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/065-chapter-4-19/spec.md`

## Summary

`docs/12` row 20 asks for FR-MOD-01 and FR-MOD-02 via API key and attaches a warning to
itself: **§7.5, check the premise, some of this may already exist.** It was run first. It does.

A tenant key deletes another author's message (204), reads history including tombstones, and
reads prior texts from a route that already refuses user tokens. What the check found instead
is at the join of the two clauses: **a message edited twice and then deleted yields two
recoverable texts out of three**, because an edit records the text it replaced and a deletion
records nothing. Zero edits yields zero of one.

So the chapter preserves the final text, and **FR-MSG-08 is the citation rather than a new
clause**: *"Hard deletion shall occur only via the compliance deletion endpoint."* Losing one
version at deletion is a hard deletion performed by the moderation path, which that sentence
reserves for erasure.

Three smaller things ship with it, each measured rather than inferred: the history row gains
the removal instant it is the only surface to omit; `message_edits` becomes append-only,
because FR-MSG-07 says *immutable* and nothing enforced it; and two comments that explain the
current behaviour are corrected, one of which justifies a branch with a row class the lane
holds **zero** of.

## Technical Context

**Language/Version**: TypeScript 5.x on Node 22, as the rest of `services/api`

**Primary Dependencies**: none new. Drizzle and Zod are already here, and the trigger
mechanism shipped last chapter

**Storage**: PostgreSQL — `message_edits` widened by one column, plus a trigger

**Testing**: vitest. The unit lane for the schema's arithmetic, the api integration lane for
the routes and the storage refusal, the isolation gauntlet for tenancy

**Target Platform**: Linux server, the composed stack

**Project Type**: web service — a tutorial chapter over `relay-platform`, published in
`relay-tutorial`

**Performance Goals**: the deletion gains one `INSERT` inside a transaction it already has.
Chapter 4.18 measured the same shape at **0.43 ms**; this plan measures its own rather than
reusing that figure

**Constraints**: no breaking change to a published response (CON-05). Every field this chapter
adds is additive, and the three renames that would read better are refused with their bill in
the complexity table below

**Scale/Scope**: 4,861 tombstones and 4,859 version rows on the development lane; 176,157
messages that still hold text

## Constitution Check

| principle | verdict |
|---|---|
| **I — tenant isolation** | **The route has two scoped reads and the one that enforces FR-006 is not the one this row first named.** `messages.controller.ts:509` calls `messageExistsIn` — three predicates, `channels.environmentId` among them — and 404s before `:512` reaches `listMessageEdits`, which carries its own copy. The new row is reached by the second and guarded by the first. **The probe deletes each arm in both, one at a time and then together** (T037), because chapters 4.11, 4.12 and 4.18 all measured that an SQL clause carries no JavaScript branch — and because 4.12 measured that arms cover for each other, which is what deleting only `listMessageEdits`' scope would have demonstrated here, as a green run |
| **II — no acknowledged message is lost** | untouched. This chapter adds a row; it removes nothing and acknowledges nothing new |
| **III — two data paths** | untouched. Versions are operational, read from Postgres by the route that already reads them. Nothing analytical is involved |
| **IV — single writer** | **engaged, and satisfied by where the row goes.** A version belongs in the version table, not as a column on `messages` — which is why option C in research R3 is refused on this principle as well as on FR-MSG-08 |
| **V — API-first** | both routes exist and both are public. No internal seam, no new surface |
| **VI — test-verified** | **five bullets, answered below rather than in this cell** — the first version of this row answered one of them |
| **VII — boring by design** | **no new service, no new dependency, no new table.** One column, one trigger, two added response fields. The ADR question is below |

### Principle VI in full, because the row above once answered a fifth of it

The clause has five bullets and this chapter engages four. The eighth and ninth analysis
passes found the row naming one, which is how a check written to catch an omission becomes
one.

| bullet | verdict |
|---|---|
| **stable identifiers, priority, verification method** | met. Every FR and SC here carries an id, and `traceability.md` (T051) is built by reading |
| **70% coverage; ordering, idempotency and tenant isolation at 100% branches** | **two of the three named properties are this chapter's, not one.** Tenant isolation: `listMessageEdits`' arms, probed by deleting each (T037) rather than read off a number. **Idempotency: FR-004 is an idempotency requirement** — a retried deletion records no second version — and it rides on `deleteMessage`'s already-deleted branch, which T018 puts the new write on the far side of and T023 pins with an absolute count. Ordering is untouched |
| **the cross-tenant suite gates releases** | met. T038 runs the gauntlet and records its counted line |
| **the quickstart MUST run unmodified, verified by automated execution in CI** | **UNMET, and not by this chapter.** There is no execution of any quickstart in `ci.yml` — chapter 4.11 measured zero occurrences of the word — and T069 runs this one by hand and *corrects it in place*, which is the opposite of *unmodified*. Recorded here rather than left silent, because this project's habit with an unmeetable clause is to name it: FR-MED-07, FR-MED-09's rendering half and FR-MOD-03's year are all carried that way. The gap is a platform one and closing it is a CI change, not a chapter |
| **input validated against a schema before processing** | **UNMET ON THIS CHAPTER'S OWN ROUTE, and carried deliberately.** `GET …/messages/not-a-uuid/edits` answers **500 `internal_error`** where an absent id answers 404 — measured with a control at analysis pass 5. It is `gaps.md` 058-3 across sixteen routes. `spec.md`'s Out of Scope gives the reason for carrying it and that reason stands; what was missing is that the carry touches a constitution MUST rather than only a gap entry, which raises what the decision has to be worth. One validating route among sixteen still makes the remaining fifteen harder to sweep |

**Does this need an ADR?** Constitution VII: *"Every architecture decision is recorded as an
ADR stating its drivers, rejected alternatives, and reversal condition."*

**No, and the reasoning is written down rather than assumed.** The two decisions this chapter
makes are both already recorded elsewhere. *Where the version goes* is settled by FR-MSG-08's
own sentence and by the one-table argument ADR-34's chapter made for renditions — the clause
decides it, not an architecture choice. *How the table is made immutable* is **ADR-35**,
shipped last chapter, applied unchanged to a second table with the same scope and the same
reversal condition.

Applying an existing ADR to a second case is the ADR working. **If the plan's measurements
falsify either — if the trigger behaves differently here, or if the one-table choice turns out
to cost a union somewhere — that is an ADR and the task list says so.**

## Project Structure

### Documentation (this feature)

```
specs/065-chapter-4-19/
├── spec.md
├── plan.md                         this file
├── research.md                     R1–R9, every number measured before the plan
├── data-model.md
├── contracts/message-versions.md
├── quickstart.md                   §1 and §2 MEASURED, the rest predictions
├── routes.md                       (phase 2)
├── baseline.txt                    (phase 1 onward)
├── clauses.md                      (phase 7)
├── traceability.md                 (phase 9)
└── gaps.md                         (phase 9)
```

### Source Code

```
relay-platform/
├── services/api/migrations/0022_message_versions.sql     the column, the check, the backfill
├── services/api/migrations/0023_message_edits_append_only.sql   the trigger — its own file,
│                                                         because it is written in phase 5
├── services/api/src/db/schema.ts                         the column, and the comment R1 corrects
├── services/api/src/db/repository.ts                     editMessage writes `ended_by`,
│                                                         deleteMessage writes the final version,
│                                                         listMessageEdits returns both new fields
├── services/api/src/messages/messages.service.ts         the history row's `deleted_at`
├── services/api/src/messages/messages.controller.ts      ditto, if the shaping is there
├── services/api/src/messages/versions.itest.ts            THE ONE NEW FILE — boots a Nest
│                                                         app, because T024 and T024a are
│                                                         route tests and T021–T023 are not
└── packages/test-harness/src/no-trigger-in-migrations.test.ts   a second permitted trigger

relay-tutorial/
├── app/(en)/part-4/chapter-19/<slug>/{page.mdx,figures.ts}
├── fences/post-series.md                                 every hunk, 4.8's rule
└── lib/tutorial.ts                                       the registration
```

**Structure Decision**: no new directory. Everything lands in files that exist, which is why
the fence bill below is the plan's largest number.

## The fence bill, counted now

Chapter 4.15's rule: count it in phase 1 where it can still change the sequencing, and read it
as a floor.

```
repository.ts              52 pages
schema.ts                  34 pages
messages.service.ts        27 pages
messages.controller.ts     18 pages
messages.schema.ts         12 pages
frames.ts                  12 pages
messages.itest.ts          18 pages   added by analysis pass 2
vitest.coverage.config.mts 23 pages   added by analysis pass 6
```

**`messages.itest.ts` is the one this list missed**, and it is not a maybe: `messages.itest.ts:1416`
asserts an exact key set on the `/edits` response and this chapter adds two fields to it. The bill
was written from the plan's own file list rather than from what the work touches, which is the
failure mode 4.15's rule predicts and 4.18 paid six files for.

**AND `vitest.coverage.config.mts` IS PUBLISHED BY 23 PAGES, WHICH IS WHY 4.18's CI WENT RED.**
T067 edits it — a pin moves, or a measured figure is written beside one — and that chapter's
first red run was `vitest.coverage.config.mts differs at line 1449`, from pins added after the
chain had been taken to zero with `check:fences` not re-run. **A file nobody thinks of as source
is in the chain**, and it is the last file this chapter touches, which is the worst position to
discover it from.

All to `fences/post-series.md`, because every one is published by pages this chapter does not
own — 4.8's rule, and one rule for eight files beats a judgement per file. **Chapter 4.18 paid 49
hunks across 21 files and six of those files arrived from repairs made after its list was
written.** This list is a floor.

**And `no-trigger-in-migrations.test.ts` is touched for the second chapter running.** 4.18
narrowed it from *no trigger* to *not the sentinel guard* and asserted the narrowing; this
chapter adds a second permitted trigger and **the narrowing already covers it** — which is the
test to run before editing the test.

## Phases

The nine phases are `tasks.md`'s and carry the same names.

1. **Setup and measurement.** The lane baseline, the CI baseline, the fence bill re-counted
   against the tree, and R1–R9 re-read against the code rather than against this document.
2. **The decision.** `ended_by`'s values and the response's field names, settled before a
   migration exists — because the alternative is a spec question with `0022` already applied,
   which is the ordering constraint 4.18 recorded.
3. **US1 — the final version, and the fact that it cannot be rewritten.** `0022` (the column,
   the backfill), the two write sites, the read, **and `0023`'s trigger**. Two migration files,
   both authored in this phase before either applies — because `migrate.ts` keys the ledger on
   a filename with no checksum, so a file written across two phases never applies in full on
   the machine that ran the first half.
   *(Analysis pass 1 split the files; pass 2 moved the trigger here, because it had no
   requirement in the spec and US3's independent test never exercised it.)*
4. **US2 — the removal instant in history.** One field, and the three surfaces reconciled.
5. **US3 — the boundary, published.** What a tenant can and cannot recover, counted. Two
   tasks: the clause count and the number of tombstones that can never be recovered.
6. **The probes.** Each tenancy arm deleted alone; the trigger attacked; the deletion's new
   cost measured against the shape before it.
7. **The documents.** FR-MSG-07 and FR-MSG-08 read before being edited, the SRS revision, both
   copies of the Part 4 table, and the two corrected comments. **And four sites in
   `docs/05-sad.md` rather than one** — §6.1's DDL, §6.1's *"keeps the three columns this
   document publishes"*, §6.1's tombstone read-path table, and **§5.3's sequence diagram of
   this exact transaction**, which chapter 4.18 amended for the identical reason. ADR-35 gains
   a second table in both of its homes (`docs/05-sad.md` and `docs/06-adr-deep-dives.md`) and
   no new ADR: the reversal condition was read and it is a deployment decision, not a statement
   about one table. *(The eighth analysis pass found all five by opening the documents.)*
8. **The chapter.** 2,000–4,000 prose words, the hunks, `check:fences` to zero.
9. **The record and the close.** And `pnpm coverage` **after** the chain is zeroed **and
   re-run after the pins go in** — which is the one thing 4.18 did not do, twice, from the
   same task. **Then `check:fences` again** (T067a), because the pin file is published by 23
   pages and the pin edit is the last thing this chapter writes to a file the chain carries.

## Complexity Tracking

| the simpler thing | why it is not taken | what it would cost |
|---|---|---|
| Rename `prior_text` → `text` and `edits` → `versions` | both are breaking changes to a published response under CON-05, for a noun | a route version, or a silent break for every existing caller |
| Rename the column `edited_at` → `ended_at` | the response field of that name is published | the same, plus a migration on 4,859 rows |
| Serve `ended_at` only, dropping `edited_at` | same reason | same |
| A separate `message_versions` table | two tables holding the same kind of row, and a union in every reader | chapter 4.15's one-table argument, paid again |
| A column on `messages` for the final text | a tombstone that keeps its text is not a tombstone (FR-MSG-08), and it puts a version on the row it is a version of (constitution IV) | every read path that treats `text === null` as *deleted* learns a second rule |
| Leave `message_edits` mutable and record FR-MSG-07's gap | the chapter's product is a recoverable text, and a recoverable text in a rewritable table is worth less than the clause claims | one migration, reusing ADR-35's mechanism |
| Converge the history row with `messageSchema` | a reshape where everything else here is an addition | breaking, and chapter 4.14 measured the construction-site cost of the smaller version of this |
| Put the new tests in `messages.itest.ts`, where every fixture already exists | **18 pages publish that file**, so a block of tests turns T025's one-line assertion change into a large published hunk | the fence bill, against a duplicated channel/user/token fixture in the new file — `messages.itest.ts` exports nothing, so no helper is importable either way |

**The duplicated instant is the cost this table is paying.** `edited_at` and `ended_at` carry
the same value on every row, for as long as the older name has callers. It is one field wide,
it is stated in the contract, and the alternative is versioning a route over a word.

## Risks

- **The premise check says most of row 20 exists, and a later pass may find it says that about
  the rest.** The arithmetic — two of three, zero of one — is measured and reproducible, so the
  gap is real; what could still move is whether `deleted_at` on the history row is already
  served somewhere this check did not look. **The task list re-reads it rather than trusting
  this paragraph.**
- **FR-MSG-07's immutability is a second clause arriving inside this chapter.** It is justified
  in research R5 and it is still scope growth. If it turns out to need anything beyond the
  migration ADR-35 already licenses, it comes out and becomes a gap.

  **AND UNTIL ANALYSIS PASS 2 THERE WAS NO CRITERION THAT WOULD HAVE TOLD YOU IT CAME OUT.**
  This risk was written while `spec.md` contained the words *immutable*, *append-only*,
  *trigger* and *rewrite* **zero times** — the decision reached this plan, the data model, the
  contract and five tasks through `research.md` and never reached the document that says what
  the feature is. It carries FR-011, FR-012 and SC-012 now. **A risk register entry about
  scope growth is not a scope boundary.**
- **`ended_by` required is a compiler-named change across one writer and one reader today**,
  and that count is from a grep. If the real number is larger the trade changes, and chapter
  4.14's measurement — 110 call sites for a constructor against 13 for two method parameters —
  is the reason to count before committing.
- **The trigger forbids the deletion erasure will need.** Row 22 must remove a user's words and
  these rows hold them. **And it is NOT the audit log's collision**, which this bullet said until
  analysis pass 6 — the third pass ran the delete and found two obstacles here where `audit_log`
  has one, the foreign key first and the trigger second. **Writing it down is this chapter's job;
  solving it is row 22's**, and a chapter that solved it here would be doing another's work.
  *(The correction was recorded in the bullet below and not in this one, which is 064's rule
  inside 065: a fact corrected in one place stays live in every other that restated it.)*
- **A version row holds text that a deletion was supposed to remove.** The clause permits it
  and a reader may still be surprised. The chapter states the distinction — a moderator removes
  a message, erasure destroys it — rather than leaving it to be inferred.
- **The fence bill is eight files before any repair** — six in the first draft, a seventh
  from analysis pass 2 and an eighth from pass 6. 4.18's list grew by six during
  implementation and every one came from running something rather than reading it.
- **THIS CHAPTER ENLARGES AN OBSTACLE THE NEXT ONE MUST CLEAR, AND THAT IS THE ONLY
  CONSEQUENCE THAT LANDS OUTSIDE IT.** `message_edits_message_id_fkey` is `NO ACTION`, so a
  message with version rows cannot be hard-deleted — and after this chapter **every** deleted
  message has one. Measured: **4,039 messages are undeletable today, 7,649 after**, growing by
  one per deletion. Row 22's erasure meets the foreign key before it meets the trigger, and
  three artifacts said this collided *"exactly as the audit log does"* until the third
  analysis pass ran the delete and read the error. **The risk is not that the chapter is
  wrong; it is that the number is invisible from inside it**, which is why T036 now measures
  it and hands it forward.
