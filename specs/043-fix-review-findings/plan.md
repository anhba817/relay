# Implementation Plan: Fix the platform implementation review's findings

**Branch**: `043-fix-review-findings` | **Date**: 2026-09-05 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/043-fix-review-findings/spec.md`

## Summary

Ten findings from `docs/09-platform-implementation-review-2026-09-03.md`, grouped into four
independently shippable stories: repair the test lanes first because they are the evidence
for everything else, then the two public-boundary defects, then the refusals that
misattribute fault to the platform, then the records that disagree with the tree.

Two measurements taken during research changed the design, and one of them makes a remedy
the review recommends wrong:

- **Validating webhook subscriptions against the emitted event types would refuse 741
  existing rows.** The review says to compare `event_types` with `OUTBOX_EVENT_TYPES`, and
  `gaps.md` 3.23-1 says the same. `OUTBOX_EVENT_TYPES` holds the five the platform emits;
  FR-WHK-02 declares eight; and 741 stored subscriptions name `channel.created`, which is
  declared and not yet built. Those customers made no mistake. The validation set is the
  **declared** eight, and the refusal for a declared-but-unemitted type has to say which it
  is.
- **The avatar rule rejects nothing that exists.** Every stored `avatar_url` in this database
  is either null (387,091) or `https` (586). The migration risk the review raises is real in
  principle and empty here.

Part 3 is closed, so no chapter teaches this work. Fifteen existing platform files change and
every one is fenced by a published chapter, so each carries an amendment hunk in
`relay-tutorial/fences/post-series.md`. The tutorial's own scripts are fenced by nothing,
which is where the two new gates go.

## Technical Context

**Language/Version**: TypeScript 5.x on Node.js 22, ESM throughout

**Primary Dependencies**: zod 4.4.3 (all boundary validation), NestJS (api only, ADR-15),
frameworkless `ws` (gateway), drizzle-orm confined to the repository layer (ADR-16),
`nats` 2.29.3, `ioredis`, vitest 4.1.10

**Storage**: PostgreSQL 15 on port 15432 (lane), Redis, NATS JetStream. No schema change:
this feature adds no table and no column.

**Testing**: two lanes — `*.test.ts` runs with no containers, `*.itest.ts` runs with the
compose stack. A third config, `vitest.coverage.config.mts`, runs both for the ratchet.

**Target Platform**: Linux; the full stack starts with `docker compose up`

**Project Type**: pnpm workspace of nine packages under Turborepo (ADR-17)

**Performance Goals**: no product performance target changes. The lane's own target is the
240 s integration budget, currently met at 233.08 s over green runs.

**Constraints**: every changed platform file is fenced by a published chapter, so each
change costs an amendment hunk. The two clause amendments may not permit more than the
platform already does (FR-025c).

**Scale/Scope**: **17 files, estimated, and it has already moved once.** Thirteen existing
platform files change; two are new (`packages/e2e/src/harness.itest.ts` and
`relay-platform/scripts/reset-lane.mjs`); the coverage ratchet edits
`vitest.coverage.config.mts` at close-out, which is the fourteenth existing one; and analysis
pass 2 added `services/gateway/src/limits.itest.ts`, the fifteenth, because it owns the port map
this feature changes. Chapter 3.23's
count moved from 33 to 34 during close-out and chapter 3.24's from 36 to 37, both for that same
reason. No new service, no new table, no new route.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Bearing on this feature | Verdict |
|---|---|---|
| **I. Tenant isolation** | No new data access, no new route, no repository constructor change. The webhook and avatar validations tighten input at the boundary and do not widen a read. | **Pass.** The isolation gauntlet's derived target list is unaffected because no route is added. |
| **II. No acknowledged message is lost** | The socket text bound refuses *before* acknowledgement, which is the safe direction. Nothing changes on the path after an ack. | **Pass.** |
| **III. Two data paths, never crossed** | Untouched. No analytical write, no operational read from ClickHouse. | **Pass.** |
| **IV. Single writer, single source of truth** | FR-008 exists to serve this principle: the message-length maximum is one definition consumed by three entry points instead of three literals. Same for the declared event-type set. | **Pass, and the feature advances it.** |
| **V. API-first, developer-first** | Every finding in stories 2 and 3 is a public-contract defect: a rule the contract publishes but one door does not enforce, a refusal that blames the platform for the customer's input, a close code with no page. | **Pass, and the feature advances it.** |
| **VI. Requirement-driven, test-verified** | Every requirement carries an acceptance scenario. The coverage ratchet pins `messages.schema.ts` and `attachments.ts` at 100 and will fail on an unreached arm. | **Pass**, provided the ratchet is re-run and re-pinned at close-out. |
| **VII. Boring by design — scope is a commitment** | The feature adds no capability. Three roadmap rows and the audit log are excluded by name in the spec's assumptions. | **Pass.** |

**Two clauses in the constitution bear directly on decisions this plan carries, and both
authorise them rather than merely permitting them:**

- **Technology constraints, ADR-16**: *"migrations remain versioned, forward-only,
  hand-reviewed SQL."* Retiring `drizzle-kit generate` (FR-023) is not a deviation from the
  constitution — it is the constitution's stated position, and the generator has contradicted
  it since chapter 3.9.
- **Governance**: *"where it conflicts with the SRS or SAD, the conflict MUST be resolved
  explicitly by amendment rather than ignored."* The two clause amendments (FR-025, FR-025a)
  are the procedure this document requires, not a concession granted to them.

**No violations. Complexity Tracking is empty.**

## Project Structure

### Documentation (this feature)

```text
specs/043-fix-review-findings/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
├── checklists/
│   └── requirements.md  # written by /speckit-specify
└── tasks.md             # /speckit-tasks output — NOT created here
```

### Source Code (repository root)

Three repositories. The root holds the records; `relay-platform` holds the code;
`relay-tutorial` holds the published listings and the gates.

```text
relay-platform/
├── packages/
│   ├── e2e/src/harness.ts                    FR-001, FR-002   port and teardown
│   └── protocol/src/
│       ├── frames.ts                         FR-008           socket door's bound
│       ├── internal.ts                       FR-008           internal door's bound
│       └── codes.ts                          FR-014, FR-018   new codes, close-code set
└── services/
    ├── api/src/
    │   ├── main.ts                           FR-002           log the bound port
    │   ├── messages/messages.schema.ts       FR-008           REST door's bound
    │   ├── users/users.schema.ts             FR-011, FR-012   avatar scheme
    │   └── webhooks/webhooks.service.ts      FR-014, FR-016   coded refusals
    ├── gateway/src/
    │   ├── limits.itest.ts                   FR-026           owns the lane's port map
    │   ├── main.ts                           FR-002           log the bound port
    │   ├── session.ts                        FR-009, FR-010   refuse at the socket
    │   ├── connections.test.ts               FR-024           the container-free half
    │   └── connections.itest.ts              FR-024           the broker half
    └── dispatcher/src/dispatcher.itest.ts    FR-003, FR-004   durable cleanup, policy

relay-platform/scripts/
└── reset-lane.mjs                            FR-005           new; clears broker and rows

relay-tutorial/
├── scripts/
│   ├── check-error-codes.mjs                 FR-019           close-code coverage
│   └── check-revision-order.mjs              FR-021           new
└── fences/post-series.md                     13 amendment hunks

docs/
├── 04-srs.md                                 FR-020, FR-025, FR-025a
├── 08-error-reference.md                     FR-015, FR-018
└── 09-platform-implementation-review-…md     FR-022
```

**Structure Decision**: no new package and no new service. The one new runtime file is
`relay-platform/scripts/reset-lane.mjs`, which sits beside `stream-info.mjs` — the script
that can already read the state this one clears. The two new gates live in
`relay-tutorial/scripts/`, which no chapter fences, so they cost no amendment.

## Constitution Re-check (post-design)

Re-run against the Phase 1 artifacts rather than against the summary.

| Principle | What the design added | Verdict |
|---|---|---|
| **I. Tenant isolation** | No route, no repository constructor, no query. `reset-lane.mjs` deletes lane debris and is a development script, not a service. | **Pass.** |
| **IV. Single writer** | `MESSAGE_TEXT_MAX`, `WEBHOOK_EVENT_TYPES` and `AVATAR_URL_SCHEMES` each become one definition with importers. `WEBHOOK_EVENT_TYPES` derives the emitted subset rather than sitting beside it — the shape `gaps.md` 3.23-4 records as a defect when two lists must agree and nothing compares them. | **Pass, strengthened by the design.** |
| **V. API-first** | Four contracts written, each stating what a caller sees before and after. Each new error code gets a reference section, which is NFR-USE-05. | **Pass.** |
| **VI. Test-verified** | Seven quickstart scenarios, each mapped to a success criterion, and two of them say to test the new gate **red** before believing it. | **Pass.** |
| **VII. Boring by design** | One new runtime file, `scripts/reset-lane.mjs`. No new package, service, table or route. | **Pass.** |

**The port strategy was re-decided in analysis pass 2 and kept.** Registering the e2e lane in
the hand-maintained port map and fixing only the teardown is cheaper: it closes 10 of the last
battery's 11 failures, changes no production file, and falsifies no published transcript.
It was rejected.

**Pass 5 then took half the argument away, and the decision is kept on the other half.** That
paragraph originally said the overlap was live because turbo runs the two packages at once. It
does not: `package.json:15` passes `--concurrency=1`, so `@relay/gateway` and `@relay/e2e` never
run together and nothing in the integration lane can make the harness's ports meet
`limits.itest.ts`'s range. **The overlap is latent.** With it latent, the cheaper repair closes
every failure the last battery actually produced.

What survives is not a measurement, it is the same argument FR-008 makes about three literals.
The map is a list maintained by hand that has already been wrong twice — chapter 3.21's
`gaps.md` item 4 found two missing entries, and it is still missing `packages/e2e` today, which
is how a lane came to hold three fixed ports inside a range registered to another file. **A
second list that must agree with reality is the defect this feature exists to remove** (FR-008,
and the `WEBHOOK_EVENT_TYPES` design in `data-model.md`). A range that is safe only because of a
flag in another package's script is a range somebody re-checks every time that flag moves.
Binding port 0 and reading the assignment back needs no list and no flag: `main.test.ts:19`
already does it, and `gaps.md` 3.24-4 records that a fixed port collides always under contention
while a random one collides sometimes.

**This is now a judgement rather than a forced move.** Reverting to the cheaper repair means
dropping the two entry-point changes, the harness's port change and the published-prose sweep,
and keeping the teardown fix — one paragraph here and four task lines, with no other artifact
affected.

**What that costs is paid explicitly rather than absorbed**: the lane is registered in the map
before the harness changes it, and the published prose it falsifies — a milestone transcript and
a published port map — is amended, which no gate can check.

**One design decision is worth naming because it looks like a violation and is not.**
`main.ts` in two services changes so the child logs the port it bound rather than the port it
requested. Editing production entry points for a test harness's benefit would be the wrong
trade — but the change is a correctness fix on its own terms, under the observability clause:
a log line that reports a requested value as though it were the assigned one is wrong whether
or not a test reads it.

## Complexity Tracking

No constitution violations, before or after design. This table is empty by design.
