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

**The users half is one line and it matters to the chapter after this one.** Eight of
eight user routes already take the identity; the only leak is the listing cursor,
which is the single live edge in ADR-37's reversal condition.

## Technical Context

| | |
|---|---|
| **Language** | TypeScript, Node.js — no new language |
| **New dependency** | **none** |
| **New service** | none |
| **New table or column** | **none** — no migration |
| **The mechanism** | an injectable pipe resolving `:channelId` at the boundary (R4) |
| **Resolution order** | shape-based, identity wins the tie (R2) |
| **Blast radius** | 6 files, 88 fence pages, 10 appendix hunks (R6) |
| **Regression surface** | **157 existing call sites** pass a uuid and must not change (R3) |
| **Unknowns** | **what replaces `users.id` in the listing cursor** — Phase 2 |

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

### VI. Requirement-driven — **FIVE BULLETS, FOUR ENGAGED**

1. *New behaviour gets a requirement first.* **FR-CHN gains a clause before the pipe
   is written**, not after — the ordering is a task, not a courtesy.
2. *100% branch coverage for tenant isolation.* The resolution's tenancy arm is in
   that population the moment it exists.
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
├── channels/channel-id.pipe.ts     NEW — the resolution, scoped by construction
├── channels/channels.controller.ts   8 @Param edits
├── messages/messages.controller.ts   5 @Param edits
├── users/users.controller.ts         1 @Param edit
├── users/users.schema.ts             the cursor payload
└── db/repository.ts                  one scoped resolution read
docs/04-srs.md · docs/05-sad.md · docs/06-adr-deep-dives.md · docs/12 · docs/07
relay-tutorial/app/(en)/part-4/chapter-22/the-identifier-the-customer-gave-it/
```

## Phases

**1 — Baseline.** Gates, lane exit codes with `Cached:` lines, the fence bill
re-derived, the CI error set, and R1–R6 re-measured.

**2 — The decisions.** The cursor's replacement and its compatibility story. Whether
an ADR is needed. Whether the identity's tie-break is written as a clause or a
comment. **Before code, because constitution VI's first bullet says so.**

**3 — The resolution (P1).** The pipe, the repository read, the 13 `@Param` edits.
Red first: an identifier that names nothing must be a named refusal.

**4 — The cursor (P2).** The users half, with the compatibility path FR-007 requires.

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
| 88 fence pages on one chapter | 13 routes contradict two clauses and a journey; the alternative was a milestone that builds, which rule 4 forbids | if the pipe turns out not to reach all 13, the design is wrong rather than the budget |
| Accepting two identifier forms | 157 call sites and every published client hold uuids | if a deprecation is ever wanted it is a later chapter with a window and a warning |
| Touching `users` at all | the cursor is ADR-37's one live reversal edge, and the chapter is about identifiers | if the cursor's replacement needs a migration, it is its own chapter |

## What this plan does not decide

- **The cursor's replacement.** A keyset tiebreak must be unique and ordered;
  `external_id` is unique per environment and the cursor is already scoped, so it is
  a candidate and not a conclusion. Phase 2.
- **Whether an ADR is written.** Predicted yes, checked at Phase 2.
- **Whether the 500's swallowed cause is ever fixed.** R1 found it, 058-3 counts 22
  routes, and fixing one of 22 is worse than recording the class.
