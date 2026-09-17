# Feature Specification: chapter 4.9 — "Milestone: the meter agrees"

**Feature branch / directory**: `054-chapter-4-9`
**Created**: 2026-09-17
**Status**: Draft
**Chapter**: Part 4, movement IV, **the milestone that closes it** — `docs/12` §3 row 10,
`docs/12` §2.3. Named by movement and title, never by number.

## Why this chapter exists

`docs/12` §2.3 says the milestone makes **two claims, not one**:

| half | claim | where |
|---|---|---|
| **CI gate** | a *planted* drift is detected and the reconciler raises | the lane, every run |
| **recorded measurement** | the 0.1% figure, at a volume where 0.1% is a real threshold | once, in the chapter |

Both halves already have most of their parts. Chapter 4.7 built the reconciler and a
planted-drift test; chapter 4.8 gave CI the ClickHouse that test needs. **Neither half works,
and the reasons were measured before this specification was written.**

### What was measured, 2026-09-17

**The gate cannot fail for its own reason, because it cannot run.** `pnpm test:integration` is
`turbo run test:integration --concurrency=1 --filter=!@relay/outsider` and stops scheduling at
the first failure: it plans 18 tasks, attempts **10**, and prints `Tasks: 8 successful, 10
total`. The api lane it runs first carries **six failures, none of them the reconciler's**:

    request-log.itest.ts   5 reds   polls for a row only an ingester can write, and
                                    `compose.yaml` ships none (gaps.md 050-8, since 4.4)
    limits.itest.ts        1 red    "the lane must configure a platform credential:
                                    expected undefined to be truthy" — a missing env var

So a build that plants a drift and a build that does not are the same colour, and have been
for every chapter of this movement.

**AND THAT SUMMARY LINE COUNTS TASKS, WHICH FOUR CHAPTERS HAVE READ AS LANES.** Measured with
`--dry=json`:

    18 planned  =  9 build  +  9 test:integration
    of the 9 test tasks, THREE are packages with no `test:integration` script at all —
    @relay/config, @relay/protocol, @relay/service-kit — which complete as successful no-ops
    six packages hold real suites: api, dispatcher, e2e, gateway, ingester, test-harness

So `8 successful, 10 total` is a task count including builds and no-ops, and **the number of
integration suites that ran before the stop is not derivable from it.** `gaps.md` 051-3 filed
this as *"reports one failure where several lanes fail"*, chapter 4.7 sharpened it to *"plans 18,
attempts 9"* and 4.8 re-measured it to 10 — all three read the count as lanes.

**And the sealed suite's absence is an exclusion by name, not the early stop.**
`--filter=!@relay/outsider` is in the command, one flag, added deliberately for a suite that
needs a running platform no lane starts. The five `request-log.itest.ts` failures need a running
ingester no lane starts, which is **the same shape and not the same mechanism**: `--filter`
selects packages, `@relay/outsider` is its own, and those five suites sit inside `@relay/api`
beside the reconciler's. Keeping one and dropping the other needs a vitest `exclude`, a second
config, or moving the file — each of which changes what the api's integration lane means for
everyone.

**`gaps.md` 053-3 is wrong about both halves of that, and one line below is why.**
`package.json:16` is `"test:outsider": "turbo run test:integration --filter=@relay/outsider"` —
so *"no local command runs the sealed suite"* is false, and it has been false since before the
item was written. The entry was made at chapter 4.8's close after running that suite by hand in
six commands, and no pass of this feature caught it until one opened the file.

**And both lines are published in the fence appendix rather than in any chapter.**
`relay-tutorial/fences/post-series.md` carries a `package.json` hunk whose `-`/`+` pair is the
`test:integration` line itself, and the appendix applies **after every chapter** — so the gate's
definition is the series' rather than a chapter's, and a chapter hunk that changed it would be
overwritten without reporting.

**And the 0.1% figure has no resolution anywhere in this lane, on either side.**

    analytical side   daily_usage_billing      7 rows over 4 environment ids
                      of those 4, present in Postgres:   0
    operational side  usage_periods        2,317 rows over 2,212 environments
                      max messages_sent    1,017 · mean 14

No tenant has both sides. And at the largest operational tenant-period there are 1,017
messages, where **the smallest drift the reconciler can express is 2 — 0.197%, twice the
bound.** The threshold's resolution against volume, from chapter 4.7:

    volume        9    100    1,000   10,000   100,000
    smallest      1      1        2       11       101
    as a %   11.111  1.000    0.200    0.110     0.101

**0.1% first resolves at 10,000 per tenant-period and is only comfortable at 100,000.**

**The harness §2.3 asked for exists for one side only.** `scripts/scale/corpus.mjs` builds a
million messages across 3 environments over 120 days — so §2.3's *"it has no analytical-volume
mode and needs one"* is stale, chapters 4.1 and 4.2 built it. But it writes `messages`,
`applications`, `environments`, `channels` and `message_edits`, and **it never writes
`usage_periods`**: the only occurrence of that table in the file is a row count in its own
report. The operational counter the reconciler compares against does not exist at volume, and
nothing builds it.

### The clause has three parts and the platform has one

FR-ANL-06, and constitution III's fourth bullet with it, asks for three things in one sentence:
*"Metered totals MUST reconcile against operational counts to within 0.1%, **verified by a daily
job** that **alerts on breach**."*

| part | mechanism in this platform |
|---|---|
| the comparison | **exists** — chapter 4.7's reconciler, with a planted-drift suite |
| the **daily job** | **none.** Nothing runs `scripts/reconcile-usage.mjs`: no npm script, no CI step, no `schedule:` trigger — `ci.yml` fires on `push` and `pull_request` — and no background loop |
| the **alert** | **none**, recorded at SRS 1.14. The job exits non-zero and the two mail paths share a transport whose default is a local catcher |

**Only the second of those three was missing from every record.** 1.14 named the alert;
`docs/12` §2.3 substituted *"the lane, every run"* for *"daily"* without saying it was a
substitution; and chapter 4.7's own test file says the quiet half out loud about the line it
moved — *"this rule used to live in `scripts/reconcile-usage.mjs`, in one expression no lane
runs."* The expression got a test. The script still has no runner.

**Per-push against a planted fixture and daily against real tenants are different claims**, and
the first is not weaker for being more frequent — it is weaker for never touching a real tenant.

**And the platform has a pattern for recurring work, which makes this a decision rather than a
gap.** Five background loops start with the api — `RELAY_OUTBOX_RELAY`,
`RELAY_DELIVERY_RELAY`, `RELAY_QUOTA_RELAY`, `RELAY_NOTIFICATION_RELAY` and
`RELAY_EVENT_CONSUMER` — each with an off-switch, because feature 030 measured them sweeping the
database during tests. The reconciler is the one recurring job built as a hand-run script
instead.

### And the clause this milestone verifies is not the one the brief was written against

FR-ANL-06 was **amended at SRS 1.14** by chapter 4.7, because the clause as written cannot
hold. The bound is unreachable for three of its four quantities for reasons that are not
defects: `uniq` is exact to 65,536 distinct and 0.5676% at 65,537; a daily rollup's finest
grain is a day and the raw TTL cuts at a timestamp, so the oldest day in any window disagrees
by 0% at midnight rising to 1.0989% just before it; and connection-minutes count a different
population on each side.

**One quantity can meet 0.1%: messages sent**, because `sendMessage` writes the message and
increments the counter in one transaction. The milestone measures that one and says so, rather
than publishing a figure whose scope a reader has to reconstruct.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A planted drift fails the build (Priority: P1)

An operator pushes a change that breaks the metering agreement. The build goes red, and the
failure names the drift rather than something else.

**Why this priority**: it is the half §2.3 calls falsifiable, and it is the half that does not
work. A gate that is red for somebody else's reason is not a gate.

**Acceptance scenarios**

1. **Given** the reconciler and its planted-drift test, **When** the integration gate runs on a
   clean tree, **Then** the gate is green and the reconciler's suite is among the suites that
   executed — shown by naming the suite, not by the absence of a failure.
2. **Given** the same tree with the drift threshold's comparison inverted, **When** the gate
   runs, **Then** it is red and the failure names the reconciler.
3. **Given** a lane where the ingester is absent, **When** the gate runs, **Then** the
   reconciler's verdict is still reached — the gate's colour does not depend on a process the
   platform does not ship.
4. **Given** the gate is green, **When** a reader asks which suites ran, **Then** the answer is
   a count the command itself prints, not an inference from the exit code.

### User Story 2 - The 0.1% figure has a volume beside it (Priority: P1)

A reader wants to know whether the platform meters accurately. They find one number, the volume
it was taken at, the quantity it is about, and the three quantities it is not about.

**Why this priority**: §2.3 puts the recorded measurement in the chapter rather than the lane
precisely because the lane cannot produce it. A figure with no volume is the assertion that
cannot fail.

**Acceptance scenarios**

1. **Given** a tenant-period holding at least 100,000 messages on both sides, **When** the
   reconciler runs over it, **Then** the agreement figure is published with the row counts on
   each side and the smallest drift expressible at that volume.
2. **Given** the published figure, **When** a reader looks for its scope, **Then** the document
   names **messages sent** and names the three quantities the amended clause excludes, with the
   reason for each.
3. **Given** a drift planted at exactly the bound and one planted one unit past it, **When** the
   reconciler runs, **Then** the first passes and the second breaches — at the measurement's own
   volume, not at the lane's.
4. **Given** the measurement document, **When** somebody wants to reproduce it, **Then** the
   commands are in it and they run as written.

### User Story 3 - Both sides of the comparison exist for one tenant (Priority: P2)

Somebody building a metering measurement needs a tenant that has operational counters and
analytical rollups for the same period, at a volume worth comparing.

**Why this priority**: it is the dependency both halves stand on, and it is the part that does
not exist. Nothing in this repository has ever produced a tenant with both sides.

**Acceptance scenarios**

1. **Given** the volume harness, **When** it is asked for a tenant at a stated volume, **Then**
   it produces operational messages, the operational counters that a real send would have
   incremented, and the analytical rows a real ingester would have written.
2. **Given** that tenant, **When** the reconciler is asked for its verdict, **Then** the verdict
   is `pass` or `breach` rather than `no-data` or `not-comparable` — the two verdicts chapter 4.7
   found every tenant in the platform to be in.
3. **Given** the harness, **When** it is run twice, **Then** the second run does not depend on
   the first having been cleaned up by hand.

### User Story 4 - The movement's claims are collected, including the ones it cannot make (Priority: P3)

A reader finishing movement IV wants to know what the four chapters before this one established
and what they could not.

**Why this priority**: a milestone that only lists successes is the document nobody trusts. The
movement produced two clause amendments and one requirement that was defined rather than built.

**Acceptance scenarios**

1. **Given** the milestone chapter, **When** a reader looks for movement IV's outcome, **Then**
   it names what shipped, what was amended, and what was defined and left unbuilt, each with the
   measurement behind it.
2. **Given** the chapter, **When** a reader asks what is still open at the movement's close,
   **Then** the carried items are named with their current measurements rather than their
   original wording.

### Edge Cases

- **A volume the machine cannot hold.** 100,000 messages per tenant-period across enough periods
  to matter is a corpus, not a fixture. If the volume cannot be built on the lane's hardware, the
  measurement states the volume it did reach and the resolution that volume gives.
- **A corpus in its own database.** `corpus.mjs` refuses to build into the lane's `relay`
  database, which is correct and means the reconciler must be pointed at the corpus rather than
  the corpus pushed into the lane.
- **The harness's own floors and its units, all three read only after a number had been
  published that ignored them.** `corpus.mjs` refuses `CORPUS_DAYS` at or below **90** — the
  query window it exists to fill — and `CORPUS_ENVIRONMENTS` below **2**. And
  `CORPUS_MESSAGES` is the **subject** environment's ninety-day window rather than a total, with
  each neighbour getting a tenth, so a month is a third of it. A volume expressed as "one
  environment over one month" cannot be built, and one expressed as a total is not what the
  script reads. **The per-period figure is read off the harness's report.**
- **The corpus's analytical half lands in the lane's own store and nothing removes it.**
  `load-analytics.mjs` writes `relay_analytics`, which is what lets the materialised views fire
  and what leaves ≈389,000 rows beside four chapters' data. The only cleanup this repository
  ships is `DROP DATABASE relay_analytics`, so a scoped one is part of the work.
- **The backfill statement doubles what it is run over twice.** `daily_usage_billing` is a
  `SummingMergeTree`, so a second `INSERT … SELECT` sums with the first; and the applier's
  ledger makes re-running it a silent no-op. The recovery from a wrong load order is to apply
  the schema first and load again, not to reach for the backfill.
- **A rollup that arrives by materialised view.** A view is a trigger on future inserts, not a
  query over history (chapter 4.6), so a corpus loaded before the view exists produces an
  analytical side of zero and a comparison that reads as total disagreement.
- **The TTL cutting inside the measurement.** The oldest day of any window disagrees for a reason
  that is not drift. The measurement's window has to sit inside retention on both sides, or say
  which day it excluded and why.
- **A gate that runs more often than daily and proves less.** A per-push check on a planted
  fixture satisfies `docs/12` §2.3's *"the lane, every run"* and does not satisfy FR-ANL-06's
  *"daily job"*, because it never reads a real tenant. Whichever the milestone claims, it says
  which of the two it is.
- **A bound whose own precedents fail it.** `docs/07` §2 gives one chapter-length range and one
  escape — the *upper* bound, which chapter 3.8 split on at 4,700 words. **Nothing in the
  document contemplates a chapter being too short**, and a milestone is structurally shorter
  because it assembles what earlier chapters built rather than building something.
- **A red workflow that cannot get redder.** `check:fences` exits 1 at 110 as its job's last
  step, so no gate in this workflow has a legible verdict at the workflow level. A drift that
  turns one step red is still worth showing; a claim that it *"fails the build"* is not available.
- **A green gate on a lane with no ingester.** Five suites are red for that reason. If the gate is
  made green by starting an ingester, it is green for a configuration CI does not have; if it is
  made green by excluding those suites, the exclusion is a hand-maintained list.
- **A drift planted in the wrong direction.** `max(a, o)` is the denominator and the comparison
  is `<=`, so the smallest breaching drift is the same size on both sides and a drift computed
  against the smaller side lands inside the bound (chapter 4.7).

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The integration gate shall reach the reconciler's suite on a clean tree, and the
  run shall report **how many integration suites executed, against how many exist** — a count of
  suites, not of turbo tasks. Turbo's summary counts tasks: 18 planned is 9 builds and 9 test
  tasks, three of which are packages with no integration script. The count comes from the lanes'
  own output or from the `.itest.ts` files in the tree, not from that line.
- **FR-002**: The gate shall be shown red by a change that breaks the metering agreement, and the
  failure shall name the reconciler. **The claim is scoped to the step** — `pnpm
  test:integration` — because the workflow's own colour is not a signal: `ci.yml`'s tutorial job
  ends with `pnpm check:fences`, which exits 1 at the standing count of 110 and has on every push
  since feature 045.
- **FR-002a**: The feature shall record that the workflow is red on every push, and shall
  **decide** whether to change that arrangement — as an architecture decision with a reversal
  condition. Building the change is not required; deciding and recording is. This is the
  milestone's own defect one level up: the api lane's six reds mask the reconciler inside a job,
  and `check:fences` masks every job's colour inside the workflow.
- **FR-003**: The gate's colour shall not depend on a process the platform does not ship. Suites
  that cannot pass without an ingester shall either be given one in the environment that runs
  them, or be separated from the gate with the separation recorded as a decision — **and the
  separation is not a `--filter` flag**, because those suites share a package with the
  reconciler's. It needs a vitest `exclude`, a second config, or moving the file, and the
  decision weighs that cost rather than a cheaper one.
- **FR-004**: The six inherited failures in the api lane shall each be resolved, given a running
  fix, or recorded with the reason and the chapter that owns it. None shall be left as an
  unexplained red.
- **FR-004a**: The feature shall record whether FR-ANL-06's **daily schedule** has a mechanism,
  and shall **decide** whether the reconciler acquires one — recorded as an architecture decision
  with its drivers, its rejected alternatives and its reversal condition. Building it is not
  required; deciding and recording is. The candidate is a sixth background relay, and its cost is
  the one feature 030 measured for the other five.
- **FR-005**: A volume harness shall produce a tenant-period with **both** an operational message
  count and the operational counter rows the send path would have written.
- **FR-006**: The same harness shall produce the analytical rows for that tenant-period, so that
  the reconciler's verdict is `pass` or `breach` rather than `no-data` or `not-comparable`.
- **FR-006a**: The harness shall report the environment ids it created, and a scoped cleanup
  shall remove its analytical rows and be **verified by count** rather than by issuing the
  delete. The analytical store has no lane guard and the only cleanup shipped today drops the
  whole database.
- **FR-006b**: The harness shall write `usage_periods` and `usage_active_users` as one unit, and
  **both row counts shall be asserted before the reconciler is asked anything**. With the first
  written and the second not, the active-user comparison reads 0 against ≈5,000 and returns
  `breach` — the harness's, not the platform's.
- **FR-006c**: **Every caller-supplied value the reconciler interpolates into an analytical
  statement shall be validated before the reconciler is called**, and each refusal shall be
  tested. There are two — the environment id and the period — and both come from the same
  unchecked `arg()`. Measured: a query scoped to one tenant and one month returns 208 rows
  honestly and **11,895 under `2026-09-01') OR 1=1 --`**, which is the whole table across every
  tenant. `toUUID()` and `toDate()` are not guards; the injection closes the quote first.
- **FR-007**: The harness shall state the volume it produced and the smallest drift expressible
  at that volume, in the same output as the figure.
- **FR-007a**: Every published per-quantity verdict shall carry **what it is worth**, not only
  what it is. Of the reconciler's four rows on a messages-only corpus, one is the measurement,
  one agrees by construction, one is a `pass` over 0 against 0, and one is `not-comparable`. A
  table of four verdicts without that column reads as corroboration.
- **FR-008**: The agreement figure shall be published with its quantity named — messages sent —
  and with the three quantities the amended FR-ANL-06 excludes, each with its reason.
- **FR-009**: A drift planted at the bound and a drift planted one unit past it shall be shown to
  pass and breach respectively, **at the measurement's volume**, and the boundary cases shall sit
  on the bound rather than near it.
- **FR-010**: The measurement shall be published as its own document, following
  `docs/11-scalability-measurement-2026-09-06.md`: the harness named, the commands reproducible
  as written, and **the clause's own verification method stated**. FR-ANL-06's letter is `T`, so
  the document shall say plainly that **the test discharges the clause and the document does
  not** — `docs/11` discharged NFR-SCL-01 because that clause's letter is `A` and a published
  analysis is the verification for an `A`. The document records the bound's resolution at a
  volume where 0.1% can be expressed, which the clause does not ask for and nothing else
  publishes.
- **FR-010a**: The document shall carry a section recording **what went wrong while measuring
  and why the numbers still stand**, and a section recording **what the run left in the lane**.
  Both are in the precedent and neither is specific to it.
- **FR-011**: The measurement's window shall sit inside retention on both sides, or shall name
  the day it excluded and why.
- **FR-012**: The milestone chapter shall record what movement IV established, what it amended,
  and what it defined and did not build, each with the measurement behind it.
- **FR-013**: Every carried gap item shall be re-measured at this close rather than copied.
- **FR-014**: No figure shall be published without the volume it was taken at.
- **FR-015**: The chapter shall not re-derive chapters 4.5 through 4.8's mechanics. It cites them.
- **FR-016**: The chapter shall be registered in the tutorial manifest and shall build.
- **FR-017**: Prose outside code fences shall measure between 2,000 and 4,000 words, with at
  least one `<Trap>` and at least one `<Why>`.
- **FR-017a**: The feature shall record, for **all three published milestone chapters**, their
  prose words **and their figure counts**, and shall **decide once** whether `docs/07` §2's
  chapter floors apply to a milestone — recorded with the reason. Measured:

      chapter                              prose   figures
      milestone-the-tuan-test              3,151         0
      milestone-the-isolation-gauntlet     1,873         1
      errors-that-resolve-and-an-outsider  1,683         2
      the-log-a-customer-can-search        3,606         3   (4.8, an ordinary chapter)

  §2 states *"2,000–4,000 words"* and *"2–4 captioned diagrams per chapter (≥1 per chapter
  half)"*, neither with a milestone exemption. **The same two chapters fail both floors**, which
  is one question rather than two: a milestone assembles what earlier chapters built, so it has
  less new prose and fewer new concepts to draw. Chapter 4.9 meets both either way; what is
  decided is whether the other two are a gap or a category the document never covered.
- **FR-017b**: The chapter shall carry **2 to 4 figures, with at least one in each half**
  (`docs/07` §2). Nothing enforces this: `check:figures` verifies that every diagram is passed as
  `code=` and that every import resolves, and **not the count** — so a chapter with zero figures
  passes that gate.
- **FR-018**: The fence-chain delta shall be reported as a delta against this feature's opening
  measurement, by kind and locale, with the two HEAD classes split.
- **FR-019**: Where a measurement falsifies a published clause or document, the clause or document
  shall be amended rather than left to diverge.
- **FR-020**: The milestone shall state, in one sentence a reader can act on, whether the meter
  agrees.

### Key Entities

- **The reconciler** — `services/api/src/metering/reconcile.ts`, built at chapter 4.7. Compares
  one tenant-period at a time, produces `pass`, `breach`, `no-data` or `not-comparable`, and
  exits non-zero on any breach.
- **The operational side** — `usage_periods` and `usage_active_users` in PostgreSQL, written by
  the send path inside the transaction that writes the message.
- **The analytical side** — `daily_usage_billing` in ClickHouse, fed by two materialised views
  and a backfill statement.
- **The volume harness** — `scripts/scale/`, which today builds a message corpus in its own
  database and writes neither operational counter.
- **The measurement document** — a new `docs/` file, the third of its kind after `docs/11` and
  the reader protocol's record.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A planted drift turns the integration gate red, shown by running it. The gate is
  `pnpm test:integration`; the workflow's colour is not part of this criterion and the record
  says why.
- **SC-002**: The same gate is green on a clean tree, and the run reports a **suite** count that
  a reader can compare against the number of `.itest.ts` files in the tree. A task count is not
  that number and the two differ by nine builds and three no-ops.
- **SC-003**: Every one of the six inherited api-lane failures is either green or recorded with
  its reason and owner; the count of unexplained reds is **0**.
- **SC-002a**: Both interpolated values are refused when malformed, shown by a test for each,
  and the count of caller-supplied values reaching an analytical statement without validation is
  **0** — established by reading the statements rather than by naming the ones already known.
- **SC-001a**: The record names the standing fence count, the step that exits 1 on it, and the
  decision taken about the arrangement.
- **SC-003a**: The record states, for each of FR-ANL-06's three requirements — the comparison,
  the daily schedule, the alert — whether a mechanism exists in this platform, and the schedule
  decision is recorded with its cost either way.
- **SC-004**: A tenant-period exists with at least **100,000** messages on both sides, or the
  highest volume the lane could build is published with the resolution it gives.
- **SC-005**: The reconciler returns `pass` or `breach` for that tenant-period — not `no-data`
  and not `not-comparable`.
- **SC-005a**: `message_events` and `daily_usage_billing` hold the same row counts after the
  cleanup as before the corpus was built.
- **SC-006**: The agreement figure is published with the row counts on each side, the volume, and
  the smallest expressible drift at that volume.
- **SC-006a**: The per-quantity table names, for each of the four, whether its verdict is a
  measurement, an agreement by construction, a zero-against-zero, or `not-comparable`.
- **SC-007**: A drift at the bound passes and a drift one unit past it breaches, at the
  measurement's volume.
- **SC-008**: The published figure names messages sent as its quantity and names the three
  excluded quantities with their reasons.
- **SC-009**: The measurement document's commands run as written, checked by running them.
- **SC-009a**: The document states which artifact discharges FR-ANL-06 — the test — and carries
  both the what-went-wrong and what-was-left-behind sections.
- **SC-010**: The chapter names movement IV's amendments — FR-ANL-06 at SRS 1.14, and FR-ANL-10,
  FR-DSH-03 and FR-ANL-08 at 1.15 — and the requirement that was defined rather than built.
- **SC-011**: Every carried gap item carries a measurement taken during this feature.
- **SC-012**: Prose measures between 2,000 and 4,000 words, with at least one `<Trap>` and one
  `<Why>`, counted by `scripts/prose-words.mjs`.
- **SC-012a**: The three published milestones' prose counts **and figure counts** are recorded,
  and the one decision about whether §2's floors cover a milestone is stated with its reason.
- **SC-012b**: The chapter carries 2 to 4 figures with at least one in each half, counted in the
  same pass as the prose words.
- **SC-013**: The chapter is registered and `pnpm build` renders its page.
- **SC-014**: The fence-chain delta is reported against this feature's opening, by kind and
  locale.
- **SC-015**: The milestone's one-sentence answer is in the chapter, and it is supported by a
  figure published in the same chapter.

---

## Which of `docs/07` §2's chapter conventions this feature binds, and why

§2 is a table of chapter rules and this specification binds some of them. Saying which, and
which not, stops the omissions reading as oversights — and pass 13 found the figure count
missing precisely because nobody had asked.

| §2 row | bound here | why |
|---|---|---|
| Chapter length, 2,000–4,000 words | **FR-017, FR-017a** | countable, and two milestone precedents fail it |
| `WHY` and `TRAP` boxes | **FR-017** | `docs/07` §4 Rule 3 makes `WHY` the paperwork link |
| `CHECKPOINT` box | **T054a** | the convention lapsed at 4.7 and returned at 4.8; nothing enforces it (R7b) |
| Visual elements, 2–4 figures, ≥1 per half | **FR-017b, FR-017a** | countable, unenforced, and two milestone precedents fail it |
| Git tag per chapter, fence rules | **FR-018, T069–T063** | `check:fences` enforces these |
| Voice — first person plural, present tense | **not bound** | no countable value and no gate; a reader notices, and a requirement that cannot be checked is one this project has learned to leave out |
| `SKIP AHEAD` box | **not bound** | its absence costs a reader one `git checkout` hint, and `pnpm build` does not care. Named here so it is a decision rather than a gap |

## Assumptions

- **The milestone is a chapter, not only a gate.** Part 2's "the Tuan test" and Part 3's "the
  isolation gauntlet" and "an outsider integrates" are all chapters that build something. This one
  builds the harness and the gate and publishes the measurement.
- **`corpus.mjs` stays in its own database.** It refuses `CORPUS_DATABASE=relay` deliberately
  (chapter 4.2), so the reconciler is pointed at the corpus rather than the corpus at the lane.
- **The 100,000 target is the resolution requirement, not a product requirement.** It comes from
  the smallest-expressible-drift table: below 10,000 the bound cannot be expressed at all. It is
  a **per-tenant-per-period** figure, and the corpus that produces it is larger — the harness's
  two floors mean the volume is spread over at least two environments and more than ninety days.
- **The reconciler reads one analytical database and always will.** `DB_ANALYTICS` is a constant
  inside `reconcile.ts` and `apply.mjs` hardcodes the same name, so the corpus's analytical rows
  live in `relay_analytics` beside the lane's and are separated by environment id — which is what
  the reconciler does for every tenant. Only the PostgreSQL side is addressable.
- **Movement IV's chapters are 4.5 through 4.8** — the gateway's first stream, the rollup nobody
  read, the job that checks the meter, and the log a customer can search. The milestone closes the
  movement and does not reopen their decisions.
- **FR-ANL-06 as amended is the clause under verification.** Verifying the original would mean
  publishing a number the amended clause says cannot exist.
- **The chapter after this one opens movement V** — hosted media — and inherits nothing from this
  milestone except the harness.

## Dependencies

- Chapter 4.7's reconciler and its `exitCodeFor`, and the planted-drift suite.
- Chapter 4.8's CI ClickHouse service and `analytics/apply.mjs` step, without which the
  reconciler's suite cannot run in CI at all.
- `scripts/scale/corpus.mjs` and `load-analytics.mjs` for the message corpus.
- SRS revisions 1.14 and 1.15, which are what the measurement is taken against.
