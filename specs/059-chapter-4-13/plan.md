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
2. **CLOSED at analysis pass 2 — the sweep needs an index after all.** `data-model.md` §5 said
   it did not, reasoning about the predicate and missing the `ORDER BY`. Measured: 90 buffers
   and 2.370 ms against 4 and 0.029 for a 50-row batch, at 88 kB. T020a ships it with the
   migration.
3. **Where does the probe's output live?** A column pair that is null for two of three kinds, a
   `jsonb` blob, or nothing stored at all until FR-MED-05 needs it. `data-model.md` takes a
   position; the tasks phase confirms it against what row 15 and row 16 will need.
4. **CLOSED at T018 — a compose service, profiled, with a Dockerfile.** The ingester's shape
   loses SC-010 outright, and the fifth-thing-nobody-runs objection is answered by the profile
   rather than by leaving it unpackaged: `--profile services` starts it and a bare `up -d
   --wait` does not. **THE THIRD REGISTRY WAS NOT THE ONE THIS QUESTION NAMED.** `INFRA_SERVICES`
   lists the *infrastructure* and excludes Relay's own containers by name; the list that had to
   grow is `infra.test.ts`'s `ours` set, which the both-directions assertion caught in one run.
   So: `compose.yaml`, `packages/config/src/infra.test.ts`, and `bound-port.test.ts`'s
   `BINDS_NOTHING` — three registries, and one of the three was misidentified by every artifact
   that named it. The original question follows.
   **Is the worker a compose service, or the ingester's shape?** `services/ingester` has no
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
   **AND THE PROFILE IS THE OPPOSITE ANSWER FROM THE SCANNER'S** (analysis pass 7). Six services
   start on a bare `up -d --wait` and three are profiled; T004a stops the profiled ones. The
   worker **writes** — an unprofiled one sweeps every `pending` object in the lane during every
   suite, rewriting fixtures other tests planted, which is 056-5 at maximum scale. The scanner
   **writes nothing** and must be up when the worker's own suites spawn it as a child. So the
   worker is profiled and ClamAV is not.
5. **CLOSED at analysis pass 4 — `media_events` is not started here.** `docs/04-srs.md:827`
   specifies it and DR-17 sums it; this chapter owns `ready` and `rejected` while DR-17 reads
   `uploaded` and `deleted`, so a producer now fills the table with the two values its own clause
   ignores. `contracts/` §5a and `gaps.md` carry the arithmetic.
6. **CLOSED at T019 — it does not avoid it, and nothing was added.** `UPDATE … WHERE state =
   'pending'` is a compare-and-set: the second worker updates no rows and is told `applied:
   false` with the state that won. A lease would buy efficiency rather than safety, at the cost
   of a column, a clock, a reaper and a new way for an object to become permanently
   unverifiable. `data-model.md` §7a carries it. The original question follows.
   **How does the sweep avoid two workers doing the same object?** One worker is the current
   reality and `FOR UPDATE SKIP LOCKED` is the obvious answer, but the read is through the api
   (ADR-04), not through a transaction the worker holds. The seam decides it.

## Constitution Check

*GATE: must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Assessment |
|---|---|
| **I · Tenant isolation** | The worker acts on objects one at a time, keyed by id, and writes through the api's internal seam which already resolves the environment from the row. **Nothing here takes a tenant as an input**, which is the property to state rather than a scope to add — a worker that accepted an environment id would be a route to forge. The gauntlet gains no new public route unless open question 1 adds one. |
| **II · No acknowledged message is lost** | Not engaged for messages. Engaged for *objects*: an object whose verification crashed halfway must come back, which is FR-009 and the reason a transient failure may not produce a terminal state. |
| **III · Two data paths** | Not engaged. No analytical read, no cross-store query. The worker touches Postgres only through the api. |
| **IV · Single writer** | **Engaged, and it is the reason for open question 6.** `media_objects.state` gains a second writer: the api writes `pending` at slot time and the worker writes the terminal states. They are different transitions on disjoint states, which is the argument — and it has to be written down rather than assumed, because two writers on one column is exactly what this principle names. |
| **V · API-first** | The transition is an internal route on an existing seam (`research.md` R8), not a new mechanism. **AND A PUBLIC CONTRACT CHANGE IS SHIPPING — this row said "whether … depends on FR-012's answer" until analysis pass 6, and FR-012 was answered two passes earlier.** T046 gates `GET /v1/media/:mediaId` on `ready`; `contracts/` §4 documents five conditions answering one 404; pass 3 measured the cost at 10 of 76 tests. A client that could fetch the bytes of a `pending` object yesterday cannot today, which is exactly the kind of change this row exists to flag. |
| **VI · Requirement-driven, test-verified** | FR-MED-03 and FR-MED-04 are both `T`. The 100%-branch clause names tenant isolation, and the obligation lands in **two** places, where this row named one until analysis pass 6. **The verdict** — four outcomes, two terminal — gets the per-arm treatment 4.11 and 4.12 both used (T083). **And `assertAttachableMedia` is the tenant-isolation code 4.11 met the clause on**, whose second arm this chapter makes reachable for the first time: T015a asserts it, T015b corrects the comment that calls it unreachable, and **T015c re-runs 4.11's per-arm probe, whose recorded result was measured when only one arm could occur.** A row that named only the verdict would have left the clause's own file to somebody else. |
| **VII · Boring by design** | **Engaged twice, and this is the chapter that answers both.** The one-language rule against a C scanner (`docs/12` §7.3, `research.md` R2) and the new-service rule against SAD §4.2's table (`research.md` R3, which no artifact had named). Both get an argument in the chapter and an ADR. |

**AND PRINCIPLE IV's ROW IS THE ONE WRITTEN AFTER READING THE CLAUSE.** 4.10's plan was wrong at
principle II and 4.11's at principle VI — both tables filled early and read past five times.
The row above says *engaged* because a second writer on `media_objects.state` is what this
chapter introduces, and the table's job is to catch exactly that.

**AND ROWS V AND VI WERE STALE ANYWAY, WHICH MAKES THIS THE THIRD FEATURE RUNNING.** They were
right when the table was filled and stopped being right two passes later — V because FR-012 got
an answer, VI because pass 3 found work in the file the clause is about. **A table filled once at
plan time is read past by every pass that changes the design**, and knowing that about 4.10 and
4.11 was not enough to stop it happening here. What would have caught it earlier is re-reading
the table at the end of each remediation rather than at the end of the feature.

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
│   │   ├── migrations/0019_media_pending_age.sql new — the sweep's partial index
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
    services/api/src/media/attach.itest.ts               —   4.11's, repaired by T008a
    services/api/src/auth/authenticate.middleware.ts      8               1
    packages/test-harness/src/bound-port.test.ts          2               1
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

**AND THE LAST THREE ROWS WERE ADDED BY THE ANALYSIS PHASE, NOT BY THE WORK.** This table said
twelve and said the count was a floor; passes 1 to 3 added tasks touching
`authenticate.middleware.ts` (T012a), `bound-port.test.ts` (T018a) and `attach.itest.ts`
(T008a), and none of the three was here. **This project's standing note is that a fenced-file
list goes stale when a chapter moves code between files — this is a new variant, where it went
stale because analysis found more work.** `attach.itest.ts` carries no titled fence, so its
repair is free; the other two are ten fences and two appendix hunks. The floor is fourteen files.

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

| **A third internal credential** | `PLATFORM_SERVICES` maps `RELAY_INTERNAL_CREDENTIAL` to the literal `"dispatcher"`, and `Principal.service` is what every log line reports. Reusing it would make the only component that reads customer bytes log as a service that never touched them. **And `@Accepts({ platform: ["media-worker"] })` is unwriteable without it** — `credential.guard.ts:36` refuses the bare `@Accepts("platform")`. | Reuse, which two artifacts had quietly assumed until analysis pass 1 read the middleware. **And the reason first given for the entry was wrong**: widening `PlatformService` stops nothing compiling, measured at pass 2 (`tsc --noEmit`, exit 0). |

**What is NOT a deviation, said because it looks like one**: reading customer bytes. ADR-13 and
ADR-14 both describe this service doing exactly that, and the SAD has called it *"the only Relay
component that ever reads media bytes"* since the first draft. The chapter's job is to say what
that costs, not to justify it.
