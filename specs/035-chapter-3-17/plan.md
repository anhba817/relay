# Implementation Plan: Chapter 3.17 — the sender a message never had

**Spec**: [spec.md](spec.md) · **Research**: [research.md](research.md) ·
**Data model**: [data-model.md](data-model.md) · **Quickstart**: [quickstart.md](quickstart.md)

**Created**: 2026-08-25 · **Status**: Draft

## Summary

A message sent by a customer's own server is stored with no sender. Chapter 3.3 decided that
deliberately, when nothing read one. Three chapters since have made the sender decide what a
user may see (3.15), what a listing renders (3.16) and — next chapter — what reaches a socket.

This chapter gives a tenant a way to name its software: a **bot user** with a description, and
a sender required on every send. It amends the SRS, which has no such concept, and it breaks a
route shipped in chapter 2.2.

**It does not deliver anything to a socket.** That is chapter 3.18, split before planning
rather than after.

## Technical Context

**Language and runtime**: TypeScript, Node 22. No new language, no new service, no new
dependency.

**What is new**: two columns on `users` (`kind`, `description`) with two CHECK constraints, one
migration, one required body field on the public send, a `user` field on its response, one new
error code (`sender_not_permitted`), a fourth per-entry status on the upsert (`kind_conflict`),
and a required parameter in the repository. No new table, **no new route**, and **no change to
the protocol's frame contract** — which is the reason a bot was chosen over a nullable sender.

**What this touches that already exists**: `POST /v1/channels/:channelId/messages` (chapter
2.2), `POST /v1/users` (3.16's upsert), `POST /auth/dev-token` (3.16's implicit creation),
`repository.sendMessage` (2.2), the listing's `last_message` arm (3.16), `toFrame` (2.7), and
**46 send sites across 12 files** — three of them in the sealed outsider package.

**Scale and performance**: no new query on the send path. The service reads the named user's
row, which is one indexed lookup on `(environment_id, external_id)` — the same lookup the
route already performs for a user token since chapter 3.15.

**Testing**: the two lanes unchanged — `pnpm turbo run test` and `pnpm test:integration`, plus
`pnpm test:outsider` for the sealed suite and `pnpm coverage` for the ratchets.

**Unknowns**: none carried. R1 through R9 resolve every choice, and the two decisions left open
are stated as such: whether a person may also carry a description (R3), and whether legacy
senderless rows become renderable (FR-013).

## Constitution Check

*GATE: passed before Phase 0. Re-checked after Phase 1 — see the second table.*

| Principle | Bearing on this chapter | Verdict |
|---|---|---|
| **I. Tenant isolation is a correctness property** | The send now resolves a second identifier — the named sender — which is a new foreign-identifier surface. A bot of another tenant must be refused indistinguishably from one that does not exist. | **Pass, with a required test.** FR-009 and SC-005 put it on the isolation oracle, and the derived target list already covers the route. |
| **II. No acknowledged message is ever lost** | Untouched. This chapter changes what a message must carry, not when it is acknowledged. | Pass |
| **III. Two data paths, never crossed** | Untouched. No analytical path, no ClickHouse. | Pass |
| **IV. Single writer, single source of truth** | `users` gains two columns and stays the single source for identity. The bot is not a second identity store. | **Pass**, and R2 records the rejected `bots` table for that reason. |
| **V. API-first, developer-first** | A route shipped in chapter 2.2 changes shape. Every refusal must name its field, and the published documentation must describe the new requirement before the chapter claims delivery. | **Pass with a named cost** — see Complexity Tracking. |
| **VI. Requirement-driven, test-verified** | *"New behavior without a requirement gets a requirement first."* The SRS has no bot concept at all. | **GATE: the amendment must land first.** FR-015 and FR-016; the chapter may not cite behaviour the governing document does not contain. |
| **VII. Boring by design — scope is a commitment** | A new user kind is a scope addition to a document that says v1 has no threads, reactions or search. | **Pass, deliberately.** A bot is not a new feature surface; it is the identity an existing surface always implied. The amendment is what makes that a decision rather than a drift. |

**The gate that binds**: principle VI. The SRS amendment is not paperwork to be done at the
end — it is the thing that makes every other requirement in this chapter legitimate, and
chapters 3.15 and 3.16 spent two corrections on a traceability row that claimed a clause
delivered before it was.

## Project Structure

### Documentation (this feature)

```text
specs/035-chapter-3-17/
├── plan.md              # this file
├── spec.md
├── research.md          # R1–R9
├── data-model.md
├── quickstart.md
├── contracts/
│   ├── bot-users.md
│   └── sending.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks, not created here
```

### Source code

```text
relay-platform/
├── services/api/migrations/0013_bot_users.sql          NEW
├── services/api/src/
│   ├── db/schema.ts                users.kind, users.description, two CHECKs
│   ├── db/repository.ts            sendMessage's userId becomes REQUIRED;
│   │                               upsertUser carries kind and description
│   ├── messages/messages.schema.ts the send body gains `user`
│   ├── messages/messages.controller.ts  resolves the sender per credential class
│   ├── messages/messages.service.ts     "an application may send only as a bot"
│   ├── users/users.schema.ts       kind and description on the upsert entry
│   ├── users/users.service.ts      the kind-change refusal
│   └── auth/dev-token.controller.ts     a bot cannot be minted for
└── packages/outsider/src/integrate.itest.ts   creates a bot and sends as it

relay-tutorial/
└── app/(en)/part-3/chapter-17/<slug>/         the chapter, and its (vi) mirror

docs/04-srs.md                                 FR-USR-07 new, FR-MSG-13 AMENDED,
                                               FR-RTL-05 AMENDED, FR-MSG-15 new
docs/05-sad.md                                 users DDL: kind, description, 2 CHECKs
relay-tutorial/scripts/check-srs-ids.sh        NEW — clause identifiers, defined once
```

## The sender attributes; it does not authorise

**This is the chapter's governing distinction and it was absent from every artifact until the
seventh analysis pass.** A person's token does two things at once — it says who may act and who
is speaking — and because they always travelled together, nothing needed to name them
separately. Adding a required sender to a key-authenticated send reads naturally as *"the key now
acts as that user"*, and that reading takes a capability away from every existing integration.

    what the credential decides      WHO MAY ACT          unchanged by this chapter
    what the sender decides          WHO IS SPEAKING      new, and only this

The concrete case is a private channel. `repository.ts` gates the membership check on
`channel.type === "private" && userId !== undefined`, so a key send skips it because there is no
user — which is chapter 3.15's FR-005, delivered on purpose. Require `userId` and the gate goes
always-true, the check fires, and a bot that is not a member is refused with a 404 that by design
cannot say why. `messages.itest.ts:194` asserts the opposite in so many words.

**A key naming a bot has exactly the authority the key has today.** FR-019, FR-019a and FR-019b
carry the rule, its consequence, and the half that is easy to break while fixing the other —
a person who is not a member is still refused, and a test that only checks the bot passes if that
refusal was deleted along with the gate.

## The two counts, kept apart

Chapters 3.15 and 3.16 revised one file count eight times and the eighth revision was the one
that mattered: **what a chapter teaches is not what it must fence.** This plan keeps two
columns from the start.

| | subject — drives the word estimate | fence — drives the chain |
|---|---|---|
| files | to be enumerated at `/speckit-tasks` from the task list, then re-derived from `git diff` before the page is written | every claimed path whose state changes, including files changed only by a corrected comment |

**Neither number is estimated here.** The last feature's first count was low by 26% and its
sixth revision came from asking `git diff` rather than reading the plan. The enumeration
happens where the tasks are, and the re-derivation happens before any prose exists.

## Complexity Tracking

| What | Why it is accepted | The cheaper alternative, and why not |
|---|---|---|
| **A breaking change to a route shipped in chapter 2.2** | The route's current behaviour is the defect. A message with no sender cannot be rendered, moderated, or delivered. | A per-environment default bot keeps every caller working — and reintroduces the message whose sender nobody chose. Rejected in R4. |
| **46 send sites change, three in the sealed outsider** | The outsider is the artifact that proves an external developer can integrate. If its script does not change, the published contract did not really change. | A compatibility window. Rejected: a shim is how the anonymous send survives, and this chapter exists to remove it. |
| **`users` now holds two kinds of thing** | Everything downstream is keyed on `users.id`; a `bots` table forks membership, roles, read positions, the listing, the ban and the gauntlet. | A separate table. Rejected in R2 with the list of what it forks. |
| **An SRS amendment before delivery** | Principle VI, and the two corrections chapters 3.15/3.16 had to make for exactly this. | Ship first, amend later. That is the defect, not the shortcut. |

## Phase plan

Each phase ends in a commit. Chapter 3.12 lost work twice to `git checkout` on uncommitted
files.

| Phase | What | Ends when |
|---|---|---|
| 1 | The amendment: `FR-USR-07` new, **`FR-MSG-13` and `FR-RTL-05` narrowed in place**, `FR-MSG-15` new, the FR-MSG-01 note; the SAD's `users` DDL; `check:srs`; `sync:docs` and `check:docs` | the governing document contains the requirement and does not contradict it |
| 2 | Foundational: schema, migration `0013`, both CHECKs, **and `sendMessage`'s `userId` made required** — they merge because the signature change is what the schema exists to enforce | the compiler names every call site that omits a sender |
| 3 | US1 — the bot on the user surface: upsert takes `kind` and `description`, the kind-change refusal, the profile returns both | a tenant can create and describe a bot over the public API |
| 4 | US2 — the send: `@Accepts` declared, `user` required for an application credential, the bot-only rule, `sender_not_permitted`, the foreign-sender refusal | the route's four refusals are tested and the oracle covers the new one |
| 5 | US3 — a bot is a user and not an account: the mint refusal, membership, the listing, the ban, the deletion, the billing decision | a bot inherits everything except a credential |
| 6 | The legacy rows, on **all four** read paths including the webhook payload | FR-013 is answered the same way four times |
| 7 | The callers: 46 HTTP sites and 27 repository calls, the sealed outsider last | `pnpm test:outsider` passes without being corrected |
| 8 | Verification: every gate by exit code, the ratchets, the battery, the traceability map | SC-001 to SC-010 each have a number |
| 9–10 | The chapter and its translation | both locales, `check:fences` clean |
| 11 | Close-out: notes, gaps, `CLAUDE.md`, tags | 3.18 can start from a clean record |

**Eleven phases, not the twelve an earlier draft of this table had.** The schema and the
signature merged because one enforces the other, and the mint refusal joined US3 because "a bot
cannot authenticate" is part of what a bot *is*. The first analysis pass caught the drift
between this table and `tasks.md`.

## Constitution re-check, after Phase 1 design

| Principle | After the design | Verdict |
|---|---|---|
| I | The new foreign-identifier surface is one field on one route, covered by the derived target list that already holds it, and FR-009 puts it on the existing oracle rather than a new one. | Pass |
| IV | `users.kind` is a column on the existing single source. No second store appeared in the design. | Pass |
| V | The design adds no route and changes no frame. The only published surface that moves is one required body field, and `contracts/sending.md` states its refusals. | Pass |
| VI | Phase 1 is the amendment, before any code. | Pass, by ordering |
| VII | The design is two columns and one field. Nothing in it grows a surface the SRS does not now name. | Pass |
