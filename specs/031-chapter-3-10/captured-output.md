# Chapter 3.10 — captured output

Printed, not described. Chapter 3.8's header bug was found by dumping a whole
response and not by any of the eighteen tests asserting on its fields, so a claim
about behaviour here is quoted from a run.

Scanned for credentials — the patterns are at the end.

---

## The query this chapter refused (T004a)

```text
->  Bitmap Heap Scan on messages m
      Recheck Cond: (c.id = channel_id)
      Filter: (created_at >= date_trunc('month'::text, (now() AT TIME ZONE 'utc'::text)))
      Heap Blocks: exact=11
Execution Time: 0.266 ms
```

The month predicate is a `Filter`, not an Index Cond: every message the
environment has ever sent is read off the heap and then discarded if it belongs to
another month. 507 rows today, out of 198,690 in the table.

**Research R1 recorded 1.189ms for this and it now measures 0.266ms.** The first
was a cold execution of a query the planner had never seen; neither is wrong and
neither is the argument, which is the `Filter` line.

## The flush test, and proof it can fail (T016a, T016b)

The property FR-002 asks for, with the counter store emptied between two reads:

```text
Test Files  2 passed (2)
      Tests  24 passed (24)
```

Rebuilt chapter 3.8's way for one run — the count's home moved to Redis, written
by `sendMessage` and read back on the way out:

```text
× reports identical figures across a FLUSHALL      102ms
Tests  1 failed | 6 passed (7)
```

One failed and six did not. Every other assertion in the file passes under both
designs, because both count correctly until something clears the store.

Reverted with `git checkout --`; `md5sum` matched the commit made beforehand.

## What the send path gained (T018)

```text
Insert on usage_periods
  Conflict Resolution: UPDATE
  Conflict Arbiter Indexes: usage_periods_pkey
  Buffers: shared hit=25
Execution Time: 0.357 ms

Insert on usage_active_users
  Conflict Resolution: NOTHING
  Buffers: shared hit=60
  Trigger for constraint usage_active_users_environment_id_fkey: time=0.687
  Trigger for constraint usage_active_users_user_id_fkey:        time=0.311
Execution Time: 1.304 ms
```

No `Seq Scan` in either plan. The honest line is the second one's: two foreign-key
constraint triggers cost 0.998ms of its 1.304ms — more than the insert — and that
is paid on every *attributed* send.

## What a configured quota costs (T033)

Same environment, same channels, same user, configuration toggled between two
identical loops, phases instrumented, 32 concurrent sends across 32 channels:

```text
unconfigured           1.77ms per send    assertWithinQuota = 1.246ms
configured             2.33ms per send    assertWithinQuota = 1.586ms
back to unconfigured   1.77ms per send    assertWithinQuota = 1.121ms
```

0.56ms per send. The crossing block measures 0.000ms, because `thresholdsCrossed`
is arithmetic on two numbers the transaction already holds and answers "nothing"
for almost every send.

**Four attempts to get this number.** An uncontrolled benchmark — one environment
per case, fixed order — reported 273%, 341%, 303% and 411%, and three separate
causes were inferred and acted on before the benchmark itself turned out to be
the problem.

## The lock that could not come back

```text
ERROR:  FOR UPDATE cannot be applied to the nullable side of an outer join
```

Once the caps and the usage are one joined read, Postgres will not lock it. The
overshoot is bounded by the number of sends in flight, which is what the
specification asked for.

## At-most-once is the constraint, not the code (T028a)

Two identical crossings inserted directly, bypassing `recordCrossings` entirely:

```text
NOTICE:  refused by quota_notifications_once_per_threshold
NOTICE:  rows for that threshold: 1
```

## The guard's prediction, on a freshly baited database (T034)

```text
exit=0        255 tests
guard refusals during the run: 15

15  sentinel row public.webhook_endpoints
---
10  planted by services/dispatcher/src/dispatcher.itest.ts
 3  planted by packages/test-harness/src/guard.itest.ts
 2  planted by __shared__/sweep-bait
```

Not one names `usage_periods`, `usage_active_users` or `quota_notifications`.
`exempt.ts` and `eslint.config.mjs` are byte-identical to
`feature-030-global-operation-guard`.

On a used database the same lane gives 3, because the sentinel endpoints have
already been disabled by earlier sweeps. **The count moves with the database's
history, not with the tree**, which is why this task specifies a fresh one.

## Coverage, and the two gaps the first run found (T035)

```text
first run   88.81 | 82.32 | 88.02 | 90.27     below this task's floor
after       89.51 | 82.73 | 88.94 | 90.92     exit=0, every ratchet green
baseline    89.08 | 82.35 | 89.25 | 90.58
```

The lane's own global threshold is 70%, so the first run exited 0 while sitting
under the floor. `period.ts` was at 50% functions because `currentPeriod()` was an
export nothing called; `quota-relay.ts` was at 56.66% statements because no test
entered `start`, `stop` or the `run` loop — the hole chapters 3.3, 3.5 and 3.9 all
have. Four lines of test took it to 96.66.

`repository.ts` holds its 100% functions ratchet: 97.48 | 90.17 | 100 | 99.38.

## Quickstart V1 to V12 (T037)

```text
V1/V2  api src/quotas                    exit=0
       FLUSHALL issued
       api src/quotas again              exit=0
V3     api src/quotas src/messages       exit=0
V4     gateway                           exit=0
       e2e                               exit=0
V5/V6  mailpit reachable                 exit=0
V7/V8  whole integration lane            exit=0
         guard refusals: 3 | naming a quota table: 0
V9     unit lane                         exit=0
       coverage                          exit=0   532 tests
                                         89.51 | 82.73 | 88.94 | 90.92
V11/12 check:fences                      exit=0
       check:docs                        exit=0
       lint                              exit=0
       build                             exit=0
```

## The size gate (T041)

```text
prose words: 2,548        gate: 2,000 to 4,000
fences:      31
```

The first draft came in at 2,053 and was thin in a way the count could not see —
missing the flush test and the distinct-user argument, both of which are what the
chapter is about.

## The fence chain

```text
check-fence-chain: 173 fenced files replay onto relay-platform across 27 chapters
(27 translated, fences mirrored, 1 retired, plus post-series amendments)
```

From 165 across 26.

## Credential scan (T039)

Patterns searched across this file, `chapter-notes.md`, `research.md`,
`baseline.txt`, `quickstart.md`, and both locales of the chapter page. The patterns
are recorded rather than the verdict, because a verdict cannot be re-checked and a
pattern can.

```text
rk_svc_[A-Za-z0-9_]{8,}              internal service credential
rk_(live|test)_[A-Za-z0-9]{8,}       tenant api key
whsec_[A-Za-z0-9+/=]{16,}            webhook signing secret
RELAY_INTERNAL_CREDENTIAL=\S+        the env var carrying a value
RELAY_WEBHOOK_SECRET_KEY=\S+         the encryption key carrying a value
[A-Za-z0-9+/]{40,}={0,2}             any base64-shaped blob, 40 chars or longer
-----BEGIN [A-Z ]*PRIVATE KEY        pem private key
postgres://[^:]+:[^@]+@              a database url carrying a password
Bearer [A-Za-z0-9._-]{20,}           a bearer token
eyJ[A-Za-z0-9_-]{10,}                a jwt
sentinel-not-a-secret                the harness's own literal
```

Results below.

```text
high-signal patterns          2 hits, both the pattern list in this file quoting itself
base64-shaped blobs, 40+      2 hits, both git commit SHAs in baseline.txt
postgres urls with password   1 hit, the pattern list quoting itself
sentinel-not-a-secret         1 hit, the pattern list quoting itself
```

Two further searches for the literal values this session's environment actually
held — the compose stack's `RELAY_WEBHOOK_SECRET_KEY` and its
`RELAY_INTERNAL_CREDENTIAL` — across every document in this feature and both
locales of the chapter page. **No hits.**

Every hit above is this section describing its own search. `sentinel-not-a-secret`
lives only in `packages/test-harness/src/sentinel.ts`, which this chapter does not
fence, and the string says what it is by design.
