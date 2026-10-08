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

- [X] T001 Pin the lane in `specs/070-chapter-4-23/baseline.txt`: `RELAY_POSTGRES_PORT=15432`, which services are up, and the row counts (`channels`, `users`, `messages`, `members`). **Record them beside every later timing** — they are part of the instrument, and 068 watched `channels` move by four in a day.
- [X] T002 Record every lane's opening exit code in `baseline.txt`, **each with its `Cached:` line and elapsed time, or under `pnpm exec turbo run <task> --force`**. `pnpm test -- --force` forwards the flag to VITEST, which rejects it and prints `Tasks: 0 successful` — an exit code with no lane behind it. **A cached run replays the counted line as well as the status** (066), so the tells are `Cached: N of N` and an elapsed time in milliseconds.
- [X] T003 Run the tutorial gates from `relay-tutorial` and record each counted line in `baseline.txt`. **It is FIVE `check:*` scripts and six programs** — `check:docs` runs `check-docs-drift.sh` and `check-revision-order.mjs`, which is where "six gates" comes from, and a reader who takes the phrase literally goes looking for a sixth script. **And CI's tutorial job runs four of the five**: `check:docs`, `check:srs`, `check:figures`, `check:fences`, preceded by `lint` and `build`. **`check:errors` runs in no workflow** — recorded in `CLAUDE.md` since 055 and missed by analysis pass 9, which added a prediction for it without saying nothing would falsify one. **Record the three unused figure exports as PRE-EXISTING**, or they read as this chapter's when T052 runs the gate: `figCursorStability` in `app/(en)` and `app/(vi)` part-2/chapter-04, and `figTwoCounters` in `app/(vi)` part-3/chapter-11. **Five of the six gates were run at analysis time** — pass 5 took three and pass 9 took `check:figures` (330 figures, 332 bindings, 3 unused) and `check:errors` (34 codes, 34 sections, 6 close codes). **Three were run at analysis pass 5 and all three agree with the figures T003a inherited from 068's close** — `check:fences` 291 files across 65 chapters, `check:srs` 246 rows and 246 unique, `check-revision-order` 30 revisions ascending to 1.29 — so those predictions start from measured ground rather than a carried number. Run all six anyway; the other three have not been. **`pnpm -s <script>` runs nothing** — this pnpm answers `error: unexpected argument '-s' found` and EXIT 2.
- [X] T003a **Write the gate deltas this chapter predicts, before any code**, in `baseline.txt`. Each is falsifiable and each belongs to one task:

```
check:fences   chapters  65 -> 66    the walker found the page        T058
check:fences   files    291 -> ?     T005 decides — this chapter titles fences
check:docs     revisions 30 -> 31    1.30                             T048
check:srs      rows     246 -> 247   FR-RTM-11, and unique            T015
check:figures  figures  330 -> 334   four, counted in 4.22's own page  T052
check:errors   34/34/6  UNCHANGED    T036 refuses exactly as today    T036
               and NO WORKFLOW RUNS IT — hand-run at T060 or not at all
```

**The last two were missing until analysis pass 9 ran those gates.** `check:figures`
is the one gate this chapter is guaranteed to move, and it was the one with no
prediction; `check:errors` moves only if somebody adds a code by accident, **which
is what makes a predicted zero worth writing** — it is falsifiable and it is how the
accident gets caught.

**The two halves of the fence line count different things.** `en.perChapter.size` moves for any page the walker visits, even one titling zero fences; `en.state.size` moves only if this chapter titles a fence the chain has not seen. 068 predicted all four of its deltas correctly; **a wrong one names its own cause**, which is the reason to write them down first.
- [X] T004 Capture the CI error-set baseline for the per-error comparison at close (SC-010), in `baseline.txt`. **An empty diff between two green runs carries nothing** and the record should say so when that is what happened.
- [X] T005 **Re-derive the fence bill** rather than copy R6's **83 English pages · 74 Vietnamese · 9 files · 18 blocks · 3 to CREATE**. Count the two language trees separately — `app/(en)` is what `check:fences` replays onto `relay-platform`, `app/(vi)` is mirror-compared against the English chapter and never against the tree (050-3). **Count blocks to CREATE, which a sweep of what exists cannot see**: `auth.ts`, `typing.ts` and `session.controller.ts` have no appendix block at all. `grep -rl 'title="[^"]*<file>"' 'app/(en)' 'app/(vi)' fences/` for pages; blocks and `@@` counts from `fences/post-series.md`. **Expect it to rise** — 4.15's rule has gone one direction every time, and the spec's own estimate was already 40% low. **And count the tests, which the fence bill does not.** 12 gateway suites mention a channel about 700 times with 76 direct `channel:` assertions, led by `typing.itest.ts` (188) and `membership.itest.ts` (163). **Then find the readers by the TYPE rather than by the word** (4.11, 065), which gives a different and sharper list — the files that CONSTRUCT a session response or a revisions map:

```
internal.itest.ts · resume.itest.ts · session.test.ts · typing.itest.ts
connections.itest.ts · fanout.itest.ts · session.itest.ts · isolation.itest.ts
connection-log/event.test.ts
packages/protocol/src/frames.test.ts   NOT a gateway suite — outside the 12 above
                                       and outside T062's gateway lane
```

**And exclude `dist/` from every count.** A grep over `packages --include=*.ts` picks up gitignored `*.d.ts` build artifacts: pass 14's raw figures were 11 files for `channel_ids` and 17 for `revisions`, **2 of each a build artifact**. The `dist` trees are untracked, so they cannot reach SC-008's diff, but they can inflate any number taken this way. A published page and a red test are two different corpora and only one of them has ever been counted here. **Analysis pass 1 raised it before the task ran**: `services/gateway/src/api-client.ts` and `services/api/src/internal/memberships.controller.ts` are a second api→gateway contract carrying channel keys, live, and R6 counted neither. The bill now reads **11 files, 83+ pages**, and the two new rows carry `?` until this task measures them.
- [X] T005a **Measure what this chapter makes untrue in already-published chapters, and split it by whether a gate can see it.** Nine English pages print a client frame's `channel` as a uuid — Part 2 chapters 5 and 6, Part 3 chapters 1, 9, 10, 11, 14, 17 and 18 — **9 English lines and 19 Vietnamese**, mostly the placeholder `11111111-1111-1111-1111-111111111111`. **Split them**: a line inside a titled fence is platform source and moves only if the platform file moves; a line in prose or in a figure moves for nobody, and **no checker reads prose** — `check:fences` compares bytes in titled fences and nothing else. 10 of the placeholders also exist in `relay-platform` source, so the fenced share is real and the unfenced share is the population that needs a decision. Six more lines say `channel_id:` and stay correct, which is the distinction this chapter is about. **The decision goes to T049a**; this task only produces the number.
**WHAT THE ANALYSIS PASSES ALREADY MEASURED, AND WHAT IS UNTOUCHED.** Three of this
phase's tasks have been done in substance and one has not, and a task that looks done
gets ticked:

```
T003   five of six gates RUN            passes 5 and 9      re-run to confirm
T006   7 schemas · 21 sites · 0 refs    pass 1              re-run to confirm
T006a  the ack's three structures       pass 1              listed, not re-swept
T008   the subjects stay keyed          R7 and pass 3       cursor storage unread
T009   UNTOUCHED — nobody has asked whether the gauntlet can hold a socket,
       and it is the one Phase 1 answer a constitution clause turns on
```

- [X] T006 **Re-measure R1 against the tree**: 7 client-facing schemas carrying `channel`, 21 gateway sites writing `channel:` onto a frame (18 `session.ts`, 1 `fanout.ts`, 1 `resume.ts`, 1 `typing.ts`), and **0 references to a channel's external id anywhere in `services/gateway/src`**. The last figure is the one the whole design rests on: the gateway cannot translate because it has nothing to translate from. **Give it its positive control** — the naive grep returns **5**, every one of them a user's external id (`connection-log/event.ts` 2, `isolation-fixtures.ts` 3), and a figure of 0 reported without the 5 beside it reads as a contradiction to whoever runs it next.
- [X] T006a **Re-count the premise BY STRUCTURE, not by field** (R1a), and record it in `baseline.txt`. A `channel` field is one way a frame names a channel; a map KEYED by one and a LIST of ids are two more, and `grep "channel:"` sees neither. Pass 1 found three on the first frame every client receives:

```
connection.ack.payload.revisions   z.record(channel, number)   frames.ts:83   session.ts:1322
connection.ack.payload.cursor      z.record(channel, seq)      frames.ts:66   session.ts:1400
connection.ack.payload.truncated   string[] of channel ids     frames.ts:67   session.ts:1354
```

**Sweep the whole client-facing surface this way before Phase 2**, because the design, the fence bill and SC-001's assertion count all move with the answer. **The word `truncated` appeared in no artifact of this feature until pass 1** — and `connectionAckSchema` is a `z.strictObject` whose payload is strict too, so each of the three is a two-sided contract change (T014).
- [X] T007 **Open the 21 sites and read them, do not grep them.** 065's T007 said fourteen and the real number was five, because a grep counts mentions. Record in `baseline.txt` which of the 21 write a channel the connection is a member of and which write one it is not — **a site writing a channel outside the map's population is a miss by construction**, and that is cheaper to find now than at T030. **Include the 22nd**, which the grep cannot see because the write is one call away: `reread()` at `session.ts:729` compares `api.memberships()` against `connection.channelIds` and publishes `channel: channelId` into `deliverMembership` at :741, on a timer, for every connection.
- [X] T008 **Check the bounding assumption the checklist flagged** (`checklists/requirements.md`, *scope is clearly bounded*): that the fan-out subjects and the resume cursor's storage do not have to move. Read `subjectForChannel` and its four siblings, and `resume.ts`'s storage and comparison. **If either has to be re-keyed the bill has moved and this is a different chapter** — which is the plan's own unjustification condition.
- [X] T009 **ANSWERED AT ANALYSIS PASS 13, BY OPENING THE FILE: the socket half of the gauntlet already exists.** `services/gateway/src/isolation.itest.ts`, **23 tests**, header: *"THE SOCKET HALF OF THE GAUNTLET (FR-007, NFR-SEC-09, constitution I). The api's gauntlet attacks every HTTP route. None of it reaches here: A WEBSOCKET IS NOT IN `router.stack`, so the derived target list cannot see it, and this file is the only place the socket gets attacked with another tenant's identifiers."* **Re-read it rather than re-deriving the answer**, and record its test count in `baseline.txt`.

**AND ELEVEN ANALYSIS PASSES ASSERTED THE OPPOSITE.** Pass 2 called the missing socket attack a CRITICAL violation of constitution I, four later passes cited that, and pass 12 priced the constitution amendment it would need. **One file read refuted all of it** — the question was asked in this very task and then reasoned about instead of looked up, against this project's own first-ranked mechanism: ask the repository a question with a yes-or-no answer. Constitution I is satisfied; the amendment branch is withdrawn. **The exposure predates this chapter and this chapter is what makes it load-bearing**, because the map is a new tenant-scoped structure on exactly that surface.

---

## Phase 2: The decisions (BLOCKING)

**Nothing in Phase 4 or 5 starts until these four are written down.** 067 deferred
two decisions into implementation and paid for it in every artifact that assumed the
other answer — a probe that could not go red, a receipt that did not exist, and a
quickstart wrong twice from one cause.

- [X] T010 **Decide how a channel joined mid-session gets its identity** (FR-007, R3's hole). Three options are priced in `research.md` R3: the membership frame carries the identity, the gateway refetches its session on change, or the map falls back to the key. **Decide with a measurement, not a preference.** **And the second option is cheaper than R3 first costed it**, which pass 1 found by opening the file: `reread()` (`session.ts:713`) already calls `api.memberships()` on a timer for every connection, so **the round trip is already being made** — it goes to `GET /internal/memberships`, which returns `channel_ids` and no identities. Widening that response to pairs fills the map on a schedule that already exists, for no new request. Weigh that against the membership frame carrying the identity, and record the decision in `baseline.txt` with the refusal of the third option in writing.
- [X] T011 **Decide whether the resume cursor accepts both key forms, and how it tells them apart** (FR-003, R4). `cursorSchema` is `z.record(z.string(), z.number().int().positive())`, so **every client reconnecting across this deployment presents uuid keys** and a gateway understanding only identities resumes nothing, loses nothing visibly, and breaks constitution II in the quietest way it can break. **A cursor key has no shape test guaranteed to separate the two forms** — an `external_id` may itself be a uuid, 0 of 41,772 today and not forbidden. Pick shape-test-then-fall-back, or try-both-and-prefer-identity, and say what each does to the case the shape test gets wrong.
- [X] T012 **Decide the fallback when a key misses the map**, and write the reason (data-model, *The miss*). **It must not be the key** — emitting it hands a client the uuid this chapter exists to stop handing them, on exactly the channels they most recently joined. Whatever it is, it is in constitution VI's 100%-branch population the moment it exists (T039).
- [X] T012a **Decide WHERE the translation happens, which decides how big this chapter is** (FR-001, FR-004). Two designs, and pass 3 is why this is a decision rather than an assumption:

```
at the 21 sites        each site writes the identity onto the frame it builds
at the outermost send  session.ts:119 `send(socket, frame)` becomes a wrapper
                       that takes the CONNECTION and translates on the way out
```

**The second keeps every internal structure keyed** — `connection.buffer`, `marks`, `channelIds`, `lastPublished` — and that matters because two internal comparisons index a buffered frame BY `frame.channel`: `flushable`'s `marks[frame.channel]` (`resume.ts:111`) and the revocation filter's `m.channel !== change.channel` (`session.ts:662`). **Translate where the frame is built and both go silently false**: every mark is lost, so a resuming client is re-sent its whole buffer, and a revoked channel's backlog is flushed to somebody who has just lost access (FR-029, named in that comment). **It may also shrink the chapter** — 21 edits become one wrapper, and the fence bill with them, which would be the first time in Part 4 that a bill went DOWN. **And it collides with T010's answer**: a per-connection translation at `send` gives two answers for the one membership frame that `session.ts:602` builds once and sends to two audiences, because on an add the subject's map has no entry yet. Decide both together.
- [X] T012b **Write the probe T012a will be judged against, before T012a decides.** Assert the two internal comparisons a buffered frame takes part in, in `relay-platform/services/gateway/src/resume.itest.ts` and `membership.itest.ts`: **a resume with a non-empty buffer delivers each frame once** (`flushable`'s `marks[frame.channel]`, `resume.ts:111`), and **a revocation landing mid-resume drops that channel's buffered frames** (`session.ts:662`, FR-029). **Both are green today and both go silently false if a buffered `message.channel` becomes an identity while the marks and the change stay keyed** — which is the test T012a is chosen against, because a paragraph cannot tell you which design keeps them. **And three assertions in `isolation.itest.ts` already encode what this chapter must not break**: *"a connection ack names nothing belonging to the other tenant"* (:234), *"a cursor naming the other tenant's channel backfills nothing"* (:450) and *"nothing from the other tenant's channel is delivered"* (:723). Run them beside the two above. Written here rather than in Phase 5, where the first draft put them, although the dependency graph had said all along that they come first: a task in a phase that T012a blocks cannot run before T012a.
- [X] T013 **Decide whether this chapter needs an ADR**, and record the reasoning either way in `baseline.txt`. **Predicted no**, with an amendment to ADR-38's *"what it does not cover"* paragraph instead — that is the paragraph that named this gap. 4.21's plan predicted no and was wrong; 4.22's predicted yes and was right. **A prediction is worth nothing without the check.**
- [X] T014 **Confirm the session response widening is a change both sides can make at once.** `internal.ts` says *"Payloads are strict: unknown fields are rejected"* (constitution VI, fifth bullet), so a gateway reading a field an older api does not send, or an api sending one an older gateway rejects, is a deployment-order defect. Read how api and gateway versions move together in `compose.yaml` and in CI, and record whether this is a two-step change or a one-step one. **And `connectionAckSchema` is strict on both levels**, so T021a's and T021b's changes are two-sided against the CLIENT as well — every field the ack gains or re-keys is a change a client's own parser can refuse. **Name the failure mode, not just the step count**: `internalSessionResponseSchema` is strict and `api-client.ts:63` parses it, so an old gateway meeting a new api throws inside `parse`, `auth.ts:107` catches it and returns `{ outcome: "unavailable" }` — **every connection refused, and the api reported as down**. `frames.ts:152` already documents this boundary for three other payloads and says what each one does; this is the fourth and it fails harder than any of them.

---

## Phase 3: User Story 3 — the clause catches up with the surface (P3), and it goes FIRST

**Goal**: a reader can answer *which identifier names a channel in a real-time
frame* without reading code.

**Independent test**: read the amended clauses and answer the question for REST and
for the socket.

- [X] T015 [US3] Add the clause to `docs/04-srs.md` saying which identifier names a channel on the real-time surface (FR-008). **It is new, not an amendment**: FR-RTM runs 01 to 10 and **none of the ten names an identifier** — the same silence FR-CHN had before FR-CHN-11, and widening a delivery clause to carry an addressing rule would hide that the rule was ever missing. **The id is FR-RTM-11** — FR-RTM-01 through 10 sit at `docs/04-srs.md:469–478` and 11 is free, checked at pass 6. Naming it here is what ties T003a's predicted row delta 246→247 to one clause, which is how 068 verified FR-CHN-11. `check:srs` counts rows and uniqueness.
- [X] T016 [US3] Record in `specs/070-chapter-4-23/clauses.md` which constitution bullets this chapter engages and how each is discharged, **and state the Phase 3 ordering explicitly**: the clause is written before the translation, which is what 4.22 could not say.
- [X] T017 [US3] Check the new clause against FR-RTM-01 through FR-RTM-10 and FR-CHN-11 by **reading all twelve beside each other**. 068 found the SRS quoting its own clause two ways — *identities* at one line and *identifiers* at another, under which spelling `users.id` violated it — by doing exactly this before writing the eleventh.

---

## Phase 4: User Story 1 — the map, and every frame that reads it (P1) 🎯 MVP

**Goal**: every field naming a channel in a frame delivered to a client carries the
customer's identifier.

**Independent test**: connect, provoke each of the seven frame kinds, read every
`channel` field, and find no uuid.

- [X] T018 [US1] Write the red test first in `services/gateway/src/channel-naming.itest.ts`: connect a member, provoke each frame kind, and assert each `channel` field equals the customer's identifier — **and assert the ack's three structures separately**, `revisions`' keys, `cursor`'s keys and `truncated`'s members. **Ten assertions, not seven** (SC-001, as amended after pass 1). It fails on all ten today, which is the measurement that says the suite is pointed at the right thing. **And they are hand-written because nothing else can see this change**: the field types are identical before and after, so the compiler names no site, and `isolation.itest.ts` derives its targets from `frameSchema`'s members and catches a new frame type rather than a new value (plan, *Two halves*).
- [X] T019 [US1] Extend `channelsForUser` in `relay-platform/services/api/src/db/repository.ts` to return the identity beside the key. **The query already `innerJoin`s `channels` for `revisionSequence`** (:4106), so `external_id: channels.externalId` adds a column and no join — *"the join costs nothing: `members` is already reached and `channels` is one hop from it on a primary key."* **No cheaper route is needed**, which answers the plan's complexity-table question about this 28-page file.

**AND REPAIR BOTH CALLERS IN THE SAME CHANGE, WHICH THE METHOD'S OWN COMMENT DEMANDS** (:4097): *"TWO CALLERS, AND BOTH ARE REPAIRED IN THE SAME CHANGE. `session.controller.ts` wants the counts; `memberships.controller.ts` wants ids alone and maps them. Widening the return without fixing both leaves the second assigning objects to a `string[]`, which is a typecheck failure at exactly the boundary this project commits at."* **Feature 044 hit that wall and left the warning**; the second caller is `memberships.controller.ts:72`, and the count is still two, checked at analysis pass 18. **AND LEAVE THREE COMMENTS ALONE.** `channels.schema.ts:34`, `internal.itest.ts:256` and `isolation.itest.ts:357` each describe where this method selects from — *"`members` joined to `users`… filters on both the user and the environment"* — and the session's channel list coming from it. **Adding a column falsifies none of them**, and 066 paid for the other half of this rule: a comment that is still accurate must not be repaired. **The probe already exists**: `repository.itest.ts:1255`, *"carries the count on channelsForUser, for both of that query's callers (FR-014)"* — written by 044 for this hazard and in none of the task lists, because it constructs no session response and so fell outside T005's type-derived set.
- [X] T020 [US1] Change the session response's channel list to pairs in `relay-platform/packages/protocol/src/internal.ts`, **and decide its `revisions` record in the same edit** — `internal.ts:196` is `z.record(z.string().min(1), …)` documented as *"the same keys as `channel_ids`"*, built at `services/api/src/internal/session.controller.ts:133` from `c.channel_id`. **Change one field and the two stop agreeing about what a channel is called**, and that contract's own comment is what says they must. Either both carry identities or the record stays keyed with a sentence saying why. And **fix the comment two lines above it** — the one that says internal uuids are the api's business while the field below carries them. That sentence is the evidence this was an oversight and it stops being true the moment T021 lands.
- [X] T021 [US1] Build the pairs in `relay-platform/services/api/src/internal/session.controller.ts`, replacing `channels.map(c => c.channel_id)` at :132. **Every suite that spawns the api reads this through `dist`** — `isolation-fixtures.ts:150` is the one that matters here — so `pnpm build` after this edit and before T042a, or the socket gauntlet tests the old response and goes green.
- [X] T021a [US1] **A client's `connection.ack.payload.revisions` names channels by identity.** The map is `relay-platform/packages/protocol/src/frames.ts:83` — a map whose KEYS are channels, on the first frame every client receives, with zeros included so it names the whole membership — and the comment above it needs amending whichever way T012a goes. **WHERE the keys change is T012a's to decide, not this task's**: re-keying at `registry.ts:21` and `auth.ts:46` is the 21-sites design, and translating at the ack is the `send`-wrapper design, which keeps the connection keyed. **The first draft of this task named the sites**, which encoded a decision Phase 2 had not made — the failure the Phase 2 block exists to prevent, committed by the pass that added the block.
- [X] T021b [US1] **A client's `connection.ack.payload.truncated` names channels by identity.** It is built at `relay-platform/services/gateway/src/session.ts:1354` as `[...connection.channelIds]`, filtered from the backfill response at :1392 — **a list of channel ids with no field name anywhere near it**, and the cheapest of the three to translate. Site per T012a.
- [X] T022 [US1] Hold the map on the registry's `Connection` in `relay-platform/services/gateway/src/registry.ts`, beside the `channelIds: Set<string>` at :25 and **the channel-keyed `revisions: Record<string, number>` at :21** — which is the plainest argument for that home: the object already holds a map keyed by exactly the thing this chapter is re-keying. **Not `auth.ts:103`**, which R2 and the first draft of `data-model.md` both named: that is `channelIds: string[]` on the auth result (`auth.ts:42`), one hop earlier and not what `session.ts` or `fanout.ts` read. Carry the pairs through `auth.ts` to get them there. **And `channelIds` stays a set of KEYS** — three membership tests read it (`session.ts:1493`, `session.ts:729`, `resume.ts:80`) and all three invert silently if it ever holds identities. The loudest is the backstop: a key-returning `api.memberships()` against an identity-holding set makes every channel look both removed and added on every tick, and the client is told so. **Nothing here applies a tenant scope and nothing here could forget to** — the scope arrives with the data, which is the property T038 measures rather than assumes.
- [X] T023 [US1] Implement the lookup with Phase 2's fallback (T012) in the gateway, as one function with one caller shape, so the miss path is one branch rather than 21. **Two directions, derived from one source** (data-model, *The map, which is two maps*): `key -> identity` for everything outbound, and `identity -> key` for the three inbound sites, built from the same session response at the same moment. **The first version of this feature specified one direction and FR-002 needs the other** — a client that may say the identity means something has to turn it back into a key before the api, the subject or the cursor filter sees it.
- [X] T024 [US1] Keep `ALL_CHANNELS` out of the map at `relay-platform/services/gateway/src/session.ts:532`, **and understand which way the risk runs** (R5, corrected at pass 3). A client never receives `"*"`: that guard expands the sentinel into one recursive `deliverMembership` per channel in `connection.channelIds`, and each inner change names a real channel. **So the danger is not emitting a wildcard — it is translating the expansion.** The sentinel must reach the guard untranslated and the expansion must stay keyed. **The test belongs with the ban path** and asserts that a banned user's frames name real channels by identity.
- [X] T025 [US1] Read through the map at the 18 sites in `relay-platform/services/gateway/src/session.ts` — **or at the one `send` wrapper, if T012a chose that design**, in which case T025 through T028 collapse into it and the fence bill is re-derived (T005).
- [X] T026 [US1] [P] Read through the map at the one site in `relay-platform/services/gateway/src/fanout.ts`.
- [X] T027 [US1] [P] Read through the map at the one site in `relay-platform/services/gateway/src/typing.ts`.
- [X] T028 [US1] Read through the map at the one site in `relay-platform/services/gateway/src/resume.ts`, **outbound only** — the cursor's storage and comparison stay on keys (R7), and its inbound half is T032. The outbound cursor the ack mints (`session.ts:1400`) is re-keyed here, which is the third of the ack's three structures.
- [X] T029 [US1] Fill the map on a mid-session join per T010's decision. **The slot is exact and both sites say their ordering is load-bearing** (`relay-platform/services/gateway/src/session.ts`):

```
added    :617 subscribe x4  ->  :630 channelIds.add  ->  :631 send(frame)
         the map insert goes BEFORE the send, inside the same .then()
removed  :652 send(frame)   ->  :657 channelIds.delete
         the map entry must SURVIVE until after the send
```

**And the frame is built once for two audiences** (:602): `others` already hold the channel, `subject` does not yet. A translation done per connection answers differently for the two; one done where the frame is built answers once. T012a and T010 decide this together.
- [X] T030 [US1] Re-run T018 and record **10 of 10 green** — seven fields and three structures — plus the count of assertions. If any site discovered at T007 writes a channel outside the map's population, it surfaces here.
- [X] T031 [US1] Update the comment in `relay-platform/packages/protocol/src/frames.ts` to say what `channel` carries. **The type does not change** — `z.string().min(1)` in all seven — so the comment is the only place a reader of that file learns the value did. **And the seven are field DECLARATIONS**: `forwardedMessageSchema` extends `messageSchema` (:152) and `messageCreatedSchema` (:156), `messageUpdatedSchema` (:161) and `messageDeletedSchema` (:198) wrap payloads that carry it, so a comment in one place leaves four schemas where the rule is invisible. Name them.

---

## Phase 5: User Story 1 — the inbound half (P1)

**Goal**: a client can say the identifier too, and a client holding a uuid is not
silently misrouted.

- [ ] T032 [US1] Accept both key forms on the resume cursor per T011's decision, in `relay-platform/services/gateway/src/resume.ts`. **The line is :80**, and what it does is FILTER: `Object.entries(cursors).filter(([channelId]) => channelIds.has(channelId))` drops any key the set does not hold — no error, no refusal, no log. **So FR-003's forbidden outcome is reached by a filter, not by a parse failure**, and an identity-keyed cursor meeting a key-holding set today resumes nothing and says nothing. **Assert the uuid-keyed cursor resumes**, with a constructed cursor — no local run reproduces a client that connected before the deployment (quickstart §5) — and assert the identity-keyed one is not filtered away.
- [ ] T033 [US1] Accept the identifier on `messageSendSchema`'s channel field, translating to the key before the gateway knocks at the api's internal door. **The line is `session.ts:1620`**, `channel_id: channel` — the client's string goes straight into `internalSendRequestSchema`, which is `z.string().uuid()`, so an untranslated identity is refused by a zod parse one service away rather than by anything this chapter wrote. Translate with T023's inverse map, before the call.
- [ ] T034 [US1] Accept the identifier on `typingSendSchema`'s channel field, translating at `session.ts:1571` before `signalTyping`. **THIS IS THE PATH WHERE FR-003 IS LOST IF IT IS LOST ANYWHERE.** `signalTyping` opens `if (!connection.channelIds.has(channelId)) return;` — commented *"DROPPED WITH NO FRAME, NO CLOSE CODE AND NO LOG LINE (FR-013)"* — and past it the string becomes a NATS subject through `subjectForTyping` (`typing.ts:137`). So an untranslated identity is **indistinguishable from a client typing into a channel it has left**: no error, no frame, no log line, and no api round trip to refuse it the way a send has. **Assert the drop does not happen**, which means asserting something arrives rather than asserting nothing was refused.
- [ ] T035 [US1] Assert a send by identifier lands and a send by uuid still lands, **each separately** (SC-002, FR-003). Two assertions, because the chapter's promise and its compatibility claim fail for different reasons.
- [ ] T036 [US1] Assert that an identifier naming a channel the client may not hear is refused **exactly as that case is refused today** (FR-005), by comparing the two refusals field by field with `request_id` stripped. **068-2 is why**: a resolver that refuses makes a user able to tell which channels exist, and it passed 92 assertions before the gauntlet caught it.

---

## Phase 6: User Story 2 and the probes

**Goal (US2)**: nothing behind the gateway's edge changed shape.

**Independent test (US2)**: read the fan-out subjects, the resume cursors' storage
and the api-facing contract; find keys, unchanged.

- [ ] T037 [US2] Demonstrate rather than assert that the subjects and the internal send door are unchanged (SC-006): `git diff part4-ch22 --` **in `relay-platform`** over `subjectForChannel` and its four siblings and over `internalSendRequestSchema`, with the result stated. **One dot, not two** (067-3). **State `internalBackfillResponseSchema.channels` and `internalMembershipsResponseSchema.channel_ids` either way** — both are internal and both carry keys, and the second one is T010's open question rather than a thing this task can assume.
- [ ] T038 [US1] Remove the map's tenant scope and record which named tests go red (FR-006, SC-005). **Name the predicate before deleting it**: the scope is `eq(users.environmentId, this.environmentId)` in `channelsForUser` (`repository.ts:4115`), reached through `members` rather than through `channels.environmentId` — there is no second candidate in the gateway, because the scope arrives with the data. **065-4 says to expect the single-mutation version to see nothing** — three chapters running — so if it reports zero, say which defence absorbed it rather than concluding the scope is untested.
- [ ] T039 Pin the new files in `relay-platform/vitest.coverage.config.mts` and **run both halves of the pin probe through `pnpm coverage`**: a pin on a file that does not exist (silent) and an impossible pin on a real file (loud). A filtered `vitest run` evaluates no per-file threshold at all (066), and **a pin above the real number is loud while a pin below it is as silent as a pin on nothing** (067).
- [ ] T040 **Before reading any number below 100, check whether the code ran in THIS process.** `isolation.itest.ts` spawns the api (`isolation-fixtures.ts:150`), so `session.controller.ts` and `repository.ts`'s `channelsForUser` are exercised there by a child process and **none of it is instrumented** — 062's finding, where three symbols measured 78.57 / 81.37 / 83.78 against pins of 100 and 84 while running on every execution of their suite. **A pin set from that run is wrong in the direction that looks like missing tests.** Then read the branch map, not the percentage, for any file that comes in under 100% — 068 spent three wrong readings on `channel-id.pipe.ts` before finding the uncovered arm was on `@Injectable()`, compiler-emitted and reachable by no test.
- [ ] T041 Count what a client receives over a full session and state the number (SC-004): **zero channel Relay identifiers**, counted rather than asserted in aggregate, **in any position — field, key or list member**. **This is the only criterion in the spec that would have caught the ack's three structures**, and at Phase 6 it catches them too late to be cheap. Run its sweep once at T006a as well, against the current binary, where the answer is still a measurement rather than a verdict.
- [ ] T042 Record the gauntlet's answer from T009 — the attacks added, or the gap written down.
- [ ] T042a Add this chapter's cases to **`relay-platform/services/gateway/src/isolation.itest.ts`** — the suite T009 found, not a new one: **a foreign channel's identity and a foreign channel's key, presented on a send, on a typing frame and in a resume cursor.** Each must be refused exactly as an unknown channel is refused, by the same code and the same message — 068-2 is the precedent, where a refusal one layer early let a banned user tell which channels existed.

**AND THE REASON HAND-WRITTEN CASES ARE NEEDED IS THE SUITE'S OWN STRENGTH.** It derives its target list from `frameSchema`'s members (`:165`, `:877–910`), so **a frame type added and forgotten is caught automatically — and this chapter adds no frame type.** It changes what a field carries, and three of the structures it changes (`revisions`, `cursor`, `truncated`) are not frame types at all. **A derived-target suite is green by construction against a value change**, which is exactly how this chapter could ship cross-tenant-untested.

**AND REBUILD THE API BEFORE RUNNING IT.** `isolation-fixtures.ts:150` spawns the api as a child process from `dist/main.js` and seeds through its build output — deliberately, because *"importing the api would make this service depend on the api's framework to test itself, and not knowing how the api is built is the whole of ADR-05."* **This chapter changes the api→gateway session response**, so a run against a stale `dist` attacks the previous binary, receives the old `channel_ids`, and passes. The chapter's central contract change, verified against the version before it.

---

## Phase 7: The documents

- [ ] T043 Amend ADR-38's *"what it does not cover"* paragraph in `docs/06-adr-deep-dives.md`. That paragraph named this gap; it is now closed and must stop saying it is open.
- [ ] T044 [P] Amend ADR-38's summary in `docs/05-sad.md`. **An ADR lives in two documents** (050) and 068 shipped four feature-local ids into both homes at once.
- [ ] T045 [P] **Correct** this chapter's row in `docs/12-part-4-structure.md` — **the file is `-structure`, not `-plan`, which is what this task said until pass 6 resolved it**, and the only dead path among thirteen `docs/` references in this feature. **The row already exists** (line 266, written when the gap was found) and it carries the estimate R6 superseded: *"Seven client-facing frame schemas, 21 sites in the gateway, ~50 English fence pages"* against a measured 83+ across 11 files. The movement column is the stable address; **column one keeps the original ordinals on purpose**, and this row's `—` is correct rather than missing, because a chapter that did not exist then has no original ordinal.
- [ ] T045b [P] **Do not go looking for a `docs/12` §7 question to close — there is none for this chapter.** 7.1, 7.2, 7.3, 7.4, 7.5 and 7.7 are closed, and **7.6, the SRS phase table disagreeing with itself, belongs to nobody here**. Checked at pass 9 because Part 4's pattern is that a chapter closes a §7 item, and an absent one looks like an oversight until somebody says it is not.
- [ ] T045a **Move the chapter counts, which no task owned and which 068 left behind.** Part 4 is 24 and three published statements still say 23: `docs/12-part-4-structure.md:199` *"seven movements, 23 chapters, three milestones"*, and `docs/07-tutorial-plan.md:84` and `:538`. `docs/12:552`'s *"It was 23, then 24, then 23 again"* is stale with them and is the open question that narrates the count. **A row was added and the number that sums the rows was not** — which is the shape to check whenever a part gains a chapter, and this part has gained two in three features.
- [ ] T046 [P] Amend `docs/07-tutorial-plan.md` for the chapter — the Part 4 section at :538 and the summary line at :84, both of which T045a also touches for their counts.
- [ ] T047 [P] Amend `docs/03-journey-map.md` Stage 5, which is the half of Journey 3's promise this chapter keeps.
- [ ] T048 Add SRS revision 1.30 in `docs/04-srs.md`. `check:docs` counts ascending revisions (T003a).
- [ ] T049 **Sweep for feature-local ids with `git diff part4-ch22 -- docs/`, in the SUPERPROJECT** — `docs/` exists in neither submodule, and the superproject is tagged only from `part4-ch19` on, so this command works for this chapter and would not have for 4.10. One dot. `..HEAD` reads committed state and reports 0 while the leak sits in the working tree (067-3) — and 068 put four `FR-006`s into four published documents **in the chapter whose own task list warns about it**. The mechanism is moving a sentence without moving its frame.
- [ ] T049a **Decide what to do about T005a's unfenced lines, and write the reason either way** (FR-010). Amending them is prose edits across nine chapters in two languages; leaving them is a published series that shows a reader a uuid where the platform now sends an identity. **"Record it and move on" is defensible here and nowhere else in this feature**, because a prose correction after publication moves no platform commit and invalidates no tag — which is the argument the reader protocol was retired on. Whichever way it goes, the count goes in `gaps.md` with it.
- [ ] T050 Write `specs/070-chapter-4-23/traceability.md`: every FR and SC to the task and the artifact that discharges it.

---

## Phase 8: The chapter

- [ ] T051 Draft `relay-tutorial/app/(en)/part-4/chapter-23/the-channel-a-socket-names/page.mdx`, 2,000–4,000 prose words. **It opens on a behaviour, not an error**: a support tool that reads an order number on REST and a uuid on the socket, from one platform, in one minute.
- [ ] T052 Write the figures in that chapter's `figures.ts` as `code`, not as titled fences, and check them against `check:figures`' counted line.
- [ ] T053 Write the TRAP box: **the fallback that must not be the key** (T012), which is the one that wears the shape of a safe default.
- [ ] T054 Write the WHY box: **why the cheaper-looking design is the expensive one**, and that 4.22 is the reason (R2). Resolving an identity early has a cost and this chapter is where it lands.
- [ ] T054a Write the `Checkpoint` box — **one per chapter is the live convention and no task wrote one until analysis pass 17.** `docs/07:68` lists four recurring classes (`WHY`, `TRAP`, `CHECKPOINT`, `SKIP AHEAD`); `Checkpoint` appears in **65 English pages**, including exactly one each in 4.21 and 4.22. Here it verifies the thing a reader can get wrong silently: **connect, read one frame's `channel`, and confirm it is the order number and not a uuid** — before going on to the inbound half. **No checker reads prose**, so nothing would have caught its absence.
- [ ] T054b **Do not add a `SkipAhead` box.** It is in 61 pages and in neither 4.21 nor 4.22 — a class that is live in the plan and lapsed in practice, like the Vietnamese translations (T059). Recorded so this chapter neither revives it by cargo cult nor is faulted for omitting it.
- [ ] T055 Say in the chapter that this is the second chapter in a row generated by its predecessor's findings, and what would make that a problem. The spec's assumptions already say it; **the chapter is where a reader will meet it.**
- [ ] T056 Generate the appendix hunks from the checker's own replay (fence-chain rule 1a), **and remove the block before dumping** — `--dump` emits the state after the appendix applies, so a hunk diffed against it is a residual rather than a hunk.
- [ ] T057 Create the three appendix blocks that do not exist: `auth.ts`, `typing.ts`, `session.controller.ts`. A block count of what exists cannot see these (068-7).
- [ ] T058 Register the chapter in `relay-tutorial/lib/tutorial.ts` with all seven fields — `id`, `path`, `title`, `status`, `readerProduces`, `sourceDoc`, `readerMinutes` — as **id `"4.23"`**, path **`/part-4/chapter-23/the-channel-a-socket-names`**, title **`"The channel a socket names"`**, and **the directory under `app/(en)/part-4/chapter-23/` must match the path's last segment**. **069 named all of that and still got the segment wrong**, which pass 5 caught, so naming it is necessary and not sufficient. Then **run `pnpm build` in `relay-tutorial`**, which is the command that throws `Error: Unknown chapter id` — 051's failure, where the manifest step failed before any gate and `check:fences` could not see it. **CI's tutorial job runs `lint` and `build` before the four gates**, so a bad registration is caught there, after the push, by a step no task ran. Then confirm `check:fences` moves the chapter count: **a count that does not move means the page was not found.**
- [ ] T059 **Decide whether this chapter is translated, and record the decision with the history** (R6, measured at pass 5). **No chapter has touched a Vietnamese file since 4.8**: fourteen chapters shipped with zero `app/(vi)` edits and the last vi commit is 055's fence repair. The tree is `app/(vi)/vi/part-4` — **chapters 01, 02 and 03 only, against 23 in English**, 46 vi pages in the series — and `check:fences` has printed its success line through all fourteen, so **the gate does not ask for a mirror and nothing was being evaded**. The options are: translate it, say the series stopped at 4.8 and write why, or leave this task and have it quietly not happen, **which is what the last fourteen chapters did**. R6's 74 is a count of vi pages mentioning these files, not of work this chapter would do.
- [ ] T060 Run `check:fences` to 0 and record its two counted figures against T003a's predictions, **and run `check:figures` and `check:errors` against theirs** — the figure count is the delta this chapter cannot avoid moving, and the error count is the one it predicts will not move.

---

## Phase 9: The record and the close

- [ ] T061 Run `pnpm lint` and `pnpm exec turbo run typecheck` **in `relay-platform`** — **fifteen tasks, not five**. CI's Docker-free gate found a one-character unused variable after four of 068's local lanes were green. **And run `pnpm lint` and `pnpm build` in `relay-tutorial` as well**: they are the tutorial job's first two steps and no task in this feature ran either until pass 10. `pnpm` in the wrong repository is its own failure mode — the gates live in `relay-tutorial` and a `check:*` run from the superproject exits without running anything.
- [ ] T062 Run the battery with the composed services stopped **by name**: `docker compose stop api gateway dispatcher media-worker`, not `ingester`. **The sealed suite and the api lane want opposite machine states** (068-9) and one command answers `Tasks: 1 successful, 4 total` in about a second. **A suite that spawns its OWN api is exempt from the stop rule** — `isolation.itest.ts` starts one on `PORT: "0"` and conflicts with nothing; the rule is about a second relay draining rows a test is counting.
- [ ] T063 Run `pnpm coverage` and record files, tests, threshold errors and the pin count.
- [ ] T064 Run `quickstart.md` unmodified and fix whatever it gets wrong (NFR-USE-03). **§2 onward are predictions** and §4 depends on T010 — 4.20's quickstart was wrong five times, 4.22's zero. **Four of its defects were found by analysis pass 8 instead of by this task**: a header where the gateway reads a query parameter, a missing `/v1/ws`, three variables nothing set, and an end-user token nothing minted. **§2 carried a MEASURED label through seven passes while being unable to connect** — so when this task runs, check the sections labelled measured first, not last.
- [ ] T065 Write `specs/070-chapter-4-23/gaps.md`: new entries, **and the carried ledger re-measured rather than copied**. **One entry is already written and measured: the webhook payloads** (R8) — `outbox/event.ts` :20, :66, :83, 8 occurrences, 3 payload types, 6 emitted event types, delivered to the customer's endpoint, on a boundary whose comment says consumers get external ids. **OPEN and deliberately not this chapter's.** 068 carried eleven; four of 043's twenty-three were wrong when re-measured and three closed with nobody working on them.
- [ ] T066 Confirm SC-008, **naming the repository for each run, because the three have different tag sets**: `git diff --name-only part4-ch22 --` in `relay-platform` (22 `part4-*` tags) and in the superproject (5, from `part4-ch19` on). **`relay-tutorial` holds two tags — `part4-ch9` and the backup — so the command cannot run there at all**, and that repository is where 83+ of this chapter's pages land. What stands in for it is the fence bill (T005) plus `git log --oneline part4-ch22..HEAD` read by hand. **And check the working tree is clean first**: all three were clean at pass 11, but this tree carries large prose edits at other times and T066 would read them as files outside the subject.
- [ ] T067 Push in submodule order — `relay-platform`, then `relay-tutorial`, then the superproject. **CI is the superproject's** and checks out gitlinks; the other order checks out commits no remote has.
- [ ] T068 Compare the CI error set to T004's baseline **per error, in both directions** (SC-010). 4.11 found the sets identical on two runs of three, and one comparison would have missed that.
- [ ] T069 Tag `part4-ch23` **on `relay-platform` AND on the superproject**, unpadded, annotated. **The last four chapters tagged both** — `part4-ch19` through `ch22` exist in the superproject — and the reason is T049's own command: `docs/` lives only in the superproject, so a missing tag there breaks the next chapter's `git diff <tag> -- docs/` sweep, and 069's SC-008 asks for `part4-ch23` by name. `relay-tutorial` is not tagged per chapter and has not been since `part4-ch9`.
- [ ] T070 Update `CLAUDE.md`: the close-out entry — **and put the Checkpoint in the measurement line.** 4.20, 4.21 and 4.22 each record *"N figures · N TRAP · N WHY"* and each contains a Checkpoint box none of them mentions, so the published record under-describes every recent chapter by one box. The active-plan line pointing at 069, and **compress the oldest entry past the last four** to its headline, measurement blocks, cited gap ids and one-line digests. The budget is 150,000 characters and the harness refuses it over that.
- [ ] T070a **Check 069's address before this chapter registers its own.** Pass 5 found 069's T046 still registering the milestone at `/part-4/chapter-23/milestone-the-priya-test` and its plan at `chapter-23/the-priya-test`, although its spec had said 4.24 since the renumber — **two features claiming one URL and one manifest id**, and an unregistered or duplicated id throws at build (051). Fixed at pass 5; re-check at the close, because **renumbering a chapter is not a find-and-replace on the spec, it is every artifact that spells the address** — and T046 and T048 had also disagreed with each other about the path's last segment.
- [ ] T071 **Hand 069 whatever this chapter falsified in its artifacts, and hand it R8.** The milestone asserts Journey 3 end to end; **Stage 1's "zero lookup tables" still fails on webhooks** after this chapter closes Stage 5, so the milestone either scopes around it knowingly or discovers it mid-run. 068's T069 exists because a milestone was written against a premise its predecessor deleted — this is the same debt in the other direction, a premise its predecessor could not close. 068's T069 exists because the milestone's spec, research and quickstart were written against a platform where Stage 2 was broken; this chapter closes Stage 5, so the milestone's real-time assertions change from *provoke the gap* to *verify the fix*. **The handoff is a task, not a courtesy.**

---

## Dependencies

```
Phase 1  baseline            everything
  T006a BLOCKS Phase 2 — it decides how big the surface is
Phase 2  the decisions       BLOCKS Phase 4 and Phase 5 entirely
  T010 -> T029    T011 -> T032    T012 -> T023, T039, T053    T013 -> T043
  T012a -> T021a, T021b, T025..T028 and the fence bill; decided WITH T010
  T005a -> T049a  (measure in Phase 1, decide in Phase 7)
  T012b is written BEFORE T012a decides — and it sits in Phase 2 for that reason
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
T045a is NOT parallel: it touches docs/12 and docs/07, which T045 and T046 hold
```

Phase 4's spine is serial on purpose: the identity has to exist in the repository
before the controller can send it, and on the connection before any site can read it.

## Independent test criteria

| story | independently testable by |
|---|---|
| **US1** | connect, provoke all seven frame kinds and the ack's three structures, send by identifier, TYPE by identifier, and find no uuid in anything received |
| **US2** | read the subjects, the cursor's storage and the internal send door, and show them unchanged against `part4-ch22` |
| **US3** | read the amended clauses and answer *which identifier names a channel* for REST and for the socket without opening code |

## MVP

**User Story 1's outbound half — Phase 4.** Ten things naming the channel the
customer named — seven `channel` fields and the ack's three structures — is the
chapter. Phase 5 is what stops it breaking every client that
is already connected, and Phase 3 is what stops the next frame being guessed.

---

## The mechanical coverage check, run and its result recorded

Grepped for each identifier, then read:

```
FR-001 every outbound field    T018·T021a·T021b·T025–T028·T030    SC-001  T018·T030
FR-002 every inbound field     T023·T032–T034         SC-002  T035·T034
FR-003 the uuid is not lost    T011·T032·T035         SC-003  T020·T021·T021a·T021b
FR-004 confined to the edge    T008·T012a·T012b·T037  SC-004  T041
FR-005 refused as today        T036                   SC-005  T038
FR-006 scoped, demonstrated    T022·T038              SC-006  T037
FR-007 mid-session membership  T010·T029              SC-007  T071
FR-004 also T006a, which decides what the edge contains
FR-008 a clause says which     T015·T017              SC-008  T066
FR-009 nothing else changes    T037·T066              SC-009  T060
FR-010 amend what is falsified T020·T031·T043–T047·T045a·T005a·T049a  SC-010  T004·T068
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
