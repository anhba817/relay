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

**Why this priority**: it covers four of the six recorded instances, it needs no
new judgement from the test author, and it is the foundation the second story
watches — the planted rows are what a global operation takes.

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
reports it, and a diagnosis mode names the test.

**Why this priority**: it covers instance 6 — the one this project caused rather
than inherited — and it is the only remedy that catches a global mutation reached
through raw SQL or an indirect call. It depends on Story 1's bait existing.

**Independent Test**: reintroduce instance 6 (`sweepDisabledEndpoints(db)` in
`notifications.itest.ts`) and run that file alone. The run must fail and report
that the sentinel environment was mutated.

**Acceptance Scenarios**:

1. **Given** the bait planted, **When** a test mutates rows belonging to the
   sentinel environment, **Then** the run fails and the message names the table
   and the row.
2. **Given** a suite that performs a global operation on purpose — the outbox and
   delivery relays — **When** the lane runs, **Then** it passes, because that
   suite carries an explicit and visible exemption rather than a silent one.
3. **Given** a lane run where something took the bait, **When** the developer
   re-runs in diagnosis mode, **Then** the offending test is named.

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
2. **Given** the five global functions, **When** any caller omits the batch size,
   **Then** the compiler rejects it.
3. **Given** a suite that legitimately drives a global function, **When** lint
   runs, **Then** it passes because the file is named on an exemption list a
   reader can audit.

---

### Edge Cases

- **A test blames itself for somebody else's mutation.** Integration files run in
  parallel, so a before/after comparison inside one test can observe a global
  mutation performed by another file. The always-on check must therefore be
  scoped to the run rather than to the test, with per-test attribution available
  in a mode where file execution is serial.
- **A legitimate global operation.** The outbox relay, the delivery relay and the
  notification relay suites all drive global drains deliberately. Each needs an
  exemption that is visible at the call site, not a blanket disable.
- **Tests that assert on global depth.** `outboxDepth` and `pendingDeliveryDepth`
  return counts across every environment. Any test comparing them to an absolute
  number is a reader-shape fault and will start failing — correctly. Those
  assertions have to become relative to a baseline the test takes itself.
- **The bait gets consumed.** A global operation that takes the bait leaves the
  sentinel in a changed state for every test after it. Re-planting must happen
  after the verdict, never before it.
- **A developer runs one test by name.** The bait must be planted for a filtered
  run too, or the guarantee holds only for whole-file runs.
- **A fresh clone.** The bait must be planted by the lane itself, not by a
  developer remembering to run a script.

---

## Requirements *(mandatory)*

### Functional Requirements

**The bait**

- **FR-001**: The integration lane MUST plant, before any test runs, a set of
  rows belonging to one sentinel environment that every global operation in the
  codebase would act on.
- **FR-002**: The planted rows MUST include at minimum: a webhook endpoint with
  an open failure run older than the disablement cutoff; enough due deliveries to
  exceed the largest default batch size in the codebase; enough unpublished
  outbox rows to do the same; and undelivered disablement notifications.
- **FR-003**: Planting MUST be idempotent — a second lane run against the same
  database leaves the bait the same size, not twice the size.
- **FR-004**: Planting MUST happen automatically as part of running the lane, on
  a freshly migrated database, with no separate command to remember.
- **FR-005**: The sentinel environment MUST be identifiable by name, so a
  developer reading a failure knows the rows are not theirs.

**The guard**

- **FR-006**: The lane MUST fail when the sentinel environment's rows are
  modified during a run.
- **FR-007**: The failure message MUST name the table and the row that changed.
- **FR-008**: A diagnosis mode MUST attribute the mutation to a specific test.
- **FR-009**: Suites that perform global operations deliberately MUST be able to
  exempt themselves, and each exemption MUST be visible in the file that uses it
  and carry the reason.
- **FR-010**: The guard MUST NOT report a mutation that did not happen. A clean
  lane run reports nothing.
- **FR-011**: Re-planting after a taken bait MUST occur after the verdict is
  recorded.

**The call site**

- **FR-012**: Every function that reads or writes across environments MUST
  require an explicit batch size. `sweepDisabledEndpoints` is the last one
  carrying a default and MUST lose it.
- **FR-013**: Importing a global admin function into a `*.itest.ts` MUST fail
  lint, unless the file appears on an exemption list.
- **FR-014**: The lint message MUST name the scoped alternative rather than only
  refusing.
- **FR-015**: The exemption list MUST be a list of paths a reader can audit, not
  a pattern that silently absorbs new files.

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

- **Sentinel environment**: one named environment whose rows exist only to be
  taken. Owned by the lane, never by a test.
- **Bait**: the planted rows — an endpoint eligible for disablement, due
  deliveries, unpublished outbox rows, undelivered notifications. Chosen so that
  every global operation in the codebase touches at least one of them.
- **Verdict**: whether the sentinel changed during a run, and if so, which table
  and row.
- **Exemption**: a named file permitted to perform global operations, with the
  reason recorded beside the name.

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
- **SC-004**: The integration lane's wall-clock time grows by less than 10
  seconds against the chapter 3.9 baseline of 3m15s.
- **SC-005**: Every suite that performs a global operation on purpose still
  passes, and each exemption is discoverable by reading the file that uses it.
- **SC-006**: All five cross-environment functions require a batch size; none
  carries a default.
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
- **The guard's always-on check is run-scoped.** Attributing a mutation to a
  specific test requires serial file execution, which the coverage lane already
  configures. The always-on check therefore reports that the lane took the bait;
  naming the test is a second, deliberate run. This is a consequence of the
  parallelism the lane already has, not a limitation being introduced.
- **This teaches no chapter.** It is test infrastructure, and the series' rule is
  that a chapter may only fence a change it discusses. If a later chapter wants
  the story, the material is in `research.md` and the six post-series entries.
- **The bait's size tracks the largest default batch in the codebase.** If a
  future default exceeds it, the bait stops working silently — so the sizes are
  derived from the constants rather than written as literals.
- **Existing suites will break when the bait lands.** That is the feature
  working. The count of suites that break is a finding to record, not a problem
  to route around.
