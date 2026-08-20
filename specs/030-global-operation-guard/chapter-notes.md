# Feature 030 — notes

Written from what happened, which is not what the plan said would happen.

## What shipped

Three defences, one per shape of the fault.

- **A Postgres trigger.** `packages/test-harness/src/sentinel.sql` installs
  `__sentinel_guard()` on the five tables carrying `environment_id`. A statement
  that modifies a sentinel row from a connection without the matching exemption
  raises inside its own transaction, naming the schema, the table, the row id and
  the test file that planted it.
- **Bait.** Each test file plants its own sentinel environment: `BAIT_ROWS`
  endpoints with an open failure run past the cutoff, `BAIT_ROWS` unpublished
  outbox rows, `BAIT_ROWS` undelivered notifications, and `BAIT_ROWS` deliveries
  that are deliberately not due. `BAIT_ROWS` is twice the largest batch any product
  reader takes.
- **The call site.** `sweepDisabledEndpoints` and `drainDisableNotifications` lost
  their last defaults, and an eslint rule restricts the six global-admin functions
  from `*.itest.ts` outside a list of six files that drive a global drain on
  purpose.

## Did the design survive?

The trigger did. Research replaced the spec's before/after checksum with it before
a line was written, on the argument that only a database-side check can raise
inside the transaction that performed the mutation, and that argument held.
Nothing in implementation made the trigger look like the wrong choice.

The trigger's *implementation* did not survive first contact, twice, and both
times on the path where it was supposed to do nothing:

- `RETURN OLD` on a `BEFORE UPDATE` trigger does not permit the update, it
  replaces it with a write of the old values. An exempt suite swept seventeen
  sentinel endpoints, disabled none of them, and found all seventeen again on the
  next pass. Research R37's verification had reported `EXEMPT allowed: 1 row(s)`,
  which was true and proved nothing (R38).
- The exemption was per file, and the fault the feature was built for lives in a
  file on the exemption list — `notifications.itest.ts` is exempt because it
  drives the notification relay, which is global over
  `webhook_disable_notifications` and nothing else. Reintroduced under a
  file-wide pass, instance 6 passed nine tests out of nine. The exemption now
  names tables (R41).

Both were found by running the lane, not by reading. Eight analysis passes read
these documents and neither appeared, because neither is visible in a design.

## What the plan did not predict

**The bait's cost is the work the bait creates.** The plan sized bait by what
would defeat a batch and never asked what draining it costs. Three shapes were
measured before one worked: due deliveries on an enabled endpoint failed ten of
the dispatcher suite's sixteen tests; on a disabled endpoint, two; not due at all,
none. The dispatcher waits eight seconds for its own row to come out of a shared
FIFO broker, and two hundred jobs ahead of it is eight seconds (R44, R47).

It happened a third time, and the third time turned three incidents into a rule.
`drainDisableNotifications` claims on `delivered_at IS NULL` and then looks up an
organisation's recipients per row; the sentinel's organisation has no addressable
member, so each bait row took the cheapest branch there is, and 3,400 cheapest
branches is a little under five seconds against a test with vitest's five-second
default. Run 1 of the twenty-run battery caught it, after three full lanes had
passed on the same tree (R49).

> **Bait may be claimable only where draining it is database work.**

A sweep and a publish qualify, and the two instances the seeder actually caught —
1 and 7 — were caught by exactly those two baits. A delivery costs an api
round-trip and an HTTP send; a notification costs a recipient lookup and a mark.
Both now sit in the table as rows a global count would see, and outside every
claim window.

The consequence is a boundary the spec did not have: the seeder seeds a database,
so the two faults that ride a broker are outside it, and so are the two drains that
do I/O per row. SC-001 was amended from six instances to four, with the two
exclusions named and a different mechanism given for each.

**A defence's cost lands on somebody else's lane.** The trigger is database state,
so every lane pointed at that database meets it whether or not it installed it —
anticipated, and handled by T016a. Bait is database state too, which was *not*
anticipated: removing bait from the dispatcher lane did not stop the dispatcher
suite meeting it in the coverage lane, which shares the database with the api
lane.

**Nine suites were running four background relays.** Research R13 measured the
exposure as nil on the strength of the four suites that spawn an api child and set
the flags in the child's environment. It did not look at the nine that import
`AppModule` in process, where every relay defaults to on. A relay catches and logs
its own errors, so the guard's refusal inside one is a log line and a green lane —
the hole R13 identified, in nine more places than R13 counted (R39).

## What it found

Four more instances of the fault, none of them planted:

| where | shape |
|---|---|
| `outbox.itest.ts` invariant 7 | drive loop bounded in batches, work bounded by the table |
| `outbox.itest.ts` invariant 8 | the same, at `batchSize: 7` — a budget of 140 rows |
| `outbox.itest.ts` invariant 7 | a deduplication assertion over every row the global relay moved |
| `consumer.itest.ts` | two runtimes with no subject filter, forty lines from where 3.7 fixed exactly that |

The last one is the one worth keeping. Chapter 3.7 fixed the identical fault in the
test immediately above it and did not look down. It has never failed — a fixed
budget against a growing shared resource passes until the resource outgrows the
budget — so nothing but a deliberate grep for the class was ever going to find it.
That grep is now a task.

And one thing that was not an instance: `repository.ts` had been failing its own
coverage ratchet since before this feature started, on an `onError` default that no
caller has ever used. `baseline.txt` had said every per-file ratchet passed, which
was inferred from the overall figures rather than read off the run — this feature's
own recurring failure, a summary that reads as a measurement (R48).

## What went badly

The eight analysis passes were worth their cost and are not the story here. What
cost real time was the reverse: **three separate occasions of reasoning where a
measurement was cheap.** The duplicate-publish failure, the dispatcher's eight
seconds, and the coverage ratchet each took several rounds of plausible theory
before the thing was simply run and printed. Each printed answer was different
from the theory.

The `git checkout --` hazard chapter 3.9 recorded did not recur, because T017a's
rule — commit before every reintroduction, not just before the battery — was
followed. Five reintroductions, five reverts, five matching `md5sum`s.

## The number that is not in yet

SC-008 — that the count of instances does not increase in the chapter that follows
— is verifiable only later. It is the outcome the work exists for, and every one of
the eleven occurrences was discovered exactly that way.
