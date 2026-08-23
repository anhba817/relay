# Contract — who may act on a channel

The authorization table for every channel verb, and the routes chapter 3.15 adds.
FR-039 requires a documented status code for each; this file is where that lives.

## The authorization table

The caller is a user of the tenant, identified by `X-Relay-User` or by a socket
session. "Member" means a row in `members` for `(channel_id, user_id)`.

| Verb | `public`, member | `public`, non-member | `private`, member | `private`, non-member |
|---|---|---|---|---|
| create the channel | tenant credential, not a user | — | tenant credential | — |
| read the channel by id | 200 | 200 | 200 | **404** |
| read history | 200 | 200 | 200 | **404** |
| send a message | 201 | 201 | 201 | **404** — the not-found envelope |
| appear in the listed user's listing | yes | no | yes | no |
| subscribed on the socket | yes | **no** | yes | no |
| join | already in | 200, becomes a member | already in | **404** |
| set a read position | 200 | **403 `not_a_member`** | 200 | **404** |
| remove members | tenant credential | tenant credential | tenant credential | tenant credential — 404 only if the channel does not exist |
| set a member's role | tenant credential | tenant credential | tenant credential | tenant credential |
| archive or unarchive | tenant credential | tenant credential | tenant credential | tenant credential |

The last three rows and `create the channel` are the tenant's verbs: an application credential
acts for the tenant, carries no user and sees private channels (FR-005), so the member columns
do not vary. They are in the table because leaving them out made it look like the table covered
every verb when it covered eight of eleven.

**The send row said `403 not_a_member` until analysis pass six.** SC-002 requires the
answer for each of SC-001's four verbs — send included — to be byte-identical to a channel
that does not exist, and a 403 naming the membership announces that the channel exists.
The oracle chapter 3.12 built for cross-tenant pairs catches exactly this, so T043 would
have failed against the implementation the same feature specified. The read-position row
two lines down had it right; this row was written minutes later and did not.

**Two different refusals, and the difference is the whole isolation argument.**

A private channel the caller cannot see answers **404 with the body of a channel that
does not exist** — status and body identical, `request_id` excepted. That is FR-TEN-05's
indistinguishability property applied inside a tenant instead of across tenants, and
chapter 3.12 built the oracle that checks it.

A public channel the caller is not a member of is **not hidden** — FR-CHN-03 says any
authenticated user of the tenant may read and join it. So a refusal there says
`not_a_member` and means it. Telling the caller which channel they are not a member of
leaks nothing they could not read anyway.

**And a non-member may send to a public channel**, which the clause does not say and
FR-004 is what decides. R3 has the argument: refusing a write that a join — which cannot
itself be refused — would immediately permit is a refusal with nothing behind it. So
`public` means "open to this tenant", not "readable by this tenant", and the read
position is the one verb where membership still matters on a public channel, because a
read position is per-member state and a non-member has none.

**An archived channel refuses sends with `403 channel_archived` — but only once the
caller can see it.** FR-021a fixes the order: **ban, then membership and visibility, then
archive.** Reversing the last two makes the archive refusal an existence oracle, because a
non-member of a private archived channel would learn it exists from `channel_archived`.
The order was ban-archive-membership until analysis pass six.

**A banned user is refused before the channel is resolved at all.** `403 user_banned` on
send, and the socket refused at connect. That placement is deliberate: resolve the channel
first and the ban path becomes the oracle the membership path is not allowed to be, since
a banned user would learn which channel ids exist. Chapter 3.16 owns the ban; it is in this
table because the order has to be one order.

**Where `not_a_member` is actually emitted**, now that private sends answer 404 and public
sends are permitted: **one place — the read-position route on a public channel by a
non-member.** A read position is per-member state, keyed by channel and user, and removal
deletes the row (T053), so refusing a non-member is the same rule the table already keeps.
The code is registered in Phase 2 with the other two and its only emitter is in chapter
3.16.

**Paths here are written with the customer's external id in the position it occupies.**
The router names that parameter **`:channelId`**, and `targets.ts`'s classification list
stores the literal router path — `"/v1/channels/:channelId/members"`. A classification
entry written from this file's `:externalId` will not match a derived target, and the
suite fails on the build that adds it. Analysis pass three found the drift before it cost
a run.

## Routes chapter 3.15 adds

### `GET /v1/channels/:channelId`

Returns the four elements FR-CHN-01 defines: external id, type, name, metadata. Plus
`archived_at` and the membership of whoever the credential identifies — the user under a user token, and nothing under an application key, which acts for the tenant and is a member of nothing. A client that just read a channel
should not need a second call to know whether it may post.

| Outcome | Status |
|---|---|
| read | 200 |
| `public`, caller not a member | 200 |
| `private`, caller not a member | 404 — the not-found envelope, byte-identical |
| no such channel | 404 |

**This route did not exist and no task created it.** The table above assumed it, SC-001
named "read by id" as one of four verbs, and FR-003 said "every read" — three artifacts
resting on a handler that was never written. It is FR-003a now.

### `POST /v1/channels/:channelId/members/remove`

**Bulk, mirroring add.** FR-006 says up to 100 in one request and FR-007 says the result is
reported per user — which is chapter 3.13's `POST /v1/channels/:channelId/members` shape in
both halves. This contract specified a single-user `DELETE …/members/:userExternalId` for ten
analysis passes, having read "the shape chapter 3.13 chose" as *named outcomes* and dropped
*up to 100*. Pass ten found it by comparing US2's scenarios to the route.

Body: `{"users": ["u_dong", "u_ana", …]}`, at most 100.

| Outcome | Status | Body |
|---|---|---|
| all entries processed | 200 | `{"results": [{"user": "u_dong", "result": "removed"}, …]}` |
| 101 entries | 400 | `invalid_request`, `field: "users"` |
| no such channel, or a private one the caller cannot see | 404 | the not-found envelope |

Per-user results, one per entry, in request order:

| Per-user result | Meaning |
|---|---|
| `removed` | was a member, now is not |
| `not_a_member` | was not a member, or no such user in this tenant |

**An action-style `POST` rather than `DELETE` with a body.** A body on `DELETE` is legal and
unreliable — proxies and some clients drop it — and this feature already sets the
action-style precedent with `POST …/archive` and `POST …/ban`. The singular route is gone
rather than kept beside it: "up to 100" covers one, and two routes for one job is two
classification entries, two tests and two chances to disagree.

**A user that does not exist reports `not_a_member`, not an error.** A user that does not
exist is not a member, and answering anything else would make this route a membership oracle
for user ids. It is the same answer a real non-member gets, which is the property the row
exists to hold.

**Removal deletes the member row and the read position, and no messages** (FR-008). The
removed user's existing messages stay in history attributed to them (SC-005), and their
socket stops receiving the channel on its next resume.

### `POST /v1/channels/:channelId/members` — the add body accepts a role

Chapter 3.13 built this route: up to 100 users, one result per entry. This feature adds an
optional `role` per entry, defaulting to `member` (FR-011).

    {"users": [{"user": "u_dong", "role": "owner"}, {"user": "u_ana"}]}

| Outcome | Status |
|---|---|
| added, with the role given or the default | 200, per-entry results |
| a role outside the three | 400 `invalid_request`, `field: "users.0.role"` |

**Why the add endpoint and not only `PATCH`.** US6's first scenario is a member *added with*
a role, and the plan had add assign the default and a separate route change it — two calls to
express one intention, and a window where the member holds a role the customer did not choose.
Found by analysis pass eleven comparing the scenario to the routes.

### `PATCH /v1/channels/:externalId/members/:userExternalId`

Sets a member's role.

| Outcome | Status | Body |
|---|---|---|
| role set | 200 | the member, with `role` |
| a role outside the three | 400 | `invalid_request`, `field: "role"` |
| not a member | 404 | the not-found envelope |
| no such channel, or invisible | 404 | the not-found envelope |

The 400 names the field, which is only true because chapter 3.14 fixed
`ZodValidationPipe` to carry `issues[0].path`. A fourth role value refused with a
`field` is SC-009's second half.

### `POST /v1/channels/:externalId/archive` and `DELETE …/archive`

Sets and clears `archived_at`. Both idempotent: archiving an archived channel is 200
and changes nothing.

| Outcome | Status |
|---|---|
| archived, or already archived | 200 |
| unarchived, or already active | 200 |
| no such channel, or invisible | 404 |

### `POST /v1/channels/:externalId/join`

The user-initiated half of FR-CHN-03. Requires a user credential, not a tenant one —
this is the caller joining, not the tenant adding someone.

| Outcome | Status |
|---|---|
| joined | 200 |
| already a member | 200 |
| the channel is `private` | 404 — indistinguishable from absent |
| the channel does not exist | 404 |
| the channel holds 1,000 members | 403 `channel_member_limit_exceeded` |

The member ceiling is chapter 3.13's, and it is read here rather than reimplemented.

### `POST /v1/channels` — the enum widens

`type` accepts `"public"` and `"private"`. FR-009 gates it: the widening lands in the
same phase as the enforcement, not before. FR-010 settles the repeat: a second creation
naming a different type returns the existing channel and does not change its type.

## Where the check lives

In `repository.sendMessage`, gated on the presence of `userId` — not in a controller,
and not in a service.

The signature already encodes the distinction the check needs.
`sendMessage(…, userId?: string)` means "a user is acting" when `userId` is present and
"the tenant is acting" when it is not, so the gate is the parameter and not a new flag.
**Three call sites, and the one that mattered supplied nothing.** `repo.sendMessage` is
called from `messages.service.ts:47`; `MessagesService.send` from `messages.controller.ts:40`
— the public route — and `internal.controller.ts:65`. The public route passed no user and
`MessagesController` declares no `@Accepts`, so a user token was accepted and the
`userId`-gated check never fired there. This paragraph said "six callers inherit the check"
until analysis pass seven counted them, and the number was the hole's hiding place.

The decision stands: constitution I is explicit that isolation is enforced in data access,
not in handlers, and a caller that wanted to skip the check would have to drop the user,
which is visible in review. What the check needs is callers that say who is acting — T031a
and T041a.

`POST /internal/messages` resolves a user and then sends, so it inherits the check too.
That is the route chapter 3.12 recorded as checking nothing.

## What the cross-tenant suite gains

The suite's four attack shapes all take **another tenant's** identifiers. A user of the
caller's own tenant who is not a member of the channel is a fixture the suite does not
have (R10), so it is new work: one environment, two users, one channel, one of them not
a member.

One attack per verb in the table above, and FR-035's harder gate on top — each must
fail when its check is removed. A test that passes both with and without the code it
covers is measuring nothing, which is the lesson chapter 3.13 recorded when it found
that adding a table to the guard's array is not the same as the guard watching it.
