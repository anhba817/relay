# Feature Specification: Chapter 3.15 — the surface a customer drives

**Feature Branch**: `main`
**Created**: 2026-08-23
**Status**: Draft
**Input**: "Start chapter 3.15"

## Why this feature exists

Chapter 3.12 refused `type: "private"` at the door, and said why: `channels.type`
has been a `"public" | "private"` column with a CHECK constraint since chapter 2.1,
and **nothing in the platform reads it**. Accepting the word would have sold a
guarantee the platform does not keep.

Auditing the rest of the deferred surface before writing a line of this spec found
the same thing four more times. Five columns exist that no non-test source reads:

| Column | Requirement it stands for | Priority |
|---|---|---|
| `channels.type` | FR-CHN-03, FR-CHN-05 | P1 |
| `users.avatar_url` | FR-USR-03 | P1 |
| `users.metadata` | FR-USR-03 | P1 |
| `channels.archived_at` | FR-CHN-10 | P2 |
| `users.banned_at` | FR-USR-06 | P3 |

Measured with `grep` over `services/**` and `packages/**`, excluding `*.test.ts`,
`*.itest.ts`, `schema.ts` itself and build output: **zero reads each**.

A schema that declares a column is a promise in the same way prose is, and this is
the fifth instance of a pattern chapters 3.12 to 3.14 kept finding: `field` in
EIR-API-04 declared and never set, `PlatformService` recorded as "for logs" and
enforcing nothing, `request_id` promised in 1.3 and first sent in 3.8, `docs_url`
pointing at a host that does not resolve. The column is the same shape of promise one
layer down — and unlike prose, a column also costs a migration to remove, so the
choice is to make it live or to say beside it that it is not.

**This feature closes the whole deferred surface**: **twelve** SRS clauses across
FR-CHN and FR-USR, the five columns, and four corrections to what chapters 3.12 to
3.14 recorded — one of them a whole class rather than a sentence, because the previous
feature shipped as three chapters and 31 files still cite it as one (FR-038a).

    FR-CHN-03  P1   the private type accepted and meaningful
    FR-CHN-04  P2   member roles — no column exists
    FR-CHN-05  P1   a private channel is visible only to its members
    FR-CHN-06  P1   the removal half; 3.13 delivered adding
    FR-CHN-08  P1   channel listing, cursor-paginated, activity-ordered
    FR-CHN-09  P2   unread counts and last message — no read position exists
    FR-CHN-10  P2   archiving; the column exists and nothing reads it
    FR-USR-02  P1   implicit creation on first AUTHENTICATION, not membership
    FR-USR-03  P1   profile: display name, avatar, metadata
    FR-USR-04  P2   upsert up to 100 users
    FR-USR-05  P2   deletion that keeps messages attributable
    FR-USR-06  P3   banning; the column exists and nothing reads it

### The gap that is not a missing column

FR-CHN-05 says a user shall not read from, send to, or observe presence in a private
channel of which they are not a member. `POST /internal/messages` — the route both
the socket and a server-side send on a user's behalf go through — resolves the
caller's user and **does not check membership**:

```
services/api/src/internal/internal.controller.ts
  const userExternalId = principalUser(req);
  const user = await this.repo.getUserByExternalId(userExternalId);
  if (!user) throw new BadRequestException("unknown user");
  const message = await this.messages.send(body.channel_id, { … }, user.id, userExternalId);
```

A user token can send into any channel in its own environment, member or not. That is
true today for `public` channels as well, so it is not a private-channel problem — it
is the membership property being absent, which is why FR-CHN-05 could not be
delivered by adding a type check.

What already holds, and is worth stating so the feature does not claim it: the
**resume** path checks membership (`repository.backfill` joins `members` on the
caller's user id), and the **session** path builds its channel list from
`channelsForUser`. A user's socket subscribes only to channels they belong to, and
backfills only those. Reading is membership-scoped; **sending is not**.

**Which means a sentence chapter 3.12 shipped is wrong.**
`services/api/src/channels/channels.schema.ts:26` says, in a comment chapter 3.13
fences and both locales carry:

> `channels.type` has been a `"public" | "private"` column with a CHECK constraint
> since chapter 2.1, and NOTHING IN THE PLATFORM READS IT. History and send scope by
> `environment_id` alone; **there is no membership check on any read path.**

The first half is true and the emphasised half is not. Both `repository.backfill` and
`session.controller` are read paths and both check membership. What is true is
narrower and more useful: **the public history and send routes are
application-authenticated and check nothing, and `POST /internal/messages` resolves a
user and checks nothing.** The claim reached shipped code because chapter 3.12
measured the public routes and generalised.

### And a twelfth clause, whose absence already surfaces as a confusing error

FR-USR-02 (P1) says a user record shall be created implicitly **on first
authentication** if it does not exist. `createUser` is called from exactly one
non-test place in the platform — `channels.service.ts`, on first **membership**,
added by chapter 3.13. `POST /auth/dev-token` mints a token for an identifier that
need not exist and creates nothing.

That is not a dormant gap. `POST /internal/messages` looks the user up and throws
`BadRequestException("unknown user")` when it cannot find one — so a token minted
for a never-seen user authenticates perfectly and then fails its first send with a
`400` that reads like the caller's mistake. The clause exists to prevent exactly
that sequence.

### Three things the schema cannot do yet

Auditing the rest of the surface turned up three constraints that shape the work
rather than following from it:

- **`channels.last_sequence` cannot order channels by recency.** FR-CHN-08 asks for a
  user's channels ordered by most recent activity. `last_sequence` is a per-channel
  monotonic counter, so two channels both at 50 say nothing about which was active
  more recently. Ordering by activity needs a timestamp — a column, or the maximum
  `messages.created_at` per channel, which is a different cost.
- **There is no read position anywhere.** FR-CHN-09's unread count needs to know how
  far a user has read in a channel, and nothing in the schema records it. Measured:
  no `last_read`, `read_at` or equivalent in any table.
- **Deleting a user cannot simply delete the row.** `messages.user_id`,
  `members.user_id` and `usage_active_users.user_id` all reference `users.id`.
  FR-USR-05 asks that messages be preserved "as authored by a deleted user" — and
  chapters 3.13 and 3.14 established that a NULL `user_id` makes a message invisible
  to sockets, because `toFrame` drops senderless rows. So "authored by a deleted user"
  and "authored by nobody" are different states, and only one of them is what the
  clause asks for. `usage_active_users` is billing history and must not vanish with a
  profile.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A private channel is private (Priority: P1)

A customer creates a channel of type `private`, adds two of their users, and a third
user of the same tenant cannot see or reach it: not by sending, not on the socket, not
through resume, not in a listing.

**Why this priority**: FR-CHN-05 is P1 and the SRS gives it a sentence of its own,
separate from FR-CHN-03's type list. It is the clause chapter 3.12 refused an endpoint
over, so this story is what makes that refusal unnecessary.

**Independent test**: create a private channel with two members, mint a token for a
third user of the same tenant, and attempt every verb. Each is refused or empty, and
the refusal for a private channel the caller cannot see is identical to the refusal
for a channel that does not exist.

**Acceptance Scenarios**

1. **Given** a private channel with members A and B, **When** user C of the same
   tenant sends to it with a valid user token, **Then** the send is refused and the
   channel gains no message, read back from the channel rather than inferred from the
   refusal.
2. **Given** the same channel, **When** C presents a resume cursor naming it,
   **Then** the accepted cursor omits it and no message from it is delivered.
3. **Given** the same channel, **When** C's socket is open and A sends to it,
   **Then** C receives nothing.
4. **Given** the same channel, **When** C asks for it by id on any read route,
   **Then** the answer is identical to the answer for an id that exists nowhere —
   same status, same body but for `request_id`.
5. **Given** a `public` channel, **When** C sends to it without being a member,
   **Then** the behaviour is whatever this feature decides for public channels,
   stated once and tested, rather than left to the absence of a check.

### User Story 2 - Membership can be taken away (Priority: P1)

FR-CHN-06 has two halves — adding and removing up to 100 members in one request — and
chapter 3.13 delivered only adding.

**Why this priority**: membership enforcement cannot be tested without removal. A
suite that can only add members can assert that a non-member is refused, but never
that someone who *was* a member stops being able to reach a channel, which is the case
a customer removing an employee cares about.

**Independent test**: add a user, confirm they can send and receive, remove them,
confirm both stop, and confirm their existing messages are still in the history.

**Acceptance Scenarios**

1. **Given** a member of a private channel with an open socket, **When** the customer
   removes them, **Then** their subsequent sends are refused.
2. **Given** the same removal, **When** they reconnect, **Then** the channel is not in
   their session and a cursor naming it is not accepted.
3. **Given** the same removal, **Then** the messages they wrote while a member remain
   in the channel's history, attributed to them.
4. **Given** a removal request naming 100 users, **Then** it is accepted; 101 is
   refused with `invalid_request` naming the field.
5. **Given** a removal naming a user who is not a member, **Then** the request succeeds
   and says so per user, in the shape chapter 3.13 chose for adding.

### User Story 3 - A user has a profile a customer can set (Priority: P1)

`users.display_name`, `users.avatar_url` and `users.metadata` exist and no route
writes them.

**Why this priority**: FR-USR-03 is P1, and a chat platform where a customer cannot
set a display name is not usable for the product this series is building. Two of the
three columns have never been written by anything.

**Independent test**: set all three fields on a user through the public API, read them
back, confirm they appear where a user is rendered, and confirm metadata over 4 KB is
refused with the field named.

**Acceptance Scenarios**

1. **Given** a user created by first membership, **When** the customer sets a display
   name, avatar URL and metadata, **Then** all three are stored and returned.
2. **Given** metadata over 4 KB of JSON, **Then** the request is refused with
   `invalid_request` and `field` naming `metadata` — the bound FR-USR-03 states, which
   is half of the 8 KB FR-CHN-01 allows a channel.
3. **Given** a user with a display name, **When** a message they wrote is delivered on
   a socket, **Then** the frame carries whatever identity the wire contract already
   specifies, unchanged by this feature — the profile is stored, and changing the
   frame shape is not in scope.
4. **Given** an avatar URL that is not a URL, **Then** it is refused with the field
   named.

### User Story 4 - A customer lists a user's channels (Priority: P1)

FR-CHN-08 asks for a user's channels, ordered by most recent activity, with cursor
pagination. `listChannels()` exists in the repository with no pagination, no ordering
and no caller.

**Why this priority**: P1, and it is the operation a client needs before it can render
anything. Without it a customer knows a user's channels only by having recorded them
when it created them.

**Independent test**: create several channels with staggered activity for one user,
list them, confirm the order, page through with the cursor, and confirm a channel the
user is not a member of never appears.

**Acceptance Scenarios**

1. **Given** a user in three channels with messages at different times, **When** the
   customer lists their channels, **Then** the most recently active is first.
2. **Given** more channels than one page holds, **When** the caller follows the
   cursor, **Then** every channel appears exactly once across the pages and none is
   skipped when a new message arrives mid-pagination, or the drift is documented the
   way chapter 2.4 documented history's.
3. **Given** a private channel the user is not a member of, **Then** it never appears
   in their listing.
4. **Given** an archived channel, **Then** whether it appears is stated and tested.

### User Story 5 - The listing says what is unread (Priority: P2)

FR-CHN-09 asks that channel listings include the caller's unread count and the most
recent message. Nothing records a read position.

**Why this priority**: P2 in the SRS, and it depends on User Story 4 existing first. It
is also the one part of this feature that needs storage that does not exist, which
makes it the part most likely to be split out.

**Independent test**: send messages to a channel, confirm the unread count rises,
record a read position, confirm it falls to zero, send again, confirm it rises from
there.

**Acceptance Scenarios**

1. **Given** a channel with five messages and a user who has read none, **Then** the
   listing reports five unread.
2. **Given** the user marks a position, **Then** the listing reports zero, and a later
   message makes it one.
3. **Given** a user's own message, **Then** whether it counts as unread for its author
   is stated and tested.
4. **Given** a channel with a tombstoned last message, **Then** the "most recent
   message" the listing reports is stated — a tombstone has no text.
5. **Given** a read position beyond the channel's last sequence, **Then** the request
   is refused rather than stored, because a position nothing can reach makes every
   later count wrong.

### User Story 6 - Members hold roles (Priority: P2)

FR-CHN-04 asks that members hold one of `owner`, `moderator` or `member`. The `members`
table is `(channel_id, user_id, joined_at)` and has no role column.

**Why this priority**: P2 in the SRS. It is also the clause chapter 3.12's traceability
map recorded as delivered, which it is not, so this feature both builds it and corrects
that record.

**Independent test**: add a member with each role, read them back, and confirm the role
vocabulary is the SRS's rather than the one `memberships` already uses.

**Acceptance Scenarios**

1. **Given** the members endpoint, **When** a member is added with a role, **Then** the
   role is stored and returned.
2. **Given** a member added without a role, **Then** the default is stated and applied.
3. **Given** a role outside the SRS's three, **Then** it is refused with the field
   named.
4. **Given** the existing `memberships.role` CHECK constraint, **Then** this feature
   does not reuse its vocabulary — `memberships` allows `owner`, `admin`, `member` for
   humans in an organisation, and channel roles are `owner`, `moderator`, `member` for
   users in a channel. Two tables, two vocabularies, stated so neither is used for the
   other.
5. **Given** roles exist, **Then** whether any operation checks them is stated. A role
   nothing reads is the sixth instance of this feature's own subject.

### User Story 7 - A channel can be archived (Priority: P2)

`channels.archived_at` exists and nothing reads it.

**Why this priority**: P2. FR-CHN-10 asks that archiving preserve history, prevent new
messages, and be reversible.

**Independent test**: archive a channel, confirm sends are refused and history still
reads, unarchive it, confirm sends work again.

**Acceptance Scenarios**

1. **Given** an archived channel, **When** anyone sends to it, **Then** the send is
   refused with a code that distinguishes "archived" from "not found" and from "not a
   member".
2. **Given** an archived channel, **When** a member reads its history, **Then** the
   history is unchanged.
3. **Given** an archived channel, **When** it is unarchived, **Then** sends work again
   and no message was lost.
4. **Given** an archived channel, **Then** whether the socket delivers anything for it
   is stated and tested.

### User Story 8 - Users upsert in bulk, and can be deleted (Priority: P2)

FR-USR-04 asks for upserting up to 100 users in one request; FR-USR-05 asks that
deleting a user remove profile data and memberships while preserving their messages as
authored by a deleted user.

**Why this priority**: P2 for both. Deletion is also a compliance surface — FR-TEN-08's
erasure and DR-06's retention both touch it — so getting the shape wrong is expensive
later.

**Independent test**: upsert 100 users in one call, confirm each; delete one, confirm
their profile and memberships are gone, their messages remain and are still
attributable, and their usage rows are untouched.

**Acceptance Scenarios**

1. **Given** 100 users in one request, **Then** all are created or updated and each is
   reported; 101 is refused with the field named.
2. **Given** an upsert naming an existing user, **Then** it updates rather than
   failing, and states which fields it changed.
3. **Given** a deleted user, **Then** their profile fields are cleared and their
   memberships are gone.
4. **Given** a deleted user, **Then** the messages they wrote are still in history and
   still distinguishable from a message that never had an author — which chapters 3.13
   and 3.14 established is not the same thing, because a NULL author makes a message
   invisible to sockets.
5. **Given** a deleted user, **Then** their rows in `usage_active_users` are unchanged,
   because that is billing history.
6. **Given** a deleted user's external id used again, **Then** whether it creates a new
   user or is refused is stated.

### User Story 9 - A user can be banned (Priority: P3)

`users.banned_at` exists and nothing reads it.

**Why this priority**: P3, the lowest in this feature. FR-USR-06 asks that banning
prevent connection and message send at tenant scope while preserving history.

**Independent test**: ban a user with an open socket, confirm the socket closes or
their sends are refused, confirm their history is intact, unban, confirm they work.

**Acceptance Scenarios**

1. **Given** a banned user, **When** they open a socket, **Then** the connection is
   refused with a close code that says why.
2. **Given** a banned user with an open socket at the moment of the ban, **Then**
   whether the existing connection is closed or merely stops accepting sends is stated
   and tested.
3. **Given** a banned user, **Then** their existing messages remain readable by others.
4. **Given** a banned user, **When** the ban is lifted, **Then** they connect and send
   again.

### Edge Cases

- A user removed from a channel **while a message of theirs is in flight**: the send
  was accepted before removal and the row exists. Removal is not retroactive.
- A channel whose **last member is removed**: reachable by nobody, and not deleted —
  archiving and deletion are different operations.
- The **application credential** on a private channel. It acts for the tenant and has
  no user, so "not a member" has no meaning for it. Stated once rather than falling out
  of a missing check.
- A **cursor naming a private channel the caller left an hour ago**: resume must not
  backfill it.
- **Presence** in a private channel. FR-CHN-05 names presence alongside read and send;
  FR-RTM-07 owns delivery scope. In scope or deferred with a number, not silent.
- A **public channel and a non-member**. FR-CHN-03 says any authenticated user of the
  tenant may read and **join** a public channel. "Join" implies a user-initiated
  membership operation that does not exist. Building it or deferring it changes what
  "public" means today.
- **Two tenants using the same `external_id`**, one private and one public: the
  identifier is per-tenant and so are the types.
- **Unread count for a channel with no read position ever recorded**: every message
  unread, or zero? A client that shows every channel as fully unread on first load is
  a bad first impression; one that shows zero hides real messages.
- **Archiving a channel a user has unread messages in**: the count is still true and
  the channel is still listed, or it is hidden and the count is lost.
- **Deleting a user who is the `owner` of a channel**: FR-CHN-04's roles and
  FR-USR-05's deletion collide, and one of them has to say what happens.
- **Banning a user who is a member of a private channel**: the ban is tenant-scoped and
  membership is channel-scoped, so the ban wins, and the reason is stated.
- **A token minted for an identifier that is then used by a membership call**: implicit
  creation happens twice for one external identifier, and must produce one row.
- **A source comment citing a chapter for something other than its own file**, such as
  chapter 2.2 for `last_sequence`. FR-038a's rule is about the chapter a change was
  taught in, so a citation like that is already right and rewriting it would be the
  correction making things worse.
- **A token minted for a BANNED user's identifier**: implicit creation must not
  resurrect a banned user as a fresh one, which is the interaction between FR-USR-02
  and FR-USR-06.

## Requirements *(mandatory)*

### Functional Requirements

**Membership and the private type**

- **FR-001**: A user MUST NOT send a message to a private channel of which they are not
  a member. The refusal MUST leave the channel unchanged, verified by reading the
  channel's messages rather than by the refusal's status.
- **FR-002**: A user MUST NOT receive messages from, resume into, or subscribe to a
  private channel of which they are not a member.
- **FR-003**: For a private channel the caller cannot see, every read MUST answer
  identically to a channel that does not exist — same status and same body but for
  `request_id`. A private channel's existence MUST NOT be discoverable.
- **FR-004**: The feature MUST state and test what a `public` channel means for a
  non-member on each verb. The current behaviour — any user of the tenant may send to
  any channel — MUST be kept deliberately or changed deliberately, with the decision
  recorded.
- **FR-005**: The feature MUST state what a private channel means for an application
  credential, which carries no user.
- **FR-006**: The public API MUST support removing members by customer-supplied user
  identifier, up to 100 in one request.
- **FR-007**: Removal MUST be idempotent in the shape chapter 3.13 chose for adding:
  removing a non-member succeeds and says so per user.
- **FR-008**: Removal MUST NOT delete the removed user's messages.
- **FR-009**: `POST /v1/channels` MUST accept `type: "private"` once FR-001 to FR-003
  hold, and MUST NOT accept it before.
- **FR-010**: A repeated creation naming a different type MUST NOT change the existing
  channel's type.
- **FR-011**: Members MUST hold one of `owner`, `moderator` or `member`, with a stated
  default. A role outside the three MUST be refused with the field named.
- **FR-012**: The feature MUST state whether any operation reads a member's role. A
  role nothing reads is this feature's own subject repeated.

**Listing and unread**

- **FR-013**: The public API MUST support listing a user's channels with cursor
  pagination, ordered by most recent activity.
- **FR-014**: The feature MUST state what "most recent activity" is measured by.
  `channels.last_sequence` is a per-channel counter and cannot order channels against
  each other, so this requires a timestamp the schema does not have or a per-channel
  aggregate over `messages.created_at`.
- **FR-015**: A channel the caller is not a member of MUST NOT appear in their listing.
- **FR-016**: Channel listings MUST include the caller's unread count and the most
  recent message.
- **FR-017**: The feature MUST record a per-user, per-channel read position, and MUST
  state what an absent position means for the count.
- **FR-018**: A read position beyond the channel's last sequence MUST be refused.
- **FR-019**: The feature MUST state what "most recent message" reports when that
  message is a tombstone.

**Archiving**

- **FR-020**: Archiving a channel MUST prevent new messages and preserve history, and
  MUST be reversible.
- **FR-021**: A send to an archived channel MUST be refused with a code that
  distinguishes archived from not-found and from not-a-member.
- **FR-022**: The feature MUST state whether an archived channel appears in a listing
  and whether the socket delivers anything for it.

**Users**

- **FR-023**: The public API MUST support setting and updating a user's display name,
  avatar URL and metadata, with metadata bounded at 4 KB of JSON.
- **FR-024**: Metadata over the bound and a malformed avatar URL MUST be refused with
  `invalid_request` and `field` naming the offending key.
- **FR-025**: The public API MUST support upserting up to 100 users in one request,
  reporting each, and refusing 101 with the field named.
- **FR-026**: An upsert naming an existing user MUST update rather than fail.
- **FR-027**: Deleting a user MUST remove their profile data and memberships.
- **FR-028**: Deleting a user MUST preserve their messages as authored by a deleted
  user, which MUST remain distinguishable from a message that never had an author —
  chapters 3.13 and 3.14 established that a NULL author makes a message invisible to
  sockets, so the two states cannot be the same.
- **FR-029**: Deleting a user MUST NOT change their rows in `usage_active_users`, which
  are billing history.
- **FR-030**: The feature MUST state what happens when a deleted user's external
  identifier is used again.
- **FR-031**: Banning a user MUST prevent connection and message send at tenant scope
  while preserving history, and MUST be reversible.
- **FR-032**: The feature MUST state what a ban does to a connection that is already
  open.

**The suite, and the records**

- **FR-033**: Every route this feature adds MUST appear in the cross-tenant suite's
  derived target list on the build that introduces it, and be attacked or carry a
  written exemption.
- **FR-034**: The cross-tenant suite MUST gain the same-tenant, non-member attack.
  Today it attacks with another tenant's identifiers only, so a non-member of the
  caller's own tenant is a case no assertion covers. This is a new fixture — one
  environment, two users, one channel — not a reuse of the two-tenant one.
- **FR-035**: Each newly enforced column MUST be shown to be read, by a test that fails
  when the read is removed. Being written is not being read; chapter 3.13 recorded the
  same distinction for the guard's trigger array.
- **FR-036**: The feature MUST state, for every column in the table above, whether it
  is now live or still unread, with the requirement it stands for and the chapter that
  owns it.
- **FR-037**: The feature MUST correct
  `services/api/src/channels/channels.schema.ts:26`, whose comment says "there is no
  membership check on any read path" when `repository.backfill` and
  `session.controller` both check membership. The comment sits inside a titled fence in
  chapter 3.13's page, so the platform file, the English page and the Vietnamese page
  move together or `pnpm check:fences` fails.
- **FR-038**: Chapter 3.12's traceability map recorded FR-CHN-04 as delivered by its
  FR-019, with a paraphrase — "members by customer-supplied user id" — belonging to
  FR-CHN-06. **Corrected in that map while this spec was written**; this requirement is
  here so the chapter states the correction rather than leaving it in a file nobody
  re-reads.
- **FR-038a**: Every source comment that attributes a change to a chapter MUST name the
  chapter whose page teaches that change. Measured: 31 platform files carry 40
  "chapter 3.12" citations, written while the previous feature was still one chapter,
  and 12 of those files are fenced in chapter 3.12's page — 9 are taught in chapter
  3.13, 9 in chapter 3.14, and 1 only in the post-series appendix. All 40 MUST be
  classified and every wrong chapter number corrected. A citation naming a chapter for
  something other than the cited file's own change — chapter 2.2 for `last_sequence`,
  for example — is already correct and MUST NOT be rewritten.
- **FR-038b**: The requirement and research identifiers inside those comments MUST NOT
  change. `FR-025` and `R14a` name the feature record `specs/033-chapter-3-12/`, which
  keeps its number because a feature directory is named once. Only the chapter number
  is wrong, and a corrected comment inside a titled fence moves the platform file, the
  English page and the Vietnamese page together, as FR-037 requires.
- **FR-039**: The feature MUST document the status code of every public route it adds
  or touches, closing chapter 3.14's gap G5 for those routes.
- **FR-039a**: A user record MUST be created implicitly on first authentication if it
  does not exist (FR-USR-02). Today `createUser` is reached only from first
  membership, so a token minted for an unknown identifier authenticates and then fails
  its first send with `unknown user` — a `400` that names the caller rather than the
  cause.
- **FR-039b**: The feature MUST state whether implicit creation on authentication and
  implicit creation on membership produce the same user record, and MUST NOT create two
  rows for one external identifier. Chapter 3.13 made `createUser` idempotent on
  `(environment_id, external_id)`, which is the property this relies on.
- **FR-040**: The feature MUST form its chapter split from a measured file count
  **before any chapter prose is written**, and record the count either way. Chapter
  3.12 estimated 37 fenced files, shipped 61, and took the split at Phase 12 — its own
  task list records that forming the estimate earlier is what makes the split free.

### Key Entities

- **Channel membership** — `(channel_id, user_id, joined_at)`. Gains a role column
  (FR-011) and a removal path (FR-006).
- **Channel type** — `channels.type`, `"public" | "private"` with a CHECK constraint
  since chapter 2.1, read by nothing until this feature.
- **Read position** — new. Per user, per channel, the sequence up to which that user
  has read. The only entity in this feature with no storage today.
- **Channel activity** — how a channel's recency is measured for FR-CHN-08's ordering.
  Either a new timestamp or an aggregate; `last_sequence` cannot do it.
- **User profile** — `users.display_name`, `users.avatar_url`, `users.metadata`. Two of
  the three have never been written by any route.
- **Archive state** — `channels.archived_at`, read by nothing.
- **Ban state** — `users.banned_at`, read by nothing.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user of the same tenant who is not a member of a private channel cannot
  reach it by any verb, demonstrated by one test per verb — send, resume, subscribe,
  read by id.
- **SC-002**: For each of those verbs, the answer for a private channel the caller
  cannot see is byte-identical to the answer for a channel that does not exist, but for
  `request_id`.
- **SC-003**: A send refused under FR-001 leaves the target channel's message count
  unchanged, read from the channel.
- **SC-004**: A removed member's sends are refused and their reconnection does not
  include the channel, both demonstrated against a socket open at the moment of
  removal.
- **SC-005**: A removed member's existing messages are still in history, attributed to
  them, counted before and after.
- **SC-006**: `POST /v1/channels` accepts `private` and the row's type reads back as
  `private`; a repeat naming a different type returns the existing channel unchanged.
- **SC-007**: A listing returns a user's channels most-recently-active first, pages
  through with a cursor with no channel appearing twice or being skipped, and never
  includes a channel the user is not a member of.
- **SC-008**: An unread count rises with each message, falls to zero when a position is
  recorded, and rises again from there — with the answer for a channel that has never
  had a position recorded stated and tested.
- **SC-009**: A member's role round-trips through the API, a fourth role value is
  refused with the field named, and the feature states whether any operation reads the
  role.
- **SC-010**: An archived channel refuses sends with a code distinct from not-found and
  not-a-member, still serves history, and accepts sends again after unarchiving.
- **SC-011**: All three profile fields round-trip; metadata over 4 KB and a malformed
  avatar URL are each refused with `field` naming the key.
- **SC-012**: 100 users upsert in one request and 101 is refused; a deleted user's
  profile and memberships are gone, their messages remain attributable, and their
  `usage_active_users` rows are unchanged — each read back from storage.
- **SC-013**: A banned user cannot connect, their history is still readable by others,
  and lifting the ban restores both.
- **SC-014**: The cross-tenant suite's derived target count moves by exactly the number
  of routes this feature adds, and no route is unclassified.
- **SC-015**: The suite gains at least one same-tenant non-member attack per verb, and
  each is shown to fail when the membership check is removed.
- **SC-016**: The count of schema columns with no non-test reader is stated before and
  after, with each remaining one named beside the requirement it stands for.
- **SC-017**: The integration lane stays green across twenty consecutive runs, with the
  test count and duration recorded for each against a stated per-run budget.
- **SC-018**: Every published page's prose word count is inside 2,000–4,000, counted
  rather than estimated, with the fence count stated against the changed-file count.
- **SC-019**: The chapter split is recorded with the file count that produced it, and
  the count was taken before any chapter prose existed.
- **SC-020**: A token minted for an identifier no user record exists for can send a
  message without a prior membership call, demonstrated end to end — which is the
  sequence that returns `unknown user` today.
- **SC-021**: All 40 chapter citations are classified, the count that attributed a
  change to a chapter not teaching it is recorded, and that count reaches zero —
  counted by the same command before and after.

## Assumptions

- **The whole deferred surface is in scope, and the chapter division is a plan-time
  decision.** Twelve SRS clauses, five columns, four corrections. This is larger than
  any single chapter in this part has carried: chapter 3.12's feature came to 61 files
  and published as three chapters. So FR-040 requires the split to be measured at
  planning rather than discovered at page-counting, which is the one thing chapter
  3.12's close-out asks the next feature to do differently.
- **Reading is already membership-scoped and sending is not.** Verified by reading
  `repository.backfill` and `session.controller`. This feature's work on reading is to
  confirm and test a property that holds; its work on sending is to create one.
- **A private channel's refusal follows FR-TEN-05's shape.** The platform already
  answers a foreign identifier exactly as an absent one, and a private channel the
  caller cannot see is the same class of answer, so it reuses chapter 3.12's oracle
  rather than inventing a second convention.
- **An application credential sees private channels.** It acts for the tenant, carries
  no user, and is the customer's own server. FR-005 asks the feature to state this
  rather than assume it; this is the stated default.
- **`joined_at` is enough membership history.** Nothing here needs to know when someone
  left, so removal deletes the row rather than tombstoning it.
- **Read positions are per user and per channel, and advance only forwards.** A client
  that reports a position behind the one already stored is not moving the position
  backwards; FR-018 covers the forwards bound and the same reasoning covers the other
  direction.
- **A user's own message is read by them.** Otherwise every send raises the sender's own
  unread count, which no chat client shows. FR-016's tests state it either way.
- **Deletion clears profile fields rather than removing the user row.** The row is what
  `messages.user_id` points at, and FR-028 requires a deleted author to stay
  distinguishable from no author. A row with cleared fields and a deletion marker does
  that; `ON DELETE SET NULL` does not.
- **Twenty runs and the size bound carry forward** with the ranges chapters 3.12 to 3.14
  recorded: twenty green runs reject a per-run failure rate of 13.91% or worse and
  nothing gentler, and the lane's budget is 240 seconds against a 193-second
  measurement.

## Dependencies

- Chapter 3.13's `POST /v1/channels/:channelId/members`, beside which removal sits and
  whose per-user result shape it reuses.
- Chapter 3.13's idempotent `createUser`, which the bulk upsert extends.
- Chapter 3.12's cross-tenant suite and derived target list, which FR-033 and FR-034
  extend.
- Chapter 3.12's indistinguishability oracle in `services/api/src/isolation/compare.ts`,
  which FR-003 reuses.
- Chapter 2.4's cursor encoding in `services/api/src/messages/cursor.ts`, which
  FR-013's pagination can reuse or deliberately not.
- `repository.backfill`'s membership join and `session.controller`'s `channelsForUser`,
  which this feature tests rather than writes.
- Chapter 3.14's error registry, for every refusal in this feature that needs a code
  that does not exist yet — archived, banned, and not-a-member are three candidates.
- Chapter 3.13's fenced comment in `channels.schema.ts`, which FR-037 corrects in three
  files at once.
- The three published pages of chapters 3.12, 3.13 and 3.14, which FR-038a classifies
  40 source citations against. The classification depends on which page fences which
  file, so it cannot be done from the platform repository alone.
