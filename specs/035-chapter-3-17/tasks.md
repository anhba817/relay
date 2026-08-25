# Tasks: Chapter 3.17 — the sender a message never had

> **FILE ORDER IS EXECUTION ORDER; TASK IDS ARE STABLE LABELS.** Eleven analysis passes
> inserted tasks with sub-letters, so the ids are no longer monotonic — `T013` precedes `T012a`,
> `T024` precedes `T023a`, and five more. They are **not** renumbered: principle VI does not
> reuse identifiers, and 146 ids are cited across eleven passes of records. Run the file top to
> bottom.
>
> **`[P]` means the task shares no artifact with another `[P]` task in its phase**, checked by
> `sweep.py` rather than asserted. Seventeen markers were wrong when that check was first run in
> pass 11 — eight of them writing `users.itest.ts` at once, which is how 3.16 destroyed a shared
> fixture three times in one feature.

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

- [X] T000 **Verify both clause identifiers are free AND that no clause already covers the ground** (FR-015b, FR-015f, FR-015g) — `grep -oE "FR-(USR\|MSG)-[0-9]+" docs/04-srs.md | sort -u`. FR-USR runs **01-06**, so `FR-USR-07` is free. FR-MSG runs **01-14**, so the sender clause is **`FR-MSG-15`** — the feature specified `FR-MSG-10` in six places and it is taken: *"History responses shall include tombstones"*, P2, cited by the personas table. **Six artifacts agreed with each other and all six were wrong**, because the contradiction lived in a file none of them quoted. Corrected in analysis pass 9; this task is the check that would have caught it. **Then read the section, not just the identifiers** — pass 13 found `FR-MSG-13`, *"The system shall support sending a message on behalf of any user via API key, for backend-originated messages"*, four rows below where `FR-MSG-15` goes. Enumerating identifiers answers *is this number free*; it never answers *does a clause already say this*, and `check:srs` cannot help because it asserts uniqueness and deliberately does not read meaning
- [X] T001 Add `FR-USR-07` to `docs/04-srs.md` §4.3: customers may create bot users representing their own software, carrying a description, which cannot authenticate. P2, verification `T` (FR-015)
- [X] T002 **Amend `FR-MSG-13` IN PLACE** (FR-015f) — `docs/04-srs.md` §4.5, line 394. It reads *"The system shall support sending a message on behalf of any user via API key, for backend-originated messages"*; **"any user" becomes "a bot user of that tenant"**. This is the one edit in the whole amendment that is not additive, and it is not optional: leaving the clause as written and adding FR-MSG-15 beside it makes the SRS say both that a key may send as anyone and that it may send only as a bot, which is the implicit resolution the Governance section forbids. Keep P2 and verification `T` — the priority and the method do not change, only the scope
- [X] T002a Add `FR-MSG-15` to `docs/04-srs.md` §4.5 for the half that is genuinely new (FR-015f): **every message shall carry a sender**. P1, verification `T`. FR-MSG-13 authorises a key to name someone; nothing before this clause requires that every message have a sender at all
- [X] T002c **Amend `FR-RTL-05` IN PLACE** (FR-018c) — `docs/04-srs.md` §4.8, line 449. It enforces quotas on *"messages sent, unique active users, and connection-minutes"*; **the active-user dimension becomes "unique active persons"**. Second of two non-additive edits in this amendment. **FR-ANL-05 (line 465) is NOT touched** — it meters *unique active users* and keeps counting bots, which is what makes a bot billed and exempt at the same time. Metering and enforcement were already two clauses in two families before this chapter; pass 6 derived that split by reading `repository.ts` and pass 14 found the SRS had it first
- [X] T002d **Cite FR-RTL-08 and state the exception** (FR-018d) — `docs/04-srs.md`, in the amendment blockquote. *"Quota exhaustion shall degrade predictably: sends rejected with a specific error code"* — a bot's send is now not rejected at exhaustion. **Uncited, that is a defect report; cited, it is a decision**
- [X] T002e **Record what the other families gave, including the two that gave nothing** (FR-015g) — in `baseline.txt`. Pass 14 read all seven clause families this chapter cites. **FR-AUT-09** provides the dev-token mint *"in the `development` environment only"* and T040 refuses a bot there — **not an in-place amendment**, because the clause grants an endpoint's existence and carries no universal quantifier, unlike FR-MSG-13's *"any user"* and FR-RTL-05's unqualified *"unique active users"*. **FR-MOD-03** requires every moderation action be audit-logged and **no audit log exists** — banning a person is already unlogged, so a bannable bot (FR-005c) adds no violation to a P3 clause nothing has built. **FR-MOD-04**'s erasure endpoint is not `deleteUser`: SC-007 claims a deleted bot keeps its attribution, and erasure removes everything, so the chapter must not let one claim be read as the other. **EIR-API-07**'s OpenAPI spec does not exist anywhere in the repository, so nothing to update. **Recording the empty answers is the point** — the next chapter starts from seven families read rather than one
- [X] T002b **Record that FR-MSG-13 is being MET, not introduced** (FR-015f, FR-017) — in the amendment blockquote and in `baseline.txt`. The clause predates chapter 2.2's route; chapter 3.3 satisfied it by sending unattributed, and `services/api/src/messages/messages.controller.ts` has cited it that way ever since: *"A tenant's own server sending on a customer's behalf is FR-MSG-13, not a mistake."* **A requirement satisfied by doing the opposite of what it says is harder to see than one nobody wrote** — thirteen analysis passes read the claim that this requirement did not exist (FR-015)
- [X] T003 Add the amendment blockquote after §4.3's table in `docs/04-srs.md`, in the form the document already uses for FR-TEN-05: what changed, why, and that **FR-MSG-01 is unchanged** — it describes what a message contains and a later reader must not look for the sender rule there (FR-015)
- [X] T004 Record in `docs/04-srs.md` that FR-USR-01's "Relay shall not generate end user identifiers" still holds for bots: a bot's identifier is customer-supplied like any other
- [X] T004d [P] **Correct `docs/07-tutorial-plan.md`'s 3.17 row** — it ends *"Amends the SRS, which has no bot concept"*, the same omission FR-015 carried, in a fourth place. It amends the SRS **and the SAD**
- [X] T004a **Amend the SAD's `users` DDL** (FR-015a) — `docs/05-sad.md` ~341. `CREATE TABLE users` lists eight columns; add `kind` and `description` with both CHECK constraints. **Follow the document's own idiom**: `channels.type TEXT NOT NULL CHECK (type IN ('public','private'))` is twelve lines below it and is the shape `data-model.md` chose independently, so the amendment cites a precedent rather than introducing a pattern. FR-015 named the SAD and then amended only the SRS for eight analysis passes; the last feature amended `05-sad.md` five times
- [X] T004e **Review all thirteen constitution MUST clauses against this chapter and record the verdict** — in `baseline.txt`. Done in analysis pass 10: eleven are untouched, **VI's quickstart clause was in violation before this chapter and T063b closes it**, and FR-ANL-06's 0.1% reconciliation (constitution line 90) is unbuilt but will inherit the two-counts divergence (T047d). The two that needed checking rather than asserting were the analytical store's no-message-text rule — `webhooks/analytics.ts` carries no `description`, `displayName` or `text` — and the reconciliation. **The point of the record is that the next chapter starts from thirteen checked clauses rather than from principle VI alone**, which is what nine passes did
- [X] T004b **Record which governing documents are deliberately NOT amended** (FR-015a) — in `baseline.txt`. The last feature amended seven files under `docs/`; this one amends `04-srs.md`, `05-sad.md`, `07-tutorial-plan.md` and `08-error-reference.md`. `02-personas.md`, `03-journey-map.md` and `06-adr-deep-dives.md` are unamended on purpose — the ADR deep-dives were grepped for a bot, service-account or unattributed-send claim and hold none. **A bot as an actor class in `02-personas.md` is a judgement this chapter declines**, and saying so is what stops the next reader re-deriving it
- [X] T004c **Write `check:srs` and wire it into CI beside `check:docs`** (FR-015c) — **built in analysis pass 9, hardened in pass 10, and run before and after this amendment (243/243 then 245/245)** — asserts every clause identifier in `docs/04-srs.md` is defined exactly once. `check:docs` compares each mirrored document to its canonical source, which is **drift, not validity**, so a duplicate identifier passes it. It enforces **principle VI's** *"never reused"*, so it is a constitution gate rather than a convenience. **Cover every class the document uses and fail on one it does not know** — the first version matched three-part ids only and silently skipped `DR-01`, `CON-06` and all 22 `EIR-*` rows, 192 of 243, while printing "192 clause rows" as though that were the document. Green now at **243 rows, 243 unique, six classes**; tested red three ways (a duplicate `FR-MSG-10`, a duplicate `DR-01`, an unclassified `XYZ-01`). Pass 8's rule applies: a checker that cries wolf on a healthy tree is how a real problem hides, so run it before the amendment and confirm it is silent
- [X] T005 Run `pnpm sync:docs`, then `pnpm check:docs` in `relay-tutorial/` — `04-srs.md` is on the mirrored list and a drift check run before the edit passes and then breaks
- [X] T006 Record the amendment's clause numbers in `specs/035-chapter-3-17/baseline.txt`, and confirm no existing clause was edited — an additive amendment shows what changed in the diff. **And re-run `check:srs` after the edit**: an additive amendment that reuses an identifier is still additive in the diff, which is exactly how `FR-MSG-10` survived six artifacts
- [X] T007 Commit Phase 1

**Checkpoint**: every requirement below can cite a clause that exists.

---

## Phase 2: Foundational — the schema and the signature

**Goal**: a bot is representable, a description is required by the database, and a senderless
write is a compile error.

- [ ] T008 Add `kind` and `description` to `users` in `services/api/src/db/schema.ts` with both CHECK constraints from `data-model.md`. The second — `kind <> 'bot' OR description IS NOT NULL` — is the requirement, not a nicety: it makes a bot without a description unrepresentable rather than merely refused (FR-003)
- [ ] T009 Write `services/api/migrations/0013_bot_users.sql` by hand in the house style. `drizzle-kit` emitted a four-migration backlog in the last feature and its output was not used. **The `migrations/meta/` journal is not updated** — chapters 3.15 and 3.16 hand-wrote 0011 and 0012 without touching it and both lanes pass, which is the precedent rather than an oversight (FR-003)
- [ ] T010 [P] Comment the CHECK naming the other constrained columns in this schema — `channels_type_check`, `members_role_check`, `memberships_role_check` — the way chapter 3.15 made the two role CHECKs name each other. One word apart is how `admin` nearly reached a channel member — writes `services/api/src/db/schema.ts` (FR-003)
- [ ] T011 **Confirm the default needs no backfill**: `ADD COLUMN … NOT NULL DEFAULT 'person'` is metadata on Postgres 11+, which chapter 3.16 measured for `last_activity_at`. Record the migration's wall-clock time in `baseline.txt` rather than assuming it (FR-002e)
- [ ] T012 **Make `userId` REQUIRED** in `repository.sendMessage`'s parameter object — `services/api/src/db/repository.ts`. This is SC-003's mechanism: a senderless write becomes a compile error rather than a test somebody has to remember (FR-006)
- [ ] T013 Run `pnpm typecheck` and record **how many call sites the compiler names**, in `baseline.txt`, against this file's predicted 27. A number that differs is a count that moved and the difference is the finding. **Three numbers describe this and only one is 27**: `grep -c 'sendMessage('` across `services/api/src` gives **100**, R1's blast radius counts **46** HTTP send sites, and the call sites that *omit* `userId` — the only ones the compiler can name — are **27**. Verified in analysis pass 8 by walking each call's argument object; per file: `idempotency` 11, `repository.itest` 6, `history-drift` 3, `history` 2, `channels` 2, and one each in `quotas`, `outbox`, `backfill`. A reader who reaches for the obvious grep gets 100 and concludes the prediction is off by 73
- [ ] T012a **Remove BOTH of `sendMessage`'s dead `userId` guards, and grep for the class rather than the two instances** — `services/api/src/db/repository.ts`. Once `userId` is required the condition is always true, so the branch is unreachable and its comment describes a state that can no longer exist. **Fourth time this project has met a guard that stopped meaning anything**: `addMember`'s `rowCount ?? 0` (3.12), `upsertUser`'s second throw and `(row.metadata ?? {})` (3.16). Tightening a type makes its runtime guards dead, and the coverage ratchet finds them afterwards — this one is found before. **Run the grep first, then classify every hit — do not sweep.** `grep -n 'userId [!=]== undefined' services/api/src/db/repository.ts` returns **seven**, and they are not the same thing: (FR-006)

      3613  the ban check                       DEAD — remove the gate, keep the check
      3681  private-channel membership          NOT DEAD IN EFFECT — see T012b, do not touch here
      3872  the usage_active_users insert       DEAD — remove the gate, keep the insert
      3902  mayHaveAddedUser (compound)         DEAD conjunct; the `userRef !== null` half stays
      4042  the active-user ceiling's return    DEAD disjunct; the `hard === null` half stays
      4241  channelVisibleTo(id, userId?)       LEGITIMATELY OPTIONAL — DO NOT TOUCH
      4302  listMessages                        LEGITIMATELY OPTIONAL — DO NOT TOUCH

**Pass 6 wrote "fix the pattern, not the instances" into this task and pass 7 ran the grep.** Three of the seven are dead, two are in methods whose `userId` is optional by design, one is a compound where only half goes, and one changes what a customer's server can do. A generalisation needs its own verification step: the rule is not *the pattern is dead*, it is *`userId` is required in `sendMessage` and nowhere else yet*
- [ ] T012b **KEEP THE APPLICATION KEY'S PRIVATE-CHANNEL ACCESS** (FR-019, FR-019a, FR-019b) — `services/api/src/db/repository.ts` ~3681. The gate is `if (channel.type === "private" && userId !== undefined)`, and a key send skips the membership check today because there is no user. Require `userId` and the gate is always true, the check fires, and a bot that is not a member is refused `ChannelNotFoundError`. **`services/api/src/messages/messages.itest.ts:194` is a named test that goes red** — *"accepts an application key's send to the same private channel (FR-005)"* — and FR-005 is a delivered requirement of a published chapter. The gate becomes conditional on the **sender being a person**, which needs the sender's `kind`: it is already read for the ban check three checks above, so read it once and use it twice rather than adding a second lookup on the send path
- [ ] T012c **Both halves in one test** (SC-012) — `services/api/src/messages/messages.itest.ts`. A bot's key-authenticated send to a private channel it is not a member of succeeds; a person's token send to the same channel is still refused, indistinguishably. **A test that checks only the bot passes when the gate has been deleted outright**, which is the change that breaks chapter 3.15's refusal. The pair is the oracle, the way `withoutRequestId` pairs are. **Use the fixtures that are already there and do not modify them**: `messages.itest.ts` sets up `privateChannelId`, a `member` and a same-tenant `stranger` at lines 33-61, and its own comment records a prior task that *"failed on its control: T057 above removes `insider` from privateChannelId"* — that membership is load-bearing for another test. Add a bot; add nothing to the channel. **Fourth time in two features that a shared fixture is the hazard** (3.16's T144 deleted one three times)
- [ ] T012d **A bot may be banned, and its send is refused** (FR-005c, SC-013) — `services/api/src/messages/messages.itest.ts`. Removing the gate at 3613 makes the ban check run against a bot's sender id for the first time; `users.banned_at` was always there. Ban a bot, send as it over the key, assert the refusal is byte-identical to a foreign sender's. **The decision is that this is a feature**: a ban stops a runaway integration without deleting the identity its messages are attributed to, and the chapter states it rather than letting the behaviour arrive as a side effect of a removed `if`
- [ ] T013a **This is SC-003a's evidence and it is not a failing test.** Record the `typecheck` transcript in `baseline.txt` as the proof that no write path can omit a sender — a compile-time guarantee has no red test to watch, so removing the constraint and watching the compiler is the only equivalent. Every other removal test in this feature stays a failing test; this one cannot be, and the chapter says why
- [ ] T014 Fix the in-process callers the compiler names, in `idempotency.itest.ts` (11), `repository.itest.ts` (6), `history-drift.itest.ts` (3), `history.itest.ts` (2), `channels.itest.ts` (2), `quotas.itest.ts`, `outbox.itest.ts`, `backfill.itest.ts` — **each gets a real user, not a placeholder**. A fixture that invents `userId: "x"` to satisfy a compiler is a test that stopped meaning what it meant (FR-006)
- [ ] T014a **`repository.itest.ts`'s unattributed-last-message test cannot be fixed this way** (R8). Its subject IS a senderless row, so it must construct one by raw SQL the way chapter 3.16's tombstone test does, and say why in the test (FR-014)
- [ ] T015 Re-run the catalogue's classification and record whether the table count moved — `services/api/src/isolation/tenant-scope.itest.ts`. It should not: this feature adds columns, not tables. **A move means a table arrived that no task named**
- [ ] T016 Commit Phase 2

**Checkpoint**: the compiler, not a test, now guarantees every message has a sender.

---

## Phase 3: User Story 1 — a customer names the software that posts (P1)

**Goal**: a tenant creates a bot with a description and reads it back.

**Independent test**: create a bot over the public API, read the profile, confirm the
description and that the record says it is software.

- [ ] T017 [US1] Add `kind` and `description` to `upsertUserEntrySchema` in `services/api/src/users/users.schema.ts` — `description` required when `kind` is `bot`, refused when it is `person`. **`kind` is optional and MUST NOT be defaulted in the schema** (FR-002b): the default belongs at creation, and a schema default makes "absent" indistinguishable from "person" before anything can compare it to the stored row
- [ ] T018 [US1] Extend `upsertUser` in `services/api/src/db/repository.ts` to carry both, and to report a kind change rather than performing one (FR-002)
- [ ] T019 [US1] Report a kind change as a **per-entry status `kind_conflict`** in `services/api/src/users/users.service.ts` — a fourth status beside `created`, `updated` and `revived`, in a **200** response (FR-002a). **Not a 400**: zod cannot see the stored row, and collapsing it into one status code would fail a batch of 100 because of entry 7, which is what chapter 3.16's per-entry array exists to prevent
- [ ] T018a [US1] **Permit `person → bot` when the row has never sent a message** (FR-002d) — `services/api/src/db/repository.ts`. `bot → person` stays refused unconditionally. Without this the natural ordering traps a customer: `POST …/members` creates any unknown identifier as a **person** because `createUser` cannot set `kind`, so "add support-bot to #support" then "register the bot" makes the bot permanently impossible
- [ ] T018b [US1] **Measure the promotion's cost and record it** (FR-002e) — `messages.user_id` carries no index, so "has this user ever sent a message" is a filtered scan. R4 measured a full message scan at 159 ms against 1,000,000 rows. Record the real number rather than adding an index nothing else needs
- [ ] T018c [US1] Test the promotion in all three states: never sent → promoted; has sent → `kind_conflict`; `bot → person` → `kind_conflict` regardless — `services/api/src/users/users.itest.ts` (FR-002d)
- [ ] T018d [US1] **Test the trap in the order a customer hits it**: add an unknown identifier as a channel member, then register it as a bot, and confirm it works — `services/api/src/users/users.itest.ts`. This is the assertion the escape exists for, and it fails without T018a (FR-002d)
- [ ] T019a [US1] Apply the `'person'` default **only when the row is created** — `services/api/src/db/repository.ts`. An entry omitting `kind` for an existing row asks for no change; treat absent as `'person'` and a bot cannot be edited through the upsert at all (FR-002b)
- [ ] T020 [P] [US1] Return `kind` and `description` from the profile read in `services/api/src/users/users.service.ts` — `kind` on every user, `description` null for a person. FR-003 is satisfied by returning it, not by documenting it
- [ ] T021 [P] [US1] Allow `description` on `PATCH /v1/users/:externalId` and refuse `kind` there — `services/api/src/users/users.schema.ts`. **NOT `.nullable()`, and the comment must say why** (FR-004b). Every sibling in `userProfileBodySchema` is nullable on purpose, and the schema's own comment teaches the rule: *"`null` CLEARS, and it is distinct from absent."* Extend it to `description` and `PATCH {"description": null}` sets null on a bot, `users_bot_description_check` raises, and the customer gets a **500** for a request the boundary should have refused. Nullability buys nothing here — a bot must never clear it, a person may never have one — so the field is settable and not clearable. **The comment is the artifact that would put `.nullable()` back**, which is why it carries the reason and not just the absence
- [ ] T021a [US1] **Update the two exact-shape assertions the profile's new fields break**, and record that they broke: `services/api/src/users/users.itest.ts:503` (`expect(body).toEqual({external_id, display_name, avatar_url, metadata})`) and `:760` (the revived-user test's `expect(back).toEqual({…})`). Enumerated by grepping every `toEqual({…})` and `Object.keys(…)` over a response this feature touches — **two of twenty-nine break**, and the field-level `.toBe(…)` assertions in the same file survive. An exact-shape assertion failing on an additive change is the instrument working; the count is recorded so the next feature greps once rather than finding them one per analysis pass (FR-004)
- [ ] T022 [US1] Test the round trip: create a bot, read it, update the description, read it again — `services/api/src/users/users.itest.ts` (FR-001)
- [ ] T023 [P] [US1] Test that a bot with no description is refused with the field named, and that the **database** refuses it too, by attempting the insert directly — `services/api/src/db/repository.itest.ts`. Validation and the constraint are two guarantees and only one of them survives a new caller (FR-002)
- [ ] T024 [US1] Test that a kind change reports `kind_conflict` in **both** directions, in a **200** whose other entries still succeeded — `services/api/src/users/users.itest.ts`. A batch where entry 7 conflicts and entries 0–6 and 8–99 are written is the assertion; a 400 would prove the opposite (FR-002a)
- [ ] T023a [US1] **Pin the upsert's `status` set with an exact-set assertion** (FR-002c) — `services/api/src/users/users.itest.ts`. `created`, `updated`, `revived`, `kind_conflict`, and nothing else. `codes.ts` pins error codes and close codes the same way, and close code 4003 is the precedent for why: an exact set makes a fifth value a decision rather than an accident
- [ ] T024a [US1] Test that **omitting `kind` while updating an existing bot's description succeeds** — the case FR-002b exists for, and the one a schema default silently breaks — `services/api/src/users/users.itest.ts`
- [ ] T025 [US1] **Test that `{"description": null}` is refused at the boundary** (SC-014) — `services/api/src/users/users.itest.ts`. Both kinds: a bot, where the null would violate the CHECK, and a person, where it would be meaningless. **The assertion is the status, not the database** — a test that checks the row is unchanged passes when the request 500s and rolls back, which is the failure this task exists to distinguish from success **T021b of analysis pass 10 was this task written a second time** — added without checking whether it existed, and merged back here in pass 11 under the earlier id, because eleven passes of records cite by number and principle VI does not reuse identifiers.
- [ ] T026 [US1] **Confirm the derived target list did not move** — `services/api/src/isolation/targets.itest.ts`. No route was added, so it stays at 38; it failed on the build that added each of six routes last feature, five separate times (FR-007)
- [ ] T027 Commit Phase 3

**Checkpoint**: a tenant can name its software, and the database holds the requirement.

---

## Phase 4: User Story 2 — a credential cannot post as a person (P1)

**Goal**: every send names a sender, an application credential may name only a bot, and the
refusals reveal nothing.

**Independent test**: post with an API key naming a bot (201), naming a person (403), naming
nothing (400), naming a foreign bot (400, byte-identical to a nonexistent one).

- [ ] T027a [US2] **Declare `@Accepts("application", "user")` on `MessagesController`** — `services/api/src/messages/messages.controller.ts`. It declares none today and relies on `credential.guard.ts`'s `EITHER` fallback, which is the fallback chapter 3.15's own comment names as what let a user token through unnoticed. Behaviour is unchanged — `EITHER` is exactly those two — but this feature makes the route's behaviour branch on the class, and **every comparable route declares**: `channels.controller.ts`, `users.controller.ts`, `dev-token.controller.ts` and the read-position route's method-level pair (FR-007)
- [ ] T028 [US2] Add `user` to `sendMessageBodySchema` in `services/api/src/messages/messages.schema.ts` (FR-008)
- [ ] T028a [US2] **Return `user` from the send** (FR-009a) — `services/api/src/messages/messages.controller.ts`. The response names five fields and no sender; a caller now required to name one gets no confirmation of which was recorded. The internal send's response already carries it
- [ ] T029 [US2] Resolve the sender per credential class in `services/api/src/messages/messages.controller.ts`: the body's `user` for an application credential, the token's subject for a user token, and **refuse a body `user` on a user token** with `field: "user"` (FR-010)
- [ ] T029a [US2] Add `sender_not_permitted` to `packages/protocol/src/codes.ts` (FR-007a), with the comment naming its two siblings — `wrong_credential_type` is the wrong class, `wrong_credential_service` the wrong service, this is the wrong kind of user
- [ ] T029b [US2] **Update `codes.test.ts`'s exact-set assertion, and record that it failed on the build that added the code** — `packages/protocol/src/codes.test.ts`. An exact-set assertion is the only kind that makes a new code a decision rather than an accident; chapter 3.16 recorded the same beat for close code 4003 (FR-007a)
- [ ] T029c [P] [US2] Add the code to `docs/08-error-reference.md` so `docsUrl` resolves against a real anchor, then `pnpm sync:docs` and `pnpm check:errors` — a code whose page does not exist is the debt chapter 3.14 closed (FR-007a)
- [ ] T030 [US2] Enforce "an application credential may send only as a bot" in `services/api/src/messages/messages.service.ts` — 403 `sender_not_permitted`. **The service and not the repository**, because the repository cannot see the credential class and should not learn it (R5) (SC-004)
- [ ] T031 [US2] Refuse an unresolvable sender with `400` and `field: "user"`, **identically for a foreign bot and for one that exists nowhere** — `services/api/src/messages/messages.service.ts` (SC-005)
- [ ] T032 [US2] **Put the refusals in the documented order** (`contracts/sending.md`): ban, visibility, archive, then sender-resolves, then may-this-credential-send-as-it. Sender resolution comes *before* the bot check for the reason archive comes after visibility — the second refusal names a fact about a user the caller may not be able to confirm exists (FR-019b)
- [ ] T032a [US2] **Assert the wire carries `sender_not_permitted` and not `forbidden`** — `services/api/src/messages/messages.itest.ts`. `ProtocolErrorFilter`'s ladder maps 403 to `forbidden`, and this is the only code in the feature that collides with a ladder entry. The filter prefers an explicitly named code; that preference is what this asserts, and the filter's own comment records that 403's fallback arrived late (FR-007a)
- [ ] T033 [US2] Test the four outcomes for an application credential — bot 201, person 403, absent 400, unresolvable 400 — in `services/api/src/messages/messages.itest.ts`, **and that the 201 echoes the sender it used** (FR-007)
- [ ] T034 [US2] Test that a user token still sends as its subject and that a body `user` is refused — `services/api/src/messages/messages.itest.ts` (FR-010)
- [ ] T035 [US2] **Add the foreign-sender pair to the oracle** — `services/api/src/isolation/gauntlet.itest.ts`. **Hand-written, and `attack.ts` needs no fifth shape**: the sender is a new *dimension* on a route already classified `write` and already attacked, not a new shape. The same-tenant block was added by hand for the same reason in the last feature A bot of another tenant and an identifier that exists nowhere must answer byte-identically under `withoutRequestId`. This is a **new foreign-identifier surface on an existing route**, which is what the constitution check flagged (SC-002)
- [ ] T036 [P] [US2] Test that the control works first: the same credential, the same channel, its own bot — 201. Chapter 3.12's fourteen green tests compared two refusals and meant nothing — writes `services/api/src/isolation/gauntlet.itest.ts` (SC-005)
- [ ] T037 [US2] **Remove the bot check and confirm T033's 403 goes red**, then restore — `services/api/src/messages/messages.service.ts` (SC-004)
- [ ] T038 [US2] **Remove the sender-resolution refusal and confirm the oracle pair goes red**, then restore. Record which of the two removals the oracle notices and which it does not: chapter 3.15 found a suite is blind to an inner check a live outer one masks (SC-003b)
- [ ] T039 Commit Phase 4

**Checkpoint**: no send reaches storage without a sender the caller was entitled to name.

---

## Phase 5: User Story 3 — a bot is a user, and is not an account (P2)

**Goal**: a bot inherits everything keyed on a user, and can obtain no credential.

**Independent test**: add a bot to a channel, see it in the members list with a role; request a
token for it and be refused.

- [ ] T040 [US3] Refuse the mint for a bot in `services/api/src/auth/dev-token.controller.ts` — **404, `not_found`**. There is no "identical to unknown" available: an unknown identifier answers 200 on this route because chapter 3.16 made it create a person, so any refusal distinguishes a bot. **That is not an oracle here** — this route and `GET /v1/users/:externalId` are both `@Accepts("application")`, so a caller who reaches the refusal can already read that user's `kind` from their profile (SC-006)
- [ ] T040a [US3] **Refuse a bot at the session route too** (FR-005b) — `services/api/src/internal/session.controller.ts`. It resolves the user and reads `banned_at` without reading `kind`, so a bot holding a live token from before its promotion could open a socket. Refusing at the mint alone leaves a window of `MAX_TOKEN_LIFETIME_SECONDS` — 24 hours
- [ ] T040b [P] [US3] Test that a promoted bot's pre-existing token cannot open a socket — `services/gateway/src/isolation.itest.ts`. The refusal is the session route's, so the socket sees a closed connection rather than a 404 (FR-005b)
- [ ] T041 [US3] Ensure implicit creation still creates a **person** for an unknown identifier, and never converts an existing bot — `services/api/src/auth/dev-token.controller.ts` (FR-005a)
- [ ] T042 [P] [US3] Test the mint's three cases — unknown creates a person and mints, a person mints, a bot is refused 404 — `services/api/src/auth/credentials.itest.ts`. **Do not assert byte-identity with the unknown case**: it succeeds, so there is nothing to be identical to, and an earlier draft of this task asked for a comparison that cannot exist (FR-005a)
- [ ] T043 [US3] Test that a bot can be a channel member with a role, appears in the member list, and that the listing, unread count and last-message field are unaffected by its presence — `services/api/src/users/users.itest.ts` (FR-004)
- [ ] T043a [US3] Test **a bot's own channel listing** — `GET /v1/users/:botExternalId/channels` — and its read position (FR-004). A bot is a user, so the route answers for one; its unread count is the whole history because nothing ever acknowledges for it, and that is worth asserting rather than leaving a reader to wonder — writes `services/api/src/users/users.itest.ts`
- [ ] T043b [US3] **Leave `description` out of `deleteUser`'s `set` clause, and comment why** — and note in the comment that `markUserDeleted` is the *other* deletion method, that it clears nothing, and that it has **no production caller** (chapter 3.16 added it so the listing's 404 branch was reachable before the deletion route existed) — `services/api/src/db/repository.ts` (FR-004a). Clearing it on a bot violates `users_bot_description_check`, so a bot could not be deleted at all. The constraint and the deletion are each correct; they meet here, and the comment is what stops the next reader from "tidying up" the omission
- [ ] T044 [US3] Test that a bot can be banned and that its sends are then refused, and that it can be deleted with its messages surviving and still attributed — `services/api/src/users/users.itest.ts` (FR-005c)
- [ ] T043c [US3] **State what a ban now applies to** (FR-007b, FR-007c): the **sender named**, not the caller — which is what makes banning a bot meaningful — and that FR-USR-06's connection half is **empty by construction** for a bot, because it has no credential. The last feature recorded a claim that was true the way a statement about an empty set is true; this one says so instead
- [ ] T044a [US3] Test that a deleted bot **keeps its description** and that its messages still name it, then that presenting the id again revives it with the description intact — `services/api/src/users/users.itest.ts`. This is the assertion that would have caught the collision, and it is worth having in the direction that proves the decision rather than the direction that proves the bug (SC-007)
- [ ] T045 [US3] **Remove the `kind` read from the send's bot check and confirm T033's 403 goes red**, then restore (the column table's removal test) (SC-004)
- [ ] T046 [US3] **Remove the `description` read from the profile response and confirm T022 goes red**, then restore (FR-004)
- [ ] T047 [US3] **Record the two things `usage_active_users` decides, and measure both** (FR-018, FR-018a) — in `baseline.txt`, before and after a bot's send. Active users are metered by **FR-ANL-05** and capped by **FR-RTL-05** — two clauses in two families, not the FR-TEN-08 this feature cited for fourteen passes, which governs application deletion — **and the cap refuses sends**: `sendMessage` inserts the usage row at `repository.ts:3874` and, around line 4042, compares `count(*)` against `caps.active_users.hard` and throws `QuotaExceededError`. **The money was the smaller half.** A bot occupying a slot means the tenant's next human to post this period is refused — so the measurement is two numbers, the row count and the ceiling's verdict, not one. The decision: **billed, exempt from the ceiling**
- [ ] T047a [US3] **Name the assertions T047's decision moves — and note that all of them are the wrong kind.** **Three** pin exact counts — `services/api/src/quotas/quotas.itest.ts:71,78,103` (`toBe(2)`, `toBe(0)`, `toBe(0)`). The other two are not counts at all: `users.itest.ts:723` is `toBeGreaterThan(0)` and `:728` is `toBe(before.activeUsers)`, **a deletion invariant** — it asserts the billed figure is unchanged after a user is removed, which is the invariant T047b's join breaks if it filters `deleted_at`. Every one of the five asserts what the counter **holds**; not one asserts what the ceiling **refuses**. Since the decision is *billed, exempt from the ceiling*, the counting assertions may not move at all — a bot is billed, so the counts it produces are the counts they already expect — and **the behaviour that changes has no test in this repository at all**. Record both lists separately, and let the second one being empty be the finding (FR-018)
- [ ] T047b [US3] **Exempt a bot from the active-user ceiling, in two places** (FR-018a, FR-018b) — `services/api/src/db/repository.ts`. The insert at ~3874 keeps running, because a bot is billed. The ceiling block at ~4042 changes twice: it MUST return before throwing when the sender is a bot, **and** the `count(*)` it compares against MUST exclude bots. **Doing only the first is the trap** — a bot whose own send is exempted but whose row still lands in the count displaces a person exactly as before, and the bot's send passing makes it look fixed. The count needs the join to `users` on `kind = 'person'` — **and MUST NOT filter `deleted_at`.** Three `users` joins in this file pair with `isNull(users.deletedAt)` (~3291, ~3306, ~3387) and it is the house idiom, so the wrong version is the one a careful implementer writes. `deleteUser` is a **soft** delete and does not touch `usage_active_users`, so adding the filter makes a deleted person's row stop counting and **deleting users becomes a way to free ceiling slots** — which it is not today. `users.itest.ts:728` asserts the *billed* figure survives a deletion; nothing asserts the *enforced* figure does, so the ratchet will not catch this. The usage read at ~648 does **not** change, because that one is the bill
- [ ] T047c [US3] **The test is a person sending after a bot, not a bot sending** (SC-011) — `services/api/src/quotas/quotas.itest.ts`. Set the ceiling to the number of people who have already sent this period, send as a bot, then send as a person who has not sent yet. A test that only asserts the bot's send succeeds passes with T047b half-applied, which is the failure mode T047b names. **This is the fifth entry in the family of tests that were green while proving nothing** (3.16's `chapter-notes.md`): the assertion that matters is the one after the bot, not the one about it
- [ ] T047d [US3] **State that the billed figure and the enforced figure now differ, and by how much** (FR-018a) — in `baseline.txt`. `repository.ts` ~648 keeps counting bots, because that read is the bill; the ceiling at ~4042 excludes them. So a tenant can see *"5 of 5 active users"* on their usage page while their people still send, and the gap is exactly the number of bots that posted this period. **That is a support call unless it is written down** — record it as a consequence the chapter chose, not a discrepancy someone will file as a bug. **And leave the note for FR-ANL-06**, the P3 clause that says *"Metered totals shall agree with counts derived from operational data to within 0.1%, verified by a daily reconciliation job"* — no code cites it and the job does not exist yet, so this feature cannot break it, but the job's whole purpose is comparing the two numbers this chapter deliberately made different. A reconciliation written later without knowing that will report drift equal to the bot population
- [ ] T048 [P] [US3] State in `baseline.txt` that a bot's `read_positions` row is written by nothing and read by nothing, so a reader does not go looking for a bot's unread count. It is not a new dead column — it is an existing table holding a row that will never exist. **Premise checked in analysis pass 7 and it holds**: the only insert into `read_positions` is `setReadPosition` at `repository.ts:3345`, and no send path touches the table — so this task states a fact rather than assuming one, which is the check five wrong premises in the last feature earned
- [ ] T049 Commit Phase 5

**Checkpoint**: a bot is a first-class user everywhere except at the door.

---

## Phase 6: The rows that came before

**Goal**: messages already stored with no sender behave the same way on every read path.

- [ ] T050 **Measure how many senderless rows exist** in the lane, per environment, and record it in `baseline.txt`. The question is not the lane's number but whether the behaviour is reachable at all — the column is nullable and any deployment has them
- [ ] T051 Decide FR-013 and record it: what a client sees for a legacy senderless message on history, on the listing's `last_message`, and on a resume. **The answer must be the same on all three**
- [ ] T052 [P] Test history's answer — `services/api/src/messages/history.itest.ts` (SC-008)
- [ ] T053 [P] Test the listing's answer — `services/api/src/db/repository.itest.ts`, extending T014a's raw-SQL row (FR-012)
- [ ] T054 [P] Test the resume's answer — `services/gateway/src/public-surface.itest.ts`, which is where `toFrame`'s drop is already pinned (FR-012)
- [ ] T054a **Test the WEBHOOK payload's answer** (FR-012a) — `services/api/src/outbox/event.test.ts` and `services/api/src/webhooks/deliveries.itest.ts`. `MessageCreatedData.user` is `string | null` and is what a customer's own endpoint receives (FR-WHK-02); FR-WHK-03 retries for up to two hours, so an event for a legacy senderless message can be delivered after this chapter ships. **This is the fourth read path and the only one that leaves the platform** — it was missing from the enumeration until the first analysis pass
- [ ] T054b Decide and record whether `MessageCreatedData.user` stays nullable, in `baseline.txt`. New events cannot carry a null; the type describes what a subscriber may still receive from the retry queue (FR-012a)
- [ ] T055 **Re-examine chapter 3.16's `last_message.user: null` test rather than deleting it** (R8). Its arm now covers legacy rows only, and a test whose subject changed needs its comment changed (FR-014)
- [ ] T056 **Assert that chapter 3.16's frame-shape assertion still passes** — `services/gateway/src/isolation.itest.ts`. A chapter that changes the sender model and leaves the frame contract alone is making a claim a reader will not believe without one (FR-012)
- [ ] T057 Commit Phase 6

**Checkpoint**: nothing that was readable stopped being readable.

---

## Phase 7: The callers

**Goal**: every send site in the workspace names a sender, and the sealed integration passes
without being corrected.

- [ ] T058 Fix the HTTP send sites in `services/api/src/isolation/gauntlet.itest.ts` (14) — these are attack shapes, so **each must keep attacking what it attacked**. A gauntlet test that starts passing because its send now fails validation has stopped testing isolation (FR-011)
- [ ] T059 [P] Fix `services/api/src/messages/messages.itest.ts` (8) (FR-011)
- [ ] T060 [P] Fix `services/api/src/limits/limits.itest.ts` (4) — the rate-limit suites count requests, so a send that now 400s still counts and the assertions may pass for the wrong reason. **Check what each assertion would do if every send were refused** (FR-011)
- [ ] T061 [P] Fix `services/api/src/users/users.itest.ts` (3), `services/api/src/auth/credentials.itest.ts` (3), `services/api/src/channels/channels.itest.ts` (3) (FR-011)
- [ ] T062 [P] Fix `services/gateway/src/public-surface.itest.ts` (2), `services/gateway/src/isolation-fixtures.ts` (2), `services/gateway/src/limits.itest.ts` (1), `services/api/src/internal/internal.itest.ts` (1) (FR-011)
- [ ] T063 [P] Fix `packages/e2e/src/tuan.itest.ts` (2) (FR-011)
- [ ] T063a **WRITE THE BOT FLOW DOWN BEFORE TOUCHING THE OUTSIDER.** Add it to (FR-015d)
  `relay-platform/README.md`'s walkthrough — a `curl` creating a bot with a description, and a
  send naming it — because chapter 3.12's `gaps.md` names the README as one of the three sources
  an outsider may read (with the published series and the reference documents). **Without this
  T065's question has a fixed answer**: the sealed suite cannot discover a required step from
  documentation nobody wrote, so it could only ever learn about bots by being corrected, which
  is the assistance chapter 3.14's verdict says the criterion forbids. **`relay-platform/README.md`
  is fenced by no chapter** — `grep 'title="README.md"'` finds nothing in `relay-tutorial/app/`
  or `relay-tutorial/fences/` — so this edit needs no fence work and `check:fences` will not see
  it. That cuts both ways: the file an outsider is told to read is a file no chapter teaches and
  no checker verifies, which is chapter 3.16's *"fences with no subject"* finding inverted
- [ ] T063b **NAME THE README THE QUICKSTART OF RECORD, and close principle VI's quickstart (FR-015d)
  clause** (FR-015d, FR-015e, SC-015). The constitution requires that *"The quickstart MUST run
  unmodified, verified by automated execution in CI against the published documentation"* — and no
  `*quickstart*` file exists in `relay-tutorial` or `docs/`, with nothing in
  `.github/workflows/ci.yml` naming one. **This is a constitution violation, not a gap**, and it
  predates this chapter by eight. The automated execution is already there: CI runs
  `pnpm test:outsider` in its own job. Declare `relay-platform/README.md` the published
  documentation that job verifies, in `baseline.txt` and in the chapter, and say that T065's run
  is the verification rather than a separate artifact — **a quickstart nobody executes is the debt
  the clause exists to prevent, and a second document written to satisfy it would recreate that
  debt**
- [ ] T064 **`packages/outsider/src/integrate.itest.ts` LAST, and it is the one that matters.** It is sealed from workspace code and stands for an external developer. Its script must **create a bot and send as it**, demonstrating the flow a customer follows (SC-001)
- [ ] T065 **Run `pnpm test:outsider` and record whether it passed first time** — after T063a, not before, or the answer is fixed. Chapter 3.14's verdict says a suite that passes *because a failing test corrected it* is the assistance the Phase 2 exit criterion forbids. **Either answer is recorded as a finding**, and with T063b the run is also **principle VI's quickstart verification** (SC-015): the suite is sealed from workspace code, so "runs unmodified against the published documentation" is a statement about whether its script can be derived from the README. A failure means the README is insufficient, which is a finding about the documentation and not about the suite
- [ ] T066 Update the published quickstart if it sends — `relay-tutorial/`, and NFR-USE-03 has CI execute it against the published documentation (FR-015d)
- [ ] T067 Commit Phase 7

**Checkpoint**: an outsider following the documentation can send a message.

---

## Phase 8: Verification

**Goal**: three separate gates pass, and each is named — the coverage ratchets re-earned for every
pin this feature moves, the derived target list still classifying every route the router mounts, and
the twenty-run integration battery inside its budget. **Twenty green rejects a per-run failure rate
above 13.91% at 95% confidence and nothing finer**, so the battery bounds flakiness rather than
proving its absence.

- [ ] T068 Run every gate and record the **exit code** of each, not a grep over its output: `pnpm lint`, `pnpm typecheck`, `pnpm build`, `pnpm turbo run test`, `pnpm test:integration`, `pnpm coverage`, `pnpm test:outsider`
- [ ] T069 [P] Add coverage ratchets for anything this feature adds, and **re-earn the pins it moves**. `repository.ts` sits at 91 branches after the last feature raised it from 90 (SC-003)
- [ ] T070 Enumerate the branch arms this feature adds and show each covered, per arm rather than by a file percentage — `baseline.txt`
- [ ] T071 **Check that every new repository function is exercised in-process**, not only through the gateway's api child whose coverage is not attributable. `functions: 100` on `repository.ts` is the measurement that answers it (SC-003)
- [ ] T072 Write `specs/035-chapter-3-17/traceability.md`, both directions, and **check FR-CHN-05's row**: chapters 3.15/3.16 recorded it delivered when the clause names three verbs and two were built. A map that claims delivery is the defect this project has now corrected three times. **And cite FR-USR-05's existing SRS note**: it already records that *"the resume path drops a senderless row, so every message a deleted user ever sent would vanish from every reconnecting client with a sequence gap as the only trace"* — the third of FR-012's four paths, anticipated by the governing document years before this chapter. Analysis pass 9 opened that note as a suspected contradiction of SC-007 and it is the reverse: the note is the SRS **rejecting** `ON DELETE SET NULL` for exactly this reason. Presenting the resume path as a new discovery understates the document the chapter is amending (SC-009)
- [ ] T073 [P] Update `docs/04-srs.md`'s verification notes for FR-USR-07 and FR-MSG-15 (FR-016)
- [ ] T074 [P] Add the 3.17 row to `docs/07-tutorial-plan.md` with the shipped numbers (SC-010)
- [ ] T075 Run `pnpm sync:docs`, then `check:docs`, `check:errors`, `check:figures`, `check:fences` — in that order and after T073
- [ ] T076 **Decide the lane budget before the battery runs.** The last feature measured 550 tests at 192–197 s against a 240 s bound, and found the lane costs per **suite** rather than per test. This feature adds tests to existing suites and one new suite at most (SC-010)
- [ ] T077 The twenty-run battery, on a machine running nothing else (SC-010)
- [ ] T078 Record what twenty green buys and does not: it rejects a per-run failure rate above 13.91% at 95% confidence, a 5% flake survives it 35.85% of the time, and rejecting one needs 59 runs — writes `baseline.txt`
- [ ] T079 Commit Phase 8

---

## Phase 9: The chapter

**Goal**: the prose exists, the figures render, and every fenced path replays onto the platform
repository. **What a chapter teaches is not what it must fence** — the two counts stay in separate
columns from the first task to the last.

- [ ] T080 **Count the files this chapter teaches and the files it must fence, as two columns**, before writing a word — `baseline.txt`. The last feature conflated them for eight revisions and the ceiling looked comfortable when it was binding
- [ ] T081 Write `relay-tutorial/app/(en)/part-3/chapter-17/<slug>/page.mdx`. The subject is one sentence: a message sent by a customer's server had no sender, and now it has one it chose (SC-010)
- [ ] T082 [P] Write `figures.ts`: the two blast radii, the refusal order with what each reveals, and the identity that was an absence (SC-010)
- [ ] T083 Diff fences at **three lines of context**, verified unique by simulating the checker rather than widened to eight on principle — writes the chapter page
- [ ] T084 **A path the appendix amends needs its target computed as HEAD-minus-appendix.** A diff straight to HEAD does the appendix's work and leaves its hunk matching 0 times (SC-010)
- [ ] T085 **Re-derive the file count from `git diff --name-only` against `check:fences`** and record whether it moved from T080's. It moved in six of the last feature's eight revisions (SC-010)
- [ ] T086 State the SRS amendment on the page (FR-015): the chapter cites a clause that did not exist when the chapter was specified, and says so
- [ ] T086a **State what an existing caller must change** (FR-011), on the page and not only in a spec: the send body gains a required field for one credential class, and the chapter must not describe that as backwards compatible
- [ ] T086b **State that chapter 3.3's decision is REVERSED, not reinterpreted** (FR-017), and why it was right when it was made — nothing read the sender then, and three chapters since have made the sender decide what is rendered, delivered and seen — writes the chapter page
- [ ] T086d **CORRECT CHAPTER 3.10's TRAP, IN BOTH LOCALES** (FR-020, SC-016) — `relay-tutorial/app/(en)/part-3/chapter-10/quotas-and-what-they-cost/page.mdx` ~272 and its `(vi)` twin. The title *"An unattributed send counts toward the messages and toward nobody"* is false after FR-018, and the body argues against this chapter: *"The alternative, inventing a synthetic user for it, would inflate the dimension the customer is actually being measured on."* **Keep the argument and draw the line it was missing** — 3.10 rejected a *synthetic* user the platform invents; a bot is a *declared* one the customer creates, names and describes. Deleting the paragraph loses the reasoning; correcting it teaches the distinction. **Both locales, or the series contradicts itself in one language**
- [ ] T086e **Sweep the published chapters for every claim this chapter reverses, and classify each hit** (FR-020) — `grep -rniE "unattributed|senderless|no sender|carries no user" relay-tutorial/app/`. Pass 15 classified the known hits and **most need no change**: `3.13:1293` (*"toFrame drops senderless rows on purpose"*), `2.07:634`, `2.07:744` and `3.16`'s `figures.ts:49` all stay true, because legacy rows still exist and FR-012 is why. **Two do**: 3.10's Trap (T086d) and `3.13:734`, which gives *"only used to write an unattributed row"* as the reason `sendMessage` stays on the 2.8 seam — the seam may still be right and **its recorded reason is gone**. Classify, do not sweep: this project has now twice shipped a checker that stopped where its pattern stopped
- [ ] T086f **Record that no checker reads prose** (FR-020a, FR-020b) — in `baseline.txt` and on the page. `check:fences` replays fenced code, `check:figures` asserts a figure has a source, `check:docs` compares mirrored documents to their canonical copies, `check:srs` reads identifiers. **A published sentence asserting something false passes all four**, which is why 3.10's Trap survived fifteen analysis passes. Also record that correcting a page's prose does not touch the chain — 3.10's page carries 36 titled fences and none changes — so this edit is invisible to `check:fences` by design, not by luck
- [ ] T086c **Revise the comments in the code that still assert the pre-3.17 rule** (FR-017) — three known sites, and grep for more. `services/api/src/db/repository.ts` ~3869 tells a reader *"A key-authenticated REST send carries no `userId` — unattributed by design since chapter 3.3 — and counts toward the message quota and toward no user"*, which is the reversed decision stated as current design, inside the billing code. `services/api/src/messages/messages.controller.ts:30` and `services/api/src/messages/messages.service.ts:39` carry the same claim. **The prose inside the code is an artifact too**, and this project's own rule is to fix the file that describes a thing and the one that instructs it. `grep -rn 'unattributed\|carries no user\|FR-MSG-13' services/api/src --include=*.ts` finds the rest; **classify each hit**. **Two of them cite FR-MSG-13 for the senderless send** — line 31 on `actingUser()` returning `undefined` for a key, and line 43 giving it as the reason `MessagesController` declares no `@Accepts`, which is the declaration T027a adds. Both comments must change what they assert **and** what the amended clause now means — `channels.service.ts:78` and `channels.controller.ts:190` say a *credential* carries no user, which stays true, because the key still carries none and the body names the bot
- [ ] T087 Add the chapter to `relay-tutorial/lib/tutorial.ts`
- [ ] T088 Count the prose words — inside 2,000–4,000, and **write against the measured rate rather than the nominal one**. The nominal 160 words per file said chapter 3.16 could not be written; it landed at 3,800 (SC-010)
- [ ] T089 Commit Phase 9

---

## Phase 10: Translation and publication

**Goal**: both locales carry the chapter, the build is green, and the page count moved by exactly
what was added. Identifiers, table names and column names stay English in the translation.

- [ ] T090 Translate to `relay-tutorial/app/(vi)/vi/part-3/chapter-17/<slug>/page.mdx`, **assembled mechanically** — split at every fence boundary, translate the prose, copy the fences untouched, then re-split both and compare the fence lists
- [ ] T091 [P] Translate the figure labels; identifiers, table and column names stay English — writes the `(vi)` locale page
- [ ] T092 `pnpm check:fences`, and ask it about **files this chapter owns** rather than pages naming it — and separately list this feature's files that no chapter claims, which the checker cannot tell you (SC-010)
- [ ] T093 [P] `pnpm lint`, `tsc`, `pnpm build`, `check:figures`, and the static page count — writes `baseline.txt` (SC-010)
- [ ] T094 Record the chapter's numbers in `baseline.txt`, both locales
- [ ] T095 Commit Phase 10

---

## Phase 11: Close-out

**Goal**: the record is written while the work is fresh — what shipped against what was planned,
the gaps with owners, traceability in both directions, and every measurement. **Nothing is ticked
before it is done.**

- [ ] T096 Write `specs/035-chapter-3-17/chapter-notes.md`: the plan against what shipped, including the phases that went badly (SC-009)
- [ ] T096a **Amend chapter 3.12's `gaps.md` G1**, which records "a message sent over REST reaches no socket, ever" as **two** independent mechanisms: nothing publishes, and the public send passes no user so every row is `user_id NULL`. **This chapter removes the second.** The recorded gap now has one mechanism, and the record should say which chapter took which — 3.17 the sender, 3.18 the publish. A gap that is half-closed and still reads as whole is the shape this project has corrected three times in traceability rows (SC-009)
- [ ] T097 [P] Write `specs/035-chapter-3-17/gaps.md`, and **carry forward the eight from the last feature that are still open**, with 3.18 and 3.19 as owners where they now have one (SC-009)
- [ ] T098 [P] Record whether the two file counts stayed apart, and what each was at every revision — writes `chapter-notes.md`
- [ ] T099 Update `CLAUDE.md` between the `<!-- SPECKIT -->` markers (SC-009)
- [ ] T100 [P] Tick the last task only when it is done, not when it is about to be — chapter 3.12 marked its close-out complete before pushing and had to reopen it — writes `tasks.md`
- [ ] T101 Tag `part3-ch17` in all three repositories, confirm each submodule pin matches its HEAD, and push. **Hold the tag if `check:fences` exits 1** (SC-009)

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

**T051 is a decision, not an implementation** — what a legacy row renders as. It is flagged so it
is answered on purpose. **T047 was one too, until pass 6 read the code it was measuring**: the
counter it asked a billing question about also refuses sends, so the decision grew an
implementation (T047b) and a test (T047c). A question about money turned out to be a question
about whether a customer's humans can post.
