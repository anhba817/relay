# Phase 0 research — Chapter 3.12, the isolation gauntlet

Twenty-one findings. Nine were measured against the running stack rather than
reasoned about, and four of those contradicted what the specification assumed.

---

## R1 — Where the gauntlet lives, and why it is not `packages/e2e`

**Decision.** The REST half is `services/api/src/isolation/gauntlet.itest.ts`, booting
`AppModule` in process. The socket half is `services/gateway/src/isolation.itest.ts`,
in the lane that already spawns a live api child. Neither goes in `packages/e2e`.

**Measured.** `vitest.coverage.config.mts` excludes `packages/e2e/**`, with the reason
in the file: the journey "measures the system, not any file's branches, and its child
processes' coverage is not attributable here anyway". A gauntlet living there would
contribute nothing to FR-040, which asks for the isolation code's branch coverage
against constitution VI's 100% clause. Chapter 3.11's R23 measured the same property
from the other side: `creditConnectionMinutes` raised `repository.ts` branches because
nineteen **in-process** tests exercised it, where chapter 3.5's additions arrived
measured at zero because only a child-process suite reached them.

The boot pattern already exists and needs no invention. `messages.itest.ts` opens with
`Test.createTestingModule({ imports: [AppModule] })` against the compose Postgres, and
**ten other api suites do the same** — eleven files under `services/api/src` import
`AppModule`, counted rather than remembered, because an earlier draft said nine.

**Rejected.** `packages/e2e` for the whole suite — the milestone precedent from chapter
2.8 makes it the obvious home, and it is the wrong one for the one reason that matters
here. The precedent it actually sets is about journeys, and this is not a journey.

---

## R2 — The target list is derived from the router, not from Nest's metadata

**Decision.** Enumerate `app.getHttpAdapter().getInstance().router.stack`, keep the
layers carrying a `route`, and read `route.path` and `route.methods`.

**Measured**, by booting the built `AppModule` against the live stack and printing both
candidates:

```
method 1 — express router stack          30 layers: 22 routes + 8 middleware
  GET    /healthz
  POST   /auth/dev-token
  POST   /v1/channels/:channelId/messages
  GET    /v1/channels/:channelId/messages
  POST   /internal/messages
  POST   /internal/backfill
  POST   /internal/session
  POST   /internal/dispatch/expand
  POST   /internal/dispatch/material
  POST   /internal/dispatch/outcome
  POST   /internal/dispatch/replay
  POST   /internal/usage/connections
  GET    /auth/:provider/start
  GET    /auth/:provider/callback
  POST   /v1/webhooks
  GET    /v1/webhooks
  GET    /v1/webhooks/:id
  POST   /v1/webhooks/:id/rotate-secret
  POST   /v1/webhooks/:id/enable
  POST   /v1/webhooks/:id/disable
  POST   /v1/webhooks/:id/test
  DELETE /v1/webhooks/:id

method 2 — Nest controller metadata      22 entries
  0 //healthz [HealthController.healthz]
  1 v1/channels/:channelId/messages// [MessagesController.send]
  3 v1/webhooks/:id [WebhooksController.remove]
```

Both find 22. Method 1 gives normalised paths and string verbs; method 2 gives
double-slash join artifacts and numeric `RequestMethod` enums, and it reads
`Reflect.getMetadata("path", …)` — a key that is Nest's private business. Method 1
reads what is actually routable, which is the property FR-002 is about: a route that
exists and is unattacked is the fault, and only the router knows what exists.

**The failure mode this creates, and the assertion that closes it.** `instance.router`
is express 5's spelling; express 4 called it `_router`. A derivation that finds nothing
and reports an empty target list would pass a suite that attacks nothing. So the
derivation MUST assert a non-zero count and MUST assert that a known route is present —
`POST /v1/channels/:channelId/messages`, which has existed since chapter 2.2. A suite
whose target list can silently empty is worse than a hand-written list, because a
hand-written list is at least visible in a diff.

---

## R3 — The oracle already exists, in one file, and the chapter generalises it

**Finding.** `services/api/src/messages/messages.itest.ts` opens with a helper and a
comment that state the gauntlet's whole assertion:

```ts
// The id is the one field that reveals nothing about the resource, so it is the
// one field the comparison must drop. Everything discriminating still has to match
// exactly.
function withoutRequestId(body: unknown): unknown { … }
```

and above it, the reason: "comparing them whole is how this suite proves a foreign
resource is indistinguishable from an absent one, which is a tenant-isolation property
(constitution I)". Chapter 3.8 forced the helper into existence by adding `request_id`
to every error body.

So the gauntlet does not invent an oracle. It lifts this one into a shared place and
applies it to 22 routes instead of one. The chapter's honest framing is that the
correct test was written once, by a chapter that needed it, and never generalised —
which is what the difference between assertions and a suite looks like in practice.

**Where it goes.** A helper in the harness the gauntlet uses, not in the test file.
Duplicating it into a second file would be the fault the chapter is about.

---

## R4 — Four endpoint shapes, four twin requests

**Decision.** Every target is classified as one of four shapes, and the classification
decides what the paired "does not exist anywhere" request is.

| Shape | Attack | Twin | Assertion |
|---|---|---|---|
| Read by id | another tenant's id | a well-formed id that exists nowhere | responses equal minus `request_id` |
| List | caller's own credential, empty tenant | same | empty page, not 404; no foreign row |
| Write by id | another tenant's id | an id that exists nowhere | responses equal, **and** target rows unchanged |
| No tenant identifier | — | — | listed as exempt with a reason |

**Why the twin is required rather than a status assertion.** A gauntlet that asserts
`404` would be wrong about the list endpoints and would freeze the current status
choices into a test. The property constitution I states is indistinguishability, and
the only way to test indistinguishability is to have both responses in hand.

**Measured, and it changes one thing the spec implied.** The exempt set is not
guessable from the path. `GET /healthz` takes no identifier. `GET /auth/:provider/start`
and `/callback` take a provider name and a browser cookie. `POST /auth/dev-token` takes
no id but is tenant-scoped by its credential, so it belongs to a fifth treatment:
attack the *credential*, not the id — a key from environment A must not mint a token
usable in B. That is not a foreign-id attack and it is not exempt, and the spec's
four-shape framing would have filed it wrongly.

---

## R5 — The internal surface is two credential classes, not one

**An earlier draft of this research had one**, and it produced an attack that does not
apply to three of the eight routes. Measured from the decorators:

| Route | Accepts | The credential's scope |
|---|---|---|
| `POST /internal/messages` | `user` | an end-user token, **scoped to one environment** |
| `POST /internal/session` | `user` | same |
| `POST /internal/backfill` | `user` | same |
| `POST /internal/usage/connections` | `platform` | no environment; named per request |
| `POST /internal/dispatch/expand` | `platform` | same |
| `POST /internal/dispatch/material` | `platform` | same |
| `POST /internal/dispatch/outcome` | `platform` | same |
| `POST /internal/dispatch/replay` | `platform` | same |

**So there are two attacks, and the first draft named only the second.** For the three
`user` routes the primary attack is the one that draft called "meaningless on
`/internal/*`": a token minted in environment A used against a resource in B — the same
shape as the socket surface, because it is the same credential. For the five `platform`
routes the credential genuinely carries no environment, so the attack is a request that
names one environment and carries an identifier from another.

**The vocabulary correction that goes with it.** The principal kind is `platform` and the
decorator is `@Accepts("platform")`; the first draft wrote `@Accepts("service")`, which
is not a value the code has. `PlatformPrincipal` in `services/api/src/auth/principal.ts`
is the type, and its comment states the property the attack turns on: "this kind carries
NO `environmentId`. That is not an omission — it is what stops it being usable anywhere a
tenant is expected".

**One instance of the platform-route refusal already exists.**
`usage.controller.ts` answers `409 connection_environment_conflict` when a report names a
connection whose row carries a different environment, on the grounds that "a connection
moving tenants is either a bug or an attempt". The gauntlet generalises that judgement to
the other four rather than re-deciding it.

---

## R6 — The socket half belongs to the gateway's lane

**Decision.** `services/gateway/src/isolation.itest.ts`, gateway in process, api as a
child — the arrangement chapter 3.2 established and chapter 3.11 chose for the same
reason.

**The attacks.** A user token minted for environment A, used to (1) connect and read
`channel_ids`, (2) send into a channel belonging to B, (3) resume from a cursor naming
B's channel, (4) receive anything from B. The session response is the interesting one:
`session.controller.ts` returns `channel_ids: channelsForUser(user.id)` and the
repository is constructed with the token's environment, so the leak would have to come
from the repository — which is where R1 puts the coverage.

**One asymmetry, and the first draft promised more than the package can deliver.**
`packages/protocol`'s `frameSchema` is one discriminated union of ten members and
**carries no direction metadata** — no inbound/outbound split, no client/server types,
nothing to derive a direction from. "Derive the inbound frame types from the union" is
not implementable: you can derive ten names and still need a hand-written direction for
each, which is what the derivation was supposed to remove.

**Decision: the same mechanism as the routes.** A classification list assigning each of
the ten to `inbound` or `outbound` with a reason, plus a totality check against the union
in both directions — every member classified, every entry naming a real member. A new
frame then fails the suite until somebody classifies it, which is the property that was
wanted, obtained the way T011 and T012 obtain it for routes.

**Rejected: adding direction to `packages/protocol`.** It is the better long-term shape
and it is a published package fenced by chapters 1.3, 3.2 and 3.11 — a contract change
for a test's convenience, in a chapter that already carries more than any other in this
part.

---

## R7 — The structural check, and the table that looked like it failed it

**Decision.** Derive from the live catalogue: for every base table in `public`, assert
`environment_id` is present, or exactly one foreign key reaches a table that has it.
Tables with neither are named in an explicit list with reasons — a list, not a pattern,
for feature 030's stated reason.

**Measured.** 22 base tables. Twelve carry `environment_id` directly. Two —
`members`, `messages` — reach it in one hop through `channels`, which is the hop
FR-TEN-06 allows. Seven are the tenancy spine or infrastructure and carry no tenant by
design: `organisations`, `applications`, `environments`, `humans`, `memberships`,
`consumed_events`, `schema_migrations`. One is the harness's own
`__sentinel_environments`, which is not product.

**And one needed a second look, which reversed the first.**

```
outbox: id, subject, payload, created_at, published_at
```

No `environment_id`, **zero** foreign keys. An earlier draft of this research escalated
that as a Principle I violation — the second clause requires a tenant identifier
"directly or through a single foreign-key hop" and neither branch is available — and
proposed adding the column, measured at one insert site (`repository.ts:2823`) with an
exact backfill from `payload->>'environment_id'`.

**That was wrong, and three of the four arguments for it do not survive.**

*"Isolation lives in data access and this table cannot express it"* is backwards.
Nothing wants a tenant-scoped read of the outbox. Its only reader is the global relay,
and `drainOutbox` sits on feature 030's restricted list precisely because being global
is its job. A column no query filters on enforces nothing.

*"Feature 030's guard cannot watch it"* is true and is not a reason. The outbox's
legitimate mutation **is** cross-environment — the relay claims every tenant's rows on
every pass — so adding the column would make the guard refuse the relay's own sweep. The
change buys an `exempt.ts` entry rather than protection, and that file's existing line,
"`outbox` is not among them and needs no entry", was right.

*"Postgres enforces a column"* — against what? The single insert site is inside
`Repository`, which already holds `this.environmentId`. There is no threat model in which
an outbox row is written with no tenant.

**And a cost the first draft did not weigh.** A foreign key to `environments` puts a
constraint check on the hot write path of every send, and blocks deleting an environment
while any outbox row exists — which makes FR-TEN-08's 30-day erasure harder rather than
easier. The proposed fix complicated the requirement invoked to justify it.

**The classification was also internally inconsistent.** `consumed_events` has no tenant
column and no foreign key either, and it was filed as infrastructure without complaint.
The difference reached for was "the outbox carries content" — which is a retention
concern wearing a tenancy clause's clothes.

**So `outbox` is infrastructure, beside `consumed_events`. No column, no amendment, and
the structural check has three classes rather than four.**

---

## R7a — What survives is worse: the outbox keeps message text for ever

**Measured.** `drainOutbox` sets `published_at = now()` and never deletes:

```sql
UPDATE outbox SET published_at = now() WHERE id = ANY(...)
```

Nothing prunes it. Nothing prunes anything — the only `.delete(` in non-test api source
is an in-memory `Map` eviction in `limits/fallback.ts:85`. And the payload is a full copy
of the message:

```json
{ "type": "message.created",
  "environment_id": "a030dd09-…",
  "data": { "id": "9e19f06c-…", "seq": 369, "text": "m368", "channel_id": "a321f176-…" } }
```

286,871 rows in the test database, each holding the text of a message that also exists in
`messages`.

**Four requirements collide with that, and the first draft cited none of them.**

| Requirement | The collision |
|---|---|
| DR-06, FR-MSG-08 | a deleted message keeps its row with `text` cleared, and hard deletion happens only through the compliance endpoint. The text survives in `outbox.payload.data.text`. A tombstone that leaves a copy behind is not a tombstone |
| FR-TEN-08 | deleting an application erases its operational data within 30 days. Unreachable for these rows by any mechanism that exists |
| FR-MOD-06 | per-environment retention with a scheduled hard-delete job. Same gap, from the other direction |

**The fix is pruning, and it needs no tenant column.**
`DELETE FROM outbox WHERE published_at < now() - interval 'N days'` reaches every row
this is about. For the rare per-tenant compliance sweep, `subject`'s last segment already
carries the environment id (`events.msg.created.<uuid>`) and the payload carries the key.

**Not this chapter.** A scheduled retention job is FR-MOD-06, which is Phase 3 and Part
4, and building one here would put a fifth half-built thing in Part 3. Recorded here
because this is the chapter that looked, and owned by whichever chapter builds retention.

---

## R8 — There are eleven error codes, and the registry holds six

**Measured.** The set the platform can emit, by source:

| Source | Codes |
|---|---|
| `packages/protocol/src/codes.ts` (`ERROR_CODES`) | `invalid_frame`, `unknown_frame_type`, `unauthorized`, `rate_limited`, `wrong_credential_type`, `quota_exceeded` |
| `protocol-error.filter.ts` status ladder | `invalid_request`, `unauthorized`, `forbidden`, `not_found`, `internal_error` |
| `packages/service-kit/src/index.ts` | `not_found` |
| named at a call site | `connection_environment_conflict` (`usage.controller.ts`) |

Union: **eleven** as the code stands today. The registry holds six. Five of the eleven exist only as string
literals inside a ternary ladder, and one exists only at a call site. Nothing anywhere
enumerates the eleven, which is why "document every error code" could not have been
done from the registry — the spec's FR-026 exists because of this measurement.

**Decision.** Make the registry the set by construction — and after this chapter the set
is **thirteen**: R24 adds `wrong_credential_service` and FR-CHN-07 adds
`channel_member_limit_exceeded`. Add the five missing keys,
type the filter's ladder as `ErrorCode` so the compiler refuses an unregistered code,
and reference the registry from the call sites that name their own code. Then
`Object.keys(ERROR_CODES)` is the derivation FR-025 asks for, and the reference
document's completeness test compares two lists rather than grepping source.

**Rejected.** Deriving by grep over the source tree. It would have to match a ternary
ladder and would go stale the first time someone formatted it differently — a
derivation that can silently under-report is the same fault as an empty target list.

**Cost, counted rather than estimated — and an earlier draft of this paragraph said
"six", listed eight, and was wrong about both.** Measured with `grep -rn 'code: "'` over
non-test source: **nine** literals.

```
services/api/src/auth/credential.guard.ts        rate_limited, wrong_credential_type
services/api/src/limits/rate-limit.middleware.ts rate_limited ×2
services/api/src/messages/messages.service.ts    quota_exceeded
services/api/src/internal/usage.controller.ts    connection_environment_conflict
services/api/src/internal/session.controller.ts  quota_exceeded
services/gateway/src/session.ts                  rate_limited
packages/service-kit/src/index.ts                not_found
```

Eight of the nine are one task's work; the ninth moves under the `serve()` option that
keeps service-kit dependency-free (R9). Plus five registry keys, one typed ladder, and the
twelfth code R24 adds.

---

## R9 — `docs_url` is built in six places and becomes one function

**Measured.** Six construction sites, two of them templated and four literal:

```
services/api/src/protocol-error.filter.ts:73    `…/errors/${code}`
services/api/src/limits/rate-limit.middleware.ts:122, 220    literal rate_limited
packages/service-kit/src/index.ts:85            literal not_found
services/gateway/src/session.ts:72              literal rate_limited
services/gateway/src/session.ts:103             `…/errors/${code}`
```

**Decision.** One function beside the registry in `@relay/protocol`, and the six sites
call it.

**The complication, measured.** `packages/service-kit` has **no dependencies at all** —
not even `@relay/protocol`. Giving it one to reach the helper would pull zod into a
package deliberately kept empty. And `serve()` has exactly **one caller**,
`services/gateway/src/main.ts`; the api answers `/healthz` through a Nest controller and
the dispatcher does not use `serve()`. So the dependency inverts for free: `ServeOptions`
gains a required field carrying the not-found `docs_url`, the compiler makes the single
caller supply it, and service-kit stays dependency-free.

**Rejected.** Duplicating the base URL into service-kit with a test that reads the other
file and fails on divergence — the pattern `db-url.test.ts` and `bait-size.test.ts`
already establish. It is the house answer for a duplicated *constant*, and this would be
a duplicated *function*. A required option costs one call site and no watcher.

---

## R10 — The anchor, and a one-character change with a measured blast radius

**Finding.** The published docs pages give heading anchors only to `h2`, through
`slugifyHeading` in `components/docs/doc-article.tsx`:

```ts
.replace(/[^\p{L}\p{N}]+/gu, "-")
```

Underscores are not letters or numbers, so `## quota_exceeded` becomes
`#quota-exceeded`. An error code contains underscores by rule — `codes.test.ts` asserts
`/^[a-z][a-z_]*$/` — so `docs_url` would need to transform the code on the platform
side to match a slug generated in a different repository. Two repositories, one
transformation rule, no way to test the pair together.

**Decision: preserve underscores in the slugifier**, add `_` to the kept class, and
build `docs_url` as base + `#` + the code verbatim. No transform on either side, and
nothing to keep in step.

**Measured blast radius**, because the same function ids every `h2` in 28 published
chapters through `mdx-components.tsx`:

```
chapter h2 headings containing an underscore        0
docs h2 headings containing an underscore           1
  ## ADR-03 — Per-channel sequences via `last_sequence` row lock
links anywhere in the site to a /docs/<slug>#anchor 0
```

One anchor changes and nothing links to it. Each code is an `h2` in the reference, so
`h3` needs no id and the component needs no second change.

---

## R11 — The reference document, and the two globs that would skip it

**Decision.** `docs/08-error-reference.md` in the parent repository, mirrored by
`scripts/sync-docs.sh`, registered in `lib/docs.ts`, published at `/docs/error-reference`
and `/vi/docs/error-reference`.

**Measured, and the glob is the trap.** Both bash scripts select
`0[1-6]-*.md` — `sync-docs.sh` copies and `check-docs-drift.sh` compares. The range
stops at 6 deliberately: `docs/07-tutorial-plan.md` is not a published reference page.
So the fix is not widening a range; `0[1-8]` would publish the tutorial plan. Both
scripts take an **explicit file list**, which is feature 030's doctrine arriving in a
shell script: whatever silently absorbs the next case is the thing to remove.

**One thing that needs no work and one that changed.** `doc-page.tsx` renders the
"referenced by" line under `citing.length > 0 &&`, so a document no chapter cites renders
cleanly. **This one will be cited**: analysis pass eight found that `lib/tutorial.ts`
already carries a 3.12 entry, and adding `docs/08-error-reference.md` to its `sourceDoc`
makes the new page link back to the chapter that built it (T119a). The empty-citation path
still renders cleanly; this document is no longer the thing testing it. And the Vietnamese
route renders the same English markdown under a translated title, with a standing note that
source documents are kept in English, so the reference needs a `titleVi` and no
translation.

**One thing to watch.** Three lists must now agree: the two scripts and the registry.
A document in the registry and not the sync list renders whatever
`content/docs/` last held — a stale page that no check notices, because
`check-docs-drift.sh` only walks files its own glob selects.

---

## R12 — What seals the sealed package, and the hole that stays open

**Measured.** `relay-platform/node_modules` has **no `@relay` directory**. pnpm links
workspace packages only into the `node_modules` of packages that declare them, so a
package that does not depend on `@relay/protocol` cannot resolve it — the seal is the
package manager's, for free, and needs no rule. Meanwhile `vitest`, `ws` and `jose` do
sit at the workspace root and resolve by the ordinary parent walk, so the sealed
package can run tests and open a socket while declaring nothing.

**And the holes — plural, which an earlier draft of this section got wrong.** It said the
remaining hole was "a relative-path import, which only a lint rule closes". There are two,
and the second is the one an import rule cannot see.

```
packages/e2e/src/harness.ts:4    import { createRequire } from "node:module";
packages/e2e/src/harness.ts:31   const REPO = join(HERE, "..", "..", "..");
packages/e2e/src/harness.ts:389  spawn("node", [join(REPO, "services", "api", "dist", "main.js")], …)
```

Line 31 is not an import. It is a string built from fragments, and `no-restricted-imports`
matches import specifiers — it never sees `join`, `createRequire`, `readFileSync` or
`spawn`. The file cited as proof that the hole exists is also proof that the proposed rule
does not close it.

**So the seal is three levels, and the chapter says which is which:**

| Level | Mechanism | Closes |
|---|---|---|
| 1 | pnpm's isolated `node_modules` | `import … from "@relay/protocol"` — no rule needed |
| 2 | `no-restricted-imports` patterns | `import … from "../../services/api/…"` |
| 3 | `no-restricted-syntax` | `join(HERE, "..", …)`, `createRequire` — a path built at run time |

Level 3 is new: `eslint.config.mjs` has no `no-restricted-syntax` rule today. Banning
`".."` string literals and `createRequire` inside `packages/outsider/**` is narrow enough
to state, and testable by writing one and watching lint fail.

**What none of the three closes**, said before the chapter claims otherwise: reading the
repository's source with human eyes. That is a discipline, and the chapter says so rather
than letting three rules imply a fourth.

---

## R13 — The credential the outsider cannot obtain

**Finding.** Signup is OAuth against GitHub or Google, and an API key is minted only
inside the signup transaction (`repository.ts:2176`). There is no key-management
endpoint — chapter 3.2 deferred it to "the dashboard's chapter". An automated suite
cannot complete a consent screen, and pointing `RELAY_OAUTH_GITHUB_*` at a local stub
is what `signup.itest.ts` does with test-only knowledge the outsider does not have.

Meanwhile the constitution requires the full stack to start with one command
"including a seeded demo tenant", and nothing seeds anything.

**Decision.** A documented seed command that creates an organisation, an application, a
development environment, and one key, and prints the key. The sealed integration starts
where a reader following the published instructions starts.

**What that closes and what it does not, stated rather than implied.** The constitution's
clause says `docker compose up`, and compose starts stores, not services; the services
run under `pnpm dev`. So a `pnpm seed` closes the clause's intent and not its letter,
and the chapter says so. Widening compose to run a seed job would need the migrations to
have run first, which is an ordering problem this chapter is not the place to solve.

---

## R14 — The two endpoints, and what they may not grow into

**Decision.**

```
POST /v1/channels                      create, idempotent on the customer's id
POST /v1/channels/:channelId/members   add members by the customer's user id
```

Both take an API key. `createChannel(externalId, type, name?)` and
`addMember(channelId, userId)` exist in the repository with those signatures;
`createUser(externalId, displayName?)` is what makes a member out of an identifier the
customer supplies. **The clause for that is FR-USR-01**, not FR-USR-02: identifiers come
from the customer and "Relay shall not generate end-user identities", and FR-CHN-06 does
not require members to pre-exist. FR-USR-02 is about creation on first *authentication*,
which is a different moment — an earlier draft cited it, and a requirement id used loosely
is worse than none, because it makes a traceability table look complete.

**Status codes.** `201` on creation and `200` on the idempotent repeat, which is the
distinction chapter 2.3 already draws for a duplicate send and the one an integrating
developer can act on. FR-CHN-02 says "return the existing channel rather than an
error", not "return the same status".

**Two repository functions need changing, not one.** `createChannel` at
`repository.ts:2571` is a plain `insert(channels).values(...)` with no `ON CONFLICT`, so a
repeated `external_id` raises against `channels_environment_id_external_id_unique` — and
409 is not one of the four statuses `ProtocolErrorFilter` maps, so it reaches the wire as
`internal_error`. Doing the idempotency in the service as read-then-insert races, and
Principle II requires it "enforced at the storage layer (unique index), not in application
memory". So `createChannel` gets `ON CONFLICT (environment_id, external_id) DO NOTHING
RETURNING`, falling back to `getChannelByExternalId`, which already exists and is already
scoped. `addMember` gets the same treatment for its own primary key (R14a).

**And four neighbouring clauses were never read, which is what analysis pass five was
for.** `POST /v1/channels` cited FR-CHN-01 and FR-CHN-02 and satisfied part of the first;
FR-CHN-03, 05 and 07 sit beside them and none had been opened.

**FR-CHN-05 is not implemented, and this endpoint would have made that a promise to a
customer.** Measured: `channels.type` is a `"public" | "private"` column with a CHECK
constraint, and **nothing reads it** — the only matches for `"private"` in `repository.ts`
are the type union at 2198 and TypeScript's `private` modifier. History and send scope by
`environment_id` alone; there is no membership check in either path. FR-CHN-05 is P1: *"A
user shall not read messages from, send messages to, or observe presence in a private
channel of which they are not a member."* Until this chapter only tests could create a
private channel, so the gap was invisible. A public create endpoint would let a paying
integrator ask for privacy, be told they had it, and get none.

**Decision: the endpoint's type vocabulary is `public` and nothing else**, refused at the
schema so the failure names the field. FR-CHN-03's private half and FR-CHN-05 go to chapter
3.13 together, because access control for private channels is the send path, the history
path and the socket subscribe path — a chapter, not a validation rule. The column keeps
both values: the database is not the thing making the promise.

*Rejected: a 422 with a new code meaning "not supported yet".* It reads better and costs a
fourth new code in a chapter that has already added two. A schema whose documented enum has
one member is the smaller honest surface, and EIR-API-04's `field` element exists to say
which input was wrong.

**FR-CHN-07 was in no artifact at all.** *"A channel shall support up to 1,000 members.
Exceeding the limit shall return `422` with a specific error code."* The SRS names the
number, the status and the requirement of a specific code — and its own worked example for
EIR-API-04 names the code itself: `channel_member_limit_exceeded`. Enforced here: one
count, one 422, one code, which makes the shipped set **thirteen**.

**FR-CHN-01 has four elements and the first draft delivered three.** Metadata was missing,
and `channels.metadata` is a `jsonb` column with a default that has existed since chapter
2.1 — so the omission cost a schema field and an 8 KB bound, not a migration.

**Bounded on purpose.** FR-CHN-06 allows up to 100 members per request; the endpoint
accepts an array and caps it, because a member endpoint that takes one id would have to
be replaced rather than extended. Nothing else: no listing, no unread counts, no
removal, no roles beyond the default. Those are chapter 3.13's, and FR-022 requires the
number to be in the plan document rather than in a comment.

---

## R15 — The guard extension, measured on both table shapes

**Measured.** The failure 3.11's R5a predicted, reproduced against the live database:

```
CREATE TRIGGER … ON probe_composite …    -- composite PK, no id column
UPDATE probe_composite SET minutes = 6;
ERROR:  record "old" has no field "id"
CONTEXT:  PL/pgSQL expression "OLD.id"
```

**And the fix, verified on both shapes in the same session:**

```sql
key_text := coalesce(to_jsonb(OLD) ->> 'id', to_jsonb(OLD)::text);
```

```
composite PK  → guard: row … (key {"period": "2026-08-01", "minutes": 5, "environment_id": "…"})
id-bearing PK → guard: row … (key 00000000-0000-0000-0000-0000000000aa)
```

One expression, no per-table branch. `to_jsonb(OLD)` has no compile-time field
requirement, and `->> 'id'` yields NULL rather than raising when the key is absent.

**Which tables, and what the fallback prints.** Three of the four have composite keys
and take the fallback — `usage_periods` (`environment_id, period`),
`usage_active_users` (`environment_id, period, user_id`), `usage_connections`
(`connection_id, period`); `quota_notifications` has an `id` and takes the first
branch. The fallback puts the whole row in an exception message, so it is worth stating
that these four carry counters, dates and identifiers and no message text — NFR-SEC-06
would forbid the same fallback on `messages`.

---

## R16 — The isolation code is 25 branch arms from the constitution's clause

**Measured** on this feature's starting commit, `pnpm coverage`, both lanes green at
69 files / 668 tests:

```
All files                    90.37 stmts  84.17 branches  89.51 funcs  91.58 lines
services/api/src/db/
  repository.ts              97.50 / 90.60 / 100 / 99.45      uncovered lines 152, 3140
                             branches 241/266  →  25 uncovered arms
```

**So the 100% clause is a countable distance away, and the count is 25.** Feature 024
measured 85.91% and pinned it, saying the clause "belongs to the next chapter that
touches the repository layer"; chapters 3.5 and 3.6 lost ground, 3.10 and 3.11 gained
it, and nobody has ever said how far there was left to go. Twenty-five arms on a file
with 100% function coverage and two uncovered lines means almost all of it is unhit
arms on covered lines — `??` defaults, optional chaining, ternaries exercised one way.

**And FR-040 cannot be satisfied with the reporters currently configured.**
`vitest.coverage.config.mts` sets `reporter: ["text", "json-summary"]`. `json-summary`
emits totals and percentages, not branch locations, so the 25 arms can be *counted* and
not *named* — which is exactly what FR-040 asks for. One more reporter (`json`) makes
them enumerable. Found by trying to list them and getting a file that does not contain
them.

**One number that did not reproduce.** Chapter 3.11 closed on
90.32 / 83.98 / 89.51 / 91.53 for all files; the same commit measures
90.37 / 84.17 / 89.51 / 91.58 today. Nothing changed in between. The lane's coverage is
mildly data-dependent — the test database has accumulated rows since, and some branches
are taken or not depending on what is in it. Worth knowing before treating a 0.05
movement as a result.

---

## R17 — The fixed port is in the other file with that name, and nothing fences it

**Two corrections, both measured, both to claims this chapter inherited rather than
checked.**

**The file is `services/gateway/src/limits.itest.ts`, not the api's.** CLAUDE.md and
chapter 3.11's notes say "`limits.itest.ts` binds a fixed api port (`?? 4124`)", and
this repository has two files with that basename. The port is in the gateway's:

```
services/gateway/src/limits.itest.ts:123
  const port = Number(process.env.RELAY_LIMITS_ITEST_API_PORT ?? 4124);
```

`services/api/src/limits/limits.itest.ts` binds nothing. It is the file that fails when
the lane has no platform credential (R22), which is how the two got conflated. An
earlier draft of this research, of the plan and of the task list all named the api's
file, so the fix would have edited a file with no port in it and left the defect
standing.

**And neither file is fenced by any chapter or by `post-series.md`.** Measured with
`grep -rn 'title="…limits.itest.ts"'` across `app/(en)`, `app/(vi)` and `fences/`: no
hits for either path. 3.11's notes call it "another chapter's fenced file"; it is not
one. The prose mentions in chapters 3.8 and 3.11 discuss the file without fencing it,
and `services/gateway/src/limits.itest.ts` appears inside chapter 3.8's fence of
`eslint.config.mjs` as a string in an ignores array — which is a fence of the config,
not of the test.

**So the port fix needs no fence work at all.** No chapter amendment, no post-series
entry. That is a smaller change than three documents claimed.

**The fault itself is unchanged.** `startApi()` binds 4123 and this file binds 4124;
vitest runs files in parallel, and back to back a previous run's child can still hold
the port, at which point the new child dies on `EADDRINUSE` and `waitForHealth` gets its
200 from the **old** api serving a different environment's signing secret. Chapter 3.11
spent a diagnosis on three assertions that named none of that.

**One thing that makes it worse than it looks.** The override exists and cannot be used:
`RELAY_LIMITS_ITEST_API_PORT` is not in `turbo.json`'s `test:integration` env allowlist,
and turbo's strict env mode filters what it does not declare — so 4124 is the only value
that ever runs under `pnpm test:integration`. The escape hatch is unreachable from the
command everybody uses.

**Decision.** A random high port, as `session.itest.ts:106` (`4400 + random*200`) and
`meter.itest.ts:64` (`4610 + random*60`) now use.

---

## R18 — Proving the suite catches things, without shipping the proof

**Decision.** Three reintroductions, run by hand in the working tree during
implementation, each recorded in `baseline.txt` with the exact assertion that fired:

1. a read predicate — drop `environment_id` from one repository `SELECT`;
2. a write predicate — drop it from one `UPDATE`;
3. a distinguishable refusal — change one 404 to a 403.

Reverted with `git checkout` after each. FR-015 asks how "none shipped" is verified
rather than asserted: the working tree is clean at the phase commit, and the phase's
diff is reviewed for the three files. This is feature 030's practice — it reintroduced
its faults deliberately and measured which of nine tests noticed — applied to a
different fault class.

**What it cannot do.** It measures sensitivity to the three faults chosen, not to the
fault nobody thought of. The chapter says that rather than presenting three passes as
proof of coverage.

---

## R19 — The seam, named before a word is written

**Finding.** This chapter carries more than any Part 3 chapter has: a derived suite over
22 routes plus a socket surface, a structural check, eleven documented error codes, a
new published document with three lists to keep in step, two endpoints, a sealed
package, three inherited debts and four this chapter found for itself. Two chapters in
this part have already exceeded the
2,000–4,000 word bound, both discovered afterwards.

**And the stronger argument was sitting unused: the fence surface.** Re-derived from the
task list after three analysis passes had added to it, restricted to `relay-platform`
paths: **16 new fenced files and 21 amended** — **37**, against chapter 3.11's 21 files
and 34 fences, and chapter 3.5's 39 fences on a budget first estimated at 22. Every
amended file needs a diff fence in this chapter's own prose or the chain's HEAD property
fails, so the fence count is not incidental to the page length; it is a floor under it.

Two files in the raw count are excluded and named rather than quietly dropped:
`services/api/src/health.controller.ts`, which T022 touches with a throwaway probe and
reverts, and `services/gateway/src/limits.itest.ts`, which is fenced by nothing (R17) and
appears in the task list only as a disambiguation note.

**An earlier draft of this paragraph said 17 and 13.** That figure was computed once, in
the first analysis pass, with a regex that also caught a `relay-tutorial` file — then
quoted in three documents across two more passes without being recomputed after twenty-odd
tasks were added. It is the input to T114's split decision, which makes it the wrong number
to have been casual about.

**Decision.** The documentation half — the error reference, the registry consolidation,
`docs_url`, the slugifier, the sealed package — is sequenced **last**, so the split can
be decided by counting the page rather than by discovering the overrun. That is the
method chapter 3.8 used deliberately and chapter 3.11 confirmed by not needing it.

If it splits, the milestone stays with the second half, because the Phase 2 exit
criterion is the second half.

---

## R20 — Chapter 3.13 needs a row before the deferral is real

**Decision.** `docs/07-tutorial-plan.md` gains a 3.13 row for the public channel and
user surface — the rest of FR-CHN, FR-USR-03/04, and the key management chapter 3.2
deferred — and a paragraph recording why Part 3's milestone no longer sits last.

FR-022 makes this a requirement rather than a courtesy: the project's rule is that a
deferral has a chapter number rather than a promise, and chapter 2.8's promise to "Part
3's tenancy work" is the eleven-chapter demonstration of what happens without one.

---

## R21 — What lands in the chapter's fences and what lands in post-series

**Three destinations, not two.** An earlier draft of this table had two and put four
changes in the wrong one.

| Change | Where |
|---|---|
| the gauntlet, the structural check, the socket suite | chapter fences |
| the two endpoints and their tests | chapter fences |
| the registry consolidation, `docs_url`, `serve()`'s option | chapter fences |
| `packages/outsider` and its lint rule | chapter fences |
| `eslint.config.mjs`'s restored itest ban (R23) | chapter fences |
| `turbo.json`'s env entries | chapter fences |
| `sentinel.sql`'s four tables and the `to_jsonb` fix | **post-series** |
| `services/gateway/src/limits.itest.ts`'s port | **neither — the file is not fenced** |
| `docs/08-error-reference.md` | **outside the chain** — a source document, mirrored |
| the slugifier, `lib/docs.ts`, the two shell scripts | **outside the chain** — tutorial-repo files |

**Why the third destination exists.** `scripts/check-fence-chain.mjs:38` resolves every
fence title against `relay-platform`, so a file in `relay-tutorial` or in the parent
repository's `docs/` cannot be fenced at all — it is covered by `pnpm build` and
`pnpm check:docs` instead. The earlier draft filed the slugifier and the two shell
scripts under "chapter fences", which would have sent implementation looking for a
mechanism that does not apply to them.

**And one row is empty on both sides.** Neither `limits.itest.ts` is fenced anywhere
(R17), so the port fix needs no fence entry of any kind.

The rule for the first column is the one the tutorial plan states: a chapter may only
fence a change it discusses. The guard is feature 030's surface and teaches no chapter.

---

## R22 — The coverage lane does not run from a clean shell

**Measured, by getting it wrong first.** `pnpm coverage` from a shell with only the
compose stack up fails 11 tests across 3 files, and none of the failures names the
cause:

```
limits.itest.ts     the lane must configure a platform credential: expected undefined to be truthy
dispatcher.itest.ts expected undefined to be defined          (× 8, cascading)
outbox.itest.ts     NatsError: CONNECTION_REFUSED
```

The lane needs four variables that exist only in `.github/workflows/ci.yml`:
`RELAY_INTERNAL_CREDENTIAL`, `RELAY_WEBHOOK_SECRET_KEY`, `RELAY_REDIS_URL`,
`RELAY_NATS_URL`. With them, the same commit is 69 files and 668 tests green in 360 s.

Nothing in the repository says so. `README.md` documents `pnpm install / lint /
typecheck / test` and the compose commands; the coverage command appears in the CI
workflow, where the variables are set two screens above it.

**Decision.** The baseline phase records the working invocation, and the chapter's own
quickstart carries it. Fixing it properly — a documented default, or a lane that fails
with one clear message instead of eleven confusing ones — is not scheduled here and is
recorded rather than absorbed. This chapter's subject is a suite that names its own
targets; a lane that fails eleven ways when a secret is missing is the same fault at a
different altitude, and saying so is cheaper than fixing it badly.

---

## R23 — The lint ban Principle I relies on is off for every integration test

**Measured, by running the gate on a file that should have failed it.**

```
$ npx eslint services/api/src/quotas/period.itest.ts
$ echo $?
0
```

That file's first line is `import { and, eq } from "drizzle-orm"`, and it is not in the
ignores list of the block that forbids exactly that import. It passes because
`eslint.config.mjs` has a **second** block, `files: ["**/*.itest.ts"]`, whose `rules`
key also names `no-restricted-imports` — feature 030's restriction on the global-admin
drain functions. In ESLint's flat config, the last configuration for a rule name
**replaces** the earlier one rather than merging with it. So for every `.itest.ts` in the
repository, the `pg` and `drizzle-orm` ban is not in force.

**Constitution I's third bullet says "raw connection access outside that layer is
lint-forbidden".** It is forbidden in two thirds of the tree and permitted in the third
where tests live — which is where a cross-tenant read is easiest to write by accident,
because a test has a database handle in scope already.

**The config states the opposite in a comment**, three lines above the block that
disables it:

```
// `limits.itest.ts` is the one TEST allowed a raw client, and for a reason
// the rule cannot express: its whole subject is that the api and the gateway
// increment the SAME key, and the only way to check that is to read the key
// with neither of their code.
```

Every test is allowed a raw client. The `ignores` entry for
`services/gateway/src/limits.itest.ts` in the first block has been redundant since the
second block was added, and the comment explaining it has been wrong for as long.

**Why this chapter owns it.** User story 6 is "the things that verify isolation are
themselves verified", and this is one of them — a rule the constitution names as a
mechanism, believed to be running, not running. It is the same shape as the guard
watching five tables while a chapter's success criterion reported silence from the four
it was not watching.

**How to restore it without breaking the lane.** The two rule configurations have to
coexist rather than replace each other: either merge both restriction sets into one
block scoped to `**/*.itest.ts`, or move the global-admin restriction to a differently
named rule instance. Then measure which files genuinely need `pg` or `drizzle-orm` — at
least `services/api/src/db/*.itest.ts`, `services/api/src/quotas/*.itest.ts` and
`services/gateway/src/limits.itest.ts` do today — and give each an entry with a reason,
by the same doctrine as `exempt.ts`: a list, not a pattern.

**What it does not buy, said before the chapter claims it.** The rule sees an import.
A test that reaches raw SQL through a helper in another file, or through the repository's
own `db` handle, is invisible to it — which is the boundary feature 030's contracts
already drew for the same rule at a different scope.

---

## R24 — A platform credential is authorized by class and not by service

**Measured.** `credential.guard.ts:26` is the whole vocabulary:

```ts
export const Accepts = (...kinds: PrincipalKind[]) => SetMetadata(ACCEPTS, kinds);
```

Kinds only. There is no way for a route to say "the gateway may call this and the
dispatcher may not". Meanwhile `authenticate.middleware.ts` resolves **two** credentials:

```ts
const PLATFORM_SERVICES = [
  [PLATFORM_CREDENTIAL_ENV, "dispatcher"],
  [GATEWAY_CREDENTIAL_ENV,  "gateway"],
];
```

Both produce `{ kind: "platform", service }`, and `PlatformPrincipal.service` is
documented as "Which internal service presented it, **for logs**". So every
`@Accepts("platform")` route accepts either credential. The gateway's reaches
`POST /internal/dispatch/replay`, whose handler is

```ts
const replayed = await replayDeadLetter(this.db, body.dead_letter_id);
```

— a dead-letter id and no environment. That route is unscoped **by design**, because the
dispatcher legitimately serves every tenant. What is not by design is that the gateway can
call it: a compromised or buggy gateway can replay any tenant's dead-lettered webhook.

**Chapter 3.11 wrote the argument for two secrets and stopped one step short.** Its
comment in `authenticate.middleware.ts` says the second property "is worth more than the
log line. The gateway terminates connections from the public internet and the dispatcher
does not, so a shared secret lets the more exposed service set the blast radius for both."
Two secrets stopped them sharing a *secret*. They still share a *surface*.

**And an earlier draft of `contracts/gauntlet.md` argued against testing it** — "what
protects it is the network boundary and the secret, not a scope". A green suite carrying
that sentence would assert a containment the code does not have.

**Decision: `Accepts` grows a service argument, and omitting it stops compiling.**

```ts
type PlatformService = (typeof PLATFORM_SERVICES)[number][1];   // "dispatcher" | "gateway"
type AcceptSpec = "application" | "user" | { platform: readonly PlatformService[] };
export const Accepts = (...specs: AcceptSpec[]) => SetMetadata(ACCEPTS, specs);
```

`@Accepts("platform")` then fails to compile, and the five routes must say which services
they serve — `{ platform: ["gateway"] }` for `/internal/usage/connections`,
`{ platform: ["dispatcher"] }` for the four dispatch routes. The service vocabulary is
derived from `PLATFORM_SERVICES` rather than retyped, so a third internal service widens
the type on its own. That is chapter 3.11's own lesson from `Dimension`: adding the config
key widened the type and the two-way ternary underneath it was the thing the compiler
could not see.

**Rejected: an optional second decorator** (`@AcceptsService("gateway")`). Two decorators
that must agree is the shape whose failure this project has recorded three times — the
lint list and `exempt.ts`, the sync glob and the docs registry, the guard's array and its
refusal message. An optional argument is a required argument nobody supplied.

**Rejected: leaving it and reporting it.** That was the option on the table, and it was
declined: the gauntlet would then ship an attack whose expected result is "succeeds", and
a suite that documents a hole is not the suite constitution I asks for.

**The refusal gets its own code: `wrong_credential_service`.** It belongs beside
`wrong_credential_type` in the registry, because it is the same kind of distinction one
dimension over — the class presented is right and the *service* is not, which is neither
"you lack a permission" (`forbidden`) nor "you presented the wrong kind of credential".
Chapter 3.2 made exactly this argument when it refused to answer a wrong-credential mistake
with a generic 403, on the grounds that the SRS names it the most common first-integration
failure. The status stays `403` and the code is named by the thrower, which is 3.2's
mechanism.

The message names the service and the permitted set — `"gateway" is not permitted on this
route (dispatcher)` — and never the credential, which is NFR-SEC-06 and the reason
`credential.guard.ts` already says the message "names the class and never the credential".
A service name is a deployment label, not a secret.

**So the emittable set grows to thirteen across this chapter.** R8 counted eleven and was
right for the code as it stands; this adds one and FR-CHN-07 adds another. Every figure
describing what ships says thirteen, and
the reference document's two-directional test is what fails if one of the six documents
carrying that count is missed.

**What this does not fix.** A credential is still a shared secret with no rotation story,
and `service` is still self-reported by which variable matched rather than proven. The
change narrows which routes a leaked credential reaches; it does not make a leak
survivable.

---

## R25 — The sealed package has nowhere to run, and the fix is the reader's own command

**Measured.** Nothing starts the api or the gateway for it, and it cannot start them
itself.

- `.github/workflows/ci.yml` contains no `docker compose` and no `pnpm dev`. The
  integration lane passes because each suite spawns the children it needs.
- The way they do it is `spawn("node", [join(REPO, "services","api","dist","main.js")])`
  with `REPO = join(HERE, "..", "..", "..")` — the level-3 escape R12 now forbids for this
  package.
- `compose.yaml` puts `api`, `gateway` and `dispatcher` behind `profiles: ["services"]`,
  so `docker compose up -d --wait` starts stores only. The api maps to host `4000`, the
  gateway to `4001`.

**Decision: compose starts the platform, in a CI job of its own.** The package reads
`RELAY_API_URL` and `RELAY_WS_URL` and starts nothing — which is what an integrator does,
and the reason to prefer compose over backgrounding `pnpm dev`: the target is genuinely
external, and the command is the one the published documentation already gives.

**And the trap that makes it a separate job rather than three lines in the existing one.**
The platform job uses GitHub *service containers* for Postgres, Redis and NATS on
`localhost:5432`. Compose's api reads
`DATABASE_URL: postgres://relay:relay@postgres:5432/relay` — its own network, its own
Postgres. Adding `--profile services` to the existing job would start a second database,
migrate the first, and leave the api serving a schema that does not exist. So the sealed
integration runs in a job that uses compose for everything:

```
docker compose up -d --wait                              # stores; postgres on host 15432
DATABASE_URL=postgres://relay:relay@localhost:15432/relay \
  node services/api/dist/db/migrate.js                   # before the api needs the schema
docker compose --profile services up -d --wait           # api 4000, gateway 4001
node scripts/seed-demo-tenant.mjs                        # prints a credential
RELAY_API_URL=http://localhost:4000 RELAY_WS_URL=ws://localhost:4001 \
  pnpm --filter @relay/outsider test:integration
```

That ordering is load-bearing: the seed writes to a migrated database, and the api needs
the schema before it serves anything the integration asks for.

**Cost, stated rather than discovered.** The job builds two Node images from
`services/api/Dockerfile` and `services/gateway/Dockerfile` on every run. That is the
price of the target being external, and it is the same build a reader pays once.

---

## R26 — Where the error-reference completeness check can actually live

**Two problems with putting it in the platform's unit lane, both measured.**

`docs/08-error-reference.md` is in the parent repository, outside `relay-platform`.
Turbo's `test` task declares `inputs: ["$TURBO_DEFAULT$", "$TURBO_ROOT$/compose.yaml"]`,
and `$TURBO_ROOT$` is the platform workspace — a file above it cannot be an input. So
editing the reference and re-running `pnpm test` returns a cache hit and the gate passes
stale.

And `relay-platform` is a submodule with its own remote
(`git@github.com:anhba817/relay-platform.git`), whose README promises "check it out and
the toolchain checks pass". A unit test requiring `../docs/08-error-reference.md` fails in
a standalone clone, where that path does not exist.

**Decision: split the check along the repository boundary.**

| Side | Assertion | Why there |
|---|---|---|
| platform | every code the platform can emit is in `ERROR_CODES` | self-contained; no parent, no cache hole |
| tutorial | `ERROR_CODES` ↔ the reference's `h2` headings, both directions | the parent is already in scope, and `check-docs-drift.sh` sets the precedent — it reaches into `../docs` and skips with a warning when the parent is absent |

The tutorial side reads `packages/protocol/src/codes.ts` as text, which the fence chain
already does for every published file, so the coupling is one the repository is built on
rather than a new one.

---

## R27 — Two governing-document gaps the gauntlet walks into rather than causes

**`GET /v1/webhooks` does not paginate.** The controller is
`list() { return this.webhooks.list(); }` — no `limit`, no `cursor`, a bare array back.
EIR-API-06 is P1: *"List endpoints shall use opaque cursor pagination with `limit` and
`cursor` parameters, returning `next_cursor` and `has_more`. Offset pagination shall not be
offered."* Unmet since chapter 3.5 shipped the route.

It matters here only because the `list` attack shape asserted "an empty page rather than a
404", and there is no page. The shape asserts an empty **result** in whatever form the
endpoint returns, and the gap is recorded as found. Fixing it is a public-API change that
belongs with FR-CHN-08's listing work in chapter 3.13, where cursor pagination has to be
built anyway.

**And the ADR question FR-044 reopened.** The plan said "no ADR required", written before
`Accepts` grew a service argument. Constitution VII requires every architecture decision to
be recorded as an ADR with drivers, rejected alternatives and reversal condition, and
narrowing platform credentials from a class to a named service changes the internal trust
model.

Chapter 3.11's precedent covers it, and the plan now says so rather than letting the older
sentence stand: 3.11 gave each internal service its own credential without an ADR, on the
grounds that it "narrows an existing mechanism rather than adding one". FR-044 narrows the
same mechanism one step further — the same class, a smaller set of callers per route. What
would need an ADR is a new authorization *mechanism*: roles, scopes, a policy engine. None
of those is here.
