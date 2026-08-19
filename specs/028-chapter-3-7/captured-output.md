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


---

## The sabotage battery

Five mutations, each applied to the real code, each reverted with the file
verified byte-identical afterwards.

```console
=============== mutation 1: never keep the marks after a successful resume
mutated 1 -> services/gateway/src/session.ts
  RESULT: caught
         × suppresses a frame the backfill already delivered, published after the resume 10735ms
         × still suppresses when two instances publish out of order 10881ms
=============== mutation 2: use < instead of <= in the predicate
mutated 2 -> services/gateway/src/resume.ts
  RESULT: caught
         × suppresses a frame the backfill already delivered, published after the resume 10724ms
         × still suppresses when two instances publish out of order 10884ms
=============== mutation 3: suppress on any channel rather than the frame's own
mutated 3 -> services/gateway/src/resume.ts
  RESULT: caught
         × delivers on a channel with no mark 9ms
         × keeps channels apart 1ms
=============== mutation 4: ignore the cursors when scoping the marks
mutated 4 -> services/gateway/src/resume.ts
  RESULT: caught
         × drops a channel the cursors never named 8ms
         × never exceeds the cursor set, which the resume contract already caps 2ms
=============== mutation 5: retire a mark once a higher sequence is delivered
mutated 5 -> services/gateway/src/session.ts
  RESULT: caught
         × still suppresses when two instances publish out of order 10883ms
=============== files restored byte-identical?
  YES
    e198acd38003926ff9884f94f466abf2  services/gateway/src/resume.ts
    4c51b9fa28ae2228983ab4488ad076cc  services/gateway/src/session.ts
  rebuild exit 0
SABDONE
```

**The battery changed the mutation list and then found a bad test.**

*The planned fourth mutation could not fail.* The quickstart's V6 listed "retain
the marks through a degraded resume". Reading the code before running it: every
`return degrade(...)` sits at lines 300-331 and the marks are assigned at line 360,
so on every degrade path the marks are still `null` and the clear inside `degrade`
cannot change anything. FR-005 holds STRUCTURALLY — the marks are only ever
assigned after a successful resume — not because that line runs. The clear stays as
a guard for a future path that degrades after computing marks, and the mutation was
replaced with one that targets the scoping instead: ignore the cursors, and the
bound FR-007 claims disappears.

*The fifth mutation survived the first run, and the fault was in the test.* The
out-of-order case published sequence 43 and then 42 against a mark of 43 — both at
or below it, so the retirement the mutation adds never fired. Research R3's scenario
needs a frame ABOVE the mark first: 43 is delivered, a rule that retired on it would
have nothing left, and the delayed 42 would then be delivered a second time. The
test now stages that, and the mutation is caught.

A test named after a property it does not exercise is worth more attention than a
test that fails. This one would have passed for ever, and the chapter's central
design decision — never retire the mark — would have had no test behind it at all.

---

## The e2e assertion, as chapter 3.6's baseline recorded it

This is the transcript that started the chapter, quoted from
`specs/027-chapter-3-6/baseline.txt` rather than re-run — it has not reproduced
since, which is itself part of the record.

```text
FLAKE 4 — a real duplicate on the resume boundary. NOT FIXED, and out of scope.
  Symptom: `expected [ 1, 2, 3, 4, 4 ] to deeply equal [ 1, 2, 3, 4 ]` in
  `packages/e2e/src/tuan.itest.ts`, journey 4. One occurrence in six lane runs.
  What it means: a client's timeline contains sequence 4 TWICE. The resume
  backfill delivered it and the live flush delivered it again. That is the exact
  property the next test in the same file asserts — "resumes with no gap and no
  double (FR-RTM-03, SAD §5.2)" — so this is not a loose assertion.
```

`[ 1, 2, 3, 4, 4 ]`. Chapter 3.6 left it deliberately, with the reproduction rate
attached "so it is a known defect rather than folklore about a flaky e2e suite" —
and that decision is the only reason this chapter had anything to start from.

Twenty pre-fix lane runs in this chapter reproduced it **zero** times. See
`baseline.txt` T005 for why that is about the load on the machine and not about
the defect.

---

## T047 — the credential scan

Six files scanned: `captured-output.md`, `baseline.txt`, `battery.txt`, both
published pages, and `relay-tutorial/fences/post-series.md`.

**The patterns, recorded rather than the conclusion.** A scan reported as "clean"
tells a later reader nothing about what was looked for.

```text
relay_sk_[A-Za-z0-9_-]+                                        0
relay_pk_[A-Za-z0-9_-]+                                        0
whsec_[A-Za-z0-9_-]+                                           0
eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}       (JWT)          0
-----BEGIN [A-Z ]*PRIVATE KEY-----                             0
[Aa][Ww][Ss][_-]?(secret|access)[_-]?key                       0
(SIGNING|ENCRYPTION|MASTER|SECRET|PRIVATE)_KEY\s*[=:]          0
(password|passwd|pwd)\s*[=:]\s*\S{6,}                          0
postgres(ql)?://\S*:\S+@                        (dsn+pw)       0
redis://\S*:\S+@                                               0
[Aa]uthorization:\s*(Bearer|Basic)\s+[A-Za-z0-9._-]{12,}       0
[0-9a-f]{64}                                    (sha256)       0
[A-Za-z0-9+/]{40,}={0,2}                        (base64 blob)  0
ghp_[A-Za-z0-9]{20,}                                           0
sk-[A-Za-z0-9]{20,}                                            0
[0-9a-f]{32}                                    (md5/hex key)  2
token=[A-Za-z0-9._-]{8,}                                       0
DATABASE_URL|REDIS_URL|NATS_URL                                1
```

**The two hits that are not credentials, checked rather than waved past.**

The `[0-9a-f]{32}` pair is the sabotage battery's `md5sum` of `resume.ts` and
`session.ts` — the byte-identical proof that each mutation was reverted. A digest
of a file that is itself published in full a few screens earlier discloses nothing.

The `DATABASE_URL|REDIS_URL|NATS_URL` hit is `process.env.RELAY_NATS_URL ??
"nats://localhost:4222"` in an unrelated post-series amendment: a variable name
and a default with no host, no user and no password.

The chapter quotes no request, no token and no signing secret. `resume.itest.ts`
mints a token through `token()` and the transcripts show test names and sequence
numbers, never a URL with a query string.
