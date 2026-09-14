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

**AND THIS CHAPTER EXPECTS TO OWE FENCE HUNKS — FOR EIGHT FILES, NOT FIVE.** This note named
`session.ts`, `main.ts`, `shape.ts`, `ingest.ts` and the protocol until analysis pass 7 counted
the titles instead of remembering them, and it was wrong in both directions:

    32  services/gateway/src/session.ts            named
    25  packages/protocol/src/internal.ts          named
    23  vitest.coverage.config.mts                 NOT named   <- 048-3: cannot take a hunk
    22  services/gateway/src/main.ts               named
    10  services/gateway/package.json              NOT named   (T018)
     4  packages/protocol/src/internal.test.ts     NOT named   (T017)
     3  services/ingester/src/clickhouse.ts        NOT named   (T051)
     3  services/ingester/src/shape.ts             named
     0  services/ingester/src/ingest.ts            named — and it carries no fence at all

`ingest.ts` has no titled fence in either locale, because 049 created it by moving `ingestOnce`
out of `main.ts` and fenced `services/ingester/src/main.ts` and `clickhouse.ts` instead. 049
discovered at its close that editing a fenced file costs the chain six problems until the diffs
are published. T010a measures this list rather than carrying it, T092 and T093 pay it in phase 8,
and `vitest.coverage.config.mts` is the one that cannot be paid — see T010b.

---

## Phase 1: Premises, the dependency, and the numbers this chapter inherits

**Everything blocks on this.** Four of `research.md`'s ten items were measured during planning;
re-run each here. A premise carried from a planning document and never re-run is what this
project finds most often.

- [X] T001 Record the gateway's dependency count in `specs/050-chapter-4-5/baseline.txt` **before** anything is added: `node -e` over `services/gateway/package.json`. Planning read **5** — `@relay/protocol`, `@relay/service-kit`, `ioredis`, `jose`, `ws`. **The number is the subject, not a detail**: ADR-07 rejects NATS for the gateway on an argument about how many client libraries it holds.
- [X] T002 Confirm R1 in `specs/050-chapter-4-5/baseline.txt`: `grep -rn "nats\|jetstream" --include=*.ts services/gateway/src` returns nothing. **Record the command and the empty result**, because a zero from a grep is a claim about the corpus only if the grep can be shown to have read it — and `grep` on this machine is ugrep, so give the pattern a positive control that matches something.
- [X] T003 Quote `session.ts`'s close-handler comment into `specs/050-chapter-4-5/baseline.txt` from the file rather than from `research.md` — *"a mass disconnect would turn one event into a burst of HTTP requests"* — with the `meter.closed(...)` call beside it. **This chapter wants to do the thing that handler declined to do**, and the quote is the reason it cannot do it naively.
- [ ] T004 Re-run R3's burst probe and record all three numbers in `specs/050-chapter-4-5/baseline.txt`: awaited-per-close, core publish, and **pipelined with 500 publishes in flight**. Planning read **0.229 ms**, **0.0030 ms**, **0.0034 ms** per record over 2,000. **Extrapolate to NFR-SCL-01's 10,000** and record that figure explicitly — it is the one the design turns on. **Record the SHAPE beside each number, not only the number.** The original third row said "batched 500 per publish", which reads as 500 records in one message; the three rows' own units disagreed (two said *publishes*, one said *records*) and no artifact disambiguated them for four passes. Measure the shape you are going to ship.
- [X] T005 [P] Quote ADR-07's v1.1 amendment into `specs/050-chapter-4-5/baseline.txt` **from `docs/05-sad.md`**, because that is where v1.1 is. **And open `docs/12` §7.2 rather than avoiding it**: an earlier version of this task called its *"clean mapping — gateway to Redis"* a paraphrase and *"a phrase that appears nowhere in the SAD"* — true of `docs/05` and misleading, because it is **verbatim in `docs/06-adr-deep-dives.md`**, which is where ADR-07's argument lives. §7.2 is quoting, and it is this chapter's own open question (T085a). Quote all three into the baseline — the SAD's v1.1, the deep dive's selection argument, and §7.2's brief — so the amendment is written against the record rather than against one excerpt of it. 049's five stale cross-references were in **§4**, not §3 — analysis pass 13 put them in the wrong section and pass 14 read the amendment that says so. **§4 also certifies the section this task was avoiding**: *"THE ORDINALS IN THIS SECTION WERE ONE AHEAD OF §3's … Five cross-references pointed one chapter too far … **§7's references were written against §3's table and are unaffected.**"* The document had already answered the question.
- [X] T006 [P] Record the meter's minute rule verbatim from `services/gateway/src/meter.ts` in `specs/050-chapter-4-5/baseline.txt`, including its worked example: open 00:00:59, close 00:01:01, **two** connection-minutes for two seconds of wall clock.
- [X] T007 [P] Record in `specs/050-chapter-4-5/baseline.txt` that `connection.id` is **server-minted and always a UUID**: `id: claimedId ?? randomUUID()` (`session.ts:933`) where `claimedId` is `pendingId = randomUUID()` (`:794`). So the `connection_id UUID` column is safe and the id is **not caller-controlled** — the question 4.4 had to settle about `X-Request-Id`, asked again here. **A premise that holds is evidence only if it is written down.**
- [X] T008 [P] Record that the meter's tick is **stopped, not unref'd** (`meter.ts:218`, cleared by `stop()` from shutdown). The publisher follows the same pattern, which is what the shutdown-ordering task already says — so nothing needs adding, and this line is why.
- [X] T009 [P] Record the existing usage path in `specs/050-chapter-4-5/baseline.txt`: the route, the cadence (`METER_INTERVAL_MS`), the batch bounds (1..5000), and the entry's four fields. **`docs/12` §3 does not mention that this path exists**, and the chapter's whole framing depends on it.
- [X] T010 [P] Run `pnpm check:fences` in `relay-tutorial` and record the opening in `specs/050-chapter-4-5/baseline.txt` **broken down by kind and locale**. 047, 048 and 049 all opened and closed at 110 — APPLY 74 (30 en, 30 vi, 14 elsewhere), HEAD 36 (all en).
- [X] T010a [P] **Count the fence exposure per file rather than carrying a list.** For every file this chapter edits, `grep -rl 'title="<path>"' app fences` in `relay-tutorial` and record the count by locale in `specs/050-chapter-4-5/baseline.txt`. Analysis pass 7 found the carried list wrong in both directions — it named `ingest.ts`, which carries no fence, and omitted four that do, including the one that cannot be paid. **A list of fenced files is a measurement, and it goes stale every time a chapter moves code between files.**
- [X] T010b [P] **Ask whether this chapter's edit to `vitest.coverage.config.mts` unanchors the appendix.** Nine of that file's hunks live in `fences/post-series.md`, which applies after every chapter, and CLAUDE.md's rule is that an appendix hunk anchored on a file's last line forbids any chapter from appending. 047 asked this of `compose.yaml`, found `post-series.md` never touches it, and published the clean premise. Record the answer for **this** file in `specs/050-chapter-4-5/baseline.txt` — and record that 048-3 already says the file cannot take a hunk, so the chapter will owe chain problems it pays with a gaps entry rather than a diff. **Decide that in phase 1; 048 and 049 both found it at the ratchet.**
- [X] T010c [P] **Measure the Vietnamese Part 4 chain, at the path it is actually on.** It is `app/(vi)/vi/part-4/`, not `app/(vi)/part-4/` — the second has never existed, and an assumption checked against it came back empty for five passes. Record in `specs/050-chapter-4-5/baseline.txt` which chapters exist there, which titled fences they carry, and **which of them are whole bodies**. Planning found three chapters and seven fences, with `services/ingester/src/shape.ts`, `services/ingester/src/clickhouse.ts` and `services/ingester/src/main.ts` published entire. T049 and T051 edit the first two. **A whole body that stops matching is one problem this chapter cannot pay with a hunk**, because the hunk would have to be written into a Vietnamese chapter and translation is not this feature's work.
- [X] T010d [P] Record the three lane premises this chapter stands on in `specs/050-chapter-4-5/baseline.txt`, each checked rather than assumed — **all three held, and each was a plausible repeat of a defect this project has already paid for.** (1) `services/gateway/vitest.integration.config.mts` has `include: ["src/**/*.itest.ts"]`, recursive — every existing gateway itest sits directly in `src/` and `connection-log/` is the first subdirectory, so a single-star glob would have run nothing new and passed green. (2) `vitest.coverage.config.mts` has `include: ["packages/*/src/**/*.ts", "services/*/src/**/*.ts"]`, so T058's nested pin binds; 4.4's `services/api/src/request-log/event.ts` is the precedent, and 049 found exactly 1 unbindable pin in 45. (3) `connection-log.itest.ts` needs **no** `EXEMPT_FILES` entry: the global-operation guard throws only when `RELAY_HARNESS_BAIT === "on"`, and the gateway lane's config says it *"gets exemption handling and NO bait"* — and `exempt.test.ts` asserts that list in both directions, so a needless entry is a defect of its own.
- [ ] T011 [P] Pin the environment in `specs/050-chapter-4-5/baseline.txt`: node, pnpm, the NATS/ClickHouse/Postgres image tags, `SELECT version()`, the `ws` and `nats` versions, cpus, RAM, `DOCKER_HOST`, `RELAY_POSTGRES_PORT=15432`.
- [ ] T012 [P] Record the analytical store's state fresh in `specs/050-chapter-4-5/baseline.txt`: `system.tables` for `relay_analytics`, the `schema_applied` ledger (tail `0004_api_requests.sql`), and the row counts of the three existing tables.
- [ ] T013 Record the stream state and **name which services were running when it was taken**. 048's planning probe reported `consumers 0` without saying that, and a zero consumer count on a stream whose consumer is simply not started proves nothing.
- [X] T014 **Retarget `check-lane-scope.py` before trusting it.** 049-3 measured that it hardcodes a worktree 045 deleted, so it reports `0 integration files` and exits 0 with all ten controls firing. Record both readings in `specs/050-chapter-4-5/baseline.txt` — the stale one and the retargeted one — because the difference is the finding.
- [ ] T015 Commit phase 1 — `specs/050-chapter-4-5/baseline.txt` only. No platform change yet.

---

## Phase 2: User Story 1 — the records exist (Priority: P1)

**Goal**: a connection opening and closing puts two records on the stream.

**Independent test**: open and close a known number of connections, then read the stream
directly and count the open and close records. Nothing consumes them yet.

**Why the table does not exist yet**: see the note at the top of this file.

- [X] T016 [P] [US1] Add `CONNECTION_OPENED_ACTION`, `CONNECTION_CLOSED_ACTION` and their subject functions to `packages/protocol/src/internal.ts`, beside the webhook and api-request pairs, using `analyticsSubjectFor` unchanged.
- [X] T017 [P] [US1] Test them in `packages/protocol/src/internal.test.ts`: each subject matches `ALL_ANALYTICS_SUBJECT`, and a non-UUID environment is **refused**. Assert the refusal, not only the success.
- [X] T018 [US1] Add `nats` at **`^2.29.3`** to `services/gateway/package.json` and record the new dependency count in `specs/050-chapter-4-5/baseline.txt`. **5 → 6**, and T001's number is what it is compared against. The version is the one `services/api`, `services/dispatcher` and `services/ingester` already pin; **there is no pnpm catalog in this workspace**, so nothing makes four packages agree except typing the same string, and `pnpm add nats` would resolve to whatever is current. Constitution VII is the argument: the same client three other services hold is boring, a fourth major version is not. **This file is fenced ten times** (T010a) and owes a hunk.
- [X] T019 [US1] Write `services/gateway/src/connection-log/event.ts`: `toConnectionEvent()` building each record by **naming every field**. A spread would carry a socket, an identity or a token onto a stream with seven-day retention; an allow-list fails closed when somebody adds a field.
- [X] T020 [US1] Discharge **FR-005a**: the open record's `ts` is **`connection.openedAt`**, the field the meter reads — not `new Date()` at hand-over. It is stamped two lines before `registry.add`, *"BEFORE the resume and before the ack, because the socket is already open and already costing a minute"*. Two instants for one open would make T073's reconciliation disagree for a reason the chapter does not explain.
- [X] T021 [US1] Assert in `services/gateway/src/connection-log/event.test.ts` that no credential, token, channel list or message content can reach the record — **by handing the shaper a real `Connection`, not a synthetic object carrying four invented fields.** All four are genuinely on it: `identity.token` is the bearer token the client presented (`api-client.ts:70-73`), `buffer` holds frames, `channelIds` is the channel list, and `socket` is the socket. Check the serialised output for each.
- [X] T022 [US1] Write the buffer in `services/gateway/src/connection-log/event.ts`: records accumulate and a tick publishes them. **Not one publish per close** — T004's 0.229 ms is 2.3 s for 10,000, which is `session.ts`'s own HTTP argument on a new transport.
- [X] T023 [US1] Discharge **FR-004c**: **name the flush interval and show the budget.** FR-ANL-04 allows 60 seconds from the event to it being queryable and the ingester's `BATCH_MS` spends up to 2. **Do not copy `METER_INTERVAL_MS`** — 60,000 ms breaches the clause before the record leaves the gateway, and it is the obvious number precisely because this chapter's posture is *be like the meter*. The meter feeds a monthly quota with no latency clause over it; this feeds a store that has one.
- [ ] T024 [US1] Record why a short interval costs nothing in `specs/050-chapter-4-5/baseline.txt`: the tick's win is removing the serial round trip from whatever accumulated, not waiting longer — 0.0034 ms a record at any interval — and R3's 2.3-second burst is a property of publishing **per close**. `5_000` ms is the proposal; whatever is chosen, write down what it spends.
- [X] T025 [US1] Discharge **FR-004a**: **bound the buffer.** An unreachable broker means records accumulate without leaving, and an unbounded buffer on a service holding 10,000 sockets is an out-of-memory that closes every one of them — FR-004 satisfied at the record level and violated at the service level. `meter.ts` caps at `MAX_RETAINED_CLOSED = 4_000`; pick a number and argue it the same way.
- [X] T026 [US1] Discharge **FR-004b**: **count the drops and name the direction.** Dropping the oldest loses the earliest events; dropping the newest loses the ones describing the outage. The meter drops the oldest because *"under-counts … is the same direction as every other loss in this design"* — say whether that argument transfers here, because a connection log is not a bill.
- [X] T026a [US1] Discharge **FR-004e**: a record whose publish **failed** goes back in the buffer and is retried on the next tick, inside T025's bound. Read `meter.ts`'s rule before copying its number: *"a report that cannot be delivered is DROPPED rather than queued"* — **with one exception**, *"a connection that has CLOSED has no next report to repair a lost one, so its final total is retained until a report carrying it is accepted"*, and `reportOnce` deletes a closed entry only after `api.reportUsage` returns. **Every connection event is in that exception**: an open is sent once, a close is sent once, and neither has a later report carrying it again. Record in `specs/050-chapter-4-5/baseline.txt` that the cap this chapter copied bounds a RETRY QUEUE, not a flush buffer, and that the two only mean the same thing once this task is done.
- [X] T026b [US1] Discharge **FR-004f**: collect the flush's outcomes **per record** — `allSettled` over the in-flight publishes, not one try/catch around the flush. One message per record means 500 outcomes, and the meter never has to do this because it sends one report and gets one answer. Assert in a test that a flush where some publishes fail retains exactly the failed records and drops none of the accepted ones.
- [X] T027 [US1] Test the bound red: fill the buffer past its cap with the broker unreachable and assert the drop counter moves and memory does not. **A cap nothing has ever reached is a cap nobody has tested** — and until T026a the buffer could not fill at all, because a flush that discards on failure empties it every tick whatever the broker is doing.
- [ ] T028 [US1] Discharge **FR-004d**: **measure** the end-to-end latency — one connection closing to its row being readable — and publish it against FR-ANL-04's 60 seconds. Derived arithmetic is not a measurement, and this chapter is the first in Part 4 where the clause can be breached at all.
- [X] T029 [US1] Publish **one JetStream message per record**, pipelined — up to 500 in flight, acks collected together — which is the form T004 measures. Not core publish: 0.0030 ms against 0.0034 buys nothing and gives up the ack and the deduplication id, and this stream exists to be recoverable, which is why 3.20 chose JetStream over core. **And not 500 records in one message**, which three artifacts said before analysis pass 5: one message carries one subject and the subject carries the tenant; one message carries one `Nats-Msg-Id` and the dedup id is `{connection_id}:{event}`; and `route()` takes one record per message.
- [X] T029a [US1] Falsify the batched-payload form against the real router before trusting the paragraph above. Hand `route()` an array of connection records and record what comes back: it has no `type`, takes the attempt arm, `shape()` returns `null`, and `ingest.ts` calls **`m.term()`** — 500 records destroyed and counted as one malformed. Record the result in `specs/050-chapter-4-5/baseline.txt`. **This is the reason R8's `unclaimed` window works at all**: the arm that retains a record is reached by a record with an unrecognised `type`, not by a batch.
- [X] T030 [US1] Write `services/gateway/src/connection-log/publisher.ts`: **one** client, created once, shared, lazily connected. An unreachable broker must leave the gateway serving sockets, which is the same posture every other publisher in this platform takes.
- [X] T031 [US1] Hand over in `services/gateway/src/session.ts` at **two different anchors**, because the meter is asymmetric by design: the open beside `registry.add(connection)` (`session.ts:959`) and the close beside `meter.closed(...)` (`session.ts:1146`). **There is no `meter.opened`** — the `Meter` interface is `closed`, `reportOnce`, `retained`, `dropped`, `stop`, and it learns about open connections by walking the registry. Not inside the meter either: its contract is connection-minutes for a quota and it is fenced in 3.24.
- [X] T032 [US1] The close-side hand-over must not throw and must not await. `session.ts`'s close handler is documented as the last place that should throw — **assert that in a test rather than trusting the comment**, by making the publisher throw and checking the socket still closes cleanly.
- [X] T033 [US1] Wire the publisher's lifecycle in `services/gateway/src/main.ts`, and **close it AFTER `sessions.close()`** in `shutdown()`. That function closes seven things in a stated order and this makes it **eight**; `sessions` is first *"because its close is the one with work to finish … the fabrics it reports and publishes through have to still be open while it does that"*, and the flush of this buffer is exactly that kind of work.
- [X] T034 [US1] Record the shutdown list's length before and after in `specs/050-chapter-4-5/baseline.txt`. The file's own warning applies: *"A `shutdown` that closed three of seven would leak four per deploy — and `main.ts` is excluded from the coverage ratchet, so no figure could show it."* **Nothing will catch a missed close**, so the count is the check.
- [ ] T035 [US1] Record what a clean stop does to in-flight records in `specs/050-chapter-4-5/baseline.txt`, and what a killed process does. The second is the number a dashboard has to tolerate.
- [X] T036 [US1] Discharge **FR-006** by recording in `specs/050-chapter-4-5/baseline.txt` that the unauthenticated-socket case **cannot arise at either anchor**, with the lines that decide it: `open()` (`session.ts:912`) takes a non-optional `identity: Identity` and is the only builder of a `Connection`; its one call site reaches it only after the 429 upgrade refusal, 4001, 1011, 4003 and 4008 have each returned. **This is not a decision to make, it is one already made** — by the anchor choice, which the plan argues for on the meter's asymmetry and not on this. Record the five refusal paths, because the question a reader will ask is why an unauthenticated socket can exist and an unauthenticated connection cannot. **A design in which a case cannot arise beats a branch that handles it**; what this task produces is the evidence, not the branch.
- [ ] T037 [US1] Write `services/gateway/src/connection-log/connection-log.itest.ts`: open and close N connections, read the stream directly, assert 2N records **against a non-zero floor**. A three-way equality at zero is satisfied by nothing at all. **Say how N is distributed across users, because five is a ceiling.** `MAX_CONNECTIONS_PER_USER = 5` (`connections.ts:12`) is enforced by claiming one of five slot keys in Redis — per user per environment, across instances — and the sixth socket is refused with close **4004**. That refusal returns before `open()`, so it produces no `Connection`, no registry entry and **no record at all**, the same way the unauthenticated case does. A test that opens ten sockets as one user asserts 20 and measures 10, and the failure reads as ten lost records rather than five refused connections. T054 and T055 inherit the same N.
- [ ] T038 [US1] Assert in the same test that the records are **left on the stream** by the existing ingester rather than terminated — 4.4's `unclaimed` arm, exercised on a real record. Run `ingestOnce` twice across `ack_wait` and show the count comes back.
- [ ] T039 [US1] Run `pnpm lint`, `pnpm typecheck`, `pnpm test` **and `pnpm test:integration`**. Record failures in `specs/050-chapter-4-5/baseline.txt` rather than only the green run. **The fourth is not optional here**: `.itest.ts` files run under `vitest.integration.config.mts`, which `pnpm test` does not load, so T037's stream assertions execute only under the integration lane. **No task in this feature ran it until analysis pass 14** — the chapter's central evidence had no gate.
- [ ] T040 [US1] Commit phase 2.

---

## Phase 3: Foundational — the table and the third arm

**Blocking for phase 4.** The `unclaimed` window measured in phase 2 closes here.

- [ ] T041 Record the `unclaimed` count the ingester reported while phase 2's records had no table, in `specs/050-chapter-4-5/baseline.txt`. **This is the number the window existed to produce**, and it is gone once the table lands.
- [ ] T042 Write `analytics/0005_connection_events.sql` per `data-model.md` §1. One statement, qualified `relay_analytics.` — `apply.mjs` refuses both otherwise.
- [ ] T043 Put `event` in the sorting key after `connection_id`. **One connection produces two rows with one `connection_id`**, and without it a `ReplacingMergeTree` collapses the open into the close. Verified against the server during planning: `count() FINAL` 2, not 1.
- [ ] T044 Use `TTL toDateTime(ts) + INTERVAL 90 DAY`, not `TTL ts + INTERVAL` — 047 measured the second refused with `BAD_TTL_EXPRESSION` on a `DateTime64`. **And record that 90 is a default rather than a derivation**: FR-ANL-07 fixes 30 for the request log and nothing fixes this one.
- [ ] T045 Give `close_code` the type **`Nullable(UInt16)`**, not a string. A close code is a small integer, and a String column answers `WHERE close_code = 1000` with nothing and no error. **Measured: ClickHouse coerces a JSON number into a String column AND a JSON string into a UInt16, so a type disagreement between the producer and the table lands silently.** The other close-only column, `duration_ms`, is **`Nullable(UInt64)`** per `data-model.md` §1 — UInt32 milliseconds wraps at 49.7 days and nothing caps a socket's lifetime, the only lifetime control being `MAX_MISSED_PINGS` on a 30 s ping, which ends a socket that has stopped answering rather than one that has not. An open record carries neither column.
- [ ] T046 Include the `ts_is_real` CHECK constraint. 048 measured that an absent column takes its default, a `DateTime64` default is the epoch, and the epoch is older than any TTL, so the row is deleted at insert while the insert returns OK.
- [ ] T047 Run `node analytics/apply.mjs` and record `applied 1: 0005_connection_events.sql`, then a second run reporting `applied nothing`. **Capture the exit code outside any pipeline** — 049 read it through `| sed` twice and got sed's status.
- [ ] T048 [P] Test the checksum refusal red: change one byte, re-run, record the refusal text, restore.
- [ ] T049 Add the third arm to `services/ingester/src/shape.ts`'s `route()` and a `shapeConnection()` that **drops `type`** — the wire carries it and the table has no column, and forwarding it lands `Code: 117`.
- [ ] T050 Add a third buffer to `services/ingester/src/ingest.ts` and insert before any ack, as the other two do. Record whether three buffers on one fetch changes the batching picture 049 measured — the empty-buffer guard is what carries it. **And correct the comment above `BATCH_ROWS` while you are in the file**: it reads *"DR-11 publishes 2 s or 10,000 rows"* and **DR-11 says neither number**. In full: *"Inserts shall be batched or use asynchronous insert mode; single-row synchronous inserts are prohibited."* The figures are `docs/05-sad.md:182`'s, which credited them to DR-11; the code then states them as the requirement's own. `ingest.ts` carries **no titled fence** (T010a), so the edit costs the chain nothing.
- [ ] T051 Extend `services/ingester/src/clickhouse.ts` with the third table, keeping `input_format_skip_unknown_fields=0` and `date_time_input_format=best_effort`.
- [ ] T052 Verify the table against `data-model.md` with `SHOW CREATE TABLE relay_analytics.connection_events` and record it. **Ask the database rather than reading the file you just wrote** — 049 found the server normalising two spellings that way.
- [ ] T053 Run the four lanes — `lint`, `typecheck`, `test`, `test:integration` and commit phase 3.

---

## Phase 4: User Story 1 — the records land (Priority: P1) 🎯 MVP

**Goal**: a connection that opens and closes becomes two rows in the analytical store.

**Independent test**: open and close N connections, drain, count rows with `FINAL` against a
non-zero floor, and show one connection's pair as two rows rather than one.

- [ ] T054 [US1] Extend `services/gateway/src/connection-log/connection-log.itest.ts`: after draining, count rows for the test's own environment and assert 2N.
- [ ] T055 [US1] Assert one connection's pair is **two rows**, with the open carrying no `close_code` and no `duration_ms` and the close carrying both. That is the `event`-in-the-key decision, checked rather than assumed.
- [ ] T056 [US1] Discharge **FR-014**: insert the same close record three times and assert physical `count()` 3 against `FINAL` 1, with `SYSTEM STOP MERGES` on the table. **A physical count taken while a merge runs measures the merge** — 049's own first probe read 2 after six inserts. **Copy the whole of 049's shape, not the half that names the hazard** (`services/ingester/src/ingest.itest.ts:281–318`): stop merges, then `try`, and in a **`finally`** both `SYSTEM START MERGES` **and** `DELETE FROM … WHERE environment_id = toUUID('<the probe's own id>')`. **Scope both counts by a dedicated environment id**, the way `RED_ENV` does — a bare `count()` is a whole-table assertion and this lane runs **four files at a time** (`maxWorkers: 4`), which is the class 045-74 found eight of. An earlier version of this task named only the stop, which is the one step with a lane-wide side effect: a failed assertion between stop and end leaves `connection_events` never collapsing duplicates for T054's counts and for the quickstart's `FINAL` query. **Clean up a probe before anything is counted** (043).
- [ ] T057 [US1] Assert the tenancy branch in `services/gateway/src/connection-log/event.test.ts` and publish the measured branch coverage beside constitution VI's 100%, met or pinned with the shortfall stated as a number.
- [ ] T058 [US1] Pin the new files in `vitest.coverage.config.mts` with freshly measured numbers, and **run both halves of the threshold probe** — demand 101%, confirm red, restore, confirm green. 049 found a pin that could not fail because its key was excluded from collection. **This edit costs the fence chain and cannot be paid with a hunk** (048-3, and T010b's reading): the file carries 23 fences and the chain replays a third of the lines the tree holds. Run `pnpm check:fences` straight after this task rather than at T094, and record the delta this one file causes on its own.
- [ ] T059 [US1] Sweep every per-file pin against the exclude patterns and record the count. 049 measured 45 pins, 1 unbindable, then 0.
- [ ] T060 [US1] Run the quickstart's §4 block verbatim and record its output. **Rebuild the gateway image first** — 049's equivalent measured the old image and produced no rows at all.
- [ ] T061 [US1] Run `specs/045-part-3-rework/check-lane-scope.py` **retargeted per T014** after adding the integration tests, and record its report **with a caption saying what its zero covers**. Its `SHARED` array is the lane's **Postgres** tables — `organisations`, `applications`, `environments`, `channels`, `messages`, `outbox`, … — and `relay_analytics.connection_events` is in neither that list nor that database. Its own closing line is *"SQL text only — a scope applied in JavaScript is invisible to it."* **So this chapter's only whole-table risk is the one the tool cannot see**, and T056 is where it is actually handled. T014 stops the tool reporting zero because it looked at nothing; this stops the zero being read as a claim about ClickHouse.
- [ ] T062 [US1] Run the four lanes — `lint`, `typecheck`, `test`, `test:integration` — **and `pnpm coverage`**, which is the only thing that enforces T058's freshly-measured pins and is in no other gate. Commit phase 4. **MVP ends here**, so this is the last gate before three phases that can break `connection-log.itest.ts` without any of them noticing. Coverage is also not reproducible run to run — about one function of forty on `session.ts` — so record the numbers, not just the pass.

---

## Phase 5: User Story 2 — the gateway keeps serving when the broker is gone (Priority: P1)

**Goal**: sockets connect, carry messages and close normally with the broker unreachable.

**Independent test**: two distributions of connection latency, broker up and stopped, with the
per-connection outcomes published beside them.

- [ ] T063 [US2] Verify by **inspection** that no publish is awaited in a socket handler, and record the call sites. A timing test passes on a fast broker whether or not the await is there.
- [ ] T064 [US2] Measure connection open-to-ready latency with the broker healthy — a warm-up, then the sample — and record the distribution. 046 published a wrong number twice by comparing a cold run against a warm one.
- [ ] T065 [US2] Stop NATS and repeat. **Stop the gateway's writers first if the stack must survive**: 049-1 measured that the stream being written when the broker restarts is the one that fails to recover, graceful or not.
- [ ] T066 [US2] Record the **connection outcomes** during the broker-down run, not only the latencies: how many opened, how many carried a message, how many closed cleanly. A connection that is fast and refused satisfies a timing assertion.
- [ ] T067 [US2] Confirm the publish failure is logged once per flush rather than once per record, and that the line carries no payload, no token and no channel list. The line reports the **counts** T026b collects — accepted, failed, retained — which is the meter's own shape: `meter.report_failed` carries `connections`, `retained` and the error and nothing else.
- [ ] T068 [US2] Restart NATS and confirm `/healthz` is `{"status":"ok"}` and the container healthy, **by a deliberate restart** — 048-6's lesson, and 049 found that check failing for a reason 048-6 had recorded wrongly.
- [ ] T069 [US2] Record what the gateway's RSS looks like after the sixth dependency. **Cite the source that holds the number**: NFR-SCL-01 is one sentence about 10,000 concurrent connections and carries **no memory figure** — the 160 MB is SRS **revision 1.9** and `docs/11-scalability-measurement-2026-09-06.md`, which measured **157 MB against a 160 MB budget** and recorded ADR-25's revisit threshold. Compare against 157, not against the rounded ceiling. **If the battery is not run, say that the figure is unmeasured rather than implying it holds** — and note that `docs/11`'s nearest published analogue for one more thing in the gateway is *"a sixth grammar costs about 3 MB in the worst ratio."*
- [ ] T070 [US2] Run the four lanes — `lint`, `typecheck`, `test`, `test:integration` and commit phase 5.

---

## Phase 6: User Story 3 — the quota path is unchanged (Priority: P1)

**Goal**: connection-minutes still reach Postgres the way they did, and the two counters can be
compared.

**Independent test**: the existing meter suite passes untouched, and the quota counters move by
the same amounts as before the chapter.

- [ ] T071 [US3] Run the meter's existing suite and record that it passes **unmodified**, with the file's git status proving it was not edited. Verification method T, and an untouched suite passing is the only evidence that means anything here.
- [ ] T072 [US3] Record the quota counters before and after a known workload, and show they move by the same amounts as a run of the same workload from `part4-ch4`.
- [ ] T073 [US3] Discharge **FR-009**: derive minute buckets from the open and close records and compare them against what the meter reported for the same connections. **Compare buckets against buckets** — one quantity computed twice.
- [ ] T074 [US3] Discharge **FR-009a**: scope the comparison to **connections with both records present**, over a window every one of them closed inside. `reportOnce` builds its report from `[...closedNow, ...open]` — **the meter bills connections that are still open** — and a connection with no close record can derive nothing. Unscoped, the two sides differ by every open connection: a third cause in a comparison built to have two.
- [ ] T075 [US3] Discharge **FR-009b**: split derived buckets **by period**, as `entriesFor` does. A socket open across a month boundary owes minutes to two periods, credited independently, and a derivation that does not split the same way disagrees for a fourth reason.
- [ ] T076 [US3] Publish the **duration-against-buckets** gap as a number in `specs/050-chapter-4-5/baseline.txt`, with the worked example: a connection open 00:00:59 to 00:01:01 is 2 connection-minutes and 2,000 ms. **They are different quantities sharing a name**, and the chapter says so rather than letting a reader treat the difference as a defect.
- [ ] T077 [US3] Record any connection where the two bucket counts disagree, with the cause. A disagreement there **is** a defect, unlike the one above.
- [ ] T078 [US3] Measure the open/close **balance** for a clean run and for a killed gateway. A killed instance produces opens with no closes, and the number is what a dashboard built on these records must tolerate.
- [ ] T079 [US3] Run the four lanes — `lint`, `typecheck`, `test`, `test:integration` and commit phase 6.

---

## Phase 7: User Story 4 — ADR-07 says what it now rests on (Priority: P2)

**Goal**: a reader of ADR-07 can tell why NATS is still not the fan-out fabric, given that the
gateway now holds a NATS client.

**Independent test**: the amendment exists, names the spent argument, and states the surviving
one. Verification method **I**.


- [ ] T080 [US4] Correct **ADR-07** in `docs/05-sad.md`, and **read its body before writing a word** — four artifacts quoted the v1.1 amendment for nine passes and none opened the paragraph it amends. The body's rejected list already says *"Redis is mandatory for the gateway regardless, since ADR-10 puts presence in Redis with TTLs"*, so that is not a reason to restore. **The clause this chapter falsifies is the one beside it**: *"so fan-out on NATS would leave that service holding two broker clients and remove none."* The gateway holds two anyway now, so NATS fan-out would add none and remove none — **the cost side of the refusal is zero**, and the refusal survives on Redis's mandatory-ness alone. v1.1's "how many client libraries" framing is that same clause restated and goes the same way.
- [ ] T080a [US4] Discharge **FR-016a**: **choose the form and say why**, in `specs/050-chapter-4-5/baseline.txt` and in the record itself. Constitution VII: *"ADRs are immutable once accepted; superseding requires a new ADR."* ADR-07 carries **both** forms — in-place amendments dated 2026-08-04 and 2026-09-03, and the status line *"extended by ADR-20 (chapter 3.20) … and by ADR-22 (chapter 3.21)"*. So precedent does not decide it and the constitution names only one. VII's closing line, *"disagreement attacks the driver, not the choice"*, is the argument for a new extending ADR here: **what changed is a driver's price, not the decision**. Whichever is chosen, the governance clause requires it stated rather than assumed.
- [ ] T080b [US4] Amend **ADR-07 in `docs/06-adr-deep-dives.md`** (line ~401), which is where the argument lives — the SAD carries the summary. 98 lines of Options/Analysis/Decision/Consequences/Revisit-when, with a dated amendment block of its own from chapter 3.20, and **no task opened it before analysis pass 13**. Two lines of the Analysis stop being true: *"fan-out on NATS gives the gateway two broker clients where it had one"* and *"Choosing Redis keeps a clean mapping — gateway to Redis, api and workers to NATS."* **Follow 3.18's amendment, which is the paragraph directly below and did this from the api's side**: it leaves the Decision and the Revisit-when clauses explicitly untouched, and says only that *"the selection argument's tidiest line is no longer literally true, and a reader comparing it against `05-sad.md`'s component diagram deserves to be told so rather than left to reconcile them."* That paragraph also supplies this chapter's best sentence, already written about the api: the two-client cost was *"relocated rather than avoided."* **It is now on the gateway as well, which is where the analysis refused to put it.**
- [ ] T081 [US4] Bump the SAD's version and run `pnpm sync:docs`. `check:docs` failed after a SAD amendment in 047, 048 and 049.
- [ ] T081a [US4] Amend **DR-11** in `docs/04-srs.md` to carry the bounds the platform actually runs, with the measurement behind them. It reads *"Inserts shall be batched or use asynchronous insert mode; single-row synchronous inserts are prohibited"* — no interval and no row count — while `docs/05-sad.md:182`, `ingest.ts` and this feature's contract all attribute **2 s or 10,000 rows** to it. 049 measured why both are needed and where they cross: a row count never flushes for a quiet tenant, an interval has no ceiling under load, and **the crossover is 5,000 records/second**. This is the governance clause's case exactly — a document that disagrees with the tree gets amended rather than worked around — and it is a clause gaining a number it never had rather than a measurement falsifying one. Bump the SRS revision and re-run `check:docs` and `check:srs`.
- [ ] T081b [US4] Discharge **FR-017a** for `docs/05-sad.md` **§6.2**: add `relay_analytics.connection_events` as the fifth analytical table, in the form §6.2 already uses. The precedent is doubled and explicit — *"AND THE DELIVERY-ATTEMPT TABLE, ADDED IN REVISION 1.3"* (because the document *"named no table for FR-ANL-01's webhook delivery attempts"*) and *"AND THE API REQUEST LOG, ADDED IN REVISION 1.4"*. **This is the same series' next entry and the same clause's last arm.** Carry the decisions §6.2 records for the other two: `event` in the sorting key because one connection makes two rows under one id; `environment_id` **not** nullable, unlike `api_requests`, and why; `Nullable(UInt16)` for a close code a String column would answer with silence; `UInt64` milliseconds because nothing caps a socket's lifetime; and 90 days as a default rather than a derivation.
- [ ] T081c [US4] Discharge **FR-017a** for `docs/05-sad.md` **§4's gateway entry**, which will otherwise describe a service that publishes analytical events and holds a broker client while mentioning neither. The dispatcher's entry already carries the sentence to copy: *"Records every attempt as an analytical event (FR-WHK-06)."* **And add the report that was already missing**: the entry lists JWT validation, slot claims, Redis subscription, resume through the api and frames over internal HTTP, and says nothing about `/internal/usage/connections` or the sixty-second meter. That is spec.md §2's framing finding — *"`docs/12` does not say the gateway already reports connection data"* — true of this document too, and T085 only amends `docs/12`.
- [ ] T082 [US4] Grep the spent argument everywhere before calling it done — `docs/`, `specs/`, both tutorial locales. **Fix the file that describes the thing and the one that instructs it.**
---

## Phase 8: The numbers, the amendments, and the chapter

- [ ] T083 [P] Measure the combined byte rate of all three producers on the shared stream and restate the crossover. 4.4 measured 320 bytes a request record, 5.5 req/s for seven days and 38.8 for the SAD's 24 h. **Measure against a length-matched subject** — 4.4's first figure was 2% light for including the probe's own shorter subject.
- [ ] T084 [P] Measure the connection-event rate against the request-event rate and record it. `research.md` R7 **assumed** connection events are rarer and did not measure it; if a reconnect storm makes them commoner the crossover moves.
- [ ] T085 Amend `docs/12-part-4-structure.md` §3's one-line description of this chapter, which says the gateway has never touched NATS and does not say it already reports connection data every sixty seconds. **And fix §3's heading while you are in it**: it reads *"seven movements, 23 chapters"* where the section's own 2026-09-13 amendment says *"23 BECAME 22"*, its milestones are *"9, 17 and 22"* and its map ends `VII ch 18–22`. The second contraction updated everything in the section except the line naming the number. **Leave the table's first column alone** — §3 says it keeps the original ordinals on purpose, so references written against them still resolve, and the movement column is the stable address.
- [ ] T085a **Close `docs/12-part-4-structure.md` §7.2, which this chapter owns.** §7 is *"Open questions, each owned by the chapter that needs it"*, and 7.2 is *"ADR-07's second amendment (ch 6)"* — ch 6 being this chapter in §3's pre-contraction ordinals. Its text is the brief: *"Chapter 3.18's amendment already recorded that this stopped being exactly true in 3.8. **Giving the gateway a publisher amends it again, and that is a chapter's worth of argument rather than a line of wiring.**"* The precedent for closing one is §7.1: it belonged to the ledger chapter, 4.2 built all four items of its brief, and §3's 2026-09-13 amendment records the closure in the section itself. **T085 amends §3's row and nothing touched §7 until analysis pass 13.**
- [ ] T086 Draft the chapter at `relay-tutorial/app/(en)/part-4/chapter-05/the-gateways-first-stream/page.mdx`. The slug is kebab-case of the title's main clause with the apostrophe **dropped**, as `the-question-the-counters-cant-answer` does it, and it must match the manifest's `path` and the MDX `metadata.alternates` exactly. **Do not re-derive** 3.20's fire-and-forget argument, 4.3's routing or 4.4's tenantless rule. **At least one `<Trap>`**, which `docs/07` §line 70 makes a counted box class per code chapter; T091 counts them. This chapter has candidates already measured — the batch of 500 the ingester terminates as one, the meter's cap that bounds a retry queue rather than a flush buffer, and a citation that points at a clause saying otherwise.
- [ ] T086a **Register the chapter in `relay-tutorial/lib/tutorial.ts`.** It is *"the single source of truth … the landing table of contents, ChapterHeader, and ChapterFooter all render exclusively from this manifest"*, and `<ChapterHeader id="4.5" />` calls `getChapter("4.5")`, which **throws** on an unregistered id. Fill `id`, `path`, `title`, `status: "published"`, `readerProduces`, `sourceDoc` and `readerMinutes` — 4.1 and 4.3 are 55 minutes at ~2,100 words, 4.2 is 60 at 2,580. Leave `titleVi`, `readerProducesVi` and `translatedIn` to the translator: `translatedIn` is the only signal a vi BODY exists, and claiming one that does not is worse than an English fallback. **Do this after T086**, because an entry whose page does not exist breaks the build in the other direction. The file carries no titled fence, so it costs the chain nothing — measured, 110 before and after.
- [ ] T087 Discharge **FR-008**: state in the chapter why BOTH paths exist and **what each cannot do** — and **cite `docs/12` §4 rather than re-deriving it**. Its subsection *"FR-ANL-06 has a concrete counterpart, and it is Part 3's"* already argues the whole thing: *"a quota must refuse a send synchronously, so its counter cannot live downstream of a lossy stream"*, hence *"Two counters of one quantity is the right answer and the reconciler is the price."* §4 is the section headed **"Chapters must not re-teach these"**, and FR-018 already forbids re-deriving two of its three neighbours. The meter cannot say a connection existed, only how many minutes it owed; the records cannot refuse a connection, because a quota refusal is synchronous and these are not. Name both limits rather than implying the new path supersedes the old.
- [ ] T088 Say plainly that `close_code` is **not** drawn from `CLOSE_CODES`. That registry is the platform's own 4001–4009 and a clean close is 1000, so `check:errors` does not guard this column — the claim that it did was in two artifacts before analysis pass 1 ran.
- [ ] T089 Put every mermaid source in `figures.ts`, never in `page.mdx`, and pass each to `<Figure>` as **`code=`**, not `chart=` — 049 shipped three as `chart` and `check:figures` named every line.
- [ ] T090 Take every number in a figure from `specs/050-chapter-4-5/baseline.txt`. No checker reads prose, and a mermaid block is prose.
- [ ] T091 Measure prose words outside code fences against the 2,000–4,000 bound and record the figure whether or not it forces a split. **Count the `TRAP` boxes in the same pass.** `docs/07-tutorial-plan.md` §line 70 makes it a counted box class at **≥1 per code chapter**, and **no gate counts it** — `check:figures` counts figures and no checker reads prose, so this rule has been honoured by habit for every chapter and could be missed by one draft. 4.4 carries four.
- [ ] T092 Publish the SQL file as a whole body — it is new — and everything else as `diff` hunks against `part4-ch4`. **The set is T010a's eight minus the one that cannot take a hunk**: `session.ts`, `internal.ts`, `main.ts`, `services/gateway/package.json`, `internal.test.ts`, `clickhouse.ts` and `shape.ts`. `ingest.ts` needs none — it carries no fence. `vitest.coverage.config.mts` gets a gaps entry instead, and a whole body would be the 111 → 203 trap.
- [ ] T093 Generate the hunks from the checker's own replay, or from `git diff -U6 part4-ch4 -- <file>` where the file has not changed since that tag. **Verify they apply before pasting, not after.** `docs/07` §line 70 says *"three lines of context"* and practice settled on six, because the rule that actually matters is in the same sentence — **each hunk's pre-image matching in exactly one place, since an ambiguous hunk proves nothing.** Three is a floor, not a target: widen past six when a pre-image matches twice, and note that `-U8` measured *worse* than `-U10` once, because widening merges adjacent hunks and a merged hunk spans more repetition than either half did.
- [ ] T094 Run `pnpm check:fences` and report the close as a **delta against T010's opening**, broken down by kind and locale. **Expect the vi half to move and say by how much**: T010c's whole bodies for `shape.ts` and `clickhouse.ts` break when T049 and T051 land, and no English hunk repairs a Vietnamese fence. A delta of 0 here would mean something is wrong with the measurement, not that the chapter was free.
- [ ] T095 Run all **eleven** gates: `check:fences`, `check:docs`, `check:srs`, `check:figures`, `check:errors` and **`pnpm build`** in `relay-tutorial`, then `lint`, `typecheck`, `test`, **`test:integration`** and **`coverage`** in `relay-platform`. **The last two are new, and between them they run every test this chapter writes**: `.itest.ts` files load `vitest.integration.config.mts`, which `pnpm test` never opens, and `coverage` is the only lane that enforces the per-file pins. Nine gates would have shipped this chapter with its own integration suite unexecuted. **Build before `check:errors`** — that one reads the built `dist`. **`pnpm build` is new and it is the one that would have caught 4.4.** The other five compare bytes and identifiers; none of them renders a page, so a chapter missing from the manifest passed all of them and broke the site. It runs in about 90 seconds and its failure names the page: `Error occurred prerendering page … Unknown chapter id: 4.4`.
- [ ] T096 Write `specs/050-chapter-4-5/gaps.md` for everything found and not closed, each entry naming what it would cost to close. **Re-measure all eleven carried items and say plainly what each one is now** — 049-1 through 049-6 and 048-1 through 048-5. This task named three of 049's six until analysis pass 7 counted them, and **049 itself dropped 048-1 to 048-5 without a word**: its file opens "Six entries" and never mentions the previous feature's open ledger. *Measure the carried ledger; do not copy it* — and 044's other half, *said plainly rather than implied by a short list*. **049-4 is this chapter's own subject**: it files the 5.5 requests/second crossover as unenforced, and FR-015 and T083 move that number. 048-3 is `vitest.coverage.config.mts`, which T010b and T058 make this chapter's problem again. **And open one for the analytical store's missing lane guard**: 4.2, 4.3, 4.4 and this chapter all write shared `relay_analytics` tables from integration tests, and nothing guards them. Postgres has feature 030's trigger, an exemption list asserted in both directions, and `check-lane-scope.py`; ClickHouse has none of the three, and this chapter performs a `SYSTEM STOP MERGES` on a table every later suite reads. **No gaps.md in 046 through 049 records it.** Name what closing it would cost — the cheapest honest version is probably a convention (a per-suite environment id and a `finally`) rather than a trigger, since the analytical store has no equivalent hook. **And open one for the Vietnamese whole bodies** (T010c): two fences this chapter breaks and cannot repair, because the repair is a Vietnamese chapter and the translation is not this feature's work. Name what it would cost — one vi 4.4 and one vi 4.5, or a decision to let the vi chain lag by design and say so once rather than per chapter.
- [ ] T097 Audit every test this feature added and confirm none asserts only that a record was published. Record the count audited.
- [ ] T098 Write `specs/050-chapter-4-5/traceability.md` mapping FR-001…FR-020 and SC-001…SC-011 to tasks and to the artifacts that discharge them. **Record the requirements nothing discharged**, if any.
- [ ] T099 Rewrite `CLAUDE.md`'s `<!-- SPECKIT -->` block for the close, including every task premise this feature falsified by running it.
- [ ] T100 Commit phase 8, tag `part4-ch5` on `relay-platform`, and push all three repositories.

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
- **US4** is the ADR amendment and needs only T001's and T018's dependency counts.

### Parallel opportunities

- Phase 1: T005–T014 are independent probes writing to separate sections, T010a–T010d included.
- Phase 2: T016 and T017 (protocol) run beside T019 (the shaper) and T021 (its allow-list test).
- Phase 8: T083 and T084 are independent measurements.

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
