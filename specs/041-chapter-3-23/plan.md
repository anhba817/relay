# Implementation Plan: Chapter 3.23 — editing and deleting a message

**Branch**: `041-chapter-3-23` | **Date**: 2026-09-03 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/041-chapter-3-23/spec.md`

## Summary

FR-RTM-05's last two event kinds get producers. An author may change a message's text; the
author or a tenant API key may delete one, leaving a tombstone that keeps its place.

**Four surfaces move, and the first draft of this paragraph counted three.** **Three** REST
routes — edit, delete, and a moderation read of a message's edit history; two real-time
frames; two webhook event types FR-WHK-02 has named since the first draft; and **the fan-out
fabric**, which carries a `Message` and stamps every arrival `message.created`, so neither new
kind can reach a socket on the subject that exists (research R13). A new error code goes with
them — `not_message_author`, because authorship is a fact about the message and the generic
403's published remedy is a change of credential or permission, which nobody can act on (R16).

**This paragraph has now been wrong twice in the same way.** It said three surfaces before the
fabric was found, and two REST routes until the edit-history read was — each time because it
was written once and the work grew underneath it. The count above is derived from
`contracts/edit-and-delete.md`, which is the document that has to be right.

**This chapter implements a design the documents already hold.** `docs/05-sad.md` publishes
both the deletion's shape and the `message_edits` DDL; `schema.ts` names that table as an
absence awaiting *"the edit chapter"*. The one schema this chapter argues with is its own —
`message.deleted` stops carrying a message payload it cannot fill.

## Technical Context

**Language/Version**: TypeScript 5.x on Node 22, ESM throughout

**Primary Dependencies**: NestJS (api), drizzle-orm + drizzle-kit (schema and migrations),
zod (protocol schemas), `ws` (gateway), ioredis (fabric), NATS JetStream (event spine)

**Storage**: PostgreSQL — `messages` (**three** existing columns nothing writes today:
`edited_at`, `deleted_at`, and `metadata`, which carries the deletion's actor and has no
writer anywhere in the platform), `message_edits` (new), `outbox` (two new event types)

**Testing**: vitest. Unit lane per package; integration lane at `--concurrency=1`; a coverage
lane with a per-file ratchet; `packages/outsider` against built Docker images

**Target Platform**: Linux, docker compose for the lane

**Project Type**: multi-service monorepo — api, gateway, dispatcher, shared packages

**Performance Goals**: the integration lane's mean stays inside its 240-second budget
(SC-010). **None of the three routes is on a hot path**: the edit and the deletion are
single-row writes in one transaction, and the edits read is one indexed read of an
append-only table that holds one row per edit

**Constraints**: no second language (Constitution VII); the api is the only writer to
Postgres (Constitution IV); `messageSchema` is published and must not change (R2)

**Scale/Scope**: 121,250 senderless rows in the lane. **Two of the three routes refuse
them** — FR-018 refuses an edit and a deletion on a row with no author to authorise against —
and the edits read does not, because reading what a message used to say needs no author.

**The three counts above are derived from `contracts/edit-and-delete.md` and `data-model.md`,
not maintained here.** This section said "neither route" and "two columns" for ten analysis
passes while the work grew: the plan's Summary, structure block and documentation list were
each re-derived when they went stale, and Technical Context sat between them untouched.

## Constitution Check

| Principle | Assessment |
|---|---|
| **I — Tenant isolation** | Both routes resolve the message through the channel's visibility predicate, so a message in another tenant is a 404 rather than a 403. FR-014. The same predicate the history route already uses, which chapter 3.15 corrected for exactly this. |
| **II — No acknowledged message lost** | Neither route deletes a row. A tombstone keeps its sequence number, author and timestamps; hard deletion stays with FR-MOD-04. |
| **III — Two data paths, never crossed** | Analytics is untouched. The webhook events go through the existing outbox and its consumer, which is the same path `message.created` takes. |
| **IV — Single writer** | Both writes are the api's. The gateway gains no write; it publishes and delivers. |
| **V — API-first** | Two routes on the existing message resource, documented before they are built (`contracts/`). |
| **VI — Requirement-driven** | FR-MSG-07, FR-MSG-08, FR-MSG-10, FR-MOD-02, FR-RTM-05 and FR-WHK-02, each traced. |
| **VII — Boring by design** | No new dependency, no new service, no second language. **One schema changes** and the record says why rather than assuming the reader agrees. |

**One ADR, and the plan's own detector is what found it.** The first draft of this section
said no ADR was expected, because the SAD prescribes both the deletion and the edit table —
and it wrote down that *if an ADR turned out to be necessary, something in this plan was
wrong*. Analysis pass 1 found that thing: the fan-out subject `chan:{channel_id}` carries a
`Message` and the gateway stamps every arrival `message.created`, so **a deletion cannot ride
it at all and an edit cannot be told apart from a creation on it** (research R13).

This repository's own rule, reached independently by three chapters, is that a kind which
cannot share a payload type cannot share a subject. So this chapter takes a **fifth subject
grammar** and owes **ADR-24** in both homes, exactly as ADR-19, -20 and -21 did. The
detector worked, and the sentence that carried it is kept above rather than quietly deleted.

## Project Structure

### Documentation (this feature)

    specs/041-chapter-3-23/
      spec.md
      plan.md                   this file
      research.md               the research log, each entry marked read or
                                measured — the count is not written here, because
                                it was wrong within one pass of being typed
      data-model.md             the two tables and the message's life
      contracts/
        edit-and-delete.md      the routes, the frames, the webhook events
      quickstart.md             P1–P5, and the lane's nine variables
      checklists/requirements.md
      gaps.md                   opened during analysis, 3 items with owners
      traceability.md           built in Phase 1, re-derived in Phase 12
      chapter-notes.md          the two counts and the word estimate
      check-refs.py sweep.py check-prose.py   per-chapter copies, by decision

### Source code

Derived from `tasks.md` rather than written beside it — the first version of this block was
composed before three analysis passes and omitted eight of the files the tasks touch.

    relay-platform/
      packages/protocol/src/
        frames.ts               message.deleted gets its own payload    CHANGED
        frames.test.ts          the `valid` fixture table at :30        CHANGED
        codes.ts                not_message_author                      CHANGED
        codes.test.ts           the exact set and the count             CHANGED
        fanout.ts               the fifth subject grammar               CHANGED
        fanout.test.ts          its subject string and payload keys     CHANGED
      services/api/src/
        db/schema.ts            message_edits                           NEW TABLE
        db/migrations/          generated by drizzle-kit                NEW
        db/repository.ts        editMessage, deleteMessage,
                                listMessageEdits                        NEW METHODS
        db/repository.itest.ts  the writers, and R5's reader test        CHANGED
        messages/messages.controller.ts   PATCH, DELETE, GET :id/edits,
                                and a method-level @Accepts on two of
                                the three — the class declares both      CHANGED
        messages/messages.service.ts      edit and remove               CHANGED
        messages/messages.schema.ts       the edit body                 CHANGED
        messages/messages.itest.ts        both routes end to end        CHANGED
        fanout/publisher.ts     publish a mutation, not only a message  CHANGED
        outbox/event.ts         two more OUTBOX_EVENT_TYPES             CHANGED
        outbox/event.test.ts    the exact set and the count             CHANGED
        webhooks/deliveries.itest.ts      an edit and a deletion        CHANGED
        isolation/targets.ts    three declared targets — the derived
                                list goes red on the build that adds
                                a route                                  CHANGED
      services/gateway/src/
        session.ts              deliver both kinds, stamped by the
                                payload rather than by the call site    CHANGED
        session.test.ts         the six-producers check                 CHANGED
        session.itest.ts        the two delivery tests                  CHANGED
        fanout.ts               subscribe to the new subject            CHANGED
        resume.itest.ts         the cursor's blind side, and its own
                                environment and user first              CHANGED
      packages/outsider/src/
        integrate.itest.ts      an edit and a delete against the images  CHANGED
      vitest.coverage.config.mts  the new production paths pinned        CHANGED

    docs/
      04-srs.md               the revision row; no clause changes       CHANGED
      05-sad.md               ADR-24, and §6.1's message_edits as built  CHANGED
      06-adr-deep-dives.md    the ADR-24 deep dive, and the count       CHANGED
      07-tutorial-plan.md     the chapter row (NOT published by
                              sync-docs.sh — its own comment says why)   CHANGED
      08-error-reference.md   not_message_author                        CHANGED

    relay-tutorial/
      app/(en)/part-3/chapter-23/<slug>/page.mdx, figures.ts             NEW
      app/(vi)/vi/part-3/chapter-23/<slug>/page.mdx, figures.ts          NEW
      lib/tutorial.ts         the registry entry                        CHANGED
      fences/post-series.md   only if a file's chain lives there         MAYBE

**Structure Decision**: no new package, no new service. The one new table is the SAD's, the
two new routes sit on the resource that already has send and history, and the two new event
types join an array that already exists to be counted.

**The question mark that used to be on `fanout.ts` has an answer, and it cost a phase.** The
first draft asked whether the two kinds could ride `chan:{channel_id}` and left it for the
tasks phase to settle with a `grep`. The grep says no, for two different reasons, and the
measured typed points are in research R13 — 15 lines across four files, to be re-counted when
the phase runs rather than carried from here.

## Phases

Twelve, and `tasks.md` lists the same twelve. Chapter 3.21 left its plan saying something
else and made a reader hold the correction in their head. **The first draft had eleven**;
analysis pass 1 added the fabric.

**Phase 1 — the premise, before any writer.** Research R5's test: a hand-planted tombstone read
back through the REST history route, asserting the position survives with a null text. **If
it is red the spec's resume decision is wrong and the plan changes rather than the code.**
Chapter 3.15 wrote the same test for the listing and said why; history never got one. The
phase also builds `traceability.md` both ways, which is where chapter 3.22 found two orphans
before a line of code existed.

**Phase 2 — the protocol.** `message.deleted` gets its own payload. `frames.test.ts`'s per-kind
table is a pinned place: predict how many, then re-measure.

**Phase 3 — the fabric, and the fifth subject grammar.** `chan:{channel_id}` carries a `Message`
and cannot carry a deletion; the gateway stamps arrivals `message.created` at the call site,
so an edit is indistinguishable from a creation on it. A new grammar, **ADR-24 in both
homes**, and the typed points re-counted rather than carried (research R13). **This blocks
both US1 and US2** — neither frame reaches a socket without it.

**Phase 4 — the table.** `message_edits` from the SAD's DDL, generated by drizzle-kit and reviewed
against §6.1 before it is applied. A phase that adds raw SQL runs the suite that executes it.

**Phase 5 — US1, the edit.** Repository, service, route, frame. Author only. 🎯 **MVP.**

**Phase 6 — US2, the deletion.** The tombstone the SAD published, the idempotent second delete, the
refusal to edit one, and history keeping the position.

**Phase 7 — US3, moderation.** A tenant API key deletes anything and edits nothing.

**Phase 8 — US4, the resume bound, demonstrated.** An edit above the cursor arrives; one below it
produces no frame **and no sequence gap**; history repairs it. The test is the documentation
for the one soft edge in the contract — and the phase corrects `backfill.controller.ts:83`,
whose comment promises a resume behaviour this chapter decided against.

**Phase 9 — the webhook events.** Two more `OUTBOX_EVENT_TYPES`; four pinned places predicted.

**Phase 10 — the documents.** The SRS revision row, the SAD's §6.1, the chapter table in
`docs/07-tutorial-plan.md` — which `sync-docs.sh` does **not** publish — and `sync:docs`,
which no task in chapter 3.22 named and `check:docs` caught.

**Phase 11 — the chapter**, its figures, its fences, both locales, and the registry.

**Phase 12 — close-out.** Titles against assertions; the coverage ratchet, where the question is
whether an uncovered arm should be deleted rather than tested; traceability re-derived against
the shipped tree; the battery; gates last, exit codes captured into variables.

## Complexity Tracking

| Thing | Why it is not simpler |
|---|---|
| A second payload shape for `message.deleted` | The alternative widens `messageSchema.text` to nullable, which makes `text: null` legal on a creation — where the send path deliberately refuses it — and edits a contract published since chapter 1.3. |
| A new table rather than a column | FR-MSG-07 asks for an immutable history with timestamps; a column holds one prior text, and the SAD already published the table. |
| Two webhook event types in the same chapter | FR-WHK-02 names them, and chapter 3.20 set the precedent by emitting the webhooks for the events it created rather than leaving them to a later chapter. |
| A test written before the writer it protects | R5. The repair path the resume decision depends on has never been exercised; a test written after the writer proves the writer, and this one has to prove the reader was already right. |
