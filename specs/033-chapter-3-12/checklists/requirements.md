# Specification Quality Checklist: Chapter 3.12 — Milestone: the isolation gauntlet

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-22
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

Every box is ticked and three of them are ticked against a reading that should be
stated rather than assumed, because a checklist that quietly redefines its own items
is worse than one that fails.

**"No implementation details" and "technology-agnostic", read as: prescribes no
design, names the state that exists.** The spec names `usage_periods`,
`packages/e2e`, `scripts/sync-docs.sh`, `docs_url`, PL/pgSQL, the figure 90.57%, and
close to thirty other artifacts. All of them exist today and none is a decision this
spec is making — they are the repository this chapter is about, at the commit it starts
from. Where the spec reaches a genuine design choice it declines to make it: FR-002
requires the target list to be derived and does not say from what; FR-040 requires the
coverage figure to be measured somewhere the run can see and leaves the location to
the plan; FR-032 requires a documented credential path and names two acceptable
answers without choosing. This is the same reading chapters 3.10 and 3.11 shipped
under, and applying the generic rule literally would produce a specification that
cannot say which port a fixed port is.

**"Written for non-technical stakeholders" is false in the ordinary sense and true in
this project's.** The stakeholder is the series' author and the reader who checks the
chapter against the requirements. A version of this document readable by someone who
does not know what a tenant identifier is could not state FR-004.

**Requirements verified by inspection rather than by test.** Seven — FR-009, FR-014,
FR-015, FR-022, FR-034, FR-035, and the "state the number" clause in FR-040 — require
the chapter to write something down. The SRS's own verification vocabulary allows
inspection alongside test, and the alternative is a chapter that measures honestly and
publishes selectively. Each names what has to be written and what would make it wrong.

**One thing the spec asserts and cannot yet prove.** FR-022 defers the rest of the
public channel and user surface to chapter 3.13, and no such chapter exists in
`docs/07-tutorial-plan.md` yet. The deferral is a promise until that table is edited,
which is planning work, not specification work — recorded here so it is not discovered
later as a gap.

**Two findings this specification is built on came from reading the code rather than
the documents, and both changed the chapter's scope.** There is no public endpoint to
create a channel or add a member, which makes the Phase 2 exit criterion unreachable
for reasons that have nothing to do with documentation; and the set of error codes the
platform can emit is larger than the registry that is supposed to hold it, so
"document every code" could not have been done from the registry alone. Neither is
visible in the SRS, the SAD, or the tutorial plan.

## Analysis pass one — documents against each other and against the published series

Seventeen findings, two CRITICAL after review, all applied. A third was CRITICAL when written and did not survive its own evidence. The checklist above
still reads 16/16, and two of its boxes are now ticked for better reasons than they were.

**Two of the three CRITICALs came from testing a claim rather than reading it.**

`grep -rn 4124` instead of trusting a filename found that the fixed port is in
`services/gateway/src/limits.itest.ts` and not the api's file of the same basename. The
wrong path had travelled from CLAUDE.md's shorthand into the research, the plan and the
task list without anybody opening the file — so the fix would have edited a file that
binds no port and left FR-041's defect standing. The same pass found that neither file is
fenced by any chapter, against chapter 3.11's note calling it "another chapter's fenced
file", so the change is smaller than three documents claimed.

`npx eslint services/api/src/quotas/period.itest.ts` exiting 0 found that Principle I's
lint ban is not in force for any integration test: a second flat-config block for
`**/*.itest.ts` redefines `no-restricted-imports`, and flat config replaces rather than
merges. The config's own comment claims one named test is "the one TEST allowed a raw
client". Every test is. That became FR-043 and SC-028 — the requirement count moved from
42 to 43 and the outcome count from 27 to 28.

**The third finding was `outbox`, and reviewing it reversed it.** The first reading said
Principle I's second clause was violated — no `environment_id`, zero foreign keys,
neither branch of "directly or through a single foreign-key hop" available — and proposed
adding the column at one insert site with an exact backfill. Three of the four arguments
for that collapsed when they were checked rather than restated: nothing wants a
tenant-scoped read of the outbox, so a column no query filters on enforces nothing; the
outbox's legitimate mutation **is** cross-environment, so the column would make feature
030's guard refuse the relay's own sweep; and the single insert site already holds the
environment. A foreign key would also block deleting an environment while outbox rows
exist, which makes FR-TEN-08 harder rather than easier. The classification was
inconsistent too — `consumed_events` has no tenant either and was filed as infrastructure
without complaint.

**What survived is worse than what was first reported.** `drainOutbox` sets
`published_at` and never deletes, nothing in the api deletes a row from any table, and
the payload is a full copy of the message including its text — 286,871 rows in the test
database. That collides with DR-06 and FR-MSG-08 (a tombstone that leaves a copy behind
is not a tombstone), FR-TEN-08 and FR-MOD-06. The fix is a one-line prune that needs no
tenant column, and it belongs to FR-MOD-06's chapter. So the pass ends at **two**
CRITICAL rather than three, and the structural check has three classes rather than four —
with no empty fourth kept open, because a bucket waiting to receive a violation is how a
finding becomes a classification.

**Four findings were the same mistake at different addresses.** A per-chapter fence file
that does not exist, tutorial-repo files filed as fenceable when the chain resolves every
title against `relay-platform`, `turbo.json`'s env allowlist unaccounted for, and a
success criterion (SC-007) asserting the opposite of what the design delivers. Each was a
claim carried from one document into the next without being checked against the
mechanism it named.

**And one omission that strengthens an argument already made.** R19 argued the size split
on prose words and never counted fences: 17 new files and 13 amended, against chapter
3.11's 21 files and 34 fences. An amended file needs a diff fence in this chapter's own
prose or the chain's HEAD property fails, so the fence surface is a floor under the page
rather than a by-product of it. The stronger half of the case was sitting unused.

## Analysis pass two — the code

Nine findings, two CRITICAL, all applied. Where pass one found paths and mechanisms
described wrongly, pass two found **surfaces modelled wrongly** — and both CRITICALs were
the same mistake.

**`/internal/*` is two credential classes and the artifacts had one.** Three routes are
`@Accepts("user")` and carry an end-user token that **is** scoped to one environment; five
are platform routes whose credential carries none. Every artifact said the internal attack
was "names one environment, carries a foreign identifier", justified by the credential
being unscoped — true of five routes, false of three, and the three would have been
attacked in a shape that does not apply to them while FR-008 reported satisfied.

**And a platform credential was authorized by class, not by service.** `Accepts` took
`...kinds: PrincipalKind[]`; both credentials resolve to `{ kind: "platform", service }`
with `service` documented "for logs"; so the gateway's credential reached
`POST /internal/dispatch/replay`, whose handler takes a dead-letter id and no environment.
Chapter 3.11 argued for two secrets on the grounds that "the gateway terminates
connections from the public internet and the dispatcher does not, so a shared secret lets
the more exposed service set the blast radius for both" — and stopped one step short. Two
secrets stopped them sharing a secret; they still shared a surface. Worse, an earlier
`contracts/gauntlet.md` §3 argued *against* testing this, so a green suite would have
carried an explicit claim that the class was contained.

That became FR-044 and SC-029: `Accepts` grows a service argument typed so that
`@Accepts("platform")` **stops compiling**. Requirements moved 43 → 44 and outcomes 28 →
29. The alternative — assert today's behaviour and report the hole — was on the table and
declined: a suite that documents a hole is not the suite constitution I asks for.

**Two promises the code cannot keep, now made keepable.** `frameSchema` has no direction
metadata, so "derive the inbound frame types from the union" was not implementable; it
becomes a classification with a totality check, the same mechanism the routes use.
`createChannel` is a plain INSERT, so FR-017's idempotency needed a storage-layer upsert
rather than a service-level read-then-insert, which races and which Principle II forbids
by name.

**One defect this checklist's own pass-one remediation introduced.** Restoring the itest
lint ban (T069a) breaks the gauntlet's two new suites, because
`services/api/src/isolation/**` was not in the permitted list and `tenant-scope.itest.ts`
queries `information_schema`. T069f resolves it, preferring a repository function over a
wider ignores list. This is what a pass reading the previous pass's edits is for.

**And three counts that were wrong because they were remembered.** Eleven api suites boot
`AppModule`, not nine. The decorator value is `platform`, not `service`. And the dispatcher
runs no HTTP server at all — no `createServer`, no `listen`, no compose healthcheck — so
there are two health endpoints in the exempt list, not three.

## Analysis pass three — the build gates

Seven findings, one CRITICAL. Six applied; the seventh was a LOW wording note and was
declined rather than absorbed.

**The sealed package had nowhere to run.** Nothing starts the api or the gateway for it:
CI has no compose step and no `pnpm dev`, and the way every existing suite gets a server
is `spawn("node", [join(REPO, "services","api","dist","main.js")])` with
`REPO = join(HERE, "..", "..", "..")` — the escape this package forbids itself. Compose's
`api`, `gateway` and `dispatcher` sit behind `profiles: ["services"]`, so
`docker compose up -d --wait` starts stores only. T099 could not have run anywhere.

Compose now starts the platform, in a CI job of its own — and the reason it is a separate
job is the trap that would have eaten an afternoon: the platform job uses GitHub service
containers on `localhost:5432`, while compose's api reads
`postgres:5432` on its own network. Adding `--profile services` to the existing job would
have started a second database, migrated the first, and left the api serving a schema that
does not exist. That became FR-045 and SC-030.

**The seal was two levels and needed three.** R12 said the remaining hole was a
relative-path import "which only a lint rule closes". A path built at run time is not an
import specifier, so `no-restricted-imports` never sees `join`, `createRequire`,
`readFileSync` or `spawn`. `harness.ts`, cited in R12 itself as proof the hole exists, is
also proof the proposed rule does not close it — and the config has no
`no-restricted-syntax` rule today. FR-030 and SC-008 now name three escapes and require
each to be demonstrated failing.

**And the completeness check could not live where it was put.**
`docs/08-error-reference.md` is above `$TURBO_ROOT$`, so it cannot be a turbo input: edit
the reference, re-run `pnpm test`, get a cache hit, gate passes stale. It also breaks the
standalone-clone promise, since `relay-platform` has its own remote and a README saying its
checks pass from a clean checkout. Split along the repository boundary — the platform
asserts every emitted code is registered, the tutorial asserts registry against reference,
where the parent is already in scope and `check-docs-drift.sh` sets the skip-when-absent
precedent.

**One finding was about where a mistake would most likely be made rather than where one
was.** Every sibling integration config points `globalSetup` and `setupFiles` at
`../../packages/test-harness/src/…`, so writing the outsider's config by copying one —
the obvious move — reaches into another package on its second line. T097 now says to write
it from scratch and names the trap.

**What the three passes found, by class.** Pass one: things described wrongly, mostly paths
and mechanisms. Pass two: surfaces modelled wrongly — `/internal/*` as one credential class
when it is two, and platform credentials authorized by class rather than by service. Pass
three: work with nowhere to run. Requirements moved 42 → 45 and outcomes 27 → 30 across the
three, and two of the additions are product code rather than tests, which is not what an
analysis pass is supposed to produce and is the honest result of reading the gates late.
