# Specification Quality Checklist: Tutorial Chapter 3.8 — "Limits you can see coming"

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-19
**Feature**: [spec.md](../spec.md)

## Content Quality

- [X] No implementation details (languages, frameworks, APIs)
- [X] Focused on user value and business needs
- [X] Written for non-technical stakeholders
- [X] All mandatory sections completed

## Requirement Completeness

- [X] No [NEEDS CLARIFICATION] markers remain
- [X] Requirements are testable and unambiguous
- [X] Success criteria are measurable
- [X] Success criteria are technology-agnostic (no implementation details)
- [X] All acceptance scenarios are defined
- [X] Edge cases are identified
- [X] Scope is clearly bounded
- [X] Dependencies and assumptions identified

## Feature Readiness

- [X] All functional requirements have clear acceptance criteria
- [X] User scenarios cover primary flows
- [X] Feature meets measurable outcomes defined in Success Criteria
- [X] No implementation details leak into specification

## Notes

### On the two "no implementation details" items

Both are marked pass, and the reasoning needs stating rather than assuming,
because the spec names Redis, Postgres, `429`, `X-RateLimit-*` and a container in
`compose.yaml`.

The item exists to catch a spec that over-constrains the solution — one that picks
a technology the requirement did not ask for. Everything named here is **already
decided in a document this spec is downstream of**:

- Redis as the counter store and the `rl:` key prefix are specified in SAD §6.3's
  key table against FR-RTL-01. The spec cites that choice; it does not make it.
  (The SAD's row also says "Token buckets", which research R1 later found
  contradicts the same row's TTL column — see R1 for why the chapter builds a fixed
  window and why that is not an ADR.)
- `X-RateLimit-Limit`, `-Remaining`, `-Reset`, `429` and `Retry-After` are the
  literal text of FR-RTL-02 and FR-RTL-03. Paraphrasing them would lose the
  requirement.
- `rate_limited` and close code 4008 are existing constants in
  `packages/protocol/src/codes.ts`, declared in chapter 1.3.

Naming a decision made upstream is citation, not leakage. Where this spec does
make a technology choice — a mail container in `compose.yaml` — it is recorded in
Assumptions with a justification against constitution VII, which is where a new
piece of infrastructure is supposed to be argued.

The "non-technical stakeholders" item is the weakest of the four. This is a
specification for a chapter of a technical tutorial; its reader is a developer.
It is marked pass on the same basis every previous chapter spec in this repository
was, and the standard applied is that a reader who has not seen the code can
follow what is being built and why.

### Two requirements were rewritten during validation

**FR-008** first read "MUST count a documented unit … and the implementation MUST
match", which is a requirement to be consistent rather than a requirement to be
correct. A test over single-message traffic passes whether the limiter counts
requests or messages, so the original wording was satisfiable by an untested
choice. It now requires a test that distinguishes the two.

**FR-014** first read "MUST NOT assert a remaining count the platform cannot
substantiate". Untestable as written: it forbids a state of mind. It now requires
that a client be able to tell "you have N left" from "we are not counting", and
requires the chapter to say which the platform sends. The matching acceptance
scenario in User Story 2 was rewritten with it.

### Decisions deliberately left to the plan

These are not gaps in the spec; they are questions the spec is right to pose and
wrong to answer.

- **The default limit numbers.** The SRS specifies none for FR-RTL-01. FR-007
  requires a documented default and configurability; what the number is belongs in
  research, with its reasoning recorded, because any number chosen here would look
  authoritative and be arbitrary.
- **What a degraded response sends** — headers omitted, or headers with an explicit
  "not counting" signal. FR-014 requires the distinction be possible and the
  chapter state the choice; which choice is a design question.
- **How the auth limiter avoids failing open** without failing closed into an
  outage. FR-011 states the property; whether it is a local in-process fallback, a
  stricter threshold, or something else is research's to answer. This is the
  chapter's sharpest decision and the spec should not pre-empt it.
- **Whether the mail transport is a section or a split.** Recorded as a size risk
  in Assumptions. Three of the last four Part 3 chapters exceeded the word bound;
  the plan should estimate the fence budget before the prose is written.

### What `/speckit-analyze` found that this checklist did not

Recorded because a validation pass that only reports itself passing is one nobody
trusts. Four findings, and the first two are the ones this checklist should have
caught.

**A1 — the biggest, and it was a hole rather than a wording problem.** Three
buckets were defined (`rest`, `send`, `connect`) and a `POST …/messages` is both a
REST request and a message send. Nothing said whether it decrements one, the other,
or both — and FR-002 describes **one** set of headers, so a client reading
`Remaining: 599` could not tell which allowance it had read. The "requirements are
testable and unambiguous" item was marked pass over it. Resolved by research R11 and
FR-036: both are counted, the headers report whichever has fewer remaining, and the
refusal names which limit was reached.

**C1 — the spec said "token buckets" and research had chosen a fixed window.** Two
of the four places carrying the stale word were *published* artifacts, the tutorial
plan's table row and the site registry in both locales. This is the failure chapter
3.7 spent itself on: a document promising something the code does not do.

**C3 — the fixed-window decision contradicted a mechanism the SAD names, with no
reversal condition and no answer to whether it needed an ADR.** Chapter 3.2's
research had set the precedent of addressing that question explicitly; R1 did not.
Both are now in R1.

**G1 and G2 — two requirements that got built and never checked.** FR-007 had tasks
creating three nullable columns and no task asserting an override changes anything;
FR-014 had an implementation task and no assertion. Both are the shape this project
keeps finding at the sabotage battery, and both now have tasks (T011a, T025a).

Four of the eight edge cases also had no task. Three now sit in T006a; the
disable/re-enable/disable case went into T049.

### One requirement carries a claim that may be wrong, on purpose

The Assumptions say this renumbering should be cheap because chapter 3.7 removed
every forward chapter reference from live source, so no fenced file should need
amending. FR-035 and SC-009 test that claim rather than trusting it. If a fence
amendment turns out to be needed anyway, that is a finding about whether 3.7's
rule actually paid for itself — which is worth more than a renumbering that went
smoothly.
