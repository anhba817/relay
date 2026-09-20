# Implementation Plan: Chapter 4.13 — the only service that reads the bytes

**Branch**: `059-chapter-4-13` | **Date**: 2026-09-20 | **Spec**: [spec.md](./spec.md)
**Input**: `docs/12` §3 row 14, movement VI · FR-MED-03, FR-MED-04 · `docs/12` §7.3

## Summary

Build the media worker: the platform's fifth service and the first Relay component that reads
bytes a customer uploaded. It finds objects whose bytes have arrived, verifies them against
what the slot declared, scans them, probes them, and moves each one to `ready` or `rejected`.

**Three things the brief did not say, all measured in `research.md`:**

1. **The event the SAD says the worker consumes has no producer and does not need one.** The
   spec assumed the client would tell us; a `HEAD` sweep costs **1.412 ms per object and 4.2 s
   for the lane's whole 3,005-row backlog**, which makes the client notice an optimisation
   rather than a mechanism — and FR-MED-04's *"every uploaded object"* is what a
   client-contingent notice cannot promise.
2. **ADR-14's delivery gate and chapter 4.12's shipped route disagree, and the gate cannot ship
   alone.** Adding `WHERE state = 'ready'` today turns **10 of 76 tests red**, including the
   isolation gauntlet's own control, because nothing can produce `ready`. The transition and the
   gate ship together or not at all.
3. **The probe splits, and only half of it needs a second program.** Image dimensions come from
   **24 bytes** of a PNG and fixed offsets in three other formats; audio and video duration is
   four unrelated container parsers with a known hard case. That split is what makes `docs/12`
   §7.3's constitutional question concrete rather than abstract.
4. **The scan has to run BEFORE the declaration check, and an impossible test is what proved
   it** (added at analysis pass 1, `research.md` R5a). ClamAV's EICAR signature matches the
   **file** rather than a substring — EICAR plus two hundred trailing spaces is already `OK` —
   and `ALLOWED_TYPES` has no text type, so **no object can both satisfy FR-MED-03 and trip the
   scanner**. FR-MED-04's own *"every uploaded object"* had required this order all along.

## Technical Context

**Language/Version**: TypeScript 5.x on Node 22 (ADR-01, ADR-15), plus — for the first time —
two programs that are not either: ClamAV (C) and, if the plan's open question 1 lands that way,
ffprobe (C).

**Primary Dependencies**: none new in `package.json` is the target and it is not yet a
prediction. The scanner speaks `INSTREAM` over a socket, which needs no client library. The
image probe is fixed offsets. Duration is the open question. **29 dependencies at
`part4-ch12`**, and SC-010 asks for the figure with an explanation rather than a promise.

**Storage**: Postgres for `media_objects` (via the api, never directly — ADR-04); MinIO for the
bytes; no new store.

**Testing**: vitest. Integration against a real MinIO and a real ClamAV, because SC-003 says the
EICAR signature must be rejected by a scanner that is running.

**Target Platform**: Linux containers; the worker is the fifth service and `compose.yaml`'s
seventh container.

**Project Type**: a background worker in a pnpm workspace, alongside `dispatcher` and
`ingester`.

**Performance Goals**: none stated by the clause. What gets measured is time from upload to
`ready`, with the scan's share separated (SC-006), and the sweep's per-object cost, which is
already 1.412 ms.

**Constraints**: the largest allowed object is **100 MB** (`KIND_CAPS.video`). **NFR-SCL-01 is
not the constraint it looks like** — it names 10,000 connections and no memory figure; the
160 MB everyone reaches for is `docs/11`'s measurement of the gateway's RSS (`research.md` R9).
The worker's memory bound has to be measured here, not quoted.

**Scale/Scope**: 3,005 `pending` rows and 253 objects on the lane today.

### Open questions for the tasks phase

1. **Does this chapter probe duration, or only dimensions?** `research.md` R6 splits them:
   dimensions need no second program, duration needs four container parsers or ffprobe.
   FR-MED-04 names both. Shipping dimensions alone means the clause is partly met and the
   chapter says so; shipping both means a second binary in the image and a longer §7.3
   argument. **Decide in `contracts/`, with the cost of each written down.**
2. **Where does the probe's output live?** A column pair that is null for two of three kinds, a
   `jsonb` blob, or nothing stored at all until FR-MED-05 needs it. `data-model.md` takes a
   position; the tasks phase confirms it against what row 15 and row 16 will need.
3. **Is the worker a compose service, or the ingester's shape?** `services/ingester` has no
   Dockerfile and nothing starts it but a test suite (`gaps.md` 050-8, open since 4.5). A fifth
   service packaged the same way is a fifth thing nobody runs — and a container costs
   `compose.yaml` plus `INFRA_SERVICES` plus a health check, which is the both-directions
   assertion 4.10 tripped over. **Whichever is chosen, the chapter names which shape it is.**
   **AND IT DECIDES WHETHER SC-010 CAN EXIST** (analysis pass 1): the sealed suite fetches the
   bytes of an object it uploaded, T046's gate refuses that until something moves it to `ready`,
   and only a worker inside the composed profile does. The unpackaged shape means SC-010 is
   unsatisfiable; the container makes it a poll. **Three registries, not two** — `compose.yaml`,
   `INFRA_SERVICES` and `bound-port.test.ts`'s `BINDS_NOTHING`, whose omission cost 050 two
   chapters when the ingester arrived without it.
4. **How does the sweep avoid two workers doing the same object?** One worker is the current
   reality and `FOR UPDATE SKIP LOCKED` is the obvious answer, but the read is through the api
   (ADR-04), not through a transaction the worker holds. The seam decides it.

## Constitution Check

*GATE: must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Assessment |
|---|---|
| **I · Tenant isolation** | The worker acts on objects one at a time, keyed by id, and writes through the api's internal seam which already resolves the environment from the row. **Nothing here takes a tenant as an input**, which is the property to state rather than a scope to add — a worker that accepted an environment id would be a route to forge. The gauntlet gains no new public route unless open question 1 adds one. |
| **II · No acknowledged message is lost** | Not engaged for messages. Engaged for *objects*: an object whose verification crashed halfway must come back, which is FR-009 and the reason a transient failure may not produce a terminal state. |
| **III · Two data paths** | Not engaged. No analytical read, no cross-store query. The worker touches Postgres only through the api. |
| **IV · Single writer** | **Engaged, and it is the reason for open question 4.** `media_objects.state` gains a second writer: the api writes `pending` at slot time and the worker writes the terminal states. They are different transitions on disjoint states, which is the argument — and it has to be written down rather than assumed, because two writers on one column is exactly what this principle names. |
| **V · API-first** | The transition is an internal route on an existing seam (`research.md` R8), not a new mechanism. Whether any *public* surface changes depends on FR-012's answer: gating delivery changes what `GET /v1/media/:mediaId` returns for a `pending` object, which is a contract change a client can see. |
| **VI · Requirement-driven, test-verified** | FR-MED-03 and FR-MED-04 are both `T`. The 100%-branch clause names tenant isolation; this chapter's isolation surface is thin, so the per-arm treatment goes on the **verdict** instead — four outcomes, two terminal, and a probe per arm as 4.11 and 4.12 both did. |
| **VII · Boring by design** | **Engaged twice, and this is the chapter that answers both.** The one-language rule against a C scanner (`docs/12` §7.3, `research.md` R2) and the new-service rule against SAD §4.2's table (`research.md` R3, which no artifact had named). Both get an argument in the chapter and an ADR. |

**AND PRINCIPLE IV's ROW IS THE ONE WRITTEN AFTER READING THE CLAUSE.** 4.10's plan was wrong at
principle II and 4.11's at principle VI — both tables filled early and read past five times.
The row above says *engaged* because a second writer on `media_objects.state` is what this
chapter introduces, and the table's job is to catch exactly that.

## Project Structure

### Documentation (this feature)

```text
specs/059-chapter-4-13/
├── plan.md              # this file
├── spec.md
├── research.md          # R1–R9, phase 0
├── data-model.md        # phase 1
├── quickstart.md        # phase 1
├── contracts/
│   └── media-verification.md
├── checklists/
│   └── requirements.md
└── tasks.md             # /speckit-tasks
```

### Source code

```text
relay-platform/
├── compose.yaml                                  clamav; maybe the worker
├── packages/
│   ├── config/src/infra.ts                       INFRA_SERVICES — both directions (056)
│   └── protocol/src/                             the state type, if it is published
├── services/
│   ├── api/
│   │   ├── migrations/0018_media_states.sql      new — widen the CHECK
│   │   └── src/
│   │       ├── db/schema.ts                      the CHECK's twin
│   │       ├── db/repository.ts                  the transition, and FR-012's gate
│   │       ├── internal/                         the transition route (ADR-04's seam)
│   │       └── media/delivery.itest.ts           the gate's tests
│   └── media-worker/                             new package — sweep, verify, scan, probe
└── vitest.coverage.config.mts                    pins for every new file

relay-tutorial/
└── app/(en)/part-4/chapter-13/…/{page.mdx,figures.ts}
```

### The fenced files this chapter may touch

**Counted against the checker, and the count is a floor.** 056 said twelve and the checker said
seventeen; 057 said thirteen and said twenty-two; 058 said six and the checker said six with a
different *set*, then eight once the late repairs landed. The error has been in one direction
every time.

    file                                            titled fences   appendix hunks
    services/api/src/db/repository.ts                    50               0
    services/api/src/db/schema.ts                        32               2
    packages/protocol/src/codes.ts                       24               3
    vitest.coverage.config.mts                           22              12
    turbo.json                                           20               3
    compose.yaml                                         16               0
    services/api/src/isolation/targets.ts                12               2
    services/api/src/isolation/gauntlet.itest.ts         12               4
    services/api/src/internal/internal.controller.ts     10               —
    packages/config/src/infra.ts                          5               0
    packages/outsider/src/integrate.itest.ts              4               2
    services/api/src/media/media.service.ts               2               0
    services/media-worker/**                              0   — new, and free
    services/api/src/media/delivery.itest.ts              0   — new at 4.12, unfenced

**`vitest.coverage.config.mts` carries twelve appendix hunks**, which is the largest appendix
surface of anything here. 4.9 found that file could not take a chapter hunk at all at one point;
4.12 got one in. Check the state before blaming the hunk.

## Complexity Tracking

| Deviation | Why it is necessary | What was rejected |
|---|---|---|
| **A second and possibly third language in the deployment** | FR-MED-04 requires a virus scan, and writing one is not a thing a tutorial platform does. `research.md` R2 argues the line: a program Relay addresses over a socket is not a program Relay is *implemented in*, and the platform already speaks to five such programs in four languages. | Writing the worker in Go because the work is CPU-bound — which VII really would forbid, and which ADR-01 named in advance. |
| **The platform's fifth service** | Different datastore, no transactions, CPU-bound off the request path: it fails all three of SAD §4.2's merge criteria (`research.md` R3). | Merging the worker into the api, which would put a 2–10 s CPU-bound pipeline in the same process as the send path — the coupling ADR-14 exists to forbid. |
| **A second writer on `media_objects.state`** | The api writes `pending` and the worker writes the terminal states. Constitution IV names single-writer, so this is a deviation that gets an argument rather than a silence. | A single writer reached by making the api poll and scan, which is the merge above wearing different clothes. |
| **A sweep rather than an event** | `research.md` R1: the event has no producer, the sweep costs 4.2 s for the whole backlog, and a client-driven notice makes FR-MED-04's *"every"* contingent on the client. | Bucket notifications, rejected on ADR-30's direction argument and recorded rather than dismissed. |

| **A third internal credential** | `PLATFORM_SERVICES` maps `RELAY_INTERNAL_CREDENTIAL` to the literal `"dispatcher"`, and `Principal.service` is what every log line reports. Reusing it would make the only component that reads customer bytes log as a service that never touched them. | Reuse, which two artifacts had quietly assumed until analysis pass 1 read the middleware. |

**What is NOT a deviation, said because it looks like one**: reading customer bytes. ADR-13 and
ADR-14 both describe this service doing exactly that, and the SAD has called it *"the only Relay
component that ever reads media bytes"* since the first draft. The chapter's job is to say what
that costs, not to justify it.
