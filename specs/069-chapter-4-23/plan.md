# Implementation Plan: chapter 4.23, "★ Milestone: the Priya test"

**Feature**: `specs/069-chapter-4-23/` · **Spec**: [spec.md](./spec.md) ·
**Research**: [research.md](./research.md)
**Created**: 2026-10-05 · **Predecessor tag**: `part4-ch21`

## Summary

Journey 3 made executable, as `tuan.itest.ts` made Journey 4 executable at chapter
2.8. The product is a path walked end to end and a set of verdicts — not a
mechanism. **A milestone appears after all the work it verifies** (`docs/12` §5 rule
4), which is the constraint that decides almost every open question below.

**The premise check found THREE holes, and swept rather than counted they are one
property with an exact predicate** (R11). Journey 3's six stages assert **fifteen**
capabilities — five stages carry a *"What Relay must provide"* block and Stage 4's
one assertion is in its prose:

```
every capability that cites a requirement   ->  HOLDS
every capability that cites none            ->  IS A HOLE
3 of 3 in both directions, no exceptions
```

**The predicate is the claim; the tally is an illustration.** Counted one way the
table is twelve and three of fifteen, and the unit is a judgement — *"external IDs on
channels and users"* is one row with two clauses. A reader who recounts and gets
sixteen has reproduced the finding, not refuted it.

**A capability `docs/03` asserts without naming a clause is a capability nobody
built.** The three: **Stage 2's** channel retrieval by external id (the natural
attempt answers **500**), **Stage 5's** *"a banned user's connections drop"* (checked
at auth and at send, never in between, and there is no ban frame), and **Stage 6's**
request-id join (both rows carry it, neither reader accepts it as a filter).

**That is 4.17's finding one level up**: each of the twelve had a chapter, and the
three with no clause had no owner, so no suite covered them and no aggregate existed
to notice. **A journey map is prose and no checker in these repositories reads
prose.** Finding them is what the milestone is for; how each is resolved is Phase 2's
and not this plan's, and in every case the option a reader wants is the one
`docs/12` §5 rule 4 forbids a milestone from taking.

## Technical Context

| | |
|---|---|
| **Language** | TypeScript, Node.js — no new language (constitution VII) |
| **New runtime dependency** | **none planned**; the test is `fetch` and `ws` as the sealed suite already uses them |
| **New service** | none — VII's "deliberately not a separate service" table is not engaged |
| **Test home** | `packages/outsider/src/priya.itest.ts`, a NEW file (R1) |
| **Runs against** | the deployed containers via `RELAY_API_URL`, `RELAY_WS_URL`, `RELAY_DEMO_CREDENTIAL` |
| **CI job** | `relay-platform — the sealed integration`, which was 21 of 21 at 4.21's close |
| **Concurrency** | **this is the package's SECOND file and its files run in parallel** against one seeded tenant — measured, R9. Assertions scope to their own fixtures |
| **Storage** | none added — no migration, no column, no table |
| **Documents** | `docs/04-srs.md` (FR-CHN group, §7.3, revision 1.29), `docs/12` the milestone row and §7.6, `docs/07` row 23 |
| **Unknowns** | **R2's option and R8's** — the only two, and both are Phase 2 |

## Constitution Check

Read clause by clause rather than cited by number, because 4.21's analysis pass 5
found that a principle's bullets do not get one verdict.

### I. Tenant isolation — **ENGAGED TWICE, and the second is not about tenants**

The sealed suite already asserts *"cannot see another tenant's channel, and cannot
tell it apart from an absent one"*. **If R2 lands on option A or C, a new resolution
path is a new place tenancy can be missed**, and 4.21 measured what that looks like:
three of four scoped arms were invisible to a single-mutation probe. A lookup by
external id MUST be scoped to the environment and MUST be probed by deleting that
scope and re-running, not by reading the code.

**AND THE SECOND IS ISOLATION FROM A NEIGHBOUR RATHER THAN FROM A TENANT (R9).** The
sealed package runs its files concurrently — measured, 6.01s of tests in 3.10s of
wall clock — and `ci.yml:355` seeds one credential for the whole run, so
`priya.itest.ts` and `integrate.itest.ts` share a tenant's audit log while one reads
it and the other writes to it. **`check-lane-scope.py` cannot see this**: it scans
SQL and the package talks HTTP. The discipline is the author's, and T031 records the
bound on its own zero rather than reporting it as evidence.

### II. No acknowledged message is ever lost — **NOT ENGAGED**

The chapter sends and deletes messages and acknowledges nothing new.

### III. Two data paths, never crossed — **ENGAGED WEAKLY, ONE PLACE**

Stage 6 reads the audit log (operational) and may read the request log (analytical)
to join an entry to its request. **That join is a READ across the fence by a human
through two published endpoints, not by a service**, which is what the request id
exists for — `docs/03` Stage 6 says so in as many words. No code crosses.

### IV. Single writer — **NOT ENGAGED**. The chapter adds no writer.

### V. API-first — **ENGAGED, AND IT IS THE POINT.** The whole test is the published
API seen from outside. Stage 2's hole is a V failure found by a V-shaped exercise.

### VI. Requirement-driven, test-verified — **FIVE BULLETS, THREE ENGAGED**

1. *"New behavior without a requirement gets a requirement first."* **This is the
   clause that governs R2.** Options A, B and C are new behaviour; all three need an
   FR-CHN amendment **before** the code, not after. Option D is an amendment and
   nothing else.
2. *100% branch coverage for tenant isolation.* Engaged only if R2 adds a resolution
   path; then its tenancy arm is in that population.
3. *The cross-tenant suite, dependency vulnerability scans and the OWASP Top 10 scan
   gate releases.* **Two of the three do not exist** — carried as 4.21's `gaps.md`
   entry and not closed here. A milestone is the chapter where that absence is most
   visible and it must be restated rather than quietly re-carried.
4. *The quickstart MUST run unmodified, verified by automated execution in CI.*
   **Zero occurrences of `quickstart` in `ci.yml`** — a `T` clause at 100% verified
   by hand every chapter. Restated, not fixed.
5. *Input validated against a schema; unknown fields rejected on write endpoints.*
   Engaged only under A/B/C, and a read route takes no body — the same reasoning
   4.21 recorded as **not engaged** rather than unmet.

### VII. Boring by design — **ENGAGED ON ITS FIRST AND FOURTH BULLETS**

No new language, no new service, no new dependency. **The ADR question is open and
the answer is probably yes under A or C and no under D** — a second key space on an
existing route is an architecture decision with a reversal condition, and 4.21's plan
predicted *no ADR* and was wrong, so a prediction here is worth nothing without the
check. It is a task, not an assumption.

**Non-goals**: nothing in this chapter adds product surface beyond what Journey 3
names, which is VII's scope commitment applied to a milestone.

## Project Structure

### Documentation (this feature)

```
specs/069-chapter-4-23/
├── spec.md              12 FR, 10 SC, 3 user stories
├── plan.md              this file
├── research.md          R1–R7, every figure measured 2026-10-05
├── data-model.md        the journey's six stages as a traversal, and what each needs
├── contracts/
│   └── journey.md       the test's contract: stages, margin annotations, revert set
├── quickstart.md        walk Journey 3 by hand, the way Priya's tool would
├── clauses.md           per-stage and per-clause verdicts          (written at close)
├── traceability.md      by reading, not by grep                    (written at close)
├── baseline.txt         every phase in the order taken             (written throughout)
├── gaps.md              numbered, carried ledger re-measured       (written at close)
└── tasks.md             /speckit-tasks
```

### Source (repository root)

```
relay-platform/
├── packages/outsider/src/
│   └── priya.itest.ts            NEW — the journey, six stages, annotated margin
└── services/api/src/             TOUCHED ONLY IF R2 LANDS ON A, B OR C
    ├── channels/channels.controller.ts
    ├── channels/channels.schema.ts
    ├── channels/channels.service.ts
    └── db/repository.ts
docs/
├── 04-srs.md                     FR-CHN amendment · §7.3 · revision 1.29
├── 07-tutorial-plan.md           row 23 SHIPPED
└── 12-part-4-structure.md        row 23 CLOSED · §7.6
relay-tutorial/
└── app/(en)/part-4/chapter-23/the-priya-test/{page.mdx,figures.ts}
```

## Phases

**Phase 1 — baseline.** Lane environment pinned, every gate's opening figure, the
fence bill from R6 re-derived against what the tasks actually touch, and the CI
error-set baseline for the per-error comparison at close.

**Phase 2 — the decisions.** R2's option, with all four priced and the losing
argument recorded. Whether that needs an ADR. Whether the Stage 2 resolution is
tenancy-scoped by construction or by a predicate somebody wrote. **These come before
code because constitution VI's first bullet says the requirement comes first.**

**Phase 3 — the journey (P1).** `priya.itest.ts`, six stages in order, each
assertion annotated with the chapter it verifies.

**Phase 4 — the arrow (P2).** Carry an image from upload to erasure, or record which
segment could not be and why.

**Phase 5 — the verdicts (P3).** `clauses.md`: six stages, three Phase 3 clauses,
each met / demonstrated / unmet by decision / unreachable, with where.

**Phase 6 — the probes.** Revert three chapters and watch three named assertions
fail (SC-002). Probe any new tenancy arm by deleting it. Both halves of the coverage
pin probe if any pin moves.

**Phase 7 — the documents.** The FR-CHN amendment, §7.3's verdicts, §7.6 if this
chapter owns it, revision 1.29, both Part 4 tables, an ADR if phase 2 said so.

**Phase 8 — the chapter.** 2,000–4,000 prose words, figures, TRAP and WHY boxes,
fences and hunks from the checker's own replay.

**Phase 9 — the record and the close.** Battery, quickstart run, push, CI compared
per error, tag `part4-ch23`.

## Complexity Tracking

| thing | why it is justified | what would make it unjustified |
|---|---|---|
| A new test file rather than a section of `integrate.itest.ts` | that file is 1,677 lines across 5 fence pages with 5 appendix hunks; a journey nobody can find is not a milestone | if the duplicated `required()` grows past a dozen lines, extract it and pay the hunks |
| Possibly amending FR-CHN on a milestone chapter | constitution VI: new behaviour gets a requirement first, and `docs/03` asserts a capability no clause carries | if R2 picks option D, nothing is built and the amendment is the whole change |
| Reading `docs/03` as normative | `docs/07` Rule 2 makes the journeys the SRS phase exit criteria, so Journey 3's "what Relay must provide" lines are requirements in another document's clothes | if §7.6's amendment resolves the disagreement the other way, re-open this |

## What this plan does not decide

- **R2's option, and R8's.** Seven options priced across two holes; both choices are
  Phase 2's and belong in `baseline.txt` with both halves of each argument. **Take
  them together** — building for one hole and not the other needs a reason better
  than which was found first.
- **Whether Phase 3 can be exited.** Its first clause needs a scheduler ADR-28
  declined to build. The chapter states a verdict; it does not build a scheduler.
- **Whether §7.6 is this chapter's.** It concerns FR-DSH and FR-EMJ, which are Part
  5's — but this is the last chapter of Part 4 and the one that reads §7.3 hardest.
  A task asks; it is not assumed either way.
