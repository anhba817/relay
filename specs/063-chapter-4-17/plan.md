# Implementation Plan: Chapter 4.17 — ★ Milestone: an image, end to end

**Branch**: `063-chapter-4-17` | **Date**: 2026-10-01 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/063-chapter-4-17/spec.md`

## Summary

Seven chapters built upload → scan → send → signed delivery, and no test joins them. Phase 0
walked the path by hand against the composed stack: every step works, an image is `ready`
**5,693 ms** after the PUT, and a recipient can fetch both the bytes and the thumbnail. So this
feature writes one journey suite in `packages/outsider` — the only lane that runs the deployed
worker — plus the rejection path, a recorded measurement, and the documents.

It adds no product surface. The three things it changes in the platform are a test file, a
comment that is false, and the SRS.

## Technical Context

**Language/Version**: TypeScript 5.7 / Node.js 22, as the rest of the workspace

**Primary Dependencies**: none added. The journey uses `fetch`, `ws` and the published routes;
`packages/outsider` is mechanically forbidden from importing workspace code.

**Storage**: none written by this feature. Postgres, MinIO and ClickHouse are read through the
platform's own surfaces.

**Testing**: `packages/outsider/src/*.itest.ts`, run by `pnpm test:outsider` against
`docker compose --profile services`, with `RELAY_DEMO_CREDENTIAL`, `RELAY_API_URL` and
`RELAY_WS_URL` set — CI's sealed job and a hand-run are the only things that execute it.

**Target Platform**: the composed stack. The media worker is a container built from
`services/media-worker/Dockerfile` under `profiles: ["services"]`.

**Project Type**: a tutorial chapter and the suite it is about. No service, no schema, no route.

**Performance Goals**: none set by this feature. It measures and publishes; the only figure it
owns is the end-to-end elapsed time and its decomposition.

**Constraints**: the sweep interval is 5,000 ms and is a deployment property — the journey waits
on a condition with a deadline rather than shortening it. The sealed suite cannot import
workspace code, so every observation is a published route or a signed URL.

**Scale/Scope**: one image, one message, one channel, one tenant. The development lane holds
6,535 media objects and this feature adds single digits.

## Constitution Check

*GATE: must pass before Phase 0 research. Re-checked after Phase 1 design.*

| principle | engaged | verdict |
|---|---|---|
| **I — tenant isolation** | the journey reads as one tenant through a seeded credential | **PASS.** It adds no query and no predicate. The thumbnail fetch exercises 4.15's composite key from outside for the first time, which is a read of an existing rule rather than a new one. |
| **II — no acknowledged message is lost** | not engaged | **PASS.** |
| **III — two data paths, never crossed** | not engaged | **PASS.** The metering path is 4.16's and is deliberately out of the journey: it travels through a process no deployment starts (050-8), and a milestone must not wait on one. |
| **IV — single writer** | not engaged | **PASS.** The feature writes no row the platform does not already write. |
| **V — API-first** | the whole journey is published surface | **PASS, and it is the point.** The seal is what makes the claim worth anything: if a step needs workspace code, the platform does not expose it and the chapter says so rather than reaching in. |
| **VI — test-verified** | FR-MED-09, and the 70%/100% clauses | **PASS with one clause recorded unmet.** FR-MED-09's *"renders as an explicit rejection marker"* has no renderer in this repository, so its data half is tested and its rendering half is recorded — 4.16's precedent with *"visible in the dashboard"*. Coverage is unaffected: `packages/outsider` is outside the coverage lane, which is itself worth one line in the chapter. |
| **VII — boring by design** | no new dependency, service, container or language | **PASS.** The feature's largest artifact is prose. |

**No violations. The Complexity Tracking table is omitted.**

**One thing this check found that the specification did not.** `packages/outsider` is reached by
no local lane and is **excluded from `pnpm coverage`**, so the journey suite — the chapter's
central claim — contributes nothing to the number constitution VI's second clause is stated in.
That is correct (coverage measures the platform, not the seal) and it means the milestone's
evidence is a green job rather than a percentage. Recorded, and the chapter says it.

## Project Structure

### Documentation (this feature)

```text
specs/063-chapter-4-17/
├── plan.md              # this file
├── spec.md
├── research.md          # Phase 0 — six questions, all answered by running
├── data-model.md        # Phase 1 — the journey's states, and what a recipient sees
├── quickstart.md        # Phase 1 — the walk, by hand, from outside
├── contracts/
│   └── journey.md       # the published surface the journey is allowed to touch
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks
```

### Source code

```text
relay-platform/
├── packages/outsider/src/
│   └── integrate.itest.ts        the journey, extending the media sequence that
│                                 already stops at `pending`
├── services/media-worker/
│   └── Dockerfile, compose.yaml  UNCHANGED — read, never edited
└── docs/                         (superproject) 04-srs.md, 05-sad.md, 07, 12

relay-tutorial/
├── app/(en)/part-4/chapter-17/milestone-an-image-end-to-end/
│   ├── page.mdx
│   └── figures.ts
├── lib/tutorial.ts               registration, seven fields
└── fences/post-series.md         hunks for whatever the chapter's edits move
```

**Structure Decision**: the journey lives in `packages/outsider` because it is the only lane
whose job starts the deployed worker (research R4). No file under `services/` changes, and
`compose.yaml` is read rather than edited.

**AND THE SEALED SUITE IS THE EXPENSIVE FILE, NOT THE CHEAP ONE.** It is titled in **five
fences** — part-3/chapter-26 in both locales, part-4/chapter-08, part-4/chapter-09 and
`fences/post-series.md` — as **two whole bodies and six diffs**. A titled fence is a whole-body
claim (051-6), so every edit to it is a claim about `relay-platform`'s HEAD that five places
publish. The feature changes one platform file and that file carries the whole fence bill; phase
8 is where it is paid, and T007 counts it before phase 2 edits anything.

## Phase plan

| phase | what | gate |
|---|---|---|
| **1** | Baseline: the five lanes, the CI error set, the fence exposure counted **before any edit**, and the sealed suite's current media assertions quoted | every number written down, including the ones that are red |
| **2** | US1 — the journey: slot → PUT → send → the deployed worker → history → link → bytes → thumbnail, each assertion naming its chapter | the suite is red with the worker stopped and green with it running, both demonstrated |
| | **One reader, not two credentials.** The seal holds exactly one and the seeder mints one on purpose; the recipient is a socket subscriber or a second read | no change to `scripts/seed-demo-tenant.mjs` |
| **3** | US2 — the rejection: bytes that contradict the declaration, the marker in history, the refusal on the link | the refusal is byte-identical to the one for an id nobody has |
| **4** | US3 — the measurement: the decomposition, the sample size, the timer named separately | no figure published without its sample size |
| **5** | The probes: stop the worker, break the scanner's address, and record what each looks like from outside | each produces a named red rather than a plausible green |
| **6** | The documents: SRS FR-MED-09, the clause count, both Part 4 tables, `sync:docs` | `check:docs` and `check:srs` green |
| **7** | The chapter: 2,000–4,000 prose words, figures, fences, the bill paid | `check:fences` 0 and `pnpm build` green |
| **8** | The record and the close: `baseline.txt`, `gaps.md`, `traceability.md`, the quickstart run, push, the per-error CI comparison, the tag | all four CI jobs green before the tag |

## Risks

**The milestone finds a defect in somebody else's chapter.** Phase 0 found none in the path, but
it walked it once. If phase 2 finds one, it is recorded with its bill and scoped deliberately —
a milestone that absorbs a repair stops being a measurement of what was already there.

**The fixture has to be bigger than the bound, and the seal makes that awkward.** The existing
image is a 1×1 literal and produces no rendition; the journey's 800×600 one deflates to 447,345
bytes, so it is generated with `node:zlib` rather than carried. That is a second Node builtin in
a file whose header claims it imports none, and the header is corrected rather than the rule
bent — `node:zlib` is not a workspace path.

**The journey becomes a second harness, and the file is already most of the way there.**
`integrate.itest.ts` defines `waitFor` **three times** — once per test, at lines 280, 348 and
423 — so "extend what is there" means deciding about those three before adding a fourth. T010a
is that decision and it is written down either way.

**The suite runs nowhere but CI.** That is already true of the sealed nineteen, and it means a
local green says nothing about this chapter's central claim. Phase 8's push is the first honest
run, which is the same position 4.11 was in when the sealed job had never executed at all.

**And the chapter has no mechanism to describe.** Every chapter so far shipped something that did
not exist. This one ships a test, which is a harder chapter to write and an easier one to pad.
The word bound is a real constraint here rather than a formality.
