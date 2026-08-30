# Quickstart — chapter 3.20

*How to run what this feature builds, and what to look at. Prerequisites first, because two of
them cost half an hour each when they are wrong.*

---

## The environment, before anything is measured

This machine's own PostgreSQL holds 5432, so the stack goes on 15432 and every command below
depends on it:

```bash
cd relay-platform
RELAY_POSTGRES_PORT=15432 docker compose up -d --wait     # --wait, or suites race readiness
DATABASE_URL=postgres://relay:relay@localhost:15432/relay \
  node services/api/dist/db/migrate.js                    # needs pnpm build first
```

`--wait` matters and so does the store count: **five containers, not four.** Mailpit is one of
them and a lane without it fails on `ECONNREFUSED :8025`.

The nine variables the lane needs are pinned in `baseline.txt`. Chapter 3.19 discovered them one
red run at a time; do not rediscover them.

**Stop the services profile before any coverage or timing run**, and stop it the right way:

```bash
docker compose stop api gateway dispatcher      # NOT --profile services down
```

`docker compose --profile services down` removes the stores and the network too — a profile
*widens* the set `down` acts on. Chapter 3.19 lost the whole stack to that once.

---

## Seeing the thing that is broken

Before any of this feature exists, the violation is already asserted in the tree:

```bash
cd relay-platform/services/gateway
npx vitest run --config vitest.integration.config.mts -t "FR-RTM-10"
```

One test passes. It is titled *"keeps delivering to a member who was REMOVED while connected"*,
it waits out the clause's own 5,500 ms, and it asserts that the frame FR-RTM-10 forbids **does**
arrive. Its closing comment is the instruction this chapter follows: *"change this to `.rejects`
on the day a re-read exists."*

---

## Watching a removal, by hand

Two gateway instances on one Redis is what the cross-instance cases need, and no suite outside
this feature's own stands up two.

```bash
# the fabric, watched directly — neither module's code, which is the point
docker compose exec redis redis-cli PSUBSCRIBE 'member:*'
```

Then, in another shell, remove a member over the public route and watch one publish on
`member:{channel_id}` carry both audiences. For an addition, watch **two** publishes: the channel
subject tells the existing members, the user subject reaches an instance that is not subscribed to
that channel at all.

The subscription count is the declared cost and it is measured, not asserted:

```bash
docker compose exec redis redis-cli CONFIG RESETSTAT
# ...run the membership suite...
docker compose exec redis redis-cli INFO commandstats | grep -E 'subscribe|publish'
```

Chapter 3.19's reading for two instances over three channels was `cmdstat_subscribe calls=12`.
The prediction here is 18 plus one per connected user per instance — and the prediction is not the
measurement.

---

## The durable half, which is not on the fabric at all

Every membership write now carries an outbox row in the **same transaction** — constitution II
forbids publish-after-commit without one, and the Redis publish beside it is the lossy live path.
Neither `addMember`, `removeMembers` nor `banUser` had a transaction before this chapter, so each
one had to be created.

```bash
# the rows accumulate: the lane runs with RELAY_OUTBOX_RELAY=off, so nothing drains them
DATABASE_URL=postgres://relay:relay@localhost:15432/relay psql -c \
  "select subject, count(*) from outbox group by 1 order by 2 desc"
```

`channel.member_added` and `channel.member_removed` are FR-WHK-02's spelling, not this chapter's.
**Two of that clause's eight names gain producers here and no endpoint subscribes to them** — the
rows exist because the publish requires them, and the webhook chapter becomes a wiring job rather
than a re-plumbing job.

## The suites

```bash
cd relay-platform
pnpm --filter @relay/gateway test:integration            # the membership suite lives here
pnpm --filter @relay/protocol test                       # the subject grammar, pure
pnpm test:integration                                    # the full lane, 240 s budget
```

**The gateway package's own wall clock is the number to watch, and the model matters.** Chapter
3.19 left the lane at 228.18 s mean against 240, and 45.09 s of that is the gateway package —
which is one file, because 28 cores run all eight in parallel and the package's clock is its
slowest. So a ninth file **under** 45 s adds almost nothing to the lane; one **over** 45 s becomes
the pacesetter and every second it spends is a lane second. The budget for this feature's file is
40 s, checked after US1 rather than at close-out — and **about 18 s of it is waiting**. Three negative assertions each need FR-RTM-10's own five-second window, and unlike every timing in chapter 3.19 this one cannot be injected shorter: it is a clause, not a constant. Share one window across them where the fixtures allow.

**Do not spawn a seventh api.** Six of the gateway's eight integration files already start their
own api process, vitest runs files in parallel, and chapter 3.19's battery lost run 10 to a
90-second hook timeout when one boot did not finish. Share the fixture.

---

## The gates

```bash
cd relay-platform && pnpm lint && pnpm typecheck && pnpm turbo run test --force && pnpm build
node services/api/dist/db/migrate.js
pnpm test:integration && pnpm coverage

cd ../relay-tutorial
pnpm check:fences && pnpm check:docs && pnpm check:figures && pnpm check:srs && pnpm check:errors
```

That is CI's order (`.github/workflows/ci.yml:96-110`), and the order matters in one place:
`check:errors` reads `packages/protocol/dist/codes.js`, the **built** artifact, so a stale `dist`
makes it green for the wrong reason.

**The five `check:*` scripts live in `relay-tutorial`.** Running `pnpm check:fences` from
`relay-platform` exits silently and reads as green.

---

## What to look at when it does not work

| Symptom | Look first at |
|---|---|
| a removal delivers nothing to anybody | the fixture's user names — chapter 3.19 lost two tests to `watcher` where the fixture says `linh` |
| a removal cuts off a second local member too | the reference count: decrement, never release (research R6) |
| the removed user gets no final frame | the ordering — FR-008 is send-then-cut, and cut-then-send is the natural way to write it |
| an addition delivers nothing | the user-addressed subject. The channel subject cannot reach an instance that is not subscribed to the channel |
| a red lane run reporting ~1m43s | not a measurement. Turbo stops after the api package fails; that is the time to fail |
| `signup.itest.ts` failing on a route it never touched | `/internal/memberships` came back. That suite asserts it refuses |
| **the removed member got a message *after* the notice** | the resume buffer. `flushable(buffer, marks)` filters on `frame.seq` and not on membership, so a removal mid-resume unsubscribes the channel and then flushes what was already buffered (FR-029). **Nothing else in the feature looks wrong when this happens** — the membership path did its job correctly |
| the removed member got no notice at all, only silence | the notice went into that same buffer and FR-029's filter dropped it. The frame reads neither `phase` nor `marks` (FR-030) |
| a presence frame arriving with `type: "membership.changed"` | four subject shapes share one Redis. The topology keeps them apart and FR-033 is what asserts it |
| the mechanism looks dead in the logs on a healthy run | there is a `membership.published` line and it is the only evidence the working path leaves (FR-031). Three names, no fourth |
| a webhook consumer sees a membership event twice, or never | the outbox row, not the publish. It is written **inside** the membership transaction — if it is beside one, a crash between them loses the event silently |
