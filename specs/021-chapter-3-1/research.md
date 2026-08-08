# Phase 0 — Research: Chapter 3.1, Tenants All the Way Down

Every decision below was checked against the repository as it stands at the
Part 2 checkpoint, not assumed from habit. Sources: `docs/04-srs.md`
(FR-TEN-01…08, FR-AUT, FR-DSH-01), `docs/05-sad.md` (§3 context view, §6.1
data view, §8 cross-cutting), `.specify/memory/constitution.md`
(Principles I, V, VI, VII), and the current `relay-platform` tree.

---

## R1 — Where provisioning lives

**Decision**: Grow the repository layer's existing *admin surface*. Today
`createEnvironment(db, {name, kind})` is the one function in
`services/api/src/db/repository.ts` that is deliberately not tenant-scoped;
it already inserts the stub `applications` row. Chapter 3.1 turns it into
real provisioning (organisation → application → environment) and deletes
the stub's DECISION comment.

**Rationale**: The seam the chapter needs already exists and is already
explained to the reader. The alternative — a second module that also writes
tenant containers — would put two doors on the one operation that creates
tenants, which is precisely the surface Principle I says must have one home.

**Alternatives considered**: a separate `TenancyRepository` class (rejected:
splits the admin surface in two, and the lint ban on `drizzle-orm` outside
`src/db/**` would then govern two files with the same authority); provisioning
inside the HTTP controller (rejected: violates ADR-04's single writer and the
repository-layer clause in SAD §8).

---

## R2 — Human identity vs. tenant end users

**Decision**: Two populations, never merged, in two tables. The Part 2
`users` table stays exactly what it is — the *customer's* end users, scoped
to an environment, who never sign in to Relay. The humans who sign up get a
separate table above the tenant boundary, linked to organisations through a
membership row carrying `owner | admin | member` (FR-TEN-07's vocabulary).

**Rationale**: They differ on every axis that matters. Tenant end users are
environment-scoped (FR-TEN-06), arrive by API, and are identified by the
customer's `external_id`. Platform humans are global (one person may own
several organisations), arrive by OAuth, and are identified by a provider
account. Merging them would put a nullable `environment_id` on the identity
table — and a nullable tenant column is the one shape Principle I forbids.

**Alternatives considered**: reusing `users` with a null environment for
platform humans (rejected: breaks FR-TEN-06 and the repository's mandatory
scoping); storing membership on the organisation as an array (rejected: not
queryable, no room for roles or joined-at, and no foreign key).

**Chapter consequence**: this is the chapter's strongest TRAP candidate — the
"one users table" instinct is the natural mistake, and its cost is a tenant
column that can be null.

---

## R3 — Enforcing "exactly two environments" (FR-TEN-04, spec FR-009)

**Decision**: `UNIQUE (application_id, kind)` on `environments`, alongside the
`kind IN ('development','production')` CHECK the 2.1 schema already carries.
The two together cap the count at two by construction.

**Rationale**: No trigger, no counting query, no race. Two constraints the
reader can read off the schema produce the invariant — the same "designed
out, not tested out" move 2.1 made for tenant isolation, and the reason the
rule survives concurrent creation attempts.

**Alternatives considered**: a `CHECK (SELECT count(*) …)` (not expressible in
Postgres); an application-level guard (loses to a race, and Principle I's
whole argument is that invariants belong in the schema); a trigger (works,
but is machinery where a unique index does).

---

## R4 — Atomic provisioning (spec FR-008)

**Decision**: One transaction for the whole trio, using the same
`db.transaction()` pattern 2.2 established for the write path.

**Rationale**: A half-built tenant — an application with no environment — is
unusable and invisible to the person who just signed up. The failure is worth
demonstrating in the chapter by forcing an error mid-provision and showing
that nothing survives.

---

## R5 — Signup idempotency (spec FR-010)

**Decision**: `UNIQUE (provider, provider_account_id)` on the identity table,
with provisioning reading the existing row when the constraint recognises a
returning human — the same shape 2.3 used for message idempotency (DR-03), and
the chapter can say so.

**Rationale**: The second authentication must return the existing
organisation, not a second one, and must do so under concurrency. Checking
"does this identity exist?" before inserting is the classic read-then-write
race; the unique index is what actually decides.

---

## R6 — OAuth flow: hand-rolled, not Passport

**Decision**: Implement the authorization-code flow directly — a redirect to
the provider, a callback that exchanges the code at the provider's token
endpoint, then one call to the provider's user endpoint — using `fetch`
(Node 22 built-in) and validating both provider responses with zod, which the
api already depends on.

**Rationale**: The chapter's subject *is* the flow; a strategy library would
hide the three steps the reader is here to learn, and would add two
dependencies (`@nestjs/passport`, `passport-github2`) to a service whose
constitution says boring by design. It also matches the series' own habit:
2.5 wired the WebSocket upgrade by hand rather than letting the library own
it, for the same pedagogical reason.

**Verified**: the api's dependency list today is NestJS 11, drizzle, pg,
reflect-metadata, rxjs, zod, plus the two workspace packages. No HTTP client
or auth library is present, and this decision adds none.

**Alternatives considered**: Passport strategies (rejected above);
`openid-client` (rejected: GitHub is not an OIDC provider, so the library's
value evaporates for the worked example).

---

## R7 — The `state` parameter needs a cookie, and that is the trap

**Decision**: Mint a random `state`, set it in a short-lived `httpOnly`,
`SameSite=Lax` cookie on the start request, and require an exact match on the
callback. Cookie reading is a five-line header parse; no `cookie-parser`
dependency.

**Rationale**: `state` exists to bind the callback to the browser that started
the flow. A stateless signed `state` proves the server minted it but not that
*this* browser asked for it, which is exactly the CSRF hole the parameter is
supposed to close. This is a strong TRAP: the "it validates, so it's fine"
version is subtly wrong, and the failing case can be demonstrated.

**Alternatives considered**: no state at all (rejected: CSRF); state in a
server-side table (rejected: a table to hold a value for thirty seconds, when
a cookie is the standard answer).

---

## R8 — Testing the provider without a network

**Decision**: The provider's token and user endpoints are configuration. Tests
point them at a local stand-in HTTP server started by the suite; the reader
points them at GitHub. One code path, two configurations.

**Rationale**: The two-lane gate (2.1) and the flake rule (2.8) both say the
suite must be deterministic and offline. Making the endpoints configurable is
also what a real deployment needs for GitHub Enterprise, so the seam is not
test-only scaffolding.

**Alternatives considered**: recorded HTTP fixtures (rejected: they rot
silently and teach nothing); hitting GitHub in CI (rejected: network flake,
secrets in CI, and rate limits).

---

## R9 — What this chapter does NOT authenticate

**Decision**: Chapter 3.1 exposes exactly two HTTP routes, both necessarily
unauthenticated (the start and the callback). It does not add a console
session, and it does not open authenticated management routes for creating a
second application or a production environment; those capabilities exist in
the provisioning layer and are exercised by tests.

**Rationale**: A session cookie that keeps a human logged in is a credential,
and credentials are 3.2's subject ("two credentials, one mistake"); the
dashboard that would consume the session is Part 5, and FR-DSH-01 ties the
first screen to an API key that does not exist until 3.2. Inventing a third
credential here — one the very next chapter reworks — is what Principle VII
tells us not to do. The chapter states the gap and names its owner, the same
way 2.5 named the dev-secret seam.

**Alternatives considered**: issuing a signed session JWT now (rejected as
above); returning nothing at all from the callback (rejected: the reader needs
to see what was created, and the walk script needs an observable outcome).

---

## R10 — Does this need an ADR?

**Decision**: One ADR is warranted, for R2 only: **the two user populations**.
Draft it as ADR-18 in `docs/05-sad.md` with a matching deep dive in
`docs/06-adr-deep-dives.md`, following the ADR-15/16/17 precedent.

**Rationale**: R2 is a constraint every later chapter inherits — dashboards,
webhooks, audit logs and the isolation gauntlet all need to know which
population an identifier belongs to — and the source documents never state it,
because §6.1 never defines these tables at all. The other decisions here are
either derivations recorded as chapter DECISIONs (R1, R3, R4, R5) or
service-local library choices (R6, R7, R8) that ADR-15's scope already covers.

**Cost check**: an ADR plus deep dive is roughly the amendment 2.6 made to
ADR-07 — a contained edit, and both documents are already living artifacts
mirrored into the site by `sync-docs.sh` with a drift check.

---

## R11 — Migration and fence mechanics

**Decision**: One forward-only migration, `0002_tenancy.sql`, generated by
drizzle-kit from the schema (the ADR-16 workflow) and reviewed before it is
applied. It creates the new tables and replaces the 2.1 `applications` stub in
place — the stub is a real table with one column, so the migration alters it
rather than dropping and recreating it.

**Verified**: `services/api/migrations/` currently holds `0000_core_tables.sql`
and `0001_drop_redundant_index.sql`, so `0002` is next; the runner applies
files in sorted order and records them in `schema_migrations`.

**Fence discipline**: amendments to files earlier chapters fenced —
`schema.ts`, `repository.ts`, `app.module.ts` — use hunked diff fences (the
convention adopted in 2.7 and recorded in docs/07 §2), verified by
`pnpm check:fences`.
