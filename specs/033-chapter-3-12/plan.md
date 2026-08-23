# Implementation Plan: Chapter 3.12 — Milestone: the isolation gauntlet

**Branch**: `033-chapter-3-12` | **Date**: 2026-08-22 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/033-chapter-3-12/spec.md`

## Summary

The SRS Phase 2 exit criterion, and NFR-SEC-09's suite — cross-tenant access verified
against every endpoint on every build. Constitution I requires that suite by name and
the repository has eleven isolation assertions across eight files instead (T033 counted
them; earlier drafts of this plan said nine across nine).

What research settled, and four of these came from measuring rather than reading:

- **The target list is derived from the express router, not from Nest's metadata and
  not from a list.** Both were probed against the booted application: the router gives
  22 normalised paths with string verbs, the metadata gives 22 entries with
  double-slash join artifacts and numeric enums off a private Nest key. The router is
  also the right authority — the fault FR-002 describes is a route that exists and is
  unattacked, and only the router knows what exists. The derivation asserts a non-zero
  count and a known route, because a suite whose target list can silently empty is
  worse than the hand-written one it replaces (R2).
- **The oracle was already written, once, in the file that needed it.**
  `messages.itest.ts` compares whole error bodies minus `request_id` and says why:
  "comparing them whole is how this suite proves a foreign resource is
  indistinguishable from an absent one". The chapter lifts that helper and applies it
  to 22 routes. Nothing about the assertion is new; its scope is (R3).
- **Every attack needs a twin.** Indistinguishability cannot be tested from one
  response, so each target is paired: another tenant's id against an id that exists
  nowhere. That forces a four-shape classification — and a fifth treatment the
  specification did not anticipate, because `POST /auth/dev-token` takes no identifier
  and is still tenant-scoped: the attack there is on the credential, not the id (R4).
- **The gauntlet is not in `packages/e2e`.** The coverage config excludes it by name,
  so a suite living there could not contribute to constitution VI's 100%-branch clause
  on isolation code — which FR-040 requires this chapter to measure. The REST half
  boots `AppModule` in process, the way eleven api suites already do — counted, after an
earlier draft said nine (R1).
- **`/internal/*` is two credential classes and needs two attacks.** Three routes are
  `@Accepts("user")` and carry an end-user token that **is** scoped to one environment, so
  their attack is a foreign credential. Five are platform routes whose credential carries
  no environment, so theirs is a request naming one environment with an identifier from
  another. An earlier draft of this plan had one shape and would have given three routes
  an attack that does not apply (R5).
- **A platform credential is authorized by class and not by service, and this chapter
  fixes that.** `Accepts` takes `...kinds: PrincipalKind[]`, both credentials resolve to
  `{ kind: "platform", service }`, and `service` is documented "for logs" — so the
  gateway's credential reaches `POST /internal/dispatch/replay`, whose handler takes a
  dead-letter id and no environment. Chapter 3.11 wrote the argument for two secrets and
  stopped one step short: two secrets stopped the services sharing a secret, and they
  still shared a surface. `Accepts` grows a service argument typed so that
  `@Accepts("platform")` stops compiling (R24, FR-044).
- **There are eleven error codes and the registry holds six.** Five live only as string
  literals in a status-to-code ternary ladder, one only at a call site. So "document
  every code" could not have been done from the registry: the registry becomes the set
  by construction — five keys added, the ladder typed as `ErrorCode` — and then
  `Object.keys` is the derivation FR-025 asks for (R8).
- **`docs_url` is built in six places, and the awkward one is dependency-free on
  purpose.** `packages/service-kit` declares no dependencies at all, and `serve()` has
  exactly one caller. So the dependency inverts for free: `ServeOptions` gains a
  required field, the compiler makes the one caller supply it, and service-kit stays
  empty (R9).
- **The anchor is a one-character change with a measured blast radius.** The site's
  slugifier turns `_` into `-`, so `#quota_exceeded` could never match a heading —
  which would have meant one transformation rule maintained in two repositories with no
  way to test the pair. Preserving underscores instead changes exactly one anchor in the
  whole site (`ADR-03 … last_sequence …`) and nothing links to it: zero chapter headings
  contain an underscore, and zero links to any docs anchor exist (R10).
- **The sealed package had nowhere to run, and compose is the answer.** Nothing starts
  the api or gateway for it: CI has no compose step and no `pnpm dev`, and every existing
  suite spawns its own children through a relative path escape this package forbids
  itself. So compose starts the platform in a CI job of its own — a separate job, because
  the platform job's GitHub service containers sit on `localhost:5432` while compose's api
  reads `postgres:5432` on its own network, and mixing them would migrate one database
  and serve from another (R25).
- **The seal is three levels, not two.** An earlier draft said the remaining hole was a
  relative-path import "which only a lint rule closes". A path built at run time —
  `join(HERE, "..", "..", "..")`, `createRequire` — is not an import specifier, and
  `no-restricted-imports` never sees it. `harness.ts`, cited as proof the hole exists, is
  also proof the proposed rule does not close it. Level 3 is a `no-restricted-syntax` rule,
  which the config does not have today (R12).
- **pnpm already seals the sealed package, and the hole is a relative path.**
  `node_modules/@relay` does not exist at the workspace root, so a package that declares
  no `@relay/*` dependency cannot resolve one. `vitest`, `ws` and `jose` do resolve from
  the root, so the package can still run. What no dependency list stops is
  `../../services/api/dist/…` — and `packages/e2e/src/harness.ts` does exactly that
  today with `createRequire`. The seal is a package manager plus a lint rule, and the
  chapter says which half is which (R12).
- **The guard extension is one expression, and it was measured on both shapes.**
  3.11's R5a predicted `record "old" has no field "id"` and the probe reproduced it.
  `coalesce(to_jsonb(OLD) ->> 'id', to_jsonb(OLD)::text)` gives an id where there is one
  and the row's JSON where there is not, with no per-table branch (R15).
- **The two endpoints cited two clauses and sat beside four more that nobody read.**
  `channels.type` has been a `"public" | "private"` column since 2.1 and **nothing reads
  it**, so FR-CHN-05 — a P1 clause forbidding non-members from reading, sending or
  observing presence in a private channel — is unimplemented. A public create endpoint
  accepting `private` would sell a guarantee the platform does not keep, so the documented
  enum has one member and FR-CHN-03's private half goes to 3.13 with FR-CHN-05. FR-CHN-07's
  1,000-member ceiling appeared in no artifact, and the SRS names its status **and** its
  code — `channel_member_limit_exceeded`, in its own worked example for EIR-API-04. And
  FR-CHN-01 has four elements where the first draft delivered three; `channels.metadata`
  already exists (R14, R27).
- **`addMember` cannot serve the members endpoint as written.** It has no
  `ON CONFLICT`, and `members`' primary key is `(channel_id, user_id)`, so a repeat
  raises a unique violation that the filter would render as `internal_error`. Its single
  boolean also conflates "added", "channel not yours" and "user not yours" — which is
  the right answer for isolation and the wrong one for an endpoint that must be
  idempotent. The endpoint needs a scoped existence check and an upsert, not a wrapper
  (R14a).

- **Constitution VI's 100% clause is 25 branch arms away, and the reporters cannot name
  them.** `repository.ts` measures 241/266 branches on this feature's starting commit —
  3.11 closed at 90.57% and this run reads 90.60%, run-to-run drift rather than a change —
  a countable distance nobody has
  ever stated, on a file with 100% function coverage and two uncovered lines, so almost
  all of it is unhit arms on covered lines. `json-summary` emits totals and not
  locations, so FR-040's "name every uncovered branch" needs one more reporter. Found by
  trying to list them and getting a file that does not contain them (R16).
- **The coverage lane does not run from a clean shell**, measured by getting it wrong
  first: 11 failures across 3 files, none naming the cause, because four variables live
  only in the CI workflow. With them, 69 files and 668 tests green in 360 s. Nothing in
  the repository says so (R22).

- **The lint ban Principle I names as a mechanism is off for every integration test.**
  `eslint.config.mjs` has a second flat-config block for `**/*.itest.ts` whose `rules`
  key names `no-restricted-imports` again, and in flat config the last configuration for
  a rule name replaces the earlier one — so the `pg` and `drizzle-orm` restriction does
  not apply to any test. Measured: `npx eslint services/api/src/quotas/period.itest.ts`
  exits 0 while that file imports `drizzle-orm` and is not in the ignores list. The
  config's own comment says one named test is "the one TEST allowed a raw client"; all of
  them are (R23).
- **The fixed port is in the other file with that name, and nothing fences either.**
  Two files are called `limits.itest.ts`; the `?? 4124` is the gateway's, and an earlier
  draft of this plan named the api's — which binds no port. Neither is fenced by any
  chapter or by post-series, so the fix needs no fence work, and the
  `RELAY_LIMITS_ITEST_API_PORT` override that exists is unreachable because `turbo.json`
  does not declare it (R17).

And one finding that reversed itself under a second look. **`outbox` has no tenant
column and zero foreign keys**, and an earlier draft of this plan escalated that as a
Principle I violation and proposed adding the column. Three of the four arguments for it
do not survive: nothing wants a tenant-scoped read of the outbox, its legitimate mutation
is cross-environment so the column would make feature 030's guard refuse the relay's own
sweep, and the single insert site already holds the environment. A foreign key would also
block deleting an environment while outbox rows exist, which makes FR-TEN-08 harder. So
`outbox` is infrastructure, beside `consumed_events` — no column, no amendment (R7).

**What survives is a retention problem, and it is worse.** `drainOutbox` sets
`published_at` and never deletes; nothing in the api deletes a row from any table; and the
payload is a full copy of the message including its text. That collides with DR-06 and
FR-MSG-08 (a tombstone that leaves a copy behind), FR-TEN-08 (30-day erasure) and
FR-MOD-06 (scheduled retention). The fix is pruning, which needs no tenant column, and it
belongs to FR-MOD-06's chapter rather than to this one (R7a).

## Technical Context

**Language/Version**: TypeScript 5.x on Node.js 22 throughout (constitution VII). The
guard's PL/pgSQL gains one expression; the argument for it not needing an ADR is
feature 030's and unchanged.

**Primary Dependencies**: NestJS 11 for the api and `@nestjs/testing` for the
in-process boot the gauntlet needs, Drizzle inside the repository layer, `ws` for the
socket attacks, zod through `@relay/protocol`. One new workspace package
(`packages/outsider`) that declares none of them. Nothing added to the dependency tree.

**Storage**: PostgreSQL. **No product migration.** The two endpoints wrap repository
functions that already exist against tables chapter 2.1 created, and the unique
constraints their idempotency needs are already there —
`channels_environment_id_external_id_unique`, `users_environment_id_external_id_unique`,
and `members`' composite primary key. The only SQL this chapter writes is
`packages/test-harness/src/sentinel.sql`, which is never a migration.

**Testing**: Vitest, and the placement is a decision rather than a convention.
`services/api/src/isolation/` boots `AppModule` in process so its branches land in the
coverage run; `services/gateway/src/isolation.itest.ts` uses the lane that spawns a
live api child, because a socket needs a real gateway; `packages/outsider` runs in the
integration lane over HTTP with no workspace imports at all. `packages/e2e` gains
nothing — it is excluded from coverage by name (R1).

**Target Platform**: Linux server, the same compose stack, plus the published tutorial
site for the one requirement that is verified against a URL rather than a process.

**Project Type**: Monorepo service work, a new test-only package, a new source
document, a published tutorial chapter, and edits to the tutorial site's docs registry.

**Performance Goals**: None new. The gauntlet's cost is lane time, and the budget is
that `pnpm test:integration` stays inside the twenty-run battery's current 193 s mean
without a new order of magnitude. 22 routes × 2 requests plus the socket set is small
beside the 330 tests already there.

**Constraints**: The chapter's published page measures 2,000–4,000 prose words, and
this chapter carries more than any other in Part 3 — so the documentation half is
sequenced last, to be cut with a number rather than discovered (R19). **The fence
surface is 16 new files and 21 amended**, 37 against chapter 3.11's 21 files and 34
fences: every amended file needs a diff fence in this chapter's own prose or the chain's
HEAD property fails, which puts a floor under the page length that a word count alone
does not see. The chain is byte-exact across 177 files and 28 chapters, resolves every
title against `relay-platform` — so tutorial-repo files and the parent's `docs/` cannot
be fenced at all — and sees every `docs_url` that changes.

**Scale/Scope**: 22 api routes — one of them `/healthz` — plus one WebSocket path and one
more health endpoint on the gateway; the dispatcher runs no HTTP server. 22 base tables,
thirteen error codes after this chapter adds two, two new public endpoints, five internal
routes gaining a declared service, four newly guarded tables, one restored lint rule, one
new CI job, three inherited debts and four this chapter found for itself, one new package,
one new document.

## Constitution Check

*GATE: passed before Phase 0, re-checked after Phase 1 design.*

| Principle | Check | Verdict |
|---|---|---|
| **I. Tenant isolation is a correctness property** | This chapter **is** the principle's fourth bullet — "an automated cross-tenant access test suite MUST attack every endpoint with foreign IDs on every build" — which has been unmet since the clause was written. The two new endpoints are scoped in the repository layer, not in their handlers, and `addMember`'s existing behaviour (false for a foreign channel *or* a foreign user, no error) is the oracle rather than a bug. FR-044 narrows platform credentials from a class to a named service, so the gateway's credential stops reaching the dispatcher's routes, and FR-046 gives that refusal its own code rather than a generic 403. | **Pass on the clause this chapter delivers, and one clause found failing.** The third bullet — "raw connection access outside that layer is lint-forbidden" — is not in force for any `.itest.ts`, measured in R23 and in scope here as FR-043. The second bullet holds: `outbox` and `consumed_events` carry no tenant identifier and are infrastructure rather than records, which R7 reached only after an earlier draft escalated `outbox` wrongly. What the outbox does have is a retention problem that four requirements care about, recorded in R7a and owned by FR-MOD-06's chapter |
| **II. No acknowledged message is ever lost** | Nothing touches the write path. The clause that does apply is idempotency on write endpoints "enforced at the storage layer (unique index), not in application memory": channel creation's key is the customer's own identifier under `channels_environment_id_external_id_unique`, and membership's is `members`' composite primary key. Both predate this chapter; R14a is the finding that the current helper does not yet honour the second one. | Pass |
| **III. Two data paths, never crossed** | Nothing analytical. No ClickHouse, no queue, no metering. | Pass |
| **IV. Single writer, single source of truth** | The api stays the only writer. `packages/outsider` cannot import `pg` — it cannot import anything — and the gauntlet writes through the repository like every other suite. | Pass |
| **V. API-first, developer-first** | The clause "every error code has a reachable documentation page" has been unmet since chapter 1.4 and is closed here for all thirteen codes. `docs_url` stops being a placeholder. The two new endpoints are the first public surface for FR-CHN since Part 2 promised it. | **Pass, and it closes the debt three chapters recorded** |
| **VI. Requirement-driven, test-verified** | **48 requirements, 33 measurable outcomes** — re-derive with `grep -c '^- [*][*]FR-' spec.md` and the same for `SC-`, never carried forward by hand. The 100%-branch clause for isolation code is measured against a number rather than restated (FR-040). The suite this principle names as a release gate is what the chapter builds. | Pass |
| **VII. Boring by design — scope is a commitment** | No new service, no new language, no new dependency, no product migration. One new workspace package, which is a test package and not a service, so §4.2's "deliberately not a separate service" table does not apply. Everything larger is named and refused: the rest of FR-CHN and FR-USR go to 3.13 with a number, the outbox column goes to whoever next touches outbox writes, a human external-developer run is named as the instrument this chapter does not use. | Pass, with three refusals recorded |

**One entry in Complexity Tracking, and still no ADR — restated against FR-044, which did
not exist when this sentence was first written.** Constitution VII requires an ADR for an
architecture decision, and narrowing platform credentials from a class to a named service
touches the internal trust model. Chapter 3.11's precedent covers it: it gave each internal
service its own credential without an ADR because that "narrows an existing mechanism
rather than adding one", and FR-044 narrows the same mechanism one step further. What would
need an ADR is a new authorization *mechanism* — roles, scopes, a policy engine — and none
is here (R27). `packages/outsider` is a new
workspace package whose whole design is a negative — it may import nothing — and a
package that exists to be empty needs its justification written down.

## Project Structure

### Documentation (this feature)

```text
specs/033-chapter-3-12/
├── plan.md              # This file
├── research.md          # Phase 0 — R1 to R27 plus R7a, twenty measured on a running stack
├── data-model.md        # Phase 1 — no product migration; the shapes the suite derives
├── quickstart.md        # Phase 1 — V0 to V16, the reintroductions among them
├── contracts/
│   ├── gauntlet.md      # the derivation, the four shapes, the fifth treatment,
│   │                    # and what the suite does not cover
│   └── errors.md        # the thirteen codes, the registry as the set, the URL rule
├── checklists/
│   └── requirements.md  # 16/16, with the three items read against a stated reading
└── tasks.md             # Phase 2 — /speckit-tasks, not created here
```

### Source Code (repository root)

```text
relay-platform/
├── README.md                                  # the compose sequence the outsider needs (R25)
├── eslint.config.mjs                          # the outsider's two rules; the itest ban restored (R23)
├── turbo.json                                 # env entries — strict mode filters what it does not declare
├── vitest.coverage.config.mts                 # the json reporter, then ratchet entries (FR-040)
├── packages/
│   ├── outsider/                              # NEW — the sealed integration
│   │   ├── package.json                       #   no @relay/* dependency, by design
│   │   ├── vitest.integration.config.mts
│   │   └── src/integrate.itest.ts             #   signup → channel → members → send → socket
│   ├── protocol/src/codes.ts                  # thirteen codes; docsUrl() beside them
│   ├── service-kit/src/index.ts               # ServeOptions gains a required field
│   └── test-harness/src/
│       ├── sentinel.sql                       # four tables, to_jsonb(OLD) (POST-SERIES)
│       └── exempt.ts                          # entries if the gauntlet needs any
├── scripts/seed-demo-tenant.mjs               # NEW — the credential an outsider can get
└── services/
    ├── api/src/
    │   ├── channels/                          # NEW — the two endpoints
    │   │   ├── channels.controller.ts
    │   │   ├── channels.schema.ts
    │   │   ├── channels.service.ts
    │   │   └── channels.itest.ts
    │   ├── db/catalogue.ts                     # NEW — the information_schema read, where drizzle is allowed
    │   ├── db/repository.ts                   # addMember's and createChannel's upserts (R14a)
    │   ├── isolation/                         # NEW — the gauntlet, in process
    │   │   ├── targets.ts                     #   the derivation + its non-empty assertion
    │   │   ├── attack.ts                      #   the twin-request oracle, lifted from 2.2
    │   │   ├── gauntlet.itest.ts              #   22 routes, four shapes, one fifth
    │   │   └── tenant-scope.itest.ts          #   FR-TEN-06 from the live catalogue
    │   ├── limits/rate-limit.middleware.ts    # docsUrl() ×2
    │   ├── auth/credential.guard.ts           # registry codes ×2; AcceptSpec (R24)
    │   ├── auth/authenticate.middleware.ts    # PlatformService derived from its own list
    │   ├── internal/usage.controller.ts       # registry code
    │   ├── messages/messages.service.ts       # registry code
    │   ├── internal/session.controller.ts     # registry code
    │   └── protocol-error.filter.ts           # the ladder, typed as ErrorCode
    └── gateway/src/
        ├── isolation.itest.ts                 # NEW — the socket attacks
        ├── limits.itest.ts                    # random port — NOT fenced anywhere (R17)
        ├── main.ts                            # serve()'s new field
        └── session.ts                         # docsUrl() ×2

.github/workflows/
└── ci.yml                                     # the `outsider` job — compose for everything

docs/
├── 04-srs.md                                  # NFR-USE-05 verification note if it moves
├── 07-tutorial-plan.md                        # the 3.13 row, and why the milestone moved
└── 08-error-reference.md                      # NEW — thirteen codes, one h2 each

relay-tutorial/
├── app/(en)/part-3/chapter-12/…/page.mdx      # NEW — the chapter
├── app/(vi)/vi/part-3/chapter-12/…/page.mdx   # NEW — translated
├── components/docs/doc-article.tsx            # slugifyHeading keeps underscores
├── content/docs/08-error-reference.md          # machine-written mirror
├── lib/docs.ts                                # a seventh registry entry
├── lib/tutorial.ts                            # the chapter manifest entry
├── scripts/sync-docs.sh                       # an explicit list, not 0[1-6]
├── scripts/check-docs-drift.sh                # the same list
├── app/(en)/part-1/chapter-04/…/page.mdx      # REVISED — prose calling docs_url a placeholder
├── app/(en)/part-3/chapter-02/…/page.mdx      # REVISED — illustrative JSON no checker sees
└── fences/post-series.md                      # sentinel.sql and exempt.ts only

Nothing in the tutorial tree above is fenceable — the chain resolves titles against
`relay-platform`. This chapter's own fences are the titled code fences inside its page,
not a file under `fences/`, which holds `post-series.md` and nothing else.
```

**Structure Decision**: three trees, as every Part 3 chapter has used. The two
placements that are decisions rather than convention are `services/api/src/isolation/`
(in process, so coverage sees it — R1) and `packages/outsider` (a package rather than a
directory, because pnpm's package boundary is what does the sealing — R12).

## Phases

Eleven, and the order is load-bearing in two places: the reintroductions cannot run
until the suite is complete, and the documentation half is last so it can be cut.

| # | Phase | Delivers | Notes |
|---|---|---|---|
| 1 | Baseline | provenance, both lanes, coverage, site checks | The lane needs four variables only CI sets, or 11 tests fail without naming why (R22). The starting figure is `repository.ts` at 241/266 branches (R16) |
| 2 | The target list | `targets.ts`, the classification, the non-empty assertion | First red on purpose: an unclassified route fails the suite (SC-002) |
| 3 | The REST gauntlet | `AcceptSpec`, `attack.ts`, `gauntlet.itest.ts` over 22 routes | Five shapes, two internal attacks (R5), and the platform-service authorization the suite would otherwise document as a hole (R24) |
| 4 | The structural check | `tenant-scope.itest.ts`, the infrastructure list | Three classes, not four. Where the outbox retention finding lands as a written entry (R7a) |
| 5 | The socket gauntlet | `services/gateway/src/isolation.itest.ts` | Inbound frame types derived from the protocol union (R6) |
| 6 | The two endpoints | channels + members, both upserts, the member ceiling, `public`-only types | They must appear in the target list without being named there (SC-016). FR-CHN-01 in full, FR-CHN-07 enforced, FR-CHN-03's private half deferred (R14) |
| 7 | The reintroductions | three, run and reverted, recorded | Sensitivity, not correctness. What stayed green is part of the result (R18) |
| 8 | The instruments | guard's four tables, the itest lint ban, the port, the `json` reporter, the coverage number | The guard lands in post-series; the port needs no fence at all (R17). The lint ban is a constitution clause found off (R23); the reporter is what makes FR-040 nameable (R16) |
| 9 | **The documentation half — separable** | thirteen codes, the registry as the set, `docsUrl()`, `turbo.json`'s env entry, the slugifier, `08-error-reference.md`, three lists | Sequenced here so the split is a measurement (R19) |
| 10 | **The outsider — separable** | `packages/outsider`, the seed command, two lint rules, a compose-driven CI job, the gap list, the verdict | Needs phase 6; carries the milestone if the chapter splits. The CI job is what gives the package somewhere to run (R25) |
| 11 | Close-out | chapter prose both locales, fences, the 3.13 row, notes | The plan-table edit is FR-022, not a courtesy (R20) |

Each phase commits. 3.11's traceability regex broke 36 files and cost five minutes to
repair for exactly this reason.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| A new workspace package, `packages/outsider`, whose design is that it may import nothing | The Phase 2 exit criterion is about what an outsider can do with published documentation only. "No insider knowledge" has to be mechanically enforceable or it is an intention, and pnpm's package boundary is the only mechanism in this repository that enforces it — measured: `node_modules/@relay` does not exist at the workspace root, so an undeclared `@relay/*` import cannot resolve (R12) | A directory inside `packages/e2e` was rejected: e2e declares `@relay/api`, `@relay/gateway` and `@relay/protocol`, so every file in it can import all three, and the seal would be a code-review convention. A lint rule alone was rejected as the primary mechanism for the same reason — it is the second line, for relative paths, which no dependency list can stop |
