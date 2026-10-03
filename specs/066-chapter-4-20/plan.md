# Implementation Plan: Chapter 4.20 — The messages that expire

**Branch**: `066-chapter-4-20` | **Date**: 2026-10-03 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/066-chapter-4-20/spec.md`

## Summary

`docs/12` row 21 asks for FR-MOD-06's retention job. The premise was run first — the habit
§7.5 asked of chapter 4.19 — and it inverts that chapter's result: **none of FR-MOD-06's three
obligations is met.** The policy column has existed since chapter 2.1 and is set on 0 of 33,051
environments; there is no scheduler of any kind; and the hard deletion the clause names is
**refused by the database**.

The refusal is the chapter. Exactly one table references `messages` and chapter 4.19 put a row
in it for every deletion, so **5,495 messages cannot be hard-deleted today** and the number
grows by one per deletion. 4.19 wrote that collision down, declined to pre-solve it, and named
row 22's erasure as the chapter that would meet it. **Row 21 meets it first.**

And it is a pincer rather than a sequence. Deleting the message is refused by the foreign key;
deleting the version rows first is refused by the append-only trigger; **and changing the key
to `ON DELETE CASCADE` is refused too, because a cascade issues an ordinary `DELETE` and a row
trigger fires on it.** The only mechanism that works without a schema change is
`session_replication_role = replica` — which is one of the two bypasses ADR-35 published as the
*limits* of its own guarantee.

So the chapter's product is a narrow, auditable exception: the trigger names its one legitimate
deleter, the foreign key cascades, and **a published guarantee changes, which is a new ADR**.

## Technical Context

**Language/Version**: TypeScript 5.x on Node 22, as the rest of `services/api`

**Primary Dependencies**: none new

**Storage**: PostgreSQL — one check constraint, one changed delete action, one trigger
condition. No new table. Object storage for FR-MED-11's half

**Testing**: vitest. The api integration lane for the sweep and the route, the isolation
gauntlet for tenancy, a unit lane for the policy's arithmetic

**Target Platform**: Linux server, the composed stack

**Performance Goals**: the shared-attachment check is **883 buffers with a bound operand
against 94,132 set-wise** (research R2), which is the shape the sweep is written in rather than
a figure to beat

**Constraints**: no breaking change to a published response (CON-05). The sweep adds no field
implying a deadline the platform does not enforce

**Scale/Scope**: 199,275 messages, 14,039 media objects, 33,051 environments, **0 with a
policy**, and **nothing older than 19 days** — so every demonstration is a backdated fixture

## Constitution Check

| principle | verdict |
|---|---|
| **I — tenant isolation** | **engaged and load-bearing.** A sweep is the first thing in this platform that destroys rows in bulk, and a predicate scoped wrong destroys another tenant's data rather than leaking it. Every read and delete is scoped by `environment_id`, and the per-arm probe deletes each scope one at a time **and in combination**, because 4.19 measured three scoped reads where removing any two was invisible |
| **II — no acknowledged message is lost** | **engaged, and the clause is the exception.** FR-MOD-06 is the licensed way to lose one. The sweep destroys only what a tenant's own policy marks expired, and nothing else in the platform gains a delete path |
| **III — two data paths** | untouched. Operational expiry does not reach ClickHouse; DR-09's 90-day raw-event TTL is a different clock with a different owner, and the chapter states the boundary rather than widening to it |
| **IV — single writer** | **satisfied by the predicate being self-clearing.** A destroyed message cannot match the next pass, so re-running needs no lease, heartbeat or reaper — chapter 4.13's compare-and-set argument in a different shape. **It needs a test rather than a sentence** (research R7) |
| **V — API-first** | the policy is set through a public route. The sweep is a command and not a route, deliberately: see the ADR question |
| **VI — test-verified** | five bullets, answered below |
| **VII — boring by design** | no new service, no new dependency, no new table. **One new ADR, and it is unavoidable** |

### Principle VI in full, because a row that answers one bullet reads as answering five

| bullet | verdict |
|---|---|
| stable identifiers, priority, verification method | met. 12 FR and 12 SC, `traceability.md` built by reading |
| **70% coverage; ordering, idempotency and tenant isolation at 100% branches** | **two of the three are this chapter's.** Tenant isolation is the sweep's predicate, probed per arm. **Idempotency is FR-008** — the second run must change nothing, counted absolutely rather than as a delta, because 0 → 0 is satisfied by nothing happening |
| the cross-tenant suite gates releases | met. The gauntlet runs, and a bulk-delete route is a new shape for it |
| the quickstart runs unmodified, verified in CI | **UNMET, and not this chapter's.** No quickstart executes in `ci.yml` and the phase-9 task runs this one by hand and corrects it in place. Named here because the alternative is a check that reads as answered |
| input validated against a schema before processing | **the new route is validated; `gaps.md` 058-3 is not repaired.** A malformed path parameter answers 500 on sixteen shipped routes and the new one would make seventeen, which is the argument for carrying rather than fixing one |

**Does this need an ADR?** Constitution VII: *"Every architecture decision is recorded as an ADR
stating its drivers, rejected alternatives, and reversal condition. ADRs are immutable once
accepted; superseding requires a new ADR."*

**Yes, and it cannot be avoided.** ADR-35 published the audit log's immutability as *to the
application and to accident, and not to somebody holding the database password*, and chapter
4.19 applied that scope to `message_edits`. This chapter makes it *to the application **except
one named path**, and to accident.* That is a change to a published guarantee, which VII says
is a new ADR superseding the scope clause rather than an edit to it.

**The ADR's drivers are measured, not asserted**: three of four escapes fail, and the one that
works without this change is the hole ADR-35 documented. **Its rejected alternatives are in
research R1** with the error each one produced. **Its reversal condition** is the same as
ADR-35's: a separate non-superuser role makes privilege the mechanism and the trigger the
second line, at which point a session setting is no longer the narrowest available exception.

## Project Structure

```
specs/066-chapter-4-20/
├── spec.md · plan.md · research.md · data-model.md
├── contracts/retention.md
├── quickstart.md               §0 and §1 MEASURED, the rest predictions
├── baseline.txt                (phase 1 onward)
├── clauses.md · traceability.md · gaps.md   (phases 5, 7, 9)
└── tasks.md
```

```
relay-platform/
├── services/api/migrations/0024_retention_policy.sql       the CHECK on retention_days
├── services/api/migrations/0025_expiry_may_delete.sql      the FK's delete action and the
│                                                           trigger's named exception
├── services/api/src/db/schema.ts                           the constraint
├── services/api/src/db/repository.ts                       the sweep's reads and deletes
├── services/api/src/retention/sweep.ts                     NEW — the command
├── services/api/src/retention/retention.itest.ts           NEW
├── services/api/src/environments/                          NEW — the PATCH route, module,
│                                                           controller, schema
├── services/api/src/app.module.ts                          the new module
├── services/api/src/isolation/targets.ts                   the new route, classified
└── vitest.coverage.config.mts                              pins for the new files
```

**TWO MIGRATIONS, AND THE SPLIT IS THE SAME HAZARD 4.19 RECORDED.** `migrate.ts` keys
`schema_migrations` on a filename with no checksum, so a file edited after it has applied never
re-runs while the ledger reports it done. Both are written before either applies.

## The fence bill, counted now

4.15's rule: count it in phase 1 where it can still change the sequencing, and read it as a
floor.

```
repository.ts              52 pages
schema.ts                  34 pages
app.module.ts              23 pages
vitest.coverage.config.mts 23 pages
targets.ts                 varies — counted in phase 1 against the tree
```

**FOUR FILES AT MINIMUM AND `targets.ts` ALMOST CERTAINLY A FIFTH**, all to
`fences/post-series.md` — every one is published by pages this chapter does not own, and one
rule for five files beats a judgement per file (4.8).

**AND THE BILL IS A CEILING AS OFTEN AS A FLOOR.** Chapter 4.19's plan named eight files and
the chain charged for five, because the work landed in fewer places than the file list
predicted. 4.18's list of 21 grew by six. The number is useful for sequencing and not for
prediction.

## Phases

1. **Setup and measurement.** The lane baseline, the CI baseline, the fence bill against the
   tree, and research R1–R7 re-read against the code rather than this document.
2. **The decisions.** The trigger's exception mechanism, the flag's name, whether the route is
   `PATCH /v1/environments/{id}` or something narrower — settled before a migration exists.
3. **US1 — the expiry, and the pincer.** Both migrations, the sweep, and the delete that is
   refused today. **The red probe comes first**: assert the refusal, then make it pass.
4. **US2 — the objects go too.** The reverse reference check, written so the planner can use
   the index 4.12 built.
5. **US3 — what runs it, published.** The clause's three obligations with a verdict each.
6. **The probes.** Each tenancy arm alone and in combination; the trigger still refusing
   everything it refused before; the sweep run twice.
7. **The documents.** FR-MOD-06 and FR-MED-11 read before being edited, the new ADR, SRS
   revision, both copies of the Part 4 table, `docs/12` row 21.
8. **The chapter.** 2,000–4,000 prose words, the hunks, `check:fences` to zero.
9. **The record and the close.** Coverage pins after the chain is zeroed, **and `check:fences`
   re-run after the pins go in.**

## Complexity Tracking

| the simpler thing | why it is not taken | what it would cost |
|---|---|---|
| `SET session_replication_role = replica` in the sweep | it is the hole ADR-35 published as the limit of its own guarantee, and it disables **every** trigger in the session | a sweep that is indistinguishable, at the database, from an attacker with the password |
| Drop `message_edits_message_id_fkey` | a version could then outlive its message, which is what makes the history trustworthy | the invariant moves from the schema into a procedure somebody maintains |
| Soft expiry — null the text, keep the row | FR-MOD-06 says **hard-deleted**, and a tombstone is precisely what expiry is not | a compliance promise met by a word change |
| A nullable `expires_at` on every message | 199,275 rows gain a column to express what `created_at` plus a policy already says | storage, a backfill, and two sources for one fact |
| Let the sweep delete objects by cascade | `media_objects` has **no foreign key to `messages`** — the link is a `media_id` inside jsonb | nothing to cascade; R2's reverse lookup is the only way |
| Build a scheduler | four clauses now want one and ADR-28 declined it three times | an architecture decision wearing a retention chapter's clothes |
| Publish `expires_at` on the message | a deadline the platform does not enforce, read by a compliance team | the exact field 4.18 refused for the audit log |

## Risks

- **THE CHAPTER CHANGES A GUARANTEE THE PREVIOUS CHAPTER SHIPPED, AND THAT IS THE WHOLE RISK.**
  `message_edits` was made append-only yesterday and is being given an exception today. If the
  exception is wider than one verb on one table under one named flag, the honest course is to
  stop and record FR-MOD-06 as unmet rather than to widen it. **The probe that decides this is
  running the old refusals after the change**, not reading the new condition.
- **A bulk delete scoped wrong destroys rather than leaks.** Constitution I's usual failure is a
  read; this one is a `DELETE`. The per-arm probe matters more here than anywhere it has been
  run, and 4.19 measured that two of three scopes can be removed invisibly.
- **The lane cannot exercise the clause.** Nothing is 30 days old, so every figure comes from a
  backdated fixture and **the cost of a real sweep is unmeasurable here**. 4.13's backdating
  piled 3,235 rows on one instant and turned twelve tests red; this one backdates per fixture.
- **FR-MED-11's reverse check is 106× the forward one** and runs per object. At lane scale that
  is fine and at tenant scale it is the thing that decides whether a sweep finishes.
- **The sweep has no runner, and the clause is a compliance promise.** The other three clauses
  bounded by ADR-28's absent scheduler are reporting obligations. This one is a customer
  telling an auditor that data does not exist. Recording it the same way is right; saying so in
  the same tone is not.
