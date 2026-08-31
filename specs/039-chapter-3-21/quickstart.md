# Quickstart — chapter 3.21

*How to run what this chapter builds, and what each command should say. Every command here
was run during planning or is quoted from chapter 3.20's record.*

---

## The lane environment

Pinned rather than rediscovered one red run at a time.

    RELAY_POSTGRES_PORT=15432 docker compose up -d --wait

**Five store containers, not four** — clickhouse, mailpit, nats, postgres, redis. A lane
without mailpit fails on `ECONNREFUSED :8025`.

**This machine's own PostgreSQL holds 5432**, so the stack goes on 15432. Omitting that
variable from `docker compose up` takes the container down mid-recreate with
`bind: address already in use`, which chapter 3.20 did once.

The nine variables:

    DATABASE_URL=postgres://relay:relay@localhost:15432/relay
    RELAY_REDIS_URL=redis://localhost:6379
    RELAY_NATS_URL=nats://localhost:4222
    RELAY_INTERNAL_CREDENTIAL=rk_svc_local_development_credential_0000
    RELAY_INTERNAL_CREDENTIAL_GATEWAY=rk_svc_local_development_gateway_00000
    RELAY_WEBHOOK_SECRET_KEY=BpDal75yBZp7Fc2GtGS3D1vh7qOKgCWJkF6/d0XWxBU=
    RELAY_OUTBOX_RELAY=off
    RELAY_EVENT_CONSUMER=off
    RELAY_DELIVERY_RELAY=off

Plus `NO_COLOR=1 FORCE_COLOR=0` and a `sed` over the ANSI escapes for any run whose counts
are recorded. **Without these the api lane reads four red** — three platform routes
answering 401 and `invariant 9` throwing `NatsError: CONNECTION_REFUSED` — and it looks
like a regression.

---

## Verify the four premises before building on them

Two of this chapter's brief were false. These are the commands that found that, and they
should be re-run at the start rather than trusted.

    # R1 — is the message path still typed to messages? Expect four hits.
    grep -n "publish(message: Message)\|message: Message\|messageCreatedSchema" \
      services/gateway/src/fanout.ts
    grep -n '"message.created"' services/gateway/src/session.ts

    # R2 — can a client say anything but message.send? Expect one refusal.
    sed -n '948,956p' services/gateway/src/session.ts

    # R3 — does the published typing frame have a state field? Expect two fields.
    sed -n '96,102p' packages/protocol/src/frames.ts

    # R5 — is the limiter's operation a closed union? Expect two members.
    grep -n 'operation: "connect" | "send"' services/gateway/src/limits.ts

---

## Phase 1's red test

**The chapter opens with a failing test and the commit body says so.** A red lane nobody
explained is indistinguishable from a red lane nobody noticed, and CI cannot tell them
apart.

    pnpm --filter @relay/gateway test:integration

Expect one failure: a client uttering the typing signal is refused with
`unknown_frame_type` and close 4002. That refusal is correct today and is what Phase 5
narrows.

---

## The gauntlet goes red in Phase 2, on purpose

    npx vitest run --root services/gateway --config vitest.integration.config.mts \
      src/isolation.itest.ts

Expect three failures the moment the union gains an eleventh member:

    derives all ten members from the union itself   expect(11) to be 10
    classifies every member exactly once            unclassified: [<the new type>]
    names no frame the union does not have

**This is the derived-list check firing on the build that adds a frame**, the same
instrument that catches a new route six times in three features. It is the plan working,
not the plan breaking.

---

## Running just this chapter's tests

    RELAY_POSTGRES_PORT=15432 npx vitest run --root services/gateway \
      --config vitest.integration.config.mts src/<file>.itest.ts

**There is a tenth integration file and it spawns no api.** Seven of nine already spawn
their own, and five of forty battery failures across chapter 3.20's two batteries were one
of those fixtures failing to come up — so the count that matters is seven, before and
after. `typing.itest.ts` follows `resume.itest.ts`: a stubbed `ApiClient`, two in-process
gateway instances, a real Redis.

---

## Before believing `check:errors`

    cd relay-platform && pnpm build
    cd ../relay-tutorial && pnpm check:errors

It reads `packages/protocol/dist/codes.js` — the **built** artifact. A stale `dist` makes
it green for the wrong reason. This chapter adds no close code, so the count must not move
from 17.

**And the five `check:*` scripts live in `relay-tutorial`, not in `relay-platform`.**
`pnpm` in the wrong repository exits without running anything and reads as green.

---

## The gate at every phase commit

    pnpm lint                    3.5 s
    pnpm typecheck               3.4 s
    pnpm turbo run test          5.9 s cold, 2.2 s warm, 11 packages

**The third was missing until analysis pass 18.** Pass 17 found `main.test.ts` red
from Phase 2 and invisible until Phase 11 because the first command that runs unit
tests was the CI-order block below. 100 gateway unit tests guard `session.ts`,
which five phases edit, and `resume.test.ts`'s suppression cases are the only
oracle for the seam chapter 3.6 got wrong.

## The gates, in CI's order

    set -o pipefail        # without it, $? after a pipeline is sed's

    pnpm lint
    pnpm typecheck
    pnpm turbo run test --force
    pnpm build
    node services/api/dist/db/migrate.js
    pnpm test:integration
    pnpm coverage
    pnpm test:outsider

`test:outsider` needs a **running** platform and starts nothing. It refuses with the five
commands that would satisfy it:

    RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d --wait
    export RELAY_DEMO_CREDENTIAL=$(node scripts/seed-demo-tenant.mjs)
    export RELAY_API_URL=http://localhost:4000 RELAY_WS_URL=ws://localhost:4001

**It is the only check that uses the public surface as a customer does** — and it has never
sent a frame. Zero `.send(` calls across eleven tests; the one socket test receives a
message that went over REST. This chapter adds an inbound frame, so T100a and T100b make
this file send one, and send a bad one.

---

## Before the battery

    RELAY_POSTGRES_PORT=15432 docker compose stop api gateway dispatcher

**Nothing else runs on the machine, and that includes editing a source file.** Chapter
3.20's first battery lost its homogeneity to a test written into `outbox.itest.ts` while it
was running — run 1 counted 700 tests and the rest 701.

Expect roughly 228.8 s per run against a 240 s budget, and expect failures: two twenty-run
batteries produced seven, in two mechanisms neither of which is new code. A recurrence of
either is expected rather than information; anything else is.
