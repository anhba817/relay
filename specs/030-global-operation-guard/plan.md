# Implementation Plan: The fault that only shows up in company

**Branch**: `030-global-operation-guard` | **Date**: 2026-08-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/030-global-operation-guard/spec.md`

## Summary

Seven times a test has asserted a local fact about a global operation, and every
one passed alone. Make the fault fail in isolation, with three defences at three
distances from the mistake: a **database trigger** that raises inside the
transaction that damaged rows belonging to no test, **planted bait** that makes a
fresh database behave like an aged one, and a **lint restriction plus required
batch sizes** at the import line where the decision is actually made.

Research changed the central mechanism. The spec assumed a before/after checksum
of sentinel rows and conceded that attribution would need serial test execution.
Measurement showed that concession is fatal rather than awkward — legitimate
global sweeps happen on every lane run, so a checksum either fires constantly or
blames bystanders. A trigger raises in the offending session instead, which
attributes exactly, under parallelism, and also catches raw SQL that no lint rule
or wrapped import can see (research R6).

## Technical Context

**Language/Version**: TypeScript on Node.js, as constitution VII requires. The
guard's logic is PL/pgSQL because it has to run inside the offending transaction.

**Primary Dependencies**: vitest (`setupFiles` and `globalSetup`, in **five**
configs — api, dispatcher, gateway, e2e and coverage), `pg` for the setup file's
DDL and its dedicated seeding client, eslint's `no-restricted-imports`. Nothing
new is added to any package manifest.

**How the exemption travels**: as a connection option in `DATABASE_URL`, rewritten
by the setup file for its own worker. Not as a `SET` statement — a pool rotates
connections and a statement lands on one of them, measured at two of five
(research R10). This needs no change to `createPool()`.

**Storage**: the compose PostgreSQL the integration lane already uses. The trigger
and the sentinel rows exist only in test databases and are created by the lane,
never by a product migration.

**Testing**: the api and dispatcher integration lanes. This feature's own
verification is the seven recorded instances, reintroduced one at a time and
required to fail.

**Target Platform**: developer machines and CI, on Linux.

**Project Type**: test infrastructure for an existing monorepo. It publishes no
chapter.

**Performance Goals**: the integration lane grows by less than 10 seconds against a
baseline T002 measures. Chapter 3.9's recorded `3m15s` is indicative only — it was
taken at 213 integration tests and the chapter finished on 223. Per-file planting
costs roughly 600 inserts.

**Constraints**: the shared database stays (chapter 2.1's decision). No product
code may carry test logic. Fences go to `post-series.md`.

**Scale/Scope**: 16 api integration files plus the dispatcher's, of which six
legitimately drive global operations and need exemptions (research R5). Five vitest
configs share the database; the trigger is database state and outlives any one of
them, so all five carry exemption handling and only two carry bait (research R11).

## Constitution Check

*GATE: must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Verdict | Reasoning |
|---|---|---|
| **I — Tenant isolation** | **Reinforced** | The fault this feature attacks is a test reaching across the `environment_id` boundary. The trigger enforces at the database exactly what principle I says belongs in data access rather than in handlers. |
| **II — No acknowledged message lost** | Not engaged | No change to the write path, ordering, idempotency or the outbox. |
| **III — Two data paths** | Not engaged | Nothing analytical. |
| **IV — Single writer** | **Respected, with care** | The trigger is not a second writer; it refuses writes. It must exist only in test databases, or the api service would ship a trigger that rejects its own legitimate sweeps. Enforced by creating it from the lane's setup, not from `migrations/`. |
| **V — API-first** | Not engaged | No public surface changes. |
| **VI — Test-verified delivery** | **This is the principle** | Constitution VI requires 100% branch coverage of tenant isolation and a cross-tenant suite that gates the build. A suite whose tests silently depend on being alone is not the verification it claims to be. |
| **VII — Boring by design** | **Asked and closed — not a violation** | The guard's logic is PL/pgSQL. VII's one-language rule reads *"One language (TypeScript/Node.js) across services, SDK, and dashboard"* — service implementation languages — and this is neither a service nor shipped. See "Two questions the gate asked" below. |

**Gate result: PASS**, with no violations. Two decisions were examined against principles VII and IV and both are compliant; the reasoning is kept because the questions are worth asking, not because the answers were close.

## Project Structure

### Documentation (this feature)

```text
specs/030-global-operation-guard/
├── plan.md              # This file
├── spec.md
├── research.md          # Phase 0 — R1..R9, two of which changed the design
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   └── guard.md         # Phase 1 — what fires, what it says, how to be exempt
└── tasks.md             # Phase 2 (/speckit-tasks)
```

### Source code

```text
relay-platform/
├── packages/test-harness/                     # NEW — shared, because five configs use it
│   ├── package.json                           # declares its own `pg`
│   └── src/
│       ├── sentinel.ts                        # the bait: what it is, how it is planted
│       ├── sentinel.sql                       # the trigger and its exemption function
│       ├── global-setup.ts                    # creates the trigger once per lane
│       ├── setup.ts                            # sets exemption at module scope; plants in beforeAll
│       └── exempt.ts                            # the auditable list of exempt files
├── services/api/
│   └── vitest.integration.config.mts          # gains globalSetup + setupFiles
├── services/api/src/db/repository.ts          # sweepDisabledEndpoints loses its default
├── services/dispatcher/
│   └── vitest.integration.config.mts          # same two hooks
├── services/gateway/
│   └── vitest.integration.config.mts          # exemption handling only, no bait
├── packages/e2e/
│   └── vitest.integration.config.mts          # exemption handling only, no bait
├── vitest.coverage.config.mts                 # exemption handling + the harness exclusion
└── eslint.config.mjs                          # the global-admin import restriction

relay-tutorial/
└── fences/post-series.md                      # every fence this feature produces
```

**Structure Decision**: a new **package**, `packages/test-harness/`, not a
directory inside a service.

The first draft put it in `services/api/src/testing/`. Once the exemption had to
reach every lane, five configs across four packages import it — and a gateway test
lane reaching into another service's `src/` is a worse precedent than a shared
package, even in test code. `packages/` is where this repository already keeps
shared things: `config`, `protocol`, `service-kit`, `e2e`.

It declares its own `pg`, which only `services/api` does today. That is what a
package is for. And it plants through raw SQL rather than the api's repository, so
it imports nothing from any service — the schema knowledge it carries, which tables
hold `environment_id`, is written down in `data-model.md` either way.

Excluded from coverage for the same reason `main.ts` and `*.module.ts` are:
counting how much of the lane's own scaffolding a test touched is not what
"business logic" means.

**Five configs, not two.** The first draft of this tree named the api's and the
dispatcher's. The trigger is database state: whichever lane installs it leaves it
for every other lane pointed at that database, and three more share it. The
coverage lane is the sharp one — it runs every `*.itest.ts` in one process with no
hooks at all, so it would have met the trigger and failed all six exempt suites
(research R11). The gateway and e2e lanes get exemption handling and no bait,
because bait changes a suite's workload and neither of them holds a reader-shape
fault.

## Phasing

The three defences are independent and land in order of how much they catch.

**Phase A — the trigger (spec US2).** Highest value: it catches the writer shape,
attributes exactly, and needs no bait. Verified by reintroducing instance 6. Its
three hard parts are all harness mechanics rather than SQL: the exemption must ride
every pooled connection (R10), every lane must be able to answer it (R11), and the
seeder must be able to plant without handing its exemption to a test (R12).

**Phase B — the bait (spec US1).** Makes a fresh database adversarial for the
reader shape. Depends on nothing in Phase A, but is cheaper to keep durable once
the trigger exists (research R2, R6). Verified by reintroducing instances 1–5.

**Phase C — the call site (spec US3).** The required limit and the lint rule.
Cheapest, least complete, and the only one that acts before the code runs.

**Phase D — fix what this exposes.** Two tests broke under measurement
(research R3) and more will break once planting is per-file. Each fix records
which of the two shapes it was.

**Phase E — the plumbing.** Fences to `post-series.md`, the plan document already
records the work, and the seven reintroductions run as a battery with each file
verified byte-identical afterwards.

## Complexity Tracking

> Fill ONLY if the Constitution Check has violations that must be justified.

**None.** Two decisions looked like violations at gate time and neither is; the
reasoning is below rather than deleted, because the questions are worth a reader's
time even though the answers are no.

## Two questions the gate asked

### Is PL/pgSQL a second language under principle VII?

**No**, and an earlier draft of this plan said yes for four analysis passes without
re-deriving it.

VII's clause is *"One language (TypeScript/Node.js) across services, SDK, and
dashboard; shared protocol types between server and SDK eliminate drift bugs
(ADR-01). Introducing a second language requires a superseding ADR with profiling
evidence."* The subject is the language services are **implemented** in — the thing
that creates drift between server and SDK. The guard is neither a service nor
shipped: it exists in test databases, created by the lane.

The repository already holds **nine `.sql` files**, and the constitution endorses
them in its own words: migrations are *"versioned, forward-only, hand-reviewed
SQL"*. SQL is not a second language here; it is the language the database speaks and
has spoken since chapter 2.1.

**The honest distinction, and why the question came up at all**: those nine files
are *declarative* SQL and this one is *procedural*. A `RAISE EXCEPTION` inside a
`plpgsql` function is closer to program logic than an `ALTER TABLE` is. That is a
real difference and it is why the gate stopped here. It is not the difference VII
legislates.

**What the earlier draft got wrong is instructive.** It wrote "Violated, justified"
in Complexity Tracking and then declined to write the ADR — and VII's escape clause
*is* the ADR, not a justification table. Four passes re-affirmed "one violation,
justified" without noticing that the remedy on offer had been refused. A
constitutional judgement inherited is a constitutional judgement unmade.

So there is no ADR, because there is nothing for an ADR to supersede. The reasoning
is still written down, at **T005e** and **T005f**: in
`docs/07-tutorial-plan.md`'s "Work that publishes no chapter" section, and in the
header of `sentinel.sql` where a reader meets the procedural SQL. Research R6 and
R10 hold the measurements — that the TypeScript alternative cannot attribute at all,
and that the naive SQL one is non-deterministic.

**Where the note goes was also asserted without checking.** An earlier draft said
`docs/06-adr-deep-dives.md`. That document is eighteen sections, every one
`## ADR-nn — …` on a fixed six-part shape, companion to `docs/05-sad.md` §9 where
`ADR-01`…`ADR-18` live, closing with a heading that counts them: "Reading the
eighteen together". It has no room for a note that is not an ADR.

### Is a trigger a second writer under principle IV?

**No.** It refuses writes rather than making them, and it exists only in test
databases. The mitigation is structural rather than promised: it is created by the
lane's setup, never by `services/api/migrations/`, so no product migration can
carry it into production. T013b asserts that.

Why the guard has to be in the database at all: nothing else observes a raw
`UPDATE`. A checksum in TypeScript cannot attribute under parallel file execution
(R5, R6), wrapping the repository's exports misses raw SQL, and putting the check
in product code would break the stronger rule that shipped code carries no test
logic.

## Constitution Re-check (post-design)

Re-evaluated against the finished design rather than the intended one.

| Principle | Verdict after Phase 1 | What changed |
|---|---|---|
| **I — Tenant isolation** | **Reinforced, more than expected** | The trigger enforces the `environment_id` boundary *at the database*, which is where principle I says isolation belongs. It is closer to that principle than the checksum would have been. |
| **IV — Single writer** | **Held, and the mitigation is now structural** | `data-model.md` places the trigger's creation in the lane's setup and names the guarded tables. No product migration can carry it to production, so the api service remains the only writer and gains no shipped trigger. |
| **VI — Test-verified delivery** | **Held** | The seven reintroductions in `quickstart.md` V3 and V4 are the verification, and each is required to fail *alone*. |
| **VII — Boring by design** | **Not a violation, and the claim that it was is itself the finding** | Roughly twenty lines of PL/pgSQL in one file, created by test infrastructure, touching no shipped path. VII legislates the language services are implemented in; nine `.sql` files already exist with the constitution's endorsement. The gate's first four passes recorded "violated, justified" and declined the ADR the clause requires — see "Two questions the gate asked". |

**Result: PASS.** One violation, unchanged in kind and reduced in size.

Three things recorded because a plan that only reports improvements is not worth
reading — the first being that this table said "violated" for four passes:

- **The outbox has no `environment_id`**, so its bait is protected by the reader
  mechanism only and the trigger cannot guard it. Platform bookkeeping is
  genuinely tenant-less, so this is a real gap rather than a modelling mistake.
  Named in `data-model.md`.
- **Exemption is coarse.** An exempt file is exempt for its whole run, so a
  reader-shape fault inside one of the six exempt suites is still invisible to the
  trigger — and four of the seven recorded instances were in files that would now
  be exempt. Those are caught by the bait instead, which is why Phase B is not
  optional and why the composition table in `contracts/guard.md` exists.
