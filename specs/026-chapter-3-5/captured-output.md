# Captured output — chapter 3.5

Every transcript the chapter quotes, captured from a real run rather than typed out.
Dated 2026-08-13 unless noted; the stores are the compose ones on 15432/16379/14222.

**Why this file exists.** A tutorial that prints output nobody ran is a tutorial that
drifts. Chapter 3.2 shipped two failing gates past a grep over a build log, and every
chapter since has captured what it quotes.

---

## R1 — the measurement that disqualified the obvious design (2026-08-10)

```text
Q1  delayed redelivery survives a restart?
    NAKKED  delay_ms=90000  at 1786500140980   (process then exits)
    ARRIVED at 1786500230983 in a fresh process — 3 ms late.  YES.

Q2  do delayed messages hold the ack-pending budget?
    max_ack_pending=3; nak'd 3 with a 300 s delay; fetched afterwards: 0
    num_ack_pending=3  num_pending=2            YES — and that is the problem.
```

Q2 is why the retry schedule is a `next_attempt_at` column and not a broker-held
delay: three sleeping messages made two available ones unfetchable, which at scale is
dead customer endpoints starving healthy ones (FR-WHK-05).

---

## The gates

```text
pnpm lint             exit 0
pnpm typecheck        exit 0
pnpm build            exit 0    9/9 turbo tasks
pnpm test             exit 0    156 unit
pnpm test:integration exit 0    149 integration
pnpm coverage         exit 0    296 tests, every ratchet intact

unit          config 6 · service-kit 3 · protocol 31 · api 74 · dispatcher 8 · gateway 34
integration   api 111 · dispatcher 16 · gateway 13 · e2e 9
```

---

## The hostile endpoint, all four modes

`--mode=ok` — one signed request, answered 200:

```text
--- request #1 -------------------------------------
  content-type: application/json
  relay-webhook-timestamp: 1786619864
  relay-webhook-signature: v1=2c8ee9a73829bbbab2a1eae67bab308a62d9d46d5adf11d32405054b47a65f59
  body: {"id":"e47e6915-…","data":{…},"type":"message.created","occurred_at":"…","environment_id":"…"}
MARKER received n=1 mode=ok
MARKER answered n=1 status=200
```

`--mode=hang` — accepted, never answered, abandoned on the attempt timeout:

```text
MARKER received n=1 mode=hang
MARKER hanging n=1
{"time":"2026-08-13T12:00:02.027Z","level":"info","service":"walk-dispatcher",
 "msg":"delivery.attempted","delivery_id":"d1ad7013-…","endpoint_id":"4d86be0c-…",
 "event_id":"5390bc67-…","attempt":1,"status":null,"latency_ms":3002}
```

`status` is null because no response was ever received, and `latency_ms` is the
timeout rather than a measurement of anything the customer's server did. The delivery
was rescheduled onto the next tier: a hang is a failure like any other, and the only
thing that ends it is the platform's own clock.

`--mode=fail --fast-forward` — the whole schedule, to the dead letter:

```text
  tiers: now → 1s → 5s → 30s → 300s → 1800s → 7200s
  7 attempts, then the delivery is dead-lettered.

  delivery 965aab34        attempt=2 state=pending next=2026-08-13T11:29:24.786Z
  attempt 2                failed → rescheduled as attempt 3
  attempt 3                failed → rescheduled as attempt 4
  attempt 4                failed → rescheduled as attempt 5
  attempt 5                failed → rescheduled as attempt 6
  attempt 6                failed → rescheduled as attempt 7
  attempt 7                failed → dead
  delivery 965aab34        attempt=7 state=dead next=2026-08-13T11:29:33.068Z
```

Seven requests reached the endpoint. `last_status=500` is what the customer's server
said on the last of them, kept for whoever has to explain it later.

---

## Verifying a signature the way a customer would (V5)

The endpoint verifies each arrival itself, in about fifteen lines whose entire
dependency list is `node:crypto` — the customer's side, written without looking at
ours:

```text
$ node scripts/hostile-endpoint.mjs --secret=hunter2
MARKER signature n=1 VERIFIED
```

The same request, with the body parsed and re-serialised first:

```text
$ node scripts/hostile-endpoint.mjs --secret=hunter2 --reserialize
MARKER signature n=1 FAILED (body re-serialised)
  ^ the data is identical and the signature does not match. Sign and
    verify the BYTES that were transmitted, never the object.
```

**The detail worth printing:** `--reserialize` sorts the top-level keys. A plain
round-trip through parse and stringify in the same runtime hands back the bytes it
was given — which is exactly why this bug survives every test written in the
service's own language, and then appears the day a customer verifies in Go, or a
proxy normalises the JSON, or somebody spreads the object into a new one to add a
field.

The walk made this mistake itself. `--print-signing-material` originally signed the
payload object as the script had built it, while the platform signs what comes back
out of `jsonb` — and PostgreSQL does not preserve key order. The printed signature
was for a rendering that never went on the wire.

---

## The dispatcher is genuinely separable (V6)

Both halves are asserted automatically, because the property is about processes and a
test can start and stop one:

```text
packages/e2e/src/webhooks.itest.ts
  invariant 14: an end user is served while the dispatcher does not exist        PASS

services/dispatcher/src/dispatcher.itest.ts
  invariant 14: a backlog accumulated while not consuming drains when it resumes PASS
```

The e2e journey never starts a dispatcher at all. Message delivery to end users is
unaffected and the customer's endpoint receives nothing, which is the assertion.

By hand, per quickstart V6: `docker compose stop dispatcher`, then
`node scripts/webhook-walk.mjs --send-only`. This needs an endpoint the CONTAINER can
reach — `--host=0.0.0.0` on the hostile endpoint and
`--url=http://host.docker.internal:4555/hook` on the walk. The `extra_hosts` entry
that makes `host.docker.internal` resolve was added to `compose.yaml` for this step,
which could not be run as written before.

---

## Coverage

```text
                    85.14 stmt / 77.16 branch / 85.57 func / 87.09 line

services/api/src/db/repository.ts     97.28 / 89.51 / 100.00 / 98.99
services/dispatcher/src/expand.ts     92.30 / 92.30 / 100.00 / 100.00
services/dispatcher/src/deliver.ts   100.00 / 90.90 / 100.00 / 100.00
```

`expand.ts` measured **0%** when the service arrived. The dispatcher's own suite
reached expansion by calling the repository against the database directly, so the
consumer that decodes an event, asks the api to expand it, and decides
ack-or-terminate had never once executed under test. Research R12 predicted that a
new deployable would leave the instrument green while measuring the wrong scope. It
was right — and the instrument needed no change to say so, only reading.

---

## Sabotage — five mutations, all caught

```text
M1  sign the re-serialised body, send the raw one   -> 1 failed  (invariants 4, 5)
M2  log the delivery-material response              -> 1 failed  (invariant 15)
M3  expand the event without claiming it            -> 2 failed  (invariant 8)
M4  drop the due predicate from the delivery relay  -> 2 failed  (invariant 10)
M5  report the outcome before posting               -> 2 failed  (at-least-once)
```

Both mutated files verified byte-identical afterwards by `md5sum`.

M1 would have PASSED before this run. The signature unit tests prove the signing
function is correct; nothing proved that the delivery path calls it over the right
bytes and puts the result on the wire, which is precisely where the re-serialisation
trap lives.

---

## The bug the walk found

The walk against `--mode=fail` stopped dead after one attempt, and the fault was in
the platform rather than the script:

```text
  attempt 2                failed → pending
  attempt 2                failed → pending
  attempt 2                failed → pending          (nine times, going nowhere)

  delivery b3ced241        attempt=2 state=pending
dead letters               0
=== endpoint attempts: 1 ===
```

The delivery relay deduplicated its publishes on the delivery id, which is the SAME
for all seven attempts, so JetStream collapsed every retry into the first attempt's
message. The publish reported success, no message reached the dispatcher, and the row
kept the `dispatched_at` its claim had set — which only an outcome report clears, and
no outcome was ever coming. **Every failing webhook was retried exactly zero times**,
and the whole of FR-WHK-03's schedule was unreachable.

No test caught it. The delivery suite drives the claim query directly with no broker
in the path, and the dispatcher's suite used a fresh delivery for every case, so
nothing had ever published the same delivery twice. The key is now
`{delivery_id}:{attempt}` — a republished attempt is still recognisably the same
work, a new attempt is allowed to say it is new — and the regression test is verified
to fail against the old key.

---

## Credential scan (T078, spec SC-011)

Scanned this file and both published chapter pages for leaked material:

```text
rk_ credentials          3 occurrences, all synthetic test fixtures
                         (rk_svc_credentials_itest_0123456789abcdef01234,
                          rk_svc_walk_0123456789abcdef0123456789abcd,
                          rk_svc_dispatcher_itest_0123456789abcdef)
43-char signing secrets  1 occurrence — whsec_test_2f4b8c1e… , a fixture in
                         signature.test.ts, not a minted secret
RELAY_WEBHOOK_SECRET_KEY value   0 occurrences
minted secrets from real runs    0 occurrences
```

The only long hex string in this file is an HMAC **output** — a signature, not a
key, computed over a throwaway development secret. `hunter2` appears five times in
each locale and is a value the reader is told to invent.

**This scan covers the captured transcript. Invariant 15 covers the running
service's log output.** Neither substitutes for the other: a secret can reach a
reader through a document nobody re-read, or through a log line somebody widened
"just for debugging", and the two are caught by different means.
