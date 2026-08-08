# Quickstart — validating chapter 3.3

Prerequisites: the `part3-ch2` state, Docker for the compose stores, and nothing
else. NATS with JetStream has been in `compose.yaml` since Part 1 — this chapter
is the first to connect to it.

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 RELAY_REDIS_PORT=16379 RELAY_NATS_PORT=14222 \
  docker compose up -d --wait postgres redis nats
pnpm build
DATABASE_URL="postgres://relay:relay@localhost:15432/relay" node services/api/dist/db/migrate.js
```

---

## V1 — Nothing regressed

```bash
pnpm lint && pnpm typecheck && pnpm test
RELAY_POSTGRES_PORT=15432 RELAY_REDIS_PORT=16379 RELAY_NATS_PORT=14222 \
  DATABASE_URL="postgres://relay:relay@localhost:15432/relay" \
  RELAY_REDIS_URL="redis://localhost:16379" \
  RELAY_NATS_URL="nats://localhost:14222" pnpm test:integration
```

Expected: every existing suite passes, including 2.8's journey, with assertions
unchanged in substance (spec FR-016). The chapter-end counts are recorded in
`baseline.txt` and must be met or exceeded.

**Check the exit codes, not the output.** Chapter 3.2 shipped two failures past a
`grep` over a build log; both were caught only when `$?` was read.

## V2 — The twelve invariants (contracts §Invariants)

```bash
RELAY_POSTGRES_PORT=15432 RELAY_NATS_PORT=14222 DATABASE_URL="…" RELAY_NATS_URL="…" \
  pnpm --filter @relay/api test:integration
```

Expected, each by name: one row per committed message; none for a rolled-back
write; none for a recognised retry; one per door; the row surviving a `SIGKILL`
in the gap; the naive path losing it under the same kill; the relay publishing
and marking; two relays publishing each row once; the backlog draining after the
broker returns; a stable event id; no payload in any log line.

## V3 — The demonstration, by hand

```bash
node scripts/dual-write-walk.mjs --mode=naive
node scripts/dual-write-walk.mjs --mode=outbox
```

Expected: the first prints a committed message and then, after the kill, an event
count of zero — with no error anywhere in the transcript, which is the whole
point. The second prints the same commit, the same kill, and an event that is
still there afterwards.

If the naive run ever *keeps* its event, the demonstration is broken and the
chapter's argument with it — treat that as a failing test, not a lucky run.

## V4 — The broker can be absent

```bash
docker compose stop nats
node scripts/credential-walk.mjs        # writes still work
psql -c "SELECT count(*) FROM outbox WHERE published_at IS NULL"
docker compose start nats
sleep 5
psql -c "SELECT count(*) FROM outbox WHERE published_at IS NULL"
```

Expected: writes succeed with the broker down, the unpublished count rises, and
after the broker returns it falls to zero without anyone intervening (SAD §7's
claim, spec SC-007).

## V5 — Two relays, one table

```bash
PORT=4000 node services/api/dist/main.js &
PORT=4010 node services/api/dist/main.js &
node scripts/dual-write-walk.mjs --mode=outbox --messages=200
```

The relay runs with the service — it is not something you switch on (ADR-06 puts
it inside the api). Suites that want a quiet database set `RELAY_OUTBOX_RELAY=off`;
nothing needs to set it on.

Expected: 200 events at the broker, 200 rows marked published, and no row
published twice — `SKIP LOCKED` doing the work a coordination mechanism would
otherwise need (spec SC-006).

## V6 — The chapter itself

```bash
cd ../relay-tutorial
pnpm lint && pnpm build && pnpm check:docs && pnpm check:fences
```

Expected: the build renders the new page; the fence chain replays every published
chapter with no drift; docs-drift is clean.

Then the battery: 2,000–4,000 canonical words, ≥2 `WHY`, ≥1 `TRAP`, exactly one
`SKIP AHEAD` naming `part3-ch3`, ≥1 forward reference, 2–4 figures, one closing
`CHECKPOINT`.

Then traceability (spec SC-009): every `FR-*`/`NFR-*`/`DR-*`/`ADR-*` in the
chapter must exist in `docs/04-srs.md`, `docs/05-sad.md` or
`docs/06-adr-deep-dives.md`, and every table and column named in prose must exist
in `schema.ts`.

## V7 — Nothing leaked

```bash
grep -rniE "rk_(dev|live)_[A-Za-z0-9_-]{20,}|eyJ[A-Za-z0-9_-]{20,}" \
  specs/023-chapter-3-3/captured-output.md
```

Expected: no working credential and no JWT body. The relay's log lines carry
counts and durations, never payloads — a message body in a log is a tenant's
data in an operator's terminal.

## V8 — Publication state

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000/part-3/chapter-03/the-outbox
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:3000/vi/part-3/chapter-03/the-outbox

# the reading shell actually mounted — not merely "the page loaded"
curl -s http://127.0.0.1:3000/part-3/chapter-03/the-outbox | grep -c 'data-series-sidebar'
curl -s http://127.0.0.1:3000/part-3/chapter-03/the-outbox | grep -c 'grid-cols-\[16rem'
```

Expected: `200` then `404` — English published, Vietnamese honestly absent, with
the listing showing 3.3 untranslated and 3.4–3.7 forthcoming. Then `1` and at
least `1` from the two greps: the series sidebar and the reading grid are both
in the markup.

**Why the last two lines exist.** Chapters 3.1 and 3.2 were both verified with a
200-and-figures check and both shipped rendering with **no sidebar and no
on-this-page rail** — `app/(en)/part-3/layout.tsx` had never been created, and
`ReadingLayout` is mounted only by a part layout. Two features called that
"published and correct". A page that loads is not a page that is laid out.

---

## Definition of done

- V1–V8 pass.
- Every number and transcript in the chapter came from V2, V3, V4 or V5 — not
  from estimation.
- The chapter states, in its own words, that ordering is not guaranteed and that
  duplicates are possible.
