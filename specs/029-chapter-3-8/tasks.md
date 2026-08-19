# Tasks: Tutorial Chapter 3.8 — "Limits you can see coming"

**Feature**: `specs/029-chapter-3-8` | **Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)

**Deliverable**: a limiter whose headers arrive before the refusal does, two
failure directions from one mechanism, and the email transport chapter 3.6 left
owed — which turns out to be the outbox pattern for the third time.

## Format: `[ID] [P?] [Story] Description`

- **[P]** — parallelisable: different file, no dependency on an incomplete task
- **[US1] [US2] [US3] [US4]** — the user story from spec.md this task serves
- Setup, Foundational, Verification, Publication and Close-out tasks carry no
  story label
- **A lettered id** (`T031a`) is a task inserted by an `/speckit-analyze` pass,
  numbered against the task it belongs beside. It may run *before* its base task
  where it is a prerequisite — `T031a` through `T031c` all precede `T031`. The
  letters ascend in execution order; the base number only says which task they
  cluster with

## Path Conventions

Platform paths are relative to `relay-platform/`, tutorial paths to
`relay-tutorial/`, spec paths to `specs/029-chapter-3-8/`.

---

## Phase 1: Setup & baseline

- [ ] T001 Record provenance in `specs/029-chapter-3-8/baseline.txt`: the submodule commits and tags this chapter starts from, confirming `relay-platform` is at `part3-ch7` and both parent pins match their submodule HEADs
- [ ] T002 Record the pre-change platform baseline in `specs/029-chapter-3-8/baseline.txt` — unit and integration counts per package, the coverage figures, every per-file ratchet in force, and the exit code of each gate rather than a grep over its output. Chapter 3.7 finished on 198 unit, 191 integration, 380 coverage
- [ ] T003 [P] Record the site baseline in `specs/029-chapter-3-8/baseline.txt`: `pnpm lint`, `pnpm build`, `pnpm check:docs` and `pnpm check:fences` in `relay-tutorial/`, with the fence and locale counts the chain reports
- [ ] T004 **Run the integration lane three times and record every failure** in `specs/029-chapter-3-8/baseline.txt`. Chapter 3.7 found one pre-existing failure at its baseline and four more during twenty runs, every one a test asserting a local fact about a global operation. This chapter adds a shared counter and a shared mail server, so the class is live before a line is written
- [ ] T004a **Count the failed authentications the lane already produces**, per minute and in total, and record it in `specs/029-chapter-3-8/baseline.txt` beside the threshold this chapter proposes (10/min/IP). The api integration suites assert `401` or `403` 26 times from `127.0.0.1` in about 110 seconds; only the 401s count, so **measure rather than infer — a count of assertions is not a count of requests**, which is the difference chapter 3.7's sweep fault turned on (SC-012, research R15)
- [ ] T005 Separate any failure T004 finds from this chapter's work before starting, and fix it forward with its own commit. A lane with two intermittent failures cannot measure either

**Checkpoint**: the starting numbers exist, and the lane is green for a known reason rather than an assumed one.

---

## Phase 2: Foundational — the arithmetic and the policy

**Blocking.** Everything in US1 and US2 depends on these. All pure or schema-only, nothing observable yet.

- [ ] T006 [P] Write `services/api/src/limits/bucket.test.ts` first: the fixed-window arithmetic, including the window-start floor, the reset time derived from the window rather than stored, and **the burst across a boundary** — a test that documents research R1's accepted cost rather than a comment claiming it
- [ ] T006a [P] Add the three edge cases from spec.md to `services/api/src/limits/bucket.test.ts`, each named in the test title: **a counter that has never been written** returns a full allowance rather than an empty one (this is also the `INCR`-returns-1 path where `EXPIRE` is set); **a limit lowered mid-window** yields neither a negative `Remaining` nor a `Reset` in the past; and **the reset is a pure function of the window**, which is what closes the clock-skew case by construction rather than by agreement between instances
- [ ] T007 Write `services/api/src/limits/bucket.ts` to pass T006 — pure functions only, no store, no clock passed implicitly. `bucket.ts` and `fallback.ts` are the pure half for the same reason chapter 3.7 split `resume.ts`: a filter written inline in the orchestration cannot be reached by a unit test
- [ ] T008 [P] Write `services/api/src/limits/fallback.test.ts`: the in-process counter, the key cap, and **that reaching the cap stops admitting new keys rather than evicting** (data-model). Eviction on a map keyed by attacker-controlled input is a policy the attacker drives
- [ ] T009 Write `services/api/src/limits/fallback.ts` to pass T008
- [ ] T010 Write `services/api/migrations/0008_limit_policy.sql`: three nullable integer columns on `environments` with non-negative checks. **Null means "use the default" and is not zero** — refuse-everything must stay expressible, so the absent state and the zero state cannot share a representation
- [ ] T011 Add the three columns to `services/api/src/db/schema.ts` with a comment recording why they are nullable, and a read in `services/api/src/db/repository.ts` that resolves null to the documented default at read time
- [ ] T011a Assert the override actually overrides, in `services/api/src/limits/limits.itest.ts`: set an environment's `rest_limit_per_minute` to 2 and confirm the third request is refused while a second environment on the default is untouched (FR-007). **Three nullable columns nothing reads would pass every other task in this phase**
- [ ] T012 Add `ioredis` to `services/api/package.json` and write `services/api/src/limits/store.ts`: `INCR`, and `EXPIRE` only when the increment returns 1. Two commands, no Lua — research R1's second reason for the fixed window

**Checkpoint**: the arithmetic is proven, the policy is stored, and nothing has been limited yet.

---

## Phase 3: User Story 1 — A developer can see the limit before hitting it (Priority: P1) 🎯 MVP

**Goal**: every limited response carries the three headers, and the refusal says how long to wait.

**Independent test**: quickstart V1 and V2 — the headers count down across successful responses, the refusal is a `429` with `Retry-After`, and honouring that interval is sufficient to recover.

- [ ] T013 [US1] Write `services/api/src/limits/limits.itest.ts` and **watch it fail**: headers on a 200, `Remaining` decreasing, the 429 with `Retry-After`, and recovery after the interval. A regression test nobody has seen fail is a regression test nobody has checked
- [ ] T014 [US1] Write `services/api/src/limits/rate-limit.middleware.ts` — middleware, not a guard, for chapter 3.2's reason (Nest builds request-scoped providers before the enhancer chain) and one of its own: FR-002 needs a header on a response the handler has not produced yet
- [ ] T015 [US1] Wire it into `services/api/src/app.module.ts` **after** `AuthenticateMiddleware`. The order is forced: the limiter counts per environment and the environment comes from the credential
- [ ] T016 [US1] Exempt the internal service seam in `services/api/src/limits/rate-limit.middleware.ts` (FR-009) **with its own test**. A limiter that throttles the dispatcher turns one busy customer's webhook backlog into a stall for every customer — the failure FR-WHK-05 forbids
- [ ] T017 [US1] Add the two-environments-independent test to `services/api/src/limits/limits.itest.ts` (SC-003, quickstart V4). A shared counter is a cross-tenant fault of a new kind: one tenant's traffic refusing another's
- [ ] T018 [US1] Add the counting-unit test required by FR-008 to `services/api/src/limits/limits.itest.ts` — a request carrying more than one message, asserted against whichever unit the chapter names. **Single-message traffic cannot verify either choice**, which is why the spec's first wording of FR-008 was rewritten at validation

- [ ] T018a [US1] Assert FR-036 in `services/api/src/limits/limits.itest.ts`: a request carrying ten messages decrements the request limit by one and the send limit by ten; the headers report **whichever has fewer remaining**; and the refusal's message names which of the two was reached (research R11). This is the case FR-008 was rewritten to force — on single-message traffic the two limiters are indistinguishable

**Checkpoint**: a developer can build against the limiter. MVP reached.

---

## Phase 4: User Story 1 — the error envelope's fourth field

**Ordered here on purpose**: Phase 3 ships the `429` body, and shipping a three-field body then widening it would mean the chapter's own fences disagreeing across two sections.

- [ ] T019 [US1] Add `request_id` to the error frame in `packages/protocol/src/frames.ts` and delete the comment promising it "joins in Part 2, when a gateway exists to mint one" — a gateway exists and has since Part 2 (research R5)
- [ ] T020 [US1] Add `request_id` to `services/api/src/protocol-error.filter.ts`, threading the id the `RequestContextMiddleware` already mints for `X-Request-Id`
- [ ] T021 [P] [US1] Add `request_id` to the 404 shape in `packages/service-kit/src/index.ts`
- [ ] T022 [US1] Fix every construction site the `strictObject` change breaks. The compiler finds them, which is what `strictObject` is for; record how many there were in `specs/029-chapter-3-8/baseline.txt`. **`services/gateway/src/session.ts`'s `sendError` is one of them and has no id to supply** — T031b is where it gets one, so either order this after T031c or land the two together

- [ ] T023 [US1] Assert the fourth field on a 404, a 401 and the 429 in `services/api/src/limits/limits.itest.ts` (quickstart V3) — **everywhere, not only on the rate-limit error**. Four fields on one status and three on the others is worse than either consistent answer

**Checkpoint**: constitution V's error envelope is four fields for the first time since chapter 1.3.

---

## Phase 5: User Story 2 — A cache outage does not become an outage, or a security hole (Priority: P2)

**Goal**: the tenant limiter fails open, the auth limiter does not, and both are demonstrated in the same outage.

**Independent test**: quickstart V6 — stop Redis, serve tenant traffic, still refuse failed logins past the threshold, and resume counting when it returns.

- [ ] T024 [US2] Make the tenant limiter allow the request when the store is unreachable (FR-010), with the test in `services/api/src/limits/limits.itest.ts` driving a real unreachable store rather than a mock that throws
- [ ] T025 [US2] Implement the degraded header shape in `services/api/src/limits/rate-limit.middleware.ts`: `X-RateLimit-Limit` only, `Remaining` and `Reset` **absent** (research R6). Not `-1` — a client that does not know the sentinel parses it as a number and concludes it is over its limit
- [ ] T025a [US2] Assert the degraded header shape in `services/api/src/limits/limits.itest.ts` with the store unreachable: `X-RateLimit-Limit` present, `X-RateLimit-Remaining` and `X-RateLimit-Reset` **absent** (FR-014). FR-014 was rewritten during spec validation because its first wording forbade a state of mind; an implementation task with no assertion would leave it in the same condition
- [ ] T025b [US2] Read the auth threshold from `RELAY_AUTH_FAILURES_PER_MINUTE` in `services/api/src/limits/fallback.ts` (or wherever the threshold is resolved), defaulting to 10. **The default enforces** — chapter 3.6's `RELAY_DISABLE_SWEEP` comment states the rule: a flag whose default disabled a requirement would be a requirement nobody had built (research R15)
- [ ] T025c [US2] Raise the threshold in the suites that deliberately submit bad credentials, and **lower** it in `services/api/src/limits/limits.itest.ts`, which is the only way to test a threshold. Any suite that needs headroom asks for it explicitly and visibly, rather than the default being chosen to suit the suite
- [ ] T026 [US2] Count failed authentication per source IP in `services/api/src/auth/authenticate.middleware.ts` (FR-012). It goes here and not in the later middleware because a request that fails authentication never reaches one
- [ ] T027 [US2] Wire `fallback.ts` in so the auth limiter does not fail open (FR-011), and add the test that submits failed attempts past the threshold **with Redis stopped**
- [ ] T028 [US2] Assert in `services/api/src/limits/limits.itest.ts` that the refusal is indistinguishable from a wrong-credential refusal to the caller (contract). A limiter that answers differently for a valid credential it refused is an oracle
- [ ] T029 [US2] Add the rate-limited degradation log line in `services/api/src/limits/rate-limit.middleware.ts` (FR-013), carrying no credential. **Rate-limited at the logger**: a Redis outage under load emits one line per request otherwise, which is how one outage becomes two
- [ ] T030 [US2] Assert in `services/api/src/limits/limits.itest.ts` that counting resumes with no operator action once the store returns (FR-015)
- [ ] T030a [US2] Add the client address to the internal authentication request in `packages/protocol/src/internal.ts`, forward it from `services/gateway/src/session.ts`, and count against it in `services/api/src/auth/authenticate.middleware.ts` (FR-039, research R14). **The api currently sees the gateway's address**, so every customer's failed handshakes share one counter and one attacker exhausts a threshold that then refuses everybody
- [ ] T030b [US2] Assert in `services/api/src/limits/limits.itest.ts` that ten failed handshakes from ten client addresses count as ten addresses, not as ten failures by the gateway (SC-011). Exemption from customer limits (FR-009) must not exempt a call from saying whose failure it carried — the same request is trusted enough not to be throttled and not trusted to be the origin

**Checkpoint**: the chapter's argument is code, and both directions are demonstrated in one outage.

---

## Phase 6: User Story 1 — the gateway's two limits

- [ ] T031a [US1] Carry the environment's connect and send limits on the internal authentication response — `packages/protocol/src/internal.ts` and the api's session controller — and cache them on `Connection` in `services/gateway/src/registry.ts`, beside the `marks` chapter 3.7 put there (FR-037, research R12). **The gateway has no database client and must not gain one**; `registry.ts` says so as a design statement
- [ ] T031b [P] [US1] Write `services/gateway/src/limits.ts` and `services/gateway/src/limits.test.ts` — the gateway's own small counter helper over the `ioredis` client it already has for fan-out. Pure arithmetic reused from the api's shape, unit-tested with no socket and no store, and pinned in `relay-platform/vitest.coverage.config.mts`
- [ ] T031c [US1] Add `request_id` to `sendError` in `services/gateway/src/session.ts` (FR-038, research R13): minted per answered frame, the connection's own id where no frame was being answered. **The gateway mints no ids today** — `sendError` builds three fields and `newRequestId` is already exported by `@relay/service-kit`
- [ ] T031 [US1] Refuse an over-limit handshake with an HTTP `429` and `Retry-After` **during the upgrade** in `services/gateway/src/session.ts`, before `wss.handleUpgrade` — deliberately unlike the 4001 path, which completes the handshake by design because a close code is what EIR-WS-05 wants for a bad token (research R7)
- [ ] T032 [US1] Add the test to `services/gateway/src/session.test.ts` that already-open sockets are unaffected by an establishment refusal (FR-005)
- [ ] T033 [US1] Emit an `error` frame carrying `rate_limited` for an over-limit frame in `services/gateway/src/session.ts`, and **keep the connection open** (FR-004). Closing it would make the client reconnect, which costs a handshake and consumes the establishment allowance — a limiter that punishes the limited into hitting a second limit
- [ ] T034 [US1] Assert in `services/gateway/src/session.test.ts` that **close code 4008 is still emitted by nothing** (quickstart V7). It reads "quota exhausted", there is no quota yet, and using it because it was there would collapse the distinction the chapter is built on

- [ ] T034a [US1] Assert in `services/gateway/src/session.test.ts` that a **configured** (non-default) connect limit is enforced on the socket (SC-011, FR-037), and that a limit changed while a socket is open does not apply to that socket until it reconnects — the consequence R12 accepted, asserted so it is a property rather than a surprise

**Checkpoint**: `rate_limited` is emitted for the first time since chapter 1.3 declared it, and 4008 still is not.

---

## Phase 7: Verification of the limiter half

**Runs before the transport**, so the limiter is a complete, shippable chapter on its own if Phase 10's measurement says it should be.

- [ ] T035 Run both lanes and coverage; confirm every pre-existing suite passes unchanged in substance and record the counts (SC-006). `bucket.ts` and `fallback.ts` are pure and should reach 100% branches — if they do not, the missing branch is a case the tests have not thought of
- [ ] T036 Raise the per-file ratchets in `relay-platform/vitest.coverage.config.mts` for every new file to what the work achieves. A ratchet left at its default is a ratchet that has not started
- [ ] T037 **Commit before running the battery.** Its revert step is `git checkout --`, which silently discarded an uncommitted correction during chapter 3.6 and failed the byte-identical check against the previous run's hashes
- [ ] T038 Run the sabotage battery per quickstart V10 — five mutations, each reverted and the file verified byte-identical by `md5sum`, recording which test failed for each (SC-007)
- [ ] T039 **The third mutation is the one that matters**: make the auth limiter fail open. Research R3's decision is a prohibition with no line of code behind it, and chapter 3.7 shipped its central decision untested until a mutation said so — and found that its own out-of-order test had never exercised the mechanism it was named for
- [ ] T040 Capture the limiter transcripts into `specs/029-chapter-3-8/captured-output.md`: T013's failure before the fix, the headers on a 200, the 429 with its four-field body, the V6 outage in both directions, and the battery

**Checkpoint**: the limiter half is finished, verified and independently publishable.

---

## Phase 8: User Story 3 — An organisation is told its endpoint was switched off (Priority: P2)

**Last on purpose, and separable.** It shares no file with the limiter except `repository.ts` and `package.json`. See Phase 10's gate.

**Goal**: FR-WHK-07 stops being half-delivered.

**Independent test**: quickstart V9 — drive an endpoint to disablement, read the message Mailpit received, confirm no secret and `delivered_at` set only after acceptance.

- [ ] T041 Add Mailpit to `relay-platform/compose.yaml` and `nodemailer` to `services/api/package.json`, with the constitution VII justification from research R9 written where a reader will find it. **Off-default ports** — `18025` HTTP and `11025` SMTP — matching the `15432`/`16379`/`14222` convention every other store follows, so the lane cannot collide with a developer's own containers
- [ ] T042 [P] [US3] Write `services/api/src/notifications/mailer.test.ts`: the message body's contents, and **that it carries no signing secret, API key or credential** (FR-021)
- [ ] T043 [US3] Write `services/api/src/notifications/mailer.ts` to pass T042
- [ ] T044 [US3] Add the claim query to `services/api/src/db/repository.ts`: `delivered_at IS NULL`, oldest first, `FOR UPDATE SKIP LOCKED`, **taking an explicit limit**. Chapter 3.7's baseline found four suites broken by tests asserting local facts about global operations, and this is another global operation
- [ ] T045 [US3] Write `services/api/src/notifications/notification-relay.ts` — claim, send, mark, with the mark **in the `finally`** for chapter 3.3's reason: whatever went wrong with row N+1, rows 1..N really did go out
- [ ] T046 [US3] Resolve recipients at send time in `services/api/src/notifications/notification-relay.ts` from the row's `organisation_id` (FR-022), not from the endpoint's current owner. Chapter 3.6 denormalised that column with the reason written down and this is the first code to depend on it
- [ ] T047 [US3] Handle the unaddressable case as a real branch with a log line and a test (FR-023) — `humans.email` is **nullable**, so an organisation whose admins all lack an address is a case, not a defensive `if`
- [ ] T048 [US3] Write `services/api/src/notifications/notifications.itest.ts` asserting on what Mailpit **received** via its HTTP API, not on what the sender passed. FR-021 is about the contents of an email and only the received message can prove it
- [ ] T049 [US3] Test the failure and repeat branches in `services/api/src/notifications/notifications.itest.ts`: a failed send leaves `delivered_at` null and the row claimable (FR-018); a delivered row is not sent twice (FR-019); an endpoint **disabled, re-enabled and disabled again** produces two rows and two emails with neither suppressing the other (spec edge case); and with Mailpit stopped, message delivery, the API and webhook dispatch are all unaffected (FR-024)
- [ ] T050 [US3] Confirm in `services/api/src/notifications/notifications.itest.ts` that the rows chapter 3.6 accumulated drain on the first run (FR-020) — **with no special handling**, because they are undelivered work by the claim predicate's own definition. If they need special handling, the shape is wrong
- [ ] T051 [US3] Wire `services/api/src/notifications/notifications.module.ts` into the app, and note in the chapter that flapping endpoints send one email per flap — out of scope to solve, named so it is a known shape rather than a surprise

**Checkpoint**: `delivered_at` is set for the first time, and the backlog is gone.

---

## Phase 9: User Story 4 — Part 3 absorbs another chapter (Priority: P3)

Mostly done during `/speckit-specify`. This phase verifies rather than performs.

- [ ] T052 [P] [US4] Confirm `docs/07-tutorial-plan.md` and `relay-tutorial/lib/tutorial.ts` agree: quotas 3.9, gauntlet 3.10 (FR-033)
- [ ] T053 [P] [US4] Run quickstart V11's sweep across `docs/`, both locales' pages and the platform's source; confirm every hit names what it claims to name (FR-034, SC-009)
- [ ] T054 [US4] Confirm **zero** forward chapter references in live source under `services/*/src` and `scripts/` (FR-035), and record in `specs/029-chapter-3-8/baseline.txt` that this renumbering cost no fence amendment — the first evidence chapter 3.7's rule paid for itself, or the first evidence it did not

---

## Phase 10: The chapter, in English — and the size gate

- [ ] T055 [P] Write `relay-tutorial/app/(en)/part-3/chapter-08/limits-you-can-see-coming/figures.ts` — the two failure directions, the middleware chain's two limiter positions, and the fixed window's boundary burst
- [ ] T056 Write the limiter sections of `relay-tutorial/app/(en)/part-3/chapter-08/limits-you-can-see-coming/page.mdx`: the vocabulary declared in 1.3 and never enforced, the headers-on-success requirement (FR-027), the two failure directions and why they differ (FR-026), and why 4008 stays unused
- [ ] T056a Add the section to `relay-tutorial/app/(en)/part-3/chapter-08/limits-you-can-see-coming/page.mdx` on the two things the gateway cannot do: it has no database, so its limits ride the authentication response and are fixed for the life of a socket (R12); and it is trusted not to be throttled while not being trusted to be the origin of a failed login (R14). One request, two opposite kinds of trust
- [ ] T057 Add the section on what this chapter does not deliver and why to `relay-tutorial/app/(en)/part-3/chapter-08/limits-you-can-see-coming/page.mdx` (FR-029) — quotas need metering that arrives with Part 4, and naming the dependency is the difference between a scope decision and a silent gap
- [ ] T058 **THE SIZE GATE. Measure the prose word count and fence count of the limiter sections alone**, and record both in `specs/029-chapter-3-8/battery.txt` against research R10's estimate of **28** fences for this half and the 2,000–4,000 bound. R10's first estimate was 23; three analysis passes added five, every one a consequence of the gateway not being the api
- [ ] T059 **Decide, with the number in hand, whether the transport is sections of this chapter or a chapter of its own.** R10 recommends the split; the scope decision said one chapter. If the limiter half alone is already near the bound, the transport's prose becomes chapter 3.9 and quotas move to 3.10 — the code from Phase 8 ships either way, because it closes FR-WHK-07 regardless of which chapter explains it. Record the decision and the number that drove it
- [ ] T060 If the transport stays: add its sections to `relay-tutorial/app/(en)/part-3/chapter-08/limits-you-can-see-coming/page.mdx` — the outbox for the third time, the table that already had the right shape, and Mailpit's justification against constitution VII
- [ ] T061 Generate every fence from the real files rather than typing them, and confirm `pnpm check:fences` replays the chain onto `relay-platform` (FR-031). **Six are amendments to files fenced in earlier chapters**, and their chains end in six different places: `packages/protocol/src/frames.ts` (1.3), `packages/service-kit/src/index.ts` (1.4), `services/api/src/protocol-error.filter.ts` (last 3.2), `packages/protocol/src/internal.ts` (last 3.6), `services/gateway/src/registry.ts` (3.7) and `services/gateway/src/session.ts` (3.7)
- [ ] T061a **An amendment diff's base is the chain's end state, not the latest tag.** `git diff part3-ch7..HEAD` produces a pre-image that matches nothing for `frames.ts`, whose chain ends in Part 1 — the trap chapter 3.7 walked into when it regenerated `consumer.itest.ts` from the wrong base and the checker reported `hunk pre-image matched 0 times`. Extract each file's chain state from the last chapter that fences it, then diff against the working tree
- [ ] T062 Measure the battery on the published page and record it in `specs/029-chapter-3-8/battery.txt`, with the final prose word count against the bound and the SKIP AHEAD naming `part3-ch8`
- [ ] T063 Traceability: confirm every `FR-*`/`NFR-*`/`ADR-*` the chapter cites resolves in `docs/` or the constitution. Chapter 3.6 leaked fourteen feature-local identifiers and chapter 3.7 caught six of its own about to be fenced — **check the source comments this chapter adds, not only its prose**

---

## Phase 11: Publication in both locales

- [ ] T064 Translate the chapter to `relay-tutorial/app/(vi)/vi/part-3/chapter-08/limits-you-can-see-coming/page.mdx`, splitting prose from fences mechanically before translating anything and leaving every fence byte-identical (FR-032, translate-mdx §2.4)
- [ ] T065 [P] Translate `relay-tutorial/app/(vi)/vi/part-3/chapter-08/limits-you-can-see-coming/figures.ts` — mermaid labels only; identifiers, header names and file paths stay English
- [ ] T066 Verify the JSX box tags balance in both locales before building — chapter 3.6's translation dropped a `<Why>` opening tag and the build error named a line 200 lines away
- [ ] T067 Set 3.8 published in `relay-tutorial/lib/tutorial.ts` with `translatedIn: ["vi"]`
- [ ] T068 Verify both routes: 200, the reading shell present, and the figures rendering as **SVG in a headless browser** with real viewBoxes and text nodes (SC-008) — a page that returns 200 is not a page that is laid out, and 3.5 shipped three blank diagrams past a passing build
- [ ] T069 Run `pnpm check:fences` and confirm the Vietnamese fences mirror the English byte for byte and the locale count has risen

---

## Phase 12: Close-out

- [ ] T070 Run quickstart V0–V11 end to end from `specs/029-chapter-3-8/quickstart.md`, reading exit codes rather than grepping output, and **correct the quickstart itself wherever a step's stated expectation did not survive contact**. Four of chapter 3.7's ten steps carried claims its own work disproved
- [ ] T071 Scan `specs/029-chapter-3-8/captured-output.md` and both published pages for leaked credentials, recording the patterns searched rather than the conclusion alone. This chapter sends email, so add the mail transcripts to the scanned set
- [ ] T072 Write `specs/029-chapter-3-8/chapter-notes.md` from what happened rather than what was planned, including T058's numbers, T059's decision, and anything the battery contradicted
- [ ] T073 Fix forward any defect this chapter exposes in an earlier chapter, in every locale that chapter has, and record it in `specs/029-chapter-3-8/chapter-notes.md`
- [ ] T074 Amend `docs/07-tutorial-plan.md` if T059 moved this chapter's scope, and confirm the Part 3 numbering it carries still matches `relay-tutorial/lib/tutorial.ts`
- [ ] T075 Tag `relay-platform` as `part3-ch8` at the chapter-end commit, because the chapter's SKIP AHEAD tells readers that tag exists — 3.5 published that claim before the tag was created

---

## Dependencies & Execution Order

### Phase dependencies

- **Phase 1 → Phase 2**: the baseline is measured before anything changes, and T004's three runs decide whether the lane can be trusted to report this chapter's own faults
- **T006 → T007**, **T008 → T009**, **T013 → T014**: the test is written, watched to fail, and only then made to pass. Reversing that order produces a test that has never been checked
- **Phase 2 → Phase 3**: the middleware needs arithmetic and policy to exist
- **Phase 3 → Phase 4**: the 429 body is shipped in Phase 3 and widened in Phase 4; doing it the other way round means the chapter's fences disagree across two sections
- **Phase 4 → Phase 5**: degradation needs a mechanism to degrade
- **Phase 7 → Phase 8**: the limiter half is verified before the transport starts, so it is publishable alone if T059 says so
- **Phase 8 → Phase 10**: the transport's prose cannot be written before the transport
- **T058 → T059 → T060**: the gate measures, then decides, then writes. Writing first would make the measurement advisory

### The phase order deviates from priority order, on purpose

US1's Phase 6 (the gateway) sits after US2's Phase 5. The reason is the plan's:
the failure directions are the chapter's argument and they need the REST mechanism
to exist before they can degrade, while the gateway's two limits are a second
application of a settled decision. US3 is P2 and runs last for the size reason
above, not because it matters least.

### Parallel opportunities

- **Phase 1**: T003 is the tutorial's lane, independent of T002's
- **Phase 2**: T006 and T008 are unit tests in files nothing else touches
- **Phase 4**: T021 touches only `service-kit`
- **Phase 8**: T042 is independent of T044's repository work
- **Phase 9**: T052 and T053 read different trees
- **Phase 10**: T055 (figures) is independent of the prose
- **Phase 11**: T065 (figures) is independent of T064 (page)

---

## Implementation Strategy

**MVP is Phase 3.** With Phases 1–3 the platform enforces a limit and tells a
developer about it before refusing them, which is the whole of FR-RTL-01 through
03 on the REST path. Everything after is the argument, the second surface, and the
debt.

**The real strategy question is T059**, and it is deliberately not answered here.
Research R10 estimates ~35 fences, 28 of them before the transport, against a
2,000–4,000 word bound; chapter 3.5
shipped 39 fences on an estimate of 22 and ran 4,952 words, and chapter 3.6 ran
5,273. Three of the last four Part 3 chapters have gone over.

The phase order is arranged so that decision is taken with a measured number
rather than a predicted one, and so that either answer is cheap: the transport's
code ships in Phase 8 either way, because it closes FR-WHK-07 whether or not this
chapter is the one that explains it.

---

## Notes

**On T004's three runs.** Chapter 3.7 spent four attempts and roughly four hours
getting twenty consecutive clean lane runs, and found four faults doing it — a
sweep with a batch limit, a drain holding a lock, a consumer draining a growing
stream on a fixed budget, and a global `count(*)` compared against itself. All four
were tests asserting a local fact about a global operation, and all four had been
passing on headroom.

This chapter adds a shared counter and a shared mail server. Three runs at the
baseline is not twenty and is not meant to be; it is enough to know whether the
lane is green before this chapter starts changing shared state, so that anything
that goes red later is this chapter's to explain.

**On the sabotage battery's third mutation.** It is listed as its own task (T039)
rather than as a line inside T038 because it is the one most likely to be skipped:
its mechanism is an absence. The auth limiter must not fail open, and there is no
line of code that says so — only a fallback path whose deletion would be silent.
Chapter 3.7's battery found exactly this shape twice: a planned mutation that could
not fail, and a test named after a property it never exercised.
