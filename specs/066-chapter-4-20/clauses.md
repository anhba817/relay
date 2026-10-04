# Clauses — chapter 4.20, "The messages that expire"

A verdict per obligation, with where. **met** means the platform does it and
something asserts it; **demonstrated** means the chapter shows it end to end;
**unmet by decision** means it was weighed and declined, with the reason;
**unreachable** means no fixture on this lane can put the clause in front of it.

## FR-MOD-06 — three obligations, and the chapter's own premise check found none met

> *Configurable message retention per environment (30 / 90 / 365 days /
> indefinite) shall be supported, with expired messages hard-deleted by a
> scheduled job.*

| obligation | verdict | where |
|---|---|---|
| **configurable per environment** | **met** | `PATCH /v1/environments/{id}`, `environments.schema.ts`, `environments_retention_days_check`. 7 of 7 in `environments.itest.ts` |
| **the four options** | **met** | a literal union of 30 / 90 / 365 and `null`, refused in two places — the schema produces the 400 and the CHECK constraint refuses a caller nobody anticipated |
| **hard-deleted** | **demonstrated** | `destroyMessages`, and it was **refused by the platform's own schema until this chapter**. `0025` is what licenses it and ADR-36 is what licenses `0025` |
| **by a scheduled job** | **UNMET BY DECISION** | there is no scheduler. See below |

**THE PREMISE CHECK IS WHY THIS TABLE EXISTS.** Chapter 4.19's `docs/12` §7.5
said *check row 21's premise before writing it*, and four of FR-MOD-01's five
obligations turned out already met. Here the inverse: **`retention_days` had
existed since chapter 2.1 and was set on 0 of 33,051 environments**, nothing
read it, no scheduler existed, and the hard deletion the clause names was
**refused by the database**. None of the three was met.

## The fourth clause bounded by ADR-28's absent scheduler

`by a scheduled job` joins **FR-ANL-06**'s daily reconciliation, **DR-17**'s
storage comparison and **FR-MOD-03**'s retention year. Four clauses now say
*periodically* and nothing in this platform runs anything periodically.

**AND THIS ONE IS A DIFFERENT KIND OF SENTENCE FROM THE OTHER THREE**, which is
worth more than the count. Those are **reporting obligations**: an absent
reconciliation costs accuracy, and a tenant reads a number that drifted. This
one is a **customer telling an auditor that data does not exist.** A sweep that
never runs does not make a report wrong — it makes a promise false, and the
party who discovers it is not the operator.

So the chapter publishes the command and refuses to publish a deadline. **No
surface carries an `expires_at`, a `retention_edge` or anything a client could
read as a bound**, which is the line chapter 4.18 drew for the audit log's
retention year. The request log publishes one only because its table has a real
TTL that ClickHouse enforces.

## FR-MED-11 — one obligation

> *Environment retention policy (FR-MOD-06) shall apply to media: expired
> messages delete their objects with them.*

| obligation | verdict | where |
|---|---|---|
| **expired messages delete their objects** | **demonstrated** | the sweep's media half; `retention.itest.ts` asserts a sole-referenced object is gone and a shared one survives, 1 and 1 in the counted line |
| *(the "unless shared" reading)* | **met** | `unreferencedAmong`, batched, operand bound. FR-MSG-11 has allowed the same `media_id` in two messages since chapter 3.24, so the survivor is a real case rather than a defensive one |
| **renditions** | **met, by the schema** | `media_objects_parent_fk`'s cascade, which chapter 4.15 chose for this. Asserted rather than reasoned about |

**THE CLAUSE HAS NO REFERENTIAL INTEGRITY BEHIND IT AND CANNOT GET ANY.**
`media_objects` has **no foreign key to `messages`** — the link is a `media_id`
inside a jsonb array (FR-MED-11's own shape) — so *unless shared* is a reverse
lookup the application performs, not a constraint the database enforces. The
cost is measured: bound operand 107 buffers, set-wise 3,423 and 127.9 ms with
the GIN index idle, batched 100 at a time 976 buffers for about 9.8 an object.

## FR-MOD-05 — unbuilt, and it is the undo this chapter does not have

> *The system shall support exporting all data for a tenant as newline-delimited
> JSON, generated asynchronously with a notification on completion.*

**Unbuilt.** It sits two rows above FR-MOD-06 in the same table and it is the
clause that would let a tenant keep what a policy destroys. A customer who sets
thirty days and then wants last quarter's messages has **no supported way to
have taken a copy first.**

Naming it is the honest version of *no undo*. The chapter says the export does
not exist rather than saying expiry is irreversible and leaving the reader to
wonder whether something else covers it.

## What this chapter deliberately did not do

- **No per-channel or per-user policy.** FR-MOD-06 says per environment.
- **No notification of what expired.** A different clause and a larger table —
  and the audit log is deliberately not it: FR-MOD-03's population is
  *moderation actions*, which are things a credential did, and the sweep carries
  no credential. That is also why `PATCH /v1/environments/{id}` is classified
  `not-moderation`.
- **No bound on a single run.** Whether a sweep that would destroy a million
  rows should stop and resume is a real question and **the lane cannot inform
  it**: nothing here is thirty days old, so every figure comes from a backdated
  fixture. Recorded as a known shape rather than solved on a guess.
- **`gaps.md` 058-3 not repaired.** A malformed path parameter answers 500 on
  twenty-two shipped routes and this chapter's makes twenty-three.
