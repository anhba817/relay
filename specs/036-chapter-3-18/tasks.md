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
**Those are the six fields the fan-out payload needs**, all in scope, plus `message.duplicate`
on the returned `MessageRow`. The publish goes immediately before that `return`.

**It does not go in `messages.service.ts`.** Two callers reach `send()`:
`messages.controller.ts:144` (public REST) and `internal.controller.ts:65` (the gateway's own
send path). A publish in the service would publish for the socket path too — where the gateway
already publishes — and deliver **every socket-sent message twice**. That is FR-006, and T009 is
the test that would have caught it.

---

## Phase 1: Setup

- [ ] T001 Pin the lane environment in `specs/036-chapter-3-18/baseline.txt`: the four variables and the compose profile from `specs/035-chapter-3-17/baseline.txt`, re-verified rather than copied, plus the Redis port this feature needs (Postgres 15432, Redis 16379 — this machine's own Postgres holds 5432)
- [ ] T002 [P] Record the starting state in `baseline.txt` — integration test count, lane mean, coverage pins for every file this feature touches, `pnpm check:fences` file count — measured, not carried over from 3.17's close
- [ ] T003 [P] Confirm the failing state that justifies the chapter: write the outsider scenario from `quickstart.md` §1 and watch it **time out** before anything is built. Record the failure mode in `baseline.txt`. A scenario that passes now is testing something else (3.17's T047c)

## Phase 2: Foundational (blocking — every story depends on these)

### The grammar move

- [ ] T004 Create `relay-platform/packages/protocol/src/fanout.ts` with `subjectFor(channelId)` and `DEFAULT_REDIS_URL`, moved **verbatim** from `services/gateway/src/fanout.ts` including the comment explaining one subject per channel
- [ ] T005 Re-export both from `relay-platform/packages/protocol/src/index.ts`
- [ ] T006 Change `services/gateway/src/fanout.ts` to import `subjectFor` and `DEFAULT_REDIS_URL` from `@relay/protocol` and delete its local definitions. **If any gateway test changes more than an import line, the move was not a move** — stop and find out why
- [ ] T007 Run `pnpm build` before believing any checker: `check:errors` reads `packages/protocol/dist/codes.js`, the built artifact, and a stale `dist` makes it green for the wrong reason

### The publisher

- [ ] T008 Create `relay-platform/services/api/src/fanout/publisher.ts` — a `MessagePublisher` with `publish(message)` and `close()` only, one ioredis client, per `contracts/fanout-publisher.md`. Client options come from `services/api/src/limits/store.ts` (`lazyConnect`, `maxRetriesPerRequest: 0`, `connectTimeout: 1_000`, and an `error` listener), **not** from `createFanout`, which has neither (R10). Carry the reason in a comment
- [ ] T009 Write the FR-006 guard test **before** the wiring: a socket-originated send delivers **exactly one** frame, asserted by count over a window, not by observing one arrival (SC-003). What would have to be false for this to fail? That the api publishes for the internal route. This test is the one that catches a publish placed in `messages.service.ts`
- [ ] T010 Wire the publisher into `services/api/src/messages/messages.module.ts` and whatever provides configuration, so `messages.controller.ts` can inject it
- [ ] T011 [P] Unit-test the publisher in `services/api/src/fanout/publisher.test.ts`: the subject is `chan:{id}`, the JSON is exactly six fields, and `publish` **resolves** when the client throws

## Phase 3: User Story 1 — a REST send reaches a connected member (P1) 🎯 MVP

**Goal**: `POST /v1/channels/:channelId/messages` reaches an already-open socket.
**Independent test**: T003's scenario, now passing.

### The ordering decision this story cannot avoid

- [ ] T012 [US1] **Resolve FR-005 against the transport before writing the publish.** The clause says *"The publish MUST happen after the acknowledgement, not before"*, and on REST the response **is** the acknowledgement — the publish site is one line above `return`, so it necessarily precedes it. `contracts/fanout-publisher.md` chose to publish before the response and argued the guarantee the clause protects (*"never before durability"*) still holds. **Decide, and amend the losing document rather than leaving both.** Either FR-005's wording narrows to the socket path and names what REST does instead, or the publish detaches from the request and FR-011's failure stops being synchronously observable. Record the decision and its cost in `spec.md` and in the chapter
- [ ] T013 [US1] Measure before deciding T012 on latency grounds: `PUBLISH` p50/p95 against a live Redis, from the api. NFR-PRF-02's budget is p95 < 150 ms for the whole write. Put the number in `baseline.txt`; the contract asserts sub-millisecond and an assertion is not a measurement

### Tests for User Story 1

- [ ] T014 [P] [US1] Integration test in `services/api/src/messages/messages.itest.ts` (or a new `fanout.itest.ts` under the api): a REST send publishes to `chan:{channelId}` — assert on a Redis subscriber, so the test names the subject rather than trusting delivery
- [ ] T015 [P] [US1] Cross-service test in `relay-platform/services/gateway/src/rest-delivery.itest.ts` (new): a socket open on a gateway, a REST send through the api, a `message.created` frame arrives. SC-001, and the story's own test
- [ ] T016 [P] [US1] The same user on two connections receives it on **both**, in `relay-platform/services/gateway/src/rest-delivery.itest.ts` (spec edge case 5)
- [ ] T017 [P] [US1] A send to a channel with no connected member publishes and drops, and the send still returns `201` — in `relay-platform/services/api/src/fanout/fanout.itest.ts` (spec edge case 2: a frame nobody hears is correct, not a loss)
- [ ] T018 [P] [US1] Byte-compatibility (FR-009, SC-008): a REST-originated frame and a socket-originated frame are indistinguishable. Use `withoutRequestId` from `isolation/compare.ts`, the oracle 3.15 built. **A shared helper moves both halves of a pair and the oracle then sees nothing** (3.17's T044) — build the two frames from independent sources
- [ ] T019 [P] [US1] The extra-key case `data-model.md` found untested: `messageSchema` is a `z.strictObject`, `fanout.itest.ts:128` proves an invalid **value** is dropped, and nothing proves a seventh key is. Add it — `channel_id` alongside `channel`, or `environment_id`, are the two mistakes this publish site is most likely to make, and both would deliver **nothing** while the send returned `201`

### Implementation for User Story 1

- [ ] T020 [US1] Add the publish to `services/api/src/messages/messages.controller.ts`, immediately before the `return` that assembles the response. Six fields: `channel: message.channel_id` (**renamed** — the frame's field is `channel`), `user: actingExternalId`, and `id`/`seq`/`text`/`created_at` from `message`
- [ ] T021 [US1] Guard it with the two conditions mirrored from `session.ts:651` — `!message.duplicate` (FR-007) and `message.text !== null`. Carry the gateway's reasons across: a retry is storage-safe, not delivery-safe; a tombstone recovered by an old key is not a creation
- [ ] T022 [US1] Verify FR-008 by construction rather than by a flag: `send()` throws on a refusal, so a publish on the success path never runs for one. **Do not use `finally`** — a `finally` publishes after a `403`

## Phase 4: User Story 2 — sender and recipient on different instances (P1)

**Goal**: the api that accepted the send has no relationship with the gateway holding the socket.
**Independent test**: two gateway processes, a member connected to each, one REST send, both receive it.

- [ ] T023 [P] [US2] Reuse the fixture shape from `services/gateway/src/fanout.itest.ts:89` — *"delivers a message published on one instance to a subscriber on another"* — which already proves FR-RTM-02 at the fan-out layer (R7). The new test changes the **publisher**, not the fixture. SC-002
- [ ] T024 [US2] Assert the negative half too: an instance with no member of the channel receives nothing (`fanout.itest.ts:102` is the socket-path precedent). The subject is the filter, and this is the test that says so for a REST send
- [ ] T025 [US2] Check the blast radius of `relay-platform/services/gateway/src/fanout.itest.ts`'s shared fixture before changing it. **Promoting or repurposing a shared gateway fixture took five tests down in 3.17's T040b**, the fifth such incident in two features. If a shared fixture needs a new capability, add one (3.17 used `disposable()`) rather than changing what the existing one is

## Phase 5: User Story 3 — no delivery to somebody who may no longer see it (P2)

**Goal**: FR-013's clause, and the plan's largest open risk.
**Independent test**: remove a member over the public route, send, assert nothing arrives within the clause's window.

- [ ] T026 [US3] **Establish where membership is checked for a REST-originated frame before writing an assertion about it.** R5's measurement: delivery filters by *subscription*, via `registry.subscribersOf(channelId)` at `session.ts:175`; the channel list is a snapshot from `POST /internal/session` at connect time; nothing in the delivery path re-reads membership. Write down what is actually true
- [ ] T027 [US3] Test it on the **socket** path first, which this chapter did not create — in `relay-platform/services/gateway/src/session.itest.ts`: remove a member while their socket is open, send over a socket, see whether a frame arrives. If the socket path already fails FR-RTM-10, this chapter did not cause it and must not claim to have fixed it
- [ ] T028 [US3] Test the REST path in `relay-platform/services/gateway/src/rest-delivery.itest.ts` (SC-006), with the clause's five-second window as the bound rather than an arbitrary one
- [ ] T029 [US3] If either path misses the window: record it in `gaps.md` with an owner, state it plainly in the chapter, and do **not** narrow FR-013 to make it pass. FR-RTM-10 is P1 and a quiet claim here is the defect this chapter exists to remove, one clause over
- [ ] T030 [P] [US3] FR-014, SC-007, in `relay-platform/services/gateway/src/rest-delivery.itest.ts`: a private channel's message reaches no non-member's socket. **This is a fourth door onto FR-CHN-05** and gets its own test rather than an inference from the read paths' three
- [ ] T031 [P] [US3] In `relay-platform/services/api/src/fanout/fanout.itest.ts` — a banned sender, an archived channel, an exhausted quota, and an application key naming a person: each refused, each publishing nothing (SC-004). Four refusals, and each assertion states what would have to be false for it to fail

## Phase 6: Failure, and the tests that must not pass for the wrong reason

- [ ] T032 Test SC-005 in `relay-platform/services/gateway/src/rest-delivery.itest.ts` — with Redis unreachable, a REST send returns `201` and the message is recoverable by resume. **This is the constitution's gate**: principle IV's *"Any new delivery mechanism MUST preserve this recovery property"*
- [ ] T033 **Prove T032 can distinguish anything.** `publish` swallows its own errors and resolves (R8), so "the send returned 201 while Redis was down" is equally true of a publisher that does nothing. Delete the publish call, run T032, and watch it stay green. Then make the assertion the **`fanout.publish_failed` log line** (FR-011), and re-run the deletion to watch it go red. Record both runs
- [ ] T034 Measure the REST send's p95 with Redis **dead**, not merely absent (R10's hazard). `limits/store.ts` learned this the hard way: *"an outage that instead adds seconds to every request has refused it in a slower way, and NFR-PRF-02 asks for a p95 under 150 ms"*. Measure the same path with `createFanout`'s default options for the contrast — that number is what justifies not copying the gateway's client
- [ ] T035 Measure a **connected but slow** Redis, the residual risk the plan's post-design re-check named and the contracts did not close. `maxRetriesPerRequest: 0` and `connectTimeout` bound a dead server; neither bounds a slow one, and ioredis has no command timeout unless one is set. If a hung Redis holds every send open, add `commandTimeout` and say so
- [ ] T036 [P] Verify R10's gateway claim rather than repeating it: stop Redis, send on a socket, watch the gateway process. `createFanout` attaches no `error` listener to either client and no test anywhere covers a dead fan-out. **If the process dies, that is pre-existing and this chapter surfaced it** — record it in `gaps.md`, and decide deliberately whether fixing it belongs here

## Phase 7: The chapter

- [ ] T037 Decide the two file counts and keep them in separate columns from here to close-out: **what the chapter teaches** drives the word estimate, **what it must fence** drives the chain. `plan.md` predicts nine and twelve. Neither number is ever asked to do the other's job
- [ ] T038 Estimate the prose from the number of **arguments**, not from a per-file rate. 3.15 and 3.16 agreed on ~154 words per taught file and 3.17 came in at 84.7 — 45% below. `plan.md` names five arguments and estimates 2,200–2,800 words against the series' 2,000–4,000 bound (SC-011)
- [ ] T039 Write `relay-tutorial/app/(en)/part-3/chapter-18/the-message-that-never-arrived/page.mdx`. The chapter's five arguments: the ordering that cannot be copied to REST, the two NFRs pulling opposite ways, why the grammar moved and the client did not, the recovery property under a lost publish, and what T026–T029 found about membership
- [ ] T040 State FR-002 explicitly: **there is no SRS amendment**, principle VI is satisfied by citation, and the unmet clause is **FR-RTM-01** — not FR-RTM-05, which `docs/07-tutorial-plan.md`'s row names (FR-001). A reader arriving from 3.17, where the amendment *was* the gate, will look for one
- [ ] T041 State FR-003: FR-RTM-05 names six event kinds and this chapter delivers one, because one is all that has a producer. `message.updated` and `membership.changed` have none outside tests, and nothing writes `messages.edited_at` or `messages.deleted_at`
- [ ] T042 State FR-012 in `page.mdx`: what a client may conclude from having received nothing. A missing frame is not evidence a message does not exist — resume is the guarantee, the fan-out is the optimisation
- [ ] T043 [P] Write `figures.ts` — the missing edge from `docs/05-sad.md:138` as it is today and as it becomes, and the ordering comparison between the two transports
- [ ] T044 [P] Assemble the Vietnamese twin under `app/(vi)/...`, fences byte-identical to the English (the chain's `MIRROR` rule)
- [ ] T045 Fence every path in T037's second column, under `relay-tutorial/fences/`. **Three lines of context suffice because uniqueness is checked**; the predecessor is a **commit**, not a tag — a feature's tail can amend a platform file after tagging, which cost 3.17 five wrong answers
- [ ] T046 Check `relay-tutorial/fences/post-series.md` for whether any file this feature touches is appendix-owned before fencing it. An appendix hunk anchored on a file's last line forbids a chapter from appending to it, and a diff generated straight to HEAD performs the appendix's edit itself

## Phase 8: Close-out

- [ ] T047 Re-derive the file count from `git diff --name-only` in both repositories and reconcile it against `pnpm check:fences`. T037's twelve is a first count and is **expected to be wrong**; this comparison found two files in no bucket in 3.16
- [ ] T048 [P] `pnpm turbo run test`, `pnpm test:integration`, `pnpm test:outsider`, `pnpm coverage` — and build first, so `check:errors` reads a current `dist`
- [ ] T049 [P] `pnpm check:fences`, `check:figures`, `check:errors`, `check:srs`, `check:docs`
- [ ] T050 Coverage, against the pins in `relay-platform/vitest.coverage.config.mts`: expect the ratchet to argue. It has **removed** code three times rather than covered it. A new publisher's error path is exactly the shape that lands at 98.9 against a pin of 99
- [ ] T051 Run the integration lane 20+ times with nothing else on the machine. 589 tests at 3.17's close, mean 193.55 s, stdev 0.99, 240 s budget — and the lane costs per **suite**, not per test, so an added api boot moves the mean more than added assertions do. **Twenty green rejects a per-run failure rate above 13.91% and nothing finer**; 3.17's one failure in twenty-six is `gaps.md` item 1, still unidentified
- [ ] T052 SC-010: the sealed outsider in `relay-platform/packages/outsider/` sends over REST, waits on a socket, and succeeds — following its README, not the source
- [ ] T053 **Use a person**, and record what they hit in `specs/036-chapter-3-18/chapter-notes.md`. Chapters 3.14, 3.15, 3.16 and 3.17 each named this gap and none closed it. Every check in this repository compares bytes; the sealed outsider was wrong about the API for two chapters because nobody ran it, and a published Trap contradicting 3.17's own chapter survived fifteen analysis passes because no checker reads prose
- [ ] T054 SC-009: close chapter 3.12's `gaps.md` G1 rather than amending it again (FR-015), and cite **FR-RTM-01** in `traceability.md`
- [ ] T055 FR-016: re-examine chapter 3.14's Phase 2 verdict and record what is now true of it in `specs/036-chapter-3-18/chapter-notes.md`
- [ ] T056 Write `chapter-notes.md` — the plan against what shipped, including the phases that went badly — and `gaps.md` with an owner per item. Update `docs/07-tutorial-plan.md`'s row from planned to shipped
- [ ] T057 Confirm FR-017 against `docs/07-tutorial-plan.md`: presence is untouched, and chapter 3.19 still owns FR-RTM-06 and FR-RTM-07

---

## Dependencies

    Phase 1  ──▶  Phase 2  ──▶  Phase 3 (US1, MVP)  ──▶  Phase 4 (US2)
                                       │
                                       ├──▶  Phase 5 (US3)   independent of US2
                                       └──▶  Phase 6         independent of US2, US3
    Phases 3–6  ──▶  Phase 7 (chapter)  ──▶  Phase 8 (close-out)

**T009 before T010.** The guard test comes before the wiring, because the wiring is where the
double-publish would be introduced.

**T012 before T020.** The ordering decision changes where the publish goes, so it cannot be
made after the publish is written.

**T026 before T028.** Establish where membership is actually checked before asserting anything
about the window.

**T033 immediately after T032.** A failure-path test that has not been shown to fail is not
yet evidence.

## Parallel opportunities

- Phase 2: T011 alongside T008/T010 (different file)
- Phase 3: T014–T019 are six independent test files
- Phase 5: T030 and T031 alongside T026–T029
- Phase 7: T043 and T044 alongside T039
- Phase 8: T048 and T049 together, then T051 alone — **nothing else runs on the machine during a
  timing battery** (3.12's attempt one failed at run 11 to two dev servers, with no port held and
  no `EADDRINUSE`)

## Independent test criteria

| story | passes when |
|---|---|
| US1 | a REST send reaches an already-open socket, and the frame is indistinguishable from a socket-sent one |
| US2 | two gateway processes, a member on each, one REST send — both receive it; an instance with no member receives nothing |
| US3 | a removed member receives nothing within FR-RTM-10's five seconds, on **both** paths, or the gap is recorded rather than narrowed |

## Implementation strategy

**MVP is Phase 3** — US1 alone closes chapter 3.14's verdict and `gaps.md` item 3. US2 is already
proven at the fan-out layer (R7), so it is a test against a new publisher rather than new
delivery. US3 is the one that may not end in a passing test, and Phase 5 is written so that
outcome is a recorded gap rather than a narrowed requirement.

**Phase 6 is where this feature is most likely to lie to itself.** Its central mechanism resolves
successfully when it fails, so every test there names what would have to be false for it to fail,
and T033 makes the suite prove it can tell.
