# Feature 030 — captured output

Printed, not described. Chapter 3.8's header bug was found by dumping a whole
response and not by any of the eighteen tests asserting on its fields, so the rule
this feature inherited is that a claim about behaviour is quoted from a run.

Every transcript below is from this feature's own runs, against the compose
Postgres on port 15432. Scanned for credentials — see the last section.

---

## The trigger refuses, and names the culprit (V2)

The guard's own lane, `packages/test-harness/src/guard.itest.ts`, eight tests.
Four are refusals; four are the paths where the guard must do nothing, which is
where both of its implementation bugs lived.

```text
global-operation guard: this statement modified sentinel row public.webhook_endpoints (id 6ba2cc2e-6280-4686-acae-2922fcb73530), which belongs to no test — the bait planted by services/api/src/notifications/notifications.itest.ts
```

The message is the contract in `contracts/guard.md`: the prefix, the schema and
table, the row id, the clause `which belongs to no test`, and whose bait it was.
No suggested fix — the right scoped alternative depends on what the test meant,
and a guess printed as advice is worse than silence.

## Instance 6 fails alone (V3)

`sweepDisabledEndpoints(db, 100)` reintroduced into `notifications.itest.ts`'s
`disable()` helper, that file run by itself against a freshly migrated database.

```text
     × sends what the organisation needs, and Mailpit confirms the contents (FR-WHK-07) 363ms
     × sets delivered_at only AFTER the send returns (FR-WHK-07) 201ms
     × does not send a delivered row twice (FR-WHK-07) 196ms
     × sends twice for an endpoint disabled, re-enabled and disabled again 207ms
     × handles an organisation nobody can be written to (FR-WHK-07) 202ms
     × sends to EVERY member with an address, one message each 193ms
     × does not take anything else down with it when the mail server is gone (FR-WHK-05) 101ms
     × does not let ONE undeliverable row block every row behind it 166ms
     × drains chapter 3.6's backlog with NO SPECIAL HANDLING (FR-WHK-07) 177ms
 Test Files  1 failed (1)
      Tests  9 failed (9)
```

Nine of nine, because every one goes through `disable()`. Reverted with
`git checkout --`; `md5sum` matches the committed file.

**The first attempt at this step passed**, nine tests of nine, because
`notifications.itest.ts` is on the exemption list — it is on that list *because of
instance 6*. The exemption now names tables rather than files (research R41).

## Instances 1, 4 and 5 fail alone (V4)

One reintroduction at a time, each on a fresh database, each reverted and
`md5sum`-checked.

```text
--- instance 1 ---
 FAIL  src/webhooks/deliveries.itest.ts > the failure run > invariant 12: the SWEEP disables the quiet endpoint no outcome ever revisits
AssertionError: expected true to be false // Object.is equality
      Tests  1 failed | 48 passed (49)
--- instance 4 ---
 FAIL  src/tenancy/signup.itest.ts > signup > exposes provisioning nowhere but the signup path (invariant 7, spec FR-011)
      Tests  1 failed | 7 passed (8)
--- instance 5 ---
 FAIL  src/dispatcher.itest.ts > the dispatcher > invariant 7: delivers an event the endpoint subscribes to
AssertionError: expected 0 to be greater than 0
 FAIL  src/dispatcher.itest.ts > the dispatcher > invariant 16: the delivered body is 3.3's envelope and carries the event id
      Tests  10 failed | 6 passed (16)
```

Instance 5's message is the one chapter 3.8's baseline recorded, character for
character, which is the strongest available evidence that the bait reproduces the
original conditions rather than merely breaking something.

**Instances 2 and 3 are excluded, with reasons rather than silence.** Instance 2's
content is *this suite leaves leftovers that starve a later one*; a cause whose
only symptom appears in another file has no alone-failure to produce, and the bait
makes it observable as instance 5 instead. Instance 3 rides the JetStream stream,
which a database seeder does not reach. SC-001 was amended from six to four.

## The exemption permits the write, and only the table it names (V5)

The bug this test exists for: with `RETURN OLD` on both paths, an exempt suite
swept seventeen sentinel endpoints, disabled none of them, and found all seventeen
again on the next pass.

```text
FAIL src/webhooks/deliveries.itest.ts > logs nothing when there is nothing to disable
AssertionError: expected 17 to be +0
```

Seventeen is the number of files in the api lane, each having planted one
sentinel. Nothing was raised and nothing was logged: the guard was wrong on the
path where it was supposed to do nothing.

With the bug deliberately restored, exactly one of the guard lane's eight tests
fails — the one that reads the row back after an exempt update. Every refusal-side
test passes, which is why no amount of testing the refusal would have found it.

## The bait survives a lane run (V6)

Counts before and after two further lane runs against the same database:

```text
before: 19|18|3600|3616      sentinels|endpoints|deliveries|notifications
run 1:  19|18|3600|3614
run 2:  19|18|3600|3614
```

Stable. One sentinel per test file, not one per run; the two-row settle on the
first run is `plant()` normalising rows a previous state had left. Eighteen
endpoints against nineteen sentinels because `guard.itest.ts` deletes its own —
that is the test asserting deletion works.

*(Counts taken before the endpoint bait was resized to `BAIT_ROWS`; the property
being checked is stability across runs, not the sizes.)*

## The call site refuses (V7)

```text
services/api/src/messages/history.itest.ts
  1:10  error  'outboxDepth' import from '../db/repository' is restricted. This
        function operates across every environment in the database, and an
        integration test shares that database with every other suite. …
✖ 1 problem (1 error, 0 warnings)

services/api/src/db/repository.itest.ts
  6:41  error  'outboxDepth' import from './repository' is restricted. …
✖ 1 problem (1 error, 0 warnings)
```

Two spellings, two entries: `no-restricted-imports` matches the specifier as
written, and the two suites in `src/db` reach the file as `./repository`. The same
import added to `outbox/outbox.itest.ts`, which is on the ignores list, exits 0.

## Nothing was lost (V8)

```text
  unit lane          11 tasks, 306 tests passed              3.781s
  integration lane   10 tasks, 231 tests passed           3m10.218s
  coverage lane      53 files, 472 tests passed           4m 5.770s

  coverage   89.08 statements | 82.35 branches | 89.25 functions | 90.58 lines
  repository.ts   97.27 | 90.90 | 100 | 99.24     (ratchet 97 | 90 | 100 | 99)
```

Against T002's baseline — 223 tests in 3m13.852s — the lane carries 8 more tests
and finishes 3.6 seconds sooner. SC-004 asked for growth under ten seconds.

`repository.ts` functions returned to the 100 its ratchet has demanded since
chapter 3.5 and had not met since before this feature began: the uncovered
function was `drainDisableNotifications`'s `onError` default, which no caller has
ever used (research R48).

