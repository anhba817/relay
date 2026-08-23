# Contract — the listing, the unread count, and the user surface

Chapter 3.16's routes. Same obligation as `membership.md`: a documented status code per
route (FR-039).

**And the same note about paths**: they are written with the customer's external id in
place, while the router names channel parameters `:channelId`. A classification entry
copied from this file verbatim will not match a derived target.

## `GET /v1/users/:externalId/channels`

A user's channels, most recently active first, cursor-paginated.

```json
{
  "data": [
    {
      "id": "c_support",
      "type": "public",
      "name": "Support",
      "role": "member",
      "unread": 12,
      "last_activity_at": "2026-08-23T10:14:02.113Z",
      "last_message": {
        "sequence": 8814,
        "text": "we shipped it",
        "user": { "id": "u_dong" },
        "created_at": "2026-08-23T10:14:02.113Z"
      }
    }
  ],
  "next_cursor": "eyJhIjoiMjAyNi0wOC0yM1QxMDoxNDowMi4xMTNaIiwiaWQiOiIu…"
}
```

| Field | Source |
|---|---|
| `unread` | `greatest(channels.last_sequence − read_position, 0)` for **the user the path names**, not the caller — the caller is the tenant |
| `last_activity_at` | `channels.last_activity_at` |
| `last_message` | the row at `channels.last_sequence`, or `null` if the channel has none — **including when that row is a tombstone**, which reports its sequence, author and `created_at` with `text: null` (FR-019) |
| `role` | `members.role` |

| Outcome | Status |
|---|---|
| listed, including an empty list | 200 |
| no such user in the tenant | 404 |
| a malformed or foreign cursor | 400 `invalid_request`, `field: "cursor"` |
| `limit` over 100 | 400 `invalid_request`, `field: "limit"` — FR-013's bound, the same 100 as the member-add and upsert bounds |

**Only channels the user is a member of** (FR-015). A public channel the user could read
by id does not appear, which is the read set and the subscription set kept apart —
`membership.md` has the table. An archived channel does appear, with a flag, because a
customer who archived a channel still needs to find it; FR-022 requires the chapter to
say so out loud.

### The cursor

Keyset on `(last_activity_at desc, id desc)`, base64 of the JSON pair, opaque to the
client. Not an offset: an offset page shifts under a client whenever a channel becomes
active, which for this ordering is constantly.

`id` is in the key because `last_activity_at` is not unique — two channels can take a
message in the same millisecond, and a keyset on a non-unique column skips or repeats
rows at the page boundary.

A cursor naming a channel in another environment is a 400, not a 404 and not an empty
page. It is a malformed cursor from this tenant's point of view, and answering anything
that distinguishes "exists elsewhere" from "malformed" is the leak the whole isolation
suite exists to catch.

### The unread count, and what it approximates

`greatest(last_sequence − read_position, 0)`, with no counter anywhere.

`channels.last_sequence` is already the sequencing authority — chapter 2.2 made it one —
and the write path maintains it. So the count has nothing to invalidate and nothing to
backfill. Measured for one page of 50 channels against 1,000,000 messages: counting
rows past the position is 9.8–13.4 ms, a cached counter on the position is 1.2–2.1 ms,
and the subtraction is 1.1–4.5 ms. The cached counter is no faster and adds a value
that can go stale.

**A tombstoned last message is still the last message.** `last_message` reports it with
`text: null` rather than walking back to the last row that still has text — that walk-back is
a second query per channel, and it would disagree with the unread count, which counts the
tombstone because the sequence is kept. One rule for both fields (FR-019). A client that wants
a preview renders "message deleted" from the null.

**The approximation, which FR-016 requires be stated: a deleted message still counts as
one unread.** A tombstone keeps its sequence, so it keeps its place in the arithmetic.
Counting rows instead would make a deleted message stop being unread, at 10× the cost
on the query a client runs to render its first screen.

`greatest(…, 0)` and not the bare subtraction, because a read position can only be
refused past `last_sequence` at the moment it is written — and `last_sequence` never
goes backwards, so the clamp is defence against a bug rather than a case that can
happen. It costs nothing and turns a negative count into zero instead of into a client
bug report.

## `PUT /v1/users/:externalId/channels/:channelExternalId/read`

Records a read position. Body `{"sequence": 8814}`.

| Outcome | Status |
|---|---|
| position advanced | 200 |
| the sequence is at or below the stored position | 200, unchanged |
| the sequence is past `channels.last_sequence` | 400 `invalid_request`, `field: "sequence"` |
| **the path's user** is not a member | 403 `not_a_member`, or 404 if the channel is private |
| no such channel or user | 404 |

Forwards only, and a replayed acknowledgement is a no-op rather than a rewind
(FR-017). A position past the channel's end is refused because the count derived from
it would be wrong for every message that arrives afterwards (FR-018).

## `GET` and `PATCH /v1/users/:externalId`

The profile: `display_name`, `avatar_url`, `metadata`.

| Outcome | Status |
|---|---|
| read, or updated | 200 |
| metadata over 4 KB | 400 `invalid_request`, `field: "metadata"` |
| a malformed `avatar_url` | 400 `invalid_request`, `field: "avatar_url"` |
| no such user, or a deleted one | 404 |

Two of the three fields have never been written by any route. The 4 KB bound is the
users bound and is half the channels bound of 8 KB, which is a difference the chapter
has to justify or change rather than inherit silently.

## `POST /v1/users`

Upsert up to 100 users in one request. An entry naming an existing user updates it
rather than failing (FR-026), on chapter 3.13's idempotent `createUser`.

| Outcome | Status |
|---|---|
| all entries upserted | 200, with a per-entry result array |
| 101 entries | 400 `invalid_request`, `field: "users"` |
| an entry fails validation | 400, the field path naming the index — `users.7.metadata` |

The per-entry result array is chapter 3.13's shape for `addMember`, reused: a partial
outcome is reported per entry rather than collapsed into one status code. The bound of
100 is the same as the member-add bound, and the same number for the same reason.

## `DELETE /v1/users/:externalId`

| Outcome | Status |
|---|---|
| deleted | 200 |
| already deleted | 200 |
| no such user | 404 |

Clears the profile fields, deletes the memberships and read positions, keeps the row
with `deleted_at` set. `data-model.md` has the argument; the short version is that
`ON DELETE SET NULL` would make the user's messages undeliverable, because
`backfill.controller`'s `toFrame` drops senderless rows.

`usage_active_users` is untouched (FR-029) — billing history does not vanish with a
profile.

Presenting the same external id afterwards reuses the row and clears `deleted_at`
(FR-030). `(environment_id, external_id)` is unique and the row is still there, so
there is no other honest answer.

## `POST` and `DELETE /v1/users/:externalId/ban`

| Outcome | Status |
|---|---|
| banned, or already banned | 200 |
| unbanned, or not banned | 200 |
| no such user | 404 |

A ban is tenant-scope: the user cannot connect and cannot send anywhere in the
environment. Their history stays readable by others, and their messages stay attributed
to them (SC-013).

FR-032 requires the chapter to state what happens to a socket that is **already open**.
The two answers are "closed at the next heartbeat" and "closed immediately by the
gateway", and they differ in whether the gateway has to be told. Whichever the chapter
takes, it takes explicitly, because a ban that only applies to new connections is a ban
a client can outlast by not reconnecting.

## `POST /auth/dev-token` — implicit creation

The token route creates the user if absent (FR-039a), on chapter 3.13's idempotent
`createUser`.

This closes a sequence that currently fails in a way that names the wrong thing: mint a
token for an identifier no user record exists for, send a message, and
`POST /internal/messages` answers `400 "unknown user"` — a message that describes the
caller rather than the cause. FR-039b requires the chapter to state whether
authentication and membership converge on one row, and they do: one external identifier
is one `users` row, whichever path reached it first.

| Outcome | Status |
|---|---|
| token minted, user existed | 200 |
| token minted, user created | 200 |

The status does not distinguish them, deliberately. A caller minting a token does not
need to know whether it was the first one, and a status that told them would be a
membership oracle for external ids.
