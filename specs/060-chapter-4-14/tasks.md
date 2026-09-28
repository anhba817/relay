# Tasks: Chapter 4.14 — "Pending, ready, rejected"

**Feature**: 060 · **Input**: [spec.md](./spec.md) · [plan.md](./plan.md) ·
[research.md](./research.md) · [data-model.md](./data-model.md) ·
[contracts/media-state.md](./contracts/media-state.md) · [quickstart.md](./quickstart.md)

## Terminology, fixed

The **frame** is the wire object a client receives; **publishing** is the act; the
**transition** is the state change that causes it. "Event" is not used for any of the three.

## Format: `[ID] [P?] [Story] Description`

`[P]` = different file, no dependency on an incomplete task. `[US1]`/`[US2]`/`[US3]` map to the
spec's three stories; Setup, Foundational, Gates, Chapter and Record phases carry no story label.

## Path Conventions

`relay-platform/` for the platform, `relay-tutorial/` for the chapter, `specs/060-chapter-4-14/`
for the record. Bring the stack up with `RELAY_POSTGRES_PORT=15432` — this machine's own
Postgres holds 5432.

## Tests are not optional here

Constitution VI requires test-verified delivery and names tenant isolation at 100% branch
coverage. Every behaviour task below has a test task that is **run red first**, because this
project has a documented record of tests that passed while proving nothing.

---

## Phase 1: Setup — the numbers this chapter is compared against

- [X] T001 Bring the stores up and record what answers: `cd relay-platform && RELAY_POSTGRES_PORT=15432 docker compose up -d --wait`. Seven containers including `clamav`. **Read the counted line, not the exit code.** If NATS comes up unhealthy it **names one unrecoverable stream at a time** (`gaps.md` 058-7) — clear them one at a time; the bulk form was refused by this environment's guard.
- [X] T002 Record the opening `check:fences` figure as an **absolute number**, not a delta. **Measured 2026-09-28: EXIT 0, `291 fenced files replay onto relay-platform across 56 chapters`.** **A clean run prints NO problem line at all** — so the documented `grep 'problem(s)\|replay onto'` matches one alternative and never the other, and there is no printed zero to read. The counted line plus EXIT 0 is what clean looks like. Run it in `relay-tutorial`: the gates live there, and `pnpm` in the wrong repository exits silently and reads as green.
- [X] T003 [P] Record the opening dependency count across every `package.json` in `relay-platform` — **31 entries, 20 third-party, 13 distinct packages** at `part4-ch13`. SC expects this NOT to move: this chapter adds no dependency.
- [X] T004 [P] Record the opening lane state with the composed services **stopped** (`gaps.md` 057-5): `pnpm test`, `pnpm test:integration`, `pnpm coverage`, `pnpm check:errors` (**34 codes, 34 sections**). Then `pnpm test:outsider` with them **up** plus `RELAY_API_URL`, `RELAY_WS_URL`, `RELAY_DEMO_CREDENTIAL` from the seeder — run without those it reports `19 skipped`, which is **a counted line that means nothing ran**.
- [X] T005 [P] Re-measure the lane's media composition rather than trusting the plan's figures, which were taken 2026-09-28: `media_objects` by state, referenced vs unreferenced, and the channels-per-object distribution. The plan read 5,403 / 4,725 unreferenced / N=1 1,545 / N=2 44. **The lane moves between chapters** — 4.13 found `media_objects` had grown 3,005 → 3,078 since its own plan.
- [X] T006 [P] Record the per-channel SUBSCRIBE count from the source, the five ADR-25 names: `fanout.ts` (2 subjects, one call), `presence.ts`, `typing.ts`, `membership.ts`. This is the number R1's decision rests on and **it is a source count, not a load test** — say so.
- [X] T007 Record the opening CI error set per error, uuids normalised, from the most recent run on `main`. **Per error, not per colour** — a colour cannot say whether a run introduced something new, and three chapters running have found a gate whose colour was true and whose meaning was not.

---

## Phase 2: Foundational — the shapes, before anything reads or writes them

**Blocking**: every user story below depends on these. Nothing here is story-specific.

- [X] T008 Read `packages/protocol/src/attachments.ts` end to end before editing it, including the five-readers comment. **The request arm must not change.** Confirm by grep which schemas embed `attachmentSchema` and which embed `forwardedAttachmentSchema` — the question that finds them is *what is this schema embedded in*, one level up from the name.
- [X] T009 Add `deliveredAttachmentSchema` to `packages/protocol/src/attachments.ts` — the url arm unchanged, the media arm gaining **required** `state`. Required, not optional, per the precedent `frames.ts:89` states in its own words: *"a caller may send none, and a payload the platform BUILDS must always say."* Required is what makes the compiler name every construction site.
- [X] T009a Point `messageSchema.attachments` at the delivered shape in `packages/protocol/src/frames.ts:46`. **This is the edit the first version of this plan missed** — `messageSchema` is the outbound contract, not a request shape, and it shared `attachmentSchema` with three request doors. Run `tsc --noEmit` across the api and the gateway; the list it prints is the real scope of US1.
- [X] T009a1 **TWO DIFFERENT THINGS ARE TYPED `Attachment[]` AND ONLY ONE OF THEM CHANGES** (analysis pass 2). **The column cast stays**: `repository.ts:4817`, `:5610`, `:5918` are `sql<Attachment[] | null>` over `messages.attachments`, which holds **what the sender declared** — no state, by FR-002's design. Changing those would make the type a false claim about stored bytes. **The constructed Message changes**: the sites that assemble a message for a door. Write the two lists separately before editing either, and put them in `specs/060-chapter-4-14/doors.txt` beside T019's output.
- [X] T009a2 **Expect `tsc` to name a gateway site, and do not read it as a surprise.** `services/gateway/src/session.ts:1628` builds a message for the socket ack from `committed.attachments`. The gateway forwards rather than judges, so the likely answer is that it keeps forwarding — but it is a site the compiler will name and no earlier version of this plan anticipated a gateway-side change at all.
- [X] T009b Put `deliveredAttachmentSchema` **ahead of** `attachmentSchema` in `forwardedAttachmentSchema`'s union in `packages/protocol/src/attachments.ts`, leaving the loose arm last. A delivered value already parses today by falling through to `z.looseObject({type})`, so this changes types rather than acceptance — but a forwarded value matching a typed arm is what FR-018d's escape hatch was meant to be spared for. **Do not remove the `attachmentSchema` arm**: an envelope written by the previous binary has no `state` and must keep parsing, and the cost of that being wrong is `message.term()`.
- [X] T010 [P] Write the red-first test for T009 in `packages/protocol/src/attachments.test.ts`: a delivery attachment **without** `state` parses; one with each of the three values parses; one with a fourth value is refused. Run it against the pre-T009 schema and record which assertions fail.
- [X] T011 [P] Write the red-first test in `packages/protocol/src/attachments.test.ts` that **all three request doors** still refuse `state` — `messages.schema.ts:40`, `frames.ts:94` (`messageSendSchema`) and `internal.ts:35`. They share `attachmentSchema`, whose `strictObject` refuses it already, so **no refusal is written**; the test pins the property against a future widening. Name all three, because a test that covers one door and claims three is the shape this project has paid for seven times.
- [X] T011a [P] Write the red-first test in `packages/protocol/src/attachments.test.ts` that a **durable envelope with no `state`** still parses through `forwardedAttachmentSchema`. This is the rolling-deploy case and the one whose failure is silent and expensive.
- [X] T012 Add the third arm `kind: "media"` to `revisionFabricSchema` in `packages/protocol/src/revision.ts`, `strictObject`, carrying `media_id`, `channel` and a **two-value** state (`ready | rejected`). No `environment` field — a channel id identifies its tenant transitively, which is the reason that file already gives for its other two arms.
- [X] T013 **Amend the module comment in `revision.ts` to say what the subject now carries.** It is named `revision:` and will carry a thing that is not a message revision; the contract becomes *"something changed about what this channel's messages show"*. A name that has quietly widened is worse than one that has widened on the record.
- [X] T012a **Sweep every site that reaches into a revision's message — there are eight in production and six in tests, not one.** Measured rather than listed, with `grep -rn 'revision\.message\|revision\.data\.message\|revision\.kind'`:

        services/api/src/fanout/publisher.ts     135, 142, 143   subject + log fields
        services/gateway/src/fanout.ts           108, 145, 153   ROUTING + the gateway's own publisher
        services/gateway/src/session.ts          400, 401, 402   the two-way ternary
        services/gateway/src/session.test.ts     163, 164        a test HARNESS that routes revisions
        services/gateway/src/fanout.itest.ts     241, 263, 279   263 and 279 carry no `kind` guard

  **Analysis pass 4 fixed one of these and pass 5's sweep found the rest.** `revision.message.channel` is the subject derivation, the routing key **and** the log field, in two services. The media arm has none of it: its channel is a direct field and it has no message id to log. `tsc` names every production site; **it does not name the intent**, which is that a media transition has no message and logging `undefined` reads as a missing value rather than an inapplicable one. One discriminated switch per site.
- [X] T012a1 [P] **`fanout.itest.ts:263` and `:279` read `revision.message.seq` with no `kind` guard**, where `:241` guards with `revision.kind === "updated" &&`. Both break on a third arm. Repair them **and then ask what each asserted** — this is D3's class in a second file, and 045's rule is that the fixture is half the task.
- [X] T012a2 [P] **`session.test.ts:163-164` is a test harness, not an assertion.** It routes revisions by `revision.message.channel` to stand in for the fabric. A harness that cannot carry the new arm makes every test downstream of it silently unable to exercise the media path — which is worse than a red test, because it is a green one.
- [X] T012b [P] Write the red-first test for T012a in `services/api/src/fanout/publisher.test.ts` — the media arm publishes to `revision:{channel}` taken from **its own** `channel` field, and a Redis failure on that arm logs without throwing. **`publishRevision` never rejects by contract**, so a test that only checks the happy path cannot tell a published frame from a swallowed one; assert the subject the client received.
- [X] T014 [P] Write the red-first test for T012 in `packages/protocol/src/revision.test.ts`: the new arm parses, an unknown `kind` is refused, an unknown key inside the arm is refused, and `state: "pending"` is refused — **the producer cannot emit it**, so a three-value enum here would be a state nothing can reach.
- [X] T015 Add the client frame to `packages/protocol/src/frames.ts` per [contracts §2](./contracts/media-state.md). Name it deliberately — see T016 — and put it in the same union the other frames live in.
- [X] T016 **Decide the frame name and record the decision** (plan open question 3), **knowing that both frames can describe one message** — analysis pass 2's finding. The edit path already emits `message.updated` and already carries attachments (`messages.controller.ts:361,381`), so an edited message with a media attachment produces `message.updated` today and `media.updated` after this chapter, on the same message, in the same `switch`. `media.updated` matches FR-MED-07's wording and is one letter from `message.updated` in a codebase where both land in the same `switch`. Either name it something further away or state why the collision is acceptable; do not leave it defaulted.
- [X] T017 [P] Write the red-first test for the frame in `packages/protocol/src/frames.test.ts`, including that it carries **no** `reason` field (FR-010) and no message id.
- [X] T018 Run `pnpm --filter @relay/protocol build` then `tsc --noEmit` across the workspace. The protocol package is consumed by every request door and by the gateway; a schema change that compiles in isolation is not the check.

---

## Phase 3: User Story 1 — the state is on the attachment, at every door (P1) 🎯 MVP

**Goal**: every door that serves a message puts the attachment's current state on it, read at
serve time.

**Independent test**: attach a `pending` object, read it back through history and live delivery,
record a verdict, read again — both reflect the change. No event involved.

- [X] T019 [US1] **Derive the set of doors that serve a message with attachments from the code. Do not list them by hand.** Walk `services/api/src` for every handler returning a message and write the result to `specs/060-chapter-4-14/doors.txt`. Every hand-written list of routes, validators or fenced files in this project's history has been wrong in both directions — seven times. Produce the derived set as a file the later tasks and T022 compare against.
- [X] T020 [US1] Read the media state alongside the message on the history read path in `services/api/src/db/repository.ts`, joined, scoped by `environment_id`. One query, not a per-attachment lookup — 4.12 measured 1,042 buffers against 84 for the shape that does not scale.
- [X] T021 [US1] Populate `state` on the delivery attachment wherever the api builds a `Message` — the sites `tsc --noEmit` names at T009a, which include `services/api/src/fanout/publisher.ts` (live delivery), `services/api/src/internal/backfill.controller.ts` (resume) and the send response path, so every door T019 derived agrees.
- [X] T022 [US1] **Assert the derived set against the covered set in both directions** (SC-002), as a test in `services/api/src/media/attachment-state.itest.ts` reading `specs/060-chapter-4-14/doors.txt`: every door T019 found is covered by a test, and every test maps to a door. A door found and not covered fails this task; a test with no door is a test of something that does not exist.
- [X] T023 [P] [US1] Red-first integration test in `services/api/src/media/` — history returns `state: "pending"` for a pending attachment. Run it before T020 and record the failure text.
- [X] T024 [P] [US1] Red-first integration test — after a verdict, the **same** history read returns `ready` with no message rewritten. Assert `messages.attachments` is byte-identical before and after, which is what proves FR-002 rather than asserting the output twice.
- [X] T025 [P] [US1] Red-first integration test in `services/api/src/media/attachment-state.itest.ts` — the send response carries the state for an object attached while `pending`.
- [X] T026 [P] [US1] Red-first integration test in `services/api/src/media/attachment-state.itest.ts` — an object attached when **already** `ready` reports `ready` on every door (FR-009, SC-006). **This is the case no event can ever serve**, and 538 of the lane's 1,589 referenced objects are in it.
- [X] T026a [P] [US1] Red-first integration test in `services/api/src/media/attachment-state.itest.ts` — **the edit response and the resume/backfill path** carry the state (analysis pass 2, D1/D4). Both return a `Message` with attachments and neither was named by the first version of FR-003; resume is the case where a client reconnects holding a stale placeholder, which is exactly when it matters.
- [X] T027 [P] [US1] Red-first integration test in `services/api/src/media/attachment-state.itest.ts` — a `rejected` attachment still returns its message, with the state, rather than the message disappearing (FR-MED-09's record that *something* was sent).
- [X] T027a [US1] **Repair the forged delivery-side fixtures, then re-read what each one asserts.** Six of them, in four files: `services/gateway/src/session.itest.ts` (3), `services/gateway/src/fanout.itest.ts`, `services/api/src/consumer/consumer.itest.ts`, `services/gateway/src/api-client.test.ts`. A required `state` invalidates every forged `Message` carrying a media attachment. **045 paid this exact bill**: adding a required `revisions` to the ack invalidated two forged sample frames three chapters away, and **the tests asserting the wrong refusal stayed green**. Repairing the fixture is half the task; the other half is asking what the test proved before and whether it still proves it.
- [X] T028 [US1] Confirm the live delivery path still parses envelopes written before this change. Write one by hand with no `state` and push it through the fanout reader — the permissive-reader property is the one that costs `message.term()` when it is wrong.

**Checkpoint**: US1 is independently shippable. A client polling history gets a correct answer
for every object, with no producer built.

---

## Phase 4: User Story 2 — a placeholder resolves without polling (P2)

**Goal**: when an object leaves `pending`, a frame reaches every channel holding a referencing
message.

**Independent test**: subscribe, send with a pending attachment, record a verdict, assert a
frame arrives with no client request in between.

- [X] T029 [US2] **Decide where the publish sits relative to the verdict, and record it** in `specs/060-chapter-4-14/research.md`. **Analysis pass 3 removed the option this task originally posed**: there is no transaction to publish inside. `recordMediaVerdict` issues `UPDATE … WHERE state = 'pending' RETURNING` and, when nothing applies, a follow-up `SELECT`; the controller manages no transaction of its own. The real question is narrower — publish after `applied === true`, and accept that a crash between the UPDATE and the PUBLISH loses one frame, which FR-009's floor already repairs on the client's next read. An outbox row for this frame is available and is almost certainly over-building; say so either way rather than defaulting.
- [X] T030 [US2] **Return `environment_id` from `recordMediaVerdict`** in `services/api/src/db/repository.ts:603`, adding it to the `.returning({ state, objectKey })` list and to the function's return type. **This is analysis pass 3's CRITICAL and it reaches back into a function 4.13 shipped**: the verdict seam is a module-level function on a raw `Db`, outside the tenant-scoped repository, because its caller is a worker and not a tenant — and the worker's principal carries `environmentId: undefined` by design (4.4). Without this value there is no environment to scope the fan-out with. Update `media-verdict.itest.ts` and any unit test asserting the return shape.
- [X] T030a [US2] **Give the fan-out a scoped entry point** taking `(db, environmentId, mediaId)`, beside `recordMediaVerdict` and in the same module-level style, reusing `channelsReferencingMedia`'s existing query body rather than writing a second one. **Do not drop the tenant predicate.** `media_id` is a primary key so an unscoped lookup would return the right rows, and it would be a shared-table read with no tenant predicate — constitution I in the data-access layer, and exactly what `check-lane-scope.py` exists to find. One query body, one predicate, two callers.
- [X] T030b [P] [US2] Red-first test that the scoped entry point **refuses to answer across tenants**: the same `media_id` with the wrong `environment_id` returns an empty channel list, not the object's real channels. This is the arm T046's per-arm probe will try to delete, and 4.12 measured that deleting it turns nothing red unless a test asks this exact question.
- [X] T030c [US2] **Provide `MESSAGE_PUBLISHER` in `InternalModule`** (`services/api/src/internal/internal.module.ts:49`). **This is analysis pass 4's CRITICAL and it is invisible to every gate the lane runs.** `MessagesModule` declares the token and **deliberately does not export it** (`messages.module.ts:98`), and `InternalModule` provides only `DB`, `ANALYTICS_PUBLISHER` and `LOGGER` — so `MediaVerificationController` has nothing to inject and T031 answers `Nest can't resolve dependencies` **on the first request**, after compiling, typechecking and linting clean. **4.10 recorded this exact failure** when `MediaModule` declared a service it did not provide: *"Only a running app asks that question."* Use the same factory and the note this file already carries three times — *"a provider is visible to the module that declares it and to nothing it imports"*.
- [X] T030d [US2] **Decide what closes the second Redis client, and record it.** `MessagePublisherLifecycle` (`OnModuleDestroy`) closes `MessagesModule`'s publisher; a second provider in `InternalModule` leaks its connection on shutdown without an equivalent. Two options: a lifecycle beside the provider, or one shared client. `ANALYTICS_PUBLISHER`'s own note — *"its own publisher, ensuring its own stream"* — is the precedent for a second client being acceptable, **and it was argued rather than assumed**. Do the same here either way.
- [X] T030e [P] [US2] Assert the wiring from a **running** app, not from the types. A test that boots the api and issues one verdict is the only thing that can see a missing provider; `pnpm lint`, `tsc --noEmit` and every unit test pass with T030c absent. This is the control for pass 4's finding and it costs one request.
- [X] T031 [US2] Publish the transition from the verdict seam in `services/api/src/internal/media.controller.ts`, gated on `result.applied` and scoped with the `environment_id` T030 now returns. **The handler is otherwise clean for this**: the 404 and the 422 both return before the publish site, and there is exactly one place before `return` where it belongs. `PublishContext` needs `{requestId, environmentId}` — the environment from T030, and the request id as `req.requestId ?? "unknown"`, which is the fallback `messages.controller.ts:72` already uses. **Do not invent a second fallback string** for the same absent value.
- [X] T031a [US2] **Decide the publish order against `deleteObject` and record it.** For a `rejected` verdict the handler `await`s `deleteObject` before returning. Publishing after it adds a store round trip to the worker's request; publishing before it announces `rejected` while the bytes still exist. Neither is obviously wrong — a client cannot fetch a `rejected` object either way, because FR-MED-08's gate reads the state and not the store — so this is a latency-versus-ordering choice that should be made out loud.
- [X] T032 [US2] Fan out one frame per referencing channel in `services/api/src/internal/media.controller.ts`, using T030a's scoped entry point. An empty list is success (FR-006) and is the **common** path: 4,725 of 5,403 lane objects are unreferenced.
- [X] T033 [US2] Route the third fabric arm to the socket in `services/gateway/src/session.ts:400`. **It is a two-way ternary** — `kind === "updated" ? message.updated : message.deleted` — so a third kind falls to the `deleted` branch. `tsc` stops it because the media arm has no `message`, but **the natural repair is a nested ternary and the right one is a switch**: the media arm delivers a **different frame type**, not a variant of those two. Add an exhaustiveness check so a fourth arm is a compile error rather than a default. **Confirm the buffering skip transfers, and say why rather than inheriting it.** `deliverRevision` skips buffering connections because the backfill carries current state; after US1 the backfill **does** carry the attachment state, so the reasoning holds exactly rather than approximately. State that, because the next arm on this fabric may not have a backfill behind it.
- [X] T034 [P] [US2] Red-first integration test in `services/api/src/media/media-updated.itest.ts` — one referencing channel, one verdict, one frame carrying the media id and `ready`.
- [X] T035 [P] [US2] Red-first integration test in `services/api/src/media/media-updated.itest.ts` — `rejected` produces a frame carrying `rejected` and **no reason** (FR-010).
- [X] T036 [P] [US2] Red-first integration test in `services/api/src/media/media-updated.itest.ts` at **N = 2** — one object referenced from two channels produces two frames, one per channel (SC-003). 44 lane objects are in this shape; a fan-out written for N = 1 is correct on 97% of the lane.
- [X] T037 [P] [US2] Red-first integration test in `services/api/src/media/media-updated.itest.ts` at **N = 0** — a verdict for an unattached object publishes nothing and the verdict still succeeds.
- [X] T038 [P] [US2] Red-first integration test in `services/api/src/media/media-updated.itest.ts` — a **duplicate** verdict on a terminal object publishes nothing (SC-005). Assert on the absence with a quiet window taken **after** a positive control has arrived, never a flat sleep instead of one.
- [X] T039 [P] [US2] Red-first integration test in `services/api/src/media/media-updated.itest.ts` — a tombstoned referencing message contributes no channel (FR-011). **No code is needed for this**: 2,867 tombstoned messages on the lane carry zero attachments because FR-MED-10's unlink already empties the array. The test exists because the property is invisible in the types and one `UPDATE` that forgot to clear attachments would break this path and the delivery gate at once.
- [X] T039a [P] [US2] Red-first integration test in `services/api/src/media/media-updated.itest.ts` — **one object attached by two messages in the SAME channel produces one frame, not two** (spec edge case; Q3). `channelsReferencingMedia` is `selectDistinct` over channels, so the answer follows from the query — assert it anyway, because a client rendering per message must find its own messages by media id and a second frame would be a silent contract change.
- [ ] T039b [US2] **Record the rolling-deploy window, which no artifact names.** An un-upgraded gateway receiving `kind: "media"` fails `revisionFabricSchema.safeParse` and drops the frame with `fanout.invalid_payload`, **logging the subject and not the reason** — `fanout.ts` predicts this exact shape in its own comment for the message path. During a deploy, transitions vanish on old instances and **SC-001 is false in that window**. FR-009's floor repairs it on the client's next read, which is the argument for having the floor; an unstated window is one somebody later reports as a bug. Note also what makes it safe rather than merely survivable: the parser **refuses** an unknown arm instead of guessing, because parsing against both schemas *"would make a malformed revision look like a message"*.
- [ ] T040 [US2] End-to-end in `services/gateway/src/media-updated.itest.ts`: socket subscribed, message sent with a pending attachment, worker verifies, frame arrives — **with no request issued by the client between the send and the frame** (SC-001).

**Checkpoint**: US1 + US2 is the chapter's subject working.

---

## Phase 5: User Story 3 — a client that may not read the channel is not told (P3)

**Goal**: the frame reaches only connections authorised to read a referencing message.

- [X] T041 [US3] Confirm the delivery set is `registry.subscribersOf(channelId)` and that subscription follows membership (`session.ts:593`). **Record the direction**: subscribers ⊆ authorised readers, so the event can under-deliver and never over-deliver (R5).
- [X] T042 [P] [US3] Red-first test in `services/gateway/src/media-updated.itest.ts` — a non-member connection receives no frame for a **private** referencing channel.
- [X] T043 [P] [US3] Red-first test in `services/gateway/src/media-updated.itest.ts` — a connection in another environment receives nothing (constitution I).
- [X] T044 [P] [US3] Test the under-delivery case explicitly in `services/gateway/src/media-updated.itest.ts`: a non-member of a **public** referencing channel is authorised under FR-MED-08 and receives no frame, and learns the state from history instead. **Assert it rather than leaving it undiscovered**, so nobody later "fixes" it by broadcasting wider — which would be the leak.
- [X] T045 [US3] Add an attack to `services/api/src/isolation/gauntlet.itest.ts` for the new path. The gauntlet is the suite constitution VI names as gating releases, and 4.12 measured that it reports nothing when a media tenancy scope is deleted — so the attack must plant its own rows, because **an empty log passes a leak check for the same reason an empty page does**.

**Checkpoint**: all three stories done; constitution I has an attack on every new surface.

---

## Phase 6: The probes and the gates

- [X] T046 **The per-arm probe.** Delete each arm individually and re-run both suites: the `applied` check, the environment scope on the fan-out, the empty-list path, the per-channel loop, and the buffering skip. **Record which arms turn nothing red.** 4.12 deleted two tenancy scopes and the release-gating suite stayed green — an SQL clause carries no JavaScript branch, so a coverage number reports less than this probe does.
- [X] T047 Any arm from T046 whose deletion turns nothing red is either untested or unnecessary. **Say which, out loud, for each one.** 4.11 found an early return that was an optimisation wearing a branch's clothes, and 4.12 found two arms that were only invisible because of each other.
- [X] T048 [P] Run `pnpm coverage` and set per-file pins for every changed file. **Pin below the lower of two observations and put both numbers in the config** — and remember 4.13 found two further shapes: a branch DENOMINATOR that differs between this machine and CI (059-20), and a pin that was right while its environment was wrong (059-22). **Ask what the number is measuring before you move it.**
- [X] T049 [P] Verify every new pin actually binds. A per-file threshold whose key matches no file is **silent** — demand 101% of a nonexistent path and confirm no error appears, then confirm the real pin fires. Run both halves.
- [X] T050 [P] Run `pnpm check:errors` in **both** directions. This chapter adds no error code, so the expected answer is 34 and 34, unchanged — assert that rather than assuming it. **That script still has no CI job** (`gaps.md` 055-3), so running it by hand is the only reason a discrepancy would be caught.
- [X] T051 [P] Run `check-lane-scope.py` after the new integration tests land. It asks which queries read a shared table with no predicate naming this test's own rows, and it **cannot see an action scoped too wide** — a `docker compose stop` or a fixture that sweeps a shared table is invisible to it (056-5).
- [X] T052 Run the full lane in both arrangements from T004 and compare against the opening figures, per suite. A suite that is slower is not automatically this chapter's fault; a suite that is **red** is, until shown otherwise.

---

## Phase 7: The chapter

- [X] T053 Register the chapter in `relay-tutorial/lib/tutorial.ts` before writing a line of it. `<ChapterHeader id="4.14" />` throws on an unregistered id and `pnpm build` exits 1 — 4.4 shipped at 112 of 112 with eight gates green and **none of them rendered a page**. **It is seven fields, not an id**: `id`, `path`, `title`, `status`, `readerProduces` (a paragraph, not a phrase), `sourceDoc`, `readerMinutes`.
- [X] T053a **Verify the registered `path` resolves to a real directory** — `test -d "relay-tutorial/app/(en)/part-4/chapter-14/<slug>"`. **Nothing checks this**: the five `check:*` scripts never read `lib/tutorial.ts`, and `<ChapterHeader>` validates the `id` and not the `path`, so a wrong path is a nav link to a 404 **with a green build**. One `test -d` is cheaper than the gate this project would otherwise be tempted to write.
- [X] T054 Write the chapter at `relay-tutorial/app/(en)/part-4/chapter-14/<slug>/page.mdx`, with `figures.ts` beside it if it carries diagrams — the shape every Part 4 chapter uses. The slug is the title in kebab case and **must match T053's registered `path` exactly**. Its argument is the one research produced: **FR-MED-07 is two sentences, the state is the mechanism and the frame is the optimisation**, and the subject question was answered by arithmetic somebody had already written down.
- [X] T055 Publish the §7.4 decision with **both** of ADR-25's bounds evaluated numerically (SC-007): per-channel SUBSCRIBEs 5 against 6, projected subjects unchanged under `5 × channels + 1 × connected users`. Say that the load test was not re-run and that this is a source count agreeing with ADR-25's rows.
- [X] T056 Publish the option that died on a missing field. Re-sending the message as `message.updated` is the cheapest shape available and **`messageSchema` has no `edited_at`**, so a client could not tell an attachment resolving from an author editing. It is ADR-24's own objection arriving one level up, and it is the most transferable thing in the chapter.
- [X] T057 [P] Publish the lane figures the tests rest on: 4,725 unreferenced of 5,403, N=2 at 44 objects, 538 already terminal, 2,867 tombstones with zero attachments. **Re-take them at T005's values if they moved.**
- [X] T058 [P] Write the TRAP boxes. Candidates: a state stored on the message instead of read at serve time; a required `state` on the reader schema; a frame published on the request rather than the transition; a fan-out written for N = 1.
- [X] T059 [P] Figures: the state machine with the two announced edges, and the fan-out at N = 0, 1, 2. Pass diagrams as `code`, not `chart={…}` — `check:figures` caught three dead diagrams that `pnpm build` served green (057).
- [X] T060 Count the chapter's prose words against the movement's bound and record the number, not an adjective.
- [X] T061 **Generate every fence hunk with `pnpm check:fences --dump <dir> --at <page>`**, not a bare `--dump`. A bare dump writes the END state: 4.13's first version verified as matching exactly once against that and matched **zero** times where it applies.
- [X] T062 Check each hunk anchors **exactly once** before pasting, not after. `-U6` is a default, not a rule; widen when the pre-image matches twice, and remember widening merges adjacent hunks and can make it worse.
- [X] T063 For any file the appendix also edits, decide which state the hunk is written against. `fences/post-series.md` applies **after every chapter**, so a file it touches has one shape at chapter N and another at the end — 4.8, 4.11 and 4.12 each paid this.
- [X] T064 **Check whether this chapter publishes something the appendix was carrying.** 4.13 found `authenticate.middleware.ts`'s hunk finished rather than broken, and the repair was to delete it. `attachments.ts`, `frames.ts` and `revision.ts` are all appendix-touched candidates.
- [X] T064a **Measure whether a Vietnamese twin is owed — do not assume it is not.** Counted 2026-09-28: **vi 3 chapters against en 13**, a lag of ten, where 056 recorded seven. Nothing is owed today and MIRROR has nothing to compare, so a byte-identical copy would be an untranslated English page in the vi tree. **056's own lesson was that its task described a corpus rather than checking one**; this task counts.
- [X] T065 **Count the fence bill at the end, not at the start**, and expect it to be larger than a one-file change: `frames.ts` and `attachments.ts` are fenced in **six English chapters** (1.3, 3.15, 3.17, 3.18, 3.22, 4.11) and four Vietnamese, and T009a touches `messageSchema` in all of them. 050, 056 and 058 each found the task table's list short, every time because repairs made after the list was written added to it. Report the absolute `check:fences` number, and expect 0.
- [X] T066 Run `pnpm build`, `pnpm check:docs`, `pnpm check:srs`, `pnpm check:figures`, `pnpm check:fences`, `lint`. **Read them off `ci.yml`, not off memory**, and assert each counted line rather than the exit code — five of seven gate scripts exit 0 when their corpus is absent.
- [X] T067 **Run the quickstart, every step, and correct it in place.** This is NFR-USE-03's whole verification and `ci.yml` contains the word `quickstart` zero times. The last three chapters' quickstarts were wrong three, three and five times, and most of those failures **produced a red that looked like a platform defect**. Record each correction beside the step.

---

## Phase 8: The record

- [X] T068 Write **ADR-33** in `docs/05-sad.md` and its deep dive in `docs/06-adr-deep-dives.md`: the third arm rather than a sixth grammar, with ADR-25's arithmetic, the four options, and **the reversal condition**. An ADR lives in two documents and ten analysis passes once amended only the summary.
- [X] T069 Amend **SRS FR-MED-07 as revision 1.21** in `docs/04-srs.md`: what this chapter met, and anything left unmet. The clause moved *vacuous* → *unmet with a reachable subject* at 1.20; this is where that sentence resolves. Follow 1.18/1.19/1.20's form — state what the old wording did not say.
- [X] T070 [P] Amend `docs/12` **row 15** to CLOSED and mark **§7.4 answered**, naming ADR-33. Row 15 is chapter 4.14 — §3 keeps pre-contraction ordinals, and reading its first column as current is how a chapter number goes wrong.
- [X] T071 [P] Amend **both** copies of the Part 4 table (`docs/12` and `docs/07`). Two chapters have now found one copy amended and not the other.
- [X] T072 [P] Write `specs/060-chapter-4-14/baseline.txt` — every phase's measurements in the order they were taken, including the ones that were wrong first.
- [X] T073 [P] Write `gaps.md`: new entries, plus **every carried item re-measured rather than copied**. Four of 043's twenty-three carried items were wrong when re-measured and three had closed with nobody working on them. Carry forward at minimum: 055-3 (`check:errors` has no job), 059-20 (the branch denominator), 043's minute bucket, and 059-11 (`media_events` deferred).
- [X] T074 [P] Write `traceability.md` **by reading, not by grep**. 057's mechanical coverage map reported 14 of 51 requirements uncited and all 14 were covered in substance — fourteen alarms, fourteen false.
- [X] T075 Audit every test this feature added, across `services/api/src/media/attachment-state.itest.ts`, `services/api/src/media/media-updated.itest.ts`, `services/gateway/src/media-updated.itest.ts` and the protocol tests: what would have to be false for this to fail? Check for titles that overclaim, conditional assertions, and assertions that can only fail for somebody else's reason.
- [ ] T076 Update `CLAUDE.md` — replace the in-flight line inside the SPECKIT markers with the close-out record. **Compress 059's entry at the same time**, per the convention at the top of that file: the budget is 150,000 characters and it stood at 134,772 when this feature opened.
- [ ] T077 Commit each phase. `git checkout` on a file with uncommitted work has destroyed work twice. Messages under five lines, no `Co-Authored-By` trailer.
- [ ] T078 Tag **`part4-ch14`** on `relay-platform`, annotated. Verify the tag checks out a tree whose stack starts — `README.md:8` promises exactly that, and a forward-only fix is what cost Part 3 twenty-one deleted tags.
- [ ] T079 Push, and **compare the CI error set per error against T007's opening**, uuids normalised. Three runs if the set moves: 057 found one comparison says *"this run introduced nothing new"* and three say whether the set is stable. A colour cannot say either.
- [ ] T080 If CI is red, establish whether it is this chapter's before repairing anything. 4.13's registry outage read as **1 distinct against a baseline of 6, zero new and five gone** — and the five were gone because the tests that produced them never ran.

---

## Dependencies & Execution Order

    Phase 1 (Setup)  ──▶ Phase 2 (Foundational) ──▶ Phase 3 (US1) ──▶ Phase 4 (US2) ──▶ Phase 5 (US3)
                                                          │                 │               │
                                                          └─────────────────┴───────────────┴──▶ Phase 6 (Probes)
                                                                                                      │
                                                                                     Phase 7 (Chapter) ┤
                                                                                     Phase 8 (Record)  ┘

**Phase 2 blocks everything.** The shapes are what the stories read and write.

**US1 → US2 is a real dependency, not a preference.** US2's tests assert a state that US1's
schema must already carry. US1 alone is shippable; US2 alone is not.

**US3 depends on US2** — there is no delivery to withhold until there is a delivery.

### Parallel opportunities

- **T003, T004, T005, T006** — four independent opening measurements.
- **T010, T011** and **T014, T017** — protocol tests in different files.
- **T023–T027** — five US1 integration tests, different files, all red-first.
- **T034–T039** — six US2 tests, same shape.
- **T042, T043, T044** — three US3 refusal tests.
- **T048, T049, T050, T051** — four gate runs.
- **T057, T058, T059** — chapter figures, boxes and prose measurements.
- **T070–T074** — four record documents.

**Do not parallelise T046.** The per-arm probe deletes one arm at a time; two deletions at once
measures neither.

### Suggested MVP

**Phase 1 + Phase 2 + Phase 3 (US1).** That is FR-MED-07's first sentence: every door serves the
attachment's current state, read at serve time. A client that polls is correct for every object
including the 538 on this lane that are already terminal when attached — and no producer exists
yet. It is the floor the rest of the chapter is an optimisation over.

## Implementation Strategy

**Build the floor, then the optimisation, and keep them separable.** 4.13 recorded the same
shape for the upload sweep against the notice: the sweep is the mechanism and a notice is an
optimisation that must not change any answer. SC-006 is what holds this one honest — a client
that receives no frame at all must still report the right state, and that test must pass at
every phase after US1.

**Run the premise before executing a task whose premise might have moved.** T005 exists because
the lane's composition changes between chapters, and three artifacts in this feature quote
figures measured on 2026-09-28.
