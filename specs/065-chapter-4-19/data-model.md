# Data model — chapter 4.19

## 1. The version row — `message_edits`, widened

One row per text a message stopped holding. Today that means *per edit*; after this chapter it
also means *per deletion*, which is the one version the table has never carried.

| column | type | null | change | why |
|---|---|---|---|---|
| `message_id` | `uuid` | no | — | unchanged, half the primary key |
| `edited_at` | `timestamptz` | no | — | unchanged. The instant this version stopped being current. **Not renamed** — see below |
| `prior_text` | `text` | no | — | unchanged, and `NOT NULL` is why a deletion could not be recorded here before: the comment read *a tombstone has no text to preserve*, which is true after the deletion and false at the write site |
| `ended_by` | `text` | **no** | **NEW** | `edit` or `deletion`, with a check constraint. The discriminator FR-003 asks for |

**`ended_by` IS REQUIRED, AND THAT IS THE MEASUREMENT RATHER THAN A PREFERENCE.** Chapter 4.14:
*required is what makes the compiler name every construction site*; chapter 4.15 paid the other
side and recorded that an optional field names none and breaks no existing assertion. Here the
compiler's list is **one writer and one reader** — `editMessage` inserts, `listMessageEdits`
selects — so the guarantee costs almost nothing and a default of `'edit'` would make *absent*
and *an edit* the same value in a table whose whole job is to say which happened.

**AND THE INSTANT COLUMN IS NOT RENAMED.** `edited_at` is the wrong word for a deletion row and
renaming it is a breaking change to a published response field, where adding one is not
(CON-05, and chapter 4.8's argument for `has_more`). The row reads `edited_at: …, ended_by:
"deletion"`, which tells a reader two things that disagree — so **the response renames it and
the column does not**: the contract serves `ended_at`, and `data-model.md` §3 is where that
mapping lives rather than in a reader's head.

### The primary key is unchanged, and the claim is asserted rather than assumed

`(message_id, edited_at)` already orders versions, and `editMessage`'s comment says a conflict
there is a loud failure rather than a silent drop. A deletion row is a second writer to that
key, and it **cannot collide with an edit on the same message**: FR-010 of chapter 3.23 refuses
an edit on a tombstone, so every edit precedes every deletion.

Measured on the lane: **4,859 rows, 4,859 distinct keys.** The ordering property is asserted in
a test rather than left as a paragraph, because *cannot collide by construction* is the kind of
claim this project has had to withdraw before.

### And the table becomes append-only

FR-MSG-07 says *"an **immutable** edit history"* and nothing enforces it — measured: no triggers
on `message_edits`, where `audit_log` has `audit_log_append_only` since last chapter. The same
`BEFORE UPDATE OR DELETE` mechanism applies here, with the same scope ADR-35 published: it
refuses the application and refuses accident, and one `SET session_replication_role = replica`
still gets through.

**This is in scope because the chapter's product depends on it.** A recoverable final text in a
table the application can rewrite is worth less than the clause already claims.

**One thing the trigger forbids that the platform may need**: erasure (row 22) must delete a
user's words, and these rows hold them. The trigger refuses that `DELETE`, exactly as the audit
log's does. Row 22 inherits both, and this chapter writes the collision down rather than
pre-solving it.

## 2. The tombstone, unchanged except on the wire

The deleted message's row keeps what FR-MSG-08 names — sequence, author, timestamps, deletion
metadata — and still carries no text. **Nothing about the tombstone changes.** The final text
moves to a version row; it does not stay on the message.

That is the distinction FR-MSG-08 draws and this chapter leans on: *"Hard deletion shall occur
only via the compliance deletion endpoint."* A deletion replaces the content of the row. It was
never licensed to destroy the version, and losing it was a hard deletion of exactly one text
performed by the moderation path.

## 3. What a reader receives

### `GET /v1/channels/{channelId}/messages/{messageId}/edits`

The existing route, serving one more row and one more field per row.

```json
{
  "versions": [
    { "text": "will be edited", "ended_at": "…", "ended_by": "edit" },
    { "text": "edited once",    "ended_at": "…", "ended_by": "edit" },
    { "text": "edited twice",   "ended_at": "…", "ended_by": "deletion" }
  ]
}
```

**THE ARRAY KEY AND THE FIELD NAMES ARE A DECISION WITH A BILL, AND THE PLAN TAKES THE CHEAP
HALF.** `edits` → `versions` and `prior_text` → `text` read better for a list that now includes
a deletion, and both are **breaking changes to a published response** under CON-05. Chapter
4.17 spent a probe on assuming an array key (`messages` against something else) and chapter
4.18 named its key in the contract so the tests and the quickstart could not disagree.

So: **`ended_at` and `ended_by` are added; `prior_text` and `edits` stay.** The shape is

```json
{
  "edits": [
    { "prior_text": "will be edited", "edited_at": "…", "ended_at": "…", "ended_by": "edit" },
    { "prior_text": "edited twice",   "edited_at": "…", "ended_at": "…", "ended_by": "deletion" }
  ]
}
```

and `edited_at` and `ended_at` carry the same value on every row. **A duplicated field is the
price of not breaking a contract**, it is visible, and the plan states it rather than letting a
reader discover two names for one instant. The alternative — rename and version the route — is
recorded in `plan.md`'s complexity table with what it would cost.

### `GET /v1/channels/{channelId}/messages`

One field added to a row that is deleted:

```json
{ "id": "…", "channel_id": "…", "seq": 3, "user": "…", "text": null,
  "created_at": "…", "edited_at": null, "deleted_at": "2026-10-03T00:04:04.509Z" }
```

`null` on a live message. **An addition, not a reshape**, which is the half CON-05 permits.

**And the history row already disagrees with `messageSchema` in three ways** — `channel_id`
against `channel`, an `edited_at` the schema does not declare, and `text: null` against
`z.string()`. Nothing parses one against the other. The plan records the divergence and does
not converge it: a reshape is breaking where this addition is not, and chapter 4.14 measured
what making a field required costs across construction sites.

## 4. State transitions

A version row has one state: written. It is created when a text stops being current and never
changes, which the trigger now enforces rather than the convention.

A message's text has the states it already had — current, replaced, removed — and this chapter
adds no state. What changes is that leaving the last of them now leaves a record.
