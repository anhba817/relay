# Tasks: chapter 3.19 — presence, and who is allowed to see it

**Input**: design documents from `/specs/037-chapter-3-19/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: required, not optional. Constitution VI — every behaviour traces to a requirement and
every requirement states how it is verified, and `traceability.md` names the verification for every one. The count is not written here on purpose: it was `34` for three analysis passes after the spec had grown past it. `check-refs.py` reports it and fails when a requirement has no traceability row.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: can run in parallel — different files, no dependency on an incomplete task
- **[Story]**: US1–US4, on user-story phases only
- Every task carries an exact path

## Path conventions

    relay-platform/     packages/protocol/src/ · services/gateway/src/ · vitest.coverage.config.mts
    relay-tutorial/     app/(en)/… · app/(vi)/vi/… · lib/tutorial.ts · content/docs/
    docs/               the governing documents, mirrored into the tutorial by `pnpm sync:docs`

---

## Premises established before any task was written

Three claims these tasks depend on, checked rather than assumed. The habit exists because chapters
3.15 and 3.16 executed five wrong premises between them and 3.17 added five more.

**1. The two-instance session harness does not exist.** `attachSessions(` per gateway integration
file:

    0  fanout.itest.ts        3  isolation.itest.ts       1  limits.itest.ts
    0  meter.itest.ts         1  public-surface.itest.ts  1  resume.itest.ts
    4  session.itest.ts

Every call stands up **one** session server inside its own `describe`. No suite runs two
concurrently against one Redis. `fanout.itest.ts` does the two-instance thing at the *fabric*
level only — two `createFanout` clients, no sessions. Research R12's first draft said this harness
already existed; it does not, and T016 builds it.

**2. The gateway's integration files run in PARALLEL, so no test may touch shared state.**
`services/gateway/vitest.integration.config.mts` sets no `fileParallelism: false`, so
`presence.itest.ts` runs alongside `fanout`, `resume`, `limits`, `session`, `isolation`, `meter` and
`public-surface`. Stopping the compose Redis mid-run breaks all seven.
`services/api/src/limits/limits.itest.ts:484` already writes the rule down — *"a dead port rather
than stopping the container, because the lane runs files in PARALLEL and stopping Redis would break
every other suite mid-run"* — and **no test in this repository manipulates a container**: zero
`docker stop`/`start` matches across `services/` and `packages/`. T067 uses a dead port; T070 needs
restoration, which a dead port cannot give, so it uses an in-process TCP proxy.

**3. A gateway test can reach Postgres, but only through the api's built `dist`.** The gateway
package has no `pg` dependency (`ioredis`, `jose`, `ws`, and two workspace packages).
`services/gateway/src/meter.itest.ts:83` does `require_(join(apiDist, "db", "repository.js"))` and
`services/gateway/src/limits.itest.ts:102` the same through a `dist` binding. So FR-026's "a transition writes no outbox row"
needs **`pnpm build` first**, exactly like `check:errors` reading
`packages/protocol/dist/codes.js`. A stale `dist` makes it green for the wrong reason.

**4. `packages/protocol/src/fanout.ts` does not need to change.** `index.ts` re-exports whole
modules (`export * from "./fanout.js"`), and `internal.ts` already keeps the event spine's own
`subjectFor` in its own file. Each fabric owning its subject grammar is the precedent. So
`subjectForPresence` and the fabric payload both live in a new `presence.ts`, `fanout.ts` keeps
zero hunks, and chapter 3.18's fences are untouched.

---

## Phase 1: Setup

**Purpose**: the environment pinned, and the failing state observed before anything is built.

- [X] T001 Stop the compose `services` profile and record what was running, in `specs/037-chapter-3-19/baseline.txt` — `docker compose --profile services down` in `relay-platform`, then `docker compose ps`. `baseline.txt` must say this is required for `pnpm test:integration` **and** `pnpm coverage`. **The premise moved while these tasks were being written**: early in research all three app containers were up; by the time T007's command was run `docker ps` was empty and Postgres on 15432 refused the connection. So this task brings the stores **up** first and stops only the `services` profile — do not assume either state.
- [X] T002 [P] Record the port facts in `specs/037-chapter-3-19/baseline.txt`: Postgres 15432, Redis 6379, NATS 4222, from `docker compose port` rather than from prose. Only Postgres uses a non-default port on this machine.
- [X] T003 [P] Record in `specs/037-chapter-3-19/baseline.txt` that the lane is not idempotent from cold volumes — after `docker compose down -v` the first `pnpm test:integration` fails and the second passes (`specs/036-chapter-3-18/gaps.md` item 3).
- [X] T004 Capture the starting lane numbers into `specs/037-chapter-3-19/baseline.txt` with the colour codes stripped: `NO_COLOR=1 FORCE_COLOR=0 pnpm test:integration | sed -r 's/\x1B\[[0-9;]*[mK]//g'`. Expected 607 tests across 41 files, ~195 s against a 240 s budget. Every parse of this count in chapter 3.18 returned zero because turbo puts ANSI codes between "Tests" and the digits.
- [X] T005 Write the failing test in `relay-platform/services/gateway/src/presence.itest.ts`: two members of one channel, one connected, the other connects, and the connected one receives `presence.changed` with `state: "online"`. **It must be red for the right reason** — no producer exists. Record the failure text in `baseline.txt`. **It stays red until T022 in phase 3**, so the phase 1 and phase 2 commits both carry a failing integration test on purpose. Say so in the commit bodies: a red lane nobody explained is indistinguishable from a red lane nobody noticed, and CI cannot tell them apart either.
- [X] T006 [P] Confirm the grammar already exists and is already defended: run `pnpm --filter @relay/protocol test -t "presence"` and record that `frames.test.ts` asserts the frame's shape and rejects `state: "away"`. Chapter 1.3 shipped this; nothing here re-declares it.
- [X] T007 [P] Confirm the refusal already exists: run `pnpm --filter @relay/gateway test:integration -t "uttering a server frame"` and record that a client sending `presence.changed` is already closed with 4002. This is FR-015, and it is cited rather than written.
- [X] T008 Run `python3 specs/037-chapter-3-19/check-refs.py` and keep it green at the end of every phase, beside `git status --short`. It checks the tasks.md checklist format, that ids are sequential with no duplicates, and — the reason it exists — that **no artifact outside `tasks.md` cites a task id**. Three renumbers were each validated inside `tasks.md` alone and each left references elsewhere pointing at whatever task later took the number; one paragraph ended up citing the very test that disproved it, with every id still valid. Its own blind spot is in its header: it compares ids, never claims.
- [X] T009 `git status --short` in all three repositories and commit phase 1. **The commit body names the requirement ids this phase closes**, derived from `traceability.md` rather than from memory — the constitution's traceability bullet says *"PRs reference the requirement IDs they implement"*, and this project commits per phase rather than per PR, so the phase commit is where that lands. Keep it under five lines and add no `Co-Authored-By` trailer. The one-line check belongs at the end of every phase — chapter 3.18's phase 7 commit landed before phase 7's last edits because nobody ran it in the tutorial repo.

**Checkpoint**: the environment is pinned, the clause is red, and two requirements are already green.

---

## Phase 2: Foundational (blocking — every story depends on these)

**Purpose**: the grammar, the module, and the harness. No user story can start before these.

### The protocol module

- [X] T010 Create `relay-platform/packages/protocol/src/presence.ts` with `subjectForPresence(channelId: string): string` returning `presence:{channelId}`, and `presenceFabricSchema` — a `z.strictObject` of `user` (min 1), `state` (`z.enum(["online","offline"])`) and `transition` (min 1). Comment must say why this is not in `fanout.ts` and not called `subjectFor` — `internal.ts` already exports a `subjectFor` and chapter 3.18 paid for that collision with `Module '"@relay/protocol"' has already exported a member named 'subjectFor'`.
- [X] T011 Add `export * from "./presence.js";` to `relay-platform/packages/protocol/src/index.ts`, matching the whole-module re-export style already used for `frames`, `codes`, `internal` and `fanout`.
- [X] T012 [P] Unit tests in `relay-platform/packages/protocol/src/presence.test.ts`: the subject grammar is exactly `presence:{id}`; the payload rejects an unknown field (`strictObject`), rejects `state: "away"`, and rejects a missing `transition`. The strictness is the point — a field added on one side of a rolling deploy must fail loudly rather than be ignored.
- [X] T013 [P] Assert in `relay-platform/packages/protocol/src/presence.test.ts` that `subjectForPresence(id) !== subjectForChannel(id)` for the same id. The two grammars must not collide, and that is what makes cross-kind mis-delivery impossible rather than merely unlikely (FR-029).

### The gateway module

- [X] T014 Create `relay-platform/services/gateway/src/presence.ts` with `createPresence(options)` returning the `Presence` interface from `contracts/presence-lifecycle.md` — `onTransition`, `connected`, `disconnected`, `subscribe`, `unsubscribe`, `close`. Two ioredis clients (a subscriber cannot run `SET`/`EXISTS`), both with `error` listeners, and the listener comment must state the **accurate** reason: ioredis 6.0.0 does not kill the process — chapter 3.18 measured that and it stays alive — but its unstructured `[ioredis] Unhandled error event:` lines are unbounded and defeat NFR-OBS-01.
- [X] T015 Add `presence?: Presence` to `SessionServerOptions` in `relay-platform/services/gateway/src/session.ts`, optional for the reason `fanout`, `limits` and the meter are. **The four timings do NOT go here** — they live on `PresenceOptions`, because `attachSessions` builds the meter but receives presence already built, and an injected thing carries its own configuration. An earlier draft mirrored all four onto `SessionServerOptions` and eslint reported every one as unused.
- [X] T016 Build the two-instance harness in `relay-platform/services/gateway/src/presence.itest.ts`: two `attachSessions` servers on two ports in one test process, sharing one Redis, each with its own `Presence`. **New work — no existing suite runs two concurrently** (see premise 1). Namespace by fresh channel **and user** UUIDs per run: Redis pub/sub has no namespaces, and the presence key is `presence:{env}:{user}`, so a fresh channel alone is not enough.
- [X] T017 [P] Add a per-user lookup to `relay-platform/services/gateway/src/registry.ts` — `connectionsFor(userExternalId): Connection[]`, a filter over the existing map. Presence asks "is this the user's last connection on this instance", and the registry is where that question belongs, beside `subscribersOf`.
- [X] T018 Wire `createPresence` in `relay-platform/services/gateway/src/main.ts` beside `createFanout` and `createGatewayLimits`, and give its close an owner. The comment at `services/gateway/src/main.ts:40` already states the rule for chapter 3.8's client; this is the fourth and fifth Redis connections on the same reasoning.
- [X] T019 `git status --short` in all three repositories and commit phase 2, **naming in the body the requirement ids this phase closes** (the rule is on the phase 1 commit).

**Checkpoint**: the grammar exists, the module exists, two instances can be stood up. Nothing publishes yet.

---

## Phase 3: User Story 1 — a member sees a co-member arrive (P1) 🎯 MVP

**Goal**: a connected watcher receives one `online` frame when a co-member connects, on one
instance and across two.

**Independent test**: connect a watcher, connect a subject, assert one `online` frame naming the
subject. Then again with two instances.

### Tests for User Story 1

- [X] T020 [P] [US1] Factor the transition decision into a pure function in `relay-platform/services/gateway/src/presence.ts` — `wonTransition(reply: string | null): boolean` — and unit-test it in `relay-platform/services/gateway/src/presence.test.ts` over `"OK"` and `null`. **The Redis reply itself is not unit-testable here**: `PresenceOptions` takes a `url` and builds its own clients, and the gateway's pattern is pure logic in `.test.ts` and Redis in `.itest.ts` — `fanout.ts` has no unit test at all, and `limits.test.ts` covers only `windowStartFor` and `overLimit`. Both reply branches are covered behaviourally in the integration lane by T021 (`OK` publishes) and T024 (`nil` publishes nothing).
- [X] T021 [P] [US1] Integration test in `presence.itest.ts`: watcher connected, subject connects, watcher receives exactly one `presence.changed` `{ state: "online" }` for the subject. **Assert by count, not by arrival** — "a frame showed up" is true of a producer that publishes three.
- [X] T022 [P] [US1] Integration test in `presence.itest.ts`: the same with the watcher on instance A and the subject on instance B. This is the case a single-process test cannot show, and it is why the fabric exists.
- [X] T023 [P] [US1] Integration test in `presence.itest.ts`: a watcher sharing **three** channels with the subject receives exactly **one** frame (FR-012). Assert by count. Without the transition id this is three.
- [X] T024 [P] [US1] Integration test in `presence.itest.ts`: the subject's second connection produces no further frame to anybody (FR-006), asserted by count in a run where the first connection did produce one.
- [X] T025 [P] [US1] Integration test in `presence.itest.ts`: the subject's own socket receives its own `online` frame (FR-011). Pinned because both readings satisfy FR-RTM-07 and one of them has to be the one that ships.
- [X] T026 [P] [US1] Integration test in `presence.itest.ts`: a subject who is a member of no channel publishes to nobody and the connect still succeeds (FR-RTM-07's degenerate case).

### Implementation for User Story 1

- [X] T027 [US1] Implement `connected(user, channelIds)` in `relay-platform/services/gateway/src/presence.ts`: `SET … NX EX ttl`; on `OK`, mint a `transition` UUID, delete the offline-election marker, and publish the payload on `subjectForPresence(c)` for every channel. On `nil`, log `presence.suppressed` and publish nothing.
- [X] T028 [US1] Implement `subscribe`/`unsubscribe` in `presence.ts` with its own reference count over channel ids — two users of one channel on one instance must not unsubscribe each other, the same property `fanout.ts` documents for its own counts.
- [X] T029 [US1] Implement the receive path in `presence.ts`: parse with `presenceFabricSchema`, log `presence.invalid_payload` and drop on failure, then hand `(channelId, payload)` to the registered handler. Validate on receipt even though the fabric is inside the trust boundary — `services/gateway/src/fanout.ts:77-79` states the reason and it is unchanged here.
- [X] T030 [US1] Implement transition-level dedup in `presence.ts`: a `Map<transitionId, Set<connectionId>>` so a given transition reaches a given connection once, cleared a few seconds after arrival. All copies of one transition land within milliseconds.
- [X] T031 [US1] Add the delivery path in `relay-platform/services/gateway/src/session.ts` — a `deliverPresence` beside `deliver` that sends `{ type: "presence.changed", payload: { user, state } }` and **constructs the wire frame from two fields**, so the `transition` id cannot leak. It must not consult `connection.phase`, `connection.buffer` or `connection.marks`.
- [X] T032 [US1] Call `presence.connected(...)` in `relay-platform/services/gateway/src/session.ts` **after** the `registry.add(connection)` statement, and `presence.subscribe(channelId)` alongside `fanout?.subscribe(channelId)` in the same `Promise.all`. **Anchored on the statements, not on line numbers** — T015 and T031 both edit this file above these points, so any coordinate written here has already moved.
- [X] T033 [US1] Measure the subscription cost of the second subject grammar and record it in `specs/037-chapter-3-19/baseline.txt`: `SUBSCRIBE` calls and connect latency for a user in 1, 5 and 20 channels, **with `presence` supplied and with it omitted** — the option is optional on `SessionServerOptions`, so both numbers come from the same run rather than from a baseline this task sits too late to capture. `plan.md` names the doubled count as R1's declared price and says the enveloped-subject alternative stays available if the number is bad — which is only true while somebody produces the number. Analysis pass 2 found the plan promising this measurement and no task taking it.
- [X] T034 [US1] `git status --short` in all three repositories and commit phase 3, **naming in the body the requirement ids this phase closes** (the rule is on the phase 1 commit).

**Checkpoint**: `online` works on one instance and across two, and the duplicate is already dead.

---

## Phase 4: User Story 2 — the grace period (P1)

**Goal**: a reconnection inside the window is invisible; a real departure produces exactly one
`offline`, no earlier than 30 seconds.

**Independent test**: close the subject's only connection, assert nothing for the window, assert
one `offline` after. Separately, reconnect inside the window and assert nothing ever arrives.

### Tests for User Story 2

- [X] T035 [P] [US2] **Unit test in `relay-platform/services/gateway/src/presence.test.ts` that the production default `presenceGraceMs` is 30_000**, that `presenceTtlMs` defaults to 30_000 and `presenceRefreshMs` to 10_000, that `presenceMarginMs` defaults to 1_000, and that `refreshMs < ttlMs` holds for the defaults. **Do not assert `ttlMs >= graceMs` as an enforced invariant** — the re-pin is what makes the grace correct, not the numeric relation, and T040 has to set `ttlMs` below `graceMs` deliberately to open the gap. A constructor that refused that configuration would refuse its own regression test. Without this the clause's number lives only in a constant somebody edits. Every other grace test runs in milliseconds — 45 s of lane headroom does not buy six real 30-second waits.
- [X] T036 [P] [US2] Integration test in `presence.itest.ts`: last connection closes, nothing arrives before `graceMs`, exactly one `offline` after (FR-004).
- [X] T037 [US2] Measure the observed close-to-`offline` delay across the suite's runs and record it in `specs/037-chapter-3-19/baseline.txt` as SC-005's upper bound. A measured number, not an estimate — the clause asks what the delay *is*, and the lower bound alone leaves the other half of it unstated.
- [X] T038 [P] [US2] Integration test in `presence.itest.ts`: reconnect at half the window — no `offline` ever, and no second `online` either (FR-007). The state did not change.
- [X] T039 [P] [US2] Integration test in `presence.itest.ts`: reconnect at half the window **to the other instance** — same outcome (FR-005). This is the case the TTL-as-liveness-signal exists for.
- [X] T040 [P] [US2] Integration test in `relay-platform/services/gateway/src/presence.itest.ts`: **reconnect after `presenceTtlMs` has lapsed but before `presenceGraceMs` ends** — no `offline`, and **no second `online`** (FR-007). This is the case T038, T039 and T043 cannot see: they reconnect at a half and a third of the window, and the gap only opens in the last third. Set `presenceTtlMs` below `presenceGraceMs` in this one test to force the gap open, and watch it fail before T051's re-pin exists.
- [X] T041 [P] [US2] Integration test in `presence.itest.ts`: two connections, one closes, no `offline` at any point while the other is open (FR-006). Then the second closes and one arrives.
- [X] T042 [P] [US2] Integration test in `presence.itest.ts`: the two connections on **two different instances** (FR-005).
- [X] T043 [P] [US2] Integration test in `presence.itest.ts`: close, reopen at a third of the window, close again — exactly one `offline`, once, answered by the state at the end of the second window (FR-028). Two pending timers would produce two.
- [X] T044 [P] [US2] Integration test in `relay-platform/services/gateway/src/presence.itest.ts`: **a deploy drain** — twenty connected users' sockets close in the same tick, and each produces exactly one `offline` after the grace. The spec's edge case asks for this in as many words: a mass disconnect is the worst case for whatever schedules the grace check, and it is twenty pending timers and twenty round trips at once. `docs/05-sad.md:634` drains the gateway on SIGTERM, so this is the deploy path, not a hypothetical.
- [X] T045 [P] [US2] Integration test in `relay-platform/services/gateway/src/presence.itest.ts`: **a user with five connections closes all five** — no `offline` until the last, then exactly one. FR-RTM-09's cap is enforced nowhere (`services/api/src/limits/policy.ts:13` mentions it in a comment and nothing counts), so the reference count is unbounded and two connections is the easy case.
- [X] T046 [P] [US2] Integration test in `presence.itest.ts`: two instances whose last connections close in the same tick produce exactly **one** `offline` frame at the watcher, not two. This is the election, and it is the only thing standing between correct behaviour and a duplicate.
- [ ] T047 [US2] In `relay-platform/services/gateway/src/presence.itest.ts`, **test that swapping `registry.remove(connection.id)` and `presence.disconnected(...)` in `relay-platform/services/gateway/src/session.ts` fails.** Not a taste assertion: with the order reversed the closing connection is still in the registry, the local count is 1 rather than 0, no grace check is ever scheduled, and the user never goes offline. Assert the scheduling, not the comment. **NOT IMPLEMENTED AS WRITTEN — see `baseline.txt`.** A test cannot swap two lines of production code. The ordering is guarded instead by the two behavioural cases (closing one of two publishes nothing; closing the last publishes one), which BOTH fail if the calls are swapped, because `connectionsFor` would count the closing connection. Left open deliberately rather than ticked.
- [X] T048 [P] [US2] Unit test in `relay-platform/services/gateway/src/presence.test.ts`: the pure `graceCheckDelay(graceMs, marginMs)` returns `graceMs + marginMs`. This is the half of R2b's fix that is a number, and a number is unit-testable.
- [X] T049 [P] [US2] Integration test in `relay-platform/services/gateway/src/presence.itest.ts` that the re-pin is **awaited**, asserted deterministically rather than by racing it. Configure `presenceTtlMs: 5_000` and `presenceGraceMs: 1_000` — deliberately unequal, which is why nothing enforces `ttlMs >= graceMs` — then `await presence.disconnected(...)` and read `PTTL presence:{env}:{user}`. It must reflect `graceMs`, not `ttlMs`: a five-fold separation, so the assertion cannot turn on a millisecond. If the implementation arms the timer without awaiting the pin, the promise resolves while the key still carries the refresh TTL and the read shows ~5_000.

  *A first draft asked for twenty close-and-wait cycles at `presenceMarginMs: 0` instead. That is a race detector whose signal is a Redis round trip and whose noise is timer lateness — the same order of magnitude — so correct code could fail it and broken code could pass. This lane already carries one unexplained flake as **chapter 3.17's** `gaps.md` item 1 — a different ledger from 3.18's, whose item 1 is the idempotency-key mismatch; it does not need a deliberate one.*

### Implementation for User Story 2

- [X] T050 [US2] Implement the refresh timer in `relay-platform/services/gateway/src/presence.ts`: every `presenceRefreshMs`, `SET presence:{env}:{user} 1 XX EX ttl` for each distinct user this instance holds. On a `nil` reply the key vanished under a live connection — treat it as a new transition and publish `online` again (FR-031), which ADR-10 permits and which beats a user who is online and unpublishable. FR-031 exists because analysis pass 1 found this behaviour implemented, described in two design documents, and authorised by no requirement.
- [X] T051 [US2] Implement `disconnected(user, channelIds)` in `presence.ts`: if the registry still holds another connection for this user on this instance, return. Otherwise **re-pin the key with `SET presence:{env}:{user} 1 XX PX graceMs`, `await` that**, and only then schedule one check at **`+graceMs + marginMs`**, keyed by user in a `pending` map and **replacing** any existing timer rather than adding one. `XX` so it never resurrects a key that is already gone. Without the re-pin the key dies up to `refreshMs` before the grace ends — the expiry counts from the last refresh, the grace from the close — and a reconnection in that gap wins `SET … NX` and publishes a second `online`, which FR-007 forbids (research R2a). **And the await and the margin are not decoration**: pinning to `graceMs` while checking at `graceMs` sets two deadlines to one instant by two clocks, the check wins when the timer is prompter than the round trip, `EXISTS` finds the key alive, and the one-shot timer is gone — the user is stuck online permanently, which is worse than the duplicate the pin fixed. Research R2b.
- [X] T052 [US2] Implement the grace check in `presence.ts`: `EXISTS presence:{env}:{user}`; if present, log `presence.suppressed` and stop. If absent, `SET presence:offline:{env}:{user} 1 NX PX ttlMs` and publish `offline` on the captured channel set only if that reply is `OK`. **The marker's TTL is derived, not a hardcoded 60 s** — under a 300 ms test grace a fixed minute is two hundred times the window, correct only because the next `online` deletes it.
- [X] T053 [US2] Call `presence.disconnected(...)` in `relay-platform/services/gateway/src/session.ts` **after** the `registry.remove(connection.id)` statement, and `presence.unsubscribe(channelId)` alongside the existing `fanout.unsubscribe` — inside the same error-swallowing wrapper, because a close handler is the last place that should throw.
- [X] T054 [US2] Add a comment at `session.ts`'s close handler recording that it now carries **three** ordering constraints: the meter before `registry.remove` (a socket that opened and closed between two reports would be counted zero), presence after it (the count must exclude the closing connection), and the unsubscribes last. A later edit that groups the two notifications breaks one of them.
- [X] T055 [US2] Clear pending timers and the refresh interval in `presence.close()` in `relay-platform/services/gateway/src/presence.ts`, so a test that stands up two instances does not leak a timer into the next suite.
- [X] T056 [US2] `git status --short` in all three repositories and commit phase 4, **naming in the body the requirement ids this phase closes** (the rule is on the phase 1 commit).

**Checkpoint**: the clause's 30 seconds is real, survives a cross-instance reconnect, and cannot double-publish.

---

## Phase 5: User Story 3 — a stranger learns nothing (P1)

**Goal**: the negative half, asserted beside a positive in the same run.

**Independent test**: one socket that must receive and one that must not, asserted together.

### Tests for User Story 3

- [X] T057 [P] [US3] Integration test in `presence.itest.ts`: a user sharing no channel with the subject receives nothing across a full online→offline cycle, **while a co-member in the same run receives both**. A test that only asserts the negative passes when the producer is dead.
- [X] T058 [P] [US3] Integration test in `presence.itest.ts`: a non-member of a **private** channel receives nothing when a member of it transitions (FR-014, FR-CHN-05's third verb).
- [X] T059 [P] [US3] Integration test in `presence.itest.ts`: a user in a different tenant receives nothing (constitution I). Use the cross-tenant fixtures `seedSocketTenants` already provides in `relay-platform/services/gateway/src/isolation-fixtures.ts`.
- [X] T060 [P] [US3] Integration test in `presence.itest.ts`: no message is ever delivered as a presence frame and no presence payload as a message (FR-029). Publish both kinds on one channel's two subjects and assert each arrives as itself, exactly once.
- [X] T061 [P] [US3] Integration test in `presence.itest.ts`: a transition arriving while a connection is mid-resume is delivered immediately and never enters the buffer (FR-027). Assert the frame arrives **and** that the buffer's overflow flag is untouched.
- [X] T062 [P] [US3] Confirm the union is still ten members each classified exactly once — run the existing totality check in `relay-platform/services/gateway/src/isolation.itest.ts` unchanged. This feature adds no frame, so the number must not move.
- [X] T063 [US3] Confirm `relay-platform/services/api/src/isolation/targets.ts` is unchanged — no route was added, so nothing external can set presence (FR-008). The derived target list fails the build that adds a route and is the highest-yield check in the repository.
- [X] T064 [US3] Confirm the presence path reads no database (FR-009): `relay-platform/services/gateway/src/presence.ts` and `session.ts` import no `pg`, no `drizzle-orm` and no repository, and `pnpm lint` in `relay-platform` still passes chapter 2.1's ban. ADR-05 is enforced by a build failure and by nothing else, so the check is running it rather than citing it.

### Implementation for User Story 3

- [X] T065 [US3] No new scoping code. Confirm by reading that the scope is a property of the topology: an instance receives a transition only on the presence subjects it subscribed to, and it subscribed only to the channels its local members belong to. Record this in `specs/037-chapter-3-19/chapter-notes.md` — the requirement is met by the subscription set, not by a filter, and a reader will look for the filter.
- [X] T066 [US3] `git status --short` in all three repositories and commit phase 5, **naming in the body the requirement ids this phase closes** (the rule is on the phase 1 commit).

**Checkpoint**: FR-RTM-07 and FR-CHN-05's third verb are green, and the negatives are trustworthy.

---

## Phase 6: User Story 4 — presence failure costs nothing but presence (P2)

**Goal**: Redis down and the platform is unharmed — proven by a log line, not by an absence.

**Independent test**: point the presence path at a dead port, connect, assert the socket opens and
one named event is logged; restore Redis and assert the next transition publishes.

### Tests for User Story 4

- [X] T067 [P] [US4] Integration test in `relay-platform/services/gateway/src/presence.itest.ts`: with presence pointed at a **dead port** — `redis://127.0.0.1:1`, the address `services/api/src/fanout/fanout.itest.ts:508` already uses — a socket opens and the handshake completes (FR-023). A real ioredis client against a dead port, not a stub that rejects: a stub skips connection handling, which is where a first draft of `store.ts` got it wrong.
- [X] T068 [P] [US4] Integration test in `presence.itest.ts`: with presence down, a message sent over either entrance still reaches connected members (FR-023). Presence must not be load-bearing.
- [X] T069 [P] [US4] Integration test in `presence.itest.ts`: **exactly one `presence.failed` event is logged**, with `user`, `op` and `error` (FR-024). This is the assertion that carries FR-023 — a path that does nothing passes every "the socket still opened" check.
- [X] T070 [US4] Integration test in `relay-platform/services/gateway/src/presence.itest.ts`: after Redis is restored the next transition publishes **without a restart**. **This is the half that proves the path was alive** — without it the whole failure story is satisfied by an empty function. **Use an in-process TCP proxy, not the compose container.** `net.createServer()` forwarding to the real Redis, with `presence` pointed at the proxy's port: close the proxy to sever the connection, re-listen on the same port to restore it, and ioredis reconnects on its own — which is what "without a restart" means. Several suites already stand up a `createServer` fake this way. **Never `docker compose stop redis`**: `services/api/src/limits/limits.itest.ts:484` already states the reason — *"a dead port rather than stopping the container, because the lane runs files in PARALLEL and stopping Redis would break every other suite mid-run"* — and `presence.itest.ts` shares the gateway pool with seven other files. `redis-server` is not installed on the lane machine, so a disposable Redis binary is not an option either; the proxy is.
- [X] T071 [P] [US4] Integration test in `presence.itest.ts`: a close with Redis down does not throw and does not produce an unhandled rejection. Chapter 2.8's lane found exactly this on the unsubscribe path.
- [X] T072 [P] [US4] Integration test asserting a transition writes **no outbox row and no JetStream publish** (FR-026). Needs the api's built `dist` — see premise 2 — so this task runs `pnpm build` first or it is green for the wrong reason.
- [X] T073 [P] [US4] Integration test in `presence.itest.ts`: `presence.published` carries `user`, `state` and a `channels` **count**, and no message text and no token (FR-025). A channel list in a log file is a membership graph.
- [X] T074 [P] [US4] Integration test in `relay-platform/services/gateway/src/presence.itest.ts` covering the rest of the log vocabulary (FR-030): `presence.suppressed` fires when the `NX` guard loses and when a reconnection cancels a grace check, and `presence.invalid_payload` fires for a payload published on a presence subject that fails `presenceFabricSchema`. Two of the four events were specified in the contract, implemented by T027/T029/T052, and asserted nowhere.

### Implementation for User Story 4

- [X] T075 [US4] Wrap every Redis operation in `relay-platform/services/gateway/src/presence.ts` so a failure logs `presence.failed` and resolves. Comment must say what chapter 3.18 learned the hard way: swallowing an error and resolving makes "it worked with Redis down" true of a function that does nothing, so the log line is the requirement's evidence.
- [X] T076 [US4] `git status --short` in all three repositories and commit phase 6, **naming in the body the requirement ids this phase closes** (the rule is on the phase 1 commit).

**Checkpoint**: all four user stories are green. The platform work is done.

---

## Phase 7: The documents

- [X] T077 Amend `docs/04-srs.md` Appendix C row 3: open question 3 closes as **not opt-in per channel**, citing ADR-10, and naming the revisit trigger as undischarged because the lane's largest membership set is five channels (FR-016, FR-016a). **Name NFR-SCL-01 too** (FR-016c): the row lists it beside FR-RTM-07 as what the question blocks, it asks for 10,000 concurrent connections per gateway instance, and nothing here measures at that scale — so it closes resting on ADR-10's trigger, not on evidence.
- [X] T078 Verify no SRS **clause** changed: `git diff docs/04-srs.md` must touch Appendix C and nothing in §4.4 or §4.6 (FR-002, FR-002a). The distinction is the whole point of principle VI here.
- [X] T079 **Add ADR-19 to `docs/05-sad.md`, superseding ADR-10's subject-grammar clause** (FR-034). **Do not edit ADR-10's decision text** — constitution VII and `docs/05-sad.md:49` both say ADRs are immutable once accepted and superseding requires a new ADR, and no ADR in this project has ever been amended. An earlier draft of this task called the edit "a correction of a description, not a new decision"; ADR-10's own **Revisit when** clause refutes that, because *"presence subjects get their own fabric"* is the remedy it reserved for ~30% of publish volume and this chapter takes half of it early. ADR-19 follows the house shape — `**Status:** accepted (chapter 3.19) · supersedes ADR-10's subject clause · **Drivers:** D8` — states the decision (`presence:{channel_id}`, its own module, `fanout.ts` untouched), the rejected alternative (envelope both kinds on `chan:{id}`, which edits the message hot path at three points, the third inside a function ten chapters fence), and a revisit condition. **ADR-10 changes in exactly one place: its `**Status:**` line**, which already carries annotations, gains `· superseded in part by ADR-19`.
- [X] T080 Amend `docs/05-sad.md:210`'s not-a-service row so it stops pointing at an open question. The revisit condition survives — presence fan-out dominating gateway CPU — and it cites ADR-10 (FR-016b).
- [X] T081 [P] Amend `docs/05-sad.md:574-575`'s Redis table: the presence key's TTL and its refresh are two numbers, not one, and `conn:{env}:{user}` as a *set* with one TTL cannot expire a dead instance's member (research R6). Record the sorted-set correction without building it. **Add the two rows this design creates**: the key `presence:offline:{env}:{user}` and the pub/sub subject `presence:{channel_id}` beside the existing `chan:{channel_id}`. FR-017 asks the SAD to describe the fabric that ships, and a table missing half of what presence uses does not.
- [X] T082 Give ADR-19 its deep dive in `docs/06-adr-deep-dives.md`, in the house shape — Problem, Options, Analysis, Decision, Consequences, Revisit when — and **leave ADR-10's deep dive alone except for a supersession pointer** (FR-034). Its `:633` line says *"SRS Open Question 3 (opt-in presence per channel) stays open"* and its Decision paragraph says *"transitions published on the member channels' subjects"*; both were true when written and are superseded rather than wrong. An earlier draft of this task rewrote the Decision paragraph, which is the one edit "immutable once accepted" most clearly forbids. **Found by running T084's grep while writing these tasks** — the spec said three positions and there are five, across three documents.
- [X] T083 Record in `specs/037-chapter-3-19/chapter-notes.md` that this chapter takes **half of ADR-10's revisit remedy before its trigger fired**. `docs/06-adr-deep-dives.md:651` says that above ~30% of publish volume *"presence subjects get their own fabric or channels opt in"* — and R1 gives presence its own subject grammar now, for a different reason: the fan-out is typed to messages at three points. Say which of the two remedies was taken and why the trigger is still undischarged, or a later reader will read the design as the trigger having fired.
- [X] T084 [P] Amend the 3.19 row in `docs/07-tutorial-plan.md` to name FR-RTM-07 and FR-CHN-05, neither of which appears anywhere in that document today (FR-018, chapter 3.18's `gaps.md` item 8).
- [X] T085 Run `pnpm sync:docs` in `relay-tutorial`, then `pnpm check:docs`. The checker reads divergence, not correctness, and will not say which of the two copies is right (FR-019). **Three of this feature's four amended documents sync; `docs/07-tutorial-plan.md` does not and must not** (FR-019a) — `sync-docs.sh` keeps the published set as an explicit list and says why in its comment. Do not add 07 to that list to make this task feel complete: it publishes the series' unreleased chapter plan.
- [X] T086 Grep for open question 3 across `docs/` and confirm exactly one position survives (SC-010). **ADR-10's own text is not edited**, so what must agree is: the SRS Appendix C row (closed), `docs/05-sad.md:210`'s pointer, and **ADR-19**, which is where the closure is recorded. ADR-10 and its deep dive keep their original wording under a supersession note — a superseded ADR saying what it said is the record working, not a contradiction.
- [X] T087 `git status --short` in all three repositories and commit phase 7, **naming in the body the requirement ids this phase closes** (the rule is on the phase 1 commit).

---

## Phase 8: The chapter

- [X] T088 Write `relay-tutorial/app/(en)/part-3/chapter-19/<slug>/page.mdx`. The argument is one: a frame declared in chapter 1.3 and never produced. Estimate words from **arguments, not files** — 3.15 and 3.16 agreed on ~154 words per taught file and 3.17 came in at 84.7, 45% below, because it taught 16 files to make one argument.
- [X] T089 Keep two file counts in `specs/037-chapter-3-19/chapter-notes.md` from the start and never let either do the other's job: what the chapter **teaches** drives the word estimate; what it must **fence** drives the chain. Re-derive the third — files changed — from `git diff --name-only` at the very end.
- [X] T090 Decide and record in `specs/037-chapter-3-19/chapter-notes.md` **which of this feature's new files the chapter fences**: `packages/protocol/src/presence.ts`, `services/gateway/src/presence.ts`, `presence.test.ts` and `presence.itest.ts`. Chapter 3.18's `gaps.md` items 2 and 7 record what happens when this is left undecided — `session.itest.ts` is fenced by no chapter, so *"the end-to-end test that proves this chapter's claim is never replayed against the repository"*. If `presence.itest.ts` stays outside the chain, that is a decision with a reason in `gaps.md`, not a discovery at close-out for the second chapter running.
- [X] T091 State in `relay-tutorial/app/(en)/part-3/chapter-19/<slug>/page.mdx` the three things a reader will otherwise discover: presence has no snapshot on connect, so a roster starts empty; a user who joins a channel while connected does not appear online there until they reconnect (FR-021); and an instance that dies inside the grace window publishes no `offline`. **No checker reads prose** — a published Trap contradicted chapter 3.17's own chapter through fifteen analysis passes.
- [X] T092 Answer chapter 2.6's forward reference in `relay-tutorial/app/(en)/part-3/chapter-19/<slug>/page.mdx`, and in the Vietnamese mirror when it is translated (FR-033). A reader arriving from Part 2 was told presence would reuse the fan-out's plumbing. It does not, and **the reason is a better opening than silence**: the fabric is typed to messages at three points and the third sits inside a function ten chapters fence, so the alternative was never "keep it simple" — it was "edit the hot path".
- [X] T093 Name the five producer-less frame kinds in the chapter and in `specs/037-chapter-3-19/chapter-notes.md` (FR-022): `message.updated`, `message.deleted`, `membership.changed`, `typing` — and `presence.changed` until this chapter. All six of FR-RTM-05's kinds have frames in the union; after this chapter two have producers. Chapter 3.18's spec claimed `typing` had no frame, which is what an unnamed list costs.
- [X] T094 Correct chapter 2.6's ForwardRef in `relay-tutorial/app/(en)/part-2/chapter-06/two-servers-one-conversation/page.mdx` and its `app/(vi)/vi/` mirror (FR-033). It currently promises that *"presence (FR-RTM-06) and typing (FR-RTM-08) will reuse **this exact pub/sub plumbing** with TTLs per ADR-10"*. Presence does not: R1 gives it its own subject grammar and its own module, and `fanout.ts` is untouched. Keep the forward reference — a Part-2 reader is owed one — and stop it promising the plumbing. Typing's half of that sentence is still an open promise and stays one.
- [X] T095 Correct chapter 3.18's two passages in `relay-tutorial/app/(en)/part-3/chapter-18/the-message-that-never-arrived/page.mdx` and its `app/(vi)/vi/` mirror (FR-033): *"Presence needs the same missing mechanism"* and *"Chapter 3.19 needs the same thing built for presence."* R7 established that presence needs the subject's channel set **at transition time**, which `POST /internal/session` already supplies — not a membership push. The corrected premise is already in this feature's `gaps.md`; these two sentences are where a reader meets it.
- [X] T096 Correct chapter 3.8's passage in `relay-tutorial/app/(en)/part-3/chapter-08/limits-you-can-see-coming/page.mdx` and its `app/(vi)/vi/` mirror (FR-033): *"Presence needs the same"* connection registry. R6 established this chapter needs no `conn:{env}:{user}`, and that a Redis set carrying one TTL cannot expire a dead instance's member anyway — the sentence points at something both unneeded here and mis-specified where it is defined.
- [X] T097 [P] Translate to `relay-tutorial/app/(vi)/vi/part-3/chapter-19/<slug>/page.mdx`. A phrase sweep needs one word list per locale — eight English phrases scored zero against the Vietnamese prose making the claims they were written to find.
- [X] T098 [P] Add the 3.19 entry to `relay-tutorial/lib/tutorial.ts` with **all three** Vietnamese fields — `titleVi`, `readerProducesVi` and **`translatedIn: ["vi"]`**. Chapter 3.18 sets all three and is the only one of the last eight that sets the third; `app/sitemap.ts:26` is its one consumer, so without it the Vietnamese chapter routes and is absent from the sitemap. "Both fields" is what this task said until analysis pass 9 counted them, and following it would have regressed from the predecessor. Without it the chapter does not route and is not among the static pages.
- [X] T099 Run `pnpm check:fences` in `relay-tutorial` against predecessor **`caeabc9`** — a commit, not the tag `part3-ch18`. Expect the count to rise from 216 across 35 chapters. Three lines of context suffice when uniqueness is checked; a diff body inside a ts fence is read as a whole file.
- [X] T100 Run `python3 specs/037-chapter-3-19/check-prose.py` and require it green (FR-033a). It holds one fragment per contradicted claim **per locale** and fails while any survives; it is red on purpose until the corrections land. Its blind spot is in its header — it proves a sentence is gone, never that the replacement is right, and it cannot see a fifth contradiction nobody listed, which is how these four survived nine analysis passes.
- [X] T101 [P] Run `pnpm check:figures` and `pnpm check:srs` in `relay-tutorial`. `check:srs` enforces id uniqueness and says in its own comment that it does not read meaning.
- [X] T102 Run `pnpm build` in `relay-platform`, **then** `pnpm check:errors` in `relay-tutorial`. It reads `packages/protocol/dist/codes.js` — the built artifact — and a stale `dist` makes it green for the wrong reason. This feature adds no close code, so the count must not move.
- [X] T103 [P] Check both `page.mdx` files parse — `pnpm build` in `relay-tutorial`. An indented JSON block is literal text in markdown and a JSX expression in MDX; chapter 3.17 got `Could not parse expression with acorn` at line 3134 of a 4,400-line page.
- [X] T104 [P] Confirm both locales route (SC-013): after `pnpm build` in `relay-tutorial`, the chapter appears at both `/part-3/chapter-19/<slug>` and `/vi/part-3/chapter-19/<slug>`, and the static-page count rises from **92 to 93**. Both numbers here were wrong until analysis pass 7 checked them: 91 was **3.17's** close, and 3.18's own T053 asserts the move `91 -> 92`, so a chapter in two locales moves the count by **one**, not two. Re-derive it rather than trusting this line. A `lib/tutorial.ts` entry that typechecks is not the same as a page that routes.
- [X] T105 `git status --short` in all three repositories and commit phase 8, **naming in the body the requirement ids this phase closes** (the rule is on the phase 1 commit).

---

## Phase 9: Close-out

- [ ] T106 Stop the compose `services` profile again, then run `pnpm coverage` in `relay-platform`. A live `relay-dispatcher-1` moved a branch pin on a byte-identical file by 7.7 points in chapter 3.18 and cost half an hour of proving innocence.
- [ ] T107 Run the gates **in CI's order**, which `.github/workflows/ci.yml:96-110` fixes and which this task list named four of seven of: `pnpm lint`, `pnpm typecheck`, `pnpm test`, `pnpm build`, `node services/api/dist/db/migrate.js`, `pnpm test:integration`, `pnpm coverage`, then `pnpm test:outsider`. **`pnpm typecheck` and the full unit lane `pnpm test` are the two that were missing and matter** — this feature adds `presence.ts` in two packages, exports two helpers, and widens `SessionServerOptions` by four fields, which is the shape of change a typecheck catches and an integration lane does not. The migration step stays in sequence and is a no-op here; 3.18 omitted it for thirteen passes and recorded that this made the omission harmless rather than right.
- [ ] T108 Write the per-file coverage pins for `services/gateway/src/presence.ts` and `packages/protocol/src/presence.ts` in `relay-platform/vitest.coverage.config.mts`. **The target is 100/100/100/100, and it is NFR-MNT-02's MUST rather than a preference** — presence is tenant-isolation code (FR-032, and `plan.md`'s Constitution Check says why). Chapter 3.18's two new fan-out files both reached it. If a branch is unreachable, delete the unreachable code and say so; the ratchet has removed code three times rather than covered it. **Do not lower the pin with a reason** — a measurement always supplies one, which is how this requirement would quietly go missing. The ratchet has removed code three times rather than covered it; if a branch is unreachable, say which and why pinning 100 would mean deleting a defensive check.
- [ ] T109 Run the full lane battery and record it in `specs/037-chapter-3-19/baseline.txt`: count with the colour codes stripped, wall clock, and the 240 s budget. Nothing else runs on the machine during a timing battery — chapter 3.12's first attempt failed at run 11 to two Next.js dev servers, with no port held and no `EADDRINUSE`.
- [ ] T110 State the battery's power honestly in `chapter-notes.md`: twenty green runs reject a per-run failure rate above 13.91% at 95% confidence and nothing finer. A 5% flake survives twenty runs 35.85% of the time.
- [ ] T111 Re-derive `specs/037-chapter-3-19/traceability.md` from the shipped tree, **both directions again**. It already added FR-027, FR-028 and FR-029 during planning; the second run is what catches a requirement whose test was renamed or deleted.
- [ ] T112 Write `specs/037-chapter-3-19/gaps.md`, one item per gap, each with an owner, written when found rather than at close-out — **and carry the predecessors' unclosed items forward with their status, which chapter 3.17 did on seven of its nine owners and chapter 3.18 did zero times.** The convention matters because CLAUDE.md's header names only the immediate predecessor's ledger: an item 3.19 does not carry becomes unreachable by the path the header describes. Carry chapter 3.18's items 1, 2, 3, 5, 7 and 9 (its 4, 6 and 8 are this chapter's and close or move here), and chapter 3.17's still-open ones — its item 2 is this chapter's own subject and its item 1 is the unidentified lane flake this feature cites. **Number collisions are the reason every reference carries its chapter**: 3.17's item 1 is the flake and 3.18's item 1 is the idempotency-key mismatch. Already known to belong there: the missing presence snapshot; `conn:{env}:{user}`'s set-versus-TTL defect (R6); the two fenced files that state chapter 1.2's Redis override unconditionally (R13); chapter 3.18's `chapter-notes.md` saying 216 fenced files at line 17 and 212 at line 260; and chapter 3.18's spec claiming no typing frame exists in the union when `typingSchema` is in `frameSchema`. **And the fate of this feature's two checkers** — `check-refs.py` and `check-prose.py` are either feature-local instruments that die with the chapter, or they belong in `relay-tutorial/scripts/` beside the five `check:*` gates CI runs. Record the decision with an owner. Chapter 3.18's `sweep.py` is the precedent for not doing so: discussed in its `chapter-notes.md`, given no owner in its `gaps.md`, and referenced nowhere outside its own feature directory since.
- [ ] T113 Record in `gaps.md` that **FR-RTM-10 is still unmet**, with the corrected premise — presence needs the subject's channel set at transition time, which the session response already supplies, so chapter 3.18's `gaps.md` item 4's stated reason for assigning it here does not hold. Then **run it** — `pnpm --filter @relay/gateway test:integration -t "FR-RTM-10"` — and record that the violation is still asserted rather than assuming it. SC-012 asks for the test's state, not for a sentence about it.
- [ ] T114 Write `specs/037-chapter-3-19/chapter-notes.md` with **four sections, three of which analysis pass 10 found unplanned**, each written by chapter 3.18: (1) **"What shipped"** — the metrics block: files taught, files fenced, prose words, tests and files in the lane, wall clock and stdev, coverage per new file, fenced files across chapters. **This is the source the next chapter's CLAUDE.md header is built from** — 3.19's own header was assembled from 3.18's block, and without it 3.20 has nothing to read. (2) **"The phases that went badly"** — what happened, not what the plan said; the writing-style guide asks for it in as many words, because a document that only reports the plan working is one nobody trusts. (3) **"What the next feature should do differently"** — 3.18's version is where CLAUDE.md's lessons came from. (4) **"For chapter 3.20"** — the fence predecessor **as a commit**, not the tag, and whether anything was amended after it; chapter 3.17 paid five wrong answers for reading a tag instead, and `part3-ch19` will be annotated, so `git rev-parse part3-ch19` returns the tag object while `^{commit}` returns the commit.
- [ ] T115 `git status --short` in all three repositories and **commit the close-out records before anything is tagged** — `baseline.txt`, `traceability.md`, `gaps.md`, `chapter-notes.md` and the coverage pins. **Name the requirement ids this phase closes** as every other phase commit does — this one closes the coverage class and the deferral records, not nothing. Phase 9 had no commit task at all until analysis pass 15, so the tag would have been cut over an uncommitted tree. Chapter 3.18 recorded this exact failure — *"Phase 7's commit came before Phase 7's last edits"* — and the check it prescribed is the one-liner above, run in **every** repository rather than the one being edited. A close-out record committed after the tag is a post-tag commit, which is the case the next section has to explain rather than the case it wants to describe.
- [ ] T116 Tag `part3-ch19` in all three repositories with `git tag` and verify the gitlinks on both remotes. If the tag turns out wrong, delete and re-cut it — deleting an unpushed tag is cheap, and the alternative is an amendment after the tag, which is the thing this section exists to catch.
- [ ] T117 Hand `specs/036-chapter-3-18/reader-protocol.md` to a second person. **Named by chapters 3.14, 3.15, 3.16, 3.17 and 3.18 and closed by none of them.** No command in this repository can discharge it: every check here compares bytes, and the two most expensive prose defects in this project were both found by a person reading, late.

---

## Dependencies

    Phase 1  ──> Phase 2  ──> Phase 3 (US1)  ──> Phase 4 (US2)  ──> Phase 5 (US3)
                                                       │                 │
                                                       └────> Phase 6 (US4)
                                                                         │
                              Phase 7 (documents) ─────────────> Phase 8 (chapter) ──> Phase 9

- **Phase 2 blocks everything.** No story can start without the subject grammar, the module and
  the two-instance harness. **Inside Phase 2 the order is not free**: T015 adds `presence` to
  `SessionServerOptions` and T016's harness passes it, so the options come first. That pair sat the
  other way round until analysis pass 8 walked the tasks in execution order — the dependency notes
  were correct and silent about it, because the constraint had never been written down.
- **US2 depends on US1** — an `offline` transition cannot be observed without an `online` one to
  leave. US3 and US4 depend on US1 only.
- **Phase 7 depends on no platform phase** and could run earlier; it is placed after the code so
  the SAD amendment describes the fabric that actually shipped rather than the one planned.
- **T072 depends on `pnpm build`** (premise 2); **T102 and T104 depend on it** for the same class of
  reason — one reads a built artifact, the other counts built pages.
- **T040 must be written before T051's re-pin exists**, so it can be watched failing (T053 is the session-layer call; T051 is the implementation that pins the key). **T048 guards the other half of that fix** — the await-then-arm ordering and the `graceMs + marginMs` delay — and is a unit test because the race it defends against cannot be provoked reliably against a live Redis. It is the only
  test that can see the gap between the key's expiry and the grace's end (research R2a).

## Parallel opportunities

| Where | Tasks | Note |
|---|---|---|
| Phase 1 | T002, T003, T006, T007 | different files; T004 and T005 are serial on the lane |
| Phase 2 | T012, T013 after T010; T015, T017 | T014 and T016 are the critical path |
| US1 tests | T021–T026 | six integration tests, one file — parallel to write, serial to run. T020 is a unit test of a pure helper; T033 is a measurement, not a test, and is serial |
| US2 tests | T035–T046 | T047 depends on T053 existing to be swapped |
| US3 tests | T057–T062 | T063 and T064 are reads, not tests |
| US4 tests | T067–T069, T071–T074 | T070 must follow T067–T069 |
| Phase 7 | T081, T082, T084 | different files |
| Phase 8 | T097, T098, T101, T103 | after T088; T104 follows T103's build. T090's fencing decision is serial and comes first |

**One file, many tests.** T021–T073 mostly land in `presence.itest.ts`, so `[P]` means they can be
written independently, not that they can be committed by different hands at once. The lane costs
per **file**, not per test, and **not per api boot inside a package**. Chapter 3.18's `baseline.txt`
corrects the model this note used to quote: *"`--concurrency=1` serialises PACKAGES; vitest
parallelises FILES inside each… so 'cost scales with api boots' is true across packages and **false
within one**."* The api package fits 196.21 s of test time into 102.26 s of wall clock for exactly
that reason.

**This feature adds a file *within* the gateway package — the case where the old model does not
hold.** A pool's wall clock is set by its slowest file, and `presence.itest.ts` is the one file here
that deliberately waits: grace periods, a twenty-user drain, a five-connection teardown. The
reassuring cross-package figure (3.18 added 18 tests for +1.2 s) does not answer whether this file
becomes the gateway pool's longest. **T109's battery must record the gateway package's own wall
clock, not only the lane total**, or the 45 s of headroom is being spent without a meter.

## Independent test criteria

| Story | Green when |
|---|---|
| **US1** | a watcher receives exactly one `online` when a co-member connects, on one instance and across two, with three shared channels still producing one frame |
| **US2** | one `offline` after the window and never before; a reconnect inside it — early or late, to either instance — produces nothing at all; two simultaneous last-closes produce one frame |
| **US3** | a non-sharer, a private-channel non-member and a cross-tenant user each receive nothing **in a run where a co-member receives** |
| **US4** | with Redis down the socket opens and messages deliver, one `presence.failed` is logged, and the next transition publishes after restore |

## Implementation strategy

**MVP is Phase 1 + Phase 2 + Phase 3 (US1).** At that point `presence.changed` has a producer for
the first time since chapter 1.3, delivery is scoped by the subscription topology, and the
duplicate is already handled. FR-RTM-06's grace period is not yet real, so the chapter's clause
set is incomplete — the MVP is a demonstrable increment, not a shippable chapter.

**Do not stop analysing on falling yield.** Chapter 3.17 ran sixteen analyse passes for 20
CRITICALs; 3.16 ran fifteen for 8, and its pass 12 recommended stopping while passes 13, 14 and 15
each found one. Yield measures the questions asked, not the defects present.
