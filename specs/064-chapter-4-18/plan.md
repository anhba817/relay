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
gives no membership rule. The router serves **25 tenant-reachable mutating routes** and the
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

**Performance Goals**: none stated by the clause. One additional insert inside transactions
that already exist; the plan measures the cost rather than predicting it, and publishes the
number beside the action's own.

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
| **VII. Boring by design** | **ENGAGED, with one justification owed** | No dependency, no service, no container. One new mechanism: a Postgres trigger, the schema's first. R2 is the justification and it is measured — the obvious alternative, `REVOKE`, does nothing on this deployment. |

**No violation requires a Complexity Tracking entry.** The trigger is new and is argued in R2
against the alternative that was measured inert; that is the form constitution VII asks for.

## Project Structure

### Documentation (this feature)

```text
specs/064-chapter-4-18/
├── plan.md              # This file
├── research.md          # Phase 0 — R1..R8, with the trigger probe and its two bypasses
├── data-model.md        # Phase 1 — the entry, the set, the actor
├── quickstart.md        # Phase 1 — walk it by hand, including the attack
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

**Phase 1 — the premise, measured before anything is built.** Derive the route list from a
booted application and write the real number down; `targets.itest.ts` prints
`gauntlet targets: N derived, M attacked, …` and asserts the both-directions property without
pinning N, deliberately. Record the lane and CI baselines the way chapter 4.17 did — every exit
code outside a pipe, every gate's counted line, and the CI error set per error. **Count the
fence bill here** (R6), not at the end.

**Phase 2 — the decision.** Classify all 25 tenant-reachable mutating routes with a reason
each, and decide R3's open question: a field on `targets.ts` or a sibling table. This phase
produces a document, not code, and it is the chapter's product.

**Phase 3 — the table and the trigger.** Migration `0021`, the schema declaration, and the
probe that attempts `UPDATE` and `DELETE` and is refused. **The probe's two bypasses are part
of the deliverable**, not an afterthought: `session_replication_role = replica` and
`DROP TRIGGER` both succeed, and the chapter's claim is scoped to what the probe actually
shows.

**Phase 4 — the writes.** The constructor change at six sites, then one action at a time,
starting with the ban pair because it is the one with no trace today. Each action gets its
entry inside the transaction it already has, and FR-012 is checked per action rather than
assumed: the action's own tests must stay green without being edited.

**Phase 5 — the read.** `GET /v1/audit-log`, the 403 for a principal with no environment, the
per-request schema built from the injected action set, and the isolation test that performs the
same actions in two environments.

**Phase 6 — the probes.** Delete each tenancy predicate and re-run, the way chapters 4.11 and
4.12 did; a coverage number will not find an SQL scope. Run the gauntlet. Run the read route
with the analytical pipeline stopped (SC-006).

**Phase 7 — the documents.** FR-MOD-03 amended for the retention it cannot enforce and the
actor it cannot identify; `docs/12` row 19 CLOSED; both copies of the Part 4 table; the SRS
revision; `clauses.md` as a count.

**Phase 8 — the chapter.** Prose, figures, fences, the chain to zero.

**Phase 9 — the record and the close.** Baseline, gaps, traceability, the quickstart run as a
document, the lane set, push, the per-error CI comparison, tag.

## Constitution Check, re-evaluated after Phase 1

Nothing in the design moved a verdict. Two gained evidence and one gained a limit.

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

- **The immutability claim is weaker than the word.** A superuser disables every trigger with
  one `SET`, and the api connects as one. The chapter states what the probe shows and records
  the non-superuser role as a gap with its cost. **Writing *"immutable"* without that sentence
  would be the chapter's own TRAP box.**
- **R3's open question has a fence bill on both sides**, and the cheaper answer may be the
  worse one. Deciding it in phase 2 with the bill in hand is the point of counting the bill in
  phase 1.
- **FR-012 is the one most likely to be violated quietly.** Adding an entry to a transaction
  changes what that transaction does. Chapter 4.17's method — diff the platform changes and
  check every one is a test, a comment or the thing the chapter is for — is SC-007a, and it
  runs in phase 9 rather than being trusted.
- **The population is 25 and the spec said nine.** The spec was counting what it expected to
  include. Expect the classification to produce findings, and expect some of them to be routes
  nobody would have listed.
