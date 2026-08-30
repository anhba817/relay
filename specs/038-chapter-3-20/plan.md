# Implementation Plan: chapter 3.20 — the membership that changed under a live socket

**Branch**: `038-chapter-3-20` | **Date**: 2026-08-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/038-chapter-3-20/spec.md`

## Summary

Two P1 clauses are unmet and they are one mechanism. FR-RTM-10 gives a five-second budget for
events to stop reaching a client whose membership no longer grants access; FR-RTM-05 names
membership change among six real-time event kinds and it is the third to get a producer.
The gateway learns memberships once, at connect, and nothing between connect and close re-reads
anything — so producing the event is the same act as satisfying the clause.

**The design has four parts, and two of them come from the constitution rather than from the
spec.**

1. **A third subject grammar, addressed two ways** (research R1). A removal can ride
   `member:{channel_id}` and reach both audiences at once; an addition cannot, because the
   instance holding the new member is not subscribed to that channel yet. `member:{env}:{user}`
   is the only way to reach a principal, and this is the first event in the system that needs to.
2. **An outbox row inside the membership transaction** (research R2), **which has to be created
   first**: none of `addMember`, `removeMembers` or `banUser` has one. Two of them are already
   multi-statement — `removeMembers` deletes members and then read positions with nothing between,
   so the transaction closes a pre-existing crash window as well as carrying the row. **And the
   event's `data.user` is an external id these methods do not hold**, so the caller passes it down
   the way `sendMessage` is handed `userExternalId`; building the event outside the transaction
   instead is the violation itself. Constitution II forbids publish-after-commit without the
   outbox. Chapter 3.18's Redis publish is legal because the
   same transaction wrote the durable event; a membership write records nothing, so a Redis
   publish beside it would be exactly the case II names. FR-WHK-02 already spells the two event
   types this owes — `channel.member_added` and `channel.member_removed` — so the row is a
   requirement being met, not a principle being appeased.
3. **A backstop for the lossy path** (research R3). Constitution IV permits an at-most-once
   fabric *"precisely because durability and resume live in PostgreSQL sequences and cursors"*
   and requires that any new delivery mechanism preserve that recovery property. A message
   recovers through the resume cursor. **A revocation has no cursor.** The re-read that fixes
   that has a contract waiting for it: `internalMembershipsResponseSchema`, exported since
   chapter 3.2 and parsed by nothing.
4. **A filter on the resume buffer** (FR-029, added in analysis pass 3). The resume path is a
   second delivery route and nothing in the membership design can see it: `flushable(buffer,
   marks)` at `session.ts:632` filters on `frame.seq` and not on membership, so a removal landing
   mid-resume unsubscribes the channel and the already-buffered messages flush afterwards.
   **FR-RTM-10 violated by a flush rather than by a subscription** — and every other test this
   feature writes passes against it, because the membership path did its job correctly. **The
   notice needs the mirror of that** (FR-030): it reads neither `phase` nor `marks`, or it joins
   the buffer it was announcing the filtering of. Chapter 3.19 needed both halves for presence and
   wrote both; this plan had one until analysis pass 7.

## Technical Context

**Language/Version**: TypeScript 5.x, Node.js 22 (ADR-01), ESM throughout
**Primary Dependencies**: `ioredis` (fan-out, restricted import), `zod` (protocol schemas),
NestJS in the api only (ADR-15), Drizzle inside the repository layer only (ADR-16), `ws` in the
gateway
**Storage**: PostgreSQL for the membership rows and the outbox; Redis pub/sub for the live path;
no new store
**Testing**: vitest — unit for pure logic, `*.itest.ts` for anything touching Redis or the api
**Target Platform**: Linux containers, `docker compose` locally on the ports `baseline.txt` pins
**Project Type**: existing pnpm/Turborepo monorepo — `relay-platform` (services + packages),
`relay-tutorial` (the published chapters and the five `check:*` gates), `docs/` (the governing
documents), `specs/` (this record)
**Performance Goals**: the revocation inside FR-RTM-10's five seconds; the full integration lane
inside its 240 s budget. Chapter 3.19 left 11.8 s of headroom at the mean — but the gateway
package's clock is `max(file)`, not the sum: 28 cores against 8 files, so a ninth file **under**
`presence.itest.ts`'s 45 s costs the lane almost nothing. What it costs is contention
**Constraints**: the gateway holds no database (ADR-05); nothing in Redis is a source of truth
(constitution IV); `ioredis` is a lint-restricted import; ADRs are immutable once accepted
**Scale/Scope**: NFR-SCL-01's 10,000 connections per instance is the budget the backstop's
interval is priced against — and it is a budget, never a measurement (SAD risk R2)

**NEEDS CLARIFICATION**: none remain. The spec's two open decisions were put to the author before
it was written (scope, and who is told); FR-014's fabric question and FR-017's dead-contract
question are answered in research R3 and R4 and are recorded there as decisions with their
rejected alternatives.

## Constitution Check

*GATE: evaluated before Phase 0 and re-evaluated after Phase 1.*

| Principle | Bearing | Verdict |
|---|---|---|
| **I — Tenant isolation** | Membership decides who may hear what. The publish carries an environment id (FR-007) so a gateway can refuse a change that does not belong to the connection it would act on; keys and subjects are composed from the authenticated connection's own identity, never from a payload. | **PASS**, and it makes both new files tenant-isolation code, which is why FR-027 pins 100% branches (NFR-MNT-02). |
| **II — No acknowledged message lost** | *"Publish-after-commit without the outbox is forbidden."* A membership write records nothing today, so the Redis publish this chapter wants would be an event with no durable record. | **PASS ONLY WITH R2's OUTBOX ROW.** Without it this design is a violation, and that is the finding that changed its shape. |
| **III — Two data paths** | Nothing analytical here. No ClickHouse write, no metering. | **PASS**, vacuously. |
| **IV — Single writer, single source of truth** | The api remains the only writer. Redis holds nothing durable. **But**: *"Any new delivery mechanism MUST preserve this recovery property."* A revocation has no resume cursor. | **PASS ONLY WITH R3's BACKSTOP**, and the backstop's interval is a measured number the chapter must publish, not a default. |
| **V — API-first** | No public route changes. The failure path emits a structured event with a stable name (FR-015), which is what makes the requirement checkable. | **PASS**. |
| **VI — Requirement-driven** | Four clauses cited, none amended (research R10). Coverage pinned at 100/100/100/100 for the new production files. | **PASS**. |
| **VII — Boring by design** | A third subject grammar, and no new service. The rejected alternative — a JetStream consumer in the gateway — is rejected on ADR-07's *"clean mapping"* and on this principle. | **PASS with a Complexity Tracking entry.** |

**Post-Phase-1 re-evaluation**: unchanged. The two conditional passes are conditional on work the
plan schedules in Phase 2 and Phase 3, and the phase order below puts the outbox row before the
publish for exactly that reason — a phase that ships the publish first would ship a constitutional
violation and then fix it.

## Project Structure

### Documentation (this feature)

```
specs/038-chapter-3-20/
├── spec.md
├── plan.md              # this file
├── research.md          # R1–R10
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── membership-fabric.md      # the subjects, the payloads, who subscribes to what
│   └── membership-lifecycle.md   # write -> outbox -> publish -> act, and the ordering
├── checklists/requirements.md
├── baseline.txt         # the running record of every measurement and every thing that went wrong
├── gaps.md              # written when found, not at close-out
├── traceability.md      # both directions, before any test is written
└── chapter-notes.md
```

### Source code

```
relay-platform/
├── packages/protocol/src/
│   ├── membership.ts             # NEW — the two subject shapes and the fabric payload
│   ├── membership.test.ts        # NEW
│   ├── internal.ts               # internalMembershipsResponseSchema revived (R4)
│   └── index.ts                  # + one export line
├── services/api/src/
│   ├── outbox/event.ts           # `type` widens from a literal to a union (R2)
│   ├── db/repository.ts          # three writes gain a TRANSACTION and an outbox row
│   ├── channels/channels.controller.ts  # publishes after commit — the CONTROLLER,
│   │                                    #   where messages.controller.ts:199 does
│   ├── users/users.controller.ts # the ban path, same layer
│   ├── internal/                 # GET /internal/memberships, revived for the backstop
│   └── membership/               # NEW — the publisher, shaped like fanout/publisher.ts
└── services/gateway/src/
    ├── membership.ts             # NEW — the subscriber, the act, the backstop timer
    ├── membership.test.ts        # NEW — pure logic only
    ├── membership.itest.ts       # NEW — shares the api fixture rather than spawning a 7th (R9)
    ├── session.ts                # the first mutation of connection.channelIds after connect
    ├── session.itest.ts          # the FR-RTM-10 test INVERTS (FR-021)
    └── main.ts                   # the sixth and seventh Redis clients

relay-tutorial/
├── app/(en)/part-3/chapter-20/<slug>/page.mdx    # NEW
├── app/(vi)/vi/part-3/chapter-20/<slug>/page.mdx # NEW
├── fences/post-series.md         # if eslint.config.mjs or the coverage config move again
└── lib/tutorial.ts               # + the 3.20 entry, all three Vietnamese fields
```

**Structure Decision**: the existing monorepo. One new module in the protocol package, one in the
gateway, one in the api. The gateway module follows the shape `fanout.ts`, `limits.ts`, `meter.ts`
and `presence.ts` share — a factory returning an interface, injected into `attachSessions` as an
optional field so chapter 2.5's tests and a single-process dev run still work without Redis.

**`fanout.ts` and `presence.ts` are not edited.** Each fabric owns its subject grammar in its own
file; `internal.ts` established that and chapter 3.19 followed it. A new file is a whole-file fence
and leaves two chapters' hunks alone.

## Implementation phases

**Phase 1 — the failing state, observed.** The FR-RTM-10 test at `session.itest.ts:677` already
asserts the violation; run it and record *which* red it produces. Stand up the two-instance harness
and the shared api fixture. Pin the lane environment in `baseline.txt` before anything is measured.

**Phase 2 — the durable record, first.** The outbox rows for `channel.member_added` and
`channel.member_removed`, written inside the membership transactions, with the envelope's `type`
widened from a literal to a union. **This phase ships before any publish exists**, because the
reverse order ships a constitutional violation and then repairs it. A phase that adds raw SQL must
run the suite that executes it.

**Phase 3 — the fabric.** `packages/protocol/src/membership.ts`, the api-side publisher beside the
outbox row, and the gateway-side subscriber. Measure the subscription count with
`CONFIG RESETSTAT` and `INFO commandstats` and record it; the prediction is 18 for two instances
over three channels plus one per connected user, and a prediction is not a measurement.

**Phase 4 — US1, the removal.** The frame before the cut-off, both audiences, the reference count
that must decrement rather than unsubscribe. **The test that carries this phase is the one that
asserts a second local member of the same channel still receives** — the obvious test passes
against an implementation that unsubscribes the channel outright.

**Phase 5 — US2, the other members.** The frame delivered to the channel's remaining members by
the same publish US1 already makes, the dedup that gives a watcher sharing three channels one
frame, and the must-not-receive cases asserted in a run where a member does receive.

**Phase 6 — US3, the addition.** The user-addressed subject, the subscribe, and chapter 3.19's
presence staleness closing as a consequence rather than as separate work.

**Phase 7 — US4, the ban.** One publish per user rather than one per channel, and a decision about
what an unban does that `POST /internal/session` already half-answers.

*The failure paths — the fabric down, the log line that is the requirement's evidence — live in
Phase 8 with the backstop, because they are the same subject: what happens when a publish does not
arrive. A publisher that does nothing satisfies "the socket still opened" exactly as well as a
working one.*

**Phase 8 — the backstop.** The revived `/internal/memberships`, its re-read timer, the fixture in
`signup.itest.ts` read **before** the route exists rather than after, and the interval chosen with
its arithmetic written down beside it.

**Phase 9 — the documents.** Whatever the architecture record needs, `docs/07-tutorial-plan.md`'s
3.20 row **and** its stale Part 3 header, then `pnpm sync:docs` and `pnpm check:docs`.

**Phase 10 — the chapter**, both locales, the fences, and the published prose R8 lists.

**Phase 11 — close-out.** Coverage pins, the battery, `gaps.md`, `traceability.md` re-derived from
the shipped tree, and the tag.

*`tasks.md` splits US2 and US4 into phases of their own, so it runs eleven where this list first
ran ten. The order is unchanged.*

**Commit each phase.** `git checkout` on a file with uncommitted work destroyed it twice in 3.12.

## Complexity Tracking

| Addition | Why it is needed | Simpler alternative rejected because |
|---|---|---|
| **A third subject grammar** | An addition cannot be addressed by any subject derived from the channel, because the receiving instance is not subscribed to it yet (R1). | Reusing `presence:{channel_id}` means widening a `strictObject` chapter 3.19 made strict on purpose, so a field added on one side of a rolling deploy fails loudly on the other. |
| **Two subject shapes under it** | The two audiences are addressed differently: the channel's members by channel, the affected user by principal. | Publishing to every remaining member's user-subject replaces one publish with one per member — 1,000 of them at FR-CHN-07's ceiling. |
| **Sixth and seventh Redis clients** | A connection in subscriber mode cannot run ordinary commands; chapter 3.8 gave this reason for the limiter's and 3.19 for presence's. | Sharing presence's clients couples two modules' lifecycles and their close paths. |
| **Outbox rows for two new event types** | Constitution II, and FR-WHK-02 already names both. | Publishing to Redis alone is the violation; not publishing at all leaves FR-RTM-10 unmet. |
| **A re-read timer in the gateway** | Constitution IV's recovery property, which a revocation has no cursor for (R3). | A JetStream consumer in the gateway is at-least-once and free of a timer, and it breaks ADR-07's *"clean mapping"* and constitution VII. |
| **The re-read period on the factory's options** | Its production value is sixty seconds and the gateway test package's whole wall clock is forty-five, so the requirement's only test cannot run without an injectable one. | A fixed constant makes FR-014a — the requirement discharging constitution IV's conditional pass — unverifiable, which is worse than the option. |
| **Mutating `connection.channelIds` mid-connection** | There is no other way to meet FR-RTM-10 in a gateway with no database. | Closing the socket and letting the client reconnect is a revocation the user can see and the clause does not ask for; close code 4009 exists and this is not it. |
| **Filtering the resume buffer on a removal** | `flushable(buffer, marks)` filters on sequence alone, so a removal mid-resume unsubscribes the channel and then flushes its buffered messages anyway (FR-029). | Leaving the buffer alone means FR-RTM-10 is violated by a flush rather than by a subscription, which every other test in this feature would pass. |
| **A transaction around three untransacted writes** | Constitution II. None of the three has one, and two are already multi-statement. | Writing the outbox row beside the statement is the violation itself, and it passes every test except the one that fails the write on purpose. |
| **External ids passed into the repository** | The event's `data.user` is what a customer reads, and these methods hold only `users.id`. | Looking the external id up inside the repository is a second query per member on a bulk path; the service already has the map. |
| **A provider, a token and a lifecycle for one publisher** | A factory is not injectable, and an unclosed Redis client hangs the api suites. | Registering the factory in both modules opens two connections for one job. |
| **A seventh api process in the gateway test package** | The new integration file needs an api and no cross-file fixture exists to share. | Building that fixture is chapter 3.19's `gaps.md` item 17's actual fix and a job of its own; putting these tests in `session.itest.ts` avoids the spawn and puts the chapter's headline tests in a file no chapter fences. |

## What this plan deliberately does not do

- **FR-RTM-08 (typing)** stays unbuilt, named in FR-018. It can genuinely reuse the fan-out, which
  is what makes it the contrast case and a chapter of its own.
- **FR-RTM-09's five-connection cap** stays unbuilt, named in FR-019, because it needs a
  `conn:{env}:{user}` registry that chapter 3.19's `gaps.md` item 6 records as mis-specified.
- **FR-WHK-02 is not claimed met.** Two of its eight names gain producers; five are still missing
  and no endpoint subscribes to the new types.
- **NFR-SCL-01 stays undischarged.** The backstop's interval is priced against its 10,000-connection
  budget and nothing here measures at that scale — the lane's largest membership set is five
  channels and its largest instance count is two.
