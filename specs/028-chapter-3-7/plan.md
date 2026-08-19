# Implementation Plan: Tutorial Chapter 3.7 — "Commit and publish are two instants"

**Feature**: `specs/028-chapter-3-7` | **Spec**: [spec.md](./spec.md)
**Created**: 2026-08-19 | **Status**: Ready for `/speckit-tasks`

## Summary

One field, one comparison, and a chapter about why they were missing for four
chapters.

A message is durable at one instant and announced at another. The gateway commits
through the api and then publishes to Redis, and a resuming client whose backfill
query lands between those two instants is delivered the same message twice —
once from the backfill, once from the fabric after its dedup window has closed.
Chapter 2.7 built that window and closes it when the connection goes live, which
is a moment too early.

The fix keeps the backfill's high-water mark on the connection instead of
discarding it, and consults it on the live path. The chapter is the reason this is
a chapter: the same seam appears in 3.3, 3.5 and 3.6 with a different correct
answer each time, and the fan-out path is the one built before the reader had the
concept.

**Research changed the design once.** The spec assumed the mark would be retired
once a higher sequence arrived. R3 shows that reintroduces the bug — two gateway
instances can publish out of order — and that no retirement is needed, because the
mark set is already capped at 200 by the resume contract.

## Technical Context

**Language/Version**: TypeScript 5.x, Node.js 22 (ADR-01)
**Framework**: none in the gateway — it is frameworkless by ADR-15, and stays so
**Data access**: none. This chapter adds no query, no column and no migration.
**Stores**: unchanged. Redis carries the fabric; nothing new is persisted anywhere.
**New runtime dependencies**: none (constitution VII)
**New deployables**: none
**Testing**: Vitest, two lanes, coverage with per-file ratchets
**Target**: the existing compose stack

**Unknowns**: none. The one the spec flagged — whether the retained state is
bounded without a retirement rule — is answered by R3: it is, by the
`MAX_RESUME_CHANNELS` cap the resume contract already enforces, and the retirement
rule the spec proposed is unsafe. The spec has since been corrected: FR-007 states
the bound and FR-007a forbids retirement outright, so the requirement and the
design no longer disagree.

## Constitution Check

Evaluated before Phase 0 and again after design. No violations to justify.

| Principle | How this feature complies |
|---|---|
| **I — Tenant isolation** | The mark is per connection and keyed by channel, and the channels are already scoped by `scopeCursors` against the membership the api returned. No new read path, no new identifier crossing a boundary. |
| **II — No acknowledged message lost** | The load-bearing one, in the direction that matters: this suppresses frames, so the risk is a GAP rather than a duplicate. Suppression is only at or below a mark the backfill has already delivered past, which is why R3 spends its length on proving no legitimate frame lives there. Two success criteria and TWO sabotage mutations exist to hold it — suppressing on every channel rather than the frame's own, and retaining the marks through a degraded resume. Both fail as a gap rather than a duplicate, which is the direction this principle cares about. |
| **III — Two data paths** | Untouched. Nothing analytical is read or written. |
| **IV — Single writer** | Untouched, and deliberately: the fix does not move fan-out publication into the api, which would close the gap by making the announcement transactional and reintroduce the dual write chapter 3.3 removed. Redis stays not-a-source-of-truth; the mark dies with the socket rather than living in it. |
| **V — API-first** | No public surface changes. The wire contract is unchanged — a client that was correct before is correct after, and receives strictly fewer frames. |
| **VI — Test-verified** | The predicate is pure and gets 100% branch coverage; `resume.ts` is already the file where the theorem is held still. A deterministic integration test replaces a probabilistic one (R4). |
| **VII — Boring by design** | One nullable field on a struct that already has four, and a comparison on a path that already serialises JSON. No timer, no cache, no new state store. |

**Post-design re-evaluation**: unchanged. The design removed a proposed mechanism
(retirement) rather than adding one.

## Project Structure

### Documentation (this feature)

```text
specs/028-chapter-3-7/
├── spec.md
├── plan.md              # this file
├── research.md          # R1–R6
├── data-model.md
├── contracts/
│   └── resume.md        # the resume contract, amended
├── quickstart.md        # V0–V9
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks
```

### Source code (repository root)

```text
relay-platform/
├── services/gateway/src/
│   ├── resume.ts              # AMEND: two pure functions — the predicate, and the scoping
│   ├── resume.test.ts         # AMEND: the predicate's cases
│   ├── resume.itest.ts        # AMEND: the fourth quadrant, deterministic
│   ├── registry.ts            # AMEND: one field on Connection
│   ├── session.ts             # AMEND: set it (scoped) on success, consult it in deliver()
│   └── session.test.ts        # AMEND: delivery with a mark present
├── services/api/src/db/
│   └── schema.ts              # AMEND: two chapter-number comments (R6)
├── scripts/webhook-walk.mjs   # AMEND: one chapter-number comment (R6)
└── vitest.coverage.config.mts # AMEND: raise resume.ts's branch pin (already at 93)

relay-tutorial/
├── app/(en)/part-3/chapter-07/commit-and-publish-are-two-instants/{page.mdx,figures.ts}
├── app/(vi)/vi/part-3/chapter-07/commit-and-publish-are-two-instants/{page.mdx,figures.ts}
├── lib/tutorial.ts            # DONE during /speckit-specify: 3.7 published, 3.8, 3.9
└── app/**/part-3/chapter-0{5,6}/…, app/**/part-0/chapter-04/…   # AMEND: prose cross-references
```

## The three pieces, in the order they should be built

**1. The failing test.** Before the fix, not after. R4 makes it a one-number
variation of a test that already exists, and it must be watched to fail — a
regression test that has never failed is a regression test nobody has checked.

**2. The fix.** The pure predicate, the field, the two call sites. `deliver()`'s
comment claiming it reads `phase` "and nothing else" is rewritten in the same
change, because that sentence is the defect stated as a principle.

**3. The renumbering.** Independent of the other two and safe to do at any point,
with one ordering constraint: the source-comment corrections must be fenced in
this chapter, so they land before the chapter's fences are generated.

## Phase 2 preview — how tasks will be shaped

Baseline first, including twenty lane runs to establish the flake rate before the
fix rather than asserting it afterwards. Then the failing test, watched to fail.
Then the fix, watched to turn it green. Then the sabotage battery, the two lanes
and coverage. **Then the renumbering** — the source-comment corrections and the
cross-reference sweep — because the corrected files have to exist before this
chapter's fences are generated from them. Then the chapter in English, the figures,
the battery. Then the Vietnamese translation and publication. Then the quickstart
run, the credential scan, the notes and the tag.

Two ordering constraints worth stating now:

- **The twenty-run baseline is measured BEFORE the fix.** SC-001 asks for twenty
  consecutive passes afterwards; that number means nothing without knowing what
  twenty runs looked like before. If the flake does not appear in twenty
  pre-fix runs, the chapter must say so — it would mean the rate is lower than
  one in six and the deterministic test is carrying the whole proof.
- **The source-comment corrections are fenced in this chapter**, not in
  `post-series.md`. Their chains end in 3.6, this chapter is the next link, and
  this chapter is precisely where the fragility is discussed.

## Traceability

| Req | Designed in | Proven by |
|---|---|---|
| FR-001 | research R3; contracts/resume.md § suppression | `resume.itest.ts` — the fourth quadrant, deterministic |
| FR-002 | research R3 — the mark is a floor, never a ceiling | `resume.itest.ts` test 3, unchanged; sabotage 2 |
| FR-003 | research R1; the field on `Connection` | `session.test.ts` — a live frame at or below the mark |
| FR-004 | data-model.md — the mark is keyed by channel | `resume.test.ts` — two channels, one suppressed |
| FR-005 | contracts/resume.md § degraded | `resume.itest.ts` — a degraded resume retains nothing |
| FR-006 | data-model.md — null for a fresh connect | `session.test.ts` — no cursor, no suppression |
| FR-007 | research R3 — the `MAX_RESUME_CHANNELS` cap | `resume.test.ts` — the mark set never exceeds the cursor set |
| FR-007a | research R3 — out-of-order publication | `resume.itest.ts` — sequence 5 then sequence 4, both suppressed |
| FR-008 | research R3 — the mark is per connection | `resume.itest.ts` — publish as another instance |
| FR-009 | the chapter's own prose | battery check at chapter end |
| FR-010 | quickstart V2 | captured-output.md |
| FR-011 | research R1, R2 | the chapter's own prose |
| FR-012 | the chapter's own prose | traceability check at chapter end |
| FR-013 | `specs/027-chapter-3-6/baseline.txt` | the chapter's own prose |
| FR-014 | — | `pnpm check:fences` locale count |
| FR-015 | research R6 | `pnpm check:fences` HEAD check |
| FR-016 | quickstart V0–V9 | captured-output.md |
| FR-017 | done during `/speckit-specify` | the plan and the registry agree |
| FR-018 | research R6 | the cross-reference sweep at chapter end |
| FR-019 | research R6 | the sweep, including the already-stale reference |
| FR-020 | research R6 | `pnpm check:fences` exit 0 |

FR-009, FR-011, FR-012 and FR-013 are claims about prose and are checked by
reading. They are listed so they cannot be quietly dropped.

## Complexity Tracking

No constitutional violations require justification. Two judgement calls a reviewer
should be able to challenge:

| Decision | Why it is not simpler | What was rejected |
|---|---|---|
| The mark is never retired | Retirement is the smaller-sounding option and it is unsafe: two gateway instances can publish out of order, so a higher sequence arriving first would retire the mark before the delayed lower one lands (R3). Not retiring is both simpler and correct, and the state is already capped at 200 by the resume contract | Observation-based retirement (the spec's own assumption, overturned); a time-based window (a guess about the publish gap, wrong in the unsafe direction); id-based dedup with a bounded set (more memory, weaker guarantee) |
| A whole chapter for one field | The change is four lines. The chapter is not about the change — it is about a model that had three cases when the matrix has four, a test suite that inherited the model's blind spot, and a seam Part 3 teaches three times before this. The plan calls 2.7 "the tutorial's flagship bug"; a series that leaves its flagship bug half-closed without saying so has a bigger problem than a duplicate frame | A post-series fence (the file exists for changes that teach nothing, and this teaches the most transferable lesson in Part 3); folding it into 7.5 (thirty chapters of a knowingly-flaky lane, and the lesson arrives long after the seam it belongs to) |
