# Data model — feature 059, chapter 4.13

## 1. What changes

One constraint, one column set, and no new table.

`media_objects` is what chapter 4.10 created. This chapter makes its `state` column mean
something and records what the probe found. Nothing else in the schema moves.

## 2. The states, and the constraint that has refused them until now

```sql
-- 0018_media_states.sql
ALTER TABLE media_objects DROP CONSTRAINT media_objects_state_check;
ALTER TABLE media_objects ADD CONSTRAINT media_objects_state_check
  CHECK (state IN ('pending', 'ready', 'rejected'));
```

**Three values and not more.** Chapter 4.10 wrote the one-value version deliberately — *"a CHECK
that accepted them now would be a schema claiming a state nothing can reach"* — and the
constraint's job is unchanged. What changes is the set, and a fourth value is still a write that
fails.

**`scanning` is not a state**, and the temptation is real: a worker that has picked up an object
would like to say so. Two reasons it stays out. It is not in the clause — FR-MED-04 names
`pending → ready` and `pending → rejected`, and FR-MED-07 tells clients about *three* states, so
a fourth would have to be either hidden from them or published in a contract no clause asks for.
And it would be **a lease wearing a state's name**: what a second worker actually needs is to not
pick up an object another worker holds, which is a lock with a timeout and not a value in a
column somebody must remember to clear after a crash. Open question 4 owns that; it is not this.

    3,005 rows on the lane, every one `pending`
      253 of them have bytes in the store — 8.4%
    1,538 are older than 24 hours

## 3. What the probe records

```sql
ALTER TABLE media_objects
  ADD COLUMN width       integer,
  ADD COLUMN height      integer,
  ADD COLUMN duration_ms integer,
  ADD COLUMN verified_bytes bigint,
  ADD COLUMN verified_type  text,
  ADD COLUMN rejected_reason text;
```

**Columns rather than a `jsonb` blob, and the reason is who reads them.** FR-MED-05's thumbnails
need dimensions and FR-MED-12 meters stored bytes; both are later chapters in this movement, and
both want a number they can filter and sum. A blob makes each of those a `->>` and a cast, which
is the shape 4.2 spent a chapter on when `postgresql()` handed it jsonb as `Nullable(String)`.

**Every one is nullable and that is not laziness.** `width`/`height` are null for audio;
`duration_ms` is null for images; all of them are null for an object that has not been verified
and for one that was rejected before the probe ran. **The nullability is the record of which
questions were asked**, which is the same argument 4.10 made for `user_id` and the same one 4.11
then depended on.

**`verified_bytes` and `verified_type` are the facts beside `declared_bytes` and `mime_type`.**
The declaration is what the caller said and 4.10 said so in a comment; this chapter produces the
first thing in the platform that knows better. Keeping both is what makes FR-MED-03's refusal
auditable after the bytes are gone — a rejected object's row is all that survives it.

**`rejected_reason` is a string and it has a closed set.** `declaration_mismatch` and
`scan_failed`, which FR-005 requires to be distinguishable, and which SC-002's and SC-003's
tests read. A CHECK on it would be a fourth thing to widen every time a reason arrives; the
closed set lives in the protocol package where the reader can see it.

## 4. The transitions, and there are four outcomes for two states

    from       event                                  to          bytes        row

    pending    verified, scanned, probed              ready       kept         probe columns set
    pending    size or type contradicts declaration   rejected    DELETED      verified_* set,
                                                                               rejected_reason
    pending    scanner reports a signature            rejected    DELETED      rejected_reason
    pending    store or scanner unreachable           pending     kept         nothing

**The fourth is the one that needs saying.** FR-009 forbids a transient failure from producing
either terminal state, so *nothing happens* is a legitimate outcome and the object comes back on
the next sweep. A worker that marked an object `rejected` because the scanner was down would be
deleting a customer's photo to record an outage.

**AND A REJECTION DELETES THE BYTES BUT NOT THE ROW.** FR-MED-04: *"retaining only the audit
record."* The row is the audit record — there is no separate table, and inventing one here would
be a second place to look for the same fact. FR-MOD-03's audit log is movement VII's and it is a
different thing: an immutable log of *moderator actions*, not of the platform's own verdicts.

**AND THE QUOTA MOVES WHEN THE BYTES DO.** SRS 1.17 made committed bytes a **sum over the media
rows** rather than a counter, precisely so a delete needs no subtraction. A rejected object's
`declared_bytes` must stop counting — which means either the row is excluded from the sum by
state, or the column is zeroed. **Excluded by state**, because zeroing destroys the fact that
somebody once declared that many bytes, and FR-MED-03's whole subject is a declaration that was
wrong.

## 5. Finding the work

```sql
SELECT id, object_key, mime_type, declared_bytes
  FROM media_objects
 WHERE state = 'pending'
 ORDER BY created_at
 LIMIT :batch
```

then one signed `HEAD` per row against the store.

**Measured before this document was written**: 1.412 ms per `HEAD`, p50 1.094, p95 1.714, over
200 rows — 34 with bytes and 166 without. The lane's whole 3,005-row backlog is **4.2 seconds**
serial. That figure is what settled `research.md` R1 against the specification's assumption.

**No index is needed and that is checked rather than assumed.** The predicate is
`state = 'pending'` and today every row matches, so an index on it would select the whole table
— the classic case where the planner reads the heap anyway. It becomes worth measuring when
`ready` dominates, which is a later chapter's problem and should be measured then rather than
guessed now. Chapter 4.12 published the general form of this: *the query has to be written so
the planner can use the index before any storage ratio means anything.*

**`ORDER BY created_at` rather than newest-first**, so an object that keeps failing does not
starve the queue behind it — and so the 24-hour reap boundary (FR-MED-10) is approached from the
right end.

## 6. What the worker never touches

Postgres. ADR-04, and `research.md` R8 found the seam already built six times: the api serves
six `internal/` controllers and `services/dispatcher/src/api-client.ts:67` is the one client
that reaches them. The worker reads its batch and writes its verdict through a route on that
seam, with `RELAY_INTERNAL_CREDENTIAL` — the variable whose absence chapter 4.9 found was
silently skipping three isolation attacks, which is the reason to name it here.

## 7. The second writer, named because constitution IV names it

`media_objects.state` gains a second writer. The api writes `pending` at slot time; the worker
writes `ready` and `rejected`.

**The argument is that the transitions are disjoint**: nothing but the slot route writes
`pending`, and nothing but the worker leaves it. The api never re-writes a state it did not
create, and the worker never creates a row.

**What that does not cover is two workers**, which is plan open question 4. One worker is the
current reality; the design that survives a second one is a claim this chapter should either
make and test or decline and record. Declining it is legitimate — *a design in which a case
cannot arise beats a branch that handles it* — but only if something makes the case not arise,
and "we only run one" is a deployment fact rather than a design.
