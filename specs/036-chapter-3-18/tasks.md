# Tasks: chapter 3.18 — the message that never arrived

**Input**: `spec.md` (17 FRs, 11 SCs), `plan.md`, `research.md` (R1–R10),
`contracts/fanout-publisher.md`, `data-model.md`, `quickstart.md`

**Tests are requested.** Principle VI is test-verified delivery, and nine of eleven success
criteria are assertions. Test tasks precede the implementation they cover.

## Format: `[ID] [P?] [Story] Description`

`[P]` = parallelisable (different files, no dependency on an incomplete task).
Story labels on user-story phases only.

## Path conventions

    relay-platform/    the running system (api, gateway, packages)
    relay-tutorial/    the chapter, both locales, and the fence chain
    specs/036-chapter-3-18/    this feature's record

## The publish site, established before any task was written

`messages.controller.ts:144` calls `this.messages.send(...)` and then assembles the public
response by hand — `id`, `channel_id`, `seq`, `text`, `created_at`, `user: actingExternalId`.
**Those are the six fields the fan-out payload needs** (`messageSchema`, `frames.ts:15`, is a
`z.strictObject` of exactly those six), all in scope, plus `message.duplicate` on the returned
`MessageRow`. The publish goes immediately before that `return`.

**It does not go in `messages.service.ts`.** Two callers reach `send()`:
`messages.controller.ts:144` (public REST) and `internal.controller.ts:65` (the gateway's own
send path). A publish in the service would publish for the socket path too — where the gateway
already publishes — and deliver **every socket-sent message twice**. That is FR-006, and T013 is
the test that would have caught it.

## Where the tests live — the fixture census, corrected

The first version of this section claimed no fixture boots a real api with a real gateway. **That
was wrong**, and the correction matters because it decides where the end-to-end test goes:

    services/gateway/src/session.itest.ts   REAL api, SPAWNED from services/api/dist/main.js
                                            (:106 startApi — seeds a real environment, user,
                                            channel, membership and key; its own error says
                                            "the suite talks to the real service, not a stub")
                                            2 sockets · NO FAN-OUT WIRED (:224 passes none)
    services/gateway/src/resume.itest.ts    stubbed api · 2 gateway instances · 6 sockets
                                            · fan-out wired (:65, :76) · :123 already publishes
                                            from a second client on the same subject
    services/gateway/src/fanout.itest.ts    fabric only — 0 gateway boots, 0 socket opens
                                            (:11 "Two fabric clients stand in for two
                                            gateway instances")
    services/api/**.itest.ts                no suite opens a socket; three reach a real Redis
    packages/outsider/                      RELAY_API_URL and RELAY_WS_URL — sealed, against a
                                            platform it did not start

The earlier census searched `services/gateway/src` for `NestFactory` and `AppModule`, found
nothing, and concluded no real api existed. The harness spawns the api's **built output** instead
of importing it, so the mechanism searched for was not the mechanism in use. Recorded because it is
the fifth instance in this project of a pattern matching the examples in front of it rather than
the set the rule names.

So the feature is proven at three levels, and each task says which it is:

| level | what it proves | where |
|---|---|---|
| **publisher** | the api publishes a payload that satisfies `messageSchema`, to the right subject, under the right conditions | `services/api/src/fanout/fanout.itest.ts` — a real Redis subscriber |
| **delivery** | a frame on `chan:{id}` reaches the right sockets and not the wrong ones | `session.itest.ts` (once T014 wires a fan-out) and `resume.itest.ts` for the two-instance case |
| **end-to-end** | a real REST send reaches a real socket | `session.itest.ts` — real spawned api, real gateway, real socket. `packages/outsider/` keeps SC-010's sealed exercise |

---

## Phase 1: Setup

- [ ] T000 Create `specs/036-chapter-3-18/baseline.txt`, `chapter-notes.md`, `gaps.md` and `traceability.md` as empty skeletons **now**, in Phase 1. Eleven tasks across Phases 2–8 write into them; without this, a finding in Phase 2 has nowhere to land for six phases and is carried in memory until close-out, which is how findings get lost. T061 then *completes* what earlier phases accumulated rather than authoring it from scratch
- [ ] T001a **Identify the fence chain's predecessor commit and write it into `specs/036-chapter-3-18/baseline.txt`.** It is a commit, not the `part3-ch17` tag: feature 034's tail amended a platform file *and* a chapter fence after tagging, which cost 3.17 five wrong answers. Find it the way 3.17 eventually did — `git log` on the platform files this feature touches, against what `part3-ch17` points at. Naming it here is what stops T050 guessing
- [ ] T001 Pin the lane environment in `specs/036-chapter-3-18/baseline.txt` **from `relay-platform/turbo.json`, which is the authoritative list**: its `test:integration` task declares an `env` array of **twenty-six** variables. CLAUDE.md's *"four variables and one stopped compose profile"* is a record of 3.17's incident, not the environment — and it was read as a specification for twelve analysis passes while the real list sat in the build config. Pin all twenty-six, and name the four that actually bit, with their failure counts from `specs/035-chapter-3-17/baseline.txt:596`:

        DATABASE_URL=postgres://relay:relay@localhost:15432/relay
        RELAY_INTERNAL_CREDENTIAL=…            unset -> 7 failures, limits and gauntlet
        RELAY_INTERNAL_CREDENTIAL_GATEWAY=…
        RELAY_NATS_URL=nats://localhost:4222   the lane defaults to 14222 -> 1 failure

    Plus the ports this feature needs (Postgres 15432, Redis 16379 — this machine's own Postgres holds 5432) and the compose profile. `test:integration` is `cache: false` and `dependsOn: ['^build','build']`, so the lane builds first — which is what satisfies `session.itest.ts:113`'s refusal to run without `services/api/dist/main.js`
- [ ] T001b **Bring the stack up — and note that the lane has two environments with different ports.** No task said this for fifteen passes: every document states a destination and none stated a command.

    **CI's `platform` job runs `test:integration` and `coverage` against GitHub service containers on the DEFAULT ports** (`ci.yml:24–50`) — postgres `5432:5432`, redis `6379:6379`, nats `4222:4222` — with the job `env` supplying `DATABASE_URL: postgres://relay:relay@localhost:5432/relay`, `RELAY_REDIS_URL: redis://localhost:6379`, `RELAY_NATS_URL: nats://localhost:4222`. Its comment is the reassurance, not a claim that ports match: *"Same images as compose.yaml, so a lane that passes here passes there."*

    **Locally the stack needs 15432 because this machine's own Postgres holds 5432**, and `compose.yaml` defaults to 5432. So `baseline.txt` must say **which environment each number describes** — an unlabelled "15432" is a property of this machine, not of the lane. The local command, from `ci.yml`'s outsider job:

        RELAY_POSTGRES_PORT=15432 docker compose up -d --wait
        DATABASE_URL=postgres://relay:relay@localhost:15432/relay \
          node services/api/dist/db/migrate.js

    `--wait` matters: without it the suites race container readiness. `compose.yaml` starts five infrastructure services with no profile — postgres, redis, nats, clickhouse, mailpit — and holds `api`, `gateway` and `dispatcher` behind `profiles: ["services"]`.

    **The two lanes need different things.** `pnpm test:integration` needs infrastructure only, because `session.itest.ts:106` spawns its own api from `dist/main.js`. **The outsider needs the app containers and a seeded tenant**, per CI:

        RELAY_POSTGRES_PORT=15432 docker compose --profile services up -d --wait
        RELAY_DEMO_CREDENTIAL=$(RELAY_POSTGRES_PORT=15432 node scripts/seed-demo-tenant.mjs)
        export RELAY_DEMO_CREDENTIAL
        export RELAY_API_URL=http://localhost:4000
        export RELAY_WS_URL=ws://localhost:4001

    The seed is not optional and not obtainable another way — CI's comment: *"the suite needs a credential that must already exist. There is no public way to obtain one — sign-up ends at an OAuth consent screen and key management is the dashboard's chapter."* **T003 and T023 both run in that lane and neither can start without all five lines.** There is also a documented networking trap in adding `--profile services` carelessly: the app containers read `postgres:5432` on compose's own network while a host service is on `localhost:5432`
- [ ] T002 [P] Record the starting state in `specs/036-chapter-3-18/baseline.txt` — integration test count, lane mean, coverage pins for every file this feature touches, `pnpm check:fences` file count — measured, not carried over from 3.17's close. **Record all five gate outputs, not just the test numbers** — they are what T053 and T054 compare against, and they were measured green in analysis pass 12:

        check:srs      245 clause rows, 245 unique · classes ASM CON DR EIR FR NFR
        check:docs     all mirrored docs match their sources
        check:figures  212 figures, every diagram passed as `code`
        check:fences   212 fenced files, 34 chapters, 34 translated, 1 retired
        check:errors   17 codes, 17 sections · dist current, 0 src files newer

    **Record the static page count** (91 at 3.17's close) — it is the only observable that would reveal a `lib/tutorial.ts` entry missing: `check-figures.mjs:35` walks `app/` on disk and never reads the registry, so a page with no entry passes every gate and does not route (T049a). **Record the per-suite cost of an api boot separately**: `services/api/src/fanout/fanout.itest.ts` is a NEW suite and the lane is `--concurrency=1`, so it costs a boot rather than a handful of assertions. 3.17 moved 407 -> 589 tests for +0.55 s *within existing suites*; that number does not predict this one, and the budget is 240 s against a 193.55 s mean
- [ ] T003 [P] Confirm the failing state that justifies the chapter in `relay-platform/packages/outsider/src/integrate.itest.ts` — **T001b first**, all five outsider lines, or this task fails on the stack rather than on the feature — send over REST, wait on a socket, watch it **time out**. **Invert the test already at `:233`; do not add one beside it.** It is titled *"receives a message on a socket — SENT over the socket"* and its comment reads *"THE SEND HAS TO BE ON THE SOCKET… the api still publishes to no fan-out, so nothing arrives LIVE… Half the gap, and the half that remains is the fan-out."* **The title encodes the workaround this chapter removes** (FR-018), so title, comment and premise all change. The file is fenced by chapters 3.14 and 3.17. Record the failure mode in `baseline.txt`. A scenario that passes now is testing something else (3.17's T047c)

## Phase 2: Foundational (blocking — every story depends on these)

### The grammar move

- [ ] T004 Create `relay-platform/packages/protocol/src/fanout.ts` with `subjectFor(channelId)` **only**, moved verbatim from `services/gateway/src/fanout.ts` including the comment explaining one subject per channel. **`DEFAULT_REDIS_URL` does not move** — it is declared in `api/src/limits/store.ts:44`, `gateway/src/fanout.ts:27` and `gateway/src/limits.ts:22`, and consolidating one of three copies leaves a shared definition plus two locals. A connection URL is configuration, not protocol
- [ ] T005 Export `subjectFor` from `relay-platform/packages/protocol/src/index.ts`
- [ ] T006 [P] Unit-test the grammar in `relay-platform/packages/protocol/src/fanout.test.ts` — `subjectFor(id) === \`chan:${id}\``. It is a pure string assertion and belongs beside the definition, not in an integration suite that needs Redis
- [ ] T007 Delete `subjectFor` from `relay-platform/services/gateway/src/fanout.ts` and import it from `@relay/protocol`. **Correct the comment at `:11` in the same edit**: it reads *"The instance that handled a send publishes the committed message AFTER the api's response"*, and this feature makes that false for the REST path — the instance that handled the send is the api, for half of all sends. Chapter 2.6 fences this file **whole**, so that sentence is published prose in two locales, and nothing but this task will change it. `gaps.md` item 8 is the precedent: a published Trap contradicting 3.17's own chapter survived fifteen analysis passes because no checker reads prose. **No re-export** — one name for one thing, so consumers take it from the package. `fanout.itest.ts:8` imports `createFanout, subjectFor, type Fanout` on one line; that line splits in two. Move the grammar assertion at `fanout.itest.ts:150` to T006 rather than leaving it testing a moved function from an integration lane
- [ ] T008 Run `pnpm build` before believing any checker: `check:errors` reads `packages/protocol/dist/codes.js`, the built artifact, and a stale `dist` makes it green for the wrong reason. `session.itest.ts:113` also refuses to run without `services/api/dist/main.js`

### The publisher

- [ ] T009 Create `relay-platform/services/api/src/fanout/publisher.ts` — a `MessagePublisher` with `publish(message)` and `close()` only, one ioredis client, per `contracts/fanout-publisher.md`. Client options come from `services/api/src/limits/store.ts` (`lazyConnect`, `maxRetriesPerRequest: 0`, `connectTimeout: 1_000`, and an `error` listener), **not** from `createFanout`, which has neither (R10). It reads `RELAY_REDIS_URL` the way `limits/store.ts:86` already does, so this feature adds no configuration. **Its `fanout.publish_failed` line carries `request_id` and `environment_id`** — NFR-OBS-01 requires both, `Logger.log(level, msg, fields)` injects nothing, and the api supplies them elsewhere (`request-context.middleware.ts:33`, `rate-limit.middleware.ts:247`). The gateway's line omits them because the gateway is not in a request; this one is. **`environment_id` goes in the log fields and never in the payload** — `messageSchema` is a `z.strictObject` of six, and `data-model.md:33` names `environment_id` as one of the two extra keys this site is most likely to add, which would deliver nothing while the send returned `201`. The log is an open record; the payload is closed. Carry all three reasons in a comment
- [ ] T009a **Carry `limits/store.ts`'s down-window into `relay-platform/services/api/src/fanout/publisher.ts`**, not just its four client options. That file says the options alone *were* the slow version: *"each request paid a second or more, twice… So a known-down store is not retried on the request path. The first failure opens a window; while it is open every call answers `null` immediately."* `DOWN_WINDOW_MS = 5_000`, a `downUntil` stamp, cleared on success. **47 send-message calls across 8 api integration suites** will publish once this ships — with a dead Redis and no window each pays about a second, against NFR-PRF-02's 150 ms
- [ ] T009b Test the window in `relay-platform/services/api/src/fanout/publisher.test.ts`: with the client throwing, the **second** publish inside the window makes no attempt at all. What would have to be false for this to fail? That the window exists — so assert on the client being untouched, not on the publish resolving, which it does either way
- [ ] T009c **Decide whether the publisher joins the api's off-switch family, and record the argument either way.** Four api modules carry one — `outbox.module.ts:20` (*"`RELAY_OUTBOX_RELAY=off` exists for the suites that want a…"*), `webhooks.module.ts:31` (*"the sibling of `RELAY_OUTBOX_RELAY`"*), `notifications.module.ts:20` (*"same switch and same reasoning"*), and the event consumer — all shaped `(process.env.RELAY_X ?? "on").toLowerCase()`, all set to `"off"` in CI's lane `env` for the reason CI states: *"a background daemon draining the table two suites are asserting on is a race between test files, not a property."*

    **The fan-out publish is that class of machinery**: once this ships, 47 send sites across 8 api suites publish on every run, and T014 gives `session.itest.ts` a live subscriber. Either add `RELAY_FANOUT_PUBLISH` following the family, or record why per-channel subjects make cross-suite interference impossible — **silence is the one option the convention rules out.** Note the symmetry: pass 3 found the *lifecycle* half of this same family's convention (T012a) from the same grep and missed the switch half
- [ ] T010 [P] Unit-test the publisher in `relay-platform/services/api/src/fanout/publisher.test.ts`: the subject is `chan:{id}`, the payload parses against `messageSchema`, and `publish` **resolves** when the client throws
- [ ] T011 **Set an explicit coverage pin** for `services/api/src/fanout/publisher.ts` in `relay-platform/vitest.coverage.config.mts`, and prove it bites by deleting T010's throwing-client case and watching it go red. **Unlisted files fall under the global `70`** — a ten-line publisher clears that with its `catch` untested, which is exactly the path FR-010 and FR-011 depend on. A pin added after the fact ratchets to whatever happened; this one is chosen. **Pin `services/api/src/messages/messages.controller.ts` too, or record why not**: only `messages.service.ts` is pinned today (`:384`), and the publish guard's two branches — `!duplicate && text !== null`, FR-007's entire mechanism — would otherwise sit under the global 70 as well
- [ ] T012 Wire the publisher into `relay-platform/services/api/src/messages/messages.module.ts`, following `services/api/src/limits/limits.module.ts:36`'s pattern — `{ provide: …, useFactory: … }`, the way the api already provides its Redis-backed counter store. **Provide it; do not export it.** `internal.module.ts:31` imports `MessagesModule` and *"reuse[s] MessagesModule's providers wholesale"*, so an exported publisher is injectable from the one route that must never publish (FR-006). `MessagesModule` already withholds `"DB"` this way (`internal.module.ts:26`) — FR-006 then holds by module boundary, not only by where the call sits
- [ ] T012a Add a `…Lifecycle implements OnModuleDestroy` to `relay-platform/services/api/src/messages/messages.module.ts` that calls `publisher.close()`, copying `CounterStoreLifecycle` at `services/api/src/limits/limits.module.ts:26` — it closes the analogous Redis client. `limits.module.ts:10` states the convention: *"resource in this api closes through `OnModuleDestroy`"*, and six modules implement it. **A `close()` nothing calls is a leaked handle in an api that boots once per integration suite**
- [ ] T013 Write the FR-006 guard test in `relay-platform/services/api/src/fanout/fanout.itest.ts` **before** T012's wiring is trusted: a send through the **internal** route publishes **nothing**, asserted by count on a Redis subscriber over a window (SC-003). **It will pass vacuously here, and that is recorded rather than mistaken for a result**: the publish does not exist until T024, so in this phase nothing publishes anywhere and the answer to "what would have to be false for this to fail?" is *everything*. Record the vacuous green in `baseline.txt` the way T003 records its expected timeout. T026a is the run that means something

### The delivery harness

- [ ] T014 Wire a fan-out into `relay-platform/services/gateway/src/session.itest.ts`'s harness. `:224` calls `attachSessions({ server, api, logger })` with no `fanout` key, and `session.ts:125` declares `fanout?: Fanout` — so today `fanout?.publish` is a no-op and **nothing in that suite subscribes to any subject**. Every delivery test below needs this. **Add it as a new capability, do not change what the existing fixture is**: promoting or repurposing a shared gateway fixture took five tests down in 3.17's T040b, the fifth such incident in two features. Run the whole gateway suite after, not just the new test
- [ ] T014a **Decide whether `relay-platform/services/gateway/src/session.itest.ts` joins the fence chain**, and record the decision in `specs/036-chapter-3-18/chapter-notes.md`. It is fenced by **no chapter** today — outside the chain like `sentinel.ts`, `sentinel.sql` and `guard.itest.ts` (`gaps.md` item 7) — and T022 puts this chapter's end-to-end test in it. Fencing it adds a file to the chain for the first time and binds every later chapter that edits it; not fencing it means the chapter shows a test the chain never verifies. Either is defensible; discovering it at T052 is not

## Phase 3: User Story 1 — a REST send reaches a connected member (P1) 🎯 MVP

**Goal**: `POST /v1/channels/:channelId/messages` reaches an already-open socket.
**Independent test**: T022, and T003's outsider scenario now passing.

### The ordering, now settled in the spec

- [ ] T015 [US1] Verify the amended **FR-005** holds as written before the publish goes in: the clause now splits by transport — socket is commit/ack/publish, REST is commit/publish/respond — because the response *is* the acknowledgement and a handler cannot publish after it without detaching. Confirm the amendment is in `spec.md`, and carry its recorded cost into the chapter: **NFR-PRF-01's clock is not measurable on the REST path** because the interval can be negative
- [ ] T016 [US1] Measure `PUBLISH` p50/p95 from the api against a live Redis and put it in `specs/036-chapter-3-18/baseline.txt`. The publish now lands inside NFR-PRF-02's budget (p95 < 150 ms for the whole write); `contracts/fanout-publisher.md` asserts sub-millisecond, and an assertion is not a measurement

### Tests for User Story 1 — publisher level

- [ ] T017 [P] [US1] **FR-004**, the feature's core clause, in `relay-platform/services/api/src/fanout/fanout.itest.ts`: a REST send publishes to `chan:{channelId}` after the write commits. Assert on a real Redis subscriber, so the test names the subject rather than trusting delivery
- [ ] T018 [US1] **Assert the published payload against `messageSchema` itself**, in `relay-platform/services/api/src/fanout/fanout.itest.ts` — not against a list of mistakes. One `safeParse` covers a seventh key, `channel_id` in place of `channel`, a missing `user`, a non-positive `seq`, a null `text`, and a `created_at` that is not RFC 3339. `fanout.itest.ts:128` proves an invalid **value** is dropped and nothing proves an extra **key** is; the schema is the class definition, and a checker that fails on an unknown member beats one that enumerates the known ones
- [ ] T019 [US1] **FR-009, SC-008** in `relay-platform/services/api/src/fanout/fanout.itest.ts`: the payload the api publishes is indistinguishable from what a socket send publishes, compared **field by field** with only `id`, `seq` and `created_at` controlled. **Do not use `withoutRequestId`** — the oracle deletes `request_id` from an error body so two envelopes can be compared whole, and a fan-out payload has no such field, so it would be an identity function dressed as rigour. This is frame equality, not tenant isolation. Build the two payloads from independent sources: **a shared helper moves both halves of a pair and the comparison then sees nothing** (3.17's T044)
- [ ] T020 [US1] A send to a channel with no connected member publishes and the send still returns `201`, in `relay-platform/services/api/src/fanout/fanout.itest.ts` (spec edge case 2 — a frame nobody hears is correct, not a loss)

### Tests for User Story 1 — delivery level

- [ ] T021 [P] [US1] The same user on two connections receives the frame on **both**, in `relay-platform/services/gateway/src/session.itest.ts` (needs T014). What is under test is the registry's fan-out to local sockets, so the publisher's identity is irrelevant — publish to `chan:{id}` directly (spec edge case 5)

### Test for User Story 1 — end-to-end

- [ ] T022 [US1] **SC-001** in `relay-platform/services/gateway/src/session.itest.ts` (needs T014): a real REST send against the spawned api reaches a real socket on the gateway. This is the whole feature in one assertion, and the harness that makes it possible already existed
- [ ] T023 [US1] T003's inverted test in `relay-platform/packages/outsider/src/integrate.itest.ts`, now green — a REST send reaching a socket, under a title that no longer says the send has to be on the socket. Record in `chapter-notes.md` that the exercise's own gap record is closed: chapter 3.17 removed one of its two causes and this chapter removes the other. The outsider adds what the integration lane cannot: it follows the README rather than the source, and it is sealed against workspace imports

### Implementation for User Story 1

- [ ] T024 [US1] Add the publish to `relay-platform/services/api/src/messages/messages.controller.ts` — fenced by **six** chapters, most recently `part-3/chapter-17`, so 3.18's fence for it is built against 3.17's version and not against a generic HEAD — immediately before the `return` that assembles the response. Six fields: `channel: message.channel_id` (**renamed** — the frame's field is `channel`), `user: actingExternalId`, and `id`/`seq`/`text`/`created_at` from `message`
- [ ] T025 [US1] Guard it in `relay-platform/services/api/src/messages/messages.controller.ts` with the two conditions mirrored from `session.ts:651` — `!message.duplicate` (**FR-007**) and `message.text !== null`. Carry the gateway's reasons across, and **record the second reason `session.ts` does not give**: `messageSchema.text` is `z.string()`, non-nullable, so a tombstone cannot be published at all — it would be dropped as `fanout.invalid_payload`. The guard has two independent justifications and only one is written down today
- [ ] T026a [US1] **Make T013 mean something.** With the publish in place, move it from `messages.controller.ts` into `messages.service.ts` — the plausible wrong site, and the one two callers make dangerous — and watch T013 go **red**. Put it back. Record both runs in `specs/036-chapter-3-18/baseline.txt`. Until this is done, T013 is a green test whose subject did not exist when it passed; this is T038's practice applied to the guard that lacked it, and SC-003's count is only evidence after it
- [ ] T025a [US1] **Retire the four comments this feature falsifies (FR-018).** All four are in files chapters fence, which makes them published prose in two locales: `services/gateway/src/fanout.ts:11` (*"The instance that handled a send publishes… AFTER the api's response"* — also T007's), `services/gateway/src/public-surface.itest.ts:309`, and `services/gateway/src/isolation.itest.ts:381` and `:596–597`. `isolation.itest.ts:381` needs care for a second reason: it documents *"no fan-out — `attachSessions({server, api, logger})` passes none"*, which T014 makes untrue of `session.itest.ts` and leaves true of this one. **Correct only present-tense claims** — a sentence saying what a chapter *recorded* stays true
- [ ] T026 [US1] Verify **FR-008** by construction in `relay-platform/services/api/src/messages/messages.controller.ts`: `send()` throws on a refusal, so a publish on the success path never runs for one. **Do not use `finally`** — a `finally` publishes after a `403`

## Phase 4: User Story 2 — sender and recipient on different instances (P1)

**Goal**: the api that accepted the send has no relationship with the gateway holding the socket.
**Independent test**: two gateway instances with real sockets, one frame on the subject, the member's instance delivers and the other does not.

- [ ] T027 [P] [US2] **SC-002's delivery half** in `relay-platform/services/gateway/src/resume.itest.ts` — two gateway instances, real sockets, `:90`'s *"Another gateway instance, as far as Redis is concerned"*, and `:123`'s existing pattern of a second fan-out client publishing on the same subject. Assert the member's socket receives it. This is stronger than `fanout.itest.ts:89`, which has no sockets at all
- [ ] T028 [US2] The negative half, same file: an instance holding no member of the channel delivers nothing. The subject is the filter, and `fanout.itest.ts:102` proves it at the fabric — this proves it at a socket
- [ ] T029 [US2] Check the blast radius of `relay-platform/services/gateway/src/resume.itest.ts`'s shared `boot()` fixture before changing it, the same discipline T014 applies to `session.itest.ts`. If it needs a new capability, add one (3.17 used `disposable()`) rather than changing what the existing one is
- [ ] T030 [US2] State the limitation in the chapter and in `specs/036-chapter-3-18/chapter-notes.md`: **the two-instance case uses a stubbed api and the real-api case uses one instance.** `resume.itest.ts` stubs the api (`:21`), `session.itest.ts` spawns a real one but boots a single gateway. SC-002's full claim is a composition of the two, and saying so is the alternative to a quiet claim

## Phase 5: User Story 3 — no delivery to somebody who may no longer see it (P2)

**Goal**: FR-013's clause, and the plan's largest open risk.
**Independent test**: remove a member, send to the channel, assert nothing arrives on their socket within the clause's window.

- [ ] T031 [US3] **Establish where membership is checked before writing an assertion about it**, and record it in `specs/036-chapter-3-18/research.md`. R5's measurement: delivery filters by *subscription*, via `registry.subscribersOf(channelId)` at `session.ts:175`; the channel list is a snapshot from `POST /internal/session` at connect time; nothing in the delivery path re-reads membership
- [ ] T032 [US3] Test the **socket** path first, which this chapter did not create, in `relay-platform/services/gateway/src/session.itest.ts` (needs T014): remove a member while their socket is open, send, see whether a frame arrives. If the socket path already fails FR-RTM-10, this chapter did not cause it and must not claim to have fixed it
- [ ] T033 [US3] Test the REST-originated path in `relay-platform/services/gateway/src/session.itest.ts` (SC-006), with the clause's five-second window as the bound rather than an arbitrary one. **The api publishes regardless of membership** — it does not read it at the publish site — so if the frame is filtered, the filter is the subscription and the answer belongs to the gateway
- [ ] T034 [US3] If either path misses the window: record it in `specs/036-chapter-3-18/gaps.md` with an owner, state it plainly in the chapter, and do **not** narrow FR-013 to make it pass. FR-RTM-10 is P1 and a quiet claim here is the defect this chapter exists to remove, one clause over
- [ ] T035 [US3] **FR-014, SC-007** in `relay-platform/services/gateway/src/session.itest.ts` (needs T014): a private channel's message reaches no non-member's socket. **This is a fourth door onto FR-CHN-05** and gets its own test rather than an inference from the read paths' three
- [ ] T036 [US3] In `relay-platform/services/api/src/fanout/fanout.itest.ts` — a banned sender, an archived channel, an exhausted quota, and an application key naming a person: each refused, each publishing nothing (SC-004). Four refusals, and each assertion states what would have to be false for it to fail
- [ ] T036a [US3] **FR-008a — the fifth refusal, and the only one constitution I calls NON-NEGOTIABLE.** In `relay-platform/services/api/src/fanout/fanout.itest.ts`: a send naming a channel that belongs to **another tenant** publishes nothing, asserted on a **Redis subscriber** rather than on the response. `POST /v1/channels/:channelId/messages` is isolation target `services/api/src/isolation/targets.ts:185` and the gauntlet already attacks it with foreign ids on every build — but its oracle compares responses, and its own comment says so: *"nothing of the victim's came back, not that a status was 4xx."* **A publish is a channel that oracle cannot see**, so a frame emitted onto a foreign tenant's subject would leave the whole suite green. Subscribe to the victim's subject, attack with the victim's channel id, assert silence. Do not extend the gauntlet — comparing responses is what it is

## Phase 6: Failure, and the tests that must not pass for the wrong reason

- [ ] T037 **FR-010 and SC-005** in `relay-platform/services/api/src/fanout/fanout.itest.ts` — with the publisher pointed at a dead port, a REST send returns `201` and the message is recoverable through the api's own history route. **This is the constitution's gate**: principle IV's *"Any new delivery mechanism MUST preserve this recovery property"*. No socket is needed; resume reads Postgres. Use `limits.itest.ts:510`'s established pattern — `"redis://127.0.0.1:1"` — rather than stopping the server: in-process, deterministic, and already in the repository
- [ ] T038 **Prove T037 can distinguish anything**, in `relay-platform/services/api/src/fanout/fanout.itest.ts`. `publish` swallows its own errors and resolves (R8), so "the send returned 201 while Redis was down" is equally true of a publisher that does nothing. Delete the publish call, run T037, and watch it stay green. Then make the assertion the **`fanout.publish_failed` log line** (**FR-011**), and re-run the deletion to watch it go red. Record both runs in `baseline.txt`
- [ ] T039 Measure the REST send's p95 against a dead port into `specs/036-chapter-3-18/baseline.txt` (R10's hazard). `limits/store.ts` learned this the hard way: *"an outage that instead adds seconds to every request has refused it in a slower way, and NFR-PRF-02 asks for a p95 under 150 ms"*. Measure the same path with `createFanout`'s default options for the contrast — that number is what justifies not copying the gateway's client
- [ ] T040 Measure a **connected but slow** Redis into `specs/036-chapter-3-18/baseline.txt` — the residual risk `plan.md`'s post-design re-check named and the contracts did not close. `maxRetriesPerRequest: 0` and `connectTimeout` bound a dead server; neither bounds a slow one, and ioredis has no command timeout unless one is set. If a hung Redis holds every send open, add `commandTimeout` to `services/api/src/fanout/publisher.ts` and say so
- [ ] T041 [P] Verify R10's gateway claim rather than repeating it: point the gateway's fan-out at a dead port, send on a socket, watch the process. `relay-platform/services/gateway/src/fanout.ts` attaches no `error` listener to either client and no test anywhere covers a dead fan-out. **If the process dies, that is pre-existing and this chapter surfaced it** — record it in `specs/036-chapter-3-18/gaps.md`, and decide deliberately whether fixing it belongs here

## Phase 7: The chapter

- [ ] T042 Decide the two file counts in `specs/036-chapter-3-18/chapter-notes.md` and keep them in separate columns from here to close-out: **what the chapter teaches** drives the word estimate, **what it must fence** drives the chain. `plan.md` predicts nine and thirteen. Neither number is ever asked to do the other's job
- [ ] T043 Estimate the prose in `specs/036-chapter-3-18/chapter-notes.md` from the number of **arguments**, not from a per-file rate. 3.15 and 3.16 agreed on ~154 words per taught file and 3.17 came in at 84.7 — 45% below. `plan.md` names **six** arguments and estimates 2,650–3,350 words against the series' 2,000–4,000 bound (SC-011). It named five until pass 7, which found three more had arrived and two of the eight did not survive the cut — re-derive rather than carry the number, and if the argument count has moved again, the estimate moves with it
- [ ] T044 Write `relay-tutorial/app/(en)/part-3/chapter-18/the-message-that-never-arrived/page.mdx`. The chapter's five arguments: the ordering that cannot be copied to REST, the two NFRs pulling opposite ways, why the grammar moved and the client did not, the recovery property under a lost publish, and what T031–T034 found about membership
- [ ] T044a **MDX is not markdown**, and this chapter shows a six-field JSON payload and log lines — the two shapes that break it. An indented `{"code": …}` block is literal text in markdown and a **JSX expression** in MDX: `Could not parse expression with acorn`, line 3134 of a 4,400-line page, is the recorded instance. Every brace block in `page.mdx` goes inside a fence, and the page builds before it is translated
- [ ] T044b Record the subject grammars' asymmetry in `specs/036-chapter-3-18/chapter-notes.md` — **not in the chapter**, which is pass 7's word-estimate decision: it is a sidebar a reader following the build does not need. This chapter is what makes it visible: moving `subjectFor(channelId)` into `packages/protocol` puts it beside `subjectFor(type, environmentId)` (`internal.ts:112`), and **the event spine's subject carries the tenant while the fan-out's does not**. It is defensible — a channel id is a globally unique UUID, and a gateway subscribes only to channels a tenant-scoped session named at connect — but a reader seeing both functions in one file will ask, and the answer is not in either signature
- [ ] T045 State **FR-002** in `page.mdx`: there is **no SRS amendment**, principle VI is satisfied by citation, and the unmet clause is **FR-RTM-01** — not FR-RTM-05, which `docs/07-tutorial-plan.md`'s row names (**FR-001**). A reader arriving from 3.17, where the amendment *was* the gate, will look for one. Note that FR-005 *was* amended, in this feature's own spec, and say why that is a different kind of amendment
- [ ] T046 State **FR-003** in `page.mdx`: FR-RTM-05 names six event kinds and this chapter delivers one, because one is all that has a producer. `message.updated` and `membership.changed` have none outside tests, and nothing writes `messages.edited_at` or `messages.deleted_at`
- [ ] T047 State **FR-012** in `page.mdx`: what a client may conclude from having received nothing. A missing frame is not evidence a message does not exist — resume is the guarantee, the fan-out is the optimisation
- [ ] T047a **Run the `humanizer` skill as a dedicated editing pass** over the finished English chapter, before it is translated. Every Spec Kit preamble in this repository says to apply `PROSE-IN-GENERATED-DOCS.md` while generating and to load the full skill for an editing pass, and **no task had asked for one** — over 2,650–3,350 words. Do it before T049, so the Vietnamese twin is translated from edited prose rather than translated and then edited twice
- [ ] T048 [P] Write `relay-tutorial/app/(en)/part-3/chapter-18/the-message-that-never-arrived/figures.ts`, and pass every binding through the prop named **`code`** — `<Figure code={figX} … />`. `check:figures` enforces exactly that one thing, because `src=` and other spellings render **a caption over empty space**: fifteen figures across chapters 3.11–3.14 shipped that way, and it was found by translating 3.15 and noticing the two locales disagreed — the missing edge from `docs/05-sad.md:138` as it is today and as it becomes, and the ordering comparison between the two transports
- [ ] T049 [P] Assemble the Vietnamese twin under `relay-tutorial/app/(vi)/vi/part-3/chapter-18/the-message-that-never-arrived/` **using the `translate-mdx` skill** — it exists for exactly this and its stated concern is *"strictly preserving Markdown and JSX syntax"*, which is the MIRROR rule and T044a's hazard in one sentence. Thirteen analysis passes went by without any task naming a skill this repository ships — **both `page.mdx` and its own `figures.ts`**, as chapter 3.17 carries on both sides. Fences byte-identical to the English (the chain's `MIRROR` rule); figure captions and prose translated, and the same **`code`** prop on every `<Figure>` — the locale mismatch is exactly how M15's fifteen broken figures were found
- [ ] T049a **Add chapter 3.18 to `relay-tutorial/lib/tutorial.ts`.** The registry holds exactly the 34 shipped chapters — 34 `status: "published"`, zero `"planned"` — so **without an entry the chapter does not route, is not among the static pages, and nothing that walks chapters can see it.** Model it on 3.17's at `:575`: `id`, `path`, `title`, `status`, `readerProduces`, `sourceDoc`, `readerMinutes`, `titleVi`, `readerProducesVi`. `sourceDoc` is **`docs/05-sad.md`** for this chapter, where 3.17's was the SRS — which is the same distinction FR-002 and FR-002a draw. The file is fenced by no chapter and has no appendix hunk: edited, not fenced
- [ ] T050 Fence every path in T042's second column, under `relay-tutorial/fences/`, **following `plan.md`'s per-file fencing table** — titled, or `(excerpt)` with a `fences/post-series.md` hunk carrying the byte-exact change. `check-fence-chain.mjs:39` drops any `(excerpt)` title from the chain (`NOT_A_FILE`), which is how `gaps.md` item 7's three files ended up permanently unverified; **and an `(excerpt)` on a file already in the chain fails the replay** unless the appendix carries it, because the comparison is against the end state. **Three lines of context suffice because uniqueness is checked**; the predecessor is a **commit**, not a tag — a feature's tail can amend a platform file after tagging, which cost 3.17 five wrong answers
- [ ] T050a **Amend `docs/05-sad.md`** (spec **FR-002a**): §5.1 gains a REST send sequence, and the ordering bullet at `:254` splits the way FR-005 splits it. The document currently says two different things — `:138`'s component diagram gives the publish to the api, `:248`'s sequence diagram draws `G->>G`, and `:254` states *"The Redis fan-out happens after the ack"* unconditionally. **This chapter's whole justification cites `:138`**, so leaving `:248` contradicting it is the kind of quiet claim the chapter is about
- [ ] T050a2 **Amend ADR-07 in `docs/06-adr-deep-dives.md:401` (spec FR-002a).** Its case against core NATS argues for *"a clean mapping — gateway to Redis, api and workers to NATS"*, and this chapter puts the api on Redis. **Do not touch the Decision or the Revisit-when** — *"Publish once per message to `chan:{channel_id}`"* still holds, because each message has one entrance, and neither revisit trigger fires. Add the exception, and **date it to chapter 3.8**, not here: `limits/store.ts` gave the api its first Redis client and the mapping has been aspirational since. This chapter is the second breach and the first on the hot path
- [ ] T050b Run `pnpm sync:docs`, then confirm `pnpm check:docs` **ran** — not merely that it exited 0. `scripts/check-docs-drift.sh:35` is `if [ ! -d "$PARENT_DOCS" ]; then echo "…skipping drift check" >&2; exit 0; fi`, so **a missing parent `docs/` is a green exit** with the warning on stderr where CI loses it. Assert `$PARENT_DOCS` resolved, or diff `docs/05-sad.md` against `relay-tutorial/content/docs/05-sad.md` by hand. This is `check:errors` reading a stale `dist` one checker over: green for the wrong reason.

    **Where this can actually bite, since the first version of this task implied CI:** it cannot happen in the pipeline — `.github/workflows/ci.yml` checks out the **parent** with `submodules: recursive` in both relevant jobs, so `$PARENT_DOCS` resolves there. The exposure is a standalone `relay-tutorial` clone, or a local run from a tree where the parent is not a parent. That is precisely how this chapter's author will run it. `docs/05-sad.md` is mirrored into `relay-tutorial/content/docs/05-sad.md` and `check-docs-drift.sh` fails on divergence — the amendment is not finished until the mirror matches
- [ ] T050c State in `page.mdx` what FR-002 and FR-002a distinguish: **no SRS clause changed**, principle VI satisfied by citing FR-RTM-01, *and* a SAD amendment because the SAD disagreed with itself. A reader arriving from 3.17 is looking for an amendment, and the honest answer is "not the one you expect"
- [ ] T050d **Amend chapter 3.13's Trap in both locales (FR-018).** `app/(en)/part-3/chapter-13/…/page.mdx:1285` is `<Trap title="A message sent over REST reaches no socket, ever">` and its body states *"Nothing in the api publishes to the gateway's fan-out"*; the Vietnamese twin is at `:1273`. The word **ever** is what makes it a permanent claim rather than a dated finding. Rewrite it as what it was — true until chapter 3.18 — rather than deleting it: a Trap that a later chapter closed is worth more to a reader than a Trap that was quietly removed
- [ ] T050e **Amend Part 3's closing paragraph in both locales (FR-018).** `app/(en)/part-3/chapter-16/…/page.mdx:4469` reads *"a REST-sent message still reaches no socket and FR-RTM-05's chapter owns that decision"*. Two corrections in one sentence: the claim is no longer true, and the clause is **FR-RTM-01** (FR-001) — this is H14's second site, and the reason the rule is *grep the claim everywhere* rather than fix the one you found
- [ ] T051 Check `relay-tutorial/fences/post-series.md` for whether any file this feature touches is appendix-owned before fencing it. An appendix hunk anchored on a file's last line forbids a chapter from appending to it, and a diff generated straight to HEAD performs the appendix's edit itself

## Phase 8: Close-out

- [ ] T052 Re-derive the file count from `git diff --name-only` in both repositories and reconcile it against **the list `pnpm check:fences` prints**, not its count. **The parse, stated because analysis pass 12 followed pass 11's version of this instruction and got it wrong:**

        node scripts/check-fence-chain.mjs --verbose | grep -E "^  [^ ]"

    `--verbose` emits **two lines per file** — the path, then `last fenced at …` — so 212 files is 425 lines of output. Filtering by extension undercounts: an attempt listing `ts mts json mjs` returned **194**, missing `.yaml`, `.md`, `.sql` and `.gitignore`. The pattern above yields exactly 212. **A file fenced as `(excerpt)` and carried by no titled fence is absent from that set**, so a count-to-count comparison cannot see the one failure this step exists to catch (T050). `plan.md`'s column was rebuilt from the task list in analysis pass 4, after the pre-task prediction missed five files and invented two — so this step should now **confirm** rather than discover. If it still finds a file in no bucket, that is the interesting result and belongs in `chapter-notes.md`
- [ ] T052a **Count the prose, do not carry the estimate (SC-011).** T043 estimated 2,650–3,350 from six arguments; SC-011 requires the chapter to be **inside 2,000–4,000**, and an estimate is not a count — the same distinction T016 draws for the publish latency. **There is no word-count instrument in this repository**: `plan.md` records that the figures for 3.15, 3.16 and 3.17 came from a tool that no longer exists and that the pass-1 reconstruction ran 4–6% high against them. So decide the instrument once, write it down in `specs/036-chapter-3-18/baseline.txt`, and **re-count 3.15, 3.16 and 3.17 with the same one** — otherwise 3.18's number is not comparable to the series it belongs to, and the per-argument rate the next chapter inherits is built on two different rulers
- [ ] T053 [P] Assert the static page count **moved** — 91 to 92 — against T002's baseline. Nothing else connects the filesystem to `lib/tutorial.ts`, so this number is the registry's only detector. Then follow **CI's order**, which is the authoritative sequence (`.github/workflows/ci.yml:96–110`): `pnpm lint`, `pnpm typecheck`, `pnpm turbo run test --force`, `pnpm build`, **`node services/api/dist/db/migrate.js`**, `pnpm test:integration`, `pnpm coverage`, then `pnpm test:outsider`. The migration step is in CI with its reason attached — *"the suites expect the schema the migration runner produces, not the one drizzle-kit imagines"* — and this task omitted it for thirteen passes. This feature adds no migration, which is why the omission was harmless and not why it was right. **`--force` because turbo caches the unit lane and typecheck**: analysis pass 13 saw 13 typecheck tasks report success in **32ms, FULL TURBO**. The cache is correctly keyed, so a cached green is trustworthy — it is simply not evidence that anything ran, and this is a verification step. Record in `baseline.txt` which numbers came from execution. (`test:integration` is `cache: false`, so the battery needs no flag), so `check:errors` reads a current `dist` and `session.itest.ts` can spawn the api
- [ ] T054 [P] Run `pnpm check:fences`, `pnpm check:figures`, `pnpm check:errors`, `pnpm check:srs`, `pnpm check:docs`. **Three of these five can be green for the wrong reason, and confirming each RAN is part of the task**: `check:errors` reads `packages/protocol/dist/codes.js`, so build first; `check:docs` exits 0 when the parent `docs/` is absent (`check-docs-drift.sh:35`); and `check:srs` does the same at `check-srs-ids.sh:40` — verified by running it from a scratch directory, where it prints *"not found — skipping (standalone clone?)"* and exits 0. Pass 10 fixed one of those two and missed the sibling eight lines away in a script this feature already touches
- [ ] T055 Coverage against `relay-platform/vitest.coverage.config.mts`: confirm T011's pin still holds and that no touched file's pin regressed. The ratchet has **removed** code three times rather than covered it
- [ ] T056 Run `pnpm test:integration` 20+ times with nothing else on the machine. 589 tests at 3.17's close, mean 193.55 s, stdev 0.99, 240 s budget — and the lane costs per **suite**, not per test, so an added api boot moves the mean more than added assertions do. **Twenty green rejects a per-run failure rate above 13.91% and nothing finer**; 3.17's one failure in twenty-six is `gaps.md` item 1, still unidentified.

    **Assert the mean against 240 s rather than reporting it.** The budget is enforced by nothing today — analysis pass 14 found no `timeout-minutes` in `.github/workflows/ci.yml` and no lane timeout in any vitest config, only per-test `testTimeout: 60_000`. So a lane at 300 s ships green, and **this feature adds the one thing that moves the mean**: a new api-boot suite, on a lane that is `--concurrency=1` and costs per suite. Compute the mean over the battery, compare it to 240, and fail the task if it is over — a comparison someone reads is not a gate
- [ ] T056a **Sweep the published corpus for claims this chapter retires**, both locales, and record the phrase list and every hit in `specs/036-chapter-3-18/chapter-notes.md`. Pass 9 found every FR-018 site with eight `grep -rln` calls over `app/(*)/**/page.mdx` — *"reaches no socket"*, *"no live socket"*, *"does not reach"*, *"never arrives"*, *"cannot succeed"*, *"the gateway publishes"*, *"instance that handled"*, *"only publisher"* — **plus the architectural phrasings, because scope and vocabulary have to widen together**: *"clean mapping"*, *"gateway to Redis"*, *"publish once per message"*, *"two broker clients"*. Pass 10 pointed this sweep at `docs/` and left its word list derived from chapter narrative; all eight original phrases score **zero** in `06-adr-deep-dives.md`, where the two that matter are the two that were missing. **Sweep the parent's `docs/` as well as the chapters** — that is where this feature's two worst prose defects were: `docs/05-sad.md:254` stated the ordering unconditionally for three analysis passes (FR-002a) and `docs/07-tutorial-plan.md:167` misattributed the clause for nine (T061). The sweep was scoped to `page.mdx` because that is where pass 9 was looking, which is the same narrowing it exists to catch. **No checker reads prose** (`gaps.md` item 8), and this is the five-minute mechanical check that stands in for one. Classify every hit: a present-tense claim is a defect, an attributed record — *"Chapter 3.12 recorded that…"* — is not
- [ ] T057 **SC-010**: the sealed outsider in `relay-platform/packages/outsider/` sends over REST, waits on a socket, and succeeds — following its README, not the source
- [ ] T058 **Use a person**, and record what they hit in `specs/036-chapter-3-18/chapter-notes.md`. Chapters 3.14, 3.15, 3.16 and 3.17 each named this gap and none closed it. Every check in this repository compares bytes; the sealed outsider was wrong about the API for two chapters because nobody ran it, and a published Trap contradicting 3.17's own chapter survived fifteen analysis passes because no checker reads prose
- [ ] T058a **Build `specs/036-chapter-3-18/traceability.md` both ways** (**SC-009**). 3.17's is 77 lines and bidirectional on purpose: *"a map that only runs requirement→test cannot catch a test that verifies nothing, and a map that only runs test→requirement cannot catch a requirement nobody built."* It has been wrong before — *"chapter 3.12's map recorded FR-CHN-05 delivered when two of its three verbs were built, and chapters 3.15 and 3.16 corrected it twice."* This chapter's map opens on the governing documents as amended: **FR-RTM-01** the unmet clause now met, **FR-RTM-05** one of six kinds met and five recorded as unbuilt, **FR-RTM-10** whatever T031–T034 found, and the `docs/05-sad.md` amendment with no SRS change beside it
- [ ] T059 **SC-009, FR-015**: close chapter 3.12's `gaps.md` G1 rather than amending it again, and cite **FR-RTM-01** in `specs/036-chapter-3-18/traceability.md`
- [ ] T060 **FR-016**: re-examine chapter 3.14's Phase 2 verdict and record what is now true of it in `specs/036-chapter-3-18/chapter-notes.md`
- [ ] T061 Write `specs/036-chapter-3-18/chapter-notes.md` — the plan against what shipped, including the phases that went badly — and `specs/036-chapter-3-18/gaps.md` with an owner per item. **Correct `docs/07-tutorial-plan.md`'s 3.18 row, not just its status.** It reads *"FR-RTM-05's message half"* and the unmet clause is **FR-RTM-01** (FR-001) — FR-RTM-05 is about which event kinds exist. Flipping planned to shipped while leaving the citation makes the series' own plan disagree with the chapter it commissioned. While there, look at 3.19's row: it cites FR-RTM-05 alongside the correct FR-RTM-06 and FR-RTM-07, so it is less wrong rather than right
- [ ] T062 Confirm **FR-017** against `docs/07-tutorial-plan.md`

### The three-repository close-out

`relay-platform` and `relay-tutorial` are **git submodules**; `docs/` and `specs/` are the parent's.
One logical chapter is three commits plus a gitlink bump, and 3.17 was *"tagged `part3-ch17` in all
three repositories"*. None of that was in this list until analysis pass 10.

- [ ] T063 Commit in each repository that changed — `relay-platform`, `relay-tutorial`, and the parent for `docs/` and `specs/` — then **bump the parent's submodule pointers** so the parent's recorded state includes the chapter. Without the bump, `check-docs-drift.sh`'s cross-repo comparison and every fence replay describe a tree nobody has
- [ ] T064 **Tag `part3-ch18` LAST**, after the platform, the tutorial, the fences and every gate — in all three repositories. CLAUDE.md's fence lesson 2 exists because a feature's tail amended a platform file *after* tagging, which cost 3.17 five wrong answers and is the entire reason this feature has T001a. Tagging before the tail is what creates that
- [ ] T065 If anything is amended after T064 — and 3.17's experience says something will be — **record the amending commit in `specs/036-chapter-3-18/chapter-notes.md` under a heading 3.19 will find.** The next chapter's fence predecessor is then a fact it reads rather than an excavation it repeats
- [ ] T066 Push all three repositories and their tags, and verify the parent's gitlinks point at the pushed submodule commits rather than at local-only ones: presence is untouched, and chapter 3.19 still owns FR-RTM-06 and FR-RTM-07

---

## Dependencies

    Phase 1  ──▶  Phase 2  ──▶  Phase 3 (US1, MVP)  ──▶  Phase 4 (US2)
                                       │
                                       ├──▶  Phase 5 (US3)   independent of US2
                                       └──▶  Phase 6         independent of US2, US3
    Phases 3–6  ──▶  Phase 7 (chapter)  ──▶  Phase 8 (close-out)

**T014 before T021, T022, T032, T033, T035.** Five delivery tests need a fan-out in
`session.itest.ts`'s harness, and today it has none.

**T011's number comes from the requirement, not from T009's first coverage report** — this is a reasoning constraint, not an ordering one, and the earlier wording (*"T011 before T009 is finished"*) read as an ordering claim that contradicts document order. You cannot pin a file that does not exist; the sequence is T009, T010, T011. The pin is chosen deliberately, not ratcheted to whatever the
first implementation happened to cover.

**T013 before T024.** The guard test comes before the publish is written, because the publish is
where the double-delivery would be introduced.

**T031 before T033.** Establish where membership is actually checked before asserting anything
about the window.

**T038 immediately after T037.** A failure-path test that has not been shown to fail is not yet
evidence.

**T006 before T007.** The grammar's new test exists before the old assertion is removed, so the
property is never untested.

**T009a before T039.** Measuring a dead Redis without the down-window measures the version that
`limits/store.ts` already rejected, so the number would describe a design nobody chose.

**T049a before T050b.** `pnpm sync:docs` and `check:docs` are about `docs/`; the registry entry is
what makes the chapter exist as a page, and a chapter that does not route cannot be checked.

**T001a before T050.** The predecessor commit is named once, in the baseline, and read from there.

**T000 before everything.** The four records exist before any phase writes into them.

**T047a before T049.** Edit the English, then translate — not translate, then edit both.

**T063 before T064, T064 before T066.** Commit, bump, then tag, then push — the order is the
finding, not a formality.

**T025a and T050d/T050e are the same requirement in two places.** FR-018 covers fenced-file
comments and chapter prose alike; they are separate tasks because they land in different phases,
not because they are different work.

**T026a after T024.** T013 cannot be evidence until the thing it guards against exists to be
mis-sited.

**T036a is the isolation clause and is sequential to T036** — they share `fanout.itest.ts`.

**T058a before T059.** The map is built, then FR-RTM-01's citation is checked against it.

**T050b immediately after T050a.** A SAD edit that is not synced leaves `check:docs` red, and
`check:docs` reads drift rather than validity — it will not tell you which of the two files is
right.

## Parallel opportunities

- Phase 2: T006 and T010 alongside their neighbours (different files)
- Phase 3: **T017 and T021 only.** T018, T019, T020 and T036 all write
  `services/api/src/fanout/fanout.itest.ts`, and T035 shares `session.itest.ts` with T021 — they
  are independent *cases* in a shared file, which makes them sequential. `[P]` means different
  files, and a mechanical check in analysis pass 5 found five tasks claiming one
- Phase 5: T032 alongside T031 (different files); T035 and T036 wait on their files' other writers
- Phase 7: T048 and T049 alongside T044
- Phase 8: T053 and T054 together, then T056 alone — **nothing else runs on the machine during a
  timing battery** (3.12's attempt one failed at run 11 to two dev servers, with no port held and
  no `EADDRINUSE`)

## Independent test criteria

| story | passes when |
|---|---|
| US1 | the published payload satisfies `messageSchema` on the right subject, and a real REST send reaches a real socket in `session.itest.ts` and in the outsider lane |
| US2 | two gateway instances — the member's socket receives, the other does not — plus T030's recorded composition |
| US3 | a removed member receives nothing within FR-RTM-10's five seconds, on **both** paths, or the gap is recorded rather than narrowed |

## Implementation strategy

**MVP is Phase 3** — US1 alone closes chapter 3.14's verdict and `gaps.md` item 3, and T022 proves
it end-to-end in the integration lane rather than only in the sealed one.

**Phase 6 is where this feature is most likely to lie to itself.** Its central mechanism resolves
successfully when it fails, so every test there names what would have to be false for it to fail,
and T038 makes the suite prove it can tell.
