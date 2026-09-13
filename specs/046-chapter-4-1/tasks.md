# Tasks — chapter 4.1, the question the counters can't answer

**Feature**: `specs/046-chapter-4-1/` · **Plan**: [plan.md](./plan.md) · **Spec**: [spec.md](./spec.md)

**This chapter ships no product code.** Three scripts in `relay-platform/scripts/scale/`, four
numbers, and one chapter in two locales. Everything it proves is proved against the platform as
Part 3 left it, which is why no task below writes a migration and several exist only to check
that none appeared.

**Verification methods, and one of them changed during analysis.** Constitution VI requires
every behaviour to trace to a requirement with a stated method. The four numbers are verified by
**A** — analysis, which is what FR-ANL-08 and NFR-PRF-02 both specify and what
`docs/11-scalability-measurement-2026-09-06.md` did for NFR-SCL-01. An analysis is not a test and
this file does not pretend otherwise.

**The seeder was going to carry unit tests and now carries a demonstration (D) instead.** A
`corpus.test.mjs` under `scripts/` matches none of `vitest.coverage.config.mts`'s four `include`
globs — all of them `packages/*/src/**` or `services/*/src/**`, all `.ts` — and `scripts/` is not
a workspace package, so `turbo run test` would never reach it. **It would have passed by never
running**, inside a chapter about instruments that report zero without looking. T043 records the
evidence, T047 is the verification, and T044 proves T047 red first.

**Nothing in this chapter joins `test:integration`.** A million-row corpus inside the lane would
break the whole-table assertions 045-74 spent a feature finding.

---

## Phase 1: Premises, instruments, and the numbers this feature inherited

**Everything blocks on this phase.** The chapter's argument rests on two claims about a schema
file, and 045 recorded a gate passing twenty-six times on a ref that did not exist. A premise
carried from a planning document and never re-run is the defect this project finds most often.

- [X] T001 **DONE DURING PLANNING** — re-derived the index facts from `relay-platform/services/api/src/db/schema.ts` at commit `52766091`: `messages` carries no `environment_id`, nothing indexes `created_at`, and the indexes present are `unique (channel_id, sequence)` (DR-01) and the partial `uniqueIndex (channel_id, idempotency_key)` (DR-03). **This must be re-run at the chapter's own tag** — see T002. The count of indexes is deliberately not carried forward (FR-014, `data-model.md` §4).
- [X] T002 **DONE.** Re-derived at `52766091` and recorded in `specs/046-chapter-4-1/baseline.txt`: no `environment_id` column, no index touching `created_at`, **2 indexes** both channel-scoped — counted by grep over the block, not carried. **The premise holds and the plan is not falsified.** Original: Re-run the derivation at this chapter's tag and record the output verbatim in `specs/046-chapter-4-1/baseline.txt`: `sed -n '/export const messages = pgTable/,/^);/p' relay-platform/services/api/src/db/schema.ts`. **If either claim is false the chapter's argument changes and the plan is wrong** — that is a finding, not an inconvenience. State the index count from this output rather than from `docs/12-part-4-structure.md`.
- [X] T003 **DONE DURING PLANNING** — confirmed `relay-platform/services/api/src/quotas/` holds no aggregate: no `count(`, no `sum(`, no `countDistinct`. `credit.ts` is `creditFor` and `highWaterMark`, two pure functions. This is research R1 and it is what falsified `docs/07-tutorial-plan.md`'s planned premise.
- [X] T004 **DONE DURING PLANNING, AND THE FIRST ANSWER WAS WRONG** — the bot exemption lives in `relay-platform/services/api/src/db/repository.ts:assertWithinQuota`, not in `quotas/` or `messages/` where it was searched for first. `docs/10-platform-review-fix-plan-2026-09-05.md` §0 had already run the check. FR-ANL-05 meters users, FR-RTL-05 caps persons, and the analytical query therefore applies **no `kind` filter** (research R3).
- [X] T005 **DONE DURING PLANNING** — `DEFAULT_LIMITS.send` and `DEFAULT_LIMITS.rest` are both 600 per environment per minute in `relay-platform/services/api/src/limits/policy.ts`, and a REST send spends both. Ten sends per second is the ceiling, so the chapter measures **latency, not throughput** (research R6).
- [X] T006 [P] **DONE — AND THE INHERITED NUMBER WAS ALREADY STALE.** `pnpm check:fences` reports **110 (APPLY 74, HEAD 36)**, against the 109 (APPLY 74, HEAD 35) CLAUDE.md carries and analysis pass 1 confirmed. The tutorial repository moved to `0f4d8d6` since; APPLY is unchanged. FR-015's delta is computed against **110**, and against 109 it would have been wrong by one in the direction that flatters the chapter. Original: **Run `pnpm check:fences` in `relay-tutorial` and record the opening number in `specs/046-chapter-4-1/baseline.txt`.** CLAUDE.md says 109 (APPLY 74, HEAD 35) and **that number was inherited by this feature, not measured by it.** FR-015 needs the opening figure to be the one this chapter's delta is computed against, and a stale opening makes the delta meaningless.
- [X] T007 [P] **DONE.** Measured 2026-09-13: 31,685 environments · 46,143 channels · 303,885 messages · 310,733 users · 487,481 outbox (6,249 pending). **All four carried figures had drifted upward** — +470, +576, +3,166, +6,230 — because `reset-lane.mjs` purges debris and not data. Stack brought up for the measurement and taken down after. Original: Record fresh row counts for the lane database in `specs/046-chapter-4-1/baseline.txt` — environments, channels, messages, outbox. 045's close-out figures (31,215 / 45,567 / 300,719 / 481,251) are **inherited, not re-measured**, and they are part of the instrument for T029's lane comparison.
- [X] T008 [P] **DONE.** node v22.23.2 · pnpm 10.33.0 · postgres:18-alpine · 10 cpus · 15 GB · WSL2 6.18.33.2, with both repository commits and the `DOCKER_HOST` this machine needs, in `specs/046-chapter-4-1/baseline.txt`. Original: Pin the environment in `specs/046-chapter-4-1/baseline.txt`: Node version, pnpm version, Postgres image tag from `relay-platform/compose.yaml`, CPU count, total RAM, and `RELAY_POSTGRES_PORT=15432`. Every number this chapter publishes is quoted against this block.
- [X] T009 [P] **DONE.** Recorded in `specs/046-chapter-4-1/baseline.txt` with the quotation: `scripts/scale/seed.mjs` writes no message rows, and `specs/034-chapter-3-15/baseline.txt:153` says its own corpus "is not seeded by anything in the repository". Original: Record in `specs/046-chapter-4-1/baseline.txt` that `relay-platform/scripts/scale/seed.mjs` writes no message rows, and that `specs/034-chapter-3-15/baseline.txt:153` says the 159 ms corpus "is not seeded by anything in the repository". This is why T011 exists rather than a reuse task.
- [ ] T010 Commit phase 1 in `relay` — `specs/046-chapter-4-1/baseline.txt` only. No platform change yet.

---

## Phase 2: Foundational — the corpus

**Blocking for all three stories.** US1 and US2 measure against this corpus; US3 is about the
interface it exposes. Contract: [contracts/seeder.md](./contracts/seeder.md). Shape:
[data-model.md](./data-model.md) §1.

- [X] T011 **DONE.** Created `relay-platform/scripts/scale/corpus.mjs` with its eight variables, `readConfig`, and a pure `planFor` that derives the volumes. **Its arithmetic reproduces the contract's example block exactly** — 1,000,000 / 1,333,334 / 1,600,000 / 6,000 / 2,400 / 12,001, six of six. **And writing it found two constraints the documents implied and never stated**: `CORPUS_ENVIRONMENTS` must exceed 1 and `CORPUS_DAYS` must exceed 90, or one of the query's two predicates excludes nothing and its cost is measured as zero. The first draft of the guards accepted both — `>= 1` and `>= 90` — and boundary probes caught it. Original text: Create `relay-platform/scripts/scale/corpus.mjs` reading its **eight** variables from the environment per [contracts/seeder.md](./contracts/seeder.md): `CORPUS_DATABASE`, `CORPUS_MESSAGES`, `CORPUS_CHANNELS`, `CORPUS_USERS`, `CORPUS_MEMBERSHIPS_PER_USER`, `CORPUS_ENVIRONMENTS`, `CORPUS_DAYS`, `CORPUS_NULL_SENDER_RATIO`. **The volume variables are what the query SCANS — inside both of its predicates** — so `CORPUS_MESSAGES` is the subject environment's rows *within the 90-day window*, and the seeder writes `CORPUS_DAYS / 90` times that many. As database totals a stated million gave the query 333,000 rows; as environment totals, 750,000. **It takes no `DATABASE_URL`** — it connects to the default database only to `CREATE DATABASE` and sets `DATABASE_URL` itself for the migration. Match `seed.mjs`'s style beside it — `.mjs`, environment variables, no framework.
- [X] T012 **DONE.** Creates `CORPUS_DATABASE` (date-stamped default) and refuses the lane's name — exercised: `CORPUS_DATABASE=relay` gives *"is the lane's own database; refusing"*. Original: In `relay-platform/scripts/scale/corpus.mjs`, create `CORPUS_DATABASE` — defaulting to `relay_corpus_<YYYYMMDDHHMMSS>`, so an unparameterised run is always a fresh corpus — and refuse if the name is the lane's. **The corpus never touches the lane** (`data-model.md` §3); `check-lane-scope.py` exists because that class of fault is hard to see one failure at a time.
- [X] T012a **DONE.** Runs `services/api/dist/db/migrate.js` with `DATABASE_URL` naming the new database; 15 migrations, 23 tables, reported as `migrations` in the output. No DDL written by the seeder. Original: In `relay-platform/scripts/scale/corpus.mjs`, **migrate the database it just created** by running `services/api/dist/db/migrate.js` with `DATABASE_URL` naming it — `client.ts:18` reads `process.env.DATABASE_URL ?? DEFAULT_DATABASE_URL`, so the runner is pointable. **Hand-write no DDL** (FR-003b): the corpus carries the schema the platform ships, which is what makes a measurement against it a measurement of this platform. The runner is `dist`, so this depends on `pnpm build` and inherits T020b's staleness problem.
- [X] T013 **DONE — AND THE SCHEMA CORRECTED THE PLAN.** Parents before children, but **not one application**: `unique (application_id, kind)` is FR-TEN-04, *exactly two environments per application*, so three environments need three applications under one organisation. Every artifact said one. The first run died on 23505. Original: In `relay-platform/scripts/scale/corpus.mjs`, write parents before children — organisation, application, environments, users, channels, channel members — so no foreign key is ever violated and no constraint is deferred.
- [X] T013a **DONE.** Mints the key on the subject environment and emits it as `credential`. Original: In `relay-platform/scripts/scale/corpus.mjs`, mint an API key on the subject environment and emit it as `credential` (FR-003, [contracts/seeder.md](./contracts/seeder.md)). **Without it T023's send loop cannot authenticate and the corpus is unreachable by any client.** `scripts/scale/seed.mjs:22` mints one and prints it for the same reason; that precedent is what found this gap.
- [X] T013b **DONE.** `upsertUser(kind: 'bot', description)`, added to `send_target.channel`, both emitted. Original: In `relay-platform/scripts/scale/corpus.mjs`, create the loop's sender: `upsertUser(externalId, { kind: "bot", description })` — **`createUser` takes no `kind` and cannot make a bot** — add it to one channel, and emit both as `send_target` (FR-003c). **An application credential may send only as a bot**, refused at `messages.service.ts:113` with 403 `sender_not_permitted`; the schema's `users_bot_description_check` is why the description is not optional. Found by sending one message, not by reading: the first attempt against a `kind = 'person'` sender was a 403 and the corpus as specified could not be written to at all.
- [X] T014 **DONE.** Bulk `INSERT … SELECT generate_series` through the `pg` pool — not `sendMessage`, not drizzle (constitution I keeps the query engine inside `src/db`). **`addMember` writes an outbox row even so**: the first floor run left 12,001, one per membership. They are cleared and `created.outbox` **reports** 0 rather than the contract asserting it. Original: In `relay-platform/scripts/scale/corpus.mjs`, bulk-insert messages **without going through `sendMessage`**. That path runs a transaction, an idempotency check, a quota read and a sequence allocation per message; it is the thing being measured (research R5). No outbox row, no event, no `usage_periods` movement — the corpus is data, not history.
- [X] T015 **DONE.** `generate_series` per channel makes `(channel_id, sequence)` unique by construction. Verified on 1.6M rows: **0 duplicates, 2,400 of 2,400 channels starting at 1.** Original: In `relay-platform/scripts/scale/corpus.mjs`, allocate `sequence` **per channel** from 1. `(channel_id, sequence)` is unique (DR-01) and a global counter violates it on the second channel.
- [X] T016 **DONE, AND THE FIRST VERSION WAS 0.02% SHORT.** A uniform offset over 120 days put **999,786** in the window against a requested 1,000,000 — binomial noise, and short of a floor stated as "≥1,000,000". The segments are now placed separately; density is identical either side (**1,111 vs 1,111 rows/day**) and the count is **exact**. Also: `(random() * 90 || ' days')::interval` died at volume on `invalid input syntax for type interval: "3.191957288484204e-05 days"` — a 2,000-row smoke test never reached it. Original: In `relay-platform/scripts/scale/corpus.mjs`, spread `created_at` across `CORPUS_DAYS` (default 120) **ending at seed time**, writing `CORPUS_DAYS / 90` times `CORPUS_MESSAGES` so the 90-day window holds exactly `CORPUS_MESSAGES`, and give each non-subject environment a tenth of the subject's rows so the **tenant** predicate excludes something too. A corpus written in one minute measures nothing about a range scan, and one with a single environment measures nothing about the join.
- [X] T017 **DONE.** 16,002 null senders counted at the floor, reported rather than derived from the ratio. Original: In `relay-platform/scripts/scale/corpus.mjs`, leave `CORPUS_NULL_SENDER_RATIO` of messages with `user_id IS NULL`. **This is research R4 made present rather than assumed absent**: `count(DISTINCT user_id)` drops nulls silently while `usage_active_users` survives user deletion (`repository.ts:3551`), so the two sides of movement IV's reconciliation diverge by construction. A corpus with no null senders hands that surprise to a later chapter.
- [X] T018 **DONE.** Emits `subject` beside `created`, every field counted from the database. **`channel_members` was a table that does not exist** — it is `members`; `memberships` is humans in organisations. Original: In `relay-platform/scripts/scale/corpus.mjs`, emit the JSON block [contracts/seeder.md](./contracts/seeder.md) specifies on stdout, reporting **what was created rather than what was requested** — including `messages_null_sender` counted rather than derived from the ratio, and a **`subject`** block carrying `messages_in_window` beside `messages`. **The chapter quotes `subject.messages_in_window`**: two predicates stand between it and `created.messages`, and at the defaults they are 1,000,000 and 1,600,000.
- [ ] T019 Commit phase 2 — `relay-platform/scripts/scale/corpus.mjs`. Gates first: `pnpm lint && pnpm typecheck && pnpm test` in `relay-platform`.

---

## Phase 3: User Story 1 — the question, and the neighbour that pays (Priority: P1) 🎯 MVP

**Goal**: the analytical question FR-ANL-05 and FR-ANL-09 ask, written against Postgres for the
first time, with its plan and its cost to a concurrent write.

**Independent test**: seed a corpus, run the query, capture plan and duration; run it again beside
a send loop and compare the loop's p95 with and without it.

- [X] T020 [US1] **DONE.** `measure.mjs` with `--phase baseline|counterfactual`, `--db`, `--environment`, `--query-only` and `--drop-all`. Original: Create `relay-platform/scripts/scale/measure.mjs` with a `--phase baseline` mode taking `--db`, and a `--query-only` mode taking `--db` and `--environment` that runs the analytical query alone — T029 uses it against the lane, where no send loop may run and where the environment has to be chosen rather than assumed. Both per [quickstart.md](./quickstart.md) §3.
- [X] T020a [US1] **DONE.** Spawns `dist/main.js` at `PORT=0`, port from the child's log line, health-checked before any send. Original: In `relay-platform/scripts/scale/measure.mjs`, spawn `services/api/dist/main.js` with `PORT=0` and a `DATABASE_URL` naming the **corpus** database, and read the bound port from the child's own log line. This is the pattern `scripts/scale/load.mjs:46` already uses, and the reason it uses it: nine hand-allocated port bands put a service inside another's range twice, and the map was deleted rather than corrected. **Without this task the send loop has nothing to send to** — the corpus lives in a database no running service is pointed at.
- [X] T020b [US1] **DONE.** `refuseStaleDist()` compares the newest mtime under `src` and `dist` and refuses. Original: In `relay-platform/scripts/scale/measure.mjs`, refuse to run if `services/api/dist` is older than `services/api/src`. **The harness spawns `dist`**, and a `dist` built against another tag produced 38 identical `42703 column … does not exist` errors that read like a broken chain and cost a published conclusion (045-77).
- [X] T021 [US1] **DONE.** The FR-ANL-05/09 query as research R2 states it, no `kind` filter. Original: In `relay-platform/scripts/scale/measure.mjs`, implement the FR-ANL-05/09 query exactly as research R2 states it — `date_trunc('day', m.created_at)`, `count(*)`, `count(DISTINCT m.user_id)`, joined to `channels` on `environment_id`, bounded to 90 days. **No `kind` filter** (T004). Written as somebody would write it against this schema, not as a straw man (FR-004).
- [X] T022 [US1] **DONE.** `EXPLAIN (ANALYZE, BUFFERS)` beside every duration — **and the plan is what carried the chapter's result**: the join is 140 ms of 698 and the sort is 656. Original: In `relay-platform/scripts/scale/measure.mjs`, capture `EXPLAIN (ANALYZE, BUFFERS)` beside every duration. **A duration says a query was slow; the plan says why**, and distinguishes a scan from a cold cache (FR-005, `data-model.md` §2).
- [X] T023 [US1] **DONE.** REST client at ten sends a second, authenticating with `credential` as `send_target.bot`. Asserts 201 and **refuses to report a percentile of nothing** — the first version died on `undefined.toFixed` where the useful output was the refusal body. Original: In `relay-platform/scripts/scale/measure.mjs`, implement the send loop as a REST client authenticating with the `credential` and addressing `send_target.channel` as `send_target.bot` from T013a/T013b's output block, at **ten sends per second**, reporting p50/p95/p99 over a stated window. T005 is the ceiling and the loop must not silently measure refusals instead of writes — assert the response status and fail loudly on a `429`.
- [X] T024 [US1] **DONE, AFTER TWO WRONG MEASUREMENTS.** The first ran the query ONCE beside a 60 s loop — 1% overlap, and it reported no effect from a measurement that could not show one. The second ran it continuously but put quiet first on a cold cache. The third warms up, runs quiet, busy, **then quiet again**: the two controls agree within **0.7 ms**, so ordering is not carrying the result. Original: In `relay-platform/scripts/scale/measure.mjs`, run the send loop **twice** — once with the analytical query running beside it and once without — and report both, plus the difference as a number rather than a direction (FR-006, `data-model.md` §2's note on M2).
- [X] T025 [US1] **DONE.** Every result carries the corpus block, the storage figures and the query count that ran alongside. Original: In `relay-platform/scripts/scale/measure.mjs`, report how many rows the send loop itself added, and quote the corpus block from T018 and the environment block from T008 into every result it prints. **The loop writes into the tables M1 counts** — 600 rows against 1,000,000, about 0.06% — and FR-ANL-05 meters bots like anyone else, so the contamination is published rather than engineered around. Four fields or the number is uninterpretable (`data-model.md` §2).
- [X] T026 [US1] **DONE.** 1,000,000 in the subject's window exactly, of 1,333,334 in the environment and 1,600,000 in the database. Seeded and measured the same day. Original: Build the corpus at the stated floor — ≥1,000,000 messages across ≥2,000 channels **inside both of the query's predicates**, which is what `subject.messages_in_window` reports — and record the emitted JSON in `specs/046-chapter-4-1/baseline.txt`. **Record the seed date**, and run T027–T029 the same day: the query anchors on `now()` and the corpus does not.
- [X] T027 [US1] **DONE. M1 = 585.9 ms**, best of three, 91 days returned. The plan names `Seq Scan` and `Hash Join` — **not an index seek** — so T002's premise is confirmed from the other side. Original: Take **M1** — the analytical query's duration and plan — and record it in `specs/046-chapter-4-1/baseline.txt` **beside `subject.messages_in_window` and the seed date**. A duration without the row count the query actually touched is not comparable to the predecessor's 159 ms or to anything else. **If the plan names an index rather than a scan, stop**: T002's premise is false and the chapter changes.
- [X] T028 [US1] **DONE. M2a 20.5 ms, M2b 13.7 ms** against NFR-PRF-02's 150 ms. **The send path is 6.8 ms FASTER beside 102 analytical queries than alone** — the hypothesis is falsified and the sign is inverted. Original: Take **M2a and M2b** — send-path p95 without and with M1 running — and record both in `specs/046-chapter-4-1/baseline.txt`, each stated against NFR-PRF-02's published 150 ms.
- [X] T029 [US1] **DONE.** Lane's busiest environment: **1,018 rows, 0.9 ms, 1 day** against the corpus's 1,000,000 rows, 585.9 ms, 91 days — **a factor of 651**. The predecessor's pair was 183. Original: Run `measure.mjs --query-only` against the **lane** database, naming **the lane environment with the most messages** — the lane holds 31,685 environments over 303,885 messages, about ten each, so an unnamed pick makes the number meaningless and an unlucky one makes it a lie. Record the environment id, **its own message count**, and the duration in `specs/046-chapter-4-1/baseline.txt` beside the corpus figure. FR-009 requires both to be published with a statement of which would have decided the question wrongly — the precedent is the chapter on what a user sees, where the lane answered 0.87 ms against a real 159 ms.
- [X] T030 [US1] **DONE, AND IT APPLIES.** Neither half of the planned argument survived: the query does not tax the write path here, and the index that would fix it buys **4.4%** for +107 MB, because the cost is a sort of a million rows that no index removes. Volume reached and limits recorded in `baseline.txt`. **The chapter's argument is now sharper than the planned one** — you cannot index your way out of an analytical question when the cost is the aggregation. Original: **If M1 and M2 do not show a cost a reader would act on**, record the volume reached and what it does not prove in `specs/046-chapter-4-1/baseline.txt`, and record the fallback FR-010 names: an analytical event per API request rather than per message, and 90-day retention as a declared TTL against a partition-and-delete job. **A measurement that refuses the hypothesis is published, not re-run at a higher volume until it agrees.**
- [X] T031 [US1] **DONE.** `git status` shows `scripts/scale/` only; migrations end at `0014_connection_minutes.sql`; both corpus databases dropped; the lane's row counts are identical to T007's. Original: Verify no schema change exists: `git -C relay-platform status --short` shows additions under `scripts/scale/` only, and `relay-platform/services/api/migrations/` is unchanged (FR-002, FR-013).
- [ ] T032 [US1] Commit phase 3 — `relay-platform/scripts/scale/measure.mjs` and `specs/046-chapter-4-1/baseline.txt`. Gates first.

---

## Phase 4: User Story 2 — the index that would fix it (Priority: P2)

**Goal**: the obvious fix, measured, and shown to cost more than it saves.

**Independent test**: on a throwaway copy of the corpus, add the column and index, re-run both
measurements, and compare all four numbers against Story 1's.

- [X] T033 [US2] **DONE.** `--phase counterfactual` copies with `create database … template …` rather than re-seeding, so the four numbers compare against identical data. Original: In `relay-platform/scripts/scale/measure.mjs`, add a `--phase counterfactual` mode that **copies** the corpus database rather than re-seeding it. Two corpora that differ by chance make the four numbers incomparable (`data-model.md` §3).
- [X] T033a [US2] **DONE.** `spawnApi(urlFor(target))` points the api at the copy before M4, so the send loop measures the schema the index is on. Original: In `relay-platform/scripts/scale/measure.mjs`, **respawn the api against the copy** before M4, using T020a's `PORT=0` pattern with `DATABASE_URL` naming the counterfactual database. **An api left pointed at the scratch database reports M4 as a latency measured against the schema the index was supposed to change** — a number that looks like a result and answers a different question.
- [X] T034 [US2] **DONE.** `ALTER TABLE` + backfill from `channels` + `CREATE INDEX`, as statements against the copy. No migration file, no `schema_migrations` row. Original: In `relay-platform/scripts/scale/measure.mjs`, apply `ALTER TABLE messages ADD COLUMN environment_id uuid`, backfill it from `channels`, and `CREATE INDEX ON messages (environment_id, created_at)` — **as statements against the copy**. No migration file, no `schema_migrations` row, no number in the sequence (`data-model.md` §3, `gaps.md` 045-69).
- [X] T035 [US2] **DONE.** `COUNTERFACTUAL_SQL` drops the join and reaches `environment_id` directly, and the source says a faster query that is also a different query proves less than it appears to. Original: In `relay-platform/scripts/scale/measure.mjs`, rewrite the query for the counterfactual schema — the join disappears and the predicate reaches `environment_id` directly — and record that the query itself changed, since a faster query that is also a different query proves less than it appears to.
- [X] T036 [US2] **DONE. M3 = 560.2 ms and 552.0 ms** across two corpora, against baselines of 585.9 and 603.4. **The gap is inside the run-to-run spread** — a single pairing would have reported 4.4% as a finding. Original: Take **M3** — the counterfactual query's duration and plan — and record it in `specs/046-chapter-4-1/baseline.txt`.
- [X] T037 [US2] **DONE. M4 quiet mean 18.6 ms**, identical to the baseline's within noise. Original: Take **M4** — send-path p95 against the counterfactual database, through the api T033a respawned against it — and record it in `specs/046-chapter-4-1/baseline.txt` beside M2a.
- [X] T038 [US2] **DONE, AFTER THREE WRONG NUMBERS.** +204 MB was the column plus dead tuples; +107 MB the index plus un-vacuumed bloat; +4.3 MB the index minus the compaction the vacuum had just done to the others (`messages_channel_id_sequence_unique` 104 → 62 MB). Measured by name: **column 24.8 MB, index 62.0 MB, rewrite 178.6 MB transient — 86.8 MB permanent on a 179 MB table, +49%.** Original: Measure the storage cost of the column and the index with `pg_total_relation_size` and `pg_relation_size`, and record it in `specs/046-chapter-4-1/baseline.txt` as a figure (FR-007a).
- [X] T039 [US2] **DONE — AND IT APPLIES ON BOTH SCHEMAS.** `hypothesis_send_path_pays` is **NOT SUPPORTED** on the baseline (18.6 quiet, 12.0 beside) and on the counterfactual (18.6, 10.1), four control loops agreeing within 1.3 ms and 0.3 ms. The harness states the verdict rather than leaving a reader to subtract and choose a direction. Original: **If M4 is not above M2a, publish that.** It is the chapter's most interesting possible result and it falsifies the central claim. Record it in `specs/046-chapter-4-1/baseline.txt` with the plan's own prediction beside it.
- [X] T040 [US2] **DONE.** `--drop-all` takes every `relay_corpus*` database, not an enumerated two. Original: In `relay-platform/scripts/scale/measure.mjs`, implement `--drop-all` dropping **every `relay_corpus*` database**, not the two this phase happens to know about. T044 and T047 each create more, and a cleanup step that enumerates its own two is a cleanup step that passes while six stand. Per [quickstart.md](./quickstart.md) §5.
- [X] T041 [US2] **DONE.** 0 corpus databases remain; the lane is identical to T007; the repository carries `scripts/scale/` only. Original: Run `--drop-all` and verify **this phase's** leftovers are gone: no `relay_corpus*` database remains, `git -C relay-platform status --short` shows no migration, column or index, and the lane database's row counts match T007's (SC-005). **This certifies Phase 4 and nothing after it** — T047a repeats it for Phase 5, because the dependency graph permits US3 to run either side of US2 and a cleanup whose correctness depends on which order somebody picked is not a cleanup. **A red probe writes to the lane** — 043 left two `javascript:alert(1)` rows and the next measurement read them as pre-existing data contradicting the plan.
- [ ] T042 [US2] Commit phase 4 — `relay-platform/scripts/scale/measure.mjs` and `specs/046-chapter-4-1/baseline.txt`. Gates first.

---

## Phase 5: User Story 3 — the instrument a later chapter reuses (Priority: P3)

**Goal**: the seeder is a contracted interface rather than a script that happened to work once.

**Independent test**: run it at three volumes and confirm the reported counts match what was asked
for (T047); run it twice and confirm it refuses (T047a); break it three ways and confirm the check
notices (T044). Every clause of that sentence now has a task behind it — **one of them did not**,
and a phase whose own test description outruns its tasks is the smallest version of a chapter
claiming more than it built.

- [X] T043 [US3] **DONE.** Evidence re-derived and recorded in `baseline.txt`: four `include` globs all under `packages/*/src` or `services/*/src`, `pnpm test` is `turbo run test`, `pnpm-workspace.yaml` lists two roots. `scripts/` is in none of them. Original: Record in `specs/046-chapter-4-1/baseline.txt` why the seeder is verified by demonstration rather than by unit test, with the evidence: `relay-platform/vitest.coverage.config.mts`'s four `include` globs are all `packages/*/src/**` or `services/*/src/**` and all `.ts`; `pnpm test` is `turbo run test` over workspace packages; and `pnpm-workspace.yaml` lists only `packages/*` and `services/*`. **A `corpus.test.mjs` under `scripts/` would be collected by nothing and pass by never running** — which is the defect this chapter is about, one level down. Verification is T047, which compares what the seeder reports against what the database holds and cannot pass while they disagree.
- [X] T044 [US3] **DONE — AND THE FIRST TWO FALSIFICATIONS WERE WRONG.** One patched in a variable that does not exist and refused on `seqBase is not defined`, a JS error rather than the constraint. The other broke the **out**-of-window count, which `messages_in_window` does not read, so the check agreed and the break went unseen. **A falsification that fails for the wrong reason proves nothing.** Redone: a channel reusing sequences 1..n gives `duplicate key value violates unique constraint "messages_channel_id_sequence_unique"`; an in-window count short by one per channel reports 1,980 against 2,000. `corpus.mjs` restored byte-identical after each. Original: **Test T047 red before trusting it green**, three ways, against `relay-platform/scripts/scale/corpus.mjs`: allocate `sequence` globally instead of per channel and confirm the run dies on `messages_channel_id_sequence_unique`; mis-spread messages across channels and confirm the reported count disagrees with the request; set `CORPUS_NULL_SENDER_RATIO` to 0 and confirm `messages_null_sender` reports 0 rather than the derived figure. Restore after each, and **clean up the probe before anything is counted** — 043 left two rows behind and the next measurement read them as contradicting data.
- [X] T045 [US3] **DONE.** Implemented in Phase 2 and exercised in T047a. Original: In `relay-platform/scripts/scale/corpus.mjs`, implement the refusal: a run naming a `CORPUS_DATABASE` that already holds a corpus **refuses and names what it found**. Adding to a corpus silently makes every published number unattributable ([contracts/seeder.md](./contracts/seeder.md)).
- [X] T046 [US3] **DONE, AND A PROBE CAUGHT THE MESSAGE LYING.** A name containing a quote gave `unterminated quoted identifier` and the failure text then said the database was **LEFT IN PLACE** — one that had never been created. `CORPUS_DATABASE` is now refused unless it matches `/^[a-z][a-z0-9_]{0,62}$/`, which makes both that message and the injection impossible rather than handled. Original: In `relay-platform/scripts/scale/corpus.mjs`, leave partial state in place on failure and name it on stderr. A half-built corpus that looks empty is worse than one that says what it is.
- [X] T047 [US3] **DONE.** 2,000 / 20,000 / 50,000 messages across 20 / 100 / 200 channels — all three match the request exactly. Original: Run the seeder at three volumes and confirm the reported counts match the request each time; record the three runs in `specs/046-chapter-4-1/baseline.txt` (SC-001).
- [X] T047a [US3] **DONE.** Second run: *"relay_corpus_twice already exists and holds 3199 messages; refusing. Pass a different CORPUS_DATABASE, or drop it."* Original: **Run the seeder twice with the same `CORPUS_DATABASE` and confirm the second run refuses, naming what it found.** Passing the name is the only way to reach the refusal — the date-stamped default makes every unparameterised run a fresh corpus — and pass 6 found that this task had been written against a contract under which the branch could never fire. Record the refusal text in `specs/046-chapter-4-1/baseline.txt`: a refusal nobody has seen is a branch nobody has run.
- [X] T047b [US3] **DONE.** Dropped 4 databases; 0 remain; the lane is identical to T007. Original: Run `--drop-all` and verify no `relay_corpus*` database remains and the lane's row counts still match T007's. **Phase 5 creates up to six databases** — three in T044's falsifications, three in T047's volumes — and T041 ran before any of them existed. Each phase drops what it made, so the result does not depend on which order US2 and US3 were taken in.
- [X] T048 [US3] **DONE.** `grep` for either script outside `scripts/` returns nothing. Original: Verify `relay-platform/scripts/scale/corpus.mjs` is imported by no service and run by no lane (SC-006, first half): `grep -rn "corpus.mjs" relay-platform --include="*.ts" --include="*.json"` returns only `scripts/`. This is the claim the plan's Constitution Check makes about principle VII.
- [X] T049 [US3] **DONE.** Two additions, both forced by T046's probe: `CORPUS_DATABASE`'s name rule, and a Failure row that says what is named on stderr. Original: Record in [contracts/seeder.md](./contracts/seeder.md) any variable or output field added after the contract was written, and say which task forced it. **A contract written by one caller is a contract written by one caller's opinion** — 045's deferral lesson one level down.
- [ ] T050 [US3] Commit phase 5 — `relay-platform/scripts/scale/corpus.mjs` and `specs/046-chapter-4-1/contracts/seeder.md`. Gates first.

---

## Phase 6: The chapter, and closing out

- [ ] T051 Choose the chapter slug and create `relay-tutorial/app/(en)/part-4/chapter-01/<slug>/page.mdx`. The directory convention is the global ordinal decided in `docs/12-part-4-structure.md` §2.1.
- [ ] T052 Write the opening of `relay-tutorial/app/(en)/part-4/chapter-01/<slug>/page.mdx`: the questions FR-ANL asks, and which of them Part 3's counters can answer. The answer is one, and the reader built those counters.
- [ ] T053 Write the shape-mismatch section of `.../page.mdx`, including the callback to the chapter on what a user sees — an index measured and dropped on camera in migration `0001`, with the schema's own comment quoted. **Name the subject, not the ordinal** (045 FR-008): the rework renumbered twenty-one of twenty-six chapters.
- [ ] T054 Write the measurement sections of `.../page.mdx` carrying M1–M4 with their plans, corpora and conditions, and the lane figure beside the corpus figure (FR-008, FR-009). **State the factor between the lane figure and the corpus figure as a number** (SC-002) — the predecessor's pair was 0.87 ms against 159 ms, and the factor is what makes the point rather than the two durations.
- [ ] T055 Write the counterfactual section of `.../page.mdx`: the index helps, and here is the bill. **This is the chapter's argument and the reason it is not answerable with "add an index."**
- [ ] T056 Write the forward reference in `.../page.mdx` naming what this chapter did not do — no ClickHouse, no emission path, no reconciliation (FR-012). And do **not** re-derive the fire-and-forget tradeoff: the chapter on when to stop trying shipped `analytics.{domain}.{action}.{environment_id}` and argued it (FR-011).
- [ ] T057 [P] Write `relay-tutorial/app/(en)/part-4/chapter-01/<slug>/figures.ts` — at least two figures: the two index shapes against the two questions, and the four measurements as a before/after.
- [ ] T058 [P] Add at least one `TRAP` box to `.../page.mdx`. The candidate with the best evidence is the lane's own answer: 0.87 ms would have settled the predecessor's question wrongly, and it is the same trap here.
- [ ] T059 Register the chapter in `relay-tutorial/lib/tutorial.ts` — path, title, and both locales — and add Part 4's title, "Everywhere the data went", with a Vietnamese rendering.
- [ ] T060 Create `relay-tutorial/app/(vi)/vi/part-4/chapter-01/<slug>/` carrying every code fence byte-identical to the English page (045 FR-010). If it ships untranslated it must be a visibly marked placeholder (045 FR-011).
- [ ] T061 Run `node scripts/prose-words.mjs` in `relay-tutorial` against `.../page.mdx` and record the count in `specs/046-chapter-4-1/baseline.txt`. The bound is 2,000–4,000 words measured **outside** code fences (SC-008).
- [ ] T062 Run `pnpm check:fences` and record the closing number in `specs/046-chapter-4-1/baseline.txt`. **Report the delta against T006's opening, not the total** (FR-015). The total is not claimed green and the chapter's close-out says so in words.
- [ ] T063 [P] Run the remaining gates and record each result in `specs/046-chapter-4-1/baseline.txt`: `lint`, `typecheck`, `test`, **`build`** in `relay-platform` **first**, then `check:docs`, `check:srs`, `check:figures`, `check:errors` in `relay-tutorial`. **The order is load-bearing** — `check-error-codes.mjs:30` reads `relay-platform/packages/protocol/dist/codes.js`, so `check:errors` run before a build reports on the previous build's registry.
- [ ] T064 Write `specs/046-chapter-4-1/traceability.md` mapping FR-001…FR-015 and SC-001…SC-008 to the tasks that verify them.
- [ ] T065 Open `specs/046-chapter-4-1/gaps.md` and record what this chapter found and did not close: research R4's reconciliation divergence, which movement IV inherits; the two gates `docs/12-part-4-structure.md` §6 says must exist before Part 4's first chapter split; and **the reuse claim SC-006 used to make** — that a later chapter runs this seeder unmodified — which only movement IV can settle.
- [ ] T066 **Run the reader protocol** per `specs/036-chapter-3-18/reader-protocol.md`: one person who has not read this specification, given the published chapter alone, answering SC-007's three questions. Record every question they could not answer verbatim in `specs/046-chapter-4-1/gaps.md`. **Fourteen records have named this and none has run it.**
- [ ] T067 Record in `specs/046-chapter-4-1/gaps.md` that the chapter **cannot be tagged**: `part3-ch18` is `54b2cd53` and `rework/part3-ch18` is `3732d6cf`, both exist, and `README.md:8` promises one tag per chapter. Name it as blocking Part 4's tag convention rather than this chapter's content.
- [ ] T068 Confirm one last time that no `relay_corpus*` database remains and the lane's row counts match T007's, then commit phase 6 in all three repositories and update the `<!-- SPECKIT -->` block in `CLAUDE.md` with the chapter's close-out figures. **The final sweep can fail for a real reason** — a phase whose cleanup task did not run — which is the only kind of check worth adding after two that already passed.

---

## Dependencies & Execution Order

### Phase dependencies

```
Phase 1  premises          ──> everything. T002 can falsify the plan.
Phase 2  the corpus        ──> US1, US2, US3 all need it
Phase 3  US1 (P1)  🎯 MVP  ──> US2 needs its numbers to compare against
Phase 4  US2 (P2)          ──> independent of US3
Phase 5  US3 (P3)          ──> independent of US2; both need Phase 2
Phase 6  the chapter       ──> needs US1 and US2's numbers; US3 optional for prose
```

### User story dependencies

- **US1** depends on Phase 2 only. It is the MVP: a chapter carrying M1, M2a and M2b already
  demonstrates CON-01, with the counterfactual left as a claim.
- **US2** depends on US1's M1 and M2a, because its whole content is the comparison.
- **US3** depends on Phase 2 and on nothing else. It could run before US2 — and that freedom is
  what produced the cleanup defect pass 4 found. **Each phase now drops the databases it created**
  (T041, T047b) rather than relying on a later phase to sweep, so either order leaves the same
  state behind.

### Parallel opportunities

- Phase 1: T006, T007, T008, T009 are four independent recordings — `[P]`.
- **Phase 5 has no parallel pair and its tasks are strictly ordered.** T043 records why the
  verification is a demonstration, T047 runs it, T047a exercises the refusal, T044 falsifies it,
  and T047b drops what all of them created. Each needs the one before it.
- Phase 6: T057, T058 and T063 touch different files from the prose tasks — `[P]`.
- **Phase 2 has none.** The seeder is one file and the tasks are its parts.
- **Phases 3 and 4 have none that matter.** Measurements are serial by nature: nothing else runs
  on the machine during one, which is the whole point of T008.

## Implementation strategy

**MVP is Phase 1 + Phase 2 + Phase 3 (US1).** That yields a chapter that asks the analytical
question, shows the plan, and shows the neighbour paying — CON-01 demonstrated rather than
asserted. The counterfactual strengthens it and is separable.

**Stop points that are real**, rather than phase boundaries that look tidy:

- **T002 can end the feature.** If `messages` has gained an `environment_id` or an index on
  `created_at` since planning, the premise is false, and the correct action is to re-open
  `docs/12-part-4-structure.md` §2.4 rather than to write around it.
- **T027 can end the chapter's first half.** A plan naming an index seek means the same thing.
- **T030 and T039 are where the chapter is allowed to disagree with its own plan**, and both say
  to publish the disagreement. A measurement re-run at a higher volume until it agrees is not a
  measurement.

## Notes

**Two numbers in this feature were inherited rather than measured**, and T006 and T007 exist to
replace them: `check:fences` at 109 and 045's close-out row counts both came from CLAUDE.md. A
number carried between documents and never re-run is the shape this project has paid for
repeatedly — most recently a gate that passed twenty-six times on a ref that did not exist.

**Analysis pass 1 changed four things and all four were found by running something.**
`check:fences` was run and confirms the inherited 109 (APPLY 74, HEAD 35), so T006 keeps its
opening figure; `pnpm prose-words` turned out not to be a package script, so T061 names the file;
`check-error-codes.mjs` reads a built `dist`, so T063 is ordered; and the seeder's unit tests
would have been collected by nothing, which is C1 and the reason phase 5 now reads as it does.
**Nothing in that list was visible by reading the artifacts against each other.**

**T011 RAN, AND IT FOUND SOMETHING NINE ANALYSIS PASSES COULD NOT.** The documents said the
neighbours and the extra thirty days exist "because a predicate that excludes nothing is not
being tested either" — a rationale, in prose, nine passes read without noticing that **nothing
enforced it**. `CORPUS_ENVIRONMENTS=1` and `CORPUS_DAYS=90` were both legal, and both produce a
corpus that measures one predicate and publishes a number about two. The code had to decide and
the prose did not. **This is the first finding since pass 3 that came from outside the loop.**

**Analysis pass 8 asked pass 7's question of the predicate two lines below the one pass 7 fixed.**
The tenant predicate had been leaving the query a third of a stated million; the date predicate
was then leaving it three quarters of that, and the fix for the first did not prompt anybody to
check the second. `CORPUS_MESSAGES` now means the rows inside **both** predicates. Pass 8 also
found that `CORPUS_MEMBERSHIPS_PER_USER` had arrived in pass 7 with a false reason attached —
**`channel_members` is not in the measured join at all** — written into two files by the pass that
was fixing unchecked claims.

**Analysis pass 7 did the arithmetic in the tables, which six passes had read and not multiplied.**
Three environments, a million messages, one subject: the query saw **333,000 rows** while every
document said the floor of 1,000,000 was met. The volume variables are now the subject
environment's and the seeder reports a `subject` block beside `created`. The lane comparison had
the same hole from the other end — 31,685 environments over 303,885 messages, and no task said
which one the query names.

**Analysis pass 6 read the contract back against the tasks that consume it, for the first time.**
Its invocation line still showed a `DATABASE_URL` from before the migration row existed, and
contradicted three rows below it and the quickstart. Worse: nothing said where the database name
came from, and under one reading of it **T047a was testing a refusal that could never fire** —
a branch nobody can reach, written by the pass that was fixing branches nobody runs.
`CORPUS_DATABASE` exists so the refusal is reachable on purpose and unreachable by accident.

**Analysis pass 4 found three things and two of them were damage the earlier passes did.**
The requirement list had run `FR-003, FR-003c, FR-003b, FR-003a` — the sub-letters descending,
because passes 2 and 3 each inserted above what was already there. And **the cleanup verification
ran before the mess it verified**: T041 certified that no corpus database remained, in Phase 4,
while Phase 5 went on to create up to six more. The third was T045's refusal, implemented and
never executed. **The first three passes found defects in the plan; this one found defects in the
fixes**, which is 045's carry-log lesson one level down — a thing classified by one of the
properties it has.

**Analysis pass 3 brought the stack up and ran the chain, and the send returned 403.** An
application credential may send only as a bot, and the corpus as specified created five thousand
people and no bot — so the loop that measures write latency could not write. `migrate.js`,
`createApiKey` and the `PORT=0` spawn all worked on the first attempt; **the only thing that
failed was the one thing nobody had executed.** T013b exists because of it, and T007's row counts
were measured in the same session and were higher than the figures inherited from CLAUDE.md in all
four columns.

**Analysis pass 2 found three more and all three came from one command** — `tail scripts/scale/seed.mjs`. Nothing migrated the corpus database (T012a), nothing minted a credential for the send loop to authenticate with (T013a), and M4 would have measured the wrong database because no task respawned the api against the copy (T033a). **None of the three was visible by comparing the artifacts**: `spec.md`, `data-model.md` and `contracts/seeder.md` all described a seven-table corpus with no credential, consistently, and the precedent beside the new script has emitted one since it was written.

**No task here writes a migration, and three exist to prove none appeared** — T031, T041 and the
verification inside T048. The chapter's subject is that the column should not exist; shipping it
would contradict the argument.
