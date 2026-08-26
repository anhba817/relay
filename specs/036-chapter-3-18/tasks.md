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
already publishes — and deliver **every socket-sent message twice**. That is FR-006, and T012 is
the test that would have caught it.

## Where the tests live, and why not in one place

Analysis measured the fixtures before these tasks named any. **No suite in this repository boots a
real api with a real gateway.** The gateway's suites stub `ApiClient` because the gateway has no
database (ADR-05), so they cannot share a Postgres fixture with a real api:

    services/gateway/src/fanout.itest.ts    0 gateway boots   0 socket opens   fabric only
    services/gateway/src/resume.itest.ts    2 gateway boots   6 socket opens   api is a STUB (:21)
    services/gateway/src/session.itest.ts   4 gateway boots  12 socket opens   api is a stub
    services/api/src/**.itest.ts            no suite opens a socket at all
    packages/outsider/                      RELAY_API_URL and RELAY_WS_URL — both

So the feature is proven at three levels, and each task says which it is:

| level | what it proves | where |
|---|---|---|
| **publisher** | the api publishes the right payload to the right subject, under the right conditions | `services/api/src/fanout/fanout.itest.ts` — a real Redis subscriber |
| **delivery** | a frame on `chan:{id}` reaches the right sockets and not the wrong ones | gateway suites, publishing to the subject **directly** — no api needed, and two real instances with real sockets are available |
| **end-to-end** | a real REST send reaches a real socket | `packages/outsider/` — the only place with both |

**The two-instance claim rests on composition plus a real delivery test, not on one end-to-end.**
T027 states that limitation in the chapter rather than letting the task table imply more.

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
- [ ] T008 Run `pnpm build` before believing any checker: `check:errors` reads `packages/protocol/dist/codes.js`, the built artifact, and a stale `dist` makes it green for the wrong reason

### The publisher

- [ ] T009 Create `relay-platform/services/api/src/fanout/publisher.ts` — a `MessagePublisher` with `publish(message)` and `close()` only, one ioredis client, per `contracts/fanout-publisher.md`. Client options come from `services/api/src/limits/store.ts` (`lazyConnect`, `maxRetriesPerRequest: 0`, `connectTimeout: 1_000`, and an `error` listener), **not** from `createFanout`, which has neither (R10). It reads `RELAY_REDIS_URL` the way `limits/store.ts:86` already does, so this feature adds no configuration. Carry the reason in a comment
- [ ] T010 [P] Unit-test the publisher in `relay-platform/services/api/src/fanout/publisher.test.ts`: the subject is `chan:{id}`, the JSON is exactly six fields, and `publish` **resolves** when the client throws
- [ ] T011 Wire the publisher into `relay-platform/services/api/src/messages/messages.module.ts`, following `services/api/src/limits/limits.module.ts:36`'s pattern — `{ provide: …, useFactory: … }`, the way the api already provides its Redis-backed counter store
- [ ] T012 Write the FR-006 guard test in `relay-platform/services/api/src/fanout/fanout.itest.ts` **before** T011's wiring is trusted: a send through the **internal** route publishes **nothing**, asserted by count on a Redis subscriber over a window (SC-003). What would have to be false for this to fail? That the api publishes for the internal route. This is the test that catches a publish placed in `messages.service.ts`

## Phase 3: User Story 1 — a REST send reaches a connected member (P1) 🎯 MVP

**Goal**: `POST /v1/channels/:channelId/messages` reaches an already-open socket.
**Independent test**: T003's outsider scenario, now passing.

### The ordering, now settled in the spec

- [ ] T013 [US1] Verify the amended **FR-005** holds as written before the publish goes in: the clause now splits by transport — socket is commit/ack/publish, REST is commit/publish/respond — because the response *is* the acknowledgement and a handler cannot publish after it without detaching. Confirm the amendment is in `spec.md`, and carry its recorded cost into the chapter: **NFR-PRF-01's clock is not measurable on the REST path** because the interval can be negative
- [ ] T014 [US1] Measure `PUBLISH` p50/p95 from the api against a live Redis and put it in `specs/036-chapter-3-18/baseline.txt`. The publish now lands inside NFR-PRF-02's budget (p95 < 150 ms for the whole write); `contracts/fanout-publisher.md` asserts sub-millisecond, and an assertion is not a measurement

### Tests for User Story 1 — publisher level

- [ ] T015 [P] [US1] **FR-004**, the feature's core clause, in `relay-platform/services/api/src/fanout/fanout.itest.ts`: a REST send publishes to `chan:{channelId}` after the write commits. Assert on a real Redis subscriber, so the test names the subject rather than trusting delivery
- [ ] T016 [P] [US1] **FR-009, SC-008** in `relay-platform/services/api/src/fanout/fanout.itest.ts`: the payload the api publishes is indistinguishable from what a socket send publishes. Use `withoutRequestId` from `services/api/src/isolation/compare.ts` — **the oracle is api-side and unreachable from a gateway test**, which is why this comparison is made on published payloads rather than on delivered frames. Build the two payloads from independent sources: **a shared helper moves both halves of a pair and the oracle then sees nothing** (3.17's T044)
- [ ] T017 [P] [US1] The extra-key case `data-model.md` found untested, in `relay-platform/services/api/src/fanout/fanout.itest.ts`: `messageSchema` is a `z.strictObject`, `fanout.itest.ts:128` proves an invalid **value** is dropped, and nothing proves a seventh key is. `channel_id` alongside `channel`, or `environment_id`, are the two mistakes this publish site is most likely to make, and both would deliver **nothing** while the send returned `201`
- [ ] T018 [P] [US1] A send to a channel with no connected member publishes and the send still returns `201`, in `relay-platform/services/api/src/fanout/fanout.itest.ts` (spec edge case 2 — a frame nobody hears is correct, not a loss)

### Tests for User Story 1 — delivery level

- [ ] T019 [P] [US1] The same user on two connections receives the frame on **both**, in `relay-platform/services/gateway/src/session.itest.ts`, by publishing to `chan:{id}` directly. No api is needed: what is under test is the registry's fan-out to local sockets, and the publisher's identity is irrelevant to it (spec edge case 5)

### Test for User Story 1 — end-to-end

- [ ] T020 [US1] **SC-001** in `relay-platform/packages/outsider/src/integrate.itest.ts` — T003's scenario, now green. This is the only level where a real REST send and a real socket meet, and the outsider follows the README rather than the source

### Implementation for User Story 1

- [ ] T021 [US1] Add the publish to `relay-platform/services/api/src/messages/messages.controller.ts`, immediately before the `return` that assembles the response. Six fields: `channel: message.channel_id` (**renamed** — the frame's field is `channel`), `user: actingExternalId`, and `id`/`seq`/`text`/`created_at` from `message`
- [ ] T022 [US1] Guard it in `relay-platform/services/api/src/messages/messages.controller.ts` with the two conditions mirrored from `session.ts:651` — `!message.duplicate` (**FR-007**) and `message.text !== null`. Carry the gateway's reasons across: a retry is storage-safe, not delivery-safe; a tombstone recovered by an old key is not a creation
- [ ] T023 [US1] Verify **FR-008** by construction in `relay-platform/services/api/src/messages/messages.controller.ts`: `send()` throws on a refusal, so a publish on the success path never runs for one. **Do not use `finally`** — a `finally` publishes after a `403`

## Phase 4: User Story 2 — sender and recipient on different instances (P1)

**Goal**: the api that accepted the send has no relationship with the gateway holding the socket.
**Independent test**: two gateway instances with real sockets, one frame on the subject, the member's instance delivers and the other does not.

- [ ] T024 [P] [US2] **SC-002's delivery half** in `relay-platform/services/gateway/src/resume.itest.ts`'s topology — two gateway instances, real sockets, `:90`'s *"Another gateway instance, as far as Redis is concerned"*. Publish to `chan:{id}` directly and assert the member's socket receives it. This is stronger than `fanout.itest.ts:89`, which has **no sockets at all**
- [ ] T025 [US2] The negative half, same file: an instance holding no member of the channel delivers nothing. The subject is the filter, and `fanout.itest.ts:102` proves it at the fabric — this proves it at a socket
- [ ] T026 [US2] Check the blast radius of `relay-platform/services/gateway/src/resume.itest.ts`'s shared `boot()` fixture before changing it. **Promoting or repurposing a shared gateway fixture took five tests down in 3.17's T040b**, the fifth such incident in two features. If it needs a new capability, add one (3.17 used `disposable()`) rather than changing what the existing one is
- [ ] T027 [US2] State the limitation in the chapter and in `specs/036-chapter-3-18/chapter-notes.md`: **SC-002's full claim rests on composition** — the api publishes (T015), any subscribed instance delivers (T024/T025), and one end-to-end runs in the outsider lane against a single gateway. No fixture in this repository boots a real api with two real gateways, and pretending otherwise is the kind of quiet claim this chapter exists to remove

## Phase 5: User Story 3 — no delivery to somebody who may no longer see it (P2)

**Goal**: FR-013's clause, and the plan's largest open risk.
**Independent test**: remove a member, publish to the channel, assert nothing arrives on their socket within the clause's window.

- [ ] T028 [US3] **Establish where membership is checked before writing an assertion about it**, and record it in `specs/036-chapter-3-18/research.md`. R5's measurement: delivery filters by *subscription*, via `registry.subscribersOf(channelId)` at `session.ts:175`; the channel list is a snapshot from `POST /internal/session` at connect time; nothing in the delivery path re-reads membership
- [ ] T029 [US3] Test the **socket** path first, which this chapter did not create, in `relay-platform/services/gateway/src/session.itest.ts`: remove a member while their socket is open, publish to the channel, see whether a frame arrives. If the socket path already fails FR-RTM-10, this chapter did not cause it and must not claim to have fixed it
- [ ] T030 [US3] Test the REST-originated path in `relay-platform/services/api/src/fanout/fanout.itest.ts` and `session.itest.ts` between them (SC-006), with the clause's five-second window as the bound rather than an arbitrary one. **The api publishes regardless of membership** — it does not read it at the publish site — so if this passes, the filter is the subscription and the answer belongs to the gateway
- [ ] T031 [US3] If either path misses the window: record it in `specs/036-chapter-3-18/gaps.md` with an owner, state it plainly in the chapter, and do **not** narrow FR-013 to make it pass. FR-RTM-10 is P1 and a quiet claim here is the defect this chapter exists to remove, one clause over
- [ ] T032 [P] [US3] **FR-014, SC-007** in `relay-platform/services/gateway/src/session.itest.ts`: a private channel's message reaches no non-member's socket. **This is a fourth door onto FR-CHN-05** and gets its own test rather than an inference from the read paths' three
- [ ] T033 [P] [US3] In `relay-platform/services/api/src/fanout/fanout.itest.ts` — a banned sender, an archived channel, an exhausted quota, and an application key naming a person: each refused, each publishing nothing (SC-004). Four refusals, and each assertion states what would have to be false for it to fail

## Phase 6: Failure, and the tests that must not pass for the wrong reason

- [ ] T034 **FR-010 and SC-005** in `relay-platform/services/api/src/fanout/fanout.itest.ts` — with Redis unreachable, a REST send returns `201` and the message is recoverable through the api's own history route. **This is the constitution's gate**: principle IV's *"Any new delivery mechanism MUST preserve this recovery property"*. No socket is needed; resume reads Postgres
- [ ] T035 **Prove T034 can distinguish anything**, in `relay-platform/services/api/src/fanout/fanout.itest.ts`. `publish` swallows its own errors and resolves (R8), so "the send returned 201 while Redis was down" is equally true of a publisher that does nothing. Delete the publish call, run T034, and watch it stay green. Then make the assertion the **`fanout.publish_failed` log line** (**FR-011**), and re-run the deletion to watch it go red. Record both runs in `baseline.txt`
- [ ] T036 Measure the REST send's p95 with Redis **dead**, not merely absent (R10's hazard), into `specs/036-chapter-3-18/baseline.txt`. `limits/store.ts` learned this the hard way: *"an outage that instead adds seconds to every request has refused it in a slower way, and NFR-PRF-02 asks for a p95 under 150 ms"*. Measure the same path with `createFanout`'s default options for the contrast — that number is what justifies not copying the gateway's client
- [ ] T037 Measure a **connected but slow** Redis into `specs/036-chapter-3-18/baseline.txt` — the residual risk `plan.md`'s post-design re-check named and the contracts did not close. `maxRetriesPerRequest: 0` and `connectTimeout` bound a dead server; neither bounds a slow one, and ioredis has no command timeout unless one is set. If a hung Redis holds every send open, add `commandTimeout` to `services/api/src/fanout/publisher.ts` and say so
- [ ] T038 [P] Verify R10's gateway claim rather than repeating it: stop Redis, send on a socket, watch the gateway process. `relay-platform/services/gateway/src/fanout.ts` attaches no `error` listener to either client and no test anywhere covers a dead fan-out. **If the process dies, that is pre-existing and this chapter surfaced it** — record it in `specs/036-chapter-3-18/gaps.md`, and decide deliberately whether fixing it belongs here

## Phase 7: The chapter

- [ ] T039 Decide the two file counts in `specs/036-chapter-3-18/chapter-notes.md` and keep them in separate columns from here to close-out: **what the chapter teaches** drives the word estimate, **what it must fence** drives the chain. `plan.md` predicts nine and thirteen. Neither number is ever asked to do the other's job
- [ ] T040 Estimate the prose in `specs/036-chapter-3-18/chapter-notes.md` from the number of **arguments**, not from a per-file rate. 3.15 and 3.16 agreed on ~154 words per taught file and 3.17 came in at 84.7 — 45% below. `plan.md` names five arguments and estimates 2,200–2,800 words against the series' 2,000–4,000 bound (SC-011)
- [ ] T041 Write `relay-tutorial/app/(en)/part-3/chapter-18/the-message-that-never-arrived/page.mdx`. The chapter's five arguments: the ordering that cannot be copied to REST, the two NFRs pulling opposite ways, why the grammar moved and the client did not, the recovery property under a lost publish, and what T028–T031 found about membership
- [ ] T042 State **FR-002** in `page.mdx`: there is **no SRS amendment**, principle VI is satisfied by citation, and the unmet clause is **FR-RTM-01** — not FR-RTM-05, which `docs/07-tutorial-plan.md`'s row names (**FR-001**). A reader arriving from 3.17, where the amendment *was* the gate, will look for one. Note that FR-005 *was* amended, in this feature's own spec, and say why that is a different kind of amendment
- [ ] T043 State **FR-003** in `page.mdx`: FR-RTM-05 names six event kinds and this chapter delivers one, because one is all that has a producer. `message.updated` and `membership.changed` have none outside tests, and nothing writes `messages.edited_at` or `messages.deleted_at`
- [ ] T044 State **FR-012** in `page.mdx`: what a client may conclude from having received nothing. A missing frame is not evidence a message does not exist — resume is the guarantee, the fan-out is the optimisation
- [ ] T045 [P] Write `relay-tutorial/app/(en)/part-3/chapter-18/the-message-that-never-arrived/figures.ts` — the missing edge from `docs/05-sad.md:138` as it is today and as it becomes, and the ordering comparison between the two transports
- [ ] T046 [P] Assemble the Vietnamese twin under `relay-tutorial/app/(vi)/part-3/chapter-18/`, fences byte-identical to the English (the chain's `MIRROR` rule)
- [ ] T047 Fence every path in T039's second column, under `relay-tutorial/fences/`. **Three lines of context suffice because uniqueness is checked**; the predecessor is a **commit**, not a tag — a feature's tail can amend a platform file after tagging, which cost 3.17 five wrong answers
- [ ] T048 Check `relay-tutorial/fences/post-series.md` for whether any file this feature touches is appendix-owned before fencing it. An appendix hunk anchored on a file's last line forbids a chapter from appending to it, and a diff generated straight to HEAD performs the appendix's edit itself

## Phase 8: Close-out

- [ ] T049 Re-derive the file count from `git diff --name-only` in both repositories and reconcile it against `pnpm check:fences`. T039's thirteen is a first count and is **expected to be wrong**; this comparison found two files in no bucket in 3.16
- [ ] T050 [P] Run `pnpm turbo run test`, `pnpm test:integration`, `pnpm test:outsider`, `pnpm coverage` — and `pnpm build` first, so `check:errors` reads a current `dist`
- [ ] T051 [P] Run `pnpm check:fences`, `pnpm check:figures`, `pnpm check:errors`, `pnpm check:srs`, `pnpm check:docs`
- [ ] T052 Coverage, against the pins in `relay-platform/vitest.coverage.config.mts`: expect the ratchet to argue. It has **removed** code three times rather than covered it. A new publisher's error path is exactly the shape that lands at 98.9 against a pin of 99
- [ ] T053 Run `pnpm test:integration` 20+ times with nothing else on the machine. 589 tests at 3.17's close, mean 193.55 s, stdev 0.99, 240 s budget — and the lane costs per **suite**, not per test, so an added api boot moves the mean more than added assertions do. **Twenty green rejects a per-run failure rate above 13.91% and nothing finer**; 3.17's one failure in twenty-six is `gaps.md` item 1, still unidentified
- [ ] T054 **SC-010**: the sealed outsider in `relay-platform/packages/outsider/` sends over REST, waits on a socket, and succeeds — following its README, not the source
- [ ] T055 **Use a person**, and record what they hit in `specs/036-chapter-3-18/chapter-notes.md`. Chapters 3.14, 3.15, 3.16 and 3.17 each named this gap and none closed it. Every check in this repository compares bytes; the sealed outsider was wrong about the API for two chapters because nobody ran it, and a published Trap contradicting 3.17's own chapter survived fifteen analysis passes because no checker reads prose
- [ ] T056 **SC-009, FR-015**: close chapter 3.12's `gaps.md` G1 rather than amending it again, and cite **FR-RTM-01** in `specs/036-chapter-3-18/traceability.md`
- [ ] T057 **FR-016**: re-examine chapter 3.14's Phase 2 verdict and record what is now true of it in `specs/036-chapter-3-18/chapter-notes.md`
- [ ] T058 Write `specs/036-chapter-3-18/chapter-notes.md` — the plan against what shipped, including the phases that went badly — and `specs/036-chapter-3-18/gaps.md` with an owner per item. Update `docs/07-tutorial-plan.md`'s row from planned to shipped
- [ ] T059 Confirm **FR-017** against `docs/07-tutorial-plan.md`: presence is untouched, and chapter 3.19 still owns FR-RTM-06 and FR-RTM-07

---

## Dependencies

    Phase 1  ──▶  Phase 2  ──▶  Phase 3 (US1, MVP)  ──▶  Phase 4 (US2)
                                       │
                                       ├──▶  Phase 5 (US3)   independent of US2
                                       └──▶  Phase 6         independent of US2, US3
    Phases 3–6  ──▶  Phase 7 (chapter)  ──▶  Phase 8 (close-out)

**T012 before T021.** The guard test comes before the publish is written, because the publish is
where the double-delivery would be introduced.

**T013 before T021.** The ordering is settled in `spec.md` now, not by a task — but confirm the
amendment is there before writing code that depends on it.

**T028 before T030.** Establish where membership is actually checked before asserting anything
about the window.

**T035 immediately after T034.** A failure-path test that has not been shown to fail is not yet
evidence.

**T007 after T006.** The grammar's new test exists before the old assertion is removed, so the
property is never untested.

## Parallel opportunities

- Phase 2: T006 and T010 alongside their neighbours (different files)
- Phase 3: T015–T019 are five independent test cases across two files
- Phase 5: T032 and T033 alongside T028–T031
- Phase 7: T045 and T046 alongside T041
- Phase 8: T050 and T051 together, then T053 alone — **nothing else runs on the machine during a
  timing battery** (3.12's attempt one failed at run 11 to two dev servers, with no port held and
  no `EADDRINUSE`)

## Independent test criteria

| story | passes when |
|---|---|
| US1 | the api publishes the right payload to the right subject, and the outsider's REST send reaches its socket |
| US2 | two gateway instances with real sockets — the member's receives, the other does not — plus T027's recorded limitation |
| US3 | a removed member receives nothing within FR-RTM-10's five seconds, on **both** paths, or the gap is recorded rather than narrowed |

## Implementation strategy

**MVP is Phase 3** — US1 alone closes chapter 3.14's verdict and `gaps.md` item 3. US2's delivery
half becomes a real socket test that `fanout.itest.ts` never was; its end-to-end half is honestly
a composition, and T027 says so. US3 is the one that may not end in a passing test, and Phase 5 is
written so that outcome is a recorded gap rather than a narrowed requirement.

**Phase 6 is where this feature is most likely to lie to itself.** Its central mechanism resolves
successfully when it fails, so every test there names what would have to be false for it to fail,
and T035 makes the suite prove it can tell.
