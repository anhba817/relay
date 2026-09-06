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
    # every send and edit below uses $TOKEN — see Prerequisites; the DELETE takes $CREDENTIAL
    # send a message      → unchanged
    # edit that message   → +1
    # edit it again       → +1
    # delete that message → +1

**Expected** (SC-003, SC-005): three revisions, three increments, and a send that moves nothing.
**Failing means** either the counter is on the wrong path or a send is being counted, which turns
every active channel into a repair on every reconnect.

**THE ORDER MATTERS AND THIS GUIDE HAD IT WRONG.** It read `send → edit → delete → edit again`,
and the fourth step cannot be run: editing a deleted message answers **403**. The order above is
the one that was executed. Second time a scenario in this file could not be followed by the
person who wrote it — the first was the credential rules now in Prerequisites.

**And the refusal is worth one more look while you are there**: after the 403 the count stays put.
FR-003 puts the increment inside the transaction that applies the revision, so a revision that
does not commit raises nothing. Run the refused edit deliberately and read the column again.

---

## Scenario 2 — a client that missed a revision is told which channel (SC-001, FR-006)

Connect, note a message and the channel's count from the ack. Disconnect. Edit that message
**with `$TOKEN`, not `$CREDENTIAL`**. Reconnect presenting the stored cursor and count.

**Expected** (SC-001): `connection.ack.payload.revisions[<channel>]` is higher than the count presented.
The client can name the channel to repair from the ack alone, with no further request.

---

## Scenario 3 — a client that missed nothing is told to repair nothing (SC-002)

The same flow with no revision during the absence.

**Expected** (SC-002): the reported count equals the presented one, for every channel. **This is the
criterion that fails loudly if the counter is bumped by a send** — scenario 1 catches the cause,
this catches the symptom a customer would see.

---

## Scenario 4 — a pre-upgrade client is not sent on a repair (research R3)

Reconnect with `cursor` against channels that have revisions, and **read the ack as a client
that does not know the field exists**.

**Expected** (SC-001, SC-002): the ack carries `revisions` and the connection is otherwise
identical to today's — same `cursor`, same `resume_ok`, same backfill. A client built before this
feature ignores an unknown key and behaves exactly as it did.

**Failing means** every un-upgraded client repairs every channel on every reconnect — during the
deploy window, when the whole fleet is reconnecting at once. **This scenario changed shape.** It
used to say "reconnect with no `rev` parameter", because the platform was going to compare the
client's counts against its own and an absent count read as zero. Zero compares as lower than any
revised channel, so a literal reading of that design signalled a repair to every client that had
never stored a count. The platform now compares nothing, so the case cannot arise — which is a
better outcome than a branch that handles it.

---

## Scenario 5 — the cursor still parses, and gained no third field (research R2)

    ?cursor=<channel_id>:42

**Expected** (SC-001): the cursor resolves to sequence 42 and the channel id is not truncated —
unchanged from before this feature, which is the whole assertion. **Confirm no second parameter
is read**: `grep -n "searchParams" services/gateway/src/resume.ts` should show the cursor and
nothing else.

**Test with a channel id containing a colon** if one can be produced. That is what the rsplit
rule exists for, and what a third cursor field would have broken silently — producing plausible
sequences rather than an error. The rule is now protected by there being nothing new to parse.

---

## Scenario 6 — the reconnect rate does not move (SC-004)

    # baseline, before the change
    SCALE_SEED=/tmp/seed.json SCALE_CONNECTIONS=10000 node scripts/scale/load.mjs
    # then again after

**Expected** (SC-004, SC-005): within 10% of the baseline re-measured on this lane. The figures in
`docs/11-scalability-measurement-2026-09-06.md` — 1,125-1,675/s — are that machine's on that
day; **re-measure rather than comparing to them.**

**And measure the revision cost too** (SC-005): a revision now writes one more row.

---

## Scenario 7 — the clauses name the remedy (SC-007, FR-013)

Read **EIR-WS-03**, **FR-RTM-03** and **FR-RTM-05** in `docs/04-srs.md`, and §5.2 of
`docs/05-sad.md`.

**Expected** (SC-006, SC-007): the clause that describes what resume delivers also states what it
cannot, and names the count as the remedy; the clause that enumerates the ack's fields includes
it; and §5.2 gives a client the whole comparison rule in a table.

**THIS SCENARIO NAMED CLAUSES THAT DO NOT EXIST.** It said "SRS FR-016a and FR-016b", which are
chapter 3.23's *specification* ids — the SRS never used them. Reading the clauses rather than
the identifiers found three to amend where two were expected. Check a task's premise before
executing it, and check a scenario's before running it.

---

## Scenario 7a — implement the client from the published text alone (SC-006)

Read §5.2 and the three clauses **with the spec, the contracts and the source closed**, and write
down the client algorithm: which field, what shape, which channels appear, what to compare, what
to do in each outcome, and when to store.

**Expected**: every question answered without opening anything else.

**It was not, the first time.** The pass found that the *higher-than-reported* case had no client
instruction at all — the text said the platform refuses nothing, which is the platform's half of
FR-008 and not the client's. Two smaller gaps came with it: the history re-read named no
endpoint, and "the difference is how many" did not say how many *of what*. All three are now in
the table in §5.2.

**And this is not SC-006.** SC-006 asks whether the text is implementable by somebody who does
not already know the answer, and the person doing this pass wrote the feature. What this exercise
can find is *absent* information; it cannot find information that is present and unclear. That
needs a reader — `specs/036-chapter-3-18/reader-protocol.md`, 45 minutes, six questions — and
chapters 3.14 through 3.24 have each named this gap and none has closed it. **See `gaps.md`.**

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
