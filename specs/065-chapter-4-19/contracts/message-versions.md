# Contract — what a tenant can recover about a message, removed or not

Two existing routes, each gaining fields and neither changing shape. **No new route**: the
premise check found both surfaces already built and already application-credential-scoped
where the clause asks, so this chapter adds to them rather than beside them.

## `GET /v1/channels/{channelId}/messages/{messageId}/edits`

| | |
|---|---|
| credential | **application only** — already enforced, measured: a user token gets **403** |
| ordering | oldest first, by the instant each version ended |
| new | one row per deletion, and two fields on every row |

### The response

```json
{
  "edits": [
    {
      "prior_text": "will be edited",
      "edited_at": "2026-10-03T00:04:13.056Z",
      "ended_at":  "2026-10-03T00:04:13.056Z",
      "ended_by":  "edit"
    },
    {
      "prior_text": "edited twice",
      "edited_at": "2026-10-03T00:04:31.880Z",
      "ended_at":  "2026-10-03T00:04:31.880Z",
      "ended_by":  "deletion"
    }
  ]
}
```

**`edited_at` AND `ended_at` CARRY THE SAME VALUE, AND THAT IS DELIBERATE.** `edited_at` is
published and cannot be removed without a breaking change under CON-05; it is the wrong word
for a deletion row. `ended_at` is the right word and is additive. The duplication is the price
of not versioning a route over a noun, it is one field wide, and it is stated here so nobody
has to work out which of two names to trust. **A client should read `ended_at` and `ended_by`;
`edited_at` is kept for callers written before this chapter.**

Likewise the array stays `edits` where `versions` would read better. Chapter 4.17 spent a probe
on assuming an array key and chapter 4.18 named its key in the contract so the tests and the
quickstart could not disagree — so this one is named too, and it is the old name.

### What is NOT in this list

**The current text of a message that still exists.** Every row here is a text that *stopped*
being current, and a live message's text has not. It comes from the channel's history, which
the caller reading versions has usually already fetched.

So assembling *every text this message has ever held* is **one request for a deleted message
and two for a live one**, and the asymmetry is the shape of the data rather than an oversight:
after a deletion there is no current text, which is the whole of what a deletion is.

### What `ended_by` can be

| value | meaning |
|---|---|
| `edit` | the text was replaced by a later edit |
| `deletion` | the text was on the message when it was removed |

Two values, a check constraint, and **required** — so a row cannot be silent about which
happened. There is no third value: a message's text stops being current for exactly these two
reasons, and if a third ever arrives it is a clause rather than a column default.

### What this route does not offer

- **No pagination.** It is unchanged in that respect: a message's version list is bounded by
  how many times somebody edited it, and nothing bounds that. **Recorded as a known shape
  rather than solved** — the same question `listMessageEdits` has had since chapter 3.23, and
  a page bound added here would be a second contract change.
- **No attachment history.** FR-MED-10 unlinks a tombstone's attachments and the versions hold
  text. What was attached to a message that has been deleted is not recoverable, and the
  chapter says so rather than implying the list is complete.
- **No actor.** Who edited and who deleted is the audit log's (FR-MOD-03, chapter 4.18), joined
  by nothing automatic. A version row says what the text was; an audit entry says who ended it.
  **The two are deliberately not joined here** — an audit entry exists only for an application
  credential's deletion, and a user editing their own message writes no entry, so a joined
  shape would be null for most rows and would read as missing data.

## `GET /v1/channels/{channelId}/messages`

One field added to each row:

| field | on a live message | on a tombstone |
|---|---|---|
| `deleted_at` | `null` | the instant of removal |

**Why it belongs here and not only on the delete response.** Three surfaces describe one
event: the `DELETE` response, the real-time `message.deleted` frame, and this. The first two
carry the instant and this one does not, so a client that was offline when the removal happened
and catches up through history learns that the message is gone and not when.

**An addition, not a reshape**, which is the distinction CON-05's URL-versioning rule turns on
and the one chapter 4.8 made when it added `has_more` to a published envelope.

### And this row already disagrees with `messageSchema`

Measured: history serves `channel_id` where the schema declares `channel`, carries an
`edited_at` the schema does not declare, and returns `text: null` against a `z.string()`.
**Nothing parses the history response against that schema**, so the divergence costs nothing
today and no instrument can see it.

This contract records it and does not converge it. Making the two agree is a reshape of a
published response, where everything above is an addition — and chapter 4.14 measured what
making one field required costs across construction sites before concluding that required was
worth it there. The question of which document is wrong is recorded in `gaps.md`.

## Refusals

| condition | status | code |
|---|---|---|
| a user token on `/edits` | 403 | `wrong_credential_type` — the guard's existing refusal, **unchanged, measured as already present, and asserted in a suite for the first time by this chapter**. `targets.ts:208` says why that matters: *"this entry and the decorator are the same authorisation fact written twice"*, and nothing had checked the half that enforces |
| a message in another tenant's channel | 404 | indistinguishable from an id nobody has, and **already attacked**: `gauntlet.itest.ts:242`, *"a foreign message's history reads as an absent one"* |
| a message id that exists nowhere | 404 | the same body |

**No new error code.** The refusals this chapter can produce are ones the platform already
answers, and `codes.ts` is published by 24 pages with an appendix that amends it twice — so
adding one is a bill to check before incurring, not after (chapter 4.11).

## What this contract does not offer

- **No write route for a version.** A version is a consequence of an edit or a deletion, never
  a request. The same position chapter 4.18 took for the audit log: a log a client can write to
  records what the client says happened.
- **No recovery of versions that predate this chapter.** A deletion before it ships destroyed
  the final text. No migration can recover it, and the chapter publishes the boundary rather
  than implying the history is complete backwards.
- **No `DELETE` on a version.** Refused by the database once the table is append-only, not by
  the absence of a route — **FR-011**'s demonstration is an attempted write at the storage
  layer, because a route that does not exist proves nothing about a table (chapter 4.18).
  *(This cited FR-004 — the no-op rule — until the third analysis pass. The citation was
  written before pass 2 gave immutability a requirement of its own, and pointed at the
  nearest clause that sounded right.)*

  **And a version row is also what stops its message being hard-deleted**, which is a
  different refusal by a different mechanism: `message_edits_message_id_fkey` is `NO ACTION`
  and fires before any trigger. Nothing in this contract exposes a hard delete, so no caller
  meets it — row 22's erasure will, and `spec.md`'s edge cases carry the measurement.
