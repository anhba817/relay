# Chapter 3.8 — captured output

Real runs, pasted rather than described. Where a number depends on the clock
(`x-ratelimit-reset`, `retry-after`) it is whatever that run produced.

Everything below was captured after the phase-6 commit `25dd8a1`, against the
compose stores on their off-default ports.

---

## 1. The test before the code (T013)

`limits.itest.ts` was written first and watched fail. The state below is that
one reproduced exactly — `RateLimitMiddleware` removed from the middleware
chain in `app.module.ts`, everything else untouched.

```
× carries all three headers on a SUCCESSFUL response
× counts down across successive responses
× refuses with 429, Retry-After, and a four-field body
× counts a REST send against BOTH budgets, and reports the nearer
× names WHICH limit was reached, because they are different problems
× describes the budget that REFUSED, not the one with fewest remaining
× never limits /healthz, whatever the environment has spent
× does not count the gateway's internal routes as requests
× an override applies to ONE environment, not to every environment
× limits account creation per address, which has no tenant to key on
× two environments carry DIFFERENT configured limits, each at its own number
× keeps Limit and DROPS Remaining and Reset, rather than inventing them

Tests  12 failed | 6 passed (18)
```

The first one, in full:

```
AssertionError: expected null to be '600' // Object.is equality

- Expected: "600"
+ Received: null

 ❯ src/limits/limits.itest.ts:98:44
```

`null`, not a wrong number. That is the shape of the failure FR-RTL-02 is
about: the header is not incorrect, it is *absent*, which is exactly what a
limiter added as an afterthought produces.

Six tests passed with the limiter unwired. Five of those are the exemptions —
`/healthz`, the internal seam, the dispatcher — which pass trivially when
nothing is limited. A suite where every test goes red is a suite that has not
separated "this is limited" from "this is not".

---

## 2. The headers on a 2xx, and the 429 (V1, V2)

An environment configured `rest_limit_per_minute = 3`, `send_limit_per_minute = 2`.

```
$ POST /v1/channels/{id}/messages   # the first send
HTTP 201
x-ratelimit-limit: 2
x-ratelimit-remaining: 1
x-ratelimit-reset: 1787197740

$ POST /v1/channels/{id}/messages   # the second
HTTP 201
x-ratelimit-limit: 2
x-ratelimit-remaining: 0
x-ratelimit-reset: 1787197740

$ POST /v1/channels/{id}/messages   # over the send limit
HTTP 429
x-ratelimit-limit: 2
x-ratelimit-remaining: 0
x-ratelimit-reset: 1787197740
retry-after: 51
{
  "code": "rate_limited",
  "message": "too many messages for this environment; retry after 51 seconds",
  "docs_url": "https://relay.example/docs/errors/rate_limited",
  "request_id": "67219aad-436e-434c-8da2-a6a8c9a16754"
}
```

Three things this shows that a description would not.

`x-ratelimit-limit: 2` on a request against an environment whose *request*
limit is 3. The headers describe whichever budget has fewer remaining, and for
a send that is the send budget. A client told "3" would set its rate to 3 and be
refused at 2.

`x-ratelimit-reset` is the same value on all three responses. That is the fixed
window being a fixed window: the third request did not push the reset out.

The body has four fields. `request_id` is the one chapter 1.3 declared and no
chapter wired, and it is on the 429 because it is on every error now, not
because the 429 is special.

**This capture found a bug.** The first run of it printed
`x-ratelimit-limit: 3` above `"too many messages"` — the header describing the
request budget and the body describing the send budget, in one response. Both
budgets reach zero remaining on that third request while only `send` is over,
and the "fewest remaining" rule ties and picks `rest`. Fixed, and the test that
now covers it is named after what it checks. Research R41.

---

## 3. The outage, in both directions (V6)

One api process, `RELAY_REDIS_URL` pointed at a port that answers nothing,
`RELAY_AUTH_FAILURES_PER_MINUTE=3`, and an environment limited to 2 of
everything.

### Direction 1 — the tenant limiter serves

```
$ POST /v1/channels/{id}/messages   # 1 of 4, limit is 2
HTTP 201
x-ratelimit-limit: 2
x-ratelimit-remaining: (absent)
x-ratelimit-reset: (absent)

$ POST /v1/channels/{id}/messages   # 4 of 4, limit is 2
HTTP 201
x-ratelimit-limit: 2
x-ratelimit-remaining: (absent)
x-ratelimit-reset: (absent)
```

Four requests against a limit of two, all served. Redis is not a source of
truth (SAD §6.3) and a cache outage is not a reason to refuse paid traffic.

`Limit` survives and the other two vanish. `Limit` is policy, read from
Postgres, and is not degraded; `Remaining` and `Reset` existed only because
something was counting. Absent is the honest answer — not `-1`, which a client
that does not know the convention would parse as a number and read as "over".

### Direction 2 — the auth limiter does not

```
$ POST /auth/dev-token   # bad credential 1 of 5, threshold is 3
HTTP 401
$ POST /auth/dev-token   # bad credential 2 of 5, threshold is 3
HTTP 401
$ POST /auth/dev-token   # bad credential 3 of 5, threshold is 3
HTTP 401
$ POST /auth/dev-token   # bad credential 4 of 5, threshold is 3
HTTP 429
$ POST /auth/dev-token   # bad credential 5 of 5, threshold is 3
HTTP 429
```

Same process, same outage, same instant — and the fourth failed authentication
is refused. The shared counter is gone, so this is the in-process fallback at
the same threshold: the guarantee weakened from 3 per minute per fleet to 3 per
minute per instance, which is a small multiple rather than infinity.

And the log line, once, not once per attempt:

```json
{"time":"2026-08-20T03:48:30.986Z","level":"error","service":"api",
 "msg":"limits.auth_degraded",
 "detail":"counter store unreachable; counting failed authentications in process",
 "tracked":0}
```

No credential and no address (NFR-SEC-06). `tracked` is the count of addresses
the fallback is holding — what an operator needs to know whether the cap is
close. It reads 0 because the check runs before the failure is recorded, and the
line is emitted at most once per ten seconds.

Two failure directions, one outage, one process. That is the chapter.

---

## 4. The sabotage battery (V10)

Four of five. The fifth — marking `delivered_at` before the send returns — has
no target until the email transport exists, and is captured with phase 8.

Each mutation was applied to the real file, the suite run, the file reverted
with `git checkout --`, and the revert verified by `md5sum`.

### Mutation 1 — never set the headers on a 2xx

`rate-limit.middleware.ts`: set the three headers only when a decision refused.

```
× carries all three headers on a SUCCESSFUL response
× counts down across successive responses
× counts a REST send against BOTH budgets, and reports the nearer
× an override applies to ONE environment, not to every environment
× two environments carry DIFFERENT configured limits, each at its own number
× keeps Limit and DROPS Remaining and Reset, rather than inventing them

Tests  6 failed | 11 passed (17)
revert byte-identical: 13f476cc33681cac8109723780047338
```

Six, not one. The requirement an afterthought passes is load-bearing for
everything that reads a header — including both tests about *configured*
limits, which have no other way to see the number in effect.

### Mutation 2 — one counter shared across every environment

`store.ts`: `counterKey` drops the scope, so the key is `rl:{op}:{window}`.

```
× counts down across successive responses
× counts a REST send against BOTH budgets, and reports the nearer
× two environments carry DIFFERENT configured limits, each at its own number

Tests  3 failed | 14 passed (17)
revert byte-identical: ffbccbea68d2f8b13ee6ea299e71c951
```

**The interesting result is which test did not fail.** "An override applies to
ONE environment, not to every environment" — the original tenant-isolation test
— passed with every environment sharing one counter. It sets a low limit on one
environment and a default on another, and the shared counter refuses the low one
first either way.

The test that caught it is T017a, added at the eighth analysis pass because
"separate keys and separate quotas" is two claims and the suite only checked
one. A cross-tenant fault of the exact kind constitution I exists to prevent,
invisible to the test named after tenant isolation.

### Mutation 3 — the auth limiter fails open

`auth-limiter.ts`: when the shared store cannot answer, return `false` — the
same fail-open the tenant limiter does, one file away.

```
× does NOT let an address spend an unlimited number of failed logins

Tests  1 failed | 16 passed (17)
revert byte-identical: 1f5f78eea680446042d1af2b1bc3e482
```

One test, and it is the right one. This is the mutation that matters: R3's
decision is a *prohibition*, and the code implementing it is a fallback path
with no line reading "do not fail open" — the shape chapter 3.7 shipped
untested. It has a test.

### Mutation 5 — exempt nothing

`rate-limit.middleware.ts`: `operationsFor` no longer returns `[]` for paths
outside `/v1/`, so every route is customer traffic.

```
api:      × does not count the gateway's internal routes as requests
          Tests  1 failed | 16 passed (17)

gateway:  × spends ONE budget across both transports (FR-036, research R11)
          × lets the gateway through an environment that is at its REST limit
          Tests  2 failed | 3 passed (5)

revert byte-identical: 13f476cc33681cac8109723780047338
```

The dispatcher's test passed, and that is not a gap. The dispatcher is exempt
*twice*: by path and by having no environment to key on, because a platform
credential belongs to a deployment rather than a tenant. Removing one exemption
leaves the other.

The gateway has no second exemption. It forwards the end user's token, so its
calls resolve to `kind: "user"` exactly like customer traffic, and the path
prefix is the only thing standing between an environment at its REST limit and a
socket that stops working for a budget it never spends. Two of the three tests
that failed are in the gateway's own suite, one service away from the mutated
line — which is what a cross-service exemption looks like when it breaks.

---

## 5. The lanes and coverage

```
unit lane          10 tasks, 229 tests passed
integration lane    9 tasks, 213 tests passed        3m15s
coverage lane      47 files, 441 tests passed        3m59s

All files    89.50 statements | 82.73 branches | 89.57 functions | 90.98 lines
```

Before this chapter: 86.55 statements, 78.07 branches. Ten new files moved both
figures up, which is not the usual direction for a chapter that adds code.

The three pure files are at 100 on every metric:

```
services/api/src/limits/bucket.ts        100  100  100  100
services/api/src/limits/policy.ts        100  100  100  100
services/api/src/limits/fallback.ts      100  100  100  100
```

`fallback.ts` reaching 100 is the one that matters. It is the mechanism the auth
limiter degrades to, and an unmeasured branch in it is a hole in the thing the
chapter is about. Two of its branches were uncovered when first measured — both
in `peek`, both about what an unknown key means when the map is full — and both
turned out to be cases the tests had not thought of rather than cases nothing
could reach.

---

## 6. Credential scan of this file

Every transcript above was captured from a running system holding real
credentials, so this file is scanned rather than assumed clean. Fifteen
patterns, all case-insensitive, all zero hits:

```
rk_live_[A-Za-z0-9]                  0     tenant API key
rk_svc_[A-Za-z0-9]                   0     internal service credential
rk_test_[A-Za-z0-9]                  0     test-tier key
eyJ[A-Za-z0-9_-]{10,}                0     a JWT, by its base64 header
whsec_                               0     webhook signing secret
RELAY_WEBHOOK_SECRET_KEY             0     the encryption key, by name
RELAY_INTERNAL_CREDENTIAL            0     the service credential, by name
BpDal75yBZp7                         0     this lane's key, by its prefix
[A-Za-z0-9+/]{40,}={0,2}             0     any long base64 run
postgres://…:…@                      0     a DSN with a password in it
redis://…:…@                         0     the same for the cache
authorization: Bearer [A-Za-z0-9]    0     a header captured with its value
secret                               0     the word, anywhere
password                             0     the word, anywhere
api[_-]?key                          0     the word, anywhere
```

The `request_id` in section 2 is a v4 UUID minted per request and identifies a
log line, not a principal — it is meant to be quoted in a support ticket, which
is the entire reason FR-038 exists.
