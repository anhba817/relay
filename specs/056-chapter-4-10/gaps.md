# Gaps — feature 056, chapter 4.10, "the upload that never reaches us"

Every carried item **re-measured** rather than copied.

---

## NEW

### 056-1 · A slot nobody uploads to holds its declared bytes forever

`POST /v1/media` writes a `pending` row and the storage quota counts it. Nothing ever
takes it back. A client that asks for ten slots and uploads none has spent ten slots'
worth of its cap, permanently, with no object in the store to show for it.

**FR-MED-10's job is not this job.** It hard-deletes *unreferenced* media objects twenty-four
hours after a tombstone unlinks them — it is about media that was uploaded and then
orphaned. A slot nobody used was never referenced and never uploaded, so nothing about
that clause reaches it, and reading the two as one is the mistake this entry exists to
prevent.

**MEASURED, not reasoned about.** `storage-quota.itest.ts`'s refusal tests leave `pending`
rows behind on purpose and the sum counts them: the tenant capped at 1,000 bytes that was
issued 600 and then refused still reports 600 committed, and always will.

The reclaim needs a decision this chapter cannot make on its own — how long a slot lives
before its bytes come back, and whether the row is deleted or moved to a third state. It
also needs FR-MED-03's verification to tell an unused slot from an uploaded object, because
today the platform cannot see the difference: `state` is `pending` in both cases until
something checks the store.

Same shape as 054's daily job with no runner. **Recording it is the whole of what a chapter
can do about it**, and it is written into the chapter rather than only into this file.

### 056-2 · The quota counts declarations, not bytes

`declared_bytes` is what the client said. Nothing verifies it, because FR-MED-03 is a later
chapter, so a client that declares 1 KB and uploads 90 MB is inside its cap and over it at
the same time — and the same client is refused for declaring 11 MB of image while quietly
storing whatever it likes.

**What it permits, stated plainly**: the size cap and the storage quota are both advisory
against a hostile client until verification ships. What they are not is useless — they are
correct against an honest client and against a buggy one, which is what most of both is
for, and the store enforces its own limits on the object itself.

**AND THE SIZE REFUSAL IS THE SHARPER HALF.** A storage quota that undercounts costs the
platform money; a per-kind size cap that a client can walk past is a claim in the error
reference that is not true — *"the declared size exceeds the limit for its kind"* refuses
a declaration and not a file. The message says "declared" for that reason, which is honest
and is not the same as enforced.

### 056-3 · Two compose services claimed host port 9000

ClickHouse has published `${RELAY_CLICKHOUSE_NATIVE_PORT:-9000}:9000` since chapter 1.2.
Phase 1 of this feature added MinIO on `${RELAY_MINIO_PORT:-9000}`. They cannot both run:

    Bind for 127.0.0.1:9000 failed: port is already allocated     exit 1

**FIXED** — MinIO's host side moved to 9100 and the container side stayed at 9000, because
the host side is the hand-maintained table and chapter 1.2's claim was there first.

**WHAT IS STILL OPEN IS THAT NOTHING CHECKS IT.** Eleven published ports in `compose.yaml`,
allocated by hand, and the only reason this one was found is that a suite needed the
analytical store. 045 deleted the api's hand-allocated port map for exactly this reason and
replaced it with `PORT=0`; a compose file cannot do that, so the available instrument is a
check that the eleven host ports are distinct. Nothing runs one.

**AND THE FAILURE IS QUIET IN A SECOND WAY.** A stopped container restarted while its port
is taken comes back **running, healthy, and publishing nothing** — `NetworkSettings.Ports`
`{}`, not even the port that was free — because the health check runs
`clickhouse-client` inside the container. `docker compose up -d` printed `Started` and
exited 0. `--force-recreate` is what fixes it. A green health check is a claim about the
inside of the container, which is chapter 4.2's `/ping` finding on a different layer.

### 056-4 · A twenty-second deadline inside a five-second test

`services/api/vitest.integration.config.mts` sets no `testTimeout`, so this lane runs at
vitest's default of 5,000 ms. `request-log.itest.ts` polls for a row to a 20,000 ms
deadline. The poll's `return null` branch was unreachable and
`expect(await settle(id)).not.toBeNull()` was an assertion that could not fail: the test
was killed four times over before its own deadline could fire.

**AND THE TWIN CONFIG HAD IT RIGHT.** `vitest.coverage.config.mts:102` sets
`testTimeout: 60_000`. Two configs run `.itest.ts` files and they disagree — chapter 4.9's
finding on a different field, where a credential went into one and not the other.

**FIXED** in both suites with per-test budgets. **What is open is the config**: a lane-wide
`testTimeout` would be one line and would make every future poll's deadline mean what it
says, and it is not this chapter's to change — `vitest.integration.config.mts` is fenced in
chapter 2.1 and a lane-wide timeout change belongs to a chapter about the lane.

### 056-5 · A test may not take a shared service away from its neighbours

FR-017's truest test is `docker compose stop minio`. The lane runs two files at a time, so
while the media suite had the store stopped, `src/isolation/gauntlet.itest.ts` asked for a
slot and got a 503 where it expected a 201 — **two of three runs**, failing in a file that
never mentions media storage.

045 found eight ASSERTIONS scoped wider than their own subject and built
`check-lane-scope.py` to find the class. This is an ACTION scoped wider than its own test,
and no instrument sees it: the script reads SQL text, and `execFileSync("docker", ...)` is
not SQL.

**WORKED AROUND** — the endpoint moves instead of the store, to a port the kernel refuses,
for the duration of one request. **What is open is the class.** A test that stops a
container, drops a table, or changes a global setting is invisible to every gate this
repository has, and the symptom is a red in somebody else's file.

### 056-6 · `docs/12` says four refusals where FR-MED-02 names three

The specification's own note, carried here so it outlives the feature. The fourth turned
out to be `docs/05-sad.md:1062`'s degradation row — *"Object storage lost … Upload slots
return a specific error"* — and it shipped as FR-017 and `media_storage_unavailable`.

**CLOSED by construction**, and recorded because the specification was written saying the
fourth was unexplained. Analysis pass 1 found it in the SAD; the lesson is the one this
project keeps paying for, which is that the answer was in a published document nobody had
opened in that pass.

### 056-7 · A list of fenced files goes stale, and the instrument that checks it is not `patch`

The task table said twelve files and named `services/api/src/db/catalogue.ts`, which this chapter
never touches. The checker says **seventeen**, and the six it missed all arrived from repairs made
after the table was written: the lint rule that moved the query into the repository, the harness
guard's three edits, the `Record<Dimension, string>` the compiler demanded, the gauntlet's attack,
and FR-016's test against a real id.

050's sentence, for the second time in five features. What is new is the second half.

**`patch --dry-run` IS NOT THE CHECKER**, and it said yes to seven hunks the checker refused with
`hunk pre-image matched 0 times`. `patch` applies with fuzz and offset; the checker needs exactly
one exact match. Rule 1a says generate hunks from the checker's own replay, and the same is true
of verifying them — the instrument that answers *"will this anchor"* has to count exact
occurrences of the pre-image, which is nine lines of JavaScript and agrees with the checker on all
seventeen.

**OPEN**: nothing in the repository does that count. It was written for this feature and lives in
its scratch directory. The next chapter that edits a deep-chain file will write it again.

### 056-8 · A container is two edits and only the full coverage lane says so

`compose.yaml` gained a sixth service and `@relay/config`'s `INFRA_SERVICES` did not. The
assertion that caught it was written by the chapter that added the fifth — *"a container added to
compose and never registered here was invisible"* — and it caught the sixth exactly as intended.

**What is open is the eleven minutes.** `packages/config` is a unit test in a package no
integration suite imports, so nothing this feature ran could see it: `pnpm test:integration`
plans the api, gateway, dispatcher, ingester, e2e and harness lanes and not that one, and the
only command that reaches it is `pnpm coverage`, which takes 664 seconds. **A green lane is a
claim about what was re-run**, and the cheapest instrument that would have caught this in a
second is `pnpm --filter @relay/config test` — which nothing tells anybody to run after editing
`compose.yaml`.

**FIXED** for this chapter: `minio` in `INFRA_SERVICES`, `minio-data` in `DURABLE_VOLUMES`, 7 of
7. The class is open.

---

## CARRIED, AND RE-MEASURED

### 050-8 · The ingester is a process no gate starts — OPEN, and narrower than it was

Re-measured. `services/ingester` still has no Dockerfile and no service in `compose.yaml`, and
`ci.yml` starts nothing. What has changed is who copes: **two suites now spawn it themselves** —
`request-log.itest.ts` since chapter 4.9, and `media.itest.ts` in this chapter, which needs it for
SC-001's instrument.

So the gap is no longer *"these suites are red on any machine with no ingester"*. It is the
original sentence underneath that one: **on the stack this series ships, a customer reading their
own request log finds it empty**, because records are published and nothing drains them. Two test
files starting a process for their own duration is not a deployment.

### 055-3 · `check:errors` is a script no workflow runs — OPEN, unchanged

Re-counted: **five `check:*` scripts in `relay-tutorial/package.json`** — `check:docs`,
`check:errors`, `check:fences`, `check:figures`, `check:srs` — and the tutorial job at
`ci.yml:184-205` runs `lint`, `build`, `check:docs`, `check:srs`, `check:figures`, `check:fences`.
`check:errors` is the one with no job, and this chapter added five error codes and five reference
sections behind it. T029 ran it by hand, in both directions, which is the only reason the
discrepancy would have been caught.

### 055-4 · A gate that exits 0 having looked at nothing — OPEN, and `cwd` is not the condition

Re-measured from an unrelated empty directory, all seven gate scripts printed their **counted
success line with the repository's real figures**:

    check-docs-drift      all mirrored docs match their sources
    check-srs-ids         245 clause rows, 245 unique identifiers
    check-revision-order  18 revisions ascend, 1.0 to 1.17
    check-fence-chain.sh  290 fenced files replay onto relay-platform across 53 chapters
    check-fence-chain.mjs the same line
    check-error-codes     33 codes, 33 sections
    check-figures         284 figures, 286 bindings resolve

Every one resolves its corpus from the script's own location, so **running the real script from
somewhere else is not how a corpus goes absent** — which is the complement of 055-5, where a
*copy* at another path replays nothing and exits 0. The entry's line numbers still name real
early-exit paths; what this re-measurement adds is that the obvious way to reproduce it does not,
and that **the rule it produced is what told the two apart in one command**: assert the counted
line, not the exit code.

### 056-6 · answered — `docs/12` row 11 is amended rather than left to drift

The row said four refusals where FR-MED-02 names three, and the row was right. The fourth is
`docs/05-sad.md:1062`'s degradation row and it is FR-017 now. Row 11 carries what the line did not
say, in the form the document already uses four times: no object storage existed at all, the
storage quota is a level where the other three are flows, and the presigned URL's independence
from the store is what made the fourth refusal cost a round trip.

### 056-9 · One failing unit test skips six steps, and every other error in that job is downstream of it

The platform CI job ran, in order: `install`, `lint`, `typecheck`, `test`, **`coverage`**. Nothing
else. There is no `continue-on-error`, so the failure of `pnpm test` skipped `pnpm build`, the
migration, `analytics/apply.mjs`, the error-registry gate and `pnpm test:integration` — and
`pnpm coverage` ran anyway, because it carries `if: always()` for the reason chapter 4.8 gave.

So the job's other errors are not separate problems:

    Table relay_analytics.api_requests does not exist       analytics/apply.mjs never ran
    ingester/dist/main.js does not exist                    pnpm build never ran
    expected 0 to be greater than 0                         the same, one layer on

**The one real failure is `main.test.ts > logs exactly one structured line per request`**, which
gets two. It has failed in CI and passed locally since before this chapter, and the second line is
almost certainly `request_log.publish_failed`: the unit lane is Docker-free by design, `nats` is a
service container so the connection succeeds, and nothing creates the `ANALYTICS` stream in that
job — so the producer chapter 4.4 added logs an error beside the request line. Locally the stream
exists from compose and the test sees one line.

**AND THIS IS THE CHAPTER'S OWN SUBJECT POINTED AT THE CHAPTER.** Chapter 4.9's finding is that a
gate which is always red carries no information about what a change did to it. This feature pushed
two new failures into that job — `expected 503 to be 201`, twice, because `ci.yml` had no MinIO —
and **the run's colour did not change**. What found them was diffing this run's `##[error]` lines
against the previous run's, which produced exactly two new ones and nothing else.

**FIXED for this chapter's half**: MinIO is provisioned in the platform job from `compose.yaml`'s
own definition, placed **before** `pnpm test` rather than beside the other provisioning steps,
because a step after the first failure never runs while the lane it provisions for still does.

**OPEN**: the unit-lane log line, and the shape of the job. A `continue-on-error` on the early
gates, or an `if: always()` on the provisioning, would make a single unit failure stop hiding five
other results. That is a CI decision rather than a chapter's, and 054-1 is the neighbouring item.
