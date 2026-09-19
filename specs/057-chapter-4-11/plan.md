# Implementation Plan: chapter 4.11 — the half of the union that was refused

**Branch**: `main` (no feature branch; this project tags chapters on `relay-platform`) | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/057-chapter-4-11/spec.md`

## Summary

FR-MED-06. The `{ "type": "media" }` attachment arm chapter 3.24 built as a discriminated union
and refused by name starts accepting: a message may attach a `media_id` that names a media object
in the sender's environment, uploaded by the sender or by the tenant, in a state the clause
permits. Another tenant's id, another user's id and an id nobody owns are refused with one answer,
because three answers would be an existence oracle.

The code that has stood in for this since 3.24 — `media_not_available` — is deleted, on its own
registry entry's instruction.

**The chapter's two products are not the accept path.** They are what running the clause found:
FR-MED-06's `ready` state is unreachable and the database refuses it by name, and the arm's
existing `z.string().min(1)` turns a malformed id into a **500** the moment the arm stops
refusing.

## Technical Context

**Language/Version**: TypeScript 5, Node 22, ESM in `services/dispatcher`/`services/ingester`, CommonJS in `services/api` (ADR-15's dialect split)

**Primary Dependencies**: NestJS 11, drizzle-orm, zod 4, `@relay/protocol`. **Dependency count moves by zero** — the check is a read the repository already has a client for.

**Storage**: PostgreSQL 18. `media_objects` read, `messages` written, one transaction.

**Testing**: vitest. `services/api/vitest.config.mts` for units (no store, since the follow-up to 056), `vitest.integration.config.mts` for `.itest.ts`, `vitest.coverage.config.mts` for the ratchet.

**Target Platform**: Linux, `docker compose` locally and in CI since the 056 follow-up.

**Project Type**: a published tutorial with a working platform beneath it — chapter prose in `relay-tutorial`, code in `relay-platform`, tagged `part4-ch11`.

**Performance Goals**: one additional read per send that carries media attachments, and none for a send that carries none. Whether it is one query or N is decided in tasks, and the figure is measured rather than predicted.

**Constraints**: the refusal is indistinguishable across three conditions (SC-002); no byte of a media object is read; nothing is added to delivery.

**Scale/Scope**: one schema arm, one predicate, one code removed, one code added, one attack extended. No new route, no new table, no migration.

## Constitution Check

*GATE: passed before Phase 0 research, re-checked after Phase 1 design.*

| principle | reading |
|---|---|
| **I · Tenant isolation** | The whole of the chapter. The environment predicate is the check; the **indistinguishable refusal** is the second half, and it is the half a design review would drop. `POST /v1/channels/:channelId/messages` is already a gauntlet target — and is its `CANARY_TARGET` — so the accounting direction that applies is "attacked but not for this identifier" (research R7). |
| **II · No acknowledged message is lost** | Untouched. The check runs before the insert, inside the same transaction; a refusal writes no message and no outbox row. |
| **III · Two data paths** | Untouched. Nothing analytical is read or written. The send's existing request-log record is unchanged. |
| **IV · Single writer** | The message records the id, not a copy of the object's state — one source of truth for what an attachment is, which is what lets FR-MED-07 report a change later without the message having lied. |
| **V · API-first** | The arm's shape does not change; its behaviour does. `media_id` tightens to a UUID, which narrows a shape nothing was accepting (research R3), so CON-05's URL-versioning rule is not engaged. The removed code and the added one both land in `docs/08-error-reference.md`. |
| **VI · Requirement-driven, test-verified** | FR-MED-06 is a `T` clause. **One of its arms cannot be tested** and the chapter says so with the database's own refusal rather than a skipped test (research R2). |
| **VII · Boring by design** | No dependency, no table, no route. One code deleted on its own instruction, one added. |

**PASS, with one clause partially unverifiable and named as such.** That is this project's third
consecutive chapter in that position — 4.7 amended FR-ANL-06, 4.8 defined FR-ANL-10's quantity and
computed nothing, 4.10 amended FR-RTL-05 — and the difference here is that no amendment is needed:
the clause is right, and the platform reaches one of its two states.

## Project Structure

### Documentation (this feature)

```text
specs/057-chapter-4-11/
├── plan.md                        # this file
├── spec.md
├── research.md                    # R1-R8, every row run
├── data-model.md                  # the read, the predicate, and what the shape cannot express
├── quickstart.md                  # five scenarios and the gates
├── contracts/
│   └── media-attachment.md        # the arm, the refusal, and what is removed
├── checklists/requirements.md
└── tasks.md                       # /speckit-tasks
```

### Source (relay-platform)

```text
packages/protocol/src/
├── attachments.ts                 # the arm: refinement removed, media_id becomes a uuid
├── attachments.test.ts            # the arm's unit tests
├── codes.ts                       # media_not_available deleted, one code added
└── codes.test.ts                  # three assertions about the departing code
services/api/src/
├── messages/
│   ├── messages.schema.ts         # unchanged — the cap already counts both arms
│   ├── messages.service.ts        # maps the repository's refusal to a protocolError
│   ├── messages.itest.ts          # the refusal tests become the accept tests
│   └── zod-validation.pipe.ts     # a comment citing a code that will not exist
├── db/repository.ts               # the predicate, inside sendMessage's transaction
└── isolation/gauntlet.itest.ts    # the existing write attack, extended
docs/
├── 04-srs.md                      # a revision recording what the chapter found
└── 08-error-reference.md          # one section removed, one added
relay-tutorial/
├── app/(en)/part-4/chapter-11/…   # the chapter
└── fences/post-series.md          # whatever no chapter can anchor
```

### Fenced files this chapter is likely to touch

**Counted, not remembered** — 050's lesson, which 056 paid again at twelve-said-seventeen. The
list below is a starting point for a task that counts it against the checker, not a substitute for
counting:

    packages/protocol/src/attachments.ts
    packages/protocol/src/codes.ts
    services/api/src/messages/messages.itest.ts
    services/api/src/messages/zod-validation.pipe.ts
    services/api/src/db/repository.ts
    services/api/src/isolation/gauntlet.itest.ts

`codes.ts` is a 12-chapter chain and `repository.ts` is the largest file in the platform. Feature
056 measured what that costs: nine of seventeen hunks could not anchor at a chapter, and two more
anchored and broke the appendix's own older hunks. **Generate every hunk from `check:fences
--dump`, and test anchoring with an exact-match count rather than `patch --dry-run`** — 056-7
records that `patch` applies with fuzz and said yes to seven hunks the checker refused.

## Phase 0 — research

Complete. `research.md` carries eight entries; three changed the plan.

- **R1 settled the specification's flagged assumption against the specification.** A NULL
  `user_id` means the tenant uploaded it and a user token of that tenant may attach it — because
  chapter 4.10's controller says *"a photo sent by a person and an attachment uploaded by a
  customer's backend are the same operation"*, and the strict reading makes them unequal.
- **R2 ran the CHECK.** `violates check constraint "media_objects_state_check"`.
- **R3 ran the lookup with a non-UUID.** `invalid input syntax for type uuid` → a caller-triggered
  500 once the arm accepts. The schema tightens.
- **R5 found `protocolCode` has exactly one user**, and this chapter removes it. The mechanism
  stays with no user and says so, following 4.10's `service_unavailable`.

## Phase 1 — design

Complete: `data-model.md`, `contracts/media-attachment.md`, `quickstart.md`.

**Post-design constitution re-check: PASS.** The design added no dependency, no table and no route.
The one thing it added that the spec did not name is the UUID tightening, which is R3's measurement
rather than a preference, and it narrows a shape nothing accepted.

## Phase 2 — what `/speckit-tasks` has to get right

**The order the mechanics force.** The schema arm cannot accept before the predicate exists, and
the predicate cannot be tested before the arm accepts — so the two land together, and
`messages.itest.ts`'s three refusal assertions become the accept assertions in the same change.
`check:errors` fails in both directions until the code is removed **and** the reference section is
removed **and** the new code has a section, so those three are one task, not three.

**The riskiest task is the refusal's indistinguishability**, because it is the one a later edit
weakens without noticing. SC-002 is byte-identical bodies, not three 422s.

**And the chapter has no new route**, which removes the check that has caught eight chapters
running. The derivation will report nothing. The accounting direction that still applies is the
gauntlet's second — a route that is attacked and not for this identifier — and it has to be asked
deliberately because nothing will ask it automatically.

## Open questions for `/speckit-analyze`

1. **One query or N.** Ten attachments could be one `IN` lookup or ten. One query is obvious and
   makes "which one failed" a set difference; the `field` path in the refusal needs the index, so
   the set difference has to preserve position. Worth deciding before it is written.
2. **Whether the new code's name should mention media at all.** `media_not_attachable` names the
   operation; something more generic would survive FR-MED-08's own refusals. The registry's style
   is that a code says what a client does about it, and all three conditions have the same answer.
3. **Whether the SRS needs a revision.** No clause is falsified — R1 and R2 are readings, not
   contradictions. 4.10's precedent says record a reading in a revision when two clauses disagree;
   here they do not, so the default is a chapter and a `gaps.md` entry with no SRS change. Check
   that against FR-MED-06's exact words before deciding.
