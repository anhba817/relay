# Contract — the volume harness, the reconciler script, and the gate

Written before the code. Chapter 4.2's lesson about `contracts/` is that it is the artifact
nothing else reads, so every claim here is one a test or a command can drive.

---

## `scripts/scale/corpus.mjs` — the operational counter side

**What it does today**: builds `relay_corpus_<timestamp>` and writes `applications`,
`environments`, `channels`, `messages` and `message_edits`. It refuses `CORPUS_DATABASE=relay`
and that refusal stands.

**What this feature adds**: after the messages are written, one statement per counter table,
derived from the rows it just wrote.

    usage_periods       one row per (environment_id, period)
                        messages_sent = count of that environment's messages in that period
                        connection_minutes = 0, and the report says so

    usage_periods and usage_active_users are ONE UNIT, and both row counts are asserted
    before the reconciler is asked anything. With the first written and the second not,
    `op.activeUsers` reads 0 — it is a COUNT OF ROWS, so absent and zero are the same
    number — against an analytical ~5,000, and the verdict is `breach`. The harness's,
    not the platform's.

    usage_active_users  one row per (environment_id, period, user_id)
                        user_id IS NOT NULL, and it is also a FOREIGN KEY to users.id
                        (schema.ts:1043) — so a null sender has no row to reference, which
                        makes the exclusion the schema's rule rather than the harness's.
                        The analytical side's uniqState ignores NULL, and the two agree
                        only if this side excludes them too

**`connection_minutes` is zero and that is not a gap.** The corpus writes no connections, and a
counter that invented them would make the connection-minutes comparison a measurement of the
harness. The amended FR-ANL-06 already excludes that quantity from the bound; the report names
the zero rather than letting a reader infer agreement from it.

**The closing report gains four lines**: the rows written per counter table, the periods
covered, — for the largest period — the volume and the smallest drift expressible at it, and
**the environment ids it created**. A figure without its volume is the assertion that cannot
fail; and without the ids there is no way to clean up afterwards, because the analytical side
lands in the lane's own `relay_analytics` and has no lane guard (R6a).

**AND THE VOLUME IS NOT DERIVABLE FROM THE KNOBS.** `CORPUS_MESSAGES` is the **subject**
environment's ninety-day window, not a total: `planFor` computes `ceil(messages × days / 90)`
for the subject and gives each neighbour a tenth. A month is a third of `CORPUS_MESSAGES`, and
the report is what the measurement quotes.

**AND THE REPORT SAYS THE SIDES ARE DERIVED FROM ONE SOURCE.** This is the sentence R10 exists
for: the counters are computed from the same `messages` rows the analytical side is loaded
from, so they agree by construction. What the corpus establishes is the reconciler's arithmetic
at volume, not the platform agreeing with itself.

---

## `scripts/reconcile-usage.mjs` — two addresses

**Today** it takes `--environment` and `--period` and reads the lane from the environment:
`createDb(createPool())` and `createAnalyticalStore()`, both with no arguments.

**It gains one optional argument**, and the default is exactly today's behaviour so the existing
invocation is unchanged:

| argument | default | what it addresses |
|---|---|---|
| `--database <url>` | `DATABASE_URL` from the environment | the PostgreSQL side |

**There is no `--analytics-database`, and the first draft of this contract had one.**
`DB_ANALYTICS` is a constant at `reconcile.ts:110`, interpolated into both statements and not a
parameter, so a flag on the script cannot reach it without changing the signature of a 224-line
file published as a whole body and pinned at 100/96/100/100. And there would be nothing to point
it at: `analytics/apply.mjs` hardcodes the same name at line 18, so this repository cannot build
a second analytical database. The corpus's rows live in `relay_analytics` beside the lane's and
the reconciler separates them by environment id, as it does for every tenant.

**TWO VALUES REACH A CLICKHOUSE STATEMENT AND BOTH ARE VALIDATED.** `reconcile.ts` interpolates
`WHERE environment_id = toUUID('${environmentId}')` and
`AND day >= toDate('${period}') AND day < toDate('${until}')`, and `arg()` produces the first two
with no checks. `toUUID()` and `toDate()` are not guards — the injection closes the quote before
either function sees it. Measured, scoped to one tenant and one month:

    honest period     208 rows
    ' OR 1=1 --    11,895 rows      the whole table, every tenant

| value | check | why |
|---|---|---|
| `--environment` | canonical UUID pattern | interpolated in both statements |
| `--period` | `^\d{4}-\d{2}-01$` | interpolated in both statements, and it is the one nine analysis passes missed |
| `until` | none needed | `nextPeriod` splits on `-`, maps to `Number` and rebuilds, so garbage becomes `NaN-NaN-01` and the server rejects it. Safe by accident rather than by design, and recorded as such |

Both refusals are tested. **The count that matters is not "the known values are checked" but
"no unvalidated value reaches a statement"**, established by reading the statements.

**The PostgreSQL URL needs no such check** and the test says why rather than leaving the
asymmetry unexplained: `pg` parses it into a connection, it is never concatenated into a
statement.

**The exit code is unchanged.** `exitCodeFor` returns 1 if any row breaches, and that is the
line the CI gate reads.

---

## The integration gate

**What it must report, which it does not today**: `pnpm test:integration` prints `Tasks: 8
successful, 10 total` for a run that planned 18. A reader cannot tell a green gate from a gate
that stopped early, and the two are the same exit code.

The contract, in the order the claims matter:

1. **A run reports how many suites it attempted against how many it planned.** A number the
   command prints, not an inference from the exit code.
2. **A planted drift makes the run red**, and the failure names the reconciler's suite.
3. **The run's colour does not depend on a process the platform does not ship.** Five suites
   are red for want of an ingester; either the environment that runs them has one, or they are
   outside this gate and the separation is an ADR with a reversal condition.
4. **Each remaining red is green or recorded** with its cause and the chapter that owns it. The
   count of unexplained reds is 0.

**The shape is a decision and not an implementation detail.** `--continue` runs every task and
reports all failures; raising `--concurrency` runs lanes in parallel against one PostgreSQL,
which feature 045 measured down to two workers for the api and four for the gateway. Whichever
is chosen, VII wants it recorded.

---

## `docs/13-metering-measurement-<date>.md` — the published figure

On `docs/11-scalability-measurement-2026-09-06.md`'s model: its own document, dated in the
filename, the harness named, and **the clause's verification method stated rather than
borrowed**.

**AND THAT PRECEDENT SAYS THIS DOCUMENT DOES NOT DISCHARGE THE CLAUSE.** `docs/11`'s method line
is *"`A` — analysis, including load testing, **which is the verification method the clause itself
specifies**"*, and NFR-SCL-01's letter is `A`: for an `A` clause a published analysis *is* the
verification. **FR-ANL-06's letter is `T`.** So the planted-drift suite is the discharge and this
document is evidence — and its first paragraph says so, because putting `Method: T` on prose
would claim a document is a test.

**What it must contain**, each item because leaving it out is a way this project has been wrong
before:

| item | why |
|---|---|
| the quantity — **messages sent** | three of the four cannot meet the bound, and a figure with no scope reads as all four |
| the volume, per tenant-period | 0.1% does not resolve below 10,000 (R9) |
| the row counts on both sides | a percentage without its operands cannot be checked |
| the smallest expressible drift at that volume | it is what the percentage means at that size |
| the window, and whether the TTL cut inside it | the oldest day of any window disagrees for a reason that is not drift (chapter 4.2) |
| a drift at the bound and one past it | boundary cases must sit ON the bound, shown by changing `<=` to `<` and watching exactly one assertion move |
| **what the figure does not prove** | both sides derive from one source (R10) |
| the three excluded quantities, each with its reason | `uniq`'s cliff at 65,536, the retention boundary, two populations |
| **the per-quantity table, with a standing column** | the reconciler prints four verdicts and a messages-only corpus gives each a different worth: `messages` is the measurement, `activeUsers` agrees by construction (`uniq` exact below 65,536 against a 5,000-user corpus), `connectionMinutes` is a `pass` over **0 against 0** because both-zero is agreement, and `storedMessages` is `not-comparable`. **Three of the four passes are not evidence**, and a table without that column reads as corroboration |
| the commands, runnable as written | checked by running them, not by reading them |
| **what went wrong while measuring, and why the numbers still stand** | in the precedent, and what this project's writing guide asks for. `docs/11`'s reads *"The first ladder measured the harness, not the gateway"* — a document that only reports the plan working is one nobody trusts |
| **what the run left in the lane** | in the precedent, with row counts. The corpus's analytical half lands in the lane's own store (R6a), so this section is where the cleanup's before-and-after goes |

**The clause it is taken against is FR-ANL-06 as amended at SRS 1.14**, and the document says
so in its first paragraph. Verifying the original would mean publishing a number the SRS says
cannot exist.

---

## The constitution amendment proposal

**Not a change this feature makes on its own.** The governance section specifies a PR modifying
`.specify/memory/constitution.md`, stating the motivation, the semantic version bump, and the
migration impact on in-flight specs and plans.

What the proposal carries:

- **The conflict, quoted from both documents.** Constitution III's *"Metered totals MUST
  reconcile against operational counts to within 0.1%, verified by a daily job that alerts on
  breach"* against SRS FR-ANL-06 as amended at 1.14.
- **The bump**: MINOR. Materially expanded guidance, no principle removed or redefined.
- **The migration impact**: no in-flight spec depends on the flat 0.1%; this feature's own
  measurement is taken against the amended clause either way.
- **What does not change**: the bound itself, for the quantity that can meet it. The amendment
  names the three quantities that cannot meet it and why.
- **AND IT DECOMPOSES THE SENTENCE, BECAUSE TWO OF ITS THREE REQUIREMENTS HAVE NO MECHANISM.**
  *"…within 0.1%, verified by a **daily job** that **alerts on breach**"* is three requirements:

  | part | mechanism | recorded where |
  |---|---|---|
  | the comparison | chapter 4.7's reconciler | this feature's measurement |
  | the **daily job** | **none** — nothing invokes `scripts/reconcile-usage.mjs`, and `ci.yml` has no `schedule:` trigger | **nowhere, until now** |
  | the **alert** | **none** — the job exits non-zero; the two mail paths share a transport defaulting to a local catcher | SRS 1.14 |

  **Only the alert had ever been written down.** `docs/12` §2.3 substituted *"the lane, every
  run"* for *"daily"* without naming the substitution, and a per-push check on a planted fixture
  reads no real tenant. The amendment says which of the three the platform has, and the
  schedule's decision — a sixth background relay, or a recorded absence — comes with it.

**It is the third constitution III item this movement has produced** and the first about the
clause a chapter was written to verify. `gaps.md` 051-2 and 052-6 carry the other two.
