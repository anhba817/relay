# Data model — chapter 3.17

Two columns, two constraints, one migration. No new table.

---

## `users` — two columns

| Column | Type | Null | Default | Meaning |
|---|---|---|---|---|
| `kind` | `text` | no | `'person'` | What this row represents. `'person'` or `'bot'`. |
| `description` | `text` | yes | — | What the software is and what it posts. Required for a bot, by constraint. |

### Constraints

```sql
CONSTRAINT users_kind_check CHECK (kind IN ('person','bot'))
CONSTRAINT users_bot_description_check CHECK (kind <> 'bot' OR description IS NOT NULL)
```

**The second one is the requirement, not a nicety.** "Force the tenant to create a bot with a
description" is enforced by the database, so a bot without one is unrepresentable rather than
merely refused by validation. A constraint the database can hold, it holds — the same rule
that gave `members.role` its own CHECK in chapter 3.15 instead of trusting the enum above it.

**`description` is bounded at 500 characters in the schema layer** — zod, not a database
constraint — which FR-002 now states, because the layer decides the failure's shape: a bound
zod holds fails the whole batch with an indexed field path, while a rule only the row can
answer is reported per entry. It
answers "what is this and why did it message me" for a person reading a conversation:
`display_name` is 255 and this needs more, `metadata` is 4 KB and this is not a document.

**A person's description is null and that is legal.** Whether people may carry one is left
open: nothing asks for it, and a column both kinds use is harder to withdraw than one only
bots use.

### The existing rows

`kind` defaults to `'person'`, so every row in every environment becomes a person on migration
with no backfill and no rewrite — `ADD COLUMN … NOT NULL DEFAULT` is metadata on Postgres 11
and later, which chapter 3.16 measured when it added `last_activity_at`.

**That default is a decision.** It says every user that existed before this chapter is a
person, which is true: nothing could have created anything else.

## `messages` — no column changes, one guarantee changed

`user_id` stays **nullable**, because rows with null exist and this chapter does not rewrite
history. What changes is that **nothing may create another one**: `repository.sendMessage`'s
`userId` parameter becomes required, so a senderless write is a compile error rather than a
runtime possibility.

**The nullable column and the required parameter say two different things, on purpose.** The
column says "this state exists in stored data". The parameter says "this state cannot be
produced". A chapter that made the column `NOT NULL` would have to decide what to do with the
rows that are already there, and deleting a customer's messages to satisfy a constraint is not
a migration anyone should write.

## State transitions

    a row is created                    kind = 'person'  (implicit creation, FR-USR-02)
    a row is created by upsert          kind as given, 'person' IF ABSENT
    an existing row is upserted,
      kind absent                       no change requested — the default does NOT apply
      kind equals the stored kind       no change
      kind differs                      refused, per-entry status `kind_conflict`

**The default applies only on creation**, and that sentence is load-bearing. Apply it on update
too and an upsert that omits `kind` while editing a bot's description reads as a demotion to
person — making a bot uneditable through the route FR-004 says can edit it. Absent is not
`'person'`; it is the absence of a request, which is the distinction chapters 3.15 and 3.16
built into the profile patch and `exactOptionalPropertyTypes` exists to hold.

**The refusal in both directions matters.** Person → bot silently revokes the ability to
authenticate for an identifier a customer's users may already hold tokens for. Bot → person
hands out a credential for an identity that was never meant to have one.

## What is keyed on a user, and therefore inherits this

Every one of these is keyed on `users.id` and needs no change to accept a bot — which is the
argument in R2 for not building a `bots` table, stated as a list so the next reader can check
it:

    members.user_id                 a bot can be a channel member, with a role
    read_positions.user_id          a bot has a read position, though nothing reads as it
    messages.user_id                a bot's messages survive its deletion (FR-USR-05)
    usage_active_users.user_id      a bot that sends counts toward active users
    users.banned_at                 a bot can be banned
    users.deleted_at                a bot can be deleted — see the constraint below

**`read_positions` is the one worth a second look.** A bot never reads, so its position is
written by nothing and read by nothing. That is not a new dead column — it is the existing
table holding a row that will never be created, which costs nothing. The chapter states it so
a reader does not go looking for the bot's unread count.

## Deletion meets the CHECK, and one reading makes a bot undeletable

`deleteUser` clears `display_name`, `avatar_url` and `metadata`. **`description` is deliberately
not on that list** (FR-004a): clearing it on a bot violates
`users_bot_description_check`, and the UPDATE would be rejected — so a bot could not be deleted
at all.

Both halves are correct on their own. The constraint says a bot always has a description; the
deletion says profile data is cleared. They only conflict if `description` is profile data, and
it is not: it describes what the software *was*, and a deleted bot's messages remain attributed
to it (FR-USR-05), so a reader asking "what was this thing that posted in March" still needs it.

**The rejected alternative** is clearing `kind` back to `'person'` before nulling the
description. That makes the deletion two writes and leaves a person nobody created, holding
messages a bot sent.

**`usage_active_users` is the one worth a decision, and it turned out to be two.** Today a bot
that sends is counted as an active user, and active users are a billing dimension (FR-TEN-08,
chapter 3.10). But `sendMessage` reads that counter **twice**: once at
`repository.ts:3874` to insert the usage row, and again around `repository.ts:4042` to compare a
`count(*)` against `caps.active_users.hard` and throw `QuotaExceededError`. The second read
refuses the send. So the counter is a bill *and* a ceiling, and a bot inherits both by default —
which means a tenant's own software can consume the last slot and their next human to post this
period is refused.

FR-018/018a/018b answer the two separately: **billed, exempt from the ceiling.** The insert at
3874 still runs for a bot; the ceiling at 4042 must neither refuse a bot nor count one. The
second half is the load-bearing one — a bot whose own send is exempted but whose row still lands
in the `count(*)` displaces a person exactly as before, and the test that catches the difference
is the one where a *person* sends after the bot (SC-011).
