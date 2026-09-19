# Implementation Plan: Chapter 4.12 — a link that expires, and who may hold it

**Branch**: `058-chapter-4-12` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)
**Input**: `docs/12` §3 row 13, movement V — FR-MED-08

## Summary

A route that turns a `media_id` into a one-hour signed GET URL, issued only to a caller who
could read a message referencing that object. The signing is arithmetic the platform already
does; the chapter is the authorisation and what it costs to ask.

**Read `research.md` first.** It settles the specification's flagged assumption **against** the
specification for the second feature running, and it finds that the obvious implementation of
FR-MED-08's own words — a membership check — would make media *less* readable than the message
carrying it.

## Technical Context

**Language/Version**: TypeScript 5.x, Node 22, NestJS · unchanged
**Primary Dependencies**: none added. `presign.ts` has signed `GET` since 4.10; `expiresIn` is
seconds, so one hour is `3600` against the upload slot's `900`. ADR-30 is not reopened.
**Storage**: Postgres (the reference lookup, plus one index) and MinIO/S3 (the bytes, untouched)
**Testing**: vitest — the api's integration config, the gauntlet, and the sealed outsider suite
**Target Platform**: Linux containers
**Project Type**: monorepo — `relay-platform` (code), `relay-tutorial` (chapter), `docs/`
**Performance Goals**: the reference lookup measured before and after an index, in buffers as
well as milliseconds (SC-004). Baseline measured before this plan: **2.886 ms and 1,016 buffers
on the refusal path**, against **0.018 ms and 5** with GIN `jsonb_path_ops` at 1.7% of the table.
**Constraints**: no parallel ACL (the SRS note under FR-MED-08); no byte passes through Relay
(ADR-13); the query engine stays in the repository layer (constitution I's lint rule).
**Scale/Scope**: one route, one index, one migration. The lane holds 66,516 messages of which
1,580 carry attachments.

### Open questions for the tasks phase

1. **One id per request, or several?** R8: every `/v1` path costs one `rest` operation, so a
   gallery of fifty images spends fifty of the tenant's budget. A batch shape would spend one.
   Against it: a batch refusal has to say which ids failed without saying why, which is the
   existence-oracle problem 4.11 solved by refusing to distinguish anything.
2. **Does the response carry the object's `state`?** FR-013 of 4.11 asserted delivery carries no
   state, and that was about the *message*. A delivery URL for a `pending` object fetches a 404
   from the store; whether the caller is told in advance is a different question with the same
   smell.
3. **Is the index created `CONCURRENTLY`?** The migration runner is forward-only hand-written
   SQL (ADR-16) and runs inside a transaction; `CREATE INDEX CONCURRENTLY` cannot. Decide and
   record, because the answer changes what a large tenant's deploy costs.

## Constitution Check

| Principle | Assessment |
|---|---|
| **I · Tenant isolation** | The predicate is `channelVisibleTo`, which is already scoped to `this.environmentId` and already refuses a private channel to a non-member. **The chapter reuses it rather than writing a rule**, which is the only way the SRS note's "no parallel ACL" is satisfied by construction. The gauntlet gains a forged-`media_id` read attack beside 4.11's forged-`media_id` write. |
| **II · No acknowledged message is lost** | Not engaged. This chapter writes nothing. |
| **III · Two data paths** | Not engaged. No analytical read, no cross-store query. |
| **IV · Single writer** | Not engaged. |
| **V · API-first** | One route, one error code — and the code is `not_found`, which **already exists** (R4). A chapter that adds a route usually adds vocabulary; this one does not, and `check:errors` reading 34/34 unchanged is asserted rather than assumed. |
| **VI · Requirement-driven, test-verified** | FR-MED-08 is a `T` clause. **Half of it was proven at 4.10** — `presign.itest.ts:53` is titled *"FR-MED-08's precondition"* — and the chapter says which half it did not build. The branch clause applies again: the authorisation predicate is tenant-isolation code, so the arms get the per-arm treatment 4.11 established, **not** a file percentage. `channelVisibleTo` is existing code with existing coverage; what is new is the reference lookup around it. |
| **VII · Boring by design** | No dependency, no table, no column, no state. One route, one index, one migration. |

**AND THE PRINCIPLE VI ROW IS WRITTEN AFTER READING THE CLAUSE, NOT WHEN THE PLAN WAS TEMPLATED.**
4.11's constitution table was wrong at principle VI and 4.10's plan was wrong at principle II —
both filled early and read past. The row above names the branch clause because the predicate is
isolation code, which is the thing that row exists to catch.

## Project Structure

### Documentation (this feature)

```
specs/058-chapter-4-12/
├── spec.md
├── plan.md              # this file
├── research.md          # READ FIRST — R1 settles the assumption against the spec
├── data-model.md
├── contracts/
│   └── media-delivery.md
├── quickstart.md
└── checklists/requirements.md
```

### Source code

```
relay-platform/
├── services/api/
│   ├── migrations/
│   │   └── 0017_media_reference_index.sql    # new — the tail is 0016
│   └── src/
│       ├── db/
│       │   ├── schema.ts                     # the index declared
│       │   └── repository.ts                 # the reference lookup, beside channelVisibleTo
│       └── media/
│           ├── media.controller.ts           # GET /v1/media/:id
│           ├── media.service.ts              # the refusal mapping
│           ├── presign.ts                    # UNCHANGED — GET and expiresIn already exist
│           └── delivery.itest.ts             # new file, so the chain charges nothing
└── packages/outsider/src/integrate.itest.ts  # fetches the bytes from outside (SC-010)
```

### The fenced files this chapter will touch

**Counted, not remembered** — 050's lesson, which 056 paid at twelve-said-seventeen and 057 paid
again at thirteen-said-twenty-two:

    file                                          titled fences (en + vi)
    services/api/src/db/repository.ts                    49
    services/api/src/db/schema.ts                        33
    services/api/src/isolation/gauntlet.itest.ts         15
    packages/outsider/src/integrate.itest.ts              5
    services/api/src/media/media.controller.ts            1
    services/api/src/media/media.service.ts               1
    services/api/src/media/delivery.itest.ts              0   — new, and free
    services/api/src/media/media.itest.ts                 0   — unfenced

**This is a starting point and has been wrong at every chapter, always low.** 057's list grew at
five of six analysis passes and every growth was a door nothing had named. `pnpm check:fences
--dump` after the first source edit is what answers it.

**And `repository.ts` at 49 is the expensive one.** 057 published a 201-line hunk for it. If this
chapter's lookup lands in the same file — and constitution I's lint rule says it must — the hunk
is the chapter's largest single fence cost, and the split between chapter and appendix should be
decided before the prose is written rather than after.

## Complexity Tracking

**One deviation, and it is the clause's words against the platform's behaviour.**

FR-MED-08 says *"channel membership"*. The platform's read rule is membership **for private
channels only** — 11,289 public channels on the lane against 995 private. Implementing the
clause literally would refuse a user the photo in a message whose text they can read.

The chapter implements the platform's rule, and the SRS is where that gets recorded if research
holds: the clause's parenthetical is a gloss on *"authorised to read the referencing message"*,
and this platform's answer to that question is `channelVisibleTo`. **Amending a clause because
measurement falsified it is what 4.6 through 4.11 each did**; this one may only need a sentence
saying which predicate the gloss refers to.

**Not a deviation, said so it is not mistaken for one**: an object with no referencing message is
readable by nobody. That is stricter than the specification assumed and it is the clause's own
note enforced (R1), not an extra rule.
