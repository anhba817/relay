# Tasks — chapter 4.5, the gateway's first stream

**Feature**: `specs/050-chapter-4-5/` · **Plan**: [plan.md](./plan.md) · **Spec**: [spec.md](./spec.md)

**US1 SPANS TWO PHASES, AND THAT IS THE PLAN'S ARGUMENT RATHER THAN A SCHEDULING ACCIDENT.**
Phase 2 publishes connection records into a stream nothing writes yet; phase 4 gives them a
table. The window between them is the only chance this project will get to prove 4.4's
`unclaimed` arm on a **real** record rather than a synthetic one — a record a real producer
sent, that a real consumer declined to claim, and that came back. Collapsing the two phases
throws that away to save a commit.

**Verification methods, decided rather than defaulted.** The record-per-connection claim is
**D**. The gateway-keeps-serving claim is **A**, from two measured distributions, because the
claim is an absence. The quota-path-unchanged claim is **T** — an existing suite passing
untouched is the only evidence that means anything about a path this chapter deliberately did
not modify. The tenancy claim is **T**, because constitution I does not take a demonstration.
ADR-07's amendment is **I**.

**AND THIS CHAPTER EXPECTS TO OWE FENCE HUNKS.** It edits `session.ts`, `main.ts`, `shape.ts`,
`ingest.ts` and the protocol — every one published as a whole body by an earlier chapter. 049
discovered at its close that this costs the chain six problems until the diffs are published.
T088 and T089 do it deliberately in phase 8 rather than discovering it.

---

## Phase 1: Premises, the dependency, and the numbers this chapter inherits

**Everything blocks on this.** Four of `research.md`'s ten items were measured during planning;
re-run each here. A premise carried from a planning document and never re-run is what this
project finds most often.

- [ ] T001 Record the gateway's dependency count in `specs/050-chapter-4-5/baseline.txt` **before** anything is added: `node -e` over `services/gateway/package.json`. Planning read **5** — `@relay/protocol`, `@relay/service-kit`, `ioredis`, `jose`, `ws`. **The number is the subject, not a detail**: ADR-07 rejects NATS for the gateway on an argument about how many client libraries it holds.
- [ ] T002 Confirm R1 in `specs/050-chapter-4-5/baseline.txt`: `grep -rn "nats\|jetstream" --include=*.ts services/gateway/src` returns nothing. **Record the command and the empty result**, because a zero from a grep is a claim about the corpus only if the grep can be shown to have read it — and `grep` on this machine is ugrep, so give the pattern a positive control that matches something.
- [ ] T003 Quote `session.ts`'s close-handler comment into `specs/050-chapter-4-5/baseline.txt` from the file rather than from `research.md` — *"a mass disconnect would turn one event into a burst of HTTP requests"* — with the `meter.closed(...)` call beside it. **This chapter wants to do the thing that handler declined to do**, and the quote is the reason it cannot do it naively.
- [ ] T004 Re-run R3's burst probe and record all three numbers in `specs/050-chapter-4-5/baseline.txt`: awaited-per-close, core publish, batched. Planning read **0.229 ms**, **0.0030 ms**, **0.0034 ms** per record over 2,000. **Extrapolate to NFR-SCL-01's 10,000** and record that figure explicitly — it is the one the design turns on.
- [ ] T005 [P] Quote ADR-07's v1.1 amendment into `specs/050-chapter-4-5/baseline.txt` **from `docs/05-sad.md`**, not from `docs/12` §7.2, which paraphrases it as *"clean mapping — gateway to Redis"* — a phrase that appears nowhere in the SAD. 049 found five stale cross-references in that same section.
- [ ] T006 [P] Record the meter's minute rule verbatim from `services/gateway/src/meter.ts` in `specs/050-chapter-4-5/baseline.txt`, including its worked example: open 00:00:59, close 00:01:01, **two** connection-minutes for two seconds of wall clock.
- [ ] T007 [P] Record the existing usage path in `specs/050-chapter-4-5/baseline.txt`: the route, the cadence (`METER_INTERVAL_MS`), the batch bounds (1..5000), and the entry's four fields. **`docs/12` §3 does not mention that this path exists**, and the chapter's whole framing depends on it.
- [ ] T008 [P] Run `pnpm check:fences` in `relay-tutorial` and record the opening in `specs/050-chapter-4-5/baseline.txt` **broken down by kind and locale**. 047, 048 and 049 all opened and closed at 110 — APPLY 74 (30 en, 30 vi, 14 elsewhere), HEAD 36 (all en).
- [ ] T009 [P] Pin the environment in `specs/050-chapter-4-5/baseline.txt`: node, pnpm, the NATS/ClickHouse/Postgres image tags, `SELECT version()`, the `ws` and `nats` versions, cpus, RAM, `DOCKER_HOST`, `RELAY_POSTGRES_PORT=15432`.
- [ ] T010 [P] Record the analytical store's state fresh in `specs/050-chapter-4-5/baseline.txt`: `system.tables` for `relay_analytics`, the `schema_applied` ledger (tail `0004_api_requests.sql`), and the row counts of the three existing tables.
- [ ] T011 Record the stream state and **name which services were running when it was taken**. 048's planning probe reported `consumers 0` without saying that, and a zero consumer count on a stream whose consumer is simply not started proves nothing.
- [ ] T012 **Retarget `check-lane-scope.py` before trusting it.** 049-3 measured that it hardcodes a worktree 045 deleted, so it reports `0 integration files` and exits 0 with all ten controls firing. Record both readings in `specs/050-chapter-4-5/baseline.txt` — the stale one and the retargeted one — because the difference is the finding.
- [ ] T013 Commit phase 1 — `specs/050-chapter-4-5/baseline.txt` only. No platform change yet.

---

## Phase 2: User Story 1 — the records exist (Priority: P1)

**Goal**: a connection opening and closing puts two records on the stream.

**Independent test**: open and close a known number of connections, then read the stream
directly and count the open and close records. Nothing consumes them yet.

**Why the table does not exist yet**: see the note at the top of this file.

- [ ] T014 [P] [US1] Add `CONNECTION_OPENED_ACTION`, `CONNECTION_CLOSED_ACTION` and their subject functions to `packages/protocol/src/internal.ts`, beside the webhook and api-request pairs, using `analyticsSubjectFor` unchanged.
- [ ] T015 [P] [US1] Test them in `packages/protocol/src/internal.test.ts`: each subject matches `ALL_ANALYTICS_SUBJECT`, and a non-UUID environment is **refused**. Assert the refusal, not only the success.
- [ ] T016 [US1] Add `nats` to `services/gateway/package.json` and record the new dependency count in `specs/050-chapter-4-5/baseline.txt`. **5 → 6**, and T001's number is what it is compared against.
- [ ] T017 [US1] Write `services/gateway/src/connection-log/event.ts`: `toConnectionEvent()` building each record by **naming every field**. A spread would carry a socket, an identity or a token onto a stream with seven-day retention; an allow-list fails closed when somebody adds a field.
- [ ] T018 [US1] Discharge **FR-005a**: the open record's `ts` is **`connection.openedAt`**, the field the meter reads — not `new Date()` at hand-over. It is stamped two lines before `registry.add`, *"BEFORE the resume and before the ack, because the socket is already open and already costing a minute"*. Two instants for one open would make T071's reconciliation disagree for a reason the chapter does not explain.
- [ ] T019 [US1] Assert in `services/gateway/src/connection-log/event.test.ts` that no credential, token, channel list or message content can reach the record, by handing the shaper an object carrying all four and checking the serialised output for each.
- [ ] T020 [US1] Write the buffer in `services/gateway/src/connection-log/event.ts`: records accumulate and a tick publishes them. **Not one publish per close** — T004's 0.229 ms is 2.3 s for 10,000, which is `session.ts`'s own HTTP argument on a new transport.
- [ ] T021 [US1] Discharge **FR-004c**: **name the flush interval and show the budget.** FR-ANL-04 allows 60 seconds from the event to it being queryable and the ingester's `BATCH_MS` spends up to 2. **Do not copy `METER_INTERVAL_MS`** — 60,000 ms breaches the clause before the record leaves the gateway, and it is the obvious number precisely because this chapter's posture is *be like the meter*. The meter feeds a monthly quota with no latency clause over it; this feeds a store that has one.
- [ ] T022 [US1] Record why a short interval costs nothing in `specs/050-chapter-4-5/baseline.txt`: batching's win is grouping whatever accumulated, not waiting longer — 0.0034 ms a record at any interval — and R3's 2.3-second burst is a property of publishing **per close**. `5_000` ms is the proposal; whatever is chosen, write down what it spends.
- [ ] T023 [US1] Discharge **FR-004a**: **bound the buffer.** An unreachable broker means records accumulate without leaving, and an unbounded buffer on a service holding 10,000 sockets is an out-of-memory that closes every one of them — FR-004 satisfied at the record level and violated at the service level. `meter.ts` caps at `MAX_RETAINED_CLOSED = 4_000`; pick a number and argue it the same way.
- [ ] T024 [US1] Discharge **FR-004b**: **count the drops and name the direction.** Dropping the oldest loses the earliest events; dropping the newest loses the ones describing the outage. The meter drops the oldest because *"under-counts … is the same direction as every other loss in this design"* — say whether that argument transfers here, because a connection log is not a bill.
- [ ] T025 [US1] Test the bound red: fill the buffer past its cap with the broker unreachable and assert the drop counter moves and memory does not. **A cap nothing has ever reached is a cap nobody has tested.**
- [ ] T026 [US1] Discharge **FR-004d**: **measure** the end-to-end latency — one connection closing to its row being readable — and publish it against FR-ANL-04's 60 seconds. Derived arithmetic is not a measurement, and this chapter is the first in Part 4 where the clause can be breached at all.
- [ ] T027 [US1] Use the batched form measured in T004, not core publish. Core is 0.0030 ms against 0.0034 and gives up the ack and the deduplication id — and this stream exists to be recoverable, which is why 3.20 chose JetStream over core in the first place.
- [ ] T028 [US1] Write `services/gateway/src/connection-log/publisher.ts`: **one** client, created once, shared, lazily connected. An unreachable broker must leave the gateway serving sockets, which is the same posture every other publisher in this platform takes.
- [ ] T029 [US1] Hand over in `services/gateway/src/session.ts` at **two different anchors**, because the meter is asymmetric by design: the open beside `registry.add(connection)` (`session.ts:959`) and the close beside `meter.closed(...)` (`session.ts:1146`). **There is no `meter.opened`** — the `Meter` interface is `closed`, `reportOnce`, `retained`, `dropped`, `stop`, and it learns about open connections by walking the registry. Not inside the meter either: its contract is connection-minutes for a quota and it is fenced in 3.24.
- [ ] T030 [US1] The close-side hand-over must not throw and must not await. `session.ts`'s close handler is documented as the last place that should throw — **assert that in a test rather than trusting the comment**, by making the publisher throw and checking the socket still closes cleanly.
- [ ] T031 [US1] Wire the publisher's lifecycle in `services/gateway/src/main.ts`, and **close it AFTER `sessions.close()`** in `shutdown()`. That function closes seven things in a stated order and this makes it **eight**; `sessions` is first *"because its close is the one with work to finish … the fabrics it reports and publishes through have to still be open while it does that"*, and the flush of this buffer is exactly that kind of work.
- [ ] T032 [US1] Record the shutdown list's length before and after in `specs/050-chapter-4-5/baseline.txt`. The file's own warning applies: *"A `shutdown` that closed three of seven would leak four per deploy — and `main.ts` is excluded from the coverage ratchet, so no figure could show it."* **Nothing will catch a missed close**, so the count is the check.
- [ ] T033 [US1] Record what a clean stop does to in-flight records in `specs/050-chapter-4-5/baseline.txt`, and what a killed process does. The second is the number a dashboard has to tolerate.
- [ ] T034 [US1] Decide the unauthenticated-socket case and record the decision **and its loser** in `specs/050-chapter-4-5/baseline.txt`. A connection that never completes a handshake has no identity and no environment. 4.4's `_none` arm is for requests; reusing it here needs an argument or a different answer.
- [ ] T035 [US1] Write `services/gateway/src/connection-log/connection-log.itest.ts`: open and close N connections, read the stream directly, assert 2N records **against a non-zero floor**. A three-way equality at zero is satisfied by nothing at all.
- [ ] T036 [US1] Assert in the same test that the records are **left on the stream** by the existing ingester rather than terminated — 4.4's `unclaimed` arm, exercised on a real record. Run `ingestOnce` twice across `ack_wait` and show the count comes back.
- [ ] T037 [US1] Run `pnpm lint`, `pnpm typecheck` and `pnpm test`. Record failures in `specs/050-chapter-4-5/baseline.txt` rather than only the green run.
- [ ] T038 [US1] Commit phase 2.

---

## Phase 3: Foundational — the table and the third arm

**Blocking for phase 4.** The `unclaimed` window measured in phase 2 closes here.

- [ ] T039 Record the `unclaimed` count the ingester reported while phase 2's records had no table, in `specs/050-chapter-4-5/baseline.txt`. **This is the number the window existed to produce**, and it is gone once the table lands.
- [ ] T040 Write `analytics/0005_connection_events.sql` per `data-model.md` §1. One statement, qualified `relay_analytics.` — `apply.mjs` refuses both otherwise.
- [ ] T041 Put `event` in the sorting key after `connection_id`. **One connection produces two rows with one `connection_id`**, and without it a `ReplacingMergeTree` collapses the open into the close. Verified against the server during planning: `count() FINAL` 2, not 1.
- [ ] T042 Use `TTL toDateTime(ts) + INTERVAL 90 DAY`, not `TTL ts + INTERVAL` — 047 measured the second refused with `BAD_TTL_EXPRESSION` on a `DateTime64`. **And record that 90 is a default rather than a derivation**: FR-ANL-07 fixes 30 for the request log and nothing fixes this one.
- [ ] T043 Give `close_code` the type **`Nullable(UInt16)`**, not a string. A close code is a small integer, and a String column answers `WHERE close_code = 1000` with nothing and no error. **Measured: ClickHouse coerces a JSON number into a String column AND a JSON string into a UInt16, so a type disagreement between the producer and the table lands silently.** The other close-only column, `duration_ms`, is `Nullable(UInt32)`; an open record carries neither.
- [ ] T044 Include the `ts_is_real` CHECK constraint. 048 measured that an absent column takes its default, a `DateTime64` default is the epoch, and the epoch is older than any TTL, so the row is deleted at insert while the insert returns OK.
- [ ] T045 Run `node analytics/apply.mjs` and record `applied 1: 0005_connection_events.sql`, then a second run reporting `applied nothing`. **Capture the exit code outside any pipeline** — 049 read it through `| sed` twice and got sed's status.
- [ ] T046 [P] Test the checksum refusal red: change one byte, re-run, record the refusal text, restore.
- [ ] T047 Add the third arm to `services/ingester/src/shape.ts`'s `route()` and a `shapeConnection()` that **drops `type`** — the wire carries it and the table has no column, and forwarding it lands `Code: 117`.
- [ ] T048 Add a third buffer to `services/ingester/src/ingest.ts` and insert before any ack, as the other two do. Record whether three buffers on one fetch changes the DR-11 picture 049 measured — the empty-buffer guard is what carries it.
- [ ] T049 Extend `services/ingester/src/clickhouse.ts` with the third table, keeping `input_format_skip_unknown_fields=0` and `date_time_input_format=best_effort`.
- [ ] T050 Verify the table against `data-model.md` with `SHOW CREATE TABLE relay_analytics.connection_events` and record it. **Ask the database rather than reading the file you just wrote** — 049 found the server normalising two spellings that way.
- [ ] T051 Run the three gates and commit phase 3.

---

## Phase 4: User Story 1 — the records land (Priority: P1) 🎯 MVP

**Goal**: a connection that opens and closes becomes two rows in the analytical store.

**Independent test**: open and close N connections, drain, count rows with `FINAL` against a
non-zero floor, and show one connection's pair as two rows rather than one.

- [ ] T052 [US1] Extend `services/gateway/src/connection-log/connection-log.itest.ts`: after draining, count rows for the test's own environment and assert 2N.
- [ ] T053 [US1] Assert one connection's pair is **two rows**, with the open carrying no `close_code` and no `duration_ms` and the close carrying both. That is the `event`-in-the-key decision, checked rather than assumed.
- [ ] T054 [US1] Discharge **FR-014**: insert the same close record three times and assert physical `count()` 3 against `FINAL` 1, with `SYSTEM STOP MERGES` on the table. **A physical count taken while a merge runs measures the merge** — 049's own first probe read 2 after six inserts.
- [ ] T055 [US1] Assert the tenancy branch in `services/gateway/src/connection-log/event.test.ts` and publish the measured branch coverage beside constitution VI's 100%, met or pinned with the shortfall stated as a number.
- [ ] T056 [US1] Pin the new files in `vitest.coverage.config.mts` with freshly measured numbers, and **run both halves of the threshold probe** — demand 101%, confirm red, restore, confirm green. 049 found a pin that could not fail because its key was excluded from collection.
- [ ] T057 [US1] Sweep every per-file pin against the exclude patterns and record the count. 049 measured 45 pins, 1 unbindable, then 0.
- [ ] T058 [US1] Run the quickstart's §4 block verbatim and record its output. **Rebuild the gateway image first** — 049's equivalent measured the old image and produced no rows at all.
- [ ] T059 [US1] Run `specs/045-part-3-rework/check-lane-scope.py` **retargeted per T012** after adding the integration tests, and record its report.
- [ ] T060 [US1] Run the three gates and commit phase 4. **MVP ends here.**

---

## Phase 5: User Story 2 — the gateway keeps serving when the broker is gone (Priority: P1)

**Goal**: sockets connect, carry messages and close normally with the broker unreachable.

**Independent test**: two distributions of connection latency, broker up and stopped, with the
per-connection outcomes published beside them.

- [ ] T061 [US2] Verify by **inspection** that no publish is awaited in a socket handler, and record the call sites. A timing test passes on a fast broker whether or not the await is there.
- [ ] T062 [US2] Measure connection open-to-ready latency with the broker healthy — a warm-up, then the sample — and record the distribution. 046 published a wrong number twice by comparing a cold run against a warm one.
- [ ] T063 [US2] Stop NATS and repeat. **Stop the gateway's writers first if the stack must survive**: 049-1 measured that the stream being written when the broker restarts is the one that fails to recover, graceful or not.
- [ ] T064 [US2] Record the **connection outcomes** during the broker-down run, not only the latencies: how many opened, how many carried a message, how many closed cleanly. A connection that is fast and refused satisfies a timing assertion.
- [ ] T065 [US2] Confirm the publish failure is logged once per flush rather than once per record, and that the line carries no payload, no token and no channel list.
- [ ] T066 [US2] Restart NATS and confirm `/healthz` is `{"status":"ok"}` and the container healthy, **by a deliberate restart** — 048-6's lesson, and 049 found that check failing for a reason 048-6 had recorded wrongly.
- [ ] T067 [US2] Record what NFR-SCL-01's numbers look like after the sixth dependency: the gateway's RSS at rest, against the published 160 MB at 10,000 connections. **If the battery is not run, say that the figure is unmeasured rather than implying it holds.**
- [ ] T068 [US2] Run the three gates and commit phase 5.

---

## Phase 6: User Story 3 — the quota path is unchanged (Priority: P1)

**Goal**: connection-minutes still reach Postgres the way they did, and the two counters can be
compared.

**Independent test**: the existing meter suite passes untouched, and the quota counters move by
the same amounts as before the chapter.

- [ ] T069 [US3] Run the meter's existing suite and record that it passes **unmodified**, with the file's git status proving it was not edited. Verification method T, and an untouched suite passing is the only evidence that means anything here.
- [ ] T070 [US3] Record the quota counters before and after a known workload, and show they move by the same amounts as a run of the same workload from `part4-ch4`.
- [ ] T071 [US3] Discharge **FR-009**: derive minute buckets from the open and close records and compare them against what the meter reported for the same connections. **Compare buckets against buckets** — one quantity computed twice.
- [ ] T072 [US3] Publish the **duration-against-buckets** gap as a number in `specs/050-chapter-4-5/baseline.txt`, with the worked example: a connection open 00:00:59 to 00:01:01 is 2 connection-minutes and 2,000 ms. **They are different quantities sharing a name**, and the chapter says so rather than letting a reader treat the difference as a defect.
- [ ] T073 [US3] Record any connection where the two bucket counts disagree, with the cause. A disagreement there **is** a defect, unlike the one above.
- [ ] T074 [US3] Measure the open/close **balance** for a clean run and for a killed gateway. A killed instance produces opens with no closes, and the number is what a dashboard built on these records must tolerate.
- [ ] T075 [US3] Run the three gates and commit phase 6.

---

## Phase 7: User Story 4 — ADR-07 says what it now rests on (Priority: P2)

**Goal**: a reader of ADR-07 can tell why NATS is still not the fan-out fabric, given that the
gateway now holds a NATS client.

**Independent test**: the amendment exists, names the spent argument, and states the surviving
one. Verification method **I**.


- [ ] T076 [US4] Amend **ADR-07** in `docs/05-sad.md` a third time. Name the spent argument — the gateway's client-library count, now 6 — and state what the fan-out decision **now** rests on: ADR-10 puts presence in Redis, so Redis is mandatory for the gateway regardless, and a NATS-only proposal would have to move presence too.
- [ ] T077 [US4] Bump the SAD's version and run `pnpm sync:docs`. `check:docs` failed after a SAD amendment in 047, 048 and 049.
- [ ] T078 [US4] Grep the spent argument everywhere before calling it done — `docs/`, `specs/`, both tutorial locales. **Fix the file that describes the thing and the one that instructs it.**
---

## Phase 8: The numbers, the amendments, and the chapter

- [ ] T079 [P] Measure the combined byte rate of all three producers on the shared stream and restate the crossover. 4.4 measured 320 bytes a request record, 5.5 req/s for seven days and 38.8 for the SAD's 24 h. **Measure against a length-matched subject** — 4.4's first figure was 2% light for including the probe's own shorter subject.
- [ ] T080 [P] Measure the connection-event rate against the request-event rate and record it. `research.md` R7 **assumed** connection events are rarer and did not measure it; if a reconnect storm makes them commoner the crossover moves.
- [ ] T081 Amend `docs/12-part-4-structure.md` §3's one-line description of this chapter, which says the gateway has never touched NATS and does not say it already reports connection data every sixty seconds.
- [ ] T082 Draft the chapter at `relay-tutorial/app/(en)/part-4/chapter-05/<slug>/page.mdx`. **Do not re-derive** 3.20's fire-and-forget argument, 4.3's routing or 4.4's tenantless rule.
- [ ] T083 Discharge **FR-008**: state in the chapter why BOTH paths exist and **what each cannot do**. The meter cannot say a connection existed, only how many minutes it owed; the records cannot refuse a connection, because a quota refusal is synchronous and these are not. Name both limits rather than implying the new path supersedes the old.
- [ ] T084 Say plainly that `close_code` is **not** drawn from `CLOSE_CODES`. That registry is the platform's own 4001–4009 and a clean close is 1000, so `check:errors` does not guard this column — the claim that it did was in two artifacts before analysis pass 1 ran.
- [ ] T085 Put every mermaid source in `figures.ts`, never in `page.mdx`, and pass each to `<Figure>` as **`code=`**, not `chart=` — 049 shipped three as `chart` and `check:figures` named every line.
- [ ] T086 Take every number in a figure from `specs/050-chapter-4-5/baseline.txt`. No checker reads prose, and a mermaid block is prose.
- [ ] T087 Measure prose words outside code fences against the 2,000–4,000 bound and record the figure whether or not it forces a split.
- [ ] T088 Publish the SQL file as a whole body — it is new — and everything else as `diff` hunks against `part4-ch4`.
- [ ] T089 Generate the hunks from the checker's own replay, or from `git diff -U6 part4-ch4 -- <file>` where the file has not changed since that tag. **Verify they apply before pasting, not after.**
- [ ] T090 Run `pnpm check:fences` and report the close as a **delta against T008's opening**, broken down by kind and locale.
- [ ] T091 Run all eight gates: `check:fences`, `check:docs`, `check:srs`, `check:figures`, `check:errors` in `relay-tutorial`, then `lint`, `typecheck`, `test` in `relay-platform`. **Build before `check:errors`.**
- [ ] T092 Write `specs/050-chapter-4-5/gaps.md` for everything found and not closed, each entry naming what it would cost to close. **Carry 049-1, 049-2 and 049-3 forward if they are still open**, re-measured rather than copied.
- [ ] T093 Audit every test this feature added and confirm none asserts only that a record was published. Record the count audited.
- [ ] T094 Write `specs/050-chapter-4-5/traceability.md` mapping FR-001…FR-020 and SC-001…SC-011 to tasks and to the artifacts that discharge them. **Record the requirements nothing discharged**, if any.
- [ ] T095 Rewrite `CLAUDE.md`'s `<!-- SPECKIT -->` block for the close, including every task premise this feature falsified by running it.
- [ ] T096 Commit phase 7, tag `part4-ch5` on `relay-platform`, and push all three repositories.

---

## Dependencies & Execution Order

```
Phase 1  premises + the dependency  ── blocks everything
Phase 2  US1 the records exist      ── blocks 3
Phase 3  the table + the third arm  ── blocks 4
Phase 4  US1 the records land 🎯MVP ── blocks 5, 6
Phase 5  US2 broker gone            ── independent of 6
Phase 6  US3 the two counters       ── independent of 5
Phase 7  US4 ADR-07                 ── needs only phase 2's dependency count
Phase 8  the numbers + the chapter  ── needs 4; needs 5, 6 and 7 for its figures
```

### User story dependencies

- **US1** spans phases 2 and 4 and phase 3 sits between them, deliberately — see the note at the
  top.
- **US2** and **US3** both need US1 and are independent of each other.
- **US4** is the ADR amendment and needs only T001's and T016's dependency counts.

### Parallel opportunities

- Phase 1: T005–T012 are independent probes writing to separate sections.
- Phase 2: T014 and T015 (protocol) run beside T017 (the shaper) and T019 (its allow-list test).
- Phase 8: T079 and T080 are independent measurements.

---

## Implementation strategy

**MVP is phases 1–4**: a connection opens, closes, and becomes two rows.

**Phases 5 and 6 are what make it correct rather than working.** US2 is constitution III's
independence claim and US3 is the promise that this chapter did not break the thing that pays
the bills. Both are separable from the MVP, which is why they are their own phases.

**Phase 7 is one amendment and can be taken any time after phase 2**, because all it needs is
the dependency count going from 5 to 6. It is its own phase because ADR-07 resting on a reason
this chapter spends is a defect in the record, not a documentation chore.

**Phase 8 carries the chapter**, and one of its tasks is a second amendment: `docs/12` must stop
saying the gateway has no way to report connection data.

---

## Notes

**Commit each phase.** `git checkout` on a file with uncommitted work has destroyed work twice
in this project.

**Commits stay under five lines with no `Co-Authored-By` trailer.**

**Capture every exit code outside a pipeline.** 049 reproduced that mistake twice in one
feature.

**Run `check:fences` after any source edit**, not only at the ratchet — and this chapter edits
five fenced files, so expect to owe hunks rather than discovering it in phase 8.
