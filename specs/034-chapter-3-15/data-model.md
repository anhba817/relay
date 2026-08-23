# Data model — chapters 3.15 and 3.16

One new table, three new columns, and five columns that already exist and are read by
nothing. Every shape below was checked against `services/api/src/db/schema.ts` rather
than against the SAD, because the schema is the thing the migration has to agree with.

## Two words one letter apart, and which table each means

**`members` is the channel table** — `(channel_id, user_id, joined_at)`, and this document
says "membership" for a row in it. **`memberships` is the organisation table** — a human's
role in an account, FR-TEN-07. They are different subjects at different levels of the
hierarchy, and the only reason to state it here is that both gain nothing from this
feature except a role column each, with vocabularies one word apart (R8). Where this
document needs to be unambiguous it names the table.

## What exists and is dead

Five columns, and the count is this feature's own headline number (SC-016). It is
measured before Phase 2 moves anything, because a count taken after an edit measures
the edit.

| Column | Declared in | Written by | Read by |
|---|---|---|---|
| `channels.type` | chapter 2.1, `CHECK (type IN ('public','private'))` | `POST /v1/channels`, always `'public'` | nothing |
| `channels.archived_at` | chapter 2.1 | nothing | nothing |
| `users.avatar_url` | chapter 3.1 | nothing | nothing |
| `users.metadata` | chapter 3.1 | nothing | nothing |
| `users.banned_at` | chapter 3.1 | nothing | nothing |

`users.display_name` is the sixth of that family and is not on the list: chapter 3.13's
`createUser` writes it. It is written and not read, which is a different state and the
one FR-035 exists to distinguish — being written is not being read.

## New: `read_positions`

The only entity in this feature with no storage today. Verified absent: no `last_read`,
`read_at`, or equivalent column in any table.

| Column | Type | Notes |
|---|---|---|
| `environment_id` | `uuid not null` → `environments.id` | for the guard, not for the query — see below |
| `channel_id` | `uuid not null` → `channels.id` | |
| `user_id` | `uuid not null` → `users.id` | |
| `sequence` | `bigint not null` | the last sequence this user has read |
| `updated_at` | `timestamptz not null default now()` | |

Primary key `(channel_id, user_id)`. No `id` column, which is the detail R15 flags: the
guard's refusal message interpolates a key, and chapter 3.13 installed
`coalesce(to_jsonb(OLD) ->> 'id', to_jsonb(OLD)::text)` for exactly this case.

**`environment_id` is denormalised here and that is deliberate.** `channel_id` already
determines it. The column exists because feature 030's guard watches tables that carry
one, and a table without it is a table the guard cannot refuse a cross-environment
delete on. `members` is the counter-example and the reason the point is worth making:
it has no `environment_id`, so `tenant-scope.itest.ts` classifies it as `hop` — reached
through a foreign key — and no trigger protects it. A read position is per-user state
that a tenant's own operations mutate, so it takes the stronger classification.

**Rules**

- A position advances forwards only. A write naming a lower sequence than the stored
  one is accepted and changes nothing, so a client that replays an old acknowledgement
  cannot move a user's unread count backwards.
- A position beyond `channels.last_sequence` is refused (FR-018). A position nothing
  can reach makes every later count wrong, and the count is `last_sequence − position`.
- No row means position zero. Nothing is seeded on membership, so a new member's
  unread count is the channel's entire history.

## New: `channels.last_activity_at`

`timestamptz not null default now()`, with `index (environment_id, last_activity_at desc)`.

Set to the message's `created_at` by the same statement that advances
`channels.last_sequence`, which is already a transaction the write path runs. Nothing
else writes it — a member joining or a name changing is not activity.

**Why a column and not the aggregate**, at 2,000 channels and 1,000,000 messages: the
aggregate over `messages.created_at` is 159 ms with a sequential scan over every
message in the environment on every listing; the indexed column is 1.1 ms. 145× apart,
and the gap grows with the one number a chat platform guarantees will grow. The test
lane's largest environment holds 579 messages and answered the aggregate in 0.87 ms,
which is why R4 records the measurement that pointed the wrong way beside the one that
decided it.

`last_sequence` cannot do this job at all. It is a per-channel counter, so two channels
both at sequence 50 say nothing about which was active more recently.

## New: `members.role`

`text not null default 'member'`, with
`CHECK (role IN ('owner','moderator','member'))`.

**Its own CHECK, and not the one that already exists.** `memberships.role` — a human's
role in an organisation, FR-TEN-07 — is
`CHECK (role IN ('owner','admin','member'))`. Different table, different subject, one
word different. A migration that reused the organisation constraint would accept
`admin` on a channel member and refuse `moderator`, and it would look correct in
review. Each constraint gets a comment naming the other.

The default is `'member'`, which makes chapter 3.13's `addMember` continue to work
unchanged and gives every existing row a value the CHECK accepts.

FR-012 asks the harder question: does anything read it? The answer the chapter has to
state is that nothing does yet — no operation is authorized by channel role in this
feature — and a role column nothing reads is this feature's own subject repeated, so
the statement is a requirement rather than a footnote.

## New: `users.deleted_at`

`timestamptz`, null by default. **Designing the deletion path is what turned this up**
— R7 decided that a deleted user keeps their row, and there was nowhere to record that
the row is deleted.

It carries one more obligation than a marker usually does: every read of a user has to
decide whether a deleted user is visible to it. The answer this feature takes is that
a deleted user is absent from the profile route and from listings, and present wherever
a message's author is resolved, because that is the whole point of keeping the row.

## Changed: `channels.type` becomes readable

The column and its CHECK have been in place since chapter 2.1. What changes is that
two verbs branch on it.

| | `public` | `private` |
|---|---|---|
| read by id | any user of the tenant | members only |
| history | any user of the tenant | members only |
| send | any user of the tenant | members only |
| subscribed on the socket | members only | members only |
| join | any user of the tenant | not by the user; added by the tenant |

**The subscription set is not the read set**, and keeping them apart is what makes a
public channel affordable. Auto-subscribing every tenant user to every public channel
makes a session unbounded in a tenant with many channels, and delivers channels a user
never asked for.

`POST /v1/channels` accepts `private` only once the three read paths and the send path
enforce it (FR-009). The order matters: the enum widened first would sell a guarantee
the platform does not keep, which is the mistake chapter 3.12's fifth analysis pass
caught one phase before it shipped.

## Changed: a deleted user keeps their row

Three tables reference `users.id`: `messages`, `members`, `usage_active_users`.

| | Action on delete |
|---|---|
| `users` row | kept, with `deleted_at` set and `display_name`, `avatar_url`, `metadata` cleared |
| `members` rows | deleted |
| `messages` rows | untouched, `user_id` intact |
| `usage_active_users` rows | untouched — billing history (FR-029) |
| `read_positions` rows | deleted with the memberships |

**`ON DELETE SET NULL` would satisfy the letter of "messages are preserved" and break
delivery.** `backfill.controller`'s `toFrame` drops senderless rows because
`messageSchema` requires `user`, so a NULL author makes a message invisible to sockets.
"Authored by a deleted user" and "authored by nobody" are different states and only the
first is what FR-USR-05 asks for.

`ON DELETE CASCADE` deletes the messages the clause says to keep. A separate
`deleted_users` table is a second identity space for one flag.

FR-030 asks what happens when a deleted user's external id is presented again. The
answer this feature has to state, because `(environment_id, external_id)` is unique and
the row is still there: the same row is reused, undeleted, with empty profile fields.

## State transitions

**Channel type** — `public → private` and back, by a creation naming a type. FR-010
settles the interesting case: a repeated creation naming a *different* type does not
change the existing channel, because idempotency means the second call returns the
first call's channel and a type change is not a creation.

**Channel archive** — `active → archived` (`archived_at` set) → `active`
(`archived_at` cleared). Sends are refused while archived; history stays readable.
FR-022 requires the chapter to state whether an archived channel still appears in a
listing.

**User ban** — `active → banned` (`banned_at` set) → `active`. A ban prevents
connecting and sending at tenant scope; the user's history stays readable by others
(SC-013). FR-032 requires the chapter to state what a ban does to a connection that is
already open, which is a different question from what it does to a new one.

**User deletion** — `active → deleted` → `active` on re-presentation of the external
id, per FR-030. Not a terminal state, which is the part worth stating.

## Entity relationships, after this feature

```
environments ─┬─< users ─────┬─< members >──┬── channels >── environments
              │              ├─< read_positions >─┤
              │              └─< messages  >──────┤
              └─< channels
```

`members` and `read_positions` both sit between a user and a channel and are reached
differently by the guard: `read_positions` carries `environment_id` and is watched;
`members` does not and is classified `hop`. The asymmetry is worth a sentence in the
chapter, because a reader who adds the third such table will have to choose.
