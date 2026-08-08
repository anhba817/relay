# Phase 1 — Contracts: Chapter 3.1

Two HTTP routes and one internal provisioning contract. Both HTTP routes are
**unauthenticated by nature** — they exist to establish who someone is — and
neither carries `x-relay-environment`, because no tenant exists yet. Every
existing route keeps its `EnvironmentContextGuard`; the guard is applied per
controller, so the new controller simply does not use it.

---

## `GET /auth/:provider/start`

Begins the authorization-code flow.

**Path params**: `provider` — `github` in this chapter; unknown providers are a
404, not a redirect (never bounce a browser somewhere on unvalidated input).

**Behaviour**
1. Mint a random `state` (128 bits, from `crypto`).
2. Set it in a cookie: `httpOnly`, `SameSite=Lax`, `Path=/auth`, `Max-Age` 600,
   `Secure` when not in development.
3. Redirect (302) to the provider's authorize URL with `client_id`,
   `redirect_uri`, `scope`, and the same `state`.

**Responses**
| Status | Meaning |
|---|---|
| 302 | redirect to the provider |
| 404 | unknown provider (1.4's error envelope) |

---

## `GET /auth/:provider/callback`

Completes the flow and provisions on first arrival.

**Query params**: `code` (required), `state` (required); a provider error
response may arrive as `error` instead.

**Behaviour**
1. **Verify the binding first**: the `state` query value must equal the cookie
   value, and the cookie must exist. A mismatch or a missing cookie is a 400 —
   before any network call, because an unverified callback must never cause the
   server to talk to the provider on an attacker's behalf.
2. Clear the state cookie.
3. Exchange `code` at the provider's token endpoint; validate the response with
   zod (an access token, or a provider error object).
4. Fetch the profile from the provider's user endpoint; validate with zod.
5. Provision (see below) and return what exists now.

**Responses**
| Status | Meaning |
|---|---|
| 200 | signed up (or recognised); body below |
| 400 | missing/mismatched `state`, missing `code`, or a provider-side error |
| 502 | the provider answered something the contract does not allow |

**200 body**
```json
{
  "organisation": { "id": "…", "name": "…" },
  "application":  { "id": "…", "name": "…" },
  "environment":  { "id": "…", "kind": "development" },
  "created": true
}
```

`created` reports whether **an organisation was created on this call** — not
whether the identity was new. A returning owner gets `created: false`; a known
human who owned nothing gets `created: true`, because an organisation really
was created for them. The response reports what happened rather than hiding it,
because the caller here is the account's owner — unlike the *public* wire, where
2.3 deliberately hides a retry.

**What the body does not contain**: no API key (3.2), no session token (R9),
no signing secret ever.

---

## Provisioning contract (repository admin surface)

Grows `createEnvironment`'s role in `services/api/src/db/repository.ts`. The
signature the module depends on:

```
provisionOrganisation(db, {
  provider, providerAccountId, displayName, email, organisationName
}) → { organisation, application, environment, human, created }
```

**Guarantees**
1. **Atomic** — one transaction; a failure at any step leaves no rows
   (spec FR-008).
2. **Idempotent on the OWNED organisation** — the operation ensures the
   identity owns exactly one organisation, which resolves every reachable
   case without ambiguity:

   | State of the identity | Result |
   |---|---|
   | unknown `(provider, provider_account_id)` | create all five rows (human, organisation, application, environment, membership); `created: true` |
   | known, and holds an `owner` membership | return that organisation; create nothing; `created: false` |
   | known, but holds only non-`owner` memberships | create four rows — organisation, application, environment, `owner` membership — reusing the existing human; `created: true`; existing memberships untouched |

   The third row is unreachable until invitations exist (a later chapter),
   but the rule is stated now because "return the existing organisation" is
   undefined for a human who belongs to someone else's — and FR-TEN-07 makes
   that state legal the moment membership management arrives. Signing up
   gives you *your own* workspace; it never silently hands you someone
   else's.
3. **Complete** — when an organisation is created, everything it needs exists:
   organisation, application, `development` environment and `owner` membership,
   plus the human row when the identity is new (FR-TEN-02). Five rows for a new
   identity, four for a known one — the full set for the call, or none at all.
4. **Not tenant-scoped, and openly so** — this is the admin surface, the one
   place that creates tenants; everything else in the file still requires an
   `environment_id` (Principle I).

---

## Configuration contract

| Variable | Purpose | Default |
|---|---|---|
| `RELAY_OAUTH_GITHUB_CLIENT_ID` | provider app id | unset — start returns 404 when absent |
| `RELAY_OAUTH_GITHUB_CLIENT_SECRET` | provider app secret | unset |
| `RELAY_OAUTH_GITHUB_AUTHORIZE_URL` | authorize endpoint | GitHub's |
| `RELAY_OAUTH_GITHUB_TOKEN_URL` | token endpoint | GitHub's |
| `RELAY_OAUTH_GITHUB_USER_URL` | profile endpoint | GitHub's |
| `RELAY_OAUTH_REDIRECT_BASE` | public base for `redirect_uri` | `http://localhost:4000` |

The three endpoint URLs are configurable so the test lane can point at a local
stand-in (R8) and so a real deployment can point at GitHub Enterprise. Secrets
are runtime configuration only — never a build argument, never in an image
layer, and the chapter repeats that rule when it introduces them.

---

## Invariants the tests must hold

| # | Invariant | Requirement | Lane |
|---|---|---|---|
| 1 | The full set for the call, or none — five rows for a new identity, four for a known one | spec FR-008 | integration |
| 2 | Second authentication creates no second organisation | spec FR-010, FR-TEN-01 | integration |
| 3 | A third environment is refused | FR-TEN-04, spec FR-009 | integration |
| 4 | Two organisations cannot see each other's containers or messages | FR-TEN-05 | integration |
| 5 | A callback whose `state` does not match the cookie is refused before any provider call | R7 | unit |
| 6 | A provider response that breaks the contract is a 502, not a crash | contract above | unit |
| 7 | Provisioning is reachable only through the signup path — no controller outside `tenancy/` and no request-scoped provider exposes the admin surface | spec FR-011, Principle I | integration |
