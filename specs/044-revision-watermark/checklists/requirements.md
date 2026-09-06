# Specification Quality Checklist: A reconnecting client can tell it missed a revision

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-06
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

**Counts at validation**: 14 functional requirements, 7 success criteria, 3 user stories, 6 edge
cases. Zero `[NEEDS CLARIFICATION]` markers — every fork had a defensible default, and the
defaults are in Assumptions where they can be argued with.

### Why there are no clarification markers

Four choices looked like questions and each had an answer already in the tree:

| Looked like a question | Answered by |
|---|---|
| per-channel or per-connection signal | FR-006 — a connection-wide flag cannot say which channel to repair |
| counter or timestamp | FR-010 — a clock the client and platform disagree about produces wrong repairs |
| who performs the repair | FR-016a already says the client re-reads history |
| what existing channels start at | reconstructing a count would tell every client to repair everything once |

**The one that could still be wrong is the last.** Starting at zero means a revision applied
before this ships is never repaired for a client that already holds the stale copy. That is the
current behaviour continuing for existing stale copies rather than a new defect, and the
alternative makes every client repair every channel once. Recorded in Assumptions rather than
decided silently.

### The three references this specification makes, and why

A specification for business stakeholders that names a document is making a claim about the
tree. Each is deliberate:

| Reference | Class | Why the spec names it |
|---|---|---|
| `FR-016a`, `FR-016b` | published clauses | they define the limit this feature supplies the remedy for; FR-013 amends them |
| `docs/11-scalability-measurement-2026-09-06.md` | a measurement | supplies the 3m20s window and SC-004's rate baseline |
| SRS revision 1.9 | the record | where the connect-limit finding was filed, named in Out of Scope |

No source file, package, table or column is named anywhere in the specification. The signal is
described by what it must do, not by where it lives.

### What the measurement changed about this specification

Written after `docs/11-scalability-measurement-2026-09-06.md` rather than before, and two
requirements exist because of it:

- **FR-014** — no per-channel query per handshake. At 10,000 connections that cost is the one
  this feature cannot pay, and the number came from the measurement rather than from judgement.
- **SC-004** — the reconnect rate has a measured baseline (1,125-1,675/s) to hold within 10% of.
  Without it the criterion would have read "does not slow reconnects", which is not testable.

The Context section's second bullet — that the edit and delete paths do not touch the channel row
while the send path does — is why the cost is stated as one write per revision rather than
assumed to be free.
