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
- **FR-002b**: An upsert entry that omits `kind` for an existing row MUST be read as **no
  change requested**, not as a request for `"person"`. The default applies on creation only;
  otherwise a bot cannot be edited through the route FR-004 says can edit it.
- **FR-003**: A bot user MUST be distinguishable from a person by a **stored property**, not
  by a naming convention. A client rendering a conversation, a moderator reading an audit
  trail, and a permission check must each be able to tell them apart without parsing an
  identifier.
- **FR-004**: A bot user MUST support the operations a person supports: profile read and
  update, channel membership, roles, listing, ban, and deletion — with FR-USR-05's guarantee
  that its messages survive its deletion, still attributed to it.
- **FR-005**: A bot user MUST NOT authenticate. No token is minted for its identifier and no
  socket opens as it. It is an identity messages are sent *as*, not an account that logs in.
- **FR-005a**: Implicit creation on first authentication (FR-USR-02) MUST NOT create a bot,
  and MUST NOT turn an existing bot into an authenticating user.

### The sender requirement

- **FR-006**: Every message the platform accepts MUST have a sender. No write path may leave
  a message with none.
- **FR-007**: A key-authenticated send MUST name its sender, and the named user MUST be a
  **bot** of that tenant. Naming a person MUST be refused: an API key that can post as any
  human is an impersonation surface.
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

### Billing

- **FR-018**: The chapter MUST decide and state whether a bot's send counts toward
  `usage_active_users`. Active users are a billing dimension (FR-TEN-08, chapter 3.10), so
  charging a customer for their own software is a product decision rather than a side effect,
  and the count MUST be measured before and after a bot's send rather than reasoned about.

### The governing documents

- **FR-015**: The SRS has **no bot, system, or service-account concept** — FR-USR-01 through
  FR-USR-06 describe end users supplied by the customer, and the SAD mentions none either.
  This chapter therefore requires an **explicit amendment** to `docs/04-srs.md`, which is what
  the constitution's Governance section demands: where the constitution conflicts with the SRS
  or SAD, *"the conflict MUST be resolved explicitly by amendment rather than"* ignored.
- **FR-016**: The amendment MUST land before the chapter claims delivery, and the chapter MUST
  cite the amended clause rather than describe behaviour the governing document does not
  contain. A feature that ships ahead of its requirement is the defect chapter 3.12's
  traceability map recorded and chapters 3.15/3.16 corrected twice.
- **FR-017**: The chapter MUST state that it **reverses** chapter 3.3's decision rather than
  reinterpreting it, and MUST say why that decision was right when it was made: nothing read
  the sender then, and three chapters since have made the sender decide what is rendered, what
  is delivered and what may be seen.

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
