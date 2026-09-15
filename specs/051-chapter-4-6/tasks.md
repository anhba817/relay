# Tasks — 051, chapter 4.6, "metering you can bill on"

**Input**: `spec.md` (21 FR, 13 SC), `plan.md` (8 phases), `research.md` (R1–R11, nine
measured), `data-model.md`, `contracts/metering-read.md`, `quickstart.md`.

**Read `research.md` before starting.** Three of its items changed what this chapter is, and
one of them — R9 — is the reason the phases below do not build a producer.

**MVP is phases 1–4**: a rollup with a named target, connection-minutes in it from the one
source that has a producer, and a read that answers from rollup rows.

**Commit each phase.** `git checkout` on a file with uncommitted work has destroyed work twice
in this project. Commits stay under five lines with no `Co-Authored-By` trailer.

**Run `pnpm check:fences` after any source edit**, not only at the ratchet.

**Capture every exit code outside a pipeline.** `fail=1` inside `for … | sort` runs in a
subshell and dies with it; 049 reproduced that twice in one feature.

---

## Phase 1: Premises, and the numbers this chapter is measured against

- [X] T001 [P] Re-run research R8's table census and record it in `specs/051-chapter-4-6/baseline.txt` as the OPENING figure: `message_events`, `api_requests`, `connection_events`, `webhook_attempts`, `daily_usage`. Planning measured 0 / 11,683 / 154 / 64 / 0. **Record the stream's depth in the same breath** (`curl -s localhost:8222/jsz`), because the two numbers only make sense together. **The tables move when an INGESTER DRAINS, not when the api serves** — an earlier draft of this task said the counts drift with `/healthz` polls, and analysis pass 7 re-measured them **identical to the opening after a full session of traffic, with 13,265 messages held on the stream and no ingester running**. So the opening is stable as long as nothing drains, and the next drain moves `api_requests` by the whole backlog at once. **A reader told the counts drift with traffic will attribute that jump to their own work.** It is also the chapter's cleanest demonstration that the analytical path is independent of the operational one: the api served all session and the store learned nothing.
- [X] T002 [P] Re-run R9 from both sides and record it: `grep -rln message_events` across the repository, and the same grep restricted to `services/`. The claim is *zero occurrences under `services/`*, and it is the chapter's spine — check it rather than cite the plan.
- [X] T003 [P] Re-run R5's both-records count and record it. Planning measured 55 / 44 / 99. **This number is a property of what has recently run on the stack**, not of the platform, so record the date and what produced the connections beside it.
- [X] T004 [P] Confirm R4: a close row's `ts - toIntervalMillisecond(duration_ms)` recovers the open instant, against three real rows. The metering read depends on the open record being unnecessary.
- [X] T005 [P] Measure the fence-chain OPENING with `pnpm check:fences`, **by kind and locale, and with the two HEAD classes split** — `differs at line` against `does not exist in relay-platform`. 050-4 measured 11 of the inherited 36 to be fences whose title names no file, so the headline is 11 units pessimistic and 25 is the number this chapter should be compared against.
- [X] T006 [P] Count the fenced-file exposure for **every file this chapter will touch**, in both locales, with `grep -rn '^```[a-z]* title=' "app/(en)" "app/(vi)"`. Planning measured `analytics/` at 5 fences, none on `0001_daily_usage.sql` or `apply.mjs`. **Count the list; do not carry it** — 050's remembered list was wrong in both directions and named a file carrying no fence at all.
- [X] T007 [P] For each fenced file T006 finds, record **which locale holds it and whether it is a whole body**. 050-3 measured that `check-fence-chain.mjs` never compares the vi chain against the tree, so a vi whole body this chapter breaks is invisible to every gate. Knowing this before phase 2 is the difference between a gaps entry and a surprise.
- [X] T008 [P] Run all eleven gates and record each colour in `baseline.txt` as the OPENING. Four api suites were red at 050's close for reasons no chapter caused — `request-log.itest.ts` (needs an ingester, 050-8), `limits.itest.ts` (`RELAY_INTERNAL_CREDENTIAL` unset), `session.perf.itest.ts` (a `Seq Scan` on an empty table) and an outbox concurrency flake. **An inherited red counted as a new one is a chapter blaming itself for somebody else's defect.**
- [X] T009 [P] Record `analytics/apply.mjs`'s ledger behaviour by running it twice on the unchanged tree: `applied nothing` the second time. Phase 2 depends on the ledger refusing an edited file, and a runner that silently re-applies would make `0001` editable after all.
- [X] T010 [P] Verify the ledger's checksum refusal **red**, in a scratch copy: change a byte of an applied `.sql`, run `apply.mjs`, confirm it refuses, then restore. 4.2 built that refusal and tested it red; this chapter's whole "new statement rather than an edit" premise rests on it, and a refusal nobody has seen fire is a promise.
- [X] T011 [P] Record the Postgres meter's opening: `select count(*), sum(messages_sent) from usage_periods`. Phase 8 shows it unchanged, and a diff proves the code is untouched while this proves the data is.
- [X] T012 Commit phase 1 — `specs/051-chapter-4-6/baseline.txt` only. No platform change yet.

---

## Phase 2: Foundational — the rollup table with a named target, and the view that waits for a producer

**Blocks every user story.** R1 measured that the four quantities can share one row only if a
named target table exists for several views to write into; R7 measured that 4.2's view owns an
implicit inner table and cannot be that target.

- [ ] T013 Decide and record in `baseline.txt` what happens to `daily_usage`: left in place beside the new table, or superseded. **A bare `DROP` of a source under a live view succeeds with no error and leaves an orphan answering queries with zeros** — 047 measured it, and recorded that the direction which errors is the safe one. Whichever is chosen, `0001` is not edited: the ledger keys on filename **and** checksum (T010). **If it is superseded, two consequences**: `analytics/query.mjs` stops working, because it reads `daily_usage` — verified as carrying no titled fence, so the chain is unaffected, but a file in the tree breaks silently and the chapter should say so rather than let a reader find it. And the `DROP VIEW` is its own numbered file — `apply.mjs`'s `check()` refuses a file holding two statements, in as many words, so it cannot ride along with `0006`.
- [ ] T014 Write `relay-platform/analytics/0006_daily_usage_v2.sql`: a `SummingMergeTree` **table**, not a view with an inline engine. Columns and types from `data-model.md`. `PARTITION BY toYYYYMM(day)`, `ORDER BY (environment_id, channel_id, day)`.
- [ ] T015 `stored_delta` is `Int64`, **not** `UInt64`. R2 measured `SummingMergeTree` summing a signed delta correctly; an unsigned column wraps on any day whose deletions exceed its creations, which is any day a tenant clears a backlog. Put the reason in the file, as every other statement in `analytics/` does.
- [ ] T016 `active_users_state` is `AggregateFunction(uniq, Nullable(UUID))`. **`Nullable`, and 046 is why**: a NULL `user_id` inserted into a non-nullable column becomes the zero UUID silently, which is one phantom active user per environment holding a deleted author's messages. 047 measured that `uniqState`/`uniqMerge` ignore NULL exactly as `uniqExact` does, so the fix survives into the rollup.
- [ ] T017 No TTL on the table, with FR-003a's reasoning stated in the file: `message_events` expires at 90 days and metering must not lose history when raw events do. **And record that this chapter widens 048-4's unbounded growth** — the key gains `channel_id`, so the product becomes `environments × channels × days`. T088 re-measures the carried item rather than inheriting its sentence.
- [ ] T017a Discharge **FR-001b**: write `relay-platform/analytics/0007_mv_messages.sql`, the second view, over `message_events`, writing `messages`, `active_users_state` and `stored_delta` into the same target. **Even though its source has no producer** — the view is what makes the rollup complete the day a producer exists, and R1 measured two views into one target summing correctly. **It is built in phase 2, not later**: the corpus proof at T035a-T036b is the only window in which these three columns can be checked against raw data, and a corpus that flows through a rollup with no message view proves nothing.
- [ ] T017b `stored_delta` is `multiIf(event='created', 1, event='deleted', -1, 0)`. **`edited` contributes 0 and that is a decision**: an edit changes a message's text and not whether it is stored. R2's probe carried an edit row for exactly this reason.
- [ ] T018 Apply them: `node analytics/apply.mjs`. **Expect `applied 2`** — `0006_daily_usage_v2.sql` and `0007_mv_messages.sql`, in that order, because `apply.mjs` sorts filenames and the table must exist before a view targets it. Then `applied nothing` on a second run. Record both lines. **A task that tells you what to expect and is wrong trains you to skim the output**, which is how 048's rename shipped looking like success; this line said `applied 1` until the message view moved into this phase.
- [ ] T019 Verify against the server rather than the file you just wrote: `SHOW CREATE TABLE relay_analytics.daily_usage_v2`, and confirm the engine, the key and every column type. 4.5's T052 is the precedent — ask the server.
- [ ] T020 Run `pnpm check:fences` and record the delta. A new file costs the chain nothing (R11), so expect 0; a non-zero here means something else moved and phase 2 is where it is cheap to find.
- [ ] T021 Run the four lanes — `lint`, `typecheck`, `test`, `test:integration` — and commit phase 2.

---

## Phase 3: User Story 1 — connection-minutes, from the source that has a producer (Priority: P1)

**Goal**: the one FR-ANL-05 quantity this chapter can populate from live traffic lands in the
rollup.

**Independent test**: open and close connections, drain, and read connection-minutes for that
environment and day from rollup rows.

- [ ] T022 [US1] Write `relay-platform/analytics/0008_mv_connection_minutes.sql`: a materialised view `TO relay_analytics.daily_usage_v2` over `connection_events`, writing `connection_minutes` and leaving every other column at its type's zero for `SummingMergeTree` to add.
- [ ] T023 [US1] Discharge **FR-002**: the view reads **close rows only** — `WHERE event = 'closed' AND duration_ms IS NOT NULL`. R4 measured that a close carries the closing instant and the duration, so `ts - duration_ms` recovers the open and the open row adds nothing.
- [ ] T024 [US1] Implement whichever definition phase 6 will decide, and **say in the file that the decision is phase 6's and where it is recorded**. R3 measured both computable: `arrayJoin` over the minute range gives the meter's calendar buckets, `sum(duration_ms)` gives elapsed. Ship one, cite the other, and do not let the file imply the question was never asked.
- [ ] T025 [US1] The view must not write `channel_id`. A connection belongs to a tenant and not to a channel, so its rows carry the zero UUID in that column — **and that is a value a reader will meet**, so `data-model.md` and the contract say what it means before anybody queries it.
- [ ] T026 [US1] Apply, then verify with `SHOW CREATE` and by planting one close record and reading the rollup back. Clean the planted record out of both the source and the target, and verify the cleanup. 043's rule: clean up a probe before anything is counted.
- [ ] T027 [P] [US1] Write an integration test at **`relay-platform/services/ingester/src/metering.itest.ts`** asserting **N connections opened and closed produce the expected minutes for a dedicated environment id**. Use a dedicated environment id and scope every count by it — the analytical store has no lane guard (050-2) and this chapter writes a table every later suite reads.
- [ ] T028 [US1] In the same test, assert the **opens-without-closes** case: plant an open with no close and assert it contributes zero minutes rather than a wrong number. R5 measured 44 of 99 connections in that state.
- [ ] T029 [US1] Assert tenancy in both directions: a second environment's connections are unreachable from the first environment's filter. Constitution I, and the shape 4.4 and 4.5 both wrote.
- [ ] T030 [US1] Measure and record in `baseline.txt`: connection-minutes computed from the rollup against the same minutes computed directly from `connection_events`, over one window, with the opens-without-closes count beside them.
- [ ] T031 [US1] Run the four lanes and commit phase 3.

---

## Phase 4: User Story 1 and 2 — the metering read 🎯 MVP (Priority: P1)

**Goal**: one read answers FR-ANL-05's quantities for a tenant and a period from rollup rows,
and can be shown not to have touched a raw table.

**Independent test**: run the read, publish its rows-read figure beside the raw tables' counts.

- [ ] T031a [US1] **Give `ClickHouse` a read.** Measured: the interface is `insert`, `insertRequests`, `insertConnections`, `count`, `countRequests`, `countConnections`, and `post()` is a private closure — **insert-and-count only**, so a read beside it opens a second client against the same four environment variables. Add a query method returning rows, in the shape the interface already grew once per chapter. **Without this the "one client per service" argument is decoration**, which is what an earlier draft of the plan claimed it was not.
- [ ] T031b [US1] **Expect T031a to break `ingest.itest.ts` and complete the stub rather than widening the type.** `ingest.itest.ts:45` is a full object literal typed as `ClickHouse`, stubbing `insertRequests`, `insertConnections` and `countConnections`. Chapter 4.5 measured the identical event one method earlier — *"TS2739 — adding `insertConnections` broke `ingest.itest.ts`'s stub"* — and the fix is the same: **the compiler names every construction site**, so complete the stub and let it keep doing that. A `Partial<ClickHouse>` or an `as` cast would silence the one thing that makes a growing interface safe.
- [ ] T032 [US1] Write the metering read exactly as `contracts/metering-read.md` states it, in **`relay-platform/services/ingester/src/metering.ts`**, over T031a's query method — a module beside `clickhouse.ts`, which already owns the store's client. `sum()` with `GROUP BY`; `uniqMerge` for the state column. **Not a script under `analytics/`**: that directory is outside the coverage lane's include, so a read there can carry no pin, and an unwired script is the exact defect this chapter is about (`query.mjs` asks FR-ANL-05's question and is referenced by nothing).
- [ ] T033 [US1] Discharge **FR-005** and **SC-005**: **show the wrong read failing first**: `SELECT messages` without `GROUP BY` against a table holding several inserts for one key, and record what it returns. 047 measured `1000 1000 1000` where the truth was 3000. Then show the contract's read returning the truth. **A read that is correct only after somebody runs `OPTIMIZE` is right in a demo and wrong in production**, and the failing half is what makes that a measurement rather than a warning.
- [ ] T034 [US1] The stored-message-count read is **separate and has no lower bound** — it sums every delta up to the day asked for, because the count is a running balance. A `BETWEEN` here reports the period's *change* in stored messages, which is a different question that reads as a plausible wrong answer. Both readings recorded.
- [ ] T035 [US1] Discharge **FR-004** and **SC-006**: assert that a day with no activity and a day with zero figures are distinguishable. A materialised view emits no row for a group with no input, so "no activity" is always a missing row — **the distinction lives in the read, not in the table**, and the test says which.
- [ ] T035a [US1a] **Load a corpus, because the store cannot answer SC-002 as it stands.** Measured at T001: `message_events` **0 rows**, `connection_events` **154**. A rows-read figure against an empty table is not a measurement, and 4.2's cited 315-against-1,052,655 exists because that chapter loaded one. Run `scripts/scale/corpus.mjs` and then `scripts/scale/load-analytics.mjs`. **Set the corpus configuration explicitly rather than taking defaults silently** — SC-002 asks for the corpus size stated, and `CORPUS_ENVIRONMENTS` defaults to 3 (minimum 2) with the message count configurable beside it. **And know that the loader cannot be pointed anywhere else**: `load-analytics.mjs:14` is `const DB = "relay_analytics"`, hardcoded with no override, so this necessarily writes into the shared store and T036b's cleanup is mandatory rather than tidy. **Record the corpus database name, the configuration used, the row counts it produced, and the environment ids it created** — 047's pass 9 found every number of that feature correct about a database the chapter had not loaded.
- [ ] T035b [US1a] **Record the bind this creates, because it is the chapter's sharpest argument and not an inconvenience.** `load-analytics.mjs:53` is `postgresql('${PG_HOST}', …)`, which is the cross-path read T053 names as constitution III's first prohibition. **So the only way to demonstrate that the rollup works is to execute the violation the chapter is about.** The clause is not merely unmet — it is unmeetable, and the demonstration needs the forbidden path. That is a `<Trap>` candidate (T066) and it belongs in T053's amendment.
- [ ] T036 [US2] Discharge **FR-006 and SC-002**: report the read's rows-read figure beside the raw tables' row counts, with the corpus size stated. 4.2 published 315 rows read against 1,052,655 and that is the shape.
- [ ] T036a [US2] **Take phase 8's cost comparison now, while the corpus exists** — the rollup read against the same question asked of the raw tables, both best-of-three, both over the same window, with the corpus size stated. Loading twice would mean two corpora, and 047 needed a neighbour held still three times in one feature.
- [ ] T036b [US1a] **Remove the corpus rows and verify both directions**, before anything else is counted. `load-analytics.mjs` writes into the shared `relay_analytics` — `DB = "relay_analytics"`, not a scratch database — and every later suite reads those tables. **050-2 is exactly this missing guard**: Postgres has a trigger, an exemption list asserted both ways and a sweeper, and ClickHouse has none of the three. Delete by the environment ids T035a recorded, then assert the counts are back to their T001 openings **and that BOTH rollups hold no rows for those ids**. **Two, not one**: `analytics/0001_daily_usage.sql:19` reads `FROM relay_analytics.message_events`, so 4.2's shipped view fires on the same load and gains rows nobody asked it for. Its storage is an implicit inner table (R7 measured the name), so it is cleaned by that name rather than through the view. Research R8's planted row was removed from the source *and* the view's inner table, because a materialised view does not propagate a delete.
- [ ] T037 [US2] Use `EXPLAIN indexes=1` for any skipping claim, not `ProfileEvents`. 046 measured `ProfileEvents['SelectedParts']` returning **0** for a query that had read four parts of twelve; `EXPLAIN indexes=1` is the only honest instrument for that question here.
- [ ] T038 [US1] Discharge **FR-001a**: publish the four tables' row counts beside the read's output (SC-001a), so a reader can see which quantities have producers. Decide and record, once, whether the unpopulated columns are present-and-documented or absent — **a column reporting 0 messages for a tenant that sent messages is worse than an absent column.**
- [ ] T039 [US1] Discharge **FR-008**: state that DR-10's clause was satisfiable by a view nothing read over a table nothing wrote, and that a rollup with no reader discharges a clause about what billing scans in form only.
- [ ] T039a [US1] Pin `services/ingester/src/metering.ts` in `vitest.coverage.config.mts` with freshly measured numbers, **taking two observations and pinning below the lower one by the swing**. `session.ts` measured 87.80 and 85.36 on identical code twenty minutes apart; 050's two files moved by 0. **Run both halves of the threshold probe**: demand something impossible of the real key and watch it fail naming the file, then demand 101% of a key naming no file and watch it say nothing. **050-1 assigned this to this chapter in as many words** — *"T058 and T059 remain undone for this chapter … and the next chapter can write them"* — and this is that chapter.
- [ ] T039b [US1] Sweep every per-file pin against the include and exclude globs and record the count. 050 measured 49 pins, 49 binding, 0 unbindable. **Expand the globs over the real tree rather than pattern-matching in memory**: the first version of that sweep reported 16 false unbindables because `fnmatch` cannot do `**`.
- [ ] T040 [US1] Run all four lanes **and `pnpm coverage`**, record failures in `baseline.txt`, and commit phase 4. **`coverage` is the only lane that enforces the per-file pins**, and 050 shipped three phases before discovering its own integration suite had never run in it.

---

## Phase 5: User Story 3 — attribution (Priority: P2)

**Goal**: FR-ANL-09's four dimensions are measured and the ones this chapter cannot add are
recorded with their cost.

- [ ] T044 [US3] Measure what the channel dimension costs. **`channel_id` is already in the key from T014** — R6 measured it on the row, so it was a key column from the start rather than something added here. What is unmeasured is the price: the rollup's row count becomes `environments x channels x days`, and a tenant-day read now sums across that tenant's channels.
- [ ] T045 [US3] Discharge **FR-009** and **SC-007**: measure which of FR-ANL-09's four dimensions the rollup now answers, and record all four with their status: application, environment, channel, day.
- [ ] T046 [US3] Discharge **FR-010**: open a gaps entry for **application-level attribution** naming what closing it would cost. No analytical row carries an application, the store holds no `applications` table, and an application holds two environments (`unique (application_id, kind)`), so the mapping lives in Postgres — **closing it means arguing constitution III rather than writing a join.**
- [ ] T047 [US3] Run the four lanes and commit phase 5.

---

## Phase 6: User Story 4 — the definition, and the clause nobody reconciled (Priority: P2)

**Goal**: the unit in the billing table is defined, and the constitution's conflict with the
shipped platform is decided out loud.

- [ ] T048 [US4] Discharge **FR-012** and **SC-003**: compute connection-minutes **both ways** over one window and publish them side by side with the gap stated. 4.5 measured 2 against 0.03 for one connection; this is that finding at a window's scale.
- [ ] T049 [US4] Include a connection crossing a **minute** boundary and one crossing a **day** boundary. R3 measured the calendar expansion assigning each minute its own `toDate`, so the day split needs no special handling — but a claim nobody ran is a claim.
- [ ] T050 [US4] Decide which definition bills, and write the argument. The calendar bucket reproduces `meter.ts`'s documented rule and **charges reconnect churn**, which summing seconds does not; the duration is what a connection record literally contains. Name the loser rather than implying the winner was the only option.
- [ ] T051 [US4] Discharge **FR-011** and **SC-004**: amend `docs/04-srs.md` to close **Appendix C open question 4** — *"Does connection-minute metering need per-second precision, or is per-minute rounding acceptable?"*, against FR-ANL-05, owner *Product / Billing*. It has been open since before Part 4 began. **Closing it is an SRS revision**, so bump the revision table and let `check:docs` verify the ascent.
- [ ] T052 [US4] Amend **FR-ANL-05** itself if the decision narrows it, following the precedent in the SRS's own margin: *"FR-RTL-05 is narrowed from 'unique active users' to 'unique active persons', and FR-ANL-05 is deliberately unchanged"* — an amendment that says what it did **not** change is the shape to copy.
- [ ] T053 [US4] Discharge **constitution III's conflict**, which the plan's Constitution Check records and does not resolve. **Quote the whole clause, and lead with its first prohibition** — *"**Analytical queries MUST NEVER execute against the operational database (PostgreSQL)**; billing, metering, and dashboard analytics read only from the analytical store (ClickHouse), fed via a durable queue (SRS CON-01)."* Two facts against it, both measured: metering today reads **only** Postgres, and `load-analytics.mjs:53` is `postgresql('${PG_HOST}', …)` — **ClickHouse executing a query against Postgres**, which is the first prohibition rather than the queue qualifier. An earlier draft of this task cited only the qualifier, which is the weaker half of the sentence it appears in.
- [ ] T054 [US4] **Name the form of that resolution and choose it out loud**, in the shape 4.5 used for ADR-07 at T080a. Constitution VII requires a conflict *"resolved explicitly by amendment rather than silent divergence"*, so the options are a constitution amendment, a new ADR, or a recorded exception — and **the missing sentence is the defect rather than either choice.** `docs/12` §4 justifies the Postgres counter existing and does not justify the constitution's sentence; say so.
- [ ] T055 [US4] Leave untouched whatever still holds. 3.18 and 4.5 both wrote amendments that name the clauses they do **not** change, and that is what keeps an amendment from reading as a reversal.
- [ ] T056 [US4] Run the four lanes and commit phase 6.

---

## Phase 7: The documents this chapter makes wrong or incomplete

- [ ] T057 [P] Discharge **FR-014**: add the rollup to `docs/05-sad.md` §6.2, which declares the analytical schema and has gained a table per chapter since revision 1.3. This is the *incomplete rather than wrong* class 050 filed as FR-017a — **a document this chapter makes incomplete is falsified by nothing**, so no measurement will ever catch it and only a task will.
- [ ] T058 [P] Discharge **FR-015** and, with T059, **SC-009**: amend `docs/12-part-4-structure.md` §3's row for this chapter. It reads *"Daily rollup materialised views (DR-10) — billing never scans raw events"*, and a daily rollup materialised view has existed since 4.2 over a table nothing writes. **Leave the table's first column alone** — §3 keeps the original ordinals on purpose so older references resolve.
- [ ] T059 [P] Discharge **FR-016**: close `docs/12` §7.1. §3's 2026-09-13 amendment records chapter 4.2 building all four items of its brief and the chapter it belonged to is gone, while §7.1 still reads as open. **This is the defect 4.5 found at §7.2 and it survived the chapter that found it** — T085a amended §7.2 and nobody looked one entry up. Use §7.2's closure block as the shape.
- [ ] T060 [P] Discharge **FR-013**: amend **DR-10** where this chapter falsifies it. Its clause is *"Materialised views shall maintain daily per-tenant rollups for metering, so billing never scans raw events"*, and what this chapter measured is that the rollup satisfying it read a table with no producer and was read by nothing. **Read the clause before amending it** — 050 found three citations pointing at clauses that did not say what four artifacts claimed.
- [ ] T061 [P] Check whether **DR-17** needs anything. It is the media analogue this chapter cites for the delta technique — *"summing `media_events` deltas (uploaded/deleted), reconciled weekly … the media analogue of FR-ANL-06"* — and if this chapter's stored-count arm diverges from it, one of the two is now wrong.
- [ ] T062 [P] Re-check every clause this feature's artifacts cite, by opening the SRS rather than the artifacts. 044's lesson reached shipped source in 050: four documents agreed on two clauses that do not exist, and three citations pointed at clauses saying something else. **The artifacts agreeing with each other is not evidence.**
- [ ] T063 Run `pnpm check:docs` and `pnpm check:srs` after the amendments, and commit phase 7.

---

## Phase 8: The numbers, and the chapter

- [ ] T064 [P] Publish the cost comparison **T036a measured**, with its corpus named. Do not re-run it: the corpus was removed at T036b, and re-loading would produce a second corpus rather than a second reading of the first. 4.2's pairing is the precedent, and **047's pass 9 is why the corpus is named at all** — every number that feature measured was correct about a database the chapter had not loaded.
- [ ] T065 [P] Measure the rollup's compression — rows in against rows out. 4.1 published 1,000,000 raw rows becoming 89 rollup rows, and that ratio is what DR-10 buys.
- [ ] T065a **Fix the chapter's title and derive its slug, once, before anything references either.** `docs/12` §3 calls its titles provisional and the last two chapters both shipped different ones — row 5's *"Every request is an event"* became *"the requests that belong to nobody"*, row 6's matched. The slug is kebab-case of the title's main clause with any apostrophe **dropped**, and **three places must agree exactly**: the directory name, the manifest's `path` (T067) and the MDX `metadata.alternates` (T066). Record all four strings in `baseline.txt` so a later task compares rather than re-derives.
- [ ] T066 Draft the chapter at `relay-tutorial/app/(en)/part-4/chapter-06/<T065a's slug>/page.mdx`. The slug is kebab-case of the title's main clause with any apostrophe **dropped**, and it must match the manifest's `path` and the MDX `metadata.alternates` exactly. **At least one `<Trap>`** — `docs/07` §line 70 makes it a counted box class per code chapter and no gate counts it. Candidates already measured: the rollup over a table nothing writes, the read that is right only after `OPTIMIZE`, and a `BETWEEN` on a running balance.
- [ ] T067 Discharge **FR-018a** and **SC-012**: **register the chapter in `relay-tutorial/lib/tutorial.ts`.** `<ChapterHeader id="4.6" />` calls `getChapter`, which **throws** on an unregistered id, and `pnpm build` is the only gate that would catch it — 4.4 shipped at 112 of 112 with eight gates green and a site that did not build. Fill `id`, `path`, `title`, `status`, `readerProduces`, `sourceDoc`, `readerMinutes`. Leave `titleVi`, `readerProducesVi` and `translatedIn` to the translator. **Do this after T066**, because an entry whose page does not exist breaks the build in the other direction.
- [ ] T068 Discharge **FR-007**: state that the Postgres quota counter is unchanged and why, **citing `docs/12` §4 rather than re-deriving it** — *"a quota must refuse a send synchronously, so its counter cannot live downstream of a lossy stream"*, therefore *"Two counters of one quantity is the right answer and the reconciler is the price."* §4 is the section headed "Chapters must not re-teach these".
- [ ] T068a Discharge **SC-008** by running the diff it names: `git diff part4-ch5 HEAD -- services/api/src/quotas/ services/api/migrations/0013_quotas.sql services/api/migrations/0014_connection_minutes.sql` and record the empty output. **T011 recorded the counter's data and T068 writes the prose claim; neither is the diff.** 050's T071 is the precedent and its title is the whole point — the meter is untouched, and `git` is the evidence.
- [ ] T069 Discharge **FR-017**: do not re-derive 4.2's `SummingMergeTree` mechanics, 4.2's `uniq` approximation finding, or Part 3's quota counters. Cite them.
- [ ] T070 State that the reconciliation is **not** this chapter's. 047-1 and 048-1 are filed for movement IV and the job is 4.7; publishing agreeing numbers here would read as settling them. **Hand them forward in the prose, not just in `gaps.md`.**
- [ ] T071 [P] Put every mermaid source in `figures.ts`, never in `page.mdx`, and pass each to `<Figure>` as **`code=`**, not `chart=` — 049 shipped three as `chart` and `check:figures` named every line.
- [ ] T072 [P] Take every number in a figure from `baseline.txt`. No checker reads prose, and a mermaid block is prose.
- [ ] T073 Discharge **FR-018** and **SC-011**: measure prose words outside code fences against the 2,000–4,000 bound and record it whether or not it forces a split. **Count the `<Trap>` boxes in the same pass** (FR-018) — no gate counts them and the rule has been honoured by habit for every chapter.
- [ ] T074 Publish the new `.sql` files as whole bodies — they are new, which is the cheapest class — and everything else as `diff` hunks against `part4-ch5`. T006's counted list decides the set.
- [ ] T075 Generate the hunks from the checker's own replay, or from `git diff -U6 part4-ch5 -- <file>` where the file has not changed since that tag. **Verify they apply before pasting, not after.** Widen past `-U6` when a pre-image matches twice, and remember `-U8` measured worse than `-U10` once, because widening merges adjacent hunks and a merged hunk spans more repetition than either half did.
- [ ] T076 For any file T007 flagged as a **vi whole body**, do not attempt a repair — an English chapter cannot fix a Vietnamese fence, and the checker will not report it broken either (050-3). File it instead.
- [ ] T077 Discharge **SC-010**: run `pnpm check:fences` and report the close as a **delta against T005's opening**, by kind and locale, **with the two HEAD classes split** (FR-019).
- [ ] T078 Run all **eleven** gates (FR-020): `check:fences`, `check:docs`, `check:srs`, `check:figures`, **`pnpm build`** and `check:errors` in `relay-tutorial`, then `lint`, `typecheck`, `test`, `test:integration` and `coverage` in `relay-platform`. **Build before `check:errors`** — it reads the built `dist`. **Diagnose every red rather than counting it**, against T008's opening.
- [ ] T079 Write `specs/051-chapter-4-6/gaps.md`. **Re-measure every carried item and say plainly what each one is now** — 050-1 through 050-8, and 049's and 048's survivors that 050 re-measured. *Measure the carried ledger; do not copy it.* New entries at least for application attribution (T046), the `message_events` producer (R9), and anything phase 6 decides to defer.
- [ ] T080 In `gaps.md`, give **050-1 its second reading**. Its close asked for exactly this: run `pnpm coverage` at the next chapter's opening and write down which of the two behaviours appears, because the one thing known is that the config is not the cause.
- [ ] T081 In `gaps.md`, re-measure **048-4** rather than carrying its sentence. This chapter adds `channel_id` to a rollup key that had `environment_id` and `day`, so the unbounded product it names is now `environments × channels × days`. The item changed and copying it forward would hide that.
- [ ] T082 Audit every test this feature added and confirm none asserts only that a row exists. Record the count audited. **A conditional assertion whose condition is asserted unconditionally on the line above is a narrowing, not a hole** — 050's audit had to read the line above to tell them apart, and a grep for the pattern cannot.
- [ ] T083 Write `specs/051-chapter-4-6/traceability.md` mapping every FR and SC to tasks and to the artifacts that discharge them. **Record the requirements nothing discharged**, if any.
- [ ] T084 Rewrite `CLAUDE.md`'s `<!-- SPECKIT -->` block for the close, including every task premise this feature falsified by running it.
- [ ] T085 Commit phase 8, tag `part4-ch6` on `relay-platform`, and push all three repositories.

---

## Dependencies & Execution Order

```
Phase 1  premises + the openings   ── blocks everything
Phase 2  the table + both views    ── blocks 3, 4, 5
Phase 3  US1 connection-minutes    ── blocks 4
Phase 4  US1/US2 the read  🎯MVP   ── blocks 5
Phase 5  US3 attribution           ── independent of 6
Phase 6  US4 the definition + III  ── needs 3's numbers
Phase 7  the documents             ── needs 6's decisions
Phase 8  the numbers + the chapter ── needs all
```

### User story dependencies

- **US1** spans phases 3 and 4: the minutes have to be in the table before a read can answer
  from it.
- **US1a** is the corpus window inside phase 4 — the only place the three message-sourced
  columns can be checked against raw data, which is why phase 2 builds their view.
- **US2** is the rows-read claim and rides on phase 4's read.
- **US3** and **US4** both need the MVP and are independent of each other.

### Parallel opportunities

- Phase 1: T001–T011 are independent probes writing to separate sections of `baseline.txt`.
- Phase 7: T057–T062 touch different documents.
- Phase 8: T064 and T065 are independent measurements; T071 and T072 are independent of both.

---

## Implementation strategy

**MVP is phases 1–4**: a rollup with a named target, minutes in it from the one source with a
producer, and a read that answers from rollup rows and can prove it did not scan a raw table.

**Phase 6 is the one that cannot be skipped quietly.** A chapter that puts connection-minutes
in a billing table while SRS Appendix C question 4 stays open publishes an undefined unit, and
a Constitution Check that names a conflict and never resolves it is the *"PASS, with one open
case"* failure one level up.

**Phase 5 builds a view whose source has no producer, deliberately.** R9 declined the producer
for scope — it is a send-path change on the busiest path in the platform and by §3's table it
is not this chapter — but the view is what makes the rollup complete the day one exists, and
building it now is what turns "we did not do it" into "here is what is waiting".

---

## Notes

**Commit each phase.**

**Commits stay under five lines with no `Co-Authored-By` trailer.**

**The analytical store has no lane guard** (050-2). Every integration test this chapter writes
uses a dedicated environment id and scopes every count by it, and anything that stops merges
carries a `finally` that starts them again. Postgres has a trigger, an exemption list asserted
both ways and a sweeper; ClickHouse has none of the three, and this chapter writes a table
every later suite reads.

**Start an ingester for any test that waits on a row** — there is no ingester service in
`compose.yaml` and 050-8 measured 4.4's suite passing 5 of 5 with one and failing 5 of 5
without.

**A zero from an instrument is a claim about the corpus only if the instrument can be shown to
have read it.** This chapter's central number is a zero — `message_events` holds 0 rows — and
T002 exists because a zero is exactly the kind of finding that deserves a second question.
