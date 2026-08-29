# Data model — chapter 3.19, presence

**Nothing here is durable.** No table, no column, no migration. Two Redis keys and one
per-connection field, all of them derived and all of them expendable — constitution IV and
ADR-10: *"the correct amount of durability for typing dots and green circles is none."*

---

## Redis keys

| Key | Type | Value | TTL | Written by |
|---|---|---|---|---|
| `presence:{env}:{user}` | string | `1` — its **existence** is the state | `ttlMs` (30 s), refreshed every `refreshMs` (10 s) while any connection is open, and **re-pinned to `graceMs` at the last close**; the check runs `marginMs` after that | the instance that wins the `online` transition; refreshed by every instance holding a connection; re-pinned by the instance whose last local connection closed |
| `presence:offline:{env}:{user}` | string | `1` — an election marker | `ttlMs`, derived rather than hardcoded | the instance that wins the right to publish `offline` |

`{env}` is the environment id from the connection's identity; `{user}` is the external user id.
Both keys are environment-scoped, which the fan-out subject is not — the subject carries only a
channel id, because a channel id is already unique across tenants. Two scoping rules in one
module is the kind of asymmetry an isolation test should be pointed at rather than trusted.

### Why existence rather than a value

A key holding `"online"` and a key holding nothing are the same information, and existence is the
only form a TTL can express. It also makes the two operations that matter atomic and single-winner
without a script:

    SET presence:{env}:{user} 1 NX EX 30      -> OK  = this instance caused online, publish
                                              -> nil = somebody already has, stay quiet
    SET presence:{env}:{user} 1 XX EX 30      -> OK  = refreshed
                                              -> nil = the key vanished under a live connection

Measured against Redis 8.10.0, both branches, in research R2.

### Why the key is re-pinned at the close

`ttlMs` and `graceMs` are both 30 s, and that is **not** why the grace period works — it nearly broke
it. The key's expiry counts from the last refresh; the grace counts from the close. Those differ by
up to `refreshMs`, so a key set only by the refresh loop dies before the grace ends, and a
reconnection in that gap wins `SET … NX` and publishes a second `online` — which FR-007 forbids.

So `disconnected` issues one more command, **awaits it**, and only then starts the timer:

    SET presence:{env}:{user} 1 XX PX graceMs        awaited
    check scheduled at graceMs + marginMs            marginMs default 1_000

`XX`, so it never resurrects a key that is already gone. The key now dies when the grace ends, and
the check runs a margin after that.

**The margin and the ordering are a second fix, and the first fix is why they are needed.** Pinning
to `graceMs` and checking at `graceMs` puts both deadlines at the same instant by two different
clocks — the key expires at `close + δ + graceMs` where δ is the round trip, the timer fires at
`close + graceMs + ε`. With `ε < δ` the check finds the key alive, logs `presence.suppressed`, and
stops; the timer is one-shot, so the user stays online permanently. That is worse than the duplicate
`online` the pin was added to prevent. Contract §2.1 and research R2b have the full account. An instance that still holds a connection pushes it back to `ttlMs` on its next refresh, so
the multi-instance case is unaffected and the grace stays measured from the **last** close.

Found in analysis pass 1. The tests planned before it reconnected at a half and a third of the
window — both inside the key's life, where the bug is invisible.

### Why a second key for the offline election

Two instances whose last connections close in the same second both find the presence key absent
at `+graceMs` and would both publish. `SET … NX` on a separate marker gives exactly one of them
the right to speak. The `online` transition **deletes** the marker, so the next cycle can elect
again.

One key with a state value would need a compare-and-set, which means a Lua script. Two keys and
two `SET`s say the same thing in the vocabulary the rest of the platform already uses.

Its TTL is `ttlMs`, **derived from the configured timings**. A hardcoded 60 s would be two hundred
times the window in a test running a 300 ms grace, and correct only because the next `online`
deletes it — a constant that happens not to bite is still a constant nobody chose.

---

## The internal fabric payload

Published on `presence:{channel_id}`, consumed only by gateways, **never sent to a client**.

| Field | Type | Notes |
|---|---|---|
| `user` | string, min 1 | the subject's external user id |
| `state` | `"online" \| "offline"` | the same enum the published frame uses |
| `transition` | string, min 1 | a UUID the publisher mints, one per transition |

`transition` is why a watcher sharing three channels receives one frame. The publisher sends the
same payload on all three of the subject's presence subjects; a receiving instance delivers a
given `(transition, connection)` pair at most once.

**The wire frame is unchanged.** What reaches a client is exactly what chapter 1.3 published and
`frames.test.ts` asserts:

    { type: "presence.changed", payload: { user, state } }

This is the first time the internal fabric payload and the public frame are different shapes. On
the message path they are the same object, which is why `fanout.ts` could type its `publish` as
`Message` and get away with it.

---

## Per-instance in-memory state

| Where | Field | Lifetime |
|---|---|---|
| `presence.ts` | `seen: Map<transitionId, Set<connectionId>>` | cleared a few seconds after a transition arrives; all copies of one transition land within milliseconds |
| `presence.ts` | `pending: Map<userId, Timeout>` | one scheduled grace check per user, replaced rather than duplicated, armed at `graceMs + marginMs` **after** the re-pin resolves |
| `presence.ts` | `refresh: Timeout` | one interval per instance, not per connection |

`pending` is keyed by user and **replaced** on each new last-close, which is what makes the
close/reopen/close case inside one window resolve to a single decision answered by the state at
the end of the window. Two transitions inside one grace window must not leave two timers.

No new field on `Connection`. The registry gains a per-user lookup and nothing else — presence
asks "how many connections does this user have on this instance", and `all()` plus a filter
answers it on a set whose size is one instance's connections.

---

## The transition state machine

    absent ──connect, SET NX wins──> online ──last close, +graceMs, key absent, election won──> offline
       ▲                              │  ▲                                                        │
       │                              │  └── further connects: NX loses, no event                 │
       └──────────────────────────────┴── reconnect inside the window: no event at all ───────────┘

Six rows below, and three of them are silent:

| From | Event | To | Published? |
|---|---|---|---|
| absent | first connection anywhere | online | **yes**, once, by the NX winner |
| online | a further connection | online | no — the state did not change |
| online | a connection closes, others remain | online | no |
| online | last close, nobody returns within the grace period | offline | **yes**, once, by the election winner |
| online | last close, somebody returns within the grace period | online | no — this is the whole point of the grace period, and it holds for the whole window only because the close re-pins the key |
| online | the key vanishes under a live connection (Redis restart) | online | **yes**, a duplicate `online`. Permitted by ADR-10; better than a user who is online and unpublishable |

The channel set a transition publishes on is the closing or connecting connection's
`channelIds`, captured at the hook point. For `offline` that set is captured at close time and
held by the scheduled check — by the time it runs, the connection is out of the registry. It is
only ever used when no reconnection happened, in which case it is still the right set.

A subject who is a member of no channel publishes on no subject, so their transitions reach
nobody. Correct under FR-RTM-07, and worth a test precisely because "no frames arrived" is what a
broken producer also looks like.
