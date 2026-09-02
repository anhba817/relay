# Specification Quality Checklist: Chapter 3.22 — the five-connection cap

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-01
**Feature**: [spec.md](../spec.md)

## Content Quality

- [X] No implementation details (languages, frameworks, APIs) — **in the requirements**; see note 1 for the deliberate exception in the narrative
- [X] Focused on user value and business needs
- [X] Written for non-technical stakeholders — the scenarios and criteria; see note 1
- [X] All mandatory sections completed

## Requirement Completeness

- [X] No [NEEDS CLARIFICATION] markers remain — 0, both resolved in session 2026-09-01
- [X] Requirements are testable and unambiguous — see note 2 on FR-009
- [X] Success criteria are measurable
- [X] Success criteria are technology-agnostic (no implementation details) — see note 3
- [X] All acceptance scenarios are defined — 11 across three stories
- [X] Edge cases are identified — 9, two of them added in pass 5 for the losing connection
- [X] Scope is clearly bounded — 5 exclusions, one of them decided rather than deferred
- [X] Dependencies and assumptions identified — 7 assumptions, each naming what it rests on

## Feature Readiness

- [X] All functional requirements have clear acceptance criteria
- [X] User scenarios cover primary flows
- [X] Feature meets measurable outcomes defined in Success Criteria
- [X] No implementation details leak into specification — see note 1

## Coverage: every requirement to something that verifies it

| Requirement | Verified by |
|---|---|
| FR-001 | Story 1 scenario 2, SC-002 |
| FR-002 | Assumption on `policy.ts`'s derivation; plan owes the check |
| FR-003 | Story 1 scenario 2, SC-007 |
| FR-004 | SC-003, SC-007 |
| FR-005 | Story 1 scenarios 3 and 4, SC-002, SC-012 |
| FR-006 | Story 2 scenario 1, SC-004 |
| FR-007 | Story 2 scenario 2, SC-005 |
| FR-008 | Story 2 scenario 4, SC-006 |
| FR-009 | SC-006 |
| FR-010 | Story 1 scenario 4, SC-003, drain edge case |
| FR-011 | "counted twice" edge case, T056, T056a — the hijack arm added in analysis pass 1 |
| FR-011a | T041a, SC-013 — release on shutdown, added in analysis pass 1 |
| FR-011b | T030a, T040a, T056b, T056c, SC-014 — what a losing connection does, added in analysis pass 5 |
| FR-012 | "two environments" edge case |
| FR-013 | "racing for the last slot" edge case |
| FR-014 | Story 3, all three scenarios, SC-001 |
| FR-015 | SC-008 |
| FR-016 / FR-016a / FR-016b | "registry unreachable" edge case, SC-011 |
| FR-017 | SC-009 |

## Notes

**1. The narrative cites code on purpose, and the requirements do not.** The
template's rule is that a spec avoids HOW. The section *"What this chapter is, after
the premises were checked"* breaks it deliberately: this project's `CLAUDE.md`
requires a chapter's premises to be checked by command before a requirement is
written, and every premise here **is** a claim about code — that `conn:` exists,
that its shape is open, that nothing already refuses a connection. Two of those
turned out false and one turned out already-decided, which is only demonstrable by
quoting the file and the line. Chapter 3.21's spec did the same for the same reason.

The boundary is held where it matters: **the twenty-one requirements name no data
structure, no library and no code path**, and the three user stories and twelve
success criteria — fourteen after passes 1 and 5 — are readable by someone who has never seen the repository. Two
leaks were found in review and removed — FR-002 named a specific constant and
another service's limit, and SC-004 said "gateway instance"; both are now stated as
outcomes.

**One requirement does name a file, and it is the right one.** FR-017 requires the
published description of the registry to match the system "in both places
`docs/05-sad.md` describes it". The document is the requirement's subject, not its
implementation — this exists because that file currently contradicts itself about
one key, in two tenses, 407 lines apart. The first version of this note claimed no
requirement named a file; it was written before FR-017 was read back.

**2. FR-009 states a relationship without a number, and that is the point.** *"The
**bound** and the **heartbeat interval** MUST be two distinct quantities, with the
heartbeat interval strictly smaller by a stated margin"* is testable the moment
the numbers exist, and the numbers are the plan's job. Chapter 3.19 shipped a bug by
arming a check at exactly its own grace period; naming the relationship in the spec
and the values in the plan is what stops this chapter repeating it. SC-006 pins the
observable consequence — three consecutive intervals without losing a place — which
holds whatever numbers are chosen.

**3. SC-010 measures the test lane, not the product.** It is a project constraint
rather than a user outcome, kept because the 240-second budget has 11.4 seconds of
headroom and a chapter that adds a spawning integration file can spend it. Chapter
3.21 carried the same criterion.

**4. What this checklist cannot tell you, and pass 1 proved it.** Every item above
compares the spec against itself, and every item was ticked before analysis pass 1
found three CRITICALs — a renewal that could steal another connection's slot, a
close code the spec named that does not exist, and a deploy path that breaks
NFR-REL-03. **None of the three was visible from the documents.** All came from
asking the running system: `SET k B XX` against a key holding `A`, `grep 4009` in
`session.test.ts`, and reading what `wss.close()` does to established sockets.

The requirements were right and the mechanism chosen to satisfy them was wrong,
which is the failure mode a spec-versus-spec checklist cannot see. Two things it
still cannot tell you: whether five is the correct number now that something will
finally count it — `policy.ts` divided by five in a comment and shipped — and
whether the design holds at NFR-SCL-01's scale, which this lane cannot measure.

**5. What seven analysis passes changed, and each of the first three found the last one's mistake.**

    pass 1   3 CRITICALs in the design: an `XX` renewal that could steal a slot
             (measured), a close code 4009 the spec named that does not exist, and a
             deploy path holding slots for a full bound against NFR-REL-03
    pass 2   1 CRITICAL in pass 1's own fix — the `DEL` release had the same
             ownership hole the renewal fix had just closed — plus two published
             tutorial pages this chapter falsifies and no task touched
    pass 3   1 CRITICAL in pass 2's premise: every gateway module is OPTIONAL, so the
             cap is opt-in per fixture and the collision pass 2 measured cannot
             happen. Three tasks were built on it. Also: T072 as written turned
             `check:errors` red, and EIR-WS-06 is met for one close code of five
    pass 4   0 CRITICAL, 3 HIGH. The chapter's own instruments did not exist — four
             passes had rewritten every artifact with no id or count checker in the
             directory — and on their first run they found nine real problems and
             two defects in themselves
    pass 5   1 CRITICAL: nothing said what a connection does when its renewal is
             refused, so it would keep serving with no slot — the cap exceeded by
             the mechanism built to enforce it. FR-011b and SC-014 answer it
    pass 6   0 CRITICAL, 3 HIGH: `contracts/refusal.md` promised payload fields the
             protocol's strict error frame rejects; a hard-coded frame count in the
             unit lane that no task owned for the second chapter running; and an
             arms list missing the branches pass 5 had just created
    pass 7   0 CRITICAL, 2 HIGH — both in documents that DESCRIBE the chapter rather
             than ones it changes: this checklist, stale by one on both counts and
             missing FR-011b entirely, and the published chapter table in
             `docs/07-tutorial-plan.md`, which stops at 3.21

**Most findings were mechanisms, not requirements.** The requirements were right and
the way chosen to satisfy them was wrong — the failure a spec-versus-spec checklist
cannot see. Only two of the twenty needed a new requirement, and both were found by
grepping the artifacts for a **state** rather than a symbol: what happens on a
deploy, and what happens when a renewal is refused.

**And this checklist was itself stale for two passes**, which is the argument for
its own note 4. It ticked *"All functional requirements have clear acceptance
criteria"* over a table that did not contain FR-011b, and said twenty and thirteen
where the spec had twenty-one and fourteen. Nothing measured it: `sweep.py` compares
counts inside the four core artifacts and `checklists/` is outside its scope.

**6. Amendments from analysis pass 1.** FR-011 gained a second sentence forbidding a
renewal from taking another connection's place; FR-011a and SC-013 were added for the
deploy path; FR-007, FR-008 and FR-009 were rewritten to use "bound" and "heartbeat
interval", the terms the plan and tasks were already using; and the per-environment
scope moved from "does not need deciding" to a stated decision with its reason, since
FR-RTM-09 says nothing about environments.
