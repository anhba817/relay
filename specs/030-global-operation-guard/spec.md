# Feature Specification: The fault that only shows up in company

**Feature Branch**: `030-global-operation-guard`

**Created**: 2026-08-20

**Status**: Draft

**Input**: User description: "Make the 'local fact about a global operation' test fault fail deterministically in isolation, instead of only when two suites run together."

---

## Context

Six times now, a test in this repository has asserted a local fact about a global
operation. Every one passed when its suite ran alone and failed beside a
neighbour:

| # | Where | Shape | Found by |
|---|---|---|---|
| 1 | `deliveries.itest.ts` | a sweep whose batch limit never reached the test's own endpoint | chapter 3.7 baseline |
| 2 | `deliveries.itest.ts` | a drain holding a lock | chapter 3.7, run 2 of 20 |
| 3 | `consumer.itest.ts` | a consumer draining a growing stream on a fixed budget | chapter 3.7 |
| 4 | `signup.itest.ts` | a global `count(*)` compared against itself | chapter 3.7, runs 3 and 4 |
| 5 | `dispatcher.itest.ts` | a drain at the default batch size of 50 | chapter 3.8 baseline |
| 6 | `notifications.itest.ts` | a global **mutation** that disabled a neighbour's fixture | chapter 3.9 |

There is a seventh, earlier: chapter 3.3 removed exactly the `count(*)` of
instance 4 from invariant 1 of the same file, wrote *"the count was never the
evidence"*, and did not look a hundred lines further down. Four chapters and nine
thousand organisations later the identical sentence failed again.

**The sixth was not inherited.** It was written by someone who had recorded the
other five, cited them in a chapter, and reached for a global function anyway
because it was the most honest-looking way to drive the real product path.

That is the argument for this feature. Three separate rules failed their own
authors during chapter 3.8 — the commit-before-the-battery rule, the
don't-cite-chapter-numbers rule, and this one. Rules that must be remembered are
not a control. The fault recurs because it is **invisible in isolation**: the
feedback only arrives when somebody else's test breaks, by which time it reads as
a flake.

The fix is to make it fail alone.

### Two shapes, two remedies

They look alike and are not:

- **READER** — a test asserts on a global batch or count, and another suite's
  rows fill it. The test is wrong about what it is measuring.
- **WRITER** — a test performs a global mutation and damages a neighbour's
  fixture. The test is wrong about what it is doing.

The reader remedy (require an explicit limit) does nothing for the writer shape.
Instance 6 passed no limit and got 100; passing `10_000` would have been worse,
not better.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reader-shape fault fails on the first run (Priority: P1)

A developer writes an integration test that drains, sweeps or counts, and asserts
on the result. Today it passes on a machine where the database is nearly empty
and fails weeks later in somebody else's pull request. With this story, it fails
the first time they run their own suite, on a freshly migrated database.

**Why this priority**: it covers four of the six recorded instances and needs no
new judgement from the test author.

**Note on build order**: these priorities describe user value. `tasks.md` builds
the guard (US2) *first*, because research found the guard needs the sentinel's
rows rather than the bait's sizes, and that the guard makes the bait durable
rather than the other way round. The MVP in build terms is US2; the MVP in value
terms is this story. Both readings are correct and they disagree — see
`tasks.md`'s Notes.

**Independent Test**: seed the bait, reintroduce instance 5 (`drainOnce()` at the
default batch size) into `dispatcher.itest.ts`, and run that file alone against a
freshly migrated database. It must fail.

**Acceptance Scenarios**:

1. **Given** a freshly migrated database and the bait planted, **When** a
   developer runs one integration file that asserts on a global batch it does not
   bound, **Then** the test fails on that run.
2. **Given** the bait planted, **When** the whole lane runs and every suite is
   correct, **Then** the lane passes and its runtime is not materially longer.
3. **Given** a lane that has already run several times, **When** it runs again,
   **Then** the bait is the same size as on the first run — the seeder does not
   accumulate the condition it exists to simulate.

---

### User Story 2 - A writer-shape fault names itself (Priority: P2)

A developer writes a test that performs a global mutation. Today the damage
surfaces as an unrelated suite failing, and the person who has to diagnose it is
not the person who caused it. With this story, the run that contains the mutation
fails **in that test**, with its own stack, and names the row it took.

**Why this priority**: it covers instance 6 — the one this project caused rather
than inherited — and it is the only remedy that catches a global mutation reached
through raw SQL or an indirect call.

**It does not depend on Story 1**, which an earlier draft of this spec asserted.
The trigger needs the sentinel rows that the foundational phase provides, not the
bait's sizes. That is why it is built first despite being P2.

**Independent Test**: reintroduce instance 6 (`sweepDisabledEndpoints(db)` in
`notifications.itest.ts`) and run that file alone. The run must fail and name the
sentinel row it took.

**Acceptance Scenarios**:

1. **Given** the bait planted, **When** a test mutates bait, **Then** the run
   fails and the message names the table and the row.
2. **Given** any of the **six** suites that perform a global operation on purpose
   (research R5), **When** the lane runs, **Then** it passes, because each carries
   an exemption visible in the file that uses it rather than a silent one.
3. **Given** a test that mutates bait while sixteen other files run in parallel,
   **When** the run reports, **Then** it names **that** test and no bystander —
   on the run that contains the fault, with no second run and no serial mode.
   *An earlier version of this criterion required a "diagnosis mode", which
   belonged to the checksum design and is why FR-008 is marked superseded.*

---

### User Story 3 - The fault is harder to write in the first place (Priority: P3)

A developer reaching for a global function inside a test is made to notice. The
signature will not let them omit the batch size, and importing it into a
`*.itest.ts` fails lint with a message naming the scoped alternative.

**Why this priority**: it stops the fault at the moment the decision is actually
made — the import line — rather than after the fact. It is the cheapest of the
three and the least complete: it catches named imports, not raw SQL.

**Independent Test**: add `import { sweepDisabledEndpoints } from "../db/repository"`
to any `*.itest.ts` not on the exemption list and run lint. It must fail.

**Acceptance Scenarios**:

1. **Given** the restriction in place, **When** a new integration test imports a
   global admin function, **Then** lint fails and the message says which scoped
   function to use instead.
2. **Given** the four batch-taking functions, **When** any caller omits the batch
   size, **Then** the compiler rejects it.
3. **Given** a suite that legitimately drives a global function, **When** lint
   runs, **Then** it passes because the file is named on an exemption list a
   reader can audit.

---

### Edge Cases

- **A refusal raised inside a background relay.** The guard raises in the
  offending statement's own transaction, so a test that performs a global mutation
  fails with its own stack even under parallel file execution — no bystander is
  blamed and no serial mode is needed. A **relay** is different: both
  `delivery-relay.ts` and `notification-relay.ts` catch their own errors and log
  `*_drain_failed`, so a refusal inside one is a log line and a green lane
  (research R13). FR-025 closes it by refusing to start a non-exempt file that has
  a relay enabled.

  *An earlier version of this bullet required a run-scoped check with serial
  attribution. That was the checksum design, withdrawn in the Assumptions section
  below — and left asserted here for five analysis passes.*
- **A legitimate global operation.** **Six** suites drive global drains or sweeps
  deliberately, measured in research R5 rather than guessed: `outbox.itest.ts`,
  `deliveries.itest.ts`, `test-event.itest.ts`, `attempts.itest.ts`,
  `notifications.itest.ts` and `dispatcher.itest.ts`. Each needs an exemption
  visible in the file that uses it, not a blanket disable.
- **Tests that assert on global depth.** `outboxDepth` and `pendingDeliveryDepth`
  return counts across every environment. Any test comparing them to an absolute
  number is a reader-shape fault and will start failing — correctly. Those
  assertions have to become relative to a baseline the test takes itself.
- **The bait gets consumed by a suite allowed to.** A non-exempt statement never
  completes, so it cannot eat bait — that is the trigger preventing rather than
  detecting, and it is why FR-011's "re-plant after the verdict" is marked
  superseded. The six **exempt** suites can and do consume it: research R2
  measured three of the four baits gone after one lane pass. Per-file planting is
  what restores it, so every file starts with its own bait present regardless of
  what ran before.
- **A developer runs one test by name.** The bait must be planted for a filtered
  run too, or the guarantee holds only for whole-file runs.
- **A fresh clone.** The bait must be planted by the lane itself, not by a
  developer remembering to run a script.

---

## Requirements *(mandatory)*

### Functional Requirements

**The bait**

- **FR-001**: The integration lane MUST plant bait — rows belonging to a sentinel
   environment that every global operation in the codebase would act on — before
   any test in a file runs.
- **FR-002**: The bait MUST include at minimum: a webhook endpoint with an open
   failure run older than the disablement cutoff; enough due deliveries to exceed
   the largest default batch size in the codebase; enough unpublished outbox rows
   to do the same; and undelivered disablement notifications.
- **FR-003**: Planting MUST be idempotent — a second lane run against the same
   database leaves the bait the same size, not twice the size.
- **FR-004**: Planting MUST happen automatically as part of running the lane, on
  a freshly migrated database, with no separate command to remember.
- **FR-005**: The sentinel environment MUST be identifiable by name, so a
  developer reading a failure knows the rows are not theirs.

**The guard**

- **FR-006**: The lane MUST fail when bait is modified during a run, whichever
  file's sentinel owns it.
- **FR-007**: The failure message MUST name the table and the row that changed.
- **FR-008** *(superseded by research R6)*: the refusal MUST identify the
  offending test with no separate diagnosis mode and no serial run. The trigger
  raises inside the statement's own transaction, so attribution is a property
  rather than a mode. The original wording — "a diagnosis mode MUST attribute the
  mutation to a specific test" — belonged to the checksum design.
- **FR-009**: Suites that perform global operations deliberately MUST be able to
  exempt themselves, and each exemption MUST be visible in the file that uses it
  and carry the reason.
- **FR-010**: The guard MUST NOT report a mutation that did not happen. A clean
  lane run reports nothing.
- **FR-011** *(superseded by research R6)*: the guard MUST **prevent** the
  mutation rather than detect it afterwards. Nothing is re-planted after a verdict
  because a non-exempt statement never completes. The original wording assumed a
  check that ran after the damage.

**The call site**

- **FR-012**: Every function that returns or mutates **rows** across
  environments MUST require an explicit batch size. `sweepDisabledEndpoints` is
  the last one carrying a default and MUST lose it.
- **FR-012a**: `outboxDepth` and `pendingDeliveryDepth` return a **count** across
  every environment and take no batch size, because a count has nothing to bound.
  They are therefore restricted from tests by FR-013 rather than fixed by FR-012 —
  a global `count(*)` compared against itself is instance 4, twice in one file,
  four chapters apart.
- **FR-012b**: `expandEventToDeliveries` and `replayDeadLetter` cross environments
  but take an id, so they are bounded by construction and need neither a batch size
  nor a restriction. Recorded so the count of cross-environment functions adds up:
  **four** take a batch, two return a count, two take an id.
- **FR-013**: Importing a global admin function into a `*.itest.ts` MUST fail
  lint, unless the file appears on an exemption list.
- **FR-014**: The lint message MUST name the scoped alternative rather than only
  refusing.
- **FR-015**: The exemption list MUST be a list of paths a reader can audit, not
  a pattern that silently absorbs new files.

**What the harness makes true, rather than the design**

- **FR-020**: The exemption MUST hold for **every** connection a pool opens.
  Issuing it as a statement through a pool sets it on whichever connection the
  pool happens to hand out — measured at two of five (research R10).
- **FR-021**: Every lane that touches the database MUST be able to answer the
  trigger. The trigger belongs to the database and outlives any one lane; five
  configs share that database and only two were given a hook (research R11).
- **FR-022**: Bait MUST be planted only in the lanes where reader-shape faults
  live. Planting it elsewhere changes a suite's workload for no return, which is
  the fault research R4 measured.
- **FR-023**: Each test file MUST have its **own** sentinel. Files execute in
  parallel, so a shared sentinel means one file's planting deletes rows another
  file is mid-test against (research R12).
- **FR-024**: Planting MUST use a connection that never enters the suite's pool.
  The seeder needs the exemption to plant; a test that inherited that connection
  would be unguarded (research R12).
- **FR-026**: The exemption MUST be applied before a suite's first line of module
  scope runs. A setup file's top-level code runs before the test file is imported;
  a hook does not, and four suites create their database pool at module scope.
- **FR-025**: A **non-exempt** file MUST fail at startup if it has a relay
  enabled. A relay catches and logs its own errors, so a refusal raised inside one
  is a log line and a green lane (research R13).

**Fixing what this exposes**

- **FR-016**: Every existing test the bait breaks MUST be fixed so it asserts on
  its own rows rather than on a global result, and each fix MUST record which of
  the two shapes it was.
- **FR-017**: The six recorded instances MUST each be reintroduced once,
  confirmed to fail, and reverted with the file verified byte-identical.

**Where this lands**

- **FR-018**: This work publishes no chapter, so its fences MUST go to
  `relay-tutorial/fences/post-series.md`.
- **FR-019**: `docs/07-tutorial-plan.md` MUST record the work, the class of fault
  it addresses, and that it teaches no chapter.

### Key Entities

- **Sentinel environment**: **one per test file**, derived from that file's path so
  it is stable across runs and unique across files. Its rows exist only to be
  taken. Owned by the lane, never by a test. *An earlier version of this entry
  said "one named environment", which FR-023 has contradicted since the third
  analysis pass.*
- **Sentinel registry**: the table the trigger tests membership in, holding one
  row per test file with the owning file's path. With one shared sentinel the
  trigger could compare against a literal id; with one per file it cannot.
- **Bait**: the planted rows — an endpoint eligible for disablement, due
  deliveries, unpublished outbox rows, undelivered notifications. Sized from the
  exported batch constants so a raised default raises the bait with it, and chosen
  so that every global operation in the codebase touches at least one of them.
- **Refusal**: the error the trigger raises in the offending statement's own
  transaction, naming the table and the row. *This replaces a **Verdict** entity —
  whether the sentinel changed during a run — which belonged to the checksum
  design and has no counterpart now that the guard prevents rather than detects.*
- **Exemption**: a connection option carried by every connection a pool opens, set
  only for files on an auditable list, with the reason recorded beside the path.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All six recorded instances, reintroduced one at a time, fail with
  **no second suite present** and on a freshly migrated database. Today all six
  pass under those conditions.
- **SC-002**: The interval between writing a global-operation fault and being
  told about it drops from *a later run of a different suite* to *the same run*.
  Measured by SC-001's six reintroductions: today zero of six report on the run
  that contains them; the target is six of six.
- **SC-003**: Twenty consecutive lane runs produce zero false positives.
- **SC-004**: The integration lane's wall-clock time grows by less than 10 seconds
  against **a baseline measured on this feature's own first task**, not against a
  literal. The only figure chapter 3.9 recorded is `3m15s` at **213** integration
  tests; the chapter finished on 223 and that run was never timed, so comparing a
  future 223-plus lane against it would spend part of the budget on ten tests that
  already existed.
- **SC-005**: Every suite that performs a global operation on purpose still
  passes, and each exemption is discoverable by reading the file that uses it.
- **SC-006**: All **four** batch-taking functions require a batch size and none
  carries a default. The other four cross-environment functions are accounted for
  rather than changed: two return a global count and have nothing to bound, and two
  are already bounded by an id argument.
- **SC-007**: Adding a global admin import to a new integration test fails lint,
  and the message tells the author what to use instead.
- **SC-008** *(lagging — verifiable only after the next chapter ships)*: the
  count of recorded instances does not increase. Recorded here because it is the
  outcome that matters and the only one this feature cannot demonstrate at
  delivery.

---

## Assumptions

- **The shared database stays.** Chapter 2.1 chose one database with per-suite
  environments deliberately, and all six findings are real production-shaped
  problems that per-suite isolation would hide rather than fix. Per-suite
  databases are explicitly out of scope.
- **~~The guard's always-on check is run-scoped.~~** *Withdrawn.* This assumption
  said attribution needed serial file execution. Research R6 replaced the checksum
  with a trigger, which raises inside the offending transaction and therefore
  attributes under parallelism with no serial mode. The assumption was correct
  about the mechanism it was written for and is now about nothing.

  What replaced it is narrower and measured: attribution holds for a **statement
  in a test**. A refusal raised inside a background relay is caught and logged by
  that relay, so it is a log line rather than a failure (research R13). FR-025
  closes that by refusing to start a non-exempt file with a relay enabled.
- **This teaches no chapter.** It is test infrastructure, and the series' rule is
  that a chapter may only fence a change it discusses. If a later chapter wants
  the story, the material is in `research.md` and the six post-series entries.
- **The bait's size tracks the largest default batch in the codebase.** If a
  future default exceeds it, the bait stops working silently — so the sizes are
  derived from the constants rather than written as literals.
- **Existing suites will break when the bait lands.** That is the feature
  working. The count of suites that break is a finding to record, not a problem
  to route around. Measured once already: two of 177 on a fresh database with a
  one-shot seeder (research R3).
- **The trigger outlives the lane that installed it.** It is database state, so
  the first lane to run leaves it behind for every other lane pointed at that
  database — including a developer's next `pnpm coverage`. Uniform exemption
  handling across all five configs is what makes that safe rather than surprising
  (FR-021, research R11).
