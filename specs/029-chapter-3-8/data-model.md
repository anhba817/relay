# Data model — chapter 3.8

Two stores, and which one holds what is the chapter's central decision rather than
a layout detail. One migration. No new table.

---

## Redis — the counters

### `rl:{environment_id}:{operation}:{window}`

One integer per environment per operation per window. `INCR` returns the new
count; `EXPIRE` is set only when the increment returns 1, so the key's lifetime is
its window and nothing accumulates.

| | |
|---|---|
| Value | integer, the number of operations counted in this window |
| TTL | the window length, set on the first increment |
| `operation` | `rest`, `send`, `connect` |
| `window` | the window's start, floored — makes the key self-expiring and the reset time computable without storing it |

**One request can touch two keys.** A `POST …/messages` increments `rest` by one and
`send` by the number of messages it carries, so the two counters answer different
questions: how much traffic, and how many messages. The response's headers describe
whichever has fewer remaining, because that is the one that will refuse first
(research R11).

**Not a source of truth** (constitution IV, SAD §6.3). Total loss means every
environment starts a fresh window and nobody is refused in the meantime. That is
the *designed* behaviour, not a tolerated one — see FR-010.

### `rlauth:{source_ip}:{window}`

The same shape keyed by source IP, counting authentication *failures* only. A
successful authentication does not increment it.

Separate key prefix rather than an `operation` value on the tenant key, because it
is keyed by something else entirely and because the two have opposite failure
behaviour. Sharing a prefix would invite sharing a code path.

**Cardinality is attacker-controlled**, which is why the in-process fallback that
mirrors this key is capped. See below.

**`source_ip` is the CLIENT's address, not the caller's.** A handshake authenticated
through the gateway arrives at the api from the gateway, so counting the caller
would put every customer's failures in one bucket and let one attacker exhaust a
threshold that then refuses everybody. The gateway forwards the client address on the
internal call and the api counts against that (research R14, FR-039). It is a field
on the internal contract rather than a header, because a header the caller asserts is
a header the caller can forge — the pattern chapter 3.2 removed.

---

## In-process — the fallback counter

Not a store, and listed here because it holds state that outlives a request.

| | |
|---|---|
| Shape | map from source IP to `{ count, windowStart }` |
| Lifetime | the process |
| Populated | only while the Redis store is unreachable |
| Cap | fixed maximum number of keys |
| On reaching the cap | stop admitting new keys |

**Stop admitting rather than evict.** An eviction policy on a map keyed by
attacker-controlled input is a policy the attacker drives: fill the map, evict the
entry that was counting them, start again. Refusing new keys degrades to "IPs we
are already tracking stay tracked", which is the safe direction.

The cap is the reason this structure is written down. An unbounded map keyed by
source IP is a memory-exhaustion vector, so the fallback that closes a
brute-force hole would open a worse one.

---

## Postgres — the policy

### `environments`, three nullable columns added

Migration `0008_limit_policy.sql`.

| Column | Type | Null means |
|---|---|---|
| `rest_limit_per_minute` | integer, nullable | use the default |
| `send_limit_per_minute` | integer, nullable | use the default |
| `connect_limit_per_minute` | integer, nullable | use the default |

**Nullable, and null is not zero.** A null column means "no override", resolved to
the documented default at read time. A zero would mean "refuse everything", which
must stay expressible — an environment can be turned off deliberately — so the
absent state and the refuse-everything state cannot share a representation.

**On `environments` rather than in a table of its own.** FR-RTL-04's independence
is per environment; the policy has exactly one row per environment, no history and
no versioning. A separate table would be a join for a value read on every request.

Constraints: each column, when present, must be non-negative.

### Defaults, from research R4

| Operation | Default per minute |
|---|---|
| `rest` | 600 |
| `send` | 600 |
| `connect` | 60 |
| failed authentication (per IP, not per environment) | 10 |

The auth threshold is **not** a column. It is not per environment — the caller has
not proved which environment they are — so it is configuration, not policy, read
from `RELAY_AUTH_FAILURES_PER_MINUTE` with a default of 10.

**The default enforces.** Chapter 3.6's `RELAY_DISABLE_SWEEP` carries the rule: a
flag whose default disabled a requirement would be a requirement nobody had built.
A suite that deliberately submits bad credentials raises the threshold explicitly;
the limiter's own suite lowers it, which is the only way to test a threshold
(research R15).

### Reaching the gateway

The gateway has no database client and must not gain one. `connect_limit_per_minute`
and `send_limit_per_minute` travel on the **internal authentication response** it
already requests at the upgrade, and are held on the `Connection` for its lifetime —
beside the `marks` chapter 3.7 put there, and dying with the socket for the same
reason (research R12).

The consequence is a real property: a limit changed while a socket is open does not
reach that socket until it reconnects. The alternative is a Postgres read per frame,
on the hot path of the thing the limit protects.

---

## Postgres — the notification obligation, unchanged

### `webhook_disable_notifications`

Chapter 3.6 built this table and this chapter adds **no column**. It is already an
outbox: a row per obligation, and a `delivered_at` that is null until the
obligation is met.

| Column | This chapter's use |
|---|---|
| `organisation_id` | the recipient scope, resolved at send time (FR-022). Denormalised by 3.6 so an application moving between organisations cannot retarget a notification already owed elsewhere — this chapter is the first code that depends on it |
| `endpoint_id`, `run_started_at`, `run_attempts`, `last_status`, `last_error` | the email's contents |
| `delivered_at` | **set by this chapter.** Null throughout 3.6, above a comment saying whichever chapter builds a transport will set it |

**The claim predicate is the whole design**: `delivered_at IS NULL`, ordered
oldest first, `FOR UPDATE SKIP LOCKED`. FR-019 (never twice) and FR-020 (drain the
backlog) both fall out of it — the rows accumulated since 3.6 are undelivered work
by the predicate's own definition and need no special handling.

**Scoped, not global.** The claim takes a limit, and chapter 3.7's baseline is why
this is worth stating: four test suites broke because a global unscoped operation
was asserted against a local row. The tests here assert on rows they created.

---

## Recipient resolution

Not stored. Computed at send time.

```text
organisation_id  →  memberships (role IN ('owner','admin'))  →  humans.email
```

**`humans.email` is nullable**, so the empty result is a real branch. FR-023
requires a notification that cannot be addressed not be marked delivered and the
condition be visible — so "no addressable admin" is an outcome with a log line and
a test, not a defensive `if` that silently marks the row.

---

## Infrastructure inventory

Mailpit joins `INFRA_SERVICES` in `@relay/config` — the constant that names the
local infrastructure so nothing has to parse YAML — and gets a healthcheck in the
shape the other four stores use.

It adds **no** entry to `DURABLE_VOLUMES`. It holds messages in memory, and the
reason is the one the Redis entry already records: a store that is not a source of
truth does not need a volume, and giving it one invites somebody to depend on it.

---

## What is deliberately absent

- **No quota counters.** FR-RTL-05's units are messages sent, unique active users
  and connection-minutes, which is FR-ANL-05's metering, which arrives with Part
  4's analytical store. Building them here means building them twice.
- **No `notification_attempts` table.** A webhook attempt log exists because a
  customer is owed evidence about their endpoint (3.6, FR-WHK-06). Nobody is owed
  evidence about our own outbound email, and `delivered_at` plus a log line answers
  the operational question.
- **No connection registry.** `conn:{env}:{user}` is FR-RTM-09's and presence's;
  limiting connection *establishment* needs a counter, not a registry.
- **No stored reset timestamp.** It is derivable from the window in the key, and
  storing a value two instances could disagree about is how `Retry-After` becomes
  wrong. This is also what closes the clock-skew edge case by construction rather
  than by two processes agreeing.
- **No record of which limit a response reported.** Recomputed per request from two
  integers already in hand. Storing it would be a third piece of state to keep
  consistent with the two it derives from.
