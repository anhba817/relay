# Feature Specification: Coverage measurement and CI

**Feature Branch**: `024-coverage-and-ci`

**Created**: 2026-08-08

**Status**: Draft

**Input**: "Let implement the deferred small feature" — the coverage-and-CI work deferred by chapters 3.1, 3.2 and 3.3 and recorded in `docs/07-tutorial-plan.md` §6.

## Why this exists

Constitution Principle VI carries two clauses the project has never been able to
check:

> Automated test coverage of business logic MUST be at least 70%. Message
> ordering, idempotency, and tenant isolation MUST have 100% branch coverage
> (NFR-MNT-02).

> The quickstart MUST run unmodified, verified by automated execution in CI
> against the published documentation.

Neither is measurable today: the workspace has no coverage tooling and none of
the three repositories has CI. Chapter 3.1 deferred the measurement, 3.2
deferred it by explicit decision recording that the remedy would run before 3.3,
and 3.3 deferred it a third time with the owner's agreement. This feature is
that remedy.

**It is not a tutorial chapter.** It publishes no page and teaches nothing; it
adds the instrument. That distinction drives the fence question below.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The bar becomes measurable (Priority: P1)

A maintainer runs one command and learns the real coverage numbers for business
logic, and specifically for the ordering, idempotency and isolation code
NFR-MNT-02 names.

**Independent Test**: `pnpm coverage` in `relay-platform/` produces a report
including branch coverage per file, and fails when a configured threshold is
breached.

**Acceptance Scenarios**:

1. **Given** the workspace, **When** coverage runs, **Then** it reports line and
   branch coverage across both test lanes, because the isolation code is
   exercised by integration tests and a unit-only figure would be a misleading
   number rather than a missing one.
2. **Given** a threshold breach, **When** coverage runs, **Then** the command
   exits non-zero.
3. **Given** the report, **When** a maintainer reads it, **Then** the actual
   figures for the NFR-MNT-02 files are recorded in this feature's notes —
   whatever they are.

### User Story 2 - The gates run without a human (Priority: P2)

Every push runs the checks that have so far been run by hand.

**Independent Test**: a workflow file exists that runs the Docker-free gate, the
integration lane against real stores, the site build, and the fence and
docs-drift checks — and the workflow's own commands match what a maintainer runs
locally.

**Acceptance Scenarios**:

1. **Given** the parent repository with submodules, **When** CI runs, **Then**
   `lint`, `typecheck`, `test`, `test:integration`, `check:docs` and
   `check:fences` all execute.
2. **Given** the integration lane, **When** CI runs it, **Then** Postgres, Redis
   and NATS are available to it as services.
3. **Given** a failing check, **When** CI runs, **Then** the run fails.

### User Story 3 - The chain stays honest (Priority: P3)

Adding tooling changes a file that published chapters fence, and no chapter
teaches this change.

**Independent Test**: `pnpm check:fences` passes, no published chapter gains a
fence for code it does not discuss, and the amendment is visible in one place
with its reason.

**Acceptance Scenarios**:

1. **Given** the fence chain, **When** it replays, **Then** the end state still
   equals the repository byte-for-byte.
2. **Given** a reader of chapter 2.8, **When** they read its fenced
   `package.json`, **Then** they see the file as that chapter left it, without a
   dependency the chapter never mentions.

### Edge Cases

- **Coverage needs the stores.** The isolation code lives behind integration
  tests; a coverage run that silently skips them would report a comfortable and
  meaningless number.
- **The 100% clause may not be met today.** The instrument's job is to say so,
  not to be tuned until it agrees.
- **CI cannot be verified from here.** No runner executes in this environment;
  the workflow's correctness is argued from its commands matching the local ones,
  and that limitation must be stated rather than implied away.

## Requirements *(mandatory)*

- **FR-001**: A single command MUST produce coverage across both test lanes.
- **FR-002**: Coverage MUST report per-file branch figures for the files
  implementing message ordering, idempotency and tenant isolation.
- **FR-003**: A global line-coverage threshold of 70% MUST be enforced, failing
  the command when breached (constitution VI).
- **FR-004**: The measured figures for the NFR-MNT-02 files MUST be recorded in
  this feature's notes, unmodified, whatever they show.
- **FR-005**: A CI workflow MUST run the Docker-free gate, the integration lane
  with real stores, the site build, and the fence and docs-drift checks.
- **FR-006**: CI commands MUST be the same commands a maintainer runs locally,
  so that a green CI run means what a green local run means.
- **FR-007**: Adding the tooling MUST NOT put a fence into any published chapter
  for code that chapter does not teach.
- **FR-008**: The fence chain MUST still replay onto the repository byte-for-byte.
- **FR-009**: Every existing suite MUST keep passing, unchanged.
- **FR-010**: What this feature does NOT deliver MUST be named, with an owner.

## Success Criteria *(mandatory)*

- **SC-001**: `pnpm coverage` runs and reports both lanes, verified by running it.
- **SC-002**: A deliberately lowered threshold makes the command exit non-zero,
  verified by running it.
- **SC-003**: The real coverage numbers are recorded, including any gap against
  the 100% branch clause.
- **SC-004**: `pnpm check:fences` passes and no chapter's fenced content gains an
  untaught line.
- **SC-005**: Both lanes still pass at their chapter-3.3 counts (120 unit, 87
  integration).
- **SC-006**: The CI workflow is syntactically valid and its steps mirror the
  local commands, verified by parsing it and by comparison.

## Assumptions

- **CI is written but not executed here.** No GitHub Actions runner exists in
  this environment. The workflow is verified by parsing and by command-for-command
  comparison with the local gates; its first real execution is the first push.
- **The quickstart-in-CI clause is partially served.** Every chapter quickstart
  begins with the same two lanes, and CI runs those. Running each chapter's
  remaining V-steps needs the chapter tags, which do not exist yet, so that
  clause stays partially unmet and is recorded as such.
- **Thresholds are set to what the constitution states**, not to what the code
  currently achieves.

## Out of Scope

- Writing new tests to reach any threshold. This feature installs the
  instrument; using it is the next chapter's work.
- Publishing a tutorial chapter about CI (Part 6 owns that).
- Cutting the chapter tags.
