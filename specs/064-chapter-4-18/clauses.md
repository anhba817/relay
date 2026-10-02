# Clauses — chapter 4.18, counted

SC-007 wants a count, not an adjective. Every obligation this chapter is answerable for,
with where it is discharged and what kind of discharge it is.

Four verdicts, and the difference between them matters more than the tally:

| verdict | what it means |
|---|---|
| **met** | the platform does it, and a test says so |
| **demonstrated** | the platform does it, and the proof is a probe that was run, not an assertion |
| **unmet by decision** | the platform does not do it, this chapter decided not to, and the reason is written down |
| **unreachable** | the clause cannot be satisfied by anything this chapter could build |

## FR-MOD-03, obligation by obligation

> Every moderation action shall be recorded in an immutable audit log with actor, action,
> target, timestamp, and request ID, retained for 1 year.

**Eight obligations.** The clause reads as one sentence and is not one.

| # | obligation | verdict | where |
|---|---|---|---|
| 1 | **every moderation action** is recorded | **met** | 8 write sites in `repository.ts`, each calling `recordAction` inside the action's own transaction; `moderation-routes.itest.ts` checks the classified set against the running router in both directions |
| 2 | the set of **moderation actions** is defined at all | **met** | `audit/moderation-routes.ts`, a reason on every one of 24 tenant-reachable mutating routes — the clause names a population and gives no membership rule, so the rule is this chapter's product |
| 3 | **an audit log** exists | **met** | `audit_log`, migration `0021` |
| 4 | **immutable** | **demonstrated** | a `BEFORE UPDATE OR DELETE` trigger, attempted through `psql` (T019) and through the suite (T030), and the suite was run red by dropping the trigger. **Scoped**: see below |
| 5 | **actor** | **met** | `actor_kind` + `actor_id`, threaded from the authenticated principal through an optional constructor argument whose production call sites are checked by reading the source |
| 6 | **action** | **met** | `action`, holding the route's own `METHOD /path` key — one name for the column, the filter and the list |
| 7 | **target** | **met** | `target_kind` + `target_id`, holding the identifier a customer uses |
| 8 | **timestamp** | **met** | `occurred_at timestamptz(3)`, written inside the action's transaction |
| 9 | **request ID** | **met** | `request_id`, the join to the request log (chapter 4.8); asserted in `audit.itest.ts` |
| 10 | **retained for 1 year** | **unmet by decision** | nothing prunes this table and nothing enforces a year. A retention job is a scheduled sweep and **ADR-28 records that this platform has no scheduler** — the same absence chapter 4.9 found for FR-ANL-06's daily job. What this chapter refused to do is publish a `retention_edge` the route does not enforce, which is how the request log's envelope would have been copied without thinking |

**Nine met or demonstrated, one unmet by decision.** The count is nine of ten and the one is
named.

### What "immutable" is scoped to, because the clause does not scope it

Measured, both directions (research R2, re-measured on the shipped table at T019 and T020):

| attempt | result |
|---|---|
| `UPDATE` through the application | refused — `audit entries are append-only (FR-MOD-03)` |
| `DELETE` through the application | refused, and **the row is still there** |
| `REVOKE UPDATE, DELETE` as the mechanism | **does nothing** — the api connects as a superuser |
| `SET session_replication_role = replica` then `UPDATE` | **succeeds**, the trigger does not fire |
| `DROP TRIGGER` then `DELETE` | **succeeds** |

**The log is immutable to the application and to accident, and it is not immutable to
somebody holding the database password.** This platform's api holds that password. The
chapter publishes that sentence rather than the word.

## NFR-SEC-10, which asks for the same artifact and is not satisfied by it

> Administrative access to production data shall require multi-factor authentication and
> shall be logged to an immutable audit trail.

**A second clause wanting an immutable audit trail, for a different actor — and it is
exactly the actor this chapter's mechanism cannot defend against.**

| obligation | verdict | why |
|---|---|---|
| administrative access requires MFA | **unmet**, and not this chapter's | an identity-provider property, outside the platform |
| administrative access is logged | **unmet** | nothing records a `psql` session. The audit log records what the API did, and an operator with the database password does not go through the API |
| that log is immutable | **unreachable as built** | the one actor who could tamper with `audit_log` is the one actor NFR-SEC-10 wants it to hold to account. A trigger a superuser can drop is not an audit trail for a superuser |

**The two clauses are not the same artifact and this chapter satisfies one of them.** Saying
so is the point of this section: a reader who sees *"immutable audit log, FR-MOD-03, shipped"*
will reasonably assume NFR-SEC-10 came with it, and it did not.

**One change would move both**, and it is a deployment change rather than a chapter: a
separate, non-superuser role for the application. `REVOKE UPDATE, DELETE` becomes real for
that role, the trigger stops being the only line, and `psql` as a superuser becomes an
exceptional act somebody can audit instead of the api's ordinary posture. It is ADR-35's
reversal condition for that reason.

## The clauses this chapter touches without owning

| clause | what this chapter does about it |
|---|---|
| **FR-MOD-01** (retrieve any history via API key) | unchanged. Reading is not an action, and no read is recorded — a log of reads is a different clause and a much larger table |
| **FR-MOD-02** (delete any message via API key) | **already met before this chapter**, and now recorded. `moderation-when-application` is its one route: the same verb under a user token is chapter 3.23's FR-013 and is not moderation |
| **FR-MOD-04** (erasure) | row 22's, and it collides with this table: an entry naming a user is a moderator's action, not the user's data. `audit_log` has no `ON DELETE` on its tenant key and this chapter takes no position on the user case |
| **FR-013a** (silence is absence of permission) | load-bearing here. It is why *edit another author's message* is not in the set: FR-MOD-02 grants deletion and says nothing about editing, so the route accepts a user token only, and the action a reasonable reader expected to find does not exist |
| **EIR-API-06** (cursor pagination with `next_cursor` and `has_more`) | **met**, and this is the second route in the platform to meet it. Chapter 4.8 was the first; `messages.service.ts` has been non-conforming since chapter 2.4 |
| **Constitution I** (tenant isolation) | the read's scope is the principal's environment and no parameter names one. Attacked in the gauntlet with a plant that goes through the product |
| **Constitution IV** (one writer) | the trigger refuses the api's own writes, which is the opposite of the sentinel guard it had to be distinguished from — `no-trigger-in-migrations.test.ts` was narrowed deliberately rather than worked around |
| **Constitution VII** (every decision is an ADR) | ADR-35 |
