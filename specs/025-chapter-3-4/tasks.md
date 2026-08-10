---

description: "Task list for chapter 3.4 — JetStream and the first consumer"
---

# Tasks: Tutorial Chapter 3.4 — JetStream and the First Consumer

**Input**: Design documents from `/specs/025-chapter-3-4/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/consumers.md, quickstart.md

**Tests**: Test tasks ARE included. The spec requires them (FR-019) and nine success criteria are worded "verified by an automated test".

**Organization**: Grouped by user story. As in 3.1, 3.2 and 3.3, the code story (US2) executes before the chapter story (US1).

> **Reconstruction note (2026-08-10).** This list is written after the fact. Task
> boundaries are inferred from the shipped chapter's structure and the code's
> commit-ready state, not from a plan that survived. Where a task's outcome is
> recorded elsewhere — a measurement in `research.md`, a defect in
> `chapter-notes.md` — the task points at it. **T009a and T034a did not exist at
> implementation time**; they are the reconstruction's own work, marked as such.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependency on incomplete work)
- **[Story]**: US1 = the chapter, US2 = the canonical code, US3 = publication

## Path Conventions

Paths are written from the repository root across three trees: `relay-platform/`
(the monorepo), `relay-tutorial/` (the site), `docs/` (the source documents).

---

## Phase 1: Setup

**Purpose**: Record the starting state so any later failure is attributable.

- [X] T001 Record the pre-change baseline in `specs/025-chapter-3-4/baseline.txt`: both lanes with **exit codes** as well as counts (expected 120 unit, 87 integration — 3.3's closing numbers), plus feature 024's coverage numbers and the ratchets now in force
- [X] T002 [P] Bring the stores up (`RELAY_POSTGRES_PORT=15432 RELAY_REDIS_PORT=16379 RELAY_NATS_PORT=14222 docker compose up -d --wait postgres redis nats`), then `pnpm build` and apply existing migrations
- [X] T003 [P] Confirm the site baseline in `relay-tutorial/`: `pnpm lint`, `pnpm build`, `pnpm check:docs`, `pnpm check:fences` — all green before any edit

**Checkpoint**: baseline recorded, broker reachable, stream present from 3.3.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Find out what the broker will actually let us change, before designing around an assumption.

**⚠️ CRITICAL**: T004 comes first. The chapter's entire configuration section is only possible if an existing stream can be reconfigured in place. If `retention` or `storage` had been wrong at 3.3, the answer would have been "delete the stream and every event in it" — and that is a different chapter.

- [X] T004 Measure which stream settings can be changed on an existing stream: apply a changed `retention`, a changed `storage`, and a changed `max_age` to the live `EVENTS` stream and record exactly what the broker does with each in `specs/025-chapter-3-4/research.md` under R1 *(transcript lost with the machine; finding preserved in the prose and in `ensureStream`'s comments — see the reconstruction note in research.md)*
- [X] T005 Record the stream's inherited defaults as the chapter's opening transcript — what 3.3 chose by hand versus what NATS supplied (research R2, `baseline.txt` §Broker)
- [X] T006 Measure what happens to a message that exhausts `max_deliver`: does anything catch it, is there a dead-letter subject, does the consumer see a log line. Record in research.md under R4 *(transcript lost; finding preserved in `MAX_DELIVER`'s comment and invariant 7)*
- [X] T007 Add `consumed_events` to `relay-platform/services/api/src/db/schema.ts` with a DECISION comment recording that SAD risk R5 specifies the behaviour and leaves the shape open, the composite primary key as the deduplication, and the per-consumer keying (spec FR-013, data-model)
- [X] T008 Generate `relay-platform/services/api/migrations/0005_consumed_events.sql` with drizzle-kit and review it line by line before applying — the composite key and the absence of a foreign key both checked rather than assumed — recording the review disposition in the file header as 0002–0004 do
- [X] T009 Apply the migration and verify with `psql \d consumed_events` that the primary key is composite and no foreign key exists (spec FR-013)
- [X] T009a **[reconstruction]** Regenerate drizzle's `meta/0005_snapshot.json` and journal entry, and verify the generated SQL is byte-identical to the reviewed migration — which also proves the reconstructed `schema.ts` is faithful *(did not exist at implementation time; the metadata was lost and the runner ignores it, so nothing was broken at runtime, but a future `drizzle-kit generate` would have re-emitted the table)*
- [X] T010 Prove the foundation changed nothing yet: both lanes match `baseline.txt`, exit codes read

**Checkpoint**: the ledger exists, the broker's limits are known, nothing has regressed.

---

## Phase 3: User Story 2 — The canonical code advances to `part3-ch4` (Priority: P2)

**Goal**: A deliberately configured stream, a shared grammar, and a consumer whose runtime deduplicates so its handler cannot forget to.

**Independent Test**: At `part3-ch4` the Docker-free gate passes; with the stores up every integration lane passes including 2.8's journey and 3.3's outbox suite; removing the ledger claim from the runtime fails three of the ten broker-backed invariants.

### The shared grammar

- [X] T011 [P] [US2] Move the subject grammar to `relay-platform/packages/protocol/src/internal.ts` — `EVENT_SUBJECT_PREFIX`, `ALL_EVENTS_SUBJECT`, the domain abbreviation map, `subjectFor` — with the reason a consumer must not assemble its own filter (spec FR-012, research R9)
- [X] T012 [P] [US2] Re-export `subjectFor` from `relay-platform/services/api/src/outbox/event.ts` so 3.3's callers keep working, with a comment saying where it went and why
- [X] T013 [US2] Write `relay-platform/packages/protocol/src/internal.test.ts` — five cases: the environment goes last, `message` abbreviates to `msg`, an unabbreviated domain passes through, a missing part throws rather than producing `events..created.`, and the output is matched by the wildcard every consumer subscribes to **⚠️ never fenced — see chapter-notes.md finding 1**

### The decision table, before any broker

- [X] T014 [US2] Write the handler contract in `relay-platform/services/api/src/consumer/handler.ts`: returns → handled, throws → not handled. No acknowledge, no nak, no retry, no dedupe, no raw message — every withheld capability is a way SAD risk R5 could otherwise materialise (spec FR-015)
- [X] T015 [US2] Extract `decideOutcome` in `relay-platform/services/api/src/consumer/runtime.ts` as a pure function taking its claim as an argument, so the decision table can be read in one place and tested without a broker (spec FR-014, FR-016)
- [X] T016 [US2] Write the two pure invariants (contracts §Invariants 10, 11) in `relay-platform/services/api/src/consumer/runtime.test.ts` **⚠️ never fenced, and the chapter never names these two invariants — the eight tests in the tree are authored during reconstruction, not recovered; see chapter-notes.md finding 1**

### The ledger claim

- [X] T017 [US2] Add `claimEvent` to `relay-platform/services/api/src/db/repository.ts`: `INSERT … ON CONFLICT DO NOTHING … RETURNING` inside a transaction, running the effect only if the row was won — with the comment explaining why claiming outside the transaction is the dangerous ordering (spec FR-014, data-model)
- [X] T018 [US2] Add `timesHandled` beside it, so the redelivery test asserts through the repository rather than reaching into the table
- [X] T019 [US2] Write the conflict path first: a second claim for the same `(consumer, event_id)` returns `duplicate` and does **not** run the effect

### The stream, made deliberate

- [X] T020 [US2] Rewrite `ensureStream` in `relay-platform/services/api/src/outbox/jetstream.publisher.ts`: mutable settings merged onto whatever exists, immutable ones supplied only on create, every value carrying its reason (spec FR-009, FR-010, research R1, R2)
- [X] T021 [US2] Derive the replica count from the environment rather than hardcoding ADR-02's R3 or the compose stack's 1 (spec FR-011, research R11)
- [X] T022 [US2] Leave `duplicate_window` where 3.3 found it, with the comment explaining why raising it looks like the fix and is not (research R3)

### The runtime

- [X] T023 [US2] Build the pull consumer in `runtime.ts`: bounded batches, explicit ack, `max_deliver`, `ack_wait`, `max_ack_pending` — each a number with a reason rather than a default (research R6, R7)
- [X] T024 [US2] Connect lazily, so an unreachable broker leaves the api serving writes (spec FR-018)
- [X] T025 [US2] Create the durable if absent, leave it alone if present, so two instances share a position rather than fighting over it (research R8)
- [X] T026 [P] [US2] Write the first handler in `relay-platform/services/api/src/consumer/recorder.ts` — identifiers and counts only, never `event.data.text` (spec FR-021, NFR-SEC-06) — with its retirement in 3.5 named in the file
- [X] T027 [P] [US2] Wire it in `consumer.module.ts`, `app.module.ts` and `main.ts`, on by default, with `RELAY_EVENT_CONSUMER` as the off switch for suites that want a quiet broker
- [X] T028 [P] [US2] Amend `turbo.json` and `packages/e2e/src/harness.ts` to carry `RELAY_EVENT_CONSUMER` and `RELAY_NATS_REPLICAS` into the lanes and the child api

### The ten broker-backed invariants

- [X] T029 [US2] Invariants 1 and 2 in `relay-platform/services/api/src/consumer/consumer.itest.ts`: settings read back as configured; applying twice is a no-op (SC-002, SC-010)
- [X] T030 [US2] Invariant 3: an event delivered, handled once, acknowledged
- [X] T031 [US2] Invariant 4 — the chapter's centrepiece: spawn the walk, wait for its marker, `SIGKILL` it, then assert the ledger says one, the redelivery arrives, and the handler runs **zero** further times (spec FR-019, SC-003)
- [X] T032 [US2] Invariants 5 and 6: deduplication surviving a restart; two instances sharing a durable dividing the work (SC-004, SC-005)
- [X] T033 [US2] Invariants 7 and 8: a throwing handler stopping after the bound; an unparseable payload terminated on the first attempt and writing no ledger row (SC-006, SC-007)
- [X] T034 [US2] Invariants 9 and 12: a stopped consumer receiving its backlog; a log line carrying counts and never payloads (SC-008, SC-009)
- [X] T034a **[reconstruction]** Verify the suite holds something: remove the ledger claim from the runtime and confirm **three of the ten** fail; mutate the pure decision table three ways and confirm each is killed by the test that names the behaviour. Restore and verify byte-identical to the fence *(the chapter states the three-of-ten result; the mutation battery on the unit lane is the reconstruction's addition)*

### The walk scripts

- [X] T035 [P] [US2] Write `relay-platform/scripts/consumer-walk.mjs` — the same artifact the reader runs and the test kills, with `--kill-before-ack` printing its marker between the claim and the acknowledgement (research R7)
- [X] T036 [P] [US2] Write `relay-platform/scripts/stream-info.mjs` — ask the broker what it holds rather than printing the config file, because a configuration that was written is not one that was applied

### Prove nothing regressed

- [X] T037 [US2] Run both lanes and confirm 133 unit / 97 integration with exit code 0, every pre-existing suite present and unchanged in substance (spec FR-020, SC-011)
- [X] T038 [US2] **Take the coverage measurement three chapters deferred**: `pnpm coverage` with the stores up, exit code read, workspace and `repository.ts` numbers recorded in `captured-output.md` and research R10. The 024 ratchet on `repository.ts` must hold — this chapter adds to that file (Principle VI)

**Checkpoint**: the code is provable, measured, and its tests hold something.

---

## Phase 4: User Story 1 — The chapter (Priority: P1)

**Goal**: The prose, written from what the code actually does.

- [X] T039 [US1] Capture every transcript the chapter will quote into `specs/025-chapter-3-4/captured-output.md` — the opening stream state, the invariant run, both walk modes, `stream-info`, the coverage summary (spec FR-024)
- [X] T040 [US1] Write `relay-tutorial/app/(en)/part-3/chapter-04/jetstream-and-the-first-consumer/page.mdx`: the inherited defaults, every setting made a decision, the consumer's gap, the ledger, and the two things the chapter must admit — that nothing catches an exhausted message, and that the shared-transaction pattern needs a transactional effect (spec FR-002…FR-007)
- [X] T041 [P] [US1] Write the three figures in `figures.ts`: the other gap (sequence), the outcomes (flowchart), where it runs (flowchart)
- [X] T042 [US1] Measure the battery on the published page and record it in `specs/025-chapter-3-4/battery.txt`; confirm the SKIP AHEAD names `part3-ch4`
- [X] T043 [US1] Traceability: every `FR-*`/`NFR-*`/`ADR-*` cited exists in a source document, every table and column named exists in `schema.ts` (spec SC-012)

**Checkpoint**: the chapter says only what the code does.

---

## Phase 5: User Story 3 — Publication in both locales (Priority: P3)

- [X] T044 [US3] Translate the chapter to `relay-tutorial/app/(vi)/vi/part-3/chapter-04/...`, fences mirrored byte for byte (spec FR-001)
- [X] T045 [US3] Amend `relay-tutorial/lib/tutorial.ts`: 3.4 published, `translatedIn: ["vi"]`, with its `readerProduces` in both languages
- [X] T046 [US3] Verify publication: EN 200, VI 200, three figures rendering in each, the reading shell present — not merely "the page loaded" (spec SC-013, quickstart V8)
- [X] T047 [US3] `pnpm check:fences` — every fenced file in every published chapter replays onto the repository byte-for-byte

---

## Phase 6: Gates

- [X] T048 Quickstart V1–V8, exit codes read rather than output grepped
- [X] T049 Write `chapter-notes.md` from what happened rather than what was planned
- [ ] T050 **Open**: fence `internal.test.ts` and `runtime.test.ts` in both locales — the chapter asserts both files and carries neither, so the fence chain cannot replay the repository it describes (spec FR-025, chapter-notes finding 1)
- [ ] T051 **Open**: re-capture the opening and closing stream counts against a stack that has been running, or accept them as historical transcripts a reader cannot reproduce (chapter-notes finding 2)
- [ ] T052 **Open**: decide whether `runtime.ts`'s identical-branch ternary is pedagogy or a defect, and simplify or comment accordingly (chapter-notes finding 3)

---

## Dependencies

**T004 blocks everything.** If an existing stream could not be reconfigured in
place, the chapter's configuration section would be "delete the stream and every
event chapter 3.3 proved durable", which is a different chapter with a different
argument. Measuring first is not caution; it is the difference between two
chapters.

**T013 and T016 precede the broker work** for the reason 3.3 put its envelope
tests before its relay: a decision table proved pure is a decision table you are
not debugging through a hundred seconds of integration suite.

**T017–T019 precede T023.** The runtime is built around the claim, and the claim's
conflict path is the one that must be right — a claim that succeeded when it
should have conflicted would make every redelivery test pass for the wrong reason.

**T038 gates the chapter.** Three chapters shipped without this measurement by
explicit decision. The instrument exists now, so a coverage run that does not
exit 0 stops the chapter rather than being recorded as a fourth deferral.

**US1 depends on all of US2.** Prose comes after code, as always: five of the last
seven chapters changed a claim once their code was real.

---

## Notes

**On the two artifacts that are one.** T035's walk script is the same file T031's
test spawns and kills. That is deliberate and it is the same argument 3.3 made:
one artifact, run by a reader and by the suite, so neither can rot alone. A
demonstration that only readers run stops compiling silently; a harness that only
tests run drifts from what the chapter shows.

**On admitting a gap.** T033's invariant 7 asserts what happens when delivery
attempts are exhausted — the message leaves the consumer's view and nothing
catches it. The temptation is to soften that into implying a dead-letter path
exists somewhere. It does not, until 3.5. Assert the exhaustion behaviour rather
than the absence of a dead letter, and the test survives 3.5 adding one.

**On the two open fence tasks.** T050 is not cosmetic. The fencing rule exists so
a reader can rebuild the repository from the chapter, and this chapter's own
reconstruction is the proof of both halves: 17 fences regenerated the platform
almost exactly, and the two files that were *not* fenced could not be recovered —
one was rewritten from a prose description, the other authored outright. A
chapter that describes a file it does not fence has a hole in exactly the place
the rule was meant to cover.
