# Quickstart — chapter 3.23

**The premises below are derived from `research.md`, not maintained beside it.** P1–P5 were
written at plan time; P6, P7 and P8 come from analysis passes 1, 7 and 6. This document went
eight passes without being reopened while the work grew underneath it — which is the same
defect the plan's Summary had twice, and this note is here so the next reader checks the
research log rather than trusting this list.


## The lane environment, pinned where the tasks can see it

Nine variables and one stopped compose profile stand between a red lane and a green one.
Chapter 3.22 spent two full lane runs learning that they apply to `pnpm coverage` as well as
`test:integration`.

    RELAY_POSTGRES_PORT=15432 docker compose up -d --wait

    DATABASE_URL=postgres://relay:relay@localhost:15432/relay
    RELAY_REDIS_URL=redis://localhost:6379
    RELAY_NATS_URL=nats://localhost:4222
    RELAY_INTERNAL_CREDENTIAL=rk_svc_local_development_credential_0000
    RELAY_INTERNAL_CREDENTIAL_GATEWAY=rk_svc_local_development_gateway_00000
    RELAY_WEBHOOK_SECRET_KEY=BpDal75yBZp7Fc2GtGS3D1vh7qOKgCWJkF6/d0XWxBU=
    RELAY_OUTBOX_RELAY=off
    RELAY_EVENT_CONSUMER=off
    RELAY_DELIVERY_RELAY=off

All local development values, pinned here because a lane variable discovered at run time is a
lane variable that will be wrong once.

**Before a timing battery**: `RELAY_POSTGRES_PORT=15432 docker compose stop api gateway
dispatcher`, and nothing else runs on the machine — including your own tooling.

## P1 — the premise the whole resume decision rests on

**Run this first, before any writer exists.** If it fails, the spec's Slack-model decision is
built on nothing and the plan changes rather than the code.

Plant a tombstone by hand the way `repository.itest.ts` does — that suite is one of the few
allowed raw SQL — and read the channel's history through the REST route:

    UPDATE messages SET text = NULL, deleted_at = now() WHERE id = …

**Expected**: the message comes back in its original position with a null text, and the
positions on either side of it are unbroken. **Nothing filters it today**, and this is the
first test to say so.

## P2 — the frame a tombstone cannot fit through

    SET text = NULL, then ask messageSchema to parse the row as a message payload

**Expected**: it refuses, because `text` is `z.string()`. That refusal is the reason
`message.deleted` gets a payload of its own, and it is worth watching happen once rather than
reading about in two comments.

## P3 — what an edit above and below a cursor does

Connect, note the cursor, disconnect. Edit one message **newer** than the cursor and one
**older**. Reconnect.

**Expected**: the newer one arrives with its current text, because the backfill reads rows at
reconnect time. The older one produces nothing at all — no frame, and **no sequence gap**, so
nothing client-side detects it. Then re-read that range through history and watch the client's
view become correct.

**This is the documented cost of the decision, and it should be demonstrated rather than
asserted.**

## P4 — the event-type set is a pinned place

    OUTBOX_EVENT_TYPES currently holds three; FR-WHK-02 names eight

Adding `message.updated` and `message.deleted` moves the array, the branch its own comment
says the union forces, the exact-set assertion and the `toHaveLength(3)`. **Predicted: four.**
Chapter 3.22 predicted two pinned places for one close code and found four, so this number is
to be re-measured at close-out rather than trusted.

## P5 — the senderless row

121,250 rows in the lane have `user_id NULL`. Attempt an edit and a deletion on one.

**Expected**: both refused, because there is no author to authorise against. The alternative —
a null author meaning "anybody may" — would leave the oldest rows in the system the least
protected.

## P6 — the fabric cannot carry either kind

**The premise that added a phase, found by analysis pass 1.** Read it rather than take it:

    sed -n '18,20p' packages/protocol/src/fanout.ts     # "the fan-out has always carried
                                                        #  a wire frame's payload"
    grep -n ": Message" services/gateway/src/fanout.ts  # the delivery handler's type
    sed -n '347p'  services/gateway/src/session.ts       # type: "message.created", hardcoded

**Expected**: the subject's payload is a `Message` and the kind is stamped at the call site.
So a deletion — which has no text and cannot be a `Message` — **cannot ride `chan:{channel_id}`
at all**, and an edit that can ride it arrives indistinguishable from a creation. That is why
there is a fifth subject grammar and an ADR, in a chapter whose plan said no ADR was expected.

Count the typed points before changing them; research R13 has the numbers and ADR-19's record
said three where a re-derivation found eight.

## P7 — the isolation target list goes red on the build that adds a route

**Run this before and after adding the first route**, because the failure lands inside the
phase rather than at the end:

    npx vitest run --config services/api/vitest.integration.config.mts \
      src/isolation/targets.itest.ts

**Expected**: green before, **red after**, until the route is declared in
`services/api/src/isolation/targets.ts`. `targets.itest.ts` derives the live route table from
the Nest adapter and compares it with a hand-maintained list of 24 entries. `CLAUDE.md`
records this firing five times over two features and calls it the highest-yield check in the
repository — and **this chapter adds three routes.**

Then run the gauntlet itself and watch all three be attacked. Nothing needs building for that:
`isolation/fixtures.ts:66` already seeds a message per tenant, and its comment says why —
*"A message the member wrote, so a read attack has something to fail to find."*

## P8 — the edits route's refusal is a declaration, not an `if`

    remove @Accepts("application") from the edits route, run the end-user refusal test

**Expected**: it goes **red**, because the controller declares `@Accepts("application", "user")`
at class level and the route inherits both — so an end user reads what a message used to say,
the one thing FR-023a exists to forbid. The guard reads `getAllAndOverride`, so a method-level
declaration is what wins.

**Watch it bite once.** `credential.guard.ts:31` argues the case and
`messages.controller.ts:59` names the alternative as the defect that let the gateway's
credential reach `POST /internal/dispatch/replay`.

## Gates, and how to run them so they mean something

From `relay-tutorial`: `check:fences`, `check:docs`, `check:figures`, `check:srs`,
`check:errors`. From `relay-platform`: `typecheck`, `lint`, `build`, `test`.

**Capture every exit code into a variable.** `pnpm -s check:x 2>&1 | tail -3; echo $?` reads
`tail`'s status, not the checker's — chapter 3.22 hit that on the one gate that was red.
`check:errors` reads the **built** `dist`, so build before believing it.
