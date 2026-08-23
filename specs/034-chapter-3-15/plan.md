# Implementation Plan: chapters 3.15 and 3.16 — the surface a customer drives

**Feature directory**: `specs/034-chapter-3-15/`
**Spec**: [spec.md](./spec.md) · **Research**: [research.md](./research.md)
**Created**: 2026-08-23

## Summary

Twelve SRS clauses that were deferred across chapters 3.12 to 3.14, five schema
columns that no code reads, and four corrections to what those chapters recorded — the
fourth being a class rather than a sentence: 31 files cite the previous feature as one
chapter, and it shipped as three (FR-038a, from R17).

The work divides into **two chapters, decided on a measured file count before any
chapter prose exists** — which is the one thing chapter 3.12's close-out asks the next
feature to do differently.

**The count was revised twice before it was enumerated**, and R18 carries both
revisions. R12 counted 25 from the clause list; the task list named 29; enumerating
every path and asking which chapter fences it gives **34**, including three the tasks
imply and never name — `app.module.ts`, `users.module.ts`, `users.service.ts`. The first
of those three is why the enumeration mattered: nothing registered `UsersModule`, so
none of the eight user routes would have mounted.

**A count without an enumeration cannot be checked, and each check found more.** R18's
table is the authority for every file count in this feature, and the figures below are
read off it rather than recomputed: **20 + 20 = 40 instances, union 36, 33 taught, 7 in
both chapters, 3 in neither.** The union has been revised four times — 25, 29, 34, 36 —
each time by a new question rather than a reread, and three analysis passes produced three
wrong overlap numbers before the table existed to read from.

| Chapter | Carries | Files | ≈ prose words |
|---|---|---|---|
| **3.15** the channel a customer controls | membership enforced on send, reading a channel by id, the `private` type made meaningful, member removal, member roles, archiving | 20 | ≈ 3,200 |
| **3.16** what a user sees | channel listing with cursor pagination and activity ordering, unread counts, user profiles, bulk upsert, deletion, banning, implicit creation on authentication | 20 | ≈ 3,200 |

Both inside 2,000–4,000 with 800 words of headroom. **Three chapters would be ~2,133
each**, which clears the floor — so at the current count the arithmetic no longer argues
either way and two chapters holds on subject coherence and on ceiling headroom against an
estimate that has run low three times. Pass one reported the floor argument gone by
scaling a group sum; that was the wrong instrument, and the right one has now moved the
same way for a different reason.

## Technical Context

**Language and runtime**: TypeScript, Node 22. No new language, no new service.

**What is new**: one table (`read_positions`), three columns
(`channels.last_activity_at`, `members.role`, `users.deleted_at`), one module
(`services/api/src/users/`), two migrations, three error codes, and **fourteen routes**,
all fourteen in the two contracts — including `GET /v1/channels/:channelId`, which three
artifacts assumed existed and nothing had built (FR-003a). `tasks.md`'s route table maps
each to its handler, credential class, repository method and coverage pin.

**What is not new**: the store, the writer, the repository boundary, the credential
model, the cross-tenant suite, the fence chain, the coverage ratchets.

**The one measurement that decided a design**: ordering a user's channels by activity.
An aggregate over `messages.created_at` costs **159 ms with a sequential scan over
1,000,000 rows**; an indexed `channels.last_activity_at` costs **1.1 ms**. The test
lane could not see this — its busiest environment holds 579 messages and answered in
0.87 ms — so the number that would have settled the question was measured in a scratch
database with 2,000 channels and 1,000,000 messages (R4).

**The one design that needed no new mechanism**: the unread count.
`channels.last_sequence` is already maintained by the write path, so unread is
`greatest(last_sequence − read_position, 0)` — no counter, nothing to invalidate, and
measured no slower than a cached counter (R5).

**Unknowns**: none. Every NEEDS CLARIFICATION from the spec was resolved into R1–R18;
the one open question the spec carried — scope — was answered by the user before
planning began.

## Constitution Check

| Principle | How this feature stands against it | Gate |
|---|---|---|
| **I. Tenant isolation is a correctness property (non-negotiable)** | The membership check goes in `repository.sendMessage`, not in a controller — "isolation is enforced in data access, not in handlers", verbatim. `read_positions` carries `environment_id`, so feature 030's guard can see it and `tenant-scope.itest.ts` classifies it as `direct` rather than failing totality. The cross-tenant suite gains a **same-tenant, non-member** attack per verb, which is a case no assertion covers today: all four existing shapes take another tenant's identifiers (R10, FR-034). Every route added appears in the derived target list on the build that adds it. | Pass |
| **II. No acknowledged message is ever lost** | Nothing here touches the write path's durability. Removal and deletion both preserve messages by requirement — FR-008 and FR-028 — and FR-028 goes further than the clause: a deleted author must stay distinguishable from *no* author, because chapters 3.13 and 3.14 established that a NULL author makes a message undeliverable. | Pass |
| **III. Two data paths, never crossed** | No analytical write. `read_positions` is operational state on the operational store. The unread count is derived from `channels.last_sequence`, which the write path already maintains, so nothing new is computed on a read path that a write path could not already answer. | Pass |
| **IV. Single writer, single source of truth** | The api remains the only writer. The gateway reads a ban at connect through the api, as it already reads a session — no new table reaches the gateway. | Pass |
| **V. API-first, developer-first** | Three new error codes — `not_a_member`, `channel_archived`, `user_banned` — each a distinct fact a client acts on differently, which is the test chapter 3.14's registry sets. Sixteen codes after this feature, each with a reference section, checked in both directions by the existing `check:errors`. Every route's status code is documented (FR-039), closing chapter 3.14's gap G5 for the routes this feature touches. | Pass |
| **VI. Requirement-driven, test-verified delivery** | **46 requirements, 21 measurable outcomes** (derived 2026-08-23; four analysis passes each found this pair stale, so re-derive rather than read) — re-derive with `grep -c '^- [*][*]FR-' spec.md` and the same for `SC-`, never carried forward by hand. FR-035 is the sharpest gate: each newly-live column must be shown read by a test that **fails when the read is removed**, because chapter 3.13 found that adding a table to the guard's array is not the same as the guard watching it. The new `users` module and `read_positions` reads get per-file pins for the reason chapter 3.11's T033c gave — an unpinned file is a figure that can slide. **The quickstart clause is met by the `outsider` CI job**, which runs the README's documented sequence verbatim; `quickstart.md` here is the Spec Kit validation guide, a different artifact. **And the 100%-branch clause is answered below rather than passed over.** | Pass, with one clause answered rather than met |

**Principle VI's second clause, and where this feature stands against it.** Ordering,
idempotency and tenant isolation MUST have 100% branch coverage (NFR-MNT-02).
`repository.ts` holds all three and measures 89.51%, pinned at `branches: 90` as a
ratchet rather than a bar — the shortfall is recorded in
`specs/024-coverage-and-ci/notes.md` with the uncovered arms named.

This feature adds four branch sets to that file: the membership check, the archive
check, the ban check and the unread subtraction. **A private-channel membership check is
authorization inside a tenant, not tenant isolation**, so the clause does not reach
three of the four by its own words — but the same-tenant attack suite tests it with
FR-TEN-05's oracle, which is the reason the question is worth answering out loud instead
of leaving the classification to whoever next reads the ratchet.

The commitment: **100% branch coverage on the new arms**, whichever side of the
classification they fall on, verified per arm rather than by a file percentage
(T174a–T174c). The file's pre-existing gap is not this feature's to close and is not
enlarged by it.

**And one failure mode is pre-armed.** Chapter 3.5 added six operations to
`repository.ts` and the ratchet went red immediately — **branches 85.91% → 78.22%** —
because the new code was exercised only through the dispatcher, a child process whose
coverage is not attributable. Five tasks here test new repository code through the
gateway, which is the same arrangement. T174b exists for that.
| **VII. Boring by design — scope is a commitment** | No new service, no new language, no new dependency. One new module inside an existing service. **No ADR required, and the candidate was weighed rather than waved past**: denormalising `last_activity_at` is the kind of decision an ADR exists for, and R14 records why it is not one — a 145× measurement and no rejected architecture is a rationale, not an architecture decision. Four things larger than this feature are named and refused with owners: presence scope (FR-RTM-07), REST-to-socket delivery (FR-RTM-05), outbox retention (FR-MOD-06), and a human reading the documentation. | Pass, with four refusals recorded |

**Post-design re-evaluation**: unchanged. The design added one table, three columns and
one module, and removed no constraint. Designing the deletion path is what turned up
the third column: `users` has no deletion marker, and R7's "keep the row" needs one. The only principle whose surface moved is I, and it moved toward
the principle: the check landed in the repository layer the principle names, and the
suite gained the attack class it was missing.

## Project Structure

```
specs/034-chapter-3-15/
├── spec.md                  46 FRs, 21 SCs, 9 stories, 42 scenarios, 10 edge cases
├── research.md              R1–R18; twelve measured, one that pointed the wrong way,
│                            and one worry the measurement refuted
├── plan.md                  this file
├── data-model.md            one new table, three new columns, four state transitions
├── contracts/
│   ├── membership.md        who may act on a channel, per verb and per type
│   └── listing.md           the listing's shape, ordering and cursor
├── quickstart.md            the validation walk, V0–V16
└── checklists/
    └── requirements.md      16/16

relay-platform/
├── services/api/migrations/  + 0011 (activity column, read positions),
│                            0012 (member roles, users.deleted_at)
├── services/api/src/
│   ├── channels/            + read by id, removal, roles, archiving, the private type
│   ├── messages/            + the public send attributes its user (T031a)
│   ├── users/               NEW — module, service, controller, schema, tests
│   ├── app.module.ts        + UsersModule registered (found by R18's enumeration)
│   ├── db/                  + read_positions, last_activity_at, members.role, users.deleted_at
│   ├── isolation/           + the same-tenant fixture and its attacks
├── services/gateway/src/    + the ban check at connect
└── packages/protocol/src/   + three error codes

docs/
├── 04-srs.md                twelve clauses' verification notes
├── 07-tutorial-plan.md      the 3.15 row splits into 3.15 and 3.16
└── 08-error-reference.md    + three sections

relay-tutorial/
├── app/(en)/part-3/chapter-1{5,6}/…    two new pages
├── app/(vi)/vi/part-3/chapter-1{5,6}/… their mirrors
└── lib/tutorial.ts                     3.15 updated, 3.16 added
```

## Phases

| # | Phase | Produces | Note |
|---|---|---|---|
| 1 | Setup and baseline | `baseline.txt` with the lane, coverage, target count and the five dead columns counted before anything moves | The column count is the chapter's own headline number; measuring it after an edit measures nothing |
| 2 | Foundational — the two migrations and the schema | `0011` and `0012`, and the guard's tenth table | R15: `read_positions` has a composite key and no `id`, so it needs the key expression chapter 3.13 installed |
| 3 | US1 — membership enforced on send | the check inside `repository.sendMessage`, gated on `userId` | R1: one function, six callers inherit it |
| 4 | US1 — the private type made meaningful | `private` accepted; the by-id read check; what `public` means for a non-member, decided and tested; **FR-037's correction, in the same edit** | R3: the subscription set is not the read set, and `public` means open rather than merely readable |
| 5 | US2 — removal | the route, the per-user result shape, and the socket that stops working | FR-008: messages survive |
| 6 | US6 — member roles | `members.role` with its own CHECK, and a stated default | R8: two vocabularies, neither borrows the other |
| 7 | US7 — archiving | `archived_at` read, `channel_archived` emitted | one of the five dead columns |
| 8 | The suite — same-tenant attacks | the new fixture, one attack per verb, and each shown to fail when the check is removed | R10, FR-035 |
| 9 | **Chapter 3.15's page**, both locales | prose, fences, figures, counted | the split's first half |
| 10 | US4 — listing | cursor pagination, activity ordering | R4's column |
| 11 | US5 — unread | read positions, and the count derived from `last_sequence` | R5: no counter |
| 12 | US3, US8, US9 — the user surface | the `users` module: profile, bulk upsert, deletion, banning | three of the five dead columns |
| 13 | FR-USR-02 — implicit creation on authentication | the token route creates, converging on chapter 3.13's idempotent `createUser` | R9: the `unknown user` 400 |
| 14 | The corrections — FR-038a's citation class | R17's 40 chapter citations, classified and corrected | FR-038a/b, SC-021. **FR-037's own correction moved to phase 4**, with the edit that already touches `channels.schema.ts`: this phase runs after chapter 3.15 publishes, and a false sentence inside a fence cannot wait that long |
| 15 | Verification | every SC measured, traceability both directions, the twenty-run battery | the battery is an hour and nothing else runs on the machine |
| 16 | **Chapter 3.16's page**, both locales | prose, fences, figures, counted | the split's second half |
| 17 | Close-out | `chapter-notes.md`, the plan rows, `CLAUDE.md`, tag, push | pins last |

**The page phases sit at 9 and 16 rather than at the end**, which is the change from
chapter 3.12's shape. There the pages came last and the split was discovered while
counting them. Here the split is already decided, so each chapter's page is written
when its own work is done and its numbers are real.

## Complexity Tracking

| Thing | Why it is not simpler | What it costs |
|---|---|---|
| `channels.last_activity_at` | A derivable value, denormalised. The alternative is a sequential scan over every message in the environment on every listing — 159 ms against 1.1 ms, measured (R4). | One column, one index, and a write-path update that has to stay correct. The write path already updates `last_sequence` in the same statement, so the update is in a transaction that exists. |
| `read_positions` | The only entity here with no storage. An unread count needs to know how far a user has read, and nothing records it. | One table, and the guard's tenth entry. |
| `members.role` | FR-CHN-04 asks for roles. A role column that nothing reads would be this feature's own subject repeated, so FR-012 requires the chapter to state whether anything reads it. | One column, one CHECK, and a stated answer to "who reads this". |
| A `users` module | Five clauses need routes and no controller exists for users. Putting them on the channels controller would put user lifecycle behind a channel path. | Four new files plus a test, on the pattern `channels/` already sets. |
| Three new error codes | Each is a distinct client action: join the channel, wait for the archive to lift, contact support. Reusing `forbidden` for all three leaves a client unable to tell them apart. | Three registry entries and three reference sections, both checked. |
| `users.deleted_at` | A deleted user keeps their row, so something has to say the row is deleted. Turned up by designing the deletion path rather than by the spec (R7). | One column, and an obligation on every read of a user to decide whether a deleted one is visible to it. |
