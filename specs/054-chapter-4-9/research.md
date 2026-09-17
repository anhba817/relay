# Research — feature 054, chapter 4.9, "Milestone: the meter agrees"

Every item was measured against the running lane on 2026-09-17 unless it says otherwise.
Where an item reads a file rather than a store, it says so and quotes the line.

---

## R1 — THE GATE CANNOT FAIL FOR ITS OWN REASON, AND HAS NOT SINCE CHAPTER 4.4

**Measured.** `pnpm test:integration` is
`turbo run test:integration --concurrency=1 --filter=!@relay/outsider`. It plans 18 tasks,
attempts **10**, and prints `Tasks: 8 successful, 10 total`. Turbo stops scheduling at the first
failure, so every lane ordered after the api has not executed under that command since chapter
4.4 (`gaps.md` 051-3, re-measured — the figures were 7 of 9 at 4.7).

**AND THE SUMMARY COUNTS TASKS, WHICH FOUR CHAPTERS HAVE READ AS LANES.** From `--dry=json`:

    18 planned = 9 build + 9 test:integration
    three of the nine test tasks are packages with NO `test:integration` script —
      @relay/config, @relay/protocol, @relay/service-kit — and complete as successful no-ops
    six packages hold real suites: api, dispatcher, e2e, gateway, ingester, test-harness

So `8 successful, 10 total` includes builds and no-ops, and **the number of integration suites
reached before the stop is not derivable from that line.** 051-3 filed it as *"reports one
failure where several lanes fail"*, 4.7 sharpened it to *"plans 18, attempts 9"*, 4.8 re-measured
it to 10 — every reading treated tasks as lanes. The count this milestone needs comes from the
lanes' own vitest summaries or from the `.itest.ts` files in the tree.

**AND THE SEALED SUITE IS EXCLUDED BY NAME, NOT BY THE EARLY STOP.** `--filter=!@relay/outsider`
is in the command. `gaps.md` 053-3 — written at chapter 4.8's close and cited by this feature —
attributes its absence to turbo stopping early. It is one flag, added deliberately for a suite
that needs a running platform no lane starts.

**AND THE PRECEDENT IS ABOUT THE SHAPE, NOT THE MECHANISM — which the first draft of this item
got wrong and put in four artifacts.** `--filter` selects **packages**. `@relay/outsider` is its
own package, which is why one flag excludes it. The five failing suites are
`services/api/src/request-log/request-log.itest.ts` — **inside `@relay/api`, the same package as
`reconcile.itest.ts`**, the suite the gate exists to reach. No `--filter` expression can keep one
and drop the other.

Separating them needs a mechanism `--filter` does not have: a vitest `exclude` in
`services/api/vitest.integration.config.mts`, a second config, or moving the file. Each changes
what `pnpm --filter @relay/api test:integration` means for everyone who runs it, so the option is
materially more expensive than *"one flag"* — which pushes the decision toward giving the
environment an ingester and is why T030a's ADR has to weigh the real ones.

The api lane it runs first is red, with six failures and **none of them the reconciler's**:

    request-log.itest.ts  5   polls for a row only an ingester can write; `compose.yaml`
                              ships none. 050-8, unchanged since chapter 4.4
    limits.itest.ts       1   "the lane must configure a platform credential: expected
                              undefined to be truthy" — a missing environment variable

**Decision**: the milestone's CI half is not "write a test". The test exists (chapter 4.7's
planted-drift describe, 33 assertions). The half that does not exist is a gate whose colour
means something, and reaching it means dealing with six failures that belong to other chapters.

**Alternatives considered**: raising `--concurrency`, which makes the lanes run in parallel
against one Postgres and is the thing feature 045 measured down to two workers for the api and
four for the gateway; and `--continue`, which runs every task and reports all failures. The
second is the cheaper change and does not alter what the lanes do. **Both flags exist in this
version** — turbo 2.10.8, checked — and **both already live in `package.json` rather than
`turbo.json`**, which holds only `dependsOn` and `env` for this task. There is no choice of file
to make. `turbo.json` also sets `"cache": false` here, so chapter 4.5's turbo-cache trap does not
reach this lane.

---

## R1a — THE GATE'S DEFINITION IS PUBLISHED IN THE APPENDIX, WHICH APPLIES AFTER EVERY CHAPTER

**Read in `relay-tutorial/fences/post-series.md`.** It carries `diff` fences for eighteen files,
two of which are this feature's: **`package.json`** and **`turbo.json`**. And the `package.json`
hunk's `-`/`+` pair **is the `test:integration` line**:

    @@ -9,23 +9,27 @@
    -    "test:integration": "turbo run test:integration --concurrency=1",
    +    "test:integration": "turbo run test:integration --concurrency=1 --filter=!@relay/outsider",
    +    "test:outsider": "turbo run test:integration --filter=@relay/outsider",
    +    "coverage": "vitest run --config vitest.coverage.config.mts --coverage",

**So a chapter hunk for `package.json` would be silently reverted.** The appendix applies last,
so a 4.9 hunk would anchor on a pre-appendix state where that line still reads
`--concurrency=1`, and the appendix would then re-apply its own version on top. Chapter 4.8 hit
the adjacent case and it at least *reported* — `hunk pre-image matched 0 times` — because its
edit and the appendix's did not overlap. **An overlapping edit does not report; it disappears.**

**AND THE "INVISIBLE EDIT" READING IS ABOUT THE WRONG HALF OF THE CHECKER.** `package.json` is
already a HEAD problem at line 15, which makes an edit invisible to the **HEAD** comparison. The
**APPLY** side is separate and is where an unanchored or overwritten hunk shows up. A file can be
free on one half and expensive on the other, and this one is.

**Decision**: any change to `test:integration` lands in the appendix's hunk, not in a chapter's.
The appendix is where anything no chapter can own goes (045-81), and the gate's definition is
exactly that — it has been edited by the series as a whole rather than by a chapter.

**AND THE SAME HUNK ANSWERS A CARRIED ITEM.** `"test:outsider": "turbo run test:integration
--filter=@relay/outsider"` is in `package.json:16` and in the tree — checked by running
`node -e` against it. **`gaps.md` 053-3 says "no local command runs the sealed suite."** It was
written at chapter 4.8's close after running that suite by hand in six commands, without looking
for a script. The item's other half still holds: `pnpm test:integration` does not reach it, for
the deliberate reason R1 now records.

---

## R1b — THE WORKFLOW IS RED ON EVERY PUSH, SO "THE BUILD FAILS" IS NOT A SIGNAL TO CHANGE

**Read in the tree, three files.**

    check-fence-chain.mjs   process.exit(1) whenever problems.length > 0
    check-fence-chain.sh    exits 0 only when relay-platform is absent
    ci.yml                  `pnpm check:fences` is the tutorial job's LAST step,
                            with no `continue-on-error`

The standing count is **110**, and every chapter since 4.1 has closed at *"110 → 110, delta 0"*.
So the tutorial job has failed on every CI run since feature 045 established that baseline, and
**the workflow has no green state to lose.**

**Nothing is stranded behind it** — it is the last step, which is why chapter 4.8's audit of the
*platform* job did not surface this. The damage is not a skipped step. It is that a planted drift
turning this feature's gate red is measurable at the **step** and changes nothing observable at
the **workflow**.

**AND IT IS THIS MILESTONE'S OWN DEFECT ONE LEVEL UP.** The api lane's six reds mask the
reconciler inside one job; `check:fences` masks every job's colour inside the workflow. The
chapter is being written about the first while standing in the second.

**It also makes `docs/07` §6's defense 1 hollow twice over** (R7b): *"If chapter 2.3's checkpoint
fails, the build fails"* — the mechanism does not exist, and the build already fails.

**What this does NOT say**: that `check:fences` is broken. 110 is the honest count of an
inherited chain state, 11 of which are fences whose titles name no file and can never be repaired
by editing the platform (`gaps.md` 050-4). The checker does exactly what it was built to do.

**Decision**: FR-002 and SC-001 are scoped to the **step** — a planted drift turns
`pnpm test:integration` red, shown by running it — and the feature records that the workflow's
colour is already uninformative rather than implying it is a signal. Whether to change the
arrangement is a decision with a reversal condition, and it belongs beside T030a's.

**Alternatives considered**, none of them this feature's to choose alone: a recorded baseline the
checker compares against, so a delta of 0 exits 0 and a regression exits 1 — which is what every
chapter already reports by hand; `continue-on-error: true` with the count published, which keeps
the number and loses the enforcement; and moving it to its own job, which makes the other jobs'
colours legible again and leaves this one permanently red on purpose.

---

## R1c — "THE FIVE INTEGRATION LANES" IS SEVEN PACKAGES AND FIFTY-FIVE FILES

**Measured**, by finding every `.itest.ts` under each package and checking which packages carry
a `test:integration` script:

    api          33 suites        gateway  12        e2e  4
    ingester      2               test-harness 2     dispatcher 1
    outsider      1  — excluded from the gate by `--filter=!@relay/outsider`
                                  total   55 files across 7 packages, 6 inside the gate

The first draft of T002 said *"the five integration lanes"* and T037 said *"the four lanes"*.
**Neither is any of those numbers**, and T002 is the task T064 runs *"every gate"* against — so a
list short by one closes the feature having verified one fewer lane than ran. It is the shape
`gaps.md` 053 recorded as *"eleven gates, not eleven"*, reproduced in the task whose own text
cites that precedent.

**AND THE FIRST ATTEMPT TO MEASURE IT REPRODUCED 049's GLOB TRAP, INVERTED.** The sweep used
`$d/src/*.itest.ts` and returned six packages **with the api absent** — 33 suites, the largest in
the repository — because the api keeps its suites in `src/request-log/`, `src/metering/` and
`src/isolation/` rather than directly in `src/`. Feature 049 found `services/*/src/**/*.ts`
missing files that sit directly in a `src/`; this is the same fault from the other side.

**The tell was the shape of the output, not the count**: the package with the most suites was
missing from the result, which is what a glob failure looks like and not what a corpus looks
like. T044 already instructs a positive control for exactly this, and it was not applied to this
sweep until the output looked wrong.

**Decision**: T002 derives the list with a command and records the command beside the output.
A count in a task is a hand-maintained table, and this project deletes those rather than
correcting them.

---

## R1d — TWO OF THIS FEATURE'S OWN MEASUREMENTS WERE WRONG, AND THE TELL WAS A PRIOR RATHER THAN A CONTROL

Recorded as a working rule rather than as a finding about the artifacts.

**Analysis pass 14**, counting integration suites per package, used `$d/src/*.itest.ts` and
returned six packages **with the api absent** — 33 suites, the largest in the repository —
because its suites live in `src/request-log/` and `src/metering/`. Feature 049's glob trap,
inverted.

**Analysis pass 15**, splitting the fence chain by locale, used `awk -F/ '$1 ~ /\(en\)/'` and
returned **0 en, 0 vi, 74 elsewhere**. The paths begin `app/(en)/…`, so field 1 is `app`.

**Neither was caught by a control.** Both were caught because the number was implausible against
something already on record — the api being the biggest lane, and 4.7's 30/30/14. **That is luck
wearing method's clothes**, and it does not work for a measurement with no prior, which is most of
what this feature takes.

**Decision**: every measurement task in this feature states the instrument beside the number, and
where a prior exists it is quoted so the comparison is visible. T044 already requires a positive
control for the checked-in sweeps; the same rule applies to a one-line command typed during a
pass. *A zero from an instrument is a claim about the corpus only if the instrument can be shown
to have read it* — and a 74 is too.

---

## R2 — THE SIX REDS, BY CAUSE, AND ONLY ONE IS A PRODUCT DEFECT

**Measured**, by running each suite alone.

| suite | count | cause | who owns it |
|---|---|---|---|
| `request-log.itest.ts` | 5 | needs a draining ingester; `compose.yaml` has none | `gaps.md` 050-8, opened at 4.5 |
| `limits.itest.ts` | 1 | `RELAY_PLATFORM_CREDENTIAL`-class env var absent from the lane | lane configuration, red since before Part 4 |

Neither is a defect in the code under test. **Both are environment**, which is why they have
survived four chapters: a red that is somebody's configuration gets read as somebody's problem.

**Decision**: the milestone resolves both or records each with the reason and the owner. FR-004
says "given a running fix" because an ingester in `compose.yaml` is a service definition and a
platform credential is a variable — neither is research.

---

## R3 — THE CORPUS IS CHEAP, AND IT ALREADY REACHES THE VOLUME THE BOUND NEEDS

**Read in `specs/047-chapter-4-2/baseline.txt:285`, which measured it:**

    relay_corpus_20260913102333    built in 92.4 s
    messages 1,600,000 · edits 33,549 · deletions 21,072 · channels 2,400
    load-analytics.mjs             1,654,621 events in 1.2 s

`corpus.mjs` defaults to `CORPUS_MESSAGES=1000000`, `CORPUS_ENVIRONMENTS=3`,
`CORPUS_DAYS=120`. At 1.6M over 3 environments and 120 days that is **≈133,000 messages per
environment per month** — already above the 100,000 the bound needs (R9).

And the load is not a bottleneck: ClickHouse reads Postgres itself through `postgresql()`, so
1.65M events move in 1.2 s and nothing streams through Node.

**AND THE SCRIPT REFUSES TWO OF THE THREE KNOBS THIS ITEM FIRST REACHED FOR.** Read in the
file, after the first draft of this research had already published a command using both:

    corpus.mjs:88   CORPUS_DAYS must EXCEED the query window — 90
    corpus.mjs:82   CORPUS_ENVIRONMENTS must be at least 2

So `CORPUS_ENVIRONMENTS=1 CORPUS_DAYS=31` — which this item, the plan and the quickstart all
carried — **fails on the script's first validation**. That is chapter 4.6's recorded defect
reproduced three chapters later: *"`corpus.mjs` REFUSES `CORPUS_DAYS=60` … analysis pass 5 wrote
60 into the quickstart and nobody ran it."* The constraint is eight lines from the line this
item quotes.

**AND `CORPUS_MESSAGES` IS NOT A TOTAL, WHICH THE FIRST REPAIR OF THIS ITEM ALSO GOT WRONG.**
Analysis pass 1 replaced the refused knobs with `CORPUS_MESSAGES=700000` and the sentence *"700,000
over 2 environments and 91 days is roughly 115,000 per environment-month"*. `planFor` says
otherwise, forty lines above the validations pass 1 had just read:

    subjectMessages = ceil(messages × days / 90)        the SUBJECT's total
    perNeighbour    = floor(subjectMessages × 0.1)      NEIGHBOUR_SHARE

So `CORPUS_MESSAGES` is `messages_in_window` **for the subject environment**, the neighbours get
a tenth each, and the volume is not split evenly at all. The 700,000 figure cleared the bar for
a reason the artifacts did not state — the subject would have held ≈233,000 a month, twice what
was claimed and twice what is needed.

**The rule, stated so it can be used for a different corpus**: the subject gets
`messages_in_window / 90` rows a day, so **a month is a third of `CORPUS_MESSAGES`**. For
≥100,000 in one tenant-month, `CORPUS_MESSAGES=350000` gives ≈116,700 and writes about 389,000
rows in total.

**AND THE NEIGHBOUR IS A FEATURE.** `NEIGHBOUR_SHARE`'s own comment — *"enough that the tenant
predicate excludes something; not enough to triple the seed"* — is exactly what a reconciliation
measurement wants beside it: a second tenant whose rows must not appear in the first's figure.

**Decision**: measure the **subject** environment. `CORPUS_MESSAGES=350000 CORPUS_ENVIRONMENTS=2
CORPUS_DAYS=91`, and the per-period figure comes from the harness's report rather than from the
rule above — the in-window/out-window split is exact by construction, and the split across
channels is floor division with a remainder. **The measurement uses the number the harness
prints** (T023), which is what makes FR-007 checkable.

**Alternatives considered**: building into the lane's `relay` database, which `corpus.mjs`
refuses by design (chapter 4.2). The refusal stands and the reconciler is pointed at the corpus
instead (R5).

---

## R4 — `corpus.mjs` WRITES NO OPERATIONAL COUNTER, AND THAT IS THE MISSING HALF

**Measured by reading the file.** `corpus.mjs` writes `messages`, `applications`,
`environments`, `message_edits`, an `update channels` and a `delete from outbox`. The only
occurrence of `usage_periods` in the whole file is a row count in its own closing report:

    usage_periods: await n1("select count(*)::int n from usage_periods"),

`usage_active_users` does not appear at all.

So the operational side of the reconciler's comparison has never existed at volume, for any
tenant, in any database this project has built. Measured on the lane: `usage_periods` holds
**2,317 rows over 2,212 environments, max `messages_sent` 1,017, mean 14**; and of the 4
environment ids in `daily_usage_billing`, **0 exist in Postgres**.

**Decision**: the harness writes both counters for the environments it creates. The foreign key
makes that natural rather than awkward — `usage_periods.environment_id` references
`environments.id`, and `corpus.mjs` already runs the platform's migration runner against its own
database, so the table exists there and the environments it references are the ones it just
wrote.

---

## R5 — THE RECONCILER IS ALREADY CALLABLE AGAINST ANY PAIR OF DATABASES

**Read in the tree.** `reconcile(db, store, { environmentId, period })` takes both sides as
arguments: a drizzle `Db` and an `AnalyticalStore`. `docs/12` §2.3's *"the reconciler must be
callable in isolation so a drift can be planted — that is a constraint on the chapter that
builds it"* was satisfied by chapter 4.7, and the planted-drift suite is the proof.

What is not injectable is the **script**. `scripts/reconcile-usage.mjs` calls
`createDb(createPool())` and `createAnalyticalStore()` with no arguments, so it reads the lane's
Postgres and the lane's `relay_analytics` from the environment and cannot be pointed anywhere
else without changing the environment.

**AND ONLY ONE OF THE TWO ADDRESSES CAN BE AN ARGUMENT.** The first draft of this item asked
for `--database` and `--analytics-database`. The second cannot work and reading one more file
says why: **`DB_ANALYTICS` is a constant at `reconcile.ts:110`**, interpolated into both
statements, and not a parameter. A flag on the script cannot reach it without changing
`reconcile()`'s signature — a 224-line file published as a whole body at chapter 4.7 and pinned
at 100/96/100/100.

And there would be nothing to point it at: `analytics/apply.mjs` hardcodes the same name at
line 18 and every statement must name the database, so this repository cannot build a second
analytical database at all. The corpus's analytical rows land in `relay_analytics` beside the
lane's, and the reconciler separates them by environment id — which is what it does for every
tenant anyway.

**AND TWO VALUES REACH A CLICKHOUSE STATEMENT, WHICH TOOK THREE READINGS OF THE SAME FILE.**
`reconcile.ts` interpolates both:

    WHERE environment_id = toUUID('${environmentId}')
      AND day >= toDate('${period}') AND day < toDate('${until}')

`reconcile-usage.mjs`'s `arg()` returns `process.argv[i + 1]` with no checks and produces both.
`toUUID()` and `toDate()` are not guards — the injection closes the quote before either function
sees it. Measured against the store, with a query scoped to one tenant and one month:

    honest period     208 rows
    ' OR 1=1 --    11,895 rows      the whole table, every tenant
    whole table    11,895 rows

**`until` is the one value that is safe**, and by accident rather than by design: `nextPeriod`
does `period.split("-").map(Number)` and rebuilds the string, so garbage becomes `NaN-NaN-01` and
ClickHouse rejects it. The Postgres side is parameterised — `usage-reads.ts` uses drizzle's `sql`
template — so only the analytical statements are exposed.

**Decision**: **one** new argument, `--database`, defaulting to today's behaviour. And **both**
interpolated values are validated before the reconciler is called: the environment id against the
canonical UUID pattern, the period against `^\d{4}-\d{2}-01$`. The first draft of this item put
the check on a database name that turned out not to exist; the second put it on one of the two
values that do. **Asking "which value reaches SQL?", finding one, and stopping is how the second
survived nine analysis passes.**

---

## R6 — A MATERIALISED VIEW IS A TRIGGER, SO A CORPUS LOADED FIRST PRODUCES AN ANALYTICAL ZERO

**Chapter 4.6 measured this and the backfill statement exists because of it.**
`analytics/0013_backfill_billing.sql` opens: *"a materialised view is a trigger on future
inserts, not a query over history. The corpus and the 154 connection records were both already
in the store when `0011` and `0012` were created."*

So the order matters: apply the analytical schema, then load, and the views fire; or load first
and run the backfill. Either works and the wrong combination produces `daily_usage_billing`
holding nothing, which the reconciler reports as `no-data` rather than as disagreement — a
verdict that reads like an absence of evidence.

**And the TTL cuts inside the window.** `message_events` carries 90 days and the corpus spans
120 by default, so 30 days vanish **at INSERT** (chapter 4.2). The measurement's month has to
sit inside 90 days of the load, or the figure is about the TTL.

**AND THE BACKFILL IS NOT SAFE TO REACH FOR WHEN THE ORDER GOES WRONG**, which is what the
first draft of the quickstart told a reader to do. `daily_usage_billing` is a
**`SummingMergeTree`**, so a second `INSERT … SELECT` adds rows that *sum* with the first and
doubles every count — and `apply.mjs`'s ledger has already recorded `0013`, so re-running the
applier is a silent no-op. **The obvious recovery does nothing and the obvious retry doubles the
answer.**

**Decision**: the quickstart applies the analytical schema **before** the load so the views fire,
and never runs the backfill by hand. A positive control after the load — `count()` on
`daily_usage_billing` — is what catches the wrong order, rather than a repair step that makes it
worse. The measurement records the order used and the window.

---

## R6a — THE CORPUS LOADS INTO THE LANE'S OWN ANALYTICAL STORE, AND ONLY A NUCLEAR CLEANUP EXISTS

**Read in the tree.** `scripts/scale/load-analytics.mjs:14` is `const DB = "relay_analytics"`.
The corpus's Postgres side is disposable — `corpus.mjs` builds `relay_corpus_<timestamp>` and
refuses `relay` — but its **analytical** side goes into the lane's own database. That is why the
materialised views fire at all (R6), and it means a measurement run deposits about **389,000
`message_events` rows** and their rollup rows beside chapter 4.4's request log and chapter 4.6's
billing rollups.

**The analytical store has no lane guard** (`gaps.md` 050-2, carried and unchanged), so nothing
stops that and nothing removes it. The only cleanup this repository ships is
`analytics/apply.mjs --drop-all`, which is `DROP DATABASE relay_analytics` at `apply.mjs:96` and
takes every other chapter's data with it.

**Decision**: the quickstart gains a scoped cleanup keyed on the corpus's environment ids, and
the harness prints those ids so the cleanup can name them. It **asserts the count** rather than
issuing the delete and returning: `ALTER TABLE … DELETE` is a queued mutation, chapter 4.6's
suite read three creations where it planted two by trusting the bare form, and chapter 4.7 found
a row from an earlier run still present.

**Alternatives considered**: loading into a corpus-specific ClickHouse database, which cannot
work — `apply.mjs` hardcodes `relay_analytics` at line 18 and every statement must name it
(R5), so the views this load depends on exist in one place only.

---

## R7 — THE CONSTITUTION STILL SAYS 0.1% FLAT, AND THE SRS NO LONGER DOES

**Read both.** Constitution III, fourth bullet:

> Metered totals MUST reconcile against operational counts to within 0.1%, verified by a daily
> job that alerts on breach.

SRS FR-ANL-06, as amended at revision 1.14 by chapter 4.7: the bound is **unreachable for three
of its four quantities** for reasons that are not defects — `uniq` is exact to 65,536 distinct
and 0.5676% at 65,537; a daily rollup's finest grain is a day and the raw TTL cuts at a
timestamp, so the oldest day in any window disagrees by 0% at midnight rising to 1.0989% just
before it; and connection-minutes count a different population on each side. The clause also now
records that *"raises an alert"* has no mechanism in this platform.

The constitution's governance section is explicit about what that is:

> where it conflicts with the SRS or SAD, the conflict MUST be resolved explicitly by amendment
> rather than ignored.

**Decision**: the milestone cannot publish "the meter agrees" against a bullet the SRS has
already contradicted. The conflict is named in the chapter and an amendment is proposed. This is
the **third** constitution III item this movement has produced — `gaps.md` 051-2 and 052-6 carry
the cross-store read — and unlike those two, this one is about the clause the milestone exists
to verify.

**Alternatives considered**: verifying the original clause, which would mean publishing a figure
the SRS says cannot exist for three quantities; and treating the SRS as authoritative silently,
which is the thing the governance section names.

---

## R7a — TWO OF THE CLAUSE'S THREE REQUIREMENTS HAVE NO MECHANISM, AND ONLY ONE WAS RECORDED

**Measured.** FR-ANL-06 and constitution III's fourth bullet ask for three things in one
sentence — a comparison within 0.1%, *"verified by a daily job"*, *"that alerts on breach"*.

    the comparison   EXISTS — chapter 4.7's reconciler and its planted-drift suite
    the daily job    NONE   — grep over package.json, *.yml, *.sh and Makefile for
                              `reconcile-usage`: zero hits. ci.yml:13 fires on `push`
                              and `pull_request`; there is no `schedule:` trigger
    the alert        NONE   — recorded at SRS 1.14

**The schedule is the one nobody wrote down.** 1.14 named the alert. `docs/12` §2.3 substituted
*"the lane, every run"* for *"daily"* and did not say it was a substitution — and §3's row 8
calls the reconciler *"FR-ANL-06's reconciliation job"*, where "job" means a program rather than
a scheduled task. **Chapter 4.7's own test file says the quiet half out loud** about the line it
moved into `reconcile.ts`: *"THIS RULE USED TO LIVE IN `scripts/reconcile-usage.mjs`, in one
expression no lane runs."* The expression got a test; the script never got a runner.

**AND THE TWO SCHEDULES ARE DIFFERENT CLAIMS RATHER THAN DIFFERENT FREQUENCIES.** A per-push
check on a planted fixture runs more often than daily and reads no real tenant. A daily job
against production tenants would catch a drift nobody planted, which is the only kind that
matters. §2.3's substitution trades the second for the first, and the trade is defensible — the
first is falsifiable and the second needs an alerting path this platform does not have — but it
is a trade and no document calls it one.

**THE PLATFORM HAS A PATTERN FOR THIS, WHICH IS WHAT MAKES IT A DECISION.** Five background
loops start with the api — `RELAY_OUTBOX_RELAY`, `RELAY_DELIVERY_RELAY`, `RELAY_QUOTA_RELAY`,
`RELAY_NOTIFICATION_RELAY`, `RELAY_EVENT_CONSUMER` — each with an off-switch, because feature 030
measured them sweeping the whole database while other suites' fixtures sat in it. The reconciler
is the one recurring job built as a hand-run script instead.

**Decision**: the milestone **decides and records** rather than necessarily building. A sixth
relay is the candidate and its cost is known: another loop in the api, another flag every
analytical suite has to set, and a job that reads both stores on a schedule nobody is watching
the output of — which is the alert problem again, one layer down. If it is not built, the
amendment states that the schedule has no mechanism, exactly as 1.14 stated it for the alert.

**Alternatives considered**: a `schedule:` trigger on CI, which runs against a lane rather than
against production tenants and so answers the weaker question with more machinery; and an npm
script, which is a runner in the sense that a hand-run script already is one.

---

## R7b — THE SERIES' OTHER GATE IS IN THE SAME STATE AS THIS MILESTONE'S, AND IS RECORDED AS CLOSED

**Read `docs/07-tutorial-plan.md` §6.** Defense 1 against tutorial rot is specified exactly:

> Every chapter's `CHECKPOINT` block is a script (`tutorial/checkpoints/part2-ch3.sh`) run
> against that chapter's git tag on every push to the tag's lineage. If chapter 2.3's checkpoint
> fails, the build fails.

**Measured**: `tutorial/checkpoints/` exists in none of the three repositories, and
`.github/workflows/ci.yml` contains **zero occurrences of `tag` or `checkpoint`**. What feature
024 closed defense 1 on is a workflow running the lanes, the coverage run, the site build and
the docs and fence checks — on `push` and `pull_request`, against the tip. That is a useful
thing and it is not the thing §6 describes.

**So a `<Checkpoint>` block is prose a reader may run by hand and nothing executes.** `gaps.md`
048-5 carries the adjacent half — *no gate checks that a chapter's tag matches the chapter* — and
this is why: nothing runs against a tag at all.

**AND §6 SAYS BOTH THINGS, TEN LINES APART, UNDER THE SAME DATE.** Line 725: *"Defense 1 does
**not** exist — there is no CI anywhere in the three repositories."* Line 732: *"Defense 1 now
exists."* Chapter 4.8 edited the second paragraph — adding the correction that *"real stores"*
excluded ClickHouse for six chapters — and left the first standing. **Correcting one half of a
contradiction without reading the other is how the contradiction gets stronger**, which is the
species SRS 1.11 produced by amending FR-ANL-07 and leaving FR-DSH-03, and which this feature's
T055a exists to fix one clause over.

**Decision**: the chapter carries a `<Checkpoint>` because a reader following along will run it,
and the record says plainly that nothing else will. §6's contradictory pair is amended in phase
6 with the rest.

**Why it belongs in this feature at all**: this is the chapter about a gate that cannot fail for
its own reason, and §6's defense 1 is a second gate in exactly that state — specified one way,
closed as something else, and recorded as closed. Finding it while writing the first is not a
coincidence worth ignoring.

---

## R7c — TWO OF `docs/07` §2's FLOORS, AND THE SAME TWO MILESTONES FAIL BOTH

**Measured**, with `scripts/prose-words.mjs` for the words and `grep -c "<Figure "` for the
diagrams:

    chapter                              prose   figures
    milestone-the-tuan-test              3,151         0     BELOW the figure floor
    milestone-the-isolation-gauntlet     1,873         1     BELOW both floors
    errors-that-resolve-and-an-outsider  1,683         2     BELOW the word floor
    the-job-that-checks-the-meter        2,265         3     inside both — 4.7
    the-log-a-customer-can-search        3,606         3     inside both — 4.8

§2 states *"Chapter length | 2,000–4,000 words"* and *"Visual elements | 2–4 captioned,
theme-legible diagrams per chapter … (≥1 per chapter half)"*. **Two of the three published
milestones fail the word floor and two fail the figure floor**, and the ordinary chapters pass
both.

**THAT IS ONE QUESTION RATHER THAN TWO.** A milestone assembles what earlier chapters built, so
it has less new prose and fewer new concepts to draw — and whichever way the word floor is
decided, the figure floor wants the same answer.

**AND NOTHING ENFORCES THE FIGURE COUNT.** `check:figures` has four failure modes and all of
them are about mechanism: a diagram not passed as `code=`, an import naming a missing export, a
name with no import. Its closing line is *"278 figures, every diagram passed as `code`; 280
imported bindings all resolve"* — a count of figures across the series and **not a count per
chapter**. A chapter with zero figures passes it, and `milestone-the-tuan-test` does.

`docs/07` §2's row reads *"Chapter length | 2,000–4,000 words + code | Longer chapters split; a
chapter is a sitting"*, and the code-chapter row confirms the count is prose outside fences —
which is what the script measures, so the instrument and the clause agree. **The rationale is
entirely about the upper bound.** The floor has none stated, and the document's only enforcement
story is a split: chapter 3.8 came to 4,700 words and became 3.8 and 3.9, recorded with the
number.

**Nothing in `docs/07` contemplates a chapter being too short**, and a milestone is structurally
shorter because it assembles what earlier chapters built rather than building something.

**Decision**: chapter 4.9 meets the bound — 2.8's milestone reached 3,151, so it is achievable —
and the feature **records the three measurements and decides** whether the bound covers a
milestone at all, with its reason. It does not exempt a chapter class on this evidence alone;
that is an amendment to `docs/07`, which this feature already opens twice (R7b, and `docs/12` §2.3).

**Alternatives considered**: reading §2's *"For code chapters (Part 1 onward)"* as scoping the
bound rather than the counting method, which the sentence does not support — it governs how the
words are counted, not which chapters are measured; and filing the two below-floor chapters as
prose to extend, which is cheap (a prose correction costs the fence chain nothing, measured at
4.8) and is the reader's loss rather than a defect, so it is filed rather than done here.

---

## R8 — `docs/11` IS THE PRECEDENT, AND IT HAS A SHAPE WORTH COPYING

**Read.** `docs/11-scalability-measurement-2026-09-06.md` discharged NFR-SCL-01 the way §2.3
says this one should: its own document, dated in the filename, the clause's verification letter
(**A** for analysis) as the method, the harness named, and the numbers with the conditions they
were taken under.

**AND THE RULE IT ESTABLISHES SAYS THIS DOCUMENT CANNOT DISCHARGE THE CLAUSE.** `docs/11`'s
method line is *"`A` — analysis, including load testing, **which is the verification method the
clause itself specifies**"*, and NFR-SCL-01's letter in the SRS **is** `A`. For an `A` clause a
published analysis *is* the verification, which is why that document discharged it.

**FR-ANL-06's letter is `T`.** Checked in the SRS: `| FR-ANL-06 | … | P3 | T |` against
`| NFR-SCL-01 | … | P1 | A |`. So the verification is a test in the lane — chapter 4.7's
planted-drift suite — and a prose document is evidence rather than discharge. Copying `docs/11`'s
shape without its rule would put `Method: T` on something that is not a test.

**Decision**: the measurement gets `docs/13-metering-measurement-<date>.md`, and its first
paragraph says what it is: **the clause's verification method is `T`, the test is in the lane,
and this document records the bound's resolution at a volume where 0.1% can be expressed** —
which the clause does not ask for and which nothing else publishes. It names the quantity, the
volume, the window, the two row counts, the smallest expressible drift at that volume, and the
three quantities the amended clause excludes.

**AND IT COPIES FOUR SECTIONS THE FIRST DRAFT OF THIS ITEM MISSED**, because R8 was written from
a description rather than from the file. `docs/11`'s sections are: *Why this exists · What was
measured · Results · What this says about consolidating the subject grammars · The finding
nobody was looking for · **What went wrong while measuring, and why the numbers still stand** ·
Reproducing · **What this left in the lane***. The two in bold are general rather than specific
to that measurement, and both matter here: the first is what this project's own writing guide
asks for — *"record what actually happened, including the parts that went badly"* — and
`docs/11`'s reads *"The first ladder measured the harness, not the gateway."* The second is R6a's
cleanup concern, already solved by precedent, with the row counts left behind.

---

## R9 — THE BOUND'S RESOLUTION, RE-DERIVED RATHER THAN COPIED

**Computed from the reconciler's own arithmetic**, not quoted from chapter 4.7. The denominator
is `max(analytical, operational)` and the comparison is `<=`, so for a volume *v* the smallest
drift that breaches is the smallest integer *d* with `d / (v + d) > 0.001` on the over side and
`d / v > 0.001` on the under side:

    volume        9    100    1,000   10,000   100,000
    smallest      1      1        2       11       101
    as a %   11.111  1.000    0.200    0.110     0.101

**0.1% first resolves at 10,000 and is only comfortable at 100,000.** Below 1,000 the bound
cannot be expressed at all: the smallest possible disagreement is already larger than it.

Against the lane's largest operational tenant-period — **1,017 messages** — the smallest
expressible drift is 2, or **0.197%**, twice the bound. So a green 0.1% assertion anywhere in
this lane claims that nothing drifted at all, which is a different and weaker statement.

**Decision**: every figure this feature publishes carries its volume, and the measurement is
taken at 100,000 or above.

---

## R10 — BOTH SIDES FROM ONE SOURCE IS A TAUTOLOGY, AND THE MEASUREMENT HAS TO SAY SO

**The sharpest thing in this research, and it is a design consequence rather than a measurement.**

If the harness derives `usage_periods.messages_sent` by counting the `messages` rows it just
wrote, and the analytical side is loaded from those same rows, the two sides agree **by
construction**. The reconciler would then report 0.0000% at any volume, and the figure would
establish nothing about the platform.

What it does establish is worth stating rather than dressing up: the reconciler's arithmetic at
volume, and the resolution of the bound at that volume. **The platform's own agreement is
established by a mechanism rather than by a measurement** — `sendMessage` writes the message and
increments the counter in one transaction — and chapter 4.7 verified that over 1,385 real
tenant-periods, finding **0 disagreements for a non-fixture reason**.

**Decision**: the measurement publishes both, separately labelled, and the planted drift is what
makes the arithmetic falsifiable. A section of the chapter says what the figure does not prove.

**Alternatives considered**: driving the corpus through the real send path so the counter is
incremented by the platform. At 100,000 messages that is 100,000 HTTP requests against a lane
that measured 20.5 ms p95 per send — over half an hour of wall clock, a different failure
surface, and a measurement of the test harness rather than of the meter. Recorded as the honest
version that was rejected on cost.

---

## R11 — FOUR PREMISES FROM THE BRIEF, CHECKED

`docs/12` §2.3 makes four claims about this milestone. Two hold and two do not.

| claim | holds? | what was measured |
|---|---|---|
| *"the reconciler must be callable in isolation"* | **yes**, satisfied at 4.7 | `reconcile(db, store, …)` takes both sides |
| *"`scripts/scale/` … has no analytical-volume mode and needs one"* | **no, stale** | `corpus.mjs` and `load-analytics.mjs` shipped at 4.1 and 4.2 |
| *"that harness is a chapter-1 dependency, not a chapter-8 one"* | **yes** | chapter 4.1 introduced it, as §2.3 asked |
| *"the planted drift is detected … the lane, every run"* | **no** | the gate stops before it, and has since 4.4 (R1) |

**The stale one matters** because it points at the wrong missing piece. What `scripts/scale/`
lacks is not analytical volume — it is the **operational counter** (R4), which §2.3 could not
have anticipated because chapter 4.7 had not yet found that every tenant in the platform is
one-sided.
