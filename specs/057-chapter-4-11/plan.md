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
| **II · No acknowledged message is lost** | **The one principle this chapter can break, and the plan did until analysis pass 3.** `outboxEventSchema` validates `attachments` with the same union at two arms and `consumer/runtime.ts` answers a failed parse with `message.term()` — so a message a new instance commits and an old one reads during a rolling deploy is destroyed, after the ack. The consumer never reads the field (zero occurrences) and neither does anything downstream, so the strictness costs the message and buys nothing (research R11). The envelope stays strict about its own fields; the attachment elements become permissive. The refusal half is unchanged and was always fine: the check runs before the insert, inside the same transaction. |
| **III · Two data paths** | Untouched. Nothing analytical is read or written. The send's existing request-log record is unchanged. |
| **IV · Single writer** | The message records the id, not a copy of the object's state — one source of truth for what an attachment is, which is what lets FR-MED-07 report a change later without the message having lied. |
| **V · API-first** | **There are two APIs and the artifacts described one until pass 2**, and the api→gateway response is a third door found at pass 4: `internalSendResponseSchema` is strict and `api-client.ts:247` parses it, so an old gateway reading a new api closes the socket **1011** — the schema's own comment, from the chapter that added the field (research R13). `messageSendSchema` embeds the same union, so the arm accepting changes the REST route and the socket's `message.send` frame together, and a live gateway test asserts the refusal this chapter removes (research R9). The arm's shape does not change; its behaviour does. `media_id` tightens to a UUID, which narrows a shape nothing was accepting (research R3), so CON-05's URL-versioning rule is not engaged. The removed code and the added one both land in `docs/08-error-reference.md`. **And 422 joins the error filter's ladder** — measured at analysis pass 1: the rungs are 400, 401, 402, 403, 404, 413, 415 and 503, so an unnamed 422 still answers `internal_error`, which is the filter's own *"lie the client cannot act on"*. Chapter 4.10 closed four and left this one. |
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
services/gateway/src/
└── session.itest.ts               # the socket door: one test converted, two added
services/api/src/
├── outbox/event.ts                # the durable reader: attachment elements become permissive
├── consumer/consumer.itest.ts     # a media envelope parses, red against today's arm
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

**Counted, not remembered** — 050's lesson, which 056 paid again at twelve-said-seventeen. This
list was six until analysis pass 1 counted the files the tasks themselves name, and it is still a
starting point rather than a substitute for `--dump`:

    file                                          titled fences (en + vi)
    services/api/src/db/repository.ts                    48
    vitest.coverage.config.mts                           33
    packages/protocol/src/codes.ts                       26
    services/api/src/messages/messages.service.ts        26
    packages/protocol/src/codes.test.ts                  17
    services/api/src/messages/messages.itest.ts          17
    services/api/src/isolation/gauntlet.itest.ts         14
    services/api/src/messages/zod-validation.pipe.ts      6
    packages/protocol/src/attachments.ts                  2
    services/api/src/outbox/event.ts                     11
    packages/protocol/src/internal.ts                     ?   — count at T005
    services/gateway/src/session.itest.ts                 9   + 8 excerpts
    services/api/src/consumer/consumer.itest.ts           9
    packages/outsider/src/integrate.itest.ts              4   — whole body at 3.26, diffs at 4.8 and 4.9
    packages/protocol/src/attachments.test.ts             0   — the only unfenced one

**Six at pass 0, ten at pass 1, eleven at pass 2, thirteen at pass 3, fourteen at pass 5**, and each
correction came
from counting rather than remembering. Pass 1 added the three the tasks already named — `codes.test.ts` (T009),
`messages.service.ts` (T022) and `vitest.coverage.config.mts` (T048), two of them among the most
expensive files in the chain. Pass 2 added `session.itest.ts`, which no artifact had mentioned at
all because no artifact had mentioned the socket (research R9). Pass 3 added `outbox/event.ts` and
`consumer.itest.ts`, which no artifact had mentioned because none had mentioned the consumer
(R11). Pass 5 added `integrate.itest.ts`, which no artifact had mentioned because none had
mentioned the sealed suite — **and every one of the five additions was a door, not a file.**
The chain cost is one `diff` hunk against the state 4.9's diff leaves; the vi whole body at 3.26 is
never compared to the repository (050-3) and a hunk for it would be an untranslated English page.

**The list has been wrong at every pass and in the same direction**, which is what 050 and 056
both recorded. It is a starting point for `--dump`, not a substitute.

Feature 056 measured what that costs: nine of seventeen hunks could not anchor at a chapter, and
two more anchored and broke the appendix's own older hunks. **Generate every hunk from
`check:fences --dump`, and test anchoring with an exact-match count rather than `patch
--dry-run`** — 056-7 records that `patch` applies with fuzz and said yes to seven hunks the
checker refused.

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

**AND THE UUID TIGHTENING IS SAFE BY ORDERING RATHER THAN BY DESIGN** (research R10). No durable
row carries a media attachment, because the arm has refused since 3.24, and the read paths cast
rather than parse. Both are facts about the timing of this change and neither is a property of it
— *"a reader of anything durable cannot require a field its writer did not have"* is the rule that
would otherwise apply, and it is the one `outboxEventSchema` broke.

## What analysis pass 1 changed

**422 was not in the ladder, and FR-009 required that it be.** Measured rather than read:
`protocol-error.filter.ts:67-81` maps eight statuses and 422 is not one of them. Every 422 in the
platform names its own code — `channel_member_limit_exceeded` twice, and `media_not_available`
until this chapter — which is why nothing has noticed. The chapter adds the rung rather than
softening the clause, because the alternative reading makes FR-009 mean "the thrower must
remember", and remembering is what the ladder exists to survive.

**Rejected: map 422 to this chapter's own code.** A channel-member-limit refusal that forgot its
code would then tell a caller their media is not attachable.

**FR-013 had no task and now has one**, and FR-008a states a requirement two tasks were already
implementing. Three more coverage gaps closed the same way; `tasks.md` carries them as suffixed
ids so the numbering a reader has already seen does not move.

## What analysis pass 4 changed

**The same defect as pass 3, on a door pass 3 did not open.** The union has **seven validators**
and four cross a boundary between processes that deploy separately; pass 3 fixed the two durable
ones and `internalSendResponseSchema` is the third. FR-018b, FR-018c, FR-020, SC-002c and four
tasks.

**And the reason it took four passes is that nothing listed the doors.** `data-model.md` §4b is
the table now: where each validator is, who parses it, and whether it crosses a skew. The
asymmetry it records is the whole rule — **strict where a value is judged, permissive where it is
forwarded.** The api's request schemas stay strict; the readers that hand the value onward do not.

**The edit path also carries attachments forward** (R14, FR-020): `repository.ts:4601` selects
them for `message.updated` and the 200 response, and this chapter creates the first media
attachment there is to preserve.

## What analysis pass 3 changed

**A constitution II violation, and it was in the plan rather than in the code.** The durable reader
refuses the shape this chapter makes the writer produce, and `message.term()` makes that
permanent. FR-018, FR-018a, SC-002b and two tasks. **The word `consumer` appeared zero times in
all six artifacts** and `outbox` five times, every one of them meaning *"a refusal writes no
outbox row"* — the sense that was already safe.

**And the lane cannot find it.** `RELAY_EVENT_CONSUMER=off` is set for the reason chapter 3.5
gave, and `outbox/event.ts`'s header records what that cost the last time: *"the api suite stayed
green through 505 tests with the defect in place."* SC-002b requires the test to fail against
today's arm, because a durable-reader test that cannot go red is the class this chapter is trying
not to join.

**`attachment_count` also changes meaning** (R12, FR-019). Recorded rather than fixed: a second
column is FR-MED-12's chapter.

## What analysis pass 2 changed

**The socket door.** Zero mentions of `gateway`, `socket` or `frame` across all six artifacts, and
the union has three doors: the REST route, the socket frame, and the internal seam the gateway
calls — one `attachmentSchema`, imported by all three. FR-001a, FR-001b and SC-002a are the
result, along with three tasks and a fenced file nobody had counted.

**And pass 1's own remediation left a gate red.** T011a added a generic 422 code and T010 wrote a
section for *"the new code's"*, singular — `check-error-codes.mjs` fails in both directions, so
T074 would have gone red on a code pass 1 introduced. FR-009b and an extended T010 close it. **The
fix is where the next defect is**, three features running.

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
