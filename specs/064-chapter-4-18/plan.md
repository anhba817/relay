# Implementation Plan: Chapter 4.18 — The log that cannot be edited

**Branch**: `064-chapter-4-18` | **Date**: 2026-10-02 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/064-chapter-4-18/spec.md`

## Summary

FR-MOD-03 asks for an immutable audit log carrying actor, action, target, timestamp and
request id for every moderation action, retained a year. The platform has none: `docs/05-sad.md`
says *"There is no `audit_log` table"*, and the two things that look like one are not —
`messages.metadata.deleted_by` is a mutable column on the row it describes, and the request
log has three of the five fields with an engine that replaces rows and a 30-day TTL.

The chapter adds an append-only Postgres table written inside the transaction of each action
it records, a trigger that refuses `UPDATE` and `DELETE`, a classification of every mutating
route carried on the derivation the isolation gauntlet already runs against the router, and a
read route for a tenant's own entries modelled on chapter 4.8's.

**The product is a decision, not a table.** *"Every moderation action"* names a population and
gives no membership rule. The router serves **24 tenant-reachable mutating routes** and the
chapter owes a decision and a reason for each — which is the same work FR-ANL-06's *"counts
derived from operational data"* was at chapter 4.7 and FR-MED-09's *"renders as"* was at 4.17.

## Technical Context

**Language/Version**: TypeScript 5.x on Node 22, as the rest of `relay-platform`

**Primary Dependencies**: none added. Drizzle and NestJS as they stand; constitution VII makes
a new dependency something to justify, and nothing here needs one.

**Storage**: PostgreSQL, operational. A new table and this schema's **first** trigger —
`grep -rl "CREATE TRIGGER\|CREATE FUNCTION" services/api/migrations/` returns nothing across
twenty migrations, so the mechanism is new and R2 is its justification.

**Testing**: vitest. The api integration lane for the write and the read; the isolation
gauntlet's existing suite for the classification's both-directions check; a `psql` probe for
the trigger, because the thing being tested is a database behaviour and the api cannot express
the attack.

**Target Platform**: the composed stack. Postgres on `RELAY_POSTGRES_PORT=15432`.

**Project Type**: a chapter of a tutorial series whose artifact is a commit on `relay-platform`
plus prose in `relay-tutorial`.

**Performance Goals**: none stated by the clause, and the cost is **two quantities rather than
one**. For `banUser`, `deleteUser` and `deleteMessage` it is one additional insert inside a
transaction that already exists. For `unbanUser`, `setMemberRole`, `archiveChannel` and
`unarchiveChannel` it is an insert **plus a transaction those methods did not have** (FR-005a).
An earlier draft of this line said *"inside transactions that already exist"* and was written
before the four were measured. The plan measures both rather than predicting either.

**Storage precision**: `occurred_at` is declared `timestamptz(3)` where every other column in
this schema is the default microsecond, because the cursor compares it against a value that
came back over the wire at millisecond precision. See `data-model.md` §1 — it is the first
keyset cursor over a timestamp column in Postgres here, and the only place the platform's
deviation from the constitution's *"millisecond precision"* would cost a reader rows.

**Constraints**: FR-012 — no behaviour change to any action recorded. The fence chain must
return to zero (SC-009).

**Scale/Scope**: the development lane holds **25** tenant-reachable mutating routes to
classify. Entry volume is one row per moderation action, which on this lane is a handful a day.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Verdict | Why |
|---|---|---|
| **I. Tenant isolation** | **ENGAGED, and it is a release gate** | The read route is tenant-scoped and the gauntlet's 100%-branch clause names isolation. SC-005 is the measurement; the classification table lives in the gauntlet's own file, so a new route arrives already in front of the suite that attacks it. |
| **II. No acknowledged message is lost** | not engaged | Nothing here is on the message path. |
| **III. Two data paths, never crossed** | **NOT ENGAGED, and the plan says so rather than leaving it to inference** | III forbids analytical queries against Postgres and governs the asynchronous path. An audit log is operational data about operational actions. R1 carries the argument, and the reason it is written down is that a reader who knows the request log went to ClickHouse will expect this one to follow it. |
| **IV. Single writer, single source of truth** | **MET by placement, and the two facts are named** | The entry is written by the same transaction that performs the action, in the repository layer, which is the only place a lint rule permits a query. No second writer. **And `users.banned_at` and an entry are not the same fact**: the column answers *is this user banned*, the log answers *what did somebody do and when*, and the column is authoritative for the first. A disagreement between them is not a reconciliation this chapter builds — DR-17 is what that question becomes when somebody asks it — and saying so is the difference between one fact with one home and two facts nobody distinguished. |
| **V. API-first** | **MET** | The read route is a published route with a documented contract, not an operator's `psql`. |
| **VI. Requirement-driven, test-verified** | **ENGAGED** | FR-004's refusal must be demonstrated by a probe that attempts the write, not asserted by a comment — chapter 4.17's *a comment is not a test*, applied to the mechanism this chapter exists to build. |
| **VII. Boring by design** | **ENGAGED, and the justification was rebuilt on a corrected premise** | No dependency, no service, no container. One new mechanism: a Postgres trigger. R2 called it *the schema's first* on a grep that returned zero — and **a test enforces that zero**: `no-trigger-in-migrations.test.ts` forbids `CREATE TRIGGER` in every migration and passes today. The rule is wider than its own stated reason, which is about the sentinel guard; T014c narrows it before phase 3 writes anything. The justification stands and is now *the mechanism is new to the product schema, the obvious alternative does nothing here, and the rule that made it look impossible was written about a different trigger.* |

**No violation requires a Complexity Tracking entry, and VII asks for one thing this plan did
not originally produce.** The trigger is new and is argued in R2 against an alternative measured
inert — but VII's own words are *"Every architecture decision is recorded as an **ADR** stating
its drivers, rejected alternatives, and reversal condition"*, and a research note is not one. It
carries no reversal condition, and it is not where a later chapter looks.

**ADR-35 is this feature's**, written at T054a into `docs/06-adr-deep-dives.md` and summarised
at T054b into `docs/05-sad.md`: the store placement, the trigger, and `timestamptz(3)` as the
read path's consequence. Its mirror already exists — ADR-26 is *"The api serves a customer
request from the analytical store"*, the same decision pointing the other way. Research R7a
carries the three reversal conditions, which is the field measuring does not produce.

## Project Structure

### Documentation (this feature)

```text
specs/064-chapter-4-18/
├── plan.md              # This file
├── research.md          # Phase 0 — R1..R8, with the trigger probe and its two bypasses
├── data-model.md        # Phase 1 — the entry, the set, the actor
├── quickstart.md        # Phase 1 — walk it by hand, including the attack
├── routes.md            # Phase 2 — every mutating route, classified, with a reason
│                        #           each. The chapter's product.
├── contracts/
│   └── audit-log.md     # Phase 1 — the read route and the entry's published shape
├── checklists/
│   └── requirements.md  # written by /speckit-specify
└── tasks.md             # Phase 2 — NOT created here
```

### Source code

```text
relay-platform/
├── services/api/
│   ├── migrations/
│   │   └── 0021_audit_log.sql          the table, and the schema's first trigger
│   └── src/
│       ├── db/
│       │   ├── schema.ts               the table declaration            33 pages publish it
│       │   └── repository.ts           the writes, and the actor on the  51 pages
│       │                               constructor
│       ├── audit/
│       │   ├── audit.controller.ts     GET /v1/audit-log                 new
│       │   ├── audit.schema.ts         the query, built per request      new
│       │   ├── audit.reader.ts         the page                          new
│       │   └── audit.itest.ts          the write, the read, the scope    new
│       ├── isolation/
│       │   └── targets.ts              the moderation classification     12 pages
│       └── {users,messages,channels,media,webhooks}/*.module.ts
│                                       six construction sites, one line each
└── relay-tutorial/
    ├── app/(en)/part-4/chapter-18/the-log-that-cannot-be-edited/
    │   ├── page.mdx
    │   └── figures.ts
    └── fences/post-series.md           where codes.ts and targets.ts hunks go (4.11, 4.12)
```

**Structure Decision**: a new `services/api/src/audit/` module beside `request-log/`, which it
is modelled on. The write lives in `db/repository.ts` because the lint rule puts every query
there and because FR-005 needs it inside the action's own transaction; concentrating it there
also keeps the fence bill to one heavily-published file instead of six (R6).

## Phases

**These are `tasks.md`'s nine phases and they have the same names.** An earlier draft of this
section numbered its own — *table and trigger*, *the writes*, *the read* at 3, 4 and 5 against
the task list's *US1*, *US2*, *US3* — and had **no phase at all** for publishing the
classification, which is a whole phase and three requirements. Chapter 4.17 met the same
defect and recorded it in one line: *the plan's phases were off by one.* A reader consults the
plan for the shape of the work; two shapes is worse than one.

**Phase 1 — Setup: the premise, measured before anything is built.** Derive the route list from
a booted application and write the real number down; `targets.itest.ts` prints
`gauntlet targets: N derived, M attacked, …` and asserts the both-directions property without
pinning N, deliberately. Record the lane and CI baselines the way chapter 4.17 did — every exit
code outside a pipe, every gate's counted line, and the CI error set per error. **Count the
fence bill here** (R6), not at the end.

**Phase 2 — Foundational: the decision.** Classify all 24 tenant-reachable mutating routes with
a reason each; decide R3's open question — a field on `targets.ts` or a sibling table; decide
the foreign key's `ON DELETE`; and **resolve FR-005 against FR-012**, which cannot both hold
for the four methods that act outside a transaction. This phase produces documents, not code,
and it is the chapter's product. **It is also User Story 3's substance arriving first**, because
US1 cannot write entries for a set nobody has decided — the decision is foundational and its
publication is phase 5.

**Phase 3 — User Story 1: a record nothing can change.** Migration `0021` with the table and
the trigger, then the writes. **The probe's two bypasses are part of the deliverable**, not an
afterthought: `session_replication_role = replica` and `DROP TRIGGER` both succeed, and the
chapter's claim is scoped to what the probe shows. Then the constructor's optional context at
six sites with an assertion standing in for the compiler, the external id threaded where the
write site holds only a uuid, and one action at a time — starting with the ban pair, the one
with no trace today. **FR-012 is checked per action rather than assumed**: each action's own
tests must stay green without being edited.

**Phase 4 — User Story 2: the read.** `GET /v1/audit-log`, the 403 for a principal with no
environment, the per-request schema built from the injected action set, `has_more` because
EIR-API-06 requires it, the index measured, and the isolation test that performs the same
actions in two environments.

**Phase 5 — User Story 3: the set, published and checked.** The classification with a reason
per route, the both-directions assertion, **SC-004 run red** by adding a route and watching the
suite fail, the routes the spec's rule misclassified recorded as findings, and the procedure
for adding an action — published both in the chapter and where the classification lives,
because `docs/12` calls this chapter *registry-shaped* and a registry keeps its procedure next
to itself.

**Phase 6 — the probes.** Delete each tenancy predicate and re-run, the way chapters 4.11 and
4.12 did; a coverage number will not find an SQL scope. Run the gauntlet. Perform the unban
with `nats` and `clickhouse` stopped (SC-006). Pin the new files, and probe the pins both ways.

**Phase 7 — the documents.** **ADR-35 in both `docs/06-adr-deep-dives.md` and
`docs/05-sad.md`**, because an ADR lives in two places and the deep dive is the one that gets
forgotten; FR-MOD-03 amended for the retention it cannot enforce and the
actor it cannot identify; **`docs/05-sad.md:430`'s *"There is no `audit_log` table"* corrected**,
because this chapter makes it false; `docs/12` row 19 CLOSED; both copies of the Part 4 table;
SRS revision 1.25; `clauses.md` as a count.

**Phase 8 — the chapter.** Prose, figures, the TRAP box, fences, the chain to zero.

**Phase 9 — the record and the close.** Baseline, gaps, traceability, the quickstart run as a
document, the lane set, push, the per-error CI comparison, tag.

## Constitution Check, re-evaluated after Phase 1

Nothing in the design moved a verdict. Two gained evidence and one gained a limit.

**VII's justification survived being wrong about why it was needed.** The claim *"the schema's
first trigger"* came from a grep whose zero is produced by a test, not by absence of thought —
analysis pass 18, nine passes after the previous CRITICAL, from one row of `docs/12` §4.
**A zero from an instrument is a claim about the corpus only if you know what produced it**, and
this is the case where the answer was *a test written to produce it*. What the mechanism is
justified against is unchanged and still measured.

**VII gained its justification and it is measured, not argued.** The trigger is this schema's
first, and the alternative a reviewer would reach for — `REVOKE UPDATE, DELETE` — was run and
**does nothing**: the api connects as `relay`, `select usesuper` answers `t`, and the update
succeeded. A new mechanism justified by *"the boring one does not work here"* is the form VII
asks for, and the proof is four lines of `psql` rather than a paragraph.

**VI gained a probe that can fail.** FR-004 is discharged by attempting the `UPDATE` and the
`DELETE` and being refused, at the storage layer, because the api exposes no route that could
attempt either — so a probe through the api would prove nothing about the table. The quickstart
runs the attack; the suite runs it again.

**I is unchanged and its cost is now visible.** The read route is tenant-scoped with no
parameter naming an environment, which is the media worker's own shape. Chapters 4.11 and 4.12
both found that an SQL scope carries no JavaScript branch, so a coverage number cannot see it:
the probe is to delete each predicate and re-run, and phase 6 does that rather than trusting a
pin.

**AND IV TAKES A SECOND READING NOW THAT FR-005a EXISTS.** Four of the seven candidate methods
— `unbanUser`, `setMemberRole`, `archiveChannel` and `unarchiveChannel` — perform their action
outside a transaction, so recording an entry atomically with them means **adding** one. That
moves a write boundary, which is squarely IV's subject, and it is permitted rather than
overlooked: FR-005a allows it and FR-012 names the exception. What each action gains is a
transaction, the ability to say whether it changed a row, and **a new way to fail** — an action
whose entry cannot be written no longer succeeds. What none of them gains is a different
answer, a different status code or a different event, and T031 checks that per action by
re-running each one's existing suite unedited.

**And the design added one honest limit rather than hiding it.** Immutability holds against the
application and against accident, and not against `SET session_replication_role = replica` —
one line, measured, and available to the role the api already connects as. The chapter states
the scope of its own claim. Writing *"immutable"* without that sentence would be exactly the
kind of comment chapter 4.17 spent its TRAP box on.

## Risks this plan is carrying

**Re-read after fifteen analysis passes, and two of the four had gone stale the way the spec's
Assumptions had** — one describing as a danger the thing the spec later decided to permit, one
listing a resolved item as live. A register that carries closed items makes the open ones harder
to see, which is the only job it has.

- **The immutability claim is weaker than the word.** A superuser disables every trigger with
  one `SET`, and the api connects as one. The chapter states what the probe shows and records
  the non-superuser role as a gap with its cost. ADR-35's reversal condition is that same
  deployment change, and NFR-SEC-10 — a second clause wanting an immutable trail, for exactly
  this actor — stays unmet. **Writing *"immutable"* without that sentence would be the
  chapter's own TRAP box.**
- **R3's open question had a fence bill on both sides, and the cheaper answer was also the
  better one** — resolved at T011 in favour of a sibling list. The risk this entry named, that
  the bill would argue against the right design, did not materialise; counting the bill in
  phase 1 is what let the question be decided at all, because the field variant had to be
  built and diffed before either side had a number.
- **FR-005a's exception taken wider than it was measured for.** This risk read *"FR-012 is the
  one most likely to be violated quietly — adding an entry to a transaction changes what that
  transaction does"*, and that is now the **permitted** case: four methods were measured to act
  outside a transaction and FR-012 names the exception. **The live risk is scope creep in the
  exception** — a fifth method gaining one because the first four did. T031 checks it per
  action by re-running each action's own suite unedited, and T075 checks it against the diff.
- **The classification will produce findings, and some will be routes nobody would have
  listed.** The premise this risk was written with is closed — the spec said nine where the
  population is 24 — pass 2 corrected nine to 25 and T005's derivation then corrected 25 to 24 —
  but the prediction stands, and T044 records each misclassification with what the rule said
  and what the right answer is.
- **No gate refuses a chapter ordinal in platform source, and this chapter writes into it.**
  `docs/12` §6 named that gate as a precondition for chapter one; seventeen chapters later it
  does not exist. Measured: **257 Part 4 ordinals** across 16 chapters, and **27 Part 3 ones**
  back on a surface 045 took to zero by hand. T009a records the number; the standing rule keeps
  this chapter from adding to it; **repairing 257 is nobody's task yet.**
- **This chapter enlarges row 22, and the part's name depends on row 22 landing.** `docs/12`
  §2.2: *"The part is named* Everywhere the data went*… its meaning only completes at movement
  VII. **The name is a promise the last movement has to keep. If erasure is deferred, the title
  lies and must change with it.**"* Research R8 defers *what erasure does to an audit entry
  naming an erased user* — correctly, FR-MOD-04 owns it — but **that obligation did not exist
  when the part was named.** The tension is recorded in R8 and in Out of Scope; the fact that
  this chapter added to the last movement's bill is recorded here.
- **`docs/06-adr-deep-dives.md` is four ADRs behind the summary.** ADR-31 through 34 are in
  `docs/05-sad.md` and appear **zero** times in the deep dive. T054b writes ADR-35 into both,
  which keeps the gap from becoming five and does nothing about the four — chapter 4.5 recorded
  this failure mode and it has been live since.
