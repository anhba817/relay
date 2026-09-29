# Tasks — Chapter 4.15, "What a thumbnail costs"

**Feature**: `specs/061-chapter-4-15/` · **Plan**: [plan.md](./plan.md) · **Spec**: [spec.md](./spec.md)

Nine phases. Commit each one. The order is the plan's; the traps are the ones this project has
already paid for, cited where they apply rather than restated in a preamble nobody reads.

**Read before starting**: `research.md` R1 and R2 carry the numbers this chapter publishes, and
R2's crossover decides a behaviour, not just a figure. `contracts/renditions.md` records that
the new field is **optional**, so unlike 4.14 the compiler will not name the construction sites
— which changes how the door set is derived and is the single most likely way this chapter
ships a door that forgot.

---

## Phase 1: Setup — the numbers this chapter is compared against

- [X] T001 Bring the stores up and record what answers: `cd relay-platform && RELAY_POSTGRES_PORT=15432 docker compose up -d --wait`. Seven containers including `clamav` and `minio`. **Read the counted line, not the exit code.** If NATS comes up unhealthy it **names one unrecoverable stream at a time** (`gaps.md` 058-7) — clear them one at a time; the bulk form was refused by this environment's guard.
- [X] T002 Record the opening `check:fences` figure as an **absolute number**, not a delta, run in `relay-tutorial` (the gates live there; `pnpm` in the wrong repository exits silently and reads as green). At `part4-ch14` it was `291 fenced files … across 57 chapters`, EXIT 0. **A clean run prints no problem line at all**, so the counted line plus EXIT 0 is what clean looks like.
- [X] T003 [P] Record the opening dependency count across every `package.json` in `relay-platform` — **31 entries** at `part4-ch14`. This chapter **adds one**, which is the first time in Part 4 that number moves, and SC-009 publishes it before and after.
- [X] T004 [P] Record the opening lane state with the composed services **stopped** (`gaps.md` 057-5): `pnpm exec turbo run test --force`, `pnpm test:integration`, `pnpm coverage`, `pnpm check:errors`. **`pnpm test` alone reports a cached number** — 4.14 read 553 where the real figure was 867. Then `pnpm test:outsider` with the services **up** plus `RELAY_API_URL`, `RELAY_WS_URL`, `RELAY_DEMO_CREDENTIAL`; without them it prints `19 skipped`, a counted line that means nothing ran.
- [X] T005 [P] Re-measure the lane's media composition rather than trusting the plan's figures: `media_objects` by state, and how many are images of an allowed type. **The lane moves between chapters** — 4.13 found it had grown 3,005 → 3,078 since its own plan.
- [X] T006 [P] Record how many of the lane's `media_objects` rows are images **above** the 320 px bound, using `width`/`height` where the worker recorded them. This is the population that would gain a rendition, and R2's crossover says the ones at or below it gain nothing. If the column is null for most rows, say so — that is a fact about 4.13's coverage, not a missing measurement.
- [X] T007 Record the opening CI error set **per error**, uuids normalised, from the most recent run on `main`. Per error, not per colour: a colour cannot say whether a run introduced something new, and four chapters running have found a gate whose colour was true and whose meaning was not.
- [X] T007a [P] **Count the fence exposure of every file this chapter will edit, BEFORE editing any of them**, with `grep -rl 'title="<path>"' app/ fences/` in `relay-tutorial`. Measured 2026-09-29, and it is nothing like the plan's first guess:

      services/api/src/db/repository.ts        52   28 en + 23 vi + 1 appendix · 50 diff, 2 whole body
      services/api/src/db/schema.ts            34
      packages/protocol/src/attachments.ts      4
      services/api/src/media/media.controller.ts 2
      services/media-worker/{package.json,Dockerfile,src/*}   0
      pnpm-lock.yaml                            0

  **The two files this chapter edits most are the two most exposed, and the three the first
  draft named are fenced nowhere.** `repository.ts` takes five separate edits here —
  `unreferencedMediaIn`, `withMediaStates`, `recordMediaVerdict` and its new transaction, the
  attach predicate, `readableMediaObjectKey` — so sequence them against the hunks rather than
  discovering the collision in phase 8. **52 is not a repair bill**: 23 are Vietnamese pages and
  050-3 records the vi chain is replayed against the English chapter's fences and never against
  `relay-platform`, so the English exposure is 28 plus the appendix.
- [X] T008 [P] Record the media-worker image size before the chapter (`docker images`), because SC-009 publishes the delta and 245 MB is the figure this plan was written against.

---

## Phase 2: Foundational — the shapes, before anything reads or writes them

**Blocking**: every user story below depends on these. Nothing here is story-specific.

- [X] T009 Read `services/api/src/db/schema.ts`'s `mediaObjects` block end to end before editing it, including the comments 4.10, 4.13 and 4.14 left there. Two of them are forward references to this chapter and **one of them is the same sentence copied into migration `0018`** — the duplication is worth noticing before adding a third copy.
- [X] T010 Write `services/api/migrations/0020_media_renditions.sql` (FR-001) per `data-model.md` §1: `parent_id`, `rendition`, `rendition_failed_reason`, the two CHECKs, the unique `(id, environment_id)`, the composite foreign key with `ON DELETE CASCADE`, the unique `(parent_id, rendition)`, and the partial index. Comment it the way `0018` and `0019` are commented — what the column is for and what a rollback meets.
- [X] T011 Mirror the columns and constraints into `services/api/src/db/schema.ts`. **Amend `declared_bytes`'s comment**, which says *"what the caller said"* and is about to hold a number nobody said (`data-model.md` §3). A comment that is now false is worse than no comment.
- [X] T012 [P] Write the migration's red probe: a rendition row with `state <> 'ready'` is refused by name; a `parent_id` naming a row in another environment is refused by the foreign key; a second rendition of the same kind for one parent is refused by the unique. **Run each red before the migration and after**, because a constraint test that was never red proves the constraint exists and not that it fires.
- [X] T013 [P] Add `RENDITIONS` and `RENDITION_FAILED` as closed sets (`data-model.md` §2). **`packages/protocol/src/media.ts` does not exist** — the directory holds `attachments`, `codes`, `fanout`, `frames`, `internal`, `membership`, `presence`, `revision` and `index` — so either create it **and export it from `index.ts`**, or put the sets in `attachments.ts` beside the schemas that use them. A new file that nothing re-exports compiles and is unreachable. A closed set in the protocol package, not a CHECK constraint — `0018`'s argument for `rejected_reason`, and the same reason: a CHECK is a fourth thing to widen.
- [X] T014 Apply the migration and confirm the composite foreign key actually refuses a cross-environment parent. **This is the constitution I claim and it is the one thing in the schema that cannot be checked by reading it.**
- [X] T015 Measure what the unique `(id, environment_id)` index costs on the lane's `media_objects` — `pg_relation_size` before and after. The plan owes this number (`data-model.md` §1) and it is the price of giving Principle I to the database instead of to a predicate.
- [X] T016 Run `pnpm exec turbo run test --force` and `pnpm test:integration`. Phase 2 changes no behaviour, so **anything red here is a schema change breaking an existing assumption** — most likely a test that counts `media_objects` columns or asserts a whole row.

---

## Phase 3: User Story 1 — a derived object belongs to its parent (P1) 🎯 MVP

**Goal**: the platform can hold an object that exists because of another, and the doors that act
on media agree about it — not served alone, not reaped as unreferenced, gone when the parent goes.

**Independent test**: plant a rendition row by hand against a real parent, then exercise the
reaper predicate, the delivery gate and parent deletion, asserting the derived row and the
parent separately. No image decoder involved anywhere.

- [X] T017 [US1] Write `unreferencedMediaIn(db, environmentId, olderThan)` (FR-002) in `services/api/src/db/repository.ts` as a module-level scoped function — the shape 4.14 established for `channelsReferencingMediaIn`, and for the same reason: its future caller is a job, not a request. An object is unreferenced when no message names it **and** it is not a rendition of a parent that is itself referenced.
- [X] T018 [US1] Write the comment on `unreferencedMediaIn` naming its caller. **It has no production caller in this chapter**, so the comment says that and names the chapter that will have one — `docs/12` row 22, the erasure chapter (R4). `CLAUDE.md`'s convention: a claim about when a symbol runs names the thing that runs it, and *"called by the reaper"* would be false today.
- [X] T019 [P] [US1] Write `services/api/src/media/rendition.itest.ts` covering US1 scenarios 1 and 2 (SC-001): a rendition of a referenced parent survives the predicate past the 24-hour boundary; a rendition whose parent is unreferenced is returned by it, and never before its parent. **Pin one instant before the query runs** — 043's `reset-lane` finding and 4.13's `pinWindow`, because `now()` re-evaluated inside the assertion is a different moment from the one the fixture used.
- [X] T020 [P] [US1] Extend the delivery gate in **`services/api/src/db/repository.ts`'s `readableMediaObjectKey`** — not the controller, which is where this plan's first draft sent it. That function is the gate: four conditions, ending in `state = 'ready'`, with the channel-visibility rule after them. Resolve `parent_id` there and run the **existing** predicate on the parent. FR-005 says the same predicate, not a copy, and **putting the resolution in the controller is precisely how the second copy gets written** — which is what 4.12 found three of, each invisible to a single-mutation probe.
- [X] T021 [US1] Refuse a rendition that is addressed directly by a caller who cannot read its parent, **byte-identically** (SC-003) to an id no object has. Assert the two bodies differ only in `request_id`, which is how 4.11 and 4.12 each tested this and the only form that proves nothing leaks.
- [X] T022 [P] [US1] Refuse a rendition at the attach predicate in `sendMessage`'s transaction: a rendition is not attachable (FR-004), and the refusal is the same `media_not_available` a foreign object gets. **Add it to the existing `IN` predicate rather than beside it** — a second refusal with its own code would report that somebody else's rendition exists.
- [X] T023 [P] [US1] Make sure a rendition never appears where a tenant's own uploads are listed or counted as uploads. Derive the doors by grepping reads of `media_objects` rather than recalling them (4.14's hand list of three and second list of six were both wrong) — **and expect the derivation to find no customer-facing list door, because there are four media routes and none lists uploads.** The two reads that do matter are already known and are the positive control that the grep looked: the **quota sum**, which counts renditions and is meant to (FR-012), and **`GET /internal/media/pending`**, which excludes them because a rendition is `ready`. A zero here means nothing unless those two came back.
- [X] T024 [US1] Write the store-side deletion beside `deleteObject` in `services/api/src/media/store.ts`: deleting a parent deletes its renditions' keys too. `ON DELETE CASCADE` does the database and **nothing does the store** — that asymmetry is real and is this chapter's `TRAP` box. **Comment it the way T018 comments `unreferencedMediaIn`, because it is in the same position: it has no production caller.** Nothing in this platform deletes a `media_objects` row — the rejection path deletes bytes and keeps the row on purpose (`0018`: *"a rejected object's row is all that survives it"*) — so name the erasure chapter as the caller-to-be rather than writing a comment that reads as though something calls it today.
- [X] T025 [P] [US1] Write the deletion-path enumeration test (FR-003, SC-002; `data-model.md` §4). **Assert the COUNT it found, not just that the list is complete** — the count is currently **zero**, because nothing in the platform deletes a `media_objects` row, and *"a test for every path"* over an empty set passes by doing nothing. Then exercise the cascade the only way it can be run today: a direct `DELETE` of the parent, with the rendition shown gone from **both** the database and the store. The test records that zero is the expected number and which chapter changes it, so the day it becomes one the assertion fails and somebody reads this.
- [X] T026 [US1] Run `python3 scripts/check-lane-scope.py`. A new integration suite reading `media_objects` without a predicate naming its own rows is a neighbour's problem, and 045 found eight of those one failure at a time. **Assert the counted line, not the exit code** (055-4): five of seven gate scripts exit 0 when their corpus is absent.
- [X] T027 [US1] Run the US1 suite plus the existing media suites. **Run `messages.itest.ts` and the outsider suite too** — 4.14's fourth whole-array assertion was a directory away and the media-only run reported green, and its fifth was in `packages/outsider`, which no local lane reaches.

---

## Phase 4: User Story 2 — an image gets a thumbnail (P2)

**Goal**: an image that passes verification gains a smaller rendition, made by the platform,
stored beside it, recorded with the dimensions it actually has.

**Independent test**: upload a real image, let the worker verify it, and assert a rendition
exists in the store with bounded dimensions, recorded against the parent.

- [X] T028 [US2] Add `sharp` to `services/media-worker/package.json` and update the lockfile. **pnpm is 10.33.0 and blocks lifecycle scripts by default** — check whether `sharp` resolves through its prebuilt platform packages or needs an `onlyBuiltDependencies` entry in `pnpm-workspace.yaml`, and record which. A silent skip here produces a module that imports and throws on first use.
- [X] T029 [US2] Verify the worker's **image** builds with the native binary: the Dockerfile runs `pnpm install` **inside `node:22-alpine`**, so the musl build is fetched in the right place — but `pnpm --filter @relay/media-worker --prod deploy --legacy /app` has to carry the platform package into `/app`. Build it and run `node -e 'require("sharp")'` in the runtime stage. **A `dist` that imports and a container that cannot is 4.11's three-kinds-of-stale-build, and only a container-talking suite finds it.**
- [X] T030 [P] [US2] Write `services/media-worker/src/thumbnail.ts`: decode, resize to a 320 px long edge with `fit: inside` and no enlargement, encode WebP q80. **Return "no rendition" for an image already within the bound**, which is R2's measurement — 97.3% of the parent and identical to it — and not a preference.
- [X] T031 [P] [US2] Write `services/media-worker/src/thumbnail.test.ts` (SC-005) in the **Docker-free** lane, covering **PNG and GIF** — both of `fixtures.ts`'s `pngOf` and `gifOf` decode and resize, measured 2026-09-28 at 3,618 B and 198 B from 800×600. `jpegOf` and `webpOf` are headers with no image data and fail with `corrupt header`. **Say in the file which two are covered and why the other two cannot be**, and do not widen the fixtures to fix it: writing a real JPEG encoder to test a decoder is the tail wagging the dog, and the composed suite (T042) covers those formats with real bytes.
- [X] T032 [US2] Derive the set of types that get a rendition from what the decoder reports it can read, intersected with `ALLOWED_TYPES` (FR-007). **Do not restate it as a list** — FR-003's own predecessor forbade hand lists and contained one, which analysis pass 4 of the last feature found.
- [X] T032a [US2] Add `getObject` to `services/media-worker/src/store.ts` — **a whole-object read the worker does not currently make** (R9). Its three existing calls hold nothing: `headObject` takes metadata, `streamObject` hands ClamAV an `AsyncIterable` consumed once at 64 KiB a chunk, and `getRange` takes a prefix. A rendition needs the bytes, and the streaming property is deliberate, so this is a fourth call and not a change to the third.
- [X] T032b [US2] Gate the fetch on the probe, in **three** states and not two (R9). The type must come from `sniff`, not from `content-type` — 4.13 measured a presigned PUT of twelve MP4 bytes sent as `image/png` answering `HEAD` with `image/png`, the client's own claim echoed. Then:

      image, dimensions known, above the bound   ->  fetch
      image, dimensions known, within the bound  ->  no fetch, no rendition   (R2's crossover)
      image, dimensions UNKNOWN                  ->  fetch, and decide from the decoded size

  **The third state is not an edge case — it is an ordinary camera JPEG.** Measured 2026-09-29: a
  JPEG carrying one maximal APP1 segment (72,215 B, which is what EXIF plus an embedded preview
  looks like) returns `dimensionsOf(prefix) === null` at `PROBE_BYTES = 65_536`, while the same
  bytes read whole give `1200x900` and decode fine. The first draft of this task had two states
  and would have **denied renditions to exactly the files most likely to want one**. Deciding
  from the decoded dimensions costs nothing, because by then the bytes are in hand.
- [X] T032c [P] [US2] Measure the fetch: a full GET of an 8 MB object from the composed store, p50 over 7 runs, **beside** the 1.412 ms `HEAD` and the scan's own duration for the same object. This is the cost `research.md` R2 left out and the chapter is named after.
- [X] T032d [P] [US2] Measure the worker's **peak RSS** across a 10 MB image. A 4000×3000 RGB bitmap is ~36 MB **if it is held whole, and libvips may not hold it whole** — it processes in strips and `sequentialRead` exists for this case. The 36 MB is arithmetic, not a measurement; publish whichever the probe says and do not publish the arithmetic as a figure.
- [X] T033 [US2] Add `putObject` to `services/media-worker/src/store.ts` — the worker's **first writer**; it has four readers and no writer today. Sign it the way `sign()` already does, and remember **the host is inside the SigV4 signature** (4.11): the worker's endpoint and the client's cannot be one field.
- [X] T034 [P] [US2] Write the store round-trip test: `putObject` then `getRange` returns the same bytes. A tamper probe that may not have altered anything has to assert that it did (4.10) — the same discipline applies to a write probe that may not have written.
- [X] T035 [US2] Wire generation into `services/media-worker/src/verify.ts` (FR-006) in R7's order: **after** the scan and declaration check pass, **before** the verdict that moves the parent to `ready`. FR-009 needs a rejected object to leave no derived bytes, and never writing them is cheaper than cleaning them up.
- [X] T036 [US2] Post the rendition with the verdict over the internal seam. **The worker holds no database credential** — the Dockerfile's own comment says so and gives the reason — so the row is written by the api inside `recordMediaVerdict`'s existing compare-and-set (Principle IV).
- [X] T037 [US2] **Wrap `recordMediaVerdict` in `db.transaction` — there is no transaction there today, and this plan's first draft said "the same transaction" as though there were.** The function is a bare `UPDATE … WHERE state = 'pending' RETURNING` plus a fallback `SELECT`. Without a transaction, an UPDATE that lands and an INSERT that fails leaves the parent `ready` with **no rendition and no recorded reason** — the absence FR-007 forbids and the silence FR-008 was written against. Inside the transaction: the CAS first, the rendition INSERT only when it applied.
- [X] T037a [US2] Amend `recordMediaVerdict`'s own comment in `services/api/src/db/repository.ts`. It argues that the key and environment come back from the UPDATE because *"fetching it separately would open a window in which the row moved between the two statements"* — still true, and now sitting beside a transaction that closes a different window. **Say which window each mechanism closes**, or the next reader concludes one of them is redundant.
- [X] T037b [P] [US2] Write the test that the pair is atomic: force the rendition INSERT to fail and assert the parent is **still `pending`**, not `ready`. Run it red against the untransacted version first — otherwise it is a test that passes because nothing made it fail.
- [X] T037c [US2] Keep the unique `(parent_id, rendition)` even though the CAS means a duplicate sweep never reaches the insert. *"The guard upstream means this cannot happen"* is what 4.14's five accounting tests were each protecting against. **Verified 2026-09-28 against `postgres:16-alpine`**: three all-NULL rows are accepted, so uploaded objects are unaffected, and a real duplicate is refused by name.
- [X] T038 [P] [US2] Record `rendition_failed_reason` on the parent when generation fails, and let the parent reach `ready` regardless (FR-008). The sweep re-reads `pending` rows for ever, so an object whose thumbnail failed **must not stay `pending`** — that is an infinite retry wearing a state's clothes.
- [X] T039 [P] [US2] Write the failure test: a decodable-type object whose generation is forced to fail still reaches `ready`, carries a reason from the closed set, and leaves **zero** derived bytes.
- [X] T040 [P] [US2] Write the rejection test: a scan failure and a declaration mismatch each produce no rendition row and no derived bytes. **List the store** to check the bytes (SC-006) — querying the database asks whether the platform thinks it wrote something, which is the wrong question.
- [X] T041 [P] [US2] Write the idempotence test (FR-010, SC-007): process one object twice, assert one rendition. Deliberately issue the duplicate rather than reasoning that it cannot happen.
- [X] T042 [US2] Write `services/media-worker/src/thumbnail.itest.ts` against the composed stack with a real store. **Do not stop a shared container in it** — 4.10 found an isolation suite that never mentions media answering 503 because a media test ran `docker compose stop minio`, and `check-lane-scope.py` cannot see an action scoped too wide.
- [X] T043 [US2] Confirm `@relay/config`'s `INFRA_SERVICES` and `compose.yaml` still agree if anything about the worker's service definition changed. **A container is two edits and only `pnpm coverage` says so** (056-8) — that package is a unit test no integration lane imports.
- [X] T044 [US2] Run the worker's lanes and the api's. Record the worker image's new size for SC-009.

---

## Phase 5: User Story 3 — a client can show the small one (P3)

**Goal**: a client rendering an image attachment can fetch the thumbnail under the parent's
authorisation without fetching the parent first.

**Independent test**: as a member of the channel, request the thumbnail and receive bytes; as a
non-member, receive the parent's refusal.

- [ ] T045 [US3] Add the optional `thumbnail` object (FR-011) to `deliveredAttachmentSchema`'s media arm in `packages/protocol/src/attachments.ts`, per `contracts/renditions.md`. `attachmentSchema` — what a sender writes — is unchanged.
- [ ] T046 [US3] **Derive the door set at runtime, because the compiler will not.** 4.14 made `state` required precisely so `tsc` would name every construction site; an optional property is silently correct everywhere. Write an assertion per door over a delivered payload and record the derivation in `specs/061-chapter-4-15/doors.txt`. **Start from 4.14's `doors.txt` and re-derive rather than re-read** — the previous answer is a fact about the previous shape.
- [ ] T047 [US3] Extend `withMediaStates` in `services/api/src/db/repository.ts` to carry the thumbnail. It already does one extra query per page for the state; **the thumbnail joins that same query rather than adding a second** — one `inArray` over parent ids. **Its `and(...)` already carries `eq(mediaObjects.environmentId, this.environmentId)` and the extension must keep it**: this is constitution I, and 4.12 found three tenancy scopes whose individual removal turned nothing red, so the predicate's presence is not something a suite will report on.
- [ ] T048 [P] [US3] Measure what T047 costs: buffers and time for a 50-message page with and without the join, on the lane's busiest environment. 4.12's index headline was a measurement of a query that chapter did not send; **measure the query that ships.**
- [ ] T049 [P] [US3] Write `services/api/src/media/rendition-delivery.itest.ts`: an authorised caller gets the thumbnail; an unauthorised one gets the parent's refusal byte-identically; a second tenant's credential is what makes that honest.
- [ ] T050 [P] [US3] Assert `thumbnail` is **absent, never null** (invariant 1) and that `thumbnail` implies `state === "ready"` in **both** directions (invariant 2).
- [ ] T051 [P] [US3] Assert a `pending` attachment offers no thumbnail, and that 4.14's `media.updated` is still what tells a client to look again. **The frame stays a notification, not a payload** — assert the frame's shape is unchanged, because a chapter that adds a fact is where somebody puts it in the event too.
- [ ] T052 [US3] Find every existing test that asserts a **whole attachment array** and update it. 4.14 found five, one a directory away and one in `packages/outsider` that only CI reached. **Grep for the assertion shape, not for the file names** — a sweep beats a battery for finding a class.
- [ ] T053 [US3] Run the accounting tests that fire when a delivered shape changes. 4.14 had five: the union's length, the gateway's advertised vocabulary, a derived count, a classified-exactly-once check and a non-inbound refusal loop. **Only `pnpm coverage` found them**, because three live in the gateway's lane.
- [ ] T054 [US3] Run the isolation gauntlet. It is the suite constitution VI names as gating releases, and 4.9 found three of its attacks returning at their first line and reporting green.

---

## Phase 6: The probes, the measurements and the gates

- [ ] T055 Probe every arm of the rendition predicate **by deletion** (SC-004). **An arm here is an SQL clause inside `readableMediaObjectKey`, not a JavaScript branch** — the predicate is four `and(...)` conditions plus the parent resolution, and an SQL clause carries no branch for a coverage number to report (048's shape, 4.12's confirmation). Remove each arm individually, re-run the delivery suite and the gauntlet, and record each arm as **tested** or **unnecessary** by name. 4.12 measured a single-mutation probe reporting green for two of three real tenancy scopes; 4.14 found one arm unreachable at runtime and load-bearing at compile time. **Say which kind each one is, in the file.**
- [ ] T056 [P] Probe the environment scope on the parent lookup specifically. An SQL clause carries no JavaScript branch, so a coverage number reports nothing about it (048's shape, 4.12's confirmation).
- [ ] T057 [P] Measure SC-008's and FR-015's three figures in this repository, with their method and corpus provenance: thumbnail bytes over the lane's real images, wall-clock p50, and the change in one environment's stored total. **`research.md`'s figures came from six files of convenience and synthetic noise** — the chapter says which source every number came from.
- [ ] T058 [P] Re-measure the crossover against the lane rather than against synthetic noise, if the lane holds enough images above and below the bound. If it does not, say so — **the lane could not have failed the shape that does not scale** is 4.12's sentence and it applies to any figure taken here.
- [ ] T059 Run `pnpm coverage` and read the **real** exit code. `pnpm coverage | sed > f; echo EXIT=$?` reads `sed`'s status — **five times in this project, once in the session that quotes the rule.** Run it without the pipe.
- [ ] T060 [P] Check the per-file coverage pins that this chapter's files fall under, and run **both halves** of the unbindable-key probe: a pin whose key matches no file is silent (049). If a pin has to move, ask what the number is measuring first — 059 found a denominator that differs between machines and a pin that was right while its environment was wrong.
- [ ] T061 [P] Run `pnpm check:errors` against the **built** `dist`, `pnpm check:fences`, `check:docs`, `check:srs`, `check:figures` and `pnpm build`. Read the gates off `ci.yml`, not off memory (055-3).
- [ ] T062 Typecheck **every** turbo task, not the services you touched. `tsconfig.build.json` excludes tests, so `pnpm build` typechecks shipped code and not its tests — 4.14's CI failure was two lines in `packages/protocol/src/revision.test.ts`, found only after a push, because five services had been typechecked individually and the protocol package never.
- [ ] T063 Run `pnpm test:outsider` with the composed services up. No local lane reaches `packages/outsider`; it needs a composed stack and three variables, and it held 4.14's fifth whole-array assertion.

---

## Phase 7: The documents

- [ ] T064 Amend **FR-MED-05** in `docs/04-srs.md` — this task is FR-013 and SC-010, and nothing else discharges them: the image half met, the video half unmet by decision with R8's reason and reversal condition, on FR-MED-04's revision 1.20 precedent and FR-MED-07's 1.18. **Read the clause before editing it** — four documents once agreed on two clauses that do not exist, and what found it was opening the SRS to make the edit.
- [ ] T065 Add the revision row 1.22 to `docs/04-srs.md`'s revision table.
- [ ] T066 Write **ADR-34** in `docs/05-sad.md` (FR-014): the dependency, its drivers, the three rejected alternatives with their measured costs, and its reversal condition. **ADR-32's line does not carry** — it is about a program addressed over a socket, and a linked library is not that case, so ADR-34 makes its own argument (plan, Complexity Tracking).
- [ ] T067 [P] Check whether ADR-34 has a deep dive in `docs/06`. An ADR lives in two documents — the SAD's summary and `docs/06`'s argument — and 4.5 found ten passes amending the summary with nobody opening the 98-line deep dive.
- [ ] T068 [P] Amend **both** copies of the Part 4 table: `docs/12-part-4-structure.md` row 16 and `docs/07-tutorial-plan.md` row 16. Two copies, and a chapter that amends one of them is how they drift.
- [ ] T069 [P] Record the storage-quota consequence FR-012 requires: derived bytes are summed by `reserveMediaSlot` the moment the row exists, so a rendition can carry a tenant past the quota **with no request to refuse**. Say what the platform does, and note that chapter 4.16 owns the meter.
- [ ] T070 [P] Grep `docs/` for feature-local ids leaking into published documents (`FR-0\d\d`). **Nothing runs this check** (`gaps.md` 052-7) and a feature-local id reached two published documents three commits after reading a correction of the same defect.
- [ ] T071 Run `check:srs`, `check:docs` and `check:refs`.

---

## Phase 8: The chapter

- [ ] T072 Register 4.15 in `relay-tutorial/lib/tutorial.ts` with **all seven fields** — `id`, `path`, `title`, `status`, `readerProduces`, `sourceDoc`, `readerMinutes`. **`path` is unchecked by any gate** (4.14's analysis pass 6), and an unregistered id throws at build: `pnpm build` exited 1 for eight chapters' worth of gates after 4.4 and none of them rendered a page.
- [ ] T073 Write the chapter at `relay-tutorial/app/(en)/part-4/chapter-15/<slug>/page.mdx` (SC-012), 2,000–4,000 prose words, English only. The argument is the title: what a thumbnail costs is about 7 kB and 15 ms, and **the ratio is a fact about the parent** — 775× across a real corpus while the thumbnail's own size spans 4×.
- [ ] T074 [P] Write the `TRAP` box: `ON DELETE CASCADE` does the database and nothing does the store, so a raw `DELETE` leaves the bytes. At least one `TRAP` per code chapter is the bound `docs/07` §2 sets.
- [ ] T075 [P] Write the figures in `figures.ts`. Pass them as `code`, not `chart` — `check:figures` caught three dead diagrams `pnpm build` did not, all three rendering nothing on a page that compiled green.
- [ ] T076 Publish R1's option table and R2's crossover series. **Both halves**, because either alone teaches the wrong rule: the crossover says an image within the bound gains nothing, and the option table says the size argument did not decide the dependency.
- [ ] T077 Publish the three instruments that lied during R1 — `apk add imagemagick` with no delegates, the all-or-nothing `apk` transaction returning a zero that read as *no change needed*, and the `grep` with no positive control. They are the chapter's own working, and a document that only reports the plan working is one nobody trusts.
- [ ] T078 Write the chapter's fences. **A titled fence is a whole-body claim** (051-6) — an excerpt must be untitled, and 4.14 paid three fences for forgetting it. **Do not re-derive the fenced-file list here** — T007a counted it in phase 1, before the edits, which is the only point at which the number can still change how the work is sequenced. Re-count only files this chapter created. 4.5's remembered list of five was eight and wrong in both directions, and this feature's own first guess was wrong in both directions again.
- [ ] T079 Generate hunks from the checker's own replay: `pnpm check:fences --dump <dir> --at <page>`. **A bare `--dump` writes the END state** (4.13), and a generator that replays differently from the checker produces hunks the checker rejects. `-U6` is a default — regenerate wider when a pre-image matches twice, and check that `-U8` is not worse than `-U10`.
- [ ] T080 Put in the appendix (`fences/post-series.md`) any hunk whose anchor is the appendix's own line, and place it after the hunks it depends on. **The appendix applies after every chapter**, so a chapter hunk for a file the appendix also edits is written against a state no reader sees (4.8), and a hunk that works while unanchoring somebody else's is still a broken chain.
- [ ] T081 Read T007a's counted table and work the bill from it, biggest first. **Adding `sharp` costs nothing in fences** — the worker's `package.json`, its `Dockerfile`, its sources and `pnpm-lock.yaml` are titled in **zero** files. The bill is `repository.ts` (28 English pages, 50 of its 52 fences being `diff` hunks whose pre-images sit in the regions this chapter edits) and `schema.ts` (34). Expect the hunks near the five edited regions to need regenerating, and expect at least one to move to the appendix for 4.8's reason. **`patch --dry-run` is not the checker** (056-7): it applies with fuzz and offset where the checker needs exactly one exact match.
- [ ] T082 Run `pnpm check:fences` to 0 and `pnpm build` green (SC-011). **Run `check:fences` after any source edit**, not only at the end — the chain is a claim about `relay-platform`'s HEAD, so any platform edit after the hunks are written invalidates them, including one made to turn CI green (4.14).
- [ ] T083 [P] Count the prose words outside code fences and confirm the bound.

---

## Phase 9: The record and the close

- [ ] T084 Write `specs/061-chapter-4-15/baseline.txt` with every phase's measurements **in the order they were taken, including the ones that were wrong first**. R1 already has three.
- [ ] T085 [P] Write `specs/061-chapter-4-15/gaps.md`, numbered, carrying forward the open items and re-measuring each rather than copying it. **One entry is already known and is this chapter's own**: an optional property on the delivered arm is a strict-parse break for a client built against the previous protocol (`contracts/renditions.md`), the durable path is safe because it reads through the loose arm, and **no suite here can see the client half** — `packages/outsider` casts rather than parses. It is 060-10's client-side twin. 043 found four of twenty-three carried items wrong when re-measured and three closed with nobody working on them.
- [ ] T086 [P] Write `traceability.md` by **reading**, not by grep. 4.11's mechanical coverage map reported 14 of 51 requirements uncited and all 14 were covered in substance — fourteen alarms, fourteen false.
- [ ] T087 [P] Re-measure the carried ledger: 055-3 (`check:errors` has no CI job), 059-20 (the branch denominator, 33 local and 13 in CI), 050-8 (two test files spawning an ingester is not a deployment), 060-13 (`docker compose --profile services stop` with no service list stops the stores too), 059-11 (`media_events`, deferred to the erasure chapter).
- [ ] T088 Run the quickstart end to end and correct it in place, recording each wrong version and what it looked like. **It has been wrong six, five and three times in the last three chapters**, and four of 4.11's five produced a red that read as a platform defect. `quickstart.md` §1 is the only step run so far.
- [ ] T089 Stop the composed services, then run the full lane set one more time: `pnpm exec turbo run test --force`, `pnpm test:integration`, `pnpm coverage` without a pipe, `pnpm test:outsider` with the services up.
- [ ] T090 Commit each phase's work. Under five lines, no trailer.
- [ ] T091 **Push submodules first, then the superproject.** `ci.yml` lives in the outer repository and the other two are submodules checked out `submodules: recursive`, so the reverse order checks out gitlinks pointing at commits no remote has (4.14).
- [ ] T092 Compare the CI error set **per error** against T007's baseline, in both directions. One comparison supports *"this run introduced nothing new"*, not *"the set is stable"* — 4.11 ran three and found the middle one's extras present in neither neighbour, which is a flake rather than a regression.
- [ ] T093 If CI is red, fix the platform, **re-dump, re-hunk, and push both** — repairing a platform file invalidates the appendix hunks that publish it, which took `relay-tutorial`'s job red on 4.14's second push with nothing in that repository changed.
- [ ] T094 Tag `part4-ch15` on a commit that **checks out a working chapter**. 4.14's tag had to be moved off a commit that fails `pnpm typecheck`, because `README.md:8` promises a chapter's tag checks out that chapter's platform — and 047 found three Part 1 tags pointing at a superseded lineage that no gate could have caught.
- [ ] T095 Compress the previous feature's `CLAUDE.md` entry to its headline, measurement block and the findings still cited elsewhere, and add this one. **The file has a 150,000-character budget and the harness refuses it over that.**

---

## Dependencies

```
Phase 1 (setup)      →  Phase 2 (schema, protocol)
Phase 2              →  Phase 3 (US1)  →  Phase 4 (US2)  →  Phase 5 (US3)
Phase 3,4,5          →  Phase 6 (probes and gates)
Phase 6              →  Phase 7 (documents)  →  Phase 8 (chapter)  →  Phase 9 (close)
```

**US2 depends on US1** and this is not the usual independence. A rendition that no door
recognises as derived is bytes the delivery gate refuses and the reaper deletes, so shipping the
generator first would produce something that works and is wrong. **US3 depends on US2** for
anything to point at, though its schema half (T045, T050) can be written against a hand-planted
rendition row.

### Parallel opportunities

- **Phase 1**: T003–T006, **T007a** and T008 are independent reads.
- **Phase 2**: T012 and T013 touch different files.
- **Phase 3**: T019, T020, T022, T023 and T025 are separate files; T021 follows T020.
- **Phase 4**: T030, T031 and T034 are worker-local; **T032c and T032d** are independent measurements; **T037b** and T038–T041 are separate test files.
- **Phase 5**: T048–T051 are independent once T045 and T047 land.
- **Phase 6**: T056–T058 and T060–T061 are independent measurements.
- **Phase 7**: T067–T070 touch different documents.

### Suggested MVP

**Phase 1 + Phase 2 + Phase 3 (US1).** That is a platform that can say what a derived object is
and prove it survives and dies correctly — with no decoder, no dependency, and no ADR. It is
also the half of FR-MED-05 that the clause actually spells out, and the half two shipped clauses
would otherwise destroy.

### What this chapter does not build

FR-MED-10's reaper (row 22, the erasure chapter), FR-MED-12's meter (row 17), and the video
half of FR-MED-05, which is ruled out in writing with its price — 114 MB for the harder half of
a clause whose easier half chapter 4.13 already declined.
