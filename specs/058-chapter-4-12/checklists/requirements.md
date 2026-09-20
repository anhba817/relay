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

## Analysis pass 2 (2026-09-20)

One finding, HIGH, applied — and **three premises run that came back clean**, which is most of
this pass's value. Pass 1 asked the running api; this pass asked whether the query the code will
send is the query that was measured, and then what that query reads.

- **The lookup would have been the only read in the repository that crosses tenants, and its
  disjunction was unbounded.** `data-model.md` §3 described two steps with no environment
  predicate — correct, because `channelVisibleTo` refuses another tenant's channel afterwards,
  and **a query whose safety depends on a later call is a query somebody will reuse without the
  later call.** `grep -c 'environmentId, this.environmentId'` in `repository.ts` is **44**; this
  would have been the one exception. And *"every referencing channel"* without `DISTINCT` is one
  `channelVisibleTo` per MESSAGE — a query each, two when the channel is private. Rewritten as
  one joined, scoped, de-duplicated query: `Bitmap Index Scan`, **13 buffers**. T010a, T011.

**The clean premises, recorded because a premise that holds is only evidence once checked:**

- **A bound parameter uses the index.** Every figure in `research.md` came from a literal `@>`
  and the driver sends a parameter. `PREPARE p(jsonb) … EXECUTE` gives the same `Bitmap Index
  Scan` at 6 buffers. **This is the premise most likely to have silently invalidated the
  chapter's headline comparison**, and it is now in R3 and in T005.
- **Drizzle can declare the index.** 0.45.2 exposes `.using('gin', …)` and `column.op(opClass)`.
  `grep -c 'using(' schema.ts` is **0** — every index in that file today is a btree or a unique
  constraint, so this is the first and there is no local shape to copy. The exact expression is
  in T009 rather than left to be discovered.
- **The fan-out is 1 on this lane.** `max(references per media object)` is 1, so B1 costs nothing
  measurable today. The lane has never forwarded a photo, which is the only thing that produces
  a second reference — so the wrong shape would have shipped green.

**Task count 85 → 86.** Requirements unchanged at 22. The probe index was dropped before anything
else was counted.

**On two passes.** 3 findings then 1; severity 1 CRITICAL then 0. Pass 1's three were one defect
seen from three sides; pass 2's one is a posture rather than a defect — the answer was always
going to be correct, and the query would have been the only one of forty-five written the other
way round.

## Analysis pass 3 (2026-09-20)

One finding, MEDIUM, applied — plus three clean premises. The pass asked what the route needs
that no artifact mentions.

- **Nothing can be signed without `object_key`, and no artifact said where it comes from.**
  Occurrences across the feature: spec 0, plan 0, tasks 0, research 0, contract 0; one in
  `data-model.md` §1 saying nothing changes. `presign` takes a bucket and a key, and the key is
  the column `media.service.ts:92` writes at slot time. **The two implementations differ in
  whose invariant they stand on**: reading the row makes the object's `environment_id` an
  explicit check, and reconstructing `${caller_env}/${media_id}` never touches `media_objects`,
  leaving tenancy to 4.11's send-time predicate — another route, another chapter, another
  moment. The query joins the row. Measured at **16 buffers, `Index Scan using
  media_objects_pkey`, no sequential scan**, so the whole question — does the object exist here,
  what is its key, which visible channels reference it — is still one query. T010b.

**Clean premises.** T043's prediction is sound: targets derive from the running router, so a new
`@Get` appears as unclassified, and `targets.ts:414` records the eight-chapter streak it
continues. The shape vocabulary already covers this route — `read` exists with five uses and
`readAttack` compares a foreign request against an absent one, which is SC-002's property
exactly; **4.8 paid for the opposite case**, where a chapter served a body shape the helper did
not know. And no stored attachment predates 4.11, which is what makes C1 a naming problem rather
than a defect.

**Task count 86 → 87.** Requirements unchanged at 22. The probe index was dropped before anything
else was counted.

**On three passes.** 3 findings, 1, 1 — severity 1 CRITICAL, 0, 0. The count has flattened and
the severity has fallen, which on this project's evidence is not a reason to stop: the last
feature's passes 6 and 7 both found a CRITICAL after a flat run. What has changed is the kind of
question left — the api, the query and the route's inputs have each been asked once.
