# Specification Quality Checklist: Chapter 4.13 — the only service that reads the bytes

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-20
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

**16 of 16, and three were argued rather than ticked.**

**"No implementation details" against a specification that names ClamAV and ffprobe.** They stay
because the chapter's open question is *about those two programs*: `docs/12` §7.3 asks whether
constitution VII's one-language rule reaches a sidecar, and that argument cannot be made about
an unnamed scanner. Naming them is what makes FR-013 testable. The same applies to
`media.uploaded` — the specification's central finding is that the event **has no producer**,
and the finding needs the name.

**"Success criteria are technology-agnostic" against SC-003, which names EICAR.** A criterion
reading *"an infected file is rejected"* is not verifiable without shipping a virus. EICAR is
the standard harmless string every scanner must detect; naming it is what turns SC-003 from an
intention into a test, and this project has a record of scan-shaped assertions that passed
against a stub.

**"Requirements are testable" against FR-013 and FR-014, which require an argument.** Both are
prose obligations — argue constitution VII, and state what the scan does not cover. They are
verifiable by reading the chapter, which is the same standard `docs/12` §7.3 sets when it says
*"argue it explicitly rather than by silence"*. An unverifiable requirement would be one where
nobody could tell whether it had been met; these are merely not machine-checkable, which every
prose requirement in this project has been.

**No `[NEEDS CLARIFICATION]` markers, and one flagged assumption instead.** How the platform
learns an upload finished is the chapter's largest hole and the specification takes a position —
the client tells us — with the argument against it written beside it. That is the shape 4.11 and
4.12 both used, and both times `research.md` settled it **against** the specification. A flagged
assumption gives research something to attack; a clarification marker gives it something to wait
for.

**What this checklist cannot say.**

It cannot say whether the client-notice assumption is right. FR-MED-04's *"every uploaded object
shall be virus-scanned"* and a notice the client may simply not send are in tension, and only
`research.md` can price the three mechanisms against each other.

It cannot say where the boundary with `docs/12` row 15 actually falls. This specification puts
the transitions here and the event next door, on the reading that a chapter which computes a
verdict it cannot record is describing a state machine rather than building one. That reading is
`/speckit-plan`'s to confirm against the row-15 brief.

And it cannot say whether FR-012 is one chapter's work. Reconciling a shipped route with an
accepted ADR may be a sentence or may be a gate on every delivery in the platform; the
measurement that decides it — how many objects would stop being deliverable — has not been taken.

---

## Post-plan (2026-09-20)

**Research settled the flagged assumption against the specification, and the spec's Assumptions
section is now wrong on purpose.** It assumed the client tells the platform the upload finished,
and rejected the sweep by pricing it at *"91.6% of the work spent on objects that hold
nothing"*. `research.md` R1 measured that work: **1.412 ms per signed `HEAD`, 4.2 s for the
lane's whole 3,005-row backlog**, 166 of 200 probes being 404s. The waste is free, and the
notice costs FR-MED-04's *"every uploaded object"*. **The spec is left as written rather than
edited back** — the flag exists to record what was believed before the work, and a specification
retro-fitted to its own research is one that has never been wrong. Fourth feature running.

**And two things the spec flagged came back sharper than it stated them.**

FR-012 asked the chapter to reconcile ADR-14's *"no signed URL until `ready`"* with the route
chapter 4.12 shipped. The spec left open whether that was a sentence or a gate on every
delivery; `research.md` R4 measured it — **10 of 76 tests red**, including the isolation
gauntlet's own control — which turns FR-012 from a reconciliation into a sequencing constraint:
the transition and the gate ship together or the gate ships broken.

FR-013 asked for the constitution VII argument that `docs/12` §7.3 names. Research found the
argument is **narrower than §7.3 implies and there is a second one nobody had written down** —
VII's new-service clause against SAD §4.2's table, which no artifact in this feature or in
`docs/12` had mentioned. Both are in `plan.md`'s Constitution Check and its Complexity Tracking.

**One requirement is now known to be partly met by decision.** `contracts/media-verification.md`
§5 ships image dimensions and not audio/video duration, on FR-MED-07's SRS 1.18 precedent —
*unmet by decision and not by oversight*. FR-006 in the spec asks for both; the chapter will
record FR-MED-04 as PARTLY MET with the missing half named, and the gap belongs to whichever
chapter decides ffmpeg is worth its image.

**What the plan still cannot say**, carried as its four open questions: whether the worker is a
compose service or the ingester's unpackaged shape (`gaps.md` 050-8 is the warning), where the
probe's output lives, how a second worker avoids duplicating a first, and whether the three
round trips per object collapse into one. Each has a measurement attached rather than an
argument.
