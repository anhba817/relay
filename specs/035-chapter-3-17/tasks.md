# Tasks: Chapter 3.17 — the sender a message never had

**Spec**: [spec.md](spec.md) · **Plan**: [plan.md](plan.md) · **Research**: [research.md](research.md)
· **Data model**: [data-model.md](data-model.md) · **Contracts**: [contracts/](contracts/)

Each phase ends in a commit. Chapter 3.12 lost work twice to `git checkout` on a file with
uncommitted changes.

---

## The two blast radii, kept apart

`research.md` R1 counted **46 HTTP send sites across 12 files**. Re-derived here, making
`repository.sendMessage`'s `userId` required breaks a different set: **27 in-process calls
across 8 files**, five of which never send over HTTP and so were invisible to the first count.

    HTTP sends, application credential or user token        46 sites / 12 files
    repository calls with no userId                         27 calls / 8 files
    union                                                   17 files

**Neither number is the one to trust at implementation time.** T085 re-derives it from
`git diff --name-only`, which is what found the last feature's sixth and eighth revisions.

## Which routes depend on who is calling

The table the last feature added after two CRITICALs, because a route's behaviour depending on
the credential class needs three places — the handler resolves, the service threads, the
repository accepts — and a check gated on a parameter nobody fills in never fires.

| Route | Credential | What it resolves | Where the rule lives |
|---|---|---|---|
| `POST /v1/channels/:channelId/messages` | application | the named `user`, which must be a **bot** | handler resolves, **service** enforces bot-ness, repository requires a sender |
| `POST /v1/channels/:channelId/messages` | user token | the token's subject; a body `user` is refused | handler, and the schema for the refusal |
| `POST /v1/users` | application | `kind` and `description`; a kind change is refused | schema for shape, **service** for the change refusal |
| `POST /auth/dev-token` | application | whether the identifier is a bot | **controller**, before the mint |
| `POST /internal/messages` | user token | unchanged — its sender was never absent | unchanged |

## The columns this feature adds

| Column | Migration | Writer | Reader | Removal test |
|---|---|---|---|---|
| `users.kind` | 0013 | the upsert | the send's bot check, the profile read, the mint refusal | T045 |
| `users.description` | 0013 | the upsert, the profile PATCH | the profile read | T046 |

---

## Phase 1: The amendment — the gate principle VI sets

**Goal**: the governing document contains the requirement before any code cites it.

- [ ] T001 Add `FR-USR-07` to `docs/04-srs.md` §4.3: customers may create bot users representing their own software, carrying a description, which cannot authenticate. P2, verification `T`
- [ ] T002 Add `FR-MSG-10` to `docs/04-srs.md` §4.5: every message shall carry a sender; a message sent with an application credential shall name a bot user of that tenant. P1, verification `T`
- [ ] T003 [P] Add the amendment blockquote after §4.3's table in `docs/04-srs.md`, in the form the document already uses for FR-TEN-05: what changed, why, and that **FR-MSG-01 is unchanged** — it describes what a message contains and a later reader must not look for the sender rule there
- [ ] T004 [P] Record in `docs/04-srs.md` that FR-USR-01's "Relay shall not generate end user identifiers" still holds for bots: a bot's identifier is customer-supplied like any other
- [ ] T005 Run `pnpm sync:docs`, then `pnpm check:docs` in `relay-tutorial/` — `04-srs.md` is on the mirrored list and a drift check run before the edit passes and then breaks
- [ ] T006 Record the amendment's clause numbers in `specs/035-chapter-3-17/baseline.txt`, and confirm no existing clause was edited — an additive amendment shows what changed in the diff
- [ ] T007 Commit Phase 1

**Checkpoint**: every requirement below can cite a clause that exists.

---

## Phase 2: Foundational — the schema and the signature

**Goal**: a bot is representable, a description is required by the database, and a senderless
write is a compile error.

- [ ] T008 Add `kind` and `description` to `users` in `services/api/src/db/schema.ts` with both CHECK constraints from `data-model.md`. The second — `kind <> 'bot' OR description IS NOT NULL` — is the requirement, not a nicety: it makes a bot without a description unrepresentable rather than merely refused
- [ ] T009 Write `services/api/migrations/0013_bot_users.sql` by hand in the house style. `drizzle-kit` emitted a four-migration backlog in the last feature and its output was not used
- [ ] T010 [P] Comment the CHECK naming the other constrained columns in this schema — `channels_type_check`, `members_role_check`, `memberships_role_check` — the way chapter 3.15 made the two role CHECKs name each other. One word apart is how `admin` nearly reached a channel member
- [ ] T011 **Confirm the default needs no backfill**: `ADD COLUMN … NOT NULL DEFAULT 'person'` is metadata on Postgres 11+, which chapter 3.16 measured for `last_activity_at`. Record the migration's wall-clock time in `baseline.txt` rather than assuming it
- [ ] T012 **Make `userId` REQUIRED** in `repository.sendMessage`'s parameter object — `services/api/src/db/repository.ts`. This is SC-003's mechanism: a senderless write becomes a compile error rather than a test somebody has to remember
- [ ] T013 Run `pnpm typecheck` and record **how many call sites the compiler names**, in `baseline.txt`, against this file's predicted 27. A number that differs is a count that moved and the difference is the finding
- [ ] T013a **This is SC-003a's evidence and it is not a failing test.** Record the `typecheck` transcript in `baseline.txt` as the proof that no write path can omit a sender — a compile-time guarantee has no red test to watch, so removing the constraint and watching the compiler is the only equivalent. Every other removal test in this feature stays a failing test; this one cannot be, and the chapter says why
- [ ] T014 Fix the in-process callers the compiler names, in `idempotency.itest.ts` (11), `repository.itest.ts` (6), `history-drift.itest.ts` (3), `history.itest.ts` (2), `channels.itest.ts` (2), `quotas.itest.ts`, `outbox.itest.ts`, `backfill.itest.ts` — **each gets a real user, not a placeholder**. A fixture that invents `userId: "x"` to satisfy a compiler is a test that stopped meaning what it meant
- [ ] T014a **`repository.itest.ts`'s unattributed-last-message test cannot be fixed this way** (R8). Its subject IS a senderless row, so it must construct one by raw SQL the way chapter 3.16's tombstone test does, and say why in the test
- [ ] T015 Re-run the catalogue's classification and record whether the table count moved — `services/api/src/isolation/tenant-scope.itest.ts`. It should not: this feature adds columns, not tables. **A move means a table arrived that no task named**
- [ ] T016 Commit Phase 2

**Checkpoint**: the compiler, not a test, now guarantees every message has a sender.

---

## Phase 3: User Story 1 — a customer names the software that posts (P1)

**Goal**: a tenant creates a bot with a description and reads it back.

**Independent test**: create a bot over the public API, read the profile, confirm the
description and that the record says it is software.

- [ ] T017 [US1] Add `kind` and `description` to `upsertUserEntrySchema` in `services/api/src/users/users.schema.ts` — `description` required when `kind` is `bot`, refused when it is `person`. **`kind` is optional and MUST NOT be defaulted in the schema** (FR-002b): the default belongs at creation, and a schema default makes "absent" indistinguishable from "person" before anything can compare it to the stored row
- [ ] T018 [US1] Extend `upsertUser` in `services/api/src/db/repository.ts` to carry both, and to report a kind change rather than performing one
- [ ] T019 [US1] Report a kind change as a **per-entry status `kind_conflict`** in `services/api/src/users/users.service.ts` — a fourth status beside `created`, `updated` and `revived`, in a **200** response (FR-002a). **Not a 400**: zod cannot see the stored row, and collapsing it into one status code would fail a batch of 100 because of entry 7, which is what chapter 3.16's per-entry array exists to prevent
- [ ] T019a [US1] Apply the `'person'` default **only when the row is created** — `services/api/src/db/repository.ts`. An entry omitting `kind` for an existing row asks for no change; treat absent as `'person'` and a bot cannot be edited through the upsert at all
- [ ] T020 [P] [US1] Return `kind` and `description` from the profile read in `services/api/src/users/users.service.ts` — `kind` on every user, `description` null for a person. FR-003 is satisfied by returning it, not by documenting it
- [ ] T021 [P] [US1] Allow `description` on `PATCH /v1/users/:externalId` and refuse `kind` there — `services/api/src/users/users.schema.ts`
- [ ] T022 [P] [US1] Test the round trip: create a bot, read it, update the description, read it again — `services/api/src/users/users.itest.ts`
- [ ] T023 [P] [US1] Test that a bot with no description is refused with the field named, and that the **database** refuses it too, by attempting the insert directly — `services/api/src/db/repository.itest.ts`. Validation and the constraint are two guarantees and only one of them survives a new caller
- [ ] T024 [P] [US1] Test that a kind change reports `kind_conflict` in **both** directions, in a **200** whose other entries still succeeded — `services/api/src/users/users.itest.ts`. A batch where entry 7 conflicts and entries 0–6 and 8–99 are written is the assertion; a 400 would prove the opposite
- [ ] T024a [P] [US1] Test that **omitting `kind` while updating an existing bot's description succeeds** — the case FR-002b exists for, and the one a schema default silently breaks — `services/api/src/users/users.itest.ts`
- [ ] T025 [P] [US1] Test that setting a bot's description to null is refused — `services/api/src/users/users.itest.ts`
- [ ] T026 [US1] **Confirm the derived target list did not move** — `services/api/src/isolation/targets.itest.ts`. No route was added, so it stays at 38; it failed on the build that added each of six routes last feature, five separate times
- [ ] T027 Commit Phase 3

**Checkpoint**: a tenant can name its software, and the database holds the requirement.

---

## Phase 4: User Story 2 — a credential cannot post as a person (P1)

**Goal**: every send names a sender, an application credential may name only a bot, and the
refusals reveal nothing.

**Independent test**: post with an API key naming a bot (201), naming a person (403), naming
nothing (400), naming a foreign bot (400, byte-identical to a nonexistent one).

- [ ] T027a [US2] **Declare `@Accepts("application", "user")` on `MessagesController`** — `services/api/src/messages/messages.controller.ts`. It declares none today and relies on `credential.guard.ts`'s `EITHER` fallback, which is the fallback chapter 3.15's own comment names as what let a user token through unnoticed. Behaviour is unchanged — `EITHER` is exactly those two — but this feature makes the route's behaviour branch on the class, and **every comparable route declares**: `channels.controller.ts`, `users.controller.ts`, `dev-token.controller.ts` and the read-position route's method-level pair
- [ ] T028 [US2] Add `user` to `sendMessageBodySchema` in `services/api/src/messages/messages.schema.ts`
- [ ] T029 [US2] Resolve the sender per credential class in `services/api/src/messages/messages.controller.ts`: the body's `user` for an application credential, the token's subject for a user token, and **refuse a body `user` on a user token** with `field: "user"`
- [ ] T029a [US2] Add `sender_not_permitted` to `packages/protocol/src/codes.ts` (FR-007a), with the comment naming its two siblings — `wrong_credential_type` is the wrong class, `wrong_credential_service` the wrong service, this is the wrong kind of user
- [ ] T029b [US2] **Update `codes.test.ts`'s exact-set assertion, and record that it failed on the build that added the code** — `packages/protocol/src/codes.test.ts`. An exact-set assertion is the only kind that makes a new code a decision rather than an accident; chapter 3.16 recorded the same beat for close code 4003
- [ ] T029c [P] [US2] Add the code to `docs/08-error-reference.md` so `docsUrl` resolves against a real anchor, then `pnpm sync:docs` and `pnpm check:errors` — a code whose page does not exist is the debt chapter 3.14 closed
- [ ] T030 [US2] Enforce "an application credential may send only as a bot" in `services/api/src/messages/messages.service.ts` — 403 `sender_not_permitted`. **The service and not the repository**, because the repository cannot see the credential class and should not learn it (R5)
- [ ] T031 [US2] Refuse an unresolvable sender with `400` and `field: "user"`, **identically for a foreign bot and for one that exists nowhere** — `services/api/src/messages/messages.service.ts`
- [ ] T032 [US2] **Put the refusals in the documented order** (`contracts/sending.md`): ban, visibility, archive, then sender-resolves, then may-this-credential-send-as-it. Sender resolution comes *before* the bot check for the reason archive comes after visibility — the second refusal names a fact about a user the caller may not be able to confirm exists
- [ ] T032a [US2] **Assert the wire carries `sender_not_permitted` and not `forbidden`** — `services/api/src/messages/messages.itest.ts`. `ProtocolErrorFilter`'s ladder maps 403 to `forbidden`, and this is the only code in the feature that collides with a ladder entry. The filter prefers an explicitly named code; that preference is what this asserts, and the filter's own comment records that 403's fallback arrived late
- [ ] T033 [P] [US2] Test the four outcomes for an application credential — bot 201, person 403, absent 400, unresolvable 400 — in `services/api/src/messages/messages.itest.ts`
- [ ] T034 [P] [US2] Test that a user token still sends as its subject and that a body `user` is refused — `services/api/src/messages/messages.itest.ts`
- [ ] T035 [US2] **Add the foreign-sender pair to the oracle** — `services/api/src/isolation/gauntlet.itest.ts`. A bot of another tenant and an identifier that exists nowhere must answer byte-identically under `withoutRequestId`. This is a **new foreign-identifier surface on an existing route**, which is what the constitution check flagged
- [ ] T036 [P] [US2] Test that the control works first: the same credential, the same channel, its own bot — 201. Chapter 3.12's fourteen green tests compared two refusals and meant nothing
- [ ] T037 [US2] **Remove the bot check and confirm T033's 403 goes red**, then restore — `services/api/src/messages/messages.service.ts`
- [ ] T038 [US2] **Remove the sender-resolution refusal and confirm the oracle pair goes red**, then restore. Record which of the two removals the oracle notices and which it does not: chapter 3.15 found a suite is blind to an inner check a live outer one masks
- [ ] T039 Commit Phase 4

**Checkpoint**: no send reaches storage without a sender the caller was entitled to name.

---

## Phase 5: User Story 3 — a bot is a user, and is not an account (P2)

**Goal**: a bot inherits everything keyed on a user, and can obtain no credential.

**Independent test**: add a bot to a channel, see it in the members list with a role; request a
token for it and be refused.

- [ ] T040 [US3] Refuse the mint for a bot in `services/api/src/auth/dev-token.controller.ts` — **404, `not_found`**. There is no "identical to unknown" available: an unknown identifier answers 200 on this route because chapter 3.16 made it create a person, so any refusal distinguishes a bot. **That is not an oracle here** — this route and `GET /v1/users/:externalId` are both `@Accepts("application")`, so a caller who reaches the refusal can already read that user's `kind` from their profile
- [ ] T041 [US3] Ensure implicit creation still creates a **person** for an unknown identifier, and never converts an existing bot — `services/api/src/auth/dev-token.controller.ts`
- [ ] T042 [P] [US3] Test the mint's three cases — unknown creates a person and mints, a person mints, a bot is refused 404 — `services/api/src/auth/credentials.itest.ts`. **Do not assert byte-identity with the unknown case**: it succeeds, so there is nothing to be identical to, and an earlier draft of this task asked for a comparison that cannot exist
- [ ] T043 [P] [US3] Test that a bot can be a channel member with a role, appears in the member list, and that the listing, unread count and last-message field are unaffected by its presence — `services/api/src/users/users.itest.ts`
- [ ] T043a [P] [US3] Test **a bot's own channel listing** — `GET /v1/users/:botExternalId/channels` — and its read position (FR-004). A bot is a user, so the route answers for one; its unread count is the whole history because nothing ever acknowledges for it, and that is worth asserting rather than leaving a reader to wonder
- [ ] T044 [P] [US3] Test that a bot can be banned and that its sends are then refused, and that it can be deleted with its messages surviving and still attributed — `services/api/src/users/users.itest.ts`
- [ ] T045 [US3] **Remove the `kind` read from the send's bot check and confirm T033's 403 goes red**, then restore (the column table's removal test)
- [ ] T046 [US3] **Remove the `description` read from the profile response and confirm T022 goes red**, then restore
- [ ] T047 [US3] **Decide and record whether a bot counts toward `usage_active_users`** (FR-018) — measured before and after a bot's send, in `baseline.txt`. Active users are a billing dimension (FR-TEN-08, chapter 3.10), and charging a customer for their own software is a product question this feature must answer on purpose rather than by accident
- [ ] T047a [US3] **Name the assertions T047's decision moves, and show one going red for the other choice.** Five already pin exact counts — `services/api/src/quotas/quotas.itest.ts:71,78,103` (`toBe(2)`, `toBe(0)`, `toBe(0)`) and `services/api/src/users/users.itest.ts:723,728` — so whichever way the decision goes, one of the two behaviours has no test until this task writes it
- [ ] T048 [P] [US3] State in `baseline.txt` that a bot's `read_positions` row is written by nothing and read by nothing, so a reader does not go looking for a bot's unread count. It is not a new dead column — it is an existing table holding a row that will never exist
- [ ] T049 Commit Phase 5

**Checkpoint**: a bot is a first-class user everywhere except at the door.

---

## Phase 6: The rows that came before

**Goal**: messages already stored with no sender behave the same way on every read path.

- [ ] T050 **Measure how many senderless rows exist** in the lane, per environment, and record it in `baseline.txt`. The question is not the lane's number but whether the behaviour is reachable at all — the column is nullable and any deployment has them
- [ ] T051 Decide FR-013 and record it: what a client sees for a legacy senderless message on history, on the listing's `last_message`, and on a resume. **The answer must be the same on all three**
- [ ] T052 [P] Test history's answer — `services/api/src/messages/history.itest.ts`
- [ ] T053 [P] Test the listing's answer — `services/api/src/db/repository.itest.ts`, extending T014a's raw-SQL row
- [ ] T054 [P] Test the resume's answer — `services/gateway/src/public-surface.itest.ts`, which is where `toFrame`'s drop is already pinned
- [ ] T054a **Test the WEBHOOK payload's answer** (FR-012a) — `services/api/src/outbox/event.test.ts` and `services/api/src/webhooks/deliveries.itest.ts`. `MessageCreatedData.user` is `string | null` and is what a customer's own endpoint receives (FR-WHK-02); FR-WHK-03 retries for up to two hours, so an event for a legacy senderless message can be delivered after this chapter ships. **This is the fourth read path and the only one that leaves the platform** — it was missing from the enumeration until the first analysis pass
- [ ] T054b Decide and record whether `MessageCreatedData.user` stays nullable, in `baseline.txt`. New events cannot carry a null; the type describes what a subscriber may still receive from the retry queue
- [ ] T055 **Re-examine chapter 3.16's `last_message.user: null` test rather than deleting it** (R8). Its arm now covers legacy rows only, and a test whose subject changed needs its comment changed
- [ ] T056 **Assert that chapter 3.16's frame-shape assertion still passes** — `services/gateway/src/isolation.itest.ts`. A chapter that changes the sender model and leaves the frame contract alone is making a claim a reader will not believe without one
- [ ] T057 Commit Phase 6

**Checkpoint**: nothing that was readable stopped being readable.

---

## Phase 7: The callers

**Goal**: every send site in the workspace names a sender, and the sealed integration passes
without being corrected.

- [ ] T058 Fix the HTTP send sites in `services/api/src/isolation/gauntlet.itest.ts` (14) — these are attack shapes, so **each must keep attacking what it attacked**. A gauntlet test that starts passing because its send now fails validation has stopped testing isolation
- [ ] T059 [P] Fix `services/api/src/messages/messages.itest.ts` (8)
- [ ] T060 [P] Fix `services/api/src/limits/limits.itest.ts` (4) — the rate-limit suites count requests, so a send that now 400s still counts and the assertions may pass for the wrong reason. **Check what each assertion would do if every send were refused**
- [ ] T061 [P] Fix `services/api/src/users/users.itest.ts` (3), `services/api/src/auth/credentials.itest.ts` (3), `services/api/src/channels/channels.itest.ts` (3)
- [ ] T062 [P] Fix `services/gateway/src/public-surface.itest.ts` (2), `services/gateway/src/isolation-fixtures.ts` (2), `services/gateway/src/limits.itest.ts` (1), `services/api/src/internal/internal.itest.ts` (1)
- [ ] T063 [P] Fix `packages/e2e/src/tuan.itest.ts` (2)
- [ ] T064 **`packages/outsider/src/integrate.itest.ts` LAST, and it is the one that matters.** It is sealed from workspace code and stands for an external developer. Its script must **create a bot and send as it**, demonstrating the flow a customer follows
- [ ] T065 **Run `pnpm test:outsider` and record whether it passed first time.** Chapter 3.14's verdict says a suite that passes *because a failing test corrected it* is the assistance the Phase 2 exit criterion forbids. If it needed correcting, the documentation was insufficient and that is the finding
- [ ] T066 Update the published quickstart if it sends — `relay-tutorial/`, and NFR-USE-03 has CI execute it against the published documentation
- [ ] T067 Commit Phase 7

**Checkpoint**: an outsider following the documentation can send a message.

---

## Phase 8: Verification

- [ ] T068 Run every gate and record the **exit code** of each, not a grep over its output: `pnpm lint`, `pnpm typecheck`, `pnpm build`, `pnpm turbo run test`, `pnpm test:integration`, `pnpm coverage`, `pnpm test:outsider`
- [ ] T069 [P] Add coverage ratchets for anything this feature adds, and **re-earn the pins it moves**. `repository.ts` sits at 91 branches after the last feature raised it from 90
- [ ] T070 [P] Enumerate the branch arms this feature adds and show each covered, per arm rather than by a file percentage — `baseline.txt`
- [ ] T071 **Check that every new repository function is exercised in-process**, not only through the gateway's api child whose coverage is not attributable. `functions: 100` on `repository.ts` is the measurement that answers it
- [ ] T072 Write `specs/035-chapter-3-17/traceability.md`, both directions, and **check FR-CHN-05's row**: chapters 3.15/3.16 recorded it delivered when the clause names three verbs and two were built. A map that claims delivery is the defect this project has now corrected three times
- [ ] T073 [P] Update `docs/04-srs.md`'s verification notes for FR-USR-07 and FR-MSG-10
- [ ] T074 [P] Add the 3.17 row to `docs/07-tutorial-plan.md` with the shipped numbers
- [ ] T075 Run `pnpm sync:docs`, then `check:docs`, `check:errors`, `check:figures`, `check:fences` — in that order and after T073
- [ ] T076 **Decide the lane budget before the battery runs.** The last feature measured 550 tests at 192–197 s against a 240 s bound, and found the lane costs per **suite** rather than per test. This feature adds tests to existing suites and one new suite at most
- [ ] T077 The twenty-run battery, on a machine running nothing else
- [ ] T078 [P] Record what twenty green buys and does not: it rejects a per-run failure rate above 13.91% at 95% confidence, a 5% flake survives it 35.85% of the time, and rejecting one needs 59 runs
- [ ] T079 Commit Phase 8

---

## Phase 9: The chapter

- [ ] T080 **Count the files this chapter teaches and the files it must fence, as two columns**, before writing a word — `baseline.txt`. The last feature conflated them for eight revisions and the ceiling looked comfortable when it was binding
- [ ] T081 Write `relay-tutorial/app/(en)/part-3/chapter-17/<slug>/page.mdx`. The subject is one sentence: a message sent by a customer's server had no sender, and now it has one it chose
- [ ] T082 [P] Write `figures.ts`: the two blast radii, the refusal order with what each reveals, and the identity that was an absence
- [ ] T083 [P] Diff fences at **three lines of context**, verified unique by simulating the checker rather than widened to eight on principle
- [ ] T084 **A path the appendix amends needs its target computed as HEAD-minus-appendix.** A diff straight to HEAD does the appendix's work and leaves its hunk matching 0 times
- [ ] T085 **Re-derive the file count from `git diff --name-only` against `check:fences`** and record whether it moved from T080's. It moved in six of the last feature's eight revisions
- [ ] T086 [P] State the SRS amendment on the page (FR-015): the chapter cites a clause that did not exist when the chapter was specified, and says so
- [ ] T086a [P] **State what an existing caller must change** (FR-011), on the page and not only in a spec: the send body gains a required field for one credential class, and the chapter must not describe that as backwards compatible
- [ ] T086b [P] **State that chapter 3.3's decision is REVERSED, not reinterpreted** (FR-017), and why it was right when it was made — nothing read the sender then, and three chapters since have made the sender decide what is rendered, delivered and seen
- [ ] T087 Add the chapter to `relay-tutorial/lib/tutorial.ts`
- [ ] T088 Count the prose words — inside 2,000–4,000, and **write against the measured rate rather than the nominal one**. The nominal 160 words per file said chapter 3.16 could not be written; it landed at 3,800
- [ ] T089 Commit Phase 9

---

## Phase 10: Translation and publication

- [ ] T090 Translate to `relay-tutorial/app/(vi)/vi/part-3/chapter-17/<slug>/page.mdx`, **assembled mechanically** — split at every fence boundary, translate the prose, copy the fences untouched, then re-split both and compare the fence lists
- [ ] T091 [P] Translate the figure labels; identifiers, table and column names stay English
- [ ] T092 `pnpm check:fences`, and ask it about **files this chapter owns** rather than pages naming it — and separately list this feature's files that no chapter claims, which the checker cannot tell you
- [ ] T093 [P] `pnpm lint`, `tsc`, `pnpm build`, `check:figures`, and the static page count
- [ ] T094 Record the chapter's numbers in `baseline.txt`, both locales
- [ ] T095 Commit Phase 10

---

## Phase 11: Close-out

- [ ] T096 Write `specs/035-chapter-3-17/chapter-notes.md`: the plan against what shipped, including the phases that went badly
- [ ] T097 [P] Write `specs/035-chapter-3-17/gaps.md`, and **carry forward the eight from the last feature that are still open**, with 3.18 and 3.19 as owners where they now have one
- [ ] T098 [P] Record whether the two file counts stayed apart, and what each was at every revision
- [ ] T099 Update `CLAUDE.md` between the `<!-- SPECKIT -->` markers
- [ ] T100 [P] Tick the last task only when it is done, not when it is about to be — chapter 3.12 marked its close-out complete before pushing and had to reopen it
- [ ] T101 Tag `part3-ch17` in all three repositories, confirm each submodule pin matches its HEAD, and push. **Hold the tag if `check:fences` exits 1**

---

## Dependencies

    Phase 1  (the amendment)     blocks everything — principle VI
    Phase 2  (schema, signature) blocks Phases 3-7
    Phase 3  (US1, the bot)      blocks Phase 4 — a send cannot name a bot that cannot exist
    Phase 4  (US2, the send)     blocks Phase 7 — the callers need the rule they are adapting to
    Phase 5  (US3)               independent of Phase 4; needs Phase 3
    Phase 6  (legacy rows)       needs Phase 2's raw-SQL fixture (T014a)
    Phase 7  (the callers)       needs Phases 4 and 5
    Phases 8-11                  sequential

**Parallel within phases**: every `[P]` task touches a different file from its neighbours.
Phase 7's T059–T063 are the widest — five files at once, none sharing a fixture.

## MVP

**Phases 1–4.** A tenant can create a bot, describe it, and send as it; no message reaches
storage without a sender; and an API key cannot post as a person. That is the chapter's claim,
and Phases 5–7 are what make it true everywhere rather than on the happy path.

## The premises this task list rests on, and where each was checked

Five task premises were wrong in the last feature, each costing a wrong attempt. These were
checked against the repository while this list was written:

    upsertUser has no `kind` today                     read, services/api/src/db/repository.ts
    27 repository calls omit userId                    counted, 8 files
    46 HTTP send sites                                 counted, 12 files
    the outsider sends with an API key                 read, integrate.itest.ts:153
    no new route is needed                             the upsert already exists
    users has no kind or description column            read, schema.ts
    the derived target list stands at 38               read, targets.itest.ts

**T047 and T051 are decisions, not implementations** — a bot's billing status and what a legacy
row renders as. Both are flagged so they are answered on purpose.
