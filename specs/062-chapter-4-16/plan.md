# Implementation Plan: Chapter 4.16 — "Storage on the bill"

**Branch**: `062-chapter-4-16` | **Date**: 2026-09-29 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/062-chapter-4-16/spec.md`

## Summary

FR-MED-12 wants stored bytes metered per tenant per day. The quota half is already built —
4.10's level read, with 4.15's renditions counting — so what is missing is the history, and
DR-17 already states the technique: a daily rollup summing `media_events` deltas, reconciled
weekly against an object-storage inventory.

Three things make that harder than it reads. **The precedent has never carried data**:
`storedMessages` is a correct query over `daily_usage_v2`, and `message_events` holds 0 rows
with no producer. **The column that looks like this one is not**: `stored_delta` counts stored
messages. And **the negative arm has almost no producer** — nothing deletes a `media_objects`
row, so until the erasure chapter ships the level only rises and the reconciliation agrees for
a reason that will stop being true.

The plan builds the producer and the rollup first, because they are reachable and everything
reads them; then the reconciliation, whose inventory turned out to be one signer change away
rather than a new capability; then the per-kind counts. What the chapter publishes is the
trade DR-17 already made on the platform's behalf: a summed level is not self-correcting, and
one lost delta costs between 1 kB and 25 MB depending which object it was, for ever.

## Technical Context

**Language/Version**: TypeScript 5.x on Node.js 22, ES modules.

**Primary Dependencies**: none new. The api's analytics publisher, the ingester's consumer,
ClickHouse and MinIO all exist. This is the first Part 4 chapter since 4.10 to add no
dependency, and the count stays at 32.

**Storage**: ClickHouse — `media_events` (new), `daily_usage_billing` gains
`stored_bytes_delta` and per-kind upload counts, fed by a third materialised view. Postgres is
unchanged: the quota's level read is already correct. MinIO gains a listing call.

**Testing**: vitest. New unit coverage in `packages/protocol` and `services/ingester`;
integration in `services/api` and `services/ingester`; the reconciliation exercised against the
real store.

**Target Platform**: Linux containers under `docker compose`; CI is the superproject's.

**Project Type**: A tutorial chapter whose deliverable is a published page in `relay-tutorial`
plus the `relay-platform` commits it fences, tagged `part4-ch16`.

**Performance Goals**: the rollup read must not scan raw events (DR-10), measured against
accumulating the same answer from `media_events`. The inventory listing is 48 ms and 377 kB per
1,000 keys; nine pages for the lane, against 11.5 s to head every object.

**Constraints**: constitution III — the operational path must not depend on the analytical
store, so emitting a delta cannot fail a request. No new dependency. `check:fences` 0 at the
close. Prose within 2,000–4,000 words with at least one `TRAP` box.

**Scale/Scope**: 8,120 chargeable objects, 4,255 MB, 1,576 environments, 187 tenants on one
listing page. Three user stories, one ClickHouse migration set, one SRS revision, no ADR
expected — the decisions this chapter makes are all inside clauses that already exist.

## Constitution Check

*GATE: checked before Phase 0 and re-checked after Phase 1.*

| Principle | Before Phase 0 | After Phase 1 |
|---|---|---|
| **I — Tenant isolation** | At risk: a per-tenant figure read from an analytical store, and an inventory that spans every tenant's objects | **PASS, with one arm the first draft assumed away.** The rollup is keyed `(environment_id, day)` and every read is scoped; an uploaded object's key is `${environment_id}/${id}`, so attribution needs no join and no unscoped query. **But the bucket also holds keys no tenant owns** — four probe and test prefixes, none of them on the listing's first page, which is where the claim of 100% came from. They are reported as their own category rather than skipped or guessed at (T035a). SC-003 probes the scope by deletion rather than trusting a number |
| **II — Contract-first** | At risk: a new analytical record type | **PASS.** The record is a protocol-package schema before it is a producer, and the **consumer learns it before the producer ships** — 049's finding, where an unrecognised type was terminated and both instruments reported nothing wrong |
| **III — Two data paths** | **ENGAGED.** This is a billing figure derived from operational events and kept in the analytical store | **PASS, on narrower ground than the first draft claimed.** That version rested on *"the operational path publishes and does not read back"*, which is true and does not cover the case the tasks described: they emitted **inside** the transaction, and `webhooks/analytics.ts:14-32` records a decision against exactly that — *"the publish happens after the commit, outside it"*, because a blocked outcome transaction is the failure III names. The publish is now after the commit, fire-and-forget, in the caller. DR-10 requires the rollup; DR-17 requires the reconciliation; SC-005 asserts a slot request succeeds with the store stopped |
| **IV — Single writer** | At risk: a second thing that knows a tenant's byte total | **PASS with a stated caveat.** The quota's level stays the single operational truth; the rollup is a derived history, and DR-17's reconciliation is what makes the derivation checkable rather than a second source. The chapter says plainly which one is authoritative |
| **V — API-first** | Not engaged | **PASS.** No client-facing surface changes. The reconciliation is an invokable command |
| **VI — Test-verified** | At risk: tenant isolation again, and an idempotence claim | **PASS with a method.** Per-arm deletion probes for the scopes, and a deliberate duplicate for FR-005 — 4.15's idempotence class was caught that way, not by reasoning about the upstream guard |
| **VII — Boring by design** | Not engaged | **PASS.** No new service, no new dependency, no new subject grammar beyond one token on a stream that exists |

**No gate fails, and no ADR is expected.** Complexity Tracking is empty for the first time in
this movement — worth noting rather than omitting, because the last three chapters each bought
something and this one spends only a column and a query parameter.

## Project Structure

### Documentation (this feature)

```text
specs/062-chapter-4-16/
├── plan.md              # This file
├── research.md          # Phase 0 — R1..R8, measured
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   └── storage-events.md
├── checklists/requirements.md
└── tasks.md             # /speckit-tasks — not created here
```

### Source Code

```text
relay-platform/
├── analytics/
│   ├── 0016_media_events.sql              # the event table
│   ├── 0017_billing_stored_bytes.sql      # the column, on the existing rollup
│   └── 0018_mv_billing_storage.sql        # the THIRD view into daily_usage_billing
├── packages/protocol/src/
│   └── analytics.ts                       # the record schema, before any producer
├── services/api/src/
│   ├── media/media.service.ts             # + on slot reservation
│   ├── media/store.ts                     # listObjects, on presign.ts's signer
│   ├── media/presign.ts                   # + query parameters, for pagination
│   ├── internal/media.controller.ts       # − on rejection, + on a rendition
│   └── metering/storage-reconcile.ts      # DR-17's comparison
├── services/ingester/src/
│   ├── shape.ts                           # the fourth route() arm — FIRST
│   └── metering.ts                        # storedBytes, beside storedMessages
└── services/media-worker/                 # UNCHANGED — see the structure decision

relay-tutorial/
├── lib/tutorial.ts                        # the 4.16 entry — seven fields
├── app/(en)/part-4/chapter-16/<slug>/{page.mdx,figures.ts}
└── fences/post-series.md                  # appendix hunks, written last

docs/
├── 04-srs.md            # FR-MED-12 and DR-17 amended; revision 1.23
├── 07-tutorial-plan.md  # row 17 SHIPPED
└── 12-part-4-structure.md # row 17 CLOSED
```

**Structure decision.** Three things, and the first is about which service owns what.

**THE LISTING GOES IN THE API, NOT THE WORKER, AND THE FIRST DRAFT PUT IT IN THE WORKER.**
The reconciliation has to read the rollup and the inventory together, and the worker **holds no
database credential** — `Dockerfile:6` says so and `api-client.ts:9` calls the internal seam
*"the worker's only road to state"* (ADR-04, ADR-31). So the comparison cannot live there, and
the api cannot import the worker's code: no cross-service import exists in either direction,
and 4.15's compiler refused exactly that when a worker test reached into the api's store.

**There are two signer implementations**, and the api's is the one this needs. It already takes
four methods and already documents the key-less bucket call — *"Empty for a BUCKET operation,
which is a different canonical URI: `/{bucket}` with no key segment and no trailing slash"*,
written at 4.10 — so the change is query parameters alone. **R2's measurement was taken against
the worker's `sign()`**, which is the right answer from the wrong code, and it is re-run against
`presign` before anything is built on it.

**`shape.ts` is first, not last**: a record the consumer does not claim is neither acked nor
terminated but **redelivered for the stream's seven days**, with an `unclaimed` counter as the
only signal (049's repair; 4.4 terminated them outright and both instruments reported health). And the **signer change
lands with the listing**, because `SignatureDoesNotMatch` is what an extra query parameter gets
today and that is a one-line discovery to make early rather than in phase 6.

## Phases

| Phase | What lands | Gate before moving on |
|---|---|---|
| 1 | Baseline: every lane count, the CI error set, and **the fence exposure of every file this chapter will touch, counted before any edit** | The numbers are in `baseline.txt`, including any that were wrong first |
| 2 | The record schema, the `route()` arm, the ClickHouse migrations. No producer | The red probe: publish the new type against the OLD consumer and watch it come back `unclaimed` and redelivered — **not terminated**, which is 4.4's behaviour and not today's |
| 3 | US1 — the producer at three emission points, and the rollup | US1's five scenarios; the scope arms probed by deletion; a deliberate duplicate |
| 4 | US2 — the listing, the signer's query parameters, the reconciliation | US2's four scenarios; **more than 1,000 keys asserted**, because 4.13's sweep read one page |
| 5 | US3 — uploads by kind | US3's two scenarios, and FR-010's one answer at every reader |
| 6 | The measurements: the rollup read against raw, the drift distribution, the inventory's cost | SC-002, SC-009 |
| 7 | Docs: SRS 1.23, FR-MED-12 and DR-17 amended, both Part 4 tables | SC-008 — every clause marked met, unmet-by-decision, or unreachable, with counts |
| 8 | The chapter: prose, figures, fences, appendix hunks | `check:fences` 0; word bound; `pnpm build` |
| 9 | Close: quickstart run, **`pnpm lint` and `turbo run typecheck` before pushing**, push in submodule order, per-error CI comparison, tag | SC-010 |

## Complexity Tracking

No violations. No new service, no new dependency, no new subject grammar, no ADR.

**One thing recorded here rather than left implicit.** Constitution IV is the closest call: a
tenant's byte total will exist in two places — the quota's operational sum and the analytical
rollup. That is not a second writer, because only one of them is authoritative and the other is
a derived history; but it is a second *number*, and two numbers for one quantity is how 4.7's
chapter began. DR-17's weekly reconciliation exists precisely to keep them honest, which is why
this plan treats it as part of the same feature rather than a follow-on.
