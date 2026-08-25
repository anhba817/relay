# Feature Specification: Chapter 3.17 — the sender a message never had

**Feature Branch**: `035-chapter-3-17`

**Created**: 2026-08-25

**Status**: Draft

**Input**: User description: "chapter 3.17"

---

## What this chapter is about

A customer's server posts a message. It is stored with **no sender**.

That is not a defect anybody introduced. Chapter 3.3 decided it deliberately — its comment
still reads *"absent on the public REST route, where a key-authenticated send is
unattributed"* — and the decision was right while nothing read the sender. Every consumer of a
message either did not need one, or had one supplied by a user token.

**The decision is wrong now, and three chapters made it wrong.** Chapter 3.15 gave every read
path a caller and made the sender decide what a user may see. Chapter 3.16 built a listing
whose `last_message` field has to render *something*, and a deletion that must keep a message
"authored by a deleted user" — a sentence with no meaning for a message authored by nobody.
And the next chapter has to deliver these messages to a socket, where the frame contract
requires a sender that is a non-empty string.

So the platform has been treating "the customer's software posted this" as an **absence**,
when it is an **identity** the customer was never given a way to name.

This chapter gives them the way: a **bot user**, created by the tenant, carrying a description
of what it is and what it posts, named on every send that a person did not make.

### What this chapter is NOT

**The fan-out is chapter 3.18.** A REST-sent message still reaches no socket when this chapter
ends, and the chapter says so. The two were specified as one chapter and split before planning
rather than after: the sender requirement is a complete, testable subject on its own, and the
delivery chapter is cleaner when it can open with "every message now has a sender" instead of
building a user model first.

Presence and typing — FR-RTM-05's other half, with FR-RTM-06 and FR-RTM-07 — move to 3.19.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — a customer names the software that posts (Priority: P1)

A customer runs a support tool that posts "your ticket was updated" into a channel. They
create a bot user for it, describe what it is, and every message it sends carries that
identity.

**Why this priority**: it is the identity that has been missing, and everything else in the
chapter depends on it existing.

**Independent test**: create a bot user with a description, read it back, send a message
naming it, and find the sender on the message through the public read path.

**Acceptance scenarios**

1. **Given** a tenant, **When** they create a bot user with an identifier and a description,
   **Then** the bot exists, the description is readable, and the record says it is software
   rather than a person.
2. **Given** a bot user, **When** a message is posted with an application credential naming
   it, **Then** the message is stored with that bot as its sender and the read path returns
   it like any other sender.
3. **Given** a bot user, **When** the tenant lists or reads users, **Then** the bot appears
   and is distinguishable from a person without parsing its identifier.
4. **Given** a bot user, **When** the tenant updates its description, **Then** the new
   description is what a reader sees.

### User Story 2 — a credential cannot post as a person (Priority: P1)

An application credential may speak as the customer's software and as nothing else.

**Why this priority**: requiring a sender creates this risk. A key that may name any user is a
credential that can post as any human in the tenant, which is an impersonation surface the
platform did not have while sends were anonymous.

**Independent test**: with an application credential, post naming a human user of the same
tenant and confirm the refusal; post naming a bot and confirm it succeeds.

**Acceptance scenarios**

1. **Given** an application credential and a human user of the same tenant, **When** a message
   is posted naming that human, **Then** it is refused.
2. **Given** an application credential, **When** a message is posted naming no sender,
   **Then** it is refused and the response names the field.
3. **Given** an application credential and a bot of **another** tenant, **When** a message is
   posted naming it, **Then** it is refused the way every other foreign identifier is —
   indistinguishably from a bot that does not exist.
4. **Given** a **user token**, **When** a message is posted, **Then** the sender is the
   token's subject and naming a different sender is refused or ignored — a user speaks as
   themselves.

### User Story 3 — a bot is a user, and is not an account (Priority: P2)

A bot can be a channel member, hold a role, be listed, be banned and be deleted. It cannot
log in.

**Why this priority**: it is what makes the model cheap. Everything downstream is keyed on a
user, so a bot that is a user inherits membership, isolation, the listing and the ban for
free — and a bot that could authenticate would be a credential nobody issued.

**Independent test**: add a bot to a channel, list the channel's members, confirm the bot is
there with a role; then attempt to mint a token for it and confirm the refusal.

**Acceptance scenarios**

1. **Given** a bot user, **When** it is added to a channel, **Then** it is a member with a
   role like any other member.
2. **Given** a bot user, **When** a token is requested for its identifier, **Then** it is
   refused.
3. **Given** a bot user that is a channel member, **When** a user lists their channels,
   **Then** nothing about the bot's presence in that channel breaks the listing, the unread
   count or the last-message field.
4. **Given** a bot user, **When** it is banned, **Then** its sends are refused the way a
   banned person's are.
5. **Given** a bot user, **When** it is deleted, **Then** its messages survive and remain
   attributed to it, exactly as FR-USR-05 requires for a person.

### Edge cases

- A tenant sends naming a bot identifier that does not exist. Refused, and indistinguishably
  from a bot belonging to another tenant.
- A bot's identifier collides with a person's. `(environment_id, external_id)` is unique, so
  one namespace holds both; the chapter states what happens when a customer tries to create a
  bot with a person's identifier.
- Implicit creation (FR-USR-02) meets a bot's identifier at authentication. A bot cannot
  authenticate, so the chapter states which of the two rules wins.
- A message stored before this chapter, with no sender at all. The column is nullable and the
  rows exist.
- A bot is the `owner` of a channel and is deleted — chapter 3.16 recorded that a channel can
  be left ownerless with no route to appoint another.

---

## Requirements *(mandatory)*

### The bot user

- **FR-001**: A tenant MUST be able to create a bot user with a customer-supplied identifier,
  unique within the tenant in the same namespace as its people (FR-USR-01).
- **FR-002**: A bot user MUST carry a **description** — what the software is and what it
  posts — of at most **500 characters, enforced in the request schema rather than by a database
  constraint** — readable by anyone who can read the user. The layer is named because it decides
  the failure's shape (FR-002a). The bound is stated here rather than only in the design, the
  way FR-024 states 4 KB for user metadata:
  `display_name`'s 255 is too short for a sentence explaining a bot, and `metadata`'s 4 KB is
  a document rather than a label.
- **FR-002a**: The upsert MUST report a rule the request schema can check as a **400 naming the
  entry's index**, and a rule that needs the stored row as a **per-entry status in the 200
  result array**. A missing description is the first; a kind change is the second. Collapsing
  the second into a 400 would fail a batch of 100 because of one entry, which is the outcome
  chapter 3.16's per-entry array exists to prevent.
- **FR-002d**: A `person` MUST be promotable to `bot` when the row **has never sent a message**.
  `bot → person` stays refused unconditionally.

  **Without this the natural ordering traps a customer.** `POST …/members` creates any unknown
  identifier as a person — `createUser` cannot set `kind` — so *"add support-bot to #support"*
  followed by *"register the bot"* makes the bot permanently impossible. That is the order a
  customer follows.

  **The predicate is "no messages", because that is what immutability protects.** Re-labelling a
  human's messages as software is the harm; a row that has never sent one has no authorship to
  re-label. Memberships are not part of the test — the member-add is what creates the trap, so
  requiring none would close the escape it exists to open.

  **The consequence is bounded and MUST be stated**: a live token for that identifier keeps
  working until it expires, at most `MAX_TOKEN_LIFETIME_SECONDS` — 24 hours. The mint refuses
  new ones immediately.
- **FR-002e**: The promotion's cost MUST be measured, not assumed. `messages.user_id` carries no
  index, so "has this user ever sent a message" is a filtered scan — R4 measured a full message
  scan at 159 ms against 1,000,000 rows. Acceptable for a rare administrative call; the chapter
  states the number rather than adding an index nothing else needs.
- **FR-002b**: An upsert entry that omits `kind` for an existing row MUST be read as **no
  change requested**, not as a request for `"person"`. The default applies on creation only;
  otherwise a bot cannot be edited through the route FR-004 says can edit it.
- **FR-002c**: The upsert's per-entry `status` values MUST be pinned by an exact-set assertion,
  the way `codes.ts`'s error codes and close codes are. `kind_conflict` is a fourth value in a
  published response field, and a fifth should be a decision rather than an accident.
- **FR-003**: A bot user MUST be distinguishable from a person by a **stored property**, not
  by a naming convention. A client rendering a conversation, a moderator reading an audit
  trail, and a permission check must each be able to tell them apart without parsing an
  identifier.
- **FR-004**: A bot user MUST support the operations a person supports: profile read and
  update, channel membership, roles, listing, ban, and deletion — with FR-USR-05's guarantee
  that its messages survive its deletion, still attributed to it.
- **FR-004a**: **A bot's description is not profile data**, and `deleteUser` MUST NOT clear it.
  (The repository holds two deletion methods: `deleteUser`, which clears the profile and the
  memberships, and `markUserDeleted`, which only stamps the marker and has **no production
  caller** — chapter 3.16 added it so the listing's 404 branch was reachable before the deletion
  route existed. This rule is `deleteUser`'s.)
  FR-027 clears profile data on deletion — `display_name`, `avatar_url`, `metadata` — and
  clearing `description` would violate `users_bot_description_check`, so **a bot could not be
  deleted at all**. The constraint and the deletion are each correct and meet here.

  Keeping it is also the better answer on its own terms: a deleted bot's messages stay
  attributed to it (FR-USR-05), and a reader asking "what was this thing that posted in March"
  needs the description to still be there. The alternative — clearing `kind` back to `'person'`
  first — makes the deletion two writes and turns a bot into a person nobody created.
- **FR-004b**: **`description` MUST NOT be nullable on any route**, and the "null clears" idiom
  that governs every neighbouring field MUST NOT be extended to it. `userProfileBodySchema`
  documents that idiom in its own comment — *"`null` CLEARS, and it is distinct from absent.
  `{"display_name": null}` removes the name; `{}` leaves it"* — and `description` is the one
  column where it cannot hold: `users_bot_description_check` forbids a null description on a bot,
  so `PATCH /v1/users/:externalId {"description": null}` would raise a constraint violation and
  reach the customer as a 500. Nullability buys nothing for either kind — a bot must never clear
  it, and a person may never be given one (FR-003) — so the field is settable and not clearable.
  **The schema comment MUST say this**, because the comment is what would otherwise put
  `.nullable()` back.
- **FR-005**: A bot user MUST NOT authenticate. No token is minted for its identifier and no
  socket opens as it. It is an identity messages are sent *as*, not an account that logs in.
- **FR-005b**: **The session route MUST refuse a bot too.** FR-005 says no socket opens as one,
  and `POST /internal/session` resolves the user and reads `banned_at` without reading `kind` —
  so a bot holding a live token from before its promotion could open a socket. Refusing at the
  mint alone leaves a 24-hour window.
- **FR-005a**: Implicit creation on first authentication (FR-USR-02) MUST NOT create a bot,
  and MUST NOT turn an existing bot into an authenticating user.
- **FR-005c**: **A bot MAY be banned, and the ban MUST refuse its sends.** `users.banned_at`
  exists on every user row, and removing `sendMessage`'s guard around the ban check makes that
  check run for a bot's sender id for the first time. The chapter MUST state this as a decision:
  a ban is how an operator stops a runaway integration without deleting the identity its
  messages are attributed to. A bot's send after a ban is refused the same way a person's is —
  indistinguishably, before the channel is read (FR-021a, chapter 3.15) — and the operator's
  route to that state is the existing ban, not a new one.

### The sender requirement

- **FR-006**: Every message the platform accepts MUST have a sender. No write path may leave
  a message with none.
- **FR-007**: A key-authenticated send MUST name its sender, and the named user MUST be a
  **bot** of that tenant. Naming a person MUST be refused: an API key that can post as any
  human is an impersonation surface.
- **FR-007b**: A ban applies to the **sender named**, not to the caller. On a key-authenticated
  send that is the bot, so `user_banned` becomes the answer for a banned bot and banning one is
  meaningful. The rule is unchanged for a user token, where the sender and the caller are the
  same person — but the sentence "the caller is banned" stops being true on that route and the
  chapter must not repeat it.
- **FR-007c**: FR-USR-06's ban prevents "connection and message send". For a bot the connection
  half is **empty by construction** — it has no credential — and the chapter MUST say so rather
  than leave a reader to assume both halves were tested. The last feature recorded a claim that
  was true the way a statement about an empty set is true, and this is the same shape.
- **FR-007a**: That refusal MUST carry **its own error code**, not the generic `forbidden`.
  The registry states the rule twice in its own comments — *"NOT `forbidden`. Chapter 3.2 made
  this argument when it added `wrong_credential_type` rather than answering a wrong-credential
  mistake with a generic 403"* — and the precedent is exact: `wrong_credential_type` is a
  credential of the wrong class, `wrong_credential_service` a credential of the wrong service,
  and this is a credential naming the wrong **kind of user**. A client that cannot tell it from
  every other 403 retries the wrong thing.
- **FR-008**: A key-authenticated send naming no sender MUST be refused with the field named,
  the way every other validation failure names its field (chapter 3.14).
- **FR-009**: A send naming a sender that does not exist in the caller's tenant MUST be
  refused indistinguishably from one naming a sender that exists in another tenant
  (FR-TEN-05), verified by the isolation suite's existing oracle.
- **FR-009a**: The send response MUST carry the sender it used. The route returns
  `{id, channel_id, seq, text, created_at}` today and names no user, so a caller who is now
  *required* to name a sender gets no confirmation of which one was recorded. The internal
  send's response already carries `user` and history returns it; the public send is the only
  surface that does not. Chapter 3.13's create-channel response set the precedent by echoing
  what it created.
- **FR-010**: A user-token send MUST continue to be attributed to the token's subject. The
  route MUST NOT let a user token name a different sender.
- **FR-011**: **This is a breaking change to a route shipped in chapter 2.2.** The chapter
  MUST state what an existing caller has to change, and MUST NOT describe the change as
  backwards compatible.

### What already exists and must keep working

- **FR-012**: FR-006's rule — no write path may create a senderless message — is stated once,
  there. What this clause adds is the other direction: messages already stored with no sender
  MUST keep working on **all four** paths
  that can reach them:

      history                 GET /v1/channels/:channelId/messages
      the listing             last_message on GET /v1/users/:externalId/channels
      the resume              toFrame, which drops a senderless row today
      THE WEBHOOK PAYLOAD     message.created, delivered to a customer's own endpoint

  The column stays nullable because the rows exist; nothing new may create one.
- **FR-012a**: **The webhook payload is the one that leaves the platform**, and it was missing
  from this list until the first analysis pass. `MessageCreatedData.user` is `string | null`
  and is what a customer's HTTPS endpoint receives (FR-WHK-02); FR-WHK-03 retries a failed
  delivery for up to two hours, so an event for a legacy senderless message can be delivered
  and redelivered after this chapter ships. The chapter MUST state whether that field stays
  nullable and what a subscriber should expect.
- **FR-013**: The chapter MUST state whether those legacy rows become renderable and what a
  client sees for them, and the answer MUST be the same on **all four** paths.
- **FR-014**: Chapter 3.16's `last_message.user: null` arm and its test MUST be re-examined
  rather than deleted: the arm now covers legacy rows only, and a test that no new write can
  reach is a test whose subject has changed.
- **FR-019**: **The sender attributes; it does not authorise.** This is the chapter's governing
  distinction and it was missing until the seventh analysis pass. A person's token does both
  things at once — it says who may act and who is speaking — and adding a required sender to a
  key-authenticated send reads naturally as *"the key now acts as that user"*. It must not mean
  that. A key naming a bot MUST have exactly the authority the key has today, and the bot's name
  MUST be what appears on the message and nothing more.
- **FR-019a**: The concrete consequence: **an application key's send to a private channel MUST
  keep working, and the bot it names MUST NOT need membership.** Chapter 3.15 delivered this on
  purpose — FR-005 there, and `channels.service.ts` records it as *"An application credential
  acts for the customer, carries no user, and sees private channels"*. Today
  `repository.ts` gates the membership check on `channel.type === "private" && userId !==
  undefined`, so a key send skips it because there is no user. Requiring `userId` makes that
  gate always true, the check fires, and a bot that is not a member is refused with
  `ChannelNotFoundError`. The gate MUST become conditional on **the sender being a person**
  rather than on a sender existing.
- **FR-019b**: A person is unaffected. A user token sending to a private channel they are not a
  member of MUST still be refused, indistinguishably, exactly as chapter 3.15 built it. The two
  behaviours diverge on `kind`, and a test that only checks the bot's send passes if the
  person's refusal has been removed along with the gate.

### Billing

- **FR-018**: A bot's send MUST record a row in `usage_active_users` — a bot **is** billed as an
  active user. The governing clause is **FR-ANL-05** (*"shall meter, per tenant per day: messages
  sent, unique active users, connection-minutes, and stored message count"*), and the count MUST
  be measured before and after a bot's send rather than reasoned about. **FR-TEN-08 was cited here
  for fourteen analysis passes and says nothing about billing** — it governs application deletion
  and 30-day data retention. A wrong citation is worse than a missing one: a missing one fails a
  coverage check, and this one looked authoritative enough that nobody read it.
- **FR-018a**: The same counter is a **hard cap that refuses sends** — **FR-RTL-05**, *"shall
  enforce configurable monthly quotas on messages sent, unique active users, and
  connection-minutes"* — and a bot MUST NOT be refused by it, nor consume a person's allowance.
  **The SRS separated metering from enforcement before this chapter existed**: FR-ANL-05 meters
  and FR-RTL-05 enforces, in two different families. Pass 6 derived that same split by reading
  `repository.ts`, and the governing document had it all along. `usage_active_users` is read twice on the send
  path: once to record usage and once to enforce a ceiling, and only the first applies to a bot.
  Billing and refusing are separate decisions about one counter, and this chapter answers them
  differently: **billed, exempt from the ceiling.** The ceiling bounds a customer's human
  population; a bot is the customer's own infrastructure, and a platform that refuses a paying
  customer's users because their support bot posted first is a support ticket before it is a line
  item.
- **FR-018b**: The exemption has two halves and the second is the one that decides whether it
  works. Not refusing a bot's own send is the visible half; the count the ceiling compares
  against MUST also exclude bots, or a bot's row still occupies a slot and **a person** is
  refused on their first send of the period. A bot exempted from its own refusal while still
  counted leaves the harm exactly where it was.

### The governing documents

- **FR-015**: The SRS has **no bot, system, or service-account concept** — FR-USR-01 through
  FR-USR-06 describe end users supplied by the customer, and the SAD mentions none either.
  This chapter therefore requires an **explicit amendment** to `docs/04-srs.md`, which is what
  the constitution's Governance section demands: where the constitution conflicts with the SRS
  or SAD, *"the conflict MUST be resolved explicitly by amendment rather than"* ignored.
- **FR-018c**: **FR-RTL-05 MUST be amended in place**, the same treatment FR-MSG-13 gets and for
  the same reason. It enforces a quota on *"unique active users"* with no exception, and this
  chapter exempts bots from that ceiling — so leaving the clause as written and describing the
  exemption only in a chapter would be the implicit resolution the Governance section forbids. The
  amendment narrows the enforced dimension to **unique active persons**; the metered dimension in
  FR-ANL-05 stays *unique active users* and keeps counting bots, which is the whole point of the
  split.
- **FR-018d**: **FR-RTL-08 MUST be cited and its exception stated.** It reads *"Quota exhaustion
  shall degrade predictably: sends rejected with a specific error code; existing connections and
  history reads unaffected."* After FR-018a a bot's send is **not** rejected at exhaustion, which
  is a documented exception to a clause about predictability. Uncited, a send that succeeds past
  exhaustion is a defect report; cited, it is a decision.
- **FR-015f**: **The sender requirement is not new, and FR-MSG-13 MUST be amended rather than
  added beside.** *"The system shall support sending a message on behalf of any user via API key,
  for backend-originated messages"* — P2, verification T, on the books since v1. So the missing
  concept is the **bot**, not the sender, and FR-015's claim holds only for the first. Two
  consequences:
    - **FR-MSG-13 says "any user" and this chapter permits only a bot** (FR-007). Adding a new
      clause beside it would leave the SRS asserting both, which is precisely the implicit
      resolution the Governance section forbids. The amendment MUST narrow FR-MSG-13 in place.
    - **The clause has never been delivered as written.** Chapter 3.3 satisfied it by sending
      unattributed, and `messages.controller.ts` says so — *"A tenant's own server sending on a
      customer's behalf is FR-MSG-13, not a mistake."* This chapter is the first implementation
      that names the user, so the amendment record MUST say the clause is being **met**, not
      introduced.
- **FR-015g**: An additive-only amendment policy is a decision that has to be re-taken per
  clause. `research.md`'s R9 proposed *"one new clause in each affected family, rather than
  editing existing ones, so the amendment is additive and the diff shows what changed"* — correct
  when nothing conflicts, and wrong here. **Before adding a clause, the amendment MUST establish
  that no existing clause already covers the ground**, which is a question about meaning and
  cannot be answered by `check:srs`: that checker asserts identifiers are unique and deliberately
  does not read what they say.
- **FR-015a**: **The SAD is amended too, and this clause exists because FR-015 named the SAD and
  then did not amend it** for eight analysis passes. `docs/05-sad.md` carries the physical schema:
  its `CREATE TABLE users` lists eight columns and this chapter adds two, plus two CHECK
  constraints. The constitution clause FR-015 quotes covers *"the SRS or SAD"*, and the last
  feature amended `05-sad.md` five times. The amendment MUST add `kind` and `description` to that
  DDL and MUST follow the document's own idiom for a constrained text column —
  `type TEXT NOT NULL CHECK (type IN ('public','private'))` on `channels`, which is the shape
  `data-model.md` chose independently.
- **FR-015b**: Clause identifiers MUST be verified against the governing document before they are
  cited. The amendment was specified as `FR-USR-07` and `FR-MSG-10`; **`FR-MSG-10` is taken** —
  *"History responses shall include tombstones"*, P2, cited by the personas table — and FR-MSG
  runs 01 through 14, so the free identifier is `FR-MSG-15`. Six artifacts named the wrong one,
  none of them inconsistent with each other, because the contradiction lived in a file none of
  them quoted. **Principle VI makes this a constitution violation rather than an inconsistency**: identifiers
  *"carry stable identifiers (`FR-*`, `NFR-*`, `DR-*`, `EIR-*`) that are never reused"*. A check
  MUST enforce it rather than a reader remembering to look (FR-015c).
- **FR-015d**: **`relay-platform/README.md` becomes the quickstart of record, and the sealed
  outsider becomes its CI verification.** The requirement has an SRS twin as well as a
  constitution clause — **NFR-USE-03**, *"The quickstart shall run without modification, verified
  by automated execution in CI against the published documentation"* — and the traceability map
  reads the SRS, so the citation belongs there too. **This feature's own `quickstart.md` is not that
  document** — it is a validation guide no CI job runs, renamed in pass 12 so one word stops
  naming two things, one of which appears in a constitution MUST. Principle VI requires that *"The quickstart MUST run
  unmodified, verified by automated execution in CI against the published documentation."* There
  is no published quickstart anywhere — no `*quickstart*` file in `relay-tutorial` or `docs/`, and
  nothing in `.github/workflows/ci.yml` names one — so the platform has been in violation of a
  constitution MUST since the integration flow first existed. Chapter 3.14 recorded the
  comprehensibility half of this and closed the other. **The automated execution already exists**:
  CI runs `pnpm test:outsider` in its own job. What is missing is published documentation for it
  to run against, which is exactly what this chapter writes.
- **FR-015e**: The verification MUST be the outsider's own run, not a second artifact. The suite
  is sealed from workspace code and stands for an external developer, so the constitution's *"run unmodified,
  verified by automated execution in CI against the published documentation"* is a statement
  about whether its script can be derived from the README — which makes the question this chapter already asks (did it pass first time?) the gate
  itself. **A quickstart nobody executes is the debt this clause exists to prevent**, and a second
  document written to satisfy the clause would recreate it.

- **FR-015c**: A checker MUST assert that every clause identifier in `docs/04-srs.md` is defined
  exactly once, **enforcing principle VI's requirement that identifiers *"are never reused"***.
  `check:docs` compares each mirrored document against its canonical source — drift, not validity
  — so a duplicate identifier passes it: both copies agree and both are wrong. The check MUST
  cover **every identifier class the document uses**, and MUST fail on a class it does not know
  rather than skipping it. Principle VI names four (`FR-*`, `NFR-*`, `DR-*`, `EIR-*`); the
  document uses six, adding `CON-*` and `ASM-*`. Green at **243 clause rows, 243 unique** before this chapter's amendment and **245/245**
  after — the check fired on the build that changed the document, which is what a pinned count
  is for.
- **FR-016**: The amendment MUST land before the chapter claims delivery, and the chapter MUST
  cite the amended clause rather than describe behaviour the governing document does not
  contain. A feature that ships ahead of its requirement is the defect chapter 3.12's
  traceability map recorded and chapters 3.15/3.16 corrected twice.
- **FR-020**: **Published prose this chapter falsifies MUST be corrected, in both locales.** Two
  passages are known:
    - **Chapter 3.10's `<Trap>`** — title *"An unattributed send counts toward the messages and
      toward nobody"*, body *"A key-authenticated REST send carries no user… It still costs a
      message against the message quota… The alternative, inventing a synthetic user for it, would
      inflate the dimension the customer is actually being measured on."* The title is now false,
      and the body **argues against this chapter's decision on the grounds FR-018 decided the
      other way**. The correction MUST carry the distinction rather than deleting the argument:
      3.10 rejected a **synthetic** user the platform invents; a bot is a **declared** one the
      customer creates, names and describes, and inflating a measured dimension with a real
      identity the customer asked for is a different act.
    - **Chapter 3.13** says `sendMessage` stays on the 2.8 seam because it *"is only used to write
      an unattributed row."* The seam may still be right; **its recorded reason is gone**, and a
      reason that stops being true is worse than none because the next reader trusts it.
- **FR-020a**: The chapter MUST record that **no checker reads prose.** `check:fences` replays
  fenced code against the platform repository, `check:figures` asserts a figure has a source,
  `check:docs` compares each mirrored reference document to its canonical copy, and `check:srs`
  reads identifiers. A published sentence asserting something false passes all four. That
  asymmetry is why FR-020's passages survived fifteen analysis passes, and stating it is what a
  reader needs in order to distrust the right things.
- **FR-020b**: Correcting a published page's **prose** does not touch the fence chain. Chapter
  3.10's page carries 36 titled fences and none of them changes here, so `check:fences` will not
  see this edit — which is the same asymmetry as FR-020a and the reason the correction needs a
  task rather than a checker.
- **FR-017**: The chapter MUST state that it **reverses** chapter 3.3's decision rather than
  reinterpreting it, and MUST say why that decision was right when it was made: nothing read
  the sender then, and three chapters since have made the sender decide what is rendered, what
  is delivered and what may be seen. **And it MUST say what the reversal closes** — FR-MSG-13
  required a key to send on behalf of a user before chapter 2.2 shipped the route, and the
  platform has cited that clause for eleven chapters as the justification for naming nobody. A
  requirement satisfied by doing the opposite of what it says is a harder thing to notice than
  one that was never written, and thirteen analysis passes read FR-015's claim that this
  requirement did not exist.

---

## Success Criteria *(mandatory)*

- **SC-001**: A customer can create a bot, describe it, and send a message as it, using only
  the public API.
- **SC-002**: A message sent by a customer's server arrives with an identity a person can
  read, and that identity says it is software rather than a person.
- **SC-003**: No write path in the platform can produce a message with no sender. **Verified in
  two halves, because the two guards fail differently:**
  - **SC-003a** (compile time): reverting `sendMessage`'s `userId` to optional makes
    `pnpm typecheck` report the call sites that would then omit it. The transcript is the
    evidence; there is no test to watch go red, because a removed type constraint makes
    everything compile.
  - **SC-003b** (run time): removing the service's bot check makes a test fail, the way every
    other removal test in this series does.

  **The split exists because the strongest guarantee here is the one FR-035's method cannot
  reach.** A check with no failing test is a check nobody has seen fail — and a compile-time
  check can never have one, so it needs a different kind of evidence rather than an exemption.
- **SC-004**: An application credential cannot post as a person, verified over the public
  route against a real human user of the same tenant.
- **SC-005**: A foreign or non-existent sender is refused indistinguishably, verified by the
  isolation oracle across the same verbs chapter 3.15 covered.
- **SC-006**: A bot cannot obtain a token, verified over the public route.
- **SC-007**: A bot's messages survive its deletion and remain attributed to it.
- **SC-008**: Messages stored before this chapter remain readable on every read path, and what
  a client sees for them is the same on all of them.
- **SC-009**: The SRS carries the amendment, and this feature's traceability map cites the
  amended clause in both directions.
- **SC-010**: The chapter is inside the series' 2,000–4,000 prose-word bound, and every fenced
  file replays onto the platform repository.
- **SC-011**: A bot cannot exhaust a person's active-user allowance: with the ceiling set to the
  number of people who have already sent this period, a bot's send succeeds and a person's first
  send of the period still succeeds after it.
- **SC-012**: An application key's send to a private channel succeeds when the bot it names is
  not a member, and a person's send to the same channel is still refused when they are not.
  Both halves in one test, because the gate they share is one line.
- **SC-013**: A banned bot's send is refused, and the refusal is indistinguishable from the one
  a foreign sender gets.
- **SC-014**: `PATCH /v1/users/:externalId` with `{"description": null}` is refused at the
  boundary, on a bot and on a person, and no request reaches the database able to violate
  `users_bot_description_check`.
- **SC-015**: The quickstart clause of principle VI is satisfied: `relay-platform/README.md`
  describes the bot flow, CI executes the sealed outsider against it, and the run is recorded.
- **SC-016**: Chapter 3.10's Trap is corrected in both locales and states the
  synthetic-versus-declared distinction, and chapter 3.13's stale reason for the 2.8 seam is
  either repaired or replaced.

---

## Assumptions

- **A bot lives in `users` rather than in a table of its own.** Membership, read positions,
  roles, the listing, the ban and every isolation guarantee are keyed on `users.id`; a parallel
  table would fork all of them and would have to be attacked separately by the gauntlet. The
  cost is that `users` now holds two kinds of thing, and every query meaning "a person" has to
  say so.
- **The frame contract does not change.** This is the reason to prefer a bot over a nullable
  sender: `messageSchema.user` stays a non-empty string, no published client tolerates a new
  shape, and chapter 3.16's frame-shape assertion keeps passing. **A nullable sender was
  specified first and rejected** — it looked cheaper until "what does a client render for
  nobody" had to be answered.
- **The description is a field, not metadata.** `users.metadata` exists and is 4 KB of
  arbitrary JSON, so a description could live there. It does not, because a convention inside
  a free-form blob is not a property anything can require, validate or render reliably —
  which is the same argument chapter 3.15 made for `members.role` against `memberships.role`.
- **A bot's identifier shares the person namespace.** `(environment_id, external_id)` is
  unique and everything resolves through it. Two namespaces would mean two lookups on every
  send and a new class of collision.
- **The fan-out is chapter 3.18 and presence is 3.19.** FR-RTM-05 names message creation,
  edit, deletion, membership change, presence change and typing in one clause; the three
  chapters take it in that order, and each states which part of the clause it delivers so it
  is not recorded as delivered three times.

## Dependencies

- Chapter 3.15's attributed public send, which established that the route resolves a caller at
  all.
- Chapter 3.16's user surface — creation, upsert, profile, deletion, ban — which a bot extends
  rather than parallels.
- The isolation gauntlet's oracle and its derived target list, for SC-005.
- `docs/04-srs.md`, which must be amended before delivery is claimed.
