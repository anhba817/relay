# Captured output — chapter 3.7

Every transcript the chapter quotes, from a real run.

---

## T007 — the deterministic failure, before the fix

Three tests were added to `services/gateway/src/resume.itest.ts` and run against
chapter 3.6's code. Two fail; the third passes, and that is correct — it guards
behaviour that already works and must survive the change.

```console
$ pnpm --filter @relay/gateway test:integration src/resume.itest.ts
 × suppresses a frame the backfill already delivered, published after the resume
 × still suppresses when two instances publish out of order
 Tests  2 failed | 4 passed (6)

 FAIL  src/resume.itest.ts > resume across a real fabric >
       suppresses a frame the backfill already delivered, published after the resume
AssertionError: expected [ 42, 42 ] to deeply equal [ 42 ]

- Expected
+ Received

  [
    42,
+   42,
  ]
```

`[ 42, 42 ]`. The duplicate, on demand, in four seconds — against a stubbed api and
a real Redis, with no race to wait for and no journey to run. Compare that with how
the defect was found: one failure in six runs of a suite that was red for three
other reasons at the time.

## T014 — the same three tests, after the fix

```console
$ pnpm --filter @relay/gateway test:integration src/resume.itest.ts
 Tests  6 passed (6)
```

Six: the three chapter 2.7 wrote, and the three this chapter added.
