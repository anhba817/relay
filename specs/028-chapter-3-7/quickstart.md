# Quickstart — validating chapter 3.7

Prerequisites: the `part3-ch6` state and Docker. No new infrastructure, no
migration — this chapter adds a field to a struct.

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 RELAY_REDIS_PORT=16379 RELAY_NATS_PORT=14222 \
  docker compose up -d --wait postgres redis nats
pnpm build
```

**The environment variables that cost an hour if you get them wrong.** Two Redis
knobs, not interchangeable: `RELAY_REDIS_URL` is read by production code,
`RELAY_REDIS_PORT` by the integration tests, which build their own URL. The e2e
harness spawns real gateways, so it needs the first. Chapters 3.4, 3.5 and 3.6 all
recorded this. `RELAY_WEBHOOK_SECRET_KEY` is base64, not hex — a 64-character hex
string decodes to 48 bytes and every webhook suite fails.

---

## V0 — Measure the flake BEFORE the fix

```bash
for i in $(seq 1 20); do pnpm test:integration >/dev/null 2>&1; echo "$i $?"; done
```

Expected: at least one failure in `packages/e2e/src/tuan.itest.ts`, journey 4,
with `expected [ 1, 2, 3, 4, 4 ] to deeply equal [ 1, 2, 3, 4 ]`.

**Run this first and record the count.** SC-001 asks for twenty consecutive passes
after the fix, and that number says nothing without knowing what twenty runs
looked like before it. Chapter 3.6 observed one failure in six runs; if twenty
pre-fix runs produce none, say so — it means the rate is lower than measured and
the deterministic test below is carrying the entire proof.

Each run takes about nine minutes with the lane serialised, so this is three hours
of wall clock. It is the only honest way to state a rate.

## V1 — The deterministic failure

```bash
pnpm --filter @relay/gateway test:integration src/resume.itest.ts
```

Expected **before the fix**: the new fourth-quadrant test fails, every time. It
publishes a frame the backfill already delivered, after the resume has completed,
and the client receives it twice.

Expected **after the fix**: it passes, and so do the three that were already
there.

**Watch it fail before you make it pass.** A regression test that has never been
seen to fail is a regression test nobody has checked — chapter 3.5 shipped an
assertion that could not fail and chapter 3.6 shipped a sabotage mutation that
could not compile.

## V2 — The timeline, captured

Capture the failing e2e run's assertion output and the deterministic test's
output. The chapter quotes both: the first is how the defect was found, the second
is how it is held.

## V3 — Nothing was lost

```bash
pnpm --filter @relay/gateway test:integration
pnpm --filter @relay/gateway test
```

Expected: every chapter 2.6, 2.7 and 2.8 assertion passes unchanged in substance.

**This is the direction that matters.** The change suppresses frames, so its
failure mode is a gap, and a gap is worse than the duplicate it replaces
(constitution II). The three existing resume tests are the ones to read: one
proves a mid-backfill frame is deduplicated, one proves a mid-backfill frame the
backfill did not contain is still delivered, one proves a post-resume frame above
the mark arrives.

## V4 — The degraded resume retains nothing

Force a degrade — a malformed cursor, or an api whose backfill throws — and then
publish a frame with a low sequence.

Expected: the frame is delivered. A degraded resume told the client to page
history, so nothing may be suppressed on the strength of a backfill it never
received.

## V5 — Out-of-order publication

Publish sequence 5 and then sequence 4, both at or below the mark, after a resume
has completed.

Expected: neither is delivered. This is the case that made the spec's original
design unsafe — it assumed the mark could be retired once a higher sequence
arrived, which would have delivered the 4.

## V6 — The sabotage check

Four mutations, each reverted afterwards and the file verified byte-identical:

| Mutation | Must fail |
|---|---|
| never set the marks after a successful resume | V1's deterministic test |
| use `<` instead of `<=` in the predicate | the boundary case — the mark's own sequence arrives twice |
| suppress on every channel rather than the frame's own | invariant 4 — a second channel's frame disappears |
| retain the marks through a degraded resume | V4 — a client told to page history is also denied the frames |

A suite that still passes with a mechanism removed is a suite that holds nothing.
The second mutation is the one to watch: `flushable` already uses `<=` and its
comment says why, so an off-by-one here would be the same mistake made twice in
one file.

## V7 — Coverage

```bash
pnpm coverage
```

Expected: exit 0, every ratchet intact. `resume.ts` is a pure module and the new
predicate is pure; it should reach 100% branches without effort, and if it does
not, the missing branch is a case the tests have not thought of.

## V8 — The site

```bash
cd ../relay-tutorial
pnpm lint && pnpm build && pnpm check:docs && pnpm check:fences
```

Expected: exit 0 throughout, the chain replays, and
`/part-3/chapter-07/commit-and-publish-are-two-instants` plus its Vietnamese twin
return 200 with figures rendered as SVG in a headless browser. A page that returns
200 is not a page that is laid out — chapter 3.5 shipped three blank diagrams past
a passing build.

## V9 — The cross-reference sweep

```bash
grep -rn "chapter 3\.[6-9]\|Chapter 3\.[6-9]" docs/ relay-tutorial/app/ relay-platform/services relay-platform/scripts
```

Expected: every hit names what it claims to name. Quotas is 3.8, the gauntlet is
3.9, and no source comment cites a chapter number at all — including
`services/api/src/db/schema.ts:375`, which has said "chapter 3.7's cross-tenant
gauntlet" since before chapter 3.6 moved the gauntlet to 3.8.

## Definition of done

- V0 measured and recorded **before** the fix exists; V1 watched to fail, then to
  pass.
- Twenty consecutive post-fix lane runs, with the count from V0 beside them.
- Every number and transcript in the chapter came from a real run.
- The chapter states which part of chapter 2.7's reasoning was incomplete, without
  rewriting chapter 2.7.
- `docs/07-tutorial-plan.md` and the site registry agree with each other and with
  the published pages.
