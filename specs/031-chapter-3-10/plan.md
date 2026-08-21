# Implementation Plan: Chapter 3.10 — Quotas and what they cost

**Branch**: `031-chapter-3-10` | **Date**: 2026-08-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/031-chapter-3-10/spec.md`

## Summary

Monthly usage quotas for messages sent and distinct active users, a hard cap that
refuses sends and a soft threshold that only alerts, and an email at 50%, 80% and
100% — FR-RTL-05 to FR-RTL-08, less the connection-minutes dimension, which is
chapter 3.11.

The shape research settled on:

- **Usage is a roll-up, written in the send transaction.** One row per
  `(environment_id, period)` carrying a message count, plus one membership row per
  distinct user per period. Not derived from `messages` on read: that query is
  1.189ms today and proportional to the tenant's lifetime traffic, because
  `messages` has no `environment_id` and no index on `created_at` (research R1).
- **Enforced in `Repository.sendMessage`, not in middleware.** Chapter 3.8's
  limiter never sees `/internal/messages`, which is how a WebSocket send arrives.
  `sendMessage` is the one point both routes pass through, and it already owns the
  write transaction, so the check and the increment commit together (R3).
- **No periodic sweep.** Usage rises only on a send, and the send transaction knows
  the value before and after — so it knows which thresholds it crossed and writes
  the notification rows itself. Feature 030's guard is never engaged and no file
  joins its exemption list (R5).
- **The outbox pattern a fourth time**, in a `quota_notifications` table with the
  same claim-predicate-starts-null shape as chapter 3.9's, drained by a relay,
  read in tests through Mailpit (R6).

## Technical Context

**Language/Version**: TypeScript 5.x on Node.js 22, as everywhere else in this
repository (constitution VII).

**Primary Dependencies**: NestJS for the api's HTTP surface, Drizzle as the query
engine inside the repository layer (ADR-16), `pg` for the driver, Nodemailer
through chapter 3.9's mailer, Mailpit in compose as the test mail server. Nothing
new.

**Storage**: PostgreSQL. Three schema changes — quota columns on `environments`
beside chapter 3.8's limit columns, a `usage_periods` roll-up table, a
`usage_active_users` membership table, and a `quota_notifications` outbox table.

**Testing**: Vitest. Unit tests for the threshold arithmetic and the period
function; integration tests against the compose Postgres for the roll-up, the
refusal and the relay; Mailpit reads for what an admin actually received.

**Target Platform**: Linux server, the same compose stack.

**Project Type**: web service — an existing multi-service TypeScript monorepo.

**Performance Goals**: no additional query on the request path (FR-020). The
per-request policy read that chapter 3.8 added gains three columns and a join on
two primary keys; the send transaction gains one indexed row read taken
`FOR UPDATE` alongside the channel row it already locks.

**Constraints**: usage figures must be identical across a counter-store flush
(FR-002). Sends refused while history reads and open connections are untouched
(FR-RTL-08). The threshold email must not be able to fail a send (FR-019).

**Scale/Scope**: 26,331 environments and 198,690 messages on the development
database this was measured against. One chapter, an estimated 3,000-3,600 prose
words against a 2,000-4,000 gate counted on the finished page (R12).

## Constitution Check

*GATE: passed before Phase 0, re-checked after Phase 1 design.*

| Principle | Check | Verdict |
|---|---|---|
| **I. Tenant isolation is a correctness property** | Usage rows are keyed by `environment_id`; the roll-up is read and written only through the repository layer; no handler touches the driver. Development and production environments carry independent caps and independent rows, which is FR-004 restating FR-RTL-04. | Pass |
| **II. No acknowledged message is ever lost** | A quota exceeded after a send does not un-acknowledge it: webhook delivery for accepted messages continues (FR-011). The refusal happens before the insert, never after. | Pass |
| **III. Two data paths, never crossed** | Quota state is operational, not analytical. It is written on the operational path and read from it; nothing here writes to or reads from the analytical store. | Pass |
| **IV. Single writer, single source of truth** | The single writer for a message is also the single writer for the count of messages — the same transaction, in `sendMessage`. No second process increments usage, which is why there is no reconciliation job and no drift to reconcile. | Pass |
| **V. API-first, developer-first** | The refusal carries a distinct error code, the quota, the period and the figure (FR-008). Its `docs_url` resolves to nothing, exactly as `rate_limited`'s does — inherited deliberately and recorded in R10 rather than quietly repeated. | Pass, with a named debt |
| **VI. Requirement-driven, test-verified** | Every FR maps to an acceptance scenario; the threshold email is verified by reading what Mailpit received rather than by asserting a send call (SC-004). Coverage ratchets apply as usual. | Pass |
| **VII. Boring by design — scope is a commitment** | No new language, no new dependency, no new service. The one abstraction question — a fourth outbox table versus one generic notifications table — is answered in favour of the fourth table, with the reasoning in R6. Connection-minutes is scheduled as 3.11 rather than absorbed here. | Pass |

**No violation to justify, and no ADR required.** The nearest thing to a new
concept is the fourth table with the same shape as three existing ones, which is a
repetition rather than an introduction.

## Project Structure

### Documentation (this feature)

```text
specs/031-chapter-3-10/
├── plan.md              # This file
├── research.md          # Phase 0 — R1 to R12, with the measurements
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   └── quota.md         # Phase 1 — the refusal, the email, the usage read
├── checklists/
│   └── requirements.md  # From /speckit-specify, 16/16
└── tasks.md             # Phase 2 — /speckit-tasks, not created here
```

### Source Code (repository root)

```text
relay-platform/
├── services/api/
│   ├── migrations/
│   │   └── 0009_quotas.sql              # caps, usage_periods,
│   │                                    # usage_active_users, quota_notifications
│   └── src/
│       ├── db/
│       │   ├── schema.ts                # the three tables and four columns
│       │   └── repository.ts            # usage read/increment inside sendMessage;
│       │                                # the quota admin surface for the relay
│       ├── quotas/                       # NEW — the chapter's own module
│       │   ├── period.ts                # the calendar month, one definition
│       │   ├── period.test.ts
│       │   ├── policy.ts                # thresholds crossed by an increase
│       │   ├── policy.test.ts
│       │   ├── quota.error.ts           # the refusal, and its shape
│       │   ├── quota-relay.ts           # the fourth relay
│       │   ├── quotas.module.ts
│       │   └── quotas.itest.ts
│       ├── messages/                    # controller mapping for the refusal
│       └── internal/                    # controller mapping for the refusal
└── relay-tutorial/
    └── app/(en)/part-3/chapter-10/quotas-and-what-they-cost/
        ├── page.mdx                     # and the (vi) mirror
        └── figures.ts
```

**Why a `quotas/` module rather than extending `limits/`.** They share a word and
nothing else: `limits/` is a Redis counter with a one-minute window, read in
middleware, allowed to fail open. Quotas are Postgres rows with a one-month period,
read in a transaction, and must fail closed. Putting them in one directory would
suggest a shared mechanism to the next reader, which is the mistake this chapter
opens by correcting.

## Phases

**Phase order is deliberate and the last phase is the separable one.** Three of
Part 3's four splits were discovered mid-chapter; 3.8 established that the phase
with the clearest seam goes last, so the size decision can be made against a
counted page rather than an estimate (R12).

| Phase | Content | Maps to |
|---|---|---|
| 0 | Baseline: record the lane's current timings and coverage before anything changes | — |
| 1 | The migration, the schema, and the period function | FR-001, FR-003, FR-005, FR-006 |
| 2 | **US1** — the roll-up written in the send transaction, and the flush test | FR-001, FR-002, FR-004, FR-020 |
| 3 | **US2** — the cap, the refusal, the two controller mappings, the degradation tests | FR-007 to FR-013 |
| 4 | **US3** — thresholds, the fourth table, the relay, the Mailpit reads | FR-014 to FR-019 |
| 5 | The chapter: prose, figures, fences, the Vietnamese mirror | SC-009 |
| 6 | Verification: the size count, twenty lane runs, coverage, the guard prediction | SC-001 to SC-008 |

Phase 4 is the seam. If Phase 5's count comes in over 4,000 words, the
notification story is what moves — it is the one with its own table, its own
relay and its own test surface, and it is the third time this series has taught
the outbox pattern, so a reader who stops before it has still learned the chapter's
subject.

## Complexity Tracking

| Thing | Why it is here | Cheaper alternative rejected because |
|---|---|---|
| A third and fourth table (`usage_active_users`, `quota_notifications`) | Distinct-user counting cannot be an increment (R2); the notification needs a claim predicate that survives a crash | HyperLogLog in Redis loses the month on a flush, which FR-002 forbids. Reusing `webhook_disable_notifications` is impossible — `endpoint_id` is `NOT NULL` |
| `FOR UPDATE` on the usage row inside the send transaction | Bounds the cap overshoot to one message rather than to concurrency (R8) | Without it the check is advisory. The cost is that sends to one environment serialise on one row, and Phase 6 measures that rather than assuming it is acceptable |
| The refusal raised in the repository layer, mapped in two controllers | `sendMessage` is the only point both send routes pass through (R3) | A second middleware over `/internal` would move the check outside the transaction and still miss any future caller |
