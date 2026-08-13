# Quickstart — validating chapter 3.5

Prerequisites: the `part3-ch4` state, Docker for the compose stores, and nothing
else. This chapter adds a service to the stack, so `docker compose up` brings up
one more container than it did in 3.4.

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 RELAY_REDIS_PORT=16379 RELAY_NATS_PORT=14222 \
  docker compose up -d --wait postgres redis nats
pnpm build
DATABASE_URL="postgres://relay:relay@localhost:15432/relay" node services/api/dist/db/migrate.js
```

**On the environment variables.** Two Redis knobs, not interchangeable:
`RELAY_REDIS_URL` is read by production code, `RELAY_REDIS_PORT` by the integration
tests, which build their own URL. Setting only the first produces seven timeouts in
the gateway's suites that look like a broken fabric and are not. Chapter 3.4's
notes recorded this; it costs an hour every time it is rediscovered.

---

## V0 — The measurement that came before the code  ✅ DONE 2026-08-10

Research R1's two questions were answered against the compose broker before any
code was written. **Keep this section**: it is the reason the design looks the way
it does, and a reader re-running it is re-deriving the decision rather than taking
it on trust.

```text
Q1  delayed redelivery survives a restart?
    NAKKED  delay_ms=90000  at 1786500140980   (process then exits)
    ARRIVED at 1786500230983 in a fresh process — 3 ms late.  YES.

Q2  do delayed messages hold the ack-pending budget?
    max_ack_pending=3; nak'd 3 with a 300 s delay; fetched afterwards: 0
    num_ack_pending=3  num_pending=2            YES — and that is the problem.
```

Q2 is why the schedule is a `next_attempt_at` column rather than a broker-held
delay: three sleeping messages made two available ones unfetchable, which at scale
is dead customer endpoints starving healthy ones (FR-WHK-05).

**The instruction was to stop and re-plan rather than adapt in place, and that is
what happened** — see research R1 and R13. If you are re-running this and Q2 now
answers "no" on a newer broker, that is a finding worth recording, not a licence to
simplify the design without re-measuring at scale.

## V1 — Nothing regressed

```bash
pnpm lint && pnpm typecheck && pnpm test
RELAY_POSTGRES_PORT=15432 RELAY_REDIS_PORT=16379 RELAY_NATS_PORT=14222 \
  DATABASE_URL="postgres://relay:relay@localhost:15432/relay" \
  RELAY_REDIS_URL="redis://localhost:16379" \
  RELAY_NATS_URL="nats://localhost:14222" pnpm test:integration
```

Expected: every existing suite passes, including 2.8's journey, 3.3's outbox suite
and 3.4's consumer suite, with assertions unchanged in substance (spec FR-027).
Counts must meet or exceed `baseline.txt` — which for this chapter starts from
3.4's closing 133 unit / 97 integration.

**Check the exit codes, not the output.**

## V2 — The sixteen invariants (contracts/dispatcher.md §Invariants)

```bash
# the two pure ones — a signature is a pure function
pnpm --filter @relay/dispatcher test

# the rest, against the stores, the broker and the hostile endpoint
RELAY_NATS_URL="nats://localhost:14222" \
  DATABASE_URL="postgres://relay:relay@localhost:15432/relay" \
  pnpm test:integration
```

Expected, each by name: the endpoint limit and its error; a secret returned once;
cross-tenant refusal; a signature verified by an independent verifier; the
re-serialisation trap failing; both secrets valid in a rotation window;
subscription filtering; one event becoming N deliveries exactly once; six attempts
on the widening schedule; no attempt early; **a pending retry surviving a restart of both
the dispatcher and the api**; nothing published before it is due, and a not-yet-due
delivery holding no acknowledgement slot; dead-letter retrieval and replay; a hanging endpoint abandoned without delaying
others; the API service unaffected by the dispatcher's absence; **no log line
carrying a signing secret or a message body**; and a delivered body carrying the
event `id` a recipient deduplicates on.

Invariant 9 spends real time on the widening schedule. That is the schedule being
real, not the suite hanging — the chapter should say what the test compresses and
what it does not. Since R1's re-plan the tiers are rows rather than broker delays,
so a test *may* legitimately advance `next_attempt_at` instead of waiting two hours;
if it does, invariant 10 is what keeps that shortcut honest.

## V3 — The sabotage check

Five mutations, each reverted afterwards and the file verified byte-identical to
its fence:

| Mutation | Must fail |
|---|---|
| sign over the parsed-and-re-serialised body instead of raw bytes | invariants 4 and 5 |
| log the delivery-material response | invariant 15 |
| expand the event without claiming it | invariant 8 |
| drop the `next_attempt_at <= now()` predicate from the delivery relay | invariants 9 and 10 |
| claim the delivery *before* posting instead of reporting after | the at-least-once invariant — a crash in the gap must lose a webhook, and a test must catch it |

A suite that still passes with a mechanism removed is a suite that holds nothing.

## V4 — The hostile endpoint, by hand

```bash
node scripts/hostile-endpoint.mjs --mode=fail      # always 500
node scripts/hostile-endpoint.mjs --mode=hang      # accepts, never responds
node scripts/hostile-endpoint.mjs --mode=ok        # 200

node scripts/webhook-walk.mjs
```

Expected: against `--mode=ok`, one signed request whose signature the walk verifies
in front of the reader. Against `--mode=fail`, six attempts on the widening
schedule and then a dead letter. Against `--mode=hang`, the attempt abandoned on
the timeout while a second, healthy endpoint keeps receiving.

The hostile endpoint is the same artifact the integration suite drives. One
artifact, run by a reader and by the tests, so neither can rot alone — 3.3 and 3.4
each made the same argument for their walk scripts.

## V5 — Verify a signature the way a customer would

```bash
node scripts/webhook-walk.mjs --print-signing-material
```

Then verify it by hand, in a different language or with a shell one-liner, using
only the documented recipe. **If it can only be verified with the platform's own
code, the contract is not a contract.**

Then repeat with the body re-serialised, and watch it fail. That failure is the
chapter's most useful paragraph.

## V6 — The dispatcher is genuinely separable

```bash
docker compose stop dispatcher
node scripts/webhook-walk.mjs --send-only     # messages still send
docker compose start dispatcher
sleep 10
# the backlog drained without intervention
```

Expected: with the dispatcher stopped, message delivery to end users is entirely
unaffected and events accumulate; on its return the backlog drains with nobody
intervening (spec FR-016, SC-009).

This is the demonstration that the service split bought something. Inside the api,
"webhooks do not delay end users" would be a claim about event loops; across a
process boundary it is a claim about processes, and it can be shown by stopping
one.

## V7 — Coverage and CI cover the new service

```bash
DATABASE_URL="postgres://relay:relay@localhost:15432/relay" \
  RELAY_REDIS_URL="redis://localhost:16379" \
  RELAY_NATS_URL="nats://localhost:14222" pnpm coverage
```

Expected: exit 0, **and the dispatcher's files appear in the report**. A new
deployable that is not in `vitest.coverage.config.mts` and not in `ci.yml` sits
outside the measurement while every existing ratchet stays green — an instrument
reporting comfortably about the wrong scope (research R12).

Check `repository.ts` specifically: it gains scoped endpoint and dead-letter
operations, and it sits at 86.30% branches against a ratchet of 85. Expect to raise
the ratchet with this chapter's work rather than discover it broken at the end.

## V8 — The chapter itself

```bash
cd ../relay-tutorial
pnpm lint && pnpm build && pnpm check:docs && pnpm check:fences
```

Expected: both locales render; the fence chain replays every published chapter with
no drift — **including every file this chapter's prose asserts** (spec FR-029, the
rule chapter 3.4 broke).

Then the battery: 2,000–4,000 canonical words, ≥2 `WHY`, ≥1 `TRAP`, exactly one
`SKIP AHEAD` naming `part3-ch5`, ≥1 forward reference, 2–4 figures, one closing
`CHECKPOINT`. Then traceability (spec SC-013).

**And the fence count.** R11 budgets 22–26. If the actual approaches the upper
bound, that is the signal to check the narrowing decision held rather than to
absorb it quietly.

## V9 — Nothing leaked, and both locales are up

```bash
grep -rniE "rk_(dev|live)_[A-Za-z0-9_-]{20,}|eyJ[A-Za-z0-9_-]{20,}|whsec_[A-Za-z0-9_-]{16,}" \
  specs/026-chapter-3-5/captured-output.md

curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000/part-3/chapter-05/…
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000/vi/part-3/chapter-05/…
curl -s http://127.0.0.1:3000/part-3/chapter-05/… | grep -c 'data-series-sidebar'
```

Expected: no credential of any kind — **including a signing secret**, which is new
this chapter and is the one most likely to be quoted innocently in a transcript
showing a delivery. Then `200`, `200`, `1`.

Figures render client-side, so verify the SVGs in a headless browser rather than by
grepping the served HTML — 3.4's notes recorded why the curl check alone is not
enough.

---

## Definition of done

- V0 measured and recorded **before** the code exists; V1–V9 pass, exit codes read.
- Every number and transcript in the chapter came from a real run.
- A signature can be verified by someone holding only the request and the secret,
  demonstrated in the chapter with something other than the platform's own code.
- The chapter states, in its own words, that delivery is at-least-once, that the
  duplicate is the customer's to absorb, and which identifier absorbs it.
- `docs/07-tutorial-plan.md` is amended to match what shipped (spec FR-033).
