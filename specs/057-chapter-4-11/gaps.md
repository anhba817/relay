# Gaps — feature 057, chapter 4.11, "the half of the union that was refused"

What this chapter found and did not close, and what it carried in and re-measured. Every
carried item is **re-measured rather than copied**: four of 043's twenty-three were wrong
when somebody finally looked, and three had closed with nobody working on them.

---

## New

### 057-1 · Nothing counts references to a media object

**Measured.** `grep -rn media_id` across `services/`, `scripts/` and `analytics/`, filtered
for `count` or `refer`: **zero hits.** No query, no column, no job.

This chapter creates the first references there have ever been. FR-MED-10's sweep
*"hard-deletes unreferenced media objects 24 hours after a tombstone unlinks them"*, and the
only way to answer *"unreferenced"* today is a scan of `messages.attachments` — a `jsonb`
column with no index on its contents, across every message in the environment, for every
object. The sweep is movement VI's and this is the shape of the bill it inherits.

**What this chapter did instead**: nothing, deliberately. Building a reference count now
would be a column maintained by one writer and read by nobody until a later chapter, which
is the `daily_usage` shape 4.6 spent a chapter on — a rollup that existed for two chapters
and was read by a file nothing ran.

### 057-2 · A message can attach an object nobody uploaded to

`state` is `pending` whether or not the client ever PUT the bytes, because the api is never
told (056-1). So a message may name a slot that holds nothing, and every client that
receives it renders a broken image with no way to tell that from a slow upload.

**Made worse by this chapter and not caused by it.** Before today the arm refused, so the
dangling slot was a row nobody could reference. FR-MED-03's verification — *"objects that
contradict their declaration shall be rejected"* — is movement VI's, and FR-MED-09 asks that
a rejected attachment render as an explicit marker rather than a broken link. Both need a
state this schema currently refuses to hold (SC-006).

### 057-3 · `attachment_count` changes meaning, and the loader does not know

`scripts/scale/load-analytics.mjs` computes `JSONLength(m.attachments)` at lines 178, 187
and 200. That number has counted **external URLs** for every row ever written, because the
media arm refused. From this chapter it counts hosted objects alongside them, in the same
column, with nothing distinguishing the two.

**No analytical clause names the distinction**, so nothing is wrong today — and a chapter
that later asks *"how much media do tenants send?"* will read a column whose meaning changed
under it without a migration, a version or a comment. Recorded here and in the chapter's
prose rather than fixed, because the fix is a decision about what the column should mean and
that belongs to whoever asks the question.

### 057-4 · `zod-validation.pipe.ts` has an arm with no producer and no pin

**Measured at 52.17% branches** in this chapter's coverage run. `protocolCode` was built by
3.24 for `media_not_available` alone and this chapter removed its only producer; the
mechanism is kept (T015) on 4.10's `service_unavailable` precedent — a general extension
point with a stated role outlives its last caller — against 4.6's opposite precedent, which
reached 100/100/100/100 on `metering.ts` **by deleting** two unreachable arms.

**What is open is not the decision but the instrument.** The file carries no coverage pin,
so nothing reports the uncovered arm either way, and the next reader meets a branch with no
caller and no number. Pinning it at the measured 52 would pin a figure that only means
something while the arm is dead.

### 057-5 · The composed stack and the integration lane cannot both run

`pnpm test:integration` reported **11 of 12** with `docker compose --profile services`
running, red on `outbox.itest.ts > invariant 8: two concurrent relays publish every row
exactly once`. The same test alone: green. The whole lane with the services stopped: **12 of
12**.

The composed api, gateway and dispatcher are a second set of relays polling the same
`outbox` rows as the lane's own. 056 recorded a test taking a shared service away from its
neighbours (`docker compose stop minio`); this is the same class from the other side, and
neither `check-lane-scope.py` nor anything else can see it — the contention is between a
process and a lane, not between two queries.

**Nothing is fixed.** A note in the quickstart would help a reader and would not help CI,
where the `lanes` job starts stores only.

### 057-6 · `RELAY_MINIO_INTERNAL_ENDPOINT` has one consumer and no check

The split exists because the presigned URL and the api's own probe need different addresses
(FR-026), and `compose.yaml` is the only thing that sets it. Nothing asserts that a
deployment which sets one sets the other sensibly: an operator who points
`RELAY_MINIO_ENDPOINT` at a public CDN and forgets the internal one gets a probe against the
CDN, which may answer 200 and prove nothing about the bucket.

The class is 4.2's — *"a check that cannot fail for the reason you care about is not a
check"* — one level out, and it is filed rather than built because the guard would have to
know what a store is, which is the thing ADR-30 spent a chapter avoiding.

### 057-7 · The sealed suite has never run in CI — FOUND AND FIXED HERE

`ci.yml`'s outsider job died at its migrate step on **every run**:

    Error: Cannot find module
      '/home/runner/work/relay/relay/services/api/dist/db/migrate.js'

The path is missing `relay-platform/`. Two of the three jobs in that workflow set the
directory once under `defaults`; this one repeats it per step, and **the repetition is what
made it possible to miss one.** So the job exists, it is red, and it has never reached the
suite it is named for.

**This chapter is what made it matter.** FR-021 adds a media test to that suite and T073a's
premise was *"CI gives it a job of its own"* — true, and the job had never got there. 4.9 found
the same shape in the integration gate (*"the gate was already red, so a planted drift deepened
a red rather than turning one"*) and 4.10 found `pnpm test:integration` skipped for nine
features. **A job's colour says nothing about which step produced it.**

Fixed — one line. **CLOSED, and the prediction in this entry was wrong.** It said the first green
run would report *"nine features of accumulated drift"*; the suite ran **19 of 19 on both runs
after the fix**, including this chapter's media test. The drift a dead gate hides is a reasonable
fear and it was not what was there — which is worth more than the fix, because the same fear is
what makes a dead gate tolerable to leave.

### 057-8 · The lanes job's error set is not stable run to run

T076 compares CI **per error rather than per colour**, which is 4.10's method and the only way
to read a workflow that is red either side of a chapter. Across three runs, planner cost
estimates normalised:

    e8b5c3c  baseline        3 distinct
    e539403  the chapter     3 · empty diff both ways
    8bc0a8f  the CI fix      6 · three extra
    81761a0  the record      3 · empty diff both ways

The three extras are absent from the run before **and** the run after: a `reset-lane` whole-table
assertion (*"the reset removed an organisation: expected 1 to be 3"*), a second query-plan
assertion, and the harness package failure they produce.

**056 COMPARED ONE RUN AND CALLED THE SET IDENTICAL.** So did this chapter, until a second and
third run existed to compare. The claim one comparison supports is *"this run introduced nothing
new"*; *"the set is stable"* needs more than one, and here it would have been false. The method is
still right and its resolution is now known: **a single per-error comparison can report a flake as
a regression, or miss one.**

Nothing is fixed. The two flaky assertions are shared-state ones of a class 043 and 045 both
recorded — `reset-lane` counts rows a neighbour can move — and finding them properly means
running the lanes job several times against one tree, which no chapter has budgeted.

---

## Carried, and re-measured

### 056-1 · An unused slot holds its bytes forever — OPEN, and now reachable

Still true, and this chapter changes what it costs. A slot nobody uploads to is a row and a
quota charge; before today it was unreferenceable, and now a message can name it (057-2).

### 056-2 · The quota counts declarations — OPEN, unchanged

`declared_bytes` is what the tenant asked for, not what arrived, and nothing reconciles the
two. Untouched by this chapter, which adds no byte accounting of its own.

### 056-9 / 056-10 · CLOSED at 056's follow-up — **confirmed still closed**

`pnpm test` ran **12 of 12 tasks, 71 files** with every store pointed at this machine's
running stack and again as the Docker-free gate; `ci.yml`'s `gates` job still carries no
service containers. The comment convention (a claim about when a symbol runs names its
caller) held through this chapter's edits to `store.ts`.

### 055-3 · `check:errors` has no CI job — OPEN, and this chapter is why it matters

**Re-measured**: five `check:*` scripts, and `ci.yml` runs `lint`, `build`, `check:docs`,
`check:srs`, `check:figures` and `check:fences`. Not this one.

This is the first chapter to both **delete** a code and **add two**, so the registry and the
reference moved in both directions at once — exactly the case the checker compares. It was
run by hand at every step and reports **34 codes, 34 sections**. Had it been wrong, nothing
in CI would have said so.

### 050-8 · Nothing drains the analytics stream — OPEN, narrower than filed

Two suites spawn an ingester for their own duration and nothing else does. This chapter adds
no analytical producer and no suite that needs one.
