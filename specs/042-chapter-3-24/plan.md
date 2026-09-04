# Implementation Plan: Chapter 3.24 — the message that is not only text

**Branch**: `042-chapter-3-24` · **Date**: 2026-09-04 · **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/042-chapter-3-24/spec.md`

## Summary

FR-MSG-11's P2 half: up to ten attachments on a message, each an external URL with a declared
kind. `messages.attachments` has been a column since chapter 2.1 with **one writer that sets
it to null** — chapter 3.23's deletion, following SAD §342. Nothing has ever put a value in
it, no route returns it, no frame carries it.

**The work is one field following `text` through every door a message has**, and the doors
were counted rather than guessed: four writers, six read shapes, three event types. What
makes it more than plumbing is three decisions the tree forces:

- **The wire frame is a `strictObject`**, so adding a field is a protocol change that every
  consumer sees. Chapter 3.23 refused to widen `messageSchema.text` and took a fifth subject
  grammar instead; this chapter widens the same object, and the difference between the two
  cases has to be argued rather than assumed.
- **`z.url()` accepts `javascript:`** — measured against the repository's own zod 4.4.3, not
  read from documentation. The scheme check is the whole of the protection.
- **The shape must leave room for §4.14's `media_id` arm** without a breaking change, which
  is the same rule chapter 3.23 reached for subjects, one level down.

## Technical Context

**Language/Version**: TypeScript 5.x, Node.js 22 (ADR-01, constitution VII)
**Primary Dependencies**: zod 4.4.3 at every boundary; drizzle-orm inside the repository layer
only; `ws` in the gateway; NestJS in the api
**Storage**: PostgreSQL — `messages.attachments jsonb`, existing, nullable, unwritten
**Testing**: vitest, two lanes (`test` Docker-free, `test:integration` against compose)
**Target Platform**: Linux containers
**Project Type**: monorepo — `packages/protocol`, `services/api`, `services/gateway`
**Performance Goals**: the integration lane stays under its 240 s budget; the send path takes
no new query
**Constraints**: no migration (the column exists); the tombstone predicate `text === null` is
chapter 3.23's and is not reopened; Relay never fetches an attachment URL
**Scale/Scope**: ten attachments per message, ~10 files, one new protocol shape

**Unknowns**: none. Both of the spec's clarifications were answered before planning, and
research resolved the rest against the tree — see [research.md](./research.md).

## Constitution Check

| Principle | Bearing on this chapter | Verdict |
|---|---|---|
| **I — Tenant isolation** | Attachments ride the message row; they carry no tenant of their own and are reached through `messages → channels → environment_id`, the hop this chapter's predecessor taught the tenancy catalogue to follow. Three routes gain a field, none gains a route. FR-014 says an attachment is unreadable by a caller who cannot read its message, which is the message's own predicate and not a second one. | **PASS** — no new surface, no new scope |
| **II — No acknowledged message lost** | Attachments are written in the same INSERT as the message, in the transaction that already exists. There is no second write to lose. | **PASS** |
| **III — Two data paths** | `attachment_count` on the analytical side is Part 4's and stays there. FR-017 asks only that the count be derivable, which an ordered list makes true by construction. NFR-SEC-06 and `recorder.ts:25` keep the URL out of the platform's own logs, for the reason they keep the text out. | **PASS** |
| **IV — Single writer** | One writer: `sendMessage`'s INSERT. The edit does not touch attachments (R9) and the deletion nulls them, which already exists. | **PASS** |
| **V — API-first** | A new field on published payloads, documented before it ships, with `docs/08-error-reference.md` gaining whatever refusal FR-003a needs. | **PASS** |
| **VI — Requirement-driven** | 24 requirements, six criteria, every one traced before implementation. The isolation suite attacks the three routes on every build already. | **PASS** |
| **VII — Boring by design** | No new service, no new dependency, no new language, no new table. The one decision that could need an ADR is whether widening `messageSchema` supersedes chapter 3.23's refusal to widen it — see below. | **PASS, with one ADR expected** |

**AN ADR IS EXPECTED AND THE PLAN SAYS SO IN ADVANCE.** Chapter 3.23's plan said no ADR was
expected and was wrong within one phase; its own early-warning sentence caught it. This plan
predicts one: **widening `messageSchema` with an attachments field**, against 3.23's ADR-24
which refused to widen the same object's `text`. If the argument turns out not to need a
record — because adding an optional field and loosening a required one's type are different
acts — then the plan was wrong here instead, and that is worth writing down either way.

## Project Structure

### Documentation (this feature)

```
specs/042-chapter-3-24/
├── spec.md              24 requirements, 6 criteria, 3 stories
├── plan.md              this file
├── research.md          R1-R10, every number taken from the tree
├── data-model.md        the attachment shape and where it lives
├── contracts/
│   └── attachments.md   the send body, the frame, the read paths
├── quickstart.md        the runnable validation
├── checklists/
│   └── requirements.md  16/16
├── traceability.md       generated in phase 1, both directions
├── gaps.md              carried forward and re-measured
└── baseline.txt         the lane environment, the counts, the findings
```

### Source code

```
relay-platform/
├── packages/protocol/src/
│   ├── frames.ts              messageSchema gains a field; messageSendSchema too
│   ├── attachments.ts         NEW — the shape, its bound, its scheme rule
│   ├── attachments.test.ts    NEW
│   └── internal.ts            internalSendRequestSchema AND internalSendResponseSchema
│                              — the second is strict and the gateway parses with it
├── services/api/src/
│   ├── messages/messages.schema.ts       the send body's array and its bound
│   ├── messages/messages.service.ts      threading, and the empty-text rule
│   ├── messages/messages.controller.ts   the response, and the published frame
│   ├── internal/internal.controller.ts   the socket's send — builds its call by NAME,
│   │                                     which the first analysis pass found
│   ├── internal/backfill.controller.ts   resume carries them
│   ├── outbox/event.ts                   MessageCreatedData, three event types
│   └── db/repository.ts                  the INSERT, and five read shapes
└── services/gateway/src/
    └── session.ts                        THREE changes, not none: the inbound
                                          destructure, the outbound builder, and
                                          the tests that see the socket door
```

**`services/gateway/src/session.ts` was listed with an expectation attached** — that the
gateway forwards a payload it does not construct, so a field added to `messageSchema` should
reach a socket without a line changing. **The first analysis pass checked it and the prediction
was wrong in both directions.**

    session.ts:1512   `const { channel, text, idem_key } = frame.data.payload`
                      a NAMED destructure, so a field added to the inbound frame is
                      parsed and dropped before it reaches the api
    session.ts:1534   the gateway BUILDS the outbound `message.created` payload field by
                      field after a socket send, so a field the api returns is absent from
                      the frame every member of that channel receives

Only the middle case holds: a `message.created` **arriving** from the fabric is forwarded
whole. The gateway is a producer on the socket-send path and a forwarder on the fan-out path,
and the plan had seen one of the two.

**Two more files move with it**, both found the same way. `internal.controller.ts:68` builds
its call by name, and `internalSendResponseSchema` is a `strictObject` the gateway **parses**
the api's reply with — so a field on `MessageRow` that reaches `{ ...message }` breaks every
socket send rather than going missing quietly. That one is latent today only because
`edited_at` is on the type and never on the value.

**The prediction is what made this cheap.** It named a file and said "verify, do not assume";
verifying took one `sed` at analysis time instead of a phase at implementation time.

## Phases

**Written as headings `sweep.py` can read, and that is not a formatting choice.** Chapter
3.23's plan listed its phases inside a code block; the sweep's extractor looks for
`**Phase N — …`, found nothing, and **the plan-against-tasks comparison never ran** — for
eight analysis passes, silently, while the sweep printed a green line about everything else.
That chapter found it at pass 8 and recorded that its verification pattern had been fitted to
its own output. This one is in the form the instrument reads, checked by running it.

**Phase 1 — Premises, instruments, and the reader test.** Blocks everything.

**Phase 2 — The shape.** `attachments.ts`, its bound, its scheme rule.

**Phase 3 — The wire.** `messageSchema`, the send frame, the internal hop. Blocks every route.

**Phase 4 — The writer.** The INSERT, and the empty-text rule.

**Phase 5 — User Story 1.** A message carries a picture somebody else is hosting. **MVP.**

**Phase 6 — User Story 2.** Ten is a limit and eleven is a refusal.

**Phase 7 — User Story 3.** The moderator, the tombstone, and what an edit leaves alone.

**Phase 8 — The read paths.** History, resume, the retry replay, and the four that do not change.

**Phase 9 — The events.** Three types, one shape.

**Phase 10 — The documents**, and the comment that schedules a P2 clause for Part 4.

**Phase 11 — The chapter.**

**Phase 12 — Close-out.** Gates last.

**Phase 1 carries a test that must pass against unchanged code.** Chapter 3.23 proved its
tombstone read path was already correct before any writer existed, and that test is what kept
a later phase from "fixing" something that worked. The equivalent here: **assert that a message with
`text = ""` is returned by every read path as a live message today**, with the row planted by
hand. If it fails, the empty-string decision is wrong and the plan changes before any code is
written.

**Phase 3 is the protocol change and it blocks everything downstream.** No route can return an
attachment the frame cannot express.

## Complexity Tracking

| Thing | Why it is not simpler | Rejected |
|---|---|---|
| A discriminated union for one arm | §4.14 adds a second arm with a different payload and a state the platform maintains. A single object with two optional fields cannot say "exactly one of these", and tightening it later is the breaking change FR-020 forbids. | One object, `url?` and `media_id?` |
| A new protocol module rather than a field in `frames.ts` | The tree's own practice, checked: `presence.ts`, `typing.ts`, `membership.ts` and `revision.ts` each own their shape. `fanout.ts` holds a subject function and nothing else. Chapter 3.23's task list named `fanout.ts` and was wrong for this reason. | Declaring the shape inline in `frames.ts` |
| An explicit scheme allowlist | `z.url()` accepts `javascript:`, `data:`, `file:` and `vbscript:` — measured, R7. The field's name promises less than a reader assumes, which is the same trap `avatar_url` is already in. | `z.url()` alone |
