# Data model — chapter 4.21, "Erasure, and every path it must find"

No new table and no new column. What this chapter adds is a traversal, and the
model worth writing down is **which stores name a user and what each one can
do about it**.

## The seven places a user is named, and the four answers

| store | how it names a user | rows | what erasure can do |
|---|---|---|---|
| `users` | the row itself | 192,641 | **delete the row** |
| `members` | `user_id`, FK `NO ACTION` | 172,965 | **delete the rows** |
| `read_positions` | `user_id`, FK `NO ACTION` | — | **delete the rows** |
| `messages` | `user_id`, FK `NO ACTION` | 205,628 naming a user | **decision** — see below |
| `media_objects` | `user_id`, nullable | 3,979 named · **11,050 null** | **delete the attributed ones** |
| `usage_active_users` | `user_id`, FK `NO ACTION` | 22,150 · 22,147 users | **decision** — money on one side |
| `connection_events` (CH) | `environment_id` **and** `user_external_id` | 1,081 | **lightweight `DELETE`, both predicates** |
| `daily_usage_*` (CH) | `active_users_state` | 880 | **nothing. no subtract exists** |
| `api_requests` (CH) | — | 205,697 | **nothing to do, by design** |
| `message_events` (CH) | `user_id` | **0** | nothing to do, by defect |

**ALL FIVE FOREIGN KEYS TO `users` ARE `NO ACTION`**, measured. Nothing cascades
and nothing nulls, so deleting the row is refused until every child is gone —
which makes the traversal order a correctness property rather than a
preference.

## The order, and the one place it matters

```
resolve the external id WITHIN the caller's environment   -> user_id, or 404
collect the user's media_ids BEFORE anything is deleted   (they vanish with the rows)
delete read_positions, members                             children first
decide messages           FR-MOD-04 says erase · FR-USR-05 says keep
decide usage_active_users FR-MOD-04 says erase · FR-029 says keep, for billing
delete the attributed media objects                        + renditions + bytes
delete the users row                                       only now will the FKs allow it
ClickHouse: DELETE FROM connection_events
              WHERE environment_id = … AND user_external_id = …
            BOTH PREDICATES. External ids are unique PER ENVIRONMENT and the
            id alone deletes other tenants' rows — measured below.
            And the external id is gone from Postgres by now — carry it
the sketches                                               report, do not attempt
```

**SCOPE EVERY ANALYTICAL STATEMENT BY `environment_id`, AND THE NUMBERS ARE WHY.**
`connection_events` carries an `environment_id UUID` column, and external ids are unique
per environment rather than globally — which is true of the whole platform: **1,576
external ids are reused across environments in `users`.** In that table, **23 of 54
distinct external ids span more than one environment**, giving 460 `(env, id)` pairs from
54 ids.

Measured on the worst of them:

    tuan              111 environments · 156 rows
      correct for one tenant                    4
      WRONGLY DELETED from 110 others         152      97.4%

**AN UNSCOPED DELETE IS NOT A NEAR MISS HERE, IT IS MOSTLY WRONG.** FR-008 requires the
scope and the spec's own Edge Cases name this exact collision; a first draft of this
sketch wrote the statement without it anyway, sixty lines below the requirement.

**AND THE REASON IS STRUCTURAL RATHER THAN CARELESS.** Every other store in the traversal
is reached through `Repository`, whose constructor requires an `environment_id`
(constitution I), so six of the seven are scoped by construction and nobody has to
remember. **ClickHouse is the only store that class does not mediate, and it is the only
one the first draft got wrong.** The function that does it takes `environmentId` as a
parameter for that reason — the signature carrying what the constructor would have.

**CARRY THE EXTERNAL ID FORWARD.** The analytical table keys on
`user_external_id` and the Postgres row that holds it is deleted earlier in the
same traversal. Read it first or the last step has nothing to match on — which
is the same ordering trap chapter 4.20 hit with `media_id` values that vanish
with the messages that named them.

## The two decisions this model does not take

**`messages`.** FR-MOD-04 says erasure removes messages. FR-USR-05 says
deletion preserves them *"unless message deletion is explicitly requested"* —
and FR-MOD-04 is arguably that request. Against: a channel's history losing
every message one participant sent is visible to everyone else in it, and
`deleteUser`'s comment records that *"authored by a deleted user" and "authored
by nobody" are different states.* Phase 2 decides; the argument goes in
`baseline.txt` either way.

**`usage_active_users`.** `deleteUser` keeps it on purpose: *"billing history
does not vanish with a profile — a customer who deleted a user in March still
owes for March."* FR-MOD-04 calls it an analytical record and requires its
erasure. **This is the strongest counter-argument in the platform to the
clause's own wording**, and it is 22,150 rows.

## What this model does NOT change

- **`audit_log`.** Append-only under ADR-35, narrowed once already by chapter
  4.20. 1,324 rows name a user target and an entry recording that somebody was
  banned is itself a record of that person. Stated, not repaired — and an
  erasure writes a NEW entry (FR-013), which is the opposite direction.
- **The object key layout.** DR-15's `{environment_id}/{media_id}` is
  tenant-prefixed and supports tenant erasure by prefix. **A user's objects are
  not a prefix** and never were; the clause does not claim they are.
- **Any foreign key's delete action.** `NO ACTION` on all five is the design
  FR-USR-05 chose with a measurement behind it, and a cascade here would make
  the traversal invisible rather than ordered.
