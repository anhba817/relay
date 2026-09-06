# Implementation Plan: A reconnecting client can tell it missed a revision

**Branch**: `044-revision-watermark` | **Date**: 2026-09-06 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/044-revision-watermark/spec.md`

## Summary

A per-channel revision counter, raised inside the transaction that applies an edit or a
deletion, reported at reconnect so a client can tell which of its channels hold revisions it
has not seen. SRS FR-016a already says the stale copy is repairable by re-reading history; nothing
tells a client to do it.

**Four measurements taken during research decided the design, and two of them changed it:**

- **The route the counts ride already exists and already carries two precedents.**
  `/internal/session` returns `channel_ids` in one call at connect, and both `banned` and
  `limits` were added to that response for the stated reason that "the gateway has no database
  and must not gain one". The counts take the same seat. **FR-014 is satisfied by an existing
  route rather than by optimising a new one.**
- **The resume cursor cannot carry a third field.** `resume.ts:62` splits on the LAST colon,
  deliberately — *"channel ids are opaque to the gateway and a colon inside one must not
  silently truncate it."* A `<channel>:<seq>:<rev>` cursor would parse `rev` as the sequence.
  A parallel `rev` parameter was the answer, was built, and was **removed**: the ack carries
  every count, so the client compares against its own and sends nothing. The rsplit rule stays
  intact by not being extended.
- **`cursorSchema` cannot express this.** It is
  `z.record(z.string(), z.number().int().positive())`, and every channel that has never been
  revised has a count of **zero**. Reusing it would make an unrevised channel unrepresentable
  and force absent-means-zero at the schema layer, which FR-007 needs to distinguish.
- **The edit and delete paths do not touch the channel row.** The send path does, and its
  comment says the activity column therefore "costs an extra assignment rather than an extra
  round trip". Here it costs one UPDATE per revision, in the transaction that already exists.

**One gap in the specification surfaced and is resolved below**: a client that presents a
cursor but no counts. FR-007 covers a first connection; this is a pre-upgrade client resuming,
which is a different case and the common one for a deploy window.

## Technical Context

**Language/Version**: TypeScript 5.x on Node.js 22, ESM throughout

**Primary Dependencies**: zod 4.4.3 (all boundary validation), NestJS (api only, ADR-15),
frameworkless `ws` (gateway), drizzle-orm confined to the repository layer (ADR-16), `ioredis`,
vitest 4.1.10

**Storage**: PostgreSQL 15 on port 15432 (lane), Redis, NATS JetStream. **One schema change**:
a column on `channels`, migration `0015`, hand-written and reviewed against SAD §6.1 — the
generator was retired in feature 043.

**Testing**: two lanes — `*.test.ts` runs with no containers, `*.itest.ts` runs with the compose
stack. A third config, `vitest.coverage.config.mts`, runs both for the ratchet.

**Target Platform**: Linux; the full stack starts with `docker compose up`

**Project Type**: pnpm workspace of nine packages under Turborepo (ADR-17)

**Performance Goals**: SC-004 — reconnecting 10,000 clients stays within 10% of a baseline
**taken on this lane immediately before the first code change**, not quoted from
`docs/11-scalability-measurement-2026-09-06.md`. SC-005 — a revision stays within 10% of its
current cost, measured the same way. Those published figures came from one gateway on a 28-core
host with the load generator beside it; a criterion that names them is one nobody can check
anywhere else.

**Constraints**: the gateway holds no database and must not gain one. The counts must reach it
on a call it already makes. Part 3 is closed, so every changed platform file that a chapter
fences carries an amendment hunk in `relay-tutorial/fences/post-series.md`.

**Scale/Scope**: **12 files, estimated, and feature 043's estimate missed by a factor of
three.** That estimate counted the fix and not the verification, so this one names what it
cannot see: the count excludes whatever the lane finds when the battery runs.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Bearing on this feature | Verdict |
|---|---|---|
| **I. Tenant isolation** | The count is read on a route that already resolves the caller's memberships and returns only their channels. No new read path, no new route, no repository constructor change. | **Pass.** The isolation gauntlet's derived target list is unaffected — no route is added. |
| **II. No acknowledged message is lost** | Nothing on the path after an ack changes. The counter rises inside the transaction that already commits the revision, so a revision that commits and a count that rises are the same event. | **Pass, and the feature advances it** — a revision that was invisible to a reconnecting client becomes discoverable. |
| **III. Two data paths, never crossed** | Untouched. No analytical write, no operational read from ClickHouse. | **Pass.** |
| **IV. Single writer, single source of truth** | The count has one writer — the revision transaction — and one definition. FR-011 keeps sends out of it, so the column means one thing. | **Pass.** |
| **V. API-first, developer-first** | The count appears in a response a customer's client reads, so it is contract. FR-012 requires it documented and FR-013 amends the two clauses that describe the limit so the remedy sits beside it. | **Pass, and the feature advances it.** |
| **VI. Requirement-driven, test-verified** | Every requirement carries an acceptance scenario. The ratchet pins the files this feature changes at close-out. | **Pass**, provided the ratchet is re-run and re-pinned. |
| **VII. Boring by design — scope is a commitment** | No new service, no new route, no new fabric. Replaying revisions and message-granular cursors are excluded by name in the spec's Out of Scope. | **Pass.** |

**Two constitution clauses bear directly and both authorise rather than merely permit:**

- **Technology constraints, ADR-16**: *"migrations remain versioned, forward-only,
  hand-reviewed SQL."* Migration `0015` is written by hand because feature 043 retired the
  generator and `migrations.test.ts` now fails if it returns.
- **Governance**: *"where it conflicts with the SRS or SAD, the conflict MUST be resolved
  explicitly by amendment rather than ignored."* FR-013's amendment of SRS FR-016a and SRS FR-016b is
  that procedure, not a concession to it.

**No violations. Complexity Tracking is empty.**

## Project Structure

### Documentation (this feature)

```text
specs/044-revision-watermark/
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
├── packages/protocol/src/
│   ├── frames.ts                          FR-004    revisionCountSchema, the ack's field
│   ├── internal.ts                        FR-014    the counts ride /internal/session
│   └── frames.test.ts                                the ack accepts zero; cursorSchema does not
└── services/
    ├── api/
    │   ├── migrations/0015_*.sql          FR-001    the column
    │   └── src/
    │       ├── db/schema.ts               FR-001    the column, in the model
    │       ├── db/repository.ts           FR-002/3  two transactions, one statement each
    │       ├── db/repository.itest.ts               the counter's tests
    │       └── internal/
    │           ├── session.controller.ts  FR-004    fills channel_revisions
    │           └── memberships.controller.ts        maps the widened rows back to ids
    └── gateway/src/
        ├── resume.ts                      FR-005    where the `rev` parameter is NOT
        ├── session.ts                     FR-006    compare, and fill the ack
        └── session.itest.ts                         the four cursor/rev combinations

docs/04-srs.md                             FR-013    amend SRS FR-016a and SRS FR-016b
docs/05-sad.md                             FR-012    §5.2, where the resume protocol is described
```

**Fifteen platform files and two documents, and the estimate has already moved twice.** It
read twelve until analysis: the second pass widened the repository task to repair **both** callers of
`channelsForUser` rather than one, which added `session.controller.ts` and
`memberships.controller.ts`; the third found `docs/05-sad.md` missing and
`limits.itest.ts` listed here without any task touching it.
`vitest.coverage.config.mts` makes sixteen at close-out, the way it made chapter 3.23's 33
become 34 and 3.24's 36 become 37.

**Feature 043 estimated seventeen and changed fifty-eight**, because a plan counts the fix and
not the verification. This one has moved 12 → 15 before a line of code was written, which is
the same effect arriving earlier.

**Which of them are fenced was measured**, and `baseline.txt` records it in two columns: eight of
nine changed platform files are fenced — `repository.ts` by 23 chapters, `internal.ts` by 11 —
and **`session.itest.ts` is published only as `(excerpt)`**, so an edit to it is invisible to
`check:fences` and carries no hunk. Thirteen files are in that state repository-wide.

## Phases

The plan named no phases until `sweep.py` compared it with `tasks.md` and found six against
zero. A plan that leaves its reader to derive the shape from the task list is one the task list
cannot be checked against.

**Phase 1 — Setup.** The lane, the two performance baselines, the fence audit in two columns,
and the gate set. Nothing here changes code, and the baselines have to exist before it does.

**Phase 2 — Foundational: the counter.** The migration, the column, both revision transactions,
and the membership query that carries the count. Blocking: every story reads this column. It
ends green only if both callers of the widened query are repaired in the same phase.

**Phase 3 — User Story 1: the signal.** Protocol shape first, then the internal response, then
the build that makes both visible, then the two consumers. The build is not optional — the
package resolves through `dist`.

**Phase 4 — User Story 2: bounded repair.** Mostly verification of US1's design, plus the
channel a client joined during its absence.

**Phase 5 — User Story 3: the published obligation.** SAD §5.2 and the two SRS clauses.

**Phase 6 — Polish and close-out.** Coverage, the ratchet, the battery, the gaps ledger, and
the records.

## Complexity Tracking

Empty. No principle is violated and no deviation is proposed.
