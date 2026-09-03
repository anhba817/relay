# Data model — chapter 3.23

## `messages` — two columns that exist and have never been written

    id, channel_id, environment_id, seq, user_id
    text            TEXT          NULL ⇒ tombstone      already nullable
    attachments     JSONB         NULL after a deletion  already nullable
    created_at      TIMESTAMPTZ   never changed by either operation
    edited_at       TIMESTAMPTZ   NULL until the first edit      EXISTS, unwritten
    deleted_at      TIMESTAMPTZ   NULL until deletion            EXISTS, unwritten
    metadata        JSONB         carries the deletion's actor   EXISTS, NOT NULL '{}'

    metadata.deleted_by = { "kind": "user", "user": "<external id>" }
    metadata.deleted_by = { "kind": "application" }

**One key, two shapes, and the boundary with FR-MOD-03 is deliberate.** The kind is always
recorded; the external id only exists for a user principal, because an application principal
has no user of its own (`messages.controller.ts:43`). **Which credential** an application
deletion used is not recorded here — that is an audit log's job, with a request id and a
retention period, and chapter 3.23's `gaps.md` item 2 draws the line.

**This chapter is `messages.metadata`'s first writer.** `grep` finds nothing that writes it
today, so every row carries the `'{}'` default — the mirror of this feature's other theme,
where three read paths had no writer and this column has neither.

**`metadata` is where the deletion's actor goes, and it needs no migration.** FR-MSG-08 asks
the tombstone to retain *"sequence number, author, timestamps, and deletion metadata"*, and
with timestamps itemised separately the last item has to mean more than `deleted_at`. A tenant
API key may delete anybody's message, so who removed it is a different fact from who wrote it —
and the column that holds it has been there, `NOT NULL DEFAULT '{}'`, since the first draft.

**No migration adds a column to this table.** Chapter 3.15's suite plants a tombstone with
raw SQL precisely because the columns are there and nothing writes them — the comment calls
it *"a live reader with no writer"*.

## `message_edits` — the one new table, published before it is built

`docs/05-sad.md:435` gives the DDL and `schema.ts:26` names it as a deliberate absence with
an arrival date. Its shape is the SAD's, not this chapter's:

    id          UUID PRIMARY KEY
    message_id  UUID NOT NULL → messages(id)
    prior_text  TEXT NOT NULL        -- FR-MSG-07: what the message said before
    edited_at   TIMESTAMPTZ NOT NULL

**Append only.** Nothing updates or deletes a row here; FR-004 says so and a later edit adds
a row rather than touching one.

**`prior_text` is NOT NULL, and that is a constraint with a consequence**: a deletion cannot
write an edit-history row, because a tombstone has no text to preserve. The two operations
touch different tables, which is why FR-010 refuses an edit on a deleted message rather than
trying to define what its history would say.

## The message's life, and which transitions this chapter adds

    (nothing)  --send-->  live  --edit-->  live'      seq unchanged, edited_at set,
                            |                          one message_edits row appended
                            |
                            +--delete-->  tombstone   text NULL, attachments NULL,
                            |                          deleted_at set, seq kept
                            |
    tombstone --delete-->  tombstone                  no change, no event  (FR-009)
    tombstone --edit---->  REFUSED                                          (FR-010)

**Every transition keeps the sequence number.** That is what makes a tombstone leave no gap
and what makes an edit invisible to a cursor — one property with two consequences, and this
chapter meets both of them.

## What each read path sees, per state

| State | REST history | Resume backfill | Listing preview |
|---|---|---|---|
| live | the message | the message | text and sequence |
| edited | **current** text | **current** text if newer than the cursor; nothing if older | current text |
| tombstone | the row, `text: null` | **dropped**; no gap appears | `text: null`, still counted as one unread |

**A fourth behaviour sits beside this table and is not a column of it**: the backfill's
`truncated` flag is computed from rows read rather than frames delivered, so a tombstone-heavy
page returns fewer frames and still reports itself truncated. It is not a per-state answer,
which is why it did not appear here — and why FR-017 asks for the statement to be derived
from the code rather than from this table.

**The middle column's second half is the cost of the spec's resume decision** and the only
place a client can hold something untrue. The right-hand column is chapter 3.15's, already
tested against a hand-planted tombstone; the left-hand column is tested by nothing, which is
research R5 and the first thing this chapter builds.

## Derived values that must not move

- **`channels.last_activity_at`** — neither route touches it, so an edit or a deletion does
  not re-order the channel listing (FR-015).
- **The unread count** — derived from sequence numbers, so a tombstone still counts as one.
  Chapter 3.15 decided that and tested it; this chapter's writer is what makes it reachable.
- **`seq`** — assigned at creation, never reassigned.
