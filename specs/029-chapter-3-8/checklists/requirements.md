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

- `rl:{env}:{bucket}` token buckets in Redis are specified in SAD §6.3's key table
  against FR-RTL-01. The spec cites that choice; it does not make it.
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

### One requirement carries a claim that may be wrong, on purpose

The Assumptions say this renumbering should be cheap because chapter 3.7 removed
every forward chapter reference from live source, so no fenced file should need
amending. FR-035 and SC-009 test that claim rather than trusting it. If a fence
amendment turns out to be needed anyway, that is a finding about whether 3.7's
rule actually paid for itself — which is worth more than a renumbering that went
smoothly.
