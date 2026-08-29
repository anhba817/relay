# Contract — the presence lifecycle

**Scope:** the module's interface, its options and their defaults, and the ordering the session
layer owes it.

---

## 1. Interface

    export interface Presence {
      /** Set by the session layer at wiring time, as the fan-out's is. */
      onTransition(handler: (channelId: string, payload: PresenceFabric) => void): void;

      /** A connection opened. May publish `online`; publishes nothing if the
       *  user was already online anywhere. */
      connected(user: string, channelIds: Iterable<string>): Promise<void>;

      /** A connection closed and the caller has already removed it from the
       *  registry. When it was the user's last connection on this instance:
       *  re-pins the key to `graceMs`, **awaits that**, then schedules one check
       *  at `graceMs + marginMs`, replacing any pending one for that user.
       *  The re-pin and that ordering are both load-bearing — see §2.1. */
      disconnected(user: string, channelIds: Iterable<string>): Promise<void>;

      subscribe(channelId: string): Promise<void>;
      unsubscribe(channelId: string): Promise<void>;
      close(): Promise<void>;
    }

    export function createPresence(options: PresenceOptions): Presence

**Two pure helpers are exported beside it**, and they exist because the module builds its own Redis
clients from a `url` and therefore cannot be stubbed. Everything reply- or clock-dependent that still
needs a unit test gets factored out to here — the shape `limits.ts` already uses for `overLimit` and
`windowStartFor`:

    export function wonTransition(reply: string | null): boolean      // "OK" -> true, null -> false
    export function graceCheckDelay(graceMs: number, marginMs: number): number

Both were added by remediation rather than by the first draft, and neither reached this section until
a later analysis pass asked which identifiers lived only in the task list.

The shape `fanout.ts`, `limits.ts` and `meter.ts` share: a factory returning an interface, with
the delivery callback registered by the session layer rather than passed in.

## 2. Options and defaults

| `PresenceOptions` | Default | Why this number |
|---|---|---|
| `graceMs` | `30_000` | FR-RTM-06 says 30 seconds. **This default is asserted by a test**, so the clause is not represented solely by a constant. |
| `ttlMs` | `30_000` | `docs/05-sad.md:575`. Must be `>= graceMs` and must exceed `refreshMs` with room to spare — see §2.1. |
| `marginMs` | `1_000` | How long after the grace ends the check runs. Not padding: without it the key's expiry and the check are the same instant reached by two clocks, and a tie strands the user online permanently (§2.1). Overridable so a millisecond-scale test is not swamped by a one-second margin. |
| `refreshMs` | `10_000` | Three refreshes per TTL, so two consecutive misses do not expire a live user. **Not** the ping loop's 30_000 — a TTL equal to its refresh interval expires a connected user (research R3). |
| `url` | `process.env.RELAY_REDIS_URL ?? DEFAULT_REDIS_URL` | The same resolution `fanout.ts` uses. |
| `logger` | required | NFR-OBS-01. |

**Two names for each, and the mapping is the one the meter already uses.** The module's options are
unprefixed because the module is the scope; the session layer's are prefixed because
`SessionServerOptions` already holds three other intervals:

    SessionServerOptions          PresenceOptions
    presenceGraceMs        ->     graceMs
    presenceTtlMs          ->     ttlMs
    presenceRefreshMs      ->     refreshMs
    presenceMarginMs       ->     marginMs

`session.ts` does exactly this for chapter 3.11 — `createMeter({ …, intervalMs: meterIntervalMs })`, at `:168` in the tree at `caeabc9`.
An earlier draft of this contract called all three by their module names at the session layer while
the task list called two of them by their prefixed names; the pair disagreed on three identifiers,
and the task list asserts those defaults *by name*, so a mismatch is a failing test rather than a puzzle.

The reason they are overridable at all is the one already written above `pingIntervalMs` in `session.ts`: an interval is
a contract, not a constant the tests should have to wait out. Without them the grace-period cases
cost 30 seconds each against 45 seconds of lane headroom.

## 2.1 The close re-pins the key, and the check runs after it — both are load-bearing

**Found in analysis pass 1, before implementation.** The key's expiry and the grace check are driven
by two clocks that start at different events:

    key expires at   last_refresh + ttlMs
    grace ends at    close        + graceMs

With `ttlMs == graceMs`, the key dies *before* the grace ends by exactly `close - last_refresh`,
which is anywhere in `[0, refreshMs)`. A reconnection landing in that gap finds the key absent, wins
`SET … NX`, and publishes a **second `online`** for a user who never went offline — which FR-007
forbids in as many words: *"A reconnection inside the grace period MUST publish nothing — neither an
`offline` nor a repeated `online`."*

**The fix is at the close, not in the numbers.** `disconnected` pins the key's remaining life to the
grace window:

    SET presence:{env}:{user} 1 XX PX graceMs

`XX` so it cannot resurrect a key that is already gone. The key then dies exactly when the grace
ends, so every reconnection inside the window finds it alive and publishes nothing. An instance that
still holds a connection for that user pushes the TTL back to `ttlMs` on its next refresh, at most
`refreshMs` later, so the multi-instance case is untouched and the grace stays measured from the
**last** close.

**No test in the first task list could have caught this**: the reconnect cases land at a half and a
third of the window, and the gap only opens after `ttlMs` has lapsed. The reconnect-late case is now
its own task.

`ttlMs >= graceMs` remains the sane default, but **it is not what makes this correct** — the re-pin
is. An earlier draft of this section was titled as though the numeric relation were the mechanism,
and one task then asserted that relation as an enforced invariant while another had to violate it to
open the gap deliberately. A test may set `ttlMs` below `graceMs`; nothing refuses to start over it.

### The second defect, which the first fix created

Pinning to `graceMs` and checking at `graceMs` sets **two deadlines to the same instant, reached by
two different clocks**:

    key expires at    close + δ + graceMs      δ = time for the SET to reach Redis
    check fires at    close     + graceMs + ε  ε = timer lateness, >= 0 and often ~0

When `ε < δ` the check runs while the key is still alive, `EXISTS` returns 1, the branch logs
`presence.suppressed` — and **stops**. The timer is one-shot and its `pending` entry is rewritten
only by the next close, so the `offline` is not late: it never happens. FR-004 is a MUST, and this
breaks it permanently, where the defect it replaced produced a spurious duplicate `online`. Redis
also holds a key alive until `now` is strictly past its expiry, so a tie falls on the wrong side.

**Two changes, and neither is sufficient alone:**

1. **`await` the re-pin before scheduling the check.** The timer then starts after Redis holds the
   new TTL, so `δ` sits inside the wait instead of racing it.
2. **Check at `graceMs + marginMs`.** This breaks the tie and absorbs timer granularity. Publishing
   later is compliant — FR-004 bounds the delay from below only — and SC-005 records the observed
   figure rather than the nominal one.

The ordering alone leaves the equality; the margin alone still races a `SET` that has not been sent.

**The margin has a residual, and it is the accepted one.** A reconnection landing in the `marginMs` window — after the grace ends, before the check runs — finds the key expired, wins `NX`, and publishes `online`; the check then sees the key present and suppresses the `offline`. Observers get two `online` frames with no `offline` between them, for at most `marginMs`. That is the same cosmetic class ADR-10 already permits, it is bounded by an option rather than unbounded, and FR-031 names it. Removing it would need the reconnect to cancel a pending timer on another instance, which is a coordination problem this design exists to avoid.

`presence` itself is **optional** on `SessionServerOptions`, for the reason `fanout`, `limits` and
`meter` are: chapter 2.5's tests and a single-process dev run have no Redis, and a socket server
that refused to start without one would be a worse default than a presence-less one. `main.ts`
always supplies it.

## 3. Ordering the session layer owes

    after  registry.add(connection)        ->  presence.connected(...)
    after  registry.remove(connection.id)   ->  presence.disconnected(...)

Anchored on the statements, not on line numbers. This feature edits `session.ts` five times before
the second of these lands, so any line number written here is wrong by the time it is used.

**Both calls come after the registry mutation, and for opposite-looking reasons.** `connected`
needs the new connection counted; `disconnected` needs the closing one gone, because it asks
whether this was the user's last local connection.

This is the third ordering constraint in the same close handler. The meter is told **before**
`registry.remove` — a socket that opened and closed between two reports would otherwise be counted
zero, which is the one thing the wall-clock-minute unit was chosen to charge. Presence is told
**after**. A future edit that "tidies" the handler by grouping the two notifications breaks one of
them silently.

**Owed test:** swapping `registry.remove` and `presence.disconnected` must fail. Not a taste
assertion — with the order reversed, the closing connection is still in the registry, the local
count is 1 rather than 0, and no grace check is ever scheduled. The user stays online forever.

## 4. Failure behaviour

| Failure | Required behaviour |
|---|---|
| Redis unreachable at connect | The socket opens, the handshake completes, one structured log event. FR-023, FR-024. **Tested with a dead port** (`redis://127.0.0.1:1`), never by stopping the compose container — the gateway's integration files run in parallel and stopping Redis breaks the other seven. |
| Redis reachable again | The next transition publishes **without a restart**: ioredis reconnects on its own, which is what makes this evidence the path was alive rather than evidence a fresh client works. A dead port cannot be restored, so the test drives an in-process TCP proxy in front of the real Redis and closes and re-listens it. |
| The re-pin fails (Redis unreachable at close) | The check is still scheduled and still runs. The key then expires on whatever TTL the last refresh left — *earlier* than the grace, never later — so the `offline` publishes on time or marginally early, never not at all. The failed pin is one `presence.failed` line. |
| Redis unreachable at close | The close handler does not throw. It is already documented as the last place that should throw, and chapter 2.8's lane found the unhandled rejection during teardown that the subscribe path had guarded and the release path had not. |
| `SET … XX` returns nil under a live connection | Treat as a new transition: publish `online` again. A duplicate for a user who never left, permitted by ADR-10. |
| The instance dies inside the grace window | Nothing publishes `offline`. Watchers hold a stale green circle until the subject next transitions. Stated in the chapter, not discovered. |
| Two instances' grace checks race | The election marker `presence:offline:{env}:{user}` is set `NX PX ttlMs` — **derived from the configured timings, not a hardcoded 60 s**. A test running a 300 ms grace would otherwise carry a marker 200 times longer than its own window, correct only by accident because the next `online` deletes it. |
| A payload fails to parse on receipt | One log line, no frame. |

**Every one of these is a path where doing nothing looks like success.** The assertion that
carries each requirement is the log line, and the test that proves the path was alive is the one
that restores Redis and watches the next transition publish. Chapter 3.18's `gaps.md` names this
trap against its own publisher: `publish` swallows its errors and resolves, so "the send returned
201 with Redis down" is true of a publisher that does nothing at all.

## 5. Logging

| Event | Fields | When |
|---|---|---|
| `presence.published` | `user`, `state`, `channels` (count) | a transition was published |
| `presence.suppressed` | `user`, `state`, `reason` | the NX guard or the election lost, or a reconnection cancelled a grace check |
| `presence.failed` | `user`, `op`, `error` | any Redis operation on the presence path failed |
| `presence.invalid_payload` | `subject` | a received payload failed to parse |

No message content and no token, ever (constitution VI). `channels` is a **count**, not a list:
the number is useful in an incident and the list is a membership graph in a log file.
