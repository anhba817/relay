# Chapter 3.11 — validation

Every step reports an exit code. Run from `relay-platform/` with the compose
stack up. `DATABASE_URL` may be set or unset — every package in this workspace
falls back to the compose address, a property feature 030's R50 had to restore.

Steps V1 to V6 drive a clock rather than waiting on one. Nothing here sleeps for
a minute; if a step takes a minute, something is wrong with the step.

## V0 — Baseline, before anything changes

```bash
pnpm turbo run test --force
pnpm test:integration
pnpm coverage
```

Record the three test counts, the integration lane's wall-clock and the coverage
figures in `baseline.txt`. Chapter 3.10 closed at 256 integration tests across
twenty consecutive runs; record what *this* machine measures, because the
verification steps compare against it.

## V1 — A duration becomes a number

```bash
pnpm --filter @relay/api test:integration src/quotas/connections
```

Expected: green, and a connection driven across three minute boundaries records
the minutes it occupied (SC-001). Two connections across the same minute record
two (SC-002). This is the step that proves the figure exists before anything is
enforced on it.

## V2 — The gateway reports, and holds almost nothing

```bash
pnpm --filter @relay/gateway test:integration src/meter
```

Expected: green. Read the test that forces every report to fail and confirm it
asserts **no queue for open connections** — the gateway drops what it cannot
deliver and the next report repairs it (research R3). A buffer of open-connection
reports means the delta protocol crept back in.

**One exception, and it is bounded.** A closed connection has no next report, so
its final total is retained until a report carrying it is accepted (R19, FR-029).
Confirm the retention is capped and that a discard at the cap is logged and
counted rather than silent.

## V2a — The socket that lives and dies between two reports

```bash
pnpm --filter @relay/api test:integration src/quotas/connections
```

Expected: a connection opened and closed inside one reporting interval records
**one** connection-minute, not zero (SC-021, FR-005). Then the churn case: a
thousand five-second sockets are not free.

This step exists because the design's first draft counted them as zero — the
`close` handler removes a connection from the registry before the meter that
walks the registry can see it, so the unit chosen to charge reconnect churn
charged nothing (R19).

## V3 — Replay, loss, and reordering

```bash
pnpm --filter @relay/api test:integration src/quotas/connections
```

Expected, in one file:

- the identical report delivered twice moves the figure once (SC-003)
- a discarded report followed by the next one lands on the value neither loss
  nor duplication would have produced (SC-004)
- a report carrying a lower total credits zero and lowers nothing

Read the response bodies: the replay must answer `{"credited": 0}`. A test that
only checks the stored figure would pass against an implementation that credits
twice and clamps.

## V4 — The crash, and the shutdown that is not one

```bash
pnpm --filter @relay/gateway test:integration src/meter
```

Two signals, two outcomes, in one file.

**SIGKILL**: after the process is killed with a connection open, the figure
advances by no more than one reporting interval and is **identical** when read
again ten intervals later (SC-005). The second read is the assertion that
matters — the first only shows the loss is bounded, the second shows nothing is
still billing for a socket nobody holds.

**SIGTERM**: the same connection's minutes are recorded in full (SC-023). The
gateway had no signal handler at all before this chapter — `serve()` returns a
bare `node:http` Server and nothing ever called `server.close()`, so the flush
that four documents promised had no path that runs (R11).

Both need a gateway **process** to signal. The existing integration suites spawn
the api and run the gateway in-process, so this is the one step in the chapter
that needed new harness before it needed a test.

## V5 — The month boundary

```bash
pnpm --filter @relay/api test:integration src/quotas/period
```

Expected: a connection driven across midnight on the first places its minutes in
both periods, and the two sum to the connection's total (SC-011).

## V6 — The cap brakes the door

```bash
pnpm --filter @relay/api test:integration src/internal
pnpm --filter @relay/gateway test:integration src/session
```

Expected: a new connect refused, a connection opened before the breach still open
and still receiving sixty seconds later (SC-006), and a REST send and a history
read both succeeding against the same environment (SC-007). Raising the cap
restores connecting on the next attempt (SC-008).

**Two hops, two shapes**, and both have to be read off the wire rather than out of
a log. The api's half:

```bash
curl -isS -X POST "http://localhost:4000/internal/session" \
  -H "Authorization: Bearer $USER_TOKEN" | head -12
```

Expected: `HTTP/1.1 402 Payment Required`, four fields, and **no `Retry-After`**.

The client's half, on a real socket:

```bash
node -e '
const {WebSocket} = require("ws");
const ws = new WebSocket(`ws://localhost:${process.env.RELAY_GATEWAY_PORT||4001}/v1/ws?token=${process.env.USER_TOKEN}`);
ws.on("message", (d) => console.log("frame:", d.toString()));
ws.on("close", (code, reason) => console.log("close:", code, reason.toString()));
'
```

Expected: an `error` frame carrying `quota_exceeded`, the figures and the resume
date, then **close code 4008**. Chapter 3.8's refusal at this same door never
completes the handshake and carries a `Retry-After`; this one completes it and
closes with a code and a date. That difference is the contract (SC-022, FR-030).

`4008` has read "quota exhausted" in `packages/protocol/src/codes.ts` since
chapter 1.3 with nothing emitting it, and `session.test.ts` has carried a test
asserting that absence since chapter 3.8, whose comment says "quotas are a later
chapter". This is the step where that stops being true.

## V7 — The guard's prediction

```bash
RELAY_SENTINEL=plant pnpm test:integration 2>&1 | tee /tmp/ch311-guard.txt
grep -c "global-operation guard" /tmp/ch311-guard.txt
git diff --stat packages/test-harness/src/exempt.ts
```

Expected: whatever refusals the baited database already produces, **none naming
`usage_connections`, `usage_periods` or `quota_notifications`**, and an empty
diff on `exempt.ts` (SC-014).

**Record what this does not prove.** The guard watches five tables and none of
them is a usage or notification table, so silence here means nobody is looking
rather than nothing happening (R5a, R22). SC-014 can make a claim about the
exemption list; it cannot make one about the tables. Research R5 predicts no sweep for the second
chapter running. This step exists to find out the prediction is wrong.

If a file does join the list, the chapter says which global operation required
it. That is a result, not a failure.

## V8 — Nothing got slower at the door

```bash
pnpm --filter @relay/api test:integration src/internal/session.perf.itest.ts
```

Expected: the added connect-time read appears as index lookups on two primary
keys, not a scan (SC-012). Capture the `EXPLAIN (ANALYZE, BUFFERS)` output into
`captured-output.md`.

**Measure before diagnosing.** Chapter 3.10's T033 reported regressions of 273%,
341%, 303% and 411% from an uncontrolled benchmark, and three separate causes
were chased and two changes made before instrumentation showed the real figure
was 0.56ms per send. The instrument comes first here.

## V9 — Nobody is surprised

```bash
pnpm --filter @relay/api test:integration src/quotas
open http://localhost:${RELAY_MAILPIT_HTTP_PORT:-8025}
```

Expected: exactly three emails for the connection-minutes dimension per period,
read out of Mailpit rather than asserted on a send call, **filtered to the
recipient this test created** (SC-009, FR-032). Re-crossing an already notified
threshold sends nothing. A soft threshold with no hard cap sends its email and
refuses no connect (SC-020).

Mailpit is shared by the whole lane, and the relay's `drainOnce()` claims
undelivered rows across every environment — so an unfiltered "exactly three" is a
claim about the lane, and chapter 3.10's `toBeGreaterThan(0)` is true whether it
drained this test's row or a neighbour's (R22).

## V10 — The unauthenticated report

```bash
curl -sS -o /dev/null -w '%{http_code}\n' \
  -X POST "http://localhost:4000/internal/usage/connections" \
  -H 'content-type: application/json' \
  -d '{"connections":[{"connection_id":"00000000-0000-4000-8000-000000000001","environment_id":"'"$ENV_ID"'","period":"2026-08-01","minutes":999999}]}'
```

Expected: `401`, and the environment's figure unchanged when read before and
after (SC-010). Repeat with a valid API key and expect `403`
`wrong_credential_type`.

## V11 — Nothing was lost

```bash
pnpm turbo run test --force
pnpm test:integration
pnpm coverage
pnpm --filter relay-tutorial check:fences
pnpm lint
```

Expected: every count at or above V0's, coverage at or above its ratchet
**including the three entries this chapter adds**, and the fence chain byte-exact.
`repository.ts` is the one to watch: pinned at branches 90, and it went red in
chapters 3.5 and 3.6 on the same move this chapter makes (R23).

Twenty-one files this chapter touches carry 95 fences between them (research
R16), four of them build-gate files with entries in `post-series.md` as well; a
chain failure here is the cheapest place to find that a diff hunk was written
against the wrong pre-image.

## V12 — Twenty runs

```bash
for i in $(seq 1 20); do
  pnpm test:integration >"/tmp/ch311-run-$i.txt" 2>&1
  echo "$i exit=$? tests=$(grep -oP 'Tests\s+\K[0-9]+' "/tmp/ch311-run-$i.txt" | tail -1)"
done
```

Expected: twenty green, and the same test count in every run (SC-014). Chapter
3.10 needed three attempts and invalidated two of them itself — one by editing
source mid-battery, one by running a concurrent `pnpm turbo run test --force`
whose `nest build` rewrote `dist/` under a running import.

**`failing-files=0` beside `exit=1` is the signature.** A real failure names a
test; interference kills the lane before a test runs.

## V13 — The size gate

Count the finished page's prose words, excluding fences, front matter and figure
captions. Count its fences by reading the page. There is no script for either —
chapter 3.10 counted the same way, and a number somebody typed after looking is
worth more than a number a regex guessed about MDX.

```bash
PAGE="relay-tutorial/app/(en)/part-3/chapter-11/counting-a-connection/page.mdx"
grep -c '^```' "$PAGE"   # opening AND closing fences: halve it
```

Expected: between 2,000 and 4,000 prose words, and a fence count **read from the
page** rather than estimated (SC-015). Chapter 3.8's fence count went stale three
times across its analysis passes — 23, then 28, then 33 — and chapter 3.5 shipped
39 against an estimate of 22.

If the count exceeds 4,000, US4 moves out and US3 goes with it (research R17).

## V14 — The paperwork

```bash
grep -n "connection_minutes" services/api/migrations/0010_*.sql \
  services/api/src/quotas/config.ts services/api/src/quotas/quota.error.ts \
  services/api/src/quotas/quota-email.ts services/api/src/db/schema.ts | wc -l
```

Count the places the third dimension actually had to be named, and write the
number into `chapter-notes.md` beside chapter 3.10's written prediction of "a new
key plus a one-line constraint change" (SC-013, FR-024).

**Count first, then compare.** R15 predicts six. Reading the prediction before
counting is how a measurement turns into a confirmation, which is the failure
FR-024 was written to avoid.
