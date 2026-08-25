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

---

## Analysis pass 4 — six findings applied, and a seventh the first one surfaced

One CRITICAL, two HIGH, two MEDIUM, one LOW. **F1 is the first product defect in four passes**
— everything before it was shapes, layers and unconsidered states.

**F1: the natural ordering trapped the customer.** `POST …/members` creates any unknown
identifier through `createUser`, which cannot set `kind`, so the row is a **person**. With an
immutable kind, *"add support-bot to #support"* followed by *"register the bot"* makes the bot
permanently impossible — and that is the order a customer follows.

Decided as FR-002d: **`person → bot` is permitted when the row has never sent a message**;
`bot → person` stays refused unconditionally. The predicate is "no messages" because that is
what immutability protects — re-labelling a human's messages as software is the harm, and a row
with no authorship has none to re-label. Memberships are deliberately *not* in the test: the
member-add is what creates the trap, so requiring none would close the escape it exists to open.

Two consequences are stated rather than discovered later. A live token for that identifier keeps
working until it expires — at most 24 hours (`MAX_TOKEN_LIFETIME_SECONDS`). And the predicate is
a filtered scan: `messages.user_id` has **no index**, and R4 measured a full message scan at
159 ms against a million rows, so T018b records the real number rather than adding an index
nothing else needs.

**And working out F1's predicate surfaced F7, which no pass had asked about.** FR-005 says no
socket opens as a bot, and it was enforced only at the mint. `POST /internal/session` resolves
the user and reads `banned_at` **without reading `kind`** — so a bot promoted while holding a
live token could open a socket for up to 24 hours. T040a closes it at the session route.

**F3 is the fourth guard this project has met that stopped meaning anything.** `sendMessage`'s
`if (userId !== undefined)` around the ban check becomes always-true the moment the parameter is
required, and its comment then describes an impossible state. The three before it —
`addMember`'s `rowCount ?? 0`, `upsertUser`'s second throw, `(row.metadata ?? {})` — were all
found *by the coverage ratchet, afterwards*. **Tightening a type makes its runtime guards dead**,
and this is the first one caught in the plan.

Checklist re-validated: 16/16. 129 tasks, all format-valid, coverage 100%.

---

## Analysis pass 5 — five findings applied

One CRITICAL, two HIGH, one MEDIUM, one LOW. **G1 is the most consequential finding of the five
passes**, not because it is the largest but because it turned a check meant to produce evidence
into one with a foregone conclusion.

**G1: T065 asked a question whose answer was already fixed, and T066 named an artifact that does
not exist.** There is **no published quickstart** — no `*quickstart*` file in `relay-tutorial` or
`docs/`, CI references none, and `relay-platform/README.md`'s walkthrough is docker-compose
commands rather than API steps. `packages/outsider` is the only place the integration steps
exist, and it is a test.

Chapter 3.14 built that suite to answer one question: can an external developer integrate on
public documentation alone? The verdict turns on the suite passing **without being corrected**,
because a correction is the assistance the criterion forbids. Add a required step — create a
bot, name it on every send — and the suite can only learn about it by being edited. T065 would
have measured nothing.

Fixed by ordering rather than by weakening the check: **T063a writes the flow into the README
before T064 touches the outsider**, because chapter 3.12's `gaps.md` names the README as one of
the three sources an outsider may read. T063b records what this chapter did *not* fix — the
absent integration guide is chapter 3.14's unmet half, and this chapter adds a step to a flow no
document describes, which makes that gap larger.

**G3 found a recorded gap that this chapter half-closes and nobody had noticed.** Chapter 3.12's
`gaps.md` G1 lists *two* independent mechanisms for "a REST-sent message reaches no socket":
nothing publishes, and the public send passes no user. This chapter removes the second. T096a
amends that record so a half-closed gap stops reading as whole — the same shape this project has
now corrected three times in traceability rows.

**G2 answered a question rather than changing anything.** `attack.ts` needs no fifth shape: the
sender is a new dimension on a route already classified `write` and already attacked, so T035's
hand-written pair is correct. Recorded because the next reader will ask.

Checklist re-validated: 16/16. 132 tasks, all format-valid, coverage 100%.

---

## Analysis pass 6 (2026-08-25)

Five findings, one CRITICAL, all applied. This pass followed the two questions pass 5 wrote down
and did not act on, and **that is where the CRITICAL came from** — a fourth mechanism to add to
the three the last feature ranked: *the questions a pass leaves open are the next pass's
highest-yield input*. Writing them down is what makes them available; pass 5 nearly didn't.

**H1: the billing question was a refusal question.** FR-018 asked whether a bot is billed as an
active user. `usage_active_users` is read twice on the send path — an insert at
`repository.ts:3874` that records usage, and a block at ~4042 that compares `count(*)` against
`caps.active_users.hard` and throws `QuotaExceededError`. **The second one refuses sends.** So a
bot does not merely cost money; on a tenant near its ceiling, the customer's own software takes
the last slot and **their next human to post that period is refused**. FR-018 forced one decision
where there were two. Split into FR-018 (billed) and FR-018a (exempt from the ceiling), answered
*billed, exempt* — the ceiling bounds a customer's human population, and a bot is their own
infrastructure.

**FR-018b is the half that would have been missed.** Exempting the bot's own send is visible and
easy; the `count(*)` the ceiling compares against must *also* exclude bots, or the bot's row
still displaces a person and nothing has been fixed. A test that watches the bot's send succeed
passes either way. T047c therefore asserts **a person sending after the bot** — the fifth entry
in this project's family of tests that were green while proving nothing.

**H2 confirmed a generalisation instead of finding an instance.** Pass 4 found `sendMessage`'s ban
check gated on a `userId !== undefined` that a required parameter makes dead, and concluded that
tightening a type makes its runtime guards dead. H2 is the second one in the same function — the
cap block's `userId === undefined` — found by grepping for the pattern. T012a now greps rather
than patching two known sites. The ratchet would have found a third one later, which is the same
finding arriving expensively.

**H3 answered the other open question and it changed nothing.** `relay-platform/README.md` is
fenced by no chapter, so T063a's edit needs no chain work and `check:fences` will not see it.
Recorded because the inverse is uncomfortable: the file an outsider is pointed at is one no
chapter teaches and no checker verifies.

**H4 and H5 were the artifacts disagreeing about whether a question was open.** `data-model.md`
described the bot-counts-as-active-user behaviour as settled while FR-018 said it must be decided;
and T047a named five assertions as the ones the decision moves when all five assert what the
counter *holds* and none assert what the ceiling *refuses*. The list that matters was empty, and
an empty list looked like coverage.

Six passes, 47 findings, 8 CRITICALs. Checklist 16/16. 134 tasks, all format-valid, coverage 100%.

---

## Analysis pass 7 (2026-08-25)

Six findings, two CRITICAL, all applied. This pass ran the command a task told someone to run,
and both CRITICALs came out of it.

**I1: requiring a sender was about to revoke a capability chapter 3.15 delivered.**
`sendMessage` gates the private-channel membership check on `channel.type === "private" &&
userId !== undefined`. A key send skips it because there is no user — that *is* 3.15's FR-005,
recorded in `channels.service.ts` as *"An application credential acts for the customer, carries
no user, and sees private channels"*. Require `userId` and the gate is always true, the check
fires, and a bot that is not a member is refused `ChannelNotFoundError` — a 404 that by design
cannot say why. `messages.itest.ts:194` is a named test asserting the opposite. **The word
"private" appeared zero times across this feature's spec, plan, tasks and research.**

The fix needed a principle, not a patch: **the sender attributes, it does not authorise.** A
person's token does both at once, which is why nothing had ever needed to name them apart. It is
now FR-019 and the opening section of `plan.md`, because a chapter that adds a sender to a
credential's send has to say what the sender does *not* mean.

**I2: the task that would have caused I1 is the one pass 6 sharpened.** Pass 6 wrote *"fix the
pattern, not the instances"* into T012a and did not run the grep. It returns **seven** hits:
three dead, one compound where half stays, two in methods whose `userId` is optional by design
(`channelVisibleTo`, `listMessages`), and the private-channel gate. T012a now carries the
classified table and the real rule — *`userId` is required in `sendMessage` and nowhere else
yet.* **A generalisation needs its own verification step.** Pass 6's own lesson was that a
written-down question is the next pass's best input; writing a command into a task and not
running it is the same mistake one level up.

**I3 turned a side effect into a decision.** Removing the ban gate makes the ban check run
against a bot's sender id for the first time — `users.banned_at` was always there. FR-005c says a
bot MAY be banned and that this is the point: a ban stops a runaway integration without deleting
the identity its messages are attributed to. Third time in two features that a removed `if`
would have shipped a feature nobody chose.

**I4 is the same rule one level down.** `repository.ts` ~3869 tells a reader *"unattributed by
design since chapter 3.3"* — the reversed decision stated as current design, inside the billing
code — and two more sites say it too. The prose inside the code is an artifact. T086c also says
to classify, because `channels.service.ts:78` says a *credential* carries no user, which stays
true.

**I5 records a divergence pass 6 created.** The billed figure counts bots, the enforced ceiling
does not, so a tenant can see "5 of 5 active users" while their people still send. Written down
as a chosen consequence rather than left to be filed as a bug.

**I6 checked a premise and it held.** T048 claims a bot's `read_positions` row is written by
nothing; the only insert is `setReadPosition` at 3345. Recorded so nobody checks it twice —
after five wrong premises in the last feature, a confirmed one is worth as much as a corrected
one.

Seven passes, 53 findings, 10 CRITICALs. Checklist 16/16. 139 tasks, all format-valid,
coverage 100%.

---

## Analysis pass 8 (2026-08-25)

Five findings applied, one CRITICAL. **Four candidates were withdrawn during verification** —
more than were kept — and the reasons matter more than the findings.

**Twice the instrument was wrong, not the artifact.** `grep -c 'sendMessage('` returns 100 and
`grep -c 'path:'` in `targets.ts` returns 41, so T014's per-file counts and the "38 targets"
baseline both looked stale. They are not. The compiler can only name the **27** call sites that
*omit* `userId`, which is exactly what T013 predicted, and the target list has 38 entries plus
three stray `path:` mentions elsewhere in the file. **Both times the grep that was easy to type
stood in for the thing being counted** — this project's own lesson about the 145× measurement,
arriving in the analysis process instead of in a benchmark.

**Twice the artifact already knew.** T009 records that the migration is hand-written, that
`drizzle-kit` emitted an unused four-migration backlog last feature, and that `migrations/meta/`
is deliberately not updated — everything the stale journal at `0007_webhook_attempts` suggested
was a problem. And T017 already requires `description` when `kind` is `bot`, which closes the
promotion path this pass opened as a CRITICAL.

**K1 survived only after being relocated.** The promotion cannot violate
`users_bot_description_check` — T017 stops it at the boundary. The **PATCH** can.
`userProfileBodySchema`'s own comment teaches the house rule — *"`null` CLEARS, and it is
distinct from absent"* — and T021 adds `description` to that schema. Follow the idiom and
`PATCH {"description": null}` nulls a bot's description, the CHECK raises, and the customer gets
a 500 for a request the boundary should have refused. FR-004b makes the field settable and not
clearable, and requires the **comment** to say so, because the comment is what would otherwise
put `.nullable()` back.

**J1 is the same shape and it is the more dangerous one.** T047b's ceiling join must filter
`kind` and must **not** filter `deleted_at` — but three `users` joins in that file pair with
`isNull(users.deletedAt)`, so the wrong version is the one a careful implementer writes.
`deleteUser` is a soft delete that leaves `usage_active_users` alone, so the filter would make
deleting users free ceiling slots. `users.itest.ts:728` pins the billed figure across a deletion;
nothing pins the enforced one.

**Two of five findings are "the defect arrives by following the local convention correctly."**
That is a new category for this project. The existing families are a guard that stopped meaning
something, a test that proves nothing, and a task premise that is false. This one is none of
them: the code is idiomatic, the reviewer nods, and the constraint fires in production. The only
defence is a comment on the exception, which is why FR-004b requires one.

J2 and J3 are bookkeeping with teeth. T047a called five assertions "exact counts" when two are
not, and one of the two is precisely the deletion invariant J1 breaks — the mislabel hid the
interaction. T012c read as though it builds a private-channel fixture when one exists whose
membership another test controls.

Eight passes, 58 findings, 11 CRITICALs. Checklist 16/16. 140 tasks, all format-valid,
coverage 100%. **Yield is falling**: pass 7 produced two CRITICALs and withdrew nothing; pass 8
produced one and withdrew four.

---

## Analysis pass 9 (2026-08-25)

Five findings, **two CRITICAL, both in Phase 1** — the amendment that principle VI makes the gate
for every other requirement, and the one artifact eight passes had taken on trust.

**M1: `FR-MSG-10` was already taken.** It is *"History responses shall include tombstones so that
clients can render deletions without gaps in ordering"* — P2, allocated, cited by the personas
table for Priya. FR-MSG runs **01 through 14**; the free identifier is **FR-MSG-15**. Six
artifacts in this feature named FR-MSG-10 and **not one of them disagreed with another** — the
contradiction lived entirely in a file none of them quoted. That is why five passes of
artifact-vs-artifact reading could not reach it, and it is chapter 3.16's *"grep the claim in
both repositories"* lesson with a different pair of files.

**M2: FR-015 named the SAD and then amended only the SRS.** `docs/05-sad.md` carries the physical
schema — `CREATE TABLE users` with eight columns, gaining two plus two CHECK constraints — and no
task touched it, while the constitution clause FR-015 *quotes* covers "the SRS or SAD" and the
last feature amended that file five times. The fix cites a precedent twelve lines below the table
it edits: `channels.type TEXT NOT NULL CHECK (type IN ('public','private'))` is the shape
`data-model.md` had already chosen for `kind` without knowing the SAD agreed.

**M3 is now a checker that exists.** `check:srs` asserts every clause identifier in
`docs/04-srs.md` is defined exactly once, wired into CI beside `check:docs`. It reports **192
clause rows, 192 unique identifiers** against the current document, and was tested by inserting
the duplicate this pass found — it fails with both line numbers and both clause texts. The
distinction it encodes: `check:docs` compares a mirror to its source and catches **drift**, and a
duplicate identifier is not drift, because both copies agree and both are wrong.

It checks uniqueness and not existence on purpose. The personas table writes `FR-MSG-07/08/10`
and the ADR notes write `FR-MOD-01→04`; a checker that parses the compressed citation form is a
checker with its own bugs, and pass 8's rule is that crying wolf on a healthy tree is how a real
problem hides.

**M4 was a suspected contradiction and is the reverse.** FR-USR-05's SRS note reads
*"`ON DELETE SET NULL` on `messages.user_id` satisfies the letter of 'preserving their messages'
and breaks delivery: the resume path drops a senderless row."* I opened it as a conflict with
SC-007; it is the SRS **rejecting** SET NULL for the same reason this chapter cares about, and it
anticipates the third of FR-012's four paths. T072 now cites it.

**On declaring convergence too early.** Pass 8 closed by calling falling yield a convergence
signal — one CRITICAL, four withdrawn candidates. Pass 9 doubled the CRITICAL count by reading
the gate task. **Falling yield measured the questions being asked, not the defects present**, and
the eight passes that never opened `docs/04-srs.md` were the reason it looked like convergence.

Nine passes, 60 findings, 13 CRITICALs. Checklist 16/16. 144 tasks, all format-valid,
coverage 100%.

---

## Analysis pass 10 and the mechanical sweep (2026-08-25)

Ten passes still landing CRITICALs is a failure of method, not a run of bad luck, and **two of
the last four were mine rather than the artifacts'**. This pass fixed four findings and then
replaced sampling with two scripts that check every claim at once.

**N1: the checker I shipped one turn earlier covered 192 of 243 clause rows.** My regex was
`(FR|NFR|CON|DR)-[A-Z]+-[0-9]+` — three parts — so it silently skipped every two-part id and
every EIR class: `DR` 17 rows, `EIR-*` 22, `CON` 6. Then it printed *"192 clause rows"*, which
reads as a complete answer. Principle VI names `EIR-*` explicitly. `check-docs-drift.sh` warns
about this exact mistake twelve lines from where I was reading — *"A range stops where it stops
for a reason nobody records"* — and `targets.ts` states the doctrine: **nothing may be exempt by
omission.** Rewritten with an explicit class list that **fails on an unknown class**, and tested
red three ways: a duplicate `FR-MSG-10`, a duplicate `DR-01` (the class the first version could
not see), and an unclassified `XYZ-01`. Green at 243/243, six classes.

Three times in three passes I reached for the pattern that matched the examples in front of me
rather than the set the rule names. Twice it was a throwaway grep; the third time it went into CI.

**N2: principle VI's quickstart clause was in violation, and nine passes filed it as a gap.**
*"The quickstart MUST run unmodified, verified by automated execution in CI against the published
documentation."* No `*quickstart*` file exists and nothing in CI names one. The automated
execution was already there — CI runs `pnpm test:outsider` in its own job — and what was missing
was published documentation for it to run against, which is what T063a writes. T063b now names
`relay-platform/README.md` the quickstart of record and makes T065's run the verification.
**A violation that predates this chapter by eight closes on work already planned.**

**N3** made `check:srs` the enforcement of a named MUST rather than a convenience: pass 9's
`FR-MSG-10` collision violated principle VI's *"never reused"*, which is a constitution conflict
and therefore CRITICAL by the analysis rules, not the inconsistency it was filed as.

### The sweep

Two scripts, committed beside the artifacts, replacing "read it again and hope":

    sweep.py            15 checks   paths, clause existence, id uniqueness both documents,
                                    FR/SC coverage by citation, task format, file:line ranges,
                                    placeholders, every `pnpm x:y` script named
    sweep-sources.py     9 checks   enumerated source attributions, cited symbols, cited
                                    columns and constraints, five numeric claims re-measured

**The sweep found one real gap: sixteen requirements whose coverage was asserted by inference.**
`FR-001`, `FR-006`, `SC-001`, `SC-010` and twelve others appeared in no task by identifier. Every
one had a covering task; none said so. Inference is exactly what missed FR-019 for seven passes,
and principle VI requires specs and plans to *reference these identifiers*. Sixteen citations
added, and coverage is now checkable rather than argued.

**And the sweep's own first version cried wolf, twice.** A fuzzy matcher over every italic-quoted
span reported 9 problems, then 8 after normalising whitespace and comment prefixes — every one a
false positive from a backtick, an apostrophe, or an emphasised phrase that was never a
quotation. It also flagged `sender_not_permitted` as a citation of nothing when T029a adds it.
A checker I could not make precise had no business sitting in the suite as a gate, so the fuzzy
pass is gone and thirteen attributions are enumerated instead, each verified by hand. That
decision is the same one `check:figures` forced last feature: 122 false problems in 193 figures
on its first run.

It did surface one thing about my own writing: FR-015e presented a paraphrase inside quotation
marks. Now the verbatim clause.

**All thirteen constitution MUST clauses reviewed, not just VI** (T004e). Eleven untouched. VI's
quickstart clause closed by T063b. FR-ANL-06's 0.1% metered-vs-operational reconciliation is
unbuilt and cites no code, so this feature cannot break it — but its entire purpose is comparing
the two counts pass 6 deliberately made different, and T047d now leaves that note. The
analytical store's no-message-text rule needed checking rather than asserting:
`webhooks/analytics.ts` carries no `description`, `displayName` or `text`.

Ten passes, 71 findings, 17 CRITICALs. Checklist 16/16. **146 tasks, all format-valid, coverage
100% by citation. Both sweeps green, `check:srs` green at 243/243.**

---

## Analysis pass 11 (2026-08-25)

Five findings, **no CRITICAL — the first pass without one.** It took a different kind of
question: ten passes examined content (does this claim hold, does this path exist), and this one
examined structure. Four structural checks, three clean, one that found twenty mismarked tasks.

**P1: `[P]` means "no shared artifact", and twenty markers were wrong.** Eight parallel-marked
tasks all wrote tests into `services/api/src/users/users.itest.ts`; three more did in phase 5;
T033/T034 shared `messages.itest.ts`; T003/T004 both added prose to `docs/04-srs.md`; and
T086/T086a/T086b/T083 all wrote the chapter page. **This project destroyed a shared fixture three
times in one feature** (3.16's T144), and pass 7 wrote a task telling T012c not to touch one —
while eight of its neighbours were cleared to write the same file concurrently. Eleven passes read
these tasks one at a time, which tells you what a task does and never whether the task beside it
opens the same file.

**P2 was a task I duplicated myself.** T025 already said *"Test that setting a bot's description
to null is refused"*; pass 10 added T021b for the same assertion without checking. Merged under
T025 — the earlier id, because principle VI does not reuse identifiers and eleven passes of
records cite by number.

**P3 is the fifth time an instrument of mine was wrong, and the second time in this pass.** The
sweep greps `pnpm ([a-z]+:[a-z]+)` across the feature's markdown, and it read the literal
`pnpm x:y` out of the checklist sentence *describing that check*. A checker that consumes its own
documentation will keep doing it, so `sweep.py` now reads only the artifacts somebody executes.

Then the collision check itself had the same bug the SRS checker had: **its extension list stopped
where it stopped.** `(ts|sql|md|sh|mts)` omitted `.txt`, so every task writing `baseline.txt` read
as "names no file", and three more collisions only appeared after the list was completed and ten
unnamed artifacts were filled in — 17 became 20. Three instruments, three passes, one mistake:
enumerating the cases in front of me instead of the set the rule names.

**P4: the ids are no longer monotonic** — `T013` precedes `T012a`, `T024` precedes `T023a`, seven
transitions in all. Not renumbered, for the same reason T025 kept its number. The header now says
file order is execution order and ids are stable labels, which closes the ambiguity in a sentence
instead of invalidating 146 citations.

**Three structural checks came back clean, and the negative results are worth as much.**
Requirement duplication: all 58 requirements compared pairwise on distinctive-term overlap, three
pairs above threshold, **all three legitimate** — a rule and its refusal, two refusals verified
the same way, a requirement and the criterion that restates it. Phase dependency: every token this
feature creates is referenced only at or after its creating phase, so no task tests something a
later phase builds. Task format: 145 of 145.

`sweep.py` now carries the collision check, the artifact-naming check and the file-order-contract
check, so none of this can drift back.

Eleven passes, 76 findings, 17 CRITICALs. Checklist 16/16. **145 tasks, 27 `[P]` markers all
verified independent, coverage 100% by citation. 18 + 9 sweep checks green, `check:srs` green at
243/243.**

---

## Analysis pass 12 (2026-08-25)

Three findings, no CRITICAL, no HIGH. **The second consecutive pass where the mechanical suite
found nothing and everything new came from a question the suite did not encode** — which is the
argument for stopping, and it is recorded here as such.

**Q1: coverage had been checked in one direction for two passes.** Pass 10 added sixteen citations
so every requirement was named by a task, called it 100%, and never ran the reverse. Sixty-four
behaviour-bearing tasks named no requirement: T008 adding the columns, T012a removing the dead
guards, T018c/T018d testing the promotion, the six caller-fixing tasks, the whole of phase 9.
`targets.ts` states the doctrine this missed — *"an entry matching no derived target fails it too
— the second direction is the one that catches a stale exemption after a rename"* — and this
project has now made the one-direction mistake at three different scales: the fence chain, the
target list, and its own coverage table. 115 of 145 tasks cite a requirement; the other 30 are
commits and measurements, which trace to nothing by design.

Doing it now also changes what T072 is. Traceability written at close-out from scratch is what
produced chapter 3.12's wrong row and 3.15's FR-CHN-05 correction; written against 115 existing
citations, it verifies instead of authors.

**Q2: two documents were called the quickstart, and one of them appears in a constitution MUST.**
`specs/035-chapter-3-17/quickstart.md` was titled *"Quickstart — validating chapter 3.17"* while
FR-015d had just named `relay-platform/README.md` the quickstart of record that principle VI's CI
clause verifies. The spec-kit artifact is now the *validation guide* and carries a note saying so.
A word that means two things is tolerable until one of the two is a gate.

**Q3: four of eleven phases had no goal** — Verification, The chapter, Translation, Close-out.
Phase 8's was the one worth writing: "Verification" covers three separate gates (the ratchets, the
derived target list, the twenty-run battery) and its title names none of them.

`sweep.py` now runs 21 checks, adding the reverse-coverage direction, the phase-goal requirement,
and an assertion that this feature's own quickstart is not titled as *the* quickstart.

### Why this is the last analysis pass

    pass    CRITICAL  HIGH   top finding
    9          2       1     a clause id collision in the gate task
    10         2       0     a constitution MUST in violation; my checker covering 79% of its document
    11         0       1     twenty [P] markers colliding on one file
    12         0       0     a traceability direction never run

Eleven passes examined the artifacts; the twelfth found that a table will be authored rather than
verified. **The highest-yield instrument left is executing the plan.** Five of the last feature's
task premises were wrong and every one was found by attempting the task — an operation the
platform lacked, an amendment that did not exist, a refusal code that was the leak it warned
about. Phase 1 is four documents and a checker. If the amendment lands clean, that is worth more
than pass 13.

Twelve passes, 79 findings, 17 CRITICALs. Checklist 16/16. **145 tasks, all format-valid, 11 of 11
phases with goals, coverage 100% forward and every behaviour-bearing task cited in reverse. 21 + 9
sweep checks green, `check:srs` green at 243/243.**

---

## Analysis pass 13 (2026-08-25)

**Pass 12 said it was the last one and recommended implementing. That was wrong**, and the way it
was wrong is worth more than the finding: the recommendation rested on two passes of falling yield,
which is a measurement of the questions being asked. Pass 13 asked the oldest question in this
project's playbook — *check a task's premise before executing it* — against Phase 1, and found the
most consequential thing since pass 10.

**R1: `FR-MSG-13` already required this, and the amendment neither cited nor amended it.**

    | FR-MSG-13 | The system shall support sending a message on behalf of any user
                  via API key, for backend-originated messages. | P2 | T |

Four rows above where `FR-MSG-15` was to be inserted. Two problems, and the second is the
serious one:

1. **It says "any user"; this chapter permits only a bot.** Adding a clause beside it would leave
   the SRS asserting both — the implicit resolution the Governance section forbids. `FR-MSG-13` is
   now narrowed in place (T002), and `FR-MSG-15` carries only the genuinely new half: that every
   message has a sender at all (T002a).
2. **It has never been delivered as written.** Chapter 3.3 satisfied a clause about naming a user
   by naming nobody, and `messages.controller.ts` has cited it that way for eleven chapters —
   *"A tenant's own server sending on a customer's behalf is FR-MSG-13, not a mistake"* — and
   again on line 43, where the same clause is the reason `MessagesController` declares no
   `@Accepts`, which is the declaration T027a adds. T002b records that the chapter **meets** the
   clause rather than introducing it.

**A requirement satisfied by doing the opposite of what it says is harder to see than one nobody
wrote.** Thirteen passes read FR-015's claim that the SRS had no such requirement.

**Why pass 9 could not find it.** Pass 9 opened this exact file and enumerated every `FR-MSG`
identifier to catch the `FR-MSG-10` collision. Enumerating identifiers answers *is this number
free* and never *does a clause already say this*. The `check:srs` I then built asserts uniqueness
and says in its own comment that it does not check existence — the right call about citations,
and it left the semantic direction unexamined. **The checker made the id question permanent and
the meaning question invisible.** T000 now has both halves, and the second one is a human read of
the section, because no checker can do it.

**R1's root cause was a policy decided once.** `research.md`'s R9 proposed *"one new clause in
each affected family, rather than editing existing ones, so the amendment is additive and the diff
shows what changed"* — a good default, never tested against §4.5's existing rows. FR-015g now says
additive-or-in-place is a decision per clause.

**R3, not fixed and recorded here:** the constitution says *"Traceability is what keeps 224
requirements coherent across four phases."* The SRS holds 192 FR+NFR, 214 with EIR, 231 with DR,
243 with CON and ASM. **224 matches no count**, and this chapter adds two. Not this feature's to
fix; T004e's constitution record is where it belongs.

Thirteen passes, 82 findings, 18 CRITICALs. Checklist 16/16. **147 tasks, coverage 100% both
directions, 21 + 9 sweep checks green, `check:srs` green at 243/243.**

---

## Analysis pass 14 (2026-08-25)

Three findings, one CRITICAL, and **all seven clause families this chapter cites are now read**.
Pass 13 found its CRITICAL by reading §4.5's clauses instead of its identifiers; this pass did the
same to the other six families and to all 21 external citations.

**S1: `FR-TEN-08` was cited three times as the billing authority and governs application
deletion.** *"Deleting an application shall irreversibly delete all associated operational data
within 30 days."* Nothing about billing, active users, or metering. The clauses that do exist:

    FR-ANL-05   meter, per tenant per day: messages sent, unique active users, ...
    FR-RTL-05   enforce configurable monthly quotas on messages sent, unique active users, ...

**Metering and enforcement, two clauses in two families, written years before this chapter — and
pass 6 spent a whole pass deriving that same split by reading `repository.ts`.** The governing
document had the answer; the feature cited a third, unrelated clause, and because that citation
existed every check passed.

**FR-RTL-05 joins FR-MSG-13 as an in-place amendment** (T002c). It enforces a quota on *"unique
active users"* with no exception and this chapter exempts bots, so the enforced dimension becomes
*unique active persons* while FR-ANL-05's metered dimension keeps counting bots. That is what makes
a bot billed and exempt at once, and it is now two clause edits rather than a paragraph in a
chapter.

**S2: `FR-RTL-08` was uncited and the exemption changes what it promises** — *"Quota exhaustion
shall degrade predictably: sends rejected with a specific error code."* A bot's send is not
rejected. Uncited, that is a defect report; cited, a decision (T002d).

**A wrong citation is worse than a missing one.** A missing one fails a coverage check. `sweep.py`
verified that every cited clause *exists*, and FR-TEN-08 exists. Pass 13 exposed this exact gap —
identifiers answer *is this free*, never *does this say what I claim* — and I fixed the instance
instead of the class: T000's semantic half covered §4.5 and left twenty other citations unread.

**Check 17 is the class fix.** `sweep.py` now pins the 28 external clauses that have been read
against the claim citing them, and a new citation fails until someone reads the clause and adds it.
Tested: inserting `FR-EMJ-02` fails with *"read the clause, then add it to REVIEWED"*. No checker
can read meaning; this one refuses a citation nobody has signed off, which is `check:srs`'s class
list one level up.

**The two families read on request, and the empty answers.** FR-AUT: **FR-AUT-09** grants the
dev-token mint *"in the `development` environment only"* and T040 refuses a bot there — **not** an
in-place amendment, because the clause grants an endpoint's existence and carries no universal
quantifier, unlike FR-MSG-13's *"any user"*. Drawing that line matters: three clauses looked alike
and only two contradict. FR-MOD: **FR-MOD-03** requires every moderation action be audit-logged and
**no audit log exists**, so a bannable bot adds no violation to a P3 clause nothing has built;
**FR-MOD-04**'s erasure endpoint is not `deleteUser`, and SC-007's claim about a deleted bot must
not be read as a claim about erasure. Also clean: **EIR-API-03**'s status set already contains 400
and 403, **EIR-API-04**'s error shape matches FR-008 and T029c, **EIR-API-07**'s OpenAPI spec
exists nowhere in the repository, and **EIR-WHK-01..05** govern transport rather than payload, so
FR-012a touches no external-interface clause. T002e records the empty answers, because the next
chapter should start from seven families read rather than one.

Fourteen passes, 85 findings, 19 CRITICALs. Checklist 16/16. **150 tasks, coverage 100% both
directions, 22 + 9 sweep checks green, `check:srs` green at 243/243.**

---

## Analysis pass 15 (2026-08-25)

Three findings, one CRITICAL. This pass closed a gap I had named in pass 10 and left open — the
SAD read past its schema section — and then found the CRITICAL somewhere no pass had looked at
all: **the published chapters.**

**T1: chapter 3.10 teaches this chapter's reversal in a `<Trap>`, and argues for it.**

    <Trap title="An unattributed send counts toward the messages and toward nobody">
    A key-authenticated REST send carries no user — unattributed by design since
    chapter 3.3, because a server-side API key is not a person. It still costs a
    message against the message quota, and it writes no membership row at all. The
    alternative, inventing a synthetic user for it, would inflate the dimension the
    customer is actually being measured on.

The title is false after FR-018 — a key send now names a bot and **is** billed as an active user
— and the body argues against the decision **on the grounds FR-018 decided the other way**. The
correction keeps the argument and adds the line it was missing: 3.10 rejected a *synthetic* user
the platform invents; a bot is a *declared* one the customer creates, names and describes. Both
locales, or the series contradicts itself in one language (T086d).

**This was reachable from pass 7 and I stopped one artifact short.** Pass 7 found
`repository.ts:3869` — *"unattributed by design since chapter 3.3 — and counts toward the message
quota and toward no user"* — and I wrote then that *"the prose inside the code is an artifact
too."* The published chapter says the same sentence **to the reader**, and I fixed the comment and
went no further. The rule on file for exactly this — fix the file that describes the thing and the
one that instructs it, then grep the claim everywhere — was applied to one repository and not to
the series.

**T2 is the structural reason it survived: no checker reads prose.** `check:fences` replays fenced
code against the platform, `check:figures` asserts a figure has a source, `check:docs` compares
mirrored documents to their canonical copies, `check:srs` reads identifiers. **A published
sentence asserting something false passes all four.** Fifteen passes read prose — all of it this
feature's own artifacts, never the published series. T086f records the asymmetry; T086e greps and
**classifies**, because this project has twice shipped a checker that stopped where its pattern
stopped, and a prose checker is exactly where crying wolf would do the most damage.

**Most of the prose is fine, and the negative results are the useful half.** `3.13:1293`
(*"toFrame drops senderless rows on purpose"*), `2.07:634`, `2.07:744` and `3.16`'s
`figures.ts:49` all stay true, because legacy rows still exist and FR-012 is why. **T3**: only
`3.13:734` also breaks, where *"only used to write an unattributed row"* is given as the reason
`sendMessage` stays on the 2.8 seam. The seam may still be right; its recorded reason is gone, and
a reason that stops being true is worse than none because the next reader trusts it.

**The SAD, finally read past the DDL.** Pass 10 admitted reading only the schema section. It states
nothing about senderless sends, and its one relevant line — *"REST send (FR-MSG-13) uses the
identical API path — one write path, two entrances"* (`05-sad.md:808`) — survives the narrowing,
because the clause still authorises REST sends and only the nameable sender changes.

**A third file bucket.** FR-020's corrections are four tutorial files that belong to neither of
`plan.md`'s two columns: not taught by 3.17, not fenced by it, prose in a published chapter that
3.17 falsifies. The last feature met the mirror image — eleven files changed by one word, giving
it **eleven fences with no subject**; here the subjects have no fence. T080 should expect three
buckets, and T085's `git diff` is what will surface them.

Fifteen passes, 88 findings, 20 CRITICALs. Checklist 16/16. **153 tasks, coverage 100% both
directions, 22 + 9 sweep checks green, `check:srs` green at 243/243.**

---

## Five passes, and where each CRITICAL came from

    1   an enumeration missing a member; a criterion that could not verify itself
        found by: reading the artifacts against each other
    2   a refusal with the wrong shape; a default in the wrong layer
        found by: reading them again, once pass 1 had made them precise
    3   a constraint colliding with an operation that already existed
        found by: asking the repository
    4   a customer's natural ordering trapping them
        found by: asking who else creates a user
    5   a check whose answer was pre-determined, and a task naming an absent artifact
        found by: checking a task's premise

**Every CRITICAL after pass 2 came from outside the artifacts**, which is the ranking the last
feature's close-out recorded: ask the repository first, read artifacts against each other second,
check task premises third. Pass 5 is this feature's first instance of the third mechanism, and
the last feature found five.
