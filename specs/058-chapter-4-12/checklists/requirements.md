# Specification Quality Checklist: Chapter 4.12 — a link that expires, and who may hold it

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-19
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

**16 of 16, and two of them were argued rather than ticked.**

**"No implementation details" against a specification naming GIN `jsonb_path_ops`.** FR-008
requires the lookup to be indexed and the Assumptions name the index type, which is closer to
implementation than this checklist likes. It stays because **the numbers were measured before
the specification was written** and a figure without the thing that produced it is not
reproducible: 0.082 ms against 2.132 ms means nothing unless the reader knows what was built.
The requirement is *"indexed, with the before-and-after published"*; the index type is recorded
as an assumption a later chapter may overturn by re-measuring, which is the honest shape.

**"Success criteria are technology-agnostic" against SC-004, which names buffers.** Milliseconds
alone would have let a warm cache report a win that a cold one does not — 4.1 spent three
measurements learning that a delta between two totals is not a measurement of the thing that
changed. `Buffers: shared hit` is what makes the comparison a fact about the query plan rather
than about the machine, so the criterion names it.

**No `[NEEDS CLARIFICATION]` markers, and one flagged assumption instead.** The object with no
referencing message is a real hole in FR-MED-08 and the specification takes a position on it
rather than asking, for the reason 4.11 established: the same shape there was settled **against**
the specification by `research.md`, producing SRS 1.18. A flagged assumption gives research
something to attack; a clarification marker gives it something to wait for.

**What this checklist cannot say.** It cannot say whether the permissive reading is right, and
it cannot say whether ten validators is still ten now that a read path joins them — 4.11's
`data-model.md` §4b was complete when it was written and wrong two passes later. Both are
`/speckit-plan`'s and `research.md`'s to answer.


---

## Post-plan (2026-09-19)

**Research settled the flagged assumption against the specification, and the spec's Assumptions
section is now wrong on purpose.** It assumed the permissive reading — an unreferenced object
readable by its uploader — and `research.md` R1 refuses it: the permissive reading is the
parallel ACL FR-MED-08's own note forbids, and FR-MED-10 hard-deletes unreferenced objects after
24 hours, so it would be a read path to a thing already scheduled for destruction. **The spec is
left as written rather than edited back**, because the flag exists to record what was believed
before the work, and a specification retro-fitted to its own research is a document that has
never been wrong. Third feature running.

**And research found a second thing the spec did not flag**: FR-MED-08's *"channel membership"*
is not what this platform means by *authorised to read*. History checks membership for `private`
channels only. A literal implementation would be stricter than the message it guards. That is in
`plan.md`'s Complexity Tracking as the chapter's one deviation, and it may cost an SRS sentence.

**Two spec requirements are now known to be cheaper than they read**: FR-009 (say the storage
half was already built) is a citation, and FR-008's index was measured before the spec existed.
Neither is padding — they are the two places a chapter most easily claims work it did not do.

---

## Analysis pass 1 (2026-09-19)

Three findings — one CRITICAL, two HIGH — all three applied, and **all three are one defect seen
from three sides**: a value of the wrong type reaching the driver.

- **A malformed UUID path parameter is a caller-triggered 500 on shipped routes.** Measured
  against the composed api rather than reasoned about: `GET /v1/channels/not-a-uuid/messages`
  answers **500 `internal_error`**. 13 routes take `@Param("channelId")` and 3 take
  `@Param("messageId")`; **none validates**. This is 4.11's research R3, which that chapter found
  in a request BODY, measured, and fixed — while nobody looked at the path. FR-005 widened;
  T016a measures it and T016b decides in writing whether this chapter repairs the class, with the
  fence bill (thirty fences across three controllers) as the input.
- **The media controller's own pattern hands an external id where a UUID is wanted.**
  `channelVisibleTo` → `isMember` compares against a `uuid` column and external ids here are
  `tuan`, `linh`. **The silent version is the one that ships**: where a tenant's ids happen to be
  UUID-shaped no parse fails, `isMember` returns false, and every private channel refuses every
  member while every public one works. T012a, citing the two places that already do it right.
- **The private-channel member GRANT had no task.** T024 covers public-without-membership and
  T028 covers private-non-member; the only arm that reaches `isMember` was untested, and a
  refusal test passes whether the predicate is right or broken. T023a, in US1.

**No new requirement id was minted, and that is a measurement.** `FR-013` appears **58** times in
platform source, `FR-014` 39, `FR-015` 48, `SC-011` 3, `SC-012` 4. 4.11's pass 9 found the bare
feature-local namespace saturated; it still is, so FR-005 and SC-001 were widened instead.

**Task count 81 → 85.** Requirement count unchanged at 22.
