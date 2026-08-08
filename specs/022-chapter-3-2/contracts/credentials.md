# Phase 1 — Contracts: Chapter 3.2

Every public route changes in one respect: the environment comes from a verified
credential rather than from a header the caller asserted. The internal seam
narrows — the gateway stops declaring who its user is and starts being told.

---

## How a credential is presented

```
Authorization: Bearer rk_dev_<public_id>_<secret>     # an application
Authorization: Bearer <jwt>                            # an end user
```

One header, two classes, told apart by the `rk_` prefix (FR-AUT-03). Nothing is
accepted from a query string: URLs end up in logs and referrers, and NFR-SEC-06
forbids credentials in either.

**The retired seam**: `x-relay-environment` is no longer read anywhere. A request
that still sends it is not rejected for sending it — it is simply ignored, and
refused for having no credential, which is the honest failure.

---

## Public routes

### `POST /v1/channels/:channelId/messages` · `GET /v1/channels/:channelId/messages`

**Accepts**: either class (R6). The environment comes from the principal.

| Status | Meaning |
|---|---|
| 200 / 201 | as before |
| 401 | no credential, or a credential that does not verify |
| 403 | `wrong_credential_type` — the class presented cannot use this route |
| 404 | the channel does not resolve **in the credential's environment** — indistinguishable from a channel that does not exist (FR-TEN-05) |

The 404 case is the one worth stating: presenting environment A's key against
environment B's channel must look exactly like asking for a channel nobody has.

### `POST /auth/dev-token`

FR-AUT-09. Mints an end-user token from an API key so a developer reaches a first
message before implementing token signing.

**Accepts**: an application credential, **and only in a `development`
environment**.

**Body**: `{ "user": "<external id>", "ttl_seconds": <optional, ≤ 86400> }`

| Status | Meaning |
|---|---|
| 200 | `{ "token": "<jwt>", "expires_at": "<RFC 3339>" }` |
| 400 | missing user, or a TTL over 24 hours (FR-AUT-07) |
| 401 / 403 | no key, or an end-user token presented instead |
| 404 | the environment is `production` — the endpoint does not exist there |

**Why 404 and not 403 in production**: the route is not a permission the caller
lacks, it is a development affordance that does not exist in production. A 403
would invite someone to look for the permission.

### `GET /auth/:provider/start` · `GET /auth/:provider/callback`

Unchanged from 3.1, and still credential-free: they establish identity. The
callback's 200 body gains one field — the first key's secret, shown exactly once
(R8, FR-AUT-02):

```json
{
  "organisation": { "id": "…", "name": "…" },
  "application":  { "id": "…", "name": "…" },
  "environment":  { "id": "…", "kind": "development" },
  "api_key":      { "prefix": "rk_dev_", "secret": "rk_dev_…", "shown_once": true },
  "created": true
}
```

`api_key` is present only when `created` is `true`. A returning owner is not
handed a new secret, and the old one is unrecoverable by design — the recovery is
rotation, not retrieval.

---

## The internal contract (gateway → api)

### `POST /internal/session` (new; replaces `GET /internal/memberships`)

The gateway sends the token it was given and is told who the caller is. It no
longer asserts an identity it verified locally (R1).

**Request**: `{ "token": "<jwt>" }`

**200**:
```json
{
  "environment_id": "…",
  "user": "<external id>",
  "channel_ids": ["…"]
}
```

| Status | Meaning |
|---|---|
| 200 | verified; identity and memberships in one answer |
| 401 | expired, malformed, mis-signed, wrong environment, or a lifetime over 24 hours (FR-AUT-08, FR-AUT-07) |

**Why one call and not two**: the gateway already made exactly one internal call
at connect (2.5's memberships lookup). Verification returns the same information
plus the identity, so the connect path's round-trip count is unchanged — the
gateway simply stops being the thing that decides who you are.

`POST /internal/messages` and `POST /internal/backfill` keep their shape and 2.5's
recorded trust model: network-internal, service-to-service credentials still Part
3 hardening. What changes is that the identity headers they receive now originate
from the api's own verification rather than from the gateway's assertion.

---

## The WebSocket upgrade

**Accepts**: an end-user token only, on the existing `?token=` query parameter
(EIR-WS-05's shape, unchanged since 2.5).

| Close code | When |
|---|---|
| 4001 | the token does not verify — expired, malformed, mis-signed, wrong environment, over-long lifetime |

**Two things that do not change**: the token still arrives in the query string,
because a browser cannot set headers on a WebSocket upgrade — and this is the one
place a credential legitimately appears in a URL, which the chapter should say out
loud rather than leave as an apparent contradiction of NFR-SEC-06. And an
established connection is never torn down because its token aged out
(FR-AUT-11's first clause): verification happens at connect.

**What retires**: `RELAY_DEV_JWT_SECRET`. The gateway holds no signing secret
after this chapter.

---

## Error bodies

EIR-API-04's envelope, unchanged in shape. One code joins the registry:

| Code | Meaning |
|---|---|
| `wrong_credential_type` | the class presented cannot use this route; the message names what was presented and what was expected |

Example message: `this route expects an API key; an end-user token was presented`.

**The rule the message follows**: name the *class*, never the credential.
"`rk_dev_abc…` is not valid" is how a live secret reaches a support ticket, and
NFR-SEC-06 forbids exactly that.

---

## Invariants the tests must hold

| # | Invariant | Requirement | Lane |
|---|---|---|---|
| 1 | A key's secret is returned once and is not recoverable from storage | FR-AUT-02, NFR-SEC-02 | integration |
| 2 | No credential → 401 naming what the route expects | spec FR-013 | integration |
| 3 | Wrong class → 403 `wrong_credential_type`, message names presented and expected | FR-AUT-10, spec FR-013 | integration |
| 4 | A key for environment A cannot see environment B's data, and the answer matches "absent" | FR-TEN-05 | integration |
| 5 | A revoked key is refused on the next request, no waiting | FR-AUT-05 | integration |
| 6 | Several active keys work at once (rotation with no downtime) | FR-AUT-04 | integration |
| 7 | A token is refused when expired, malformed, mis-signed, for another environment, or with `exp - iat` > 24 h | FR-AUT-06/07/08 | unit + integration |
| 8 | Verification accepts only HS256 — an `alg: none` or asymmetric-`alg` token is refused | FR-AUT-06 | unit |
| 9 | The dev-token endpoint mints a usable token in development and 404s in production | FR-AUT-09 | integration |
| 10 | An established socket survives its token's expiry | FR-AUT-11 | integration |
| 11 | No credential appears in any log line or error body | NFR-SEC-06 | integration |
| 12 | The prefix matches the environment kind (`rk_dev_` ↔ development) | FR-AUT-03 | unit |
