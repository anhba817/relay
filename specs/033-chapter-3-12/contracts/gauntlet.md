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

## 3. The internal surface — two credential classes, two attacks

An earlier version of this contract had one, and gave three of the eight routes an attack
that does not apply to them.

### The three that take an end-user token

`@Accepts("user")` — the credential **is** scoped to one environment, so the attack is a
foreign credential, the same shape as the socket surface.

```
POST /internal/messages     a token minted in A, a channel in B
POST /internal/session      a token minted in A, a resume cursor naming B's channel
POST /internal/backfill     a token minted in A, a channel in B
```

### The five that take a platform credential

`@Accepts({ platform: [...] })` — the credential carries no environment and names one per
request, so the attack is a request that names one environment and carries an identifier
from another.

```
POST /internal/usage/connections   environment A, a connection first seen in B
POST /internal/dispatch/expand     environment A, an event in B
POST /internal/dispatch/material   environment A, a delivery in B
POST /internal/dispatch/outcome    environment A, a delivery in B
POST /internal/dispatch/replay     a dead letter belonging to B
```

The last one is unscoped **by design** — `replayDeadLetter(db, id)` takes an id and no
environment, because the dispatcher legitimately serves every tenant. That is the
distinction this section has to keep visible: unscoped by design is not the same as
unscoped by accident, and only the second is a defect.

`POST /internal/usage/connections` already refuses with `409
connection_environment_conflict`; chapter 3.11 treated a connection changing tenants as a
correctness question rather than a data-quality one, and the gauntlet generalises that
judgement to the other four.

### And a third attack, on the credential rather than the request

Until this chapter, a route could say *which class* may call it and not *which service*.
`Accepts` took `...kinds: PrincipalKind[]`, both platform credentials resolved to
`{ kind: "platform", service }`, and `service` was documented "for logs" — so the
gateway's credential reached every dispatch route, including `replay`. Two secrets stopped
the services sharing a secret; they still shared a surface.

```
gateway credential    → POST /internal/dispatch/*        must be refused
dispatcher credential → POST /internal/usage/connections must be refused
```

Both directions, route by route. The refusal is a `403` naming the class and not the
credential, by the rule `credential.guard.ts` already follows for a wrong credential class.

**What still protects a platform credential, after this change.** The network boundary,
the secret's confidentiality, and now the route's declared service list. What does not:
rotation, which does not exist, and `service`, which is self-reported by which variable
matched rather than proven. The change narrows which routes a leaked credential reaches;
it does not make a leak survivable, and the chapter says so.

## 4. The socket surface

Gateway in process, api as a child (`services/gateway/src/isolation.itest.ts`).

| Attack | Assertion |
|---|---|
| connect with a token minted for A | `channel_ids` contains nothing belonging to B |
| send into a channel belonging to B | refused; B's channel gains no message |
| resume from a cursor naming B's channel | no backfill from B |
| subscribe to B's channel | nothing delivered |

**The inbound list is a classification, not a derivation**, because the package has no
direction to derive. `frameSchema` is one discriminated union of ten members with no
inbound/outbound metadata anywhere. So each of the ten is assigned a direction with a
reason, and a totality check runs in both directions against the union — every member
classified, every entry naming a real member. A new frame then fails the suite until
somebody classifies it, which is the property that was wanted, obtained the way §1 obtains
it for routes.

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
- **A leaked platform credential.** §3 narrows which routes each service may call. It
  does not make a leak survivable: there is no rotation, and `service` is self-reported by
  which variable matched.
- **Routes that are unscoped by design.** The four dispatch routes reach every tenant
  because the dispatcher serves every tenant. The suite checks who may call them, not
  whether they should exist.
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
