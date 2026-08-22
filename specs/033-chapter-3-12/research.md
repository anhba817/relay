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
eight other api suites do the same.

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

## R5 — The internal surface, and what its credential is trusted for

**Finding.** `RELAY_INTERNAL_CREDENTIAL` is not scoped to an environment, by design:
one gateway and one dispatcher serve every tenant, and each names the environment in
the request. `credential.guard.ts` resolves it to a principal with no environment, and
`@Accepts("service")` routes read the environment from the body.

So "attack with a foreign credential" is meaningless on `/internal/*`. The attack that
means something is a request that **names one environment and carries an identifier
from another** — and chapter 3.11 already built one instance of the refusal:
`usage.controller.ts` answers `409 connection_environment_conflict` when a report names
a connection whose row carries a different environment, on the grounds that "a
connection moving tenants is either a bug or an attempt".

**Decision.** All eight internal routes are attacked in that shape. The chapter states,
in prose, that the internal credential is a tenant-*selection* authority and that what
protects it is the network boundary and the secret — not a scope. A green suite that
left that unsaid would imply a containment the code does not have.

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

**One asymmetry to state.** `packages/protocol`'s frame union has ten types and only
some are inbound. The suite attacks the inbound ones and lists the outbound ones as
not-attackable, derived from the union rather than typed out, so a new inbound frame
appears in the list.

---

## R7 — The structural check, and one table that fails it

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

**And one does not fit any of those categories.**

```
outbox: id, subject, payload, created_at, published_at
```

The `outbox` holds product events and carries no tenant column and no foreign key.
Constitution I's second clause reads *"Every persisted operational and analytical
record MUST carry a non-null tenant (`environment_id`) identifier, directly or through
a single foreign-key hop"*. The outbox's tenant is inside `payload` — measured, the
JSON keys are `id, data, type, occurred_at, environment_id`, and the subject's last
segment is the environment id as well (`events.msg.created.<uuid>`). A jsonb key is
neither a column nor a hop. `exempt.ts` records the consequence without naming the
cause: "`outbox` is not among them and needs no entry", which is true because the
guard's trigger condition is `__is_sentinel(OLD.environment_id)` and the outbox has no
such column to test.

**Measured cost of fixing it: one insert site.** `repository.ts:2823` is the only
`insert(outbox)`, it sits inside `Repository`, which already holds `this.environmentId`,
and the backfill is exact because the payload carries the id. The test lane's outbox
holds **286,871 rows**, so the backfill is a real statement rather than a no-op.

**Decision: record it, do not fix it here, and name what recording costs.** A migration
on the write path of every message send does not belong in a milestone chapter, and this
chapter is already carrying two new endpoints, a documentation surface, and three
inherited debts. But an exception to a constitutional MUST is not something a test's
allow-list may quietly grant: the governance section requires a conflict to be
"resolved explicitly by amendment rather than ignored". So the exception list carries
the entry, the reason, and the measured cost, and the finding is escalated as a
governance decision — fix the column or amend the clause — rather than absorbed.

---

## R8 — There are eleven error codes, and the registry holds six

**Measured.** The set the platform can emit, by source:

| Source | Codes |
|---|---|
| `packages/protocol/src/codes.ts` (`ERROR_CODES`) | `invalid_frame`, `unknown_frame_type`, `unauthorized`, `rate_limited`, `wrong_credential_type`, `quota_exceeded` |
| `protocol-error.filter.ts` status ladder | `invalid_request`, `unauthorized`, `forbidden`, `not_found`, `internal_error` |
| `packages/service-kit/src/index.ts` | `not_found` |
| named at a call site | `connection_environment_conflict` (`usage.controller.ts`) |

Union: **eleven**. The registry holds six. Five of the eleven exist only as string
literals inside a ternary ladder, and one exists only at a call site. Nothing anywhere
enumerates the eleven, which is why "document every error code" could not have been
done from the registry — the spec's FR-026 exists because of this measurement.

**Decision.** Make the registry the set by construction: add the five missing keys,
type the filter's ladder as `ErrorCode` so the compiler refuses an unregistered code,
and reference the registry from the call sites that name their own code. Then
`Object.keys(ERROR_CODES)` is the derivation FR-025 asks for, and the reference
document's completeness test compares two lists rather than grepping source.

**Rejected.** Deriving by grep over the source tree. It would have to match a ternary
ladder and would go stale the first time someone formatted it differently — a
derivation that can silently under-report is the same fault as an empty target list.

**Cost, counted rather than estimated.** Five registry keys, one typed ladder, six
call sites naming a code (`rate-limit.middleware.ts` ×2, `credential.guard.ts` ×2,
`usage.controller.ts`, `messages.service.ts`, `session.controller.ts`,
`gateway/session.ts` — eight, in fact, once both spellings are counted).

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

**Two things that need no work, measured.** `doc-page.tsx` renders the "referenced by"
line under `citing.length > 0 &&`, so a document no chapter cites renders cleanly — and
no chapter cites this one. And the Vietnamese route renders the same English markdown
under a translated title, with a standing note that source documents are kept in
English, so the reference needs a `titleVi` and no translation.

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

**And the hole.** A relative path is not a package specifier. `../../services/api/dist/…`
resolves regardless of any dependency list, and this repository already does it:
`packages/e2e/src/harness.ts` uses `createRequire` to load the api's build output
precisely because it may not declare `pg`. So the seal needs a lint rule after all —
not for package names, which pnpm handles, but for relative and absolute paths escaping
the package directory.

**Decision.** `packages/outsider`, dependency list empty of `@relay/*`, plus a
`no-restricted-imports` pattern rule on paths climbing out of it. The chapter states
which half is mechanical and which is a rule, because a rule trusted past its range is
the thing feature 030's contracts warn about.

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
customer supplies, which is FR-USR-02's "created implicitly on first authentication"
read one step earlier — implicitly on first *membership*.

**Status codes.** `201` on creation and `200` on the idempotent repeat, which is the
distinction chapter 2.3 already draws for a duplicate send and the one an integrating
developer can act on. FR-CHN-02 says "return the existing channel rather than an
error", not "return the same status".

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

## R17 — The fixed port, and why it is not this chapter's file

**Finding.** `services/api/src/limits/limits.itest.ts` binds `?? 4124`.
`startApi()` in the same lane binds 4123. Vitest runs files in parallel, and back to
back a previous run's child can still hold the port — at which point the new child dies
on `EADDRINUSE` and `waitForHealth` gets its 200 from the **old** api, serving a
different environment's signing secret. Chapter 3.11 spent a diagnosis on three
assertions that named none of that.

**Decision.** A random high port, as `session.itest.ts` and `meter.itest.ts` now use.
The file is chapter 3.8's fence, so the change lands in
`relay-tutorial/fences/post-series.md` — a published chapter may only fence what it
teaches, and 3.8 does not teach port selection.

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
package, and three inherited debts. Two chapters in this part have already exceeded the
2,000–4,000 word bound, both discovered afterwards.

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

| Change | Where |
|---|---|
| the gauntlet, the structural check, the socket suite | chapter fences |
| the two endpoints and their tests | chapter fences |
| the registry consolidation, `docs_url`, `serve()`'s option | chapter fences |
| `docs/08-error-reference.md` | a source document, mirrored |
| the slugifier's one character, the docs registry, the two script lists | chapter fences |
| `packages/outsider` and its lint rule | chapter fences |
| `sentinel.sql`'s four tables and the `to_jsonb` fix | **post-series** |
| `limits.itest.ts`'s port | **post-series** |

The rule is the one the tutorial plan states: a chapter may only fence a change it
discusses. The guard is feature 030's surface and teaches no chapter; the port is
chapter 3.8's file and this chapter does not teach port selection.

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
