# Tasks — chapter 4.23, "The channel a socket names"

**Feature**: `specs/070-chapter-4-23/` · **Plan**: [plan.md](./plan.md) ·
**Research**: [research.md](./research.md) · **Contract**: [contracts/frames.md](./contracts/frames.md)

**The chapter builds; 069 / chapter 4.24 verifies.** `docs/12` §5 rule 4, and the
second time in a row Part 4 has used it. 4.22 came from the milestone's premise
check and this came from 4.22's response-shape sweep — **if a third chapter arrives
the same way, that is the signal to stop and let the milestone run** (plan,
complexity table).

**The clause is Phase 3 and the code is Phase 4, in that order.** 4.22 wrote its
clause after the code and `clauses.md` had to record constitution VI's first bullet
as met late. Not twice.

---

## Phase 1: Baseline

- [ ] T001 Pin the lane in `specs/070-chapter-4-23/baseline.txt`: `RELAY_POSTGRES_PORT=15432`, which services are up, and the row counts (`channels`, `users`, `messages`, `members`). **Record them beside every later timing** — they are part of the instrument, and 068 watched `channels` move by four in a day.
- [ ] T002 Record every lane's opening exit code in `baseline.txt`, **each with its `Cached:` line and elapsed time, or under `pnpm exec turbo run <task> --force`**. `pnpm test -- --force` forwards the flag to VITEST, which rejects it and prints `Tasks: 0 successful` — an exit code with no lane behind it. **A cached run replays the counted line as well as the status** (066), so the tells are `Cached: N of N` and an elapsed time in milliseconds.
- [ ] T003 Run all six tutorial gates from `relay-tutorial` and record each counted line in `baseline.txt`. **`pnpm -s <script>` runs nothing** — this pnpm answers `error: unexpected argument '-s' found` and EXIT 2.
- [ ] T003a **Write the gate deltas this chapter predicts, before any code**, in `baseline.txt`. Each is falsifiable and each belongs to one task:

```
check:fences   chapters  65 -> 66    the walker found the page        T058
check:fences   files    291 -> ?     T005 decides — this chapter titles fences
check:docs     revisions 30 -> 31    1.30                             T048
check:srs      rows     246 -> 247   FR-RTM-11, and unique            T015
```

**The two halves of the fence line count different things.** `en.perChapter.size` moves for any page the walker visits, even one titling zero fences; `en.state.size` moves only if this chapter titles a fence the chain has not seen. 068 predicted all four of its deltas correctly; **a wrong one names its own cause**, which is the reason to write them down first.
- [ ] T004 Capture the CI error-set baseline for the per-error comparison at close (SC-010), in `baseline.txt`. **An empty diff between two green runs carries nothing** and the record should say so when that is what happened.
- [ ] T005 **Re-derive the fence bill** rather than copy R6's **83 English pages · 74 Vietnamese · 9 files · 18 blocks · 3 to CREATE**. Count the two language trees separately — `app/(en)` is what `check:fences` replays onto `relay-platform`, `app/(vi)` is mirror-compared against the English chapter and never against the tree (050-3). **Count blocks to CREATE, which a sweep of what exists cannot see**: `auth.ts`, `typing.ts` and `session.controller.ts` have no appendix block at all. `grep -rl 'title="[^"]*<file>"' 'app/(en)' 'app/(vi)' fences/` for pages; blocks and `@@` counts from `fences/post-series.md`. **Expect it to rise** — 4.15's rule has gone one direction every time, and the spec's own estimate was already 40% low. **Analysis pass 1 raised it before the task ran**: `services/gateway/src/api-client.ts` and `services/api/src/internal/memberships.controller.ts` are a second api→gateway contract carrying channel keys, live, and R6 counted neither. The bill now reads **11 files, 83+ pages**, and the two new rows carry `?` until this task measures them.
- [ ] T006 **Re-measure R1 against the tree**: 7 client-facing schemas carrying `channel`, 21 gateway sites writing `channel:` onto a frame (18 `session.ts`, 1 `fanout.ts`, 1 `resume.ts`, 1 `typing.ts`), and **0 references to a channel's external id anywhere in `services/gateway/src`**. The last figure is the one the whole design rests on: the gateway cannot translate because it has nothing to translate from. **Give it its positive control** — the naive grep returns **5**, every one of them a user's external id (`connection-log/event.ts` 2, `isolation-fixtures.ts` 3), and a figure of 0 reported without the 5 beside it reads as a contradiction to whoever runs it next.
- [ ] T006a **Re-count the premise BY STRUCTURE, not by field** (R1a), and record it in `baseline.txt`. A `channel` field is one way a frame names a channel; a map KEYED by one and a LIST of ids are two more, and `grep "channel:"` sees neither. Pass 1 found three on the first frame every client receives:

```
connection.ack.payload.revisions   z.record(channel, number)   frames.ts:83   session.ts:1322
connection.ack.payload.cursor      z.record(channel, seq)      frames.ts:66   session.ts:1400
connection.ack.payload.truncated   string[] of channel ids     frames.ts:67   session.ts:1354
```

**Sweep the whole client-facing surface this way before Phase 2**, because the design, the fence bill and SC-001's assertion count all move with the answer. **The word `truncated` appeared in no artifact of this feature until pass 1** — and `connectionAckSchema` is a `z.strictObject` whose payload is strict too, so each of the three is a two-sided contract change (T014).
- [ ] T007 **Open the 21 sites and read them, do not grep them.** 065's T007 said fourteen and the real number was five, because a grep counts mentions. Record in `baseline.txt` which of the 21 write a channel the connection is a member of and which write one it is not — **a site writing a channel outside the map's population is a miss by construction**, and that is cheaper to find now than at T030. **Include the 22nd**, which the grep cannot see because the write is one call away: `reread()` at `session.ts:729` compares `api.memberships()` against `connection.channelIds` and publishes `channel: channelId` into `deliverMembership` at :741, on a timer, for every connection.
- [ ] T008 **Check the bounding assumption the checklist flagged** (`checklists/requirements.md`, *scope is clearly bounded*): that the fan-out subjects and the resume cursor's storage do not have to move. Read `subjectForChannel` and its four siblings, and `resume.ts`'s storage and comparison. **If either has to be re-keyed the bill has moved and this is a different chapter** — which is the plan's own unjustification condition.
- [ ] T009 **Find out whether the cross-tenant suite can attack a socket at all.** `services/api/src/isolation/gauntlet.itest.ts` attacks REST routes; constitution VI's third bullet names that suite. **If it cannot hold a WebSocket, record that as a gap rather than ticking the box** — `packages/e2e/src/harness.ts:176` already imports `ws`, so the question is whether the gauntlet may, not whether anything can.

---

## Phase 2: The decisions (BLOCKING)

**Nothing in Phase 4 or 5 starts until these four are written down.** 067 deferred
two decisions into implementation and paid for it in every artifact that assumed the
other answer — a probe that could not go red, a receipt that did not exist, and a
quickstart wrong twice from one cause.

- [ ] T010 **Decide how a channel joined mid-session gets its identity** (FR-007, R3's hole). Three options are priced in `research.md` R3: the membership frame carries the identity, the gateway refetches its session on change, or the map falls back to the key. **Decide with a measurement, not a preference.** **And the second option is cheaper than R3 first costed it**, which pass 1 found by opening the file: `reread()` (`session.ts:713`) already calls `api.memberships()` on a timer for every connection, so **the round trip is already being made** — it goes to `GET /internal/memberships`, which returns `channel_ids` and no identities. Widening that response to pairs fills the map on a schedule that already exists, for no new request. Weigh that against the membership frame carrying the identity, and record the decision in `baseline.txt` with the refusal of the third option in writing.
- [ ] T011 **Decide whether the resume cursor accepts both key forms, and how it tells them apart** (FR-003, R4). `cursorSchema` is `z.record(z.string(), z.number().int().positive())`, so **every client reconnecting across this deployment presents uuid keys** and a gateway understanding only identities resumes nothing, loses nothing visibly, and breaks constitution II in the quietest way it can break. **A cursor key has no shape test guaranteed to separate the two forms** — an `external_id` may itself be a uuid, 0 of 41,772 today and not forbidden. Pick shape-test-then-fall-back, or try-both-and-prefer-identity, and say what each does to the case the shape test gets wrong.
- [ ] T012 **Decide the fallback when a key misses the map**, and write the reason (data-model, *The miss*). **It must not be the key** — emitting it hands a client the uuid this chapter exists to stop handing them, on exactly the channels they most recently joined. Whatever it is, it is in constitution VI's 100%-branch population the moment it exists (T039).
- [ ] T013 **Decide whether this chapter needs an ADR**, and record the reasoning either way in `baseline.txt`. **Predicted no**, with an amendment to ADR-38's *"what it does not cover"* paragraph instead — that is the paragraph that named this gap. 4.21's plan predicted no and was wrong; 4.22's predicted yes and was right. **A prediction is worth nothing without the check.**
- [ ] T014 **Confirm the session response widening is a change both sides can make at once.** `internal.ts` says *"Payloads are strict: unknown fields are rejected"* (constitution VI, fifth bullet), so a gateway reading a field an older api does not send, or an api sending one an older gateway rejects, is a deployment-order defect. Read how api and gateway versions move together in `compose.yaml` and in CI, and record whether this is a two-step change or a one-step one. **And `connectionAckSchema` is strict on both levels**, so T021a's and T021b's changes are two-sided against the CLIENT as well — every field the ack gains or re-keys is a change a client's own parser can refuse.

---

## Phase 3: User Story 3 — the clause catches up with the surface (P3), and it goes FIRST

**Goal**: a reader can answer *which identifier names a channel in a real-time
frame* without reading code.

**Independent test**: read the amended clauses and answer the question for REST and
for the socket.

- [ ] T015 [US3] Add the clause to `docs/04-srs.md` saying which identifier names a channel on the real-time surface (FR-008). **It is new, not an amendment**: FR-RTM runs 01 to 10 and **none of the ten names an identifier** — the same silence FR-CHN had before FR-CHN-11, and widening a delivery clause to carry an addressing rule would hide that the rule was ever missing. Keep the identifier unique; `check:srs` counts rows and uniqueness (T003a).
- [ ] T016 [US3] Record in `specs/070-chapter-4-23/clauses.md` which constitution bullets this chapter engages and how each is discharged, **and state the Phase 3 ordering explicitly**: the clause is written before the translation, which is what 4.22 could not say.
- [ ] T017 [US3] Check the new clause against FR-RTM-01 through FR-RTM-10 and FR-CHN-11 by **reading all twelve beside each other**. 068 found the SRS quoting its own clause two ways — *identities* at one line and *identifiers* at another, under which spelling `users.id` violated it — by doing exactly this before writing the eleventh.

---

## Phase 4: User Story 1 — the map, and every frame that reads it (P1) 🎯 MVP

**Goal**: every field naming a channel in a frame delivered to a client carries the
customer's identifier.

**Independent test**: connect, provoke each of the seven frame kinds, read every
`channel` field, and find no uuid.

- [ ] T018 [US1] Write the red test first in `services/gateway/src/channel-naming.itest.ts`: connect a member, provoke each frame kind, and assert each `channel` field equals the customer's identifier — **and assert the ack's three structures separately**, `revisions`' keys, `cursor`'s keys and `truncated`'s members. **Ten assertions, not seven** (SC-001, as amended after pass 1). It fails on all ten today, which is the measurement that says the suite is pointed at the right thing.
- [ ] T019 [US1] Extend `channelsForUser` in `relay-platform/services/api/src/db/repository.ts` to return the identity beside the key. `repository.ts:4106` already joins the row that holds both; **this is the method the bill charges 28 pages for**, and the plan's complexity table says to take a cheaper route if the identity can reach the controller without it.
- [ ] T020 [US1] Change the session response's channel list to pairs in `relay-platform/packages/protocol/src/internal.ts`, and **fix the comment two lines above it** — the one that says internal uuids are the api's business while the field below carries them. That sentence is the evidence this was an oversight and it stops being true the moment T021 lands.
- [ ] T021 [US1] Build the pairs in `relay-platform/services/api/src/internal/session.controller.ts`, replacing `channels.map(c => c.channel_id)` at :132.
- [ ] T021a [US1] Re-key `connection.ack.payload.revisions` to identities, in `relay-platform/packages/protocol/src/frames.ts` (:83, and the comment above it that says *"every channel the user belongs to"*), `services/gateway/src/registry.ts` (:21), `auth.ts` (:46) and `session.ts` (:1322). **This is the one a count of `channel` fields could not see** — a map whose KEYS are channels, on the first frame every client receives, with zeros included so it names the whole membership.
- [ ] T021b [US1] Re-key `connection.ack.payload.truncated` to identities in `relay-platform/services/gateway/src/session.ts` — :1354, which is `[...connection.channelIds]`, and :1392's filter over the backfill response. **A list of channel ids with no field name anywhere near it**, and the cheapest of the three to translate.
- [ ] T022 [US1] Hold the map on the registry's `Connection` in `relay-platform/services/gateway/src/registry.ts`, beside the `channelIds: Set<string>` at :25 and **the channel-keyed `revisions: Record<string, number>` at :21** — which is the plainest argument for that home: the object already holds a map keyed by exactly the thing this chapter is re-keying. **Not `auth.ts:103`**, which R2 and the first draft of `data-model.md` both named: that is `channelIds: string[]` on the auth result (`auth.ts:42`), one hop earlier and not what `session.ts` or `fanout.ts` read. Carry the pairs through `auth.ts` to get them there. **Nothing here applies a tenant scope and nothing here could forget to** — the scope arrives with the data, which is the property T038 measures rather than assumes.
- [ ] T023 [US1] Implement the lookup with Phase 2's fallback (T012) in the gateway, as one function with one caller shape, so the miss path is one branch rather than 21.
- [ ] T024 [US1] Special-case `ALL_CHANNELS` **before the map is consulted** (R5). `membership.ts:75` is `export const ALL_CHANNELS = "*"`; a ban publishes it, and translating a sentinel turns a wildcard into a lookup miss. **The test belongs with the ban path**, not with the map.
- [ ] T025 [US1] Read through the map at the 18 sites in `relay-platform/services/gateway/src/session.ts`.
- [ ] T026 [US1] [P] Read through the map at the one site in `relay-platform/services/gateway/src/fanout.ts`.
- [ ] T027 [US1] [P] Read through the map at the one site in `relay-platform/services/gateway/src/typing.ts`.
- [ ] T028 [US1] Read through the map at the one site in `relay-platform/services/gateway/src/resume.ts`, **outbound only** — the cursor's storage and comparison stay on keys (R7), and its inbound half is T032. The outbound cursor the ack mints (`session.ts:1400`) is re-keyed here, which is the third of the ack's three structures.
- [ ] T029 [US1] Fill the map on a mid-session join per T010's decision, in whichever file that decision names.
- [ ] T030 [US1] Re-run T018 and record **10 of 10 green** — seven fields and three structures — plus the count of assertions. If any site discovered at T007 writes a channel outside the map's population, it surfaces here.
- [ ] T031 [US1] Update the comment in `relay-platform/packages/protocol/src/frames.ts` to say what `channel` carries. **The type does not change** — `z.string().min(1)` in all seven — so the comment is the only place a reader of that file learns the value did.

---

## Phase 5: User Story 1 — the inbound half (P1)

**Goal**: a client can say the identifier too, and a client holding a uuid is not
silently misrouted.

- [ ] T032 [US1] Accept both key forms on the resume cursor per T011's decision, in `relay-platform/services/gateway/src/resume.ts`. **The line is :80**, and what it does is FILTER: `Object.entries(cursors).filter(([channelId]) => channelIds.has(channelId))` drops any key the set does not hold — no error, no refusal, no log. **So FR-003's forbidden outcome is reached by a filter, not by a parse failure**, and an identity-keyed cursor meeting a key-holding set today resumes nothing and says nothing. **Assert the uuid-keyed cursor resumes**, with a constructed cursor — no local run reproduces a client that connected before the deployment (quickstart §5) — and assert the identity-keyed one is not filtered away.
- [ ] T033 [US1] Accept the identifier on `messageSendSchema`'s channel field, translating to the key before the gateway knocks at the api's internal door.
- [ ] T034 [US1] Accept the identifier on `typingSendSchema`'s channel field.
- [ ] T035 [US1] Assert a send by identifier lands and a send by uuid still lands, **each separately** (SC-002, FR-003). Two assertions, because the chapter's promise and its compatibility claim fail for different reasons.
- [ ] T036 [US1] Assert that an identifier naming a channel the client may not hear is refused **exactly as that case is refused today** (FR-005), by comparing the two refusals field by field with `request_id` stripped. **068-2 is why**: a resolver that refuses makes a user able to tell which channels exist, and it passed 92 assertions before the gauntlet caught it.

---

## Phase 6: User Story 2 and the probes

**Goal (US2)**: nothing behind the gateway's edge changed shape.

**Independent test (US2)**: read the fan-out subjects, the resume cursors' storage
and the api-facing contract; find keys, unchanged.

- [ ] T037 [US2] Demonstrate rather than assert that the subjects and the internal send door are unchanged (SC-006): `git diff part4-ch22 --` over `subjectForChannel` and its four siblings and over `internalSendRequestSchema`, with the result stated. **One dot, not two** (067-3). **State `internalBackfillResponseSchema.channels` and `internalMembershipsResponseSchema.channel_ids` either way** — both are internal and both carry keys, and the second one is T010's open question rather than a thing this task can assume.
- [ ] T038 [US1] Remove the map's tenant scope and record which named tests go red (FR-006, SC-005). **065-4 says to expect the single-mutation version to see nothing** — three chapters running — so if it reports zero, say which defence absorbed it rather than concluding the scope is untested.
- [ ] T039 Pin the new files in `relay-platform/vitest.coverage.config.mts` and **run both halves of the pin probe through `pnpm coverage`**: a pin on a file that does not exist (silent) and an impossible pin on a real file (loud). A filtered `vitest run` evaluates no per-file threshold at all (066), and **a pin above the real number is loud while a pin below it is as silent as a pin on nothing** (067).
- [ ] T040 Read the branch map, not the percentage, for any file that comes in under 100% — 068 spent three wrong readings on `channel-id.pipe.ts` before finding the uncovered arm was on `@Injectable()`, compiler-emitted and reachable by no test.
- [ ] T041 Count what a client receives over a full session and state the number (SC-004): **zero channel Relay identifiers**, counted rather than asserted in aggregate, **in any position — field, key or list member**. **This is the only criterion in the spec that would have caught the ack's three structures**, and at Phase 6 it catches them too late to be cheap. Run its sweep once at T006a as well, against the current binary, where the answer is still a measurement rather than a verdict.
- [ ] T042 Record the gauntlet's answer from T009 — the attacks added, or the gap written down.

---

## Phase 7: The documents

- [ ] T043 Amend ADR-38's *"what it does not cover"* paragraph in `docs/06-adr-deep-dives.md`. That paragraph named this gap; it is now closed and must stop saying it is open.
- [ ] T044 [P] Amend ADR-38's summary in `docs/05-sad.md`. **An ADR lives in two documents** (050) and 068 shipped four feature-local ids into both homes at once.
- [ ] T045 [P] Mark the row in `docs/12-part-4-plan.md` and amend **both** copies of the Part 4 table. The movement column is the stable address; **column one keeps the original ordinals on purpose** and reading it as current is how a chapter number goes wrong.
- [ ] T046 [P] Amend `docs/07-tutorial-plan.md` for the chapter.
- [ ] T047 [P] Amend `docs/03-journey-map.md` Stage 5, which is the half of Journey 3's promise this chapter keeps.
- [ ] T048 Add SRS revision 1.30 in `docs/04-srs.md`. `check:docs` counts ascending revisions (T003a).
- [ ] T049 **Sweep for feature-local ids with `git diff part4-ch22 -- docs/`.** One dot. `..HEAD` reads committed state and reports 0 while the leak sits in the working tree (067-3) — and 068 put four `FR-006`s into four published documents **in the chapter whose own task list warns about it**. The mechanism is moving a sentence without moving its frame.
- [ ] T050 Write `specs/070-chapter-4-23/traceability.md`: every FR and SC to the task and the artifact that discharges it.

---

## Phase 8: The chapter

- [ ] T051 Draft `relay-tutorial/app/(en)/part-4/chapter-23/the-channel-a-socket-names/page.mdx`, 2,000–4,000 prose words. **It opens on a behaviour, not an error**: a support tool that reads an order number on REST and a uuid on the socket, from one platform, in one minute.
- [ ] T052 Write the figures in that chapter's `figures.ts` as `code`, not as titled fences, and check them against `check:figures`' counted line.
- [ ] T053 Write the TRAP box: **the fallback that must not be the key** (T012), which is the one that wears the shape of a safe default.
- [ ] T054 Write the WHY box: **why the cheaper-looking design is the expensive one**, and that 4.22 is the reason (R2). Resolving an identity early has a cost and this chapter is where it lands.
- [ ] T055 Say in the chapter that this is the second chapter in a row generated by its predecessor's findings, and what would make that a problem. The spec's assumptions already say it; **the chapter is where a reader will meet it.**
- [ ] T056 Generate the appendix hunks from the checker's own replay (fence-chain rule 1a), **and remove the block before dumping** — `--dump` emits the state after the appendix applies, so a hunk diffed against it is a residual rather than a hunk.
- [ ] T057 Create the three appendix blocks that do not exist: `auth.ts`, `typing.ts`, `session.controller.ts`. A block count of what exists cannot see these (068-7).
- [ ] T058 Register the chapter so the walker finds it, and confirm `check:fences` moves the chapter count. **A chapter count that does not move means the page was not found** — 051's `Error: Unknown chapter id`, where the manifest step had failed first.
- [ ] T059 Translate the chapter into `app/(vi)`. The 74 Vietnamese pages are a mirror cost, compared against the English chapter and never against `relay-platform` (050-3).
- [ ] T060 Run `check:fences` to 0 and record the two counted figures against T003a's predictions.

---

## Phase 9: The record and the close

- [ ] T061 Run `pnpm lint` and `pnpm exec turbo run typecheck` — **fifteen tasks, not five**. CI's Docker-free gate found a one-character unused variable after four of 068's local lanes were green.
- [ ] T062 Run the battery with the composed services stopped **by name**: `docker compose stop api gateway dispatcher media-worker`, not `ingester`. **The sealed suite and the api lane want opposite machine states** (068-9) and one command answers `Tasks: 1 successful, 4 total` in about a second.
- [ ] T063 Run `pnpm coverage` and record files, tests, threshold errors and the pin count.
- [ ] T064 Run `quickstart.md` unmodified and fix whatever it gets wrong (NFR-USE-03). **§3 and §4 are predictions**, and §4 depends on T010 — 4.20's quickstart was wrong five times, 4.22's zero.
- [ ] T065 Write `specs/070-chapter-4-23/gaps.md`: new entries, **and the carried ledger re-measured rather than copied**. 068 carried eleven; four of 043's twenty-three were wrong when re-measured and three closed with nobody working on them.
- [ ] T066 Confirm SC-008: `git diff --name-only part4-ch22 --` contains no file outside this chapter's subject, tests and documents (FR-009).
- [ ] T067 Push in submodule order — `relay-platform`, then `relay-tutorial`, then the superproject. **CI is the superproject's** and checks out gitlinks; the other order checks out commits no remote has.
- [ ] T068 Compare the CI error set to T004's baseline **per error, in both directions** (SC-010). 4.11 found the sets identical on two runs of three, and one comparison would have missed that.
- [ ] T069 Tag `part4-ch23` on `relay-platform`, unpadded, annotated.
- [ ] T070 Update `CLAUDE.md`: the close-out entry, the active-plan line pointing at 069, and **compress the oldest entry past the last four** to its headline, measurement blocks, cited gap ids and one-line digests. The budget is 150,000 characters and the harness refuses it over that.
- [ ] T071 **Hand 069 whatever this chapter falsified in its artifacts.** 068's T069 exists because the milestone's spec, research and quickstart were written against a platform where Stage 2 was broken; this chapter closes Stage 5, so the milestone's real-time assertions change from *provoke the gap* to *verify the fix*. **The handoff is a task, not a courtesy.**

---

## Dependencies

```
Phase 1  baseline            everything
  T006a BLOCKS Phase 2 — it decides how big the surface is
Phase 2  the decisions       BLOCKS Phase 4 and Phase 5 entirely
  T010 -> T029    T011 -> T032    T012 -> T023, T039, T053    T013 -> T043
Phase 3  the clause          before Phase 4, deliberately (constitution VI.1)
Phase 4  the map             T019 -> T020 -> T021 -> T022 -> T023 -> T025..T028
                             T021a · T021b after T023, with the other sites
                             T018 is RED first and T030 closes it
Phase 5  inbound             after T023; T032 also needs T011
Phase 6  probes              after Phase 5
Phase 7  documents           after Phase 6, because T050 traces what happened
Phase 8  the chapter         after Phase 7; T056 after every platform edit is final
Phase 9  close               T061..T064 before T067; T068 after T067
```

**T008 can end this chapter.** If the subjects or the cursor's storage must move, the
bound has gone and the plan says so in writing.

## Parallel opportunities

```
T026 · T027              different gateway files, one site each
T044 · T045 · T046 · T047  four documents, no shared anchor
```

Phase 4's spine is serial on purpose: the identity has to exist in the repository
before the controller can send it, and on the connection before any site can read it.

## Independent test criteria

| story | independently testable by |
|---|---|
| **US1** | connect, provoke all seven frame kinds, read every `channel` field, send by identifier, and find no uuid in anything received |
| **US2** | read the subjects, the cursor's storage and the internal send door, and show them unchanged against `part4-ch22` |
| **US3** | read the amended clauses and answer *which identifier names a channel* for REST and for the socket without opening code |

## MVP

**User Story 1's outbound half — Phase 4.** Seven frame kinds naming the channel the
customer named is the chapter. Phase 5 is what stops it breaking every client that
is already connected, and Phase 3 is what stops the next frame being guessed.

---

## The mechanical coverage check, run and its result recorded

Grepped for each identifier, then read:

```
FR-001 every outbound field    T018·T021a·T021b·T025–T028·T030    SC-001  T018·T030
FR-002 every inbound field     T032–T034              SC-002  T035
FR-003 the uuid is not lost    T011·T032·T035         SC-003  T020·T021·T021a·T021b
FR-004 confined to the edge    T008·T037              SC-004  T041
FR-005 refused as today        T036                   SC-005  T038
FR-006 scoped, demonstrated    T022·T038              SC-006  T037
FR-007 mid-session membership  T010·T029              SC-007  T071
FR-004 also T006a, which decides what the edge contains
FR-008 a clause says which     T015·T017              SC-008  T066
FR-009 nothing else changes    T037·T066              SC-009  T060
FR-010 amend what is falsified T020·T031·T043–T047    SC-010  T004·T068
```

**AND PASS 1 FOUND THAT THE WEAKNESS IS REAL, ON THIS LIST.** Every FR and SC had a
named task, FR-001 among them — and FR-001's tasks covered seven `channel` fields
while three more client-facing structures named channels by key and by list. **The
check passed and the surface was wrong by three.** The repair was to re-measure the
premise, not to add identifiers.

**Every FR and SC is discharged by a named task, and that is the weakest kind of
coverage this project recognises.** 4.22's pass 10 raised twenty alarms and all
twenty were false; the check that matters is reading whether the task does what the
id requires. **A task citing an id it does not discharge makes the next mechanical
check pass and the reading never happen.**
