# Data model — chapter 4.11

This chapter **adds no table and alters no column.** It reads one table the previous chapter
created and writes one it has written since chapter 2.2. What follows is the shape of the read,
the predicate it applies, and the two things the shape cannot express.

---

## 1. What is read: `media_objects`

Created by chapter 4.10's `0015_media_objects.sql`. Unchanged here.

| column | type | what this chapter does with it |
|---|---|---|
| `id` | `uuid` | matched against the attachment's `media_id` |
| `environment_id` | `uuid NOT NULL` | **the tenant predicate** — must equal the sender's environment |
| `user_id` | `uuid NULL` | **the uploader predicate** — see §2; NULL means the tenant uploaded it |
| `filename` | `text NOT NULL` | not read |
| `mime_type` | `text NOT NULL` | not read |
| `declared_bytes` | `bigint NOT NULL` | not read |
| `state` | `text NOT NULL` | **the state predicate** — `pending` or `ready`; `CHECK (state = 'pending')` makes the second unreachable (research R2) |
| `object_key` | `text NOT NULL` | not read |
| `created_at` | `timestamptz NOT NULL` | not read |

Four columns are not read, and that is the point of listing them: this chapter asks whether an
id may be attached, not what it contains. Nothing about the file — its declared type, its size,
its name — takes part in the decision, because nothing has verified any of it.

---

## 2. The predicate, in the order the clause states it

For each media attachment in the message, with `sender` being the environment and, for a user
token, the user the send already resolved:

```text
environment_id = sender.environmentId          — FR-002
AND (sender is an API key
     OR user_id IS NULL                        — the tenant uploaded it (research R1)
     OR user_id = sender.userId)                — FR-003
AND state IN ('pending', 'ready')              — FR-010
```

**A row that does not match and a row that does not exist are the same outcome** (FR-005). The
query returns the ids that pass; anything asked for and not returned is refused, with no way for
the caller to tell which clause it failed or whether the row exists at all.

**The API-key arm is not a hole.** An application credential acts for the tenant, and every media
object in the environment is the tenant's. The user predicate exists because a user token acts for
one person; the clause says so — *"(for user tokens)"*.

---

## 3. What is written: `messages.attachments`

A bare `jsonb` column, the array as sent, in order, with no de-duplication — chapter 3.24's rule,
unchanged: *"the same URL twice is two attachments, because the platform does not compare them."*
The same media id twice is two attachments for the same reason.

The stored element is exactly what the caller sent: `{ "type": "media", "media_id": "…" }`. No
state, no filename, no resolved anything. **A message records which object was attached, not what
that object was at the moment of sending** — which is what lets FR-MED-07 report a state change
later without the message having lied.

---

## 4. Two things this shape cannot express, recorded rather than designed around

**There is no reference count.** Nothing records that a media object is attached to a message, in
either direction — the message names the id and the object knows nothing. FR-MED-10's sweep deletes
*unreferenced* objects 24 hours after a tombstone unlinks them, and the only way to answer
"unreferenced" against this shape is to scan `messages.attachments`. That is a later chapter's
problem and it is created here, so it is written down here.

**There is no ready state to observe.** `state` is `pending` for every row that exists. A message
attaching one is a message attaching a file nobody has checked, which is FR-MED-06's design note —
*"the scan is a delivery gate for bytes, never for the message"* — and a recipient has no way to
learn when that changes until FR-MED-07 ships.

---

## 5. State transitions

None. This chapter reads `state` and never writes it. The transitions FR-MED-07 names —
`pending → ready`, `pending → rejected` — belong to the worker in movement VI, and the database
currently refuses both.
