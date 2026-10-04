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

### One pass

    pass 1   3 findings   0 CRITICAL   opening the files the artifacts cite

**A1 and A3 are the same mistake at two scales**: the artifacts treat as open a question
the tree has already answered, once for a module and once for a classification. A1 came
from carrying a conclusion across from the chapter before it without re-checking its
premise — which is what the premise check exists to catch, applied to a plan rather than
to a clause.

## Notes

- Items marked incomplete require spec updates before `/speckit-clarify` or
  `/speckit-plan`. **All 16 pass.**
