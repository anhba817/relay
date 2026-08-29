# Quickstart — validating chapter 3.19

How to see presence work, and how to see each requirement fail if it were broken. Commands only;
the code lives in `tasks.md` and the implementation.

---

## 0. The environment, before anything is measured

**Bring the stores up, and stop the app containers.** `baseline.txt` requires the `services`
profile stopped for `pnpm test:integration` and — since chapter 3.18 — for `pnpm coverage` too.

**Assume neither state.** During this feature's research all three app containers were running;
an hour later `docker ps` was empty and Postgres on 15432 refused the connection, which is how a
task's command failed while the task list was being written. So bring the stores up first and
stop only the profile:

```bash
cd relay-platform
docker compose up -d postgres redis nats clickhouse   # the stores, whatever was running before
docker compose --profile services down                # api, gateway, dispatcher
docker compose ps                                     # confirm what you actually have
```

**Confirm the ports rather than trusting a comment.** Two fenced test files instruct
`RELAY_REDIS_PORT=16379`, which is an override from chapter 1.2 and not what a plain
`docker compose up -d` produces (research R13).

```bash
docker compose port redis 6379                   # -> 0.0.0.0:6379 unless you overrode it
docker exec relay-redis-1 redis-cli PING         # -> PONG
```

**After a `docker compose down -v`, run the lane twice and believe the second.** The first run
after cold volumes fails; nothing creates JetStream state on purpose (chapter 3.18's `gaps.md` item 3).

---

## 1. The failing state, before any code

The point of phase 1. This must show that nothing produces a presence frame today.

```bash
cd relay-platform
pnpm --filter @relay/gateway test:integration -t "presence"
```

Expected before the feature: **no such test**, and after phase 1's first task: a red test
asserting a watcher receives `presence.changed` when a co-member connects. If it passes before
phase 3, something else is producing presence and the whole premise needs re-reading.

Also worth running once, to see the grammar that already exists:

```bash
pnpm --filter @relay/protocol test -t "presence"
```

Chapter 1.3's `frames.test.ts` already asserts the frame's shape and rejects `state: "away"`.

---

## 2. Watch it by hand

Two gateways, one Redis, three terminals. This is the exercise the sealed outsider does and the
one no checker in this repository can do — chapter 3.18's `gaps.md` item 6, carried by five chapters.

```bash
# terminal 1
cd relay-platform && pnpm --filter @relay/api dev

# terminal 2 — instance A
PORT=4001 pnpm --filter @relay/gateway dev

# terminal 3 — instance B, same Redis, no knowledge of A
PORT=4002 pnpm --filter @relay/gateway dev
```

**`PORT`, not `RELAY_PORT`.** `services/gateway/src/main.ts:97` reads
`Number(process.env.PORT ?? 4001)` and nothing reads `RELAY_PORT`; an earlier draft of this
quickstart used the latter, which would have put both gateways on 4001 and killed the second with
`EADDRINUSE`. The two-instance walk is the one exercise an outsider runs, so the command has to be
the one that works.

Connect a watcher to A and the subject to B, with two user tokens that share a channel. What must
happen:

| Do this | See this |
|---|---|
| subject connects to B | watcher on A receives one `presence.changed` `{ state: "online" }` |
| subject opens a second socket to A | **nothing** — the state did not change |
| subject closes one of the two | **nothing** |
| subject closes the last one, waits ~31 s | watcher receives one `offline` — never before 30 s, and a `marginMs` after it |
| subject closes and reconnects at 10 s | **nothing at all**, to anybody |
| a user sharing no channel connects and watches | **nothing**, while the co-member above still receives |

The fourth row is the only one that costs wall-clock time by hand. In the suite it costs
milliseconds, because `presenceGraceMs` is an option (research R4).

---

## 3. The suites

```bash
cd relay-platform
pnpm --filter @relay/protocol test                    # the payload schema, the union's totality
pnpm --filter @relay/gateway test                     # transitions, guards, the 30_000 default
pnpm --filter @relay/gateway test:integration         # one Redis, two instances, the grace period
pnpm test:integration                                 # the whole lane
```

Reading the count needs the colour codes stripped. Every parse of it in chapter 3.18 returned
zero, including all 22 runs of its timing battery:

```bash
NO_COLOR=1 FORCE_COLOR=0 pnpm test:integration | sed -r 's/\x1B\[[0-9;]*[mK]//g' | tail -20
```

**Budget:** 607 tests and 195 s at chapter 3.18's close-out, against 240 s. 45 s of headroom.

**Record the close-to-`offline` delay while the suite runs.** SC-005 asks for an upper bound this
feature measured, not one it estimated; the number belongs in `baseline.txt` beside the lane
timings.

---

## 4. Prove the failure path is a path

The trap this feature inherits, stated as a command. With Redis down, a presence implementation
that does nothing at all passes every "the socket still opened" assertion.

```bash
docker compose stop redis
pnpm --filter @relay/gateway test:integration -t "presence.*redis"
docker compose start redis
```

Two things must be true, and only the second one distinguishes a working path from an absent one:

1. The socket opens, the handshake completes, messages still deliver.
2. **One `presence.failed` log event exists**, and after Redis is back the next transition
   publishes without a restart.

---

## 5. The gates

All five live in `relay-tutorial`. `pnpm` in the wrong repository exits silently and reads as
green.

```bash
cd relay-tutorial
pnpm check:docs        # docs/ vs content/docs — reads divergence, not correctness
pnpm check:srs         # id uniqueness; its own comment says it does not read meaning
pnpm check:figures
pnpm check:fences      # replays every titled fence onto relay-platform
pnpm check:errors      # reads packages/protocol/dist/codes.js — BUILD FIRST
```

```bash
cd relay-platform && pnpm build      # before check:errors, or it is green for the wrong reason
```

The fence predecessor is commit **`caeabc9`** in `relay-platform` — a commit, not the tag
`part3-ch18`. Chapter 3.18's `chapter-notes.md` T065 section records that nothing fenced was
amended after it.

---

## 6. What none of this proves

- **That the chapter can be read.** Every check here compares bytes.
  `specs/036-chapter-3-18/reader-protocol.md` is the runnable version — one engineer who has not
  read the specs, 45 minutes, six questions — and it needs a second person. Chapters 3.14 through
  3.18 each named this and none closed it.
- **That the fan-out cost is acceptable at scale.** ADR-10's revisit trigger is presence fan-out
  above roughly 30% of gateway publish volume. The lane's largest membership set is five channels.
- **That a 5% flake is absent.** Twenty green runs reject a per-run failure rate above 13.91% at
  95% confidence and nothing finer; rejecting a 5% flake needs 59 runs.
