# Specification Quality Checklist: Chapter 3.12 — Milestone: the isolation gauntlet

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-22
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

Every box is ticked and three of them are ticked against a reading that should be
stated rather than assumed, because a checklist that quietly redefines its own items
is worse than one that fails.

**"No implementation details" and "technology-agnostic", read as: prescribes no
design, names the state that exists.** The spec names `usage_periods`,
`packages/e2e`, `scripts/sync-docs.sh`, `docs_url`, PL/pgSQL, the figure 90.57%, and
close to thirty other artifacts. All of them exist today and none is a decision this
spec is making — they are the repository this chapter is about, at the commit it starts
from. Where the spec reaches a genuine design choice it declines to make it: FR-002
requires the target list to be derived and does not say from what; FR-040 requires the
coverage figure to be measured somewhere the run can see and leaves the location to
the plan; FR-032 requires a documented credential path and names two acceptable
answers without choosing. This is the same reading chapters 3.10 and 3.11 shipped
under, and applying the generic rule literally would produce a specification that
cannot say which port a fixed port is.

**"Written for non-technical stakeholders" is false in the ordinary sense and true in
this project's.** The stakeholder is the series' author and the reader who checks the
chapter against the requirements. A version of this document readable by someone who
does not know what a tenant identifier is could not state FR-004.

**Requirements verified by inspection rather than by test.** Seven — FR-009, FR-014,
FR-015, FR-022, FR-034, FR-035, and the "state the number" clause in FR-040 — require
the chapter to write something down. The SRS's own verification vocabulary allows
inspection alongside test, and the alternative is a chapter that measures honestly and
publishes selectively. Each names what has to be written and what would make it wrong.

**One thing the spec asserts and cannot yet prove.** FR-022 defers the rest of the
public channel and user surface to chapter 3.13, and no such chapter exists in
`docs/07-tutorial-plan.md` yet. The deferral is a promise until that table is edited,
which is planning work, not specification work — recorded here so it is not discovered
later as a gap.

**Two findings this specification is built on came from reading the code rather than
the documents, and both changed the chapter's scope.** There is no public endpoint to
create a channel or add a member, which makes the Phase 2 exit criterion unreachable
for reasons that have nothing to do with documentation; and the set of error codes the
platform can emit is larger than the registry that is supposed to hold it, so
"document every code" could not have been done from the registry alone. Neither is
visible in the SRS, the SAD, or the tutorial plan.

## Analysis pass one — documents against each other and against the published series

Seventeen findings, three CRITICAL, all three applied or escalated. The checklist above
still reads 16/16, and two of its boxes are now ticked for better reasons than they were.

**Two of the three CRITICALs came from testing a claim rather than reading it.**

`grep -rn 4124` instead of trusting a filename found that the fixed port is in
`services/gateway/src/limits.itest.ts` and not the api's file of the same basename. The
wrong path had travelled from CLAUDE.md's shorthand into the research, the plan and the
task list without anybody opening the file — so the fix would have edited a file that
binds no port and left FR-041's defect standing. The same pass found that neither file is
fenced by any chapter, against chapter 3.11's note calling it "another chapter's fenced
file", so the change is smaller than three documents claimed.

`npx eslint services/api/src/quotas/period.itest.ts` exiting 0 found that Principle I's
lint ban is not in force for any integration test: a second flat-config block for
`**/*.itest.ts` redefines `no-restricted-imports`, and flat config replaces rather than
merges. The config's own comment claims one named test is "the one TEST allowed a raw
client". Every test is. That became FR-043 and SC-028 — the requirement count moved from
42 to 43 and the outcome count from 27 to 28.

**The third is `outbox`, and it is escalated rather than fixed.** It has no
`environment_id` column and **zero** foreign keys, so neither branch of Principle I's
second clause is available; its tenant lives in a jsonb key and in a substring of
`subject`. Its payload carries `data.text`, so this is not a bookkeeping table — a
cross-tenant read here reads message content. The fix measures at one insert site with
an exact backfill. The decision between fixing the column and amending the clause is a
governance action, not a chapter's.

**Four findings were the same mistake at different addresses.** A per-chapter fence file
that does not exist, tutorial-repo files filed as fenceable when the chain resolves every
title against `relay-platform`, `turbo.json`'s env allowlist unaccounted for, and a
success criterion (SC-007) asserting the opposite of what the design delivers. Each was a
claim carried from one document into the next without being checked against the
mechanism it named.

**And one omission that strengthens an argument already made.** R19 argued the size split
on prose words and never counted fences: 17 new files and 13 amended, against chapter
3.11's 21 files and 34 fences. An amended file needs a diff fence in this chapter's own
prose or the chain's HEAD property fails, so the fence surface is a floor under the page
rather than a by-product of it. The stronger half of the case was sitting unused.
