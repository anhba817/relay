# Implementation Plan: Chapter 4.14 — "Pending, ready, rejected"

**Feature**: `060-chapter-4-14` | **Date**: 2026-09-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/060-chapter-4-14/spec.md`

## Summary

FR-MED-07 is two sentences and neither is met. **Sentence one**: every door that serves a message
puts the attachment's current state on it, read at serve time. **Sentence two**: when an object
leaves `pending`, a frame goes to every channel holding a message that references it, so a
placeholder resolves without polling.

The approach, after Phase 0: the state goes on the **delivery** attachment schema only, never on
the request side and never stored on the message; the event rides a **third arm on the existing
`revision:{channel_id}` fabric** rather than a sixth subject grammar; and the producer hangs off
the `applied` boolean the verdict's compare-and-set already returns, so a duplicate verdict
announces nothing without new machinery.

**No migration.** `0018` shipped the states, 4.12 shipped the referencing lookup, 4.13 shipped
the compare-and-set. This chapter writes **a new attachment shape**, a fabric arm, a frame and a
producer.

**Pass 5 swept the class pass 4 patched.** Reusing `revision:{channel_id}` means every site that
reaches into a revision's message has to learn a third arm — **eight in production across three
files and six in tests**, measured with one grep, where pass 4 had named one. Two of them are the
gateway's routing key and its own publisher; two more are a test harness and two unguarded
assertions. **When the count of a class keeps growing, stop counting failures and ask the
repository** — that rule is in CLAUDE.md and this is the pass that applied it.

**And the rolling-deploy window is now recorded** rather than left for somebody to report as a
bug: an un-upgraded gateway drops a `kind: "media"` frame with a log naming the subject and not
the reason, so SC-001 is false during a deploy and FR-009's floor is what repairs it.

**Pass 4 found the seam has no publisher, and that the fabric's publisher assumes one arm
shape.** `MESSAGE_PUBLISHER` is declared by `MessagesModule` and deliberately unexported, so
`InternalModule` must provide its own — a failure that compiles, typechecks and lints clean and
appears on the first request, which is 4.10's finding exactly. And `publishRevision` derives its
subject from `revision.message.channel`, which the media arm does not have.

**Pass 3 resized the producer work.** `recordMediaVerdict` returns `{applied, state, objectKey}`
and no tenant, so the fan-out's scoped query has nothing to scope with. Two changes, not the one
research first described: return `environment_id` from the verdict, and give the query a
module-level scoped entry point.

**Pass 1 resized the schema work.** The first version of this plan said the state went on one
existing delivery schema. `attachmentSchema` has four structural users and only one of them —
`messageSchema`, the payload the api BUILDS — is the one that must carry a state; the other
three are request doors that must refuse one. See [data-model §2](./data-model.md).

## Technical Context

**Language/Version**: TypeScript on Node.js 22.23.2, one language across services (constitution
VII, ADR-01)

**Primary Dependencies**: **none added.** The work is zod schemas in `@relay/protocol`, an
existing Redis publish path in the api, and an existing subscriber route in the gateway

**Storage**: PostgreSQL — read only. No migration, no column, no constraint. Redis carries the
fabric

**Testing**: vitest — unit (`*.test.ts`), integration (`*.itest.ts`), the sealed outsider suite,
and the isolation gauntlet that gates releases under constitution VI

**Target Platform**: Linux containers; the composed stack plus the media worker (4.13's fifth
service)

**Project Type**: multi-service TypeScript monorepo with a published tutorial chain

**Performance Goals**: no new per-channel subscription — per-channel SUBSCRIBEs stay at **5**
against ADR-25's bound of **6**; projected subjects unchanged at `5 × channels + 1 × connected
users`

**Constraints**: the delivery schema must stay permissive for durable envelopes written by an
older binary (FR-018d); the fan-out must use the delivery gate's own query, not a second one;
the frame must not carry a rejection reason

**Scale/Scope**: measured on the development lane — 5,403 media objects (4,725 unreferenced,
1,589 referenced), channels-per-object 1 → 1,545 and 2 → 44, 1,051 referenced objects still
`pending`

## Constitution Check

*GATE: evaluated before Phase 0, re-evaluated after Phase 1. Both recorded.*

| Principle | Verdict | Evidence |
|---|---|---|
| **I. Tenant isolation** | **PASS, and pass 3 found the work it costs** | The fan-out reuses `channelsReferencingMedia`'s query body and its `environment_id` predicate — no second place to forget it. **But the verdict seam has no tenant**: `recordMediaVerdict` is module-level on a raw `Db` and returns no `environment_id`, and the worker's principal carries none by design. The environment is carried out of the `RETURNING` list (T030) rather than the predicate being dropped, which is the version of this that would have violated the principle. The gauntlet gains an attack for the new frame. |
| **II. No acknowledged message lost** | **N/A** | No message is acknowledged on this path. The frame is an optimisation over a floor that does not depend on it (FR-009). |
| **III. Two data paths, never crossed** | **PASS** | Operational only. Nothing analytical is written — `media_events` stays deferred to the erasure chapter (`gaps.md` 059-11), because its sum reads `deleted`, which has no producer until FR-MED-10. |
| **IV. Single writer, single source of truth** | **PASS, and it is the reason for FR-002.** | The state has exactly one home, `media_objects.state`. Storing it on `messages.attachments` would make two sources of truth for one fact and turn every verdict into a write across every referencing message. |
| **V. API-first** | **PASS, and the evidence was wrong at first** | Additive on the wire: a new key on a payload clients already parse, plus one new frame. **Pass 1 corrected the scope** — this is not "one optional field on a delivery shape" but a required field on a **new** shape that `messageSchema` points at, and `messageSchema` is the contract published since chapter 1.3. The clause still passes; the plan's "smaller change" framing did not. |
| **VI. Requirement-driven, test-verified** | **PASS with a named risk** | Every task traces to FR-MED-07, FR-MED-08 or FR-MED-09. **The risk**: 100% branch coverage is required for tenant isolation, and 4.12 measured that this chapter's kind of predicate carries **no JavaScript branch at all** — deleting the scope turned nothing red. The per-arm probe (below) is the instrument, not the coverage number. |
| **VII. Boring by design** | **PASS, and it is the chapter's central decision** | No new service, no new dependency, **no sixth subject grammar**. ADR-25's threshold is preserved rather than spent. An ADR records the choice with the arithmetic. |

**Gate result: PASS. No violations, so Complexity Tracking is empty and omitted.**

### Post-Phase-1 re-evaluation

Re-run after the contracts were written. **Unchanged, with one thing that moved:**

The pre-Phase-0 reading assumed a sixth subject grammar and would have needed VII justified as
*permitted but at the bound*. Research overturned it. **Adding an arm to an existing fabric is a
smaller claim against VII than taking a new subject**, so the gate got easier rather than
harder — which is worth recording, because the plan's constitution check is exactly the artifact
057 found a CRITICAL in twice, filled once and read past five times.

## Project Structure

### Documentation (this feature)

```text
specs/060-chapter-4-14/
├── spec.md                      # /speckit-specify output
├── plan.md                      # this file
├── research.md                  # Phase 0 — R1…R8, all decisions measured
├── data-model.md                # Phase 1 — what is read; the one shape added
├── quickstart.md                # Phase 1 — validation guide
├── contracts/
│   └── media-state.md           # Phase 1 — three surfaces
├── checklists/
│   └── requirements.md          # spec quality, 16 of 16
└── tasks.md                     # /speckit-tasks — NOT created here
```

### Source (relay-platform)

```text
packages/protocol/src/
├── attachments.ts               # NEW deliveredAttachmentSchema, state required
├── frames.ts                    # messageSchema points at it; the new client frame
└── revision.ts                  # third arm, kind: "media"

services/api/src/
├── db/repository.ts             # verdict returns environment_id; scoped fan-out entry point
├── fanout/publisher.ts          # publishRevision learns a third arm (pass 4)
├── internal/media.controller.ts # publish on `applied`, the verdict seam
├── internal/internal.module.ts  # MESSAGE_PUBLISHER provider — pass 4's CRITICAL
└── messages/, backfill, resume  # the doors that serve a message, derived not listed

services/gateway/src/
├── fanout.ts                    # routing + the gateway's OWN publisher (pass 5)
└── session.ts                   # the two-way ternary becomes a switch

relay-tutorial/
├── app/(en)/part-4/chapter-14/… # the chapter
└── fences/post-series.md        # amended only if a hunk cannot anchor at this chapter
```

**THE FENCE EXPOSURE IS THE LARGEST SINGLE COST AND PASS 1 FOUND IT UNDERSTATED.**
`frames.ts` and `attachments.ts` carry titled fences in **six English chapters** — 1.3, 3.15,
3.17, 3.18, 3.22 and 4.11 — and **four Vietnamese**. Touching `messageSchema` is a chain event
across the series, not a one-file edit, and the chapter's own hunks compete with
`fences/post-series.md`, which applies after every chapter. Budget for it at T061–T065 rather
than discovering it at the close, which is what 050, 056 and 058 each did.

**Structure Decision**: the existing monorepo. The protocol package is where the request doors and the delivered shape meet,
which is the argument `attachments.ts` already makes for living there — *"two schemas that
happen to agree are the defect this chapter is trying not to repeat."*

## What Phase 0 changed about the plan

Recorded because a research phase that only confirms the spec is one nobody should trust.

**The spec's working answer to §7.4 was wrong.** It assumed a sixth grammar, `media:{channel_id}`,
and said research must confirm it or record why the rule points elsewhere. **The rule points
elsewhere**: `fanout.ts` already subscribes `chan:` and `revision:` together under one reference
count as *"co-extensive by construction"*, so a third arm on the revision fabric costs zero
subscriptions where a sixth grammar costs one per channel and lands exactly on ADR-25's ceiling.

**And the cheapest option died on a missing field.** Re-sending the message as `message.updated`
needs no new anything — but `messageSchema` has no `edited_at`, so a client could not tell an
attachment resolving from an author editing. That is ADR-24's own objection to putting edits on
`chan:`, one level up.

**Two findings that remove work rather than add it.** FR-011 needs no code: 2,867 tombstoned
messages carry **zero** attachments, because FR-MED-10's unlink already empties the array, so a
tombstone cannot match the containment predicate. And FR-007 holds by construction: real-time
delivery reaches subscribers, which is a **subset** of those authorised to read, so the event can
under-deliver but never over-deliver.

## What analysis pass 2 changed

Pass 2 ran pass 1's repairs rather than re-reading them. **All three of pass 1's claims hold** —
a delivered attachment already parses through the forwarding union's loose arm and the field
survives, the strict request shape refuses it with `Unrecognized key: "state"`, and a durable
envelope with no state still parses. The outbox was never at risk: `outbox/event.ts` already
reads attachments permissively, with its own comment recording the `message.term()` failure that
taught it.

**What pass 1 got wrong was the door count, not the schema.** It corrected the shape and
inherited FR-003's list of three, while the code holds at least six construction sites — history,
the send response, **the edit response**, live delivery, **resume/backfill**, and the gateway's
socket ack. FR-003 forbade hand lists and contained one. The list is gone; the derivation is the
definition.

**And two different things are typed `Attachment[]`.** The jsonb column cast holds what the
sender declared and must stay; the constructed Message is what changes. Conflating them would
make the column's type a false claim about stored bytes.

## Phase 2 approach (for `/speckit-tasks`, not executed here)

Ordering is forced by one dependency and one habit.

**The dependency**: the state on the attachment (story 1) is independently shippable and the
event is not — the event's tests assert a state the delivery schema must already carry. Story 1
first, in full, including the door derivation.

**The habit, which this project has paid for seven times**: the set of doors that serve a message
is **derived from the code, not listed**. Every hand-written list of fenced files, routes or
validators in this project's history has been wrong in both directions. The derivation is a task,
and its output is checked against the tests in both directions (SC-002).

**The per-arm probe is a task, not a coverage number.** 4.12 measured that deleting a tenancy
predicate here turns nothing red, because an SQL clause carries no JavaScript branch. Each arm —
the scope, the `applied` check, the empty-list path, the per-channel loop — is deleted
individually and the suites re-run, and any arm whose deletion turns nothing red is either
untested or unnecessary, said out loud either way.

**The fence bill is counted at the end, not estimated at the start.** 050, 056 and 058 each
found the task table's file list short, every time because repairs made *after* the list was
written added to it.

## Open questions carried into tasks

1. **Where the publish sits relative to the verdict.** **Pass 3 removed the option this question
   originally posed** — there is no transaction. `recordMediaVerdict` is an `UPDATE … RETURNING`
   plus a follow-up `SELECT`, and the controller manages no transaction of its own. What is left
   is narrower: publish after `applied === true` and accept that a crash between the UPDATE and
   the PUBLISH loses one frame, which FR-009's floor repairs on the client's next read. An outbox
   row is available and is almost certainly over-building. **And for a `rejected` verdict there is
   a second ordering question**: the handler `await`s `deleteObject`, so a publish after it adds a
   store round trip to the worker's request and a publish before it announces `rejected` while the
   bytes still exist.
2. **Whether the api runs one Redis publisher or two.** Pass 4's fix gives `InternalModule` its
   own `MESSAGE_PUBLISHER`, which is a second client in one process needing its own
   `OnModuleDestroy`. `ANALYTICS_PUBLISHER` set the precedent for a second client and argued it;
   sharing one instead means exporting a token `MessagesModule` deliberately withholds. Neither
   is free and the decision belongs in the record.
3. **How the scoped query is reached, now that the environment has to travel.** A module-level
   entry point taking `(db, environmentId, mediaId)` beside `recordMediaVerdict`, reusing
   `channelsReferencingMedia`'s body — one query, one predicate, two callers. The alternative that
   is **not** available is an unscoped lookup by primary key.
4. **The frame name.** `media.updated` matches FR-MED-07's wording. It is one letter from
   `message.updated` in a codebase where both will appear in the same `switch`.
