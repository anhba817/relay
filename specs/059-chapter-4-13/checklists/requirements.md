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

---

## Analysis pass 1 (2026-09-20)

Six findings — one CRITICAL, three HIGH, two MEDIUM — all six applied. **Four came from running
a premise rather than from reading the artifacts against each other**, and the CRITICAL one
inverted a design decision three documents had agreed on.

- **THE EICAR TEST AND FR-MED-03 ARE MUTUALLY EXCLUSIVE, AND THE CLAUSE HAD ALREADY DECIDED THE
  ORDER.** SC-003 needs the scanner to refuse a file; EICAR is 68 bytes of text and
  `ALLOWED_TYPES` holds no text type, so a declaration-first worker refuses it as
  `declaration_mismatch` and never asks. The obvious dodge — embed the signature in a valid PNG
  — was measured against a running ClamAV through `INSTREAM` and **does not work**: EICAR alone
  is `FOUND`, EICAR plus a newline is `FOUND`, and **EICAR plus two hundred spaces, EICAR at
  either end of a valid PNG, and EICAR followed by a kilobyte are all `OK`**. The signature
  matches the file, not a substring. So the scan runs first — which is what FR-MED-04's *"every
  uploaded object"* required all along, since declaration-first leaves the mis-declared objects
  unscanned and those are the ones worth scanning. `research.md` R5a, `data-model.md` §4,
  T039a/T039b/T040/T040a.
- **`research.md` R4's "10 of 76" was an undercount, because the probe ran in one lane.** The
  sealed outsider suite fetches the bytes of a **`pending`** object — the three assertions 4.12
  added as SC-010 — and T046's gate turns that 404. **And it couples two open questions**: only
  a worker inside the composed profile moves the object to `ready`, so plan open question 3
  decides whether SC-010 can be satisfied at all or merely becomes a poll. T086 is a repair now
  rather than a check.
- **A fifth service joins a third registry and no task named it.** `bound-port.test.ts:49`
  derives `serviceMains()` from the tree and asserts each reads back a bound port unless
  declared in `BINDS_NOTHING`, in both directions — so `services/media-worker/src/main.ts` turns
  the unit lane red the moment it exists. **050 paid two chapters for this exact omission**, and
  turbo's cache hid it. T018a.
- **The worker would have authenticated as the dispatcher.** `contracts/` §1 and `research.md`
  R8 both said it holds `RELAY_INTERNAL_CREDENTIAL`; `authenticate.middleware.ts:63` maps that
  variable to the literal `"dispatcher"`, and `Principal.service` is what every log line and
  request-log row reports. **Two artifacts agreed with each other and neither asked what the
  credential says** — the shape this project names. T012a adds a third entry, and the widened
  `PlatformService` union stopping routes from compiling is that type's stated purpose.
- **The store's two headers are not equally trustworthy, measured.** A presigned PUT of twelve
  MP4 bytes sent with `content-type: image/png` answers `HEAD` with `image/png` — the client's
  claim, echoed — and `content-length: 12`, the store's own count. **So FR-MED-03 splits**: the
  size is answered by the `HEAD` the sweep already issues and the type needs the bytes. T022,
  T022a.
- **One coverage gap of nineteen alarms.** The mechanical sweep flagged 19 of 26 requirement ids
  as uncited; reading each, **18 are false** — the tasks cite SRS clause ids where the spec cites
  local ones — and one is real: FR-008 and SC-005's *"the bytes are read once"* had no task.
  T026a. This is chapter 4.11's pass-10 result reproduced, and the reason `traceability.md` gets
  built by reading.

**Two premises came back clean and are recorded because a premise that holds is only evidence
once checked.** A presigned GET honours `Range` — **206 · `bytes 0-7/12`** — so the contract's
three-read design is buildable; SigV4 signs `host` and not `Range`. And `pnpm-workspace.yaml`
globs `services/*`, so the new package needs no workspace edit — one list the fifth service does
not have to join.

**Task count 92 → 99.** Requirements unchanged at 26. The probe container was removed before
anything else was counted.
