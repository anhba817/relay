# Traceability — chapter 4.18

**Built by reading, not by grep.** Chapter 4.11's mechanical coverage map raised fourteen
alarms over `tasks.md` and all fourteen were false — every one covered in substance by a task
that did not quote the identifier. What a grep can tell you is which strings appear; what a
clause needs is somebody who read it.

Each row says where the obligation is discharged and what kind of evidence that is:
**code** (it exists), **test** (a test asserts it), **measured** (a probe was run and the
number recorded), **decided** (it is not built and the reason is written down).

## The spec's functional requirements

| | requirement | where | evidence |
|---|---|---|---|
| FR-001 | an entry per moderation action | `repository.ts`, 8 `recordAction` call sites | code + test (`audit.itest.ts`) |
| FR-002 | the set is defined with a reason per route | `audit/moderation-routes.ts`, 24 entries | code; `routes.md` carries the long reasons |
| FR-002a | one route classified by the credential | `deleteMessage`, gated on `this.actorKind` | test, **both directions** (an application credential writes one, a user token none) |
| FR-003 | the set is derived from the running router | `moderation-routes.itest.ts`, both directions | test, and **run red** at T043 |
| FR-004 | not modifiable by any path the platform exposes, demonstrated | the trigger; `audit.itest.ts`'s refusal probe | measured (T019, T020) + test, **run red by dropping the trigger** |
| FR-005 | the entry commits with the action | `recordAction(tx, …)` inside each action's transaction | code; **scoped** by FR-005c below |
| FR-005a | a transaction may be added, and which actions needed one is recorded | `unbanUser`, `setMemberRole`, `archiveChannel`, `unarchiveChannel` | code + measured (T049: 94.6% on an archive) |
| FR-005b | an action that cannot report a change is made able to | `unbanUser` gains `isNotNull`, a `RETURNING` and a transaction | code + test (*an unban that lifted nothing writes nothing*) |
| FR-005c | every production construction site supplies an actor or the named absence | `repository.itest.ts`'s source walk, both directions | test, **written red before T023** |
| FR-006 | a tenant reads its own, ordered, windowed, and no other's | `audit.reader.ts`, `db/audit-reads.ts`, `GET /v1/audit-log` | test (`audit.itest.ts`, `route.itest.ts`, the gauntlet) |
| FR-007 | no row in two consecutive pages | the row-value cursor on `(occurred_at, id)` | test + **measured** (T032a: the OR form lands in a `Filter:`) |
| FR-008 | a refused action and a no-op action earn no entry | the guard precedes each `recordAction` | decided per action (T014) + test (re-ban, unban-that-lifted-nothing) |
| FR-009 | the refusal names the field | `invalid_request` with the field, `forbidden` with the reason | test, **by code and not by status** |
| FR-010 | the read is application-credential only | `@Accepts("application")` | test (`route.itest.ts`), **run red by deleting the decorator** |
| FR-011 | a principal with no environment is refused rather than served an empty page | the controller's 403 | code. **The branch is unreachable** — T046 arm 3 — and the clause is met by the decorator instead; both recorded |
| FR-012 | no existing moderation behaviour changes | T031: four suites, 179 of 179, **no expectation edited** | measured |
| FR-013 | the actor and request id reach the write | `audit/actor.ts`, five module factories | code + test |

**Sixteen functional requirements, sixteen discharged**, one of them (FR-011) met by a
different mechanism than the one it names — recorded as a finding rather than quietly
re-pointed.

## The success criteria

| | criterion | result |
|---|---|---|
| SC-001 | a ban and its reversal produce two entries naming actor, target and order | **PASS** — whole-row equality, not field by field |
| SC-002 | the entry's `request_id` is the one the api assigned | **PASS** |
| SC-003 | `UPDATE` and `DELETE` are refused and the row survives | **PASS**, demonstrated at the database and in the suite |
| SC-003a | the two bypasses are published with the claim | **PASS** — in the migration, the SRS, the SAD and ADR-35 |
| SC-004 | a route added with no decision fails a check | **PASS**, run red twice — unclassified, then classified for security only |
| SC-005 | a tenant sees its own and zero of another's | **PASS** — the reader-level test and the gauntlet's HTTP attack |
| SC-006 | the entry survives the analytical pipeline being stopped | **PASS** — `nats` and `clickhouse` stopped, two entries |
| SC-007 | FR-MOD-03's obligations counted, not adjectived | **PASS** — `clauses.md`: ten obligations, nine met or demonstrated |
| SC-007a | every non-test, non-document change listed and checked against the diff | phase 9 |
| SC-008 | the CI error set compared per error, both directions | phase 9 |
| SC-009 | `check:fences` zero and the tutorial builds | phase 8 |
| SC-010 | 2,000–4,000 prose words | phase 8 |

## The published clauses

| clause | verdict | where it is recorded |
|---|---|---|
| **FR-MOD-03** | nine of ten obligations met or demonstrated | SRS revision 1.25; `clauses.md` has the breakdown |
| FR-MOD-03's *"retained for 1 year"* | **unmet by decision** | SRS 1.25, ADR-35, on ADR-28's precedent |
| **NFR-SEC-10** | **unmet**, and not satisfied by FR-MOD-03 | `clauses.md`, ADR-35's consequences |
| FR-MOD-01, FR-MOD-02 | unchanged; 02 is now recorded | `clauses.md` |
| **EIR-API-06** | met — the platform's second conforming list route | `route.itest.ts` asserts the fields by name |
| Constitution I | the read is scoped; no parameter names an environment | the gauntlet's 48/40/8 line |
| Constitution III | the log is operational, measured under a stopped pipeline | ADR-35 decision 1 |
| Constitution IV | the trigger refuses the api's own writes | `no-trigger-in-migrations.test.ts`, narrowed deliberately |
| Constitution VII | **ADR-35**, in `docs/06` *and* the SAD | T054a, T054b |

## What this chapter did not discharge, and who owns it

- **ADR-31, 32, 33 and 34 are in the SAD and appear zero times in `docs/06`.** Chapter 4.5
  wrote the rule — *an ADR lives in two documents and the deep dive is the one that gets
  forgotten* — and four ADRs have been written since without it. ADR-35 is in both; the
  backfill is not this chapter's. `gaps.md`.
- **`gaps.md` 058-3**, the caller-triggered 500 on sixteen routes taking a path parameter.
  This route takes none, which is the cheap way not to join that list, and does not fix it.
- **Row 22's erasure** inherits the collision this table creates: an entry naming a user is a
  moderator's action, not the user's data. `audit_log` takes no `ON DELETE` on its tenant key
  and this chapter takes no position on the user case.
