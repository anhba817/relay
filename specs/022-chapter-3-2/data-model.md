# Phase 1 — Data Model: Chapter 3.2

One new table, one amended function, and two shapes that exist only in memory —
the principal and the token claims. Everything persisted here sits **below** the
tenant boundary 3.1 drew, which is why every row carries an environment.

> **Provenance.** `docs/04-srs.md` states the requirements (FR-AUT-01…12,
> NFR-SEC-02) but no document defines a key table. Its shape is therefore a
> **chapter derivation**, recorded as a DECISION in the schema, the same way 2.1
> recorded `members` and 3.1 recorded the tenancy containers.

---

## `api_keys` (new)

An application's credential for exactly one environment (FR-AUT-01).

| Field | Type | Notes |
|---|---|---|
| `id` | uuid, PK | app-generated, like every other id |
| `environment_id` | uuid, not null → `environments(id)` | the tenant column: this table is below the boundary, so it has one (FR-TEN-06) |
| `public_id` | text, not null | the indexed lookup half of the credential — not a secret |
| `secret_hash` | text, not null | salted SHA-256 of the secret half; the secret itself is never stored (FR-AUT-02, NFR-SEC-02) |
| `salt` | text, not null | per key, so two identical secrets never share a hash |
| `prefix` | text, not null | `rk_dev_` or `rk_live_`, mirroring the environment kind (FR-AUT-03) |
| `name` | text, nullable | a human label ("CI", "staging box"); absent for the key signup mints |
| `created_at` | timestamptz, not null, default now | |
| `last_used_at` | timestamptz, nullable | updated on use; useful for spotting a key nobody rotated |
| `revoked_at` | timestamptz, nullable | non-null means refused from that moment (FR-AUT-05) |

| Constraint | Purpose |
|---|---|
| `UNIQUE (public_id)` | the lookup must resolve to at most one key, globally, because authentication happens before any tenant scope exists (R2) |
| `CHECK (prefix IN ('rk_dev_','rk_live_'))` | FR-AUT-03's two prefixes, and nothing else |

**Rules**

- **Several active keys per environment are legal** — that is what makes rotation
  possible without downtime (FR-AUT-04). Nothing constrains the count.
- **Revocation is a timestamp, not a deletion.** A deleted row loses the audit
  trail of what once had access; a `revoked_at` keeps it and still refuses the
  credential on the next request (FR-AUT-05).
- **`prefix` duplicates information** derivable by joining the environment's
  kind. It is stored anyway so the credential can be reconstructed for display
  and matched against its environment without a join — and so a mismatch between
  prefix and environment kind is detectable rather than assumed.

### The credential as a string

```
rk_dev_<public_id>_<secret>
└──┬──┘└────┬────┘ └──┬───┘
   │        │          └─ 32 random bytes, base64url. Shown once. Hashed at rest.
   │        └─ 16 random bytes, base64url. Indexed. Not a secret.
   └─ FR-AUT-03's visible prefix: which environment kind am I about to hit?
```

Presented as a bearer credential (FR-AUT-01). The parts are split on the last
separator, so nothing breaks if base64url output contains one.

---

## `provisionOrganisation` (amended, 3.1's function)

Signup now mints the environment's first key inside the same transaction and
returns its plaintext once (R8). The row count per outcome changes from five to
six for a new identity, and from four to five for a known one — which is the sort
of number the chapter's tests assert, so it is stated here rather than left to be
rediscovered.

**Rule**: the returned secret is the only time it exists outside a hash
(FR-AUT-02). If the caller loses it, the recovery is a new key, not a lookup.

---

## `principal` (in memory, per request)

What authentication produces. Never persisted.

| Field | Type | Notes |
|---|---|---|
| `kind` | `"application" \| "user"` | which credential was presented; decides what the request may do (FR-AUT-10) |
| `environmentId` | string | resolved from the credential, never from a header — this is what replaces the retired seam |
| `keyId` | string, only when `kind = "application"` | for `last_used_at` and for quota accounting in 3.6 |
| `userExternalId` | string, only when `kind = "user"` | the token's subject |

**Rules**

- The principal is the *only* source of tenant scope after this chapter. The
  request-scoped repository reads `principal.environmentId`; nothing reads a
  header.
- A request with no credential has no principal, and routes that require one
  refuse before any handler runs.

---

## End-user token claims (in memory, verified)

Signed with the environment's `signing_secret` using HS256 (FR-AUT-06).

| Claim | Required | Rule |
|---|---|---|
| `sub` | yes | the end user's `external_id` in that environment |
| `env` | yes | the environment the token is for; a token presented against another environment is refused (FR-AUT-08's "issued for a different application") |
| `iat` | yes | issued-at |
| `exp` | yes | expiry; `exp - iat` may not exceed 24 hours (FR-AUT-07) |

**Rules**

- Verification names its algorithm explicitly. A verifier that accepts whatever
  the token's header claims is the algorithm-confusion vulnerability, and it is
  the chapter's TRAP candidate.
- Claims are checked *after* the signature, and the environment claim decides
  which secret to check the signature with — so the lookup is by claim, the trust
  is by signature.
- Nothing here is stored. Tokens are not a table; they are an assertion the api
  re-verifies every time it sees one (R7).

---

## What the model deliberately does not have

- **No sessions table.** No human session exists in this chapter (R11), and 3.1's
  forward reference to the contrary gets corrected.
- **No token blocklist.** Tokens are short-lived by construction (FR-AUT-07);
  revoking one before expiry would need state this chapter does not build, and no
  requirement asks for it.
- **No key-scope or permission columns.** FR-AUT-10 distinguishes two classes,
  not per-key scopes; adding a permission model nothing asks for is exactly what
  Principle VII forbids.
- **No cache table or column.** Revocation is immediate because verification is
  live (R7).
