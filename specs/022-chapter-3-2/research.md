# Phase 0 — Research: Chapter 3.2, Keys and Tokens

Checked against the repository at the `part3-ch1` state, not assumed. Sources:
`docs/04-srs.md` (FR-AUT-01…12 and the design note beneath them, NFR-SEC-02/06,
FR-TEN-05, EIR-API-04), `docs/05-sad.md` (ADR-04, ADR-05, §8), the constitution
(Principles I, V, VI, VII), and the current code.

---

## R1 — How the gateway verifies a token without touching the database

**Decision**: it doesn't verify anything itself. The gateway sends the token to
the api, and the api answers with the identity and the memberships in one
response. That call **replaces** the existing `GET /internal/memberships` the
gateway already makes at connect, so the connect path gains no round trip.

**Rationale**: ADR-05 says the gateway never touches Postgres, and end-user
tokens are signed with a per-environment secret that lives there. The two
candidate designs are "ship the secret to the gateway" and "ask the owner to
verify". Shipping a signing secret to a second service multiplies the places it
can leak, needs an invalidation story the moment it rotates, and puts a
tenant-scoped secret inside a process that deliberately holds no tenant state.
Asking the api costs one HTTP hop that the connect path was already paying.

**Consequence**: the gateway stops asserting identity on the internal hop. Today
it sends `x-relay-environment` and `x-relay-user` headers it invented from a
locally-verified dev token; after this chapter it sends the token itself and is
*told* who the caller is. The internal seam gets narrower, not wider.

**Alternatives considered**: gateway-side verification with a cached secret
(rejected: secret sprawl, rotation story, ADR-05's spirit); a shared asymmetric
key so the gateway verifies a public half (rejected: FR-AUT-06 fixes HS256, and
introducing a second algorithm to avoid one HTTP call is a bad trade).

---

## R2 — Finding a key without knowing the tenant

**Decision**: the key is two parts — a public, indexed lookup id and a secret —
formatted `rk_dev_<public_id>_<secret>`. Authentication looks the row up by
`public_id`, then compares the presented secret against the stored hash in
constant time.

**Rationale**: authentication has to happen *before* a tenant scope exists,
which inverts the rule every other query in the repository follows. Hashing the
whole credential would leave nothing to look up and force a scan of every key in
the system; a lookup id keeps the query a single indexed hit while the secret
stays unrecoverable at rest. The visible prefix (`rk_dev_`, `rk_live_`) is
FR-AUT-03's requirement and is not a secret — it exists so a human can tell at a
glance which environment they are about to point at production.

**Alternatives considered**: hash-only with a table scan (rejected: O(keys) per
request); truncated-hash bucketing (rejected: complexity for no gain over an
explicit id); storing the secret encrypted rather than hashed (rejected:
FR-AUT-02 and NFR-SEC-02 both say hash, and nothing needs to read it back).

---

## R3 — Which hash

**Decision**: SHA-256 over a per-key random salt plus the secret, using
`node:crypto`, compared with `timingSafeEqual`. No password-hashing KDF.

**Rationale**: this is the one place where the boring choice is *not* bcrypt or
argon2. Those exist to make guessing **low-entropy human passwords** expensive.
A key secret here is 256 bits of `randomBytes` — an attacker cannot guess it at
any work factor, so a KDF's deliberate slowness buys nothing and is paid on
every authenticated request instead. NFR-SEC-02 asks for a salted hash, which
this is. Worth a WHY box, because "use bcrypt for everything" is exactly the kind
of received wisdom that is right for passwords and wrong here.

**Alternatives considered**: bcrypt/argon2 (rejected above, and each adds a
native dependency); unsalted SHA-256 (rejected: identical secrets would produce
identical hashes, and the salt costs one column).

---

## R4 — JWT: use `jose`, do not hand-roll

**Decision**: add `jose` to the api service as a runtime dependency, pinned to
the `^6.2.7` the workspace already resolves, and verify with an explicit
algorithm allow-list.

**Rationale**: the api must both verify end-user tokens and, for FR-AUT-09's
development endpoint, mint one. Hand-rolling HS256 is thirty lines and three
classic vulnerabilities: algorithm confusion (accepting `none` or an asymmetric
`alg` the verifier then mishandles), forgetting to check `exp`, and comparing
signatures with `===`. Chapter 2.5 already brought `jose` into the workspace for
exactly this job on the gateway side, and it is already in the lockfile — so this
adds a dependency to one package's manifest, not to the project.

**Trade-off, stated plainly**: chapter 3.1 claimed zero new dependencies and
kept that claim by typing an express response structurally. This chapter spends
a dependency deliberately, and the difference is the subject matter: a response
type is a convenience, token verification is security code.

**Consequence**: `services/api/package.json` changes, and three published
chapters fence that file — so the amendment is a hunked diff fence, which is the
normal mechanism. (Contrast 3.1's deferred coverage tooling, where the *tool* was
not the chapter's subject.)

**Alternatives considered**: hand-rolled HMAC (rejected above; the chapter says
why, which is more useful than the code); `jsonwebtoken` (rejected: `jose` is
already here and is the maintained modern option).

---

## R5 — Where authentication runs, given 2.6's DI finding

**Decision**: authenticate in **middleware**, put the resolved principal on the
request, and let the request-scoped `Repository` factory read it — but verify the
ordering empirically before building on it, exactly as 2.6 did.

**Rationale**: chapter 2.6 discovered that Nest resolves request-scoped providers
*before* the enhancer chain, which is why 2.2's factory reads the header itself
rather than trusting a guard to have run. That finding constrains this chapter:
authentication now involves an async database lookup, and a guard would still run
too late for the factory. Middleware runs earlier than guards in Nest's pipeline,
and the api already has one (`RequestContextMiddleware`, from 1.4), so the seam
exists.

**To verify first (implementation task 1)**: a diagnostic that logs the order of
middleware execution versus request-scoped factory construction. If middleware
also runs too late, the fallback is to make the factory itself `async` and
resolve the principal there — uglier, because a factory that throws produces a
poor error shape, so the guard would then exist only to convert that into
EIR-API-04's envelope. The plan does not pretend to know; it schedules the
experiment.

**MEASURED (T004, 2026-08-08).** A diagnostic wrote one line from
`RequestContextMiddleware.use`, one from the request-scoped `Repository`
factory, and one from `EnvironmentContextGuard.canActivate`, then sent a single
authenticated `POST /v1/channels/:id/messages` against the real app on the
compose Postgres. Observed order, every run:

```
DIAG middleware
DIAG repository-factory
DIAG guard
```

Two things are now facts rather than assumptions. **Middleware runs before the
request-scoped factory is constructed**, so the primary design stands: the
middleware resolves the principal, puts it on the request, and the factory reads
`req.principal` exactly the way it reads the header today — a one-line swap in
2.2's published factory, not a redesign. And **the factory still runs before the
enhancer chain**, which re-confirms chapter 2.6's finding on this chapter's own
code path; a guard remains useless as a place to resolve tenant scope, and keeps
the narrower job of deciding whether the route accepts the principal's class.

The named fallback (an async factory) is therefore **not taken**. The diagnostic
was removed once measured; the temporary file was `services/api/src/di-order.itest.ts`.

**Alternatives considered**: dropping request scoping and resolving a repository
per call from the principal (rejected for this chapter: it rewrites 2.2's
published design and three chapters' fences to solve a problem middleware may
already solve); a global guard (rejected: same ordering problem, and pre-auth
routes like signup would need opt-outs).

---

## R6 — What each surface accepts

**Decision**: one `principal` with a `kind` of `application` or `user`, and
routes that declare what they accept. Concretely:

| Surface | Accepts | Source |
|---|---|---|
| `POST /v1/channels/:id/messages`, `GET …/messages` | either class | FR-MSG-13 allows server-to-server sends; FR-AUT-10 does not reserve these |
| `POST /auth/dev-token` | application only, and only in a `development` environment | FR-AUT-09 |
| The WebSocket upgrade | user only | it is an end user by definition (EIR-WS-05) |
| Administrative operations named by FR-AUT-10 | application only | FR-AUT-10 verbatim |
| `/auth/:provider/start` and `/callback` | no credential | 3.1: they establish identity |

**Rationale**: FR-AUT-10 names exactly what must require a key — "creating
channels with arbitrary membership, deleting others' messages, and all tenant
management" — and the chapter should honour that list rather than inventing a
broader matrix. None of those operations has a public route yet, so the rule is
installed and tested at the layer that will enforce it when they arrive.

**Bounded deliberately**: attributing a key-authenticated public send to a
specific end user is left as it is today (unattributed), because doing it
properly needs a user reference on the public contract, and that belongs with
the REST-send chapter rather than here.

---

## R7 — Revocation with no cache (FR-AUT-05)

**Decision**: verify against Postgres on every authenticated request. Revocation
is then immediate by construction, on every instance, with nothing to invalidate.

**Rationale**: FR-AUT-05's five-second bound is usually read as "invalidate a
cache fast enough". The cheaper reading is to have no cache: one indexed lookup
on a primary-key-ish column per request, in the same connection pool the request
already uses. If profiling ever makes that the bottleneck, the fix is a cache
plus a Redis invalidation channel — which is 2.6's fabric doing a second job,
and belongs to whichever chapter measures the need rather than this one.

---

## R8 — The first key, and how tests get one

**Decision**: 3.1's `provisionOrganisation` also mints one `development` key and
returns its secret in the signup response — the one place it is ever shown
(FR-AUT-02). Test suites and walk scripts get their keys the same way, through a
helper that signs up (or provisions directly) and keeps the returned secret.

**Rationale**: with no console session, a brand-new organisation cannot
authenticate a request for its first key; something has to bootstrap. Signup is
the natural place, it matches FR-DSH-01's "development API key on the first
screen following signup", and it means the chapter never has to explain a
chicken-and-egg problem it left unsolved.

**Alternatives considered**: letting a valid key mint another key (rejected, and
worth saying why: a leaked credential could then extend itself indefinitely, and
no requirement asks for it); an unauthenticated bootstrap route (rejected
outright); building the console session here (rejected: docs/07 gives 3.2 two
credentials, and the session belongs with the dashboard — see R11).

---

## R9 — The wrong-credential error

**Decision**: a new error code in `@relay/protocol`'s registry —
`wrong_credential_type` — whose message names both what was presented and what
the route expected, e.g. "this route expects an API key; an end-user token was
presented".

**Rationale**: the SRS singles this out as the most common first-integration
failure and requires the message to name the mistake. The registry was built in
1.3 to be extended by the chapters that need codes, and the uniqueness of codes
is already test-enforced. A generic `unauthorized` would satisfy the status code
and fail the requirement.

**Care**: the message names the *class*, never the credential. NFR-SEC-06 forbids
secrets in logs and error bodies, and "the key `rk_dev_abc…` is invalid" is
exactly how a secret ends up in a support ticket.

---

## R10 — Retiring the header, and the blast radius

**Verified**: `x-relay-environment` appears in eight files today — the guard, the
request-scoped factory, four api integration suites, the gateway's api client,
and the e2e harness. Retiring it is therefore the same class of risk as 3.1's
`createEnvironment`: a change that is correct in one file and red in seven.

**Decision**: the credential replaces the header in one increment, together with
a test helper that mints a key for a seeded environment, and a checkpoint that
re-runs every existing suite before any chapter prose is written.

**Internal hop**: the gateway→api internal routes keep the trust model 2.5
recorded (network-internal, forwarded identity trusted) — except that the
identity is no longer *asserted* by the gateway, it is returned by the api's
token verification (R1). Service-to-service credentials remain Part 3 hardening,
named in the chapter, unbuilt here.

---

## R11 — 3.1 promised the session to this chapter

**Verified**: chapter 3.1's SkipAhead reads "No session — that is 3.2's", while
its body says credentials are 3.2's subject and the dashboard that would consume
a session is Part 5.

**Decision**: 3.2 builds no human session, and this feature corrects 3.1's
wording forward to name the dashboard's chapter. docs/07 gives 3.2 two
credentials; the SAD's context view gives dashboard users an OAuth session.

**Rationale**: the alternative — building a session here to honour a sentence —
would make the chapter's title wrong and duplicate work Part 5 owns. Fixing a
forward reference is cheap; leaving a promise unmet is the drift this series
exists to prevent. Only the English 3.1 exists, so it is a one-file edit.

---

## R12 — Fence and documentation mechanics

- `services/api/package.json` gains `jose` → hunked diff fence (three chapters
  fence this file; the chain tooling verifies the pre-image).
- `packages/protocol/src/codes.ts` gains an error code → hunked diff fence.
- 3.1's published chapter needs two edits: the corrected session reference
  (R11) and the signup response gaining a key field (R8). Both are fix-forward
  under spec FR-024, and 3.1 has no Vietnamese edition to mirror.
- No new ADR is expected. R1 (verify at the owner) follows ADR-05 rather than
  amending it; R3 and R4 are service-local choices inside ADR-15's scope. If a
  reviewer wants R1 recorded architecturally, it is a sentence in SAD §8 rather
  than a new record.
