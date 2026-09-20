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

**AND THIS WIDENING TURNS TWO SHIPPED TESTS RED, MEASURED AT ANALYSIS PASS 3.** The constraint
was applied to the live database exactly as above and chapter 4.11's suite was run:
**2 failed, 15 passed.** `attach.itest.ts:288` is titled *"cannot be given a `ready` object to
attach, because the database refuses one (SC-006)"* and asserts the constraint's own name in the
refusal text; its sibling at :307 uses `'rejected'` as its example of *"a state that is neither"*.
Both now insert successfully and both get `''`.

**Neither is a defect.** They were 4.11's published evidence that the second arm of
`state IN ('pending','ready')` could not occur, and this chapter is what makes it occur. The
first becomes an assertion that a `ready` object **is** attachable; the second keeps its title
and changes its example to a value genuinely outside the set — **`'scanning'`**, which §2 below
refuses to make a state, so the two decisions hold each other up.

**AND 0018 CANNOT BE ROLLED BACK ONCE A TERMINAL ROW EXISTS.** Found by trying: restoring the
narrow constraint answers

    ERROR:  check constraint "media_objects_state_check" of relation "media_objects"
            is violated by some row

and the `ready` and `rejected` rows have to be deleted first. ADR-16 makes migrations
forward-only, so this is a property rather than a fault — and it is one a developer testing
locally meets within minutes, which is why it is written here rather than discovered there.

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

**THE SIZE COMPARISON IS EXACT, AND THE QUOTA IS WHY.** FR-MED-03 says *"contradict their
declaration"*; the spec's acceptance scenario said *"materially larger"* and gave no tolerance
until analysis pass 4 asked what the number was. The quota sums `declared_bytes` (SRS 1.17), so
under any tolerance a client that under-declares is billed for the declaration and stores the
difference. **Exact makes the quota correct by construction**: for every `ready` object,
`verified_bytes = declared_bytes`, and the column pair is a record rather than a discrepancy.

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

    pending    scanned, verified, probed              ready       kept         probe columns set
    pending    scanner reports a signature            rejected    DELETED      rejected_reason
                                                                               = scan_failed
    pending    size or type contradicts declaration   rejected    DELETED      verified_* set,
                                                                               rejected_reason
                                                                               = declaration_mismatch
    pending    store or scanner unreachable           pending     kept         nothing

**THE SCAN IS FIRST, AND A TEST THAT COULD NOT BE WRITTEN IS WHY** (`research.md` R5a). The first
version of this table checked the declaration first, which is the cheaper refusal and the
obvious order. It makes SC-003 impossible: EICAR is a 68-byte text file, `ALLOWED_TYPES` has no
text type, so the object is refused as `declaration_mismatch` before the scanner is asked — and
ClamAV's signature matches the FILE rather than a substring, so it cannot be smuggled inside a
valid PNG either. Measured: EICAR plus two hundred trailing spaces is already `OK`.

**FR-MED-04's own word settles it.** *"Every uploaded object shall be virus-scanned"*, and
declaration-first leaves some uploaded objects unscanned — the mis-declared ones, which are the
ones worth scanning.

**AND THE FULL ORDER IS SCAN, THEN SIZE, THEN TYPE — WHICH TOOK FIVE ANALYSIS PASSES TO STATE.**
Each fix was pairwise: pass 1 moved the size comparison onto the sweep's own `HEAD`, and pass 1's
EICAR finding put the scan ahead of the *type* check. Composed, they leave the size verdict
**knowable before the scan runs**, and nothing said whether a size mismatch should skip it.

**It should not, and the argument is R5a's own applied twice.** *"The mis-declared ones are the
ones worth scanning"* is at least as true of an object declaring one byte and holding five
megabytes as of one whose type is wrong. Using the clause's word to order the type check and
ignoring it for the size check would be reading *"every"* selectively.

**The cost is bounded and it is bounded by something that already exists.** Scanning an object
that will be rejected on size means streaming up to `KIND_CAPS`'s 100 MB for nothing — and a
caller who wants the platform to stream 100 MB can upload a valid 100 MB video, so the worst case
is the cap either way. **Knowing the size early and refusing late are different things**: the
`HEAD` still saves the round trip, it just does not short-circuit.

**What is given up**: every object with bytes is streamed once, including the ones a cheaper
order would have refused for free.

**And `scan_failed` wins when both fail.** An object can now be both infected and a lie; the
scan is the more serious fact about the caller and the one an operator reading `rejected_reason`
needs.

**The fourth is the one that needs saying.** FR-009 forbids a transient failure from producing
either terminal state, so *nothing happens* is a legitimate outcome and the object comes back on
the next sweep. A worker that marked an object `rejected` because the scanner was down would be
deleting a customer's photo to record an outage.

**AND A REJECTION DELETES THE BYTES BUT NOT THE ROW.** FR-MED-04: *"retaining only the audit
record."* The row is the audit record — there is no separate table, and inventing one here would
be a second place to look for the same fact. FR-MOD-03's audit log is movement VII's and it is a
different thing: an immutable log of *moderator actions*, not of the platform's own verdicts.

**AND THE TABLE BEING DECLINED HAS A NAME, WHICH THIS PARAGRAPH DID NOT KNOW.** `docs/04-srs.md`
line 827 specifies `media_events` — *"Storage metering, scan-pipeline health (FR-MED-12)"* — with
`event` in `uploaded/ready/rejected/deleted`, `kind`, `bytes` and `processing_ms`, and **DR-17**
builds stored-bytes-per-tenant by *"summing `media_events` deltas (uploaded/deleted), reconciled
weekly against an object-storage inventory"*. It has no `.sql` file and two live source files
quote DR-17 about it.

**Declined here, and the reason is arithmetic rather than scope.** This chapter owns `ready` and
`rejected`; `uploaded` is 4.10's slot and `deleted` is FR-MED-10's sweep. A producer built now
would fill the table with **exactly the two values DR-17's sum does not read** — a table holding
only the rows its own clause ignores, which is chapter 4.6's finding rebuilt deliberately. The
row above stays the audit record, `gaps.md` carries the arithmetic, and FR-MED-12's chapter
inherits a measurement instead of a question.

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

**AND THE `HEAD` IS ALSO WHERE SC-006's CLOCK STARTS, WHICH NOTHING NAMED.** *"Time from upload
to `ready`"* has a start instant the platform never observes: under the sweep, nobody tells it
when the PUT finished. The store does, on this same round trip — measured at analysis pass 5:

    last-modified          Sun, 20 Sep 2026 17:02:53 GMT
    content-length         1
    etag                   "9dd4e461268c8034f5c8564e155c67a6"

**At one-second resolution**, because an HTTP date has no sub-second field. **That is a cost of
`research.md` R1's decision and it was not recorded as one**: the client notice the sweep replaced
would have given the platform an exact instant. SC-006 is measurable, from a header no artifact
named until pass 5, and its figure carries a ±1 s quantisation that has to be published beside it
rather than rounded away.

**AND THE `HEAD` ANSWERS HALF OF FR-MED-03 ON ITS OWN.** Measured at analysis pass 1: a presigned
PUT of twelve MP4 bytes sent with `content-type: image/png` comes back from `HEAD` as
`content-type: image/png` — **the client's claim, echoed** — and `content-length: 12`, which is
**the store's own count**. So the size comparison needs no bytes at all, and only the type
comparison needs the object. A worker that read `Content-Type` off the response would have
verified the client's claim twice and called the second one a verification.

**Measured before this document was written**: 1.412 ms per `HEAD`, p50 1.094, p95 1.714, over
200 rows — 34 with bytes and 166 without. The lane's whole 3,005-row backlog is **4.2 seconds**
serial. That figure is what settled `research.md` R1 against the specification's assumption.

**AN INDEX IS NEEDED, AND THE FIRST VERSION OF THIS PARAGRAPH REASONED ABOUT THE WRONG HALF.**
It said no index was needed because *"the predicate is `state = 'pending'` and today every row
matches"* — true about the predicate, and the query also carries `ORDER BY created_at LIMIT 50`.
Measured at analysis pass 2:

    no index                        Seq Scan 3,028 rows + top-N heapsort   90 buffers   2.370 ms
    partial (created_at)            Index Scan, stopping at 50              4 buffers   0.029 ms
      WHERE state = 'pending'

    88 kB against a 736 kB table — 11.96%

**IT IS `0019_media_pending_age.sql`, NOT AN EDIT TO 0018.** `schema_migrations` is
`(version, applied_at)` with **no checksum**, so the Postgres runner skips an edited applied file
in silence — where `analytics/apply.mjs` keys on `(filename, checksum)` and refuses one. The two
runners in this platform give different guarantees about the same mistake, and the Postgres side
is the one where a developer's lane and CI end up with different schemas.

**Chapter 4.1's sentence, at small scale**: *the join is 140 ms of a 698 ms plan and the sort is
656.* The cost is the ordering. And the ratio runs the opposite way from 4.12's GIN — 11.96%
today because every row is `pending`, shrinking to the size of the backlog as objects resolve,
where a whole-column index stays the size of the table.

**`ORDER BY created_at` rather than newest-first**, so an object that keeps failing does not
starve the queue behind it — and so the 24-hour reap boundary (FR-MED-10) is approached from the
right end.

## 5a. The arm chapter 4.11 left for this one

`assertAttachableMedia` admits `state IN ('pending', 'ready')`, and `repository.ts:5119` says why
in a note addressed to this chapter by name:

> *"`'ready'` is unreachable today and the predicate says it anyway: the clause names both, and a
> predicate that named one would have to be found and widened by whoever builds the scanner."*

**Nothing needs widening — 4.11 wrote both arms — and three things follow anyway.**

**The second arm becomes reachable for the first time**, so the behaviour it produces is now
observable and has to be asserted: a `ready` object is still attachable, and a `rejected` one is
not. That second half is FR-MED-06's refusal arriving for free, because `rejected` is outside the
predicate's set.

**The comment goes stale the moment 0018 applies.** *"Unreachable today"* stops being true, and a
comment describing behaviour no code performs is the class this movement has found in `store.ts`,
in `docs/07` §6, in `docs/12` row 11 and in a test's deadline. Correcting it costs a fence hunk
in a file carrying fifty of them.

**And 4.11's per-arm probe result changes.** That comment records deleting each arm and re-running
— *"the three SQL clauses: no JavaScript branch at all"* — measured when only one arm could
occur. With `ready` reachable, deleting it can turn a test red that previously could not, so the
probe is re-run here rather than inherited.

## 6. What the worker never touches

Postgres. ADR-04, and `research.md` R8 found the seam already built six times: the api serves
six `internal/` controllers and `services/dispatcher/src/api-client.ts:67` is the one client
that reaches them. The worker reads its batch and writes its verdict through a route on that
seam.

**WITH ITS OWN CREDENTIAL, AND THE FIRST DRAFT OF THIS SECTION SAID OTHERWISE.**
`authenticate.middleware.ts:63` maps `RELAY_INTERNAL_CREDENTIAL` to the literal `"dispatcher"`,
and `Principal.service` is what every structured log line and every request-log row reports. A
worker on the dispatcher's variable is a fifth service that logs as the fourth — in the audit
trail of the only component that reads customer bytes. `RELAY_INTERNAL_CREDENTIAL_WORKER` is a
third entry in `PLATFORM_SERVICES`.

**AND WHAT MAKES THAT ENTRY MANDATORY IS THE GUARD, NOT THE UNION.** This paragraph first said
the widening *"stops every route that must now decide about it from compiling"*, copying the
middleware's own comment. Measured at analysis pass 2: a third entry, `tsc --noEmit`, **exit 0**.
Nothing breaks, because `PlatformService` only ever appears as `readonly PlatformService[]`. What
is mandatory is `@Accepts({ platform: ["media-worker"] })` — `credential.guard.ts:36` refuses the
bare `@Accepts("platform")`, and `"media-worker"` is unwriteable until the list holds it.

`RELAY_INTERNAL_CREDENTIAL` is still worth naming here for a different reason — chapter 4.9
found its absence silently skipping three isolation attacks at 0 ms apiece.

## 7. The second writer, named because constitution IV names it

`media_objects.state` gains a second writer. The api writes `pending` at slot time; the worker
writes `ready` and `rejected`.

**The argument is that the transitions are disjoint**: nothing but the slot route writes
`pending`, and nothing but the worker leaves it. The api never re-writes a state it did not
create, and the worker never creates a row.

**What that does not cover is two workers**, which is plan open question 6. One worker is the
current reality; the design that survives a second one is a claim this chapter should either
make and test or decline and record. Declining it is legitimate — *a design in which a case
cannot arise beats a branch that handles it* — but only if something makes the case not arise,
and "we only run one" is a deployment fact rather than a design.
