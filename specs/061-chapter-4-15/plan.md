# Implementation Plan: Chapter 4.15 — "What a thumbnail costs"

**Branch**: `061-chapter-4-15` | **Date**: 2026-09-28 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/061-chapter-4-15/spec.md`

## Summary

FR-MED-05 has two halves and they fail for different reasons. *"Derived objects sharing the
parent's lifecycle"* is a question about rows and predicates: a rendition is referenced by no
message, so FR-MED-08 refuses to serve it and FR-MED-10 would delete it after 24 hours, and
`media_objects` cannot currently say that two rows are related at all. *"Generate a thumbnail
for images and a poster frame for videos"* is a question about what this platform may depend
on, since nothing in it can decode a pixel.

The plan builds parenthood first, because it is testable with no decoder anywhere in the
repository and because a rendition no door recognises is bytes the platform will delete
tomorrow. Then the bytes, with `sharp` in the media worker — 30.4 MB, 15.2 ms for a 1920×1080
JPEG, against 28.9 MB and 35.8 ms for an ImageMagick subprocess. Then delivery, on the shape
4.14 built. The video half is ruled out with its price written down: ffmpeg is 114 MB, 3.75×
the image half, for the harder half of a clause whose easier half chapter 4.13 already declined.

The title is the deliverable. What a thumbnail costs is **about 7 kB and 15 ms** — and the
measurement that matters is that the *ratio* to the parent spans 775× across a real corpus while
the thumbnail's own size spans 4×, so the ratio is a fact about the parent and publishing it as
the cost is publishing the wrong variable.

## Technical Context

**Language/Version**: TypeScript 5.x on Node.js 22 (`node:22-alpine` in the worker's image),
ES modules throughout.

**Primary Dependencies**: `sharp` (new — native, libvips 8.18.7, the workspace's first native
binary in a shipped service). Existing: Drizzle in the api's repository layer, Zod in
`@relay/protocol`, NestJS in the api, plain consumers in the worker.

**Storage**: PostgreSQL — `media_objects` gains `parent_id`, `rendition`, and a reason column.
MinIO for the bytes, through the api's signing code; the worker's own store client gains its
first writer.

**Testing**: vitest. Unit in `pnpm test` (Docker-free), integration in `pnpm test:integration`
against real stores, `pnpm coverage` as the only lane that runs everything. New suites in
`services/media-worker/src` and `services/api/src/media`.

**Target Platform**: Linux containers under `docker compose`; CI is the superproject's
`.github/workflows/ci.yml` with the two repositories as submodules.

**Project Type**: A tutorial chapter whose deliverable is a published page in `relay-tutorial`
plus the `relay-platform` commits it fences, tagged `part4-ch15`.

**Performance Goals**: Thumbnail generation must not dominate the per-object cost the 4.13
sweep already pays. **The cost has three components and the plan's first draft priced one.**
CPU is measured: 50.8 ms at the 10 MB image cap. The other two are R9's and are unmeasured
until phase 4 — a **full-object GET the worker does not currently make** (its three calls hold
metadata, a 64 KiB scan window and a prefix), and the peak memory libvips needs while it reads.
Both are taken on images above the bound only, which R2's crossover makes a minority.

**Constraints**: The worker's image grows by 30.4 MB. No file under `relay-platform/` may be
edited to make a fence correct. `check:fences` must report 0 at the close. Prose within
2,000–4,000 words with at least one `TRAP` box.

**Scale/Scope**: Three user stories, one migration, one new dependency, one ADR, one SRS
revision. The delivery contract changes, which means 4.14's door derivation has to be re-run
rather than re-read.

## Constitution Check

*GATE: checked before Phase 0 and re-checked after Phase 1. Both results below.*

| Principle | Before Phase 0 | After Phase 1 |
|---|---|---|
| **I — Tenant isolation** | At risk: a self-referencing `parent_id` can name a row in another environment, and no plain foreign key forbids it | **PASS.** R3 puts it in a composite foreign key `(parent_id, environment_id)`, so the database refuses it rather than a predicate somebody maintains. FR-005 keeps authorisation as *the same predicate* as the parent's, not a copy |
| **II — Contract-first** | At risk: a new field on a delivered message | **PASS.** The field goes on `deliveredAttachmentSchema`, the outbound-only shape 4.14 created for exactly this asymmetry. Contract written in `contracts/renditions.md` before code |
| **III — Two data paths** | Not engaged | **PASS.** No analytical read or write. Storage metering is FR-MED-12 and chapter 4.16's |
| **IV — Single writer** | At risk: the worker would write rendition rows | **PASS, after a correction.** The worker posts to the api as it already does for verdicts; the api's repository layer is the only writer. The first draft said the rendition insert *"rides the verdict's existing compare-and-set"* — **there is no transaction there to ride**, and an analysis pass found it by reading `recordMediaVerdict` rather than the plan. The CAS and the insert are wrapped in one `db.transaction` (T037), because otherwise a landed UPDATE and a failed INSERT leave a parent `ready` with no rendition and no reason |
| **V — API-first** | Not engaged for the worker seam (internal) | **PASS.** The client-facing surface is the existing `GET /v1/media/:mediaId` and one optional field |
| **VI — Test-verified** | At risk: 100% branch coverage is named for tenant isolation, and the new predicate is tenancy | **PASS with a method.** SC-004 probes every arm by deletion rather than trusting a number, because 4.12 measured a single-mutation probe reporting green for two of three real tenancy scopes, and an SQL clause carries no JavaScript branch |
| **VII — Boring by design** | **ENGAGED.** A new dependency, and a possible new service | **PASS via ADR.** No new service — the "deliberately not a separate service" test says merged (same datastore, same transactions, same team). The dependency needs the ADR that FR-014 requires; see Complexity Tracking |

**No gate fails.** One entry goes to Complexity Tracking.

## Project Structure

### Documentation (this feature)

```text
specs/061-chapter-4-15/
├── plan.md              # This file
├── research.md          # Phase 0 — R1..R8, all measured
├── data-model.md        # Phase 1
├── quickstart.md        # Phase 1
├── contracts/
│   └── renditions.md    # Phase 1 — the wire shape and its invariants
├── checklists/
│   └── requirements.md  # from /speckit-specify
└── tasks.md             # /speckit-tasks — not created here
```

### Source Code

```text
relay-platform/
├── packages/protocol/src/
│   ├── attachments.ts             # deliveredAttachmentSchema gains `thumbnail`
│   └── media.ts                   # RENDITIONS, the closed set; rendition failure reasons
├── services/api/
│   ├── migrations/0020_media_renditions.sql
│   └── src/
│       ├── db/
│       │   ├── schema.ts          # parent_id, rendition, composite FK, unique (id, environment_id)
│       │   └── repository.ts      # unreferencedMediaIn (the reaper's future predicate),
│       │                          # rendition insert inside recordMediaVerdict's transaction,
│       │                          # withMediaStates extended to carry the thumbnail
│       ├── media/
│       │   ├── media.controller.ts        # delivery refuses a rendition addressed directly
│       │   ├── rendition.itest.ts         # US1 — lifecycle
│       │   └── rendition-delivery.itest.ts# US3 — the wire and the gate
│       └── internal/
│           └── media.controller.ts        # the verdict door accepts a rendition
└── services/media-worker/
    ├── package.json                # + sharp
    └── src/
        ├── store.ts                # putObject — the worker's first writer
        ├── thumbnail.ts            # sharp, the bound, the no-rendition rule
        ├── thumbnail.test.ts
        └── thumbnail.itest.ts

relay-tutorial/
├── lib/tutorial.ts                          # the 4.15 entry — seven fields
├── app/(en)/part-4/chapter-15/<slug>/page.mdx
├── app/(en)/part-4/chapter-15/<slug>/figures.ts
└── fences/post-series.md                    # appendix hunks, written last

docs/
├── 04-srs.md          # FR-MED-05 amended; revision 1.22
├── 05-sad.md          # ADR-34
├── 07-tutorial-plan.md# row 16 SHIPPED
└── 12-part-4-structure.md # row 16 CLOSED
```

**Structure decision.** Nothing new in the layout. The one shape worth naming is that
`thumbnail.ts` lives in the worker and the *row* is written by the api — the worker produces
bytes and posts a verdict, which is the seam 4.13 built and 4.14 extended, and Principle IV is
why it is not tempting to shortcut it.

## Phases

| Phase | What lands | Gate before moving on |
|---|---|---|
| 1 | Baseline: every lane's real count, the dependency count, `check:fences`, the CI error set | The numbers are recorded in `baseline.txt`, including any that were wrong first |
| 2 | Migration, schema, protocol set. No behaviour | `pnpm test` green; the migration's red probe fails by name |
| 3 | US1 — parenthood and lifecycle, with `unreferencedMediaIn` and its stand-in caller | US1's five scenarios; every arm probed by deletion (SC-004) |
| 4 | US2 — `sharp`, `putObject`, the bound, the no-rendition rule, ordering and failure, **and the transaction `recordMediaVerdict` does not currently have** | US2's five scenarios; the atomicity test run red first; the store listed rather than the database queried (SC-006) |
| 5 | US3 — the wire field, the delivery gate, the direct-address refusal | US3's four scenarios; 4.14's door derivation re-run, not re-read |
| 6 | The cost measurements, published with their method and corpus provenance | SC-008's three figures, each measured in this repository |
| 7 | Docs: SRS 1.22, ADR-34, both Part 4 tables, the video ruling | SC-010; `check:srs`, `check:docs`, `check:refs` |
| 8 | The chapter: prose, figures, fences, appendix hunks | `check:fences` 0; word bound; `pnpm build` |
| 9 | Close: push in submodule-then-superproject order, per-error CI comparison, tag | SC-011; the error set diffed both ways against the baseline |

## Complexity Tracking

| Violation | Why needed | Simpler alternative rejected because |
|---|---|---|
| A new third-party runtime dependency in a service whose current count is zero — and the workspace's **first native binary in a shipped service** (the three existing `.node` files are `lightningcss`, `@swc/core` and `@rolldown/binding`, all build-time) | FR-MED-05 requires generated renditions, and `ALLOWED_TYPES` holds four image formats. Nothing in `node:*` decodes any of them | **Pure TypeScript** reaches PNG alone — `node:zlib` gives inflate, and JPEG needs a DCT decoder, GIF LZW, WebP VP8. **An ImageMagick subprocess** was measured at 28.9 MB and 35.8 ms against sharp's 30.4 MB and 15.2 ms, and pays its 20 ms as spawn on every object in a backlog the sweep walks in pages. **A seventh container** fails the "deliberately not a separate service" test on all three columns and engages ADR-31 for a job with no independent scaling story. ADR-34 records this with its reversal condition |

**And one non-violation worth recording.** ADR-32 ruled that a program addressed over a socket
is not a program Relay is implemented in. `sharp` is not that case — it is a library linked into
the worker's own process — so ADR-32's argument does not carry, and ADR-34 has to make its own.
The constitution's one-language clause governs **what Relay is implemented in**; a native module
called from TypeScript is the same relationship as the JSON parser in Node, which is C. ADR-34
states that reading rather than assuming it, because assuming it is how a clause gets widened by
silence.
