# Gaps — feature 059, chapter 4.13, "the only service that reads the bytes"

Everything here was measured during this feature. Carried items are **re-measured**, never
copied.

---

## New

### 059-1 · The event the SAD says the worker consumes has no producer

**Zero occurrences of `media.uploaded` anywhere in these three repositories.** `docs/05-sad.md`
names a consumer and an event; this chapter ships the consumer and there is no event, because
**the client PUTs straight to the store** (ADR-13) and the only two parties that know the upload
finished are the client and the store. 4.10's *"the api never opens a socket"* arrives here as a
hole rather than as a cost.

**The specification's answer — the client tells us — is priced wrong, and the measurement is
what settles it.** The spec rejected a sweep on *"91.6% of the work spent on objects that hold
nothing"*. One signed `HEAD` is **1.412 ms** (p50 1.094, p95 1.714, n=200) and the lane's whole
**3,292-row backlog is 4.2 s serial**, 166 of 200 being 404s. **The waste is free.**

**So the sweep is the mechanism and a notice is an optimisation that must not change any
answer** — because FR-MED-04's *"every uploaded object shall be virus-scanned"* cannot be
contingent on a client choosing to send one. Bucket notifications are rejected on ADR-30's
direction argument one layer down: a store-specific webhook is a vendor coupling at the moment
the platform is choosing a replaceable store.

**What a later chapter inherits is a measurement rather than a question.** If bucket
notifications are ever added, the figure to beat is 4.2 s for the whole backlog and the property
to keep is that the sweep still runs.

### 059-2 · Time to `ready` is bounded below by the sweep interval

**SC-006, and this is what the sweep gives up.** The real worker against the real api and store,
8 objects of 256 KiB:

    interval 1000 ms    min  244   p50 1073   max 1099    8 of 8 ready
    interval 5000 ms    min 3163   p50 5080   max 5098    8 of 8 ready

**The work is 7 ms of a 5,080 ms answer.** Everything else is waiting for the next poll. A
client notice would have removed the whole of it, and cannot, for 059-1's reason.

**AND THE START INSTANT IS THE STORE'S, AT ONE-SECOND RESOLUTION.** Nothing tells this platform
when a PUT finished, so `last-modified` on the sweep's own `HEAD` is the only observation of it
— and an HTTP date has no sub-second field. **Publishing only the 4.2-second backlog figure
would have been selling the trade rather than stating it.**

### 059-3 · `authenticate.middleware.ts` claims a compiler behaviour it does not have

*"Adding a third internal service widens this union on its own and every route that must now
decide about it stops compiling."* **Measured: it does not.** A third entry added to
`PLATFORM_SERVICES`, `tsc --noEmit` on the api, **exit 0**. `PlatformService` appears in three
positions and every one is `readonly PlatformService[]`, where a new member is purely additive.

**Three of this feature's artifacts repeated the sentence before anybody ran it** — the
contract, `research.md` R8 and T012a — each having copied it from the source comment.

**The protection the comment describes is real and lives one file over.**
`credential.guard.ts:36` types `AcceptSpec` so that a bare `@Accepts("platform")` does not
compile: a platform route must name its callers. **That** is what made the third entry mandatory.
Corrected in place this chapter, which cost a fence the chapter was already opening that file
for.

### 059-4 · JavaScript's `<<` is signed, and it reached the api as a 400

`u32be` in the PNG reader was `(b[at] << 24) | …`. Bytes `ff 00 00 0a` read **-16,777,206**
rather than 4,278,190,090, the verdict schema says `z.number().int().positive()`, and the api
answered **400** — **three layers from the arithmetic that caused it**.

**And the worker retried it forever.** A 400 is the worker's own bug and is not transient, so
the sweep re-streamed the same eight objects through ClamAV on every interval, with the log
saying exactly what was wrong and nothing acting on it. Fixed three ways: `>>> 0`; a
`MAX_DIMENSION` of 1,000,000 above which the answer is `null` rather than a clamp; and a
process-local set of ids the api refused with a 4xx, skipped for this worker's lifetime.

**No unit test would have produced the input.** Every fixture in `dimensions.test.ts` is a header
this repository wrote with dimensions somebody chose. The bytes came from `randomFillSync`, in a
measurement script written to time something else.

### 059-5 · A liveness probe passes against a signature database thirteen days old

`clamav/clamav:latest`, a fresh container, the shipped check every four seconds:

    t≈12s   exit 1   ClamAV 1.5.4/28122/Sun Sep 13   age 13d
    t≈25s   exit 1   28122 · 13d
    t≈30s   exit 0   ClamAV 1.5.4/28135/Sat Sep 26   age  0d

`zPING` answers `PONG` throughout, so a check of the shape every other service in
`compose.yaml` uses would report ready at twelve seconds and the worker would scan against
definitions from a fortnight ago. **That is 4.2's `/ping`, 4.9's unset credential and 4.10's
bucket for the fourth time** — *a check that cannot fail for the reason you care about is not a
check* — and this one has a measured window.

**AND SC-003 CANNOT CATCH IT.** EICAR lives in `main.cvd` at version **63**, reported
*"up-to-date"* in both readings, while the staleness is entirely in `daily.cld` (28122 → 28135,
355,678 signatures). Measured: `Eicar-Test-Signature FOUND` at t≈12s, 16s, 20s and 26s alike.
**The test that proves the scanner runs is structurally unable to prove it is current.**

**What is not closed**: the bound is seven days and the window is bandwidth-bound. On a slow
link `freshclam`'s first run is unbounded, and `start_period: 30s` plus twenty retries is 130 s
of grace chosen from one machine's measurement.

### 059-6 · The sweep writes an analytics record on every poll, forever

Chapter 4.4's producer records internal-seam calls deliberately, so `GET /internal/media/pending`
produces one `api_requests` row per poll **whether or not there is work**. At a five-second
interval: **17,280 rows a day** at 4.5's measured 403.5 B a record, about **0.2 rec/s against
the 4.40 rec/s** that fills the stream's seven-day retention — **4.5% of the budget, spent on an
idle platform.**

Small, **constant**, and the interval is a number this chapter chooses. Published rather than
routed around, for 4.8's reason about the request log spending the tenant's own budget: a cost
the platform imposes on itself is still a cost, and the first person to notice it should find it
written down rather than discover it.

### 059-7 · Audio and video carry no duration (FR-MED-04 partly met)

**Unmet by decision, not by oversight** — FR-MED-07's SRS 1.18 precedent. Dimensions are 24 bytes
of 4,722 for a PNG and fixed offsets or a short walk for the other three formats. Duration is
**four unrelated container parsers** with MP3 VBR as a genuinely hard case: a VBR file's length
is not in its header, and computing it means walking every frame.

**What it costs a client**: no scrubber length before playback. A player must download enough of
the file to compute it, which is exactly the work the platform declined to do.

**And it makes §7.3's argument narrower rather than wider**: ADR-32 defends **one** non-TypeScript
program, not two. If duration ever ships via `ffprobe`, that is a sixth program Relay addresses
over a socket and not a sixth language — the clause it engages is the same one and the answer is
already written.

### 059-8 · The two migration runners give different guarantees about an edited file

`analytics/apply.mjs:123` keys `schema_applied` on **`(filename, checksum)`** and refuses a
changed file — the refusal 4.2 built and 4.6 re-ran by hand. `services/api/src/db/migrate.ts`
keys `schema_migrations` on **filename alone**, so the same edit is skipped **without a word**.

The forward-only discipline (ADR-16) makes an edit wrong either way; what differs is whether
anybody finds out — and the Postgres side is the one where a developer's lane and CI end up with
different schemas from the same tree. This chapter paid it directly: T020a's index went into
`0019` rather than into `0018` **because `0018` had already applied**, and the index would then
have existed on a fresh CI database and not on the lane, with no test able to tell, since the
sweep works either way and only slower.

**Found because an analysis pass added a task that edited an applied migration and a later pass
asked what the runner would do about it.**

### 059-9 · The media worker's integration lane must run serially, and nothing checks that

`GET /internal/media/pending` is oldest-first over the whole platform and takes no tenant
parameter — the isolation property the route is built around. **Two suites sweeping at once
sweep the same queue**: both backdate their fixture to the head, the second wins, and the first
suite's sweep verifies the second suite's object. Measured: **six tests red across two files,
every one `expected 'pending' to be 'ready'`, with nothing wrong in the worker.**

**It is not an assertion that is too wide but the ACTION** — 056-5's shape — and
`check-lane-scope.py` cannot see it, because the scope that is missing is in a route's contract
rather than in SQL. `fileParallelism: false` in that lane's config, with the reason written
there.

**What is not closed**: nothing stops a future suite in another package from sweeping. The
property that would need checking is *"only one process calls `/internal/media/pending` at a
time"*, and no instrument in this repository can express it.

### 059-10 · SRS 1.19 publishes lane figures that were true for six days

*"11,557 public channels against 1,016 private on the lane"* is now **12,718 against 1,172**,
measured 2026-09-26 — the ratio moved **11.38:1 to 10.85:1**, so **the argument holds and both
numerals are wrong**. Public channels grew 10.0% and private ones 15.4% in fifteen days, which
is the direction that would eventually falsify the clause's reasoning and is nowhere near doing
so.

**Do not edit the shipped revision**: revisions are appended in `docs/04-srs.md`, and 1.14
corrected an earlier one's citation in new prose rather than in place. **A measurement published
as a fact about a moving population needs the date it was taken**, which 4.8 learned when its own
per-tenant median moved from 10 to 7 during its own feature.

### 059-11 · `media_events` is specified, unbuilt, and this chapter declined to start it

`docs/04-srs.md:827` specifies an analytical table — *"Storage metering, scan-pipeline health
(FR-MED-12)"* — whose `event` column is `uploaded/ready/rejected/deleted` and whose
`processing_ms` is this chapter's SC-006 measurement. **DR-17** builds stored-bytes-per-tenant by
*"summing `media_events` deltas (uploaded/deleted), reconciled weekly against an object-storage
inventory"*. Two live files quote DR-17; the table has **no `.sql` file**; it appeared in **zero**
of this feature's six artifacts until analysis pass 4.

**The decision is not to emit, and the reason is arithmetic rather than scope.** This chapter
owns `ready` and `rejected`. `uploaded` belongs to 4.10's slot route and `deleted` to FR-MED-10's
reap — so a producer here would fill the table with **exactly the two values DR-17's sum does not
read**.

**That is 4.6's finding rebuilt on purpose.** 4.6 found a rollup satisfying DR-10 over a table
that receives no events, read by a file nothing runs — both halves conforming to the clause and
the pair meaning nothing. Building half a producer for a consumer that reads the other half is
the same shape, and the way to avoid it is to build the producer and the consumer in one chapter.

---

## Carried and re-measured

### 057-2 · CLOSED — *"a message can attach an object nobody uploaded to"*

**The gate closes it and FR-MED-10 does not.** 4.11's predicate admits `pending`, so a message
could carry an object whose bytes never arrived; ADR-14's delivery gate now refuses a signed URL
until `ready`, and `ready` requires bytes that were fetched, scanned and measured. **The
attachment still parses** — the send path is unchanged — and what the entry was about is that a
client holding the id could get nothing. Now the platform says so with the same 404 it gives a
foreign object.

### 056-1 · NOT CLOSED, and narrowed — *"an unused slot holds its bytes forever"*

**This chapter does not touch it and must not claim to.** An object that was never uploaded to
holds no bytes at all; one that WAS uploaded to and never attached holds them until FR-MED-10's
reap, which is a later chapter. What 4.13 adds is that such an object is now **countable**:
`state = 'pending'` older than 24 hours is exactly the reap's population, and the sweep's own
window predicate names it. The lane's figure at this chapter's close is **4,077 pending against
291 ready and 88 rejected**.

### 058-1 · RE-MEASURED — a signed URL outlives the authorisation that produced it

**And the gate does not change it.** The hour is unchanged and the store still checks a
signature and has never heard of a channel. What this chapter adds is one more thing the URL
outlives: an object rejected a minute after a URL was issued keeps serving until the store
deletes the bytes — which happens inside the same request as the verdict, so the window is the
delete's own latency rather than the hour. Measured at 2 ms.

### 058-3 · RE-MEASURED — a malformed path parameter is still a 500 on sixteen routes

Unchanged, and this chapter's two new routes are not among them: `/internal/media/:mediaId/
verdict` takes a `ParseUUIDPipe` and answers 400, asserted. **Seventeen routes now take a uuid
path parameter and one validates it**, which is a worse ratio than the entry recorded and the
same number of defects.

### 058-4 · RE-MEASURED — three tenancy predicates no single-mutation probe sees

**A fourth arrives with the gate.** `readableMediaObjectKey` now carries `state = 'ready'`
alongside the environment scope, and deleting it turns two tests red — so unlike the three the
entry names, this one IS visible to a single mutation. The difference is that it guards a
STATE rather than a tenant, and the tenancy arms are still invisible for the reason 4.12 gave:
they are redundant with each other.



### 055-3 · `check:errors` still has no job

Re-measured at this chapter's close: five `check:*` scripts, and `ci.yml` runs four. This chapter
adds **no** error code — the verdict route's refusal reuses 4.11's `unprocessable_request`
deliberately, so `check:errors` stays at **34 codes, 34 sections**, asserted by hand in both
directions because nothing runs it.

### 056-10 · A comment that says *when* something runs must name its caller

**Applied rather than only carried.** `store.ts`'s *"on boot, every boot"* was corrected at 4.10;
this chapter found the same class twice more and fixed both in place: `repository.ts`'s
*"`'ready'` is unreachable today"* (made false by migration 0018) and
`authenticate.middleware.ts`'s compiler claim (059-3, never true).

**The checker is still unbuilt and the reason has not changed.** The targeted version's surface
is 13 lines in 10 files; the naive one reports 37 exports whose only callers are tests, nearly
all legitimate, and needs a hand-maintained allow-list.

### 050-8 · Two test files starting a process is not a deployment

**Narrower again, and moving the right way.** `services/media-worker` ships a Dockerfile and a
`compose.yaml` service, which is the first thing in this movement to close the shape rather than
restate it — the ingester still has neither. Two suites spawn the worker's *api*; the worker
itself is a container behind `--profile services`.

### 059-12 · A sweep that reads only the first page cannot reach a new object

**MEASURED AGAINST A LANE WITH REAL HISTORY, and it is the defect this chapter came closest to
shipping.** `GET /internal/media/pending` is oldest-first with a batch of fifty. The lane held
**3,849 rows in `pending`, 858 of them inside FR-MED-10's 24-hour window** — and an object
nobody uploaded to stays `pending` until the reap, so **the head of the queue never moves**. A
fresh upload was row 858 and was never reached: the sealed suite timed out at thirty seconds
with the worker running perfectly, the scanner current, and the log saying nothing, because it
logs only when something happened.

**AND THE CHAPTER'S OWN HEADLINE FIGURE ASSUMED THE FIX.** *"The whole backlog is 4.2 s serial"*
is the argument for a sweep over a client notice; it is only true if a sweep is a whole pass. A
fixed first page made the published arithmetic describe something the code did not do.

Two changes, and both are in the chapter: the batch query excludes objects older than
FR-MED-10's window, because an object pending for more than a day is the reap's; and the sweep
**pages** with a keyset cursor on `created_at` until a page comes back short, bounded by
`maxPages` so a queue growing faster than it drains cannot hang one pass.

**WHAT IS NOT CLOSED** is that the cycle time is a function of the queue. 858 objects at fifty
a page is eighteen pages a sweep — fine at 1.4 ms an object, and a number nobody has a bound
for. A tenant that takes ten thousand slots an hour and uploads none makes every other tenant's
upload wait, and the only thing that removes them is a reap that is not built.

### 059-13 · The composed worker could not reach the scanner, and nothing failed

**4.11's MinIO defect, one chapter later, in the service whose whole subject is reading bytes.**
`scannerConfigFromEnv` defaults to `localhost:3310`, which inside the container is that
container. The first composed run logged `scanner: "unreachable"` at boot and then behaved
perfectly: every object stayed `pending`, which is **FR-009 working exactly as designed**, and
the symptom of a correct refusal is indistinguishable from the symptom of an object nobody
uploaded to.

**The boot line is the only thing that said so**, which is why it prints the scanner's version
string rather than a boolean. `RELAY_CLAMAV_HOST: clamav` in `compose.yaml`, with
`depends_on: clamav: { condition: service_healthy }` — `service_started` would let the worker
begin against a database a fortnight old.

### 059-14 · The quickstart was wrong three times, and every one read as a platform defect

**NFR-USE-03 is a `T` clause at 100% and `ci.yml` contains the word `quickstart` zero times**
(055-3's neighbour), so running it is its whole verification.

    §2   asked for a delivery URL for an object it never attached      ready -> 404
    §3   the signed HEAD was an ellipsis, not a command                nothing to run
    §5   read `$ID`, which nothing assigned, twice                     two empty results

**The first is the instructive one.** FR-MED-08 authorises through a *referencing message*, so
an object nobody has sent is 404 whatever its state — the run reads as ADR-14's gate refusing a
verified object, which is this chapter's own subject failing. §0 creates a channel and a bot
for exactly that step and §1 never used them.

**And §5's is the shape 4.11 named**: three of its five lines were comments describing work
rather than doing it. **A step whose commands cannot run is indistinguishable from a step whose
subject is broken.**

### 059-15 · `quay.io/minio/minio` stopped being publicly pullable, and both platform CI jobs now die at step one

**NOT THIS CHAPTER'S, AND FOUND BY IT.** `compose.yaml:106` has said
`image: quay.io/minio/minio:latest` since chapter 4.10. It pulled on 2026-09-20 and on
2026-09-26 it does not:

    minio Error unauthorized: access to the requested resource is not authorized

Reproduced off CI, three ways:

    docker pull quay.io/minio/minio:latest                    401 Unauthorized
    docker pull quay.io/minio/minio:RELEASE.2025-04-22T…      401 UNAUTHORIZED
    docker pull minio/minio:latest                            pull access denied
    docker manifest inspect chainguard/minio:latest           OK

**IT BLOCKS EVERYTHING DOWNSTREAM OF IT IN BOTH JOBS.** `lanes` fails at
`docker compose up -d --wait …` and skips `build`, `migrate`, `apply`, `check:errors` and
`test:integration`; `sealed` fails at its own `up` before migrating. **Five of eleven steps
and none of six.**

**AND NO LOCAL RUN COULD SEE IT**, because the image is in this machine's cache and has been
since 4.10 — which is 056-10's shape exactly (a persisting local volume hid a bucket nothing
created) at the registry layer rather than the storage one. **The first machine without the
cache is CI, and CI is where it appeared.**

**CLOSED 2026-09-27 by reworking chapter 4.10, and the guesses in this entry's first draft
were wrong in the useful direction.** It read *"a different image: different entrypoint,
different credential variables, its own health check"*. Measured:

    binary            RELEASE.2026-09-22T19-25-18Z — the same MinIO, repackaged
    entrypoint        ["/usr/bin/minio"], so `command: server /data` is unchanged
    credentials       MINIO_ROOT_USER / MINIO_ROOT_PASSWORD, unchanged
    health check      `mc` is in the image; the compose check runs VERBATIM
    what DID change   it runs as uid 65532 where the old image ran as root

**ADR-30's REVERSAL CONDITION HELD, AND THAT IS THE RESULT WORTH KEEPING.** The argument for
signing our own URLs was that the store is replaceable; the store was replaced, and the signer,
the bucket layout, the presign probe and every media suite were untouched. **A claim that had
only ever been an opinion is now a measurement** — 768 of 768 on the api lane, 22 of 22 on the
worker's, 19 of 19 sealed, with no change outside `compose.yaml`.

**THE ONE COST IS A UID, AND IT IS A `chown` RATHER THAN A WIPE.** An existing volume is
root-owned at mode 755, so the new image dies with `FATAL Unable to initialize backend: file
access denied` — reproduced deliberately against a root-owned volume before it was written down.
`docker run --rm -v relay_minio-data:/d alpine chown -R 65532:65532 /d` migrates it with every
object intact, verified. **CI and a fresh clone never meet it**, which is the direction that
matters: the failure belongs to machines that already had the old image, and those are the
machines that could not see the registry break either.

**AND THE FIX WENT INTO HISTORY RATHER THAN ON TOP OF IT.** `README.md:8` promises a chapter's
tag checks out that chapter's platform, and a forward-only commit would have left `part4-ch10`
through `part4-ch13` pointing at four trees whose stack cannot start — which is the defect 047
found for Part 3 and deleted twenty-one tags over. The image block is rewritten in all
twenty-five commits from the one that introduced the store; the replaced history is
`backup/pre-minio-image-20260927`, pushed first, and it names the four old tag targets in its
own message.

**WHAT THE REWRITE COSTS A READER**, said rather than hidden: the comment inside those four
trees is dated after the commits that carry it. It records a registry failure measured on
2026-09-26 and sits in commits from the 19th onward, because the fence chain compares its END
state to `HEAD` — so whatever text those lines hold, every commit after the last one to touch
them must hold it too. **One text everywhere is the only shape the chain permits.**

### 059-16 · A per-error comparison can only say what the run executed

**THE SET IS ONE ERROR AGAINST THE BASELINE'S SIX, AND THAT IS NOT AN IMPROVEMENT.**

    baseline (058's push)   6 distinct   two query-plan assertions, a typing frame,
                                         two lane commands, one exit code
    this push               1 distinct   `Process completed with exit code 1.`
    new                     0
    gone                    5

**Five errors are gone because the tests that produced them never ran.** 059-15 killed both
jobs at the image pull. *A zero from an instrument is a claim about the corpus only if the
instrument can be shown to have read it* — and this instrument read nothing.

**AND TWO RUNS AFTER THE IMAGE REPAIR SAY WHAT ONE COULD NOT** (2026-09-27). With the pull
fixed the lanes job reaches its tests for the first time in this chapter's history — nine steps
of eleven where the broken run managed five:

    058's push, the baseline          6 distinct
    A · the image rework              5 · ONE new (`expected 201 to be 429`), two gone
    B · a docs commit on A's code     3 · ZERO new, three gone

**The new error in A is absent from B on identical platform code**, which is 057's definition of
a flake rather than a regression. It is `limits.itest.ts:417`, which spends three requests
against a `send` limit of 2 and expects a 429 — and **`limits/bucket.ts` is a FIXED 60-second
window** whose own comment states the cost: *"up to twice the limit across a boundary."* The test
pins no window instant, so three requests straddling a minute boundary make the third the first
of a new bucket and it answers 201. **That is 043's wall-clock minute bucket, still open, in a
file 043 did not sweep.**

**PINNED 2026-09-27, AND THE SUITE HAD ALREADY SOLVED THE OTHER HALF.** `limits.itest.ts:239`
carries `windowsSince`, which sums both keys so a straddling test still counts ten sends as ten
— and its comment reads as complete. It made COUNTING boundary-proof and **cannot make the
PLATFORM boundary-proof**: the limiter keys on the same minute, so the third request of a
straddled burst is the first of a new window and is allowed. **No sum recovers a 429 that never
happened.** Two of the five tests read a count and were already safe; the three that read the
platform's own answer — a 429, and an `x-ratelimit-remaining` of exactly `14` — were not.

`pinWindow` waits **only when the window is nearly over, and only for the sliver that is left**,
so the wait is bounded by the headroom rather than by the window — which is what that same
comment records as the difference between this and the fix whose failure mode was worse than the
fault. 3 s against a longest measured test of **143 ms**; it fires on 5% of runs. It sits in
`beforeEach` so a sixth test cannot bring the class back by being written without it.

**RUN RED WITH THE BOUNDARY FORCED**, which is the only thing that proves a pin does anything:
arriving 120 ms before a boundary with 200 ms inside the burst gives `expected 201 to be 429`
with the pin off — the CI error reproduced on demand — and green with it on.

**AND THE PROBE'S FIRST VERSION MADE THE MISTAKE THE FILE WARNS ABOUT.** It waited up to 60 s to
reach a boundary inside a hook with a 10-second limit and died `Hook timed out in 10000ms`,
so the pin was never reached and both arms read red. **A probe that cannot reach the thing it is
testing reports on itself** — 045's shape, one level in.

**B IS THE STRONGEST READING THIS INSTRUMENT CAN PRODUCE** — zero new against the pre-chapter
baseline and three fewer — and **it was unavailable from a colour**, which was red for all three
runs and for three different reasons.

**WHAT THE RUN DOES SAY**, and it is the half that is real: `relay-tutorial — build, docs
drift, fence chain` **SUCCEEDED** (SC-009), and so did `relay-platform — the Docker-free gate`,
which is the job 056 split out precisely so that a store outage could not hide the unit lane.
**Two jobs cannot hide each other** is the sentence that made this run legible at all: without
the split, one red would have covered both the real failure and the clean one.

### 059-17 · A grouped A/B on a flaky lane said the opposite of an interleaved one

**Measuring the pin's blast radius produced a wrong conclusion twice, and the second one is the
instructive half.**

    3 runs with the change, no control           1 failed | 228 passed, each time
      → read as "pre-existing"                   WRONG: no control had been run
    6 control runs, then 5 with the change       control 5 green / 1 red · change 0 green / 5 red
      → read as "the change is implicated"       WRONG: every control ran before every change
    3 INTERLEAVED pairs                          A 1 green / 2 red · B 3 green / 0 red

**The gateway lane fails one test of 229 on roughly a third of runs on this machine, and which
test it is moves** — `typing.itest.ts` twice, `membership.itest.ts` once, each passing 23 of 23
and 229 of 229 when run alone. `limits.itest.ts`, the file actually changed, was green in every
single run.

**THE GROUPED COMPARISON IS THE TRAP.** Running all of A and then all of B confounds the change
with everything that drifted between them — here the composed stack was stopped partway through,
which is load this project's own rule says to hold still. **Interleave, or the ordering is the
variable.** 045 measured twenty runs a side to compare two batteries and could say they were
comparable; six runs split into two blocks cannot say anything, and read as if it could.

**AND AN EXPERIMENT SEPARATED THE HALVES WHEN THE TALLY COULD NOT.** Keeping the structural
change and setting the headroom to zero — so the hook is still async and still merged, and
simply never waits — reproduced the reds. That ruled out *waiting* as the mechanism and should
have been the signal that the tally was measuring something other than the change.

### 059-18 · A query-plan assertion that required the planner to make a bad choice

**`session.perf.itest.ts:102` was red on every CI run in this project's recorded history**, and
both of its lines were the same mistake:

```
expect(plan).toMatch(/Index (Only )?Scan|Index Cond/);
expect(plan).not.toMatch(/Seq Scan on (environments|usage_periods)/);
```

**It asked whether the planner CHOOSES an index, which is a property of the corpus.** Reproduced
on a freshly migrated database — CI's condition, and any new contributor's first run:

    Nested Loop Left Join  (cost=0.00..4.29 rows=1 width=40)
      ->  Seq Scan on environments e    (cost=0.00..1.59 rows=1 width=48)
      ->  Seq Scan on usage_periods u   (cost=0.00..2.69 rows=1 width=24)

**Postgres is right.** Reading one page beats descending a B-tree, so the test demanded a bad
plan and passed only on a developer lane with 31,215 environments behind it. **A test that
passes because the machine is dirty is not passing.**

**THE QUESTION IT MEANT TO ASK IS ABOUT THE QUERY**: can the planner look this up through an
index at all — the defect 4.12 found, where a containment operand built from a joined column
left the index *present and idle*. `SET LOCAL enable_seqscan = off` asks exactly that and is
corpus-independent: green on a two-row database and on the lane's 31,215.

**AND `Index Scan` IS THE WRONG THING TO MATCH, WHICH THE RED PROBE FOUND.** With sequential
scans penalised the planner reaches for an index whether or not it can use one, and a predicate
it cannot push down comes back as an index scan carrying a **`Filter:`**. Measured against a
deliberately broken shape:

    the shape that ships      Index Cond x2   Filter x0
    WHERE e.id::text = $1     Index Cond x1   Filter x2

**An `Index Scan` assertion passes on both** — it would have replaced one corpus-dependent
assertion with one that cannot fail. `Index Cond` per table is the question: it says the
predicate reached the index rather than the rows. Run red on both databases with the broken
shape, green on both with the shape that ships.

**`SET LOCAL` INSIDE A TRANSACTION THAT ROLLS BACK**, on a dedicated connection from the pool,
so no other suite in the lane inherits a planner that refuses sequential scans — 056-5's *action
scoped wider than its own test*, which a bare `SET` would have been.

### 059-19 · Five suites failed on this session's own analytics backlog

While verifying the repair the api lane reported five failures, all at **~20 seconds** — the
ingester poll deadline (050-8). The cause was in the stream, not the code:

    ANALYTICS   msgs=1034   consumers=0

**059-6 predicted this and undercounted it.** That entry costed the media worker's own polling
at 17,280 rows a day; what filled the stream here was hours of a composed stack running for the
sealed-suite checks, and a suite that spawns an ingester has to drain the whole backlog before
it reaches the row it is polling for. Draining it — 1,000 then 34 in two batches — returned the
lane to **768 of 768**.

**It reads exactly like a regression** and the five test names have nothing in common but a
deadline. The tell is the duration: five tests failing at the same 20 s are waiting for one
thing, and no code change makes five unrelated assertions time out identically.

### 059-20 · A per-file branch pin is a claim about the machine, because the denominator moves

**`media.controller.ts` measures 33 branch points locally and 13 in CI** — same commit, same
Node **22.23.2**, all **136** test files green on both sides:

    local      30/33   90.90%
    CI         11/13   84.61%   three consecutive runs, identical
    the pin    89              set from ONE local observation

**This is not coverage's known run-to-run swing.** 045 measured that at about one function of
forty on identical code, and prescribed *"pin below the lower observation by the observed swing
and put both numbers in the config"*. Here the **denominator** changes, which is a different
thing: the two runs are not two samples of one quantity, they are two quantities. No value
pinned here means what the ratchet wants it to mean until that is understood.

**IT IS ONE FILE OF NINE, WHICH IS WHAT MAKES IT A LEAD RATHER THAN A SHRUG.** The eight sibling
pins this feature added on the same day hold in both environments. The odd one out is the only
decorated NestJS class among them, reached through DI — a candidate, not a finding, and said as
such.

**Pinned at 83 and the pin is honest again**: below the lower of two stable observations, still
able to catch a real regression in the four arms that file has. **The mistake being corrected is
mine and it is the one 045 wrote down** — I had one observation and pinned just under it, which
is a ratchet calibrated to a single machine.

### 059-21 · `pnpm test:integration` ran 0 of 63 suites in CI and turbo called it 14 successes

    Tasks:    14 successful, 14 total
    @relay/api           40 suites · did not run
    @relay/gateway       12 suites · did not run
                         63 suites · 0 ran
    integration gate: no summary from @relay/api, @relay/dispatcher, @relay/e2e,
      @relay/gateway, @relay/ingester, @relay/media-worker, @relay/test-harness

**The gate caught it and the step is red for the right reason** — which is the shape this
project has been building toward for six chapters: *assert the counted line, not the exit code*.
Turbo reported total success while nothing executed, and only the summary said so.

**NOT DIAGNOSED HERE AND NOT THIS WORK'S.** It is visible now because 059-15's image repair let
the job reach that step at all — before it, the lane died at `docker compose up`. The coverage
run in the same job executes all 136 files and passes, so **the suites are fine and the lane
that runs them is not**. 050's sentence, unchanged: *a green lane is a claim about what was
re-run.*
