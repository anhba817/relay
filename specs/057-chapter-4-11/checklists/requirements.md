# Specification Quality Checklist: Chapter 4.11 — the half of the union that was refused

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

**Named artifacts are not implementation details here, and the distinction is worth stating.**
`media_not_available`, `media_objects_state_check` and `FR-MED-06` are quoted because they are
the published contract this chapter changes — the code is in a customer-facing error reference,
the constraint is what makes one of the clause's states unreachable, and neither claim survives
being paraphrased. What is absent is how any of it is built: no table shape, no route, no
library, no query.

**One assumption is flagged rather than marked.** FR-MED-06's treatment of a tenant-uploaded
object attached by a user token has two readings with different consequences for what customers
can build. The specification takes the strict one and says why, and says what the permissive one
would permit. It is an assumption rather than a `[NEEDS CLARIFICATION]` marker because a
defensible default exists and because this project settles exactly this shape in `research.md` —
`CLAUDE.md` records the pattern from the previous chapter: *"`research.md` first — it settles the
specification's one flagged assumption against the assumption."*

**SC-002 is the criterion most likely to be weakened during planning.** "Byte-identical bodies
apart from the request id" is what makes FR-005 testable; a plan that reduces it to "all three
return 422" would satisfy the letter and lose the property, which is a cross-tenant existence
oracle. The wording is deliberate.

**Two inherited gaps bound what this chapter can claim** and are named in Dependencies rather
than left to be rediscovered: a slot nobody uploaded to is indistinguishable from one that was
(`gaps.md` 056-1), and the storage quota counts declarations rather than bytes (056-2).

---

## Analysis pass 1 (2026-09-19)

Twelve findings, no CRITICAL, all twelve applied. Three came from running something rather than
reading it, and those three changed the design:

- **422 is not in the error filter's ladder.** Measured at `protocol-error.filter.ts:67-81` —
  eight rungs and 422 is not one, so FR-009's *"a status the ladder maps"* was unsatisfiable as
  written. The chapter adds the rung (FR-009a) rather than softening the clause. Nothing throws an
  unnamed 422 today, which is the argument for the rung and not against it.
- **Nothing said how the repository learns the credential class**, which the predicate's second
  clause needs. `senderMustBeBot` exists and reusing it overloads a flag named for the sender;
  T020a decides it in writing.
- **The plan's fenced-file list was six and the tasks named nine.** Counted:
  `messages.service.ts` 26 titled fences, `codes.test.ts` 17, `vitest.coverage.config.mts` 33 —
  the last two being among the most expensive files in the chain. Wrong before a line was written,
  which is the direction 050 and 056 both recorded.

And three requirements had no task: FR-013 (delivery carries nothing new), FR-012's route-level
half, and the `docs/12` row-12 amendment that four consecutive chapters wrote. The UUID tightening
was the reverse — two tasks implementing something no requirement stated, now FR-008a.

**Requirement count moved 26 → 30** (FR-008a, FR-009a, FR-017 added; SC-002, SC-010 and FR-013
sharpened) and **task count 76 → 83**. New tasks carry suffixed ids so numbering a reader has
already seen does not move.

## Analysis pass 2 (2026-09-19)

Seven findings, no CRITICAL, all seven applied. **All seven came from running something**, and the
first is larger than anything pass 1 found.

- **The union has three doors and the artifacts described one.** Zero mentions of `gateway`,
  `socket` or `frame` across all six — while `messageSendSchema` embeds `attachmentSchema` and
  `packages/protocol/src/internal.ts` imports it. A socket client can attach a `media_id` the
  moment the arm accepts, and **`session.itest.ts:415` asserts the refusal this chapter removes**,
  so it goes red on the first phase that lands. FR-001a, FR-001b, SC-002a, T032a-T032d.
- **Pass 1's own remediation left a gate red.** T011a added a generic 422 code; T010 wrote a
  section for *"the new code's"*, singular. `check-error-codes.mjs` fails in both directions.
  FR-009b, T011a0, and T010 extended.
- **The fenced-file list is eleven.** Six at pass 0, ten at pass 1, eleven now —
  `session.itest.ts` carries 9 titled whole-body fences and appeared in no artifact, because no
  artifact mentioned the socket. Wrong at every pass, in the same direction.
- **The UUID tightening is safe by ordering, not by design** (R10): no durable row carries a media
  attachment and the read paths cast rather than parse. Both are facts about timing.

**Requirement count 29 → 33** and **task count 83 → 89.**

**On yield.** Pass 1 found twelve and three came from running. Pass 2 found seven and all seven
did. The count fell and the value did not, which is what `CLAUDE.md` means by *"do not stop on
falling yield"* — and the unasked question of the same shape is what a **third** consumer would
do with a stored media attachment, which today is nobody, because none has ever been stored.

## Analysis pass 3 (2026-09-19)

Three findings, **one CRITICAL**, all three applied and all three from running something.

- **The durable reader refuses what this chapter makes the writer produce.**
  `outbox/event.ts:373,412` validate `attachments` with the same union and
  `consumer/runtime.ts:204` answers a failed parse with `message.term()`. A message a new instance
  commits and an old one reads during a rolling deploy is destroyed **after the ack** —
  constitution II. The consumer never reads the field and neither does anything downstream, so the
  strictness costs the message and buys nothing. FR-018, FR-018a, SC-002b, T017a-T017c.
  **`consumer` appeared zero times in all six artifacts**; `outbox` appeared five, every one
  meaning *"a refusal writes no outbox row"* — the sense that was already safe.
- **The lane cannot find that class**, by configuration: `RELAY_EVENT_CONSUMER=off`, and
  `outbox/event.ts`'s header records the last time — *"the api suite stayed green through 505
  tests with the defect in place."* SC-002b requires the test to fail against today's arm.
- **`attachment_count` changes meaning** (R12, FR-019, T055a). Recorded, not split: a second
  column is FR-MED-12's chapter.

**Requirement count 33 → 37** and **task count 89 → 93.** The fenced-file list is **thirteen**:
six at pass 0, ten at pass 1, eleven at pass 2, thirteen now.

**On the three passes.** Twelve findings, then seven, then three — and zero CRITICAL, then zero,
then one. Each pass asked a different question of the tree rather than re-reading the artifacts:
pass 1 asked the api, pass 2 asked which services import the union, pass 3 asked what reads it off
durable storage. **The count fell every time and the worst finding came last**, which is what
`CLAUDE.md` means by not stopping on falling yield.

## Analysis pass 4 (2026-09-19)

Three findings, no CRITICAL, one HIGH, all three applied and all three from running.

- **The synchronous reader has pass 3's defect.** `internalSendResponseSchema` is a `strictObject`
  with a required `attachments: z.array(attachmentSchema)`, and `api-client.ts:247` parses the
  api's send response with it. Old gateway, new api: the payload is refused and the socket closes
  **1011** — the schema's own comment, written by the chapter that added the field. The message is
  committed, so the client loses its acknowledgement rather than its data, and an idempotent retry
  fails identically. FR-018b, SC-002c, T017d, T017e.
- **One union has seven validators and no artifact listed them.** Four cross a deploy boundary.
  They were found one per pass — REST at pass 0, the socket frame at pass 2, the outbox at pass 3,
  the response now. FR-018c, T004a, and the table at `data-model.md` §4b.
- **An edit carries attachments forward** and nothing asserted it survives with a media arm.
  FR-020, T028b.

**Requirement count 37 → 41** and **task count 93 → 97.**

**On four passes.** 12 findings, 7, 3, 3 — severity 0 CRITICAL, 0, 1, then 1 HIGH. The count
stopped being informative after the first pass. What kept working was asking a different question
of the tree each time: the api, then which services import the union, then what reads it off
durable storage, then *enumerate every validator*. **Three of the four boundary readers were found
one pass apart, and the enumeration that would have found all of them in one command took until
pass 4 to run.** That is the finding about the method, and it is why FR-018c exists.


## Analysis pass 5 (2026-09-19)

Three findings — one HIGH, one MEDIUM, one LOW — all three applied, and **three premises that came
back clean and are recorded as evidence rather than dropped.**

- **The Part 4 chapter table lives in two documents and only one is ever amended.**
  `docs/07-tutorial-plan.md` carries the same table as `docs/12` §3 and has received none of the
  four own-row amendments chapters 4.7 through 4.10 wrote. The divergence is live, not
  hypothetical: row 11 still reads *"four distinct refusals"* where 056 established three plus
  FR-017; the section states *"The count. **It is 23**"*, a contraction behind; and *"milestones
  at 10, 18 and 23"* presents original ordinals as current, which is exactly how `CLAUDE.md` put
  hosted media at 4.5 and 4.6 until 056's eighth pass. FR-017 widened, T070b.
- **The sealed suite proves the platform from outside and this chapter was invisible to it.**
  `integrate.itest.ts:321` delivers two attachments to a socket in order — FR-001 and FR-006's
  claim exactly — and annotates the frames `attachments?: { url?: string }[]`. No 057 artifact
  contained the word *outsider*. FR-021, SC-002d, T032e, and the fenced-file table thirteen → 14.
- **`protocolCode`'s branch loses its only caller and one of two precedents was cited.** T015
  keeps it on 4.10's `service_unavailable` precedent; 4.6 reached 100/100/100/100 **by deleting**
  two unreachable arms. Both are named now, with the discriminator that decides it — this arm is
  one `params:` key from reachable and those were unreachable by construction. T015.

**Clean premises, run and recorded.** No production code branches on the attachment discriminator
— three sites, all tests, all ternaries — so the arm becoming reachable creates no exhaustive-switch
hazard. Chapter 3.18's `<ForwardRef>` makes two commitments and T008 and T010 honour both; **no gate
reads a forward reference.** And the full six-file sweep for `media_not_available` lands entirely
inside existing tasks.

**Requirement count 41 → 43** and **task count 97 → 99.**

**On five passes.** 12 findings, 7, 3, 3, 3 — severity 0 CRITICAL, 0, 1, 1 HIGH, 1 HIGH. **The
count has been flat for three passes while the findings stayed real**, which settles what passes 3
and 4 suspected: the number is not the signal, the question is. Each pass asked a new one of the
tree — the api, which services import the union, what reads it off durable storage, enumerate every
validator, and now *where does the text this chapter amends actually live*. **The first four asked
about code and found doors; the fifth asked about a document and found that four chapters had been
amending one of two copies.** That class is named twice in `CLAUDE.md` and had never been checked
here.

## Analysis pass 6 (2026-09-19)

One finding, **CRITICAL**, applied.

- **Three runtime readers of the union were absent from every artifact, and the table built to
  prevent exactly that said the schema they share is parsed by nothing.** §4b's row 7 read
  *"`packages/protocol/src/frames.ts:45` | nothing at runtime | a TypeScript type"*. That line is
  `messageSchema.attachments`, and `messageSchema` is embedded in three schemas the **gateway**
  `safeParse`s against payloads the **api** produced: `messageCreatedSchema.payload` at
  `fanout.ts:109`, `revisionFabricSchema` at `fanout.ts:98`, and `internalBackfillResponseSchema`
  at `api-client.ts:218`. Zero hits for `fanout` across all six artifacts. FR-018c corrected,
  FR-018d, SC-002e, T017f, T017g, T017h.

**What a refusal costs, per door.** The backfill one degrades the resume and loses no data. The
other two are worse than anything the previous five passes found: `logger.log("error",
"fanout.invalid_payload"); return` — **the frame is dropped after the send was acknowledged with a
201**, so a message is committed, the sender is told it worked, and no socket on that instance
receives it. Pass 4's defect cost the sender its acknowledgement while the message survived; this
one delivers nothing and says 201.

**The method finding, which is the reason this pass exists.** §4b was written at pass 4 so that
pass 5 would not have to rediscover the list, and it was built by enumerating the seven sites that
name `attachmentSchema` and asking of each *"who parses this?"* Nothing parses `messageSchema` under
that name, so row 7 came back inert. **The question that finds the other three is one level up:
what is this schema embedded in, and who parses that?** A list is worth what its question was worth,
and a wrong row in a list is worse than no list, because five passes then read past it.

**Requirement count 43 → 45** and **task count 99 → 102.** The fenced-file table went **14 → 18**,
the largest jump of any pass — `frames.ts` 10, `fanout.itest.ts` 10, `fanout.ts` 6, `revision.ts` 2
— and `internal.ts`'s `?` resolved to **26** by counting rather than scheduling the count.

**On six passes.** 12 findings, 7, 3, 3, 3, 1 — severity 0 CRITICAL, 0, 1, 1 HIGH, 1 HIGH,
**1 CRITICAL**. The count fell to one and the severity went up, which is the clearest version of
what the previous three passes suspected: **the number of findings measures the question, not the
artifacts.** Five passes asked which processes read the union; the sixth asked what the union is
*inside of*. And nothing in these three repositories runs an old protocol build against a new one —
not a lane, not a gate, not the sealed suite — so red-first tests against today's build are the only
instrument this class has.

## Analysis pass 7 (2026-09-19)

Three findings — one CRITICAL, one MEDIUM, one LOW — all three applied. The pass asked the
governing document what it requires of the thing being built, rather than asking the tree who
reads it.

- **Constitution VI's 100%-branch clause for tenant isolation was unaddressed, and the ratchet
  could not have reported it.** VI reads *"Message ordering, idempotency, and tenant isolation
  MUST have 100% branch coverage (NFR-MNT-02)"*, and this chapter's central artifact is a
  three-clause tenant-isolation predicate. The plan's principle VI row discussed only whether
  FR-MED-06's two states can be tested. Two halves, both true: the predicate is a SQL `WHERE` and
  carries **no JavaScript branches** — 048 recorded the same clause as unmeasurable because a
  sorting key has none — while the JS around it does, and those arms land in `repository.ts` at
  **branches 92** against a measured 92.66. **0.66 points of headroom means an uncovered isolation
  arm passes.** FR-023, SC-011, T050a, and the plan's row rewritten.
- **The delete path has no media test and it is where FR-MED-10's window opens.** The chapter
  tests edit and not delete. `repository.ts` nulls the column and returns `attachments: []` on all
  three tombstone sites, arm-agnostically — the argument R6 rejected for the cap. For the URL arm
  an unlink costs nothing; for this arm it is the first time unlinking strands bytes the platform
  stores and the quota counts, and it is the only orphan a customer can produce at will. FR-024,
  T028c.
- **A bare `FR-012` means two things 400 lines apart** — this feature's ten-attachment cap and
  `repository.ts:4877`'s *"deleting a message unlinks its attachments"*. Neither is in the SRS.
  The `FR-003a` class, noted where a reader of this chapter meets both, and **FR-022 was skipped
  when numbering this pass's requirements** because `frames.ts:45`'s comment already uses it.

**Clean premises.** Nothing drops attachments on a read path — ten production construction sites
pass the row through and the three that hardcode a value are all the deletion path and all say why.
The tombstone → sweep relationship was already written at `data-model.md:78`; what was missing was
the assertion, not the idea.

**Requirement count 45 → 48** and **task count 102 → 104.**

**On seven passes.** 12 findings, 7, 3, 3, 3, 1, 3 — severity 0 CRITICAL, 0, 1, 1 HIGH, 1 HIGH,
1 CRITICAL, 1 CRITICAL. Six passes asked the tree what reads the union; this one asked the
constitution what it requires. **The plan's constitution table has now been wrong twice — principle
II at pass 3, principle VI at pass 7** — and both times the row was filled when the plan was
written and never re-read against what the chapter turned out to build. A constitution check is a
measurement, and a measurement taken before the thing exists is a prediction.
