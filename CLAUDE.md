**FEATURE 045 IS CLOSED.** Its record is `specs/045-part-3-rework/` — `gaps.md` first
(**82 entries; 74 through 82 are the lane rework**), then `baseline.txt`, `carry-log.md`,
`traceability.md` and `tasks.md`. 044's is `specs/044-revision-watermark/`, 043's is
`specs/043-fix-review-findings/`.

**PART 3 IS 26 CHAPTERS, REGROUPED INTO EIGHT CONTIGUOUS SUBJECT MOVEMENTS AND RENUMBERED.**
**Twenty-one of the twenty-six numbers mean a different chapter than they did**, and four
numbers exist before and after pointing at different content — so **name a chapter, never
number it**. `specs/045-part-3-rework/chapter-map.json` is the one record; the mapping page
`relay-tutorial/app/(en)/part-3/whats-moved` publishes it and carries the fresh-start
database instruction. Everything deferred is still Part 4's: hosted media
(`media_not_available`) is **4.10 and 4.11** — this line said 4.5 and 4.6 until analysis pass 8,
which is `docs/12` §3's table rows 11 and 12 read as current when the table deliberately keeps
pre-contraction ordinals — the queryable attempt log is 4.2, FR-MOD-03's audit log is 4.7.
**Name a Part 4 chapter by its movement and title, not its number**, for the reason Part 3
already taught.

**THE REBUILT CHAIN IS `main` NOW.** 228 commits replaced by 230, diverging at the end of
Part 2; the old history is tagged `backup/pre-main-move-20260911` in all three repositories.
One annotated tag per chapter (`rework/part3-chN`, unpadded) with `rework/base-convention` as
chapter 1's base — **not `rework/part3-base`, which does not exist and which a gate silently
passed on twenty-six times**. `pnpm check:fences` runs for real against it and reports **109**,
the number the patched checker reported throughout the rebuild.

**AND IT IS PUSHED.** `relay-platform`'s `main` was force-pushed over 227 commits of published
history; the replaced history is preserved on the remote as the tag
`backup/pre-main-move-20260911` in all three repositories, alongside the 27 `rework/*` chapter
tags. **Anyone holding an older clone of `relay-platform` must reset rather than pull.**

<!-- SPECKIT START -->
**052 IS CLOSED at 87 of 87 — CHAPTER 4.7, "the job that checks the meter".** Its record is
`specs/052-chapter-4-7/` — `baseline.txt` first, then `gaps.md` (**23 entries: 7 new, 15
carried and re-measured, and 047-1/048-1 closed by amendment**), `traceability.md`, `tasks.md`.
Tagged **`part4-ch7`**.

    the aggregate 0.2630% · 49 of 1,385 tenant-periods over the bound · 0 non-fixture
    uniq exact to 65,536 · 0.5676% at 65,537                    the cliff is one user wide
    the TTL gap is 0% at midnight and 1.0989% before the next   047's 0.49% is one point on it
    check:fences 110 -> 110, delta 0 · 2,265 prose words · 11 gates · 33 tests · SRS 1.14

**FR-ANL-06 CANNOT PASS, AND THREE OF THE FOUR REASONS ARE NOBODY'S FAULT.** So the chapter's
product is a clause amendment, not a green number. SRS 1.14 states which operational table the
job means per quantity, that the comparison is per tenant, that absence has verdicts of its
own, and where its own bound is unreachable. **Amending the requirement is the whole of what a
chapter can do about an obstacle that is a design decision.**

**"COUNTS DERIVED FROM OPERATIONAL DATA" IS NOT ONE NUMBER.** `messages` through `channels`
holds 19,012 and `usage_periods.messages_sent` holds 18,962 — 0.2630% aggregated, **49 of
1,385 tenant-periods over the bound**, and every disagreement attributable to a fixture. **Two
mechanisms pushing opposite ways**: a raw `INSERT INTO messages` bypasses the counter (seven
call sites), and `history-drift.itest.ts:85`'s hard `DELETE FROM messages` removes a row the
counter already counted. **0 of 1,385 disagree for a non-fixture reason**, because `sendMessage`
writes the message and increments the counter in one transaction.

**AND 1,317 TENANTS ARE ONE-SIDED, WHICH IS ALL OF THEM.** 4 environment ids in
`daily_usage_billing`, none of which exist in Postgres at all; 1,313 with operational usage and
none with a rollup row. `not-comparable` and `no-data` are not edge cases here — they are the
answer, and collapsing them into "missing data" lets the platform's largest defect read as an
absence of evidence.

## BOTH OBVIOUS WAYS TO PLANT A 0.1% DRIFT PASS

Against an operational 100,000, measured against the real job:

    99,900   -100   0.100000%   pass      "0.1% under" — the naive shortfall
    99,899   -101   0.101000%   breach
   100,100   +100   0.099900%   pass      "0.1% over"  — the naive excess
   100,101   +101   0.100898%   breach

`max(a, o)` is the denominator and the comparison is `<=`, so **the smallest breaching drift is
101 in both directions** and a drift computed off the smaller side lands inside the bound.
Changing `<=` to `<` turns exactly one test red, which is how you know the boundary cases sit
ON the bound. **AND THE THRESHOLD HAS NO RESOLUTION AT LANE SCALE**: at a tenant's real nine
connection-minutes the smallest possible drift is **11.11%**, a hundred times the bound — every
drift breaches, so a green 0.1% assertion there claims nothing drifted at all.

    volume        9    100    1,000   10,000   100,000
    smallest      1      1        2       11       101
    as a %   11.111  1.000    0.200    0.110     0.101

## `pnpm coverage` WAS ANSWERING WITH SILENCE, AND HAD SINCE 4.4

`coverage.reportOnFailure` defaults to **false**, so one red test suppresses the whole report:
no table, no per-file threshold errors, no `coverage/` directory — only `Coverage enabled with
v8`. Run both ways over the same three files: green printed the table and every threshold
error, one red printed neither. `request-log.itest.ts` has been red on any machine with no
ingester since 4.4 (050-8). **Silence is indistinguishable from a pass at a glance.** Turned on,
and the first reporting run found `services/ingester/src/shape.ts` failing its 100% pin at
95.12 — left at 100 rather than lowered, because this chapter made it visible rather than
measuring it down.

**AND `pnpm test:integration` RUNS THREE OF ITS SIX LANES.** `--dry=json` plans 18 tasks; the
run attempts **9** and prints `Tasks: 7 successful, 9 total`. `--concurrency=1` means turbo
stops scheduling at the first failure, so **every lane ordered after the api has not executed
under that command since 4.4** — the gateway's 225 tests among them, and the gateway lane had a
red of its own that run. 051-3 read this as a summary that collapses lanes; it is worse.

## READ THE CLAUSES, AND ONE OF THEM POINTED AT NOTHING

**`FR-003a` IS NOT A CLAUSE, AND TWO PUBLISHED DOCUMENTS CITED IT AS ONE.** `docs/04-srs.md`'s
DR-09 and `docs/05-sad.md:879` both wrote it as a requirement id. **There is no `FR-003` in the
SRS**; `FR-003a` is feature-local and four features use it to mean four different things. And
the sentence it sat in was false: *"the rollups carry no TTL"*, when 4.6 gave both a 25-month
TTL **in the same feature that paragraph was written in**.

**AND ADR-06 HAD ASSUMED CONSTITUTION III's ANSWER ALL ALONG.** Its accepted trade-off reads
*"mitigated because the only strict consumer (metering) reconciles daily against Postgres
(FR-ANL-06)"* — so the cross-store read is **the mitigation that makes choosing NATS over Kafka
acceptable**, not an oversight. Five features cited both documents without reading them beside
each other. The reading that holds: **the reconciler is none of the three roles III names — an
auditor confined to one side of a fence cannot check the fence.** Recorded in SRS 1.14 and the
SAD; the amendment is still the constitution's (`gaps.md` 052-6, after 051-2).

## WHAT RUNNING IT COST, AND EVERY ONE WAS AN INSTRUMENT

- **A LINT RULE IS A CONSTITUTION CLAUSE.** The Postgres read went inline in `metering/` and
  failed: *"'drizzle-orm' import is restricted … the query engine lives inside the repository
  layer only (constitution I, ADR-16)"*. **The plan put the job in the api BECAUSE the api owns
  the repository and never noticed the wall between them.** It lives in `db/usage-reads.ts`.
- **4.6's FACT RAN THE OTHER WAY.** *A bare aggregate with no `GROUP BY` always returns exactly
  one row* — 4.6 used it to delete a guard; here it made an empty result set unreachable, so
  "holds nothing" and "holds zero" became the same answer. `count()` is the first column now.
  And the arm is reachable for a non-aggregate: `SELECT 1 WHERE 0` really does answer `[]`.
- **A `diff` FENCE CARRIES THE `@@` HUNKS ONLY.** Pasted complete from `git diff -U6`, the
  `--- a/` and `+++ b/` headers are read as body text: 112 problems, `hunk pre-image matched 0
  times — starts "-- a/compose.yaml"`. Dropping two lines took it to 110, delta 0.
- **A GLOB IS AN INSTRUMENT.** The coverage-pin sweep's first run named 17 pins unbindable and
  **all 17 are real files**: `git ls-files 'services/*/src/**/*.ts'` misses every file directly
  in a `src/`, where picomatch — which is what vitest uses — matches it. 53 pins, 53 binding.
- **`pnpm -s <script>` REPORTS RED FOR A GREEN GATE.** All four tutorial gates read RED under
  `-s` and GREEN under `pnpm run`. Every figure was re-taken.
- **A FIRE-AND-FORGET `ALTER … DELETE` LEFT A ROW FROM AN EARLIER RUN.** Issued by hand the same
  statement removed it in under four seconds. **What the fire-and-forget form lacks is evidence
  that it ran**, so the cleanup polls AND asserts a count of 0.
- **A TITLE OVERCLAIMED AND THE AUDIT CAUGHT IT.** *"however much analytical data exists"*
  asserted only the empty case. Fixed by making the title true. 33 tests audited, 0 with no
  assertion, 0 conditional.
- **AND AN EDIT WAS INVISIBLE TO THE FENCE CHAIN.** `vitest.coverage.config.mts` gained four
  changes and the delta did not move, because **a checker reports the first failure per file**
  and that file has diverged at line 29 since before Part 4 (048-3). The zero is real and it
  counts one divergence where there are now three.

**051 IS CLOSED at 94 of 94 — CHAPTER 4.6, "the rollup nobody read".** Its record is
`specs/051-chapter-4-6/` — `baseline.txt` first, then `gaps.md` (**15 entries: 6 new, 8
carried re-measured, and 047-3/048-4 closed**), `traceability.md`, `tasks.md`. Tagged
**`part4-ch6`**.

    the rollup read 32,778 rows · the raw table 32,768   for the same tenant-month
    147,534 rows keyed (env, channel, day) · 281 keyed (env, day)      525x
    56 calendar minutes against 0.6513 elapsed                          86x
    check:fences 110 -> 110, delta 0 · 2,302 prose words · 11 gates, 9 green

**THE BRIEF ASKED FOR A ROLLUP THAT HAD EXISTED SINCE 4.2, AND NOTHING READ IT.**
`analytics/0001_daily_usage.sql` shipped two chapters earlier. `grep` finds two references: a
comment, and `analytics/query.mjs`, which opens *"FR-ANL-05's daily question, asked of the
analytical store"* and is referenced by no script, service or config.

**AND THE ONE TABLE IT READS IS THE ONE TABLE NOTHING WRITES.** `message_events` 0 rows,
`api_requests` 11,683, `connection_events` 154, `webhook_attempts` 64 — and **zero occurrences
of `message_events` under `services/`**. Three of FR-ANL-05's four quantities come from it. So
DR-10's *"billing never scans raw events"* was satisfied, for two chapters, by a rollup over a
table that receives no events, read by a file nothing runs. Both halves conform to the clause.

**THE COUNTS HOLD STILL WHILE THE STREAM CLIMBS, AND THAT IS THE CHAPTER'S FIRST FIGURE.**
13,265 held, then 13,481 minutes later, every table count unchanged. **The tables move when an
ingester drains, not when the platform works** — constitution III's independence in two
commands. T001 had blamed `/healthz` polls for a drift that does not happen.

## WHAT A CORPUS SAID THAT SEVEN ANALYSIS PASSES DID NOT

**THE ROLLUP READ MORE ROWS THAN THE RAW TABLE.** One tenant's 91-day bill, from
`system.query_log`:

    against daily_usage_v2 (env, channel, day)   32,778 rows · 3.56 MiB · 4 ms
    against message_events, the same question    32,768 rows · 1.31 MiB · 3 ms

4.2 published 315 rows against 1,052,655 for this clause. **The cause is the key and not an
unmerged table**: 147,534 distinct `(env, channel, day)` keys against 286 `(env, day)` keys
over 2,400 channels, and `OPTIMIZE FINAL` changes nothing. **FR-ANL-09's channel dimension
and DR-10's cheap read cannot share a key.** Two rollups ship. The compression says it in one
pair: 248,155 raw rows become **281** at `(env, day)` — 884× — and **147,534** with channel —
1.7×, which is an index with extra steps.

**R6 ASKED THE WRONG QUESTION AND WAS RIGHT.** It measured `channel_id` on the row and
concluded it *"costs a key column, not a join"*. True, and about storage. **What it costs the
READ needed a corpus**, and no analysis pass loaded one.

**A MATERIALISED VIEW IS A TRIGGER ON FUTURE INSERTS, NOT A QUERY OVER HISTORY.** The first
comparison of the chapter failed: rollup 0, raw 56, over records already in the table. Proven
with a control — one new close moved it to 2 while the rest stayed at 0. **So DR-10 is empty
without a backfill on any store that already holds data, and it reads as working without one**,
because every new record appears.

**AND A BACKFILL RECOVERS ONLY WHAT STILL EXISTS.** The view counted 242,667 messages over 92
days; a backfill minutes later found 239,997 over 91. The difference is one day — the one the
90-day TTL removed **during the insert**, because the view fires first. The rollups carry no
raw TTL precisely so they outlive it, which means **a rollup created late is permanently
short**. Build it with the table, not after.

## THE UNIT, DECIDED AT 86x, AND A CLAUSE THAT FORBIDS ITS OWN DEMONSTRATION

**SRS APPENDIX C QUESTION 4 IS CLOSED** — open since before Part 4, owner *Product /
Billing*. A connection-minute is a **calendar minute during any part of which a connection was
open**, which is what `meter.ts` has billed since 3.24, so the two agree by construction rather
than by reconciliation. The argument is 56 against 0.6513 over 55 real closes, median
connection **252 ms**: a client reconnecting every quarter-second holds a slot continuously and
pays almost nothing on elapsed duration. What is given up is in the clause — short connections
over-report against wall-clock intuition.

**AND THE CORPUS COMMAND IS THE VIOLATION.** Constitution III forbids analytical queries
against Postgres; `load-analytics.mjs:53` is `postgresql('${PG_HOST}', …)`. **The only way to
demonstrate the rollup the clause asks for is to run the thing the clause forbids** — which is
the strongest available argument that `message_events` needs a producer. Recorded in SRS 1.13
rather than amended, because the amendment is the constitution's own (051-2).

**AND DR-09 HAD SAID IT ALL ALONG.** *"Raw events shall be retained for 90 days; **daily
aggregates for 25 months**."* `gaps.md` 047-3 and 048-4 both read *"no clause says how long
metering history is kept"* — while quoting DR-10, **the next row down in the same table**.
Three features, two entries, an adjacent clause. Applied at `0014`/`0015`; it does not
contradict FR-003a, because 25 months against 90 days outlives the source eightfold and *"not
the raw table's TTL"* is all that decision asked for.

## WHAT RUNNING IT COST, AND EVERY ONE WAS AN INSTRUMENT

- **`corpus.mjs` REFUSES `CORPUS_DAYS=60`** — it needs more than the 90-day query window, and
  `message_events` TTLs at 90. **They cannot both be satisfied**, so a conforming corpus always
  produces the rollup/raw discrepancy. Analysis pass 5 wrote 60 into the quickstart and nobody
  ran it. `load-analytics.mjs` also needs `--corpus <corpus.json>`, which the same block omitted.
- **A TEST THAT ASSERTS THE WRONG READ IS WRONG DEPENDS ON A MERGE NOT HAVING HAPPENED.** Three
  versions: three rows of 1000 (failed, already merged), `{1000, 3000}` (failed, a *partial*
  merge gives 2000 and 1000), then the invariant — the rows sum to 3000 in every state.
- **A MUTATION IS NOT A DELETE.** `clean()` used `ALTER TABLE … DELETE` and returned; the next
  test read three creations where it planted two. It polls `system.mutations` now.
- **100/100/100/100 BY DELETING BRANCHES.** `metering.ts` measured 50% branches twice. Both
  arms were unreachable, and one carried a comment I had written in the same commit claiming a
  test drove it. **A bare aggregate with no GROUP BY always returns exactly one row.**
- **TWO CHECKS RETURNED A CONFIDENT ZERO ABOUT THE WRONG QUESTION.** `engine_full LIKE '%25
  MONTH%'` read as a failed `ALTER` — the server normalises to `toIntervalMonth(25)` and the TTL
  is not in `engine_full`. And `require.resolve('pg')` from the workspace root read as a broken
  `corpus.mjs`, which imports the api's pool and loads fine.
- **A TITLED FENCE IS A WHOLE-BODY CLAIM.** Two excerpts published with `title=` took the chain
  to 113. Both are new files, so publishing them whole cost nothing (051-6).
- **AND `pnpm test:integration` REPORTED ONE FAILURE WHERE THREE LANES FAILED** — one `FAIL`
  line against `Tasks: 6 successful, 9 total`, with the api lane printing no test output at all.
  Asked directly: `request-log.itest.ts` 5 of 5 red (050-8, no ingester), `reset-lane.itest.ts`
  3 of 3 green alone. **The gate a chapter is told to run and believe** (051-3).

**AND THE MANIFEST STEP FAILED FIRST, ON PURPOSE-ADJACENT GROUNDS.** The registration edit
matched two anchors and was refused, so `pnpm build` said `Error: Unknown chapter id: 4.6` —
4.4's failure reproduced, and the only one of eleven gates that notices.

**050 IS CLOSED at 114 of 114
**050 IS CLOSED at 114 of 114 — CHAPTER 4.5, "the gateway's first stream".** Its record is
`specs/050-chapter-4-5/` — `baseline.txt` first, then `gaps.md` (**19 entries: 8 new and all
11 carried items re-measured**), `traceability.md`, `tasks.md`. Tagged **`part4-ch5`**.

    close -> row readable   min 2.0 s · p50 5.7 · max 5.8   9.7% of FR-ANL-04's 60 s
    60/60 acked broker down · 139 retained · 0 dropped
    403.5 B a record on the real stream — 26% heavier than the synthetic 320
    check:fences 110 -> 110, delta 0 · 2,330 prose words · 11 gates, 9 green
    dependency count 5 -> 6 · event.ts 100/100/100/100 · 35 tests added

**THE GATEWAY ALREADY REPORTED CONNECTION DATA, WHICH `docs/12` DID NOT SAY.** `meter.ts` has
shipped connection-minutes to `/internal/usage/connections` every sixty seconds since 3.24. So
the chapter is not *"the gateway has no way to report"* — it is **"the one it has was built for
a different question and goes through the service the analytical path is supposed to be
independent of."** And `session.ts`'s close handler had already refused to do what this chapter
wanted, in writing since 3.24: *"a mass disconnect would turn one event into a burst of HTTP
requests."* **A publish per close is the same burst on a different transport**, so the records
buffer and flush on a tick exactly as the meter does.

**"BATCHED" MEANT THE WAITING, NOT THE PAYLOAD, AND FOUR PASSES DID NOT ASK WHICH.** A research
row read *"batched 500 per publish"* — which is 500 records in ONE message — and three
artifacts adopted it in that form with three requirements built on top. It breaks three claims
the feature had already published: one message carries one subject and the subject carries the
tenant; one message carries one `Nats-Msg-Id`, so `{connection_id}:{event}` cannot hold across
500; and **the shipped ingester destroys it** — an array has no `type`, so `route()` takes the
attempt arm and `ingest.ts` calls `m.term()`, 500 records gone counted as one malformed. **The
units in the three rows were the only tell**: two said *publishes* and the third said *records*.

**AND THE MEASUREMENT THEN MOVED 7.6x WHEN THE SHAPE WAS CORRECTED.** Planning read 0.0034 ms
a record; measured in the shape that shipped it is **0.0260** — 11x faster than awaited, not
67x, and **ten times core speed, not 1.13 times**. The decision survives on the smaller margin,
which is worth more than the old figure was. Corrected in six places.

**AND THE UNAUTHENTICATED CONNECTION CANNOT ARISE.** Five artifacts carried it as a decision and
the plan's constitution check read *"PASS, with one open case"*. `open()` is the only function
that builds a `Connection`, it takes a **non-optional** `Identity`, and its one call site is
reached only after 429, 4001, 1011, 4003 and 4008 have each returned — three of which complete
the handshake in order to close it. **An unauthenticated socket exists and an unauthenticated
connection does not**, so 4.4's `_none` arm is unnecessary rather than declined. **A design in
which a case cannot arise beats a branch that handles it.**

**AND `MAX_CONNECTIONS_PER_USER = 5` IS A CEILING ON "N CONNECTIONS".** A task said *"open and
close N connections, assert 2N records"* and never said across how many users. The sixth socket
is refused with close **4004**, which returns before `open()` and produces no record — so ten
sockets as one user assert 20 and measure 10, and the failure reads as ten lost records rather
than five refused connections. **Reading cannot find what the schema refuses**, and a cap is
the same kind of refusal.

## WHAT RUNNING IT FOUND THAT READING COULD NOT

**A CLEAN STOP PUBLISHES A LEDGER SAYING TEN CONNECTIONS ARE STILL OPEN.** Ten connections
opened and closed inside one flush window, then the process ended two ways:

    clean stop (SIGTERM)   opened 10 | closed 0      of 20 expected
    kill      (SIGKILL)    opened  0 | closed 0      of 20 expected

`sessions.close()` calls `wss.close()`, which **does not close established sockets**, so no
per-socket close handler fires and no close record is ever enqueued — which `session.ts` says
at :335 for a different reason entirely. **Zero of twenty is visibly wrong; ten opens with no
closes is not**, and a dashboard subtracting closes from opens drifts up by a full instance on
every deploy. Held past two flush intervals the kill costs nothing, because the opens have
already gone; inside the window it costs everything. The two bound the loss from both ends.

**THE COVERAGE LANE WAS RECORDED DEAD AND IS NOT.** Phase 4 measured `pnpm coverage` printing
`No test files found, exiting with code 1`, reproduced it in a `part4-ch4` worktree, and blocked
two tasks on it. T095 ran the same command against the same config: **108 files, 1,545 tests,
511 seconds.** The conclusion drawn from the dead lane — that 049's 100/100/100/100 must have
come from somewhere else — is withdrawn; the workspace lane now reports the same figure. **One
instrument here produced a false "nothing to see" and nobody can yet say why** (050-1).

**AND 4.4's INTEGRATION SUITE NEEDS A PROCESS NO GATE STARTS.** `request-log.itest.ts` polls
ClickHouse for a row only the ingester can write, to a 20-second deadline, and **there is no
ingester service in `compose.yaml`**. Measured: 5 passed with one running, 5 failed without.
That suite discharges 4.4's SC-001 and is green only for an operator who happens to have a
process alive (050-8). This chapter's own suites were checked the same way and need nothing.

**THE VIETNAMESE CHAIN IS NEVER COMPARED TO THE TREE.** `check-fence-chain.mjs:265` iterates
**`en.state`**; the vi chain is replayed and then compared against the ENGLISH chapter's fences
(MIRROR), never against `relay-platform`. So three vi whole bodies are stale today —
`shape.ts`, `clickhouse.ts` and `main.ts`, all in vi 4.3 — and every gate is green. T010c
predicted two and missed the third. **A prediction that the instrument would show something is
a claim about the instrument**, and the delta of 0 was real (050-3).

**ELEVEN OF THE 36 INHERITED HEAD PROBLEMS ARE NOT DRIFT.** Split by what the checker says:
**25 are `<path> differs at line N`** and **11 are `<title> does not exist in relay-platform`**
— fences titled with a prose phrase rather than a path (*"the ladder against the registry"*,
*"the typo, now"*). They can never be repaired by editing the platform. The headline 110 is
eleven units pessimistic, and 25 is the number a chapter should be measured against (050-4).

**A BATCH REDELIVERED INTO ITSELF AND THE COUNT WAS THE ONLY TELL.** `ingestOnce` reported 16
for a stream holding 8: `ack_wait` of 1 s against a 2,000 ms fetch window. Diagnosed by printing
the stream's own depth, not by reasoning about the consumer.

**AND TURBO'S CACHE HID A TWO-CHAPTER-OLD RED.** `bound-port.test.ts` had been failing since
4.3 — the ingester arrived and its `BINDS_NOTHING` entry did not — and the `test` task's cache
key does not cover another package's `main.ts`. This chapter's `compose.yaml` edit busted the
key and the failure appeared. **A green lane is a claim about what was re-run.**

## READ THE CLAUSES, NOT THE IDENTIFIERS — THREE CITATIONS POINTED AT CLAUSES THAT DO NOT SAY IT

Eleven passes read the platform, the tutorial and the structure record; the twelfth opened the
SRS the quotations point at.

- **DR-11 names neither number.** It governs the SHAPE of an insert — *"batched or asynchronous;
  single-row synchronous inserts are prohibited"*. The 2 s and 10,000 rows are
  `docs/05-sad.md:182`'s, and `ingest.ts`'s comment is the furthest-travelled copy of a figure
  credited to the wrong clause. DR-11 carries them now.
- **NFR-SCL-01 carries no memory figure.** The 160 MB is SRS revision 1.9 and `docs/11`, which
  measured **157 against a 160 budget**. Cite the source that holds the number and compare
  against 157, not the rounded ceiling.
- **No clause forbade a credential in an analytical record.** FR-ANL-11 governs message text and
  NFR-SEC-06 governs application logs; neither reaches it. The authority is **constitution III's
  allow-list** — *"only lengths, identifiers, and metadata"* — which refuses by construction.
  **An allow-list is the citation; a deny-list about something else is not.**
- **FR-ANL-04's qualifier was dropped four times.** The clause is *"within 60 seconds … **under
  normal conditions**"*, and the retry rule is what makes the qualifier load-bearing: a record
  published during a broker outage is queryable minutes late and that is not a breach.

**AND AN ADR LIVES IN TWO DOCUMENTS — THE SAD'S SUMMARY AND `docs/06`'s ARGUMENT.** Ten passes
amended the summary and none opened the 98-line deep dive, which states the two lines this
chapter falsifies more fully than the SAD does. **The mapping is the argument and the gateway
half is the half it is named for**: *"Choosing Redis keeps a clean mapping — gateway to Redis,
api and workers to NATS."* 3.8 and 3.18 broke the api half and the deep dive records the cost as
*"relocated rather than avoided"*; this chapter puts it on the gateway, which is where the
analysis refused to put it, and afterwards the mapping describes nothing. **What is falsified is
the arithmetic beside the refusal**, not the refusal: the gateway holds two clients either way,
so NATS fan-out would now add none and remove none, and ADR-07 survives on Redis alone.

**AND CONSTITUTION VII SAYS ADRs ARE IMMUTABLE** — *"superseding requires a new ADR"* — while
ADR-07 carries two in-place amendments. Precedent does not decide it and the constitution names
only one form, which makes **the missing sentence the defect rather than either choice**.
Decided out loud rather than defaulted.

## THE MEASUREMENTS WORTH CARRYING

**403.5 BYTES A RECORD, 26% HEAVIER THAN THE SYNTHETIC FIGURE TWO CHAPTERS HAVE IN PRINT.**
Reconstructing 4.4's method reproduced 5.55 and 38.8 rec/s exactly from 320 B — which is what
made the method trustworthy before it was applied to anything new. Then the stream's own
accounting over 3,992 real messages said 403.5. **The 7-day crossover is 4.40 rec/s, not 5.55.**
And a third producer spends the budget outright: **two connection-pairs a second takes the
request allowance from 5.55/s to 0.86/s.** 4.4 corrected this figure once already for a 2%
subject-length error; it is still a quarter light of production.

**TWO CONNECTION-MINUTE COUNTERS THAT MEASURE DIFFERENT QUANTITIES.** The meter charges every
calendar minute a connection was open for any part of; the records give elapsed duration. **2
against 0.03 for the same connection.** The reconciliation compares buckets against buckets —
one quantity computed twice — and publishes the duration/bucket gap as a number so nobody reads
it as a defect. Scoped to connections with BOTH records present, because unscoped it would have
compared 8 against 0.

**AND THE RECORD'S KEY NEEDS `event` IN IT.** One connection produces two rows with one
`connection_id`; without `event` in the sorting key a `ReplacingMergeTree` collapses the open
into the close. Verified against the server: `count() FINAL` 2, not 1.

## THE HABITS THIS FEATURE PAID FOR AGAIN

- **The fenced-file list was remembered, not counted — eight files, not five.** Both the plan and
  the tasks named a set that was wrong in both directions: `ingest.ts` carries no titled fence
  anywhere, and `vitest.coverage.config.mts` carries 23. **A list of fenced files goes stale
  every time a chapter moves code between files.**
- **The tutorial had not built since 4.4 shipped.** `<ChapterHeader id="4.4" />` throws on an
  unregistered id, so `pnpm build` exited 1 from the moment 049 closed — at 112 of 112 with
  eight gates green. **None of the eight rendered a page.** `pnpm build` is a gate now, and
  registering the chapter is a task no requirement had named.
- **The vi path that was checked has never existed.** An assumption read *"`app/(vi)/part-4/` is
  still empty"*; the tree is **`app/(vi)/vi/part-N/`**, so that check could only come back empty.
  **A zero from an instrument is a claim about the corpus only if the instrument can be shown to
  have read it** — and here the instrument was a path.
- **A probe copied from 049 kept the hazard and dropped the guards.** A task named the
  `SYSTEM STOP MERGES` and not the `finally`, the scoped `DELETE` or the dedicated environment
  id. **Copy the shape, not the sentence.**
- **A pass's own fix was the next pass's defect**, twice. The fix is where the next defect is,
  now including this cycle's own repairs.
- **Sixteen analysis passes, and none of the last four found anything in the tree** — they found
  the artifacts' own agreement with each other. **The pass that RUNS the premise finds the most.**


**049 IS CLOSED at 112 of 112 — CHAPTER 4.4, "the requests that belong to nobody".** Its
record is `specs/049-chapter-4-4/` — `baseline.txt` first (842 lines), then `gaps.md` (six
entries), `traceability.md`, `tasks.md`. Tagged **`part4-ch4`** on `relay-platform`.

    54 requests · 34 with no tenant    application 20/20 attributed, platform 18/18 tenantless
    broker up 2.61 ms · down 2.45      200 each side, all 200s — down is FASTER
    320 bytes a record                 5.5 req/s fills 7 days · 38.8 breaks the SAD's 24 h
    check:fences 110 -> 110, delta 0   2,393 prose words · 8 gates · 6 fences, all diffs

**"EVERY REQUEST" AND "PER TENANT" ARE NOT THE SAME POPULATION.** FR-ANL-01 wants an event for
every API request; FR-ANL-07 wants a log per tenant. Every 404, every 401, `/healthz`, signup —
and **every call the dispatcher and gateway make on the internal seam**, because
`PlatformPrincipal` carries `environmentId?: undefined` BY DESIGN and its own comment says the
absence is what stops it being usable where a tenant is expected. **The gap is widest exactly
where the traffic is.**

**CONSTITUTION I FORBIDS THE RECORD FR-ANL-01 REQUIRES, AND THE THIRD READING IS THE ONE THAT
HOLDS.** Drop them and "every" is false for the busiest routes; invent an environment and 047's
zero-UUID phantom user is back; **or the clause governs tenant DATA, and a record with no tenant
is not tenant data.** Only worth anything because it is testable: tenant A's exact filter saw 1
and tenant B's 0 over a stream of six candidate tokens, and a tenant-scoped read returns that
tenant's rows and **zero** tenantless ones.

**THE CONSUMER SHIPPED LAST CHAPTER DESTROYED EVERYTHING THIS ONE SENDS, AND BOTH INSTRUMENTS
SAID NOTHING WAS WRONG.** `analytics-ingester` filters on `analytics.>` and `shape()` knows one
record type; `null` means `m.term()`.

    pass 1: written 1  malformed 1      the attempt wrote — that is the positive control
    pass 2: written 0  malformed 0      terminated, never comes back
    stream still holds 2 of 2 · consumer num_pending 0 · ack_pending 0

`retention: Limits` keeps a terminated message, so depth says the record is there and lag says
there is nothing to do. **`route()` now decides what a record IS before anything shapes it**, so
"not mine" stops being the same answer as "malformed".

**NO MIDDLEWARE POSITION GIVES BOTH PROPERTIES, AND FINDING THAT OUT TOOK THREE ANALYSIS
PASSES.** `RateLimitMiddleware` refuses a 429 with `res.end(); return;` and **never calls
`next()`**, so a producer registered last never runs for a rate-limited request — the one an
operator opens a request log to find. Registered SECOND it does, because **the listener's
registration point and its read point are different moments**: it attaches before anything can
short-circuit and reads `req.principal` when `finish` fires. **Attach early, read late.**

**AND TWO OF `refused_at`'s FOUR ARMS ARE NOT OBSERVABLE.** A guard refusal and a handler
response are byte-identical from the producer — same status, same `req.route`, same properties —
so `middleware` and `guard` are STAMPED and `unmatched` and `handler` inferred. **The `handler`
arm is an inference from silence**, so a future guard that refuses without stamping is recorded
as a plausible wrong value. The guard against that walks the api's source for every
`CanActivate` and was run red by deleting the stamp.

**A REMEDY BUILT ON A FUNCTION NOBODY OPENED.** Pass 3 prescribed "the limiter already knows
which route it matched" across four artifacts. `operationsFor` returns `[]`, `["rest"]` or
`["rest","send"]` — quota classes, three-valued. **The question was mis-posed too**: this
platform does not limit per endpoint, so a per-endpoint breakdown of its refusals describes a
mechanism that does not exist. The record carries `limited_operation` from `refusal.operation`,
which the limiter already narrows to word the 429 body.

**THE COLUMN TYPE WAS WRONG AND ONLY TRAFFIC SAID SO.** Lint, typecheck, 27 unit tests, the
schema applied and `SHOW CREATE` verified — then `Code: 27. Cannot parse input: expected ','
before '.556'`. `latency_ms` was `UInt32`; the producer reports fractional milliseconds.
**Rounding would have been one line and the wrong fix**: three of four real requests are under
1 ms and would have read 0. Nothing was lost — the insert threw, nothing was acked, and the
records waited on the stream.

**AND `LowCardinality(String)` CANNOT SAY "ABSENT".** An absent field and an explicit `""` both
land as `''`, which is 048's defect on a different column — and **none of 048's three guards
reaches it**: skip-unknown-fields catches an UNKNOWN field, not an absent one, and a CHECK
cannot help because absent is legal for `endpoint`.

**THE BYTE COUNT INCLUDED THE INSTRUMENT.** Two probes read 313 and 315 bytes a record; the
stream's accounting counts the SUBJECT and the probes' subjects differed by two characters.
Measured across three lengths: 51 chars → 313.0, 53 → 315.0, **58 → 320.0**, which is the real
subject. Every figure derived from 313 was 2% light.

**048-6's RECORDED CAUSE IS WRONG, AND THIS CHAPTER MADE THE FAILURE PERMANENT.** It blamed an
ABRUPT `compose down`. A graceful `compose stop` does it too, and so does `restart` — **the
stream that fails to recover is whichever is being WRITTEN**, proven with a control (api
stopped → clean) and a deliberate reproduction under load. Before 4.4 the api wrote to
`ANALYTICS` once per webhook attempt; it now writes on every request and Docker polls `/healthz`
every five seconds, so **the stream is never idle and every restart lands mid-write** (049-1).

**AND THE COMPOSE API CANNOT CREATE A STREAM IT DOES NOT HAVE.** `replicas > 1 not supported in
non-clustered mode` — `replicaCount()` returns 3 under `NODE_ENV=production` and the Dockerfile
sets it. 474 publish failures accumulated while the streams were missing. It hid because the
streams were first created from OUTSIDE the container, which is also why 048-6's own repair
appeared to work (049-2).

**`check-lane-scope.py` REPORTS ZERO BECAUSE IT LOOKS AT NOTHING.** Line 28 hardcodes a worktree
045 deleted; the glob matches nothing and it exits 0 with all ten controls firing. **That is the
rule its own feature wrote**, and the controls cannot catch it: synthetic strings checked in
memory fire whether or not the corpus is empty. **A control that proves the checker WORKS says
nothing about whether it LOOKED.** Retargeted: 50 files, 0 unscoped reads (049-3).

**CONSTITUTION VI's 100%-BRANCH CLAUSE IS MET RATHER THAN PINNED, FOR THE FIRST TIME IN PART
4.** It names tenant isolation, and this chapter's tenancy branch — a tenant's subject against
the `_none` arm — is in `event.ts` at 100/100/100/100. 048 recorded the same clause as
unreachable because its idempotency was a sorting key and **a schema has no branches to cover**.

**AND A PIN THAT COULD NOT FAIL WAS FOUND BY SWEEPING FOR IT.** `vitest.coverage.config.mts`
excluded `**/main.ts` and also pinned `services/ingester/src/main.ts` — 45 per-file pins, exactly
1 unbindable. `ingestOnce` moved to `ingest.ts`, measured 76.66/75/100/75 against 048's silent
41/33/25/40, and **both halves of the probe were run**, which is the step 048 skipped.

**THE FENCE CHAIN CHARGED FOR SIX FILES THIS CHAPTER TOUCHED.** The first draft carried no
fences and the chain went 110 → 116: six files that earlier chapters publish as whole bodies no
longer matched the tree. Six `diff` hunks against `part4-ch3` took it back to **110, delta 0**.
A whole body would have been the 111 → 203 trap.

**047 IS CLOSED at 74 of 74 — CHAPTER 4.2, "the store that was never listening".** Its
record is `specs/047-chapter-4-2/` — `baseline.txt` first, then `gaps.md` (five entries),
`traceability.md`, `tasks.md`. Tagged **`part4-ch2`** on `relay-platform`.

    13.22 ms against 4.1's 585.9 ms   both best of 3, both 91 days, same question
    315 rows read against 1,052,655   the rollup, for 19% less time
    90 of 91 days agree exactly       the 91st cannot, by 4,941 — 0.49% vs a 0.1% bound
    check:fences 110 -> 110, delta 0  2,580 prose words · 8 gates green · 6 fences, 0 problems

**THE STORE HAD BEEN UNREACHABLE FOR SIXTEEN CHAPTERS BEHIND A GREEN TICK.** `/ping`
neither authenticates nor is network-restricted, so it answered `Ok.` while every query
from outside the container was refused. **A check that cannot fail for the reason you care
about is not a check** — and the two halves do not even name the same mechanism: the image
restricts by NETWORK and the caller sees an AUTHENTICATION error. Write down what the
failure looks like from outside, not what the config file says.

**FOUR TASK PREMISES WERE FALSIFIED BY RUNNING THEM, AND ALL FOUR ARE IN `baseline.txt`.**
**(1)** `CLICKHOUSE_DB` creates nothing on a volume that already holds a database — the
entrypoint prints `Skipping initialization` and the variable is read and ignored, so
`apply.mjs`'s `CREATE DATABASE IF NOT EXISTS` is the only thing that ever makes it.
**(2)** T001's falsification could not fire: `default` is refused identically before and
after the fix, so the discriminator had to become whether `relay` answers. **A test whose
condition cannot occur is a test that cannot fail.** **(3)** The TTL is a **schedule, not
an event** — an insert landing in one part is cleaned immediately, one landing in nine is
not: 121 days and 146,582 expired rows still present straight after the load, 91 days after
the merge. **A row count taken the moment a load finishes shrinks overnight on its own.**
**(4)** T059 predicted a non-zero fence delta; it is 0, because the chapter fenced exactly
what it changed.

**THE ROLLUP AND THE RAW TABLE DISAGREE ON ONE DAY AND ALWAYS WILL.** The TTL cuts at a
TIMESTAMP and a daily rollup's finest grain is a DAY, so the oldest day in the window is
counted whole by the view and then partly deleted from the source. 90 of 91 days agree
exactly; the 91st differs by 4,941. **That is 0.49% against FR-ANL-06's 0.1%, at any
cardinality** — a second, independent reason DR-10 and FR-ANL-06 conflict, and worse than
the `uniq` one because no corpus size hides it. The distinct-user half came back
**5,000 against 5,000, 0.0000%**, over a corpus of 5,000 users: `uniq` is exact to 65,000,
so that zero is a fact about the corpus and is published beside the table proving it.

**A CORPUS OF CREATIONS CANNOT SHOW WHAT THE CHAPTER IS ABOUT.** `corpus.mjs` wrote seven
columns and no attachments, edits or deletions, so three of the four column findings were
invisible in the store the chapter builds — every row `created`, `attachment_count`
uniformly NULL, and `'corpus <n>'` ASCII where `length` and `lengthUTF8` agree exactly. It
has four ratios now. **And its first extension was wrong in a way that looked right**:
`cross join lateral generate_series(1, 1 + floor(random() * 3)::int)` evaluates the
volatile argument ONCE PER QUERY, giving exactly three edits to every message. Reporting
the counts rather than asserting them is what caught it.

**THE LEDGER CAUGHT A FILE THAT CHANGED AND NOTHING THAT VANISHED.** Deleting a statement
file left four ledger rows against three files, its table still in the store, and the
runner saying `skipped 3` — because the run walks the DIRECTORY. **An instrument that walks
one side of a relationship only tells you about that side.** It reports the orphan now.

**THE THREE PART 1 TAGS WERE NOT ORPHANED, THEY WERE WRONG.** 046-8 recorded them as
unreachable. They also pointed at a **superseded lineage**: `main` carries rebuilt
equivalents with byte-identical subjects and trees differing by 11-13 files, seven of them
fenced — and `part1-ch4` already sat on the new lineage while 1.1-1.3 sat on the old, which
is why no single angle looked wrong. Chapter 1.2 publishes `INFRA_SERVICES` over five lines
and the old `part1-ch2` held it on one. Measured fence by fence, **old tags matched 14 of 20
whole-body fences, the new ones match 19 of 20.** Moved, annotated, pushed; the old lineage
is kept as `backup/part1-orphan-lineage-20260913`, pushed first.

**AND NOTHING COULD HAVE CAUGHT IT.** `check-fence-chain` replays onto the working tree and
compares against `HEAD` — it never resolves a tag, so the chain was green the whole time.
**No gate in these three repositories checks that a chapter's tag matches the chapter**,
which is exactly what `relay-platform/README.md:8` promises. `gaps.md` 047-6 files the one
fence that matches neither lineage (`turbo.json` at 1.1, prettier drift in both directions).

**AND `eslint.config.mjs` COULD NOT TAKE A FENCE.** The chain replays 206 lines where the
tree holds 451 — a 243-line divergence predating this chapter, one of the 36 inherited HEAD
problems. A hunk cannot anchor on it and regenerating it is the 111 -> 203 trap, so the
chapter ships ONE fence and files the other. `gaps.md` 047-1 through 047-5.

**PHASE 0 FOUND THREE PUBLISHED DOCUMENTS WRONG, ALL BY RUNNING THE STORE.**
**(1) `compose.yaml`'s ClickHouse has never been reachable from outside its container** and its
health check has been green since chapter 1.2 — the image restricts `default` to `::1` and
`127.0.0.1`, and `/ping` neither authenticates nor is network-restricted. **A check that cannot
fail for the reason you care about is not a check.**
**(2) SAD §6.2's DDL does not apply**: `TTL ts + INTERVAL 90 DAY` on a `DateTime64` is refused
with `BAD_TTL_EXPRESSION`; it needs `toDateTime(ts)` and has been published since the first
draft.
**(3) DR-10 AND FR-ANL-06 CANNOT BOTH HOLD.** `uniq` is exact to 60,000 distinct and **off by
0.51% at 70,000**; FR-ANL-06's reconciliation bound is **0.1%**, and DR-10 forbids reading raw
events instead. **The threshold is a cardinality, not a row count**, which is why testing at the
corpus's 5,000 users would never have found it. Filed for movement IV.

**PASS 3 WENT LOOKING FOR TWO DEFECTS AND FOUND NEITHER** — the first pass across two features
whose named targets came back clean. `SummingMergeTree` does handle `uniqState` (1,500 against
1,500 across three parts) and the event filter does survive the event-per-event load (1,210 mixed
events roll to the 100 creations). **What it found instead**: the rollup holds one row per insert
per `(environment_id, day)` until a background merge, so `SELECT messages` returned
`1000 1000 1000` where the truth was 3000. **The read contract is `sum()` with `GROUP BY`**, and
a query whose correctness depends on somebody having run `OPTIMIZE` is right in a demo and wrong
in production.

**PASS 9 ASKED WHICH DATABASE, AFTER EIGHT PASSES OF ASKING THE DATABASE.** Every number this
feature measured is consistent, reproducible and correct — **about the lane `relay`, which is not
what the chapter loads.** `corpus.mjs` builds `relay_corpus_<timestamp>` and **refuses
`CORPUS_DATABASE=relay`** in as many words. Its writes, in full: `messages` (seven columns),
`applications`, `environments`, an `update channels` and a `delete from outbox`. **Occurrences of
`message_edits`, `attachments`, `edited_at` and `deleted_at` in that file: zero, all four.**

**SO A STOCK CORPUS CANNOT SHOW THREE OF THE FOUR COLUMN FINDINGS.** Every row is `created`, so
the event-literal defect has nothing to show; `attachments` is never written, so `JSONLength`
against `length` is invisible; and `'corpus ' || s` is ASCII, where `length` and `lengthUTF8`
agree exactly. **Only `user_id` nullability survives.** And 4.1's 585.9 ms came from a
`relay_corpus%` database, so publishing it beside a measurement over the lane's 303,885 messages
compares two corpora rather than two stores — **the third time this feature needed a neighbour
held still**, after the rollup's window and the fence delta's locale.

**THE MECHANISM THAT FINDS THE MOST HAS A PREMISE OF ITS OWN.** *Ask the database a question with
a yes-or-no answer* was right eight times running and never asked **which database**. T024 named
the corpus from the first draft; no pass opened the script to see what it writes. **A premise
does not stop being a premise because it is the one your best instrument stands on** — and this
is the first CRITICAL in nine passes, found by reading a file that had been cited all along.

**THE REMEDY WAS CHEAP AND THE CHECK FOR THAT CAME FIRST.** `scripts/scale/` carries no titled
fence in either locale, so extending the seeder costs the chain nothing; and `corpus.mjs` already
runs the platform's migration runner against the database it creates, so `message_edits` exists
there and is merely empty — an insert, not a schema change.

**PASS 8 FOUND THAT PASS 7'S 3,935 NEW ROWS HAD NO DEFINED `text_length`, AND THE ANSWER IS IN
THE NEXT ROW.** `message_edits` holds `message_id`, `edited_at`, `prior_text` and nothing else —
**it records what a message used to say**, so the text an edit PRODUCED is only ever in the row
after it, or in the message itself. It chains: edit *k*'s result is edit *k+1*'s `prior_text`,
and the last edit's result is `messages.text`. Measured: **3,160 recoverable, 775 NULL.**

**AND THE 775 ARE THE SAME 775.** Messages edited once and then deleted. For the `created` event
that edit row is exactly what makes the original length recoverable; for the `edited` event the
deletion is what destroys the resulting one. **One row, two events, opposite outcomes** — which
is FR-ANL-02's emit-at-the-time rule as a figure rather than a sentence. **The same artefact is
evidence for the rule and against the workaround, depending on which event you ask about.**

**TWO ORDERING TRAPS, ONE ON EACH SIDE, AND THE SECOND WAS THE PROBE'S OWN.** The creation text
is the **earliest** edit's `prior_text` (`argMin` on `edited_at`) and **428 messages carry more
than one edit row**, so `any()` is wrong for up to 428 creations. And the probe that produced the
3,160/775 split tested `prior_text != ''` — right about this corpus, wrong about the rule, since
`prior_text` is `NOT NULL` and empty string is legal. **The counts survived only because an
independent Postgres computation agreed**; the expression did not.

**AND THE LOAD OPENS THREE TABLES, WHERE TWO ARTIFACTS STILL SAID TWO.** `message_edits` carries
**no tenant column**, so an edit event's `environment_id` arrives through two joins —
`message_edits → messages → channels`, checked at 3,935 rows over 505 environments. It is the
first row in this feature that does not get its tenant directly. `prior_text` arrives as a
non-nullable `String`; `edited_at` arrives as `DateTime64(6)` into a `(3)` column and the
microseconds go quietly.

**EVERY FINDING IN PASS 8 WAS DOWNSTREAM OF PASS 7'S FIX** — the fourth time in one feature.
Going from 3,201 edit rows to 3,935 did not just change a number: **it turned a by-product into a
population with its own recoverability story**, and nothing had been written for it.

**PASS 7 FOUND A COLUMN WHOSE NAME MATCHED THE CONCEPT AND WHOSE CONTENTS DID NOT.** T020a said
*write one row per EVENT, not one per message* and then took the edit timestamp from
`messages.edited_at` — which holds the **latest** edit, one per message. `message_edits` holds
one per edit: **3,935 against 3,201, 734 events lost across the 428 messages edited more than
once** (max 3). The total is **311,876**, not 311,142. **The rollup filters `event = 'created'`,
so the headline figure never noticed** — which is why this survived two passes that were staring
at that figure. Same shape as pass 2's finding one level down: **pass 2 caught the right number
of rows with the wrong label, this is the right label on the wrong count.**

**AND THE CONTRAST WITH THE TOMBSTONES IS THE PUBLISHABLE PART.** 3,282 lost `text_length`
values are genuinely gone — a deletion preserves no prior text. These 734 were never lost; they
sit in a table the loader already opens. **One is a limit of reconstructing from state, the
other was a reading error**, and filing them together would teach the wrong lesson about both.
Also resolved: **4,056 tombstones and one live message with no text** (`text IS NULL` 4,057,
`deleted_at IS NOT NULL` 4,056) — so NULL text does not mean deleted, and the prose cannot say
it does.

**AND THE FENCE DELTA HAS A NEIGHBOUR.** 110 is **APPLY 74 — 30 `(en)`, 30 `(vi)`, 14
elsewhere — and HEAD 36, all `(en)`.** Thirty live in the Vietnamese chain, which is under
active translation and is not a chapter's work, so a bare total moves for reasons the chapter did
not cause. **T004 and T059 record the breakdown now.** Third time in one feature that a delta
needed the thing beside it held still.

**FOUR PREMISES CAME BACK CLEAN AND TWO OF THEM COULD HAVE COST PHASE 6 A REBUILD.** The
`compose.yaml` chain is **identical in both locales** — 1.2, 3.19, 3.21, 3.22, 3.24 — and clean
in both, so a byte-identical Vietnamese mirror of 4.2's hunk applies in the vi chain too. And
**`fences/post-series.md` never touches `compose.yaml`** (it amends `package.json`, three
`.itest.ts` files and `eslint.config.mjs`), so there is no appendix hunk for a new chapter
amendment to unanchor.

**PASS 6 FOUND THE COMPARISONS HAD NO WINDOW, AND THE MATERIALISED VIEW COUNTS WHAT THE TTL IS
ABOUT TO DELETE.** The view fires on the insert, the TTL deletes on the same insert, **and the
view goes first**: 120,000 rows over 120 days leave `message_events` holding **90,000 over 90**
and `daily_usage` holding **120,000 over 120** — thirty days of figures for rows that never
persisted. Two tasks compared the tables unwindowed, so both would have printed a real number
about the TTL and handed it to FR-009 as `uniq`'s approximation error, **which is 0.51% at
70,000 distinct and small enough to be swallowed whole.** Inside the window they agree exactly:
90 days in common, 0 disagreements.

**AND THE THIRTY DAYS ARE THE DESIGN.** `daily_usage` carries no TTL, so it outlives the events
it was built from — DR-09 expires raw events and DR-10 says metering never reads them, and a
rollup that expired with its source would lose the billing history the pair exists to keep. **No
artifact said so**, which is why the only place a reader would have met it was as a thirty-day
discrepancy in a comparison. It is FR-003a now.

**SC-002 ALREADY CARRIED "FOR THE SAME NINETY DAYS" FROM PASS 3 — THE SPEC WAS AHEAD OF THE
TASKS THAT VERIFY IT.** That is the reverse of this project's usual direction and worth noticing:
**agreement between a criterion and its tasks is not the same as the tasks implementing it**, and
nothing checks that direction. One premise came back clean: `uniqState`/`uniqMerge` ignore NULL
exactly as `uniqExact` does, so pass 1's `Nullable(UUID)` fix survives into the rollup.

**PASS 5 FOUND THAT `analytics/` HAD NO ADDRESS, AND THE DEFAULT IS NOT THE ONE COMPOSE
PROVISIONS.** `CLICKHOUSE_DB=relay_analytics` **creates that database and does not make it the
session default** — `currentDatabase()` over HTTP is `default`, so SAD §6.2's unqualified
`CREATE TABLE` builds the whole analytical schema in **`default`**, with no error, while the
provisioned database sits empty beside it. **And the cleanup cannot catch it from either side**:
`DROP DATABASE relay_analytics` removes nothing and says nothing; `DROP DATABASE default`
succeeds, the server still answers `SELECT 1`, and every unqualified statement then fails
`Code: 81` with nothing to re-create it. Every statement names `relay_analytics` now and
`apply.mjs` **refuses one that does not** — the case is made impossible rather than handled.
**A missing address is harder to see than a wrong one: there is no sentence to disagree with**,
and five artifacts described what the statements do without one of them saying where they go.

**AND THE PASS FOUND NO WRONG FACT — IT FOUND A MISSING ONE.** Four premises checked in the same
pass all held: the vi placeholder's regex was generalised from `(3\.\d+)` to `(\d+\.\d+)`, the
migration tail is `0014`, all five gate scripts resolve, and the fence precedent is exactly four
`diff` hunks against chapter 1.2's one whole body. **Checking a premise that holds is not a
wasted pass**; it is the only way the clean ones become evidence.

**PASS 4 OPENED `contracts/schema.md` AND FOUND 046'S DEFECT VERBATIM.** The invocation line
read `RELAY_POSTGRES_PORT=15432 node scripts/scale/../../analytics/apply.mjs` — a **Postgres**
variable on a ClickHouse-only script, and a traversal for a path the quickstart writes plainly.
**046 carried the identical defect and it took six passes to find; this took four, and only
because the hiding place was known.** The contracts directory is the artifact nothing else reads.

**THE SAME PASS SETTLED THE SCRIPT'S SHAPE BY ASKING THE SERVER, AND WAS WRONG ABOUT THE
INTERESTING HALF.** The HTTP interface refuses a multi-statement body (`Code: 62 …
Multi-statements are not allowed`), so one statement per `.sql` file is **the interface's rule**,
not a tidiness convention — and a ledger keyed on filename means something only under it. The
transport had never been named in any artifact: it is Node's own `fetch`, which is what makes
the zero-dependency check a confirmation rather than a discovery.

**AND THE `--drop-all` HAZARD WAS THE OPPOSITE OF THE ONE EXPECTED.** The hypothesis was that a
materialised view's hidden `.inner_id.<uuid>` table outlives its view and leaks; it does not —
dropping the view by name leaves **0** of them. **The real hazard is the quiet direction**:
`DROP TABLE` on the source under a live view **succeeds with no error** and leaves an orphan that
still answers queries, with zeros. Inserting into the missing source errors loudly (`Code: 60`).
`--drop-all` is `DROP DATABASE` for that reason. **The direction that errors is the safe one.**

**AND THAT PROBE'S FIRST RUN REPORTED AN AUTHENTICATION ERROR THREE TIMES AS DATA** —
`clickhouse-server:25.3` refuses `default` without `CLICKHOUSE_SKIP_USER_SETUP=1`, and the probe
read `curl`'s output without checking it. `SELECT 1` -> `1` caught it. **Second broken probe this
feature, second caught by its own positive control, and neither was visible by reading.**

**AND PASS 2 ASKED PASS 1'S QUESTION OF THE COLUMNS PASS 1 SKIPPED.** `user_id` was not the
only nullable source column — `text` is NULL for **4,057 tombstones** and `attachments` for
**301,644 of 303,885 rows**, and both insert **0** into a non-nullable target. **A `text_length`
of 0 is a claim that a zero-length message was sent.** Pass 2 also found `event` written as the
literal `'created'` for 4,056 deleted and 3,201 edited messages, in a table whose rollup filters
on that label — **FR-ANL-05's messages-sent would have been over by 4,056.** SAD §6.2 means one
row per EVENT: the load writes **311,876 rows from 303,885 messages** (pass 2 said 311,142; see
pass 7), and **3,282 creations have no recoverable `text_length`** because a tombstone preserves no prior text. **That is FR-ANL-02's
emit-at-the-time rule arriving three chapters before the ingester: a store reconstructed from
current state cannot recover what the state no longer holds.** **THE FIX IS WHERE THE NEXT
DEFECT IS** — two features running.

**ANALYSIS PASS 1 FOUND THREE OF THE LOAD'S EIGHT COLUMN EXPRESSIONS WRONG, FROM ONE
`SELECT`.** `postgresql()` delivers jsonb as `Nullable(String)`, so `length(attachments)` gives
**151** for a two-attachment row; `length(text)` is **bytes** where FR-EMJ-02 counts code points;
and a NULL `user_id` inserted into SAD §6.2's non-nullable `UUID` becomes the **zero UUID**
silently — **one phantom active user per environment holding a deleted author's messages**. The
column is `Nullable(UUID)` now, which makes `uniqExact` ignore NULLs exactly as Postgres's
`count(DISTINCT user_id)` does. **R6 proved `postgresql()` could READ Postgres and stopped there:
reachability is not mapping**, and three artifacts then agreed with each other about a type none
of them had checked.

Also measured: the **TTL removes rows at INSERT, not at merge** — 120,000 rows over 120 days
became 90,000 immediately, silently. `EXPLAIN indexes=1` is the only honest instrument for
skipping (`Parts: 4/12 · Granules: 49/147`); `ProfileEvents['SelectedParts']` returned **0** for
the same query. And **ClickHouse reads Postgres directly** through `postgresql()`, so the
chapter adds **zero dependencies** — 1,000,000 raw rows become **89 rollup rows**.
**046 IS CLOSED at 76 of 76**; its record is `specs/046-chapter-4-1/` — `baseline.txt` first,
then `gaps.md` (eight entries, two closed), `traceability.md`, `tasks.md`.

**PART 4 IS 22 CHAPTERS, AND IT CONTRACTED TWICE.** `docs/12` split movement I in two;
**chapter 4.1 shipped with both halves at 2,132 prose words**, inside the bound, so movement I
is one chapter and every ordinal after the first moved down by one — 24 to 23. Then **4.2 built
all four items of the ledger chapter's brief** (runner, filename-and-checksum ledger, reporting
idempotence, a checksum refusal tested red), movement II had one subject left, and every ordinal
after 3 moved down again — 23 to 22, amended 2026-09-13. Milestones are at **9, 17 and 22**.
**§3's own heading still says 23** and this block said so until analysis pass 8; the specs' "of
22" was right. **§3's table keeps the ORIGINAL ordinals in column one on purpose** so older
references resolve — the movement column is the stable address, and reading the table's first
column as current is how a chapter number goes wrong. **Both corrections ran downward** —
Part 3 was planned as seven and shipped 26 —
and `docs/12` and `docs/07` were both amended before 047's spec was written rather than after
they disagreed with it. **4.2 is "ClickHouse from zero", not "the index that would fix it".**

**WHAT 4.1 MEASURED, AND IT FALSIFIED ITS OWN PLAN TWICE.** There was no metering query to slow
down — Part 3's counters are two pure functions on the send path. Then: an analytical query does
**not** tax the write path here (send p95 20.5 ms alone, **13.7 ms beside 102 of them**, four
control loops inside 1.3 ms), and the index that should fix the query **buys a gap inside the
run-to-run spread for +49% storage**. The join is 140 ms of a 698 ms plan and **the sort is 656**.
**You cannot index your way out of an analytical question when the cost is the aggregation** —
which is what 4.2's `ORDER BY (environment_id, ts)` and its rollup exist to answer.

    M1 585.9 ms over 1,000,000 rows   ·   lane's busiest env 0.9 ms over 1,018   ·   651x
    column 24.8 MB + index 62.0 MB = 86.8 MB permanent on a 178.6 MB table
    check:fences 110 -> 110, delta 0   ·   2,132 prose words   ·   8 gates green   ·   part4-ch1

**NINE ANALYSIS PASSES FOUND 27 THINGS AND, FROM PASS 4 ON, ONLY THEIR OWN PREDECESSORS'
REPAIRS.** The last finding from the tree was pass 3's 403. **Phase 2 then found six in ninety
minutes and five were invisible to reading**: an application holds two environments, not three
(FR-TEN-04, `unique (application_id, kind)`); the table is **`members`**, not `channel_members`;
`addMember` writes an outbox row; a small random formats as scientific notation and `interval`
will not parse it; a uniform offset lands 999,786 in a window asked for a million; and
**`channels.last_sequence` is a counter the write path maintains**, so a bulk insert that leaves
it at 0 makes every later send collide. **Reading cannot find what the schema refuses.**

**AND EVERY MEASUREMENT WAS WRONG BEFORE IT WAS RIGHT.** One query beside a 60 s loop is 1%
overlap; quiet-then-busy confounds the neighbour with the cache — the fix is a warm-up and a
**second quiet loop after busy**. The storage figure was wrong three times, each conflating a
different pair: +204 MB column plus dead tuples, +107 MB index plus un-vacuumed bloat, +4.3 MB
index **minus** the compaction the vacuum had just done. **A delta between two totals is not a
measurement of the thing that changed unless nothing else changed.** Two of three falsifications
also failed for the wrong reason — one on a JS error rather than the constraint, one on a count
the check does not read.

**THE TAG NAMESPACE IS CONSISTENT AGAIN.** Part 4 tags as **`part4-chN`**; `rework/` was a
rebuild artefact and does not carry forward. **The twenty-one stale `part3-chN` tags are deleted,
local and remote, in all three repositories** — they resolved to the replaced history, so
`README.md:8`'s promise was false for Part 3 and every SKIP AHEAD box with it. All 21 commits
remain reachable from `backup/pre-main-move-20260911`, checked after the deletion. **Three Part 1
tags are on neither `main` nor the backup** and are the only thing keeping those commits alive:
`gaps.md` 046-8.
<!-- SPECKIT END -->

    045 "part 3 rework"           24 chapters -> 26, eight movements, English prose only
                                  296 -> 110 fence-chain problems · 26 of 26 tags typecheck
    SC-007  403.76 s -> 232.05 s, 20 of 20 green, stdev 0.51, cv 0.22%
            inside the 202.91-248.00 s window it had been failing at +79%
    peak memory 5,180 MB mean · 913 tests and 0 leaked processes every run

**WHAT IT COST TO MAKE THE LANE FAST, AND WHERE THE TIME ACTUALLY WAS.** `fileParallelism:
false` had been serialising the api and gateway lanes since the outbox chapter, for a real
error — two suites issuing `CREATE TYPE` against one schema. **The reason died eight chapters
later** when `globalSetup` began migrating once before any file starts, and the setting
stayed, justified in a comment written in the very chapter that closed the race.

**EIGHT PLACES HELD THE LANES APART, THE ESTIMATE SAID THREE, AND THREE OF THE EIGHT ARE NOT
ASSERTIONS AT ALL** — a fixture planting rows no broker will accept, two forged frames a
required field three chapters later invalidated, and a count that could never have failed for
its own reason. Six were found one failure at a time over six runs; **the last two came from
asking the tree in one pass**, which is `check-lane-scope.py`. When a count keeps growing,
stop counting failures and go ask the repository.

**AND THE WORKER COUNT IS A BILL, NOT A SETTING.** Vitest defaults to about one worker per
core — here eighteen NestJS apps against one Postgres, which killed two battery attempts
before anything was measured. Every second of the api lane's saving is in **one worker to
two** (177 s -> 102 s for 87 MB); a ninth buys nothing and costs 1.2 GB. The gateway's knee is
**four**, not two. **The right worker count is per-lane and measured; a default is a number
about the machine, chosen by something that has never seen the workload.**

    044 "the revision watermark"  one column, `channels.revision_sequence`, raised inside the
                                  transaction that edits or deletes, never by a send
    reported on every `connection.ack` as `revisions: {channel_id: count}`, zeros included
    **the platform reports and never compares**
    mean 225.45 s, stdev 1.15 · SC-004 -2.33% · SC-005 edit +2.75% delete +2.99% · both MET

**044'S REVERSAL IS THE LESSON THAT OUTLIVED IT.** A draft had the client present its counts
on the upgrade URL. It was built, then removed. **A parameter the server parses and never acts
on is a contract it can never remove**; one it acts on hands the client a number the platform
decides with, which is how a fabricated count becomes a denial of service the client controls.
Removing it also deleted three edge cases rather than handling them — **a design in which a
case cannot arise beats a branch that handles it**, because the branch is the thing that rots.

## AN INSTRUMENT THAT REPORTS ZERO HAS TO PROVE IT LOOKED

Four lies in two features, each in a different way, and the rule is the same every time:
**a zero from an instrument is a claim about the corpus only if the instrument can be shown
to have read it.**

**`grep` ON THIS MACHINE IS ugrep 7.8.4, NOT GNU grep** (`/usr/bin/grep` is GNU 3.12; PATH
resolves elsewhere). A grouped alternation followed by two negated classes matches nothing
under it and matches under GNU — `(postgres|redis)://[^:/@]+:[^@/]+@` gives ugrep 0, GNU 1,
over a corpus holding the string twice. **Give every pattern a positive control**, and report
a pattern that fails its own example as BROKEN rather than as zero. One shipped gate uses the
construct (`check-srs-ids.sh:49`); it agrees under both engines.

**A PER-FILE COVERAGE THRESHOLD WHOSE KEY MATCHES NO FILE IS SILENT.** Demanding 101% of
`this-file-does-not-exist.ts` produces no error, no warning, nothing. **Run both halves of
that probe every time the ratchet is re-pinned.**

**A CHECKER HANDED A REF THAT DOES NOT RESOLVE COMPARED NOTHING AND EXITED 0** — twenty-six
times, printing `12 fences, 0 compared, 0 problem(s)`. **The zero that means "clean" and the
zero that means "never looked" printed the same line**, and four real problems sat behind it.
A checker must refuse its arguments rather than trust them, and refuse a run that compares
nothing (045-81).

**AND A TEST WRITTEN BY THE AUDIT THAT FINDS VACUOUS TESTS WAS VACUOUS.** It passed
identically with the counter moved outside the transaction, because the path refuses earlier
and the bump never runs. **Ask what would have to be false for this to fail, and then read the
code it calls**, not the test.

## COVERAGE IS NOT REPRODUCIBLE RUN TO RUN, AND THE RATCHET HAS TO ALLOW FOR IT

`session.ts` functions measured **87.80%** and **85.36%** on identical code twenty minutes
apart — about one function of forty — while every other pinned file was byte-identical across
both runs. A floor at the measured value goes red for no change to the code, and the fix is
then to lower it: **a ratchet that teaches people to lower ratchets.** Pin below the lower
observation by the observed swing and put both numbers in the config.

**AND A p50 IS NOT AUTOMATICALLY THE ROBUST STATISTIC.** Six runs a side: edit mean cv 12.9%,
edit p50 **17.3%**; delete mean 13.5%, p50 **20.6%**. **p50 was noisier on both paths** — a
median of 200 samples with a long tail wanders inside a crowded middle while the mean is
anchored by the whole sample. Resolving a 10% shift at that variance needs ~26 runs per side;
the criterion was kept with its resolution limit recorded rather than adjusted to fit.

## READ THE CLAUSES, NOT THE IDENTIFIERS — AND THEN RUN THE TASK

**FOUR DOCUMENTS AGREED ON TWO CLAUSES THAT DO NOT EXIST.** Spec, plan, tasks and quickstart all
said 044 would amend "SRS FR-016a and FR-016b" — chapter ids, absent from `docs/04-srs.md`.
Three analysis passes saw agreement because the artifacts agreed with EACH OTHER and not with
the tree. What found it was **opening the SRS to make the edit**, and reading the clauses gave
**three** to amend where the requirement named two. 045 hit the same shape from the other side:
a sweep passed `rework/part3-base` twenty-six times and there is no such tag.

## THE ONE THAT KEEPS EARNING ITS PLACE

**AN ARGUMENT THAT IS RIGHT ABOUT THE PRODUCER CAN INVERT ABOUT THE READER.** Making
`messageSchema.attachments` required is correct for a schema the platform BUILDS — required is
what makes the compiler name every construction site. The same sentence carried into
`outboxEventSchema`, which READS off a durable queue, answered every in-flight `message.created`
written by the previous binary with `message.term()`. **043 was told to do it again by a task
citing a line number, and did not.**

**Required is a claim about what you write. A reader of anything durable cannot require a field
its writer did not have.** 045 paid the test-side of this: adding a required `revisions` to the
ack invalidated two forged sample frames three chapters away, and the tests asserting the wrong
refusal stayed green.

## MEASURE THE CARRIED LEDGER; DO NOT COPY IT — AND THAT GOES FOR COMMITS

Four of 043's twenty-three carried items were wrong when re-measured, and **three closed with
nobody working on them**. 044 re-measured all twenty-eight and closed none DURING the feature,
said plainly rather than implied by a short list; two were then closed afterwards as work of
their own. **A lookalike nearly closed one** — a test file asserting the right shape about the
wrong pair of lists. **Read the assertion, not the filename.** And that item's own premise was
wrong: there was no second list, and the real defect was sharper than the one filed, because
the linter checked one direction only.

**045 CARRIED COMMITS RATHER THAN ITEMS, AND THE FAILURE MODE IS THE SAME ONE LEVEL DOWN.**
Twenty-four commits from two closed features. Four of the first rows were decided wrong, in
opposite directions, for one reason: **a commit was classified by one of the things it does.**
One did two things and was skipped for the half already present — its subject named both
halves. One was accepted as complete because its file count was right.

**THE `test(` / `fix(` PAIRING IS THE SPECIFIC TRAP, AND IT CAUGHT THIS PROJECT THREE TIMES IN
ONE CARRY.** A tombstone test, a race test and a teardown assertion were each taken without the
`fix(` commit they were written to prove, and every time the symptom was a suite that failed
some or all of the time and read as flaky. **A red test is the visible half, so it gets carried
first and alone.** Before taking a `test(` commit, find the fix it exists to demonstrate.

**AND FOUR OF SIX SKIPS WERE RIGHT FOR A BETTER REASON THAN EXPECTED** — the work was already
in the chain, arrived at independently, and in three cases in a STRONGER form: the lane reset
plants the row it asserts on, the port map is deleted rather than extended, the exemption list
is read from the rule rather than restated. **Cherry-picking blindly would have downgraded the
chain in every one of those three.**

**A TASK ID IN A TEST TITLE OUTLIVES THE TASK, AND A TITLE IS THE PART READ DETACHED FROM ITS
FILE** — a CI summary has no repository to grep. Seven are gone; two could not be removed alone,
one having a comment fifty lines away pointing AT the title by its id, one printing to stdout.
Ids anywhere in test files still number **330 across 46 files**, filed rather than swept.

## TWO CLOSED STORIES, KEPT FOR THEIR RULES

**A HAND-MAINTAINED TABLE CANNOT BE CHECKED.** Nine api ports came from hand-allocated bands
across eight files, and **two bands contained a service the lane itself runs** — 5432 inside
`membership`'s range, 4222 inside `limits`'. The failure is silent both ways: the child cannot
bind, and the health check gets its answer from whatever *does* hold the port. All nine now use
`PORT=0` with the port read from the child's own log line, and the map is **deleted rather than
corrected**.

**A TEST OF A SCRIPT MUST ASSERT WHAT THE SCRIPT DID, NOT WHAT THE TABLE HOLDS.** `reset-lane`
counted rows "due now", which a run that just finished violates legitimately, and counted
staleness against a `now()` re-evaluated ~115 ms after the script's own. **Pin one instant
before the script runs** — the same pin 045 needed to keep that suite's whole-table count honest
under a lane that no longer serialises.

## OTHER THINGS 043 PAID FOR

**A RED PROBE WRITES TO THE LANE.** Reverting the avatar rule to check the tests could see its
absence left two `javascript:alert(1)` rows stored, accepted with a 200 — and the next
measurement read them as pre-existing data contradicting the plan. **Clean up a probe before
anything is counted.**

**AN ASSERTION SCOPED WIDER THAN THE THING IT TESTS FAILS FOR SOMEBODY ELSE'S REASON.** 043
found two — a whole-table `outbox` count and a wall-clock minute bucket — and **the first fix
was worse than the fault**, sleeping to the next boundary and blowing the test's timeout. 045
found six more and made the class checkable; see the lane section below.

**WHEN MEASUREMENT FALSIFIES A CLAUSE, AMEND IT.** Done three times: FR-RTM-09 and FR-RTM-10 in
the SRS (revision 1.8), and **043's own FR-016**, which would have refused 838 stored
subscriptions to a declared, published, unbuilt event type. The governance clause requires
amendment rather than silent divergence, and that applies to a feature's own specification.

**A PLAN COUNTS THE FIX AND NOT THE VERIFICATION.** 17 files estimated, 58 changed, and every
unplanned one came from RUNNING something rather than reading it. 045 said three and found
eight, the same way. **The error is in one direction, every time.**

## THE LANE, AND WHAT IT STILL CANNOT TELL YOU

**The test lane is the instrument closest to hand and the least representative thing here.**
Ordering by `max(messages.created_at)` costs 0.87 ms on the lane and 159 ms at a million
rows — 145x from an indexed column — and the lane's largest membership set is FIVE channels,
so it cannot see any of that.

**IT NO LONGER COSTS PER SUITE.** The api lane runs two files at a time and the gateway four,
both bounds measured rather than inherited (045-79); `vitest.coverage.config.mts` and the e2e
lane still serialise. That changes what a duration means: a suite's own time is now overlapped
with a neighbour's, so **a slower suite does not always show up in the total**, and the lane is
correspondingly less useful as a per-suite stopwatch than it was.

**AND IT MAKES EVERY WHOLE-TABLE ASSERTION A NEIGHBOUR'S PROBLEM.** Eight of them were found
this way (045-74). `check-lane-scope.py` asks the question directly — which queries read a
shared table without a predicate naming this test's own rows — and reports zero. **Run it after
adding an integration test**, because the alternative is finding out once, in the fifteenth run
of a battery.

**BATTERIES ARE COMPARABLE NOW, AND THE PAIRS SAY SO.** 043 and 044 came in 0.10 s apart on a
240 s budget. 045 measured its own lane either side of one change, twenty runs a side:
**403.76 s -> 232.05 s, stdev 0.50 and 0.51, cv 0.22% both.** The old rule was "no two batteries
are comparable"; the rule now is **"two batteries are comparable once the lane stops colliding
with itself, and you find out by measuring, not by assuming either way."** 3.23's 228.80 s and
3.24's 233.08 s are still not comparable to anything.

**A FLAKE DOES NOT SHOW UP IN THE DISTRIBUTION.** cv 0.22% across twenty runs, and one of them
red — a frame that had not arrived, not a slow run. **Twenty runs is a sample of the lane's
timing and a very thin sample of its failure modes**; three green runs is weaker still, and
045 offered exactly that as evidence before the fourth run falsified it.

**Postgres rows still accumulate and `reset-lane.mjs` does not touch them by design** — it
purges lane debris, not data. Measured at 045's close-out: **31,215 environments, 481,251
outbox rows (5,253 pending), 300,719 messages, 45,567 channels.** Record the row counts beside
any close-out timing, because they are part of the instrument.

**A FILE AT 100% BRANCHES IS NOT A FILE WHOSE EVERY ARM HAS RUN.** v8 records a `binary-expr`
arm as covered when the operand was EVALUATED, not when it went both ways. Constitution VI's
100%-branch clause is stated in that number.

**AN ARGUMENT COSTS 545 WORDS IF IT IS MADE OF PROSE AND ABOUT 280 IF IT IS MADE OF
ARTIFACTS.** Say which kind each argument is when the estimate is written.

## THE THREE MECHANISMS THAT FIND THINGS, RANKED BY YIELD

1. **Ask the repository — or the broker, or the database — a question with a yes-or-no
   answer.** `curl localhost:8222/jsz?consumers=1` answered in one command what two hypotheses
   could not. 043's decisive numbers were all queries. **045's were too, and one of them ended a
   hunt**: `3,200 pending outbox rows in 16 subjects are unroutable, every one of them a test
   fixture's bait, and nothing else in the backlog is` — which explained two failures of
   different shapes at once, `NatsError: 503` and `expected 41 to be 700`.
2. **Read the clauses, not the identifiers.**
3. **Check a task's premise before executing it**, and run the command a task tells someone to
   run. 043 found four tasks whose premise was wrong, including one that would have caused a
   defect.

**AND WHEN A MECHANISM IS PROPOSED, FORCE IT — BUT FORCE IT UNDER THE CONDITION IT FAILED IN.**
Eight gateway-suite runs at 35 s found two flakes in five minutes that a 78-minute battery found
once. **The same trick then failed**: a flake from a twenty-run battery would not reproduce in
eight runs of that lane alone, because it needs the api lane loading the machine beside it.
Amplifying the wrong variable proves nothing; **8 of 8 green was not evidence the flake was
gone, and reading it that way would have closed the item.** Raising the worker count until the
failure returned is what gave a probe to fix against.

**AND A SWEEP BEATS A BATTERY FOR FINDING A CLASS.** Six instances of one fault were found one
failure at a time across six runs; the last two came from one pass of an instrument that asked
the tree directly. **When the count of a class keeps growing, stop counting failures.**

## A CHECKER'S BLIND SPOT IS WORSE THAN ITS ABSENCE

Write the class list explicitly and make the checker **fail on an unknown member**. Then test it
red, three ways — `check-revision-order.mjs` fails on a descent, an unparseable version and a
renamed heading; `check-error-codes.mjs` compares `CLOSE_CODES` in both directions;
`check-lane-scope.py` carries ten controls including two that pin its own earlier mistakes.

- **`check:errors` reads the BUILT `dist`.** Build before believing it — and before RUNNING a
  tag, because the harness spawns `dist` too.
- **A checker reports the FIRST failure per file.**
- **No checker reads prose**, and a `mermaid` block is prose.
- **A checker that cannot resolve its arguments must refuse**, not compare nothing and exit 0.
- **AN UNTITLED FENCE IS NEVER COMPARED TO ANYTHING.** `check-fence-chain.mjs:77` collects a
  fence only when it matches `title="…"`. **146 of 904 — 16% — are outside every gate**, one
  step further out than the excerpt-only class, which is at least skipped BY a title somebody
  wrote. Nobody decided this one; `gaps.md` 043-1 opens it and 045 did not close it.
- **FOURTEEN GATES, NOT ELEVEN**, and capture every exit code OUTSIDE a pipeline. `fail=1`
  inside `for … | sort` runs in a subshell and dies with it. **043 reproduced that mistake three
  times**, once in a task whose own text warns about it.
- **AND AN INSTRUMENT'S FALSE NEGATIVE IS WORSE THAN ITS FALSE POSITIVE.** `check-lane-scope`
  went through two wrong designs: one reported three correctly-scoped queries, the next MISSED a
  real one because the surrounding JavaScript happened to contain a scope word. **The first
  wastes an afternoon; the second reports a clean sweep over a file you already know is dirty.**

## TESTS THAT PASS WHILE PROVING NOTHING

Ask, of every test on a failure path: **what would have to be false for this to fail?**

- **A health check that has never passed.** `membership` and `presence` probed `/health`; this
  api serves `/healthz`. Both loops ran 100 failed probes and returned the URL anyway — a flat
  ten-second sleep reporting success. **Neither fault could surface while the other was there
  to absorb it.**
- **`webhooks.itest.ts` asserted status and message text** and passed while the body said
  `internal_error`. Only the code could have caught it, which is why it survived from 3.5.
- **A repository test proves a check exists; only a route test proves it fires.**
- **A conditional assertion is an assertion that may not run.**
- **Two 204s prove nothing.** Idempotence is about what the second call DID.
- **A title that overclaims is the same defect.** 043's audit caught two of its own: one
  claimed a derivation nothing in the body can observe, one said "every refusal" while leaving
  one asserted by status alone.
- **An assertion that can only fail for somebody else's reason.** Signup's invariant 7 counted
  every `organisations` row before and after an unauthenticated request that is refused before it
  reaches a handler — **no code path existed that could move the number**, and it moved anyway.
  Replaced by the structural claim its own comment already made and nothing was checking:
  `provisionOrganisation` has exactly one non-test importer.
- **A flat sleep before an assertion is a bet that the lane is idle.** `await settle(700)`, then
  count the frames. **Arrival is a condition and absence is not**: poll to a deadline for what
  must arrive, and keep a quiet window only for what must not — taken AFTER the arrival wait,
  never instead of it. One red in twenty full runs, in two different tests of one file.
- **And a fixture is a test too.** Drain bait planted on a subject no stream accepts, carrying no
  envelope id, broke two invariants of a suite that never mentions it. **A fixture imitating a
  thing must be usable everywhere the thing is**, or it is a landmine rather than bait.

## THE FENCE CHAIN

1. **`-U6` IS A DEFAULT, NOT A RULE.** Regenerate wider when the pre-image matches twice.
   `resume.itest.ts` carries eight session stubs byte-identical far past six lines; `-U10` made
   all nine hunks unique and **`-U8` was worse — `[1, 1, 3]`** — because widening context merges
   adjacent hunks and a merged hunk spans more repetition than either half did. **Verify the
   hunks apply clean before pasting, not after.**
1a. **GENERATE HUNKS FROM THE CHECKER'S OWN REPLAY.** Copy `check-fence-chain.mjs`, truncate it
   at the HEAD comparison, make it dump its 240-file end state, diff that against the working
   tree, delete the copy. A generator that replays differently from the checker produces hunks
   the checker rejects for reasons neither of them explains.
2. **The predecessor is a commit, not a tag.**
3. **A `diff` hunk says A way to get from one file to another, not THE way.**
4. **An appendix hunk anchored on a file's last line forbids any chapter from appending**,
   and a diff body inside a ```ts fence is read as a whole file — the appendix takes `diff`.
5. **An excerpt-only file is never verified — THIRTEEN of them**, re-measured at 044's
   close-out. A naive count says fifteen: two titles carry a prose suffix and both base files
   are chained elsewhere, so **normalise the title before comparing.** This count has been
   wrong four times out of five and every error was in parsing the title.
   `services/gateway/src/session.itest.ts` is one of the thirteen and now holds the **only**
   end-to-end proof that 044's column, api and ack are connected.
6. **Run `check:fences` after ANY source edit**, not only the ratchet.

**AND MDX IS NOT MARKDOWN.** An indented `400  {"code": …}` block is literal text in markdown
and a JSX expression in MDX.

**A FOUNDATION FENCE IS NOT A THING TO REGENERATE.** Chapter 1 fences several files as WHOLE
BODIES, and every later diff in every later chapter is anchored on those bytes. Bringing one up
to date satisfies the per-chapter checker and takes the cumulative chain from **111 problems to
203**, unanchoring ninety-two downstream hunks. Where the two checkers disagree there, the chain
is the one carrying the readers — and the change belongs in the appendix, which applies after
every chapter and is where anything no chapter can own goes (045-81).

**AND REBUILD BEFORE RUNNING A TAG, NOT ONLY BEFORE TYPECHECKING ONE.** The stale-`dist` trap has
a runtime form: the harness SPAWNS `services/api/dist`, so a `dist` built at the tip against an
older tag's database gives 38 identical `42703 column ... does not exist` errors that read like a
broken chain. It cost a wrong published conclusion before it was found (045-77).

## THE CYCLE THIS PROJECT USES

`/speckit-specify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` (repeatedly) →
`/speckit-implement` (once per phase). 3.24 ran twenty-one analyze passes, 3.23 eleven, 043
fourteen, 044 three, 045 five. **Do not stop on falling yield** — and note two things no number
of passes finds: a defect in code no lane runs, and **artifacts that agree with each other and
not with the tree**. **The pass that RUNS the premise finds the most.**

**Commit each phase.** `git checkout` on a file with uncommitted work destroyed it twice.
**Pin the lane environment where the tasks can see it** (`baseline.txt`), and bring the stack up
with `RELAY_POSTGRES_PORT=15432` — this machine's own Postgres holds 5432.

**NOTHING ELSE RUNS ON THE MACHINE DURING A TIMING BATTERY, AND NOTHING TOUCHES THE REPOSITORY
EITHER** — a few hundred `git show` calls in a sibling worktree cost one run 768 seconds while
its per-suite times stayed identical, which is how you tell interference from a defect. Two 045
batteries were also killed by the host's own memory supervisor at ~20 s in, with 12 GB free;
detaching the driver is what let the twenty runs finish.

**THE READER PROTOCOL IS RETIRED.** Chapters 3.14 onward each named this gap, 045 was the
fourteenth record to name it and not close it, and 046 is where it was **decided rather than
deferred again**. Fifteen intentions and no runs is not a gap, it is a habit.

**THE ARGUMENT IS ABOUT COST.** A chapter's tag is cut on `relay-platform` and its prose lives
in `relay-tutorial`, so a prose correction after publication moves no platform commit and
invalidates no tag. A chapter contributing no TITLED fences changes `check:fences` by nothing —
4.1 contributes 0 and its close-out delta was 0. **Feedback on the writing comes from readers
and is applied then**, and a gate earns its cost only when the thing it guards is expensive to
change. Prose here is cheap; the fence chain is not, and that is where the gates are.

**WHAT IS GIVEN UP, AND IT IS REAL.** 044 had the sharpest evidence for what the exercise
finds: reading the published text with the spec and source closed found a hole — FR-008's
client half was missing — **because that exercise finds information that is ABSENT**. Nothing
now finds that. 046 accepted the risk with its eyes open: **its argument changed twice during
measurement and the prose was rewritten each time by the person holding the numbers.**
`specs/036-chapter-3-18/reader-protocol.md` stays in the tree as a procedure anyone can pick
up; it is no longer a criterion any chapter has to satisfy.

Every check in these three repositories compares bytes. Twelve Python instruments and five
`check:*` scripts — and not one can say whether a paragraph is understandable to somebody who
does not already know the answer. Each says so in its own last line:

    check-refs: ids only — this says nothing about whether the prose around them is true
    check-chapter: bytes only — it cannot say whether the PROSE describes the diff
    check-lane-scope: SQL text only — a scope applied in JavaScript is invisible to it

**An instrument that is easy to run tells you what it measures, not what you wanted to know.**
