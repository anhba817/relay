# Implementation Plan: chapter 4.22, "The identifier the customer gave it"

**Feature**: `specs/068-chapter-4-22/` · **Spec**: [spec.md](./spec.md) ·
**Research**: [research.md](./research.md)
**Created**: 2026-10-05 · **Predecessor tag**: `part4-ch21` · **Successor**: 069 / chapter 4.23

## Summary

Thirteen channel routes take an identifier Relay minted where FR-CHN-01 took the
customer's, so a customer must store a uuid to post to a channel they named. The fix
is one resolution at the request boundary; **everything downstream keeps receiving a
uuid and the ten repository methods are untouched.**

**The 500 turns out to be a failed cast** — `'order-88412'::uuid` raises in Postgres
before any `OR` can help — so the chapter's central change also removes the error,
and the two are the same edit rather than two.

**The users half may be no lines at all, and finding that out is the work.** Eight of
eight user routes already take the identity. The listing cursor every document calls
the one live edge on ADR-37's reversal condition belongs to a different route and
carries a **channel** uuid — so the chapter amends a published ADR under FR-010 and
sweeps for a real leak rather than closing the named one.

## Technical Context

| | |
|---|---|
| **Language** | TypeScript, Node.js — no new language |
| **New dependency** | **none** |
| **New service** | none |
| **New table or column** | **none** — no migration |
| **The mechanism** | an injectable pipe resolving `:channelId` at the boundary (R4) |
| **Resolution order** | shape-based; **the identity wins the tie** — the procedure is T009's, two candidates priced (R2) |
| **Blast radius** | **7 files, 101 fence pages, 17 appendix blocks / 66 hunks** (R6) — 84, then 107/9, then 88/6, now measured with its method written down; the move is `gauntlet.itest.ts`, which T031 edits |
| **Regression surface** | **173 existing call sites** pass a uuid and must not change — counted with its scope stated, after the first figure of 157 proved unreproducible (R3) |
| **Added cost** | **one scoped `SELECT` per request on all 13 routes** — the handler's own read is not replaced. Measured at T023a (R4) |
| **Unknowns** | **whether any internal key reaches a customer at all** — FR-006's sweep, Phase 4 |

## Constitution Check

Read clause by clause, because a principle's bullets do not get one verdict.

### I. Tenant isolation — **ENGAGED, AND IT IS THE REASON THE CHEAP DESIGN LOSES**

A middleware would have been 13 pages cheaper and Nest runs it **before guards**, so
it has no principal and cannot scope the lookup. **An unscoped resolution is a
cross-tenant read**, which makes this a correctness refusal rather than a preference.
The pipe takes the request-scoped `Repository`, whose constructor requires an
`environment_id` — scope by construction, 4.21's mechanism.

**And it must be probed, not read.** 4.21 found three of four scoped arms invisible
to a single-mutation probe. Deleting the scope from the resolution must turn a named
test red; if it does not, the test is missing.

### II. No acknowledged message is lost — **NOT ENGAGED.**

### III. Two data paths — **NOT ENGAGED.** No analytical surface changes.

### IV. Single writer — **NOT ENGAGED.** The resolution is a read.

### V. API-first — **ENGAGED, AND THIS CHAPTER IS ITS REPAIR.** FR-USR-01 and ADR-18
say the customer's string is the identity. Thirteen routes disagree. Nothing about
this chapter is new product; it is the API matching its own specification.

### V-ERRATA. Two claims that are narrower than they first read

**The no-5xx claim is about the CHANNEL SEGMENT.** Three of the thirteen routes take
a `:messageId` that reaches `messages.id`, a uuid column with no shape check, so
`…/messages/not-a-uuid` is a 500 the pipe does not touch. **SC-003 and FR-004 are
scoped to the channel segment**, the exclusion is asserted (T020b) and published
(T050), and fixing three of 058-3's sixteen routes is the shape that chapter already
refused.

**And the identity claim is about the PUBLIC PATH SURFACE.** Three internal doors
name a channel in a body and keep the uuid by published position; and **every
real-time frame still carries one**, so a customer holding a socket keeps the lookup
table this chapter removes from REST. The second is the bigger gap and the one most
visible to a reader: it is the gateway, `subjectForChannel`, the resume cursors and
the internal contract, which is a chapter. **V says the API is the product, and after
this one half of the product speaks the customer's language and half does not** —
published (T050), handed to 4.23 (T069), and the reason SC-007 names Stage 2 rather
than the journey.

### VI. Requirement-driven — **FIVE BULLETS, FOUR ENGAGED**

1. *New behaviour gets a requirement first.* **FR-CHN-11 is written before the pipe
   is**, not after — the ordering is a task (T027), not a courtesy. **And it is a new
   clause rather than an amendment**: FR-CHN runs 01 to 10 and none of them says a
   channel can be addressed by its customer identifier (analysis pass 7, which opened
   the SRS). Creation takes the identifier, creation is idempotent on it, and nothing
   says you may then name the channel by it. **So the behaviour has no requirement
   today**, which is what this bullet forbids, and widening a creation clause to carry
   a retrieval rule would hide that rather than fix it.
2. *100% branch coverage for tenant isolation.* The resolution's tenancy arm is in
   that population the moment it exists, **and that beats the ratchet's "pin below
   the measured value" for this one file** (T033a). The two rules contradicted each
   other for three analysis passes; the pin rule answers run-to-run drift over a
   moving denominator, which a thirty-line file does not have.
3. *The cross-tenant suite gates releases.* `gauntlet.itest.ts` must attack the new
   form: an identifier belonging to another tenant must not resolve.
4. *The quickstart runs unmodified.* Still verified by hand; zero occurrences of
   `quickstart` in `ci.yml`, restated rather than fixed.
5. *Unknown fields rejected on write endpoints.* Not engaged — a path parameter is
   not a body, and no body changes.

### VII. Boring by design — **ENGAGED, AND THE ADR QUESTION IS LIVE**

No new language, service or dependency. **An ADR is likely**: *which identifier
addresses a noun* is an architecture decision with a reversal condition, it will be
cited by every future table carrying a customer identifier, and ADR-18 is the one it
extends from users to channels. 4.21's plan predicted no ADR and was wrong; this one
predicts yes and the prediction is still worth nothing without the check.

## Project Structure

```
specs/068-chapter-4-22/
├── spec.md · plan.md · research.md (R1–R7)
├── data-model.md        the two identifier spaces and the resolution
├── contracts/
│   └── addressing.md    what each route accepts, before and after
├── quickstart.md        walk the 13 routes with a customer identifier
├── clauses.md · traceability.md · baseline.txt · gaps.md · tasks.md
```

```
relay-platform/services/api/src/
├── channels/channel-id.pipe.ts       NEW — the resolution, scoped by construction
├── channels/channels.controller.ts     7 @Param edits
├── messages/messages.controller.ts     5 @Param edits
├── users/users.controller.ts           1 @Param edit
├── users/users.schema.ts               the cursor payload
└── db/repository.ts                    one scoped resolution read

   NO MODULE FILE IS TOUCHED, AND THAT WAS MEASURED RATHER THAN ASSUMED. A
   param-level pipe class is instantiated from the module's injector without being
   in `providers`; what must be resolvable is its DEPENDENCY, and `Repository`
   already is one in all three. Analysis pass 1 reasoned the opposite from the
   module-visibility rule and would have added three files and 19 fence pages of
   work that does nothing (R4).
docs/04-srs.md · docs/05-sad.md · docs/06-adr-deep-dives.md · docs/12 · docs/07
relay-tutorial/app/(en)/part-4/chapter-22/the-identifier-the-customer-gave-it/
```

## Phases

**1 — Baseline.** Gates, lane exit codes with `Cached:` lines, the fence bill
re-derived, the CI error set, and R1–R6 re-measured.

**2 — The decisions.** The cursor's replacement and its compatibility story. Whether
an ADR is needed. Whether the identity's tie-break is written as a clause or a
comment. **Before code, because constitution VI's first bullet says so.**

**3 — The resolution (P1).** The pipe, the repository read, the 13 `@Param` edits (**7 + 5 + 1**).
Red first: an identifier that names nothing must be a named refusal.

**4 — The sweep (P2).** Enumerate what the user surface returns, state the count,
and close or record each internal key found. **Amend ADR-37 in both homes either
way** — its named exception does not exist. If the sweep finds nothing, this phase is
one document edit and the chapter says so.

**5 — The rule (P3).** The FR-CHN amendment, and the clause that tells a future noun
which identifier addresses it.

**6 — The probes.** Delete the tenancy scope and watch a named test fail. Attack the
new form from the gauntlet. Both halves of the coverage pin probe.

**7 — The documents.** SRS 1.29, ADR if Phase 2 says so, the SAD, both Part 4 tables.

**8 — The chapter.** 2,000–4,000 prose words, figures, TRAP and WHY boxes, hunks from
the checker's own replay.

**9 — The record and the close.** Battery, quickstart, push, CI per error, tag
`part4-ch22`.

## Complexity Tracking

| thing | why justified | what would make it unjustified |
|---|---|---|
| 101 fence pages on one chapter | 13 routes contradict two clauses and a journey; the alternative was a milestone that builds, which rule 4 forbids | if the pipe turns out not to reach all 13, the design is wrong rather than the budget |
| Accepting two identifier forms | 173 call sites and every published client hold uuids | if a deprecation is ever wanted it is a later chapter with a window and a warning |
| Touching `users` at all | a published ADR is falsified and FR-010 requires the amendment; and nobody has yet asked whether an internal key reaches a customer | if the sweep finds nothing and the ADR is amended, US2 is done — do not invent an edit to justify the phase |

## What this plan does not decide

- **Whether the cursor changes at all.** It carries a channel uuid every route
  accepts, so FR-006 does not reach it. Phase 4's sweep decides, and the default is
  to leave it alone.
- **The procedure behind the tie-break.** The outcome is settled — the identity wins.
  One query with an `order by` preference needs `EXPLAIN` before it is chosen (4.18);
  identity-first costs a second round trip on all 173 uuid call sites. T009.
- **Whether an ADR is written.** Predicted yes, checked at Phase 2.
- **Whether the 500's swallowed cause is ever fixed.** R1 found it, 058-3 counts 22
  routes, and fixing one of 22 is worse than recording the class.
