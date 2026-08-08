# Captured output — chapter 3.2

Everything the chapter quotes comes from here, and everything here came from a
run on 2026-08-08 against the compose stores. **Every credential below is
truncated or synthetic**: the walks print 18 characters and an ellipsis, and no
JWT body appears at all (spec SC-007, NFR-SEC-06).

---

## Lane counts

| Lane | Before (baseline.txt) | After |
|---|---|---|
| `pnpm test` (Docker-free) | 86 | **109** |
| `pnpm test:integration` | 60 | **76** |

New suites: `api-key.test.ts` (10), `user-token.test.ts` (12),
`credentials.itest.ts` (10), `gateway/session.itest.ts` (5). Existing suites
kept every assertion; `internal.itest.ts` gained one (a refused token) and
`session.test.ts` gained one (the api being unreachable closes 1011, not 4001).

---

## The invariants, as the runner prints them

```text
✓ src/auth/credentials.itest.ts > credentials > invariant 1: a key's secret is returned once and is unrecoverable afterwards
✓ src/auth/credentials.itest.ts > credentials > invariant 2: no credential is a 401 that names what the route expects
✓ src/auth/credentials.itest.ts > credentials > invariant 3: the wrong class is a 403 naming presented and expected
✓ src/auth/credentials.itest.ts > credentials > invariant 4: a foreign key sees nothing, and it looks exactly like absent
✓ src/auth/credentials.itest.ts > credentials > invariant 5: a revoked key is refused on the very next request
✓ src/auth/credentials.itest.ts > credentials > invariant 6: several active keys work at once, which is what rotation needs
✓ src/auth/credentials.itest.ts > credentials > invariant 7: a token is refused when expired, malformed, mis-signed, foreign, or over-long
✓ src/auth/credentials.itest.ts > credentials > invariant 9: the dev-token endpoint mints in development and does not exist in production
✓ src/auth/credentials.itest.ts > credentials > invariant 11: no credential appears in a log line or an error body
✓ src/auth/credentials.itest.ts > credentials > signup hands over exactly one key, and only when it creates something
Tests  10 passed (10)
```

Invariants 8 and 12 are pure and run in the unit lane (`user-token.test.ts`,
`api-key.test.ts`); invariant 10 needs a socket and runs in
`gateway/src/session.itest.ts`.

---

## The two refusals, verbatim

An end-user token presented to a route that wants an API key:

```json
{
  "code": "wrong_credential_type",
  "message": "this route expects an API key; an end-user token was presented",
  "docs_url": "https://relay.example/docs/errors/wrong_credential_type"
}
```

Nothing presented at all:

```json
{
  "code": "unauthorized",
  "message": "this route requires a credential: an API key or an end-user token, presented as \"Authorization: Bearer …\"",
  "docs_url": "https://relay.example/docs/errors/unauthorized"
}
```

Both name the class. Neither names the credential.

---

## `node scripts/credential-walk.mjs`

```text
api key (shown once)       rk_dev_2777b9f8ef4…
its prefix                 rk_dev_
POST with the key          201 seq=1
dev-token                  200 expires 2026-08-08T14:30:59.000Z
socket with the token      open as tuan
token → key-only route     403 wrong_credential_type
                           "this route expects an API key; an end-user token was presented"
key → socket               closed 4001

heard as tuan; both credentials worked, both refusals held.
```

---

## `node scripts/signup-walk.mjs` (quickstart V4)

```text
first authentication  → GET /auth/github/callback
    200 created=true
    organisation cc19528d-a1f7-4d16-b25a-e74b812922d1
    application  85184e51-c6e5-4b48-804a-a7a25687f4b7
    environment  98a995d7-fa28-442a-b67d-782ae08c002a (development)
     api key      rk_dev_f373520fba4… (shown once)

second authentication → GET /auth/github/callback
    200 created=false
    organisation cc19528d-a1f7-4d16-b25a-e74b812922d1
    application  85184e51-c6e5-4b48-804a-a7a25687f4b7
    environment  98a995d7-fa28-442a-b67d-782ae08c002a (development)
     api key      none — the secret was shown at creation and is gone
```

---

## The seam check (quickstart V3)

```console
$ grep -rn "x-relay-environment" services packages scripts --include=*.ts --include=*.mjs | grep -v itest
$ grep -rn "RELAY_DEV_JWT_SECRET\|DEV_JWT_SECRET" services --include=*.ts | grep -v test
$
```

No matches in either — not "only in comments". The comments that describe the
retired seam do so without quoting it, so the check needs no exclusions to come
back clean.

---

## The DI ordering measurement (T004, research R5)

```text
DIAG middleware
DIAG repository-factory
DIAG guard
```

Middleware runs before the request-scoped factory is constructed; the factory
still runs before the enhancer chain. Both facts, measured on this code path
rather than assumed from 2.6.

---

## The expiry finding (invariant 10)

An established socket outlives its token — and stops being able to write, because
the internal hop forwards that same token:

```text
✓ keeps an established connection alive past its token's expiry (invariant 10)
```

What the client is told when it tries:

```json
{
  "type": "error",
  "payload": {
    "code": "unauthorized",
    "message": "the token this connection was opened with has expired; reconnect with a fresh one to send again",
    "docs_url": "https://relay.example/docs/errors/unauthorized"
  }
}
```

Delivery is unaffected — fan-out never asks the api anything. This is FR-AUT-11's
first clause holding and its second clause (a refresh frame on the open
connection) being visibly absent.
