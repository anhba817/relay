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
