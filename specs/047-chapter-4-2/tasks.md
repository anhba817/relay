# Tasks — chapter 4.2, ClickHouse from zero

**Feature**: `specs/047-chapter-4-2/` · **Plan**: [plan.md](./plan.md) · **Spec**: [spec.md](./spec.md)

**This chapter builds a schema and a comparison, not a pipeline.** Two ClickHouse tables, a
view, a ledger, and one `INSERT … SELECT` that reads Postgres from inside ClickHouse. **No new
dependency** — `postgresql()` was checked before it was planned and returned the lane's exact
message count (R6).

**Verification methods, stated.** The comparison against 4.1's recorded numbers is **A**. The
ledger's idempotence and its checksum refusal are **D**. **Nothing here joins a test lane**:
`vitest.coverage.config.mts`'s four `include` globs are all `packages/*/src/**` or
`services/*/src/**`, so a test under `analytics/` would be collected by nothing — the same
finding 046 paid for.

**AND THIS CHAPTER'S FENCE DELTA WILL NOT BE ZERO.** 4.1 fenced no platform file and closed at
a delta of 0. This one amends `compose.yaml`, which chapter 1.2 fences as a whole body — so it
carries a **hunked `diff` fence**, the mechanism four Part 3 chapters already use for that file.
**It does not regenerate chapter 1.2's body**: bringing a foundation fence up to date satisfies
the per-chapter checker and takes the cumulative chain from 111 problems to 203 by unanchoring
ninety-two downstream hunks.

---

## Phase 1: Premises, and the numbers this feature inherited

**Everything blocks on this.** Phase 0 found three published documents wrong by running them;
this phase re-runs each at the chapter's own tag, because a premise carried from a planning
document and never re-run is what this project finds most often.

- [ ] T001 Re-run R1 at this chapter's tag and record both halves in `specs/047-chapter-4-2/baseline.txt`: `curl -s "http://localhost:${RELAY_CLICKHOUSE_HTTP_PORT:-8123}/ping"` returns `Ok.` and the same URL with `/?query=SELECT+1` returns `Code: 194 … (REQUIRED_PASSWORD)`. **Use the variable, not the literal** — `compose.yaml` publishes the port as `${RELAY_CLICKHOUSE_HTTP_PORT:-8123}`, and hardcoding a default is how this project ended up needing `RELAY_POSTGRES_PORT=15432`. **If the query now succeeds, the compose amendment is already present and the chapter's opening is wrong** — that is the finding, not an inconvenience.
- [ ] T002 Record the restriction's source in `specs/047-chapter-4-2/baseline.txt`: `docker exec relay-clickhouse-1 cat /etc/clickhouse-server/users.d/default-user.xml`, which limits `default` to `::1` and `127.0.0.1`. Quote it rather than describing it.
- [ ] T003 Re-run R2 and record the exact refusal in `specs/047-chapter-4-2/baseline.txt`: SAD §6.2's `CREATE TABLE` verbatim gives `Code: 450 … BAD_TTL_EXPRESSION`. **Copy the DDL from `docs/05-sad.md` rather than from `research.md`** — the point is that the published document does not apply, and quoting a quotation cannot establish that.
- [ ] T004 [P] Run `pnpm check:fences` in `relay-tutorial` and record the opening in `specs/047-chapter-4-2/baseline.txt` **broken down by kind and locale, not as one number**. **046 inherited 109 and measured 110**; this chapter inherits 110 and re-measures rather than carrying it. At the time of writing that 110 is **APPLY 74 — 30 in `(en)`, 30 in `(vi)`, 14 elsewhere — and HEAD 36, all `(en)`.** **Thirty of them are in the Vietnamese chain, which is under active translation and is not this chapter's work**, so a bare total moves for reasons 4.2 did not cause. FR-015's delta is computed against whatever this run says.
- [ ] T005 [P] Record the lane's row counts fresh in `specs/047-chapter-4-2/baseline.txt`. 046 measured 31,685 environments · 46,143 channels · 303,885 messages · 487,481 outbox on 2026-09-13, **and all four had drifted upward from 045's close-out**. They are part of the instrument for the corpus load.
- [ ] T006 [P] Pin the environment in `specs/047-chapter-4-2/baseline.txt`: node, pnpm, the ClickHouse image tag from `compose.yaml`, the version `SELECT version()` reports, cpus, RAM, and the `DOCKER_HOST` this machine needs.
- [ ] T007 [P] Record in `specs/047-chapter-4-2/baseline.txt` that `packages/config/src/infra.ts` is the only source file naming ClickHouse, and that the lockfile contains no client — so the "zero dependencies" claim is a measurement rather than an intention.
- [ ] T008 Commit phase 1 — `specs/047-chapter-4-2/baseline.txt` only. No platform change yet.

---

## Phase 2: Foundational — a reachable store, and a schema with a ledger

**Blocking for all three stories.** Nothing can be loaded into a store nothing can connect to,
and nothing can be measured against a schema that has not been applied.

- [ ] T009 Amend `relay-platform/compose.yaml`: add an `environment:` block with `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD` and `CLICKHOUSE_DB`. **This adds a NEW user; it does not lift `default`'s restriction** — verified: with `CLICKHOUSE_USER=relay`, `relay` answers from the host and `default` still returns `REQUIRED_PASSWORD`. Anyone trying to fix `default` will edit `users.d/` instead and be editing the image. **Additive**, per chapter 1.2's rule. **`CLICKHOUSE_DB=relay_analytics` creates that database at first start and does NOT make it the session default** — `SELECT currentDatabase()` over HTTP as `relay` returns `default`, so an unqualified `CREATE TABLE` builds the schema in `default` while the provisioned database sits empty. Name that in the comment beside the variable: it is the reason every statement carries `relay_analytics.` explicitly.
- [ ] T010 In `relay-platform/compose.yaml`, replace the health check's command so it **runs a query** rather than `/ping`. This is the one non-additive edit in the chapter and it is a correction: the current check passes while every query is refused, and **a check that cannot fail for the reason you care about is not a check**. **The image has `clickhouse-client` at `/usr/bin/clickhouse-client` and `wget`; it has no `curl`** — `clickhouse-client --user relay --password relay --query 'SELECT 1'` returns `1` inside the container, checked.
- [ ] T011 **Prove the new health check can fail.** Point it at a deliberately wrong credential, confirm `docker compose up --wait` reports the container unhealthy, restore. **Test it red, or it is the old check with a longer command** — and clean up the probe before anything is counted.
- [ ] T012 Create `relay-platform/analytics/0002_schema_applied.sql` — the ledger: `filename`, `applied_at`, `checksum`, `ENGINE = MergeTree ORDER BY filename`. It is applied first and unconditionally, because a ledger cannot record its own creation from a table that does not exist ([contracts/schema.md](./contracts/schema.md)). **And one step above it: `apply.mjs` issues `CREATE DATABASE IF NOT EXISTS relay_analytics` before the ledger.** A ledger cannot live in a database that does not exist either, and under T015a's one-statement rule that `CREATE DATABASE` cannot ride inside this file — it belongs to the script, since any `.sql` file holding it would need a name sorting before `0000` and could not be recorded by the ledger it precedes.
- [ ] T013 Create `relay-platform/analytics/0000_message_events.sql` from SAD §6.2 as **`relay_analytics.message_events`** — the database is named in the statement, which is the fifth divergence and the one that is not about a column — with **four further divergences, each commented**: `toDateTime(ts)` in the TTL (the published statement is refused with `BAD_TTL_EXPRESSION`), **`text_length Nullable(UInt32)`** and **`attachment_count Nullable(UInt8)`** (a tombstone's `lengthUTF8(NULL)` inserts **0**, which claims a zero-length message was sent), and **`user_id Nullable(UUID)`** — `messages.user_id` is nullable and SAD's non-nullable column turns every deleted-author message into the **zero UUID** without failing, which `uniqExact` then counts as one distinct user.
- [ ] T014 Create `relay-platform/analytics/0001_daily_usage.sql` — DR-10's materialised view from SAD §6.2, with **both its own name and its `FROM` qualified**: `CREATE MATERIALIZED VIEW relay_analytics.daily_usage … FROM relay_analytics.message_events`. An unqualified view over an unqualified source is two chances to land in `default` instead of one. It applies only after `0000`: the creation fails with `UNKNOWN_TABLE` otherwise, which was checked.
- [ ] T015 Create `relay-platform/analytics/apply.mjs`: **bootstrap first — `CREATE DATABASE IF NOT EXISTS relay_analytics`, then the ledger (T012) — and only then** read `analytics/*.sql` in filename order, applying what the ledger does not record. **Say the bootstrap here rather than only in the contract**: the ledger is `0002` and sorts last, so "filename order" and "the ledger goes first" reconcile only through a sentence that lived in one artifact, and **print what it applied and what it skipped**. A run that applies nothing prints that it applied nothing — a zero that proves it looked. **The transport is Node's own `fetch` against the HTTP interface** — no client package, which is what makes T018's lockfile check pass by design rather than by luck. Verified: one statement with SQL comments posts `200 OK`, with or without a trailing semicolon.
- [ ] T015a In `relay-platform/analytics/apply.mjs`, **refuse a `.sql` file containing more than one statement**, naming the file. The HTTP interface rejects a multi-statement body with `Code: 62 … Multi-statements are not allowed`, so `analytics/*.sql` is a directory of statements rather than of files that happen to hold some — **and a ledger keyed on filename only means something if a filename is one change.** Refuse up front rather than discover it mid-run.
- [ ] T015b In `relay-platform/analytics/apply.mjs`, **refuse a statement that does not name `relay_analytics`**, naming the file. `CLICKHOUSE_DB` creates the database without making it the session default, so an unqualified statement applies **to `default`, successfully, with no error** — the schema then exists in a place nothing else looks at. `?database=` on the URL also works and is weaker: it lives in the connection, so a statement pasted into `clickhouse-client` lands in `default` again. **Make the case impossible rather than handling it** — a design in which it cannot arise beats a branch that catches it.
- [ ] T016 In `relay-platform/analytics/apply.mjs`, store each file's checksum and **refuse a file whose bytes changed after it was applied**, naming it. ClickHouse has no `ALTER` path for most of what these files do, so a ledger claiming a schema is applied when it is not is worse than one that has not run.
- [ ] T017 In `relay-platform/analytics/apply.mjs`, implement `--drop-all` as **`DROP DATABASE IF EXISTS relay_analytics`** — one named database, not a table-by-table sweep and **not an unqualified `DROP DATABASE`**. Both directions of the unnamed version are wrong and silent: dropping the provisioned database while the tables sit in `default` **returns no error and removes nothing**, and dropping `default` leaves the server answering `SELECT 1` while every unqualified statement fails `Code: 81 … UNKNOWN_DATABASE` with nothing to re-create it. It does **not** re-create the database — T015's bootstrap does, on the next run. **Dropping the source table under a live materialised view succeeds with no error** and leaves the view queryable and returning 0, so a sweep in an unlucky order leaves a view pointing at nothing. Dropping the *view* by name does clean up its hidden `.inner_id` table — that half was checked and is not a leak.
- [ ] T018 Verify `relay-platform/analytics/apply.mjs` uses no ClickHouse client package: `grep -c clickhouse relay-platform/pnpm-lock.yaml` stays at 0 and `package.json`'s dependencies are unchanged (R6). **The check passes because the transport is native `fetch`** — T015 names it, so this task confirms a design rather than discovering an absence.
- [ ] T019 Commit phase 2 — `relay-platform/compose.yaml`, `relay-platform/analytics/`. Gates first: `pnpm lint && pnpm typecheck && pnpm test` in `relay-platform`.

---

## Phase 3: User Story 1 — the same question, answered by a store shaped for it (Priority: P1) 🎯 MVP

**Goal**: FR-ANL-05's question asked of ClickHouse and published beside 4.1's 585.9 ms.

**Independent test**: load the corpus, run the query, publish the duration, the rows scanned and
the `EXPLAIN indexes=1` line beside the predecessor's figures.

- [ ] T020 [US1] Create `relay-platform/scripts/scale/load-analytics.mjs`: one `INSERT INTO message_events SELECT … FROM postgresql('postgres:5432', …)` over **three** tables — `messages` joined to `channels` for the tenant, and `message_edits` for the edit events (T020a). The two-table join was checked and returns 303,885; the three-table chain was checked and returns **3,935 rows across 505 environments**. **`message_edits` carries no tenant column**, so an edit event's `environment_id` arrives through two joins — `message_edits → messages → channels`. It is the first row in this feature that does not get its tenant directly, and constitution I is why that is worth a sentence rather than a shrug. **Three expressions are not the obvious ones**, and `data-model.md` §1 carries the measurements:

        text_length        lengthUTF8(text)        NOT length() — that is bytes, and
                                                   FR-EMJ-02 counts code points
        attachment_count   JSONLength(attachments)  NOT length() — jsonb arrives as
                                                   Nullable(String); a 2-attachment
                                                   row measured 151
        user_id / text_length / attachment_count   all three targets are Nullable:
                                                   4,056 tombstones + 1 text-less
                                                   live message, 301,644 null
                                                   attachment lists, 20,541 null senders

  **Never the text itself** (FR-ANL-11, DR-08).
- [ ] T020a [US1] In `relay-platform/scripts/scale/load-analytics.mjs`, **write one row per EVENT, not one per message** — `created` at `created_at`, plus `edited` at `edited_at` and `deleted` at `deleted_at` where those are not null. SAD §6.2's column is `created|edited|deleted` and `daily_usage` filters on it, so **a load that labels everything `created` inflates FR-ANL-05's messages-sent by every deletion** — 4,056 for the lane. **Take the edit rows from `message_edits`, which holds one row per edit — not from `messages.edited_at`, which holds only the latest**: 3,935 against 3,201, **734 events lost across the 428 messages edited more than once** (max 3). One row per event is the rule this task states, and `messages.edited_at` is one row per edited *message*. Expect **311,876 rows from 303,885 messages** — 303,885 + 3,935 + 4,056. **Unlike T020b's tombstones this history is not gone**; it is in a table the loader already opens.
- [ ] T020c [US1] In `relay-platform/scripts/scale/load-analytics.mjs`, define `text_length` **on the `edited` rows** — it is the length the message had **after** that edit, and `message_edits` does not hold it. **It chains**: edit *k*'s resulting text is edit *k+1*'s `prior_text`, and the last edit's resulting text is `messages.text`. Measured through `postgresql()`: **3,160 recoverable, 775 NULL**. **Use a null-safe test for "no next edit", not `prior_text != ''`** — the probe that produced these counts used the empty-string test and was right only because no row in this corpus has empty prior text.
- [ ] T020d [US1] **Publish the 775 as the same 775.** They are the messages edited once and then deleted: for the `created` event that edit row is what makes the length recoverable (T020b), and for the `edited` event the deletion is what destroys it. **One row, two events, opposite outcomes** — FR-ANL-02's emit-at-the-time rule argued in a single figure rather than asserted.
- [ ] T020b [US1] In `relay-platform/scripts/scale/load-analytics.mjs`, leave `text_length` **NULL** where it cannot be recovered, and **report the count**. **4,056 messages are tombstones and one more is a live message with no text** — `text IS NULL` counts 4,057, `deleted_at IS NOT NULL` counts 4,056, and the difference is a single undeleted row carrying attachments and no words. Both get a NULL `text_length`, for two different reasons, and **the chapter must not teach that NULL text means deleted.** Of the tombstones, only **775** carry an edit row with `prior_text`; chapter 3.23 preserves none for a deletion — *"a tombstone has no text to preserve"*. **Take the EARLIEST edit's `prior_text`, with `argMin` on `edited_at`** — that is the text as sent, and **428 messages carry more than one edit row**, which an `any()` picks among arbitrarily. **3,282 creations have no recoverable length** — 3,281 deleted and never edited, plus the one live text-less message —, and that is the argument for FR-ANL-02's emit-at-the-time rule arriving three chapters before the ingester: a store reconstructed from current state cannot recover what the state no longer holds.
- [ ] T021 [US1] In `relay-platform/scripts/scale/load-analytics.mjs`, report **what the table holds after the load, not what was sent**. The TTL removes rows **at insert** — 120,000 over 120 days became 90,000 immediately, with no error — so a loader quoting its own INSERT is quoting an intention (R3).
- [ ] T022 [US1] Create `relay-platform/analytics/query.mjs` taking `--environment`: FR-ANL-05's daily question against `message_events`, reporting duration, rows scanned, and `EXPLAIN indexes=1`.
- [ ] T023 [US1] In `relay-platform/analytics/query.mjs`, publish the **parts and granules** line from `EXPLAIN indexes=1`. **`ProfileEvents['SelectedParts']` returned 0 for the same query** (R5), so the obvious instrument reports nothing and reports it silently — and at this size a full scan answers quickly enough to look ordered.
- [ ] T024 [US1] Build the corpus with `scripts/scale/corpus.mjs` and load it. Record the emitted JSON and the post-load ClickHouse count in `specs/047-chapter-4-2/baseline.txt`, **with the difference between them named as the TTL**.
- [ ] T025 [US1] Take the measurement and record it in `specs/047-chapter-4-2/baseline.txt` **beside 4.1's 585.9 ms and its 1,000,000 rows**, quoted from `specs/046-chapter-4-1/baseline.txt` with the corpus and machine they were taken on. **4.1's Postgres measurement is not re-run** (FR-014, constitution III).
- [ ] T026 [US1] Record the `EXPLAIN indexes=1` output in `specs/047-chapter-4-2/baseline.txt` with all three stages — MinMax, partition, primary key — because two of the three skip nothing and only the third is the ordering doing work.
- [ ] T027 [US1] **If the second store is not faster, publish that.** Record the volume, the plan and what it does not prove rather than tuning the query until it agrees. 4.1's hypothesis was falsified twice and the chapter was better for it.
- [ ] T028 [US1] Commit phase 3 — `relay-platform/scripts/scale/load-analytics.mjs`, `relay-platform/analytics/query.mjs`, `specs/047-chapter-4-2/baseline.txt`. Gates first.

---

## Phase 4: User Story 2 — a rollup that never scans raw events (Priority: P2)

**Goal**: DR-10's claim, measured — and the conflict it has with FR-ANL-06, recorded.

**Independent test**: query the rollup for the same ninety days and compare it, row for row and
figure for figure, against the raw table.

- [ ] T029 [US2] In `relay-platform/analytics/query.mjs`, add a rollup mode querying `daily_usage` for the same range with **`sum(messages)` and `GROUP BY day`**, reporting duration and rows scanned. **A bare `SELECT messages` is wrong**: the rollup holds one row per insert per key until a background merge, and three inserts on one day measured `1000 1000 1000` where the truth was 3000.
- [ ] T030 [US2] Compare the rollup's daily figures against the raw table's **day by day and inside the 90-day window on BOTH sides** — not row by row, because the rollup holds more rows than days — and record the comparison in `specs/047-chapter-4-2/baseline.txt`. A count that matches in total and not per day is a different defect. **Without the window the comparison is between two different populations**: the materialised view counts rows the TTL deletes in the same insert, so a 120-day corpus leaves the raw table 90 days and the rollup 120. Measured: 120,000 rows in, **raw 90,000 over 90 days, rollup 120,000 over 120**, and **inside the window 90 days in common with 0 disagreements**.
- [ ] T030a [US2] **Record how many rows the rollup holds per `(environment_id, day)` before any `OPTIMIZE`**, in `specs/047-chapter-4-2/baseline.txt`. That number is the reason T029's query shape is not optional, and it is the figure a reader needs to understand why their own dashboard query returned a fraction.
- [ ] T031 [US2] Record the row ratio and **re-measure it rather than carrying the 89**. The probe that produced *1,000,000 raw rows became 89 rollup rows* ran before it was known that the rollup keeps the days the TTL removes, so the full corpus adds out-of-window days the probe never counted. That ratio is DR-10's argument in one number, which is why it has to be this corpus's number.
- [ ] T032 [US2] In `relay-platform/analytics/query.mjs`, add `--compare-exact`: `uniqMerge(active_users_state)` against `uniqExact(user_id)` over the raw table, **both restricted to the same 90-day window**, reporting the difference as a number. **Unwindowed, this instrument prints a real number about the wrong thing** — 120 days of rollup against 90 days of raw, a difference that is mostly TTL, handed to FR-009 and T034 as `uniq`'s approximation error. **A delta between two totals is not a measurement of the thing that changed unless nothing else changed.**
- [ ] T033 [US2] Insert rows after the rollup exists and confirm it includes them **without being rebuilt** (FR-005). A view somebody refreshes is a table with extra steps.
- [ ] T033a [US2] Record in `specs/047-chapter-4-2/baseline.txt` that **`daily_usage` carries no TTL and outlives the events it was built from** (FR-003a). The raw table drops a day at 90; the rollup keeps that day's figures forever, because it counted them at insert. **That is DR-09 and DR-10 working as a pair** — metering must not lose history when raw events expire — and it is the half a reader meets as a 30-day discrepancy in T030 unless the chapter says it first.
- [ ] T034 [US2] **Measure where `uniq` stops being exact** and record the table in `specs/047-chapter-4-2/baseline.txt`: exact to 60,000 distinct, **off by 0.51% at 70,000**. **Take this from a population where the two sides hold the same rows** — T032's window — or the approximation error arrives with the TTL folded into it, and 0.51% is small enough for that to swamp it. **The threshold is a cardinality, not a row count** — which is why the corpus's 5,000 users hide it completely.
- [ ] T035 [US2] Record the conflict in `specs/047-chapter-4-2/gaps.md`: **FR-ANL-06 wants 0.1% and DR-10 forbids reading raw events**, so above roughly 65,000 distinct senders neither path satisfies both. **File it for movement IV** — there is no reconciler here to test an amendment against, and amending a clause without one is deciding before measuring.
- [ ] T036 [US2] Commit phase 4 — `relay-platform/analytics/query.mjs`, `specs/047-chapter-4-2/baseline.txt`, `specs/047-chapter-4-2/gaps.md`. Gates first.

---

## Phase 5: User Story 3 — a second store's schema needs a ledger of its own (Priority: P3)

**Goal**: schema changes that are idempotent and say what they did.

**Independent test**: apply to an empty store, apply again, add a statement, edit an applied
file — and confirm the fourth is refused.

- [ ] T037 [US3] Apply the schema to an empty ClickHouse and record what `apply.mjs` printed in `specs/047-chapter-4-2/baseline.txt`, **including the database and ledger the bootstrap created before the first file**. "Empty" here means the database does not exist, which is the state `--drop-all` leaves behind.
- [ ] T038 [US3] Apply it again and record the output. **It must say it applied nothing**, not print nothing.
- [ ] T039 [US3] Add a fourth statement file, apply, and confirm **only that statement runs**.
- [ ] T040 [US3] **Test the checksum refusal red**: edit an already-applied file's bytes, run `apply.mjs`, and confirm it refuses and names the file. Restore afterwards and confirm `apply.mjs` is quiet again. **046's first two falsifications failed for the wrong reason** — one on a JS error rather than the constraint, one on a count the check does not read — so confirm the refusal fires on the checksum and not on something incidental.
- [ ] T041 [US3] Verify `analytics/apply.mjs` writes nothing to Postgres: `schema_migrations` is unchanged and `services/api/migrations/` still ends at `0014_connection_minutes.sql` (FR-012, SC-007).
- [ ] T042 [US3] Record in [contracts/schema.md](./contracts/schema.md) any field or behaviour added after the contract was written, and say which task forced it. **A contract written by one caller is a contract written by one caller's opinion.**
- [ ] T043 [US3] Run `--drop-all`, then verify with **`SELECT count() FROM system.tables WHERE database = 'relay_analytics'`** and confirm the lane's row counts match T005's. **Name the database in the check**: `system.tables` returns **0** for a database that does not exist rather than erroring, which is what makes this honest — while a check that counted tables in whichever database the connection happened to be on would have reported a clean drop with `message_events` still standing. Each phase drops what it made.
- [ ] T044 [US3] Commit phase 5 — `relay-platform/analytics/`, `specs/047-chapter-4-2/`. Gates first.

---

## Phase 6: The chapter, the amendments, and closing out

- [ ] T045 Choose the slug and create `relay-tutorial/app/(en)/part-4/chapter-02/<slug>/page.mdx`.
- [ ] T046 Write the opening of `.../page.mdx`: 4.1 ended with a 656 ms sort no index removes. This chapter builds the ordering that is that sort's answer.
- [ ] T047 Write the section that **amends SAD §6.2 in `docs/05-sad.md`** — `TTL toDateTime(ts)` — and quotes the refusal. A published DDL that does not apply is amended, not silently diverged from.
- [ ] T048 Write the health-check section of `.../page.mdx`: the store has been in compose since chapter 1.2, `/ping` has been green throughout, and nothing outside the container could query it. **Name the subject, not the ordinal** (045 FR-008).
- [ ] T049 Write the measurement sections of `.../page.mdx` carrying the query, the rollup, both `EXPLAIN indexes=1` lines and the comparison against 4.1, each with the rows it scanned.
- [ ] T050 Write the rollup-accuracy section: exact to 60,000, off by 0.51% at 70,000, and **FR-ANL-06's 0.1% against DR-10's prohibition**. State the conflict; do not resolve it.
- [ ] T051 Write the `<ForwardRef>` in `.../page.mdx`: no ingester, no emission path, no reconciliation, and `delivery_latency_ms` created with no producer until FR-ANL-10's chapter.
- [ ] T052 **Publish the `compose.yaml` amendment as a hunked ```diff fence** in `.../page.mdx`, following the four Part 3 chapters that already amend that file. **Do not regenerate chapter 1.2's whole-body fence** — that satisfies the per-chapter checker and unanchors ninety-two downstream hunks.
- [ ] T053 **Generate the hunk from the checker's own replay, not from `git diff`.** Copy `check-fence-chain.mjs`, truncate it at the HEAD comparison, dump its end state, diff that against the working tree, delete the copy. `-U6` is a default and not a rule: **verify the hunk applies clean before pasting, not after.**
- [ ] T054 [P] Write `relay-tutorial/app/(en)/part-4/chapter-02/<slug>/figures.ts` — at least two figures: the two orderings against the two questions, and where the rollup's row count comes from.
- [ ] T055 [P] Add at least one `TRAP` box to `.../page.mdx`. The strongest candidate is the TTL removing rows at insert with no error, which cost a quarter of a corpus in the probe — **and its sharper half: the rollup counted those rows on the way past**, so the only surviving trace of a deleted quarter is a figure in the view.
- [ ] T056 Register the chapter in `relay-tutorial/lib/tutorial.ts` with a Vietnamese title.
- [ ] T057 Create `relay-tutorial/app/(vi)/vi/part-4/chapter-02/<slug>/` with `specs/046-chapter-4-1/vi-placeholder.py`, mirroring every fence (045 FR-010/FR-011). **Invent no Vietnamese** beyond the standing notice and the registry's own title.
- [ ] T058 Run `node scripts/prose-words.mjs` in `relay-tutorial` against `.../page.mdx` and record the count. The bound is 2,000–4,000 outside fences (SC-008).
- [ ] T059 Run `pnpm check:fences` and record the closing figures **in T004's breakdown — kind and locale — and report the delta per line, not only the total** (FR-015). **It will not be 0** — this chapter amends a fenced file, unlike 4.1. **A total that moved in `(vi)` is somebody else's translation, not this chapter's chain**, and only the breakdown can tell them apart. Third time in this feature that a delta needed the thing beside it held still.
- [ ] T060 [P] Run the remaining gates and record each in `specs/047-chapter-4-2/baseline.txt`: `lint`, `typecheck`, `test`, **`build`** in `relay-platform` **first**, then `check:docs`, `check:srs`, `check:figures`, `check:errors` in `relay-tutorial`. `check:errors` reads `packages/protocol/dist`.
- [ ] T061 Write `specs/047-chapter-4-2/traceability.md`: FR-001…FR-015 and SC-001…SC-008 against the tasks that verify them, with the method actually used.
- [ ] T062 Complete `specs/047-chapter-4-2/gaps.md` — starting with T035's clause conflict, `delivery_latency_ms`'s missing producer, the three Part 1 tags from `046-8`, and the two gates `docs/12` §6 still says must exist.
- [ ] T063 Tag the chapter `part4-ch2`, annotated, following the convention 046 settled.
- [ ] T064 Confirm no analytical table and no `relay_corpus*` database remains, the lane's counts match T005's, and `services/api/migrations/` is unchanged. Then commit phase 6 across all three repositories and update `CLAUDE.md`'s `<!-- SPECKIT -->` block with the close-out figures.

---

## Dependencies & Execution Order

```
Phase 1  premises        ──> everything. T001 can falsify the chapter's opening.
Phase 2  store + schema  ──> US1, US2, US3 all need it
Phase 3  US1 (P1) 🎯     ──> US2 needs the corpus loaded
Phase 4  US2 (P2)        ──> independent of US3
Phase 5  US3 (P3)        ──> independent of US2; both need Phase 2
Phase 6  the chapter     ──> needs US1 and US2's numbers
```

### User story dependencies

- **US1** depends on Phase 2 only. It is the MVP: the question answered by a store shaped for
  it, beside 4.1's number, is the chapter's reason to exist.
- **US2** depends on US1's loaded corpus. The rollup is compared against the raw table, and
  both need rows.
- **US3** depends on Phase 2 and nothing else. It could run before US1.

### Parallel opportunities

- Phase 1: T004–T007 are four independent recordings — `[P]`.
- Phase 6: T054, T055 and T060 touch different files from the prose tasks — `[P]`.
- **Phases 2 to 5 have none that matter.** The schema files are ordered by dependency, and
  measurements are serial: nothing else runs on the machine during one.

## Implementation strategy

**MVP is Phases 1 + 2 + 3.** That yields a chapter that asks 4.1's question of a store built
for it and publishes both answers with what each scanned. The rollup strengthens it; the ledger
is what lets movement II change the schema.

**Stop points that are real:**

- **T001 can falsify the chapter's opening.** If ClickHouse is already reachable, the
  health-check finding is not this chapter's to make and §1 of the prose changes.
- **T003 likewise.** If SAD §6.2's DDL now applies, someone amended it and the chapter says so
  rather than claiming the discovery.
- **T027 and T034 are where the chapter may disagree with its own plan**, and both say to
  publish the disagreement.

## Notes

**ANALYSIS PASS 6 FOUND THE COMPARISONS HAD NO WINDOW.** The materialised view fires on the
insert and the TTL deletes on the same insert, **and the view goes first**: 120,000 rows over
120 days leave the raw table holding 90,000 over 90 and the rollup holding **120,000 over 120**,
with 30 days of figures for rows that never persisted. T030 compared day by day over everything
and T032 compared whole table to whole table, so both would have printed a real number about the
TTL and handed it to FR-009 as `uniq`'s error. **Inside the window the two agree exactly — 90
days in common, 0 disagreements.** SC-002 already carried "for the same ninety days" from pass 3;
**the spec was ahead of the tasks that verify it**, which is the reverse of this feature's usual
direction. One thing came back clean: `uniqState`/`uniqMerge` ignore NULL exactly as `uniqExact`
does, both returning 5 over a population holding 500 NULL senders, so pass 1's `Nullable(UUID)`
fix survives into the rollup.

**ANALYSIS PASS 5 FOUND THAT `analytics/` HAD NO ADDRESS.** Every artifact described what
the statements do and none said **where they go**, and the default is not the one compose
provisions: `CLICKHOUSE_DB=relay_analytics` creates that database without making it the session
default, so SAD §6.2's unqualified `CREATE TABLE` lands in **`default`** — no error, and the
provisioned database sits empty beside it. **The cleanup then cannot catch it in either
direction**: `DROP DATABASE relay_analytics` removes nothing and returns nothing, `DROP DATABASE
default` leaves the server answering `SELECT 1` while every unqualified statement fails
`Code: 81`. Four premises checked in the same pass came back clean — the vi placeholder's regex,
the migration tail, the five gate scripts, and the four-chapters-to-one-body fence precedent.
**The pass found no wrong fact; it found a missing one.**

**ANALYSIS PASS 4 WENT TO THE ARTIFACT THAT WAS WRONG IN 046 AND WAS READ LAST.** The
contract's invocation line said `RELAY_POSTGRES_PORT=15432 node scripts/scale/../../analytics/apply.mjs`
— a Postgres variable on a ClickHouse script, and a traversal for a path the quickstart writes
plainly. **046 carried the identical defect and it took six passes to open the file**; knowing
where it hid is the only reason this took four. The same pass found that the HTTP interface
refuses multi-statement bodies, which decides the shape of every `.sql` file, and that dropping
a source table under a live view succeeds silently.

**ANALYSIS PASS 3 WENT LOOKING FOR TWO THINGS AND FOUND NEITHER**, which is worth recording
because the eleven passes before it across two features all found what they went looking for.
`SummingMergeTree` handles `uniqState` correctly — 1,500 against the raw table's 1,500, across
three parts, before and after a merge — and the event filter survives pass 2's change, rolling
1,210 mixed events down to the 100 creations among them. **What it did find** is that the rollup
holds one row per insert per key until a merge, so the read contract is `sum()` with `GROUP BY`
and SC-002's "row for row" was false of the rows.

**ANALYSIS PASS 2 ASKED PASS 1'S QUESTION OF THE COLUMNS PASS 1 DID NOT ASK IT ABOUT.**
`user_id` was not the only nullable source column: `text` is NULL for 4,057 tombstones and
`attachments` for 301,644 of 303,885 rows, and both insert **0** into a non-nullable target.
**The fix is where the next defect is**, and pass 1's fix was incomplete in exactly the
direction pass 1's finding described. Pass 2 also found `event = 'created'` written for 4,056
deleted and 3,201 edited messages, in a table whose rollup filters on that label.

**ANALYSIS PASS 1 FOUND FOUR THINGS AND ALL FOUR CAME FROM ONE `SELECT`.** Three of the load's
eight column expressions were wrong — `length(attachments)` gives 151 for two attachments,
`length(text)` gives bytes where FR-EMJ-02 counts code points, and a NULL `user_id` becomes the
**zero UUID** in SAD §6.2's non-nullable column, inventing one active user per environment. The
fourth was that the compose fix adds a user rather than lifting `default`'s restriction.
**`data-model.md`, `contracts/schema.md` and `tasks.md` agreed with each other that `length()`
gave what the column meant**, and the data arrives as a different type than the name implies.

**Three numbers in this feature are inherited and T004, T005 and T025 exist to replace or quote
them properly**: `check:fences` at 110, the lane's row counts, and 4.1's 585.9 ms. The first two
are re-measured; the third is **quoted with the corpus and machine it was taken on**, because
re-running 4.1's measurement is not this chapter's work and re-deriving it would be.

**The compose amendment is the riskiest artefact here and it is one hunk.** Four Part 3 chapters
already amend that file the same way, so the mechanism is precedent rather than invention — but
`resume.itest.ts` needed `-U10` where `-U8` was worse, and the rule is to verify before pasting.
