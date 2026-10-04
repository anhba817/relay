# Data model — chapter 4.20, "The messages that expire"

No new table. One column stops being empty, one constraint changes its delete action, one
trigger gains a named exception. The whole chapter is three lines of DDL and an argument about
each of them.

## `environments.retention_days` — the column that has been there since 2.1

| | |
|---|---|
| type | `integer`, nullable |
| exists since | chapter 2.1, named in SRS §6.1 and SAD §338 |
| read by | nothing, in seventeen chapters |
| set on | **0 of 33,051** environments |

**NULL means indefinite, and that is the clause's own vocabulary.** FR-MOD-06 offers
*30 / 90 / 365 days / indefinite*, so three integers and an absence. A fourth sentinel value
for "indefinite" would be a second way to spell the same state.

**BOUNDED TO THE THREE VALUES BY A CHECK CONSTRAINT.** The clause enumerates them rather than
describing a range, so `retention_days = 45` is not a stricter policy a customer chose — it is
a value nothing in the specification licenses, and a sweep acting on it would be enforcing a
promise nobody made. A check constraint is how the enumeration survives a caller nobody
anticipated.

## `message_edits_message_id_fkey` — `NO ACTION` becomes `ON DELETE CASCADE`

**And by itself this changes nothing**, which is the measurement that shaped the design: a
cascade issues an ordinary `DELETE` against the child table and the append-only trigger fires
on it. Research R1 has the error with the generated statement in it.

The cascade is still right, for a reason independent of expiry: **a version row must not
outlive its message.** Without the cascade the sweep would carry an ordered two-step delete in
application code, and the invariant would live in a procedure rather than in the schema — which
is the distinction chapter 4.15 drew when it gave a rendition's reachability to a composite
foreign key rather than to a predicate somebody maintains.

## `message_edits_append_only` — one named exception

```
IF TG_OP = 'DELETE' AND current_setting('relay.expiring', true) = 'on' THEN RETURN OLD; END IF;
```

Three properties, each measured rather than argued (R1):

| | |
|---|---|
| an `UPDATE` | refused, flag or no flag — immutability of a version's **content** is untouched |
| a `DELETE` with the flag unset | refused |
| a `DELETE` cascaded from an expiring message, flag set | permitted |

**THE FLAG IS `SET LOCAL`, SO ITS LIFETIME IS ONE TRANSACTION.** A session that sets it and then
does something else has the setting for that transaction only, and a connection returned to the
pool carries nothing.

**WHAT THIS COSTS, AND IT IS A PUBLISHED GUARANTEE.** ADR-35 scoped the audit log's
immutability as *to the application and to accident, and not to somebody holding the database
password*. Chapter 4.19 applied that scope to `message_edits`. After this chapter the scope for
this table is **to the application except one named path, and to accident** — and the named
path is auditable in a way `session_replication_role` is not: the condition is in the trigger's
own body, in a migration, inside the fence chain, and it names exactly one verb on one table.

Constitution VII makes an accepted ADR immutable, so this is a **new ADR** superseding ADR-35's
scope clause for this table rather than an amendment to it.

## What a sweep touches, in order

```
for each environment with retention_days set     UNSCOPED, in retention-reads.ts —
                                                 Repository's constructor requires one
                                                 environment and this crosses all of them
                                             ONE QUERY PER ENVIRONMENT below, not one join
  find messages older than the policy        the bound is a CONSTANT here, computed in the
                                             application. As a join filter across all
                                             environments it is 604 buffers and discards every
                                             message in the policied one (`Rows Removed by Join
                                             Filter: 1018`); per environment it is 74 and
                                             reaches channels_environment_last_activity.
                                             Keyset, paged — R7's lesson from 4.13
  collect their media_id values              free: jsonb already on the row
  SET LOCAL relay.expiring = 'on'
  DELETE FROM messages WHERE id = ANY(…)     cascades to message_edits
  for each media_id, is it still referenced? 883 buffers with a bound operand (R2)
    if not, delete the object and its renditions, and the stored bytes
```

**THE ORDER MATTERS IN ONE PLACE.** The reference check runs **after** the messages are gone,
because an object referenced only by expired messages is only unreferenced once they are. Run
it first and every shared-looking object survives.

## What this model does NOT change

- **`messages` itself.** No column, no index, no trigger. Expiry is a `DELETE`, and
  `messages.created_at` already carries the age the policy compares against.
- **`audit_log`.** No foreign key to `messages` exists and none is added: an entry records that
  an action happened, not the thing it happened to. 1,435 rows name a message target today and
  a destroyed message leaves them naming an id that resolves to nothing — stated in the chapter
  rather than repaired, because repairing it means deleting from an append-only log.
- **The analytical store.** Constitution III. DR-09's 90-day TTL on raw events is a different
  clock with a different owner, and an operational expiry does not reach it.
- **Tombstones.** A tombstone is a message and expires like one. Nothing distinguishes them in
  the predicate, which is the answer to "does a deleted message ever expire" being *yes*.
