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

## Analysis pass 2 (2026-09-20)

Five findings — three HIGH, two MEDIUM, no CRITICAL — all five applied. **Two of them falsify a
sentence written in the platform's own source and copied into three of this feature's
artifacts**, which is the *artifacts agree with each other and not with the tree* shape one level
further out than usual: here they agreed with a comment.

- **`@Accepts("platform")` does not compile, and `contracts/` §1 opened with it.**
  `credential.guard.ts:36` types `AcceptSpec` so a platform route must name its callers —
  *"an authorization that can be omitted is one that will be, and the omission is invisible"*.
  The form is `@Accepts({ platform: ["media-worker"] })`, and `"media-worker"` is unwriteable
  until `PLATFORM_SERVICES` holds the row. **That is what makes pass 1's T012a mandatory**, for a
  reason no artifact had given. T012b.
- **AND THE REASON THEY DID GIVE IS FALSE.** Three artifacts repeated the middleware's own
  comment: *"adding a third internal service widens this union on its own and every route that
  must now decide about it stops compiling."* Measured — third entry added, `tsc --noEmit` on the
  api, **exit 0**. `PlatformService` occurs in three positions and every one is
  `readonly PlatformService[]`, where a new member is purely additive. The protection the comment
  describes is real and lives one file over. T055a files the comment itself.
- **T049's premise was backwards.** It said this chapter adds internal routes *"so the derivation
  may report nothing — and if it comes back green, that is the finding"*. `targets.ts` already
  classifies **nine `/internal` routes**, four of them `accepts: "platform"`. The derivation will
  name both new ones, and a green run would mean it missed them: a defect pre-labelled as an
  expected outcome.
- **The sweep's batch query is a sort, and `data-model.md` §5 reasoned about the predicate.**
  `ORDER BY created_at LIMIT 50` over 3,028 rows is a `Seq Scan` plus a top-N heapsort —
  **90 buffers, 2.370 ms** — against **4 buffers and 0.029 ms** with a partial index on
  `(created_at) WHERE state = 'pending'`, at 88 kB. Chapter 4.1's *"the sort is 656 of a 698 ms
  plan"* at small scale. **And the ratio runs the opposite way from 4.12's GIN**: 11.96% today
  because every row is `pending`, shrinking to the size of the backlog as objects resolve, where
  a whole-column index stays the size of its table. The two published together say what a partial
  predicate buys. T020a, and plan open question 2 closes.
- **Type verification had no per-format enumeration for the six audio and video types**, where
  T024 has one for the four image types — zero occurrences of `audio/mpeg`, `audio/ogg`,
  `audio/wav` or `video/webm` across the tasks, the contract and the data model, while FR-MED-03
  covers all ten. T023a. **And `audio/mp4` and `video/mp4` are the same container**: both declare
  `ftyp` and the authoritative discriminator is inside `moov`, so T023b decides in writing what
  the bytes can tell apart before a test asserts a distinction they cannot make.

**One premise held and is recorded**: `serviceMains()` reads `services/*/src/main.ts` straight
off the filesystem, with no `package.json` and no build, which confirms pass 1's T018a — the unit
lane goes red the moment the worker's `main.ts` exists.

**Task count 99 → 104.** Requirements unchanged at 26. Plan open questions 5, one closed. The
probe index was dropped and the third `PLATFORM_SERVICES` entry reverted before anything else was
counted; `probe_%` indexes remaining, **0**.

**On two passes.** 6 findings then 5; severity 1 CRITICAL then 0. Pass 1 asked what the platform
*does* — the store's headers, ClamAV's signature, the sealed suite's fixture. Pass 2 asked what
the platform *claims about itself*, and two of five claims were wrong. The count has barely moved
and the kind of question has.

## Analysis pass 3 (2026-09-20)

Five findings — one CRITICAL, three HIGH, one MEDIUM — all five applied. The pass asked a
question the first two did not: **what does this chapter break in the chapters behind it?**

- **THE WIDENED CHECK TURNS TWO SHIPPED TESTS RED, AND NOTHING PREDICTED IT.** T008's constraint
  was applied to the live database and chapter 4.11's suite run: **2 failed, 15 passed.**
  `attach.itest.ts:288` is titled *"cannot be given a `ready` object to attach, because the
  database refuses one (SC-006)"* and asserts the constraint's own name in the refusal text; its
  sibling at :307 uses `'rejected'` as its example of *"a state that is neither"*. Both inserts
  now succeed and both get `''`. **Nothing in this feature named that file** — its only two
  `SC-006` mentions are this chapter's own criterion, a different one with the same number. And
  `research.md` R4's *"10 of 76"* missed them for a **second** reason: pass 1 found it had
  skipped the sealed suite in another lane; this is a third file in the lane it did run. T008a
  repairs both — the first becomes *a `ready` object is attachable*, the second keeps its title
  and changes its example to **`'scanning'`**, the value T011 refuses to make a state.
- **AND 0018 IS ONE-WAY ONCE A TERMINAL ROW EXISTS**, found by trying: restoring the narrow
  constraint answers `is violated by some row` until the `ready` and `rejected` rows are deleted.
  ADR-16 makes migrations forward-only so it is a property, not a fault — and it is the first
  thing a local rollback meets. T008b.
- **T014's 409 would have answered `internal_error`.** The status ladder has nine rungs and 409
  is not one. **The precedent is three files away and was paid for**: `usage.controller.ts:90`
  throws a `ConflictException`, and `connection_environment_conflict` exists at 409 in the
  registry with `expected 'internal_error' to be 'connection_environment_conflict'` in its
  comment. Decided as **422 `unprocessable_request`** — 4.11's own code, the same caller action,
  and `check:errors` stays at 34/34. The rejected alternative is recorded: a new code at 409 puts
  vocabulary for a route no customer can call into the document customers read.
- **Chapter 4.11 left a note addressed to this chapter and no task answered it.**
  `repository.ts:5119`: *"`'ready'` is unreachable today and the predicate says it anyway … a
  predicate that named one would have to be found and widened by **whoever builds the
  scanner**."* Three consequences, none covered: the second arm becomes reachable and nothing
  asserted it (T015a), the comment goes stale — the class this movement keeps finding in its own
  files (T015b) — and **4.11's recorded per-arm probe result was measured when only one arm could
  occur** (T015c).
- **The plan's fence table was stale by three files, and the analysis phase is what staled it.**
  Passes 1–3 added tasks touching `authenticate.middleware.ts` (8 fences, 1 appendix hunk),
  `bound-port.test.ts` (2, 1) and `attach.itest.ts` (no titled fence, so free). The standing note
  is that such a list goes stale when a chapter moves code between files; **this is a new
  variant, where it went stale because analysis found more work.** The floor is fourteen files.

**The lane was left as it was found**, which took a deliberate cleanup: the constraint probe
inserted a `ready` and a `rejected` row, and **the narrow constraint could not be restored until
they were deleted** — 043's *"a red probe writes to the lane"* in a form where the probe blocks
its own revert. Constraint back to `CHECK ((state = 'pending'::text))`, 3,053 rows all `pending`,
`attach.itest.ts` 17 of 17. The row count is up from 3,005 at the open because intervening suite
runs added rows, which is what T005 exists to re-measure.

**Task count 104 → 109.** Requirements unchanged at 26.

**On three passes.** 6 findings, 5, 4 — severity 1 CRITICAL, 0, 1. The count falls and the
CRITICAL returns, which is 057's passes 6 and 7 again. What changed each time is the question:
what the platform *does*, what it *claims about itself*, and what it *has already written down
about a chapter that does not exist yet*. Only the third required running this chapter's own
migration, and it is the only one that found a shipped test going red.

## Analysis pass 4 (2026-09-20)

Four findings — three HIGH, one MEDIUM, no CRITICAL — all four applied. The pass asked two
questions the first three had not: **does a task's own command work when run as worded**, and
**what does the specification already say this chapter's data is for?**

- **T004's `pnpm test:outsider` cannot run as worded, and its counted line is a number that means
  nothing ran.** Executed literally: `Missing: RELAY_API_URL, RELAY_WS_URL, RELAY_DEMO_CREDENTIAL`
  and **`Tests 19 skipped (19)`**. T004's own instruction is *"read each one's counted line, not
  its exit code"*, so a reader records 19 as the opening state. **And the four commands need two
  opposite arrangements** — three want the composed services stopped and this one wants them up
  with a seeded credential. T086 named the preconditions; T004 did not. 043's rule earning its
  place again: *run the command a task tells someone to run.*
- **T020a edited a migration T009 has already applied, and the Postgres runner would have skipped
  it in silence.** `schema_migrations` is `(version, applied_at)` — no checksum — where
  `analytics/apply.mjs` keys `schema_applied` on `(filename, checksum)` and **refuses** a changed
  file, which is the throw 4.2 built and 4.6 re-ran by hand. The index would never exist on the
  lane where 0018 ran and would exist on a fresh CI database, with **no test able to tell**: the
  sweep works either way, just slower. Now `0019_media_pending_age.sql`, and T055b files the
  asymmetry — **two runners in one repository giving different guarantees about the same
  mistake**, which nobody had written down. Found because analysis pass 2 added the task and pass
  4 asked what the runner would do with it.
- **The SRS already names an analytical table for this chapter's transitions, and no artifact
  mentioned it.** `docs/04-srs.md:827`: `media_events` · *"Storage metering, scan-pipeline health
  (FR-MED-12)"* · `event` in `uploaded/ready/rejected/deleted`, `kind`, `bytes`, **`processing_ms`**
  — which is SC-006's measurement. **DR-17** sums it for stored-bytes-per-tenant, two live source
  files quote DR-17, and the table has no `.sql` file. **Decided: not started here, and the reason
  is the enum rather than scope.** This chapter owns `ready` and `rejected`; `uploaded` is 4.10's
  and `deleted` is FR-MED-10's, so a producer now fills the table with **exactly the two values
  DR-17's sum does not read** — 4.6's *"a rollup over a table that receives no events"*, rebuilt
  deliberately. **And `data-model.md` §4 had argued against "a separate table" without knowing one
  was specified**; it names it now, because declining a declared table is a different sentence
  from not knowing it exists. T051a, T056a, plan open question 5 closes.
- **"Materially larger" was unquantified and the quota made it a billing question.** FR-MED-03
  says *"contradict their declaration"*; the acceptance scenario and T031 both hedged and nothing
  gave a tolerance, while the quota sums `declared_bytes` (SRS 1.17) and no task changes that — so
  any tolerance is storage a client is not billed for. **Exact, which makes the quota correct by
  construction**: for every `ready` object, `verified_bytes = declared_bytes`. T031 now tests one
  byte over and one byte under rather than a large mismatch.

**Task count 109 → 112.** Requirements unchanged at 26. Plan open questions: six, two closed.

**On four passes.** 6 findings, 5, 4, 4 — severity 1 CRITICAL, 0, 1, 0. The count has flattened
and the yield has not, because each pass changed the question rather than re-reading the
artifacts. Pass 4's two new ones were cheap: running a task's own command took minutes and found
two, and reading the SRS's **schema** table rather than its clause table found the third — a
place no requirements-to-tasks map can reach, because `media_events` appears in neither an FR nor
an SC.

**And three passes of remediation have now added work a fourth pass had to check.** T020a came
from pass 2 and tripped pass 4's migration question; the fence table went stale at pass 3 for the
same reason. The artifacts are not converging on a fixed point on their own.

## Analysis pass 5 (2026-09-20)

Four findings — three HIGH, one LOW, no CRITICAL — all four applied. The pass asked a fifth
question: **do four rounds of remediation agree with each other, and can the criteria they left
behind be measured?** Two findings are places where separately-correct fixes did not compose.

- **THREE CHECKS, AND FIVE PASSES FIXED THEIR ORDER PAIRWISE WITHOUT EVER STATING IT.** Pass 1
  moved the size comparison onto the sweep's own `HEAD`; pass 1's EICAR finding moved the scan
  ahead of the *type* check. Composed, the size verdict is knowable **before** the scan, and
  nothing said whether it short-circuits. **It does not**, and the argument is R5a's own applied
  twice: *"the mis-declared ones are the ones worth scanning"* is at least as true of an object
  declaring one byte while holding five megabytes. Reading *"every uploaded object"* to order the
  type check and ignoring it for the size check would be reading it selectively. **The cost is
  bounded by something that already exists** — streaming up to `KIND_CAPS`'s 100 MB for an object
  that will be refused, where a caller who wants 100 MB streamed can upload a valid 100 MB video.
  The order is **scan, size, type**. T039c.
- **T038 asked the health check to distinguish *running* from *has definitions* and gave no
  mechanism and no red run** — the class this project has found four times. Asked of a running
  clamd: `zPING\0` answers `PONG` and `zVERSION\0` answers
  `ClamAV 1.5.4/28129/Sun Sep 20 06:26:26 2026` — engine, signature database version, build date.
  **And bounding the reported date is what makes the check runnable red without manufacturing a
  definitionless scanner**, which is the part that turns T038 from an intention into a test.
  T038a.
- **SC-006 measures an interval whose start the platform does not observe.** *"Time from upload
  to `ready`"* — and under the sweep nobody tells the platform when the PUT finished. The store
  does, on the round trip already being made: `last-modified: Sun, 20 Sep 2026 17:02:53 GMT`,
  **at one-second resolution**, because an HTTP date has no sub-second field. **No artifact named
  that header**, and the quantisation is a cost of `research.md` R1's decision that R1 did not
  record: the client notice the sweep replaced would have given an exact instant. T044.
- **T058 named a script with no path, and that script's location has already been a defect.**
  `check-lane-scope.py` lives in a closed feature's directory, and 049 found it pointing at a
  worktree 045 deleted — reporting zero over an empty corpus with all ten controls firing. The
  only one of 112 tasks naming a command without a path; run from the right place it answers
  **61 integration files, 0 unscoped reads**.

**Three setup commands run as worded and are recorded as checked**: `pnpm check:fences`
(291 files, 55 chapters, 0 problems), the dependency counter (29 across 11 `package.json`), and
`check-lane-scope.py`. Pass 4 found the fourth broken. **And the coverage globs came back clean**
— `vitest.coverage.config.mts:122` includes `services/*/src/**/*.ts`, so the new package needs no
registry edit, and the global thresholds are 70% against a tree measuring 92.39/86.50, so partial
coverage mid-implementation cannot drag the run red. One list the fifth service does not join,
after pass 1 found three that it does.

**Task count 112 → 114.** Requirements unchanged at 26.

**On five passes.** 6 findings, 5, 4, 4, 4 — severity 1 CRITICAL, 0, 1, 0, 0. Flat at four for
three passes, with the question changing each time. **Pass 5's question was made necessary by the
four before it**: two separately-correct fixes had composed into an order nobody had written
down, and a criterion had survived a design change that removed the thing it measured. Neither is
visible by reading any single artifact, and neither is a defect in any single fix.

**The remediation is now itself a source of findings** — true at pass 4 (T020a came from pass 2)
and true again here (T022 and T039a came from pass 1). More passes of this shape would probably
keep yielding at about this rate, which is an argument for implementing rather than for
analysing: the findings left are cheaper to fix during the work than before it.
