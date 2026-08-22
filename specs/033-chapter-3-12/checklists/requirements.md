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

## Analysis pass four — the numbers

Nine findings, no CRITICALs, eight applied. The ninth was a misleading denominator in a
contract's closing list and was left alone.

**Zero criticals is the expected shape for a fourth pass** — chapter 3.11's fourth found
nine findings and none critical too. The first three passes find things that would break;
the fourth finds things that would embarrass. Every one of these nine was a number written
once and quoted afterwards without being re-derived.

**The shape table did not sum to its own total.** Five rows accounted for 21 of 22 routes,
and the missing one was `POST /v1/webhooks` — the webhook *create* route, absent from
`data-model.md`'s `write` row and from T030's list of public writes. The derivation would
have caught it on the first run, because T017 fails on a target matching no classification
entry, so the mechanism worked; the arithmetic just got there first. Writes are fifteen.

**The fence surface was understated by seven files.** The claim was 17 new and 13 amended.
Re-derived from the task list after three passes had added to it: **16 new and 21 amended,
37 total**, against chapter 3.11's 21 files and 34 fences. The original figure was computed
once in pass one with a regex that also caught a `relay-tutorial` file, then quoted in three
documents across two more passes. It is the input to T114's split decision, which makes it
the wrong number to have been casual about — and correcting it strengthens R19's argument
rather than weakening it.

**One sentence contradicted itself.** R8's cost paragraph said "six call sites naming a
code", listed eight, and the measured count is nine. All three numbers were in the same
sentence.

**And the new refusal needed a code, which moved a count through six documents.** A platform
credential refused for its service presented the right class and the wrong service — neither
"you lack a permission" nor "you presented the wrong kind of credential". Chapter 3.2 made
this argument once already when it added `wrong_credential_type` rather than answering with a
generic 403. So `wrong_credential_service` joins the registry beside it, the emittable set
ships at **twelve** rather than eleven, and the message names the service and the permitted
set and never the credential. Requirements moved 45 → 46 and outcomes 30 → 31.

**What four passes cost and returned.** 42 findings, 5 CRITICAL, requirements 42 → 46 and
outcomes 27 → 31. Three of the additions are product code rather than test code — the
service-scoped authorization, its error code, and the compose-driven CI job — which is not
what analysis passes are meant to produce. Two of the three came from reading the credential
model and the build gates in passes two and three; had either been read during planning,
they would have been plan decisions instead of corrections.

## Analysis pass five — the governing documents

Seven findings, one CRITICAL, all applied. The CRITICAL is the most consequential single
finding of the five passes, and four earlier passes had every chance to catch it.

**The chapter was about to ship a privacy guarantee the platform does not implement.**
`POST /v1/channels` accepted `type: "private"`. `channels.type` has been a
`"public" | "private"` column with a CHECK constraint since chapter 2.1, and **nothing reads
it** — the only matches for `"private"` in `repository.ts` are the type union and
TypeScript's own modifier. History and send scope by `environment_id` alone; there is no
membership check in either path. FR-CHN-05 is P1: a user must not read from, send to, or
observe presence in a private channel they are not a member of. Until now only tests could
create a private channel, so nothing exercised the gap. A public create endpoint would have
let a paying integrator ask for privacy, be told they had it, and get none — in the chapter
whose whole subject is access control.

The endpoint's documented type vocabulary is now `public` and nothing else, refused at the
schema so the failure names the field, and FR-CHN-03's private half goes to chapter 3.13
with FR-CHN-05, because access control for private channels is the send path, the history
path and the socket subscribe path.

**Two more clauses beside the ones the endpoints cited.** FR-CHN-07's 1,000-member ceiling
appeared in no artifact, and the SRS states the number, the `422`, **and** the requirement
of a specific code — whose name is in the SRS's own worked example for EIR-API-04,
`channel_member_limit_exceeded`. FR-CHN-01 has four elements and the first draft delivered
three; `channels.metadata` is a jsonb column with a default that has existed since 2.1, so
the omission cost a schema field, not a migration. The shipped code set is now thirteen.

**And a requirement id used loosely.** FR-USR-02 was cited for creating users when they are
named as members. It describes creation on first *authentication* — a different moment. The
clause that supports the behaviour is FR-USR-01. An id used loosely is worse than none,
because it makes a traceability table look complete.

**Why four passes missed all of it.** Each earlier pass checked the artifacts against
something: each other, the code, the gates, arithmetic. None checked them against the
requirements they claim to deliver. Pass two read `sendMessage` closely enough to note it
has no membership check and recorded that as *convenient* — it was why the minimum surface
could be two endpoints — rather than as FR-CHN-05 being unimplemented. The same fact, read
twice, meaning opposite things.

Eight of the chapter's requirements cited a governing-document id before this pass. T105a
now builds the map in both directions, which is the check that would have caught FR-CHN-05,
FR-CHN-07, FR-CHN-01 and EIR-API-06 in one pass instead of five.

## Analysis pass six — task executability

Seven findings, no CRITICALs, all applied — the same shape chapter 3.11's sixth pass
produced. **Two of the seven came from twenty lines of Python rather than from reading**,
and that is the pass's real lesson.

A script that treats "Write `X`" as a file's creator, collects every backticked file
reference, and flags any reference numbered before its creator found both immediately.
T051a enforced FR-CHN-07 in `channels/channels.service.ts` five tasks before T054 created
that file — it had also been written to do two things at two different times, a registry key
with no dependencies and an enforcement with one. And T104 recorded the exit-criterion
verdict into `chapter-notes.md` and "the page" from Phase 10, when those arrive in Phases 14
and 12. I had read past T104 three times, because "record the verdict in
`chapter-notes.md`" is a sentence that looks correct until you ask when the file exists.
Executability is the most mechanically checkable surface of the six, and the check was built
on the sixth pass rather than the second.

**One circular instruction, and it was a previous pass's repair.** T069f was added in pass
two to fix what restoring the lint ban would break in the gauntlet's own suites, and its
scheduling note then told it to run before those suites existed. The fix was not to
reorder it but to delete it: T025 now reads rows through `Repository` and T037 puts the
`information_schema` query behind a function in `services/api/src/db/`, where the query
engine is already permitted. The constraint moved upstream to where the code is written,
which is T069f's own argument applied to itself, and T069b now asserts that
`services/api/src/isolation/**` never appears on the permitted list — the place where a
shortcut would show.

**And one change three tasks described while leaving a third of it unbuilt.** Widening
`Accepts` to `AcceptSpec` breaks `expectation()` at `credential.guard.ts:30`, which feeds
the two strings an integrator actually reads at `:89` and `:96`. T030b changed the type,
T030c changed the check, and nothing touched the message — in a chapter that had just added
an error code specifically so the refusal would say what went wrong.

**Two things the mechanical check flags that are not defects**, recorded so a later pass
does not "fix" them. `T069e -> T069` is the lettered-id convention working as documented — a
lettered task may precede its base where it is a prerequisite. And T104 still mentions
`chapter-notes.md`, now in a sentence saying explicitly *not* to write there; the checker
reads references, not negations.

## Analysis pass seven — the previous pass's edits

Five findings, no CRITICALs, no HIGHs, all applied. **This is what running out of reading
looks like**, and it is the same result chapter 3.11's seventh pass reported: every finding
was a sentence or a list the sixth pass wrote, and none of them would have changed what
gets built.

**Two of the five are the same failure mode, committed while fixing it.** The note that
deleted T069f for telling a repair to run before the files it repaired existed then claimed
"Phase 8 finds nothing to fix" — a conclusion stated wider than it holds, since the
permitted list still owes entries to three pre-existing suites that import the query
engine. And T115 listed two costs of taking the size split while skipping the one that
happens in the phase making the decision: the prose for Phases 9 and 10 has been written by
the time the count exists, so the first cost is discarding sections just drafted. Both
sentences read as settled and were slightly wider than the facts.

**One omission with a number attached.** `services/api/src/db/catalogue.ts` — created by the
sixth pass to keep the catalogue query inside the directory where the query engine is
permitted — was missing from T079's ratchet decision, in the one directory that already
carries a per-file ratchet and the one the constitution's 100%-branch clause is about. And
`data-model.md` §4 still described the classification as "computed from `information_schema`"
with no mention of where, so a reader working from the data model alone would write the
query into the test and need an exemption for as long as it lived.

**What the pass checked and found clean, recorded because a pass that reports only hits is
not a pass.** T025's central instruction — read the target tenant's rows through
`Repository` — needed a public read for every write target, and there is one for each:
`getEndpoint`, `listEndpoints`, `listDeliveriesForEvent`, `listDeadLetters`, `listMessages`,
`listMembers`, `listChannels`, and `usageFor` at `repository.ts:612` for the usage tables I
expected to be the hole. That was the finding this pass went looking for and it was not
there. No stale references to T051b, T054b, T069f or T002a survive the renumbering, and
task order is clean but for `T069e -> T069`, which is the lettered-id convention working as
documented.

## Seven passes, and where they stopped

  pass 1   the documents + the published series   17 findings   2 CRITICAL
  pass 2   the code                                9            2
  pass 3   the build gates                         7            1
  pass 4   the numbers                             9            0
  pass 5   the governing documents                 7            1
  pass 6   task executability                      7            0
  pass 7   the sixth pass's edits                  5            0

Sixty-one findings, six CRITICAL. Requirements moved 42 → 48 and outcomes 27 → 33, and
**three of those additions are product code rather than test code** — the service-scoped
authorization, its error code, and the compose-driven CI job. An analysis pass is not
supposed to produce product work; that three did is the honest cost of reading the
credential model, the build gates and the governing documents in passes two, three and five
instead of during planning.

The decline is not monotonic, and the exception is the lesson: pass five found a CRITICAL
after pass four found none, because it read a surface no earlier pass had. Pass seven read
no new surface and its yield shows it. Analysis stops here.
