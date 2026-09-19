# Tasks: chapter 4.10 — the upload that never reaches us

**Feature**: `specs/056-chapter-4-10` · **Plan**: [plan.md](./plan.md) ·
**Research**: [research.md](./research.md) — read it first, it settles the specification's one
flagged assumption against the assumption.

**Read before executing any task**: every figure below was measured on 2026-09-18 against
`quay.io/minio/minio` and the tree at `554dd6b`. A task that names a number is quoting that
measurement rather than asserting it. **Check a task's premise before executing it** — feature
055 found eight of nine held and the ninth was the whole of T008.

**The gate loop, after anything that touches a fence**:

    pnpm check:fences 2>&1 | grep 'problem(s)\|replay onto'

**Not `| tail -1`**, which prints pnpm's `ELIFECYCLE` line and never the count. The chain is at
**0**; report the absolute number, not a delta.

---

## Phase 1: Setup — the store, and a health check that can fail

**Goal**: object storage exists in the local stack and something proves it is reachable for the
reason this chapter cares about.

- [X] T001 **DONE — `quay.io/minio/minio:latest`, 241 MB**, `server /data`, a named volume and `RELAY_MINIO_PORT`. `minio/minio` is `pull access denied` as predicted. Original: Add a `minio` service to `relay-platform/compose.yaml` using **`quay.io/minio/minio`**, with `MINIO_ROOT_USER` and `MINIO_ROOT_PASSWORD` from the environment and a port mapping beside the four existing stores.
  **THE REGISTRY IS PART OF THE NAME.** `docker run minio/minio` fails on this machine with `pull access denied for minio/minio, repository does not exist or may require 'docker login'`, and `docs/05-sad.md:1002` names MinIO without a registry. Four images were tried: `quay.io/minio/minio` (241 MB) and `chrislusf/seaweedfs` and `adobe/s3mock` pull; `bitnami/minio` does not.
- [X] T001a **DONE — `minio: { condition: service_healthy }`** beside postgres, nats and redis, with the reason clickhouse is absent written into the file. Original: Add the store to the **api's `depends_on` with `condition: service_healthy`**, beside `postgres`, `nats` and `redis`. Not beside `clickhouse`, which is absent from that list because the api never touches it at boot — this store the api reaches **on every slot request**.
  **WITHOUT IT THE FIRST SLOT REQUEST CAN FAIL FOR A STARTUP REASON**, and FR-017 makes that failure `media_storage_unavailable` — correct, and indistinguishable from a real outage. A refusal that is right for the wrong reason makes the quickstart read as flaky, which is worse than a crash.
- [X] T002 **DONE, AND PROBED IN BOTH DIRECTIONS.** The check is `mc alias set … && mc ls`, the authenticated shape ClickHouse's uses. Correct credentials **exit 0**; a wrong password **exit 1** with `The request signature we calculated does not match`. And **`/minio/health/live` answers HTTP 200 to a caller with no credentials at all** — the `/ping` shape that was green for sixteen chapters. Container healthy, failing streak 0. Original: Give the service a health check, and **write down what its failure looks like from outside** rather than what the config says. **T001a's `service_healthy` waits on this check**, which is a second reason it has to be the signed round trip and not the liveness probe. `/minio/health/live` answers 200 from the host — measured — and that is the shape chapter 4.2 warns about: ClickHouse answered `/ping` with `Ok.` for sixteen chapters while every query from outside its container was refused. The liveness probe is the container's; T009's signed round trip is the chapter's.
- [X] T003 [P] **DONE IN PHASE 2 — it cannot precede the signer it uses.** `ensureBucket` returns `created` or `exists` and throws otherwise; `BucketAlreadyOwnedByYou` is what makes running it on every boot safe. This task creates the bucket with the signer T007 writes and sat in phase 1 marked `[P]`. Recorded in `baseline.txt` rather than reordered silently; the work is done beside T007. Original: **Create the media bucket from the api on boot, with the signer this chapter already writes.** Not an entrypoint, not a migration-like script: measured in analysis pass 6, `PUT /{bucket}` signed the same way answers **200**, `HEAD /{bucket}` answers 200, and a second create answers **`BucketAlreadyOwnedByYou`** — a named error to branch on, which is what makes running it on every boot safe. No `mc` invocation, no entrypoint wrapper, no fourth moving part.
  **THE ANALYTICS RUNNER IS THE PRECEDENT THAT LOOKS RIGHT AND IS HEAVIER.** `analytics/apply.mjs` is a separate script with a ledger because ClickHouse DDL is versioned and forward-only; a bucket is one idempotent call. An open decision in a task invites whoever reaches it to pick the precedent, so this one is decided here.
- [X] T004 [P] **DONE — AND `turbo.json` HAS NO `globalEnv`.** Its top-level keys are `$schema` and `tasks`; environment is per task. `test:integration` carried **25** keys and now carries **29**. Original: Add the store's address and credentials to the api's environment, and to `turbo.json`'s `globalEnv`. **`globalEnv` is a fenced file** in ten chapters plus two appendix hunks; adding a key is a chain edit.
- [X] T004a **DONE — four keys in each of the two configs.** Original: **AND TO BOTH VITEST CONFIGS, WHICH IS WHERE THE LANE ACTUALLY GETS THEM.** Two configs run `.itest.ts` files: `services/api/vitest.integration.config.mts` (4 env keys today) and `vitest.coverage.config.mts` (7). They are **already divergent**, which is exactly what makes the second easy to miss.
  **THIS IS CHAPTER 4.9's DEFECT, VERBATIM.** Its record: *"THE FIX WAS RIGHT IN ONE CONFIG AND MISSING FROM ITS TWIN … `pnpm coverage` stayed red and kept the gauntlet skipped in the run that measures constitution VI's own coverage bar, until eight minutes of a coverage run said so."* An earlier draft of T004 named the api's environment and `turbo.json`, which is neither config.
- [ ] T004b End this phase by running **`pnpm coverage`**, not only `pnpm test:integration`. The twin is only visible from the run that uses it, and eight minutes is what finding out cost last time.
- [X] T005 **DONE — packages 60 before, 60 after, delta ZERO**, across every `package.json`, with **0 S3 clients** anywhere. The stack comes up with `minio` healthy beside the four stores. Original: Confirm `docker compose up -d` brings the store up beside the four existing ones and that `pnpm test:integration` still reports every lane. **And measure the package count across every `package.json` in `relay-platform`, before and after: it must move by ZERO** (SC-010). One container is not one dependency — `docs/12` carries no dependency count, and the "5 → 6" in this project's record is chapter 4.5's gateway package count. Chapter 4.9 built `scripts/integration-gate.mjs` for exactly this: turbo's own summary counts tasks and does not reproduce run to run.
- [X] T006 **DONE.** Commit phase 1.

**Checkpoint**: a store exists and something can reach it.

---

## Phase 2: Foundational — the signature, which everything rests on

**Goal**: a presigned URL this platform produces is accepted by the store. **Blocks all three
stories.**

- [X] T007 **DONE — 104 lines in `services/api/src/media/presign.ts`, no package.** Typecheck and lint clean. Original: Write the SigV4 presigner in `relay-platform/services/api/src/media/presign.ts`, with **`node:crypto` and no dependency**. Five HMAC-SHA256 rounds over a canonical request; 28 lines in the probe. The workspace has no S3 client of any kind — zero matches for `@aws-sdk`, `minio` or `aws-sdk` across every `package.json` — and this chapter adds none.
  **THE CANONICAL REQUEST IS UNFORGIVING AND ITS FAILURE MODE IS A BARE 400.** `UNSIGNED-PAYLOAD`, the exact signed-header list, the path encoded segment by segment. A unit test against an expected string tests the test; the acceptance is T009.
- [X] T008 [P] **DONE — 8 of 8.** Six parameters and no others, stable for a pinned clock, different one second later, `/{bucket}` with no key segment, segment-by-segment encoding, 900 by default, the method signed, the credential scoped. **None of it can say the store accepts the URL** — a consistently wrong signature passes all eight. Original: Unit-test the presigner's shape: six query parameters and no others — `X-Amz-Algorithm`, `X-Amz-Credential`, `X-Amz-Date`, `X-Amz-Expires`, `X-Amz-SignedHeaders`, `X-Amz-Signature` — and a stable signature for a pinned clock and pinned credentials.
- [X] T009 **DONE — 9 of 9, three consecutive runs. And one published result was wrong.** The tampered signature answers **403 `SignatureDoesNotMatch`**, not the 400 planning published: that 400 was the probe's own shell rebuilding the URL as `${URL%?*}?…`, which splits on the **last** `?` and sent something malformed. **The test found it by asserting the published figure and going red**, and two independent checks afterwards agree on 403. Corrected in `plan.md`, `research.md`, `contracts/`, `tasks.md`, `quickstart.md` and `CLAUDE.md`. Original: **The round trip against the running store, which is the real health check.** Nine results, all measured before this plan was written — the first five in the probe that produced it, the last four in analysis pass 6, which found the first five were **all about objects** while the probe had created the bucket with `mkdir`:

        PUT  /relay-media                 200   the bucket, signed — a DIFFERENT canonical URI,
                                                `/{bucket}`, no key segment, no trailing slash
        HEAD /relay-media                 200
        PUT  /relay-media again           BucketAlreadyOwnedByYou
        unsigned LIST of the bucket       403

  and then the five about objects:

        PUT with the presigned URL, no client library, no auth header    200
        the same object through a signed GET                            200, byte-exact
        an UNSIGNED GET of that object                                  403
        a URL whose X-Amz-Expires has passed       AccessDenied · "Request has expired"
        one character of X-Amz-Signature changed                        403

  **Four of those five are requirements of this chapter or the next.** The 403 is FR-MED-08's precondition holding by default rather than by configuration, and the expiry comes from the **store**, which is what FR-003 asks for. Assert all five.
- [X] T010 **DONE — lint exit 0, typecheck exit 0.** Original: Run lint and the api's unit lane; commit phase 2.

**Checkpoint**: the platform can issue a URL a client can use and nobody else can.

---

## Phase 3: The slot (US1) 🎯 MVP

**Goal**: a caller declares an upload and receives a `media_id` and a URL. **Independently
testable**: request a slot, upload to it directly, and confirm the api saw one request.

- [X] T011 [US1] **DONE — `0015_media_objects.sql` and the drizzle table.** Nine columns, `user_id` nullable. **And the first attempt invented a table**: the migration did `INSERT INTO __sentinel_rows`, which does not exist — the guard's list is a literal in `sentinel.sql` and joining it is three edits in `packages/test-harness`. Original: Add the media table to `relay-platform/services/api/src/db/schema.ts` and **`services/api/migrations/0015_media_objects.sql`** — the tail is `0014_connection_minutes.sql` and `migrate.ts` orders by filename with no journal, so two tasks each reaching for "a migration" is a silent collision in a forward-only ledger (ADR-16). T031 takes `0016`. The columns: `id`, `environment_id`, `user_id` **nullable**, `filename`, `mime_type`, `declared_bytes`, `state`, `object_key`, `created_at`. `user_id` is nullable because an API key has no user and FR-MED-06 later distinguishes the two.
  **AND THE TABLE JOINS THE SENTINEL LIST**, with its bait row and its case in `guard.itest.ts` — the array's own documented rule is that a table joins *in the chapter that creates it*.
  **THAT RULE IS NOT WHAT THE TREE DOES, AND THE NUMBER IS WORTH KNOWING BEFORE QUOTING IT.** The comment says *"every table that carries `environment_id`"*; measured, **7 of 12 do**. `api_keys`, `webhook_endpoints`, `webhook_deliveries`, `webhook_dead_letters` and `webhook_disable_notifications` carry the column and are not guarded. The instruction stands — join it — but file the five rather than repeating a rule the repository has broken five times.
- [X] T012 [US1] **DONE — `direct`, and `tenant-scope.itest.ts` is what would have failed.** Original: Add the path to `services/api/src/db/catalogue.ts`'s tenancy map — `direct`, since the row carries `environment_id`. **The refusal is in `services/api/src/isolation/tenant-scope.itest.ts:42`, not in the catalogue**: `these tables have no path to an environment: …`. The catalogue is the data; the test is what fails. A task that names the wrong file sends somebody to the wrong file.
- [X] T013 [US1] **DONE — `kinds.ts`, one place, read by both.** And `kindOf("constructor")` returned a function until `Object.hasOwn`. Original: Write the allowed-MIME set and the per-kind caps **in one place** in `services/api/src/media/`, read by both the refusal and the cap lookup. A MIME list that disagrees with itself refuses the wrong things.
- [X] T014 [US1] **DONE — `POST /v1/media`, and the compiler found two walls.** The drizzle query was refused by constitution I's lint rule and moved to the repository; and `ErrorCode`/`Dimension` forced T021's codes and T031's parser half forward. Original: Implement the slot route, `POST /v1/media`, per `contracts/upload-slot.md`. It accepts a user token or an API key, scopes the row to the authenticated environment, and returns `media_id`, `state: "pending"`, `upload_url` and `expires_at`.
- [X] T014a [US1] **DONE — registered, and the route 404s without it.** Original: **Register the module in `services/api/src/app.module.ts`'s `imports` array**, beside the other fifteen. Without it the route does not exist and T016, T018 and all four refusal tests get a 404 — which reads as a routing bug rather than a missing line. **Chapter 4.6 shipped this exact omission in a different file**: `pnpm build` said `Error: Unknown chapter id: 4.6` because a registration edit was refused and nothing caught it, and its record says *"registering the chapter is a task no requirement had named."*
  **AND IT IS A CHAIN EDIT TOO.** `app.module.ts` is fenced in **11 chapters plus one appendix hunk**, so the registration needs a hunk in this chapter and a byte-identical Vietnamese twin. See T048.
- [X] T015 [US1] **DONE — nine columns, none of them the URL.** Asserted two ways: the row stringified holds no signature, no `X-Amz-` and no endpoint, and the column list is pinned. Either half alone passes on an empty row. Original: **Store nothing about the URL.** It is derived from the row and the store's credentials at request time. Storing its expiry would make two sources of truth for one fact, and T009 measured which is authoritative: the store answers `Request has expired` from its own clock.
- [X] T016 [US1] **DONE — 5 records drained, 5 slot requests, 0 for the 44-byte PUT.** The suite spawns the ingester and reports what it drained. The first version's before/after count was a neighbour's problem one file down; scoped by `ts` instead, with the slot's own row as the non-zero floor. Original: Integration test: a slot is issued, the client uploads to the URL, and **the api's own request log shows the slot request and nothing else**. Chapter 4.8's surface is the instrument — a byte through the api would appear there.
  **AND THE SUITE SPAWNS THE INGESTER, BECAUSE NOTHING ELSE DOES.** The request log is written by `services/ingester`, which has **no Dockerfile and no compose service**, so those rows do not exist on a machine where nothing drains the stream — `request-log.itest.ts:29` records those tests as *"red on any machine with no ingester since chapter 4.4"*. Chapter 4.9 closed `gaps.md` 050-8 by starting the process in `beforeAll` and killing it in `afterAll`, and reporting what it drained. **Copy that shape, not the sentence**: a probe copied from 049 once kept the hazard and dropped the guards. Without it this test asserts an empty table and passes.
- [X] T017 [US1] **DONE — asserted as a PAIR.** An API key's row carries no user and a user token's does; neither assertion alone means anything against a column that is always the same. Original: Integration test: an API key gets a slot and the row carries **no** user; a user token gets a slot and the row carries the user.
- [X] T018 [US1] **DONE — `unclassified: ["POST /v1/media"]`, the eighth time.** `44 derived, 37 attacked, 6 exempt` before the entry. `credential` and not `write` (nothing in the body to forge), `accepts: "either"` (the controller declares both). Original: **Classify it first.** The gauntlet derives routes from the running router, and `targets.ts` is a **hand-maintained list** of `{ method, path, accepts, shape }` entries. `targets.itest.ts:66` asserts *"classifies every derived target exactly once"*, so the moment the module registers, that suite fails with `POST /v1/media` **derived but unclassified**. Add the entry; `accepts` and `shape` are the two decisions.
- [X] T018a [US1] **DONE — 58 of 58, and run red on purpose.** `shared/${id}` in place of the environment prefix: `expected '/relay-media/shared/…' to contain '/dbafd039-…/'`. Original: **Then attack it.** With the entry present, `targets.itest.ts` goes green and the gauntlet goes red the other way: **classified but never attacked**. The attack plants a row for each of two tenants and asserts neither sees the other's.
  **TWO DIRECTIONS, IN TWO SUITES, AND THEY FAIL IN ORDER.** Chapter 4.8 walked this sequence — `43 derived, 42 classified, unclassified: ["GET /v1/request-log"]`, then adding the entry turned that green and the gauntlet red — and its record says the plan *"named two of"* three directions. Naming a route is not covering it.
- [X] T018b [US1] **DONE — five pins, both halves probed.** Each key demanded 101% and each fired; the measured pins pass at exit 0. **Three of the five files are absent from the text table because v8 omits a file at 100/100/100/100** — read `coverage-summary.json` for which files were SEEN. Original: **Pin every new file in `vitest.coverage.config.mts`.** The config carries **63 per-file pins** and a global floor of 70% lines and statements, whose own comment says a threshold *"tuned down to pass measures nothing"*. Unpinned, `presign.ts`, the slot service and the refusals sit on that floor alone. The word "coverage" appeared nowhere in these tasks until analysis pass 4.
  **AND CHECK EACH KEY BINDS, BOTH HALVES.** 049 swept 45 pins and found exactly one unbindable; 052 found `git ls-files 'services/*/src/**/*.ts'` misses every file directly in a `src/` where picomatch — which is what vitest uses — matches it. Demand an impossible figure of each new key and confirm it fires; a pin whose key matches no file is silent.
- [X] T019 [US1] **DONE — met, not pinned around.** `media.controller.ts` 100/100/100/100; its one branch is the tenancy one and both arms run over HTTP. Original: Pin the tenant-scoping branch at 100%. Constitution VI's 100%-branch clause **names tenant isolation**, and 049 was the first Part 4 chapter to meet it rather than pin around it.
- [X] T020 [US1] **DONE.** `check:fences` 0 -> 15 — fifteen files where the plan named twelve. Four instruments were wrong and every one was found by running something; `baseline.txt` phase 3 carries them. Original: Re-measure and record: the route, the row, the request-log count, and what the gauntlet says. Commit phase 3.

**Checkpoint**: a photo can be uploaded to Relay's storage without a byte reaching Relay.

---

## Phase 4: Three refusals a client can tell apart (US2)

**Goal**: FR-MED-02's three conditions, three distinct codes. **Independently testable**: three
requests, three different codes, no rows written.

- [X] T021 [US2] **DONE — five codes, not four.** The four FR-MED-02/FR-017 codes, plus `service_unavailable` for T027a's 503 rung, which needed a code that names no particular store. Original: Add `media_type_not_allowed`, `media_too_large`, `media_storage_exhausted` and **`media_storage_unavailable`** to `packages/protocol/src/codes.ts`, each with the comment the registry's style requires and each **naming its near-neighbour**.
  **AND NONE OF THEM IS `quota_exceeded`.** `codes.ts` already refuses that reuse twice: `channel_member_limit_exceeded` says *"NOT `quota_exceeded`. That is a monthly, billable, resets-on-a-date refusal whose message promises a resume date"*. **A storage cap does not reset on a date** (R3), so the same objection applies one dimension over.
- [X] T022 [US2] **DONE — and all ten accepted types are asked for in the same file.** A refusal test alone is satisfied by a route that refuses everything. Original: Refuse a MIME type outside the ten FR-MED-02 permits — `image/jpeg`, `image/png`, `image/gif`, `image/webp`; `audio/mpeg`, `audio/mp4`, `audio/ogg`, `audio/wav`; `video/mp4`, `video/webm`.
- [X] T023 [US2] **DONE — both figures in the message,** and a second test shows the caps are PER KIND: 25 MB of audio passes where 25 MB of image does not. Original: Refuse a declared size over its kind's cap: image 10 MB, audio 25 MB, video 100 MB. The message names the size and the cap, because the remedy is to compress and a client cannot compress to an unknown target.
- [X] T024 [US2] **DONE IN PHASE 5, where the condition became reachable.** `storage-quota.itest.ts` covers the refusal, the exact-fill boundary (`>` and not `>=`), a cap of zero, and the race. Original: Refuse when committed bytes plus the declared size exceeds the environment's cap. **Depends on phase 5's configuration**; until then the condition is unreachable and a test of it cannot fail.
- [X] T024a [US2] **DONE — `storeReachable()`, and it costs +1.524 ms at p50, +24.1%.** Measured 200 samples a side. A presigned URL needs no contact with the store, so this round trip exists only to produce the refusal. Placed after type and size and before the reservation — the only position that satisfies FR-009 without a compensating delete. Original: **Refuse with `media_storage_unavailable` when the object store cannot be reached** (FR-017). This is `docs/05-sad.md:1062`'s degradation row — *"Object storage lost … Upload slots return a specific error"* — which FR-MED-02 does not carry and `docs/12`'s brief counted. Analysis pass 1 found it after the specification had called the fourth refusal unexplained.
  **IT IS THE ONLY TRANSIENT ONE, AND THAT IS WHY IT NEEDS ITS OWN CODE.** The other three are permanent — transcode, compress, free space — so retry is right for exactly one of the four. A client that cannot tell them apart either retries three refusals that will never succeed or abandons the one that would. Its message says so; the other three's must not.
- [X] T024b [US2] **DONE — `docker compose stop minio`, ask, assert, `start`, poll the health endpoint to a deadline.** The refusal arrived in 312 ms, a refused connection rather than the 2 s timeout, and no row was written. Original: Test it by **taking the store away**, not by mocking a client this chapter does not have: stop the container, request a slot, assert the code, restart. A test that stubs the failure asserts the stub.
- [X] T025 [US2] **DONE — before, before, before + 1.** The accepted request beside the two refusals is the control: "no row" alone is satisfied by a route that never writes. Original: **A refusal writes no row and reserves no bytes** (FR-009). Asserted by counting rows before and after, scoped to this test's own environment — an unscoped whole-table count is somebody else's problem in a lane that runs two files at a time (045-74).
- [X] T026 [US2] **DONE.** Every assertion names the code; the status is checked beside it, never instead. Original: Test each refusal **by code**, not by status. `webhooks.itest.ts` asserted status and message text and passed for four chapters while the body said `internal_error`; only the code could have caught it.
- [X] T027 [US2] **DONE.** Distinctness is one assertion and correctness is four, asserted separately. Original: Assert the four codes are **distinct**, and separately that each is **right**. Distinctness is one assertion and correctness is four; a test that only checks distinctness passes when every code is wrong in the same way.
- [X] T027a [US2] **DONE — four rungs, and 503 needed a new code.** 402 -> `quota_exceeded`, 413 -> `media_too_large`, 415 -> `media_type_not_allowed`, 503 -> `service_unavailable`. The two existing 503 throwers name a specific store and neither generalises. Original: **Add 415, 413, 402 and 503 to the status ladder in `services/api/src/protocol-error.filter.ts`** (FR-018). It maps 400, 401, 403 and 404 and falls everything else through to `internal_error`, so this chapter's four statuses are correct only while every thrower remembers to name its code. The filter's own comment calls that fallback **"a lie the client cannot act on"** — once about the 400 chapter 2.2 fixed and once about the 403 the credentials chapter fixed. Four new statuses without ladder entries is four more of the same.
- [X] T027b [US2] **DONE — 19 tests, eight rungs asserted twice.** Each rung's code, and separately that it is not `internal_error`. Run red by deleting the 415 rung: 3 failures. Original: Test the ladder by throwing **unnamed** at each of the four statuses and asserting the code is not `internal_error`. That is the probe that would have caught the two the filter already documents.
- [X] T028 **DONE — five sections.** `check:errors` reads `33 codes, 33 sections`. Original: [P] [US2] Write a section for each code in `docs/08-error-reference.md`. **The shape is exact and `check-error-codes.mjs` enforces four things**: the heading is `## <bare code>` — level two, the code itself, not `### \`code\`` (`:47`); the section contains **`**Retryable:**`** (`:75`); it contains **`**What to do:**`** (`:79`); and the body is **at least 200 characters** after whitespace collapse, a floor whose own comment says *"a restatement cannot clear"* it (`:85`).
  **`**Retryable:**` IS THIS CHAPTER'S CENTRAL DISTINCTION, AND THE GATE ALREADY DEMANDS IT.** Three of the four refusals are permanent and `media_storage_unavailable` is not, so the field the checker requires of every section is the one FR-017 exists to make.
  **AND THE CHECKER FAILS IN BOTH DIRECTIONS** — a code with no section, and a section naming no code — so T021's codes and these four sections must both be complete before T029 runs it. Either alone is red.
- [X] T028a **DONE — and now against an id this platform really minted.** The old test uses `"m_1"`, which a refusal could pass by rejecting anything unparseable. Still 422, still `media_not_available`, and the message does not echo the id. Original: [P] [US2] **Assert the `{ type: "media" }` arm still refuses with `media_not_available`** (FR-016). This chapter creates the very thing that arm refuses, so making it accept looks like finishing the job — and it would ship 4.11's surface with none of 4.11's checks: same environment, uploader identity, `pending` or `ready`. `codes.ts:204` already says *"§4.14 replaces the arm rather than this code"*, and the replacement is the next chapter's. FR-016 was the only requirement with no task until analysis pass 1.
- [X] T029 [US2] **DONE — both directions fire.** Code with no section: exit 1. Section with no code: exit 1. Control: exit 0 and the counted line. Original: Run `pnpm check:errors` in both directions after building `relay-platform` — it reads the built `dist`. **It is a gate no CI job runs** (`gaps.md` 055-3), so running it here is deliberate rather than automatic.
- [X] T030 [US2] **DONE — committed as `feat(056): phase 4 — four refusals, and the one that cost 24%`.** Original: Commit phase 4.

**Checkpoint**: a refused client knows which rule it broke.

---

## Phase 5: The storage cap, and the clause it forces (US3)

**Goal**: David sets a storage limit the way he sets the other three, and the third refusal
becomes reachable.

- [X] T031 [US3] **DONE — `0016_storage_quota.sql`, twelve clauses where 0014 had nine,** dropped and restated whole. The parser key and the CHECK clause landed in one change. Original: Add `storage_bytes` to `quotaConfigSchema` in `relay-platform/services/api/src/quotas/config.ts` **and** to the migration's `CHECK`, in the same change.
  In **`services/api/migrations/0016_storage_quota.sql`**, after T011's `0015`.
  **THE `CHECK` IS DROPPED AND RE-ADDED WHOLE, NOT APPENDED TO.** `0014_connection_minutes.sql:40-46` does `DROP CONSTRAINT environments_quota_config_shape` and then `ADD CONSTRAINT` restating every dimension. A new migration does the same with four, and **a restatement that omits one silently stops constraining it** — the same silent loss the config comment warns about from the parser's side. The existing comment says why: the constraint would otherwise accept a config the parser rejects, `capsFor` fails closed, and **the cap would silently become no cap**.
- [X] T032 [US3] **DONE — and the two gates disagree about a fifth dimension, on purpose.** `{"disk_inodes":{"hard":10}}` is accepted by the column and refused by `.strict()`, which is the division of labour the quota chapter described. Original: **Probe both halves** (049's rule about a pin that cannot fail): the parser refuses an unimplemented dimension, and the `CHECK` refuses the same input written straight to the column. One half passing proves nothing about the other.
- [X] T033 [US3] **DONE — absent, zero and null are three states.** No key: 18 MB across two requests. `hard: 0`: one byte refused. Original: An absent cap means **no cap and no alert**, resolved the way the three existing dimensions resolve an absent cap — `NO_CAPS` is `{ hard: null, soft: null }` and the absent state stays absent all the way to the reader rather than becoming `Infinity` or `-1`.
- [X] T034 [US3] **DONE — `sum(declared_bytes)` over the tenant's rows,** on `media_objects_environment_idx`. The cost is stated, not measured into a claim this chapter has no corpus for. Original: Compute committed bytes as a **sum over the media rows**, not a counter on `environments`. A counter would be a second source of truth for something the rows already say (constitution IV). The cost is a sum per request; say that rather than claiming a measurement at a scale this chapter does not have.
- [X] T035 [US3] **DONE — and a transaction is not a lock.** READ COMMITTED lets both writers read the same sum. `SELECT ... FOR UPDATE` on the environment row serialises them per tenant at no extra statement. Original: **Read and write in one transaction.** Unserialised, two slots race the same remaining allowance and both are issued. Publish the transaction and state what the alternative costs, because a reader who copies a read-then-write quota check ships the race.
- [X] T036 [US3] **DONE — interleaved by hand, because ten concurrent requests could not lose the race.** The `Promise.all` version passed with the lock and without it. By hand: plain commits 1,200 against a cap of 1,000; `FOR UPDATE` blocks and commits 600. **And the probe for "does the method take the lock" first measured the foreign key's own `FOR KEY SHARE`** — `FOR NO KEY UPDATE` is the discriminator. Original: Test the race: two concurrent slot requests against a cap that admits one. Exactly one is issued.
- [X] T037 [US3] **DONE — SRS 1.17.** The missing word was `monthly`. FR-RTL-05 now says three of its four quotas are flows and storage is a level, and that a storage refusal must not promise a resume date. Original: **Amend SRS FR-RTL-05** and add revision **1.17**. It reads *"configurable monthly quotas on messages sent, unique active persons, and connection-minutes"* — three quantities, none of them storage — while FR-MED-02 refuses on *"the environment's storage quota"* and FR-MED-12 says stored bytes are *"included in quota enforcement (FR-RTL-05)"*. **Two clauses cite a third for something it does not define.**
  **AND THE AMENDMENT MUST SAY WHICH KIND OF QUANTITY IT IS.** Storage is a **level**, not a monthly flow: `usage_periods` is keyed on a calendar month and `creditFor`'s own comment says *"the one thing this function must never do is subtract from a bill"*. A monthly storage quota would have to subtract on delete and would reset on the 1st, so a tenant holding 100 GB would start every month at zero. **A clause amended without that sentence means the thing R3 ruled out.**
- [X] T038 [US3] **DONE — FR-MED-12 re-read and amended too.** Its daily figure is a time series for the dashboard; the quota reads the level. Amending a clause two others cite is not finished when the first one reads right. Original: Re-read FR-MED-12 against the amended FR-RTL-05 and record whether it still says what it means. Amending a clause two others cite is not finished when the first one reads right.
- [X] T039 [US3] **DONE.** `sync:docs` first, then `check:srs` (245 clause rows, 245 unique identifiers) and `check:docs` (all mirrored docs match; 18 revisions ascend, 1.0 to 1.17). Both exit 0 and both printed their counted line. Original: Run `pnpm check:srs`, which counts clause rows and unique identifiers, and `pnpm check:docs`, which compares `docs/` against its mirror. **Run `pnpm sync:docs` first** — editing `docs/` does not update the mirror, and analysis found that ordering missing in feature 055.
- [X] T040 [US3] **DONE.** `check:fences` 15 -> 17. Coverage pins raised: `store.ts` to 100/100/100/100 and `media.service.ts` to 100/92.85/100/100. Original: Commit phase 5.

**Checkpoint**: the third refusal is reachable, and the clause it rests on says what it needs to.

---

## Phase 6: The boundary, and the two things this chapter cannot fix

- [X] T041 **DONE — three requests on the three sides of the bound.** 999 issued, 1,000 issued, 1,001 refused against an empty cap, +1 refused against a full one. Falsified by flipping `>` to `>=`: one test of six goes red. Original: **Test the quota at its boundary**: one byte under the cap is issued, one byte over is refused. A test in the middle of a range proves the comparison exists, not that it is right — chapter 4.7 found both obvious ways to plant a 0.1% drift pass for exactly this reason.
- [X] T042 [P] **DONE — `gaps.md` 056-1, measured rather than reasoned about.** The tenant issued 600 against a cap of 1,000 and then refused still reports 600 committed, permanently. FR-MED-10's twenty-four hours is about *unreferenced* media and does not reach an unused slot. Original: Record, in the chapter and in `gaps.md`: **a slot nobody uploads to holds its declared bytes indefinitely.** No job here reclaims it, and FR-MED-10's is 24 hours and about *unreferenced* media rather than *unused slots*. This chapter records the leak rather than closing it — the same shape as 4.7's daily job with no runner, and saying so is the whole of what a chapter can do about it.
- [X] T043 [P] **DONE — `gaps.md` 056-2.** The size refusal's own message says "declared" because that is what it refuses. Original: Record that **the quota arithmetic is over declarations, not over verified bytes.** FR-MED-03 is a later chapter, so a client that declares 1 KB and uploads 90 MB is inside the cap and over it. State what that permits until verification ships.
- [X] T043a **DONE — 59 integration files, 0 unscoped reads, 10 of 10 controls, exit 0.** Was 55. **Four new suites where the task predicted eight**, which is an estimate high in the direction this project's are usually low. Original: **Run `check-lane-scope.py` and record the file count.** This chapter adds eight integration suites; the script reads **55 files today with 0 unscoped reads and 10 of 10 controls firing**, and that number must rise. `CLAUDE.md`: *"Run it after adding an integration test, because the alternative is finding out once, in the fifteenth run of a battery."*
  **T025 ALREADY CARRIES THE HAZARD IT DETECTS** — counting rows before and after, scoped to this test's own environment. A run that reads nothing exits 2 since 053, so the count is the evidence the instrument looked.
- [X] T044 **DONE.** The committed sums are in the boundary table above; every one was read back out of Postgres after the request rather than inferred from the status. Original: Re-measure the committed-bytes sum against the boundary tests and record the numbers.

---

## Phase 7: The chapter

- [X] T045 **DONE — 3,992 prose words** of a 2,000-4,000 bound, measured with `prose-words.mjs`. The first draft came in at 4,171 and was cut rather than argued down. Original: Write `relay-tutorial/app/(en)/part-4/chapter-10/…/page.mdx`, **2,000–4,000 words outside code fences** (`docs/07:67`), measured with `node relay-tutorial/scripts/prose-words.mjs <page>` — chapter 4.9 came in at 2,826. **The ten fence hunks do not count**: *"+ code is additive, not counted"*, which is what lets a chapter publish 1,100 lines of listing inside a 4,000-word bound. **Say which kind each argument is when the estimate is written** — an argument costs 545 words as prose and about 280 as artifacts.
- [X] T045a **DONE — four TRAP boxes**: the tamper probe that was a no-op 6.23% of runs, `kindOf("constructor")` walking past two refusals, the lock probe that measured the foreign key, and FR-014's declarations-not-bytes. Original: **At least one `TRAP` box.** `docs/07:70` makes it a counted class with a per-chapter minimum for code chapters, and 4.7, 4.8 and 4.9 carry 2, 3 and 2. Neither this plan nor these tasks mentioned it until analysis pass 3. The obvious candidate is **FR-014**: the quota arithmetic is over **declarations**, so a reader who trusts the cap is trusting a number the uploader chose, and nothing verifies it until FR-MED-03's chapter.
- [X] T046 **DONE — registered, and `pnpm build` exits 0** with the page in the route list. Original: **Register the chapter in `relay-tutorial/lib/tutorial.ts`.** `<ChapterHeader id="4.10" />` throws on an unregistered id, so `pnpm build` exits 1 from the moment the page exists. That has cost two chapters, once for a whole chapter at 112 of 112 with eight gates green and none of them rendering a page.
- [X] T047 [P] **DONE — three figures**, each named by a `<Figure>`; `check:figures` reports no note for this chapter. Original: Figures in `figures.ts`, each named by a `<Figure>`. `check:figures` reports an export nothing names as a note rather than a failure, so the note is the check.
- [X] T048 **DONE — seventeen files, where the table said twelve.** The table listed `db/catalogue.ts`, which this chapter never touches, and missed six that arrived from repairs made after it was written. **And `patch --dry-run` said yes to seven hunks the checker refused** — it applies with fuzz and offset where the checker needs exactly one exact match. Original: **A hunk per fenced file this chapter edits — TEN of them, counted rather than remembered.** Generate each with `pnpm check:fences --dump <dir>`, never with `git diff` against the working tree (fence-chain rule 1a, and feature 055 built the flag for it).

        file                                    en chapters   appendix hunks
        services/api/src/db/schema.ts                15            2
        packages/protocol/src/codes.ts               12            1
        services/api/src/app.module.ts               11            1
        vitest.coverage.config.mts                   11           10
        turbo.json                                   10            2
        compose.yaml                                  8            0
        services/api/src/isolation/targets.ts         6            1
        services/api/src/protocol-error.filter.ts     6            0
        services/api/vitest.integration.config.mts    6            0
        services/api/src/db/catalogue.ts              4            1
        packages/test-harness/src/sentinel.sql        3            1
        services/api/src/quotas/config.ts             2            0
                                                     94           19

  **AND THE TABLE WAS TEN UNTIL ANALYSIS PASS 5 COUNTED IT AGAIN.** Pass 4's own remediation added the two vitest configs to this chapter — T004a puts the store's address in both and T018b puts the new files' pins in one — and neither reached this table. **The remediation of a finding about counting created another instance of it**, which is this project's *"a pass's own fix was the next pass's defect"* one pass later.
  **`vitest.coverage.config.mts` IS THE MOST EXPENSIVE FENCE EDIT IN THIS REPOSITORY.** Feature 055 spent most of a phase on it: 15 bad hunks, 743 differing lines, and a chain state carrying **no `env` block at all** — which is the block T004a adds a key to.
  **AND T004a AND T018b ARE ONE HUNK, NOT TWO.** They edit the same file in the same chapter, and feature 055 measured that no page in the series holds two chained fences for one path; `--at <page>` granularity assumes it. Combine the `env` key and the pins into a single `diff` fence.
  **AND `compose.yaml` IS EIGHT, NOT FIVE.** Research R5 listed 1.2, 3.19, 3.21, 3.22 and 3.24; Part 4 added **4.2, 4.5 and 4.7** after that list was written. This task said five until analysis pass 2 counted.
  **THIS IS 050's LESSON, WORD FOR WORD**: *"The fenced-file list was remembered, not counted — eight files, not five. A list of fenced files goes stale every time a chapter moves code between files."* `schema.ts` at 15 chapters and `codes.ts` at 12 are the deepest chains this chapter touches, and feature 055 measured what regenerating an early fence costs.
- [X] T049 **NOT APPLICABLE, AND THE TASK ASSUMED A CORPUS.** `app/(vi)/vi/part-4/` holds chapters 1-3; the translation lags by seven chapters, so there is no vi 4.10 page and MIRROR has nothing to compare. 050's finding, repeated. Original: The Vietnamese twin **for each of the ten**: the same fence body, byte-identical, copied rather than regenerated. `--dump` writes the English chain; FR-011's rule from 055 is that vi takes a copy.
- [X] T050 **DONE, AND IT DECIDED NINE OF THE SEVENTEEN.** Seven anchor at no width because their change sits between appendix-added lines. Two anchor here and break the appendix's own older hunks by doing so, and go last in the appendix instead. Two more stayed at `-U2` and `-U3`. Original: **Check which state each new hunk is written against.** A chapter hunk for a file the appendix also edits is written against a state no reader sees (4.8's finding) — and **eight of the twelve have an appendix hunk**, nineteen in total, ten of them on `vitest.coverage.config.mts` alone. Only `compose.yaml`, `protocol-error.filter.ts` and `quotas/config.ts` do not. Use `--at <page>` for a chapter hunk and plain `--dump` for the end state; using the wrong mode produces a hunk that fails exactly like the one it replaces.
- [X] T051 **DONE — the absolute number is 0.** `290 fenced files replay onto relay-platform across 53 chapters`, EXIT 0, from 282 and 52. Original: Run `pnpm check:fences` and report the **absolute number**. It is 0 today. A delta of zero is what hid a problem for nine chapters, and feature 055 named the file it hid.

---

## Phase 8: The record

- [X] T052 **DONE — ADR-30 in both documents.** Three options, and the count is not the whole argument: 29 runtime dependencies at `part4-ch9` and 29 now, across all eight `package.json` files. The reversal condition is the ratio. Original: Write **ADR-30** in `docs/05-sad.md` and `docs/06-adr-deep-dives.md`: **sign it ourselves rather than take a client.** ADR-13 already chose the pattern, so this is the narrower dependency decision, with the rejected alternatives — `@aws-sdk/client-s3` plus `@aws-sdk/s3-request-presigner`, and `minio` — and a reversal condition. Constitution VII requires it because it is a dependency decision, even though the dependency count moves by zero.
- [X] T053 **DONE — `sync:docs` first, then both gates.** `check-docs-drift: all mirrored docs match their sources`; `check:srs: 245 clause rows, 245 unique identifiers`; `check-revision-order: 18 revisions ascend, 1.0 to 1.17`. Original: Then `pnpm sync:docs`, `pnpm check:docs` and `pnpm check:srs` **again**, after the last `docs/` edit. The docs gates must run after the docs change; feature 055 found that ordering missing and fixed it there.
- [X] T054 **DONE — `baseline.txt`, every phase in the order it was taken.** Original: Write `specs/056-chapter-4-10/baseline.txt` carrying every phase's measurements and the pinned environment, in the order they were taken.
- [X] T055 **DONE — 11 entries: 7 new, 3 carried and re-measured, 1 answered.** **055-4 did not reproduce the obvious way** — all seven gate scripts print their counted line from an unrelated empty directory, because each resolves its corpus from the script's own location. 050-8 is narrower and not closed. Original: Write `gaps.md`. **Re-measure every carried item rather than copying it**: 055-3 (`check:errors` has no runner — T029 runs it by hand), 055-4 (five of seven gate scripts exit 0 on an absent corpus), 050-8 (the ingester nothing starts), and this chapter's own two recorded leaks from T042 and T043.
- [X] T056 **DONE — the row was right and the fourth refusal is not FR-MED-02's.** `docs/05-sad.md:1062`'s degradation row, shipped as FR-017. Original: In `gaps.md`, answer the **four-refusals discrepancy**: `docs/12` row 11 says four and FR-MED-02 names three. The best candidate is the SAD's degradation row — *"upload slots return a specific error"* when the store is down — which is a real refusal and is not FR-MED-02's. Record the finding either way rather than leaving the number to drift.
- [X] T056a **DONE — row 11 amended with four things the line did not say.** No object storage existed; the fourth refusal is the SAD's; the quota is a level not a flow; and the presigned URL's independence from the store is what made FR-017 cost 24.1%. Original: **Amend `docs/12` row 11 with what the line did not say.** It reads *"the slot, the presigned URL, the four distinct refusals, the storage quota"* — right about the count, and silent about the cost: **there was no object storage at all**, `minio/minio` cannot be pulled, the storage quota is a **level** where `usage_periods` holds flows, and the fourth refusal was in the SAD's degradation table rather than in FR-MED-02. `docs/12` carries *"What this line did not say is…"* four times and chapters 4.7, 4.8 and 4.9 each amended their own row; this chapter's tasks cited the document three times and amended nothing until analysis pass 3.
- [X] T057 **DONE — and six items are named as discharged in a weaker form than their words suggest**, including FR-013, which is an observation about one path rather than an invariant anything enforces. Original: Write `traceability.md`, and **name anything discharged in a weaker form than its words suggest.**
- [X] T058 **DONE — the block rewritten for the close**, including every task premise this chapter falsified by running it: the twelve-file table, `patch --dry-run`, the ten-way race, the `FOR UPDATE` probe, the vi twin, and 055-4's `cwd`. Original: Update `CLAUDE.md`'s `<!-- SPECKIT -->` block for the close, including every task premise this chapter falsified by running it.
- [X] T059 **DONE — six gates, each read by its counted line.** `lint` exit 0 (**and it is the one gate with no counted line at all** — eslint prints nothing on success); `build` exit 0, 124 static pages; `check:docs` 18 revisions ascend to 1.17; `check:srs` 245 clause rows; `check:figures` 284 figures, 286 bindings; `check:fences` 290 files across 53 chapters. Original: Run the tutorial job's five other gates, named from `ci.yml:184-205` rather than from memory — `lint`, `build`, `check:docs`, `check:srs`, `check:figures` — and **read each one's counted success line**, because five of the seven gate scripts exit 0 when their corpus is absent.
- [ ] T060 Tag `part4-ch10` on `relay-platform`, commit, and push all three repositories.
- [ ] T061 After the push, confirm the **tutorial job in CI succeeds**. It went green for the first time in nine chapters at feature 055's close; this is the first chapter that can break it again and know.

**Checkpoint**: the slot ships, the clause it needed says what it needs, and what this chapter
could not fix is written down.

---

## Dependencies

    Phase 1  ──────────────────────────► everything (no store, no signature)
    Phase 2  ──────────────────────────► US1, US2, US3
    Phase 3 (US1) ─────────────────────► US2 (there is no route to refuse on)
    Phase 5 (US3) ─────────────────────► T024 and T041 (the third refusal is unreachable without a cap)
    T031     ─────► T032               (probe both halves of the pin)
    T037     ─────► T038               (re-read the citing clause after the amendment)
    T046     ─────► T051               (an unregistered chapter fails the build before the chain)
    T060     ─────► T061               (CI is only observable after a push)

**US1 is the MVP and it is independently shippable.** A slot that is always issued is a working
upload path; the refusals make it safe and the quota makes the third refusal reachable. US2
depends on US1 having a route, and US2's third case depends on US3.

**US3 is where the clause work is**, not the code work. `storage_bytes` is one key in a schema;
FR-RTL-05's amendment is the thing that needed a measurement to get right.

## Parallel opportunities

- **Phase 1**: T003 and T004 are different files.
- **Phase 2**: T008 is a unit test beside T007's implementation.
- **Phase 4**: T028 is documentation beside the code tasks.
- **Phase 6**: T042 and T043 are two records in the same file and can be written together.
- **Phase 7**: T047's figures are independent of the fence work.

## Implementation strategy

**The MVP is phase 3**, and phases 1 and 2 are what make it possible. If the signature does not
round-trip against the store, nothing after it is worth writing — which is why T009 asserts five
results rather than one.

**Then the order the mechanics force**: the route before the refusals, the configuration before
the third refusal, the boundary after the configuration, the chapter after the code, and the
docs gates after the last `docs/` edit.

**The riskiest task is T007.** The canonical request is unforgiving and its failure mode is a
bare 400 with no indication of which field was wrong. The probe that produced this plan is the
reference implementation; the acceptance is the store, not a string.
