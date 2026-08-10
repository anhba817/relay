# Quickstart — validating chapter 3.4

Prerequisites: the `part3-ch3` state plus feature 024's coverage tooling, Docker
for the compose stores, and nothing else. The `EVENTS` stream already exists —
this chapter configures it rather than creating it.

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 RELAY_REDIS_PORT=16379 RELAY_NATS_PORT=14222 \
  docker compose up -d --wait postgres redis nats
pnpm build
DATABASE_URL="postgres://relay:relay@localhost:15432/relay" node services/api/dist/db/migrate.js
```

**On the environment variables.** There are two Redis knobs and they are not
interchangeable: `RELAY_REDIS_URL` is what the gateway's *production* code reads,
and `RELAY_REDIS_PORT` is what the gateway's *integration tests* read — they
build their own URL from it. Setting only the first produces seven timeouts in
`fanout.itest.ts` and `resume.itest.ts` that look like a broken fabric and are
not. Set both, as every block below does.

---

## V1 — Nothing regressed

```bash
pnpm lint && pnpm typecheck && pnpm test
RELAY_POSTGRES_PORT=15432 RELAY_REDIS_PORT=16379 RELAY_NATS_PORT=14222 \
  DATABASE_URL="postgres://relay:relay@localhost:15432/relay" \
  RELAY_REDIS_URL="redis://localhost:16379" \
  RELAY_NATS_URL="nats://localhost:14222" pnpm test:integration
```

Expected: every existing suite passes, including 2.8's journey and 3.3's outbox
suite, with assertions unchanged in substance (spec FR-020). The counts in
`baseline.txt` must be met or exceeded: **133 unit, 97 integration**.

**Check the exit codes, not the output.** Chapter 3.2 shipped two failures past a
`grep` over a build log; both were caught only when `$?` was read.

## V2 — The twelve invariants (contracts §Invariants)

```bash
# the ten that need a broker
RELAY_NATS_URL="nats://localhost:14222" \
  DATABASE_URL="postgres://relay:relay@localhost:15432/relay" \
  pnpm --filter @relay/api test:integration src/consumer/consumer.itest.ts

# the two that need nothing
pnpm --filter @relay/api test src/consumer/runtime.test.ts
```

Expected, each by name: the stream's settings read back as configured; applying
twice is a no-op; an event delivered, handled once, acknowledged; a kill in the
gap redelivered and handled once; deduplication surviving a restart; two
instances dividing the work; a throwing handler stopping; an unparseable payload
terminated on the first attempt; a stopped consumer receiving its backlog; a log
line carrying counts and never payloads. Then, Docker-free: a throwing handler
retried and never acknowledged, and a duplicate claim acknowledged without
running the handler again.

Invariant 4 takes about 30 seconds and invariant 7 about 60. That is the
acknowledgement deadline being real, not the suite hanging.

## V3 — The sabotage check

Remove the ledger claim from `runtime.ts` — leave everything else exactly as it
is — and re-run the broker-backed suite.

Expected: **three of the ten fail** (invariants 3, 4 and 6). A suite that still
passes with the mechanism removed is a suite that holds nothing. Restore the file
and confirm it is byte-identical to the fence before continuing.

The unit lane has its own version: making the `catch` return `acknowledge`
instead of `retry` must fail invariant 10 and nothing else.

## V4 — The walk, by hand

```bash
RELAY_NATS_URL="nats://localhost:14222" \
  DATABASE_URL="postgres://relay:relay@localhost:15432/relay" \
  node scripts/consumer-walk.mjs

RELAY_NATS_URL="nats://localhost:14222" \
  DATABASE_URL="postgres://relay:relay@localhost:15432/relay" \
  node scripts/consumer-walk.mjs --kill-before-ack
```

Expected: the first publishes, delivers, claims and acknowledges — four lines
that are the whole happy path. The second stops at `MARKER kill-me-now` with the
claim committed and no acknowledgement sent, which is the state the test's
`SIGKILL` freezes.

This is the same script the integration test spawns. One artifact, run by a
reader and by the suite, so neither can rot alone.

## V5 — Ask the broker, do not read the config file

```bash
RELAY_NATS_URL="nats://localhost:14222" node scripts/stream-info.mjs
```

Expected: every setting in `contracts/consumers.md` read back from the broker —
`max_age 604800s`, `max_bytes 1.00 GiB`, `discard old`, `duplicate_window 120s`,
`replicas 1`, with `retention` and `storage` marked immutable. A configuration
that was written is not the same as a configuration that was applied, which is
why this script asks rather than prints what it hoped for.

## V6 — Coverage, for the first time in Part 3

```bash
DATABASE_URL="postgres://relay:relay@localhost:15432/relay" \
  RELAY_REDIS_URL="redis://localhost:16379" \
  RELAY_NATS_URL="nats://localhost:14222" pnpm coverage
```

Expected: exit 0. Feature 024's thresholds hold, including the per-file ratchet
on `repository.ts` at 85% branches — which this chapter adds to and must not
break. Record the workspace numbers and `repository.ts`'s in `captured-output.md`
(spec SC-011, research R10).

**This is the check three chapters deferred.** If it exits non-zero, the chapter
does not ship until it does — that is what the instrument is for.

## V7 — The chapter itself

```bash
cd ../relay-tutorial
pnpm lint && pnpm build && pnpm check:docs && pnpm check:fences
```

Expected: the build renders both locales; the fence chain replays every published
chapter with no drift; docs-drift is clean.

Then the battery: 2,000–4,000 canonical words, ≥2 `WHY`, ≥1 `TRAP`, exactly one
`SKIP AHEAD` naming `part3-ch4`, ≥1 forward reference, 2–4 figures, one closing
`CHECKPOINT` — measured on the English page and mirrored in the Vietnamese one.

Then traceability (spec SC-012): every `FR-*`/`NFR-*`/`DR-*`/`ADR-*` in the
chapter must exist in `docs/04-srs.md`, `docs/05-sad.md` or
`docs/06-adr-deep-dives.md`, and every table and column named in prose must exist
in `schema.ts`.

## V8 — Nothing leaked, and both locales are up

```bash
grep -rniE "rk_(dev|live)_[A-Za-z0-9_-]{20,}|eyJ[A-Za-z0-9_-]{20,}" \
  specs/025-chapter-3-4/captured-output.md

curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000/part-3/chapter-04/jetstream-and-the-first-consumer
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000/vi/part-3/chapter-04/jetstream-and-the-first-consumer

# the reading shell actually mounted — not merely "the page loaded"
curl -s http://127.0.0.1:3000/part-3/chapter-04/jetstream-and-the-first-consumer | grep -c 'data-series-sidebar'
```

Expected: no working credential and no JWT body; `200` then `200` — this chapter
ships both locales; then `1` from the sidebar grep. Chapters 3.1 and 3.2 both
shipped with no sidebar because a 200-and-figures check called them correct. A
page that loads is not a page that is laid out.

---

## Definition of done

- V1–V8 pass, exit codes read rather than output grepped.
- Every number and transcript in the chapter came from V2, V4, V5 or V6 — not
  from estimation.
- The chapter states, in its own words, that a message exhausting its delivery
  attempts is caught by nothing, and that the shared-transaction pattern requires
  a transactional effect.
