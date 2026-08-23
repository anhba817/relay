# Feature Specification: Chapter 3.12 — Milestone: the isolation gauntlet

**Feature Branch**: `033-chapter-3-12`

**Created**: 2026-08-22

**Status**: Draft

**Input**: User description: "Start chapter 3.12"

Chapter 3.12 is the SRS Phase 2 exit criterion. It runs NFR-SEC-09 — *"cross-tenant
access shall be verified by an automated test suite covering every endpoint, executed
on every build"* — and it answers §7.3's exit line for Phase 2: *"an external
developer integrates using only public documentation, with no assistance"*.

Constitution I calls FR-TEN-05 the single most important requirement in the system and
requires that suite by name. The repository does not have one. What it has is **eleven
isolation assertions across eight files**, each written by whichever chapter happened
to be thinking about tenancy that week: a foreign channel's history, a foreign
external id, a foreign key that looks like an absent key, a webhook test against
another environment's endpoint, a connection that may not change tenants. Every one of
them is a good test. Together they are not a suite, because nothing anywhere knows
which endpoints have been attacked and which have merely never been thought about.

So the subject is not "write more isolation tests". The subject is **the difference
between a set of assertions and a suite**: a suite knows its own targets, fails when
a target appears that nobody classified, and has been shown to go red for the fault it
exists to catch.

The second half of the chapter is the milestone. Phase 2's exit criterion is not about
code at all — it is about whether somebody outside this repository can integrate — and
measuring it turned up two things the plan did not know. Every error code the platform
emits carries a `docs_url` that resolves to nothing, a placeholder every chapter since
1.4 has carried. And there is no public endpoint to create a channel or add a member:
`packages/e2e/src/harness.ts` says so in a comment written in chapter 2.8 — *"there is
no admin API to create an environment, a user or a channel yet — that is Part 3's
tenancy work"* — and Part 3 ends here.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Every endpoint is attacked, and the target list maintains itself (Priority: P1)

A suite attacks every endpoint the platform exposes with identifiers belonging to
another tenant. It does not attack a list somebody typed: it derives its targets from
the running application, so an endpoint added in a later chapter arrives in the suite
the moment it exists.

Each attack asserts three things, and the third is the one the scattered assertions
mostly do not: no data comes back, no state changes, and the answer is
**indistinguishable from the answer for an identifier that does not exist anywhere**.
A 403 where a 404 belongs is a disclosure; so is a message that echoes the id back;
so is an empty list on one path and a 404 on another for the same class of miss.

**Why this priority**: this is NFR-SEC-09, and constitution I makes a build that
fails it unshippable. Everything else in the chapter reads this suite's verdict.

**Independent Test**: create two environments, walk the derived target list, and
confirm every target is either attacked or carries a written reason for being
exempt. Add a route with no classification and confirm the suite goes red.

**Acceptance Scenarios**:

1. **Given** the api's route table, **When** the suite runs, **Then** every route is
   either attacked with a foreign identifier or listed as taking no tenant-owned
   identifier, with a stated reason.
2. **Given** a new route added after this chapter, **When** the suite runs, **Then**
   it fails until the route is classified.
3. **Given** an endpoint that reads a tenant-owned resource, **When** it is called
   with another tenant's identifier and with an identifier that exists nowhere,
   **Then** the two responses are identical in status, error code, and message.
4. **Given** an endpoint that writes, **When** it is called with another tenant's
   identifier, **Then** the target tenant's rows are byte-identical before and after,
   read directly rather than inferred from the status code.
5. **Given** a list endpoint, **When** it is called by a tenant with no rows, **Then**
   it returns an empty result rather than a 404, and returns nothing belonging to the
   other tenant. The shape of that result is whatever the endpoint returns — the one list
   route the platform has returns a bare array, not a page.
6. **Given** the WebSocket surface, **When** a token minted for one environment is
   used to subscribe to, resume from, or send into a channel belonging to another,
   **Then** each attempt is refused and nothing is delivered.
7. **Given** an internal route that accepts a platform credential, **When** a request
   names one environment and carries an identifier belonging to another, **Then** it is
   refused and nothing is written.
8. **Given** an internal route that accepts an end-user token, **When** a token minted
   for one environment is used against a resource in another, **Then** it is refused and
   nothing is written.
9. **Given** an internal route that accepts a platform credential, **When** the
   credential presented was issued to a different internal service, **Then** it is
   refused with the code reserved for that mistake, and the message names the service and
   the permitted set rather than the credential.

---

### User Story 2 - The suite has been shown to catch something (Priority: P1)

A test suite that has never failed is an untested test. Before the chapter claims the
gauntlet verifies isolation, the isolation is deliberately broken — the
`environment_id` predicate removed from one repository read — and the suite is run.
The chapter records which assertions fired, which did not, and what that says about
the ones that stayed green.

**Why this priority**: feature 030 established the practice for a whole class of
defect and it applies here with more force. Constitution I says a build failing this
suite must not ship, which is a promise about the suite's sensitivity, not about its
existence.

**Independent Test**: revert one scoping predicate, run the gauntlet, confirm it is
red; restore it, confirm green. Repeat for a write path and for the socket.

**Acceptance Scenarios**:

1. **Given** a repository read with its environment predicate removed, **When** the
   gauntlet runs, **Then** it fails, and the failure names the endpoint and the
   tenant whose data leaked.
2. **Given** a repository write with its environment predicate removed, **When** the
   gauntlet runs, **Then** it fails on the state comparison rather than on a status
   code.
3. **Given** an endpoint whose refusal is changed from 404 to 403, **When** the
   gauntlet runs, **Then** it fails on the indistinguishability assertion.
4. **Given** every predicate restored, **When** the gauntlet runs, **Then** it is
   green, and the chapter states which of the three reintroductions each assertion
   caught.

---

### User Story 3 - An external developer integrates on published documentation alone (Priority: P1)

Mai has never seen this repository. She has the published documentation and a running
Relay. She signs up, gets a key, creates a channel, adds two users to it, mints a
token, sends a message over REST, reads it back over REST, connects a socket, and
receives the next one — with no assistance and nothing she could only have learned
from the source.

That developer is represented by `packages/outsider`, a package **mechanically
forbidden from knowing anything**: it declares no workspace dependency, so it cannot
import `@relay/protocol` for a frame type or the test harness for a fixture, and lint
fails the build if it tries. Every fact it needs comes from published documentation. Any
fact that is not there is a documentation defect, recorded with a decision.

**Why this priority**: this is the phase exit criterion, and by the plan's Rule 2 a
part that does not reach its milestone journey is unfinished.

**Independent Test**: run the sealed package against a running stack from a checkout
with no other build artifacts, and confirm it completes a send and a socket receive.
Add a workspace import and confirm the build fails.

**Acceptance Scenarios**:

1. **Given** the sealed package, **When** its dependency list is inspected, **Then**
   it names no workspace package, and a lint rule fails the build if one is added.
2. **Given** a running stack and published documentation only, **When** the sealed
   integration runs, **Then** it reaches a delivered message over the socket.
3. **Given** a step the sealed integration cannot perform from published
   documentation, **When** the chapter is written, **Then** that step is named, with
   what was missing and whether it was fixed here or scheduled.
4. **Given** the sealed integration, **When** it needs a credential, **Then** it
   obtains one by a documented path that requires no repository knowledge.
5. **Given** the sealed integration passes, **When** the chapter states what that
   proves, **Then** it also states what it does not: sufficiency of content is not
   comprehensibility, and no automated suite can be confused.
6. **Given** no running platform, **When** the sealed integration is run, **Then** it
   fails with a message saying the platform is absent rather than starting one — the
   platform is started by the documented command, from outside the package, on every
   build.

---

### User Story 4 - Every error code has a page that resolves (Priority: P2)

Mai gets a `402` with `"code": "quota_exceeded"` and a `docs_url`. She opens it and
reads what the code means, what causes it, and what to do. Today that URL is
`https://relay.example/docs/errors/quota_exceeded` and there is nothing behind it.

**Why this priority**: constitution V requires every error code to have a reachable
page and NFR-USE-05 states it as 100% coverage, verified by test. A chapter whose exit
criterion is "public documentation alone" cannot ship a documentation link that 404s.
It is P2 rather than P1 because the gauntlet's verdict does not depend on it.

**Independent Test**: enumerate every code the platform can emit, and confirm each
resolves to a section of the published reference. Add a code with no entry and confirm
the build fails.

**Acceptance Scenarios**:

1. **Given** the set of error codes the platform can emit, **When** the reference is
   checked, **Then** every code has an entry, and every entry names a code that can
   actually be emitted.
2. **Given** an error response, **When** its `docs_url` is fetched, **Then** it
   resolves to the entry for that code.
3. **Given** a new error code added with no reference entry, **When** the build runs,
   **Then** it fails.
4. **Given** the reference, **When** the site is built, **Then** the page renders and
   the mirrored copy matches the source document.

---

### User Story 5 - A channel and its members exist over the public API (Priority: P2)

A customer's backend creates a channel with its own identifier and adds users to it,
over the public API, with an API key. Repeating the creation returns the same channel
rather than an error. Both endpoints are tenant-scoped, and both are attacked by the
gauntlet on the build that introduces them.

**Why this priority**: without it there is no first integration to verify, so story 3
cannot run. It is deliberately the minimum: two endpoints, not the channel and user
surface FR-CHN and FR-USR describe.

**Independent Test**: with only an API key, create a channel, repeat the request, add
two members, send a message, and receive it on a socket for one of those members.

**Acceptance Scenarios**:

1. **Given** an API key, **When** a channel is created with a customer-supplied
   identifier, **Then** it is created and returned.
2. **Given** the same identifier, **When** creation is repeated, **Then** the existing
   channel is returned rather than an error.
3. **Given** the same identifier used by a different tenant, **When** creation runs,
   **Then** both tenants have their own channel and neither can see the other's.
4. **Given** a channel, **When** members are added by customer-supplied user
   identifier, **Then** users that do not exist yet are created and the members are
   added.
5. **Given** a member of a channel, **When** they connect a socket, **Then** they
   receive messages sent to that channel.
6. **Given** another tenant's channel identifier, **When** members are added to it,
   **Then** the request is refused and that channel's membership is unchanged.
7. **Given** a create request naming a private channel, **When** it is submitted, **Then**
   it is refused with the offending field named, because nothing in the platform enforces
   private-channel access and an API that accepts the word would sell a guarantee the
   platform does not keep.
8. **Given** a channel holding a thousand members, **When** one more is added, **Then**
   the request is refused with the limit's own error code and the channel still holds a
   thousand.
9. **Given** a create request carrying channel metadata, **When** the channel is read
   back, **Then** the metadata round-trips; and metadata beyond the documented size bound
   is refused.

---

### User Story 6 - The things that verify isolation are themselves verified (Priority: P2)

The chapter that claims tenant isolation is verified checks its own instruments. The
guard that detects cross-environment mutations watches five tables and none of the four
tenant-scoped tables chapters 3.10 and 3.11 added. The constitution asks for 100%
branch coverage on isolation code and the file measured 90.57% when chapter 3.11 closed
  and 90.60% on this feature's starting commit. The integration lane
carries a fixed api port that produced three unrelated-looking failures in 3.11 and is
green today by luck.

**Why this priority**: silence from an instrument that is not looking reads exactly
like silence from an instrument that found nothing. Chapter 3.10's SC-008 said "no new
file was added to the exemption list", which was true and meant less than it sounded,
because the tables it wrote were not guarded.

**Independent Test**: plant a sentinel row in each of the four unguarded tables, drive
a cross-environment mutation, and confirm the guard refuses it. Read the coverage
report for the isolation file against the constitution's clause.

**Acceptance Scenarios**:

1. **Given** the four usage tables, **When** a cross-environment mutation is driven
   against each, **Then** the guard refuses it, and the refusal names the table.
2. **Given** a table whose primary key has no `id` column, **When** the guard refuses
   a mutation on it, **Then** the refusal message is produced without error.
3. **Given** the coverage run, **When** the isolation file is measured, **Then** the
   number is stated against the constitution's 100% clause and either closes it or
   names every uncovered branch and why.
4. **Given** the integration lane, **When** two suites that spawn an api run in
   parallel or back to back, **Then** neither takes the other's port.
5. **Given** an integration test that imports the query engine or the driver from outside
   the permitted directories, **When** the lint gate runs, **Then** it fails — the ban
   Principle I names as a mechanism applies to tests again, and the permitted set is a
   list with a reason per entry.

### Edge Cases

- **"Every endpoint" needs a definition, and the default has to be attack.** There
  are 22 routes on the api, one WebSocket path on the gateway, and a health check on
  each of the two services that serve HTTP — the api's and the gateway's; the dispatcher
  runs no HTTP server at all. Some take no tenant-owned identifier at all —
  `GET /healthz`, `GET /auth/:provider/start`. A classification that lets a route
  default to "no tenant identifier" is a classification that absorbs the next route
  silently, which is the failure mode feature 030 was built about.
- **The internal surface is two credential classes and takes two attacks.** Three routes
  — `/internal/messages`, `/internal/session`, `/internal/backfill` — accept an end-user
  token, which **is** scoped to one environment, so a foreign credential is exactly the
  attack: a token minted in A used against a resource in B. The other five accept a
  platform credential, which carries no environment and names one per request, so their
  attack is "a request that names environment A and carries an id from B". An earlier
  draft of this edge case had one shape for all eight and would have left three routes
  attacked in a way that does not apply to them.
- **And a platform credential is a third thing to attack: the service that holds it.**
  Two credentials exist and both resolve to the same class, so until this chapter a route
  could say which *class* may call it and not which *service* — and the gateway's
  credential reached the dispatcher's routes. What protects such a credential after the
  chapter is the network, the secret, and the route's declared service list. What does
  not: rotation, which does not exist. The chapter must say so rather than let a green
  suite imply otherwise.
- **A list endpoint's correct answer is an empty result, not a 404 — and not a page
  either.** The indistinguishability oracle is per endpoint shape, not one status code for
  everything, and a suite asserting 404 across the board would be wrong about the one
  route of 22 that lists. "Page" is the wrong word for it today:
  `GET /v1/webhooks` takes no `limit` and no `cursor` and returns a bare array, so
  EIR-API-06's cursor pagination is unmet on the only list route the platform has. The
  assertion is an empty result in whatever form the endpoint returns, and the gap is
  recorded as walked into rather than caused.
- **The error message is part of the answer.** `messages.service.ts` already keeps a
  constant string for exactly this reason — echoing the id back would make the foreign
  answer differ from the absent answer. The gauntlet has to compare messages, or it
  will pass an endpoint that leaks through its prose.
- **Timing is a channel this chapter does not claim to close.** A foreign id that
  returns in 3 ms and an absent id that returns in 30 ms is a disclosure. Measuring
  that reliably in CI is a different discipline; the chapter states the bound it does
  claim and names timing as unaddressed rather than implying it is covered.
- **The sealed package can still cheat by reading the source.** A dependency rule is
  mechanically enforceable; not opening `repository.ts` is a discipline. The chapter
  states which half is enforced.
- **The sealed package needs a credential, and signup is OAuth in a browser.** An
  automated suite cannot click GitHub's consent screen, and the constitution requires
  `docker compose up` to include a seeded demo tenant where nothing seeds. Both are settled:
  compose starts the api and gateway from behind their `services` profile, a documented seed
  command creates a tenant and prints a key, and the integration reads two URLs and starts
  nothing itself. That closes the clause's intent and not its letter, and the chapter says
  which.

- **`packages/e2e` is excluded from the coverage run.** A gauntlet that attacks over
  HTTP against a spawned api contributes nothing to the constitution's 100%-branch
  clause on isolation code. Chapter 3.11's R23 measured the same thing from the other
  side: `creditConnectionMinutes` went up because nineteen in-process tests covered
  it. Where the gauntlet lives decides what it can measure.
- **A suite that attacks every write endpoint writes to every table, on every build.**
  Cleaning up afterwards with a global delete is precisely feature 030's fault class.
  Every fixture the gauntlet creates has to be scoped to the environments the file
  created.
- **The guard's refusal message interpolates `OLD.id`.** Three of the four unguarded
  tables — `usage_periods`, `usage_active_users`, `usage_connections` — have composite
  primary keys and no `id` column, so adding them to the trigger's table array
  produces a guard that raises `record "old" has no field "id"` on the first
  legitimate write. `quota_notifications` has an `id` and would work unchanged.
- **The reference document is the seventh, and the sync script globs six.**
  `scripts/sync-docs.sh` copies `docs/0[1-6]-*.md`; the renderer's registry lists six
  entries. A document added without touching both is a page that renders stale
  content, and `check:docs` is what notices.
- **Changing `docs_url` changes every error response on the wire, and the fences are the
  part that is fine.** It is not a breaking change — the field is informational — and the
  fenced occurrences across six published chapters are correct as earlier states of a
  byte-exact chain, so they must not be touched. What rots instead is prose no checker
  reads: chapter 1.4 asserts the host "is a placeholder until a docs site exists", and
  chapter 3.2 shows the old URL in illustrative JSON at `:1232` and `:1480`.
- **The two new endpoints are new gauntlet targets on the build that adds them.** If
  the target list is derived, this happens by itself. If it is derived and the
  endpoints are still missed, the derivation is wrong and this is where that shows.
- **A milestone chapter still has a size gate.** 2,000–4,000 prose words on the
  finished page. This chapter carries a suite, two endpoints, a
  documentation reference, a sealed integration, service-scoped platform authorization, a
  compose-driven CI job, a restored lint ban, three inherited debts and four this chapter
  found for itself. The chapter most likely
  to exceed the bound in this part is this one, and the series' own history says the
  split is discovered mid-chapter unless the separable half is sequenced last.

## Requirements *(mandatory)*

### Functional Requirements

**The gauntlet**

- **FR-001**: A single automated suite MUST attack every endpoint the platform exposes
  with identifiers belonging to another tenant, and MUST run on every build in the same
  lane as the other integration tests.
- **FR-002**: The suite's target list MUST be derived from the running application
  rather than maintained by hand. An endpoint that exists and is not classified MUST
  fail the suite.
- **FR-003**: Every target MUST be classified as either attacked or as taking no
  tenant-owned identifier, and each exemption MUST carry a written reason. A target
  MUST NOT be able to become exempt by omission.
- **FR-004**: For every endpoint that accepts a tenant-owned identifier, the response
  to another tenant's identifier MUST be indistinguishable from the response to an
  identifier that exists nowhere — same status, same error code, and same message.
- **FR-005**: For every endpoint that writes, an attack MUST be verified to have
  changed no row belonging to the target tenant, read directly from storage before and
  after rather than inferred from the response.
- **FR-006**: For every endpoint that lists, an attack MUST return an empty result rather
  than an error, in whatever form that endpoint returns results, and MUST return no row
  belonging to another tenant. **Not "a page"**: `GET /v1/webhooks` takes no `limit` and no
  `cursor` and returns a bare array, so EIR-API-06's cursor pagination is unmet on the only
  list route there is. The gauntlet asserts emptiness, not a shape it does not have.
- **FR-007**: The suite MUST cover the WebSocket surface: a credential minted for one
  environment MUST NOT subscribe to, resume from, or send into a channel belonging to
  another, and MUST receive nothing from it.
- **FR-008**: The suite MUST cover the internal service surface, and MUST use the attack
  that fits each route's credential class rather than one shape for all of them. A route
  accepting an end-user token MUST be attacked with a token minted for another
  environment; a route accepting a platform credential — which carries no environment —
  MUST be attacked with a request that names one environment and carries an identifier
  belonging to another.
- **FR-009**: The chapter MUST state what a platform credential is trusted for — it
  carries no environment and selects one per request — and what protects it, rather than
  leaving a green suite to imply a scope that does not exist.
- **FR-044**: A route accepting a platform credential MUST declare which internal
  services may call it, and a credential issued to one service MUST be refused on a
  route declared for another. Declaring the credential class without naming a service
  MUST NOT compile: the platform has more than one internal caller, they are not equally
  exposed, and an authorization that can be omitted is one that will be.
- **FR-046**: The refusal MUST carry its own error code rather than the generic one for
  the status. A caller refused here presented the right credential class and the wrong
  service, which is a different mistake from lacking a permission and from presenting the
  wrong class — the distinction chapter 3.2 made when it added a code rather than
  answering "forbidden". The message MUST name the service and the permitted set, and MUST
  NOT name the credential.
- **FR-010**: The suite MUST NOT depend on the nine existing scattered isolation
  assertions, and those assertions MUST NOT be deleted to avoid duplication: a suite
  that replaces in-process assertions with over-the-wire ones would move coverage off
  the isolation code the constitution measures.
- **FR-011**: Every fixture the suite creates MUST be scoped to environments the suite
  itself created. No cleanup may operate across environments.
- **FR-012**: Isolation MUST be verified structurally as well as behaviourally: every
  persisted table MUST be shown to carry a tenant identifier directly or through a
  single foreign-key hop (FR-TEN-06), derived from the live schema so that a new table
  fails the check until it is either scoped or explained.

**Proving the suite works**

- **FR-013**: Before the chapter claims the suite verifies isolation, at least three
  deliberate reintroductions MUST be run — a read losing its environment predicate, a
  write losing its environment predicate, and a refusal changed from indistinguishable
  to distinguishable — and the suite MUST fail on each.
- **FR-014**: The chapter MUST record which assertions caught each reintroduction and
  which stayed green, and MUST state what the green ones do not cover.
- **FR-015**: No deliberate reintroduction may be left in the shipped code, and the
  chapter MUST state how that is verified rather than asserted.

**The public surface the criterion needs**

- **FR-016**: The public API MUST support creating a channel with a customer-supplied
  identifier, a type, a display name, and up to 8 KB of JSON metadata, authenticated by an
  API key. All four elements, because FR-CHN-01 names all four and `channels.metadata`
  already exists with a default.
- **FR-047**: The create endpoint MUST refuse `private` as a channel type, naming the
  field, for as long as the platform does not enforce private-channel access. FR-CHN-05
  requires that a user not read from, send to, or observe presence in a private channel of
  which they are not a member; nothing in the platform reads `channels.type`, so a channel
  created as private would be private in name only. An API that accepts the word and
  delivers nothing is worse than one whose documented vocabulary is honestly smaller.
- **FR-017**: Channel creation MUST be idempotent on the customer-supplied identifier:
  repeating the request MUST return the existing channel rather than an error
  (FR-CHN-02).
- **FR-018**: The same customer-supplied channel identifier MUST be usable
  independently by two tenants, and neither MUST be able to reach the other's channel.
- **FR-019**: The public API MUST support adding members to a channel by
  customer-supplied user identifier, creating the user record if it does not exist. The
  add half of FR-CHN-06, and FR-USR-01's rule that identifiers come from the customer and
  Relay generates none — **not** FR-USR-02, which is about creation on first
  authentication and describes a different moment.
- **FR-048**: A channel MUST NOT exceed 1,000 members. An attempt that would MUST be
  refused with `422` and an error code specific to that limit. FR-CHN-07 states the number,
  the status and the requirement of a specific code, and the SRS's own worked example for
  EIR-API-04 names the code.
- **FR-020**: A member added over the public API MUST receive that channel's messages
  on a socket, with no repository access and no seeding.
- **FR-021**: Both new endpoints MUST appear in the gauntlet's derived target list on
  the build that introduces them, without being added to it by hand.
- **FR-022**: The remaining public channel and user surface — listing with cursor
  pagination, unread counts, user profile and bulk upsert, member removal, and API key
  management — MUST NOT be built here, and the deferral MUST carry a chapter number in
  `docs/07-tutorial-plan.md` rather than a promise.
- **FR-023**: The test-only seam `packages/e2e/src/harness.ts` opened in chapter 2.8 —
  seeding through the api's repository because no admin API existed — MUST be
  reassessed against what this chapter builds, and either retired for channels and
  members or kept with a restated reason and the chapter that will retire it.

**Documentation an outsider can integrate on**

- **FR-024**: Every error code the platform can emit MUST have an entry in a published
  reference, reachable from the `docs_url` in the error response carrying that code.
- **FR-025**: The set of codes the platform can emit MUST be derivable rather than
  remembered, and a code with no reference entry MUST fail the build. An entry naming a
  code that cannot be emitted MUST also fail.
- **FR-026**: The derivation MUST account for codes that exist outside
  `packages/protocol`'s registry: today `invalid_request`, `unauthorized`, `forbidden`,
  `not_found` and `internal_error` are produced by a status-to-code ladder in the api's
  error filter, `not_found` again by the shared service kit, and
  `connection_environment_conflict` at a call site in a controller. The registry is not
  the set.
- **FR-027**: `docs_url` MUST resolve for a reader who types it, verified against the
  published site rather than against a string pattern.
- **FR-028**: Each reference entry MUST state what the code means, what causes it, and
  what a client should do about it. The entry for a retryable condition MUST say what
  makes it retryable, and the entry for one that is not MUST say so.
- **FR-029**: Adding the reference MUST leave `check:docs` green: the mirrored copy and
  the source document MUST agree, and the sync script's file selection MUST include the
  new document rather than silently skipping it.

**The external developer**

- **FR-030**: The integration that stands for an external developer MUST declare no
  workspace dependency, MUST NOT import a path outside its own package, and MUST NOT
  construct one at run time. A build-time rule MUST fail for each of the three. An import
  restriction alone does not reach the third: a path built from string fragments is not an
  import specifier, and the repository already reaches into another package that way.
- **FR-031**: It MUST complete signup-to-delivered-message: obtain a credential, create
  a channel, add members, mint an end-user token, send over REST, read history over
  REST, connect a socket, and receive a message.
- **FR-045**: The integration MUST target a running platform it does not start, addressed
  entirely through documented configuration. Starting the platform MUST be the job of
  something outside the package, MUST use the same command a reader following the
  published documentation would run, and MUST happen on every build.
- **FR-032**: It MUST obtain its credential by a path an outsider can follow from
  published documentation. Where no such path exists, the chapter MUST either build the
  minimum one and name the requirement or constitution clause it closes, or state
  precisely which step remains impossible.
- **FR-033**: Every fact the integration needs that is absent from published
  documentation MUST be recorded as a defect with a decision — fixed here, or scheduled
  with a chapter number.
- **FR-034**: The chapter MUST state what the sealed integration does not prove: that
  the dependency rule is enforced and reading the source is not, and that content
  sufficiency is not comprehensibility. A person is the only instrument for the second,
  and this chapter does not use one.
- **FR-035**: The chapter MUST give a verdict on the Phase 2 exit criterion — met, met
  in part, or not met — with the evidence for whichever it is.

**The instruments**

- **FR-036**: The global-operation guard MUST watch the four tenant-scoped tables added
  by chapters 3.10 and 3.11: `usage_periods`, `usage_active_users`,
  `quota_notifications`, `usage_connections`.
- **FR-037**: The guard MUST produce its refusal message for a table whose primary key
  has no `id` column. Extending the table array alone MUST be shown to be insufficient.
- **FR-038**: Each newly guarded table MUST be shown to refuse a cross-environment
  mutation, driven deliberately, rather than assumed to be covered because it is in the
  array.
- **FR-039**: The guard's changes MUST land where feature 030's surface lands — the
  post-series fence entries — because that feature publishes no chapter and a published
  chapter may only fence what it teaches.
- **FR-040**: The chapter MUST measure the api repository layer's branch coverage
  against constitution VI's 100% clause for ordering, idempotency and tenant isolation,
  and MUST either close the clause or name every uncovered branch with the reason it is
  uncovered. The ratchet MUST end no lower than it started.
- **FR-041**: `services/gateway/src/limits.itest.ts` MUST stop binding a fixed api
  port, using the random high port `session.itest.ts` and `meter.itest.ts` now use.
  **The path is stated in full because two files in this repository are called
  `limits.itest.ts`** — the other is `services/api/src/limits/limits.itest.ts`, which
  binds no port and is the one that fails when the lane's platform credential is
  missing.
- **FR-042**: Any test this chapter adds that drives a global operation MUST be named in
  the test harness's exemption list with the tables it needs, and in the matching lint
  ignores list.
- **FR-043**: The lint rule that forbids raw data access outside the repository layer
  MUST actually apply to integration tests. It does not today: a later flat-config block
  for `**/*.itest.ts` redefines the same rule name and replaces the restriction, so every
  `.itest.ts` may import the query engine and the driver. The chapter MUST restore the
  ban, MUST correct the config comment claiming one named test file is "the one TEST
  allowed a raw client", and MUST state which files legitimately need the exemption.

### Key Entities

- **Target**: one endpoint plus the tenant-owned identifiers it accepts. Derived, not
  written down. Either attacked or exempt with a reason; never unclassified.
- **Attack**: a request carrying another tenant's identifier, paired with the same
  request carrying an identifier that exists nowhere. The pair is the assertion — one
  request alone cannot show indistinguishability.
- **Reintroduction**: a deliberate, reverted removal of an isolation predicate, used to
  measure the suite's sensitivity rather than the code's correctness.
- **Error reference**: the published document mapping every emittable code to its
  meaning, cause, and remedy. Its completeness is derived from the code, not curated.
- **Sealed integration**: the package standing in for an external developer, defined by
  what it may not import.
- **Channel**: extended from chapter 2.1's table with a public creation path keyed on
  the customer's own identifier, idempotent, and tenant-scoped.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Every endpoint the platform exposes is either attacked with a foreign
  identifier or carries a written exemption. The count of each is stated, and the two
  sum to the derived total.
- **SC-002**: Adding an unclassified route turns the suite red, demonstrated rather
  than asserted.
- **SC-003**: For every attacked read endpoint, the foreign-identifier response and the
  nonexistent-identifier response are equal in status, code, and message — compared
  field by field, not by status alone.
- **SC-004**: For every attacked write endpoint, the target tenant's affected rows are
  identical before and after the attack, read from storage.
- **SC-005**: Three deliberate reintroductions each turn the suite red, and the chapter
  names which assertion fired for each and which assertions stayed green.
- **SC-006**: The shipped tree contains no reintroduction, shown by a check rather than
  by recollection.
- **SC-007**: Every table in the live schema is classified — a tenant identifier
  directly, one foreign-key hop to a table that has one, or membership of an explicit
  list with a reason — and a table matching none of the three fails the check. The
  counts are recorded rather than asserted, because one of the tables is created by
  the test harness and exists only after the lane has run.
- **SC-008**: The sealed package's dependency list is empty of workspace packages, and
  three escapes each fail the build, demonstrated one at a time: a workspace package
  import, a relative import climbing out of the package, and a path to another package
  built at run time from string fragments.
- **SC-009**: The sealed integration completes a socket-delivered message from a
  standing start, in one run, with no fixture from the test harness.
- **SC-010**: Every documentation gap the sealed integration hit is listed with its
  disposition. A list of zero is a result only if the chapter states how it was
  checked.
- **SC-011**: Every error code the platform can emit resolves to a reference entry,
  counted, with the count of codes and the count of entries stated and equal.
- **SC-012**: A new error code with no entry fails the build; an entry for a code that
  cannot be emitted fails it too.
- **SC-013**: `docs_url` from a live error response is fetched against the published
  site and returns the entry for that code.
- **SC-014**: A channel created twice with the same customer-supplied identifier
  returns the same channel both times, and two tenants using the same identifier hold
  two channels neither can see from the other. Metadata round-trips, and metadata over
  8 KB is refused.
- **SC-032**: A create request naming `private` is refused with the field named, and the
  refusal states where private channels arrive. Verified against the published
  documentation as well as the response: an API whose error says "not supported" and whose
  reference says otherwise has moved the problem rather than fixed it.
- **SC-033**: Adding the member that would be the 1,001st is refused with `422` and the
  limit's own code, and the channel still has 1,000 members afterwards — read from
  storage, not inferred from the status.
- **SC-015**: A member added over the public API receives a message on a socket, in a
  test that touches no repository function.
- **SC-016**: The two new endpoints appear in the gauntlet's target list without being
  named there by hand.
- **SC-017**: Each of the four newly guarded tables refuses a driven cross-environment
  mutation, and the refusal names the table. For the three with no `id` column, the
  refusal is produced without a PL/pgSQL error.
- **SC-018**: The api repository layer's branch coverage is stated against
  constitution VI's 100% clause, against 90.60% measured on this feature's starting commit
  (3.11 closed at 90.57%, and the difference is run-to-run drift rather than a change), and every remaining
  uncovered branch named. The pinned ratchet ends at or above where it started.
- **SC-019**: The integration lane stays green across twenty consecutive runs, with the
  test count and the run duration reported for every run. No file is added to feature 030's
  exemption list without the chapter naming the global operation that required it.
  **The chapter MUST state what twenty runs establishes and what it does not.** Twenty green
  runs give 95% confidence only against a per-run failure probability of roughly 14% or
  worse; a 5% flake survives them unseen better than a third of the time. Chapter 3.11's
  battery ran twenty green and an eleven-chapter-old flake surfaced on run twenty-one. A
  green battery is evidence, not proof, and this chapter applies to its own instrument the
  rule it applies to the guard, the lint rule and the sealed package.
- **SC-020**: No suite in the lane binds a fixed api port, verified by reading the port
  selection of every suite that spawns one.
- **SC-021**: The chapter states a verdict on the Phase 2 exit criterion, with what was
  measured and what was assumed.
- **SC-022**: The chapter's published page measures between 2,000 and 4,000 prose
  words, with its fence count, box count and figure count derived by reading the finished
  page. **Figures are 2 to 4, captioned, with at least one in each half of the chapter** —
  the bound `docs/07-tutorial-plan.md` sets for every chapter, counted separately from
  specimen fences. If any bound is exceeded, the overrun is stated with the number rather
  than left to be found later.
- **SC-023**: `check:fences` and `check:docs` both pass, with the fenced-file and
  chapter counts stated, in both locales.

- **SC-024**: The eleven existing isolation assertions still exist and still pass,
  counted before and after — eleven because T033 counted them, where an earlier draft
  of this document said nine. The gauntlet adds to the isolation surface rather than
  relocating it off the code the coverage run measures.
- **SC-025**: The gauntlet's own fixtures are removed only by identifiers it created,
  verified by running the lane with the four newly guarded tables armed and the guard
  silent.
- **SC-026**: Every reference entry names a cause and a client action. An entry that
  only restates the code's own name counts as missing, and the count of such entries
  is zero.
- **SC-027**: The chapter states which repository functions `packages/e2e`'s seeding
  seam still needs after this chapter, as a difference against the list it needed
  before — a shorter list, or the same list with the chapter that shortens it.
- **SC-028**: An integration test importing the query engine or the driver from outside
  the permitted directories fails lint, demonstrated by adding such an import and
  running the gate. The count of files legitimately exempted is stated, and every one of
  them carries a reason.
- **SC-031**: A platform credential refused for its service returns the code reserved for
  that mistake, not the status's generic code, and the message names the service and the
  permitted set and contains no part of the credential.
- **SC-030**: The platform is started for the sealed integration by the documented
  command, on every build, and the package itself starts nothing — verified by reading its
  source for any process launch and by the integration failing with a clear message when
  the platform is absent rather than starting one.
- **SC-029**: Every route accepting a platform credential names its permitted services,
  and a credential issued to one service is refused on every route declared for another —
  measured route by route, in both directions, with the count of platform routes stated.
  A route that accepts the class without naming a service fails to compile, demonstrated
  by writing one.

## Assumptions

- **"Every endpoint" means every route the platform serves, not every public route.**
  The internal surface is where a forged environment identifier would be most
  valuable, and `usage.controller.ts` already refuses a connection that changes tenants
  because chapter 3.11 treated that as a correctness question. Excluding internal
  routes would exclude the interesting half.
- **The oracle is indistinguishability, not refusal.** Constitution I forbids revealing
  the existence of another tenant's data, so the correct answer to a foreign identifier
  is whatever the platform says about an identifier that does not exist. Three existing
  tests already say this in their names — "a foreign channel's history is empty, not
  forbidden"; "a foreign key sees nothing, and it looks exactly like absent"; "treats a
  foreign tenant's channel id as a channel that is not there". The gauntlet generalises
  what they already do.
- **The gauntlet is measured where coverage can see it.** `packages/e2e` is excluded
  from the coverage run on purpose, so a suite living only there cannot contribute to
  constitution VI's clause on isolation code. Chapter 3.11's R23 measured this from the
  other side. Where the suite lives is a plan decision; that it must be somewhere the
  coverage run includes is a requirement of FR-040.
- **The error reference is a document in `docs/`, rendered by the site that already
  renders the other six.** Feature 009 built a renderer for the project's paper
  documents and `scripts/sync-docs.sh` mirrors them; a seventh document costs **three
  lists** — the sync script's, the drift checker's, and the renderer's registry — plus a
  title in two languages. Not a widened glob: `0[1-6]` stops at six on purpose, and
  `0[1-8]` would publish the tutorial plan. The alternative considered and
  rejected was a route tree of per-code pages: truer to the `/docs/errors/<code>` shape
  already shipping, and a dozen hand-authored files to keep in step with a registry
  that changes every chapter. `docs_url` gains an anchor instead of a path segment.
  The tutorial plan's line that "a docs site is not a chapter of this series" stands —
  this is not a docs site, it is one more document on a surface that exists.
- **The external developer is a sealed package, not a person.** The criterion says a
  developer integrates with no assistance; what CI can enforce is that no insider
  knowledge is required, which is the mechanical half of the same claim. A human run
  would test comprehensibility and is the honest instrument for it; it is not scheduled
  here, and FR-034 requires the chapter to say so rather than let the suite stand in
  for it silently.
- **The minimum public surface is two endpoints.** Channel creation and member addition
  are what a first integration cannot do without. **Both are backed by repository functions
  that exist and both need an upsert first** — an earlier draft of this assumption said
  they existed "and are tested", which was the load-bearing half of the argument and was
  wrong: `createChannel` is a plain INSERT that raises on a repeat, and `addMember` has no
  `ON CONFLICT` against a composite primary key and returns one boolean for three
  outcomes. They are tested for what they were built for, which was seeding fixtures.
  Everything else FR-CHN and FR-USR describe — listing, unread counts, profiles, bulk
  upsert, removal — is deferred to its own chapter, because a milestone chapter that builds
  nine endpoints is a chapter about endpoints.
- **The deferred surface gets chapter 3.13**, "the surface a customer drives": the rest of
  FR-CHN and FR-USR's public API, the key management chapter 3.2 deferred to "the
  dashboard's chapter", **FR-CHN-03's private half together with FR-CHN-05's access
  control**, and **EIR-API-06's cursor pagination**, which FR-CHN-08's listing needs
  anyway. The last two are not simply "the rest of FR-CHN" — FR-CHN-05 is access control
  rather than surface, and EIR-API-06 is not an FR-CHN clause at all.
  Part 3's milestone therefore no longer sits last in the part, recorded as a consequence
  rather than hidden. **And the independence is partial, not clean**: the milestone measures
  Phase 2's exit criterion, which the two endpoints make reachable — but FR-CHN-05's absence
  is exactly why `private` is refused, so what 3.13 owes shapes what this chapter can offer.
  Three of the four splits in this part were discovered mid-chapter; this one is decided
  before a word is written.
- **The platform is started by compose and seeded by a documented command.** The
  constitution requires the full stack to start with one command "including a seeded demo
  tenant", and nothing seeds; the sealed integration needs a credential and cannot click an
  OAuth consent screen. So compose starts the api and gateway — they sit behind a
  `services` profile, which is why `docker compose up` alone does not — and a documented
  seed command creates an organisation, an application, a development environment and one
  key, and prints it. That closes the clause's intent and not its letter, because compose
  starts stores where the clause says the whole stack, and the chapter says so. The
  integration itself starts nothing (FR-045).
- **Chapter 3.13's existence does not weaken FR-023.** The 2.8 seam is reassessed here
  because this chapter changes what it depends on, not because it can be closed
  entirely.
- **This chapter publishes**, so its fences belong in the chapter that teaches them. **The
  guard extension is the one exception** and belongs in `fences/post-series.md`, because
  feature 030's surface teaches no chapter. The port fix is not an exception: it lands in
  `services/gateway/src/limits.itest.ts` — not the api's file of the same basename, and not
  chapter 3.8's — and **neither file is fenced by anything**, so it needs no entry in
  post-series or anywhere else.
- **No new metering, analytics, or dashboard.** FR-ANL and FR-DSH are Part 4.
- **The chapter is the largest in the part by content and the most likely to exceed the
  word bound.** The separable half is the documentation and sealed-integration work,
  and sequencing it last is what lets the split be decided with a number rather than
  discovered — the method chapter 3.8 used and chapter 3.11 confirmed.

## Dependencies

- Every chapter from 2.1 onward, since the gauntlet attacks all of them. Chapter 2.1's
  repository layer with its mandatory `environment_id` is the thing being verified;
  the constitution calls this "designed out, not tested out", and this chapter is the
  test that the design held.
- Chapter 3.2's credential model, extended by 3.11 and narrowed here: an API key resolves
  to one environment, a user token to one environment and one user, and a platform
  credential to no environment at all. **There are two platform credentials and one
  platform class** — 3.11 gave the dispatcher and the gateway a secret each while both
  still resolve to `{ kind: "platform", service }` — so the attack shapes outnumber the
  classes: a foreign key, a foreign user token, a platform request naming one environment
  with an identifier from another, and a credential issued to a service the route does not
  serve. The last of those is what FR-044 makes refusable.
- Chapter 3.8's error envelope and chapter 3.10's `quota_exceeded`, whose `docs_url`
  has resolved to nothing since it shipped, and chapter 1.4's placeholder that both
  inherited.
- Chapter 2.8's Tuan test and its harness, whose seeding comment scheduled this
  chapter's channel and member endpoints to "Part 3's tenancy work".
- Feature 024's coverage run and its pinned ratchets, and the 100%-branch clause it
  measured and left open for "the next chapter that touches the repository layer".
- Feature 030's guard, its exemption list, its lint ignores, and the four tables it
  does not watch.
- Feature 009's document renderer, `scripts/sync-docs.sh` and `scripts/check-docs-drift.sh`
  — three lists the error reference joins, two of them shell globs that stop at six on
  purpose.
- The fence chain, byte-exact across 177 files and 28 chapters, which resolves every fence
  title against `relay-platform` — so tutorial-repo files and the parent's `docs/` cannot be
  fenced at all. It will see every platform file this chapter amends; the `docs_url` change
  needs a new fence per amended file, not an edit to an old one.
