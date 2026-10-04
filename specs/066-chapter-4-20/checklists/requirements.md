# Specification Quality Checklist: Chapter 4.20 — The messages that expire

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-10-03
**Feature**: [spec.md](../spec.md)

## Content Quality

- [X] No implementation details (languages, frameworks, APIs)
- [X] Focused on user value and business needs
- [X] Written for non-technical stakeholders
- [X] All mandatory sections completed

## Requirement Completeness

- [X] No [NEEDS CLARIFICATION] markers remain
- [X] Requirements are testable and unambiguous
- [X] Success criteria are measurable
- [X] Success criteria are technology-agnostic (no implementation details)
- [X] All acceptance scenarios are defined
- [X] Edge cases are identified
- [X] Scope is clearly bounded
- [X] Dependencies and assumptions identified

## Feature Readiness

- [X] All functional requirements have clear acceptance criteria
- [X] User scenarios cover primary flows
- [X] Feature meets measurable outcomes defined in Success Criteria
- [X] No implementation details leak into specification

## What the premise check found, before a word of the spec was written

`docs/12` §7.5 asked chapter 4.19 to check its premise and four of five obligations turned
out already met. The habit transferred, and here it inverted: **none of FR-MOD-06's three
obligations is met, and the interesting one is refused by the database.**

| measured | |
|---|---|
| `environments.retention_days` | exists since chapter 2.1 — *"DECLARED IN 2.1 AND STILL EMPTY … read by nothing in seventeen chapters"* — and set on **0 of 33,051** environments |
| a scheduler | **none.** 0 `schedule:` triggers, no cron, no timer. ADR-28's precedent, and this would be the **fourth** clause bounded by the same absence |
| a hard delete of a message | **refused**, with a control: a message *with* a version row gives `message_edits_message_id_fkey`; a message *without* one gives `DELETE 1` |
| what references `messages` | **exactly one table**, `message_edits`, `NO ACTION`. So the FK is the only obstacle rather than one of several |
| messages blocked today | **5,495**, where chapter 4.19 measured 4,565 at its close and handed the number to row 22 |
| `media_objects` → `messages` | **no foreign key at all.** FR-MED-11's link is a `media_id` inside jsonb, so nothing in the database will cascade it and nothing will notice if it is wrong |
| the lane's oldest message | **19 days.** 0 messages older than 30, 90 or 365 days — the clause cannot be exercised at any of its four settings without a backdated fixture |

**THE CHAPTER IS THE OBSTACLE, NOT THE JOB.** Chapter 4.19 wrote the FK collision down,
declined to pre-solve it, and named row 22 as the chapter that would meet it. **Row 21 meets
it first** — and resolving it here means erasure inherits the resolution rather than repeating
the discovery.

## Analysis pass 1 — four findings, none CRITICAL, all fixed

**The question**: *do the files the artifacts cite say what they are cited as saying?* — the
mechanism with the best record as a first pass.

- **A1 HIGH — the ADR had no number.** `ADR-35` is the last in both homes, so this chapter's is
  **ADR-36**, and the plan said *"a new ADR"* six times without naming it. T045 could have been
  executed and produced a record the SRS, the SAD and `docs/12` have nothing to cite. Chapter
  4.18 named ADR-35 in its plan before writing a line of it. **Fixed in plan, tasks and
  research** — and the post-correction sweep found three more mentions after the first edit,
  which is the third feature running that the sweep has paid.
- **A2 MEDIUM — `api_keys.credential_hash` does not exist.** The columns are `id,
  environment_id, public_id, secret_hash, salt, prefix, name, created_at, last_used_at,
  revoked_at`. `quickstart.md`'s policy section queried it and would have failed before the chapter did
  anything. **Fixed** by taking the environment id from the seeder's own stderr line, which is
  the right source anyway, and the correction is in the preamble's list.
- **A3 MEDIUM — SC-012 had two halves and one task.** *"…published, **and re-measured at the
  close**."* T007 measures the refused count at the open and nothing re-measured it, on a
  number that moves **by one per deletion by construction** — the clearest case of 4.17's rule
  there has been. **Fixed** as T063a, publishing the pair rather than the later figure alone.
- **A4 LOW — the fence bill left one file uncounted.** `targets.ts` is **13 pages**, and the
  appendix already carries **4 hunks** for it, so the bill is five files. Counting it at
  analysis is what counting in phase 1 is for. **And it is the file where 4.12's rule bites**:
  its entries neighbour rows the appendix itself adds, so T026's hunk likely extends an
  existing one rather than adding one.

### Checked, and clean

```
no environments surface anywhere          the route is genuinely new
docs/07's Part 4 row 21                   exists — "The messages that expire"
src/retention/sweep.ts -> dist/retention/ the layout migrate.js already proves
nothing parses an environment response    no route, so no reader to break
```

**The last one is the risk 065 was bitten by, checked by type rather than assumed.** A required
field reaching a strict schema one seam away cost that chapter three red tests. Here the new
route creates a response shape **nothing yet parses** — `createEnvironment` is a fixture helper,
not a parsed contract — so the class does not apply.

**AND THE MECHANICAL COVERAGE MAP RAISED 18 ALARMS OF WHICH 17 WERE FALSE**, which is 4.11's
finding reproduced almost exactly (14 of 51 there). Every FR and SC except SC-012 is discharged
by a task that does not cite its number — FR-001 by T025, FR-006 by T028–T030, FR-009 by T035,
FR-012 by T042–T047. Recorded so a later pass does not re-walk them, and it is why
`traceability.md` is built by reading.

## Analysis pass 2 — four findings, none CRITICAL, all fixed

**The question**: *what do the queries nobody has written yet actually cost?* The sweep's
predicate and the media reverse-lookup were both described in prose and neither had been run.

- **B1 HIGH — there is no index on `messages.created_at`.** The table carries
  `messages_pkey`, `messages_channel_id_sequence_unique`, `messages_idem` and
  `messages_attachments_gin` — nothing for an age predicate, nothing for the order T020
  demands. **T020 said *keyset, not offset* with nothing to keyset on.** Fixed as a phase-2
  decision (T013a) with 4.1's treatment attached: measure the index before adding it, because
  that chapter added the one its query obviously needed and bought a gap inside the run-to-run
  spread for +49% storage.
- **B2 HIGH — the plan sketched the slow shape.** As a join across all environments the age
  bound lands in a `Join Filter`: **`Rows Removed by Join Filter: 1018`, 604 buffers** — every
  message in a policied environment fetched and discarded, each pass. Per environment with the
  bound as a constant it is **74 buffers** and reaches `channels_environment_last_activity`.
  **8×.** Fixed in `plan.md`'s Performance Goals, `data-model.md`'s sweep sketch, T013a and
  T020.
- **B3 MEDIUM — selecting the policied environments is a seq scan every pass**: 33,051 rows,
  **546 buffers, `Rows Removed by Filter: 33050`**. A partial index on `WHERE retention_days IS
  NOT NULL` would be nearly empty, because the column is 0-populated. Named in the risks and in
  T013a, with the same measure-first rule.
- **B4 MEDIUM — the two scales do not coincide on this lane.** The busiest *message*
  environment holds **1,018 messages and 0 media objects**; the busiest *media* environment
  holds **531 objects and 843 messages**. So an end-to-end sweep cost cannot be observed here
  even with backdated fixtures — it is a sum of two measurements, and T038 now says which half
  each figure came from.

### What this changed about the plan's own framing

The Performance Goals cited **883 against 94,132 buffers** for the media check and called it
*"the shape the sweep is written in rather than a figure to beat"*. That was a real measurement
of a real query — **and it is the second query the sweep runs.** The first one, the predicate
that decides which messages expire at all, had no measurement, and the shape the plan sketched
was the slow one.

**It is 4.12's error, caught earlier than 4.12 caught it.** That chapter published 26x-160x for
an index measured on a query its route did not send, and three analysis passes went by before
anybody asked what the planner would do with the shipped version. Here it was pass 2, before a
line of code.

### Checked, and clean

```
channels_environment_last_activity   exists, and the fast form reaches it
messages_attachments_gin             exists (4.12's), and R2's 883 figure uses it
the cascade's cost                   not separately measurable — the trigger refuses
                                     it today, so it is phase-3 work
```

## Analysis pass 3 — four findings, none CRITICAL, all fixed

**The question**: *walk the tasks in execution order and ask, at each one, what it assumes is
already true.* The thing most worth stressing was T015's deliberate inversion — the red probe
before the migration.

- **C1 HIGH — T013a decided two indexes and no task wrote either.** T016 is *the CHECK
  constraint* and T017 is *the FK and the trigger*; an index decided in phase 2 had no carrier
  in phase 3, so it would have landed in `baseline.txt` and nowhere else. **That is 4.8's
  sentence exactly** — *049 measured the retarget and never landed it; a measurement is not a
  repair* — and it exists **because pass 2 added T013a**: a new decision task without a matching
  implementation task, a defect an earlier pass created. **Fixed**: T016 is the carrier, and if
  the answer is *neither index*, the migration's comment says so.
- **C2 HIGH — nothing rebuilt the api image before the quickstart.** §3 onward hit
  `localhost:4000`, which is the composed **container**, so `PATCH /v1/environments/{id}` would
  answer 404 against an image built before this chapter — and the failure reads as a missing
  route rather than a stale build. **4.11 named this as the third kind of stale build** and 065
  rediscovered it mid-phase-9. **Fixed** in T067 and in the new prerequisites section.
- **C3 MEDIUM — the quickstart had no prerequisites section.** §0 was a measurement, not setup,
  so a reader on a cold machine had no `compose up`, no `pnpm build`, no `migrate`. **Fixed**,
  and every section renumbered — which the post-correction sweep then caught in **six places**
  across four files, the fourth feature running that the sweep has paid.
- **C4 MEDIUM — T015's probe is correctly red for four tasks and nothing said so.** T017 applies
  the trigger change; T018, T019 and T020 run with `retention.itest.ts` failing for the right
  reason; only T021 inverts it. **Fixed**: T017 names the window and says a red nobody predicted
  inside it is a finding.

### Checked, and clean

```
targets.itest.ts:195   expect(CLASSIFICATIONS.length).toBe(derived.length) — both directions,
                       so T025 and T026 must land together, and they are adjacent
targets.itest.ts:123   deliberately NOT a hard route count, with the comment saying so
T015 before T016/T017  the inversion holds: globalSetup migrates files that do not yet
                       exist, so the probe runs green and goes red exactly at T017
```

**T015's inversion surviving the walk is the result I most wanted**, because it is the one
ordering in this feature that runs against the usual direction. What was missing was only the
note that the red it produces is expected.

## Analysis pass 4 — four findings, none CRITICAL, all fixed

**The question**: *open the code the tasks will edit.* The sweep is entirely new, so the thing
to check was not a function's behaviour but where a cross-tenant sweep is allowed to live.

- **D1 HIGH — a cross-tenant sweep cannot use `Repository`.** Constitution I: *"a repository
  layer whose constructors require an `environment_id`"*. Every instance is bound to one
  tenant and the sweep enumerates all of them; T019 said *add the expiry read and delete to
  `repository.ts`*, as methods. **Fixed**: the enumeration is an unscoped function, the
  per-environment delete stays a scoped method on a `Repository` constructed per environment —
  which satisfies the constructor requirement literally rather than by exception.
- **D2 HIGH — three sibling files already do this and the plan named none.**
  `services/api/src/db/` holds `audit-reads.ts`, `storage-reads.ts` and `usage-reads.ts`, and
  the second's header says why the directory matters: *"chapter 4.7's reconciler was written
  with its Postgres read inline in `metering/` and failed lint on the import; this file is
  where that rule puts the read."* **Fixed**: `retention-reads.ts`, named in the plan's
  structure, T019 and the data model's sweep sketch.
- **D3 MEDIUM — T035 probed arms the correct design does not have.** `pendingMediaObjects`
  states the property for the sweep this one is modelled on: *"the route above it takes no
  tenant parameter at all, **which is the isolation property to assert rather than a scope to
  add**. A route that could be asked for one tenant's objects would be a route worth forging."*
  **Fixed**: the delete's scope is probed per arm; the enumeration's is asserted about its
  signature. **A probe looking for an arm to delete there would report nothing red and mean
  something entirely different by it.**
- **D4 MEDIUM — B3's partial index has a measured precedent nobody cited.**
  `media_objects_pending_age`, migration `0019`, is a partial index on `created_at` for the
  identical sweep shape, and `repository.ts` records what it bought: **93 buffers to 4** on a
  50-row batch, *"a top-N heapsort over 3,158 rows"* to an index scan. **Fixed** in T013a, with
  measure-first still standing.

### What D1 and D2 really are

Not a design question raised by this pass — **a design question the platform answered at 4.7,
wrote into a file header, and has repeated three times.** The plan reached for `repository.ts`
because that is where queries live, which is right, and missed that *a method on a tenant-bound
class* and *an exported function in the same directory* are different things with constitution I
between them.

### Checked, and clean

```
the lint rule   permits services/api/src/db/** — so a sibling file is legal
                where 4.7's inline read in metering/ was not
```

**Operational note**: the compose stack was **down** at this pass — `docker compose ps` returned
nothing. Nothing here needed it, because the index precedent is documented in the source rather
than re-measured, but **phase 1's T001 needs it up.**

## Analysis pass 5 — three findings, ONE CRITICAL, all three resolved

**The question**: *open the constitution and the SRS rather than the source.* 065's eighth and
ninth passes found their best results that way, and so did this one.

- **E1 CRITICAL, DECIDED BY THE USER — two documents forbid exactly what FR-MOD-06 requires.**

      constitution II   "hard deletion exists ONLY ON THE COMPLIANCE PATH"
      FR-MSG-08         "Hard deletion shall occur ONLY VIA THE COMPLIANCE DELETION ENDPOINT"
      FR-MOD-06         "expired messages HARD-DELETED BY A SCHEDULED JOB"

  No artifact in this feature mentions it. The plan's principle II row says *"the clause is the
  exception — FR-MOD-06 is the licensed way to lose one"*, **which is an exception neither
  document grants.** This is **4.19's finding run backwards**: that chapter cited FR-MSG-08 as
  the clause its defect broke, this feature's own spec quotes it for that reason, and nobody
  noticed the sentence forbids this chapter too. **Left open by this pass deliberately** — the
  three available readings were put to the user, because amending a constitution principle is outside
  `/speckit-analyze` and recording a P3 clause unmet is a product call.

  **DECIDED: a retention sweep IS a compliance path** (option A). The constitution's own word is
  **path**, not *endpoint*, so **the rule hardest to change is the one that already permits
  this** — and the cost is two SRS amendments, FR-MSG-08 and DR-06, which are the two documents
  narrower than the principle. Recorded as **ADR-36 decision 1**, with research R1a carrying the
  argument, the three rejected readings and the reversal condition: *if a later chapter needs
  hard deletion on a third path, `compliance path` has stopped being a category.* The option
  deliberately avoided is **soft expiry** — clearing `text` and keeping the row satisfies all
  three clauses word for word and is the only reading that keeps every internal rule and still
  misleads somebody.
- **E2 HIGH — a third document, naming the exact population the spec targets.** DR-06:
  *"Deleted messages shall **retain their row**; only `text` and `attachments` shall be
  cleared."* US1 scenario 5 says *"a tombstone is a message that has expired like any other"* —
  deliberately destroying the rows DR-06 protects. **Fixed** by naming DR-06 in that scenario
  and tying it to E1 rather than letting one acceptance line settle a three-document conflict;
  the note now cites **ADR-36 decision 1** as what resolved it.
- **E3 MEDIUM — the undo that would have existed is two rows up and unbuilt.** FR-MOD-05,
  *"exporting all data for a tenant as newline-delimited JSON"*. A tenant who wants to keep
  what a policy destroys has no supported way to take a copy first. **Fixed** in the contract's
  *no undo* and in T032's clause list — which turns a shrug into a measured statement.

### Checked, and clean

```
ADR-28         cited correctly — "FR-ANL-06's daily job has no runner, and that is
               recorded rather than built"
principle VI   the plan answers all five bullets in its own table — 065's pass-9
               lesson transferred rather than being relearned
```

## Analysis pass 6 — four findings, 0 CRITICAL, all four fixed

**The question**: *open the publishing side.* Five passes had read documents inside this
feature directory and the platform source they cite. Nothing had opened the tutorial
repository, `ci.yml`, or the two sibling features' task lists — and the fence bill is a
counted claim sitting in `plan.md` unverified.

- **P1 HIGH — the bill's arithmetic was right and its population was short.** All five figures
  verify exactly against `grep -rl 'title="<path>"'`: 52 / 34 / 23 / 23 / 13. The list still
  missed a file, because **a gauntlet attack is written inside `gauntlet.itest.ts`** and T026's
  second half therefore edits **13 pages carrying 6 appendix hunks** — more than any billed
  file but the coverage config. The precedent is one chapter old and exact: 4.18 added
  `GET /v1/audit-log` and commit `7f3992fc` touched **four** isolation files. **Fixed**: the
  bill is six files with each one's existing appendix hunks beside it, T006 counts the rest of
  the isolation family, T026 names the file it writes into, and T060's biggest-first ordering
  reads off the longer list. **A re-count cannot catch this and a re-derivation can** — the
  list has to come from the files the tasks name, not the files the plan remembered.
- **P2 HIGH — two CI gates validate this feature's own tasks and no task ran them.**
  `check:srs` is what checks T044's revision 1.27; `check:figures` is what catches a figure
  passed as `chart` instead of `code`, which `pnpm build` compiles green. The tasks ran
  `check:docs` and `check:fences` only, and the tutorial's own `pnpm lint` not at all.
  **The gate-recording task existed in 063 (T005) and 064 (T003), was dropped at 065, and 066
  inherited the gap** — invisible from inside this directory, because the artifacts are
  consistent with each other. **Fixed** as T003a, with T061 widened to all six and told to
  compare each counted line against T003a's.
- **P3 HIGH — `FR-020` is not a clause.** `spec.md` cited it for *a message survives its
  archived channel*. It is **feature 043's feature-local id** for the SRS revision-order
  checker, recorded as such in `docs/09:75`, and it appears **zero times** in `docs/04-srs.md`,
  which uses prefixed ids throughout. Its companion `FR-USR-05` is real and carries the
  deleted-author half correctly, which is what made the pair read as checked. **Fixed** to
  **FR-CHN-10**, quoted. This is 052's `FR-003a`, 053's leak into two published documents and
  063-4's three-way collision, for the fourth time — and **the mechanical coverage grep's only
  true hit of eighteen**, caught only because the number fell outside the spec's own range.
- **P4 MEDIUM — `docs/07` holds two rows numbered 21.** Part 3's *"The email nobody was
  sending"* at line 194 and Part 4's at line 602, 408 lines apart, and T047 said *"row 21"*.
  **Fixed**: match on the title. *Name a chapter, never number it*, inside the task that
  numbered one.

**What verified clean**: `docs/12` row 21 present and matching — both Part 4 table copies exist
with the right per-file vocabulary, CLOSED in one and SHIPPED in the other — the chapter
registration covered with the right seven fields and slug, `code` not `chart` already in T054,
and **no `(vi)` task, correctly**: the translation reaches part 4 chapter 3 against English's
19, so there is no twin to write. T076's *147,331 with 2,669 of headroom* matches `wc -c`
exactly.

## Analysis pass 7 — six findings, ONE CRITICAL, all six fixed

**The question**: *run the quickstart as an execution trace, and open the suite no task
mentions.* The stack is down, so the quickstart was traced statically — every variable, every
identifier, every expected output against the repository. The CRITICAL came from somewhere
else: a stray citation in a migration comment, followed out of curiosity.

- **Q1 CRITICAL — US2's predicate already exists, tested, in a file this chapter is already
  billed for.** `repository.ts` exports **`unreferencedMediaIn(db, environmentId, olderThan,
  limit = 100)`** — chapter 4.15's, environment-scoped, and **already in the two-query form**
  that 4.12's measurement forces. No artifact in this feature named it, and T028 said to write
  it. **R2 re-derived its measurement from scratch and got the same answer**, which is the only
  reason anyone can be confident it is the right function. **Fixed**: T028 reads it instead of
  writing one and records two things to check rather than assume — its `lt(createdAt,
  olderThan)` arm and its `limit = 100`; T029 calls it; T029a repairs the comment.
  **ITS COMMENT IS WHY SIX PASSES READ PAST IT**: *"CALLED BY NOTHING YET, AND THAT IS NOT AN
  OVERSIGHT. `docs/12` row 22, the erasure chapter, is where it gets a caller."* That is 065's
  own CRITICAL inverted — *a comment that explains an absence as a necessity is why four
  chapters read past it* — and here the absence explained is the absence of a **caller**,
  which is exactly what this chapter supplies. **Six source comments across five files point at
  row 22, and this chapter is row 21.**
- **Q2 HIGH — the analytical meter would keep charging for destroyed bytes.**
  `storage-event.ts`: *"THE CAUSES ARE FOUR AND THE CALLERS ARE THREE … `deleted` from
  **nothing yet** … this signature is the one it will call."* **Fixed** as **FR-013** and
  T029b. **The asymmetry is what makes it skippable**: the operational quota self-corrects,
  because committed bytes are a `sum(declared_bytes)` over rows (SRS 1.17), so every
  operational assertion stays green while the event-sourced meter drifts — the drift 4.16
  measured at 4,436 MB charged against 30.7 MB held.
- **Q3 HIGH — `$OLD` and `$NEW` were used five times and set nowhere**, and `$CH` was set and
  used nowhere, because the step between them was the ellipsis *"… mint a token, add a member,
  send two messages, edit one of them …"*. 4.12's `$OBJECT_KEY`, exactly. **Fixed**: the block
  is written, and it echoes both ids with a note on what an empty one looks like downstream.
- **Q4 HIGH — the immutability re-check could not fail.** `message_edits_append_only` is
  `BEFORE UPDATE OR DELETE … **FOR EACH ROW**`, §4 edited only the expiring message, so §6's
  tamper matched zero rows, fired the trigger zero times and returned `UPDATE 0` with no error
  — under an expectation reading *"still refused"*. **Fixed**: §4 edits both messages, §6
  counts the surviving version rows first, and the dangling `'see below'` label row became a
  real count. *Ask what would have to be false for this to fail.* Here: nothing.
- **Q5 MEDIUM — the sealed suite, dropped the same way the gate task was.** Named 29 times in
  063's tasks, once in 064's, zero in 065's, zero here. It is one of CI's four jobs, reached by
  no local lane, and **T025 adds a Nest module** — which compiles, typechecks and lints while
  failing on the first request (4.10). **Fixed** as T070a, after T067's rebuild.
- **Q6 LOW — §3's comment described the seeder's streams backwards.** It showed
  `environment_id` then `rk_dev_` and said *"the second line goes to stderr"*; `:77` is
  `console.error` and `:78` is `console.log`, so it is the first. The commands were right and
  the explanation of why was inverted, which is the version a reader trusts and then breaks.

**What verified clean**: `DATABASE_URL` is real and its default is byte-identical to the string
§0 passes · `migrate.js` has a `require.main` entry · the trigger's error text matches §2
verbatim · the seeder is idempotent, so §3's two invocations agree on the tenant ·
`${RELAY_POSTGRES_PORT:-5432}` carries a default, so §1 and §2 work unexported.

## Analysis pass 8 — three findings, ONE CRITICAL, all three fixed

**The question**: *what does a new mutating route do to the sets derived from a booted
application?* Pass 6 found the gauntlet by asking what a route costs the fence chain. The same
question asked of behaviour has a longer answer: **three lists key off one derived route set,
and the tasks covered two.**

- **R1 CRITICAL — `moderation-routes.ts` holds 24 entries for 24 derived routes and this
  chapter's route makes 25.** `moderation-routes.itest.ts` fails in **both** directions from a
  booted app — *"these routes exist and nobody decided whether they are moderation"* one way,
  an entry naming no route the other. `owedADecision` filters to mutating and not-`/internal/`,
  which `PATCH /v1/environments/{id}` is. **Zero `/v1/environments` entries exist in either
  list today**; T026 added the `targets.ts` one and nothing added this. **Fixed** as T026a, with
  the enumeration rule written down: the three lists are reachable only by
  `grep -rn deriveTargets`, because nothing else records that they are a set.
- **R2 HIGH — the classification is a real decision and it has a schema cost.** The file's own
  precedent: `POST /v1/channels/:channelId/archive` is moderation because it *"removes a shared
  space from use for everyone in it"*; `POST /v1/channels` is provisioning and is not. **Setting
  `retention_days = 30` destroys every user's messages past thirty days, for everyone, with no
  undo** — the archive test met harder. **And `moderation` is not one word**:
  `Repository.recordAction`'s `targetKind` is the closed union `"user" | "message" |
  "membership" | "channel"`, mirrored by `audit_log_target_kind_check` in `0021_audit_log.sql`
  **and again** at `schema.ts:1360`, which is 34 pages of fence chain. **Fixed** as **FR-014**,
  T013b (decide in phase 2, with the bill measured beside the decision) and T026b.
  **The mechanical half of R1 fails loudly in phase 6; this half is one word in a lookup table
  and a wrong word there is silent forever.**
- **R3 HIGH — the route's credential decorator is unprobed.** T035 probes the sweep's tenancy
  arms and the enumeration's signature, both well-judged, and T014a *reads* the guard's
  decorators at design time. 4.18 ran this exact probe on a READ route and found that deleting
  `@Accepts("application")` answers an end-user token **200 with the tenant's whole moderation
  history**, while the controller's own 403 defended a case that cannot arise. **Here the
  consequence is worse than disclosure** — an end-user token that can set a thirty-day policy
  destroys the tenant's history. **Fixed** as T035a.

**What verified clean, and three were worth the look.** `contracts/retention.md` holds: all
three error codes exist in `codes.ts` **and** `docs/08-error-reference.md`, and
`@Accepts("application")` does answer 403 `wrong_credential_type` at `credential.guard.ts:144`.
**The request-log's endpoint set is free** — it calls `deriveTargets` off the running router,
so a new route joins the closed set with no edit, which is 4.8's design paying off two chapters
later. **`tenant-scope.itest.ts` classifies base tables, not routes**, and this chapter adds no
table. Migrations stop at `0023`, so `0024` and `0025` are free. T046 names SAD §6.1 correctly
— `retention_days INT,` is at line 489 and the section opens at 481. **And `clauses.md` is a
deliverable, not a missing file**: T032 writes it, and pass 7's closing note saying it had not
been read against the tree was wrong.

## Analysis pass 9 — three findings, ONE CRITICAL, all three fixed

**The question**: *read principle VI as five bullets with their own sub-clauses, and ask of each
success criterion whether it names an instrument that exists.* Pass 5 read the constitution's
**principles**; this pass read the **clauses inside one bullet of one principle**.

- **S1 CRITICAL — bullet 3 names three gating mechanisms and two do not exist.** The clause is
  *"The cross-tenant suite (Principle I), **dependency vulnerability scans, and the OWASP Top
  10 scan** gate releases: critical findings block ship."* The plan's row answered the gauntlet
  alone and said **met**. Measured: one workflow file, **zero** matches for
  `audit|snyk|trivy|owasp|zap|codeql|dependabot`, no `.github/dependabot.yml`, no `pnpm audit`
  in any of the eight `package.json`. **Fixed**: recorded UNMET on bullet four's precedent,
  with the measurement in the row and a `gaps.md` entry in T064.
  **THE ROW IS THE ERROR ITS OWN HEADING WARNS ABOUT.** That table exists because 065's ninth
  pass found a check answering one of principle VI's five bullets, and it is headed *"because a
  row that answers one bullet reads as answering five"*. It then answered one clause of three.
  **057's shape for the third time: a CRITICAL inside the artifact written to prevent its own
  class** — and the remedy is always finer-grained than the error it fixed, which is why the
  next one is finer again.
- **S2 HIGH — bullet 5's second clause was uncovered on a new write endpoint.** *"unknown
  fields are rejected on write endpoints"* is a MUST. The plan's row discussed validation and
  `gaps.md` 058-3 and stopped short of it; the contract's refusal table had four rows and this
  was not one. **The convention was already here** — `z.strictObject`, 7 uses in
  `channels.schema.ts` and 4 in `messages.schema.ts` — so the gap was a missing assertion, not
  a missing design. **Fixed**: a fifth refusal row, and **T025a** tests an unknown field for a
  400. 065 met this schema from the producer's side and three tests answered
  `unrecognized_keys`; this is the same strictness from the caller's.
- **S3 MEDIUM — FR-013 and FR-014 had no success criterion**, and the bullet-1 row read
  *"12 FR and 12 SC"* against 14 FR. **Both are this analysis's own doing**: passes 7 and 8
  each added a requirement and neither added its verification, which is exactly what bullet 1
  obliges. **Fixed** as SC-013 and SC-014, cited from T029b and T026a, with the count corrected
  and the reason left in the row. **The number that would have caught it was sitting in the row
  that went stale**, so the instrument and the thing it measures drifted together — which is
  the argument for putting a count in a verdict rather than a word.

**What verified clean**: **all twelve original success criteria name an instrument that
exists** — SC-001–006 the retention suite, SC-007 `clauses.md` (T032), SC-008 `git diff`
(T068), SC-009 the CI error set (T073), SC-010 `check:fences` and the build (T061), SC-011 the
word count (T062), SC-012 T007 with T063a's re-measure. Not one names a tool nobody has. Bullet
4 was already recorded UNMET with its reason, which is the treatment S1 now gets, and bullet 2
says honestly which two of its three named concerns are this chapter's. `traceability.md` has
T050, *by reading, not by grep*.

## Analysis pass 10 — four findings, 0 CRITICAL, all four fixed

**The question**: *walk the list in execution order.* Pass 3 did that at 83 tasks. Nine were
inserted afterwards by passes 6 through 9, each argued inside its own body and **none placed by
anyone looking at the whole sequence.**

- **W1 HIGH — `T026b` was tagged `[US1]` and sat inside Phase 4 between two `[US2]` tasks.**
  Pass 8 anchored its insertion on T030 and it landed in the wrong story block. Phase 4's
  independent test is *"expire a message with a sole-referenced attachment and one with a
  shared attachment"* and says nothing about an audit entry, so **US1 could not have shipped
  complete without a task living in US2's phase**. **Fixed**: moved beside T026a.
- **W2 HIGH — the Dependencies & Execution Order block described the 83-task list.** It named
  T005, T015/T016/T017, T010/T011 and T065a, which was the complete set four passes ago, and
  **not one of the nine new tasks**. **It is the section a reader executes from**, so three
  real constraints existed only inside individual task bodies. **Fixed**: T013b blocks T026a
  and T026b, T029b comes before T029a, T003a blocks T061 — with a paragraph naming all nine
  and what went wrong, so the next inserter sees the block is theirs to update.
- **W3 MEDIUM — T029a repaired a comment describing a state T029b had not produced.** Order
  was T029 → T029a → T029b, and T029a's own text says `storage-event.ts`'s *"the causes are
  four and the callers are three"* becomes four and four *"with T029b"*. **Half the task was
  correctly placed** — `repository.ts`'s *"called by nothing yet"* is false the moment T029
  lands — and half was one task early. **Fixed**: T029a runs after both, and says why it sits
  where it does.
- **W4 MEDIUM — T026b wrote a migration with no number.** T016 is `0024_retention_policy.sql`
  and T017 is `0025_expiry_may_delete.sql`; T026b said only *"a migration altering
  `audit_log_target_kind_check`"*. **Fixed** as `0026_audit_target_environment.sql`. T016's own
  text carries the reason this matters: `migrate.ts` keys the ledger on **filename with no
  checksum**, so a file edited after it has run never re-runs while the ledger reports it done.

**What verified clean**: the other seven insertions hold their phases. T003a sits with phase 1's
other baselines; **T013b is right in phase 2**, whose purpose line is *"the exception's exact
shape, settled before DDL exists"* and whose own cost is a schema change; T025a precedes T026;
T035a sits beside T035; T070a follows T070 and T067's rebuild as its text requires. No `[P]`
conflicts — none of the nine is marked parallel, and T029a and T029b touch the same files.

**EVERY ONE OF THE FOUR IS A PLACEMENT ERROR AND NOT A CONTENT ERROR.** The tasks said the
right things; three said them in the wrong place and the index of ordering constraints was
never updated at all. **That is this feature's third instance of one shape** — after a task
dropped by copying a list forward (pass 6) and a requirement added without its verification
(pass 9) — and the one where the instrument that would have caught it, the Dependencies block,
is itself what went stale. **An edit made with three lines in view is correct locally and
unplaced globally, and nothing in a diff shows that.**

## Analysis pass 11 — three findings, 0 CRITICAL, all three fixed

**The question**: *measure the carried ledger; do not copy it.* 043 re-measured twenty-three
carried items and **four were wrong while three had closed with nobody working on them.** T064
carries eight ids and nothing in ten passes had checked one.

- **V1 HIGH — 058-3's "sixteen routes" is twenty-two, and was wrong when it was written.**
  That entry is not sloppy: it measured against a composed api, with a control, and **published
  its own method** — `@Param("channelId")` 13 and `@Param("messageId")` 3, across
  `messages.controller.ts` and `channels.controller.ts`. The method is what was short. It never
  opened `webhooks.controller.ts`, where **six routes take `@Param("id") id: string`
  unvalidated** and `webhook_endpoints.id` is `uuid PRIMARY KEY`. **Carried verbatim through
  059, 060, 061, 062, 063, 064 and 065, into this chapter's contract and plan.** **Fixed** at
  four sites, with the correction recorded against 058-3 the way 062 corrected 055-3. The
  carry-rather-than-fix argument gets **stronger** with the real figure, which is the only
  reason correcting it here is safe rather than scope creep.
- **V2 HIGH — the carry list omitted 065-4 and the five items 065 marked "checked, not live
  here", two of which THIS FEATURE made live.** **050-8**, nothing drains the records the stack
  publishes: `compose.yaml` has no `ingester` service and **pass 7's FR-013 adds a `deleted`
  producer to that stream**. **062-12**, 68 of 139 files unpinned: T065 adds pins for this
  chapter's several new files. And **065-4** is the finding T035 is built on — the task quotes
  its measurement and never carries its id. **Fixed**: T064 is a table now, with what pass 11
  already measured against each row. **A carried ledger is re-measured against the feature as
  it stands at close-out, not as it stood when the list was written** — and this one has gained
  a requirement since.
- **V3 MEDIUM — 064-5 was carried at a weaker prior than the one already paid for.** 065's
  table records it as *"did not fail in any of three lane runs on this host"*; T064 listed the
  bare id, which throws that away. **Fixed**: carry the measurement, not the id.

**What verified clean, by measurement rather than by reading.** **064-1 re-measures exactly**:
ADR-31 through 34 are in `docs/05-sad.md` and appear **zero** times in `docs/06`, while ADR-35
is in both — so 065 did write it into both homes and the carry correctly did not grow.
**065-2 reproduces**: `repository.ts:5376` sets the column from SQL `now()`, line 5380 reads it
back as a millisecond `Date` through the driver, and line 5411 writes that into
`message_edits`, beside a comment warning that two edits inside one microsecond collide. All
eight ids exist and their one-line descriptions match their headings.

**A NEAR-MISS WORTH RECORDING, BECAUSE IT WOULD HAVE BEEN A CONFIDENT FALSE FINDING.** The
first instrument — grepping each `gaps.md` for foreign-feature ids **as headings** — returned
five for 063, **zero for 064 and zero for 065**, which reads as a ledger decaying by attrition
across three features. Both 064 and 065 carry a full re-measured ledger **in a table section**,
which a heading-grep cannot see. **The control was opening the files**, and the rule it pays
into is this project's own: *a zero from an instrument is a claim about the corpus only if the
instrument can be shown to have read it.*

## Analysis pass 12 — three findings, 0 CRITICAL, all three fixed

**The question**: *run it.* Eleven passes read. This project ranks *ask the database a question
with a yes-or-no answer* first among the three mechanisms that find things, and T005 says the
chapter moves if the pincer has moved since 2026-10-03 — which was yesterday. Postgres was
brought up and four queries run.

**EVERY HEADLINE FIGURE RE-MEASURES EXACT, AND NOBODY HAD CHECKED ONE.**

    environments                     33,051   artifacts: 33,051   EXACT
      with retention_days set             0   artifacts: 0        EXACT
    messages                        199,275   plan.md             EXACT
    distinct message_id in edits      5,495   T007                EXACT
    audit_log naming a message        1,435   T009                EXACT
    oldest message               2026-09-14   quickstart §1       EXACT
    messages older than 30 days           0   quickstart §1       EXACT
    busiest env by messages           1,018   T038                EXACT
      …its media objects                  0   T038                EXACT
    busiest env by media                531   T038                EXACT
      …its messages                     843   T038                EXACT

- **X1 HIGH — the premise expires on 2026-10-14 and the quickstart's safety rests on it.** §3
  sets `retention_days = 30` on the demo tenant and §5 runs the sweep. Today that destroys only
  the backdated fixture. **The demo tenant is `bbda7667…`, which is the busiest media
  environment on this lane**: 843 messages, 531 objects, **0 past thirty days today and 570
  crossing by 2026-10-20** — destroyed irreversibly, in a tenant `reset-lane.mjs` does not
  restore by design. **Fixed**: §3 carries a precondition guard that counts what is already at
  risk and says STOP, and §5's dry run must read **1** before the destructive line is run.
  **The hazard arrives with no code change, no diff shows it, and no checker reads a date.**
- **X2 MEDIUM — every artifact stated the negative undated.** *"nothing on this lane is thirty
  days old"* across the quickstart, `research.md` R5, `spec.md`, `plan.md` and T038. 4.17's
  rule — a number measured at one moment is a fact about that moment — is applied by T063a to
  SC-012's refused count and was applied by nothing to the age. **Fixed** at seven sites, each
  carrying 2026-10-04 and the 2026-10-14 crossing.
- **X3 MEDIUM — `message_edits` precision measured by path, which nobody had done.**
  `ended_by='edit'`: **5,549 of 5,549 millisecond-exact, 100.00%** — 065-2 confirmed from data
  and not only from source. `ended_by='deletion'`: **50 of 1,114, 4.49%**, where chance
  predicts ~0.1%. The 50 are **interleaved** with precise rows rather than preceding 4.19's fix
  — ms-exact span 11:06→12:17 on 2026-10-03, first precise row 11:11. Both writers are in
  `repository.ts` and the deletion path does use SQL `now()`. **Fixed** into T064's carry table
  as a measurement **with no theory attached**, because the cause is not identifiable from
  source and inventing one would be worse than recording the number.

**X3 IS A MEASUREMENT 065 COULD NOT HAVE TAKEN.** Before its fix the column was 100%
millisecond on every row, so there was no contrast; the fix is what makes 4.49% legible as an
anomaly rather than as the background. **A repair can create the instrument that shows what it
did not repair.**

### Twelve passes

    pass 1   4 findings   0 CRITICAL   opening the files the artifacts cite
    pass 2   4 findings   0 CRITICAL   writing the queries nobody had written
    pass 3   4 findings   0 CRITICAL   walking the tasks in execution order
    pass 4   4 findings   0 CRITICAL   opening the code the tasks will edit
    pass 5   3 findings   1 CRITICAL   opening the constitution and the SRS
    pass 6   4 findings   0 CRITICAL   opening the tutorial, `ci.yml` and two sibling features
    pass 7   6 findings   1 CRITICAL   tracing the quickstart, and one stray citation
    pass 8   3 findings   1 CRITICAL   what a new route costs the sets derived from a booted app
    pass 9   3 findings   1 CRITICAL   principle VI's bullets read as clauses, and the SC instruments
    pass 10  4 findings   0 CRITICAL   the list walked end to end, after nine insertions
    pass 11  3 findings   0 CRITICAL   the carried ledger measured instead of copied
    pass 12  3 findings   0 CRITICAL   RUNNING it — every figure exact, and a dated premise

**Four passes found nothing critical, the fifth found the thing that decides whether the
chapter can ship as specified, and the sixth found three things no document in this directory
could contain.** The conflict pass 5 found was reachable from the first page of the spec —
FR-MSG-08 is quoted in it — which is why *read the clauses, not the identifiers* is this
project's most-cited rule. Pass 6's additions are its companion: **P1, P2 and P4 are invisible
from inside `specs/066-chapter-4-20/`**, and P2 is a task that two earlier features had and
this one does not. It is 057's *artifacts that agree with each other and not with the tree*,
one repository over — and the thing that was drifting was the task list itself.

## Notes

- Items marked incomplete require spec updates before `/speckit-clarify` or `/speckit-plan`
- **No `[NEEDS CLARIFICATION]` markers were raised.** The three decisions a reader might expect
  to be open — which column, whether to build a scheduler, and how to resolve the foreign key —
  are each settled by something already written down: the column exists and is named in two
  published documents; ADR-28 declined a scheduler for the same reason three times; and the FK
  resolution is a design question for `/speckit-plan` with the measurement already in hand.
  Recording them as assumptions with their evidence is more useful than asking.
