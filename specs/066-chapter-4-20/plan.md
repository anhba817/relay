# Implementation Plan: Chapter 4.20 — The messages that expire

**Branch**: `066-chapter-4-20` | **Date**: 2026-10-03 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/066-chapter-4-20/spec.md`

## Summary

`docs/12` row 21 asks for FR-MOD-06's retention job. The premise was run first — the habit
§7.5 asked of chapter 4.19 — and it inverts that chapter's result: **none of FR-MOD-06's three
obligations is met.** The policy column has existed since chapter 2.1 and is set on 0 of 33,051
environments; there is no scheduler of any kind; and the hard deletion the clause names is
**refused by the database**.

The refusal is the chapter. Exactly one table references `messages` and chapter 4.19 put a row
in it for every deletion, so **5,495 messages cannot be hard-deleted today** and the number
grows by one per deletion. 4.19 wrote that collision down, declined to pre-solve it, and named
row 22's erasure as the chapter that would meet it. **Row 21 meets it first.**

And it is a pincer rather than a sequence. Deleting the message is refused by the foreign key;
deleting the version rows first is refused by the append-only trigger; **and changing the key
to `ON DELETE CASCADE` is refused too, because a cascade issues an ordinary `DELETE` and a row
trigger fires on it.** The only mechanism that works without a schema change is
`session_replication_role = replica` — which is one of the two bypasses ADR-35 published as the
*limits* of its own guarantee.

So the chapter's product is a narrow, auditable exception: the trigger names its one legitimate
deleter, the foreign key cascades, and **a published guarantee changes, which is ADR-36**.

## Technical Context

**Language/Version**: TypeScript 5.x on Node 22, as the rest of `services/api`

**Primary Dependencies**: none new

**Storage**: PostgreSQL — one check constraint, one changed delete action, one trigger
condition. No new table. Object storage for FR-MED-11's half

**Testing**: vitest. The api integration lane for the sweep and the route, the isolation
gauntlet for tenancy, a unit lane for the policy's arithmetic

**Target Platform**: Linux server, the composed stack

**Performance Goals**: two queries, and the one this section originally named is the second.
**The driving predicate — which messages expire — has no index behind it**: `messages` carries
`messages_pkey`, `messages_channel_id_sequence_unique`, `messages_idem` and
`messages_attachments_gin`, and nothing for `created_at`. Written as a join across all
environments the age bound lands in a `Join Filter` — measured, `Rows Removed by Join Filter:
1018` on the busiest environment, **617 buffers** — and written per environment with the bound
as a constant it is **73** and reaches `channels_environment_last_activity`.

**THERE IS NO SPEEDUP AND AN EARLIER DRAFT CLAIMED 8×.** Re-measured end to end at analysis
pass 14: **546 of the 617 is a `Seq Scan` of all 33,051 environments** (`Rows Removed by
Filter: 33050`), and the per-environment form pays that as step 1, so the two shapes come to
**617 and 546 + 73 = 619**. The reasons to take it are pageability, FR-008's re-runnability
and a bound the planner can use — **none of them a ratio** (4.15). The second query is the
shared-attachment check, which is 4.12's rule at a third address: with the operand bound it
reaches `messages_attachments_gin`, and set-wise the same index sits **idle** under a Parallel
Seq Scan with `Rows Removed by Join Filter: 210,696`. **Quote that signature rather than a
buffer count** — R2's 883 and 94,132 re-measure as **107 and 3,423**, because R2 published no
query text (research R2)

**Constraints**: no breaking change to a published response (CON-05). The sweep adds no field
implying a deadline the platform does not enforce

**Scale/Scope**: 199,275 messages, 14,039 media objects, 33,051 environments, **0 with a
policy**, and **nothing older than 19 days at planning, 20 on 2026-10-04 and thirty on
2026-10-14** — so every demonstration is a backdated fixture

## Constitution Check

| principle | verdict |
|---|---|
| **I — tenant isolation** | **engaged twice, and the two halves are opposite.** The clause says *"a repository layer whose constructors require an `environment_id`"* — so the enumeration of environments with a policy **cannot be a `Repository` method**, because every instance is bound to one tenant and this crosses all of them. It is an unscoped function in `services/api/src/db/retention-reads.ts`, the shape `storage-reads.ts`, `usage-reads.ts` and `audit-reads.ts` already use, and `pendingMediaObjects` states the isolation property for it: *"the route above it takes no tenant parameter at all, which is the isolation property to **assert** rather than a scope to add."* **The delete is the other half** and is tenant-scoped, one environment at a time, with the per-arm probe on it — because a sweep is the first thing here that destroys rows in bulk, and a predicate scoped wrong loses another tenant's data rather than leaking it |
| **II — no acknowledged message is lost** | **ENGAGED, AND IT TOOK A DECISION RATHER THAN A SENTENCE.** Bullet four reads *"hard deletion exists **only on the compliance path**"*, and FR-MSG-08 and DR-06 say the same thing more narrowly — so three documents reserve this verb and FR-MOD-06 asks for it anyway. **The reading taken is that a retention sweep IS a compliance path**: the constitution's own word is *path* rather than *endpoint*, and a policy exists to keep a promise a customer made to an auditor. The constitution needs no amendment under that reading; **FR-MSG-08 and DR-06 do**, because they say *endpoint* and *retains its row*. That is ADR-36's second decision and the SRS amendments are T043a and T043b |
| **III — two data paths** | untouched. Operational expiry does not reach ClickHouse; DR-09's 90-day raw-event TTL is a different clock with a different owner, and the chapter states the boundary rather than widening to it |
| **IV — single writer** | **satisfied by the predicate being self-clearing.** A destroyed message cannot match the next pass, so re-running needs no lease, heartbeat or reaper — chapter 4.13's compare-and-set argument in a different shape. **It needs a test rather than a sentence** (research R7) |
| **V — API-first** | the policy is set through a public route. The sweep is a command and not a route, deliberately: see the ADR question |
| **VI — test-verified** | five bullets, answered below |
| **VII — boring by design** | no new service, no new dependency, no new table. **ADR-36, and it is unavoidable** |

### Principle VI in full, because a row that answers one bullet reads as answering five

| bullet | verdict |
|---|---|
| stable identifiers, priority, verification method | met. **14 FR and 14 SC**, `traceability.md` built by reading. **The count is in this row on purpose**: analysis passes 7 and 8 each added a requirement without adding its verification, and this is the row whose own number would have said so — it read `12 FR and 12 SC` against 14 FR for two passes. SC-013 and SC-014 close it |
| **70% coverage; ordering, idempotency and tenant isolation at 100% branches** | **two of the three are this chapter's.** Tenant isolation is the sweep's predicate, probed per arm. **Idempotency is FR-008** — the second run must change nothing, counted absolutely rather than as a delta, because 0 → 0 is satisfied by nothing happening |
| **the cross-tenant suite, dependency vulnerability scans AND the OWASP Top 10 scan gate releases** | **ONE OF THREE MET, AND THIS ROW SAID "met" UNTIL ANALYSIS PASS 9.** The gauntlet runs, and a bulk-delete route is a new shape for it. **The other two mechanisms do not exist anywhere in this workspace** — one workflow file, **zero** matches for `audit\|snyk\|trivy\|owasp\|zap\|codeql\|dependabot`, no `.github/dependabot.yml`, and no `pnpm audit` in any of the eight `package.json`. **UNMET, and not this chapter's**, on bullet four's precedent; `gaps.md` carries it. **The row answered one clause of three under a heading warning that a row answering one bullet reads as answering five** — which is 057's shape for the third time: a CRITICAL inside the artifact written to prevent its own class |
| the quickstart runs unmodified, verified in CI | **UNMET, and not this chapter's.** No quickstart executes in `ci.yml` and the phase-9 task runs this one by hand and corrects it in place. Named here because the alternative is a check that reads as answered |
| **input validated against a schema; UNKNOWN FIELDS REJECTED on write endpoints** | **two clauses, and the second was uncovered until analysis pass 9.** The new route is validated, and its schema is **`z.strictObject`** so an unknown field is a 400 — the platform's convention, 7 uses in `channels.schema.ts` and 4 in `messages.schema.ts`, and 065 paid `unrecognized_keys` from the producer's side. **`gaps.md` 058-3 is not repaired**: a malformed path parameter answers 500 on **twenty-two** shipped routes and the new one makes twenty-three, which is the argument for carrying rather than fixing one. **That entry says sixteen and analysis pass 11 re-measured it** — it counted two parameter names in two controllers and never opened `webhooks.controller.ts`, whose six `@Param("id")` routes take a `uuid PRIMARY KEY` unvalidated |

**Does this need an ADR?** Constitution VII: *"Every architecture decision is recorded as an ADR
stating its drivers, rejected alternatives, and reversal condition. ADRs are immutable once
accepted; superseding requires a new ADR."*

**Yes — ADR-36, with TWO decisions, which is ADR-35's own shape** (*"the audit log is
operational, its immutability is a trigger, and its timestamp is declared"*). **Decision 1: a
retention sweep is a compliance path**, so FR-MOD-06's hard deletion is licensed by the same
clause that licenses erasure — the constitution says *path*, not *endpoint*, and FR-MSG-08 and
DR-06 are amended to match rather than the constitution. **Decision 2: the trigger's exception**,
below. The first was found at analysis pass 5 and the second at planning; they belong together
because both answer *what is allowed to destroy evidence*, and separating them would leave a
reader of either asking the other's question.

**And it cannot be avoided.** `ADR-35` is the last in both homes, checked, so
this chapter's number is **ADR-36** and it is written down here rather than invented in phase 7
under pressure. Chapter 4.18 named ADR-35 in its plan before writing a line of it, for the same
reason: five documents will cite this and a citation needs an address. ADR-35 published the audit log's immutability as *to the
application and to accident, and not to somebody holding the database password*, and chapter
4.19 applied that scope to `message_edits`. This chapter makes it *to the application **except
one named path**, and to accident.* That is a change to a published guarantee, which VII says
is a new ADR — **ADR-36** — superseding ADR-35's scope clause rather than an edit to it.

**The ADR's drivers are measured, not asserted**: three of four escapes fail, and the one that
works without this change is the hole ADR-35 documented. **Its rejected alternatives are in
research R1** with the error each one produced. **Its reversal condition** is the same as
ADR-35's: a separate non-superuser role makes privilege the mechanism and the trigger the
second line, at which point a session setting is no longer the narrowest available exception.

## Project Structure

```
specs/066-chapter-4-20/
├── spec.md · plan.md · research.md · data-model.md
├── contracts/retention.md
├── quickstart.md               §1 and §2 MEASURED, the rest predictions
├── baseline.txt                (phase 1 onward)
├── clauses.md · traceability.md · gaps.md   (phases 5, 7, 9)
└── tasks.md
```

```
relay-platform/
├── services/api/migrations/0024_retention_policy.sql       the CHECK on retention_days
├── services/api/migrations/0025_expiry_may_delete.sql      the FK's delete action and the
│                                                           trigger's named exception
├── services/api/src/db/schema.ts                           the constraint
├── services/api/src/db/retention-reads.ts                  NEW — the UNSCOPED enumeration
│                                                           of environments with a policy
├── services/api/src/db/repository.ts                       the per-environment delete,
│                                                           which IS tenant-scoped
├── services/api/src/retention/sweep.ts                     NEW — the command
├── services/api/src/retention/retention.itest.ts           NEW
├── services/api/src/environments/                          NEW — the PATCH route, module,
│                                                           controller, schema
├── services/api/src/app.module.ts                          the new module
├── services/api/src/isolation/targets.ts                   the new route, classified
└── vitest.coverage.config.mts                              pins for the new files
```

**TWO MIGRATIONS, AND THE SPLIT IS THE SAME HAZARD 4.19 RECORDED.** `migrate.ts` keys
`schema_migrations` on a filename with no checksum, so a file edited after it has applied never
re-runs while the ledger reports it done. Both are written before either applies.

## The fence bill, counted now

4.15's rule: count it in phase 1 where it can still change the sequencing, and read it as a
floor.

```
                            pages   appendix hunks it already carries
repository.ts                  52   5
schema.ts                      34   5
app.module.ts                  23   3
vitest.coverage.config.mts     23   16
targets.ts                     13   4
gauntlet.itest.ts              13   6
```

**SIX FILES**, counted at analysis rather than deferred to phase 1, which is what counting in
phase 1 is for. All to `fences/post-series.md` — every one is published by pages this chapter
does not own, and one rule for six files beats a judgement per file (4.8).

**AND THE SIXTH WAS MISSING UNTIL ANALYSIS PASS 6, WHICH IS THE INTERESTING PART: THE
ARITHMETIC WAS RIGHT AND THE POPULATION WAS SHORT.** All five original figures verify exactly.
What the list left out is the file T026's second half writes into — **a gauntlet attack is
written inside `gauntlet.itest.ts`**, not beside it, so classifying the new route in
`targets.ts` and covering it are two edits to two expensive files rather than one. The
precedent is exact and one chapter old: 4.18 added `GET /v1/audit-log` and its commit
`7f3992fc` touched **four** isolation files — `targets.ts`, `gauntlet.itest.ts`, `attack.ts`
and `attack.test.ts`. **So read the isolation directory as a family, not as `targets.ts`**:
`attack.ts` is 10 pages with 1 hunk, `targets.itest.ts` 11, `attack.test.ts` 3. Whether this
chapter reaches them depends on whether the new route needs a helper, which T014a is the task
that will find out.

**And `targets.ts` is still where 4.12's rule bites**: its entries sit next to rows the appendix
itself adds, so a hunk anchored there extends an existing hunk rather than adding one — 4.8
found the shape, 4.11 paid it on `codes.ts` and 4.12 paid it on this very file. `gauntlet.itest.
ts` carries six appendix hunks already, more than any file here but the coverage config, so
expect the same.

**AND THE BILL IS A CEILING AS OFTEN AS A FLOOR.** Chapter 4.19's plan named eight files and
the chain charged for five, because the work landed in fewer places than the file list
predicted. 4.18's list of 21 grew by six. The number is useful for sequencing and not for
prediction.

## Phases

1. **Setup and measurement.** The lane baseline, the CI baseline, the fence bill against the
   tree, and research R1–R7 re-read against the code rather than this document.
2. **The decisions.** The trigger's exception mechanism, the flag's name, whether the route is
   `PATCH /v1/environments/{id}` or something narrower — settled before a migration exists.
   **And whether setting a policy is a moderation action**, which is the one decision here with
   a schema cost: `moderation` obliges an `audit_log` entry, and that column's CHECK admits
   four `target_kind` values of which none is an environment.
3. **US1 — the expiry, and the pincer.** Both migrations, the sweep, and the delete that is
   refused today. **The red probe comes first**: assert the refusal, then make it pass.
4. **US2 — the objects go too.** The reverse reference check **is `unreferencedMediaIn`,
   which chapter 4.15 already wrote in the shape the planner can use**; this phase reads it,
   calls it, publishes the `deleted` storage event nothing has ever published, and repairs the
   two comments that promise a caller arriving one chapter later than it does.
5. **US3 — what runs it, published.** The clause's three obligations with a verdict each.
6. **The probes.** Each tenancy arm alone and in combination; the trigger still refusing
   everything it refused before; the sweep run twice.
7. **The documents.** FR-MOD-06 and FR-MED-11 read before being edited, **ADR-36**, SRS
   revision, both copies of the Part 4 table, `docs/12` row 21.
8. **The chapter.** 2,000–4,000 prose words, the hunks, `check:fences` to zero.
9. **The record and the close.** Coverage pins after the chain is zeroed, **and `check:fences`
   re-run after the pins go in.**

## Complexity Tracking

| the simpler thing | why it is not taken | what it would cost |
|---|---|---|
| `SET session_replication_role = replica` in the sweep | it is the hole ADR-35 published as the limit of its own guarantee, and it disables **every** trigger in the session | a sweep that is indistinguishable, at the database, from an attacker with the password |
| Drop `message_edits_message_id_fkey` | a version could then outlive its message, which is what makes the history trustworthy | the invariant moves from the schema into a procedure somebody maintains |
| Soft expiry — null the text, keep the row | FR-MOD-06 says **hard-deleted**, and a tombstone is precisely what expiry is not | a compliance promise met by a word change |
| A nullable `expires_at` on every message | 199,275 rows gain a column to express what `created_at` plus a policy already says | storage, a backfill, and two sources for one fact |
| Let the sweep delete objects by cascade | `media_objects` has **no foreign key to `messages`** — the link is a `media_id` inside jsonb | nothing to cascade; R2's reverse lookup is the only way |
| Build a scheduler | four clauses now want one and ADR-28 declined it three times | an architecture decision wearing a retention chapter's clothes |
| Publish `expires_at` on the message | a deadline the platform does not enforce, read by a compliance team | the exact field 4.18 refused for the audit log |

## Risks

- **AND THE READING COULD BE WRONG, WHICH IS WHAT AN ADR IS FOR.** *A retention sweep is a
  compliance path* is an argument, not a measurement: somebody could reasonably hold that
  constitution II means the FR-MOD-04 endpoint and nothing else, in which case FR-MOD-06 is
  unmet by decision and this chapter is *why the platform cannot expire messages*. **ADR-36
  records the reading, its two amendments and its reversal condition** — if a later chapter
  needs hard deletion on a third path, the category has stopped meaning anything and the
  decision is re-opened.
- **THE CHAPTER CHANGES A GUARANTEE THE PREVIOUS CHAPTER SHIPPED, AND THAT IS THE WHOLE RISK.**
  `message_edits` was made append-only yesterday and is being given an exception today. If the
  exception is wider than one verb on one table under one named flag, the honest course is to
  stop and record FR-MOD-06 as unmet rather than to widen it. **The probe that decides this is
  running the old refusals after the change**, not reading the new condition.
- **A bulk delete scoped wrong destroys rather than leaks.** Constitution I's usual failure is a
  read; this one is a `DELETE`. The per-arm probe matters more here than anywhere it has been
  run, and 4.19 measured that two of three scopes can be removed invisibly.
- **The lane cannot exercise the clause — until 2026-10-14.** Nothing is 30 days old, so every figure comes from a
  backdated fixture and **the cost of a real sweep is unmeasurable here**. 4.13's backdating
  piled 3,235 rows on one instant and turned twelve tests red; this one backdates per fixture.
- **FR-MED-11's reverse check is 106× the forward one** and runs per object. At lane scale that
  is fine and at tenant scale it is the thing that decides whether a sweep finishes.
- **TWO INDEXES ARE MISSING AND NEITHER IS OBVIOUSLY WORTH ADDING.** There is nothing on
  `messages.created_at`, so the sweep's own order sorts every pass; and finding the environments
  with a policy is a **sequential scan of 33,051 rows, 546 buffers, `Rows Removed by Filter:
  33050`**, where a partial index on `WHERE retention_days IS NOT NULL` would be nearly empty.
  **Both are phase-2 decisions and both get 4.1's treatment** — that chapter added the index its
  query obviously needed and measured a gap inside the run-to-run spread for +49% storage.
- **THE TWO SCALES DO NOT COINCIDE ON THIS LANE**, so the sweep's end-to-end cost cannot be
  measured here even with backdated fixtures: the busiest message environment holds **1,018
  messages and 0 media objects**, and the busiest media environment holds **531 objects and 843
  messages**. Any figure T038 publishes names which half it came from.
- **The sweep has no runner, and the clause is a compliance promise.** The other three clauses
  bounded by ADR-28's absent scheduler are reporting obligations. This one is a customer
  telling an auditor that data does not exist. Recording it the same way is right; saying so in
  the same tone is not.
