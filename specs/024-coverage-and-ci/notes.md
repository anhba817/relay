# Feature 024 — implementation notes

**Date**: 2026-08-08
**Publishes**: no chapter. This feature installs an instrument.

---

## The numbers, for the first time

Measured over both lanes (199 tests: the 120 unit and the 79 integration tests
outside the e2e journey), `pnpm coverage` in `relay-platform/`:

| Metric | Result | Constitution VI |
|---|---|---|
| Statements | **86.55%** (702/811) | ≥70% ✅ |
| Lines | **87.83%** (657/748) | ≥70% ✅ |
| Functions | **88.77%** (174/196) | ≥70% ✅ |
| Branches | **78.07%** (324/415) | ≥70% ✅ |

The first clause of Principle VI is **met, with room to spare**, and this is the
first time anyone could say that with a number attached.

## The clause that is not met

> Message ordering, idempotency, and tenant isolation MUST have 100% branch
> coverage (NFR-MNT-02).

| File | Branch coverage | What lives there |
|---|---|---|
| `services/api/src/db/repository.ts` | **85.91%** (61/71) | all three: sequence assignment, the idempotency conflict path, every tenant-scoped query |
| `services/gateway/src/resume.ts` | 93.75% (15/16) | resume cursors and flush ordering |
| `services/api/src/auth/user-token.ts` | 96% (24/25) | the credential that resolves a tenant |
| `services/api/src/auth/api-key.ts` | 75% (3/4) | the credential that resolves a tenant |
| `services/api/src/messages/messages.service.ts` | 57.69% (15/26) | the write path's error shaping |
| `services/api/src/outbox/relay.ts` | 66.66% (4/6) | not named by NFR-MNT-02; recorded for context |

**The bar is 100%. The file that matters most is at 85.91%.** That is a real,
recorded gap in a constitutional MUST, and it is now a number rather than an
unanswerable question.

### Why the thresholds are pinned below the bar

The config enforces the measured values as a **ratchet**, not the constitutional
100%. Two bad alternatives were rejected:

- Threshold at 100 → CI is red on its first run and stays red until someone does
  unrelated work. A check that is always failing teaches people to ignore checks.
- Threshold at 85 with the requirement marked satisfied → a lie, and exactly the
  "dilution" the constitution forbids.

The ratchet stops the number sliding backwards while the gap is closed, and the
gap is written into the config, into this file, and into `docs/07` §6.

**Owner for closing it**: whichever chapter next touches the repository layer.
The uncovered branches are concentrated in error paths and in the idempotency
conflict clause — precisely the branches a durability argument leans on.

## The fence problem, and the mechanism it produced

Adding a devDependency was not possible without breaking the fence chain: every
manifest in the workspace is fenced by some chapter, and the workspace root's
last fence is chapter 2.8. The options were:

1. Amend chapter 2.8's fenced `package.json` — a chapter about the Tuan test
   would then show a reader a coverage provider it never mentions, in both
   locales.
2. Give the chain a home for amendments no chapter teaches.

Built option 2: `relay-tutorial/fences/post-series.md`. Diffs only, applied after
the last chapter, checked exactly as strictly. Verified by sabotage — adding an
undeclared dependency to the manifest fails the chain with a HEAD error, so the
mechanism records rather than excuses.

This is the third mechanism the fence checker has grown from a real need: hunked
diffs (2.7), deletions (3.2), post-series amendments (here). Each arrived
because the alternative was to let a chapter lie.

## CI

`.github/workflows/ci.yml` in the **parent** repository, because that is the only
place all three trees exist at once — the fence check replays chapters onto
`relay-platform`, and neither submodule can verify it alone.

- **platform job**: `pnpm lint`, `typecheck`, `test`, `build`, migrations,
  `test:integration`, `coverage` — with Postgres, Redis and NATS as services on
  the same images `compose.yaml` uses.
- **tutorial job**: `pnpm lint`, `build`, `check:docs`, `check:fences`.

Every command is one a maintainer runs locally, verbatim.

**Not verified by execution.** No runner exists in this environment. The workflow
parses, its two jobs contain 13 run-steps, and each matches a local command. Its
first real run is the first push, and that is a genuine limitation of this
feature rather than a formality.

## What remains unmet

| Clause | Status |
|---|---|
| 70% coverage of business logic | **met**, measured |
| 100% branch coverage for ordering/idempotency/isolation | **not met** — 85.91%, ratcheted, owned |
| Gates run automatically in CI | **met** (pending first push) |
| "The quickstart MUST run unmodified, verified by automated execution in CI" | **partial** — CI runs the two lanes every quickstart begins with; running each chapter's remaining V-steps needs the chapter tags, which do not exist |

The tag gap is the same standing debt every chapter since 2.2 has recorded. It is
now blocking a constitutional clause as well as the SKIP AHEAD instructions.

## Verification

| Check | Result |
|---|---|
| `pnpm lint` · `typecheck` · `test` · `test:integration` | exit 0 · 120 unit · 87 integration |
| `pnpm coverage` | exit 0, both lanes, 199 tests |
| threshold enforcement | proven: raising a ratchet to 99% fails with `Coverage for branches (85.91%) does not meet ... threshold (99%)` |
| `pnpm check:fences` | 113 files, 20 chapters, 1 retired, plus post-series amendments |
| `pnpm check:docs` | clean |
| fence mechanism | proven: an undeclared manifest change fails the chain |
| workflow | parses; 13 run-steps; commands match local |
