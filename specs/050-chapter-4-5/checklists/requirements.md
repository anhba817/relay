# Specification Quality Checklist: chapter 4.5 — the gateway's first stream

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-14
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

**Two items pass on this project's terms, as they did for 046 through 049.** This specifies a
tutorial chapter about a named platform, so file paths, clause ids and component names are the
subject rather than leakage. The line held is that no requirement states **how**: FR-012 says
the record must reach the store through the existing ingester *unless a measurement says
otherwise*, FR-009 requires the two counters to be reconcilable without saying by what query,
and FR-016 requires ADR-07 to state what it now rests on without deciding the answer.

**Four premises were run against the tree before the spec was written.** The gateway holds no
broker client and no `nats` dependency — five dependencies, none of them a broker. It already
reports connection data through `/internal/usage/connections` every sixty seconds. ADR-07's
v1.1 amendment rests its NATS rejection on the gateway's client-library count. And 4.4 measured
the gateway's seam calls as 18 of 18 tenantless.

**The third premise is the one `docs/12` understated.** §3's table says this chapter "amends
ADR-07 a second time". What it actually does is spend the argument that ADR-07 itself flagged
as its weakest: *"an argument about how many client libraries the gateway holds, not about
whether the mechanism fits."* The chapter increases that count by one. FR-016 and SC-009 make
the record say what it now rests on rather than leaving a reason in place that no longer holds.

**No [NEEDS CLARIFICATION] markers.** The two questions that could have been asked — whether
the quota path is replaced, and whether a third record type needs a second consumer — are
settled by existing decisions and by measurement respectively. Constitution III and FR-RTL-05
settle the first: a quota must refuse synchronously, so it cannot move downstream of a lossy
queue. The second is FR-012's "unless a measurement says otherwise", which is how 4.4's
equivalent was settled and where it belongs.

**One assumption is explicitly unmeasured and flagged as such**: that connection events are
lower volume than request events. FR-015 measures it rather than the plan assuming it, because
4.4 found that the byte figure it carried from planning was 2% light for including the probe's
own subject.
