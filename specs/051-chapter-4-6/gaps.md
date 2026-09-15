# Gaps — 051, chapter 4.6, "the rollup nobody read"

**Six new entries, and all eight carried items re-measured.** Two of 050's eight are closed
by this chapter and one is closed by a clause that was always there.

---

## 051-1 — `message_events` STILL HAS NO PRODUCER, AND THREE QUANTITIES REST ON IT

The chapter's subject, carried forward because the chapter deliberately did not fix it.
Measured at the opening and unchanged at the close: **0 rows**, zero occurrences under
`services/`, one batch loader. `api_requests` holds 11,683 and `connection_events` 154.

Messages sent, unique active users and stored message count all derive from it, so three of
FR-ANL-05's four quantities are columns with a view and no data. The billing rollup ships
with them present and empty, which FR-001a decided out loud: a column reading 0 for a tenant
that sent messages would be worse.

**Cost to close**: a fourth arm on the ingester's `route()` and a producer on the send path.
The producer is the expensive half — it is the busiest path in the platform, and Part 3's
counters already maintain the same quantity synchronously in `usage_periods` for a reason
`docs/12` §4 argues. **The honest sequencing is a chapter, not a task**, and until it exists
DR-10's clause is satisfied by a rollup nothing can fill.

## 051-2 — CONSTITUTION III FORBIDS THE ONLY WAY TO DEMONSTRATE ITS OWN CLAUSE

*"Analytical queries MUST NEVER execute against the operational database (PostgreSQL);
billing, metering, and dashboard analytics read only from the analytical store (ClickHouse),
fed via a durable queue."*

Metering reads **only** Postgres today. And every cost figure in this chapter came from a
corpus loaded by `load-analytics.mjs:53` — `postgresql('${PG_HOST}', …)`, ClickHouse
executing a query against Postgres, the clause's first prohibition.

SRS revision 1.13 records the conflict with its measurements. **The amendment itself is the
constitution's and this feature could not write it.**

**Cost to close**: a constitution amendment, a new ADR, or a recorded exception — the three
forms named in the SRS entry. The decision is cheap; finding it again from scratch is what
this entry prevents.

## 051-3 — `pnpm test:integration` REPORTS ONE FAILURE WHERE THREE LANES FAIL

Measured at T078: the log holds exactly one `FAIL` line while the summary says
`Tasks: 6 successful, 9 total`. The api lane printed `cache bypass, force executing` and no
test output at all. A reader taking the visible line at face value concludes one test failed.

Asked directly, `request-log.itest.ts` fails 5 of 5 and `reset-lane.itest.ts` passes 3 of 3
alone. Neither is visible from the gate's own output.

**This is the gate a chapter is told to run and believe.** 050's close diagnosed four red
suites by name; this run would have hidden three of them.

**Cost to close**: an hour. `turbo run` with `--output-logs=full`, or a summary step that
re-prints each failing task's tail. The failure mode is worse than a missing gate, because
the number it prints looks like an answer.

## 051-4 — TWO ROLLUPS NOW, AND NOTHING CHECKS THEY AGREE

`daily_usage_billing` and `daily_usage_v2` carry the same four quantities at different
grains, fed by four views over two sources. Nothing compares them. Measured once by hand
during this chapter, they disagreed by 2,670 messages — one day the TTL had removed — and
that disagreement was correct rather than a fault.

**Cost to close**: a query, and a decision about what a legitimate difference looks like. It
belongs with FR-ANL-06's reconciliation (chapter 4.7), which already has to answer the harder
version of the same question against operational counts.

## 051-5 — A BACKFILL CANNOT RECOVER WHAT THE TTL ALREADY TOOK

Measured: the view counted 242,667 messages over 92 days and a backfill taken minutes later
found 239,997 over 91. The difference is the oldest day, deleted by `message_events`' 90-day
TTL **during the insert** — the view fires first.

The rollups carry a 25-month TTL and the raw table 90 days, so the rollup is meant to outlive
its source. **Which means a rollup created late is permanently short**, and every deployment
that adds one to a store with history inherits a hole it cannot fill.

**Cost to close**: nothing, for this platform — both rollups exist now and the raw retention
has not yet cut anything they hold. It is a deployment note rather than a defect, recorded
because the next store to gain a rollup will be an old one.

## 051-6 — THE EXCERPT-AS-WHOLE-BODY TRAP CAUGHT THIS CHAPTER TWICE IN ONE DRAFT

`metering.ts` and `0006_daily_usage_v2.sql` were each fenced with a `title=` while showing
part of the file, and the checker read both as whole bodies. CLAUDE.md records the `diff`-
inside-a-`ts`-fence form of this; the partial-quote form is the same rule and is not written
down anywhere a drafter would meet it.

**Cost to close**: a sentence in `docs/07` — a titled fence is a whole-body claim, so quote
partially only without a title — or a checker that warns when a titled fence is a strict
subset of the file it names. The second is better and is perhaps twenty lines.

---

# Carried, re-measured

## 050-1 — `pnpm coverage`'s false "No test files found" — **DID NOT RETURN**

Its close asked for exactly this: run the lane at the next chapter's opening and write down
which behaviour appears. Run three times across this feature — 108 files at the opening, 109
at the close, 545.85 s and 554.69 s — and **the "no test files" behaviour did not appear
once**. Still unexplained, now with five clean observations against one bad one. **T058 and
T059's successors were also done**: `metering.ts` is pinned at 100 on all four and the sweep
is 50 of 50 binding.

## 050-2 — The analytical store has no lane guard — **UNCHANGED, AND THIS CHAPTER LEANED ON THE CONVENTION**

`metering.itest.ts` uses a dedicated environment id and scopes every count by it, because
nothing makes it. The chapter also ran `TRUNCATE` on three shared tables and `OPTIMIZE TABLE
… FINAL` on one during measurement — both lane-wide, both unguarded, and both invisible to
`check-lane-scope.py`, whose `SHARED` array is Postgres tables and whose last line is *"SQL
text only"*. **Five chapters write this store from tests now.**

## 050-3 — The vi chain is never compared to the tree — **UNCHANGED, AND THIS CHAPTER TOUCHED A FOURTH FILE**

`services/ingester/src/clickhouse.ts` carries a Vietnamese whole body, and T007 measured it
**already stale** before this chapter edited it. `vitest.coverage.config.mts` carries one
too, also already stale. So this chapter adds to a debt it did not create and that no gate
reports: the checker compares the vi chain against the English chapter's fences and never
against `relay-platform`.

## 050-4 — Eleven of the HEAD problems are fences whose title names no file — **UNCHANGED, AND USED**

Still 25 `differs at line` against 11 `does not exist`, identical at the opening and the
close. This feature reported its delta with the split, which is what the entry asked for.

## 050-5 — A clean stop publishes a ledger saying connections are still open — **UNCHANGED**

Untouched by this chapter. It is now upstream of a billing number rather than of a
dashboard: connection-minutes come from close records, so a deploy's worth of opens with no
closes is a deploy's worth of minutes never billed.

## 050-6 — `internal.test.ts` has no base in the chain — **UNCHANGED**

## 050-7 — `bound-port.test.ts` diverged before 4.5 — **UNCHANGED**, and one of 050-4's 25.

## 050-8 — 4.4's integration suite needs a process no gate starts — **CONFIRMED AGAIN, TWICE**

`request-log.itest.ts` fails 5 of 5 with nothing draining, measured at this chapter's opening
and again at its close. **And 051-3 makes it worse**: the gate that runs it no longer shows
which tests failed, so the next chapter reading `pnpm test:integration`'s output would not
learn what this one had to run a suite directly to find.

## 047-3 / 048-4 — "no clause says how long metering history is kept" — **CLOSED, AND THE PREMISE WAS FALSE**

**DR-09 says it**: *"Raw events shall be retained for 90 days; daily aggregates for 25
months."* Both entries were quoting DR-10, which is the next row down in the same table.
Three features carried a missing clause that was adjacent to the one they cited.

Applied at `0014` and `0015`: `TTL toDateTime(day) + INTERVAL 25 MONTH` on both rollups. It
does not contradict FR-003a — 25 months against 90 days outlives the source roughly
eightfold, and *"not the raw table's TTL"* is all that decision ever asked for.
