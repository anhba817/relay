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

## Notes

- Items marked incomplete require spec updates before `/speckit-clarify` or
  `/speckit-plan`. **All 16 pass.**
