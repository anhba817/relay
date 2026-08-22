# Contract — the gauntlet

What the suite promises, how it derives what it attacks, and — at the end, deliberately
not summarised away — the list of things it does not cover. Constitution I makes a build
that fails this suite unshippable, which is a promise about sensitivity, not existence.

## 1. Derivation

```
targets = app.getHttpAdapter().getInstance().router.stack
            .filter(layer => layer.route)
            .flatMap(layer => methodsOf(layer.route).map(m => ({ method: m, path: layer.route.path })))
```

**Three assertions before any attack runs**, because every one of them fails silently
otherwise:

| Assertion | The failure it prevents |
|---|---|
| `targets.length > 0` | express renames its router property (`router` in 5, `_router` in 4) and the suite attacks nothing while passing |
| `POST /v1/channels/:channelId/messages` ∈ targets | the derivation finds *some* routes but not the mounted ones |
| every target matches exactly one classification entry, and every entry matches a target | a new route is unattacked; a renamed route leaves a stale exemption behind |

The derivation is not the router's public API and the plan says so. The mitigation is
that a wrong derivation is loud rather than empty.

## 2. The five shapes and their attacks

For every target the suite issues a **pair** of requests, because indistinguishability
cannot be observed from one response.

### `read`

```
A: GET /v1/webhooks/{id belonging to environment B}     with A's key
B: GET /v1/webhooks/{a uuid that exists nowhere}        with A's key
assert equal(status), equal(body minus request_id)
```

### `list`

```
A: GET /v1/webhooks     with a key for an environment that owns nothing
assert 200, an empty page, and no row belonging to any other environment
```

A list's correct answer to "nothing of yours here" is an empty page. A suite that
asserted 404 across the board would be wrong about this shape and would freeze today's
status choices into a test.

### `write`

```
before = read the target tenant's rows directly
A: POST /v1/webhooks/{B's id}/disable     with A's key
B: POST /v1/webhooks/{nowhere}/disable    with A's key
after  = read the same rows directly
assert equal(status), equal(body minus request_id), before == after
```

The state read is the point. A 404 that completed the write is the nightmare case and no
status code reveals it.

### `credential`

```
A: POST /auth/dev-token  with environment A's key, user "u"
   → use the returned token against environment B's channel
assert the token is refused
```

No identifier is involved. This shape exists because `POST /auth/dev-token` takes no
tenant-owned id and is nonetheless tenant-scoped — the specification's four shapes would
have filed it as exempt, which is how a route stops being attacked.

### `exempt`

`GET /healthz` takes nothing. `GET /auth/:provider/start` and `/callback` take a
provider name and a browser cookie. Each carries a written reason; `because` is a
required field, so nothing is exempt by omission.

## 3. The internal surface

`RELAY_INTERNAL_CREDENTIAL` is **not scoped to an environment**, by design: one gateway
and one dispatcher serve every tenant and each names the environment in the request. So
the attack is not a foreign credential — it is a request that names one environment and
carries an identifier from another.

```
POST /internal/messages          environment A, a channel in B
POST /internal/backfill          environment A, a channel in B
POST /internal/session           a token for A, a resume cursor naming B
POST /internal/dispatch/expand   environment A, an event in B
POST /internal/dispatch/material environment A, a delivery in B
POST /internal/dispatch/outcome  environment A, a delivery in B
POST /internal/dispatch/replay   environment A, a delivery in B
POST /internal/usage/connections environment A, a connection first seen in B
```

The last one already refuses, with `409 connection_environment_conflict` — chapter 3.11
treated a connection changing tenants as a correctness question rather than a
data-quality one, and this suite generalises that judgement to the other seven.

**What the suite therefore does not test, stated because a green result would imply
otherwise:** the internal credential itself. A holder of that secret can act for any
tenant, which is what it is for. What contains it is the network boundary and the
secret's own confidentiality — not a scope, and not this suite.

## 4. The socket surface

Gateway in process, api as a child (`services/gateway/src/isolation.itest.ts`).

| Attack | Assertion |
|---|---|
| connect with a token minted for A | `channel_ids` contains nothing belonging to B |
| send into a channel belonging to B | refused; B's channel gains no message |
| resume from a cursor naming B's channel | no backfill from B |
| subscribe to B's channel | nothing delivered |

Inbound frame types are derived from `@relay/protocol`'s frame union rather than typed
out, so a new inbound frame appears in the attack list. The union has ten members today
and only some are inbound; the outbound ones are listed as not-attackable with a reason,
by the same rule as `exempt`.

## 5. The structural half

Behaviour is tested above; this is the shape. For every base table in `public`:
`environment_id`, or exactly one foreign key to a table that has it, or membership of
an explicit list with a reason. Twelve, two and eight today. There is deliberately no
fourth class: a table fitting none of the three is a finding, and a bucket kept open to
receive it is how a finding turns into a classification.

## 6. Sensitivity — what the suite has been shown to catch

A suite that has never failed is an untested test. Three reintroductions, run by hand,
reverted, each recorded with the assertion that fired:

| Reintroduction | Expected to fire |
|---|---|
| drop `environment_id` from one repository `SELECT` | a `read` pair's body comparison |
| drop it from one `UPDATE` | a `write` pair's before/after comparison, **not** its status |
| change one 404 to a 403 | a `read` pair's status comparison |

**And what stays green is part of the result.** Three faults chosen by the person who
wrote the suite measure sensitivity to three faults, not coverage of the class. The
chapter records which assertions did not fire and what that means.

## 7. What this contract does not cover

Enumerated rather than summarised, because a defence trusted past its range is worse
than none — feature 030's rule, applied to its own successor.

- **Timing.** A foreign id answering in 3 ms and an absent id in 30 ms is a disclosure
  this suite cannot see. Measuring it stably in CI is a different discipline and is not
  attempted; the chapter names it as unaddressed rather than implying otherwise.
- **The internal credential's holders.** See §3.
- **Error-message content beyond equality.** The pair proves the two answers match; it
  does not prove that what they say is wise. A constant message that leaks a schema
  detail would pass.
- **Anything not routed through the HTTP router.** A future direct-socket admin surface,
  a CLI, a cron job reading across environments — none appear in `router.stack`.
- **Storage-level leaks with no endpoint.** The structural check finds a missing tenant
  column; it does not find a query that ignores the one that is there. That is what the
  behavioural half is for, and the two halves are not the same claim.
- **The guard's blind spots that remain.** Nine tables watched after this chapter, out
  of 22. `outbox` cannot be watched at all — the trigger condition is
  `__is_sentinel(OLD.environment_id)` and there is no such column — and it should not be:
  its legitimate mutation is the relay's cross-environment sweep, so a guard over it
  would refuse the thing it exists to permit.
- **Retention.** The structural check sees a missing tenant column. It does not see a
  table that keeps message text for ever, which is what the outbox turned out to be
  doing (R7a). Nothing in this contract measures how long data lives.
