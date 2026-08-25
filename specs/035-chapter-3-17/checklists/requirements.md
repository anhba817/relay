# Specification Quality Checklist: Chapter 3.17 — the sender a message never had

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-25
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

**This spec was rewritten twice, and both rewrites came from the user rather than from
analysis.** The record is kept because the rejected versions were not obviously wrong.

**First shape — "the api publishes".** One missing arrow, which `docs/05-sad.md`'s C4 diagram
already draws. Research corrected two carried claims: the gap is one cause and not the two
chapters 3.12 and 3.13 recorded, because chapter 3.15 closed the other without anyone
noticing; and `public-surface.itest.ts` pins the application-credential path only, which is
narrower than its name.

**Second shape — "deliver with a null sender".** Rejected. It looked cheaper than a new
concept: `MessageWithSender.user` is already `string | null` and the REST read path already
returns null, so the socket frame was the outlier. What it could not answer is what a client
renders for nobody — and it required a published protocol change that every client parsing
frames would have to tolerate.

**Third shape — the bot user, and it is the one specified.** The frame contract stops changing
entirely, the cost moves from the protocol to the user model, and a message that a customer's
software sent arrives with something a person can read.

**Two things fell out of the third shape that neither of the first two had surfaced:**

1. **An impersonation surface.** Requiring a sender forces the question of *which* senders a
   credential may name. "Any user" means an API key can post as any human in the tenant, which
   the platform never had while sends were anonymous. FR-007 forbids it.
2. **The SRS has no bot concept at all** — not in FR-USR, not in the SAD. FR-015 and FR-016
   require an explicit amendment before delivery is claimed, which is the constitution's own
   Governance procedure and the defect chapters 3.15/3.16 corrected twice in chapter 3.12's
   traceability map.

**Scope was the last open marker and is now closed: two chapters, split before planning.**
3.17 is the sender; 3.18 is the fan-out; presence moves to 3.19. Chapter 3.12 was specified as
one chapter and shipped as three, and 3.15 as one and shipped as two — both split *late*,
after the fences were written. This one splits on purpose, and the seam is clean: the delivery
chapter opens with "every message now has a sender" instead of building a user model first.

**On "no implementation details":** the spec cites `messageSchema`, `users.metadata`,
`public-surface.itest.ts` and chapter 3.3's comment. Retained deliberately — this is a
specification for a tutorial chapter about a specific codebase, and the series' convention
since chapter 3.10 is that a spec names the artifact whose behaviour it changes. A reader who
cannot see which decision is being reversed cannot check the claim.

---

## Analysis pass 1 — ten findings, all applied

Two CRITICAL, three HIGH, four MEDIUM, one LOW. The two that matter:

**C1 — the enumeration named three read paths and there are four.** FR-012 listed history, the
listing and the resume; it omitted the **webhook payload**, which is `MessageCreatedData` on a
customer's own HTTPS endpoint. FR-WHK-03 retries a failed delivery for two hours, so an event
for a legacy senderless message can arrive after this chapter ships — and it is the only
consumer of the sender that leaves the platform. Fixed as FR-012a and T054a/T054b.

**C2 — the feature's strongest guarantee had no way to be verified.** SC-003 asked that no write
path can produce a senderless message *"shown by removing each guard and watching a test go
red"*, and the mechanism is a required parameter: remove it and everything compiles, nothing
fails. Split into SC-003a (a `typecheck` transcript) and SC-003b (a real removal test), with the
reason stated — a compile-time check can never have a failing test, so it needs different
evidence rather than an exemption from FR-035's doctrine.

**And one finding was half wrong, corrected before it was applied.** M1 claimed T047 and T051
were both decisions with no requirement. T051 traces to FR-013 and always did; only the billing
decision lacked a clause, and it is now FR-018. Checking a finding before acting on it is the
same discipline the last feature applied to five wrong task premises.

**H1 produced a new error code.** `403 forbidden` for "a key may not post as a person"
contradicts the registry's own comments, which reject `forbidden` by name twice. The refusal is
the third instance of a shape the registry already has — wrong class, wrong service, and now
wrong **kind of user** — so it becomes `sender_not_permitted`, and `codes.test.ts`'s exact-set
assertion will fail on the build that adds it, which is the instrument working.

Checklist re-validated after the edits: 16/16, no new markers.

---

## Analysis pass 2 — eight findings, all applied

Two CRITICAL, two HIGH, three MEDIUM, one LOW — and **both CRITICALs were the same defect,
made by this design and already solved elsewhere in the platform.**

**D1 and D2: the design did not distinguish *absent* from *a value equal to the default*.**

- D1 specified a kind change as `400 invalid_request, field: "users.N.kind"` — the shape zod
  produces. zod cannot see the stored row, so the rule cannot be a validation failure, and a
  400 would fail a batch of 100 because of entry 7. That is the outcome chapter 3.16's
  per-entry array was built to prevent. It is now a fourth status, `kind_conflict`, in a 200.
- D2 defaulted `kind` to `'person'` in the request schema. Compare that default against a
  stored bot and every upsert editing a bot's description without restating `kind: "bot"` reads
  as a demotion — making a bot uneditable through the route FR-004 says can edit it.

Chapters 3.15 and 3.16 built exactly this distinction for the profile patch — *absent keeps its
value, present-and-null clears it* — and `exactOptionalPropertyTypes` is on for it. The pattern
was in the repository and this design did not reach for it.

**Neither was findable in pass 1.** Both required asking what shape a refusal takes on the wire
and what an upsert that omits a field does — questions that became askable only because pass 1
sharpened "refused" into a status, a code and a field path.

**D7 corrected reasoning of my own that was wrong.** Pass 1 wrote into the contract and into
T040 that a bot's mint refusal must be byte-identical to an unknown identifier's, on chapter
3.16's enumeration argument. Two things are wrong with it: an unknown identifier answers **200**
on that route (3.16 made it create a person), so there is nothing to be identical to; and the
enumeration argument's premise does not hold, because `POST /auth/dev-token` and
`GET /v1/users/:externalId` are both `@Accepts("application")` — a caller who reaches the
refusal can already read that user's `kind`. The argument was carried from a neighbouring route
without checking whether its premise applied.

**D3 found five assertions the billing decision moves** — `quotas.itest.ts:71,78,103` and
`users.itest.ts:723,728` all pin exact active-user counts — with no task updating them either
way.

Checklist re-validated: 16/16, no new markers. 116 tasks, all format-valid.

---

## Analysis pass 3 — six findings, all applied

One CRITICAL, two HIGH, two MEDIUM, one LOW. **The CRITICAL is the first finding in three
passes that is a design hole rather than a mis-specification.**

**E1: deleting a bot collided with the constraint that defines one.** `deleteUser` clears
profile data — `display_name`, `avatar_url`, `metadata`. If `description` is profile data it is
cleared too, and `CHECK (kind <> 'bot' OR description IS NOT NULL)` rejects the UPDATE, so **a
bot could not be deleted at all**. Both halves were correct on their own; nothing in spec, plan,
data-model or tasks had put them in the same sentence. T044 asserted a bot *can* be deleted and
would have been the test that failed.

Decided as FR-004a: **a description is not profile data.** A deleted bot's messages stay
attributed to it, and a reader asking "what was this thing that posted in March" needs the
description to still be there. The rejected alternative — clearing `kind` back to `'person'`
first — makes the deletion two writes and leaves a person nobody created holding messages a bot
sent. T043b keeps `description` out of the `set` clause *with a comment*, so the omission is not
tidied away later, and T044a asserts the decision rather than the bug.

**Where the finding came from matters.** Passes 1 and 2 asked *"do these documents agree?"* and
found things stated wrongly. E1 came from asking *"what happens when this chapter's constraint
meets last chapter's operation?"* — answerable only against the repository. That is the record's
top-ranked mechanism, above artifact-versus-artifact reading, and three passes in the artifacts
largely agree with each other while the boundary with existing code still yields.

**E2 was run as a sweep rather than a finding.** Pass 2's D3 found five billing assertions
one at a time; this pass enumerated **every** `toEqual({…})` and `Object.keys(…)` over a response
the feature touches — 29 sites — and found **two** that break: `users.itest.ts:503` and `:760`.
The field-level `.toBe(…)` assertions in the same file survive. The number is recorded so the
next feature greps once instead of discovering them one per pass.

**E3 found an asymmetry nobody had looked for**: the send response names five fields and no
sender, while the internal send's response carries `user` and history returns it. A caller now
*required* to name a sender got no confirmation of which one was recorded.

Checklist re-validated: 16/16. 121 tasks, all format-valid, coverage 100%.
