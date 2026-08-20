# Specification Quality Checklist: The fault that only shows up in company

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-20
**Last re-validated**: 2026-08-20, after three analysis passes and four rounds of amendment
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

**This checklist was stale, and that is the first thing it should say.** It was
written against a 19-requirement spec and left untouched while the spec gained
nine requirements, superseded two, withdrew an assumption and changed its central
mechanism. Its previous Notes described the checksum design in the present tense
and ended with *"if the plan finds a sound way to attribute under parallelism,
that assumption should be revisited rather than inherited"*. The plan found one.
Nobody revisited. A validation artifact that passes because no one re-ran it is
this feature's own subject matter, arriving in the file whose job is to prevent
exactly that.

Re-validated below against 28 FR and 8 SC.

### Where the ticks need reasoning

**"No implementation details" and "written for non-technical stakeholders"** are
judged against the domain, and the spec has moved *toward* mechanism since the
first validation — deliberately. FR-020 names a connection option; FR-026 names
module scope; FR-023 names per-file sentinels. Those are not leaked details, they
are the requirement: research measured that a `SET` through a pool carries on two
of five connections, so *where* the exemption is written is the difference between
a working guard and an intermittent one. A spec that hid that behind
"the exemption must be reliable" would be less testable, not more abstract.

What the spec still declines to name: the test runner, the shape of the lint
rule's options, and the SQL the trigger contains.

**"Requirements are testable and unambiguous"** holds for 26 of 28. FR-008 and
FR-011 are marked *superseded by research R6* and describe a mechanism that no
longer exists — retained rather than deleted so the record shows what was believed
and what replaced it. A reader must not treat them as work. They are the reason
this line is not a bare tick.

**"All functional requirements have clear acceptance criteria"** was **false** at
the start of the third analysis pass: FR-012b had no task. It records that
`expandEventToDeliveries` and `replayDeadLetter` are bounded by an id and need
neither a batch size nor a restriction — the accounting category whose absence
produced a wrong number in three documents. T022b now carries it.

**SC-008 is lagging**, and cannot be otherwise. The only proof that a class of
fault stopped recurring is the chapter after this one not recurring it. The other
seven success criteria are verifiable on delivery.

### The assumption that was withdrawn

The previous version of this file called it "the assumption that carries more
weight than the rest": that the guard's check would be run-scoped because
attribution needed serial execution. Research R6 replaced the checksum with a
trigger, which raises inside the offending transaction and attributes under
parallelism with no serial mode. The assumption is struck through in spec.md
rather than deleted.

What replaced it is narrower and measured: attribution holds for a statement in a
test, and **not** for one issued by a background relay, which catches and logs its
own errors. FR-025 closes that by refusing to start a non-exempt file with a relay
enabled.
