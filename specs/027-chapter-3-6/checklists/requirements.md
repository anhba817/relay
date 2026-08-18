# Specification Quality Checklist: Tutorial Chapter 3.6 — "When to stop trying"

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-18
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs) — *with a stated exception, see Notes*
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details) — *see Notes*
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification — *see Notes*

## Notes

**Two items pass with a recorded exception rather than cleanly, and pretending
otherwise would make this checklist useless.**

1. **Architectural nouns appear in requirements.** FR-003 names the durable queue
   and the analytical path; the Assumptions section names PostgreSQL and ClickHouse.
   These are not free choices being smuggled in — they are constraints the SAD
   (§ webhook dispatcher, "records every attempt as an analytical event") and
   constitution III impose before this feature exists. Removing the words would
   make the spec *less* testable: the whole point of the first scope decision is
   which path the record travels on, and a reader cannot check that decision
   against the source documents if the spec refuses to name it. This matches how
   chapters 3.3–3.5 were specified.

2. **Three success criteria are project gates, not user outcomes.** SC-008 (both
   lanes, coverage ratchets), SC-009 (sabotage) and SC-010 (both locales, figures
   render) describe the tutorial's own quality bar rather than something a customer
   experiences. They are kept because this feature's deliverable *is* a published
   chapter — constitution VI makes test-verification a delivery condition, and
   FR-029's fence rule was added precisely because an earlier chapter shipped
   without it.

**Deliberate partial delivery, stated in the spec rather than discovered later.**
FR-WHK-06 is half-met (attempts are published, not queryable) and FR-WHK-07 is
half-met (notification recorded, no email sent). Both are recorded in Assumptions
with the chapter that finishes them, and FR-005 and FR-011 make saying so a
requirement rather than a footnote. This is the same shape as 3.5's deferral of
these two requirements — the difference is that 3.5 deferred them entirely, and
this chapter delivers the halves that do not need infrastructure the series has
not built yet.

**Ready for `/speckit-plan`.** The two decisions that would otherwise have blocked
planning — where the attempt log lives, and what "notified by email" means with no
email — were settled before the spec was written, not left as markers.
