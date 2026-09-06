# Quickstart — validating the revision watermark

Seven scenarios. Each proves one success criterion and each is runnable.

## Prerequisites

**The lane environment, pinned where the tasks can see it.** Nine variables, and the addresses
having fallbacks does not make them optional — the credentials have none, and their absence
reads as a regression rather than a misconfiguration.

    RELAY_POSTGRES_PORT=15432          # this machine's own Postgres holds 5432
    DATABASE_URL=postgres://relay:relay@localhost:15432/relay
    RELAY_REDIS_URL=redis://localhost:6379
    RELAY_NATS_URL=nats://localhost:4222
    RELAY_INTERNAL_CREDENTIAL=rk_svc_local_development_credential_0000
    RELAY_INTERNAL_CREDENTIAL_GATEWAY=rk_svc_local_development_gateway_00000
    RELAY_WEBHOOK_SECRET_KEY=BpDal75yBZp7Fc2GtGS3D1vh7qOKgCWJkF6/d0XWxBU=
    RELAY_OUTBOX_RELAY=off  RELAY_EVENT_CONSUMER=off  RELAY_DELIVERY_RELAY=off

Local development values, in the record deliberately.

    cd relay-platform
    RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
    node scripts/reset-lane.mjs --yes-this-is-my-test-lane
    pnpm build

**AND AN END-USER TOKEN, WHICH THE SCENARIOS BELOW ALL NEED.** Every scenario here sends or
edits a message, and **neither can be done with the API key**:

    # an application credential may send only as a BOT user
    POST /v1/channels/<id>/messages   with the API key   →  422 sender_not_permitted
    # and the edit route refuses an API key outright
    PATCH /v1/channels/<id>/messages/<id>                →  403 wrong_credential_type

So mint a token for a real user first, and use it for both:

    TOKEN=$(curl -s -X POST "$API/auth/dev-token" \
      -H "authorization: Bearer $CREDENTIAL" -H 'content-type: application/json' \
      -d '{"user":"<external_id>","ttl_seconds":3600}' | jq -r .token)

**This is recorded because following the earlier draft of this guide failed twice** — once on
each rule, in that order — and neither refusal named the credential the route wanted until the
body was read.

---

## Scenario 1 — the counter rises once per revision, and not on a send (SC-003, FR-002, FR-011)

    psql "$DATABASE_URL" -Atc "select revision_sequence from channels where id = '<channel>'"
    # every send and edit below uses $TOKEN — see Prerequisites
    # send a message      → unchanged
    # edit that message   → +1
    # delete that message → +1
    # edit again          → +1

**Expected**: three revisions, three increments, and a send that moves nothing. **Failing
means** either the counter is on the wrong path or a send is being counted, which turns every
active channel into a repair on every reconnect.

---

## Scenario 2 — a client that missed a revision is told which channel (SC-001, FR-006)

Connect, note a message and the channel's count from the ack. Disconnect. Edit that message
**with `$TOKEN`, not `$CREDENTIAL`**. Reconnect presenting the stored cursor and count.

**Expected**: `connection.ack.payload.revisions[<channel>]` is higher than the count presented.
The client can name the channel to repair from the ack alone, with no further request.

---

## Scenario 3 — a client that missed nothing is told to repair nothing (SC-002)

The same flow with no revision during the absence.

**Expected**: the reported count equals the presented one, for every channel. **This is the
criterion that fails loudly if the counter is bumped by a send** — scenario 1 catches the cause,
this catches the symptom a customer would see.

---

## Scenario 4 — a pre-upgrade client is not sent on a repair (research R3)

Reconnect with `cursor` and **no** `rev` parameter, against channels that have revisions.

**Expected**: counts reported, no repair signalled. **Failing means** every un-upgraded client
repairs every channel on every reconnect — during the deploy window, when the whole fleet is
reconnecting at once. This is the scenario most likely to be got wrong, because reading FR-007
literally produces it.

---

## Scenario 5 — the cursor still parses (research R2)

    ?cursor=<channel_id>:42&rev=<channel_id>:7

**Expected**: the cursor resolves to sequence 42, not 7, and the channel id is not truncated.

**Test with a channel id containing a colon** if one can be produced, because that is what the
rsplit rule exists for and what a third cursor field would have broken silently — producing
plausible sequences rather than an error.

---

## Scenario 6 — the reconnect rate does not move (SC-004)

    # baseline, before the change
    SCALE_SEED=/tmp/seed.json SCALE_CONNECTIONS=10000 node scripts/scale/load.mjs
    # then again after

**Expected**: within 10% of the baseline re-measured on this lane. The figures in
`docs/11-scalability-measurement-2026-09-06.md` — 1,125-1,675/s — are that machine's on that
day; **re-measure rather than comparing to them.**

**And measure the revision cost too** (SC-005): a revision now writes one more row.

---

## Scenario 7 — the clauses name the remedy (SC-007, FR-013)

Read SRS FR-016a and SRS FR-016b in `docs/04-srs.md`.

**Expected**: both describe the limit and name the signal that reports it. A reader who finds
the limit finds the remedy in the same place.

---

## The gate set, at the end

Fourteen, and every exit code captured **outside** a pipeline — `fail=1` inside a
`for … | sort` runs in a subshell and dies with it, which has printed "ALL GATES: GREEN" over a
red one.

    relay-platform   pnpm typecheck · pnpm lint · pnpm build
    relay-tutorial   pnpm check:fences · check:docs · check:figures · check:srs · check:errors
    feature          the instruments in specs/044-revision-watermark/

**Run `check:fences` after ANY source edit**, not only the ratchet — and note that an edit to a
file published only as `(excerpt)` is invisible to it. Thirteen files are in that state.
