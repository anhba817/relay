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

- [ ] T001 Pin the lane environment in `specs/036-chapter-3-18/baseline.txt`: the four variables and the compose profile from `specs/035-chapter-3-17/baseline.txt`, re-verified rather than copied, plus the ports this feature needs (Postgres 15432, Redis 16379 — this machine's own Postgres holds 5432)
- [ ] T002 [P] Record the starting state in `specs/036-chapter-3-18/baseline.txt` — integration test count, lane mean, coverage pins for every file this feature touches, `pnpm check:fences` file count — measured, not carried over from 3.17's close
- [ ] T003 [P] Confirm the failing state that justifies the chapter: add the scenario to `relay-platform/packages/outsider/src/integrate.itest.ts` — send over REST, wait on a socket — and watch it **time out**. Record the failure mode in `baseline.txt`. A scenario that passes now is testing something else (3.17's T047c)

## Phase 2: Foundational (blocking — every story depends on these)

### The grammar move

- [ ] T004 Create `relay-platform/packages/protocol/src/fanout.ts` with `subjectFor(channelId)` **only**, moved verbatim from `services/gateway/src/fanout.ts` including the comment explaining one subject per channel. **`DEFAULT_REDIS_URL` does not move** — it is declared in `api/src/limits/store.ts:44`, `gateway/src/fanout.ts:27` and `gateway/src/limits.ts:22`, and consolidating one of three copies leaves a shared definition plus two locals. A connection URL is configuration, not protocol
- [ ] T005 Export `subjectFor` from `relay-platform/packages/protocol/src/index.ts`
- [ ] T006 [P] Unit-test the grammar in `relay-platform/packages/protocol/src/fanout.test.ts` — `subjectFor(id) === \`chan:${id}\``. It is a pure string assertion and belongs beside the definition, not in an integration suite that needs Redis
- [ ] T007 Delete `subjectFor` from `relay-platform/services/gateway/src/fanout.ts` and import it from `@relay/protocol`. **No re-export** — one name for one thing, so consumers take it from the package. `fanout.itest.ts:8` imports `createFanout, subjectFor, type Fanout` on one line; that line splits in two. Move the grammar assertion at `fanout.itest.ts:150` to T006 rather than leaving it testing a moved function from an integration lane
- [ ] T008 Run `pnpm build` before believing any checker: `check:errors` reads `packages/protocol/dist/codes.js`, the built artifact, and a stale `dist` makes it green for the wrong reason. `session.itest.ts:113` also refuses to run without `services/api/dist/main.js`

### The publisher

- [ ] T009 Create `relay-platform/services/api/src/fanout/publisher.ts` — a `MessagePublisher` with `publish(message)` and `close()` only, one ioredis client, per `contracts/fanout-publisher.md`. Client options come from `services/api/src/limits/store.ts` (`lazyConnect`, `maxRetriesPerRequest: 0`, `connectTimeout: 1_000`, and an `error` listener), **not** from `createFanout`, which has neither (R10). It reads `RELAY_REDIS_URL` the way `limits/store.ts:86` already does, so this feature adds no configuration. Carry the reason in a comment
- [ ] T010 [P] Unit-test the publisher in `relay-platform/services/api/src/fanout/publisher.test.ts`: the subject is `chan:{id}`, the payload parses against `messageSchema`, and `publish` **resolves** when the client throws
- [ ] T011 **Set an explicit coverage pin** for `services/api/src/fanout/publisher.ts` in `relay-platform/vitest.coverage.config.mts`, and prove it bites by deleting T010's throwing-client case and watching it go red. **Unlisted files fall under the global `70`** — a ten-line publisher clears that with its `catch` untested, which is exactly the path FR-010 and FR-011 depend on. A pin added after the fact ratchets to whatever happened; this one is chosen
- [ ] T012 Wire the publisher into `relay-platform/services/api/src/messages/messages.module.ts`, following `services/api/src/limits/limits.module.ts:36`'s pattern — `{ provide: …, useFactory: … }`, the way the api already provides its Redis-backed counter store
- [ ] T013 Write the FR-006 guard test in `relay-platform/services/api/src/fanout/fanout.itest.ts` **before** T012's wiring is trusted: a send through the **internal** route publishes **nothing**, asserted by count on a Redis subscriber over a window (SC-003). What would have to be false for this to fail? That the api publishes for the internal route. This is the test that catches a publish placed in `messages.service.ts`

### The delivery harness

- [ ] T014 Wire a fan-out into `relay-platform/services/gateway/src/session.itest.ts`'s harness. `:224` calls `attachSessions({ server, api, logger })` with no `fanout` key, and `session.ts:125` declares `fanout?: Fanout` — so today `fanout?.publish` is a no-op and **nothing in that suite subscribes to any subject**. Every delivery test below needs this. **Add it as a new capability, do not change what the existing fixture is**: promoting or repurposing a shared gateway fixture took five tests down in 3.17's T040b, the fifth such incident in two features. Run the whole gateway suite after, not just the new test

## Phase 3: User Story 1 — a REST send reaches a connected member (P1) 🎯 MVP

**Goal**: `POST /v1/channels/:channelId/messages` reaches an already-open socket.
**Independent test**: T022, and T003's outsider scenario now passing.

### The ordering, now settled in the spec

- [ ] T015 [US1] Verify the amended **FR-005** holds as written before the publish goes in: the clause now splits by transport — socket is commit/ack/publish, REST is commit/publish/respond — because the response *is* the acknowledgement and a handler cannot publish after it without detaching. Confirm the amendment is in `spec.md`, and carry its recorded cost into the chapter: **NFR-PRF-01's clock is not measurable on the REST path** because the interval can be negative
- [ ] T016 [US1] Measure `PUBLISH` p50/p95 from the api against a live Redis and put it in `specs/036-chapter-3-18/baseline.txt`. The publish now lands inside NFR-PRF-02's budget (p95 < 150 ms for the whole write); `contracts/fanout-publisher.md` asserts sub-millisecond, and an assertion is not a measurement

### Tests for User Story 1 — publisher level

- [ ] T017 [P] [US1] **FR-004**, the feature's core clause, in `relay-platform/services/api/src/fanout/fanout.itest.ts`: a REST send publishes to `chan:{channelId}` after the write commits. Assert on a real Redis subscriber, so the test names the subject rather than trusting delivery
- [ ] T018 [P] [US1] **Assert the published payload against `messageSchema` itself**, in `relay-platform/services/api/src/fanout/fanout.itest.ts` — not against a list of mistakes. One `safeParse` covers a seventh key, `channel_id` in place of `channel`, a missing `user`, a non-positive `seq`, a null `text`, and a `created_at` that is not RFC 3339. `fanout.itest.ts:128` proves an invalid **value** is dropped and nothing proves an extra **key** is; the schema is the class definition, and a checker that fails on an unknown member beats one that enumerates the known ones
- [ ] T019 [P] [US1] **FR-009, SC-008** in `relay-platform/services/api/src/fanout/fanout.itest.ts`: the payload the api publishes is indistinguishable from what a socket send publishes, compared **field by field** with only `id`, `seq` and `created_at` controlled. **Do not use `withoutRequestId`** — the oracle deletes `request_id` from an error body so two envelopes can be compared whole, and a fan-out payload has no such field, so it would be an identity function dressed as rigour. This is frame equality, not tenant isolation. Build the two payloads from independent sources: **a shared helper moves both halves of a pair and the comparison then sees nothing** (3.17's T044)
- [ ] T020 [P] [US1] A send to a channel with no connected member publishes and the send still returns `201`, in `relay-platform/services/api/src/fanout/fanout.itest.ts` (spec edge case 2 — a frame nobody hears is correct, not a loss)

### Tests for User Story 1 — delivery level

- [ ] T021 [P] [US1] The same user on two connections receives the frame on **both**, in `relay-platform/services/gateway/src/session.itest.ts` (needs T014). What is under test is the registry's fan-out to local sockets, so the publisher's identity is irrelevant — publish to `chan:{id}` directly (spec edge case 5)

### Test for User Story 1 — end-to-end

- [ ] T022 [US1] **SC-001** in `relay-platform/services/gateway/src/session.itest.ts` (needs T014): a real REST send against the spawned api reaches a real socket on the gateway. This is the whole feature in one assertion, and the harness that makes it possible already existed
- [ ] T023 [US1] The same scenario in `relay-platform/packages/outsider/src/integrate.itest.ts` — T003's, now green. The outsider adds what the integration lane cannot: it follows the README rather than the source, and it is sealed against workspace imports

### Implementation for User Story 1

- [ ] T024 [US1] Add the publish to `relay-platform/services/api/src/messages/messages.controller.ts`, immediately before the `return` that assembles the response. Six fields: `channel: message.channel_id` (**renamed** — the frame's field is `channel`), `user: actingExternalId`, and `id`/`seq`/`text`/`created_at` from `message`
- [ ] T025 [US1] Guard it in `relay-platform/services/api/src/messages/messages.controller.ts` with the two conditions mirrored from `session.ts:651` — `!message.duplicate` (**FR-007**) and `message.text !== null`. Carry the gateway's reasons across, and **record the second reason `session.ts` does not give**: `messageSchema.text` is `z.string()`, non-nullable, so a tombstone cannot be published at all — it would be dropped as `fanout.invalid_payload`. The guard has two independent justifications and only one is written down today
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
- [ ] T035 [P] [US3] **FR-014, SC-007** in `relay-platform/services/gateway/src/session.itest.ts` (needs T014): a private channel's message reaches no non-member's socket. **This is a fourth door onto FR-CHN-05** and gets its own test rather than an inference from the read paths' three
- [ ] T036 [P] [US3] In `relay-platform/services/api/src/fanout/fanout.itest.ts` — a banned sender, an archived channel, an exhausted quota, and an application key naming a person: each refused, each publishing nothing (SC-004). Four refusals, and each assertion states what would have to be false for it to fail

## Phase 6: Failure, and the tests that must not pass for the wrong reason

- [ ] T037 **FR-010 and SC-005** in `relay-platform/services/api/src/fanout/fanout.itest.ts` — with the publisher pointed at a dead port, a REST send returns `201` and the message is recoverable through the api's own history route. **This is the constitution's gate**: principle IV's *"Any new delivery mechanism MUST preserve this recovery property"*. No socket is needed; resume reads Postgres. Use `limits.itest.ts:510`'s established pattern — `"redis://127.0.0.1:1"` — rather than stopping the server: in-process, deterministic, and already in the repository
- [ ] T038 **Prove T037 can distinguish anything**, in `relay-platform/services/api/src/fanout/fanout.itest.ts`. `publish` swallows its own errors and resolves (R8), so "the send returned 201 while Redis was down" is equally true of a publisher that does nothing. Delete the publish call, run T037, and watch it stay green. Then make the assertion the **`fanout.publish_failed` log line** (**FR-011**), and re-run the deletion to watch it go red. Record both runs in `baseline.txt`
- [ ] T039 Measure the REST send's p95 against a dead port into `specs/036-chapter-3-18/baseline.txt` (R10's hazard). `limits/store.ts` learned this the hard way: *"an outage that instead adds seconds to every request has refused it in a slower way, and NFR-PRF-02 asks for a p95 under 150 ms"*. Measure the same path with `createFanout`'s default options for the contrast — that number is what justifies not copying the gateway's client
- [ ] T040 Measure a **connected but slow** Redis into `specs/036-chapter-3-18/baseline.txt` — the residual risk `plan.md`'s post-design re-check named and the contracts did not close. `maxRetriesPerRequest: 0` and `connectTimeout` bound a dead server; neither bounds a slow one, and ioredis has no command timeout unless one is set. If a hung Redis holds every send open, add `commandTimeout` to `services/api/src/fanout/publisher.ts` and say so
- [ ] T041 [P] Verify R10's gateway claim rather than repeating it: point the gateway's fan-out at a dead port, send on a socket, watch the process. `relay-platform/services/gateway/src/fanout.ts` attaches no `error` listener to either client and no test anywhere covers a dead fan-out. **If the process dies, that is pre-existing and this chapter surfaced it** — record it in `specs/036-chapter-3-18/gaps.md`, and decide deliberately whether fixing it belongs here

## Phase 7: The chapter

- [ ] T042 Decide the two file counts in `specs/036-chapter-3-18/chapter-notes.md` and keep them in separate columns from here to close-out: **what the chapter teaches** drives the word estimate, **what it must fence** drives the chain. `plan.md` predicts nine and thirteen. Neither number is ever asked to do the other's job
- [ ] T043 Estimate the prose in `specs/036-chapter-3-18/chapter-notes.md` from the number of **arguments**, not from a per-file rate. 3.15 and 3.16 agreed on ~154 words per taught file and 3.17 came in at 84.7 — 45% below. `plan.md` names five arguments and estimates 2,200–2,800 words against the series' 2,000–4,000 bound (SC-011)
- [ ] T044 Write `relay-tutorial/app/(en)/part-3/chapter-18/the-message-that-never-arrived/page.mdx`. The chapter's five arguments: the ordering that cannot be copied to REST, the two NFRs pulling opposite ways, why the grammar moved and the client did not, the recovery property under a lost publish, and what T031–T034 found about membership
- [ ] T045 State **FR-002** in `page.mdx`: there is **no SRS amendment**, principle VI is satisfied by citation, and the unmet clause is **FR-RTM-01** — not FR-RTM-05, which `docs/07-tutorial-plan.md`'s row names (**FR-001**). A reader arriving from 3.17, where the amendment *was* the gate, will look for one. Note that FR-005 *was* amended, in this feature's own spec, and say why that is a different kind of amendment
- [ ] T046 State **FR-003** in `page.mdx`: FR-RTM-05 names six event kinds and this chapter delivers one, because one is all that has a producer. `message.updated` and `membership.changed` have none outside tests, and nothing writes `messages.edited_at` or `messages.deleted_at`
- [ ] T047 State **FR-012** in `page.mdx`: what a client may conclude from having received nothing. A missing frame is not evidence a message does not exist — resume is the guarantee, the fan-out is the optimisation
- [ ] T048 [P] Write `relay-tutorial/app/(en)/part-3/chapter-18/the-message-that-never-arrived/figures.ts` — the missing edge from `docs/05-sad.md:138` as it is today and as it becomes, and the ordering comparison between the two transports
- [ ] T049 [P] Assemble the Vietnamese twin under `relay-tutorial/app/(vi)/part-3/chapter-18/`, fences byte-identical to the English (the chain's `MIRROR` rule)
- [ ] T050 Fence every path in T042's second column, under `relay-tutorial/fences/`. **Three lines of context suffice because uniqueness is checked**; the predecessor is a **commit**, not a tag — a feature's tail can amend a platform file after tagging, which cost 3.17 five wrong answers
- [ ] T051 Check `relay-tutorial/fences/post-series.md` for whether any file this feature touches is appendix-owned before fencing it. An appendix hunk anchored on a file's last line forbids a chapter from appending to it, and a diff generated straight to HEAD performs the appendix's edit itself

## Phase 8: Close-out

- [ ] T052 Re-derive the file count from `git diff --name-only` in both repositories and reconcile it against `pnpm check:fences`. T042's thirteen is a first count and is **expected to be wrong**; this comparison found two files in no bucket in 3.16
- [ ] T053 [P] Run `pnpm turbo run test`, `pnpm test:integration`, `pnpm test:outsider`, `pnpm coverage` — and `pnpm build` first, so `check:errors` reads a current `dist` and `session.itest.ts` can spawn the api
- [ ] T054 [P] Run `pnpm check:fences`, `pnpm check:figures`, `pnpm check:errors`, `pnpm check:srs`, `pnpm check:docs`
- [ ] T055 Coverage against `relay-platform/vitest.coverage.config.mts`: confirm T011's pin still holds and that no touched file's pin regressed. The ratchet has **removed** code three times rather than covered it
- [ ] T056 Run `pnpm test:integration` 20+ times with nothing else on the machine. 589 tests at 3.17's close, mean 193.55 s, stdev 0.99, 240 s budget — and the lane costs per **suite**, not per test, so an added api boot moves the mean more than added assertions do. **Twenty green rejects a per-run failure rate above 13.91% and nothing finer**; 3.17's one failure in twenty-six is `gaps.md` item 1, still unidentified
- [ ] T057 **SC-010**: the sealed outsider in `relay-platform/packages/outsider/` sends over REST, waits on a socket, and succeeds — following its README, not the source
- [ ] T058 **Use a person**, and record what they hit in `specs/036-chapter-3-18/chapter-notes.md`. Chapters 3.14, 3.15, 3.16 and 3.17 each named this gap and none closed it. Every check in this repository compares bytes; the sealed outsider was wrong about the API for two chapters because nobody ran it, and a published Trap contradicting 3.17's own chapter survived fifteen analysis passes because no checker reads prose
- [ ] T059 **SC-009, FR-015**: close chapter 3.12's `gaps.md` G1 rather than amending it again, and cite **FR-RTM-01** in `specs/036-chapter-3-18/traceability.md`
- [ ] T060 **FR-016**: re-examine chapter 3.14's Phase 2 verdict and record what is now true of it in `specs/036-chapter-3-18/chapter-notes.md`
- [ ] T061 Write `specs/036-chapter-3-18/chapter-notes.md` — the plan against what shipped, including the phases that went badly — and `specs/036-chapter-3-18/gaps.md` with an owner per item. Update `docs/07-tutorial-plan.md`'s row from planned to shipped
- [ ] T062 Confirm **FR-017** against `docs/07-tutorial-plan.md`: presence is untouched, and chapter 3.19 still owns FR-RTM-06 and FR-RTM-07

---

## Dependencies

    Phase 1  ──▶  Phase 2  ──▶  Phase 3 (US1, MVP)  ──▶  Phase 4 (US2)
                                       │
                                       ├──▶  Phase 5 (US3)   independent of US2
                                       └──▶  Phase 6         independent of US2, US3
    Phases 3–6  ──▶  Phase 7 (chapter)  ──▶  Phase 8 (close-out)

**T014 before T021, T022, T032, T033, T035.** Five delivery tests need a fan-out in
`session.itest.ts`'s harness, and today it has none.

**T011 before T009 is finished.** The pin is chosen deliberately, not ratcheted to whatever the
first implementation happened to cover.

**T013 before T024.** The guard test comes before the publish is written, because the publish is
where the double-delivery would be introduced.

**T031 before T033.** Establish where membership is actually checked before asserting anything
about the window.

**T038 immediately after T037.** A failure-path test that has not been shown to fail is not yet
evidence.

**T006 before T007.** The grammar's new test exists before the old assertion is removed, so the
property is never untested.

## Parallel opportunities

- Phase 2: T006 and T010 alongside their neighbours (different files)
- Phase 3: T017–T021 are five independent cases across two files
- Phase 5: T035 and T036 alongside T031–T034
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
