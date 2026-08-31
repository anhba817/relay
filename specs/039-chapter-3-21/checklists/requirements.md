# Specification Quality Checklist: Chapter 3.21 — the typing indicator

**Purpose**: Validate specification completeness and quality before planning
**Created**: 2026-08-31
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
- [~] Success criteria are technology-agnostic
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

**The one `[~]` is deliberate and is the same exception the last four chapters took.**
SC-006 names `unknown_frame_type` and close code 4002, and SC-010 counts producers of
FR-RTM-05's frame kinds. Both are protocol-level facts a customer's client depends on —
`codes.test.ts` asserts the exact close-code set for that reason — so they are the
product's vocabulary rather than an implementation detail. A version of SC-006 that said
"the client is told it broke the rules" would be untestable and weaker.

**Two premises in the brief were checked and both were false**, which is why the spec opens
with them rather than burying them in research:

- *"typing reuses `chan:{channel_id}`"* — the typed points that refused `chan:` for presence
  are all still in the tree, and there are **seven** where ADR-19's record counts three, so
  the argument refuses it here too and for more places than the record names.
- *"typing is the small one"* — `session.ts:948` refuses every inbound frame but
  `message.send`, and the published `typingSchema` has no `state` field. This is the first
  chapter to open a second inbound frame.

**What planning must decide, and the spec deliberately does not**: the renewal interval's
number (FR-011 requires arithmetic, not a value) and the inbound frame's name, which one
task decides and no other repeats.

**A third item stood here and it was already answered when this file was written down.**
*"Whether the typing limit reuses `rl:{env}:{bucket}` or needs its own bucket"* — the answer
is **neither**. Analysis pass 1 read the limiter: it is keyed per environment on a 60-second
window with a two-member `operation` union, against a rule that is per connection, per
channel and 2 seconds. Three mismatches, each fatal alone. The interval is a gateway-held
debounce and `limits.ts` is not edited. **The question offered a binary that excluded its
own answer**, which is the shape a question takes when it is written before the code is
read.
