# Specification Quality Checklist: Chapter 4.21 — "Erasure, and every path it must find"

**Purpose**: Validate specification completeness and quality before planning
**Created**: 2026-10-04
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

## The premise check, run before the spec was written

This project's record says the premise check is worth more than any later pass,
and the two chapters before this one proved it in opposite directions — 4.19
found four of five obligations already met, 4.20 found none of three. Here it is
mixed, which is why the table in the Overview is the first thing in the spec.

**Measured, not assumed:**

    no erasure endpoint                zero hits for `erase` in any controller
    deleteMessage writes attachments: []   FR-MED-10's unlink is ALREADY MET
    unreferencedMediaIn callers        0, still — three hits, all definition
                                       or comment, unchanged by chapter 4.20
    users / members / messages         192,641 · 172,965 · 205,628 naming a user
    media_objects with a user_id       3,979 · and 11,050 WITHOUT
    audit_log naming a user target     1,324

**And the analytical store, which is where the chapter is:**

    api_requests        205,697 rows   no user column at all
    connection_events     1,081 rows   user_external_id String
    message_events            0 rows   and no producer under services/
    daily_usage_billing     824 rows   AggregateFunction(uniq, Nullable(UUID))
    daily_usage_v2           56 rows   the same

## Three findings that shaped the spec

**1 · `analytical records` is not one thing, and one of its three parts cannot
comply.** A `uniqState` is a sketch with no subtract operation, so a user's
contribution to 880 rollup rows can be recomputed but not removed — and
recomputing needs `message_events`, which has 0 rows, no producer and a 90-day
TTL. That is why FR-005 exists: the receipt must name a store it could not
clear rather than omit it.

**2 · DR-15's prefix supports TENANT erasure and not USER erasure.** The clause
says object keys are `{environment_id}/{media_id}` *so bucket-level lifecycle
rules and tenant export/erasure operate on prefixes* — verified against real
keys. There is no user in the path, so FR-MED-10's *a user's media objects* is a
database lookup one key at a time, not a prefix operation. The clause is right
about what it claims and does not claim this.

**3 · `a user's media objects` is undefined for 73% of them.** 11,050 of 15,029
rows carry `user_id IS NULL`, which chapter 4.11 established was deliberate:
FR-MED-06 made the column nullable because a server-side upload has no user. An
erasure that takes only the 3,979 attributed rows is correct and incomplete, and
saying which is the chapter's job.

## Why no clarification markers

Three decisions a reader might expect to be open are each settled by something
already written down:

- **Whether erasure is synchronous or scheduled.** ADR-28 has declined a
  scheduler four times; a fifth is not a new question. Synchronous satisfies
  *within 30 days* trivially and the chapter says the bound is unexercised.
- **Whether a tombstone keeps its author.** FR-USR-05 already carries the
  escape — *unless message deletion is explicitly requested* — and FR-MOD-04 is
  that request.
- **Whether the audit log is erased.** It is append-only under ADR-35, which
  chapter 4.20 narrowed once already. Narrowing it again for this would be the
  second exception in two chapters, and the tension is stated instead.

## Analysis pass 1 — three findings, 0 CRITICAL, all three fixed

**The question**: *open the files the artifacts cite.* `tasks.md` cites several by
behaviour rather than by name, and `plan.md` assumed a module shape without checking what
the path prefix already holds.

- **A1 HIGH — the route needs no new module, and the plan assumed one by carrying chapter
  4.20's shape across.** `@Controller("v1/users")` already exists with
  `@UseGuards(CredentialGuard)` and `@Accepts("application")` at class level — **the exact
  three decorators the plan specified** — and already holds `@Delete(":externalId")`.
  Measured: `users.controller.ts` is **4 pages with 0 appendix hunks** against
  `app.module.ts`'s **23 with 4**, so a new module costs **19 extra pages to duplicate
  three decorators**. 4.20 genuinely needed one because `v1/environments` had no
  controller at all; this prefix does. **Fixed** across `plan.md`, `research.md`'s bill,
  `contracts/erasure.md` and five tasks.
  **AND THE BILL IS NOT THE MAIN ARGUMENT.** The contract's central worry is that erasure
  and FR-USR-05's deletion must not be confused — *"two verbs that differ only in what
  they preserve must not differ only in a flag"* — and **two `DELETE`s side by side in one
  file are harder to confuse than two in different files.** The cheaper option is also the
  one that serves the stated requirement.
- **A2 MEDIUM — T017 described an enforced constraint as a preference.** It said to reuse
  `destroyMediaObjects` *"rather than writing a second path"*; `rendition.itest.ts:282`
  asserts `toHaveLength(1)` on row-deletion paths, so a second `delete(mediaObjects)`
  **turns it red** with its own instruction attached. **Fixed**: the task says the test
  enforces it, and that the companion assertion expects this chapter to add a byte-delete
  caller.
- **A3 MEDIUM — T025a presented a classification the file already answers for the
  adjacent route.** `"DELETE /v1/users/:externalId": "moderation"` is there, reasoned
  *"removes a person's profile and memberships"*, and `ACTION.deleteUser` exists.
  **Fixed**: erasure is the same judgement applied to a strictly larger action, and the
  new `ACTION` entry is modelled on the existing one.

**WHAT VERIFIED CLEAN, AND ONE I NEARLY REPORTED AS A DEFECT.**
`audit_log_target_kind_check` admits `'user'`, so T025b costs no migration and no
`schema.ts` hunk — which is why this chapter's classification can be `moderation` where
4.20's could not. `destroyMediaObjects(ids: readonly string[])` matches T017.
`users.itest.ts` exists. R4's `deleteUser` quotation is verbatim.

**And `deleteUser` DOES write its audit entry.** A first grep over lines 4386–4440 found
no `recordAction`, which would have meant chapter 4.18's moderation log was incomplete on
a route it classifies `moderation`. The method spans **4394–4455** and the call is at the
end: **the window was too short, not the code wrong.** Re-measured by brace depth before
reporting, and the finding evaporated — which is the only reason it is recorded here
rather than in `gaps.md`.

## Analysis pass 2 — two findings, ONE CRITICAL, both fixed

**The question**: *write the queries nobody has written.* The artifacts carried
platform-wide totals; nobody had checked that the analytical key means the same thing as
the operational one.

- **B1 CRITICAL — the analytical delete had no environment predicate, and the spec's own
  FR-008 forbids that.** `data-model.md` wrote `DELETE FROM connection_events WHERE
  user_external_id = …`. The table **has** an `environment_id UUID` column, and external
  ids are unique **per environment** — which the spec states in its own Edge Cases.

      users: external ids reused across environments      1,576
      connection_events: 54 distinct ids, 460 (env, id) pairs
        …used in MORE THAN ONE environment                   23
      the worst — `tuan`          111 environments · 156 rows
        correct for one tenant                                4
        WRONGLY DELETED from 110 others                     152     97.4%

  **Fixed** in `data-model.md`, T019, T023(b), `contracts/erasure.md`, FR-008 and a new
  research section R8. **An unscoped delete is not a near miss here; it is mostly wrong.**

- **B2 MEDIUM — the mechanism that would have caught it stops at exactly that
  boundary.** Six of the traversal's seven stores are reached through `Repository`, whose
  constructor requires an `environment_id`, so they are scoped by construction and nobody
  has to remember. **ClickHouse is the only store that class does not mediate, and it is
  the only one the draft got wrong.** **Fixed**: the analytical function takes
  `environmentId` as a parameter — the signature carrying what the constructor would
  have — and T023(b) asserts a second tenant's identically-named user survives.

**NOTHING CONTRADICTED ITSELF IN A WAY A READER WOULD NOTICE.** FR-008 required the
scope, the Edge Cases named the exact collision, and the query sat sixty lines below
both. Requirement and statement were each right alone, which is why the pass that found
it is the one that ran the query rather than the one that read the files.

**What verified clean**: `usage_active_users` keys on a uuid and cannot collide; every
Postgres path goes through the scoped `Repository`; `connection_events` already carries
`environment_id`, so the fix is a predicate rather than a schema change. And the probe
table in R3 and quickstart §2 is unscoped on purpose — it measures the verb, not the
predicate — which R3 now says, because a reader copies shapes.

## Analysis pass 3 — three findings, ONE CRITICAL, all three fixed

**The question**: *walk the tasks in execution order.* The first pair does not work.

- **C1 CRITICAL — the red probe could never go red.** T015 called `deleteUser` and
  asserted what survives: the row, the messages, the billing rows. **This chapter
  preserves all three on purpose** — erasure is a separate verb, which is the whole of
  T010, T011 and R4 — so T021's *"watch it go red"* described something that cannot
  happen. The probe would have been green at the open, green after the traversal and
  green at close-out, **and read as evidence three times.**

  **A genuine refusal exists and is the better probe**, measured:

      DELETE FROM users WHERE id = <one with memberships>
        ERROR: violates foreign key constraint "members_user_id_users_id_fk"
      DELETE FROM users WHERE id = <one with no children anywhere>
        DELETE 1                                       <- the control

  All five foreign keys are `NO ACTION`, so the row is unreachable until the children
  go — which is exactly what T016's *children first, the row last* traverses. **Fixed**:
  T015 asserts the refusal with its control, T021 inverts it, and the characterisation
  test the first draft was reaching for is kept as a separate assertion — green today
  and green forever, going red only if somebody collapses the two verbs.

  **THE RITUAL WAS COPIED WITHOUT THE CONDITION THAT MAKES IT MEAN SOMETHING.** This
  project's rule is *a probe that was never green proves nothing about the fix*. The
  corollary nobody had written down is **a probe that can never go red proves nothing
  either.**

- **C2 HIGH — the route takes no body, so `z.strictObject` had nothing to validate.**
  Three artifacts specified a strict body schema and a 400. Measured against the
  existing bodyless `DELETE /v1/users/:externalId`: `{"totally":"unknown"}` and `{}`
  both answer **404**, because no `@Body()` decorator exists to parse either. **Fixed**:
  constitution VI's fifth bullet is recorded **not engaged** rather than met, and T020a
  asserts the route declares no `@Body()` — the property that makes the bullet
  inapplicable. Adding one purely to reject would be work with no clause behind it.

- **C3 MEDIUM — this route is not in 058-3's population.** `spec.md` said it *"would
  make twenty-four"*. That population takes **uuid-typed** path parameters; this one
  takes a string external id, and `DELETE /v1/users/no-such-xyz` answers **404**, not
  500. **Fixed**: the count stays at twenty-three and the spec says why.

**C2 AND C3 ARE THE SAME MISTAKE POINTING THE OTHER WAY FROM C1.** Chapter 4.20's route
was a `PATCH` with a body and a uuid parameter, so both sentences applied there. This one
is a `DELETE` with neither, and four artifacts repeated the claims inherited rather than
checked. **Three of this pass's three findings are carried sentences**, which is what an
execution-order walk finds that a reading does not: the artifacts are internally
consistent, and consistently about a different route.

## Analysis pass 4 — three findings, ONE CRITICAL, all three fixed

**The question**: *open the code the tasks will edit.* T019 placed the ClickHouse
statement and gave a reason; the reason was wrong, and following the thread found
something worse.

- **D3 CRITICAL — the erasure's analytical statement is SQL injection through a URL path
  parameter.** `AnalyticalStore.query` takes a SQL string and **has no parameter
  binding** — `request-log.module.ts:16` says so and names `endpoint` as *"the sharpest
  caller-supplied value on this surface"*, because chapter 4.8 defended that one with a
  **closed derived set**. An external id has no closed set: `z.string().min(1).max(255)`,
  any 255 characters, arriving from a path that no body schema parses.

      POST /v1/users  {"external_id": "ev'il OR 1=1 --"}     201, round-tripped
      interpolated into the scoped count                   1,081   the whole table
      bound, {env:UUID} and {uid:String}                       0
      bound, `tuan` scoped — the control                       4

  **An erasure for that user deletes `connection_events` across all 460
  tenant-environment pairs.** It is 4.8's sentence word for word, and **it defeats the
  `environment_id` predicate pass 2 added** — R8 and R9 are one surface, and R8 alone
  produces a statement that looks scoped and is not.

  **4.8's REMEDY DOES NOT TRANSFER AND THE REPLACEMENT IS MEASURED.** That chapter's
  answer was *a type, not an escape*; free text has no type. ClickHouse's `param_<name>`
  binding works, with a control proving it does not simply refuse everything. **Fixed**
  as **FR-014**, **SC-014**, **T019a** (extend the client rather than escape at the call
  site — an escape is a thing every future caller must remember) and **T023a**, the only
  assertion that tells a scoped statement from one that looks scoped.

- **D1 HIGH — T019's placement cited a rule that does not cover ClickHouse.** The lint
  rule restricts **`drizzle-orm`, `ioredis`, `pg`**; no ClickHouse client is named, and
  **`db/` holds no ClickHouse code at all** — `metering/`, `request-log/` and `audit/`
  each hold their own. **Fixed**: the statement goes in `users/`, with the real reason.

- **D2 HIGH — the receipt's analytical count cannot come from the delete.** Measured in
  the shape `query` actually issues: a `DELETE` answers **HTTP 200 with a 0-byte body**,
  so the method returns `[]`. R3's rationale — *"a receipt states a count, so it must use
  the verb whose count it can trust"* — was wrong about the mechanism; **neither verb
  returns a count.** **Fixed**: the decision survives on a better reason — after the
  lightweight form a `SELECT count()` is accurate and after the mutation it is not, so
  the receipt can **verify** with one verb and only **predict** with the other.

**D1 IS WHY D3 WAS REACHABLE.** The task reasoned about placement from a rule it had not
read, and **a rationale that does not apply is also a rationale that stops you asking the
next question** — *what does this client do with a string?* The answer was one grep away,
in a comment written two chapters ago.

**And D2 is the sixth carried-or-assumed claim across four passes**: a correct decision
resting on a mechanism that does not exist, which is pass 1's A1 and pass 3's C2 again.

The probe user created to measure D3 was deleted; `users` is back to 0 matching rows.

### Four passes

    pass 1   3 findings   0 CRITICAL   opening the files the artifacts cite
    pass 2   2 findings   1 CRITICAL   writing the queries nobody had written
    pass 3   3 findings   1 CRITICAL   walking the tasks in execution order
    pass 4   3 findings   1 CRITICAL   opening the code the tasks will edit

**A1 and A3 are the same mistake at two scales**: the artifacts treat as open a question
the tree has already answered, once for a module and once for a classification. A1 came
from carrying a conclusion across from the chapter before it without re-checking its
premise — which is what the premise check exists to catch, applied to a plan rather than
to a clause.

## Notes

- Items marked incomplete require spec updates before `/speckit-clarify` or
  `/speckit-plan`. **All 16 pass.**
