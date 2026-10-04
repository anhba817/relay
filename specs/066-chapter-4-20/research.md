# Research — chapter 4.20, "The messages that expire"

Every figure below was measured against the development lane before the plan was written,
most of them inside a rolled-back transaction so the probe did not become the data.

---

## R1 — The hard delete is pinned between a foreign key and a trigger, and three of four escapes fail

FR-MOD-06 says *hard-deleted*. Exactly one table references `messages`:
`message_edits_message_id_fkey`, `NO ACTION`. Four ways out, each run:

| | attempt | result |
|---|---|---|
| **A** | delete the version rows first, then the message | **refused** — `message versions are append-only (FR-MSG-07)` |
| **B** | change the FK to `ON DELETE CASCADE`, then delete the message | **refused** — and the error names the generated statement: `DELETE FROM ONLY "public"."message_edits" WHERE $1 = "message_id"` |
| **C** | `SET LOCAL session_replication_role = replica`, delete the children | `DELETE 1` |
| **D** | a trigger that permits `DELETE` when a named session setting is on | `DELETE 1`, with both refusals intact |

**B IS THE RESULT WORTH HAVING, AND IT IS THE ONE A READER WOULD GUESS WRONG.** A cascade is
generated SQL, not a privileged path: it issues an ordinary `DELETE` against the child table
and a `BEFORE DELETE … FOR EACH ROW` trigger fires on it. **So no schema change resolves this.**
The obstacle chapter 4.19 described as *"the foreign key first, the trigger second"* is not two
obstacles in a line — it is a pincer, and clearing the first puts you into the second.

**C WORKS AND IS THE WRONG MECHANISM.** `session_replication_role = replica` is one of the two
bypasses ADR-35 **published as the limits of its own guarantee**. Using it here would make the
platform's retention sweep the first caller of a hole the previous chapter documented as the
reason its claim is scoped. It also disables *every* trigger in the session, so it is wider
than the one table and the one verb.

**DECISION: D.** The trigger names the one legitimate deleter:

```sql
IF TG_OP = 'DELETE' AND current_setting('relay.expiring', true) = 'on' THEN RETURN OLD; END IF;
```

Measured in all three directions rather than the one that passes:

```
UPDATE, flag irrelevant            refused
DELETE, flag unset                 refused
DELETE of the MESSAGE, flag set + ON DELETE CASCADE       DELETE 1
```

**AND IT CHANGES A PUBLISHED GUARANTEE, WHICH IS AN ADR RATHER THAN A MIGRATION.** ADR-35's
scope was *immutable to the application and to accident, and not to somebody holding the
database password*. After this chapter it is *immutable to the application except one named
path, and to accident*. Constitution VII makes an accepted ADR immutable, so this is **ADR-36**,
superseding ADR-35's scope clause rather than an edit to it.

**Alternatives considered and rejected**: dropping the FK (loses the guarantee that a version
cannot outlive its message, which is what makes the history trustworthy); soft-expiry by
nulling text (FR-MOD-06 says *hard-deleted* and a tombstone is what expiry is not); a separate
`expired_messages` table (two tables holding one kind of row, which chapter 4.15's one-table
argument refuses).

## R1a — Three documents reserve hard deletion for one path, and FR-MOD-06 asks for a second

Found at analysis pass 5, by opening the constitution and the SRS rather than the source.

```
constitution II, bullet 4   "Deletions produce tombstones that preserve sequence, author,
                             and timestamps; hard deletion exists ONLY ON THE COMPLIANCE PATH."
FR-MSG-08                   "Hard deletion shall occur ONLY VIA THE COMPLIANCE DELETION
                             ENDPOINT."
DR-06                       "Deleted messages shall RETAIN THEIR ROW; only `text` and
                             `attachments` shall be cleared."

FR-MOD-06                   "expired messages HARD-DELETED BY A SCHEDULED JOB."
```

The first three are consistent with each other. **This is chapter 4.19's finding run
backwards**: that chapter cited FR-MSG-08 as the clause its defect broke, this feature's own
spec quotes it for that reason, and nobody noticed the sentence forbids this chapter too.

**DECISION: a retention sweep IS a compliance path.** The constitution's own word is **path**,
not *endpoint*, and a retention policy exists to keep a promise a customer made to an auditor —
the same kind of obligation FR-MOD-04's erasure serves, arriving on a schedule rather than on a
request. Under that reading **the constitution needs no amendment**, which is the strongest
thing about it: the rule that is hardest to change is the one that already permits this.

**WHAT IT COSTS IS TWO SRS AMENDMENTS**, and they are the two documents narrower than the
constitution. FR-MSG-08 says *endpoint* where the principle says *path*; DR-06 says a deleted
message retains its row, which a sweep destroys. Both are amended to name the second path
explicitly rather than left to be read around.

**Alternatives considered and rejected.** *Amend constitution II* — unnecessary under this
reading, and three items already stand against principle III with an amendment written and
never applied, so a fourth unapplied one would be a pattern. *Record FR-MOD-06 unmet by
decision* — honest, and the fallback used for FR-MED-07, FR-MED-09's rendering half,
FR-MOD-03's year and FR-ANL-06's job, but it leaves row 22 to solve the pincer alone. **Soft
expiry — clear `text` and keep the row** — satisfies all three clauses word for word and is the
one option to avoid: FR-MOD-06 says *hard-deleted*, and a compliance team told an auditor the
data is gone. **It is the only reading that keeps every internal rule and still misleads
somebody.**

**REVERSAL CONDITION**: if a later chapter needs hard deletion on a third path, *compliance
path* has stopped being a category and the decision is re-opened.

## R2 — FR-MED-11's expensive half is the "unless shared" check, and 4.12 already built its index

A sweep needs two directions and they do not cost the same.

**Forward — an expired message's attachments.** Free: `attachments` is a jsonb column on rows
the sweep already has in hand.

**Reverse — is this object still referenced by a message that did NOT expire?** Required,
because FR-MSG-11 has allowed the same `media_id` in two messages since chapter 3.24.

**AND IT IS ALREADY WRITTEN, WHICH THIS SECTION DID NOT KNOW WHEN IT MEASURED.**
`repository.ts` exports `unreferencedMediaIn(db, environmentId, olderThan, limit = 100)` —
chapter 4.15's, tested, environment-scoped, and already in the two-query form for the reason
measured below. The measurement stands and is worth keeping: **it was taken independently and
agrees**, which is the only way anyone found out the function was there. Analysis pass 7 found
it by following a stray `docs/12 row 22` citation out of a migration comment, six passes in.

```
set-wise semi-join over media_objects     94,132 buffers · 79.6 ms · 4,930 rows
one object, operand bound                    883 buffers · 27.2 ms
```

**106×, and it is 4.12's lesson exactly**: `messages_attachments_gin` (`jsonb_path_ops`) already
exists, and a containment operand the planner cannot see before the join does not reach it.
That chapter measured `Rows Removed by Join Filter: 1017` with the index present and idle.
**The check runs per object with a bound operand**, which also makes it batchable.

## R3 — There is no scheduler, and this is the fourth clause to say so

Zero `schedule:` triggers in `ci.yml`, no cron, no timer, nothing. ADR-28 declined to build one
for FR-ANL-06's daily reconciliation; FR-MOD-03's retention year and DR-17 are bounded by the
same absence.

**What is different here, and it is worth one paragraph rather than a shrug**: the other three
are *reporting* obligations whose absence costs accuracy. This one is a **compliance promise** —
a customer told an auditor that chat older than ninety days does not exist. An unenforced
reporting bound is a gap; an unenforced deletion bound is a statement that is false.

So the sweep ships as a **runnable command with no timer**, the clause is recorded against the
same precedent, and the chapter says plainly which half is built. What it must not do is
publish a `retention_edge` or any field implying a bound the platform does not enforce —
chapter 4.18 refused exactly that for the audit log and the request log publishes one only
because its table has a real TTL.

## R4 — The policy column exists, is empty, and has no reader or writer

`environments.retention_days integer`, in `schema.ts` since chapter 2.1 with its own comment:
*"DECLARED IN 2.1 AND STILL EMPTY. Named in SRS §6.1's Environment entity and SAD §338, read by
nothing in seventeen chapters."*

```
environments                33,051
with retention_days set          0
occurrences outside schema.ts    0        no reader, no writer, no route
```

**DECISION: use it.** A second column would be a parallel policy, which is the shape FR-MED-08's
note refuses for authorisation and the same argument holds here. The surface that writes it is
the plan's question; the column is not.

## R5 — The lane cannot exercise the clause at any of its four settings

```
oldest message            2026-09-14        19 days at planning, 20 on 2026-10-04
                                            and THIRTY on 2026-10-14
older than  30 days       0
older than  90 days       0
older than 365 days       0
```

FR-MOD-06's shortest policy is 30 days. **Every scenario needs a backdated fixture**, and the
figure a reader would most want — how much a sweep deletes on real traffic — cannot be measured
on this lane at all. The chapter publishes that rather than implying otherwise.

**And a backdated fixture has a known failure mode here**: chapter 4.13's sweep fixture stepped
by a second and piled 3,235 rows on one instant, which turned twelve tests red in milliseconds
and which CI never sees because a fresh database has no pile.

## R6 — An audit entry outlives its target, and nothing refuses that

```
FKs from audit_log to messages          (none)
audit rows whose target is a message     1,435
```

So destroying a message leaves audit entries naming an id that no longer resolves, and the
database will not object. **That is correct and should be stated rather than discovered**: an
audit entry records that an action happened, not the thing it happened to, and FR-MOD-03's log
is append-only — deleting entries to match would be the larger wrong. The chapter names the
consequence: an audit target id is not a foreign key and a reader following one may find
nothing.

## R7 — What a sweep in this platform already looks like

Chapter 4.13's media sweep is the precedent and it carries two findings this chapter inherits.
**It read one page and the head never moved** — an object nobody uploaded to stayed `pending`
for ever — so it pages, keyset on `created_at`. And **its idempotence is a compare-and-set**:
`UPDATE … WHERE state = 'pending'` is constitution IV's single writer without a lease, a
heartbeat or a reaper.

For expiry the equivalent is that the predicate is self-clearing: a message the sweep destroyed
cannot match the next pass, so re-running is safe by construction rather than by bookkeeping.
**That claim needs a test, not a sentence** — chapter 4.18's `deleteUser` returned `true` for
*a row existed* where the plan read it as *something changed*, and the lesson was that reading a
return type is not reading what it means.
