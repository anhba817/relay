# Implementation Plan: Tutorial Chapter 3.6 — "When to stop trying"

**Feature**: `specs/027-chapter-3-6` | **Spec**: [spec.md](./spec.md)
**Created**: 2026-08-18 | **Status**: Ready for `/speckit-tasks`

## Summary

Chapter 3.5 left the platform able to give up on a delivery and unable to give up
on an endpoint. This chapter adds the record of what happened to each attempt, and
the decision to stop attempting, in that order.

Three pieces of work, and they are unequal in size. The attempt record is a
publish onto a new analytics stream using data the seam has been carrying and
discarding since 3.5 shipped (research R6). The disable is two columns, a policy
function, and — because of what R1 measured — two triggers rather than one. The
test event is a route that borrows the delivery path.

Two requirements are delivered in half, on purpose, and the chapter has to say so
in the same breath it introduces them:

- **FR-WHK-06** — attempts are published, not queryable. Part 4's ingester makes
  them queryable. The publish is also allowed to be lost (R5), so "every attempt"
  is approximate.
- **FR-WHK-07** — the notification is recorded, not sent. This platform has no
  email transport, and chapter 3.7 needs one for quotas as well.

## Technical Context

**Language/Version**: TypeScript 5.x, Node.js 22 (ADR-01)
**Framework**: NestJS in the api service only (ADR-15). No framework changes.
**Data access**: Drizzle in the repository layer; migrations are hand-reviewed
forward-only SQL (ADR-16)
**Stores**: PostgreSQL for the failure run and the notification record; NATS
JetStream for the attempt event. No ClickHouse in this chapter — that is Part 4.
**New runtime dependencies**: none (constitution VII)
**New deployables**: none. The dispatcher and gateway are untouched.
**Testing**: Vitest, two lanes, coverage with per-file ratchets
**Target**: the existing compose stack; no new infrastructure

**Unknowns**: none. The two that would have blocked planning — where the attempt
log lives, and what "notified by email" means with no email — were settled before
the spec was written and are recorded in its Assumptions. R1 and R3 were settled
by arithmetic against 3.5's tier table.

## Constitution Check

Evaluated before Phase 0 and again after design. No violations to justify.

| Principle | How this feature complies |
|---|---|
| **I — Tenant isolation** | Attempt events carry `environment_id` in the subject and the payload. The notification table carries it. Every repository operation added here is environment-scoped, and the test event names an endpoint the caller must already own. |
| **II — No acknowledged message lost** | Untouched. This chapter adds no path a tenant message travels. The attempt event is explicitly allowed to be lost (R5) and is not a tenant message. |
| **III — Two data paths** | The load-bearing one. Attempts go to the analytical path as the SAD requires, on their own stream, published *after* the outcome commits so a backlogged analytics pipeline cannot stall webhook dispatch. No analytical query runs against PostgreSQL: auto-disable reads two operational columns, not the event stream. |
| **IV — Single writer** | Every write stays in the api. The dispatcher gains nothing; it does not publish the attempt event, does not know the failure run exists, and continues to reach state only over the internal seam. |
| **V — API-first** | The test event and the re-enable are HTTP routes on the versioned public API. No dashboard. |
| **VI — Test-verified** | Each new operation gets a direct test at the point it lands, not once at the end (R11). Sabotage battery per the quickstart. |
| **VII — Boring by design** | No new dependency, no new service, no new loop. The sweep rides the relay loop that already polls. |

**Post-design re-evaluation**: unchanged. The design added no store, no service and
no dependency after Phase 1.

## Project Structure

### Documentation (this feature)

```text
specs/027-chapter-3-6/
├── spec.md
├── plan.md              # this file
├── research.md          # R1–R11
├── data-model.md
├── contracts/
│   ├── attempts.md      # the analytics event and its subject grammar
│   └── webhooks.md      # test event, re-enable, disable semantics
├── quickstart.md        # V0–V9
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks
```

### Source code (repository root)

```text
relay-platform/
├── packages/protocol/src/
│   └── internal.ts                      # AMEND: analytics subject grammar
├── services/api/
│   ├── migrations/
│   │   └── 0007_webhook_attempts.sql    # NEW: columns + notification table
│   └── src/
│       ├── db/
│       │   ├── schema.ts                # AMEND: 4 columns, 1 table
│       │   └── repository.ts            # AMEND: run, disable, sweep, notify, test
│       ├── internal/
│       │   └── dispatch.controller.ts   # AMEND: publish the attempt event
│       ├── outbox/
│       │   └── jetstream.publisher.ts   # AMEND: ensure the ANALYTICS stream
│       └── webhooks/
│           ├── analytics.ts             # NEW: the attempt event publisher
│           ├── analytics.test.ts        # NEW: payload shape, no secrets
│           ├── disable.ts               # NEW: the policy, pure and testable
│           ├── disable.test.ts          # NEW
│           ├── attempts.itest.ts        # NEW
│           ├── test-event.itest.ts      # NEW
│           ├── deliveries.itest.ts      # AMEND: run lifecycle, disable, sweep
│           ├── delivery-relay.ts        # AMEND: the sweep rides the loop
│           ├── webhooks.controller.ts   # AMEND: test event, re-enable
│           └── webhooks.service.ts      # AMEND: test-event orchestration
├── packages/protocol/src/
│   └── internal.test.ts                 # AMEND: analyticsSubjectFor cases
├── scripts/
│   ├── stream-info.mjs                  # AMEND: take a stream name
│   └── webhook-walk.mjs                 # AMEND: --watch-disable
└── vitest.coverage.config.mts           # AMEND: ratchets (R11)

relay-tutorial/
├── app/(en)/part-3/chapter-06/when-to-stop-trying/{page.mdx,figures.ts}
├── app/(vi)/vi/part-3/chapter-06/when-to-stop-trying/{page.mdx,figures.ts}
└── lib/tutorial.ts                      # AMEND: 3.6 published
```

## The three pieces, in the order they should be built

**1. The attempt record.** Smallest and least entangled. The subject grammar goes
in `@relay/protocol`; the publisher module wraps the existing JetStream publisher
and ensures the new stream; `dispatch.controller.ts` calls it after the outcome
transaction returns. Nothing else depends on this, so it can land first and be
sabotaged on its own.

**2. The disable.** Columns, then a pure policy function, then the two triggers.
The policy is separated from both triggers deliberately: it is the only part with
arithmetic in it, and a pure function is the only version of it that can be tested
without a database, a clock and a broker. The on-outcome trigger goes inside the
existing transaction; the sweep goes in the relay loop.

**3. The test event.** Depends on nothing above except that a disabled endpoint
exists to test against, so it is last. It reuses expansion, signing and delivery,
with the three deviations R8 records.

## Phase 2 preview — how tasks will be shaped

Setup and the migration first, then the three pieces in the order above, each
piece ending with its own tests rather than deferring all tests to a block at the
end. Then the sabotage battery, the two lanes, coverage. Then the chapter in
English, the figures, the battery and traceability. Then the Vietnamese
translation and publication. Then the plan amendment, the quickstart run, the
credential scan, and the notes.

The one ordering constraint worth stating now: **the ratchet check happens as each
operation lands** (R11), not once at the end. Chapter 3.5 deferred it and found
four thresholds red with the chapter otherwise finished.

## Traceability

Every requirement, where it is designed and where it will be proven. Written now
so `/speckit-tasks` can hang tasks off it, and so the chapter-end traceability
check has something to check against rather than being reconstructed from memory.

| Req | Designed in | Proven by |
|---|---|---|
| FR-001 | contracts/attempts.md § Payload; research R6 | `attempts.itest.ts` — status, latency, error present for 2xx, non-2xx and timeout |
| FR-002 | contracts/attempts.md § Payload | `attempts.itest.ts` — all four identifiers on every event |
| FR-003 | research R4, R5; contracts/attempts.md § Delivery guarantee | quickstart V3 — a dead broker does not stop a delivery; sabotage 4 |
| FR-004 | contracts/attempts.md § Payload; invariant 3 | `attempts.itest.ts` — no payload, secret, signature or header in any field |
| FR-005 | research R5; contracts/attempts.md § Delivery guarantee | the chapter's own prose; battery check at chapter end |
| FR-006 | data-model.md § transitions; research R2 | `disable.test.ts` (pure policy) and `attempts.itest.ts` (the column) |
| FR-007 | research R1, R3; contracts/webhooks.md invariant 6 | `disable.test.ts` for the arithmetic; quickstart V4 end to end |
| FR-008 | data-model.md — the `enabled = true` predicate; invariant 8 | sabotage 2 — dropping the predicate must produce a second notification |
| FR-009 | data-model.md § `webhook_endpoints`; contracts/webhooks.md § representation | `attempts.itest.ts` — customer-disabled leaves `disabled_at` null |
| FR-010 | contracts/webhooks.md invariant 9 | `attempts.itest.ts` — no expansion, and scheduled rows not attempted |
| FR-011 | data-model.md § `webhook_disable_notifications` | `attempts.itest.ts` — one row, `delivered_at` null, organisation resolved |
| FR-012 | contracts/webhooks.md invariant 10 | `attempts.itest.ts` — a second endpoint keeps receiving |
| FR-013 | research R8; contracts/webhooks.md § test | `test-event.itest.ts` — including against a disabled endpoint |
| FR-014 | research R8; contracts/webhooks.md § test | `test-event.itest.ts` — signature verified by the hostile endpoint's own recipe |
| FR-015 | contracts/webhooks.md § synthetic envelope | `test-event.itest.ts` — `type` and `test` both present |
| FR-016 | contracts/webhooks.md § test response | `test-event.itest.ts` — status and latency returned for success and failure |
| FR-017 | research R9; contracts/webhooks.md § enable | `test-event.itest.ts` — all four columns null after re-enable |
| FR-018 | data-model.md; every repository operation scoped | `attempts.itest.ts` — a second environment sees nothing |
| FR-019 | — | `pnpm check:fences` reporting the locale count |
| FR-020 | research R10 (the budget counts test files) | `pnpm check:fences` HEAD check |
| FR-021 | quickstart V1–V10 | captured-output.md at chapter end |

FR-005 is the one with no test, and that is honest rather than an omission: "the
chapter says plainly that this is half-delivered" is a claim about prose, checked
by reading it. It is listed so that it cannot be quietly dropped.

## Complexity Tracking

No constitutional violations require justification. Two entries recorded because
they are judgement calls a reviewer should be able to challenge:

| Decision | Why it is not simpler | What was rejected |
|---|---|---|
| Two disable triggers instead of one | R1 measured that an outcome-only check never fires for a low-traffic endpoint: the next attempt after 35m36s is at 2h35m36s, and if the delivery dead-letters with no further events the endpoint is never disabled at all | A dedicated scheduler or cron (a third loop, constitution VII); lazy evaluation at read time (an effect that only happens when somebody looks is not an effect) |
| Idempotency logic added to a file below NFR-MNT-02's bar | Constitution VI requires 100% branch coverage for idempotency logic. The at-most-once disable is idempotency logic and lands in `repository.ts`, whose ratchet is 89. **This extends a deviation feature 024 accepted and recorded, rather than creating one** — the ratchet exists because a threshold nothing can pass teaches everyone to ignore CI. The disable path itself is small and mostly pure, so `disable.ts` carries its own 100%-branch pin and only the database-facing half sits under the inherited number | Pinning `repository.ts` at 100 now (nothing would pass, and the file is 1500 lines of inherited surface); leaving the disable path unpinned (the new idempotency logic would be the least measured code in the chapter) |
| A new `ANALYTICS` stream rather than reusing `EVENTS` | Different volume, different retention, and Part 4's ingester should consume attempts without also consuming every message event | Reusing `EVENTS` (couples retention policies); routing through the `outbox` table (puts analytical volume through the operational store, couples the two paths constitution III separates) |
