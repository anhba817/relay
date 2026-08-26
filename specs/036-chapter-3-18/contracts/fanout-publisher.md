# Contract — the api's fan-out publisher

## The shared grammar (moves to `packages/protocol`)

    export function subjectFor(channelId: string): string   // `chan:${channelId}`

Moved verbatim from `services/gateway/src/fanout.ts`, exported from `packages/protocol`'s index.
The gateway imports it instead of defining it; nothing about the string changes, so **no existing
subscription should change behaviour** — only import paths.

**`DEFAULT_REDIS_URL` stays where it is, in all three places it already lives** (`api/src/limits/
store.ts:44`, `gateway/src/fanout.ts:27`, `gateway/src/limits.ts:22`). Consolidating one of three
copies into a shared package is worse than leaving three, and a connection URL is not protocol.
The api's publisher reads `RELAY_REDIS_URL` the way `limits/store.ts:86` already does, so this
feature adds no configuration.

**No re-export from `gateway/src/fanout.ts`.** One name for one thing: the gateway's consumers —
including `fanout.itest.ts:8`, whose single import line splits in two — take it from
`@relay/protocol`. A re-export would leave two paths to the same function and make the move
cosmetic.

## The api's interface

    export interface MessagePublisher {
      publish(message: Message): Promise<void>;
      close(): Promise<void>;
    }

Two methods. The gateway's `Fanout` has five (`onDelivery`, `publish`, `subscribe`, `unsubscribe`,
`close`); the api never subscribes and never delivers, so it takes none of those three. One ioredis
client, not two — the two-client rule exists because a *subscribed* connection cannot issue
ordinary commands, and this one never subscribes.

## Client options — different from the gateway's, deliberately

    lazyConnect: true
    maxRetriesPerRequest: 0
    connectTimeout: 1_000
    redis.on("error", () => {})

Copied from `services/api/src/limits/store.ts`, not from `createFanout`. The reason is in that
file: on the request path, a dead Redis that waits out a retry schedule turns every send slow
rather than merely undelivered, and NFR-PRF-02 asks for p95 < 150 ms. The error listener is not
optional — without it ioredis emits `error` on an EventEmitter with none attached.

**`createFanout` has neither the options nor the listener** (R10). Do not treat it as the reference
implementation for this one.

### And the down-window, which is the half that matters

The four options above were `limits/store.ts`'s **first** version, and that file says so:

    FAILING OPEN IS NOT FREE IF IT FAILS SLOWLY, and the first version of this file was
    slow. With the store gone, every command waits out its connect timeout before giving
    up — so each request paid a second or more, twice.

    So a known-down store is not retried on the request path. The first failure opens a
    window; while it is open every call answers `null` immediately, which is the same
    signal the caller already handles. One probe per window is what notices the store
    coming back.

So the publisher carries the window too, not only the options:

    const DOWN_WINDOW_MS = 5_000;
    let downUntil = 0;
    // publish(): if (Date.now() < downUntil) return;   — no attempt, no wait
    //            on success: downUntil = 0
    //            on failure: downUntil = Date.now() + DOWN_WINDOW_MS, and log

**The blast radius makes this concrete: 47 send-message calls across 8 api integration suites**
will publish once this ships. With a dead Redis and no window, each pays the connect timeout —
about a second apiece against NFR-PRF-02's 150 ms budget. With the window, the first send in every
five seconds pays it and the rest return immediately.

An earlier draft of this contract copied the options and not the window, which is to say it copied
the bug and left the fix.

### Lifecycle

    close(): Promise<void>   — called from a `…Lifecycle implements OnModuleDestroy`

`limits/limits.module.ts:10` states the convention: *"resource in this api closes through
`OnModuleDestroy`"*, and six modules implement it — webhooks, limits, notifications, outbox,
consumer, quotas. `CounterStoreLifecycle` (`limits.module.ts:26`) is the one to copy, because it
closes the analogous Redis client. **A `close()` nothing calls is a leaked handle in an api that
boots once per integration suite.**

### Module boundary

Provide the publisher in `MessagesModule`; **do not export it.** `internal.module.ts:31` imports
`MessagesModule` and, in its own words, *"reuse[s] MessagesModule's providers wholesale"* — so an
exported publisher is injectable from the internal route, the one path that must never publish
(FR-006). `MessagesModule` already does this with `"DB"`: *"provides 'DB' but does not export it"*
(`internal.module.ts:26`). FR-006 then holds by module boundary rather than only by where the call
sits.

## Behaviour

### `publish` never rejects

    try { await redis.publish(subjectFor(message.channel), JSON.stringify(message)) }
    catch  { logger.log("error", "fanout.publish_failed", { channel, error }) }

Same contract as the gateway's, same log event name. A caller cannot distinguish a failed publish
from a successful one, and that is intended: delivery is allowed to fail because the message is
already durable and resume will find it.

**Consequence for tests, stated here because it is a contract property and not an implementation
detail:** any test whose only assertion is "the send returned 201 while Redis was down" is
satisfied by a publisher that does nothing at all. The observable difference is the log line.

### When the api publishes, and when it does not

Two guards, mirrored from `session.ts:651`, both load-bearing:

| condition | why | requirement |
|---|---|---|
| the send committed a new row (not a recognised retry) | a client retrying on a flaky link would otherwise put the same message on every member's screen twice | FR-006 |
| `text !== null` | a tombstone recovered by an old idempotency key is not a creation | FR-007 |

And one the gateway never needed:

| the send was not refused | the gateway publishes only for sends it accepted itself; the api's publish site sits after a call that may throw | FR-008 |

FR-008's shape follows from where the publish goes: on the success path, not in a `finally`. A
`finally` would publish after a `403`.

## Ordering — the contract REST cannot inherit

`docs/05-sad.md:254` fixes it: *"Ack after commit, never before (FR-MSG-05). The Redis fan-out
happens after the ack; a recipient may see the message milliseconds after the sender's ack, never
before durability."* The gateway performs it literally — `send(socket, message.ack)` and *then*
`await fanout.publish(...)`, with a comment naming the sequence.

**A request handler has no such seam.** The response is the ack, and anything the handler awaits
happens before the response is written. So the api has two choices:

| | publish before the response | detach the publish |
|---|---|---|
| ordering as written | inverted — recipients may see it before the sender's `201` | preserved |
| the guarantee that ordering protects | **held** — the commit precedes both | held |
| lands in | NFR-PRF-02 (write, p95 < 150 ms) | NFR-PRF-01 (ack → receipt, p95 < 250 ms) |
| FR-011's failure observable | yes, synchronously | only by racing the response |

**Decision: publish before the response, awaited.** The sentence's actual guarantee is *"never
before durability"*, and that holds either way; what the literal reading protects is a measurement
convention, not a correctness property. Awaiting is what makes the failure testable, and a Redis
`PUBLISH` against a live server is sub-millisecond against a 150 ms budget — a number the chapter
must measure rather than assert.

The cost, recorded rather than hidden: **NFR-PRF-01's clock — "send acknowledged to recipient
receipt" — cannot be read literally on the REST path**, because a recipient may receive before the
sender is acknowledged. The interval is measurable on the socket path and is not on this one. That
is the second documented order this feature finds unachievable as written, and both come from the
same cause: the documents were written when the socket was the only way in.
